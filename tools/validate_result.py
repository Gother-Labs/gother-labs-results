#!/usr/bin/env python3
"""Validate public result bundles before they are consumed by the website."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

if __package__:
    from .schema_validation import SchemaValidationError, validate_instance
else:
    from schema_validation import SchemaValidationError, validate_instance


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
RESULT_SCHEMA_ID = "https://gotherlabs.com/schemas/result.schema.json"
PUBLIC_ARTIFACT_ROOTS = {"artifacts", "assets"}
SAFE_PATH_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BEFORE_AFTER_EVIDENCE_MODEL = "before_after"
FORBIDDEN_NAME_PARTS = (
    "prompt",
    "reason",
    "rationale",
    "thought",
    "telemetry",
    "log",
    "dump",
    "private",
    "secret",
)


class ResultValidationError(ValueError):
    """Raised when a result bundle fails semantic or security validation."""


def _reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant {value}")


def load_json(path: Path, *, label: str | None = None) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_nonfinite_constant,
        )
    except FileNotFoundError as exc:
        raise ResultValidationError(f"{label or path}: file does not exist") from exc
    except json.JSONDecodeError as exc:
        raise ResultValidationError(
            f"{label or path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except ValueError as exc:
        raise ResultValidationError(f"{label or path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise ResultValidationError(f"{label or path}: cannot be read: {exc}") from exc


def assert_close(name: str, actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise ResultValidationError(f"{name} mismatch: expected {expected}, got {actual}")


def _declared_artifacts(result: dict[str, Any]) -> Iterator[tuple[str, str]]:
    yield "$.evaluation_contract.artifact", result["evaluation_contract"]["artifact"]
    for key, value in result["artifacts"].items():
        if isinstance(value, str):
            yield f"$.artifacts.{key}", value
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield f"$.artifacts.{key}[{index}]", item


def resolve_public_file(result_dir: Path, reference: str, *, json_path: str) -> Path:
    """Resolve one bundle-local public file without permitting path traversal."""

    if "\\" in reference or "\x00" in reference:
        raise ResultValidationError(
            f"result.json {json_path}: unsafe artifact reference {reference!r}"
        )

    relative = PurePosixPath(reference)
    parts = relative.parts
    if (
        relative.is_absolute()
        or not parts
        or reference != relative.as_posix()
        or parts[0] not in PUBLIC_ARTIFACT_ROOTS
        or any(part in {".", ".."} or not SAFE_PATH_SEGMENT.fullmatch(part) for part in parts)
    ):
        raise ResultValidationError(
            f"result.json {json_path}: unsafe artifact reference {reference!r}; "
            "use a normalized bundle-relative path under artifacts/ or assets/"
        )

    root = result_dir.resolve()
    candidate = (root / Path(*parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ResultValidationError(
            f"result.json {json_path}: unsafe artifact reference {reference!r} escapes the bundle"
        ) from exc
    if not candidate.is_file():
        raise ResultValidationError(
            f"result.json {json_path}: declared artifact does not exist: {reference}"
        )
    return candidate


def validate_declared_files(result_dir: Path, result: dict[str, Any]) -> None:
    for json_path, reference in _declared_artifacts(result):
        resolve_public_file(result_dir, reference, json_path=json_path)

    captions = result["website"].get("figure_captions", {})
    for reference in captions:
        resolve_public_file(
            result_dir,
            reference,
            json_path=f"$.website.figure_captions[{json.dumps(reference)}]",
        )


def validate_public_names(result_dir: Path) -> None:
    bad_names: list[str] = []
    root = result_dir.resolve()
    for path in result_dir.rglob("*"):
        relative = path.relative_to(result_dir)
        if path.is_symlink():
            resolved = path.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise ResultValidationError(
                    f"Bundle path escapes through symlink: {relative.as_posix()}"
                ) from exc
            if not resolved.is_file():
                raise ResultValidationError(
                    f"Broken or non-file bundle symlink: {relative.as_posix()}"
                )
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if any(part in lowered for part in FORBIDDEN_NAME_PARTS):
            bad_names.append(relative.as_posix())
    if bad_names:
        raise ResultValidationError(f"Forbidden public artifact names detected: {bad_names}")


def _required_artifact(result: dict[str, Any], key: str) -> str:
    value = result["artifacts"].get(key)
    if not isinstance(value, str):
        raise ResultValidationError(
            f"result.json $.artifacts.{key}: a string artifact path is required "
            f"for {result['slug']}"
        )
    return value


def validate_website_paths(result_dir: Path, result: dict[str, Any]) -> None:
    slug = result["slug"]
    expected_detail = f"results/{slug}/"
    if result["website"]["detail_path"] != expected_detail:
        raise ResultValidationError(
            "result.json $.website.detail_path: "
            f"expected {expected_detail!r}, got {result['website']['detail_path']!r}"
        )

    surface_path = result["website"].get("surface_path")
    if surface_path is None:
        return
    expected_surface = f"results/{slug}/run/"
    if surface_path != expected_surface:
        raise ResultValidationError(
            "result.json $.website.surface_path: "
            f"expected {expected_surface!r}, got {surface_path!r}"
        )
    if not (result_dir / "run" / "index.html").is_file():
        raise ResultValidationError(
            "result.json $.website.surface_path: declared surface is missing run/index.html"
        )


def validate_metrics(result_dir: Path, result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    metrics_reference = _required_artifact(result, "metrics")
    artifact_metrics = load_json(
        resolve_public_file(result_dir, metrics_reference, json_path="$.artifacts.metrics"),
        label=metrics_reference,
    )
    if artifact_metrics != metrics:
        raise ResultValidationError("artifacts/metrics.json does not match result.metrics")

    if result.get("evidence_model") == BEFORE_AFTER_EVIDENCE_MODEL:
        return

    if result["slug"] == "circle-packing-26-unit-square":
        expected = float(metrics["seed"]) - float(metrics["best"])
        if not math.isclose(float(metrics["improvement"]), expected, rel_tol=1e-12, abs_tol=0.0):
            raise ResultValidationError(
                f"improvement mismatch: expected {expected}, got {metrics['improvement']}"
            )
        expected_pct = expected / abs(float(metrics["seed"])) * 100.0
        if not math.isclose(
            float(metrics["improvement_pct"]), expected_pct, rel_tol=1e-12, abs_tol=0.0
        ):
            raise ResultValidationError(
                f"improvement_pct mismatch: expected {expected_pct}, "
                f"got {metrics['improvement_pct']}"
            )

        report_reference = _required_artifact(result, "verification_report")
        report = load_json(
            resolve_public_file(
                result_dir,
                report_reference,
                json_path="$.artifacts.verification_report",
            ),
            label=report_reference,
        )
        expected_scores = {
            "1e-6": metrics["tolerance_1e_6_sum_radii"],
            "1e-10": metrics["tolerance_1e_10_sum_radii"],
            "exact": metrics["exact_accepted_sum_radii"],
        }
        for name, expected_score in expected_scores.items():
            case = report["cases"][name]
            if not case["valid"] or case["score"] != expected_score:
                raise ResultValidationError(
                    f"{name} verification report disagrees with result.metrics"
                )
            if case["total_conditions_checked"] != metrics["constraint_checks_passed"]:
                raise ResultValidationError(
                    f"{name} condition count disagrees with result.metrics"
                )
        if any(case["valid"] for case in report["relaxed_certificates_rechecked_at_zero"].values()):
            raise ResultValidationError(
                "relaxed Circle Packing certificates unexpectedly pass at zero"
            )

        manifest_reference = _required_artifact(result, "publication_manifest")
        manifest = load_json(
            resolve_public_file(
                result_dir,
                manifest_reference,
                json_path="$.artifacts.publication_manifest",
            ),
            label=manifest_reference,
        )
        witness = manifest["strict_finite_decimal_witness"]
        if witness["exact_sum_radii"] != metrics["exact_accepted_sum_radii"]:
            raise ResultValidationError(
                "publication manifest strict witness disagrees with metrics"
            )
        return

    evolution_reference = _required_artifact(result, "evolution_trace")
    evolution = load_json(
        resolve_public_file(
            result_dir,
            evolution_reference,
            json_path="$.artifacts.evolution_trace",
        ),
        label=evolution_reference,
    )
    scores = [
        float(step["score"])
        for step in evolution.get("steps", [])
        if step.get("score") is not None
    ]
    if not scores:
        raise ResultValidationError("evolution trace has no scored steps")

    seed = float(metrics["seed"])
    best = float(metrics["best"])
    improvement = float(metrics["improvement"])
    direction = metrics.get("direction", "lower_is_better")
    expected_best = min(scores) if direction == "lower_is_better" else max(scores)
    expected_improvement = seed - best if direction == "lower_is_better" else best - seed
    assert_close("seed", scores[0], seed)
    assert_close("best", expected_best, best)
    assert_close("improvement", expected_improvement, improvement)

    candidate_reference = _required_artifact(result, "candidate_code")
    candidate_path = resolve_public_file(
        result_dir,
        candidate_reference,
        json_path="$.artifacts.candidate_code",
    )
    candidate = candidate_path.read_text(encoding="utf-8")
    expected_entrypoints = {
        "quadrature-rule-optimization": "quadrature_rule",
    }
    expected_entrypoint = expected_entrypoints.get(result["slug"])
    if expected_entrypoint and f"def {expected_entrypoint}" not in candidate:
        raise ResultValidationError(
            f"accepted candidate does not expose {expected_entrypoint}"
        )


def validate_result(result_dir: Path, *, schema_dir: Path = SCHEMA_DIR) -> dict[str, Any]:
    result_dir = result_dir.resolve()
    result_path = result_dir / "result.json"
    result = load_json(result_path, label=str(result_path))
    if not isinstance(result, dict):
        raise ResultValidationError(f"{result_path}: top-level JSON value must be an object")

    try:
        validate_instance(
            result,
            schema_id=RESULT_SCHEMA_ID,
            schema_dir=schema_dir,
            instance_label=str(result_path),
        )
    except SchemaValidationError as exc:
        raise ResultValidationError(str(exc)) from exc

    if result["slug"] != result_dir.name:
        raise ResultValidationError(
            f"result.json $.slug: {result['slug']!r} does not match directory {result_dir.name!r}"
        )
    if not (result_dir / "article.md").is_file():
        raise ResultValidationError("Bundle file missing: article.md")

    validate_declared_files(result_dir, result)
    validate_public_names(result_dir)
    validate_website_paths(result_dir, result)
    validate_metrics(result_dir, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        for result_dir in args.result_dirs:
            validate_result(result_dir)
            print(f"Validated {result_dir}")
    except ResultValidationError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate a public result bundle before it is consumed by the website."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_close(name: str, actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise SystemExit(f"{name} mismatch: expected {expected}, got {actual}")


def validate_declared_files(result_dir: Path, result: dict[str, Any]) -> None:
    declared = [
        result.get("evaluation_contract", {}).get("artifact"),
        result.get("artifacts", {}).get("candidate_code"),
        result.get("artifacts", {}).get("evolution_trace"),
        result.get("artifacts", {}).get("metrics"),
        result.get("artifacts", {}).get("provenance"),
        *(result.get("artifacts", {}).get("plots") or []),
    ]
    missing = [file for file in declared if file and not (result_dir / file).is_file()]
    if missing:
        raise SystemExit(f"Missing declared artifact files: {missing}")


def validate_public_names(result_dir: Path) -> None:
    bad = []
    for path in result_dir.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if any(part in lowered for part in FORBIDDEN_NAME_PARTS):
            bad.append(str(path.relative_to(result_dir)))
    if bad:
        raise SystemExit(f"Forbidden public artifact names detected: {bad}")


def validate_metrics(result_dir: Path, result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    artifact_metrics = load_json(result_dir / result["artifacts"]["metrics"])
    if artifact_metrics != metrics:
        raise SystemExit("artifacts/metrics.json does not match result.metrics")

    evolution = load_json(result_dir / result["artifacts"]["evolution_trace"])
    scores = [float(step["score"]) for step in evolution.get("steps", []) if step.get("score") is not None]
    if not scores:
        raise SystemExit("evolution trace has no scored steps")

    seed = float(metrics["seed"])
    best = float(metrics["best"])
    improvement = float(metrics["improvement"])
    assert_close("seed", scores[0], seed)
    assert_close("best", min(scores), best)
    assert_close("improvement", seed - best, improvement)

    candidate = (result_dir / result["artifacts"]["candidate_code"]).read_text(encoding="utf-8")
    expected_entrypoints = {
        "quadrature-rule-optimization": "quadrature_rule",
    }
    expected_entrypoint = expected_entrypoints.get(result["slug"])
    if expected_entrypoint and f"def {expected_entrypoint}" not in candidate:
        raise SystemExit(f"accepted candidate does not expose {expected_entrypoint}")


def validate_result(result_dir: Path) -> None:
    result = load_json(result_dir / "result.json")
    required = (
        "schema_version",
        "slug",
        "title",
        "domain",
        "status",
        "published_at",
        "summary",
        "problem_statement",
        "evaluation_contract",
        "metrics",
        "artifacts",
        "website",
    )
    missing = [key for key in required if key not in result]
    if missing:
        raise SystemExit(f"result.json missing required keys: {missing}")
    if result["schema_version"] != "result/v1":
        raise SystemExit("Unsupported schema_version")
    if result["slug"] != result_dir.name:
        raise SystemExit(f"Slug {result['slug']} does not match directory {result_dir.name}")
    if not (result_dir / "article.md").is_file():
        raise SystemExit("Missing article.md")

    validate_declared_files(result_dir, result)
    validate_public_names(result_dir)
    validate_metrics(result_dir, result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    validate_result(args.result_dir.resolve())
    print(f"Validated {args.result_dir}")


if __name__ == "__main__":
    main()

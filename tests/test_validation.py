from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from tools.build_catalog import CatalogBuildError, build_catalog, check_catalog, render_catalog
from tools.validate_result import ResultValidationError, validate_result


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "minimal-result"
BEFORE_AFTER_FIXTURE = ROOT / "tests" / "fixtures" / "before-after-result"


@contextmanager
def fixture_bundle(source: Path = FIXTURE) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as temp_dir:
        bundle = Path(temp_dir) / source.name
        shutil.copytree(source, bundle)
        yield bundle


def load_fixture_result(bundle: Path) -> dict[str, Any]:
    return json.loads((bundle / "result.json").read_text(encoding="utf-8"))


def write_fixture_result(bundle: Path, result: dict[str, Any]) -> None:
    (bundle / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


class ResultValidationTests(unittest.TestCase):
    def test_current_bundles_pass_schema_and_semantic_validation(self) -> None:
        result_dirs = sorted(path.parent for path in ROOT.glob("results/*/result.json"))
        self.assertGreater(len(result_dirs), 0)
        for result_dir in result_dirs:
            with self.subTest(result=result_dir.name):
                validate_result(result_dir)

    def test_valid_fixture_passes(self) -> None:
        validate_result(FIXTURE)

    def test_before_after_fixture_passes_without_optimizer_history(self) -> None:
        result = validate_result(BEFORE_AFTER_FIXTURE)
        self.assertEqual(result["evidence_model"], "before_after")
        self.assertNotIn("evolution_trace", result["artifacts"])
        self.assertNotIn("candidate_code", result["artifacts"])
        self.assertNotIn("seed", result["metrics"])

    def test_before_after_missing_patch_fails_closed(self) -> None:
        with fixture_bundle(BEFORE_AFTER_FIXTURE) as bundle:
            result = load_fixture_result(bundle)
            del result["artifacts"]["patch"]
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        self.assertIn("patch", str(raised.exception))

    def test_before_after_rejects_legacy_evolution_trace(self) -> None:
        with fixture_bundle(BEFORE_AFTER_FIXTURE) as bundle:
            result = load_fixture_result(bundle)
            result["artifacts"]["evolution_trace"] = "artifacts/evaluation.json"
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError):
                validate_result(bundle)

    def test_additional_top_level_property_reports_json_path(self) -> None:
        with fixture_bundle() as bundle:
            result = load_fixture_result(bundle)
            result["unexpected"] = True
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        message = str(raised.exception)
        self.assertIn("result.json $:", message)
        self.assertIn("Additional properties are not allowed", message)
        self.assertIn("unexpected", message)

    def test_missing_nested_property_reports_json_path(self) -> None:
        with fixture_bundle() as bundle:
            result = load_fixture_result(bundle)
            del result["website"]["card_label"]
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        message = str(raised.exception)
        self.assertIn("$.website", message)
        self.assertIn("card_label", message)
        self.assertIn("is a required property", message)

    def test_non_standard_numeric_constant_is_rejected(self) -> None:
        with fixture_bundle() as bundle:
            result_path = bundle / "result.json"
            contents = result_path.read_text(encoding="utf-8")
            result_path.write_text(
                contents.replace('"seed": 10.0', '"seed": NaN', 1),
                encoding="utf-8",
            )

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        self.assertIn("non-standard JSON numeric constant NaN", str(raised.exception))

    def test_missing_declared_artifact_reports_property_path(self) -> None:
        with fixture_bundle() as bundle:
            result = load_fixture_result(bundle)
            result["artifacts"]["metrics"] = "artifacts/missing.json"
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        message = str(raised.exception)
        self.assertIn("$.artifacts.metrics", message)
        self.assertIn("declared artifact does not exist", message)

    def test_parent_traversal_artifact_reference_is_rejected(self) -> None:
        with fixture_bundle() as bundle:
            result = load_fixture_result(bundle)
            result["evaluation_contract"]["artifact"] = "../../outside.md"
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        message = str(raised.exception)
        self.assertIn("$.evaluation_contract.artifact", message)
        self.assertIn("unsafe artifact reference", message)

    def test_symlink_escape_is_rejected(self) -> None:
        with fixture_bundle() as bundle:
            outside = bundle.parent / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            link = bundle / "artifacts" / "outside-link.json"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            result = load_fixture_result(bundle)
            result["artifacts"]["provenance"] = "artifacts/outside-link.json"
            write_fixture_result(bundle, result)

            with self.assertRaises(ResultValidationError) as raised:
                validate_result(bundle)

        self.assertIn("escapes the bundle", str(raised.exception))


class CatalogTests(unittest.TestCase):
    def test_two_builds_from_the_same_inputs_are_byte_identical(self) -> None:
        first = render_catalog(build_catalog(ROOT))
        second = render_catalog(build_catalog(ROOT))
        self.assertEqual(first, second)

    def test_catalog_accepts_both_evidence_models_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shutil.copytree(ROOT / "schemas", root / "schemas")
            shutil.copytree(FIXTURE, root / "results" / FIXTURE.name)
            shutil.copytree(
                BEFORE_AFTER_FIXTURE,
                root / "results" / BEFORE_AFTER_FIXTURE.name,
            )
            first = render_catalog(build_catalog(root))
            second = render_catalog(build_catalog(root))
            self.assertEqual(first, second)
            self.assertEqual(
                [entry["slug"] for entry in json.loads(first)["results"]],
                ["before-after-result", "minimal-result"],
            )

    def test_committed_catalog_matches_validated_inputs(self) -> None:
        expected = render_catalog(build_catalog(ROOT))
        self.assertEqual((ROOT / "catalog.json").read_text(encoding="utf-8"), expected)

    def test_catalog_check_rejects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shutil.copytree(ROOT / "schemas", root / "schemas")
            shutil.copytree(FIXTURE, root / "results" / "minimal-result")
            (root / "catalog.json").write_text("{}\n", encoding="utf-8")

            with self.assertRaises(CatalogBuildError) as raised:
                check_catalog(root)

        self.assertIn("catalog.json is out of date", str(raised.exception))

    def test_catalog_is_the_single_embedded_result_surface(self) -> None:
        catalog = build_catalog(ROOT)
        self.assertEqual(catalog["schema_version"], "results-catalog/v2")
        self.assertNotIn("generated_at", catalog)
        self.assertGreater(len(catalog["results"]), 0)
        for result in catalog["results"]:
            self.assertEqual(result["schema_version"], "result/v1")
            self.assertNotIn("path", result)
            self.assertIn("problem_statement", result)
            self.assertIn("artifacts", result)


if __name__ == "__main__":
    unittest.main()

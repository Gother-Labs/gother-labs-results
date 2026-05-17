#!/usr/bin/env python3
"""Rebuild catalog.json from results/*/result.json."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def validate_result(result: dict[str, Any], path: Path) -> None:
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
        raise SystemExit(f"{path} is missing required keys: {missing}")
    if result["schema_version"] != "result/v1":
        raise SystemExit(f"{path} has unsupported schema_version")
    for key in ("seed", "best", "improvement", "units", "validation_status"):
        if key not in result["metrics"]:
            raise SystemExit(f"{path} metrics missing {key}")


def main() -> None:
    entries = []
    for result_path in sorted(ROOT.glob("results/*/result.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        validate_result(result, result_path)
        entries.append(
            {
                "slug": result["slug"],
                "title": result["title"],
                "domain": result["domain"],
                "status": result["status"],
                "published_at": result["published_at"],
                "summary": result["summary"],
                "metrics": result["metrics"],
                "website": result["website"],
                "path": f"results/{result['slug']}/result.json",
            }
        )
    entries.sort(key=lambda item: (item["website"].get("order", 999), item["slug"]))
    catalog = {
        "schema_version": "results-catalog/v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": entries,
    }
    (ROOT / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

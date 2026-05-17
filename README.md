# Göther Labs Results

This repository is the public editorial and technical source for Göther Labs
results.

Each result lives in `results/<slug>/` and contains:

- `result.json`: structured metadata validated against the public result schema
- `article.md`: editable technical note
- `artifacts/`: sanitized public artifacts
- `assets/`: public figures used by the website

Internal Evolther runs must be exported through the publication exporter before
they are committed here. Public bundles must not include non-public generation
context, operational run records, sensitive configuration, or uncurated
intermediate material.

The website consumes this repository through `catalog.json`.

The current schema identifiers retain the historical `open-result/v1` naming for
compatibility with already published bundles. New documentation, tooling, and
website routes use “results”.

```bash
python3 tools/validate_result.py results/quadrature-rule-optimization
python3 tools/build_catalog.py
```

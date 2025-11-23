# Gov Data Pipeline

Modern, test-driven skeleton for loading, normalizing, enriching, and exporting government datasets into Enigma’s SMB ontology.

## What’s inside

| Layer | Location | Responsibilities |
| --- | --- | --- |
| **Ingestion** | `src/ingestion` | Detect file types, load CSV/JSON/API sources via `IngestManager`. |
| **Normalization** | `src/normalization` | Alias mapping, null cleanup, coordinate/phone/ZIP fixes, orchestrated by `Normalizer`. |
| **Feature Detection** | `src/feature_detection` | Unique-value stats, regex patterns, heuristics, schema fingerprinting exposed via `FeatureManager`. |
| **ML Row Filtering** | `src/ml_process` | XGBoost-backed classifier that drops low-confidence rows and persists its model. |
| **Routing & Enrichment** | `src/routing` | Strategy router + strategies (address, geo, financial, demographic, generic) to append derived annotations. |
| **Ontology Formatter** | `src/ontology` | Converts normalized rows into Enigma’s legal/brand/location ontology and prepares MCP metadata payloads. |
| **Exports** | `src/export` | JSON exporter used for cleaned/enriched/ontology outputs. |
| **Pipeline** | `src/pipeline.py` | Runs ingest → normalize → ML filter → feature detection → routing → ontology export for each file in `data/raw/`. |
| **Tests** | `tests/` | Pytest coverage for normalization, feature detection, routing, exporter, ML, ontology. |

## Getting started

1. **Install dependencies** (adjust command as needed):
   ```bash
   pip install -e .
   ```
2. **Inspect sample data** under `data/raw/`.
3. **Run the pipeline**:
   ```bash
   python3 src/pipeline.py
   ```
   Outputs land in:

   | File | Description |
   | --- | --- |
   | `data/clean/<name>_clean.csv` | Fully normalized records. |
   | `data/processed/<name>_profile.json` | Schema fingerprint + per-column stats/tags. |
   | `data/processed/<name>_ontology.json` | Legal/brand/location payload conforming to Enigma’s SMB ontology. |
   | `data/processed/<name>_mcp_metadata.json` | Full raw/alias metadata for MCP servers. |
   | `data/processed/<name>_row_classifier.json` | Persisted ML model used to drop low-quality rows. |
4. **Run tests**:
   ```bash
   python3 -m pytest
   ```

## Architecture overview

```
Raw Data (CSV/JSON/API)
      │
      ▼
[1] Ingestion  →  pandas.DataFrame
      │
      ▼
[2] Normalization  →  canonical columns, cleaned types
      │
      ▼
[3] ML Row Filter  →  drops low-confidence rows (saved model)
      │
      ▼
[4] Feature Detection  →  uniqueness stats, heuristics, schema fingerprint
      │
      ▼
[5] Strategy Router + Enrichment  →  address/geo/financial/demographic/generic tags
      │
      ▼
[6] Ontology Formatter  →  Enigma SMB contract + MCP metadata
      │
      ▼
[7] Exports  →  cleaned CSV + JSON artefacts
```

## Repository layout

```
gov-data-pipeline/
├── README.md
├── pyproject.toml
├── data/
│   ├── raw/         # drop source files here
│   ├── clean/       # normalized CSV outputs
│   └── processed/   # profiles, ontology JSON, metadata, classifier models
├── src/
│   ├── ingestion/
│   ├── normalization/
│   ├── feature_detection/
│   ├── ml_process/
│   ├── routing/
│   ├── ontology/
│   ├── export/
│   └── pipeline.py
└── tests/
    ├── test_export.py
    ├── test_feature_detection.py
    ├── test_ml_process.py
    ├── test_normalization.py
    ├── test_ontology.py
    └── test_routing.py
```

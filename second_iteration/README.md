# Gov Data Pipeline

Modular, testable pipeline skeleton for ingesting, normalizing, analyzing, and exporting government datasets.

## Layout
- `data/`: sample raw, processed, and example datasets for local experiments.
- `src/`: modular pipeline code grouped by responsibility (ingestion, normalization, feature detection, etc.).
- `tests/`: pytest-style smoke tests that validate each subsystem's surface API.

## Getting Started
1. Create a `.env` file from `.env.example` and provide credentials for any APIs.
2. Install dependencies with `pip install -e .` or `pip install -r requirements.txt` once defined.
3. Use `src/pipeline.py` as the orchestrator entry point when wiring real data sources.

```
   Raw Data
      │
      ▼
[1] Ingestion Layer       (CSV/JSON/XML → Pandas DataFrame)
      │
      ▼
[2] Normalization Layer   (clean types, fix names)
      │
      ▼
[3] Feature Detection     (unique values, regex, patterns)
      │
      ▼
[4] Rule Engine           (decide semantic meaning)
      │
      ▼
[5] Strategy Router       (pick export logic)
      │
      ▼
[6] Export Layer          (JSON, SQL, Parquet, etc.)
```

# File Structure: #
```
gov-data-pipeline/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── examples/
│
├── src/
│   ├── ingestion/
│   │   ├── loaders/
│   │   │   ├── csv_loader.py
│   │   │   ├── json_loader.py
│   │   │   ├── xml_loader.py
│   │   │   └── api_loader.py
│   │   ├── file_detector.py
│   │   └── ingest_manager.py
│   │
│   ├── normalization/
│   │   ├── cleaner.py
│   │   ├── type_casting.py
│   │   ├── alias_mapper.py
│   │   └── normalizer.py
│   │
│   ├── feature_detection/
│   │   ├── unique_value_analyzer.py
│   │   ├── pattern_detector.py
│   │   ├── schema_fingerprint.py
│   │   ├── heuristics_engine.py
│   │   └── feature_manager.py
│   │
│   ├── routing/
│   │   ├── strategy_router.py
│   │   ├── base_strategy.py
│   │   ├── strategies/
│   │   │   ├── address_strategy.py
│   │   │   ├── financial_strategy.py
│   │   │   ├── geo_strategy.py
│   │   │   ├── categorical_strategy.py
│   │   │   └── generic_strategy.py
│   │
│   ├── export/
│   │   ├── export_manager.py
│   │   ├── json_exporter.py
│   │   ├── parquet_exporter.py
│   │   └── sql_exporter.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── config.py
│   │   └── helpers.py
│   │
│   └── pipeline.py
│
└── tests/
    ├── test_ingestion.py
    ├── test_normalization.py
    ├── test_features.py
    ├── test_rules.py
    ├── test_routing.py
    └── test_export.py

```

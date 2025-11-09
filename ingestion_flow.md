# USAspending Data Ingestion Flow

## Overview
This document explains how the USAspending data ingestion pipeline works. It details each step — from pulling raw data through the API to generating clean, structured Enigma Brand Entities. The flow is simple: **extract**, **transform**, **map**, **validate**, and **export**.

---

## 1. Extraction

**Class:** `USAspendingExtractor`  
**Endpoint:** `https://api.usaspending.gov/api/v2/subawards/`

The process begins by fetching contract and subaward data directly from the USAspending API. The extractor sends a POST request with a defined time period and filters for contract-related award types (B, C, and D). The payload requests specific fields such as `subaward_number`, `recipient_name`, `amount`, `action_date`, and `description`.

If successful, the API returns JSON records which are converted into a Pandas DataFrame for further processing.  
If not, errors such as rate limits or authentication failures are handled gracefully.

**Output:** `df_raw` — the raw, unprocessed API response in DataFrame form.

---

## 2. Transformation

**Class:** `DataTransformer`

Once raw data is retrieved, it must be standardized and cleaned. This step ensures consistent field names, valid data types, and normalized recipient names so that multiple records referring to the same company are grouped together.

### `clean_data()`
- Renames columns to a consistent schema (`recipient_name` → `Recipient Name`)
- Converts date strings into proper `datetime` objects
- Ensures numeric fields are valid numbers
- Strips extra spaces and normalizes recipient names to uppercase
- Adds a helper column `Recipient Name Clean` for grouping

### `aggregate_by_recipient()`
- Groups all contract records by `Recipient Name Clean`
- Aggregates key values:
  - Total award amount
  - Number of contracts
  - Average award size
  - Earliest and latest contract dates
- Keeps location information (city, state, ZIP)
- Flattens multi-level column names into a readable format

**Outputs:**
- `df_clean` — cleaned and standardized data  
- `df_aggregated` — aggregated data by recipient entity

---

## 3. Mapping

**Class:** `EnigmaMapper`

The mapping step converts each aggregated recipient into an **Enigma Brand Entity**. This aligns every company or organization to Enigma’s ontology, which represents real-world entities consistently across datasets.

Each entity includes:
- A deterministic ID  
- Clean name  
- Physical location  
- Contract activity signals  
- Aggregated metrics  
- Metadata such as data source and last update time

### Step 1: Generate Entity ID
Each company gets a consistent ID derived from its name and location:
```python
entity_id = "B" + hashlib.md5(f"{name}|{location}".encode()).hexdigest()[:15]
```
This ensures the same entity always produces the same ID.

### Step 2: Create Address Object
The address is mapped into a structured object:
```json
{
  "city": "ARLINGTON",
  "state": "VA",
  "zip_code": "22202",
  "country": "USA"
}
```

### Step 3: Create Activity Signals
Each contract is represented as an `ActivitySignal` describing a federal contract award:
```json
{
  "signal_type": "federal_contract_awarded",
  "timestamp": "2023-03-15T00:00:00",
  "amount": 250000.0,
  "metadata": {
    "award_id": "1234AB",
    "contract_type": "Contract",
    "description": "Professional engineering services"
  }
}
```

### Step 4: Calculate Contract Metrics
All of a company’s contracts are summarized into one set of metrics:
```json
{
  "total_contract_value": 3500000.0,
  "contract_count": 7,
  "avg_contract_size": 500000.0,
  "most_recent_award_date": "2024-07-10T00:00:00",
  "oldest_award_date": "2023-01-12T00:00:00"
}
```

### Step 5: Build the Enigma Entity
All parts are combined into a final entity aligned with the Enigma ontology:
```json
{
  "entity_id": "B4f2a1c7b98d452",
  "entity_type": "Brand",
  "primary_name": "ACME ENGINEERING INC",
  "alternate_names": [],
  "operating_location": {
    "city": "ARLINGTON",
    "state": "VA",
    "zip_code": "22202",
    "country": "USA"
  },
  "activity_signals": [
    {
      "signal_type": "federal_contract_awarded",
      "timestamp": "2023-03-15T00:00:00",
      "amount": 250000.0,
      "metadata": {
        "award_id": "1234AB",
        "contract_type": "Contract",
        "description": "Professional engineering services"
      }
    },
    {
      "signal_type": "federal_contract_awarded",
      "timestamp": "2024-02-20T00:00:00",
      "amount": 275000.0,
      "metadata": {
        "award_id": "5678CD",
        "contract_type": "Contract",
        "description": "Technical support services"
      }
    }
  ],
  "contract_metrics": {
    "total_contract_value": 525000.0,
    "contract_count": 2,
    "avg_contract_size": 262500.0,
    "most_recent_award_date": "2024-02-20T00:00:00",
    "oldest_award_date": "2023-03-15T00:00:00"
  },
  "data_sources": ["USAspending"],
  "last_updated": "2025-11-09T11:00:00"
}
```

This JSON mirrors the internal Enigma ontology. Each **Brand Entity** includes:
- Identification fields (`entity_id`, `primary_name`)
- Structured location data (`operating_location`)
- Event-level history (`activity_signals`)
- Financial summaries (`contract_metrics`)
- Provenance (`data_sources`, `last_updated`)

**Output:** `entities` — list of Enigma Brand Entities representing each recipient.

---

## 4. Validation

**Class:** `Validator`

This step performs basic data quality checks to ensure entities are complete and consistent.  
It reports:
- Total number of entities
- Entities with valid locations
- Entities with contract signals
- Average number of contracts per entity
- Total contract value across all entities

Example report:
```
============================================================
VALIDATION REPORT
============================================================
Total entities: 86
With location data: 72 (83.7%)
With contracts: 86 (100.0%)
Avg contracts per entity: 4.3
Total contract value: $14,230,000
============================================================
```

---

## 5. Export

**Function:** `export_entities()`

The final step serializes all entities to disk in a human-readable JSON format.  
Each entity is converted to a dictionary and wrapped with metadata before writing.

Example output file structure:
```json
{
  "metadata": {
    "source": "USAspending API",
    "extraction_date": "2025-11-09T11:02:00",
    "entity_count": 86,
    "parser_version": "1.0"
  },
  "entities": [
    {
      "entity_id": "B4f2a1c7b98d452",
      "entity_type": "Brand",
      "primary_name": "ACME ENGINEERING INC",
      "operating_location": { "city": "ARLINGTON", "state": "VA", "country": "USA" },
      "contract_metrics": { "total_contract_value": 525000.0, "contract_count": 2 },
      "data_sources": ["USAspending"],
      "last_updated": "2025-11-09T11:00:00"
    }
  ]
}
```

**Output:** `enigma_entities.json` — ready for downstream ingestion or analysis.

---

## 6. Full Pipeline Summary

| Stage | Component | Input | Output |
|-------|------------|--------|---------|
| Extraction | `USAspendingExtractor` | API JSON | `df_raw` |
| Transformation | `DataTransformer` | Raw DataFrame | `df_clean`, `df_aggregated` |
| Mapping | `EnigmaMapper` | Clean + Aggregated Data | `entities` |
| Validation | `Validator` | Entity List | Validation Report |
| Export | `export_entities()` | Entity List | `enigma_entities.json` |

---

## 7. Execution Flow Example

```python
if __name__ == "__main__":
    extractor = USAspendingExtractor()
    raw_data = extractor.search_subawards(limit=100)
    df_raw = pd.DataFrame(raw_data)

    transformer = DataTransformer()
    df_clean = transformer.clean_data(df_raw)
    df_aggregated = transformer.aggregate_by_recipient(df_clean)

    mapper = EnigmaMapper()
    entities = [mapper.map_to_entity(row, df_clean) for _, row in df_aggregated.iterrows()]

    validator = Validator()
    validation = validator.validate_entities(entities)
    validator.print_validation_report(validation)

    export_entities(entities)
```

---

## Notes
- Each entity follows the **Enigma Brand Entity** schema for consistent representation across datasets.
- The JSON output is formatted for both human readability and automated ingestion.
- The script can be adapted for other open data sources with similar award structures.
- For production, consider adding pagination and incremental ingestion logic to handle large datasets.

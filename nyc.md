# Enigma Ingestion Prototype  
## NYC License Data Parser (JSON Ontology Export)

### 1. Description  

This prototype implements the **NYC License Data Parser**, a working ingestion pipeline for Enigma’s data framework.  
It ingests and standardizes **public NYC business license data**, then exports a unified, structured **Enigma-style JSON ontology** that connects business entities, their licenses, and operating locations.

The script is built to reflect Enigma’s ingestion model — supporting entity, license, and location relationships while preserving data provenance and schema consistency.

---

### 2. Overview  

The parser retrieves open business license data from the **NYC Department of Consumer and Worker Protection (DCWP)** API (`w7w3-xahh`), cleans and normalizes key identifiers, and produces a **single enriched JSON output** (`enigma_ontology_YYYYMMDD.json`).  

Each JSON entry represents a single business with nested `licenses` and `locations` objects, formatted for graph ingestion and ontology integration.

---

### 3. Objectives  

- Ingest live NYC DCWP business license data via Open Data API.  
- Clean and normalize ZIP codes, phone numbers, and addresses.  
- Remove incomplete, duplicate, or inactive records.  
- Exclude missing (`NaN`) latitude/longitude values.  
- Export one ontology-style JSON file with nested entity, license, and location data.  
- Preserve metadata for transparency and traceability.  

---

### 4. Ingestion Flow  

#### **Step 1 — Extract**  
- Downloads CSV data directly from NYC Open Data:  
  [`https://data.cityofnewyork.us/api/views/w7w3-xahh/rows.csv?accessType=DOWNLOAD`](https://data.cityofnewyork.us/api/views/w7w3-xahh/rows.csv?accessType=DOWNLOAD)  
- Loads data using `pandas` for cleaning and transformation.  
- Suppresses SSL warnings for local development.  

#### **Step 2 — Transform**  
The dataset is cleaned and standardized to ensure all identifiers and attributes can be joined into Enigma’s ontology schema.

| Operation | Description |
|------------|-------------|
| **Active License Filter** | Keeps only rows with `License Status = Active`. |
| **Borough Validation** | Ensures the business operates in one of NYC’s five boroughs. |
| **ZIP Code Normalization** | Converts ZIPs into 5-digit or ZIP+4 format. |
| **Phone Cleaning** | Converts phone numbers into `+1XXXXXXXXXX` format (E.164). |
| **Address Construction** | Merges building, street, unit, city, state, and ZIP fields into one normalized `fullAddress`. |
| **Duplicate Handling** | Removes duplicate entities, keeping the earliest issuance date. |
| **Integrity Check** | Ensures valid links between entity, license, and address fields. |

#### **Step 3 — Load**  
The cleaned data is exported as **a single nested JSON ontology** file in the `enigma_ingestion/` folder.

**Example record:**
```json
{
  "entity_id": "BA-1528318-2022",
  "legal_name": "VANDERSTAR CONTRACTING CO., INC.",
  "entity_status": "Active",
  "licenses": [
    {
      "registration_id": "0835028-DCA",
      "license_type": "Premises",
      "license_status": "Active",
      "license_start": "1997-01-02",
      "license_end": "2027-02-28",
      "source": {
        "source_name": "NYC Department of Consumer and Worker Protection",
        "source_url": "https://data.cityofnewyork.us/resource/w7w3-xahh.json",
        "last_updated": "2025-11-09T11:16:07Z"
      }
    }
  ],
  "locations": [
    {
      "full_address": "123 MAIN ST MANHATTAN NY 10027",
      "zip_code": "10027",
      "borough": "Manhattan",
      "lat": 40.812,
      "lon": -73.953,
      "source": {
        "source_name": "NYC Open Data Geocoding",
        "source_url": "https://data.cityofnewyork.us/resource/geoclient",
        "last_updated": "2025-11-09T11:16:07Z"
      }
    }
  ],
  "source": {
    "source_name": "NYC Open Data Portal",
    "source_url": "https://data.cityofnewyork.us/Business/Active-Businesses/w7w3-xahh",
    "last_updated": "2025-11-09T11:16:07Z"
  }
}
```
Entries missing both latitude and longitude are retained with valid address strings, but coordinates are excluded to ensure data accuracy.

---

## 5. Results  

- Loaded **~67,000 raw NYC license records**.  
- Cleaned and filtered to **~23,800 active, valid entities**.  
- Excluded all **NaN coordinates**.  
- Generated **one ontology-style JSON file**:  

```
enigma_ingestion/enigma_ontology_YYYYMMDD.json
```


- Verified field and record counts across all stages.  

| Stage | Input Rows | Output Rows |
|--------|-------------|-------------|
| Raw import | 67,246 | 67,246 |
| After borough + status filter | 23,872 | 23,872 |
| After deduplication | 23,872 | 23,872 |
| Final JSON export | 23,872 | 23,872 |

---

## 6. Output Schema  

| Field | Description |
|--------|-------------|
| **entity_id** | Unique business identifier (e.g., `BA-1458200-2022`). |
| **legal_name** | Official registered name of the business. |
| **entity_status** | Operational state (`Active`). |
| **licenses[]** | List of nested license records per entity. |
| **locations[]** | List of nested address/location objects per entity. |
| **source** | Metadata block describing data origin and last updated time. |

---

## 7. Integration Notes  

- Fully aligned with **Enigma’s ontology ingestion format**.  
- Each record nests related **licenses** and **locations** under one entity.  
- All nodes include provenance (`source_name`, `source_url`, `last_updated`).  
- The exported JSON can be directly ingested into Enigma’s **GraphQL** schema, which expects entities and nested edges.  

**GraphQL Representation Example:**
```graphql
{
  entity(id: "ENGM:ENTITY:NYC_DCWP:BA-1528318-2022") {
    legal_name
    licenses {
      registration_id
      license_status
      locations {
        full_address
      }
    }
  }
}
```
---

## 8. Known Limitations  

| Issue | Description | Planned Fix |
|--------|-------------|-------------|
| **Local IDs** | Current identifiers use NYC `Business Unique ID` and `License Number`. | Add Enigma global namespace prefix (e.g., `ENGM:ENTITY:NYC_DCWP:`). |
| **Partial Borough Coverage** | Some entries are missing boroughs but include valid ZIP codes. | Infer boroughs from ZIP codes in the next iteration. |
| **Schema Validation** | No JSON schema enforcement yet. | Integrate validation via **Pydantic** or **JSONSchema** in Iteration 2. |

---

## 9. Next Steps  

1. Add **ID namespacing** for global identifier consistency.  
2. Introduce **schema validation and logging**.  
3. Build **CLI support** for configurable source URLs and output paths.  
4. Test ingestion flow in **Enigma’s staging environment**.  

---

## 10. Summary  

The **NYC License Data Parser** provides a functional, end-to-end data ingestion prototype aligned with **Enigma’s ontology principles**.  

It:  
- Extracts live business data from **NYC Open Data**.  
- Cleans, normalizes, and validates key attributes.  
- Exports a single, ontology-ready JSON structure with provenance metadata.  

This parser demonstrates a scalable ingestion framework capable of powering **Enigma’s broader data ontology system** with minimal post-processing.

---

**Prepared by:** Jackson Zheng  
**Date:** November 2025  
**Project:** Enigma Data Ingestion — NYC DCWP Parser Prototype  

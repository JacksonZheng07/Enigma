# Enigma Ingestion Prototype

## Description

**Context:**  
* This week, the goal is to move from planning what data to analyze to the development of a working prototype that can ingest and process real or sample data.
* Start to implement a basic parser or ingestion script for two of the most promising datasets previously selected (e.g., government contract records, business registry data).
* Follow the integration framework defined last week to ensure alignment with Enigma’s data flow.
* Test initial parsing runs using a small sample (100–500 rows or entries).
* Log any formatting inconsistencies, schema mismatches, or encoding issues encountered.
* Collaborate with consultants to confirm whether parsed fields align with the business attributes Enigma tracks (e.g., company identifiers, industry codes).
* Document setup steps, dependencies, and troubleshooting notes.

**Deliverable:**  
> Functional prototype of a parser for one dataset + a short technical memo summarizing ingestion flow, key data fields extracted, and issues to address in iteration 2.
>
> “I know one week seems ambitious, but try your best and see how far you get! The more fleshed out your prototype is, the more things John will be able to give you feedback on during the midpoint check-in.”  
> — *Arsh*

---

# NYC License Data Parser — Enigma Ingestion Prototype

## Overview
The **NYC License Data Parser** is a working prototype that ingests and processes business license data from the **New York City Department of Consumer and Worker Protection (DCWP)**.  
It converts raw public data into clean, structured CSV outputs that align with Enigma’s ingestion framework, laying the groundwork for ontology integration.

---

## Objectives
- Ingest real, public NYC business license data directly from the city’s open API.  
- Clean and normalize key attributes such as business identifiers, license details, and locations.  
- Export the data in Enigma’s node-and-edge format for ingestion testing.  
- Identify and document early integration challenges (e.g., GraphQL compatibility and ID uniqueness).

---

## Ingestion Flow

### 1. **Extract**
- Downloads CSV data from NYC Open Data (`w7w3-xahh`) using `requests` and `pandas`.  
- Loads the data into a DataFrame for filtering and normalization.

---

### 2. **Transform**
This stage prepares the raw NYC license dataset for ingestion by applying multiple cleaning, filtering, and normalization operations.  
The goal is to make the data consistent, interpretable, and relational — ensuring that every license, business, and location can be uniquely identified and linked together later in Enigma’s ontology.

- **Filters only active licenses**  
  Removes expired or suspended records so that the dataset reflects currently operating businesses.  
  This reduces noise and ensures the graph represents real-world, valid entities.

- **Removes locations outside NYC’s five boroughs**  
  The NYC dataset occasionally includes entries listed as “Outside NYC” (e.g., in nearby counties or PO boxes).  

- **Cleans key identifying fields**
  - **ZIP Codes:**  
    Standardized into `#####` or `#####-####` formats using regex.  
    This prevents mismatches where the same area might appear as `10001`, `10001.0`, or `10001-1234`.  
    Consistent ZIP formats also make it easier to join or match with external geographic datasets later (e.g., census data).
  
  - **Phone Numbers:**  
    Reformatted into E.164 international standard (`+1XXXXXXXXXX`).  
    This ensures all phone numbers have the same structure and country code,  
    supporting reliable linking between entities across multiple data sources (e.g., when matching a NYC business to a federal registry entry).

  - **Addresses:**  
    Multiple columns such as building number, street, apartment, city, and state are merged into one normalized string.  
    This prevents partial duplicates like:
    ```
    123 MAIN ST
    123 MAIN STREET
    APT 3, 123 MAIN ST
    ```
    and ensures consistent formatting for location-based joins and geocoding.  
    Each address also includes the borough name, giving context even when street names overlap (e.g., “Broadway” in Manhattan vs. Brooklyn).

- **Removes duplicates and incomplete records**  
  - Duplicates (same `Business Unique ID` or `License Number`) are dropped, keeping only the earliest issuance.  
  - Entries missing critical identifiers, addresses, or license information are excluded.  
  This guarantees that every node and edge in Enigma’s graph corresponds to a valid, referenceable business record.

- **Ensures referential consistency across identifiers**  
  Every row that survives cleaning has a valid connection between:
  - `Business Unique ID` → Entity node  
  - `License Number` → License node  
  - `fullAddress` → Location node  

  These relationships form the backbone of Enigma’s entity–license–location model and enable clean edge creation later in the pipeline.

---

### 3. **Load**
Exports the cleaned dataset into **five CSV files** in the `enigma_ingestion/` directory:

| File | Description |
|------|--------------|
| `entities_YYYYMMDD.csv` | Business information (Legal Entities). |
| `licenses_YYYYMMDD.csv` | License registration details. |
| `locations_YYYYMMDD.csv` | Business addresses with latitude/longitude. |
| `entity_license_edges_YYYYMMDD.csv` | Connects businesses to their licenses. |
| `license_location_edges_YYYYMMDD.csv` | Connects licenses to their physical locations. |

---

## Results
- Parsed and processed ~60,000+ NYC license records.  
- Filtered to ~20,000 valid entities and ~20,000 geolocated addresses.  
- All five output files exported successfully for ingestion testing.  
- Confirmed relational links between entities, licenses, and locations.

---

## Integration with Enigma’s System
The exported CSVs feed directly into Enigma’s ingestion pipeline:

1. **Validation:** Schema and field-type verification.  
2. **Staging:** Data loaded into internal staging tables.  
3. **Entity Resolution:** Merges duplicate businesses and aligns with global identifiers.  
4. **Ontology Build:** Converts flat tables into graph nodes and relationships.

Once ingested, the data becomes queryable via Enigma’s **GraphQL API**, enabling graph-based insights across entities, licenses, and locations.

---

## Current Hurdles

### 1. **Global ID Compatibility**
The parser currently uses **local NYC identifiers** such as `BA-1706040-2024` for entities and `2124289-DCWP` for licenses.  

However, Enigma’s ontology requires **globally unique, namespaced IDs** to avoid collisions across datasets.

This can be resolved by adding a lightweight namespacing step during export:

BA-1706040-2024 → ENGM:ENTITY:NYC_DCWP:BA-1706040-2024


At this stage, it is not yet confirmed how Enigma’s ingestion service transforms or stores identifiers once data reaches the GraphQL layer.  
The current parser assumes that:
- Enigma will either accept pre-namespaced IDs, or  
- Apply its own namespace or hashing logic internally.  

This introduces a small **discrepancy risk** — the parser cannot currently verify how its identifiers will be interpreted once ingested.  
The safest approach for now is to preserve clear, consistent key relationships so Enigma’s ingestion framework can later apply final ID transformations without breaking referential integrity.

---

### 2. **GraphQL Alignment**
Enigma’s production GraphQL schema expects globally resolvable nodes and typed edges (e.g., `HAS_LICENSE`, `OPERATES_AT`).  
The parser’s node and edge structure already aligns conceptually with this model, but the **exact GraphQL indexing behavior** is not yet confirmed.  

If the ingestion layer rewrites or hashes incoming identifiers,  
the prefixed IDs (e.g., `ENGM:ENTITY:NYC_DCWP:BA-1706040-2024`) may require remapping or metadata tagging during ingestion.

A successful GraphQL query after ingestion would look like:
```graphql
{
  entity(id: "ENGM:ENTITY:NYC_DCWP:BA-1706040-2024") {
    legal_name
    licenses {
      registration_id
      locations {
        full_address
      }
    }
  }
}
```



# Output Directory
All cleaned CSVs are automatically exported to `/enigma_ingestion`.

---

## Testing and Validation

To ensure data quality and schema consistency:

- Verified required fields (`Business Unique ID`, `License Number`, `License Status`) exist.  
- Dropped rows missing essential identifiers or coordinates.  
- Confirmed that no duplicate `Business Unique ID` or `License Number` remained.  
- Regex-tested ZIP and phone formats on random samples.  
- Compared record counts across each cleaning stage:

| Step | Input Rows | Output Rows |
|------|-------------|-------------|
| Raw import | 60,000 | 60,000 |
| After borough filter | 56,000 | 56,000 |
| After active license filter | 22,000 | 22,000 |
| Final cleaned output | 20,000 | 20,000 |

---

## Data Schema Reference

| Table | Key Columns | Description |
|--------|--------------|-------------|
| **entities** | `entity_id`, `legal_name`, `entity_status` | Represents a legal business entity. |
| **licenses** | `registration_id`, `license_type`, `license_status` | Represents an issued license or permit. |
| **locations** | `full_address`, `latitude`, `longitude` | Represents the physical location of a business. |
| **entity_license_edges** | `entity_id`, `license_id` | Connects each entity to its license(s). |
| **license_location_edges** | `license_id`, `location_key` | Connects each license to its location. |

---

## Data Quality Notes and Edge Cases

- Some entries share the same `Business Unique ID` but operate under multiple DBAs.  
  → Retained only the earliest issuance per entity.  

- A few addresses lack boroughs but include valid coordinates.  
  → Retained and flagged for enrichment.  

- Inconsistent capitalization or punctuation in business names.  
  → Planned to standardize to title case in Iteration 2.  

---

## Next Iteration Plan

1. Implement global namespacing for GraphQL compatibility.  
2. Add schema validation and automated logging.  

---

## Summary

The **NYC License Parser** successfully converts public NYC business data into Enigma’s schema-ready node and edge formats.  

It provides a strong ingestion foundation with verified relational consistency and data quality.  

The remaining step is confirming Enigma’s global ID and GraphQL mapping conventions.  
Once finalized, the parser will be fully compatible with Enigma’s ingestion and ontology systems.

---

**Prepared by:** Jackson Zheng  
**Date:** November 2025  
**Project:** Enigma Data Ingestion — NYC DCWP Parser Prototype

# Enigma Technical Architecture

## Executive Summary
Enigma’s data model is designed to accurately represent the complexity of real-world business relationships. Its core innovation — the **Dual-Identity Architecture** — distinguishes between how a business presents itself (brand) and how it is legally recognized (legal entity). This structure allows Enigma to model everything from franchise networks to corporate hierarchies with precision and scale.

---

## Data Model and Characteristics

### Core Innovation: Dual-Identity Architecture
Enigma separates business data into two distinct but interconnected identities:

- **Brand Identity:** How a business presents itself to customers.  
- **Legal Entity Identity:** How a business is recognized by governments and financial systems.  

This distinction allows Enigma to model complex cases such as:
- One legal entity managing multiple brands.
- Food courts or shared retail spaces with multiple brands under one ownership.

---

## Three Core Entity Types

| Entity Type | Description |
|--------------|-------------|
| **Brands** | Customer-facing identities, including names, NAICS codes, revenue, and employee counts. |
| **Legal Entities** | Registered businesses with tax IDs, incorporation details, and business structures. |
| **Operating Locations** | Physical sites with USPS-validated addresses, contact information, and activity status. |

---

## Graph-Centric Architecture
Enigma uses a **2.4 billion-node knowledge graph**, where relationships are first-class citizens.  
Rather than using traditional relational joins, all associations between brands, entities, and locations are **pre-joined edges** that can be traversed instantly.

This allows complex queries like:

Brand → Location → Legal Entity → Parent Company → Officers

to execute in milliseconds rather than hours.

**Key Advantages:**
- Eliminates runtime JOIN costs.  
- Enables real-time semantic traversal.  
- Scales efficiently to billions of nodes.

---

## Relationship Network

| Relationship | Description |
|---------------|-------------|
| **Brand → Location** | Which brands operate at which physical sites. |
| **Brand → Legal Entity** | Which legal entities own or manage brands. |
| **Location → Legal Entity** | Legal responsibility for specific operating sites. |
| **Hierarchies** | Parent-subsidiary, franchise, and personnel linkages. |

---

## Key Characteristics

| Attribute | Description |
|------------|-------------|
| **Scale** | 48.9M brands and locations, 98M legal entities, and 600M+ raw records resolved into 45M distinct entities. |
| **Precision** | 97%+ entity resolution accuracy, 95% brand-to-legal linking precision, 98% NAICS code accuracy. |
| **Freshness** | Address re-validated every 90 days; 30B+ transactions processed annually. |
| **Query Performance** | GraphQL API supports 2,000 requests/second with millisecond response times. |

---

## Data Ingestion and Processing

### The “Garden Model” Philosophy
Enigma’s ingestion model favors **horizontal scalability** — collecting many smaller, messy datasets rather than a few massive ones.  
Each dataset is treated as an independent “garden,” maintained through modular ingestion functions.  
Currently, over **100,000+ sources** are integrated.

---

## Seven-Stage Ingestion Pipeline

### 1. Ingestion
Raw data collection from:
- Government registries (Secretary of State, SEC, SBA)
- Public web sources (directories, .gov domains)
- Financial partners (750M+ anonymized transaction cards, $4.5T+ annually)
- FOIA requests and private data vendors

### 2. Ontology Mapping
Maps all data to Enigma’s **SMB Ontology**, a universal schema that standardizes definitions like:
- Business name  
- Address  
- Tax ID  
- Industry classification  

### 3. Standardization
Applies canonical formatting:
- USPS-verified addresses (65M+)
- Consistent abbreviations and case normalization  
- Standard field naming and typing  

### 4. Entity Resolution
Machine learning links records referring to the same business using:
- Random forest models  
- String distance and token similarity  
- Transformer-based models for semantic matching  

Achieves 97%+ precision; resolves 600M+ records into 45M unique entities.

### 5. Entity Linking
Connects **brands** to **legal entities**, creating over **8M+ verified ownership relationships.**

### 6. Attribute Prediction
Predicts missing values such as:
- NAICS industry codes  
- SIC classifications  
- Employee counts  
- Revenue estimates  

### 7. Validation
Performs **492 quality checks** across 188 datasets:
- **Blocking checks** halt pipelines if critical fields fail (e.g., address validation).  
- **Alerting checks** monitor trends for anomalies.  
Validation combines:
- Ground truth sets (400 brands, 2,500 locations, etc.)  
- Weekly automated audits and monthly manual reviews  

---

## Technical Infrastructure

### Storage Layer
- **Graph Database:** Stores relationships and entities.  
- **Postgres:** Handles metadata and raw ingestion logs.  
- **Elasticsearch:** Supports full-text search and analytics.

### Processing Layer
- **Python + Pandas:** Data manipulation and modeling.  
- **Multiprocessing:** Parallel data operations.  
- **mprof:** Memory profiling and optimization.

### Orchestration
- **Apache Airflow:** DAG-based workflow management.  
- **Docker:** Isolated task execution environments.  
- **Terraform:** Infrastructure as Code with CI/CD integration.

### Compute
- **AWS EC2/ECS:** Parallel compute jobs with horizontal scaling.  
- **CloudWatch:** Monitors system performance.

---

## Data Access and Security

| Access Type | Description |
|--------------|-------------|
| **GraphQL API** | Flexible, high-performance querying with millisecond response times. |
| **Data Shares** | Bulk exports via Delta Sharing (Snowflake, Databricks, Redshift). |
| **Security** | SAML SSO, Cognito-based authentication, and PII isolation using access control policies. |

---

## Key Sources
- [Enigma’s Garden Model for ETL Tooling](https://medium.com/enigma-engineering/enigmas-garden-model-for-etl-tooling-fcbc8ffaa2e9)  
- [Enigma Financial Health Data Launch (PR Newswire)](https://www.prnewswire.com/news-releases/enigma-launches-small-business-financial-health-data-on-databricks-marketplace-302307504.html)  
- [Ensuring Data Quality in Enigma’s Graph Model](https://www.enigma.com/resources/blog/ensuring-unparalleled-data-quality-in-enigmas-graph-model-1)  
- [Official Enigma Documentation](https://documentation.enigma.com/getting_started/data_model)  

---

## Notes Section

### Document Purpose
This document outlines Enigma’s technical architecture and ingestion framework, focusing on the data model, infrastructure stack, and validation systems.

---

## Understanding the Data Model

Enigma’s model captures the **two key identities** behind every business:
1. **Brand** — public-facing representation.  
2. **Legal Entity** — government-recognized registration.  

It connects these with **Operating Locations**, providing a unified structure that reflects both ownership and operational relationships.

---

## Relationships Between Entities

| Relationship | Example | Purpose |
|---------------|----------|----------|
| Brand → Location | “Starbucks” → “123 Main St” | Shows where brands operate. |
| Brand → Legal Entity | “Starbucks” → “Starbucks Corporation” | Shows ownership and control. |
| Location → Legal Entity | “123 Main St” → “Starbucks Corporation” | Assigns legal responsibility for operations. |

---

## Infrastructure Behind the Data Model

| Layer | Tools | Purpose |
|-------|-------|----------|
| **Storage** | Postgres, Graph DB, Elasticsearch | Entity storage, search, and metadata tracking. |
| **Processing** | Python, Pandas, Multiprocessing | ETL, record linkage, and data cleaning. |
| **Orchestration** | Airflow, Docker | Workflow control and environment isolation. |
| **Infrastructure** | AWS (EC2/ECS), Terraform | Scalable compute and automated deployments. |
| **API/Serving** | GraphQL, Cognito (SAML) | Flexible access and secure authentication. |

---

## Understanding the Knowledge Graph

A **Knowledge Graph** represents data as entities (nodes) and relationships (edges), enabling fast lookups and semantic queries.  
Unlike relational databases, graphs capture *how* data is connected, not just *what* it is.

**In Enigma:**
- Each node (brand, entity, location) is a unique identifier.  
- Each edge represents a verified relationship (e.g., ownership, operation).  
- Pre-joined edges make queries fast and intuitive.

---

## Data Ingestion Workflow — “The Garden Model”

| Step | Description |
|------|-------------|
| **1. Ingestion** | Collect data from government, private, and web sources. |
| **2. Ontology Mapping** | Map raw data into Enigma’s SMB ontology. |
| **3. Standardization** | Clean and normalize attributes (e.g., addresses). |
| **4. Entity Resolution** | Use ML to deduplicate and merge records. |
| **5. Entity Linking** | Connect brands to legal entities. |
| **6. Attribute Prediction** | Enrich with NAICS, revenue, and employee data. |
| **7. Validation** | Apply 492+ quality checks before publishing. |

---

## Understanding the Ontology

An **ontology** is Enigma’s universal organizer — defining what each data element means and how it connects to others.  
It ensures that messy, unstructured source data becomes clean, interpretable, and linkable.

| Entity Type | What It Is | Why It Matters |
|--------------|-------------|----------------|
| **Brand** | Public-facing business name | Enables accurate customer targeting. |
| **Location** | Physical address and contact details | Supports logistics and regional analysis. |
| **Legal Entity** | Registered organization | Verifies compliance and legitimacy. |
| **Personnel** | Key individuals (owners, officers) | Identifies decision-makers. |

---

## Enigma’s Entity Resolution

Enigma achieves 97%+ precision in record resolution using:
- Probabilistic linkage + transformer models.  
- Random forest evaluation of name, address, and token similarity.  
- Ground truth validation against 2,500+ verified records.  

**Quality Metrics:**
- 97%+ entity match precision  
- 95% brand-to-entity linking accuracy  
- 98% NAICS classification accuracy  
- 70% of revenue predictions within ±30%  

---

## Extracting Data from Enigma

Data can be accessed in two primary ways:
1. **GraphQL API** — for structured, query-based access.
2. **Data Shares** — for bulk exports to warehouses (Snowflake, Databricks, Redshift).

**GraphQL Example:**
```graphql
{
  entity(id: "ENGM:ENTITY:STARBUCKS_CORP") {
    legal_name
    brands {
      name
      locations {
        full_address
      }
    }
  }
}
```
##
Prepared by: Jackson Zheng

Date: November 2025

Document: Enigma Technical Architecture Overview
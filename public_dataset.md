# Business and Regulatory Data Sources — Research Summary

## Business Licenses and Government Contracts

### Source: [Data.gov](https://www.data.gov/)
- Provides extensive data across federal, state, and local governments.  
- Not all datasets are frequently updated.

### Example Dataset: [Philadelphia Business Licenses](https://data.phila.gov/visualizations/li-business-licenses)
- Contains all business licenses issued in Philadelphia.  
- Offers both an interactive embed card and CSV export options.  
- Includes attributes such as:
  - License issue and expiration dates  
  - License types and current status  
  - Business identifiers and addresses  

### Applications for Enigma
This dataset can serve as a **business risk and compliance indicator**. Possible analytical use cases:
- **Business activity tracking:**  
  Identify licensing gaps or changes in license types that may indicate operational or regulatory issues.  
- **Risk profiling by license type:**  
  Certain license types (e.g., liquor, food service) may be riskier due to stricter compliance requirements.  
- **Business lifecycle analysis:**  
  Comparing license issue dates helps identify whether a business is new (higher risk) or established.  
- **Industry enrichment:**  
  License type fields often contain more granularity than standard industry codes (NAICS/SIC).  
- **Scale estimation:**  
  The number of licenses tied to a business can reflect operational scale or multi-location presence.  

---

## Court and Legal Records

### Federal Level
- **PACER:**  
  The most comprehensive U.S. court database, though paywalled at **$0.10 per page**.
- **CourtListener:**  
  A free, open-access alternative integrating **PACER** data via the [RECAP Archive](https://www.courtlistener.com/recap/).  
  - Offers a free tier with case metadata (party names, case type, filing date, outcomes).  
  - Paid tier provides deeper financial and document-level access.  
  - API available with both free and paid access levels.

#### Example:
[Bankruptcy Case Example — Alfa Global Ventures](https://www.courtlistener.com/docket/69301306/parties/despins-luc-a-chapter-11-trustee-v-alfa-global-ventures-limited/)  
- Provides fields such as:
  - Business name  
  - Filing date  
  - Case status  
  - Number of creditors  
- For Enigma, these details help flag financially distressed businesses and quantify debt exposure (more creditors = higher financial risk).

---

### State Level Example: [Massachusetts Court Database](https://www.masscourts.org/eservices/search.page.3?x=ZCieIU0*u9RvTh*BO3kcDg)
- Allows company name searches and district-level filtering.  
- Common case types relevant to business intelligence:
  - **Civil:** Contract disputes, unpaid bills, or legal disagreements.  
  - **Small Claims:** Disputes under $7,000 — typical for local SMBs.  

#### Search Results Provide:
| Field | Description |
|--------|-------------|
| Party/Company | The business or person involved |
| Case Number | Unique case identifier |
| Case Type | e.g., Civil, Small Claims |
| File Date | When the case was filed |
| Case Status | Active, Closed, Pending |
| Court | Jurisdiction or district |
| Affiliation | Plaintiff/Defendant role |

**Use Case for Enigma:**  
Helps identify SMBs involved in litigation, unpaid invoices, or contract breaches — direct signals of financial instability or non-compliance risk.

---

## Regulatory and Compliance Data

### Source: [OSHA Database](https://www.osha.gov/data)
- Enables searches by establishment name, state, or ZIP code.  
- Ideal for linking business locations to occupational safety violations.  

#### Key Fields:
| Field | Description |
|--------|-------------|
| Activity | Inspection or investigation type |
| Date Opened | Start of OSHA case |
| RID | Record identifier |
| NAICS / SIC | Industry classification |
| Violations | Number and type of infractions |
| Establishment Name | Business name or site inspected |

#### Example Record:
[Octavian Development LLC — Inspection Detail](https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1771081.015)  
- Small private construction business in Massachusetts.  
- Violation: Fall protection failure.  
- Shows penalties and fine resolutions.  
- Offers insight into **operational and compliance risk** at the business level.

**Limitations:**  
- Lacks a bulk download option.  
- Best used for direct establishment-level matching by name or ZIP code.

---

## Business Dynamics Statistics (Census Bureau)

### Source: [U.S. Census Bureau — Business Dynamics Statistics (BDS)](https://www.census.gov/programs-surveys/bds.html)
- Provides national-level business creation, expansion, and closure data.  
- Available in CSV format with datasets extending up to **2023**.  

### Interactive Tool: [BDS Explorer](https://bds.explorer.ces.census.gov/?year=2023&xaxis-id=sector&xaxis-selected=31-33,44-45,54,72&group-id=fage&group-selected=010,065,070,075,150&group-group=2&measure-id=job_creation&chart-type=bar)
- Allows viewing by:
  - **Sector**
  - **Firm Age**
  - **Employment Size**
  - **Geographic Region**
- Visual outputs: Table, line graph, or bar chart, all exportable as CSV.  
- Ideal for macroeconomic analysis of **business churn**, **job creation**, and **sectoral trends**.

---

## Summary of Usefulness to Enigma

| Data Source | Key Insights | Integration Potential |
|--------------|---------------|-----------------------|
| **Data.gov (Philadelphia Licenses)** | Licensing activity, expiration trends, regulatory risk | Direct ingestion via parser (CSV API) |
| **CourtListener / State Court DBs** | Litigation and bankruptcy risk | Enrichment source for financial distress flags |
| **OSHA Database** | Compliance and operational risk | Establishment-level linking to existing locations |
| **Census BDS** | National business dynamics and lifecycle data | Macro-level enrichment for risk modeling |

---

**Prepared by:** Jackson Zheng  
**Date:** November 2025  
**Document:** Business and Regulatory Data Source Review

import os
import re
import io
import json
import warnings
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter("ignore", InsecureRequestWarning)


def load_data(url: str) -> pd.DataFrame:
    """
    Load the NYC business license dataset from the provided URL.

    Args:
        url (str): Direct CSV download link from data.cityofnewyork.us.

    Returns:
        pd.DataFrame: Raw dataset loaded into memory.
    """
    response = requests.get(url, verify=False)
    df = pd.read_csv(io.StringIO(response.text), low_memory=False)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_zip(zip_value: str | float | None) -> str | None:
    """
    Normalize ZIP codes into standard formats (5-digit or ZIP+4).

    Args:
        zip_value: The raw ZIP code.

    Returns:
        str | None: Cleaned ZIP code or None if missing.
    """
    if pd.isna(zip_value):
        return None

    z = re.sub(r"[^0-9-]", "", str(zip_value).strip().replace(".0", ""))
    if re.fullmatch(r"\d{5}", z) or re.fullmatch(r"\d{5}-\d{4}", z):
        return z
    if re.fullmatch(r"\d{9}", z):
        return f"{z[:5]}-{z[5:]}"
    return z[:5].zfill(5)


def clean_phone(phone: str | float | None) -> str | None:
    """
    Convert phone numbers into E.164 international format.

    Args:
        phone: Raw phone number as string or numeric.

    Returns:
        str | None: Cleaned phone number or None if invalid.
    """
    if pd.isna(phone):
        return None

    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


def make_address(row: pd.Series) -> str:
    """
    Construct a standardized full address from multiple columns.

    Args:
        row (pd.Series): Single dataset row containing address parts.

    Returns:
        str: Formatted address string.
    """
    parts: List[str] = []
    if pd.notna(row.get("Building Number")):
        parts.append(str(row["Building Number"]).strip())
    if pd.notna(row.get("Street1")):
        parts.append(str(row["Street1"]).strip())
    if pd.notna(row.get("Apt/Suite")) and str(row["Apt/Suite"]).strip():
        parts.append(f"Apt {str(row['Apt/Suite']).strip()}")
    if pd.notna(row.get("City")):
        parts.append(str(row["City"]).strip())
    if pd.notna(row.get("State")):
        parts.append(str(row["State"]).strip())
    if pd.notna(row.get("ZIP Code")):
        parts.append(str(row["ZIP Code"]))
    return " ".join(parts).upper()


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the dataset before entity extraction.

    Steps:
        1. Drop irrelevant or empty columns.
        2. Keep only active licenses.
        3. Clean ZIP and phone fields.
        4. Construct full address strings.
        5. Filter by recognized NYC boroughs if available.

    Args:
        df (pd.DataFrame): Raw NYC dataset.

    Returns:
        pd.DataFrame: Preprocessed dataset ready for splitting.
    """
    df = df.drop(columns=["Street2", "Street3", "Unit Type", "Details"], errors="ignore")

    borough_col = None
    for c in ["Borough", "Borough Name"]:
        if c in df.columns:
            borough_col = c
            break

    if borough_col:
        valid_boroughs = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
        df = df[df[borough_col].notna() & df[borough_col].str.strip().isin(valid_boroughs)]

    df = df[df["License Status"] == "Active"]
    df = df[df["Street1"].notna()]

    required = [
        "Business Unique ID",
        "License Number",
        "Business Name",
        "License Status",
        "Initial Issuance Date"
    ]
    df = df.dropna(subset=required)

    df["ZIP Code"] = df["ZIP Code"].apply(clean_zip)
    df["Contact Phone"] = df["Contact Phone"].apply(clean_phone)
    df["fullAddress"] = df.apply(make_address, axis=1)

    if borough_col:
        df["fullAddress"] = df.apply(
            lambda r: f"{r['fullAddress']} ({r[borough_col]})"
            if pd.notna(r.get(borough_col)) else r["fullAddress"],
            axis=1
        )

    if "Address Type" in df.columns:
        df = df[df["Address Type"] == "Complete Address"]

    return df


def build_entities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract unique entities (legal businesses) from the dataset.

    Args:
        df (pd.DataFrame): Cleaned dataset.

    Returns:
        pd.DataFrame: Table of distinct entities.
    """
    base = df[[
        "Business Unique ID", "Business Name", "License Number", "License Status",
        "Initial Issuance Date", "Expiration Date", "License Type",
        "Business Category", "Contact Phone", "ZIP Code"
    ]].copy()

    base = base.sort_values("Initial Issuance Date").drop_duplicates(subset=["Business Unique ID"])
    entities = base.rename(columns={
        "Business Unique ID": "entity_id",
        "Business Name": "legal_name",
        "License Status": "entity_status",
        "Initial Issuance Date": "entity_start",
        "Expiration Date": "entity_end",
        "License Type": "license_type",
        "Business Category": "business_category",
        "Contact Phone": "phone_number",
        "ZIP Code": "zip_code"
    })
    return entities.dropna(subset=["entity_id"])


def build_licenses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a table of licenses linked to entities.

    Args:
        df (pd.DataFrame): Cleaned dataset.

    Returns:
        pd.DataFrame: License table.
    """
    licenses = df[[
        "Business Unique ID", "License Number", "License Type",
        "License Status", "Initial Issuance Date", "Expiration Date"
    ]].copy()

    licenses = licenses.drop_duplicates(subset=["License Number"]).rename(columns={
        "Business Unique ID": "entity_id",
        "License Number": "registration_id",
        "License Type": "license_type",
        "License Status": "license_status",
        "Initial Issuance Date": "license_start",
        "Expiration Date": "license_end"
    })
    return licenses.dropna(subset=["registration_id"])


def build_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct a locations table containing all physical business addresses.

    Args:
        df (pd.DataFrame): Cleaned dataset.

    Returns:
        pd.DataFrame: Location table (includes ZIP, borough, coordinates).
    """
    cols = ["Business Unique ID", "License Number", "fullAddress", "ZIP Code", "Latitude", "Longitude"]
    if "Borough" in df.columns:
        cols.append("Borough")

    locations = df[cols].copy()
    locations = locations.rename(columns={
        "Business Unique ID": "entity_id",
        "License Number": "registration_id",
        "ZIP Code": "zip_code",
        "fullAddress": "full_address"
    })
    return locations


def export_data_enigma_style(
    entities: pd.DataFrame,
    licenses: pd.DataFrame,
    locations: pd.DataFrame,
    output_dir: str = "enigma_ingestion"
) -> None:
    """
    Export all entities, licenses, and locations into a single Enigma-style JSON ontology.

    Each entity record contains:
        - Basic identifying fields.
        - A list of associated licenses.
        - A list of corresponding locations.

    Args:
        entities (pd.DataFrame): Entity table.
        licenses (pd.DataFrame): License table.
        locations (pd.DataFrame): Location table.
        output_dir (str): Directory for JSON output.
    """
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today().strftime("%Y%m%d")

    licenses["registration_id"] = licenses["registration_id"].astype(str).str.strip().str.upper()
    locations["registration_id"] = locations["registration_id"].astype(str).str.strip().str.upper()

    license_dict: Dict[str, List[Dict[str, Any]]] = (
        licenses.groupby("entity_id", dropna=True)
        .apply(lambda g: g.drop(columns=["entity_id"]).to_dict(orient="records"))
        .to_dict()
    )

    location_dict: Dict[str, List[Dict[str, Any]]] = {}
    for entity_id, group in locations.groupby("entity_id", dropna=True):
        loc_records = []
        for _, row in group.iterrows():
            entry: Dict[str, Any] = {
                "full_address": row.get("full_address"),
                "zip_code": row.get("zip_code")
            }
            if "Borough" in row and pd.notna(row["Borough"]):
                entry["borough"] = row["Borough"]

            lat, lon = row.get("Latitude"), row.get("Longitude")
            if pd.notna(lat) and pd.notna(lon):
                entry["lat"] = float(lat)
                entry["lon"] = float(lon)

            loc_records.append(entry)
        location_dict[entity_id] = loc_records

    print(f"Built {len(location_dict)} location groups")

    records: List[Dict[str, Any]] = []
    for _, row in entities.iterrows():
        entity_id = row["entity_id"]
        record = row.to_dict()
        record["licenses"] = license_dict.get(entity_id, [])
        record["locations"] = location_dict.get(entity_id, [])
        record["source"] = {
            "source_name": "NYC Open Data Portal",
            "source_url": "https://data.cityofnewyork.us/Business/Active-Businesses/w7w3-xahh",
            "last_updated": datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        for lic in record["licenses"]:
            lic["source"] = {
                "source_name": "NYC Department of Consumer and Worker Protection",
                "source_url": "https://data.cityofnewyork.us/resource/w7w3-xahh.json",
                "last_updated": record["source"]["last_updated"]
            }
        for loc in record["locations"]:
            loc["source"] = {
                "source_name": "NYC Open Data Geocoding",
                "source_url": "https://data.cityofnewyork.us/resource/geoclient",
                "last_updated": record["source"]["last_updated"]
            }

        records.append(record)

    output_path = f"{output_dir}/enigma_ontology_{today}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"Exported Enigma ontology: {output_path}")
    print(f"Total Entities Exported: {len(records)}")


def main() -> None:
    """
    Execute the full data ingestion and export pipeline.

    Steps:
        1. Load dataset from NYC Open Data.
        2. Clean and preprocess data.
        3. Build structured tables for entities, licenses, and locations.
        4. Export ontology in JSON format.
    """
    url = "https://data.cityofnewyork.us/api/views/w7w3-xahh/rows.csv?accessType=DOWNLOAD"
    df = load_data(url)
    df = preprocess(df)
    entities = build_entities(df)
    licenses = build_licenses(df)
    locations = build_locations(df)
    export_data_enigma_style(entities, licenses, locations)


if __name__ == "__main__":
    main()
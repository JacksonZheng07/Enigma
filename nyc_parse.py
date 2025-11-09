import os
import re
import io
import requests
import pandas as pd
from datetime import datetime
from typing import Tuple

# Loads the Data
def load_data(url: str) -> pd.DataFrame:
    """
    Load NYC license data from the given URL.

    Args:
        url (str): Direct CSV download URL from data.cityofnewyork.us.

    Returns:
        pd.DataFrame: Raw dataset loaded into a pandas DataFrame.
    """
    response = requests.get(url, verify=False)
    df = pd.read_csv(io.StringIO(response.text))
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


# Cleaning Utilities
# Cleaning the zipcode
def clean_zip(zip_value: str | float | None) -> str | None:
    """
    Normalize ZIP codes into 5-digit or ZIP+4 format.

    Args:
        zip_value: The raw ZIP code value.

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

# Cleaning the phone number
def clean_phone(phone: str | float | None) -> str | None:
    """
    Convert phone numbers to E.164 format.

    Args:
        phone: Raw phone number.

    Returns:
        str | None: Standardized phone in format +1XXXXXXXXXX.
    """
    if pd.isna(phone):
        return None

    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None

# Make an engima compatable address
def make_address(row: pd.Series) -> str:
    """
    Combine address components into a standardized address string.

    Args:
        row (pd.Series): DataFrame row containing address fields.

    Returns:
        str: Full formatted address.
    """
    parts: list[str] = []

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

# Preprocessing
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and filter the raw dataset to prepare for entity extraction.

    Steps:
        - Drop irrelevant columns.
        - Keep only active licenses.
        - Remove invalid or incomplete addresses.
        - Standardize ZIP codes and phone numbers.
        - Construct full address strings.

    Args:
        df (pd.DataFrame): Raw dataframe.

    Returns:
        pd.DataFrame: Cleaned dataframe.
    """
    df = df.drop(columns=["Street2", "Street3", "Unit Type", "Details"], errors="ignore")

    df = df[df["License Status"] == "Active"]
    df = df[df["Street1"].notna()]
    df = df[df["Borough"].notna() & df["Borough"].str.strip().isin(
        ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
    )]

    required = ["Business Unique ID", "License Number", "Business Name",
                "License Status", "Initial Issuance Date"]
    df = df.dropna(subset=required)

    df["ZIP Code"] = df["ZIP Code"].apply(clean_zip)
    df["Contact Phone"] = df["Contact Phone"].apply(clean_phone)

    df["fullAddress"] = df.apply(make_address, axis=1)
    df["fullAddress"] = df.apply(
        lambda r: f"{r['fullAddress']} ({r['Borough']})"
        if pd.notna(r.get("Borough")) else r["fullAddress"], axis=1
    )

    if "Address Type" in df.columns:
        df = df[df["Address Type"] == "Complete Address"]

    return df


# Entity, License, and Location Builders
# Builds Entity file
def build_entities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a table of unique legal entities.

    Args:
        df (pd.DataFrame): Cleaned dataframe.

    Returns:
        pd.DataFrame: Entity table.
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

# Builds licenses file
def build_licenses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a table of individual licenses linked to entities.

    Args:
        df (pd.DataFrame): Cleaned dataframe.

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

# Builds location Builders
def build_locations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a table of physical locations for each license.

    Args:
        df (pd.DataFrame): Cleaned dataframe.

    Returns:
        pd.DataFrame: Location table.
    """
    locations = df[[
        "Business Unique ID", "License Number", "fullAddress",
        "ZIP Code", "Latitude", "Longitude"
    ]].copy()

    locations = locations.drop_duplicates(subset=["License Number", "fullAddress"]).rename(columns={
        "Business Unique ID": "entity_id",
        "License Number": "registration_id",
        "ZIP Code": "zip_code",
        "fullAddress": "full_address"
    })

    locations = locations.dropna(subset=["registration_id", "full_address"])
    return locations[locations["Latitude"].notna() & locations["Longitude"].notna()]


# Relationship Builders
def build_edges(licenses_df: pd.DataFrame, locations_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create edge tables connecting entities to licenses and licenses to locations.

    Args:
        licenses_df (pd.DataFrame): License table.
        locations_df (pd.DataFrame): Location table.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (entity_license_edges, license_location_edges)
    """
    entity_license_edges = licenses_df[["entity_id", "registration_id"]].drop_duplicates()
    entity_license_edges.rename(columns={"registration_id": "license_id"}, inplace=True)

    license_location_edges = locations_df[["registration_id", "full_address"]].drop_duplicates()
    license_location_edges.rename(columns={
        "registration_id": "license_id",
        "full_address": "location_key"
    }, inplace=True)

    return entity_license_edges, license_location_edges

# Export Logic
def export_data(
    entities: pd.DataFrame,
    licenses: pd.DataFrame,
    locations: pd.DataFrame,
    e_edges: pd.DataFrame,
    l_edges: pd.DataFrame,
    output_dir: str = "enigma_ingestion"
) -> None:
    """
    Export all node and edge tables to timestamped CSV files.

    Args:
        entities: Entity table.
        licenses: License table.
        locations: Location table.
        e_edges: Entity-license edge table.
        l_edges: License-location edge table.
        output_dir: Folder to save CSV outputs.
    """
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today().strftime("%Y%m%d")

    entities = entities.sort_values("entity_id")
    licenses = licenses.sort_values("registration_id")
    locations = locations.sort_values("registration_id")

    entities.to_csv(f"{output_dir}/entities_{today}.csv", index=False)
    licenses.to_csv(f"{output_dir}/licenses_{today}.csv", index=False)
    locations.to_csv(f"{output_dir}/locations_{today}.csv", index=False)
    e_edges.to_csv(f"{output_dir}/entity_license_edges_{today}.csv", index=False)
    l_edges.to_csv(f"{output_dir}/license_location_edges_{today}.csv", index=False)

    print(f"Entities: {entities.columns}")
    print(f"Licenses: {licenses.columns}")
    print(f"Locations: {locations.columns}")
    print(f"E_edge: {e_edges.columns}")
    print(f"l_egde: {l_edges.columns}")

# Main Pipeline
def main() -> None:
    """
    Run the full NYC license ingestion pipeline.
    """
    url = "https://data.cityofnewyork.us/api/views/w7w3-xahh/rows.csv?accessType=DOWNLOAD"

    df = load_data(url)
    df = preprocess(df)

    entities = build_entities(df)
    licenses = build_licenses(df)
    locations = build_locations(df)
    e_edges, l_edges = build_edges(licenses, locations)

    export_data(entities, licenses, locations, e_edges, l_edges)


if __name__ == "__main__":
    main()

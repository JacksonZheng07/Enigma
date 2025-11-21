"""Applies whitespace, casing, and formatting fixes."""

from __future__ import annotations
import pandas as pd

class Cleaner():
    """
    Created Class Cleaner()
    """
    @staticmethod
    def fix_nulls(df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace common null placeholders with None.
        """

        null_like = {"nan", "none", "null", "", "na"}
        df = pd.DataFrame(df)

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Fuck Me you dont got a pd.dataframe u have a dict")

        columns = df.columns.to_list()

        for col in columns:
            df[col] = df[col].apply(
                lambda v: None
                if v is None or str(v).strip().lower() in null_like
                else v
            )

        return df

    @staticmethod
    def clean_record(record: dict[str, object]) -> dict[str, object]:
        """
        Return a cleaned record copy.
        """
        raise NotImplementedError("Implement cleaning rules")

    @staticmethod
    def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize coordinate fields into canonical:
            - latitude (float | None)
            - longitude (float | None)
        
        Rules (matches Enigma ETL style):
        - Never drop rows.
        - Only parse coordinates if dataset actually contains them.
        - Support both combined "(lat, lon)" string or separate numeric fields.
        """
        try:
            df = pd.DataFrame(df)
        except TypeError as T: 
            raise TypeError('It already is a dataframe')

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Where the hell is my pd.Dataframe at")

        columns = df.columns.to_list()
        # Normalize presence flags
        has_lat = "lat" in columns
        has_lon = "lon" in columns
        has_location = "location" in columns

        if has_location:
            def extract(pair):
                if not isinstance(pair, str) or "(" not in pair:
                    return None
                try:
                    lat, lon = pair.strip("()").split(",")
                    return float(lat), float(lon)
                except Exception:
                    return None

            df["coord_pair"] = df["location"].apply(extract)

            # canonical fields
            df["latitude"] = df["coord_pair"].apply(lambda x: x[0] if x else None)
            df["longitude"] = df["coord_pair"].apply(lambda x: x[1] if x else None)

        # CASE 2: Separate columns, convert to floats
        if has_lat:
            df["latitude"] = df["latitude"].apply(lambda v: Cleaner._to_float(v))

        if has_lon:
            df["longitude"] = df["longitude"].apply(lambda v: Cleaner._to_float(v))

        return df
    
    @staticmethod
    def _to_float(v):
        """
        return a float
        """
        try:
            return float(v)
        except TypeError:
            return None

    @staticmethod
    def clean_zip_codes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize ZIP codes into canonical 5-digit strings.
        """

        if "zip" not in df.columns():
            return df

        def fix_zip(z):
            if z is None:
                return None

            z = str(z).strip()

            # Remove ZIP+4 extension (ex: 11372-0000)
            if "-" in z:
                z = z.split("-")[0]

            # Must be 5 digits
            if len(z) == 5 and z.isdigit():
                return z

            return None  # invalid ZIP

        df["zip"] = df["zip"].apply(fix_zip)
        return df
    
    @staticmethod
    def clean_phone_numbers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize phone numbers into 10-digit numeric strings.
        """

        if "phone" not in df.columns():
            return df

        def clean_phone(p):
            if not p:
                return None
            p = "".join(ch for ch in str(p) if ch.isdigit())
            return p if len(p) == 10 else None

        df["phone"] = df["phone"].apply(clean_phone)
        return df
    
    @staticmethod
    def clean_addresses(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize address fields into clean, human-readable format.
        Handles missing columns and missing values safely.
        """

        address_fields = [
            "address_building",
            "address_street",
            "address_street_2",
            "city",
            "state"
        ]

        for col in address_fields:
            if col not in df.columns():
                continue 

            def clean_addr(val):
                if val is None:
                    return None

                val = str(val).strip()

                if val.lower() in {"", "nan", "none", "null"}:
                    return None

                val = " ".join(val.split())

                # Formatting rules
                if col in ("address_street", "address_street_2", "city"):
                    return val.title()

                if col == "state":
                    return val.upper()

                return val

            df[col] = df[col].apply(clean_addr)

        return df



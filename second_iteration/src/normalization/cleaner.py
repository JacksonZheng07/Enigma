"""Applies whitespace, casing, and formatting fixes."""

from __future__ import annotations
import pandas as pd
import re

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
        if record is None:
            return {}
        if not isinstance(record, dict):
            raise TypeError("record must be a dictionary")

        cleaned: dict[str, object] = {}
        for key, value in record.items():
            if isinstance(value, str):
                normalized = re.sub(r"\s+", " ", value).strip()
                cleaned[key] = normalized if normalized else None
                continue

            if isinstance(value, float) and pd.isna(value):
                cleaned[key] = None
                continue

            cleaned[key] = value

        return cleaned

    @staticmethod
    def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = pd.DataFrame(df)
        except TypeError:
            raise TypeError("It already is a DataFrame")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Where the hell is my pd.Dataframe at")

        has_location = "location" in df.columns

        location_lat = None
        location_lon = None

        if has_location:

            def extract(pair):
                if not isinstance(pair, str) or "(" not in pair:
                    return None
                try:
                    lat, lon = pair.strip("()").split(",")
                    return float(lat), float(lon)
                except (ValueError, TypeError):
                    return None

            parsed = df["location"].apply(extract)
            location_lat = parsed.apply(lambda x: x[0] if x else None)
            location_lon = parsed.apply(lambda x: x[1] if x else None)
            df = df.drop(columns=["location"])

        lat_sources = []
        lon_sources = []

        if location_lat is not None:
            lat_sources.append(location_lat)
        if location_lon is not None:
            lon_sources.append(location_lon)

        for column in ("latitude", "lat"):
            if column in df.columns:
                lat_sources.append(df[column].apply(Cleaner._to_float))
        for column in ("longitude", "lon"):
            if column in df.columns:
                lon_sources.append(df[column].apply(Cleaner._to_float))

        def coalesce(series_list):
            merged = None
            for series in series_list:
                if merged is None:
                    merged = series
                else:
                    merged = merged.combine_first(series)
            return merged

        latitude = coalesce(lat_sources)
        longitude = coalesce(lon_sources)

        if latitude is not None:
            df["latitude"] = latitude
        if longitude is not None:
            df["longitude"] = longitude

        drop_candidates = {
            "lat",
            "lon",
            "Latitude",
            "Longitude",
        }
        existing = drop_candidates.intersection(df.columns)
        if existing:
            df = df.drop(columns=list(existing))

        return df


    @staticmethod
    def _to_float(v):
        """
        return a float
        """
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def clean_zip_codes(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize ZIP codes into canonical 5-digit strings.
        """

        try:
            df = pd.DataFrame(df)
        except TypeError as T: 
            raise TypeError('It already is a dataframe')

        columns = df.columns.to_list()

        if "zip_code" not in columns:
            return df

        def fix_zip(z : str) -> str:
            if z is None:
                return None

            z = str(z).strip()

            if len(z) == 10:
                if '-' in z:
                    return z
            
            if len(z) == 9:
                left = z[0:5]
                right = z[5:]
                z = left + '-' + right
                return z

            if len(z) == 5:
                return z

            return None 

        df["zip_code"] = df["zip_code"].apply(fix_zip)
        return df
    
    @staticmethod
    def clean_phone_numbers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize phone numbers into 10-digit strings.
        - Strips punctuation & letters
        - Removes country code (+1 or 1xxx...)
        - Removes extensions (x1234, ext.999)
        - Returns None if invalid
        """
        df = pd.DataFrame(df)

        if "phone" not in df.columns:
            return df

        def clean_phone(raw):
            if pd.isna(raw):
                return None

            s = str(raw).lower().strip()

            s = re.sub(r"(ext\.?|x)\s*\d+", "", s)

            digits = "".join(ch for ch in s if ch.isdigit())

            if digits.startswith("1") and len(digits) == 11:
                digits = digits[1:]

            return digits if len(digits) == 10 else None

        df["phone"] = df["phone"].apply(clean_phone)
        return df

    @staticmethod
    def clean_addresses(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize free-form address strings into structured components.
        """
        df = pd.DataFrame(df)

        if "address" not in df.columns:
            return df

        secondary_pattern = re.compile(
            r"(?:\b(?:apt|apartment|unit|suite|ste|floor|fl)\b|\#)\s*[\w-]*$", re.IGNORECASE
        )

        def split_address(raw: object) -> tuple[object, object, object]:
            if raw is None or (isinstance(raw, float) and pd.isna(raw)):
                return (None, None, None)

            normalized = re.sub(r"\s+", " ", str(raw)).strip()
            if not normalized:
                return (None, None, None)

            secondary = None
            match = secondary_pattern.search(normalized)
            if match:
                secondary = match.group(0).strip()
                normalized = normalized[: match.start()].strip()

            building = None
            street = normalized or None

            match = re.match(r"^(?P<number>\d+[A-Za-z]?)\s+(?P<street>.+)$", normalized)
            if match:
                building = match.group("number")
                street = match.group("street").strip() or None

            return (building, street, secondary)

        parsed = df["address"].apply(split_address)
        buildings = parsed.apply(lambda parts: parts[0])
        streets = parsed.apply(lambda parts: parts[1])
        secondary = parsed.apply(lambda parts: parts[2])

        if "address_building" in df.columns:
            df["address_building"] = df["address_building"].fillna(buildings)
        else:
            df["address_building"] = buildings

        if "address_street_name" in df.columns:
            df["address_street_name"] = df["address_street_name"].fillna(streets)
        else:
            df["address_street_name"] = streets

        if "secondary_address_street_name" in df.columns:
            df["secondary_address_street_name"] = df["secondary_address_street_name"].fillna(
                secondary
            )
        else:
            df["secondary_address_street_name"] = secondary

        return df

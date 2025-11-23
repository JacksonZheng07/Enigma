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
        raise NotImplementedError("Implement cleaning rules")

    @staticmethod
    def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = pd.DataFrame(df)
        except TypeError:
            raise TypeError("It already is a DataFrame")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Where the hell is my pd.Dataframe at")

        has_location = "location" in df.columns
        has_lat = "lat" in df.columns
        has_lon = "lon" in df.columns

        # CASE 1: Location string "(lat, lon)"
        if has_location:

            def extract(pair):
                if not isinstance(pair, str) or "(" not in pair:
                    return None
                try:
                    lat, lon = pair.strip("()").split(",")
                    return float(lat), float(lon)
                except NameError:
                    return None

            parsed = df["location"].apply(extract)

            df["lat"] = parsed.apply(lambda x: x[0] if x else None)
            df["lon"] = parsed.apply(lambda x: x[1] if x else None)
        df = df.drop(columns=["location"])

        # CASE 2: Separate lat/lon columns and convert to floats
        if has_lat:
            df["lat"] = df["lat"].apply(lambda v: Cleaner._to_float(v))

        if has_lon:
            df["lon"] = df["lon"].apply(lambda v: Cleaner._to_float(v))

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



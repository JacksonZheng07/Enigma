"""
Coordinates cleaning, aliasing, and type casting.
"""

from __future__ import annotations
import pandas as pd

from .alias_mapper import AliasMapper
from .cleaner import Cleaner


class Normalizer:
    """ class that runs all normalization primitives sequentially."""

    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        """
        Run all normalization steps in the correct order.
        ---------------------------------------------------------
        Parameters:
            df: pd.DataFrame

        ---------------------------------------------------------
        Return:
            pd.DataFrame
        """

        df = AliasMapper.map_aliases(df)
        df = Cleaner.fix_nulls(df)

        columns = df.columns.to_list()

        has_lat = any(col in {"lat", "latitude"} for col in columns)
        has_lon = any(col in {"lon", "longitude"} for col in columns)
        has_location = "location" in columns

        if has_lat and has_lon or has_location:
            df = Cleaner.clean_coordinates(df)

        if "zip_code" in columns:
            df = Cleaner.clean_zip_codes(df)
        if "phone" in columns:
            df = Cleaner.clean_phone_numbers(df)
        if "address" in columns:
            df = Cleaner.clean_addresses(df)
        return df

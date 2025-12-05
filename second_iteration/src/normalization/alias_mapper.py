"""
alias_mapper.py
Maps provider-specific column names to standardized aliases.

Example:
    "Address Zip"   -> "zip_code"
    "PostalCode"    -> "zip_code"
"""

from __future__ import annotations
from typing import Dict, Mapping, Union
import pandas as pd
from .alias import NORMALIZED_ALIASES, standardize_alias_key


class AliasMapper:
    """
    Utility class for standardizing and normalizing column names.
    """

    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes all DataFrame column names:
            - strips whitespace
            - replaces special chars with underscores
            - lowercases text
            - applies alias mapping
        """
        standardized = {col: AliasMapper.standardize(col) for col in df.columns}

        normalized = {
            original: NORMALIZED_ALIASES.get(standardized_col, standardized_col)
            for original, standardized_col in standardized.items()
        }

        renamed = df.rename(columns=normalized)
        return AliasMapper._coalesce_duplicate_columns(renamed)

    @staticmethod
    def map_aliases(
        record: Union[pd.DataFrame, Mapping[str, object]]
    ) -> Union[pd.DataFrame, Dict[str, object]]:
        """
        Normalize keys for either a DataFrame or a single mapping.
        """
        if isinstance(record, pd.DataFrame):
            return AliasMapper.normalize_columns(record)

        if not isinstance(record, Mapping):
            raise TypeError("record must be a mapping or pandas DataFrame")

        normalized_keys: Dict[str, object] = {}
        for key, value in record.items():
            standardized_key = AliasMapper.standardize(key)
            canonical = NORMALIZED_ALIASES.get(standardized_key, standardized_key)
            normalized_keys[canonical] = value
        return normalized_keys

    @staticmethod
    def standardize(col: str) -> str:
        """Expose the shared alias normalization helper."""
        return standardize_alias_key(col)

    @staticmethod
    def _coalesce_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Combine duplicate columns created after renaming.

        If multiple columns share the same canonical name, keep the first one
        encountered and fill missing values from later duplicates. This ensures
        downstream cleaners (which expect unique column labels) operate on a
        single column per canonical field.
        """
        if not df.columns.duplicated().any():
            return df

        coalesced: Dict[str, pd.Series] = {}
        order: list[str] = []
        for index, column in enumerate(df.columns):
            series = df.iloc[:, index]
            if column not in coalesced:
                coalesced[column] = series
                order.append(column)
            else:
                coalesced[column] = coalesced[column].combine_first(series)

        return pd.DataFrame({column: coalesced[column] for column in order}, index=df.index)

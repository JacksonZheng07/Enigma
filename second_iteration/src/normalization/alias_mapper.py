"""
alias_mapper.py
Maps provider-specific column names to standardized aliases.

Example:
    "Address Zip"   -> "zip_code"
    "PostalCode"    -> "zip_code"
"""

from __future__ import annotations
import re
from typing import Dict
import pandas as pd
from .alias import ALIASES

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

        ---------------------------------------------------
        Parameters:
            df : pd.DataFrame

        ---------------------------------------------------
        Return 
            pd.DataFrame
        """
        # standardize formatting
        standardized = {
            col: AliasMapper.standardize(col)
            for col in df.columns
        }

        # apply alias mapping
        normalized = {
            old: ALIASES.get(new, new)
            for old, new in standardized.items()
        }

        return df.rename(columns=normalized)

    @staticmethod
    def map_aliases(record: Dict[str, object]) -> Dict[str, object]:
        """
        Normalize keys of a single record (dict).
        -----------------------------------------------
        Parameter:
            record: Dict[str, object]
        
        -----------------------------------------------
        Returns:
            Dict[str, object]
        """
        return {
            ALIASES.get(AliasMapper.standardize(key), AliasMapper.standardize(key)): value
            for key, value in record.items()
        }

    @staticmethod
    def standardize(col: str) -> str:
        """
        Standardizes a column string into snake_case:
            - trims whitespace
            - replaces punctuation with underscores
            - collapses repeated underscores
        -----------------------------------------------
        Parameter:
            col: str

        -----------------------------------------------
        Returns:
            str
        """
        
        # replace punctuation with spaces
        col = (
            col.strip()
               .replace("-", " ")
               .replace(".", " ")
               .replace("/", " ")
               .replace(",", " ")
               .replace("?", " ")
               .replace("!", " ")
               .replace("@", " ")
               .replace("%", " ")
               .replace("&", " ")
        )

        col = re.sub(r"\s+", " ", col)

        # convert spaces to underscores
        col = col.replace(" ", "_").lower()

        # collapse multiple underscores (VERY IMPORTANT)
        col = re.sub(r"_+", "_", col)
        return col.rstrip('_')

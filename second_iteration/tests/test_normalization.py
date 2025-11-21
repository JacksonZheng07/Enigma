"""
Testing for normalization
"""

import unittest
import pandas as pd
from normalization.alias_mapper import AliasMapper

class TestNormalization(unittest.TestCase):
    """
    init class to test for normalization/ directory 
    """

    def test_basic_normalization(self) -> None:
        """
        Testing the basic normalization of Alias Mapper
        """
        self.assertEqual(
            AliasMapper.standardize(" Address Zip "),
            "address_zip"
        )

    def test_punctuation_normalization(self) -> None:
        """
        Testing the punctuation normalization of Alias Mapper
        """
        self.assertEqual(
            AliasMapper.standardize("Street-Name/Here."),
            "street_name_here"
        )

    def test_multiple_spaces(self) -> None:
        """
        Testing filtering of multiple spaces of Alias Mapper
        """
        self.assertEqual(
            AliasMapper.standardize("  City     Name    "),
            "city_name"
        )

    def test_collapse_underscores(self) -> None:
        """
        Testing collapse underscores of Alias Mapper
        """
        self.assertEqual(
            AliasMapper.standardize("Hello---World"),
            "hello_world"
        )

    def test_normalize_dataframe_two_columns(self) -> None:
        """
        Ensure two-column DataFrame normalizes correctly.
        """
        df = pd.DataFrame({
            "Address ZIP": ["10001"],
            "Business Name": ["Foo Corp"]
        })

        normalized_df = AliasMapper.normalize_columns(df)

        self.assertIn("zip_code", normalized_df.columns)
        self.assertIn("business_name", normalized_df.columns)

        # Test values are still correct
        self.assertEqual(normalized_df["zip_code"].iloc[0], "10001")
        self.assertEqual(normalized_df["business_name"].iloc[0], "Foo Corp")

unittest.main()

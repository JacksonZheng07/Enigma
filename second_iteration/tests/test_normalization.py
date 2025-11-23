"""
Testing for normalization
"""

import unittest
import pandas as pd
from normalization.alias_mapper import AliasMapper
from normalization.cleaner import Cleaner

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

    def test_clean_zip_codes(self) -> None:
        """
        Test Zip Code Cleaner 
        """
        df = pd.DataFrame({
            "Address ZIP": ["10001", '100010001', '11111-1111', None, '1qa3wsdfhjk'],
        })

        df = AliasMapper.map_aliases(df)
        cleaned = Cleaner().clean_zip_codes(df)
        self.assertEqual(cleaned.columns.to_list(), ['zip_code'])
        self.assertEqual(cleaned['zip_code'].iloc[0], '10001')
        self.assertEqual(cleaned['zip_code'].iloc[1], '10001-0001')
        self.assertEqual(cleaned['zip_code'].iloc[2], '11111-1111')
        self.assertEqual(cleaned['zip_code'].iloc[3], None)
        self.assertEqual(cleaned['zip_code'].iloc[4], None)

    def test_clean_phone(self) -> None:
        """
        Test Clean Phone Number
        """
        df = pd.DataFrame({
            "phone" : ['1111111111', None, '+1111111111', '111-111-1111', '+(1)-111-111-1111']
        })
        df = AliasMapper.map_aliases(df)
        cleaned = Cleaner().clean_phone_numbers(df)
        self.assertEqual(cleaned['phone'].iloc[0], '1111111111')
        self.assertEqual(cleaned['phone'].iloc[1], None)
        self.assertEqual(cleaned['phone'].iloc[2], '1111111111')
        self.assertEqual(cleaned['phone'].iloc[3], '1111111111')
        self.assertEqual(cleaned['phone'].iloc[4], '1111111111')

    def test_parse_valid_location_string(self) -> None:
        """
        Should extract valid lat/lon from '(lat, lon)' string.
        """
        df = pd.DataFrame({
            "location": ["(40.123, -73.456)"]
        })

        df = AliasMapper.map_aliases(df)
        cleaned = Cleaner.clean_coordinates(df)
        df_shape = cleaned.shape
        print(cleaned.columns.to_list)
        self.assertAlmostEqual(cleaned["lat"].iloc[0], 40.123)
        self.assertAlmostEqual(cleaned["lon"].iloc[0], -73.456)
        self.assertEqual(df_shape, (1,2))

unittest.main()

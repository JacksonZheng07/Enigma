"""
Testing src/ingest.py
"""

import unittest
import pandas as pd
from ingestion.ingest import IngestManager

class TestIngest(unittest.TestCase):
    """
    Setting up the unittest class to ingest.py 
    """

    def setUp(self) -> None:
        """
        setting up the object to be tested
        """
        self.ingest = IngestManager()

    def test_load_data_csv(self) -> None:
        """
        Testing load data function from ingest.py with .csv file
        """
        df = self.ingest.load_data('data/raw/testing_data.csv')
        self.assertIsInstance(df, pd.DataFrame)

    def test_load_data_json(self) -> None:
        """
        Testing load data function from ingest.py with .json file
        """
        df = self.ingest.load_data('data/raw/testing_data.json')
        self.assertIsInstance(df, pd.DataFrame)

    def test_load_data_api(self) -> None:
        """
        Testing Load data function from ingest.py
        """

    def test_bad_path(self) -> None:
        """
        Testing load data function from IngestManger with a bad path
        """
        with self.assertRaises(FileNotFoundError):
            self.ingest.load_data('asdfghjkldata/raw/testing_data.csv')

    def test_invalid_suffix(self) -> None:
        """
        Testing for when load data function is used on a file that isnt a 
        API, .json or .csv
        """
        with self.assertRaises(ValueError):
            self.ingest.load_data('data/test_data/testing_data.txt')

if __name__ == "__main__":
    unittest.main()

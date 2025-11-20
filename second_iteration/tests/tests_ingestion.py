"""
Testing src/ingest.py
"""
from src.ingestion.ingest_manager import IngestManager
import pandas as pd
import unittest

class TestIngest(unittest.TestCase):
    """
    Setting up the unittest class to ingest.py 
    """

    def setUp(self) -> None:
        """
        setting up the object to be tested
        """
        self.ingest = IngestManager()

    def test_load_data(self) -> None:
        """
        Test load data function from IngestManger 
        """
        df = self.ingest.load_data('../data/raw/testing_data.csv')
        self.assertIsInstance(df, pd.DataFrame)
unittest.TestCase()

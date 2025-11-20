"""
API loader responsible for fetching datasets from REST endpoints.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import httpx

from .base_loader import BaseLoader


class APILoader(BaseLoader):
    """Load dataset from a REST API endpoint into a pandas DataFrame."""

    def load(self, endpoint: str) -> pd.DataFrame:
        """
        Fetch JSON payload from a remote REST endpoint and convert it to a DataFrame.

        Parameters
        ----------
        endpoint : str
            The REST API URL to call.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the fetched dataset, with all values coerced to string.
        """
        # Synchronous HTTP request
        with httpx.Client() as client:
            response = client.get(endpoint, timeout=20.0)
            response.raise_for_status()

        data: Any = response.json()

        if not isinstance(data, list):
            raise ValueError(
                f"Expected a list of JSON objects from API, got {type(data)}"
            )

        df = pd.DataFrame(data).astype(str)
        return df

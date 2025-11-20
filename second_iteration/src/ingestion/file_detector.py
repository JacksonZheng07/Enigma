"""
File type detector used before selecting a loader.
"""

from __future__ import annotations
from pathlib import Path

SUPPORTED_EXTENSIONS = {".csv", ".json"}

class FileDetector():
    """
    Detects if the file is a csv or json 
    """
    def detect_file_type(self, path: Path) -> str:
        """
        Checks if the file is a .json or .csv
        ------------------------------------------------------------
        Parameters:
            path : Path 
        
        Return the loader key to use for the provided path.
        ------------------------------------------------------------
        Returns:
            str
            The suffix of the file wethers its .json, .csv, or any other format 
        """
        return path.suffix.lower()

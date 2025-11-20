"""Load configuration from environment variables."""

from __future__ import annotations

import os


def get_config() -> dict[str, str]:
    """Return a shallow copy of the config dictionary."""
    return {
        'data_dir': os.getenv('DATA_DIR', './data'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'api_base_url': os.getenv('API_BASE_URL', ''),
    }

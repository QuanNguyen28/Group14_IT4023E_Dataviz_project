"""Raw and processed data loading utilities."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import RAW_CO2_PATH


def load_raw_co2(path=RAW_CO2_PATH) -> pd.DataFrame:
    """Load the OWID CO2 CSV with a clear error if it is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"Raw OWID CO2 file not found at {path}. "
            "Download owid-co2-data.csv and place it in data/raw/."
        )
    return pd.read_csv(path)


def load_csv_if_exists(path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


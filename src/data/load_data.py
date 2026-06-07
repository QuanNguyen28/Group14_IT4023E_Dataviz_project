from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.constants import RAW_DATA_PATH, FEATURE_DATA_PATH, CLUSTERED_DATA_PATH


def load_raw_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {path}")
    return pd.read_csv(path)


def load_feature_data(path: str | Path = FEATURE_DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Feature dataset not found: {path}")
    return pd.read_csv(path)


def load_clustered_data(path: str | Path = CLUSTERED_DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if path.exists():
        return pd.read_csv(path)
    return load_feature_data()

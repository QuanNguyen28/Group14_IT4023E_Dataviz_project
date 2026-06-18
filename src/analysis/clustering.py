"""Optional clustering helpers for future extensions."""

from __future__ import annotations

import pandas as pd


def prepare_clustering_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return numeric complete cases for exploratory clustering."""
    available = [col for col in columns if col in df.columns]
    return df[["country", *available]].dropna() if available and "country" in df.columns else pd.DataFrame()


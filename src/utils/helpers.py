"""General helper functions."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def safe_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [col for col in columns if col in df.columns]


def first_existing(df: pd.DataFrame, columns: Iterable[str]) -> str | None:
    for col in columns:
        if col in df.columns:
            return col
    return None


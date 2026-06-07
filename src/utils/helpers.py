# handling file paths, saving outputs, and other small utilities
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    df.to_csv(path, index=index)
    return path

def load_csv(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)

def percent(numerator: float, denominator: float, digits: int = 2) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, digits)


def ordered_categorical(series: pd.Series, order: Iterable[str]) -> pd.Categorical:
    return pd.Categorical(series, categories=list(order), ordered=True)


def snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [c.strip().replace(" ", "_") for c in out.columns]
    return out

# data validation and quality checks for the smartphone usage dataset
from __future__ import annotations

import pandas as pd

from src.utils.constants import NUMERIC_COLS, CATEGORICAL_COLS


def validate_required_columns(df: pd.DataFrame) -> None:
    required = set(NUMERIC_COLS + CATEGORICAL_COLS + ["User_ID"])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def build_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "column": df.columns,
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing_count": [int(df[c].isna().sum()) for c in df.columns],
        "missing_pct": [round(df[c].isna().mean() * 100, 2) for c in df.columns],
        "unique_values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })


def detect_iqr_outliers(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or [c for c in NUMERIC_COLS if c in df.columns]
    rows = []
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = int(((df[col] < lower) | (df[col] > upper)).sum())
        rows.append({
            "column": col,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "lower_bound": lower,
            "upper_bound": upper,
            "outlier_count": count,
            "outlier_pct": round(count / len(df) * 100, 2),
        })
    return pd.DataFrame(rows)


def validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    checks = []
    rules = {
        "Age": (0, 120),
        "Daily_Screen_Time_Hours": (0, 24),
        "Total_App_Usage_Hours": (0, 24),
        "Number_of_Apps_Used": (0, None),
        "Social_Media_Usage_Hours": (0, 24),
        "Productivity_App_Usage_Hours": (0, 24),
        "Gaming_App_Usage_Hours": (0, 24),
    }
    for col, (min_allowed, max_allowed) in rules.items():
        if col not in df.columns:
            continue
        invalid_min = int((df[col] < min_allowed).sum()) if min_allowed is not None else 0
        invalid_max = int((df[col] > max_allowed).sum()) if max_allowed is not None else 0
        checks.append({
            "column": col,
            "min_allowed": min_allowed,
            "max_allowed": max_allowed,
            "actual_min": df[col].min(),
            "actual_max": df[col].max(),
            "invalid_below_min": invalid_min,
            "invalid_above_max": invalid_max,
        })
    return pd.DataFrame(checks)

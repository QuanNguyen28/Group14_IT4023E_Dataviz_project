"""Descriptive statistics and summary tables."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import USAGE_COLS, SCREEN_SEGMENT_ORDER


def kpi_summary(df: pd.DataFrame) -> dict:
    heavy_mask = df["Screen_Time_Segment"].isin(["Heavy (8–12h)", "Extreme (>12h)"])
    return {
        "total_users": int(len(df)),
        "avg_age": round(df["Age"].mean(), 2),
        "avg_daily_screen_time": round(df["Daily_Screen_Time_Hours"].mean(), 2),
        "avg_total_app_usage": round(df["Total_App_Usage_Hours"].mean(), 2),
        "avg_apps_used": round(df["Number_of_Apps_Used"].mean(), 2),
        "heavy_extreme_users": int(heavy_mask.sum()),
        "heavy_extreme_pct": round(heavy_mask.mean() * 100, 2),
    }


def screen_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df["Screen_Time_Segment"].value_counts().reindex(SCREEN_SEGMENT_ORDER).fillna(0).reset_index()
    out.columns = ["Screen_Time_Segment", "Users"]
    out["Percentage"] = (out["Users"] / len(df) * 100).round(2)
    return out


def categorical_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    out = df[column].value_counts().reset_index()
    out.columns = [column, "Users"]
    out["Percentage"] = (out["Users"] / len(df) * 100).round(2)
    return out


def group_usage_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    return (
        df.groupby(group_col, observed=True)[USAGE_COLS]
        .mean()
        .round(2)
        .reset_index()
    )


def numeric_profile(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or USAGE_COLS
    return df[columns].describe().T.round(2)

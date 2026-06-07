"""Behavioral relationship analysis helpers."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import BEHAVIOR_FEATURES


def correlation_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or BEHAVIOR_FEATURES
    return df[columns].corr().round(3)


def screen_time_correlations(df: pd.DataFrame) -> pd.Series:
    return correlation_matrix(df)["Daily_Screen_Time_Hours"].sort_values(ascending=False)


def relationship_sample(df: pd.DataFrame, n: int = 1000, random_state: int = 42) -> pd.DataFrame:
    if len(df) <= n:
        return df.copy()
    return df.sample(n=n, random_state=random_state)


def lifestyle_profiles(df: pd.DataFrame) -> pd.DataFrame:
    profile_cols = [
        "Social_Media_Usage_Hours",
        "Productivity_App_Usage_Hours",
        "Gaming_App_Usage_Hours",
        "Total_App_Usage_Hours",
        "Daily_Screen_Time_Hours",
        "Number_of_Apps_Used",
    ]
    return df.groupby("Dominant_Lifestyle", observed=True)[profile_cols].mean().round(2).reset_index()

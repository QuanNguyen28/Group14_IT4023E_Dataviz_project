"""Demographic and location analysis helpers."""

from __future__ import annotations

import pandas as pd

from src.utils.constants import AGE_GROUP_ORDER, USAGE_COLS


def age_group_usage(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("Age_Group", observed=True)[USAGE_COLS].mean().round(2).reset_index()
    return out.sort_values("Age_Group")


def gender_usage(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Gender", observed=True)[USAGE_COLS].mean().round(2).reset_index()


def location_usage(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Location", observed=True)[USAGE_COLS]
        .mean()
        .round(2)
        .sort_values("Daily_Screen_Time_Hours", ascending=False)
        .reset_index()
    )


def lifestyle_by_age(df: pd.DataFrame, normalize: bool = True) -> pd.DataFrame:
    table = pd.crosstab(df["Age_Group"], df["Dominant_Lifestyle"], normalize="index" if normalize else False)
    if normalize:
        table = (table * 100).round(2)
    table = table.reindex(AGE_GROUP_ORDER)
    return table.reset_index()


def lifestyle_by_gender(df: pd.DataFrame, normalize: bool = True) -> pd.DataFrame:
    table = pd.crosstab(df["Gender"], df["Dominant_Lifestyle"], normalize="index" if normalize else False)
    if normalize:
        table = (table * 100).round(2)
    return table.reset_index()


def age_category_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Social_Media_Usage_Hours",
        "Productivity_App_Usage_Hours",
        "Gaming_App_Usage_Hours",
        "Total_App_Usage_Hours",
        "Daily_Screen_Time_Hours",
    ]
    return df.groupby("Age_Group", observed=True)[cols].mean().round(2).reindex(AGE_GROUP_ORDER)

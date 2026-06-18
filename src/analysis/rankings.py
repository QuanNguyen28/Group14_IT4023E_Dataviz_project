"""Ranking and responsibility calculations."""

from __future__ import annotations

import pandas as pd


def get_top_emitters(df: pd.DataFrame, year: int, metric: str = "co2", n: int = 10) -> pd.DataFrame:
    if metric not in df.columns:
        return pd.DataFrame()
    return df.loc[df["year"].eq(year)].dropna(subset=[metric]).nlargest(n, metric)


def get_highest_per_capita(df: pd.DataFrame, year: int, n: int = 10) -> pd.DataFrame:
    return get_top_emitters(df, year, "co2_per_capita", n)


def compute_cumulative_responsibility(df: pd.DataFrame, year: int | None = None, n: int = 10) -> pd.DataFrame:
    if "cumulative_co2" not in df.columns:
        return pd.DataFrame()
    year = int(df["year"].max()) if year is None else year
    return df.loc[df["year"].eq(year)].dropna(subset=["cumulative_co2"]).nlargest(n, "cumulative_co2")


def compute_regional_totals(aggregates: pd.DataFrame, year: int) -> pd.DataFrame:
    regions = ["Asia", "Europe", "North America", "South America", "Africa", "Oceania"]
    return aggregates.loc[aggregates["year"].eq(year) & aggregates["country"].isin(regions)].copy()


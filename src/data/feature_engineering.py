"""Feature engineering for dashboard-ready CO2 datasets."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.constants import FUEL_COLUMNS


def add_world_shares(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "co2" not in out.columns:
        out["share_of_world_co2"] = np.nan
        return out
    world = out.loc[out["country"].eq("World"), ["year", "co2"]].rename(columns={"co2": "world_co2"})
    out = out.merge(world, on="year", how="left")
    out["share_of_world_co2"] = np.where(out["world_co2"] > 0, out["co2"] / out["world_co2"] * 100, np.nan)
    return out.drop(columns=["world_co2"])


def add_previous_year_values(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["country", "year"]).copy()
    for col in ["co2", "co2_per_capita", "population"]:
        if col in out.columns:
            out[f"previous_{col}"] = out.groupby("country")[col].shift(1)
    return out


def add_cagr_features(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    out = df.sort_values(["country", "year"]).copy()
    if "co2" not in out.columns:
        out[f"co2_cagr_{window}y"] = np.nan
        out[f"co2_change_{window}y"] = np.nan
        return out
    start = out.groupby("country")["co2"].shift(window)
    out[f"co2_start_{window}y"] = start
    out[f"co2_change_{window}y"] = out["co2"] - start
    out[f"co2_cagr_{window}y"] = np.where(
        (out["co2"] > 0) & (start > 0),
        (out["co2"] / start) ** (1 / window) - 1,
        np.nan,
    )
    return out


def add_cumulative_share(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "cumulative_co2" not in out.columns:
        out["cumulative_share_of_world"] = np.nan
        return out
    world = out.loc[out["country"].eq("World"), ["year", "cumulative_co2"]].rename(
        columns={"cumulative_co2": "world_cumulative_co2"}
    )
    out = out.merge(world, on="year", how="left")
    out["cumulative_share_of_world"] = np.where(
        out["world_cumulative_co2"] > 0,
        out["cumulative_co2"] / out["world_cumulative_co2"] * 100,
        np.nan,
    )
    return out.drop(columns=["world_cumulative_co2"])


def build_fuel_long(country_year: pd.DataFrame) -> pd.DataFrame:
    id_cols = [col for col in ["country", "iso_code", "year", "region", "income_group"] if col in country_year.columns]
    value_cols = [col for col in FUEL_COLUMNS if col in country_year.columns]
    if not value_cols:
        return pd.DataFrame(columns=id_cols + ["fuel_source", "value"])
    long = country_year.melt(id_vars=id_cols, value_vars=value_cols, var_name="fuel_column", value_name="value")
    long["fuel_source"] = long["fuel_column"].map(FUEL_COLUMNS)
    return long.drop(columns=["fuel_column"])

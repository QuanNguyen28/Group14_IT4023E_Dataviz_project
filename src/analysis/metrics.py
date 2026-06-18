"""KPI and metric calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def get_latest_year(df: pd.DataFrame) -> int | None:
    return int(df["year"].max()) if "year" in df.columns and not df.empty else None


def get_available_years(df: pd.DataFrame) -> list[int]:
    return sorted(df["year"].dropna().astype(int).unique().tolist()) if "year" in df.columns else []


def compute_share_of_world(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "share_of_world_co2" not in out.columns and {"co2", "year"}.issubset(out.columns):
        world = out.loc[out["country"].eq("World"), ["year", "co2"]].rename(columns={"co2": "world_co2"})
        out = out.merge(world, on="year", how="left")
        out["share_of_world_co2"] = np.where(out["world_co2"] > 0, out["co2"] / out["world_co2"] * 100, np.nan)
        out = out.drop(columns=["world_co2"])
    return out


def compute_global_kpis(country_df: pd.DataFrame, aggregate_df: pd.DataFrame, year: int, selected_country: str = "World") -> dict:
    year_countries = country_df.loc[country_df["year"].eq(year)].copy()
    year_aggregates = aggregate_df.loc[aggregate_df["year"].eq(year)].copy()
    world = year_aggregates.loc[year_aggregates["country"].eq("World")]
    world_row = world.iloc[0] if not world.empty else pd.Series(dtype="object")
    with_co2 = year_countries.dropna(subset=["co2"]) if "co2" in year_countries else pd.DataFrame()
    with_pc = year_countries.dropna(subset=["co2_per_capita"]) if "co2_per_capita" in year_countries else pd.DataFrame()
    largest = with_co2.nlargest(1, "co2").iloc[0] if not with_co2.empty else pd.Series(dtype="object")
    highest_pc = with_pc.nlargest(1, "co2_per_capita").iloc[0] if not with_pc.empty else pd.Series(dtype="object")
    selected_pool = pd.concat([year_countries, year_aggregates], ignore_index=True)
    selected = selected_pool.loc[selected_pool["country"].eq(selected_country)]
    selected_row = selected.iloc[0] if not selected.empty else world_row
    return {
        "global_co2": world_row.get("co2", np.nan),
        "world_per_capita": world_row.get("co2_per_capita", np.nan),
        "countries_reported": int(with_co2["country"].nunique()) if not with_co2.empty else 0,
        "largest_emitter": largest.get("country", "No data"),
        "largest_emitter_co2": largest.get("co2", np.nan),
        "largest_emitter_share": largest.get("share_of_world_co2", np.nan),
        "highest_per_capita": highest_pc.get("country", "No data"),
        "highest_per_capita_value": highest_pc.get("co2_per_capita", np.nan),
        "selected_country": selected_row.get("country", selected_country),
        "selected_co2": selected_row.get("co2", np.nan),
        "selected_share": selected_row.get("share_of_world_co2", np.nan),
    }


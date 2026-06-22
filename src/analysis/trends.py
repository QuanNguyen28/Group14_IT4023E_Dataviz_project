"""Trend, fuel mix, and insight generation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.constants import FUEL_COLUMNS


def compute_cagr(start: float, end: float, years: int) -> float:
    if years <= 0 or pd.isna(start) or pd.isna(end) or start <= 0 or end <= 0:
        return np.nan
    return (end / start) ** (1 / years) - 1


def compute_country_trends(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if "co2" not in df.columns or start_year >= end_year:
        return pd.DataFrame()
    start = df.loc[df["year"].eq(start_year), ["country", "co2"]].rename(columns={"co2": "co2_start"})
    end_cols = [c for c in ["country", "iso_code", "region", "income_group", "year", "co2", "co2_per_capita", "population", "cumulative_co2"] if c in df.columns]
    end = df.loc[df["year"].eq(end_year), end_cols].rename(columns={"co2": "co2_end"})
    out = end.merge(start, on="country", how="left")
    if {"gdp", "population"}.issubset(df.columns):
        economic = (
            df.loc[df["year"].between(start_year, end_year), ["country", "year", "gdp", "population"]]
            .dropna(subset=["gdp", "population"])
            .loc[lambda d: (d["gdp"] > 0) & (d["population"] > 0)]
            .sort_values(["country", "year"])
            .groupby("country", as_index=False)
            .tail(1)
            .rename(columns={"year": "gdp_year", "gdp": "latest_gdp", "population": "gdp_population"})
        )
        if not economic.empty:
            economic["gdp_per_capita"] = economic["latest_gdp"] / economic["gdp_population"]
            out = out.merge(economic[["country", "gdp_year", "latest_gdp", "gdp_per_capita"]], on="country", how="left")
    years = end_year - start_year
    out["co2_change"] = out["co2_end"] - out["co2_start"]
    out["co2_cagr"] = out.apply(lambda r: compute_cagr(r["co2_start"], r["co2_end"], years), axis=1)
    out["co2"] = out["co2_end"]
    return out


def get_fastest_increasing(trends: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return trends.dropna(subset=["co2_cagr"]).loc[lambda d: d["co2_cagr"] > 0].nlargest(n, "co2_cagr")


def get_fastest_declining(trends: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return trends.dropna(subset=["co2_cagr"]).loc[lambda d: d["co2_cagr"] < 0].nsmallest(n, "co2_cagr")


def compute_fuel_shares(fuel_long: pd.DataFrame, region: str) -> pd.DataFrame:
    if "region" not in fuel_long.columns:
        return pd.DataFrame()
    df = fuel_long.loc[fuel_long["region"].eq(region)].copy()
    if df.empty:
        return df
    df["value_for_share"] = df["value"].clip(lower=0)
    df = df.groupby(["year", "fuel_source"], as_index=False)["value_for_share"].sum()
    totals = df.groupby("year")["value_for_share"].transform("sum")
    df["share"] = np.where(totals > 0, df["value_for_share"] / totals * 100, np.nan)
    return df


def compute_fuel_absolute(fuel_long: pd.DataFrame, region: str) -> pd.DataFrame:
    """Year x fuel-source totals in their native Mt CO2 units (no normalization).

    Companion to compute_fuel_shares: that function expresses each fuel's
    contribution as a 0-100% share of the year's total, this one keeps the
    absolute Mt CO2 values so growth/decline in real volume is visible.
    """
    if "region" not in fuel_long.columns:
        return pd.DataFrame()
    df = fuel_long.loc[fuel_long["region"].eq(region)].copy()
    if df.empty:
        return df
    return df.groupby(["year", "fuel_source"], as_index=False)["value"].sum()


def compute_fuel_share_change(fuel_long: pd.DataFrame, region: str) -> pd.DataFrame:
    shares = compute_fuel_shares(fuel_long, region)
    if shares.empty:
        return pd.DataFrame(columns=["fuel_source", "start_share", "end_share", "change_pp"])
    years = sorted(shares.loc[shares["share"].notna(), "year"].unique())
    if len(years) < 2:
        return pd.DataFrame(columns=["fuel_source", "start_share", "end_share", "change_pp"])
    start_year, end_year = int(years[0]), int(years[-1])
    start = shares.loc[shares["year"].eq(start_year), ["fuel_source", "share"]].rename(columns={"share": "start_share"})
    end = shares.loc[shares["year"].eq(end_year), ["fuel_source", "share"]].rename(columns={"share": "end_share"})
    out = end.merge(start, on="fuel_source", how="outer").fillna(0)
    out["change_pp"] = out["end_share"] - out["start_share"]
    out["start_year"] = start_year
    out["end_year"] = end_year
    order = {name: i for i, name in enumerate(FUEL_COLUMNS.values())}
    return out.sort_values("fuel_source", key=lambda s: s.map(order).fillna(99))


def generate_page_1_insights(kpis: dict, top_emitters: pd.DataFrame, regional_totals: pd.DataFrame, selected_country: str) -> list[str]:
    insights = []
    if kpis.get("largest_emitter") != "No data":
        insights.append(f"{kpis['largest_emitter']} is the largest current emitter.")
    if not regional_totals.empty and "co2" in regional_totals:
        region = regional_totals.nlargest(1, "co2").iloc[0]
        insights.append(f"{region['country']} contributes the largest regional total.")
    if not top_emitters.empty and "share_of_world_co2" in top_emitters:
        insights.append(f"The top {len(top_emitters)} countries account for {top_emitters['share_of_world_co2'].sum():.1f}% of global CO2.")
    if kpis.get("highest_per_capita") != "No data":
        insights.append(f"Per-capita emissions peak in {kpis['highest_per_capita']}, showing large inequality.")
    insights.append(f"{selected_country} is selected for drill-down context.")
    return insights


def generate_page_2_insights(global_yearly: pd.DataFrame, responsibility: pd.DataFrame, regional_yearly: pd.DataFrame) -> list[str]:
    insights = ["Global CO2 stayed low for centuries, then accelerated after industrialization and especially after World War II."]
    if not responsibility.empty:
        insights.append(f"{responsibility.iloc[0]['country']} has the largest cumulative CO2 responsibility in the dataset.")
    if not regional_yearly.empty and "co2" in regional_yearly:
        latest = regional_yearly.loc[regional_yearly["year"].eq(regional_yearly["year"].max())]
        if not latest.empty:
            insights.append(f"{latest.nlargest(1, 'co2').iloc[0]['country']} is the largest regional emitter today.")
    insights.append("Current annual emissions and cumulative historical responsibility answer different questions.")
    return insights


def generate_page_3_insights(increasing: pd.DataFrame, declining: pd.DataFrame, fuel_change: pd.DataFrame, selected_region: str) -> list[str]:
    insights = []
    if not increasing.empty:
        insights.append(f"{increasing.iloc[0]['country']} has the fastest positive CO2 growth in the selected window.")
    if not declining.empty:
        insights.append(f"{declining.iloc[0]['country']} has the fastest decline in the selected window.")
    if not fuel_change.empty:
        biggest = fuel_change.reindex(fuel_change["change_pp"].abs().sort_values(ascending=False).index).iloc[0]
        insights.append(f"In {selected_region}, {biggest['fuel_source']} changed the most in the regional fuel mix.")
    insights.append("Top-right scatter countries combine high emissions with high growth and deserve priority attention.")
    return insights

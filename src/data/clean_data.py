"""Cleaning logic for the OWID CO2 dataset."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.utils.constants import METRIC_COLUMNS, NON_COUNTRY_AGGREGATES, NON_NEGATIVE_METRICS, REGIONS


COUNTRY_REGION_OVERRIDES = {
    "United States": "North America", "Canada": "North America", "Mexico": "North America",
    "China": "Asia", "India": "Asia", "Japan": "Asia", "Indonesia": "Asia", "Iran": "Asia",
    "Saudi Arabia": "Asia", "South Korea": "Asia", "Turkey": "Asia", "Qatar": "Asia",
    "Russia": "Europe", "Germany": "Europe", "United Kingdom": "Europe", "France": "Europe",
    "Italy": "Europe", "Poland": "Europe", "Ukraine": "Europe", "Estonia": "Europe",
    "Lithuania": "Europe", "Romania": "Europe", "Bulgaria": "Europe", "Czechia": "Europe",
    "Slovakia": "Europe", "Brazil": "South America", "Argentina": "South America",
    "Chile": "South America", "Colombia": "South America", "Peru": "South America",
    "South Africa": "Africa", "Egypt": "Africa", "Nigeria": "Africa", "Algeria": "Africa",
    "Morocco": "Africa", "Democratic Republic of Congo": "Africa", "DR Congo": "Africa",
    "Australia": "Oceania", "New Zealand": "Oceania",
}


def snake_case(name: str) -> str:
    name = re.sub(r"[^0-9a-zA-Z]+", "_", str(name).strip())
    return re.sub(r"_+", "_", name).strip("_").lower()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [snake_case(col) for col in out.columns]
    return out


def is_aggregate_row(row: pd.Series) -> bool:
    country = row.get("country")
    iso = row.get("iso_code")
    if country in NON_COUNTRY_AGGREGATES or country in REGIONS:
        return True
    if isinstance(iso, str) and iso.startswith("OWID_"):
        return True
    if not isinstance(iso, str) or len(iso) != 3:
        return country not in COUNTRY_REGION_OVERRIDES
    return False


def infer_region(row: pd.Series) -> str:
    country = row.get("country")
    continent = row.get("continent")
    if continent in REGIONS:
        return continent
    if country in REGIONS:
        return country
    if country in COUNTRY_REGION_OVERRIDES:
        return COUNTRY_REGION_OVERRIDES[country]
    return "Unknown"


def infer_income_group(row: pd.Series) -> str:
    if "income_group" in row and pd.notna(row["income_group"]):
        return str(row["income_group"])
    country = row.get("country", "")
    if country in {
        "High-income countries", "Upper-middle-income countries",
        "Lower-middle-income countries", "Low-income countries",
    }:
        return country.replace(" countries", "")
    return "Unknown"


def clean_co2_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean OWID data while preserving optional columns when present."""
    out = standardize_columns(df)
    if "year" not in out.columns or "country" not in out.columns:
        raise ValueError("The OWID CO2 dataset must contain at least country and year columns.")

    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out = out.dropna(subset=["country", "year"]).copy()
    out["year"] = out["year"].astype(int)

    for col in [c for c in METRIC_COLUMNS if c in out.columns]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in [c for c in NON_NEGATIVE_METRICS if c in out.columns]:
        out.loc[out[col] < 0, col] = np.nan

    if "iso_code" not in out.columns:
        out["iso_code"] = np.nan
    out["is_aggregate"] = out.apply(is_aggregate_row, axis=1)
    out["region"] = out.apply(infer_region, axis=1)
    out["income_group"] = out.apply(infer_income_group, axis=1)

    if "gdp" in out.columns and "co2" in out.columns:
        out["co2_per_gdp"] = np.where(out["gdp"] > 0, out["co2"] / out["gdp"], np.nan)
    return out.sort_values(["country", "year"]).reset_index(drop=True)

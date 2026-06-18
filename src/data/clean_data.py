"""Cleaning logic for the OWID CO2 dataset."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
try:
    import country_converter as coco
except ImportError:  # pragma: no cover - optional at runtime, listed in requirements for app use.
    coco = None

from src.utils.constants import METRIC_COLUMNS, NON_COUNTRY_AGGREGATES, NON_NEGATIVE_METRICS, REGIONS


COUNTRY_REGION_OVERRIDES = {
    # --- Asia ---
    "Afghanistan": "Asia",
    "Armenia": "Asia",
    "Azerbaijan": "Asia",
    "Bahrain": "Asia",
    "Bangladesh": "Asia",
    "Bhutan": "Asia",
    "Brunei": "Asia",
    "Cambodia": "Asia",
    "China": "Asia",
    "Cyprus": "Asia",
    "East Timor": "Asia",
    "Georgia": "Asia",
    "Hong Kong": "Asia",
    "India": "Asia",
    "Indonesia": "Asia",
    "Iran": "Asia",
    "Iraq": "Asia",
    "Israel": "Asia",
    "Japan": "Asia",
    "Jordan": "Asia",
    "Kazakhstan": "Asia",
    "Kuwait": "Asia",
    "Kyrgyzstan": "Asia",
    "Laos": "Asia",
    "Lebanon": "Asia",
    "Macao": "Asia",
    "Malaysia": "Asia",
    "Maldives": "Asia",
    "Mongolia": "Asia",
    "Myanmar": "Asia",
    "Nepal": "Asia",
    "North Korea": "Asia",
    "Oman": "Asia",
    "Pakistan": "Asia",
    "Palestine": "Asia",
    "Philippines": "Asia",
    "Qatar": "Asia",
    "Russia": "Asia",          # geographically transcontinental; placed in Asia per OWID convention
    "Saudi Arabia": "Asia",
    "Singapore": "Asia",
    "South Korea": "Asia",
    "Sri Lanka": "Asia",
    "Syria": "Asia",
    "Taiwan": "Asia",
    "Tajikistan": "Asia",
    "Thailand": "Asia",
    "Turkey": "Asia",
    "Turkmenistan": "Asia",
    "United Arab Emirates": "Asia",
    "Uzbekistan": "Asia",
    "Vietnam": "Asia",
    "Yemen": "Asia",
 
    # --- Europe ---
    "Albania": "Europe",
    "Andorra": "Europe",
    "Austria": "Europe",
    "Belarus": "Europe",
    "Belgium": "Europe",
    "Bosnia and Herzegovina": "Europe",
    "Bulgaria": "Europe",
    "Croatia": "Europe",
    "Czechia": "Europe",
    "Denmark": "Europe",
    "Estonia": "Europe",
    "Faroe Islands": "Europe",
    "Finland": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Greece": "Europe",
    "Greenland": "Europe",   # territory of Denmark
    "Hungary": "Europe",
    "Iceland": "Europe",
    "Ireland": "Europe",
    "Italy": "Europe",
    "Kosovo": "Europe",
    "Latvia": "Europe",
    "Liechtenstein": "Europe",
    "Lithuania": "Europe",
    "Luxembourg": "Europe",
    "Malta": "Europe",
    "Moldova": "Europe",
    "Monaco": "Europe",
    "Montenegro": "Europe",
    "Netherlands": "Europe",
    "North Macedonia": "Europe",
    "Norway": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Romania": "Europe",
    "San Marino": "Europe",
    "Serbia": "Europe",
    "Slovakia": "Europe",
    "Slovenia": "Europe",
    "Spain": "Europe",
    "Sweden": "Europe",
    "Switzerland": "Europe",
    "Ukraine": "Europe",
    "United Kingdom": "Europe",
    "Vatican": "Europe",
 
    # --- North America ---
    "Anguilla": "North America",
    "Antigua and Barbuda": "North America",
    "Aruba": "North America",
    "Bahamas": "North America",
    "Barbados": "North America",
    "Belize": "North America",
    "Bermuda": "North America",
    "Bonaire Sint Eustatius and Saba": "North America",
    "British Virgin Islands": "North America",
    "Canada": "North America",
    "Cayman Islands": "North America",
    "Costa Rica": "North America",
    "Cuba": "North America",
    "Curacao": "North America",
    "Dominica": "North America",
    "Dominican Republic": "North America",
    "El Salvador": "North America",
    "Grenada": "North America",
    "Guatemala": "North America",
    "Haiti": "North America",
    "Honduras": "North America",
    "Jamaica": "North America",
    "Mexico": "North America",
    "Montserrat": "North America",
    "Nicaragua": "North America",
    "Panama": "North America",
    "Saint Kitts and Nevis": "North America",
    "Saint Lucia": "North America",
    "Saint Pierre and Miquelon": "North America",
    "Saint Vincent and the Grenadines": "North America",
    "Sint Maarten (Dutch part)": "North America",
    "Trinidad and Tobago": "North America",
    "Turks and Caicos Islands": "North America",
    "United States": "North America",
 
    # --- South America ---
    "Argentina": "South America",
    "Bolivia": "South America",
    "Brazil": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Ecuador": "South America",
    "Guyana": "South America",
    "Paraguay": "South America",
    "Peru": "South America",
    "Suriname": "South America",
    "Uruguay": "South America",
    "Venezuela": "South America",
 
    # --- Africa ---
    "Algeria": "Africa",
    "Angola": "Africa",
    "Benin": "Africa",
    "Botswana": "Africa",
    "Burkina Faso": "Africa",
    "Burundi": "Africa",
    "Cameroon": "Africa",
    "Cape Verde": "Africa",
    "Central African Republic": "Africa",
    "Chad": "Africa",
    "Comoros": "Africa",
    "Congo": "Africa",
    "Cote d'Ivoire": "Africa",
    "Democratic Republic of Congo": "Africa",
    "Djibouti": "Africa",
    "Egypt": "Africa",
    "Equatorial Guinea": "Africa",
    "Eritrea": "Africa",
    "Eswatini": "Africa",
    "Ethiopia": "Africa",
    "Gabon": "Africa",
    "Gambia": "Africa",
    "Ghana": "Africa",
    "Guinea": "Africa",
    "Guinea-Bissau": "Africa",
    "Kenya": "Africa",
    "Lesotho": "Africa",
    "Liberia": "Africa",
    "Libya": "Africa",
    "Madagascar": "Africa",
    "Malawi": "Africa",
    "Mali": "Africa",
    "Mauritania": "Africa",
    "Mauritius": "Africa",
    "Morocco": "Africa",
    "Mozambique": "Africa",
    "Namibia": "Africa",
    "Niger": "Africa",
    "Nigeria": "Africa",
    "Rwanda": "Africa",
    "Saint Helena": "Africa",
    "Sao Tome and Principe": "Africa",
    "Senegal": "Africa",
    "Seychelles": "Africa",
    "Sierra Leone": "Africa",
    "Somalia": "Africa",
    "South Africa": "Africa",
    "South Sudan": "Africa",
    "Sudan": "Africa",
    "Tanzania": "Africa",
    "Togo": "Africa",
    "Tunisia": "Africa",
    "Uganda": "Africa",
    "Zambia": "Africa",
    "Zimbabwe": "Africa",
 
    # --- Oceania ---
    "Antarctica": "Oceania",
    "Australia": "Oceania",
    "Christmas Island": "Oceania",
    "Cook Islands": "Oceania",
    "Fiji": "Oceania",
    "French Polynesia": "Oceania",
    "Kiribati": "Oceania",
    "Marshall Islands": "Oceania",
    "Micronesia (country)": "Oceania",
    "Nauru": "Oceania",
    "New Caledonia": "Oceania",
    "New Zealand": "Oceania",
    "Niue": "Oceania",
    "Palau": "Oceania",
    "Papua New Guinea": "Oceania",
    "Samoa": "Oceania",
    "Solomon Islands": "Oceania",
    "Tonga": "Oceania",
    "Tuvalu": "Oceania",
    "Vanuatu": "Oceania",
    "Wallis and Futuna": "Oceania",
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


def enrich_missing_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing country regions from ISO3 metadata when available."""
    if coco is None or df.empty or "region" not in df.columns or "iso_code" not in df.columns:
        return df
    out = df.copy()
    iso = out["iso_code"].astype("string")
    missing = out["region"].eq("Unknown") & iso.str.len().eq(3) & ~iso.str.startswith("OWID_", na=False)
    if not missing.any():
        return out
    unique_iso = out.loc[missing, "iso_code"].dropna().astype(str).unique().tolist()
    converted = coco.convert(
        names=unique_iso,
        src="ISO3",
        to="continent_7",
        not_found="Unknown",
    )
    iso_to_region = pd.Series(converted, index=unique_iso).where(lambda s: s.isin(REGIONS), "Unknown").to_dict()
    out.loc[missing, "region"] = out.loc[missing, "iso_code"].map(iso_to_region).fillna("Unknown")
    return out


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
    out = enrich_missing_regions(out)
    out["income_group"] = out.apply(infer_income_group, axis=1)

    if "gdp" in out.columns and "co2" in out.columns:
        out["co2_per_gdp"] = np.where(out["gdp"] > 0, out["co2"] / out["gdp"], np.nan)
    return out.sort_values(["country", "year"]).reset_index(drop=True)

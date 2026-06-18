"""Build processed and aggregated datasets for the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd

from src.data.clean_data import clean_co2_data
from src.data.feature_engineering import add_cagr_features, add_cumulative_share, add_previous_year_values, add_world_shares, build_fuel_long
from src.data.load_data import load_raw_co2
from src.utils.constants import (
    AGGREGATED_DIR, AGGREGATES_PATH, CLEANED_PATH, COUNTRY_LATEST_PATH, COUNTRY_YEAR_PATH,
    FUEL_LONG_PATH, GLOBAL_YEARLY_PATH, LATEST_YEAR_PATH, PROCESSED_DIR, REGIONAL_YEARLY_PATH,
    TRENDS_PATH,
)
from src.utils.helpers import ensure_dirs


def build_all() -> dict[str, pd.DataFrame]:
    """Run the full raw-to-dashboard data pipeline."""
    ensure_dirs([PROCESSED_DIR, AGGREGATED_DIR])
    raw = load_raw_co2()
    cleaned = clean_co2_data(raw)
    cleaned = add_world_shares(add_cumulative_share(add_previous_year_values(add_cagr_features(cleaned, 5))))

    countries = cleaned.loc[~cleaned["is_aggregate"]].copy()
    aggregates = cleaned.loc[cleaned["is_aggregate"]].copy()
    latest_year = int(cleaned["year"].max())
    latest = countries.loc[countries["year"].eq(latest_year)].copy()
    trends = countries.loc[countries["year"].between(latest_year - 5, latest_year)].copy()
    fuel_long = build_fuel_long(countries)

    global_yearly = cleaned.loc[cleaned["country"].eq("World")].copy()
    regional_yearly = aggregates.loc[aggregates["country"].isin(["Asia", "Europe", "North America", "South America", "Africa", "Oceania"])].copy()
    country_latest = latest.copy()

    outputs = {
        str(CLEANED_PATH): cleaned,
        str(COUNTRY_YEAR_PATH): countries,
        str(AGGREGATES_PATH): aggregates,
        str(LATEST_YEAR_PATH): latest,
        str(TRENDS_PATH): trends,
        str(FUEL_LONG_PATH): fuel_long,
        str(GLOBAL_YEARLY_PATH): global_yearly,
        str(REGIONAL_YEARLY_PATH): regional_yearly,
        str(COUNTRY_LATEST_PATH): country_latest,
    }
    for path, df in outputs.items():
        df.to_csv(path, index=False)
    return {
        "cleaned": cleaned, "countries": countries, "aggregates": aggregates,
        "latest": latest, "trends": trends, "fuel_long": fuel_long,
        "global_yearly": global_yearly, "regional_yearly": regional_yearly,
    }


if __name__ == "__main__":
    try:
        built = build_all()
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from None
    else:
        print("Built CO2 dashboard datasets:")
        for name, df in built.items():
            print(f"- {name}: {len(df):,} rows")

"""Shared constants for paths, metrics, colors, and semantic groups."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
AGGREGATED_DIR = DATA_DIR / "aggregated"

RAW_CO2_PATH = RAW_DIR / "owid-co2-data.csv"
CLEANED_PATH = PROCESSED_DIR / "co2_cleaned.csv"
COUNTRY_YEAR_PATH = PROCESSED_DIR / "co2_country_year.csv"
AGGREGATES_PATH = PROCESSED_DIR / "co2_aggregates.csv"
LATEST_YEAR_PATH = PROCESSED_DIR / "co2_latest_year.csv"
TRENDS_PATH = PROCESSED_DIR / "co2_trends.csv"
FUEL_LONG_PATH = PROCESSED_DIR / "co2_fuel_long.csv"
GLOBAL_YEARLY_PATH = AGGREGATED_DIR / "global_yearly.csv"
REGIONAL_YEARLY_PATH = AGGREGATED_DIR / "regional_yearly.csv"
COUNTRY_LATEST_PATH = AGGREGATED_DIR / "country_latest_metrics.csv"

REGIONS = ["Asia", "Europe", "North America", "South America", "Africa", "Oceania"]
REGION_AGGREGATES = set(REGIONS)
NON_COUNTRY_AGGREGATES = {
    "World", "Asia", "Europe", "Africa", "North America", "South America", "Oceania",
    "European Union", "High-income countries", "Upper-middle-income countries",
    "Lower-middle-income countries", "Low-income countries", "International aviation",
    "International shipping",
}

METRIC_COLUMNS = [
    "co2", "co2_per_capita", "cumulative_co2", "population", "gdp", "coal_co2",
    "oil_co2", "gas_co2", "cement_co2", "flaring_co2", "land_use_change_co2",
    "methane", "nitrous_oxide", "total_ghg", "primary_energy_consumption",
    "energy_per_capita",
]
NON_NEGATIVE_METRICS = [col for col in METRIC_COLUMNS if col != "land_use_change_co2"]
FUEL_COLUMNS = {
    "coal_co2": "Coal",
    "oil_co2": "Oil",
    "gas_co2": "Gas",
    "cement_co2": "Cement",
    "flaring_co2": "Flaring",
    "land_use_change_co2": "Land-use Change",
}

METRIC_LABELS = {"co2": "Total CO2", "co2_per_capita": "CO2 Per Capita"}
METRIC_UNITS = {"co2": "Mt CO2", "co2_per_capita": "t / person", "cumulative_co2": "Mt CO2"}

REGION_COLORS = {
    "Asia": "#D55E00",
    "Europe": "#0072B2",
    "North America": "#009E73",
    "South America": "#E69F00",
    "Africa": "#CC79A7",
    "Oceania": "#56B4E9",
    "Unknown": "#8A94A6",
}
FUEL_COLORS = {
    "Coal": "#000000",
    "Oil": "#D55E00",
    "Gas": "#0072B2",
    "Cement": "#CC79A7",
    "Land-use Change": "#009E73",
    "Flaring": "#F0E442",
}

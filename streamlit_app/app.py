"""Main Streamlit entry point for the Global CO2 dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.build_datasets import build_all
from src.data.clean_data import enrich_missing_regions
from src.data.load_data import load_csv_if_exists
from src.utils.constants import AGGREGATES_PATH, COUNTRY_YEAR_PATH, FUEL_LONG_PATH, GLOBAL_YEARLY_PATH, REGIONAL_YEARLY_PATH
from streamlit_app.components.sidebar import render_navigation
from streamlit_app.pages.current_trend_analysis import render_current_trend_analysis
from streamlit_app.pages.global_snapshot import render_global_snapshot
from streamlit_app.pages.historical_evolution import render_historical_evolution
from streamlit_app.styles import CSS


st.set_page_config(page_title="Global CO2 Dashboard", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_dashboard_data():
    country = load_csv_if_exists(COUNTRY_YEAR_PATH)
    aggregates = load_csv_if_exists(AGGREGATES_PATH)
    fuel = load_csv_if_exists(FUEL_LONG_PATH)
    global_yearly = load_csv_if_exists(GLOBAL_YEARLY_PATH)
    regional_yearly = load_csv_if_exists(REGIONAL_YEARLY_PATH)
    if any(x is None for x in [country, aggregates, fuel, global_yearly, regional_yearly]):
        built = build_all()
        return built["countries"], built["aggregates"], built["fuel_long"], built["global_yearly"], built["regional_yearly"]
    return enrich_missing_regions(country), aggregates, enrich_missing_regions(fuel), global_yearly, regional_yearly


try:
    country_df, aggregate_df, fuel_long, global_yearly, regional_yearly = load_dashboard_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.info("Run `python -m src.data.build_datasets` after placing `owid-co2-data.csv` in `data/raw/`.")
    st.stop()

page = render_navigation()

if page == "Global Snapshot":
    render_global_snapshot(country_df, aggregate_df)
elif page == "Historical Evolution":
    render_historical_evolution(country_df, aggregate_df, global_yearly, regional_yearly)
else:
    render_current_trend_analysis(country_df, fuel_long)

st.sidebar.markdown("<div class='sidebar-caption'>Last updated from latest available OWID year.</div>", unsafe_allow_html=True)

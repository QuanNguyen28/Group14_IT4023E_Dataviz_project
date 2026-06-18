"""Page 1: Global Snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.analysis.metrics import compute_global_kpis
from src.analysis.rankings import compute_regional_totals, get_top_emitters
from src.analysis.trends import generate_page_1_insights
from src.visualization.charts import create_top_emitters_bar, create_treemap
from src.visualization.maps import create_choropleth_map
from streamlit_app.components.kpi_cards import render_kpis
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, insight_list, page_header, section_header, single_insight
from streamlit_app.components.sidebar import common_filter_values


def _filter(df, region, income):
    out = df.copy()
    if region != "All" and "region" in out:
        out = out[out["region"].eq(region)]
    if income != "All" and "income_group" in out:
        out = out[out["income_group"].eq(income)]
    return out


def render_global_snapshot(country_df, aggregate_df) -> None:
    page_header("GLOBAL SNAPSHOT", "What does the world look like today?", "#D94C45", "Current-state overview")
    years, regions, incomes, countries = common_filter_values(country_df)
    min_year, max_year = min(years), max(years)
    default_start = max(min_year, max_year - 5)
    with st.sidebar:
        st.markdown("### Filters")
        if min_year < max_year:
            year_start, year = st.slider(
                "Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(default_start, max_year),
            )
        else:
            year_start = year = max_year
            st.info(f"Only {year} is available.")
        metric_label = st.radio("Metric", ["Total CO2", "CO2 Per Capita"], horizontal=True)
        region = st.selectbox("Region", regions)
        income = st.selectbox("Income Group", incomes)
        selected_country = st.selectbox("Selected Country", countries)
    metric = "co2" if metric_label == "Total CO2" else "co2_per_capita"
    filtered = _filter(country_df, region, income)

    kpis = compute_global_kpis(country_df, aggregate_df, year, selected_country)
    filter_summary([
        ("Year Range", f"{year_start}-{year}"),
        ("Selected Year", year),
        ("Metric", metric_label),
        ("Region", region),
        ("Income", income),
        ("Drill-down", selected_country),
    ])
    render_kpis(kpis)
    section_header("Spatial and Regional Composition", "Country distribution on the left, regional part-to-whole structure on the right.", "Snapshot")

    left, right = st.columns([1.25, 1])
    with left:
        st.plotly_chart(create_choropleth_map(filtered, year, metric), width="stretch", config=PLOTLY_CONFIG)
        single_insight("Use the map to compare country-level distribution across the selected metric.")
    with right:
        st.plotly_chart(create_treemap(filtered, compute_regional_totals(aggregate_df, year), year), width="stretch", config=PLOTLY_CONFIG)
        single_insight("Regional blocks show which parts of the world dominate the selected year.")

    top = get_top_emitters(filtered, year, metric, 10)
    regional = compute_regional_totals(aggregate_df, year)
    section_header("Country Ranking and Executive Interpretation", "Sorted bars preserve precise comparison; insights summarize what changed attention should focus on.", "Ranking")
    bottom_left, bottom_right = st.columns([1.45, 1])
    with bottom_left:
        st.plotly_chart(create_top_emitters_bar(top, metric, f"Top 10 Countries by {metric_label}"), width="stretch", config=PLOTLY_CONFIG)
        single_insight("The top emitters concentrate a large share of global CO2 emissions.")
    with bottom_right:
        insight_list(generate_page_1_insights(kpis, top, regional, selected_country))

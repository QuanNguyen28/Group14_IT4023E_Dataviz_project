"""Page 3: Current Trend Analysis."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.analysis.trends import (
    compute_country_trends, compute_fuel_share_change, generate_page_3_insights,
    get_fastest_declining, get_fastest_increasing,
)
from src.visualization.charts import (
    create_bubble_scatter, create_fastest_declining_bar, create_fastest_increasing_bar,
    create_fuel_decomposition_area, create_fuel_share_change_table_or_panel,
)
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, insight_list, page_header, section_header
from streamlit_app.components.sidebar import common_filter_values


def _fuel_country_options(countries, fuel_long):
    country_set = {country for country in countries if country != "World"}
    if fuel_long.empty or "country" not in fuel_long or "value" not in fuel_long:
        options = sorted(country_set) or list(countries)
    else:
        with_data = fuel_long.loc[fuel_long["value"].fillna(0).gt(0), "country"].dropna().unique()
        options = sorted(country_set.intersection(with_data))
        if not options:
            options = sorted(country_set) or list(countries)
    preferred = ["China", "United States", "India", "Russia", "Japan", "Germany"]
    default = next((country for country in preferred if country in options), options[0])
    return options, options.index(default)


def render_current_trend_analysis(country_df, fuel_long) -> None:
    page_header("CURRENT TREND ANALYSIS", "Who is changing fastest today?", "#D94C45", "Momentum scanner")
    years, regions, incomes, countries = common_filter_values(country_df)
    latest = max(years)
    earliest = min(years)
    default_start = max(min(years), latest - 5)
    fuel_options, fuel_default_index = _fuel_country_options(countries, fuel_long)
    with st.sidebar:
        st.markdown("### Filters")
        if earliest >= latest:
            st.warning("At least two years are required for trend analysis.")
            return
        base_year, end_year = st.slider(
            "Compare Years",
            min_value=earliest,
            max_value=latest,
            value=(default_start, latest),
        )
        if base_year >= end_year:
            st.warning("Move the right handle after the left handle to compare trends.")
            return
        _ = st.selectbox("Time Window", ["Selected Years", "5-Year (CAGR)"], index=1)
        region = st.selectbox("Region", regions)
        income = st.selectbox("Income Group", incomes)
        y_label = st.radio("Metric (Y-Axis)", ["CO2 Per Capita", "Total CO2"], horizontal=True)
        selected_country = st.selectbox("Fuel Country", fuel_options, index=fuel_default_index)
    y_metric = "co2_per_capita" if y_label == "CO2 Per Capita" else "co2"

    trends = compute_country_trends(country_df, base_year, end_year)
    if region != "All" and "region" in trends:
        trends = trends[trends["region"].eq(region)]
    if income != "All" and "income_group" in trends:
        trends = trends[trends["income_group"].eq(income)]
    increasing = get_fastest_increasing(trends, 10)
    declining = get_fastest_declining(trends, 10)
    fuel_change = compute_fuel_share_change(fuel_long, selected_country)

    filter_summary([
        ("Window", f"{base_year}-{end_year}"),
        ("Y-axis", y_label),
        ("Region", region),
        ("Income", income),
        ("Fuel country", selected_country),
    ])
    section_header("Growth, Emissions Profile, and Momentum Rankings", "Bubble size encodes current scale; the two rankings isolate fastest movers.", "Signal Scan")
    top_left, top_mid, top_right = st.columns([1.55, .78, .78])
    with top_left:
        st.plotly_chart(create_bubble_scatter(trends, y_metric), width="stretch", config=PLOTLY_CONFIG)
    with top_mid:
        st.plotly_chart(create_fastest_increasing_bar(increasing), width="stretch", config=PLOTLY_CONFIG)
    with top_right:
        st.plotly_chart(create_fastest_declining_bar(declining), width="stretch", config=PLOTLY_CONFIG)

    section_header("Fuel Mix Decomposition", "A 100 percent stacked area chart shows how the selected country's emissions sources are changing.", "Decomposition")
    bottom_left, bottom_right = st.columns([1.65, .75])
    with bottom_left:
        st.plotly_chart(create_fuel_decomposition_area(fuel_long, selected_country), width="stretch", config=PLOTLY_CONFIG)
    with bottom_right:
        st.plotly_chart(create_fuel_share_change_table_or_panel(fuel_change), width="stretch", config=PLOTLY_CONFIG)
        insight_list(generate_page_3_insights(increasing, declining, fuel_change, selected_country), "Trend Insights")

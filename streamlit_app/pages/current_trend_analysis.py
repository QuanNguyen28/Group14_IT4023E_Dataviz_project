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
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, insight_list, page_header, section_header, single_insight
from streamlit_app.components.sidebar import common_filter_values


def _fuel_region_options(regions, fuel_long):
    region_set = {region for region in regions if region != "All"}
    if fuel_long.empty or "region" not in fuel_long or "value" not in fuel_long:
        options = sorted(region_set)
    else:
        with_data = fuel_long.loc[fuel_long["value"].fillna(0).gt(0), "region"].dropna().unique()
        options = sorted(region_set.intersection(with_data))
    if not options:
        options = sorted(region_set) or ["Asia"]
    default = "Asia" if "Asia" in options else options[0]
    return options, options.index(default)


def render_current_trend_analysis(country_df, fuel_long) -> None:
    page_header("CURRENT TREND ANALYSIS", "Who is changing fastest today?", "#D94C45", "Momentum scanner")
    years, regions, _, _ = common_filter_values(country_df)
    latest = max(years)
    earliest = min(years)
    base_year, end_year = 2022, 2024
    fuel_options, fuel_default_index = _fuel_region_options(regions, fuel_long)
    with st.sidebar:
        st.markdown("### Filters")
        if earliest > base_year or latest < end_year:
            st.warning("The 2022-2024 trend window is not available in this dataset.")
            return
        region = st.selectbox("Region", regions)
        selected_fuel_region = st.selectbox("Fuel Region", fuel_options, index=fuel_default_index)
    y_label = "GDP Per Capita"
    y_metric = "gdp_per_capita"

    trends = compute_country_trends(country_df, base_year, end_year)
    if region != "All" and "region" in trends:
        trends = trends[trends["region"].eq(region)]
    increasing = get_fastest_increasing(trends, 10)
    declining = get_fastest_declining(trends, 10)
    fuel_change = compute_fuel_share_change(fuel_long, selected_fuel_region)

    filter_summary([
        ("Window", f"{base_year}-{end_year}"),
        ("Y-axis", y_label),
        ("Region", region),
        ("Fuel region", selected_fuel_region),
    ])
    section_header("Growth, Emissions Profile, and Momentum Rankings", "Bubble size encodes current scale; the two rankings isolate fastest movers.", "Signal Scan")
    top_left, top_mid, top_right = st.columns([1.48, .9, .9])
    with top_left:
        st.plotly_chart(create_bubble_scatter(trends, y_metric), width="stretch", config=PLOTLY_CONFIG)
        single_insight("CO2 CAGR is fixed to 2022-2024; Y-axis is latest available GDP per capita in that window; bubble size is 2024 total CO2.")
    with top_mid:
        st.plotly_chart(create_fastest_increasing_bar(increasing), width="stretch", config=PLOTLY_CONFIG)
        single_insight("Emerging fast movers may shape future emissions.")
    with top_right:
        st.plotly_chart(create_fastest_declining_bar(declining), width="stretch", config=PLOTLY_CONFIG)
        single_insight("Declining countries show where reductions are already visible.")

    section_header("Fuel Mix Decomposition", "A 100 percent stacked area chart shows how the selected region's emissions sources are changing.", "Decomposition")
    bottom_left, bottom_right = st.columns([1.65, .75])
    with bottom_left:
        st.plotly_chart(create_fuel_decomposition_area(fuel_long, selected_fuel_region), width="stretch", config=PLOTLY_CONFIG)
        single_insight("Fuel mix shares aggregate all countries in the selected region.")
    with bottom_right:
        st.plotly_chart(create_fuel_share_change_table_or_panel(fuel_change), width="stretch", config=PLOTLY_CONFIG)
        insight_list(generate_page_3_insights(increasing, declining, fuel_change, selected_fuel_region), "Trend Insights")

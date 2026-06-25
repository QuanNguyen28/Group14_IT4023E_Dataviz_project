"""Page 3: Current Trend Analysis."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.analysis.trends import (
    compute_country_trends,
    compute_fuel_share_change_range,
    compute_fuel_shares,
)
from src.visualization.charts import (
    create_bubble_scatter,
    create_fuel_decomposition_area,
    create_fuel_slope_graph,
    create_growth_volume_scatter,
)
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, page_header, section_header
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


def _fuel_share_year_range(fuel_long, region):
    """Return (min_year, max_year, default_start, default_end) for the slope slider."""
    shares = compute_fuel_shares(fuel_long, region)
    if shares.empty:
        return 1990, 2024, 2000, 2024
    valid = shares.loc[shares["share"].notna() & shares["share"].gt(0), "year"]
    if valid.empty:
        return 1990, 2024, 2000, 2024
    y_min, y_max = int(valid.min()), int(valid.max())
    default_start = max(y_min, y_max - 30)   # sensible 30-year default window
    return y_min, y_max, default_start, y_max


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

        # ── Time range slider moved to sidebar ──────────────────────────────
        st.markdown("#### Fuel Share Comparison Window")
        s_min, s_max, s_default_start, s_default_end = _fuel_share_year_range(
            fuel_long, selected_fuel_region
        )
        slope_start, slope_end = st.select_slider(
            "Year range",
            options=list(range(s_min, s_max + 1)),
            value=(s_default_start, s_default_end),
            help="Drag the handles to choose the start and end years for the slope graph and fuel mix area chart.",
        )

    y_label = "GDP Per Capita"
    y_metric = "gdp_per_capita"

    trends = compute_country_trends(country_df, base_year, end_year)
    if region != "All" and "region" in trends:
        trends = trends[trends["region"].eq(region)]

    filter_summary([
        ("Window", f"{base_year}-{end_year}"),
        ("Y-axis", y_label),
        ("Region", region),
        ("Fuel region", selected_fuel_region),
        ("Fuel years", f"{slope_start}–{slope_end}"),
    ])

    # ── Scatter section ──────────────────────────────────────────────────────
    section_header(
        "Growth Rate & Emissions Profile",
        "Left: growth vs wealth (bubble size = volume). Right: growth rate vs absolute volume.",
        "Signal Scan",
    )
    top_left, top_right = st.columns([1, 1])
    with top_left:
        st.plotly_chart(create_bubble_scatter(trends, y_metric), width="stretch", config=PLOTLY_CONFIG)
    with top_right:
        st.plotly_chart(
            create_growth_volume_scatter(trends, label_n=0),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

    # ── Fuel mix section ─────────────────────────────────────────────────────
    section_header(
        "Fuel Mix Decomposition",
        "Left: absolute stacked area of emissions by source (filtered to selected year range). Right: slope graph showing how each fuel's share shifted between the two chosen years.",
        "Decomposition",
    )

    fuel_change = compute_fuel_share_change_range(
        fuel_long, selected_fuel_region, slope_start, slope_end
    )

    # Filter fuel_long to selected time range for the area chart
    fuel_long_filtered = fuel_long[fuel_long["year"].between(slope_start, slope_end)] if not fuel_long.empty else fuel_long

    bottom_left, bottom_right = st.columns([1.55, 0.85])
    with bottom_left:
        st.plotly_chart(
            create_fuel_decomposition_area(fuel_long_filtered, selected_fuel_region),
            width="stretch",
            config=PLOTLY_CONFIG,
        )
    with bottom_right:
        st.plotly_chart(
            create_fuel_slope_graph(fuel_change),
            width="stretch",
            config=PLOTLY_CONFIG,
        )

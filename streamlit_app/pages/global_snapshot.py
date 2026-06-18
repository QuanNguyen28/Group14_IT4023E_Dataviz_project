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


def _filter(df, region):
    out = df.copy()
    if region != "All" and "region" in out:
        out = out[out["region"].eq(region)]
    return out


def _selected_country_from_event(event) -> str | None:
    if not event:
        return None
    points = event.get("selection", {}).get("points", []) if isinstance(event, dict) else event.selection.points
    if not points:
        return None
    point = points[0]
    customdata = point.get("customdata") if isinstance(point, dict) else getattr(point, "customdata", None)
    if customdata is not None and len(customdata) > 0:
        country = customdata[0]
        return country if country != "World" else None
    label = point.get("label") if isinstance(point, dict) else getattr(point, "label", None)
    return label if label and label != "World" else None


def render_global_snapshot(country_df, aggregate_df) -> None:
    page_header("GLOBAL SNAPSHOT", "What does the world look like today?", "#D94C45", "Current-state overview")
    years, regions, _, countries = common_filter_values(country_df)
    year = max(years)
    if "page1_country_select" not in st.session_state:
        st.session_state.page1_country_select = "World"
    pending_country = st.session_state.pop("page1_pending_country", None)
    if pending_country in countries:
        st.session_state.page1_country_select = pending_country
    with st.sidebar:
        st.markdown("### Filters")
        st.caption(f"Snapshot uses latest available year: {year}.")
        metric_label = st.radio("Metric", ["Total CO2", "CO2 Per Capita"], horizontal=True)
        region = st.selectbox("Region", regions)
        selected_country = st.selectbox(
            "Selected Country",
            countries,
            key="page1_country_select",
        )
    metric = "co2" if metric_label == "Total CO2" else "co2_per_capita"
    filtered = _filter(country_df, region)
    selected_country = st.session_state.page1_country_select

    kpis = compute_global_kpis(country_df, aggregate_df, year, selected_country)
    filter_summary([
        ("Selected Year", year),
        ("Metric", metric_label),
        ("Region", region),
        ("Drill-down", selected_country),
    ])
    render_kpis(kpis)
    section_header("Spatial and Regional Composition", "Country distribution on the left, regional part-to-whole structure on the right.", "Snapshot")

    left, right = st.columns([1.25, 1])
    with left:
        map_event = st.plotly_chart(
            create_choropleth_map(filtered, year, metric, selected_country),
            width="stretch",
            config=PLOTLY_CONFIG,
            key="page1_region_map",
            on_select="rerun",
            selection_mode="points",
        )
        map_country = _selected_country_from_event(map_event)
        if map_country and map_country in countries and map_country != st.session_state.page1_country_select:
            st.session_state.page1_pending_country = map_country
            st.rerun()
        single_insight("Use the map to compare country-level distribution across the selected metric.")
    with right:
        tree_event = st.plotly_chart(
            create_treemap(filtered, compute_regional_totals(aggregate_df, year), year, metric, selected_country),
            width="stretch",
            config=PLOTLY_CONFIG,
            key="page1_region_treemap",
            on_select="rerun",
            selection_mode="points",
        )
        tree_country = _selected_country_from_event(tree_event)
        if tree_country and tree_country in countries and tree_country != st.session_state.page1_country_select:
            st.session_state.page1_pending_country = tree_country
            st.rerun()
        single_insight("Treemap size follows the selected metric, so per-capita view no longer shows total CO2 blocks.")

    top = get_top_emitters(filtered, year, metric, 10)
    regional = compute_regional_totals(aggregate_df, year)
    section_header("Country Ranking and Executive Interpretation", "Sorted bars preserve precise comparison; insights summarize what changed attention should focus on.", "Ranking")
    bottom_left, bottom_right = st.columns([1.45, 1])
    with bottom_left:
        st.plotly_chart(create_top_emitters_bar(top, metric, f"Top 10 Countries by {metric_label}"), width="stretch", config=PLOTLY_CONFIG)
        single_insight("The top emitters concentrate a large share of global CO2 emissions.")
    with bottom_right:
        insight_list(generate_page_1_insights(kpis, top, regional, selected_country))

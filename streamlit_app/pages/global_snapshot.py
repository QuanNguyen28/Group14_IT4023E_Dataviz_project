"""Page 1: Global Snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from src.analysis.metrics import compute_global_kpis
from src.analysis.rankings import compute_regional_totals, get_top_emitters
from src.utils.formatting import fmt_mt_as_gt
from src.visualization.charts import create_top_emitters_bar, create_treemap
from src.visualization.maps import create_choropleth_map
from streamlit_app.components.kpi_cards import render_kpis
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, page_header, section_header
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
    # customdata[0] is the primary source — set explicitly on both the choropleth
    # main trace (maps.py) and the treemap trace (charts.py).
    customdata = point.get("customdata") if isinstance(point, dict) else getattr(point, "customdata", None)
    if customdata is not None and len(customdata) > 0:
        country = customdata[0]
        return country if country != "World" else None
    # Fallback: treemap uses "label"; choropleth map exposes hover_name as "hovertext".
    label = point.get("label") if isinstance(point, dict) else getattr(point, "label", None)
    if label and label != "World":
        return label
    hovertext = point.get("hovertext") if isinstance(point, dict) else getattr(point, "hovertext", None)
    return hovertext if hovertext and hovertext != "World" else None


def render_global_snapshot(country_df, aggregate_df) -> None:
    page_header("GLOBAL SNAPSHOT", "What does the world look like today?", "#D94C45", "Current-state overview")
    years, regions, _, countries = common_filter_values(country_df)
    year = max(years)

    # ── Session-state initialisation ─────────────────────────────────────────
    if "page1_country_select" not in st.session_state:
        st.session_state.page1_country_select = "World"
    if "page1_treemap_level" not in st.session_state:
        st.session_state.page1_treemap_level = ""

    # ── Resolve any pending country pushed by map/treemap click ──────────────
    # A click sets page1_pending_country then calls st.rerun(). On the next
    # run we consume it here, before the sidebar widget renders, so the
    # selectbox picks up the new value via its key.
    pending_country = st.session_state.pop("page1_pending_country", None)
    if pending_country and pending_country in countries:
        st.session_state.page1_country_select = pending_country
        # Always force the treemap to jump to that country when a click drives the change.
        st.session_state.page1_treemap_level = f"country:{pending_country}"

    # ── Sidebar filters ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Filters")
        metric_label = st.radio("Metric", ["Total CO2", "CO2 Per Capita"], horizontal=True)
        region = st.selectbox("Region", regions)
        # The selectbox is bound to page1_country_select via its key.
        # Changing it here (user types/picks) will update session_state on rerun.
        st.selectbox(
            "Selected Country",
            countries,
            key="page1_country_select",
        )

    metric = "co2" if metric_label == "Total CO2" else "co2_per_capita"
    filtered = _filter(country_df, region)

    # Read the authoritative country value from session state (covers both
    # sidebar-driven changes and map/treemap-driven changes).
    selected_country = st.session_state.page1_country_select

    # ── Keep treemap in sync with the sidebar dropdown ────────────────────────
    # When the user changes the country via the sidebar (not via a chart click),
    # there is no pending_country, so we sync the treemap level here.
    # We always follow the sidebar value: jump straight to the country tile
    # (or clear to root if "World" is selected).
    if not selected_country or selected_country == "World":
        st.session_state.page1_treemap_level = ""
    else:
        expected_level = f"country:{selected_country}"
        if st.session_state.page1_treemap_level != expected_level:
            # Only override if we're not already drilling into this country.
            # This preserves a region-level drill-down only when the country
            # hasn't changed (i.e. the user is browsing the region context).
            current_level = st.session_state.page1_treemap_level
            currently_at_same_country = current_level == expected_level
            if not currently_at_same_country:
                st.session_state.page1_treemap_level = expected_level

    # ── KPIs and filter summary ───────────────────────────────────────────────
    kpis = compute_global_kpis(country_df, aggregate_df, year, selected_country)
    filter_summary([
        ("Selected Year", year),
        ("Metric", metric_label),
        ("Region", region),
        ("Drill-down", selected_country),
    ])
    render_kpis(kpis)
    section_header("Spatial and Regional Composition", "Country distribution on the left, regional part-to-whole structure on the right.", "Snapshot")

    # Resolve country row once — passed into the treemap so stats appear inside the chart
    country_row = None
    if selected_country and selected_country != "World":
        _cr = country_df.loc[
            country_df["country"].eq(selected_country) & country_df["year"].eq(year)
        ]
        if not _cr.empty:
            country_row = _cr.iloc[0]

    # ── Map + Treemap ─────────────────────────────────────────────────────────
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
        if map_country and map_country in countries:
            if map_country != st.session_state.page1_country_select:
                # Map click → update country filter AND treemap simultaneously.
                st.session_state.page1_pending_country = map_country
                # page1_treemap_level is set when pending_country is consumed
                # at the top of the next run, so we don't need to set it here.
                st.rerun()

    with right:
        tree_event = st.plotly_chart(
            create_treemap(
                filtered,
                compute_regional_totals(aggregate_df, year),
                year,
                metric,
                selected_country,
                treemap_level=st.session_state.page1_treemap_level,
                country_row=country_row,
            ),
            width="stretch",
            config=PLOTLY_CONFIG,
            key="page1_region_treemap",
            on_select="rerun",
            selection_mode="points",
        )

        # Parse what was clicked in the treemap
        raw_points = []
        if tree_event:
            if isinstance(tree_event, dict):
                raw_points = tree_event.get("selection", {}).get("points", [])
            elif hasattr(tree_event, "selection"):
                raw_points = tree_event.selection.points

        if raw_points:
            point = raw_points[0]
            customdata = point.get("customdata") if isinstance(point, dict) else getattr(point, "customdata", None)

            is_region_click = (
                customdata is not None and len(customdata) >= 2
                and customdata[0] == customdata[1]
            )

            if is_region_click:
                # User clicked a region tile — drill into that region in the treemap.
                # Does NOT change the country filter.
                new_level = f"region:{customdata[0]}"
                if st.session_state.page1_treemap_level != new_level:
                    st.session_state.page1_treemap_level = new_level
                    st.rerun()
            else:
                # User clicked a country tile → update both country filter AND map.
                tree_country = _selected_country_from_event(tree_event)
                if tree_country and tree_country in countries:
                    new_level = f"country:{tree_country}"
                    already_at_country = st.session_state.page1_treemap_level == new_level
                    country_changed = tree_country != st.session_state.page1_country_select

                    if already_at_country and not country_changed:
                        # Second click on the same country tile: zoom out to region.
                        country_region = None
                        match_rows = filtered[filtered["country"].eq(tree_country)]
                        if not match_rows.empty and "region" in match_rows.columns:
                            country_region = match_rows.iloc[0]["region"]
                        st.session_state.page1_treemap_level = f"region:{country_region}" if country_region else ""
                        st.rerun()
                    else:
                        # Treemap click → update country filter (drives map highlight too).
                        st.session_state.page1_treemap_level = new_level
                        st.session_state.page1_pending_country = tree_country
                        st.rerun()

    # ── Rankings bar ─────────────────────────────────────────────────────────
    top = get_top_emitters(filtered, year, metric, 10)
    section_header("Country Ranking", "Sorted bars preserve precise comparison.", "Ranking")
    st.plotly_chart(create_top_emitters_bar(top, metric, f"Top 10 Countries by {metric_label}"), width="stretch", config=PLOTLY_CONFIG)

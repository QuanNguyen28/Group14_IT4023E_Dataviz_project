"""KPI card row component."""

from __future__ import annotations

import streamlit as st

from src.utils.formatting import fmt_mt_as_gt, fmt_share, fmt_tonnes
from src.visualization.cards import kpi_card


def render_kpis(kpis: dict) -> None:
    cols = st.columns(6)
    cards = [
        ("Global CO2", fmt_mt_as_gt(kpis.get("global_co2")), "Current selected year", "#0F8B5F", "CO2"),
        ("Countries", str(kpis.get("countries_reported", 0)), "With reported data", "#118A8A", "N"),
        ("Largest Emitter", kpis.get("largest_emitter", "No data"), f"{fmt_mt_as_gt(kpis.get('largest_emitter_co2'))} ({fmt_share(kpis.get('largest_emitter_share'))})", "#D94C45", "TOP"),
        ("Highest Per Capita", kpis.get("highest_per_capita", "No data"), fmt_tonnes(kpis.get("highest_per_capita_value")), "#2F6DE1", "PC"),
        ("World Avg Per Capita", fmt_tonnes(kpis.get("world_per_capita")), "Global mean", "#7C5CDB", "AVG"),
        ("Selected Country", kpis.get("selected_country", "World"), f"{fmt_mt_as_gt(kpis.get('selected_co2'))} ({fmt_share(kpis.get('selected_share'))})", "#E69A1C", "SEL"),
    ]
    for col, args in zip(cols, cards):
        col.markdown(kpi_card(*args), unsafe_allow_html=True)

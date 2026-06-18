"""Sidebar navigation and filters."""

from __future__ import annotations

import streamlit as st


PAGES = ["Global Snapshot", "Historical Evolution", "Current Trend Analysis"]
PAGE_LABELS = {
    "Global Snapshot": "01  Global Snapshot",
    "Historical Evolution": "02  Historical Evolution",
    "Current Trend Analysis": "03  Current Trend Analysis",
}


def render_navigation() -> str:
    """Render the dashboard navigation inside the Streamlit sidebar."""
    if "dashboard_page" not in st.session_state:
        st.session_state.dashboard_page = PAGES[0]

    with st.sidebar:
        st.markdown(
            '<div class="dashboard-brand">'
            '<div class="brand-mark">CO2</div>'
            '<div><div class="brand-title">GLOBAL CO2<br/>DASHBOARD</div>'
            '<div class="brand-subtitle">Analytical cockpit</div></div>'
            "</div>",
            unsafe_allow_html=True,
        )
        current = st.radio(
            "Pages",
            PAGES,
            index=PAGES.index(st.session_state.dashboard_page),
            format_func=lambda page: PAGE_LABELS[page],
            key="sidebar_page_radio",
        )
        st.session_state.dashboard_page = current
        st.markdown("<div class='sidebar-rule'></div>", unsafe_allow_html=True)
    return st.session_state.dashboard_page


def common_filter_values(country_df):
    years = sorted(country_df["year"].dropna().astype(int).unique().tolist()) if not country_df.empty else [2024]
    regions = ["All"] + sorted(country_df.loc[~country_df["region"].eq("Unknown"), "region"].dropna().unique().tolist()) if "region" in country_df else ["All"]
    incomes = ["All"] + sorted(country_df.loc[~country_df["income_group"].eq("Unknown"), "income_group"].dropna().unique().tolist()) if "income_group" in country_df else ["All"]
    countries = ["World"] + sorted(country_df["country"].dropna().unique().tolist()) if "country" in country_df else ["World"]
    return years, regions, incomes, countries

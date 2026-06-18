"""Page 2: Historical Evolution."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.analysis.rankings import compute_cumulative_responsibility
from src.analysis.trends import generate_page_2_insights
from src.visualization.charts import create_annotated_global_line, create_cumulative_responsibility_bar, create_regional_small_multiples
from streamlit_app.components.layout import PLOTLY_CONFIG, filter_summary, insight_list, page_header, section_header, single_insight
from streamlit_app.components.sidebar import common_filter_values


def render_historical_evolution(country_df, aggregate_df, global_yearly, regional_yearly) -> None:
    page_header("HISTORICAL EVOLUTION", "How did global CO2 emissions evolve over time?", "#D94C45", "Long-run story")
    years, regions, incomes, _ = common_filter_values(country_df)
    min_year, max_year = min(years), max(years)
    with st.sidebar:
        st.markdown("### Filters")
        if min_year < max_year:
            time_range = st.slider("Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))
        else:
            time_range = (max_year, max_year)
            st.info(f"Only {max_year} is available.")
        view_by = st.radio("View By", ["World", "Region", "Income Group"])
        metric_label = st.radio("Metric", ["Total CO2", "CO2 Per Capita"], horizontal=True)
        region = st.selectbox("Region", regions)
        income = st.selectbox("Income Group", incomes)
    metric = "co2" if metric_label == "Total CO2" else "co2_per_capita"
    start, end = time_range
    global_part = global_yearly[global_yearly["year"].between(start, end)]
    regional_part = regional_yearly[regional_yearly["year"].between(start, end)]
    country_part = country_df[country_df["year"].between(start, end)]
    if region != "All":
        country_part = country_part[country_part["region"].eq(region)]
    if income != "All":
        country_part = country_part[country_part["income_group"].eq(income)]

    filter_summary([
        ("Years", f"{start}-{end}"),
        ("View", view_by),
        ("Metric", metric_label),
        ("Region", region),
        ("Income", income),
    ])
    section_header("Annotated Global Trajectory", "Major historical events are pinned to the time series to reduce change blindness.", "Storyline")
    st.plotly_chart(create_annotated_global_line(global_part, metric), width="stretch", config=PLOTLY_CONFIG)
    single_insight("Global CO2 emissions remained low for centuries, then accelerated rapidly after industrialization.")

    section_header("Historical Responsibility and Regional Evolution", "Cumulative bars answer responsibility; small multiples keep regional trajectories readable.", "Comparison")
    left, right = st.columns([1, 1.35])
    responsibility = compute_cumulative_responsibility(country_part, end, 10)
    with left:
        st.plotly_chart(create_cumulative_responsibility_bar(responsibility), width="stretch", config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(create_regional_small_multiples(regional_part, metric), width="stretch", config=PLOTLY_CONFIG)

    insight_list(generate_page_2_insights(global_part, responsibility, regional_part), "Historical Insights")

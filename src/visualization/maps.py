"""Map visualizations."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from src.visualization.theme import RED, apply_common_layout


def create_choropleth_map(df: pd.DataFrame, year: int, metric: str = "co2"):
    # Power BI equivalent: filled map visual.
    work = df.loc[df["year"].eq(year)].dropna(subset=["iso_code", metric]).copy() if metric in df.columns else pd.DataFrame()
    if work.empty:
        return px.scatter_geo(title="CO2 Emissions by Country")
    title = "CO2 Emissions by Country" if metric == "co2" else "CO2 Per Capita by Country"
    hover_data = {
        col: fmt for col, fmt in {
            metric: ":.2f",
            "region": True,
            "co2": ":.2f",
            "co2_per_capita": ":.2f",
            "population": ":,.0f",
            "share_of_world_co2": ":.1f",
        }.items() if col in work.columns
    }
    fig = px.choropleth(
        work, locations="iso_code", color=metric, hover_name="country",
        hover_data=hover_data,
        color_continuous_scale=["#FFF1F0", "#F8B4AC", "#D94C45", "#8F1D1B"],
        title=title,
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,.72)", marker_line_width=.45)
    fig.update_geos(
        showframe=False,
        showcoastlines=False,
        showcountries=True,
        countrycolor="rgba(255,255,255,.62)",
        showland=True,
        landcolor="#E9EEF5",
        showocean=True,
        oceancolor="#F8FAFD",
        projection_type="natural earth",
        bgcolor="rgba(0,0,0,0)",
    )
    fig = apply_common_layout(fig, 420)
    fig.update_layout(coloraxis_colorbar=dict(title="CO2" if metric == "co2" else "t/person", tickcolor=RED))
    return fig

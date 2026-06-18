"""Map visualizations."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.visualization.theme import NAVY, RED, apply_common_layout


FRIENDLY_LABELS = {
    "co2": "CO2 emissions (Mt)",
    "co2_per_capita": "CO2 per capita (t/person)",
    "population": "Population",
    "share_of_world_co2": "Share of world CO2 (%)",
    "region": "Region",
}


def _region_label(series: pd.Series) -> pd.Series:
    return series.fillna("Unknown").replace({"Unknown": "Unclassified"})


def create_choropleth_map(df: pd.DataFrame, year: int, metric: str = "co2", selected_country: str | None = None):
    # Power BI equivalent: filled map visual.
    work = df.loc[df["year"].eq(year)].dropna(subset=["iso_code", metric]).copy() if metric in df.columns else pd.DataFrame()
    if work.empty:
        return px.scatter_geo(title="CO2 Emissions by Country")
    title = "CO2 Emissions by Country" if metric == "co2" else "CO2 Per Capita by Country"
    work["region_label"] = _region_label(work["region"]) if "region" in work.columns else "Unclassified"
    hover_data = {
        col: fmt for col, fmt in {
            metric: ":.2f",
            "region_label": True,
            "co2": ":.2f",
            "co2_per_capita": ":.2f",
            "population": ":,.0f",
            "share_of_world_co2": ":.1f",
        }.items() if col in work.columns
    }
    fig = px.choropleth(
        work,
        locations="iso_code",
        color=metric,
        hover_name="country",
        hover_data=hover_data,
        color_continuous_scale=["#FFF1F0", "#F8B4AC", "#D94C45", "#8F1D1B"],
        labels={**FRIENDLY_LABELS, "region_label": "Region"},
        title=title,
    )
    fig.update_traces(marker_line_color="rgba(255,255,255,.72)", marker_line_width=.45)

    if selected_country and selected_country != "World":
        selected = work[work["country"].eq(selected_country)]
        if not selected.empty:
            fig.add_trace(go.Choropleth(
                locations=selected["iso_code"],
                z=[1] * len(selected),
                name="Selected",
                colorscale=[[0, "#4B5563"], [1, "#4B5563"]],
                showscale=False,
                showlegend=False,
                marker_line_color=NAVY,
                marker_line_width=2.8,
                customdata=selected[["country", "region_label", metric]].to_numpy(),
                hovertemplate="<b>%{customdata[0]}</b><br>Selected country<extra></extra>",
            ))

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

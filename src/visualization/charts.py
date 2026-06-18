"""Reusable Plotly charts for Power BI-style Streamlit visuals."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis.trends import compute_fuel_shares
from src.utils.constants import FUEL_COLORS, FUEL_COLUMNS, REGION_COLORS, REGIONS
from src.visualization.theme import BLUE, GREEN, NAVY, ORANGE, RED, apply_common_layout

PRIMARY_BAR = "#D94C45"


def _empty(title: str):
    fig = go.Figure()
    fig.add_annotation(
        text="No data available",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(color="#667A94", size=13),
    )
    fig.update_layout(title=title)
    apply_common_layout(fig, 320)
    return fig


def _with_chart_margins(fig, *, l=18, r=18, t=72, b=74):
    fig.update_layout(margin=dict(l=l, r=r, t=t, b=b))
    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return hex_color
    r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _scaled_series(series: pd.Series, metric: str) -> tuple[pd.Series, str]:
    if metric in {"co2", "cumulative_co2"}:
        return series / 1000, "Gt CO2"
    if metric == "co2_per_capita":
        return series, "t / person"
    return series, metric.replace("_", " ").title()


def _format_values(values: pd.Series, metric: str) -> list[str]:
    scaled, unit = _scaled_series(values, metric)
    if unit == "Gt CO2":
        return [f"{v:.1f} Gt" for v in scaled]
    if unit == "t / person":
        return [f"{v:.1f} t" for v in scaled]
    return [f"{v:.1f}" for v in scaled]


def create_treemap(country_df: pd.DataFrame, regional_df: pd.DataFrame, year: int):
    # Power BI equivalent: Treemap visual with Region -> Country hierarchy.
    df = country_df.loc[country_df["year"].eq(year)].dropna(subset=["co2"]).copy()
    df = df[df["co2"] > 0]
    if df.empty:
        return _empty("CO2 Emissions by Region and Country")
    hover_cols = [col for col in ["co2", "share_of_world_co2"] if col in df.columns]
    fig = px.treemap(
        df, path=["region", "country"], values="co2", color="region",
        color_discrete_map=REGION_COLORS, hover_data=hover_cols,
        title="CO2 Emissions by Region and Country",
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:.0f} Mt",
        marker=dict(line=dict(color="rgba(255,255,255,.72)", width=1)),
        hovertemplate="<b>%{label}</b><br>%{value:.2f} Mt<extra></extra>",
    )
    return apply_common_layout(fig, 390)


def create_top_emitters_bar(df: pd.DataFrame, metric: str = "co2", title: str = "Top Countries"):
    # Power BI equivalent: sorted clustered bar chart with data labels.
    if df.empty or metric not in df.columns:
        return _empty(title)
    work = df.sort_values(metric, ascending=True).copy()
    plot_values, unit = _scaled_series(work[metric], metric)
    fig = go.Figure(go.Bar(
        x=plot_values,
        y=work["country"],
        orientation="h",
        marker=dict(color=PRIMARY_BAR, line=dict(color="rgba(255,255,255,.85)", width=1)),
        text=_format_values(work[metric], metric),
        textposition="outside",
        cliponaxis=False,
        customdata=np.stack([work.get("share_of_world_co2", pd.Series(np.nan, index=work.index)).fillna(np.nan)], axis=-1),
        hovertemplate=f"<b>%{{y}}</b><br>Value: %{{x:.2f}} {unit}<br>Share: %{{customdata[0]:.1f}}%<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title=unit, yaxis_title="", bargap=0.34)
    fig.update_yaxes(categoryorder="array", categoryarray=work["country"].tolist())
    return apply_common_layout(fig, 360)


def create_annotated_global_line(df: pd.DataFrame, metric: str = "co2"):
    # Power BI equivalent: line chart with event annotations.
    if df.empty or metric not in df.columns:
        return _empty("Global CO2 Emissions Over Time")
    work = df.dropna(subset=[metric]).sort_values("year")
    y_values, unit = _scaled_series(work[metric], metric)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=work["year"],
        y=y_values,
        mode="lines",
        showlegend=False,
        line=dict(color=RED, width=3.4, shape="spline", smoothing=.35),
        fill="tozeroy",
        fillcolor="rgba(217,76,69,0.18)",
        hovertemplate=f"Year %{{x}}<br>CO2: %{{y:.2f}} {unit}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=work["year"].tail(1),
        y=y_values.tail(1),
        mode="markers",
        marker=dict(size=10, color=RED, line=dict(color="white", width=2)),
        showlegend=False,
        hoverinfo="skip",
    ))
    events = [(1780, "Industrial<br>Revolution"), (1945, "Post-WWII<br>Boom"), (1973, "Oil Crisis"), (2008, "Financial<br>Crisis"), (2020, "COVID-19")]
    y_max = y_values.max()
    for x, label in events:
        if work["year"].min() <= x <= work["year"].max():
            fig.add_vline(x=x, line_width=1, line_dash="dot", line_color="#AAB6C8")
            fig.add_annotation(
                x=x,
                y=y_max * 0.8,
                text=label,
                showarrow=False,
                font=dict(size=11, color=NAVY),
                bgcolor="rgba(255,255,255,0.86)",
                bordercolor="#D8E2EE",
                borderwidth=1,
                borderpad=5,
            )
    fig.update_layout(title="Global CO2 Emissions Over Time", xaxis_title="", yaxis_title=unit)
    return _with_chart_margins(apply_common_layout(fig, 430), l=52, r=26, t=74, b=42)


def create_cumulative_responsibility_bar(df: pd.DataFrame):
    return create_top_emitters_bar(df, "cumulative_co2", "Top Countries by Cumulative CO2")


def create_regional_small_multiples(df: pd.DataFrame, metric: str = "co2"):
    # Power BI equivalent: small multiples line chart.
    work = df[df["country"].isin(REGIONS)].dropna(subset=[metric]).copy() if metric in df.columns else pd.DataFrame()
    if work.empty:
        return _empty("Regional CO2 Emissions Over Time")
    regions = [r for r in REGIONS if r in set(work["country"])]
    n_cols = 3
    n_rows = int(np.ceil(len(regions) / n_cols))
    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=regions,
        shared_yaxes=True,
        horizontal_spacing=0.08,
        vertical_spacing=0.16,
    )
    x_min, x_max = int(work["year"].min()), int(work["year"].max())
    tick_years = sorted(set([x_min, int((x_min + x_max) / 2), x_max]))
    y_max_global = _scaled_series(work[metric], metric)[0].max()
    for i, region in enumerate(regions):
        row = i // n_cols + 1
        col = i % n_cols + 1
        part = work[work["country"].eq(region)]
        y_values, unit = _scaled_series(part[metric], metric)
        fig.add_trace(
            go.Scatter(
                x=part["year"],
                y=y_values,
                mode="lines",
                line=dict(color=REGION_COLORS[region], width=3, shape="spline", smoothing=.25),
                showlegend=False,
                hovertemplate=f"{region}<br>%{{x}}: %{{y:.2f}} {unit}<extra></extra>",
            ),
            row=row,
            col=col,
        )
        fig.update_xaxes(tickmode="array", tickvals=tick_years, tickangle=0, row=row, col=col)
    fig.update_layout(title="Regional CO2 Emissions Over Time", showlegend=False)
    apply_common_layout(fig, 470)
    _with_chart_margins(fig, l=42, r=20, t=78, b=46)
    fig.update_annotations(font=dict(size=13, color=NAVY))
    if pd.notna(y_max_global) and y_max_global > 0:
        fig.update_yaxes(range=[0, y_max_global * 1.08])
    return fig


def create_bubble_scatter(df: pd.DataFrame, y_metric: str = "co2_per_capita"):
    # Power BI equivalent: scatter chart with size and legend encodings.
    needed = {"co2_cagr", y_metric, "co2", "region"}
    work = df.dropna(subset=[c for c in needed if c in df.columns]).copy()
    if y_metric == "co2_per_capita":
        work = work[work[y_metric] > 0]
    if work.empty:
        return _empty("CO2 Growth Rate vs Emissions Profile")
    if y_metric == "co2":
        work["y_display"] = work[y_metric] / 1000
        y_axis_title = "Total CO2 (Gt)"
    else:
        work["y_display"] = work[y_metric]
        y_axis_title = "CO2 per capita"
    y_median = work[y_metric].median()
    hover_cols = [col for col in ["region", "co2", "co2_per_capita", "population", "cumulative_co2"] if col in work.columns]
    fig = px.scatter(
        work, x="co2_cagr", y="y_display", size="co2", color="region", color_discrete_map=REGION_COLORS,
        hover_name="country", hover_data=hover_cols,
        title="Growth Rate vs Emissions Profile", size_max=46, opacity=0.78,
    )
    y_line = y_median / 1000 if y_metric == "co2" else y_median
    y_min, y_max = work["y_display"].min(), work["y_display"].max()
    x_min = min(work["co2_cagr"].min() * 1.12, -0.01)
    x_max = max(work["co2_cagr"].max() * 1.12, 0.01)
    y_low = max(y_min * .72, .001)
    y_high = y_max * 1.12 if y_max > 0 else 1
    fig.add_shape(type="rect", xref="x", yref="y", x0=0, x1=x_max, y0=y_line, y1=y_high, fillcolor="rgba(214,59,50,.055)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=x_min, x1=0, y0=y_line, y1=y_high, fillcolor="rgba(46,98,212,.045)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=0, x1=x_max, y0=y_low, y1=y_line, fillcolor="rgba(242,161,43,.045)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=x_min, x1=0, y0=y_low, y1=y_line, fillcolor="rgba(61,150,81,.045)", line_width=0, layer="below")
    fig.add_vline(x=0, line_dash="dot", line_color="#697791")
    fig.add_hline(y=y_line, line_dash="dot", line_color="#697791")
    fig.update_traces(marker=dict(line=dict(width=0.6, color="white")))
    fig.update_xaxes(tickformat=".0%", title="CO2 CAGR")
    fig.update_yaxes(title=y_axis_title, type="log" if y_metric == "co2_per_capita" else "linear")
    for x, y, text, color in [(0.13, 0.88, "High emission<br>high growth", RED), (-0.08, 0.88, "High emission<br>declining", BLUE), (0.13, 0.16, "Low emission<br>growing", ORANGE), (-0.08, 0.16, "Low emission<br>stable/declining", GREEN)]:
        fig.add_annotation(x=x, y=y, xref="paper", yref="paper", text=text, showarrow=False, font=dict(color=color, size=12))
    fig.update_layout(legend_title_text="Region")
    return _with_chart_margins(apply_common_layout(fig, 500), l=58, r=24, t=78, b=94)


def create_fastest_increasing_bar(df: pd.DataFrame):
    return _trend_bar(df, "Fastest Increasing Countries", RED)


def create_fastest_declining_bar(df: pd.DataFrame):
    return _trend_bar(df, "Fastest Declining Countries", "#B23A48")


def _trend_bar(df: pd.DataFrame, title: str, color: str):
    if df.empty or "co2_cagr" not in df.columns:
        return _empty(title)
    work = df.sort_values("co2_cagr", ascending=True).copy()
    values = work["co2_cagr"]
    fig = go.Figure(go.Bar(
        x=values,
        y=work["country"],
        orientation="h",
        marker=dict(color=color, line=dict(color="rgba(255,255,255,.88)", width=1)),
        text=[f"{v*100:.1f}%" for v in values],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>CAGR: %{x:.2%}<extra></extra>",
    ))
    if values.max() <= 0:
        x_range = [values.min() * 1.32, 0]
    elif values.min() >= 0:
        x_range = [0, values.max() * 1.32]
    else:
        spread = max(abs(values.min()), abs(values.max())) * 1.25
        x_range = [-spread, spread]
    fig.update_xaxes(tickformat=".0%", range=x_range)
    fig.update_layout(title=title, xaxis_title="CAGR", yaxis_title="", bargap=0.34)
    fig.update_yaxes(tickfont=dict(size=10))
    return _with_chart_margins(apply_common_layout(fig, 380), l=150, r=58, t=72, b=58)


def create_fuel_decomposition_area(fuel_long: pd.DataFrame, country: str):
    # Power BI equivalent: 100% stacked area chart.
    shares = compute_fuel_shares(fuel_long, country).dropna(subset=["share"]).copy()
    if shares.empty or shares["share"].sum() <= 0:
        return _empty(f"Fuel Mix by Source - {country}")
    fuel_order = list(FUEL_COLUMNS.values())
    shares = shares[shares["fuel_source"].isin(fuel_order)]
    share_wide = (
        shares.pivot_table(index="year", columns="fuel_source", values="share", aggfunc="sum")
        .reindex(columns=fuel_order)
        .fillna(0)
        .sort_index()
    )
    if share_wide.empty or share_wide.to_numpy().sum() <= 0:
        return _empty(f"Fuel Mix by Source - {country}")

    fig = go.Figure()
    for source in fuel_order:
        values = share_wide[source]
        if values.sum() <= 0:
            continue
        color = FUEL_COLORS.get(source, "#667A94")
        fig.add_trace(go.Scatter(
            x=share_wide.index,
            y=values,
            name=source,
            mode="lines",
            stackgroup="fuel",
            line=dict(width=1.1, color=color),
            fillcolor=_hex_to_rgba(color, 0.82),
            hovertemplate=f"<b>{source}</b><br>Year: %{{x}}<br>Share: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig.update_layout(
        yaxis_title="Share of CO2 emissions",
        xaxis_title="",
        legend_title_text="",
        hovermode="x unified",
        title=f"Fuel Mix by Source - {country}",
    )
    return _with_chart_margins(apply_common_layout(fig, 440), l=58, r=26, t=78, b=96)


def create_fuel_share_change_table_or_panel(change_df: pd.DataFrame):
    if change_df.empty:
        return _empty("Fuel Share Change")
    colors = ["#0F8B5F" if v >= 0 else "#D94C45" for v in change_df["change_pp"]]
    row_fills = [["#FFFFFF" if i % 2 == 0 else "#F7FAFD" for i in range(len(change_df))] for _ in range(4)]
    fig = go.Figure(data=[go.Table(
        columnwidth=[1.45, .8, .8, .9],
        header=dict(
            values=["Fuel", "Start", "End", "Change"],
            fill_color="#EAF1F8",
            line_color="#D8E2EE",
            align="left",
            font=dict(color=NAVY, size=12),
            height=34,
        ),
        cells=dict(values=[
            change_df["fuel_source"],
            change_df["start_share"].map(lambda v: f"{v:.0f}%"),
            change_df["end_share"].map(lambda v: f"{v:.0f}%"),
            change_df["change_pp"].map(lambda v: f"{v:+.0f} pp"),
        ], align="left", height=32, fill_color=row_fills, line_color="#D8E2EE", font=dict(color=[NAVY, NAVY, NAVY, colors], size=12)),
    )])
    fig.update_layout(title="Fuel Share Change", height=320, margin=dict(l=8, r=8, t=56, b=8), paper_bgcolor="rgba(0,0,0,0)")
    return fig

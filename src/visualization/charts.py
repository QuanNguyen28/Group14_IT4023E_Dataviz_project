"""Reusable Plotly charts for Power BI-style Streamlit visuals."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis.trends import compute_fuel_absolute
from src.utils.constants import FUEL_COLORS, FUEL_COLUMNS, REGION_COLORS, REGIONS
from src.visualization.theme import BLUE, GREEN, NAVY, ORANGE, RED, apply_common_layout

PRIMARY_BAR = "#D94C45"
UNCLASSIFIED_REGION = "Unclassified"
DISPLAY_REGION_COLORS = {**REGION_COLORS, UNCLASSIFIED_REGION: REGION_COLORS.get("Unknown", "#8A94A6")}
FRIENDLY_LABELS = {
    "co2": "CO2 emissions (Mt)",
    "co2_per_capita": "CO2 per capita (t/person)",
    "gdp_per_capita": "GDP per capita",
    "cumulative_co2": "Cumulative CO2 (Mt)",
    "share_of_world_co2": "Share of world CO2 (%)",
    "population": "Population",
    "co2_cagr": "Annualized CO2 growth",
    "region_label": "Region",
}


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


def _with_region_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "region" in out.columns:
        out["region_label"] = out["region"].fillna("Unknown").replace({"Unknown": UNCLASSIFIED_REGION})
    else:
        out["region_label"] = UNCLASSIFIED_REGION
    return out


def create_treemap(country_df: pd.DataFrame, regional_df: pd.DataFrame, year: int, metric: str = "co2", selected_country: str | None = None):
    # Power BI equivalent: Treemap visual with Region -> Country hierarchy.
    if metric not in country_df.columns:
        return _empty("Country Composition")
    df = country_df.loc[country_df["year"].eq(year)].dropna(subset=[metric]).copy()
    df = df[df[metric] > 0]
    if df.empty:
        return _empty("Country Composition")
    df = _with_region_label(df)
    title = "CO2 Emissions by Region and Country" if metric == "co2" else "CO2 Per Capita by Region and Country"
    unit = "Mt" if metric == "co2" else "t/person"

    regions = [r for r in DISPLAY_REGION_COLORS if r in set(df["region_label"])]
    region_values = df.groupby("region_label", as_index=True)[metric].sum()
    labels = regions + df["country"].tolist()
    ids = [f"region:{region}" for region in regions] + [f"country:{country}" for country in df["country"]]
    parents = [""] * len(regions) + [f"region:{region}" for region in df["region_label"]]
    values = [region_values.get(region, 0) for region in regions] + df[metric].tolist()
    colors = [DISPLAY_REGION_COLORS.get(region, PRIMARY_BAR) for region in regions] + [
        DISPLAY_REGION_COLORS.get(region, PRIMARY_BAR) for region in df["region_label"]
    ]
    line_colors = ["rgba(255,255,255,.78)"] * len(labels)
    line_widths = [1.2] * len(labels)
    if selected_country and selected_country in set(df["country"]):
        selected_index = len(regions) + df["country"].tolist().index(selected_country)
        line_colors[selected_index] = NAVY
        line_widths[selected_index] = 4
        colors[selected_index] = "#4B5563"

    country_customdata = np.stack([
        df["country"],
        df["region_label"],
        df[metric],
        df.get("co2", pd.Series(np.nan, index=df.index)).fillna(np.nan),
        df.get("co2_per_capita", pd.Series(np.nan, index=df.index)).fillna(np.nan),
        df.get("share_of_world_co2", pd.Series(np.nan, index=df.index)).fillna(np.nan),
    ], axis=-1)
    region_customdata = np.array([[region, region, region_values.get(region, 0), np.nan, np.nan, np.nan] for region in regions], dtype=object)
    customdata = np.vstack([region_customdata, country_customdata])

    fig = go.Figure(go.Treemap(
        labels=labels,
        ids=ids,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors, line=dict(color=line_colors, width=line_widths)),
        customdata=customdata,
        texttemplate=f"<b>%{{label}}</b><br>%{{value:.1f}} {unit}",
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Region: %{customdata[1]}<br>"
            f"Value: %{{customdata[2]:.2f}} {unit}<br>"
            "Total CO2: %{customdata[3]:.2f} Mt<br>"
            "CO2 per capita: %{customdata[4]:.2f} t/person<br>"
            "Share of world CO2: %{customdata[5]:.1f}%"
            "<extra></extra>"
        ),
    )
    )
    fig.update_layout(title=title)
    return apply_common_layout(fig, 420)


def create_top_emitters_bar(df: pd.DataFrame, metric: str = "co2", title: str = "Top Countries", height: int = 390):
    # Power BI equivalent: sorted clustered bar chart with data labels.
    if df.empty or metric not in df.columns:
        return _empty(title)
    work = _with_region_label(df).sort_values(metric, ascending=True).copy()
    plot_values, unit = _scaled_series(work[metric], metric)
    work["plot_value"] = plot_values
    work["text_label"] = _format_values(work[metric], metric)
    fig = go.Figure()
    for region in [r for r in DISPLAY_REGION_COLORS if r in set(work["region_label"])]:
        part = work[work["region_label"].eq(region)]
        fig.add_trace(go.Bar(
            x=part["plot_value"],
            y=part["country"],
            name=region,
            orientation="h",
            marker=dict(color=DISPLAY_REGION_COLORS[region], line=dict(color="rgba(255,255,255,.85)", width=1)),
            text=part["text_label"],
            textposition="outside",
            cliponaxis=False,
            customdata=np.stack([
                part.get("share_of_world_co2", pd.Series(np.nan, index=part.index)).fillna(np.nan),
                part["region_label"],
            ], axis=-1),
            hovertemplate=f"<b>%{{y}}</b><br>Region: %{{customdata[1]}}<br>Value: %{{x:.2f}} {unit}<br>Share: %{{customdata[0]:.1f}}%<extra></extra>",
        ))
    fig.update_layout(title=title, xaxis_title=unit, yaxis_title="", bargap=0.34, showlegend=True)
    fig.update_yaxes(categoryorder="array", categoryarray=work["country"].tolist())
    return _with_chart_margins(apply_common_layout(fig, height), l=142, r=86, t=58, b=84)


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
    return create_top_emitters_bar(df, "cumulative_co2", "Top Countries by Cumulative CO2", height=430)


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


def create_regional_line(df: pd.DataFrame, metric: str = "co2"):
    work = df[df["country"].isin(REGIONS)].dropna(subset=[metric]).copy() if metric in df.columns else pd.DataFrame()
    if work.empty:
        return _empty("Regional CO2 Emissions Over Time")
    work["display_value"], unit = _scaled_series(work[metric], metric)
    fig = px.line(
        work,
        x="year",
        y="display_value",
        color="country",
        color_discrete_map=REGION_COLORS,
        labels={"year": "Year", "display_value": unit, "country": "Region"},
        title="Regional CO2 Emissions Over Time",
    )
    fig.update_traces(line=dict(width=3), hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:.2f}<extra></extra>")
    fig.update_layout(hovermode="x unified", legend_title_text="Region")
    return _with_chart_margins(apply_common_layout(fig, 430), l=58, r=26, t=78, b=92)


_BUBBLE_CHART_META = {
    "gdp_per_capita": {
        "title": "CO2 Growth vs GDP per Capita",
        "quadrants": [
            (0.74, 0.86, "Richer<br>growing"),
            (0.26, 0.86, "Richer<br>declining"),
            (0.74, 0.18, "Lower income<br>growing"),
            (0.26, 0.18, "Lower income<br>declining"),
        ],
    },
    "co2_per_capita": {
        "title": "CO2 Growth vs Per-Capita Emissions",
        "quadrants": [
            (0.74, 0.86, "High emitter<br>growing"),
            (0.26, 0.86, "High emitter<br>declining"),
            (0.74, 0.18, "Low emitter<br>growing"),
            (0.26, 0.18, "Low emitter<br>declining"),
        ],
    },
    "co2": {
        "title": "CO2 Growth vs Total Emissions",
        "quadrants": [
            (0.74, 0.86, "Large emitter<br>growing"),
            (0.26, 0.86, "Large emitter<br>declining"),
            (0.74, 0.18, "Small emitter<br>growing"),
            (0.26, 0.18, "Small emitter<br>declining"),
        ],
    },
}


def create_bubble_scatter(df: pd.DataFrame, y_metric: str = "co2_per_capita", highlight_extremes: int = 0):
    # Power BI equivalent: scatter chart with size and legend encodings.
    # Bubble size always encodes current emissions volume ("co2"), independent of the y-axis metric.
    # FIX 1: Use logarithmic emission scale for co2 and co2_per_capita y-axes.
    # FIX 2: Label top emitters by volume + CAGR outliers (not just CAGR extremes).
    # FIX 3: Use median of raw (unlogged) emission values as the quadrant split line.
    # FIX 4: Increase point transparency from 0.82 → 0.62.
    needed = {"co2_cagr", y_metric, "co2", "region"}
    work = df.dropna(subset=[c for c in needed if c in df.columns]).copy()
    if y_metric in {"co2_per_capita", "gdp_per_capita"}:
        work = work[work[y_metric] > 0]
    chart_title = _BUBBLE_CHART_META.get(y_metric, _BUBBLE_CHART_META["co2_per_capita"])["title"]
    if work.empty:
        return _empty(chart_title)

    # --- Axis setup with FIX 1 (log scale) ---
    use_log_y = False
    if y_metric == "co2":
        # FIX 1: log scale on total emissions to spread the long tail
        work = work[work[y_metric] > 0]
        work["y_display"] = np.log10(work[y_metric] / 1000)   # log10(Gt)
        y_axis_title = "Total CO2 (Gt)"
        y_hover = work[y_metric] / 1000
        y_hover_unit = "Gt"
        use_log_y = True
        # FIX 3: median split on raw Gt values → convert to log space
        y_median_raw = (work[y_metric] / 1000).median()
        y_median = np.log10(y_median_raw) if y_median_raw > 0 else work["y_display"].median()
    elif y_metric == "gdp_per_capita":
        work["y_display"] = np.log10(work[y_metric])
        y_axis_title = "GDP per capita"
        y_hover = work[y_metric]
        y_hover_unit = "USD/person"
        # FIX 3: median split on raw GDP values → log space
        y_median_raw = work[y_metric].median()
        y_median = np.log10(y_median_raw) if y_median_raw > 0 else work["y_display"].median()
    else:  # co2_per_capita
        # FIX 1: log scale for per-capita too
        work = work[work[y_metric] > 0]
        work["y_display"] = np.log10(work[y_metric])
        y_axis_title = "CO2 per capita (t/person)"
        y_hover = work[y_metric]
        y_hover_unit = "t/person"
        use_log_y = True
        # FIX 3: median split on raw per-capita values → log space
        y_median_raw = work[y_metric].median()
        y_median = np.log10(y_median_raw) if y_median_raw > 0 else work["y_display"].median()

    work = _with_region_label(work)
    work["y_hover"] = y_hover
    work["gdp_year_display"] = work.get("gdp_year", pd.Series(np.nan, index=work.index)).fillna(np.nan)
    work["population_display"] = work.get("population", pd.Series(np.nan, index=work.index)).fillna(np.nan)

    # FIX 4: opacity lowered to 0.62 for better overlap visibility
    fig = px.scatter(
        work,
        x="co2_cagr",
        y="y_display",
        size="co2",
        color="region_label",
        color_discrete_map=DISPLAY_REGION_COLORS,
        custom_data=["country", "region_label", "y_hover", "co2", "gdp_year_display", "population_display"],
        title=chart_title,
        size_max=42,
        opacity=0.62,  # FIX 4: was 0.82
    )

    # FIX 3: quadrant divider at median of raw emission values
    y_line = y_median
    y_min, y_max = work["y_display"].min(), work["y_display"].max()
    x_abs = max(abs(work["co2_cagr"].min()), abs(work["co2_cagr"].max()), 0.01) * 1.12
    x_min, x_max = -x_abs, x_abs
    y_span = max(abs(y_min - y_line), abs(y_max - y_line), 0.12) * 1.16
    y_low, y_high = y_line - y_span, y_line + y_span
    fig.add_shape(type="rect", xref="x", yref="y", x0=0, x1=x_max, y0=y_line, y1=y_high, fillcolor="rgba(12,34,53,.045)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=x_min, x1=0, y0=y_line, y1=y_high, fillcolor="rgba(12,34,53,.025)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=0, x1=x_max, y0=y_low, y1=y_line, fillcolor="rgba(12,34,53,.030)", line_width=0, layer="below")
    fig.add_shape(type="rect", xref="x", yref="y", x0=x_min, x1=0, y0=y_low, y1=y_line, fillcolor="rgba(12,34,53,.015)", line_width=0, layer="below")
    fig.add_vline(x=0, line_dash="dot", line_color="#697791")
    fig.add_hline(y=y_line, line_dash="dot", line_color="#697791")
    fig.update_traces(
        marker=dict(line=dict(width=0.7, color="white")),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Region: %{customdata[1]}<br>"
            "CO2 CAGR: %{x:+.2%}<br>"
            f"{y_axis_title}: %{{customdata[2]:,.2f}} {y_hover_unit}<br>"
            "Total CO2: %{customdata[3]:,.1f} Mt<br>"
            "GDP year: %{customdata[4]:.0f}<br>"
            "Population: %{customdata[5]:,.0f}"
            "<extra></extra>"
        ),
    )
    fig.update_xaxes(tickformat=".0%", title="CO2 CAGR, 2022-2024", zeroline=False)
    fig.update_xaxes(range=[x_min, x_max])

    # Axis tick formatting — log scales get human-readable labels
    if y_metric == "gdp_per_capita":
        tick_values = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
        tick_vals = [np.log10(v) for v in tick_values if y_low <= np.log10(v) <= y_high]
        tick_text = [f"${int(v / 1000)}k" for v in tick_values if y_low <= np.log10(v) <= y_high]
        fig.update_yaxes(title="GDP per capita", range=[y_low, y_high], tickmode="array", tickvals=tick_vals, ticktext=tick_text)
    elif y_metric == "co2":
        # FIX 1: human-readable log ticks in Gt
        tick_vals_gt = [0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10, 20]
        tick_vals_log = [np.log10(v) for v in tick_vals_gt if y_low <= np.log10(v) <= y_high]
        tick_text_gt = [f"{v:g} Gt" for v in tick_vals_gt if y_low <= np.log10(v) <= y_high]
        fig.update_yaxes(title=y_axis_title, range=[y_low, y_high], tickmode="array", tickvals=tick_vals_log, ticktext=tick_text_gt)
    elif y_metric == "co2_per_capita":
        # FIX 1: human-readable log ticks in t/person
        tick_vals_pc = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50]
        tick_vals_log = [np.log10(v) for v in tick_vals_pc if y_low <= np.log10(v) <= y_high]
        tick_text_pc = [f"{v:g} t" for v in tick_vals_pc if y_low <= np.log10(v) <= y_high]
        fig.update_yaxes(title=y_axis_title, range=[y_low, y_high], tickmode="array", tickvals=tick_vals_log, ticktext=tick_text_pc)
    else:
        fig.update_yaxes(title=y_axis_title, type="linear", range=[y_low, y_high])

    quadrant_labels = _BUBBLE_CHART_META.get(y_metric, _BUBBLE_CHART_META["co2_per_capita"])["quadrants"]
    for x, y, text in quadrant_labels:
        fig.add_annotation(x=x, y=y, xref="paper", yref="paper", text=text, showarrow=False, align="center", font=dict(color="#334155", size=11), bgcolor="rgba(255,255,255,.78)", bordercolor="#D8E2EE", borderwidth=1, borderpad=4)

    # FIX 2: label top emitters by volume + CAGR outliers (not just CAGR extremes)
    if highlight_extremes > 0 and len(work) > 1:
        n = min(highlight_extremes, len(work) // 2 or 1)
        top_volume = work.nlargest(n, "co2")
        cagr_extremes = pd.concat([
            work.nlargest(n, "co2_cagr"),
            work.nsmallest(n, "co2_cagr"),
        ])
        extremes = pd.concat([top_volume, cagr_extremes]).drop_duplicates(subset=["country"]).sort_values("co2_cagr")
        for i, (_, erow) in enumerate(extremes.iterrows()):
            offset = -22 if i % 2 == 0 else 22
            fig.add_annotation(
                x=erow["co2_cagr"], y=erow["y_display"],
                text=_short_country_label(erow["country"], max_len=14),
                showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#9AA7BC",
                ax=0, ay=offset,
                font=dict(size=9.5, color=NAVY),
                bgcolor="rgba(255,255,255,.92)", bordercolor="#D8E2EE", borderwidth=1, borderpad=2,
            )
    fig = apply_common_layout(fig, 520)
    fig.update_layout(
        legend_title_text="Region",
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5, bgcolor="rgba(255,255,255,.78)", bordercolor="#D8E2EE", borderwidth=1, font=dict(size=10)),
        title=dict(text=chart_title, font=dict(size=15, color=NAVY), x=0.02, y=0.97),
    )
    return _with_chart_margins(fig, l=64, r=28, t=70, b=118)



def create_growth_volume_scatter(df, label_n=4):
    """Scatter: x = CO2 growth rate (CAGR), y = total CO2 volume (Gt).

    Uniform dot size — position alone carries the information.
    Colour encodes region.
    FIX 1: Log scale on y-axis to spread the long tail of emission volumes.
    FIX 2: Label top emitters by volume + CAGR outliers.
    FIX 3: Quadrant split at median of raw Gt values (converted to log space).
    FIX 4: Opacity lowered from 0.82 → 0.62 for better overlap visibility.
    """
    needed = {"co2_cagr", "co2", "region", "country"}
    work = df.dropna(subset=[c for c in needed if c in df.columns]).copy()
    work = work[work["co2"] > 0]
    if work.empty:
        return _empty("CO2 Growth Rate vs Volume")
    work["co2_gt"] = work["co2"] / 1000
    # FIX 1: log-transform for display; keep raw for median calc
    work["co2_gt_log"] = np.log10(work["co2_gt"])
    work = _with_region_label(work)
    x_abs = max(abs(work["co2_cagr"].min()), abs(work["co2_cagr"].max()), 0.01) * 1.1
    # FIX 3: median split on raw Gt (not log-transformed median)
    y_med_raw = work["co2_gt"].median()
    y_med_log = np.log10(y_med_raw) if y_med_raw > 0 else work["co2_gt_log"].median()
    y_min_log = work["co2_gt_log"].min() - 0.05
    y_max_log = work["co2_gt_log"].max() * 1.04
    # FIX 4: opacity 0.62 (was 0.82)
    fig = px.scatter(
        work,
        x="co2_cagr",
        y="co2_gt_log",
        color="region_label",
        color_discrete_map=DISPLAY_REGION_COLORS,
        custom_data=["country", "region_label", "co2_gt", "co2_cagr"],
        title="CO2 Growth Rate vs Emissions Volume",
        opacity=0.62,  # FIX 4
    )
    fig.update_traces(
        marker=dict(size=7, line=dict(width=0.6, color="white")),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Region: %{customdata[1]}<br>"
            "Total CO2: %{customdata[2]:,.2f} Gt<br>"
            "CAGR: %{customdata[3]:+.2%}"
            "<extra></extra>"
        ),
    )
    # FIX 3: Quadrant shading centred on log(median) of raw Gt
    for (x0, x1), (y0, y1), alpha in [
        ((0, x_abs), (y_med_log, y_max_log), 0.045),
        ((-x_abs, 0), (y_med_log, y_max_log), 0.025),
        ((0, x_abs), (y_min_log, y_med_log), 0.030),
        ((-x_abs, 0), (y_min_log, y_med_log), 0.015),
    ]:
        fig.add_shape(type="rect", xref="x", yref="y",
                      x0=x0, x1=x1, y0=y0, y1=y1,
                      fillcolor=f"rgba(12,34,53,{alpha})", line_width=0, layer="below")
    fig.add_vline(x=0, line_dash="dot", line_color="#697791")
    fig.add_hline(y=y_med_log, line_dash="dot", line_color="#697791")
    for xp, yp, text in [
        (0.74, 0.88, "Large emitter<br>growing"),
        (0.26, 0.88, "Large emitter<br>declining"),
        (0.74, 0.14, "Small emitter<br>growing"),
        (0.26, 0.14, "Small emitter<br>declining"),
    ]:
        fig.add_annotation(
            x=xp, y=yp, xref="paper", yref="paper",
            text=text, showarrow=False, align="center",
            font=dict(color="#334155", size=10.5),
            bgcolor="rgba(255,255,255,.78)", bordercolor="#D8E2EE", borderwidth=1, borderpad=4,
        )
    # FIX 2: label top emitters by volume + CAGR outliers
    n = min(label_n, max(1, len(work) // 4))
    top_volume = work.nlargest(n, "co2_gt")
    cagr_extremes = pd.concat([
        work.nlargest(n, "co2_cagr"),
        work.nsmallest(n, "co2_cagr"),
    ])
    to_label = pd.concat([top_volume, cagr_extremes]).drop_duplicates(subset=["country"]).sort_values("co2_cagr")
    for i, (_, row) in enumerate(to_label.iterrows()):
        ay = -22 if i % 2 == 0 else 22
        fig.add_annotation(
            x=row["co2_cagr"], y=row["co2_gt_log"],
            text=_short_country_label(str(row["country"]), max_len=14),
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#9AA7BC",
            ax=0, ay=ay,
            font=dict(size=9.5, color=NAVY),
            bgcolor="rgba(255,255,255,.92)", bordercolor="#D8E2EE", borderwidth=1, borderpad=2,
        )
    # FIX 1: human-readable log ticks on y-axis
    tick_vals_gt = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10, 20]
    tick_vals_log = [np.log10(v) for v in tick_vals_gt if y_min_log <= np.log10(v) <= y_max_log]
    tick_text_gt = [f"{v:g} Gt" for v in tick_vals_gt if y_min_log <= np.log10(v) <= y_max_log]
    fig.update_xaxes(tickformat=".0%", title="CO2 CAGR, 2022-2024",
                     range=[-x_abs, x_abs], zeroline=False)
    fig.update_yaxes(title="Total CO2 (Gt, log scale)", range=[y_min_log, y_max_log],
                     tickmode="array", tickvals=tick_vals_log, ticktext=tick_text_gt)
    fig = apply_common_layout(fig, 520)
    fig.update_layout(
        legend_title_text="Region",
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5,
                    bgcolor="rgba(255,255,255,.78)", bordercolor="#D8E2EE", borderwidth=1, font=dict(size=10)),
        title=dict(text="CO2 Growth Rate vs Emissions Volume", font=dict(size=15, color=NAVY), x=0.02, y=0.97),
    )
    return _with_chart_margins(fig, l=64, r=28, t=70, b=118)


def _short_country_label(country: str, max_len: int = 16) -> str:
    aliases = {
        "Democratic Republic of Congo": "DR Congo",
        "Dominican Republic": "Dominican Rep.",
        "United Kingdom": "United Kingdom",
        "United States": "United States",
    }
    label = aliases.get(str(country), str(country))
    return label if len(label) <= max_len else f"{label[:max_len - 1]}..."


def create_fuel_decomposition_area(fuel_long: pd.DataFrame, region: str):
    # Power BI equivalent: absolute stacked area chart (native Mt/Gt units, not normalized to 100%).
    absolute = compute_fuel_absolute(fuel_long, region).dropna(subset=["value"]).copy()
    if absolute.empty or absolute["value"].sum() <= 0:
        return _empty(f"Fuel Mix by Source - {region}")
    fuel_order = list(FUEL_COLUMNS.values())
    absolute = absolute[absolute["fuel_source"].isin(fuel_order)]
    value_wide = (
        absolute.pivot_table(index="year", columns="fuel_source", values="value", aggfunc="sum")
        .reindex(columns=fuel_order)
        .fillna(0)
        .sort_index()
    )
    if value_wide.empty or value_wide.to_numpy().sum() <= 0:
        return _empty(f"Fuel Mix by Source - {region}")

    # Express in Gt CO2 once totals get large enough that Mt is hard to read.
    use_gt = value_wide.to_numpy().max(initial=0) >= 1000 or value_wide.sum(axis=1).max() >= 1000
    scale = 1000 if use_gt else 1
    unit = "Gt" if use_gt else "Mt"

    fig = go.Figure()
    for source in fuel_order:
        values = value_wide[source] / scale
        if values.sum() <= 0:
            continue
        color = FUEL_COLORS.get(source, "#667A94")
        fig.add_trace(go.Scatter(
            x=value_wide.index,
            y=values,
            name=source,
            mode="lines",
            stackgroup="fuel",
            line=dict(width=1.1, color=color),
            fillcolor=_hex_to_rgba(color, 0.82),
            hovertemplate=f"<b>{source}</b><br>Year: %{{x}}<br>Emissions: %{{y:,.2f}} {unit}<extra></extra>",
        ))
    fig.update_yaxes(rangemode="tozero", ticksuffix=f" {unit}")
    fig.update_layout(
        yaxis_title=f"CO2 emissions ({unit})",
        xaxis_title="",
        legend_title_text="",
        hovermode="x unified",
        title=f"Fuel Mix by Source - {region}",
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
    fig.update_layout(title="Fuel Share Change", height=440, margin=dict(l=8, r=8, t=56, b=8), paper_bgcolor="rgba(0,0,0,0)")
    return fig

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

from src.utils.constants import AGE_GROUP_ORDER, SCREEN_SEGMENT_ORDER, LIFESTYLE_ORDER, BEHAVIOR_FEATURES
from src.visualization.colors import BLUE, GREEN, ORANGE, RED, GRAY, LIFESTYLE_COLORS, SCREEN_SEGMENT_COLORS
from src.visualization.theme import apply_dark_theme


def kpi_card_values(df: pd.DataFrame) -> dict:
    heavy_mask = df["Screen_Time_Segment"].isin(["Heavy (8–12h)", "Extreme (>12h)"])
    return {
        "Total Users": f"{len(df):,}",
        "Avg Daily Screen Time": f"{df['Daily_Screen_Time_Hours'].mean():.2f}h",
        "Avg App Usage": f"{df['Total_App_Usage_Hours'].mean():.2f}h",
        "Avg Apps Used": f"{df['Number_of_Apps_Used'].mean():.2f}",
        "Heavy / Extreme Users": f"{heavy_mask.mean() * 100:.1f}%",
    }


def screen_time_density(df: pd.DataFrame, by: str | None = None) -> go.Figure:
    fig = go.Figure()
    if by is None:
        groups = [("All Users", df)]
    else:
        groups = list(df.groupby(by, observed=True))

    palette = [BLUE, ORANGE, GREEN, RED, GRAY]
    for i, (name, g) in enumerate(groups):
        values = g["Daily_Screen_Time_Hours"].dropna().values
        if len(values) < 3:
            continue
        xs = np.linspace(values.min(), values.max(), 250)
        kde = gaussian_kde(values)
        fig.add_trace(go.Scatter(
            x=xs,
            y=kde(xs),
            mode="lines",
            fill="tozeroy",
            name=str(name),
            opacity=0.65,
            line=dict(width=2, color=palette[i % len(palette)]),
        ))
    return apply_dark_theme(fig, "Daily Screen Time Density", 360)


def screen_segment_bar(df: pd.DataFrame) -> go.Figure:
    summary = df["Screen_Time_Segment"].value_counts().reindex(SCREEN_SEGMENT_ORDER).fillna(0).reset_index()
    summary.columns = ["Screen_Time_Segment", "Users"]
    summary["Percentage"] = summary["Users"] / len(df) * 100
    fig = px.bar(
        summary,
        x="Users",
        y="Screen_Time_Segment",
        orientation="h",
        text=summary["Percentage"].map(lambda x: f"{x:.1f}%"),
        color="Screen_Time_Segment",
        color_discrete_map=SCREEN_SEGMENT_COLORS,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return apply_dark_theme(fig, "Screen Time Segments", 360)


def lifestyle_distribution_bar(df: pd.DataFrame) -> go.Figure:
    summary = df["Dominant_Lifestyle"].value_counts().reindex(LIFESTYLE_ORDER).fillna(0).reset_index()
    summary.columns = ["Dominant_Lifestyle", "Users"]
    fig = px.bar(
        summary,
        x="Users",
        y="Dominant_Lifestyle",
        orientation="h",
        text="Users",
        color="Dominant_Lifestyle",
        color_discrete_map=LIFESTYLE_COLORS,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return apply_dark_theme(fig, "Dominant Digital Lifestyle", 360)


def location_screen_time_bar(df: pd.DataFrame) -> go.Figure:
    summary = (
        df.groupby("Location", observed=True)["Daily_Screen_Time_Hours"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(summary, x="Daily_Screen_Time_Hours", y="Location", orientation="h", text="Daily_Screen_Time_Hours")
    fig.update_traces(marker_color=BLUE, texttemplate="%{text:.2f}h", textposition="outside", cliponaxis=False)
    return apply_dark_theme(fig, "Average Screen Time by Location", 360)


def age_usage_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = ["Social_Media_Usage_Hours", "Productivity_App_Usage_Hours", "Gaming_App_Usage_Hours", "Total_App_Usage_Hours", "Daily_Screen_Time_Hours"]
    table = df.groupby("Age_Group", observed=True)[cols].mean().reindex(AGE_GROUP_ORDER)
    fig = px.imshow(
        table,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="YlGnBu",
        labels=dict(x="Metric", y="Age group", color="Hours"),
    )
    return apply_dark_theme(fig, "Average Usage Hours by Age Group", 420)


def gender_grouped_bar(df: pd.DataFrame) -> go.Figure:
    cols = ["Social_Media_Usage_Hours", "Productivity_App_Usage_Hours", "Gaming_App_Usage_Hours", "Total_App_Usage_Hours", "Daily_Screen_Time_Hours"]
    long = df.groupby("Gender", observed=True)[cols].mean().reset_index().melt(id_vars="Gender", var_name="Metric", value_name="Hours")
    fig = px.bar(long, x="Metric", y="Hours", color="Gender", barmode="group", text="Hours")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    return apply_dark_theme(fig, "Usage by Gender", 420)


def apps_vs_screen_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="Number_of_Apps_Used",
        y="Daily_Screen_Time_Hours",
        color="Dominant_Lifestyle",
        color_discrete_map=LIFESTYLE_COLORS,
        hover_data=["User_ID", "Age", "Gender", "Location", "Total_App_Usage_Hours"],
        opacity=0.45,
        trendline="ols",
    )
    return apply_dark_theme(fig, "Apps Used vs. Daily Screen Time", 450)


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    corr = df[BEHAVIOR_FEATURES].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    return apply_dark_theme(fig, "Correlation Matrix", 460)


def pca_user_map(df: pd.DataFrame) -> go.Figure:
    if "PCA_1" not in df.columns or "PCA_2" not in df.columns:
        raise ValueError("PCA_1 and PCA_2 not found. Run segmentation.py first.")
    color_col = "Cluster_Name" if "Cluster_Name" in df.columns else "Dominant_Lifestyle"
    fig = px.scatter(
        df,
        x="PCA_1",
        y="PCA_2",
        color=color_col,
        hover_data=["User_ID", "Age", "Gender", "Location", "Daily_Screen_Time_Hours"],
        opacity=0.65,
    )
    return apply_dark_theme(fig, "User Map: Behavioral Space (PCA)", 500)


def cluster_profile_parallel(df: pd.DataFrame) -> go.Figure:
    if "Cluster_Name" not in df.columns:
        raise ValueError("Cluster_Name not found. Run segmentation.py first.")
    cols = ["Age", "Number_of_Apps_Used", "Social_Media_Usage_Hours", "Productivity_App_Usage_Hours", "Gaming_App_Usage_Hours", "Daily_Screen_Time_Hours"]
    fig = px.parallel_coordinates(
        df,
        dimensions=cols,
        color="Cluster_ID" if "Cluster_ID" in df.columns else None,
        color_continuous_scale="Turbo",
    )
    return apply_dark_theme(fig, "Parallel Coordinates: User Behavioral Profiles", 520)


def slopegraph_light_vs_heavy(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work["Comparison_Group"] = np.where(
        work["Screen_Time_Segment"].isin(["Heavy (8–12h)", "Extreme (>12h)"]),
        "Heavy / Extreme",
        "Light / Moderate",
    )
    metrics = {
        "Social": "Social_Media_Usage_Hours",
        "Productivity": "Productivity_App_Usage_Hours",
        "Gaming": "Gaming_App_Usage_Hours",
    }
    summary = work.groupby("Comparison_Group", observed=True)[list(metrics.values())].mean()
    fig = go.Figure()
    for label, col in metrics.items():
        y = [summary.loc["Light / Moderate", col], summary.loc["Heavy / Extreme", col]]
        fig.add_trace(go.Scatter(x=["Light / Moderate", "Heavy / Extreme"], y=y, mode="lines+markers+text", name=label, text=[f"{y[0]:.2f}", f"{y[1]:.2f}"], textposition="top center"))
    return apply_dark_theme(fig, "Slopegraph: Light vs Heavy Users", 420)

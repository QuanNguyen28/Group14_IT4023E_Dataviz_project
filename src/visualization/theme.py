"""Plotly theme utilities."""

from __future__ import annotations

import plotly.graph_objects as go

from src.visualization.colors import DARK_BG, CARD_BG, GRID, TEXT, MUTED_TEXT


def apply_dark_theme(fig: go.Figure, title: str | None = None, height: int | None = None) -> go.Figure:
    # Apply a custom dark theme to a Plotly figure
    fig.update_layout(
        title=title,
        height=height,
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter, Arial, sans-serif", size=13),
        title_font=dict(size=18, color=TEXT),
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED_TEXT),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def apply_light_theme(fig: go.Figure, title: str | None = None, height: int | None = None) -> go.Figure:
    fig.update_layout(
        title=title,
        height=height,
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=13),
        margin=dict(l=40, r=30, t=60, b=40),
    )
    fig.update_xaxes(gridcolor="#E5E7EB", zerolinecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#E5E7EB", zerolinecolor="#CBD5E1")
    return fig

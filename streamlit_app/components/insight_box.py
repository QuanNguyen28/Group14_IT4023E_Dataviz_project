"""Insight callout component."""

from __future__ import annotations

import streamlit as st

from streamlit_app.components.layout import insight_list


def render_insight_box(title: str, insights: list[str]) -> None:
    insight_list(insights, title)

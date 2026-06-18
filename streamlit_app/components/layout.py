"""Layout helpers."""

from __future__ import annotations

from html import escape

import streamlit as st

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def render_html(markup: str) -> None:
    """Render compact HTML without Markdown treating indentation as code."""
    if hasattr(st, "html"):
        st.html(markup)
    else:
        st.markdown(markup, unsafe_allow_html=True)


def page_header(title: str, question: str, accent: str = "#D94C45", mode: str = "Analytical Report") -> None:
    """Header intentionally hidden to keep the dashboard dense."""
    return None


def filter_summary(items: list[tuple[str, str | int | float]]) -> None:
    """Filter chips are hidden because the sidebar already shows active controls."""
    return None


def section_header(title: str, subtitle: str = "", kicker: str = "Visual") -> None:
    render_html(
        '<div class="section-heading"><div>'
        f'<div class="section-title">{escape(title)}</div>'
        "</div></div>"
    )


def insight_list(items: list[str], title: str = "Executive Insights") -> None:
    rendered = "".join(f"<div class='insight'>{escape(item)}</div>" for item in items)
    render_html(
        '<div class="insight-panel">'
        f'<div class="insight-title"><span class="insight-mark">i</span>{escape(title)}</div>'
        f"{rendered}"
        "</div>"
    )


def single_insight(text: str) -> None:
    render_html(f'<div class="insight single-insight">{escape(text)}</div>')

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
    """Render a compact executive dashboard header."""
    render_html(
        '<div class="page-hero" style="--hero-accent:{accent};">'
        '<div><div class="page-eyebrow">Global CO2 Dashboard</div>'
        "<h1>{title}</h1>"
        '<div class="page-question">{question}</div></div>'
        '<div class="hero-meta">'
        '<div class="hero-pill">{mode}</div>'
        '<div class="hero-pill">OWID CO2 Dataset</div>'
        "</div></div>".format(
            accent=escape(accent),
            title=escape(title),
            question=escape(question),
            mode=escape(mode),
        )
    )


def filter_summary(items: list[tuple[str, str | int | float]]) -> None:
    chips = []
    for key, value in items:
        chips.append(
            '<span class="filter-chip">'
            f'<span class="filter-key">{escape(str(key))}</span>'
            f'<span class="filter-value">{escape(str(value))}</span>'
            "</span>"
        )
    render_html(f'<div class="filter-strip">{"".join(chips)}</div>')


def section_header(title: str, subtitle: str = "", kicker: str = "Visual") -> None:
    render_html(
        '<div class="section-heading"><div>'
        f'<div class="section-kicker">{escape(kicker)}</div>'
        f'<div class="section-title">{escape(title)}</div>'
        f'<div class="section-subtitle">{escape(subtitle)}</div>'
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

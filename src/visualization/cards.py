"""HTML helpers for dashboard cards."""

from __future__ import annotations

from html import escape


def _soft_color(hex_color: str) -> str:
    clean = hex_color.lstrip("#")
    if len(clean) != 6:
        return "rgba(214,59,50,.10)"
    r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    return f"rgba({r},{g},{b},.11)"


def _stat_chip(label: str, value: str) -> str:
    label_safe = escape(str(label))
    value_safe = escape(str(value))
    return (
        '<div class="detail-stat">'
        f'<div class="detail-stat-label">{label_safe}</div>'
        f'<div class="detail-stat-value">{value_safe}</div>'
        "</div>"
    )


def country_detail_panel(detail: dict, stats: list[tuple[str, str]], accent: str = "#0F8B5F") -> str:
    """Render a rich drill-down panel for a single country.

    `stats` is a list of (label, formatted_value) pairs already formatted by
    the caller, kept presentation-agnostic so this module has no formatting
    logic of its own.
    """
    country_safe = escape(str(detail.get("country", "")))
    region_safe = escape(str(detail.get("region", "Unknown")))
    income_safe = escape(str(detail.get("income_group", "Unknown")))
    accent_safe = escape(accent)
    chips = "".join(_stat_chip(label, value) for label, value in stats)
    return (
        f'<div class="country-detail-panel" style="--accent:{accent_safe};">'
        '<div class="country-detail-head">'
        f'<div class="country-detail-name">{country_safe}</div>'
        f'<div class="country-detail-tags">'
        f'<span class="country-detail-tag">{region_safe}</span>'
        f'<span class="country-detail-tag">{income_safe}</span>'
        "</div></div>"
        f'<div class="detail-grid">{chips}</div>'
        "</div>"
    )



def kpi_card(title: str, value: str, subtitle: str = "", accent: str = "#D94C45", icon: str = "CO2") -> str:
    title_safe = escape(str(title))
    value_safe = escape(str(value))
    subtitle_safe = escape(str(subtitle))
    icon_safe = escape(str(icon))
    accent_safe = escape(accent)
    accent_soft = _soft_color(accent)
    return (
        f'<div class="kpi-card" style="--accent:{accent_safe};--accent-soft:{accent_soft};">'
        f'<div class="kpi-icon">{icon_safe}</div>'
        '<div class="kpi-body">'
        f'<div class="kpi-title">{title_safe}</div>'
        f'<div class="kpi-value">{value_safe}</div>'
        f'<div class="kpi-subtitle">{subtitle_safe}</div>'
        "</div></div>"
    )

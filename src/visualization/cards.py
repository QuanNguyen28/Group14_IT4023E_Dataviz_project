"""HTML helpers for dashboard cards."""

from __future__ import annotations

from html import escape


def _soft_color(hex_color: str) -> str:
    clean = hex_color.lstrip("#")
    if len(clean) != 6:
        return "rgba(214,59,50,.10)"
    r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    return f"rgba({r},{g},{b},.11)"


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

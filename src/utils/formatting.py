"""Human-readable formatting helpers."""

from __future__ import annotations

import math
from typing import Any


def is_missing(value: Any) -> bool:
    try:
        return value is None or math.isnan(float(value))
    except (TypeError, ValueError):
        return value is None


def fmt_number(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.{decimals}f}k"
    return f"{value:.{decimals}f}"


def fmt_mt_as_gt(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    return f"{float(value) / 1000:.{decimals}f} Gt"


def fmt_tonnes(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    return f"{float(value):.{decimals}f} t / person"


def fmt_pct(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    return f"{float(value) * 100:.{decimals}f}%"


def fmt_usd(value: Any, decimals: int = 0) -> str:
    if is_missing(value):
        return "No data"
    value = float(value)
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}k"
    return f"${value:.{decimals}f}"


def fmt_pp(value: Any, decimals: int = 1) -> str:
    """Format a value already expressed in percentage-point units (not a fraction)."""
    if is_missing(value):
        return "No data"
    return f"{float(value):+.{decimals}f}%"


def fmt_people(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.{decimals}f}k"
    return f"{value:.0f}"


def fmt_share(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return "No data"
    return f"{float(value):.{decimals}f}%"



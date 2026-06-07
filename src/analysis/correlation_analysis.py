"""Correlation, regression-ready and density-ready data utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


def pairwise_correlation_report(df: pd.DataFrame, target: str, predictors: list[str]) -> pd.DataFrame:
    rows = []
    for col in predictors:
        clean = df[[target, col]].dropna()
        if len(clean) < 3:
            continue
        pearson_val, pearson_p = pearsonr(clean[col], clean[target])
        spearman_val, spearman_p = spearmanr(clean[col], clean[target])
        rows.append({
            "predictor": col,
            "target": target,
            "pearson_r": round(pearson_val, 3),
            "pearson_p": pearson_p,
            "spearman_r": round(spearman_val, 3),
            "spearman_p": spearman_p,
        })
    return pd.DataFrame(rows).sort_values("pearson_r", ascending=False)


def add_jitter(series: pd.Series, amount: float = 0.08, seed: int = 42) -> pd.Series:
    rng = np.random.default_rng(seed)
    return series + rng.normal(0, amount, len(series))

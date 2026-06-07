# export aggregated tables for PowerBI dashboard
from __future__ import annotations

import pandas as pd

from src.analysis.descriptive_stats import kpi_summary, screen_segment_summary, categorical_summary
from src.analysis.demographic_analysis import age_group_usage, gender_usage, location_usage, lifestyle_by_age, lifestyle_by_gender
from src.analysis.behavioral_analysis import lifestyle_profiles
from src.analysis.segmentation import fit_kmeans_pca
from src.data.feature_engineering import build_features
from src.utils.constants import (
    FEATURE_DATA_PATH,
    CLUSTERED_DATA_PATH,
    POWERBI_DATA_PATH,
    AGGREGATED_DIR,
)
from src.utils.helpers import save_csv, ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_analysis_data() -> pd.DataFrame:
    if CLUSTERED_DATA_PATH.exists():
        return pd.read_csv(CLUSTERED_DATA_PATH)
    if FEATURE_DATA_PATH.exists():
        df = pd.read_csv(FEATURE_DATA_PATH)
    else:
        df = build_features()
    clustered, *_ = fit_kmeans_pca(df)
    save_csv(clustered, CLUSTERED_DATA_PATH)
    return clustered


def export_powerbi_tables(df: pd.DataFrame | None = None) -> dict[str, str]:
    df = get_analysis_data() if df is None else df.copy()
    ensure_dir(AGGREGATED_DIR)

    outputs = {}
    outputs["powerbi_model"] = str(save_csv(df, POWERBI_DATA_PATH))
    outputs["kpi_summary"] = str(save_csv(pd.DataFrame(kpi_summary(df).items(), columns=["Metric", "Value"]), AGGREGATED_DIR / "kpi_summary.csv"))
    outputs["screen_segments"] = str(save_csv(screen_segment_summary(df), AGGREGATED_DIR / "screen_time_segment_summary.csv"))
    outputs["gender_summary"] = str(save_csv(gender_usage(df), AGGREGATED_DIR / "gender_summary.csv"))
    outputs["location_summary"] = str(save_csv(location_usage(df), AGGREGATED_DIR / "location_summary.csv"))
    outputs["age_group_summary"] = str(save_csv(age_group_usage(df), AGGREGATED_DIR / "age_group_summary.csv"))
    outputs["lifestyle_summary"] = str(save_csv(lifestyle_profiles(df), AGGREGATED_DIR / "lifestyle_summary.csv"))
    outputs["location_counts"] = str(save_csv(categorical_summary(df, "Location"), AGGREGATED_DIR / "location_counts.csv"))
    outputs["gender_counts"] = str(save_csv(categorical_summary(df, "Gender"), AGGREGATED_DIR / "gender_counts.csv"))
    outputs["lifestyle_by_age"] = str(save_csv(lifestyle_by_age(df), AGGREGATED_DIR / "lifestyle_by_age.csv"))
    outputs["lifestyle_by_gender"] = str(save_csv(lifestyle_by_gender(df), AGGREGATED_DIR / "lifestyle_by_gender.csv"))

    if "Cluster_Name" in df.columns:
        cluster_summary = (
            df.groupby(["Cluster_ID", "Cluster_Name"], observed=True)
            .agg(
                Users=("User_ID", "count"),
                Avg_Age=("Age", "mean"),
                Avg_Screen_Time=("Daily_Screen_Time_Hours", "mean"),
                Avg_Total_App_Usage=("Total_App_Usage_Hours", "mean"),
                Avg_Apps_Used=("Number_of_Apps_Used", "mean"),
                Avg_Social=("Social_Media_Usage_Hours", "mean"),
                Avg_Productivity=("Productivity_App_Usage_Hours", "mean"),
                Avg_Gaming=("Gaming_App_Usage_Hours", "mean"),
            )
            .round(2)
            .reset_index()
        )
        outputs["cluster_summary"] = str(save_csv(cluster_summary, AGGREGATED_DIR / "cluster_summary.csv"))

    return outputs


def main() -> None:
    outputs = export_powerbi_tables()
    for name, path in outputs.items():
        logger.info("Exported %-24s -> %s", name, path)


if __name__ == "__main__":
    main()

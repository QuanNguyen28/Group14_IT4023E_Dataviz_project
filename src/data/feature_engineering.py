# feature engineering for the smartphone usage dataset
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.clean_data import clean_data
from src.utils.constants import (
    CLEAN_DATA_PATH,
    FEATURE_DATA_PATH,
    AGE_GROUP_ORDER,
    SCREEN_SEGMENT_ORDER,
    APP_CATEGORY_COLS,
)
from src.utils.helpers import save_csv, ordered_categorical
from src.utils.logger import get_logger

logger = get_logger(__name__)


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bins = [17, 24, 34, 44, 54, 120]
    labels = AGE_GROUP_ORDER
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)
    return df


def add_screen_time_segment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bins = [-np.inf, 4, 8, 12, np.inf]
    labels = SCREEN_SEGMENT_ORDER
    df["Screen_Time_Segment"] = pd.cut(
        df["Daily_Screen_Time_Hours"], bins=bins, labels=labels, right=False
    )
    return df


def dominant_lifestyle(row: pd.Series) -> str:
    values = {
        "Social Enthusiast": row["Social_Media_Usage_Hours"],
        "Productivity Focused": row["Productivity_App_Usage_Hours"],
        "Mobile Gamer": row["Gaming_App_Usage_Hours"],
    }
    return max(values, key=values.get)


def build_features(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Create analysis-ready features for dashboard and Power BI."""
    if df is None:
        try:
            df = pd.read_csv(CLEAN_DATA_PATH)
        except FileNotFoundError:
            df = clean_data()
    else:
        df = df.copy()

    df = add_age_group(df)
    df = add_screen_time_segment(df)
    df["Dominant_Lifestyle"] = df.apply(dominant_lifestyle, axis=1)

    df["Category_Usage_Sum"] = df[APP_CATEGORY_COLS].sum(axis=1)
    df["Entertainment_Hours"] = df["Social_Media_Usage_Hours"] + df["Gaming_App_Usage_Hours"]
    df["Screen_to_App_Gap"] = df["Daily_Screen_Time_Hours"] - df["Total_App_Usage_Hours"]
    df["App_Fragmentation_Score"] = df["Total_App_Usage_Hours"] / df["Number_of_Apps_Used"].replace(0, np.nan)
    df["Category_vs_Total_Diff"] = df["Category_Usage_Sum"] - df["Total_App_Usage_Hours"]

    # Ratios are useful for pattern discovery, but should not be interpreted as exact parts of total if source data is inconsistent.
    df["Social_Ratio"] = df["Social_Media_Usage_Hours"] / df["Category_Usage_Sum"].replace(0, np.nan)
    df["Productivity_Ratio"] = df["Productivity_App_Usage_Hours"] / df["Category_Usage_Sum"].replace(0, np.nan)
    df["Gaming_Ratio"] = df["Gaming_App_Usage_Hours"] / df["Category_Usage_Sum"].replace(0, np.nan)

    df["Age_Group"] = ordered_categorical(df["Age_Group"].astype(str), AGE_GROUP_ORDER)
    df["Screen_Time_Segment"] = ordered_categorical(df["Screen_Time_Segment"].astype(str), SCREEN_SEGMENT_ORDER)
    return df


def main() -> None:
    df = build_features()
    path = save_csv(df, FEATURE_DATA_PATH)
    logger.info("Feature data saved to %s with shape %s", path, df.shape)


if __name__ == "__main__":
    main()

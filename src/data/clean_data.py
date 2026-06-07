# clean and preprocess the raw dataset for analysis and visualization
from __future__ import annotations

import pandas as pd

from src.data.load_data import load_raw_data
from src.data.validators import validate_required_columns
from src.utils.constants import CLEAN_DATA_PATH, NUMERIC_COLS, CATEGORICAL_COLS
from src.utils.helpers import save_csv, snake_case_columns
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_data(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_raw_data() if df is None else df.copy()
    df = snake_case_columns(df)
    validate_required_columns(df)

    df = df.drop_duplicates().reset_index(drop=True)

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in CATEGORICAL_COLS:
        df[col] = df[col].astype(str).str.strip().str.title()

    if "User_ID" in df.columns:
        df["User_ID"] = df["User_ID"].astype(str).str.strip()

    return df


def main() -> None:
    df = clean_data()
    path = save_csv(df, CLEAN_DATA_PATH)
    logger.info("Cleaned data saved to %s with shape %s", path, df.shape)


if __name__ == "__main__":
    main()

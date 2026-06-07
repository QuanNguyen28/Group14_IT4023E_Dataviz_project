"""project data pipeline.
+ run from project root:
    python -m src.run_pipeline
"""

from src.data.clean_data import clean_data
from src.data.feature_engineering import build_features
from src.analysis.segmentation import fit_kmeans_pca
from src.data.export_powerbi import export_powerbi_tables
from src.utils.constants import CLEAN_DATA_PATH, FEATURE_DATA_PATH, CLUSTERED_DATA_PATH
from src.utils.helpers import save_csv
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("Step 1/4: cleaning raw data")
    clean = clean_data()
    save_csv(clean, CLEAN_DATA_PATH)

    logger.info("Step 2/4: feature engineering")
    features = build_features(clean)
    save_csv(features, FEATURE_DATA_PATH)

    logger.info("Step 3/4: clustering and PCA")
    clustered, *_ = fit_kmeans_pca(features)
    save_csv(clustered, CLUSTERED_DATA_PATH)

    logger.info("Step 4/4: exporting Power BI tables")
    export_powerbi_tables(clustered)

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()

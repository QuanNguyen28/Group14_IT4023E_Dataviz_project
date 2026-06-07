"""KMeans clustering and PCA projection for lifestyle archetypes."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.data.feature_engineering import build_features
from src.utils.constants import BEHAVIOR_FEATURES, CLUSTERED_DATA_PATH, FEATURE_DATA_PATH
from src.utils.helpers import save_csv
from src.utils.logger import get_logger

logger = get_logger(__name__)


def choose_cluster_name(row: pd.Series) -> str:
    if row["Daily_Screen_Time_Hours"] < 5:
        return "Digital Minimalists"
    if row["Gaming_App_Usage_Hours"] >= max(row["Social_Media_Usage_Hours"], row["Productivity_App_Usage_Hours"]):
        return "Mobile Gamers"
    if row["Social_Media_Usage_Hours"] >= row["Productivity_App_Usage_Hours"]:
        return "Social Enthusiasts"
    return "Productivity Focused"


def fit_kmeans_pca(
    df: pd.DataFrame,
    features: list[str] | None = None,
    n_clusters: int = 4,
    random_state: int = 42,
) -> tuple[pd.DataFrame, KMeans, StandardScaler, PCA]:
    """Fit scaler + KMeans + PCA and return augmented DataFrame."""
    features = features or BEHAVIOR_FEATURES
    out = df.copy()
    X = out[features].fillna(out[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20)
    out["Cluster_ID"] = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2, random_state=random_state)
    coords = pca.fit_transform(X_scaled)
    out["PCA_1"] = coords[:, 0]
    out["PCA_2"] = coords[:, 1]

    profiles = out.groupby("Cluster_ID", observed=True)[features].mean()
    names = profiles.apply(choose_cluster_name, axis=1).to_dict()

    used = {}
    final_names = {}
    for cid, name in names.items():
        used[name] = used.get(name, 0) + 1
        final_names[cid] = name if used[name] == 1 else f"{name} {used[name]}"
    out["Cluster_Name"] = out["Cluster_ID"].map(final_names)

    out["PCA_Explained_Variance_1"] = pca.explained_variance_ratio_[0]
    out["PCA_Explained_Variance_2"] = pca.explained_variance_ratio_[1]
    return out, kmeans, scaler, pca


def cluster_quality(df: pd.DataFrame, features: list[str] | None = None, k_range: range = range(2, 8)) -> pd.DataFrame:
    features = features or BEHAVIOR_FEATURES
    X = df[features].fillna(df[features].median())
    X_scaled = StandardScaler().fit_transform(X)
    rows = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X_scaled)
        rows.append({
            "k": k,
            "inertia": model.inertia_,
            "silhouette": silhouette_score(X_scaled, labels),
        })
    return pd.DataFrame(rows)


def cluster_profiles(df: pd.DataFrame) -> pd.DataFrame:
    features = BEHAVIOR_FEATURES
    return (
        df.groupby(["Cluster_ID", "Cluster_Name"], observed=True)[features]
        .mean()
        .round(2)
        .reset_index()
    )


def main() -> None:
    try:
        df = pd.read_csv(FEATURE_DATA_PATH)
    except FileNotFoundError:
        df = build_features()
    out, *_ = fit_kmeans_pca(df)
    path = save_csv(out, CLUSTERED_DATA_PATH)
    logger.info("Clustered data saved to %s with shape %s", path, out.shape)


if __name__ == "__main__":
    main()

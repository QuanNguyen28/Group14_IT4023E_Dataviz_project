from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
AGGREGATED_DIR = DATA_DIR / "aggregated"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

RAW_DATA_PATH = RAW_DIR / "mobile_usage_behavioral_analysis.csv"
CLEAN_DATA_PATH = PROCESSED_DIR / "smartphone_clean.csv"
FEATURE_DATA_PATH = PROCESSED_DIR / "smartphone_features.csv"
CLUSTERED_DATA_PATH = PROCESSED_DIR / "smartphone_clustered.csv"
POWERBI_DATA_PATH = PROCESSED_DIR / "smartphone_powerbi_model.csv"

USER_ID_COL = "User_ID"
NUMERIC_COLS = [
    "Age",
    "Total_App_Usage_Hours",
    "Daily_Screen_Time_Hours",
    "Number_of_Apps_Used",
    "Social_Media_Usage_Hours",
    "Productivity_App_Usage_Hours",
    "Gaming_App_Usage_Hours",
]
CATEGORICAL_COLS = ["Gender", "Location"]
USAGE_COLS = [
    "Total_App_Usage_Hours",
    "Daily_Screen_Time_Hours",
    "Number_of_Apps_Used",
    "Social_Media_Usage_Hours",
    "Productivity_App_Usage_Hours",
    "Gaming_App_Usage_Hours",
]
APP_CATEGORY_COLS = [
    "Social_Media_Usage_Hours",
    "Productivity_App_Usage_Hours",
    "Gaming_App_Usage_Hours",
]
BEHAVIOR_FEATURES = [
    "Daily_Screen_Time_Hours",
    "Total_App_Usage_Hours",
    "Number_of_Apps_Used",
    "Social_Media_Usage_Hours",
    "Productivity_App_Usage_Hours",
    "Gaming_App_Usage_Hours",
]
AGE_GROUP_ORDER = ["18–24", "25–34", "35–44", "45–54", "55–59"]
SCREEN_SEGMENT_ORDER = ["Light (<4h)", "Moderate (4–8h)", "Heavy (8–12h)", "Extreme (>12h)"]
LIFESTYLE_ORDER = ["Social Enthusiast", "Productivity Focused", "Mobile Gamer"]

COLOR_MAP = {
    "Social Enthusiast": "#3B82F6",
    "Productivity Focused": "#22C55E",
    "Mobile Gamer": "#F59E0B",
    "Light (<4h)": "#22C55E",
    "Moderate (4–8h)": "#3B82F6",
    "Heavy (8–12h)": "#F59E0B",
    "Extreme (>12h)": "#EF4444",
}

"""Central configuration: feature contract, target, and reproducibility settings."""

from pathlib import Path

# The 15-feature contract from notebook 02. Serving and monitoring both
# validate against this contract, so drift and API schema stay in sync.
FEATURES = [
    "week_sin", "week_cos", "month",
    "archetype_enc", "category_enc", "market_enc",
    "store_size", "city_pop_k", "promo_flag", "temp_idx",
    "lag_1w", "lag_4w", "lag_13w", "rolling_4w_mean", "rolling_13w_mean",
]
TARGET = "units_sold"

RANDOM_STATE = 42

VALID_ARCHETYPES = ["urban", "suburban", "rural", "outlet"]
VALID_CATEGORIES = ["fashion", "lingerie", "home_textiles", "hard_goods"]
VALID_MARKETS = ["DE", "AT", "PL", "CZ", "SK", "HU"]

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = REPO_ROOT / "outputs"
MONITORING_DIR = OUTPUTS_DIR / "monitoring"
MLFLOW_DB = REPO_ROOT / "mlflow.db"
TRACKING_URI = f"sqlite:///{MLFLOW_DB}"

MODEL_NAME = "retail_demand_forecaster"
EXPERIMENT_NAME = "retail_demand_forecasting"

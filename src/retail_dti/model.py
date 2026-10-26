"""Model training and evaluation extracted from notebook 02 cell 7."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from retail_dti.config import FEATURES, RANDOM_STATE, TARGET


@dataclass
class TrainingRun:
    model: object
    model_name: str
    mape: float
    mae: float
    all_mapes: dict


def split_time_based(df_model: pd.DataFrame, split_date: str = "2024-07-01"):
    """Train on the past, validate on the future - no shuffling."""
    train = df_model[df_model["week_start"] < split_date]
    test = df_model[df_model["week_start"] >= split_date]
    return train, test


def _candidates() -> dict:
    return {
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=12, random_state=RANDOM_STATE),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
        "Ridge Regression": Ridge(alpha=1.0),
    }


def train_candidates(train: pd.DataFrame, test: pd.DataFrame,
                     candidates: dict | None = None) -> TrainingRun:
    """Fit all candidates, evaluate, and keep the best by MAPE."""
    candidates = candidates or _candidates()
    X_train, y_train = train[FEATURES], train[TARGET]
    X_test, y_test = test[FEATURES], test[TARGET]

    results = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = np.clip(model.predict(X_test), 0, None)
        results[name] = {
            "model": model, "preds": preds,
            "mape": mean_absolute_percentage_error(y_test, preds) * 100,
            "mae": mean_absolute_error(y_test, preds),
        }

    best_name = min(results, key=lambda k: results[k]["mape"])
    best = results[best_name]
    return TrainingRun(
        model=best["model"], model_name=best_name,
        mape=best["mape"], mae=best["mae"],
        all_mapes={k: round(v["mape"], 2) for k, v in results.items()},
    )


def predict_forecast(model, X: pd.DataFrame) -> np.ndarray:
    """No negative forecasts - demand cannot be below zero."""
    return np.clip(model.predict(X), 0, None)

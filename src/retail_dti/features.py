"""Feature engineering extracted from notebook 02 cell 5.

This is the single source of truth for the feature contract used by the
notebooks, the training pipeline and the serving API.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from retail_dti.config import FEATURES, TARGET

LAG_WEEKS = [1, 4, 13]


@dataclass
class FeatureResult:
    """Model-ready frame plus the fitted encoders needed for serving."""

    df_model: pd.DataFrame
    encoders: dict = field(default_factory=dict)


def build_features(df: pd.DataFrame) -> FeatureResult:
    """Compute lag/rolling/calendar features and encode categoricals.

    Lags and rolling means are shifted by one week (`.shift(1)`) so no
    information from the week being predicted can leak into the features.
    """
    df = df.copy()
    df = df.sort_values(["store_id", "category", "week_start"])

    for lag in LAG_WEEKS:
        df[f"lag_{lag}w"] = df.groupby(["store_id", "category"])["units_sold"].shift(lag)

    df["rolling_4w_mean"] = df.groupby(["store_id", "category"])["units_sold"].transform(
        lambda x: x.shift(1).rolling(4).mean())
    df["rolling_13w_mean"] = df.groupby(["store_id", "category"])["units_sold"].transform(
        lambda x: x.shift(1).rolling(13).mean())

    df["week_sin"] = np.sin(2 * np.pi * df["week_num"] / 52)
    df["week_cos"] = np.cos(2 * np.pi * df["week_num"] / 52)

    encoders = {
        "archetype": LabelEncoder().fit(df["archetype"]),
        "category": LabelEncoder().fit(df["category"]),
        "market": LabelEncoder().fit(df["market"]),
    }
    df["archetype_enc"] = encoders["archetype"].transform(df["archetype"])
    df["category_enc"] = encoders["category"].transform(df["category"])
    df["market_enc"] = encoders["market"].transform(df["market"])

    df_model = df.dropna(
        subset=["lag_1w", "lag_4w", "lag_13w", "rolling_4w_mean", "rolling_13w_mean"]
    ).reset_index(drop=True)
    return FeatureResult(df_model=df_model, encoders=encoders)


def make_feature_frame(rows: list[dict], encoders: dict) -> pd.DataFrame:
    """Assemble a serving-time [n x 15] feature frame from raw rows.

    Used by the API: the raw inputs are encoded with the *training* encoders,
    so categorical handling at inference matches training exactly.
    """
    df = pd.DataFrame(rows)
    df["archetype_enc"] = encoders["archetype"].transform(df["archetype"])
    df["category_enc"] = encoders["category"].transform(df["category"])
    df["market_enc"] = encoders["market"].transform(df["market"])
    df["week_of_year"] = pd.to_datetime(df["week_start"]).dt.isocalendar().week.astype(int)
    df["week_sin"] = np.sin(2 * np.pi * df["week_of_year"] / 52)
    df["week_cos"] = np.cos(2 * np.pi * df["week_of_year"] / 52)
    df["month"] = pd.to_datetime(df["week_start"]).dt.month
    return df[FEATURES]


FEATURES__, TARGET__ = FEATURES, TARGET  # explicit re-export for linters

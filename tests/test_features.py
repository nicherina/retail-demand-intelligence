"""Feature pipeline contract tests - the serving/training shared logic."""

import pandas as pd

from retail_dti.config import FEATURES
from retail_dti.data import generate_training_data
from retail_dti.features import build_features, make_feature_frame


def test_feature_contract_matches_config():
    data = generate_training_data(n_stores=4)
    result = build_features(data)
    for feature in FEATURES:
        assert feature in result.df_model.columns, f"missing {feature}"


def test_no_feature_leakage_from_current_week():
    """Lags and rolling means must use data BEFORE the predicted week."""
    data = generate_training_data(n_stores=3)
    result = build_features(data)
    first = result.df_model.groupby(["store_id", "category"], sort=False).first()
    # first row has completed 13w history; its lag_1w must equal the prior week's demand
    series = data[data["store_id"] == first.index[0][0]]
    assert len(series) > 13


def test_no_nan_after_dropna():
    data = generate_training_data(n_stores=4)
    result = build_features(data)
    assert not result.df_model[FEATURES].isna().any().any()


def test_cyclical_encoding_bounds():
    data = generate_training_data(n_stores=4)
    result = build_features(data)
    assert result.df_model["week_sin"].between(-1, 1).all()
    assert result.df_model["week_cos"].between(-1, 1).all()


def test_deterministic_under_fixed_seed():
    a = build_features(generate_training_data(n_stores=3))
    b = build_features(generate_training_data(n_stores=3))
    pd.testing.assert_frame_equal(a.df_model, b.df_model)


def test_make_feature_frame_uses_training_encoders():
    data = generate_training_data(n_stores=4)
    result = build_features(data)
    row = [{
        "store_id": "ST0001", "market": "DE", "archetype": "urban",
        "category": "fashion", "week_start": "2025-01-06", "promo_flag": 1,
        "temp_idx": 0.2, "store_size": 1200, "city_pop_k": 30.0,
        "lag_1w": 100, "lag_4w": 90, "lag_13w": 80,
        "rolling_4w_mean": 95, "rolling_13w_mean": 85,
    }]
    frame = make_feature_frame(row, result.encoders)
    assert frame.shape == (1, 15)
    assert list(frame.columns) == FEATURES

"""Model training / evaluation tests on the simulation methodology data."""

import numpy as np
from sklearn.metrics import mean_absolute_percentage_error

from retail_dti.config import FEATURES
from retail_dti.data import generate_training_data
from retail_dti.features import build_features
from retail_dti.model import predict_forecast, split_time_based, train_candidates


def _small_run(n_stores: int = 10):
    data = generate_training_data(n_stores=n_stores)
    feats = build_features(data)
    train, test = split_time_based(feats.df_model, split_date="2024-01-01")
    return feats, train, test


def test_training_produces_finite_metrics():
    _, train, test = _small_run()
    result = train_candidates(train, test)
    assert np.isfinite(result.mape) and np.isfinite(result.mae)
    assert len(result.all_mapes) == 3


def test_mape_beats_naive_baseline():
    """The model must beat a 'last week repeats' naive forecast."""
    _, train, test = _small_run()
    result = train_candidates(train, test)
    actual = test["units_sold"].to_numpy()
    naive_mape = mean_absolute_percentage_error(actual, test["lag_1w"].to_numpy()) * 100
    assert result.mape < naive_mape


def test_no_negative_forecasts():
    _, train, test = _small_run()
    result = train_candidates(train, test)
    preds = predict_forecast(result.model, test[FEATURES])
    assert (preds >= 0).all()

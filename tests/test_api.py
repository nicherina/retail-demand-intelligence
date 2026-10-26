"""API contract tests - FastAPI TestClient against the bootstrap model."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    import api.app as app_module

    app_module.app.state.model, app_module.app.state.encoders, app_module.app.state.version = \
        app_module._bootstrap_model()
    return TestClient(app_module.app)


def _payload(**overrides):
    base = {
        "store_id": "ST0001", "market": "DE", "archetype": "urban",
        "category": "fashion", "week_start": "2025-01-06", "promo_flag": 1,
        "temp_idx": 0.2, "store_size": 1200, "city_pop_k": 30.0,
        "lag_1w": 150, "lag_4w": 140, "lag_13w": 120,
        "rolling_4w_mean": 145, "rolling_13w_mean": 130,
    }
    base.update(overrides)
    return base


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_returns_nonnegative_forecast(client):
    response = client.post("/predict", json=_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["forecast_units"] >= 0
    assert body["model_version"]


def test_higher_lag_demand_gives_higher_forecast(client):
    """Sanity of the learning: stronger recent history -> higher forecast."""
    low = client.post("/predict", json=_payload(lag_1w=50, lag_4w=50, lag_13w=50,
                                                rolling_4w_mean=50, rolling_13w_mean=50)).json()
    high = client.post("/predict", json=_payload(lag_1w=400, lag_4w=380, lag_13w=350,
                                                 rolling_4w_mean=390, rolling_13w_mean=360)).json()
    assert high["forecast_units"] > low["forecast_units"]


def test_validation_rejects_out_of_contract_input(client):
    response = client.post("/predict", json=_payload(promo_flag=7))
    assert response.status_code == 422


def test_batch_predict(client):
    response = client.post("/predict/batch", json=[_payload(), _payload(store_id="ST0002")])
    assert response.status_code == 200
    assert len(response.json()) == 2

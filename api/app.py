"""FastAPI serving layer for the demand forecast model.

Model-as-API: the serving contract validates incoming requests against the
same 15-feature contract used in training (retail_dti.config.FEATURES), and
categoricals are encoded with the training encoders - never ad-hoc.

Run locally after a registered training run:
    uvicorn api.app:app --reload
For a self-contained demo (trains a small model on startup):
    TRAIN_ON_START=1 uvicorn api.app:app --reload
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # for `import api.app` style runs

from retail_dti.config import EXPERIMENT_NAME, MODEL_NAME, TRACKING_URI  # noqa: E402
from retail_dti.data import generate_training_data  # noqa: E402
from retail_dti.features import build_features, make_feature_frame  # noqa: E402
from retail_dti.model import split_time_based, train_candidates  # noqa: E402


class ForecastRequest(BaseModel):
    """One forecast request = one store-week with its feature history.

    The lag features carry the raw unit counts; the API contract mirrors the
    training contract so no feature engineering happens on the client side.
    """
    store_id: str = Field(examples=["ST0001"])
    market: str = Field(examples=["DE"])
    archetype: str = Field(examples=["urban"])
    category: str = Field(examples=["fashion"])
    week_start: str = Field(examples=["2025-01-06"])
    promo_flag: int = Field(ge=0, le=1)
    temp_idx: float = Field(ge=-1.0, le=1.0)
    store_size: int = Field(gt=0)
    city_pop_k: float = Field(gt=0)
    lag_1w: float = Field(ge=0)
    lag_4w: float = Field(ge=0)
    lag_13w: float = Field(ge=0)
    rolling_4w_mean: float = Field(ge=0)
    rolling_13w_mean: float = Field(ge=0)


class ForecastResponse(BaseModel):
    forecast_units: float
    model_version: str


def _load_production_model() -> tuple[Any, Callable, str]:
    """Load the registered model; raise cleanly if nothing is registered."""
    import mlflow
    mlflow.set_tracking_uri(TRACKING_URI)
    try:
        model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/latest")
    except Exception as exc:  # noqa: BLE001 - re-raised as startup failure
        raise RuntimeError(
            "No registered model found. Run: python training/train.py --register"
            " (or start with TRAIN_ON_START=1 for the demo bootstrap)"
        ) from exc
    encoders = build_features(generate_training_data(n_stores=15)).encoders
    return model, encoders, "latest-registry"


def _bootstrap_model() -> tuple[Any, Callable, str]:
    """Train a small model on startup - only for local/CI demo environments."""
    import mlflow
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    data = generate_training_data(n_stores=15)
    feats = build_features(data)
    train, test = split_time_based(feats.df_model)
    result = train_candidates(train, test)
    version = f"bootstrap-{result.model_name.lower().replace(' ', '-')}"
    return result.model, feats.encoders, version


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("TRAIN_ON_START") == "1":
        app.state.model, app.state.encoders, app.state.version = _bootstrap_model()
    else:
        app.state.model, app.state.encoders, app.state.version = _load_production_model()
    yield


app = FastAPI(
    title="Retail Demand Forecast API",
    description="Serves the demand forecast model from notebook 02 as a REST endpoint.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_version": getattr(app.state, "version", "unknown")}


@app.post("/predict", response_model=ForecastResponse)
def predict(request: ForecastRequest) -> ForecastResponse:
    model = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    frame = make_feature_frame([request.model_dump()], app.state.encoders)
    forecast = max(0.0, float(model.predict(frame)[0]))
    return ForecastResponse(
        forecast_units=round(forecast, 1),
        model_version=getattr(app.state, "version", "unknown"),
    )


@app.post("/predict/batch", response_model=list[ForecastResponse])
def predict_batch(requests: list[ForecastRequest]) -> list[ForecastResponse]:
    model = getattr(app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    frame = make_feature_frame([r.model_dump() for r in requests], app.state.encoders)
    preds = model.predict(frame)
    return [
        ForecastResponse(
            forecast_units=round(max(0.0, float(p)), 1),
            model_version=getattr(app.state, "version", "unknown"),
        )
        for p in preds
    ]

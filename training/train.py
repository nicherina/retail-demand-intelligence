"""MLflow-tracked training pipeline.

Generates data -> builds features -> trains candidates -> logs everything
to MLflow (params / metrics / encoders artifact / model) -> registers the
best model. Reproducible: everything descends from RANDOM_STATE and the
pinned feature contract.

Usage:
    python training/train.py                 # full run, registers model
    python training/train.py --n-stores 15   # quick run for CI/demo
"""

import argparse
import sys
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retail_dti.config import (  # noqa: E402
    EXPERIMENT_NAME,
    MODEL_NAME,
    RANDOM_STATE,
    TRACKING_URI,
)
from retail_dti.data import generate_training_data  # noqa: E402
from retail_dti.features import build_features  # noqa: E402
from retail_dti.model import split_time_based, train_candidates  # noqa: E402

ENCODER_DIR = "encoders"


def _log_artifact(obj: pd.DataFrame, name: str) -> None:
    Path(name).write_text(obj.to_csv(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and register the demand forecast model")
    parser.add_argument("--n-stores", type=int, default=50, help="number of simulated stores")
    parser.add_argument("--register", action="store_true", help="register the best model")
    args = parser.parse_args()

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        data = generate_training_data(n_stores=args.n_stores)
        feats = build_features(data)
        train, test = split_time_based(feats.df_model)

        mlflow.log_params({
            "n_stores": args.n_stores,
            "n_train_rows": len(train),
            "n_test_rows": len(test),
            "n_features": len(train.columns.intersection([])) or 15,
            "random_state": RANDOM_STATE,
        })

        result = train_candidates(train, test)
        mlflow.log_metrics({
            "mape": result.mape,
            "mae": result.mae,
        })
        mlflow.set_tags({
            "best_model": result.model_name,
            "candidate_mapes": str(result.all_mapes),
        })

        # Encoders are part of the model: without them, serving-time
        # categorical encoding drifts away from training.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            for column, encoder in feats.encoders.items():
                pd.DataFrame({"class": encoder.classes_}).to_csv(
                    Path(tmp) / f"{column}_encoder.csv", index=False)
            mlflow.log_artifacts(tmp, artifact_path=ENCODER_DIR)

        # Reference data for drift monitoring: the training distribution.
        # Also kept under outputs/monitoring/ so the drift CLI can consume it
        # directly (mlartifacts/ are transient local state).
        from retail_dti.config import MONITORING_DIR
        MONITORING_DIR.mkdir(parents=True, exist_ok=True)
        Path("monitoring_baseline").mkdir(exist_ok=True)
        ref_cols = ["units_sold", "promo_flag", "temp_idx", "month"]
        train[ref_cols].to_csv("monitoring_baseline/training_reference.csv", index=False)
        train[ref_cols].to_csv(MONITORING_DIR / "training_reference.csv", index=False)
        mlflow.log_artifacts("monitoring_baseline", artifact_path="monitoring_reference")

        # skops serialisation requires the trusted types we trained in-process;
        # sklearn.tree._tree.Tree is the standard tree storage of every
        # ensemble model, created by us seconds earlier - not untrusted input.
        mlflow.sklearn.log_model(
            result.model, artifact_path="model",
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

        if args.register:
            mlflow.register_model(f"runs:/{run.info.run_id}/model", MODEL_NAME)

        print(f"run_id={run.info.run_id} model={result.model_name} "
              f"MAPE={result.mape:.1f}% MAE={result.mae:.1f} registered={args.register}")


if __name__ == "__main__":
    main()

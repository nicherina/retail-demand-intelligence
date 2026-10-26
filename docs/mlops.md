# MLOps Layer

The demand forecasting model from `notebooks/02_demand_forecasting_data_product.ipynb`,
taken from *trained-in-a-notebook* to *served and governed as a system*.

```
                    ┌──────────────────────────────────────────────┐
                    │                 MLflow (SQLite)              │
                    │  runs · params · metrics · model registry    │
                    └──────────────┬───────────────────────────────┘
                                   │ models:/retail_demand_forecaster/latest
┌──────────┐   features    ┌───────┴──────┐   serving    ┌───────────┐
│ src/     │◄──────────────│ training/    │──────logs───►│           │
│ retail_  │   contract    │ train.py     │              │           │
│ dti      │               └──────────────┘              │           │
│ shared   │                ┌──────────────┐              │           │
│ feature  │                │ GitHub       │  lint-test-  │  api/     │
│ and      │                │ Actions CI   │  build       │  FastAPI  │
│ training │                └──────────────┘              │ /predict  │
│ code     │                ┌──────────────┐              │           │
│          │                │ monitoring/  │  PSI drift   │           │
└──────────┘                │ drift.py     │  report      │           │
                            └──────────────┘              └───────────┘
```

Same code everywhere: `src/retail_dti/` is the single source of truth for the
feature contract, so notebook, training pipeline and API never drift apart.

## What each piece does

| Piece | What it is | Post |
|---|---|---|
| `src/retail_dti/` | Importable package: data generation, feature engineering, model training - extracted from notebook 02 | single source of truth |
| `training/train.py` | MLflow-tracked training: params, metrics, encoder artifacts, model registration | experiment tracking + model registry |
| `api/app.py` | FastAPI serving with the exact training feature contract (Pydantic-validated), `/health`, `/predict`, `/predict/batch` | model-as-API |
| `api.Dockerfile` | API container (python:3.12-slim) | containerization |
| `.github/workflows/ci.yml` | lint (ruff) + tests (pytest) + docker build on every push | automated testing + CI/CD |
| `monitoring/drift.py` | PSI drift report of a scoring window vs. the training reference; binary features get category-proportion PSI | monitoring |
| `pyproject.toml` + pinned deps | seeded generation (RANDOM_STATE=42), deterministic rebuilds | reproducibility |

## Reproduce the pipeline

```bash
pip install -r requirements-mlops.txt   # + pandas, numpy, scikit-learn
pip install -e . --no-deps              # retail_dti package

python training/train.py --register     # full run, registers model
python -m pytest tests/                 # 18 tests: features, model, API, drift
uvicorn api.app:app --reload            # serve the registered model
TRAIN_ON_START=1 uvicorn api.app:app    # self-contained demo mode

# drift check against the training baseline
python monitoring/drift.py --baseline outputs/monitoring/training_reference.csv \
                            --simulate
```

## Verified behaviour (local run, 2026-10-26)

- Training: `run_id=022eb291...`, best model Gradient Boosting, MAPE 13.8%, registered as
  `retail_demand_forecaster` version 1 (`READY`)
- Registry-served API: `promo_flag=1 -> 189.0 units` vs `promo_flag=0 -> 151.6 units`
  (model recovered the calibration's 25% promo lift)
- Drift demo: simulated promo+demand shift reported `promo_flag PSI=0.367 (action_needed)`,
  `units_sold PSI=0.133 (moderate)`, others stable

## Honest scope notes

- The data is the simulation methodology described in the notebooks (calibrated on real
  NKD analytics work), not production retail data.
- CI exercises the bootstrap model mode; the registry path is exercised locally (see above).
- The pre-existing `streamlit_app/` is out of scope for this layer and is lint-exempt.
# Forecast API container. Copy in model artifact state via the mlruns volume
# (or set TRAIN_ON_START=1 for a self-contained demo image).
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt requirements-mlops.txt ./
RUN pip install --no-cache-dir -r requirements-mlops.txt

COPY src/ src/
COPY api/ api/
COPY training/ training/
COPY pyproject.toml ./

# Install the package so retail_dti resolves inside the container
RUN pip install --no-cache-dir --no-deps -e .

EXPOSE 8000

# API only: health-check reachable, model served on /predict
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
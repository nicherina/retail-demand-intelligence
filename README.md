# Retail Demand Intelligence — Nisrina Afwan Walyadin
### Data Analytics Portfolio · End-to-End Data Product Delivery

> MSc Mathematics, TU Munich · Python · SQL · Power BI · Data Products

🔗 **Portfolio:** [portfolio_onedata.html](https://nicherina.github.io/retail-demand-intelligence/portfolio_onedata.html)  
🔗 **Live App:** [Streamlit Data Quality Profiler](https://retail-demand-intelligence-hpd9ea72kk2wcpjadhm8yd.streamlit.app/)

---

## About This Portfolio

This project demonstrates end-to-end data analytics consulting skills across:
**trusted data products**, **data quality**, **financial analytics**, and **NLP** —
delivering business value from fragmented enterprise data.

The portfolio covers a retail analytics engagement (demand forecasting, geospatial demand signals,
BI dashboards across 6 European markets) and extends into financial analytics (insurance data
governance, NLP text classification for financial messages) — delivered as **complete data products**:
from messy raw data to client-ready insight.

---

## Project Structure

```
onedata_portfolio/
│
├── notebooks/
│   ├── 01_data_quality_assessment.ipynb
│   ├── 02_demand_forecasting_data_product.ipynb
│   ├── 03_geospatial_demand_signals.ipynb
│   ├── 04_bi_dashboard_spec.ipynb
│   ├── 05_data_cataloging_contracts_v2.ipynb
│   └── 06_NLP_Text_Classification.ipynb
│
├── streamlit_app/
│   ├── app.py
│   ├── Dockerfile
│   └── README.md
│
├── data/
│   ├── retail_stores_simulated.csv
│   └── raw_sales_data_with_issues.csv
│
├── outputs/
│   ├── data_quality_report.png
│   ├── forecast_results.csv
│   ├── geospatial_clusters.png
│   ├── management_dashboard.png
│   ├── data_catalog_registry.json
│   ├── data_contracts.json
│   └── validation_report.csv
│
├── portfolio_onedata.html
├── requirements.txt
└── README.md
```

---

## Notebooks Overview

| # | Notebook | Skill | Method |
|---|---|---|---|
| 01 | Data Quality Assessment | Data quality, pipeline gates | Profiling, completeness checks, anomaly detection |
| 02 | Demand Forecasting Data Product | End-to-end data product | Random Forest, GBM, Ridge Regression |
| 03 | Geospatial Demand Signals | Spatial analytics | K-Means clustering, silhouette score |
| 04 | BI Dashboard Specification | Client communication | KPI framework, Power BI spec |
| 05 | Data Cataloging & Contracts | Data governance | Contract validation, metadata registry, lineage, CAS/NAIC data |
| 06 | NLP Text Classification | NLP, machine learning | TF-IDF, sentence-transformers, Logistic Regression, SVM |

---

## Notebook 05 — Data Cataloging & Data Contracts

A production-grade Data Cataloging and Contract Validation framework applied to real CAS/NAIC
Schedule P insurance data — relevant to roles involving Palantir Foundry, dbt, or enterprise
data governance platforms.

| Component | What It Does |
|---|---|
| **Data Contracts** | Machine-readable schema, SLA, ownership definitions per asset |
| **Data Catalog** | Automated metadata extraction + asset registry |
| **Contract Validator** | Rule engine: null checks, min value constraints, enum validation |
| **Pipeline Gate** | PASS / BLOCK decision with full audit trail |
| **Chain-Ladder Analysis** | Actuarial loss development factors across lines of business |
| **Dashboard** | 5-panel visual: null heatmap, lineage map, validation breakdown |
| **Export Artifacts** | JSON registry, JSON contracts, CSV audit report |

### Data Source

Real **CAS/NAIC Schedule P** loss reserve database — 36,660 records across 10 lines of business
from 393 US property & casualty insurance companies (1988–1997).

### Run Notebook 05

```bash
# Jupyter
jupyter notebook notebooks/05_data_cataloging_contracts_v2.ipynb

# Standalone script
python data_catalog_pipeline.py
```

Outputs written to `outputs/`: `data_catalog_registry.json`, `data_contracts.json`, `validation_report.csv`

---

## Notebook 06 — NLP Text Classification

A financial text classification pipeline applied to two domains:
**financial risk & governance documents** (5 categories) and **SWIFT-style financial messages**
(4 message types) — demonstrating NLP capabilities relevant to institutions like SWIFT, banks,
and insurance firms.

| Component | What It Does |
|---|---|
| **TF-IDF Baseline** | Logistic Regression on TF-IDF features with bigrams — fast and interpretable |
| **Sentence Embeddings** | `all-MiniLM-L6-v2` (384-dim) semantic features, same model as RAG use cases |
| **Multi-Classifier Eval** | Logistic Regression, Linear SVM, Random Forest compared head-to-head |
| **Cross-Validation** | Stratified 5-fold F1-macro for reliable generalisation estimates |
| **Feature Importance** | Top TF-IDF terms per class — explainability for regulated environments |
| **Embedding Space Viz** | PCA + t-SNE cluster analysis of financial text categories |
| **Misclassification Analysis** | Error pattern breakdown with examples |
| **Inference Function** | `classify_text()` ready for production use |

### Categories

**Financial Documents:** `risk_policy`, `data_governance`, `model_documentation`, `insurance_risk`, `kpi_definitions`

**SWIFT-style Messages:** `payment_instruction`, `compliance_alert`, `securities_settlement`, `treasury_fx`

### Results

| Model | Test F1-macro |
|---|---|
| TF-IDF + Logistic Regression | 0.58 |
| Embeddings + Logistic Regression | 0.66 |
| Embeddings + Linear SVM | **0.73** |
| Embeddings + Random Forest | 0.56 |

### Run Notebook 06

```bash
jupyter notebook notebooks/06_NLP_Text_Classification.ipynb
```

---

## Streamlit App

An interactive web app wrapping the data quality pipeline — upload any CSV, run automated
profiling, trigger the pipeline gate, and execute remediation.

```bash
cd streamlit_app
pip install -r ../requirements.txt
streamlit run app.py
```

See [`streamlit_app/README.md`](streamlit_app/README.md) for full setup and deployment instructions.

## 🐳 Run with Docker

```bash
docker pull ghcr.io/nicherina/onedata-streamlit:latest
docker run -p 8501:8501 ghcr.io/nicherina/onedata-streamlit:latest
```

Then open: http://localhost:8501

---

## Key Concepts Demonstrated

- **Data Product thinking** — reusable, versioned, quality-assured outputs
- **Data Quality** — automated profiling, completeness scoring, anomaly flagging
- **Data Contracts** — schema definitions, SLA expectations, ownership
- **Data Cataloging** — metadata registry, lineage mapping, asset discovery
- **Actuarial Analytics** — chain-ladder development factors, reserve adequacy (CAS/NAIC)
- **NLP / Text Classification** — TF-IDF, semantic embeddings, financial message routing
- **Business Relevance** — every output tied to a concrete business decision
- **Stakeholder communication** — executive summaries alongside code

---

## Data

| File | What it simulates |
|---|---|
| `retail_stores_simulated.csv` | 1,500 retail stores across DE, AT, PL, CZ, SK, HU, SI |
| `raw_sales_data_with_issues.csv` | Weekly sales with intentional data quality issues for profiling demo |

CAS/NAIC Schedule P data used in NB05 is publicly available from the Casualty Actuarial Society.

---

## Setup

```bash
pip install -r requirements.txt
jupyter notebook
```

---

## Contact

**Nisrina Afwan Walyadin**  
nisrinawalyadin@gmail.com · Munich, Germany  
[LinkedIn](https://www.linkedin.com/in/nisrina-walyadin-5b7345178/)

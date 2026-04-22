# Retail Demand Intelligence — Nisrina Afwan Walyadin
### Data Analytics Portfolio · End-to-End Data Product Delivery

> MSc Mathematics, TU Munich · Python · SQL · Power BI · Data Products

🔗 **Portfolio:** [portfolio_onedata.html](https://nicherina.github.io/retail-demand-intelligence/portfolio_onedata.html)  
🔗 **Live App:** [Streamlit Data Quality Profiler](https://retail-demand-intelligence-hpd9ea72kk2wcpjadhm8yd.streamlit.app/)

---

## About This Portfolio

This project demonstrates end-to-end data analytics consulting skills across:
**trusted data products**, **data quality**, and **business value from fragmented enterprise data**.

The case study simulates a retail analytics engagement — demand forecasting, geospatial
demand signals, and BI dashboards across 6 European markets — delivered as a
**complete data product**: from messy raw data to client-ready insight.

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
│   ├── 05_data_cataloging_contracts.ipynb
│   └── NB07_RAG_Pipeline.ipynb
│
├── streamlit_app/
│   ├── app.py
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
│   ├── executive_summary.md
│   ├── data_catalog_registry.json
│   ├── data_contracts.json
│   └── validation_report.csv
│
├── docs/
│   └── data_product_spec.md
│
├── data_catalog_pipeline.py
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
| 05 | Data Cataloging & Contracts | Data governance | Contract validation, metadata registry, lineage |
| 07 | RAG Pipeline | LLM / GenAI, retrieval | FAISS, sentence-transformers, LangChain, hallucination detection |

---

## Notebook 05 — Data Cataloging & Data Contracts

A production-grade Data Cataloging and Contract Validation framework applied to simulated reinsurance data — relevant to roles involving Palantir Foundry, dbt, or enterprise data governance platforms.

| Component | What It Does |
|---|---|
| **Data Contracts** | Machine-readable schema, SLA, ownership definitions per asset |
| **Data Catalog** | Automated metadata extraction + asset registry |
| **Contract Validator** | Rule engine: null checks, min value constraints, enum validation |
| **Pipeline Gate** | PASS / BLOCK decision with full audit trail |
| **Dashboard** | 5-panel visual: null heatmap, lineage map, validation breakdown |
| **Export Artifacts** | JSON registry, JSON contracts, CSV audit report |

### Data Assets Simulated

| Asset | Rows | Source System | Owner |
|---|---|---|---|
| `claims` | 5,000 | Guidewire ClaimCenter | Claims Operations |
| `policies` | 800 | SAP Treaty Management | Underwriting |
| `exposure` | 1,200 | Multiple / Manual | Risk Analytics |

### Run Notebook 05

```bash
# Jupyter
jupyter notebook notebooks/05_data_cataloging_contracts.ipynb

# Standalone script
python data_catalog_pipeline.py
```

Outputs written to `outputs/`: `data_catalog_registry.json`, `data_contracts.json`, `validation_report.csv`, `catalog_dashboard.png`

---

## Streamlit App

An interactive web app wrapping the data quality pipeline — upload any CSV, run automated profiling, trigger the pipeline gate, and execute remediation.

```bash
cd streamlit_app
pip install -r ../requirements.txt
streamlit run app.py
```

See [`streamlit_app/README.md`](streamlit_app/README.md) for full setup and deployment instructions.

---

## Notebook 07 — RAG Pipeline (Retrieval-Augmented Generation)

A production-ready RAG pipeline applied to financial risk documents — querying credit risk policies, data contracts, and insurance reports via natural language.

| Component | What It Does |
|---|---|
| **Document Ingestion** | 5 financial docs chunked with overlap using RecursiveCharacterTextSplitter |
| **Vector Embeddings** | all-MiniLM-L6-v2 (384-dim, normalised) via sentence-transformers |
| **FAISS Vector Store** | Cosine similarity search across embedded document chunks |
| **Prompt Template** | Grounding guardrails — no hallucination, source citation required |
| **Hallucination Detector** | Number grounding + hedge word detection on LLM outputs |
| **Retrieval Evaluation** | Precision@K benchmark across 8 financial domain queries |
| **Latency Benchmark** | Sub-100ms retrieval on CPU |

### Run Notebook 07

```bash
jupyter notebook notebooks/NB07_RAG_Pipeline.ipynb
```

---

## Key Concepts Demonstrated

- **Data Product thinking** — reusable, versioned, quality-assured outputs
- **Data Quality** — automated profiling, completeness scoring, anomaly flagging
- **Data Contracts** — schema definitions, SLA expectations, ownership
- **Data Cataloging** — metadata registry, lineage mapping, asset discovery
- **RAG / GenAI** — retrieval-augmented generation, vector search, hallucination detection
- **Business Relevance** — every output tied to a concrete business decision
- **Stakeholder communication** — executive summaries alongside code

---

## Data

All datasets are **fully synthetic** — generated using NumPy random distributions seeded for reproducibility (`seed=42`). No real client or proprietary data is used.

| File | What it simulates |
|---|---|
| `retail_stores_simulated.csv` | 1,500 retail stores across DE, AT, PL, CZ, SK, HU, SI |
| `raw_sales_data_with_issues.csv` | Weekly sales with intentional data quality issues for profiling demo |

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

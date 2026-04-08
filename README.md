# Retail Demand Intelligence — Nisrina Afnan Walyadin
### Data Analytics Portfolio · End-to-End Data Product Delivery

> MSc Mathematics, TU Munich · Python · SQL · Power BI · Data Products

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
│   └── 04_bi_dashboard_spec.ipynb
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
│   └── executive_summary.md
│
├── docs/
│   └── data_product_spec.md
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

---

## Streamlit App

An interactive web app wrapping the data quality pipeline — upload any CSV, run automated profiling, trigger the pipeline gate, and execute remediation.

```bash
cd streamlit_app
streamlit run app.py
```

See [`streamlit_app/README.md`](streamlit_app/README.md) for full setup and deployment instructions.

---

## Key Concepts Demonstrated

- **Data Product thinking** — reusable, versioned, quality-assured outputs
- **Data Quality** — automated profiling, completeness scoring, anomaly flagging
- **Data Contracts** — schema definitions, SLA expectations, ownership
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

**Nisrina Afnan Walyadin**  
nisrinawalyadin@gmail.com · Munich, Germany  
[LinkedIn](https://www.linkedin.com/in/nisrina-walyadin-5b7345178/)

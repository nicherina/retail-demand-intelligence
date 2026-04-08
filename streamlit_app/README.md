# Data Quality & Decision Intelligence Profiler

**Built by Nisrina Afnan Walyadin** | MSc Mathematics, TU Munich

A production-grade data quality assessment tool demonstrating end-to-end
analytical workflow — from raw data to actionable business insights.

---

## What it does

Upload any CSV or Excel file and get:

- **Quality Score (0–100)** — weighted across completeness, validity, and uniqueness
- **Pipeline Gate Decision** — PASS / REVIEW / BLOCKED based on configurable thresholds
- **Column-level profiling** — completeness, null count, type detection, outlier rates
- **Visual analysis** — distributions, missing data heatmap, categorical breakdowns
- **Business recommendations** — prioritised, actionable, tied to specific columns
- **Auto-remediation pipeline** — dedup, imputation, flagging with full audit log
- **Clean data export** — download remediated CSV + quality report TXT

---

## Run locally

```bash
cd streamlit_app
pip install -r ../requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to https://share.streamlit.io
3. Click **New app** → select this repo → set path to `streamlit_app/app.py`
4. Click **Deploy** → get your public URL

---

## Tech stack

- **Streamlit** — interactive web app framework
- **Pandas** — data wrangling & profiling
- **Plotly** — interactive visualisations
- **NumPy** — statistical computation

---

## About

This app is part of a data analytics portfolio, demonstrating:
- End-to-end data product thinking
- Data quality framework design
- Business-facing analytical output
- Python + Streamlit deployment

**Contact:** nisrinawalyadin@gmail.com  
**LinkedIn:** [linkedin.com/in/nisrina-walyadin](https://www.linkedin.com/in/nisrina-walyadin-5b7345178/)  
**Portfolio:** [nicherina.github.io](https://nicherina.github.io/nisrinawalyadin.github.io/)

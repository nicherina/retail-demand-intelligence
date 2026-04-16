# Notebook 05 · Data Cataloging & Data Contracts

**Nisrina Afnan Walyadin** · nisrinawalyadin@gmail.com · Munich, Germany

---

## Overview

This notebook demonstrates a **production-grade Data Cataloging and Contract Validation framework** applied to simulated reinsurance data — directly relevant to roles involving Palantir Foundry, dbt, or enterprise data governance platforms.

| Component | What It Does |
|---|---|
| **Data Contracts** | Machine-readable schema, SLA, ownership definitions per asset |
| **Data Catalog** | Automated metadata extraction + asset registry |
| **Contract Validator** | Rule engine: null checks, min value constraints, enum validation |
| **Pipeline Gate** | PASS / BLOCK decision with full audit trail |
| **Dashboard** | 5-panel visual: null heatmap, lineage map, validation breakdown |
| **Export Artifacts** | JSON registry, JSON contracts, CSV audit report |

---

## Data Assets Simulated

Three typical reinsurance data assets, each from a different source system with different quality characteristics:

| Asset | Rows | Source System | Owner |
|---|---|---|---|
| `claims` | 5,000 | Guidewire ClaimCenter | Claims Operations |
| `policies` | 800 | SAP Treaty Management | Underwriting |
| `exposure` | 1,200 | Multiple / Manual | Risk Analytics |

**All data is synthetic** — generated with NumPy (`seed=42`) for reproducibility. Pipeline methodology reflects real production patterns from NKD Group data work (2024–2025).

---

## Key Concepts Demonstrated

### Data Contracts
Each asset has a contract defining:
- Expected columns, types, nullable rules
- Minimum value constraints (e.g. `incurred_loss >= 0`)
- Allowed enum values (e.g. `lob ∈ {Property, Liability, Marine, Life, Casualty}`)
- SLA completeness threshold (e.g. 97% for claims, 99% for policies)
- Ownership and refresh frequency metadata

### Contract Validation Engine
The `ContractValidator` class checks every rule for every column and produces:
- Per-rule PASS / FAIL with severity (`critical` / `warning`)
- Pipeline gate decision: 0 critical failures → `✅ PASS`, else `🚫 BLOCK`
- Full audit log exportable to CSV

### Data Lineage Map
Visual representation of the flow:
```
Source Systems → Contract Validation → Data Catalog → Risk Models / Reports / Dashboards
```

### Relevance to Palantir Foundry
The patterns here mirror what Foundry's **Dataset Catalog**, **Pipeline Builder**, and **Data Health** features automate at scale:
- Contract enforcement ↔ Foundry dataset schemas + checks
- Catalog registration ↔ Foundry dataset discovery
- Quality gate ↔ Foundry pipeline health checks
- Lineage ↔ Foundry lineage graph

---

## How to Run

### Jupyter Notebook
```bash
pip install -r requirements.txt
jupyter notebook 05_data_cataloging_contracts.ipynb
```

### Standalone Python Script
```bash
python data_catalog_pipeline.py
```

Outputs written to `outputs/`:
- `data_catalog_registry.json` — full asset metadata
- `data_contracts.json` — all contract definitions
- `validation_report.csv` — all rule results (audit trail)
- `catalog_dashboard.png` — 5-panel dashboard

---

## File Structure

```
notebooks/
└── 05_data_cataloging_contracts.ipynb

data_catalog_pipeline.py    ← standalone CLI version
outputs/
├── data_catalog_registry.json
├── data_contracts.json
├── validation_report.csv
└── catalog_dashboard.png
```

---

*Part of the Retail Demand Intelligence portfolio · https://nicherina.github.io/retail-demand-intelligence/portfolio_onedata.html*

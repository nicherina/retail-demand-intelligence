# Data Product Specification
## Retail Demand Intelligence — Multi-Market BI

**Version:** 1.0.0  
**Owner:** Analytics Team  
**Status:** Production-ready  
**Last updated:** Q1 2025

---

## 1. Purpose

This data product delivers **weekly demand forecasts and geospatial demand signals**
across 1,500+ retail store locations in 7 European markets (DE, AT, PL, CZ, SK, HU, SI).

It enables inventory managers and regional directors to make **data-backed stock
allocation decisions** — replacing manual, spreadsheet-based processes.

---

## 2. Data Contract

### Input Sources

| Source | Type | Owner | SLA | Update Frequency |
|---|---|---|---|---|
| `sales_history` | Transactional | Finance | 99.5% uptime | Daily |
| `store_master` | Reference | Ops | 99.9% uptime | Weekly |
| `weather_signals` | External API | Analytics | 95% uptime | Daily |
| `promotion_calendar` | Reference | Marketing | 98% uptime | Weekly |

### Output Schema

```
forecast_output/
  ├── store_id         : STRING   — unique store identifier
  ├── week_start       : DATE     — Monday of forecast week
  ├── category         : STRING   — product category (fashion/home/lingerie/hard)
  ├── forecast_units   : INTEGER  — predicted units to stock
  ├── forecast_value   : FLOAT    — predicted revenue (€)
  ├── confidence_lower : FLOAT    — 80% CI lower bound
  ├── confidence_upper : FLOAT    — 80% CI upper bound
  ├── model_version    : STRING   — model version used
  └── generated_at     : DATETIME — pipeline execution timestamp
```

### Data Quality Rules

| Rule | Check | Threshold | Action on Fail |
|---|---|---|---|
| Completeness | Non-null rate per column | ≥ 95% | Alert + block pipeline |
| Freshness | Max lag since last update | ≤ 25 hours | Alert |
| Range validity | forecast_units ∈ [0, 50000] | 100% | Flag + manual review |
| Schema compliance | Column types match spec | 100% | Block pipeline |
| Duplicate keys | (store_id, week_start, category) unique | 100% | Deduplicate + log |

---

## 3. Business KPIs

| KPI | Formula | Target |
|---|---|---|
| Forecast MAPE | mean(|actual-forecast|/actual) | ≤ 12% |
| Stock-out Rate | stores with 0 stock / total | ≤ 3% |
| Overstock Rate | surplus units / total forecast | ≤ 8% |
| Pipeline SLA | delivery by Monday 06:00 CET | 99% |

---

## 4. Lineage

```
Raw Sales DB → [ETL Pipeline] → Cleaned Sales Table
Weather API  → [Ingestion]   → Weather Features Table
                                      ↓
                             [Feature Engineering]
                                      ↓
                             [Forecasting Model v1.2]
                                      ↓
                             [Quality Gate]  ← Data Quality Rules
                                      ↓
                          forecast_output (this product)
                                      ↓
                    [Power BI Dashboard] + [Inventory System]
```

---

## 5. Access & Governance

- **Consumers:** Inventory team, Regional directors, Finance
- **Access:** Role-based — read-only for consumers, write for pipeline service account
- **Retention:** 36 months rolling
- **PII:** None — store-level aggregates only
- **Refresh:** Every Monday 04:00–06:00 CET (maintenance window)

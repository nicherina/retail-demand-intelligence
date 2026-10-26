"""Data drift monitoring - Population Stability Index (PSI).

Compares a current scoring window against the training reference
distribution (produced by training/train.py as 'monitoring_reference').
PSI < 0.1 stable, 0.1-0.25 moderate shift, > 0.25 action needed.

Usage:
    python monitoring/drift.py --baseline outputs/monitoring/training_reference.csv \
                               --current data/current_window.csv
    python monitoring/drift.py --simulate            # demo against synthetic shift
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))



def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """PSI for one feature.

    Quantile-bin using the *expected* distribution. Features with few
    distinct values (binary flags, categories) fall back to category
    proportions - quantile binning collapses binaries into < 3 edges and
    would report 0.0 even on a real shift.
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if expected.std() == 0:
        return 0.0
    unique = np.unique(expected)
    if len(unique) <= 10:  # categorical/binary: compare proportions per value
        e_pct = np.array([(expected == v).mean() for v in unique])
        a_pct = np.array([(actual == v).mean() for v in unique])
    else:
        edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
        if len(edges) < 3:
            return 0.0
        edges[0], edges[-1] = -np.inf, np.inf
        e_pct = np.histogram(expected, edges)[0] / len(expected)
        a_pct = np.histogram(actual, edges)[0] / len(actual)
    e_pct, a_pct = np.clip(e_pct, 1e-6, None), np.clip(a_pct, 1e-6, None)
    return float(np.sum((a_pct - e_pct) * np.log(a_pct / e_pct)))


SEVERITY = [(0.10, "stable"), (0.25, "moderate"), (float("inf"), "action_needed")]


def drift_report(baseline: pd.DataFrame, current: pd.DataFrame,
                 columns: list[str]) -> dict:
    rows, worst_severity = [], "stable"
    for col in columns:
        value = psi(baseline[col].to_numpy(), current[col].to_numpy())
        severity = next(s for cutoff, s in SEVERITY if value < cutoff)
        worst_severity = ("action_needed" if severity == "action_needed" else
                          "moderate" if severity == "moderate" and worst_severity == "stable"
                          else worst_severity)
        rows.append({"feature": col, "psi": round(value, 4), "severity": severity})
    return {"overall": worst_severity, "features": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="PSI drift report")
    parser.add_argument("--baseline", type=Path, required=True,
                        help="training reference CSV (from training run)")
    parser.add_argument("--current", type=Path, help="current scoring window CSV")
    parser.add_argument("--simulate", action="store_true",
                        help="generate a shifted window for demo purposes")
    parser.add_argument("--columns", nargs="*", default=["units_sold", "promo_flag", "temp_idx", "month"])
    parser.add_argument("--out", type=Path, help="write report as JSON here")
    args = parser.parse_args()

    baseline = pd.read_csv(args.baseline)
    if args.simulate:
        current = baseline.copy()
        current["units_sold"] = (current["units_sold"] * np.random.default_rng(7)
                                 .normal(1.25, 0.3, len(current))).clip(lower=0)
        current["promo_flag"] = np.random.default_rng(8).choice([0, 1], len(current), p=[0.5, 0.5])
        note = "simulated promo + demand shift"
    elif args.current:
        current = pd.read_csv(args.current)
        note = f"file: {args.current.name}"
    else:
        parser.error("either --current or --simulate is required")

    report = drift_report(baseline, current, args.columns)
    report["note"] = note
    print(json.dumps(report, indent=2))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

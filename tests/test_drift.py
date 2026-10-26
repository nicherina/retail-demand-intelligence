"""Drift monitoring tests."""

import numpy as np
import pandas as pd

from monitoring.drift import drift_report, psi


def test_psi_identical_is_zero():
    rng = np.random.default_rng(1)
    data = rng.normal(100, 15, 1000)
    assert psi(data, data) < 1e-6


def test_psi_binary_flag_detects_shift():
    """78/22 -> 50/50 promo shift must NOT report zero (quantile-binning bug)."""
    expected = np.array([0] * 78 + [1] * 22, dtype=float)
    actual = np.array([0] * 50 + [1] * 50, dtype=float)
    value = psi(expected, actual)
    assert value > 0.25  # action_needed territory


def test_psi_quantile_features_detect_shift():
    rng = np.random.default_rng(2)
    expected = rng.normal(100, 15, 2000)
    shifted = rng.normal(250, 15, 2000)
    assert psi(expected, shifted) > 0.25


def test_drift_report_overall_severity_wins():
    baseline = pd.DataFrame({"flag": np.r_[np.zeros(80), np.ones(20)],
                             "value": np.arange(100, dtype=float)})
    current = pd.DataFrame({"flag": np.r_[np.zeros(50), np.ones(50)],
                            "value": np.arange(100, dtype=float)})
    report = drift_report(baseline, current, ["value", "flag"])
    assert report["overall"] == "action_needed"
    by_feature = {row["feature"]: row for row in report["features"]}
    assert by_feature["flag"]["severity"] == "action_needed"
    assert by_feature["value"]["severity"] == "stable"

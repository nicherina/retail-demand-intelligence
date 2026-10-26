"""Training data generation.

The demand generator is a simulation calibrated on the real NKD retail
analytics work (market mix, store archetypes, seasonality, promo lift) -
same logic as notebook 02 cell 3, parameterized for reuse and testing.
The generator is deterministic under RANDOM_STATE, which is what makes the
training pipeline reproducible end to end.
"""

import numpy as np
import pandas as pd

from retail_dti.config import RANDOM_STATE

CAT_MULT = {"fashion": 1.4, "lingerie": 0.9, "home_textiles": 0.8, "hard_goods": 0.7}
ARCH_BASE = {"urban": 120, "suburban": 80, "rural": 45, "outlet": 95}
MARKETS = ["DE", "AT", "PL", "CZ", "SK", "HU"]
MARKET_PROBS = [0.45, 0.12, 0.18, 0.10, 0.08, 0.07]
ARCHETYPES = ["urban", "suburban", "rural", "outlet"]
ARCHETYPE_PROBS = [0.30, 0.40, 0.20, 0.10]
STORE_SIZES = [800, 1200, 1800, 2500, 3500]


def generate_training_data(n_stores: int = 50, start: str = "2022-01-03",
                           end: str = "2024-12-30") -> pd.DataFrame:
    """Generate weekly store-category demand rows (simulation methodology)."""
    rng = np.random.default_rng(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)
    stores = [f"ST{str(i).zfill(4)}" for i in range(1, n_stores + 1)]
    weeks = pd.date_range(start, end, freq="W")
    categories = list(CAT_MULT.keys())

    rows = []
    for store in stores:
        market = MARKETS[rng.choice(len(MARKETS), p=MARKET_PROBS)]
        archetype = ARCHETYPES[rng.choice(len(ARCHETYPES), p=ARCHETYPE_PROBS)]
        store_size = STORE_SIZES[rng.integers(len(STORE_SIZES))]
        city_pop_k = round(float(rng.lognormal(5, 1)), 1)

        for cat in categories:
            for w in weeks:
                base = ARCH_BASE[archetype] * CAT_MULT[cat]
                week_of_year = w.isocalendar().week
                seasonal = 1 + 0.35 * np.sin(2 * np.pi * (week_of_year - 10) / 52)
                if cat == "fashion":
                    seasonal += 0.2 * np.sin(2 * np.pi * (week_of_year - 36) / 52)
                temp_idx = np.sin(2 * np.pi * (week_of_year - 26) / 52)
                weather_effect = 1 + 0.1 * temp_idx if cat in ("fashion", "home_textiles") else 1.0
                promo = int(rng.choice([0, 1], p=[0.78, 0.22]))
                promo_lift = 1.25 if promo else 1.0
                weeks_since_start = (w - weeks[0]).days / 7
                trend = 1 + 0.004 * weeks_since_start
                demand = base * seasonal * weather_effect * promo_lift * trend
                demand = max(0, int(demand * rng.normal(1, 0.15)))

                rows.append({
                    "store_id": store,
                    "market": market,
                    "archetype": archetype,
                    "store_size": store_size,
                    "city_pop_k": city_pop_k,
                    "week_start": w,
                    "week_num": week_of_year,
                    "month": w.month,
                    "year": w.year,
                    "category": cat,
                    "units_sold": demand,
                    "promo_flag": promo,
                    "temp_idx": round(float(temp_idx), 3),
                })
    return pd.DataFrame(rows)

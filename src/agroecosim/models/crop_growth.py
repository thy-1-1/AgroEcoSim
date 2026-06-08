"""Crop growth process layer.

This module separates crop growth drivers from food-web interactions. It follows
the portfolio framing inspired by process-based crop models: weather, seasonal
stage, and soil response affect the crop carrying capacity before biotic
interactions are evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CropGrowthConfig:
    """Configuration for a seasonal crop-growth driver."""

    base_growth_rate: float = 0.20
    base_capacity: float = 500.0
    harvest_capacity_fraction: float = 0.10
    fallow_growth_rate: float = 0.005


class CropGrowthDriver:
    """Generate seasonal crop growth and carrying-capacity signals."""

    def __init__(self, config: CropGrowthConfig | None = None) -> None:
        self.config = config or CropGrowthConfig()

    def seasonal_profile(self, days: int = 365) -> pd.DataFrame:
        """Return daily crop growth-rate and carrying-capacity drivers."""

        day = np.arange(days)
        month = ((day / 30.4).astype(int) % 12) + 1
        growth = np.full(days, self.config.fallow_growth_rate, dtype=float)
        capacity = np.full(days, self.config.base_capacity, dtype=float)

        preparation = month == 3
        early_growth = (month >= 5) & (month <= 6)
        peak_growth = (month >= 7) & (month <= 9)
        harvest = month == 10

        capacity[preparation | harvest] = self.config.base_capacity * self.config.harvest_capacity_fraction
        growth[early_growth] = 0.010
        growth[peak_growth] = 0.015
        growth[harvest] = -0.020

        return pd.DataFrame(
            {
                "day": day,
                "month": month,
                "crop_growth_rate": growth,
                "crop_carrying_capacity": capacity,
            }
        )


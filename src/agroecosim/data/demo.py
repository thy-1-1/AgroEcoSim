"""Deterministic demo data for the AgroEcoSim pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_demo_timeseries(periods: int = 36, seed: int = 2025) -> pd.DataFrame:
    """Generate a compact monthly agroecosystem time series.

    The data are synthetic but structured: crop biomass follows a seasonal
    cycle, pest abundance tracks crop availability, chemical pressure declines
    under a transition pathway, and soil/resilience indicators improve over
    time. This gives the demo pipeline a stable input without bundling external
    datasets.
    """

    rng = np.random.default_rng(seed)
    index = np.arange(periods)
    season = 0.5 + 0.5 * np.sin(2 * np.pi * (index % 12) / 12 - np.pi / 5)
    transition = index / max(periods - 1, 1)

    pesticide_intensity = np.clip(0.85 - 0.55 * transition + 0.05 * np.cos(index / 2), 0.08, 0.90)
    crop_biomass = 90 + 320 * season + 60 * transition + rng.normal(0, 8, periods)
    pest_abundance = 35 + 120 * season * (0.45 + pesticide_intensity) - 18 * transition + rng.normal(0, 5, periods)
    bird_abundance = 6 + 5 * season + 4 * transition + rng.normal(0, 0.5, periods)
    bat_abundance = 2 + 7 * transition + 2 * season + rng.normal(0, 0.4, periods)
    bee_abundance = 10 + 18 * transition + 8 * season + rng.normal(0, 1.0, periods)
    soil_quality = 48 + 26 * transition + 4 * np.sin(index / 4) + rng.normal(0, 1.2, periods)

    total_biomass = crop_biomass + pest_abundance + bird_abundance + bat_abundance + bee_abundance
    biomass_growth = pd.Series(total_biomass).pct_change().fillna(0.0).clip(lower=-0.25, upper=0.35)
    crop_cover = np.clip(crop_biomass / 520, 0.1, 0.95)

    return pd.DataFrame(
        {
            "month_index": index,
            "crop_biomass": np.round(crop_biomass, 3),
            "pest_abundance": np.round(np.clip(pest_abundance, 0, None), 3),
            "bird_abundance": np.round(np.clip(bird_abundance, 0, None), 3),
            "bat_abundance": np.round(np.clip(bat_abundance, 0, None), 3),
            "bee_abundance": np.round(np.clip(bee_abundance, 0, None), 3),
            "soil_quality": np.round(soil_quality, 3),
            "producer_reduction_rate": np.round(np.clip(0.36 - 0.12 * transition + rng.normal(0, 0.01, periods), 0.05, 0.45), 4),
            "pesticide_intensity": np.round(pesticide_intensity, 4),
            "total_biomass_reduction": np.round(np.clip(0.32 - 0.14 * transition - biomass_growth * 0.15, 0.02, 0.40), 4),
            "crop_cover": np.round(crop_cover, 4),
            "total_biomass_growth": np.round(np.clip(0.16 + biomass_growth + 0.18 * transition, 0.02, 0.55), 4),
            "carrying_capacity_growth": np.round(0.18 + 0.32 * transition, 4),
            "ecosystem_resilience": np.round(0.28 + 0.30 * transition + soil_quality / 600, 4),
            "ecosystem_resistance": np.round(0.34 + 0.26 * transition + (1 - pesticide_intensity) * 0.12, 4),
        }
    )


def write_demo_timeseries(output_path: str) -> None:
    """Write the deterministic demo data set to disk."""

    frame = generate_demo_timeseries()
    frame.to_csv(output_path, index=False)

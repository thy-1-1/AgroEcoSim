"""Ecological indicator pipeline for AgroEcoSim.

This module expresses the data-processing layer used in the portfolio:
raw ecological and management observations are aligned to a common time axis,
converted into PSR-compatible indicators, and normalized so positive and
negative indicators can be compared in one composite evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IndicatorSpec:
    """Description of one ecological indicator.

    Attributes:
        name: Column name in the source data.
        tendency: ``"positive"`` if larger values improve stability, otherwise
            ``"negative"``.
        group: PSR layer name: pressure, state, or response.
    """

    name: str
    tendency: str
    group: str


DEFAULT_INDICATORS: tuple[IndicatorSpec, ...] = (
    IndicatorSpec("producer_reduction_rate", "negative", "pressure"),
    IndicatorSpec("pesticide_intensity", "negative", "pressure"),
    IndicatorSpec("total_biomass_reduction", "negative", "pressure"),
    IndicatorSpec("crop_cover", "positive", "state"),
    IndicatorSpec("total_biomass_growth", "positive", "state"),
    IndicatorSpec("carrying_capacity_growth", "positive", "response"),
    IndicatorSpec("ecosystem_resilience", "positive", "response"),
    IndicatorSpec("ecosystem_resistance", "positive", "response"),
)


def normalize_indicator(values: pd.Series, tendency: str) -> pd.Series:
    """Normalize one indicator to the 0.1 to 1.0 range used by PSR scoring.

    Args:
        values: Raw indicator values.
        tendency: ``"positive"`` or ``"negative"``.

    Returns:
        A normalized series where higher values always indicate better
        ecosystem stability.
    """

    series = values.astype(float)
    lower = series.min()
    upper = series.max()
    if np.isclose(upper, lower):
        return pd.Series(np.full(len(series), 0.55), index=series.index)

    if tendency == "positive":
        scaled = (series - lower) / (upper - lower)
    elif tendency == "negative":
        scaled = (upper - series) / (upper - lower)
    else:
        raise ValueError("tendency must be either 'positive' or 'negative'")
    return 0.1 + 0.9 * scaled


def build_indicator_frame(
    raw: pd.DataFrame,
    indicators: Iterable[IndicatorSpec] = DEFAULT_INDICATORS,
) -> pd.DataFrame:
    """Build a PSR-ready indicator table.

    Args:
        raw: Data frame containing ecological signals and management variables.
        indicators: Indicator definitions to extract and normalize.

    Returns:
        Data frame with normalized indicator columns and PSR group metadata.
    """

    normalized = pd.DataFrame(index=raw.index)
    metadata = {}
    for spec in indicators:
        if spec.name not in raw.columns:
            raise KeyError(f"Missing required indicator column: {spec.name}")
        normalized[spec.name] = normalize_indicator(raw[spec.name], spec.tendency)
        metadata[spec.name] = {"group": spec.group, "tendency": spec.tendency}
    normalized.attrs["indicator_metadata"] = metadata
    return normalized


def synthetic_indicator_sample(periods: int = 12) -> pd.DataFrame:
    """Create a compact demonstration indicator set for portfolio figures."""

    t = np.linspace(0, 1, periods)
    return pd.DataFrame(
        {
            "producer_reduction_rate": 0.42 - 0.12 * t,
            "pesticide_intensity": 0.80 - 0.55 * t,
            "total_biomass_reduction": 0.36 - 0.14 * t,
            "crop_cover": 0.44 + 0.18 * t,
            "total_biomass_growth": 0.30 + 0.22 * t,
            "carrying_capacity_growth": 0.20 + 0.28 * t,
            "ecosystem_resilience": 0.34 + 0.24 * t,
            "ecosystem_resistance": 0.38 + 0.30 * t,
        }
    )

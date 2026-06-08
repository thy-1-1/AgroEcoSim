"""Stability metrics for comparing ecosystem trajectories."""

from __future__ import annotations

import numpy as np
import pandas as pd


def coefficient_of_variation(values: pd.Series) -> float:
    """Return standard deviation divided by mean for one trajectory."""

    mean = float(values.mean())
    if np.isclose(mean, 0.0):
        return 0.0
    return float(values.std(ddof=0) / mean)


def recovery_time(values: pd.Series, tolerance: float = 0.05) -> int:
    """Estimate time index when a trajectory stays near its final value."""

    final = float(values.iloc[-1])
    if np.isclose(final, 0.0):
        return len(values) - 1
    relative_error = (values - final).abs() / abs(final)
    stable = relative_error <= tolerance
    for index in range(len(values)):
        if stable.iloc[index:].all():
            return index
    return len(values) - 1


def stability_report(trajectory: pd.DataFrame, species_columns: list[str]) -> pd.DataFrame:
    """Compute compact stability metrics for selected species."""

    rows = []
    for column in species_columns:
        rows.append(
            {
                "species": column,
                "coefficient_of_variation": coefficient_of_variation(trajectory[column]),
                "recovery_time_index": recovery_time(trajectory[column]),
                "final_state": float(trajectory[column].iloc[-1]),
            }
        )
    return pd.DataFrame(rows)

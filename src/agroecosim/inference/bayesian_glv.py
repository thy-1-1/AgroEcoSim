"""Bayesian-style interface for generalized Lotka-Volterra inference.

This module presents the workflow interface used for uncertainty analysis:
compute log-derivatives, form regression matrices, and summarize interaction
coefficients with credible intervals. A production implementation could connect
this layer to CmdStanPy, PyMC, or another Bayesian backend.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class InteractionInterval:
    """Posterior-style interval for one interaction coefficient."""

    source: str
    target: str
    mean: float
    lower: float
    upper: float
    significant: bool


class BayesianGLV:
    """Prepare and summarize gLV interaction inference."""

    def compute_log_derivative(self, abundance: pd.DataFrame, time: pd.Series) -> pd.DataFrame:
        """Approximate dlog(X)/dt with finite differences."""

        safe = abundance.clip(lower=1e-9)
        log_values = np.log(safe)
        gradients = np.gradient(log_values.to_numpy(), time.to_numpy(), axis=0)
        return pd.DataFrame(gradients, columns=abundance.columns, index=abundance.index)

    def design_matrix(self, abundance: pd.DataFrame) -> pd.DataFrame:
        """Create the covariate matrix used for gLV regression."""

        matrix = abundance.copy()
        matrix.insert(0, "intercept", 1.0)
        return matrix

    def summarize_interactions(
        self,
        species: list[str],
        coefficient_mean: np.ndarray,
        coefficient_sd: np.ndarray,
        z_value: float = 1.96,
    ) -> list[InteractionInterval]:
        """Build credible intervals from coefficient means and standard deviations."""

        intervals: list[InteractionInterval] = []
        for i, target in enumerate(species):
            for j, source in enumerate(species):
                mean = float(coefficient_mean[i, j])
                sd = float(coefficient_sd[i, j])
                lower = mean - z_value * sd
                upper = mean + z_value * sd
                intervals.append(
                    InteractionInterval(
                        source=source,
                        target=target,
                        mean=mean,
                        lower=lower,
                        upper=upper,
                        significant=(lower > 0 or upper < 0),
                    )
                )
        return intervals

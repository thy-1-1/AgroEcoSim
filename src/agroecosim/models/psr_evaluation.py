"""Pressure-State-Response ecosystem stability evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PSRResult:
    """Composite PSR score and the entropy weights used to compute it."""

    scores: pd.Series
    weights: pd.Series


class PSREvaluator:
    """Evaluate ecosystem stability from normalized PSR indicators."""

    def entropy_weights(self, indicators: pd.DataFrame) -> pd.Series:
        """Compute objective entropy weights for normalized indicators."""

        values = indicators.astype(float).clip(lower=1e-12)
        proportions = values.div(values.sum(axis=0), axis=1)
        entropy = -(proportions * np.log(proportions)).sum(axis=0) / np.log(len(values))
        utility = 1.0 - entropy
        if np.isclose(utility.sum(), 0):
            return pd.Series(np.full(len(utility), 1.0 / len(utility)), index=utility.index)
        return utility / utility.sum()

    def score(self, indicators: pd.DataFrame) -> PSRResult:
        """Return weighted composite stability scores."""

        weights = self.entropy_weights(indicators)
        scores = indicators.mul(weights, axis=1).sum(axis=1)
        return PSRResult(scores=scores, weights=weights)

    @staticmethod
    def classify(score: float) -> str:
        """Map a composite score to an interpretable stability level."""

        if score < 0.2:
            return "precarious"
        if score < 0.4:
            return "less stable"
        if score < 0.6:
            return "critical stability"
        if score < 0.8:
            return "more stable"
        return "stable"

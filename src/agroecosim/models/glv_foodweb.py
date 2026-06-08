"""Generalized Lotka-Volterra food-web model.

The class in this module is a lightweight research interface for representing
crop, pest, predator, pollinator, and soil-biota interactions as a matrix-driven
dynamic system. It is intentionally compact so the repository communicates the
modeling structure without claiming full scientific reproduction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    from scipy.integrate import solve_ivp
except ModuleNotFoundError:  # pragma: no cover - fallback for lightweight portfolio environments
    solve_ivp = None


@dataclass
class GLVFoodWeb:
    """Generalized Lotka-Volterra simulator.

    Args:
        species: Ordered species names.
        growth_rates: Intrinsic growth-rate vector.
        carrying_capacity: Carrying-capacity vector.
        interaction_matrix: Square matrix where positive values support the
            receiving species and negative values suppress it.
    """

    species: list[str]
    growth_rates: np.ndarray
    carrying_capacity: np.ndarray
    interaction_matrix: np.ndarray

    def derivative(self, _: float, state: np.ndarray) -> np.ndarray:
        """Compute the gLV derivative for the current state."""

        safe_state = np.clip(state, 0.0, self.carrying_capacity * 3.0)
        interaction_term = self.interaction_matrix @ safe_state
        density_term = 1.0 - safe_state / self.carrying_capacity
        return safe_state * (self.growth_rates * density_term + interaction_term)

    def simulate(
        self,
        initial_state: np.ndarray,
        horizon: float = 365.0,
        steps: int = 365,
    ) -> pd.DataFrame:
        """Simulate a trajectory and return a tidy data frame.

        Args:
            initial_state: Initial abundance for each species.
            horizon: Simulation horizon in model time units.
            steps: Number of output points.
        """

        time = np.linspace(0.0, horizon, steps)
        initial = np.asarray(initial_state, dtype=float)

        if solve_ivp is not None:
            solution = solve_ivp(
                self.derivative,
                t_span=(0.0, horizon),
                y0=initial,
                t_eval=time,
                vectorized=False,
                rtol=1e-6,
                atol=1e-8,
            )
            if not solution.success:
                raise RuntimeError(solution.message)
            values = solution.y.T
        else:
            values = np.zeros((steps, len(initial)), dtype=float)
            values[0] = initial
            dt = horizon / max(steps - 1, 1)
            upper = self.carrying_capacity * 3.0
            for index in range(1, steps):
                next_state = values[index - 1] + dt * self.derivative(time[index - 1], values[index - 1])
                values[index] = np.clip(
                    np.nan_to_num(next_state, nan=0.0, posinf=upper.max(), neginf=0.0),
                    0.0,
                    upper,
                )

        frame = pd.DataFrame(values, columns=self.species)
        frame.insert(0, "time", time)
        return frame


def demo_foodweb() -> GLVFoodWeb:
    """Return a display-oriented six-species food-web model."""

    species = ["crop", "pest", "bird", "bat", "bee", "soil_biota"]
    growth = np.array([0.20, 0.15, 0.05, 0.04, 0.06, 0.03])
    capacity = np.array([500, 300, 20, 18, 60, 250], dtype=float)
    interactions = np.array(
        [
            [0.00, -0.0020, 0.0000, 0.0010, 0.0012, 0.0007],
            [0.0014, 0.0000, -0.0300, -0.0350, 0.0000, 0.0000],
            [0.0000, 0.0040, 0.0000, -0.0010, 0.0000, 0.0000],
            [0.0000, 0.0045, -0.0010, 0.0000, 0.0000, 0.0000],
            [0.0008, 0.0000, 0.0000, 0.0000, 0.0000, 0.0004],
            [0.0006, 0.0000, 0.0000, 0.0000, 0.0004, 0.0000],
        ],
        dtype=float,
    )
    return GLVFoodWeb(species, growth, capacity, interactions)

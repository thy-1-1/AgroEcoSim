"""Simple ensemble assimilation interface for ecosystem state updates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class EnsembleState:
    """State ensemble and uncertainty covariance."""

    particles: np.ndarray
    covariance: np.ndarray

    @property
    def mean(self) -> np.ndarray:
        """Return the ensemble mean state."""

        return self.particles.mean(axis=0)


class EnsembleAssimilator:
    """Observation update layer inspired by ensemble Kalman filtering."""

    def update(
        self,
        state: EnsembleState,
        observation: np.ndarray,
        observation_matrix: np.ndarray,
        observation_noise: np.ndarray,
    ) -> EnsembleState:
        """Update ensemble particles with one observation vector."""

        predicted_obs = state.particles @ observation_matrix.T
        innovation = observation - predicted_obs.mean(axis=0)
        cov_xy = np.cov(state.particles.T, predicted_obs.T)[: state.particles.shape[1], state.particles.shape[1] :]
        cov_yy = np.cov(predicted_obs.T) + observation_noise
        gain = cov_xy @ np.linalg.pinv(cov_yy)
        updated_particles = state.particles + innovation @ gain.T
        updated_cov = np.cov(updated_particles.T)
        return EnsembleState(particles=updated_particles, covariance=updated_cov)

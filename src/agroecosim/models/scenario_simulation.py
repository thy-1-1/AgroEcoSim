"""Scenario orchestration for management interventions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from agroecosim.models.glv_foodweb import GLVFoodWeb, demo_foodweb


@dataclass(frozen=True)
class Scenario:
    """Management scenario loaded from configuration."""

    name: str
    label: str
    chemical_intensity: float
    bats: bool
    bees: bool
    soil_regeneration_rate: float
    narrative: str


class ScenarioRunner:
    """Apply scenario choices to a baseline food-web model."""

    def __init__(self, base_model: GLVFoodWeb | None = None) -> None:
        self.base_model = base_model or demo_foodweb()

    @staticmethod
    def load(path: str | Path) -> list[Scenario]:
        """Load scenario definitions from a YAML configuration file."""

        with Path(path).open("r", encoding="utf-8") as handle:
            config: dict[str, Any] = yaml.safe_load(handle)
        scenarios = []
        for name, item in config["scenarios"].items():
            scenarios.append(
                Scenario(
                    name=name,
                    label=item["label"],
                    chemical_intensity=float(item["chemical_intensity"]),
                    bats=bool(item["bats"]),
                    bees=bool(item["bees"]),
                    soil_regeneration_rate=float(item["soil_regeneration_rate"]),
                    narrative=item["narrative"],
                )
            )
        return scenarios

    def model_for(self, scenario: Scenario) -> GLVFoodWeb:
        """Create a scenario-adjusted copy of the baseline model."""

        model = self.base_model
        growth = model.growth_rates.copy()
        capacity = model.carrying_capacity.copy()
        interactions = model.interaction_matrix.copy()

        crop = model.species.index("crop")
        pest = model.species.index("pest")
        bat = model.species.index("bat")
        bee = model.species.index("bee")
        soil = model.species.index("soil_biota")

        interactions[crop, pest] -= 0.0012 * scenario.chemical_intensity
        growth[pest] -= 0.05 * scenario.chemical_intensity
        growth[soil] += scenario.soil_regeneration_rate

        if scenario.bats:
            interactions[pest, bat] -= 0.015
            interactions[crop, bat] += 0.0006
            capacity[bat] *= 1.20
        else:
            capacity[bat] *= 0.15

        if scenario.bees:
            interactions[crop, bee] += 0.0009
            interactions[soil, bee] += 0.0002
            capacity[bee] *= 1.25
        else:
            capacity[bee] *= 0.20

        return GLVFoodWeb(model.species, growth, capacity, interactions)

    def run(self, scenario: Scenario, initial_state: np.ndarray) -> pd.DataFrame:
        """Simulate one scenario."""

        return self.model_for(scenario).simulate(initial_state=initial_state)

from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from agroecosim.models.glv_foodweb import demo_foodweb
from agroecosim.models.scenario_simulation import ScenarioRunner


ROOT = Path(__file__).resolve().parents[1]


class ModelTest(unittest.TestCase):
    def test_glv_simulation_returns_finite_trajectory(self) -> None:
        model = demo_foodweb()
        trajectory = model.simulate(np.array([100, 50, 5, 3, 12, 80]), horizon=30, steps=30)

        self.assertEqual(list(trajectory.columns), ["time", "crop", "pest", "bird", "bat", "bee", "soil_biota"])
        self.assertEqual(trajectory.shape, (30, 7))
        self.assertFalse(trajectory.isna().any().any())

    def test_scenario_configuration_loads(self) -> None:
        scenarios = ScenarioRunner.load(ROOT / "configs" / "scenarios.json")
        names = {scenario.name for scenario in scenarios}

        self.assertIn("conventional_baseline", names)
        self.assertIn("organic_transition", names)
        self.assertEqual(len(scenarios), 6)


if __name__ == "__main__":
    unittest.main()

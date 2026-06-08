from __future__ import annotations

import unittest

from agroecosim.data.demo import generate_demo_timeseries
from agroecosim.data.pipeline import DEFAULT_INDICATORS, build_indicator_frame
from agroecosim.models.psr_evaluation import PSREvaluator


class DataPipelineTest(unittest.TestCase):
    def test_indicator_frame_contains_all_default_indicators(self) -> None:
        raw = generate_demo_timeseries(periods=18)
        indicators = build_indicator_frame(raw)

        self.assertEqual(set(indicators.columns), {spec.name for spec in DEFAULT_INDICATORS})
        self.assertGreaterEqual(float(indicators.min().min()), 0.1)
        self.assertLessEqual(float(indicators.max().max()), 1.0)

    def test_entropy_weights_sum_to_one(self) -> None:
        raw = generate_demo_timeseries(periods=18)
        indicators = build_indicator_frame(raw)
        result = PSREvaluator().score(indicators)

        self.assertAlmostEqual(float(result.weights.sum()), 1.0, places=6)
        self.assertEqual(len(result.scores), len(raw))


if __name__ == "__main__":
    unittest.main()

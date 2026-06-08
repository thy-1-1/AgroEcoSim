from __future__ import annotations

import unittest

import pandas as pd

from agroecosim.metrics.stability import coefficient_of_variation, recovery_time, stability_report


class StabilityMetricsTest(unittest.TestCase):
    def test_coefficient_of_variation_handles_constant_series(self) -> None:
        self.assertEqual(coefficient_of_variation(pd.Series([5, 5, 5])), 0.0)

    def test_recovery_time_identifies_stable_tail(self) -> None:
        self.assertLessEqual(recovery_time(pd.Series([1.0, 2.0, 3.0, 3.02, 3.01])), 3)

    def test_stability_report_contains_expected_columns(self) -> None:
        frame = pd.DataFrame({"crop": [1, 2, 3], "pest": [3, 2, 1]})
        report = stability_report(frame, ["crop", "pest"])

        self.assertEqual(set(report["species"]), {"crop", "pest"})
        self.assertIn("coefficient_of_variation", report.columns)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agroecosim.pipeline import run_full_pipeline


ROOT = Path(__file__).resolve().parents[1]


class PipelineTest(unittest.TestCase):
    def test_full_pipeline_writes_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            shutil.copytree(ROOT / "configs", temp_root / "configs")
            outputs = run_full_pipeline(temp_root)

            expected = {
                "indicator_scores",
                "stability_indicators",
                "scenario_summary",
                "scenario_figure",
                "trajectory_figure",
            }
            self.assertTrue(expected.issubset(outputs))
            for key in expected:
                self.assertTrue(outputs[key].exists(), key)


if __name__ == "__main__":
    unittest.main()

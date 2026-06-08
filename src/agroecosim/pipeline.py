"""Executable research pipeline for AgroEcoSim."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from agroecosim.data.demo import write_demo_timeseries
from agroecosim.data.pipeline import DEFAULT_INDICATORS, build_indicator_frame
from agroecosim.metrics.stability import stability_report
from agroecosim.models.psr_evaluation import PSREvaluator
from agroecosim.models.scenario_simulation import ScenarioRunner
from agroecosim.visualization.figures import write_scenario_comparison, write_trajectory_figure


@dataclass(frozen=True)
class PipelinePaths:
    """Resolved project paths used by the executable pipeline."""

    root: Path
    config: Path
    demo_data: Path
    results: Path

    @classmethod
    def from_root(cls, root: str | Path) -> "PipelinePaths":
        base = Path(root).resolve()
        return cls(
            root=base,
            config=base / "configs" / "scenarios.json",
            demo_data=base / "data" / "demo" / "agroecosystem_timeseries.csv",
            results=base / "results",
        )


def ensure_demo_data(paths: PipelinePaths) -> Path:
    """Create the demo data set if it is missing."""

    paths.demo_data.parent.mkdir(parents=True, exist_ok=True)
    if not paths.demo_data.exists():
        write_demo_timeseries(str(paths.demo_data))
    return paths.demo_data


def run_indicator_pipeline(paths: PipelinePaths) -> dict[str, Path]:
    """Build PSR indicator scores and weight tables."""

    ensure_demo_data(paths)
    raw = pd.read_csv(paths.demo_data)
    indicators = build_indicator_frame(raw)
    result = PSREvaluator().score(indicators)

    tables_dir = paths.results / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    indicator_scores = raw[["month_index"]].copy()
    indicator_scores["composite_psr_score"] = result.scores.round(5)
    indicator_scores["stability_level"] = indicator_scores["composite_psr_score"].map(PSREvaluator.classify)
    scores_path = tables_dir / "indicator_scores.csv"
    indicator_scores.to_csv(scores_path, index=False)

    weights = pd.DataFrame(
        {
            "indicator": [spec.name for spec in DEFAULT_INDICATORS],
            "psr_group": [spec.group for spec in DEFAULT_INDICATORS],
            "tendency": [spec.tendency for spec in DEFAULT_INDICATORS],
            "entropy_weight": [round(float(result.weights[spec.name]), 6) for spec in DEFAULT_INDICATORS],
        }
    )
    weights_path = tables_dir / "stability_indicators.csv"
    weights.to_csv(weights_path, index=False)
    return {"indicator_scores": scores_path, "stability_indicators": weights_path}


def _scenario_score(row: dict[str, float]) -> float:
    stability = (
        0.34 * (1.0 - row["chemical_pressure"])
        + 0.26 * (1.0 - min(row["crop_cv"], 1.0))
        + 0.22 * row["soil_response"]
        + 0.18 * row["biodiversity_proxy"]
    )
    return round(0.38 + 0.42 * stability, 5)


def run_scenario_pipeline(paths: PipelinePaths) -> dict[str, Path]:
    """Run all configured intervention scenarios and summarize outcomes."""

    scenarios = ScenarioRunner.load(paths.config)
    runner = ScenarioRunner()
    initial_state = np.array([100, 50, 5, 3, 12, 80], dtype=float)

    tables_dir = paths.results / "tables"
    trajectory_dir = paths.results / "trajectories"
    tables_dir.mkdir(parents=True, exist_ok=True)
    trajectory_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, float | str]] = []
    trajectories: dict[str, pd.DataFrame] = {}
    max_soil_response = max(scenario.soil_regeneration_rate for scenario in scenarios)

    for scenario in scenarios:
        trajectory = runner.run(scenario, initial_state)
        trajectories[scenario.name] = trajectory
        trajectory_path = trajectory_dir / f"{scenario.name}.csv"
        trajectory.to_csv(trajectory_path, index=False)

        report = stability_report(trajectory, ["crop", "pest", "bird", "bat", "bee", "soil_biota"])
        mean_cv = float(report["coefficient_of_variation"].mean())
        crop_cv = float(report.loc[report["species"] == "crop", "coefficient_of_variation"].iloc[0])
        biodiversity_proxy = float((trajectory[["bird", "bat", "bee", "soil_biota"]].iloc[-1] > 1.0).mean())
        row = {
            "scenario": scenario.label,
            "scenario_id": scenario.name,
            "chemical_pressure": scenario.chemical_intensity,
            "mean_cv": mean_cv,
            "crop_cv": crop_cv,
            "soil_response": scenario.soil_regeneration_rate / max_soil_response,
            "biodiversity_proxy": biodiversity_proxy,
            "final_crop": float(trajectory["crop"].iloc[-1]),
            "mean_crop": float(trajectory["crop"].mean()),
            "mean_pest": float(trajectory["pest"].mean()),
            "interpretation": scenario.narrative,
        }
        row["stability_score"] = _scenario_score(row)
        rows.append(row)

    summary = pd.DataFrame(rows)
    baseline_crop = float(summary.loc[summary["scenario_id"] == "conventional_baseline", "mean_crop"].iloc[0])
    summary["crop_output_index"] = (summary["mean_crop"] / baseline_crop).round(4)
    summary["chemical_pressure"] = summary["chemical_pressure"].round(4)
    summary["mean_cv"] = summary["mean_cv"].round(5)
    summary["crop_cv"] = summary["crop_cv"].round(5)
    summary_path = tables_dir / "scenario_summary.csv"
    summary.to_csv(summary_path, index=False)
    return {"scenario_summary": summary_path, "trajectory_dir": trajectory_dir}


def run_figure_pipeline(paths: PipelinePaths) -> dict[str, Path]:
    """Generate result figures from pipeline outputs."""

    summary_path = paths.results / "tables" / "scenario_summary.csv"
    integrated_path = paths.results / "trajectories" / "integrated_biocontrol.csv"
    if not summary_path.exists() or not integrated_path.exists():
        run_scenario_pipeline(paths)

    figures_dir = paths.results / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(summary_path)
    trajectory = pd.read_csv(integrated_path)

    scenario_figure = write_scenario_comparison(summary, figures_dir / "scenario_comparison_generated.svg")
    trajectory_figure = write_trajectory_figure(trajectory, figures_dir / "integrated_trajectories_generated.svg")
    return {"scenario_figure": scenario_figure, "trajectory_figure": trajectory_figure}


def run_full_pipeline(root: str | Path) -> dict[str, Path]:
    """Run the full demo pipeline from data to tables and figures."""

    paths = PipelinePaths.from_root(root)
    outputs: dict[str, Path] = {}
    outputs.update(run_indicator_pipeline(paths))
    outputs.update(run_scenario_pipeline(paths))
    outputs.update(run_figure_pipeline(paths))
    return outputs

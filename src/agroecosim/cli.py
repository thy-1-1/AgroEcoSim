"""Command line interface for AgroEcoSim."""

from __future__ import annotations

import argparse
from pathlib import Path

from agroecosim.data.demo import write_demo_timeseries
from agroecosim.pipeline import PipelinePaths, run_figure_pipeline, run_full_pipeline, run_indicator_pipeline, run_scenario_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Create the project command-line parser."""

    parser = argparse.ArgumentParser(description="Run AgroEcoSim demo analyses.")
    parser.add_argument("--root", default=Path.cwd(), type=Path, help="Repository root directory.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("pipeline", help="Run data, scenario, and figure pipelines.")
    subparsers.add_parser("data", help="Generate the demo agroecosystem time series.")
    subparsers.add_parser("indicators", help="Run PSR indicator scoring.")
    subparsers.add_parser("scenarios", help="Run management scenario simulations.")
    subparsers.add_parser("figures", help="Generate result figures.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "pipeline"
    paths = PipelinePaths.from_root(args.root)

    if command == "data":
        paths.demo_data.parent.mkdir(parents=True, exist_ok=True)
        write_demo_timeseries(str(paths.demo_data))
        outputs = {"demo_data": paths.demo_data}
    elif command == "indicators":
        outputs = run_indicator_pipeline(paths)
    elif command == "scenarios":
        outputs = run_scenario_pipeline(paths)
    elif command == "figures":
        outputs = run_figure_pipeline(paths)
    elif command == "pipeline":
        outputs = run_full_pipeline(args.root)
    else:
        parser.error(f"Unknown command: {command}")
        return 2

    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

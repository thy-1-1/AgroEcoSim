"""Publication-style figure helpers for AgroEcoSim."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_scenario_comparison(summary: pd.DataFrame, output_path: str) -> None:
    """Create a stability and chemical-pressure scenario comparison plot."""

    fig, ax1 = plt.subplots(figsize=(10, 4.8))
    ax1.plot(summary["scenario"], summary["stability_score"], color="#1d3d32", marker="o", linewidth=2.5)
    ax1.set_ylabel("Composite stability score", color="#1d3d32")
    ax1.tick_params(axis="x", rotation=25)
    ax1.set_ylim(0.35, 0.82)

    ax2 = ax1.twinx()
    ax2.plot(summary["scenario"], summary["chemical_pressure"], color="#d97955", marker="o", linewidth=2.5)
    ax2.set_ylabel("Chemical pressure index", color="#d97955")
    ax2.set_ylim(0.0, 1.05)

    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)

#!/usr/bin/env python3
"""Run the full AgroEcoSim demo pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agroecosim.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["--root", str(ROOT), "pipeline"]))

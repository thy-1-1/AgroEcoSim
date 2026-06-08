"""Configuration loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON project configuration.

    JSON is used for the committed demo configuration so the full pipeline can
    run without an additional parser dependency.
    """

    config_path = Path(path)
    if config_path.suffix.lower() != ".json":
        raise ValueError("AgroEcoSim demo configurations must use JSON")
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

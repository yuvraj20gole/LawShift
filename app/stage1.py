"""Stage 1 — offence-date extraction.

Reuses the validated extractor from src/stage1_entity_extraction.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage1_entity_extraction import (  # noqa: E402
    CUTOFF,
    extract_offense_date,
    route as route_from_date,
)

__all__ = ["CUTOFF", "extract_offense_date", "route_from_date"]

"""Stage 2 — deterministic IPC/BNS gate on the extracted offence date.

Reuses the exact route() function validated in src/stage1_entity_extraction.py
(offense_date < 2024-07-01 → IPC, else BNS).
"""
from datetime import date

from .stage1 import CUTOFF, route_from_date


def route(offense_date: date) -> str:
    """Return 'IPC' or 'BNS' for a resolved offence date."""
    result = route_from_date(offense_date)
    if result == "CLARIFY":
        raise ValueError("route() called with None offence date")
    return result


__all__ = ["CUTOFF", "route"]

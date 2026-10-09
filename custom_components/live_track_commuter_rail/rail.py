"""The railroad's rail lines, shipped with the integration (rail/<operator>.json.gz), for the
off-rail refusal (SSOT 7.10, Lee 2026-10-08). No Home Assistant imports.

Built by tools/build_rail.py from the FRA North American Rail Network Lines (NTAD, US DOT),
a US Government work in the public domain, clipped to 3 km around the railroad's own GTFS
shapes and simplified at 10 m. A railroad without a file gets no check, and every fix it
reports is published as before.
"""

from __future__ import annotations

import gzip
import json
import os
from typing import Callable

from saw_livetrack.rail import RailIndex

from .const import OFF_RAIL_M

RAIL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rail")
FORMAT = 1


def load(operator_id: str) -> RailIndex | None:
    """The railroad's rail, or None without a usable file. Blocking: run it in an executor."""
    path = os.path.join(RAIL_DIR, f"{operator_id}.json.gz")
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("format") != FORMAT:
        return None
    idx = RailIndex(doc.get("lines") or [])
    return idx if len(idx) else None


def check(idx: RailIndex) -> Callable[[float, float], bool]:
    """Fleet's on_rail: some rail within OFF_RAIL_M."""
    return lambda lat, lon: idx.near(lat, lon, OFF_RAIL_M)

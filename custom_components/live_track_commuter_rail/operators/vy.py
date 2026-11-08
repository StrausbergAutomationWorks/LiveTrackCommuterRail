"""Vy's commuter trains (Norway): L1 Spikkestad-Oslo S-Lillestrom, L2 Stabekk-Oslo S-Ski and L4 Bergen-Arna, on
Entur through the shared client. No Home Assistant imports.

Lee 2026-11-07 (backlog 326): L lines here; Vy's F, RE, RX and R lines are Live Track Intercity Rail's. Operator id
`vy` (Lee 2026-11-08, SSOT 12; the id Intercity Rail uses for the same railroad, in this integration's namespace).
Look, label, lateness and identity: operators/norway.py. Keyless; CREDIT: NLOD's own form.
"""

from __future__ import annotations

from saw_livetrack.entur import VY as CODESPACE

from .norway import HUBS, make_operator

# L1 and L2's colour in Vy's timetable, until the timetable names the line's.
VY_GREEN = "#8DC63F"

VY = make_operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-08: vy.
    op_id="vy",
    name="Vy",
    short="Vy",
    codespace=CODESPACE,
    default_colour=VY_GREEN,
    hubs=HUBS,
)

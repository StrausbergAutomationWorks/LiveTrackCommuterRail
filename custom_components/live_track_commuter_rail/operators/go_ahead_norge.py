"""Go-Ahead Norge's commuter trains (Norway): L5 Jaerbanen, Stavanger-Egersund, on Entur through the shared client.
No Home Assistant imports.

Lee 2026-11-07 (backlog 326): L5 here; Go-Ahead's F5 and R50 are Live Track Intercity Rail's. Operator id
`go_ahead_norge` (Lee 2026-11-08, SSOT 12). Go-Ahead's route ids are numbers (GOA:Line:59 is L5), so the label waits
for the timetable (minutes after the first poll); until then Fleet's, the train number. Look, label, lateness and
identity: operators/norway.py. Keyless; CREDIT: NLOD's own form.
"""

from __future__ import annotations

from saw_livetrack.entur import GO_AHEAD as CODESPACE

from .norway import HUBS, make_operator

# L5's colour in Go-Ahead's timetable, until the timetable names the line's.
GO_AHEAD_GREEN = "#8DC63F"

GO_AHEAD_NORGE = make_operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-08: go_ahead_norge.
    op_id="go_ahead_norge",
    name="Go-Ahead Norge",
    short="Go-Ahead",
    codespace=CODESPACE,
    default_colour=GO_AHEAD_GREEN,
    hubs=HUBS,
)

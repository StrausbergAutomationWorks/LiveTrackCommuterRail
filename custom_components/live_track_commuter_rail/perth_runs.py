"""Transperth's trains (Perth) drawn from their timetable alone, each placed along its trip's own shape and published as
the map contract's NO-FIX estimate (06_MAP_CONTRACT.md D3d). No Home Assistant imports. SSOT 20.

Lee 2026-11-13 20:40 CST: "Perth doesn't release real time info, so if we build anything it has to be simulated from the
timetable like Cork." The runs are saw-livetrack 0.2.40's (transperth.scheduled_runs: every trip the timetable runs
yesterday or today, placed by its aimed times; no delay is ever known). Everything else is irish_runs.py's, which draws
Cork the same way: where a run is drawn along its trip's shape, what is published (position_source "estimated", no fix,
observed_at the timetable time it was last AT something, the shape's bearing while running, track_path along the
shape). Only the source of the runs differs, so this is a subclass that replaces poll().
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.transperth import scheduled_runs

from .irish_runs import IrishRuns


class PerthRuns(IrishRuns):
    """Per config entry: the runs scheduled_runs places, the calls placed on each trip's shape, and the position
    published last for each train. poll() in the executor, publish() on the event loop after Fleet; never both at
    once."""

    def poll(self, static: Mapping[str, Any] | None, now: float) -> list[dict[str, Any]]:  # type: ignore[override]
        """One row per run drawn, each with where it is drawn (IrishRuns._row). Blocking work on the first sight of a
        trip: run it in the executor."""
        self._fresh(static)
        table = (static or {}).get("table") or {}
        if not table.get("trips"):
            self.rows, self.skipped, self.unplaced = {}, {"no_timetable": 1}, 0
            return []
        runs, skipped = scheduled_runs(table, now)
        pos_of = table.get("stops") or {}
        names = table.get("stop_names") or {}
        rows: list[dict[str, Any]] = []
        unplaced = 0
        for run in runs:
            row = self._row(run, now, static or {}, pos_of, names)
            if row is None:
                skipped["no_stop_position"] = skipped.get("no_stop_position", 0) + 1
                continue
            unplaced += row["held"]
            rows.append(row)
        self.rows = {r["key"]: r for r in rows}
        self.skipped, self.unplaced = skipped, unplaced
        return rows

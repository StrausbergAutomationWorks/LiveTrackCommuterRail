"""Flytoget (Norway): FLY1 Drammen-Oslo S-Oslo lufthavn and FLY2 Stabekk-Oslo S-Oslo lufthavn, on Entur through the
shared client. No Home Assistant imports. SSOT section 12.

Lee 2026-11-07 (backlog 326): all of Flytoget here. Operator id `flytoget` (Lee 2026-11-08). Identity, label,
lateness: operators/norway.py.

THE LOOK (Lee 2026-11-08: "Leaving Oslo = Grey fill, Orange ring, Orange numbers/letters. Leaving Oslo Airport =
Orange fill, Grey ring, Grey numbers/letters"): going TO Oslo lufthavn, grey fill with an orange ring and label; going
away from it, orange fill with a grey ring and label. Read as: the hub is the airport (SSOT 12, decision 2). Direction
unknown: away. Lee 2026-11-08 13:03: "Flytoget needs its letters/numbers to be white": the label is white both ways;
fill, ring and arrow as before. The colours were read from a logo site (whatthelogo.com), not from a Flytoget style guide.

THE LINE (Lee 2026-11-08, decision 3): Flytoget's own shapes are straight lines (35 shapes, 121 points), so each is
REWRITTEN before distilling from rail/flytoget_lines.json.gz, built by tools/build_flytoget_lines.py from Vy's
shapes over the same track, one piece per pair of consecutive stations. A shape whose trips call at a pair the file
lacks (the rail-replacement buses' bus terminals) keeps Flytoget's own points.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import os
import zipfile
from typing import Any

from saw_livetrack.entur import FLYTOGET as CODESPACE

from .norway import RING_WIDTH, WHITE, keep_all, make_operator

GREY = "#7C7B7B"
ORANGE = "#EE7203"
AIRPORT = "Oslo lufthavn stasjon"
LINES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rail", "flytoget_lines.json.gz")
CREDIT = "; Flytoget's lines cut from Vy's timetable shapes, modified"

_pairs: dict[str, list] | None = None


def load_pairs(path: str = LINES_FILE) -> dict[str, list]:
    """{"<StopPlace>><StopPlace>": [[lat, lon], ...]} from the shipped file; {} when it is missing or unreadable."""
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    p = d.get("pairs") if isinstance(d, dict) else None
    return p if isinstance(p, dict) else {}


def look(colour: str | None, toward: bool | None) -> dict[str, Any]:
    fill, other = (GREY, ORANGE) if toward is True else (ORANGE, GREY)
    return {"marker_color": fill, "marker_ring_color": other, "marker_ring_width": RING_WIDTH,
            "marker_label_color": WHITE, "marker_label_outline_color": "none",
            "marker_arrow_color": fill, "marker_arrow_outline_color": other}


def _rows(z: zipfile.ZipFile, name: str):
    with z.open(name) as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline=""))
        header = next(rd, None)
        if header is None:
            return
        keys = [h.strip() for h in header]
        for row in rd:
            yield {k: (row[i].strip() if i < len(row) else "") for i, k in enumerate(keys)}


def rewrite_shapes(raw: bytes, pairs: dict[str, list] | None = None) -> bytes:
    """The zip with each shape replaced by the shipped pieces along its first trip's stations (module docstring).
    Blocking."""
    global _pairs
    if pairs is None:
        if _pairs is None:
            _pairs = load_pairs()
        pairs = _pairs
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    if not pairs or "shapes.txt" not in names or "stop_times.txt" not in names:
        return raw
    parent = {r["stop_id"]: (r.get("parent_station") or r["stop_id"]) for r in _rows(z, "stops.txt") if r.get("stop_id")}
    trip_shape = {r["trip_id"]: r.get("shape_id", "") for r in _rows(z, "trips.txt") if r.get("trip_id")}
    calls: dict[str, list] = {}
    for r in _rows(z, "stop_times.txt"):
        tid = r.get("trip_id", "")
        if trip_shape.get(tid):
            try:
                calls.setdefault(tid, []).append((int(r.get("stop_sequence", "")), parent.get(r["stop_id"], r["stop_id"])))
            except (ValueError, KeyError):
                continue
    built: dict[str, list] = {}
    for tid in sorted(calls):
        sid = trip_shape[tid]
        if sid in built:
            continue
        st = [p for _, p in sorted(calls[tid])]
        line: list = []
        for a, b in zip(st, st[1:]):
            piece = pairs.get("%s>%s" % (a, b))
            if not piece:
                line = []
                break
            line += piece if not line else piece[1:]
        built[sid] = line
    if not any(built.values()):
        return raw
    out_rows = ["shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"]
    kept = set()
    for sid in sorted(built):
        if built[sid]:
            kept.add(sid)
            out_rows += ["%s,%.6f,%.6f,%d\n" % (sid, la, lo, i + 1) for i, (la, lo) in enumerate(built[sid])]
    for r in _rows(z, "shapes.txt"):
        if r.get("shape_id") and r["shape_id"] not in kept:
            out_rows.append("%s,%s,%s,%s\n" % (r["shape_id"], r.get("shape_pt_lat", ""), r.get("shape_pt_lon", ""),
                                               r.get("shape_pt_sequence", "")))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for n in names:
            out.writestr(n, "".join(out_rows) if n == "shapes.txt" else z.read(n))
    return buf.getvalue()


FLYTOGET = make_operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-08: flytoget.
    op_id="flytoget",
    name="Flytoget",
    short="Flytoget",
    codespace=CODESPACE,
    default_colour=ORANGE,
    hubs=(AIRPORT,),
    look=look,
    route_keep=keep_all,
    rewrite=rewrite_shapes,
    credit=CREDIT,
)

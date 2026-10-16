"""Cut a GTFS static zip down to the routes of some route_types, before it is distilled.
No Home Assistant imports.

SE Queensland's timetable is ONE zip for every mode (SSOT section 9): measured
2026-10-15 on the copy of 2026-10-14 (bin\\seq_build_measure.txt), 35,966,145 bytes,
1,093 routes of which 511 are rail (route_type 2), 3,717,795 stop_times rows of which
236,615 are rail's, 13,118 stops of which rail uses 357. Distilled whole it would load
every bus stop time into memory once a day; cut to rail it is a zip of under 5 MB, and
the shapes it gives the off-rail check are rail's alone.

stop_times.txt is read ONCE, by column index (a first version read it twice through
csv.DictReader and took 24.3 s on the laptop; bin\\ltcr_seq_replay.txt). Values are
matched stripped (05_SHARED_LESSONS.md B5, Metra's spaces); rows are written back as
they were read. Files tied to no route (agency, calendars, feed_info, anything else)
are copied whole.
"""

from __future__ import annotations

import csv
import io
import zipfile
from typing import Iterable


def _reader(z: zipfile.ZipFile, name: str):
    """(raw header, stripped header, row iterator, open file), or None when the file
    is absent or empty."""
    if name not in z.namelist():
        return None
    fh = z.open(name)
    rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline=""))
    try:
        header = next(rd)
    except StopIteration:
        fh.close()
        return None
    return header, [h.strip() for h in header], rd, fh


def _column(z: zipfile.ZipFile, name: str, col: str, where: str | None = None,
            allowed: set[str] | None = None) -> set[str]:
    """Values of `col` (stripped), from rows whose `where` is in `allowed` (every row
    when `where` is None)."""
    r = _reader(z, name)
    if r is None:
        return set()
    _, keys, rd, fh = r
    with fh:
        if col not in keys or (where is not None and where not in keys):
            return set()
        ic = keys.index(col)
        iw = keys.index(where) if where is not None else None
        out: set[str] = set()
        for row in rd:
            if len(row) <= ic:
                continue
            if iw is not None and (len(row) <= iw or row[iw].strip() not in allowed):
                continue
            v = row[ic].strip()
            if v:
                out.add(v)
        return out


def _filter(z: zipfile.ZipFile, out: zipfile.ZipFile, name: str, col: str,
            allowed: set[str], collect: str | None = None) -> set[str]:
    """Copy `name` keeping the rows whose `col` is in `allowed`; returns the stripped
    values of `collect` in the kept rows (empty when None)."""
    got: set[str] = set()
    r = _reader(z, name)
    if r is None:
        out.writestr(name, z.read(name) if name in z.namelist() else b"")
        return got
    header, keys, rd, fh = r
    with fh:
        if col not in keys:
            out.writestr(name, z.read(name))
            return got
        i = keys.index(col)
        j = keys.index(collect) if collect in keys else None
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(header)
        for row in rd:
            if len(row) > i and row[i].strip() in allowed:
                w.writerow(row)
                if j is not None and len(row) > j:
                    got.add(row[j].strip())
    out.writestr(name, buf.getvalue())
    return got


def keep_route_types(raw: bytes, route_types: Iterable[str]) -> bytes:
    """The zip with only the routes whose route_type is in `route_types`, their trips,
    stop times, stops (with their parent stations) and shapes. Blocking."""
    types = {str(t).strip() for t in route_types}
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    routes = _column(z, "routes.txt", "route_id", "route_type", types)
    trips = _column(z, "trips.txt", "trip_id", "route_id", routes)
    shapes = _column(z, "trips.txt", "shape_id", "route_id", routes)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        # stop_times first: the stops it uses decide which stops are kept.
        used = (_filter(z, out, "stop_times.txt", "trip_id", trips, collect="stop_id")
                if "stop_times.txt" in names else set())
        parents = _column(z, "stops.txt", "parent_station", "stop_id", used)
        for name in names:
            if name == "stop_times.txt":
                continue
            if name == "routes.txt":
                _filter(z, out, name, "route_id", routes)
            elif name == "trips.txt":
                _filter(z, out, name, "trip_id", trips)
            elif name == "stops.txt":
                _filter(z, out, name, "stop_id", used | parents)
            elif name == "shapes.txt":
                _filter(z, out, name, "shape_id", shapes)
            else:
                out.writestr(name, z.read(name))
    return buf.getvalue()

"""Irish Rail's Commuter trains (SSOT 13): the cut, the runs drawn along their shapes as no-fix estimates (D3d), the
label, the hover, the look by line and direction, lateness, and the registry. A synthetic zip in the NTA's shape: one
line due east along 53.35 N, Maynooth (-6.40) - Ashtown (-6.33) - Connolly (-6.25) - Bray (Daly) (-6.20)."""

import datetime as dt
import io
import json
import pathlib
import unittest
import zipfile

from _load import load

from saw_livetrack import irish_rail as lib
from saw_livetrack.gtfs import Fleet, distill

ir = load("operators.irish_rail")
base = load("operators.base")
ops = load("operators")
runs_m = load("irish_runs")
rail = load("rail")
poll = load("poll")
gtfs_filter = load("gtfs_filter")
attributes = load("attributes")

DAY = dt.date(2026, 11, 10)   # a Tuesday; Dublin is on GMT
LAT = 53.35
STOPS = {"MYN": ("Maynooth", -6.40), "ASH": ("Ashtown", -6.33), "CNL": ("Connolly", -6.25), "BRY": ("Bray (Daly)", -6.20)}


def ts(h, m, s=0):
    return dt.datetime(2026, 11, 10, h, m, s, tzinfo=dt.timezone.utc).timestamp()


def _csv(rows):
    return "\n".join(",".join(str(c) for c in r) for r in rows) + "\n"


def make_zip(off_shape=None):
    """P100 Maynooth-Connolly (shape W, west to east), D101 Connolly-Maynooth (shape WR, W reversed), P102 Maynooth-
    Bray through Connolly (shape WB), P103 on a service that ran once in 2020, A200 InterCity and E300 DART on W (to
    be cut). `off_shape`: a stop id moved 1 km
    north, off every shape."""
    # No parent stations: the NTA's Irish Rail zip has none (0 of 152 stops, bin\ie_ltcr_replay.txt).
    stops = [["stop_id", "stop_name", "stop_lat", "stop_lon", "parent_station"]]
    for sid, (name, lon) in STOPS.items():
        stops.append([sid, name, LAT + (0.009 if sid == off_shape else 0.0), lon, ""])
    sid = lambda s: s
    w = [(LAT, round(-6.40 + 0.01 * i, 2)) for i in range(16)]           # -6.40 .. -6.25
    wb = [(LAT, round(-6.40 + 0.01 * i, 2)) for i in range(21)]          # -6.40 .. -6.20
    shapes = [["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]]
    for name, pts in (("W", w), ("WR", w[::-1]), ("WB", wb)):
        shapes += [[name, a, b, i + 1] for i, (a, b) in enumerate(pts)]
    trips = [["route_id", "service_id", "trip_id", "shape_id", "trip_short_name"],
             ["R1", "WK", "t100", "W", "P100"], ["R1", "WK", "t101", "WR", "D101"], ["R1", "WK", "t102", "WB", "P102"],
             ["R1", "OLD", "t103", "W", "P103"],
             ["R2", "WK", "t200", "W", "A200"], ["R3", "WK", "t300", "W", "E300"]]
    st = [["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "pickup_type", "drop_off_type"]]

    def run(tid, calls):
        for i, (s, a, d) in enumerate(calls):
            st.append([tid, a, d, sid(s), i + 1, 0, 0])
    run("t100", [("MYN", "07:00:00", "07:00:00"), ("ASH", "07:10:00", "07:11:00"), ("CNL", "07:20:00", "07:20:00")])
    run("t101", [("CNL", "08:00:00", "08:00:00"), ("ASH", "08:10:00", "08:11:00"), ("MYN", "08:20:00", "08:20:00")])
    run("t102", [("MYN", "09:00:00", "09:00:00"), ("ASH", "09:10:00", "09:11:00"), ("CNL", "09:20:00", "09:22:00"),
                 ("BRY", "09:30:00", "09:30:00")])
    run("t103", [("MYN", "12:00:00", "12:00:00"), ("CNL", "12:20:00", "12:20:00")])
    run("t200", [("MYN", "10:00:00", "10:00:00"), ("CNL", "10:20:00", "10:20:00")])
    run("t300", [("MYN", "11:00:00", "11:00:00"), ("CNL", "11:20:00", "11:20:00")])
    files = {
        "agency.txt": _csv([["agency_id", "agency_name", "agency_url", "agency_timezone"],
                            ["IE", "Irish Rail", "https://irishrail.ie", "Europe/Dublin"]]),
        "routes.txt": _csv([["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
                            ["R1", "IE", "", "Commuter", 2], ["R2", "IE", "", "InterCity", 2],
                            ["R3", "IE", "", "DART", 2]]),
        "calendar.txt": _csv([["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                               "sunday", "start_date", "end_date"], ["WK", 1, 1, 1, 1, 1, 1, 1, "20200101", "20991231"],
                              ["OLD", 1, 1, 1, 1, 1, 1, 1, "20200101", "20200101"]]),
        "stops.txt": _csv(stops), "shapes.txt": _csv(shapes), "trips.txt": _csv(trips), "stop_times.txt": _csv(st),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def build(raw, day=DAY):
    """statics._distill for this operator (statics imports Home Assistant), with the table for `day`."""
    cut = ir.IRISH_RAIL.static_rewrite(raw)
    d = distill(cut, stop_times=ir.IRISH_RAIL.static_stop_times)
    d["rail_shapes"], index = rail.shapes_indexed(cut)
    d["trip_shapes"] = rail.trip_shapes(cut, index, None)    # statics.py keeps every trip's with a static_table
    d["table"] = lib.read_timetable(cut, lib.COMMUTER, day)
    d["fetched_at"] = 1.0
    return d


API = [{"code": "MYNTH", "name": "Maynooth", "lat": LAT, "lon": -6.40},
       {"code": "ASHTN", "name": "Ashtown", "lat": LAT, "lon": -6.33},
       {"code": "CNLLY", "name": "Dublin Connolly", "lat": LAT, "lon": -6.25}]


def report(code, origin, delay, last=None, kind=None, status="R"):
    return {"code": code, "status": status, "lat": None, "lon": None, "date": DAY.isoformat(), "delay_s": delay,
            "last_location": last, "last_location_type": kind, "origin_time": origin}


class CutTests(unittest.TestCase):

    def test_keeps_the_commuter_trips_only(self):
        z = zipfile.ZipFile(io.BytesIO(ir.cut(make_zip())))
        rows = lambda n: list(__import__("csv").DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8")))
        self.assertEqual(sorted(r["trip_id"] for r in rows("trips.txt")), ["t100", "t101", "t102", "t103"])
        self.assertEqual({r["trip_id"] for r in rows("stop_times.txt")}, {"t100", "t101", "t102", "t103"})
        self.assertEqual(len(rows("stop_times.txt")), 12)
        self.assertEqual({r["shape_id"] for r in rows("shapes.txt")}, {"W", "WR", "WB"})
        self.assertEqual([r["route_id"] for r in rows("routes.txt")], ["R1"])
        self.assertEqual({r["stop_id"] for r in rows("stops.txt")}, {"MYN", "ASH", "CNL", "BRY"})
        self.assertEqual(len(rows("calendar.txt")), 2)

    def test_the_table_from_the_cut_equals_the_whole_zip(self):
        raw = make_zip()
        a = lib.read_timetable(raw, lib.COMMUTER, DAY)
        b = lib.read_timetable(ir.cut(raw), lib.COMMUTER, DAY)
        for k in ("trips", "calls", "dates"):
            self.assertEqual(a[k], b[k], k)
        self.assertEqual(sorted(b["trips"]), ["t100", "t101", "t102", "t103"])
        self.assertEqual(b["stop_names"]["CNL"], "Connolly")

    def test_commuter_trip(self):
        for code, want in (("P508", True), ("D509", True), (" p1 ", True), ("A700", False), ("B182", False),
                           ("E101", False), ("BUS1", False), ("", False)):
            self.assertEqual(ir.commuter_trip({"trip_short_name": code}), want, code)

    def test_static_table_is_today_in_dublin(self):
        t = ir.IRISH_RAIL.static_table(make_zip())
        self.assertEqual(t["consumer"], lib.COMMUTER)
        self.assertEqual(sorted(t["trips"]), ["t100", "t101", "t102", "t103"])
        self.assertEqual(t["dates"]["OLD"], [])
        today = lib.local_day(__import__("time").time())
        self.assertIn(today.isoformat(), t["dates"]["WK"])
        self.assertIn((today - dt.timedelta(days=1)).isoformat(), t["dates"]["WK"])


class StaticsTests(unittest.TestCase):
    """statics.py for this operator, through test_timetable's stubs of aiohttp and Home Assistant."""

    @classmethod
    def setUpClass(cls):
        import test_timetable  # noqa: F401 - stubs aiohttp and homeassistant.core where they are not installed
        cls.statics = load("statics")

    def test_distill_keeps_the_table_and_every_trips_shape(self):
        d = self.statics._distill(make_zip(), ir.IRISH_RAIL)
        self.assertEqual(sorted(d["table"]["trips"]), ["t100", "t101", "t102", "t103"])
        self.assertEqual(d["table"]["consumer"], "commuter")
        # t103 runs on no day near today: distill's `sched` leaves it out, the shapes keep it (the table spans a
        # week).
        self.assertNotIn("t103", d["sched"])
        self.assertEqual(sorted(d["trip_shapes"]), ["t100", "t101", "t102", "t103"])
        self.assertNotIn("t200", d["sched"])                      # the cut ran first
        self.assertEqual(len(d["rail_shapes"]), 2)                # W (WR is W reversed) and WB

    def test_other_operators_keep_sched_s_trips_only(self):
        op = ops.OPERATORS["metra"]
        d = self.statics._distill(make_zip(), op)
        self.assertNotIn("table", d)
        self.assertEqual(set(d["trip_shapes"]), set(d["sched"]) & set(d["trip_shapes"]))
        self.assertNotIn("t103", d["trip_shapes"])

    def test_a_cache_without_the_table_is_fetched_again(self):
        import os, tempfile, types
        folder = tempfile.mkdtemp()
        os.makedirs(os.path.join(folder, ".storage"))
        hass = types.SimpleNamespace(config=types.SimpleNamespace(path=lambda *a: os.path.join(folder, *a)))
        st = self.statics.StaticTimetable(hass, None, ir.IRISH_RAIL)
        self.assertEqual(st._path, os.path.join(folder, ".storage", "saw_gtfs_irish_rail.json"))
        d = self.statics._distill(make_zip(), ir.IRISH_RAIL)
        st._write(d)
        self.assertEqual(st._read()["table"]["consumer"], "commuter")
        del d["table"]
        st._write(d)
        self.assertIsNone(st._read())
        other = self.statics.StaticTimetable(hass, None, ops.OPERATORS["metra"])
        other._path = st._path
        self.assertIsNotNone(other._read())                       # no table asked for


class PlaceTests(unittest.TestCase):

    def setUp(self):
        self.line = runs_m.Line([[LAT, round(-6.40 + 0.01 * i, 2)] for i in range(16)])

    def test_calls_in_order_and_reversed(self):
        pts = [(LAT, -6.40), (LAT, -6.33), (LAT, -6.25)]
        fwd = runs_m.place_calls(self.line, False, pts)
        self.assertAlmostEqual(fwd[0], 0.0, places=3)
        self.assertLess(fwd[0], fwd[1])
        self.assertLess(fwd[1], fwd[2])
        back = runs_m.place_calls(self.line, True, pts[::-1])
        self.assertEqual([round(x) for x in back], [round(x) for x in fwd[::-1]])

    def test_a_call_may_not_go_far_back(self):
        # Going east, a call a little west of the one before it (a platform's point) is placed where it is; one far
        # west of it is not placed at all, never back along the line.
        s = runs_m.place_calls(self.line, False, [(LAT, -6.30), (LAT, -6.3005)])
        self.assertAlmostEqual(s[0] - s[1], 33.3, delta=0.5)
        s = runs_m.place_calls(self.line, False, [(LAT, -6.30), (LAT, -6.302)])    # ~133 m back: clamped
        self.assertAlmostEqual(s[0] - s[1], runs_m.BACK_M, places=3)
        s = runs_m.place_calls(self.line, False, [(LAT, -6.30), (LAT, -6.35)])
        self.assertIsNone(s[1])
        s = runs_m.place_calls(self.line, True, [(LAT, -6.35), (LAT, -6.3495)])
        self.assertAlmostEqual(s[1] - s[0], 33.3, delta=0.5)
        s = runs_m.place_calls(self.line, True, [(LAT, -6.35), (LAT, -6.30)])
        self.assertIsNone(s[1])

    def test_off_the_shape_or_unknown_is_none(self):
        s = runs_m.place_calls(self.line, False, [(LAT, -6.40), None, (LAT + 0.009, -6.33), (LAT, -6.25)])
        self.assertIsNotNone(s[0])
        self.assertIsNone(s[1])
        self.assertIsNone(s[2])
        self.assertIsNotNone(s[3])
        near = runs_m.place_calls(self.line, False, [(LAT + 0.004, -6.33)])   # ~445 m off
        self.assertIsNotNone(near[0])

    def test_way(self):
        self.assertEqual(runs_m.way([0.0, 10.0, 20.0], 0), 1.0)
        self.assertEqual(runs_m.way([20.0, 10.0, 0.0], 1), -1.0)
        self.assertEqual(runs_m.way([0.0, 10.0, None], 1), 1.0)      # from the one before
        self.assertEqual(runs_m.way([20.0, 10.0, None], 1), -1.0)
        self.assertEqual(runs_m.way([5.0, 5.0], 0), 0.0)
        self.assertEqual(runs_m.way([None, 5.0], 0), 0.0)

    def test_path_along(self):
        p = runs_m.path_along(self.line, (LAT, -6.395), (LAT, -6.345))
        self.assertEqual(p[0], [LAT, -6.395])
        self.assertEqual(p[-1], [LAT, -6.345])
        self.assertIsNone(runs_m.path_along(self.line, (LAT, -6.39), (LAT, -6.39)))
        self.assertIsNone(runs_m.path_along(self.line, (LAT, -6.39), (LAT, -6.39001)))   # under MIN_MOVE_M
        self.assertIsNone(runs_m.path_along(self.line, (LAT + 0.001, -6.39), (LAT, -6.35)))   # ~111 m off


class RunTests(unittest.TestCase):

    def setUp(self):
        self.d = build(make_zip())
        self.r = runs_m.IrishRuns()

    def row(self, now, trains=(), key="P100-10", d=None):
        rows = self.r.poll(list(trains), API, 1, d or self.d, now)
        return {x["key"]: x for x in rows}.get(key)

    def test_no_timetable_draws_nothing(self):
        self.assertEqual(self.r.poll([], API, 1, None, ts(7, 5)), [])
        self.assertEqual(self.r.skipped, {"no_timetable": 1})
        self.assertEqual(self.r.poll([], API, 1, {"table": {}}, ts(7, 5)), [])

    def test_waiting_at_its_origin(self):
        x = self.row(ts(6, 57))
        self.assertEqual((x["lat"], x["lon"]), (LAT, -6.40))
        self.assertEqual(x["state"], "standing")
        self.assertEqual(x["at"], ts(6, 57))            # now, while it waits
        self.assertFalse(x["moving"])
        self.assertAlmostEqual(x["course"], 90.0, delta=0.5)
        self.assertEqual(x["number"], "100")
        self.assertEqual(x["names"], ["Maynooth", "Ashtown", "Connolly"])
        self.assertEqual(x["next"], ("Ashtown", ts(7, 10)))
        self.assertIsNone(x["delay_s"])                 # never reported: no delay (D0)
        self.assertIsNone(self.row(ts(6, 54)))          # before PRE_DEPARTURE_S

    def test_running_along_the_shape_by_time(self):
        x = self.row(ts(7, 5))
        self.assertAlmostEqual(x["lon"], -6.365, places=4)
        self.assertAlmostEqual(x["lat"], LAT, places=6)
        self.assertEqual(x["at"], ts(7, 0))             # its departure from the call it left
        self.assertTrue(x["moving"])
        self.assertAlmostEqual(x["course"], 90.0, delta=0.5)
        self.assertIsNotNone(x["line"])
        x = self.row(ts(7, 2, 30))
        self.assertAlmostEqual(x["lon"], -6.3825, places=4)

    def test_at_the_instant_it_leaves_it_is_not_yet_moving(self):
        x = self.row(ts(7, 0))
        self.assertEqual(x["state"], "running")
        self.assertAlmostEqual(x["lon"], -6.40, places=5)
        self.assertFalse(x["moving"])
        x = self.row(ts(7, 0, 6))
        self.assertTrue(x["moving"])

    def test_the_delay_is_kept_at_the_last_call(self):
        self.row(ts(7, 5), [report("P100", ts(7, 0), 300)])
        x = self.row(ts(7, 26), [])
        self.assertIsNone(x["next"])
        self.assertEqual(x["state"], "standing")
        self.assertEqual(x["delay_s"], 300)
        self.assertEqual(x["at"], ts(7, 25))

    def test_standing_at_a_call(self):
        x = self.row(ts(7, 10, 30))
        self.assertAlmostEqual(x["lon"], -6.33, places=5)
        self.assertEqual(x["at"], ts(7, 10))            # its arrival there
        self.assertFalse(x["moving"])
        self.assertAlmostEqual(x["course"], 90.0, delta=0.5)
        self.assertEqual(x["next"], ("Connolly", ts(7, 20)))

    def test_at_its_last_call(self):
        x = self.row(ts(7, 22))
        self.assertAlmostEqual(x["lon"], -6.25, places=5)
        self.assertIsNone(x["next"])
        self.assertAlmostEqual(x["course"], 90.0, delta=0.5)   # the way it came
        self.assertIsNone(self.row(ts(7, 26)))           # gone after FINISHED

    def test_the_reversed_shape_runs_west(self):
        x = self.row(ts(8, 5), key="D101-10")
        self.assertEqual(self.d["trip_shapes"]["t101"][1], 1)
        self.assertAlmostEqual(x["lon"], -6.29, places=4)
        self.assertAlmostEqual(x["course"], 270.0, delta=0.5)
        self.assertTrue(x["moving"])

    def test_a_genuine_report_moves_the_run_by_its_delay(self):
        rep = report("P100", ts(7, 0), 300)
        x = self.row(ts(7, 10), [rep])
        self.assertAlmostEqual(x["lon"], -6.365, places=4)      # five minutes late: halfway at 07:10
        self.assertEqual(x["delay_s"], 300)
        self.assertEqual(x["at"], ts(7, 5))
        self.assertEqual(x["next"], ("Ashtown", ts(7, 15)))
        # Kept for the run when the next poll has no report.
        x = self.row(ts(7, 12, 30), [])
        self.assertEqual(x["delay_s"], 300)
        self.assertAlmostEqual(x["lon"], -6.3475, places=4)

    def test_a_report_of_another_run_is_not_believed(self):
        x = self.row(ts(7, 5), [report("P100", ts(6, 0), 300)])
        self.assertIsNone(x["delay_s"])
        self.assertAlmostEqual(x["lon"], -6.365, places=4)

    def test_the_last_location_is_a_floor(self):
        x = self.row(ts(7, 5), [report("P100", ts(7, 0), 0, last="ASHTN", kind="A")])
        self.assertAlmostEqual(x["lon"], -6.33, places=5)
        self.assertEqual(x["state"], "standing")

    def test_terminated_ends_the_run(self):
        self.assertIsNone(self.row(ts(7, 5), [report("P100", ts(7, 0), 0, status="T")]))

    def test_without_a_shape_it_is_held_at_the_call_it_left(self):
        d = build(make_zip())
        del d["trip_shapes"]["t100"]
        x = self.row(ts(7, 5), d=d)
        self.assertEqual((x["lat"], x["lon"]), (LAT, -6.40))
        self.assertIsNone(x["course"])
        self.assertIsNone(x["line"])
        self.assertFalse(x["moving"])
        self.assertEqual(self.r.unplaced, 1)

    def test_a_stretch_with_an_end_off_the_shape_is_held(self):
        d = build(make_zip(off_shape="ASH"))
        x = self.row(ts(7, 5), d=d)
        self.assertEqual((x["lat"], x["lon"]), (LAT, -6.40))   # held at Maynooth, on the shape
        self.assertIsNotNone(x["line"])
        self.assertFalse(x["moving"])
        self.assertTrue(x["held"])
        self.assertAlmostEqual(x["course"], 90.0, delta=0.5)   # toward Connolly, the next call placed
        self.assertEqual(self.r.unplaced, 1)
        x = self.row(ts(7, 15), d=d)                     # from Ashtown, itself off the shape: at its own point
        self.assertEqual((x["lat"], x["lon"]), (LAT + 0.009, -6.33))
        self.assertIsNone(x["line"])
        self.assertIsNone(x["course"])
        self.assertTrue(x["held"])
        x = self.row(ts(6, 57), d=d)                     # waiting at Maynooth: not held
        self.assertFalse(x["held"])
        self.assertEqual(self.r.unplaced, 0)

    def test_the_join_is_cached_per_station_list(self):
        self.r.poll([], API, 1, self.d, ts(7, 5))
        j = self.r._join
        self.assertEqual(j["ASHTN"], "ASH")
        self.assertEqual(j["CNLLY"], "CNL")
        self.r.poll([], API, 1, self.d, ts(7, 6))
        self.assertIs(self.r._join, j)
        self.r.poll([], API[:2], 2, self.d, ts(7, 7))
        self.assertIsNot(self.r._join, j)

    def test_caches_reset_with_a_new_timetable(self):
        self.r.poll([], API, 1, self.d, ts(7, 5))
        self.assertTrue(self.r._calls)
        d2 = build(make_zip())
        d2["fetched_at"] = 2.0
        self.r.poll([], API, 1, d2, ts(7, 5))
        self.assertEqual(set(self.r._lines), {self.d["trip_shapes"]["t100"][0]})
        self.assertEqual(len(self.r._calls), 1)


class PublishTests(unittest.TestCase):

    def setUp(self):
        self.d = build(make_zip())
        self.r = runs_m.IrishRuns()

    def go(self, now):
        rows = self.r.poll([], API, 1, self.d, now)
        rec = {"vehicle_id": "P100-10", "in_service": True, "latitude": rows[0]["lat"], "longitude": rows[0]["lon"],
               "marker_label": "100", "previous_latitude": 1.0, "previous_longitude": 2.0,
               "previous_observed_at": "x", "segment_duration_s": 30, "position_jump": True, "stalled": True,
               "fix_latitude": 1.0, "fix_longitude": 2.0, "track_path": [[0, 0], [1, 1]], "course_deg": 12.0,
               "icon_rotation_deg": 12.0, "icon_rotation_basis": "course"}
        other = {"vehicle_id": "X", "in_service": True, "latitude": 1.0, "longitude": 2.0, "stalled": True}
        nis = {"vehicle_id": "P100-10x", "in_service": False, "latitude": 1.0, "longitude": 2.0, "stalled": True}
        result = {"vehicles": {"P100-10": rec, "X": other, "P100-10x": nis}}
        n = self.r.publish(result)
        return n, rec, other, nis

    def test_a_no_fix_estimate(self):
        n, rec, other, nis = self.go(ts(7, 5))
        self.assertEqual(n, 1)
        self.assertEqual(rec["position_source"], "estimated")
        for k in ("previous_latitude", "previous_longitude", "previous_observed_at", "segment_duration_s",
                  "position_jump", "stalled", "fix_latitude", "fix_longitude", "track_path"):
            self.assertNotIn(k, rec, k)
        self.assertEqual(rec["observed_at"], "2026-11-10T07:00:00+00:00")
        self.assertEqual(rec["last_seen"], rec["observed_at"])
        self.assertAlmostEqual(rec["course_deg"], 90.0, delta=0.5)
        self.assertEqual(rec["icon_rotation_deg"], rec["course_deg"])
        self.assertEqual(rec["icon_rotation_basis"], "course")
        self.assertEqual(other["stalled"], True)          # not this run's
        self.assertNotIn("position_source", other)
        self.assertEqual(nis["stalled"], True)            # not in service

    def test_a_run_s_record_out_of_service_is_left_alone(self):
        self.r.poll([], API, 1, self.d, ts(7, 5))
        rec = {"vehicle_id": "P100-10", "in_service": False, "latitude": 1.0, "longitude": 2.0, "stalled": True}
        self.assertEqual(self.r.publish({"vehicles": {"P100-10": dict(rec)}}), 0)
        result = {"vehicles": {"P100-10": dict(rec)}}
        self.r.publish(result)
        self.assertEqual(result["vehicles"]["P100-10"], rec)
        self.assertEqual(self.r._last, {})

    def test_held_at_a_call(self):
        _, rec, _, _ = self.go(ts(7, 10, 30))
        self.assertNotIn("course_deg", rec)
        self.assertEqual(rec["icon_rotation_basis"], "held")
        self.assertAlmostEqual(rec["icon_rotation_deg"], 90.0, delta=0.5)
        self.assertEqual(rec["observed_at"], "2026-11-10T07:10:00+00:00")

    def test_no_bearing_no_rotation(self):
        del self.d["trip_shapes"]["t100"]
        _, rec, _, _ = self.go(ts(7, 5))
        for k in ("course_deg", "icon_rotation_deg", "icon_rotation_basis", "track_path"):
            self.assertNotIn(k, rec)
        self.assertEqual(rec["position_source"], "estimated")

    def test_track_path_from_the_position_published_last(self):
        _, first, _, _ = self.go(ts(7, 2))
        self.assertNotIn("track_path", first)
        _, rec, _, _ = self.go(ts(7, 5))
        p = rec["track_path"]
        self.assertEqual(p[0], [first["latitude"], first["longitude"]])
        self.assertEqual(p[-1], [rec["latitude"], rec["longitude"]])
        self.assertAlmostEqual(rec["longitude"], -6.365, places=4)

    def test_forgotten_when_it_leaves(self):
        self.go(ts(7, 2))
        self.r.publish({"vehicles": {}})
        self.assertEqual(self.r._last, {})
        _, rec, _, _ = self.go(ts(7, 5))
        self.assertNotIn("track_path", rec)


class LookTests(unittest.TestCase):

    def test_show_and_hover(self):
        self.assertEqual(ir.show("Connolly"), "Dublin Connolly")
        self.assertEqual(ir.show("Dublin Heuston"), "Dublin Heuston")
        self.assertEqual(ir.show("Cork (Kent)"), "Cork (Kent)")
        self.assertEqual(ir.hover("P508", ["Maynooth", "Ashtown", "Connolly"]),
                         "Irish Rail P508 · Maynooth–Dublin Connolly")
        self.assertEqual(ir.hover("D509", ["Connolly", "Maynooth"]), "Irish Rail D509 · Dublin Connolly–Maynooth")
        self.assertEqual(ir.hover("P1", []), "Irish Rail P1")

    def test_line_by_end_stations(self):
        cases = [("Midleton", "Cork (Kent)", "cork"), ("Cork (Kent)", "Cobh", "cork"), ("Cobh", "Mallow", "cork"),
                 ("Mallow", "Midleton", "cork"), ("Charleville", "Cork (Kent)", "cork"),
                 ("Maynooth", "Connolly", "western"), ("M3 Parkway", "Docklands", "western"),
                 ("Clonsilla", "M3 Parkway", "western"), ("Longford", "Dublin Pearse", "western"),
                 ("Connolly", "Mullingar", "western"), ("Maynooth", "Bray (Daly)", "western"),
                 ("Portlaoise", "Dublin Heuston", "south_western"),
                 ("Grand Canal Dock", "Hazelhatch and Celbridge", "south_western"),
                 ("Newbridge", "Grand Canal Dock", "south_western"), ("Dublin Heuston", "Kildare", "south_western"),
                 ("Hazelhatch and Celbridge", "Dublin Heuston", "south_western"),
                 ("Drogheda (MacBride)", "Grand Canal Dock", "northern"), ("Dundalk (Clarke)", "Bray (Daly)", "northern"),
                 ("Dun Laoghaire (Mallin)", "Dundalk (Clarke)", "northern"),
                 ("Bray (Daly)", "Connolly", "northern")]   # Lee's ruling: no end in any set
        for first, last, want in cases:
            self.assertEqual(ir.trip_line(first, last), want, (first, last))
        # Two lines at the two ends (none measured): the end that is not the hub's.
        self.assertEqual(ir.trip_line("Dublin Heuston", "Maynooth"), "western")
        self.assertEqual(ir.trip_line("Maynooth", "Dublin Heuston"), "western")

    def test_toward_the_hub(self):
        t = ir.toward_hub
        self.assertTrue(t(["Maynooth", "Ashtown", "Connolly"], 0, "standing"))
        self.assertTrue(t(["Maynooth", "Ashtown", "Connolly"], 1, "running"))
        self.assertFalse(t(["Connolly", "Ashtown", "Maynooth"], 0, "standing"))
        self.assertTrue(t(["M3 Parkway", "Clonsilla"], 0, "running"))              # toward Clonsilla
        self.assertFalse(t(["Clonsilla", "M3 Parkway"], 0, "running"))
        self.assertTrue(t(["Newbridge", "Kildare", "Grand Canal Dock"], 1, "running"))
        self.assertFalse(t(["Dublin Heuston", "Kildare", "Portlaoise"], 0, "running"))
        self.assertFalse(t(["Grand Canal Dock", "Tara Street", "Connolly", "Maynooth"], 0, "running"))
        self.assertTrue(t(["Bray (Daly)", "Connolly"], 0, "running"))
        self.assertTrue(t(["Midleton", "Cork (Kent)"], 0, "running"))
        self.assertFalse(t(["Cork (Kent)", "Cobh"], 0, "running"))
        # A through train flips after it LEAVES Connolly, Dublin Heuston or Cork (Kent).
        thru = ["Maynooth", "Ashtown", "Connolly", "Tara Street", "Bray (Daly)"]
        self.assertTrue(t(thru, 1, "running"))
        self.assertTrue(t(thru, 2, "standing"))
        self.assertFalse(t(thru, 2, "running"))
        self.assertFalse(t(thru, 3, "standing"))
        cork = ["Mallow", "Cork (Kent)", "Cobh"]
        self.assertTrue(t(cork, 1, "standing"))
        self.assertFalse(t(cork, 1, "running"))
        self.assertTrue(t(["Hazelhatch and Celbridge", "Dublin Heuston", "Connolly", "Drogheda (MacBride)"], 1,
                          "running"))        # the LAST flip station counts
        self.assertFalse(t(["Cobh", "Midleton"], 0, "running"))
        self.assertFalse(t([], 0, "running"))

    def test_the_looks(self):
        base_ = {"marker_ring_width": 2, "marker_label_outline_color": "none"}
        self.assertEqual(ir.look("northern", False), {**base_, "marker_color": "#1E9DD8", "marker_ring_color": "#FFFFFF",
                         "marker_label_color": "#FFFFFF", "marker_arrow_color": "#1E9DD8",
                         "marker_arrow_outline_color": "#FFFFFF"})
        self.assertEqual(ir.look("northern", True), {**base_, "marker_color": "#FFFFFF", "marker_ring_color": "#1E9DD8",
                         "marker_label_color": "#1E9DD8", "marker_arrow_color": "#FFFFFF",
                         "marker_arrow_outline_color": "#1E9DD8"})
        self.assertEqual(ir.look("cork", False)["marker_color"], "#7171A3")
        self.assertEqual(ir.look("cork", True)["marker_ring_color"], "#7171A3")
        self.assertNotIn("marker_inner_ring_color", ir.look("cork", False))
        band = {"marker_inner_ring_width": 3}
        self.assertEqual(ir.look("western", False), {**base_, **band, "marker_color": "#FDE709",
                         "marker_ring_color": "#000000", "marker_label_color": "#000000",
                         "marker_arrow_color": "#FDE709", "marker_arrow_outline_color": "#000000",
                         "marker_inner_ring_color": "#FFFDE7"})
        self.assertEqual(ir.look("western", True), {**base_, **band, "marker_color": "#000000",
                         "marker_ring_color": "#FDE709", "marker_label_color": "#FDE709",
                         "marker_arrow_color": "#000000", "marker_arrow_outline_color": "#FDE709",
                         "marker_inner_ring_color": "#FFFDE7"})
        self.assertEqual(ir.look("south_western", False)["marker_inner_ring_color"], "#F67320")
        self.assertEqual(ir.look("south_western", True)["marker_inner_ring_color"], "#F67320")
        self.assertEqual(ir.look("south_western", True)["marker_ring_color"], "#FBB042")

    def test_lateness(self):
        rec = {}
        ir.irish_decorate(rec, None, None)
        self.assertEqual(rec, {"late_threshold_min": 5, "very_late_threshold_min": 10})


class OperatorTests(unittest.TestCase):

    def test_registry(self):
        op = ops.OPERATORS["irish_rail"]
        self.assertIs(op, ir.IRISH_RAIL)
        self.assertEqual((op.name, op.short, op.regions), ("Irish Rail", "Irish Rail", ("IE",)))
        self.assertEqual(op.source, base.SOURCE_IRISH_RAIL)
        self.assertEqual(op.irish_rail_consumer, "commuter")
        self.assertFalse(op.needs_key)
        self.assertEqual(op.attribution, lib.ATTRIBUTION)
        self.assertEqual(op.terms_url, lib.NTA_URL)
        self.assertEqual(op.static_url, lib.STATIC_URL)
        self.assertIs(op.static_rewrite, ir.cut)
        self.assertIs(op.static_table, ir.table)
        self.assertIs(op.parse_stops, ir.irish_stops)
        self.assertIs(op.decorate, ir.irish_decorate)
        self.assertIsNone(op.styling)
        self.assertFalse(op.narn)
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertIsNone(op.max_fix_age_s)
        self.assertEqual(base.REGIONS["IE"], "Ireland")
        self.assertEqual([o.id for o in ops.operators_in("IE")], ["irish_rail"])
        for other in ops.OPERATORS.values():
            if other is not op:
                self.assertIsNone(other.irish_rail_consumer, other.id)
                self.assertIsNone(other.static_table, other.id)
                self.assertNotEqual(other.source, base.SOURCE_IRISH_RAIL, other.id)

    def test_manifest_asks_for_the_library_with_the_runs(self):
        m = json.loads((pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
                        / "manifest.json").read_text(encoding="utf-8"))
        # 0.2.35 since 2026-11-11: saw_livetrack.ns (NS, SSOT 15). 0.2.34 from 2026-11-11: the runs.
        self.assertIn("saw-livetrack[gtfs]>=0.2.35,<0.3", m["requirements"])

    def test_attributes_pass_the_band(self):
        self.assertIn("marker_inner_ring_color", attributes.PASSTHROUGH)
        self.assertIn("marker_inner_ring_width", attributes.PASSTHROUGH)


class EndToEndTests(unittest.TestCase):
    """As the coordinator runs one poll: IrishRuns.poll, parse, parse_stops, Fleet, apply_extras, decorate, publish."""

    def setUp(self):
        self.d = build(make_zip())
        self.r = runs_m.IrishRuns()
        self.fleet = Fleet(styling=ir.IRISH_RAIL.styling)

    def one(self, now, trains=()):
        op = ir.IRISH_RAIL
        rows = self.r.poll(list(trains), API, 1, self.d, now)
        obs, _ = poll.fresh_only(op.parse(rows), now, op.max_fix_age_s)
        nxt, delays, extras = op.parse_stops(rows, self.d, now)
        result = self.fleet.update(obs, now, next_stops=nxt, static=self.d, trip_delays=delays)
        poll.apply_extras(result, extras)
        poll.decorate_all(result, obs, self.d, op.decorate)
        result["estimated"] = self.r.publish(result)
        return result, {k: attributes.to_attributes(v, op.id) for k, v in result["vehicles"].items()}

    def test_a_western_train_toward_dublin(self):
        result, a = self.one(ts(7, 10), [report("P100", ts(7, 0), 400)])
        x = a["P100-10"]
        self.assertEqual(result["estimated"], 1)
        self.assertEqual(x["marker_label"], "100")
        self.assertEqual(x["line_name"], "Irish Rail P100 · Maynooth–Dublin Connolly")
        self.assertEqual(x["next_stop"], "Ashtown")
        self.assertEqual(x["delay_min"], 6)
        self.assertEqual(x["position_source"], "estimated")
        self.assertNotIn("fix_latitude", x)
        self.assertEqual((x["marker_color"], x["marker_ring_color"], x["marker_label_color"]),
                         ("#000000", "#FDE709", "#FDE709"))
        self.assertEqual((x["marker_inner_ring_color"], x["marker_inner_ring_width"]), ("#FFFDE7", 3))
        self.assertEqual((x["late_threshold_min"], x["very_late_threshold_min"]), (5, 10))
        self.assertEqual(x["operator"], "irish_rail")
        self.assertEqual(x["observed_at"], "2026-11-10T07:06:40+00:00")

    def test_a_through_train_flips_after_connolly(self):
        _, a = self.one(ts(9, 21))
        x = a["P102-10"]
        self.assertEqual(x["line_name"], "Irish Rail P102 · Maynooth–Bray (Daly)")
        self.assertEqual(x["marker_color"], "#000000")          # standing at Connolly: still toward
        _, a = self.one(ts(9, 25))
        self.assertEqual(a["P102-10"]["marker_color"], "#FDE709")   # left Connolly: leaving
        self.assertEqual(a["P102-10"]["next_stop"], "Bray (Daly)")

    def test_next_stop_shows_dublin_connolly(self):
        _, a = self.one(ts(7, 15))
        self.assertEqual(a["P100-10"]["next_stop"], "Dublin Connolly")
        self.assertNotIn("delay_min", a["P100-10"])

    def test_a_leaving_train(self):
        _, a = self.one(ts(8, 5))
        x = a["D101-10"]
        self.assertEqual((x["marker_color"], x["marker_ring_color"]), ("#FDE709", "#000000"))
        self.assertEqual(x["marker_label"], "101")
        self.assertAlmostEqual(x["course_deg"], 270.0, delta=0.5)


if __name__ == "__main__":
    unittest.main()

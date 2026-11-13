"""V/Line's commuter trains (SSOT 17): the registry entry, the route cut, the timetable extras and their view, the runs
read through saw_livetrack.vline, the next stop, direction, look and decoration, the key check, the shared client's copy.
Offline. Run from the repo root:  python -m unittest tests.test_vline
"""

import datetime as dt
import io
import json
import pathlib
import unittest
import urllib.error
import zipfile
from zoneinfo import ZoneInfo

from google.transit import gtfs_realtime_pb2

from _load import load

from saw_livetrack import vline as lib
from saw_livetrack.transport_vic import COMMUTER

ops = load("operators")
vl = load("operators.vline")
base = load("operators.base")
poll = load("poll")

MEL = ZoneInfo("Australia/Melbourne")
START = "20261113"
ORIGIN = dt.datetime(2026, 11, 13, 12, tzinfo=MEL).timestamp() - 43200.0
T = lambda h, m=0, s=0: ORIGIN + h * 3600 + m * 60 + s  # noqa: E731
HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
# The library's reference copy, in a LiveTrackCore clone (AmtrakerClient) beside this one; skipped without it.
LIB_REF = pathlib.Path(__file__).resolve().parents[2] / "AmtrakerClient" / "reference" / "shared_transport_vic.py"
GEL = "aus:vic:vic-01-GEL:"
LIVE = "01-GEL--1-T0-8751"          # the live id the timetable lacks
TWIN = "01-GEL--5-T0-8751"          # the timetable's trip for it, Friday's service
DOWN = "01-GEL--5-T0-8752"          # toward Melbourne

TIMETABLE = {
    "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n1,Transport Victoria,https://x,Australia/Melbourne\n",
    "routes.txt": "route_id,route_short_name,route_long_name,route_type,route_color\n"
                  "aus:vic:vic-01-GEL:,Geelong,Geelong - Melbourne,2,8F1A95\n"
                  "aus:vic:vic-01-WBL:,Geelong,Warrnambool - Melbourne via Colac & Geelong,2,8F1A95\n",
    "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nSSS,Southern Cross Station,-37.818,144.952\n"
                 "FSY,Footscray Station,-37.801,144.903\nGLG,Geelong Station,-38.144,144.355\n",
    # out of order on purpose
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                      "01-GEL--5-T0-8751,10:10:00,10:11:00,FSY,2\n01-GEL--5-T0-8751,10:00:00,10:00:00,SSS,1\n"
                      "01-GEL--5-T0-8751,11:05:00,11:05:00,GLG,3\n"
                      "01-GEL--5-T0-8752,12:00:00,12:00:00,GLG,1\n01-GEL--5-T0-8752,12:55:00,12:56:00,FSY,2\n"
                      "01-GEL--5-T0-8752,13:05:00,,SSS,3\n",
    "trips.txt": "route_id,service_id,trip_id,shape_id,direction_id\n"
                 "aus:vic:vic-01-GEL:,FRI,01-GEL--5-T0-8751,S1,0\naus:vic:vic-01-GEL:,FRI,01-GEL--5-T0-8752,S1,1\n"
                 "aus:vic:vic-01-GEL:,SAT,01-GEL--6-T0-8751,S1,x\n",
    "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                    "FRI,0,0,0,0,1,0,0,20261001,20261231\nSAT,0,0,0,0,0,1,0,20261001,20261231\n",
    "calendar_dates.txt": "service_id,date,exception_type\nSAT,20261114,2\nFRI,20261112,1\n",
}


def zip_of(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


def static():
    z = zip_of(TIMETABLE)
    ex = vl.extras(z, {}, {"S1": [0, 0]}, today=dt.date(2026, 11, 13))
    # As the coordinator reads it: through JSON (statics.py writes and reads the cache).
    return json.loads(json.dumps({"stops": {"SSS": "Southern Cross Station", "FSY": "Footscray Station",
                                            "GLG": "Geelong Station"}, "extras": ex}))


def positions(*rows):
    """Each: (trip, lat, lon, time[, route])."""
    f = gtfs_realtime_pb2.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, row in enumerate(rows):
        trip, lat, lon, ts = row[:4]
        e = f.entity.add()
        e.id = str(i)
        e.vehicle.trip.trip_id = trip
        e.vehicle.trip.start_date = START
        e.vehicle.trip.route_id = row[4] if len(row) > 4 else GEL
        if lat is not None:
            e.vehicle.position.latitude = lat
            e.vehicle.position.longitude = lon
        if ts is not None:
            e.vehicle.timestamp = int(ts)
    return f


def updates(trip, *stops):
    f = gtfs_realtime_pb2.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    e = f.entity.add()
    e.id = "u"
    e.trip_update.trip.trip_id = trip
    e.trip_update.trip.start_date = START
    for seq, delay in stops:
        s = e.trip_update.stop_time_update.add()
        s.stop_sequence = seq
        s.arrival.delay = delay
    return f


def reports(pos, upd, now, st=None):
    runs = lib.VLineRuns()
    return runs.update(pos, upd, now, vl.Timetable(static() if st is None else st))[0]


class Registry(unittest.TestCase):
    def test_the_entry(self):
        op = ops.OPERATORS["vline"]
        self.assertIs(op, vl.VLINE)
        self.assertEqual((op.id, op.name, op.short, op.regions), ("vline", "V/Line commuter", "V/Line", ("AU-VIC",)))
        self.assertEqual((op.source, op.transport_vic_consumer), (base.SOURCE_TRANSPORT_VIC, COMMUTER))
        self.assertEqual(base.REGIONS["AU-VIC"], "Australia — Victoria")
        self.assertIn("AU-VIC", ops.regions_in_use())
        self.assertIn(vl.VLINE, ops.operators_in("AU-VIC"))

    def test_settings(self):
        op = vl.VLINE
        self.assertTrue(op.needs_key)
        self.assertEqual(op.key_param, "KeyId")
        self.assertEqual((op.max_fix_age_s, op.stand_max_fix_age_s), (600.0, lib.ROW_GONE_TIMED_S))
        self.assertEqual(lib.ROW_GONE_TIMED_S, 120.0)
        self.assertTrue(op.static_window)
        self.assertFalse(op.narn)
        self.assertFalse(op.static_stop_times)
        self.assertIs(op.parse, vl.parse)
        self.assertIs(op.parse_stops, vl.vline_stops)
        self.assertIs(op.decorate, vl.decorate)
        self.assertIn("Transport Victoria", op.attribution)
        self.assertIn("not sponsored", op.attribution)

    def test_the_manifest_asks_for_0_2_38_or_later(self):
        # 0.2.39 since 2026-11-13 (Adelaide, SSOT 19); V/Line needs 0.2.38.
        m = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("saw-livetrack[gtfs]>=0.2.39,<0.3", m["requirements"])


class Cut(unittest.TestCase):
    def test_the_five_commuter_routes(self):
        for code in ("GEL", "BAT", "TRN", "BGO", "SER"):
            self.assertTrue(vl.commuter_route({"route_id": "aus:vic:vic-01-%s:" % code}), code)
        for code in ("SNH", "ART", "WBL", "ECH", "BDE", "ABY", "MBY", "SWL", "vPK"):
            self.assertFalse(vl.commuter_route({"route_id": "aus:vic:vic-01-%s:" % code}), code)
        self.assertFalse(vl.commuter_route({}))


class Extras(unittest.TestCase):
    def setUp(self):
        self.ex = vl.extras(zip_of(TIMETABLE), {}, {"S1": [4, 1]}, today=dt.date(2026, 11, 13))

    def test_routes(self):
        self.assertEqual(self.ex["route"][GEL], ["Geelong", "8F1A95", "Geelong - Melbourne"])

    def test_trips(self):
        self.assertEqual(self.ex["trip"][TWIN], [GEL, 4, 1, "0", "Southern Cross", "Geelong"])
        self.assertEqual(self.ex["trip"][DOWN][3], "1")
        self.assertNotIn("01-GEL--6-T0-8751", self.ex["trip"])   # no stop times: not kept

    def test_rows_in_order_with_both_times(self):
        self.assertEqual(self.ex["rows"][TWIN], [[1, "SSS", 36000, 36000], [2, "FSY", 36600, 36660], [3, "GLG", 39900, 39900]])
        self.assertEqual(self.ex["rows"][DOWN][-1], [3, "SSS", 47100, None])

    def test_the_days_each_service_runs(self):
        self.assertEqual(self.ex["runs"][TWIN], ["20261112", "20261113"])   # Thursday added, Friday
        days = vl.service_days(zip_of(TIMETABLE), [dt.date(2026, 11, 14)])
        self.assertNotIn("SAT", days)                                       # Saturday removed

    def test_a_service_outside_its_dates_runs_on_no_day(self):
        z = dict(TIMETABLE)
        z["calendar.txt"] = TIMETABLE["calendar.txt"].replace("FRI,0,0,0,0,1,0,0,20261001,20261231",
                                                              "FRI,0,0,0,0,1,0,0,20251001,20251231")
        z["calendar_dates.txt"] = "service_id,date,exception_type\n"
        self.assertEqual(vl.extras(zip_of(z), {}, {}, today=dt.date(2026, 11, 13))["runs"][TWIN], [])

    def test_a_bad_direction_is_none(self):
        z = dict(TIMETABLE)
        z["trips.txt"] = TIMETABLE["trips.txt"].replace("S1,1", "S1,2")
        self.assertIsNone(vl.extras(zip_of(z), {}, {}, today=dt.date(2026, 11, 13))["trip"][DOWN][3])

    def test_no_shape(self):
        self.assertEqual(vl.extras(zip_of(TIMETABLE), {}, {}, today=dt.date(2026, 11, 13))["trip"][TWIN][1:3], [-1, 0])


class View(unittest.TestCase):
    def test_the_four_names(self):
        st = static()
        v = vl.Timetable(st)
        self.assertIn(TWIN, v)
        self.assertNotIn(LIVE, v)
        self.assertEqual(sorted(v.twin_candidates()), [TWIN, DOWN])
        self.assertTrue(v.runs_on(TWIN, "20261113"))
        self.assertFalse(v.runs_on(TWIN, "20261114"))
        self.assertEqual(v.stop_rows(TWIN)[0], [1, "SSS", 36000, 36000])
        self.assertEqual(v.stop_rows("nope"), [])
        self.assertIs(v.token, st["extras"]["rows"])

    def test_no_timetable(self):
        v = vl.Timetable(None)
        self.assertNotIn(TWIN, v)
        self.assertEqual(list(v.twin_candidates()), [])
        self.assertFalse(v.runs_on(TWIN, START))


class ParseAndStops(unittest.TestCase):
    def test_a_live_id_the_timetable_lacks_takes_its_twin(self):
        reps = reports(positions((LIVE, -37.80, 144.90, T(10, 12))), updates(LIVE, (2, 120)), T(10, 12, 30))
        obs = vl.parse(reps)
        self.assertEqual(len(obs), 1)
        o = obs[0]
        self.assertEqual((o.vehicle_id, o.train, o.line, o.trip_id, o.in_service), ("8751-13", "8751", "GEL", TWIN, True))
        self.assertEqual(o.observed_at.timestamp(), T(10, 12))
        self.assertAlmostEqual(o.lat, -37.80, places=4)

    def test_next_stop_never_the_origin_with_the_delay(self):
        reps = reports(positions((LIVE, -37.81, 144.94, T(9, 58))), updates(LIVE, (1, 300)), T(9, 59))
        stops, delays, extras = vl.vline_stops(reps, static(), T(9, 59))
        self.assertEqual(stops, {TWIN: ("Footscray Station", T(10, 10) + 300)})
        self.assertEqual(delays, {TWIN: 300})
        self.assertEqual(extras, {})

    def test_a_stop_the_timetable_cannot_name_is_not_shown(self):
        st = static()
        del st["stops"]["FSY"]
        reps = reports(positions((LIVE, -37.81, 144.94, T(9, 58))), updates(LIVE, (1, 300)), T(9, 59), st=st)
        stops, delays, _ = vl.vline_stops(reps, st, T(9, 59))
        self.assertEqual((stops, delays), ({}, {TWIN: 300}))

    def test_no_delay_said_without_one(self):
        reps = reports(positions((LIVE, -37.81, 144.94, T(9, 58))), None, T(9, 59))
        stops, delays, _ = vl.vline_stops(reps, static(), T(9, 59))
        self.assertEqual((stops[TWIN][0], delays), ("Footscray Station", {}))

    def test_no_timetable_no_stop_but_still_drawn(self):
        reps = reports(positions((LIVE, -37.81, 144.94, T(9, 58))), None, T(9, 59), st={})
        self.assertEqual(vl.vline_stops(reps, {}, T(9, 59)), ({}, {}, {}))
        obs = vl.parse(reps)
        self.assertEqual((len(obs), obs[0].trip_id), (1, LIVE))

    def test_a_held_run_is_drawn_at_its_last_fix_then_refused_by_age(self):
        runs = lib.VLineRuns()
        st = static()
        runs.update(positions((LIVE, -37.80, 144.90, T(10, 12))), None, T(10, 12), vl.Timetable(st))
        reps, skipped = runs.update(positions(), None, T(10, 15), vl.Timetable(st))
        self.assertEqual((skipped, [r.held for r in reps]), ({"held": 1}, [True]))
        kept, refused = poll.fresh_only(vl.parse(reps), T(10, 15), vl.VLINE.max_fix_age_s)
        self.assertEqual((len(kept), refused), (1, 0))
        reps, _ = runs.update(positions(), None, T(10, 22, 1), vl.Timetable(st))
        kept, refused = poll.fresh_only(vl.parse(reps), T(10, 22, 1), vl.VLINE.max_fix_age_s)
        self.assertEqual((len(reps), len(kept), refused), (1, 0, 1))

    def test_a_run_with_no_fix_is_not_drawn(self):
        r = lib.Run(LIVE, START, "8751", GEL)
        self.assertEqual(vl.parse([lib.Report("8751-13", r, True)]), [])
        self.assertEqual(vl.parse(None), [])


class LookAndDecorate(unittest.TestCase):
    def rec(self):
        return {"latitude": -37.80, "longitude": 144.90}

    def test_direction(self):
        self.assertIs(vl.toward_melbourne([GEL, 0, 0, "1"]), True)
        self.assertIs(vl.toward_melbourne([GEL, 0, 0, "0"]), False)
        self.assertIsNone(vl.toward_melbourne([GEL, 0, 0, None]))
        self.assertIsNone(vl.toward_melbourne(None))

    def test_the_look(self):
        leaving = vl.look(False)
        self.assertEqual((leaving["marker_color"], leaving["marker_ring_color"], leaving["marker_label_color"],
                          leaving["marker_label_outline_color"]), ("#902095", "#FFFFFF", "#FFFFFF", "#902095"))
        toward = vl.look(True)
        self.assertEqual((toward["marker_color"], toward["marker_ring_color"], toward["marker_label_color"],
                          toward["marker_label_outline_color"]), ("#FFFFFF", "#902095", "#902095", "#FFFFFF"))
        self.assertEqual(vl.look(None), leaving)
        self.assertEqual(leaving["marker_ring_width"], 3)

    def test_decorate(self):
        st = static()
        o = vl.parse(reports(positions((LIVE, -37.80, 144.90, T(10, 12))), None, T(10, 12)))[0]
        rec = self.rec()
        vl.decorate(rec, o, st)
        self.assertEqual(rec["marker_label"], "GEL")
        self.assertEqual(rec["line_name"], "Train 8751 · Geelong - Melbourne")
        self.assertEqual((rec["late_threshold_min"], rec["very_late_threshold_min"]), (6, 12))
        self.assertEqual(rec["marker_color"], "#902095")     # direction_id 0: leaving
        st["extras"]["trip"][TWIN][3] = "1"
        rec = self.rec()
        vl.decorate(rec, o, st)
        self.assertEqual(rec["marker_color"], "#FFFFFF")

    def test_decorate_without_a_timetable(self):
        o = vl.parse(reports(positions((LIVE, -37.80, 144.90, T(10, 12))), None, T(10, 12), st={}))[0]
        rec = self.rec()
        vl.decorate(rec, o, None)
        self.assertEqual((rec["marker_label"], rec["line_name"], rec["marker_color"]), ("GEL", "Train 8751", "#902095"))
        self.assertNotIn("icon_rotation_deg", rec)


class Opener:
    """Answers both V/Line feeds with `code` (200: an empty FeedMessage)."""

    def __init__(self, code):
        self.code, self.headers = code, []

    def __call__(self, req, timeout=None):
        self.headers.append(dict(req.header_items()))
        if self.code != 200:
            raise urllib.error.HTTPError(req.full_url, self.code, "x", {}, None)
        body = gtfs_realtime_pb2.FeedMessage()
        body.header.gtfs_realtime_version = "2.0"
        raw = body.SerializeToString()

        class R:
            status = 200
            headers = {}

            def read(self, n=None):
                return raw

            def close(self):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        return R()


class KeyCheck(unittest.TestCase):
    def test_accepted_with_the_key_in_the_header(self):
        op = Opener(200)
        self.assertIsNone(vl.check_key(" k ", op))
        self.assertTrue(any(h.get("Keyid") == "k" for h in op.headers))

    def test_refused(self):
        self.assertEqual(vl.check_key("k", Opener(401)), "invalid_key")
        self.assertEqual(vl.check_key("k", Opener(403)), "invalid_key")

    def test_unreachable(self):
        self.assertEqual(vl.check_key("k", Opener(500)), "cannot_connect")

    def test_empty(self):
        self.assertEqual(vl.check_key("  ", Opener(200)), "invalid_key")
        self.assertEqual(vl.check_key(None, Opener(200)), "invalid_key")


class SharedCopy(unittest.TestCase):
    def test_shared_client_copy_is_byte_exact(self):
        here = (HERE / "shared_transport_vic.py").read_bytes()
        if LIB_REF.exists():
            self.assertEqual(here, LIB_REF.read_bytes())
        self.assertIn(b"def get_shared_transport_vic_client(", here)


class CoordinatorWiring(unittest.TestCase):
    """The coordinator reads like the others: its source text (it imports Home Assistant)."""

    def test_the_branch(self):
        src = (HERE / "coordinator.py").read_text(encoding="utf-8")
        self.assertIn("get_shared_transport_vic_client(hass, op.transport_vic_consumer", src)
        self.assertIn("whole = client.feed_newest(consumer)", src)
        self.assertIn("VLineTimetable(self._static_data()), whole)", src)
        self.assertIn("release_shared_transport_vic_client(self.hass, self.operator.transport_vic_consumer)", src)
        self.assertIn("SOURCE_TRANSPORT_VIC)\n                and feed.header.HasField", src)


if __name__ == "__main__":
    unittest.main()

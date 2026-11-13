"""NSW TrainLink's Intercity trains (SSOT 16): run and identity, parse, the timetable extras, direction and look, the
decoration, finished runs, the key check and the registry. Offline.
Run from the repo root:  python -m unittest tests.test_nsw
"""

import datetime as dt
import hashlib
import io
import pathlib
import unittest
import urllib.error
import zipfile
from zoneinfo import ZoneInfo

from google.transit import gtfs_realtime_pb2

from _load import load

ops = load("operators")
nsw = load("operators.nsw_trainlink")
base = load("operators.base")

SYD = ZoneInfo("Australia/Sydney")
# Friday 2026-11-13 13:30 in Sydney.
NOW = dt.datetime(2026, 11, 13, 13, 30, tzinfo=SYD).timestamp()
HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
# The library's reference copy, in a LiveTrackCore clone (AmtrakerClient) beside this one; skipped without it.
LIB_REF = pathlib.Path(__file__).resolve().parents[2] / "AmtrakerClient" / "reference" / "shared_tfnsw.py"


def feed(*vehicles):
    f = gtfs_realtime_pb2.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    f.header.timestamp = int(NOW)
    for i, v in enumerate(vehicles):
        e = f.entity.add()
        e.id = str(i)
        if v is None:
            continue
        trip, route, start, lat, lon = v
        veh = e.vehicle
        if trip is not None:
            veh.trip.trip_id = trip
            veh.trip.route_id = route
            veh.trip.start_date = start
        if lat is not None:
            veh.position.latitude = lat
            veh.position.longitude = lon
        veh.timestamp = int(NOW) - 60
    return f


def zip_of(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


TIMETABLE = {
    "routes.txt": "route_id,route_short_name,route_long_name,route_color,route_type\n"
                  "4T.T.SCO,SCO,South Coast Line,005aa3,100\n4T.T.HUN,HUN,Hunter Line,,100\n",
    "stops.txt": "stop_id,stop_name,parent_station\nKMA,Kiama Station,\nKMA1,Kiama Station Platform 1,KMA\n"
                 "BMD,Bomaderry Station,\nBMD2,Bomaderry Station Platform 2,BMD\nGER,Gerringong Station,\n",
    # KN56 listed out of order on purpose; KN99 is not in `sched`.
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                      "KN56.x,13:40:00,13:41:00,GER,2\nKN56.x,13:16:00,13:16:00,BMD2,1\n"
                      "KN56.x,13:52:00,13:55:00,KMA1,3\nKN99.x,08:00:00,08:00:00,KMA,1\n"
                      "HM1.x,24:10:00,24:10:00,KMA,1\nHM1.x,24:50:00,,BMD,2\n"
                      "BAD.x,09:00:00,09:00:00,KMA,1\n",
    "trips.txt": "trip_id,route_id,shape_id,direction_id\nKN56.x,4T.T.SCO,S1,1\nKN99.x,4T.T.SCO,S1,0\n"
                 "HM1.x,4T.T.HUN,S9,\nBAD.x,4T.T.SCO,S1,x\n",
}


class RunAndIdentity(unittest.TestCase):
    def test_run_is_the_trip_ids_first_field(self):
        self.assertEqual(nsw.run_of("KN56.131126.16.N.2.1316"), "KN56")
        self.assertEqual(nsw.run_of(" SN47.1421.149.64.N.2.92126706 "), "SN47")
        self.assertEqual(nsw.run_of("V741"), "V741")

    def test_not_a_run(self):
        for bad in (None, 5, "", ".x", "K.x", "TOOLONGRUN9.x", "KN-56.x"):
            self.assertIsNone(nsw.run_of(bad), bad)

    def test_identity_from_the_run_date(self):
        self.assertEqual(nsw.identity("KN56", "20261113", NOW), "KN56-13")
        self.assertEqual(nsw.identity("KN56", "20261101", NOW), "KN56-1")

    def test_identity_without_a_date_takes_sydneys_day(self):
        # 2026-11-13 00:30 in Sydney is still the 12th in UTC.
        early = dt.datetime(2026, 11, 13, 0, 30, tzinfo=SYD).timestamp()
        self.assertEqual(nsw.identity("KN56", "", early), "KN56-13")
        self.assertEqual(nsw.identity("KN56", "2026111", early), "KN56-13")
        self.assertEqual(nsw.identity("KN56", None, early), "KN56-13")

    def test_line(self):
        self.assertEqual(nsw.line_of("4T.T.SCO"), "SCO")
        self.assertIsNone(nsw.line_of("4T.T."))
        self.assertIsNone(nsw.line_of("SCO_1a"))
        self.assertIsNone(nsw.line_of(None))


class Parse(unittest.TestCase):
    def setUp(self):
        self._clock = nsw.clock
        nsw.clock = lambda: NOW

    def tearDown(self):
        nsw.clock = self._clock

    def test_parse(self):
        f = feed(("KN56.131126.16.N.2.1316", "4T.T.SCO", "20261113", -34.8, 150.67),
                 None,                                                   # no vehicle
                 (None, None, None, -34.8, 150.67),                      # no trip
                 ("SN47.x", "4T.T.SHL", "20261113", None, None),         # no position
                 ("bad-run.x", "4T.T.SHL", "20261113", -34.1, 150.6))    # not a run
        obs = nsw.parse(f)
        self.assertEqual(len(obs), 1)
        o = obs[0]
        self.assertEqual(o.vehicle_id, "KN56-13")
        self.assertEqual(o.train, "KN56")
        self.assertEqual(o.line, "SCO")
        self.assertEqual(o.trip_id, "KN56.131126.16.N.2.1316")
        self.assertTrue(o.in_service)
        self.assertIsNone(o.reported_course)
        self.assertAlmostEqual(o.lat, -34.8, places=4)
        self.assertEqual(int(nsw.epoch(o.observed_at)), int(NOW) - 60)


class Extras(unittest.TestCase):
    def setUp(self):
        sched = {"KN56.x": {}, "HM1.x": {}, "BAD.x": {}}
        self.ex = nsw.extras(zip_of(TIMETABLE), {"sched": sched}, {"S1": [4, 1]})

    def test_routes(self):
        self.assertEqual(self.ex["route"]["4T.T.SCO"], ["SCO", "#005AA3", "South Coast Line"])
        self.assertIsNone(self.ex["route"]["4T.T.HUN"][1])

    def test_trip_row(self):
        # Ends by sequence, not by file order; parent station names, " Station" dropped.
        self.assertEqual(self.ex["trip"]["KN56.x"],
                         ["4T.T.SCO", 4, 1, "1", 13 * 3600 + 16 * 60, 13 * 3600 + 52 * 60, "Bomaderry", "Kiama",
                          1, "BMD2"])

    def test_unknown_shape_and_direction_and_no_departure(self):
        row = self.ex["trip"]["HM1.x"]
        self.assertEqual(row[1:4], [-1, 0, None])
        # The last stop has no departure: its arrival is the run's end.
        self.assertEqual(row[5], 24 * 3600 + 50 * 60)

    def test_trips_outside_sched_are_left_out(self):
        self.assertNotIn("KN99.x", self.ex["trip"])

    def test_a_direction_that_is_not_0_or_1_is_unknown(self):
        self.assertIsNone(self.ex["trip"]["BAD.x"][3])

    def test_the_end_is_the_last_stops_arrival_not_its_departure(self):
        self.assertEqual(self.ex["trip"]["KN56.x"][5], 13 * 3600 + 52 * 60)


class DirectionAndLook(unittest.TestCase):
    def test_toward(self):
        self.assertTrue(nsw.toward_sydney(["r", 0, 0, "1"]))
        self.assertFalse(nsw.toward_sydney(["r", 0, 0, "0"]))
        self.assertIsNone(nsw.toward_sydney(["r", 0, 0, None]))
        self.assertIsNone(nsw.toward_sydney(["r", 0, 0]))
        self.assertIsNone(nsw.toward_sydney(None))

    def test_leaving_is_filled(self):
        k = nsw.look("#005AA3", False)
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]),
                         ("#005AA3", "#FFFFFF", "#FFFFFF"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#005AA3", "#FFFFFF"))
        self.assertEqual(k["marker_ring_width"], 3)
        self.assertEqual(k["marker_label_outline_color"], "none")

    def test_toward_is_swapped(self):
        k = nsw.look("#005AA3", True)
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]),
                         ("#FFFFFF", "#005AA3", "#005AA3"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#FFFFFF", "#005AA3"))

    def test_unknown_leaves_and_no_colour_is_orange(self):
        self.assertEqual(nsw.look("#005AA3", None), nsw.look("#005AA3", False))
        self.assertEqual(nsw.look(None, False)["marker_color"], "#F6891F")


def _obs(trip="KN56.x", train="KN56", line="SCO"):
    return base.Obs(vehicle_id="KN56-13", lat=-34.8, lon=150.67, observed_at=None, in_service=True, train=train,
                    line=line, reported_course=None, trip_id=trip)


class Decorate(unittest.TestCase):
    def setUp(self):
        self.static = {"extras": {"route": {"4T.T.SCO": ["SCO", "#005AA3", "South Coast Line"]},
                                  "trip": {"KN56.x": ["4T.T.SCO", 4, 1, "0", 0, 1, "Bomaderry", "Kiama"],
                                           "NOSHAPE.x": ["4T.T.SCO", -1, 0, "1", 0, 1, "", "Kiama"]}}}
        self._course = nsw.shape_course
        self.calls = []

        def fake(static, lines, lat, lon):
            self.calls.append((lines, lat, lon))
            return 42.0
        nsw.shape_course = fake

    def tearDown(self):
        nsw.shape_course = self._course

    def rec(self, **kw):
        return {"latitude": -34.8, "longitude": 150.67, "position_jump": True, **kw}

    def test_label_hover_lateness_look(self):
        r = self.rec()
        nsw.decorate(r, _obs(), self.static)
        self.assertNotIn("position_jump", r)
        self.assertEqual(r["marker_label"], "SCO")
        self.assertEqual(r["line_name"], "Train KN56 · Bomaderry–Kiama")
        self.assertEqual((r["late_threshold_min"], r["very_late_threshold_min"]), (6, 12))
        self.assertEqual(r["marker_color"], "#005AA3")

    def test_next_stop_names_the_station(self):
        r = self.rec(next_stop="Berry Station Platform 1")
        nsw.decorate(r, _obs(), self.static)
        self.assertEqual(r["next_stop"], "Berry Station")
        r = self.rec(next_stop="Central Station")
        nsw.decorate(r, _obs(), self.static)
        self.assertEqual(r["next_stop"], "Central Station")
        self.assertEqual(nsw.station_name("Platform 2 Road Platform 2"), "Platform 2 Road")
        # Only the trailing platform goes.
        self.assertEqual(nsw.station_name("Old Platform 9 Halt Platform 1"), "Old Platform 9 Halt")
        # 124 of TfNSW's names carry a comma (seen live: "Mittagong Station,").
        r = self.rec(next_stop="Mittagong Station, Platform 1")
        nsw.decorate(r, _obs(), self.static)
        self.assertEqual(r["next_stop"], "Mittagong Station")
        self.assertEqual(nsw.station_name("Mittagong Station, Regent St"), "Mittagong Station, Regent St")
        r = self.rec()
        nsw.decorate(r, _obs(), self.static)
        self.assertNotIn("next_stop", r)

    def test_arrow_from_the_shape(self):
        r = self.rec(course_deg=200.0)
        nsw.decorate(r, _obs(), self.static)
        self.assertEqual(self.calls, [([[4, 1]], -34.8, 150.67)])
        self.assertEqual((r["course_deg"], r["icon_rotation_basis"], r["icon_rotation_deg"]), (42.0, "course", 42.0))

    def test_arrow_held_at_rest(self):
        r = self.rec()
        nsw.decorate(r, _obs(), self.static)
        self.assertNotIn("course_deg", r)
        self.assertEqual((r["icon_rotation_basis"], r["icon_rotation_deg"]), ("held", 42.0))

    def test_no_arrow_without_a_shape_or_a_course(self):
        r = self.rec()
        nsw.decorate(r, _obs(trip="NOSHAPE.x"), self.static)
        self.assertEqual(self.calls, [])
        self.assertNotIn("icon_rotation_basis", r)
        self.assertEqual(r["line_name"], "Train KN56")
        self.assertEqual(r["marker_color"], "#FFFFFF")
        nsw.shape_course = lambda *a: None
        r = self.rec()
        nsw.decorate(r, _obs(), self.static)
        self.assertNotIn("icon_rotation_basis", r)

    def test_unknown_trip_falls_back_to_the_feed(self):
        r = self.rec()
        nsw.decorate(r, _obs(trip="OTHER.x", line="HUN"), None)
        self.assertEqual(r["marker_label"], "HUN")
        self.assertEqual(r["line_name"], "Train KN56")
        self.assertEqual(r["marker_color"], "#F6891F")
        r = self.rec()
        nsw.decorate(r, _obs(trip="OTHER.x", line=None, train=None), None)
        self.assertNotIn("marker_label", r)
        self.assertNotIn("line_name", r)


def _updates():
    tu = gtfs_realtime_pb2.FeedMessage()
    tu.header.gtfs_realtime_version = "2.0"
    e = tu.entity.add()
    e.id = "1"
    e.trip_update.trip.trip_id = "V945.x"
    for seq, sid in ((1, "NCI3"), (2, "WRH1"), (3, "BFD2")):
        u = e.trip_update.stop_time_update.add()
        u.stop_sequence, u.stop_id = seq, sid
    e2 = tu.entity.add()
    e2.id = "2"
    e2.trip_update.trip.trip_id = "BYID.x"
    for sid in ("A1", "B1"):
        e2.trip_update.stop_time_update.add().stop_id = sid
    e3 = tu.entity.add()
    e3.id = "3"
    e3.trip_update.trip.trip_id = "UNKNOWN.x"
    e3.trip_update.stop_time_update.add().stop_sequence = 1
    tu.entity.add().id = "4"          # no trip update at all
    return tu


class NeverTheOrigin(unittest.TestCase):
    static = {"extras": {"trip": {"V945.x": ["r", 0, 0, "0", 0, 1, "Newcastle Interchange", "Dungog", 1, "NCI3"],
                                  "BYID.x": ["r", 0, 0, "0", 0, 1, "a", "b", 7, "A1"]}}}

    def setUp(self):
        self._n, self._d = nsw.next_stops, nsw.stop_delays
        self.seen = []

        def fake_next(feed, static, now):
            self.seen.append(feed)
            return {"n": 1}

        nsw.next_stops = fake_next
        nsw.stop_delays = lambda feed, static, now: {"d": feed is self.seen[-1]}

    def tearDown(self):
        nsw.next_stops, nsw.stop_delays = self._n, self._d

    def calls(self, feed, i):
        return [(u.stop_sequence if u.HasField("stop_sequence") else None, u.stop_id)
                for u in feed.entity[i].trip_update.stop_time_update]

    def test_origin_taken_out_by_sequence_and_by_stop_id(self):
        tu = _updates()
        got = nsw.stops_from_updates(tu, self.static, NOW)
        self.assertEqual(got, ({"n": 1}, {"d": True}))
        cut = self.seen[0]
        self.assertEqual(self.calls(cut, 0), [(2, "WRH1"), (3, "BFD2")])
        self.assertEqual(self.calls(cut, 1), [(None, "B1")])
        # A trip the timetable does not know keeps every call.
        self.assertEqual(self.calls(cut, 2), [(1, "")])
        # The caller's feed is not changed.
        self.assertEqual(len(tu.entity[0].trip_update.stop_time_update), 3)

    def test_a_sequence_decides_over_a_matching_stop_id(self):
        u = gtfs_realtime_pb2.TripUpdate.StopTimeUpdate()
        u.stop_sequence, u.stop_id = 2, "NCI3"
        self.assertFalse(nsw.is_origin(u, self.static["extras"]["trip"]["V945.x"]))
        u = gtfs_realtime_pb2.TripUpdate.StopTimeUpdate()
        self.assertFalse(nsw.is_origin(u, ["r", 0, 0, "0", 0, 1, "a", "b", 7, ""]))
        self.assertFalse(nsw.is_origin(u, ["short"]))
        self.assertFalse(nsw.is_origin(u, None))
        # A row from before the origin was kept (8 fields) never decides, even with a sequence.
        u.stop_sequence = 1
        self.assertFalse(nsw.is_origin(u, ["r", 0, 0, "0", 0, 1, "a", "b"]))

    def test_no_timetable(self):
        nsw.stops_from_updates(_updates(), None, NOW)
        self.assertEqual(self.calls(self.seen[0], 0), [(1, "NCI3"), (2, "WRH1"), (3, "BFD2")])

    def test_registered(self):
        self.assertIs(ops.OPERATORS["nsw_trainlink"].stops_from_updates, nsw.stops_from_updates)


def _at(fixed, trip="KN56.x"):
    return base.Obs(vehicle_id="x", lat=0, lon=0, observed_at=fixed, in_service=True, train="KN56", line="SCO",
                    reported_course=None, trip_id=trip)


class Finished(unittest.TestCase):
    # KN56.x ends at 13:00 Sydney; NOW is 13:30.
    static = {"extras": {"trip": {"KN56.x": ["r", 0, 0, "0", 12 * 3600, 13 * 3600, "a", "b"],
                                  "LATE.x": ["r", 0, 0, "0", 12 * 3600, 13 * 3600 + 26 * 60, "a", "b"],
                                  "NIGHT.x": ["r", 0, 0, "0", 23 * 3600, 25 * 3600, "a", "b"]}}}

    def test_old_fix_after_the_end_is_dropped(self):
        old = dt.datetime.fromtimestamp(NOW - 301, dt.timezone.utc)
        self.assertEqual(nsw.drop_finished([_at(old)], self.static, NOW), [])

    def test_fresh_fix_after_the_end_is_kept(self):
        o = _at(dt.datetime.fromtimestamp(NOW - 299, dt.timezone.utc))
        self.assertEqual(nsw.drop_finished([o], self.static, NOW), [o])

    def test_old_fix_before_the_end_plus_grace_is_kept(self):
        # Ends 13:26; 13:30 is under 300 s past it.
        o = _at(NOW - 3600, "LATE.x")
        self.assertEqual(nsw.drop_finished([o], self.static, NOW), [o])

    def test_unknown_trip_no_time_no_timetable_kept(self):
        a, b = _at(NOW - 3600, "OTHER.x"), _at(None)
        self.assertEqual(nsw.drop_finished([a, b], self.static, NOW), [a, b])
        c = _at(NOW - 3600)
        self.assertEqual(nsw.drop_finished([c], None, NOW), [c])

    def test_service_day_past_midnight(self):
        # 00:30 on the 14th is 24:30 on the 13th's service day for a trip running 23:00-25:00.
        t = dt.datetime(2026, 11, 14, 0, 30, tzinfo=SYD).timestamp()
        self.assertEqual(nsw.service_seconds(t, 23 * 3600, 25 * 3600), 24 * 3600 + 30 * 60)
        self.assertEqual(nsw.service_seconds(t, 0, 3600), 30 * 60)
        self.assertEqual(nsw.service_seconds(t, None, None), 30 * 60)
        o = _at(t - 3600, "NIGHT.x")
        self.assertEqual(nsw.drop_finished([o], self.static, t), [o])

    def test_epoch(self):
        self.assertEqual(nsw.epoch(5), 5.0)
        self.assertIsNone(nsw.epoch(True))
        self.assertIsNone(nsw.epoch("5"))


class _Resp:
    def __init__(self, body):
        self.body, self.headers = body, {}

    def read(self, *a):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def opener_answering(code):
    body = gtfs_realtime_pb2.FeedMessage()
    body.header.gtfs_realtime_version = "2.0"
    raw = body.SerializeToString()
    seen = []

    def open_(req, timeout=None):
        seen.append(req)
        if code == 200:
            return _Resp(raw)
        raise urllib.error.HTTPError(req.full_url, code, "x", {}, None)
    open_.seen = seen
    return open_


class CheckKey(unittest.TestCase):
    def test_accepted(self):
        op = opener_answering(200)
        self.assertIsNone(nsw.check_key(" k ", op))
        self.assertEqual(op.seen[0].get_header("Authorization"), "apikey k")

    def test_refused(self):
        self.assertEqual(nsw.check_key("k", opener_answering(401)), "invalid_key")
        self.assertEqual(nsw.check_key("k", opener_answering(403)), "invalid_key")

    def test_other_failures(self):
        self.assertEqual(nsw.check_key("k", opener_answering(500)), "cannot_connect")
        self.assertEqual(nsw.check_key("k", opener_answering(429)), "cannot_connect")

    def test_blank(self):
        op = opener_answering(200)
        self.assertEqual(nsw.check_key("  ", op), "invalid_key")
        self.assertEqual(nsw.check_key(None, op), "invalid_key")
        self.assertEqual(op.seen, [])


class Registry(unittest.TestCase):
    def test_registered(self):
        op = ops.OPERATORS["nsw_trainlink"]
        self.assertIs(op, nsw.NSW_TRAINLINK)
        self.assertEqual(op.regions, ("AU-NSW",))
        self.assertEqual(ops.regions_in_use()["AU-NSW"], "Australia — New South Wales")
        self.assertIn(op, ops.operators_in("AU-NSW"))
        self.assertEqual((op.source, op.tfnsw_consumer), (base.SOURCE_TFNSW, "commuter"))
        self.assertTrue(op.needs_key)
        self.assertEqual(op.static_route_types, ("100",))
        self.assertTrue(op.static_window)
        self.assertFalse(op.narn)
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertIs(op.decorate, nsw.decorate)
        self.assertIs(op.obs_filter, nsw.drop_finished)
        self.assertIn("Transport for NSW", op.attribution)

    @unittest.skipUnless(LIB_REF.exists(), "LiveTrackCore clone not present")
    def test_shared_client_copy_is_byte_exact(self):
        mine = hashlib.sha256((HERE / "shared_tfnsw.py").read_bytes()).hexdigest()
        self.assertEqual(mine, hashlib.sha256(LIB_REF.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

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
    "trips.txt": "trip_id,route_id,shape_id,direction_id,trip_headsign\nKN56.x,4T.T.SCO,S1,1,Kiama\n"
                 "KN99.x,4T.T.SCO,S1,0,Bomaderry\nHM1.x,4T.T.HUN,S9,,Empty Train\nBAD.x,4T.T.SCO,S1,x,\n",
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
        self.assertIsNone(nsw.line_of(None))

    def test_line_from_sydney_trains(self):
        self.assertEqual(nsw.line_of("SCO_1a"), "SCO")
        self.assertEqual(nsw.line_of(" CCN_2b "), "CCN")
        for other in ("APS_1a", "CTY_NC1", "RTTA_DEF", "SCO", "SCO1a", "_1a", "WST_1a"):
            self.assertIsNone(nsw.line_of(other), other)


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
                          1, "BMD2", "Kiama"])

    def test_headsign_kept(self):
        self.assertEqual(self.ex["trip"]["HM1.x"][10], "Empty Train")
        self.assertEqual(self.ex["trip"]["BAD.x"][10], "")
        # A timetable without the column.
        tt = dict(TIMETABLE, **{"trips.txt": "trip_id,route_id,shape_id,direction_id\nKN56.x,4T.T.SCO,S1,1\n"})
        ex = nsw.extras(zip_of(tt), {"sched": {"KN56.x": {}}}, {})
        self.assertEqual(ex["trip"]["KN56.x"][10], "")

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

    def test_not_in_service_is_grey_nis_with_its_run(self):
        o = base.Obs(vehicle_id="E123-13", lat=-34.8, lon=150.67, observed_at=None, in_service=False, train=None,
                     line="SCO", reported_course=None, trip_id="KN56.x")
        r = self.rec(marker_label="NIS E123-13", next_stop="Kiama Station Platform 1")
        nsw.decorate(r, o, self.static)
        self.assertEqual(r["marker_label"], "NIS E123")
        self.assertEqual((r["marker_color"], r["marker_ring_color"], r["marker_label_color"]),
                         ("#808080", "#FFFFFF", "#FFFFFF"))
        self.assertEqual((r["marker_arrow_color"], r["marker_arrow_outline_color"]), ("#808080", "#FFFFFF"))
        self.assertEqual((r["marker_ring_width"], r["marker_label_outline_color"]), (3, "none"))
        for k in ("line_name", "late_threshold_min", "very_late_threshold_min", "position_jump"):
            self.assertNotIn(k, r)
        # Not this function's to tidy: Fleet never gives a train out of service a next stop.
        self.assertEqual(r["next_stop"], "Kiama Station Platform 1")
        # Never swapped toward Sydney (KN56.x runs away here; a toward trip looks the same).
        r2 = self.rec()
        self.static["extras"]["trip"]["KN56.x"][3] = "1"
        try:
            nsw.decorate(r2, o, self.static)
        finally:
            self.static["extras"]["trip"]["KN56.x"][3] = "0"
        self.assertEqual(r2["marker_color"], "#808080")
        # The arrow from its shape, as any train's.
        self.assertEqual(r["icon_rotation_deg"], 42.0)

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

    def test_a_late_run_ends_later(self):
        # Ends 13:00; at 13:30 with a fix 301 s old: 26 minutes late keeps it, 24 does not, early is on time.
        old = NOW - 301
        self.assertEqual(len(nsw.drop_finished([_at(old)], self.static, NOW, {"KN56.x": 26 * 60})), 1)
        self.assertEqual(len(nsw.drop_finished([_at(old)], self.static, NOW, {"KN56.x": 24 * 60})), 0)
        self.assertEqual(len(nsw.drop_finished([_at(old)], self.static, NOW, {"KN56.x": -3600})), 0)
        self.assertEqual(len(nsw.drop_finished([_at(old)], self.static, NOW, {"OTHER.x": 3600})), 0)
        # Running early never brings the end forward: LATE.x ends 13:26, under 300 s before 13:30.
        self.assertEqual(len(nsw.drop_finished([_at(NOW - 3600, "LATE.x")], self.static, NOW, {"LATE.x": -600})), 1)


def _late_updates(trip, delay):
    tu = gtfs_realtime_pb2.FeedMessage()
    tu.header.gtfs_realtime_version = "2.0"
    e = tu.entity.add()
    e.trip_update.trip.trip_id = trip
    e.trip_update.stop_time_update.add().arrival.delay = delay
    return tu


class Refine(unittest.TestCase):
    static = {"extras": {"trip": {"KN56.x": ["r", 0, 0, "0", 12 * 3600, 13 * 3600, "a", "b", 1, "A", "Kiama"],
                                  "E1.x": ["r", 0, 0, "0", 13 * 3600, 14 * 3600, "a", "b", 1, "A", "Empty Train"],
                                  "OLD.x": ["r", 0, 0, "0", 13 * 3600, 14 * 3600, "a", "b", 1, "A"]}}}

    def test_empty_trains_are_not_in_service(self):
        e, r, o = _at(NOW - 60, "E1.x"), _at(NOW - 60, "KN56.x"), _at(NOW - 60, "OLD.x")
        got = nsw.refine([e, r, o], self.static, NOW)
        self.assertEqual(len(got), 3)
        self.assertFalse(got[0].in_service)
        self.assertIsNone(got[0].train)
        self.assertEqual((got[0].trip_id, got[0].vehicle_id, got[0].line), ("E1.x", e.vehicle_id, e.line))
        self.assertIs(got[1], r)
        # A row from before the headsign was kept is never an Empty Train.
        self.assertIs(got[2], o)

    def test_finished_runs_dropped_with_their_delay(self):
        old = _at(NOW - 301, "KN56.x")
        self.assertEqual(nsw.refine([old], self.static, NOW), [])
        self.assertEqual(nsw.refine([old], self.static, NOW, updates=None), [])
        self.assertEqual(nsw.refine([old], self.static, NOW, updates=_late_updates("KN56.x", 30 * 60)), [old])

    def test_is_empty(self):
        self.assertTrue(nsw.is_empty(self.static["extras"]["trip"]["E1.x"]))
        self.assertFalse(nsw.is_empty(self.static["extras"]["trip"]["KN56.x"]))
        self.assertFalse(nsw.is_empty(self.static["extras"]["trip"]["OLD.x"]))
        self.assertFalse(nsw.is_empty(None))
        self.assertFalse(nsw.refine([], None, NOW))


SYD_TRIP = "C151.1421.149.64.H.8.92125932"     # Sydney Trains' id shape: run, service 1421.149.64, ...
NSW_TRIP = "KN56.131126.16.N.2.1316"            # nswtrains': run, run date 131126, ...


class SydneyCut(unittest.TestCase):
    def test_the_routes_the_client_hands_this_operator(self):
        keep = nsw.sydney_intercity
        for rid in ("CCN_1a", "BMT_2", "SCO_1b", "SHL_2e", "HUN_1a"):
            self.assertTrue(keep({"route_id": rid, "agency_id": "NSWTrains"}), rid)
        for rid, agency in (("APS_1a", "SydneyTrains"), ("T3_1", "SydneyTrains"), ("CTY_NC1", "NSWTrains"),
                            ("RTTA_DEF", "SydneyTrains"), ("", "NSWTrains")):
            self.assertFalse(keep({"route_id": rid, "agency_id": agency}), rid)
        self.assertFalse(keep({}))

    def test_an_unlisted_prefix_goes_by_its_agency(self):
        self.assertTrue(nsw.sydney_intercity({"route_id": "NEW_1", "agency_id": "NSWTrains"}))
        self.assertFalse(nsw.sydney_intercity({"route_id": "NEW_1", "agency_id": "SydneyTrains"}))
        self.assertFalse(nsw.sydney_intercity({"route_id": "NEW_1"}))


def _first():
    return {"v": 4, "tz": "Australia/Sydney", "fetched_at": 100.0, "feed_version": "nsw",
            "stops": {"S1": "Kiama Station, Platform 1", "A": "Gerringong Station"},
            "stop_pos": {"S1": [-34.67, 150.85], "A": [-34.74, 150.82]},
            "routes": {"4T.T.SCO": "South Coast Line"},
            "sched": {NSW_TRIP: {"A": 1}},
            "rail_shapes": [[[0, 0], [0, 1]], [[1, 0], [1, 1]]],
            "trip_shapes": {NSW_TRIP: [1, 0]},
            "extras": {"route": {"4T.T.SCO": ["SCO", "#005AA3", "South Coast Line"]},
                       "trip": {NSW_TRIP: ["4T.T.SCO", 1, 0, "0", 0, 1, "a", "b", 1, "A"]}}}


def _second():
    return {"v": 4, "tz": "Australia/Sydney", "fetched_at": 50.0,
            "stops": {"S1": "Kiama Station Platform 1", "B": "Central Station"},
            "stop_pos": {"S1": [-34.671, 150.851], "B": [-33.88, 151.21]},
            "routes": {"CCN_1a": "Central to Newcastle Interchange via Strathfield"},
            "sched": {SYD_TRIP: {"B": 2}},
            "stop_times": {SYD_TRIP: {"1": ["B", "13:00:00"]}},
            "trip_routes": {SYD_TRIP: "CCN_1a"},
            "rail_shapes": [[[2, 0], [2, 1]]],
            "trip_shapes": {SYD_TRIP: [0, 1], "NOLINE.x": [-1, 0]},
            "extras": {"route": {"CCN_1a": ["CCN", "#D11F2F", "Central to Newcastle Interchange"]},
                       "trip": {SYD_TRIP: ["CCN_1a", 0, 1, "1", 0, 1, "Central", "Newcastle Interchange", 1, "B",
                                           "Newcastle Interchange"],
                                "NOSHAPE.x": ["CCN_1a", -1, 0, None, 0, 1, "", "", 1, "B", "Empty Train"]}}}


class Merge(unittest.TestCase):
    def test_one_missing(self):
        a, b = _first(), _second()
        self.assertIsNone(nsw.merge(None, None))
        self.assertIs(nsw.merge(a, None), a)
        self.assertIs(nsw.merge(None, b), b)

    def test_trips_from_both_shapes_shifted(self):
        m = nsw.merge(_first(), _second())
        self.assertEqual(len(m["rail_shapes"]), 3)
        self.assertEqual(m["rail_shapes"][2], [[2, 0], [2, 1]])
        self.assertEqual(m["trip_shapes"], {NSW_TRIP: [1, 0], SYD_TRIP: [2, 1], "NOLINE.x": [-1, 0]})
        self.assertEqual(m["extras"]["trip"][SYD_TRIP][:3], ["CCN_1a", 2, 1])
        self.assertEqual(m["extras"]["trip"][SYD_TRIP][3:], _second()["extras"]["trip"][SYD_TRIP][3:])
        self.assertEqual(m["extras"]["trip"]["NOSHAPE.x"][1], -1)
        self.assertEqual(m["extras"]["trip"][NSW_TRIP], _first()["extras"]["trip"][NSW_TRIP])
        self.assertEqual(set(m["sched"]), {NSW_TRIP, SYD_TRIP})
        self.assertEqual(m["stop_times"], {SYD_TRIP: {"1": ["B", "13:00:00"]}})
        self.assertEqual(m["trip_routes"], {SYD_TRIP: "CCN_1a"})
        self.assertEqual(set(m["extras"]["route"]), {"4T.T.SCO", "CCN_1a"})
        self.assertEqual(set(m["routes"]), {"4T.T.SCO", "CCN_1a"})

    def test_a_shared_stop_keeps_nswtrains_entry(self):
        m = nsw.merge(_first(), _second())
        self.assertEqual(m["stops"]["S1"], "Kiama Station, Platform 1")
        self.assertEqual(m["stop_pos"]["S1"], [-34.67, 150.85])
        self.assertEqual(m["stops"]["B"], "Central Station")
        self.assertEqual(m["feed_version"], "nsw")

    def test_fetched_at_moves_when_either_moves(self):
        a, b = _first(), _second()
        self.assertEqual(nsw.merge(a, b)["fetched_at"], 150.0)
        b2 = dict(b, fetched_at=60.0)
        self.assertNotEqual(nsw.merge(a, b2)["fetched_at"], nsw.merge(a, b)["fetched_at"])
        # The first alone and the pair never share a token (an older second appearing still moves it).
        self.assertNotEqual(nsw.merge(a, b)["fetched_at"], a["fetched_at"])

    def test_inputs_untouched(self):
        a, b = _first(), _second()
        nsw.merge(a, b)
        self.assertEqual((a, b), (_first(), _second()))

    def test_without_stop_times_none_is_made(self):
        b = _second()
        del b["stop_times"], b["trip_routes"]
        m = nsw.merge(_first(), b)
        self.assertNotIn("stop_times", m)
        self.assertNotIn("trip_routes", m)


def _sydney_updates(trip=SYD_TRIP, stops=("B", "C", "D"), seq=0):
    tu = gtfs_realtime_pb2.FeedMessage()
    tu.header.gtfs_realtime_version = "2.0"
    e = tu.entity.add()
    e.id = "s"
    e.trip_update.trip.trip_id = trip
    e.trip_update.trip.start_date = "20261113"
    for i, sid in enumerate(stops):
        u = e.trip_update.stop_time_update.add()
        u.stop_id, u.stop_sequence = sid, seq
        u.arrival.delay = 60 * (i + 1)
    return tu


class SydneySequences(unittest.TestCase):
    static = {"stop_times": {SYD_TRIP: {"3": ["D", "13:20:00"], "1": ["B", "13:00:00"], "2": ["C", "13:10:00"],
                                        "x": ["Z", "?"], "4": []}},
              "extras": {"trip": {SYD_TRIP: ["CCN_1a", 0, 0, "0", 0, 1, "Central", "Gosford", 1, "B", "Gosford"]}}}

    def calls(self, feed):
        return [(u.stop_sequence, u.stop_id) for u in feed.entity[0].trip_update.stop_time_update]

    def test_rows_in_timetable_order(self):
        self.assertEqual(nsw.rows_of(self.static, SYD_TRIP), [(1, "B"), (2, "C"), (3, "D")])
        self.assertEqual(nsw.rows_of(self.static, "OTHER"), [])
        self.assertEqual(nsw.rows_of(None, SYD_TRIP), [])

    def test_sequences_filled_from_its_own_rows(self):
        tu = _sydney_updates()
        self.assertEqual(nsw.fill_sequences(tu, self.static), 3)
        self.assertEqual(self.calls(tu), [(1, "B"), (2, "C"), (3, "D")])

    def test_a_stop_it_cannot_place_goes(self):
        tu = _sydney_updates(stops=("B", "Q", "D"))
        self.assertEqual(nsw.fill_sequences(tu, self.static), 2)
        self.assertEqual(self.calls(tu), [(1, "B"), (3, "D")])
        tu = _sydney_updates(trip="C999.1421.149.64.H.8.1")
        self.assertEqual(nsw.fill_sequences(tu, self.static), 0)
        self.assertEqual(self.calls(tu), [])

    def test_nswtrains_trips_left_as_sent(self):
        tu = _sydney_updates(trip=NSW_TRIP, seq=7)
        self.assertEqual(nsw.fill_sequences(tu, self.static), 0)
        self.assertEqual(self.calls(tu), [(7, "B"), (7, "C"), (7, "D")])
        tu.entity.add().id = "no trip update"
        self.assertEqual(nsw.fill_sequences(tu, self.static), 0)

    def test_the_origin_found_after_the_fill(self):
        seen = []
        n, d = nsw.next_stops, nsw.stop_delays
        try:
            nsw.next_stops = lambda feed, static, now: seen.append(feed) or {}
            nsw.stop_delays = lambda feed, static, now: {}
            tu = _sydney_updates()
            nsw.stops_from_updates(tu, self.static, NOW)
        finally:
            nsw.next_stops, nsw.stop_delays = n, d
        self.assertEqual(self.calls(seen[0]), [(2, "C"), (3, "D")])
        # The caller's feed is not changed.
        self.assertEqual(self.calls(tu), [(0, "B"), (0, "C"), (0, "D")])

    def test_next_stop_and_lateness_from_delays_alone(self):
        # The real library: Sydney Trains' updates carry delays and no times; the rows give the scheduled times.
        static = {"v": 4, "tz": "Australia/Sydney", "stops": {"B": "Central Station Platform 1",
                                                              "C": "Strathfield Station Platform 3",
                                                              "D": "Hornsby Station Platform 2"},
                  "sched": {SYD_TRIP: {"B": 13 * 3600, "C": 13 * 3600 + 600, "D": 13 * 3600 + 1200}},
                  **{k: v for k, v in self.static.items()}}
        now = dt.datetime(2026, 11, 13, 13, 12, tzinfo=SYD).timestamp()
        nxt, late = nsw.stops_from_updates(_sydney_updates(), static, now)
        name, eta = nxt[SYD_TRIP]
        # C was due 13:10 + 2 min late = 13:12, not yet 30 s past: still next.
        self.assertEqual(name, "Strathfield Station Platform 3")
        self.assertEqual(eta, dt.datetime(2026, 11, 13, 13, 12, tzinfo=SYD).timestamp())
        self.assertEqual(late[SYD_TRIP], 120)
        # Unfilled, the first update listed (the origin, B, behind the train) would have been taken.
        self.assertEqual(nsw.next_stops(_sydney_updates(), static, now)[SYD_TRIP], ("Central Station Platform 1", None))


class LatestDelays(unittest.TestCase):
    def test_the_last_update_with_a_delay(self):
        tu = _sydney_updates()
        e = tu.entity.add()
        e.trip_update.trip.trip_id = NSW_TRIP
        u = e.trip_update.stop_time_update.add()
        u.departure.delay = 90
        e.trip_update.stop_time_update.add().stop_id = "no delay"
        e2 = tu.entity.add()
        e2.trip_update.trip.trip_id = "NODELAY.x"
        e2.trip_update.stop_time_update.add().stop_id = "A"
        tu.entity.add().id = "empty"
        self.assertEqual(nsw.latest_delays(tu), {SYD_TRIP: 180, NSW_TRIP: 90})
        self.assertEqual(nsw.latest_delays(None), {})

    def test_arrival_before_departure(self):
        tu = _sydney_updates(stops=("B",))
        tu.entity[0].trip_update.stop_time_update[0].departure.delay = 999
        self.assertEqual(nsw.latest_delays(tu), {SYD_TRIP: 60})


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
        self.assertIs(op.obs_filter, nsw.refine)
        self.assertTrue(op.obs_filter_updates)
        self.assertEqual(op.max_fix_age_s, 600.0)
        self.assertIn("Transport for NSW", op.attribution)

    def test_sydney_trains_asked_for_and_its_timetable_merged(self):
        op = ops.OPERATORS["nsw_trainlink"]
        self.assertTrue(op.tfnsw_sydney_trains)
        self.assertIsNone(op.tfnsw_timetable)
        self.assertIs(op.static_second, nsw.SYDNEY_CUT)
        self.assertIs(op.static_merge, nsw.merge)
        cut = nsw.SYDNEY_CUT
        self.assertEqual(cut.id, "nsw_trainlink_sydneytrains")
        self.assertEqual(cut.tfnsw_timetable, "sydneytrains")
        self.assertTrue(cut.static_url.endswith("/schedule/sydneytrains"))
        self.assertTrue(cut.static_window)
        self.assertIsNone(cut.static_route_types)
        self.assertIsNone(cut.static_route_prefixes)
        self.assertIs(cut.static_route_keep, nsw.sydney_intercity)
        self.assertTrue(cut.static_stop_times)
        self.assertIs(cut.static_extras, nsw.extras)
        self.assertGreaterEqual(cut.static_max_bytes, 64 * 1024 * 1024)
        # Never an entry of its own; nobody else asks or merges.
        self.assertNotIn(cut, ops.OPERATORS.values())
        self.assertNotIn(cut.id, ops.OPERATORS)
        self.assertEqual(cut.regions, ())
        for other in ops.OPERATORS.values():
            if other is not op:
                self.assertFalse(other.tfnsw_sydney_trains, other.id)
                self.assertIsNone(other.static_second, other.id)
                self.assertIsNone(other.static_merge, other.id)
                self.assertFalse(other.obs_filter_updates, other.id)

    @unittest.skipUnless(LIB_REF.exists(), "LiveTrackCore clone not present")
    def test_shared_client_copy_is_byte_exact(self):
        mine = hashlib.sha256((HERE / "shared_tfnsw.py").read_bytes()).hexdigest()
        self.assertEqual(mine, hashlib.sha256(LIB_REF.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

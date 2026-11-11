"""Norway on Entur (SSOT 12): the three operators, identity, the timetable cut and extras, the look, direction,
lateness, finished runs, Flytoget's line and the push through Oslo's tunnels. No Home Assistant."""

import gzip
import io
import json
import os
import tempfile
import unittest
import zipfile
from datetime import date, datetime, timezone

from google.transit import gtfs_realtime_pb2 as pb
from saw_livetrack import entur

from _load import load

nw = load("operators.norway")
fly = load("operators.flytoget")
ops = load("operators")
base = load("operators.base")
gtfs_filter = load("gtfs_filter")
push = load("entur_push")
shapepath = load("shapepath")
Obs = base.Obs

# 2026-11-08 08:09:00 in Oslo (UTC+1).
NOW = datetime(2026, 11, 8, 7, 9, 0, tzinfo=timezone.utc).timestamp()
S = 3600
BRYN, OSLO_S, NATTH, SKOYEN = (59.90940, 10.81660), (59.91093, 10.75328), (59.91539, 10.72813), (59.92235, 10.67883)
WAY_IN, COMEBACK = (59.91168, 10.75219), (59.92012, 10.68731)          # oslotunnelen_w
T1 = "VYG:ServiceJourney:2218_443612-R"
# Bryn 08:00, Oslo S 08:05-08:07, Nationaltheatret 08:10, Skoyen 08:13.
CALLS = [[1, "q:bryn", None, 8 * S], [2, "q:oslo", 8 * S + 300, 8 * S + 420], [3, "q:nat", 8 * S + 600, 8 * S + 600],
         [4, "q:sky", 8 * S + 780, None]]
INFO = ["VYG:Line:L1", 0, 0, nw.HUB_MID, 8 * S + 300, 8 * S, 8 * S + 780, "Bryn stasjon", "Skøyen stasjon", CALLS]
LINE = [list(BRYN), [59.9105, 10.785], list(OSLO_S), list(WAY_IN), list(NATTH), [59.9180, 10.705], list(COMEBACK),
        list(SKOYEN)]


def static():
    return {"fetched_at": 1.0, "rail_shapes": [LINE], "trip_shapes": {T1: [0, 0]},
            "stop_pos": {"q:bryn": list(BRYN), "q:oslo": list(OSLO_S), "q:nat": list(NATTH), "q:sky": list(SKOYEN)},
            "extras": {"route": {"VYG:Line:L1": ["L1", "#8DC63F", "Spikkestad-Oslo S-Lillestrøm"]},
                       "trip": {T1: list(INFO)}}}


def obs(vid="2218-8", lat=WAY_IN[0], lon=WAY_IN[1], at=NOW - 120, trip=T1, train="2218", line="L1"):
    """As saw_livetrack.gtfs builds them: observed_at a UTC datetime."""
    when = None if at is None else datetime.fromtimestamp(at, timezone.utc)
    return Obs(vehicle_id=vid, lat=lat, lon=lon, observed_at=when, in_service=True, train=train, line=line,
               reported_course=None, trip_id=trip)


def at_oslo(hhmmss):
    h, m, s = hhmmss
    return datetime(2026, 11, 8, h - 1, m, s, tzinfo=timezone.utc).timestamp()


def _zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return b.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self._clock = nw.clock
        nw.clock = lambda: NOW

    def tearDown(self):
        nw.clock = self._clock


class IdentityTests(Base):
    def test_number_of(self):
        self.assertEqual(nw.number_of("VYG:ServiceJourney:2218_443612-R"), "2218")
        self.assertEqual(nw.number_of("GOA:ServiceJourney:3001_63033-R"), "3001")
        self.assertEqual(nw.number_of("FLT:ServiceJourney:1-2614-3724-20261108"), "3724")
        self.assertIsNone(nw.number_of("FLT:ServiceJourney:1-2614-x-20261108"))
        self.assertIsNone(nw.number_of("FLT:ServiceJourney:1-2614"))
        self.assertIsNone(nw.number_of("VYG:ServiceJourney:BRG-1_1-R"))
        self.assertIsNone(nw.number_of(""))
        self.assertIsNone(nw.number_of(None))

    def test_identity(self):
        self.assertEqual(nw.identity("2218", "20261108", NOW), "2218-8")
        self.assertEqual(nw.identity("2218", "20261031", NOW), "2218-31")
        self.assertEqual(nw.identity("2218", "", NOW), "2218-8")        # Oslo's day
        self.assertEqual(nw.identity("2218", None, at_oslo((24, 30, 0))), "2218-9")
        self.assertEqual(nw.identity("2218", "2026-11-08", NOW), "2218-8")   # not 8 digits: today

    def test_parse(self):
        fm = pb.FeedMessage()
        fm.header.gtfs_realtime_version = "2.0"

        def add(trip, route, start, lat, lon, ts=int(NOW) - 5, pos=True):
            e = fm.entity.add()
            e.id = trip
            e.vehicle.trip.trip_id = trip
            e.vehicle.trip.route_id = route
            if start:
                e.vehicle.trip.start_date = start
            if pos:
                e.vehicle.position.latitude, e.vehicle.position.longitude = lat, lon
            e.vehicle.timestamp = ts

        add(T1, "VYG:Line:L1", "20261108", 59.95, 11.04)
        add("FLT:ServiceJourney:1-2614-3724-20261108", "FLT:Line:FLY1", "20261108", 59.89, 10.53)
        add("GOA:ServiceJourney:3069_63130-R", "GOA:Line:59", "20261107", 58.9, 5.7)
        add("VYG:ServiceJourney:x_1-R", "VYG:Line:L1", "20261108", 59.0, 10.0)        # no number
        add("VYG:ServiceJourney:9_1-R", "VYG:Line:L1", "20261108", 0, 0, pos=False)   # no position
        e = fm.entity.add()
        e.id = "tu"
        e.trip_update.trip.trip_id = T1
        got = nw.parse(fm)
        self.assertEqual([(o.vehicle_id, o.train, o.line) for o in got],
                         [("2218-8", "2218", "L1"), ("3724-8", "3724", "FLY1"), ("3069-7", "3069", None)])
        self.assertTrue(all(o.in_service and o.reported_course is None for o in got))
        self.assertEqual(nw.epoch(got[0].observed_at), int(NOW) - 5)
        self.assertEqual(got[0].trip_id, T1)


class TimetableTests(Base):
    GTFS = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nVYG:Authority:VYG,Vy,https://x,Europe/Oslo\n",
        "routes.txt": ("route_id,agency_id,route_short_name,route_long_name,route_type,route_color\n"
                       "VYG:Line:L1,VYG:Authority:VYG,L1,Spikkestad-Oslo S-Lillestrøm,100,8DC63F\n"
                       "VYG:Line:R13,VYG:Authority:VYG,R13,Drammen-Oslo S-Dal,100,DF2027\n"),
        "calendar_dates.txt": "service_id,date,exception_type\nD8,20261108,1\nD1,20261201,1\n",
        "trips.txt": ("route_id,service_id,trip_id,shape_id\nVYG:Line:L1,D8,%s,S1\nVYG:Line:R13,D8,R1,S2\n"
                      "VYG:Line:L1,D1,DEC,S1\n" % T1),
        "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                           "%s,08:00:00,08:00:00,q:bryn,1\n%s,08:05:00,08:07:00,q:oslo,2\n"
                           "%s,08:10:00,08:10:00,q:nat,3\n%s,08:13:00,08:13:00,q:sky,4\n"
                           "R1,08:00:00,08:00:00,q:oslo,1\nR1,08:20:00,08:20:00,q:sky,2\n"
                           "DEC,08:00:00,08:00:00,q:bryn,1\n" % (T1, T1, T1, T1)),
        "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,parent_station\n"
                      "p:bryn,Bryn stasjon,59.9094,10.8166,\np:oslo,Oslo S,59.91093,10.75328,\n"
                      "p:nat,Nationaltheatret stasjon,59.91539,10.72813,\np:sky,Skøyen stasjon,59.92235,10.67883,\n"
                      "q:bryn,Bryn,59.9094,10.8166,p:bryn\nq:oslo,Oslo S,59.91093,10.75328,p:oslo\n"
                      "q:nat,Nationaltheatret,59.91539,10.72813,p:nat\nq:sky,Skøyen,59.92235,10.67883,p:sky\n"),
        "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nS1,59.9094,10.8166,1\n"
                       "S1,59.92235,10.67883,2\nS2,59.91093,10.75328,1\nS2,59.92235,10.67883,2\n"),
    }

    def cut(self):
        return gtfs_filter.keep_service_window(_zip(self.GTFS), None, today=date(2026, 11, 8),
                                               route_keep=nw.keep_route)

    def test_route_keep_cuts_to_l_lines_and_the_window(self):
        z = zipfile.ZipFile(io.BytesIO(self.cut()))
        self.assertEqual(z.read("routes.txt").decode().count("VYG:Line:"), 1)
        trips = z.read("trips.txt").decode()
        self.assertIn(T1, trips)
        self.assertNotIn("R1", trips)
        self.assertNotIn("DEC", trips)
        self.assertNotIn("R1,", z.read("stop_times.txt").decode())

    def test_route_keep_none_keeps_every_route(self):
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(self.GTFS), None,
                                                                       today=date(2026, 11, 8))))
        self.assertIn("R1", z.read("trips.txt").decode())

    def test_keep_route(self):
        self.assertTrue(nw.keep_route({"route_short_name": "L1"}))
        self.assertTrue(nw.keep_route({"route_short_name": "L5"}))
        self.assertFalse(nw.keep_route({"route_short_name": "RE11"}))
        self.assertFalse(nw.keep_route({"route_short_name": "FLY1"}))
        self.assertFalse(nw.keep_route({}))
        self.assertTrue(nw.keep_all({}))

    def test_extras(self):
        z = zipfile.ZipFile(io.BytesIO(self.cut()))
        ex = nw.make_extras(nw.HUBS)(z, {"sched": {T1: {}}}, {"S1": [3, 1]})
        self.assertEqual(ex["route"]["VYG:Line:L1"], ["L1", "#8DC63F", "Spikkestad-Oslo S-Lillestrøm"])
        self.assertEqual(ex["trip"][T1], ["VYG:Line:L1", 3, 1, nw.HUB_MID, 8 * S + 300, 8 * S, 8 * S + 780,
                                          "Bryn stasjon", "Skøyen stasjon",
                                          [[1, "q:bryn", 8 * S, 8 * S], [2, "q:oslo", 8 * S + 300, 8 * S + 420],
                                           [3, "q:nat", 8 * S + 600, 8 * S + 600],
                                           [4, "q:sky", 8 * S + 780, 8 * S + 780]]])

    def test_extras_hub_kinds_and_none(self):
        g = dict(self.GTFS)
        g["stop_times.txt"] = ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                               "%s,08:00:00,08:00:00,q:oslo,1\n%s,08:10:00,,q:nat,2\n" % (T1, T1))
        z = zipfile.ZipFile(io.BytesIO(_zip(g)))
        row = nw.make_extras(nw.HUBS)(z, {"sched": {T1: {}}}, {})["trip"][T1]
        self.assertEqual(row[1:7], [-1, 0, nw.HUB_FIRST, 8 * S, 8 * S, 8 * S + 600])
        row = nw.make_extras(("Nationaltheatret stasjon",))(z, {"sched": {T1: {}}}, {})["trip"][T1]
        self.assertEqual(row[3], nw.HUB_LAST)
        row = nw.make_extras(("Nowhere",))(z, {"sched": {T1: {}}}, {})["trip"][T1]
        self.assertEqual((row[3], row[4]), (nw.NO_HUB, None))
        self.assertEqual(nw.make_extras(nw.HUBS)(z, {"sched": {}}, {})["trip"], {})

    def test_hub_order(self):
        self.assertEqual(nw.hub(["Bergen stasjon", "Oslo S", "Arna stasjon", "Oslo S"], nw.HUBS), 3)
        self.assertEqual(nw.hub(["Arna stasjon", "Bergen stasjon"], nw.HUBS), 1)
        self.assertEqual(nw.hub(["Egersund stasjon", "Stavanger stasjon"], nw.HUBS), 1)
        self.assertIsNone(nw.hub(["Arna stasjon"], nw.HUBS))


class DirectionTests(Base):
    def test_service_seconds(self):
        self.assertEqual(nw.service_seconds(NOW, 8 * S, 9 * S), 8 * S + 540)
        late = at_oslo((24, 20, 0))      # 00:20 on the 9th
        self.assertEqual(nw.service_seconds(late, 23 * S + 3000, 24 * S + 2400), 24 * S + 1200)
        self.assertEqual(nw.service_seconds(late, 6 * S, 7 * S), 1200)          # neither spans: today's
        self.assertEqual(nw.service_seconds(late, None, None), 1200)

    def test_toward_hub(self):
        mid = list(INFO)
        self.assertTrue(nw.toward_hub(mid, 0, at_oslo((8, 4, 0))))
        self.assertFalse(nw.toward_hub(mid, 0, at_oslo((8, 6, 0))))
        self.assertTrue(nw.toward_hub(mid, 180, at_oslo((8, 6, 0))))           # 3 min late: still going to it
        self.assertFalse(nw.toward_hub(mid[:3] + [nw.HUB_FIRST] + mid[4:], 0, at_oslo((8, 4, 0))))
        self.assertTrue(nw.toward_hub(mid[:3] + [nw.HUB_LAST] + mid[4:], 0, at_oslo((9, 0, 0))))
        self.assertIsNone(nw.toward_hub(mid[:3] + [nw.NO_HUB, None] + mid[5:], 0, NOW))
        self.assertIsNone(nw.toward_hub(mid[:3] + [nw.HUB_MID, None] + mid[5:], 0, NOW))
        self.assertIsNone(nw.toward_hub(None, 0, NOW))
        self.assertIsNone(nw.toward_hub(mid[:6], 0, NOW))

    def test_line_look(self):
        out = nw.line_look("#8DC63F", False)
        self.assertEqual((out["marker_color"], out["marker_ring_color"], out["marker_label_color"]),
                         ("#8DC63F", "#FFFFFF", "#FFFFFF"))
        out = nw.line_look("#8DC63F", True)
        self.assertEqual((out["marker_color"], out["marker_ring_color"], out["marker_label_color"],
                          out["marker_arrow_color"], out["marker_arrow_outline_color"]),
                         ("#FFFFFF", "#8DC63F", "#8DC63F", "#FFFFFF", "#8DC63F"))
        self.assertEqual(nw.line_look("#8DC63F", None)["marker_color"], "#8DC63F")
        self.assertEqual(out["marker_ring_width"], 3)
        self.assertEqual(out["marker_label_outline_color"], "none")

    def test_flytoget_look(self):
        to = fly.look(None, True)
        away = fly.look(None, False)
        self.assertEqual((to["marker_color"], to["marker_ring_color"], to["marker_label_color"]),
                         ("#7C7B7B", "#EE7203", "#FFFFFF"))
        self.assertEqual((away["marker_color"], away["marker_ring_color"], away["marker_label_color"]),
                         ("#EE7203", "#7C7B7B", "#FFFFFF"))   # Lee 13:03: white letters both ways
        self.assertEqual(fly.look("#123456", None)["marker_color"], "#EE7203")
        self.assertEqual(fly.look("#123456", None)["marker_label_color"], "#FFFFFF")
        self.assertEqual((to["marker_arrow_color"], to["marker_arrow_outline_color"]), ("#7C7B7B", "#EE7203"))


class DecorateTests(Base):
    def rec(self, **kw):
        r = {"latitude": 59.9112, "longitude": 10.76, "in_service": True, "position_jump": True, "course_deg": 1.0}
        r.update(kw)
        return r

    def test_label_name_lateness_look_and_arrow(self):
        dec = nw.make_decorate(lambda c, t: nw.line_look(c or "#000000", t))
        r = self.rec()
        nw.clock = lambda: at_oslo((8, 4, 0))
        dec(r, obs(), static())
        self.assertEqual(r["marker_label"], "L1")
        self.assertEqual(r["line_name"], "Train 2218 · Spikkestad-Oslo S-Lillestrøm")
        self.assertEqual((r["late_threshold_min"], r["very_late_threshold_min"]), (4, 8))
        self.assertNotIn("position_jump", r)
        self.assertEqual(r["marker_color"], "#FFFFFF")                    # going to Oslo S
        self.assertEqual(r["icon_rotation_basis"], "course")
        self.assertGreater(r["course_deg"], 260.0)                        # westward along the shape
        self.assertEqual(r["course_deg"], r["icon_rotation_deg"])
        r = self.rec(delay_min=0)
        del r["course_deg"]
        nw.clock = lambda: at_oslo((8, 8, 0))
        dec(r, obs(), static())
        self.assertEqual(r["marker_color"], "#8DC63F")                    # left Oslo S
        self.assertEqual(r["icon_rotation_basis"], "held")
        self.assertNotIn("course_deg", r)

    def test_delay_keeps_it_going_to_the_hub(self):
        dec = nw.make_decorate(lambda c, t: nw.line_look(c, t))
        r = self.rec(delay_min=3)
        nw.clock = lambda: at_oslo((8, 6, 0))
        dec(r, obs(), static())
        self.assertEqual(r["marker_color"], "#FFFFFF")

    def test_unknown_trip(self):
        dec = nw.make_decorate(lambda c, t: nw.line_look(c or "#DF2027", t))
        r = self.rec()
        dec(r, obs(trip="VYG:ServiceJourney:1_1-R", line=None, train="1"), static())
        self.assertEqual(r["line_name"], "Train 1")
        self.assertNotIn("marker_label", r)
        self.assertEqual(r["marker_color"], "#DF2027")
        self.assertNotIn("icon_rotation_basis", r)
        r = self.rec()
        dec(r, obs(trip="x", line="FLY1"), None)
        self.assertEqual(r["marker_label"], "FLY1")

    def test_label_from_the_route_not_the_feed(self):
        r = self.rec()
        nw.make_decorate(lambda c, t: {})(r, obs(line=None), static())        # Go-Ahead: route ids carry no line
        self.assertEqual(r["marker_label"], "L1")
        r = self.rec()
        nw.make_decorate(lambda c, t: {})(r, obs(line="X9"), static())
        self.assertEqual(r["marker_label"], "L1")

    def test_end_names_without_a_long_name(self):
        st = static()
        st["extras"]["route"]["VYG:Line:L1"][2] = ""
        r = self.rec()
        nw.make_decorate(lambda c, t: {})(r, obs(), st)
        self.assertEqual(r["line_name"], "Train 2218 · Bryn-Skøyen")
        self.assertEqual(nw.short_name("Oslo S"), "Oslo S")
        self.assertEqual(nw.short_name("Oslo lufthavn stasjon"), "Oslo lufthavn")


class NextStopTests(Base):
    def tu(self, rows, trip=T1):
        fm = pb.FeedMessage()
        fm.header.gtfs_realtime_version = "2.0"
        e = fm.entity.add()
        e.id = "1"
        e.trip_update.trip.trip_id = trip
        for seq, delay, skipped in rows:
            s = e.trip_update.stop_time_update.add()
            s.stop_sequence = seq
            if delay is not None:
                s.departure.delay = delay
            if skipped:
                s.schedule_relationship = 1
        p = fm.entity.add()
        p.id = "p"
        p.vehicle.trip.trip_id = trip
        return fm

    def st(self):
        st = static()
        st["stops"] = {"q:bryn": "Bryn", "q:oslo": "Oslo S", "q:nat": "Nationaltheatret", "q:sky": "Skøyen"}
        return st

    def test_never_the_origin_and_its_delay_carries(self):
        now = at_oslo((7, 58, 0))                        # before Bryn's departure: still the stop after it
        nxt, dl = nw.stops_from_updates(self.tu([(1, 60, False)]), self.st(), now)
        self.assertEqual(nxt[T1][0], "Oslo S")
        self.assertEqual(dl[T1], 60)
        self.assertAlmostEqual(nxt[T1][1], at_oslo((8, 6, 0)))   # arrival 08:05 + 60 s

    def test_passed_stops_skipped(self):
        rows = [(1, 0, False), (2, 30, False), (3, 120, False), (4, 120, False)]
        nxt, dl = nw.stops_from_updates(self.tu(rows), self.st(), at_oslo((8, 8, 0)))
        self.assertEqual(nxt[T1][0], "Nationaltheatret")
        self.assertEqual(dl[T1], 120)
        nxt, _ = nw.stops_from_updates(self.tu(rows), self.st(), at_oslo((8, 7, 10)))
        self.assertEqual(nxt[T1][0], "Oslo S")          # departure 08:07 + 30 s still ahead
        nxt, _ = nw.stops_from_updates(self.tu([(1, 0, False), (2, 0, False), (3, 0, True)]), self.st(),
                                       at_oslo((8, 8, 0)))
        self.assertEqual(nxt[T1][0], "Skøyen")           # a skipped stop is never the next

    def test_unknown_and_finished(self):
        self.assertEqual(nw.stops_from_updates(self.tu([(1, 0, False)], trip="x"), self.st(), NOW), ({}, {}))
        self.assertEqual(nw.stops_from_updates(self.tu([(1, 0, False)]), None, NOW), ({}, {}))
        self.assertEqual(nw.stops_from_updates(self.tu([(1, 0, False)]), self.st(), at_oslo((9, 0, 0))), ({}, {}))
        st = self.st()
        del st["stops"]["q:oslo"]
        nxt, dl = nw.stops_from_updates(self.tu([(1, 0, False)]), st, at_oslo((7, 58, 0)))
        self.assertEqual((nxt, dl), ({}, {T1: 0}))        # no name: no station shown, the delay kept

    def test_registered(self):
        for op_id in ("vy", "go_ahead_norge", "flytoget"):
            self.assertIs(ops.OPERATORS[op_id].stops_from_updates, nw.stops_from_updates)
        for op in ops.OPERATORS.values():
            if op.source != base.SOURCE_ENTUR:
                self.assertIsNone(op.stops_from_updates, op.id)


class EpochTests(unittest.TestCase):
    def test_epoch(self):
        self.assertEqual(nw.epoch(datetime(2026, 11, 8, 7, 9, tzinfo=timezone.utc)), NOW)
        self.assertEqual(nw.epoch(5), 5.0)
        self.assertIsNone(nw.epoch(None))
        self.assertIsNone(nw.epoch(True))
        self.assertIsNone(nw.epoch("x"))


class FinishedTests(Base):
    def test_drop_finished(self):
        st = static()
        late = at_oslo((8, 30, 0))
        kept = nw.drop_finished([obs(vid="a", at=late - 400), obs(vid="b", at=late - 100),
                                 obs(vid="c", at=late - 400, trip="unknown"), obs(vid="d", at=None)], st, late)
        self.assertEqual([o.vehicle_id for o in kept], ["b", "c", "d"])
        self.assertEqual(len(nw.drop_finished([obs(at=late - 400)], None, late)), 1)
        early = at_oslo((8, 17, 0))                       # 4 min after the last stop: not yet
        self.assertEqual(len(nw.drop_finished([obs(at=early - 400)], st, early)), 1)


class FlytogetLineTests(unittest.TestCase):
    GTFS = {
        "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,parent_station\nA,A,59.0,10.0,\nB,B,59.1,10.0,\n"
                      "C,C,59.2,10.0,\nqa,A,59.0,10.0,A\nqb,B,59.1,10.0,B\nqc,C,59.2,10.0,C\n"),
        "trips.txt": ("route_id,service_id,trip_id,shape_id\nFLY1,D,t1,SH1\nFLY1,D,t2,SH1\nFLY1,D,t3,SH2\n"
                      "FLY1,D,t4,SH3\n"),
        "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                           "t1,08:00:00,08:00:00,qa,1\nt1,08:05:00,08:05:00,qb,2\nt1,08:10:00,08:10:00,qc,3\n"
                           "t2,08:20:00,08:20:00,qa,1\nt2,08:25:00,08:25:00,qb,2\nt2,08:30:00,08:30:00,qc,3\n"
                           "t3,08:00:00,08:00:00,qc,1\nt3,08:05:00,08:05:00,qa,2\n"
                           "t4,08:00:00,08:00:00,qa,1\nt4,08:05:00,08:05:00,qb,2\nt4,08:09:00,08:09:00,qa,3\n"),
        "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nSH1,59.0,10.0,1\nSH1,59.2,10.0,2\n"
                       "SH2,59.2,10.0,1\nSH2,59.0,10.0,2\nSH3,59.0,10.0,1\nSH3,59.1,10.0,2\nSH3,59.0,10.0,3\n"),
        "routes.txt": "route_id,route_short_name,route_type\nFLY1,FLY1,101\n",
    }
    PAIRS = {"A>B": [[59.0, 10.0], [59.05, 10.01], [59.1, 10.0]], "B>C": [[59.1, 10.0], [59.15, 10.01], [59.2, 10.0]]}

    def shapes(self, raw):
        z = zipfile.ZipFile(io.BytesIO(raw))
        rows = z.read("shapes.txt").decode().strip().splitlines()
        out = {}
        for r in rows[1:]:
            sid, la, lo, seq = r.split(",")
            out.setdefault(sid, []).append((int(seq), float(la), float(lo)))
        return {k: [(la, lo) for _, la, lo in sorted(v)] for k, v in out.items()}, z

    def test_rewrite(self):
        got, z = self.shapes(fly.rewrite_shapes(_zip(self.GTFS), self.PAIRS))
        self.assertEqual(got["SH1"], [(59.0, 10.0), (59.05, 10.01), (59.1, 10.0), (59.15, 10.01), (59.2, 10.0)])
        self.assertEqual(got["SH2"], [(59.2, 10.0), (59.0, 10.0)])       # C>A is not in the file: its own points
        self.assertEqual(got["SH3"], [(59.0, 10.0), (59.1, 10.0), (59.0, 10.0)])   # A>B there, B>A not: all its own
        self.assertEqual(z.read("routes.txt"), self.GTFS["routes.txt"].encode())

    def test_nothing_to_do(self):
        raw = _zip(self.GTFS)
        self.assertIs(fly.rewrite_shapes(raw, {}), raw)
        g = dict(self.GTFS)
        del g["shapes.txt"]
        raw = _zip(g)
        self.assertIs(fly.rewrite_shapes(raw, self.PAIRS), raw)

    def test_shipped_file(self):
        pairs = fly.load_pairs()
        self.assertEqual(len(pairs), 20)
        oslo_airport = pairs["NSR:StopPlace:337>NSR:StopPlace:269"]
        self.assertGreater(len(oslo_airport), 1000)
        self.assertAlmostEqual(oslo_airport[0][0], 59.911, places=2)
        with gzip.open(fly.LINES_FILE, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertIn("NLOD", doc["credit"])
        self.assertEqual(fly.load_pairs(os.path.join(tempfile.gettempdir(), "no_such_saw_file.json.gz")), {})

    def test_default_pairs_are_the_shipped_ones(self):
        fly._pairs = None
        raw = _zip(self.GTFS)
        self.assertIs(fly.rewrite_shapes(raw), raw)                     # A, B, C are no Flytoget stations
        self.assertEqual(len(fly._pairs), 20)


class PushTests(Base):
    def setUp(self):
        super().setUp()
        self.p = push.EnturPush()

    def result(self, o, **kw):
        rec = {"latitude": o.lat, "longitude": o.lon, "in_service": True, "previous_latitude": 1.0,
               "previous_longitude": 1.0, "segment_duration_s": 30, "stalled": True}
        rec.update(kw)
        return {"vehicles": {o.vehicle_id: rec}}

    def test_where(self):
        info = list(INFO)
        svc = lambda h, m: h * S + m * 60
        self.assertEqual(push.where(info, svc(8, 8), 0), (1, 2))
        self.assertIsNone(push.where(info, svc(8, 6), 0))                # standing at Oslo S
        self.assertIsNone(push.where(info, svc(8, 8), 120))              # 2 min late: still standing
        self.assertIsNone(push.where(info, svc(7, 59), 0))               # before its first departure
        self.assertIsNone(push.where(info, svc(9, 0), 0))                # after its last stop
        self.assertEqual(push.where(info, svc(8, 11), 0), (2, 3))
        self.assertIsNone(push.where(info[:9], svc(8, 8), 0))
        self.assertIsNone(push.where(None, svc(8, 8), 0))

    def test_push_then_hold_then_release(self):
        st = static()
        o = obs(at=at_oslo((8, 7, 30)))
        now = at_oslo((8, 9, 0))
        res = self.result(o)
        self.assertEqual(self.p.apply(res, [o], st, now), 1)
        r = res["vehicles"][o.vehicle_id]
        self.assertEqual(r["position_source"], "estimated")
        self.assertEqual((r["fix_latitude"], r["fix_longitude"]), WAY_IN)
        for k in ("previous_latitude", "previous_longitude", "segment_duration_s", "stalled"):
            self.assertNotIn(k, r)
        self.assertEqual(r["icon_rotation_basis"], "course")
        self.assertLess(r["longitude"], WAY_IN[1] - 0.005)               # pushed west of the frozen fix
        self.assertGreater(r["longitude"], COMEBACK[1])
        self.assertIn("track_path", r)
        self.assertEqual(r["track_path"][-1], [r["latitude"], r["longitude"]])
        mid = (r["latitude"], r["longitude"])
        res = self.result(o)
        self.p.apply(res, [o], st, at_oslo((8, 20, 0)))
        r = res["vehicles"][o.vehicle_id]
        self.assertAlmostEqual(r["latitude"], COMEBACK[0], places=4)     # at the comeback, held
        self.assertAlmostEqual(r["longitude"], COMEBACK[1], places=4)
        self.assertEqual(r["icon_rotation_basis"], "held")
        self.assertNotIn("course_deg", r)
        fresh = obs(lat=SKOYEN[0], lon=SKOYEN[1], at=at_oslo((8, 20, 30)))
        res = self.result(fresh)
        self.assertEqual(self.p.apply(res, [fresh], st, at_oslo((8, 20, 40))), 0)
        r = res["vehicles"][fresh.vehicle_id]
        self.assertEqual(r["position_source"], "observed")
        self.assertAlmostEqual(r["previous_latitude"], COMEBACK[0], places=4)
        self.assertEqual(r["latitude"], SKOYEN[0])
        self.assertTrue(mid)

    def test_push_starts_at_the_departure(self):
        st = static()
        o = obs(at=at_oslo((8, 5, 30)))                                  # frozen while standing, then left at 08:07
        res = self.result(o)
        self.p.apply(res, [o], st, at_oslo((8, 6, 59)))                  # still standing: held, not pushed
        self.assertEqual(res["vehicles"][o.vehicle_id]["position_source"], "observed")
        self.assertEqual(res["vehicles"][o.vehicle_id]["longitude"], WAY_IN[1])
        res = self.result(o)
        self.p.apply(res, [o], st, at_oslo((8, 7, 1)))
        r = res["vehicles"][o.vehicle_id]
        self.assertEqual(r["position_source"], "estimated")
        self.assertAlmostEqual(r["longitude"], WAY_IN[1], places=3)      # 1 s after leaving: barely moved

    def test_fresh_fix_is_left_alone(self):
        o = obs(at=at_oslo((8, 8, 30)))
        res = self.result(o)
        self.assertEqual(self.p.apply(res, [o], static(), at_oslo((8, 9, 0))), 0)
        r = res["vehicles"][o.vehicle_id]
        self.assertEqual(r["position_source"], "observed")
        self.assertIn("previous_latitude", r)
        self.assertIn("stalled", r)

    def test_not_at_a_tunnel_is_held(self):
        o = obs(lat=NATTH[0] + 0.004, lon=NATTH[1] - 0.03, at=at_oslo((8, 10, 30)))
        res = self.result(o)
        self.assertEqual(self.p.apply(res, [o], static(), at_oslo((8, 12, 0))), 0)
        self.assertEqual(res["vehicles"][o.vehicle_id]["longitude"], o.lon)

    def test_runs_on_whatever_the_timetable_says(self):
        st = static()
        o = obs(at=at_oslo((8, 7, 30)))
        self.p.apply(self.result(o), [o], st, at_oslo((8, 9, 0)))
        res = self.result(o, delay_min=-30)                              # the timetable now says it is elsewhere
        self.p.apply(res, [o], st, at_oslo((8, 9, 30)))
        self.assertEqual(res["vehicles"][o.vehicle_id]["position_source"], "estimated")

    def test_no_timetable_out_of_service_and_gone(self):
        o = obs(at=at_oslo((8, 7, 30)))
        res = self.result(o)
        self.assertEqual(self.p.apply(res, [o], None, at_oslo((8, 9, 0))), 0)
        res = self.result(o, in_service=False)
        self.assertEqual(self.p.apply(res, [o], static(), at_oslo((8, 9, 0))), 0)
        self.assertNotIn("position_source", res["vehicles"][o.vehicle_id])
        self.p.apply(self.result(o), [o], static(), at_oslo((8, 9, 0)))
        self.assertIn(o.vehicle_id, self.p._runs)
        self.p.apply({"vehicles": {}}, [], static(), at_oslo((8, 9, 30)))
        self.assertEqual(self.p._runs, {})

    def test_shape_too_far(self):
        st = static()
        st["rail_shapes"] = [[[la + 0.01, lo] for la, lo in LINE]]      # the same line 1.1 km north
        st["fetched_at"] = 2.0
        o = obs(at=at_oslo((8, 7, 30)))
        self.assertEqual(self.p.apply(self.result(o), [o], st, at_oslo((8, 9, 0))), 0)


class RegistryTests(unittest.TestCase):
    def test_three_operators(self):
        self.assertEqual([o.id for o in ops.operators_in("NO")], ["flytoget", "go_ahead_norge", "vy"])
        self.assertEqual(ops.regions_in_use()["NO"], "Norway")
        for op_id, cs in (("vy", "VYG"), ("go_ahead_norge", "GOA"), ("flytoget", "FLT")):
            op = ops.OPERATORS[op_id]
            self.assertEqual(op.source, base.SOURCE_ENTUR)
            self.assertEqual((op.entur_consumer, op.entur_codespace), (entur.COMMUTER, cs))
            self.assertTrue(op.entur_push)
            self.assertFalse(op.needs_key)
            self.assertEqual(op.positions_url, entur.TRIP_UPDATES_URL % cs)
            self.assertTrue(op.static_window)
            self.assertFalse(op.narn)
            self.assertIs(op.obs_filter, nw.drop_finished)
            self.assertTrue(op.attribution.startswith(entur.ATTRIBUTION))
            self.assertEqual(op.terms_url, entur.TERMS_URL)
            self.assertIn("rb_%s-aggregated-gtfs.zip" % cs.lower(), op.static_url)
        self.assertIs(ops.OPERATORS["flytoget"].static_rewrite, fly.rewrite_shapes)
        self.assertIn("Vy's timetable shapes", ops.OPERATORS["flytoget"].attribution)
        self.assertIsNone(ops.OPERATORS["vy"].static_rewrite)
        self.assertIs(ops.OPERATORS["vy"].static_route_keep, nw.keep_route)
        self.assertIs(ops.OPERATORS["flytoget"].static_route_keep, nw.keep_all)

    def test_defaults_left_alone_elsewhere(self):
        for op in ops.OPERATORS.values():
            if op.source != base.SOURCE_ENTUR:
                self.assertIsNone(op.entur_consumer, op.id)
                self.assertFalse(op.entur_push, op.id)
                self.assertIsNone(op.static_route_keep, op.id)
                if op.source != base.SOURCE_IRISH_RAIL:   # Irish Rail cuts its zip: tests/test_irish_rail.py
                    self.assertIsNone(op.static_rewrite, op.id)
                self.assertIsNone(op.obs_filter, op.id)

    def test_look_colours(self):
        vy = ops.OPERATORS["vy"]
        r = {"latitude": 60.0, "longitude": 10.0, "in_service": True}
        vy.decorate(r, obs(trip="nope", line=None), None)
        self.assertEqual(r["marker_color"], "#8DC63F")
        r = {"latitude": 60.0, "longitude": 10.0, "in_service": True}
        ops.OPERATORS["flytoget"].decorate(r, obs(trip="nope", line="FLY1"), None)
        self.assertEqual(r["marker_color"], "#EE7203")


if __name__ == "__main__":
    unittest.main()

"""The tunnel push (backlog 290 step 3, SSOT 8.3): a train dark in Finland's Lentoasema
tunnel drawn along the tracks as the map contract's estimate (D3d). No Home Assistant."""

import math
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from _load import load

tracknet = load("tracknet")
tunnel = load("tunnel")
vr = load("operators.vr_lahijunat")
ops = load("operators")
attributes = load("attributes")

LAT0 = 60.2
KY = 6371000.0 * math.pi / 180
KX = KY * math.cos(math.radians(LAT0))
T0 = 1_790_000_000.0


def ll(x, y=0.0):
    """(lat, lon) of a point x m east and y m north of 60.2 N, 24.9 E."""
    return (round(LAT0 + y / KY, 7), round(24.9 + x / KX, 7))


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace("+00:00", "Z")


# One straight track west to east, 10 km. Entry portal at 2 km, stops S1 at 3 km and S2 at
# 4 km, far portal at 6 km; the comeback point 200 m past it.
STRAIGHT = [[list(ll(x)) for x in range(0, 10001, 500)]]
TUN = tunnel.Tunnel(line="X", start=ll(0), end=ll(10000), portal_in=ll(2000),
                    stops=(("S1", ll(3000)), ("S2", ll(4000))), portal_out=ll(6000),
                    back_past_portal_m=200.0, between_s=80.0, back_s=100.0)


def net():
    return tracknet.Network(STRAIGHT, LAT0)


def clocks(**kw):
    """Stop clocks for S1 and S2: S1 arrives T0+100 and leaves T0+130, S2 leaves T0+260,
    by live estimate unless overridden."""
    c1 = dict(arr_estimate=T0 + 100, arr_scheduled=T0 + 90, dep_estimate=T0 + 130,
              dep_scheduled=T0 + 120)
    c2 = dict(arr_scheduled=T0 + 200, dep_estimate=T0 + 260, dep_scheduled=T0 + 250)
    c1.update(kw.get("c1", {}))
    c2.update(kw.get("c2", {}))
    return {"S1": tunnel.StopClock(**c1), "S2": tunnel.StopClock(**c2)}


def along(way, rec):
    return way.project(rec["latitude"], rec["longitude"])[1]


class WayTests(unittest.TestCase):

    def test_marks(self):
        w = tunnel.Way(net(), TUN)
        for got, want in ((w.portal_in, 2000), (w.stop1, 3000), (w.stop2, 4000),
                          (w.portal_out, 6000), (w.back, 6200), (w.length, 10000)):
            self.assertAlmostEqual(got, want, delta=1.0)

    def test_a_tunnel_out_of_order_is_skipped(self):
        bad = tunnel.Tunnel(**{**TUN.__dict__, "stops": (("S2", ll(4000)), ("S1", ll(3000)))})
        with self.assertRaises(ValueError):
            tunnel.Way(net(), bad)
        self.assertEqual(tunnel.TunnelPush(net(), [bad]).ways, {})

    def test_a_mark_off_the_way(self):
        with self.assertRaises(ValueError):
            tunnel.Way(net(), tunnel.Tunnel(**{**TUN.__dict__, "portal_out": ll(6000, 40)}))

    def test_the_zone_needs_room_before_the_portal(self):
        with self.assertRaises(ValueError):
            tunnel.Way(net(), tunnel.Tunnel(**{**TUN.__dict__, "portal_in": ll(200)}))

    def test_bearing(self):
        self.assertAlmostEqual(tunnel.Way(net(), TUN).bearing(3000), 90.0, delta=0.2)


class ScheduleTests(unittest.TestCase):

    def setUp(self):
        self.w = tunnel.Way(net(), TUN)

    def times(self, dep1=T0 + 130, dep2=T0 + 260, **kw):
        c = clocks(**kw)
        return self.w.schedule(2000.0, T0, c["S1"], c["S2"], dep1, dep2)

    def test_the_whole_passage(self):
        t = self.times()
        self.assertEqual(t, (T0 + 100, T0 + 130, T0 + 210, T0 + 260, T0 + 360))
        for now, s, moving in ((T0 + 50, 2500, True), (T0 + 110, 3000, False),
                               (T0 + 170, 3500, True), (T0 + 230, 4000, False),
                               (T0 + 310, 5100, True), (T0 + 400, 6200, False),
                               (T0 - 5, 2000, False)):
            got = self.w.position(2000.0, T0, t, now)
            self.assertAlmostEqual(got[0], s, delta=0.5, msg=now - T0)
            self.assertEqual(got[1], moving, msg=now - T0)

    def test_an_actual_arrival_wins(self):
        self.assertEqual(self.times(c1={"arr_actual": T0 + 120})[0], T0 + 120)

    def test_never_faster_than_max_kmh(self):
        a1 = self.times(c1={"arr_estimate": T0 + 5})[0]
        self.assertAlmostEqual(a1, T0 + 1000 / (120 / 3.6), delta=0.01)

    def test_a_departure_leaves_on_its_estimate_not_its_actual(self):
        late = {"dep_actual": T0 + 190}
        self.assertEqual(self.times(c1=late)[1], T0 + 130)
        self.assertEqual(self.times(dep1=None, c1=late)[1], T0 + 190)
        self.assertEqual(self.times(dep1=None)[1], T0 + 120)
        self.assertEqual(self.times(dep2=None, c2={"dep_actual": T0 + 300})[3], T0 + 300)
        self.assertEqual(self.times(c2={"dep_actual": T0 + 300})[3], T0 + 260)
        self.assertEqual(self.times(dep2=None)[3], T0 + 250)

    def test_the_second_arrival_caps_the_first_departure(self):
        t = self.times(dep1=T0 + 150, c2={"arr_actual": T0 + 180})
        self.assertEqual(t[1:3], (T0 + 100, T0 + 180))
        t = self.times(c2={"arr_actual": T0 + 300})
        self.assertEqual(t[1:4], (T0 + 130, T0 + 300, T0 + 300))

    def test_no_departure_time_no_schedule(self):
        c = tunnel.StopClock(arr_estimate=T0 + 100)
        self.assertIsNone(self.w.schedule(2000.0, T0, c, clocks()["S2"], None, None))


class PushTests(unittest.TestCase):

    def setUp(self):
        self.push = tunnel.TunnelPush(net(), [TUN])
        self.way = self.push.ways["X"]

    def poll(self, x, now, clock=None, fix_t=T0, line="X", y=0.0, service=True, vid="v",
             **extra):
        rec = {"vehicle_id": vid, "latitude": ll(x, y)[0], "longitude": ll(x, y)[1],
               "in_service": service, "marker_label": line,
               "observed_at": iso(fix_t) if fix_t is not None else None, **extra}
        res = {"vehicles": {vid: rec}}
        obs = [SimpleNamespace(vehicle_id=vid, line=line)]
        counts = self.push.apply(res, obs, {vid: clock if clock is not None else clocks()}, now)
        return rec, counts

    def test_an_estimate_carries_d3d(self):
        fix = ll(2000)
        rec, counts = self.poll(2000, T0 + 50, previous_latitude=1.0, previous_longitude=2.0,
                                previous_observed_at=iso(T0 - 30), segment_duration_s=30,
                                position_jump=True, stalled=True, course_deg=10.0)
        self.assertEqual(counts, {"estimated": 1, "observed": 0})
        self.assertEqual(rec["position_source"], "estimated")
        self.assertAlmostEqual(along(self.way, rec), 2500, delta=1.0)
        self.assertEqual((rec["fix_latitude"], rec["fix_longitude"]), fix)
        self.assertEqual(rec["observed_at"], iso(T0))
        # Named here, not read from tunnel.SEGMENT_KEYS: a test that reads the constant
        # changes with it (ltcr_fi_mutate.py "tu segment keys" survived that way).
        for key in ("previous_latitude", "previous_longitude", "previous_observed_at",
                    "segment_duration_s", "position_jump", "stalled"):
            self.assertNotIn(key, rec)
        self.assertAlmostEqual(rec["course_deg"], 90.0, delta=0.2)
        self.assertEqual(rec["icon_rotation_basis"], "course")
        attrs = attributes.to_attributes(dict(rec, marker_label="X"), "vr_lahijunat")
        for key in ("position_source", "fix_latitude", "fix_longitude"):
            self.assertEqual(attrs[key], rec[key])

    def test_held_at_a_stop(self):
        rec, _ = self.poll(2000, T0 + 110)
        self.assertAlmostEqual(along(self.way, rec), 3000, delta=1.0)
        self.assertNotIn("course_deg", rec)
        self.assertEqual(rec["icon_rotation_basis"], "held")
        self.assertAlmostEqual(rec["icon_rotation_deg"], 90.0, delta=0.2)

    def test_held_at_the_comeback_point(self):
        rec, _ = self.poll(2000, T0 + 500)
        self.assertAlmostEqual(along(self.way, rec), 6200, delta=1.0)
        self.assertEqual(rec["icon_rotation_basis"], "held")

    def test_the_zone(self):
        for x, y, src in ((1600, 0, "observed"), (1800, 0, "estimated"),
                          (2900, 0, "estimated"), (3100, 0, "observed"),
                          (2500, 40, "observed"), (2500, 20, "estimated")):
            self.push = tunnel.TunnelPush(net(), [TUN])
            rec, _ = self.poll(x, T0 + 10, y=y)
            self.assertEqual(rec["position_source"], src, msg=(x, y))
            if src == "observed":
                self.assertEqual((rec["latitude"], rec["longitude"]), ll(x, y))

    def test_other_lines_no_clock_and_out_of_service(self):
        rec, counts = self.poll(2000, T0 + 50, line="R")
        self.assertEqual((rec["position_source"], counts["observed"]), ("observed", 1))
        rec, _ = self.poll(2000, T0 + 50, clock={})
        self.assertEqual(rec["position_source"], "observed")
        rec, counts = self.poll(2000, T0 + 50, service=False)
        self.assertNotIn("position_source", rec)
        self.assertEqual(counts, {"estimated": 0, "observed": 0})
        rec, _ = self.poll(2000, T0 + 50, fix_t=None)
        self.assertEqual(rec["position_source"], "observed")

    def test_never_backwards(self):
        rec, _ = self.poll(2000, T0 + 90)
        self.assertAlmostEqual(along(self.way, rec), 2900, delta=1.0)
        rec, _ = self.poll(2000, T0 + 120, clock=clocks(c1={"arr_estimate": T0 + 400}))
        self.assertAlmostEqual(along(self.way, rec), 2900, delta=1.0)
        self.assertEqual(rec["icon_rotation_basis"], "held")
        self.assertNotIn("track_path", rec)

    def test_track_path_along_the_way_from_the_last_published(self):
        rec0, _ = self.poll(1500, T0)                         # outside the zone: the fix
        self.assertEqual(rec0["position_source"], "observed")
        rec1, _ = self.poll(2000, T0 + 30)
        p1 = rec1["track_path"]
        self.assertEqual(p1[0], [round(ll(1500)[0], 6), round(ll(1500)[1], 6)])
        self.assertEqual(p1[-1], [rec1["latitude"], rec1["longitude"]])
        rec2, _ = self.poll(2000, T0 + 60)
        p2 = rec2["track_path"]
        self.assertEqual(p2[0], [rec1["latitude"], rec1["longitude"]])
        self.assertEqual(p2[-1], [rec2["latitude"], rec2["longitude"]])
        self.assertTrue(2 <= len(p2) <= 500)
        self.assertTrue(all(abs(la - LAT0) < 1e-5 for la, _ in p2))

    def test_the_comeback_fix_takes_over_from_the_estimate(self):
        est, _ = self.poll(2000, T0 + 500)
        rec, counts = self.poll(6500, T0 + 530, fix_t=T0 + 520, previous_latitude=ll(2000)[0],
                                previous_longitude=ll(2000)[1], segment_duration_s=520)
        self.assertEqual(counts, {"estimated": 0, "observed": 1})
        self.assertEqual(rec["position_source"], "observed")
        self.assertEqual((rec["latitude"], rec["longitude"]), ll(6500))
        self.assertEqual(rec["previous_latitude"], ll(2000)[0])
        p = rec["track_path"]
        self.assertEqual(p[0], [est["latitude"], est["longitude"]])
        self.assertEqual(p[-1], [rec["latitude"], rec["longitude"]])
        # Taken over: the next fix past the zone gets the fix-based path untouched.
        rec, _ = self.poll(7000, T0 + 560, fix_t=T0 + 550, track_path=[[1, 2], [3, 4]])
        self.assertEqual(rec["track_path"], [[1, 2], [3, 4]])

    def test_remembers_a_departure_estimate_once_the_actual_is_in(self):
        self.poll(2000, T0 + 30)
        rec, _ = self.poll(2000, T0 + 150, clock=clocks(c1={"dep_estimate": None,
                                                            "dep_actual": T0 + 190}))
        self.assertAlmostEqual(along(self.way, rec), 3250, delta=1.0)

    def test_forgets_a_train_that_is_gone(self):
        self.poll(2000, T0 + 90)
        self.push.apply({"vehicles": {}}, [], {}, T0 + 100)
        rec, _ = self.poll(2000, T0 + 120, clock=clocks(c1={"arr_estimate": T0 + 400,
                                                            "dep_estimate": None}))
        self.assertAlmostEqual(along(self.way, rec), 2300, delta=1.0)
        self.assertNotIn("track_path", rec)


class OperatorTests(unittest.TestCase):

    def rows(self, codes=("LEN", "AVP")):
        def r(code, kind, t, **kw):
            return {"stationShortCode": code, "type": kind, "scheduledTime": iso(t),
                    "commercialStop": True, "trainStopping": True, "cancelled": False, **kw}
        out = [r("HKI", "DEPARTURE", T0 - 600, actualTime=iso(T0 - 590))]
        if "LEN" in codes:
            out += [r("LEN", "ARRIVAL", T0 + 100, actualTime=iso(T0 + 103)),
                    r("LEN", "DEPARTURE", T0 + 130, liveEstimateTime=iso(T0 + 140))]
        if "AVP" in codes:
            out += [r("AVP", "ARRIVAL", T0 + 200), r("AVP", "DEPARTURE", T0 + 220)]
        return out + [r("HKI", "ARRIVAL", T0 + 3000)]

    def record(self, line="I", number="8804", rows=None):
        return {"number": number, "departure_date": "2026-10-12", "commuter_line": line,
                "train_type": "HL", "train": {"timeTableRows": rows or self.rows(),
                                              "commuterLineID": line}}

    def test_stop_clocks(self):
        c = vr.stop_clocks({"timeTableRows": self.rows()}, ("LEN", "AVP"))
        self.assertEqual(c["LEN"], tunnel.StopClock(
            arr_actual=T0 + 103, arr_estimate=None, arr_scheduled=T0 + 100,
            dep_actual=None, dep_estimate=T0 + 140, dep_scheduled=T0 + 130))
        self.assertEqual(c["AVP"], tunnel.StopClock(arr_scheduled=T0 + 200,
                                                    dep_scheduled=T0 + 220))
        half = self.rows()[:-2] + [self.rows()[-1]]          # AVP's departure row gone
        self.assertEqual(set(vr.stop_clocks({"timeTableRows": half}, ("LEN", "AVP"))), {"LEN"})

    def test_tunnel_clocks(self):
        got = vr.tunnel_clocks([self.record(), self.record(line="P", number="8601"),
                                self.record(line="R", number="9001"),
                                self.record(number="8806", rows=self.rows(("LEN",)))])
        self.assertEqual(set(got), {"8804-12", "8601-12"})
        done = [dict(r, actualTime=iso(T0)) for r in self.rows()]
        self.assertEqual(vr.tunnel_clocks([self.record(rows=done)]), {})

    def test_only_finland_has_tunnels(self):
        for op in ops.OPERATORS.values():
            if op.id == "vr_lahijunat":
                self.assertEqual({t.line for t in op.tunnels}, {"I", "P"})
                self.assertIs(op.tunnel_clocks, vr.tunnel_clocks)
            else:
                self.assertEqual((op.tunnels, op.tunnel_clocks), ((), None))


class ShippedTunnelTests(unittest.TestCase):
    """Lentoasema on the shipped network, and two passages of capture round 1."""

    @classmethod
    def setUpClass(cls):
        cls.net = tracknet.load("vr_lahijunat")
        cls.push = tunnel.TunnelPush(cls.net, vr.TUNNELS)

    def test_both_ways_and_their_marks(self):
        self.assertEqual(set(self.push.ways), {"I", "P"})
        for line in ("I", "P"):
            w = self.push.ways[line]
            self.assertAlmostEqual(w.stop1 - w.portal_in, 3013 if line == "I" else 3737, delta=40)
            self.assertAlmostEqual(w.stop2 - w.stop1, 1440, delta=40)
            self.assertAlmostEqual(w.portal_out - w.stop2, 3737 if line == "I" else 3013, delta=40)

    def passage(self, line, number, t, dark, dur):
        """The run's two stops on its actual times as live estimates (dark_to_stop1,
        dwell1, stop1_to_stop2, dwell2 from ltcr_fi_tunnel_rows.tsv)."""
        a1 = t + dur[0]; d1 = a1 + dur[1]; a2 = d1 + dur[2]; d2 = a2 + dur[3]
        c1, c2 = (tunnel.StopClock(arr_estimate=a1, dep_estimate=d1),
                  tunnel.StopClock(arr_estimate=a2, dep_estimate=d2))
        codes = [code for code, _ in self.push.ways[line].tunnel.stops]
        push = tunnel.TunnelPush(self.net, vr.TUNNELS)
        out = []
        for now in (t + 15, t + 60, t + 200, t + 600):
            rec = {"vehicle_id": number, "latitude": dark[0], "longitude": dark[1],
                   "in_service": True, "observed_at": iso(t)}
            push.apply({"vehicles": {number: rec}}, [SimpleNamespace(vehicle_id=number, line=line)],
                       {number: {codes[0]: c1, codes[1]: c2}}, now)
            out.append(rec)
        return push.ways[line], out

    def test_line_i_8804(self):
        way, recs = self.passage("I", "8804-12", 1791770558, (60.322706, 25.012347),
                                 (111, 44, 97, 20))
        self.check(way, recs)

    def test_line_p_8601(self):
        way, recs = self.passage("P", "8601-12", 1791769587, (60.309588, 24.896446),
                                 (130, 26, 97, 82))
        self.check(way, recs)

    def check(self, way, recs):
        s = [along(way, r) for r in recs]
        self.assertTrue(all(r["position_source"] == "estimated" for r in recs))
        self.assertEqual(s, sorted(s))
        for r in recs:
            self.assertLess(self.net.snap(r["latitude"], r["longitude"])[0][0], 2.0)
            if "track_path" in r:
                self.assertEqual(r["track_path"][-1], [r["latitude"], r["longitude"]])
        # Ten minutes on: held where the quickest train came back, past the far portal.
        self.assertGreater(s[-1] - way.portal_out, 100)
        self.assertLess(s[-1] - way.portal_out, 250)


if __name__ == "__main__":
    unittest.main()

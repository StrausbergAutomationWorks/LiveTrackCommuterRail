"""plausible: a train kept forward along its own line at a train's speed, its arrow the way
its stops run (Lee 2026-10-20, Madrid: "super sonic speeds and change direction")."""

import math
import os
import unittest
from datetime import datetime, timezone

from _load import load

pl = load("plausible")
base = load("operators.base")
ops = load("operators")
K = 6371008.8 * math.pi / 180
KX = K * math.cos(math.radians(40.0))


def at(m, north=0.0):
    return (40.0 + north / K, -3.0 + m / KX)


LINE = [list(at(i * 1000)) for i in range(11)]          # 10 km east along 40 N
OTHER = [list(at(0, 5000)), list(at(10000, 5000))]       # another line 5 km north


def static(**extra):
    st = {"fetched_at": 1, "rail_shapes": [LINE, OTHER],
          "trip_shapes": {"T": [0, 0], "R": [0, 1], "X": [1, 0]},
          "sched": {"T": {"A": 100, "B": 200, "C": 300}, "R": {"C": 100, "B": 200, "A": 300},
                    "X": {"D": 100}},
          "stop_pos": {"A": list(at(0)), "B": list(at(5000)), "C": list(at(10000)), "D": list(at(0, 5000))}}
    st.update(extra)
    return st


def obs(m, t=0, trip="T", vid="v", north=0.0):
    lat, lon = at(m, north)
    return base.Obs(vehicle_id=vid, lat=lat, lon=lon, in_service=True, trip_id=trip,
                    observed_at=datetime.fromtimestamp(1792000000 + t, timezone.utc))


class DirectionTests(unittest.TestCase):
    def test_from_the_stops(self):
        st = static()
        self.assertEqual(pl.direction(st, "T"), 1)
        self.assertEqual(pl.direction(st, "R"), -1)

    def test_none_without_the_means(self):
        st = static()
        self.assertIsNone(pl.direction(st, "X"))           # one stop
        self.assertIsNone(pl.direction(st, "NOPE"))
        self.assertIsNone(pl.direction(None, "T"))
        self.assertIsNone(pl.direction(static(stop_pos={}), "T"))

    def test_stops_in_time_order_not_listed_order(self):
        st = static(sched={"T": {"C": 300, "A": 100, "B": 200}}, fetched_at=7)
        self.assertEqual(pl.direction(st, "T"), 1)

    def test_cached_per_timetable(self):
        a = static()
        b = static(sched={"T": {"C": 100, "A": 200}})
        self.assertEqual(pl.direction(a, "T"), 1)
        self.assertEqual(pl.direction(b, "T"), -1)


class FilterTests(unittest.TestCase):
    def setUp(self):
        self.st = static()
        self.p = pl.Plausible()

    def run1(self, o, now):
        return self.p.filter([o], self.st, now)

    def test_forward_at_a_train_speed_passes(self):
        self.assertEqual(self.run1(obs(1000, 0), 0)[0].lon, at(1000)[1])
        got = self.run1(obs(2500, 60), 60)[0]                 # 1.5 km in 60 s: 90 km/h
        self.assertEqual((got.lat, got.lon), at(2500))
        self.assertEqual(self.p.refused, 0)

    def test_back_along_the_line_is_refused_and_held(self):
        first = obs(3000, 0)
        self.run1(first, 0)
        got = self.run1(obs(2800, 30), 30)[0]                 # 200 m back
        self.assertEqual((got.lat, got.lon, got.observed_at), (first.lat, first.lon, first.observed_at))
        self.assertEqual(self.p.refused, 1)

    def test_a_little_back_is_noise_and_passes(self):
        self.run1(obs(3000, 0), 0)
        got = self.run1(obs(2920, 30), 30)[0]                 # 80 m back
        self.assertEqual((got.lat, got.lon), at(2920))
        self.assertEqual(self.p.refused, 0)

    def test_too_fast_forward_is_refused(self):
        first = obs(1000, 0)
        self.run1(first, 0)
        got = self.run1(obs(6000, 30), 30)[0]                 # 5 km in 30 s
        self.assertEqual((got.lat, got.lon), (first.lat, first.lon))
        self.assertEqual(self.p.refused, 1)

    def test_timed_from_when_the_train_was_first_seen_there(self):
        self.run1(obs(1000, 0), 0)
        for t in range(30, 330, 30):
            self.run1(obs(1000, t), t)                        # stands 5 minutes
        got = self.run1(obs(6000, 330), 330)[0]               # 5 km since 0 s: 55 km/h
        self.assertEqual((got.lat, got.lon), at(6000))

    def test_speed_limit_boundary(self):
        self.run1(obs(0, 0), 0)
        ok = pl.MAX_KMH / 3.6 * 100 * 0.99
        self.assertEqual(self.run1(obs(ok, 100), 100)[0].lon, at(ok)[1])
        p2 = pl.Plausible()
        p2.filter([obs(0, 0)], self.st, 0)
        bad = pl.MAX_KMH / 3.6 * 100 * 1.01
        self.assertEqual(p2.filter([obs(bad, 100)], self.st, 100)[0].lon, at(0)[1])

    def test_off_its_own_line_is_refused(self):
        first = obs(2000, 0)
        self.run1(first, 0)
        got = self.run1(obs(2100, 30, north=5000), 30)[0]     # on the OTHER line
        self.assertEqual((got.lat, got.lon), (first.lat, first.lon))
        got = self.run1(obs(2100, 60, north=160), 60)[0]
        self.assertEqual((got.lat, got.lon), (first.lat, first.lon))
        got = self.run1(obs(2100, 90, north=140), 90)[0]
        self.assertEqual((got.lat, got.lon), at(2100, 140))

    def test_a_first_fix_off_its_line_is_left_out(self):
        self.assertEqual(self.run1(obs(2000, 0, north=5000), 0), [])
        self.assertEqual(self.p.refused, 1)

    def test_the_hold_runs_out(self):
        # Refused fixes that disagree with each other (two at the same spot would agree and
        # be taken as the train).
        self.run1(obs(3000, 0), 0)
        self.assertEqual(len(self.run1(obs(2000, pl.HOLD_S), pl.HOLD_S)), 1)
        self.assertEqual(self.run1(obs(1500, pl.HOLD_S + 1), pl.HOLD_S + 1), [])
        self.assertEqual(self.p.confirmed, 0)

    def test_refused_fixes_that_agree_are_the_train(self):
        self.run1(obs(8000, 0), 0)                            # a wrong first fix, far ahead
        n = pl.CONFIRM
        for i in range(1, n):                                 # refused, each agreeing
            got = self.run1(obs(1000 + 100 * i, 30 * i), 30 * i)[0]
            self.assertEqual(got.lon, at(8000)[1])
        got = self.run1(obs(1000 + 100 * n, 30 * n), 30 * n)[0]
        self.assertEqual((got.lat, got.lon), at(1000 + 100 * n))
        self.assertEqual(self.p.confirmed, 1)
        got = self.run1(obs(1100 + 100 * n, 30 * n + 30), 30 * n + 30)[0]
        self.assertEqual((got.lat, got.lon), at(1100 + 100 * n))

    def test_disagreeing_refusals_never_confirm(self):
        self.run1(obs(8000, 0), 0)
        for i in range(1, 3 * pl.CONFIRM):
            m = 1000 if i % 2 else 6000                       # 5 km apart, every 30 s
            got = self.run1(obs(m, 30 * i), 30 * i)[0]
            self.assertEqual(got.lon, at(8000)[1])
        self.assertEqual(self.p.confirmed, 0)

    def test_six_to_confirm(self):
        self.assertEqual(pl.CONFIRM, 6)

    def test_a_bounce_never_confirms(self):
        self.run1(obs(3000, 0), 0)
        for i, m in enumerate([2400, 3050, 2400, 3060, 2400]):
            got = self.run1(obs(m, 30 * (i + 1)), 30 * (i + 1))[0]
            self.assertGreaterEqual(got.lon, at(3000)[1])
        self.assertEqual(self.p.confirmed, 0)

    def test_a_reversed_trip_runs_the_other_way(self):
        self.p.filter([obs(8000, 0, trip="R")], self.st, 0)
        got = self.p.filter([obs(7000, 60, trip="R")], self.st, 60)[0]
        self.assertEqual((got.lat, got.lon), at(7000))
        got = self.p.filter([obs(7500, 90, trip="R")], self.st, 90)[0]
        self.assertEqual((got.lat, got.lon), at(7000))

    def test_unjudged_without_a_shape_or_direction(self):
        for o in (obs(2000, 0, trip="X"), obs(2000, 0, trip="NOPE"), obs(2000, 0, trip=None)):
            self.assertIs(self.p.filter([o], self.st, 0)[0], o)
        o = obs(9000, 30)
        self.assertIs(self.p.filter([o], None, 30)[0], o)

    def test_forgotten_after_a_while(self):
        self.run1(obs(3000, 0), 0)
        self.p.filter([obs(5000, 0, vid="w")], self.st, pl.FORGET_S + 1)
        got = self.run1(obs(1000, pl.FORGET_S + 2), pl.FORGET_S + 2)[0]
        self.assertEqual((got.lat, got.lon), at(1000))         # a new start, not a step back


class PlaceholderTests(unittest.TestCase):
    def setUp(self):
        self.st = static()
        self.p = pl.Plausible()

    def test_a_placeholder_is_held_not_taken(self):
        first = obs(1000, 0)
        self.p.filter([first], self.st, 0)
        got = self.p.filter([obs(3000, 30)], self.st, 30, untrusted={"v"})[0]
        self.assertEqual((got.lat, got.lon, got.observed_at), (first.lat, first.lon, first.observed_at))
        self.assertEqual((self.p.placeholders, self.p.refused, self.p.confirmed), (1, 0, 0))
        got = self.p.filter([obs(1200, 60)], self.st, 60)[0]   # the real one after it
        self.assertEqual((got.lat, got.lon), at(1200))

    def test_placeholders_never_confirm(self):
        self.p.filter([obs(5000, 0)], self.st, 0)
        self.p.filter([obs(1000, 30)], self.st, 30)              # refused, a candidate
        for t in (60, 90, 120):
            got = self.p.filter([obs(1000, t)], self.st, t, untrusted={"v"})[0]
            self.assertEqual(got.lon, at(5000)[1])
        self.assertEqual(self.p.confirmed, 0)

    def test_nothing_better_shows_the_placeholder_provisionally(self):
        # Held, 23% of the replay's records went missing: shown, until a real fix.
        got = self.p.filter([obs(4000, 0)], self.st, 0, untrusted={"v"})[0]
        self.assertEqual((got.lat, got.lon), at(4000))
        got = self.p.filter([obs(2500, 30)], self.st, 30)[0]        # behind it, and real
        self.assertEqual((got.lat, got.lon), at(2500))
        got = self.p.filter([obs(2300, 60)], self.st, 60)[0]        # back again: judged now
        self.assertEqual((got.lat, got.lon), at(2500))

    def test_a_placeholder_follows_a_placeholder(self):
        self.p.filter([obs(4000, 0)], self.st, 0, untrusted={"v"})
        got = self.p.filter([obs(6000, 30)], self.st, 30, untrusted={"v"})[0]
        self.assertEqual((got.lat, got.lon), at(6000))

    def test_a_placeholder_off_its_line_is_left_out(self):
        self.assertEqual(self.p.filter([obs(1000, 0, north=5000)], self.st, 0, untrusted={"v"}), [])

    def test_after_the_hold_the_placeholder_shows(self):
        self.p.filter([obs(1000, 0)], self.st, 0)
        got = self.p.filter([obs(3000, pl.HOLD_S)], self.st, pl.HOLD_S, untrusted={"v"})[0]
        self.assertEqual(got.lon, at(1000)[1])
        got = self.p.filter([obs(3000, pl.HOLD_S + 1)], self.st, pl.HOLD_S + 1, untrusted={"v"})[0]
        self.assertEqual(got.lon, at(3000)[1])

    def test_others_unaffected(self):
        self.p.filter([obs(1000, 0, vid="w")], self.st, 0)
        got = self.p.filter([obs(1200, 60, vid="w")], self.st, 60, untrusted={"v"})[0]
        self.assertEqual((got.lat, got.lon), at(1200))

    def test_renfe_reads_incoming_at(self):
        from google.transit import gtfs_realtime_pb2 as pb
        rn = load("operators.renfe")
        fm = pb.FeedMessage()
        for trip, status in (("A1", 0), ("B2", 1), ("C3", 2), (" D4 ", 0), ("", 0)):
            e = fm.entity.add()
            e.vehicle.trip.trip_id = trip
            e.vehicle.current_status = status
        e = fm.entity.add()
        e.vehicle.trip.trip_id = "E5"                            # no status: not a placeholder
        fm.entity.add().trip_update.trip.trip_id = "F6"
        self.assertEqual(rn.incoming_ids(fm), {"A1", "D4"})
        self.assertIs(ops.OPERATORS["renfe_madrid"].untrusted_fixes, rn.incoming_ids)


class ArrowTests(unittest.TestCase):
    def rec(self, m, **kw):
        lat, lon = at(m)
        r = {"latitude": lat, "longitude": lon, "icon_rotation_deg": 12.0, "icon_rotation_basis": "course",
             "course_deg": 12.0}
        r.update(kw)
        return r

    def test_the_way_the_stops_run(self):
        res = {"vehicles": {"a": self.rec(3000), "b": self.rec(3000)}}
        pl.Plausible().apply_arrows(res, [obs(3000, vid="a"), obs(3000, vid="b", trip="R")], static())
        self.assertAlmostEqual(res["vehicles"]["a"]["icon_rotation_deg"], 90.0, delta=0.5)
        self.assertAlmostEqual(res["vehicles"]["a"]["course_deg"], 90.0, delta=0.5)
        self.assertAlmostEqual(res["vehicles"]["b"]["icon_rotation_deg"], 270.0, delta=0.5)
        self.assertEqual(res["vehicles"]["b"]["icon_rotation_basis"], "course")

    def test_basis_held_when_none(self):
        r = self.rec(3000)
        del r["icon_rotation_basis"], r["course_deg"]
        res = {"vehicles": {"a": r}}
        pl.Plausible().apply_arrows(res, [obs(3000, vid="a")], static())
        self.assertEqual(r["icon_rotation_basis"], "held")
        self.assertNotIn("course_deg", r)

    def test_no_direction_no_arrow(self):
        res = {"vehicles": {"x": self.rec(0, latitude=at(0, 5000)[0])}}
        pl.Plausible().apply_arrows(res, [obs(0, vid="x", trip="X")], static())
        for k in ("icon_rotation_deg", "icon_rotation_basis", "course_deg"):
            self.assertNotIn(k, res["vehicles"]["x"])

    def test_others_untouched(self):
        r = self.rec(3000)
        res = {"vehicles": {"n": r}}
        pl.Plausible().apply_arrows(res, [obs(3000, vid="n", trip="NOPE")], static())
        self.assertEqual(r["icon_rotation_deg"], 12.0)

    def test_point_at_clamps(self):
        ln = load("shapepath").Line(LINE)
        self.assertEqual(pl.point_at(ln, -50), tuple(LINE[0]))
        self.assertEqual(pl.point_at(ln, ln.length + 50), tuple(LINE[-1]))


class WiringTests(unittest.TestCase):
    def test_renfe_only(self):
        for op in ops.OPERATORS.values():
            self.assertEqual(op.plausible, op.source == base.SOURCE_RENFE, op.id)

    def test_the_coordinator_order(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "custom_components",
                            "live_track_commuter_rail", "coordinator.py")
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        i_fresh = src.index("poll.fresh_only(op.parse(feed)")
        i_filter = src.index("observations = self._plausible.filter(\n"
                             "                observations, static, now,\n"
                             "                untrusted=op.untrusted_fixes(feed) if op.untrusted_fixes is not None else ())")
        i_fleet = src.index("result = self.fleet.update(")
        i_dec = src.index("poll.decorate_all(result")
        i_arrow = src.index("self._plausible.apply_arrows(result, observations, static)")
        i_path = src.index("shapepath.add_shape_paths(")
        self.assertTrue(i_fresh < i_filter < i_fleet < i_dec < i_arrow < i_path)
        self.assertIn("self._plausible = plausible.Plausible() if op.plausible else None", src)


if __name__ == "__main__":
    unittest.main()

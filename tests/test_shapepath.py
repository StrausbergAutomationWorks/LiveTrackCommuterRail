"""shapepath: track_path along the trip's own shape (Lee 2026-10-20: "A train cannot exist
off of the tracks"), rail.trip_shapes, and the coordinator's use of it."""

import io
import math
import os
import unittest
import zipfile
from collections import namedtuple

from _load import load

sp = load("shapepath")
rail = load("rail")

Obs = namedtuple("Obs", "vehicle_id trip_id")
K = 6371008.8 * math.pi / 180

# An L: east 0.01 degrees of longitude along 40.0 N (853 m), then north 0.01 (1,112 m).
L_SHAPE = [[40.0, -3.0], [40.0, -2.99], [40.01, -2.99]]
# A U: east 853 m, north 33 m, back west 853 m. The legs are 33 m apart, both inside SNAP_M.
U_SHAPE = [[40.0, -3.0], [40.0, -2.99], [40.0003, -2.99], [40.0003, -3.0]]


def static(**trips):
    return {"fetched_at": 1, "rail_shapes": [L_SHAPE, U_SHAPE], "trip_shapes": dict(trips)}


def metres(a, b):
    kx = K * math.cos(math.radians(a[0]))
    return math.hypot((b[1] - a[1]) * kx, (b[0] - a[0]) * K)


def off_shape(p, shape):
    return min(sp.Line(shape).project(*p)[1] for _ in [0])


class TripPathTests(unittest.TestCase):
    def setUp(self):
        self.st = static(T1=[0, 0], T2=[0, 1], U=[1, 0])

    def test_round_the_corner_on_the_shape(self):
        start, end = (40.0, -2.995), (40.005, -2.99)
        p = sp.trip_path(self.st, "T1", start, end)
        self.assertEqual(p[0], [40.0, -2.995])
        self.assertEqual(p[-1], [40.005, -2.99])
        self.assertIn([40.0, -2.99], p)                       # the corner, not the diagonal
        for q in p:
            self.assertLess(off_shape(q, L_SHAPE), 0.5)

    def test_either_way_along_the_shape(self):
        # Renfe gives both directions of a line one shape: the shape's order is not the
        # train's (ltcr_shape_replay.txt, the first run).
        back = [[40.005, -2.99], [40.0, -2.99], [40.0, -2.995]]
        self.assertEqual(sp.trip_path(self.st, "T1", (40.005, -2.99), (40.0, -2.995)), back)
        self.assertEqual(sp.trip_path(self.st, "T2", (40.005, -2.99), (40.0, -2.995)), back)
        self.assertEqual(sp.trip_path(self.st, "T2", (40.0, -2.995), (40.005, -2.99)), back[::-1])

    def test_a_short_step_back_follows_the_shape_too(self):
        self.assertEqual(sp.trip_path(self.st, "T1", (40.0, -2.995), (40.0, -2.9952)),
                         [[40.0, -2.995], [40.0, -2.9952]])

    def test_under_the_minimum_move_no_path(self):
        d = 4.0 / (K * math.cos(math.radians(40.0)))         # 4 m east
        self.assertIsNone(sp.trip_path(self.st, "T1", (40.0, -2.995), (40.0, -2.995 + d)))
        d = 6.0 / (K * math.cos(math.radians(40.0)))         # 6 m east
        self.assertIsNotNone(sp.trip_path(self.st, "T1", (40.0, -2.995), (40.0, -2.995 + d)))

    def test_a_fix_off_the_shape_is_not_routed(self):
        far = 51.0 / K
        near = 49.0 / K
        self.assertIsNone(sp.trip_path(self.st, "T1", (40.0 + far, -2.995), (40.005, -2.99)))
        self.assertIsNone(sp.trip_path(self.st, "T1", (40.0, -2.995), (40.005, -2.99 + far / 0.766)))
        p = sp.trip_path(self.st, "T1", (40.0 + near, -2.995), (40.005, -2.99))
        self.assertEqual(p[0], [round(40.0 + near, 6), -2.995])

    def test_out_of_reach_along_the_shape_no_path(self):
        # 33 m apart in a straight line, 1,706 m apart along the U: farther than reach.
        self.assertIsNone(sp.trip_path(self.st, "U", (40.0, -2.9999), (40.0003, -2.9999)))

    def test_the_nearer_wrong_leg_is_not_taken(self):
        # The end is 28 m from the outbound leg and 5 m from the return leg; it is reached
        # along the outbound leg, never round the U.
        p = sp.trip_path(self.st, "U", (40.0, -2.998), (40.00025, -2.997))
        self.assertIsNotNone(p)
        self.assertEqual(len(p), 2)
        self.assertNotIn([40.0, -2.99], p)
        self.assertNotIn([40.0003, -2.99], p)

    def test_the_nearer_wrong_leg_behind_is_not_taken(self):
        # From the return leg: the end is 5 m from the outbound leg (behind, along the
        # shape) and 28 m from the return leg; it is reached along the return leg.
        p = sp.trip_path(self.st, "U", (40.0003, -2.997), (40.00005, -2.998))
        self.assertIsNotNone(p)
        self.assertEqual(len(p), 2)
        self.assertNotIn([40.0, -2.99], p)
        self.assertNotIn([40.0003, -2.99], p)

    def test_a_horseshoe_curve_is_followed(self):
        # Two legs 47 degrees apart: points 1,250 m out on each are 1,000 m apart in a
        # straight line and 2,500 m along the track - past straight + DETOUR_MIN_M, inside
        # DETOUR_FACTOR times the straight line.
        def at(east_m, north_m):
            return (40.0 + north_m / K, -3.0 + east_m / (K * math.cos(math.radians(40.0))))
        h = math.radians(23.578)
        leg = lambda r, s: at(r * math.cos(h), s * r * math.sin(h))  # noqa: E731
        shape = [list(leg(1500, 1)), list(at(0, 0)), list(leg(1500, -1))]
        st = {"fetched_at": 3, "rail_shapes": [shape], "trip_shapes": {"H": [0, 0]}}
        a, b = leg(1250, 1), leg(1250, -1)
        self.assertAlmostEqual(metres(a, b), 1000, delta=5)
        p = sp.trip_path(st, "H", a, b)
        self.assertIsNotNone(p)
        self.assertIn([round(x, 6) for x in at(0, 0)], p)

    def test_the_far_leg_is_reached_round_the_turn(self):
        p = sp.trip_path(self.st, "U", (40.0, -2.992), (40.0003, -2.992))
        self.assertEqual(p, [[40.0, -2.992], [40.0, -2.99], [40.0003, -2.99], [40.0003, -2.992]])

    def test_no_way_without_a_trip_or_a_shape(self):
        s, e = (40.0, -2.995), (40.005, -2.99)
        self.assertIsNone(sp.trip_path(self.st, "NOPE", s, e))
        self.assertIsNone(sp.trip_path(self.st, None, s, e))
        self.assertIsNone(sp.trip_path(None, "T1", s, e))
        self.assertIsNone(sp.trip_path({"rail_shapes": [L_SHAPE]}, "T1", s, e))
        self.assertIsNone(sp.trip_path(static(T1=[7, 0]), "T1", s, e))
        self.assertIsNone(sp.trip_path(static(T1=[-1, 0]), "T1", s, e))
        self.assertIsNone(sp.trip_path(self.st, "T1", s, s))

    def test_a_long_wiggle_is_cut_to_the_contract(self):
        # 1.5 m zigzag at 1 m spacing: 1.8 times the straight line (inside DETOUR_FACTOR),
        # every point kept at the 1 m tolerance, so it must be cut to MAX_POINTS.
        pts = [[40.0 + (1.5 / K if i % 2 else 0.0), -3.0 + i * 1.0 / (K * 0.766)] for i in range(2000)]
        st = {"fetched_at": 2, "rail_shapes": [pts], "trip_shapes": {"W": [0, 0]}}
        p = sp.trip_path(st, "W", tuple(pts[2]), tuple(pts[1990]))
        self.assertIsNotNone(p)
        self.assertLessEqual(len(p), sp.MAX_POINTS)
        self.assertGreaterEqual(len(p), 2)
        self.assertEqual(p[-1], pts[1990])

    def test_points_rounded_the_end_exact(self):
        end = (40.0051234567, -2.99)
        p = sp.trip_path(self.st, "T1", (40.0, -2.9951234567), end)
        self.assertEqual(p[0], [40.0, -2.995123])
        self.assertEqual(p[-1], [40.0051234567, -2.99])

    def test_lines_are_per_timetable(self):
        a = {"fetched_at": 5, "rail_shapes": [L_SHAPE], "trip_shapes": {"T": [0, 0]}}
        b = {"fetched_at": 5, "rail_shapes": [U_SHAPE], "trip_shapes": {"T": [0, 0]}}
        self.assertIn([40.0, -2.99], sp.trip_path(a, "T", (40.0, -2.995), (40.005, -2.99)))
        self.assertEqual(sp.trip_path(b, "T", (40.0, -2.992), (40.0003, -2.992))[1], [40.0, -2.99])
        self.assertIsNone(sp.trip_path(b, "T", (40.0, -2.995), (40.005, -2.99)))


class LineTests(unittest.TestCase):
    def test_projection_within_a_stretch(self):
        ln = sp.Line(U_SHAPE)
        whole = ln.project(40.00025, -2.997)
        part = ln.project(40.00025, -2.997, 0, 800)
        self.assertGreater(whole[0], 1000)
        self.assertLess(whole[1], 6)
        self.assertLess(part[0], 800)
        self.assertGreater(part[1], 25)
        self.assertIsNone(ln.project(40.0, -3.0, ln.length + 10, ln.length + 20))

    def test_between_both_ways(self):
        ln = sp.Line(L_SHAPE)
        self.assertEqual(ln.between(10, ln.length - 10), [(40.0, -2.99)])
        self.assertEqual(ln.between(ln.length - 10, 10), [(40.0, -2.99)])
        self.assertEqual(ln.between(0, 100), [])
        self.assertEqual(ln.between(-1, ln.length + 1), [(40.0, -3.0), (40.0, -2.99), (40.01, -2.99)])
        self.assertEqual(ln.between(ln.length + 1, -1), [(40.01, -2.99), (40.0, -2.99), (40.0, -3.0)])


class AddShapePathsTests(unittest.TestCase):
    def rec(self, **kw):
        r = {"latitude": 40.005, "longitude": -2.99, "previous_latitude": 40.0,
             "previous_longitude": -2.995, "segment_duration_s": 60}
        r.update(kw)
        return r

    def test_paths_on_moved_records_only(self):
        st = static(T1=[0, 0])
        res = {"vehicles": {"a": self.rec(), "b": {"latitude": 40.0, "longitude": -2.995},
                            "c": self.rec(track_path=[[1, 1], [2, 2]])}}
        obs = [Obs("a", "T1"), Obs("b", "T1"), Obs("c", "NOPE")]
        self.assertEqual(sp.add_shape_paths(res, obs, st), 1)
        self.assertIn([40.0, -2.99], res["vehicles"]["a"]["track_path"])
        self.assertNotIn("track_path", res["vehicles"]["b"])
        self.assertNotIn("track_path", res["vehicles"]["c"])     # an old one never survives

    def test_a_jump_still_follows_the_shape(self):
        # Renfe's modelled positions catch up in jumps; along the trip's shape a long way
        # is still on the track (4,168 refused over 200 km/h in the first replay).
        st = static(T1=[0, 0])
        res = {"vehicles": {"a": self.rec(segment_duration_s=5)}}
        self.assertEqual(sp.add_shape_paths(res, [Obs("a", "T1")], st), 1)

    def test_nothing_without_trip_shapes(self):
        res = {"vehicles": {"a": self.rec()}}
        self.assertEqual(sp.add_shape_paths(res, [Obs("a", "T1")], None), 0)
        self.assertEqual(sp.add_shape_paths(res, [Obs("a", "T1")], {"rail_shapes": [L_SHAPE]}), 0)
        self.assertEqual(sp.add_shape_paths({}, [], static(T1=[0, 0])), 0)


def _zip(trips_txt):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("trips.txt", trips_txt)
    return b.getvalue()


class TripShapesTests(unittest.TestCase):
    TRIPS = ("route_id, service_id, trip_id, shape_id\n"
             "R1, S, 1090L1C5  , SH1\n"
             "R1, S, T2, SH2\n"
             "R1, S, T3, \n"
             "R1, S, T4, NOSHAPE\n")

    def test_padded_ids_reversed_lines_missing_shapes(self):
        got = rail.trip_shapes(_zip(self.TRIPS), {"SH1": [0, 0], "SH2": [0, 1]})
        self.assertEqual(got, {"1090L1C5": [0, 0], "T2": [0, 1]})

    def test_kept_trips_only(self):
        got = rail.trip_shapes(_zip(self.TRIPS), {"SH1": [0, 0], "SH2": [0, 1]}, {"T2": 1})
        self.assertEqual(got, {"T2": [0, 1]})

    def test_nothing_without_trips_or_shapes(self):
        self.assertEqual(rail.trip_shapes(_zip(self.TRIPS), {}), {})
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("stops.txt", "stop_id\n")
        self.assertEqual(rail.trip_shapes(b.getvalue(), {"SH1": [0, 0]}), {})


class CoordinatorTests(unittest.TestCase):
    def test_shapes_where_no_track_network_ships(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "custom_components",
                            "live_track_commuter_rail", "coordinator.py")
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("        if self._track_path is not None:\n"
                      "            result[\"track_paths\"] = poll.add_track_paths(result, self._track_path)\n"
                      "        else:\n", src)
        self.assertIn("result[\"track_paths\"] = shapepath.add_shape_paths(result, observations,\n"
                      "                                                              self._static.data)", src)
        # After the operator's own touches, before the tunnel push replaces anything.
        self.assertLess(src.index("poll.decorate_all("), src.index("shapepath.add_shape_paths("))
        self.assertLess(src.index("shapepath.add_shape_paths("), src.index("if self._push is not None:"))


if __name__ == "__main__":
    unittest.main()

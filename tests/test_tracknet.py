"""The track network and track_path (backlog 290, SSOT 8.3). No Home Assistant."""

import gzip
import importlib.util
import json
import math
import os
import pathlib
import tempfile
import unittest

from _load import load

tracknet = load("tracknet")
poll = load("poll")
attributes = load("attributes")

LAT0 = 60.2
KY = 6371000.0 * math.pi / 180
KX = KY * math.cos(math.radians(LAT0))


def ll(x, y):
    """[lat, lon] of a point x m east and y m north of 60.2 N, 24.9 E."""
    return [round(LAT0 + y / KY, 7), round(24.9 + x / KX, 7)]


def line(*xy):
    return [ll(x, y) for x, y in xy]


def length(net, pts):
    return sum(math.dist(net.xy(*a), net.xy(*b)) for a, b in zip(pts, pts[1:]))


def off(net, p):
    s = net.snap(*p)
    return s[0][0] if s else 99.0


# A through track with a switch at x=1000: T1 west of it, T2 east, D diverging gently.
SWITCH = [line((0, 0), (500, 0), (1000, 0)),
          line((1000, 0), (2000, 0)),
          line((1000, 0), (1500, 20), (2000, 60))]

# A terminus: platform stub S west of node N (x=500), and two tracks leaving N east.
TERMINUS = [line((0, 0), (500, 0)),
            line((500, 0), (1500, 0)),
            line((500, 0), (1000, 15), (1500, 50))]


class RouteTests(unittest.TestCase):

    def test_along_one_line(self):
        net = tracknet.Network([line((0, 0), (300, 0), (600, 3))], LAT0)
        p = net.route(tuple(ll(100, 1)), tuple(ll(500, 2)), 2000)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(length(net, p), 400.0, delta=2.0)

    def test_through_a_switch_forward(self):
        net = tracknet.Network(SWITCH, LAT0)
        p = net.route(tuple(ll(500, 0)), tuple(ll(1500, 20)), 3000)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(length(net, p), 1000.4, delta=2.0)
        self.assertEqual(net.last_lines, (0, 2))

    def test_never_doubles_back_through_a_switch(self):
        # From T2 to D, 20 m apart: the only way is back through the switch.
        # (Within 3,000 m: past that, a reversal at the buffer stop at x=0 is legal.)
        net = tracknet.Network(SWITCH, LAT0)
        self.assertIsNone(net.route(tuple(ll(1500, 0)), tuple(ll(1500, 20)), 3000))

    def test_reverses_at_a_buffer_stop_only(self):
        net = tracknet.Network(TERMINUS, LAT0)
        a, b = tuple(ll(900, 0)), tuple(ll(900, 12))
        p = net.route(a, b, 5000)
        self.assertIsNotNone(p)
        # In to the buffer and out again: 400 + 500 + 500 + about 400.
        self.assertAlmostEqual(length(net, p), 1800.0, delta=5.0)
        self.assertEqual(net.last_lines, (1, 0, 0, 2))
        # The penalty is counted against the limit.
        self.assertIsNone(net.route(a, b, 1950))

    def test_off_the_network(self):
        net = tracknet.Network(SWITCH, LAT0)
        self.assertIsNone(net.route(tuple(ll(500, 16)), tuple(ll(800, 0)), 5000))
        self.assertEqual(net.snap(*ll(500, 14.9))[0][1], 0)

    def test_parallel_track_is_a_candidate(self):
        net = tracknet.Network([line((0, 0), (1000, 0)), line((0, 4.5), (1000, 4.5))], LAT0)
        self.assertEqual(len(net.snap(*ll(500, 2))), 2)
        wide = tracknet.Network([line((0, 0), (1000, 0)), line((0, 10), (1000, 10))], LAT0)
        self.assertEqual(len(wide.snap(*ll(500, 3))), 2)    # 3 and 7 m: within 6 m of best
        self.assertEqual(len(wide.snap(*ll(500, -1))), 1)   # 1 and 11 m

    def test_limit(self):
        net = tracknet.Network(SWITCH, LAT0)
        self.assertIsNone(net.route(tuple(ll(0, 0)), tuple(ll(2000, 0)), 1900))
        self.assertIsNotNone(net.route(tuple(ll(0, 0)), tuple(ll(2000, 0)), 2100))


class TrackPathTests(unittest.TestCase):

    def test_starts_and_ends_at_the_positions(self):
        net = tracknet.Network(SWITCH, LAT0)
        a, b = (LAT0 + 1 / KY, 24.9 + 500 / KX), tuple(ll(1500, 21))
        p = tracknet.track_path(net, a, b, 30)
        self.assertEqual(p[0], [round(a[0], 6), round(a[1], 6)])
        self.assertEqual(p[-1], [b[0], b[1]])
        self.assertTrue(all(isinstance(x, list) and len(x) == 2 for x in p))

    def test_no_path_for_no_move_or_off_network(self):
        net = tracknet.Network(SWITCH, LAT0)
        a = tuple(ll(500, 0))
        self.assertIsNone(tracknet.track_path(net, a, a, 30))
        self.assertIsNone(tracknet.track_path(net, a, tuple(ll(800, 40)), 30))

    def test_a_jump_gets_no_path(self):
        net = tracknet.Network(SWITCH, LAT0)
        a, b = tuple(ll(0, 0)), tuple(ll(2000, 0))
        self.assertIsNone(tracknet.track_path(net, a, b, 30))      # 240 km/h
        self.assertIsNotNone(tracknet.track_path(net, a, b, 40))   # 180 km/h
        self.assertIsNotNone(tracknet.track_path(net, a, b, None))

    def test_a_long_detour_gets_no_path(self):
        net = tracknet.Network(TERMINUS, LAT0)
        self.assertIsNone(tracknet.track_path(net, tuple(ll(900, 0)), tuple(ll(900, 12)), 120))

    def test_at_most_500_points(self):
        wiggle = [(x * 3.0, 1.5 if x % 2 else -1.5) for x in range(1500)]
        net = tracknet.Network([line(*wiggle)], LAT0)
        p = tracknet.track_path(net, tuple(ll(*wiggle[1])), tuple(ll(*wiggle[1400])), None)
        self.assertLessEqual(len(p), tracknet.MAX_POINTS)
        self.assertGreaterEqual(len(p), 2)


class PollTests(unittest.TestCase):

    def _result(self, **rec):
        base = {"vehicle_id": "v", "latitude": ll(1500, 20)[0], "longitude": ll(1500, 20)[1],
                "in_service": True, "marker_label": "R"}
        return {"vehicles": {"v": dict(base, **rec)}}

    def test_path_from_the_previous_fix(self):
        net = tracknet.Network(SWITCH, LAT0)
        prev = ll(500, 0)
        res = self._result(previous_latitude=prev[0], previous_longitude=prev[1],
                           segment_duration_s=30)
        fn = lambda a, b, s: tracknet.track_path(net, a, b, s)  # noqa: E731
        self.assertEqual(poll.add_track_paths(res, fn), 1)
        rec = res["vehicles"]["v"]
        self.assertEqual(rec["track_path"][0], [round(prev[0], 6), round(prev[1], 6)])
        self.assertEqual(rec["track_path"][-1], [rec["latitude"], rec["longitude"]])
        self.assertEqual(attributes.to_attributes(rec, "vr_lahijunat")["track_path"],
                         rec["track_path"])

    def test_no_previous_fix_no_path(self):
        res = self._result(track_path=[[0, 0], [1, 1]])
        self.assertEqual(poll.add_track_paths(res, lambda a, b, s: [[0, 0], [1, 1]]), 0)
        self.assertNotIn("track_path", res["vehicles"]["v"])

    def test_no_way_no_key(self):
        res = self._result(previous_latitude=1.0, previous_longitude=2.0)
        self.assertEqual(poll.add_track_paths(res, lambda a, b, s: None), 0)
        self.assertNotIn("track_path", res["vehicles"]["v"])

    def test_no_network_changes_nothing(self):
        res = self._result(previous_latitude=1.0, previous_longitude=2.0)
        before = json.dumps(res, sort_keys=True)
        self.assertEqual(poll.add_track_paths(res, None), 0)
        self.assertEqual(json.dumps(res, sort_keys=True), before)


class ShippedNetworkTests(unittest.TestCase):

    def test_finland_loads_and_follows_the_tracks(self):
        net = tracknet.load("vr_lahijunat")
        self.assertIsNotNone(net)
        self.assertGreater(len(net), 1000)
        # Capture round 1, train 9881 near Kerava, 2026-10-12 21:36:59Z, 27 s apart:
        # the straight slide's middle is more than 15 m from any track.
        a, b = (60.433659, 25.108602), (60.439468, 25.11187)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.assertGreater(off(net, mid), 15)
        p = tracknet.track_path(net, a, b, 27)
        self.assertIsNotNone(p)
        worst = max(off(net, (u[0] + (v[0] - u[0]) * i / 10, u[1] + (v[1] - u[1]) * i / 10))
                    for u, v in zip(p, p[1:]) for i in range(11))
        self.assertLess(worst, 2.0)

    def test_the_file_credits_its_source(self):
        path = os.path.join(tracknet.TRACKS_DIR, "vr_lahijunat_tracks.json.gz")
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["format"], 1)
        self.assertIn("Fintraffic / digitraffic.fi", doc["credit"])
        self.assertIn("modified", doc["credit"])

    def test_no_file_or_wrong_format_is_none(self):
        self.assertIsNone(tracknet.load("metra"))
        old = tracknet.TRACKS_DIR
        with tempfile.TemporaryDirectory() as d:
            try:
                tracknet.TRACKS_DIR = d
                with gzip.open(os.path.join(d, "x_tracks.json.gz"), "wt") as fh:
                    json.dump({"format": 2, "lines": [line((0, 0), (10, 0))]}, fh)
                self.assertIsNone(tracknet.load("x"))
            finally:
                tracknet.TRACKS_DIR = old


class BuildTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "build_tracks.py"
        spec = importlib.util.spec_from_file_location("build_tracks", path)
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)

    def test_a_switch_on_a_track_interior_is_split_and_joined(self):
        through = {"id": "t", "name": "", "main": True,
                   "pts": [tuple(p) for p in line((0, 0), (2000, 0))]}
        branch = {"id": "b", "name": "", "main": False,
                  "pts": [tuple(p) for p in line((1000, 0.4), (1500, 20), (2000, 60))]}
        lines = self.build.simplify_round(self.build.split([through, branch]))
        self.assertEqual(len(lines), 3)
        net = tracknet.Network(lines, LAT0)
        self.assertIsNotNone(net.route(tuple(ll(500, 0)), tuple(ll(1500, 20)), 3000))
        self.assertIsNone(net.route(tuple(ll(1500, 0)), tuple(ll(1500, 20)), 2500))

    def test_ends_a_little_apart_are_joined(self):
        a = {"id": "a", "name": "", "main": True, "pts": [tuple(p) for p in line((0, 0), (500, 0))]}
        b = {"id": "b", "name": "", "main": True, "pts": [tuple(p) for p in line((500.6, 0), (1000, 0))]}
        net = tracknet.Network(self.build.simplify_round(self.build.split([a, b])), LAT0)
        self.assertIsNotNone(net.route(tuple(ll(100, 0)), tuple(ll(900, 0)), 2000))


if __name__ == "__main__":
    unittest.main()

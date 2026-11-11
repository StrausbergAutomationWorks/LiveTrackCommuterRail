"""NS's Sprinters (SSOT 15): the operator, its observations and stops, its lines from SpoorKaart, the off-rail check
and the way between fixes on them, and option B's observed_at_source and NS's speed on the map. Offline.
Run from the repo root:  python -m unittest tests.test_ns
"""

import datetime as dt
import hashlib
import pathlib
import unittest

from _load import load

ops = load("operators")
nsop = load("operators.ns")
base = load("operators.base")
lines = load("ns_lines")
shapepath = load("shapepath")
rail = load("rail")
attributes = load("attributes")

NOW = 1794389454.0
HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
STATIONS = {"DDR": {"name": "Dordrecht", "lat": 51.8076, "lon": 4.6687},
            "DDZD": {"name": "Dordrecht Zuid", "lat": 51.7907, "lon": 4.6697},
            "ZLW": {"name": "Lage Zwaluwe", "lat": 51.7115, "lon": 4.7059},
            "BD": {"name": "Breda", "lat": 51.5953, "lon": 4.7800}}


def _enc(points):
    out, pla, plo = [], 0, 0
    for la, lo in points:
        a, b = int(round(la * 1e5)), int(round(lo * 1e5))
        out.extend((a - pla, b - plo))
        pla, plo = a, b
    return out


# DDR|DDZD by a curve, stored from the lower code (DDR) to the higher (DDZD); ZLW|BD not drawn (a straight leg).
LINES = {"DDR|DDZD": _enc([(51.8076, 4.6687), (51.8000, 4.6750), (51.7907, 4.6697)]),
         "DDZD|ZLW": _enc([(51.7907, 4.6697), (51.7115, 4.7059)])}


def call(code, name, aa, ad, ea=None, ed=None):
    c = {"stop_id": code.lower(), "code": code, "name": name, "aimed_arrival": aa, "aimed_departure": ad}
    if ea is not None:
        c["expected_arrival"] = ea
    if ed is not None:
        c["expected_departure"] = ed
    return c


def train(number="6632", updated=True, **kw):
    t = {"number": number, "type": "SPR", "lat": 51.75, "lon": 4.69, "speed_kmh": 98.236, "heading": 160.0,
         "observed_at": NOW - 5, "observed_at_source": "first_seen", "operator": "ns", "trip_id": "393120570",
         "service_date": "20261111", "agency": "NS", "brand": None, "route_name": "Sprinter", "updated": updated,
         "calls": [call("DDR", "Dordrecht", None, NOW - 600, None, NOW - 540),
                   call("DDZD", "Dordrecht Zuid", NOW - 420, NOW - 400, NOW - 360, NOW - 340),
                   call("ZLW", "Lage Zwaluwe", NOW + 120, NOW + 150, NOW + 240, NOW + 270),
                   call("BD", "Breda", NOW + 700, None)],
         "path": ["DDR", "DDZD", "ZLW", "BD"]}
    t.update(kw)
    return t


class Registry(unittest.TestCase):
    def test_ns_is_registered_as_lee_named_it(self):
        op = ops.OPERATORS["ns"]
        self.assertIs(op, nsop.NS)
        self.assertEqual((op.regions, op.source, op.ns_consumer), (("NL",), base.SOURCE_NS, "commuter"))
        self.assertEqual(ops.regions_in_use()["NL"], "Netherlands")

    def test_keyed_but_never_a_url_parameter(self):
        from saw_livetrack import ns as lib
        op = ops.OPERATORS["ns"]
        self.assertTrue(op.needs_key)
        self.assertEqual(op.key_url, lib.KEY_URL)
        self.assertEqual(op.positions_url, lib.VEHICLE_URL)

    def test_credit_and_no_affiliation(self):
        op = ops.OPERATORS["ns"]
        self.assertIn("OVapi", op.attribution)
        self.assertIn("not sponsored by", op.attribution)
        self.assertFalse(op.narn)
        self.assertEqual(op.off_rail_m, 1000.0)


class Observations(unittest.TestCase):
    def test_parse(self):
        obs = nsop.parse([train(), train(), {"number": "", "lat": 1, "lon": 2}, train(number="4072", lat=None)])
        self.assertEqual(len(obs), 1)
        o = obs[0]
        self.assertEqual((o.vehicle_id, o.train, o.trip_id, o.in_service), ("6632-11", "6632", "6632-11", True))
        self.assertEqual(o.observed_at, dt.datetime.fromtimestamp(NOW - 5, dt.timezone.utc))
        self.assertEqual(o.reported_course, 160.0)

    def test_identity(self):
        self.assertEqual(lines.identity("6632", "20261101"), "6632-1")
        self.assertEqual(lines.identity("6632", None), "6632")

    def test_stops_delays_and_extras(self):
        nxt, delays, extras = nsop.ns_stops([train()], {"stops": {}}, NOW)
        self.assertEqual(nxt["6632-11"], ("Lage Zwaluwe", NOW + 240))
        self.assertEqual(delays["6632-11"], 120)
        ex = extras["6632-11"]
        self.assertEqual(ex["observed_at_source"], "first_seen")
        self.assertEqual(ex["speed_kmh"], 98.2)
        self.assertEqual(ex["line_name"], "Sprinter 6632 · Dordrecht–Breda")
        self.assertEqual(ex["marker_color"], "#FFC917")
        self.assertEqual(ex["marker_ring_color"], "#003082")

    def test_no_delay_without_the_updates(self):
        nxt, delays, extras = nsop.ns_stops([train(updated=False)], None, NOW)
        self.assertNotIn("6632-11", delays)
        self.assertIn("6632-11", nxt)

    def test_lateness_3_and_10(self):
        rec = {}
        nsop.ns_decorate(rec, None, None)
        self.assertEqual(rec, {"late_threshold_min": 3, "very_late_threshold_min": 10})


class Map(unittest.TestCase):
    def test_observed_at_source_and_speed_reach_the_map(self):
        rec = {"vehicle_id": "6632-11", "marker_label": "6632", "in_service": True,
               "observed_at": "2026-11-11T09:30:49+00:00", "observed_at_source": "first_seen", "speed_kmh": 98.2}
        a = attributes.to_attributes(rec, "ns")
        self.assertEqual((a["observed_at_source"], a["speed_kmh"]), ("first_seen", 98.2))


class Geometry(unittest.TestCase):
    def test_a_train_s_line_is_its_path_s_legs(self):
        g = lines.NsGeometry()
        d = g.update([train()], STATIONS, LINES, "v1")
        self.assertEqual(len(d["rail_shapes"]), 1)
        pts = d["rail_shapes"][0]
        self.assertEqual(pts[0], [51.8076, 4.6687])
        self.assertIn([51.8, 4.675], pts)                    # the drawn curve
        self.assertEqual(pts[-1], [51.5953, 4.78])           # ZLW to BD straight
        self.assertEqual(d["trip_shapes"], {"6632-11": [0, 0]})
        self.assertEqual(d["stops"]["ZLW"], "Lage Zwaluwe")
        self.assertEqual(set(d["stop_pos"]), {"DDR", "DDZD", "ZLW", "BD"})

    def test_one_line_per_path_and_a_new_version_starts_again(self):
        g = lines.NsGeometry()
        d = g.update([train()], STATIONS, LINES, "v1")
        v1 = d["fetched_at"]
        d = g.update([train(), train(number="6634")], STATIONS, LINES, "v1")
        self.assertEqual((len(d["rail_shapes"]), d["fetched_at"]), (1, v1))
        d = g.update([train()], STATIONS, LINES, "v2")
        self.assertEqual(len(d["rail_shapes"]), 1)
        self.assertGreater(d["fetched_at"], v1)

    def test_a_train_without_a_path_has_no_line(self):
        d = lines.NsGeometry().update([train(path=[])], STATIONS, LINES, "v1")
        self.assertEqual(d["trip_shapes"], {})

    def test_the_way_between_two_fixes_follows_the_line(self):
        d = lines.NsGeometry().update([train()], STATIONS, LINES, "v1")
        p = shapepath.trip_path(d, "6632-11", (51.8076, 4.6687), (51.7907, 4.6697))
        self.assertIsNotNone(p)
        self.assertIn([51.8, 4.675], p)

    def test_the_off_rail_check_reads_the_lines(self):
        g = lines.NsGeometry()
        check = rail.RailCheck(None, 1000.0)
        check.set_shapes(g.update([train(number="6630", path=["DDR", "DDZD"])], STATIONS, LINES, "v1"))
        self.assertFalse(check(51.70, 4.71))                 # near Lage Zwaluwe: no line there yet
        check.set_shapes(g.update([train()], STATIONS, LINES, "v1"))
        self.assertTrue(check(51.70, 4.71))


class SharedCopy(unittest.TestCase):
    def test_the_copy_is_byte_exact_with_the_reference(self):
        mine = (HERE / "shared_ns.py").read_bytes()
        import saw_livetrack
        ref = pathlib.Path(saw_livetrack.__file__).resolve().parents[2] / "reference" / "shared_ns.py"
        if not ref.exists():
            self.skipTest("the library's reference/ is not beside an installed wheel")
        self.assertEqual(hashlib.sha256(mine).hexdigest(), hashlib.sha256(ref.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

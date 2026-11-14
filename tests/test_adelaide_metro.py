"""Adelaide Metro's trains (SSOT 19): the registry entry, the feed read, the timetable extras, the look from the rail
map, direction, label, hover and lateness, the shared client's copy, the manifest. Offline.
Run from the repo root:  python -m unittest discover -s tests -p test_adelaide_metro.py
"""

import datetime as dt
import io
import json
import pathlib
import unittest
import zipfile

from google.transit import gtfs_realtime_pb2

from _load import load

from saw_livetrack.adelaide_metro import COMMUTER

ops = load("operators")
am = load("operators.adelaide_metro")
base = load("operators.base")

HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
# The library's reference copy, in a LiveTrackCore clone (AmtrakerClient) beside this one; skipped without it.
LIB_REF = pathlib.Path(__file__).resolve().parents[2] / "AmtrakerClient" / "reference" / "shared_adelaide_metro.py"

TIMETABLE = {
    "routes.txt": "route_id,agency_id,route_short_name,route_long_name,route_type,route_color,route_text_color\n"
                  "SEAFRD,2,SEAFRD,Seaford to City,2,FE5000,ffffff\n"
                  "BEL,2,BEL,Belair to City,2,509E2F,ffffff\n"
                  "NEW1,2,NEWLN,A line not on the map,2,123abc,ffffff\n",
    "trips.txt": "route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,block_id,shape_id\n"
                 "SEAFRD,8501,684256,Seaford,,1,SR1,S1\n"
                 "SEAFRD,8501,684118,City,,0,SR2,S2\n"
                 "BEL,8501,683827,,,x,BR1,S3\n"
                 "BEL,8501,999999,City,,0,BR2,S3\n"
                 "NEW1,8501,700001,City,,0,NR1,S4\n",
}


def zip_of(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


def static():
    distilled = {"sched": {"684256": [], "684118": [], "683827": [], "700001": []}}
    return {"extras": am.extras(zip_of(TIMETABLE), distilled, {})}


def feed(rows):
    fm = gtfs_realtime_pb2.FeedMessage()
    fm.header.gtfs_realtime_version = "2.0"
    fm.header.timestamp = 1794603700
    for vid, trip, route, lat, lon, bearing in rows:
        e = fm.entity.add()
        e.id = vid
        v = e.vehicle
        if vid:
            v.vehicle.id = vid
            v.vehicle.label = vid
        if trip is not None:
            v.trip.trip_id = trip
        if route is not None:
            v.trip.route_id = route
        v.position.latitude = lat
        v.position.longitude = lon
        if bearing is not None:
            v.position.bearing = bearing
        v.timestamp = 1794603690
    return fm


def obs(trip, route, vid="4006", in_service=True):
    return base.Obs(vehicle_id=vid, lat=-35.1, lon=138.48, observed_at=None, in_service=in_service, train=None,
                    line=route, reported_course=None, trip_id=trip)


class Registry(unittest.TestCase):
    def test_entry(self):
        op = ops.OPERATORS["adelaide_metro"]
        self.assertIs(op, am.ADELAIDE_METRO)
        self.assertEqual(op.name, "Adelaide Metro")
        self.assertEqual(op.regions, ("AU-SA",))
        self.assertEqual(op.source, base.SOURCE_ADELAIDE_METRO)
        self.assertEqual(op.adelaide_metro_consumer, COMMUTER)
        self.assertEqual(op.static_route_types, ("2",))
        self.assertFalse(op.needs_key)
        self.assertFalse(op.narn)
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertEqual(op.max_fix_age_s, 300)
        self.assertIn("Department for Infrastructure and Transport, South Australia", op.attribution)
        self.assertIn("CC BY 4.0", op.attribution)
        self.assertIn("not sponsored", op.attribution)
        self.assertEqual(op.terms_url, "https://www.adelaidemetro.com.au/developer-info")

    def test_region_label(self):
        self.assertEqual(base.REGIONS["AU-SA"], "Australia — South Australia")
        self.assertEqual([o.id for o in ops.operators_in("AU-SA")], ["adelaide_metro"])

    def test_the_manifest_asks_for_0_2_39(self):
        m = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("saw-livetrack[gtfs]>=0.2.39,<0.3", m["requirements"])

    @unittest.skipUnless(LIB_REF.exists(), "LiveTrackCore clone not present")
    def test_the_shared_copy_is_byte_exact(self):
        self.assertEqual((HERE / "shared_adelaide_metro.py").read_bytes(), LIB_REF.read_bytes())


class Parse(unittest.TestCase):
    def test_rows(self):
        got = am.parse(feed([("4006", "684256", "SEAFRD", -35.10, 138.48, 224.0),
                             ("3026", "", "BEL", -34.97, 138.62, None),
                             ("", "684118", "SEAFRD", -35.0, 138.5, 10.0),
                             ("4011", "684118", "SEAFRD", 0.0, 0.0, 25.0),
                             ("4014", "684300", None, -35.2, 138.5, 365.0)]))
        self.assertEqual([o.vehicle_id for o in got], ["4006", "3026", "4014"])
        a, b, c = got
        self.assertTrue(a.in_service)
        self.assertEqual((a.line, a.trip_id, a.train), ("SEAFRD", "684256", None))
        self.assertAlmostEqual(a.reported_course, 224.0)
        self.assertAlmostEqual(a.lat, -35.10, places=4)
        self.assertEqual(a.observed_at, dt.datetime.fromtimestamp(1794603690, dt.timezone.utc))
        self.assertFalse(b.in_service)
        self.assertIsNone(b.trip_id)
        self.assertIsNone(b.reported_course)
        self.assertIsNone(c.line)
        self.assertAlmostEqual(c.reported_course, 5.0)


class Extras(unittest.TestCase):
    def test_routes_and_the_window(self):
        ex = static()["extras"]
        self.assertEqual(ex["route"]["SEAFRD"], ["SEAFRD", "FE5000"])
        self.assertEqual(ex["route"]["NEW1"], ["NEWLN", "123ABC"])     # the short name, not the id
        self.assertEqual(ex["trip"]["684256"], ["SEAFRD", "1", "Seaford"])
        self.assertEqual(ex["trip"]["684118"], ["SEAFRD", "0", "City"])
        self.assertNotIn("999999", ex["trip"])          # not in the distilled window


class Look(unittest.TestCase):
    def test_the_map_colours_win(self):
        self.assertEqual(am.line_colour("BEL", "509E2F"), "#6ABF4B")
        self.assertEqual(am.line_colour("SEAFRD", "FE5000"), "#FF7F30")
        self.assertEqual(am.line_colour("FLNDRS"), "#FF7F30")
        self.assertEqual(am.line_colour("NOAR"), "#FF7F30")
        self.assertEqual(am.line_colour("GAW"), "#C23B33")
        self.assertEqual(am.line_colour("GAWC"), "#C23B33")
        self.assertEqual(am.line_colour("SALIS"), "#C23B33")
        for code in ("GRNG", "OSBORN", "OUTHA", "PTDOCK"):
            self.assertEqual(am.line_colour(code), "#007DC3", code)
        self.assertEqual(am.line_colour("gawc"), "#C23B33")

    def test_a_route_no_line_claims(self):
        self.assertEqual(am.line_colour("NEWLN", "123ABC"), "#123ABC")
        self.assertEqual(am.line_colour("NEWLN", "#123abc"), "#123ABC")
        self.assertEqual(am.line_colour("NEWLN", "12"), am.GREY)
        self.assertEqual(am.line_colour(None), am.GREY)

    def test_every_rail_route_has_a_line(self):
        self.assertEqual(set(am.ROUTE_LINE), {"BEL", "FLNDRS", "GAW", "GAWC", "GRNG", "NOAR", "OSBORN", "OUTHA",
                                              "PTDOCK", "SALIS", "SEAFRD"})
        self.assertEqual(set(am.ROUTE_LINE.values()), set(am.LINES))

    def test_direction(self):
        self.assertIs(am.toward_city(["SEAFRD", "0", "City"]), True)
        self.assertIs(am.toward_city(["SEAFRD", "1", "Seaford"]), False)
        self.assertIsNone(am.toward_city(["BEL", "x", ""]))
        self.assertIsNone(am.toward_city(None))
        self.assertIsNone(am.toward_city(["BEL"]))

    def test_look(self):
        away = am.look("#FF7F30", False)
        self.assertEqual((away["marker_color"], away["marker_ring_color"], away["marker_label_color"],
                          away["marker_label_outline_color"]), ("#FF7F30", "#FFFFFF", "#FFFFFF", "#FF7F30"))
        self.assertEqual(away["marker_ring_width"], 3)
        toward = am.look("#FF7F30", True)
        self.assertEqual((toward["marker_color"], toward["marker_ring_color"], toward["marker_label_color"],
                          toward["marker_label_outline_color"]), ("#FFFFFF", "#FF7F30", "#FF7F30", "#FFFFFF"))
        self.assertEqual((toward["marker_arrow_color"], toward["marker_arrow_outline_color"]), ("#FFFFFF", "#FF7F30"))
        self.assertEqual(am.look("#FF7F30", None), away)


class Decorate(unittest.TestCase):
    def rec(self, o, st=None):
        r = {"latitude": -35.1, "longitude": 138.48}
        am.decorate(r, o, static() if st is None else st)
        return r

    def test_leaving_the_city(self):
        r = self.rec(obs("684256", "SEAFRD"))
        self.assertEqual(r["marker_label"], "SEA")                     # Lee 2026-11-13 19:33: the first 3 letters
        self.assertEqual(r["line_name"], "SEAFRD to Seaford · railcar 4006")
        self.assertEqual((r["late_threshold_min"], r["very_late_threshold_min"]), (5, 10))
        self.assertEqual(r["marker_color"], "#FF7F30")

    def test_toward_the_city(self):
        r = self.rec(obs("684118", "SEAFRD", vid="4011"))
        self.assertEqual(r["marker_color"], "#FFFFFF")
        self.assertEqual(r["marker_ring_color"], "#FF7F30")
        self.assertEqual(r["line_name"], "SEAFRD to City · railcar 4011")

    def test_no_headsign_and_no_direction(self):
        r = self.rec(obs("683827", "BEL", vid="3026"))
        self.assertEqual(r["line_name"], "BEL · railcar 3026")
        self.assertEqual(r["marker_color"], "#6ABF4B")       # unknown: the leaving look

    def test_a_trip_the_timetable_lacks(self):
        r = self.rec(obs("555", "GAWC", vid="4003"))
        self.assertEqual(r["marker_label"], "GAW")                     # GAWC and GAW both read GAW
        self.assertEqual(r["line_name"], "GAWC · railcar 4003")
        self.assertEqual(r["marker_color"], "#C23B33")

    def test_the_route_from_the_trip_when_the_row_has_none(self):
        r = self.rec(obs("684256", None))
        self.assertEqual(r["marker_label"], "SEA")

    def test_no_timetable(self):
        r = self.rec(obs("684256", "OUTHA", vid="3011"), st={})
        self.assertEqual(r["marker_label"], "OUT")
        self.assertEqual(r["marker_color"], "#007DC3")
        self.assertEqual(r["line_name"], "OUTHA · railcar 3011")

    def test_a_route_off_the_map_its_short_name_and_its_own_colour(self):
        r = self.rec(obs("700001", "NEW1", vid="4200"))
        self.assertEqual(r["marker_label"], "NEW")
        self.assertEqual(r["line_name"], "NEWLN to City · railcar 4200")
        self.assertEqual(r["marker_ring_color"], "#123ABC")             # toward the City: the colour as the ring

    def test_not_in_service_is_left_to_fleet(self):
        r = self.rec(obs(None, None, in_service=False))
        self.assertEqual(r, {"latitude": -35.1, "longitude": 138.48})

    def test_no_route_at_all(self):
        r = self.rec(obs("555", None, vid="4100"))
        self.assertNotIn("marker_label", r)
        self.assertEqual(r["line_name"], "railcar 4100")
        self.assertEqual(r["marker_color"], am.GREY)


if __name__ == "__main__":
    unittest.main()

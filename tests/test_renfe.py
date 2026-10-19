"""Renfe (Spain): the operators per network, the service-window cut, extras and decorate.
No Home Assistant. SSOT section 10; the numbers in comments are measured there
(20_Research/ES_RENFE_CERCANIAS_FEED_20261016.md)."""

import io
import unittest
import zipfile
from datetime import date, datetime, timezone

from google.transit import gtfs_realtime_pb2 as pb

from _load import load

rn = load("operators.renfe")
ops = load("operators")
base = load("operators.base")
gtfs_filter = load("gtfs_filter")
rail = load("rail")
attributes = load("attributes")

MONDAY = date(2026, 10, 19)


def _zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return b.getvalue()


# Two networks (10 Madrid, 41 Murcia), padded as Renfe pads; Murcia C2 has a green rail
# route and a pink bus route; Valencia's white ER24 (40); a season's calendar where each
# service runs one date.
GTFS = {
    "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\n1071VC,Renfe Cercanias,https://x,Europe/Madrid\n",
    "routes.txt": ("route_id,route_short_name,route_long_name,route_type,route_color,route_text_color\n"
                   "10T0001C5  ,C5  ,Mostoles el Soto    -Humanes   ,2,FECB00,FFFFFF\n"
                   "10T0002C5  ,C5  ,Humanes    -Mostoles el Soto   ,2,FECB00,FFFFFF\n"
                   "41T0003C2  ,C2  ,Murcia del Carmen   -Aguilas   ,2,108C2C,FFFFFF\n"
                   "41T0025C2  ,C2  ,Aguilas   -Lorca-Sutullena   ,3,E93CAC,FFFFFF\n"
                   "40T0057ER24,ER24,-Xativa                        ,2,FFFFFF,FFFFFF\n"),
    "calendar.txt": ("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                     "1090L,1,0,0,0,0,0,0,20261019,20261019\n"
                     "1093J,0,0,0,1,0,0,0,20261022,20261022\n"),
    "trips.txt": ("route_id,service_id,trip_id,trip_headsign,wheelchair_accessible,block_id,shape_id\n"
                  "10T0001C5  ,1090L,1090L23743C5  ,  ,1,1,10_C5\n"
                  "10T0002C5  ,1090L,1090L23744C5  ,  ,1,1,10_C5R\n"
                  "10T0001C5  ,1093J,1093J23743C5  ,  ,1,1,10_C5\n"
                  "41T0003C2  ,1090L,4190L84000C2  ,  ,1,1,41_C2\n"
                  "41T0025C2  ,1090L,4190L84931C2  ,  ,1,1,41_BUS\n"
                  "40T0057ER24,1090L,4090L99001ER24,  ,1,1,\n"),
    "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,wheelchair_boarding\n"
                  "18000,Mostoles el Soto,40.30,-3.90,1\n18001,Humanes,40.40,-3.90,1\n"
                  "61000,Murcia del Carmen,37.97,-1.13,1\n61001,Aguilas,37.40,-1.58,1\n"
                  "65000,Xativa,38.99,-0.52,1\n99999,Unused,0.1,0.1,1\n"),
    "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                       "1090L23743C5  ,08:00:00,08:00:00,18000,001\n1090L23743C5  ,08:20:00,08:20:00,18001,002\n"
                       "1090L23744C5  ,09:00:00,09:00:00,18001,001\n1090L23744C5  ,09:20:00,09:20:00,18000,002\n"
                       "1093J23743C5  ,08:00:00,08:00:00,18000,001\n1093J23743C5  ,08:20:00,08:20:00,18001,002\n"
                       "4190L84000C2  ,10:00:00,10:00:00,61000,001\n4190L84000C2  ,11:00:00,11:00:00,61001,002\n"
                       "4190L84931C2  ,10:00:00,10:00:00,61001,001\n"
                       "4090L99001ER24,12:00:00,12:00:00,65000,001\n"),
    # 10_C5 runs due north along lon -3.9 from 40.30 to 40.40; 10_C5R is it reversed.
    "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                   "10_C5,40.30,-3.90,1\n10_C5,40.35,-3.9001,2\n10_C5,40.40,-3.90,3\n"
                   "10_C5R,40.40,-3.90,1\n10_C5R,40.35,-3.9001,2\n10_C5R,40.30,-3.90,3\n"
                   "41_C2,37.97,-1.13,1\n41_C2,37.40,-1.58,2\n"
                   "41_BUS,37.40,-1.58,1\n41_BUS,37.41,-1.59,2\n"),
}


def timetable(prefixes=("10",)):
    """What statics._distill keeps for an operator, built the same way."""
    from saw_livetrack.gtfs import distill
    raw = gtfs_filter.keep_service_window(_zip(GTFS), ("2",), today=MONDAY,
                                          route_prefixes=prefixes)
    d = distill(raw, stop_times=False, today=MONDAY)
    d["rail_shapes"], index = rail.shapes_indexed(raw)
    d["extras"] = rn.extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
    d["fetched_at"] = 1.0
    return d


def feed(rows):
    fm = pb.FeedMessage()
    fm.header.gtfs_realtime_version = "2.0"
    fm.header.timestamp = 1792310000
    for trip, lat, lon in rows:
        e = fm.entity.add()
        e.id = "VP_X"
        e.vehicle.trip.trip_id = trip
        e.vehicle.position.latitude = lat
        e.vehicle.position.longitude = lon
        e.vehicle.timestamp = 1792309998
    return fm


def rec_for(obs, moving=True):
    rec = {"vehicle_id": obs.vehicle_id, "latitude": obs.lat, "longitude": obs.lon,
           "in_service": True, "marker_label": obs.train, "train": obs.train,
           "position_jump": True}
    if moving:
        rec["course_deg"] = 12.0
        rec["icon_rotation_deg"] = 12.0
        rec["icon_rotation_basis"] = "course"
    return rec


MADRID = ops.OPERATORS["renfe_madrid"]
MURCIA = ops.OPERATORS["renfe_murcia_alicante"]


class WindowCutTests(unittest.TestCase):
    def setUp(self):
        self.z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(
            _zip(GTFS), ("2",), today=MONDAY)))

    def rows(self, name):
        return self.z.read(name).decode().splitlines()

    def test_trips_of_the_window_only(self):
        trips = [r.split(",")[2].strip() for r in self.rows("trips.txt")[1:]]
        # Thursday's run is three days out; the bus route is not route_type 2.
        self.assertEqual(sorted(trips), ["1090L23743C5", "1090L23744C5", "4090L99001ER24",
                                         "4190L84000C2"])

    def test_stop_times_kept_as_read(self):
        st = self.rows("stop_times.txt")
        self.assertEqual(st[0], "trip_id,arrival_time,departure_time,stop_id,stop_sequence")
        self.assertIn("1090L23743C5  ,08:00:00,08:00:00,18000,001", st)
        self.assertFalse(any(r.startswith("1093J") or r.startswith("4190L84931") for r in st))
        self.assertEqual(len(st), 1 + 7)

    def test_stops_used_only(self):
        ids = sorted(r.split(",")[0] for r in self.rows("stops.txt")[1:])
        self.assertEqual(ids, ["18000", "18001", "61000", "61001", "65000"])

    def test_shapes_of_kept_trips(self):
        ids = {r.split(",")[0] for r in self.rows("shapes.txt")[1:]}
        self.assertEqual(ids, {"10_C5", "10_C5R", "41_C2"})

    def test_routes_of_the_type_every_one(self):
        ids = sorted(r.split(",")[0].strip() for r in self.rows("routes.txt")[1:])
        self.assertEqual(ids, ["10T0001C5", "10T0002C5", "40T0057ER24", "41T0003C2"])

    def test_parent_stations_kept(self):
        files = dict(GTFS)
        files["stops.txt"] = ("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n"
                              "P18000,Mostoles,40.30,-3.90,1,\n18000,Mostoles 1,40.30,-3.90,0,P18000\n"
                              "18001,Humanes,40.40,-3.90,0,\nP99,Unused parent,0.1,0.1,1,\n")
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",),
                                                                        today=MONDAY)))
        ids = sorted(r.split(",")[0] for r in z.read("stops.txt").decode().splitlines()[1:])
        self.assertEqual(ids, ["18000", "18001", "P18000"])

    def test_calendar_copied_whole(self):
        self.assertEqual(len(self.rows("calendar.txt")), 3)

    def test_network_prefix(self):
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(
            _zip(GTFS), ("2",), today=MONDAY, route_prefixes=("41",))))
        trips = [r.split(",")[2].strip() for r in z.read("trips.txt").decode().splitlines()[1:]]
        self.assertEqual(trips, ["4190L84000C2"])
        routes = [r.split(",")[0].strip() for r in z.read("routes.txt").decode().splitlines()[1:]]
        self.assertEqual(routes, ["41T0003C2"])

    def test_every_type_when_none(self):
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(GTFS), None,
                                                                        today=MONDAY)))
        trips = [r.split(",")[2].strip() for r in z.read("trips.txt").decode().splitlines()[1:]]
        self.assertIn("4190L84931C2", trips)

    def test_quoted_rows_and_another_column_order(self):
        files = dict(GTFS)
        files["stop_times.txt"] = ('stop_sequence,stop_id,trip_id,arrival_time\n'
                                   '1,18000,"1090L23743C5",08:00:00\n'
                                   '2,18001,1093J23743C5,08:20:00\n')
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",),
                                                                        today=MONDAY)))
        st = z.read("stop_times.txt").decode().splitlines()
        self.assertEqual(st, ['stop_sequence,stop_id,trip_id,arrival_time',
                              '1,18000,"1090L23743C5",08:00:00'])
        stops = [r.split(",")[0] for r in z.read("stops.txt").decode().splitlines()[1:]]
        self.assertEqual(stops, ["18000"])

    def test_quoted_first_column(self):
        files = dict(GTFS)
        files["stop_times.txt"] = ('trip_id,arrival_time,departure_time,stop_id,stop_sequence\n'
                                   '"1090L23743C5",08:00:00,08:00:00,18000,1\n'
                                   '"1093J23743C5",08:00:00,08:00:00,18000,1\n\n')
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",),
                                                                        today=MONDAY)))
        self.assertEqual(z.read("stop_times.txt").decode().splitlines()[1:],
                         ['"1090L23743C5",08:00:00,08:00:00,18000,1'])

    def test_no_calendar_every_trip_runs(self):
        files = {k: v for k, v in GTFS.items() if k != "calendar.txt"}
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",),
                                                                        today=MONDAY)))
        trips = [r.split(",")[2].strip() for r in z.read("trips.txt").decode().splitlines()[1:]]
        self.assertIn("1093J23743C5", trips)

    def test_calendar_dates(self):
        files = dict(GTFS)
        files["calendar_dates.txt"] = ("service_id,date,exception_type\n"
                                       "1090L,20261019,2\n1093J,20261020,1\n")
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",),
                                                                        today=MONDAY)))
        trips = sorted(r.split(",")[2].strip() for r in z.read("trips.txt").decode().splitlines()[1:])
        self.assertEqual(trips, ["1093J23743C5"])

    def test_the_agency_date_when_none(self):
        # Without `today` the window is the agency's date: a run of today stays.
        today = datetime.now(timezone.utc).date().strftime("%Y%m%d")
        files = dict(GTFS)
        files["calendar.txt"] = ("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                                 "1090L,1,1,1,1,1,1,1,%s,%s\n" % (today, today))
        z = zipfile.ZipFile(io.BytesIO(gtfs_filter.keep_service_window(_zip(files), ("2",))))
        self.assertIn("1090L23743C5", z.read("trips.txt").decode())

    def test_distill_on_the_cut_equals_distill_on_the_whole(self):
        from saw_livetrack.gtfs import distill
        whole = distill(gtfs_filter.keep_route_types(_zip(GTFS), ("2",)), stop_times=False,
                        today=MONDAY)
        cut = distill(gtfs_filter.keep_service_window(_zip(GTFS), ("2",), today=MONDAY),
                      stop_times=False, today=MONDAY)
        self.assertEqual(whole["sched"], cut["sched"])


class ParseTests(unittest.TestCase):
    def test_own_network_only_trip_is_identity(self):
        obs = MADRID.parse(feed([("1090L23743C5", 40.35, -3.90), ("4190L84000C2", 37.9, -1.2),
                                 ("SPECIAL_50_95224R4", 41.7, 1.8), ("9090L00001C9", 40.8, -4.0)]))
        self.assertEqual([o.vehicle_id for o in obs], ["1090L23743C5", "9090L00001C9"])
        o = obs[0]
        self.assertEqual((o.trip_id, o.train, o.line, o.in_service, o.reported_course),
                         ("1090L23743C5", "23743", None, True, None))
        self.assertEqual(o.observed_at, datetime.fromtimestamp(1792309998, timezone.utc))
        # GTFS-RT positions are float32: 40.35 arrives as 40.349998.
        self.assertAlmostEqual(o.lat, 40.35, places=5)
        self.assertAlmostEqual(o.lon, -3.9, places=5)

    def test_special_trips_drawn_by_nobody(self):
        for op in ops.OPERATORS.values():
            if op.source == base.SOURCE_RENFE:
                self.assertEqual(op.parse(feed([("SPECIAL_50_95224R4", 41.7, 1.8)])), [])

    def test_null_island_and_missing_position(self):
        fm = feed([("1090L23743C5", 0.0, 0.0)])
        e = fm.entity.add()
        e.vehicle.trip.trip_id = "1090L23744C5"
        e2 = fm.entity.add()
        e2.trip_update.trip.trip_id = "1090L23743C5"
        self.assertEqual(MADRID.parse(fm), [])

    def test_padded_trip(self):
        self.assertEqual([o.vehicle_id for o in MADRID.parse(feed([(" 1090L23743C5 ", 40.3, -3.9)]))],
                         ["1090L23743C5"])


class ExtrasTests(unittest.TestCase):
    def test_extras(self):
        d = timetable(("10", "41", "40"))
        ex = d["extras"]
        self.assertEqual(ex["route"]["10T0001C5"], ["#FECB00", "#FFFFFF"])
        self.assertEqual(sorted(ex["trip"]), ["1090L23743C5", "1090L23744C5", "4090L99001ER24",
                                              "4190L84000C2"])
        self.assertEqual(ex["trip"]["4090L99001ER24"], ["40T0057ER24", -1, 0])
        self.assertEqual(ex["trip"]["1090L23743C5"][0], "10T0001C5")
        self.assertEqual(ex["line_colour"]["10 C5"], ["#FECB00", "#FFFFFF"])
        # the shape and its reverse share one line, the reverse flagged
        a, b = ex["trip"]["1090L23743C5"], ex["trip"]["1090L23744C5"]
        self.assertEqual(a[1], b[1])
        self.assertNotEqual(a[2], b[2])

    def test_line_colour_is_the_most_common(self):
        # Over EVERY trip of the zip it is given: green twice, pink once.
        files = dict(GTFS)
        files["routes.txt"] = GTFS["routes.txt"] + "41T0019C2  ,C2  ,Murcia - Lorca  ,2,E93CAC,FFFFFF\n"
        files["trips.txt"] = (GTFS["trips.txt"] + "41T0003C2  ,1093J,4193J84001C2  ,  ,1,1,41_C2\n"
                              "41T0019C2  ,1093J,4193J84002C2  ,  ,1,1,41_C2\n")
        raw = gtfs_filter.keep_route_types(_zip(files), ("2",))
        from saw_livetrack.gtfs import distill
        d = distill(raw, stop_times=False, today=MONDAY)
        _, index = rail.shapes_indexed(raw)
        ex = rn.extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
        self.assertEqual(ex["line_colour"]["41 C2"], ["#108C2C", "#FFFFFF"])

    def test_trip_map_keeps_the_window_only(self):
        # Given a zip NOT cut to the window, only the distilled window's trips are kept.
        raw = gtfs_filter.keep_route_types(_zip(GTFS), ("2",))
        from saw_livetrack.gtfs import distill
        d = distill(raw, stop_times=False, today=MONDAY)
        _, index = rail.shapes_indexed(raw)
        ex = rn.extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
        self.assertNotIn("1093J23743C5", ex["trip"])
        self.assertIn("1090L23743C5", ex["trip"])

    def test_line_colour_from_routes_without_trips(self):
        files = dict(GTFS)
        files["routes.txt"] = (GTFS["routes.txt"] + "40T0099ER25,ER25,-Xativa  ,2,ffffff,FFFFFF\n"
                               "41T0090C2  ,C2  ,Pink 1  ,2,E93CAC,FFFFFF\n"
                               "41T0091C2  ,C2  ,Pink 2  ,2,E93CAC,FFFFFF\n")
        raw = gtfs_filter.keep_service_window(_zip(files), ("2",), today=MONDAY)
        from saw_livetrack.gtfs import distill
        d = distill(raw, stop_times=False, today=MONDAY)
        _, index = rail.shapes_indexed(raw)
        ex = rn.extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
        self.assertEqual(ex["line_colour"]["40 ER25"], ["#FFFFFF", "#FFFFFF"])
        # a line with trips keeps the trips' vote, though most of its routes are pink
        self.assertEqual(ex["line_colour"]["41 C2"], ["#108C2C", "#FFFFFF"])
        self.assertEqual(ex["line_colour"]["10 C5"], ["#FECB00", "#FFFFFF"])

    def test_colour_form(self):
        self.assertEqual(rn._colour("fecb00"), "#FECB00")
        self.assertEqual(rn._colour(" #108c2c "), "#108C2C")
        for bad in ("", None, "FFF", "GGGGGG", "1234567"):
            self.assertIsNone(rn._colour(bad))


class DecorateTests(unittest.TestCase):
    def setUp(self):
        self.d = timetable(("10", "41", "40"))

    def decorate(self, trip, lat, lon, moving=True):
        o = rn.make_parse(frozenset({"10", "41", "40"}))(feed([(trip, lat, lon)]))[0]
        rec = rec_for(o, moving)
        rn.decorate(rec, o, self.d)
        return rec

    def test_route_colour_label_name(self):
        rec = self.decorate("1090L23743C5", 40.35, -3.9001)
        self.assertEqual(rec["marker_label"], "C5")
        self.assertEqual(rec["train"], "23743")
        self.assertEqual(rec["marker_color"], "#FECB00")
        self.assertEqual(rec["marker_arrow_color"], "#FECB00")
        self.assertEqual(rec["marker_label_color"], "#FFFFFF")
        self.assertEqual(rec["line_name"], "Mostoles el Soto -Humanes")
        self.assertNotIn("marker_ring_color", rec)
        self.assertNotIn("marker_label_outline_color", rec)
        self.assertNotIn("position_jump", rec)

    def test_arrow_along_the_trip_shape(self):
        north = self.decorate("1090L23743C5", 40.32, -3.90002)
        south = self.decorate("1090L23744C5", 40.32, -3.90002)
        self.assertEqual(north["icon_rotation_basis"], "course")
        self.assertTrue(north["icon_rotation_deg"] < 2 or north["icon_rotation_deg"] > 358)
        self.assertTrue(178 < south["icon_rotation_deg"] < 182)
        self.assertEqual(north["course_deg"], north["icon_rotation_deg"])

    def test_arrow_held_at_rest(self):
        rec = self.decorate("1090L23743C5", 40.32, -3.90002, moving=False)
        self.assertEqual(rec["icon_rotation_basis"], "held")
        self.assertNotIn("course_deg", rec)
        self.assertTrue(rec["icon_rotation_deg"] < 2 or rec["icon_rotation_deg"] > 358)

    def test_no_arrow_far_from_the_shape(self):
        rec = self.decorate("1090L23743C5", 41.5, -3.9)
        self.assertEqual(rec["icon_rotation_basis"], "course")     # Fleet's, untouched
        self.assertEqual(rec["icon_rotation_deg"], 12.0)

    def test_white_disc_ringed_and_outlined_black(self):
        rec = self.decorate("4090L99001ER24", 39.0, -0.5)
        self.assertEqual(rec["marker_color"], "#FFFFFF")
        self.assertEqual(rec["marker_ring_color"], "#000000")
        self.assertEqual(rec["marker_ring_width"], 1)
        self.assertIs(type(rec["marker_ring_width"]), int)
        self.assertEqual(rec["marker_label_outline_color"], "#000000")
        self.assertEqual(rec["marker_label"], "ER24")
        # no shape: Fleet's arrow left as it was
        self.assertEqual(rec["icon_rotation_deg"], 12.0)

    def test_unknown_trip_takes_the_line_colour(self):
        rec = self.decorate("1090L55555C5", 40.35, -3.9)
        self.assertEqual(rec["marker_color"], "#FECB00")
        self.assertNotIn("line_name", rec)
        self.assertEqual(rec["icon_rotation_deg"], 12.0)

    def test_unknown_line_no_look(self):
        rec = self.decorate("1090L55555C99", 40.35, -3.9)
        self.assertEqual(rec["marker_label"], "C99")
        self.assertNotIn("marker_color", rec)

    def test_no_timetable(self):
        o = MADRID.parse(feed([("1090L23743C5", 40.35, -3.9)]))[0]
        rec = rec_for(o)
        rn.decorate(rec, o, None)
        self.assertEqual(rec["marker_label"], "C5")
        self.assertNotIn("marker_color", rec)
        self.assertNotIn("position_jump", rec)

    def test_attributes_pass_the_look(self):
        rec = self.decorate("4090L99001ER24", 39.0, -0.5)
        attrs = attributes.to_attributes(rec, "renfe_valencia")
        for k in ("marker_color", "marker_ring_color", "marker_ring_width",
                  "marker_label_outline_color", "marker_label_color", "marker_arrow_color",
                  "train"):
            self.assertEqual(attrs[k], rec[k])


class OperatorTests(unittest.TestCase):
    IDS = {"renfe_madrid", "renfe_asturias", "renfe_sevilla", "renfe_cadiz", "renfe_malaga",
           "renfe_valencia", "renfe_murcia_alicante", "renfe_cartagena", "renfe_ferrol",
           "renfe_leon", "renfe_barcelona", "renfe_bilbao", "renfe_san_sebastian",
           "renfe_cantabria", "renfe_zaragoza"}

    def renfe(self):
        return [op for op in ops.OPERATORS.values() if op.source == base.SOURCE_RENFE]

    def test_ids(self):
        self.assertEqual({op.id for op in self.renfe()}, self.IDS)

    def test_every_network_once(self):
        from saw_livetrack.renfe import NETWORKS
        seen = [n for _, _, _, _, nets in rn.NETWORKS for n in nets]
        self.assertEqual(sorted(seen), sorted(NETWORKS))
        self.assertEqual(len(seen), len(set(seen)))

    def test_settings(self):
        for op in self.renfe():
            self.assertEqual(op.renfe_consumer, "commuter", op.id)
            self.assertTrue(op.static_window, op.id)
            self.assertEqual(op.static_route_types, ("2",), op.id)
            self.assertTrue(op.static_route_prefixes, op.id)
            self.assertEqual(op.static_timeout_s, 180, op.id)
            self.assertFalse(op.narn, op.id)
            self.assertEqual(op.off_rail_m, 1000.0, op.id)
            self.assertEqual(op.stall_m, float("inf"), op.id)
            self.assertIsNone(op.max_fix_age_s, op.id)
            self.assertFalse(op.needs_key, op.id)
            self.assertIsNone(op.trip_updates_url, op.id)
            self.assertIn("Renfe", op.attribution)
            self.assertIn("CC BY 4.0", op.attribution)
            self.assertTrue(op.positions_url.startswith("https://gtfsrt.renfe.com/"))

    def test_prefixes_are_the_networks(self):
        for op_id, _, _, _, nets in rn.NETWORKS:
            self.assertEqual(ops.OPERATORS[op_id].static_route_prefixes, nets)

    def test_regions(self):
        self.assertEqual([o.id for o in ops.operators_in("ES-AN")],
                         ["renfe_cadiz", "renfe_malaga", "renfe_sevilla"])
        self.assertEqual([o.id for o in ops.operators_in("ES-MC")],
                         ["renfe_cartagena", "renfe_murcia_alicante"])
        self.assertEqual([o.id for o in ops.operators_in("ES-VC")],
                         ["renfe_murcia_alicante", "renfe_valencia"])
        self.assertEqual(ops.regions_in_use()["ES-CT"], "Spain — Catalonia")

    def test_names_distinct(self):
        names = [op.name for op in self.renfe()]
        self.assertEqual(len(names), len(set(names)))
        shorts = [op.short for op in self.renfe()]
        self.assertEqual(len(shorts), len(set(shorts)))

    def test_other_sources_unchanged(self):
        for op in ops.OPERATORS.values():
            if op.source != base.SOURCE_RENFE:
                self.assertIsNone(op.renfe_consumer, op.id)
                self.assertFalse(op.static_window, op.id)
                self.assertIsNone(op.static_route_prefixes, op.id)
                self.assertEqual(op.static_timeout_s, 60, op.id)


if __name__ == "__main__":
    unittest.main()

"""SE Queensland (Queensland Rail Citytrain): the adapter, the timetable cut and extras,
the stale-fix and skipped-stop steps, and decorate. No Home Assistant.
SSOT section 9; the numbers in comments are measured there."""

import io
import unittest
import zipfile
from datetime import datetime, timezone

import feeds
from _load import load

qr = load("operators.qr_citytrain")
ops = load("operators")
poll = load("poll")
gtfs_filter = load("gtfs_filter")
rail = load("rail")
attributes = load("attributes")

HEX = "7DBC12428F13E6FACD8FDFD0866122D3"


def _zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return b.getvalue()


# A small all-modes timetable: two rail routes (one each way, one both ways), one bus.
# Line N runs due north along lon 153.0 from -27.50 to -27.40 (shape S1, in that order);
# S2 is S1 reversed.
GTFS = {
    "agency.txt": "agency_name,agency_url,agency_timezone\nTranslink,https://translink.com.au,Australia/Brisbane\n",
    "routes.txt": ("route_id,route_short_name,route_long_name,route_type,route_color\n"
                   "BRCA-5200,BRCA,Brisbane City - Caboolture,2,27855A\n"
                   "CABR-5200,CABR,Caboolture - Brisbane City,2,27855A\n"
                   "BRBR-5208,BRBR,Brisbane City - Brisbane City,2,666D8E\n"
                   "BUS-1,66,A bus,3,FF0000\n"),
    "trips.txt": ("route_id,service_id,trip_id,direction_id,shape_id\n"
                  "BRCA-5200,ALL,T-N-1,1,S1\n"
                  "CABR-5200,ALL,T-S-1,0,S2\n"
                  "BRBR-5208,ALL,T-G-1,1,S1\n"
                  "BRBR-5208,ALL,T-G-2,0,S2\n"
                  "BUS-1,ALL,BUS-T,0,BS\n"),
    "calendar.txt": ("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                     "ALL,1,1,1,1,1,1,1,20260101,20271231\n"),
    "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n"
                  "place_a,A station,-27.5,153.0,1,\n"
                  "600001,A station platform 1,-27.5,153.0,0,place_a\n"
                  "600002,B station platform 1,-27.4,153.0,0,\n"
                  "900001,A bus stop,-27.45,153.2,0,\n"),
    "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                       "T-N-1,08:00:00,08:00:00,600001,1\nT-N-1,08:10:00,08:10:00,600002,2\n"
                       "T-S-1,09:00:00,09:00:00,600002,1\nT-S-1,09:10:00,09:10:00,600001,2\n"
                       "T-G-1,10:00:00,10:00:00,600001,1\nT-G-1,10:10:00,10:10:00,600002,2\n"
                       "T-G-2,11:00:00,11:00:00,600002,1\nT-G-2,11:10:00,11:10:00,600001,2\n"
                       "BUS-T,12:00:00,12:00:00,900001,1\n"),
    "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                   "S1,-27.50,153.0,1\nS1,-27.45,153.0001,2\nS1,-27.40,153.0,3\n"
                   "S2,-27.40,153.0,1\nS2,-27.45,153.0001,2\nS2,-27.50,153.0,3\n"
                   "BS,-27.45,153.2,1\nBS,-27.46,153.21,2\n"),
}


def timetable():
    """What statics._distill keeps for this operator, built the same way."""
    distill = __import__("saw_livetrack.gtfs", fromlist=["distill"]).distill
    raw = gtfs_filter.keep_route_types(_zip(GTFS), qr.QR_CITYTRAIN.static_route_types)
    d = distill(raw, stop_times=False)
    d["rail_shapes"], index = rail.shapes_indexed(raw)
    d["extras"] = qr.extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
    d["fetched_at"] = 1
    return d


def obs(trip="T-N-1", route="BRCA-5200", lat=-27.45, lon=153.0, in_service=True,
        label="1E15", ts=None):
    return qr.Obs(f"{HEX}_{label}", lat, lon, ts, in_service,
                  train=label if in_service else None, line=route, trip_id=trip)


def rec_for(o, **extra):
    r = {"vehicle_id": o.vehicle_id, "latitude": o.lat, "longitude": o.lon,
         "in_service": o.in_service, "marker_label": o.train or o.vehicle_id}
    r.update(extra)
    return r


class Parse(unittest.TestCase):

    def setUp(self):
        fm = feeds.feed()
        feeds.vehicle(fm, "VU-1", vid=f"{HEX}_1E15", label="1E15", route="BRCA-5200",
                      trip="39074408-QR 26_27-44209-1E15", lat=-27.402393, lon=152.936554)
        feeds.vehicle(fm, "VU-2", vid=f"{HEX}_D804", label="D804", route="BRCA-5200",
                      trip="T-X", lat=0.0, lon=0.0)                       # 0,0: refused
        feeds.vehicle(fm, "VU-3", vid=None, label="1E25", trip="T-Y")     # no vehicle id
        feeds.vehicle(fm, "VU-4", vid=f"{HEX}_1SB0", label="1SB0", route="CABR-5200",
                      trip="UNPLANNED-1234", lat=-27.46, lon=153.02)
        feeds.vehicle(fm, "VU-5", vid=f"{HEX}_0000", label="0000", lat=-27.47, lon=153.03)
        self.obs = {o.vehicle_id: o for o in qr.parse(fm)}

    def test_identity_is_the_whole_vehicle_id(self):
        self.assertEqual(set(self.obs), {f"{HEX}_1E15", f"{HEX}_1SB0", f"{HEX}_0000"})

    def test_no_trip_is_not_in_service(self):
        o = self.obs[f"{HEX}_0000"]
        self.assertFalse(o.in_service)
        self.assertEqual((o.train, o.trip_id, o.line), (None, None, None))

    def test_run_number_is_the_train_route_is_the_line(self):
        o = self.obs[f"{HEX}_1E15"]
        self.assertTrue(o.in_service)
        self.assertEqual((o.train, o.line, o.trip_id),
                         ("1E15", "BRCA-5200", "39074408-QR 26_27-44209-1E15"))
        self.assertIsNone(o.reported_course)

    def test_unplanned_trip_is_in_service(self):
        self.assertEqual(self.obs[f"{HEX}_1SB0"].trip_id, "UNPLANNED-1234")


class Rules(unittest.TestCase):

    def test_interurban_by_either_end(self):
        for code in ("BDVL", "VLBR", "IPRW", "RWIP", "BRNA", "NAIP", "BRGY", "GYSP"):
            self.assertTrue(qr.interurban(f"{code}-5200"), code)
        for code in ("BRCA", "BNFG", "BRBR", "SHSH", "BDBN", "", "VAL"):
            self.assertFalse(qr.interurban(f"{code}-5200"), code)
        self.assertFalse(qr.interurban(None))

    def test_operator_declares_its_source(self):
        op = qr.QR_CITYTRAIN
        self.assertEqual(op.id, "qr_citytrain")
        self.assertFalse(op.needs_key)
        self.assertEqual(op.max_fix_age_s, 300)
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertFalse(op.narn)
        self.assertEqual(op.static_route_types, ("2",))
        self.assertGreater(op.static_max_bytes, 36_000_000)
        self.assertIsNone(op.styling)
        self.assertIs(op.decorate, qr.decorate)
        self.assertIs(op.static_extras, qr.extras)
        self.assertIn("CC BY 4.0", op.attribution)
        self.assertIn("Translink", op.attribution)
        self.assertIs(ops.OPERATORS["qr_citytrain"], op)

    def test_other_operators_keep_their_defaults(self):
        for oid in ("metra", "nictd"):
            op = ops.OPERATORS[oid]
            self.assertEqual((op.max_fix_age_s, op.off_rail_m, op.narn, op.decorate,
                              op.static_route_types, op.static_extras),
                             (None, 300.0, True, None, None, None), oid)
            self.assertEqual(op.static_max_bytes, 20 * 1024 * 1024, oid)


class Timetable(unittest.TestCase):

    def test_the_cut_keeps_rail_only(self):
        raw = gtfs_filter.keep_route_types(_zip(GTFS), ("2",))
        z = zipfile.ZipFile(io.BytesIO(raw))
        text = {n: z.read(n).decode() for n in z.namelist()}
        self.assertNotIn("BUS-1", text["routes.txt"])
        self.assertNotIn("BUS-T", text["trips.txt"] + text["stop_times.txt"])
        self.assertNotIn("900001", text["stops.txt"])
        self.assertIn("place_a,A station", text["stops.txt"])  # a parent station is kept
        self.assertNotIn("BS,", text["shapes.txt"])
        self.assertEqual(text["agency.txt"], GTFS["agency.txt"])  # copied whole
        self.assertEqual(text["stop_times.txt"].count("\n"), 9)   # header + 8 rail rows

    def test_the_cut_matches_on_stripped_values_and_keeps_rows_as_read(self):
        spaced = dict(GTFS, **{"routes.txt": ("route_id, route_type, route_color\n"
                                              "BRCA-5200, 2, 27855A\nBUS-1, 3, FF0000\n")})
        raw = gtfs_filter.keep_route_types(_zip(spaced), ("2",))
        got = zipfile.ZipFile(io.BytesIO(raw)).read("routes.txt").decode()
        self.assertEqual(got, "route_id, route_type, route_color\nBRCA-5200, 2, 27855A\n")
        spaced["trips.txt"] = ("route_id, service_id, trip_id, direction_id, shape_id\n"
                              "BRCA-5200, ALL, T-N-1, 1, S1\nBUS-1, ALL, BUS-T, 0, BS\n")
        raw = gtfs_filter.keep_route_types(_zip(spaced), ("2",))
        z = zipfile.ZipFile(io.BytesIO(raw))
        self.assertEqual(z.read("trips.txt").decode(),
                         "route_id, service_id, trip_id, direction_id, shape_id\n"
                         "BRCA-5200, ALL, T-N-1, 1, S1\n")
        self.assertEqual(z.read("stop_times.txt").decode().count("T-N-1"), 2)

    def test_extras(self):
        ex = timetable()["extras"]
        self.assertEqual(ex["route_color"]["BRBR-5208"], "666D8E")
        self.assertNotIn("BUS-1", ex["route_color"])
        self.assertEqual(ex["route_dir"], {"BRCA-5200": 1, "CABR-5200": 0})   # BRBR both ways
        self.assertNotIn("BRBR-5208", ex["route_shapes"])
        n, s = ex["trip"]["T-N-1"], ex["trip"]["T-S-1"]
        self.assertEqual(n[0], s[0])              # one line for S1 and S2...
        self.assertEqual((n[1], s[1]), (0, 1))    # ...S2 its reverse
        self.assertEqual((n[2], s[2]), (1, 0))

    def test_shapes_indexed_agrees_with_shapes_from_zip(self):
        raw = gtfs_filter.keep_route_types(_zip(GTFS), ("2",))
        lines, index = rail.shapes_indexed(raw)
        self.assertEqual(lines, rail.shapes_from_zip(raw))
        self.assertEqual(len(lines), 1)
        self.assertEqual(index, {"S1": [0, 0], "S2": [0, 1]})


class StaleAndSkipped(unittest.TestCase):

    def test_older_than_the_limit_is_refused(self):
        now = 1_800_000_000
        mk = lambda age: obs(label=str(age), ts=datetime.fromtimestamp(now - age, tz=timezone.utc))
        kept, refused = poll.fresh_only([mk(299), mk(300), mk(301), obs(label="none")], now, 300)
        self.assertEqual([o.train for o in kept], ["299", "300", "none"])
        self.assertEqual(refused, 1)

    def test_no_limit_keeps_everything(self):
        o = [obs(ts=datetime.fromtimestamp(0, tz=timezone.utc))]
        self.assertEqual(poll.fresh_only(o, 1_800_000_000, None), (o, 0))

    def test_skipped_stops_are_dropped(self):
        from google.transit import gtfs_realtime_pb2 as pb
        fm = feeds.feed()
        e = fm.entity.add()
        e.id = "tu"
        e.trip_update.trip.trip_id = "T-N-1"
        for seq, rel in ((1, 0), (2, pb.TripUpdate.StopTimeUpdate.SKIPPED), (3, 0),
                         (4, pb.TripUpdate.StopTimeUpdate.SKIPPED)):
            s = e.trip_update.stop_time_update.add()
            s.stop_sequence = seq
            s.schedule_relationship = rel
            s.arrival.time = 1_800_000_000 + seq
        self.assertEqual(poll.SKIPPED, pb.TripUpdate.StopTimeUpdate.SKIPPED)
        self.assertEqual(poll.drop_skipped(fm), 2)
        self.assertEqual([s.stop_sequence for s in e.trip_update.stop_time_update], [1, 3])
        self.assertEqual(poll.drop_skipped(None), 0)


class Decorate(unittest.TestCase):

    def setUp(self):
        self.tt = timetable()

    def run_one(self, o, **extra):
        r = rec_for(o, **extra)
        qr.decorate(r, o, self.tt)
        return r

    def test_northbound_badge_as_published(self):
        r = self.run_one(obs())
        self.assertEqual(r["marker_label"], "T1")
        self.assertEqual((r["marker_color"], r["marker_ring_color"]), ("#0A1116", "#2E9C69"))
        self.assertEqual((r["marker_label_color"], r["marker_label_outline_color"]),
                         ("#FFFFFF", "none"))
        self.assertEqual((r["marker_arrow_color"], r["marker_arrow_outline_color"]),
                         ("#2E9C69", "#000000"))
        self.assertIs(type(r["marker_ring_width"]), int)
        self.assertEqual(r["marker_ring_width"], 4)
        self.assertNotIn("marker_symbol", r)

    def test_southbound_swapped_and_outlined(self):
        r = self.run_one(obs(trip="T-S-1", route="CABR-5200"))
        self.assertEqual((r["marker_color"], r["marker_ring_color"]), ("#2E9C69", "#0A1116"))
        self.assertEqual(r["marker_label_outline_color"], "#0A1116")
        self.assertEqual(r["marker_arrow_color"], "#2E9C69")

    def test_grey_runs_are_the_star_with_no_t_number(self):
        n = self.run_one(obs(trip="T-G-1", route="BRBR-5208", label="1SB8"))
        s = self.run_one(obs(trip="T-G-2", route="BRBR-5208", label="1SB9"))
        self.assertEqual((n["marker_symbol"], n["marker_label"]), ("star", "1SB8"))
        self.assertNotIn("marker_symbol_outline_color", n)
        self.assertEqual((n["marker_color"], n["marker_ring_color"]), ("#0A1116", "#666D8E"))
        self.assertEqual(s["marker_symbol_outline_color"], "#0A1116")
        self.assertEqual((s["marker_color"], s["marker_ring_color"]), ("#666D8E", "#0A1116"))

    def test_every_colour_is_the_contract_form(self):
        import re
        for trip, route in (("T-N-1", "BRCA-5200"), ("T-S-1", "CABR-5200"),
                            ("T-G-1", "BRBR-5208"), ("T-G-2", "BRBR-5208")):
            r = self.run_one(obs(trip=trip, route=route))
            for k, v in r.items():
                if k.endswith("_color") and v != "none":
                    self.assertRegex(v, r"^#[0-9A-F]{6}$", (trip, k))

    def test_all_six_lines(self):
        want = {"27855A": "T1", "6CC6E9": "T2", "9B60A6": "T3", "4778B2": "T4",
                "FFC425": "T5", "D53E45": "T6"}
        self.assertEqual({k: v[0] for k, v in qr.BADGE.items() if v[0]}, want)
        self.assertEqual(qr.BADGE["666D8E"], (None, "#666D8E"))
        # Measured from Translink's badges (world note section 8).
        self.assertEqual([v[1] for v in qr.BADGE.values()],
                         ["#2E9C69", "#6DC7E9", "#A769AB", "#4E85C5", "#FFC628", "#EF474F",
                          "#666D8E"])

    def test_unplanned_takes_its_routes_direction_and_shape(self):
        r = self.run_one(obs(trip="UNPLANNED-9", route="CABR-5200", lat=-27.45, lon=153.0),
                         course_deg=10.0, icon_rotation_deg=10.0, icon_rotation_basis="course")
        self.assertEqual(r["marker_color"], "#2E9C69")          # southbound look
        self.assertAlmostEqual(r["course_deg"], 180.0, delta=1)  # along S2, southward

    def test_unknown_direction_is_drawn_as_published_and_keeps_fleets_course(self):
        r = self.run_one(obs(trip="UNPLANNED-9", route="BRBR-5208"),
                         course_deg=33.0, icon_rotation_deg=33.0, icon_rotation_basis="course")
        self.assertEqual(r["marker_color"], "#0A1116")
        self.assertEqual((r["course_deg"], r["icon_rotation_deg"]), (33.0, 33.0))

    def test_unknown_route_gets_no_look_and_keeps_the_run_number(self):
        r = self.run_one(obs(trip="UNPLANNED-9", route="BNBN-5167"))
        self.assertEqual(r["marker_label"], "1E15")
        self.assertFalse([k for k in r if k.startswith("marker_") and k != "marker_label"])
        self.assertEqual(r["late_threshold_min"], 4)

    def test_lateness(self):
        self.assertEqual(self.run_one(obs())["late_threshold_min"], 4)
        o = obs(route="BDVL-5200", trip="T-Q")
        self.assertEqual(self.run_one(o)["late_threshold_min"], 6)
        self.assertNotIn("very_late_threshold_min", self.run_one(o))
        r = self.run_one(obs(in_service=False, trip=None))
        self.assertNotIn("late_threshold_min", r)

    def test_arrow_along_the_shape_moving_and_at_rest(self):
        moving = self.run_one(obs(), course_deg=95.0, icon_rotation_deg=95.0,
                              icon_rotation_basis="course")
        self.assertAlmostEqual(moving["course_deg"], 0.0, delta=1)    # S1 runs north
        self.assertEqual(moving["icon_rotation_deg"], moving["course_deg"])
        self.assertEqual(moving["icon_rotation_basis"], "course")
        rest = self.run_one(obs(trip="T-S-1", route="CABR-5200"))
        self.assertNotIn("course_deg", rest)
        self.assertAlmostEqual(rest["icon_rotation_deg"], 180.0, delta=1)
        self.assertEqual(rest["icon_rotation_basis"], "held")

    def test_arrow_near_a_line_end_stays_inside_it(self):
        r = self.run_one(obs(lat=-27.4000, lon=153.0))
        self.assertAlmostEqual(r["icon_rotation_deg"], 0.0, delta=2)

    def test_no_arrow_from_a_shape_more_than_1_km_away(self):
        r = self.run_one(obs(lon=153.02), course_deg=95.0, icon_rotation_deg=95.0,
                         icon_rotation_basis="course")
        self.assertEqual((r["course_deg"], r["icon_rotation_deg"]), (95.0, 95.0))
        near = self.run_one(obs(lon=153.009), course_deg=95.0)
        self.assertAlmostEqual(near["course_deg"], 0.0, delta=1)

    def test_position_jump_is_dropped(self):
        self.assertNotIn("position_jump", self.run_one(obs(), position_jump=True))

    def test_no_timetable_changes_only_the_jump_and_lateness(self):
        o = obs()
        r = rec_for(o, position_jump=True, course_deg=5.0)
        qr.decorate(r, o, None)
        self.assertEqual(r, dict(rec_for(o, course_deg=5.0), late_threshold_min=4))

    def test_new_keys_reach_the_map(self):
        a = attributes.to_attributes(self.run_one(obs(trip="T-G-2", route="BRBR-5208")),
                                     "qr_citytrain")
        for k in ("marker_symbol", "marker_symbol_outline_color", "late_threshold_min"):
            self.assertIn(k, a)


class OffRail(unittest.TestCase):

    def test_the_operators_own_distance(self):
        line = [[[-27.50, 153.0], [-27.40, 153.0]]]
        c = rail.RailCheck(None, qr.OFF_RAIL_M)
        c.set_shapes({"fetched_at": 1, "rail_shapes": line})
        self.assertTrue(c(-27.45, 153.0065))     # ~640 m: Rosewood platform 1 is 637 m off
        self.assertFalse(c(-27.45, 153.011))     # ~1.08 km
        us = rail.RailCheck(None)
        us.set_shapes({"fetched_at": 1, "rail_shapes": line})
        self.assertFalse(us(-27.45, 153.0065))   # 300 m elsewhere


class Wiring(unittest.TestCase):

    def test_decorate_all_hands_each_record_its_observation(self):
        o1, o2 = obs(label="A"), obs(label="B", trip="T-S-1", route="CABR-5200")
        result = {"vehicles": {o1.vehicle_id: rec_for(o1), o2.vehicle_id: rec_for(o2)}}
        poll.decorate_all(result, [o1, o2], timetable(), qr.decorate)
        v = result["vehicles"]
        self.assertEqual(v[o1.vehicle_id]["marker_color"], "#0A1116")
        self.assertEqual(v[o2.vehicle_id]["marker_color"], "#2E9C69")
        poll.decorate_all(result, [o1], None, None)          # no decorate: nothing


if __name__ == "__main__":
    unittest.main()

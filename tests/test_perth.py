"""Transperth's trains, Perth (SSOT 20): the cut, the runs drawn from the timetable along their shapes as no-fix
estimates (D3d), the label, the hover, the look by line and direction, and the registry. A synthetic zip in the PTA's
shape (stops.txt's spaced header, parent stations, Transwa and a bus in the same zip) on lines along 115.86 E:
High Wycombe (-31.90) - Perth Stn (-31.95) - Claremont (-31.98) for the Airport Line through Perth; Perth Underground
(-31.95) - Murdoch (-32.07) - Mandurah (-32.52) for the Mandurah Line; Byford (-32.20) - Perth Stn for Armadale."""

import datetime as dt
import io
import json
import pathlib
import unittest
import zipfile

from _load import load

from saw_livetrack import transperth as lib
from saw_livetrack.gtfs import Fleet, distill

pe = load("operators.perth")
base = load("operators.base")
ops = load("operators")
runs_m = load("perth_runs")
rail = load("rail")
poll = load("poll")
attributes = load("attributes")

DAY = dt.date(2026, 11, 16)   # a Monday; Perth is UTC+8 all year
LON = 115.86


def ts(h, m, s=0, day=DAY):
    return dt.datetime(day.year, day.month, day.day, h, m, s, tzinfo=lib.TZ).timestamp()


def _csv(rows, sep=","):
    return "\n".join(sep.join(str(c) for c in r) for r in rows) + "\n"


def make_zip():
    # Platforms under parent stations, the header with a space after each comma (MEASURED 2026-11-13).
    stops = [["location_type", "parent_station", "stop_id", "stop_name", "stop_lat", "stop_lon"],
             [1, "", "56", "Perth Stn", -31.95, LON], [0, "56", "99009", "Perth Stn Platform 9", -31.95, LON],
             [0, "56", "99004", "Perth Stn Platform 4", -31.95, LON],
             [1, "", "64", "Perth Underground Stn", -31.951, LON],
             [0, "64", "99602", "Perth Underground Stn Platform 2", -31.951, LON],
             [0, "64", "99601", "Perth Underground Stn Platform 1", -31.951, LON],
             [0, "", "99662", "Murdoch Stn Platform 2", -32.07, LON],
             [0, "", "99732", "Mandurah Stn Platform 2", -32.52, LON],
             [0, "", "99731", "Mandurah Stn Platform 1", -32.52, LON],
             [0, "", "99562", "High Wycombe Stn Platform 2", -31.90, LON],
             [0, "", "99282", "Claremont Stn Platform 2", -31.98, LON],
             [0, "", "99362", "Byford Stn Platform 2", -32.20, LON],
             [0, "", "95022", "East Perth", -31.95, 115.87], [0, "", "95499", "Bunbury", -33.36, 115.66],
             [0, "", "10001", "Bus A", -31.7, 115.7], [0, "", "10002", "Bus B", -31.71, 115.71]]
    stops_txt = ", ".join(stops[0]) + "\n" + _csv(stops[1:])
    south = [(round(-31.90 - 0.01 * i, 2), LON) for i in range(63)]          # -31.90 .. -32.52
    shapes = [["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]]
    for name, pts in (("MS", [p for p in south if p[0] <= -31.95]), ("MN", [p for p in south if p[0] <= -31.95][::-1]),
                      ("AP", [p for p in south if p[0] >= -31.98]), ("RN", [p for p in south
                                                                         if -32.20 <= p[0] <= -31.95][::-1]),
                      ("TW", [(-31.95, 115.87), (-33.36, 115.66)]), ("BS", [(-31.7, 115.7), (-31.71, 115.71)])):
        shapes += [[name, a, b, i + 1] for i, (a, b) in enumerate(pts)]
    trips = [["route_id", "service_id", "trip_id", "direction_id", "trip_headsign", "shape_id"],
             ["WES-RAI-1865", "WD", "M1", 1, "Mandurah Stn", "MS"], ["WES-RAI-1865", "WD", "M2", 0,
                                                                      "Perth Underground Stn", "MN"],
             ["WES-RAI-4106", "WD", "A1", 0, "Claremont Stn", "AP"], ["WES-RAI-1830", "WD", "R1", 0, "Perth Stn", "RN"],
             ["TRA-TRA-137", "WD", "X1", 1, "Bunbury", "TW"], ["SWA-JOO-1", "WD", "B1", 0, "Bus B", "BS"]]
    st = [["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "pickup_type", "drop_off_type"]]

    def run(tid, calls):
        for i, (s, a, d) in enumerate(calls):
            st.append([tid, a, d, s, i + 1, 1 if i == len(calls) - 1 else 0, 1 if i == 0 else 0])
    run("M1", [("99602", "08:00:00", "08:00:00"), ("99662", "08:10:00", "08:11:00"), ("99732", "08:30:00", "08:30:00")])
    run("M2", [("99731", "09:00:00", "09:00:00"), ("99662", "09:19:00", "09:20:00"), ("99601", "09:30:00", "09:30:00")])
    run("A1", [("99562", "10:00:00", "10:00:00"), ("99009", "10:10:00", "10:12:00"), ("99282", "10:20:00", "10:20:00")])
    run("R1", [("99362", "11:00:00", "11:00:00"), ("99004", "11:30:00", "11:30:00")])
    run("X1", [("95022", "06:00:00", "06:00:00"), ("95499", "08:30:00", "08:30:00")])
    run("B1", [("10001", "07:00:00", "07:00:00"), ("10002", "07:20:00", "07:20:00")])
    files = {
        "agency.txt": _csv([["agency_id", "agency_name", "agency_url", "agency_timezone"],
                            ["WES-RAI", "Transperth", "http://www.transperth.wa.gov.au", "Australia/Perth"],
                            ["TRA-TRA", "Transwa", "http://www.transwa.wa.gov.au", "Australia/Perth"],
                            ["SWA-JOO", "Transperth", "http://www.transperth.wa.gov.au", "Australia/Perth"]]),
        "routes.txt": _csv([["route_id", "agency_id", "route_short_name", "route_long_name", "route_type", "route_color",
                             "route_text_color"],
                            ["WES-RAI-1865", "WES-RAI", "", "Mandurah Line", 2, "CB6015", "FFFFFF"],
                            ["WES-RAI-4106", "WES-RAI", "", "Airport Line", 2, "4FC7B5", "FFFFFF"],
                            ["WES-RAI-1830", "WES-RAI", "", "Armadale Line", 2, "F2A900", "000000"],
                            ["TRA-TRA-137", "TRA-TRA", "", "Australind", 2, "CF4520", "FFFFFF"],
                            ["SWA-JOO-1", "SWA-JOO", "460", "", 3, "", ""]]),
        "calendar.txt": _csv([["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                               "sunday", "start_date", "end_date"], ["WD", 1, 1, 1, 1, 1, 1, 1, "20200101", "20991231"]]),
        "calendar_dates.txt": _csv([["service_id", "date", "exception_type"]]),
        "stops.txt": stops_txt, "shapes.txt": _csv(shapes), "trips.txt": _csv(trips), "stop_times.txt": _csv(st),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def build(raw, day=DAY):
    """statics._distill for this operator (statics imports Home Assistant), with the table for `day`."""
    cut = pe.PERTH.static_rewrite(raw)
    d = distill(cut, stop_times=pe.PERTH.static_stop_times)
    d["rail_shapes"], index = rail.shapes_indexed(cut)
    d["trip_shapes"] = rail.trip_shapes(cut, index, None)    # statics.py keeps every trip's with a static_table
    d["table"] = lib.read_timetable(cut, lib.COMMUTER, day)
    d["fetched_at"] = 1.0
    return d


class CutTests(unittest.TestCase):

    def test_keeps_transperth_trains_only(self):
        z = zipfile.ZipFile(io.BytesIO(pe.cut(make_zip())))
        rows = lambda n: list(__import__("csv").DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8")))
        self.assertEqual(sorted(r["trip_id"] for r in rows("trips.txt")), ["A1", "M1", "M2", "R1"])
        self.assertEqual(sorted(r["route_id"] for r in rows("routes.txt")), ["WES-RAI-1830", "WES-RAI-1865",
                                                                             "WES-RAI-4106"])
        self.assertIn("stop_id", rows("stops.txt")[0])            # the spaced header stripped
        self.assertNotIn("95022", {r["stop_id"] for r in rows("stops.txt")})
        self.assertIn("56", {r["stop_id"] for r in rows("stops.txt")})   # the parent kept

    def test_static_table_is_today_in_perth(self):
        t = pe.PERTH.static_table(pe.cut(make_zip()))
        self.assertEqual(t["consumer"], lib.COMMUTER)
        self.assertEqual(sorted(t["trips"]), ["A1", "M1", "M2", "R1"])
        today = lib.local_day(__import__("time").time())
        self.assertIn(today.isoformat(), t["dates"]["WD"])
        self.assertEqual(t["stop_names"]["99009"], "Perth Stn")


class StaticsTests(unittest.TestCase):
    """statics.py for this operator, through test_timetable's stubs of aiohttp and Home Assistant."""

    @classmethod
    def setUpClass(cls):
        import test_timetable  # noqa: F401 - stubs aiohttp and homeassistant.core where they are not installed
        cls.statics = load("statics")

    def test_distill_keeps_the_table_and_every_trips_shape(self):
        d = self.statics._distill(make_zip(), pe.PERTH)
        self.assertEqual(sorted(d["table"]["trips"]), ["A1", "M1", "M2", "R1"])
        self.assertEqual(sorted(d["trip_shapes"]), ["A1", "M1", "M2", "R1"])
        self.assertNotIn("X1", d["trip_shapes"])
        self.assertEqual(d["table"]["stop_names"]["99009"], "Perth Stn")
        self.assertEqual(len(d["rail_shapes"]), 3)                # MS (MN is MS reversed), AP, RN


class LookTests(unittest.TestCase):

    def test_label_is_the_line_s_first_three_letters(self):
        for line, want in (("Mandurah Line", "MAN"), ("Thornlie-Cockburn Line", "THO"), ("Airport Line", "AIR"),
                           ("Stadium Special", "STA"), ("Yanchep Line", "YAN"), (" Mandurah Line", "MAN"),
                           ("", "")):
            self.assertEqual(pe.label(line), want, line)

    def test_colour_the_map_wins(self):
        self.assertEqual(pe.colour("Fremantle Line", "#002F6C"), "#0056B8")
        self.assertEqual(pe.colour("Stadium Special", "#009645"), "#009645")
        self.assertEqual(pe.colour("Somewhere Line", ""), "#808080")
        self.assertEqual(pe.colour("Somewhere Line", "009645"), "#808080")
        self.assertEqual(len(pe.COLOURS), 8)

    def test_show_drops_stn(self):
        self.assertEqual(pe.show("Perth Underground Stn"), "Perth Underground")
        self.assertEqual(pe.show("East Perth"), "East Perth")
        self.assertEqual(pe.show(" Murdoch Stn "), "Murdoch")
        self.assertEqual(pe.show("Murdoch Stn Platform 2"), "Murdoch")
        self.assertEqual(pe.show("Platform Road Stn"), "Platform Road")

    def test_hover(self):
        self.assertEqual(pe.hover("Mandurah Line", ["Perth Underground Stn", "Murdoch Stn", "Mandurah Stn"]),
                         "Mandurah Line · Perth Underground–Mandurah")
        self.assertEqual(pe.hover("Mandurah Line", []), "Mandurah Line")

    def test_toward_perth(self):
        ends = ["Mandurah Stn", "Murdoch Stn", "Perth Underground Stn"]
        self.assertTrue(pe.toward_hub(ends, 0, "running"))
        self.assertFalse(pe.toward_hub(ends[::-1], 1, "running"))
        self.assertTrue(pe.toward_hub(["Yanchep Stn", "Perth Underground Stn", "Elizabeth Quay Stn"], 1, "running"))
        through = ["High Wycombe Stn", "Perth Stn", "Claremont Stn"]
        self.assertTrue(pe.toward_hub(through, 0, "running"))
        self.assertTrue(pe.toward_hub(through, 1, "standing"))        # at Perth: still toward
        self.assertFalse(pe.toward_hub(through, 1, "running"))        # left Perth: leaving
        self.assertFalse(pe.toward_hub(["Perth Stadium Stn", "Mandurah Stn"], 0, "running"))
        self.assertFalse(pe.toward_hub([], 0, "running"))

    def test_the_looks(self):
        self.assertEqual(pe.look("#D25F15", False), {
            "marker_color": "#D25F15", "marker_ring_color": "#FFFFFF", "marker_ring_width": 3,
            "marker_label_color": "#FFFFFF", "marker_label_outline_color": "#D25F15", "marker_arrow_color": "#D25F15",
            "marker_arrow_outline_color": "#FFFFFF"})
        t = pe.look("#D25F15", True)
        self.assertEqual((t["marker_color"], t["marker_ring_color"], t["marker_label_color"],
                          t["marker_label_outline_color"]), ("#FFFFFF", "#D25F15", "#D25F15", "#FFFFFF"))
        self.assertEqual(pe.look("#F6A800", False, True)["marker_label_color"], "#000000")
        self.assertEqual(pe.look("#F6A800", True, True)["marker_label_color"], "#000000")


class RunTests(unittest.TestCase):

    def setUp(self):
        self.d = build(make_zip())
        self.r = runs_m.PerthRuns()

    def rows(self, now):
        return {x["trip_id"]: x for x in self.r.poll(self.d, now)}

    def test_no_timetable_draws_nothing(self):
        self.assertEqual(self.r.poll({}, ts(8, 5)), [])
        self.assertEqual(self.r.skipped, {"no_timetable": 1})

    def test_waiting_at_its_origin(self):
        x = self.rows(ts(7, 57))["M1"]
        self.assertEqual((x["state"], x["index"], x["lat"]), ("standing", 0, -31.951))
        self.assertEqual(x["key"], "M1-16")
        self.assertIsNone(x["delay_s"])

    def test_running_along_the_shape_by_time(self):
        x = self.rows(ts(8, 5))["M1"]
        self.assertEqual(x["state"], "running")
        self.assertAlmostEqual(x["lat"], (-31.951 + -32.07) / 2, delta=0.002)
        self.assertAlmostEqual(x["course"], 180.0, delta=0.5)
        self.assertTrue(x["moving"])
        self.assertEqual(x["next"][0], "Murdoch Stn Platform 2")   # no parent: the platform's own name

    def test_gone_after_its_end(self):
        self.assertNotIn("M1", self.rows(ts(8, 40)))

    def test_the_transwa_train_and_the_bus_are_never_drawn(self):
        got = self.rows(ts(7, 10))
        self.assertNotIn("X1", got)
        self.assertNotIn("B1", got)


class OperatorTests(unittest.TestCase):

    def test_registry(self):
        op = ops.OPERATORS["perth"]
        self.assertIs(op, pe.PERTH)
        self.assertEqual((op.name, op.short, op.regions), ("Perth trains", "Perth", ("AU-WA",)))
        self.assertEqual(op.source, base.SOURCE_TRANSPERTH)
        self.assertEqual(op.transperth_consumer, "commuter")
        self.assertFalse(op.needs_key)
        self.assertEqual(op.attribution, lib.ATTRIBUTION)
        self.assertEqual(op.terms_url, lib.TERMS_URL)
        self.assertEqual(op.static_url, lib.STATIC_URL)
        self.assertIs(op.static_rewrite, pe.cut)
        self.assertIs(op.static_table, pe.table)
        self.assertIs(op.parse_stops, pe.perth_stops)
        self.assertIsNone(op.decorate)
        self.assertIsNone(op.styling)
        self.assertFalse(op.narn)
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertNotIn("Transperth", op.name + op.short)          # no PTA trademark with the data
        self.assertEqual(base.REGIONS["AU-WA"], "Australia — Western Australia")
        self.assertEqual([o.id for o in ops.operators_in("AU-WA")], ["perth"])
        for other in ops.OPERATORS.values():
            if other is not op:
                self.assertIsNone(other.transperth_consumer, other.id)
                self.assertNotEqual(other.source, base.SOURCE_TRANSPERTH, other.id)

    def test_manifest_asks_for_the_library_with_perth(self):
        m = json.loads((pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
                        / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("saw-livetrack[gtfs]>=0.2.40,<0.3", m["requirements"])

    def test_every_translation_names_the_region(self):
        root = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
        for p in [root / "strings.json", *sorted((root / "translations").glob("*.json"))]:
            self.assertIn('"au-wa"', p.read_text(encoding="utf-8"), p.name)


class EndToEndTests(unittest.TestCase):
    """As the coordinator runs one poll: PerthRuns.poll, parse, parse_stops, Fleet, apply_extras, publish."""

    def setUp(self):
        self.d = build(make_zip())
        self.r = runs_m.PerthRuns()
        self.fleet = Fleet(styling=pe.PERTH.styling)

    def one(self, now):
        op = pe.PERTH
        rows = self.r.poll(self.d, now)
        obs, _ = poll.fresh_only(op.parse(rows), now, op.max_fix_age_s)
        nxt, delays, extras = op.parse_stops(rows, self.d, now)
        result = self.fleet.update(obs, now, next_stops=nxt, static=self.d, trip_delays=delays)
        poll.apply_extras(result, extras)
        poll.decorate_all(result, obs, self.d, op.decorate)
        result["estimated"] = self.r.publish(result)
        return result, {k: attributes.to_attributes(v, op.id) for k, v in result["vehicles"].items()}

    def test_a_mandurah_train_leaving_perth(self):
        result, a = self.one(ts(8, 5))
        x = a["M1-16"]
        self.assertEqual(result["estimated"], 1)
        self.assertEqual(x["marker_label"], "MAN")
        self.assertEqual(x["line_name"], "Mandurah Line · Perth Underground–Mandurah")
        self.assertEqual(x["next_stop"], "Murdoch")
        self.assertEqual(x["position_source"], "estimated")
        self.assertNotIn("fix_latitude", x)
        self.assertNotIn("delay_min", x)
        self.assertNotIn("late_threshold_min", x)
        self.assertEqual((x["marker_color"], x["marker_ring_color"], x["marker_label_color"]),
                         ("#D25F15", "#FFFFFF", "#FFFFFF"))
        self.assertAlmostEqual(x["course_deg"], 180.0, delta=0.5)
        self.assertEqual(x["operator"], "perth")
        self.assertEqual(x["observed_at"], "2026-11-16T00:00:00+00:00")   # left Perth Underground 08:00 local

    def test_toward_perth_the_disc_is_white(self):
        _, a = self.one(ts(9, 25))
        x = a["M2-16"]
        self.assertEqual((x["marker_color"], x["marker_ring_color"], x["marker_label_color"]),
                         ("#FFFFFF", "#D25F15", "#D25F15"))
        self.assertEqual(x["next_stop"], "Perth Underground")

    def test_the_airport_line_flips_after_perth(self):
        _, a = self.one(ts(10, 11))
        self.assertEqual(a["A1-16"]["marker_color"], "#FFFFFF")      # standing at Perth: still toward
        self.assertEqual(a["A1-16"]["marker_label"], "AIR")
        _, a = self.one(ts(10, 15))
        self.assertEqual(a["A1-16"]["marker_color"], "#46C3B2")      # left Perth: leaving
        self.assertEqual(a["A1-16"]["next_stop"], "Claremont")

    def test_armadale_s_label_is_black(self):
        _, a = self.one(ts(11, 10))
        x = a["R1-16"]
        self.assertEqual((x["marker_color"], x["marker_ring_color"], x["marker_label_color"]),
                         ("#FFFFFF", "#F6A800", "#000000"))
        self.assertEqual(x["marker_label"], "ARM")

    def test_track_path_along_the_shape(self):
        self.one(ts(8, 3))
        _, a = self.one(ts(8, 6))
        self.assertIn("track_path", a["M1-16"])


if __name__ == "__main__":
    unittest.main()

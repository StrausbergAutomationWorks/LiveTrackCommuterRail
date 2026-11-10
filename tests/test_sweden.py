"""Sweden's commuter trains on Trafikverket (SSOT 14). No Home Assistant, no network."""

import gzip
import json
import os
import tempfile
import unittest

from _load import load

ops = load("operators")
base = load("operators.base")
se = load("operators.sweden")
lines = load("sweden_lines")
shapepath = load("shapepath")
rail = load("rail")

NOW = 1_762_750_000.0   # 2026-11-10 ~04:4x Stockholm


def call(sig, activity, adv, est=None, act=None, public=True, canceled=False):
    return {"id": f"{sig}{activity}{adv}", "sig": sig, "activity": activity, "advertised": adv,
            "estimated": est, "actual": act, "public": public, "canceled": canceled}


def run(number="2241", date="2026-11-10", calls=None, lat=59.33, lon=18.06, ts=NOW - 20, bearing=180.0):
    return {"key": f"{number}|{date}", "number": number, "date": date, "brand": "sl_pendeltag",
            "product": "SL Pendeltåg", "operator": "SLL",
            "position": {"lat": lat, "lon": lon, "ts": ts, "bearing": bearing, "speed": None},
            "calls": calls if calls is not None else []}


# Märsta -> Stockholm City -> Södertälje, the train between Odenplan and City.
SOUTH = [call("Mr", "Avgang", NOW - 1800, act=NOW - 1740),
         call("Sod", "Ankomst", NOW - 300, act=NOW - 240),
         call("Sod", "Avgang", NOW - 240, act=NOW - 180),
         call("Sci", "Ankomst", NOW + 60, est=NOW + 120),
         call("Sci", "Avgang", NOW + 120, est=NOW + 180),
         call("Söc", "Ankomst", NOW + 1800, est=NOW + 1860)]
STATIONS = {"Mr": {"name": "Märsta", "lat": 59.6280, "lon": 17.8600},
            "Sod": {"name": "Stockholm Odenplan", "lat": 59.344444, "lon": 18.045145},
            "Sci": {"name": "Stockholm City", "lat": 59.332372, "lon": 18.064852},
            "Söc": {"name": "Södertälje Centrum", "lat": 59.1920, "lon": 17.6270},
            "Cst": {"name": "Stockholm C", "lat": 59.329971, "lon": 18.057267},
            "Arns": {"name": "Arlanda S", "lat": 59.64682, "lon": 17.928329},
            "Arnn": {"name": "Arlanda N", "lat": 59.651522, "lon": 17.929839},
            "Hel": {"name": "Helenelund", "lat": 59.4090, "lon": 17.9620}}
ENDS = {"Mr": {"population": 30576}, "Söc": {"population": 78377}, "Sci": {"population": 1652895},
        "G": {"population": 674529}, "Kb": {"population": 674529}, "A": {"population": 27895}}


class RegistryTests(unittest.TestCase):

    def test_three_operators_with_the_ids_lee_confirmed(self):
        # ! Permanent: config entry unique_ids and entity names (Lee 2026-11-10 00:33 CST).
        self.assertEqual({o.id for o in se.SWEDEN}, {"sl_pendeltag", "vasttagen", "arlanda_express"})
        for op in se.SWEDEN:
            self.assertIs(ops.OPERATORS[op.id], op)

    def test_each_claims_its_brand_as_commuter_on_trafikverket(self):
        for op in se.SWEDEN:
            self.assertEqual(op.source, base.SOURCE_TRAFIKVERKET)
            self.assertEqual((op.trafikverket_consumer, op.trafikverket_brand), ("commuter", op.id))
            self.assertEqual(op.regions, ("SE",))

    def test_brands_are_the_library_s_ids_for_commuter_runs(self):
        from saw_livetrack import trafikverket as trv
        self.assertEqual(trv.BRANDS["SL Pendeltåg"], "sl_pendeltag")
        self.assertEqual(trv.BRANDS["Västtågen"], "vasttagen")
        self.assertEqual(trv.ARLANDA_EXPRESS, "arlanda_express")

    def test_keyed_but_the_key_is_never_a_url_parameter(self):
        from saw_livetrack import trafikverket as trv
        for op in se.SWEDEN:
            self.assertTrue(op.needs_key)
            self.assertEqual(op.positions_url, trv.URL)
            self.assertNotIn("?", op.positions_url)
            self.assertEqual(op.key_url, trv.KEY_URL)

    def test_credit_and_no_affiliation(self):
        for op in se.SWEDEN:
            self.assertTrue(op.attribution.startswith("Data: Trafikverket (trafikverket.se), CC0"))
            self.assertIn("OpenStreetMap", op.attribution)
            self.assertIn("not sponsored by, affiliated with, or operated by Trafikverket", op.attribution)

    def test_sweden_is_a_region(self):
        self.assertEqual(ops.regions_in_use()["SE"], "Sweden")
        self.assertEqual([o.id for o in ops.operators_in("SE")],
                         ["arlanda_express", "sl_pendeltag", "vasttagen"])

    def test_off_rail_on_its_own_lines_at_a_kilometre(self):
        for op in se.SWEDEN:
            self.assertFalse(op.narn)
            self.assertEqual(op.off_rail_m, 1000.0)


class LookTests(unittest.TestCase):

    def test_sl_pendeltag_pink_and_white(self):
        self.assertEqual(se.BRANDS["sl_pendeltag"][2:5], ("#F166A7", "#FFFFFF", "#FFFFFF"))
        away = se.look(*se.BRANDS["sl_pendeltag"][2:5], False)
        self.assertEqual((away["marker_color"], away["marker_ring_color"], away["marker_label_color"]),
                         ("#F166A7", "#FFFFFF", "#FFFFFF"))
        to = se.look(*se.BRANDS["sl_pendeltag"][2:5], True)
        self.assertEqual((to["marker_color"], to["marker_ring_color"], to["marker_label_color"]),
                         ("#FFFFFF", "#F166A7", "#F166A7"))

    def test_vasttagen_as_intercity_rail_s(self):
        self.assertEqual(se.BRANDS["vasttagen"][2:5], ("#00ACEA", "#00394D", "#00394D"))

    def test_arlanda_express_yellow_with_black(self):
        self.assertEqual(se.BRANDS["arlanda_express"][2:5], ("#FEF380", "#000000", "#000000"))
        to = se.look(*se.BRANDS["arlanda_express"][2:5], True)
        self.assertEqual((to["marker_color"], to["marker_label_color"]), ("#000000", "#FEF380"))

    def test_every_colour_is_six_hex_digits_and_the_ring_a_number(self):
        for b in se.BRANDS.values():
            for toward in (False, True):
                k = se.look(*b[2:5], toward)
                for key, v in k.items():
                    if key == "marker_ring_width":
                        self.assertIs(type(v), int)
                    elif key != "marker_label_outline_color":
                        self.assertRegex(v, r"^#[0-9A-F]{6}$", key)

    def test_lateness_sl_3_and_6_the_others_6_and_12(self):
        want = {"sl_pendeltag": (3, 6), "vasttagen": (6, 12), "arlanda_express": (6, 12)}
        for op_id, (late, very) in want.items():
            rec = {}
            se.decorate_for(op_id)(rec, None, None)
            self.assertEqual((rec["late_threshold_min"], rec["very_late_threshold_min"]), (late, very), op_id)


class RunTests(unittest.TestCase):

    def test_identity_is_number_and_day(self):
        self.assertEqual(lines.identity("2241", "2026-11-10"), "2241-10")
        self.assertEqual(lines.identity("7720", "2026-11-09"), "7720-9")
        self.assertEqual(lines.identity("2241", None), "2241")

    def test_parse_every_run_in_service_labelled_by_its_number(self):
        obs = se.parse([run(calls=SOUTH)])
        self.assertEqual(len(obs), 1)
        o = obs[0]
        self.assertEqual((o.vehicle_id, o.trip_id, o.train, o.in_service), ("2241-10", "2241-10", "2241", True))
        self.assertEqual((o.lat, o.lon, o.reported_course), (59.33, 18.06, 180.0))
        self.assertEqual(int(o.observed_at.timestamp()), int(NOW - 20))

    def test_filter_keeps_a_running_train(self):
        f = lines.RunFilter()
        self.assertEqual(len(f.keep([run(calls=SOUTH)], NOW)), 1)

    def test_filter_skips_no_calls_and_all_cancelled(self):
        f = lines.RunFilter()
        gone = [call(c["sig"], c["activity"], c["advertised"], canceled=True) for c in SOUTH]
        self.assertEqual(f.keep([run(calls=[]), run(number="2", calls=gone)], NOW), [])
        self.assertEqual(f.skipped, {"no_calls": 1, "canceled": 1})

    def test_filter_skips_a_stale_first_sight_but_not_a_train_already_drawn(self):
        f = lines.RunFilter()
        self.assertEqual(f.keep([run(calls=SOUTH, ts=NOW - 400)], NOW), [])
        self.assertEqual(f.skipped, {"stale_first_sight": 1})
        f.keep([run(calls=SOUTH, ts=NOW - 10)], NOW - 100)
        self.assertEqual(len(f.keep([run(calls=SOUTH, ts=NOW - 400)], NOW)), 1)

    def test_filter_skips_a_finished_run_with_an_old_fix(self):
        done = [call("Mr", "Avgang", NOW - 3600, act=NOW - 3600), call("Söc", "Ankomst", NOW - 1200, act=NOW - 1100)]
        f = lines.RunFilter()
        f.keep([run(calls=done, ts=NOW - 1200)], NOW - 1150)
        self.assertEqual(f.keep([run(calls=done, ts=NOW - 1200)], NOW), [])
        self.assertEqual(f.skipped, {"finished": 1})


class NextStopTests(unittest.TestCase):

    def test_next_stop_after_the_last_actual_with_its_estimate(self):
        delay, nxt, eta = se.delay_and_next(SOUTH, NOW)
        self.assertEqual((nxt["sig"], eta, delay), ("Sci", NOW + 120, 60))

    def test_the_delay_is_the_next_stop_s_estimate_over_the_last_actual(self):
        calls = [call("Mr", "Avgang", NOW - 600, act=NOW - 540),          # 60 s late leaving
                 call("Sci", "Ankomst", NOW + 300, est=NOW + 540)]         # 240 s late expected
        self.assertEqual(se.delay_and_next(calls, NOW)[0], 240)

    def test_an_arrival_row_at_the_origin_is_never_the_next_stop(self):
        calls = [call("Söc", "Ankomst", NOW + 60), call("Söc", "Avgang", NOW + 120),
                 call("Sst", "Ankomst", NOW + 1500)]
        self.assertEqual(se.delay_and_next(calls, NOW)[1]["sig"], "Sst")

    def test_never_the_origin_nor_a_passed_or_cancelled_stop(self):
        calls = [call("Mr", "Avgang", NOW - 600),
                 call("Sod", "Ankomst", NOW - 120),           # passed: no actual, time gone
                 call("Sci", "Ankomst", NOW + 60, canceled=True),
                 call("Söc", "Ankomst", NOW + 900)]
        delay, nxt, eta = se.delay_and_next(calls, NOW)
        self.assertEqual(nxt["sig"], "Söc")
        self.assertEqual((delay, eta), (None, NOW + 900))

    def test_an_unadvertised_row_is_not_a_stop_on_an_advertised_trip(self):
        calls = [call("Mr", "Avgang", NOW - 600, act=NOW - 600),
                 call("Hel", "Ankomst", NOW + 60, public=False),
                 call("Sci", "Ankomst", NOW + 600)]
        self.assertEqual(se.delay_and_next(calls, NOW)[1]["sig"], "Sci")

    def test_arlanda_express_advertises_nothing_and_stops_at_its_own_stations(self):
        calls = [call("Cst", "Avgang", NOW - 600, act=NOW - 540, public=False),
                 call("Hel", "Ankomst", NOW - 60, public=False),
                 call("Arns", "Ankomst", NOW + 300, public=False),
                 call("Arnn", "Ankomst", NOW + 480, public=False)]
        self.assertIsNone(se.delay_and_next(calls, NOW)[1])
        delay, nxt, eta = se.delay_and_next(calls, NOW, se.ARLANDA_STOPS)
        self.assertEqual((nxt["sig"], delay, eta), ("Arns", 60, NOW + 360))
        self.assertEqual(lines.stop_signatures(calls, se.ARLANDA_STOPS), ["Cst", "Arns", "Arnn"])


class HubTests(unittest.TestCase):

    def test_stockholm_city_is_the_pendeltag_s_hub(self):
        self.assertEqual(se.hub_index(["Mr", "Sod", "Sci", "Söc"], ENDS), 2)

    def test_the_last_call_at_a_hub_is_the_hub(self):
        self.assertEqual(se.hub_index(["Sci", "Sod", "Sci", "Söc"], ENDS), 2)

    def test_stockholm_c_too(self):
        self.assertEqual(se.hub_index(["Cst", "Arns", "Arnn"], ENDS), 0)

    def test_else_the_larger_end_city(self):
        self.assertEqual(se.hub_index(["A", "G"], ENDS), 1)
        self.assertEqual(se.hub_index(["G", "A"], ENDS), 0)

    def test_both_ends_in_one_place_is_no_hub(self):
        self.assertIsNone(se.hub_index(["Kb", "G"], ENDS))
        self.assertIsNone(se.hub_index(["X", "Y"], ENDS))
        self.assertIsNone(se.hub_index([], ENDS))


class StopsTests(unittest.TestCase):

    def static(self):
        return {"stops": {s: v["name"] for s, v in STATIONS.items()}, "extras": {"ends": ENDS}}

    def test_toward_the_hub_until_city_then_away(self):
        stops = se.stops_for("sl_pendeltag")
        nxt, delays, extras = stops([run(calls=SOUTH)], self.static(), NOW)
        k = extras["2241-10"]
        self.assertEqual(k["marker_color"], "#FFFFFF")           # toward City: swapped
        self.assertEqual(nxt["2241-10"], ("Stockholm City", NOW + 120))
        self.assertEqual(delays["2241-10"], 60)
        self.assertEqual(k["line_name"], "SL Pendeltåg 2241 · Märsta–Södertälje Centrum")
        past = [dict(c, actual=c["advertised"] + 60) if c["sig"] in ("Sci",) else c for c in SOUTH]
        _, _, extras = stops([run(calls=past)], self.static(), NOW + 200)
        self.assertEqual(extras["2241-10"]["marker_color"], "#F166A7")

    def test_no_name_no_next_stop(self):
        nxt, delays, extras = se.stops_for("sl_pendeltag")([run(calls=SOUTH)], {"stops": {}}, NOW)
        self.assertEqual(nxt, {})
        self.assertNotIn("line_name", extras["2241-10"])
        self.assertEqual(delays["2241-10"], 60)


def _shipped(tmp, pairs):
    path = os.path.join(tmp, "lines.json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump({"v": 1, "meta": {}, "lines": pairs}, fh)
    return path


def _enc(pts):
    out, pa, po = [], 0, 0
    for la, lo in pts:
        a, b = round(la * 1e5), round(lo * 1e5)
        out += [a - pa, b - po]
        pa, po = a, b
    return out


class GeometryTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Odenplan -> City by a curve (stored from the lower signature, "Sci", to the higher, "Sod").
        curve = [(59.332372, 18.064852), (59.3400, 18.0620), (59.344444, 18.045145)]
        self.path = _shipped(self.tmp, {"Sci|Sod": [1500.0, _enc(curve)]})

    def geo(self, fallback=()):
        return lines.SwedenGeometry(fallback, lines_path=self.path, ends_path=os.path.join(self.tmp, "none.json"))

    def test_a_trip_s_line_is_its_legs_shipped_reversed_or_straight(self):
        g = self.geo()
        d = g.update([run(calls=SOUTH)], STATIONS, 1)
        self.assertEqual(len(d["rail_shapes"]), 1)
        pts = d["rail_shapes"][0]
        self.assertEqual(pts[0], [59.628, 17.86])                     # Märsta, straight to Odenplan
        self.assertIn([59.34, 18.062], pts)                          # the shipped curve, run Sod -> Sci
        self.assertLess(pts.index([59.34444, 18.04515]), pts.index([59.34, 18.062]))
        self.assertEqual(pts[-1], [59.192, 17.627])
        self.assertEqual(d["trip_shapes"], {"2241-10": [0, 0]})
        self.assertEqual(d["stops"]["Sci"], "Stockholm City")

    def test_a_leg_that_stops_short_of_its_station_runs_on_to_it(self):
        # The router snapped Göteborg C to track 500 m away (2026-11-10): the line must still reach the station.
        coords = {"A": (57.7089, 11.9739), "B": (57.7300, 12.0100)}
        short = [(57.7103, 11.9819), (57.7200, 11.9950), (57.7298, 12.0098)]   # starts ~500 m from A, ends at B
        pts = lines.assemble([["A", "B", "A|B"]], {"A|B": _enc(short)}, coords)
        self.assertEqual(pts[0], [57.7089, 11.9739])
        self.assertEqual(pts[1], [57.7103, 11.9819])
        self.assertEqual(pts[-1], [57.7298, 12.0098])                  # 25 m from B: no stub
        rev = lines.assemble([["B", "A", "A|B"]], {"A|B": _enc(short)}, coords)
        self.assertEqual((rev[0], rev[-1]), ([57.7298, 12.0098], [57.7089, 11.9739]))

    def test_a_pair_never_built_takes_the_chain_of_shipped_pairs(self):
        # Ulriksdal straight to Arlanda S (2026-11-10): the shipped pairs along the track join them.
        coords = {"A": (59.0, 18.0), "B": (59.1, 18.0), "C": (59.2, 18.0), "D": (59.2, 18.5)}
        shipped = {"A|B": _enc([coords["A"], coords["B"]]), "B|C": _enc([coords["B"], coords["C"]]),
                   "C|D": _enc([coords["C"], coords["D"]])}
        g = lines.pair_graph(shipped)
        self.assertEqual(lines.chain("A", "C", g, coords), ["A", "B", "C"])
        self.assertEqual(lines.chain("C", "A", g, coords), ["C", "B", "A"])
        self.assertEqual(lines.expand([["A", "C", None]], g, coords), [["A", "B", "A|B"], ["B", "C", "B|C"]])
        # A chain far longer than the straight line is no chain: A to D straight is ~33 km, the chain ~51 km.
        self.assertEqual(lines.chain("A", "D", g, coords), ["A", "B", "C", "D"])
        far = dict(coords, D=(59.0, 18.3))
        self.assertIsNone(lines.chain("A", "D", lines.pair_graph({**shipped, "C|D": _enc([far["C"], far["D"]])}), far))
        self.assertEqual(lines.expand([["A", "X", None]], g, coords), [["A", "X", None]])
        # A shipped leg is never expanded.
        self.assertEqual(lines.expand([["A", "B", "A|B"]], g, coords), [["A", "B", "A|B"]])

    def test_one_line_per_stop_pattern_and_the_version_moves_only_for_a_new_one(self):
        g = self.geo()
        d = g.update([run(calls=SOUTH)], STATIONS, 1)
        v1 = d["fetched_at"]
        d = g.update([run(calls=SOUTH), run(number="2243", calls=SOUTH)], STATIONS, 1)
        self.assertEqual((len(d["rail_shapes"]), d["fetched_at"]), (1, v1))
        self.assertEqual(d["trip_shapes"]["2243-10"], [0, 0])
        other = [c for c in SOUTH if c["sig"] != "Söc"]
        d = g.update([run(number="2245", calls=other)], STATIONS, 1)
        self.assertEqual(len(d["rail_shapes"]), 2)
        self.assertGreater(d["fetched_at"], v1)
        self.assertEqual(set(d["trip_shapes"]), {"2245-10"})

    def test_stop_positions_are_stops_only(self):
        calls = [call("Cst", "Avgang", NOW - 600, public=False), call("Hel", "Ankomst", NOW, public=False),
                 call("Arns", "Ankomst", NOW + 300, public=False), call("Arnn", "Ankomst", NOW + 480, public=False)]
        d = self.geo(se.ARLANDA_STOPS).update([run(number="7720", calls=calls)], STATIONS, 1)
        self.assertEqual(set(d["stop_pos"]), {"Cst", "Arns", "Arnn"})

    def test_the_way_between_two_fixes_follows_the_trip_s_line(self):
        d = self.geo().update([run(calls=SOUTH)], STATIONS, 1)
        p = shapepath.trip_path(d, "2241-10", (59.344444, 18.045145), (59.3360, 18.0640))
        self.assertIsNotNone(p)
        self.assertIn([59.34, 18.062], p)

    def test_the_off_rail_check_takes_a_new_pattern(self):
        g = self.geo()
        check = rail.RailCheck(None, 1000.0)
        check.set_shapes(g.update([run(calls=[c for c in SOUTH if c["sig"] in ("Sod", "Sci")])], STATIONS, 1))
        self.assertFalse(check(59.62, 17.87))                         # Märsta: no line yet
        check.set_shapes(g.update([run(calls=SOUTH)], STATIONS, 1))
        self.assertTrue(check(59.62, 17.87))


class ShippedFilesTests(unittest.TestCase):

    def test_the_lines_file_loads(self):
        got = lines.load_lines()
        self.assertGreater(len(got), 100)
        for k, enc in got.items():
            a, b = k.split("|")
            self.assertLess(a, b)
            self.assertGreaterEqual(len(enc), 4)

    def test_the_ends_file_holds_the_hubs_and_the_ends(self):
        ends = lines.load_ends()
        for s in ("Cst", "Sci", "Mr", "Söc", "U", "G", "Kb", "Arnn"):
            self.assertIn(s, ends)


class LibraryCopiesTests(unittest.TestCase):

    def test_services_on_is_the_library_s_day_by_day_rule(self):
        import inspect
        from saw_livetrack.gtfs import filter as lib
        mine = load("gtfs_filter")
        self.assertEqual(inspect.getsource(mine.services_on), inspect.getsource(lib.services_on))

    def test_a_removal_on_one_day_keeps_the_service_on_another(self):
        import io
        import zipfile
        from datetime import date
        mine = load("gtfs_filter")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("calendar.txt", "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,"
                                       "start_date,end_date\nS,1,1,1,1,1,1,1,20260101,20261231\n")
            z.writestr("calendar_dates.txt", "service_id,date,exception_type\nS,20261109,2\n")
        z = zipfile.ZipFile(io.BytesIO(buf.getvalue()))
        self.assertEqual(mine.services_on(z, [date(2026, 11, 9), date(2026, 11, 10)]), {"S"})
        self.assertEqual(mine.services_on(z, [date(2026, 11, 9)]), set())


if __name__ == "__main__":
    unittest.main()

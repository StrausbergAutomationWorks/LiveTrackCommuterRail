"""VR lähijunat (Finland, Digitraffic): records -> observations, stops, look, and the
generic poll steps it brings (unstall_stale, apply_extras). No Home Assistant.
SSOT 8.1."""

import unittest
from datetime import datetime, timedelta, timezone

from _load import load

vr = load("operators.vr_lahijunat")
ops = load("operators")
poll = load("poll")
attributes = load("attributes")
base = load("operators.base")

T0 = datetime(2026, 10, 15, 6, 0, tzinfo=timezone.utc)


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def row(code, kind, minutes, *, commercial=True, stopping=True, actual=False,
        diff=None, cancelled=False):
    r = {"stationShortCode": code, "type": kind, "scheduledTime": iso(T0 + timedelta(minutes=minutes)),
         "commercialStop": commercial, "trainStopping": stopping, "cancelled": cancelled}
    if actual:
        r["actualTime"] = iso(T0 + timedelta(minutes=minutes + (diff or 0)))
    if diff is not None:
        r["differenceInMinutes"] = diff
    return r


def record(number="9123", date="2026-10-15", ttype="HL", line="P", rows=None,
           lat=60.2, lon=24.9, fix=T0, cancelled=False):
    train = {"trainNumber": int(number), "departureDate": date, "trainType": ttype,
             "commuterLineID": line, "trainCategory": "Commuter", "cancelled": cancelled,
             "timeTableRows": rows if rows is not None else []}
    return {"key": (number, date), "number": number, "departure_date": date,
            "lat": lat, "lon": lon, "speed_kmh": 40, "observed_at": fix, "gps": True,
            "category": "Commuter", "train_type": ttype, "commuter_line": line,
            "operator": "vr", "cancelled": cancelled, "train": train, "consumer": "commuter"}


RUNNING = [row("HKI", "DEPARTURE", 0, actual=True, diff=1),
           row("PSL", "ARRIVAL", 5, actual=True, diff=2),
           row("PSL", "DEPARTURE", 6, actual=True, diff=2),
           row("ILA", "ARRIVAL", 8, commercial=False, stopping=False),
           row("LEN", "ARRIVAL", 25, diff=3)]
BEFORE = [row("HKI", "DEPARTURE", 10), row("LPV", "ARRIVAL", 22)]
FINISHED = [row("HKI", "DEPARTURE", -30, actual=True), row("LPV", "ARRIVAL", -18, actual=True)]
# Line V: "commercial" at its first and last rows only (68 of the 100 runs measured;
# all 100 are commercial at both ends, fi_hv_o_check.txt).
POSITIONING = [row("HKI", "DEPARTURE", -5, actual=True), row("PSL", "ARRIVAL", 0, commercial=False),
               row("KKN", "ARRIVAL", 20)]
POSITIONING_DONE = [row("HKI", "DEPARTURE", -40, actual=True),
                    row("KKN", "ARRIVAL", -10, actual=True)]
# Line V with real stops ahead (#10148, Riihimaki-Helsinki, 9 commercial stops).
V_STOPS = [row("RI", "DEPARTURE", -5, actual=True), row("HY", "ARRIVAL", 5),
           row("HKI", "ARRIVAL", 45)]

NAMES = {"stops": {"HKI": "Helsinki", "PSL": "Pasila", "LEN": "Lentoasema",
                   "LPV": "Leppävaara", "RI": "Riihimäki", "HY": "Hyvinkää",
                   "KKN": "Kirkkonummi"}}


class StateTests(unittest.TestCase):

    def test_running_and_before_departure_are_in_service(self):
        self.assertEqual(vr.state(record(rows=RUNNING)), "service")
        self.assertEqual(vr.state(record(rows=BEFORE)), "service")

    def test_finished_cancelled_and_trainless_are_dropped(self):
        self.assertIsNone(vr.state(record(rows=FINISHED)))
        self.assertIsNone(vr.state(record(rows=RUNNING, cancelled=True)))
        r = record(rows=RUNNING)
        r["train"] = None
        self.assertIsNone(vr.state(r))
        self.assertIsNone(vr.state(record(rows=[])))

    def test_a_cancelled_stop_is_not_ahead(self):
        rows = FINISHED[:1] + [row("LPV", "ARRIVAL", 5, cancelled=True)]
        self.assertIsNone(vr.state(record(rows=rows)))

    def test_a_cancelled_train_object_is_dropped(self):
        r = record(rows=RUNNING)
        r["train"]["cancelled"] = True
        self.assertIsNone(vr.state(r))

    def test_a_record_marked_cancelled_is_dropped(self):
        r = record(rows=RUNNING)
        r["cancelled"] = True          # the client's describe(), the train untouched
        self.assertFalse(r["train"]["cancelled"])
        self.assertIsNone(vr.state(r))

    def test_a_commercial_row_the_train_passes_is_not_ahead(self):
        rows = FINISHED[:1] + [row("LPV", "ARRIVAL", 5, stopping=False)]
        self.assertIsNone(vr.state(record(rows=rows)))

    def test_line_v_is_nis_unless_a_commercial_stop_lies_past_its_first_station(self):
        self.assertEqual(vr.state(record(ttype="HV", line="V", rows=POSITIONING)), "nis")
        self.assertEqual(vr.state(record(ttype="HV", line="V", rows=V_STOPS)), "service")
        # Before it leaves, its own origin does not count.
        before = [row("HKI", "DEPARTURE", 10), row("KKN", "ARRIVAL", 30)]
        self.assertEqual(vr.state(record(ttype="HV", line="V", rows=before)), "nis")

    def test_a_stop_made_without_an_actual_is_behind_a_later_actual(self):
        # 1502-16, 2026-10-16: Santala made, no actual; Lappohja after it has one.
        rows = [row("HNK", "DEPARTURE", -30, actual=True), row("STA", "ARRIVAL", -20),
                row("LPO", "ARRIVAL", -10, actual=True, diff=1)]
        self.assertIsNone(vr.state(record(rows=rows)))
        rows.append(row("SGY", "ARRIVAL", 5, diff=2))
        self.assertEqual(vr.state(record(rows=rows)), "service")
        code, eta, delay = vr.next_commercial(record(rows=rows)["train"])
        self.assertEqual((code, delay), ("SGY", 2))
        self.assertEqual(eta, T0 + timedelta(minutes=5))

    def test_next_commercial_falls_back_to_the_last_actuals_delay_and_the_estimate(self):
        rows = [row("HKI", "DEPARTURE", 0, actual=True, diff=3),
                dict(row("PSL", "ARRIVAL", 5), liveEstimateTime=iso(T0 + timedelta(minutes=8)))]
        code, eta, delay = vr.next_commercial(record(rows=rows)["train"])
        self.assertEqual((code, delay, eta), ("PSL", 3, T0 + timedelta(minutes=8)))
        rows[1] = dict(rows[1], differenceInMinutes=True)     # a bool is not a delay
        self.assertEqual(vr.next_commercial(record(rows=rows)["train"])[2], 3)
        self.assertIsNone(vr.next_commercial(record(rows=FINISHED)["train"]))
        self.assertIsNone(vr.next_commercial(None))
        # Before departure: the origin is next, with no delay known.
        self.assertEqual(vr.next_commercial(record(rows=BEFORE)["train"])[::2], ("HKI", None))

    def test_next_commercial_skips_a_stop_that_carries_no_one(self):
        # Backlog 289: the library's next_stop, asked for commercial stops only.
        rows = [row("HKI", "DEPARTURE", -10, actual=True), row("ILA", "ARRIVAL", 2, commercial=False),
                row("PSL", "ARRIVAL", 5)]
        self.assertEqual(vr.next_commercial(record(rows=rows)["train"])[0], "PSL")

    def test_line_v_stops_behind_its_last_actual_do_not_count(self):
        rows = [row("RI", "DEPARTURE", -30, actual=True), row("HY", "ARRIVAL", -20),
                row("JK", "ARRIVAL", -10, commercial=False, actual=True), row("HKI", "ARRIVAL", 20)]
        self.assertEqual(vr.state(record(ttype="HV", line="V", rows=rows)), "nis")

    def test_line_v_is_dropped_once_its_last_row_is_made(self):
        self.assertIsNone(vr.state(record(ttype="HV", line="V", rows=POSITIONING_DONE)))


class ParseTests(unittest.TestCase):

    def test_identity_is_number_and_day(self):
        self.assertEqual(vr.identity("9123", "2026-10-15"), "9123-15")
        self.assertEqual(vr.identity("9123", "2026-10-05"), "9123-5")
        self.assertEqual(vr.identity("9123", None), "9123")
        self.assertEqual(vr.identity("9123", "bad"), "9123")

    def test_in_service_observation(self):
        (o,) = vr.parse([record(rows=RUNNING, lat=60.1234567, lon=24.9876543)])
        self.assertEqual(o.vehicle_id, "9123-15")
        self.assertTrue(o.in_service)
        self.assertEqual((o.train, o.line, o.trip_id), ("9123", "P", "9123-15"))
        self.assertEqual((o.lat, o.lon), (60.123457, 24.987654))
        self.assertIsNone(o.reported_course)
        self.assertEqual(o.observed_at, T0)

    def test_nis_has_no_train_and_no_trip(self):
        (o,) = vr.parse([record(number="10045", ttype="HV", line="V", rows=POSITIONING)])
        self.assertFalse(o.in_service)
        self.assertIsNone(o.train)
        self.assertIsNone(o.trip_id)
        self.assertEqual(o.line, "V")

    def test_skips_no_number_no_position_zero_and_dropped(self):
        bad = [record(rows=RUNNING, lat=0, lon=0), record(rows=FINISHED),
               dict(record(rows=RUNNING), number=""), dict(record(rows=RUNNING), lat=None)]
        self.assertEqual(vr.parse(bad), [])
        self.assertEqual(vr.parse(None), [])


class StopsTests(unittest.TestCase):

    def test_next_commercial_stop_named_with_eta_and_minutes_delay(self):
        nxt, delays, extras = vr.stops([record(rows=RUNNING)], NAMES, 0.0)
        name, eta = nxt["9123-15"]
        self.assertEqual(name, "Lentoasema")
        self.assertEqual(eta, (T0 + timedelta(minutes=25)).timestamp())
        self.assertEqual(delays["9123-15"], 180)
        self.assertEqual(extras["9123-15"]["line_name"], "Helsinki - Lentoasema")
        self.assertEqual(extras["9123-15"]["marker_color"], "#8C4799")

    def test_a_station_without_a_name_is_never_shown_as_a_code(self):
        nxt, delays, extras = vr.stops([record(rows=RUNNING)], {"stops": {}}, 0.0)
        self.assertEqual(nxt, {})
        self.assertEqual(delays["9123-15"], 180)
        self.assertNotIn("line_name", extras["9123-15"])
        nxt, _, _ = vr.stops([record(rows=RUNNING)], None, 0.0)
        self.assertEqual(nxt, {})

    def test_nothing_for_trains_not_in_service(self):
        recs = [record(number="10045", ttype="HV", line="V", rows=POSITIONING),
                record(rows=FINISHED)]
        self.assertEqual(vr.stops(recs, NAMES, 0.0), ({}, {}, {}))

    def test_a_boolean_delay_is_not_a_delay(self):
        # Backlog 289 (2026-11-10): the library's rule, falling back to the last ACTUAL row that carries a number
        # (here an earlier one, 2 minutes); the integration's own copy fell back to the very last actual row only,
        # and gave none.
        rows = RUNNING[:-1] + [dict(row("LEN", "ARRIVAL", 25), differenceInMinutes=True)]
        rows[2] = dict(rows[2], differenceInMinutes=True)
        _, delays, _ = vr.stops([record(rows=rows)], NAMES, 0.0)
        self.assertEqual(delays["9123-15"], 120)
        # With no actual row carrying a number, none.
        rows = [dict(r, differenceInMinutes=True) if r.get("actualTime") else r for r in rows]
        _, delays, _ = vr.stops([record(rows=rows)], NAMES, 0.0)
        self.assertNotIn("9123-15", delays)


class PlaceTests(unittest.TestCase):

    def test_colour_follows_the_next_stop(self):
        # R northbound: purple to Jokela, green once Hyvinkaa is next.
        inside = [row("HKI", "DEPARTURE", -40, actual=True), row("JK", "ARRIVAL", 5)]
        outside = [row("JK", "DEPARTURE", -5, actual=True), row("HY", "ARRIVAL", 5)]
        _, _, ex = vr.stops([record(line="R", rows=inside)], NAMES, 0.0)
        self.assertEqual((ex["9123-15"]["marker_color"], ex["9123-15"]["marker_arrow_color"]),
                         ("#8C4799",) * 2)
        _, _, ex = vr.stops([record(line="R", rows=outside)], NAMES, 0.0)
        self.assertEqual(ex["9123-15"]["marker_color"], "#00B451")

    def test_at_the_origin_before_departure(self):
        _, _, ex = vr.stops([record(line="R", rows=[row("RI", "DEPARTURE", 5),
                                                    row("HKI", "ARRIVAL", 60)])], NAMES, 0.0)
        self.assertEqual(ex["9123-15"]["marker_color"], "#00B451")
        _, _, ex = vr.stops([record(rows=BEFORE)], NAMES, 0.0)
        self.assertEqual(ex["9123-15"]["marker_color"], "#8C4799")

    def test_area_colour_falls_back_to_the_last_station_made(self):
        rows = [row("HKI", "DEPARTURE", -40, actual=True), row("HY", "ARRIVAL", -5, actual=True)]
        self.assertEqual(vr.area_colour(record(rows=rows)["train"], None), "#00B451")
        self.assertEqual(vr.area_colour(record(rows=rows[:1])["train"], None), "#8C4799")
        self.assertIsNone(vr.area_colour(record(rows=[row("HKI", "DEPARTURE", 5)])["train"], None))
        self.assertIsNone(vr.area_colour(None, ""))
        self.assertEqual(vr.area_colour(None, "KE"), "#8C4799")
        self.assertEqual(vr.area_colour(None, "MLÄ"), "#00B451")

    def test_a_trailing_comma_in_a_code_is_ignored(self):
        # Digitraffic's metadata carries one code as "NLA," (35_Dependencies digitraffic SSOT 3).
        self.assertEqual(vr.area_colour(None, "KE,"), "#8C4799")


class DirectionTests(unittest.TestCase):
    """Lee 2026-10-16 00:43: away from Helsinki filled, toward it swapped."""

    def keys(self, number, rows, line="R"):
        _, _, ex = vr.stops([record(number=number, line=line, rows=rows)], NAMES, 0.0)
        k = ex[f"{number}-15"]
        return (k["marker_color"], k["marker_ring_color"], k["marker_label_color"],
                k["marker_arrow_color"])

    def test_odd_away_is_filled_even_toward_is_swapped(self):
        out = [row("HKI", "DEPARTURE", -5, actual=True), row("PSL", "ARRIVAL", 0)]
        self.assertEqual(self.keys("9635", out), ("#8C4799", "#FFFFFF", "#FFFFFF", "#8C4799"))
        back = [row("RI", "DEPARTURE", -5, actual=True), row("HY", "ARRIVAL", 5)]
        self.assertEqual(self.keys("9636", back), ("#FFFFFF", "#00B451", "#00B451", "#00B451"))

    def test_a_ring_swaps_at_the_airport(self):
        ring = [row("HKI", "DEPARTURE", -30, actual=True), row("PSL", "ARRIVAL", -25, actual=True),
                row("LEN", "ARRIVAL", -2), row("LEN", "DEPARTURE", -1), row("TKL", "ARRIVAL", 5),
                row("HKI", "ARRIVAL", 30)]
        # Even, but away until it has made the airport.
        self.assertEqual(self.keys("8628", ring, line="P")[:2], ("#8C4799", "#FFFFFF"))
        made = [dict(r) for r in ring]
        made[2]["actualTime"] = made[2]["scheduledTime"]
        # Odd, but toward Helsinki once it has.
        self.assertEqual(self.keys("8629", made, line="P")[:2], ("#FFFFFF", "#8C4799"))

    def test_a_loop_without_the_airport_goes_by_parity(self):
        loop = [row("HKI", "DEPARTURE", -5, actual=True), row("PSL", "ARRIVAL", 0),
                row("HKI", "ARRIVAL", 20)]
        self.assertEqual(self.keys("8630", loop, line="P")[0], "#FFFFFF")
        self.assertEqual(self.keys("8631", loop, line="P")[0], "#8C4799")

    def test_with_no_station_the_line_colour_still_swaps(self):
        blind = [row("", "DEPARTURE", 5), row("", "ARRIVAL", 20)]
        self.assertEqual(self.keys("9640", blind, line="G"), ("#FFFFFF", "#00B451", "#00B451", "#00B451"))
        self.assertEqual(vr.line_colour("r"), "#8C4799")
        self.assertIsNone(vr.line_colour("X"))
        self.assertIsNone(vr.line_colour(None))

    def test_inbound_reads_digits_only(self):
        self.assertFalse(vr.inbound(None, "9123"))
        self.assertTrue(vr.inbound(None, "9124"))
        self.assertFalse(vr.inbound(None, None))
        self.assertFalse(vr.inbound(None, "V12"))


class LookTests(unittest.TestCase):

    def obs(self, line, in_service=True, vid="9123-15"):
        return base.Obs(vid, 60.2, 24.9, None, in_service,
                        train="9123" if in_service else None, line=line)

    def test_by_line_hsl_lines_purple_vr_only_green(self):
        # The fallback, when no station is known (stops() sets the place).
        for letter in "ADEHIKLPRTUYZ":
            s = vr.styling(self.obs(letter))
            self.assertEqual((s["marker_color"], s["marker_arrow_color"]), ("#8C4799",) * 2, letter)
        for letter in "GMOV":
            s = vr.styling(self.obs(letter))
            self.assertEqual((s["marker_color"], s["marker_arrow_color"]), ("#00B451",) * 2, letter)
        self.assertEqual(vr.HSL_LINES & vr.VR_ONLY_LINES, frozenset())

    def test_hsl_stations_are_the_fifty_zoned_ones(self):
        self.assertEqual(len(vr.HSL_STATIONS), 50)
        for code in ("HKI", "PSL", "TKL", "KE", "JP", "JK", "HAA", "STI", "KKN", "LEN", "KÄP"):
            self.assertIn(code, vr.HSL_STATIONS)
        for code in ("HY", "RI", "LH", "MLÄ", "HNN", "TPE", "KV", "HNK", "KR"):
            self.assertNotIn(code, vr.HSL_STATIONS)

    def test_ring_label_and_arrow_outline(self):
        s = vr.styling(self.obs("P"))
        self.assertEqual(s["marker_ring_color"], "#FFFFFF")
        self.assertIs(type(s["marker_ring_width"]), int)
        self.assertEqual(s["marker_ring_width"], 2)
        self.assertEqual(s["marker_label_color"], "#FFFFFF")
        self.assertEqual(s["marker_label_outline_color"], "none")
        self.assertEqual(s["marker_arrow_outline_color"], "#FFFFFF")

    def test_unknown_letter_has_no_fill_and_nis_is_grey(self):
        s = vr.styling(self.obs("X"))
        self.assertNotIn("marker_color", s)
        self.assertNotIn("marker_arrow_color", s)
        s = vr.styling(self.obs("V", in_service=False))
        self.assertEqual((s["marker_color"], s["marker_arrow_color"]), ("#808080",) * 2)

    def test_lowercase_letter_is_read(self):
        self.assertEqual(vr.styling(self.obs("p"))["marker_color"], "#8C4799")

    def test_label_is_the_letter_and_lateness_four_and_eight(self):
        rec = {"marker_label": "9123"}
        vr.decorate(rec, self.obs("P"), None)
        self.assertEqual(rec["marker_label"], "P")
        self.assertEqual((rec["late_threshold_min"], rec["very_late_threshold_min"]), (4, 8))
        rec = {"marker_label": "10148"}
        vr.decorate(rec, self.obs("V"), None)
        self.assertEqual(rec["marker_label"], "V")
        rec = {"marker_label": "9123"}
        vr.decorate(rec, self.obs("X"), None)
        self.assertEqual(rec["marker_label"], "9123")

    def test_nis_label_is_the_number_without_the_day(self):
        rec = {"marker_label": "NIS 10045-15"}
        vr.decorate(rec, self.obs("V", in_service=False, vid="10045-15"), None)
        self.assertEqual(rec["marker_label"], "NIS 10045")
        self.assertNotIn("late_threshold_min", rec)

    def test_very_late_threshold_reaches_the_map(self):
        rec = {"vehicle_id": "x", "marker_label": "P", "in_service": True,
               "latitude": 0, "longitude": 0, "very_late_threshold_min": 8}
        self.assertEqual(attributes.to_attributes(rec, "vr_lahijunat")["very_late_threshold_min"], 8)


class OperatorTests(unittest.TestCase):

    def test_declared(self):
        op = vr.VR_LAHIJUNAT
        self.assertEqual(op.id, "vr_lahijunat")
        self.assertEqual(op.regions, ("FI",))
        self.assertEqual(op.source, base.SOURCE_DIGITRAFFIC)
        self.assertEqual(op.digitraffic_consumer, "commuter")
        self.assertFalse(op.needs_key)
        self.assertFalse(op.narn)
        self.assertEqual(op.static_route_types, ("109",))
        self.assertEqual(op.static_headers, {"Digitraffic-User": "StrausbergAutomationWorks/saw-livetrack"})
        self.assertEqual((op.max_fix_age_s, op.stand_max_fix_age_s), (600, 120))
        self.assertEqual(op.off_rail_m, 1000.0)
        self.assertIs(op.parse_stops, vr.stops)
        self.assertIs(op.styling, vr.styling)
        self.assertIs(op.decorate, vr.decorate)
        self.assertTrue(op.attribution.startswith("Data: Fintraffic / digitraffic.fi, CC BY 4.0"))
        # HSL_STATIONS is HSL's data (CC BY 4.0): credited where the operator is shown.
        self.assertIn("Fare zones: HSL, hsl.fi, CC BY 4.0", op.attribution)
        self.assertIn("Track geometry: Fintraffic / digitraffic.fi infra-api, CC BY 4.0, "
                      "modified", op.attribution)
        self.assertIs(ops.OPERATORS["vr_lahijunat"], op)

    def test_other_operators_keep_the_defaults(self):
        for op in ops.OPERATORS.values():
            if op.id == "vr_lahijunat" or op.source in (base.SOURCE_RENFE, base.SOURCE_ENTUR,
                                                        base.SOURCE_TRAFIKVERKET, base.SOURCE_IRISH_RAIL,
                                                        base.SOURCE_NS):
                continue   # Renfe's: tests/test_renfe.py; Norway's: tests/test_norway.py; Sweden's: test_sweden.py;
                #            Irish Rail's: test_irish_rail.py; NS's: test_ns.py
            self.assertEqual(op.source, base.SOURCE_GTFS_RT, op.id)
            self.assertIsNone(op.parse_stops, op.id)
            self.assertIsNone(op.static_headers, op.id)
            self.assertIsNone(op.stand_max_fix_age_s, op.id)

    def test_finland_region(self):
        self.assertEqual([o.id for o in ops.operators_in("FI")], ["vr_lahijunat"])
        self.assertEqual(ops.regions_in_use()["FI"], "Finland")


class PollStepTests(unittest.TestCase):

    def result(self):
        return {"vehicles": {
            "a": {"vehicle_id": "a", "in_service": True, "stalled": True},
            "b": {"vehicle_id": "b", "in_service": True, "stalled": True},
            "c": {"vehicle_id": "c", "in_service": False}}}

    def obs(self, vid, age_s):
        return base.Obs(vid, 0.0, 0.0, T0 - timedelta(seconds=age_s), True)

    def test_unstall_stale_drops_stalled_at_and_past_the_age(self):
        res = self.result()
        now = T0.timestamp()
        n = poll.unstall_stale(res, [self.obs("a", 120), self.obs("b", 119), self.obs("c", 999)],
                               now, 120)
        self.assertEqual(n, 1)
        self.assertNotIn("stalled", res["vehicles"]["a"])
        self.assertTrue(res["vehicles"]["b"]["stalled"])

    def test_unstall_stale_off_and_without_a_fix_time(self):
        res = self.result()
        self.assertEqual(poll.unstall_stale(res, [self.obs("a", 999)], T0.timestamp(), None), 0)
        self.assertTrue(res["vehicles"]["a"]["stalled"])
        nofix = base.Obs("a", 0.0, 0.0, None, True)
        self.assertEqual(poll.unstall_stale(res, [nofix], T0.timestamp(), 120), 0)

    def test_apply_extras_only_to_trains_in_service(self):
        res = self.result()
        poll.apply_extras(res, {"a": {"line_name": "X"}, "c": {"line_name": "Y"}})
        self.assertEqual(res["vehicles"]["a"]["line_name"], "X")
        self.assertNotIn("line_name", res["vehicles"]["c"])
        poll.apply_extras(res, None)


if __name__ == "__main__":
    unittest.main()

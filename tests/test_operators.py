"""Operator adapters and the registry. No Home Assistant."""

import unittest
from datetime import timezone

import feeds
from _load import load

ops = load("operators")
metra = load("operators.metra")
nictd = load("operators.nictd")


class MetraTests(unittest.TestCase):

    def setUp(self):
        fm = feeds.feed()
        feeds.vehicle(fm, "15", vid="8528", label="2159", route="MD-N",
                      trip="MD-N_MN2159_V2_C", bearing=346.0)
        feeds.vehicle(fm, "1", vid="8530", bearing=359.0)          # no trip block
        feeds.vehicle(fm, "2", vid="8531", position=False)         # no position
        feeds.vehicle(fm, "3", vid=None, lat=41.9, lon=-87.9)      # no vehicle id
        feeds.vehicle(fm, "4", vid="8599", route="SWS", trip="SWS_SW841_V3_C")  # no label
        feeds.vehicle(fm, "5", vid="8600", ts=None, route="RI", label="517")
        self.obs = {o.vehicle_id: o for o in metra.parse(fm)}

    def test_skips_vehicles_without_id_or_position(self):
        self.assertEqual(set(self.obs), {"8528", "8530", "8599", "8600"})

    def test_routed_vehicle_is_in_service_with_its_train_number(self):
        o = self.obs["8528"]
        self.assertTrue(o.in_service)
        self.assertEqual((o.train, o.line), ("2159", "MD-N"))
        self.assertEqual(o.reported_course, 346.0)
        self.assertEqual(o.observed_at.tzinfo, timezone.utc)
        self.assertEqual(int(o.observed_at.timestamp()), feeds.T0)

    def test_unrouted_vehicle_is_not_in_service_and_has_no_train(self):
        o = self.obs["8530"]
        self.assertFalse(o.in_service)
        self.assertIsNone(o.train)
        self.assertIsNone(o.line)

    def test_train_number_falls_back_to_the_trip_id(self):
        self.assertEqual(self.obs["8599"].train, "841")

    def test_train_number_from_both_trip_id_forms(self):
        # Metra's 2026 GTFS static change: the train number sits between the
        # first and second underscores. Today's form keeps its letters.
        for trip in ("BNSF_BN1200_V4_A", "BNSF_1200_8_2009_5682524"):
            fm = feeds.feed()
            feeds.vehicle(fm, "7", vid="8500", route="BNSF", trip=trip)
            o = metra.parse(fm)[0]
            self.assertEqual((o.train, o.trip_id), ("1200", trip), trip)

    def test_float32_noise_is_rounded_to_six_decimals(self):
        fm = feeds.feed()
        feeds.vehicle(fm, "9", vid="1357", lat=41.860512, lon=-87.618576)
        o = metra.parse(fm)[0]
        # float32 cannot hold 41.860512; unrounded it reads 41.86051177978...
        self.assertEqual((o.lat, o.lon), (41.860512, -87.618576))

    def test_no_timestamp_means_no_observed_at(self):
        self.assertIsNone(self.obs["8600"].observed_at)

    def test_key_and_terms_are_declared(self):
        self.assertTrue(metra.METRA.needs_key)
        self.assertEqual(metra.METRA.key_param, "api_token")
        self.assertIn("not sponsored by, affiliated with, or operated by Metra",
                      metra.METRA.attribution)


class MetraStylingTests(unittest.TestCase):
    """Lee, 2026-10-02: fill = Metra's line colour; halo and arrow fill
    #0054A4; arrow outlined white; SWS's halo white."""

    OFFICIAL = {"BNSF": "#29C233", "HC": "#550E0C", "MD-N": "#CC5500",
                "MD-W": "#F1AD0E", "ME": "#EB5C00", "NCS": "#9785BC",
                "RI": "#E02400", "SWS": "#0042A8", "UP-N": "#008000",
                "UP-NW": "#FFE600", "UP-W": "#FE8D81"}

    def obs(self, line, in_service=True):
        return metra.Obs("8528", 41.9, -87.9, None, in_service,
                         train="47" if in_service else None, line=line)

    def test_every_line_fills_with_its_published_colour(self):
        self.assertEqual(metra.LINE_COLOR, self.OFFICIAL)
        for line, colour in self.OFFICIAL.items():
            self.assertEqual(metra.styling(self.obs(line))["marker_color"], colour, line)

    def test_halo_and_arrow_are_metra_blue_with_a_white_arrow_outline(self):
        for line in self.OFFICIAL:
            s = metra.styling(self.obs(line))
            self.assertEqual(s["marker_arrow_color"], "#0054A4", line)
            self.assertEqual(s["marker_arrow_outline_color"], "#FFFFFF", line)
            want = "#FFFFFF" if line == "SWS" else "#0054A4"
            self.assertEqual(s["marker_ring_color"], want, line)

    def test_equipment_not_in_service_is_grey_with_halo_and_arrow(self):
        s = metra.styling(self.obs(None, in_service=False))
        self.assertEqual(s["marker_color"], "#808080")
        self.assertEqual(s["marker_ring_color"], "#0054A4")
        self.assertEqual(s["marker_arrow_color"], "#0054A4")
        self.assertEqual(s["marker_arrow_outline_color"], "#FFFFFF")

    def test_an_in_service_train_on_an_unknown_line_gets_no_fill(self):
        s = metra.styling(self.obs("XYZ"))
        self.assertNotIn("marker_color", s)
        self.assertEqual(s["marker_ring_color"], "#0054A4")

    def test_every_value_is_hash_and_six_hex_digits(self):
        import re
        for line in list(self.OFFICIAL) + [None]:
            for key, value in metra.styling(self.obs(line)).items():
                if key == "marker_ring_width":
                    continue
                self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$", (line, key))

    def test_halo_is_2_px_on_every_metra_marker_as_a_json_number(self):
        # Lee, 2026-10-02: thicker on Metra only. D4a 6b: a number 0.5-4,
        # never a bool (True is an int in Python and JSON true to the card).
        for line in list(self.OFFICIAL) + [None]:
            for in_service in (True, False):
                w = metra.styling(self.obs(line, in_service))["marker_ring_width"]
                self.assertIs(type(w), int, line)
                self.assertEqual(w, 2, line)
                self.assertTrue(0.5 <= w <= 4)

    def test_no_label_colour_is_set(self):
        s = metra.styling(self.obs("UP-W"))
        for key in ("marker_label_color", "marker_label_outline_color"):
            self.assertNotIn(key, s)

    def test_the_operator_uses_this_styling(self):
        self.assertIs(metra.METRA.styling, metra.styling)


class NictdTests(unittest.TestCase):

    def setUp(self):
        fm = feeds.feed()
        feeds.vehicle(fm, "vehicle_position_310", vid="310", label="515", trip="515", bearing=0.0)
        feeds.vehicle(fm, "vehicle_position_32", vid="32", label="NIS", trip="515", bearing=0.0)
        feeds.vehicle(fm, "vehicle_position_35", vid="35", label="NIS", trip="1601", bearing=0.0)
        feeds.vehicle(fm, "vehicle_position_77", vid=None, label="311", trip="311")
        feeds.vehicle(fm, "vehicle_position_90", vid="90")          # no trip, no label
        self.obs = {o.vehicle_id: o for o in nictd.parse(fm)}

    def test_lead_unit_is_the_train(self):
        o = self.obs["310"]
        self.assertTrue(o.in_service)
        self.assertEqual((o.train, o.line), ("515", "lakeshore"))

    def test_nis_units_are_not_in_service_but_keep_their_line_from_the_trip(self):
        self.assertFalse(self.obs["32"].in_service)
        self.assertIsNone(self.obs["32"].train)
        self.assertEqual(self.obs["35"].line, "monon")

    def test_bearing_is_never_used(self):
        self.assertTrue(all(o.reported_course is None for o in self.obs.values()))

    def test_vehicle_id_falls_back_to_the_entity_id(self):
        self.assertIn("vehicle_position_77", self.obs)
        self.assertEqual(self.obs["vehicle_position_77"].line, "monon")

    def test_unit_with_neither_trip_nor_label_is_skipped(self):
        self.assertNotIn("90", self.obs)

    def test_line_rule(self):
        cases = {"299": "lakeshore", "300": "monon", "399": "monon",
                 "400": "lakeshore", "999": "lakeshore", "1000": "monon",
                 "1601": "monon", "": None, "NIS": None, None: None}
        for trip, want in cases.items():
            self.assertEqual(nictd.line_of(trip), want, trip)

    def test_styling_per_line_and_none_without_a_line(self):
        o = self.obs["310"]
        s = nictd.styling(o)
        self.assertEqual(s["marker_color"], "#EF8322")
        self.assertEqual(s["marker_label_color"], "#7F281F")
        no_line = nictd.Obs("x", 0.0, 0.0, None, False)
        self.assertEqual(nictd.styling(no_line), {})

    def test_delays_take_the_soonest_stop_and_keep_zero(self):
        fm = feeds.feed()
        feeds.trip_update(fm, "515", [(5, 240), (3, 120)])
        feeds.trip_update(fm, "311", [(2, 0)])
        self.assertEqual(nictd.parse_delays(fm), {"515": 120, "311": 0})

    def test_south_shore_keeps_the_default_halo_width(self):
        # The Metra halo width must not reach another operator.
        self.assertNotIn("marker_ring_width", nictd.styling(self.obs["310"]))

    def test_needs_no_key(self):
        self.assertFalse(nictd.NICTD.needs_key)


class RegistryTests(unittest.TestCase):

    def test_operator_ids_are_the_released_ones(self):
        # ! An id is a config entry unique_id and part of entity names.
        self.assertEqual(set(ops.OPERATORS), {"metra", "nictd", "qr_citytrain", "vr_lahijunat",
                                              "renfe_madrid", "renfe_asturias", "renfe_sevilla",
                                              "renfe_cadiz", "renfe_malaga", "renfe_valencia",
                                              "renfe_murcia_alicante", "renfe_cartagena",
                                              "renfe_ferrol", "renfe_leon", "renfe_barcelona",
                                              "renfe_bilbao", "renfe_san_sebastian",
                                              "renfe_cantabria", "renfe_zaragoza",
                                              "vy", "go_ahead_norge", "flytoget",
                                              "sl_pendeltag", "vasttagen", "arlanda_express",
                                              "irish_rail", "ns", "nsw_trainlink", "vline"})

    def test_every_region_has_a_label_and_the_list_is_sorted(self):
        regions = ops.regions_in_use()
        self.assertEqual(list(regions.values()), sorted(regions.values()))
        self.assertEqual(set(regions), {"US-IL", "US-IN", "US-WI", "AU-NSW", "AU-QLD", "FI",
                                        "ES-AN", "ES-AR", "ES-AS", "ES-CB", "ES-CL", "ES-CT",
                                        "ES-GA", "ES-MC", "ES-MD", "ES-PV", "ES-VC", "NO", "SE", "IE", "NL",
                                        "AU-VIC"})

    def test_operators_in_region(self):
        self.assertEqual([o.id for o in ops.operators_in("US-IL")], ["metra", "nictd"])
        self.assertEqual([o.id for o in ops.operators_in("US-IN")], ["nictd"])
        self.assertEqual(ops.operators_in("US-XX"), [])
        self.assertEqual([o.id for o in ops.operators_in("AU-QLD")], ["qr_citytrain"])


if __name__ == "__main__":
    unittest.main()

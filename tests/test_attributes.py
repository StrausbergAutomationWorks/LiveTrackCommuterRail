"""Record -> attributes. No Home Assistant."""

import unittest

from _load import load

attributes = load("attributes")

D10_LAYERS = {"fixed", "water", "rail", "air_low", "air"}
NEVER = {"heading_deg", "speed_kmh", "max_extrapolation_s", "object_ids",
         "z_index_offset", "mmsi", "imo", "icao24", "registration"}

REC = {"vehicle_id": "8528", "latitude": 41.9, "longitude": -87.9,
       "in_service": True, "marker_label": "47", "train": "47", "line": "UP-W",
       "observed_at": "2026-10-02T07:00:00+00:00", "course_deg": 12.3,
       "icon_rotation_deg": 12.3, "icon_rotation_basis": "course"}


class AttributeTests(unittest.TestCase):

    def test_required_keys(self):
        a = attributes.to_attributes(dict(REC), "metra")
        self.assertEqual(a["identity"], "8528")
        self.assertEqual(a["marker_label"], "47")
        self.assertEqual(a["operator"], "metra")
        self.assertEqual(a["map_layer"], "rail")
        self.assertIn(a["map_layer"], D10_LAYERS)

    def test_position_is_not_an_attribute(self):
        a = attributes.to_attributes(dict(REC), "metra")
        self.assertNotIn("latitude", a)
        self.assertNotIn("longitude", a)

    def test_none_is_omitted_never_published(self):
        a = attributes.to_attributes(dict(REC, delay_min=None, line=None), "metra")
        self.assertNotIn("delay_min", a)
        self.assertNotIn("line", a)

    def test_unlisted_and_forbidden_keys_never_reach_the_map(self):
        rec = dict(REC, map_layer="air", heading_deg=90.0, speed_kmh=0,
                   max_extrapolation_s=60, object_ids={"mmsi": "1"},
                   z_index_offset=5, surprise="x")
        a = attributes.to_attributes(rec, "metra")
        self.assertEqual(a["map_layer"], "rail")
        self.assertFalse(NEVER & set(a), sorted(NEVER & set(a)))
        self.assertNotIn("surprise", a)


if __name__ == "__main__":
    unittest.main()

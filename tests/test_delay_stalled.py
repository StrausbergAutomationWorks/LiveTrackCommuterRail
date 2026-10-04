"""Backlog 275: `delay_min` and `stalled` reach the map through the allowlist.
The rules themselves are tested in saw-livetrack (tests/test_gtfs_delay_stall.py)."""

import unittest

from _load import load

attributes = load("attributes")

REC = {"vehicle_id": "8426", "marker_label": "835", "in_service": True}


class DelayAndStalled(unittest.TestCase):
    def test_both_pass_through(self):
        a = attributes.to_attributes(dict(REC, delay_min=12, stalled=True), "metra")
        self.assertEqual(a["delay_min"], 12)
        self.assertIs(a["stalled"], True)

    def test_negative_and_zero_delay_pass_through(self):
        for d in (-1, 0):
            self.assertEqual(attributes.to_attributes(dict(REC, delay_min=d), "metra")["delay_min"], d)

    def test_absent_stays_absent(self):
        a = attributes.to_attributes(dict(REC), "metra")
        self.assertNotIn("stalled", a)
        self.assertNotIn("delay_min", a)


if __name__ == "__main__":
    unittest.main()

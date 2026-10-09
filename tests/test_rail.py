"""The shipped rail files (rail/<operator>.json.gz) and their loader (SSOT 7.10).
Positions below are real fixes from the 2026-10-02 PM-peak capture and the recorded polls
of 2026-10-03 (bin\\ltcr_offshape_measure.txt, ltcr_offshape_narn.txt)."""

import gzip
import json
import os
import unittest

from _load import load

rail = load("rail")
const = load("const")
ops = load("operators")

ON = {  # real fixes, with their measured distance to NARN track
    "metra": [(41.516811, -87.969818),   # RI 705, 210 m: the farthest real fix measured
              (41.885311, -87.623306),   # ME 330 at Millennium Station, underground, 144 m
              (42.494015, -88.097023),   # NCS 107 laying over north of Antioch, 3 m
              (41.871738, -87.638191)],  # an MD-N train south of Union Station, 2 m
    "nictd": [(41.52284, -87.51792)],    # the first point of NICTD's own Monon shape
}
OFF = {  # unit 8426 (UP-N 835), whose GPS ran off the line
    "metra": [(41.978882, -87.670212),   # 374 m, the closest it came, 2026-10-03 23:18
              (42.097946, -87.711418),   # 1,060 m twenty minutes later
              (42.366550, -87.788582)],  # in Lake Michigan, 2026-10-04 01:32
}


class ShippedFiles(unittest.TestCase):

    def test_a_file_for_every_railroad_with_a_timetable(self):
        for oid, op in ops.OPERATORS.items():
            if op.static_url:
                self.assertTrue(os.path.isfile(os.path.join(rail.RAIL_DIR, f"{oid}.json.gz")), oid)

    def test_header(self):
        for oid in ("metra", "nictd"):
            with gzip.open(os.path.join(rail.RAIL_DIR, f"{oid}.json.gz"), "rt", encoding="utf-8") as fh:
                doc = json.load(fh)
            self.assertEqual(doc["format"], rail.FORMAT)
            self.assertEqual(doc["operator"], oid)
            self.assertIn("public domain", doc["source"])
            self.assertEqual((doc["corridor_m"], doc["tolerance_m"]), (3000, 10))
            self.assertEqual(doc["net_excluded"], ["A", "X", "R"])

    def test_real_fixes_are_on_rail_and_the_bad_unit_is_not(self):
        for oid in ("metra", "nictd"):
            on = rail.check(rail.load(oid))
            for p in ON.get(oid, []):
                self.assertTrue(on(*p), (oid, p))
            for p in OFF.get(oid, []):
                self.assertFalse(on(*p), (oid, p))

    def test_size(self):
        for oid in ("metra", "nictd"):
            self.assertGreater(len(rail.load(oid)), 1000, oid)


class Loader(unittest.TestCase):

    def test_no_file_no_check(self):
        self.assertIsNone(rail.load("no_such_railroad"))

    def test_wrong_format_or_empty_is_refused(self):
        import tempfile
        d = tempfile.mkdtemp()
        saved = rail.RAIL_DIR
        try:
            rail.RAIL_DIR = d
            for name, doc in (("v2", {"format": 2, "lines": [[[41.0, -87.0], [41.1, -87.0]]]}),
                              ("empty", {"format": 1, "lines": []}),
                              ("list", [1, 2])):
                with gzip.open(os.path.join(d, name + ".json.gz"), "wt", encoding="utf-8") as fh:
                    json.dump(doc, fh)
                self.assertIsNone(rail.load(name), name)
            with open(os.path.join(d, "junk.json.gz"), "wb") as fh:
                fh.write(b"not gzip")
            self.assertIsNone(rail.load("junk"))
            with gzip.open(os.path.join(d, "badjson.json.gz"), "wb") as fh:
                fh.write(b"{not json")
            self.assertIsNone(rail.load("badjson"))
        finally:
            rail.RAIL_DIR = saved

    def test_threshold(self):
        self.assertEqual(const.OFF_RAIL_M, 300.0)


if __name__ == "__main__":
    unittest.main()

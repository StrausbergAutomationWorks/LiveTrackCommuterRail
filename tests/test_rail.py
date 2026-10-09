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


def _zip(files):
    import io as _io
    import zipfile as _zf
    b = _io.BytesIO()
    with _zf.ZipFile(b, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return b.getvalue()


MONON_1035 = [(41.582932, -87.518532), (41.582489, -87.518517), (41.57925, -87.518448)]


class OwnShapes(unittest.TestCase):
    """2026-10-09: NARN lacks NICTD's Monon Corridor south of Hammond (opened 2025).
    Monon 1035 was 0.2-0.5 m from NICTD's own shape and 2.0-2.3 km from NARN."""

    SHAPES = ("shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence\r\n"
              "A, 41.58, -87.5185, 3\r\nA, 41.60, -87.5185, 1\r\nA, 41.59, -87.5185, 2\r\n"
              "B, 41.58, -87.5185, 1\r\nB, 41.59, -87.5185, 2\r\nB, 41.60, -87.5185, 3\r\n")

    def test_shapes_by_sequence_simplified_and_deduplicated(self):
        got = rail.shapes_from_zip(_zip({"shapes.txt": self.SHAPES}))
        # A runs 41.60 -> 41.58 by sequence; its middle point is collinear and dropped;
        # B is A reversed and is dropped as a duplicate.
        self.assertEqual(got, [[[41.6, -87.5185], [41.58, -87.5185]]])

    def test_no_shapes_file(self):
        self.assertEqual(rail.shapes_from_zip(_zip({"stops.txt": "stop_id\nA\n"})), [])

    def test_the_monon_gap_is_real_in_the_shipped_file(self):
        on = rail.check(rail.load("nictd"))
        for p in MONON_1035:
            self.assertFalse(on(*p), p)

    def test_monon_on_its_own_shape_is_on_rail(self):
        c = rail.RailCheck(rail.load("nictd"))
        c.set_shapes({"fetched_at": 1, "rail_shapes": rail.shapes_from_zip(_zip({"shapes.txt": self.SHAPES}))})
        for p in MONON_1035:
            self.assertTrue(c(*p), p)
        self.assertFalse(c(42.366550, -87.788582))          # the lake is still off rail
        self.assertTrue(c(41.52284, -87.51792))              # NARN still counts

    def test_nothing_refused_before_the_timetable(self):
        c = rail.RailCheck(rail.load("metra"))
        self.assertTrue(c(42.366550, -87.788582))
        c.set_shapes({"fetched_at": 1})                      # a cache without shapes: still waiting
        self.assertTrue(c(42.366550, -87.788582))
        c.set_shapes({"fetched_at": 1, "rail_shapes": []})
        self.assertFalse(c(42.366550, -87.788582))
        self.assertEqual(c.shape_segments, 0)

    def test_no_rail_at_all_refuses_nothing(self):
        c = rail.RailCheck(None)
        c.set_shapes({"fetched_at": 1, "rail_shapes": []})
        self.assertTrue(c(42.366550, -87.788582))

    def test_shapes_alone_decide_without_narn(self):
        c = rail.RailCheck(None)
        c.set_shapes({"fetched_at": 1, "rail_shapes": [[[41.60, -87.5185], [41.58, -87.5185]]]})
        self.assertTrue(c(41.59, -87.5185))
        self.assertFalse(c(41.59, -87.40))

    def test_new_timetable_new_shapes_same_timetable_kept(self):
        c = rail.RailCheck(None)
        c.set_shapes({"fetched_at": 1, "rail_shapes": [[[41.60, -87.5185], [41.58, -87.5185]]]})
        c.set_shapes({"fetched_at": 1, "rail_shapes": [[[42.0, -88.0], [42.1, -88.0]]]})
        self.assertTrue(c(41.59, -87.5185))                  # same fetch: not rebuilt
        c.set_shapes({"fetched_at": 2, "rail_shapes": [[[42.0, -88.0], [42.1, -88.0]]]})
        self.assertFalse(c(41.59, -87.5185))
        self.assertTrue(c(42.05, -88.0))


if __name__ == "__main__":
    unittest.main()

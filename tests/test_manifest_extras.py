"""Backlog 286: Home Assistant ignores a requirement's extras (it compares only the installed version of the base
package), so every package of each saw-livetrack extra the manifest names must also be named in the manifest by
itself. Read from the installed saw-livetrack's own metadata, so a pin change there fails here instead of drifting."""
import json
import os
import re
import unittest
from importlib import metadata

MANIFEST = os.path.join(os.path.dirname(__file__), "..", "custom_components", "live_track_commuter_rail",
                        "manifest.json")


def _name(req):
    """The distribution name of a requirement string, normalised (PEP 503)."""
    m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", req)
    return re.sub(r"[-_.]+", "-", m.group(1)).lower()


class ManifestNamesEveryExtraPackage(unittest.TestCase):
    def setUp(self):
        with open(MANIFEST, encoding="utf-8") as f:
            self.reqs = json.load(f)["requirements"]

    def test_each_extras_packages_are_named(self):
        lib = [r for r in self.reqs if _name(r) == "saw-livetrack"]
        self.assertEqual(len(lib), 1, self.reqs)
        extras = re.search(r"\[([^\]]*)\]", lib[0])
        self.assertIsNotNone(extras, "the manifest names no saw-livetrack extra")
        named = {_name(r) for r in self.reqs}
        declared = metadata.requires("saw-livetrack") or []
        for extra in (e.strip() for e in extras.group(1).split(",")):
            pkgs = {_name(r) for r in declared
                    if re.search(r"""extra\s*==\s*['"]%s['"]""" % re.escape(extra), r)}
            self.assertTrue(pkgs, f"saw-livetrack declares no packages for [{extra}]")
            self.assertEqual(pkgs - named, set(), f"[{extra}]'s packages missing from the manifest")

    def test_a_missing_package_is_caught(self):
        # The check itself: drop one named package and it must notice.
        named = {_name(r) for r in self.reqs if _name(r) != "gtfs-realtime-bindings"}
        declared = metadata.requires("saw-livetrack") or []
        pkgs = {_name(r) for r in declared if re.search(r"""extra\s*==\s*['"]gtfs['"]""", r)}
        self.assertIn("gtfs-realtime-bindings", pkgs - named)


if __name__ == "__main__":
    unittest.main()

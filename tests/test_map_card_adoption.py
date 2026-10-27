"""Backlog 291: the map card is offered in setup, before the first refresh; nothing
happens on unload; only the domain's LAST entry withdraws it; and the shipped bundle
is a released card with no compressed copy beside it.

__init__.py imports Home Assistant, which this suite does not have, so it is loaded
under its own name with stand-ins for the three Home Assistant modules it imports and
for the two modules it hands work to (the coordinator and shared_map_card). The real
const and operators modules are used. sys.modules is restored afterwards.
"""

import asyncio
import importlib.util
import pathlib
import sys
import types
import unittest

from _load import COMP, load

const = load("const")
OPERATORS = load("operators").OPERATORS

CALLS = []


class _Coordinator:
    def __init__(self, hass, entry, op):
        self.op = op

    async def async_config_entry_first_refresh(self):
        CALLS.append(("first_refresh",))

    def release(self):
        CALLS.append(("release",))


async def _offer(hass, domain, folder):
    CALLS.append(("offer", domain, folder))


async def _withdraw(hass, domain):
    CALLS.append(("withdraw", domain))


def _load_init():
    """__init__.py with stand-ins, as module ltcr._init_under_test."""
    saved = {k: sys.modules.get(k) for k in (
        "homeassistant", "homeassistant.config_entries", "homeassistant.const",
        "homeassistant.core", "ltcr.coordinator", "ltcr.shared_map_card")}
    ha = types.ModuleType("homeassistant")
    ce = types.ModuleType("homeassistant.config_entries")
    ce.ConfigEntry = object
    hc = types.ModuleType("homeassistant.const")
    hc.Platform = types.SimpleNamespace(GEO_LOCATION="geo_location", SENSOR="sensor")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    coord = types.ModuleType("ltcr.coordinator")
    coord.CommuterRailCoordinator = _Coordinator
    smc = types.ModuleType("ltcr.shared_map_card")
    smc.async_offer_map_card = _offer
    smc.async_withdraw_map_card = _withdraw
    sys.modules.update({
        "homeassistant": ha, "homeassistant.config_entries": ce,
        "homeassistant.const": hc, "homeassistant.core": core,
        "ltcr.coordinator": coord, "ltcr.shared_map_card": smc})
    try:
        # Not a package of its own (a file named __init__.py would be), so
        # its relative imports resolve against ltcr.
        spec = importlib.util.spec_from_file_location(
            "ltcr._init_under_test", COMP / "__init__.py",
            submodule_search_locations=None)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


INIT = _load_init()


class _Entry:
    def __init__(self, entry_id, op_id):
        self.entry_id = entry_id
        self.data = {const.CONF_OPERATOR: op_id}

    def async_on_unload(self, fn):
        pass

    def add_update_listener(self, fn):
        return fn


class _ConfigEntries:
    def __init__(self, entries):
        self.entries = entries

    def async_entries(self, domain):
        CALLS.append(("async_entries", domain))
        return list(self.entries)

    async def async_forward_entry_setups(self, entry, platforms):
        CALLS.append(("forward",))

    async def async_unload_platforms(self, entry, platforms):
        CALLS.append(("unload_platforms",))
        return True


class _Hass:
    def __init__(self, entries=()):
        self.data = {}
        self.config_entries = _ConfigEntries(entries)


OP_ID = next(iter(OPERATORS))


class TestMapCardAdoption(unittest.TestCase):
    def setUp(self):
        CALLS.clear()

    def test_offer_in_setup_before_first_refresh(self):
        hass = _Hass()
        ok = asyncio.run(INIT.async_setup_entry(hass, _Entry("a", OP_ID)))
        self.assertTrue(ok)
        names = [c[0] for c in CALLS]
        self.assertEqual(names.count("offer"), 1)
        self.assertLess(names.index("offer"), names.index("first_refresh"))
        offer = CALLS[names.index("offer")]
        self.assertEqual(offer[1], const.DOMAIN)
        self.assertEqual(pathlib.Path(offer[2]), COMP / "frontend")
        self.assertNotIn("withdraw", names)

    def test_unload_neither_offers_nor_withdraws(self):
        hass = _Hass()
        ok = asyncio.run(INIT.async_unload_entry(hass, _Entry("a", OP_ID)))
        self.assertTrue(ok)
        names = [c[0] for c in CALLS]
        self.assertEqual(names, ["unload_platforms"])

    def test_remove_with_another_entry_left_keeps_the_card(self):
        a, b = _Entry("a", OP_ID), _Entry("b", OP_ID)
        hass = _Hass([a, b])
        asyncio.run(INIT.async_remove_entry(hass, a))
        self.assertIn(("async_entries", const.DOMAIN), CALLS)
        self.assertNotIn("withdraw", [c[0] for c in CALLS])

    def test_remove_of_the_last_entry_withdraws(self):
        a = _Entry("a", OP_ID)
        # Home Assistant may or may not still list the entry being removed.
        for listed in ([a], []):
            CALLS.clear()
            asyncio.run(INIT.async_remove_entry(_Hass(listed), a))
            self.assertEqual([c for c in CALLS if c[0] == "withdraw"],
                             [("withdraw", const.DOMAIN)])


class TestShippedBundle(unittest.TestCase):
    FOLDER = COMP / "frontend"

    def test_released_card_alone_in_its_folder(self):
        names = sorted(p.name for p in self.FOLDER.iterdir())
        self.assertEqual(names, ["live-track-map-card.js"])

    def test_line_one_is_a_release_stamp(self):
        with open(self.FOLDER / "live-track-map-card.js", "rb") as f:
            first = f.readline()
        self.assertRegex(first, rb"^/\*! live-track-map-card \d+\.\d+\.\d+\+[0-9a-f]{7} \*/")

    def test_manifest_orders_after_lovelace_and_needs_http(self):
        import json
        m = json.loads((COMP / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("http", m["dependencies"])
        self.assertIn("lovelace", m["after_dependencies"])

    def test_both_repairs_issues_are_translated(self):
        import json
        for f in ("strings.json", "translations/en.json"):
            issues = json.loads((COMP / f).read_text(encoding="utf-8"))["issues"]
            for key, ph in (("map_card_yaml_resource", "{url}"),
                            ("map_card_duplicate_resources", "{urls}")):
                self.assertIn(ph, issues[key]["description"], f)
                self.assertTrue(issues[key]["title"], f)


if __name__ == "__main__":
    unittest.main()

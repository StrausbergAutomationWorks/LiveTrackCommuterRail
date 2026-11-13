"""The setup dialog in every language shipped (Lee 2026-11-13): each translations/<lang>.json has exactly en.json's keys,
the same placeholders in every string, and the YAML lines of the repair issue unchanged; strings.json equals en.json; the
region selector's keys are the REGIONS codes in lower case (hassfest's [a-z0-9-_] rule; config_flow maps them back)."""
import json
import pathlib
import re
import unittest

from _load import load

COMP = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_commuter_rail"
LANGS = ("fi", "sv", "nb", "es", "nl", "ga")
PH = re.compile(r"\{[a-z_]+\}")


def leaves(d, pre=""):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from leaves(v, pre + k + ".")
        else:
            yield pre + k, v


def read(name):
    return json.loads((COMP / name).read_text(encoding="utf-8"))


class Translations(unittest.TestCase):
    def setUp(self):
        self.en = dict(leaves(read("translations/en.json")))

    def test_strings_json_is_en_json(self):
        self.assertEqual(read("strings.json"), read("translations/en.json"))

    def test_every_language_has_every_string_and_placeholder(self):
        for lang in LANGS:
            tr = dict(leaves(read(f"translations/{lang}.json")))
            self.assertEqual(set(tr), set(self.en), lang)
            for k, v in tr.items():
                self.assertTrue(v.strip(), (lang, k))
                self.assertEqual(sorted(PH.findall(v)), sorted(PH.findall(self.en[k])), (lang, k))
            self.assertTrue(tr["issues.map_card_yaml_resource.description"].endswith(
                "\n\n- url: {url}\n  type: module"), lang)

    def test_region_keys_are_the_codes_in_lower_case(self):
        base = load("operators.base")
        keys = {k.rsplit(".", 1)[1] for k in self.en if k.startswith("selector.region.options.")}
        self.assertEqual(keys, {c.lower() for c in base.REGIONS})
        for k in keys:
            self.assertRegex(k, r"^[a-z0-9-_]+$")

    def test_the_flow_offers_lower_case_values_with_the_translation_key(self):
        src = (COMP / "config_flow.py").read_text(encoding="utf-8")
        self.assertIn('SelectOptionDict(value=c.lower(), label=l) for c, l in regions.items()], "region")', src)
        self.assertIn("{c.lower(): c for c in regions}", src)


if __name__ == "__main__":
    unittest.main()

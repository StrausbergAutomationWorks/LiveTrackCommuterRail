"""Import the component's HA-free modules without Home Assistant.

The package __init__ imports Home Assistant, so it must never run here. This
registers the component folder as a bare package named `ltcr` whose __init__
is skipped; `ltcr.fleet`, `ltcr.operators` and `ltcr.attributes` then import
normally, relative imports included.

Run from the repo root:  python -m unittest discover -s tests -v
"""

import importlib
import importlib.machinery
import importlib.util
import pathlib
import sys

COMP = (pathlib.Path(__file__).resolve().parents[1]
        / "custom_components" / "live_track_commuter_rail")

if "ltcr" not in sys.modules:
    spec = importlib.machinery.ModuleSpec("ltcr", None, is_package=True)
    pkg = importlib.util.module_from_spec(spec)
    pkg.__path__ = [str(COMP)]
    sys.modules["ltcr"] = pkg


def load(name: str):
    return importlib.import_module(f"ltcr.{name}")

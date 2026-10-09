"""Is the cached timetable the realtime feed's? (Metra's GTFS static change,
Developer Change Notice received 2026-10-08.) timetable_stale, and
StaticTimetable's early refresh, which must still fetch at most once an hour.

StaticTimetable imports aiohttp and Home Assistant for typing and the session
only; where they are not installed (this suite runs without Home Assistant)
the two names it touches are stubbed. Nothing here makes a network request."""

import asyncio
import io
import os
import shutil
import sys
import tempfile
import types
import unittest
import zipfile


def _stub():
    try:
        import aiohttp  # noqa: F401
    except ImportError:
        m = types.ModuleType("aiohttp")

        class ClientTimeout:
            def __init__(self, total=None):
                self.total = total

        class ClientSession:
            pass

        m.ClientTimeout, m.ClientSession = ClientTimeout, ClientSession
        sys.modules["aiohttp"] = m
    try:
        import homeassistant.core  # noqa: F401
    except ImportError:
        ha = types.ModuleType("homeassistant")
        core = types.ModuleType("homeassistant.core")

        class HomeAssistant:
            pass

        core.HomeAssistant = HomeAssistant
        ha.core = core
        sys.modules["homeassistant"], sys.modules["homeassistant.core"] = ha, core


_stub()
from _load import load  # noqa: E402

statics = load("statics")
schedule = load("schedule")
ops = load("operators")


def _zip(version="V1"):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("agency.txt", "agency_id,agency_name,agency_timezone\nM,M,America/Chicago\n")
        z.writestr("stops.txt", "stop_id,stop_name,stop_lat,stop_lon\nA,A,41.8,-87.6\n")
        z.writestr("feed_info.txt", f"feed_publisher_name,feed_version\nM,{version}\n")
    return b.getvalue()


class Hass:
    def __init__(self, folder):
        self.config = types.SimpleNamespace(path=lambda *a: os.path.join(folder, *a))

    async def async_add_executor_job(self, fn, *args):
        return fn(*args)


class Resp:
    def __init__(self, raw):
        self.status, self.content_length, self._raw = 200, len(raw), raw

    async def read(self):
        return self._raw

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class Session:
    def __init__(self, raw):
        self.raw, self.calls = raw, 0

    def get(self, url, **kw):
        self.calls += 1
        return Resp(self.raw)


class Stale(unittest.TestCase):

    def test_share_and_minimum(self):
        f = schedule.timetable_stale
        self.assertFalse(f(0, 0))
        self.assertFalse(f(0, 4))          # too few trips to say
        self.assertTrue(f(0, 5))
        self.assertTrue(f(2, 5))
        self.assertFalse(f(3, 5))
        self.assertFalse(f(739, 739))      # measured, right timetable
        self.assertTrue(f(0, 739))         # measured, wrong timetable
        self.assertTrue(f(369, 739))
        self.assertFalse(f(370, 739))
        self.assertFalse(f(5, 10))         # exactly half is not stale

    def test_trip_coverage_is_the_librarys(self):
        import saw_livetrack.gtfs as g
        self.assertIs(schedule.trip_coverage, g.trip_coverage)


class EarlyRefresh(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, ".storage"))
        self.clock = [1_000_000.0]
        self._time = statics.time
        statics.time = types.SimpleNamespace(time=lambda: self.clock[0])
        self.session = Session(_zip())
        self.t = statics.StaticTimetable(Hass(self.tmp), self.session, ops.OPERATORS["metra"])
        self.assertTrue(self.t.due())
        asyncio.run(self.t.async_ensure())          # no cache file: fetched

    def tearDown(self):
        statics.time = self._time
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_first_load_fetches_and_says_which_timetable(self):
        self.assertEqual(self.session.calls, 1)
        info = self.t.info
        self.assertEqual(info["feed_version"], "V1")
        self.assertEqual(info["fetched_at"], 1_000_000.0)
        self.assertIn("trips_scheduled", info)

    def test_a_fresh_timetable_is_left_alone(self):
        self.clock[0] += 3 * 3600
        self.assertFalse(self.t.due())
        asyncio.run(self.t.async_ensure())
        self.assertEqual(self.session.calls, 1)

    def test_a_request_waits_for_the_hour_since_the_last_fetch(self):
        self.t.request_refresh()
        self.clock[0] += statics.RETRY_S - 1
        self.assertFalse(self.t.due())
        asyncio.run(self.t.async_ensure())
        self.assertEqual(self.session.calls, 1)
        self.clock[0] += 1
        self.assertTrue(self.t.due())
        asyncio.run(self.t.async_ensure())
        self.assertEqual(self.session.calls, 2)

    def test_the_fetch_spends_the_request(self):
        self.t.request_refresh()
        self.clock[0] += statics.RETRY_S
        asyncio.run(self.t.async_ensure())
        self.clock[0] += statics.RETRY_S
        self.assertFalse(self.t.due())          # fresh, and nothing asked since

    def test_asking_every_poll_costs_one_fetch_an_hour(self):
        for _ in range(240):                    # two hours of 30 s polls, each asking
            self.clock[0] += 30
            self.t.request_refresh()
            if self.t.due():
                asyncio.run(self.t.async_ensure())
        self.assertEqual(self.session.calls, 3)

    def test_a_cache_without_route_lines_is_fetched_again(self):
        # Written before 2026-10-09: no rail_shapes, so the off-rail check would wait
        # for them until the daily refresh. It is read as no cache at all.
        import json as _json
        path = os.path.join(self.tmp, ".storage", "saw_gtfs_metra.json")
        with open(path, encoding="utf-8") as fh:
            d = _json.load(fh)
        self.assertEqual(d["rail_shapes"], [])
        d.pop("rail_shapes")
        with open(path, "w", encoding="utf-8") as fh:
            _json.dump(d, fh)
        t = statics.StaticTimetable(Hass(self.tmp), self.session, ops.OPERATORS["metra"])
        asyncio.run(t.async_ensure())
        self.assertEqual(self.session.calls, 2)
        self.assertEqual(t.data["rail_shapes"], [])

    def test_a_cache_with_route_lines_is_used(self):
        t = statics.StaticTimetable(Hass(self.tmp), self.session, ops.OPERATORS["metra"])
        asyncio.run(t.async_ensure())
        self.assertEqual(self.session.calls, 1)

    def test_a_new_timetable_is_picked_up(self):
        self.session.raw = _zip("V2")
        self.t.request_refresh()
        self.clock[0] += statics.RETRY_S
        asyncio.run(self.t.async_ensure())
        self.assertEqual(self.t.info["feed_version"], "V2")


if __name__ == "__main__":
    unittest.main()

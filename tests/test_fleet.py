"""Fleet: what is published, and each record. No Home Assistant.

Positions are built by offsetting latitude: 0.001 deg is ~111 m.
"""

import unittest
from datetime import datetime, timedelta, timezone

from _load import load

fleet_mod = load("fleet")
base = load("operators.base")
const = load("const")
Obs = base.Obs

T = datetime(2026, 10, 2, 7, 0, 0, tzinfo=timezone.utc)
LAT, LON = 41.880, -87.950


def ob(vid="8528", dlat=0.0, t=0, in_service=True, train="47", line="UP-W",
       course=270.0, ts=True):
    return Obs(vehicle_id=vid, lat=LAT + dlat, lon=LON,
               observed_at=(T + timedelta(seconds=t)) if ts else None,
               in_service=in_service, train=train if in_service else None,
               line=line, reported_course=course)


class Clock:
    def __init__(self):
        self.now = 1_000_000.0

    def tick(self, s):
        self.now += s
        return self.now


class InServiceTests(unittest.TestCase):

    def setUp(self):
        self.f = fleet_mod.Fleet()
        self.c = Clock()

    def poll(self, *obs, **kw):
        return self.f.update(list(obs), self.c.now, **kw)

    def test_shown_at_once_with_its_number_and_no_motion_yet(self):
        r = self.poll(ob())
        rec = r["vehicles"]["8528"]
        self.assertEqual(rec["marker_label"], "47")
        self.assertEqual(rec["observed_at"], T.isoformat())
        self.assertEqual(rec["last_seen"], rec["observed_at"])
        for key in ("previous_latitude", "course_deg", "icon_rotation_deg",
                    "segment_duration_s", "position_jump"):
            self.assertNotIn(key, rec, key)

    def test_a_move_publishes_the_reported_course_and_the_segment(self):
        self.poll(ob())
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.005, t=30, course=12.3))["vehicles"]["8528"]
        self.assertEqual(rec["course_deg"], 12.3)
        self.assertEqual((rec["icon_rotation_deg"], rec["icon_rotation_basis"]), (12.3, "course"))
        self.assertEqual(rec["previous_latitude"], LAT)
        self.assertEqual(rec["segment_duration_s"], 30)
        gap = (datetime.fromisoformat(rec["observed_at"])
               - datetime.fromisoformat(rec["previous_observed_at"])).total_seconds()
        self.assertEqual(rec["segment_duration_s"], gap)

    def test_course_from_two_fixes_when_the_source_reports_none(self):
        self.poll(ob(course=None))
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.005, t=30, course=None))["vehicles"]["8528"]
        self.assertAlmostEqual(rec["course_deg"], 0.0, delta=0.5)   # due north

    def test_at_rest_the_course_goes_and_the_arrow_is_held(self):
        self.poll(ob())
        self.c.tick(30)
        self.poll(ob(dlat=0.005, t=30, course=12.3))
        self.c.tick(const.REST_S + 1)
        # Standing: the feed now says 359.0, which must not turn the arrow.
        rec = self.poll(ob(dlat=0.005, t=30 + const.REST_S + 1, course=359.0))["vehicles"]["8528"]
        self.assertNotIn("course_deg", rec)
        self.assertEqual((rec["icon_rotation_deg"], rec["icon_rotation_basis"]), (12.3, "held"))

    def test_jitter_under_50_m_is_not_a_move(self):
        self.poll(ob())
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.0003, t=30, course=359.0))["vehicles"]["8528"]   # ~33 m
        self.assertNotIn("course_deg", rec)
        self.assertNotIn("icon_rotation_deg", rec)

    def test_a_duplicate_poll_keeps_the_segment(self):
        self.poll(ob())
        self.c.tick(30)
        a = self.poll(ob(dlat=0.005, t=30))["vehicles"]["8528"]
        self.c.tick(30)
        b = self.poll(ob(dlat=0.005, t=30))["vehicles"]["8528"]
        for key in ("previous_latitude", "previous_longitude", "previous_observed_at",
                    "segment_duration_s"):
            self.assertEqual(a[key], b[key], key)

    def test_an_impossible_jump_is_placed_not_slid(self):
        self.poll(ob())
        self.c.tick(30)
        self.poll(ob(dlat=0.005, t=30))
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.5, t=60))["vehicles"]["8528"]   # ~55 km in 30 s
        self.assertIs(rec["position_jump"], True)
        self.assertNotIn("previous_latitude", rec)
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.505, t=90))["vehicles"]["8528"]
        self.assertNotIn("position_jump", rec)

    def test_no_segment_across_a_long_gap(self):
        self.poll(ob())
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.005, t=const.MAX_SEGMENT_S + 1))["vehicles"]["8528"]
        self.assertNotIn("previous_latitude", rec)
        self.assertNotIn("segment_duration_s", rec)

    def test_no_segment_without_observation_times(self):
        self.poll(ob(ts=False))
        self.c.tick(30)
        rec = self.poll(ob(dlat=0.005, ts=False))["vehicles"]["8528"]
        for key in ("observed_at", "last_seen", "previous_latitude", "segment_duration_s"):
            self.assertNotIn(key, rec, key)

    def test_delay_in_minutes_for_trains_in_service(self):
        rec = self.poll(ob(train="515"), delays={"515": 150})["vehicles"]["8528"]
        self.assertEqual(rec["delay_min"], 2)

    def test_counts(self):
        r = self.poll(ob(vid="1", train="515"), ob(vid="2", train="515"),
                      ob(vid="3", in_service=False), ob(vid="4", in_service=False))
        self.assertEqual((r["trains_in_service"], r["non_revenue"], r["vehicles_in_feed"]),
                         (1, 2, 4))

    def test_styling_is_applied(self):
        f = fleet_mod.Fleet(styling=lambda o: {"marker_color": "#123456"})
        rec = f.update([ob()], self.c.now)["vehicles"]["8528"]
        self.assertEqual(rec["marker_color"], "#123456")


class NonRevenueTests(unittest.TestCase):
    """06_MAP_CONTRACT.md D8: appear on the first move, leave only after
    sustained stillness."""

    def setUp(self):
        self.f = fleet_mod.Fleet()
        self.c = Clock()

    def poll(self, *obs, **kw):
        return self.f.update(list(obs), self.c.now, **kw)

    def nis(self, dlat=0.0, t=0):
        return ob(vid="8425", dlat=dlat, t=t, in_service=False, line=None, course=359.0)

    def test_parked_is_hidden_from_the_first_poll(self):
        r = self.poll(self.nis())
        self.assertNotIn("8425", r["vehicles"])
        self.assertEqual(r["non_revenue"], 1)

    def test_shown_on_the_first_move_labelled_nis(self):
        self.poll(self.nis())
        self.c.tick(30)
        rec = self.poll(self.nis(dlat=0.005, t=30))["vehicles"]["8425"]
        self.assertEqual(rec["marker_label"], "NIS 8425")
        self.assertIs(rec["in_service"], False)
        self.assertNotIn("train", rec)

    def test_held_through_a_stop_then_removed_after_the_hold(self):
        self.poll(self.nis())
        self.c.tick(30)
        self.poll(self.nis(dlat=0.005, t=30))
        self.c.tick(const.HOLD_S - 30)
        r = self.poll(self.nis(dlat=0.005, t=const.HOLD_S))
        self.assertIn("8425", r["vehicles"])       # crawled to a stop, still shown
        self.c.tick(60)
        r = self.poll(self.nis(dlat=0.005, t=const.HOLD_S + 60))
        self.assertNotIn("8425", r["vehicles"])
        self.assertEqual(r["departed"], ["8425"])
        self.c.tick(30)
        r = self.poll(self.nis(dlat=0.005, t=const.HOLD_S + 90))
        self.assertEqual(r["departed"], [])        # departs once, not every poll

    def test_wander_never_shows_it(self):
        self.poll(self.nis())
        for i in range(1, 6):
            self.c.tick(30)
            r = self.poll(self.nis(dlat=0.0003 * (i % 2), t=30 * i))   # ~33 m back and forth
            self.assertNotIn("8425", r["vehicles"])

    def test_show_parked_shows_it_at_once(self):
        r = self.poll(self.nis(), show_parked=True)
        self.assertEqual(r["vehicles"]["8425"]["marker_label"], "NIS 8425")


class AbsenceTests(unittest.TestCase):

    def setUp(self):
        self.f = fleet_mod.Fleet()
        self.c = Clock()

    def test_absent_within_grace_is_not_departed_then_is(self):
        self.f.update([ob()], self.c.now)
        self.c.tick(30)
        r = self.f.update([], self.c.now)
        self.assertEqual((r["vehicles"], r["departed"]), ({}, []))
        self.c.tick(const.GRACE_S)
        r = self.f.update([], self.c.now)
        self.assertEqual(r["departed"], ["8528"])
        self.assertEqual(self.f.stats()["known"], 0)

    def test_back_within_grace_keeps_its_segment(self):
        self.f.update([ob()], self.c.now)
        self.c.tick(30)
        self.f.update([ob(dlat=0.005, t=30)], self.c.now)
        self.c.tick(30)
        self.f.update([], self.c.now)
        self.c.tick(30)
        rec = self.f.update([ob(dlat=0.010, t=90)], self.c.now)["vehicles"]["8528"]
        self.assertEqual(rec["previous_latitude"], LAT + 0.005)

    def test_the_same_unit_twice_in_one_feed_is_one_vehicle(self):
        r = self.f.update([ob(), ob(dlat=0.01)], self.c.now)
        self.assertEqual(r["vehicles_in_feed"], 1)
        self.assertEqual(r["vehicles"]["8528"]["latitude"], LAT)


if __name__ == "__main__":
    unittest.main()

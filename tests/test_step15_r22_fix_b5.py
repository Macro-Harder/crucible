"""Pins for fix wave 22, builder b5, Group 5: the MOD-10 day
limbs, rows R22-011 and R22-012 of the Round 22 register.

Unit 1, row R22-011: retain_daily_aggregate_deliveries, at the
day limb of its non numeric component refusal.
Unit 2, row R22-012: retain_checkpoint, at its second checkpoint
refusal sentence.

Distinguishing pins fail on the pristine basis and pass on the
cured copy. Control pins pass on both trees.
"""
import unittest

from crucible import mod10


class LyingStr(str):
    """A text value storing one text whose string reading
    answers another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie


class RaisingStr(str):
    """A text value storing one text whose string and repr
    readings both raise."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


def bad_delivery(day):
    return {
        "simulated_day": day,
        "viewer_id": "viewer-1",
        "joint_outcome_components": ["text", 2.0],
        "component_denominators": [1.0, 1.0],
    }


def refusal_text(run_id, day):
    try:
        mod10.retain_daily_aggregate_deliveries(
            run_id, [bad_delivery(day)])
    except ValueError as error:
        return str(error)
    return ""


class TestR22011AggregateDayLimb(unittest.TestCase):

    def test_distinguishing_lying_day_fake_names_stored(self):
        text = refusal_text(
            "r22-b5-u1-d1", LyingStr("day-3", "day-FAKE"))
        self.assertIn("at day day-3", text)
        self.assertNotIn("day-FAKE", text)

    def test_distinguishing_lying_day_seven_names_stored_day3(self):
        text = refusal_text(
            "r22-b5-u1-d2", LyingStr("day-3", "7"))
        self.assertIn("at day day-3", text)
        self.assertNotIn("at day 7", text)

    def test_distinguishing_lying_day_seven_names_stored_zzz(self):
        text = refusal_text(
            "r22-b5-u1-d3", LyingStr("zzz-day", "7"))
        self.assertIn("at day zzz-day", text)
        self.assertNotIn("at day 7", text)

    def test_distinguishing_raising_day_names_stored(self):
        text = refusal_text("r22-b5-u1-d4", RaisingStr("day-3"))
        self.assertIn("at day day-3", text)

    def test_control_plain_int_day_named(self):
        text = refusal_text("r22-b5-u1-c1", 7)
        self.assertIn("at day 7", text)
        self.assertIn("non numeric form", text)

    def test_control_plain_text_day_named(self):
        text = refusal_text("r22-b5-u1-c2", "day-3")
        self.assertIn("at day day-3", text)
        self.assertIn("non numeric form", text)

    def test_control_valid_delivery_retained(self):
        good = {
            "simulated_day": 1,
            "viewer_id": "viewer-1",
            "joint_outcome_components": [1.0, 2.0],
            "component_denominators": [1.0, 1.0],
        }
        count = mod10.retain_daily_aggregate_deliveries(
            "r22-b5-u1-c3", [good])
        self.assertEqual(count, 1)


def second_checkpoint_text(run_id, first_day, second_day):
    mod10.retain_checkpoint(
        {"run_identifier": run_id, "simulated_day": first_day})
    try:
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": second_day})
    except ValueError as error:
        return str(error)
    return ""


class TestR22012CheckpointDayLimb(unittest.TestCase):

    def test_distinguishing_lying_day_fake_names_stored(self):
        text = second_checkpoint_text(
            "run-b5-u2-d1", "day-3", LyingStr("day-3", "day-FAKE"))
        self.assertIn("day day-3", text)
        self.assertNotIn("day-FAKE", text)

    def test_distinguishing_raising_day_names_stored(self):
        text = second_checkpoint_text(
            "run-b5-u2-d2", "day-3", RaisingStr("day-3"))
        self.assertIn("day day-3", text)

    def test_control_plain_text_day_named(self):
        text = second_checkpoint_text(
            "run-b5-u2-c1", "day-3", "day-3")
        self.assertIn("day day-3", text)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)

    def test_control_plain_int_day_named(self):
        text = second_checkpoint_text("run-b5-u2-c2", 3, 3)
        self.assertIn("day 3", text)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)


if __name__ == "__main__":
    unittest.main()

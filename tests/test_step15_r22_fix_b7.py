"""Pins for fix wave 22, composition repair builder b7: the
plain number form inside _vocabulary_text in crucible/mod10.py,
on the ruling at step record Entry 214.

The composed defect: builder b5 reroutes the two MOD-10 day
limbs (retain_daily_aggregate_deliveries and retain_checkpoint)
through _vocabulary_text, and builder b4 cure under Ruling A
renders a non text value through _stored_text, so a plain
number day renders as the empty text at both limbs. The repair
renders a plain number, as _plain_number reads it, as that
plain number own text inside _vocabulary_text, while text and
buffer forms and every other non text form stand rendered
through _stored_text exactly as b4 cured them.

Distinguishing pins fail on the merged standing and pass on
the cured copy. Control pins pass on both standings, and the
two guard controls among them guard the b4 cure at one of its
vocabulary loci against regression.
"""
import unittest
from decimal import Decimal

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


class LyingInt(int):
    """An integer value storing one number whose string and
    repr readings both answer a lying text."""

    def __new__(cls, stored, lie):
        obj = int.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie

    def __repr__(self):
        return self._lie


class PlainReading:
    """A plain object carrying no text form in any form, whose
    string reading alone answers the stated name."""

    def __init__(self, reading):
        self._reading = reading

    def __str__(self):
        return self._reading


def bad_delivery(day):
    return {
        "simulated_day": day,
        "viewer_id": "viewer-1",
        "joint_outcome_components": ["text", 2.0],
        "component_denominators": [1.0, 1.0],
    }


def aggregate_refusal_text(run_id, day):
    try:
        mod10.retain_daily_aggregate_deliveries(
            run_id, [bad_delivery(day)])
    except ValueError as error:
        return str(error)
    return ""


def second_checkpoint_text(run_id, first_day, second_day):
    mod10.retain_checkpoint(
        {"run_identifier": run_id, "simulated_day": first_day})
    try:
        mod10.retain_checkpoint(
            {"run_identifier": run_id,
             "simulated_day": second_day})
    except ValueError as error:
        return str(error)
    return ""


class TestAggregateDayPlainNumber(unittest.TestCase):

    def test_distinguishing_plain_int_day_renders_digits(self):
        text = aggregate_refusal_text("r22-b7-a-d1", 7)
        self.assertIn("at day 7", text)
        self.assertIn("non numeric form", text)

    def test_distinguishing_lying_int_day_renders_plain_digits(self):
        text = aggregate_refusal_text(
            "r22-b7-a-d2", LyingInt(7, "999"))
        self.assertIn("at day 7", text)
        self.assertNotIn("999", text)

    def test_distinguishing_plain_float_day_renders_its_text(self):
        text = aggregate_refusal_text("r22-b7-a-d3", 7.5)
        self.assertIn("at day 7.5", text)
        self.assertIn("non numeric form", text)

    def test_control_plain_text_day_named(self):
        text = aggregate_refusal_text("r22-b7-a-c1", "day-3")
        self.assertIn("at day day-3", text)
        self.assertIn("non numeric form", text)


class TestCheckpointDayPlainNumber(unittest.TestCase):

    def test_distinguishing_plain_int_day_renders_digits(self):
        text = second_checkpoint_text("run-b7-k-d1", 3, 3)
        self.assertIn("day 3", text)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)

    def test_distinguishing_lying_int_day_renders_plain_digits(self):
        text = second_checkpoint_text(
            "run-b7-k-d2", LyingInt(3, "999"), LyingInt(3, "999"))
        self.assertIn("day 3", text)
        self.assertNotIn("999", text)

    def test_distinguishing_plain_decimal_day_renders_its_text(self):
        text = second_checkpoint_text(
            "run-b7-k-d3", Decimal(3), Decimal(3))
        self.assertIn("day 3", text)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)

    def test_control_plain_text_day_named(self):
        text = second_checkpoint_text(
            "run-b7-k-c1", "day-3", "day-3")
        self.assertIn("day day-3", text)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)


class TestVocabularyGuards(unittest.TestCase):

    def test_guard_plain_object_at_store_lookup_renders_empty(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k", store_kind=PlainReading("sweep"))
        message = str(ctx.exception)
        self.assertIn("unknown store kind: ;", message)
        self.assertNotIn("unknown store kind: sweep", message)

    def test_guard_lying_text_at_store_lookup_renders_stored(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k",
                store_kind=LyingStr("bogus-kind", "sweep"))
        self.assertIn(
            "unknown store kind: bogus-kind;", str(ctx.exception))

    def test_control_helper_plain_text_vocabulary_form(self):
        self.assertEqual(mod10._vocabulary_text("sweep"), "sweep")
        self.assertEqual(
            mod10._vocabulary_text(LyingStr("run-x", "run-y")),
            "run-x")
        self.assertEqual(mod10._vocabulary_text(b"bogus"), "bogus")


if __name__ == "__main__":
    unittest.main()

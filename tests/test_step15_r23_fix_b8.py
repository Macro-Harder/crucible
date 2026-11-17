"""Pins for fix wave 23, builder b8, Group 8: the plain integer
beyond the interpreter integer string conversion limit at the
plain number rendering of _vocabulary_text in crucible/mod10.py,
row R23-012 of the Round 23 register, on Ruling 9, from Red 4
finding R23-RED4-04.

The defect: _vocabulary_text renders a plain number as
str(plain), and a plain integer past the conversion limit (4300
digits on this interpreter) raises bare ValueError carrying the
limit sentence alone, so the refusal or failure sentence of the
consuming act stands never delivered. The cure renders the
plain integer beyond the limit in its plain form at that
rendering, at _vocabulary_text alone.

Distinguishing pins fail at the pristine pole and pass at the
cured pole. Control pins pass at both poles.
"""
import sys
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod10

LIMIT = sys.get_int_max_str_digits()
BIG = 10 ** 5000
BIG_DIGITS = "1" + "0" * 5000
MIXED = 10 ** 5000 + 10 ** 2500 + 7
MIXED_DIGITS = "1" + "0" * 2499 + "1" + "0" * 2499 + "7"
TAIL = 10 ** 5000 + 12345
TAIL_DIGITS = "1" + "0" * 4995 + "12345"


class BigLyingInt(int):
    """An integer storing the beyond limit value whose string
    and repr readings answer a lying text."""

    def __new__(cls, stored):
        return int.__new__(cls, stored)

    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


def view_record(run_id, item, seen_day):
    return {
        "run_identifier": run_id,
        "viewer_identifier": "viewer-1",
        "simulated_day": 5,
        "scheduling_position_identifier": "s",
        "rule_version_set": "r",
        "view_contents": {},
        "reputation_and_band_values": {},
        "graph_position_as_seen": {},
        "first_seen_day_per_record": {item: seen_day},
        "delay_applied_per_record": {},
        "completeness_state": "complete",
        "building_component": "c",
        "delivering_contract": "d",
        "selection_rule_version": "v",
    }


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


def second_checkpoint_text(run_id, day):
    mod10.retain_checkpoint(
        {"run_identifier": run_id, "simulated_day": day})
    try:
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": day})
    except ValueError as error:
        return str(error)
    return ""


def view_failure_text(run_id, item, seen_day):
    try:
        mod10.run_view_leak_check(view_record(run_id, item, seen_day))
    except ValueError as error:
        return str(error)
    return ""


class TestBeyondLimitHelper(unittest.TestCase):

    def test_distinguishing_beyond_limit_int_renders_plain_digits(self):
        self.assertGreater(len(BIG_DIGITS), LIMIT)
        self.assertEqual(mod10._vocabulary_text(BIG), BIG_DIGITS)

    def test_distinguishing_beyond_limit_negative_int_renders(self):
        self.assertEqual(
            mod10._vocabulary_text(-BIG), "-" + BIG_DIGITS)

    def test_distinguishing_beyond_limit_mixed_digits_render(self):
        self.assertEqual(mod10._vocabulary_text(MIXED), MIXED_DIGITS)
        self.assertEqual(mod10._vocabulary_text(TAIL), TAIL_DIGITS)

    def test_distinguishing_lying_int_subclass_beyond_limit(self):
        text = mod10._vocabulary_text(BigLyingInt(BIG))
        self.assertEqual(text, BIG_DIGITS)
        self.assertNotIn("999", text.replace("0", ""))


class TestBeyondLimitConsumingLoci(unittest.TestCase):

    def test_distinguishing_view_item_after_sentence_delivered(self):
        text = view_failure_text("r23-b8-v1", BIG, 9)
        self.assertIn(
            "record " + BIG_DIGITS + " first seen after the view day",
            text)
        self.assertNotIn("Exceeds the limit", text)

    def test_distinguishing_view_item_nonfinite_sentence_delivered(self):
        text = view_failure_text("r23-b8-v2", BIG, float("inf"))
        self.assertIn(
            "record " + BIG_DIGITS + " states a day in a non finite "
            "form", text)
        self.assertNotIn("Exceeds the limit", text)

    def test_distinguishing_aggregate_day_refusal_delivered(self):
        text = aggregate_refusal_text("r23-b8-a1", BIG)
        self.assertIn("at day " + BIG_DIGITS, text)
        self.assertIn("non numeric form", text)
        self.assertNotIn("Exceeds the limit", text)

    def test_distinguishing_checkpoint_day_refusal_delivered(self):
        text = second_checkpoint_text("r23-b8-c1", BIG)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)
        self.assertIn("day " + BIG_DIGITS, text)
        self.assertNotIn("Exceeds the limit", text)


class TestControls(unittest.TestCase):

    def test_control_within_limit_ints_render_as_before(self):
        self.assertEqual(mod10._vocabulary_text(7), "7")
        self.assertEqual(mod10._vocabulary_text(0), "0")
        self.assertEqual(mod10._vocabulary_text(-42), "-42")
        self.assertEqual(
            mod10._vocabulary_text(10 ** 100), "1" + "0" * 100)

    def test_control_at_limit_int_renders_as_before(self):
        at_limit = "1" + "0" * (LIMIT - 1)
        self.assertEqual(len(at_limit), LIMIT)
        self.assertEqual(mod10._vocabulary_text(10 ** (LIMIT - 1)),
                         at_limit)

    def test_control_float_forms_render_as_before(self):
        self.assertEqual(mod10._vocabulary_text(7.5), "7.5")
        self.assertEqual(mod10._vocabulary_text(float("inf")), "inf")
        self.assertEqual(mod10._vocabulary_text(float("nan")), "nan")

    def test_control_other_plain_numbers_render_as_before(self):
        self.assertEqual(mod10._vocabulary_text(Decimal("3.5")), "3.5")
        self.assertEqual(mod10._vocabulary_text(Fraction(7, 2)), "7/2")
        self.assertEqual(mod10._vocabulary_text(1 + 2j), "(1+2j)")
        self.assertEqual(mod10._vocabulary_text(True), "1")

    def test_control_text_and_plain_object_render_as_before(self):
        self.assertEqual(mod10._vocabulary_text("day-3"), "day-3")
        self.assertEqual(mod10._vocabulary_text(object()), "")

    def test_control_aggregate_day_within_limit(self):
        text = aggregate_refusal_text("r23-b8-a2", 7)
        self.assertIn("at day 7", text)
        self.assertIn("non numeric form", text)

    def test_control_checkpoint_day_within_limit(self):
        text = second_checkpoint_text("r23-b8-c2", 3)
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            text)
        self.assertIn("day 3", text)

    def test_control_view_item_within_limit(self):
        text = view_failure_text("r23-b8-v3", "rec-1", 9)
        self.assertIn(
            "record rec-1 first seen after the view day", text)


if __name__ == "__main__":
    unittest.main()

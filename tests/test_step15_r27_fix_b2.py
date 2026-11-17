"""Pins for row R27-002, fix wave 27 builder b2.

Locus: crucible/mod10.py _timing_day, Decimal branch.
Distinguishing pins: a Decimal signaling NaN day, in plain,
signed, and payload dresses, delivers float NaN at the helper,
the same delivery a quiet Decimal NaN draws, instead of
escaping bare ValueError, and at the public run_view_leak_check
surface it draws the named timing failure in the same form a
quiet Decimal NaN draws, instead of the bare escape.
Control pins: forms standing as before at both poles.
"""
import math
import sys
import unittest
from decimal import Decimal

from crucible import mod10
from crucible.mod10 import (
    _day_match_form,
    _day_sort_key,
    _retention_day_key,
    _same_day_form,
    _timing_day,
    _whole_day,
)

NAMED_TIMING = (
    "view leak check failure: form timing, view "
    "run-r27-b2/viewer-1, field first_seen_day_per_record: "
    "record item states a day in a non finite form the "
    "timing comparison cannot order")
BARE = "cannot convert signaling NaN to float"


def view_record(day, seen_day):
    return {
        "run_identifier": "run-r27-b2",
        "viewer_identifier": "viewer-1",
        "simulated_day": day,
        "scheduling_position_identifier": "position-1",
        "rule_version_set": "rule-set-1",
        "view_contents": [{"item": "ordinary content"}],
        "reputation_and_band_values": {"band": "stated"},
        "graph_position_as_seen": "stated",
        "first_seen_day_per_record": {"item": seen_day},
        "delay_applied_per_record": {"item": 1},
        "completeness_state": "complete",
        "building_component": "Recorder",
        "delivering_contract": "stated",
        "selection_rule_version": "rule-set-1",
    }


class TimingDayDecimalSignalingTests(unittest.TestCase):

    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), 4300)

    # Distinguishing pins, 6 methods.

    def test_helper_plain_signaling_nan_returns_float_nan(self):
        result = _timing_day(Decimal("sNaN"))
        self.assertIsInstance(result, float)
        self.assertTrue(math.isnan(result))

    def test_helper_signed_signaling_nan_returns_float_nan(self):
        for dress in ("-sNaN", "+sNaN"):
            result = _timing_day(Decimal(dress))
            self.assertIsInstance(result, float)
            self.assertTrue(math.isnan(result))

    def test_helper_payload_signaling_nan_returns_float_nan(self):
        for dress in ("sNaN123", "-sNaN42", "sNaN5000"):
            result = _timing_day(Decimal(dress))
            self.assertIsInstance(result, float)
            self.assertTrue(math.isnan(result))

    def test_public_signaling_nan_at_view_day_draws_named_timing(self):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(view_record(Decimal("sNaN"), 3))
        self.assertEqual(str(caught.exception), NAMED_TIMING)
        self.assertNotIn(BARE, str(caught.exception))

    def test_public_signaling_nan_at_first_seen_draws_named_timing(self):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(view_record(5, Decimal("sNaN")))
        self.assertEqual(str(caught.exception), NAMED_TIMING)
        self.assertNotIn(BARE, str(caught.exception))

    def test_public_signed_and_payload_signaling_nan_draw_named(self):
        for day, seen in (
                (Decimal("-sNaN"), 3),
                (Decimal("sNaN123"), 3),
                (5, Decimal("-sNaN")),
                (5, Decimal("sNaN123"))):
            with self.assertRaises(ValueError) as caught:
                mod10.run_view_leak_check(view_record(day, seen))
            self.assertEqual(str(caught.exception), NAMED_TIMING)
            self.assertNotIn(BARE, str(caught.exception))

    # Control pins, 8 methods.

    def test_control_quiet_decimal_nan_helper(self):
        for dress in ("NaN", "-NaN", "+NaN", "NaN123"):
            result = _timing_day(Decimal(dress))
            self.assertIsInstance(result, float)
            self.assertTrue(math.isnan(result))

    def test_control_decimal_infinity_helper(self):
        self.assertEqual(_timing_day(Decimal("Infinity")), math.inf)
        self.assertEqual(_timing_day(Decimal("-Infinity")), -math.inf)
        self.assertEqual(_timing_day(Decimal("+Infinity")), math.inf)

    def test_control_finite_and_huge_integral_decimal_helper(self):
        self.assertEqual(_timing_day(Decimal("3")), 3)
        self.assertIsInstance(_timing_day(Decimal("3")), int)
        self.assertEqual(_timing_day(Decimal("2.5")), 2.5)
        self.assertEqual(_timing_day(Decimal("-7")), -7)
        self.assertEqual(_timing_day(Decimal("1E+5000")), 10 ** 5000)
        result = _timing_day(Decimal("1." + "1" * 5000))
        self.assertIsInstance(result, float)
        self.assertTrue(math.isfinite(result))

    def test_control_float_nan_ruled_form(self):
        result = _timing_day(float("nan"))
        self.assertIsInstance(result, float)
        self.assertTrue(math.isnan(result))
        self.assertEqual(_timing_day(math.inf), math.inf)
        self.assertEqual(_timing_day(2.5), 2.5)

    def test_control_sibling_branches_untouched(self):
        self.assertEqual(_timing_day("0x1p5000"), "0x1p5000")
        self.assertEqual(_timing_day("0x1p10"), 1024.0)
        self.assertEqual(_timing_day("1e5000"), math.inf)
        self.assertEqual(_timing_day("-1e5000"), -math.inf)
        self.assertEqual(_timing_day("1_0e3"), 10000.0)
        text = "9" * 400 + ".5"
        self.assertEqual(_timing_day(text), text)
        self.assertEqual(_timing_day("42"), 42)
        self.assertEqual(_timing_day("1.5"), 1.5)

    def test_control_companion_day_helpers_signaling_nan(self):
        handed = Decimal("sNaN")
        self.assertIs(_whole_day(handed), handed)
        self.assertEqual(
            _day_match_form(handed),
            ("other", "Decimal:Decimal('sNaN')"))
        self.assertEqual(
            _retention_day_key(handed), "other:Decimal:Decimal('sNaN')")
        self.assertTrue(_same_day_form(handed, Decimal("sNaN")))
        self.assertEqual(
            _day_sort_key((handed, "viewer-1")),
            (1, 0, "", "Decimal:Decimal('sNaN')",
             "viewer-1", "str:8:viewer-1"))

    def test_control_public_quiet_nan_and_infinity_named_timing(self):
        for day, seen in (
                (Decimal("NaN"), 3),
                (5, Decimal("NaN")),
                (Decimal("Infinity"), 3),
                (5, Decimal("-Infinity"))):
            with self.assertRaises(ValueError) as caught:
                mod10.run_view_leak_check(view_record(day, seen))
            self.assertEqual(str(caught.exception), NAMED_TIMING)

    def test_control_public_clean_record_and_limit(self):
        result = mod10.run_view_leak_check(view_record(5, 3))
        self.assertTrue(result["reportable"])
        self.assertEqual(
            result["forms_run"], ["canary", "field_validation", "timing"])
        self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()

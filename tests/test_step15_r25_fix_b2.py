"""Pins for fix wave 25 builder b2: row R25-002.

Copyright: J.P. Picard aka Macro-Harder.
"""
import sys
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod10

BIG = 10 ** 5000
DIGITS = "1" + "0" * 5000
LIMIT = 4300


def delivery(day, viewer="viewer-1"):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 1,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 1},
    }


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


class TestWholeDayBeyond(Base):
    def test_plain_digit_text_beyond(self):
        self.assertEqual(mod10._whole_day(DIGITS), BIG)

    def test_signed_plus_digit_text_beyond(self):
        self.assertEqual(mod10._whole_day("+" + DIGITS), BIG)

    def test_signed_minus_digit_text_beyond(self):
        self.assertEqual(mod10._whole_day("-" + DIGITS), -BIG)

    def test_spaced_digit_text_beyond(self):
        self.assertEqual(mod10._whole_day("  " + DIGITS + "  "), BIG)

    def test_spaced_signed_digit_text_beyond(self):
        self.assertEqual(mod10._whole_day("  -" + DIGITS + " "), -BIG)


class TestRetentionDayKeyBeyond(Base):
    def test_plain_digit_text_beyond(self):
        self.assertEqual(mod10._retention_day_key(DIGITS), "int:" + DIGITS)

    def test_signed_plus_digit_text_beyond(self):
        self.assertEqual(
            mod10._retention_day_key("+" + DIGITS), "int:" + DIGITS)

    def test_signed_minus_digit_text_beyond(self):
        self.assertEqual(
            mod10._retention_day_key("-" + DIGITS), "int:-" + DIGITS)

    def test_spaced_digit_text_beyond(self):
        self.assertEqual(
            mod10._retention_day_key(" " + DIGITS + " "), "int:" + DIGITS)

    def test_spaced_signed_digit_text_beyond(self):
        self.assertEqual(
            mod10._retention_day_key("  +" + DIGITS + "  "),
            "int:" + DIGITS)


class TestSameDayFormBeyond(Base):
    def test_plain_pair_beyond(self):
        self.assertTrue(mod10._same_day_form(BIG, DIGITS))

    def test_signed_pair_beyond(self):
        self.assertTrue(mod10._same_day_form(BIG, "+" + DIGITS))

    def test_spaced_pair_beyond(self):
        self.assertTrue(mod10._same_day_form(" " + DIGITS + " ", BIG))

    def test_spaced_signed_negative_pair_beyond(self):
        self.assertTrue(mod10._same_day_form(-BIG, "  -" + DIGITS + " "))


class TestPublicRetainBeyond(Base):
    def test_retain_int_and_digit_text_count_one(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "r25-b2-public-1", [delivery(BIG), delivery(DIGITS)])
        self.assertEqual(count, 1)

    def test_retain_int_and_signed_spaced_count_one(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "r25-b2-public-2",
            [delivery(BIG), delivery("  +" + DIGITS + "  ")])
        self.assertEqual(count, 1)


class TestControls(Base):
    def test_within_limit_digit_text_merges(self):
        small = 10 ** 100
        small_digits = "1" + "0" * 100
        self.assertEqual(mod10._whole_day(small_digits), small)
        self.assertEqual(mod10._whole_day(" +" + small_digits + " "), small)
        self.assertTrue(mod10._same_day_form(small, small_digits))
        self.assertEqual(
            mod10._retention_day_key(small_digits), "int:" + small_digits)
        self.assertEqual(mod10._whole_day("7"), 7)
        self.assertTrue(mod10._same_day_form(7, "7"))

    def test_plain_integer_days(self):
        self.assertEqual(mod10._whole_day(BIG), BIG)
        self.assertEqual(mod10._whole_day(7), 7)
        self.assertEqual(mod10._retention_day_key(7), "int:7")
        self.assertTrue(mod10._same_day_form(7, 7))

    def test_non_digit_text_pristine(self):
        self.assertEqual(mod10._whole_day("abc"), "abc")
        self.assertEqual(mod10._whole_day("12a"), "12a")
        self.assertEqual(mod10._whole_day(""), "")
        self.assertEqual(mod10._retention_day_key("abc"), "str:3:abc")
        self.assertEqual(mod10._whole_day("²"), "²")
        self.assertFalse(mod10._same_day_form(7, "abc"))

    def test_r24009_serialisation_controls(self):
        self.assertEqual(mod10._retention_day_key(BIG), "int:" + DIGITS)
        self.assertEqual(mod10._retention_day_key(-BIG), "int:-" + DIGITS)
        self.assertEqual(
            mod10._retention_day_key(Fraction(BIG, 1)), "int:" + DIGITS)
        self.assertEqual(
            mod10._retention_day_key(Decimal("1E+5000")), "int:" + DIGITS)
        self.assertEqual(mod10._retention_day_key(True), "bool:1")
        self.assertEqual(mod10._retention_day_key(2.5), "float:2.5")

    def test_limit_stands_default(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


if __name__ == "__main__":
    unittest.main()

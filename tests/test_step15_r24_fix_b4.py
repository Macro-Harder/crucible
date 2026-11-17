"""Pins for fix wave 24 builder b4: rows R24-005, R24-008, R24-009.

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


class _FractionSubclass(Fraction):
    pass


class TestR24005VocabularyText(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_num_beyond_nonintegral(self):
        self.assertEqual(
            mod10._vocabulary_text(Fraction(BIG, 7)), DIGITS + "/7")

    def test_den_beyond_nonintegral(self):
        self.assertEqual(
            mod10._vocabulary_text(Fraction(3, BIG)), "3/" + DIGITS)

    def test_both_beyond_nonintegral(self):
        den_digits = "1" + "0" * 4999 + "1"
        self.assertEqual(
            mod10._vocabulary_text(Fraction(BIG, BIG + 1)),
            DIGITS + "/" + den_digits)

    def test_denom_one_beyond(self):
        self.assertEqual(mod10._vocabulary_text(Fraction(BIG, 1)), DIGITS)

    def test_negative_num_beyond(self):
        self.assertEqual(
            mod10._vocabulary_text(Fraction(-BIG, 7)), "-" + DIGITS + "/7")

    def test_subclass_beyond(self):
        self.assertEqual(
            mod10._vocabulary_text(_FractionSubclass(BIG, 3)),
            DIGITS + "/3")


class TestR24008DayMatchForm(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_num_beyond(self):
        self.assertEqual(
            mod10._day_match_form(Fraction(BIG, 7)),
            ("other", "Fraction:Fraction(" + DIGITS + ", 7)"))

    def test_den_beyond(self):
        self.assertEqual(
            mod10._day_match_form(Fraction(3, BIG)),
            ("other", "Fraction:Fraction(3, " + DIGITS + ")"))

    def test_both_beyond(self):
        den_digits = "1" + "0" * 4999 + "1"
        self.assertEqual(
            mod10._day_match_form(Fraction(BIG, BIG + 1)),
            ("other", "Fraction:Fraction(" + DIGITS + ", "
             + den_digits + ")"))

    def test_negative_beyond(self):
        self.assertEqual(
            mod10._day_match_form(Fraction(-BIG, 3)),
            ("other", "Fraction:Fraction(-" + DIGITS + ", 3)"))


class TestR24009RetentionDayKey(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_plain_int_beyond(self):
        self.assertEqual(mod10._retention_day_key(BIG), "int:" + DIGITS)

    def test_integral_fraction_beyond(self):
        self.assertEqual(
            mod10._retention_day_key(Fraction(BIG, 1)), "int:" + DIGITS)

    def test_negative_int_beyond(self):
        self.assertEqual(
            mod10._retention_day_key(-BIG), "int:-" + DIGITS)

    def test_integral_decimal_beyond(self):
        self.assertEqual(
            mod10._retention_day_key(Decimal("1E+5000")), "int:" + DIGITS)


class TestControls(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_vocabulary_controls(self):
        self.assertEqual(mod10._vocabulary_text(Fraction(7, 2)), "7/2")
        self.assertEqual(mod10._vocabulary_text(Fraction(7, 1)), "7")
        self.assertEqual(mod10._vocabulary_text(Fraction(-7, 2)), "-7/2")
        self.assertEqual(mod10._vocabulary_text(7), "7")
        self.assertEqual(mod10._vocabulary_text(BIG), DIGITS)
        self.assertEqual(mod10._vocabulary_text("plain"), "plain")
        self.assertEqual(
            mod10._vocabulary_text(Decimal("1E+5000")), "1E+5000")

    def test_day_match_controls(self):
        self.assertEqual(
            mod10._day_match_form(Fraction(3, 2)),
            ("other", "Fraction:Fraction(3, 2)"))
        self.assertEqual(mod10._day_match_form(Fraction(6, 2)), ("int", 3))
        self.assertEqual(mod10._day_match_form(5), ("int", 5))
        self.assertEqual(mod10._day_match_form("5"), ("int", 5))
        self.assertEqual(mod10._day_match_form(2.5), ("float", 2.5))

    def test_retention_controls(self):
        self.assertEqual(mod10._retention_day_key(5), "int:5")
        self.assertEqual(mod10._retention_day_key(Fraction(5, 1)), "int:5")
        self.assertEqual(
            mod10._retention_day_key(Fraction(3, 2)),
            "other:Fraction:Fraction(3, 2)")
        self.assertEqual(mod10._retention_day_key(2.5), "float:2.5")
        self.assertEqual(mod10._retention_day_key("abc"), "str:3:abc")
        self.assertEqual(mod10._retention_day_key(True), "bool:1")

    def test_limit_stands_default(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


if __name__ == "__main__":
    unittest.main()

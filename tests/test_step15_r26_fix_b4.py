"""Pins for row R26-004, fix wave 26 builder b4.

Locus: crucible/mod10.py _timing_day, base prefixed branch.
Distinguishing pins: a hexadecimal float spelling beyond float
range delivers the handed value itself, in the form the branch
states for a conversion it cannot take and the plain decimal
branch states for a non finite conversion, instead of escaping
bare OverflowError.
Control pins: forms standing as before at both poles.
"""
import math
import sys
import unittest

from crucible.mod10 import _timing_day


class TimingDayBasePrefixedTests(unittest.TestCase):

    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), 4300)

    # Distinguishing pins, 6 methods.

    def test_beyond_range_hex_float_plain_returns_value_itself(self):
        self.assertEqual(_timing_day("0x1p5000"), "0x1p5000")

    def test_beyond_range_hex_float_short_returns_value_itself(self):
        self.assertEqual(_timing_day("0x1p2000"), "0x1p2000")

    def test_beyond_range_hex_float_signed_returns_value_itself(self):
        self.assertEqual(_timing_day("-0x1p5000"), "-0x1p5000")
        self.assertEqual(_timing_day("+0x1p5000"), "+0x1p5000")

    def test_beyond_range_hex_float_negative_short_returns_itself(self):
        self.assertEqual(_timing_day("-0x1p2000"), "-0x1p2000")

    def test_beyond_range_hex_float_upper_and_fraction_return_itself(self):
        self.assertEqual(_timing_day("0X1P5000"), "0X1P5000")
        self.assertEqual(_timing_day("0x1.8p5000"), "0x1.8p5000")

    def test_beyond_range_hex_float_spaced_returns_value_itself(self):
        self.assertEqual(_timing_day(" 0x1p5000 "), " 0x1p5000 ")

    # Control pins, 8 methods.

    def test_within_range_hex_float_controls(self):
        self.assertEqual(_timing_day("0x1p100"), float.fromhex("0x1p100"))
        self.assertEqual(_timing_day("0x1p10"), 1024.0)
        self.assertEqual(_timing_day("0x1.8p1"), 3.0)
        self.assertEqual(_timing_day("0x1p-5000"), 0.0)
        self.assertEqual(_timing_day("-0x1p10"), -1024.0)

    def test_prefixed_integer_controls(self):
        self.assertEqual(_timing_day("0x10"), 16)
        self.assertEqual(_timing_day("0b101"), 5)
        self.assertEqual(_timing_day("0o17"), 15)
        self.assertEqual(_timing_day("0x" + "f" * 100), 16 ** 100 - 1)
        self.assertEqual(_timing_day("0o" + "7" * 100), 8 ** 100 - 1)

    def test_sibling_exponent_overflow_control(self):
        self.assertEqual(_timing_day("1e5000"), math.inf)
        self.assertEqual(_timing_day("-1e5000"), -math.inf)

    def test_plain_decimal_nonfinite_control(self):
        text = "9" * 400 + ".5"
        self.assertEqual(_timing_day(text), text)

    def test_decimal_exponent_underscore_controls(self):
        self.assertEqual(_timing_day("1.5"), 1.5)
        self.assertEqual(_timing_day("1e3"), 1000.0)
        self.assertEqual(_timing_day("1_000"), 1000.0)
        self.assertEqual(_timing_day("42"), 42)
        self.assertEqual(_timing_day("-7"), -7)

    def test_beyond_limit_digit_text_through_whole_day_control(self):
        self.assertEqual(_timing_day("1" + "0" * 5000), 10 ** 5000)
        self.assertEqual(_timing_day("-1" + "0" * 5000), -(10 ** 5000))

    def test_invalid_and_plain_form_controls(self):
        self.assertEqual(_timing_day("0xZZ"), "0xZZ")
        self.assertEqual(_timing_day("0b102"), "0b102")
        self.assertEqual(_timing_day("hello"), "hello")
        self.assertEqual(_timing_day(""), "")
        self.assertEqual(_timing_day("inf"), math.inf)
        self.assertEqual(_timing_day("-infinity"), -math.inf)
        self.assertTrue(math.isnan(_timing_day("nan")))

    def test_interpreter_limit_control(self):
        self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()

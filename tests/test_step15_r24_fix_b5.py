"""Pins for fix wave 24, builder b5: the beyond limit handings
at crucible/mod10.py _stored_form (row R24-006) and _stored_repr
(row R24-007) of the Round 24 register.

The defect: _stored_form builds its int form as
str(int.__int__(value)) and its plain number form as the type
name beside repr(plain), each unguarded, and _stored_repr builds
its rendering as repr(int.__int__(value)) at its int limb and
repr(plain) at its plain number limb, each unguarded, so a
handed value standing beyond the interpreter integer string
conversion limit (4300 digits on this interpreter) escapes bare
ValueError at those limbs and no form or rendering stands
delivered. The cure delivers the form and the rendering in
their stated forms at those limbs, with no bare escape and no
interpreter limit setting changed.

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


class BigLyingInt(int):
    """An integer storing the beyond limit value whose string
    and repr readings answer a lying text."""

    def __new__(cls, stored):
        return int.__new__(cls, stored)

    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


class TestStoredFormBeyondLimit(unittest.TestCase):

    def test_distinguishing_beyond_limit_int_form(self):
        self.assertGreater(len(BIG_DIGITS), LIMIT)
        self.assertEqual(mod10._stored_form(BIG), "int:" + BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_negative_int_form(self):
        self.assertEqual(
            mod10._stored_form(-BIG), "int:-" + BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_mixed_digits_form(self):
        self.assertEqual(
            mod10._stored_form(MIXED), "int:" + MIXED_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_lying_int_subclass_beyond_limit_form(self):
        self.assertEqual(
            mod10._stored_form(BigLyingInt(BIG)), "int:" + BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_fraction_form(self):
        self.assertEqual(
            mod10._stored_form(Fraction(BIG, 7)),
            "Fraction:Fraction(" + BIG_DIGITS + ", 7)")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_fraction_denominator_form(self):
        self.assertEqual(
            mod10._stored_form(Fraction(7, BIG)),
            "Fraction:Fraction(7, " + BIG_DIGITS + ")")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_negative_fraction_form(self):
        self.assertEqual(
            mod10._stored_form(Fraction(-BIG, 3)),
            "Fraction:Fraction(-" + BIG_DIGITS + ", 3)")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


class TestStoredReprBeyondLimit(unittest.TestCase):

    def test_distinguishing_beyond_limit_int_repr(self):
        self.assertEqual(mod10._stored_repr(BIG), BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_negative_int_repr(self):
        self.assertEqual(mod10._stored_repr(-BIG), "-" + BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_lying_int_subclass_beyond_limit_repr(self):
        self.assertEqual(
            mod10._stored_repr(BigLyingInt(BIG)), BIG_DIGITS)
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_fraction_repr(self):
        self.assertEqual(
            mod10._stored_repr(Fraction(BIG, 3)),
            "Fraction(" + BIG_DIGITS + ", 3)")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_fraction_denominator_repr(self):
        self.assertEqual(
            mod10._stored_repr(Fraction(7, BIG)),
            "Fraction(7, " + BIG_DIGITS + ")")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)

    def test_distinguishing_beyond_limit_int_inside_list_repr(self):
        self.assertEqual(
            mod10._stored_repr([BIG]), "[" + BIG_DIGITS + "]")
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


class TestPlainControls(unittest.TestCase):

    def test_control_ordinary_int_both_helpers(self):
        self.assertEqual(mod10._stored_form(7), "int:7")
        self.assertEqual(mod10._stored_repr(7), "7")
        self.assertEqual(mod10._stored_form(-42), "int:-42")
        self.assertEqual(mod10._stored_repr(-42), "-42")

    def test_control_ordinary_fraction_both_helpers(self):
        self.assertEqual(
            mod10._stored_form(Fraction(3, 2)), "Fraction:Fraction(3, 2)")
        self.assertEqual(
            mod10._stored_repr(Fraction(3, 2)), "Fraction(3, 2)")

    def test_control_ordinary_decimal_both_helpers(self):
        self.assertEqual(
            mod10._stored_form(Decimal("3.5")), "Decimal:Decimal('3.5')")
        self.assertEqual(
            mod10._stored_repr(Decimal("3.5")), "Decimal('3.5')")

    def test_control_beyond_limit_decimal_both_helpers(self):
        form = mod10._stored_form(Decimal(BIG))
        self.assertTrue(form.startswith("Decimal:Decimal('1"))
        self.assertEqual(len(form), len("Decimal:") + 5012)
        rendered = mod10._stored_repr(Decimal(BIG))
        self.assertTrue(rendered.startswith("Decimal('1"))
        self.assertEqual(len(rendered), 5012)

    def test_control_other_ordinary_forms(self):
        self.assertEqual(mod10._stored_form(True), "bool:1")
        self.assertEqual(mod10._stored_form("ab"), "str:2:ab")
        self.assertEqual(mod10._stored_repr("x"), "'x'")
        self.assertEqual(mod10._stored_repr(None), "None")
        self.assertEqual(mod10._stored_repr(2.5), "2.5")
        self.assertEqual(mod10._stored_form(2.5), "float:2.5")

    def test_control_limit_standing_at_default(self):
        self.assertEqual(LIMIT, 4300)
        self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()

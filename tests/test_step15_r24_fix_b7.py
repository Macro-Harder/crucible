"""Step 15, second run, fix wave 24, Builder b7 pins.

Row R24-011: crucible/mod11.py _form_repr, at its scalar limbs,
the integer limb and the Fraction limb, MOD-11. The helper builds
its plain scalar forms unguarded at those limbs, so a handed
value standing beyond the interpreter integer string conversion
limit escapes bare there.

Pins whose names carry control stand as the controls, passing
on the pristine tree and on the cured tree alike. Every other
pin stands distinguishing, failing or erroring on the pristine
tree and passing on the cured tree.
"""

import sys
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod11

BIG = 10 ** 5000
BIG_TEXT = "1" + "0" * 5000
MIXED = 10 ** 5000 + 10 ** 2500 + 7
MIXED_TEXT = "1" + "0" * 2499 + "1" + "0" * 2499 + "7"
BIG_FRACTION_TEXT = "Fraction(" + BIG_TEXT + ", 3)"


class BigInt(int):
    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


def make_evil(kind_name, exc):
    cls = type(kind_name, (), {
        "__repr__": lambda self: "5",
        "__dict__": property(
            lambda self: (_ for _ in ()).throw(exc)),
    })
    return object.__new__(cls)


class Holder:
    pass


class LimitGuard(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), 4300)


class TestR24011IntLimb(LimitGuard):
    def test_direct_beyond_limit_int(self):
        self.assertEqual(mod11._form_repr(BIG), BIG_TEXT)

    def test_direct_beyond_limit_negative_int(self):
        self.assertEqual(mod11._form_repr(-BIG), "-" + BIG_TEXT)

    def test_direct_beyond_limit_mixed_int(self):
        self.assertEqual(mod11._form_repr(MIXED), MIXED_TEXT)

    def test_direct_beyond_limit_int_subclass_lying_readings(self):
        self.assertEqual(mod11._form_repr(BigInt(BIG)), BIG_TEXT)


class TestR24011FractionLimb(LimitGuard):
    def test_direct_beyond_limit_fraction_numerator(self):
        self.assertEqual(
            mod11._form_repr(Fraction(BIG, 3)), BIG_FRACTION_TEXT)

    def test_direct_beyond_limit_fraction_denominator(self):
        self.assertEqual(
            mod11._form_repr(Fraction(3, BIG)),
            "Fraction(3, " + BIG_TEXT + ")")

    def test_direct_beyond_limit_fraction_negative(self):
        self.assertEqual(
            mod11._form_repr(Fraction(-BIG, 3)),
            "Fraction(-" + BIG_TEXT + ", 3)")


class TestR24011Nested(LimitGuard):
    def test_nested_list_beyond_limit_int(self):
        self.assertEqual(
            mod11._form_repr([BIG]), "[" + BIG_TEXT + "]")

    def test_nested_tuple_beyond_limit_fraction(self):
        self.assertEqual(
            mod11._form_repr((Fraction(BIG, 3),)),
            "(" + BIG_FRACTION_TEXT + ",)")

    def test_nested_dict_value_beyond_limit_fraction(self):
        self.assertEqual(
            mod11._form_repr({"k": Fraction(BIG, 3)}),
            "{'k': " + BIG_FRACTION_TEXT + "}")

    def test_nested_vars_holder_beyond_limit_int(self):
        holder = Holder()
        holder.x = BIG
        self.assertEqual(
            mod11._form_repr(holder), "Holder(x=" + BIG_TEXT + ")")


class TestR24011Controls(LimitGuard):
    def test_control_plain_int(self):
        self.assertEqual(mod11._form_repr(7), "7")

    def test_control_plain_negative_and_zero_int(self):
        self.assertEqual(mod11._form_repr(-42), "-42")
        self.assertEqual(mod11._form_repr(0), "0")

    def test_control_int_at_limit(self):
        self.assertEqual(
            mod11._form_repr(10 ** 4299), "1" + "0" * 4299)

    def test_control_plain_fraction(self):
        self.assertEqual(
            mod11._form_repr(Fraction(7, 2)), "Fraction(7, 2)")

    def test_control_plain_whole_fraction(self):
        self.assertEqual(
            mod11._form_repr(Fraction(7, 1)), "Fraction(7, 1)")

    def test_control_other_scalars(self):
        self.assertEqual(mod11._form_repr(True), "True")
        self.assertEqual(mod11._form_repr(7.5), "7.5")
        self.assertEqual(mod11._form_repr("abc"), "'abc'")
        self.assertEqual(mod11._form_repr(None), "None")
        self.assertEqual(
            mod11._form_repr(Decimal("3.5")), "Decimal('3.5')")
        self.assertEqual(mod11._form_repr(1 + 2j), "(1+2j)")

    def test_control_vars_dress_runtime_by_kind_name(self):
        evil = make_evil(
            "EvilVarsRuntime",
            RuntimeError("stored mapping raises RuntimeError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsRuntime")

    def test_control_vars_dress_index_by_kind_name(self):
        evil = make_evil(
            "EvilVarsIndex",
            IndexError("stored mapping raises IndexError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsIndex")

    def test_control_plain_holder(self):
        holder = Holder()
        holder.plain = "abc"
        holder.num = 3
        self.assertEqual(
            mod11._form_repr(holder), "Holder(num=3, plain='abc')")

    def test_control_limit_stands_default(self):
        self.assertEqual(sys.get_int_max_str_digits(), 4300)
        mod11._form_repr(7)
        self.assertEqual(sys.get_int_max_str_digits(), 4300)


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 24, builder b6, row R24-010: the MOD-09
sibling repr helpers _stored_form_repr and _catalogue_repr in
crucible/mod09.py, at their integer limbs.

The defect: both helpers build their integer form unguarded as
repr(int.__int__(value)), _stored_form_repr standing on its
delegation to _catalogue_repr, so a handed value standing
beyond the interpreter integer string conversion limit escapes
bare ValueError carrying the limit sentence alone, and no
sentence the helpers stand behind stands delivered.

Distinguishing pins fail at the pristine pole and pass at the
cured pole. Control pins pass at both poles, among them the
raising kinds of the wave 23 cure at _catalogue_repr still
rendering by kind name, and the interpreter limit standing at
its default after every act. No pin changes the interpreter
limit, and no pin runs a link behaviour test.
"""
import sys
import unittest

from crucible import mod09

DEFAULT_LIMIT = sys.get_int_max_str_digits()
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


def make_evil(class_name, exc):
    """Build a handed class whose __dict__ property raises exc,
    in the wave 23 pin construction form."""

    def raise_it(self, _exc=exc):
        raise _exc("stored mapping raises")

    return type(class_name, (), {
        "__repr__": lambda self: "5",
        "__dict__": property(raise_it),
    })


EVIL_KINDS = (
    ("EvilRuntime", RuntimeError),
    ("EvilValue", ValueError),
    ("EvilIndex", IndexError),
    ("EvilKeyboardInterrupt", KeyboardInterrupt),
    ("EvilSystemExit", SystemExit),
)
EVIL_CLASSES = {name: make_evil(name, exc) for name, exc in EVIL_KINDS}


class PlainObj:
    """A plain object whose repr reading answers 5."""

    def __repr__(self):
        return "5"


def attempt(act):
    """Run one act, returning (True, value) where it stands
    delivered and (False, kind name) where any kind escapes
    bare, BaseException kinds included."""
    try:
        return (True, act())
    except BaseException as escaped:
        return (False, type(escaped).__name__)


def gate_attempt(act):
    """Run one gate act, returning (True, sentence) where the
    named failure stands delivered and (False, kind name)
    where any other kind escapes bare."""
    try:
        act()
    except mod09.NamedAttackerFailure as failure:
        return (True, str(failure))
    except BaseException as escaped:
        return (False, type(escaped).__name__)
    return (False, "no failure delivered")


class LimitGuard(unittest.TestCase):
    def tearDown(self):
        self.assertEqual(sys.get_int_max_str_digits(), DEFAULT_LIMIT)


class TestDistinguishingDirect(LimitGuard):

    def test_distinguishing_stored_form_repr_beyond_limit(self):
        self.assertGreater(len(BIG_DIGITS), DEFAULT_LIMIT)
        delivered, value = attempt(lambda: mod09._stored_form_repr(BIG))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, BIG_DIGITS)

    def test_distinguishing_catalogue_repr_beyond_limit(self):
        delivered, value = attempt(lambda: mod09._catalogue_repr(BIG))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, BIG_DIGITS)

    def test_distinguishing_stored_form_repr_negative(self):
        delivered, value = attempt(lambda: mod09._stored_form_repr(-BIG))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, "-" + BIG_DIGITS)

    def test_distinguishing_catalogue_repr_negative(self):
        delivered, value = attempt(lambda: mod09._catalogue_repr(-BIG))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, "-" + BIG_DIGITS)

    def test_distinguishing_stored_form_repr_mixed_digits(self):
        delivered, value = attempt(lambda: mod09._stored_form_repr(MIXED))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, MIXED_DIGITS)

    def test_distinguishing_catalogue_repr_tail_digits(self):
        delivered, value = attempt(lambda: mod09._catalogue_repr(TAIL))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, TAIL_DIGITS)

    def test_distinguishing_lying_subclass_stored_form_repr(self):
        delivered, value = attempt(
            lambda: mod09._stored_form_repr(BigLyingInt(BIG)))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, BIG_DIGITS)

    def test_distinguishing_lying_subclass_catalogue_repr(self):
        delivered, value = attempt(
            lambda: mod09._catalogue_repr(BigLyingInt(BIG)))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, BIG_DIGITS)


class TestDistinguishingNestedAndGate(LimitGuard):

    def test_distinguishing_tuple_carrying_beyond_limit(self):
        delivered, value = attempt(lambda: mod09._stored_form_repr((BIG,)))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, "(" + BIG_DIGITS + ",)")

    def test_distinguishing_list_carrying_beyond_limit(self):
        delivered, value = attempt(lambda: mod09._catalogue_repr([BIG]))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, "[" + BIG_DIGITS + "]")

    def test_distinguishing_holder_mapping_beyond_limit(self):
        holder = PlainObj()
        holder.part = BIG
        delivered, value = attempt(lambda: mod09._stored_form_repr(holder))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, "PlainObj(part=" + BIG_DIGITS + ")")

    def test_distinguishing_gate_strategy_beyond_limit(self):
        delivered, value = gate_attempt(
            lambda: mod09.sweep_external_profit(BIG))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn("in no record form: " + BIG_DIGITS, value)
        self.assertNotIn("Exceeds the limit", value)

    def test_distinguishing_gate_tuple_strategy_beyond_limit(self):
        delivered, value = gate_attempt(
            lambda: mod09.sweep_external_profit((BIG,)))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn("in no record form: (" + BIG_DIGITS + ",)", value)
        self.assertNotIn("Exceeds the limit", value)


class TestControls(LimitGuard):

    def test_control_ordinary_ints_render_whole(self):
        for helper in (mod09._stored_form_repr, mod09._catalogue_repr):
            self.assertEqual(helper(5), "5")
            self.assertEqual(helper(0), "0")
            self.assertEqual(helper(-42), "-42")
            self.assertEqual(helper(10 ** 100), "1" + "0" * 100)

    def test_control_at_limit_int_renders_whole(self):
        at_limit = "1" + "0" * (DEFAULT_LIMIT - 1)
        self.assertEqual(len(at_limit), DEFAULT_LIMIT)
        for helper in (mod09._stored_form_repr, mod09._catalogue_repr):
            self.assertEqual(helper(10 ** (DEFAULT_LIMIT - 1)), at_limit)

    def test_control_ordinary_scalars_render_whole(self):
        for helper in (mod09._stored_form_repr, mod09._catalogue_repr):
            self.assertEqual(helper("x"), "'x'")
            self.assertEqual(helper(True), "True")
            self.assertEqual(helper(False), "False")
            self.assertEqual(helper(7.5), "7.5")
            self.assertEqual(helper(1 + 2j), "(1+2j)")
            self.assertEqual(helper(b"ab"), "b'ab'")

    def test_control_ordinary_containers_render_whole(self):
        self.assertEqual(mod09._stored_form_repr([1, 2]), "[1, 2]")
        self.assertEqual(mod09._catalogue_repr((1, 2)), "(1, 2)")
        self.assertEqual(
            mod09._stored_form_repr({"x": 5}), "dict({'x'=5})")
        self.assertEqual(mod09._catalogue_repr({2, 1}), "set({1, 2})")

    def test_control_plain_object_renders_whole(self):
        self.assertEqual(
            mod09._stored_form_repr(object.__new__(PlainObj)),
            "PlainObj()")
        obj = PlainObj()
        obj.marker = "stored-content-xyz"
        self.assertEqual(
            mod09._catalogue_repr(obj),
            "PlainObj(marker='stored-content-xyz')")

    def test_control_gate_plain_strategy_refusal(self):
        delivered, value = gate_attempt(
            lambda: mod09.sweep_external_profit(3))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn("in no record form: 3", value)

    def test_control_limit_stands_default_after_acts(self):
        self.assertEqual(mod09._stored_form_repr(7), "7")
        self.assertEqual(sys.get_int_max_str_digits(), DEFAULT_LIMIT)
        self.assertEqual(mod09._catalogue_repr("x"), "'x'")
        self.assertEqual(sys.get_int_max_str_digits(), DEFAULT_LIMIT)


def _control_evil_pin(name):
    def pin(self):
        handed = object.__new__(EVIL_CLASSES[name])
        self.assertEqual(mod09._stored_form_repr(handed), name)
        self.assertEqual(mod09._catalogue_repr(handed), name)
        self.assertEqual(sys.get_int_max_str_digits(), DEFAULT_LIMIT)
    return pin


for _name, _exc in EVIL_KINDS:
    setattr(TestControls, "test_control_raising_kind_%s" % _name,
            _control_evil_pin(_name))


if __name__ == "__main__":
    unittest.main()

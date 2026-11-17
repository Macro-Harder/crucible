"""Pins for fix wave 23, builder b2, Group 2: the MOD-10 number
family, rows R23-002 and R23-003 of the Round 23 register.

Unit 1, row R23-002: _plain_number at its Fraction limb. The limb
fails on the numerator and denominator property dresses alone.
Unit 2, row R23-003: _plain_number at its complex limb. The limb
fails on the __complex__ dress alone.

Distinguishing pins fail on the pristine basis and pass on the
cured copy. Control pins pass on both trees.
"""
import unittest
from fractions import Fraction

from crucible import mod10


class NumLieFraction(Fraction):
    """A Fraction storing one value whose numerator property
    reading answers 999."""

    @property
    def numerator(self):
        return 999


class DenLieFraction(Fraction):
    """A Fraction storing one value whose denominator property
    reading answers 999."""

    @property
    def denominator(self):
        return 999


class NumRaiseFraction(Fraction):
    """A Fraction whose numerator property reading raises
    RuntimeError."""

    @property
    def numerator(self):
        raise RuntimeError("numerator reading raises")


class DenRaiseFraction(Fraction):
    """A Fraction whose denominator property reading raises
    ValueError."""

    @property
    def denominator(self):
        raise ValueError("denominator reading raises")


class StrLieFraction(Fraction):
    """A Fraction whose string and repr readings answer 999."""

    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


class StrRaiseFraction(Fraction):
    """A Fraction whose string and repr readings raise."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class FloatLieFraction(Fraction):
    """A Fraction whose __float__ reading answers 999.0."""

    def __float__(self):
        return 999.0


class ComplexLieFraction(Fraction):
    """A Fraction whose __complex__ reading answers 999+0j."""

    def __complex__(self):
        return 999 + 0j


class ComplexLie(complex):
    """A complex value whose __complex__ reading answers
    999+0j."""

    def __complex__(self):
        return 999 + 0j


class ComplexRaise(complex):
    """A complex value whose __complex__ reading raises
    IndexError."""

    def __complex__(self):
        raise IndexError("complex reading raises")


class StrLieComplex(complex):
    """A complex value whose string and repr readings answer
    999."""

    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


class StrRaiseComplex(complex):
    """A complex value whose string and repr readings raise."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class RealLieComplex(complex):
    """A complex value whose real property reading answers
    999.0."""

    @property
    def real(self):
        return 999.0


class ImagLieComplex(complex):
    """A complex value whose imag property reading answers
    888.0."""

    @property
    def imag(self):
        return 888.0


class RealRaiseComplex(complex):
    """A complex value whose real property reading raises
    RuntimeError."""

    @property
    def real(self):
        raise RuntimeError("real reading raises")


class ImagRaiseComplex(complex):
    """A complex value whose imag property reading raises
    RuntimeError."""

    @property
    def imag(self):
        raise RuntimeError("imag reading raises")


def helper_outcome(value):
    """Return (exception type name or None, rendered text or
    exception text) for _vocabulary_text handed the value."""
    try:
        return (None, mod10._vocabulary_text(value))
    except Exception as error:
        return (type(error).__name__, str(error))


def store_lookup_outcome(kind):
    try:
        mod10.store_lookup(store_kind=kind)
        return (None, "")
    except Exception as error:
        return (type(error).__name__, str(error))


def gc08_outcome(kind):
    try:
        mod10.retain_gc08_record(kind, {}, "owner-r23-b2")
        return (None, "")
    except Exception as error:
        return (type(error).__name__, str(error))


def bad_delivery(day):
    return {
        "simulated_day": day,
        "viewer_id": "viewer-1",
        "joint_outcome_components": ["text", 2.0],
        "component_denominators": [1.0, 1.0],
    }


def aggregate_outcome(run_id, day):
    try:
        mod10.retain_daily_aggregate_deliveries(
            run_id, [bad_delivery(day)])
        return (None, "")
    except Exception as error:
        return (type(error).__name__, str(error))


def checkpoint_outcome(run_id, first_day, second_day):
    mod10.retain_checkpoint(
        {"run_identifier": run_id, "simulated_day": first_day})
    try:
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": second_day})
        return (None, "")
    except Exception as error:
        return (type(error).__name__, str(error))


class TestR23002FractionHelper(unittest.TestCase):

    def test_distinguishing_num_lie_helper(self):
        outcome = helper_outcome(NumLieFraction(1, 2))
        self.assertEqual(outcome, (None, "1/2"))

    def test_distinguishing_den_lie_helper(self):
        outcome = helper_outcome(DenLieFraction(3, 2))
        self.assertEqual(outcome, (None, "3/2"))

    def test_distinguishing_num_raise_helper(self):
        outcome = helper_outcome(NumRaiseFraction(3, 2))
        self.assertEqual(outcome, (None, "3/2"))

    def test_distinguishing_den_raise_helper(self):
        outcome = helper_outcome(DenRaiseFraction(3, 2))
        self.assertEqual(outcome, (None, "3/2"))


class TestR23002FractionConsumingLoci(unittest.TestCase):

    def test_distinguishing_num_lie_store_lookup(self):
        kind, text = store_lookup_outcome(NumLieFraction(1, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown store kind: 1/2;", text)
        self.assertNotIn("999/2", text)

    def test_distinguishing_num_raise_store_lookup(self):
        kind, text = store_lookup_outcome(NumRaiseFraction(3, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown store kind: 3/2;", text)

    def test_distinguishing_den_lie_gc08(self):
        kind, text = gc08_outcome(DenLieFraction(3, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown GC-08 record kind: 3/2;", text)
        self.assertNotIn("3/999", text)

    def test_distinguishing_den_raise_gc08(self):
        kind, text = gc08_outcome(DenRaiseFraction(3, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown GC-08 record kind: 3/2;", text)

    def test_distinguishing_num_lie_aggregate_day(self):
        kind, text = aggregate_outcome(
            "r23-b2-agg-d1", NumLieFraction(1, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("at day 1/2", text)
        self.assertNotIn("999/2", text)

    def test_distinguishing_num_raise_aggregate_day(self):
        kind, text = aggregate_outcome(
            "r23-b2-agg-d2", NumRaiseFraction(3, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("at day 3/2", text)

    def test_distinguishing_num_lie_checkpoint_day(self):
        kind, text = checkpoint_outcome(
            "r23-b2-ckpt-d1", NumLieFraction(1, 2),
            NumLieFraction(1, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("day 1/2", text)
        self.assertNotIn("999/2", text)


class TestR23003ComplexHelper(unittest.TestCase):

    def test_distinguishing_complex_lie_helper(self):
        outcome = helper_outcome(ComplexLie(1 + 2j))
        self.assertEqual(outcome, (None, "(1+2j)"))

    def test_distinguishing_complex_raise_helper(self):
        outcome = helper_outcome(ComplexRaise(1 + 2j))
        self.assertEqual(outcome, (None, "(1+2j)"))


class TestR23003ComplexConsumingLoci(unittest.TestCase):

    def test_distinguishing_complex_lie_store_lookup(self):
        kind, text = store_lookup_outcome(ComplexLie(1 + 2j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown store kind: (1+2j);", text)
        self.assertNotIn("999", text)

    def test_distinguishing_complex_raise_store_lookup(self):
        kind, text = store_lookup_outcome(ComplexRaise(1 + 2j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown store kind: (1+2j);", text)

    def test_distinguishing_complex_lie_gc08(self):
        kind, text = gc08_outcome(ComplexLie(3 + 0j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown GC-08 record kind: (3+0j);", text)
        self.assertNotIn("999", text)

    def test_distinguishing_complex_lie_aggregate_day(self):
        kind, text = aggregate_outcome(
            "r23-b2-agg-d3", ComplexLie(1 + 2j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("at day (1+2j)", text)
        self.assertNotIn("999", text)

    def test_distinguishing_complex_raise_aggregate_day(self):
        kind, text = aggregate_outcome(
            "r23-b2-agg-d4", ComplexRaise(1 + 2j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("at day (1+2j)", text)

    def test_distinguishing_complex_lie_checkpoint_day(self):
        kind, text = checkpoint_outcome(
            "r23-b2-ckpt-d2", ComplexLie(1 + 2j), ComplexLie(1 + 2j))
        self.assertEqual(kind, "ValueError")
        self.assertIn("day (1+2j)", text)
        self.assertNotIn("999", text)


class TestNumberControls(unittest.TestCase):

    def test_control_plain_fraction_helper(self):
        self.assertEqual(
            helper_outcome(Fraction(3, 2)), (None, "3/2"))
        self.assertEqual(
            helper_outcome(Fraction(7, 1)), (None, "7"))

    def test_control_plain_complex_helper(self):
        self.assertEqual(
            helper_outcome(complex(1, 2)), (None, "(1+2j)"))
        self.assertEqual(
            helper_outcome(complex(7, 0)), (None, "(7+0j)"))

    def test_control_fraction_str_repr_lie(self):
        self.assertEqual(
            helper_outcome(StrLieFraction(3, 2)), (None, "3/2"))

    def test_control_fraction_str_repr_raise(self):
        self.assertEqual(
            helper_outcome(StrRaiseFraction(3, 2)), (None, "3/2"))

    def test_control_fraction_float_lie(self):
        self.assertEqual(
            helper_outcome(FloatLieFraction(3, 2)), (None, "3/2"))

    def test_control_fraction_complex_lie(self):
        self.assertEqual(
            helper_outcome(ComplexLieFraction(3, 2)), (None, "3/2"))

    def test_control_complex_str_repr_lie(self):
        self.assertEqual(
            helper_outcome(StrLieComplex(1 + 2j)), (None, "(1+2j)"))

    def test_control_complex_str_repr_raise(self):
        self.assertEqual(
            helper_outcome(StrRaiseComplex(1 + 2j)), (None, "(1+2j)"))

    def test_control_complex_real_lie(self):
        self.assertEqual(
            helper_outcome(RealLieComplex(1 + 2j)), (None, "(1+2j)"))

    def test_control_complex_imag_lie(self):
        self.assertEqual(
            helper_outcome(ImagLieComplex(1 + 2j)), (None, "(1+2j)"))

    def test_control_complex_real_raise(self):
        self.assertEqual(
            helper_outcome(RealRaiseComplex(1 + 2j)),
            (None, "(1+2j)"))

    def test_control_complex_imag_raise(self):
        self.assertEqual(
            helper_outcome(ImagRaiseComplex(1 + 2j)),
            (None, "(1+2j)"))

    def test_control_plain_fraction_day_aggregate(self):
        kind, text = aggregate_outcome(
            "r23-b2-agg-c1", Fraction(3, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("at day 3/2", text)

    def test_control_plain_complex_store_lookup(self):
        kind, text = store_lookup_outcome(complex(1, 2))
        self.assertEqual(kind, "ValueError")
        self.assertIn("unknown store kind: (1+2j);", text)

    def test_control_sound_limbs_helper(self):
        from decimal import Decimal

        self.assertEqual(helper_outcome(True), (None, "1"))
        self.assertEqual(helper_outcome(7), (None, "7"))
        self.assertEqual(helper_outcome(2.5), (None, "2.5"))
        self.assertEqual(
            helper_outcome(Decimal("2.5")), (None, "2.5"))


if __name__ == "__main__":
    unittest.main()

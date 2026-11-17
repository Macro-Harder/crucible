"""Pins for fix wave 23, builder b6, Group 6: row R23-008 of
the Round 23 register, the MOD-10 day match form at
_day_match_form, at its Decimal and Fraction limbs.

The distinguishing pins stand on the supplying dress handings
at retain_checkpoint, in both judgement directions: a true
duplicate admitted in silence by a lying is_finite reading, a
duplicate manufactured by a lying numerator reading, and the
bare escapes of the raising limbs at is_finite,
to_integral_value, equality, numerator, and denominator.
Distinguishing pins fail or error on the pristine basis and
pass on the cured copy. Control pins pass on both trees.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod10


class LyingFiniteDecimal(Decimal):
    """A Decimal storing 3 whose is_finite reading answers
    False."""

    def is_finite(self):
        return False


class RaisingFiniteDecimal(Decimal):
    """A Decimal storing 3 whose is_finite reading raises."""

    def is_finite(self):
        raise IndexError("is_finite reading raises")


class RaisingIntegralDecimal(Decimal):
    """A Decimal storing 3 whose to_integral_value reading
    raises."""

    def to_integral_value(self, *args, **kwargs):
        raise IndexError("to_integral_value reading raises")


class RaisingEqDecimal(Decimal):
    """A Decimal storing 3 whose equality reading raises."""

    __hash__ = Decimal.__hash__

    def __eq__(self, other):
        raise IndexError("equality reading raises")


class LyingIntegralDecimal(Decimal):
    """A Decimal storing 3.5 whose to_integral_value reading
    answers the stored value itself, so the integral test
    passes on a non whole day."""

    def to_integral_value(self, *args, **kwargs):
        return Decimal("3.5")


class LyingEqDecimal(Decimal):
    """A Decimal storing 3.5 whose equality reading answers
    True to every comparison."""

    __hash__ = Decimal.__hash__

    def __eq__(self, other):
        return True


class LyingNumeratorFraction(Fraction):
    """A Fraction storing 3/2 whose numerator property answers
    999 and whose denominator property answers 1."""

    numerator = property(lambda self: 999)
    denominator = property(lambda self: 1)


class LyingDenominatorFraction(Fraction):
    """A Fraction storing 3/2 whose denominator property
    answers 1."""

    denominator = property(lambda self: 1)


class RaisingNumeratorFraction(Fraction):
    """A Fraction whose numerator property raises."""

    @property
    def numerator(self):
        raise IndexError("numerator reading raises")


class RaisingDenominatorFraction(Fraction):
    """A Fraction whose denominator property raises."""

    @property
    def denominator(self):
        raise IndexError("denominator reading raises")


def attempt(run_id, first_day, second_day):
    """Retain a first checkpoint, then attempt a second for the
    same run. Return ("refused", sentence) on the named refusal
    or ("retained", count) where the second stands retained.
    Any bare escape propagates to the caller."""
    mod10.retain_checkpoint(
        {"run_identifier": run_id, "simulated_day": first_day})
    try:
        mod10.retain_checkpoint(
            {"run_identifier": run_id,
             "simulated_day": second_day})
    except ValueError as error:
        return ("refused", str(error))
    return ("retained", len(mod10.checkpoints_for_run(run_id)))


class TestDistinguishingDayMatchForm(unittest.TestCase):

    def test_lying_is_finite_duplicate_refused(self):
        standing, text = attempt(
            "r23-b6-d1", 3, LyingFiniteDecimal(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)
        self.assertIn(
            "second checkpoint for the same run and day is "
            "rejected", text)

    def test_lying_numerator_manufactured_duplicate_retained(self):
        standing, count = attempt(
            "r23-b6-d2", 999, LyingNumeratorFraction(3, 2))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_raising_is_finite_refused_not_bare(self):
        standing, text = attempt(
            "r23-b6-d3", 3, RaisingFiniteDecimal(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_raising_to_integral_refused_not_bare(self):
        standing, text = attempt(
            "r23-b6-d4", 3, RaisingIntegralDecimal(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_raising_equality_refused_not_bare(self):
        standing, text = attempt(
            "r23-b6-d5", 3, RaisingEqDecimal(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_raising_numerator_retained_not_bare(self):
        standing, count = attempt(
            "r23-b6-d6", 999, RaisingNumeratorFraction(3, 2))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_raising_denominator_retained_not_bare(self):
        standing, count = attempt(
            "r23-b6-d7", 999, RaisingDenominatorFraction(3, 2))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_raising_numerator_whole_refused_not_bare(self):
        standing, text = attempt(
            "r23-b6-d8", 3, RaisingNumeratorFraction(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_raising_denominator_whole_refused_not_bare(self):
        standing, text = attempt(
            "r23-b6-d9", 3, RaisingDenominatorFraction(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_lying_denominator_manufactured_duplicate_retained(self):
        standing, count = attempt(
            "r23-b6-d10", 3, LyingDenominatorFraction(3, 2))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_lying_to_integral_manufactured_duplicate_retained(self):
        standing, count = attempt(
            "r23-b6-d11", 3, LyingIntegralDecimal("3.5"))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_lying_equality_manufactured_duplicate_retained(self):
        standing, count = attempt(
            "r23-b6-d12", 3, LyingEqDecimal("3.5"))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)


class TestControlDayMatchForm(unittest.TestCase):

    def test_control_plain_decimal_whole_refused(self):
        standing, text = attempt("r23-b6-c1", 3, Decimal(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_control_plain_decimal_nonwhole_retained(self):
        standing, count = attempt(
            "r23-b6-c2", 3, Decimal("3.5"))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_control_plain_decimal_nan_pair_refused(self):
        standing, text = attempt(
            "r23-b6-c3", Decimal("NaN"), Decimal("NaN"))
        self.assertEqual(standing, "refused")
        self.assertIn("day NaN", text)

    def test_control_plain_fraction_whole_refused(self):
        standing, text = attempt("r23-b6-c4", 3, Fraction(3))
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_control_plain_fraction_nonwhole_retained(self):
        standing, count = attempt(
            "r23-b6-c5", 999, Fraction(3, 2))
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_control_bool_pair_refused_as_int_sentence(self):
        standing, text = attempt("r23-b6-c6", True, True)
        self.assertEqual(standing, "refused")
        self.assertIn("day 1", text)

    def test_control_bool_day_distinct_from_int_day(self):
        standing, count = attempt("r23-b6-c7", 1, True)
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_control_int_pair_refused(self):
        standing, text = attempt("r23-b6-c8", 3, 3)
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)

    def test_control_float_day_distinct_from_int_day(self):
        standing, count = attempt("r23-b6-c9", 3, 3.0)
        self.assertEqual(standing, "retained")
        self.assertEqual(count, 2)

    def test_control_float_pair_refused(self):
        standing, text = attempt("r23-b6-c10", 2.5, 2.5)
        self.assertEqual(standing, "refused")
        self.assertIn("day 2.5", text)

    def test_control_text_pair_refused(self):
        standing, text = attempt(
            "r23-b6-c11", "day-3", "day-3")
        self.assertEqual(standing, "refused")
        self.assertIn("day day-3", text)

    def test_control_digit_text_day_matches_int_day(self):
        standing, text = attempt("r23-b6-c12", 3, "3")
        self.assertEqual(standing, "refused")
        self.assertIn("day 3", text)


if __name__ == "__main__":
    unittest.main()

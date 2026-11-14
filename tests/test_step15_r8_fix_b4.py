"""Pin tests for rows R7-012 and R7-015.

Row R7-012 covers the int and float limbs of
validate_stream_cardinality at MOD-02. Row R7-015 covers the
closed vocabulary judgements at validate_domain and
validate_derivation_domain_use at MOD-02 and at
validate_store_addressing at MOD-01.
"""

import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod01, mod02


class ConversionLieInt(int):
    """An int storing one value whose conversion readings report one."""

    def __new__(cls, value):
        return int.__new__(cls, value)

    def __int__(self):
        return 1

    def __index__(self):
        return 1

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class ConversionLieFloat(float):
    """A float storing one value whose conversion reading reports one."""

    def __new__(cls, value):
        return float.__new__(cls, value)

    def __float__(self):
        return 1.0

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = float.__hash__


class EqualityLieInt(int):
    """An int whose equality reading answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class EqualityLieFloat(float):
    """A float whose equality reading answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = float.__hash__


class EqualityLieDecimal(Decimal):
    """A Decimal whose equality reading answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = Decimal.__hash__


class EqualityLieFraction(Fraction):
    """A Fraction whose equality reading answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = Fraction.__hash__


class EqualityLieComplex(complex):
    """A complex value whose equality reading answers True always."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = complex.__hash__


class EqualityLieText(str):
    """A text value whose equality reading answers True always."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


def cardinality_of(value):
    counts = {"alpha": value, "beta": 1}
    stream_set = {"stream_class_inventory": ["alpha", "beta"]}
    return mod02.validate_stream_cardinality(counts, stream_set=stream_set)


class TestR7012CardinalityConversionLimbs(unittest.TestCase):

    def test_int_conversion_lie_storing_99_fails(self):
        self.assertFalse(cardinality_of(ConversionLieInt(99)))

    def test_float_conversion_lie_storing_99_fails(self):
        self.assertFalse(cardinality_of(ConversionLieFloat(99.0)))

    def test_int_conversion_lie_storing_one_passes(self):
        self.assertTrue(cardinality_of(ConversionLieInt(1)))

    def test_float_conversion_lie_storing_one_passes(self):
        self.assertTrue(cardinality_of(ConversionLieFloat(1.0)))

    def test_plain_int_counts_stand_both_ways(self):
        self.assertTrue(cardinality_of(1))
        self.assertFalse(cardinality_of(99))
        self.assertFalse(cardinality_of(0))
        self.assertFalse(cardinality_of(2))

    def test_plain_float_counts_stand_both_ways(self):
        self.assertTrue(cardinality_of(1.0))
        self.assertFalse(cardinality_of(99.0))
        self.assertFalse(cardinality_of(0.0))

    def test_equality_lie_int_storing_99_fails(self):
        self.assertFalse(cardinality_of(EqualityLieInt(99)))

    def test_equality_lie_int_storing_one_passes(self):
        self.assertTrue(cardinality_of(EqualityLieInt(1)))

    def test_equality_lie_float_storing_99_fails(self):
        self.assertFalse(cardinality_of(EqualityLieFloat(99.0)))

    def test_equality_lie_float_storing_one_passes(self):
        self.assertTrue(cardinality_of(EqualityLieFloat(1.0)))

    def test_decimal_limb_does_not_regress(self):
        self.assertFalse(cardinality_of(EqualityLieDecimal(99)))
        self.assertTrue(cardinality_of(EqualityLieDecimal(1)))
        self.assertTrue(cardinality_of(Decimal(1)))
        self.assertFalse(cardinality_of(Decimal(99)))

    def test_fraction_limb_does_not_regress(self):
        self.assertFalse(cardinality_of(EqualityLieFraction(99)))
        self.assertTrue(cardinality_of(EqualityLieFraction(1)))
        self.assertTrue(cardinality_of(Fraction(1)))
        self.assertFalse(cardinality_of(Fraction(99)))

    def test_complex_limb_does_not_regress(self):
        self.assertFalse(cardinality_of(EqualityLieComplex(99 + 0j)))
        self.assertTrue(cardinality_of(EqualityLieComplex(1 + 0j)))
        self.assertTrue(cardinality_of(complex(1, 0)))
        self.assertFalse(cardinality_of(complex(1, 1)))
        self.assertFalse(cardinality_of(complex(99, 0)))


class TestR7015DomainVocabulary(unittest.TestCase):

    def test_plain_domain_values_stand_both_ways(self):
        self.assertTrue(mod02.validate_domain("screening"))
        self.assertTrue(mod02.validate_domain("held out confirmation"))
        self.assertFalse(mod02.validate_domain("bogus"))
        self.assertFalse(mod02.validate_domain(None))
        self.assertFalse(mod02.validate_domain(""))

    def test_lying_text_storing_bogus_fails_as_domain(self):
        self.assertFalse(mod02.validate_domain(EqualityLieText("bogus")))

    def test_lying_text_storing_a_stated_domain_passes(self):
        self.assertTrue(mod02.validate_domain(EqualityLieText("screening")))
        self.assertTrue(
            mod02.validate_domain(EqualityLieText("held out confirmation")))

    def test_plain_derivation_domain_use_stands_both_ways(self):
        self.assertTrue(mod02.validate_derivation_domain_use(
            "screening", "screening"))
        self.assertTrue(mod02.validate_derivation_domain_use(
            "held out confirmation", "held out confirmation"))
        self.assertFalse(mod02.validate_derivation_domain_use(
            "screening", "held out confirmation"))
        self.assertFalse(mod02.validate_derivation_domain_use(
            "bogus", "bogus"))
        self.assertFalse(mod02.validate_derivation_domain_use(
            None, None))

    def test_lying_text_pair_storing_bogus_values_fails(self):
        self.assertFalse(mod02.validate_derivation_domain_use(
            EqualityLieText("bogus"), EqualityLieText("bogus2")))

    def test_lying_text_pair_storing_distinct_domains_fails(self):
        self.assertFalse(mod02.validate_derivation_domain_use(
            EqualityLieText("screening"),
            EqualityLieText("held out confirmation")))

    def test_lying_text_pair_storing_bogus_and_a_domain_fails(self):
        self.assertFalse(mod02.validate_derivation_domain_use(
            EqualityLieText("bogus"), EqualityLieText("screening")))

    def test_lying_text_pair_storing_the_same_domain_passes(self):
        self.assertTrue(mod02.validate_derivation_domain_use(
            EqualityLieText("screening"), EqualityLieText("screening")))
        self.assertTrue(mod02.validate_derivation_domain_use(
            EqualityLieText("held out confirmation"),
            EqualityLieText("held out confirmation")))


class TestR7015StoreAddressingVocabulary(unittest.TestCase):

    def test_plain_store_addressing_stands_both_ways(self):
        self.assertTrue(mod01.validate_store_addressing(["sweep"]))
        self.assertTrue(mod01.validate_store_addressing(["pilot"]))
        self.assertTrue(mod01.validate_store_addressing(["live"]))
        self.assertFalse(mod01.validate_store_addressing(["bogus"]))
        self.assertFalse(mod01.validate_store_addressing([]))
        self.assertFalse(mod01.validate_store_addressing(["sweep", "pilot"]))

    def test_lying_text_storing_bogus_fails_as_store_kind(self):
        self.assertFalse(
            mod01.validate_store_addressing([EqualityLieText("bogus")]))

    def test_lying_text_storing_a_stated_kind_passes(self):
        self.assertTrue(
            mod01.validate_store_addressing([EqualityLieText("sweep")]))
        self.assertTrue(
            mod01.validate_store_addressing([EqualityLieText("pilot")]))

    def test_lying_text_storing_bogus_in_tuple_form_fails(self):
        self.assertFalse(
            mod01.validate_store_addressing((EqualityLieText("bogus"),)))


if __name__ == "__main__":
    unittest.main()

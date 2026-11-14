"""Pins for fix wave 6, Builder 11.

Rows R6-018 (MOD-02 stream cardinality fall through) and R6-036
(MOD-07 tracer memoryview blank check). Each charged defect form
stands stated with lawful controls standing both ways.
"""

import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod02, mod07


class LyingObject:
    """A plain object storing no number whose equality reading
    answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class LyingFloat(float):
    """A float subclass whose equality and inequality readings
    answer as a count of one, whatever it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = float.__hash__


class LyingStr(str):
    """A text subclass whose equality and inequality readings
    answer as a count of one, whatever it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class LyingDecimal(Decimal):
    """A Decimal subclass whose equality and inequality readings
    answer as a count of one, whatever it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = Decimal.__hash__


class LyingFraction(Fraction):
    """A Fraction subclass whose equality and inequality readings
    answer as a count of one, whatever it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = Fraction.__hash__


class TestR6018CardinalityFallThrough(unittest.TestCase):

    STREAM_SET = {"stream_class_inventory": ["alpha", "beta"]}

    def verdict(self, count):
        return mod02.validate_stream_cardinality(
            counts={"alpha": count, "beta": 1},
            stream_set=self.STREAM_SET)

    def test_object_count_storing_no_number_refused(self):
        self.assertFalse(self.verdict(LyingObject()))

    def test_float_subclass_count_storing_99_refused(self):
        self.assertFalse(self.verdict(LyingFloat(99.0)))

    def test_text_subclass_count_storing_99_refused(self):
        self.assertFalse(self.verdict(LyingStr("99")))

    def test_decimal_subclass_count_storing_99_refused(self):
        self.assertFalse(self.verdict(LyingDecimal(99)))

    def test_fraction_subclass_count_storing_99_refused(self):
        self.assertFalse(self.verdict(LyingFraction(99)))

    def test_text_subclass_count_storing_one_as_text_refused(self):
        self.assertFalse(self.verdict(LyingStr("1")))

    def test_controls_plain_counts(self):
        self.assertTrue(self.verdict(1))
        self.assertFalse(self.verdict(99))
        self.assertFalse(self.verdict(0))

    def test_controls_boundary_counts_of_one(self):
        self.assertTrue(self.verdict(True))
        self.assertFalse(self.verdict(False))
        self.assertTrue(self.verdict(1.0))
        self.assertTrue(self.verdict(Decimal(1)))
        self.assertTrue(self.verdict(Fraction(1)))

    def test_controls_honest_other_counts(self):
        self.assertFalse(self.verdict(99.0))
        self.assertFalse(self.verdict(Decimal(2)))
        self.assertFalse(self.verdict(Fraction(99)))
        self.assertFalse(self.verdict("99"))
        self.assertFalse(self.verdict("1"))
        self.assertFalse(self.verdict(object()))

    def test_controls_stored_one_under_lying_readings(self):
        self.assertTrue(self.verdict(LyingFloat(1.0)))
        self.assertTrue(self.verdict(LyingDecimal(1)))

    def test_controls_container_counts(self):
        self.assertTrue(self.verdict(["one"]))
        self.assertFalse(self.verdict(["one", "two"]))
        self.assertTrue(self.verdict(("one",)))
        self.assertFalse(self.verdict(("one", "two")))


def tracer_set_with(field, value):
    records = mod07.tracer_passage_records("run-1")
    records[0][field] = value
    return records


class TestR6036TracerMemoryviewBlank(unittest.TestCase):

    FIELDS = ("point_in_run", "what_in_fact_passed")

    def test_memoryview_spaces_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b"  "))))

    def test_memoryview_tab_newline_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b"\t\n"))))

    def test_memoryview_over_bytearray_space_refused(self):
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(
                        field, memoryview(bytearray(b" ")))))

    def test_controls(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            mod07.tracer_passage_records("run-1")))
        for field in self.FIELDS:
            with self.subTest(field=field):
                self.assertTrue(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b"x"))))
                self.assertTrue(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b" x"))))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, memoryview(b""))))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, b"  ")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, bytearray(b"  "))))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, "")))
                self.assertFalse(mod07.validate_tracer_passage_set(
                    tracer_set_with(field, "   ")))


if __name__ == "__main__":
    unittest.main()

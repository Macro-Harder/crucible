"""Pins for fix wave 26 builder b1: row R26-001.

Copyright: J.P. Picard aka Macro-Harder.
"""
import sys
import unittest

from crucible import mod10

BIG = 10 ** 5000
DIGITS = "1" + "0" * 5000
SMALL_BIG = 10 ** 4999
SMALL_DIGITS = "1" + "0" * 4999
NINES_DIGITS = "9" * 4999
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


class TestDaySortKeyBeyond(Base):
    def test_plain_digit_text_beyond_numbered_group(self):
        key = mod10._day_sort_key((DIGITS, "viewer-1"))
        self.assertEqual(key[0], 0)
        self.assertEqual(key[1], BIG)

    def test_spaced_digit_text_beyond_numbered_group(self):
        key = mod10._day_sort_key(("  " + DIGITS + "  ", "viewer-1"))
        self.assertEqual(key[0], 0)
        self.assertEqual(key[1], BIG)

    def test_leading_zero_digit_text_beyond_numbered_group(self):
        key = mod10._day_sort_key(("0" * 100 + SMALL_DIGITS, "viewer-1"))
        self.assertEqual(key[0], 0)
        self.assertEqual(key[1], SMALL_BIG)

    def test_two_beyond_texts_in_number_order_not_text_order(self):
        days = [SMALL_DIGITS, NINES_DIGITS]
        ordered = sorted(
            days,
            key=lambda day: mod10._day_sort_key((day, "viewer-1")))
        self.assertTrue(ordered == [NINES_DIGITS, SMALL_DIGITS])

    def test_beyond_digit_text_before_larger_integer_day(self):
        text_key = mod10._day_sort_key((SMALL_DIGITS, "viewer-1"))
        int_key = mod10._day_sort_key((BIG, "viewer-1"))
        self.assertTrue(text_key < int_key)


def day_labels(records):
    labels = []
    for record in records:
        day = record["simulated_day"]
        if isinstance(day, str) and day == SMALL_DIGITS:
            labels.append("small_digits")
        elif isinstance(day, int) and day == BIG:
            labels.append("big_int")
        elif isinstance(day, int) and day == 7:
            labels.append("seven")
        else:
            labels.append("other")
    return labels


class TestHelperAndPublicOrderingBeyond(Base):
    def test_aggregates_from_deliveries_number_order(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r26-b1-helper",
                [delivery(BIG, "viewer-a"),
                 delivery(SMALL_DIGITS, "viewer-b"),
                 delivery(7, "viewer-c")])
        self.assertIn(
            "stand impossible in the form the module "
            "validator states", str(caught.exception))

    def test_daily_aggregates_public_number_order(self):
        with self.assertRaises(ValueError) as caught:
            mod10.daily_aggregates_for_run(
                "r26-b1-daily",
                [delivery(BIG, "viewer-a"),
                 delivery(SMALL_DIGITS, "viewer-b"),
                 delivery(7, "viewer-c")])
        self.assertIn(
            "stand impossible in the form the module "
            "validator states", str(caught.exception))

    def test_aggregate_manifest_public_number_order(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r26-b1-manifest",
                [delivery(BIG, "viewer-a"),
                 delivery(SMALL_DIGITS, "viewer-b"),
                 delivery(7, "viewer-c")])
        self.assertIn(
            "stand impossible in the form the module "
            "validator states", str(caught.exception))


class TestControls(Base):
    def test_within_limit_digit_text_numbered_group(self):
        key = mod10._day_sort_key(("42", "viewer-1"))
        self.assertEqual(key[0], 0)
        self.assertEqual(key[1], 42)
        spaced = mod10._day_sort_key((" 42 ", "viewer-1"))
        self.assertEqual(spaced[0], 0)
        self.assertEqual(spaced[1], 42)

    def test_integer_day_itself_numbered_group(self):
        self.assertEqual(mod10._day_sort_key((7, "viewer-1"))[:2], (0, 7))
        big_key = mod10._day_sort_key((BIG, "viewer-1"))
        self.assertEqual(big_key[0], 0)
        self.assertEqual(big_key[1], BIG)
        self.assertEqual(
            mod10._day_sort_key((-1, "viewer-1"))[:2], (0, -1))

    def test_signed_text_in_later_group(self):
        self.assertEqual(mod10._day_sort_key(("-1", "viewer-1"))[:2], (1, 0))
        self.assertEqual(mod10._day_sort_key(("+2", "viewer-1"))[:2], (1, 0))
        beyond_signed = mod10._day_sort_key(("-" + DIGITS, "viewer-1"))
        self.assertEqual(beyond_signed[:2], (1, 0))
        beyond_plus = mod10._day_sort_key(("+" + DIGITS, "viewer-1"))
        self.assertEqual(beyond_plus[:2], (1, 0))

    def test_non_digit_text_in_later_group(self):
        for text in ("a-day", "12a", "", "1_000"):
            key = mod10._day_sort_key((text, "viewer-1"))
            self.assertEqual(key[:2], (1, 0))

    def test_superscript_text_in_later_group(self):
        key = mod10._day_sort_key(("\u00b2", "viewer-1"))
        self.assertEqual(key[:2], (1, 0))
        key_many = mod10._day_sort_key(("\u00b2" * 5000, "viewer-1"))
        self.assertEqual(key_many[:2], (1, 0))

    def test_limit_stands_default(self):
        self.assertEqual(sys.get_int_max_str_digits(), LIMIT)


if __name__ == "__main__":
    unittest.main()

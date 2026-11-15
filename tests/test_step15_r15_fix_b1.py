"""Pins for fix wave 14, Builder 1 (Group 1): rows R14-001 to
R14-006, the dict node, segmentation, and enumeration family at
MOD-01, MOD-06, MOD-08, and MOD-13, under settlements S-4, S-11,
S-12, S-13, and S-14.

Each defect pin fails on the charged defect against the pristine
tree and passes after the cure. Controls state the standing forms
the cures must not move.
"""

import time
import unittest

from crucible import mod01, mod06, mod08, mod13


class TestR14001Mod06ZeroReadingMiddleKey(unittest.TestCase):
    """R14-001: a barred marker split across two keys of one dict,
    with a zero reading key between them, stands judged at the
    MOD-06 node act, the walk, and the escrow gate."""

    MONEY_FORMS = (
        {"real_": 5, "": 9, "money": 6},
        {"real_": 5, 123: 9, "money": 6},
        {"real_": 5, (): 9, "money": 6},
        {"real_": 5, frozenset(): 9, "money": 6},
    )
    ANCHOR_FORMS = (
        {"anchor_": 5, "": 9, "set": 6},
        {"anchor_": 5, 123: 9, "set": 6},
        {"anchor_": 5, (): 9, "set": 6},
    )

    def test_money_split_with_zero_reading_middle_barred(self):
        for form in self.MONEY_FORMS:
            self.assertTrue(mod06._dict_node_split_barred(form), form)
            self.assertTrue(mod06._payload_carries_barred(form), form)

    def test_anchor_split_with_zero_reading_middle_barred(self):
        for form in self.ANCHOR_FORMS:
            self.assertTrue(mod06._dict_node_split_barred(form), form)
            self.assertTrue(mod06._payload_carries_barred(form), form)

    def test_split_with_zero_reading_middle_refused_at_gate(self):
        for form in self.MONEY_FORMS + self.ANCHOR_FORMS:
            with self.assertRaises(ValueError, msg=repr(form)):
                mod06.escrow_result("release", payload=form)

    def test_two_key_split_control_still_barred(self):
        form = {"real_": 5, "money": 6}
        self.assertTrue(mod06._dict_node_split_barred(form))
        self.assertTrue(mod06._payload_carries_barred(form))
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=form)

    def test_clean_and_reversed_controls_still_clean(self):
        self.assertFalse(mod06._payload_carries_barred(
            {"plain": 5, "other": 6}))
        self.assertFalse(mod06._payload_carries_barred(
            {"money": 6, "": 9, "real_": 5}))


class TestR14002Mod01MoneyWalkDictNode(unittest.TestCase):
    """R14-002: the MOD-01 money walk judges the dict node itself,
    so a barred marker split across two keys of one dict stands
    judged in plain and folded forms, in every position."""

    def test_single_key_control_carries(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"field": {"real_money": 5}}))
        self.assertTrue(mod01._carries_real_money_value(
            {"field": {"realmani": 5}}))

    def test_plain_split_carries_in_every_position(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"real_": 5, "money": 6}))
        self.assertTrue(mod01._carries_real_money_value(
            {"field": {"real_": 5, "money": 6}}))
        self.assertTrue(mod01._carries_real_money_value(
            {"field": [{"real_": 5, "money": 6}]}))

    def test_folded_split_carries(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"field": {"real": 5, "mani": 6}}))
        self.assertTrue(mod01._carries_real_money_value(
            {"real": 5, "mani": 6}))

    def test_clean_control_still_clean(self):
        self.assertFalse(mod01._carries_real_money_value({"plain": 5}))
        self.assertFalse(mod01._carries_real_money_value(
            {"money": 6, "real_": 5}))


class TestR14003PairSplitAcrossKeys(unittest.TestCase):
    """R14-003: the amount and currency pair, judged at dict level
    by both money walks, stands judged where each name stands
    split across two keys of the same dict."""

    SPLIT = {"amo": 5, "unt": 6, "curr": 7, "ency": 8}
    HALF_SPLIT = {"amo": 5, "unt": 6, "currency": 7}

    def test_plain_pair_controls_barred_at_both_walks(self):
        form = {"amount": 5, "currency": 7}
        self.assertTrue(mod01._carries_real_money_value(
            {"field": form}))
        self.assertTrue(mod06._payload_carries_barred(form))
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=form)

    def test_whole_split_pair_barred_at_both_walks(self):
        self.assertTrue(mod01._carries_real_money_value(self.SPLIT))
        self.assertTrue(mod01._carries_real_money_value(
            {"field": self.SPLIT}))
        self.assertTrue(mod06._payload_carries_barred(self.SPLIT))
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=self.SPLIT)

    def test_half_split_pair_barred_at_both_walks(self):
        self.assertTrue(mod01._carries_real_money_value(
            self.HALF_SPLIT))
        self.assertTrue(mod06._payload_carries_barred(self.HALF_SPLIT))

    def test_amount_alone_split_still_clean(self):
        self.assertFalse(mod01._carries_real_money_value(
            {"amo": 5, "unt": 6}))
        self.assertFalse(mod06._payload_carries_barred(
            {"amo": 5, "unt": 6}))


class TestR14004Mod08GateDictNode(unittest.TestCase):
    """R14-004: the MOD-08 delivery gate walk judges the dict node
    itself, so a barred reading split across two keys of one dict
    stands refused at accept_detection_input."""

    @staticmethod
    def record(feature_values):
        return {
            "agent_identifier": "agent-y2",
            "day": 1,
            "feature_values": feature_values,
            "records_for_agent_and_day": [],
        }

    def test_predicate_bars_node_and_walk_now_finds_it(self):
        form = {"ground": 1, "truth": 2}
        self.assertTrue(mod08._is_barred_key(form))
        self.assertTrue(mod08._find_barred(form))

    def test_nested_split_found(self):
        self.assertTrue(mod08._find_barred(
            {"wrap": {"ground": 1, "truth": 2}}))

    def test_split_forms_refused_at_gate(self):
        for features in (
            {"ground": 1, "truth": 2},
            {"gro": 1, "undtr": 2, "uth": 3},
            {"member": 1, "ship": 2},
            {"can": 1, "ary": 2},
        ):
            with self.assertRaises(Exception, msg=repr(features)):
                mod08.accept_detection_input(self.record(features))

    def test_single_key_control_still_refused(self):
        with self.assertRaises(Exception):
            mod08.accept_detection_input(
                self.record({"groundtruth": 1}))

    def test_reversed_and_clean_controls_still_accepted(self):
        accepted = mod08.accept_detection_input(
            self.record({"truth": 2, "ground": 1}))
        self.assertEqual(accepted["agent_identifier"], "agent-y2")
        accepted = mod08.accept_detection_input(
            self.record({"alpha": 1, "beta": 2}))
        self.assertEqual(accepted["agent_identifier"], "agent-y2")


def _mod13_part(width, tag):
    return tuple(
        frozenset({tag + "a" + str(index), tag + "b" + str(index)})
        for index in range(width))


class TestR14005Mod13UnorderedLimbBound(unittest.TestCase):
    """R14-005: the MOD-13 unordered limb computes the combination
    total before any join stands built, in the S-13 form, so a
    small clean key whose cross product stands far past 5040
    returns its sorted join alone at once."""

    def test_three_parts_seven_wide_returns_single_join_fast(self):
        key = frozenset({_mod13_part(7, "q0"), _mod13_part(7, "q1"),
                         _mod13_part(7, "q2")})
        start = time.monotonic()
        texts = mod13._stored_key_texts(key)
        elapsed = time.monotonic() - start
        self.assertEqual(texts, {mod13._stored_key_text(key)})
        self.assertLess(elapsed, 4.0)

    def test_two_parts_wide_returns_single_join_fast(self):
        key = frozenset({_mod13_part(9, "w0"), _mod13_part(9, "w1")})
        start = time.monotonic()
        texts = mod13._stored_key_texts(key)
        elapsed = time.monotonic() - start
        self.assertEqual(texts, {mod13._stored_key_text(key)})
        self.assertLess(elapsed, 4.0)

    def test_unordered_controls_hold_exact(self):
        seven = frozenset("abcdefg")
        self.assertEqual(len(mod13._stored_key_texts(seven)), 5040)
        eight = frozenset("abcdefgh")
        self.assertEqual(
            mod13._stored_key_texts(eight),
            {mod13._stored_key_text(eight)})


class TestR14006Mod06SevenPartDigitBound(unittest.TestCase):
    """R14-006: a clean seven part frozenset key carrying one digit
    part answers inside the S-12 bound of 4 seconds, at the walk,
    at the reading act, and at escrow_result, its verdict correct."""

    Z_FORM = frozenset({"a", "m", "0", "u", "n", "t", "z"})
    ONE_FORM = frozenset({"a", "m", "1", "u", "n", "t", "z"})

    def test_z_form_walk_inside_bound(self):
        start = time.monotonic()
        result = mod06._payload_carries_barred({self.Z_FORM: 1})
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 4.0)

    def test_z_form_gate_inside_bound(self):
        start = time.monotonic()
        record = mod06.escrow_result(
            "release", payload={self.Z_FORM: 1})
        elapsed = time.monotonic() - start
        self.assertEqual(record["kind"], "release")
        self.assertLess(elapsed, 4.0)

    def test_one_form_walk_inside_bound(self):
        start = time.monotonic()
        result = mod06._payload_carries_barred({self.ONE_FORM: 1})
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 4.0)

    def test_reading_act_forms_inside_bound(self):
        start = time.monotonic()
        self.assertFalse(mod06._key_reads_as(self.Z_FORM, "amount"))
        self.assertLess(time.monotonic() - start, 4.0)
        start = time.monotonic()
        self.assertFalse(mod06._key_reads_as(
            frozenset({"b", "m", "0", "u", "n", "t", "z"}), "amount"))
        self.assertLess(time.monotonic() - start, 4.0)
        start = time.monotonic()
        self.assertFalse(mod06._key_reads_as(
            frozenset({"a", "m", "0", "u", "n", "t", "zz"}),
            "currency"))
        self.assertLess(time.monotonic() - start, 4.0)

    def test_digit_reading_true_control_holds(self):
        self.assertTrue(mod06._key_reads_as(
            frozenset({"a", "m", "0", "u", "n", "t"}), "amount"))

    def test_neighbouring_sizes_still_fast_and_correct(self):
        start = time.monotonic()
        self.assertFalse(mod06._payload_carries_barred(
            {frozenset({"a", "m", "0", "u", "n", "t", "z", "w"}): 1}))
        self.assertLess(time.monotonic() - start, 4.0)


if __name__ == "__main__":
    unittest.main()

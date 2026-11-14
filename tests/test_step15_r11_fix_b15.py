"""Pins for fix wave 10 Builder 15 (second supplementary): the
joined reading of an unordered container must not escape on part
count. Row R10-003 stands PARTIAL on the beyond bound limb left
by Builder 14: a barred name split across 8 distinct parts of one
frozenset returned not barred at MOD-03, MOD-04, MOD-05, MOD-08,
and MOD-10 at PYTHONHASHSEED 0, 1, 2, and 4, while the 7 part form
returned barred at every seed. The settlement at limb 3 names
frozenset as a container whose parts joined in order stand read
as one name, with no part count, candidate count, or size
exception. These pins carry the 8 part forms, and larger forms,
at the charged acts of MOD-01, MOD-03, MOD-04, MOD-05, MOD-06,
MOD-08, and MOD-10, beside clean controls past the same counts
and ordered controls that must keep their standing behaviour."""
import unittest

from crucible import mod01, mod03, mod04, mod05, mod06, mod08, mod10

GROUND8 = frozenset(("g", "ro", "un", "d", "_t", "ru", "t", "h"))
GROUND8_SET = {"g", "ro", "un", "d", "_t", "ru", "t", "h"}
GROUND12 = frozenset(
    ("g", "r", "o", "u", "n", "d", "_", "t",
     b"r", b"u", b"t", "h"))
AMOUNT8 = frozenset(("a", "m", "ou", "n", "t", "_", "-", " "))
CURRENCY8 = frozenset(("c", "u", "rr", "e", "n", "cy", "_", "-"))
REALMONEY8 = frozenset(("r", "ea", "l", "mo", "n", "e", "y", "_"))
REAL_MONEY8 = frozenset(("r", "ea", "l", "_", "mo", "ne", "y", "x"))
ANCHOR8 = frozenset(("a", "n", "c", "h", "o", "r", "_s", "et"))
PAIR8 = frozenset(("a", "mo", "un", "t", "cu", "rr", "en", "cy"))
CLEAN8 = frozenset(("g", "ro", "un", "d", "_n", "ot", "es", "x"))
SHORT8 = frozenset(("g", "ro", "un", "d", "_t", "ru", "t", "x"))


class TestMod03BeyondBound(unittest.TestCase):

    def test_frozenset_eight_part_ground_truth(self):
        self.assertTrue(mod03._is_barred_key(GROUND8))

    def test_set_eight_part_ground_truth(self):
        self.assertTrue(mod03._is_barred_key(GROUND8_SET))

    def test_frozenset_twelve_part_ground_truth(self):
        self.assertTrue(mod03._is_barred_key(GROUND12))

    def test_frozenset_eight_part_bytes_ground_truth(self):
        self.assertTrue(mod03._is_barred_key(frozenset(
            (b"g", b"ro", b"un", b"d", b"_t", b"ru", b"t", b"h"))))

    def test_frozenset_eight_part_inside_tuple(self):
        self.assertTrue(mod03._is_barred_key((GROUND8, "x")))
        self.assertTrue(mod03._is_barred_key(("x", GROUND8)))

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod03._is_barred_key(CLEAN8))
        self.assertFalse(mod03._is_barred_key(SHORT8))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod03._is_barred_key(("ship", "member")))
        self.assertTrue(mod03._is_barred_key(("member", "ship")))


class TestMod04BeyondBound(unittest.TestCase):

    def test_frozenset_eight_part_ground_truth(self):
        self.assertTrue(mod04._is_barred_key(GROUND8))

    def test_set_eight_part_ground_truth(self):
        self.assertTrue(mod04._is_barred_key(GROUND8_SET))

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod04._is_barred_key(CLEAN8))
        self.assertFalse(mod04._is_barred_key(SHORT8))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod04._is_barred_key(("ship", "member")))


class TestMod05BeyondBound(unittest.TestCase):

    def test_frozenset_eight_part_ground_truth(self):
        self.assertTrue(mod05._panel_key_barred(GROUND8))

    def test_set_eight_part_ground_truth(self):
        self.assertTrue(mod05._panel_key_barred(GROUND8_SET))

    def test_public_gate_eight_part_ground_truth(self):
        self.assertFalse(mod05.validate_panel_inputs({GROUND8: 1}))
        self.assertTrue(mod05.validate_panel_inputs({CLEAN8: 1}))

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod05._panel_key_barred(CLEAN8))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod05._panel_key_barred(("ship", "member")))


class TestMod08BeyondBound(unittest.TestCase):

    def test_frozenset_eight_part_ground_truth(self):
        self.assertTrue(mod08._is_barred_key(GROUND8))

    def test_set_eight_part_ground_truth(self):
        self.assertTrue(mod08._is_barred_key(GROUND8_SET))

    def test_frozenset_eight_part_stake_held(self):
        self.assertTrue(mod08._is_barred_key(frozenset(
            ("s", "t", "a", "k", "e", "_h", "el", "d"))))

    def test_public_find_barred_eight_part(self):
        self.assertTrue(mod08._find_barred({GROUND8: 1}))
        self.assertFalse(mod08._find_barred({CLEAN8: 1}))

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod08._is_barred_key(CLEAN8))
        self.assertFalse(mod08._is_barred_key(SHORT8))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod08._is_barred_key(("ship", "member")))


class TestMod10BeyondBound(unittest.TestCase):

    def test_frozenset_eight_part_ground_truth(self):
        self.assertTrue(mod10._is_barred_view_key(GROUND8))

    def test_set_eight_part_ground_truth(self):
        self.assertTrue(mod10._is_barred_view_key(GROUND8_SET))

    def test_frozenset_twelve_part_ground_truth(self):
        self.assertTrue(mod10._is_barred_view_key(GROUND12))

    def test_carries_barred_eight_part(self):
        self.assertTrue(mod10._carries_barred_key({GROUND8: 1}))
        self.assertFalse(mod10._carries_barred_key({CLEAN8: 1}))

    def test_money_key_matches_eight_part_amount(self):
        self.assertTrue(mod10._money_key_matches(AMOUNT8, "amount"))

    def test_money_key_carries_eight_part_real_money(self):
        self.assertTrue(mod10._money_key_carries(REALMONEY8, "realmoney"))

    def test_carries_real_money_eight_part_pair(self):
        self.assertTrue(mod10._carries_real_money_field(
            {AMOUNT8: 10, CURRENCY8: "USD"}))

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod10._is_barred_view_key(CLEAN8))
        self.assertFalse(mod10._is_barred_view_key(SHORT8))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod10._is_barred_view_key(("ship", "member")))


class TestMod01BeyondBound(unittest.TestCase):

    def test_folded_key_matches_eight_part_amount(self):
        self.assertTrue(mod01._folded_key_matches(AMOUNT8, "amount"))

    def test_folded_key_carries_eight_part_real_money(self):
        self.assertTrue(mod01._folded_key_carries(REALMONEY8, "realmoney"))

    def test_carries_real_money_eight_part_pair(self):
        self.assertTrue(mod01._carries_real_money_value(
            {AMOUNT8: 10, CURRENCY8: "USD"}))

    def test_carries_real_money_eight_part_name(self):
        self.assertTrue(mod01._carries_real_money_value({REALMONEY8: 5}))

    def test_unordered_clean_past_bound_not_carried(self):
        self.assertFalse(mod01._carries_real_money_value({CLEAN8: 10}))
        self.assertFalse(mod01._carries_real_money_value(
            {frozenset(("a", "m", "ou", "n", "_", "-", " ", "x")): 10,
             CURRENCY8: "USD"}))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod01._folded_key_matches(("unt", "amo"), "amount"))


class TestMod06BeyondBound(unittest.TestCase):

    def test_key_reads_as_eight_part_amount(self):
        self.assertTrue(mod06._key_reads_as(AMOUNT8, "amount"))

    def test_key_reads_as_eight_part_real_money(self):
        self.assertTrue(mod06._key_reads_as(REALMONEY8, "realmoney"))

    def test_payload_eight_part_anchor_set_key(self):
        self.assertTrue(mod06._payload_carries_barred({ANCHOR8: ["x"]}))

    def test_payload_eight_part_real_money_key(self):
        self.assertTrue(mod06._payload_carries_barred({REAL_MONEY8: 10}))

    def test_payload_pair_split_across_one_eight_part_key(self):
        self.assertTrue(mod06._payload_carries_barred({PAIR8: 10}))

    def test_payload_eight_part_amount_and_currency_keys(self):
        self.assertTrue(mod06._payload_carries_barred(
            {AMOUNT8: 10, CURRENCY8: "USD"}))

    def test_public_gate_eight_part_pair(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "x", payload={AMOUNT8: 10, CURRENCY8: "USD"})

    def test_unordered_clean_past_bound_not_barred(self):
        self.assertFalse(mod06._payload_carries_barred({CLEAN8: 10}))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod06._key_reads_as(("unt", "amo"), "amount"))


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 10 Builder 14 (supplementary): the joined
reading of a barred name split across the parts of a set or
frozenset key must not depend on hash order or iteration order,
at MOD-01, MOD-03, MOD-04, MOD-05, MOD-06, MOD-08, and MOD-10,
under limb 3 of the Round 10 governing stored text settlement
and row R10-003 as graded PARTIAL on its unordered limb.
Ordered containers keep their exact standing behaviour."""
import unittest

from crucible import mod01, mod03, mod04, mod05, mod06, mod08, mod10


class TestMod03UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_membership(self):
        self.assertTrue(
            mod03._is_barred_key(frozenset(("member", "ship"))))

    def test_set_split_membership(self):
        self.assertTrue(mod03._is_barred_key({"member", "ship"}))

    def test_frozenset_split_ground_truth(self):
        self.assertTrue(
            mod03._is_barred_key(frozenset(("ground", "_truth"))))

    def test_frozenset_three_part_split(self):
        self.assertTrue(
            mod03._is_barred_key(frozenset(("mem", "ber", "ship"))))

    def test_frozenset_bytes_parts_split(self):
        self.assertTrue(
            mod03._is_barred_key(frozenset((b"member", b"ship"))))

    def test_frozenset_inside_tuple(self):
        self.assertTrue(mod03._is_barred_key(
            (frozenset(("member", "ship")), "x")))
        self.assertTrue(mod03._is_barred_key(
            ("x", frozenset(("member", "ship")))))

    def test_ordered_tuple_inside_frozenset(self):
        self.assertTrue(mod03._is_barred_key(
            frozenset((("member", "ship"), "x"))))

    def test_unordered_clean_not_barred(self):
        self.assertFalse(
            mod03._is_barred_key(frozenset(("member", "notes"))))
        self.assertFalse(
            mod03._is_barred_key(frozenset(("acti", "vity"))))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod03._is_barred_key(("ship", "member")))
        self.assertTrue(mod03._is_barred_key(("member", "ship")))


class TestMod04UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_membership(self):
        self.assertTrue(
            mod04._is_barred_key(frozenset(("member", "ship"))))

    def test_set_split_membership(self):
        self.assertTrue(mod04._is_barred_key({"member", "ship"}))

    def test_frozenset_three_part_split(self):
        self.assertTrue(
            mod04._is_barred_key(frozenset(("mem", "ber", "ship"))))

    def test_unordered_clean_not_barred(self):
        self.assertFalse(
            mod04._is_barred_key(frozenset(("member", "notes"))))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod04._is_barred_key(("ship", "member")))


class TestMod05UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_membership(self):
        self.assertTrue(
            mod05._panel_key_barred(frozenset(("member", "ship"))))

    def test_set_split_membership(self):
        self.assertTrue(mod05._panel_key_barred({"member", "ship"}))

    def test_frozenset_split_ground_truth(self):
        self.assertTrue(
            mod05._panel_key_barred(frozenset(("ground", "_truth"))))

    def test_public_gate_frozenset_split(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {frozenset(("member", "ship")): 1}))
        self.assertTrue(mod05.validate_panel_inputs(
            {frozenset(("acti", "vity")): 1}))

    def test_unordered_clean_not_barred(self):
        self.assertFalse(
            mod05._panel_key_barred(frozenset(("member", "notes"))))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod05._panel_key_barred(("ship", "member")))


class TestMod08UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_membership(self):
        self.assertTrue(
            mod08._is_barred_key(frozenset(("member", "ship"))))

    def test_set_split_membership(self):
        self.assertTrue(mod08._is_barred_key({"member", "ship"}))

    def test_frozenset_split_stake_held(self):
        self.assertTrue(
            mod08._is_barred_key(frozenset(("stake_", "held"))))

    def test_public_find_barred_frozenset_split(self):
        self.assertTrue(
            mod08._find_barred({frozenset(("member", "ship")): 1}))
        self.assertFalse(
            mod08._find_barred({frozenset(("acti", "vity")): 1}))

    def test_unordered_clean_not_barred(self):
        self.assertFalse(
            mod08._is_barred_key(frozenset(("member", "notes"))))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod08._is_barred_key(("ship", "member")))


class TestMod06UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_anchor_set_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {frozenset(("anchor", "_set")): ["x"]}))

    def test_frozenset_split_amount_and_currency_keys(self):
        self.assertTrue(mod06._payload_carries_barred(
            {frozenset(("amo", "unt")): 10,
             frozenset(("curr", "ency")): "USD"}))

    def test_pair_split_across_one_frozenset_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {frozenset(("amo", "unt", "curr", "ency")): 10}))

    def test_frozenset_split_real_money_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {frozenset(("real_", "money")): 10}))

    def test_key_reads_as_frozenset_split(self):
        self.assertTrue(
            mod06._key_reads_as(frozenset(("amo", "unt")), "amount"))
        self.assertTrue(mod06._key_reads_as(
            frozenset(("real_", "money")), "realmoney"))

    def test_public_gate_frozenset_split(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "x", payload={frozenset(("amo", "unt")): 10,
                              frozenset(("curr", "ency")): "USD"})

    def test_unordered_clean_not_barred(self):
        self.assertFalse(mod06._payload_carries_barred(
            {frozenset(("amo", "notes")): 10,
             frozenset(("curr", "notes")): "USD"}))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(
            mod06._key_reads_as(("unt", "amo"), "amount"))


class TestMod10UnorderedJoined(unittest.TestCase):

    def test_frozenset_split_membership(self):
        self.assertTrue(
            mod10._is_barred_view_key(frozenset(("member", "ship"))))

    def test_set_split_membership(self):
        self.assertTrue(mod10._is_barred_view_key({"member", "ship"}))

    def test_frozenset_split_ground_truth(self):
        self.assertTrue(mod10._is_barred_view_key(
            frozenset(("ground", "truth"))))

    def test_carries_barred_frozenset_split(self):
        self.assertTrue(mod10._carries_barred_key(
            {frozenset(("member", "ship")): 1}))

    def test_money_key_matches_frozenset_split(self):
        self.assertTrue(mod10._money_key_matches(
            frozenset(("amo", "unt")), "amount"))

    def test_money_key_carries_frozenset_split(self):
        self.assertTrue(mod10._money_key_carries(
            frozenset(("real_", "money")), "realmoney"))

    def test_carries_real_money_frozenset_pair(self):
        self.assertTrue(mod10._carries_real_money_field(
            {frozenset(("amo", "unt")): 10,
             frozenset(("curr", "ency")): "USD"}))

    def test_unordered_clean_not_barred(self):
        self.assertFalse(
            mod10._is_barred_view_key(frozenset(("member", "notes"))))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(mod10._is_barred_view_key(("ship", "member")))


class TestMod01UnorderedJoined(unittest.TestCase):

    def test_folded_key_matches_frozenset_split(self):
        self.assertTrue(mod01._folded_key_matches(
            frozenset(("amo", "unt")), "amount"))

    def test_folded_key_carries_frozenset_split(self):
        self.assertTrue(mod01._folded_key_carries(
            frozenset(("real_", "money")), "realmoney"))

    def test_carries_real_money_frozenset_pair(self):
        self.assertTrue(mod01._carries_real_money_value(
            {frozenset(("amo", "unt")): 10,
             frozenset(("curr", "ency")): "USD"}))

    def test_carries_real_money_frozenset_name(self):
        self.assertTrue(mod01._carries_real_money_value(
            {frozenset(("real_", "money")): 5}))

    def test_unordered_clean_not_carried(self):
        self.assertFalse(mod01._carries_real_money_value(
            {frozenset(("amo", "notes")): 10,
             frozenset(("curr", "notes")): "USD"}))

    def test_ordered_tuple_reversed_stays_clean(self):
        self.assertFalse(
            mod01._folded_key_matches(("unt", "amo"), "amount"))


if __name__ == "__main__":
    unittest.main()

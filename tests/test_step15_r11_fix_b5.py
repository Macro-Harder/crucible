"""Pins for fix wave 10 Builder 5: the joined container reading
and the memoryview and bytearray helper limb at MOD-05, MOD-06,
and MOD-08, under limbs 3, 5, and 6 of the Round 10 governing
stored text settlement. Rows R10-003, R10-006 (MOD-06 limb),
R10-007, and R10-008 (iterative limbs at these modules)."""
import unittest

from crucible import mod05, mod06, mod08


def _nest(leaf, depth):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


class TestStoredTextHelperForms(unittest.TestCase):
    """R10-007, limb 6: the helpers decode bytes, bytearray, and
    memoryview on their stored bytes at all three modules."""

    def test_helper_decodes_memoryview(self):
        for module in (mod05, mod06, mod08):
            self.assertEqual(
                "membership",
                module._stored_text(memoryview(b"membership")))

    def test_helper_decodes_bytearray(self):
        for module in (mod05, mod06, mod08):
            self.assertEqual(
                "membership",
                module._stored_text(bytearray(b"membership")))

    def test_helper_decodes_bytes_control(self):
        for module in (mod05, mod06, mod08):
            self.assertEqual(
                "membership", module._stored_text(b"membership"))

    def test_helper_memoryview_drops_undecodable(self):
        for module in (mod05, mod06, mod08):
            self.assertEqual(
                "ab", module._stored_text(memoryview(b"a\xffb")))


class TestMod05Joined(unittest.TestCase):
    """R10-003 at MOD-05: a barred name split across the parts of
    one container key stands barred under the joined reading."""

    def test_split_membership_tuple(self):
        self.assertTrue(mod05._panel_key_barred(("member", "ship")))

    def test_split_ground_truth_tuple(self):
        self.assertTrue(mod05._panel_key_barred(("ground", "_truth")))

    def test_split_is_honest_tuple(self):
        self.assertTrue(mod05._panel_key_barred(("is_", "honest")))

    def test_split_across_bytes_parts(self):
        self.assertTrue(mod05._panel_key_barred((b"member", b"ship")))

    def test_split_list_and_frozenset(self):
        self.assertTrue(mod05._panel_key_barred(["member", "ship"]))
        self.assertTrue(
            mod05._panel_key_barred(frozenset(("member", "ship"))))

    def test_split_nested_container(self):
        self.assertTrue(
            mod05._panel_key_barred((("member", "ship"), "x")))
        self.assertTrue(
            mod05._panel_key_barred(("x", ("member", "ship"))))

    def test_single_part_container_control(self):
        self.assertTrue(mod05._panel_key_barred(("membership",)))
        self.assertFalse(mod05._panel_key_barred(("activity",)))

    def test_joined_clean_not_barred(self):
        self.assertFalse(mod05._panel_key_barred(("member", "notes")))
        self.assertFalse(mod05._panel_key_barred(("acti", "vity")))

    def test_public_gate_split_key(self):
        self.assertFalse(
            mod05.validate_panel_inputs({("member", "ship"): 1}))
        self.assertTrue(
            mod05.validate_panel_inputs({("acti", "vity"): 1}))


class TestMod05MemoryviewAndBytearray(unittest.TestCase):
    """R10-007 at MOD-05."""

    def test_memoryview_key_barred(self):
        self.assertTrue(
            mod05._panel_key_barred(memoryview(b"membership")))

    def test_memoryview_parts_joined_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            (memoryview(b"member"), memoryview(b"ship"))))

    def test_bytearray_inside_container_barred(self):
        self.assertTrue(
            mod05._panel_key_barred((bytearray(b"membership"),)))

    def test_bytearray_key_barred(self):
        self.assertTrue(
            mod05._panel_key_barred(bytearray(b"membership")))

    def test_public_gate_memoryview_key(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {memoryview(b"membership"): 1}))
        self.assertTrue(mod05.validate_panel_inputs(
            {memoryview(b"activity"): 1}))


class TestMod08Joined(unittest.TestCase):
    """R10-003 at MOD-08."""

    def test_split_membership_tuple(self):
        self.assertTrue(mod08._is_barred_key(("member", "ship")))

    def test_split_ground_truth_tuple(self):
        self.assertTrue(mod08._is_barred_key(("ground", "_truth")))

    def test_split_stake_held_tuple(self):
        self.assertTrue(mod08._is_barred_key(("stake_", "held")))

    def test_split_canary_tuple(self):
        self.assertTrue(mod08._is_barred_key(("can", "ary")))

    def test_split_across_bytes_parts(self):
        self.assertTrue(mod08._is_barred_key((b"member", b"ship")))

    def test_split_nested_container(self):
        self.assertTrue(
            mod08._is_barred_key((("stake_", "held"), "x")))
        self.assertTrue(
            mod08._is_barred_key(("x", ("member", "ship"))))

    def test_joined_clean_not_barred(self):
        self.assertFalse(mod08._is_barred_key(("member", "notes")))
        self.assertFalse(mod08._is_barred_key(("acti", "vity")))

    def test_public_find_barred_split_key(self):
        self.assertTrue(mod08._find_barred({("member", "ship"): 1}))
        self.assertFalse(mod08._find_barred({("acti", "vity"): 1}))


class TestMod08MemoryviewAndBytearray(unittest.TestCase):
    """R10-007 at MOD-08."""

    def test_memoryview_key_barred(self):
        self.assertTrue(
            mod08._is_barred_key(memoryview(b"membership")))

    def test_memoryview_parts_joined_barred(self):
        self.assertTrue(mod08._is_barred_key(
            (memoryview(b"member"), memoryview(b"ship"))))

    def test_bytearray_inside_container_barred(self):
        self.assertTrue(
            mod08._is_barred_key((bytearray(b"membership"),)))

    def test_bytearray_key_barred(self):
        self.assertTrue(
            mod08._is_barred_key(bytearray(b"membership")))

    def test_public_find_barred_memoryview_key(self):
        self.assertTrue(
            mod08._find_barred({memoryview(b"membership"): 1}))
        self.assertFalse(
            mod08._find_barred({memoryview(b"activity"): 1}))


class TestMod06JoinedMoney(unittest.TestCase):
    """R10-003 and the MOD-06 limb of R10-006, limb 5: a money
    pair or marker split across the parts of one container key,
    or in single part container dress, stands barred at MOD-06
    as the plain and bytes forms already stand barred."""

    def test_split_amount_and_currency_keys(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("amo", "unt"): 10, ("curr", "ency"): "USD"}))

    def test_split_amount_plain_currency(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 10, ("cur", "rency"): "USD"}))

    def test_pair_split_across_one_container_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("amo", "unt", "curr", "ency"): 10}))

    def test_split_real_money_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("real_", "money"): 10}))
        self.assertTrue(mod06._payload_carries_barred(
            {("real", "_money"): 10}))

    def test_split_anchor_set_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("anchor", "_set"): ["x"]}))
        self.assertTrue(mod06._payload_carries_barred(
            {("anch", "or_set"): ["x"]}))

    def test_single_part_container_money_keys(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("amount",): 10, ("currency",): "USD"}))
        self.assertTrue(mod06._key_reads_as(("amount",), "amount"))
        self.assertTrue(mod06._key_reads_as(("amo", "unt"), "amount"))

    def test_public_escrow_result_split_payload_refused(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "x", payload={("amo", "unt"): 10,
                              ("curr", "ency"): "USD"})
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "x", payload={("anchor", "_set"): ["x"]})

    def test_joined_clean_not_barred(self):
        self.assertFalse(mod06._payload_carries_barred(
            {("amo", "notes"): 10, ("curr", "notes"): "USD"}))
        self.assertFalse(mod06._payload_carries_barred(
            {("real_", "notes"): 10}))
        self.assertFalse(mod06._payload_carries_barred(
            {("activity", "x"): 1}))


class TestMod06MemoryviewAndBytearray(unittest.TestCase):
    """R10-007 and the MOD-06 limb of R10-006, limbs 5 and 6."""

    def test_memoryview_amount_currency_pair(self):
        self.assertTrue(mod06._payload_carries_barred(
            {memoryview(b"amount"): 10,
             memoryview(b"currency"): "USD"}))

    def test_memoryview_container_parts_amount(self):
        self.assertTrue(mod06._payload_carries_barred(
            {(memoryview(b"amount"),): 10, "currency": "USD"}))

    def test_memoryview_anchor_set_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {memoryview(b"anchor_set"): ["x"]}))

    def test_bytearray_inside_container_real_money(self):
        self.assertTrue(mod06._key_reads_as(
            (bytearray(b"real_money"),), "realmoney"))

    def test_memoryview_split_parts_joined(self):
        self.assertTrue(mod06._payload_carries_barred(
            {(memoryview(b"amo"), memoryview(b"unt")): 10,
             "currency": "USD"}))


class TestDeepContainerStanding(unittest.TestCase):
    """R10-008 limbs at these modules: the container limbs walk
    their parts on an explicit stack and answer at depth 2000
    both ways, with the joined reading in force at depth."""

    def test_mod05_deep_2000_both_ways(self):
        self.assertTrue(
            mod05._panel_key_barred(_nest("membership", 2000)))
        self.assertFalse(
            mod05._panel_key_barred(_nest("activity", 2000)))

    def test_mod08_deep_2000_both_ways(self):
        self.assertTrue(
            mod08._is_barred_key(_nest("membership", 2000)))
        self.assertFalse(
            mod08._is_barred_key(_nest("activity", 2000)))

    def test_mod05_joined_at_depth(self):
        self.assertTrue(mod05._panel_key_barred(
            _nest(("member", "ship"), 200)))

    def test_mod08_joined_at_depth(self):
        self.assertTrue(mod08._is_barred_key(
            _nest(("member", "ship"), 200)))

    def test_mod06_deep_key_both_ways(self):
        barred_forms = mod06._key_and_parts(_nest("anchor_set", 2000))
        self.assertIn("anchor_set", barred_forms)
        clean_forms = mod06._key_and_parts(_nest("activity", 2000))
        self.assertIn("activity", clean_forms)
        self.assertNotIn("anchor_set", clean_forms)
        self.assertTrue(mod06._payload_carries_barred(
            {_nest("anchor_set", 90): 1}))
        self.assertFalse(mod06._payload_carries_barred(
            {_nest("activity", 90): 1}))

    def test_mod06_joined_at_depth(self):
        self.assertTrue(mod06._payload_carries_barred(
            {_nest(("anchor", "_set"), 90): ["x"]}))


if __name__ == "__main__":
    unittest.main()

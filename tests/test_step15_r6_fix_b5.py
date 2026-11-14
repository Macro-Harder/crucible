"""Pins for fix wave 5, MOD-06 items R5-015 and R5-034 MOD-06 limb.

Each test states its distinguishing case with controls both ways:
the dressed form the register charges, the plain form that
already stands refused or accepted, and a clean form that must
keep its standing.
"""

import unittest

from crucible import mod06

_EN = "\u043d"
_ES = "\u0441"

# R5-015, variant generation limb: anchor_set needing the
# homoglyph reading c of Cyrillic es at its c position and the
# multi reading n of Cyrillic en at its n position.
_COMPOSITE_MULTI = "a" + _EN + _ES + "hor_set"

# R5-015, fold combination limb: anchor_set needing the homoglyph
# reading c of the first Cyrillic es and the transliteration
# reading s of the second.
_COMPOSITE_FOLD = "an" + _ES + "hor_" + _ES + "et"

# R5-015, excluded profile limb: backup extended profile needing
# the homoglyph reading c of Cyrillic es in backup and the multi
# reading n of Cyrillic en in extended.
_COMPOSITE_PROFILE = "ba" + _ES + "kup exte" + _EN + "ded profile"


def _hand_built_result(payload):
    return {
        "core_only_qualifier": True,
        "verification_limit": mod06.VERIFICATION_LIMIT,
        "k1_and_l2_state": "carried",
        "real_money_value": None,
        "payload": payload,
    }


class TestR5015VariantGenerationLimb(unittest.TestCase):

    def test_composite_key_reads_as_anchor_set(self):
        self.assertIn("anchorset", mod06._folded_readings(_COMPOSITE_MULTI))
        self.assertTrue(mod06._key_reads_as(_COMPOSITE_MULTI, "anchorset"))

    def test_composite_key_barred_at_payload_screen(self):
        self.assertTrue(
            mod06._payload_carries_barred({_COMPOSITE_MULTI: [1]}))

    def test_composite_key_refused_by_escrow_result(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={_COMPOSITE_MULTI: [1]})

    def test_composite_key_rejected_by_validate_escrow_result(self):
        delivered = _hand_built_result({_COMPOSITE_MULTI: [1]})
        self.assertFalse(mod06.validate_escrow_result(delivered))

    def test_composite_key_behind_multi_prefixes_is_barred(self):
        for count in (11, 15):
            key = _EN * count + _COMPOSITE_MULTI
            self.assertTrue(
                mod06._payload_carries_barred({key: [1]}), count)
            with self.assertRaises(ValueError):
                mod06.escrow_result("k", payload={key: [1]})
            self.assertFalse(
                mod06.validate_escrow_result(
                    _hand_built_result({key: [1]})), count)


class TestR5015ExcludedProfileLimb(unittest.TestCase):

    def test_composite_profile_reads_as_excluded(self):
        self.assertTrue(
            mod06._reads_as_excluded_profile(_COMPOSITE_PROFILE))

    def test_composite_profile_raises_excluded_subpath(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(_COMPOSITE_PROFILE)


class TestR5015FoldCombinationLimb(unittest.TestCase):

    def test_fold_composite_key_reads_as_anchor_set(self):
        self.assertIn("anchorset", mod06._folded_readings(_COMPOSITE_FOLD))
        self.assertTrue(mod06._key_reads_as(_COMPOSITE_FOLD, "anchorset"))

    def test_fold_composite_key_barred_at_payload_screen(self):
        self.assertTrue(
            mod06._payload_carries_barred({_COMPOSITE_FOLD: [1]}))

    def test_fold_composite_key_refused_by_escrow_result(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={_COMPOSITE_FOLD: [1]})

    def test_fold_composite_key_rejected_by_validate(self):
        delivered = _hand_built_result({_COMPOSITE_FOLD: [1]})
        self.assertFalse(mod06.validate_escrow_result(delivered))


class TestR5034SmallCapitalReadings(unittest.TestCase):

    def test_small_capital_e_dress_of_anchor_set_is_barred(self):
        key = "anchor_s\u1d31t"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={key: [1]})
        self.assertFalse(
            mod06.validate_escrow_result(_hand_built_result({key: [1]})))

    def test_small_capital_o_dress_of_anchor_set_is_barred(self):
        key = "anch\u1d3cr_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={key: [1]})
        self.assertFalse(
            mod06.validate_escrow_result(_hand_built_result({key: [1]})))

    def test_small_capital_t_dress_of_anchor_set_is_barred(self):
        key = "anchor_se\u1d40"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={key: [1]})
        self.assertFalse(
            mod06.validate_escrow_result(_hand_built_result({key: [1]})))

    def test_small_capital_readings_recorded_in_fold(self):
        self.assertIn("e", mod06._folded_readings("\u1d31"))
        self.assertIn("o", mod06._folded_readings("\u1d3c"))
        self.assertIn("t", mod06._folded_readings("\u1d40"))

    def test_small_capital_l_reading_recorded_in_fold(self):
        # The barred vocabulary of this module holds no word with
        # an l position, so this reading stands pinned at the fold
        # itself and at no barred surface.
        self.assertIn("l", mod06._folded_readings("\u1d38"))


class TestControlsBothWays(unittest.TestCase):

    def test_plain_barred_forms_stand_barred(self):
        self.assertTrue(mod06._payload_carries_barred({"anchor_set": [1]}))
        self.assertTrue(mod06._payload_carries_barred({"real_money": 5}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={"anchor_set": [1]})

    def test_homoglyph_dress_alone_stands_barred(self):
        key = "an" + _ES + "hor_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))

    def test_multi_dress_alone_stands_barred(self):
        key = "a" + _EN + "chor_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))

    def test_two_multi_positions_stand_barred(self):
        key = "a" + _EN + "c" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))

    def test_amount_currency_pair_in_single_dress_stands_barred(self):
        payload = {"amou" + _EN + "t": 5, _ES + "urrency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_excluded_profile_plain_and_single_dresses(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup extended profile")
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("ba" + _ES + "kup extended profile")
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup exte" + _EN + "ded profile")

    def test_clean_forms_stand_admitted(self):
        for key in ("honest", "blorple_set", "summary_set"):
            self.assertFalse(
                mod06._payload_carries_barred({key: 1}), key)
            result = mod06.escrow_result("k", payload={key: 1})
            self.assertTrue(mod06.validate_escrow_result(result), key)

    def test_small_capital_dress_of_clean_key_stands_admitted(self):
        key = "hon\u1d31st"
        self.assertFalse(mod06._payload_carries_barred({key: 1}))
        result = mod06.escrow_result("k", payload={key: 1})
        self.assertTrue(mod06.validate_escrow_result(result))


if __name__ == "__main__":
    unittest.main()

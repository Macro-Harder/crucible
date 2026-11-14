"""Pins for the Step 15 fix wave 4 items charged to this seat on
MOD-05: the MOD-05 limb of R4-015 and the MOD-05 limb of R4-018.
Each distinguishing pin stands in the composite form that needs
two different letter readings inside one word, with plain
controls, single reading controls, and clean controls beside it.
"""

import unittest

from crucible import mod05


# R4-015 composite: the word membership spelled with Cyrillic es
# U+0441 at the s position, which needs its transliteration
# reading s, and Cyrillic er U+0440 at the p position, which
# needs its homoglyph reading p. No single whole map reading
# spells the word: the homoglyph map alone gives memberchip and
# the transliteration map alone gives membershir.
COMPOSITE_MEMBERSHIP = "member\u0441hi\u0440"

# R4-018 composite: the key is_honest spelled with Cyrillic en
# U+043D at the h position, which needs its homoglyph reading h,
# and Cyrillic en U+043D at the n position, which needs its
# transliteration reading n. The homoglyph map alone gives
# ishohest and the transliteration map alone gives isnonest.
COMPOSITE_IS_HONEST = "is_\u043do\u043dest"


def adjudicate_kwargs():
    return {
        "accuracy_value": 0.5,
        "assumption_set": "assumption-set-1",
        "row": "row-1",
        "error_direction": "over",
        "outcome": "slashable",
    }


class TestR4015CompositeMembershipFold(unittest.TestCase):
    def test_folded_readings_combine_both_readings(self):
        self.assertIn("membership", mod05._folded_readings(COMPOSITE_MEMBERSHIP))

    def test_composite_key_reads_barred(self):
        self.assertTrue(mod05._panel_key_barred(COMPOSITE_MEMBERSHIP))

    def test_composite_key_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs({COMPOSITE_MEMBERSHIP: 1}))

    def test_composite_key_removed_by_former(self):
        formed = mod05.panel_inputs({COMPOSITE_MEMBERSHIP: 1, "keep": 1})
        self.assertEqual(formed, {"keep": 1})

    def test_composite_key_barred_at_depth(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"outer": {COMPOSITE_MEMBERSHIP: 1}}))

    def test_composite_key_inside_container_key_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({(COMPOSITE_MEMBERSHIP, "x"): 1}))

    def test_adjudicate_refuses_composite_key(self):
        case = {"case_identifier": "c1", COMPOSITE_MEMBERSHIP: 1}
        with self.assertRaises(ValueError):
            mod05.adjudicate(case, **adjudicate_kwargs())

    def test_plain_membership_control_still_barred(self):
        self.assertFalse(mod05.validate_panel_inputs({"membership": 1}))

    def test_transliteration_position_alone_control_still_barred(self):
        key = "member\u0441hip"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))

    def test_homoglyph_position_alone_control_still_barred(self):
        key = "membershi\u0440"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))

    def test_clean_controls_pass(self):
        self.assertTrue(mod05.validate_panel_inputs({"clean": 1}))
        self.assertTrue(mod05.validate_panel_inputs({"member": 1}))
        self.assertEqual(
            mod05.panel_inputs({"clean": 1, "member": 2}),
            {"clean": 1, "member": 2})

    def test_near_miss_spelling_control_passes(self):
        self.assertTrue(mod05.validate_panel_inputs({"memberchip": 1}))
        self.assertTrue(mod05.validate_panel_inputs({"membershir": 1}))


class TestR4018CompositeIsHonestFold(unittest.TestCase):
    def test_folded_readings_combine_both_readings(self):
        self.assertIn("ishonest", mod05._folded_readings(COMPOSITE_IS_HONEST))

    def test_composite_key_reads_barred(self):
        self.assertTrue(mod05._panel_key_barred(COMPOSITE_IS_HONEST))

    def test_composite_key_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs({COMPOSITE_IS_HONEST: 1}))

    def test_composite_key_removed_by_former(self):
        formed = mod05.panel_inputs({COMPOSITE_IS_HONEST: 1, "keep": 1})
        self.assertEqual(formed, {"keep": 1})

    def test_composite_key_barred_at_depth(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"outer": [{COMPOSITE_IS_HONEST: 1}]}))

    def test_adjudicate_refuses_composite_key(self):
        case = {"case_identifier": "c1", COMPOSITE_IS_HONEST: 1}
        with self.assertRaises(ValueError):
            mod05.adjudicate(case, **adjudicate_kwargs())

    def test_plain_is_honest_control_still_barred(self):
        self.assertFalse(mod05.validate_panel_inputs({"is_honest": 1}))

    def test_h_position_alone_control_still_barred(self):
        key = "is_\u043donest"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))

    def test_n_position_alone_control_still_barred(self):
        key = "is_ho\u043dest"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))

    def test_clean_controls_pass(self):
        self.assertTrue(mod05.validate_panel_inputs({"honest": 1}))
        self.assertTrue(mod05.validate_panel_inputs({"clean": 1}))
        self.assertEqual(
            mod05.panel_inputs({"honest": 1}), {"honest": 1})

    def test_near_miss_spelling_control_passes(self):
        self.assertTrue(mod05.validate_panel_inputs({"ishohest": 1}))
        self.assertTrue(mod05.validate_panel_inputs({"isnonest": 1}))

    def test_sleeper_word_outside_panel_vocabulary_control(self):
        # The register states the sleeper limb of R4-018 stands at
        # MOD-03 and MOD-04 only, sleeper standing in no MOD-05
        # panel vocabulary, so the same composite dress of that
        # word states no barred key at this surface.
        key = "slee\u0440e\u0440"
        self.assertTrue(mod05.validate_panel_inputs({key: 1}))


if __name__ == "__main__":
    unittest.main()

"""Pins for the Step 15 fix wave 5 items charged to this seat on
MOD-05: the MOD-05 limb of R5-013, row R5-014, and the MOD-05
limb of R5-034. Each defect pin stands in the form the Round 5
register states for its row, with plain controls, inside bound
controls, and clean controls beside it.
"""

import unittest

from crucible import mod05


# The mixed reading membership core of row R5-013: m, e, m, b, e,
# Cyrillic er U+0440 at the r position needing its transliteration
# reading r, Cyrillic es U+0441 at the s position needing its
# transliteration reading s, Cyrillic en U+043D at the h position
# needing its homoglyph reading h, plain i, and Cyrillic er
# U+0440 at the p position needing its homoglyph reading p. The
# same letter U+0440 therefore needs two readings at two
# positions in the core.
MIXED_CORE = "membe\u0440\u0441\u043di\u0440"

SHORT_I_FILLER = "\u0439" * 13
CHI_FILLER = "\u03c7" * 13

# A uniform homoglyph dress of membership: Cyrillic ie U+0435 at
# both e positions and Cyrillic er U+0440 at the p position. One
# whole map reading spells the word, so the whole map fallback
# bars this dress at any filler size.
HOMOGLYPH_MEMBERSHIP = "m\u0435mb\u0435rshi\u0440"

# The composite membership key of row R5-014: membership spelled
# with Cyrillic es U+0441 at the s position, needing its
# transliteration reading, and Cyrillic er U+0440 at the p
# position, needing its homoglyph reading.
COMPOSITE_MEMBERSHIP = "member\u0441hi\u0440"

ER_FILLER = "\u0440"


class TestR5013CombinedBoundBasis(unittest.TestCase):
    def test_core_alone_barred(self):
        self.assertTrue(mod05._panel_key_barred(MIXED_CORE))

    def test_core_with_short_i_filler_barred(self):
        self.assertTrue(
            mod05._panel_key_barred(MIXED_CORE + SHORT_I_FILLER))

    def test_core_with_short_i_filler_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {MIXED_CORE + SHORT_I_FILLER: 1}))

    def test_core_with_chi_filler_barred(self):
        self.assertTrue(
            mod05._panel_key_barred(MIXED_CORE + CHI_FILLER))

    def test_core_with_chi_filler_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {MIXED_CORE + CHI_FILLER: 1}))

    def test_plain_membership_barred(self):
        self.assertTrue(mod05._panel_key_barred("membership"))

    def test_homoglyph_dress_with_short_i_filler_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            HOMOGLYPH_MEMBERSHIP + SHORT_I_FILLER))

    def test_homoglyph_dress_with_chi_filler_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            HOMOGLYPH_MEMBERSHIP + CHI_FILLER))

    def test_clean_key_with_short_i_filler_admitted(self):
        self.assertFalse(
            mod05._panel_key_barred("activity" + SHORT_I_FILLER))

    def test_clean_key_with_chi_filler_admitted(self):
        self.assertFalse(
            mod05._panel_key_barred("activity" + CHI_FILLER))


class TestR5014CombinationFallback(unittest.TestCase):
    def test_composite_alone_barred(self):
        self.assertTrue(mod05._panel_key_barred(COMPOSITE_MEMBERSHIP))

    def test_composite_behind_9_fillers_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            ER_FILLER * 9 + "_" + COMPOSITE_MEMBERSHIP))

    def test_composite_behind_10_fillers_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            ER_FILLER * 10 + "_" + COMPOSITE_MEMBERSHIP))

    def test_composite_behind_11_fillers_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            ER_FILLER * 11 + "_" + COMPOSITE_MEMBERSHIP))

    def test_composite_behind_12_fillers_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            ER_FILLER * 12 + "_" + COMPOSITE_MEMBERSHIP))

    def test_composite_behind_11_fillers_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {ER_FILLER * 11 + "_" + COMPOSITE_MEMBERSHIP: 1}))

    def test_composite_behind_11_fillers_removed_by_former(self):
        formed = mod05.panel_inputs(
            {ER_FILLER * 11 + "_" + COMPOSITE_MEMBERSHIP: 1, "keep": 2})
        self.assertEqual(formed, {"keep": 2})

    def test_composite_behind_12_fillers_at_depth_barred(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {"outer": {ER_FILLER * 12 + "_" + COMPOSITE_MEMBERSHIP: 1}}))

    def test_plain_membership_behind_11_fillers_barred(self):
        self.assertTrue(mod05._panel_key_barred(
            ER_FILLER * 11 + "_" + "membership"))

    def test_clean_key_behind_11_fillers_admitted(self):
        key = ER_FILLER * 11 + "_" + "clean"
        self.assertFalse(mod05._panel_key_barred(key))
        self.assertTrue(mod05.validate_panel_inputs({key: 1}))


class TestR5034ModifierSmallCapitals(unittest.TestCase):
    def test_small_capital_e_reading_barred(self):
        self.assertTrue(mod05._panel_key_barred("memb\u1d31rship"))

    def test_small_capital_e_reading_in_folded_readings(self):
        self.assertIn(
            "membership", mod05._folded_readings("memb\u1d31rship"))

    def test_small_capital_l_reading_barred(self):
        self.assertTrue(mod05._panel_key_barred("\u1d38abel"))

    def test_small_capital_o_reading_barred(self):
        self.assertTrue(mod05._panel_key_barred("gr\u1d3cund_truth"))

    def test_small_capital_t_reading_barred(self):
        self.assertTrue(mod05._panel_key_barred("ground_\u1d40ruth"))

    def test_plain_membership_barred_control(self):
        self.assertTrue(mod05._panel_key_barred("membership"))

    def test_plain_label_barred_control(self):
        self.assertTrue(mod05._panel_key_barred("label"))

    def test_clean_key_with_small_capital_e_admitted(self):
        self.assertFalse(mod05._panel_key_barred("cl\u1d31an"))

    def test_plain_clean_key_admitted(self):
        self.assertFalse(mod05._panel_key_barred("hello"))


if __name__ == "__main__":
    unittest.main()

"""Fix wave 8 pins, Builder 3: MOD-03 rows R8-016, R8-017, and
the MOD-03 limb of row R8-007.

Row R8-016: the letter maps record no reading for the Cyrillic
hard sign and soft sign, in lower and upper case, which every
sister map records as an empty reading, so a barred key carrying
one of those signs inside the barred word escapes at MOD-03.
Row R8-017: Greek phi stands recorded only under its f reading
with no ph reading for any of its five forms, so a membership
key dressed with phi at its p position escapes at MOD-03.
Row R8-007, MOD-03 limb: the barred key fold takes a handed text
from the plain str call at _canonical_text, _folded_readings,
_combined_key_barred, and _is_barred_key, so a string subclass
storing a barred name while its string reading reports another
name stands judged as the reported name.
Each defect method fails on the uncured module and passes on
the cured module. Control methods pass both ways.
"""
import unittest

from crucible import mod03


class LieStr(str):
    """A text value storing one text while its string reading
    reports another. Its hash stands as the base string hash of
    the stored text."""

    def __new__(cls, stored, reported):
        instance = str.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class LowerLieStr(str):
    """A text value whose lower and casefold readings alone lie,
    with no string reading override, while the text it stores
    stands as given."""

    def lower(self):
        return "figure"

    def casefold(self):
        return "figure"


HARD_LOWER = "ъ"
SOFT_LOWER = "ь"
HARD_UPPER = "Ъ"
SOFT_UPPER = "Ь"
PHI_FORMS = ("Φ", "φ", "ϕ", "ᵠ", "ᵩ")
THETA = "θ"


class TestR8016SignReadings(unittest.TestCase):

    def test_defect_hard_sign_lower_inside_membership(self):
        key = "member" + HARD_LOWER + "ship"
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(
            mod03.record_carries_ground_truth({"a": {key: 1}}))

    def test_defect_soft_sign_lower_inside_membership(self):
        key = "member" + SOFT_LOWER + "ship"
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(
            mod03.record_carries_ground_truth({"a": {key: 1}}))

    def test_defect_hard_sign_upper_inside_membership(self):
        key = "member" + HARD_UPPER + "ship"
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_soft_sign_upper_inside_membership(self):
        key = "member" + SOFT_UPPER + "ship"
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_sign_readings_recorded_empty_in_all_maps(self):
        for sign in (HARD_LOWER, SOFT_LOWER, HARD_UPPER,
                     SOFT_UPPER):
            for letter_map in (mod03._HOMOGLYPH_MAP,
                               mod03._WIDE_LETTER_MAP,
                               mod03._ALT_LETTER_MAP):
                self.assertEqual("", letter_map.get(sign))

    def test_defect_sign_dress_past_the_bound(self):
        key = THETA * 13 + "member" + SOFT_LOWER + "ship"
        self.assertTrue(mod03._is_barred_key(key))

    def test_control_plain_membership_barred(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertTrue(
            mod03.record_carries_ground_truth(
                {"a": {"membership": 1}}))

    def test_control_sign_inside_clean_word_admitted(self):
        key = "activ" + HARD_LOWER + "ity"
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod03._combined_key_barred(key))
        self.assertFalse(
            mod03.record_carries_ground_truth({"a": {key: 1}}))

    def test_control_sign_at_word_edges_still_barred(self):
        self.assertTrue(
            mod03._is_barred_key(SOFT_LOWER + "membership"))
        self.assertTrue(
            mod03._is_barred_key("membership" + SOFT_LOWER))


class TestR8017PhiReadings(unittest.TestCase):

    def test_defect_phi_capital_at_p_position(self):
        key = "membershi" + PHI_FORMS[0]
        self.assertEqual(
            {"f", "ph"}, mod03._character_variants(PHI_FORMS[0]))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_phi_small_at_p_position(self):
        key = "membershi" + PHI_FORMS[1]
        self.assertEqual(
            {"f", "ph"}, mod03._character_variants(PHI_FORMS[1]))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(
            mod03.record_carries_ground_truth({"a": {key: 1}}))

    def test_defect_phi_symbol_at_p_position(self):
        key = "membershi" + PHI_FORMS[2]
        self.assertEqual(
            {"f", "ph"}, mod03._character_variants(PHI_FORMS[2]))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_phi_modifier_at_p_position(self):
        key = "membershi" + PHI_FORMS[3]
        self.assertEqual(
            {"f", "ph"}, mod03._character_variants(PHI_FORMS[3]))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_phi_modifier_small_at_p_position(self):
        key = "membershi" + PHI_FORMS[4]
        self.assertEqual(
            {"f", "ph"}, mod03._character_variants(PHI_FORMS[4]))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_phi_dress_past_the_bound(self):
        key = THETA * 13 + "membershi" + PHI_FORMS[1]
        self.assertTrue(mod03._is_barred_key(key))

    def test_control_phi_at_h_position_admitted(self):
        self.assertFalse(
            mod03._is_barred_key("members" + PHI_FORMS[1] + "ip"))

    def test_control_clean_word_carrying_phi_admitted(self):
        self.assertFalse(
            mod03._is_barred_key("gra" + PHI_FORMS[1] + "e"))

    def test_control_near_miss_membershi_q_admitted(self):
        self.assertFalse(mod03._is_barred_key("membershiq"))
        self.assertFalse(mod03._combined_key_barred("membershiq"))

    def test_control_phi_f_reading_still_barred(self):
        self.assertTrue(
            mod03._is_barred_key("is_" + PHI_FORMS[1] + "arm"))


class TestR8007HandedTextFold(unittest.TestCase):

    def test_defect_canonical_text_reads_stored_characters(self):
        key = LieStr("membership", "activity")
        self.assertEqual(
            "membership", mod03._canonical_text(key))

    def test_defect_folded_readings_read_stored_characters(self):
        key = LieStr("membership", "activity")
        self.assertIn("membership", mod03._folded_readings(key))
        self.assertNotIn("activity", mod03._folded_readings(key))

    def test_defect_combined_key_barred_reads_stored(self):
        key = LieStr("membership", "activity")
        self.assertTrue(mod03._combined_key_barred(key))

    def test_defect_is_barred_key_storing_membership(self):
        key = LieStr("membership", "activity")
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_is_barred_key_storing_canary(self):
        key = LieStr("canary", "activity")
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_is_barred_key_storing_ground_truth(self):
        key = LieStr("ground_truth", "figure")
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_public_acts_judge_the_stored_name(self):
        key = LieStr("ground_truth", "figure")
        record = {"a": {key: 1}}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertFalse(mod03.validate_detection_input(record))
        self.assertEqual({"a": {}}, mod03.strip_ground_truth(record))

    def test_defect_reverse_direction_judged_as_stored(self):
        key = LieStr("activity", "membership")
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod03._combined_key_barred(key))
        record = {"a": {key: 1}}
        self.assertFalse(mod03.record_carries_ground_truth(record))
        self.assertTrue(mod03.validate_detection_input(record))

    def test_control_plain_barred_names_barred(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertTrue(mod03._is_barred_key("canary"))
        self.assertTrue(mod03._is_barred_key("ground_truth"))

    def test_control_plain_clean_names_admitted(self):
        self.assertFalse(mod03._is_barred_key("activity"))
        self.assertFalse(mod03._is_barred_key("figure"))

    def test_control_lying_clean_key_admitted(self):
        key = LieStr("figure", "figure")
        self.assertFalse(mod03._is_barred_key(key))
        self.assertTrue(
            mod03.validate_detection_input({"a": {key: 1}}))

    def test_control_lower_only_lie_still_barred(self):
        key = LowerLieStr("membership")
        self.assertTrue(mod03._is_barred_key(key))

    def test_control_non_text_key_unbarred(self):
        self.assertFalse(mod03._is_barred_key(12345))


if __name__ == "__main__":
    unittest.main()

"""Step 15 rerun fix wave 4, seat 8. MOD-12 items.

Pins for register rows R4-017 and the MOD-12 limb of R4-016.
Each pin was written before its cure and the failing counts on
the unmodified tree stand recorded in the paper for this seat.
"""
import unittest

from crucible import mod12

ES = "\u0441"
PADDED_MIXED = (
    "an" + ES + "hor" + "$" * 12 + "_" + ES + ES + "enario_values")
PADDED_MIXED_LONG = (
    "an" + ES + "hor" + "$" * 20 + "_" + ES + ES + "enario_values")
UNPADDED_MIXED = "an" + ES + "hor_" + ES + ES + "enario_values"
PLAIN_PADDED = "anchor" + "$" * 12 + "_scenario_values"
PLAIN_ANCHOR = "anchor_scenario_values"
MIXED_LEET = "anchor_scenar1o_va1ues"
I_ONLY_LEET = "anchor_scenar1o_values"
L_ONLY_LEET = "anchor_scenario_va1ues"


def run_record(name, count):
    return {
        "run_class": "screening",
        "seed_domain": "screening",
        name: ["value"] * count,
    }


class TestR4017PaddedMixedAnchor(unittest.TestCase):
    def test_padded_mixed_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(PADDED_MIXED, 4)))

    def test_padded_mixed_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(PADDED_MIXED, 3)))

    def test_longer_padded_mixed_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(PADDED_MIXED_LONG, 4)))

    def test_longer_padded_mixed_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(PADDED_MIXED_LONG, 3)))

    def test_unpadded_mixed_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(UNPADDED_MIXED, 4)))

    def test_unpadded_mixed_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(UNPADDED_MIXED, 3)))

    def test_plain_padded_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(PLAIN_PADDED, 4)))

    def test_plain_padded_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(PLAIN_PADDED, 3)))

    def test_plain_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(PLAIN_ANCHOR, 4)))

    def test_plain_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(PLAIN_ANCHOR, 3)))

    def test_near_miss_name_passes_at_count_4(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anchor_scenario_notes", 4)))


class TestR4016MixedLeetAnchorMod12Limb(unittest.TestCase):
    def test_mixed_leet_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(MIXED_LEET, 4)))

    def test_mixed_leet_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(MIXED_LEET, 3)))

    def test_i_only_leet_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(I_ONLY_LEET, 4)))

    def test_i_only_leet_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(I_ONLY_LEET, 3)))

    def test_l_only_leet_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record(L_ONLY_LEET, 4)))

    def test_l_only_leet_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record(L_ONLY_LEET, 3)))

    def test_mixed_leet_near_miss_passes_at_count_4(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anchor_scenar1o_va1uex", 4)))


if __name__ == "__main__":
    unittest.main()

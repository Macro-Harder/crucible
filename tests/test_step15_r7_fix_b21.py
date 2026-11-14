"""Step 15 rerun fix wave 6 pins, completion seat b21, MOD-10.

Pins for the remaining limb of row R6-010: Greek eta counts one
reading at MOD-10, as it counts at MOD-03, MOD-04, and MOD-05,
while Greek theta keeps its two readings at every surface.
Values are simulated and test values only.
"""
import unittest

import crucible.mod03 as mod03
import crucible.mod04 as mod04
import crucible.mod05 as mod05
import crucible.mod10 as mod10

ETA = "\u03b7"
THETA = "\u03b8"
CORE = "\u0441a\u043dary"


class TestEtaCountsOneAtMod10(unittest.TestCase):
    def test_eta_single_option_is_e_only(self):
        self.assertEqual(mod10._expanded_texts(ETA), {"e"})

    def test_eta_single_option_count_is_one(self):
        self.assertEqual(len(mod10._expanded_texts(ETA)), 1)

    def test_eta_eleven_alone_inside_bound(self):
        self.assertEqual(mod10._expanded_texts(ETA * 11), {"e" * 11})

    def test_eta_thirteen_alone_inside_bound(self):
        self.assertEqual(mod10._expanded_texts(ETA * 13), {"e" * 13})

    def test_canary_core_behind_eleven_eta_inside_bound(self):
        key = CORE + ETA * 11
        self.assertNotEqual(mod10._expanded_texts(key), set())
        self.assertEqual(len(mod10._expanded_texts(key)), 4)

    def test_canary_core_behind_ten_eta_inside_bound(self):
        key = CORE + ETA * 10
        self.assertEqual(len(mod10._expanded_texts(key)), 4)

    def test_canary_core_behind_twelve_eta_inside_bound(self):
        key = CORE + ETA * 12
        self.assertEqual(len(mod10._expanded_texts(key)), 4)

    def test_plain_canary_behind_eleven_eta_inside_bound(self):
        key = "canary" + ETA * 11
        self.assertEqual(
            mod10._expanded_texts(key), {"canary" + "e" * 11})


class TestEtaBarredStandingAgrees(unittest.TestCase):
    def test_canary_core_behind_eleven_eta_barred_at_mod10(self):
        self.assertTrue(mod10._is_barred_view_key(CORE + ETA * 11))

    def test_plain_canary_behind_eleven_eta_barred_at_mod10(self):
        self.assertTrue(mod10._is_barred_view_key("canary" + ETA * 11))

    def test_canary_core_behind_eleven_eta_barred_at_sisters(self):
        key = CORE + ETA * 11
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod04._is_barred_key(key))


class TestEtaSisterStandingControls(unittest.TestCase):
    def test_eta_one_reading_at_every_sister_surface(self):
        self.assertEqual(mod03._character_variants(ETA), {"e"})
        self.assertEqual(mod04._character_variants(ETA), {"e"})
        self.assertEqual(mod05._character_options(ETA), {"e"})

    def test_eta_mod10_reading_matches_sister_reading(self):
        self.assertEqual(
            mod10._expanded_texts(ETA), mod05._character_options(ETA))


class TestThetaStandingControls(unittest.TestCase):
    def test_theta_single_options_unchanged(self):
        self.assertEqual(mod10._expanded_texts(THETA), {"t", "th"})

    def test_theta_ten_at_bound_unchanged(self):
        key = CORE + THETA * 10
        self.assertEqual(len(mod10._expanded_texts(key)), 4096)

    def test_theta_eleven_past_bound_unchanged(self):
        key = CORE + THETA * 11
        self.assertEqual(mod10._expanded_texts(key), set())


class TestLawfulKeysUnaffected(unittest.TestCase):
    def test_clean_key_behind_eleven_eta_admitted(self):
        key = "activity" + ETA * 11
        self.assertEqual(
            mod10._expanded_texts(key), {"activity" + "e" * 11})
        self.assertFalse(mod10._is_barred_view_key(key))

    def test_clean_key_behind_eleven_eta_admitted_at_sisters(self):
        key = "activity" + ETA * 11
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod04._is_barred_key(key))

    def test_eta_currency_dress_still_reads_as_money(self):
        record = {"amount": 5, "curr" + ETA + "ncy": "usd"}
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_core_alone_inside_bound_control(self):
        self.assertEqual(len(mod10._expanded_texts(CORE)), 4)
        self.assertTrue(mod10._is_barred_view_key(CORE))


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 6, completion seat b18, row R6-011.

R6-011: a barred key whose combined readings pass the 4096 bound
stands barred at MOD-05 and admitted at MOD-03, MOD-04, MOD-08,
and MOD-10, because only MOD-05 carries a bound free combined
read behind its enumeration. The cure takes the basis Builder 4
stated: a bound free read at each surface. These pins record the
barred standing on the past bound key at the four surfaces the
trace left uncured, with MOD-05 barring as the passing control
and clean controls agreeing at all five surfaces.
"""

import unittest

from crucible import mod03, mod04, mod05, mod08, mod10

MIXED_CORE = (
    "membe"
    + "\u0440"
    + "\u0441"
    + "\u043d"
    + "i"
    + "\u0440"
)
SHORT_I_FILLER = "\u0439" * 13
CHI_FILLER = "\u03c7" * 13

PAST_BOUND_KEYS = (
    MIXED_CORE + SHORT_I_FILLER,
    MIXED_CORE + CHI_FILLER,
    MIXED_CORE + "\u0439" * 14,
    MIXED_CORE + "\u03c7" * 14,
    MIXED_CORE + "\u0439" * 7 + "\u03c7" * 6,
    MIXED_CORE + "\u0419" * 13,
)


class TestR6011Mod03(unittest.TestCase):

    def test_past_bound_keys_barred_at_mod03(self):
        for key in PAST_BOUND_KEYS:
            with self.subTest(key=repr(key)):
                self.assertTrue(mod03._is_barred_key(key))


class TestR6011Mod04(unittest.TestCase):

    def test_past_bound_keys_barred_at_mod04(self):
        for key in PAST_BOUND_KEYS:
            with self.subTest(key=repr(key)):
                self.assertTrue(mod04._is_barred_key(key))


class TestR6011Mod08(unittest.TestCase):

    def test_past_bound_keys_barred_at_mod08(self):
        for key in PAST_BOUND_KEYS:
            with self.subTest(key=repr(key)):
                self.assertTrue(mod08._is_barred_key(key))


class TestR6011Mod10(unittest.TestCase):

    def test_past_bound_keys_barred_at_mod10(self):
        for key in PAST_BOUND_KEYS:
            with self.subTest(key=repr(key)):
                self.assertTrue(mod10._is_barred_view_key(key))


class TestR6011Controls(unittest.TestCase):

    def test_past_bound_keys_barred_at_mod05_control(self):
        for key in PAST_BOUND_KEYS:
            with self.subTest(key=repr(key)):
                self.assertTrue(mod05._panel_key_barred(key))

    def test_mixed_core_alone_barred_at_all_five(self):
        self.assertTrue(mod03._is_barred_key(MIXED_CORE))
        self.assertTrue(mod04._is_barred_key(MIXED_CORE))
        self.assertTrue(mod05._panel_key_barred(MIXED_CORE))
        self.assertTrue(mod08._is_barred_key(MIXED_CORE))
        self.assertTrue(mod10._is_barred_view_key(MIXED_CORE))

    def test_clean_key_past_bound_admitted_at_all_five(self):
        key = "activity" + SHORT_I_FILLER
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod04._is_barred_key(key))
        self.assertFalse(mod05._panel_key_barred(key))
        self.assertFalse(mod08._is_barred_key(key))
        self.assertFalse(mod10._is_barred_view_key(key))

    def test_clean_chi_key_past_bound_admitted_at_all_five(self):
        key = "activity" + CHI_FILLER
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod04._is_barred_key(key))
        self.assertFalse(mod05._panel_key_barred(key))
        self.assertFalse(mod08._is_barred_key(key))
        self.assertFalse(mod10._is_barred_view_key(key))


if __name__ == "__main__":
    unittest.main()

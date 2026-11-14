"""Step 15 second run fix completion pins for the MOD-10 limbs.

Five register items landed on every charged surface except MOD-10
in the Round 1 fix wave: R1-001, R1-004, R1-006, R1-010 and R1-016.
Each class below pins one limb at MOD-10 only, in the cured form
the standing surfaces already carry.
"""
import unittest

from crucible import mod10


_SMALL_CAPITAL = {
    "a": "\u1d00", "b": "\u0299", "c": "\u1d04", "d": "\u1d05",
    "e": "\u1d07", "f": "\ua730", "g": "\u0262", "h": "\u029c",
    "i": "\u026a", "j": "\u1d0a", "k": "\u1d0b", "l": "\u029f",
    "m": "\u1d0d", "n": "\u0274", "o": "\u1d0f", "p": "\u1d18",
    "q": "\ua7af", "r": "\u0280", "s": "\ua731", "t": "\u1d1b",
    "u": "\u1d1c", "v": "\u1d20", "w": "\u1d21", "y": "\u028f",
    "z": "\u1d22",
}


def _small_capital(text):
    return "".join(_SMALL_CAPITAL.get(ch, ch) for ch in text)


class TestR1001SmallCapitalMod10(unittest.TestCase):
    def test_fold_variants_read_small_capital_marker(self):
        dressed = _small_capital("realmoney")
        self.assertIn("realmoney", mod10._fold_variants(dressed))

    def test_folded_money_key_reads_small_capital_marker(self):
        dressed = _small_capital("realmoney")
        self.assertEqual(mod10._folded_money_key(dressed), "realmoney")

    def test_carries_real_money_field_small_capital(self):
        dressed = _small_capital("realmoney")
        self.assertTrue(mod10._carries_real_money_field({dressed: 500}))
        self.assertTrue(mod10._carries_real_money_field(
            {"outer": {dressed: 500}}))


class TestR1004SymbolLeetMod10(unittest.TestCase):
    MONEY_DRESSES = (
        "re@lmoney",
        "r\u20acalmoney",
        "rea\u00a3money",
        "rea!money",
        "rea|money",
        "realmone\u00a5",
    )

    def test_symbol_dressed_money_marker_read(self):
        for dressed in self.MONEY_DRESSES:
            self.assertEqual(
                mod10._folded_money_key(dressed), "realmoney", dressed)
            self.assertTrue(
                mod10._carries_real_money_field({dressed: 500}), dressed)

    def test_symbol_dressed_amount_and_currency_read(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"@mount": 5, "currency": "stated"}))
        self.assertTrue(mod10._carries_real_money_field(
            {"amount": 5, "currenc\u00a5": "stated"}))

    def test_symbol_dressed_anchor_fold_read(self):
        self.assertIn(
            "anchorscenariovalues",
            mod10._fold_variants("@nchor_scenario_values"))


class TestR1006ArmenianMod10(unittest.TestCase):
    DRESSES = (
        "realm\u0585ney",
        "realm\u0555ney",
        "realmo\u0578ey",
        "realmo\u0548ey",
    )

    def test_armenian_dressed_marker_read(self):
        for dressed in self.DRESSES:
            self.assertEqual(
                mod10._folded_money_key(dressed), "realmoney", dressed)
            self.assertTrue(
                mod10._carries_real_money_field({dressed: 500}), dressed)


class TestR1010BarredLeetMod10(unittest.TestCase):
    def test_symbol_barred_keys_read_before_symbols_dropped(self):
        self.assertTrue(mod10._is_barred_view_key("l@bel"))
        self.assertTrue(mod10._is_barred_view_key("member$hip"))

    def test_digit_one_reads_as_i_in_barred_fold(self):
        self.assertIn("membership", mod10._fold_variants("membersh1p"))
        self.assertTrue(mod10._is_barred_view_key("membersh1p"))

    def test_barred_reading_reaches_nested_keys(self):
        self.assertTrue(mod10._carries_barred_key(
            {"outer": {"l@bel": 1}}))
        self.assertTrue(mod10._carries_barred_key(
            {"outer": {"member$hip": 1}}))

    def test_clean_keys_still_admitted(self):
        for key in ("activity", "labelled", "labels", "honest_score"):
            self.assertFalse(mod10._is_barred_view_key(key), key)


class TestR1016BaseDictMod10(unittest.TestCase):
    class HidingDict(dict):
        def items(self):
            return []

        def keys(self):
            return []

    def test_hiding_dict_real_money_field_read(self):
        record = self.HidingDict({"realmoney": 500})
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_hiding_dict_amount_currency_shape_read(self):
        record = self.HidingDict({"amount": 5, "currency": "stated"})
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_hiding_dict_barred_key_read(self):
        record = self.HidingDict({"membership": 1})
        self.assertTrue(mod10._carries_barred_key(record))
        self.assertTrue(mod10._carries_barred_key({"outer": record}))

    def test_hiding_dict_clean_record_still_clean(self):
        record = self.HidingDict({"activity": 1})
        self.assertFalse(mod10._carries_real_money_field(record))
        self.assertFalse(mod10._carries_barred_key(record))


if __name__ == "__main__":
    unittest.main()

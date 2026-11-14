"""Step 15 second run fix pins, Fix Builder 4, MOD-05 only.

Items R1-008, R1-010, R1-019, R1-020, R1-038, R1-040, R1-043
and R1-071, each pinned test first against crucible.mod05.
"""
import math
import unittest

from crucible import mod05


def barred_via_panel(key):
    return (
        mod05._panel_key_barred(key)
        and not mod05.validate_panel_inputs({key: "v"})
        and key not in mod05.panel_inputs({key: "v", "keep": 1})
    )


class TestR1008HomoglyphMap(unittest.TestCase):
    def test_nu_reads_as_n(self):
        self.assertTrue(barred_via_panel("isho\u03bdest"))
        self.assertIn("n", mod05._folded_readings("\u03bd"))

    def test_cyrillic_letters_mod03_reads(self):
        self.assertTrue(barred_via_panel("\u043cembership"))
        self.assertTrue(barred_via_panel("la\u0432el"))
        self.assertTrue(barred_via_panel("ground_tru\u0442h"))
        self.assertTrue(barred_via_panel("\u0456shonest"))

    def test_greek_letters_mod03_reads(self):
        self.assertTrue(barred_via_panel("la\u03b2el"))
        self.assertTrue(barred_via_panel("\u03bcembership"))
        self.assertTrue(barred_via_panel("ishone\u03c3t"))
        self.assertTrue(barred_via_panel("ground_tr\u03c5th"))


class TestR1010LeetBeforeDroppingSymbols(unittest.TestCase):
    def test_at_sign_fires(self):
        self.assertTrue(barred_via_panel("l@bel"))

    def test_dollar_sign_fires(self):
        self.assertTrue(barred_via_panel("i$honest"))

    def test_digit_one_reads_as_i(self):
        self.assertTrue(barred_via_panel("membersh1p"))
        self.assertTrue(barred_via_panel("1shonest"))

    def test_digit_one_still_reads_as_l(self):
        self.assertTrue(barred_via_panel("1abel"))


class TestR1019ProportionBaseGetitem(unittest.TestCase):
    def test_valid_underlying_stands_despite_override(self):
        class Evil(dict):
            def __getitem__(self, key):
                return -1

        record = Evil(numerator=1, denominator=2, quotient=0.5)
        self.assertTrue(mod05.validate_proportion(record))

    def test_invalid_underlying_fails_despite_override(self):
        class Evil(dict):
            def __getitem__(self, key):
                return {"numerator": 1, "denominator": 2, "quotient": 0.5}[key]

        record = Evil(numerator=0, denominator=0)
        self.assertFalse(mod05.validate_proportion(record))

    def test_wrong_quotient_underlying_fails_despite_override(self):
        class Evil(dict):
            def __getitem__(self, key):
                return {"numerator": 1, "denominator": 2, "quotient": 0.5}[key]

        record = Evil(numerator=1, denominator=2, quotient=0.9)
        self.assertFalse(mod05.validate_proportion(record))


class TestR1020ProportionFiniteness(unittest.TestCase):
    def test_nan_and_infinite_parts_fail(self):
        for record in (
            {"numerator": float("nan"), "denominator": 2},
            {"numerator": 1, "denominator": float("nan")},
            {"numerator": float("inf"), "denominator": 2},
            {"numerator": 1, "denominator": float("inf")},
            {"numerator": 1, "denominator": 2, "quotient": float("nan")},
            {"numerator": 1, "denominator": 2, "quotient": float("inf")},
            {"numerator": float("-inf"), "denominator": 2},
        ):
            with self.subTest(record=record):
                self.assertFalse(mod05.validate_proportion(record))

    def test_finite_parts_still_stand(self):
        self.assertTrue(mod05.validate_proportion(
            {"numerator": 1, "denominator": 2, "quotient": 0.5}))


class TestR1038ResidualLetterClasses(unittest.TestCase):
    def test_dotless_i(self):
        self.assertTrue(barred_via_panel("membersh\u0131p"))
        self.assertTrue(barred_via_panel("\u0131shonest"))

    def test_h_bar(self):
        self.assertTrue(barred_via_panel("members\u0127ip"))
        self.assertTrue(barred_via_panel("is_\u0127onest"))

    def test_l_stroke(self):
        self.assertTrue(barred_via_panel("\u0142abel"))
        self.assertTrue(barred_via_panel("\u0142abe\u0142"))

    def test_cyrillic_em(self):
        self.assertTrue(barred_via_panel("\u043cembership"))

    def test_further_transliteration_letters(self):
        self.assertTrue(barred_via_panel("ground_\u0167ruth"))
        self.assertTrue(barred_via_panel("\u0142abel_reference"))


class TestR1040PanelCleanTuples(unittest.TestCase):
    def test_tuple_values_recursed_in_panel_inputs(self):
        formed = mod05.panel_inputs(
            {"keep": ({"membership": 1, "keep2": 2}, "x")})
        self.assertEqual(formed, {"keep": ({"keep2": 2}, "x")})
        self.assertIsInstance(formed["keep"], tuple)

    def test_tuple_inside_list_recursed(self):
        formed = mod05.panel_inputs(
            {"keep": [({"label": 1, "keep2": 2},)]})
        self.assertEqual(formed, {"keep": [({"keep2": 2},)]})

    def test_validator_reads_tuples_as_before(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {"keep": ({"membership": 1},)}))


class TestR1043EmptyWorkCredit(unittest.TestCase):
    def test_empty_event_set_totals_proportion_is_unknown(self):
        result = mod05.work_credit([])
        self.assertEqual(result["totals"]["submitted"], 0)
        self.assertEqual(result["totals"]["accepted"], 0)
        self.assertEqual(result["totals"]["proportion"], "unknown")
        self.assertEqual(
            result["totals"]["proportion"], mod05.UNKNOWN_SHARE)
        self.assertTrue(mod05.validate_logged_share(
            result["totals"]["proportion"]))

    def test_nonempty_event_set_keeps_proportion_record(self):
        result = mod05.work_credit(
            [{"agent": "a", "accepted": True}])
        self.assertEqual(result["totals"]["proportion"],
                         {"numerator": 1, "denominator": 1})


def deep_value(depth):
    root = {}
    current = root
    for _ in range(depth):
        nxt = {}
        current["a"] = nxt
        current = nxt
    return root


def cyclic_value():
    value = {}
    value["self"] = value
    return value


class TestR1071PanelDepthAndCycleGuard(unittest.TestCase):
    def test_deep_validate_returns_false_not_recursion_error(self):
        self.assertFalse(mod05.validate_panel_inputs(deep_value(5000)))

    def test_deep_panel_inputs_raises_value_error(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs(deep_value(5000))

    def test_cyclic_validate_returns_false_not_recursion_error(self):
        self.assertFalse(mod05.validate_panel_inputs(cyclic_value()))

    def test_cyclic_panel_inputs_raises_value_error(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs(cyclic_value())

    def test_cyclic_list_validate_returns_false(self):
        value = []
        value.append(value)
        self.assertFalse(mod05.validate_panel_inputs({"keep": value}))

    def test_shared_reference_is_not_a_cycle(self):
        shared = {"activity": 1}
        formed = mod05.panel_inputs({"a": shared, "b": shared})
        self.assertEqual(formed, {"a": {"activity": 1},
                                  "b": {"activity": 1}})
        self.assertTrue(mod05.validate_panel_inputs(
            {"a": shared, "b": shared}))


if __name__ == "__main__":
    unittest.main()

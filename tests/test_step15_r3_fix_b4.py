"""Step 15 rerun Round 2 fix wave 2 pins, Fix Builder 4, MOD-05 only.

Items R2-001, R2-002, R2-003, R2-025, R2-026, R2-027, R2-046
and R2-051, each pinned test first against crucible.mod05.
"""
import unittest

from crucible import mod05


def barred_via_panel(key):
    return (
        mod05._panel_key_barred(key)
        and not mod05.validate_panel_inputs({key: "v"})
        and key not in mod05.panel_inputs({key: "v", "keep": 1})
    )


class HideList(list):
    def __iter__(self):
        return iter(())


class HideTuple(tuple):
    def __iter__(self):
        return iter(())


class LyingItems(dict):
    def items(self):
        return [("keep", 2)]


class LyingContains(dict):
    def __contains__(self, key):
        return True


def frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


class TestR2001BaseIteration(unittest.TestCase):
    def test_hide_list_holding_barred_dict_is_barred(self):
        record = {"x": HideList([{"membership": 1}])}
        self.assertFalse(mod05.validate_panel_inputs(record))

    def test_hide_list_cleaned_by_panel_inputs(self):
        formed = mod05.panel_inputs({"x": HideList([{"membership": 1, "keep": 2}])})
        self.assertEqual(formed, {"x": [{"keep": 2}]})

    def test_hide_tuple_holding_barred_dict_is_barred(self):
        record = {"x": HideTuple(({"label": 1},))}
        self.assertFalse(mod05.validate_panel_inputs(record))

    def test_hide_tuple_cleaned_by_panel_inputs(self):
        formed = mod05.panel_inputs({"x": HideTuple(({"label": 1, "keep": 2},))})
        self.assertEqual(formed, {"x": ({"keep": 2},)})


class TestR2002SmallCapitalAndArmenianOh(unittest.TestCase):
    def test_small_capital_label(self):
        self.assertTrue(barred_via_panel("\u029f\u1d00\u0299\u1d07\u029f"))

    def test_small_capital_membership(self):
        key = "\u1d0d\u1d07\u1d0d\u0299\u1d07\u0280\ua731\u029c\u026a\u1d18"
        self.assertTrue(barred_via_panel(key))

    def test_armenian_oh_ground_truth(self):
        self.assertTrue(barred_via_panel("gr\u0585und_truth"))
        self.assertTrue(barred_via_panel("gr\u0555und_truth"))


class TestR2003BaseDictReading(unittest.TestCase):
    def test_lying_items_top_level(self):
        record = LyingItems({"label": 1, "keep": 2})
        self.assertFalse(mod05.validate_panel_inputs(record))

    def test_lying_items_nested(self):
        record = {"x": LyingItems({"membership": 1, "keep": 2})}
        self.assertFalse(mod05.validate_panel_inputs(record))

    def test_lying_items_cleaned_from_stored_contents(self):
        formed = mod05.panel_inputs({"x": LyingItems({"membership": 1, "ok": 2})})
        self.assertEqual(formed, {"x": {"ok": 2}})

    def test_validate_proportion_lying_contains_empty(self):
        record = LyingContains()
        self.assertFalse(mod05.validate_proportion(record))

    def test_validate_proportion_lying_contains_partial(self):
        record = LyingContains({"numerator": 1})
        self.assertFalse(mod05.validate_proportion(record))


class TestR2025ProportionBaseOperators(unittest.TestCase):
    def test_lying_int_denominator_negative(self):
        class LyingInt(int):
            def __le__(self, other):
                return False

            def __lt__(self, other):
                return False

        record = {"numerator": 1, "denominator": LyingInt(-5)}
        self.assertFalse(mod05.validate_proportion(record))

    def test_lying_float_denominator_negative(self):
        class LyingFloat(float):
            def __le__(self, other):
                return False

            def __lt__(self, other):
                return False

        record = {"numerator": 1, "denominator": LyingFloat(-5.0)}
        self.assertFalse(mod05.validate_proportion(record))

    def test_lying_division_on_quotient_limb(self):
        class LyingDivInt(int):
            def __truediv__(self, other):
                return 0.9

        record = {"numerator": LyingDivInt(1), "denominator": 2, "quotient": 0.9}
        self.assertFalse(mod05.validate_proportion(record))

    def test_lying_int_numerator_negative(self):
        class LyingInt(int):
            def __lt__(self, other):
                return False

            def __le__(self, other):
                return False

        record = {"numerator": LyingInt(-1), "denominator": 2}
        self.assertFalse(mod05.validate_proportion(record))

    def test_plain_valid_still_stands(self):
        self.assertTrue(mod05.validate_proportion(
            {"numerator": 1, "denominator": 2, "quotient": 0.5}))


class TestR2026TransliteratedReading(unittest.TestCase):
    def test_cyrillic_er_membership(self):
        self.assertTrue(barred_via_panel("membe\u0440ship"))

    def test_cyrillic_el_label(self):
        self.assertTrue(barred_via_panel("labe\u043b"))

    def test_cyrillic_i_membership(self):
        self.assertTrue(barred_via_panel("membersh\u0438p"))

    def test_greek_eta_label(self):
        self.assertTrue(barred_via_panel("lab\u03b7l"))


class TestR2027FrozensetBound(unittest.TestCase):
    def test_frozenset_chain_past_bound_fails_validation(self):
        self.assertFalse(mod05.validate_panel_inputs({"x": frozenset_chain(150)}))

    def test_frozenset_chain_at_5000_fails_validation(self):
        self.assertFalse(mod05.validate_panel_inputs({"x": frozenset_chain(5000)}))

    def test_frozenset_chain_panel_inputs_raises_value_error(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs({"x": frozenset_chain(150)})

    def test_frozenset_chain_panel_inputs_no_recursion_error_at_5000(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs({"x": frozenset_chain(5000)})

    def test_shallow_frozenset_still_stands(self):
        self.assertTrue(mod05.validate_panel_inputs({"x": frozenset((1, 2))}))
        formed = mod05.panel_inputs({"x": frozenset((1, 2))})
        self.assertEqual(formed, {"x": frozenset((1, 2))})


class TestR2046MembershipPartReading(unittest.TestCase):
    def test_membership_ground_truth_composite_one(self):
        key = "m3mbership_\u0433round_truth"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))
        self.assertNotIn(key, mod05.panel_inputs({key: 1, "keep": 2}))

    def test_membership_ground_truth_composite_two(self):
        key = "m3mbe-rship_\u0433round_truth"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))
        self.assertNotIn(key, mod05.panel_inputs({key: 1, "keep": 2}))

    def test_membership_part_with_unread_ground_part(self):
        key = "m3mbership_\u0433r ound_truth"
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))


class TestR2051WiderCommonReadingSet(unittest.TestCase):
    def test_cyrillic_transliteration_composites(self):
        self.assertTrue(barred_via_panel("m3mbe-rs\u0445ip"))
        self.assertTrue(barred_via_panel("gr0un\u0434_tr-uth"))
        self.assertTrue(barred_via_panel("\u0433round._7ruth"))

    def test_greek_only_at_mod10_composites(self):
        self.assertTrue(barred_via_panel("m\u03b7mb-3rship"))
        self.assertTrue(barred_via_panel("i\u03c2_hon-3st"))

    def test_armenian_vo_composite(self):
        self.assertTrue(barred_via_panel("grou\u0578d_truth"))

    def test_small_capital_composite(self):
        self.assertTrue(barred_via_panel("\u1d0d3mbe_rship"))

    def test_symbol_composites(self):
        self.assertTrue(barred_via_panel("\u00a3a-b3l"))
        self.assertTrue(barred_via_panel("lab\u20acl"))

    def test_r1009_added_letters(self):
        self.assertTrue(barred_via_panel("member\u0452hip"))
        self.assertTrue(barred_via_panel("members\u0493ip"))


if __name__ == "__main__":
    unittest.main()

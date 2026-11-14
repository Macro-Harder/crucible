# Step 15, second run, fix wave 4, Builder 1 pins. MOD-01 only.
# Rows R4-007, R4-012, R4-016 (MOD-01 limb), R4-019 and R4-024
# of the Round 4 register.
import unittest

import crucible.mod01 as mod01


RESERVED = "banked real money stake behaviour"
MIXED_ANCHOR_NAME = "anchor_scenar1o_va1ues"


def form4_with(key, value):
    instance = mod01.minimal_valid_instance("4")
    instance[key] = value
    return instance


def provenance_block(counts, shares):
    return {
        "entries": [{"field": "plain field", "applicability": "applies"}],
        "excluded_class_counts": counts,
        "excluded_class_shares": shares,
    }


class GhostFieldDict(dict):
    """A dict subclass whose contains, item and get readings supply
    a value for a field the stored record does not carry."""

    def __init__(self, stored, ghost):
        super().__init__(stored)
        self._ghost = ghost

    def __contains__(self, key):
        if key == self._ghost:
            return True
        return dict.__contains__(self, key)

    def __getitem__(self, key):
        if key == self._ghost and not dict.__contains__(self, key):
            return "stated ghost value"
        return dict.__getitem__(self, key)

    def get(self, key, default=None):
        if key == self._ghost and not dict.__contains__(self, key):
            return "stated ghost value"
        return dict.get(self, key, default)


class TestR4007RequiredFieldBaseReading(unittest.TestCase):
    def test_plain_missing_annotation_link_fails(self):
        instance = mod01.minimal_valid_instance("4")
        del instance["annotation_link"]
        self.assertFalse(mod01.validate_record("4", instance))

    def test_ghost_missing_annotation_link_fails(self):
        stored = mod01.minimal_valid_instance("4")
        del stored["annotation_link"]
        record = GhostFieldDict(stored, "annotation_link")
        self.assertTrue(dict.__contains__(record, "annotation_link")
                        is False)
        self.assertFalse(mod01.validate_record("4", record))

    def test_ghost_missing_required_field_fails_at_inner_read(self):
        stored = mod01.minimal_valid_instance("4")
        del stored["run_identifier"]
        record = GhostFieldDict(stored, "run_identifier")
        self.assertFalse(mod01.validate_record("4", record))

    def test_complete_record_in_ghost_wrapper_still_passes(self):
        stored = mod01.minimal_valid_instance("4")
        record = GhostFieldDict(stored, "annotation_link")
        self.assertTrue(mod01.validate_record("4", record))

    def test_plain_complete_record_still_passes(self):
        instance = mod01.minimal_valid_instance("4")
        self.assertTrue(mod01.validate_record("4", instance))


class CleanValuesDict(dict):
    """A dict subclass whose values reading reports clean values
    while its stored values stand in a refused form."""

    def __init__(self, stored, clean_values):
        super().__init__(stored)
        self._clean = list(clean_values)

    def values(self):
        return list(self._clean)


class CleanKeysDict(dict):
    """A dict subclass whose keys and iteration readings report
    only the lawful keys while it stores an extra key."""

    def __init__(self, stored, clean_keys):
        super().__init__(stored)
        self._clean_keys = list(clean_keys)

    def keys(self):
        return list(self._clean_keys)

    def __iter__(self):
        return iter(list(self._clean_keys))


class CleanGetDict(dict):
    """A dict subclass whose get reading returns clean parts while
    its stored parts stand in a refused form."""

    def __init__(self, stored, clean):
        super().__init__(stored)
        self._clean = dict(clean)

    def get(self, key, default=None):
        if key in self._clean:
            return self._clean[key]
        return dict.get(self, key, default)


class HideItemsDict(dict):
    """A dict subclass whose items reading reports nothing."""

    def items(self):
        return []


class HideIterList(list):
    """A list subclass whose iteration yields nothing."""

    def __iter__(self):
        return iter(())


class LyingFloat(float):
    """A float subclass storing one value whose float conversion
    reports another value."""

    def __new__(cls, stored, reported):
        instance = super().__new__(cls, stored)
        instance._reported = reported
        return instance

    def __float__(self):
        return self._reported


class TestR4012ProvenanceAndReservedBaseReadings(unittest.TestCase):
    def test_counts_text_value_hidden_by_values_reading_fails(self):
        counts = CleanValuesDict({"a": "one"}, [1])
        block = provenance_block(counts, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_shares_text_value_hidden_by_values_reading_fails(self):
        shares = CleanValuesDict({"a": "half"}, [0.5])
        block = provenance_block({"a": 1}, shares)
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_extra_count_key_hidden_by_keys_and_iteration_fails(self):
        counts = CleanKeysDict({"a": 1, "b": 2}, ["a"])
        block = provenance_block(counts, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_whole_block_hidden_by_get_reading_fails(self):
        stored = {
            "entries": [],
            "excluded_class_counts": {"a": "one"},
            "excluded_class_shares": {"a": "half"},
        }
        clean = {
            "entries": [{"field": "plain field",
                         "applicability": "applies"}],
            "excluded_class_counts": {"a": 1},
            "excluded_class_shares": {"a": 0.5},
        }
        block = CleanGetDict(stored, clean)
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_reserved_matter_hidden_by_dict_items_reading_fails(self):
        holder = HideItemsDict({"inner": RESERVED})
        record = form4_with("note_field", holder)
        self.assertFalse(mod01.validate_record("4", record))

    def test_reserved_matter_hidden_at_top_level_items_fails(self):
        stored = form4_with("note_field", RESERVED)
        record = HideItemsDict(stored)
        self.assertFalse(mod01.validate_record("4", record))

    def test_reserved_matter_hidden_by_list_iteration_fails(self):
        holder = HideIterList([RESERVED])
        record = form4_with("note_field", holder)
        self.assertFalse(mod01.validate_record("4", record))

    def test_reserved_matter_plain_forms_still_fail(self):
        self.assertFalse(mod01.validate_record(
            "4", form4_with("note_field", {"inner": RESERVED})))
        self.assertFalse(mod01.validate_record(
            "4", form4_with("note_field", [RESERVED])))
        self.assertFalse(mod01.validate_record(
            "4", form4_with("note_field", RESERVED)))

    def test_float_subclass_fraction_reported_as_one_fails_count(self):
        value = LyingFloat(0.5, 1.0)
        self.assertFalse(mod01._is_count_value(value))
        block = provenance_block({"a": value}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_float_subclass_fraction_reported_as_two_fails_count(self):
        value = LyingFloat(1.5, 2.0)
        self.assertFalse(mod01._is_count_value(value))
        block = provenance_block({"a": value}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_float_subclass_whole_value_still_passes_count(self):
        value = LyingFloat(2.0, 2.0)
        self.assertTrue(mod01._is_count_value(value))
        block = provenance_block({"a": value}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_negative_int_count_fails(self):
        block = provenance_block({"a": -2}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_negative_float_count_fails(self):
        block = provenance_block({"a": -2.0}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_share_above_one_fails(self):
        block = provenance_block({"a": 2}, {"a": 1.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_negative_share_fails(self):
        block = provenance_block({"a": 2}, {"a": -0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_integer_share_of_two_fails(self):
        block = provenance_block({"a": 2}, {"a": 2})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_valid_count_and_share_controls_pass(self):
        self.assertTrue(mod01.validate_provenance_block(
            provenance_block({"a": 2}, {"a": 0.5})))
        self.assertTrue(mod01.validate_provenance_block(
            provenance_block({"a": 0}, {"a": 0})))
        self.assertTrue(mod01.validate_provenance_block(
            provenance_block({"a": 2.0}, {"a": 1})))
        self.assertTrue(mod01.validate_provenance_block(
            provenance_block({"a": 1}, {"a": 1.0})))

    def test_cured_form_controls_still_fail(self):
        self.assertFalse(mod01.validate_provenance_block(
            provenance_block({"a": "one"}, {"a": 0.5})))
        self.assertFalse(mod01.validate_provenance_block(
            provenance_block({"a": 1.5}, {"a": 0.5})))
        self.assertFalse(mod01.validate_provenance_block(
            provenance_block({"a": True}, {"a": 0.5})))
        self.assertFalse(mod01.validate_provenance_block(
            provenance_block({"a": 1}, {"a": "half"})))
        self.assertFalse(mod01.validate_provenance_block(
            provenance_block({"a": 1}, {"a": True})))


def list_chain(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = [value]
    return value


def tuple_chain(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = (value,)
    return value


def frozenset_chain(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = frozenset((value,))
    return value


def dict_chain(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = {"k": value}
    return value


def count_guard_calls(value):
    original = mod01._traversal_guard
    calls = [0]

    def counting(guarded, depth, seen):
        calls[0] += 1
        return original(guarded, depth, seen)

    mod01._traversal_guard = counting
    try:
        mod01._guard_copyable(value)
    finally:
        mod01._traversal_guard = original
    return calls[0]


class TestR4019GuardCopyableSingleWalk(unittest.TestCase):
    def test_list_chain_8_draws_8_guard_calls(self):
        self.assertEqual(count_guard_calls(list_chain(8)), 8)

    def test_list_chain_10_draws_10_guard_calls(self):
        self.assertEqual(count_guard_calls(list_chain(10)), 10)

    def test_list_chain_12_draws_12_guard_calls(self):
        self.assertEqual(count_guard_calls(list_chain(12)), 12)

    def test_list_chain_14_draws_14_guard_calls(self):
        self.assertEqual(count_guard_calls(list_chain(14)), 14)

    def test_tuple_chain_12_draws_12_guard_calls(self):
        self.assertEqual(count_guard_calls(tuple_chain(12)), 12)

    def test_frozenset_chain_12_draws_12_guard_calls(self):
        self.assertEqual(count_guard_calls(frozenset_chain(12)), 12)

    def test_dict_chain_14_draws_14_guard_calls(self):
        self.assertEqual(count_guard_calls(dict_chain(14)), 14)

    def test_dict_chain_99_draws_99_guard_calls(self):
        self.assertEqual(count_guard_calls(dict_chain(99)), 99)

    def test_list_chain_past_bound_still_refuses_in_named_form(self):
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._guard_copyable(list_chain(102))

    def test_version_stamp_with_list_chain_still_copies(self):
        values = {
            "family_version": list_chain(3),
            "family_manifest_hash": "stated hash",
            "rule_version_set": "stated set",
        }
        stamp = mod01.VersionStamp(values)
        self.assertEqual(stamp.as_dict(), values)


class TestR4024FoldReadingsForCyrillicEAndPsi(unittest.TestCase):
    def test_currency_pair_with_cyrillic_e_carries_money(self):
        record = {"amount": 5, "curr\u044dncy": "USD"}
        self.assertTrue(mod01._carries_real_money_value(record))

    def test_currency_pair_with_cyrillic_e_fails_record(self):
        instance = form4_with("amount", 5)
        instance["curr\u044dncy"] = "USD"
        self.assertFalse(mod01.validate_record("4", instance))

    def test_money_marker_with_cyrillic_e_carries_money(self):
        record = {"r\u044dalmoney": 500}
        self.assertTrue(mod01._carries_real_money_value(record))

    def test_money_marker_with_cyrillic_e_fails_record(self):
        instance = form4_with("r\u044dalmoney", 500)
        self.assertFalse(mod01.validate_record("4", instance))

    def test_anchor_name_with_cyrillic_e_matches_fold(self):
        key = "anchor_sc\u044dnario_values"
        self.assertTrue(mod01._folded_key_matches(
            key, mod01._ANCHOR_VALUES_FIELD_FOLDED))

    def test_anchor_name_with_cyrillic_e_fails_at_four(self):
        key = "anchor_sc\u044dnario_values"
        bad = form4_with(key, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))
        good = form4_with(key, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))

    def test_cyrillic_e_single_letter_reads_as_e(self):
        self.assertIn("e", mod01._folded_key_variants("\u044d"))
        self.assertIn("e", mod01._canonical_variants("\u044d"))

    def test_psi_single_letter_reads_as_ps(self):
        self.assertIn("ps", mod01._folded_key_variants("\u03c8"))
        self.assertIn("ps", mod01._canonical_variants("\u03c8"))
        self.assertTrue(mod01._folded_key_matches("\u03c8", "ps"))

    def test_money_pair_controls_stand_both_ways(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"amount": 5, "currency": "USD"}))
        self.assertFalse(mod01._carries_real_money_value(
            {"amount": 5, "clean_key": "USD"}))
        self.assertFalse(mod01._carries_real_money_value(
            {"clean_key": 500}))


class TestR4016MixedLeetReadingsOfFigureOne(unittest.TestCase):
    def test_mixed_name_matches_anchor_fold(self):
        self.assertTrue(mod01._folded_key_matches(
            MIXED_ANCHOR_NAME, mod01._ANCHOR_VALUES_FIELD_FOLDED))

    def test_mixed_name_stands_in_folded_variants(self):
        self.assertIn(
            mod01._ANCHOR_VALUES_FIELD_FOLDED,
            mod01._folded_key_variants(MIXED_ANCHOR_NAME))

    def test_mixed_name_fails_at_four_and_passes_at_three(self):
        bad = form4_with(MIXED_ANCHOR_NAME, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))
        good = form4_with(MIXED_ANCHOR_NAME, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))

    def test_single_reading_names_still_fail_at_four(self):
        for key in ("anchor_scenar1o_values",
                    "anchor_scenario_va1ues",
                    "anchor_scenario_values"):
            bad = form4_with(key, ["a", "b", "c", "d"])
            self.assertFalse(mod01.validate_record("4", bad), key)
            good = form4_with(key, ["a", "b", "c"])
            self.assertTrue(mod01.validate_record("4", good), key)

    def test_benign_name_still_passes_at_four(self):
        good = form4_with(
            "combined_anchor_like_name", ["a", "b", "c", "d"])
        self.assertTrue(mod01.validate_record("4", good))


if __name__ == "__main__":
    unittest.main()

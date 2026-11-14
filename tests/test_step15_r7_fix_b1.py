# Step 15, second run, fix wave 6, Builder 1 pins. MOD-01 only.
# Rows R6-006, R6-016, R6-017, R6-019 (MOD-01 limbs), and R6-030
# of the Round 6 register.
import time
import unittest

import crucible.mod01 as mod01


class GetLieDict(dict):
    """A dict subclass whose get reading answers the named keys
    from a supplied lie mapping, whatever stands stored."""

    def __init__(self, stored, lies):
        super().__init__(stored)
        self._lies = dict(lies)

    def get(self, key, default=None):
        if key in self._lies:
            return self._lies[key]
        return dict.get(self, key, default)


class ComponentGetLieDict(dict):
    """A dict subclass whose get reading supplies a text value
    for a named part that stands absent from its stored keys."""

    def __init__(self, stored, supplied_part):
        super().__init__(stored)
        self._supplied = supplied_part

    def get(self, key, default=None):
        if key == self._supplied and not dict.__contains__(self, key):
            return "stated value"
        return dict.get(self, key, default)


class HideContainsDict(dict):
    """A dict subclass whose contains reading denies the named
    stored keys."""

    def __init__(self, stored, hidden):
        super().__init__(stored)
        self._hidden = frozenset(hidden)

    def __contains__(self, key):
        if key in self._hidden:
            return False
        return dict.__contains__(self, key)


class ContainsTrueDict(dict):
    """A dict subclass whose contains reading answers True for
    every key, stored or not."""

    def __contains__(self, key):
        return True


class HideKeysDict(dict):
    """A dict subclass whose iteration and keys readings yield
    every stored key except the named hidden ones."""

    def __init__(self, stored, hidden):
        super().__init__(stored)
        self._hidden = frozenset(hidden)

    def __iter__(self):
        return iter(
            key for key in dict.keys(self) if key not in self._hidden)

    def keys(self):
        return [
            key for key in dict.keys(self) if key not in self._hidden]


class HideIterList(list):
    """A list subclass whose iteration yields one text value
    while it stores one integer."""

    def __iter__(self):
        return iter(("stated text",))


class StoredTextStr(str):
    """A string subclass storing one text while its string
    reading reports another."""

    def __new__(cls, stored, reported):
        instance = str.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported


class TruthyEmptyList(list):
    def __bool__(self):
        return True


class TruthyObject:
    def __bool__(self):
        return True


class LyingKeyObject:
    """A plain object whose hash and equality readings answer
    as the class name a."""

    def __hash__(self):
        return hash("a")

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def shared_shape(depth, leaf):
    value = [leaf]
    for _ in range(depth):
        value = [value, value]
    return value


class TestR6006Form15ComponentReads(unittest.TestCase):
    def test_component_supplied_by_record_get_fails(self):
        stored = mod01.minimal_valid_instance("15")
        complete = dict(stored["attacker_controlled_share"])
        del stored["attacker_controlled_share"]["numerator"]
        record = GetLieDict(
            stored, {"attacker_controlled_share": complete})
        self.assertFalse(mod01.validate_record("15", record))

    def test_component_part_supplied_by_component_get_fails(self):
        stored = mod01.minimal_valid_instance("15")
        component = dict(stored["attacker_controlled_share"])
        del component["numerator"]
        stored["attacker_controlled_share"] = ComponentGetLieDict(
            component, "numerator")
        self.assertFalse(mod01.validate_record("15", stored))

    def test_plain_missing_part_fails_control(self):
        stored = mod01.minimal_valid_instance("15")
        del stored["attacker_controlled_share"]["numerator"]
        self.assertFalse(mod01.validate_record("15", stored))

    def test_plain_complete_form15_passes_control(self):
        stored = mod01.minimal_valid_instance("15")
        self.assertTrue(mod01.validate_record("15", stored))


class TestR6006ClosedFormIterationRead(unittest.TestCase):
    def test_extra_field_hidden_by_iteration_fails(self):
        for fid in ("16", "17", "19", "20", "21"):
            stored = mod01.minimal_valid_instance(fid)
            stored["unnamed_extra_field"] = "stated value"
            record = HideKeysDict(stored, ("unnamed_extra_field",))
            self.assertFalse(
                mod01.validate_record(fid, record), fid)

    def test_extra_field_plain_fails_control(self):
        for fid in ("16", "17", "19", "20", "21"):
            stored = mod01.minimal_valid_instance(fid)
            stored["unnamed_extra_field"] = "stated value"
            self.assertFalse(mod01.validate_record(fid, stored), fid)

    def test_plain_closed_records_pass_control(self):
        for fid in ("16", "17", "19", "20", "21"):
            stored = mod01.minimal_valid_instance(fid)
            self.assertTrue(mod01.validate_record(fid, stored), fid)


class TestR6006Form1SlugRead(unittest.TestCase):
    def test_bad_slug_reported_none_by_get_fails(self):
        stored = mod01.minimal_valid_instance("1")
        stored["farm_size_steps"] = "a closed value, no marker"
        record = GetLieDict(stored, {"farm_size_steps": None})
        self.assertFalse(mod01.validate_record("1", record))

    def test_bad_slug_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("1")
        stored["farm_size_steps"] = "a closed value, no marker"
        self.assertFalse(mod01.validate_record("1", stored))

    def test_plain_form1_passes_control(self):
        stored = mod01.minimal_valid_instance("1")
        self.assertTrue(mod01.validate_record("1", stored))


class TestR6006TailBranches(unittest.TestCase):
    def test_bogus_calibration_hidden_by_contains_fails(self):
        stored = mod01.minimal_valid_instance("4")
        stored["calibration_claim_field"] = "a bogus calibration claim"
        record = HideContainsDict(stored, ("calibration_claim_field",))
        self.assertFalse(mod01.validate_record("4", record))

    def test_bogus_calibration_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("4")
        stored["calibration_claim_field"] = "a bogus calibration claim"
        self.assertFalse(mod01.validate_record("4", stored))

    def test_contains_true_for_absent_field_raises_no_bare_error(self):
        stored = mod01.minimal_valid_instance("2")
        self.assertNotIn("calibration_claim_field", stored)
        record = ContainsTrueDict(stored)
        self.assertTrue(mod01.validate_record("2", record))

    def test_bogus_store_kind_hidden_by_contains_fails(self):
        stored = mod01.minimal_valid_instance("4")
        stored["store_kind"] = "a bogus store kind"
        record = HideContainsDict(stored, ("store_kind",))
        self.assertFalse(mod01.validate_record("4", record))

    def test_bogus_store_kind_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("4")
        stored["store_kind"] = "a bogus store kind"
        self.assertFalse(mod01.validate_record("4", stored))

    def test_settled_lien_hidden_by_contains_fails(self):
        stored = mod01.minimal_valid_instance("10")
        stored["lien_state"] = "settled in the chosen escrow"
        stored["cross_seam_effect"] = True
        record = HideContainsDict(stored, ("lien_state",))
        self.assertFalse(mod01.validate_record("10", record))

    def test_cross_seam_flag_reported_false_by_get_fails(self):
        stored = mod01.minimal_valid_instance("10")
        stored["lien_state"] = "settled in the chosen escrow"
        stored["cross_seam_effect"] = True
        record = GetLieDict(stored, {"cross_seam_effect": False})
        self.assertFalse(mod01.validate_record("10", record))

    def test_settled_lien_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("10")
        stored["lien_state"] = "settled in the chosen escrow"
        stored["cross_seam_effect"] = True
        self.assertFalse(mod01.validate_record("10", stored))

    def test_lien_without_cross_seam_passes_control(self):
        stored = mod01.minimal_valid_instance("10")
        stored["lien_state"] = "settled in the chosen escrow"
        self.assertTrue(mod01.validate_record("10", stored))

    def test_parameter_integer_hidden_by_iteration_fails(self):
        stored = mod01.minimal_valid_instance("5")
        stored["parameter_values"] = HideIterList([123])
        self.assertFalse(mod01.validate_record("5", stored))

    def test_parameter_values_hidden_by_contains_fails(self):
        stored = mod01.minimal_valid_instance("5")
        stored["parameter_values"] = [123]
        record = HideContainsDict(stored, ("parameter_values",))
        self.assertFalse(mod01.validate_record("5", record))

    def test_parameter_integer_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("5")
        stored["parameter_values"] = [123]
        self.assertFalse(mod01.validate_record("5", stored))

    def test_plain_form5_passes_control(self):
        stored = mod01.minimal_valid_instance("5")
        self.assertTrue(mod01.validate_record("5", stored))


class TestR6016FoldStoredCharacters(unittest.TestCase):
    def test_normalised_characters_read_stored_text(self):
        key = StoredTextStr("amount", "notes")
        self.assertEqual(
            mod01._normalised_characters(key), list("amount"))

    def test_money_pair_under_reported_key_text_carries(self):
        pair = {
            StoredTextStr("amount", "notes"): 5,
            "currency": "USD",
        }
        self.assertTrue(mod01._carries_real_money_value(pair))

    def test_money_pair_under_reported_key_text_fails_record(self):
        stored = mod01.minimal_valid_instance("4")
        stored["payment"] = {
            StoredTextStr("amount", "notes"): 5,
            StoredTextStr("currency", "notes"): "USD",
        }
        self.assertFalse(mod01.validate_record("4", stored))

    def test_clean_key_reporting_amount_does_not_carry(self):
        pair = {
            StoredTextStr("notes", "amount"): 5,
            "currency": "USD",
        }
        self.assertFalse(mod01._carries_real_money_value(pair))

    def test_marker_key_under_reported_text_carries(self):
        key = StoredTextStr("realmoney", "notes")
        self.assertTrue(mod01._folded_key_carries(
            key, mod01._MONEY_MARKER_FOLDED))

    def test_anchor_name_under_reported_text_counts(self):
        stored = mod01.minimal_valid_instance("4")
        name = StoredTextStr("anch0r_scenario_values", "other_name")
        stored[name] = ["one", "two", "three", "four"]
        self.assertFalse(mod01.validate_record("4", stored))

    def test_anchor_name_under_reported_text_at_three_passes(self):
        stored = mod01.minimal_valid_instance("4")
        name = StoredTextStr("anch0r_scenario_values", "other_name")
        stored[name] = ["one", "two", "three"]
        self.assertTrue(mod01.validate_record("4", stored))

    def test_plain_money_pair_carries_control(self):
        pair = {"amount": 5, "currency": "USD"}
        self.assertTrue(mod01._carries_real_money_value(pair))

    def test_clean_pair_does_not_carry_control(self):
        pair = {"amount": 5, "note": "USD"}
        self.assertFalse(mod01._carries_real_money_value(pair))


def provenance_block(entries, counts, shares):
    return {
        "entries": entries,
        "excluded_class_counts": counts,
        "excluded_class_shares": shares,
    }


def plain_entry():
    return {"field": "plain field", "applicability": "applies"}


class TestR6017ProvenanceStoredForm(unittest.TestCase):
    def test_empty_list_reporting_truthy_as_field_fails(self):
        entry = {"field": TruthyEmptyList(), "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_plain_object_reporting_truthy_as_field_fails(self):
        entry = {"field": TruthyObject(), "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_empty_list_reporting_truthy_as_error_direction_fails(self):
        entry = {
            "field": "arbiter accuracy value",
            "applicability": "applies",
            "error_direction": TruthyEmptyList(),
        }
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_nonempty_list_as_field_passes_control(self):
        entry = {"field": ["stated"], "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_plain_empty_list_as_field_fails_control(self):
        entry = {"field": [], "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_lying_non_text_key_fails_key_set(self):
        block = provenance_block(
            [plain_entry()], {LyingKeyObject(): 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_lying_non_text_key_against_other_name_fails_control(self):
        block = provenance_block(
            [plain_entry()], {LyingKeyObject(): 1}, {"b": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_plain_non_text_keys_matching_pass_control(self):
        block = provenance_block(
            [plain_entry()], {1: 1}, {1: 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_plain_block_passes_control(self):
        block = provenance_block(
            [plain_entry()], {"a": 1}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))


class TestR6019WalkedStandingAcrossPaths(unittest.TestCase):
    def test_money_walk_shared_shape_depth_20_is_prompt(self):
        shape = shared_shape(20, "leaf")
        started = time.monotonic()
        result = mod01._carries_real_money_value(shape)
        elapsed = time.monotonic() - started
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_reserved_walk_shared_shape_depth_20_is_prompt(self):
        shape = shared_shape(20, "leaf")
        started = time.monotonic()
        result = mod01._carries_reserved_matter(shape)
        elapsed = time.monotonic() - started
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_money_walk_shared_money_pair_still_carries(self):
        pair = {"amount": 5, "currency": "USD"}
        shape = shared_shape(10, pair)
        self.assertTrue(mod01._carries_real_money_value(shape))

    def test_reserved_walk_shared_reserved_value_still_carries(self):
        shape = shared_shape(10, "banked real money stake behaviour")
        self.assertTrue(mod01._carries_reserved_matter(shape))

    def test_plain_chain_answers_control(self):
        value = "leaf"
        for _ in range(50):
            value = [value]
        self.assertFalse(mod01._carries_real_money_value(value))
        self.assertFalse(mod01._carries_reserved_matter(value))

    def test_deep_reach_past_bound_still_refused_control(self):
        shared = []
        deep = shared
        for _ in range(102):
            deep = [deep]
        top = [shared, deep]
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._carries_real_money_value(top)
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._carries_reserved_matter(top)


class TestR6030ThetaReading(unittest.TestCase):
    def test_amount_key_with_small_theta_matches(self):
        self.assertTrue(mod01._folded_key_matches(
            "amoun\u03b8", "amount"))

    def test_amount_key_with_capital_theta_matches(self):
        self.assertTrue(mod01._folded_key_matches(
            "amoun\u0398", "amount"))

    def test_amount_key_with_vartheta_matches(self):
        self.assertTrue(mod01._folded_key_matches(
            "amoun\u03d1", "amount"))

    def test_theta_amount_pair_fails_record(self):
        stored = mod01.minimal_valid_instance("4")
        stored["payment"] = {
            "amoun\u03b8": 5, "currency": "USD"}
        self.assertFalse(mod01.validate_record("4", stored))

    def test_theta_key_does_not_match_other_target_control(self):
        self.assertFalse(mod01._folded_key_matches(
            "amoun\u03b8", "currency"))

    def test_plain_amount_key_matches_control(self):
        self.assertTrue(mod01._folded_key_matches("amount", "amount"))


if __name__ == "__main__":
    unittest.main()

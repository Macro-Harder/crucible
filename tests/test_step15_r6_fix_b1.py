# Step 15, second run, fix wave 5, Builder 1 pins. MOD-01 only.
# Rows R5-006, R5-009 (MOD-01 limb), R5-010, R5-016, R5-017,
# R5-018 (MOD-01 limb), R5-023 (MOD-01 limb), and R5-035
# of the Round 5 register.
import unittest

import crucible.mod01 as mod01


class GhostDict(dict):
    """A dict subclass whose contains, get, and item readings answer
    for the named ghost keys from no stored entry."""

    def __init__(self, stored, ghost_keys):
        super().__init__(stored)
        self._ghost = frozenset(ghost_keys)

    def __contains__(self, key):
        if key in self._ghost:
            return True
        return dict.__contains__(self, key)

    def __getitem__(self, key):
        if key in self._ghost and not dict.__contains__(self, key):
            return "stated value"
        return dict.__getitem__(self, key)

    def get(self, key, default=None):
        if key in self._ghost and not dict.__contains__(self, key):
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


class HideIterList(list):
    def __iter__(self):
        return iter(())


class HideIterTuple(tuple):
    def __iter__(self):
        return iter(())


class LyingLenList(list):
    def __len__(self):
        return 3


class LyingLenTuple(tuple):
    def __len__(self):
        return 3


class LyingBoolStr(str):
    def __bool__(self):
        return True


class LyingKeyStr(str):
    def __hash__(self):
        return str.__hash__("a")

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def form4_with(key, value):
    instance = mod01.minimal_valid_instance("4")
    instance[key] = value
    return instance


def form4_anchor(name, count):
    instance = mod01.minimal_valid_instance("4")
    instance[name] = ["value %d" % index for index in range(count)]
    return instance


def tuple_chain(length):
    value = "leaf"
    for _ in range(length):
        value = (value,)
    return value


def frozenset_chain(length):
    value = frozenset()
    for _ in range(length):
        value = frozenset((value,))
    return value


class TestR5006ConditionalLoopBaseReadings(unittest.TestCase):
    def test_form2_conditional_field_ghosted_absent_fails(self):
        stored = mod01.minimal_valid_instance("2")
        stored["belongs_to_decay_arm"] = True
        self.assertNotIn("decay_slice", stored)
        record = GhostDict(stored, ("decay_slice",))
        self.assertFalse(mod01.validate_record("2", record))

    def test_form2_conditional_field_plain_absent_fails_control(self):
        stored = mod01.minimal_valid_instance("2")
        stored["belongs_to_decay_arm"] = True
        self.assertFalse(mod01.validate_record("2", stored))

    def test_form13_conditional_field_ghosted_absent_fails(self):
        condition = mod01.field_conditions("13")[0]
        stored = mod01.minimal_valid_instance(
            "13", condition_holds=condition)
        self.assertTrue(stored["is_anchor_scenario_run"])
        del stored["anchor_scenario_identity"]
        record = GhostDict(stored, ("anchor_scenario_identity",))
        self.assertFalse(mod01.validate_record("13", record))

    def test_form2_ghost_wrapped_complete_record_passes_control(self):
        condition = mod01.field_conditions("2")[0]
        stored = mod01.minimal_valid_instance(
            "2", condition_holds=condition)
        record = GhostDict(stored, ("decay_slice",))
        self.assertTrue(mod01.validate_record("2", record))

    def test_form2_condition_not_holding_passes_control(self):
        stored = mod01.minimal_valid_instance("2")
        self.assertTrue(mod01.validate_record("2", stored))


class TestR5006EventlogBaseReadings(unittest.TestCase):
    def test_eventlog_base_field_ghosted_absent_fails(self):
        stored = mod01.minimal_valid_instance("36")
        del stored["run_identifier"]
        record = GhostDict(stored, ("run_identifier",))
        self.assertFalse(mod01.validate_record("36", record))

    def test_eventlog_base_field_plain_absent_fails_control(self):
        stored = mod01.minimal_valid_instance("36")
        del stored["run_identifier"]
        self.assertFalse(mod01.validate_record("36", stored))

    def test_eventlog_forbidden_field_hidden_by_contains_passes_not(self):
        stored = mod01.minimal_valid_instance("36")
        stored["agent_identifier"] = "stated agent"
        record = HideContainsDict(stored, ("agent_identifier",))
        self.assertFalse(mod01.validate_record("36", record))

    def test_eventlog_forbidden_field_plain_fails_control(self):
        stored = mod01.minimal_valid_instance("36")
        stored["agent_identifier"] = "stated agent"
        self.assertFalse(mod01.validate_record("36", stored))

    def test_eventlog_agent_field_ghosted_absent_fails(self):
        stored = mod01.minimal_valid_instance("36", entry_kind="agent")
        del stored["agent_identifier"]
        record = GhostDict(stored, ("agent_identifier",))
        self.assertFalse(mod01.validate_record("36", record))

    def test_eventlog_supersession_field_ghosted_absent_fails(self):
        stored = mod01.minimal_valid_instance(
            "36", entry_kind="supersession")
        del stored["resume_attempt_identifier"]
        record = GhostDict(stored, ("resume_attempt_identifier",))
        self.assertFalse(mod01.validate_record("36", record))

    def test_eventlog_plain_kinds_pass_control(self):
        for kind in ("ordinary", "agent", "supersession"):
            stored = mod01.minimal_valid_instance("36", entry_kind=kind)
            self.assertTrue(mod01.validate_record("36", stored))


class TestR5009CombinedLeetAndDropReadings(unittest.TestCase):
    def test_anchor_leet_and_drop_name_fails_at_four(self):
        bad = form4_anchor("anch0r9_scenario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_anchor_leet_and_drop_name_passes_at_three_control(self):
        good = form4_anchor("anch0r9_scenario_values", 3)
        self.assertTrue(mod01.validate_record("4", good))

    def test_anchor_drop_and_two_readings_name_fails_at_four(self):
        bad = form4_anchor("anchor9_scenar1o_va1ues", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_anchor_drop_and_two_readings_name_passes_at_three_control(self):
        good = form4_anchor("anchor9_scenar1o_va1ues", 3)
        self.assertTrue(mod01.validate_record("4", good))

    def test_anchor_combined_name_matches_fold_directly(self):
        self.assertTrue(mod01._folded_key_matches(
            "anch0r9_scenario_values",
            mod01._ANCHOR_VALUES_FIELD_FOLDED))
        self.assertTrue(mod01._folded_key_matches(
            "anchor9_scenar1o_va1ues",
            mod01._ANCHOR_VALUES_FIELD_FOLDED))

    def test_amount_key_leet_and_drop_pair_fails(self):
        bad = form4_with(
            "payment", {"4m0unt9": 5, "currency": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_amount_key_combined_matches_directly(self):
        self.assertTrue(mod01._folded_key_matches("4m0unt9", "amount"))

    def test_marker_key_leet_and_drop_fails(self):
        bad = form4_with("r3almo9ney", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_one_reading_and_drop_fails(self):
        bad = form4_with("rea1mo9ney", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_combined_carries_directly(self):
        self.assertTrue(mod01._folded_key_carries(
            "r3almo9ney", mod01._MONEY_MARKER_FOLDED))
        self.assertTrue(mod01._folded_key_carries(
            "rea1mo9ney", mod01._MONEY_MARKER_FOLDED))

    def test_leet_only_anchor_name_fails_at_four_control(self):
        bad = form4_anchor("anch0r_scenario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_drop_only_anchor_name_fails_at_four_control(self):
        bad = form4_anchor("anchor9_scenario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_plain_money_pair_fails_control(self):
        bad = form4_with("payment", {"amount": 5, "currency": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_benign_name_at_four_passes_control(self):
        good = form4_anchor("combined_anchor_like_name", 4)
        self.assertTrue(mod01.validate_record("4", good))


class TestR5010FoldLetterClasses(unittest.TestCase):
    def test_anchor_name_with_ha_for_h_fails_at_four(self):
        bad = form4_anchor("anc\u0445or_scenario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_anchor_name_with_capital_ha_for_h_fails_at_four(self):
        bad = form4_anchor("anc\u0425or_scenario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_anchor_name_with_ha_passes_at_three_control(self):
        good = form4_anchor("anc\u0445or_scenario_values", 3)
        self.assertTrue(mod01.validate_record("4", good))

    def test_anchor_name_with_eta_in_scenario_fails_at_four(self):
        bad = form4_anchor("anchor_sc\u03b7nario_values", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_anchor_name_with_eta_in_values_fails_at_four(self):
        bad = form4_anchor("anchor_scenario_valu\u03b7s", 4)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_currency_key_with_eta_fails(self):
        bad = form4_with(
            "payment", {"amount": 5, "curr\u03b7ncy": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_currency_key_with_capital_eta_fails(self):
        bad = form4_with(
            "payment", {"amount": 5, "curr\u0397ncy": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_currency_key_with_short_i_for_y_fails(self):
        bad = form4_with(
            "payment", {"amount": 5, "currenc\u0439": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_currency_key_with_yery_for_y_fails(self):
        bad = form4_with(
            "payment", {"amount": 5, "currenc\u044b": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_eta_for_first_e_fails(self):
        bad = form4_with("r\u03b7almoney", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_eta_for_money_e_fails(self):
        bad = form4_with("realmon\u03b7y", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_short_i_for_y_fails(self):
        bad = form4_with("realmone\u0439", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_yery_for_y_fails(self):
        bad = form4_with("realmone\u044b", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_yu_fails(self):
        bad = form4_with("realmone\u044e", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_marker_key_with_ya_fails(self):
        bad = form4_with("realmone\u044f", 5)
        self.assertFalse(mod01.validate_record("4", bad))

    def test_short_i_currency_matches_fold_directly(self):
        self.assertTrue(mod01._folded_key_matches(
            "currenc\u0439", "currency"))

    def test_plain_money_pair_fails_control(self):
        bad = form4_with("payment", {"amount": 5, "currency": "USD"})
        self.assertFalse(mod01.validate_record("4", bad))

    def test_clean_pair_passes_control(self):
        good = form4_with("payment", {"amount": 5, "note": "USD"})
        self.assertTrue(mod01.validate_record("4", good))

    def test_benign_eta_name_at_four_passes_control(self):
        good = form4_anchor("summ\u03b7ry_values", 4)
        self.assertTrue(mod01.validate_record("4", good))


def provenance_block(entries, counts, shares):
    return {
        "entries": entries,
        "excluded_class_counts": counts,
        "excluded_class_shares": shares,
    }


def plain_entry():
    return {"field": "plain field", "applicability": "applies"}


class TestR5016ProvenanceHandedReadings(unittest.TestCase):
    def test_entry_field_empty_text_with_lying_bool_fails(self):
        entry = {"field": LyingBoolStr(""), "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_entry_field_plain_empty_fails_control(self):
        entry = {"field": "", "applicability": "applies"}
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_error_direction_empty_text_with_lying_bool_fails(self):
        entry = {
            "field": "arbiter accuracy value",
            "applicability": "applies",
            "error_direction": LyingBoolStr(""),
        }
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_error_direction_plain_empty_fails_control(self):
        entry = {
            "field": "arbiter accuracy value",
            "applicability": "applies",
            "error_direction": "",
        }
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_error_direction_stated_passes_control(self):
        entry = {
            "field": "arbiter accuracy value",
            "applicability": "applies",
            "error_direction": "symmetric",
        }
        block = provenance_block([entry], {"a": 1}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_counts_key_lying_as_shares_key_fails(self):
        block = provenance_block(
            [plain_entry()], {LyingKeyStr("b"): 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_counts_key_plain_mismatch_fails_control(self):
        block = provenance_block(
            [plain_entry()], {"b": 1}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_plain_block_passes_control(self):
        block = provenance_block(
            [plain_entry()], {"a": 1}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))


class TestR5017RealMoneyContainerBaseIteration(unittest.TestCase):
    def test_money_pair_hidden_by_list_iteration_fails(self):
        pair = {"amount": 5, "currency": "USD"}
        bad = form4_with("payment_forms", HideIterList([pair]))
        self.assertFalse(mod01.validate_record("4", bad))

    def test_money_pair_hidden_by_tuple_iteration_fails(self):
        pair = {"amount": 5, "currency": "USD"}
        bad = form4_with("payment_forms", HideIterTuple((pair,)))
        self.assertFalse(mod01.validate_record("4", bad))

    def test_money_read_directly_on_hidden_list(self):
        pair = {"amount": 5, "currency": "USD"}
        self.assertTrue(mod01._carries_real_money_value(
            HideIterList([pair])))

    def test_money_pair_in_plain_list_fails_control(self):
        pair = {"amount": 5, "currency": "USD"}
        bad = form4_with("payment_forms", [pair])
        self.assertFalse(mod01.validate_record("4", bad))

    def test_clean_hidden_list_passes_control(self):
        good = form4_with("payment_forms", HideIterList(["a note"]))
        self.assertTrue(mod01.validate_record("4", good))


class TestR5018AnchorCountBaseLength(unittest.TestCase):
    def test_anchor_values_lying_length_list_fails_at_four(self):
        instance = mod01.minimal_valid_instance("4")
        instance["anchor_scenario_values"] = LyingLenList(
            ["one", "two", "three", "four"])
        self.assertFalse(mod01.validate_record("4", instance))

    def test_anchor_values_lying_length_tuple_fails_at_four(self):
        instance = mod01.minimal_valid_instance("4")
        instance["anchor_scenario_values"] = LyingLenTuple(
            ("one", "two", "three", "four"))
        self.assertFalse(mod01.validate_record("4", instance))

    def test_anchor_values_plain_four_fails_control(self):
        instance = mod01.minimal_valid_instance("4")
        instance["anchor_scenario_values"] = [
            "one", "two", "three", "four"]
        self.assertFalse(mod01.validate_record("4", instance))

    def test_anchor_values_lying_length_three_stored_passes_control(self):
        instance = mod01.minimal_valid_instance("4")
        instance["anchor_scenario_values"] = LyingLenList(
            ["one", "two", "three"])
        self.assertTrue(mod01.validate_record("4", instance))


class TestR5023GuardCopyableSharedRewalk(unittest.TestCase):
    def test_shared_chain_guard_calls_stay_near_linear(self):
        shared = "leaf"
        for _ in range(16):
            shared = [shared, shared]
        calls = []
        original = mod01._traversal_guard

        def counting(value, depth, seen):
            calls.append(1)
            return original(value, depth, seen)

        mod01._traversal_guard = counting
        try:
            mod01._guard_copyable(shared)
        finally:
            mod01._traversal_guard = original
        self.assertLessEqual(len(calls), 1000)

    def test_shared_subchain_shared_twice_passes_control(self):
        subchain = "leaf"
        for _ in range(50):
            subchain = [subchain]
        value = {"first": subchain, "second": subchain}
        mod01._guard_copyable(value)

    def test_cycle_still_refused_control(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._guard_copyable(cyclic)

    def test_deep_chain_still_refused_control(self):
        chain = "leaf"
        for _ in range(102):
            chain = [chain]
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._guard_copyable(chain)


class TestR5035RealMoneyReadDictKeys(unittest.TestCase):
    def test_tuple_chain_key_past_bound_refused(self):
        value = {tuple_chain(101): "stated value"}
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._carries_real_money_value(value)

    def test_frozenset_chain_key_past_bound_refused(self):
        value = {frozenset_chain(101): "stated value"}
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._carries_real_money_value(value)

    def test_tuple_chain_key_inside_bound_returns_false_control(self):
        value = {tuple_chain(99): "stated value"}
        self.assertFalse(mod01._carries_real_money_value(value))

    def test_value_chain_past_bound_refused_control(self):
        chain = "leaf"
        for _ in range(102):
            chain = [chain]
        with self.assertRaises(mod01.RecordTraversalFailure):
            mod01._carries_real_money_value({"note": chain})

    def test_plain_pair_still_read_control(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"amount": 5, "currency": "USD"}))


if __name__ == "__main__":
    unittest.main()

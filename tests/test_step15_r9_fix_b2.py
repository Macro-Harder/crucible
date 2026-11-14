"""Pin tests for rows R8-012, R8-013, and R8-014 at MOD-02.

Row R8-012 covers the closed vocabulary judgements at
battery_verdict_state, determinism_statement_permitted, and
validate_open_limb_standing. Row R8-013 covers the plain
equality return at validate_generator_state_carriage. Row
R8-014 covers the handed record readings at
validate_battery_record, battery_record_counts_as_run, and
validate_exposure_log_entry. Every judgement stands on the
stored contents read through base class operations, never on
a reading a handed value supplies.
"""

import unittest

from crucible import mod02


class EqStr(str):
    """A text value whose equality reading answers True always."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqDict(dict):
    """A dict whose equality reading answers True always."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = None


class GetLieDict(dict):
    """A dict whose get reading reports a handed mapping."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class KeysLieDict(dict):
    """A dict whose keys reading reports a handed field list."""

    def __init__(self, stored, reported_keys):
        dict.__init__(self, stored)
        self._reported_keys = reported_keys

    def keys(self):
        return list(self._reported_keys)


def stored_text(value):
    return str.__str__(value)


COMPLETE_SINGLE = {"family_a": {"outcome": 1}, "family_b": {"outcome": 2}}
COMPLETE_INTER = {"family_a": "recorded", "family_b": "recorded"}


def complete_battery_record():
    return {
        "single_stream_results": dict(COMPLETE_SINGLE),
        "inter_stream_element": dict(COMPLETE_INTER),
    }


class TestR8012BatteryVerdictState(unittest.TestCase):

    def test_eq_lie_storing_bogus_stands_gated(self):
        result = mod02.battery_verdict_state(
            inter_stream_element_recorded=True, verdict_recorded=True,
            verdict=EqStr("bogus"))
        self.assertEqual(stored_text(result), "gated")

    def test_plain_verdicts_stand_both_ways(self):
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            True, True, "passed")), "passed")
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            True, True, "failed")), "failed")
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            True, True, "gated")), "gated")
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            True, True, "bogus")), "gated")
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            False, True, "passed")), "gated")
        self.assertEqual(stored_text(mod02.battery_verdict_state(
            True, False, "passed")), "gated")

    def test_eq_lie_storing_a_stated_state_returns_that_state(self):
        result = mod02.battery_verdict_state(
            inter_stream_element_recorded=True, verdict_recorded=True,
            verdict=EqStr("passed"))
        self.assertEqual(stored_text(result), "passed")
        result = mod02.battery_verdict_state(
            inter_stream_element_recorded=True, verdict_recorded=True,
            verdict=EqStr("failed"))
        self.assertEqual(stored_text(result), "failed")


class TestR8012DeterminismStatement(unittest.TestCase):

    def test_eq_lie_storing_bogus_permits_nothing(self):
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state=EqStr("bogus")), False)

    def test_eq_lie_storing_failed_without_corrected_pass_permits_nothing(self):
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state=EqStr("failed"),
            corrected_battery_passed=False), False)

    def test_plain_states_stand_both_ways(self):
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state="passed"), True)
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state="failed", corrected_battery_passed=False),
            False)
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state="failed", corrected_battery_passed=True),
            True)
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state="gated"), False)
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state="bogus"), False)
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state=None), False)

    def test_eq_lie_storing_passed_permits(self):
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state=EqStr("passed")), True)

    def test_eq_lie_storing_failed_with_corrected_pass_permits(self):
        self.assertIs(mod02.determinism_statement_permitted(
            battery_state=EqStr("failed"),
            corrected_battery_passed=True), True)


class TestR8012OpenLimbStanding(unittest.TestCase):

    def test_eq_lie_limb_storing_bogus_stands_refused(self):
        self.assertIs(mod02.validate_open_limb_standing(
            EqStr("bogus"), named_as="open"), False)

    def test_eq_lie_named_as_storing_settled_stands_refused(self):
        self.assertIs(mod02.validate_open_limb_standing(
            "substream extension", named_as=EqStr("settled")), False)

    def test_eq_lie_limb_and_named_as_both_lying_stand_refused(self):
        self.assertIs(mod02.validate_open_limb_standing(
            EqStr("bogus"), named_as=EqStr("bogus")), False)

    def test_plain_open_limb_forms_stand_both_ways(self):
        self.assertIs(mod02.validate_open_limb_standing(
            "substream extension", named_as="open"), True)
        self.assertIs(mod02.validate_open_limb_standing(
            "analysis resampling", named_as="open"), True)
        self.assertIs(mod02.validate_open_limb_standing(
            "bogus", named_as="open"), False)
        self.assertIs(mod02.validate_open_limb_standing(
            "substream extension", named_as="settled"), False)
        self.assertIs(mod02.validate_open_limb_standing(
            "substream extension", named_as=None), False)

    def test_eq_lie_storing_a_named_open_limb_and_open_passes(self):
        self.assertIs(mod02.validate_open_limb_standing(
            EqStr("substream extension"), named_as=EqStr("open")),
            True)


class TestR8013GeneratorStateCarriage(unittest.TestCase):

    def test_dict_eq_lie_storing_a_different_state_stands_refused(self):
        held = EqDict({"a": 1})
        self.assertIs(mod02.validate_generator_state_carriage(
            held, {"a": 2}), False)

    def test_nested_dict_eq_lie_storing_a_different_value_stands_refused(self):
        held = {"slot": EqDict({"p": 1})}
        consumed = {"slot": {"p": 999}}
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_nested_text_eq_lie_storing_a_different_value_stands_refused(self):
        held = {"slot": EqStr("stored")}
        consumed = {"slot": "other"}
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), False)

    def test_plain_states_stand_both_ways(self):
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 1}), True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 2}), False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1, "b": {"c": [1, 2]}}, {"a": 1, "b": {"c": [1, 2]}}),
            True)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1, "b": {"c": [1, 2]}}, {"a": 1, "b": {"c": [1, 3]}}),
            False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"a": 1, "b": 2}), False)
        self.assertIs(mod02.validate_generator_state_carriage(
            {"a": 1}, {"b": 1}), False)

    def test_dict_eq_lie_storing_the_same_state_passes(self):
        held = EqDict({"a": 1})
        self.assertIs(mod02.validate_generator_state_carriage(
            held, {"a": 1}), True)

    def test_nested_dict_eq_lie_storing_the_same_value_passes(self):
        held = {"slot": EqDict({"p": 1})}
        consumed = {"slot": {"p": 1}}
        self.assertIs(mod02.validate_generator_state_carriage(
            held, consumed), True)


class TestR8014BatteryRecord(unittest.TestCase):

    def test_get_lie_storing_nothing_stands_refused(self):
        record = GetLieDict({}, complete_battery_record())
        self.assertIs(mod02.validate_battery_record(record), False)

    def test_inter_get_lie_storing_nothing_stands_refused(self):
        record = complete_battery_record()
        record["inter_stream_element"] = GetLieDict(
            {}, dict(COMPLETE_INTER))
        self.assertIs(mod02.validate_battery_record(record), False)

    def test_plain_battery_records_stand_both_ways(self):
        self.assertIs(mod02.validate_battery_record(
            complete_battery_record()), True)
        incomplete = complete_battery_record()
        incomplete["inter_stream_element"] = {"family_a": "recorded"}
        self.assertIs(mod02.validate_battery_record(incomplete), False)
        self.assertIs(mod02.validate_battery_record({}), False)
        self.assertIs(mod02.validate_battery_record(None), False)
        self.assertIs(mod02.validate_battery_record(
            {"single_stream_results": dict(COMPLETE_SINGLE)}), False)

    def test_get_lie_subclass_storing_a_complete_record_passes(self):
        record = GetLieDict(
            complete_battery_record(), complete_battery_record())
        self.assertIs(mod02.validate_battery_record(record), True)


class TestR8014BatteryRecordCountsAsRun(unittest.TestCase):

    def test_get_lie_storing_nothing_stands_refused(self):
        record = GetLieDict({}, {"advance_sample_size_stated": True})
        self.assertIs(mod02.battery_record_counts_as_run(record),
                      False)

    def test_plain_records_stand_both_ways(self):
        self.assertIs(mod02.battery_record_counts_as_run(
            {"advance_sample_size_stated": True}), True)
        self.assertIs(mod02.battery_record_counts_as_run(
            {"advance_sample_size_stated": False}), False)
        self.assertIs(mod02.battery_record_counts_as_run({}), False)
        self.assertIs(mod02.battery_record_counts_as_run(None), False)

    def test_get_lie_subclass_storing_the_stated_size_passes(self):
        record = GetLieDict(
            {"advance_sample_size_stated": True},
            {"advance_sample_size_stated": True})
        self.assertIs(mod02.battery_record_counts_as_run(record),
                      True)


class TestR8014ExposureLogEntry(unittest.TestCase):

    def test_keys_lie_storing_nothing_stands_refused(self):
        entry = KeysLieDict({}, mod02.exposure_log_fields())
        self.assertIs(mod02.validate_exposure_log_entry(entry),
                      False)

    def test_plain_entries_stand_both_ways(self):
        self.assertIs(mod02.validate_exposure_log_entry(
            mod02.make_exposure_log_entry()), True)
        self.assertIs(mod02.validate_exposure_log_entry(
            {"family and run identifier": "run 1"}), False)
        self.assertIs(mod02.validate_exposure_log_entry({}), False)
        self.assertIs(mod02.validate_exposure_log_entry(None), False)
        wider = mod02.make_exposure_log_entry()
        wider["one further field"] = "recorded"
        self.assertIs(mod02.validate_exposure_log_entry(wider), True)

    def test_keys_lie_subclass_storing_a_complete_entry_passes(self):
        stored = mod02.make_exposure_log_entry()
        entry = KeysLieDict(stored, mod02.exposure_log_fields())
        self.assertIs(mod02.validate_exposure_log_entry(entry),
                      True)


if __name__ == "__main__":
    unittest.main()

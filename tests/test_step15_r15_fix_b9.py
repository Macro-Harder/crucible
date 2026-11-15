"""Pins for fix wave 14, Builder 9 (Group 9): rows R14-069 to
R14-075 and R14-077 to R14-085 of the Round 14 register. Row
R14-076 stands assigned to Group 7 and takes no pin here.

The weekly count, outside call, flag, and error carriage command
and sentence family across MOD-10, MOD-11, MOD-12, and MOD-14.
"""

import unittest

import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod12 as mod12
import crucible.mod14 as mod14
import crucible.mod16 as mod16


def message_of(fn):
    try:
        fn()
    except Exception as error:
        return str(error)
    raise AssertionError("act did not raise")


class LyingGetRecord(dict):
    """A dict storing one week and identifiers whose get reports
    another week and other identifiers."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class EvilEqText(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class LyingIterList(list):
    def __iter__(self):
        return iter(["u9", "u8"])


PERSON_SENTENCE = (
    "flag evaluation by a person is barred: the flag rule stands "
    "evaluated by a program alone, and no flag evaluation stands "
    "performed")


class TestR14069WeeklyAbsentInputs(unittest.TestCase):
    def test_direct_act_absent_records_refused(self):
        message = message_of(
            lambda: mod14.weekly_headline_count(None, "W1"))
        self.assertIn("summary_records", message)

    def test_direct_act_absent_week_refused(self):
        records = [{"week": "W1", "headline_unit_identifiers": ["u1"]}]
        message = message_of(
            lambda: mod14.weekly_headline_count(records, None))
        self.assertIn("week", message)

    def test_command_no_payload_is_a_failure_not_a_zero(self):
        result = mod14.run_command("weekly_headline_count")
        self.assertIn("failure", result)
        self.assertNotIn("count", result)

    def test_command_records_without_week_is_a_failure(self):
        result = mod14.run_command("weekly_headline_count", {
            "summary_records": [
                {"week": "W1", "headline_unit_identifiers": ["u1"]}]})
        self.assertIn("failure", result)

    def test_command_week_without_records_is_a_failure(self):
        result = mod14.run_command(
            "weekly_headline_count", {"week": "W1"})
        self.assertIn("failure", result)

    def test_supplied_empty_week_still_counts_zero(self):
        result = mod14.run_command("weekly_headline_count", {
            "summary_records": [], "week": "W1"})
        self.assertEqual(result, {"count": 0, "week": "W1"})
        self.assertEqual(mod14.weekly_headline_count([], "W1"), 0)


class TestR14070WeeklyStoredReadings(unittest.TestCase):
    def test_record_counted_on_stored_week_not_reported(self):
        record = LyingGetRecord(
            {"week": 99, "headline_unit_identifiers": ["u1"]},
            {"week": 3,
             "headline_unit_identifiers": ["u1", "u2", "u3", "u4", "u5"]})
        self.assertEqual(mod11.weekly_count([record], 3), 0)
        self.assertEqual(mod11.weekly_count([record], 99), 1)

    def test_record_storing_the_week_not_silently_passed(self):
        record = LyingGetRecord(
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W2", "headline_unit_identifiers": []})
        self.assertEqual(mod11.weekly_count([record], "W1"), 1)


class TestR14071WeeklyIdentifierReadings(unittest.TestCase):
    def test_evil_equality_does_not_suppress_a_count(self):
        records = [{"week": "W1", "headline_unit_identifiers": [
            EvilEqText("u1"), "u2"]}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 2)

    def test_lying_iteration_field_counts_stored_identifiers(self):
        field = LyingIterList(["u1"])
        records = [{"week": "W1", "headline_unit_identifiers": field}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 1)


class TestR14072WeeklyIdentifierForm(unittest.TestCase):
    def test_word_identifiers_refused_in_named_form(self):
        records = [{"week": "W1", "headline_unit_identifiers": [
            "bogus", "also bogus"]}]
        message = message_of(lambda: mod11.weekly_count(records, "W1"))
        self.assertIn("no unit identifier form", message)

    def test_number_identifiers_refused(self):
        records = [{"week": "W1", "headline_unit_identifiers": [123, 456]}]
        message = message_of(lambda: mod11.weekly_count(records, "W1"))
        self.assertIn("no unit identifier form", message)

    def test_none_beside_a_unit_refused(self):
        records = [{"week": "W1", "headline_unit_identifiers": [
            "u1", None, ""]}]
        message = message_of(lambda: mod11.weekly_count(records, "W1"))
        self.assertIn("no unit identifier form", message)

    def test_bare_string_field_in_form_counts_as_one(self):
        records = [{"week": "W1", "headline_unit_identifiers": "u7"}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 1)

    def test_container_element_stands_at_its_wave13_bound(self):
        # The standing wave 13 pin counts a list in place of an
        # identifier as one at both acts; the charged forms of
        # row R14-072 are the scalar forms above, so the cure
        # stands bounded there and this standing is kept.
        records = [{"week": "W1", "headline_unit_identifiers": [["u1"]]}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 1)


class TestR14073WeeklyWholeArgumentForms(unittest.TestCase):
    def test_number_argument_named_list_refusal(self):
        message = message_of(lambda: mod11.weekly_count(42, "W1"))
        self.assertIn("list", message)
        self.assertNotIn("not iterable", message)

    def test_mapping_argument_named_list_refusal(self):
        handed = {"week": "W1", "headline_unit_identifiers": ["u1"]}
        message = message_of(lambda: mod11.weekly_count(handed, "W1"))
        self.assertIn("list", message)
        self.assertNotIn("no week field", message)

    def test_text_argument_named_list_refusal(self):
        message = message_of(lambda: mod11.weekly_count("text", "W1"))
        self.assertIn("list", message)

    def test_generator_argument_refused_as_at_mod14(self):
        def handed():
            yield {"week": "W1", "headline_unit_identifiers": ["u1"]}
        message = message_of(lambda: mod11.weekly_count(handed(), "W1"))
        self.assertIn("list", message)


class TestR14074OutsideCallKeyForms(unittest.TestCase):
    def test_calls_under_an_unread_key_refused_naming_keys(self):
        log = {"log": [{"outside_call": True}]}
        message = message_of(
            lambda: mod14.outside_call_check({"entries": []}, log))
        self.assertIn("calls", message)
        self.assertIn("entries", message)

    def test_outside_mark_under_an_unread_key_refused(self):
        log = {"calls": [{"outside": True}]}
        message = message_of(
            lambda: mod14.outside_call_check({"entries": []}, log))
        self.assertIn("outside_call", message)

    def test_bare_text_call_entry_refused(self):
        log = {"calls": ["https://example.com"]}
        message = message_of(
            lambda: mod14.outside_call_check({"entries": []}, log))
        self.assertIn("outside_call", message)

    def test_calls_in_no_list_form_refused(self):
        log = {"calls": "{\"outside_call\": true}"}
        message = message_of(
            lambda: mod14.outside_call_check({"entries": []}, log))
        self.assertIn("calls", message)

    def test_unknown_log_key_refused(self):
        log = {"calls": [], "notes": "x"}
        message = message_of(
            lambda: mod14.outside_call_check({"entries": []}, log))
        self.assertIn("notes", message)

    def test_lawful_forms_stand(self):
        clean = mod14.outside_call_check(
            {"entries": []}, {"calls": [{"outside_call": False}]})
        self.assertEqual(clean["outcome"], "no outside calls read")
        present = mod14.outside_call_check(
            {"entries": []}, {"entries": [{"outside_call": True}]})
        self.assertEqual(present["outcome"], "outside calls present")
        empty = mod14.outside_call_check({"entries": []}, {})
        self.assertEqual(empty["outcome"], "no outside calls read")


class TestR14075OutsideCallValueVocabulary(unittest.TestCase):
    def outcome(self, value):
        return mod14.outside_call_check(
            {"entries": []},
            {"calls": [{"outside_call": value}]})["outcome"]

    def test_text_false_reads_as_no_outside_call(self):
        self.assertEqual(self.outcome("false"), "no outside calls read")
        self.assertEqual(self.outcome("no"), "no outside calls read")
        self.assertEqual(self.outcome("False"), "no outside calls read")

    def test_text_true_reads_as_outside_call(self):
        self.assertEqual(self.outcome("true"), "outside calls present")
        self.assertEqual(self.outcome("yes"), "outside calls present")

    def test_number_marks(self):
        self.assertEqual(self.outcome(1), "outside calls present")
        self.assertEqual(self.outcome(0), "no outside calls read")

    def test_unstated_value_refused(self):
        message = message_of(lambda: self.outcome("perhaps"))
        self.assertIn("outside_call", message)
        message = message_of(lambda: self.outcome(2))
        self.assertIn("outside_call", message)


class TestR14077PersonBarFirstAtShell(unittest.TestCase):
    def record(self):
        return {"run_id": "r-b9-77", "retention_tier": "Tier 2"}

    def test_person_promote_bad_tier_draws_person_sentence(self):
        message = message_of(lambda: mod14.flag_evaluation(
            self.record(), inputs={"flag_conditions_fired": ["c1"]},
            outcome="promote", tier="Tier 9", actor="person"))
        self.assertEqual(message, PERSON_SENTENCE)

    def test_person_promote_no_inputs_draws_person_sentence(self):
        message = message_of(lambda: mod14.flag_evaluation(
            self.record(), outcome="promote", tier="Tier 3",
            actor="person"))
        self.assertEqual(message, PERSON_SENTENCE)

    def test_person_promote_no_condition_draws_person_sentence(self):
        message = message_of(lambda: mod14.flag_evaluation(
            self.record(), inputs={"flag_conditions_fired": []},
            outcome="promote", tier="Tier 3", actor="person"))
        self.assertEqual(message, PERSON_SENTENCE)


class TestR14078TierZeroVocabulary(unittest.TestCase):
    def test_promotion_to_tier_zero_effects_at_shell(self):
        result = mod14.flag_evaluation(
            {"run_id": "r-b9-78"},
            inputs={"flag_conditions_fired": ["c1"]},
            outcome="promote", tier="Tier 0")
        self.assertEqual(result["retention_tier"], "Tier 0")

    def test_tier_zero_below_a_record_agrees_with_mod10(self):
        record = {"run_id": "r-b9-78b", "retention_tier": "Tier 1"}
        handed = {"flag_conditions_fired": ["c1"]}
        shell = message_of(lambda: mod14.flag_evaluation(
            dict(record), inputs=handed, outcome="promote", tier="Tier 0"))
        direct = message_of(lambda: mod10.apply_flag_evaluation(
            dict(record), inputs=handed, outcome="promote", tier="Tier 0"))
        self.assertEqual(shell, direct)


class TestR14079NoTierDivergence(unittest.TestCase):
    def test_no_tier_sentence_agrees_word_for_word(self):
        record = {"run_id": "r-b9-79", "retention_tier": "Tier 2"}
        handed = {"flag_conditions_fired": ["c1"]}
        shell = message_of(lambda: mod14.flag_evaluation(
            dict(record), inputs=handed, outcome="promote"))
        direct = message_of(lambda: mod10.apply_flag_evaluation(
            dict(record), inputs=handed, outcome="promote"))
        self.assertEqual(shell, direct)
        self.assertEqual(
            shell,
            "a promote outcome with no tier stands refused: no "
            "promotion stands effected by it")


class TestR14080InputsInNoRecordForm(unittest.TestCase):
    def test_each_form_names_the_inputs_fault_at_both_acts(self):
        record = {"run_id": "r-b9-80", "retention_tier": "Tier 1"}
        for handed in ("text", ["x"], 42):
            shell = message_of(lambda: mod14.flag_evaluation(
                dict(record), inputs=handed, outcome="promote",
                tier="Tier 2"))
            direct = message_of(lambda: mod10.apply_flag_evaluation(
                dict(record), inputs=handed, outcome="promote",
                tier="Tier 2"))
            self.assertEqual(shell, direct)
            self.assertIn("no record form", shell)
            self.assertIn("mapping", shell)


class TestR14081DemoteTierSentenceConsequence(unittest.TestCase):
    def test_stated_tier_below_record_tier_states_consequence(self):
        record = {"run_id": "r-b9-81", "retention_tier": "Tier 2"}
        message = message_of(lambda: mod10.apply_flag_evaluation(
            record, tier="Tier 1"))
        self.assertEqual(
            message,
            "the flag rule never demotes: the stated tier stands "
            "below the record tier, and no demotion stands effected "
            "by it")


class TestR14082VocabularyRefusalsNameVocabulary(unittest.TestCase):
    def test_start_run_class_refusal_names_the_classes(self):
        result = mod12.start_run(run_class="bogus", family_id="fam-1")
        for name in ("screening", "confirmation", "headline",
                     "validation"):
            self.assertIn(name, result["failure"])

    def test_start_run_no_class_refusal_names_the_classes(self):
        result = mod12.start_run(family_id="fam-1")
        for name in ("screening", "confirmation", "headline",
                     "validation"):
            self.assertIn(name, result["failure"])

    def test_flag_tier_refusal_names_the_tiers_at_both_acts(self):
        record = {"run_id": "r-b9-82", "retention_tier": "Tier 1"}
        handed = {"flag_conditions_fired": ["c1"]}
        for message in (
                message_of(lambda: mod14.flag_evaluation(
                    dict(record), inputs=handed, outcome="promote",
                    tier="Tier 9")),
                message_of(lambda: mod10.apply_flag_evaluation(
                    dict(record), inputs=handed, outcome="promote",
                    tier="Tier 9"))):
            for name in ("Tier 0", "Tier 1", "Tier 2", "Tier 3"):
                self.assertIn(name, message)


class TestR14083NonMappingPayload(unittest.TestCase):
    def test_payload_forms_draw_the_named_payload_refusal(self):
        for command in ("read_store", "weekly_headline_count",
                        "flag_evaluation", "outside_call_check",
                        "start_run"):
            for payload in (["x"], "text", 42):
                result = mod14.run_command(command, payload)
                self.assertIn("failure", result, (command, payload))
                self.assertIn("payload", result["failure"])
                self.assertIn("mapping", result["failure"])
                self.assertNotIn(
                    "has no attribute", result["failure"])
                self.assertTrue(result["failure_value"])


class TestR14084KeyErrorQuoteForms(unittest.TestCase):
    def test_read_store_quote_bearing_identifier_unwrapped(self):
        result = mod14.run_command("read_store", {
            "run_id": "o'brien", "store_kind": "sweep"})
        self.assertIn("failure", result)
        self.assertNotIn('"', result["failure"])
        self.assertNotIn(
            '"', result["failure_value"].get("message", ""))

    def test_fixture_lookup_quote_bearing_identifier_unwrapped(self):
        carriage = mod14.error_carriage(
            mod16.FixtureLookupFailure("o'brien"))
        self.assertNotIn('"', carriage["failure"])
        self.assertNotIn(
            '"', carriage["failure_value"].get("message", ""))

    def test_non_text_identifier_unwrapped(self):
        carriage = mod14.error_carriage(mod10.LookupFailure(["x"]))
        self.assertNotIn('"', carriage["failure"])


class TestR14085TextFailureCarriage(unittest.TestCase):
    def test_text_failure_carries_the_sentence_twice(self):
        carriage = mod14.error_carriage(
            "a plain string failure", run_id="run-9", stage="stage-2")
        self.assertEqual(carriage["failure"], "a plain string failure")
        self.assertTrue(carriage["failure_value"])
        self.assertEqual(
            carriage["failure_value"].get("message"),
            "a plain string failure")
        self.assertEqual(carriage["run_id"], "run-9")
        self.assertFalse(carriage["swallowed"])


if __name__ == "__main__":
    unittest.main()

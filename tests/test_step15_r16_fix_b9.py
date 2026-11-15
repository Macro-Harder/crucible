"""Fix wave 15, Builder 9 pins: rows R15-079 to R15-085,
R15-090 to R15-092, and R15-096 to R15-098.

Test first pins for the weekly count, outside call, vocabulary,
and error carriage command and sentence family across MOD-10,
MOD-11, MOD-13, and MOD-14. Python standard library only.
"""

import types
import unittest
from collections.abc import Mapping

from crucible import mod10, mod11, mod13, mod14


def message_of(call):
    try:
        call()
    except Exception as failure:
        return str(failure)
    raise AssertionError("no failure raised")


class EqStr(str):
    """A text value whose equality answers True against every
    value and whose inequality answers False, storing its text
    whole."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class TestR15079OutsideCallBothKeys(unittest.TestCase):

    def test_entries_outside_call_read_where_calls_key_present(self):
        result = mod14.outside_call_check(
            {}, {"calls": [], "entries": [{"outside_call": True}]})
        self.assertEqual(result["outcome"], "outside calls present")

    def test_entries_outside_call_read_in_either_key_order(self):
        log = {"entries": [{"outside_call": True}],
               "calls": [{"outside_call": False}]}
        result = mod14.outside_call_check({}, log)
        self.assertEqual(result["outcome"], "outside calls present")

    def test_malformed_entry_under_entries_refused_where_calls_present(self):
        message = message_of(lambda: mod14.outside_call_check(
            {}, {"calls": [], "entries": [{}]}))
        self.assertIn("outside_call", message)

    def test_calls_value_at_none_draws_no_list_form_refusal(self):
        message = message_of(lambda: mod14.outside_call_check(
            {}, {"calls": None}))
        self.assertIn("no list form", message)

    def test_entries_value_at_none_draws_no_list_form_refusal(self):
        message = message_of(lambda: mod14.outside_call_check(
            {}, {"entries": None}))
        self.assertIn("no list form", message)

    def test_single_key_controls_stand(self):
        clean = mod14.outside_call_check(
            {}, {"calls": [{"outside_call": False}]})
        self.assertEqual(clean["outcome"], "no outside calls read")
        present = mod14.outside_call_check(
            {}, {"entries": [{"outside_call": True}]})
        self.assertEqual(present["outcome"], "outside calls present")


class TestR15080WeeklyHeadlineIdentifierForm(unittest.TestCase):

    def record(self, identifiers):
        return [{"week": "W1",
                 "headline_unit_identifiers": identifiers}]

    def test_bogus_text_identifier_refused_in_named_form(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            self.record(["bogus"]), "W1"))
        self.assertIn("no unit identifier form", message)
        self.assertIn("no count stands stated", message)

    def test_number_identifier_refused(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            self.record([123]), "W1"))
        self.assertIn("no unit identifier form", message)

    def test_number_and_none_identifiers_refused(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            self.record([123, None]), "W1"))
        self.assertIn("no unit identifier form", message)

    def test_bare_string_identifier_in_no_form_refused(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            self.record("bogus"), "W1"))
        self.assertIn("no unit identifier form", message)

    def test_container_element_bound_counts_one(self):
        # The R14-072 bound, stated in the open: a container
        # element in place of an identifier still counts as one.
        self.assertEqual(mod14.weekly_headline_count(
            self.record([["u1"]]), "W1"), 1)
        self.assertEqual(mod14.weekly_headline_count(
            self.record([{"x": 1}]), "W1"), 1)

    def test_valid_identifiers_count_as_before(self):
        self.assertEqual(mod14.weekly_headline_count(
            self.record(["u1", "u2", "u1"]), "W1"), 2)
        self.assertEqual(mod14.weekly_headline_count(
            self.record("u1"), "W1"), 1)


class TestR15081ManifestEntriesForm(unittest.TestCase):

    def test_number_entries_draw_named_refusal_not_bare_type_error(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.outside_call_check(
                {"entries": 5}, {"calls": []})

    def test_text_entries_refused_not_counted_as_characters(self):
        message = message_of(lambda: mod14.outside_call_check(
            {"entries": "abc"}, {"calls": []}))
        self.assertIn("manifest", message)
        self.assertIn("no list form", message)

    def test_mapping_entries_refused_not_counted_as_keys(self):
        message = message_of(lambda: mod14.outside_call_check(
            {"entries": {"a": 1}}, {"calls": []}))
        self.assertIn("no list form", message)

    def test_generator_and_boolean_entries_refused(self):
        for value in ((item for item in [1]), True):
            message = message_of(lambda: mod14.outside_call_check(
                {"entries": value}, {"calls": []}))
            self.assertIn("no list form", message)

    def test_shell_carriage_names_the_manifest_fault(self):
        result = mod14.run_command("outside_call_check", {
            "dependency_manifest": {"entries": 5},
            "call_log": {"calls": [{"outside_call": True}]}})
        self.assertIn("manifest", result["failure"])
        self.assertNotIn("has no len()", result["failure"])

    def test_lawful_and_absent_entries_stand(self):
        result = mod14.outside_call_check(
            {"entries": [1, 2]}, {"calls": []})
        self.assertEqual(result["manifest_entries"], 2)
        result = mod14.outside_call_check({}, {"calls": []})
        self.assertEqual(result["manifest_entries"], 0)


class TestR15082WeeklyHeadlineConsequences(unittest.TestCase):

    def test_list_form_refusal_states_consequence(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            {"week": "W1"}, "W1"))
        self.assertIn("no weekly headline count stands certified",
                      message)

    def test_no_identifier_field_sentence_states_consequence(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            [{"week": "W1"}], "W1"))
        self.assertIn("no weekly headline count stands certified",
                      message)

    def test_no_value_sentence_states_consequence(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            [{"week": "W1", "headline_unit_identifiers": None}], "W1"))
        self.assertIn("no weekly headline count stands certified",
                      message)

    def test_unreadable_field_sentence_states_consequence(self):
        message = message_of(lambda: mod14.weekly_headline_count(
            [{"week": "W1", "headline_unit_identifiers": 42}], "W1"))
        self.assertIn("no weekly headline count stands certified",
                      message)


class TestR15083WeeklyCountAbsentWeek(unittest.TestCase):

    def test_absent_week_refused_in_named_form(self):
        message = message_of(lambda: mod11.weekly_count(
            [{"week": "W1", "headline_unit_identifiers": ["u1"]}],
            None))
        self.assertIn("no week stands supplied", message)
        self.assertIn("no weekly count stands certified", message)

    def test_absent_week_on_empty_records_refused(self):
        message = message_of(lambda: mod11.weekly_count([], None))
        self.assertIn("no week stands supplied", message)


class TestR15084WeeklyCountAbsentRecords(unittest.TestCase):

    def test_absent_records_named_as_absence_with_consequence(self):
        message = message_of(lambda: mod11.weekly_count(None, "W1"))
        self.assertIn("no summary_records stand supplied", message)
        self.assertIn("no weekly count stands certified", message)

    def test_other_list_form_faults_keep_list_form_sentence(self):
        message = message_of(lambda: mod11.weekly_count(42, "W1"))
        self.assertIn("stands in no list form", message)


class TestR15085WeeklyCountWeekEquality(unittest.TestCase):

    def test_stored_week_equality_reading_does_not_count(self):
        records = [{"week": EqStr("W2"),
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 0)

    def test_handed_week_equality_reading_does_not_count(self):
        records = [{"week": "W1",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod11.weekly_count(records, EqStr("W9")), 0)

    def test_plain_week_controls_stand(self):
        records = [{"week": "W2",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 0)
        self.assertEqual(mod11.weekly_count(records, "W2"), 1)


class TestR15090VocabularyRefusals(unittest.TestCase):

    def record(self):
        return {"run_id": "r1", "retention_tier": "Tier 2",
                "flag_conditions_fired": ["condition-1"]}

    def test_flag_outcome_refusal_names_vocabulary_and_consequence(self):
        message = message_of(lambda: mod10.apply_flag_evaluation(
            self.record(), outcome="bogus"))
        self.assertIn("promote", message)
        self.assertIn("demote", message)
        self.assertIn("no flag evaluation stands performed", message)

    def test_flag_outcome_refusal_at_shell_names_vocabulary(self):
        message = message_of(lambda: mod14.flag_evaluation(
            self.record(), outcome="PROMOTE"))
        self.assertIn("promote", message)
        self.assertIn("demote", message)

    def test_flag_outcome_forms_all_name_vocabulary(self):
        for value in (123, ["promote"], b"bogus", ("promote",)):
            message = message_of(lambda: mod10.apply_flag_evaluation(
                self.record(), outcome=value))
            self.assertIn("promote and demote", message)

    def test_verdict_outcome_refusal_names_vocabulary_and_consequence(self):
        message = message_of(lambda: mod13.verdict_record(
            "c1", outcome="bogus"))
        self.assertIn("rests", message)
        self.assertIn("does not rest", message)
        self.assertIn("no verdict record stands made", message)

    def test_verdict_standard_refusal_names_vocabulary_and_consequence(self):
        message = message_of(lambda: mod13.verdict_record(
            "c1", standard="bogus"))
        self.assertIn("exact replay alone", message)
        self.assertIn("no verdict record stands made", message)


class TestR15091UnknownCommandVocabulary(unittest.TestCase):

    LAWFUL = ("start_run", "start_sweep", "read_store", "write_store",
              "run_pilot", "assemble_report", "outside_call_check",
              "store_kind_check", "weekly_headline_count",
              "flag_evaluation")

    def test_unknown_command_names_lawful_commands(self):
        result = mod14.run_command("weekly_headline_coun",
                                   {"summary_records": [],
                                    "week": "W1"})
        self.assertIn("unknown shell command", result["failure"])
        for name in self.LAWFUL:
            self.assertIn(name, result["failure"])
        self.assertIn("no shell command stands run",
                      result["failure"])

    def test_unknown_command_forms_name_vocabulary(self):
        for command in ("bogus", "", None, 123, "START_RUN",
                        "start_run "):
            result = mod14.run_command(command, {})
            self.assertIn("weekly_headline_count",
                          result["failure"], command)


class TestR15092ReadStoreAbsentIdentifier(unittest.TestCase):

    def test_absent_run_id_named_as_required_input(self):
        result = mod14.run_command("read_store", {})
        self.assertIn("run_id", result["failure"])
        self.assertIn("no run_id stands supplied", result["failure"])
        self.assertNotIn("one lookup resolution failure",
                         result["failure"])

    def test_run_id_in_no_identifier_form_named_as_form_fault(self):
        for value in ("", 123, ["run-1"], {"run": 1}):
            result = mod14.run_command("read_store", {"run_id": value})
            self.assertIn("run_id", result["failure"], value)
            self.assertIn("no run record stands read",
                          result["failure"], value)
            self.assertNotIn("one lookup resolution failure",
                             result["failure"], value)

    def test_supplied_identifier_still_draws_lookup_failure(self):
        result = mod14.run_command("read_store",
                                   {"run_id": "no-such-run"})
        self.assertIn("one lookup resolution failure",
                      result["failure"])


class TestR15096CarriageQuoteStripScope(unittest.TestCase):

    def test_text_failure_quote_wrapped_sentence_stands_whole(self):
        carriage = mod14.error_carriage("'quoted sentence'")
        self.assertEqual(carriage["failure"], "'quoted sentence'")
        self.assertEqual(
            carriage["failure_value"].get("message"),
            "'quoted sentence'")

    def test_exception_sentence_quotes_stand_whole(self):
        carriage = mod14.error_carriage(
            ValueError("'a' is not 'b'"))
        self.assertEqual(
            carriage["failure"], "ValueError: 'a' is not 'b'")

    def test_quote_only_failure_returns_its_sentence(self):
        carriage = mod14.error_carriage("''")
        self.assertEqual(carriage["failure"], "''")
        self.assertTrue(carriage["operator_sees_failure"])

    def test_key_error_family_strip_stands_as_control(self):
        carriage = mod14.error_carriage(
            mod10.LookupFailure("o'brien"))
        self.assertNotIn('"', carriage["failure"])
        self.assertNotIn(
            '"', carriage["failure_value"].get("message", ""))


class TestR15097NamedShellFailureTwoForms(unittest.TestCase):

    def test_quote_wrapped_sentence_agrees_in_both_places(self):
        carriage = mod14.error_carriage(
            mod14.NamedShellFailure("'quoted named sentence'"))
        self.assertEqual(
            carriage["failure"],
            "NamedShellFailure: 'quoted named sentence'")
        self.assertEqual(
            carriage["failure_value"].get("message"),
            "'quoted named sentence'")

    def test_double_quoted_sentence_agrees_in_both_places(self):
        carriage = mod14.error_carriage(
            mod14.NamedShellFailure('"quoted named sentence"'))
        self.assertEqual(
            carriage["failure_value"].get("message"),
            '"quoted named sentence"')


class _MappingPayload(Mapping):

    def __init__(self, data):
        self._data = dict(data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class TestR15098PayloadGateSentenceTruth(unittest.TestCase):

    def test_mapping_proxy_payload_sentence_names_dict_form(self):
        payload = types.MappingProxyType({"kind": "sweep"})
        result = mod14.run_command("store_kind_check", payload)
        self.assertIn("failure", result)
        self.assertNotIn("stands in no mapping form",
                         result["failure"])
        self.assertIn("no dict form", result["failure"])

    def test_mapping_subclass_payload_sentence_names_dict_form(self):
        payload = _MappingPayload({"kind": "sweep"})
        result = mod14.run_command("store_kind_check", payload)
        self.assertIn("failure", result)
        self.assertNotIn("stands in no mapping form",
                         result["failure"])
        self.assertIn("no dict form", result["failure"])

    def test_plain_non_dict_payloads_draw_the_same_true_sentence(self):
        for payload in (["x"], "text", 42):
            result = mod14.run_command("read_store", payload)
            self.assertIn("no dict form", result["failure"])
            self.assertIn("mapping", result["failure"])


if __name__ == "__main__":
    unittest.main()

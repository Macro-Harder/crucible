"""Pins for fix wave 13, Builder 9: rows R13-042 and R13-050 to
R13-054 of the Round 13 register.

R13-042 and R13-052: MOD-11 weekly_count against MOD-14
weekly_headline_count, count standings and failure sentences.
R13-050: the MOD-14 command surface flag_evaluation example and
its stated inputs shape.
R13-051: MOD-14 outside_call_check on missing required inputs.
R13-053: MOD-10 apply_flag_evaluation actor and demote sentences.
R13-054: MOD-14 flag_evaluation sentences against the MOD-10
sentences for the same failures.
"""

import unittest

import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod14 as mod14


def message_of(fn):
    try:
        fn()
    except Exception as error:
        return str(error)
    raise AssertionError("act did not raise")


class TestWeeklyCountStandings(unittest.TestCase):
    """R13-042: the count standings themselves."""

    def test_bare_string_identifier_counts_as_one_at_both_acts(self):
        records = [{"week": 3, "headline_unit_identifiers": "u123"}]
        self.assertEqual(mod11.weekly_count(records, 3), 1)
        self.assertEqual(mod14.weekly_headline_count(records, 3), 1)
        records = [{"week": 3, "headline_unit_identifiers": "u12"}]
        self.assertEqual(mod11.weekly_count(records, 3), 1)
        self.assertEqual(mod14.weekly_headline_count(records, 3), 1)

    def test_none_identifier_field_refused_at_both_acts(self):
        records = [{"week": 3, "headline_unit_identifiers": None}]
        with self.assertRaises(ValueError):
            mod11.weekly_count(records, 3)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count(records, 3)

    def test_other_week_record_without_identifiers_passes_over(self):
        records = [{"week": 9},
                   {"week": 3, "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod11.weekly_count(records, 3), 1)
        self.assertEqual(mod14.weekly_headline_count(records, 3), 1)

    def test_list_in_place_of_identifier_counts_one_at_both_acts(self):
        records = [{"week": 3, "headline_unit_identifiers": [["u1"]]}]
        self.assertEqual(mod11.weekly_count(records, 3), 1)
        self.assertEqual(mod14.weekly_headline_count(records, 3), 1)

    def test_plain_distinct_count_control_stands(self):
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W1", "headline_unit_identifiers": ["u2"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(mod11.weekly_count(records, "W1"), 2)
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 2)
        self.assertEqual(mod11.weekly_count(records, "W2"), 1)


class TestWeeklyCountSentences(unittest.TestCase):
    """R13-052: the failure sentence forms of the act pair."""

    def test_no_week_sentence_is_the_split_form(self):
        text = message_of(
            lambda: mod11.weekly_count(
                [{"headline_unit_identifiers": ["u1"]}], 3))
        self.assertEqual(
            text,
            "summary record carries no week field, so its weekly "
            "headline count cannot stand read")

    def test_no_identifiers_sentence_is_the_split_form(self):
        text = message_of(
            lambda: mod11.weekly_count([{"week": 3}], 3))
        self.assertEqual(
            text,
            "summary record for the week carries no "
            "headline_unit_identifiers field")

    def test_non_record_sentence_is_the_no_week_form(self):
        text = message_of(
            lambda: mod11.weekly_count(["just text"], 3))
        self.assertEqual(
            text,
            "summary record carries no week field, so its weekly "
            "headline count cannot stand read")

    def test_none_sentence_is_the_no_value_form(self):
        text = message_of(
            lambda: mod11.weekly_count(
                [{"week": 3, "headline_unit_identifiers": None}], 3))
        self.assertEqual(
            text,
            "summary record for the week carries a "
            "headline_unit_identifiers field standing at no value")

    def test_unreadable_identifier_sentence_names_the_form(self):
        text = message_of(
            lambda: mod11.weekly_count(
                [{"week": 3, "headline_unit_identifiers": 5}], 3))
        self.assertEqual(
            text,
            "summary record for the week carries a "
            "headline_unit_identifiers field the count cannot "
            "read: int")

    def test_the_four_sentences_stand_apart(self):
        texts = {
            message_of(lambda: mod11.weekly_count(
                [{"headline_unit_identifiers": ["u1"]}], 3)),
            message_of(lambda: mod11.weekly_count([{"week": 3}], 3)),
            message_of(lambda: mod11.weekly_count(
                [{"week": 3, "headline_unit_identifiers": None}], 3)),
            message_of(lambda: mod11.weekly_count(
                [{"week": 3, "headline_unit_identifiers": 5}], 3)),
        }
        self.assertEqual(len(texts), 4)


class TestFlagCommandSurface(unittest.TestCase):
    """R13-050: the shipped flag_evaluation example and shape."""

    def entry(self):
        entries = {e["command"]: e for e in mod14.command_surface()}
        return entries["flag_evaluation"]

    def test_example_runs_exactly_as_written_and_promotes(self):
        example = self.entry()["example"]
        result = eval(example, {"run_command": mod14.run_command})
        self.assertNotIn("failure", result)
        self.assertEqual(result["retention_tier"], "Tier 3")

    def test_surface_states_the_inputs_shape_a_promotion_needs(self):
        entry = self.entry()
        self.assertIn("flag_conditions_fired", str(entry))
        self.assertIn("inputs", entry["example"])


class TestOutsideCallCheckMissingInputs(unittest.TestCase):
    """R13-051: a check that examined nothing certifies nothing."""

    def test_run_command_with_no_inputs_refuses_in_carriage(self):
        result = mod14.run_command("outside_call_check", {})
        self.assertIn("failure", result)
        self.assertTrue(result["operator_sees_failure"])
        self.assertFalse(result["swallowed"])

    def test_run_command_with_mistyped_log_key_refuses(self):
        result = mod14.run_command("outside_call_check", {
            "dependency_manifest": {},
            "log": {"calls": [{"outside_call": True}]},
        })
        self.assertIn("failure", result)
        self.assertTrue(result["operator_sees_failure"])

    def test_direct_act_refuses_non_record_inputs(self):
        for manifest, log in ((None, None), ([], []),
                              (None, {"calls": []}),
                              ({"entries": []}, None),
                              ({"entries": []}, []),
                              ("text", {"calls": []})):
            with self.assertRaises(mod14.NamedShellFailure):
                mod14.outside_call_check(manifest, log)

    def test_supplied_inputs_controls_stand(self):
        clean = mod14.outside_call_check({}, {})
        self.assertEqual(clean["outcome"], "no outside calls read")
        self.assertEqual(clean["manifest_entries"], 0)
        present = mod14.outside_call_check(
            {"entries": ["a"]}, {"calls": [{"outside_call": True}]})
        self.assertEqual(present["outcome"], "outside calls present")
        self.assertEqual(present["manifest_entries"], 1)
        via_shell = mod14.run_command("outside_call_check", {
            "dependency_manifest": {}, "call_log": {}})
        self.assertEqual(via_shell["outcome"], "no outside calls read")


class TestMod10FlagSentences(unittest.TestCase):
    """R13-053: the MOD-10 actor limb and the two demote limbs."""

    def test_person_actor_sentence_names_no_close_condition(self):
        record = {"retention_tier": "Tier 1"}
        text = message_of(
            lambda: mod10.apply_flag_evaluation(
                dict(record), actor="person"))
        self.assertEqual(
            text,
            "flag evaluation by a person is barred: the flag rule "
            "stands evaluated by a program alone, and no flag "
            "evaluation stands performed")
        self.assertNotIn("after close", text)

    def test_demote_outcome_sentence_states_its_ground_in_full(self):
        record = {"retention_tier": "Tier 1"}
        text = message_of(
            lambda: mod10.apply_flag_evaluation(
                dict(record), outcome="demote"))
        self.assertEqual(
            text,
            "the flag rule never demotes: the stated outcome "
            "stands as demote, and no demotion stands effected "
            "by it")

    def test_demote_tier_below_sentence_stands_as_before(self):
        record = {"retention_tier": "Tier 2"}
        text = message_of(
            lambda: mod10.apply_flag_evaluation(
                dict(record), tier="Tier 1"))
        self.assertEqual(
            text,
            "the flag rule never demotes: the stated tier stands "
            "below the record tier, and no demotion stands "
            "effected by it")
class TestShellFlagSentencesMatchMod10(unittest.TestCase):
    """R13-054: one failure, one wording, at shell and at MOD-10."""

    def test_non_record_sentence_agrees(self):
        shell = message_of(lambda: mod14.flag_evaluation("text"))
        core = message_of(lambda: mod10.apply_flag_evaluation("text"))
        self.assertEqual(shell, core)

    def test_unknown_tier_sentence_agrees(self):
        kwargs = {"inputs": {"flag_conditions_fired": ["c1"]},
                  "outcome": "promote", "tier": "Tier 9"}
        shell = message_of(lambda: mod14.flag_evaluation({}, **kwargs))
        core = message_of(
            lambda: mod10.apply_flag_evaluation({}, **kwargs))
        self.assertEqual(shell, core)

    def test_no_inputs_sentence_agrees_and_states_the_need(self):
        kwargs = {"outcome": "promote", "tier": "Tier 3"}
        shell = message_of(lambda: mod14.flag_evaluation({}, **kwargs))
        core = message_of(
            lambda: mod10.apply_flag_evaluation({}, **kwargs))
        self.assertEqual(shell, core)
        self.assertIn("inputs actually supplied", shell)

    def test_no_fired_condition_sentence_agrees_and_states_the_need(self):
        kwargs = {"inputs": {"x": 1}, "outcome": "promote",
                  "tier": "Tier 3"}
        shell = message_of(lambda: mod14.flag_evaluation({}, **kwargs))
        core = message_of(
            lambda: mod10.apply_flag_evaluation({}, **kwargs))
        self.assertEqual(shell, core)
        self.assertIn("at least one stated flag condition fired", shell)


if __name__ == "__main__":
    unittest.main()

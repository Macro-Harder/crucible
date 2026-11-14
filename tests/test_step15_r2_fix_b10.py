# Step 15 second run fix tests, Builder 10.
# Items R1-021, R1-076, R1-082, R1-084, R1-093, R1-094, R1-095,
# R1-045, R1-046, R1-047, R1-048, R1-067, R1-029, R1-030, R1-078,
# R1-020, R1-055. Plain simulated values only.
import copy
import math
import unittest

import crucible.mod02 as mod02
import crucible.mod07 as mod07
import crucible.mod09 as mod09
import crucible.mod10 as mod10
import crucible.mod11 as mod11

FIELD10_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence mark: DQ-164 confirmation form, recording that "
    "DQ-164 stands settled as confirmation only; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)

FIELD10_COMPUTED_TEXT = (
    "seam status: computed in Parley and not settled in the "
    "chosen escrow; "
    "kill check name: kill check K-7; "
    "dependence mark: no dependence mark applies beyond the "
    "DQ-164 confirmation form; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: no anchor scenario is used in "
    "this unit."
)

CLAIM_TEXT = (
    "At the sampled points within the stated scope, the result "
    "holds for the sampled points only, and nothing is claimed "
    "beyond the stated limits."
)

GROUNDING_TEXT = (
    "This unit rests on the retained run records within the "
    "stated scope, and its limits are that nothing is claimed "
    "beyond the sampled points in this unit."
)


def compliant_unit():
    unit = {field: "value for " + field
            for field in mod11.HEADLINE_UNIT_FIELDS}
    unit["claim_sentence"] = CLAIM_TEXT
    unit["grounding_sentence"] = GROUNDING_TEXT
    unit["qualifiers_and_markings_block"] = FIELD10_TEXT
    unit["holding_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 200}, "outcome": "holds"}]}
    unit["failure_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 800}, "outcome": "fails"}]}
    return unit


def deep_value(depth, leaf="stated content"):
    value = {"leaf": leaf}
    for _ in range(depth):
        value = {"k": value}
    return value


class TestR1021QuoteThroughBaseReadings(unittest.TestCase):
    def test_deepcopy_override_part_is_not_forged(self):
        class ForgingPart:
            def __deepcopy__(self, memo):
                return "forged quoted content"
        part = ForgingPart()
        unit = compliant_unit()
        unit["assumption_record"] = {"a": "stated content", "b": part}
        self.assertTrue(mod11.validate_headline_unit(unit))
        quoted = mod11.quote_headline_unit(unit)
        self.assertIs(quoted["assumption_record"]["b"], part)
        self.assertEqual(quoted["assumption_record"]["a"],
                         "stated content")

    def test_items_override_part_is_not_forged(self):
        class Uncopyable:
            def __deepcopy__(self, memo):
                raise TypeError("uncopyable part")
        class BadItems(dict):
            def items(self):
                return [("forged_key", "forged content")]
        part = BadItems()
        part["a"] = "stated content"
        part["hidden"] = Uncopyable()
        unit = compliant_unit()
        unit["assumption_record"] = part
        self.assertTrue(mod11.validate_headline_unit(unit))
        quoted = mod11.quote_headline_unit(unit)
        self.assertNotIn("forged_key", quoted["assumption_record"])
        self.assertEqual(quoted["assumption_record"]["a"],
                         "stated content")
        self.assertIs(quoted["assumption_record"]["hidden"],
                      part["hidden"])


class TestR1076DepthBound(unittest.TestCase):
    def test_deeply_nested_field_value_returns_false(self):
        unit = compliant_unit()
        unit["assumption_record"] = deep_value(600)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_deeply_nested_list_returns_false(self):
        value = "stated content"
        for _ in range(600):
            value = [value]
        unit = compliant_unit()
        unit["assumption_record"] = value
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_quoted_copy_on_deep_value_raises_no_recursion_error(self):
        try:
            mod11._quoted_copy(deep_value(2000))
        except RecursionError:
            self.fail("quoted copy escaped as a RecursionError")
        except Exception:
            pass
        else:
            self.fail("quoted copy accepted a deeply nested value")


class TestR1082Field10Marks(unittest.TestCase):
    def test_generic_field10_fails(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = (
            "value for qualifiers_and_markings_block")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_banana_seam_status_fails(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = (
            "seam status: banana, kill check: none, marks: none")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_missing_parley_q3_statement_fails(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = FIELD10_TEXT.replace(
            "Parley Q3 statement: no part of the result encodes "
            "Parley Q3 behaviour; ", "")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_missing_dependence_mark_fails(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = FIELD10_TEXT.replace(
            "dependence mark: DQ-164 confirmation form, recording "
            "that DQ-164 stands settled as confirmation only; ", "")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_computed_seam_status_form_passes(self):
        unit = compliant_unit()
        unit["qualifiers_and_markings_block"] = FIELD10_COMPUTED_TEXT
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)


class TestR1084LookupFailureKey(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def test_failure_carries_run_identifier_key(self):
        values = compliant_unit()
        result = mod11.build_headline_unit_from_run(
            "run-absent-b10", values)
        self.assertFalse(result["built"])
        failure = result["failure"]
        self.assertEqual(failure["name"],
                         "one lookup resolution failure")
        self.assertEqual(failure["run_identifier"], "run-absent-b10")
        self.assertNotIn("record", failure)
        self.assertNotIn("owner_identifier", failure)


class TestR1093PlainScopeAndLimits(unittest.TestCase):
    def test_code_only_claim_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = "zz zz zz."
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_code_only_grounding_fails(self):
        unit = compliant_unit()
        unit["grounding_sentence"] = "A9 R9 K9."
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_working_range_code_only_text_fails(self):
        self.assertFalse(mod11.validate_working_range_claim(
            "A9 R9 K9 rest", "A9", "R9", "K9"))

    def test_working_range_plain_text_passes(self):
        good = ("Over assumption set A-1, rows R-1 to R-9, in the "
                "working range kind, the claim holds within the "
                "stated scope and limits. Further sentences follow.")
        self.assertTrue(mod11.validate_working_range_claim(
            good, "assumption set A-1", "rows R-1 to R-9",
            "working range"))


class TestR1094TransitionHorizonValue(unittest.TestCase):
    def _unit(self, sentence, horizon=60):
        replicates = (
            [{"first_terminal_regime": "attacker winning"}] * 5
            + [{"first_terminal_regime": None}] * 5)
        figure = mod11.transition_figure(replicates)
        figure["horizon"] = horizon
        return {
            "headline_figure": 0.5,
            "transition_figure": figure,
            "incidence_label": (
                "derived from the replicate counts in this unit"),
            "location_sentences": [sentence],
        }

    def test_word_horizon_alone_fails(self):
        self.assertFalse(mod11.validate_transition_unit(
            self._unit("by the horizon")))

    def test_stated_horizon_value_passes(self):
        self.assertTrue(mod11.validate_transition_unit(
            self._unit("at the 60 day horizon, the region stands")))

    def test_wrong_horizon_value_fails(self):
        self.assertFalse(mod11.validate_transition_unit(
            self._unit("at the 30 day horizon, the region stands")))


class TestR1095ReadoutNamesAndRules(unittest.TestCase):
    def test_quantity_without_name_fails(self):
        readout = {"quantities": [
            {"recorded_number": 3, "class_based": True,
             "class_rule": "a point stands in the holding class "
                           "where its share reaches the bound"}]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_one_letter_class_rule_fails(self):
        readout = {"quantities": [
            {"name": "holding share", "recorded_number": 3,
             "class_based": True, "class_rule": "z"}]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_named_quantity_with_rule_in_words_passes(self):
        readout = {"quantities": [
            {"name": "holding share", "recorded_number": 3,
             "class_based": True,
             "class_rule": "a point stands in the holding class "
                           "where its share reaches the bound"}]}
        self.assertTrue(mod11.validate_readout(readout))


def _approved_choice():
    approval = {"approver": "Project Manager",
                "choice_identifier": "ch-b10",
                "effects": "creation and release paths",
                "standing": "approved"}
    return mod07.make_adapter_choice(
        "ch-b10", "reading for the seam", "rule point",
        "governing text v1", "fold v1", approval=approval,
        drives=[{"level": "decision", "kind": "computed value"}],
        dependence_marks=["mark one"])


def _joint_run(choice, **extra):
    run = {
        "adapter_choices": [choice],
        "tracer_passage_records": mod07.tracer_passage_records("r-b10"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [],
    }
    run.update(extra)
    return run


class TestR1045SeamWording(unittest.TestCase):
    def test_computed_on_another_effect_does_not_excuse_release(self):
        self.assertFalse(mod07.validate_seam_wording(
            "the lien is computed in Parley and the vouch is released"))

    def test_interim_form_still_passes(self):
        self.assertTrue(mod07.validate_seam_wording(
            "computed in Parley and not settled in the chosen escrow"))

    def test_computed_attached_to_the_release_passes(self):
        self.assertTrue(mod07.validate_seam_wording(
            "the effect was computed and released only as a "
            "computed figure in Parley"))

    def test_plain_released_still_fails(self):
        self.assertFalse(mod07.validate_seam_wording(
            "the vouch was released"))


class TestR1046JointRunStoredPair(unittest.TestCase):
    def test_disagreeing_stored_log_entry_fails_the_run(self):
        choice = _approved_choice()
        stored_log = mod07.interpretation_log_entry(choice)
        stored_log["reading_applied"] = "DIFFERENT"
        run = _joint_run(
            choice,
            interpretation_log_entries=[stored_log],
            run_record_entries=[mod07.run_record_entry(choice)])
        self.assertFalse(mod07.validate_joint_run(run))

    def test_agreeing_stored_pair_passes_the_run(self):
        choice = _approved_choice()
        run = _joint_run(
            choice,
            interpretation_log_entries=[
                mod07.interpretation_log_entry(choice)],
            run_record_entries=[mod07.run_record_entry(choice)])
        self.assertTrue(mod07.validate_joint_run(run))


class TestR1047ChoicePairAbsentFields(unittest.TestCase):
    def test_two_empty_entries_fail(self):
        self.assertFalse(mod07.validate_choice_pair({}, {}))

    def test_partially_absent_fields_fail(self):
        entry = {"choice_identifier": "X"}
        self.assertFalse(mod07.validate_choice_pair(entry, dict(entry)))

    def test_full_agreeing_pair_passes(self):
        choice = _approved_choice()
        self.assertTrue(mod07.validate_choice_pair(
            mod07.interpretation_log_entry(choice),
            mod07.run_record_entry(choice)))


class TestR1048TracerBlankField(unittest.TestCase):
    def test_blank_what_in_fact_passed_fails_on_all_records(self):
        records = mod07.tracer_passage_records("r-b10")
        for record in records:
            record["what_in_fact_passed"] = ""
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_whitespace_what_in_fact_passed_fails(self):
        records = mod07.tracer_passage_records("r-b10")
        records[3]["what_in_fact_passed"] = "   "
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_unaltered_set_passes(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            mod07.tracer_passage_records("r-b10")))


class TestR1067LiteralWordingValues(unittest.TestCase):
    def test_seam_effect_report_carries_literal_wording(self):
        report = mod07.seam_effect_report(
            {"kind": "vouch release", "value": 3})
        self.assertEqual(
            report["reporting"],
            "computed in Parley and not settled in the chosen escrow")
        self.assertEqual(report["lien_state"], "computed not settled")


class TestR1029BatteryVerdictRecorded(unittest.TestCase):
    def test_unrecorded_verdict_is_gated_not_passed(self):
        self.assertEqual(
            mod02.battery_verdict_state(
                inter_stream_element_recorded=True,
                verdict_recorded=False, verdict="passed"),
            "gated")

    def test_recorded_verdict_still_passes(self):
        self.assertEqual(
            mod02.battery_verdict_state(
                inter_stream_element_recorded=True,
                verdict_recorded=True, verdict="passed"),
            "passed")


class TestR1030CandidateEncodingFieldNameType(unittest.TestCase):
    def test_integer_and_string_field_names_encode_differently(self):
        self.assertNotEqual(
            mod02.encode_candidate_input({1: "x"}),
            mod02.encode_candidate_input({"1": "x"}))

    def test_same_input_still_encodes_the_same(self):
        self.assertEqual(
            mod02.encode_candidate_input({"a": "one", "b": "two"}),
            mod02.encode_candidate_input({"b": "two", "a": "one"}))


class TestR1078StreamCardinalityAgainstStreamSet(unittest.TestCase):
    def test_missing_class_fails(self):
        stream_set = {"stream_class_inventory": ["class a", "class b"]}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1}, stream_set=stream_set))

    def test_extra_class_fails(self):
        stream_set = {"stream_class_inventory": ["class a", "class b"]}
        self.assertFalse(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1, "class zz": 1},
            stream_set=stream_set))

    def test_exact_set_passes(self):
        stream_set = {"stream_class_inventory": ["class a", "class b"]}
        self.assertTrue(mod02.validate_stream_cardinality(
            counts={"class a": 1, "class b": 1},
            stream_set=stream_set))

    def test_typed_stream_set_positional(self):
        typed = mod02.StreamSet(
            {"stream_class_inventory": ["class a", "class b"],
             "adjudication_stream": "class a"})
        self.assertFalse(mod02.validate_stream_cardinality(
            {"class a": 1}, typed))
        self.assertTrue(mod02.validate_stream_cardinality(
            {"class a": 1, "class b": 1}, typed))


class TestR1020AttackerPayoffFinite(unittest.TestCase):
    def test_non_finite_external_profit_refused_by_name(self):
        strategy = mod09.make_strategy("s", in_protocol_payoff=3)
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(mod09.NamedAttackerFailure):
                mod09.attacker_payoff(strategy, value)

    def test_non_finite_in_protocol_payoff_refused_by_name(self):
        strategy = mod09.make_strategy(
            "s", in_protocol_payoff=math.nan)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(strategy, 1)

    def test_finite_payoff_still_computed(self):
        strategy = mod09.make_strategy("s", in_protocol_payoff=3)
        self.assertEqual(mod09.attacker_payoff(strategy, 4), 7)


class TestR1055RunRecordCarriageEmptyForms(unittest.TestCase):
    def test_empty_strategy_class_list_fails(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage([], 0, "v1", "ptr", "v1")

    def test_empty_catalogue_string_fails(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(["a"], 0, "", "ptr", "v1")

    def test_empty_ladder_strings_fail(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(["a"], 0, "v1", "", "")
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.run_record_carriage(["a"], 0, "v1", "ptr", "")

    def test_full_carriage_still_stands(self):
        carriage = mod09.run_record_carriage(
            ["a"], 0, "v1", "ptr", "v1")
        self.assertEqual(carriage["strategy_class"], ["a"])


if __name__ == "__main__":
    unittest.main()

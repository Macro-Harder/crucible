# Step 15 rerun Round 2 fix wave 2 tests, Builder 10.
# Items R2-034, R2-035, R2-054, R2-055, R2-029, R2-047.
# Plain simulated values only.
import unittest

import crucible.mod07 as mod07
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

FIELD10_ANCHOR_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence mark: DQ-164 confirmation form, recording that "
    "DQ-164 stands settled as confirmation only; "
    "Parley Q3 statement: no part of the result encodes Parley "
    "Q3 behaviour; "
    "core only qualifier: this unit is a core only result; "
    "anchor scenario statement: anchor scenario AN-1 is used "
    "in this unit, awaiting a ruling, citing DQ-163."
)

FIELD10_NO_DEPENDENCE_TEXT = (
    "seam status: no cross seam effect; "
    "kill check: self checked only; "
    "dependence: no dependence mark applies; "
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


class TestR2034Field10GroundsComparison(unittest.TestCase):
    def test_vouch_ground_denied_by_field10_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            CLAIM_TEXT
            + " This result rests on a vouch release and a "
              "vouch lien amount.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_vouch_ground_with_computed_field10_passes(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            CLAIM_TEXT
            + " This result rests on a vouch release and a "
              "vouch lien amount.")
        unit["qualifiers_and_markings_block"] = FIELD10_COMPUTED_TEXT
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_ground_denied_by_field10_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchor scenario AN-1, "
            "awaiting a ruling")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_ground_with_dq163_field10_passes(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchor scenario AN-1, "
            "awaiting a ruling")
        unit["qualifiers_and_markings_block"] = FIELD10_ANCHOR_TEXT
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_q1_ground_denied_by_field10_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            CLAIM_TEXT + " This claim depends on Parley Q1.")
        unit["qualifiers_and_markings_block"] = (
            FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q1_ground_with_dq164_field10_passes(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            CLAIM_TEXT + " This claim depends on Parley Q1.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_base_unit_still_passes_and_quotes(self):
        unit = compliant_unit()
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)


class TestR2035PlainSentenceReadableWords(unittest.TestCase):
    def test_repeated_word_claim_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = "Scope only only only only only only."
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_repeated_word_grounding_fails(self):
        unit = compliant_unit()
        unit["grounding_sentence"] = (
            "Scope only only only only only only.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_gibberish_claim_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = "Scope zzzz yyyy xxxx wwww vvvv only."
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_gibberish_grounding_fails(self):
        unit = compliant_unit()
        unit["grounding_sentence"] = (
            "Scope zzzz yyyy xxxx wwww vvvv only.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_working_range_gibberish_text_fails(self):
        self.assertFalse(mod11.validate_working_range_claim(
            "zzzz yyyy xxxx wwww A9 R9 K9 rest", "A9", "R9", "K9"))

    def test_working_range_plain_text_still_passes(self):
        good = ("Over assumption set A-1, rows R-1 to R-9, in the "
                "working range kind, the claim holds within the "
                "stated scope and limits. Further sentences follow.")
        self.assertTrue(mod11.validate_working_range_claim(
            good, "assumption set A-1", "rows R-1 to R-9",
            "working range"))

    def test_genuine_unit_still_passes(self):
        self.assertTrue(mod11.validate_headline_unit(compliant_unit()))


class TestR2054TransitionHorizonPosition(unittest.TestCase):
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

    def test_wrong_horizon_with_correct_value_as_count_fails(self):
        self.assertFalse(mod11.validate_transition_unit(
            self._unit(
                "at the 30 day horizon, the region stands "
                "after 60 replicates")))

    def test_no_horizon_named_with_correct_value_as_count_fails(self):
        self.assertFalse(mod11.validate_transition_unit(
            self._unit(
                "the region stands, horizon not stated, "
                "based on 60 replicates")))

    def test_horizon_value_at_horizon_position_passes(self):
        self.assertTrue(mod11.validate_transition_unit(
            self._unit("at the 60 day horizon, the region stands")))

    def test_horizon_of_value_form_passes(self):
        self.assertTrue(mod11.validate_transition_unit(
            self._unit(
                "the region stands at the stated horizon of 60 days")))

    def test_wrong_horizon_value_alone_still_fails(self):
        self.assertFalse(mod11.validate_transition_unit(
            self._unit("at the 30 day horizon, the region stands")))


class TestR2055ReadoutReadableWords(unittest.TestCase):
    def _readout(self, name, rule):
        return {"quantities": [
            {"name": name, "recorded_number": 3,
             "class_based": True, "class_rule": rule}]}

    def test_invented_name_and_rule_fail(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("zzz", "zzz yyy xxx")))

    def test_invented_longer_name_and_rule_fail(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("qqqq", "qqqq wwww eeee")))

    def test_repeated_word_class_rule_fails(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("holding share", "the the the")))

    def test_genuine_name_and_rule_still_pass(self):
        self.assertTrue(mod11.validate_readout(self._readout(
            "holding share",
            "a point stands in the holding class where its "
            "share reaches the bound")))


class TestR2029Mod07CopyBoundAndCycleGuard(unittest.TestCase):
    def _choice_kwargs(self, approval):
        return dict(
            choice_identifier="ch-b10-r3",
            reading_applied="reading for the seam",
            parameter_or_rule_point_affected="rule point",
            governing_text_version="governing text v1",
            escrow_variant_and_fold_version="fold v1",
            approval=approval)

    def test_deep_approval_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod07.make_adapter_choice(
                **self._choice_kwargs(deep_value(2000)))
        self.assertNotIsInstance(caught.exception, RecursionError)
        self.assertIn("named form", str(caught.exception))

    def test_approval_past_bound_of_100_refused(self):
        with self.assertRaises(ValueError):
            mod07.make_adapter_choice(
                **self._choice_kwargs(deep_value(150)))

    def test_cyclic_approval_refused_in_named_form(self):
        approval = {"approver": "Project Manager"}
        approval["self"] = approval
        with self.assertRaises(ValueError) as caught:
            mod07.make_adapter_choice(
                **self._choice_kwargs(approval))
        self.assertIn("named form", str(caught.exception))

    def test_deep_seam_effect_value_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod07.seam_effect_report(
                {"kind": "vouch release", "value": deep_value(2000)})
        self.assertNotIsInstance(caught.exception, RecursionError)
        self.assertIn("named form", str(caught.exception))

    def test_cyclic_seam_effect_value_refused_in_named_form(self):
        value = {"leaf": "stated content"}
        value["self"] = value
        with self.assertRaises(ValueError) as caught:
            mod07.seam_effect_report(
                {"kind": "vouch release", "value": value})
        self.assertIn("named form", str(caught.exception))

    def test_shallow_choice_and_report_still_stand(self):
        approval = {"approver": "Project Manager",
                    "choice_identifier": "ch-b10-r3",
                    "effects": "creation and release paths",
                    "standing": "approved"}
        choice = mod07.make_adapter_choice(
            **self._choice_kwargs(approval))
        self.assertEqual(choice["approval"], approval)
        report = mod07.seam_effect_report(
            {"kind": "vouch release", "value": 3})
        self.assertEqual(report["value"], 3)


class TestR2047TracerBlankPointInRun(unittest.TestCase):
    def test_blank_point_in_run_fails_on_all_records(self):
        records = mod07.tracer_passage_records("r-b10-r3")
        for record in records:
            record["point_in_run"] = ""
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_whitespace_point_in_run_fails(self):
        records = mod07.tracer_passage_records("r-b10-r3")
        records[3]["point_in_run"] = "   "
        self.assertFalse(mod07.validate_tracer_passage_set(records))

    def test_unaltered_set_still_passes(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            mod07.tracer_passage_records("r-b10-r3")))


if __name__ == "__main__":
    unittest.main()

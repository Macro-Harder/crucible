# Step 15 rerun Round 3 fix wave 3 tests, Builder 10.
# Items R3-035, R3-036, R3-037.
# Plain simulated values only.
import unittest

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


def unit_with_claim_extra(sentence, field10=None):
    unit = compliant_unit()
    unit["claim_sentence"] = CLAIM_TEXT + " " + sentence
    if field10 is not None:
        unit["qualifiers_and_markings_block"] = field10
    return unit


class TestR3035Field10GroundsVariants(unittest.TestCase):
    def test_base_unit_still_passes_and_quotes(self):
        unit = compliant_unit()
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)

    def test_exact_vouch_release_denied_still_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a vouch release.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_plural_vouch_releases_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on vouch releases from the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_plural_vouch_releases_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "This result rests on vouch releases from the seam.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_plural_vouch_liens_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on vouch liens from the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_plural_slashes_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on slashes applied in the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_hyphenated_vouch_release_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a vouch-release at the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_verb_form_vouch_released_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a vouch that was released.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_slashed_amount_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a slashed amount.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_hyphenated_vouch_lien_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a vouch-lien amount.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_scenarios_plural_denied_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchor scenarios AN-1 in its basis")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_hyphenated_anchor_scenario_denied_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchor-scenario AN-1")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_test_wording_denied_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on the anchor test AN-1")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_test_wording_with_anchor_field10_passes(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on the anchor test AN-1")
        unit["qualifiers_and_markings_block"] = FIELD10_ANCHOR_TEXT
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_q1_spaced_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q 1 for its basis.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q1_hyphenated_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q-1.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q1_reversed_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on the Q1 of Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_one_spelled_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question 1.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q2_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q2_with_dq164_field10_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q2.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_q5_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q5.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_q5_with_dq164_field10_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q5.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_q2_in_other_field_denied_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "arbiter accuracy results depend on Parley Q2")
        unit["qualifiers_and_markings_block"] = (
            FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_two_spelled_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_five_spelled_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question five.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR3036ReadableWordReading(unittest.TestCase):
    def test_invented_strings_count_as_no_plain_words(self):
        self.assertEqual(mod11._plain_word_count(
            "zarn blim torva quesh mibra sostu"), 0)

    def test_genuine_words_still_count(self):
        self.assertEqual(mod11._plain_word_count(
            "scope result holds within stated limits"), 6)

    def test_rhythm_is_a_genuine_word(self):
        self.assertTrue(mod11._is_readable_word("rhythm"))

    def test_no_vowel_gibberish_still_counts_as_no_word(self):
        self.assertFalse(mod11._is_readable_word("zzzz"))

    def test_headline_invented_claim_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            "Blorve snarp quizzle drintal vorple scope only.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_headline_invented_claim_purple_form_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            "Scope zarn blim torva quesh only mibra sostu.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_headline_invented_grounding_fails(self):
        unit = compliant_unit()
        unit["grounding_sentence"] = (
            "Scope blorple snizzle wizzle frobnicate quizzle "
            "zonkle only.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_genuine_unit_still_passes(self):
        self.assertTrue(mod11.validate_headline_unit(compliant_unit()))

    def test_no_vowel_gibberish_claim_still_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = "Scope zzzz yyyy xxxx wwww vvvv only."
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_working_range_invented_text_fails(self):
        self.assertFalse(mod11.validate_working_range_claim(
            "blorve snarp quizzle vorple A9 R9 K9 rest",
            "A9", "R9", "K9"))

    def test_working_range_plain_text_still_passes(self):
        good = ("Over assumption set A-1, rows R-1 to R-9, in the "
                "working range kind, the claim holds within the "
                "stated scope and limits. Further sentences follow.")
        self.assertTrue(mod11.validate_working_range_claim(
            good, "assumption set A-1", "rows R-1 to R-9",
            "working range"))

    def _readout(self, name, rule):
        return {"quantities": [
            {"name": name, "recorded_number": 3,
             "class_based": True, "class_rule": rule}]}

    def test_readout_invented_name_and_rule_fail(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("blorve share",
                          "blorve snarp quizzle drintal")))

    def test_readout_invented_rule_only_fails(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("holding share",
                          "blorve snarp quizzle drintal")))

    def test_readout_genuine_name_and_rule_still_pass(self):
        self.assertTrue(mod11.validate_readout(self._readout(
            "holding share",
            "a point stands in the holding class where its "
            "share reaches the bound")))

    def test_readout_no_vowel_forms_still_fail(self):
        self.assertFalse(mod11.validate_readout(
            self._readout("zzz", "zzz yyy xxx")))


class TestR3037ScopeLimitsWholeWords(unittest.TestCase):
    def test_commonly_sentence_states_no_limit(self):
        self.assertFalse(mod11._has_plain_scope_limits_sentence(
            "Within the sampled points the holding result "
            "describes the scope commonly seen across the farm "
            "pattern fully."))

    def test_commonly_claim_unit_fails(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            "Within the sampled points the holding result "
            "describes the scope commonly seen across the farm "
            "pattern fully.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_no_limit_control_sentence_still_fails(self):
        self.assertFalse(mod11._has_plain_scope_limits_sentence(
            "Within the sampled points the holding result "
            "describes the scope of the farm and the pattern fully."))

    def test_genuine_scope_limits_sentence_still_passes(self):
        self.assertTrue(mod11._has_plain_scope_limits_sentence(
            CLAIM_TEXT))

    def test_scope_word_inside_longer_word_does_not_count(self):
        self.assertFalse(mod11._has_plain_scope_limits_sentence(
            "The microscope result holds only for the stated "
            "pattern across the farm."))

    def test_limit_word_inside_longer_word_does_not_count(self):
        self.assertFalse(mod11._has_plain_scope_limits_sentence(
            "At the sampled points within the stated scope, the "
            "result holds for the unlimited pattern across the "
            "farm fields."))


if __name__ == "__main__":
    unittest.main()

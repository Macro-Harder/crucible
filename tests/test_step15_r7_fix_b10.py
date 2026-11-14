# Step 15 rerun Round 6 fix wave 6 tests, Builder 10.
# Items R6-028 and R6-029, all at MOD-11.
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


def anchor_field10(scenario):
    return (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: anchor scenario " + scenario +
        " is used in this unit, awaiting a ruling, citing DQ-163."
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


ANCHOR_FAR_SENTENCES = (
    "The anchor named in the retained records is scenario AN-9.",
    "The anchor for this result, stated in the retained records, "
    "is scenario AN-9.",
    "The scenario AN-9, stated in the retained records, serves "
    "as the anchor for this result.",
    "The result rests on an anchor that stands behind the whole "
    "stated result in the named scenario AN-9.",
    "Scenario AN-9 stands as the stated basis for the whole "
    "result and its anchor.",
    "The result rests on an anchor drawn from the tested and "
    "documented scenario AN-9.",
    "The result is anchored in the named and fully tested and "
    "documented scenario AN-9.",
    "The result rests on scenarioanchor AN-9.",
)


class TestR6028AnchorWhereverStated(unittest.TestCase):
    def test_anchor_far_sentences_denied_fail(self):
        for sentence in ANCHOR_FAR_SENTENCES:
            with self.subTest(sentence=sentence):
                unit = unit_with_claim_extra(sentence)
                self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_far_sentences_conforming_pass(self):
        for sentence in ANCHOR_FAR_SENTENCES:
            with self.subTest(sentence=sentence):
                unit = unit_with_claim_extra(
                    sentence, field10=anchor_field10("AN-9"))
                self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_far_direct_reading_distance_seven(self):
        self.assertTrue(mod11._anchor_ground_stated(
            "the anchor named in the retained records is "
            "scenario an-9"))

    def test_anchor_far_direct_reading_reversed_distance(self):
        self.assertTrue(mod11._anchor_ground_stated(
            "the scenario an-9, stated in the retained records, "
            "serves as the anchor for this result"))

    def test_anchor_reversed_joined_direct_reading(self):
        self.assertTrue(mod11._anchor_ground_stated(
            "the result rests on scenarioanchor an-9"))

    def test_anchor_reversed_joined_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on scenarioanchor AN-9.")
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_anchor_standard_wording_denied_control(self):
        unit = unit_with_claim_extra(
            "The result rests on an anchor scenario AN-9.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_standard_wording_conforming_control(self):
        unit = unit_with_claim_extra(
            "The result rests on an anchor scenario AN-9.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_without_scenario_word_states_no_ground(self):
        self.assertFalse(mod11._anchor_ground_stated(
            "the anchor named in the retained records stands "
            "behind this result"))
        unit = unit_with_claim_extra(
            "The anchor named in the retained records stands "
            "behind this result.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_scenario_without_anchor_word_states_no_ground(self):
        self.assertFalse(mod11._anchor_ground_stated(
            "the scenario an-9 stands in the retained records"))
        unit = unit_with_claim_extra(
            "The scenario AN-9 stands in the retained records.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_base_unit_control_passes(self):
        self.assertTrue(
            mod11.validate_headline_unit(compliant_unit()))

    def test_seam_across_statement_boundary_control_stands(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouch at the seam. "
            "A release was later recorded for it.")
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR6028ParleyNumberedAndOrdinalForms(unittest.TestCase):
    def test_parley_question_numbered_two_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the Parley question numbered two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_numbered_two_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the Parley question numbered two.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_question_numbered_five_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the Parley question numbered "
            "five.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_numbered_direct_reading(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "this claim rests on the parley question "
                "numbered two"),
            {"2"})

    def test_parley_numbers_after_name_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on the questions of Parley, "
            "numbers two and five.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_numbers_after_name_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on the questions of Parley, "
            "numbers two and five.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_numbers_after_name_direct_reading(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "this claim depends on the questions of parley, "
                "numbers two and five"),
            {"2", "5"})

    def test_parley_ordinal_past_window_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second of the several "
            "questions that Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_ordinal_past_window_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second of the several "
            "questions that Parley poses.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_ordinal_past_window_direct_reading(self):
        self.assertIn(
            "2",
            mod11._parley_grounds_stated(
                "this claim rests on the second of the several "
                "questions that parley poses"))

    def test_parley_ordinal_filler_word_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second stated question that "
            "Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_spaced_q2_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_second_question_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second Parley question.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_reversed_questions_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim depends on questions two and five of "
            "Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_number_word_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question number two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


ADVERBS = (
    "easily", "happily", "silently", "gently", "brightly",
    "darkly", "coldly", "gladly", "bravely", "foolishly")
PRODUCT_WORDS = (
    "escrow", "coverage", "calibration", "provenance", "verdict",
    "checkpoint", "retention", "promotion", "operator", "archive",
    "stake", "decay")
READOUT_WORDS = (
    "honest", "cumulative", "censored", "divergence", "finite",
    "aggregate", "identical", "width", "uncertainty",
    "observation", "summary", "fraction", "decimal", "integer",
    "maximum", "combined", "zero", "rebuilt", "reran")
FRESH_WORDS = (
    "brother", "animal", "golden", "angry", "hungry", "brave",
    "gentle", "polite", "quick", "bright", "dark", "clean",
    "dirty", "narrow", "empty", "healthy", "awake", "asleep",
    "alive", "proud", "lonely", "wonderful")
FRESH_WORDS_YELLOW3 = (
    "busy", "slow", "cool", "indian", "birds", "knew", "told",
    "heard", "black", "vowel", "hundred", "numeral", "english")


class TestR6029ReadableLexiconNamedWords(unittest.TestCase):
    def test_adverbs_are_readable(self):
        for word in ADVERBS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_product_vocabulary_words_are_readable(self):
        for word in PRODUCT_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_vocabulary_words_are_readable(self):
        for word in READOUT_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_fresh_plain_words_are_readable(self):
        for word in FRESH_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_fresh_plain_words_yellow3_are_readable(self):
        for word in FRESH_WORDS_YELLOW3:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_escrow_coverage_passes(self):
        readout = {"quantities": [
            {"name": "escrow coverage", "recorded_number": 3,
             "class_based": True,
             "class_rule": "escrow coverage reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_calibration_verdict_passes(self):
        readout = {"quantities": [
            {"name": "calibration verdict", "recorded_number": 3,
             "class_based": True,
             "class_rule": "calibration verdict reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_honest_cumulative_name_passes(self):
        readout = {"quantities": [
            {"name": "honest cumulative", "recorded_number": 3,
             "class_based": True,
             "class_rule": "median variance reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_cumulative_honest_rule_passes(self):
        readout = {"quantities": [
            {"name": "median variance", "recorded_number": 3,
             "class_based": True,
             "class_rule": "cumulative honest totals stand"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_brother_animal_golden_rule_passes(self):
        readout = {"quantities": [
            {"name": "median variance", "recorded_number": 3,
             "class_based": True,
             "class_rule": "brother animal golden"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_quantity_named_brother_passes(self):
        readout = {"quantities": [
            {"name": "brother", "recorded_number": 3,
             "class_based": True,
             "class_rule": "median variance reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_headline_easily_sentence_states_a_limit(self):
        sentence = "Scope holds only easily sampled points apply"
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_headline_honest_cumulative_sentence_states_limit(self):
        sentence = ("Honest cumulative scope stands only within "
                    "finite totals")
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_working_range_honest_cumulative_sentence_passes(self):
        self.assertTrue(mod11.validate_working_range_claim(
            "honest cumulative honest rows honest range kind",
            "honest cumulative", "honest rows",
            "honest range kind"))

    def test_working_range_escrow_coverage_sentence_passes(self):
        self.assertTrue(mod11.validate_working_range_claim(
            "escrow coverage escrow rows escrow range kind",
            "escrow coverage", "escrow rows",
            "escrow range kind"))

    def test_invented_strings_still_count_as_no_word(self):
        for word in ("blorple", "snizzle", "frumious", "quandrix"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word))
        self.assertEqual(mod11._plain_word_count(
            "blorple snizzle frumious quandrix"), 0)

    def test_readout_invented_strings_still_fail(self):
        readout = {"quantities": [
            {"name": "blorple share", "recorded_number": 3,
             "class_based": True,
             "class_rule": "blorple snizzle frumious quandrix"}]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_round5_named_words_still_readable(self):
        for word in ("sensitivity", "development", "triangle",
                     "decomposition", "contiguity", "endpoint",
                     "misuse", "indices", "replication",
                     "independent", "verification", "confidence",
                     "threshold", "actually", "amongst", "throughout",
                     "mountain", "doctor", "autumn"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_genuine_control_words_still_readable(self):
        for word in ("the", "water", "people", "kitchen", "garden",
                     "question", "median", "variance"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))


if __name__ == "__main__":
    unittest.main()

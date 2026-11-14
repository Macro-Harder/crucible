# Step 15 rerun Round 4 fix wave 4 tests, Builder 10.
# Items R4-025, R4-026, and R4-030 limb c, all at MOD-11.
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


def list_chain(length, leaf=7):
    value = leaf
    for _ in range(length):
        value = [value]
    return value


class TestR4025ReversedVouchGrounds(unittest.TestCase):
    def test_release_of_a_vouch_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a release of a vouch at the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_released_vouches_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on released vouches from the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_vouches_released_denied_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on vouches released from the seam.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_reversed_vouch_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "This result rests on a release of a vouch at the seam.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_vouches_released_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "This result rests on vouches released from the seam.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_release_of_vouch_liens_denied_still_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a release of vouch liens.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_singular_vouch_release_denied_still_fails(self):
        unit = unit_with_claim_extra(
            "This result rests on a vouch release.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_base_unit_still_passes_and_quotes(self):
        unit = compliant_unit()
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)


class TestR4025JoinedParleyGrounds(unittest.TestCase):
    def test_parleyq2_joined_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on ParleyQ2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parleyq5_joined_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on ParleyQ5.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parleyq2_joined_with_dq164_field10_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on ParleyQ2.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parleyq5_joined_with_dq164_field10_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on ParleyQ5.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_spaced_parley_q2_denied_still_fails(self):
        # Grounds in the scan terms: DQ-164, confirmation only.
        # A copy of the mark is carried in the run record.
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR4025VerbFormVouchGrounds(unittest.TestCase):
    def test_vouched_release_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouched release.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_vouching_releases_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on vouching releases.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_vouched_release_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouched release.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_vouching_releases_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on vouching releases.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_release_past_five_token_window_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouch amount that the parties "
            "later agreed would be subject to release.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_release_past_window_with_computed_field10_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouch amount that the parties "
            "later agreed would be subject to release.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))


class TestR4025PluralHeadWordForms(unittest.TestCase):
    def test_anchors_scenarios_denied_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchors scenarios AN-1 in its basis")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchors_scenarios_with_anchor_field10_passes(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchors scenarios AN-1 in its basis")
        unit["qualifiers_and_markings_block"] = FIELD10_ANCHOR_TEXT
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_singular_anchor_scenario_denied_still_fails(self):
        unit = compliant_unit()
        unit["assumption_record"] = (
            "the result rests on anchor scenario AN-1 in its basis")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_questions_two_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley questions two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_questions_five_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley questions five.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_questions_two_with_dq164_field10_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley questions two.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_singular_parley_question_two_denied_still_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR4026ReadableLexiconGenuineWords(unittest.TestCase):
    def test_register_named_words_are_readable(self):
        for word in ("because", "although", "despite", "hence",
                     "median", "variance", "question", "readable",
                     "children", "beautiful", "country"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_orange_probe_words_are_readable(self):
        for word in ("banana", "elephant", "zebra", "quilt",
                     "oxygen", "voyage", "purple", "orange",
                     "silver"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_further_proven_words_are_readable(self):
        for word in ("cohort", "quantile", "estimand", "whilst",
                     "among", "sometimes", "moreover", "meanwhile"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_because_sentence_counts_and_states_a_limit(self):
        sentence = "Scope holds only because sampled points apply"
        self.assertGreaterEqual(mod11._plain_word_count(sentence), 6)
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_because_sentence_headline_unit_passes(self):
        unit = compliant_unit()
        unit["claim_sentence"] = (
            "Scope holds only because sampled points apply.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_where_control_sentence_still_passes(self):
        sentence = "Scope holds only where sampled points apply"
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_working_range_genuine_uncommon_words_pass(self):
        self.assertTrue(mod11.validate_working_range_claim(
            "Zebra voyage banana country children A-1 R-1 K-1",
            "A-1", "R-1", "K-1"))

    def test_working_range_plain_text_still_passes(self):
        good = ("Over assumption set A-1, rows R-1 to R-9, in the "
                "working range kind, the claim holds within the "
                "stated scope and limits. Further sentences follow.")
        self.assertTrue(mod11.validate_working_range_claim(
            good, "assumption set A-1", "rows R-1 to R-9",
            "working range"))

    def test_readout_median_variance_passes(self):
        readout = {"quantities": [
            {"name": "median variance", "recorded_number": 3,
             "class_based": True,
             "class_rule": "median variance reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_orange_words_pass(self):
        readout = {"quantities": [
            {"name": "zebra voyage", "recorded_number": 3,
             "class_based": True,
             "class_rule": "zebra elephant banana voyage"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_genuine_control_still_passes(self):
        readout = {"quantities": [
            {"name": "holding share", "recorded_number": 3,
             "class_based": True,
             "class_rule": "a point stands in the holding class "
                           "where its share reaches the bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

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

    def test_genuine_control_words_still_readable(self):
        for word in ("the", "water", "people", "kitchen", "garden"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))


class TestR4030QuotedCopyContainersOnly(unittest.TestCase):
    def test_list_chain_101_within_bound(self):
        chain = list_chain(101)
        self.assertEqual(mod11._quoted_copy(chain), chain)

    def test_list_chain_102_past_bound_raises(self):
        with self.assertRaises(ValueError):
            mod11._quoted_copy(list_chain(102))

    def test_list_chain_100_still_copies(self):
        chain = list_chain(100)
        self.assertEqual(mod11._quoted_copy(chain), chain)


if __name__ == "__main__":
    unittest.main()

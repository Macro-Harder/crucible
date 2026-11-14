# Step 15 rerun Round 5 fix wave 5 tests, Builder 10.
# Items R5-008 MOD-11 limb, R5-028, R5-029, and R5-036, all at MOD-11.
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


def container_chain(length, leaf):
    value = leaf
    for _ in range(length):
        value = [value]
    return value


class EvilSet(set):
    def __new__(cls, items=()):
        if isinstance(items, (list, tuple)):
            return super().__new__(cls)
        return {"amount": 10, "currency": "USD"}


class EvilFrozenSet(frozenset):
    def __new__(cls, items=()):
        if isinstance(items, (list, tuple)):
            return super().__new__(cls, items)
        return {"amount": 10, "currency": "USD"}


class TestR5008QuotedCopyPlainConstructors(unittest.TestCase):
    def test_evil_set_copy_is_plain_set_of_stored_items(self):
        copied = mod11._quoted_copy({"part": EvilSet([1, 2])})
        self.assertEqual(copied, {"part": {1, 2}})
        self.assertIs(type(copied["part"]), set)

    def test_evil_frozenset_copy_is_plain_frozenset(self):
        copied = mod11._quoted_copy({"part": EvilFrozenSet([1, 2])})
        self.assertEqual(copied, {"part": frozenset({1, 2})})
        self.assertIs(type(copied["part"]), frozenset)

    def test_evil_set_at_top_level_copy_is_plain_set(self):
        copied = mod11._quoted_copy(EvilSet([1, 2]))
        self.assertEqual(copied, {1, 2})
        self.assertIs(type(copied), set)

    def test_evil_frozenset_at_top_level_copy_is_plain(self):
        copied = mod11._quoted_copy(EvilFrozenSet([1, 2]))
        self.assertEqual(copied, frozenset({1, 2}))
        self.assertIs(type(copied), frozenset)

    def test_plain_set_copy_control(self):
        copied = mod11._quoted_copy({"part": {1, 2}})
        self.assertEqual(copied, {"part": {1, 2}})
        self.assertIs(type(copied["part"]), set)

    def test_plain_frozenset_copy_control(self):
        copied = mod11._quoted_copy({"part": frozenset({1, 2})})
        self.assertEqual(copied, {"part": frozenset({1, 2})})
        self.assertIs(type(copied["part"]), frozenset)


class TestR5028AnchorVerbJoinedReversed(unittest.TestCase):
    def test_anchor_verb_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result is anchored in scenario AN-9.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_verb_wording_conforming_passes(self):
        unit = unit_with_claim_extra(
            "The result is anchored in scenario AN-9.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_joined_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on anchorscenario AN-9.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_joined_wording_conforming_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on anchorscenario AN-9.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_reversed_uses_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result uses scenario AN-9 as its anchor.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_reversed_uses_wording_conforming_passes(self):
        unit = unit_with_claim_extra(
            "The result uses scenario AN-9 as its anchor.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_reversed_leading_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "Scenario AN-9 is the anchor for this result.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_reversed_leading_conforming_passes(self):
        unit = unit_with_claim_extra(
            "Scenario AN-9 is the anchor for this result.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_testing_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on anchor testing AN-1.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_testing_wording_conforming_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on anchor testing AN-1.",
            field10=anchor_field10("AN-1"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_standard_wording_denied_control(self):
        unit = unit_with_claim_extra(
            "The result rests on an anchor scenario AN-9.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_standard_wording_conforming_control(self):
        unit = unit_with_claim_extra(
            "The result rests on an anchor scenario AN-9.",
            field10=anchor_field10("AN-9"))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_anchor_near_reversed_wording_denied_control(self):
        unit = unit_with_claim_extra(
            "The result rests on the scenario AN-9 anchor.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_anchor_test_wording_denied_control(self):
        unit = unit_with_claim_extra(
            "The result rests on anchor test AN-1.")
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR5028SeamAcrossStatementBoundary(unittest.TestCase):
    def test_seam_ground_across_statements_denied_fails(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouch at the seam. "
            "A release was later recorded for it.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_seam_ground_across_statements_conforming_passes(self):
        unit = unit_with_claim_extra(
            "The result rests on a vouch at the seam. "
            "A release was later recorded for it.",
            field10=FIELD10_COMPUTED_TEXT)
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_seam_ground_one_statement_denied_control(self):
        unit = unit_with_claim_extra(
            "A vouch at the seam released later by the parties "
            "stands in the basis.")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_base_unit_control_passes_and_quotes(self):
        unit = compliant_unit()
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)


class TestR5028ParleyOrdinalNumberReversed(unittest.TestCase):
    def test_parley_ordinal_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second Parley question.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_ordinal_wording_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the second Parley question.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_ordinal_depends_wording_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on the second Parley question.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_number_word_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question number two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_question_number_word_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley question number two.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_reversed_questions_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on questions two and five of Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_reversed_questions_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on questions two and five of Parley.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_parley_questions_two_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley questions two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_spaced_q2_denied_control(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley Q2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


PLAN_WORDS = ("sensitivity", "development", "triangle")
PLAN_PROBE_COMPANIONS = (
    "decomposition", "contiguity", "endpoint", "misuse", "indices")
READOUT_WORDS = (
    "replication", "independent", "verification", "confidence",
    "equivalence", "distribution", "threshold", "proportion",
    "deviation", "correlation", "regression", "parameter",
    "statistic", "hypothesis", "alternative", "exposure",
    "baseline", "duration", "percentage")
ORDINARY_WORDS = (
    "actually", "always", "amongst", "around", "barely", "been",
    "doing", "door", "ever", "possibly", "rarely", "something",
    "them", "took", "went", "were", "throughout", "mountain",
    "doctor", "autumn")


class TestR5029ReadableLexiconGenuineWords(unittest.TestCase):
    def test_plan_vocabulary_words_are_readable(self):
        for word in PLAN_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_plan_probe_companion_words_are_readable(self):
        for word in PLAN_PROBE_COMPANIONS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_vocabulary_words_are_readable(self):
        for word in READOUT_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_ordinary_words_are_readable(self):
        for word in ORDINARY_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_replication_threshold_name_passes(self):
        readout = {"quantities": [
            {"name": "replication threshold", "recorded_number": 3,
             "class_based": True,
             "class_rule": "median variance reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_replication_confidence_rule_passes(self):
        readout = {"quantities": [
            {"name": "median variance", "recorded_number": 3,
             "class_based": True,
             "class_rule": "replication confidence distribution"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_development_triangle_passes(self):
        readout = {"quantities": [
            {"name": "development triangle", "recorded_number": 3,
             "class_based": True,
             "class_rule": "development triangle reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_sensitivity_index_passes(self):
        readout = {"quantities": [
            {"name": "sensitivity index", "recorded_number": 3,
             "class_based": True,
             "class_rule": "sensitivity reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_ordinary_words_rule_passes(self):
        readout = {"quantities": [
            {"name": "median variance", "recorded_number": 3,
             "class_based": True,
             "class_rule": "always around door actually"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_headline_domain_sentence_states_a_limit(self):
        sentence = ("Replication scope stands only within the "
                    "threshold distribution")
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_headline_throughout_sentence_states_a_limit(self):
        sentence = "Scope holds only throughout sampled points apply"
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))

    def test_working_range_domain_sentence_passes(self):
        self.assertTrue(mod11.validate_working_range_claim(
            "replication threshold replication rows replication "
            "range kind",
            "replication threshold", "replication rows",
            "replication range kind"))

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
        for word in ("the", "water", "people", "kitchen", "garden",
                     "question", "median", "variance"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_parallel_plain_sentence_control(self):
        sentence = "Water scope stands only within the rate range"
        self.assertTrue(
            mod11._has_plain_scope_limits_sentence(sentence))


class TestR5036DepthContainersOnly(unittest.TestCase):
    def test_envelope_chain_101_containers_stands(self):
        self.assertTrue(
            mod11._envelope_part_stands(container_chain(101, "holds")))

    def test_envelope_chain_102_containers_does_not_stand(self):
        self.assertFalse(
            mod11._envelope_part_stands(container_chain(102, "holds")))

    def test_envelope_chain_100_containers_control(self):
        self.assertTrue(
            mod11._envelope_part_stands(container_chain(100, "holds")))

    def test_part_text_chain_101_containers_is_whole(self):
        self.assertEqual(
            mod11._part_text(container_chain(101, "holds")), "holds")

    def test_part_text_chain_102_containers_is_empty(self):
        self.assertEqual(
            mod11._part_text(container_chain(102, "holds")), "")

    def test_part_text_chain_100_containers_control(self):
        self.assertEqual(
            mod11._part_text(container_chain(100, "holds")), "holds")

    def test_quoted_copy_chain_101_control(self):
        chain = container_chain(101, 7)
        self.assertEqual(mod11._quoted_copy(chain), chain)


if __name__ == "__main__":
    unittest.main()

# Step 15 rerun Round 8 fix wave 8 tests, Builder 11.
# Rows R8-018 and R8-019, all at MOD-11.
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


class TestR8019LexiconWords(unittest.TestCase):
    def test_word_apple(self):
        self.assertTrue(mod11._is_readable_word("apple"))

    def test_word_bamboo(self):
        self.assertTrue(mod11._is_readable_word("bamboo"))

    def test_word_bathroom(self):
        self.assertTrue(mod11._is_readable_word("bathroom"))

    def test_word_beach(self):
        self.assertTrue(mod11._is_readable_word("beach"))

    def test_word_bedroom(self):
        self.assertTrue(mod11._is_readable_word("bedroom"))

    def test_word_bird(self):
        self.assertTrue(mod11._is_readable_word("bird"))

    def test_word_blue(self):
        self.assertTrue(mod11._is_readable_word("blue"))

    def test_word_boat(self):
        self.assertTrue(mod11._is_readable_word("boat"))

    def test_word_bronze(self):
        self.assertTrue(mod11._is_readable_word("bronze"))

    def test_word_brown(self):
        self.assertTrue(mod11._is_readable_word("brown"))

    def test_word_butter(self):
        self.assertTrue(mod11._is_readable_word("butter"))

    def test_word_camera(self):
        self.assertTrue(mod11._is_readable_word("camera"))

    def test_word_canyon(self):
        self.assertTrue(mod11._is_readable_word("canyon"))

    def test_word_carrot(self):
        self.assertTrue(mod11._is_readable_word("carrot"))

    def test_word_cheese(self):
        self.assertTrue(mod11._is_readable_word("cheese"))

    def test_word_chicken(self):
        self.assertTrue(mod11._is_readable_word("chicken"))

    def test_word_cinnamon(self):
        self.assertTrue(mod11._is_readable_word("cinnamon"))

    def test_word_cliff(self):
        self.assertTrue(mod11._is_readable_word("cliff"))

    def test_word_clock(self):
        self.assertTrue(mod11._is_readable_word("clock"))

    def test_word_cloud(self):
        self.assertTrue(mod11._is_readable_word("cloud"))

    def test_word_coast(self):
        self.assertTrue(mod11._is_readable_word("coast"))

    def test_word_cold(self):
        self.assertTrue(mod11._is_readable_word("cold"))

    def test_word_completeness(self):
        self.assertTrue(mod11._is_readable_word("completeness"))

    def test_word_conformance(self):
        self.assertTrue(mod11._is_readable_word("conformance"))

    def test_word_duck(self):
        self.assertTrue(mod11._is_readable_word("duck"))

    def test_word_fold(self):
        self.assertTrue(mod11._is_readable_word("fold"))

    def test_word_frog(self):
        self.assertTrue(mod11._is_readable_word("frog"))

    def test_word_garlic(self):
        self.assertTrue(mod11._is_readable_word("garlic"))

    def test_word_gate(self):
        self.assertTrue(mod11._is_readable_word("gate"))

    def test_word_ginger(self):
        self.assertTrue(mod11._is_readable_word("ginger"))

    def test_word_grape(self):
        self.assertTrue(mod11._is_readable_word("grape"))

    def test_word_graph(self):
        self.assertTrue(mod11._is_readable_word("graph"))

    def test_word_grey(self):
        self.assertTrue(mod11._is_readable_word("grey"))

    def test_word_honey(self):
        self.assertTrue(mod11._is_readable_word("honey"))

    def test_word_hostile(self):
        self.assertTrue(mod11._is_readable_word("hostile"))

    def test_word_juice(self):
        self.assertTrue(mod11._is_readable_word("juice"))

    def test_word_lake(self):
        self.assertTrue(mod11._is_readable_word("lake"))

    def test_word_lemon(self):
        self.assertTrue(mod11._is_readable_word("lemon"))

    def test_word_lion(self):
        self.assertTrue(mod11._is_readable_word("lion"))

    def test_word_lookup(self):
        self.assertTrue(mod11._is_readable_word("lookup"))

    def test_word_melon(self):
        self.assertTrue(mod11._is_readable_word("melon"))

    def test_word_passage(self):
        self.assertTrue(mod11._is_readable_word("passage"))

    def test_word_peach(self):
        self.assertTrue(mod11._is_readable_word("peach"))

    def test_word_pepper(self):
        self.assertTrue(mod11._is_readable_word("pepper"))

    def test_word_qualifier(self):
        self.assertTrue(mod11._is_readable_word("qualifier"))

    def test_word_resume(self):
        self.assertTrue(mod11._is_readable_word("resume"))

    def test_word_sheep(self):
        self.assertTrue(mod11._is_readable_word("sheep"))

    def test_word_snake(self):
        self.assertTrue(mod11._is_readable_word("snake"))

    def test_word_tiger(self):
        self.assertTrue(mod11._is_readable_word("tiger"))

    def test_word_timber(self):
        self.assertTrue(mod11._is_readable_word("timber"))

    def test_word_token(self):
        self.assertTrue(mod11._is_readable_word("token"))

    def test_word_tracer(self):
        self.assertTrue(mod11._is_readable_word("tracer"))

    def test_word_vanilla(self):
        self.assertTrue(mod11._is_readable_word("vanilla"))


class TestR8019Acts(unittest.TestCase):
    def test_plain_word_count_bronze_timber_bamboo(self):
        self.assertEqual(
            mod11._plain_word_count("bronze timber bamboo"), 3)

    def test_readout_gate_graph_passes(self):
        readout = {"quantities": [
            {"name": "gate graph", "recorded_number": 3,
             "class_based": True,
             "class_rule": "gate graph reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_readout_blue_bird_passes(self):
        readout = {"quantities": [
            {"name": "blue bird", "recorded_number": 3,
             "class_based": True,
             "class_rule": "blue bird reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))


class TestR8018ParleyForms(unittest.TestCase):
    def test_two_questions_that_parley_poses_direct(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "the two questions that parley poses"),
            {"2"})

    def test_two_questions_that_parley_poses_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two questions that "
            "Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_two_questions_that_parley_poses_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two questions that "
            "Parley poses.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_two_questions_that_parley_poses_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two questions that "
            "Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_two_questions_of_parley_direct(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "two questions of parley"),
            {"2"})

    def test_two_questions_of_parley_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on two questions of Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_two_questions_of_parley_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on two questions of Parley.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_two_questions_of_parley_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on two questions of Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_two_parley_questions_direct(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "the two parley questions"),
            {"2"})

    def test_two_parley_questions_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two Parley questions.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_two_parley_questions_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two Parley questions.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_two_parley_questions_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the two Parley questions.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_five_questions_that_parley_poses_direct(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "the five questions that parley poses"),
            {"5"})

    def test_five_questions_that_parley_poses_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the five questions that "
            "Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_five_questions_that_parley_poses_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim rests on the five questions that "
            "Parley poses.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_five_questions_that_parley_poses_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "This claim rests on the five questions that "
            "Parley poses.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)


R7_019_WORDS = (
    "dog", "cat", "sat", "sun", "man", "dance", "ball", "fire",
    "bread", "coffee", "sky", "city", "chair", "desert", "harbor",
    "meadow", "sunset", "sunrise", "thunder", "lightning",
    "rainbow", "breeze", "shadow", "mirror", "candle", "button",
    "wallet", "basket", "kettle", "blanket", "pillow", "curtain",
    "carpet", "ladder", "hammer", "needle", "thread", "copper",
    "marble", "velvet", "cotton", "wooden", "gold", "zinc",
    "east", "joyfully", "actor", "boundary", "canary", "carriage",
    "closure", "defect", "ledger", "mechanism", "partition",
    "probability", "reputation", "settlement", "anxiously",
    "eagerly", "nervously", "furthermore", "nevertheless",
    "nonetheless", "consequently", "accordingly", "precision",
    "reliability", "validity", "boy", "girl", "eye",
)


class TestControlsStandingBothWays(unittest.TestCase):
    def test_r7019_words_still_readable(self):
        self.assertEqual(len(R7_019_WORDS), 72)
        self.assertEqual(len(set(R7_019_WORDS)), 72)
        for word in R7_019_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_invented_strings_still_count_as_no_word(self):
        for word in ("blorple", "snizzle", "frumious",
                     "quandrix"):
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

    def test_readout_canary_boundary_control_passes(self):
        readout = {"quantities": [
            {"name": "canary boundary", "recorded_number": 3,
             "class_based": True,
             "class_rule": "canary boundary reaches bound"}]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_base_unit_control_passes(self):
        self.assertTrue(
            mod11.validate_headline_unit(compliant_unit()))

    def test_parley_no_number_states_no_ground(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "parley question with no stated number"),
            set())

    def test_r7020_charged_limbs_still_stand(self):
        self.assertEqual(
            mod11._parley_grounds_stated(
                "this claim rests on parley in the matter of "
                "the ruling marked q2"),
            {"2"})
        self.assertEqual(
            mod11._parley_grounds_stated(
                "the parley question stated as two in "
                "the record"),
            {"2"})
        self.assertEqual(
            mod11._parley_grounds_stated(
                "the parley question numbered as two"),
            {"2"})
        self.assertEqual(
            mod11._parley_grounds_stated(
                "parley question numbered two"),
            {"2"})
        self.assertIn(
            "2",
            mod11._parley_grounds_stated(
                "the second of the several questions that "
                "parley poses"))
        self.assertTrue(mod11._anchor_ground_stated(
            "the result rests on testanchor an-9"))

    def test_r7020_charged_limbs_denied_still_fail(self):
        unit = unit_with_claim_extra(
            "This claim rests on Parley in the matter of "
            "the ruling marked Q2.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))
        unit = unit_with_claim_extra(
            "This claim rests on the Parley question "
            "numbered as two.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


if __name__ == "__main__":
    unittest.main()

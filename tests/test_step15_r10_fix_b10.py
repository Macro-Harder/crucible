# Step 15 rerun Round 9 fix wave 9 tests, Builder 10.
# Rows R9-031 to R9-036, all at MOD-11.
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


def readout_for(name, rule):
    return {"quantities": [
        {"name": name, "recorded_number": 3,
         "class_based": True, "class_rule": rule}]}


class TestR9031DoubledConsonant(unittest.TestCase):
    def test_running(self):
        self.assertTrue(mod11._is_readable_word("running"))

    def test_swimming(self):
        self.assertTrue(mod11._is_readable_word("swimming"))

    def test_beginning(self):
        self.assertTrue(mod11._is_readable_word("beginning"))

    def test_planning(self):
        self.assertTrue(mod11._is_readable_word("planning"))

    def test_sitting(self):
        self.assertTrue(mod11._is_readable_word("sitting"))

    def test_getting(self):
        self.assertTrue(mod11._is_readable_word("getting"))

    def test_stopping(self):
        self.assertTrue(mod11._is_readable_word("stopping"))

    def test_winning(self):
        self.assertTrue(mod11._is_readable_word("winning"))

    def test_putting(self):
        self.assertTrue(mod11._is_readable_word("putting"))

    def test_stopped(self):
        self.assertTrue(mod11._is_readable_word("stopped"))

    def test_planned(self):
        self.assertTrue(mod11._is_readable_word("planned"))

    def test_dropped(self):
        self.assertTrue(mod11._is_readable_word("dropped"))

    def test_readout_running_stopped_planning_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "running share", "running stopped planning")))


class TestR9032SuperlativeEst(unittest.TestCase):
    def test_coldest(self):
        self.assertTrue(mod11._is_readable_word("coldest"))

    def test_bluest(self):
        self.assertTrue(mod11._is_readable_word("bluest"))

    def test_greyest(self):
        self.assertTrue(mod11._is_readable_word("greyest"))

    def test_brownest(self):
        self.assertTrue(mod11._is_readable_word("brownest"))

    def test_smallest(self):
        self.assertTrue(mod11._is_readable_word("smallest"))

    def test_largest(self):
        self.assertTrue(mod11._is_readable_word("largest"))

    def test_longest(self):
        self.assertTrue(mod11._is_readable_word("longest"))

    def test_strongest(self):
        self.assertTrue(mod11._is_readable_word("strongest"))

    def test_weakest(self):
        self.assertTrue(mod11._is_readable_word("weakest"))

    def test_fastest(self):
        self.assertTrue(mod11._is_readable_word("fastest"))

    def test_slowest(self):
        self.assertTrue(mod11._is_readable_word("slowest"))

    def test_brightest(self):
        self.assertTrue(mod11._is_readable_word("brightest"))

    def test_darkest(self):
        self.assertTrue(mod11._is_readable_word("darkest"))

    def test_cleanest(self):
        self.assertTrue(mod11._is_readable_word("cleanest"))

    def test_quickest(self):
        self.assertTrue(mod11._is_readable_word("quickest"))

    def test_readout_coldest_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "coldest share", "coldest cloudy morning")))


class TestR9033YAdjective(unittest.TestCase):
    def test_juicy(self):
        self.assertTrue(mod11._is_readable_word("juicy"))

    def test_cheesy(self):
        self.assertTrue(mod11._is_readable_word("cheesy"))

    def test_peachy(self):
        self.assertTrue(mod11._is_readable_word("peachy"))

    def test_cloudy(self):
        self.assertTrue(mod11._is_readable_word("cloudy"))

    def test_milky(self):
        self.assertTrue(mod11._is_readable_word("milky"))

    def test_rainy(self):
        self.assertTrue(mod11._is_readable_word("rainy"))

    def test_smoky(self):
        self.assertTrue(mod11._is_readable_word("smoky"))

    def test_windy(self):
        self.assertTrue(mod11._is_readable_word("windy"))

    def test_sandy(self):
        self.assertTrue(mod11._is_readable_word("sandy"))

    def test_tasty(self):
        self.assertTrue(mod11._is_readable_word("tasty"))

    def test_sticky(self):
        self.assertTrue(mod11._is_readable_word("sticky"))

    def test_snowy(self):
        self.assertTrue(mod11._is_readable_word("snowy"))

    def test_stormy(self):
        self.assertTrue(mod11._is_readable_word("stormy"))

    def test_sleepy(self):
        self.assertTrue(mod11._is_readable_word("sleepy"))

    def test_readout_juicy_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "juicy share", "juicy cheesy peachy")))


class TestR9034ClosedCompounds(unittest.TestCase):
    def test_bluebird(self):
        self.assertTrue(mod11._is_readable_word("bluebird"))

    def test_butterfly(self):
        self.assertTrue(mod11._is_readable_word("butterfly"))

    def test_clockwork(self):
        self.assertTrue(mod11._is_readable_word("clockwork"))

    def test_watermelon(self):
        self.assertTrue(mod11._is_readable_word("watermelon"))

    def test_notebook(self):
        self.assertTrue(mod11._is_readable_word("notebook"))

    def test_textbook(self):
        self.assertTrue(mod11._is_readable_word("textbook"))

    def test_handbook(self):
        self.assertTrue(mod11._is_readable_word("handbook"))

    def test_workbook(self):
        self.assertTrue(mod11._is_readable_word("workbook"))

    def test_bookshelf(self):
        self.assertTrue(mod11._is_readable_word("bookshelf"))

    def test_daylight(self):
        self.assertTrue(mod11._is_readable_word("daylight"))

    def test_moonlight(self):
        self.assertTrue(mod11._is_readable_word("moonlight"))

    def test_sunlight(self):
        self.assertTrue(mod11._is_readable_word("sunlight"))

    def test_starlight(self):
        self.assertTrue(mod11._is_readable_word("starlight"))

    def test_birdsong(self):
        self.assertTrue(mod11._is_readable_word("birdsong"))

    def test_applewood(self):
        self.assertTrue(mod11._is_readable_word("applewood"))

    def test_dogwood(self):
        self.assertTrue(mod11._is_readable_word("dogwood"))

    def test_goldfish(self):
        self.assertTrue(mod11._is_readable_word("goldfish"))

    def test_houseboat(self):
        self.assertTrue(mod11._is_readable_word("houseboat"))

    def test_spaceship(self):
        self.assertTrue(mod11._is_readable_word("spaceship"))

    def test_candlelight(self):
        self.assertTrue(mod11._is_readable_word("candlelight"))

    def test_plain_word_count_counts_compounds(self):
        self.assertEqual(mod11._plain_word_count(
            "the butterfly and the bluebird stood over "
            "the watermelon"), 6)

    def test_readout_butterfly_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "butterfly share", "butterfly bluebird watermelon")))

    def test_compound_with_part_outside_lexicon_still_false(self):
        for word in ("bluequandrix", "quandrixbird",
                     "buttersnizzle", "blorplefish"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word))


class TestR9035ReversedJoinedGrounds(unittest.TestCase):
    def test_question2parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "question2parley"), {"2"})

    def test_questions2parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "questions2parley"), {"2"})

    def test_q1parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "q1parley"), {"1"})

    def test_questiononeparley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "questiononeparley"), {"1"})

    def test_twoquestionsparley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "twoquestionsparley"), {"2"})

    def test_onequestionparley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "onequestionparley"), {"1"})

    def test_1qparley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "1qparley"), {"1"})

    def test_parley1q_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley1q"), {"1"})

    def test_twoparleyquestions_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "twoparleyquestions"), {"2"})

    def test_parleytwoquestions_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parleytwoquestions"), {"2"})

    def test_questiontwo_of_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "questiontwo of parley"), {"2"})

    def test_question2parley_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on question2parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_question2parley_conforming_passes(self):
        unit = unit_with_claim_extra(
            "This claim depends on question2parley.")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_question2parley_denied_quote_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on question2parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_q1parley_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on q1parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_twoquestionsparley_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on twoquestionsparley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR9036NumberBeforeQ(unittest.TestCase):
    def test_one_q_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "one q parley"), {"1"})

    def test_five_q_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "five q parley"), {"5"})

    def test_parley_one_q_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley one q"), {"1"})

    def test_parley_1_q_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley 1 q"), {"1"})

    def test_twoq_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "twoq parley"), {"2"})

    def test_1q_of_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "1q of parley"), {"1"})

    def test_one_q_parley_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on one q Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_parley_1_q_denied_fails(self):
        unit = unit_with_claim_extra(
            "This claim depends on Parley 1 q.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11.validate_headline_unit(unit))


SETTLEMENT3_WORDS = (
    "apple", "bamboo", "bathroom", "beach", "bedroom", "bird",
    "blue", "boat", "bronze", "brown", "butter", "camera",
    "canyon", "carrot", "cheese", "chicken", "cinnamon", "cliff",
    "clock", "cloud", "coast", "cold", "completeness",
    "conformance", "duck", "fold", "frog", "garlic", "gate",
    "ginger", "grape", "graph", "grey", "honey", "hostile",
    "juice", "lake", "lemon", "lion", "lookup", "melon",
    "passage", "peach", "pepper", "qualifier", "resume", "sheep",
    "snake", "tiger", "timber", "token", "tracer", "vanilla",
)

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
    def test_settlement3_words_still_readable(self):
        self.assertEqual(len(SETTLEMENT3_WORDS), 53)
        self.assertEqual(len(set(SETTLEMENT3_WORDS)), 53)
        for word in SETTLEMENT3_WORDS:
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

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
        self.assertFalse(mod11.validate_readout(readout_for(
            "blorple share", "blorple snizzle frumious quandrix")))

    def test_readout_gate_graph_control_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "gate graph", "gate graph reaches bound")))

    def test_forward_joined_grounds_still_read(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parleyquestion2"), {"2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "parleyquestionone"), {"1"})
        self.assertEqual(mod11._parley_grounds_stated(
            "parleyq1"), {"1"})

    def test_forward_q_grounds_still_read(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "q one parley"), {"1"})
        self.assertEqual(mod11._parley_grounds_stated(
            "q five parley"), {"5"})
        self.assertEqual(mod11._parley_grounds_stated(
            "parley q two"), {"2"})

    def test_parley_no_number_states_no_ground(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley question with no stated number"), set())

    def test_base_unit_control_passes(self):
        self.assertTrue(
            mod11.validate_headline_unit(compliant_unit()))


if __name__ == "__main__":
    unittest.main()

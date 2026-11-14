# Step 15 rerun Round 11 fix wave 11 tests, Builder 4.
# Rows R11-036 to R11-055, all at MOD-11: lexicon limbs and
# Parley grounds placements. Plain simulated values only.
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


def unit_denying(sentence):
    unit = compliant_unit()
    unit["claim_sentence"] = CLAIM_TEXT + " " + sentence
    unit["qualifiers_and_markings_block"] = FIELD10_NO_DEPENDENCE_TEXT
    return unit


def readout_for(rule):
    return {"quantities": [
        {"name": "sample share", "recorded_number": 3,
         "class_based": True, "class_rule": rule}]}


def assert_all_readable(case, words):
    for word in words:
        with case.subTest(word=word):
            case.assertTrue(mod11._is_readable_word(word), word)


def assert_none_readable(case, words):
    for word in words:
        with case.subTest(word=word):
            case.assertFalse(mod11._is_readable_word(word), word)


class TestR11036Ness(unittest.TestCase):
    def test_plain_ness_words(self):
        # The Red 2 base confirmed forms only: illness,
        # madness, and gladness yield their stems under the
        # cure but ill, mad, and glad stand in no lexicon
        # entry, the lexicon gap class the papers record.
        assert_all_readable(self, [
            "sadness", "darkness", "kindness", "happiness",
            "fitness", "brightness", "loneliness", "busyness",
            "sickness", "thickness", "weakness", "greatness",
            "softness", "hardness"])

    def test_ness_as_compound_part(self):
        assert_all_readable(self, [
            "sadnessreport", "darknessfalls", "happinessshare"])

    def test_ness_on_whole_compound(self):
        assert_all_readable(self, ["notebookness", "bluebirdness"])

    def test_readout_ness(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("sadness darkness kindness")))


class TestR11037ErEFinal(unittest.TestCase):
    def test_e_final_comparatives(self):
        assert_all_readable(self, [
            "larger", "wiser", "braver", "finer", "nicer",
            "safer", "simpler", "gentler", "bluer", "freer",
            "huger", "littler", "looser", "politer", "purer",
            "truer", "whiter", "wider", "closer"])

    def test_e_final_agent_nouns(self):
        assert_all_readable(self, [
            "dancer", "driver", "lover", "maker", "manager",
            "observer", "provider", "computer", "arguer",
            "ruler", "gamer", "miner", "smoker"])

    def test_readout_er(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("larger wiser braver")))


class TestR11038En(unittest.TestCase):
    def test_en_words(self):
        assert_all_readable(self, [
            "brighten", "darken", "harden", "soften", "widen",
            "sharpen", "deepen", "shorten", "weaken",
            "strengthen", "lengthen", "sweeten", "freshen"])

    def test_en_stacked_ed_ing(self):
        assert_all_readable(self, ["brightened", "brightening"])

    def test_en_compound_part(self):
        assert_all_readable(self, ["brightenhouse"])

    def test_readout_en(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("brighten darken harden")))


class TestR11039Ful(unittest.TestCase):
    def test_ful_words(self):
        # Joyful and successful yield their stems under the
        # cure but joy and success stand in no lexicon entry.
        assert_all_readable(self, [
            "helpful", "thankful", "powerful",
            "playful", "hopeful", "stressful"])

    def test_ful_compounds(self):
        assert_all_readable(self, [
            "helpfulhouse", "doghouseful", "houseboatful"])

    def test_ful_stacked_ness(self):
        assert_all_readable(self, ["helpfulness"])

    def test_readout_ful(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("helpful thankful powerful")))


class TestR11040Ish(unittest.TestCase):
    def test_ish_words(self):
        assert_all_readable(self, [
            "childish", "selfish", "boyish", "girlish",
            "bookish", "darkish", "greenish", "reddish",
            "bluish", "smallish"])

    def test_readout_ish(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("childish selfish bookish")))


class TestR11041Ment(unittest.TestCase):
    def test_ment_words(self):
        assert_all_readable(self, [
            "movement", "management", "judgement"])

    def test_ment_compounds(self):
        assert_all_readable(self, [
            "movementreport", "notebookmovement"])

    def test_readout_ment(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("movement management judgement")))


class TestR11042AlIveOus(unittest.TestCase):
    def test_al_words(self):
        assert_all_readable(self, [
            "national", "regional", "musical"])

    def test_ive_words(self):
        assert_all_readable(self, [
            "active", "creative", "effective"])

    def test_ous_words(self):
        # Dangerous and glorious yield their stems under the
        # cure but danger and glory stand in no lexicon entry.
        assert_all_readable(self, ["nervous", "victorious"])

    def test_readout_al_ive_ous(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("national regional musical")))
        self.assertTrue(mod11.validate_readout(
            readout_for("active creative nervous")))


class TestR11043UnPrefix(unittest.TestCase):
    def test_un_words(self):
        assert_all_readable(self, [
            "unhappy", "unfair", "unsafe", "unkind", "unclean"])

    def test_un_stacked_comparative(self):
        assert_all_readable(self, ["unhappier"])

    def test_readout_un(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("unhappy unfair unsafe")))


class TestR11044TwoLetterCompoundParts(unittest.TestCase):
    def test_two_part_compounds(self):
        assert_all_readable(self, [
            "onboard", "inhouse", "byline", "backup",
            "setup", "sunup"])

    def test_three_part_compounds(self):
        assert_all_readable(self, [
            "backuphouse", "housebackup", "birdinhouse",
            "houseonfire"])

    def test_readout_two_letter_compounds(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("onboard inhouse byline")))


class TestR11045WhollyDuly(unittest.TestCase):
    def test_wholly(self):
        self.assertTrue(mod11._is_readable_word("wholly"))

    def test_duly(self):
        self.assertTrue(mod11._is_readable_word("duly"))

    def test_readout_wholly(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("wholly largely bravely")))

    def test_readout_duly(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("the wholly duly night")))


class TestR11046ErEstYOvershoot(unittest.TestCase):
    def test_misspelt_comparatives_rejected(self):
        assert_none_readable(self, [
            "biger", "bigest", "hoter", "hotest", "sader",
            "sadest", "fiter", "fitest", "weter", "wetest"])

    def test_noun_comparatives_rejected(self):
        assert_none_readable(self, [
            "suner", "sunest", "doger", "dogest",
            "tableer", "chairest"])

    def test_y_noun_overshoot_rejected(self):
        assert_none_readable(self, [
            "booky", "chairy", "housey", "windowy"])

    def test_readout_overshoot_rejected(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("biger hoter suner")))

    def test_doubled_controls_still_read(self):
        assert_all_readable(self, [
            "bigger", "biggest", "hotter", "hottest",
            "sadder", "sunny", "doggy"])


class TestR11047YFourLetter(unittest.TestCase):
    def test_four_letter_y_words(self):
        assert_all_readable(self, [
            "airy", "oily", "wavy", "wiry", "ropy",
            "nosy", "sexy"])

    def test_fiery(self):
        self.assertTrue(mod11._is_readable_word("fiery"))

    def test_readout_y_four(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("the wavy oily night")))


class TestR11048IngFiveLetter(unittest.TestCase):
    def test_ing_words(self):
        assert_all_readable(self, ["using", "lying", "tying"])

    def test_readout_ing(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("the using lying tying")))


class TestR11049EdFourLetter(unittest.TestCase):
    def test_ed_words(self):
        assert_all_readable(self, [
            "eyed", "lied", "tied", "toed"])

    def test_readout_ed(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("the tied eyed toed")))


class TestR11050VesPlurals(unittest.TestCase):
    def test_ves_plurals(self):
        assert_all_readable(self, [
            "wives", "halves", "shelves", "selves"])

    def test_readout_ves(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("the wives halves selves")))


class TestR11051NaiveSPlurals(unittest.TestCase):
    def test_naive_plurals_rejected(self):
        assert_none_readable(self, [
            "childs", "mans", "womans", "sheeps", "tooths"])


class TestControlsStillStand(unittest.TestCase):
    def test_cured_controls_read(self):
        assert_all_readable(self, [
            "sunny", "doggy", "bigger", "biggest", "happier",
            "happiest", "angrily", "carried", "coldestnight",
            "notebooks", "butterflies", "doghouses",
            "blackbirdhouse", "bluebirdhouse", "doghousefire",
            "sunlightmoon", "daylighttime"])

    def test_invented_controls_rejected(self):
        assert_none_readable(self, [
            "blorple", "snizzle", "frumious"])


class TestR11052QBeforeNameNumberAfter(unittest.TestCase):
    def test_joined_forms(self):
        cases = {
            "qparley2": {"2"}, "qparleytwo": {"2"},
            "qparley1": {"1"}, "qparley5": {"5"},
            "questionparley2": {"2"},
            "questionparleytwo": {"2"},
            "questionsparley5": {"5"},
            "questionsparleyfive": {"5"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_spaced_forms(self):
        cases = {
            "qparley 2": {"2"}, "qparley two": {"2"},
            "questionparley 2": {"2"}, "q parley 2": {"2"},
            "q parley two": {"2"}, "q parley 1": {"1"},
            "q parley five": {"5"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_separated_forms(self):
        cases = {
            "qparley-2": {"2"}, "qparley/2": {"2"},
            "qparley.2": {"2"}, "qparley:two": {"2"},
            "qparley_2": {"2"}, "questionparley-2": {"2"},
            "q-parley-2": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_composed_forms(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley q1 and on qparley2"), {"1", "2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "parley q1 and on qparleyfive"), {"1", "5"})
        self.assertEqual(mod11._parley_grounds_stated(
            "the claim depends on qparley1 and on qparley5"),
            {"1", "5"})
        self.assertEqual(mod11._parley_grounds_stated(
            "the claim depends on q parley five and on qparley1"),
            {"1", "5"})

    def test_validation_refused(self):
        for sentence in (
                "the claim depends on qparley2",
                "the claim depends on qparleytwo",
                "the claim depends on questionparley2",
                "the claim depends on qparley 2",
                "the claim depends on q parley 2",
                "the claim depends on q-parley-2",
                "the claim depends on QPARLEY5"):
            with self.subTest(sentence=sentence):
                unit = unit_denying(sentence)
                self.assertFalse(mod11._field10_matches_grounds(unit))
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


class TestR11053NumberBeforeNameQAfter(unittest.TestCase):
    def test_joined_forms(self):
        cases = {
            "twoparleyq": {"2"}, "oneparleyq": {"1"},
            "fiveparleyq": {"5"}, "1parleyq": {"1"},
            "2parleyq": {"2"}, "5parleyq": {"5"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_spaced_forms(self):
        cases = {
            "two parley q": {"2"}, "one parley q": {"1"},
            "five parley q": {"5"}, "2 parley q": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_separated_forms(self):
        cases = {
            "two-parley-q": {"2"}, "two/parley/q": {"2"},
            "one-parley-q": {"1"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_composed_forms(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "twoparleyq and on parley q1"), {"1", "2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "the claim depends on twoparleyq and on oneparleyq"),
            {"1", "2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "the claim depends on 2parleyq and on 5parleyq"),
            {"2", "5"})

    def test_validation_refused(self):
        for sentence in (
                "the claim depends on twoparleyq",
                "the claim depends on two parley q",
                "the claim depends on 1parleyq",
                "the claim depends on two-parley-q"):
            with self.subTest(sentence=sentence):
                unit = unit_denying(sentence)
                self.assertFalse(mod11._field10_matches_grounds(unit))
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


class TestR11054OrdinalWithQ(unittest.TestCase):
    def test_spaced_ordinal_word_q_forms(self):
        cases = {
            "parley q first": {"1"}, "parley q second": {"2"},
            "parley q fifth": {"5"}, "parley first q": {"1"},
            "parley second q": {"2"}, "first q parley": {"1"},
            "second q parley": {"2"}, "q first parley": {"1"},
            "q second parley": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_spaced_suffixed_digit_q_forms(self):
        cases = {
            "parley q 1st": {"1"}, "parley q 2nd": {"2"},
            "parley 1st q": {"1"}, "parley 2nd q": {"2"},
            "1st q parley": {"1"}, "q 2nd parley": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_joined_ordinal_forms(self):
        cases = {
            "parleyquestionfirst": {"1"},
            "parleyquestionsecond": {"2"},
            "questionfirstparley": {"1"},
            "parleyfirstq": {"1"}, "firstqparley": {"1"},
            "parley1stq": {"1"}, "parleyq1st": {"1"},
            "parley2ndq": {"2"}, "q1stparley": {"1"},
            "2ndqparley": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_composed_forms(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parley q first and on parley q2"), {"1", "2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "the claim depends on first q parley and on "
            "second q parley"), {"1", "2"})

    def test_validation_refused(self):
        for sentence in (
                "the claim depends on parley q first",
                "the claim depends on first q parley",
                "the claim depends on parley q 2nd",
                "the claim depends on parleyquestionfirst",
                "the claim depends on PARLEY Q FIRST"):
            with self.subTest(sentence=sentence):
                unit = unit_denying(sentence)
                self.assertFalse(mod11._field10_matches_grounds(unit))
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


class TestR11055PluralOrLargerNameSpacedQuestion(unittest.TestCase):
    def test_spaced_question_forms(self):
        cases = {
            "parleys question 2": {"2"},
            "parleys question two": {"2"},
            "parleys questions 2": {"2"},
            "parleys questions two": {"2"},
            "xparley question 2": {"2"},
            "parleyx question 2": {"2"},
            "preparley question 2": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_bare_controls_stay_empty(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "parleys question"), set())
        self.assertEqual(mod11._parley_grounds_stated(
            "xparley question"), set())

    def test_q_sibling_controls_read(self):
        cases = {
            "parleys q2": {"2"}, "parleys qtwo": {"2"},
            "xparley q2": {"2"}, "xparley qtwo": {"2"},
            "preparley q2": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_validation_refused(self):
        for sentence in (
                "the claim depends on parleys question 2",
                "the claim depends on parleys questions two",
                "the claim depends on xparley question 2"):
            with self.subTest(sentence=sentence):
                unit = unit_denying(sentence)
                self.assertFalse(mod11._field10_matches_grounds(unit))
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


if __name__ == "__main__":
    unittest.main()

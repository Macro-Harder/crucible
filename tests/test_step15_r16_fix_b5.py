"""Fix wave 15 pins, Builder 5: rows R15-042 to R15-045 and
R15-095.

MOD-11 stem ed limb at sinked, ies limb at wifies and lifies,
er and est undoubling at sunner and sunnest, able, ible, and
ability cross spellings, and the headline identifier conversion
limb letting a bare RuntimeError escape.
"""
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


def readout_for(rule):
    return {"quantities": [
        {"name": "sample share", "recorded_number": 3,
         "class_based": True, "class_rule": rule}]}


class RaisingStr:
    def __str__(self):
        raise RuntimeError("string reading raises")


class TestR15042EdSinked(unittest.TestCase):
    def test_sinked_not_readable(self):
        self.assertFalse(mod11._is_readable_word("sinked"))

    def test_sinked_yields_no_sink_stem(self):
        self.assertNotIn("sink", mod11._readable_stem("sinked"))
        self.assertNotIn("sinke", mod11._readable_stem("sinked"))

    def test_readout_refuses_sinked_rule(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("sinked result holds")))

    def test_controls_hold(self):
        self.assertTrue(mod11._is_readable_word("sink"))
        for word in ("hitted", "tooked", "gaved", "spinned"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)
        self.assertFalse(mod11.validate_readout(
            readout_for("hitted result holds")))


class TestR15043IesWifeLife(unittest.TestCase):
    def test_wifies_lifies_not_readable(self):
        for word in ("wifies", "lifies"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_wifies_lifies_yield_no_barred_derivation(self):
        self.assertNotIn("wify", mod11._readable_stem("wifies"))
        self.assertNotIn("lify", mod11._readable_stem("lifies"))

    def test_readout_refuses_wifies_lifies_rule(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("wifies lifies result")))

    def test_cured_kin_hold(self):
        for word in ("wifees", "lifees", "leafies", "childies",
                     "dataies", "sheepies", "halfies", "shelfies",
                     "mouseies", "footies", "toothies"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)
        self.assertFalse(mod11.validate_readout(
            readout_for("childes dataes result")))
        for word in ("parties", "stories", "classes"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)


class TestR15044ErEstSunDoubled(unittest.TestCase):
    def test_sunner_sunnest_not_readable(self):
        for word in ("sunner", "sunnest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_sunner_sunnest_yield_no_sun_stem(self):
        self.assertNotIn("sun", mod11._readable_stem("sunner"))
        self.assertNotIn("sun", mod11._readable_stem("sunnest"))

    def test_readout_refuses_sunner_sunnest_rule(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("sunner sunnest result")))

    def test_controls_hold(self):
        for word in ("suner", "sunest", "mucher", "muchest",
                     "manyer", "wronger", "wrongest", "realer",
                     "realest", "gooder", "goodest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)
        self.assertTrue(mod11._is_readable_word("sun"))
        self.assertTrue(mod11._is_readable_word("sunny"))
        self.assertTrue(mod11._is_readable_word("sunning"))


class TestR15045AbleIbleCrossSpellings(unittest.TestCase):
    def test_able_spellings_of_ible_bases_refused(self):
        for word in ("accessable", "convertable"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_ible_spellings_of_able_bases_refused(self):
        for word in ("washible", "breakible", "portible",
                     "movible", "lovible", "likible", "sizible",
                     "usible", "readible"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_ability_cross_spellings_refused(self):
        for word in ("accessability", "convertability"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_readouts_refuse_cross_spelled_rules(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("accessable convertable washible")))
        self.assertFalse(mod11.validate_readout(
            readout_for("breakible portible movible")))
        self.assertFalse(mod11.validate_readout(
            readout_for("readible usible likible")))
        self.assertFalse(mod11.validate_readout(
            readout_for("accessability convertability result")))

    def test_lawful_controls_hold(self):
        for word in ("accessible", "convertible", "washable",
                     "breakable", "portable", "movable", "lovable",
                     "likable", "sizable", "usable", "readable",
                     "usability", "breakability", "washability",
                     "accessibility", "convertibility",
                     "visibility", "sensibility", "capability",
                     "visible", "sensible"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)
        self.assertTrue(mod11.validate_readout(
            readout_for("accessible convertible washable")))


class TestR15095HeadlineIdentifierRaisingStr(unittest.TestCase):
    def test_compliant_unit_quotes_whole(self):
        unit = compliant_unit()
        self.assertTrue(mod11.validate_headline_unit(unit))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(
            quoted["headline_unit_identifier_and_issue_date"],
            unit["headline_unit_identifier_and_issue_date"])

    def test_raising_identifier_validates_false_no_bare_escape(self):
        unit = compliant_unit()
        unit["headline_unit_identifier_and_issue_date"] = RaisingStr()
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_raising_identifier_quote_raises_named_value_error(self):
        unit = compliant_unit()
        unit["headline_unit_identifier_and_issue_date"] = RaisingStr()
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertIn("quote_headline_unit stands refused",
                      str(caught.exception))

    def test_raising_object_in_other_fields_still_named(self):
        for field in mod11.HEADLINE_UNIT_FIELDS:
            if field == "headline_unit_identifier_and_issue_date":
                continue
            unit = compliant_unit()
            unit[field] = RaisingStr()
            with self.subTest(field=field):
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


if __name__ == "__main__":
    unittest.main()

"""Fix wave 12 pins, Builder 5: rows R12-025 to R12-033 and R12-045.

MOD-11 lexicon limbs, Parley grounds placements, the long token
cost, and the publication record stored reading. Every act stands
on the stored contents of the handed form, read through base class
readings, and on the proving acts the Round 12 source papers used:
Red 1 Findings 2 to 5, Blue 1 Finding 1, Yellow 1 Findings Y1-1 to
Y1-4, and Purple 1 Finding 3.
"""
import time
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


def assert_grounds(case, cases):
    for text, expected in cases.items():
        with case.subTest(text=text):
            case.assertEqual(mod11._parley_grounds_stated(text), expected)


def assert_unit_refused(case, sentence):
    unit = unit_denying(sentence)
    case.assertFalse(mod11.validate_headline_unit(unit))
    with case.assertRaises(ValueError):
        mod11.quote_headline_unit(unit)


class TestR12025SIrregular(unittest.TestCase):
    def test_s_irregular_forms(self):
        assert_none_readable(self, ["wifes", "mouses", "foots"])

    def test_s_controls(self):
        assert_all_readable(self, ["wives", "houses"])
        assert_none_readable(self, ["childs", "sheeps", "tooths"])

    def test_readout_s_irregular(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("wifes mouses foots")))
        self.assertFalse(mod11.validate_readout(
            readout_for("childs sheeps tooths")))
        self.assertTrue(mod11.validate_readout(
            readout_for("houses chairs tables")))


class TestR12025EdIrregular(unittest.TestCase):
    def test_ed_irregular_forms(self):
        assert_none_readable(self, [
            "wented", "teached", "bringed", "runned", "swimmed"])

    def test_readout_ed_irregular(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("wented teached bringed")))
        self.assertTrue(mod11.validate_readout(
            readout_for("houses chairs tables")))


class TestR12026LongTokenCost(unittest.TestCase):
    def test_long_token_answers_fast(self):
        start = time.perf_counter()
        result = mod11._is_readable_word("a" * 2000)
        elapsed = time.perf_counter() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 2.0)

    def test_long_token_readout_answers_fast(self):
        start = time.perf_counter()
        result = mod11.validate_readout(
            readout_for("a" * 2000 + " sample"))
        elapsed = time.perf_counter() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 2.0)

    def test_compound_friendly_long_token(self):
        self.assertTrue(mod11._is_readable_word("house" * 400))


class TestR12027DomHood(unittest.TestCase):
    def test_dom_hood_words(self):
        assert_all_readable(self, [
            "kingdom", "freedom", "childhood", "brotherhood",
            "manhood", "womanhood", "neighbourhood"])

    def test_readout_dom_hood(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("kingdom childhood brotherhood")))
        self.assertTrue(mod11.validate_readout(
            readout_for("sadness darkness kindness")))


class TestR12028TionAnceIty(unittest.TestCase):
    def test_tion_ance_ence_ity_words(self):
        assert_all_readable(self, [
            "creation", "information", "resistance", "existence",
            "appearance", "importance", "possibility"])

    def test_readout_tion_ance_ity(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("creation resistance existence")))


class TestR12029IzeIfyIstIsm(unittest.TestCase):
    def test_ize_ify_ist_ism_words(self):
        assert_all_readable(self, [
            "modernize", "realize", "organize", "classify",
            "simplify", "tourist", "realism", "tourism"])

    def test_artist_stem_yields_art(self):
        # The ist limb yields the true base of artist. That base
        # stands in no lexicon entry, so no readable assertion
        # stands on artist itself in this pin file.
        self.assertIn("art", mod11._readable_stem("artist"))

    def test_readout_ize_ify_ist(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("modernize classify tourist")))


class TestR12030SpacedQBesideLargerName(unittest.TestCase):
    def test_spaced_q_forms(self):
        assert_grounds(self, {
            "parleys q 2": {"2"}, "parleys q two": {"2"},
            "parleys q second": {"2"}, "parleys q 5": {"5"},
            "xparley q 2": {"2"}, "parleyx q 2": {"2"},
        })

    def test_spaced_q_controls(self):
        assert_grounds(self, {
            "parleys question 2": {"2"}, "parleys q2": {"2"},
            "parley q 2": {"2"}, "parleys 2 q": {"2"},
        })

    def test_public_gate_spaced_q(self):
        for sentence in (
                "This result depends on parleys q 2.",
                "This result depends on parleys q two.",
                "This result depends on xparley q 2."):
            with self.subTest(sentence=sentence):
                assert_unit_refused(self, sentence)
        assert_unit_refused(
            self, "This result depends on parley question 2.")


class TestR12031JoinedOrdinalAfterQ(unittest.TestCase):
    def test_joined_ordinal_after_q(self):
        assert_grounds(self, {"parley q2nd": {"2"}})

    def test_joined_ordinal_controls(self):
        assert_grounds(self, {
            "parley q 2nd": {"2"}, "parleyq1st": {"1"},
            "parley1stq": {"1"},
        })

    def test_public_gate_q2nd(self):
        assert_unit_refused(
            self, "This result depends on parley q2nd.")
        assert_unit_refused(
            self, "This result depends on parley q 2nd.")


class TestR12032OrdinalBeforeNameQAfter(unittest.TestCase):
    def test_joined_ordinal_before_name(self):
        assert_grounds(self, {
            "firstparleyq": {"1"}, "secondparleyq": {"2"},
            "fifthparleyq": {"5"}, "1stparleyq": {"1"},
            "2ndparleyq": {"2"}, "5thparleyq": {"5"},
        })

    def test_no_ground_numbers_stay_empty(self):
        assert_grounds(self, {
            "thirdparleyq": set(), "3rdparleyq": set(),
            "4thparleyq": set(),
        })

    def test_public_gate_ordinal_before_name(self):
        unit = unit_denying("This result depends on firstparleyq.")
        self.assertFalse(mod11._field10_matches_grounds(unit))
        assert_unit_refused(
            self, "This result depends on firstparleyq.")
        assert_unit_refused(
            self, "This result depends on first parley q.")


class TestR12033NumberedWithoutQuestion(unittest.TestCase):
    def test_numbered_forms(self):
        assert_grounds(self, {
            "parley numbered two": {"2"},
            "parley numbered 2": {"2"},
            "parley numbered five": {"5"},
            "parley q numbered two": {"2"},
            "numbered two parley": {"2"},
        })

    def test_numbered_controls(self):
        assert_grounds(self, {
            "parley question numbered two": {"2"},
            "parley questions numbered five": {"5"},
            "parley number two": {"2"},
            "parley question number two": {"2"},
        })

    def test_public_gate_numbered(self):
        unit = unit_denying("depends on parley numbered two")
        self.assertFalse(mod11._field10_matches_grounds(unit))
        marked = unit_denying("depends on Parley Q2")
        self.assertFalse(mod11._field10_matches_grounds(marked))
        marked["qualifiers_and_markings_block"] = FIELD10_TEXT
        self.assertTrue(mod11._field10_matches_grounds(marked))


class GetReportDict(dict):
    """Stores pairs plainly; its get reading reports other pairs."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class GetNothingDict(dict):
    """Stores pairs plainly; its get reading reports nothing."""

    def get(self, key, default=None):
        return default


def publication_record(failed=()):
    verdicts = {check: "passed" for check in mod11.RETIREMENT_CHECKS}
    for check in failed:
        verdicts[check] = "failed"
    return {
        "test_run": "run-1",
        "version": "v1",
        "verdicts": verdicts,
        "failures_recorded": list(failed),
    }


class TestR12045PublicationStoredReading(unittest.TestCase):
    def test_plain_controls(self):
        self.assertTrue(mod11.validate_publication_record(
            publication_record()))
        record = publication_record(failed=("T-03",))
        record["failures_recorded"] = []
        self.assertFalse(mod11.validate_publication_record(record))

    def test_get_reports_failure_recorded(self):
        stored = publication_record(failed=("T-03",))
        stored["failures_recorded"] = []
        lying = GetReportDict(
            stored, dict(stored, failures_recorded=["T-03"]))
        self.assertFalse(mod11.validate_publication_record(lying))
        unit = {"publication_record": lying}
        self.assertFalse(mod11.unit_is_publishable(unit))

    def test_get_reports_nothing_mirror(self):
        lying = GetNothingDict(publication_record())
        self.assertTrue(mod11.validate_publication_record(lying))
        unit = {"publication_record": publication_record()}
        self.assertTrue(mod11.unit_is_publishable(unit))

    def test_verdicts_get_reports_failure(self):
        stored = publication_record()
        stored["failures_recorded"] = ["T-03"]
        reported_verdicts = dict(stored["verdicts"], **{"T-03": "failed"})
        stored["verdicts"] = GetReportDict(
            stored["verdicts"], reported_verdicts)
        self.assertFalse(mod11.validate_publication_record(stored))

    def test_unit_get_reports_record(self):
        reported = publication_record()
        unit = GetReportDict({}, {"publication_record": reported})
        self.assertFalse(mod11.unit_is_publishable(unit))
        empty_unit = GetNothingDict(
            {"publication_record": publication_record()})
        self.assertTrue(mod11.unit_is_publishable(empty_unit))


if __name__ == "__main__":
    unittest.main()

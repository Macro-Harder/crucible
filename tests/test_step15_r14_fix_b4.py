"""Fix wave 13 pins, Builder 4: rows R13-017 to R13-020, R13-040,
R13-041, and R13-055.

MOD-11 publication record iteration and equality limbs, the
Parley grounds ordinal before the name in the next ring of
joined, split, and fused forms, the stem limbs next ring and
the able derivation, the headline unit builder copy limb under
settlement S-1, the publication verdict value limb, and the
headline unit builder refusal wording. Every act stands on the
proving acts the Round 13 source papers used: Red 5 Findings 1
to 4, Yellow 5 Findings Y5-1 to Y5-3, Orange 3 Findings 1 to 3,
Yellow 1 Finding Y1-3, and Orange 5 Finding 4.
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


def genuine_record():
    verdicts = mod11.retirement_verdicts("F-01")
    failures = [check for check in mod11.RETIREMENT_CHECKS
                if verdicts[check] == "failed"]
    return {
        "test_run": "retirement run 1",
        "version": "report format paper version pinned in the "
                   "family record",
        "verdicts": verdicts,
        "failures_recorded": failures,
    }


def passed_record():
    return {
        "test_run": "retirement run 1",
        "version": "v1",
        "verdicts": {check: "passed"
                     for check in mod11.RETIREMENT_CHECKS},
        "failures_recorded": [],
    }


class IterationReportDict(dict):
    """A dict whose iteration and keys readings report a fixed
    name list, whatever pairs it stores."""

    def __init__(self, stored, reported_names):
        super().__init__(stored)
        self._reported_names = list(reported_names)

    def __iter__(self):
        return iter(self._reported_names)

    def keys(self):
        return list(self._reported_names)


class EqualityLiar:
    """A plain object whose equality reading answers True
    against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class CopyLiar:
    """A value whose copy protocol returns a fabricated text."""

    def __deepcopy__(self, memo):
        return "LIED"

    def __copy__(self):
        return "LIED"


class CopyRaiser:
    """A value whose copy protocol raises."""

    def __deepcopy__(self, memo):
        raise RuntimeError("copy protocol raised")

    def __copy__(self):
        raise RuntimeError("copy protocol raised")


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
            case.assertEqual(
                mod11._parley_grounds_stated(text), expected)


def assert_unit_refused(case, sentence):
    unit = unit_denying(sentence)
    case.assertFalse(mod11.validate_headline_unit(unit))
    with case.assertRaises(ValueError):
        mod11.quote_headline_unit(unit)


class TestR13017PublicationIterationEquality(unittest.TestCase):

    def test_iteration_reports_all_fifteen(self):
        record = passed_record()
        record["verdicts"] = IterationReportDict(
            {"T-01": "passed"}, mod11.RETIREMENT_CHECKS)
        self.assertFalse(mod11.validate_publication_record(record))
        unit = {"publication_record": record}
        self.assertFalse(mod11.unit_is_publishable(unit))

    def test_iteration_reports_one_mirror(self):
        record = passed_record()
        record["verdicts"] = IterationReportDict(
            dict(record["verdicts"]), ["T-01"])
        self.assertTrue(mod11.validate_publication_record(record))
        unit = {"publication_record": record}
        self.assertTrue(mod11.unit_is_publishable(unit))

    def test_equality_lying_failure_entry(self):
        verdicts = {check: "passed"
                    for check in mod11.RETIREMENT_CHECKS}
        verdicts["T-04"] = "failed"
        record = passed_record()
        record["verdicts"] = verdicts
        record["failures_recorded"] = [EqualityLiar()]
        self.assertFalse(mod11.validate_publication_record(record))

    def test_equality_lying_verdict_values(self):
        liar = EqualityLiar()
        record = passed_record()
        record["verdicts"] = {
            check: liar for check in mod11.RETIREMENT_CHECKS}
        record["failures_recorded"] = list(mod11.RETIREMENT_CHECKS)
        self.assertFalse(mod11.validate_publication_record(record))

    def test_publication_controls(self):
        self.assertTrue(mod11.validate_publication_record(
            genuine_record()))
        self.assertTrue(mod11.validate_publication_record(
            passed_record()))
        record = passed_record()
        record["verdicts"] = {"T-01": "passed"}
        self.assertFalse(mod11.validate_publication_record(record))
        record = passed_record()
        record["verdicts"]["T-03"] = "failed"
        self.assertFalse(mod11.validate_publication_record(record))


class TestR13041PublicationVerdictValues(unittest.TestCase):

    def test_all_bogus_verdicts(self):
        record = passed_record()
        record["verdicts"] = {
            check: "bogus" for check in mod11.RETIREMENT_CHECKS}
        self.assertFalse(mod11.validate_publication_record(record))
        unit = {"publication_record": record}
        self.assertFalse(mod11.unit_is_publishable(unit))

    def test_half_unknown_verdicts(self):
        record = passed_record()
        checks = list(mod11.RETIREMENT_CHECKS)
        for check in checks[:7]:
            record["verdicts"][check] = "unknown"
        self.assertFalse(mod11.validate_publication_record(record))

    def test_failed_with_trailing_space(self):
        record = passed_record()
        record["verdicts"]["T-02"] = "failed "
        self.assertFalse(mod11.validate_publication_record(record))

    def test_genuine_record_control(self):
        self.assertTrue(mod11.validate_publication_record(
            genuine_record()))
        record = genuine_record()
        self.assertTrue(mod11.unit_is_publishable(
            {"publication_record": record}))


class TestR13018ParleyOrdinalBeforeName(unittest.TestCase):

    def test_ordinal_fused_before_question_and_name(self):
        assert_grounds(self, {
            "firstquestionparley": {"1"},
            "secondquestionparley": {"2"},
            "fifthquestionparley": {"5"},
            "1stquestionparley": {"1"},
            "2ndquestionparley": {"2"},
            "5thquestionparley": {"5"},
        })

    def test_name_fused_before_ordinal_and_question(self):
        assert_grounds(self, {
            "parleyfirstquestion": {"1"},
            "parleysecondquestion": {"2"},
            "parleyfifthquestion": {"5"},
        })

    def test_ordinal_fused_before_name_question_after(self):
        assert_grounds(self, {
            "firstparleyquestion": {"1"},
            "secondparleyquestion": {"2"},
            "fifthparleyquestion": {"5"},
            "firstparleyquestions": {"1"},
            "fifthparleyquestions": {"5"},
            "1stparleyquestion": {"1"},
            "2ndparleyquestion": {"2"},
            "5thparleyquestion": {"5"},
        })

    def test_plural_name_fused_to_q_and_number(self):
        assert_grounds(self, {
            "parleysq1": {"1"},
            "parleysq2": {"2"},
            "parleysq5": {"5"},
        })

    def test_fused_name_question_beside_spaced_number(self):
        assert_grounds(self, {
            "parleyquestion 1": {"1"},
            "parleyquestion 2": {"2"},
            "parleyquestion 5": {"5"},
        })

    def test_split_joining_forms(self):
        assert_grounds(self, {
            "firstparley q": {"1"},
            "first parleyq": {"1"},
            "2ndparley q": {"2"},
            "5thparley q": {"5"},
            "fifth parleyq": {"5"},
            "firstparley question": {"1"},
            "first parleyquestion": {"1"},
            "secondparley question": {"2"},
        })

    def test_grounds_controls(self):
        assert_grounds(self, {
            "firstparleyq": {"1"},
            "secondqparley": {"2"},
            "first parley q": {"1"},
            "parleyquestionsecond": {"2"},
            "the result stands on its own": set(),
        })

    def test_public_gate_next_ring_forms(self):
        for sentence in (
                "the result depends on secondquestionparley",
                "the result depends on parleysecondquestion",
                "the result depends on secondparleyquestion",
                "the result depends on parleysq2",
                "the result depends on parleyquestion 2",
                "the result depends on firstparley q",
                "the result depends on firstparleyquestion"):
            with self.subTest(sentence=sentence):
                assert_unit_refused(self, sentence)

    def test_public_gate_cured_control(self):
        assert_unit_refused(
            self, "the result depends on secondqparley")


class TestR13019StemNextRing(unittest.TestCase):

    def test_s_irregular_forms(self):
        assert_none_readable(self, [
            "leafs", "lifes", "halfs", "shelfs",
            "childrens", "datas"])

    def test_ed_irregular_forms(self):
        assert_none_readable(self, [
            "catched", "thinked", "speaked", "stealed",
            "writed", "rided", "growed", "knowed", "throwed",
            "seeked", "selled", "telled", "falled", "taked",
            "maked", "gived", "breaked", "choosed", "drived",
            "finded", "sayed", "feeled", "keeped", "sleeped",
            "leaved", "rised", "sitted", "winned", "holded",
            "standed", "losed", "drawed", "leaded"])

    def test_stated_bound_compound_forms(self):
        # Bound, stated in the builder paper: forgeted and
        # informations stand refused at their own stem limbs,
        # and each still returns True through the closed
        # compound reading alone, forgeted as for plus geted on
        # the base get and informations as in plus formations,
        # neither base nor split standing named in any record,
        # so no refusal for those paths stands on decided
        # ground and none is invented here.
        self.assertEqual(mod11._readable_stem("forgeted"), [])
        self.assertEqual(mod11._readable_stem("informations"),
                         [])
        self.assertTrue(mod11._is_readable_word("forgeted"))
        self.assertTrue(mod11._is_readable_word("informations"))

    def test_er_est_irregular_forms(self):
        assert_none_readable(self, ["gooder", "goodest"])

    def test_stem_controls(self):
        assert_none_readable(self, [
            "wifes", "mouses", "foots", "wented", "teached",
            "childs", "sheeps"])
        assert_all_readable(self, [
            "leaves", "lives", "halves", "shelves", "children",
            "wives", "houses"])

    def test_readout_next_ring_rules(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("catched thinked growed")))
        self.assertFalse(mod11.validate_readout(
            readout_for("leafs lifes halfs")))
        self.assertFalse(mod11.validate_readout(
            readout_for("taked maked gived")))
        self.assertFalse(mod11.validate_readout(
            readout_for("childrens datas informations")))
        self.assertTrue(mod11.validate_readout(
            readout_for("houses chairs tables")))


class TestR13020AbleDerivation(unittest.TestCase):

    def test_able_words_readable(self):
        assert_all_readable(self, [
            "breakable", "washable", "portable", "movable",
            "lovable", "usable", "likable", "sizable"])

    def test_able_stems_land_on_lexicon_bases(self):
        bases = {
            "breakable": "break", "washable": "wash",
            "portable": "port", "movable": "move",
            "lovable": "love", "usable": "use",
            "likable": "like", "sizable": "size",
        }
        for word, base in bases.items():
            with self.subTest(word=word):
                self.assertIn(base, mod11._READABLE_LEXICON)
                self.assertIn(base, mod11._readable_stem(word))

    def test_readout_able_rule(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("breakable washable portable")))
        self.assertTrue(mod11.validate_readout(
            readout_for("sampled points only")))
        self.assertFalse(mod11.validate_readout(
            readout_for("zxqwv ukjhp mlqrs")))


class TestR13040HeadlineBuilderCopy(unittest.TestCase):

    def test_copy_protocol_fabrication(self):
        values = compliant_unit()
        field = mod11.HEADLINE_UNIT_FIELDS[0]
        liar = CopyLiar()
        values[field] = liar
        unit = mod11.make_headline_unit(values)
        self.assertIs(unit[field], liar)
        self.assertNotEqual(unit[field], "LIED")

    def test_copy_protocol_raising(self):
        values = compliant_unit()
        field = mod11.HEADLINE_UNIT_FIELDS[0]
        raiser = CopyRaiser()
        values[field] = raiser
        unit = mod11.make_headline_unit(values)
        self.assertIs(unit[field], raiser)

    def test_copy_container_parts_copied_apart(self):
        values = compliant_unit()
        unit = mod11.make_headline_unit(values)
        self.assertEqual(unit, values)
        self.assertIsNot(
            unit["holding_region"], values["holding_region"])
        self.assertIsNot(
            unit["holding_region"]["sampled_points"],
            values["holding_region"]["sampled_points"])


class TestR13055HeadlineBuilderWording(unittest.TestCase):

    def test_list_handed_full_form(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit(["not", "a", "mapping"])
        self.assertEqual(
            str(caught.exception),
            "make_headline_unit stands refused: the headline "
            "unit stands in no record form, a headline unit "
            "stands as a field mapping, and no unit stands built")

    def test_extra_field_full_form(self):
        values = compliant_unit()
        values["zzz_extra"] = "extra"
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit(values)
        self.assertEqual(
            str(caught.exception),
            "make_headline_unit stands refused: fields beyond "
            "the closed unit: zzz_extra, and no unit stands built")

    def test_missing_first_field_full_form(self):
        values = compliant_unit()
        del values[mod11.HEADLINE_UNIT_FIELDS[0]]
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit(values)
        self.assertEqual(
            str(caught.exception),
            "make_headline_unit stands refused: headline unit "
            "field absent: headline_unit_identifier_and_issue_date"
            ", and no unit stands built")


if __name__ == "__main__":
    unittest.main()

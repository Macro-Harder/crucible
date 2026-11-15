"""Fix wave 14 pins, Builder 5: rows R14-031 to R14-038.

MOD-11 Parley grounds next ring, stem ed and er and est next
ring, es and ies refusal, ible and ability derivations,
publication failures handed iteration and truthiness limbs,
headline builder handed mapping readings, and the quote
refusal content fault sentences.
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


class TestR14031ParleyNextRing(unittest.TestCase):
    def test_reversed_joined_ordinal_forms(self):
        for text in ("qparleyfirst", "qparleysecond", "qparleyfifth",
                     "questionparleyfirst", "questionsparleyfirst"):
            with self.subTest(text=text):
                self.assertTrue(mod11._parley_grounds_stated(text))

    def test_plural_fused_spelled_and_questioned(self):
        for text in ("parleysqone", "parleysquestions1",
                     "parleysquestion1", "parleysquestionone",
                     "parleysquestions5"):
            with self.subTest(text=text):
                self.assertTrue(mod11._parley_grounds_stated(text))

    def test_plural_spaced_ordinal_and_q(self):
        for text in ("first parleys question", "parleys question first",
                     "first parleys q", "firstparleysquestion",
                     "firstparleysq", "fifth parleys questions",
                     "second parleys q"):
            with self.subTest(text=text):
                self.assertTrue(mod11._parley_grounds_stated(text))

    def test_ordinal_after_qparley_token(self):
        for text in ("second qparley", "qparleysecond"):
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), {"2"})

    def test_ordinal_at_distance_with_q_limb(self):
        for text in ("first alpha beta gamma delta parley q",
                     "first alpha beta gamma parley q"):
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), {"1"})

    def test_split_joins_name_first_and_question_middle(self):
        for text in ("parleyfirst question", "parley firstquestion",
                     "parleysecond question", "parley fifthquestion",
                     "first questionparley", "firstquestion parley",
                     "second questionparley", "parleyfirst q",
                     "parleysecond q"):
            with self.subTest(text=text):
                self.assertTrue(mod11._parley_grounds_stated(text))

    def test_denying_units_refused(self):
        for sentence in (
                "the result depends on qparleyfirst",
                "the result depends on parleysqone",
                "the result depends on first parleys question",
                "the result depends on parleyfirst question",
                "the result depends on first questionparley",
                "the result depends on second qparley"):
            with self.subTest(sentence=sentence):
                unit = unit_denying(sentence)
                self.assertFalse(mod11.validate_headline_unit(unit))
                with self.assertRaises(ValueError):
                    mod11.quote_headline_unit(unit)


class TestR14032StemNextRing(unittest.TestCase):
    def test_ed_next_ring_refused(self):
        words = [
            "hitted", "putted", "setted", "shutted", "hurted",
            "builded", "sended", "meeted", "readed", "fighted",
            "dealed", "getted", "meaned", "shaked", "shooted",
            "spended", "sticked", "striked", "swinged", "weared",
            "understanded", "spreaded", "splitted", "springed",
            "sweared", "arised", "becomed", "begined", "beginned",
            "comed", "heared", "undergoed", "withdrawed", "beared",
            "inputed", "outputed", "letted", "spinned",
            "tooked", "gaved", "maded", "tolded", "knewed",
            "helded", "hearded", "lefted", "solded", "thoughted",
            "leded", "shoted", "builted", "reraned",
        ]
        for word in words:
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_er_est_next_ring_refused(self):
        for word in ("mucher", "muchest", "manyer", "wronger",
                     "wrongest", "realer", "realest"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_readout_refuses_next_ring_rules(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("hitted hurted builded")))
        self.assertFalse(mod11.validate_readout(
            readout_for("mucher wronger realer")))

    def test_cured_controls_hold(self):
        for word in ("catched", "thinked", "gooder", "goodest"):
            self.assertFalse(mod11._is_readable_word(word), word)
        self.assertTrue(mod11.validate_readout(
            readout_for("houses chairs tables")))


class TestR14033EsIesRefusal(unittest.TestCase):
    def test_es_forms_refused(self):
        for word in ("childes", "womanes", "sheepes",
                     "wifees", "mousees", "footes", "leafes",
                     "lifees", "halfes", "shelfes", "childrenes",
                     "dataes"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_es_barred_base_not_yielded_as_stem(self):
        # toothes and informationes stand at the stated bound:
        # no stem limb yields the barred base after the cure,
        # and each reads only through the closed compound
        # reading, as the R13-019 bound forms do. No record
        # bars those compound splits.
        self.assertNotIn("tooth", mod11._readable_stem("toothes"))
        self.assertNotIn(
            "information", mod11._readable_stem("informationes"))

    def test_ies_forms_refused(self):
        for word in ("sheepies", "leafies", "childies", "dataies"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word), word)

    def test_readout_refuses_es_ies_rules(self):
        self.assertFalse(mod11.validate_readout(
            readout_for("childes sheepes dataes")))
        self.assertFalse(mod11.validate_readout(
            readout_for("sheepies leafies childies")))

    def test_s_controls_hold(self):
        for word in ("childs", "sheeps", "datas"):
            self.assertFalse(mod11._is_readable_word(word), word)
        for word in ("classes", "houses"):
            self.assertTrue(mod11._is_readable_word(word), word)


class TestR14034IbleAbility(unittest.TestCase):
    def test_ible_forms_readable(self):
        for word in ("convertible", "accessible"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)

    def test_ability_forms_readable(self):
        for word in ("usability", "breakability", "washability"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word), word)

    def test_readout_accepts_lawful_rules(self):
        self.assertTrue(mod11.validate_readout(
            readout_for("convertible accessible usable")))
        self.assertTrue(mod11.validate_readout(
            readout_for("usability breakability washability")))


class IterYieldsFailure:
    """Stores no failure; its iteration yields one name."""

    def __iter__(self):
        return iter(["T-02"])


class LyingFailuresList(list):
    """Stores a bogus entry; iterates as the failed check."""

    def __iter__(self):
        return iter(["T-02"])


class TestR14035PublicationFailuresHandedIteration(unittest.TestCase):
    def test_plain_object_iteration_fabrication_refused(self):
        record = publication_record(failed=("T-02",))
        record["failures_recorded"] = IterYieldsFailure()
        self.assertFalse(mod11.validate_publication_record(record))
        self.assertFalse(mod11.unit_is_publishable(
            {"publication_record": record}))

    def test_mapping_iteration_fabrication_refused(self):
        record = publication_record(failed=("T-02",))
        record["failures_recorded"] = {"T-02": "arbitrary"}
        self.assertFalse(mod11.validate_publication_record(record))
        self.assertFalse(mod11.unit_is_publishable(
            {"publication_record": record}))

    def test_list_subclass_iteration_fabrication_refused(self):
        record = publication_record(failed=("T-02",))
        record["failures_recorded"] = LyingFailuresList(["bogus entry"])
        self.assertFalse(mod11.validate_publication_record(record))
        self.assertFalse(mod11.unit_is_publishable(
            {"publication_record": record}))

    def test_list_subclass_mirror_judged_on_stored_entry(self):
        record = publication_record(failed=("T-02",))

        class MirrorList(list):
            def __iter__(self):
                return iter(["bogus entry"])

        record["failures_recorded"] = MirrorList(["T-02"])
        self.assertTrue(mod11.validate_publication_record(record))

    def test_set_form_genuine_record_validates(self):
        record = publication_record(failed=("T-02", "T-05", "T-11"))
        record["failures_recorded"] = {"T-02", "T-05", "T-11"}
        self.assertTrue(mod11.validate_publication_record(record))
        self.assertTrue(mod11.unit_is_publishable(
            {"publication_record": record}))

    def test_plain_controls_hold(self):
        self.assertTrue(mod11.validate_publication_record(
            publication_record()))
        self.assertTrue(mod11.validate_publication_record(
            publication_record(failed=("T-02",))))
        record = publication_record()
        record["failures_recorded"] = "T-02"
        self.assertFalse(mod11.validate_publication_record(record))


class RaisingTruth:
    def __bool__(self):
        raise RuntimeError("truth reading raises")


class TestR14036PublicationTruthiness(unittest.TestCase):
    def test_integer_run_and_bare_object_version_refused(self):
        record = publication_record()
        record["test_run"] = 12345
        record["version"] = object()
        self.assertFalse(mod11.validate_publication_record(record))
        self.assertFalse(mod11.unit_is_publishable(
            {"publication_record": record}))

    def test_raising_truth_reading_returns_false(self):
        record = publication_record()
        record["test_run"] = RaisingTruth()
        self.assertFalse(mod11.validate_publication_record(record))
        self.assertFalse(mod11.unit_is_publishable(
            {"publication_record": record}))


class LyingMapping(dict):
    """Stores a compliant unit plus an extra field; its own
    iteration, contains, and getitem readings report otherwise."""

    def __iter__(self):
        return iter(mod11.HEADLINE_UNIT_FIELDS)

    def __contains__(self, key):
        return key in mod11.HEADLINE_UNIT_FIELDS

    def __getitem__(self, key):
        return CLAIM_TEXT


class TestR14037HeadlineBuilderHandedMapping(unittest.TestCase):
    def test_lying_mapping_refused(self):
        values = compliant_unit()
        values["secret_extra"] = "extra"
        with self.assertRaises(ValueError):
            mod11.make_headline_unit(LyingMapping(values))

    def test_lying_getitem_none_field_refused(self):
        class NoneLying(dict):
            def __getitem__(self, key):
                if key == "witness_block":
                    return "fabricated witness"
                return dict.__getitem__(self, key)

        values = compliant_unit()
        values["witness_block"] = None
        with self.assertRaises(ValueError):
            mod11.make_headline_unit(NoneLying(values))

    def test_plain_controls_hold(self):
        unit = mod11.make_headline_unit(compliant_unit())
        self.assertEqual(tuple(unit), mod11.HEADLINE_UNIT_FIELDS)
        values = compliant_unit()
        values["secret_extra"] = "extra"
        with self.assertRaises(ValueError):
            mod11.make_headline_unit(values)


def refusal_text(unit):
    try:
        mod11.quote_headline_unit(unit)
    except ValueError as error:
        return str(error)
    raise AssertionError("unit was quoted")


class TestR14038QuoteContentFaultSentences(unittest.TestCase):
    def test_three_content_faults_draw_three_named_refusals(self):
        overclaim = compliant_unit()
        overclaim["claim_sentence"] = (
            CLAIM_TEXT + " The result holds everywhere at all points.")
        empty_witness = compliant_unit()
        empty_witness["witness_block"] = ""
        no_scope = compliant_unit()
        no_scope["claim_sentence"] = (
            "The result holds for the sampled points in this unit.")
        texts = [
            refusal_text(overclaim),
            refusal_text(empty_witness),
            refusal_text(no_scope),
        ]
        self.assertEqual(len(set(texts)), 3)
        self.assertIn("claim_sentence", texts[0])
        self.assertIn("witness_block", texts[1])
        self.assertIn("claim_sentence", texts[2])

    def test_structural_refusal_still_named(self):
        unit = compliant_unit()
        unit["secret_extra"] = "extra"
        self.assertIn("secret_extra", refusal_text(unit))


if __name__ == "__main__":
    unittest.main()

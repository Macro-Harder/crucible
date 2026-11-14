# Step 15 rerun Round 10 fix wave 10 tests, Builder 7.
# Rows R10-024 at MOD-09, R10-042 to R10-048 at MOD-11, and the
# records pin for R10-049 at MOD-11.
# Plain simulated values only.
import unittest

import crucible.mod09 as mod09
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


def lawful_search_record():
    carriage = mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])
    return mod09.build_search_record(
        carriage, points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=[0, 5])


class LyingRecord(dict):
    """A dict subclass storing one mapping and reporting another
    through its own get, contains, and item readings."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)

    def __contains__(self, key):
        return dict.__contains__(self._reported, key)

    def __getitem__(self, key):
        return dict.__getitem__(self._reported, key)


class TestR10024ValidateSearchRecord(unittest.TestCase):
    def test_plain_controls(self):
        self.assertTrue(mod09.validate_search_record(
            lawful_search_record()))
        self.assertFalse(mod09.validate_search_record({}))

    def test_lying_record_storing_nothing_is_not_certified(self):
        lawful = lawful_search_record()
        lying = LyingRecord({}, lawful)
        self.assertEqual(dict.__len__(lying), 0)
        self.assertFalse(mod09.validate_search_record(lying))

    def test_lying_record_storing_lawful_record_validates(self):
        lawful = lawful_search_record()
        reported = {
            "run_record": {},
            "search_record": {},
            "bond_parameter_search": {},
            "mid_run_strategies": ["introduced"],
            "case_uses": [],
        }
        lying = LyingRecord(lawful, reported)
        self.assertTrue(mod09.validate_search_record(lying))

    def test_lying_search_dict_contains_and_item_readings(self):
        record = lawful_search_record()
        lying_search = LyingRecord(
            {}, {field.replace(" ", "_"): "reported value"
                 for field in mod09.SEARCH_RECORD_FIELDS})
        record = dict(record)
        record["search_record"] = lying_search
        self.assertFalse(mod09.validate_search_record(record))


class TestR10024HostileKinds(unittest.TestCase):
    def test_plain_controls(self):
        family = {kind: 5 for kind in mod09.HOSTILE_INPUT_KINDS}
        record = {"hostile_kind_runs": {
            kind: 9 for kind in mod09.HOSTILE_INPUT_KINDS}}
        covered = mod09.search_record_covers_hostile_kinds(
            record, family)
        self.assertTrue(all(covered.values()))
        low = {"hostile_kind_runs": {
            kind: 3 for kind in mod09.HOSTILE_INPUT_KINDS}}
        covered = mod09.search_record_covers_hostile_kinds(
            low, family)
        self.assertFalse(any(covered.values()))
        covered = mod09.search_record_covers_hostile_kinds(
            {}, family)
        self.assertFalse(any(covered.values()))

    def test_lying_record_storing_nothing_covers_no_kind(self):
        family = {kind: 5 for kind in mod09.HOSTILE_INPUT_KINDS}
        lying = LyingRecord({}, {"hostile_kind_runs": {
            kind: 9 for kind in mod09.HOSTILE_INPUT_KINDS}})
        covered = mod09.search_record_covers_hostile_kinds(
            lying, family)
        self.assertEqual(
            covered,
            {kind: False for kind in mod09.HOSTILE_INPUT_KINDS})

    def test_lying_record_storing_runs_covers_every_kind(self):
        family = {kind: 5 for kind in mod09.HOSTILE_INPUT_KINDS}
        stored = {"hostile_kind_runs": {
            kind: 9 for kind in mod09.HOSTILE_INPUT_KINDS}}
        lying = LyingRecord(stored, {})
        covered = mod09.search_record_covers_hostile_kinds(
            lying, family)
        self.assertTrue(all(covered.values()))

    def test_lying_family_record_supplies_no_fixed_magnitude(self):
        record = {"hostile_kind_runs": {
            kind: 9 for kind in mod09.HOSTILE_INPUT_KINDS}}
        lying_family = LyingRecord(
            {}, {kind: 5 for kind in mod09.HOSTILE_INPUT_KINDS})
        covered = mod09.search_record_covers_hostile_kinds(
            record, lying_family)
        self.assertFalse(any(covered.values()))


class TestR10042YDoubledUndoing(unittest.TestCase):
    def test_doubled_y_forms(self):
        for word in ("sunny", "doggy", "piggy", "froggy", "catty",
                     "skinny", "spotty", "tinny", "leggy", "starry",
                     "runny", "snappy"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_in_doubled_y_forms_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "sunny share", "sunny doggy starry")))


class TestR10043ErDoubledUndoing(unittest.TestCase):
    def test_doubled_comparatives(self):
        for word in ("bigger", "hotter", "sadder", "thinner",
                     "wetter", "redder", "fitter", "flatter"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_est_siblings_control(self):
        for word in ("biggest", "hottest", "saddest", "thinnest",
                     "wettest", "reddest", "fittest", "flattest"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_readout_in_doubled_comparatives_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "bigger share", "bigger hotter thinner")))


class TestR10044CompoundReading(unittest.TestCase):
    def test_derived_part_beside_plain_part(self):
        for word in ("coldestnight", "biggestdog", "runningwater",
                     "stoppedclock", "plannedtrip", "cloudyday"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_plain_part_beside_derived_part(self):
        for word in ("waterrunning", "nightcoldest", "suncoldest",
                     "housedogs", "swimmingpool"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_both_parts_derived(self):
        for word in ("coldestrunning", "runningcoldest",
                     "cloudystormy", "stoppedplanned"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_derivation_carried_on_a_whole_compound(self):
        for word in ("notebooks", "butterflies", "doghouses",
                     "houseboats", "sunlights", "daylights",
                     "notebooked", "birdsongs", "goldfishes",
                     "clockworks", "spaceships"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_compound_part_itself_a_compound(self):
        self.assertTrue(mod11._is_readable_word("bluebirdsong"))

    def test_readout_in_compound_forms_passes(self):
        self.assertTrue(mod11.validate_readout(readout_for(
            "coldestnight share",
            "coldestnight runningwater doghouses")))


class TestR10045YToIStemChange(unittest.TestCase):
    def test_er_forms_on_y_final_bases(self):
        for word in ("happier", "angrier", "healthier", "easier",
                     "earlier", "busier"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_est_forms_on_y_final_bases(self):
        for word in ("happiest", "angriest", "healthiest",
                     "easiest", "earliest", "busiest"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_ly_forms_on_y_final_bases(self):
        for word in ("angrily", "hungrily", "readily",
                     "healthily"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_ed_forms_on_y_final_bases(self):
        for word in ("carried", "studied", "copied", "replied",
                     "varied", "identified", "qualified",
                     "satisfied", "supplied", "relied"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_ies_and_ing_controls(self):
        self.assertTrue(mod11._is_readable_word("parties"))
        for word in ("carrying", "studying", "copying",
                     "replying"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))


class TestR10046NumberSpacedBeforeQParley(unittest.TestCase):
    def test_number_spaced_before_qparley_token(self):
        cases = {
            "two qparley": {"2"},
            "one qparley": {"1"},
            "five qparley": {"5"},
            "1 qparley": {"1"},
            "5 qparley": {"5"},
            "two-qparley": {"2"},
            "one-qparley": {"1"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_parleyq_token_with_spaced_number(self):
        cases = {
            "parleyq 2": {"2"},
            "parleyq two": {"2"},
            "one parleyq": {"1"},
            "parleyq one": {"1"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_composed_with_reversed_joined_forms(self):
        cases = {
            "q1parley and on two qparley": {"1", "2"},
            "two qparley and on question1parley": {"1", "2"},
            "the claim depends on two qparley and on "
            "question 5parley": {"2", "5"},
            "the claim depends on one qparley and on "
            "parley5 q": {"1", "5"},
            "the claim depends on question 2parley and on "
            "five qparley": {"2", "5"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_denied_qparley_ground_unit_is_refused(self):
        unit = unit_with_claim_extra(
            "The claim depends on two qparley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11._field10_matches_grounds(unit))
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR10047ParleyJoinedWithSpacedLimb(unittest.TestCase):
    def test_joined_parley_forms_with_spaced_limb(self):
        cases = {
            "question 2parley": {"2"},
            "questions 2parley": {"2"},
            "q 2parley": {"2"},
            "2parley question": {"2"},
            "question twoparley": {"2"},
            "questions twoparley": {"2"},
            "two questionsparley": {"2"},
            "question fiveparley": {"5"},
            "question parley2": {"2"},
            "parley1 q": {"1"},
            "parleyone q": {"1"},
            "parleyfive q": {"5"},
            "parley2 q": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_mirror_splits_control(self):
        cases = {
            "question2 parley": {"2"},
            "twoquestions parley": {"2"},
            "questionfive parley": {"5"},
            "parley 1q": {"1"},
            "parley oneq": {"1"},
            "parley fiveq": {"5"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_bare_joined_tokens_state_no_ground(self):
        for text in ("2parley", "fiveparley", "parley1",
                     "parleyone", "two parley", "parley 1"):
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), set())

    def test_denied_joined_ground_unit_is_refused(self):
        for sentence in ("The claim depends on question "
                         "2parley.",
                         "The claim depends on parley1 q.",
                         "The claim depends on question "
                         "twoparley."):
            unit = unit_with_claim_extra(
                sentence, field10=FIELD10_NO_DEPENDENCE_TEXT)
            with self.subTest(sentence=sentence):
                self.assertFalse(
                    mod11._field10_matches_grounds(unit))
                self.assertFalse(
                    mod11.validate_headline_unit(unit))


class TestR10048NumberBeforeQGuard(unittest.TestCase):
    def test_second_ground_read_beside_reversed_joined_form(self):
        cases = {
            "question2parley one q": {"1", "2"},
            "question5parley two q": {"2", "5"},
            "question2parley and 1q": {"1", "2"},
            "question2parley and q1": {"1", "2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)

    def test_standalone_parley_composition_control(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "question2parley and one q parley"), {"1", "2"})
        self.assertEqual(mod11._parley_grounds_stated(
            "one q parley"), {"1"})
        self.assertEqual(mod11._parley_grounds_stated(
            "question2parley"), {"2"})


class TestR10049RecordsPin(unittest.TestCase):
    def test_the_twoquestions_of_parley_direct(self):
        self.assertEqual(mod11._parley_grounds_stated(
            "the twoquestions of parley"), {"2"})

    def test_the_twoquestions_of_parley_denied_unit_refused(self):
        unit = unit_with_claim_extra(
            "The claim depends on the twoquestions of Parley.",
            field10=FIELD10_NO_DEPENDENCE_TEXT)
        self.assertFalse(mod11._field10_matches_grounds(unit))
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestControlsKept(unittest.TestCase):
    def test_invented_strings_are_no_word(self):
        for word in ("blorple", "snizzle", "frumious"):
            with self.subTest(word=word):
                self.assertFalse(mod11._is_readable_word(word))

    def test_plain_and_cured_lexicon_controls(self):
        for word in ("cloudy", "peachy", "biggest", "coldest",
                     "running", "bluebird", "butterfly",
                     "notebook", "doghouse", "sunlight", "happy",
                     "carry"):
            with self.subTest(word=word):
                self.assertTrue(mod11._is_readable_word(word))

    def test_no_ground_forms_stay_empty(self):
        for text in ("qparley", "parley question", "parley q",
                     "two parley", "parley 1", "one q", "1q"):
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), set())

    def test_cured_ground_controls(self):
        cases = {
            "twoq parley": {"2"},
            "1q of parley": {"1"},
            "twoqparley": {"2"},
            "1qparley": {"1"},
            "parley q 2": {"2"},
            "parley 2q": {"2"},
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(
                    mod11._parley_grounds_stated(text), expected)


if __name__ == "__main__":
    unittest.main()

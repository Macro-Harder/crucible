"""Pins for Round 14 rows R14-058 to R14-063 and R14-065.

MOD-09 search, readout, and catalogue forms, Builder 8 of fix
wave 14. Each test pins the defect its row states with the
proving acts the source papers used (Blue 4 Findings 1 to 5,
Yellow 1 Finding Y1-7, Orange 2 Findings 1 and 6, and Purple 4
Finding 1), beside the plain controls those papers ran.
"""
import unittest

from crucible import mod09


def _carriage(strategies=("conditional briber",)):
    return mod09.run_record_carriage(
        list(strategies), 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(outcome="no failure", swept_values=(0, 5), **kwargs):
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": outcome}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=swept_values, **kwargs)


def _class_record(members):
    record = _record()
    record["run_record"]["strategy_class"] = list(members)
    record["run_record"]["strategies_exercised"] = list(members)
    return record


def _dyn_bytes():
    return bytes([97, 108, 112, 104, 97])


class IterLieList(list):
    """Stores one set of items, iterates as another."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)


class LenZeroList(list):
    """Stores items, reports a length of zero."""

    def __len__(self):
        return 0


class TestR14058BufferMemberEquality(unittest.TestCase):

    def test_helpers_agree_on_distinct_equal_buffers(self):
        pairs = [
            (_dyn_bytes(), _dyn_bytes()),
            (bytearray(b"alpha"), bytearray(b"alpha")),
            (memoryview(b"alpha"), memoryview(b"alpha")),
            (_dyn_bytes(), bytearray(b"alpha")),
            (bytearray(b"alpha"), memoryview(b"alpha")),
        ]
        for first, second in pairs:
            self.assertTrue(mod09._stored_eq(first, second),
                            repr((first, second)))
            self.assertTrue(mod09._stored_match(first, second),
                            repr((first, second)))

    def test_helpers_agree_on_distinct_buffer_content(self):
        self.assertFalse(mod09._stored_match(_dyn_bytes(), b"beta"))
        self.assertFalse(mod09._stored_eq(_dyn_bytes(), b"beta"))

    def test_record_validates_against_apart_built_bytes_class(self):
        record = _class_record([_dyn_bytes()])
        self.assertTrue(
            mod09.validate_search_record(record, [_dyn_bytes()]))
        ok, failures = mod09.validate_search_record_with_reason(
            record, [_dyn_bytes()])
        self.assertTrue(ok)
        self.assertEqual(failures, [])

    def test_record_validates_against_cross_buffer_fixed_class(self):
        record = _class_record([bytearray(b"alpha")])
        self.assertTrue(mod09.validate_search_record(
            record, [_dyn_bytes()]))
        record = _class_record([memoryview(b"alpha")])
        self.assertTrue(mod09.validate_search_record(
            record, [bytearray(b"alpha")]))

    def test_record_refused_against_other_buffer_class(self):
        record = _class_record([_dyn_bytes()])
        self.assertFalse(
            mod09.validate_search_record(record, [b"beta"]))

    def test_carriage_accepts_apart_built_buffer_member(self):
        carriage = mod09.run_record_carriage(
            [_dyn_bytes()], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1",
            strategies=[_dyn_bytes()])
        self.assertEqual(len(carriage["strategies_exercised"]), 1)
        carriage = mod09.run_record_carriage(
            [bytearray(b"alpha")], 6, "catalogue version 1",
            "ladder definition pointer", "ladder version 1",
            strategies=[bytearray(b"alpha")])
        self.assertEqual(len(carriage["strategies_exercised"]), 1)

    def test_same_object_and_text_controls(self):
        shared = _dyn_bytes()
        record = _class_record([shared])
        self.assertTrue(
            mod09.validate_search_record(record, [shared]))
        record = _class_record(["alpha"])
        self.assertTrue(
            mod09.validate_search_record(record, ["alpha"]))
        self.assertFalse(
            mod09.validate_search_record(record, ["beta"]))


class TestR14059MidRunStrategiesStoredReading(unittest.TestCase):

    def test_iteration_lie_strategies_not_dropped(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(mid_run_strategies=IterLieList(["alpha"], []))

    def test_zero_length_reading_strategies_not_dropped(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(mid_run_strategies=LenZeroList(["alpha"]))

    def test_plain_mid_run_strategies_still_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(mid_run_strategies=["alpha"])

    def test_no_mid_run_strategies_controls(self):
        for handed in (None, []):
            record = _record(mid_run_strategies=handed)
            self.assertEqual(record["mid_run_strategies"], [])
            self.assertTrue(mod09.validate_search_record(record))


class TestR14060ReadoutWordingNonTextForms(unittest.TestCase):

    def test_bytes_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording=b"economically secure")

    def test_bytearray_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording=bytearray(b"economic security"))

    def test_list_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording=["economically secure"])

    def test_tuple_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording=("established claim",))

    def test_list_of_bytes_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording=[b"economic security"])

    def test_plain_and_non_claim_controls(self):
        unit = mod09.readout(
            _record(), wording="readout wording for the search")
        self.assertEqual(unit["wording"],
                         "readout wording for the search")
        unit = mod09.readout(_record(), wording=b"plain wording")
        self.assertEqual(unit["wording"], b"plain wording")
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording="the system stands "
                                   "economically secure")


class TestR14061ReadoutFailureBytesOutcome(unittest.TestCase):

    def test_bytes_outcome_withholds_no_failure_sentence(self):
        record = _record(outcome=b"failure found")
        self.assertTrue(mod09.validate_search_record(record))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_bytearray_outcome_withholds_sentence(self):
        record = _record(outcome=bytearray(b"failure found"))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_text_controls(self):
        record = _record(outcome="failure found")
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)
        record = _record(outcome="no failure")
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)


class TestR14062ReadoutNoOutcomeNoSentence(unittest.TestCase):

    def test_empty_outcomes_record_gets_no_sentence(self):
        record = _record()
        record["search_record"]["per_point_outcome"] = []
        self.assertFalse(mod09.validate_search_record(record))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_deleted_search_limb_gets_no_sentence(self):
        record = _record()
        del record["search_record"]
        self.assertFalse(mod09.validate_search_record(record))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_bare_carriage_gets_no_sentence(self):
        carriage = _record()["run_record"]
        unit = mod09.readout(carriage, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_single_dict_outcome_failure_seen(self):
        record = _record()
        record["search_record"]["per_point_outcome"] = {
            "point": "point one", "outcome": "failure found"}
        self.assertTrue(mod09.validate_search_record(record))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_clean_record_control_keeps_sentence(self):
        record = _record(outcome="no failure")
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)


class TestR14063CaseUseNoRecordForm(unittest.TestCase):

    def test_integer_case_use_named_refusal(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(case_uses=[123])

    def test_text_case_use_named_refusal(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(case_uses=["not a record"])

    def test_list_case_use_named_refusal(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _record(case_uses=[["fixture"]])

    def test_dict_case_use_controls(self):
        record = _record(case_uses=[{"fixture": "F-26",
                                     "use": "whatever"}])
        self.assertEqual(record["case_uses"][0]["use"],
                         "strategy search point only")
        record = _record(case_uses=[{"fixture": "other",
                                     "use": "another use"}])
        self.assertEqual(record["case_uses"][0]["fixture"], "other")


class TestR14065ReadoutWordingDressForms(unittest.TestCase):

    def test_double_space_economic_security_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording="economic  security assured")

    def test_double_space_economically_secure_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording="economically  secure")

    def test_tab_divided_phrase_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording="economic\tsecurity assured")

    def test_hyphen_dress_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording="economically-secure")

    def test_single_space_and_plain_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording="the system stands "
                                   "economically secure")
        unit = mod09.readout(
            _record(), wording="readout wording for the search")
        self.assertEqual(unit["wording"],
                         "readout wording for the search")


if __name__ == "__main__":
    unittest.main()

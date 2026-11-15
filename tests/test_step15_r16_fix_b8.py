"""Pins for Round 15 rows R15-060 to R15-067 and R15-093.

MOD-09 search, readout, and catalogue forms, with the MOD-02
generator state forms in the same scope, Builder 8 of fix
wave 15. Each test pins the defect its row states with the
proving acts the source papers used (Blue 4 Findings 1 to 8
and Orange 2 Finding 1), beside the plain controls those
papers ran.
"""
import unittest

from crucible import mod02, mod09


def _carriage(strategies=("conditional briber",)):
    return mod09.run_record_carriage(
        list(strategies), 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(outcome="no failure", **kwargs):
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
        external_profit_swept_values=(0, 5), **kwargs)


def _build_with(**overrides):
    call = {
        "run_carriage": _carriage(),
        "points_tried": ["point one"],
        "per_point_outcome": [{"point": "point one",
                               "outcome": "no failure"}],
        "bond_candidates": [{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        "budget": "stated budget",
        "neighbourhood": {"definition": "adjacent points",
                          "step sizes": [1]},
        "starting_points": ["point zero"],
        "order_of_search": ["point one"],
        "external_profit_swept_values": (0, 5),
    }
    call.update(overrides)
    return mod09.build_search_record(**call)


class EqFalseStr(str):
    """Stores its text, answers False to every equality test."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class EqTrueStr(str):
    """Stores its text, answers True to every equality test."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqFalseNeFalseStr(str):
    """Stores its text; equality and inequality both say False."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqTrueInt(int):
    """Stores its number, answers True to every equality test."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class EqFalseInt(int):
    """Stores its number, answers False to every equality test."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = int.__hash__


class GtTrueInt(int):
    """Stores its number, answers True to every greater test."""

    def __gt__(self, other):
        return True

    __hash__ = int.__hash__


class WrongHashStr(str):
    """Stores its text, hashes into a bucket no stored key uses."""

    def __hash__(self):
        return hash("bucket no stored key uses")


class GreedyNameStr(str):
    """Stores its text, hashes as another name, claims all equal."""

    def __hash__(self):
        return hash("b")

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class IterLieList(list):
    """Stores one set of items, iterates as another."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)


class IterLieSet(set):
    """Stores one set of items, iterates as another."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)


class RaisingStr:
    """An object in no text form whose string reading raises."""

    def __str__(self):
        raise RuntimeError("string reading unavailable")


class TestR15060CaseUseStoredEquality(unittest.TestCase):

    def _with_case_uses(self, uses):
        record = _record()
        record["case_uses"] = uses
        return record

    def test_lying_fixture_evasion_refused_at_both_acts(self):
        record = self._with_case_uses([{
            "fixture": EqFalseStr("F-26"),
            "use": "deployed failure"}])
        self.assertFalse(mod09.validate_search_record(record))
        failures = mod09.search_record_validation_failures(record)
        self.assertTrue(any("F-26" in line for line in failures))

    def test_clean_case_no_false_refusal_at_both_acts(self):
        record = self._with_case_uses([{
            "fixture": EqTrueStr("other"),
            "use": "deployed failure"}])
        self.assertTrue(mod09.validate_search_record(record))
        self.assertEqual(
            mod09.search_record_validation_failures(record), [])

    def test_lying_use_reading_evasion_refused(self):
        record = self._with_case_uses([{
            "fixture": "F-26",
            "use": EqFalseNeFalseStr("deployed failure")}])
        self.assertFalse(mod09.validate_search_record(record))
        failures = mod09.search_record_validation_failures(record)
        self.assertTrue(any("F-26" in line for line in failures))

    def test_plain_controls(self):
        record = self._with_case_uses([{
            "fixture": "F-26", "use": "deployed failure"}])
        self.assertFalse(mod09.validate_search_record(record))
        record = self._with_case_uses([{
            "fixture": "F-26",
            "use": "strategy search point only"}])
        self.assertTrue(mod09.validate_search_record(record))
        record = self._with_case_uses([{
            "fixture": "other", "use": "deployed failure"}])
        self.assertTrue(mod09.validate_search_record(record))


class TestR15061SweepStoredReadings(unittest.TestCase):

    def _sweep(self, values, largest):
        strategy = mod09.make_strategy(
            "sweep subject", in_protocol_payoff=largest,
            external_profit_range=list(values))
        return mod09.sweep_external_profit(strategy)

    def test_greedy_equality_no_zero_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            self._sweep([EqTrueInt(5), EqTrueInt(9)], 4)

    def test_stored_zero_seen_through_lying_equality(self):
        rows = self._sweep([EqFalseInt(0), 9], 4)
        self.assertEqual(len(rows), 2)

    def test_lying_greater_reading_no_cover_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            self._sweep([0, GtTrueInt(2)], 100)

    def test_plain_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            self._sweep([5, 9], 4)
        with self.assertRaises(mod09.NamedAttackerFailure):
            self._sweep([0, 2], 100)
        rows = self._sweep([0, 9], 4)
        self.assertEqual(len(rows), 2)


class TestR15062CarriedStateStoredNameLookup(unittest.TestCase):

    def test_wrong_hash_name_carries_its_position(self):
        state = mod02.checkpoint_generator_state(
            run_id="run one",
            stream_classes=[WrongHashStr("a")], positions={"a": 7})
        positions = [entry["position"]
                     for entry in state["stream_states"].values()]
        self.assertEqual(positions, [7])

    def test_greedy_name_carries_its_own_position(self):
        for act in (mod02.checkpoint_generator_state,
                    mod02.resume_consumed_generator_state):
            state = act(run_id="run one",
                        stream_classes=[GreedyNameStr("a")],
                        positions={"a": 7, "b": 9})
            by_name = {str.__str__(name): entry["position"]
                       for name, entry in
                       state["stream_states"].items()}
            self.assertEqual(by_name, {"a": 7, "b": 9})

    def test_base_dict_get_contrast_control(self):
        self.assertEqual(
            mod02._base_dict_get({"a": 7}, WrongHashStr("a")), 7)

    def test_plain_name_control(self):
        state = mod02.checkpoint_generator_state(
            run_id="run one", stream_classes=["a", "b"],
            positions={"a": 7, "b": 9})
        by_name = {name: entry["position"]
                   for name, entry in state["stream_states"].items()}
        self.assertEqual(by_name, {"a": 7, "b": 9})


class TestR15063WordingUnorderedAndMappingDress(unittest.TestCase):

    def test_set_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording={"economic security"})

    def test_frozenset_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording=frozenset({"economic security"}))

    def test_dict_value_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording={"note": "economic security"})

    def test_dict_key_wording_claim_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording={"economic security": "note"})

    def test_set_established_wording_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording={"established"})

    def test_list_holding_set_wording_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording=[{"economic security"}])

    def test_tuple_holding_dict_wording_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                _record(), wording=({"note": "economically secure"},))

    def test_plain_controls(self):
        unit = mod09.readout(
            _record(), wording="readout wording for the search")
        self.assertEqual(unit["wording"],
                         "readout wording for the search")
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording="economic security")


class TestR15064OutcomeContainerDress(unittest.TestCase):

    def _assert_withholds(self, outcome):
        record = _record(outcome=outcome)
        self.assertTrue(mod09.validate_search_record(record))
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_list_outcome_withholds_sentence(self):
        self._assert_withholds(["failure found"])

    def test_tuple_outcome_withholds_sentence(self):
        self._assert_withholds(("failure found",))

    def test_set_outcome_withholds_sentence(self):
        self._assert_withholds({"failure found"})

    def test_list_of_bytes_outcome_withholds_sentence(self):
        self._assert_withholds([b"failure found"])

    def test_split_list_outcome_withholds_sentence(self):
        self._assert_withholds(["failure", "found"])

    def test_clean_container_outcome_keeps_sentence(self):
        record = _record(outcome=["no failure"])
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)

    def test_text_controls(self):
        record = _record(outcome="failure found")
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)
        record = _record(outcome="no failure")
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)


class TestR15065CatalogueStoredIteration(unittest.TestCase):

    def test_list_iteration_lie_lists_stored_identifier(self):
        catalogue = mod09.strategy_catalogue(
            extra_identifiers=IterLieList(["x1"], ["ghost-id"]))
        self.assertIn("x1", catalogue["identifiers"])
        self.assertNotIn("ghost-id", catalogue["identifiers"])

    def test_list_iteration_drop_lists_stored_identifier(self):
        catalogue = mod09.strategy_catalogue(
            extra_identifiers=IterLieList(["x1"], []))
        self.assertIn("x1", catalogue["identifiers"])

    def test_set_iteration_lie_lists_stored_identifier(self):
        catalogue = mod09.strategy_catalogue(
            extra_identifiers=IterLieSet({"x1"}, ["ghost-id"]))
        self.assertIn("x1", catalogue["identifiers"])
        self.assertNotIn("ghost-id", catalogue["identifiers"])

    def test_bare_text_handed_as_one_identifier(self):
        catalogue = mod09.strategy_catalogue(extra_identifiers="ab")
        self.assertIn("ab", catalogue["identifiers"])
        self.assertNotIn("a", catalogue["identifiers"])
        self.assertNotIn("b", catalogue["identifiers"])

    def test_plain_controls(self):
        catalogue = mod09.strategy_catalogue(extra_identifiers=["x1"])
        self.assertIn("x1", catalogue["identifiers"])
        self.assertIn("conditional briber", catalogue["identifiers"])
        catalogue = mod09.strategy_catalogue(extra_identifiers={"x1"})
        self.assertIn("x1", catalogue["identifiers"])


class TestR15066FieldEmptinessBufferAndFrozenset(unittest.TestCase):

    def test_empty_bytes_budget_build_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(budget=b"")

    def test_empty_bytearray_budget_build_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(budget=bytearray(b""))

    def test_empty_frozenset_budget_build_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(budget=frozenset())

    def test_empty_frozenset_points_build_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(points_tried=frozenset())

    def test_empty_bytes_points_build_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(points_tried=b"")

    def test_handed_record_dresses_refused_at_both_acts(self):
        record = _record()
        record["search_record"]["search_budget"] = b""
        self.assertFalse(mod09.validate_search_record(record))
        self.assertNotEqual(
            mod09.search_record_validation_failures(record), [])
        record = _record()
        record["search_record"]["points_tried"] = frozenset()
        self.assertFalse(mod09.validate_search_record(record))
        self.assertNotEqual(
            mod09.search_record_validation_failures(record), [])

    def test_controls(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            _build_with(budget=[])
        record = _record()
        self.assertTrue(mod09.validate_search_record(record))
        self.assertEqual(
            mod09.search_record_validation_failures(record), [])


class TestR15067HeldSortKeyStoredName(unittest.TestCase):

    def test_raising_name_as_stream_class_carries(self):
        state = mod02.checkpoint_generator_state(
            run_id="run one", stream_classes=[RaisingStr()])
        self.assertEqual(len(state["stream_states"]), 1)
        positions = [entry["position"]
                     for entry in state["stream_states"].values()]
        self.assertEqual(positions, [0])

    def test_raising_name_as_positions_key_carries(self):
        marker = RaisingStr()
        state = mod02.checkpoint_generator_state(
            run_id="run one", positions={marker: 3})
        positions = [entry["position"]
                     for entry in state["stream_states"].values()]
        self.assertEqual(positions, [3])

    def test_raising_name_as_held_state_key_carries(self):
        marker = RaisingStr()
        state = mod02.checkpoint_generator_state(
            run_id="run one", held_state={marker: 5})
        positions = [entry["position"]
                     for entry in state["stream_states"].values()]
        self.assertEqual(positions, [5])

    def test_text_and_integer_name_controls(self):
        state = mod02.checkpoint_generator_state(
            run_id="run one", stream_classes=["a"],
            positions={"a": 7})
        self.assertEqual(
            state["stream_states"]["a"]["position"], 7)
        state = mod02.checkpoint_generator_state(
            run_id="run one", positions={5: 2})
        self.assertEqual(state["stream_states"][5]["position"], 2)


class TestR15093ReadoutRecordedFailureCarriage(unittest.TestCase):

    def _unit_for(self, per_point_outcome):
        record = _record()
        record["search_record"]["per_point_outcome"] = per_point_outcome
        return mod09.readout(record, found_failure=False)

    def test_empty_dict_outcome_gets_no_sentence(self):
        unit = self._unit_for({})
        self.assertNotIn("no_failure_sentence", unit)

    def test_entry_without_outcome_key_gets_no_sentence(self):
        unit = self._unit_for([{"search_point": 1}])
        self.assertNotIn("no_failure_sentence", unit)

    def test_entry_with_none_outcome_gets_no_sentence(self):
        unit = self._unit_for([{"outcome": None}])
        self.assertNotIn("no_failure_sentence", unit)

    def test_point_mapping_text_failure_withholds_sentence(self):
        unit = self._unit_for({"p1": "failure found"})
        self.assertNotIn("no_failure_sentence", unit)

    def test_point_mapping_entry_failure_withholds_sentence(self):
        unit = self._unit_for({"p1": {"outcome": "failure found"}})
        self.assertNotIn("no_failure_sentence", unit)

    def test_clean_controls_keep_sentence(self):
        unit = self._unit_for([{"outcome": "no failure"}])
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)
        unit = self._unit_for({"outcome": "no failure"})
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)
        unit = self._unit_for({"p1": "no failure"})
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)

    def test_absent_outcome_controls_get_no_sentence(self):
        unit = self._unit_for([])
        self.assertNotIn("no_failure_sentence", unit)
        record = _record(outcome="no failure")
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)


if __name__ == "__main__":
    unittest.main()

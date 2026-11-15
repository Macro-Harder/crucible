"""Pins for Round 19 rows R19-007, R19-008, R19-018, R19-037,
and R19-039.

MOD-09 readout, outcome, and wording family, Builder 1 of fix
wave 19. Each pin states the defect its row charges in the
distinguishing case, beside the plain controls the source
papers ran.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod09


def _carriage(strategies=("conditional briber",), position=6):
    return mod09.run_record_carriage(
        list(strategies), position, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(per_point_outcome=None, swept=(0, 5)):
    if per_point_outcome is None:
        per_point_outcome = [{"point": "point one",
                              "outcome": "no failure"}]
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=per_point_outcome,
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=swept)


def _record_with_outcome(per_point_outcome):
    record = _record()
    record["search_record"]["per_point_outcome"] = per_point_outcome
    return record


NO_FAILURE = (
    "The search found no failure at the points the search record "
    "names.")


def _present(per_point_outcome):
    unit = mod09.readout(
        _record(per_point_outcome=per_point_outcome),
        found_failure=False)
    return unit.get("no_failure_sentence") == NO_FAILURE


def _present_on_record(record):
    unit = mod09.readout(record, found_failure=False)
    return unit.get("no_failure_sentence") == NO_FAILURE


class LyingInt(int):
    """An int subclass storing a value whose inequality reading
    answers False against every value."""

    def __ne__(self, other):
        return False


class LyingFloat(float):
    """A float subclass storing a value whose inequality reading
    answers False against every value."""

    def __ne__(self, other):
        return False


class ArmedKey:
    """A key storing a plain name, its hash reading returning 7
    in every state, and its equality and inequality readings
    raising once the class flag stands up."""

    armed = False

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 7

    def __eq__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed equality")
        return False

    def __ne__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed inequality")
        return True


def _armed_inner():
    ArmedKey.armed = False
    inner = {ArmedKey("a"): 1, ArmedKey("b"): 2}
    ArmedKey.armed = True
    return inner


def _nested_in_list(value, count):
    for _ in range(count):
        value = [value]
    return value


def _nested_in_tuple(value, count):
    for _ in range(count):
        value = (value,)
    return value


def _nested_in_dict(value, count):
    for _ in range(count):
        value = {"k": value}
    return value


class TestR19007PointKeyBesideFellow(unittest.TestCase):
    def _present_with(self, entry):
        return _present([{"p0": "clean"}, entry])

    def test_failure_under_point_beside_int_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": 5}))

    def test_failure_under_point_beside_bool_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": True}))

    def test_failure_under_point_beside_none_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": None}))

    def test_failure_under_point_beside_float_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": 0.0}))

    def test_failure_under_point_beside_complex_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": 1j}))

    def test_failure_under_point_beside_decimal_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": Decimal(5)}))

    def test_failure_under_point_beside_fraction_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": Fraction(1, 2)}))

    def test_failure_under_point_beside_object_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": object()}))

    def test_failure_under_point_beside_range_fellow(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": range(3)}))

    def test_nested_failure_under_point_beside_scalar_fellow(self):
        self.assertFalse(self._present_with(
            {"point": {"p9": "failure found"}, "p2": 5}))

    def test_tuple_carriage_failure_under_point_beside_int(self):
        self.assertFalse(_present(
            ({"p0": "clean"},
             {"point": "failure found", "p2": 5})))

    def test_dict_carriage_int_fellow_control(self):
        self.assertFalse(_present(
            {"p0": "clean", "point": "failure found", "p2": 5}))

    def test_dict_carriage_decimal_fellow_control(self):
        self.assertFalse(_present(
            {"p0": "clean", "point": "failure found",
             "p2": Decimal(5)}))

    def test_dict_carriage_object_fellow_control(self):
        self.assertFalse(_present(
            {"p0": "clean", "point": "failure found",
             "p2": object()}))

    def test_clean_under_point_beside_int_fellow_control(self):
        self.assertTrue(self._present_with(
            {"point": "no failure", "p2": 5}))

    def test_wave18_text_fellow_control(self):
        self.assertFalse(self._present_with(
            {"point": "failure found", "p2": "clean"}))

    def test_point_key_alone_bound_control(self):
        self.assertFalse(_present([{"point": "point one"}]))

    def test_scalar_alone_bound_control(self):
        self.assertFalse(_present([{"search_point": 1}]))


class TestR19008StoredTruthyNumberLimb(unittest.TestCase):
    def test_mid_run_lying_int_refused(self):
        record = _record()
        record["mid_run_strategies"] = LyingInt(5)
        self.assertFalse(mod09.validate_search_record(record))

    def test_mid_run_lying_int_failure_named(self):
        record = _record()
        record["mid_run_strategies"] = LyingInt(5)
        failures = mod09.search_record_validation_failures(record)
        self.assertTrue(any(
            "mid_run_strategies stand stated" in failure
            for failure in failures))

    def test_mid_run_lying_float_refused(self):
        record = _record()
        record["mid_run_strategies"] = LyingFloat(5.0)
        self.assertFalse(mod09.validate_search_record(record))

    def test_make_strategy_parameters_lying_int_delivered(self):
        strategy = mod09.make_strategy(
            "some strategy", parameters=LyingInt(5))
        self.assertEqual(strategy["parameters"], 5)

    def test_parameter_set_lying_int_no_failure(self):
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = (
            LyingInt(5))
        failures = mod09.search_record_validation_failures(record)
        self.assertFalse(any(
            "carries no parameter set" in failure
            for failure in failures))
        self.assertTrue(mod09.validate_search_record(record))

    def test_mid_run_plain_int_control(self):
        record = _record()
        record["mid_run_strategies"] = 5
        self.assertFalse(mod09.validate_search_record(record))

    def test_mid_run_absent_control(self):
        record = _record()
        self.assertTrue(mod09.validate_search_record(record))

    def test_make_strategy_parameters_plain_control(self):
        strategy = mod09.make_strategy(
            "some strategy", parameters=5)
        self.assertEqual(strategy["parameters"], 5)

    def test_parameter_set_plain_control(self):
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = 5
        self.assertTrue(mod09.validate_search_record(record))

    def test_mid_run_plain_zero_control(self):
        record = _record()
        record["mid_run_strategies"] = 0
        self.assertTrue(mod09.validate_search_record(record))


class TestR19018StoredCopyAssignment(unittest.TestCase):
    def tearDown(self):
        ArmedKey.armed = False

    def test_make_strategy_armed_inner_carried_whole(self):
        inner = _armed_inner()
        strategy = mod09.make_strategy(
            "some strategy", parameters={"payload": inner})
        carried = strategy["parameters"]["payload"]
        self.assertEqual(len(carried), 2)
        self.assertEqual(sorted(carried.values()), [1, 2])

    def test_stored_copy_armed_inner_carried_whole(self):
        inner = _armed_inner()
        carried = mod09._stored_copy({"payload": inner})
        self.assertEqual(len(carried["payload"]), 2)
        self.assertEqual(
            sorted(carried["payload"].values()), [1, 2])

    def test_plain_nested_copy_control(self):
        strategy = mod09.make_strategy(
            "some strategy", parameters={"payload": {"a": 1, "b": 2}})
        self.assertEqual(
            strategy["parameters"], {"payload": {"a": 1, "b": 2}})

    def test_no_parameters_control(self):
        strategy = mod09.make_strategy("some strategy")
        self.assertEqual(strategy["parameters"], {})


class TestR19037OutcomeStandsFailureBound(unittest.TestCase):
    def test_deep_list_outcome_in_dict_carriage_returns_unit(self):
        record = _record_with_outcome(
            {"p1": _nested_in_list("failure found", 3000)})
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_deep_tuple_outcome_in_dict_carriage_returns_unit(self):
        record = _record_with_outcome(
            {"p1": _nested_in_tuple("failure found", 3000)})
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_deep_dict_outcome_under_outcome_key_returns_unit(self):
        record = _record_with_outcome(
            [{"outcome": _nested_in_dict("failure found", 3000)}])
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_cyclic_list_outcome_returns_unit(self):
        cyclic = []
        cyclic.append(cyclic)
        record = _record_with_outcome([{"outcome": cyclic}])
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_cyclic_dict_outcome_returns_unit(self):
        cyclic = {}
        cyclic["self"] = cyclic
        record = _record_with_outcome([{"outcome": cyclic}])
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_deep_clean_outcome_returns_unit(self):
        record = _record_with_outcome(
            {"p1": _nested_in_list("clean", 3000)})
        unit = mod09.readout(record, found_failure=False)
        self.assertIn("readout_status", unit)

    def test_shallow_list_wrapped_failure_control(self):
        self.assertFalse(_present([{"outcome": ["failure found"]}]))

    def test_shallow_dict_wrapped_failure_control(self):
        self.assertFalse(_present(
            [{"outcome": {"detail": "failure found"}}]))

    def test_plain_clean_outcome_control(self):
        self.assertTrue(_present([{"outcome": "no failure"}]))


class TestR19039WordingClaimTextBound(unittest.TestCase):
    def test_cyclic_list_wording_returns_unit(self):
        wording = []
        wording.append(wording)
        unit = mod09.readout(_record(), wording=wording)
        self.assertIn("readout_status", unit)

    def test_cyclic_dict_wording_returns_unit(self):
        wording = {}
        wording["self"] = wording
        unit = mod09.readout(_record(), wording=wording)
        self.assertIn("readout_status", unit)

    def test_deep_list_wording_returns_unit(self):
        wording = _nested_in_list("plain wording", 3000)
        unit = mod09.readout(_record(), wording=wording)
        self.assertIn("readout_status", unit)

    def test_established_beside_cycle_still_refused(self):
        wording = ["established"]
        wording.append(wording)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording=wording)

    def test_plain_wording_control(self):
        unit = mod09.readout(_record(), wording="a plain wording")
        self.assertIn("readout_status", unit)

    def test_established_list_wording_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), wording=["established"])


if __name__ == "__main__":
    unittest.main()

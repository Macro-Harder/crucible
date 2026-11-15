"""Pins for fix wave 18, Builder 7, group 7 rows.

Rows pinned: R18-005, R18-006, R18-007, R18-008, R18-036,
R18-037, R18-038, and R18-058.
"""

import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod11, mod14


class LyingInt(int):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class FalseInt(int):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = int.__hash__


class LyingFloat(float):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = float.__hash__


class FalseStr(str):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class StripLyingStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj.reading = reading
        return obj

    def strip(self, *args):
        return self.reading


class StripRaisingStr(str):
    def strip(self, *args):
        raise RuntimeError("strip boom")


class HidingList(list):
    def __iter__(self):
        return iter(())


class FabricatingList(list):
    def __iter__(self):
        return iter([{
            "week": 2,
            "headline_unit_identifiers": ["u1", "u2", "u3"],
        }])


class ZeroLenList(list):
    def __len__(self):
        return 0


class _Failure(Exception):
    pass


def _carriage(failure_dict):
    failure = _Failure("boom")
    failure.failure = failure_dict
    return mod14.error_carriage(failure)


class TestR18005WeeklyPairNumbers(unittest.TestCase):
    records = [
        {"week": 999, "headline_unit_identifiers": ["u1"]},
        {"week": 2, "headline_unit_identifiers": ["u2"]},
    ]

    def test_mod11_lying_int_week_counts_only_stored_match(self):
        self.assertEqual(mod11.weekly_count(self.records, LyingInt(2)), 1)

    def test_mod14_lying_int_week_counts_only_stored_match(self):
        self.assertEqual(
            mod14.weekly_headline_count(self.records, LyingInt(2)), 1)

    def test_mod11_false_int_week_still_counts_its_stored_week(self):
        self.assertEqual(mod11.weekly_count(self.records, FalseInt(2)), 1)

    def test_mod14_false_int_week_still_counts_its_stored_week(self):
        self.assertEqual(
            mod14.weekly_headline_count(self.records, FalseInt(2)), 1)

    def test_mod11_lying_float_week_counts_only_stored_match(self):
        self.assertEqual(
            mod11.weekly_count(self.records, LyingFloat(2.0)), 1)

    def test_mod14_lying_float_week_counts_only_stored_match(self):
        self.assertEqual(
            mod14.weekly_headline_count(self.records, LyingFloat(2.0)), 1)

    def test_plain_week_control_mod11(self):
        self.assertEqual(mod11.weekly_count(self.records, 2), 1)
        self.assertEqual(mod11.weekly_count(self.records, 999), 1)
        self.assertEqual(mod11.weekly_count(self.records, 5), 0)

    def test_plain_week_control_mod14(self):
        self.assertEqual(mod14.weekly_headline_count(self.records, 2), 1)
        self.assertEqual(mod14.weekly_headline_count(self.records, 999), 1)


class TestR18005WeeklyPairContainers(unittest.TestCase):
    def test_bool_inside_list_week_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(module._week_stands_equal([True], [1]))
            self.assertFalse(module._week_stands_equal([1], [True]))

    def test_decimal_inside_list_week_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(
                module._week_stands_equal([Decimal(1)], [1]))

    def test_fraction_inside_list_week_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(
                module._week_stands_equal([Fraction(1, 1)], [1]))

    def test_bool_inside_tuple_and_set_weeks_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(module._week_stands_equal((True,), (1,)))
            self.assertFalse(module._week_stands_equal({True}, {1}))

    def test_bool_inside_dict_week_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(
                module._week_stands_equal({"k": True}, {"k": 1}))

    def test_decimal_inside_nested_list_week_apart_from_int(self):
        for module in (mod11, mod14):
            self.assertFalse(
                module._week_stands_equal([[Decimal(2)]], [[2]]))

    def test_container_gate_counts_only_stored_match_mod11(self):
        records = [
            {"week": [True], "headline_unit_identifiers": ["u1"]},
            {"week": [1], "headline_unit_identifiers": ["u2"]},
        ]
        self.assertEqual(mod11.weekly_count(records, [1]), 1)

    def test_container_gate_counts_only_stored_match_mod14(self):
        records = [
            {"week": [True], "headline_unit_identifiers": ["u1"]},
            {"week": [1], "headline_unit_identifiers": ["u2"]},
        ]
        self.assertEqual(mod14.weekly_headline_count(records, [1]), 1)

    def test_container_controls(self):
        for module in (mod11, mod14):
            self.assertTrue(module._week_stands_equal([1, 2], [1, 2]))
            self.assertFalse(module._week_stands_equal([1], [2]))
            self.assertTrue(module._week_stands_equal("2", "2"))
            self.assertTrue(module._week_stands_equal(True, True))
            self.assertFalse(module._week_stands_equal(True, 1))
            self.assertTrue(
                module._week_stands_equal(Decimal(1), Decimal(1)))
            self.assertTrue(module._week_stands_equal(2, 2.0))
            self.assertTrue(
                module._week_stands_equal({1, 2}, {2, 1}))


class TestR18006PilotClaim(unittest.TestCase):
    def test_false_equality_behaviour_kind_still_barred(self):
        claim = {"cites_pilot_output": True, "kind": FalseStr("behaviour")}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_bytes_behaviour_kind_still_barred(self):
        claim = {"cites_pilot_output": True, "kind": b"behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_pilot_run_refuses_false_equality_behaviour_claim(self):
        artefact = {"cites_pilot_output": True, "kind": FalseStr("behaviour")}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_pilot_run_refuses_bytes_behaviour_claim(self):
        artefact = {"cites_pilot_output": True, "kind": b"behaviour"}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_controls(self):
        self.assertFalse(mod14.validate_pilot_claim(
            {"cites_pilot_output": True, "kind": "behaviour"}))
        self.assertTrue(mod14.validate_pilot_claim(
            {"cites_pilot_output": True, "kind": "other"}))
        self.assertTrue(mod14.validate_pilot_claim(
            {"cites_pilot_output": True, "kind": FalseStr("other")}))
        self.assertFalse(mod14.validate_pilot_claim(
            {"settles_population_behaviour_rate": True}))


class TestR18007OutsideCallMark(unittest.TestCase):
    def _outcome_of(self, mark):
        result = mod14.outside_call_check(
            {}, {"calls": [{"outside_call": mark}]})
        return result["outcome"]

    def test_true_mark_with_false_readings_still_present(self):
        self.assertEqual(
            self._outcome_of(StripLyingStr("true", "false")),
            "outside calls present")

    def test_false_mark_with_true_readings_still_absent(self):
        self.assertEqual(
            self._outcome_of(StripLyingStr("false", "true")),
            "no outside calls read")

    def test_raising_strip_mark_judged_on_stored_text(self):
        self.assertEqual(
            self._outcome_of(StripRaisingStr("true")),
            "outside calls present")

    def test_controls(self):
        self.assertEqual(self._outcome_of("true"), "outside calls present")
        self.assertEqual(self._outcome_of("false"), "no outside calls read")
        self.assertEqual(self._outcome_of(True), "outside calls present")
        self.assertEqual(self._outcome_of(0), "no outside calls read")


class TestR18008WeeklyHeadlineRecords(unittest.TestCase):
    records = [
        {"week": 2, "headline_unit_identifiers": ["u1"]},
        {"week": 2, "headline_unit_identifiers": ["u2"]},
    ]

    def test_hiding_iteration_records_still_counted(self):
        self.assertEqual(
            mod14.weekly_headline_count(HidingList(self.records), 2), 2)

    def test_fabricating_iteration_records_not_counted(self):
        self.assertEqual(
            mod14.weekly_headline_count(
                FabricatingList(self.records), 2), 2)

    def test_zero_length_reading_records_still_counted(self):
        self.assertEqual(
            mod14.weekly_headline_count(ZeroLenList(self.records), 2), 2)

    def test_hidden_refusal_record_still_refused(self):
        bad = HidingList([{"no_week_field": 1}])
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count(bad, 2)

    def test_controls(self):
        self.assertEqual(
            mod14.weekly_headline_count(list(self.records), 2), 2)
        self.assertEqual(
            mod14.weekly_headline_count(tuple(self.records), 2), 2)


class TestR18036SimulationFamilies(unittest.TestCase):
    def test_hidden_non_synthetic_family_still_refused(self):
        families = HidingList([
            {"synthetic": True, "retained_under_first_rule": True},
            {"synthetic": False},
        ])
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.dual_rule_retention_simulation(families)

    def test_controls(self):
        result = mod14.dual_rule_retention_simulation([
            {"synthetic": True, "retained_under_first_rule": True,
             "retained_under_second_rule": False},
            {"synthetic": True, "retained_under_first_rule": True,
             "retained_under_second_rule": True},
        ])
        self.assertEqual(
            result["paired_field"],
            {"first_rule_retained": 2, "second_rule_retained": 1})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.dual_rule_retention_simulation([{"synthetic": False}])


class SecondCallRaiser:
    def __init__(self):
        self.armed = False
        self.calls = 0

    def __hash__(self):
        return 7

    def __eq__(self, other):
        if self.armed:
            self.calls += 1
            if self.calls >= 2:
                raise RuntimeError("eq boom at assignment")
            return False
        return self is other

    def __ne__(self, other):
        return not self.__eq__(other)


class AlwaysRaiser:
    def __init__(self, exc):
        self.armed = False
        self.exc = exc

    def __hash__(self):
        return 11

    def __eq__(self, other):
        if self.armed:
            raise self.exc("eq boom after arming")
        return self is other

    def __ne__(self, other):
        if self.armed:
            raise self.exc("ne boom after arming")
        return self is not other


class FlagHash:
    def __init__(self):
        self.up = False

    def __hash__(self):
        if self.up:
            raise RuntimeError("hash boom after flag up")
        return 7

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class TestR18037FreezeAssignmentEquality(unittest.TestCase):
    def test_assignment_equality_raise_delivers_carriage(self):
        first = SecondCallRaiser()
        second = SecondCallRaiser()
        inner = {first: "first", second: "second"}
        first.armed = True
        second.armed = True
        carriage = _carriage({"inner": inner})
        frozen_inner = carriage["failure_value"]["inner"]
        self.assertEqual(len(frozen_inner), 2)
        self.assertEqual(
            sorted(frozen_inner.values()), ["first", "second"])

    def test_assignment_equality_raise_delivers_frozen_copy(self):
        first = SecondCallRaiser()
        second = SecondCallRaiser()
        inner = {first: "first", second: "second"}
        first.armed = True
        second.armed = True
        frozen = mod14._freeze(inner)
        self.assertEqual(len(frozen), 2)
        self.assertEqual(sorted(frozen.values()), ["first", "second"])


class TestR18038FreezeInsertion(unittest.TestCase):
    def _run(self, exc):
        first = AlwaysRaiser(exc)
        second = AlwaysRaiser(exc)
        inner = {first: "first", second: "second"}
        first.armed = True
        second.armed = True
        carriage = _carriage({"inner": inner})
        frozen_inner = carriage["failure_value"]["inner"]
        self.assertEqual(len(frozen_inner), 2)
        self.assertEqual(
            sorted(frozen_inner.values()), ["first", "second"])

    def test_two_colliding_keys_runtime_error_dress(self):
        self._run(RuntimeError)

    def test_two_colliding_keys_value_error_dress(self):
        self._run(ValueError)

    def test_single_key_control_delivers_whole(self):
        key = AlwaysRaiser(RuntimeError)
        inner = {key: "only"}
        key.armed = True
        carriage = _carriage({"inner": inner})
        frozen_inner = carriage["failure_value"]["inner"]
        self.assertEqual(len(frozen_inner), 1)
        self.assertEqual(list(frozen_inner.values()), ["only"])


class TestR18058FreezeAssignmentHash(unittest.TestCase):
    def test_flag_hash_raise_delivers_carriage(self):
        key = FlagHash()
        inner = {key: "value"}
        key.up = True
        carriage = _carriage({"inner": inner})
        frozen_inner = carriage["failure_value"]["inner"]
        self.assertEqual(len(frozen_inner), 1)
        self.assertEqual(list(frozen_inner.values()), ["value"])

    def test_flag_down_control_delivers_whole(self):
        key = FlagHash()
        inner = {key: "value"}
        carriage = _carriage({"inner": inner})
        frozen_inner = carriage["failure_value"]["inner"]
        self.assertEqual(len(frozen_inner), 1)
        self.assertEqual(list(frozen_inner.values()), ["value"])
        self.assertIn(key, list(frozen_inner.keys()))


class TestFreezePlainControls(unittest.TestCase):
    def test_plain_freeze_control(self):
        source = {"a": {"b": [1, 2]}, "c": ("x", 3)}
        self.assertEqual(mod14._freeze(source), source)


if __name__ == "__main__":
    unittest.main()

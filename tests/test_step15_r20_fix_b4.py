"""Pins for fix wave 19, Builder 4, group 4 rows.

Rows pinned: R19-005, R19-010, R19-034, R19-035, R19-054,
and R19-055.
"""

import unittest

from crucible import mod14
from crucible.mod14 import NamedShellFailure


class BoolLiar:
    """Stores a value and answers the opposite from its
    truth reading."""

    def __init__(self, stored):
        self.stored = stored

    def __bool__(self):
        return not self.stored


class BoolRaiser:
    """Its truth reading raises on every call."""

    def __bool__(self):
        raise RuntimeError("bool boom")


class FalseList(list):
    """A list storing its parts whose truth reading answers
    False whatever it stores."""

    def __bool__(self):
        return False


class EqTrueInt(int):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class EqFalseInt(int):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = int.__hash__


class EqRaisingInt(int):
    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = int.__hash__


class ArmedHashStr(str):
    """A text key whose hash reading answers the base string
    hash while disarmed and raises once armed."""

    def __new__(cls, stored):
        obj = str.__new__(cls, stored)
        obj.armed = False
        return obj

    def __hash__(self):
        if self.armed:
            raise RuntimeError("hash boom")
        return str.__hash__(self)


class ReprLyingList(list):
    def __repr__(self):
        return "same"


class ReprLyingDict(dict):
    def __repr__(self):
        return "same"


class ReprLyingSet(set):
    def __repr__(self):
        return "same"


def _outside_outcome(mark):
    result = mod14.outside_call_check(
        {"entries": []}, {"calls": [{"outside_call": mark}]})
    return result["outcome"]


class TestR19005PilotClaimTruthLimbs(unittest.TestCase):

    def test_cites_bool_liar_storing_true_barred(self):
        claim = {"cites_pilot_output": BoolLiar(True),
                 "kind": "behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_settles_bool_liar_storing_true_barred(self):
        claim = {"settles_population_behaviour_rate": BoolLiar(True),
                 "kind": "timing"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_cites_container_storing_a_part_barred(self):
        claim = {"cites_pilot_output": FalseList([1]),
                 "kind": "behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_cites_raising_truth_no_bare_escape(self):
        claim = {"cites_pilot_output": BoolRaiser(),
                 "kind": "behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_settles_raising_truth_no_bare_escape(self):
        claim = {"settles_population_behaviour_rate": BoolRaiser(),
                 "kind": "timing"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_pilot_run_bool_liar_claim_refused(self):
        claim = {"cites_pilot_output": BoolLiar(True),
                 "kind": "behaviour"}
        with self.assertRaises(NamedShellFailure):
            mod14.pilot_run("timing", claim)

    def test_pilot_run_settles_bool_liar_claim_refused(self):
        claim = {"settles_population_behaviour_rate": BoolLiar(True),
                 "kind": "timing"}
        with self.assertRaises(NamedShellFailure):
            mod14.pilot_run("timing", claim)

    def test_control_plain_cites_behaviour_barred(self):
        claim = {"cites_pilot_output": True, "kind": "behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_control_plain_settles_barred(self):
        claim = {"settles_population_behaviour_rate": True}
        self.assertFalse(mod14.validate_pilot_claim(claim))

    def test_control_cites_timing_kind_admitted(self):
        claim = {"cites_pilot_output": True, "kind": "timing"}
        self.assertTrue(mod14.validate_pilot_claim(claim))

    def test_control_empty_claim_admitted(self):
        self.assertTrue(mod14.validate_pilot_claim({}))

    def test_control_non_dict_claim_refused(self):
        self.assertFalse(mod14.validate_pilot_claim("claim"))


class TestR19010OutsideCallNumberMark(unittest.TestCase):

    def test_storing_five_lying_equality_refused(self):
        with self.assertRaises(NamedShellFailure):
            _outside_outcome(EqTrueInt(5))

    def test_storing_one_false_equality_present(self):
        self.assertEqual(
            _outside_outcome(EqFalseInt(1)), "outside calls present")

    def test_storing_one_raising_equality_present(self):
        self.assertEqual(
            _outside_outcome(EqRaisingInt(1)), "outside calls present")

    def test_storing_five_raising_equality_refused(self):
        with self.assertRaises(NamedShellFailure):
            _outside_outcome(EqRaisingInt(5))

    def test_shell_carriage_raising_equality_present(self):
        carriage = mod14.run_command("outside_call_check", {
            "dependency_manifest": {"entries": []},
            "call_log": {"calls": [
                {"outside_call": EqRaisingInt(1)}]},
        })
        self.assertEqual(
            carriage.get("outcome"), "outside calls present")

    def test_control_plain_one_present(self):
        self.assertEqual(_outside_outcome(1), "outside calls present")

    def test_control_plain_zero_no_outside(self):
        self.assertEqual(_outside_outcome(0), "no outside calls read")

    def test_control_plain_five_refused(self):
        with self.assertRaises(NamedShellFailure):
            _outside_outcome(5)

    def test_control_bool_true_present(self):
        self.assertEqual(
            _outside_outcome(True), "outside calls present")

    def test_control_text_true_present(self):
        self.assertEqual(
            _outside_outcome("true"), "outside calls present")


class TestR19034ErrorCarriageVarsLoop(unittest.TestCase):

    def _armed_failure(self, extra_plain=False):
        failure = ValueError("plain failure")
        if extra_plain:
            failure.note = "kept"
        key = ArmedHashStr("odd_field")
        failure.__dict__[key] = "odd value"
        key.armed = True
        return failure

    def test_armed_hash_key_carriage_produced(self):
        carriage = mod14.error_carriage(self._armed_failure())
        self.assertTrue(carriage["operator_sees_failure"])
        self.assertFalse(carriage["swallowed"])
        self.assertEqual(
            carriage["failure"], "ValueError: plain failure")

    def test_armed_hash_key_plain_field_still_carried(self):
        carriage = mod14.error_carriage(
            self._armed_failure(extra_plain=True))
        self.assertEqual(carriage.get("note"), "kept")
        self.assertTrue(carriage["operator_sees_failure"])

    def test_control_plain_extra_attribute_carried(self):
        failure = ValueError("plain failure")
        failure.note = "kept"
        carriage = mod14.error_carriage(failure)
        self.assertEqual(carriage.get("note"), "kept")
        self.assertEqual(
            carriage["failure"], "ValueError: plain failure")

    def test_control_named_failure_carried(self):
        carriage = mod14.error_carriage(
            NamedShellFailure("named boom"), run_id="r1", stage="s1")
        self.assertEqual(carriage["run_id"], "r1")
        self.assertTrue(carriage["operator_sees_failure"])


class TestR19035PilotRunNonDictDelivery(unittest.TestCase):

    def test_list_artefact_copied_apart(self):
        artefact = [1, [2, 3]]
        record = mod14.pilot_run("timing", artefact)
        self.assertIsNot(record["figure"], artefact)
        self.assertIsNot(record["figure"][1], artefact[1])
        artefact[1].append(99)
        self.assertEqual(record["figure"], [1, [2, 3]])
        record["figure"][1].append(7)
        self.assertEqual(artefact, [1, [2, 3, 99]])

    def test_bytearray_artefact_copied_apart(self):
        artefact = bytearray(b"abc")
        record = mod14.pilot_run("timing", artefact)
        self.assertIsNot(record["figure"], artefact)
        self.assertEqual(bytes(record["figure"]), b"abc")
        artefact[0] = ord("z")
        self.assertEqual(bytes(record["figure"]), b"abc")

    def test_set_artefact_copied_apart(self):
        artefact = {1, 2}
        record = mod14.pilot_run("timing", artefact)
        self.assertIsNot(record["figure"], artefact)
        self.assertEqual(record["figure"], {1, 2})
        artefact.add(99)
        self.assertEqual(record["figure"], {1, 2})

    def test_tuple_artefact_copied_apart(self):
        artefact = (1, [2, 3])
        record = mod14.pilot_run("timing", artefact)
        self.assertIsNot(record["figure"], artefact)
        self.assertIsNot(record["figure"][1], artefact[1])
        artefact[1].append(99)
        self.assertEqual(record["figure"], (1, [2, 3]))

    def test_barred_entry_appended_after_run_not_carried(self):
        artefact = [{"x": 1}]
        record = mod14.pilot_run("timing", artefact)
        artefact.append({"money": 99})
        self.assertEqual(record["figure"], [{"x": 1}])

    def test_shell_list_artefact_copied_apart(self):
        artefact = [1, 2]
        record = mod14.run_command(
            "run_pilot", {"use": "timing", "artefact": artefact})
        self.assertIsNot(record["figure"], artefact)
        self.assertEqual(record["figure"], [1, 2])

    def test_control_dict_artefact_copied_apart(self):
        artefact = {"figure": [1, 2]}
        record = mod14.pilot_run("timing", artefact)
        self.assertIsNot(record, artefact)
        self.assertIsNot(record["figure"], artefact["figure"])
        self.assertEqual(record["figure"], [1, 2])

    def test_control_scalar_artefact_figure(self):
        record = mod14.pilot_run("timing", 7)
        self.assertEqual(record["figure"], 7)

    def test_control_barred_entry_before_run_refused(self):
        with self.assertRaises(NamedShellFailure):
            mod14.pilot_run("timing", [{"money": 1}])


class TestR19054WeeklyHeadlineContainerKeying(unittest.TestCase):

    def _count(self, identifiers):
        records = [{
            "week": "W1",
            "headline_unit_identifiers": identifiers,
        }]
        return mod14.weekly_headline_count(records, "W1")

    def test_two_lying_repr_lists_count_two(self):
        self.assertEqual(self._count(
            [ReprLyingList([1]), ReprLyingList([2])]), 2)

    def test_two_lying_repr_dicts_count_two(self):
        self.assertEqual(self._count(
            [ReprLyingDict({"a": 1}), ReprLyingDict({"a": 2})]), 2)

    def test_two_lying_repr_sets_count_two(self):
        self.assertEqual(self._count(
            [ReprLyingSet({1, 2}), ReprLyingSet({1, 3})]), 2)

    def test_control_two_plain_lists_count_two(self):
        self.assertEqual(self._count([[1], [2]]), 2)

    def test_control_duplicate_plain_lists_count_one(self):
        self.assertEqual(self._count([[1], [1]]), 1)

    def test_control_text_identifiers_count_two(self):
        self.assertEqual(self._count(["u1", "u2"]), 2)


class TestR19055OperatorActionBufferPath(unittest.TestCase):

    def test_bytes_flag_rule_path_allowed(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "closed run record",
            "path": b"flag rule"})
        self.assertTrue(result["allowed"])

    def test_bytearray_flag_rule_path_allowed(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "closed run record",
            "path": bytearray(b"flag rule")})
        self.assertTrue(result["allowed"])

    def test_memoryview_flag_rule_path_allowed(self):
        self.assertTrue(mod14.validate_operator_action({
            "kind": "edit", "target": "closed run record",
            "path": memoryview(b"flag rule")}))

    def test_memoryview_deletion_rule_path_allowed(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "checkpoint set",
            "path": memoryview(b"deletion rule")})
        self.assertTrue(result["allowed"])

    def test_control_plain_text_flag_rule_path_allowed(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "closed run record",
            "path": "flag rule"})
        self.assertTrue(result["allowed"])

    def test_control_plain_text_other_path_refused(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "closed run record",
            "path": "somewhere else"})
        self.assertFalse(result["allowed"])

    def test_control_buffer_other_path_refused(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "edit", "target": "closed run record",
            "path": b"somewhere else"})
        self.assertFalse(result["allowed"])
        self.assertIn("outside the flag rule path", result["reason"])

    def test_control_destructive_buffer_path_refused(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": "delete", "target": "closed run record",
            "path": b"flag rule"})
        self.assertFalse(result["allowed"])

    def test_control_bytes_kind_form_sentence(self):
        result = mod14.validate_operator_action_with_reason({
            "kind": b"edit", "target": "closed run record",
            "path": "flag rule"})
        self.assertFalse(result["allowed"])
        self.assertIn(
            "stands in a form the boundary cannot read",
            result["reason"])


if __name__ == "__main__":
    unittest.main()

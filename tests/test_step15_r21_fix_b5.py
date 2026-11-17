"""Pins for fix wave 20, Builder 5, Group 5.

Rows R20-005, R20-008, R20-009, and R20-011 of the Round 20
register: the copy, freeze, and reading family under
settlement S-1, with row R20-009 on ruling (aq).
"""

import unittest

from crucible import mod01, mod03, mod04, mod05, mod06, mod07
from crucible import mod08, mod09, mod10, mod12, mod13, mod14


class ArmedHash:
    """An element whose hash reading raises once armed."""

    armed = False

    def __hash__(self):
        if ArmedHash.armed:
            raise RuntimeError("armed hash")
        return 11

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class ArmedEqCollide:
    """A key sharing one hash whose equality raises once armed."""

    armed = False

    def __hash__(self):
        return 7

    def __eq__(self, other):
        if ArmedEqCollide.armed:
            raise RuntimeError("armed equality")
        return False

    def __ne__(self, other):
        if ArmedEqCollide.armed:
            raise RuntimeError("armed inequality")
        return True


class RaisingHashKey:
    """A dict key whose hash reading raises once armed."""

    armed = False

    def __hash__(self):
        if RaisingHashKey.armed:
            raise RuntimeError("armed hash")
        return 13

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class CollideStr(str):
    """A text key storing one text, hashing as a stated field
    name, whose equality reading raises once armed."""

    armed = False

    def __new__(cls, text, target):
        obj = str.__new__(cls, text)
        obj._target = target
        return obj

    def __hash__(self):
        return str.__hash__(self._target)

    def __eq__(self, other):
        if CollideStr.armed:
            raise RuntimeError("armed equality")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if CollideStr.armed:
            raise RuntimeError("armed inequality")
        return str.__ne__(self, other)


def _armed_set():
    ArmedHash.armed = False
    elem = ArmedHash()
    handed = {elem, "plain"}
    ArmedHash.armed = True
    return handed, elem


def _armed_frozenset():
    ArmedHash.armed = False
    elem = ArmedHash()
    handed = frozenset((elem, "plain"))
    ArmedHash.armed = True
    return handed, elem


def _colliding_dict():
    ArmedEqCollide.armed = False
    handed = {ArmedEqCollide(): 1, ArmedEqCollide(): 2}
    ArmedEqCollide.armed = True
    return handed


def _two_raising_keys():
    RaisingHashKey.armed = False
    handed = {RaisingHashKey(): "first", RaisingHashKey(): "second"}
    RaisingHashKey.armed = True
    return handed


def _one_raising_key():
    RaisingHashKey.armed = False
    handed = {RaisingHashKey(): "only"}
    RaisingHashKey.armed = True
    return handed


class _ArmedCase(unittest.TestCase):
    def tearDown(self):
        ArmedHash.armed = False
        ArmedEqCollide.armed = False
        RaisingHashKey.armed = False
        CollideStr.armed = False


class TestR20005SetLimbs(_ArmedCase):
    """Row R20-005: set and frozenset limbs of the copy helpers."""

    def _check_set(self, helper):
        handed, elem = _armed_set()
        result = helper(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))

    def _check_frozenset(self, helper):
        handed, elem = _armed_frozenset()
        result = helper(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))

    def test_mod01_set(self):
        self._check_set(mod01._guarded_copy)

    def test_mod01_frozenset(self):
        self._check_frozenset(mod01._guarded_copy)

    def test_mod03_set(self):
        self._check_set(mod03._guarded_copy)

    def test_mod03_frozenset(self):
        self._check_frozenset(mod03._guarded_copy)

    def test_mod04_set(self):
        self._check_set(mod04._guarded_copy)

    def test_mod04_frozenset(self):
        self._check_frozenset(mod04._guarded_copy)

    def test_mod06_set(self):
        self._check_set(mod06._undirected_copy)

    def test_mod06_frozenset(self):
        self._check_frozenset(mod06._undirected_copy)

    def test_mod07_set(self):
        self._check_set(mod07._stored_copy)

    def test_mod07_frozenset(self):
        self._check_frozenset(mod07._stored_copy)

    def test_mod08_set(self):
        self._check_set(mod08._undirected_copy)

    def test_mod08_frozenset(self):
        self._check_frozenset(mod08._undirected_copy)

    def test_mod09_set(self):
        self._check_set(mod09._stored_copy)

    def test_mod09_frozenset(self):
        self._check_frozenset(mod09._stored_copy)

    def test_mod10_set(self):
        self._check_set(mod10._safe_copy)

    def test_mod10_frozenset(self):
        self._check_frozenset(mod10._safe_copy)


class TestR20008CleaningWalks(_ArmedCase):
    """Row R20-008: cleaning walk assignment and constructions."""

    def test_mod04_clean_dict(self):
        result = mod04._clean_value(_colliding_dict())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), [1, 2])

    def test_mod04_clean_set(self):
        handed, elem = _armed_set()
        result = mod04._clean_value(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))

    def test_mod04_clean_frozenset(self):
        handed, elem = _armed_frozenset()
        result = mod04._clean_value(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))

    def test_mod05_panel_dict(self):
        result = mod05._panel_clean(_colliding_dict())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), [1, 2])

    def test_mod05_panel_set(self):
        handed, elem = _armed_set()
        result = mod05._panel_clean(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))

    def test_mod05_panel_frozenset(self):
        handed, elem = _armed_frozenset()
        result = mod05._panel_clean(handed)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)
        self.assertTrue(any(item is elem for item in result))


class TestR20009FreezeFallback(_ArmedCase):
    """Row R20-009, on ruling (aq): two raising keys, no drop."""

    def _check_two(self, helper):
        result = helper(_two_raising_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["first", "second"])

    def _check_one(self, helper):
        result = helper(_one_raising_key())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.values()), ["only"])

    def test_mod01_two_keys(self):
        self._check_two(mod01._guarded_copy)

    def test_mod05_two_keys(self):
        self._check_two(mod05._freeze)

    def test_mod12_two_keys(self):
        self._check_two(mod12._freeze)

    def test_mod13_two_keys(self):
        self._check_two(mod13._freeze)

    def test_mod14_two_keys(self):
        self._check_two(mod14._freeze)

    def test_mod01_one_key_control(self):
        self._check_one(mod01._guarded_copy)

    def test_mod05_one_key_control(self):
        self._check_one(mod05._freeze)

    def test_mod12_one_key_control(self):
        self._check_one(mod12._freeze)

    def test_mod13_one_key_control(self):
        self._check_one(mod13._freeze)

    def test_mod14_one_key_control(self):
        self._check_one(mod14._freeze)


class TestR20011StoredPairsReadings(_ArmedCase):
    """Row R20-011: the _get form family at MOD-04, MOD-05, MOD-07."""

    def test_mod05_get_helper(self):
        CollideStr.armed = False
        record = {
            CollideStr("zzz-other", "agent_identifier"): 0,
            "agent_identifier": "agent-1",
        }
        CollideStr.armed = True
        self.assertEqual(
            mod05._get(record, "agent_identifier", "agent"), "agent-1")

    def test_mod05_work_credit(self):
        CollideStr.armed = False
        event = {
            CollideStr("zzz-other", "agent_identifier"): 0,
            "agent_identifier": "agent-1",
            "accepted": True,
        }
        CollideStr.armed = True
        result = mod05.work_credit([event])
        self.assertEqual(result["counters"]["agent-1"]["submitted"], 1)
        self.assertEqual(result["counters"]["agent-1"]["accepted"], 1)

    def test_mod05_aggregate_reputation(self):
        CollideStr.armed = False
        inputs = {
            CollideStr("zzz-other", "agent_identifier"): 0,
            "agent_identifier": "agent-1",
            "accepted_work": 2,
            "penalties": 0,
            "vouches_received": [],
        }
        CollideStr.armed = True
        result = mod05.aggregate_reputation(inputs)
        self.assertEqual(result["agent_identifier"], "agent-1")
        self.assertEqual(result["score"], 2)

    def test_mod07_bget_helper(self):
        CollideStr.armed = False
        record = {
            CollideStr("zzz-other", "edges"): 0,
            "edges": ["edge-1"],
        }
        CollideStr.armed = True
        self.assertEqual(mod07._bget(record, "edges"), ["edge-1"])

    def test_mod07_validate_dependency_record(self):
        CollideStr.armed = False
        record = {
            CollideStr("zzz-other", "edges"): 0,
            "edges": [],
            "joint_dependent": "MOD-07",
        }
        CollideStr.armed = True
        self.assertTrue(mod07.validate_dependency_record(record))

    def test_mod04_state_field_helper(self):
        CollideStr.armed = False
        state = {
            CollideStr("zzz-other", "day"): 0,
            "day": 3,
            "agent_identifier": "agent-1",
        }
        CollideStr.armed = True
        self.assertEqual(
            mod04._state_field(state, ["day", "simulated_day"]), 3)

    def test_mod04_project_detection_input(self):
        CollideStr.armed = False
        state = {
            CollideStr("zzz-other", "agent_identifier"): 0,
            "agent_identifier": "agent-1",
            "day": 3,
            "feature_values": {},
            "rule_records": [],
        }
        CollideStr.armed = True
        result = mod04.project_detection_input(state)
        self.assertEqual(result["agent_identifier"], "agent-1")
        self.assertEqual(result["day"], 3)


class TestControls(_ArmedCase):
    """Plain controls, passing on pristine and cured code alike."""

    def test_plain_set_copy_mod01(self):
        self.assertEqual(mod01._guarded_copy({1, 2}), {1, 2})

    def test_plain_frozenset_copy_mod03(self):
        self.assertEqual(
            mod03._guarded_copy(frozenset((1, 2))), frozenset((1, 2)))

    def test_plain_dict_clean_mod04(self):
        self.assertEqual(mod04._clean_value({"a": 1}), {"a": 1})

    def test_plain_panel_clean_mod05(self):
        self.assertEqual(mod05._panel_clean({"a": 1}), {"a": 1})

    def test_plain_get_mod05(self):
        self.assertEqual(
            mod05._get({"agent_identifier": "a"}, "agent_identifier"),
            "a")

    def test_plain_bget_mod07(self):
        self.assertEqual(mod07._bget({"edges": [1]}, "edges"), [1])

    def test_plain_state_field_mod04(self):
        self.assertEqual(
            mod04._state_field({"day": 5}, ["day"]), 5)


if __name__ == "__main__":
    unittest.main()

"""Step 15 rerun fix wave 4 pins, seat 9. MOD-13.

Item R4-030 limb a only: the comparison counting in _strict_eq
stands on the containers only basis of R3-056, so a chain of 101
containers stands within the bound of 100 and a chain of 102
stands past it, at the locus, through replay_check and
resume_check, and in dict key position.
"""
import unittest

import crucible.mod13 as mod13


def _list_chain(length, leaf):
    value = leaf
    for _ in range(length):
        value = [value]
    return value


def _tuple_chain(length, leaf):
    value = leaf
    for _ in range(length):
        value = (value,)
    return value


def _dict_chain(length, leaf):
    value = leaf
    for _ in range(length):
        value = {"k": value}
    return value


def _frozenset_chain(length, leaf):
    value = leaf
    for _ in range(length):
        value = frozenset([value])
    return value


def _mixed_chain(length, leaf):
    value = leaf
    for index in range(length):
        step = index % 3
        if step == 0:
            value = [value]
        elif step == 1:
            value = (value,)
        else:
            value = {"k": value}
    return value


def _pair():
    fields = list(mod13.ac1_field_list())
    facts = {field: "value for " + field for field in fields}
    facts["headline_unit"] = {"unit": "unit-1"}
    first = dict(facts)
    second = dict(facts)
    verdicts = {
        "first verdict state after resume": "verdict-a",
        "run close": "verdict-b",
    }
    first["detection_verdicts"] = dict(verdicts)
    second["detection_verdicts"] = dict(verdicts)
    return fields, first, second


class TestR4030ListChainAtLocus(unittest.TestCase):
    def test_list_chain_101_agrees(self):
        self.assertTrue(mod13._strict_eq(
            _list_chain(101, "leaf"), _list_chain(101, "leaf")))

    def test_list_chain_101_differing_leaf_disagrees_without_raising(self):
        self.assertFalse(mod13._strict_eq(
            _list_chain(101, "leaf"), _list_chain(101, "other")))

    def test_list_chain_100_agrees_control(self):
        self.assertTrue(mod13._strict_eq(
            _list_chain(100, "leaf"), _list_chain(100, "leaf")))

    def test_list_chain_102_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _list_chain(102, "leaf"), _list_chain(102, "leaf"))

    def test_list_chain_102_differing_leaf_still_refused(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _list_chain(102, "leaf"), _list_chain(102, "other"))


class TestR4030OtherContainerChainsAtLocus(unittest.TestCase):
    def test_tuple_chain_101_agrees(self):
        self.assertTrue(mod13._strict_eq(
            _tuple_chain(101, "leaf"), _tuple_chain(101, "leaf")))

    def test_tuple_chain_102_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _tuple_chain(102, "leaf"), _tuple_chain(102, "leaf"))

    def test_dict_chain_101_agrees(self):
        self.assertTrue(mod13._strict_eq(
            _dict_chain(101, "leaf"), _dict_chain(101, "leaf")))

    def test_dict_chain_102_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _dict_chain(102, "leaf"), _dict_chain(102, "leaf"))

    def test_frozenset_chain_101_agrees(self):
        self.assertTrue(mod13._strict_eq(
            _frozenset_chain(101, "leaf"),
            _frozenset_chain(101, "leaf")))

    def test_frozenset_chain_102_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _frozenset_chain(102, "leaf"),
                _frozenset_chain(102, "leaf"))

    def test_mixed_chain_101_agrees(self):
        self.assertTrue(mod13._strict_eq(
            _mixed_chain(101, "leaf"), _mixed_chain(101, "leaf")))

    def test_mixed_chain_102_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(
                _mixed_chain(102, "leaf"), _mixed_chain(102, "leaf"))


class TestR4030DictKeyPosition(unittest.TestCase):
    def test_tuple_chain_key_100_in_record_dict_agrees(self):
        first = {_tuple_chain(100, "x"): 1}
        second = {_tuple_chain(100, "x"): 1}
        self.assertTrue(mod13._strict_eq(first, second))

    def test_tuple_chain_key_100_in_record_dict_differing_value(self):
        first = {_tuple_chain(100, "x"): 1}
        second = {_tuple_chain(100, "x"): 2}
        self.assertFalse(mod13._strict_eq(first, second))

    def test_tuple_chain_key_99_in_record_dict_agrees_control(self):
        first = {_tuple_chain(99, "x"): 1}
        second = {_tuple_chain(99, "x"): 1}
        self.assertTrue(mod13._strict_eq(first, second))

    def test_tuple_chain_key_101_in_record_dict_refused(self):
        first = {_tuple_chain(101, "x"): 1}
        second = {_tuple_chain(101, "x"): 1}
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(first, second)


class TestR4030ThroughReplayCheck(unittest.TestCase):
    def test_replay_list_chain_101_deterministic(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(101, "leaf")
        second[fields[0]] = _list_chain(101, "leaf")
        check = mod13.replay_check(first, second)
        self.assertTrue(check["deterministic"])

    def test_replay_list_chain_101_differing_leaf_not_deterministic(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(101, "leaf")
        second[fields[0]] = _list_chain(101, "other")
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])

    def test_replay_list_chain_102_refused_in_named_form(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(102, "leaf")
        second[fields[0]] = _list_chain(102, "leaf")
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.replay_check(first, second)

    def test_replay_tuple_chain_key_100_in_field_dict(self):
        fields, first, second = _pair()
        first[fields[0]] = {_tuple_chain(100, "x"): 1}
        second[fields[0]] = {_tuple_chain(100, "x"): 1}
        check = mod13.replay_check(first, second)
        self.assertTrue(check["deterministic"])


class TestR4030ThroughResumeCheck(unittest.TestCase):
    def test_resume_list_chain_101_equal_in_scope(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(101, "leaf")
        second[fields[0]] = _list_chain(101, "leaf")
        check = mod13.resume_check(first, second)
        self.assertTrue(check["equal_in_scope"])

    def test_resume_list_chain_101_differing_leaf_not_equal(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(101, "leaf")
        second[fields[0]] = _list_chain(101, "other")
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])

    def test_resume_list_chain_102_refused_in_named_form(self):
        fields, first, second = _pair()
        first[fields[0]] = _list_chain(102, "leaf")
        second[fields[0]] = _list_chain(102, "leaf")
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.resume_check(first, second)

    def test_resume_tuple_chain_key_100_in_field_dict(self):
        fields, first, second = _pair()
        first[fields[0]] = {_tuple_chain(100, "x"): 1}
        second[fields[0]] = {_tuple_chain(100, "x"): 1}
        check = mod13.resume_check(first, second)
        self.assertTrue(check["equal_in_scope"])


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 6, seat 9: MOD-13 cure rows R6-037 and
R6-019 (MOD-13 limb), with the standing watch on MOD-13 and
MOD-16 labelled as evidence.

Cure pins record the charged defect forms first hand on the
merged tree: each fails against the unmodified module and
passes against the cured copy, with lawful controls passing
both ways. Watch pins stand labelled as evidence only: they
record a standing and claim no pass for any carried finding.
"""

import time
import unittest

from crucible import mod13
from crucible import mod16


_MONEY_DICT = {"amount": 10, "currency": "USD"}


class _ListMoneySet(set):
    def __new__(cls, iterable=()):
        if isinstance(iterable, list):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _ListMoneyFrozenset(frozenset):
    def __new__(cls, iterable=()):
        if isinstance(iterable, list):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class TestFreezeMemoR6037(unittest.TestCase):
    """R6-037: the set, frozenset, and tuple branches of _freeze
    carry memo entries in the stated form."""

    def test_shared_set_part_is_one_copy(self):
        part = {1, 2}
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])
        self.assertEqual(copied["a"], {1, 2})

    def test_shared_frozenset_part_is_one_copy(self):
        part = frozenset((1, 2))
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])
        self.assertEqual(copied["a"], frozenset((1, 2)))

    def test_shared_set_holding_tuple_is_one_copy(self):
        part = {(7, 8)}
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])

    def test_shared_frozenset_in_tuple_is_one_copy(self):
        part = frozenset((9,))
        copied = mod13._freeze((part, part))
        self.assertIs(copied[0], copied[1])

    def test_cyclic_tuple_through_list_is_one_copy(self):
        lst = []
        tup = (lst,)
        lst.append(tup)
        copied = mod13._freeze(tup)
        self.assertIs(copied[0][0], copied)

    def test_cyclic_tuple_through_dict_is_one_copy(self):
        holder = {}
        tup = (holder,)
        holder["t"] = tup
        copied = mod13._freeze(tup)
        self.assertIs(copied[0]["t"], copied)

    def test_extend_history_shared_set_is_one_copy(self):
        part = {5, 6}
        history = [{
            "run_id": "r1", "rule_set_version": "v1",
            "a": part, "b": part,
        }]
        result = mod13.extend_history(history, {"note": "next"})
        self.assertIs(result[0]["a"], result[0]["b"])

    # Controls: passing before and after the cure.

    def test_shared_dict_part_is_one_copy(self):
        part = {"x": 1}
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])

    def test_shared_list_part_is_one_copy(self):
        part = [1, 2]
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])

    def test_shared_tuple_part_is_one_copy(self):
        part = (1, 2)
        copied = mod13._freeze({"a": part, "b": part})
        self.assertIs(copied["a"], copied["b"])

    def test_cyclic_dict_and_list_controls(self):
        cyc_dict = {}
        cyc_dict["self"] = cyc_dict
        copied_dict = mod13._freeze(cyc_dict)
        self.assertIs(copied_dict["self"], copied_dict)
        cyc_list = []
        cyc_list.append(cyc_list)
        copied_list = mod13._freeze(cyc_list)
        self.assertIs(copied_list[0], copied_list)

    def test_plain_values_control(self):
        copied = mod13._freeze(
            {"s": {1, 2}, "f": frozenset((1, 2)), "t": (3, 4),
             "l": [5], "d": {"x": 6}})
        self.assertEqual(copied, {"s": {1, 2}, "f": frozenset((1, 2)),
                                  "t": (3, 4), "l": [5], "d": {"x": 6}})


def _shared_list_dag(depth, leaf=0):
    value = [leaf]
    for _ in range(depth):
        value = [value, value]
    return value


def _shared_dict_dag(depth, leaf=0):
    value = {"x": leaf}
    for _ in range(depth):
        value = {"a": value, "b": value}
    return value


def _shared_tuple_dag(depth, leaf=0):
    value = (leaf,)
    for _ in range(depth):
        value = (value, value)
    return value


def _chain(containers, leaf=1):
    value = leaf
    for _ in range(containers):
        value = [value]
    return value


def _wrapped(part, wraps):
    value = part
    for _ in range(wraps):
        value = [value]
    return value


class TestStrictEqRewalkR6019(unittest.TestCase):
    """R6-019, MOD-13 limb: _strict_eq carries a walked standing
    across paths, keyed so a deeper reach stands judged at its
    own depth."""

    def test_shared_list_dag_depth20_completes(self):
        first = _shared_list_dag(20)
        second = _shared_list_dag(20)
        start = time.perf_counter()
        result = mod13._strict_eq(first, second)
        elapsed = time.perf_counter() - start
        self.assertTrue(result)
        self.assertLess(elapsed, 2.0)

    def test_shared_dict_dag_depth18_completes(self):
        first = _shared_dict_dag(18)
        second = _shared_dict_dag(18)
        start = time.perf_counter()
        result = mod13._strict_eq(first, second)
        elapsed = time.perf_counter() - start
        self.assertTrue(result)
        self.assertLess(elapsed, 2.0)

    def test_shared_tuple_dag_depth18_completes(self):
        first = _shared_tuple_dag(18)
        second = _shared_tuple_dag(18)
        start = time.perf_counter()
        result = mod13._strict_eq(first, second)
        elapsed = time.perf_counter() - start
        self.assertTrue(result)
        self.assertLess(elapsed, 2.0)

    # Controls: passing before and after the cure. The depth
    # controls also fail a walked standing keyed by identity
    # alone: the shallow first past bound forms must still
    # stand refused.

    def test_shared_unequal_control(self):
        self.assertFalse(mod13._strict_eq(
            _shared_list_dag(10, leaf=1), _shared_list_dag(10, leaf=2)))

    def test_cyclic_controls(self):
        first = []
        first.append(first)
        first.append(1)
        same = []
        same.append(same)
        same.append(1)
        different = []
        different.append(different)
        different.append(2)
        self.assertTrue(mod13._strict_eq(first, same))
        self.assertFalse(mod13._strict_eq(first, different))

    def test_depth_within_bound_shared_both_orders(self):
        for order in ("shallow_first", "deep_first"):
            shared_a = _chain(6)
            deep_a = _wrapped(shared_a, 94)
            shared_b = _chain(6)
            deep_b = _wrapped(shared_b, 94)
            root_a = [shared_a, deep_a] if order == "shallow_first" else [deep_a, shared_a]
            root_b = [shared_b, deep_b] if order == "shallow_first" else [deep_b, shared_b]
            self.assertTrue(mod13._strict_eq(root_a, root_b))

    def test_depth_past_bound_shared_both_orders(self):
        for wraps in (95, 96):
            for order in ("shallow_first", "deep_first"):
                shared_a = _chain(6)
                deep_a = _wrapped(shared_a, wraps)
                shared_b = _chain(6)
                deep_b = _wrapped(shared_b, wraps)
                root_a = [shared_a, deep_a] if order == "shallow_first" else [deep_a, shared_a]
                root_b = [shared_b, deep_b] if order == "shallow_first" else [deep_b, shared_b]
                with self.assertRaises(mod13.NamedReplicationFailure):
                    mod13._strict_eq(root_a, root_b)

    def test_plain_nested_controls(self):
        self.assertTrue(mod13._strict_eq(
            {"a": [1, (2, 3), {4, 5}]}, {"a": [1, (2, 3), {4, 5}]}))
        self.assertFalse(mod13._strict_eq({"a": 1}, {"a": 2}))
        self.assertTrue(mod13._strict_eq(
            _chain(101), _chain(101)))
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(_chain(102), _chain(102))


class TestWatchEvidence(unittest.TestCase):
    """Watch pins: evidence only. No pass stands claimed for
    F-LE-09 or F-LE-10 by any pin in this class, and no carried
    finding stands discharged by them."""

    def test_watch_r5040_list_fed_set_at_locus(self):
        copied = mod13._freeze({"wrap": _ListMoneySet((1, 2))})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertIsInstance(copied["wrap"], set)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_watch_r5040_list_fed_frozenset_through_extend_history(self):
        history = [{"run_id": "r1", "rule_set_version": "v1"}]
        segment = {"payload": _ListMoneyFrozenset((1, 2))}
        result = mod13.extend_history(history, segment)
        self.assertNotEqual(result[1]["payload"], _MONEY_DICT)
        self.assertIsInstance(result[1]["payload"], frozenset)
        self.assertEqual(set(result[1]["payload"]), {1, 2})

    def test_watch_mod16_screening_and_validation_exercise(self):
        for run_class in ("screening", "validation"):
            result = mod16.exercise_run_class(run_class)
            self.assertTrue(result["exercised_end_to_end"])
            self.assertTrue(result["read_back_matches"])
            self.assertTrue(result["driven_through_wired_product"])

    def test_watch_mod16_companion_exercise(self):
        both = mod16.exercise_confirmation_and_headline()
        self.assertTrue(both["confirmation"]["exercised_end_to_end"])
        self.assertTrue(both["confirmation"]["read_back_matches"])
        self.assertTrue(both["headline"]["exercised_end_to_end"])
        self.assertTrue(both["headline"]["unit_built"])
        self.assertTrue(both["headline"]["read_back_matches"])
        lineage = both["confirmation"]["settings_lineage_record"]
        self.assertEqual(lineage["form"], "Form 32")
        self.assertTrue(lineage["completed"])

    def test_watch_freeze_chain_2000_standing_as_on_merged_tree(self):
        # Evidence only: on the merged tree and on this cured
        # copy alike, _freeze on a chain of 2,000 containers
        # raises a bare RecursionError. The copy act states no
        # depth form in the records this seat read, so this pin
        # records the standing and grades nothing.
        deep = 0
        for _ in range(2000):
            deep = [deep]
        with self.assertRaises(RecursionError):
            mod13._freeze(deep)

    # The F-LE-09 alias inventory stands re-derived by probe in
    # this seat paper, as evidence only, on the form of the fix
    # wave 5 watch: no pin in this file asserts its count, and
    # no pass stands claimed for F-LE-09.


if __name__ == "__main__":
    unittest.main()

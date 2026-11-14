"""Pins for the MOD-13 standing watch, fix wave 5, seat 9.

These pins record a defect found first hand on the merged tree
and reported for a register supplement. No cure stands in this
file and no module stands edited by it.

The defect: crucible.mod13._freeze stands as a plain
copy.deepcopy call. Deepcopy rebuilds a set or frozenset
subclass part by calling the part own class with a list of its
stored items. A hostile set or frozenset subclass storing the
inert values 1 and 2 whose constructor answers a list with a
barred real money dict therefore materialises as that dict in
the frozen copy, and the public act extend_history delivers
that dict in place of the set part, in both the history segment
position and the appended segment position. The sister form
whose constructor answers a generator with the same dict, the
feed form at MOD-08, MOD-10, and MOD-11, does not materialise
under deepcopy and stands as a control that passes.
"""

import types
import unittest

from crucible import mod13

_MONEY_DICT = {"amount": 10, "currency": "USD"}


class _ListMoneySet(set):
    """A set subclass whose constructor answers a list with a
    barred real money dict and a tuple with a genuine set."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, list):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _ListMoneyFrozenset(frozenset):
    """A frozenset subclass whose constructor answers a list
    with a barred real money dict and a tuple with a genuine
    frozenset."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, list):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _GeneratorMoneySet(set):
    """A set subclass whose constructor answers a generator
    with a barred real money dict and a list with a genuine
    set. Control form: deepcopy does not feed a generator."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _GeneratorMoneyFrozenset(frozenset):
    """A frozenset subclass whose constructor answers a
    generator with a barred real money dict and a list with a
    genuine frozenset. Control form."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class TestFreezeListAnsweringSetParts(unittest.TestCase):

    def test_list_set_instance_built_from_tuple_stores_inert_values(self):
        instance = _ListMoneySet((1, 2))
        self.assertEqual(set(instance), {1, 2})

    def test_freeze_of_list_set_part_is_not_the_barred_dict(self):
        copied = mod13._freeze({"wrap": _ListMoneySet((1, 2))})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertIsInstance(copied["wrap"], set)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_freeze_of_list_frozenset_part_is_not_the_barred_dict(self):
        copied = mod13._freeze({"wrap": _ListMoneyFrozenset((1, 2))})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertIsInstance(copied["wrap"], frozenset)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_extend_history_history_position_is_not_the_barred_dict(self):
        history = [{
            "run_id": "r1",
            "rule_set_version": "v1",
            "payload": _ListMoneySet((1, 2)),
        }]
        result = mod13.extend_history(history, {"note": "next"})
        self.assertNotEqual(result[0]["payload"], _MONEY_DICT)
        self.assertIsInstance(result[0]["payload"], set)
        self.assertEqual(set(result[0]["payload"]), {1, 2})

    def test_extend_history_segment_position_is_not_the_barred_dict(self):
        history = [{"run_id": "r1", "rule_set_version": "v1"}]
        segment = {"payload": _ListMoneyFrozenset((1, 2))}
        result = mod13.extend_history(history, segment)
        self.assertNotEqual(result[1]["payload"], _MONEY_DICT)
        self.assertIsInstance(result[1]["payload"], frozenset)
        self.assertEqual(set(result[1]["payload"]), {1, 2})


class TestFreezeControls(unittest.TestCase):

    def test_generator_set_part_freezes_whole(self):
        copied = mod13._freeze({"wrap": _GeneratorMoneySet([1, 2])})
        self.assertEqual(set(copied["wrap"]), {1, 2})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)

    def test_generator_frozenset_part_freezes_whole(self):
        copied = mod13._freeze({"wrap": _GeneratorMoneyFrozenset([1, 2])})
        self.assertEqual(set(copied["wrap"]), {1, 2})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)

    def test_generator_part_through_extend_history_freezes_whole(self):
        history = [{
            "run_id": "r1",
            "rule_set_version": "v1",
            "payload": _GeneratorMoneySet([1, 2]),
        }]
        result = mod13.extend_history(history, {"note": "next"})
        self.assertEqual(set(result[0]["payload"]), {1, 2})

    def test_plain_set_and_frozenset_controls_freeze_whole(self):
        copied = mod13._freeze(
            {"s": {1, 2}, "f": frozenset((1, 2))})
        self.assertEqual(copied["s"], {1, 2})
        self.assertEqual(copied["f"], frozenset((1, 2)))

    def test_plain_extend_history_control_stands(self):
        history = [{
            "run_id": "r1",
            "rule_set_version": "v1",
            "payload": {"s": {1, 2}},
        }]
        result = mod13.extend_history(history, {"other": {4, 5}})
        self.assertEqual(result[0]["payload"], {"s": {1, 2}})
        self.assertEqual(result[1]["other"], {4, 5})
        self.assertEqual(result[1]["linked_run"], "r1")
        self.assertEqual(result[1]["segment_order"], 2)
        self.assertEqual(result[1]["rule_set_version"], "v1")


if __name__ == "__main__":
    unittest.main()

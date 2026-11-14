"""Pins for fix wave 6, completion seat b19.

Row R6-019, MOD-07 limb: the _copy_guard walk in crucible/mod07.py
carries a walked standing across paths, keyed by container identity
and depth, so a container shared by two siblings stands walked once
for each depth it stands at, and a reach at a greater depth stands
judged at its own depth against the stated depth bound of 100
(the depth limb row R6-020 states, as it applies at this locus).

The defect pins state the walked count through a counting wrapper
around the module walk, in place of a wall clock assertion, beside
one timing pin in the sister form. The control pins state the
guard copying behaviour on lawful shapes: shared references stand
admitted, cycles stand refused in named form, and the depth bound
stands judged at the depth of each reach, in both child orders.
"""

import time
import unittest

from crucible import mod07


def _shared_list_dag(depth):
    value = [0]
    for _ in range(depth):
        value = [value, value]
    return value


def _shared_dict_dag(depth):
    value = {"leaf": 0}
    for _ in range(depth):
        value = {"a": value, "b": value}
    return value


def _shared_tuple_dag(depth):
    value = (0,)
    for _ in range(depth):
        value = (value, value)
    return value


def _chain(wraps):
    value = []
    for _ in range(wraps):
        value = [value]
    return value


def _shared_chain():
    value = ["leaf"]
    for _ in range(5):
        value = [value]
    return value


def _wrapped(value, wraps):
    for _ in range(wraps):
        value = [value]
    return value


def _counted_calls(value):
    original = mod07._copy_guard
    calls = {"count": 0}

    def counting(*args, **kwargs):
        calls["count"] += 1
        return original(*args, **kwargs)

    mod07._copy_guard = counting
    try:
        counting(value)
    finally:
        mod07._copy_guard = original
    return calls["count"]


class TestCopyGuardRewalkR6019(unittest.TestCase):

    def test_shared_list_dag_walked_count_depth16(self):
        calls = _counted_calls(_shared_list_dag(16))
        self.assertLessEqual(calls, 100)

    def test_shared_dict_dag_walked_count_depth16(self):
        calls = _counted_calls(_shared_dict_dag(16))
        self.assertLessEqual(calls, 200)

    def test_shared_tuple_dag_walked_count_depth16(self):
        calls = _counted_calls(_shared_tuple_dag(16))
        self.assertLessEqual(calls, 100)

    def test_shared_list_dag_depth20_completes_quickly(self):
        start = time.perf_counter()
        mod07._copy_guard(_shared_list_dag(20))
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 2.0)

    def test_shared_dag_through_public_surface_counted(self):
        effect = {"kind": "lien", "value": _shared_list_dag(10)}
        original = mod07._copy_guard
        calls = {"count": 0}

        def counting(*args, **kwargs):
            calls["count"] += 1
            return original(*args, **kwargs)

        mod07._copy_guard = counting
        try:
            report = mod07.seam_effect_report(effect)
        finally:
            mod07._copy_guard = original
        self.assertLessEqual(calls["count"], 100)
        self.assertEqual(report["reporting"], mod07.INTERIM_REPORTING)
        self.assertEqual(report["lien_state"], mod07.COMPUTED_NOT_SETTLED)
        self.assertEqual(report["value"], effect["value"])
        self.assertIsNot(report["value"], effect["value"])

    # Controls: passing before and after the cure.

    def test_shared_references_admitted(self):
        shared_list = [1, {"inner": (2, 3)}]
        shared_dict = {"shared": shared_list, "again": shared_list}
        value = [shared_dict, shared_dict, (shared_list, shared_list)]
        mod07._copy_guard(value)
        mod07._copy_guard({"one": shared_list, "two": shared_list})
        mod07._copy_guard([{4, 5}, {4, 5}])

    def test_public_copy_surfaces_on_shared_shapes(self):
        shared = ["mark", {"nested": [1, 2]}]
        approval_input = {
            "approver": "Project Manager",
            "choice_identifier": "choice-1",
            "effects": [shared, shared],
            "standing": "approved",
        }
        choice = mod07.make_adapter_choice(
            "choice-1", "reading", "point", "text-1", "variant-1",
            dependence_marks=[shared, shared],
            approval=approval_input,
            drives=[{"level": "decision", "kind": "computed value"}],
            ruling_references=[shared])
        self.assertEqual(choice["recorded_as"], "adapter choice")
        self.assertEqual(
            choice["approval"]["effects"], [shared, shared])
        self.assertIsNot(choice["approval"], approval_input)
        self.assertEqual(choice["approval"], approval_input)
        log_entry = mod07.interpretation_log_entry(choice)
        run_entry = mod07.run_record_entry(choice)
        self.assertEqual(
            log_entry["choice_identifier"], "choice-1")
        self.assertEqual(
            run_entry["choice_identifier"], "choice-1")
        report = mod07.slash_outcome_report(
            {"value": _shared_list_dag(6)})
        self.assertEqual(report["effect"], "slash")
        self.assertEqual(report["value"], _shared_list_dag(6))

    def test_cycles_refused_in_named_form(self):
        list_cycle = []
        list_cycle.append(list_cycle)
        dict_cycle = {}
        dict_cycle["self"] = dict_cycle
        mutual_a = []
        mutual_b = {"a": mutual_a}
        mutual_a.append(mutual_b)
        behind_shared = []
        behind_shared.append(behind_shared)
        shapes = (
            list_cycle,
            dict_cycle,
            mutual_a,
            [behind_shared, behind_shared],
            {"first": list_cycle, "second": list_cycle},
        )
        for shape in shapes:
            with self.subTest(shape=type(shape).__name__):
                with self.assertRaises(ValueError) as caught:
                    mod07._copy_guard(shape)
                self.assertIn("cycle", str(caught.exception))

    def test_depth_chain_controls(self):
        mod07._copy_guard(_chain(100))
        for wraps in (101, 102):
            with self.subTest(wraps=wraps):
                with self.assertRaises(ValueError) as caught:
                    mod07._copy_guard(_chain(wraps))
                self.assertIn(
                    "deeper than the stated bound",
                    str(caught.exception))

    def test_depth_shared_within_bound_both_orders(self):
        for order in ("shallow_first", "deep_first"):
            with self.subTest(order=order):
                shared = _shared_chain()
                deep = _wrapped(shared, 94)
                root = [shared, deep] if order == "shallow_first" \
                    else [deep, shared]
                mod07._copy_guard(root)

    def test_depth_shared_past_bound_both_orders(self):
        for wraps in (95, 96):
            for order in ("shallow_first", "deep_first"):
                with self.subTest(wraps=wraps, order=order):
                    shared = _shared_chain()
                    deep = _wrapped(shared, wraps)
                    root = [shared, deep] if order == "shallow_first" \
                        else [deep, shared]
                    with self.assertRaises(ValueError):
                        mod07._copy_guard(root)

    def test_plain_shapes_controls(self):
        mod07._copy_guard(None)
        mod07._copy_guard(0)
        mod07._copy_guard("text")
        mod07._copy_guard([])
        mod07._copy_guard({})
        mod07._copy_guard(
            {"a": [1, (2, 3), {4, 5}], "b": {"c": [None, True]}})


if __name__ == "__main__":
    unittest.main()

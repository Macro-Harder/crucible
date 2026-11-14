"""Pins for fix wave 6, Builder 4, MOD-05 limbs of rows R6-007,
R6-010, R6-011, and R6-019.

R6-007: the MOD-05 _freeze copy act stands as a plain
copy.deepcopy call, so a set or frozenset subclass part storing
inert items stands rebuilt by its own constructor into a barred
dict, delivered through graph_snapshot, and a nested object
whose copy protocol so answers stands materialised the same way.

R6-010: the per character option count at MOD-05 counts Greek
eta U+03B7 as two readings against one at MOD-04 and MOD-10,
while Greek theta U+03B8 counts two readings, as at MOD-04.

R6-011: MOD-05 carries a bound free combined read behind its
enumeration, so a barred key whose combined readings pass the
4096 bound stands barred at MOD-05. These pins record that
standing at MOD-05, the basis this cure takes.

R6-019: _panel_carries_barred and _panel_clean rewalk shared
containers at every path, so a container shared by two siblings
stands walked once for every path and the work grows at two to
the power of the shared depth.
"""

import time
import unittest

from crucible import mod04, mod05

BARRED_DICT = {"amount": 10, "currency": "USD"}


class ListFedSet(set):
    """A set subclass whose constructor answers a barred dict
    when it is fed a list, and a genuine set when fed a tuple."""

    def __new__(cls, items=()):
        if isinstance(items, list):
            return dict(BARRED_DICT)
        return super().__new__(cls)


class ListFedFrozenSet(frozenset):
    """The frozenset form of ListFedSet."""

    def __new__(cls, items=()):
        if isinstance(items, list):
            return dict(BARRED_DICT)
        return super().__new__(cls, items)


class GeneratorFedSet(set):
    """A set subclass whose constructor answers a genuine set
    whatever it is fed. Stands as a control both ways."""


class DeepcopyObject:
    """A plain object whose copy protocol answers with a
    barred dict."""

    def __deepcopy__(self, memo):
        return dict(BARRED_DICT)


MIXED_CORE = (
    "membe"
    + "\u0440"
    + "\u0441"
    + "\u043d"
    + "i"
    + "\u0440"
)
SHORT_I_FILLER = "\u0439" * 13
CHI_FILLER = "\u03c7" * 13

CANARY_CORE = "\u0441" + "a" + "\u043d" + "ary"
ETA = "\u03b7"
THETA = "\u03b8"
CHI = "\u03c7"


def shared_shape(depth):
    value = ["leaf"]
    for _ in range(depth):
        value = [value, value]
    return {"root": value}


def chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


class TestR6007Freeze(unittest.TestCase):

    def test_list_fed_set_subclass_freezes_as_plain_set(self):
        part = ListFedSet((1, 2))
        frozen = mod05._freeze({"wrap": part})
        self.assertEqual(frozen, {"wrap": {1, 2}})
        self.assertIs(type(frozen["wrap"]), set)

    def test_list_fed_frozenset_subclass_freezes_as_plain_frozenset(self):
        part = ListFedFrozenSet((1, 2))
        frozen = mod05._freeze({"wrap": part})
        self.assertEqual(frozen, {"wrap": frozenset({1, 2})})
        self.assertIs(type(frozen["wrap"]), frozenset)

    def test_deepcopy_object_freezes_as_itself(self):
        part = DeepcopyObject()
        frozen = mod05._freeze({"wrap": part})
        self.assertIs(frozen["wrap"], part)

    def test_graph_snapshot_delivers_plain_set_payload(self):
        edges = [{
            "voucher": "a", "vouchee": "b", "stake": 1,
            "payload": ListFedSet((1, 2)),
        }]
        snapshot = mod05.graph_snapshot(edges)
        payload = snapshot["edge_list_reference"][0]["payload"]
        self.assertEqual(payload, {1, 2})
        self.assertIs(type(payload), set)

    def test_generator_fed_set_subclass_control(self):
        frozen = mod05._freeze({"wrap": GeneratorFedSet((1, 2))})
        self.assertEqual(frozen, {"wrap": {1, 2}})

    def test_plain_containers_control(self):
        value = {
            "a": [1, {"b": (2, 3)}],
            "s": {4, 5},
            "f": frozenset({6}),
            "n": None,
            "t": "x",
        }
        frozen = mod05._freeze(value)
        self.assertEqual(frozen, value)
        self.assertIsNot(frozen["a"], value["a"])
        value["a"].append(99)
        self.assertEqual(frozen["a"], [1, {"b": (2, 3)}])

    def test_shared_part_stays_shared_control(self):
        shared = [1, 2]
        frozen = mod05._freeze({"x": shared, "y": shared})
        self.assertIs(frozen["x"], frozen["y"])
        self.assertEqual(frozen["x"], [1, 2])

    def test_cyclic_tuple_through_list_stays_one_copy(self):
        # Completion pin, added by the completion seat: the copy
        # act docstring states shared and cyclic container parts
        # stand preserved through the memo, as a plain deep copy
        # preserves them, and a tuple standing in a cycle through
        # a list part is the form that stood short of that state.
        lst = []
        tup = (lst,)
        lst.append(tup)
        frozen = mod05._freeze(tup)
        self.assertIs(frozen[0][0], frozen)

    def test_cyclic_tuple_through_dict_stays_one_copy(self):
        dct = {}
        tup = (dct,)
        dct["t"] = tup
        frozen = mod05._freeze(tup)
        self.assertIs(frozen[0]["t"], frozen)


class TestR6010CountingBasis(unittest.TestCase):

    def test_eta_counts_one_recorded_reading(self):
        self.assertEqual(mod05._character_options(ETA), {"e"})

    def test_theta_counts_two_recorded_readings(self):
        self.assertEqual(mod05._character_options(THETA), {"t", "th"})

    def test_chi_counts_two_readings_control(self):
        self.assertEqual(mod05._character_options(CHI), {"x", "h"})

    def test_eta_filler_key_folded_readings_carry_canary(self):
        key = CANARY_CORE + ETA * 11
        readings = mod05._folded_readings(key)
        self.assertTrue(
            any(reading.startswith("canary") for reading in readings))

    def test_theta_filler_key_stands_past_bound_and_barred_at_mod04(self):
        key = CANARY_CORE + THETA * 11
        readings = mod05._folded_readings(key)
        self.assertFalse(
            any(reading.startswith("canary") for reading in readings))
        self.assertTrue(mod04._is_barred_key(key))

    def test_short_i_filler_key_stands_past_bound_control(self):
        key = CANARY_CORE + "\u0439" * 11
        readings = mod05._folded_readings(key)
        self.assertFalse(
            any(reading.startswith("canary") for reading in readings))


class TestR6011PastBoundStanding(unittest.TestCase):

    def test_past_bound_short_i_core_barred_at_mod05(self):
        self.assertTrue(
            mod05._panel_key_barred(MIXED_CORE + SHORT_I_FILLER))

    def test_past_bound_chi_core_barred_at_mod05(self):
        self.assertTrue(
            mod05._panel_key_barred(MIXED_CORE + CHI_FILLER))

    def test_past_bound_core_fails_panel_validation(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {MIXED_CORE + SHORT_I_FILLER: "v"}))

    def test_past_bound_clean_key_admitted_at_mod05(self):
        self.assertFalse(
            mod05._panel_key_barred("activity" + SHORT_I_FILLER))

    def test_mixed_core_alone_barred_control(self):
        self.assertTrue(mod05._panel_key_barred(MIXED_CORE))


class TestR6019PanelWalks(unittest.TestCase):

    def test_panel_carries_barred_shared_shape_answers_fast(self):
        shape = shared_shape(20)
        started = time.monotonic()
        result = mod05._panel_carries_barred(shape)
        elapsed = time.monotonic() - started
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_panel_clean_shared_shape_answers_fast(self):
        shape = shared_shape(20)
        started = time.monotonic()
        cleaned = mod05._panel_clean(shape)
        elapsed = time.monotonic() - started
        self.assertEqual(cleaned, shape)
        self.assertLess(elapsed, 5.0)

    def test_panel_carries_barred_deep_reach_refused_at_own_depth(self):
        shared = chain(10)
        deep = shared
        for _ in range(95):
            deep = [deep]
        root = {"a": shared, "b": deep}
        with self.assertRaises(ValueError):
            mod05._panel_carries_barred(root)

    def test_panel_carries_barred_within_bound_shared_control(self):
        shared = chain(10)
        deep = shared
        for _ in range(89):
            deep = [deep]
        root = {"a": shared, "b": deep}
        self.assertFalse(mod05._panel_carries_barred(root))

    def test_panel_clean_deep_reach_refused_at_own_depth(self):
        shared = chain(10)
        deep = shared
        for _ in range(95):
            deep = [deep]
        root = {"a": shared, "b": deep}
        with self.assertRaises(ValueError):
            mod05._panel_clean(root)

    def test_panel_carries_barred_cycle_still_refused(self):
        value = []
        value.append(value)
        with self.assertRaises(ValueError):
            mod05._panel_carries_barred(value)

    def test_panel_clean_cycle_still_refused(self):
        value = []
        value.append(value)
        with self.assertRaises(ValueError):
            mod05._panel_clean(value)

    def test_panel_carries_barred_finds_barred_in_shared_control(self):
        shared = [{"membership": 1}]
        root = {"a": shared, "b": shared}
        self.assertTrue(mod05._panel_carries_barred(root))

    def test_panel_clean_strips_barred_in_shared_control(self):
        shared = {"membership": 1, "kept": 2}
        cleaned = mod05.panel_inputs({"a": shared, "b": shared})
        self.assertEqual(cleaned, {"a": {"kept": 2}, "b": {"kept": 2}})


if __name__ == "__main__":
    unittest.main()

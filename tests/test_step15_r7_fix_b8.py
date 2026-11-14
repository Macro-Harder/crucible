"""Step 15 second run, fix wave 6, seat 8. MOD-12 pins.

Pins for register rows R6-007 (MOD-12 limb) and R6-015. Each
defect pin was written before its cure and run against the
unmodified module; the counts stand recorded in the paper for
this seat. Lawful controls pass on the unmodified module and on
the cured module alike.
"""

import types
import unittest

from crucible import mod12

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
    with a barred real money dict. Control form."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _GeneratorMoneyFrozenset(frozenset):
    """A frozenset subclass whose constructor answers a
    generator with a barred real money dict. Control form."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _DeepcopyMoney:
    """A plain object whose copy protocol answers with a barred
    real money dict."""

    def __deepcopy__(self, memo):
        return dict(_MONEY_DICT)


class _HandedCount:
    """A plain object holding four items whose length reading
    answers the number it is handed at construction."""

    def __init__(self, items, answer):
        self._items = list(items)
        self._answer = answer

    def __len__(self):
        return self._answer

    def __iter__(self):
        return iter(self._items)


class _LyingLengthList(list):
    """A list subclass storing four items whose length reading
    answers 3. The base count reads the stored count in both
    standings, as cured under the earlier MOD-12 limb."""

    def __len__(self):
        return 3


def _run_record(values):
    return {
        "run_class": "screening",
        "seed_domain": "screening",
        "anchor_scenario_values": values,
    }


class TestR6007FreezeSetParts(unittest.TestCase):

    def test_list_set_instance_built_from_tuple_stores_inert_values(self):
        instance = _ListMoneySet((1, 2))
        self.assertEqual(set(instance), {1, 2})

    def test_freeze_of_list_set_part_is_not_the_barred_dict(self):
        copied = mod12._freeze({"wrap": _ListMoneySet((1, 2))})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertIsInstance(copied["wrap"], set)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_freeze_of_list_frozenset_part_is_not_the_barred_dict(self):
        copied = mod12._freeze({"wrap": _ListMoneyFrozenset((1, 2))})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertIsInstance(copied["wrap"], frozenset)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_freeze_of_deepcopy_object_is_not_the_barred_dict(self):
        carrier = _DeepcopyMoney()
        copied = mod12._freeze({"wrap": carrier})
        self.assertIs(copied["wrap"], carrier)

    def test_seal_delivers_list_set_payload_whole(self):
        record = mod12.make_family_record()
        record["payload"] = _ListMoneySet((1, 2))
        sealed = mod12.seal_family_record(record)
        self.assertNotEqual(sealed["payload"], _MONEY_DICT)
        self.assertIsInstance(sealed["payload"], set)
        self.assertEqual(set(sealed["payload"]), {1, 2})

    def test_seal_delivers_list_frozenset_payload_whole(self):
        record = mod12.make_family_record()
        record["payload"] = _ListMoneyFrozenset((1, 2))
        sealed = mod12.seal_family_record(record)
        self.assertNotEqual(sealed["payload"], _MONEY_DICT)
        self.assertIsInstance(sealed["payload"], frozenset)
        self.assertEqual(set(sealed["payload"]), {1, 2})

    def test_seal_delivers_deepcopy_object_as_itself(self):
        carrier = _DeepcopyMoney()
        record = mod12.make_family_record()
        record["payload"] = carrier
        sealed = mod12.seal_family_record(record)
        self.assertIs(sealed["payload"], carrier)


class TestR6007Controls(unittest.TestCase):

    def test_generator_set_part_freezes_whole(self):
        copied = mod12._freeze({"wrap": _GeneratorMoneySet([1, 2])})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_generator_frozenset_part_freezes_whole(self):
        copied = mod12._freeze({"wrap": _GeneratorMoneyFrozenset([1, 2])})
        self.assertNotEqual(copied["wrap"], _MONEY_DICT)
        self.assertEqual(set(copied["wrap"]), {1, 2})

    def test_plain_set_payload_seals_whole(self):
        record = mod12.make_family_record()
        record["payload"] = {1, 2}
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["payload"], {1, 2})
        self.assertTrue(sealed["sealed"])

    def test_plain_record_seals_whole(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertTrue(sealed["sealed"])
        self.assertEqual(sealed["family_id"], "family-under-test")

    def test_shared_list_part_stays_shared_through_freeze(self):
        shared = [1, 2]
        copied = mod12._freeze({"first": shared, "second": shared})
        self.assertIs(copied["first"], copied["second"])
        self.assertEqual(copied["first"], [1, 2])

    def test_cyclic_dict_freezes_with_cycle_preserved(self):
        value = {"name": "root"}
        value["self"] = value
        copied = mod12._freeze(value)
        self.assertIs(copied["self"], copied)
        self.assertEqual(copied["name"], "root")


class TestR6015BaseCountFallback(unittest.TestCase):

    def test_base_count_judges_no_count_from_a_handed_length(self):
        handed = _HandedCount([1, 2, 3, 4], 3)
        with self.assertRaises(TypeError):
            mod12._base_count(handed)

    def test_validate_refuses_four_values_behind_a_length_of_three(self):
        handed = _HandedCount([1, 2, 3, 4], 3)
        self.assertFalse(mod12.validate_run_record(_run_record(handed)))


class TestR6015Controls(unittest.TestCase):

    def test_validate_with_length_answering_four_refuses_both_ways(self):
        handed = _HandedCount([1, 2, 3, 4], 4)
        self.assertFalse(mod12.validate_run_record(_run_record(handed)))

    def test_plain_list_of_three_anchor_values_validates(self):
        self.assertTrue(mod12.validate_run_record(
            _run_record(["one", "two", "three"])))

    def test_plain_list_of_four_anchor_values_refuses(self):
        self.assertFalse(mod12.validate_run_record(
            _run_record(["one", "two", "three", "four"])))

    def test_base_count_reads_each_sized_base_form(self):
        self.assertEqual(mod12._base_count([1, 2, 3]), 3)
        self.assertEqual(mod12._base_count((1, 2)), 2)
        self.assertEqual(mod12._base_count({1, 2, 3, 4}), 4)
        self.assertEqual(mod12._base_count(frozenset((1,))), 1)
        self.assertEqual(mod12._base_count({"a": 1, "b": 2}), 2)
        self.assertEqual(mod12._base_count("abc"), 3)
        self.assertEqual(mod12._base_count(b"ab"), 2)
        self.assertEqual(mod12._base_count(bytearray(b"abcd")), 4)

    def test_base_count_reads_a_lying_list_by_its_stored_count(self):
        self.assertEqual(mod12._base_count(_LyingLengthList([1, 2, 3, 4])), 4)

    def test_base_count_on_a_number_raises_type_error(self):
        with self.assertRaises(TypeError):
            mod12._base_count(5)


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 4, MOD-06 items R4-008 and R4-014.

Each test states its distinguishing case with controls both ways:
the hostile or dressed form the register charges, the plain form
that already stands refused or accepted, and a clean form that
must keep its standing.
"""

import types
import unittest

from crucible import mod06

_MONEY_DICT = {"amount": 10, "currency": "USD"}


class _GeneratorMoneySet(set):
    """A set subclass whose constructor answers a generator with a
    barred real money dict and a list with a genuine set."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class _GeneratorMoneyFrozenset(frozenset):
    """A frozenset subclass whose constructor answers a generator
    with a barred real money dict and a list with a genuine set."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_MONEY_DICT)
        return super().__new__(cls, iterable)


class TestR4008UndirectedCopySetParts(unittest.TestCase):

    def test_evil_set_instance_built_from_list(self):
        instance = _GeneratorMoneySet([1, 2])
        self.assertEqual(set(instance), {1, 2})

    def test_direct_copy_of_evil_set_is_plain_set(self):
        copied = mod06._undirected_copy({"nested": _GeneratorMoneySet([1, 2])})
        self.assertEqual(copied, {"nested": {1, 2}})
        self.assertIs(type(copied["nested"]), set)

    def test_direct_copy_of_evil_frozenset_is_plain_frozenset(self):
        copied = mod06._undirected_copy(
            {"nested": _GeneratorMoneyFrozenset([1, 2])})
        self.assertEqual(copied, {"nested": frozenset((1, 2))})
        self.assertIs(type(copied["nested"]), frozenset)

    def test_escrow_result_never_delivers_the_money_dict_set_form(self):
        result = mod06.escrow_result(
            "k", payload={"nested": _GeneratorMoneySet([1, 2])})
        self.assertEqual(result["payload"], {"nested": {1, 2}})
        self.assertIs(type(result["payload"]["nested"]), set)
        self.assertNotEqual(result["payload"]["nested"], _MONEY_DICT)
        self.assertFalse(
            mod06._payload_carries_barred(result["payload"]))
        self.assertTrue(mod06.validate_escrow_result(result))

    def test_escrow_result_never_delivers_the_money_dict_frozenset_form(self):
        result = mod06.escrow_result(
            "k", payload={"nested": _GeneratorMoneyFrozenset([1, 2])})
        self.assertEqual(result["payload"], {"nested": frozenset((1, 2))})
        self.assertIs(type(result["payload"]["nested"]), frozenset)
        self.assertTrue(mod06.validate_escrow_result(result))

    def test_plain_copy_controls_stand(self):
        plain_set = mod06.escrow_result("k", payload={"nested": {1, 2}})
        self.assertEqual(plain_set["payload"], {"nested": {1, 2}})
        self.assertTrue(mod06.validate_escrow_result(plain_set))
        plain_frozen = mod06.escrow_result(
            "k", payload={"nested": frozenset((1, 2))})
        self.assertEqual(
            plain_frozen["payload"], {"nested": frozenset((1, 2))})
        self.assertTrue(mod06.validate_escrow_result(plain_frozen))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={"real_money": 5})


_EN = "\u043d"
_UPSILON = "\u03c5"
_PROBE_KEY = _EN * 10 + "anc" + _EN + "or_set"


class TestR4014VariantCapWholeKey(unittest.TestCase):

    def test_probe_key_is_barred(self):
        payload = {_PROBE_KEY: [1]}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_probe_key_whole_key_reading_reaches_anchor_set(self):
        readings = mod06._folded_readings(_PROBE_KEY)
        self.assertTrue(
            any("anchorset" in reading for reading in readings))

    def test_probe_key_hand_built_result_fails_validation(self):
        result = {
            "core_only_qualifier": True,
            "verification_limit": mod06.VERIFICATION_LIMIT,
            "k1_and_l2_state": "carried",
            "real_money_value": None,
            "payload": {_PROBE_KEY: [1]},
        }
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_mixed_prefix_past_cap_is_barred(self):
        key = _EN * 5 + _UPSILON * 5 + "anc" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={key: [1]})

    def test_ten_upsilon_prefix_past_cap_is_barred(self):
        key = _UPSILON * 10 + "anc" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({key: [1]}))

    def test_longer_prefixes_past_cap_are_barred(self):
        for count in (15, 20):
            key = _EN * count + "anc" + _EN + "or_set"
            self.assertTrue(
                mod06._payload_carries_barred({key: [1]}), count)
            with self.assertRaises(ValueError):
                mod06.escrow_result("k", payload={key: [1]})

    def test_real_money_key_behind_multi_prefix_is_barred(self):
        # The marker word spelled with Greek upsilon at its y
        # position reads as realmoney only under the multi reading
        # of that letter, which stands past the variant cap behind
        # eleven Cyrillic en letters.
        key = _EN * 11 + "real_mone" + _UPSILON
        self.assertTrue(mod06._payload_carries_barred({key: 5}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={key: 5})

    def test_controls_below_cap_and_plain_forms_stand_barred(self):
        below = _EN * 9 + "anc" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({below: [1]}))
        self.assertTrue(mod06._payload_carries_barred({"anchor_set": [1]}))
        self.assertTrue(
            mod06._payload_carries_barred({"anc" + _EN + "or_set": [1]}))
        ascii_prefix = "a" * 15 + "anc" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({ascii_prefix: [1]}))
        trailing = "anc" + _EN + "or_set" + _EN * 15
        self.assertTrue(mod06._payload_carries_barred({trailing: [1]}))
        mixed_below = _EN * 5 + _UPSILON * 4 + "anc" + _EN + "or_set"
        self.assertTrue(mod06._payload_carries_barred({mixed_below: [1]}))

    def test_clean_controls_stand(self):
        self.assertFalse(mod06._payload_carries_barred({"honest": 1}))
        clean_long = _EN * 11 + "honest"
        self.assertFalse(mod06._payload_carries_barred({clean_long: 1}))
        result = mod06.escrow_result("k", payload={clean_long: 1})
        self.assertTrue(mod06.validate_escrow_result(result))


if __name__ == "__main__":
    unittest.main()

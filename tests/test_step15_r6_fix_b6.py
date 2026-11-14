"""Step 15, second run, fix wave 5 pins. MOD-08 items R5-008
(MOD-08 limb), R5-026, R5-034 (MOD-08 limb), and R5-037.

R5-008: the set and frozenset branches of _undirected_copy rebuild
through the plain set and plain frozenset constructors, through
base class readings only, so a hostile subclass constructor cannot
materialise a barred dict in the copy accept_detection_input
delivers. R5-026: the folded barred reading combines the
transliteration and homoglyph readings position by position.
R5-034: the fold carries the modifier small capital readings
U+1D31 as e, U+1D38 as l, U+1D3C as o, and U+1D40 as t. R5-037:
the fold carries the cent sign U+00A2 reading as c for canary.

No detection score is reported as a pass or as a fail in this
file: verdict readings and barred readings only.
"""

import types
import unittest

from crucible import mod08

_BARRED_DICT = {"membership": "barred-value"}


class _GeneratorBarredSet(set):
    """A set subclass whose constructor answers a generator with a
    barred dict and a list with a genuine set."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_BARRED_DICT)
        return super().__new__(cls, iterable)


class _GeneratorBarredFrozenset(frozenset):
    """A frozenset subclass whose constructor answers a generator
    with a barred dict and a list with a genuine frozenset."""

    def __new__(cls, iterable=()):
        if isinstance(iterable, types.GeneratorType):
            return dict(_BARRED_DICT)
        return super().__new__(cls, iterable)


def record_with_records(records):
    return {
        "agent_identifier": "agent-b6",
        "day": 2,
        "feature_values": {"activity": 3},
        "records_for_agent_and_day": records,
    }


def record_with_nested_key(key):
    return record_with_records([{"wrap": {key: 1}}])


class TestR5008UndirectedCopySetParts(unittest.TestCase):

    def test_evil_instances_hold_inert_stored_items(self):
        self.assertEqual(set(_GeneratorBarredSet([1, 2])), {1, 2})
        self.assertEqual(
            set(_GeneratorBarredFrozenset([1, 2])), {1, 2})

    def test_direct_copy_of_evil_set_is_plain_set(self):
        copied = mod08._undirected_copy(
            {"nested": _GeneratorBarredSet([1, 2])})
        self.assertEqual(copied, {"nested": {1, 2}})
        self.assertIs(type(copied["nested"]), set)

    def test_direct_copy_of_evil_frozenset_is_plain_frozenset(self):
        copied = mod08._undirected_copy(
            {"nested": _GeneratorBarredFrozenset([1, 2])})
        self.assertEqual(copied, {"nested": frozenset((1, 2))})
        self.assertIs(type(copied["nested"]), frozenset)

    def test_acceptance_delivers_plain_set_for_evil_set(self):
        accepted = mod08.accept_detection_input(record_with_records(
            [{"kind": "daily_record",
              "nested": _GeneratorBarredSet([1, 2])}]))
        nested = accepted["records_for_agent_and_day"][0]["nested"]
        self.assertEqual(nested, {1, 2})
        self.assertIs(type(nested), set)
        self.assertNotEqual(nested, _BARRED_DICT)

    def test_acceptance_delivers_plain_frozenset_for_evil_frozenset(self):
        accepted = mod08.accept_detection_input(record_with_records(
            [{"kind": "daily_record",
              "nested": _GeneratorBarredFrozenset([1, 2])}]))
        nested = accepted["records_for_agent_and_day"][0]["nested"]
        self.assertEqual(nested, frozenset((1, 2)))
        self.assertIs(type(nested), frozenset)
        self.assertNotEqual(nested, _BARRED_DICT)

    def test_plain_set_and_frozenset_controls_stand(self):
        accepted = mod08.accept_detection_input(record_with_records(
            [{"kind": "daily_record", "nested": {1, 2}}]))
        self.assertEqual(
            accepted["records_for_agent_and_day"][0]["nested"], {1, 2})
        accepted = mod08.accept_detection_input(record_with_records(
            [{"kind": "daily_record", "nested": frozenset((1, 2))}]))
        nested = accepted["records_for_agent_and_day"][0]["nested"]
        self.assertEqual(nested, frozenset((1, 2)))
        self.assertIs(type(nested), frozenset)

    def test_plain_barred_dict_control_refused_at_acceptance(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record_with_records(
                [{"kind": "daily_record", "nested": dict(_BARRED_DICT)}]))


_ES = "\u0441"
_ER = "\u0440"
_EN = "\u043d"
_YU = "\u0443"

COMBINED_KEYS = (
    "member" + _ES + "hi" + _ER,
    "is_" + _EN + "o" + _EN + "est",
    "slee" + _ER + "e" + _ER,
    _ES + "ana" + _ER + _YU,
)

SINGLE_READING_KEYS = (
    "member" + _ES + "hip",
    "member" + "shi" + _ER,
    "is_h" + "o" + _EN + "est",
)


class TestR5026CombinedFoldedReading(unittest.TestCase):

    def test_combined_keys_are_barred(self):
        for key in COMBINED_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_combined_keys_found_by_barred_search(self):
        for key in COMBINED_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._find_barred({"wrap": {key: 1}}))

    def test_acceptance_refuses_each_combined_key(self):
        for key in COMBINED_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_single_reading_dress_controls_still_barred(self):
        for key in SINGLE_READING_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_plain_and_clean_controls_stand(self):
        self.assertTrue(mod08._is_barred_key("membership"))
        self.assertTrue(mod08._is_barred_key("canary"))
        self.assertFalse(mod08._is_barred_key("blorple"))
        self.assertFalse(mod08._is_barred_key("summary"))
        accepted = mod08.accept_detection_input(
            record_with_nested_key("activity"))
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


SMALL_CAPITAL_KEYS = (
    "sl\u1d31eper",
    "s\u1d38eeper",
    "gr\u1d3cund_truth",
    "ground_\u1d40ruth",
    "m\u1d31mbership",
    "\u1d38abel",
)


class TestR5034ModifierSmallCapitals(unittest.TestCase):

    def test_small_capital_keys_are_barred(self):
        for key in SMALL_CAPITAL_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_acceptance_refuses_each_small_capital_key(self):
        for key in SMALL_CAPITAL_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_plain_controls_stand(self):
        for key in ("sleeper", "ground_truth", "membership", "label"):
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))
        self.assertFalse(mod08._is_barred_key("activity"))
        self.assertFalse(mod08._is_barred_key("notes"))


CENT_CANARY_KEY = "\u00a2anary"


class TestR5037CentSignCanary(unittest.TestCase):

    def test_cent_sign_canary_is_barred(self):
        self.assertTrue(mod08._is_barred_key(CENT_CANARY_KEY))

    def test_cent_sign_canary_found_by_barred_search(self):
        self.assertTrue(
            mod08._find_barred({"wrap": {CENT_CANARY_KEY: 1}}))

    def test_acceptance_refuses_cent_sign_canary(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(
                record_with_nested_key(CENT_CANARY_KEY))

    def test_controls_stand(self):
        self.assertTrue(mod08._is_barred_key("canary"))
        self.assertTrue(mod08._is_barred_key("member\u00a7hip"))
        self.assertTrue(mod08._is_barred_key("ground_+ruth"))
        self.assertFalse(mod08._is_barred_key("activity"))
        accepted = mod08.accept_detection_input(
            record_with_nested_key("notes"))
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


if __name__ == "__main__":
    unittest.main()

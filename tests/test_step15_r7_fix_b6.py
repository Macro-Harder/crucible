"""Step 15, second run, fix wave 6 pins. MOD-08 items R6-026,
R6-009 (MOD-08 limb), and R6-019 (MOD-08 limbs).

R6-026: the folded barred reading reads Cyrillic short i U+0439
under both of its readings, i and y, before compatibility
decomposition consumes the letter, so canary dressed with short
i at its y position, in small form, in capital form U+0419, and
in the three kind combination form, stands barred at MOD-08 as
it stands barred at MOD-03, MOD-04, and MOD-10. R6-009: the
combined fold mixes the leet reading and the drop reading
position by position, so a barred key needing the leet reading
at one digit position and the drop reading at another stands
barred. R6-019: the barred search and the barred verdict read
carry a walked standing across paths, keyed by identity and
depth, so a container shared by two siblings stands walked
once for each depth it stands reached at, and a deeper reach
still stands judged at its own depth.

No detection score is reported as a pass or as a fail in this
file: verdict readings and barred readings only.
"""

import time
import unittest

from crucible import mod08

_ES = "\u0441"
_EN = "\u043d"
_ER = "\u0440"
_SHORT_I = "\u0439"
_SHORT_I_CAPITAL = "\u0419"


def record_with_records(records):
    return {
        "agent_identifier": "agent-b6",
        "day": 2,
        "feature_values": {"activity": 3},
        "records_for_agent_and_day": records,
    }


def record_with_nested_key(key):
    return record_with_records([{"wrap": {key: 1}}])


SHORT_I_KEYS = (
    "canar" + _SHORT_I,
    "canar" + _SHORT_I_CAPITAL,
    _ES + "ana" + _ER + _SHORT_I,
)


class TestR6026ShortIReadings(unittest.TestCase):

    def test_fold_reads_short_i_as_y(self):
        for key in SHORT_I_KEYS:
            with self.subTest(key=key):
                self.assertIn("canary", mod08._folded_readings(key))

    def test_short_i_keys_are_barred(self):
        for key in SHORT_I_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_short_i_keys_found_by_barred_search(self):
        for key in SHORT_I_KEYS:
            with self.subTest(key=key):
                self.assertEqual(
                    mod08._find_barred({key: 1}), ["/" + key])

    def test_acceptance_refuses_short_i_records(self):
        for key in SHORT_I_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_short_i_controls_stand(self):
        self.assertTrue(mod08._is_barred_key("canary"))
        self.assertTrue(mod08._is_barred_key(
            "membersh" + _SHORT_I + "p"))
        self.assertFalse(mod08._is_barred_key("blorple"))
        self.assertFalse(mod08._is_barred_key("summary"))
        self.assertFalse(mod08._is_barred_key("canari"))
        accepted = mod08.accept_detection_input(
            record_with_nested_key("activity"))
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


TRIPLE_KEYS = (
    _ES + "4" + _EN + "ar9y",
    "c4na9ry",
    "m3mbershi9p",
)

COMBINED_CONTROLS = (
    "canary",
    "c4nary",
    "cana9ry",
    _ES + "a" + _EN + "ary",
    _ES + "4" + _EN + "ary",
    _ES + "a" + _EN + "ar9y",
)


class TestR6009CombinedLeetDrop(unittest.TestCase):

    def test_triple_keys_are_barred(self):
        for key in TRIPLE_KEYS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))

    def test_triple_keys_found_by_barred_search(self):
        for key in TRIPLE_KEYS:
            with self.subTest(key=key):
                self.assertTrue(
                    mod08._find_barred({"wrap": {key: 1}}))

    def test_acceptance_refuses_triple_records(self):
        for key in TRIPLE_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(mod08.NamedDetectionFailure):
                    mod08.accept_detection_input(
                        record_with_nested_key(key))

    def test_combined_controls_stand(self):
        for key in COMBINED_CONTROLS:
            with self.subTest(key=key):
                self.assertTrue(mod08._is_barred_key(key))
        self.assertFalse(mod08._is_barred_key("hello"))
        accepted = mod08.accept_detection_input(
            record_with_nested_key("activity"))
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


def shared_shape(depth):
    value = ["leaf"]
    for _ in range(depth):
        value = [value, value]
    return value


def deep_wrap(shared, wraps):
    value = shared
    for _ in range(wraps):
        value = [value]
    return value


class TestR6019WalkedStanding(unittest.TestCase):

    def test_find_barred_shared_shape_within_time_bound(self):
        start = time.monotonic()
        hits = mod08._find_barred(shared_shape(20))
        elapsed = time.monotonic() - start
        self.assertEqual(hits, [])
        self.assertLess(elapsed, 5.0)

    def test_carries_barred_verdict_shared_shape_within_time_bound(
            self):
        start = time.monotonic()
        result = mod08._carries_barred_verdict(shared_shape(20))
        elapsed = time.monotonic() - start
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_find_barred_reports_shared_container_on_each_path(self):
        shared = {"canary": 1}
        root = {"a": shared, "b": shared}
        self.assertEqual(
            mod08._find_barred(root), ["/a/canary", "/b/canary"])

    def test_carries_barred_verdict_reads_shared_container(self):
        shared = {"score_verdict": "pass"}
        root = {"a": shared, "b": shared}
        self.assertTrue(mod08._carries_barred_verdict(root))

    def test_find_barred_deep_reach_still_bounded(self):
        shared = ["leaf"]
        root = [shared, deep_wrap(shared, 105)]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred(root)

    def test_carries_barred_verdict_deep_reach_still_bounded(self):
        shared = ["leaf"]
        root = [shared, deep_wrap(shared, 105)]
        self.assertTrue(mod08._carries_barred_verdict(root))

    def test_find_barred_cycle_still_refused(self):
        cyclic = ["leaf"]
        cyclic.append(cyclic)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08._find_barred(cyclic)

    def test_carries_barred_verdict_cycle_still_carries(self):
        cyclic = ["leaf"]
        cyclic.append(cyclic)
        self.assertTrue(mod08._carries_barred_verdict(cyclic))


if __name__ == "__main__":
    unittest.main()

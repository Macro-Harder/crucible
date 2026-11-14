"""Step 15 second run, fix wave 5, seat 8. MOD-12 items.

Pins for register rows R5-009 (MOD-12 limb), R5-011, R5-018
(MOD-12 limb), R5-022, and R5-023 (MOD-12 limb). Each defect pin
was written before its cure and run against the unmodified tree;
the counts stand recorded in the paper for this seat. Row R5-035
charges no MOD-12 limb, so no pin here cures it.
"""
import signal
import time
import unittest

from crucible import mod12

SHORT_I = "\u0439"
SHORT_I_CAPITAL = "\u0419"


def run_record(name, count):
    return {
        "run_class": "screening",
        "seed_domain": "screening",
        name: ["value"] * count,
    }


def money_record(key, sibling=True):
    inner = {key: 10}
    if sibling:
        inner["currency"] = "usd"
    return {
        "run_class": "screening",
        "seed_domain": "screening",
        "nested": inner,
    }


class LyingLengthList(list):
    def __len__(self):
        return 3


class SilentItemsDict(dict):
    def items(self):
        return iter(())


class SilentIterList(list):
    def __iter__(self):
        return iter(())


class SilentIterTuple(tuple):
    def __iter__(self):
        return iter(())


def chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = [value]
    return value


def shared(depth):
    node = ["leaf"]
    for _ in range(depth):
        node = [node, node]
    return node


class _Alarm(Exception):
    pass


def _raise_alarm(signum, frame):
    raise _Alarm()


class TestR5009CombinedLeetDrop(unittest.TestCase):
    def test_amount_key_needing_leet_and_drop_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("4m0unt9")))

    def test_marker_key_leet_then_drop_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("r3almo9ney", sibling=False)))

    def test_marker_key_drop_after_leet_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("rea1mo9ney", sibling=False)))

    def test_anchor_leet_and_drop_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anch0r9_scenario_values", 4)))

    def test_anchor_drop_and_mixed_leet_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anchor9_scenar1o_va1ues", 4)))

    def test_anchor_leet_and_drop_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anch0r9_scenario_values", 3)))

    def test_anchor_drop_and_mixed_leet_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anchor9_scenar1o_va1ues", 3)))

    def test_leet_only_amount_control_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("4mount")))

    def test_drop_only_amount_control_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("am9ount")))

    def test_combined_near_miss_amount_passes(self):
        self.assertTrue(mod12.validate_run_record(
            money_record("4m0unx9")))


class TestR5011ShortIDecomposition(unittest.TestCase):
    def test_short_i_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anchor_scenar" + SHORT_I + "o_values", 4)))

    def test_capital_short_i_anchor_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anchor_scenar" + SHORT_I_CAPITAL + "o_values", 4)))

    def test_short_i_anchor_passes_at_count_3(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anchor_scenar" + SHORT_I + "o_values", 3)))

    def test_plain_anchor_control_refused_at_count_4(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anchor_scenario_values", 4)))


class TestR5018AnchorCountBaseLength(unittest.TestCase):
    def test_lying_length_four_values_refused(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "anchor_scenario_values": LyingLengthList(
                ["a", "b", "c", "d"]),
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_lying_length_three_values_passes(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "anchor_scenario_values": LyingLengthList(["a", "b", "c"]),
        }
        self.assertTrue(mod12.validate_run_record(record))

    def test_plain_four_values_control_refused(self):
        self.assertFalse(mod12.validate_run_record(
            run_record("anchor_scenario_values", 4)))

    def test_plain_three_values_control_passes(self):
        self.assertTrue(mod12.validate_run_record(
            run_record("anchor_scenario_values", 3)))


class TestR5022BaseReadings(unittest.TestCase):
    def test_money_pair_inside_silent_dict_is_barred(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": SilentItemsDict(
                {"amount": 10, "currency": "usd"}),
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_money_pair_inside_silent_list_is_barred(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": SilentIterList(
                [{"amount": 10, "currency": "usd"}]),
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_money_pair_inside_silent_tuple_is_barred(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": SilentIterTuple(
                ({"amount": 10, "currency": "usd"},)),
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_deep_chain_inside_silent_list_is_refused(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": SilentIterList([chain(150)]),
        }
        self.assertFalse(mod12.validate_run_record(record))

    def test_plain_money_control_is_barred(self):
        self.assertFalse(mod12.validate_run_record(
            money_record("amount")))

    def test_shallow_chain_inside_silent_list_passes(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": SilentIterList([chain(50)]),
        }
        self.assertTrue(mod12.validate_run_record(record))

    def test_plain_deep_chain_control_is_refused(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": chain(150),
        }
        self.assertFalse(mod12.validate_run_record(record))


class TestR5023SharedContainerRewalk(unittest.TestCase):
    def _shape_with_alarm(self, value, seconds=10):
        previous = signal.signal(signal.SIGALRM, _raise_alarm)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            started = time.time()
            result = mod12._shape_exceeds_bounds(value)
            return result, time.time() - started
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)

    def test_shared_depth_24_within_bound_and_fast(self):
        try:
            result, elapsed = self._shape_with_alarm(shared(24))
        except _Alarm:
            self.fail("shared depth 24 walk did not answer in 10 seconds")
        self.assertFalse(result)
        self.assertLess(elapsed, 10)

    def test_shared_depth_24_record_validates(self):
        record = {
            "run_class": "screening",
            "seed_domain": "screening",
            "nested": shared(24),
        }
        try:
            previous = signal.signal(signal.SIGALRM, _raise_alarm)
            signal.setitimer(signal.ITIMER_REAL, 10)
            try:
                result = mod12.validate_run_record(record)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous)
        except _Alarm:
            self.fail("shared depth 24 record did not answer in 10 seconds")
        self.assertTrue(result)

    def test_cycle_control_still_refused(self):
        cyclic = []
        cyclic.append(cyclic)
        self.assertTrue(mod12._shape_exceeds_bounds(cyclic))

    def test_chain_101_control_within_bound(self):
        self.assertFalse(mod12._shape_exceeds_bounds(chain(101)))

    def test_chain_102_control_exceeds_bound(self):
        self.assertTrue(mod12._shape_exceeds_bounds(chain(102)))


if __name__ == "__main__":
    unittest.main()

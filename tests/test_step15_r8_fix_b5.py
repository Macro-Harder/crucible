"""Step 15 Round 8 fix pins, Fix Wave 7 Builder 5.

Row R7-006: release_view at MOD-04 reads the held view record
through base class operations, so a held dict whose own get
reading reports a clean record cannot deliver its stored barred
record as released, and a held dict whose own get reading reports
a barred record cannot refuse its stored clean record.

Row R7-017: the walks at MOD-04 _view_copy_guard, MOD-04
_value_appears, and MOD-11 _envelope_part_stands each carry a
walked standing across paths, keyed so a deeper reach still stands
judged at its own depth where a depth bound applies. The pins
assert the walked standing on shared shapes with time bounded and
measured, in the form the Round 6 papers used, and they carry the
depth and cycle controls standing both ways.
"""
import signal
import time
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10
import crucible.mod11 as mod11


class _Alarm(Exception):
    pass


def _raise_alarm(signum, frame):
    raise _Alarm()


def run_bounded(call, seconds=10):
    previous = signal.signal(signal.SIGALRM, _raise_alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        started = time.time()
        result = call()
        return result, time.time() - started
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def diamond(depth, leaf):
    value = [leaf]
    for _ in range(depth):
        value = [value, value]
    return value


def chain(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def _clean_view():
    return mod04.build_view_record(
        run_id="run-r8-b5-view", viewer_id="viewer-1", day=2,
        contents=[{"day": 1, "delay": 0}],
        position="pos-1", rule_version_set="rv-1")


def _barred_view():
    record = _clean_view()
    record["view_contents"] = [{"canary": "barred value"}]
    return record


class LyingHeld(dict):
    """A held dict whose get reading reports another record."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        if key == "view_record":
            return self._reported
        return dict.get(self, key, default)


class TestR7006ReleaseViewBaseReading(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_plain_clean_held_releases(self):
        released = mod04.release_view(mod04.hold_view(_clean_view()))
        self.assertTrue(released["released"])
        self.assertFalse(released["held"])

    def test_plain_barred_held_refused(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(_barred_view())
        with self.assertRaises(mod04.NamedFailure):
            mod04.release_view(mod04.hold_view(_barred_view()))

    def test_lying_get_reporting_clean_cannot_deliver_stored_barred(self):
        held = LyingHeld(
            {"view_record": _barred_view(), "held": True,
             "released": False},
            _clean_view())
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.release_view(held)
        self.assertIn("canary", str(caught.exception))

    def test_lying_get_reporting_barred_cannot_refuse_stored_clean(self):
        held = LyingHeld(
            {"view_record": _clean_view(), "held": True,
             "released": False},
            _barred_view())
        released = mod04.release_view(held)
        self.assertTrue(released["released"])
        stored = dict.get(released, "view_record")
        self.assertEqual(
            dict.get(stored, "view_contents"),
            [{"day": 1, "delay": 0}])


class TestR7017ViewCopyGuardWalk(unittest.TestCase):
    def test_shared_depth_20_diamond_answers_fast(self):
        try:
            result, elapsed = run_bounded(
                lambda: mod04._view_copy_guard(diamond(20, "x")))
        except _Alarm:
            self.fail("shared depth 20 guard walk gave no answer in 10 seconds")
        self.assertIsNone(result)
        self.assertLess(elapsed, 5.0)

    def test_plain_chain_and_cycle_controls(self):
        mod04._view_copy_guard(chain(50, "leaf"))
        with self.assertRaises(mod04.NamedFailure):
            mod04._view_copy_guard(chain(102, "leaf"))
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod04.NamedFailure):
            mod04._view_copy_guard(cyclic)

    def test_deeper_reach_of_shared_chain_still_judged_at_its_depth(self):
        shared = chain(50, "leaf")
        holder = chain(60, shared)
        with self.assertRaises(mod04.NamedFailure):
            mod04._view_copy_guard([shared, holder])
        with self.assertRaises(mod04.NamedFailure):
            mod04._view_copy_guard([holder, shared])


class TestR7017ValueAppearsWalk(unittest.TestCase):
    def test_shared_depth_20_diamond_absent_answers_fast(self):
        try:
            result, elapsed = run_bounded(
                lambda: mod04._value_appears("absent", diamond(20, "x")))
        except _Alarm:
            self.fail("shared depth 20 presence walk gave no answer in 10 seconds")
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_present_and_depth_controls(self):
        self.assertTrue(mod04._value_appears("needle", chain(50, "needle")))
        self.assertFalse(mod04._value_appears("absent", chain(50, "needle")))
        self.assertTrue(
            mod04._value_appears("needle", diamond(12, "needle")))
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("needle", chain(150, "needle"))

    def test_cyclic_shape_refused_in_named_form(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("absent", cyclic)

    def test_deeper_reach_of_shared_chain_still_judged_at_its_depth(self):
        shared = chain(50, "leaf")
        holder = chain(60, shared)
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("absent", [shared, holder])
        with self.assertRaises(mod04.NamedFailure):
            mod04._value_appears("absent", [holder, shared])


class TestR7017EnvelopePartStandsWalk(unittest.TestCase):
    def test_shared_depth_20_diamond_absent_answers_fast(self):
        try:
            result, elapsed = run_bounded(
                lambda: mod11._envelope_part_stands(diamond(20, 0)))
        except _Alarm:
            self.fail("shared depth 20 envelope walk gave no answer in 10 seconds")
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_depth_bound_controls(self):
        self.assertTrue(mod11._envelope_part_stands(chain(101, "holds")))
        self.assertFalse(mod11._envelope_part_stands(chain(102, "holds")))
        self.assertTrue(mod11._envelope_part_stands(chain(100, "holds")))

    def test_deep_false_reach_does_not_poison_shallow_reach(self):
        shared = ["holds"]
        deep = chain(105, shared)
        self.assertTrue(mod11._envelope_part_stands([deep, shared]))

    def test_present_and_cycle_controls(self):
        self.assertTrue(
            mod11._envelope_part_stands(diamond(12, "holds")))
        cyclic = []
        cyclic.append(cyclic)
        self.assertFalse(mod11._envelope_part_stands(cyclic))


if __name__ == "__main__":
    unittest.main()

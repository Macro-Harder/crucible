"""Step 17 fix wave 5, Slice 3 defect tests: the mod10 aggregate
component judgement in dressed subclass form (FW5-03) and the
mod10 file backed retention sync cost form (FW5-15).

FW5-03: the aggregate component judgement, at retention and at
the validation acts alike, judges a component and a denominator
on the plain value of the handing, so a component above its
denominator, a component below zero, and a denominator at or
below zero refuse in the named daily aggregate delivery form in
dressed subclass form exactly as in plain form. The dressed
form here stands as an int subclass whose comparison methods
each answer in the passing direction, the LyingInt form of the
Round 4 filing S17R4-RED1-01.

FW5-15: the file backed retention act stands bounded in its
sync cost form. The charged form: one file backed retain pays
one posix.fsync, so a batch of N retentions on one store pays
N fsync calls. The bound the cure states: the sync stands
batched across the flushes of one store standing, at most one
posix.fsync per batch of 32 flushes of one instance, the first
flush of an instance standing synced as now, and a flush
carrying removal forms standing synced as now, so a batch of
100 retentions pays at most 5 fsync calls. The defect test
counts fsync calls through a counting wrapper that calls the
real act through, in the measurement check form of FW4-03:
the count stands as the charged form standing bounded or
unbounded, and any timing figure stands beside the row in the
builder paper as a measurement, never as the verdict of a
test. The store file keeps its sealed single payload form
whole under this cure, and no store format question stands
settled by any test here.
"""
import os
import shutil
import unittest
from unittest import mock

import crucible.mod10 as mod10


class LyingInt(int):
    """An int subclass whose comparison methods each answer in
    the passing direction, as filed at S17R4-RED1-01."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False


class LyingFloat(float):
    """A float subclass whose comparison methods each answer
    in the passing direction, the float twin of LyingInt."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False


def delivery(components, denominators):
    return {
        "simulated_day": 1,
        "viewer_id": "viewer-1",
        "joint_outcome_components": components,
        "component_denominators": denominators,
        "honest_share": 0.5,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0.5},
    }


class Fix5B3Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestFW503Retention(Fix5B3Base):
    """FW5-03 at the retention door: dressed handings refuse in
    the named daily aggregate delivery form exactly as their
    plain twins refuse."""

    def test_dressed_component_above_denominator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw503-r1", [delivery(
                    [LyingInt(11), 0, 0, 0], [10, 10, 10, 10])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertIn("stand impossible", str(caught.exception))
        rows = mod10.daily_aggregates_for_run("fw503-r1")
        self.assertTrue(all(
            row.get("form") == "form_only" for row in rows))

    def test_dressed_component_below_zero_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw503-r2", [delivery(
                    [LyingInt(-5), 0, 0, 0], [10, 10, 10, 10])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertIn("stand impossible", str(caught.exception))

    def test_dressed_denominator_zero_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw503-r3", [delivery(
                    [0, 0, 0, 0], [LyingInt(0), 1, 1, 1])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertIn("stand impossible", str(caught.exception))

    def test_dressed_denominator_below_zero_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw503-r4", [delivery(
                    [0, 0, 0, 0], [LyingInt(-3), 1, 1, 1])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertIn("stand impossible", str(caught.exception))

    def test_dressed_float_component_above_denominator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw503-r5", [delivery(
                    [LyingFloat(2.5), 0, 0, 0], [1, 1, 1, 1])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertIn("stand impossible", str(caught.exception))

    def test_plain_controls_refuse_in_named_form(self):
        for run_id, components, denominators in (
                ("fw503-c1", [11, 0, 0, 0], [10, 10, 10, 10]),
                ("fw503-c2", [-1, 0, 0, 0], [10, 10, 10, 10]),
                ("fw503-c3", [1, 0, 0, 0], [0, 1, 1, 1]),
                ("fw503-c4", [0, 0, 0, 0], [-3, 1, 1, 1])):
            with self.assertRaises(ValueError) as caught:
                mod10.retain_daily_aggregate_deliveries(
                    run_id, [delivery(components, denominators)])
            self.assertIn("daily aggregate delivery in named form",
                          str(caught.exception))

    def test_valid_dressed_handing_served_whole_control(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "fw503-c5", [delivery(
                [LyingInt(3), 0, 0, 0], [10, 10, 10, 10])])
        self.assertEqual(count, 1)
        rows = mod10.daily_aggregates_for_run("fw503-c5")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["joint_outcome_components"][0], 3)

    def test_plain_valid_handing_served_whole_control(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "fw503-c6", [delivery([1, 2, 3, 4], [10, 10, 10, 10])])
        self.assertEqual(count, 1)
        rows = mod10.daily_aggregates_for_run("fw503-c6")
        self.assertEqual(len(rows), 1)


class TestFW503Validation(Fix5B3Base):
    """FW5-03 at the validation acts: validate_daily_aggregates
    and daily_aggregates_validation_failures judge a dressed
    record on the plain value of its components and
    denominators, exactly as a plain record stands judged."""

    @staticmethod
    def _row(components, denominators):
        return {
            "run_id": "fw503-v", "viewer_id": "viewer-1",
            "joint_outcome_components": components,
            "component_denominators": denominators,
        }

    def test_validate_dressed_component_below_zero_false(self):
        rows = [self._row([LyingInt(-5), 0, 0, 0], [10, 10, 10, 10])]
        self.assertFalse(mod10.validate_daily_aggregates(rows))
        failures = mod10.daily_aggregates_validation_failures(rows)
        self.assertTrue(failures)
        self.assertTrue(any(
            "joint_outcome_components" in failure
            for failure in failures))

    def test_validate_dressed_component_above_denominator_false(self):
        rows = [self._row([LyingInt(11), 0, 0, 0], [10, 10, 10, 10])]
        self.assertFalse(mod10.validate_daily_aggregates(rows))
        self.assertTrue(
            mod10.daily_aggregates_validation_failures(rows))

    def test_validate_dressed_denominator_zero_false(self):
        rows = [self._row([0, 0, 0, 0], [LyingInt(0), 1, 1, 1])]
        self.assertFalse(mod10.validate_daily_aggregates(rows))
        self.assertTrue(
            mod10.daily_aggregates_validation_failures(rows))

    def test_validate_dressed_denominator_below_zero_false(self):
        rows = [self._row([0, 0, 0, 0], [LyingInt(-3), 1, 1, 1])]
        self.assertFalse(mod10.validate_daily_aggregates(rows))
        self.assertTrue(
            mod10.daily_aggregates_validation_failures(rows))

    def test_validate_plain_negative_component_control(self):
        rows = [self._row([-5, 0, 0, 0], [10, 10, 10, 10])]
        self.assertFalse(mod10.validate_daily_aggregates(rows))
        self.assertTrue(
            mod10.daily_aggregates_validation_failures(rows))

    def test_validate_valid_dressed_row_control(self):
        rows = [self._row(
            [LyingInt(3), 0, 0, 0], [LyingInt(10), 10, 10, 10])]
        self.assertTrue(mod10.validate_daily_aggregates(rows))
        self.assertEqual(
            mod10.daily_aggregates_validation_failures(rows), [])


class local_temp_dir:
    """A temporary directory under the product tree, in the
    form the sibling mod10 test files use."""

    def __enter__(self):
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".fix5b3_tmp")
        self.path = os.path.join(base, "case-%d" % os.getpid())
        os.makedirs(self.path, exist_ok=True)
        return self.path

    def __exit__(self, *exc):
        shutil.rmtree(self.path, ignore_errors=True)
        return False


class TestFW515SyncCost(Fix5B3Base):
    """FW5-15: the file backed retention sync cost form, judged
    by counted fsync calls in the measurement check form stated
    at the head of this file. The bound the cure states: at
    most one posix.fsync per batch of 32 flushes of one store
    instance, beside the first flush of an instance and any
    flush carrying removal forms, each standing synced as now,
    so a batch of 100 retentions on one store pays at most 5
    fsync calls where the uncured act pays 100."""

    def test_fw515_bulk_retention_fsync_count_bounded(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            real_fsync = os.fsync
            calls = []

            def counting_fsync(fd):
                calls.append(fd)
                return real_fsync(fd)

            with mock.patch("os.fsync", counting_fsync):
                for n in range(100):
                    store.retain_run_record(
                        {"run_id": "fw515-%d" % n, "v": n})
            self.assertLessEqual(len(calls), 5)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(
                reopened.read_run_record("fw515-99"),
                {"run_id": "fw515-99", "v": 99})
            self.assertEqual(len(reopened.index()), 100)

    def test_fw515_fsync_count_bounded_at_rising_counts(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            real_fsync = os.fsync
            calls = []

            def counting_fsync(fd):
                calls.append(fd)
                return real_fsync(fd)

            with mock.patch("os.fsync", counting_fsync):
                for n in range(300):
                    store.retain_run_record(
                        {"run_id": "fw515r-%d" % n, "v": n})
            self.assertLessEqual(len(calls), 11)

    def test_control_single_retention_stands_synced_and_whole(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            real_fsync = os.fsync
            calls = []

            def counting_fsync(fd):
                calls.append(fd)
                return real_fsync(fd)

            with mock.patch("os.fsync", counting_fsync):
                store.retain_run_record({"run_id": "fw515-one", "v": 1})
            self.assertEqual(len(calls), 1)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(
                reopened.read_run_record("fw515-one"),
                {"run_id": "fw515-one", "v": 1})

    def test_control_clear_stands_synced_and_whole(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            for n in range(40):
                store.retain_run_record(
                    {"run_id": "fw515c-%d" % n, "v": n})
            real_fsync = os.fsync
            calls = []

            def counting_fsync(fd):
                calls.append(fd)
                return real_fsync(fd)

            with mock.patch("os.fsync", counting_fsync):
                store.clear()
            self.assertEqual(len(calls), 1)
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(reopened.index(), [])

    def test_control_failed_flush_leaves_prior_file_whole(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "fw515-prior"})
            with mock.patch("crucible.mod10.json.dumps",
                            side_effect=OSError("interrupted")):
                with self.assertRaises(ValueError):
                    store.retain_run_record({"run_id": "fw515-later"})
            reopened = mod10.RecorderStore(
                store_kind="sweep", path=path)
            self.assertEqual(
                reopened.read_run_record("fw515-prior"),
                {"run_id": "fw515-prior"})
            with self.assertRaises(mod10.LookupFailure):
                reopened.read_run_record("fw515-later")

    def test_control_two_instances_read_each_other_whole(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            first = mod10.RecorderStore(store_kind="sweep", path=path)
            second = mod10.RecorderStore(store_kind="sweep", path=path)
            for n in range(40):
                first.retain_run_record(
                    {"run_id": "fw515a-%d" % n, "v": n})
            for n in range(40):
                second.retain_run_record(
                    {"run_id": "fw515b-%d" % n, "v": n})
            third = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(len(third.index()), 80)
            self.assertEqual(
                third.read_run_record("fw515a-39"),
                {"run_id": "fw515a-39", "v": 39})
            self.assertEqual(
                third.read_run_record("fw515b-39"),
                {"run_id": "fw515b-39", "v": 39})


if __name__ == "__main__":
    unittest.main()

"""Step 17 fix wave 3, Builder 3 tests: Slice 3, the mod10
scaling rows. Rows FW3-06 and FW3-07.

Each defect test states the growth or cost form its row charges
and the bound the cure states, and reproduces the charged form
standing absent or unbounded on the uncured tree (the landed tree
carrying the Slice 1 and Slice 2 cures, uncured for these rows).
A timing figure stands nowhere as the verdict of a test: the
defect tests judge counted work (guarded store file loads, and
stored form computations), which is the growth form itself.
File stores stand built in temporary directories only.
Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import json
import os
import tempfile
import unittest
from unittest import mock

from crucible import mod10


class GuardedLoadCounter:
    """Count guarded store file loads while installed."""

    def __init__(self):
        self.calls = 0
        self._real = mod10._guarded_store_records

    def __enter__(self):
        real = self._real
        counter = self

        def counting(path, kind_text, fast=False):
            counter.calls += 1
            return real(path, kind_text, fast=fast)

        mod10._guarded_store_records = counting
        return self

    def __exit__(self, *exc):
        mod10._guarded_store_records = self._real
        return False


class StoredFormCounter:
    """Count stored form computations while installed."""

    def __init__(self):
        self.calls = 0
        self._real = mod10._stored_form

    def __enter__(self):
        real = self._real
        counter = self

        def counting(value):
            counter.calls += 1
            return real(value)

        mod10._stored_form = counting
        return self

    def __exit__(self, *exc):
        mod10._stored_form = self._real
        return False


class TempDirBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "store.json")

    def fill_store(self, count):
        store = mod10.new_store("sweep", path=self.path)
        for i in range(count):
            store.retain_run_record(
                {"run_id": "run-%03d" % i, "v": i})
        return store


class TestFW306BoundedFileGrowth(TempDirBase):
    """FW3-06 (Medium, T17R2-06): the file backed retention and
    reading paths carry a stated growth form bounded by the act,
    in place of whole file rewrites and reloads on every act, in
    the bounded form alone. The bound the cure states: an act on
    a store file whose standing has not changed since this
    instance last stood on it takes no guarded load of the file
    at all (one file standing check stands in its place), and a
    changed file stands reloaded once through the guarded path.
    The store file format stands unchanged."""

    def test_reads_on_unchanged_file_take_no_guarded_load(self):
        store = self.fill_store(30)
        with GuardedLoadCounter() as counter:
            for i in range(10):
                record = store.read_run_record("run-%03d" % i)
                self.assertEqual(record["v"], i)
            for i in range(5):
                self.assertTrue(
                    store.has_run_record("run-%03d" % i))
            self.assertEqual(len(store.index()), 30)
        self.assertEqual(counter.calls, 0)

    def test_retain_on_unchanged_file_takes_no_guarded_load(self):
        store = self.fill_store(30)
        with GuardedLoadCounter() as counter:
            store.retain_run_record({"run_id": "run-new", "v": 99})
        self.assertEqual(counter.calls, 0)
        fresh = mod10.new_store("sweep", path=self.path)
        self.assertEqual(fresh.read_run_record("run-new")["v"], 99)
        self.assertEqual(len(fresh.index()), 31)

    def test_retention_batch_takes_no_guarded_load_per_act(self):
        store = mod10.new_store("sweep", path=self.path)
        with GuardedLoadCounter() as counter:
            for i in range(40):
                store.retain_run_record(
                    {"run_id": "batch-%03d" % i, "v": i})
        self.assertEqual(counter.calls, 0)
        self.assertEqual(len(store.index()), 40)

    def test_second_instance_records_stand_read_after_change(self):
        first = self.fill_store(5)
        second = mod10.new_store("sweep", path=self.path)
        first.retain_run_record({"run_id": "from-first", "v": 50})
        self.assertEqual(
            second.read_run_record("from-first")["v"], 50)
        second.retain_run_record({"run_id": "from-second", "v": 60})
        self.assertEqual(
            first.read_run_record("from-second")["v"], 60)
        self.assertEqual(len(first.index()), 7)

    def test_tampered_file_stands_refused_at_read(self):
        store = self.fill_store(5)
        with open(self.path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["records"][0]["v"] = 999
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record("run-000")

    def test_failed_retention_stands_not_served_afterwards(self):
        store = self.fill_store(5)
        with mock.patch.object(
                mod10.os, "replace",
                side_effect=OSError("no replace stands taken")):
            with self.assertRaises(ValueError):
                store.retain_run_record(
                    {"run_id": "doomed", "v": 1})
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record("doomed")
        self.assertNotIn("doomed", store.index())
        self.assertEqual(len(store.index()), 5)


class TestFW307BucketGrowth(unittest.TestCase):
    """FW3-07 (Medium, T17R2-07): event log and daily snapshot
    retention carry a stated growth form and a stated cap, so
    per act cost stands bounded by the act. The growth form the
    cure states: the duplicate judgement of one retention act
    computes the stored form of the handed entry alone and
    judges it against a maintained index of the forms already
    held, so the stored form work of one act stands bounded by
    the handed entry and never by the volume already held. The
    cap the cure states: 10000 entries held for one run, the
    figure the module already states for a per run retained
    collection; a retention past the cap stands refused in
    named form."""

    def setUp(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)

    def test_event_log_form_work_bounded_by_handed_entry(self):
        for i in range(60):
            mod10.retain_event_log_entry(
                {"run_identifier": "log-run", "seq": i,
                 "note": "n"})
        with StoredFormCounter() as counter:
            mod10.retain_event_log_entry(
                {"run_identifier": "log-run", "seq": 1000,
                 "note": "n"})
        self.assertLessEqual(counter.calls, 70)
        self.assertEqual(len(mod10.event_log_entries("log-run")), 61)

    def test_daily_snapshot_form_work_bounded_by_handed_entry(self):
        for i in range(60):
            mod10.retain_daily_snapshot(
                {"run_identifier": "snap-run", "day": i,
                 "note": "n"})
        with StoredFormCounter() as counter:
            mod10.retain_daily_snapshot(
                {"run_identifier": "snap-run", "day": 1000,
                 "note": "n"})
        self.assertLessEqual(counter.calls, 70)
        self.assertEqual(
            len(mod10.daily_snapshots("snap-run")), 61)

    def test_event_log_bucket_cap_refused_in_named_form(self):
        mod10._EVENT_LOGS[("sweep", "cap-run")] = [
            {"run_identifier": "cap-run", "seq": i}
            for i in range(10000)]
        with self.assertRaises(ValueError) as caught:
            mod10.retain_event_log_entry(
                {"run_identifier": "cap-run", "seq": 20000})
        self.assertIn("cap", str(caught.exception))
        self.assertEqual(
            len(mod10.event_log_entries("cap-run")), 10000)

    def test_daily_snapshot_bucket_cap_refused_in_named_form(self):
        mod10._DAILY_SNAPSHOTS[("sweep", "cap-run")] = [
            {"run_identifier": "cap-run", "day": i}
            for i in range(10000)]
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_snapshot(
                {"run_identifier": "cap-run", "day": 20000})
        self.assertIn("cap", str(caught.exception))
        self.assertEqual(
            len(mod10.daily_snapshots("cap-run")), 10000)

    def test_event_log_duplicate_and_order_control(self):
        first = {"run_identifier": "ctl-run", "seq": 1}
        second = {"run_identifier": "ctl-run", "seq": 2}
        mod10.retain_event_log_entry(first)
        mod10.retain_event_log_entry(second)
        returned = mod10.retain_event_log_entry(dict(first))
        self.assertEqual(returned["seq"], 1)
        entries = mod10.event_log_entries("ctl-run")
        self.assertEqual([e["seq"] for e in entries], [1, 2])

    def test_daily_snapshot_duplicate_and_order_control(self):
        first = {"run_identifier": "ctl-run", "day": 1}
        second = {"run_identifier": "ctl-run", "day": 2}
        mod10.retain_daily_snapshot(first)
        mod10.retain_daily_snapshot(second)
        returned = mod10.retain_daily_snapshot(dict(first))
        self.assertEqual(returned["day"], 1)
        snaps = mod10.daily_snapshots("ctl-run")
        self.assertEqual([s["day"] for s in snaps], [1, 2])


if __name__ == "__main__":
    unittest.main()

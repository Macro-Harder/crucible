"""Pins for fix wave 24, builder b3, row R24-004 of the
Round 24 register, on triage ruling T24-4: the MOD-10
RecorderStore flush ordering limb.

The defect, at crucible/mod10.py RecorderStore._flush, at
its record ordering limb, sorted(merged, key=lambda item:
_safe_str(item)): the limb orders the records it writes
through a reading the handed record itself supplies. A run
identifier storing one text whose string reading answers
another stands ordered by the reading it supplies; a run
identifier whose string reading raises stands ordered by
its base object repr; and a run identifier whose string
reading raises KeyboardInterrupt or SystemExit escapes
bare at RecorderStore.retain_run_record through that limb,
the retention rollback catching plain Exception alone, so
no store file stands written and the record stands left
in the store. The cure: the delivered store file order
stands decided on stored text ordering at the ordering
limb, in the form the companion ordering forms state,
_day_sort_key in MOD-10 and _catalogue_order_key in
MOD-09, and _safe_str itself takes no edit.

Distinguishing pins fail on the pristine basis and pass
on the cured copy. Control pins pass on both trees. Every
distinguishing pin catches BaseException inside the pin,
so a bare escape of any kind stands as a pin failure and
never as a runner abort.
"""
import json
import os
import tempfile
import unittest

from crucible import mod10


class LyingStr(str):
    """A text value storing one text whose string reading
    answers another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie


class RaisingStr(str):
    """A text value storing one text whose string reading
    raises a plain Exception kind."""

    def __str__(self):
        raise RuntimeError("string reading raises")


class RaisingIndexStr(str):
    """A text value storing one text whose string reading
    raises IndexError."""

    def __str__(self):
        raise IndexError("string reading raises")


class KeyboardStr(str):
    """A text value storing one text whose string reading
    raises KeyboardInterrupt."""

    def __str__(self):
        raise KeyboardInterrupt("string reading raises")


class ExitStr(str):
    """A text value storing one text whose string reading
    raises SystemExit."""

    def __str__(self):
        raise SystemExit("string reading raises")


class HonestStr(str):
    """A text value whose string reading answers the text
    it stores, read through the base string form."""

    def __str__(self):
        return str.__str__(self)


def file_order(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return [
        record.get("run_id") or record.get("run_identifier")
        for record in data["records"]]


def retain_outcome(store, rid):
    try:
        store.retain_run_record({"run_id": rid})
    except BaseException as exc:
        return exc
    return None


class FlushStoreCase(unittest.TestCase):

    def make_store(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = os.path.join(tmp.name, "store.json")
        return mod10.RecorderStore(store_kind="sweep", path=path), path


class TestR24004FlushOrderingDresses(FlushStoreCase):

    def test_distinguishing_lying_low_lie_orders_by_stored_text(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "a-run"))
        self.assertIsNone(retain_outcome(
            store, LyingStr("b-run", "a-lie")))
        self.assertEqual(file_order(path), ["a-run", "b-run"])

    def test_distinguishing_lying_high_lie_orders_by_stored_text(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "m-run"))
        self.assertIsNone(retain_outcome(
            store, LyingStr("a-run", "zzz-lie")))
        self.assertEqual(file_order(path), ["a-run", "m-run"])

    def test_distinguishing_raising_orders_by_stored_text(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "a-run"))
        self.assertIsNone(retain_outcome(store, RaisingStr("b-run")))
        self.assertEqual(file_order(path), ["a-run", "b-run"])

    def test_distinguishing_raising_index_orders_by_stored_text(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "aaa-plain"))
        self.assertIsNone(retain_outcome(
            store, RaisingIndexStr("zzz-stored")))
        self.assertEqual(file_order(path), ["aaa-plain", "zzz-stored"])

    def test_distinguishing_keyboard_interrupt_at_retain(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "a-run"))
        outcome = retain_outcome(store, KeyboardStr("b-run"))
        self.assertIsNone(outcome)
        self.assertEqual(file_order(path), ["a-run", "b-run"])
        self.assertTrue(store.has_run_record("b-run"))

    def test_distinguishing_system_exit_at_retain(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "a-run"))
        outcome = retain_outcome(store, ExitStr("b-run"))
        self.assertIsNone(outcome)
        self.assertEqual(file_order(path), ["a-run", "b-run"])
        self.assertTrue(store.has_run_record("b-run"))

    def test_distinguishing_keyboard_first_stored_at_retain(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "b-run"))
        outcome = retain_outcome(store, KeyboardStr("a-run"))
        self.assertIsNone(outcome)
        self.assertEqual(file_order(path), ["a-run", "b-run"])
        self.assertTrue(store.has_run_record("a-run"))


class TestR24004FlushOrderingControls(FlushStoreCase):

    def test_control_plain_reverse_retention_orders_stored(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "b-run"))
        self.assertIsNone(retain_outcome(store, "a-run"))
        self.assertEqual(file_order(path), ["a-run", "b-run"])

    def test_control_plain_stored_retention_orders_stored(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "a-run"))
        self.assertIsNone(retain_outcome(store, "b-run"))
        self.assertEqual(file_order(path), ["a-run", "b-run"])

    def test_control_honest_subclass_orders_by_stored_text(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "m-run"))
        self.assertIsNone(retain_outcome(store, HonestStr("a-run")))
        self.assertEqual(file_order(path), ["a-run", "m-run"])

    def test_control_plain_single_record_written(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "only-run"))
        self.assertEqual(file_order(path), ["only-run"])

    def test_control_plain_duplicate_refusal_unmoved(self):
        store, path = self.make_store()
        self.assertIsNone(retain_outcome(store, "run-1"))
        with self.assertRaises(ValueError) as ctx:
            store.retain_run_record({"run_id": "run-1"})
        self.assertIn(
            "second record for the same run is rejected: run-1",
            str(ctx.exception))
        self.assertEqual(file_order(path), ["run-1"])

    def test_control_memory_store_retains_dressed_record(self):
        store = mod10.RecorderStore()
        result = store.retain_run_record(
            {"run_id": LyingStr("b-run", "a-lie")})
        self.assertEqual(result["run_id"], "b-run")
        self.assertTrue(store.has_run_record("b-run"))


if __name__ == "__main__":
    unittest.main()

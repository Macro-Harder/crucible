"""Pin tests for fix wave 18, Builder 6, Group 6 rows.

Rows pinned: R18-014, R18-034, R18-035, R18-042, R18-043,
R18-055, R18-056. Each pin states the charged defect at its
locus in crucible/mod10.py and fails on the pristine code for
that defect, beside plain controls that pass on both standings.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10

VICTIM = "victim-b6"


class LieAll:
    """No text form, hash naming a stored run, equality True."""

    def __init__(self, target):
        self._target = target

    def __hash__(self):
        return hash(self._target)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class EqRaisesObj:
    """No text form, hash naming a stored value, equality raises."""

    def __init__(self, target):
        self._target = target

    def __hash__(self):
        return hash(self._target)

    def __eq__(self, other):
        raise RuntimeError("boom-eq-obj")

    def __ne__(self, other):
        raise RuntimeError("boom-eq-obj")


class EqRaiseStr(str):
    """Text form holding a stored identifier, equality raises."""

    __hash__ = str.__hash__

    def __eq__(self, other):
        raise RuntimeError("boom-eq-str")

    def __ne__(self, other):
        raise RuntimeError("boom-eq-str")


class StrRaisesStr(str):
    """Text form whose string reading raises."""

    def __str__(self):
        raise RuntimeError("boom-str")


class ObjStrRaises:
    """Plain object whose string reading raises."""

    def __str__(self):
        raise RuntimeError("boom-str-obj")


class BadEq:
    """A firing in no stated form whose equality reading raises."""

    def __eq__(self, other):
        raise RuntimeError("boom-eq-firing")

    def __ne__(self, other):
        raise RuntimeError("boom-eq-firing")

    __hash__ = object.__hash__


def build_victim_standing():
    mod10.retain_run_record({"run_id": VICTIM, "marker": "runrec"})
    mod10.write_summary_record(
        {"run_id": VICTIM, "retention_tier": "Tier 3"})
    mod10.retain_checkpoint(
        {"run_identifier": VICTIM, "simulated_day": 1})
    mod10.retain_checkpoint(
        {"run_identifier": VICTIM, "simulated_day": 2})
    mod10.retain_event_log_entry(
        {"run_identifier": VICTIM, "note": "e1"})
    mod10.retain_daily_snapshot(
        {"run_identifier": VICTIM, "note": "s1"})
    mod10.retain_gc08_record("call_log", {"log": "g1"}, VICTIM)
    mod10.place_reserve_hold(VICTIM)


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR18014LyingIdentifier(Base):
    def setUp(self):
        super().setUp()
        build_victim_standing()

    def test_lying_read_and_has_fresh_store(self):
        store = mod10.new_store()
        store.retain_run_record({"run_id": VICTIM, "marker": "runrec"})
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record(LieAll(VICTIM))
        self.assertFalse(store.has_run_record(LieAll(VICTIM)))

    def test_lying_run_records_for_run(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.run_records_for_run(LieAll(VICTIM))

    def test_lying_checkpoints(self):
        self.assertEqual(mod10.checkpoints_for_run(LieAll(VICTIM)), [])

    def test_lying_event_log_entries(self):
        self.assertEqual(mod10.event_log_entries(LieAll(VICTIM)), [])

    def test_lying_daily_snapshots(self):
        self.assertEqual(mod10.daily_snapshots(LieAll(VICTIM)), [])

    def test_lying_gc08_record(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", LieAll(VICTIM))

    def test_lying_reserve_hold(self):
        self.assertIsNone(mod10.reserve_hold_for_run(LieAll(VICTIM)))

    def test_lying_retention_record(self):
        record = mod10.retention_record_for_run(LieAll(VICTIM))
        self.assertNotEqual(record["retention_tier"], "Tier 3")
        self.assertEqual(record["tier_forms"], [])
        self.assertEqual(record["retained_forms"], [])

    def test_lying_summary_record(self):
        record = mod10.summary_record_for_run(LieAll(VICTIM))
        self.assertNotEqual(record.get("retention_tier"), "Tier 3")
        self.assertFalse(record.get("record_found", False))

    def test_plain_controls(self):
        store = mod10.new_store()
        store.retain_run_record({"run_id": VICTIM, "marker": "runrec"})
        self.assertEqual(
            store.read_run_record(VICTIM)["marker"], "runrec")
        self.assertTrue(store.has_run_record(VICTIM))
        self.assertFalse(store.has_run_record("nope-b6"))
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record("nope-b6")
        self.assertEqual(len(mod10.checkpoints_for_run(VICTIM)), 2)
        self.assertEqual(len(mod10.event_log_entries(VICTIM)), 1)
        self.assertEqual(len(mod10.daily_snapshots(VICTIM)), 1)
        self.assertEqual(
            mod10.gc08_record("call_log", VICTIM)["log"], "g1")
        self.assertIsNotNone(mod10.reserve_hold_for_run(VICTIM))
        self.assertEqual(mod10.checkpoints_for_run("nope-b6"), [])
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", "nope-b6")
        self.assertIsNone(mod10.reserve_hold_for_run("nope-b6"))


class TestR18042RaisingIdentifier(Base):
    def setUp(self):
        super().setUp()
        build_victim_standing()

    def test_raising_collection_reads(self):
        self.assertEqual(
            mod10.checkpoints_for_run(EqRaisesObj(VICTIM)), [])
        self.assertEqual(
            mod10.event_log_entries(EqRaisesObj(VICTIM)), [])
        self.assertEqual(
            mod10.daily_snapshots(EqRaisesObj(VICTIM)), [])

    def test_raising_gc08_and_reserve(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", EqRaisesObj(VICTIM))
        self.assertIsNone(
            mod10.reserve_hold_for_run(EqRaisesObj(VICTIM)))

    def test_raising_read_and_has_fresh_store(self):
        store = mod10.new_store()
        store.retain_run_record({"run_id": VICTIM, "marker": "runrec"})
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record(EqRaisesObj(VICTIM))
        self.assertFalse(store.has_run_record(EqRaisesObj(VICTIM)))

    def test_summary_pole_control(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.summary_record_for_run(EqRaisesObj(VICTIM))

    def test_stored_side_plain_read(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": EqRaiseStr(VICTIM), "marker": "storedside"})
        record = store.read_run_record(VICTIM)
        self.assertEqual(record["marker"], "storedside")

    def test_stored_side_second_retain(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": EqRaiseStr(VICTIM), "marker": "storedside"})
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                {"run_id": EqRaiseStr(VICTIM), "marker": "again"})
        self.assertIn("second record", str(caught.exception))

    def test_unhashable_control(self):
        store = mod10.new_store()
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record(["unhashable"])
        with self.assertRaises(mod10.LookupFailure):
            store.has_run_record(["unhashable"])


class TestR18034DuplicateSentence(Base):
    def test_run_identifier_str_raises(self):
        manifest = {
            "run_identifier": StrRaisesStr("b6-r34a"),
            "simulated_day": 3,
        }
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            str(caught.exception))

    def test_day_str_raises(self):
        manifest = {
            "run_identifier": "b6-r34b",
            "simulated_day": ObjStrRaises(),
        }
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "second checkpoint for the same run and day is rejected",
            str(caught.exception))

    def test_plain_control(self):
        manifest = {"run_identifier": "b6-r34c", "simulated_day": 3}
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        text = str(caught.exception)
        self.assertIn("b6-r34c", text)
        self.assertIn("day 3", text)


class TestR18035LeakCheckRendering(Base):
    def test_canary_field_str_raises(self):
        record = mod04.build_view_record()
        record[StrRaisesStr("extra_field")] = {"label": 1}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("view leak check failure", str(caught.exception))
        self.assertIn("canary", str(caught.exception))

    def test_timing_item_str_raises_nonfinite(self):
        record = mod04.build_view_record()
        record["first_seen_day_per_record"] = {
            ObjStrRaises(): float("inf")}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("view leak check failure", str(caught.exception))
        self.assertIn("non finite", str(caught.exception))

    def test_timing_item_str_raises_first_seen(self):
        record = mod04.build_view_record()
        record["first_seen_day_per_record"] = {ObjStrRaises(): 5}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("view leak check failure", str(caught.exception))
        self.assertIn("first seen after", str(caught.exception))

    def test_plain_control(self):
        record = mod04.build_view_record()
        result = mod10.run_view_leak_check(record)
        self.assertTrue(result["reportable"])


class TestR18043RestoreCheck(Base):
    def test_raising_identifier(self):
        result = mod10.restore_check(
            {"relative_identifier": EqRaisesObj("a")}, {"a"})
        self.assertFalse(result)

    def test_raising_present_element(self):
        result = mod10.restore_check(
            {"relative_identifier": "a"}, {EqRaisesObj("a")})
        self.assertFalse(result)

    def test_controls(self):
        portable = {"relative_identifier": "checkpoints/a"}
        self.assertTrue(
            mod10.restore_check(portable, {"checkpoints/a"}))
        self.assertFalse(mod10.restore_check(portable, {"other"}))
        with self.assertRaises(ValueError) as caught:
            mod10.restore_check({"relative_identifier": ["x"]}, {"a"})
        self.assertIn("restore_check", str(caught.exception))


class TestR18055DeferredEscape(Base):
    def test_raising_firing_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_deferred_evaluation(
                {"run_id": "b6-d1"}, BadEq(), inputs={}, outcome="x")
        self.assertIn("stands outside the stated firings",
                      str(caught.exception))

    def test_controls(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_deferred_evaluation(
                {"run_id": "b6-d2"}, "1", inputs={}, outcome="x")
        self.assertIn("stands outside the stated firings",
                      str(caught.exception))
        updated = mod10.apply_deferred_evaluation(
            {"run_id": "b6-d3"}, 1, inputs={"a": 1}, outcome="o1")
        self.assertEqual(
            updated["deferred_evaluations"][0]["firing"], 1)


class TestR18056StoreLookup(Base):
    def setUp(self):
        super().setUp()
        mod10.retain_run_record({"run_id": "lk-b6", "marker": "route"})

    def test_generator_single_kind(self):
        record = mod10.store_lookup(
            store_kinds=iter(["sweep"]), key="lk-b6")
        self.assertEqual(record["marker"], "route")

    def test_map_single_kind(self):
        record = mod10.store_lookup(
            store_kinds=map(str, ["sweep"]), key="lk-b6")
        self.assertEqual(record["marker"], "route")

    def test_controls(self):
        self.assertEqual(
            mod10.store_lookup(
                store_kinds=["sweep"], key="lk-b6")["marker"], "route")
        self.assertEqual(
            mod10.store_lookup(
                store_kinds=("sweep",), key="lk-b6")["marker"], "route")
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(
                store_kinds=["sweep", "pilot"], key="lk-b6")
        self.assertIn("exactly one store kind", str(caught.exception))
        with self.assertRaises(ValueError):
            mod10.store_lookup(
                store_kinds=iter(["sweep", "pilot"]), key="lk-b6")
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(store_kinds=["bogus"], key="lk-b6")
        self.assertIn("unknown store kind", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

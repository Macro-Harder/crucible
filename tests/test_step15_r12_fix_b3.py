"""Pin tests for fix wave 11, Builder 3, MOD-10 rows R11-009 to
R11-012 and R11-016 to R11-035, under settlements S-1 and S-2.

Each test states the exact proving act of its source paper:
the dressed form the register charges, beside a plain control
that must keep its standing.
"""

import datetime
import pathlib
import unittest
import uuid
from decimal import Decimal
from fractions import Fraction

from crucible import mod04
from crucible import mod10


class LyingLeaf:
    def __init__(self, raising=False):
        self._raising = raising

    def __deepcopy__(self, memo):
        if self._raising:
            raise RuntimeError("boom from copy protocol")
        return "TAMPERED"

    def __copy__(self):
        return "TAMPERED"


class ReduceLeaf:
    def __reduce_ex__(self, protocol):
        return (str, ("REBUILT",))


class LyingGetDict(dict):
    def __init__(self, stored, reported=None, raising=False):
        super().__init__(stored)
        self._reported = reported or {}
        self._raising = raising

    def get(self, key, default=None):
        if self._raising:
            raise RuntimeError("boom from get reading")
        if key in self._reported:
            return self._reported[key]
        return super().get(key, default)


class LyingGetItemDict(dict):
    def __getitem__(self, key):
        if key == "checkpoint_state":
            return {"fabricated": True}
        return super().__getitem__(key)


def chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def delivery(day, viewer="v", **extra):
    base = {"simulated_day": day, "viewer_id": viewer}
    base.update(extra)
    return base


def manifest(run="run-b3", day=5, state=None, **extra):
    base = {"run_identifier": run, "run_id": run, "simulated_day": day}
    if state is not None:
        base["checkpoint_state"] = state
    base.update(extra)
    return base


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR11009StateAtCopy(Base):
    def test_lying_leaf_direct_and_nested(self):
        leaf = LyingLeaf()
        mod10.retain_checkpoint(manifest(state={"a": [leaf]}))
        got = mod10.checkpoint_state_at("run-b3", 5)
        self.assertIs(got["a"][0], leaf)

    def test_lying_leaf_through_mod04_write(self):
        leaf = LyingLeaf()
        result = mod04.write_checkpoint(
            {"run_identifier": "run-b3m", "run_id": "run-b3m",
             "simulated_day": 3},
            agent_states=[{"leaf": leaf}],
            escrow_contract_states=[],
            detection_state={"state": "stated"},
            stream_positions_and_generator_states={},
            simulation_clock_value=leaf)
        got = mod10.checkpoint_state_at("run-b3m", 3)
        self.assertIs(got["simulation_clock_value"], leaf)
        self.assertIs(result["checkpoint_state"]["simulation_clock_value"], leaf)

    def test_reduce_leaf_reads_back_as_itself(self):
        leaf = ReduceLeaf()
        mod10.retain_checkpoint(manifest(state={"leaf": leaf}))
        got = mod10.checkpoint_state_at("run-b3", 5)
        self.assertIs(got["leaf"], leaf)

    def test_raising_leaf_does_not_escape(self):
        leaf = LyingLeaf(raising=True)
        mod10.retain_checkpoint(manifest(state={"leaf": leaf}))
        got = mod10.checkpoint_state_at("run-b3", 5)
        self.assertIs(got["leaf"], leaf)


class TestR11010PlainDeepcopySites(Base):
    def test_portable_manifest_copy(self):
        leaf = LyingLeaf()
        out = mod10.portable_checkpoint_manifest(manifest(extra=leaf))
        self.assertIs(out["manifest"]["extra"], leaf)

    def test_resume_both_paths_copy(self):
        leaf = LyingLeaf()
        mod10.retain_checkpoint(manifest(payload=leaf))
        handed = manifest(payload=leaf)
        self.assertIs(mod10.resume_from_checkpoint(handed)["payload"], leaf)
        orphan = manifest(run="run-none", payload=leaf)
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(orphan)
        self.assertIn(
            "checkpoint integrity refusal", str(caught.exception))

    def test_append_annotation_both_values(self):
        leaf = LyingLeaf()
        out = mod10.append_annotation(manifest(payload=leaf), {"note": leaf})
        self.assertIs(out["payload"], leaf)
        self.assertIs(out["annotation_record"]["note"], leaf)

    def test_rejected_writes_read_back(self):
        leaf = LyingLeaf()
        mod10.retain_checkpoint(manifest())
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(manifest(payload=leaf))
        got = mod10.rejected_checkpoint_writes("run-b3")
        self.assertIs(got[0]["manifest"]["payload"], leaf)

    def test_gc08_retain_and_read(self):
        leaf = LyingLeaf()
        out = mod10.retain_gc08_record(
            "dependency_manifest", {"leaf": leaf}, "owner-1")
        self.assertIs(out["leaf"], leaf)
        got = mod10.gc08_record("dependency_manifest", "owner-1")
        self.assertIs(got["leaf"], leaf)

    def test_gate_share_copy(self):
        leaf = LyingLeaf()
        out = mod10.record_gate_passing_share("run-b3", "epoch-1", leaf)
        self.assertIs(out["share"], leaf)
        got = mod10.gate_passing_shares_for_run("run-b3")
        self.assertIs(got["epoch-1"]["share"], leaf)

    def test_aggregate_family_copy(self):
        leaf = LyingLeaf()
        mod10.retain_daily_aggregate_deliveries(
            "run-b3", [delivery(5, divergence_companion={"leaf": leaf})])
        records = mod10.daily_aggregates_for_run("run-b3")
        self.assertIs(records[0]["divergence_companion"]["leaf"], leaf)
        leaf2 = LyingLeaf()
        mod10.retain_daily_aggregate_deliveries(
            "run-b3x", [delivery(5, honest_share=leaf2)])
        records = mod10.daily_aggregates_for_run("run-b3x")
        self.assertIs(records[0]["honest_share"], leaf2)


class TestR11011BufferForms(Base):
    def test_memoryview_day_viewer_and_nested_delivery(self):
        self.assertEqual(mod10.retain_daily_aggregate_deliveries(
            "r1", [delivery(memoryview(b"5"))]), 1)
        self.assertEqual(mod10.retain_daily_aggregate_deliveries(
            "r2", [delivery(5, viewer=memoryview(b"v1"))]), 1)
        self.assertEqual(mod10.retain_daily_aggregate_deliveries(
            "r3", [delivery(5, divergence_companion={
                "x": memoryview(b"z")})]), 1)
        records = mod10.daily_aggregates_for_run("r3")
        self.assertEqual(
            bytes(records[0]["divergence_companion"]["x"]), b"z")

    def test_memoryview_checkpoint_state_and_resume(self):
        mod10.retain_checkpoint(manifest(
            state={"x": memoryview(b"s")}))
        got = mod10.checkpoint_state_at("run-b3", 5)
        self.assertEqual(bytes(got["x"]), b"s")
        mod10.retain_checkpoint(manifest(
            run="run-b3r", payload=memoryview(b"p")))
        handed = manifest(run="run-b3r", payload=memoryview(b"p"))
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(bytes(resumed["payload"]), b"p")


class TestR11012UnhashableDays(Base):
    def test_list_day_with_state_retains_and_reads(self):
        mod10.retain_checkpoint(manifest(day=[5], state={"k": 1}))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 1)
        self.assertEqual(mod10.checkpoint_state_at("run-b3", [5]), {"k": 1})

    def test_bytearray_day_with_state_retains_and_reads(self):
        mod10.retain_checkpoint(manifest(
            day=bytearray(b"5"), state={"k": 2}))
        self.assertEqual(
            mod10.checkpoint_state_at("run-b3", bytearray(b"5")), {"k": 2})

    def test_state_query_at_dict_and_set_day_answers_none(self):
        mod10.retain_checkpoint(manifest(state={"k": 1}))
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", {"d": 5}))
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", {5}))


class TestR11016StateAtMatchForm(Base):
    def test_float_retained_not_returned_for_int_family_queries(self):
        mod10.retain_checkpoint(manifest(day=5.0, state={"k": "f"}))
        for query in (5, Decimal("5"), Fraction(5, 1)):
            self.assertIsNone(mod10.checkpoint_state_at("run-b3", query))
        self.assertEqual(mod10.checkpoint_state_at("run-b3", 5.0), {"k": "f"})

    def test_bool_retained_not_returned_for_int_query(self):
        mod10.retain_checkpoint(manifest(day=True, state={"k": "b"}))
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", 1))
        self.assertEqual(mod10.checkpoint_state_at("run-b3", True), {"k": "b"})

    def test_decimal_retained_not_returned_for_fraction_query(self):
        mod10.retain_checkpoint(manifest(day=Decimal("5.5"), state={"k": "d"}))
        self.assertIsNone(
            mod10.checkpoint_state_at("run-b3", Fraction(11, 2)))
        self.assertEqual(
            mod10.checkpoint_state_at("run-b3", Decimal("5.5")), {"k": "d"})

    def test_memoryview_retained_not_returned_for_bytes_query(self):
        mod10.retain_checkpoint(manifest(
            day=memoryview(b"5"), state={"k": "m"}))
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", b"5"))
        self.assertEqual(
            mod10.checkpoint_state_at("run-b3", memoryview(b"5")), {"k": "m"})


class TestR11017MinusTextDay(Base):
    def test_minus_text_deliveries_merge(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "run-b3", [delivery(-5), delivery("-5")])
        self.assertEqual(count, 1)

    def test_minus_text_checkpoint_duplicate_refused(self):
        mod10.retain_checkpoint(manifest(day=-5))
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(manifest(day="-5"))


class TestR11018PaddedDaySort(Base):
    def test_padded_day_sorts_as_its_number(self):
        mod10.retain_daily_aggregate_deliveries(
            "run-b3", [delivery(100), delivery(" 5 ")])
        records = mod10.daily_aggregates_for_run("run-b3")
        self.assertEqual(records[0]["simulated_day"], " 5 ")
        self.assertEqual(records[1]["simulated_day"], 100)


class TestR11019StoredFormFallback(Base):
    def test_stored_forms_carry_values(self):
        self.assertNotEqual(
            mod10._stored_form(datetime.date(2026, 1, 1)),
            mod10._stored_form(datetime.date(2026, 1, 2)))
        self.assertNotEqual(
            mod10._stored_form(uuid.UUID(int=1)),
            mod10._stored_form(uuid.UUID(int=2)))
        self.assertNotEqual(
            mod10._stored_form(datetime.timedelta(days=1)),
            mod10._stored_form(datetime.timedelta(days=2)))

    def test_date_days_and_uuid_viewers_retained_apart(self):
        count = mod10.retain_daily_aggregate_deliveries("run-b3", [
            delivery(datetime.date(2026, 1, 1)),
            delivery(datetime.date(2026, 1, 2))])
        self.assertEqual(count, 2)
        count = mod10.retain_daily_aggregate_deliveries("run-b3u", [
            delivery(5, viewer=uuid.UUID(int=1)),
            delivery(5, viewer=uuid.UUID(int=2))])
        self.assertEqual(count, 2)


class TestR11020IntegralDecimalFraction(Base):
    def test_integral_forms_retained_as_one_day(self):
        count = mod10.retain_daily_aggregate_deliveries("run-b3", [
            delivery(5), delivery(Decimal("5")),
            delivery(Decimal("5.0")), delivery(Fraction(5, 1))])
        self.assertEqual(count, 1)
        records = mod10.daily_aggregates_for_run("run-b3")
        self.assertEqual(len(records), 1)


class TestR11021BytesFamilyStandings(Base):
    def test_bytes_pair_duplicate_stands_distinct(self):
        mod10.retain_checkpoint(manifest(day=b"5"))
        mod10.retain_checkpoint(manifest(day=bytearray(b"5")))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 2)

    def test_bytes_day_sorts_in_later_group_not_numbered(self):
        mod10.retain_daily_aggregate_deliveries(
            "run-b3", [delivery(b"5"), delivery(100)])
        records = mod10.daily_aggregates_for_run("run-b3")
        self.assertEqual(records[0]["simulated_day"], 100)
        self.assertEqual(records[1]["simulated_day"], b"5")

    def test_bytes_family_retention_stays_three(self):
        count = mod10.retain_daily_aggregate_deliveries("run-b3", [
            delivery(b"5"), delivery(bytearray(b"5")), delivery("5")])
        self.assertEqual(count, 3)


class TestR11022DuplicateMatchForm(Base):
    def test_float_and_bool_after_int_accepted(self):
        mod10.retain_checkpoint(manifest(day=5))
        mod10.retain_checkpoint(manifest(day=5.0))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 2)
        mod10.retain_checkpoint(manifest(run="run-b3b", day=1))
        mod10.retain_checkpoint(manifest(run="run-b3b", day=True))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3b")), 2)

    def test_container_float_after_int_accepted(self):
        mod10.retain_checkpoint(manifest(day=[5]))
        mod10.retain_checkpoint(manifest(day=[5.0]))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 2)


class TestR11023BaseValueEqUnnamed(Base):
    def test_resume_equal_copies_of_unnamed_types(self):
        pairs = [
            (datetime.date(2026, 1, 1), datetime.date(2026, 1, 1)),
            (uuid.UUID(int=7), uuid.UUID(int=7)),
            (datetime.timedelta(days=3), datetime.timedelta(days=3)),
            (pathlib.Path("a/b"), pathlib.Path("a/b")),
        ]
        for retained_value, handed_value in pairs:
            mod10.reset_stores()
            mod10.retain_checkpoint(manifest(payload=retained_value))
            handed = manifest(payload=handed_value)
            resumed = mod10.resume_from_checkpoint(handed)
            self.assertEqual(resumed["payload"], retained_value)


class TestR11024PortableIdentity(Base):
    def test_run_and_day_split_collisions(self):
        first = mod10.portable_checkpoint_manifest(
            manifest(run="a/b", day="c"))
        second = mod10.portable_checkpoint_manifest(
            manifest(run="a", day="b/c"))
        self.assertNotEqual(
            first["relative_identifier"], second["relative_identifier"])
        self.assertFalse(mod10.restore_check(
            second, {first["relative_identifier"]}))

    def test_day_form_collisions(self):
        pairs = [
            (None, "None"), (True, "True"), (5.0, "5.0"),
            (datetime.date(2026, 1, 1), "2026-01-01"),
            (b"5", "b'5'"), (Decimal("5.5"), "5.5"), (1, "1"),
        ]
        for left, right in pairs:
            one = mod10.portable_checkpoint_manifest(manifest(day=left))
            two = mod10.portable_checkpoint_manifest(manifest(day=right))
            self.assertNotEqual(
                one["relative_identifier"], two["relative_identifier"],
                (left, right))


class TestR11025DeletionRemovesState(Base):
    def test_delete_removes_state_and_no_inheritance(self):
        mod10.retain_checkpoint(manifest(state={"k": "OLD"}))
        mod10.delete_checkpoint(
            "run-b3", 5, trigger="clause C5 trigger",
            rule_path="deletion rule path")
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", 5))
        mod10.retain_checkpoint(manifest())
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", 5))

    def test_close_releases_state(self):
        mod10.retain_checkpoint(manifest(day=5, state={"k": 5}))
        mod10.retain_checkpoint(manifest(day=6, state={"k": 6}))
        mod10.close_run_retention("run-b3", "Tier 0")
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", 5))
        self.assertIsNone(mod10.checkpoint_state_at("run-b3", 6))


class TestR11026CloseAllDayForms(Base):
    def test_tier0_non_integer_day_released_and_named(self):
        mod10.retain_checkpoint(manifest(day="abc"))
        result = mod10.close_run_retention("run-b3", "Tier 0")
        self.assertEqual(result["kept_days"], [])
        self.assertEqual(result["released_days"], ["abc"])
        self.assertEqual(mod10.checkpoints_for_run("run-b3"), [])

    def test_mixed_close_names_every_released_day(self):
        days = [1, 2, 3, "abc", 9.5, datetime.date(2026, 1, 2),
                Decimal("20")]
        for day in days:
            mod10.retain_checkpoint(manifest(day=day))
        result = mod10.close_run_retention("run-b3", "Tier 1")
        named = result["kept_days"] + result["released_days"]
        self.assertEqual(len(named), len(days))
        for day in days:
            self.assertIn(day, named)
        remaining = mod10.checkpoints_for_run("run-b3")
        self.assertEqual(len(remaining), len(result["kept_days"]))

    def test_decimal_final_day_kept_at_tier1(self):
        mod10.retain_checkpoint(manifest(day=3))
        mod10.retain_checkpoint(manifest(day=Decimal("20")))
        result = mod10.close_run_retention("run-b3", "Tier 1")
        self.assertEqual(result["kept_days"], [Decimal("20")])
        self.assertEqual(result["released_days"], [3])

    def test_tier2_integer_control(self):
        for day in range(1, 13):
            mod10.retain_checkpoint(manifest(run="run-t2", day=day))
        result = mod10.close_run_retention("run-t2", "Tier 2")
        self.assertEqual(result["kept_days"], [10, 12])
        self.assertEqual(len(result["released_days"]), 10)


class TestR11027DeleteMatchForm(Base):
    def _delete(self, run, day):
        return mod10.delete_checkpoint(
            run, day, trigger="clause C5 trigger",
            rule_path="deletion rule path")

    def test_float_and_bool_do_not_delete_int(self):
        mod10.retain_checkpoint(manifest(day=5))
        self.assertEqual(self._delete("run-b3", 5.0)["removed"], 0)
        mod10.retain_checkpoint(manifest(run="run-b3b", day=1))
        self.assertEqual(self._delete("run-b3b", True)["removed"], 0)

    def test_list_float_does_not_delete_list_int(self):
        mod10.retain_checkpoint(manifest(day=[5]))
        self.assertEqual(self._delete("run-b3", [5.0])["removed"], 0)

    def test_minus_text_and_decimal_delete_int(self):
        mod10.retain_checkpoint(manifest(day=-5))
        self.assertEqual(self._delete("run-b3", "-5")["removed"], 1)
        mod10.retain_checkpoint(manifest(run="run-b3d", day=5))
        self.assertEqual(self._delete("run-b3d", Decimal("5"))["removed"], 1)


class TestR11028SnapshotEventDuplicate(Base):
    def test_snapshot_distinct_day_forms_retained(self):
        snap = {"run_identifier": "run-b3", "simulated_day": 5,
                "payload": "x"}
        mod10.retain_daily_snapshot(snap)
        mod10.retain_daily_snapshot({**snap, "simulated_day": 5.0})
        self.assertEqual(len(mod10.daily_snapshots("run-b3")), 2)
        mod10.retain_daily_snapshot({**snap, "simulated_day": b"5"})
        mod10.retain_daily_snapshot(
            {**snap, "simulated_day": bytearray(b"5")})
        self.assertEqual(len(mod10.daily_snapshots("run-b3")), 4)
        mod10.retain_daily_snapshot({**snap, "simulated_day": 5})
        self.assertEqual(len(mod10.daily_snapshots("run-b3")), 4)

    def test_event_log_distinct_day_forms_retained(self):
        entry = {"run_identifier": "run-b3", "simulated_day": 5,
                 "payload": "x"}
        mod10.retain_event_log_entry(entry)
        mod10.retain_event_log_entry(
            {**entry, "simulated_day": Decimal("5")})
        self.assertEqual(len(mod10.event_log_entries("run-b3")), 2)
        mod10.retain_event_log_entry(dict(entry))
        self.assertEqual(len(mod10.event_log_entries("run-b3")), 2)


class TestR11029GateShareEpochForms(Base):
    def test_int_bool_float_epochs_kept_apart(self):
        mod10.record_gate_passing_share("run-b3", 1, "share-int")
        mod10.record_gate_passing_share("run-b3", True, "share-bool")
        mod10.record_gate_passing_share("run-b3", 1.0, "share-float")
        got = mod10.gate_passing_shares_for_run("run-b3")
        self.assertEqual(len(got), 3)
        shares = sorted(item["share"] for item in got.values())
        self.assertEqual(
            shares, ["share-bool", "share-float", "share-int"])


class TestR11030RetainHandedReadings(Base):
    def test_lying_get_retains_under_stored_identity(self):
        handed = LyingGetDict(
            manifest(day=3, state={"k": "stored"}),
            reported={"run_identifier": "fabricated-run",
                      "run_id": "fabricated-run", "simulated_day": 99})
        mod10.retain_checkpoint(handed)
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 1)
        self.assertEqual(mod10.checkpoints_for_run("fabricated-run"), [])
        self.assertEqual(mod10.checkpoint_state_at("run-b3", 3),
                         {"k": "stored"})
        self.assertIsNone(
            mod10.checkpoint_state_at("fabricated-run", 99))

    def test_raising_get_does_not_escape(self):
        handed = LyingGetDict(manifest(day=3), raising=True)
        mod10.retain_checkpoint(handed)
        self.assertEqual(len(mod10.checkpoints_for_run("run-b3")), 1)

    def test_lying_getitem_state_reads_stored_state(self):
        handed = LyingGetItemDict(manifest(state={"k": "stored"}))
        mod10.retain_checkpoint(handed)
        self.assertEqual(mod10.checkpoint_state_at("run-b3", 5),
                         {"k": "stored"})


class TestR11031PositionCheckHanded(Base):
    def test_lying_get_judged_by_stored_position(self):
        mod10.retain_event_log_entry(
            {"run_identifier": "run-b3", "payload": "x"})
        handed = LyingGetDict(
            {"run_identifier": "run-b3", "journal_position": 9999},
            reported={"journal_position": 1})
        result = mod10.checkpoint_position_check(handed)
        self.assertFalse(result["reportable"])
        self.assertEqual(result["journal_position"], 9999)

    def test_raising_get_does_not_escape(self):
        handed = LyingGetDict(
            {"run_identifier": "run-b3", "journal_position": 1},
            raising=True)
        result = mod10.checkpoint_position_check(handed)
        self.assertIn("outcome", result)


class TestR11032PortableHanded(Base):
    def test_lying_get_identifier_uses_stored(self):
        handed = LyingGetDict(
            manifest(run="stored-run", day=5),
            reported={"run_identifier": "fabricated-run",
                      "run_id": "fabricated-run", "simulated_day": 99})
        out = mod10.portable_checkpoint_manifest(handed)
        self.assertNotIn("fabricated-run", out["relative_identifier"])
        self.assertNotIn("/99", out["relative_identifier"])

    def test_raising_get_does_not_escape(self):
        handed = LyingGetDict(manifest(), raising=True)
        out = mod10.portable_checkpoint_manifest(handed)
        self.assertTrue(out["portable"])


class TestR11033GuardRefusalForm(Base):
    def test_deep_refusal_names_act_argument_bound_and_cause(self):
        handed = manifest(extra=chain(101))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(handed)
        text = str(caught.exception)
        self.assertIn("retain_checkpoint", text)
        self.assertIn("manifest", text)
        self.assertIn("100", text)
        self.assertIn("depth", text)

    def test_cycle_refusal_differs_and_names_cause(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(manifest(extra=cyclic))
        text = str(caught.exception)
        self.assertIn("cycle", text)
        self.assertIn("retain_checkpoint", text)
        with self.assertRaises(ValueError) as caught2:
            mod10.retain_checkpoint(manifest(extra=chain(101)))
        self.assertNotEqual(text, str(caught2.exception))

    def test_other_retention_acts_name_themselves(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_event_log_entry(
                {"run_identifier": "run-b3", "extra": chain(101)})
        self.assertIn("retain_event_log_entry", str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_snapshot(
                {"run_identifier": "run-b3", "extra": chain(101)})
        self.assertIn("retain_daily_snapshot", str(caught.exception))


class TestR11034DeleteProtectionNames(Base):
    def test_each_protection_named(self):
        mod10.retain_checkpoint(manifest())
        cases = [
            ({"integrity_flag_open": True}, "integrity"),
            ({"named_in_retention_record": True}, "retention record"),
            ({"regression_corpus_copy": True}, "regression corpus"),
        ]
        texts = []
        for kwargs, word in cases:
            with self.assertRaises(ValueError) as caught:
                mod10.delete_checkpoint(
                    "run-b3", 5, trigger="clause C5 trigger",
                    rule_path="deletion rule path", **kwargs)
            self.assertIn(word, str(caught.exception))
            texts.append(str(caught.exception))
        self.assertEqual(len(set(texts)), 3)


class TestR11035NonRecordNamedForm(Base):
    def test_append_annotation_non_record(self):
        for bad in ("text", [1], None):
            with self.assertRaises(ValueError):
                mod10.append_annotation(bad, {"note": 1})

    def test_portable_non_record(self):
        for bad in ("text", None):
            with self.assertRaises(ValueError):
                mod10.portable_checkpoint_manifest(bad)


if __name__ == "__main__":
    unittest.main()

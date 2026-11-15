"""Step 15 second run, fix wave 13 pins, Builder 2.

Pins for rows R13-005 to R13-009 of the Round 13 register, the
MOD-10 direct acts: apply_flag_evaluation judged directly at
row R13-005, the identity acts at row R13-006, run_view_leak_check
at row R13-007, storage_accounting at row R13-008, and the
deliveries keying limbs at row R13-009, proved on the acts of
Blue 2 Findings 1 to 5 and Red 2 Finding 4 of the Round 13
papers.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10


class LyingGetDict(dict):
    """A dict storing one set of values and reporting another
    set through its own get reading, for the keys named in the
    reported mapping. Every other key reads as stored."""

    def __init__(self, stored, reported=None):
        super().__init__(stored)
        self._reported = dict(reported or {})

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return dict.get(self, key, default)


class LenLyingDict(dict):
    """A dict whose length reading reports zero whatever it
    stores."""

    def __len__(self):
        return 0


def view_record(day=10, first_seen=None):
    return {
        "run_identifier": "run-b2",
        "viewer_identifier": "viewer-1",
        "simulated_day": day,
        "scheduling_position_identifier": "position-1",
        "rule_version_set": "rule-set-1",
        "view_contents": {"note": "clean"},
        "reputation_and_band_values": {"band": "stated"},
        "graph_position_as_seen": "stated",
        "first_seen_day_per_record": (
            {"item": 3} if first_seen is None else first_seen),
        "delay_applied_per_record": {"item": 1},
        "completeness_state": "complete",
        "building_component": "Recorder",
        "delivering_contract": "stated",
        "selection_rule_version": "rule-set-1",
    }


def delivery(day, viewer, **extra):
    base = {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [10, 10, 10, 10],
        "honest_share": 1,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 1},
    }
    base.update(extra)
    return base


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def promote(self, record, inputs):
        return mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            actor="program", inputs=inputs)


class TestR13005DirectFlagAct(B2Base):
    def test_plain_controls_stand_both_ways(self):
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": []}
        with self.assertRaises(ValueError):
            self.promote(record, {})
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": ["condition a"]}
        result = self.promote(
            record, {"flag_conditions_fired": ["condition a"]})
        self.assertEqual(result["retention_tier"], "Tier 2")
        record = {"retention_tier": "Tier 3",
                  "flag_conditions_fired": ["condition a"]}
        with self.assertRaises(ValueError):
            self.promote(
                record, {"flag_conditions_fired": ["condition a"]})

    def test_inputs_reporting_fired_they_do_not_store_refused(self):
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": []}
        inputs = LyingGetDict(
            {}, {"flag_conditions_fired": ["condition a"]})
        with self.assertRaises(ValueError) as caught:
            self.promote(record, inputs)
        self.assertIn("no stated flag condition", str(caught.exception))

    def test_record_reporting_fired_it_does_not_store_refused(self):
        record = LyingGetDict(
            {"retention_tier": "Tier 1", "flag_conditions_fired": []},
            {"flag_conditions_fired": ["condition a"]})
        with self.assertRaises(ValueError) as caught:
            self.promote(record, {})
        self.assertIn("no stated flag condition", str(caught.exception))

    def test_inputs_storing_fired_they_report_empty_promotes(self):
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": []}
        inputs = LyingGetDict(
            {"flag_conditions_fired": ["condition a"]},
            {"flag_conditions_fired": []})
        result = self.promote(record, inputs)
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_both_reporting_empty_where_stored_fired_promotes(self):
        record = LyingGetDict(
            {"retention_tier": "Tier 1",
             "flag_conditions_fired": ["condition a"]},
            {"flag_conditions_fired": []})
        inputs = LyingGetDict(
            {"flag_conditions_fired": ["condition a"]},
            {"flag_conditions_fired": []})
        result = self.promote(record, inputs)
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_tier_reported_lower_stands_no_demotion(self):
        record = LyingGetDict(
            {"retention_tier": "Tier 3",
             "flag_conditions_fired": ["condition a"]},
            {"retention_tier": "Tier 1"})
        with self.assertRaises(ValueError) as caught:
            self.promote(
                record, {"flag_conditions_fired": ["condition a"]})
        self.assertIn("never demotes", str(caught.exception))


class TestR13006IdentityActs(B2Base):
    def test_plain_controls_stand(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record({"payload": "x"})
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry({"payload": "x"})
        with self.assertRaises(ValueError):
            mod10.retain_daily_snapshot({"payload": "x"})
        mod10.retain_run_record({"run_id": "plain-run", "payload": "x"})
        self.assertEqual(
            mod10.read_run_record("plain-run")["payload"], "x")

    def test_run_record_retained_under_stored_identity_only(self):
        record = LyingGetDict(
            {"payload": "x"}, {"run_id": "fake-run"})
        with self.assertRaises(ValueError):
            mod10.retain_run_record(record)

    def test_run_record_stored_identity_governs_over_reported(self):
        record = LyingGetDict(
            {"run_id": "real-run", "payload": "x"},
            {"run_id": "fake2"})
        mod10.retain_run_record(record)
        self.assertEqual(
            mod10.read_run_record("real-run")["run_id"], "real-run")
        with self.assertRaises(mod10.LookupFailure):
            mod10.read_run_record("fake2")

    def test_event_log_entry_retained_under_stored_identity_only(self):
        entry = LyingGetDict(
            {"payload": "x"}, {"run_identifier": "fake-log"})
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(entry)
        self.assertEqual(mod10.event_log_entries("fake-log"), [])

    def test_daily_snapshot_retained_under_stored_identity_only(self):
        snapshot = LyingGetDict(
            {"payload": "x"}, {"run_identifier": "fake-snap"})
        with self.assertRaises(ValueError):
            mod10.retain_daily_snapshot(snapshot)
        self.assertEqual(mod10.daily_snapshots("fake-snap"), [])

    def test_summary_record_filed_under_stored_identity_only(self):
        record = LyingGetDict(
            {"payload": "x"}, {"run_id": "fake-sum"})
        with self.assertRaises(ValueError) as caught:
            mod10.write_summary_record(record)
        self.assertEqual(
            str(caught.exception),
            "identity less summary record: no run identifier "
            "stands on the record, and no summary record stands "
            "retained under no identifier")
        found = mod10.summary_record_for_run("fake-sum")
        self.assertEqual(found.get("record_found"), False)
    def test_summary_record_stored_identity_governs_over_reported(self):
        record = LyingGetDict(
            {"run_id": "real-sum", "payload": "kept"},
            {"run_id": "fake-sum2"})
        mod10.write_summary_record(record)
        self.assertEqual(
            mod10.summary_record_for_run("real-sum")["payload"], "kept")
        found = mod10.summary_record_for_run("fake-sum2")
        self.assertEqual(found.get("record_found"), False)


class TestR13007ViewLeakTimingForm(B2Base):
    def test_plain_timing_controls_stand(self):
        result = mod10.run_view_leak_check(view_record())
        self.assertTrue(result["reportable"])
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(
                view_record(first_seen={"rec": 99}))
        self.assertIn("timing", str(caught.exception))

    def test_falsy_non_mapping_first_seen_stands_refused(self):
        for form in ([], "", 0):
            with self.subTest(form=form):
                with self.assertRaises(ValueError) as caught:
                    mod10.run_view_leak_check(
                        view_record(first_seen=form))
                self.assertIn("timing", str(caught.exception))
                self.assertIn(
                    "first_seen_day_per_record", str(caught.exception))

    def test_length_lying_mapping_first_seen_stands_judged(self):
        first_seen = LenLyingDict({"rec": 99})
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(
                view_record(first_seen=first_seen))
        self.assertIn("timing", str(caught.exception))

    def test_retain_view_record_gates_on_the_timing_form(self):
        with self.assertRaises(ValueError):
            mod10.retain_view_record(view_record(first_seen=[]))
        self.assertEqual(mod10.view_records_for_run("run-b2"), [])


class TestR13008StorageAccounting(B2Base):
    def plain_retained(self):
        return {"summaries": 1, "daily_snapshots": 2, "event_logs": 3,
                "checkpoints": 4, "held_corpus_copies": 5}

    def test_plain_controls_stand(self):
        result = mod10.storage_accounting(self.plain_retained())
        self.assertEqual(result["result_count"], 6)
        self.assertEqual(result["checkpoint_count"], 9)
        claim = dict(self.plain_retained())
        claim.update({"result_count": 999, "checkpoint_count": 9})
        self.assertFalse(mod10.validate_storage_accounting(claim))
        claim["result_count"] = 6
        self.assertTrue(mod10.validate_storage_accounting(claim))

    def test_accounting_reads_stored_counts_not_reported(self):
        retained = LyingGetDict(
            {"summaries": 0, "daily_snapshots": 0, "event_logs": 0,
             "checkpoints": 0, "held_corpus_copies": 0},
            {"summaries": 100})
        result = mod10.storage_accounting(retained)
        self.assertEqual(result["summaries"], 0)
        self.assertEqual(result["result_count"], 0)

    def test_accounting_stored_counts_stand_over_reported_zero(self):
        retained = LyingGetDict(
            self.plain_retained(), {"summaries": 0, "event_logs": 0})
        result = mod10.storage_accounting(retained)
        self.assertEqual(result["result_count"], 6)
        self.assertEqual(result["checkpoint_count"], 9)

    def test_validate_reads_stored_result_count(self):
        claim = LyingGetDict(
            {"summaries": 1, "daily_snapshots": 0, "event_logs": 0,
             "result_count": 999},
            {"result_count": 1})
        self.assertFalse(mod10.validate_storage_accounting(claim))

    def test_validate_stored_true_claim_stands_over_reported(self):
        claim = LyingGetDict(
            {"summaries": 1, "daily_snapshots": 0, "event_logs": 0,
             "checkpoints": 4, "held_corpus_copies": 5,
             "result_count": 1, "checkpoint_count": 9},
            {"result_count": 999, "checkpoint_count": 0})
        self.assertTrue(mod10.validate_storage_accounting(claim))


class TestR13009AggregateDeliveries(B2Base):
    def test_plain_controls_stand_as_two(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "run-b2", [delivery(1, "viewer-a"), delivery(2, "viewer-b")])
        self.assertEqual(count, 2)
        records = mod10.daily_aggregates_for_run("run-b2")
        self.assertEqual(len(records), 2)

    def test_stored_non_numeric_components_stand_refused(self):
        bad = LyingGetDict(
            {"simulated_day": 9, "viewer_id": "viewer-stored",
             "joint_outcome_components": ["a", "b", "c", "d"],
             "component_denominators": ["a", "b", "c", "d"],
             "honest_share": 1, "epochs_ending_on_day": ["epoch-1"],
             "gate_passing_shares": {"epoch-1": 1}},
            {"joint_outcome_components": [1, 2, 3, 4],
             "component_denominators": [1, 1, 1, 1],
             "simulated_day": 5, "viewer_id": "viewer-real"})
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries("run-b2", [bad])
        plain = dict(bad)
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries("run-b2", [plain])

    def test_reported_shared_key_stands_retained_as_two(self):
        first = LyingGetDict(
            delivery(1, "viewer-a"),
            {"simulated_day": 9, "viewer_id": "viewer-z"})
        second = LyingGetDict(
            delivery(2, "viewer-b"),
            {"simulated_day": 9, "viewer_id": "viewer-z"})
        count = mod10.retain_daily_aggregate_deliveries(
            "run-b2", [first, second])
        self.assertEqual(count, 2)
        records = mod10.daily_aggregates_for_run("run-b2")
        self.assertEqual(len(records), 2)
        days = sorted(
            (record["simulated_day"], record["viewer_id"])
            for record in records)
        self.assertEqual(
            days, [(1, "viewer-a"), (2, "viewer-b")])


if __name__ == "__main__":
    unittest.main()

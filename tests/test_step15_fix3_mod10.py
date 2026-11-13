"""Step 15 Round 1 fix pins for cluster 3, MOD-10 stored truth.

Each test pins one register item cure on the MOD-10 surface, in the
form the triage sections state. The file uses plain simulated values
only. Tests reset the module stores around themselves so their
standing does not depend on suite order.
"""
import copy
import os
import shutil
import unittest
from unittest import mock

import crucible.mod01 as mod01
import crucible.mod10 as mod10


class local_temp_dir:
    """A temporary directory under the product tree, used because
    the system temporary directory does not stand usable in every
    run environment for this suite."""

    def __enter__(self):
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".fix3_tmp")
        self.path = os.path.join(base, "case-%d" % os.getpid())
        os.makedirs(self.path, exist_ok=True)
        return self.path

    def __exit__(self, *exc):
        shutil.rmtree(self.path, ignore_errors=True)
        return False


def complete_delivery(day=1, viewer="viewer-1"):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [10, 10, 10, 10],
        "honest_share": 0.5,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0.5},
        "excluded_class_counts_and_shares": {"excluded": 0},
    }


class Fix3Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestMarkerCures(Fix3Base):
    def test_c56_form_only_rederivation_carries_the_marker(self):
        aggregates = mod10.daily_aggregates_for_run(run_id="run-fix3-ghost")
        self.assertEqual(aggregates[0].get("form"), mod10.FORM_ONLY)
        result = mod10.rederive_regime_classification(aggregates)
        self.assertIsNotNone(result)
        self.assertEqual(result.get("form"), mod10.FORM_ONLY)
        self.assertNotEqual(result.get("carriage"),
                            "computed from the aggregates handed in")
        self.assertIn("form only", str(result.get("carriage", "")))
        self.assertEqual(result.get("days"), 0)

    def test_ta14_partial_delivery_is_marked_never_computed(self):
        partial = {"simulated_day": 1, "viewer_id": "viewer-1",
                   "joint_outcome_components": [1, 2, 3, 4]}
        records = mod10.daily_aggregates_for_run(
            run_id="run-fix3-partial", deliveries=[partial])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get("form"), mod10.FORM_ONLY)
        self.assertNotIn("carriage", records[0])
        complete = mod10.daily_aggregates_for_run(
            run_id="run-fix3-complete", deliveries=[complete_delivery()])
        self.assertNotIn("form", complete[0])
        self.assertEqual(complete[0]["joint_outcome_components"], [1, 2, 3, 4])

    def test_ta55_fixed_value_surfaces(self):
        absent = mod10.retained_version_set(record_id="record-fix3-absent")
        self.assertIsInstance(absent, dict)
        self.assertEqual(absent.get("form"), mod10.FORM_ONLY)
        rerun = mod10.rerun_list_for_rule_change(family_id="family-fix3-absent")
        self.assertEqual(rerun.get("form"), mod10.FORM_ONLY)
        self.assertEqual(rerun.get("records_in_question"), [])
        record = mod10.retention_record_for_run("run-fix3-absent")
        self.assertEqual(record.get("form"), mod10.FORM_ONLY)
        mod10.retain_run_record({
            "run_id": "record-fix3-present",
            "run_identifier": "record-fix3-present",
            "rule_version_set": "rule-set-9",
        })
        self.assertEqual(
            mod10.retained_version_set(record_id="record-fix3-present"),
            "rule-set-9")

    def test_c43_missing_run_summary_states_no_record_found(self):
        record = mod10.summary_record_for_run("run-fix3-ghost")
        self.assertEqual(record.get("form"), mod10.FORM_ONLY)
        self.assertIn("no summary record and no run record was found",
                      str(record.get("statement", "")))
        self.assertNotIn("retention_tier", record)
        self.assertNotIn("written_at", record)
        self.assertNotIn("source", record)


class TestAggregateFormAndState(Fix3Base):
    def test_ta39_aggregates_in_day_order(self):
        deliveries = [complete_delivery(day=d) for d in (10, 1, 20, 3, 2)]
        records = mod10.daily_aggregates_for_run(
            run_id="run-fix3-order", deliveries=deliveries)
        self.assertEqual(
            [r["simulated_day"] for r in records], [1, 2, 3, 10, 20])

    def test_c19_aggregate_validates_as_form_14(self):
        records = mod10.daily_aggregates_for_run(
            run_id="run-fix3-form14", deliveries=[complete_delivery()])
        record = records[0]
        self.assertTrue(mod01.validate_record("14", record))
        self.assertEqual(record["run_identifier"], "run-fix3-form14")
        self.assertEqual(record["viewer_identifier"], "viewer-1")
        self.assertIn("gate_passing_share_per_epoch", record)
        self.assertIn("excluded_class_counts_and_shares", record)
        self.assertNotIn("carriage", record)

    def test_c30_manifest_state_and_amendment_naming(self):
        records = mod10.daily_aggregates_for_run(
            run_id="run-fix3-state", deliveries=[complete_delivery()])
        manifest = mod10.aggregate_manifest_for_run("run-fix3-state")
        self.assertEqual(len(manifest), 1)
        entry = manifest[0]
        self.assertTrue(entry.get("record_identity"))
        self.assertEqual(entry.get("writer"), "Recorder")
        self.assertEqual(entry.get("amendment_standing"), "as originally written")
        result = mod10.rederive_regime_classification(records)
        self.assertEqual(result["carriage"],
                         "computed from the aggregates handed in")
        states = result.get("aggregate_states")
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].get("writer"), "Recorder")
        amended = [dict(records[0])]
        amended[0]["amendment_standing"] = "as amended"
        amended_result = mod10.rederive_regime_classification(amended)
        amended_state = amended_result["aggregate_states"][0]
        self.assertEqual(amended_state.get("amendment_standing"), "as amended")
        self.assertIsNone(amended_state.get("amending_act"))


class TestReentrancy(Fix3Base):
    def scenario(self, run_id):
        record = {"run_id": run_id, "run_identifier": run_id,
                  "record_state": "as retained"}
        mod10.retain_run_record(record)
        manifest = {"run_identifier": run_id, "simulated_day": 3,
                    "state_reference": "state-1"}
        mod10.retain_checkpoint(dict(manifest))
        for n in (1, 2, 3):
            mod10.retain_event_log_entry(
                {"run_identifier": run_id, "journal_position": n,
                 "event": "event-%d" % n})
        return {
            "record": mod10.read_run_record(run_id),
            "checkpoints": mod10.checkpoints_for_run(run_id),
            "positions": [e["journal_position"]
                          for e in mod10.event_log_entries(run_id)],
        }

    def test_ta15_same_scenario_twice_replays_identically(self):
        first = self.scenario("run-fix3-replay")
        mod10.reset_stores()
        second = self.scenario("run-fix3-replay")
        self.assertEqual(first, second)
        self.assertEqual(len(second["checkpoints"]), 1)
        self.assertEqual(second["positions"], [1, 2, 3])

    def test_ta15_event_log_replay_without_reset(self):
        for n in (1, 2, 3):
            entry = {"run_identifier": "run-fix3-log", "journal_position": n,
                     "event": "event-%d" % n}
            mod10.retain_event_log_entry(entry)
            mod10.retain_event_log_entry(dict(entry))
        held = mod10.event_log_entries("run-fix3-log")
        self.assertEqual([e["journal_position"] for e in held], [1, 2, 3])

    def test_ta15_released_hold_no_longer_stands(self):
        run_id = "run-fix3-hold-replay"
        mod10.place_reserve_hold(run_id)
        summary = {"run_id": run_id}
        fired = mod10.apply_deferred_evaluation(
            summary, 1, inputs="recorded", outcome="recorded")
        mod10.apply_deferred_evaluation(
            fired, 2, inputs="recorded", outcome="recorded")
        self.assertIsNone(mod10.reserve_hold_for_run(run_id))


class TestStoreFlush(Fix3Base):
    def test_ta11_failed_flush_leaves_prior_file_whole(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.RecorderStore(store_kind="sweep", path=path)
            store.retain_run_record({"run_id": "run-fix3-a"})
            with mock.patch("crucible.mod10.json.dump",
                            side_effect=OSError("interrupted")):
                with self.assertRaises(ValueError):
                    store.retain_run_record({"run_id": "run-fix3-b"})
            reopened = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(reopened.read_run_record("run-fix3-a"),
                             {"run_id": "run-fix3-a"})
            with self.assertRaises(mod10.LookupFailure):
                reopened.read_run_record("run-fix3-b")

    def test_ta11_corrupt_store_opens_as_named_failure(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{ not json")
            with self.assertRaises(mod10.LookupFailure):
                mod10.RecorderStore(store_kind="sweep", path=path)

    def test_ta11_two_instances_do_not_lose_each_other(self):
        with local_temp_dir() as tmp:
            path = os.path.join(tmp, "store.json")
            first = mod10.RecorderStore(store_kind="sweep", path=path)
            second = mod10.RecorderStore(store_kind="sweep", path=path)
            first.retain_run_record({"run_id": "run-fix3-s1"})
            second.retain_run_record({"run_id": "run-fix3-s2"})
            third = mod10.RecorderStore(store_kind="sweep", path=path)
            self.assertEqual(third.read_run_record("run-fix3-s1"),
                             {"run_id": "run-fix3-s1"})
            self.assertEqual(third.read_run_record("run-fix3-s2"),
                             {"run_id": "run-fix3-s2"})


class TestIdentityAndTypeBars(Fix3Base):
    def test_ta13_identity_less_records_refused(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({})
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint({})
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint({})
        self.assertFalse(mod10.validate_run_record_set([{}]))
        self.assertTrue(mod10.validate_run_record_set(
            [{"run_id": "run-fix3-owned", "group_writers": {}}]))

    def test_ta30_ta35_accounting_type_bars(self):
        with self.assertRaises(ValueError):
            mod10.storage_accounting({"summaries": "2"})
        with self.assertRaises(ValueError):
            mod10.storage_accounting({"summaries": 2.9})
        clean = mod10.storage_accounting(
            {"summaries": 2, "daily_snapshots": 3, "event_logs": 1,
             "checkpoints": 4})
        self.assertEqual(clean["result_count"], 6)
        self.assertTrue(mod10.validate_storage_accounting(
            dict(clean, summaries=2, daily_snapshots=3, event_logs=1)))

    def test_ta32_resume_refuses_tampered_checkpoint(self):
        manifest = {"run_identifier": "run-fix3-resume", "simulated_day": 3,
                    "state_reference": "state-1"}
        mod10.retain_checkpoint(dict(manifest))
        resumed = mod10.resume_from_checkpoint(dict(manifest))
        self.assertEqual(resumed, manifest)
        tampered = dict(manifest)
        tampered["state_reference"] = "state-forged"
        tampered["added_field"] = "added"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(tampered)


class TestFlagEvaluation(Fix3Base):
    def test_tb35_ta31_vocabulary_direction_and_tier_bars(self):
        record = {"run_id": "run-fix3-flag", "retention_tier": "Tier 3"}
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 1", inputs="recorded")
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="invented-token", tier="Tier 3",
                inputs="recorded")
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="demoted", tier="Tier 1", inputs="recorded")
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 99", inputs="recorded")
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier=None, inputs="recorded")
        lawful = {"run_id": "run-fix3-flag-2", "retention_tier": "Tier 1"}
        promoted = mod10.apply_flag_evaluation(
            lawful, outcome="promote", tier="Tier 3", inputs="flag inputs")
        self.assertEqual(promoted["retention_tier"], "Tier 3")
        self.assertEqual(promoted["flag_evaluation"]["inputs"], "flag inputs")

    def test_ta31_inputs_recorded_as_supplied(self):
        record = {"run_id": "run-fix3-flag-3", "retention_tier": "Tier 2"}
        updated = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 3")
        self.assertIn("inputs", updated["flag_evaluation"])
        self.assertIsNone(updated["flag_evaluation"]["inputs"])


class TestDeferredAndRetention(Fix3Base):
    def test_ta10_tb39_sequence_and_empty_firing_bars(self):
        run_id = "run-fix3-deferred"
        mod10.place_reserve_hold(run_id)
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 1"})
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                mod10.summary_record_for_run(run_id), 2,
                inputs="recorded", outcome="recorded")
        hold = mod10.reserve_hold_for_run(run_id)
        self.assertEqual(hold["state"], "held")
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                mod10.summary_record_for_run(run_id), 1)
        first = mod10.apply_deferred_evaluation(
            mod10.summary_record_for_run(run_id), 1,
            inputs="condition inputs", outcome="recorded")
        stored = mod10.summary_record_for_run(run_id)
        self.assertEqual(len(stored["deferred_evaluations"]), 1)
        mod10.apply_deferred_evaluation(
            first, 2, inputs="condition inputs", outcome="recorded")
        stored = mod10.summary_record_for_run(run_id)
        self.assertEqual(len(stored["deferred_evaluations"]), 2)
        self.assertIsNone(mod10.reserve_hold_for_run(run_id))

    def test_tb38_retention_met_through_product_surfaces(self):
        run_id = "run-fix3-retention-met"
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 2"})
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 1})
        first = mod10.apply_deferred_evaluation(
            mod10.summary_record_for_run(run_id), 1,
            inputs="condition inputs", outcome="recorded")
        mod10.apply_deferred_evaluation(
            first, 2, inputs="condition inputs", outcome="recorded")
        record = mod10.retention_record_for_run(run_id)
        self.assertEqual(record["later_evaluation"]["conditions"], [1, 2, 3])
        self.assertTrue(record["summary_record_written"])
        self.assertTrue(record["retained_forms_pointed_to"])
        self.assertTrue(mod10.retention_met(record))
        bare = mod10.retention_record_for_run("run-fix3-retention-unmet")
        self.assertFalse(mod10.retention_met(bare))

    def test_ta37_retention_record_states_memory_standing(self):
        record = mod10.retention_record_for_run("run-fix3-memory")
        self.assertEqual(record["pointers"]["checkpoints"], 0)
        for form in ("checkpoints", "event_log_entries", "daily_snapshots"):
            self.assertIn("memory only", record["form_standing"][form])


class TestCheckpointDuties(Fix3Base):
    def test_ta08_tb36_delete_checkpoint_requires_trigger(self):
        run_id = "run-fix3-delete"
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 3})
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(run_id, 3)
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(
                run_id, 3, trigger="clause C5 stated trigger",
                rule_path="stated deletion rule path",
                regression_corpus_copy=True)
        act = mod10.delete_checkpoint(
            run_id, 3, trigger="clause C5 stated trigger",
            rule_path="stated deletion rule path")
        self.assertEqual(act["trigger"], "clause C5 stated trigger")
        self.assertEqual(act["actor"], "Recorder")
        self.assertEqual(mod10.checkpoints_for_run(run_id), [])

    def test_tb37_close_applies_the_retained_set(self):
        def seed(run_id):
            for day in range(1, 13):
                mod10.retain_checkpoint(
                    {"run_identifier": run_id, "simulated_day": day})
        seed("run-fix3-tier1")
        result = mod10.close_run_retention("run-fix3-tier1", "Tier 1")
        self.assertEqual(result["kept_days"], [12])
        self.assertEqual(len(result["released_days"]), 11)
        self.assertEqual(
            [c["simulated_day"]
             for c in mod10.checkpoints_for_run("run-fix3-tier1")], [12])
        seed("run-fix3-tier2")
        result = mod10.close_run_retention("run-fix3-tier2", "Tier 2")
        self.assertEqual(result["kept_days"], [10, 12])
        seed("run-fix3-tier3")
        result = mod10.close_run_retention("run-fix3-tier3", "Tier 3")
        self.assertEqual(len(result["kept_days"]), 12)


class TestAccountingForms(Fix3Base):
    def test_tb43_c10_alias_and_stock_bars(self):
        with self.assertRaises(ValueError):
            mod10.checkpoint_count_c10([{
                "retained_per_run": 1, "runs": 1,
                "held_corpus_copies": 5, "corpus_copies": 6}])
        equal = mod10.checkpoint_count_c10([{
            "retained_per_run": 1, "runs": 1,
            "held_corpus_copies": 5, "corpus_copies": 5}])
        self.assertEqual(equal, 6)
        with self.assertRaises(ValueError):
            mod10.checkpoint_count_c10(
                [{"retained_per_run": -5, "runs": 2}])
        with self.assertRaises(ValueError):
            mod10.checkpoint_count_c10(
                [{"retained_per_run": 2.9, "runs": 1}])

    def test_tb44_storage_accounting_carries_copies(self):
        retained = {"summaries": 2, "daily_snapshots": 3, "event_logs": 1,
                    "checkpoints": 4, "held_corpus_copies": 3}
        accounting = mod10.storage_accounting(retained)
        self.assertEqual(accounting["held_corpus_copies"], 3)
        self.assertEqual(accounting["checkpoint_count"], 7)
        self.assertTrue(mod10.validate_storage_accounting(
            dict(retained, result_count=6, checkpoint_count=7)))
        self.assertFalse(mod10.validate_storage_accounting(
            dict(retained, result_count=6, checkpoint_count=4)))


class TestLookupForms(Fix3Base):
    def test_c44_ta60_store_lookup_forms(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.store_lookup(store_kinds="sweep", key="run-fix3-absent")
        with self.assertRaises(ValueError):
            mod10.store_lookup(store_kinds=("sweep", "pilot"), key="x")
        with self.assertRaises(ValueError):
            mod10.store_lookup(store_kinds=("bogus",), key="x")

    def test_c45_gc08_failure_names_owner_and_kind(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.gc08_record("call_log", "owner-fix3")
        failure = caught.exception.failure
        self.assertEqual(failure["owner_identifier"], "owner-fix3")
        self.assertEqual(failure["record_kind"], "call_log")
        self.assertNotIn("run_identifier", failure)

    def test_c14_annotation_link_plan_name(self):
        self.assertEqual(mod10.annotation_link_at_checkpoint(
            {"annotation_link_identifier": "link-plan"}), "link-plan")
        self.assertEqual(mod10.annotation_link_at_checkpoint(
            {"annotation_link": "link-legacy"}), "link-legacy")

    def test_fle02_reading_never_writes(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record("run-fix3-never")
        self.assertEqual(store.index(), [])
        before = mod10.store_indexes()
        with self.assertRaises(mod10.LookupFailure):
            mod10.run_records_for_run("run-fix3-never")
        self.assertEqual(mod10.store_indexes(), before)


class TestPositionCheckAndViews(Fix3Base):
    def test_c12_position_check_free_limb(self):
        run_id = "run-fix3-position"
        for n in (1, 2, 3):
            mod10.retain_event_log_entry(
                {"run_identifier": run_id, "journal_position": n})
        inside = mod10.checkpoint_position_check(
            {"run_identifier": run_id, "journal_position": 2})
        self.assertTrue(inside["reportable"])
        outside = mod10.checkpoint_position_check(
            {"run_identifier": run_id, "journal_position": 99})
        self.assertFalse(outside["reportable"])
        self.assertEqual(outside["failure_under"], "C-09")
        self.assertIn("retention failure", outside["outcome"])

    def view_record(self):
        return {
            "run_identifier": "run-fix3-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": 5,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": [{"item": "ordinary content"}],
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"item": 3},
            "delay_applied_per_record": {"item": 1},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }

    def test_tb06_view_leak_check_runner(self):
        result = mod10.run_view_leak_check(self.view_record())
        self.assertEqual(result["forms_run"],
                         ["canary", "field_validation", "timing"])
        self.assertTrue(result["reportable"])
        contaminated = self.view_record()
        contaminated["view_contents"] = [{"ground_truth": "canary value"}]
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(contaminated)
        self.assertIn("canary", str(caught.exception))

    def test_tb06_view_retention_tier_split(self):
        record = self.view_record()
        mod10.retain_view_record(record, tier="Tier 1")
        held = mod10.view_records_for_run("run-fix3-view")
        self.assertEqual(len(held), 1)
        self.assertIn("divergence_companion", held[0])
        self.assertNotIn("view_contents", held[0])
        record2 = self.view_record()
        record2["run_identifier"] = "run-fix3-view-2"
        mod10.retain_view_record(record2, tier="Tier 2")
        held2 = mod10.view_records_for_run("run-fix3-view-2")
        self.assertIn("view_contents", held2[0])


class TestRetentionBarsAndCarriage(Fix3Base):
    def test_ta05_retention_refuses_real_money_forms(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-fix3-money-1", "real_money_value": 5})
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-fix3-money-2",
                "payment": {"amount": 3, "currency": "stated currency"}})
        kept = store.retain_run_record({"run_id": "run-fix3-money-3"})
        self.assertEqual(kept["run_id"], "run-fix3-money-3")

    def test_c13_journal_count_carried_at_checkpoint_writing(self):
        run_id = "run-fix3-journal-count"
        for n in (1, 2, 3):
            mod10.retain_event_log_entry(
                {"run_identifier": run_id, "journal_position": n})
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 2})
        held = mod10.checkpoints_for_run(run_id)
        self.assertEqual(
            held[0]["journal_event_count_at_checkpoint"], 3)
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 4,
             "journal_event_count_at_checkpoint": 9})
        held = mod10.checkpoints_for_run(run_id)
        stated = [c for c in held if c["simulated_day"] == 4][0]
        self.assertEqual(stated["journal_event_count_at_checkpoint"], 9)

    def test_c18_checkpoint_state_paired_store(self):
        run_id = "run-fix3-paired"
        state = {"agent_states": "stated", "simulation_clock_value": 4}
        mod10.retain_checkpoint({
            "run_identifier": run_id, "simulated_day": 4,
            "checkpoint_state": state})
        self.assertEqual(mod10.checkpoint_state_at(run_id, 4), state)
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 5})
        self.assertIsNone(mod10.checkpoint_state_at(run_id, 5))


class TestSummaryCarriage(Fix3Base):
    def test_c36_summary_carries_week_and_unit_identifiers(self):
        mod10.retain_run_record({
            "run_id": "run-fix3-week",
            "run_identifier": "run-fix3-week",
            "week": 7,
            "headline_unit_identifiers": ["unit-1", "unit-2"],
            "groups": {},
        })
        summary = mod10.summary_record_for_run("run-fix3-week")
        self.assertEqual(summary["week"], 7)
        self.assertEqual(summary["headline_unit_identifiers"],
                         ["unit-1", "unit-2"])


if __name__ == "__main__":
    unittest.main()

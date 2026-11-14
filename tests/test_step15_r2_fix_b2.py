"""Step 15 second run fix wave pins for Fix Builder 2, MOD-10.

Each test pins one register item from the Round 1 register
(R1-002, R1-003, R1-007, R1-009, R1-052, R1-053, R1-054, R1-056,
R1-070, R1-077, R1-080, R1-087, R1-088, R1-089) on the MOD-10
surface in crucible/mod10.py, plus the leak check acceptance at
R1-087 for a MOD-04 view record. Tests reset the module stores
around themselves so their standing does not depend on suite
order. Values are simulated and test values only.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def view_record(self, contents):
        return {
            "run_identifier": "run-b2-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": 5,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": contents,
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"item": 3},
            "delay_applied_per_record": {"item": 1},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }


class TestR1002CapitalDresses(B2Base):
    def test_modifier_capital_money_marker_refused(self):
        key = (
            "\u1d3f\u1d31\u1d2c\u1d38\u1d39\u1d3c\u1d3a\u1d31"
            + "y" + "value")
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-b2-r1002-a", key: 500})

    def test_letterlike_capital_money_marker_refused(self):
        key = (
            "\u211b\u2130" + "a" + "\u2112\u2133" + "o"
            + "\u2115\u2130" + "y" + "value")
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-b2-r1002-b", key: 500})


class TestR1003UpsilonYReading(B2Base):
    def test_upsilon_as_y_money_marker_refused(self):
        key = "realmone\u03c5value"
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-b2-r1003", key: 500})


class TestR1007AmountCurrencyPair(B2Base):
    def test_amount_with_none_currency_refused(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-b2-r1007-a",
                "stake": {"amount": 5, "currency": None},
            })

    def test_amount_only_control_retained(self):
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record(
            {"run_id": "run-b2-r1007-b", "amount": 5})
        self.assertEqual(kept["run_id"], "run-b2-r1007-b")


class TestR1009LeakMapLetters(B2Base):
    KEYS = (
        "member\u0452hip",
        "members\u0493ip",
        "membersh\u0456p",
        "membershi\u03c1",
    )

    def test_dressed_keys_read_barred(self):
        for key in self.KEYS:
            self.assertTrue(mod10._is_barred_view_key(key), msg=key)

    def test_runner_refuses_dressed_keys(self):
        for key in self.KEYS:
            record = self.view_record([{"detail": {key: "v"}}])
            with self.assertRaises(ValueError, msg=key):
                mod10.run_view_leak_check(record)


class TestR1052DeferredEvaluationHoldFallback(B2Base):
    def test_hold_released_for_run_identifier_only_record(self):
        run_key = "run-b2-r1052"
        mod10.place_reserve_hold(run_key)
        summary = {"run_identifier": run_key, "retention_tier": "Tier 1"}
        first = mod10.apply_deferred_evaluation(
            summary, 1, inputs={"a": 1}, outcome="held")
        second = mod10.apply_deferred_evaluation(
            first, 2, inputs={"a": 1}, outcome="released")
        self.assertEqual(second.get("reserve_hold_state"), "released")
        self.assertIsNone(mod10.reserve_hold_for_run(run_key))


class TestR1053AggregateComponentForm(B2Base):
    DELIVERY = {
        "simulated_day": 1,
        "viewer_id": "viewer-1",
        "joint_outcome_components": ["word", 2, 3, 4],
        "component_denominators": [10, 10, 10, 10],
        "honest_share": 0.5,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0.5},
    }

    def test_non_numeric_components_refused_at_retention(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries(
                "run-b2-r1053", [dict(self.DELIVERY)])

    def test_non_numeric_components_fail_validation(self):
        record = {
            "viewer_id": "viewer-1",
            "joint_outcome_components": ["word", 2, 3, 4],
            "component_denominators": [10, 10, 10, 10],
        }
        self.assertFalse(mod10.validate_daily_aggregates([record]))

    def test_rederive_does_not_raise_bare_type_error(self):
        record = {
            "viewer_id": "viewer-1",
            "record_identity": "run-b2-r1053:1:viewer-1",
            "writer": "Recorder",
            "joint_outcome_components": ["word", 2, 3, 4],
        }
        result = mod10.rederive_regime_classification([record])
        self.assertIsNone(result)

    def test_numeric_control_holds(self):
        delivery = dict(self.DELIVERY)
        delivery["joint_outcome_components"] = [1, 2, 3, 4]
        mod10.retain_daily_aggregate_deliveries("run-b2-r1053-ok", [delivery])
        aggregates = mod10.daily_aggregates_for_run("run-b2-r1053-ok")
        self.assertTrue(mod10.validate_daily_aggregates(aggregates))
        derived = mod10.rederive_regime_classification(aggregates)
        self.assertEqual(derived["component_totals"], [1, 2, 3, 4])


class TestR1054IdentifierLessRetention(B2Base):
    def test_event_log_entry_without_identifier_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry({"journal_position": 1})
        self.assertEqual(mod10.event_log_entries(None), [])

    def test_daily_snapshot_without_identifier_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_snapshot({"simulated_day": 1})
        self.assertEqual(mod10.daily_snapshots(None), [])


class TestR1056GroupWritersForm(B2Base):
    def test_wrong_form_group_writers_returns_false(self):
        for writers in (["Recorder"], "Recorder", 5):
            record = {"run_id": "run-b2-r1056", "group_writers": writers}
            self.assertFalse(
                mod10.validate_run_record_set([record]), msg=repr(writers))

    def test_record_form_group_writers_control(self):
        record = {
            "run_id": "run-b2-r1056-ok",
            "group_writers": {"assumption_record": "Recorder"},
        }
        self.assertTrue(mod10.validate_run_record_set([record]))


class TestR1070DeepAndCyclicRecords(B2Base):
    def test_deep_record_refused_in_value_error_form(self):
        record = {"run_id": "run-b2-r1070-deep"}
        node = record
        for _ in range(300):
            node["child"] = {}
            node = node["child"]
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record(record)

    def test_cyclic_record_refused_in_value_error_form(self):
        record = {"run_id": "run-b2-r1070-cyclic"}
        record["self_reference"] = record
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record(record)


class TestR1077UnhashableIdentifiers(B2Base):
    def test_reads_raise_lookup_failure(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record(["unhashable"])
        with self.assertRaises(mod10.LookupFailure):
            store.has_run_record(["unhashable"])
        with self.assertRaises(mod10.LookupFailure):
            mod10.read_run_record(["unhashable"])

    def test_retention_raises_value_error(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": ["unhashable"]})
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_identifier": {"a": 1}})


class TestR1080CheckpointUniqueness(B2Base):
    MANIFEST = {
        "run_identifier": "run-b2-r1080",
        "simulated_day": 3,
        "state_reference": "state-1",
    }

    def test_second_differing_write_rejected_and_recorded(self):
        mod10.retain_checkpoint(dict(self.MANIFEST))
        differing = dict(self.MANIFEST)
        differing["state_reference"] = "state-2"
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(differing)
        held = mod10.checkpoints_for_run("run-b2-r1080")
        self.assertEqual(len(held), 1)
        rejected = mod10.rejected_checkpoint_writes("run-b2-r1080")
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["simulated_day"], 3)

    def test_second_identical_write_rejected_and_recorded(self):
        mod10.retain_checkpoint(dict(self.MANIFEST))
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(dict(self.MANIFEST))
        self.assertEqual(len(mod10.checkpoints_for_run("run-b2-r1080")), 1)
        self.assertEqual(
            len(mod10.rejected_checkpoint_writes("run-b2-r1080")), 1)


class TestR1087ViewRecordEmptyForms(B2Base):
    def test_mod04_view_record_passes_leak_check_and_retains(self):
        record = mod04.build_view_record(
            run_id="run-b2-r1087", viewer_id="viewer-1", day=1)
        self.assertIsNone(record["scheduling_position_identifier"])
        self.assertIsNone(record["rule_version_set"])
        result = mod10.run_view_leak_check(record)
        self.assertTrue(result["reportable"])
        mod10.retain_view_record(record)
        self.assertEqual(len(mod10.view_records_for_run("run-b2-r1087")), 1)


class TestR1088ResumeReadBackCheckpoint(B2Base):
    def test_checkpoint_read_back_can_be_resumed(self):
        manifest = {
            "run_identifier": "run-b2-r1088",
            "simulated_day": 2,
            "state_reference": "state-1",
        }
        mod10.retain_checkpoint(dict(manifest))
        handed = mod10.checkpoints_for_run("run-b2-r1088")[0]
        self.assertIn("journal_event_count_at_checkpoint", handed)
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(resumed["state_reference"], "state-1")

    def test_genuine_tampering_still_refused(self):
        manifest = {
            "run_identifier": "run-b2-r1088",
            "simulated_day": 2,
            "state_reference": "state-1",
        }
        mod10.retain_checkpoint(dict(manifest))
        handed = mod10.checkpoints_for_run("run-b2-r1088")[0]
        handed["state_reference"] = "state-forged"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)


class TestR1089FlagEvaluationChecks(B2Base):
    RECORD = {
        "run_id": "run-b2-r1089",
        "retention_tier": "Tier 1",
        "flag_conditions_fired": [],
    }

    def test_promotion_with_no_inputs_refused_and_not_persisted(self):
        mod10.write_summary_record(dict(self.RECORD))
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                dict(self.RECORD), outcome="promote", tier="Tier 2",
                inputs=None)
        stored = mod10.summary_record_for_run("run-b2-r1089")
        self.assertEqual(stored["retention_tier"], "Tier 1")

    def test_promotion_with_no_fired_condition_refused(self):
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                dict(self.RECORD), outcome="promote", tier="Tier 2",
                inputs={})
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                dict(self.RECORD), outcome="promote", tier="Tier 2",
                inputs="some inputs")

    def test_promotion_with_fired_condition_holds(self):
        promoted = mod10.apply_flag_evaluation(
            dict(self.RECORD), outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(promoted["retention_tier"], "Tier 2")


if __name__ == "__main__":
    unittest.main()

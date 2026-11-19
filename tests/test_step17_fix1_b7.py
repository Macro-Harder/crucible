"""Step 17 fix wave 1, Builder 7 tests (Slice 7).

Rows FW-15, FW-19, FW-30, FW-31, and FW-32. Each defect test
reproduces its filing defect on the base tree at product head
9f938470807f90b7c8c6d9882fde1105c807e0a1 and passes on the
fixed tree. Control tests pin the standings that already hold.
"""
import unittest

import crucible.mod05 as mod05
import crucible.mod08 as mod08
import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod13 as mod13

HUGE = 10 ** 5000


def delivery(day=1, components=None, denominators=None, **extra):
    record = {
        "simulated_day": day,
        "viewer_id": "v1",
        "joint_outcome_components": (
            [1.0] if components is None else components),
        "component_denominators": (
            [1.0] if denominators is None else denominators),
    }
    record.update(extra)
    return record


def complete_delivery(**extra):
    record = {
        "simulated_day": 1,
        "viewer_id": "v1",
        "joint_outcome_components": [1, 0, 0, 0],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 0.5,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0.5},
    }
    record.update(extra)
    return record


class TestFW15AggregateHugeIntegers(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_huge_component_stands_retained(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "run-x", [delivery(1), delivery(2, components=[HUGE])])
        self.assertEqual(count, 2)
        days = {
            record["simulated_day"]
            for record in mod10.daily_aggregates_for_run("run-x")}
        self.assertEqual(days, {1, 2})

    def test_defect_huge_denominator_stands_retained(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "run-x", [delivery(1), delivery(2, denominators=[HUGE])])
        self.assertEqual(count, 2)

    def test_control_named_refusal_leaves_no_partial_retention(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "run-x",
                [delivery(1),
                 delivery(2, components=[float("nan")])])
        self.assertIn(
            "daily aggregate delivery in named form",
            str(caught.exception))
        records = mod10.daily_aggregates_for_run("run-x")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].get("form"), mod10.FORM_ONLY)


class TestFW15Mod10ReadingDoors(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_record_gate_unhashable_run_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share(["x"], "e", 0.5)
        self.assertIn("unhashable form", str(caught.exception))

    def test_defect_rederive_non_iterable_answers_undelivered(self):
        self.assertIsNone(mod10.rederive_regime_classification(123))

    def test_control_record_gate_round_trip(self):
        mod10.record_gate_passing_share("run-g", "epoch-1", 0.5)
        logged = mod10.gate_passing_shares_for_run("run-g")
        self.assertEqual(len(logged), 1)

    def test_control_rederive_valid_aggregates(self):
        result = mod10.rederive_regime_classification(
            [complete_delivery()])
        self.assertEqual(
            result["classification"],
            "rederived_from_daily_aggregates")
        self.assertEqual(result["component_totals"], [1, 0, 0, 0])


class TestFW15Mod05HostileForms(unittest.TestCase):
    def test_defect_work_credit_unhashable_agent_identifier(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit(
                [{"agent_identifier": ["x"], "accepted": True}])
        self.assertIn("work_credit stands refused", str(caught.exception))

    def test_defect_work_credit_unhashable_agent_key(self):
        with self.assertRaises(ValueError):
            mod05.work_credit([{"agent": ["x"], "accepted": True}])

    def test_defect_component_mixed_identifier_types(self):
        result = mod05.component(
            [mod05.vouch(1, "a", 1), mod05.vouch("a", 1, 1)])
        self.assertEqual(len(result["component_list"]), 1)
        members = result["component_list"][0]["members"]
        self.assertEqual(set(members), {1, "a"})

    def test_defect_gate_share_unhashable_member(self):
        with self.assertRaises(ValueError):
            mod05.gate_passing_share([["x"]], [["x"]])

    def test_defect_boundary_text_score_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.boundary_neighbourhood(
                [{"distance_slice": "near", "score": "high"}],
                10, ["near"])
        self.assertIn(
            "boundary_neighbourhood stands refused",
            str(caught.exception))

    def test_defect_boundary_unhashable_slice_label(self):
        with self.assertRaises(ValueError):
            mod05.boundary_neighbourhood(
                [{"distance_slice": ["x"], "score": 1}], 10, ["near"])

    def test_defect_excluded_class_unhashable(self):
        with self.assertRaises(ValueError) as caught:
            mod05.excluded_class_counts([{"excluded_class": ["x"]}])
        self.assertIn(
            "excluded_class_counts stands refused",
            str(caught.exception))

    def test_control_work_credit_plain_events(self):
        result = mod05.work_credit(
            [{"agent_identifier": "a", "accepted": True}])
        self.assertEqual(result["totals"]["submitted"], 1)
        self.assertEqual(result["totals"]["accepted"], 1)

    def test_control_component_mutual_pair(self):
        result = mod05.component(
            [mod05.vouch("a", "b", 1), mod05.vouch("b", "a", 1)])
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 2)

    def test_control_excluded_class_counts_plain(self):
        result = mod05.excluded_class_counts(
            [{"excluded_class": "cryptographic offences"}])
        total = sum(
            entry["count"] for entry in result.values())
        self.assertEqual(total, 1)


class TestFW15Mod08DetectionDoors(unittest.TestCase):
    def test_defect_accept_huge_int_feature_refused_named(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(
                {"agent_identifier": "a", "day": 1,
                 "feature_values": {"f": HUGE}})

    def test_defect_score_day_huge_int_feature_refused_named(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day(
                [{"agent_identifier": "a", "day": 1,
                  "feature_values": {"f": HUGE}}])

    def test_control_accept_large_feature_within_limit(self):
        accepted = mod08.accept_detection_input(
            {"agent_identifier": "a", "day": 1,
             "feature_values": {"f": 10 ** 100}})
        self.assertEqual(accepted["feature_values"]["f"], 10 ** 100)

    def test_control_score_day_large_feature(self):
        outputs = mod08.score_day(
            [{"agent_identifier": "a", "day": 1,
              "feature_values": {"f": 10 ** 100}}])
        self.assertEqual(
            outputs["verdict_states"][0]["verdict_state"],
            "ACCUSED")


class TestFW19ComponentGrowth(unittest.TestCase):
    def test_defect_component_work_grows_with_the_act_not_the_graph(self):
        edges = []
        for index in range(60):
            first = "a%d" % index
            second = "b%d" % index
            edges.append(mod05.vouch(first, second, 1))
            edges.append(mod05.vouch(second, first, 1))
        calls = []
        original_get = mod05._get

        def counting_get(record, *names, **kwargs):
            calls.append(1)
            return original_get(record, *names, **kwargs)

        mod05._get = counting_get
        try:
            result = mod05.component(edges)
        finally:
            mod05._get = original_get
        self.assertEqual(len(result["component_list"]), 60)
        self.assertLess(len(calls), 2000)

    def test_control_component_stake_and_edges_stand(self):
        result = mod05.component(
            [mod05.vouch("a", "b", 3), mod05.vouch("b", "a", 2)])
        entry = result["component_list"][0]
        self.assertEqual(entry["edge_count"], 2)
        self.assertEqual(entry["stake_total"], 5)


class TestFW19RejectedCheckpointCap(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_rejected_writes_record_carries_a_cap(self):
        manifest = {"run_id": "ckpt-run", "simulated_day": 1}
        mod10.retain_checkpoint(dict(manifest))
        cap = mod10._REJECTED_CHECKPOINT_WRITES_CAP
        for _ in range(cap + 5):
            with self.assertRaises(ValueError):
                mod10.retain_checkpoint(dict(manifest))
        self.assertEqual(
            len(mod10._REJECTED_CHECKPOINT_WRITES), cap)
        self.assertEqual(
            len(mod10.rejected_checkpoint_writes("ckpt-run")), cap)

    def test_control_rejected_writes_recorded_under_cap(self):
        manifest = {"run_id": "ckpt-run", "simulated_day": 1}
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(dict(manifest))
        self.assertEqual(
            len(mod10.rejected_checkpoint_writes("ckpt-run")), 1)


class TestFW30ResumeFromCheckpoint(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_resume_unnamed_unretained_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(
                {"run_id": "run-ghost", "simulated_day": 40,
                 "state_marker": "fabricated"})
        self.assertIn(
            "checkpoint integrity refusal", str(caught.exception))

    def test_control_resume_named_unretained_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(
                {"run_id": "run-ghost", "simulated_day": 40},
                store_kind="sweep")
        self.assertIn(
            "checkpoint integrity refusal", str(caught.exception))

    def test_control_resume_retained_checkpoint(self):
        manifest = {"run_id": "run-kept", "simulated_day": 3,
                    "payload": "original"}
        mod10.retain_checkpoint(dict(manifest))
        resumed = mod10.resume_from_checkpoint(dict(manifest))
        self.assertEqual(resumed["payload"], "original")


class TestFW30WitnessRerun(unittest.TestCase):
    def test_defect_witness_rerun_absent_original(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.witness_rerun(None)

    def test_defect_witness_rerun_no_identifier(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.witness_rerun({"rule_set_version": "rules-1"})

    def test_defect_witness_rerun_non_text_identifier(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.witness_rerun({"run_id": 123})

    def test_control_witness_rerun_text_original(self):
        rerun = mod13.witness_rerun(
            {"run_id": "run-1", "rule_set_version": "rules-1"},
            rule_set_version="rules-2")
        self.assertEqual(rerun["run_id"], "run-1-rerun")
        self.assertEqual(rerun["linked_to"], "run-1")
        self.assertFalse(rerun["verdicts_transferred"])


class TestFW31ReplayCheck(unittest.TestCase):
    def test_defect_replay_check_empty_records_undelivered(self):
        result = mod10.replay_check({}, {})
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])
        self.assertIn(
            "undelivered", result["comparison_standing"])

    def test_defect_replay_check_unrelated_records_undelivered(self):
        result = mod10.replay_check({"a": 1}, {"b": 2})
        self.assertIn(
            "undelivered", result["comparison_standing"])

    def test_control_replay_check_equal_records(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 1}, "verdict": "x"})
        self.assertTrue(result["record_level_equal"])
        self.assertTrue(result["verdict_level_equal"])
        self.assertNotIn("comparison_standing", result)

    def test_control_replay_check_differing_records(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 2}, "verdict": "y"})
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])

    def test_control_replay_check_present_none_values_compare(self):
        result = mod10.replay_check(
            {"record": None, "verdict": None},
            {"record": None, "verdict": None})
        self.assertTrue(result["record_level_equal"])
        self.assertTrue(result["verdict_level_equal"])


class TestFW32Mod11StatisticsDoors(unittest.TestCase):
    def test_defect_point_standing_negative_count(self):
        with self.assertRaises(ValueError) as caught:
            mod11.point_standing(-1)
        self.assertIn(
            "point_standing stands refused", str(caught.exception))

    def test_defect_classify_run_outcome_negative_days(self):
        with self.assertRaises(ValueError) as caught:
            mod11.classify_run_outcome(-5, "x")
        self.assertIn(
            "classify_run_outcome stands refused",
            str(caught.exception))

    def test_defect_top_up_applies_nan(self):
        with self.assertRaises(ValueError) as caught:
            mod11.top_up_applies(float("nan"))
        self.assertIn(
            "top_up_applies stands refused", str(caught.exception))

    def test_defect_top_up_applies_above_one(self):
        with self.assertRaises(ValueError):
            mod11.top_up_applies(1.5)

    def test_defect_top_up_applies_below_zero(self):
        with self.assertRaises(ValueError):
            mod11.top_up_applies(-0.5)

    def test_control_top_up_applies_in_range(self):
        self.assertTrue(mod11.top_up_applies(0.5))
        self.assertFalse(mod11.top_up_applies(0.05))
        self.assertFalse(mod11.top_up_applies(1.0))
        self.assertFalse(mod11.top_up_applies(0.0))

    def test_control_point_standing_floor(self):
        self.assertEqual(
            mod11.point_standing(30)["standing"], "at floor")
        self.assertEqual(
            mod11.point_standing(29)["standing"], "below floor")

    def test_control_classify_run_outcome_forms(self):
        self.assertEqual(
            mod11.classify_run_outcome(20, "steady")["outcome"],
            "horizon insufficient")
        self.assertEqual(
            mod11.classify_run_outcome(30, "steady")["outcome"],
            "steady")


class TestFW32Mod05StatisticsDoors(unittest.TestCase):
    def test_defect_band_membership_nan_score_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(
                float("nan"), [("low", 0), ("high", 10)],
                evaluation_order={"order": "O-1"})
        self.assertIn(
            "band_membership stands refused", str(caught.exception))

    def test_defect_band_membership_empty_bands_states_standing(self):
        result = mod05.band_membership(
            5, [], evaluation_order={"order": "O-1"})
        self.assertIsNone(result["band"])
        self.assertIn("no bands", result["band_standing"])

    def test_defect_band_membership_below_band_states_standing(self):
        result = mod05.band_membership(
            5, [("high", 10)], evaluation_order={"order": "O-1"})
        self.assertIsNone(result["band"])
        self.assertIn("reaches no", result["band_standing"])

    def test_control_band_membership_reached_band_states_standing(self):
        result = mod05.band_membership(
            5, [("low", 0), ("high", 10)],
            evaluation_order={"order": "O-1"})
        self.assertEqual(result["band"], "low")
        self.assertIn("reaches", result["band_standing"])

    def test_defect_boundary_text_boundary_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.boundary_neighbourhood(
                [{"score": 5, "distance_slice": "near"}],
                "10", ["near"])
        self.assertIn(
            "boundary_neighbourhood stands refused",
            str(caught.exception))

    def test_defect_boundary_bool_score_refused(self):
        with self.assertRaises(ValueError):
            mod05.boundary_neighbourhood(
                [{"score": True, "distance_slice": "near"}],
                10, ["near"])

    def test_defect_boundary_nan_score_refused(self):
        with self.assertRaises(ValueError):
            mod05.boundary_neighbourhood(
                [{"score": float("nan"), "distance_slice": "near"}],
                10, ["near"])

    def test_control_boundary_neighbourhood_plain(self):
        result = mod05.boundary_neighbourhood(
            [{"score": 5, "distance_slice": "near"}], 10, ["near"])
        self.assertEqual(
            result["counts_per_distance_slice"], {"near": 1})
        self.assertEqual(
            result[
                "cheapest_crossing_movement_in_accepted_work_units"],
            5)

    def test_defect_component_cap_nan_cap_refused(self):
        edges = [mod05.vouch("a", "b", 1), mod05.vouch("b", "a", 1)]
        with self.assertRaises(ValueError) as caught:
            mod05.component_cap_check(edges, float("nan"))
        self.assertIn(
            "component_cap_check stands refused",
            str(caught.exception))

    def test_control_component_cap_plain(self):
        edges = [mod05.vouch("a", "b", 1), mod05.vouch("b", "a", 1)]
        self.assertTrue(mod05.component_cap_check(edges, 2))
        self.assertFalse(mod05.component_cap_check(edges, 1))


class TestFW32Mod10RecorderStatistics(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_rederive_overflow_answers_undelivered(self):
        records = [
            {"joint_outcome_components": [1e308, 1e308, 1e308, 1e308]},
            {"joint_outcome_components": [1e308, 1e308, 1e308, 1e308]},
        ]
        self.assertIsNone(
            mod10.rederive_regime_classification(records))

    def test_defect_retain_text_honest_share_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "run-s", [complete_delivery(honest_share="banana")])
        self.assertIn(
            "daily aggregate delivery in named form",
            str(caught.exception))

    def test_defect_retain_gate_share_above_one_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries(
                "run-s",
                [complete_delivery(gate_passing_shares={"e": 42})])

    def test_defect_retain_honest_share_above_one_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_aggregate_deliveries(
                "run-s", [complete_delivery(honest_share=1.5)])

    def test_control_retain_valid_shares_stand(self):
        mod10.retain_daily_aggregate_deliveries(
            "run-s", [complete_delivery()])
        records = mod10.daily_aggregates_for_run("run-s")
        self.assertEqual(records[0]["honest_share"], 0.5)
        self.assertEqual(
            records[0]["gate_passing_shares"], {"epoch-1": 0.5})

    def test_control_retain_proportion_record_share_stands(self):
        share = {"numerator": 1, "denominator": 2}
        mod10.retain_daily_aggregate_deliveries(
            "run-s",
            [complete_delivery(gate_passing_shares={"epoch-1": share})])
        records = mod10.daily_aggregates_for_run("run-s")
        self.assertEqual(
            records[0]["gate_passing_shares"]["epoch-1"],
            {"numerator": 1, "denominator": 2})


if __name__ == "__main__":
    unittest.main()

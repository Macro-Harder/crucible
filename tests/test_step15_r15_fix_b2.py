"""Pins for fix wave 14, Builder 2, Group 2: rows R14-007 to R14-018.

Each pin places the same stored contents in plain dict form and in a
dict subclass whose get, keys, items, contains, subscript, or copy
protocol reports fabricated readings, in both directions where the
charged act allows both, beside a raising protocol probe where the
register charges one. The cured acts judge the stored contents only.
"""
import unittest

from crucible import mod01, mod04, mod05, mod06, mod10, mod11, mod14, mod16


class LyingGet(dict):
    """A dict whose get reports the fake mapping, never the stored one."""

    def __init__(self, stored, fake):
        super().__init__(stored)
        self._fake = fake

    def get(self, key, default=None):
        if key in self._fake:
            return self._fake[key]
        return dict.get(self, key, default)


class RaisingGet(dict):
    def get(self, key, default=None):
        raise RuntimeError("marker get")


class LyingContains(dict):
    def __init__(self, stored, present):
        super().__init__(stored)
        self._present = present

    def __contains__(self, key):
        return self._present


class LyingKeys(dict):
    def __init__(self, stored, fake_keys):
        super().__init__(stored)
        self._fake_keys = fake_keys

    def keys(self):
        return list(self._fake_keys)


class LyingItems(dict):
    def __init__(self, stored, fake_items):
        super().__init__(stored)
        self._fake_items = fake_items

    def items(self):
        return list(self._fake_items)


class LyingSubscript(dict):
    def __init__(self, stored, fake):
        super().__init__(stored)
        self._fake = fake

    def __getitem__(self, key):
        if key in self._fake:
            return self._fake[key]
        return dict.__getitem__(self, key)


class LyingCopyMark(dict):
    def __deepcopy__(self, memo):
        return {"affected_share": "fabricated-share", "count": 0,
                "resolved": True}


class RaisingCopyPart:
    def __deepcopy__(self, memo):
        raise RuntimeError("marker copy")


def components():
    return {
        "attacker_controlled_share": {
            "numerator": 3, "denominator": 10, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count"},
        "farm_share_of_reputation_mass": {
            "numerator": 1.5, "denominator": 5.0, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "binary64 value",
            "denominator_kind": "binary64 value"},
        "largest_component_share": {
            "component_size": 4, "population_size": 10,
            "proportion": 0.4,
            "component_definition_version": "version in force",
            "viewer_identifier": "viewer-1",
            "component_size_kind": "integer count",
            "population_size_kind": "integer count"},
        "honest_loss_rate": {
            "numerator": 1, "denominator": 10, "rate": 0.1,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count"},
    }


class TestR14007Mod10BooleanValidators(unittest.TestCase):
    def test_storage_claim_both_directions_and_raising(self):
        bad = {"basis": "DQ7-08", "reliance": "governing"}
        good = {"basis": "DQ7-03", "reliance": "recorded"}
        self.assertFalse(mod10.validate_storage_claim(bad))
        self.assertTrue(mod10.validate_storage_claim(good))
        self.assertFalse(mod10.validate_storage_claim(
            LyingGet(bad, {"basis": "DQ7-03", "reliance": "recorded"})))
        self.assertTrue(mod10.validate_storage_claim(
            LyingGet(good, {"basis": "DQ7-08", "reliance": "governing"})))
        self.assertFalse(mod10.validate_storage_claim(RaisingGet(bad)))

    def test_retention_report_both_directions(self):
        bad = {"source": "interval_records", "tier_claim": "final"}
        good = {"source": "summary", "tier_claim": "draft"}
        self.assertFalse(mod10.validate_retention_report(bad))
        self.assertTrue(mod10.validate_retention_report(good))
        self.assertFalse(mod10.validate_retention_report(
            LyingGet(bad, {"source": "summary", "tier_claim": "draft"})))
        self.assertTrue(mod10.validate_retention_report(
            LyingGet(good, {"source": "interval_records",
                            "tier_claim": "final"})))

    def test_annotation_claim_both_directions(self):
        bad = {"claim": "annotation_state_equal_across_append"}
        good = {"claim": "another claim"}
        self.assertFalse(mod10.validate_annotation_claim(bad))
        self.assertTrue(mod10.validate_annotation_claim(good))
        self.assertFalse(mod10.validate_annotation_claim(
            LyingGet(bad, {"claim": "another claim"})))
        self.assertTrue(mod10.validate_annotation_claim(
            LyingGet(good, {"claim": "annotation_state_equal_across_append"})))

    def test_sample_record_both_directions(self):
        bad = {"presented_as": "generator_test_battery_sample"}
        good = {"presented_as": "ordinary sample"}
        self.assertFalse(mod10.validate_sample_record(bad))
        self.assertTrue(mod10.validate_sample_record(good))
        self.assertFalse(mod10.validate_sample_record(
            LyingGet(bad, {"presented_as": "ordinary sample"})))
        self.assertTrue(mod10.validate_sample_record(
            LyingGet(good, {"presented_as": "generator_test_battery_sample"})))
        bad2 = {"kind": "retention_sample", "in_family_record": False}
        good2 = {"kind": "retention_sample", "in_family_record": True,
                 "registration_standing": "before_runs"}
        self.assertFalse(mod10.validate_sample_record(bad2))
        self.assertTrue(mod10.validate_sample_record(good2))
        self.assertFalse(mod10.validate_sample_record(
            LyingGet(bad2, {"in_family_record": True,
                            "registration_standing": "before_runs"})))

    def test_retention_record_both_directions(self):
        bad = {"governing_rule": "DQ7-08 rule", "reliance": "governing"}
        good = {"governing_rule": "DQ7-08 rule", "reliance": "recorded"}
        self.assertFalse(mod10.validate_retention_record(bad))
        self.assertTrue(mod10.validate_retention_record(good))
        self.assertFalse(mod10.validate_retention_record(
            LyingGet(bad, {"reliance": "recorded"})))
        self.assertTrue(mod10.validate_retention_record(
            LyingGet(good, {"reliance": "governing"})))

    def test_store_placement_both_directions_and_contains(self):
        bad = {"kind": "pilot", "store": "archive"}
        good = {"kind": "pilot", "store": "pilot"}
        self.assertFalse(mod10.validate_store_placement(bad))
        self.assertTrue(mod10.validate_store_placement(good))
        self.assertFalse(mod10.validate_store_placement(
            LyingGet(bad, {"store": "pilot"})))
        self.assertTrue(mod10.validate_store_placement(
            LyingGet(good, {"store": "archive"})))
        valued = {"kind": "pilot", "store": "pilot", "value": 1}
        self.assertFalse(mod10.validate_store_placement(valued))
        self.assertFalse(mod10.validate_store_placement(
            LyingContains(valued, False)))

    def test_retention_sizing_both_directions_and_nested(self):
        good = {"workings": {"central_form": {},
                             "high_form": {"events_per_agent_per_day": 5}},
                "wording": {"a": "statement"}}
        empty = {"workings": {}, "wording": {}}
        self.assertTrue(mod10.validate_retention_sizing(good))
        self.assertFalse(mod10.validate_retention_sizing(empty))
        self.assertTrue(mod10.validate_retention_sizing(
            LyingGet(good, {"workings": {}})))
        self.assertFalse(mod10.validate_retention_sizing(
            LyingGet(empty, {"workings": good["workings"]})))
        no_count = {"workings": {"central_form": {}, "high_form": {}},
                    "wording": {}}
        self.assertFalse(mod10.validate_retention_sizing(no_count))
        nested = {"workings": LyingGet(
            no_count["workings"],
            {"high_form": {"events_per_agent_per_day": 5}}),
            "wording": {}}
        self.assertFalse(mod10.validate_retention_sizing(nested))
        forecast = {"workings": good["workings"],
                    "wording": {"a": "forecast"}}
        self.assertFalse(mod10.validate_retention_sizing(forecast))
        self.assertFalse(mod10.validate_retention_sizing(
            LyingGet(forecast, {"wording": {"a": "statement"}})))

    def test_view_carriage_both_directions(self):
        bad = {"form": "singular_vector"}
        good = {"form": "per viewer"}
        self.assertFalse(mod10.validate_view_carriage(bad))
        self.assertTrue(mod10.validate_view_carriage(good))
        self.assertFalse(mod10.validate_view_carriage(
            LyingGet(bad, {"form": "per viewer"})))
        self.assertTrue(mod10.validate_view_carriage(
            LyingGet(good, {"form": "singular_vector"})))


class TestR14008Mod10AnsweringActs(unittest.TestCase):
    def test_retention_met_both_directions(self):
        met = {"later_evaluation": {"conditions": [1, 2, 3],
                                    "inputs": {"x": 1}, "outcome": "o"},
               "summary_record_written": True,
               "retained_forms_pointed_to": True}
        bare = {"state": "x"}
        self.assertTrue(mod10.retention_met(met))
        self.assertFalse(mod10.retention_met(bare))
        self.assertTrue(mod10.retention_met(
            LyingGet(met, {"summary_record_written": None})))
        fake_later = {"conditions": [1, 2, 3], "inputs": {"x": 1},
                      "outcome": "o"}
        self.assertFalse(mod10.retention_met(LyingGet(
            bare, {"later_evaluation": fake_later,
                   "summary_record_written": True,
                   "retained_forms_pointed_to": True})))

    def test_annotation_link_stored_and_raising(self):
        stored = {"annotation_link_identifier": "link-stored"}
        self.assertEqual(
            mod10.annotation_link_at_checkpoint(stored), "link-stored")
        self.assertEqual(mod10.annotation_link_at_checkpoint(
            LyingGet(stored, {"annotation_link_identifier": "link-fake"})),
            "link-stored")
        self.assertEqual(mod10.annotation_link_at_checkpoint(
            RaisingGet(stored)), "link-stored")


class TestR14009Mod10JointVector(unittest.TestCase):
    def test_vector_built_only_from_stored_components(self):
        record = mod10.build_joint_outcome_vector(components=components())
        self.assertEqual(
            record["attacker_controlled_share"]["numerator"], 3)
        stored_only = {"unrelated": 1}
        dressed = LyingGet(stored_only, components())
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=dressed)
        nested = components()
        nested["attacker_controlled_share"] = LyingGet(
            {"numerator": 3}, components()["attacker_controlled_share"])
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=nested)


class TestR14010Mod11Validators(unittest.TestCase):
    def test_bounding_headline_both_directions(self):
        good = {"axes": list(mod11.AXES),
                "traces": [{"moved": True}, {"moved": False},
                           {"moved": True}],
                "rests_on_axis": "farm size"}
        bad = dict(good, axes=["wrong axis"])
        self.assertTrue(mod11.validate_bounding_headline(good, {}, {}))
        self.assertFalse(mod11.validate_bounding_headline(bad, {}, {}))
        self.assertTrue(mod11.validate_bounding_headline(
            LyingGet(good, {"axes": ["wrong axis"]}), {}, {}))
        self.assertFalse(mod11.validate_bounding_headline(
            LyingGet(bad, {"axes": list(mod11.AXES)}), {}, {}))

    def test_envelope_claim_both_directions(self):
        good = {"scope": "sampled points and stated ranges only",
                "claims_between_points": False}
        bad = {"scope": "everywhere", "claims_between_points": True}
        self.assertTrue(mod11.validate_envelope_claim(good))
        self.assertFalse(mod11.validate_envelope_claim(bad))
        self.assertTrue(mod11.validate_envelope_claim(
            LyingGet(good, {"scope": "everywhere"})))
        self.assertFalse(mod11.validate_envelope_claim(LyingGet(
            bad, {"scope": "sampled points and stated ranges only",
                  "claims_between_points": False})))

    def test_observation_time_both_directions(self):
        good = {"interval": [1, 2]}
        bad = {"exact_event_time": 5, "interval": [1, 2]}
        self.assertTrue(mod11.validate_observation_time(good))
        self.assertFalse(mod11.validate_observation_time(bad))
        self.assertTrue(mod11.validate_observation_time(
            LyingGet(good, {"exact_event_time": 5})))
        self.assertFalse(mod11.validate_observation_time(
            LyingGet(bad, {"exact_event_time": None})))

    def test_transition_report_and_nested_point(self):
        good = {"distribution_near_threshold": True,
                "regime_class_counts": {"a": 1, "b": 2, "c": 3},
                "honest_loss_rate": {"form": "H1"},
                "points": [{"near_threshold": True, "replicates": 40}]}
        bad = dict(good, honest_loss_rate={"form": "H2"})
        self.assertTrue(mod11.validate_transition_report(good))
        self.assertFalse(mod11.validate_transition_report(bad))
        self.assertFalse(mod11.validate_transition_report(
            LyingGet(bad, {"honest_loss_rate": {"form": "H1"}})))
        low = dict(good, points=[{"near_threshold": True, "replicates": 5}])
        self.assertFalse(mod11.validate_transition_report(low))
        dressed_low = dict(good, points=[LyingGet(
            {"near_threshold": True, "replicates": 5},
            {"replicates": 40})])
        self.assertFalse(mod11.validate_transition_report(dressed_low))

    def test_transition_unit_and_nested_figure(self):
        good = {"transition_figure": {
                    "cumulative_incidence": {"r": 1},
                    "right_censored": 0.1, "horizon": 10},
                "incidence_label":
                    "derived from the replicate counts in this unit",
                "location_sentences": ["the location at 10 days horizon"]}
        bad = dict(good, transition_figure={"horizon": 10})
        self.assertTrue(mod11.validate_transition_unit(good))
        self.assertFalse(mod11.validate_transition_unit(bad))
        self.assertFalse(mod11.validate_transition_unit(LyingGet(
            bad, {"transition_figure": good["transition_figure"]})))
        dressed = dict(good, transition_figure=LyingContains(
            good["transition_figure"], False))
        self.assertTrue(mod11.validate_transition_unit(dressed))

    def test_readout_and_nested_quantity(self):
        good = {"quantities": [{"name": "share value",
                                "recorded_number": 3}]}
        bad = {"quantities": [{"name": "share value",
                               "recorded_number": "3"}]}
        empty = {"quantities": []}
        self.assertTrue(mod11.validate_readout(good))
        self.assertFalse(mod11.validate_readout(bad))
        self.assertFalse(mod11.validate_readout(empty))
        self.assertFalse(mod11.validate_readout(LyingGet(
            empty, {"quantities": good["quantities"]})))
        dressed = {"quantities": [LyingGet(
            {"name": "share value", "recorded_number": "3"},
            {"recorded_number": 3})]}
        self.assertFalse(mod11.validate_readout(dressed))

    def test_disclosure_form_keys_protocol(self):
        good = {"entries": [{"row": "r1", "column": "c1", "quantity": 2}]}
        bad = {"entries": [{"quantity": 2, "row": "r1", "column": "c1"}]}
        self.assertTrue(mod11.validate_disclosure_form(good))
        self.assertFalse(mod11.validate_disclosure_form(bad))
        dressed = {"entries": [LyingKeys(
            {"quantity": 2, "row": "r1", "column": "c1"},
            ["row", "column", "quantity"])]}
        self.assertFalse(mod11.validate_disclosure_form(dressed))
        dressed_good = {"entries": [LyingKeys(
            {"row": "r1", "column": "c1", "quantity": 2},
            ["quantity", "row", "column"])]}
        self.assertTrue(mod11.validate_disclosure_form(dressed_good))


class TestR14011Mod11AnsweringActs(unittest.TestCase):
    def test_location_for_endpoint_stored_only(self):
        plain = {"cumulative_incidence": {"regime": {"share": 0.5}}}
        self.assertIsNone(mod11.location_for_endpoint(plain, "regime", 0.9))
        dressed = LyingGet(plain, {"cumulative_incidence":
                                   {"regime": {"share": 0.99}}})
        self.assertIsNone(mod11.location_for_endpoint(dressed, "regime", 0.9))
        rich = {"cumulative_incidence": {"regime": {"share": 0.99}}}
        self.assertEqual(
            mod11.location_for_endpoint(rich, "regime", 0.9)["share"], 0.99)

    def test_reporter_inputs_get_and_deepcopy_limbs(self):
        records = {"divergence_count": 3,
                   "blocked_family_mark": {"affected_share": "real-share",
                                           "count": 2,
                                           "resolved": False}}
        out = mod11.reporter_inputs_for_family(records)
        self.assertEqual(out["divergence_count"], 3)
        dressed = LyingGet(records, {"divergence_count": 999})
        self.assertEqual(
            mod11.reporter_inputs_for_family(dressed)["divergence_count"], 3)
        lying_mark = {"blocked_family_mark": LyingCopyMark(
            {"affected_share": "real-share", "count": 2,
             "resolved": False})}
        out2 = mod11.reporter_inputs_for_family(lying_mark)
        self.assertEqual(out2["blocked_family_mark"],
                         {"affected_share": "real-share", "count": 2,
                          "resolved": False})
        raising_mark = {"blocked_family_mark":
                        {"part": RaisingCopyPart()}}
        out3 = mod11.reporter_inputs_for_family(raising_mark)
        self.assertIsInstance(
            out3["blocked_family_mark"]["part"], RaisingCopyPart)

    def test_share_report_stands_both_directions(self):
        mark = {"affected_share": "share-x", "count": 2, "resolved": False}
        blocked = {"blocked_family_mark": mark}
        self.assertFalse(mod11.share_report_stands(blocked, "share-x"))
        self.assertTrue(mod11.share_report_stands({}, "share-x"))
        self.assertFalse(mod11.share_report_stands(
            LyingGet(blocked, {"blocked_family_mark": None}), "share-x"))
        dressed_mark = {"blocked_family_mark": LyingGet(
            mark, {"count": 0})}
        self.assertFalse(mod11.share_report_stands(dressed_mark, "share-x"))


class TestR14012Mod14OperatorBoundary(unittest.TestCase):
    def test_stored_delete_on_sealed_record_refused(self):
        bad = {"kind": "delete", "target": "sealed family record"}
        good = {"kind": "read", "target": "ordinary record"}
        self.assertFalse(mod14.validate_operator_action(bad))
        self.assertTrue(mod14.validate_operator_action(good))
        self.assertFalse(mod14.validate_operator_action(
            LyingGet(bad, {"kind": "read"})))
        self.assertFalse(mod14.validate_operator_action_with_reason(
            LyingGet(bad, {"kind": "read"}))["allowed"])
        self.assertTrue(mod14.validate_operator_action(
            LyingGet(good, {"kind": "delete",
                            "target": "sealed family record"})))


class TestR14013Mod14Pilot(unittest.TestCase):
    def test_pilot_claim_both_directions(self):
        bad = {"cites_pilot_output": True, "kind": "behaviour"}
        good = {"kind": "behaviour"}
        self.assertFalse(mod14.validate_pilot_claim(bad))
        self.assertTrue(mod14.validate_pilot_claim(good))
        self.assertFalse(mod14.validate_pilot_claim(
            LyingGet(bad, {"cites_pilot_output": False})))
        self.assertTrue(mod14.validate_pilot_claim(
            LyingGet(good, {"cites_pilot_output": True,
                            "kind": "behaviour"})))

    def test_pilot_confinement_gate_stored_only(self):
        bad = {"material_class": "sweep material", "figure": 1}
        good = {"material_class": "pilot confined", "figure": 1}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.nondeterminism_census(bad)
        census = mod14.nondeterminism_census(good)
        self.assertEqual(census["entries_read"], 1)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.nondeterminism_census(
                LyingGet(bad, {"material_class": "pilot confined"}))
        census2 = mod14.nondeterminism_census(
            LyingGet(good, {"material_class": "sweep material"}))
        self.assertEqual(census2["entries_read"], 1)


class TestR14014Mod05PanelAndCost(unittest.TestCase):
    def test_evaluation_order_both_directions(self):
        bad = {"order": "sequential", "presented_as_ruled": True}
        good = {"order": "sequential"}
        self.assertFalse(mod05.validate_evaluation_order(bad))
        self.assertTrue(mod05.validate_evaluation_order(good))
        self.assertFalse(mod05.validate_evaluation_order(
            LyingGet(bad, {"presented_as_ruled": False})))
        self.assertTrue(mod05.validate_evaluation_order(
            LyingGet(good, {"presented_as_ruled": True})))

    def test_view_wording_both_directions(self):
        bad = {"description": "summary", "scope": "everyone"}
        good = {"description": "record enforced",
                "scope": "agent held views"}
        self.assertFalse(mod05.validate_view_wording(bad))
        self.assertTrue(mod05.validate_view_wording(good))
        self.assertFalse(mod05.validate_view_wording(LyingGet(
            bad, {"description": "record enforced",
                  "scope": "agent held views"})))
        self.assertTrue(mod05.validate_view_wording(
            LyingGet(good, {"description": "summary"})))

    def test_band_transition_both_directions(self):
        good = {"counts_per_distance_slice": {}, "crossing_count": 1,
                "cheapest_crossing_movement_in_accepted_work_units": 2}
        bad = dict(good, counts_per_distance_slice="no record")
        self.assertTrue(mod05.validate_band_transition_result(good))
        self.assertFalse(mod05.validate_band_transition_result(bad))
        self.assertFalse(mod05.validate_band_transition_result(
            LyingGet(bad, {"counts_per_distance_slice": {}})))
        self.assertTrue(mod05.validate_band_transition_result(
            LyingContains(good, False)))

    def test_cost_statement_both_directions_and_subscript(self):
        good = {"share_log": [{"numerator": 1, "denominator": 2}],
                "degree_distribution_log": {},
                "assumption_share": {"fitted": False}}
        bad = dict(good, assumption_share={"fitted": True})
        self.assertTrue(mod05.cost_statement_valid(good))
        self.assertTrue(mod05.validate_run_share_logs(good))
        self.assertFalse(mod05.cost_statement_valid(bad))
        self.assertFalse(mod05.cost_statement_valid(
            LyingGet(bad, {"assumption_share": {"fitted": False}})))
        self.assertFalse(mod05.validate_run_share_logs(
            LyingGet(bad, {"assumption_share": {"fitted": False}})))
        self.assertTrue(mod05.cost_statement_valid(
            LyingContains(good, False)))
        self.assertTrue(mod05.cost_statement_valid(
            LyingSubscript(good, {"share_log": None})))

    def test_reputation_and_band_values_items_protocol(self):
        bands = [("low", 0), ("high", 5)]
        order = {"order": "sequential"}
        out = mod05.reputation_and_band_values(
            {"agent-a": 10}, bands, evaluation_order=order)
        self.assertEqual(out["values"]["agent-a"]["band"], "high")
        self.assertEqual(out["values"]["agent-a"]["score"], 10)
        dressed = LyingItems({"agent-a": 10}, [("agent-a", 0)])
        out2 = mod05.reputation_and_band_values(
            dressed, bands, evaluation_order=order)
        self.assertEqual(out2["values"]["agent-a"]["band"], "high")
        self.assertEqual(out2["values"]["agent-a"]["score"], 10)


class TestR14015Mod06EscrowAndFolding(unittest.TestCase):
    def test_escrow_result_carries_stored_states(self):
        state = {"k1_and_l2_state": "stored-state",
                 "lien_state": "stored-lien"}
        out = mod06.escrow_result("kind1", payload={}, contract_state=state)
        self.assertEqual(out["k1_and_l2_state"], "stored-state")
        self.assertEqual(out["lien_state"], "stored-lien")
        dressed = LyingGet(state, {"k1_and_l2_state": "fabricated-state",
                                   "lien_state": "fabricated-lien"})
        out2 = mod06.escrow_result(
            "kind1", payload={}, contract_state=dressed)
        self.assertEqual(out2["k1_and_l2_state"], "stored-state")
        self.assertEqual(out2["lien_state"], "stored-lien")

    def test_pause_result_both_directions(self):
        good = {"variant": "B-3", "per_variant_pause_value": 7}
        bad = {"variant": "B-3"}
        self.assertTrue(mod06.validate_pause_result(good))
        self.assertFalse(mod06.validate_pause_result(bad))
        self.assertFalse(mod06.validate_pause_result(
            LyingGet(bad, {"per_variant_pause_value": 7})))
        self.assertTrue(mod06.validate_pause_result(
            LyingGet(good, {"per_variant_pause_value": None})))

    def test_folding_record_and_difference_both_directions(self):
        bad = {"entries": [{"filled_by_inference": True,
                            "checked_by_independent_reader": True,
                            "ruling": "r1"}]}
        good = {"entries": [{"filled_by_inference": False,
                             "checked_by_independent_reader": True,
                             "ruling": "r1"}]}
        self.assertFalse(mod06.validate_folding_record(bad))
        self.assertTrue(mod06.validate_folding_record(good))
        dressed = {"entries": [LyingGet(
            {"filled_by_inference": True,
             "checked_by_independent_reader": True, "ruling": "r1"},
            {"filled_by_inference": False})]}
        self.assertFalse(mod06.validate_folding_record(dressed))
        report = mod06.report_difference("diff", bad)
        self.assertEqual(report["reported_as"], "unfolded difference only")
        self.assertFalse(report["ruling_effect_wording"])
        report2 = mod06.report_difference("diff", dressed)
        self.assertEqual(report2["reported_as"], "unfolded difference only")


class TestR14016Mod16Validators(unittest.TestCase):
    def test_folding_discharge_both_directions(self):
        bad = {"discharged_by_slice_tests_alone": True,
               "checker_distinct_from_folder": True,
               "seam_cases_per_ruling": {"r": 1}}
        good = {"checker_distinct_from_folder": True,
                "seam_cases_per_ruling": {"r": 1}}
        self.assertFalse(mod16.validate_folding_discharge(bad))
        self.assertTrue(mod16.validate_folding_discharge(good))
        self.assertFalse(mod16.validate_folding_discharge(
            LyingGet(bad, {"discharged_by_slice_tests_alone": False})))
        self.assertTrue(mod16.validate_folding_discharge(
            LyingGet(good, {"discharged_by_slice_tests_alone": True})))

    def test_tracer_wording_both_directions(self):
        bad = {"slice_built_because_tracer_ran": True}
        good = {}
        self.assertFalse(mod16.validate_tracer_wording(bad))
        self.assertTrue(mod16.validate_tracer_wording(good))
        self.assertFalse(mod16.validate_tracer_wording(
            LyingGet(bad, {"slice_built_because_tracer_ran": False})))
        self.assertTrue(mod16.validate_tracer_wording(
            LyingGet(good, {"slice_built_because_tracer_ran": True})))

    def test_mixed_patience_both_directions(self):
        bad = {"distribution_shape": "bimodal"}
        good = {"distribution_shape": "bimodal",
                "labelled_assumption_in_family_record": True,
                "recorded_before_runs": True, "falsifier_stated": True}
        self.assertFalse(mod16.validate_mixed_patience(bad))
        self.assertTrue(mod16.validate_mixed_patience(good))
        self.assertFalse(mod16.validate_mixed_patience(LyingGet(bad, {
            "labelled_assumption_in_family_record": True,
            "recorded_before_runs": True, "falsifier_stated": True})))
        self.assertTrue(mod16.validate_mixed_patience(
            LyingGet(good, {"falsifier_stated": False})))

    def test_fixture_record_contains_protocol(self):
        bad = {"ran": False}
        good = {"ran": True, "showed": "x", "does_not_show": "y",
                "value_source": "brief"}
        self.assertFalse(mod16.validate_fixture_record(bad))
        self.assertTrue(mod16.validate_fixture_record(good))
        self.assertFalse(mod16.validate_fixture_record(
            LyingContains(bad, True)))
        self.assertTrue(mod16.validate_fixture_record(
            LyingContains(good, False)))

    def test_confirmation_result_both_directions(self):
        bad = {"run_class": "confirmation", "seed_domain": "screening"}
        good = {"run_class": "confirmation", "seed_domain": "production"}
        self.assertFalse(mod16.validate_confirmation_result(bad))
        self.assertTrue(mod16.validate_confirmation_result(good))
        self.assertFalse(mod16.validate_confirmation_result(
            LyingGet(bad, {"seed_domain": "production"})))
        self.assertTrue(mod16.validate_confirmation_result(
            LyingGet(good, {"seed_domain": "screening"})))
        self.assertFalse(mod16.validate_confirmation_result(
            LyingContains({"seed_domain": "production"}, True)))

    def test_headline_claim_both_directions(self):
        bad = {"headline_claim": True, "material": "validation"}
        good = {"headline_claim": True, "material": "sweep"}
        self.assertFalse(mod16.validate_headline_claim(bad))
        self.assertTrue(mod16.validate_headline_claim(good))
        self.assertFalse(mod16.validate_headline_claim(
            LyingGet(bad, {"material": "sweep"})))
        self.assertTrue(mod16.validate_headline_claim(
            LyingGet(good, {"material": "validation"})))
        self.assertFalse(mod16.validate_headline_claim(
            LyingContains({"material": "sweep"}, True)))

    def test_horizon_generalisation_both_directions(self):
        bad = {"generalised_to_grid": True}
        good = {"generalised_to_grid": False}
        self.assertFalse(mod16.validate_horizon_generalisation(bad))
        self.assertTrue(mod16.validate_horizon_generalisation(good))
        self.assertFalse(mod16.validate_horizon_generalisation(
            LyingGet(bad, {"generalised_to_grid": False})))
        self.assertTrue(mod16.validate_horizon_generalisation(
            LyingGet(good, {"generalised_to_grid": True})))
        self.assertFalse(mod16.validate_horizon_generalisation(
            LyingContains({}, True)))


class TestR14017Mod04Projection(unittest.TestCase):
    def test_projection_reads_stored_state_only(self):
        state = {"agent_identifier": "agent-1", "day": 3,
                 "feature_values": {}, "rule_records": []}
        out = mod04.project_detection_input(state)
        self.assertEqual(out["agent_identifier"], "agent-1")
        self.assertEqual(out["day"], 3)
        out2 = mod04.project_detection_input(LyingContains(state, False))
        self.assertEqual(out2["agent_identifier"], "agent-1")
        self.assertEqual(out2["day"], 3)
        out3 = mod04.project_detection_input(
            LyingSubscript(state, {"agent_identifier": "fabricated-id"}))
        self.assertEqual(out3["agent_identifier"], "agent-1")


class TestR14018Mod01MinimalInstance(unittest.TestCase):
    def test_minimal_instance_reads_stored_condition_field(self):
        plain = mod01.minimal_valid_instance(
            2, condition_holds={"field": "decay_slice"})
        self.assertTrue(plain["belongs_to_decay_arm"])
        self.assertIn("decay_slice", plain)
        dressed = LyingGet({"field": "decay_slice"},
                           {"field": "no such field"})
        out = mod01.minimal_valid_instance(2, condition_holds=dressed)
        self.assertTrue(out["belongs_to_decay_arm"])
        self.assertIn("decay_slice", out)


if __name__ == "__main__":
    unittest.main()

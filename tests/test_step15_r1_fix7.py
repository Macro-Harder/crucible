"""Step 15 Round 1 supplementary fix pins, Fix Builder 7, cluster A.

Pins for TA-04, TA-18, TA-23, TA-66, TA-67 on the MOD-03 surfaces,
TA-52 and TA-53 on the MOD-07 surfaces, and the TA-30 severed limbs
on the MOD-08 and MOD-09 surfaces. Each test was written before its
cure and seen to fail on the uncured tree. No detection score is
reported as a pass or as a fail in this file; detection outputs are
checked for their profile bound label carriage only, under OP-16.
"""

import unittest

from crucible import mod03, mod07, mod08, mod09


PROJECTION_KEYS = (
    "ground_truth", "ground_truth_field", "membership",
    "honest_membership", "farm_membership", "is_honest", "is_farm",
    "canary", "canary_value", "membership_value", "sleeper",
    "ground_truth_label", "label",
)

VARIANT_KEYS = (
    "GROUND_TRUTH", "Ground_Truth_Label", "groundtruth",
    "sleeper_membership_score", "derived_from_membership",
    "ground_truth_derived_score",
)


def _nested_record(key):
    return {"feature_values": {"nested": {key: "CANARY", "activity": 1}}}


def _honest_record():
    return mod03.make_archetype_record(
        archetype_id="honest", behaviour={"action": "vouch"})


def _farm_record():
    return mod03.make_archetype_record(
        archetype_id="farm", behaviour={"action": "link"},
        farm_member=True)


class TestFix7TA04BarredVocabulary(unittest.TestCase):
    def test_projection_keys_rejected_and_stripped_at_depth(self):
        for key in PROJECTION_KEYS:
            with self.subTest(key=key):
                record = _nested_record(key)
                self.assertTrue(mod03.record_carries_ground_truth(record))
                self.assertFalse(mod03.validate_detection_input(record))
                self.assertFalse(mod03.validate_adjudication_input(record))
                stripped = mod03.strip_ground_truth(record)
                self.assertEqual(
                    stripped, {"feature_values": {"nested": {"activity": 1}}})

    def test_variant_keys_rejected_and_stripped_at_depth(self):
        for key in VARIANT_KEYS:
            with self.subTest(key=key):
                record = _nested_record(key)
                self.assertFalse(mod03.validate_detection_input(record))
                self.assertFalse(mod03.validate_adjudication_input(record))
                stripped = mod03.strip_ground_truth(record)
                self.assertEqual(
                    stripped, {"feature_values": {"nested": {"activity": 1}}})

    def test_legitimate_sibling_content_survives(self):
        record = {"feature_values": {
            "activity": 1, "labelled_assumptions": "case"}}
        self.assertTrue(mod03.validate_detection_input(record))
        self.assertTrue(mod03.validate_adjudication_input(record))
        self.assertEqual(mod03.strip_ground_truth(record), record)


class TestFix7TA18ZeroEdgeSociety(unittest.TestCase):
    def _point_with_edge(self):
        return {
            "population": 2,
            "archetype_mix": {"farm": 2},
            "farm_size": 2,
            "initial_edges": [
                {"voucher": "agent-0000", "vouchee": "agent-0001",
                 "stake": 9}],
        }

    def test_zero_edge_society_excludes_point_edges(self):
        records = [_farm_record(), _honest_record()]
        society = mod03.zero_edge_society(
            self._point_with_edge(), records, strategy_class="fixed")
        self.assertEqual(society["initial_graph"], {"edges": []})
        self.assertEqual(society["attack_edge_count"], 0)
        self.assertEqual(society["summed_stake"], 0)
        self.assertEqual(
            society["internal_edge_count_per_farm"], {"farm-0": 0})

    def test_explicit_empty_edge_list_means_no_edges(self):
        records = [_farm_record(), _honest_record()]
        cast = mod03.build_cast(
            self._point_with_edge(), records, strategy_class="fixed",
            initial_edges=())
        self.assertEqual(cast["initial_graph"], {"edges": []})
        self.assertEqual(
            cast["internal_edge_count_per_farm"], {"farm-0": 0})

    def test_ordinary_cast_states_the_edge_it_carries(self):
        records = [_farm_record(), _honest_record()]
        cast = mod03.build_cast(
            self._point_with_edge(), records, strategy_class="fixed")
        self.assertEqual(len(cast["initial_graph"]["edges"]), 1)
        self.assertEqual(cast["initial_graph"]["edges"][0]["stake"], 9)
        self.assertEqual(
            cast["internal_edge_count_per_farm"], {"farm-0": 1})


class TestFix7TA23ValidatorTypeLimb(unittest.TestCase):
    def test_non_record_values_fail_both_validators(self):
        for value in (None, 42, "x", []):
            with self.subTest(value=repr(value)):
                self.assertFalse(mod03.validate_detection_input(value))
                self.assertFalse(mod03.validate_adjudication_input(value))

    def test_clean_record_still_passes(self):
        record = {"feature_values": {"activity": 1}}
        self.assertTrue(mod03.validate_detection_input(record))
        self.assertTrue(mod03.validate_adjudication_input(record))


class TestFix7TA66GeneratorOutputDepth(unittest.TestCase):
    def test_nested_decided_effect_fails(self):
        self.assertFalse(mod03.validate_generator_output(
            [{"effect": {"reputation": 5}}]))
        self.assertFalse(mod03.validate_generator_output(
            [{"outer": [{"decided_effect": "sealed"}]}]))
        self.assertFalse(mod03.validate_generator_output(
            {"a": {"b": {"stake_held": 1}}}))

    def test_flat_lawful_output_still_passes(self):
        proposals = [{
            "agent_id": "agent-0000", "archetype_id": "honest",
            "action": "vouch", "draw": 0.5,
            "assumptions": {"labelled": "case"}}]
        self.assertTrue(mod03.validate_generator_output(proposals))
        self.assertFalse(mod03.validate_generator_output(
            [{"reputation": 5}]))


class TestFix7TA67BuildCastPopulation(unittest.TestCase):
    def test_negative_population_fails_in_module_form(self):
        point = {"population": -1, "archetype_mix": {"honest": -1}}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                point, [_honest_record()], strategy_class="fixed")

    def test_float_population_fails_in_module_form(self):
        point = {"population": 2.5, "archetype_mix": {"honest": 2.5}}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                point, [_honest_record()], strategy_class="fixed")

    def test_negative_mix_count_fails_in_module_form(self):
        point = {"population": 2,
                 "archetype_mix": {"honest": 3, "farm": -1}}
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                point, [_honest_record(), _farm_record()],
                strategy_class="fixed")

    def test_farm_members_without_farm_size_state_non_construction(self):
        point = {"population": 2, "archetype_mix": {"farm": 2}}
        cast = mod03.build_cast(
            point, [_farm_record()], strategy_class="fixed")
        self.assertEqual(cast["farms"], [])
        self.assertIn("farm_construction", cast)
        self.assertIn("no farm size", cast["farm_construction"])

    def test_lawful_points_unchanged(self):
        point = {"population": 3,
                 "archetype_mix": {"honest": 2, "farm": 1},
                 "farm_size": 2}
        records = [_honest_record(), _farm_record()]
        cast = mod03.build_cast(point, records, strategy_class="fixed")
        self.assertEqual(cast["population"], 3)
        self.assertEqual(len(cast["cast"]), 3)
        self.assertEqual(len(cast["farms"]), 1)
        self.assertNotIn("farm_construction", cast)
        plain = {"population": 2, "archetype_mix": {"honest": 2}}
        plain_cast = mod03.build_cast(
            plain, [_honest_record()], strategy_class="fixed")
        self.assertEqual(len(plain_cast["cast"]), 2)
        self.assertNotIn("farm_construction", plain_cast)


class TestFix7TA52SeamWording(unittest.TestCase):
    def test_mixed_texts_fail(self):
        self.assertFalse(mod07.validate_seam_wording(
            "computed in Parley, the lien was released"))
        self.assertFalse(mod07.validate_seam_wording(
            "not settled in escrow but settled in Parley"))

    def test_clean_and_plain_forms_unchanged(self):
        self.assertTrue(mod07.validate_seam_wording(
            "computed in Parley and not settled in the chosen escrow"))
        self.assertFalse(mod07.validate_seam_wording("the lien is settled"))
        self.assertFalse(mod07.validate_seam_wording(
            "the vouch release was released at the seam"))
        report = mod07.seam_effect_report({"kind": "vouch lien amount",
                                           "value": 1})
        self.assertTrue(mod07.validate_seam_wording(report["reporting"]))


class TestFix7TA53TracerPassageSet(unittest.TestCase):
    def setUp(self):
        self.records = mod07.tracer_passage_records("run-fix7")

    def test_bare_boolean_control_fails(self):
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.records, {"recorded_as_passing": True}))

    def test_wrong_path_blocked_control_fails(self):
        control = dict(mod07.positive_control_record())
        control["path"] = "some other path"
        control["result"] = "blocked"
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.records, control))

    def test_missing_fixture_control_fails(self):
        control = dict(mod07.positive_control_record())
        del control["fixture"]
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.records, control))

    def test_module_own_control_still_validates(self):
        self.assertTrue(mod07.validate_tracer_passage_set(
            self.records, mod07.positive_control_record()))
        self.assertTrue(mod07.validate_tracer_passage_set(self.records))
        failing = {"fixture": "F-10", "path": "escrow request lien path",
                   "result": "blocked", "recorded_as_passing": False}
        self.assertFalse(mod07.validate_tracer_passage_set(
            self.records, failing))

    def test_joint_run_gate_uses_the_cured_control_check(self):
        run = {
            "adapter_choices": [],
            "tracer_passage_records": self.records,
            "positive_control": {"recorded_as_passing": True},
            "cross_seam_effects": [],
        }
        self.assertFalse(mod07.validate_joint_run(run))
        run["positive_control"] = mod07.positive_control_record()
        self.assertTrue(mod07.validate_joint_run(run))


class TestFix7TA30Mod08Score(unittest.TestCase):
    def test_score_on_none_raises_the_named_failure(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score(None)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day(None)

    def test_well_formed_input_unchanged_in_carriage(self):
        record = {"agent_identifier": "agent-1", "day": 1,
                  "feature_values": {"x": 5},
                  "records_for_agent_and_day": []}
        result = mod08.score(record)
        self.assertEqual(
            result[mod08.PROFILE_BOUND_LABEL_FIELD],
            mod08.PROFILE_LABEL_CARRIAGE)
        self.assertIsNone(result["score_verdict"])
        self.assertEqual(len(result["verdict_states"]), 1)


class TestFix7TA30Mod09AttackerSurfaces(unittest.TestCase):
    def test_attacker_payoff_wrong_typed_strategy(self):
        for strategy in ({}, None, "x"):
            with self.subTest(strategy=repr(strategy)):
                with self.assertRaises(mod09.NamedAttackerFailure):
                    mod09.attacker_payoff(strategy, 1)

    def test_bond_search_wrong_typed_candidates(self):
        for candidates in ([-5], ["x"], 42):
            with self.subTest(candidates=repr(candidates)):
                with self.assertRaises(mod09.NamedAttackerFailure):
                    mod09.bond_search(candidates)

    def test_well_formed_inputs_unchanged(self):
        strategy = mod09.make_strategy("s", in_protocol_payoff=3)
        self.assertEqual(mod09.attacker_payoff(strategy, 4), 7)
        result = mod09.bond_search(
            [{"parameter_set": {"a": 1}, "attacker_cost": 2, "harm": 6}])
        self.assertEqual(result["worst_griefing_factor"], 3.0)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search(None)
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.bond_search([])


if __name__ == "__main__":
    unittest.main()

"""Step 15 Round 1 supplementary fix pins for cluster C, Fix Builder 9.

Each test pins one charged cure: TB-40 and TB-42 on the MOD-10
surface, the MOD-04 limbs of TB-06 and C-18, and C-23 on the MOD-01
specification and the MOD-10 builder. Tests reset the module stores
around themselves so their standing does not depend on suite order.
"""
import unittest

import crucible.mod01 as mod01
import crucible.mod04 as mod04
import crucible.mod10 as mod10


class Fix9Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestTB40RetentionSizing(Fix9Base):
    def test_tb40_high_activity_figure_stands(self):
        sizing = mod10.retention_sizing(fixture="F-27", costing_forms="F-19")
        high = sizing["workings"]["high_form"]
        self.assertEqual(high["events_per_agent_per_day"], 25.71)
        self.assertIn("provenance", high)
        self.assertTrue(mod10.validate_retention_sizing(sizing))

    def test_tb40_validator_refuses_high_working_with_no_figure(self):
        sizing = mod10.retention_sizing(fixture="F-27", costing_forms="F-19")
        sizing["workings"]["high_form"]["events_per_agent_per_day"] = None
        self.assertFalse(mod10.validate_retention_sizing(sizing))


class TestTB42ComputedSummaryTier(Fix9Base):
    def _computed(self, run_id, record):
        record.setdefault("run_id", run_id)
        record.setdefault("run_identifier", run_id)
        mod10.retain_run_record(record)
        return mod10.summary_record_for_run(run_id)

    def test_tb42_class_derived_tiers(self):
        cases = (
            ("screening", "Tier 1"),
            ("confirmation", "Tier 2"),
            ("headline", "Tier 3"),
            ("validation", "Tier 3"),
        )
        for run_class, tier in cases:
            run_id = "run-fix9-" + run_class
            summary = self._computed(run_id, {"run_class": run_class})
            self.assertEqual(summary["retention_tier"], tier, run_class)
            self.assertIn("computed", summary["carriage"])

    def test_tb42_group_carried_class_derives_tier(self):
        summary = self._computed("run-fix9-grouped", {
            "groups": {"identity_and_design": {"run_class": "screening"}},
        })
        self.assertEqual(summary["retention_tier"], "Tier 1")

    def test_tb42_no_class_asserts_no_tier(self):
        summary = self._computed("run-fix9-classless", {"groups": {}})
        self.assertNotIn("retention_tier", summary)

    def test_tb42_stored_record_path_unchanged(self):
        mod10.write_summary_record({
            "run_id": "run-fix9-stored", "retention_tier": "Tier 2",
            "run_class": "screening", "written_at": "run_close",
        })
        stored = mod10.summary_record_for_run("run-fix9-stored")
        self.assertEqual(stored["retention_tier"], "Tier 2")
        self.assertEqual(stored["written_at"], "run_close")


def _view_record():
    return mod04.build_view_record(
        run_id="run-fix9-view", viewer_id="viewer-1", day=2,
        contents=[{"day": 1, "delay": 0}],
        position="pos-1", rule_version_set="rv-1")


class TestTB06Mod04Wiring(Fix9Base):
    def test_tb06_release_follows_runner_not_caller_booleans(self):
        held = mod04.hold_view(_view_record())
        released = mod04.release_view(
            held, field_validation_passed=False, timing_passed=False)
        self.assertTrue(released["released"])
        self.assertFalse(released["held"])
        self.assertTrue(released["leak_check"]["reportable"])
        self.assertEqual(
            released["leak_check"]["forms_run"],
            ["canary", "field_validation", "timing"])

    def test_tb06_leaking_view_refused_despite_caller_passes(self):
        record = _view_record()
        record["view_contents"] = [{"membership": "canary value"}]
        held = mod04.hold_view(record)
        with self.assertRaises(Exception) as caught:
            mod04.release_view(
                held, field_validation_passed=True, timing_passed=True)
        self.assertIn("canary", str(caught.exception))
        self.assertIn("run-fix9-view", str(caught.exception))


class TestC18Mod04Writer(Fix9Base):
    def test_c18_writer_writes_state_beside_manifest(self):
        manifest = {
            "run_identifier": "run-fix9-ckpt",
            "run_id": "run-fix9-ckpt",
            "simulated_day": 3,
        }
        result = mod04.write_checkpoint(
            manifest,
            agent_states=[{"agent_identifier": "agent-1"}],
            escrow_contract_states=[],
            detection_state={"state": "stated"},
            stream_positions_and_generator_states={
                "stream-1": {"position": 1}},
            simulation_clock_value=3)
        state = result["checkpoint_state"]
        self.assertEqual(state["run_identifier"], "run-fix9-ckpt")
        self.assertEqual(state["simulated_day"], 3)
        self.assertTrue(mod01.validate_record("13A", state))
        self.assertEqual(
            mod10.checkpoint_state_at("run-fix9-ckpt", 3), state)
        held = mod10.checkpoints_for_run("run-fix9-ckpt")
        self.assertEqual(len(held), 1)
        self.assertEqual(result["manifest"]["checkpoint_state"], state)

    def test_c18_incomplete_state_writes_neither(self):
        manifest = {
            "run_identifier": "run-fix9-ckpt2",
            "run_id": "run-fix9-ckpt2",
            "simulated_day": 4,
        }
        with self.assertRaises(Exception):
            mod04.write_checkpoint(
                manifest,
                agent_states=[],
                escrow_contract_states=[],
                detection_state=None,
                stream_positions_and_generator_states={},
                simulation_clock_value=4)
        self.assertEqual(mod10.checkpoints_for_run("run-fix9-ckpt2"), [])
        self.assertIsNone(mod10.checkpoint_state_at("run-fix9-ckpt2", 4))


def _components():
    return {
        "attacker_controlled_share": {
            "numerator": 3, "denominator": 10, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
        "farm_share_of_reputation_mass": {
            "numerator": 1.5, "denominator": 5.0, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "binary64 value",
            "denominator_kind": "binary64 value",
        },
        "largest_component_share": {
            "component_size": 4, "population_size": 10, "proportion": 0.4,
            "component_definition_version": "version in force",
            "viewer_identifier": "viewer-1",
            "component_size_kind": "integer count",
            "population_size_kind": "integer count",
        },
        "honest_loss_rate": {
            "numerator": 1, "denominator": 10, "rate": 0.1,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
    }


class TestC23Form15Components(Fix9Base):
    def test_c23_bare_integer_components_fail_validation(self):
        instance = {
            "attacker_controlled_share": 1,
            "farm_share_of_reputation_mass": 2,
            "largest_component_share": 3,
            "honest_loss_rate": 4,
            "divergence_companion": {},
        }
        self.assertFalse(mod01.validate_record("15", instance))

    def test_c23_structured_components_validate(self):
        instance = _components()
        instance["divergence_companion"] = {"nil_divergence_components": []}
        self.assertTrue(mod01.validate_record("15", instance))
        self.assertTrue(mod01.validate_record(
            "15", mod01.minimal_valid_instance("15")))

    def test_c23_builder_produces_plan_form(self):
        record = mod10.build_joint_outcome_vector(
            components=_components(),
            divergence_companion={"nil_divergence_components": []})
        self.assertTrue(mod01.validate_record("15", record))
        self.assertEqual(
            record["largest_component_share"]["component_definition_version"],
            "version in force")
        self.assertEqual(
            record["honest_loss_rate"]["loss_definition_version"],
            "loss definition version 1")
        for field in mod01.JOINT_OUTCOME_COMPONENT_PARTS:
            self.assertEqual(
                record[field]["viewer_identifier"], "viewer-1")

    def test_c23_builder_refuses_bare_missing_and_mixed(self):
        bare = _components()
        bare["attacker_controlled_share"] = 1
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=bare)
        missing = _components()
        del missing["farm_share_of_reputation_mass"]["viewer_identifier"]
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=missing)
        mixed = _components()
        mixed["honest_loss_rate"]["viewer_identifier"] = "viewer-2"
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=mixed)


if __name__ == "__main__":
    unittest.main()

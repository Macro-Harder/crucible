"""Step 14 re-run pins for cluster B4, slices S-06 and S-07.

Pins for the TB-52 cure in MOD-07, the TA-30 residual limb in
MOD-08, and the wrong typed input forms of the MOD-07 dependency
validator, the MOD-07 seam effect report, and the MOD-08 verdict
determinism check. Each test states the behaviour it pins.
"""
import unittest

from crucible import mod01, mod07, mod08


def _valid_run():
    return {
        "adapter_choices": [],
        "tracer_passage_records": mod07.tracer_passage_records("run-b04"),
        "positive_control": mod07.positive_control_record(),
        "cross_seam_effects": [],
    }


class TestB04JointRunFailureForm(unittest.TestCase):
    def test_failure_is_the_mod01_failure_value(self):
        run = _valid_run()
        run["tracer_passage_records"] = run["tracer_passage_records"][:-1]
        failure = mod07.joint_run_failure(run)
        self.assertEqual(
            failure,
            mod01.failure_value(
                "joint run missing a tracer passage record fails"))
        self.assertEqual(failure["run_status"], "failed")
        self.assertIs(failure["complete"], False)

    def test_each_ground_carries_its_name_in_the_value(self):
        self.assertEqual(
            mod07.joint_run_failure(None),
            mod01.failure_value("joint run record absent"))
        bad_control = _valid_run()
        bad_control["positive_control"] = {"recorded_as_passing": True}
        self.assertEqual(
            mod07.joint_run_failure(bad_control),
            mod01.failure_value(
                "joint run has no valid tracer passage record"))
        settled = _valid_run()
        settled["cross_seam_effects"] = [
            {"kind": "vouch release", "lien_state": "released"}]
        self.assertEqual(
            mod07.joint_run_failure(settled),
            mod01.failure_value(
                "cross seam effect carries settled wording"))

    def test_standing_run_has_no_failure_value(self):
        self.assertIsNone(mod07.joint_run_failure(_valid_run()))
        self.assertTrue(mod07.validate_joint_run(_valid_run()))


class TestB04Mod08ScoreWrongType(unittest.TestCase):
    def test_score_on_a_scalar_raises_the_named_failure(self):
        for value in (42, 4.5, True):
            with self.assertRaises(mod08.NamedDetectionFailure):
                mod08.score(value)

    def test_score_still_scores_a_record_and_a_list(self):
        record = {
            "agent_identifier": "agent-b04",
            "day": 1,
            "feature_values": {"feature": 3},
            "records_for_agent_and_day": [],
        }
        single = mod08.score(record)
        self.assertEqual(
            single["verdict_states"][0]["agent_identifier"], "agent-b04")
        listed = mod08.score([record])
        self.assertEqual(
            listed["verdict_states"][0]["agent_identifier"], "agent-b04")


class TestB04DeterminismWrongType(unittest.TestCase):
    def test_non_list_material_raises_the_named_failure(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.compare_verdict_determinism(42)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.compare_verdict_determinism([], 42)

    def test_permuted_material_still_compares_same(self):
        material = [
            {"agent_identifier": "a", "day": 1,
             "feature_values": {"f": 5}, "records_for_agent_and_day": []},
            {"agent_identifier": "b", "day": 1,
             "feature_values": {"f": 50}, "records_for_agent_and_day": []},
        ]
        check = mod08.compare_verdict_determinism(
            material, list(reversed(material)))
        self.assertTrue(check["same"])


class TestB04DependencyValidatorForm(unittest.TestCase):
    def test_malformed_edges_return_false(self):
        base = {"joint_dependent": "MOD-07"}
        self.assertFalse(mod07.validate_dependency_record(
            dict(base, edges=[("MOD-05",)])))
        self.assertFalse(mod07.validate_dependency_record(
            dict(base, edges=[("MOD-05", "MOD-07", "extra")])))
        self.assertFalse(mod07.validate_dependency_record(
            dict(base, edges=["ab"])))
        self.assertFalse(mod07.validate_dependency_record(
            dict(base, edges=[42])))

    def test_the_module_own_record_still_validates(self):
        self.assertTrue(
            mod07.validate_dependency_record(mod07.dependency_record()))


class TestB04SeamEffectReportForm(unittest.TestCase):
    def test_non_record_effect_reads_as_an_empty_effect(self):
        for value in (None, "text", 42):
            report = mod07.seam_effect_report(value)
            self.assertIsNone(report["effect"])
            self.assertEqual(
                report["reporting"], mod07.INTERIM_REPORTING)
            self.assertEqual(
                report["lien_state"], mod07.COMPUTED_NOT_SETTLED)

    def test_a_record_effect_still_reports_its_kind_and_value(self):
        report = mod07.seam_effect_report(
            {"kind": "vouch lien amount", "value": 3})
        self.assertEqual(report["effect"], "vouch lien amount")
        self.assertEqual(report["value"], 3)


if __name__ == "__main__":
    unittest.main()

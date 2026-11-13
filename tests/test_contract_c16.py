"""Contract test for operation C-16, plan section 2 section 5.

The test pins the check field of contract C-16 as plan section 9
states it. Surfaces crossed: MOD-08, via TG-07.5 and TG-14.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-16.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod08 as _m_mod08
    SURFACES["mod08"] = True
except Exception:
    SURFACES["mod08"] = False


class TestContractC16(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-16: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_verdict_determinism_as_records(self):
        """
        Fixture: Shape 11 record set: the same DetectionInput material delivered twice to the Detection Layer
        Pins: the verdict determinism check: the same material returns the same verdict states and, in the two carrying forms, DetectionState per agent per day and the scoring payload by agent and day, the same update records as delivered; the layer changes no reputation, stake or contract state
        Bar: a difference in verdict state on the same inputs is a breach with no tolerated window; no equality claim stands for accumulator values in hash entry or in resume comparison
        Failure: differing verdict states or differing delivered update records on the same material fail this test; while the surface is absent the test fails naming this behaviour and C-16
        """
        self.require("same DetectionInput material returns the same verdict states and the same delivered update records", "mod08")
        import crucible.mod08 as surface
        material = [
            {"agent_identifier": "agent-c16", "day": 1,
             "feature_values": {"activity": 4},
             "records_for_agent_and_day": [{"kind": "daily_record"}]},
            {"agent_identifier": "agent-c16", "day": 2,
             "feature_values": {"activity": 40},
             "records_for_agent_and_day": []},
        ]
        check = surface.compare_verdict_determinism(material)
        self.assertTrue(check["same"])
        first = surface.score_day(material)
        second = surface.score_day(material)
        self.assertEqual(
            first["verdict_states"], second["verdict_states"])
        self.assertEqual(
            first["detection_states"], second["detection_states"])
        self.assertEqual(
            first["accumulator_updates"],
            second["accumulator_updates"])
        society = {"reputation": 7, "stake_held": 3,
                   "contract_state": "open"}
        result = surface.score_day(material, society_state=society)
        self.assertFalse(result["rule_state_changed"])
        self.assertEqual(
            society, {"reputation": 7, "stake_held": 3,
                      "contract_state": "open"})
        self.assertIsNone(check["accumulator_equality_claim"])

    def test_verdict_difference_recorded_as_barred_event(self):
        """
        Fixture: Shape 11 record set: a verdict difference on the same DetectionInput material, recorded while the OP-16 bar stands
        Pins: the difference is recorded as a barred check event: the event bars the run from reporting, and it is recorded as neither a pass score nor a fail score
        Bar: while the verdict rule limb of OP-16 stands unfixed, no score under this contract is reported as a pass or as a fail, and the profile bound label value set stands unnamed; no test invents label values
        Failure: a verdict difference recorded as a pass score or a fail score, or a run reported past a barred check event, fails this test; while the surface is absent the test fails naming this behaviour and C-16
        """
        self.require("verdict difference is recorded as a barred check event, neither a pass score nor a fail score", "mod08")
        import crucible.mod08 as surface
        material_a = [
            {"agent_identifier": "agent-c16", "day": 1,
             "feature_values": {"activity": 4},
             "records_for_agent_and_day": []},
        ]
        material_b = [
            {"agent_identifier": "agent-c16", "day": 1,
             "feature_values": {"activity": 40},
             "records_for_agent_and_day": []},
        ]
        event = surface.record_verdict_difference(
            material_a, material_b)
        self.assertEqual(event["event"], "barred check event")
        self.assertFalse(event["run_reportable"])
        self.assertEqual(
            event["recorded_as"],
            "neither a pass score nor a fail score")
        self.assertIsNone(event["score_verdict"])
        self.assertEqual(
            event["profile_bound_label"],
            surface.PROFILE_LABEL_CARRIAGE)
        same = surface.record_verdict_difference(
            material_a, material_a)
        self.assertIsNone(same["event"])
        self.assertTrue(same["run_reportable"])

    def test_accumulator_list_and_update_rules_gated(self):
        """
        Fixture: no fixture stands for the carried remainder while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: accumulator values follow the decided Candidate B form in full, over the closed list of accumulators and each update rule
        Bar: the closed list of accumulators and each update rule stand carried open on the DQ7-01 record, and no hash completeness claim stands over the detection state; DQ7-01 stands carried open for reliance until the reconciliation act for Plan Amendment (Step 11, reconciliation) stands, and no accumulator behaviour rests on the Candidate B form for reliance in the meantime
        Failure: an accumulator behaviour claim resting on the carried remainder while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-01 record standing complete on its closed list of accumulators and each update rule, with the reconciliation act for Plan Amendment (Step 11, reconciliation) for reliance")


if __name__ == "__main__":
    unittest.main()

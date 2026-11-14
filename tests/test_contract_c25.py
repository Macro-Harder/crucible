"""Contract test for operation C-25, plan section 2 section 5.

The test pins the check field of contract C-25 as plan section 9
states it. Surfaces crossed: MOD-04 and MOD-08, via TG-09.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-25.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod04 as _m_mod04
    SURFACES["mod04"] = True
except Exception:
    SURFACES["mod04"] = False
try:
    import crucible.mod08 as _m_mod08
    SURFACES["mod08"] = True
except Exception:
    SURFACES["mod08"] = False


class TestContractC25(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-25: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_projection_field_closure(self):
        """
        Fixture: F-09, the canary membership leak test
        Pins: projection field closure holds: a DetectionInput record carries only the fields the detection rules consume, agent identifier, day, feature values as the Vigil style rules define them at record level, and the records the rules give the detection layer for that agent and day, and no ground truth field, no honest or farm membership field, and no field derived from membership; the Detection Layer receives no AgentState record, and its module cannot name AgentState at all
        Bar: a field enters the projection only by a change to the shape on the record, and any such change retriggers the canary test before a reportable run may use the changed projection
        Failure: a DetectionInput carrying any barred field, or a detection module able to name AgentState, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-25
        """
        self.require("DetectionInput projection carries only the fields the detection rules consume", "mod04", "mod08")
        import crucible.mod04 as mod04
        import crucible.mod08 as mod08
        import inspect
        state = {"agent_identifier": "agent-c25", "day": 1, "feature_values": {"activity": 2}, "rule_records": [{"kind": "daily_record"}], "membership": mod04.CANARY_VALUE, "ground_truth": mod04.CANARY_VALUE}
        projected = mod04.project_detection_input(state)
        self.assertEqual(list(projected.keys()), ["agent_identifier", "day", "feature_values", "rule_records"])
        source = inspect.getsource(mod08)
        self.assertNotIn("AgentState", source)
        accepted = mod08.accept_detection_input({"agent_identifier": "agent-c25", "day": 1, "feature_values": {"activity": 2}, "records_for_agent_and_day": []})
        self.assertEqual(accepted, {"agent_identifier": "agent-c25", "day": 1, "feature_values": {"activity": 2}, "records_for_agent_and_day": []})
        self.assertEqual(list(accepted.keys()), ["agent_identifier", "day", "feature_values", "records_for_agent_and_day"])

    def test_canary_absence_before_any_reportable_run(self):
        """
        Fixture: F-09 continued, with the canary membership value placed in AgentState
        Pins: the leak test passes before any reportable run and on every projection change only if the canary appears in no DetectionInput record and in no detection output record
        Bar: a run whose projection has not passed this test is not reportable, without exception; the OP-16 bar does not apply to contract C-25 and no score under C-25 stands barred by it
        Failure: a canary appearance in any input or output record, or a reportable run standing on an unpassed projection, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-25
        """
        self.require("canary value appears in no DetectionInput record and no detection output record", "mod04", "mod08")
        import crucible.mod04 as mod04
        import crucible.mod08 as mod08
        self.assertFalse(mod04.exercise_f09_canary())
        self.assertFalse(mod04.canary_appears_in_projection())
        material = [{"agent_identifier": "agent-c25", "day": 1, "feature_values": {"activity": 4}, "records_for_agent_and_day": [{"kind": "daily_record"}]}]
        output = mod08.score_day(material)
        rendered = str(output)
        self.assertNotIn(mod04.CANARY_VALUE, rendered)
        unpassed = {"run_id": "run-c25", "run_class": "screening", "scheduling_order_identifier": "order-1", "form": "run record"}
        self.assertFalse(mod04.run_is_reportable(unpassed))
        passed = dict(unpassed)
        passed["projection_canary_passed"] = True
        passed["reportable"] = True
        self.assertTrue(mod04.run_is_reportable(passed))


if __name__ == "__main__":
    unittest.main()

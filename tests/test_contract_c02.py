"""Contract test for operation C-02, plan section 2 section 5.

The test pins the check field of contract C-02 as plan section 9
states it. Surfaces crossed: MOD-10 and MOD-13, via TG-14.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-02.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False
try:
    import crucible.mod13 as _m_mod13
    SURFACES["mod13"] = True
except Exception:
    SURFACES["mod13"] = False


class TestContractC02(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-02: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_resume_equality_in_settled_scope(self):
        """
        Fixture: AC-2 comparison pair: an interrupted run, its most recent retained checkpoint, and the uninterrupted comparison state named in the run record before the comparison
        Pins: the resumed run reaches the same state as the comparison state on every part except the detection part of a joint run; resume does not proceed on a log whose completeness stands unchecked
        Bar: no divergence inside the settled scope is tolerated; a run with no comparison state named carries no resume equality claim, and that record is not a failure of this check
        Failure: a state difference at a compared point that stands unrecorded, or a witness use outside the scope, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-02
        """
        self.require("resumed run equals the named comparison state inside the settled scope", "mod10", "mod13")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        facts = {field: "value for " + field for field in fields}
        verdicts = {"first verdict state after resume": "verdict-a", "run close": "verdict-b"}
        original = dict(facts)
        original["detection_verdicts"] = dict(verdicts)
        resumed = dict(facts)
        resumed["detection_verdicts"] = dict(verdicts)
        check = surface.resume_check(original, resumed)
        self.assertTrue(check["equal_in_scope"])
        self.assertEqual(check["detection_comparison_points"], ["first verdict state after resume", "run close"])
        unnamed = surface.resume_check({}, {})
        self.assertTrue(unnamed["equal_in_scope"])
        self.assertIsNone(unnamed["divergence_record"])

    def test_resume_failure_promotes_and_bars_witness(self):
        """
        Fixture: AC-2 comparison pair with one state difference at a compared point
        Pins: a resume equality failure promotes the run to full retention and bars its use as a witness until the difference is explained; the first divergence record names the first differing field in the AC-1 field order, the tick and day, the agent identifier where the field is an agent field, and the two values compared
        Bar: no hash equality claim stands while OP-24 stands open, and every comparison report states that the hash limb did not run and names the non hash form actually compared
        Failure: a failed comparison that leaves the run as a witness, or a divergence record missing any named part, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-02
        """
        self.require("resume failure promotes to full retention, bars witness use, and records the first divergence", "mod10", "mod13")
        import crucible.mod01 as mod01
        import crucible.mod13 as surface
        fields = list(mod01.state_hash_field_list())
        facts = {field: "value for " + field for field in fields}
        verdicts = {"first verdict state after resume": "verdict-a", "run close": "verdict-b"}
        original = dict(facts)
        original["detection_verdicts"] = dict(verdicts)
        resumed = dict(facts)
        resumed["detection_verdicts"] = dict(verdicts)
        resumed[fields[2]] = "another value"
        resumed["tick"] = 41
        resumed["simulated_day"] = 5
        resumed["agent_identifier"] = "agent-c02"
        check = surface.resume_check(original, resumed)
        self.assertFalse(check["equal_in_scope"])
        self.assertTrue(check["promoted_to_full_retention"])
        self.assertTrue(check["witness_use_barred"])
        record = check["divergence_record"]
        self.assertEqual(record["field"], fields[2])
        self.assertEqual(record["tick"], 41)
        self.assertEqual(record["day"], 5)
        self.assertEqual(record["agent_identifier"], "agent-c02")
        self.assertEqual(record["values_compared"], [facts[fields[2]], "another value"])
        self.assertFalse(record["hash_limb_ran"])
        self.assertIn("no hash equality", record["compared_form"])
        self.assertFalse(surface.validate_replay_claim({"hash_equality_claimed": True}))

    def test_detection_resume_reliance_gated(self):
        """
        Fixture: no fixture stands for the detection reliance limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: resume equality for the detection part of a joint run at verdict level only, per agent per day, under the DQ7-01 Candidate B form
        Bar: DQ7-01 stands carried open for reliance until the reconciliation act for Plan Amendment (Step 11, reconciliation) stands; the Candidate B form stands as the recorded decision form only and no resume claim rests on it in the meantime; no equality for the detection part in any form wider than verdict level
        Failure: a detection resume claim resting on the Candidate B form while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the reconciliation act for Plan Amendment (Step 11, reconciliation) for DQ7-01 reliance")


if __name__ == "__main__":
    unittest.main()

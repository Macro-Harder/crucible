"""Contract test for operation C-18, plan section 2 section 5.

The test pins the check field of contract C-18 as plan section 9
states it. Surfaces crossed: MOD-05, via TG-04.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-18.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod05 as _m_mod05
    SURFACES["mod05"] = True
except Exception:
    SURFACES["mod05"] = False


class TestContractC18(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-18: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_interface_and_comparison_form_produce_one_score(self):
        """
        Fixture: F-14 and F-15: a fixed set of credits, vouches and penalties scored under the recommended candidate in its comparison form
        Pins: the aggregation interface and its comparison form produce one reputation score for an agent inside the comparison programme; within a family every score traces to the one rule and the one decay mapping the family record names, and a comparison arm stands labelled as one, with its results never merged into the family scores and never reported as the family scores
        Bar: the recommended candidate stands as a comparison form only and not as an adoption; no headline rests on any candidate, and no headline rests on an eigenvector candidate while contested entry C-5 stands
        Failure: a score tracing to no named rule or to two rules, or comparison results merged into family scores, fails this test; while the surface is absent the test fails naming this behaviour and C-18
        """
        self.require("aggregation interface produces one score per agent inside the comparison programme, with arms labelled and unmerged", "mod05")
        import crucible.mod05 as mod05
        interface = mod05.aggregation_interface()
        self.assertFalse(interface["adopted"])
        self.assertIsNone(interface["adopted_rule"])
        self.assertFalse(interface["headline_use_permitted"])
        inputs = {"agent_identifier": "agent-1", "accepted_work": 5, "vouches_received": [{"stake": 3, "score_bearing_flag": True}], "penalties": 1}
        result = mod05.aggregate_reputation(inputs)
        self.assertEqual(result["score"], 7)
        self.assertEqual(result["scores"], [7])
        self.assertEqual(result["form"], "comparison form only")
        self.assertFalse(result["headline_use_permitted"])
        comparison = mod05.compare_aggregation(inputs)
        self.assertEqual(comparison["score"], result["score"])

    def test_ac8_face_statements_on_every_artefact(self):
        """
        Fixture: F-14 and F-15: one decay arm result and one aggregation comparison
        Pins: every decay arm result and aggregation comparison states on its face that neither decay arm tests Candidate 1 as written and that the aggregation comparison is unspecified for Candidate 1 as written, per AC-8, while the decay mapping at NQ-58 stands open
        Bar: a result missing either face statement fails this group even where its numbers are correct
        Failure: an artefact missing either face statement fails this test; while the surface is absent the test fails naming this behaviour and C-18
        """
        self.require("every decay and aggregation artefact carries both AC-8 face statements", "mod05")
        import crucible.mod05 as mod05
        decay = mod05.decay_result()
        for statement in mod05.AC8_FACE_STATEMENTS:
            self.assertIn(statement, decay["face_statements"])
        self.assertEqual(len(decay["face_statements"]), 2)
        inputs = {"agent_identifier": "agent-1", "accepted_work": 1, "vouches_received": [], "penalties": 0}
        comparison = mod05.aggregate_reputation(inputs)
        for statement in mod05.AC8_FACE_STATEMENTS:
            self.assertIn(statement, comparison["face_statements"])

    def test_rule_selection_limb_gated(self):
        """
        Fixture: no fixture stands for the rule selection limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: scores computed under a rule adopted by name and version on a decision record, with its decay mapping
        Bar: the selector stands open at SEL-10 read with register item NQ-64 and open point OP-09; the rule selection itself is the barred limb of this contract, carried at gap G-11, with the working treatment adoption held at DQ7-04; a test that names a rule as the adopted rule, by name and version or in any other wording, fails its group until a decision record adopts a rule by name and version
        Failure: a named adopted rule claimed while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: a decision record adopting an aggregation rule by name and version, settling the selector at SEL-10 and the decay mapping at NQ-58")


if __name__ == "__main__":
    unittest.main()

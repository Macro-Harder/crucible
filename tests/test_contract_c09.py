"""Contract test for operation C-09, plan section 2 section 5.

The test pins the check field of contract C-09 as plan section 9
states it. Surfaces crossed: MOD-10, via TG-10.4.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-09.
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


class TestContractC09(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-09: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_interval_tier_reading_bar(self):
        """
        Fixture: brief section 6.3 gap passage: a closed run in the interval before its later evaluations
        Pins: in the interval, no reader concludes either way: no reader concludes that a run is finally unflagged, that it is not a failure witness, a holding witness or a boundary run, or that the tier it shows at close is its final tier, and no reader concludes the opposite either; conditions 1 and 2 are evaluated once the headline results in the same sweep family are stated, and condition 3 once its replicate group and any neighbouring control points are complete
        Bar: a promotion under any of the three deferred conditions takes effect at that later evaluation and at no other time
        Failure: an interval reading concluding either way, or a promotion taking effect at any other time, fails this test; while the surface is absent the test fails naming this behaviour and C-09
        """
        self.require("in the interval no reader concludes either way on the deferred flag conditions", "mod10")
        import crucible.mod10 as mod10
        self.assertFalse(mod10.validate_retention_report({"source": "interval_records", "tier_claim": "final"}))
        record = mod10.retention_record_for_run("run-c09-interval")
        self.assertIsNone(record["later_evaluation"])
        summary = {"run_id": "run-c09-interval", "retention_tier": "Tier 2"}
        fired = mod10.apply_deferred_evaluation(summary, 1, inputs="condition inputs", outcome="recorded")
        self.assertEqual(fired["deferred_evaluations"][0]["written_into"], "summary record")
        self.assertNotIn("deferred_evaluations", summary)

    def test_report_needing_a_released_form_says_not_retained(self):
        """
        Fixture: brief section 6.3 gap passage: a report needing a form the summary record does not point to as retained for that run
        Pins: the report says the form is not retained for that run; retention is met only by the named record of the later evaluation of conditions 1, 2 and 3, its inputs and its outcome as written into the summary record, and the forms that record points to as retained
        Bar: a retention record that states only that the gap is declared in words does not meet AC-11
        Failure: a report that supplies the form, stays silent, or marks retention met on a declaration alone fails this test; while the surface is absent the test fails naming this behaviour and C-09
        """
        self.require("report needing an unretained form states the form is not retained for that run", "mod10")
        import crucible.mod10 as mod10
        self.assertFalse(mod10.retention_met({"declaration_only": True}))
        self.assertFalse(mod10.retention_met({"state": "DECLARED NOT CLOSED"}))
        record = mod10.retention_record_for_run("run-c09-forms")
        self.assertEqual(record["pointers"]["checkpoints"], 0)
        self.assertEqual(record["pointers"]["event_log_entries"], 0)
        met = {"later_evaluation": {"conditions": [1, 2, 3], "inputs": "recorded", "outcome": "recorded"}, "summary_record_written": True, "retained_forms_pointed_to": ["event_log"]}
        self.assertTrue(mod10.retention_met(met))

    def test_ac11_pass_claim_limb_gated(self):
        """
        Fixture: no fixture stands for the barred limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: an AC-11 pass claim resting on this contract
        Bar: DECLARED NOT CLOSED stands as the non pass state for AC-11 on the sample size item; no retention claim rests on the sample size, the maximum hold duration or the checkpoint cap while any of them stands carried at DQ7-03; the DQ7-08 rule stands as the recorded decided form only, carried open for reliance until the reconciliation act stands
        Failure: an AC-11 pass claim made while the gap stands declared not closed fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-03 carried items standing fixed on the record, with the sample size item closing the late promotion gap")


if __name__ == "__main__":
    unittest.main()

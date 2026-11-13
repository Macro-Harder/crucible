"""Contract test for operation C-08, plan section 2 section 5.

The test pins the check field of contract C-08 as plan section 9
states it. Surfaces crossed: MOD-10, via TG-10.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-08.
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


class TestContractC08(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-08: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_program_only_amendment_and_no_demotion(self):
        """
        Fixture: brief section 11 third near case: a closed run whose flag rule evaluation promotes it after close
        Pins: the flag rule program, and no person, writes promotion, inputs and outcome into the stored summary record itself; the rule may promote any run to Tier 3 and never demotes; readers read the tier and the flag list as they stand at the last evaluation, from the stored record and not from a summary computed on read
        Bar: promotion by a person after close is barred; a reader reads values as at the last evaluation and from nowhere else
        Failure: a post close change carrying a person as its writer, a demotion in any summary record, or a tier read from a computed on read summary fails this test; while the surface is absent the test fails naming this behaviour and C-08
        """
        self.require("only the flag rule program amends a closed summary record, promoting and never demoting", "mod10")
        import crucible.mod10 as mod10
        record = {"run_id": "run-c08", "retention_tier": "Tier 2"}
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(record, outcome="promote", tier="Tier 3", actor="person")
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(record, outcome="demote", tier="Tier 1", actor="program")
        promoted = mod10.apply_flag_evaluation(record, outcome="promote", tier="Tier 3", actor="program", inputs="flag inputs")
        self.assertEqual(promoted["retention_tier"], "Tier 3")
        self.assertEqual(promoted["flag_evaluation"]["actor"], "program")
        mod10.write_summary_record(promoted)
        stored = mod10.summary_record_for_run("run-c08")
        self.assertEqual(stored["retention_tier"], "Tier 3")

    def test_interval_reading_concludes_neither_way(self):
        """
        Fixture: brief section 11 third near case: a report built from interval records, before the last evaluation
        Pins: such a report stands short of any promotion that may follow and says so where it cites a tier; inside the interval no reader concludes that a deferred condition has fired or that it has not
        Bar: the tolerated window is the interval between run close and the last evaluation, bounded by the evaluation points at C-09 and by nothing else
        Failure: an interval report presenting its tier as final, or concluding either way on a deferred condition, fails this test; while the surface is absent the test fails naming this behaviour and C-08
        """
        self.require("interval report states its tier as short of any later promotion", "mod10")
        import crucible.mod10 as mod10
        self.assertFalse(mod10.validate_retention_report({"source": "interval_records", "tier_claim": "final"}))
        record = mod10.retention_record_for_run("run-c08-interval")
        self.assertIsNone(record["later_evaluation"])

    def test_ac11_pass_claim_limb_gated(self):
        """
        Fixture: no fixture stands for the barred limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: an AC-11 pass claim resting on this contract
        Bar: no AC-11 pass claim rests on this contract while the sample size, the maximum hold duration and the checkpoint cap stand carried at DQ7-03; the late promotion gap stands DECLARED NOT CLOSED as a non pass state for AC-11; the DQ7-08 rule stands as the recorded decided form only, carried open for reliance until the reconciliation act stands
        Failure: an AC-11 pass claim made while any carried item stands open fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the DQ7-03 carried items standing fixed on the record: the sample size, the maximum hold duration and the checkpoint numeric cap")


if __name__ == "__main__":
    unittest.main()

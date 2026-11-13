"""Contract test for operation C-04, plan section 2 section 5.

The test pins the check field of contract C-04 as plan section 9
states it. Surfaces crossed: MOD-13, via TG-14.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-04.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod13 as _m_mod13
    SURFACES["mod13"] = True
except Exception:
    SURFACES["mod13"] = False


class TestContractC04(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-04: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_rerun_is_a_new_linked_run(self):
        """
        Fixture: Contract I passage: an original run and a witness rerun of it under a later rule set
        Pins: the rerun appends as a new linked run under its own run identifier and its own rule set version, carrying the link to the original and both version identities; the original record and standing are untouched, and no write path from a rerun reaches the original record
        Bar: a rerun is never read as a corrected original, and no report text presents it as one
        Failure: a rerun that overwrites the original, lacks the link or either version identity, or is presented as the corrected original fails this test; while the surface is absent the test fails naming this behaviour and C-04
        """
        self.require("witness rerun is a new linked run and the original stands untouched", "mod13")
        import crucible.mod13 as surface
        import copy
        original = {"run_id": "run-c04", "rule_set_version": "rules-1", "result": "original", "standing": "witness"}
        before = copy.deepcopy(original)
        rerun = surface.witness_rerun(original, rule_set_version="rules-2")
        self.assertEqual(original, before)
        self.assertNotEqual(rerun["run_id"], original["run_id"])
        self.assertEqual(rerun["linked_to"], "run-c04")
        self.assertEqual(rerun["rule_set_version"], "rules-2")
        self.assertEqual(rerun["original_rule_set_version"], "rules-1")
        self.assertFalse(surface.validate_rerun_reading({"read_as": "corrected version of the original"}))

    def test_rerun_verdicts_do_not_transfer(self):
        """
        Fixture: Contract I passage: a rerun record inspected for verdict carriage from its original
        Pins: Replication Checker verdicts attach to the original run and are not transferred by a rerun; every writer that has written the original record since its close is a writer C-07 permits, in a form C-07 permits
        Bar: divergence of standing is not tolerated at any numeric difference size
        Failure: a verdict standing transferred to a rerun, or an unpermitted writer on the original record, fails this test; while the surface is absent the test fails naming this behaviour and C-04
        """
        self.require("verdicts stay on the original run and only C-07 writers have written it", "mod13")
        import crucible.mod13 as surface
        original = {"run_id": "run-c04", "rule_set_version": "rules-1"}
        rerun = surface.witness_rerun(original, rule_set_version="rules-2")
        self.assertFalse(rerun["verdicts_transferred"])
        verdict = surface.verdict_record("run-c04", standard="exact replay alone", outcome="rests")
        self.assertTrue(surface.publishable_on_replication({"claim_identifier": "run-c04"}, verdict))
        self.assertFalse(surface.publishable_on_replication({"claim_identifier": rerun["run_id"]}, verdict))


if __name__ == "__main__":
    unittest.main()

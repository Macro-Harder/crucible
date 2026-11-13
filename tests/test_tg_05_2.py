"""Test group TG-05.2, slice S-05, MOD-06 Escrow Core.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
Relation to the DQ7-04 exercise test paper: the paper at
design/steps/step-13-dq7-04-exercise-test-paper.md stands as a paper
with its own 20 exercise tests ET-01 to ET-20. The tests in this file
are the group tests of TG-05.2, written from the plan mapping. They
do not duplicate the exercise tests and are not the paper coverage.
"""
import unittest

try:
    from crucible import mod06 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG052(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-05.2: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_allowed_subpaths_run_as_written(self):
        """
        Fixture: F-21, the exercised escrow instruction cases
        Pins: replace_backup_key, deposit and withdraw_unliened run for DQ-5 with backup key registration at setup, with the pool subpaths excluded and the backup extended profile excluded; open_request runs for DQ-10 with a lien sized from the self declared estimated cost consumed in that form, with no countersigning, bound or verification added, and that value carried as a labelled assumption in accuracy form, stated cost divided by true cost, with its sensitivity range as the fixture states it; check_in and claim_lost_contact run for DQ-17 for each contract that turns the clause on, with the window value N set in the standard for that contract and contact clocks tracked
        Bar: no test encodes a guess at any DQ-5 to DQ-30 item in any of these cases, and contested entries C-9 and C-11 travel beside the DQ-17 and DQ-5 paths in every fixture that touches them
        Failure: a case that adds a countersigning, bound or verification, that drops a contested entry standing, or that runs an excluded subpath fails this test; while the surface is absent the test fails naming this behaviour and TG-05.2
        """
        self.require_surface("allowed subpaths of fixture F-21 run as written with C-9 and C-11 carried")
        backup = _mod.run_instruction(
            "replace_backup_key", context={"backup_key_registered_at_setup": True})
        self.assertIn("C-11", backup["payload"]["contested_entries"])
        self.assertFalse(backup["payload"]["claims_dq_answer"])
        for name in ("deposit", "withdraw_unliened"):
            run = _mod.run_instruction(name)
            self.assertIn("C-11", run["payload"]["contested_entries"])
        opened = _mod.run_instruction(
            "open_request", context={"stated_cost": 50, "true_cost": 100})
        self.assertEqual(opened["payload"]["lien_size"], 50)
        self.assertEqual(opened["payload"]["lien_sized_from"], "self declared estimated cost")
        self.assertEqual(opened["payload"]["additions"], [])
        self.assertEqual(opened["payload"]["estimated_cost"]["accuracy"], 0.5)
        self.assertIn("labelled assumption", opened["payload"]["estimated_cost"]["form"])
        self.assertTrue(opened["payload"]["estimated_cost"]["sensitivity_range"])
        for name in ("check_in", "claim_lost_contact"):
            run = _mod.run_instruction(name, context={
                "clause_on": True,
                "window_n": "window N as set in the standard for that contract"})
            self.assertIn("C-9", run["payload"]["contested_entries"])
            self.assertTrue(run["payload"]["contact_clocks_tracked"])

    def test_excluded_subpaths_and_guesses_fail(self):
        """
        Fixture: F-21, the exercised escrow instruction cases, excluded subpaths limb
        Pins: no pool subpath runs and the backup extended profile runs in no working run, and no case encodes a floor under N, a clock scope, or a DQ-5 scope reading as a DQ answer
        Bar: a construction excluded on a DQ ground stays excluded on that ground, and co occurrence by itself is not recorded as traversal of backup resolution for a deposit or a withdrawal
        Failure: a run taking a pool subpath, running the backup extended profile, or encoding a guessed DQ answer fails this test; while the surface is absent the test fails naming this behaviour and TG-05.2
        """
        self.require_surface("excluded subpaths and guessed DQ answers are refused")
        self.require_surface("excluded subpaths and guessed DQ answers are refused")
        with self.assertRaises(_mod.ExcludedSubpath):
            _mod.run_instruction("pool_init")
        with self.assertRaises(_mod.ExcludedSubpath):
            _mod.run_instruction("deposit", context={"profile": "backup extended profile"})
        with self.assertRaises(_mod.GuessedAnswer):
            _mod.run_instruction("deposit", context={"claims_dq_answer": True})
        with self.assertRaises(_mod.GuessedAnswer):
            _mod.run_instruction("check_in", context={
                "clause_on": True, "window_n": "stated",
                "asserts_clock_scope_as_answer": True})
        occurrence = _mod.run_instruction(
            "replace_backup_key", context={"backup_key_registered_at_setup": True})
        self.assertIsNone(occurrence["payload"]["traversal_claim"])
        self.assertIn("pool subpaths", _mod.excluded_subpaths())
        self.assertIn("backup extended profile", _mod.excluded_subpaths())

    def test_pause_cap_in_force_for_ruled_core(self):
        """
        Fixture: F-25, the pause cap case
        Pins: in ruled core runs the pause cap in force is an extension up to 300 percent, a total of 400 percent, under ruling DQ-3, stated in every pause related result as one of the four per variant fields
        Bar: a pause related result stating no per variant pause value fails validation
        Failure: a pause result with a cap other than the DQ-3 ruled value for a ruled core run, or with no per variant field, fails this test; while the surface is absent the test fails naming this behaviour and TG-05.2
        """
        self.require_surface("pause cap in force is extension 300 percent, total 400 percent, under DQ-3")
        cap = _mod.pause_cap("B-4")
        self.assertEqual(cap["extension_percent"], 300)
        self.assertEqual(cap["total_percent"], 400)
        self.assertEqual(cap["per_variant_pause_value"]["ruling"], "DQ-3")
        result = _mod.escrow_result(
            "pause", payload={"per_variant_pause_value": cap["per_variant_pause_value"]})
        self.assertTrue(_mod.validate_pause_result(result))
        self.assertFalse(_mod.validate_pause_result(_mod.escrow_result("pause")))

    def test_b3_pause_ambiguity_never_resolved_by_test(self):
        """
        Fixture: F-25, the pause cap case, at the B-3 variant limb
        Pins: B-3 results state the value in force for the variant in the same per variant field form as ruled core results
        Bar: the B-3 text ambiguity, total or extension, unstated in that variant text, is never resolved by a test choosing a reading for B-3
        Failure: a test or result that resolves the B-3 ambiguity by choosing a reading fails this test; while the surface is absent the test fails naming this behaviour and TG-05.2
        """
        self.require_surface("B-3 pause value is stated per variant with no reading chosen for its ambiguity")
        cap = _mod.pause_cap("B-3", stated_value="the value in force for B-3 as stated in its run record")
        self.assertEqual(
            cap["per_variant_pause_value"],
            "the value in force for B-3 as stated in its run record")
        self.assertIsNone(cap["reading_chosen"])
        self.assertIn("unstated", cap["ambiguity"])


if __name__ == "__main__":
    unittest.main()

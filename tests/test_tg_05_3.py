"""Test group TG-05.3, slice S-05, MOD-06 Escrow Core.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
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


class TestTG053(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-05.3: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_recommended_profiles_run_as_sweep_set(self):
        """
        Fixture: F-24, the named profile constructions
        Pins: Profile 1, the B-3 core only with all toggles off, and Profile 2, the B-4 ruled core only with all toggles off, run as the recommended sweep set, carried as a recommendation and not a ruling at register question NQ-50; the core with split on construction stays distinct from both the recommended set and the excluded set
        Bar: the recommended set is a recommendation and not a ruling, and no test presents it as ruled
        Failure: a run that merges the split on construction into either set, or that presents the set as ruled, fails this test; while the surface is absent the test fails naming this behaviour and TG-05.3
        """
        self.require_surface("Profile 1 and Profile 2 run as the recommended sweep set, distinct from the split on construction")
        sweep = _mod.recommended_sweep_set()
        self.assertEqual([entry["name"] for entry in sweep], ["Profile 1", "Profile 2"])
        self.assertIn("B-3", sweep[0]["construction"])
        self.assertIn("B-4", sweep[1]["construction"])
        for entry in sweep:
            self.assertEqual(entry["standing"], "recommendation, not a ruling")
            self.assertTrue(_mod.validate_sweep_membership(entry["name"]))
        split = _mod.split_on_construction()
        self.assertFalse(split["in_recommended_set"])
        self.assertFalse(split["in_excluded_set"])
        self.assertFalse(_mod.validate_sweep_membership(split["name"]))

    def test_excluded_construction_never_runs_as_sweep_member(self):
        """
        Fixture: F-24, the named profile constructions, excluded set limb
        Pins: a construction excluded on a DQ ground stays excluded on that ground, with grounds kept apart: 18 entries on a DQ ground, 1 on a ruling ground, 2 on a scope or coverage ground
        Bar: a test that runs an excluded construction as a sweep member fails this group
        Failure: an excluded construction run as a sweep member, or grounds merged across the three kinds, fails this test; while the surface is absent the test fails naming this behaviour and TG-05.3
        """
        self.require_surface("excluded constructions stay excluded with their grounds kept apart")
        excluded = _mod.excluded_constructions()
        self.assertEqual(excluded["grounds"], {
            "DQ ground": 18, "ruling ground": 1, "scope or coverage ground": 2})
        self.assertEqual(excluded["total"], 21)
        self.assertFalse(_mod.validate_sweep_membership("an excluded construction"))


if __name__ == "__main__":
    unittest.main()

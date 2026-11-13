"""Test group TG-16.5. Longer horizons and mixed patience at selected points.
Slice S-16, integration, fixtures, and the validation run class. The suite
convention surface named here is crucible.mod11. Suite form: design/steps/step-13-opening-record.md section 4.
While that surface does not stand, every non gated test in this file fails by name,
stating the pinned behaviour and its group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG165(unittest.TestCase):
    def test_horizon_picks_stay_at_selected_points(self):
        """
        Fixture: The two longer horizons applied at selected witness and decay points only, with run cost stated in the days multiplied form and labelled estimated.
        Pins: No horizon value is settled for any other point by that pick, and the baseline horizon discipline of fixture F-18 stands untouched elsewhere.
        Bar: A horizon value generalised from a selected point to the grid fails this group and the provisional grid guard at TG-12.3 with it.
        Failure: Fails while the integrated surface stands absent, naming TG-16.5 and this behaviour; a horizon value generalised to the grid fails this test when the surface stands.
        """
        require_surface(self, "TG-16.5", "longer horizons at selected witness and decay points only, no horizon value settled for any other point, run cost in days multiplied form labelled estimated")
        import crucible.mod16 as surface
        selected = ("witness point 1", "decay point 1")
        self.assertTrue(surface.horizon_application("witness point 1", selected))
        self.assertFalse(surface.horizon_application("grid point 9", selected))
        cost = surface.horizon_run_cost(60, 30)
        self.assertEqual(cost["form"], "days multiplied")
        self.assertEqual(cost["labelled"], "estimated")
        self.assertFalse(surface.validate_horizon_generalisation({"generalised_to_grid": True}))
        self.assertTrue(surface.validate_horizon_generalisation({"generalised_to_grid": False}))

    def test_mixed_patience_labelled_assumptions(self):
        """
        Fixture: Mixed patience distributions at selected control points, their distribution shapes standing as labelled assumptions in the family record before runs, with the falsifier stated against the single value plane.
        Pins: The distributions enter only in that labelled form, in the family record before runs, with the falsifier stated.
        Bar: A mixed distribution run whose shape stands in no family record fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.5 and this behaviour; a mixed patience run with no family record shape fails this test when the surface stands.
        """
        require_surface(self, "TG-16.5", "mixed patience distributions enter only as labelled assumptions in the family record before runs, with the falsifier stated")
        import crucible.mod16 as surface
        labelled = {"distribution_shape": "two point mixture", "labelled_assumption_in_family_record": True, "recorded_before_runs": True, "falsifier_stated": True}
        self.assertTrue(surface.validate_mixed_patience(labelled))
        unlabelled = {"distribution_shape": "two point mixture"}
        self.assertFalse(surface.validate_mixed_patience(unlabelled))
        self.assertTrue(surface.validate_mixed_patience({"distribution_shape": None}))


if __name__ == "__main__":
    unittest.main()

"""Test group TG-16.3. Validation run class end to end.
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


class TestTG163(unittest.TestCase):
    def test_screening_and_validation_exercised_end_to_end(self):
        """
        Fixture: Pilot confined and validation material only, driven through the wired product in the screening and validation run classes.
        Pins: The screening and validation run classes stand exercised end to end in this group, run class stands as a required field on every run, and no confirmation result can be produced by a run whose record shows the screening domain, in the condition the slices paper states for the combined confirmation and headline reporting slice.
        Bar: An integration result that would need a bar lifted is reported as bounded, in the bound form the live proof plan section states, and never as a pass over the bar.
        Failure: Fails while the integrated surface stands absent, naming TG-16.3 and this behaviour; a run with no run class field, or a confirmation result produced from the screening domain, fails this test when the surface stands.
        """
        require_surface(self, "TG-16.3", "screening and validation run classes exercised end to end on pilot confined and validation material only, run class a required field on every run")
        import crucible.mod16 as surface
        for run_class in ("screening", "validation"):
            result = surface.exercise_run_class(run_class)
            self.assertTrue(result["exercised_end_to_end"])
            self.assertTrue(result["run_class_required_field_present"])
            self.assertEqual(result["record"]["run_class"], run_class)
            self.assertIn("validation", result["material"])
            self.assertFalse(result["headline_claim"])

    def test_confirmation_and_headline_carried_unexercised_here(self):
        """
        Fixture: Pilot confined and validation material only, as in the companion entry of this group.
        Pins: The confirmation and headline run classes stand pinned as wired behaviour at TG-12.2, run class separation, and stand carried as unexercised end to end in this group; no sentence in this group claims an end to end exercise for either class. The confirmation and headline run classes stand exercised end to end in companion group TG-16.3b, on validation material only, before Step 17 closes, and no result of that group is a headline claim, as Amendment G2-C41 states.
        Bar: A sentence in this group claiming an end to end exercise of the confirmation or headline class fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.3 and this behaviour; a claim of end to end exercise for either class resting on this group fails this test in every state.
        """
        require_surface(self, "TG-16.3", "confirmation and headline run classes carried as unexercised end to end in TG-16.3, their exercise standing in companion group TG-16.3b only")
        import crucible.mod16 as surface
        for run_class in ("confirmation", "headline"):
            result = surface.exercise_run_class(run_class)
            self.assertFalse(result["exercised_end_to_end"])
            self.assertTrue(result["carried_unexercised_here"])
            self.assertIn("TG-16.3b", result["exercise_stands_in"])


if __name__ == "__main__":
    unittest.main()

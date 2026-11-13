"""Test group TG-16.3b. Companion group: confirmation and headline run classes end to end.
Slice S-16, integration, fixtures, and the validation run class. The suite
convention surface named here is crucible.mod11. Suite form: design/steps/step-13-opening-record.md section 4.
While that surface does not stand, every non gated test in this file fails by name,
stating the pinned behaviour and its group, as plan section 2 rules 1 and 2 state.
This group rests on its material basis only, pilot confined and validation
material only, and on no inventory fixture, as its mapping entry states.
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


class TestTG163b(unittest.TestCase):
    def test_confirmation_and_headline_exercised_end_to_end(self):
        """
        Fixture: No fixture F-01 to F-27 is assigned to this group. Its material basis stands in place of an inventory fixture: pilot confined and validation material only, driven through the wired product, in the form the fixture assignment table states for this group.
        Pins: This group exercises one confirmation run and one headline run end to end on validation material before Step 17 closes, with run class as a required field on each run, the settings lineage record of Form 32 completed for the confirmation run, and the headline run ending in a HeadlineResultUnit built under Contract H from retained records only, each result recorded as validation material and as no headline claim, as Amendment G2-C41 states.
        Bar: A Step 18 proof script may not list Route 1 as ready until the record of this group stands, as Amendment G2-C41 states, and no result of this group is a headline claim.
        Failure: Fails while the integrated surface stands absent, naming TG-16.3b and this behaviour; an exercise resting on any inventory fixture, or on material other than pilot confined and validation material, fails this test when the surface stands.
        """
        require_surface(self, "TG-16.3b", "one confirmation run and one headline run exercised end to end on validation material only, on the material basis of this group and on no inventory fixture")
        import crucible.mod11 as mod11
        import crucible.mod16 as surface
        result = surface.exercise_confirmation_and_headline()
        confirmation = result["confirmation"]
        self.assertEqual(confirmation["run_class"], "confirmation")
        self.assertEqual(confirmation["material"], "validation")
        self.assertEqual(confirmation["settings_lineage_record"], "Form 32 completed")
        self.assertFalse(confirmation["headline_claim"])
        headline = result["headline"]
        self.assertEqual(headline["run_class"], "headline")
        self.assertTrue(headline["unit_built"])
        self.assertTrue(mod11.validate_headline_unit(headline["unit"]))
        self.assertFalse(headline["headline_claim"])

    def test_confirmation_result_from_screening_domain_fails(self):
        """
        Fixture: The material basis of this group only: pilot confined and validation material, with a run whose record shows the screening domain offered for a confirmation result.
        Pins: No confirmation result can be produced by a run whose record shows the screening domain, in the condition TG-16.3 states for the combined confirmation and headline reporting slice.
        Bar: A confirmation result produced from the screening domain fails this group, in the failure form the mapping states for this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.3b and this behaviour; a confirmation result produced from the screening domain fails this test when the surface stands.
        """
        require_surface(self, "TG-16.3b", "no confirmation result produced by a run whose record shows the screening domain")
        import crucible.mod16 as surface
        self.assertFalse(surface.validate_confirmation_result({"run_class": "confirmation", "seed_domain": "screening"}))
        self.assertFalse(surface.validate_confirmation_result({"run_class": "confirmation", "domain": "screening"}))
        self.assertTrue(surface.validate_confirmation_result({"run_class": "confirmation", "seed_domain": "held out confirmation"}))

    def test_headline_claim_from_this_group_fails(self):
        """
        Fixture: The material basis of this group only: pilot confined and validation material, with a result of this group offered as a headline claim.
        Pins: Each result of this group is recorded as validation material and as no headline claim, as Amendment G2-C41 states, and the headline run in this group exercises the unit building form only.
        Bar: A headline claim drawn from a result of this group fails this group, in the failure form the mapping states for this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.3b and this behaviour; a headline claim drawn from a result of this group fails this test in every state.
        """
        require_surface(self, "TG-16.3b", "no headline claim drawn from any result of TG-16.3b, each result recorded as validation material only")
        import crucible.mod16 as surface
        result = surface.exercise_confirmation_and_headline()
        for part in result.values():
            self.assertFalse(part["headline_claim"])
            self.assertEqual(part["material"], "validation")
        self.assertFalse(surface.validate_headline_claim({"headline_claim": True, "material": "validation"}))


if __name__ == "__main__":
    unittest.main()

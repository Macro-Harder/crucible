"""Test group TG-15.2. Pilot confinement.
Slice S-15, Shell, MOD-14. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod14, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod14 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod14 absent, pinned behaviour unmet: " + behaviour)


class TestTG152(unittest.TestCase):
    def test_three_uses_only_allowed(self):
        """
        Fixture: The purpose built run driven through the pilot runner for timing, for conformance, and for procedure rates.
        Pins: The purpose built run stands confined to timing, conformance, and procedure rates, per decision D-07 and brief section 6.2 seventh, and every pilot output carries its confinement label in the same artefact as the number.
        Bar: A pilot output carrying no confinement label in the same artefact as its number fails this group.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.2 and this behaviour; a pilot output for an allowed use with no confinement label beside its number fails this test when the surface stands.
        """
        require_surface(self, "TG-15.2", "pilot confined to timing, conformance, and procedure rates, every pilot output carrying its confinement label in the same artefact")
        import crucible.mod14 as surface
        for use in ("timing", "conformance", "procedure rates"):
            output = surface.pilot_run(use, {"figure": 7})
            self.assertEqual(output["confinement_label"], "pilot confined")
            self.assertEqual(output["figure"], 7)
            self.assertEqual(output["use"], use)
        with self.assertRaises(surface.NamedShellFailure):
            surface.pilot_run("behaviour fitting", {"figure": 7})

    def test_behaviour_fitting_barred(self):
        """
        Fixture: The purpose built run attempted for behaviour fitting through the pilot runner.
        Pins: The purpose built run is never used for behaviour fitting, per decision D-07, and events per agent per day and trust graph average degree are not settled as population behaviour rates by the pilot in any wording.
        Bar: A behaviour claim citing a pilot output fails this group wherever the citation appears.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.2 and this behaviour; a behaviour claim citing a pilot output fails this test when the surface stands, wherever the citation appears.
        """
        require_surface(self, "TG-15.2", "pilot never used for behaviour fitting, no pilot output settling a population behaviour rate in any wording")
        import crucible.mod14 as surface
        self.assertFalse(surface.validate_pilot_claim({"kind": "behaviour", "cites_pilot_output": True}))
        self.assertFalse(surface.validate_pilot_claim({"settles_population_behaviour_rate": True}))
        self.assertFalse(surface.validate_pilot_claim({"settles_population_behaviour_rate": True, "rate": "events per agent per day"}))
        self.assertTrue(surface.validate_pilot_claim({"kind": "timing", "cites_pilot_output": True}))


if __name__ == "__main__":
    unittest.main()

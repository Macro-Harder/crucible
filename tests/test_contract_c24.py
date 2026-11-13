"""Contract test for operation C-24, plan section 2 section 5.

The test pins the check field of contract C-24 as plan section 9
states it. Surfaces crossed: MOD-04 and MOD-10, via TG-11.1 and TG-11.2.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-24.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod04 as _m_mod04
    SURFACES["mod04"] = True
except Exception:
    SURFACES["mod04"] = False
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC24(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-24: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_singular_presentation_bar_and_divergence_carriage(self):
        """
        Fixture: a run with gossip delay in force, scored over all viewers of the run, with the per viewer components and the divergence companion the run records, as TG-11.2 states; gossip and delivery delay carried at 0 to 7 days as a scenario choice and a labelled assumption
        Pins: divergence is reported as a spread, never as one vector: the components stand computed per viewer with the viewer identifier on every component and the divergence companion beside the form; two viewers may hold different reputation values, different graph snapshots and different record sets for the same day, and each holding is correct for its viewer; the C-15 and C-19 report checks fail any cross run comparison or viewer free reading that breaches the singular presentation bar
        Bar: decided bars only, as at TG-11.2: no per viewer quantity stands presented as one singular quantity; boundaries one and two of brief section 7 stand described as record enforced for agent held views only, and for no wider class
        Failure: a singular vector reported, a cross run comparison on the components as one quantity, or a record enforced description used for any wider class fails this test; while a crossed surface is absent the test fails naming this behaviour and C-24
        """
        self.require("per viewer divergence is reported as a spread and never as one singular quantity", "mod04", "mod10")
        import crucible.mod04 as mod04
        import crucible.mod05 as mod05
        import crucible.mod10 as mod10
        components = mod04.per_viewer_components(run_id="run-c24", viewers=("viewer-1", "viewer-2"))
        self.assertTrue(all("viewer_id" in item for item in components))
        companion = mod04.divergence_companion(run_id="run-c24", components=components)
        self.assertIn("daily_aggregates", companion)
        self.assertIn("end_of_run", companion)
        self.assertFalse(mod10.validate_view_carriage({"form": "singular_vector", "presented_as": "one comparable quantity"}))
        self.assertTrue(mod05.validate_view_wording({"description": "record enforced", "scope": "agent held views"}))
        self.assertFalse(mod05.validate_view_wording({"description": "record enforced", "scope": "all views"}))

    def test_view_construction_and_leak_check_gated_on_pg02(self):
        """
        Fixture: none assigned. No inventory fixture stands assigned to the TG-11.1 limb under PG-02, and Step 13 is barred from authoring its tests from the prose scenario at TG-11.1 as if it were an inventory fixture, as Amendment M-02 states. Recorded state: gated, never passed
        Pins: when the gate opens: the ViewRecord constructed by MOD-04 in its decided field groups, delivered under Contract K, held at the hold point while the Recorder runs the field validation form and the timing form of the three form leak check, and released only on a pass of both forms, before the agent next act inside the same simulated day; the canary form of the three form leak check stands in its own timing form, before any reportable run and whenever the view projection changes; each agent acts only on the records its own per viewer view contains, and view contents are never read across viewers
        Bar: OB-26 stands carried open in its own terms, in two limbs only: Tier 1 views are not recheckable after the run, and the type of the scheduling position identifier stands unstated; the view count stands open at NQ-52 and every cost or storage claim for this channel carries that standing; the three form leak check is not a post run recheck of Tier 1 views, and the C-25 leak test covers the DetectionInput channel only and is not this check
        Failure: a leak check result or a ViewRecord field claim made from this limb while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: a fixture assignment standing on a plan level record or a decision record, under PG-02, as Amendment M-02 states; no owner stands named and no due step stands named")


if __name__ == "__main__":
    unittest.main()

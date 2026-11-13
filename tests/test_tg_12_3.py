"""Test group TG-12.3. Grids, replicates, and screening surfaces.

Slice S-12, MOD-12 Sweep Controller. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod12, and
records whether the surface stands. While the surface stands absent, each non
gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
"""
import unittest

try:
    from crucible import mod12
    SURFACE = mod12
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-12.3"
F17_FARM_SHARES = (50, 60, 70)


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod12 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod12 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestProvisionalGridMarking(unittest.TestCase):
    def test_provisional_grid_marking(self):
        """Fixture: any grid, density, or run count artefact produced before the NQ-4 timing pilot lands, as TG-12.3 states.
        Pins: every such artefact is marked provisional, per AC-7.
        Bar: no grid point is presented as affordable before the pilot lands.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, an unmarked artefact from before the pilot fails.
        """
        require_surface(self, "grid artefacts before the timing pilot marked provisional", "grid_artefacts")
        artefacts = SURFACE.grid_artefacts(produced_before_pilot=True)
        self.assertTrue(artefacts)
        for artefact in artefacts:
            self.assertEqual(artefact["standing"], "provisional")

    def test_affordability_before_pilot_fails(self):
        """Fixture: a suite asserting a grid point affordable before the NQ-4 timing pilot lands, as TG-12.3 states.
        Pins: the assertion fails validation.
        Bar: no grid point is presented as affordable before the pilot lands, and a suite asserting affordability earlier fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, acceptance of the assertion fails.
        """
        require_surface(self, "affordability asserted before the pilot rejected", "validate_grid_claim")
        claim = {"kind": "grid_point", "claim": "affordable", "pilot_landed": False}
        self.assertFalse(SURFACE.validate_grid_claim(claim))

    def test_grid_refixed_after_pilot_gated(self):
        """Fixture: the grid for a family after the NQ-4 timing pilot record lands.
        Pins: no behaviour; this test records its state as gated on the NQ-4 timing pilot record standing, the record waited on at plan section 2 section 10 line 9. When the gate opens the behaviour pinned is: after the pilot lands the grid is re fixed on the measured figure and its derivation before any sweep runs, in the form Amendment S12-017 states.
        Bar: no sweep run starts in the family before that re fixing stands.
        Failure: gated form only; this test never passes while the pilot record stands unlanded.
        """
        self.skipTest("gated on the NQ-4 timing pilot record standing")


class TestReplicateAndReadoutDiscipline(unittest.TestCase):
    def test_replicate_and_readout_discipline(self):
        """Fixture: F-18 with fixtures F-14 and F-17 beside it, as TG-12.3 states.
        Pins: shares are evaluated at the end of each simulated day; the attacker winning regime requires the attacker share above the honest share at every daily evaluation over the final 30 simulated days; screening points at F-17, farm shares of 50 percent, 60 percent, and 70 percent, are reported on the D-05 traces and on the honest loss rate and not on the win count, in their weighed and not adopted standing.
        Bar: F-17 points are a weighing, not adopted scope, and the 70 percent figure source use is evidence for nothing in Crucible.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, a winning regime read on fewer than the final 30 daily evaluations, or an F-17 point reported on the win count, fails.
        """
        require_surface(self, "replicate and readout discipline over the final 30 simulated days", "screening_readout")
        readout = SURFACE.screening_readout(fixture="F-17")
        self.assertEqual(tuple(readout["farm_shares_percent"]), F17_FARM_SHARES)
        self.assertEqual(readout["reported_on"], ["D-05 traces", "honest loss rate"])
        self.assertNotIn("win count", readout["reported_on"])
        self.assertEqual(readout["standing"], "weighed, not adopted")
        regime = SURFACE.winning_regime(daily_shares=[(0.6, 0.4)] * 30)
        self.assertTrue(regime)
        short = SURFACE.winning_regime(daily_shares=[(0.6, 0.4)] * 29)
        self.assertFalse(short)

    def test_f17_point_as_adopted_scope_fails(self):
        """Fixture: a test or report presenting an F-17 point as adopted scope, as TG-12.3 states.
        Pins: the presentation fails validation.
        Bar: a test presenting any F-17 point as adopted scope fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, acceptance of the presentation fails.
        """
        require_surface(self, "F-17 point presented as adopted scope rejected", "validate_screening_claim")
        claim = {"fixture": "F-17", "farm_share_percent": 50, "standing": "adopted scope"}
        self.assertFalse(SURFACE.validate_screening_claim(claim))

    def test_top_up_rule_recorded_in_run_record(self):
        """Fixture: F-18, the canonical scale and readout set, at its top up rule, as slice S-12 states for that fixture.
        Pins: the top up rule stands as at least 30 replicates at a control point found in screening with a winning probability above 0.1 and below 0.9, recorded in the run record.
        Bar: a control point at or outside those bounds takes no top up under this rule.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, a top up below 30 replicates, or at a point outside the stated bounds, fails.
        """
        require_surface(self, "top up rule to at least 30 replicates inside the stated bounds", "top_up_applies")
        self.assertTrue(SURFACE.top_up_applies(winning_probability=0.5, replicates_after_top_up=30))
        self.assertFalse(SURFACE.top_up_applies(winning_probability=0.1, replicates_after_top_up=30))
        self.assertFalse(SURFACE.top_up_applies(winning_probability=0.9, replicates_after_top_up=30))
        self.assertFalse(SURFACE.top_up_applies(winning_probability=0.5, replicates_after_top_up=29))


class TestDecayArmCompanionTable(unittest.TestCase):
    def test_decay_arm_companion_table(self):
        """Fixture: F-14, the decay slice set, at the planes the decay arm reports, as Amendment TG4-59 states at slice S-12 outputs.
        Pins: every plane the decay arm reports carries a companion table in the same readout, one row per slice, stating the slice half life, the control point values, and the result values in numbers; the table, not the plane, is the checkable form of the arm result.
        Bar: a plane reported with no companion table in the same readout fails this test.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, a readout plane with no companion table fails.
        """
        require_surface(self, "decay arm companion table in the same readout, one row per slice", "decay_arm_readout")
        readout = SURFACE.decay_arm_readout(fixture="F-14")
        for plane in readout["planes"]:
            self.assertIn("companion_table", plane)
            for row in plane["companion_table"]:
                self.assertIn("half_life", row)
                self.assertIn("control_point_values", row)
                self.assertIn("result_values", row)

    def test_plane_without_companion_table_fails(self):
        """Fixture: a decay arm readout plane carrying no companion table, as Amendment TG4-59 states.
        Pins: the readout fails validation.
        Bar: the table, not the plane, is the checkable form of the arm result, so a plane alone supports no check.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.3; with the surface present, acceptance of the readout fails.
        """
        require_surface(self, "decay arm plane with no companion table rejected", "validate_decay_readout")
        readout = {"planes": [{"name": "plane", "companion_table": None}]}
        self.assertFalse(SURFACE.validate_decay_readout(readout))


if __name__ == "__main__":
    unittest.main()

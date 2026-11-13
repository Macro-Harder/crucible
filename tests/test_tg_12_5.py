"""Test group TG-12.5. Counting illustrations are not costs.

Slice S-12, MOD-12 Sweep Controller. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod12, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
"""
import unittest

try:
    from crucible import mod12
    SURFACE = mod12
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-12.5"
SALTELLI_DISTINCT_EVALUATIONS = 14336
SALTELLI_INPUTS = 12
SALTELLI_BASE_SAMPLE = 1024


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


class TestSaltelliFiguresStayIllustrations(unittest.TestCase):
    def test_saltelli_figures_stay_illustrations(self):
        """Fixture: F-20, the Saltelli counting illustrations, 14,336 distinct evaluations at 12 inputs and a base sample of 1,024 without second order indices, with fixture F-19 beside it, as TG-12.5 states.
        Pins: the figures illustrate the counting method and price nothing; seed replicates sit outside any sampled base design, and held out confirmation seeds form a separate seed family.
        Bar: a cost claim resting on an F-20 figure fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.5; with the surface present, a counting record pricing anything from the illustration figures fails.
        """
        require_surface(self, "Saltelli figures illustrate the counting method and price nothing", "counting_basis")
        basis = SURFACE.counting_basis(fixture="F-20")
        self.assertEqual(basis["distinct_evaluations"], SALTELLI_DISTINCT_EVALUATIONS)
        self.assertEqual(basis["inputs"], SALTELLI_INPUTS)
        self.assertEqual(basis["base_sample"], SALTELLI_BASE_SAMPLE)
        self.assertEqual(basis["standing"], "illustration")
        self.assertFalse(basis["prices_anything"])

    def test_cost_claim_on_saltelli_figure_fails(self):
        """Fixture: a cost claim, a run count commitment, and an affordability statement, each resting on an F-20 figure, as TG-12.5 states.
        Pins: all three fail validation.
        Bar: a cost claim, a run count commitment, or an affordability statement resting on an F-20 figure fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.5; with the surface present, acceptance of any of the three fails.
        """
        require_surface(self, "cost claim resting on a Saltelli figure rejected", "validate_cost_claim")
        for kind in ("cost", "run count commitment", "affordability"):
            claim = {"kind": kind, "basis_fixture": "F-20"}
            self.assertFalse(SURFACE.validate_cost_claim(claim))

    def test_seed_families_separate(self):
        """Fixture: F-20 at its seed placement, with fixture F-19 beside it, as TG-12.5 states.
        Pins: seed replicates sit outside any sampled base design, and held out confirmation seeds form a separate seed family from screening seeds.
        Bar: a design placing seed replicates inside the sampled base, or drawing confirmation seeds from the screening family, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.5; with the surface present, either placement fails.
        """
        require_surface(self, "seed replicates outside the sampled base and confirmation seeds a separate family", "validate_seed_placement")
        good = {"replicates_inside_base_design": False, "confirmation_family": "held out", "screening_family": "screening"}
        self.assertTrue(SURFACE.validate_seed_placement(good))
        inside = {"replicates_inside_base_design": True, "confirmation_family": "held out", "screening_family": "screening"}
        self.assertFalse(SURFACE.validate_seed_placement(inside))
        shared = {"replicates_inside_base_design": False, "confirmation_family": "screening", "screening_family": "screening"}
        self.assertFalse(SURFACE.validate_seed_placement(shared))

    def test_f19_composite_worded_as_measured_cost_fails(self):
        """Fixture: an F-19 composite form worded as a measured cost, as TG-12.5 states.
        Pins: the wording fails validation; compute and cost claims resting on unpriced forms stand guarded in full at plan section 2 section 8.
        Bar: a cost claim resting on an F-19 composite form worded as a measured cost fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.5; with the surface present, acceptance of the wording fails.
        """
        require_surface(self, "F-19 composite form worded as a measured cost rejected", "validate_cost_claim")
        claim = {"kind": "cost", "basis_fixture": "F-19", "wording": "measured cost"}
        self.assertFalse(SURFACE.validate_cost_claim(claim))


if __name__ == "__main__":
    unittest.main()

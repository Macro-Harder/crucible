"""Test group TG-12.2. Run classes and the stopping rule.

Slice S-12, MOD-12 Sweep Controller. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod12, and
records whether the surface stands. While the surface stands absent, each test
fails with a message naming the pinned behaviour and its group.
Standing bar for this file, recorded in full: this group pins no part of the
consolidated R20 duty. Manager settlement S-5 holds: test group TG-08.2 is
the single check for that duty, under Step 12 Amendment R1-010. No test in
this file checks the run record duty, the readout carriage duty, the
condition two duty, or the bar of that consolidated duty, in any form.
Report wording beside this group, Amendment G2-C51, stands as wording only,
assigns no fixture, and enters this group as no test.
"""
import unittest

try:
    from crucible import mod12
    SURFACE = mod12
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-12.2"
RUN_CLASSES = ("screening", "confirmation", "headline", "validation")


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


class TestRunClassSeparation(unittest.TestCase):
    def test_run_class_separation(self):
        """Fixture: one run of each class, screening, confirmation, headline, and validation, inspected for its record markings, as TG-12.2 states. The validation class name is a plan internal name in this fixture.
        Pins: the four classes are distinct, measure choosing runs are kept separate from reporting runs, and confirmation uses held out seeds and held out settings, per AC-9.
        Bar: a claim without a settings lineage is labelled a screening finding only.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, two classes sharing one marking, or a confirmation run on screening domain seeds, fails.
        """
        require_surface(self, "four run classes distinct with confirmation on held out seeds and settings", "run_class_markings")
        markings = SURFACE.run_class_markings()
        self.assertEqual(tuple(sorted(markings.keys())), tuple(sorted(RUN_CLASSES)))
        confirmation = markings["confirmation"]
        self.assertEqual(confirmation["seed_domain"], "held out confirmation")
        self.assertTrue(confirmation["held_out_settings"])

    def test_screening_promoted_by_relabelling_fails(self):
        """Fixture: a screening run relabelled into a confirmation role, as TG-12.2 states.
        Pins: the relabelled run fails validation and gains no confirmation standing.
        Bar: a suite that promotes a screening run into a confirmation role by relabelling fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, acceptance of the relabelled run fails.
        """
        require_surface(self, "screening run promoted by relabelling rejected", "validate_run_record")
        run = {"run_class": "confirmation", "seed_domain": "screening", "relabelled_from": "screening"}
        self.assertFalse(SURFACE.validate_run_record(run))

    def test_claim_without_lineage_labelled_screening_only(self):
        """Fixture: a claim with no settings lineage, as TG-12.2 states.
        Pins: the claim is labelled a screening finding only, and carries no stronger standing.
        Bar: a claim without a settings lineage is labelled a screening finding only.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, a stronger label on such a claim fails.
        """
        require_surface(self, "claim without a settings lineage labelled a screening finding only", "claim_label")
        label = SURFACE.claim_label(claim={"settings_lineage": None})
        self.assertEqual(label, "screening finding only")


class TestEstablishedOnlyUnderStoppingRule(unittest.TestCase):
    def test_incomplete_search_reported_as_lower_bound(self):
        """Fixture: a readout whose challenge search is incomplete against stopping conditions 1 to 6 at brief section 5.11, as TG-12.2 states.
        Pins: the readout is reported as a lower bound with condition 2 named as the failed or unrun condition where the search finds a material failure under the bound as fixed, in the form section 6 states for DQ7-10.
        Bar: no readout is reported as established under condition 2 until the materiality bound stands fixed in advance of the runs it judges, per DQ7-10.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, an established wording on this readout fails.
        """
        require_surface(self, "incomplete challenge search reported as a lower bound with condition 2 named", "readout_status")
        readout = {"search_complete": False, "material_failure_found": True, "bound_fixed_in_advance": True}
        status = SURFACE.readout_status(readout)
        self.assertEqual(status["form"], "lower_bound")
        self.assertEqual(status["named_condition"], 2)

    def test_bound_not_fixed_in_advance_blocks_established(self):
        """Fixture: a readout whose materiality bound was not fixed in advance, as TG-12.2 states.
        Pins: the readout is reported as a lower bound with condition 2 named, and never as established.
        Bar: no readout is reported as established under condition 2 until the materiality bound stands fixed in advance of the runs it judges.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, an established wording on this readout fails.
        """
        require_surface(self, "bound not fixed in advance blocks the established wording", "readout_status")
        readout = {"search_complete": True, "material_failure_found": False, "bound_fixed_in_advance": False}
        status = SURFACE.readout_status(readout)
        self.assertNotEqual(status["form"], "established")
        self.assertEqual(status["named_condition"], 2)


class TestLookRegister(unittest.TestCase):
    def test_look_register_records_each_look(self):
        """Fixture: a family read before its planned replicates complete, as Amendment G5-C07 folded at TG-12.2 states.
        Pins: the family carries a look register under a prewritten alpha spending function fixed in advance; the register records, for each look, the look number, the information fraction as a derived ratio, the boundary the spending function assigned to that look, and whether the readout crossed it; every look taken before a family completes stands in the register.
        Bar: no decision may rest on an unregistered look.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, a register entry missing any of the four recorded items fails.
        """
        require_surface(self, "look register records each look in its four items", "look_register_for_family")
        register = SURFACE.look_register_for_family(family_id="family-under-test")
        self.assertTrue(register["entries"])
        for entry in register["entries"]:
            self.assertIn("look_number", entry)
            self.assertIn("information_fraction", entry)
            self.assertIn("boundary", entry)
            self.assertIn("crossed", entry)
        self.assertTrue(register["spending_function_fixed_in_advance"])

    def test_decision_on_unregistered_look_fails(self):
        """Fixture: a promotion decision resting on a look that stands in no look register entry, as Amendment G5-C07 states.
        Pins: the decision fails validation.
        Bar: no promotion, refinement, top up beyond a rule fixed in the family record before runs, or readout wording decision rests on a look that stands in no look register entry.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, acceptance of the decision fails.
        """
        require_surface(self, "decision resting on an unregistered look rejected", "validate_look_decision")
        decision = {"kind": "promotion", "look_number": 3, "registered": False}
        self.assertFalse(SURFACE.validate_look_decision(decision))

    def test_late_register_entry_does_not_cure(self):
        """Fixture: a look register entry written after the decision it would judge, as Amendment G5-C07 states.
        Pins: the entry does not cure the decision; the decision stands invalid.
        Bar: a look register entry written after the decision it would judge does not cure the decision.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.2; with the surface present, a cured verdict on the decision fails.
        """
        require_surface(self, "late look register entry does not cure its decision", "validate_look_decision")
        decision = {"kind": "promotion", "look_number": 3, "registered": True, "entry_written_after_decision": True}
        self.assertFalse(SURFACE.validate_look_decision(decision))


if __name__ == "__main__":
    unittest.main()

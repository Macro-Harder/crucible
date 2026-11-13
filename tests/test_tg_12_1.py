"""Test group TG-12.1. Family fixed before runs.

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

GROUP = "TG-12.1"


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


class TestFamilySeal(unittest.TestCase):
    def test_edit_to_sealed_family_creates_new_identifier(self):
        """Fixture: a family record edited after sealing, as TG-12.1 states.
        Pins: any edit to a sealed family record creates a new family identifier and runs under the new identifier start again, per Shape 1 and operation C-10.
        Bar: the family is the unit of multiplicity control, fixed before screening runs, per AC-9 and decision D-06.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, an edit keeping the sealed identifier fails.
        """
        require_surface(self, "edit to a sealed family record creates a new family identifier", "apply_family_edit")
        sealed = {"family_id": "fam-1", "sealed": True}
        edited = SURFACE.apply_family_edit(sealed, change={"field": "value"})
        self.assertNotEqual(edited["family_id"], "fam-1")
        self.assertEqual(edited["runs_under"], edited["family_id"])

    def test_reused_identifier_across_edit_fails(self):
        """Fixture: a suite reusing a family identifier across an edit to the sealed record, as TG-12.1 states.
        Pins: the reuse fails validation.
        Bar: a suite that reuses a family identifier across an edit fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, acceptance of the reused identifier fails.
        """
        require_surface(self, "family identifier reuse across an edit rejected", "validate_family_record")
        record = {"family_id": "fam-1", "sealed": True, "edited_after_seal": True, "identifier_changed": False}
        self.assertFalse(SURFACE.validate_family_record(record))

    def test_late_claim_barred_from_family(self):
        """Fixture: a claim entering the family after results are seen, as TG-12.1 states.
        Pins: the claim is barred from the family and supports no headline publication from it.
        Bar: a claim entering after results are seen is barred from the family.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, admission of the late claim fails.
        """
        require_surface(self, "claim entering after results are seen barred", "admit_claim")
        family = {"family_id": "fam-1", "results_seen": True}
        with self.assertRaises(Exception):
            SURFACE.admit_claim(family, claim={"name": "late claim"})


class TestKillCheckPerClaim(unittest.TestCase):
    def test_kill_check_fixed_per_claim(self):
        """Fixture: a family record inspected claim by claim, as TG-12.1 states.
        Pins: for every headline claim in the family list, one named kill check stands fixed before runs, in four parts: the name of the check; the data it runs on, standing outside the artefact under check; the judge that applies it, standing outside the artefact under check; and the killing result.
        Bar: a claim with no kill check supports no headline publication.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, a headline claim with no four part kill check fixed before runs fails.
        """
        require_surface(self, "one named kill check fixed before runs per headline claim", "kill_checks_for_family")
        checks = SURFACE.kill_checks_for_family(family_id="family-under-test")
        self.assertTrue(checks)
        for check in checks:
            self.assertIn("name", check)
            self.assertIn("data", check)
            self.assertIn("judge", check)
            self.assertIn("killing_result", check)
            self.assertTrue(check["data_outside_artefact"])
            self.assertTrue(check["judge_outside_artefact"])
            self.assertTrue(check["fixed_before_runs"])

    def test_claim_without_kill_check_or_inside_judge_fails(self):
        """Fixture: a headline claim with no kill check, and a claim whose check data sits inside the artefact under check, as TG-12.1 states.
        Pins: both claims fail validation and support no headline publication.
        Bar: a claim with no kill check, or with a check whose data or judge sits inside the artefact under check, supports no headline publication.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, acceptance of either claim fails.
        """
        require_surface(self, "claim with no kill check or inside data or judge rejected", "validate_kill_check")
        self.assertFalse(SURFACE.validate_kill_check(None))
        inside = {"name": "k", "data_outside_artefact": False, "judge_outside_artefact": True, "killing_result": "x"}
        self.assertFalse(SURFACE.validate_kill_check(inside))
        inside_judge = {"name": "k", "data_outside_artefact": True, "judge_outside_artefact": False, "killing_result": "x"}
        self.assertFalse(SURFACE.validate_kill_check(inside_judge))


class TestCarriedPinsForThisGroup(unittest.TestCase):
    def test_ecology_point_before_amendment_fails(self):
        """Fixture: a family record fixing an ecology point before the plan amendment Amendment G2-C45 names stands, as that amendment states at TG-12.1.
        Pins: the family record fails validation; AV8b-03 stays banked, its release condition UNMET, and the release condition is necessary and not sufficient.
        Bar: no family record may fix an ecology point until a plan amendment first lands the build changes the point needs.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, acceptance of the family record fails.
        """
        require_surface(self, "family record fixing an ecology point before its amendment rejected", "validate_family_record")
        record = {"family_id": "fam-1", "ecology_point": "fixed", "amendment_landed": False}
        self.assertFalse(SURFACE.validate_family_record(record))

    def test_data_dependent_topup_empty_look_register_fails(self):
        """Fixture: a family record that carries a data dependent top up and an empty look register, as Amendment G1-C19 states at TG-12.
        Pins: the family record fails validation; the look register form stands as one entry per interim read, stating the replicate count at the read, what was decided from that read, and the spending function or the prewritten top up rule that authorised the decision.
        Bar: a family record that carries a data dependent top up and an empty look register fails validation.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-12.1; with the surface present, acceptance of the family record fails.
        """
        require_surface(self, "data dependent top up with an empty look register rejected", "validate_family_record")
        record = {"family_id": "fam-1", "data_dependent_top_up": True, "look_register": []}
        self.assertFalse(SURFACE.validate_family_record(record))


if __name__ == "__main__":
    unittest.main()

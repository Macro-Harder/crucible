"""Contract test for operation C-20, plan section 2 section 5.

The test pins the check field of contract C-20 as plan section 9
states it. Surfaces crossed: MOD-06 and MOD-07, via TG-01.2 and TG-06.3.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-20.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod06 as _m_mod06
    SURFACES["mod06"] = True
except Exception:
    SURFACES["mod06"] = False
try:
    import crucible.mod07 as _m_mod07
    SURFACES["mod07"] = True
except Exception:
    SURFACES["mod07"] = False


class TestContractC20(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-20: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_computed_not_settled_interim_rule(self):
        """
        Fixture: Shape 9 and Contract D: a joint run producing a vouch lien amount, a vouch release and a slash outcome
        Pins: every seam effect reports as computed in Parley and not settled in the chosen escrow, while NQ-45 stands open; validation fails any record that carries settled or released for a cross seam effect, and the report check fails any headline or summary wording that drifts from computed toward settled; the lien state field holds four values only: no lien in force, computed not settled, settled in the chosen escrow, and released, with the last two barred across the seam
        Bar: NQ-45 stands open in full; the interim rule is the contract until it closes; the 21 seam gaps, creation 7, release 6, slash execution 8, collected as the fourteen open semantic items OS-1 to OS-14, are the standing reason
        Failure: a settled or released cross seam record that validates, or settled wording in any report, fails this test; while a crossed surface is absent the test fails naming this behaviour and C-20
        """
        self.require("every cross seam effect reports as computed and not settled, and settled wording fails", "mod06", "mod07")
        import crucible.mod01 as mod01
        import crucible.mod07 as mod07
        for kind in ("vouch lien amount", "vouch release", "slash outcome"):
            report = mod07.seam_effect_report({"kind": kind, "value": 3})
            self.assertEqual(report["lien_state"], "computed not settled")
            self.assertIn("not settled", report["reporting"])
        self.assertTrue(mod07.validate_cross_seam_effect({"lien_state": "computed not settled"}))
        self.assertFalse(mod07.validate_cross_seam_effect({"lien_state": "settled in the chosen escrow"}))
        self.assertFalse(mod07.validate_cross_seam_effect({"lien_state": "released"}))
        self.assertTrue(mod01.validate_lien_state("computed not settled", cross_seam=True))
        self.assertFalse(mod01.validate_lien_state("settled in the chosen escrow", cross_seam=True))
        self.assertFalse(mod07.validate_seam_wording("the effect is settled in the chosen escrow"))

    def test_approval_and_tracer_conditions_on_seam_results(self):
        """
        Fixture: Shape 9 and Contract D: a joint run using an adapter choice with no approval on the record, and a joint run whose positive control does not stand recorded as passing
        Pins: the contract check fails both runs: a choice needs the Project Manager approval on the record, naming the choice, its effects and its approver in the run record before the run starts, and a run holds one tracer passage record for each open semantic item it touches, with the positive control recorded as passing in record form; the seam results of a run failing on either ground are not reportable, and a run whose positive control does not pass has no valid tracer passage record
        Bar: the Escrow Core is reached through the Adapter only, and the Parley Core never calls the Escrow Core directly
        Failure: seam results reported from either run fail this test; while a crossed surface is absent the test fails naming this behaviour and C-20
        """
        self.require("seam results require an approved choice, a passing positive control and a tracer record per touched item", "mod06", "mod07")
        import crucible.mod07 as mod07
        unapproved = mod07.make_adapter_choice("choice-c20", "reading", "point", "v1", "B-4 fold 1")
        self.assertFalse(mod07.choice_approval_stands(unapproved))
        approved = mod07.make_adapter_choice("choice-c20-b", "reading", "point", "v1", "B-4 fold 1", approval={"approver": "Project Manager", "choice_identifier": "choice-c20-b", "effects": "decision level values", "standing": "approved"})
        self.assertTrue(mod07.choice_approval_stands(approved))
        control = mod07.positive_control_record()
        records = mod07.tracer_passage_records("run-c20")
        self.assertEqual(len(records), 14)
        self.assertTrue(mod07.validate_tracer_passage_set(records, positive_control=control))
        run = {"choices": [unapproved], "tracer_records": records, "positive_control": control}
        self.assertFalse(mod07.seam_headline_claim_stands(run, ["OS-1"]))


if __name__ == "__main__":
    unittest.main()

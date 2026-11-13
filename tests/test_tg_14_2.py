"""Test group TG-14.2. Replication verdicts, Contract J.
This group pins no part of the consolidated R20 duty; that duty is checked at
TG-08.2 only, under Step 12 Amendment R1-010, Manager settlement S-5.
Slice S-14, Replication Checker and scoring interface, MOD-13. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod13, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod13 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod13 absent, pinned behaviour unmet: " + behaviour)


class TestTG142(unittest.TestCase):
    def test_one_verdict_record_per_claim(self):
        """
        Fixture: F-12 at the verdict limb, one headline claim submitted for replication.
        Pins: The Checker delivers one replication verdict record per claim, holding the claim identifier, the standard applied, exact replay alone or the distributional standard, and the rests or does not rest outcome, per Contract J.
        Bar: The Reporter may not publish a claim as resting on replication without the verdict record, per operation C-03, and a verdict record naming a distributional standard while the quantities at open point OP-20 stand unfixed, namely the confidence interval method, the numeric equivalence margin, and the named two sample distributional test, fails this group.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.2 and this behaviour; a claim published as resting on replication with no verdict record fails this test when the surface stands.
        """
        require_surface(self, "TG-14.2", "one replication verdict record per claim under Contract J, holding claim identifier, standard applied, and rests or does not rest outcome")
        import crucible.mod13 as surface
        record = surface.verdict_record("claim-1", standard="exact replay alone", outcome="rests")
        self.assertEqual(record["claim_identifier"], "claim-1")
        self.assertEqual(record["standard_applied"], "exact replay alone")
        self.assertEqual(record["outcome"], "rests")
        self.assertTrue(surface.validate_verdict_record(record))
        claim = {"claim_identifier": "claim-1"}
        self.assertTrue(surface.publishable_on_replication(claim, record))
        self.assertFalse(surface.publishable_on_replication(claim, None))
        distributional = {"claim_identifier": "claim-2", "standard_applied": "distributional equivalence", "outcome": "rests"}
        self.assertFalse(surface.validate_verdict_record(distributional))
        with self.assertRaises(Exception):
            surface.verdict_record("claim-2", standard="distributional equivalence", outcome="rests")

    def test_probe_scope_honesty(self):
        """
        Fixture: The replication probe record for a headline scenario.
        Pins: The probe is scoped as a probe of specification completeness with a disagreement catalogue as its deliverable, not as a full second implementation, per open point OP-20.
        Bar: A headline claim quoting a margin or a method as settled before the family record fixes it fails this group.
        Failure: Fails while crucible.mod13 stands absent, naming TG-14.2 and this behaviour; a probe scoped or quoted as a full second implementation, or a margin or method quoted as settled, fails this test when the surface stands.
        """
        require_surface(self, "TG-14.2", "replication probe scoped as a specification completeness probe with a disagreement catalogue as its deliverable")
        import crucible.mod13 as surface
        probe = surface.probe_record("headline scenario")
        self.assertEqual(probe["scope"], "probe of specification completeness")
        self.assertEqual(probe["deliverable"], "disagreement catalogue")
        self.assertFalse(probe["full_second_implementation"])
        self.assertFalse(probe["margin_or_method_presented_as_settled"])
        self.assertFalse(surface.validate_probe_claim({"margin_or_method_presented_as_settled": True}))

    def test_catalogue_field_list_gated(self):
        """
        Fixture: The replication probe record for a headline scenario, inspected for its catalogue carriage. State recorded as gated on the catalogue field list standing fixed on the record at open point OP-20.
        Pins: The DisagreementCatalogue stands carried with its field list open inside OP-20, and this test records the catalogue limb as gated, never as passed, until that field list stands fixed on the record, per gated duty register line 12, no owner named in any record the register rests on.
        Bar: A verdict record, a probe record, or a suite summary presenting the catalogue as a delivered form with a settled field list before that fixing fails this group.
        Failure: Gated form only; this test never passes while the catalogue field list does not stand fixed on the record.
        """
        self.skipTest("Gated: the DisagreementCatalogue field list standing fixed on the record at open point OP-20")


if __name__ == "__main__":
    unittest.main()

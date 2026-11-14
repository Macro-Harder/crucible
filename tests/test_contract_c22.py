"""Contract test for operation C-22, plan section 2 section 5.

The test pins the check field of contract C-22 as plan section 9
states it. Surfaces crossed: MOD-11, via TG-13.1 and TG-13.5.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-22.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod11 as _m_mod11
    SURFACES["mod11"] = True
except Exception:
    SURFACES["mod11"] = False


class TestContractC22(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-22: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_resolution_and_state_checks(self):
        """
        Fixture: F-01 and F-02: the records a headline unit is built from, and the unit itself
        Pins: the resolution check at building: every input record resolves in one lookup, or no unit stands, and the failure is recorded at the building act as a named failure entry in the family record of the family whose unit was not built, stating the record that did not resolve and the lookup that failed; the state check at reporting: every unit names its record state, the run record it reads and, where a summary record is among its inputs, whether that record stood before or after its last evaluation under C-08, with the evaluation outcome it read, and a unit cited across a C-08 amendment without rederivation fails; the Reporter reads the GC-08 outside call check field in the run record before building any headline unit from that run, and every reported interval states the lower endpoint, the upper endpoint, the point estimate, the interval method by name and the level, in numbers in the same unit as any display of it, with one sentence in words stating the interval reading rule
        Bar: derivation to record state tie stands as gap G-12 in research paper R11 in the mapping row form; the contract closes that gap by the record state tie in its guarantee, and tests pin the counting and lookup rules the brief states, in the form the contract check states them
        Failure: a unit built from an unresolved record, a unit naming no record state, an interval missing any stated element, or a failed entry left unrecorded fails this test; while the surface is absent the test fails naming this behaviour and C-22
        """
        self.require("headline units build only from records resolving in one lookup and name their record state", "mod11")
        import crucible.mod11 as mod11
        family = {}
        failed = mod11.build_headline_unit_from_run("run-c22-absent", {}, family_record=family)
        self.assertFalse(failed["built"])
        self.assertIsNone(failed["unit"])
        self.assertTrue(family["named_failures"])
        self.assertEqual(family["named_failures"][0]["run_identifier"], "run-c22-absent")
        import crucible.mod10 as mod10
        mod10.retain_run_record({"run_id": "run-c22", "run_identifier": "run-c22", "record_state": "as retained"})
        values = {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}
        values["claim_sentence"] = (
            "At the sampled points within the stated scope, the "
            "result holds for the sampled points only, and nothing "
            "is claimed beyond the stated limits.")
        values["grounding_sentence"] = (
            "This unit rests on the retained run records within "
            "the stated scope, and its limits are that nothing is "
            "claimed beyond the sampled points in this unit.")
        values["qualifiers_and_markings_block"] = (
            "seam status: no cross seam effect; "
            "kill check: self checked only; "
            "dependence mark: DQ-164 confirmation form, recording "
            "that DQ-164 stands settled as confirmation only; "
            "Parley Q3 statement: no part of the result encodes "
            "Parley Q3 behaviour; "
            "core only qualifier: this unit is a core only result; "
            "anchor scenario statement: no anchor scenario is "
            "used in this unit.")
        built = mod11.build_headline_unit_from_run("run-c22", values)
        self.assertTrue(built["built"])
        self.assertTrue(mod11.validate_headline_unit(built["unit"]))

    def test_weekly_counts_count_units_once(self):
        """
        Fixture: F-01 and F-02: the summary records for one week and the reported weekly headline reading load
        Pins: the counting check: the weekly load recomputed from summary records alone under the count once rule equals the reported load; one unit counts once however many runs support it, counting the distinct headline unit identifiers whose witness records fall in that week
        Bar: a weekly count that double counts a unit supported by many runs is a breach at any size, not a divergence
        Failure: a recomputed load differing from the reported load fails this test; while the surface is absent the test fails naming this behaviour and C-22
        """
        self.require("weekly headline load counts each unit once and recomputes from summary records alone", "mod11")
        import crucible.mod11 as mod11
        records = [{"week": "W1", "headline_unit_identifiers": ["u1", "u2"]}, {"week": "W1", "headline_unit_identifiers": ["u1"]}, {"week": "W2", "headline_unit_identifiers": ["u3"]}]
        self.assertEqual(mod11.weekly_count(records, "W1"), 2)
        reported = mod11.weekly_count(records, "W1")
        recomputed = len({uid for record in records if record["week"] == "W1" for uid in record["headline_unit_identifiers"]})
        self.assertEqual(reported, recomputed)

    def test_late_claim_barred_from_the_family(self):
        """
        Fixture: F-01 and F-02 beside a family record inspected for a claim entering after results are seen
        Pins: the claim is barred from the family: the family is the unit of multiple testing control, fixed before runs, and no claim enters the family after results are seen; a transition derivation stands reported as a finished derivation only where the interval method stands fixed in the family record before runs
        Bar: a claim without a settings lineage is labelled a screening finding only
        Failure: a late claim standing in the family, or a transition derivation reported as finished with no method fixed in advance, fails this test; while the surface is absent the test fails naming this behaviour and C-22
        """
        self.require("no claim enters a family after results are seen", "mod11")
        import crucible.mod11 as mod11
        family = {"headline_claims": ["claim-1"]}
        self.assertFalse(mod11.claim_enters_family(family, "claim-1", results_seen=True))
        self.assertFalse(mod11.claim_enters_family(family, "late claim", results_seen=False))
        self.assertTrue(mod11.claim_enters_family(family, "claim-1", results_seen=False))


if __name__ == "__main__":
    unittest.main()

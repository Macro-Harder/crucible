"""Test group TG-16.6. The refusal set as test input.
Slice S-16, integration, fixtures, and the validation run class. The suite
convention surface named here is crucible.mod11. Suite form: design/steps/step-13-opening-record.md section 4.
While that surface does not stand, every non gated test in this file fails by name,
stating the pinned behaviour and its group, as plan section 2 rules 1 and 2 state.
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


class TestTG166(unittest.TestCase):
    def test_every_refusal_has_an_enforcing_test(self):
        """
        Fixture: The refusal set the plan carries as test input for plan section 2, namely the guard tests of section 8 and the barred contract tests of section 5 of the mapping, refusal by refusal.
        Pins: Each refusal in that set points to the contract and the slice that enforce the refusal, and each such refusal is exercised by at least one guard test in section 8 or one barred contract test in section 5 of the mapping.
        Bar: A refusal in that set with no enforcing test named is a defect in the mapping, recorded at Step 13 before the test audit sits, and never cured by a test that merely restates the refusal in its name.
        Failure: Fails while the integrated surface stands absent, naming TG-16.6 and this behaviour; a refusal with no enforcing test named fails this test in every state, as a mapping defect recorded before the test audit sits.
        """
        require_surface(self, "TG-16.6", "every refusal in the refusal set points to its enforcing contract and slice and is exercised by at least one guard test or barred contract test")
        import crucible.mod16 as surface
        records = surface.refusal_set()
        self.assertTrue(records)
        for record in records:
            self.assertTrue(record["contract"])
            self.assertTrue(record["slice"])
            self.assertIn("test_", record["enforcing_test"])
        self.assertTrue(surface.validate_refusal_coverage(records))

    def test_refusal_not_cured_by_restatement(self):
        """
        Fixture: One refusal from the refusal set, offered with a test that merely restates the refusal in its name as its only enforcement.
        Pins: A restatement is not an enforcing test: the enforcing test must exercise the refusal against its scan set or its barred contract limb, as section 8 and section 5 of the mapping state.
        Bar: A refusal counted as enforced by a name only restatement fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.6 and this behaviour; a name only restatement counted as enforcement fails this test in every state.
        """
        require_surface(self, "TG-16.6", "no refusal cured by a test that merely restates the refusal in its name")
        import crucible.mod16 as surface
        restated_only = [{"refusal": "some refusal", "contract": "C-01", "slice": "S-01", "enforcing_test": "some refusal"}]
        self.assertFalse(surface.validate_refusal_coverage(restated_only))
        unnamed = [{"refusal": "some refusal", "contract": "C-01", "slice": "S-01", "enforcing_test": "a restatement in prose"}]
        self.assertFalse(surface.validate_refusal_coverage(unnamed))


if __name__ == "__main__":
    unittest.main()

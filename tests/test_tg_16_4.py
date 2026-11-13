"""Test group TG-16.4. Folding check discharge at integration.
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


class TestTG164(unittest.TestCase):
    def test_seam_cases_checked_by_non_folder(self):
        """
        Fixture: F-12 at integration level, with fixture F-11 beside it in its gated form.
        Pins: This slice discharges the folding check the escrow slice names: seam tests written against the ruling text, at least one seam case per ruling checked by a reader who did not perform that folding, before any B-5 difference is reported as a ruling effect.
        Bar: The check is discharged here or it stands undischarged on the integration record; it is never discharged by the slice level tests alone, and the sham control at F-11 stays gated until its two records stand, as TG-05.4 states.
        Failure: Fails while the integrated surface stands absent, naming TG-16.4 and this behaviour; a B-5 difference reported as a ruling effect before this discharge fails this test when the surface stands.
        """
        require_surface(self, "TG-16.4", "folding check discharged at integration, seam tests against the ruling text, at least one seam case per ruling checked by a reader who did not fold")
        import crucible.mod16 as surface
        record = surface.folding_check_record()
        self.assertTrue(surface.validate_folding_discharge(record))
        self.assertTrue(record["checker_distinct_from_folder"])
        for ruling in ("DQ-1", "DQ-2", "DQ-3", "DQ-4"):
            self.assertGreaterEqual(record["seam_cases_per_ruling"][ruling], 1)
        self.assertFalse(record["discharged_by_slice_tests_alone"])
        self.assertFalse(surface.validate_folding_discharge({"discharged_by_slice_tests_alone": True, "checker_distinct_from_folder": True, "seam_cases_per_ruling": {"DQ-1": 1}}))

    def test_sham_control_stays_gated_at_integration(self):
        """
        Fixture: F-11, the sham variant control, at integration level in its gated form, beside F-12.
        Pins: The sham control at F-11 stays gated until its two records stand, the equivalence margin at NQ-49 fixed on the record and the seam check under the duty at decision D-02 condition three read with D-20, as TG-05.4 states, and no sham result is reported at integration before both stand.
        Bar: A sham result reported at integration before both records stand fails this group, and a suite record presenting the control as passed fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.4 and this behaviour; a sham result reported before its two records stand fails this test in every state.
        """
        require_surface(self, "TG-16.4", "sham control at F-11 stays gated at integration until its two records stand, no sham result reported before both stand")
        import crucible.mod16 as surface
        standing = surface.sham_control_standing()
        self.assertTrue(standing["gated"])
        self.assertFalse(standing["records_standing"])
        self.assertEqual(len(standing["waiting_on"]), 2)
        self.assertFalse(surface.validate_sham_result({"form": "sham result"}))
        self.assertTrue(surface.validate_sham_result(None))


if __name__ == "__main__":
    unittest.main()

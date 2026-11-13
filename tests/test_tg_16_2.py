"""Test group TG-16.2. The tracer run.
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


class TestTG162(unittest.TestCase):
    def test_smallest_end_to_end_cut(self):
        """
        Fixture: One family with one point, one run class, and one retained RunRecord in form only, retained in one store by the narrowed S-10 element and read back through the Recorder store reading path in MOD-10, which that element itself builds, and through no other path, in the thin cut the slices paper states: S-01, S-02 in interface form only, S-03, a narrowed S-09 element, and a narrowed S-10 element, and no other slice. The narrowed S-09 element is the Tick Engine interface and the DetectionInput projection only, exercised against the canary case at fixture F-09 for field closure, with no ground truth field and no field derived from membership in the projected record.
        Pins: The tracer proves the dependency direction in running form for the restated path alone, delivers no event to a rule core in running form, delivers no DetectionInput to the detection layer in running form, forms no reportable run, proves no hash equality claim while OP-24 stands open, and its result stands recorded before the full build proceeds.
        Bar: The tracer is not a seventeenth slice, claims no headline result, and no slice is described as built because the tracer ran; wording to any of those effects fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.2 and this behaviour; a tracer forming a reportable run or claiming a headline result fails this test when the surface stands.
        """
        require_surface(self, "TG-16.2", "smallest end to end tracer cut proving dependency direction for the restated path alone, no reportable run, no hash equality claim, recorded before the full build proceeds")
        import crucible.mod16 as surface
        record = surface.tracer_record()
        self.assertTrue(record["read_back_matches"])
        self.assertFalse(record["reportable_run_formed"])
        self.assertFalse(record["headline_result_claimed"])
        self.assertFalse(record["hash_equality_claimed"])
        self.assertTrue(record["recorded_before_full_build"])
        result = surface.run_tracer_cut()
        self.assertEqual(result["read_back_record"], result["record"])
        self.assertFalse(result["projection_evidence"]["canary_value_present_in_projection"])

    def test_tracer_scope_exclusions(self):
        """
        Fixture: The tracer cut inspected for any element outside its stated contents.
        Pins: The stated dependencies of S-09 that the cut does not contain, namely S-04, S-05, S-06, S-07, and S-08, stand outside the cut; the shell, module MOD-14 and its building slice S-15, stands outside the cut and no part of the cut uses the shell; slice S-14, building module MOD-13, stands outside the cut, no element of the cut bears that identifier, and the cut makes no replication claim and no verdict claim.
        Bar: A cut element from a named outside slice, a cut using the shell, or a replication or verdict claim from the cut, fails this group.
        Failure: Fails while the integrated surface stands absent, naming TG-16.2 and this behaviour; a tracer cut containing a named outside element fails this test when the surface stands.
        """
        require_surface(self, "TG-16.2", "tracer scope exclusions, S-04 to S-08, the shell and S-15, and S-14 with MOD-13 outside the cut, no replication or verdict claim from the cut")
        import crucible.mod16 as surface
        record = surface.tracer_record()
        outside = " ".join(record["outside_the_cut"])
        for excluded in ("S-04", "S-05", "S-06", "S-07", "S-08", "S-14", "MOD-13", "S-15", "MOD-14"):
            self.assertIn(excluded, outside)
        self.assertFalse(record["replication_claim_made"])
        self.assertFalse(record["verdict_claim_made"])
        self.assertFalse(record["seventeenth_slice"])
        self.assertFalse(surface.validate_tracer_wording({"slice_built_because_tracer_ran": True}))
        self.assertFalse(surface.validate_tracer_wording({"headline_result_claimed": True}))

    def test_tracer_projection_field_closure(self):
        """
        Fixture: F-09, the canary membership leak test, at the narrowed S-09 element of the tracer cut.
        Pins: The DetectionInput projection is exercised against the canary case at F-09 for field closure, with no ground truth field and no field derived from membership in the projected record.
        Bar: A projected record carrying a ground truth field, or a field derived from membership, fails this group in the canary form.
        Failure: Fails while the integrated surface stands absent, naming TG-16.2 and this behaviour; a projection leaking a ground truth or membership derived field fails this test when the surface stands.
        """
        require_surface(self, "TG-16.2", "DetectionInput projection field closure against the F-09 canary case, no ground truth field and no membership derived field")
        import crucible.mod04 as mod04
        state = {"agent_identifier": "agent-1", "day": 2, "feature_values": {"activity": 3, "nested": {"membership": mod04.CANARY_VALUE, "kept": 1}}, "rule_records": [{"kind": "daily_record", "detail": {"ground_truth": mod04.CANARY_VALUE, "kept_detail": "here"}}], "membership": mod04.CANARY_VALUE, "ground_truth": mod04.CANARY_VALUE}
        projected = mod04.project_detection_input(state)
        self.assertEqual(list(projected.keys()), list(mod04.PROJECTION_KEYS))
        self.assertFalse(mod04._value_appears(mod04.CANARY_VALUE, projected))
        self.assertEqual(projected["feature_values"]["nested"]["kept"], 1)
        self.assertFalse(mod04.exercise_f09_canary())


if __name__ == "__main__":
    unittest.main()

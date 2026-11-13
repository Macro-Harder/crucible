"""Test group TG-15.3. Outside call check surface, GC-08 and DQ7-12.
Slice S-15, Shell, MOD-14. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod14, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod14 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod14 absent, pinned behaviour unmet: " + behaviour)


class TestTG153(unittest.TestCase):
    def test_check_reads_named_records_only(self):
        """
        Fixture: The dependency manifest for the build a run used and the process and network call log for the run, in the Candidate A forms DQ7-12 supplies as plan design, with the outside call check field the decision names in the run record.
        Pins: The outside call check outcome stands in that field, computed from those two records and from no other source, per open point OP-04 as restated on the decision; the check reads the dependency manifest and the call log only.
        Bar: GC-08 operates on the carried records in those forms only, and a pass certifies only the absence the check reads, in the form governing constraint GC-08 itself states; a check computed from any third source fails this group.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.3 and this behaviour; a check computed from any third source fails this test when the surface stands.
        """
        require_surface(self, "TG-15.3", "outside call check computed from the dependency manifest and the call log only, outcome standing in the named field of the run record")
        import crucible.mod14 as surface
        manifest = {"entries": [{"name": "crucible.mod01"}]}
        call_log = {"calls": [{"outside_call": False}]}
        result = surface.outside_call_check(manifest, call_log)
        self.assertEqual(result["field"], "outside_call_check")
        self.assertEqual(result["sources"], ["dependency manifest", "process and network call log"])
        self.assertEqual(result["outcome"], "no outside calls read")
        with self.assertRaises(surface.NamedShellFailure):
            surface.outside_call_check(manifest, call_log, extra_source={"name": "third source"})
        run_record = {"outside_call_check": result["outcome"]}
        self.assertEqual(run_record["outside_call_check"], "no outside calls read")

    def test_operator_boundary_at_the_shell(self):
        """
        Fixture: An operator action attempted against a run record, a checkpoint set, and a sealed family record through the command surface.
        Pins: Validation reads checkpoint manifests beside the run record to compare seeds, settings, and rule versions, per brief section 7.4, and no operator action edits a sealed family record, a closed run record outside the flag rule path at TG-10.3, or a checkpoint set outside the deletion rule at plan section 2 section 6.
        Bar: An operator edit path that bypasses a validation or seal check fails this group.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.3 and this behaviour; an operator edit bypassing a validation or seal check fails this test when the surface stands.
        """
        require_surface(self, "TG-15.3", "operator boundary at the shell, no operator edit of a sealed family record, a closed run record outside the flag rule path, or a checkpoint set outside the deletion rule")
        import crucible.mod14 as surface
        self.assertFalse(surface.validate_operator_action({"kind": "edit", "target": "sealed family record"}))
        self.assertFalse(surface.validate_operator_action({"kind": "edit", "target": "closed run record", "path": "direct"}))
        self.assertFalse(surface.validate_operator_action({"kind": "edit", "target": "checkpoint set", "path": "direct"}))
        self.assertTrue(surface.validate_operator_action({"kind": "edit", "target": "closed run record", "path": "flag rule"}))
        self.assertTrue(surface.validate_operator_action({"kind": "edit", "target": "checkpoint set", "path": "deletion rule"}))
        self.assertTrue(surface.validate_operator_action({"kind": "read", "target": "checkpoint set"}))


if __name__ == "__main__":
    unittest.main()

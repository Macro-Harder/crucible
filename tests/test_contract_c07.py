"""Contract test for operation C-07, plan section 2 section 5.

The test pins the check field of contract C-07 as plan section 9
states it. Surfaces crossed: MOD-01 and MOD-10, via TG-01.5 and TG-10.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-07.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod01 as _m_mod01
    SURFACES["mod01"] = True
except Exception:
    SURFACES["mod01"] = False
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC07(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-07: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_one_record_one_owner_complete_or_invalid(self):
        """
        Fixture: Shape 4: one completed run inspected across its record, in the F-22 form discipline the mapping row states as its basis
        Pins: one record, one owner per field group, complete or invalid; record validation at close runs field by field against Shape 4, plus the reconciliation trace check: every field named, its record form named, its place in the single record named, and the independent reader check recorded
        Bar: a partial record never validates as complete; a missing required field, a version or hash mismatch, or a dropped load bearing field fails the run as not reportable
        Failure: a second record for the run, a field group filled by a writer other than its owner, or a partial record validating as complete fails this test; while a crossed surface is absent the test fails naming this behaviour and C-07
        """
        self.require("one run record with one owner per field group, complete or invalid", "mod01", "mod10")
        import crucible.mod01 as mod01
        import crucible.mod10 as mod10
        complete = mod01.minimal_valid_instance("4")
        self.assertTrue(mod01.validate_record("4", complete))
        partial = dict(complete)
        partial.pop(next(iter(partial)))
        self.assertFalse(mod01.validate_record("4", partial))
        store = mod10.RecorderStore(store_kind="sweep")
        record = {"run_id": "run-c07", "form": "run record"}
        store.retain_run_record(record)
        self.assertEqual(store.read_run_record("run-c07"), record)
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-c07"})
        owned = {"run_id": "run-c07", "group_writers": {}}
        self.assertTrue(mod10.validate_run_record_set([owned]))
        self.assertFalse(mod10.validate_run_record_set([owned, dict(owned)]))
        trace = mod01.reconciliation_trace()
        self.assertTrue(mod01.check_reconciliation_trace(trace))

    def test_family_version_and_hash_match_the_seal(self):
        """
        Fixture: Shape 4: a run record carrying a family version or manifest hash differing from the sealed manifest under C-10
        Pins: validation fails the record on the mismatch, and the run is not reportable
        Bar: two writers filling the same group differently is a breach detected at validation, not a lag a reader waits out
        Failure: such a record that validates fails this test; while a crossed surface is absent the test fails naming this behaviour and C-07
        """
        self.require("run record mismatching the sealed family version or hash fails validation", "mod01", "mod10")
        import crucible.mod01 as mod01
        manifest = {"family_version": "v1", "sealed_family_record_hash": "hash-1"}
        matching = {"family_version": "v1", "family_manifest_hash": "hash-1"}
        self.assertTrue(mod01.validate_family_seal_match(manifest, matching))
        mismatched = {"family_version": "v2", "family_manifest_hash": "hash-1"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, mismatched))
        mismatched_hash = {"family_version": "v1", "family_manifest_hash": "hash-2"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, mismatched_hash))

    def test_reconciliation_claim_limb_gated(self):
        """
        Fixture: no fixture stands for the reconciliation limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: claims resting on field groups the outstanding reconciliation acts touch, in the full AC-14 form
        Bar: the reconciliation stands as a criterion, AC-14, not as a published table, until the two outstanding reconciliation acts stand; until they stand, no claim rests on a field group those acts touch and any such group carries that standing on its face
        Failure: a claim resting on a touched field group while the gate stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the two outstanding reconciliation acts for the five source record forms under AC-14")


if __name__ == "__main__":
    unittest.main()

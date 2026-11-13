"""Contract test for operation C-01, plan section 2 section 5.

The test pins the check field of contract C-01 as plan section 9
states it. Surfaces crossed: MOD-02 and MOD-10, via TG-02.4 and TG-10.2.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-01.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod02 as _m_mod02
    SURFACES["mod02"] = True
except Exception:
    SURFACES["mod02"] = False
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC01(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-01: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_manifest_uniqueness_and_same_state(self):
        """
        Fixture: Shape 12 record set: one run, one simulated day, its checkpoint manifest
        Pins: one manifest per run per day plus run close, carrying every Shape 12 field, with hash and generator state describing the same state; a second write under the same run and day key is rejected and recorded as a rejected write
        Bar: no divergence between manifest, hash and stored state is tolerated; storage accounting never counts a checkpoint as a summary, a snapshot or an event log
        Failure: two manifests standing for one run and day, fields describing different states, or a checkpoint counted as a result fails this test; while a crossed surface is absent the test fails naming this behaviour and C-01
        """
        self.require("one checkpoint manifest per run per day describing one state, never counted as a result", "mod02", "mod10")
        import crucible.mod10 as mod10
        manifest = {"run_identifier": "run-c01-a", "simulated_day": 3, "state_reference": "state-1", "generator_state": "generator-1", "form": "checkpoint manifest"}
        retained = mod10.retain_checkpoint(dict(manifest))
        self.assertEqual(retained, manifest)
        held = [item for item in mod10.checkpoints_for_run("run-c01-a") if item.get("simulated_day") == 3]
        self.assertEqual(len(held), 1)
        same = mod10.checkpoint_integrity_check(manifest, dict(manifest))
        self.assertFalse(same["alteration_detected"])
        self.assertFalse(same["state_hash_equality_claimed"])
        differing = dict(manifest)
        differing["state_reference"] = "state-2"
        self.assertTrue(mod10.checkpoint_integrity_check(manifest, differing)["alteration_detected"])
        store = mod10.RecorderStore(store_kind="sweep")
        store.retain_run_record({"run_id": "run-c01-a"})
        rejected = []
        try:
            store.retain_run_record({"run_id": "run-c01-a"})
        except ValueError as exc:
            rejected.append(str(exc))
        self.assertEqual(len(rejected), 1)
        self.assertIn("second record", rejected[0])
        accounting = mod10.storage_accounting({"summaries": 1, "daily_snapshots": 1, "event_logs": 1, "checkpoints": 1})
        self.assertEqual(accounting["result_count"], 3)
        self.assertEqual(accounting["checkpoint_count"], 1)

    def test_checkpoint_counted_as_result_fails_accounting(self):
        """
        Fixture: Shape 12 record set: a storage accounting total counting one checkpoint as a summary
        Pins: the accounting check fails any total that counts a checkpoint as a summary, a snapshot or an event log
        Bar: a checkpoint is not a result form in any accounting total
        Failure: such a total that passes accounting fails this test; while a crossed surface is absent the test fails naming this behaviour and C-01
        """
        self.require("storage total counting a checkpoint as a result fails", "mod02", "mod10")
        import crucible.mod10 as mod10
        counted = {"summaries": 1, "daily_snapshots": 1, "event_logs": 1, "checkpoints": 1, "result_count": 4}
        self.assertFalse(mod10.validate_storage_accounting(counted))
        correct = {"summaries": 1, "daily_snapshots": 1, "event_logs": 1, "checkpoints": 1, "result_count": 3}
        self.assertTrue(mod10.validate_storage_accounting(correct))

    def test_hash_equality_and_retention_reliance_gated(self):
        """
        Fixture: no fixture stands for the barred limbs while their gates stand. Recorded state: gated, never passed
        Pins: when the gates open: hash recomputation as an equality check, and storage and cost reliance on the DQ7-08 rule at clauses C1 to C12 beyond the loci clause C12 names
        Bar: while OP-24 stands open the check claims the field list and its order only and no result rests on a computed hash equality; the DQ7-08 rule stands as the recorded decided form only, carried open for reliance until the reconciliation act for Plan Amendment (Step 11, reconciliation) stands; checkpoint size by population stands open and the checkpoint numeric cap stands carried at DQ7-03
        Failure: a hash equality claim or a barred reliance claim made while either gate stands fails this group; this test records the gated state and never passes while the gates stand
        """
        self.skipTest("Gated: OP-24 canonical form per hashed field on a plan level record, and the reconciliation act for Plan Amendment (Step 11, reconciliation) for DQ7-08 reliance")


if __name__ == "__main__":
    unittest.main()

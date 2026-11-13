"""Test group TG-06.1, slice S-06, MOD-07 Escrow Adapter.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
"""
import unittest

try:
    from crucible import mod07 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG061(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-06.1: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_every_seam_effect_is_a_recorded_choice(self):
        """
        Fixture: one joint run exercising creation, release and slash specification paths in turn
        Pins: each adapter choice stands recorded as an adapter choice in an InterpretationLogEntry and in the run record, never presented as a rule of either system, per Contract D and operation C-12
        Bar: a recorded choice may drive only decision level computed values, and each choice needs the Project Manager approval on the record before a run may use it, per Trade 7; a run using an unapproved choice fails this group
        Failure: a seam effect with no log entry, no run record entry, a disagreement between the pair, or no approval on the record fails this test; a choice presented as a rule of either system fails this test; a recorded choice driving a value that is not a decision level computed value fails this test; while the surface is absent the test fails naming this behaviour and TG-06.1
        """
        self.require_surface("every seam effect is recorded as an adapter choice in the log and the run record with approval on the record")
        approval = {"approver": "Project Manager", "choice_identifier": "ch-1", "effects": "creation, release and slash specification paths", "standing": "approved"}
        for path in ("creation", "release", "slash specification"):
            choice = _mod.make_adapter_choice(
                "ch-1", "reading for " + path, "rule point of " + path,
                "governing text v1", "B-4 fold v1",
                approval=dict(approval),
                drives=[{"level": "decision", "kind": "computed value"}],
            )
            self.assertEqual(choice["recorded_as"], "adapter choice")
            self.assertIsNone(choice["presented_as_rule_of"])
            log_entry = _mod.interpretation_log_entry(choice)
            run_entry = _mod.run_record_entry(choice)
            self.assertTrue(_mod.validate_choice_pair(log_entry, run_entry))
            self.assertTrue(_mod.choice_approval_stands(choice))
            self.assertTrue(_mod.validate_adapter_choice(choice))
        as_rule = _mod.make_adapter_choice(
            "ch-2", "reading", "rule point", "governing text v1", "B-4 fold v1",
            approval=dict(approval, choice_identifier="ch-2"))
        as_rule["presented_as_rule_of"] = "Parley"
        self.assertFalse(_mod.validate_adapter_choice(as_rule))
        drives_outcome = _mod.make_adapter_choice(
            "ch-3", "reading", "rule point", "governing text v1", "B-4 fold v1",
            approval=dict(approval, choice_identifier="ch-3"),
            drives=[{"level": "settlement", "kind": "lien figure"}])
        self.assertFalse(_mod.validate_adapter_choice(drives_outcome))

    def test_unapproved_choice_fails_the_run(self):
        """
        Fixture: one joint run using one adapter choice with no Project Manager approval on its record
        Pins: a run using an unapproved adapter choice fails
        Bar: no adapter choice drives a run without the approval the record names, per Trade 7
        Failure: a run that proceeds on an unapproved choice fails this test; while the surface is absent the test fails naming this behaviour and TG-06.1
        """
        self.require_surface("run using an unapproved adapter choice fails")
        choice = _mod.make_adapter_choice(
            "ch-9", "reading", "rule point", "governing text v1", "B-4 fold v1",
            approval=None,
            drives=[{"level": "decision", "kind": "computed value"}])
        self.assertFalse(_mod.choice_approval_stands(choice))
        run = {
            "adapter_choices": [choice],
            "tracer_passage_records": _mod.tracer_passage_records("run-9"),
            "positive_control": _mod.positive_control_record(),
            "cross_seam_effects": [],
        }
        self.assertFalse(_mod.validate_joint_run(run))
        self.assertEqual(
            _mod.joint_run_failure(run),
            "run using an unapproved adapter choice fails")

    def test_no_direct_core_to_core_call(self):
        """
        Fixture: the module dependency record for the whole build
        Pins: the Parley Core never calls the Escrow Core directly; MOD-07 alone depends on both cores
        Bar: a direct dependency edge between the two core modules fails this group at dependency inspection, before any run
        Failure: a dependency record showing a direct core to core edge fails this test; while the surface is absent the test fails naming this behaviour and TG-06.1
        """
        self.require_surface("no direct dependency edge stands between the Parley Core and the Escrow Core")
        record = _mod.dependency_record()
        self.assertTrue(_mod.validate_dependency_record(record))
        self.assertEqual(record["direct_core_to_core_edges"], [])
        self.assertEqual(record["joint_dependent"], "MOD-07")
        for source, target in record["edges"]:
            self.assertNotEqual({source, target}, {"MOD-05", "MOD-06"})
        forged = {
            "edges": [("MOD-05", "MOD-06"), ("MOD-05", "MOD-07"),
                      ("MOD-06", "MOD-07")],
            "joint_dependent": "MOD-07",
            "direct_core_to_core_edges": [("MOD-05", "MOD-06")],
        }
        self.assertFalse(_mod.validate_dependency_record(forged))


if __name__ == "__main__":
    unittest.main()

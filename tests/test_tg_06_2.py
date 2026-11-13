"""Test group TG-06.2, slice S-06, MOD-07 Escrow Adapter.

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


class TestTG062(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-06.2: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_one_record_per_open_semantic_item(self):
        """
        Fixture: a joint run record inspected for its TracerPassageRecord set
        Pins: one record per open semantic item OS-1 to OS-14 in every joint run, naming the item, the point in the run where a value for that item would have to pass the seam, what in fact passed, and the result: passed as a record, blocked, or not attempted, per Contract D
        Bar: a joint run missing any one of the fourteen records fails this group, and a headline claim resting on the seam carries the tracer passage result for the items it touches
        Failure: a joint run record set with fewer than fourteen records, or a record missing any of its four stated parts, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.2
        """
        self.require_surface("every joint run carries one tracer passage record per item OS-1 to OS-14")
        records = _mod.tracer_passage_records("run-under-test")
        self.assertEqual(len(records), 14)
        items = tuple(sorted(r["open_semantic_item"] for r in records))
        self.assertEqual(items, tuple(sorted(_mod.OPEN_SEMANTIC_ITEMS)))
        for record in records:
            for field in ("open_semantic_item", "point_in_run",
                          "what_in_fact_passed", "result"):
                self.assertIn(field, record)
                self.assertIsNotNone(record[field])
            self.assertIn(record["result"], _mod.TRACER_RESULTS)
        self.assertTrue(_mod.validate_tracer_passage_set(records))

    def test_positive_control_passes_in_record_form(self):
        """
        Fixture: F-10, the positive control tracer
        Pins: a tracer value placed on the escrow request lien path, the one path the register records as meeting in shape, is recorded as passing in record form
        Bar: a run whose positive control does not pass has no valid tracer passage record, and no seam result from that run is reportable
        Failure: a positive control not recorded as passing, or a seam result reported from such a run, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.2
        """
        self.require_surface("positive control on the escrow request lien path is recorded as passing in record form")
        control = _mod.positive_control_record()
        self.assertEqual(control["fixture"], "F-10")
        self.assertEqual(control["path"], "escrow request lien path")
        self.assertEqual(control["result"], "passed as a record")
        self.assertTrue(control["recorded_as_passing"])
        records = _mod.tracer_passage_records("run-under-test")
        self.assertTrue(_mod.validate_tracer_passage_set(records, control))
        failing = {"fixture": "F-10", "path": "escrow request lien path",
                   "result": "blocked", "recorded_as_passing": False}
        self.assertFalse(_mod.validate_tracer_passage_set(records, failing))

    def test_missing_tracer_record_fails_the_run(self):
        """
        Fixture: a joint run record with one of the fourteen tracer passage records removed
        Pins: the joint run fails and no headline claim resting on the seam stands from it
        Bar: a headline claim resting on the seam carries the tracer passage result for the items it touches
        Failure: a run missing a record that validates, or a headline claim standing from it, fails this test; while the surface is absent the test fails naming this behaviour and TG-06.2
        """
        self.require_surface("joint run missing a tracer passage record fails")
        records = _mod.tracer_passage_records("run-under-test")
        short = records[:-1]
        self.assertEqual(len(short), 13)
        self.assertFalse(_mod.validate_tracer_passage_set(short))
        run = {
            "adapter_choices": [],
            "tracer_passage_records": short,
            "positive_control": _mod.positive_control_record(),
            "cross_seam_effects": [],
        }
        self.assertFalse(_mod.validate_joint_run(run))
        self.assertEqual(
            _mod.joint_run_failure(run),
            "joint run missing a tracer passage record fails")
        self.assertFalse(
            _mod.seam_headline_claim_stands(run, ["OS-1"]))


if __name__ == "__main__":
    unittest.main()

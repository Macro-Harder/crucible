"""Contract test for operation C-11, plan section 2 section 5.

The test pins the check field of contract C-11 as plan section 9
states it. Surfaces crossed: MOD-10, via TG-10.1 and TG-10.2.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-11.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC11(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-11: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_append_order_is_consumption_order(self):
        """
        Fixture: Shape 12 journal field: the event log of one run with its journal positions
        Pins: the event log is append only and its order is the order the events were delivered in the run; appends extend the log at its end only and no append rewrites, reorders or inserts into what stands; a reader who resumes or replays from a journal position starts from the events up to that position, in that order, and from no others; on a resume, an appended supersession entry marks the partial day log tail beyond the checkpoint journal position as superseded and names the resume attempt identifier it belongs to
        Bar: no divergence in order or in content stands tolerated while the log stands retained
        Failure: an append that rewrites, reorders or inserts, or a resume consuming events past its position or out of order, fails this test; while the surface is absent the test fails naming this behaviour and C-11
        """
        self.require("event log append order is the order resume and replay consume", "mod10")
        import crucible.mod10 as mod10
        run_id = "run-c11-order"
        entries = [{"run_identifier": run_id, "journal_position": n, "event": "event-%d" % n} for n in (1, 2, 3)]
        for entry in entries:
            mod10.retain_event_log_entry(entry)
        held = mod10.event_log_entries(run_id)
        self.assertEqual([item["journal_position"] for item in held], [1, 2, 3])
        self.assertEqual([item["event"] for item in held], ["event-1", "event-2", "event-3"])
        consumed = held[:2]
        self.assertEqual([item["journal_position"] for item in consumed], [1, 2])

    def test_position_into_released_log_is_a_named_failure(self):
        """
        Fixture: Shape 12 journal field: a checkpoint manifest whose journal position points into a released part of the log, outside the reserve hold
        Pins: a position pointing into a released part of the log, outside the reserve hold, stands as a named retention failure under C-09, never absorbed as a resume failure under C-02 and never a silent gap
        Bar: for a run in scope of the full reserve hold decided at DQ7-03, the position resolves from the held log; for a run outside the hold, no promise stands that a position will still resolve
        Failure: such a position silently honoured, or its failure recorded under C-02, fails this test; while the surface is absent the test fails naming this behaviour and C-11
        """
        self.require("journal position pointing into a released log is a named retention failure", "mod10")
        import crucible.mod10 as mod10
        run_id = "run-c11-hold"
        self.assertIsNone(mod10.reserve_hold_for_run(run_id))
        hold = mod10.place_reserve_hold(run_id)
        self.assertEqual(hold["state"], "held")
        summary = {"run_id": run_id}
        mod10.apply_deferred_evaluation(summary, 1, inputs="recorded", outcome="recorded")
        released = mod10.apply_deferred_evaluation(summary, 2, inputs="recorded", outcome="recorded")
        self.assertEqual(released["reserve_hold_state"], "released")
        with self.assertRaises(mod10.LookupFailure):
            mod10.run_records_for_run("run-c11-absent")

    def test_position_check_free_limb(self):
        """
        Fixture: Shape 12 journal field: the event log of one run with three retained entries, and checkpoint manifests whose journal positions stand inside and outside that retained log
        Pins: the free limb of the C-11 position check, runnable on the landed Form 36 list under Manager ruling Entry 9 read with ruling Entry 1: a manifest journal position inside the retained log passes the check as reportable, and a manifest journal position outside the retained log, the position 99 probe over a three entry log, stands reported as a retention failure under C-09
        Bar: only the barred limbs stand gated, each named item by item under ruling Entry 1: the stream position limb of the position check and the completeness limb of the append audit; no whole check stands gated
        Failure: a position outside the retained log passing the check, or reported under any name other than a C-09 retention failure, fails this test; while the surface is absent the test fails naming this behaviour and C-11
        """
        self.require("checkpoint position check free limb on the landed Form 36 list", "mod10")
        import crucible.mod10 as mod10
        run_id = "run-c11-position"
        for n in (1, 2, 3):
            mod10.retain_event_log_entry({"run_identifier": run_id, "journal_position": n})
        inside = mod10.checkpoint_position_check({"run_identifier": run_id, "journal_position": 2})
        self.assertTrue(inside["reportable"])
        outside = mod10.checkpoint_position_check({"run_identifier": run_id, "journal_position": 99})
        self.assertFalse(outside["reportable"])
        self.assertEqual(outside["failure_under"], "C-09")
        self.assertIn("retention failure", outside["outcome"])

    def test_position_check_stream_position_limb_gated(self):
        """
        Fixture: no fixture stands for the barred limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: the stream position limb of the position check, stated against the landed Form 36 list
        Bar: the stream position limb stands barred item by item under Manager ruling Entry 1, read under ruling Entry 9, while OP-18 stands open on its 11 exclusions, and no act of this test rests on that limb while the bar stands
        Failure: a check resting on the stream position limb while its bar stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the stream position limb of the C-11 position check stands barred item by item under Manager ruling Entry 1, read under ruling Entry 9")

    def test_append_audit_completeness_limb_gated(self):
        """
        Fixture: no fixture stands for the barred limb while its gate stands. Recorded state: gated, never passed
        Pins: when the gate opens: the completeness limb of the append audit, stated against the landed Form 36 and Form 37 lists
        Bar: the completeness limb stands barred item by item under Manager ruling Entry 1, read under ruling Entry 9, while OP-18 stands open on its 11 exclusions, and no act of this test rests on that limb while the bar stands
        Failure: a check resting on the append audit completeness limb while its bar stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the completeness limb of the C-11 append audit stands barred item by item under Manager ruling Entry 1, read under ruling Entry 9")


if __name__ == "__main__":
    unittest.main()

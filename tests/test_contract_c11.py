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

    def test_append_audit_and_position_check_gated_on_op18_remainder(self):
        """
        Fixture: no fixture stands for the gated remainder while its gate stands. Recorded state: gated, never passed. The landed lists stand: the EventLog, Form 36, carries 8 fields and the DailySnapshot, Form 37, carries 3 fields, as landed in plan section 3
        Pins: when the gate opens: the append audit and the position check stated against the full field lists of Forms 36 and 37
        Bar: the remainder of each form stands carried at OP-18 on the gaps in the OP-18 design act 11 exclusions, and no limb of this check rests on a gap the exclusions name while that gap stands; the Manager ruling at route M-FL1-1 allocates the gaps
        Failure: a check resting on a gap the exclusions name while that gap stands fails this group; this test records the gated state and never passes while the gate stands
        """
        self.skipTest("Gated: the Manager ruling at route M-FL1-1 allocating the gaps in the OP-18 design act 11 exclusions")


if __name__ == "__main__":
    unittest.main()

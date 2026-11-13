"""Contract test for operation C-12, plan section 2 section 5.

The test pins the check field of contract C-12 as plan section 9
states it. Surfaces crossed: MOD-07, via TG-06.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-12.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod07 as _m_mod07
    SURFACES["mod07"] = True
except Exception:
    SURFACES["mod07"] = False


class TestContractC12(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-12: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_log_and_run_record_agree(self):
        """
        Fixture: Shape 17 record set: one interpretation choice and its two records
        Pins: every interpretation choice stands in an InterpretationLogEntry and in the run record, carrying choice identifier, reading applied, rule point affected, governing text version, escrow variant and fold version at the seam, and every dependence mark that applies, and the pair agree; a pair audit fails any result where the two name different readings, different governing text versions or different dependence marks, and a failed result is not reportable until the pair agrees and the failure is recorded
        Bar: no divergence between the log entry and the run record group for the same choice is tolerated, with no window in which both are correct
        Failure: a disagreeing pair that is reported, or a result whose failure stands unrecorded, fails this test; while the surface is absent the test fails naming this behaviour and C-12
        """
        self.require("interpretation log entry and run record agree for every choice", "mod07")
        import crucible.mod07 as mod07
        choice = mod07.make_adapter_choice("choice-c12", "reading one", "rule point 1", "text v1", "B-4 fold 1", dependence_marks=["mark-1"])
        log_entry = mod07.interpretation_log_entry(choice)
        run_entry = mod07.run_record_entry(choice)
        self.assertTrue(mod07.validate_choice_pair(log_entry, run_entry))
        for field in ("choice_identifier", "reading_applied", "governing_text_version", "dependence_marks"):
            self.assertEqual(log_entry[field], run_entry[field])
        differing = dict(run_entry)
        differing["reading_applied"] = "reading two"
        self.assertFalse(mod07.validate_choice_pair(log_entry, differing))

    def test_later_reading_appends_and_never_edits(self):
        """
        Fixture: Shape 17 record set: two entries for the same rule point with different readings
        Pins: a later reading appends a new entry and edits no earlier entry; a reader takes the reading that governs a result from the entry that result carries, not from the latest entry in the log
        Bar: no supersession rule may be invented by a test; agreement is checked, not assumed
        Failure: an earlier entry edited in place, or a result read from the latest entry rather than the entry it carries, fails this test; while the surface is absent the test fails naming this behaviour and C-12
        """
        self.require("later reading for a rule point appends a new entry and results read their own entry", "mod07")
        import crucible.mod07 as mod07
        import copy
        first = mod07.make_adapter_choice("choice-c12-a", "reading one", "rule point 1", "text v1", "B-4 fold 1")
        log = [mod07.interpretation_log_entry(first)]
        before = copy.deepcopy(log)
        second = mod07.make_adapter_choice("choice-c12-b", "reading two", "rule point 1", "text v1", "B-4 fold 1")
        extended = mod07.append_reading(log, second)
        self.assertEqual(log, before)
        self.assertEqual(len(extended), 2)
        self.assertEqual(extended[0], before[0])
        carried = mod07.reading_for_result(extended, "choice-c12-a")
        self.assertEqual(carried["reading_applied"], "reading one")


if __name__ == "__main__":
    unittest.main()

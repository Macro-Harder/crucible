"""Test group TG-10.2. Checkpoint storage accounting.

Slice S-10, MOD-10 Recorder and stores. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod10, and
records whether the surface stands. While the surface stands absent, each non
gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
The clause C10 formula stated form rested on here is the form the settlement
register Entry 7 states: retained checkpoints per run under clause C3,
multiplied by the runs in that row, summed over rows, with no copy term
stated. The copy term question stands open at that entry as item RM-6.
"""
import unittest

try:
    from crucible import mod10
    SURFACE = mod10
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-10.2"


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod10 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod10 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestCheckpointIsNotAResult(unittest.TestCase):
    def test_checkpoint_not_counted_as_result(self):
        """Fixture: a storage accounting run over a retained set containing summaries, snapshots, event logs, and checkpoints, as TG-10.2 states. Snapshot here names the DailySnapshot, Form 37.
        Pins: a checkpoint is never counted as a summary, a DailySnapshot snapshot, or an event log, per operation C-01.
        Bar: a retention total that counts a checkpoint as a result form fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, an accounting whose result counts include any checkpoint fails.
        """
        require_surface(self, "checkpoint never counted as a result form", "storage_accounting")
        retained = {"summaries": 2, "daily_snapshots": 3, "event_logs": 1, "checkpoints": 4}
        accounting = SURFACE.storage_accounting(retained)
        self.assertEqual(accounting["result_count"], 6)
        self.assertEqual(accounting["checkpoint_count"], 4)

    def test_retention_total_counting_checkpoint_fails(self):
        """Fixture: a retained set in its true form counts, summaries 2, daily snapshots 3, event logs 1, and checkpoints 4, presented with a claimed total of 7, a result count that counts one checkpoint, as TG-10.2 states.
        Pins: the accounting check rejects that claimed total, and the correct total of 6 for the same set stands accepted beside it as the control.
        Bar: a retention total that counts a checkpoint as a result form fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, acceptance of the claimed total of 7, or rejection of the correct total of 6, fails.
        """
        require_surface(self, "retention total counting a checkpoint rejected", "validate_storage_accounting")
        true_set = {"summaries": 2, "daily_snapshots": 3, "event_logs": 1, "checkpoints": 4}
        claimed = dict(true_set, result_count=7)
        self.assertFalse(SURFACE.validate_storage_accounting(claimed))
        control = dict(true_set, result_count=6)
        self.assertTrue(SURFACE.validate_storage_accounting(control))

    def test_no_checkpoint_byte_total_while_size_unsettled(self):
        """Fixture: a storage accounting run over a retained set containing checkpoints, as TG-10.2 states.
        Pins: no checkpoint byte total is stated while checkpoint size by population stands unsettled, per checkpoint clause C10.
        Bar: a sizing, storage, or cost statement carrying a checkpoint byte total in that standing fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, an accounting stating a checkpoint byte total fails.
        """
        require_surface(self, "no checkpoint byte total while size by population unsettled", "storage_accounting")
        retained = {"summaries": 0, "daily_snapshots": 0, "event_logs": 0, "checkpoints": 1}
        accounting = SURFACE.storage_accounting(retained)
        self.assertNotIn("checkpoint_bytes", accounting)
        self.assertNotIn("checkpoint_byte_total", accounting)


class TestC10FormulaStatedForm(unittest.TestCase):
    def test_c10_formula_stated_form(self):
        """Fixture: rows of a retained set, each row stating retained checkpoints per run under clause C3 and the runs in that row, in the stated form settlement register Entry 7 records.
        Pins: the retained stock count for a row is the per run count multiplied by the runs in that row, and the stock count over rows is the sum over rows; the stated form carries no copy term.
        Bar: no part of this test rests on the missing copy term; the corpus copy question stands open at settlement register Entry 7 as item RM-6.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, a count differing from the stated form on rows with no corpus copy fails.
        """
        require_surface(self, "clause C10 formula in its stated form", "checkpoint_count_c10")
        rows = [
            {"retained_per_run": 2, "runs": 3},
            {"retained_per_run": 1, "runs": 4},
        ]
        self.assertEqual(SURFACE.checkpoint_count_c10(rows), 10)

    def test_c10_corpus_copy_term_gated_on_rm6(self):
        """Fixture: a run whose checkpoint stands copied into the regression corpus, in the form settlement register Entry 7 states.
        Pins: no behaviour; this test records its state as gated on the missing term at settlement register Entry 7, item RM-6, clause C10 missing term standing open.
        Bar: no retained stock count for such a run is pinned until the settlement stands; the two readings in that entry give different counts and neither is chosen here.
        Failure: gated form only; this test never passes while item RM-6 stands open.
        """
        self.skipTest("gated on settlement register Entry 7 item RM-6: clause C10 copy term stands open")


class TestRetentionRuleRelianceStanding(unittest.TestCase):
    def test_retention_policy_table_carries_recorded_form(self):
        """Fixture: the retention policy table at slice S-10, as TG-10.2 states.
        Pins: the table carries the checkpoint retention rule recorded at DQ7-08, clauses C1 to C12, as its recorded form.
        Bar: while the reconciliation act for Plan Amendment stands unmade, no storage claim and no cost claim in this group rests on that rule as a decided rule, and the clause C12 bar stands unlifted for reliance.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, a table not carrying clauses C1 to C12 as its recorded form fails.
        """
        require_surface(self, "retention policy table carries clauses C1 to C12 as recorded form", "retention_policy_table")
        table = SURFACE.retention_policy_table()
        self.assertEqual(tuple(table["recorded_rule_clauses"]), tuple("C%d" % n for n in range(1, 13)))

    def test_presenting_dq708_rule_as_governing_fails(self):
        """Fixture: a sizing statement presenting the DQ7-08 rule as governing for reliance while the reconciliation gate stands, as TG-10.2 states.
        Pins: the statement fails validation in that standing.
        Bar: a sizing, storage, or cost statement presenting the DQ7-08 rule as governing for reliance while the gate stands fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.2; with the surface present, acceptance of the statement fails.
        """
        require_surface(self, "DQ7-08 rule presented as governing for reliance rejected", "validate_storage_claim")
        claim = {"basis": "DQ7-08", "reliance": "governing", "kind": "sizing"}
        self.assertFalse(SURFACE.validate_storage_claim(claim))


if __name__ == "__main__":
    unittest.main()

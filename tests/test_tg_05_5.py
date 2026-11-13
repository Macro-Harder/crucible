"""Test group TG-05.5, slice S-05, MOD-06 Escrow Core.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
Relation to the DQ7-04 exercise test paper: the paper at
design/steps/step-13-dq7-04-exercise-test-paper.md stands as a paper
with its own 20 exercise tests ET-01 to ET-20. The tests in this file
are the group tests of TG-05.5, written from the plan mapping. They
do not duplicate the exercise tests and are not the paper coverage.
"""
import unittest

try:
    from crucible import mod06 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG055(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-05.5: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_blank_form_integrity(self):
        """
        Fixture: F-22, the DQ arrival table
        Pins: the shipped form holds 26 rows, one per item from DQ-5 to DQ-30, with standings as the fixture states them: 3 exercised, 20 not exercised, 3 whose position cannot be told, and the final column of every row stands empty until the ruling for that item arrives, when the ruling text is entered there verbatim
        Bar: no row carries an expected answer, a favoured answer, or a placeholder value
        Failure: a form with a row count other than 26, standings other than the fixture standings, or any final column cell filled before its ruling arrives fails this test; while the surface is absent the test fails naming this behaviour and TG-05.5
        """
        self.require_surface("DQ arrival table holds 26 rows with fixture standings and an empty final column")
        rows = _mod.dq_arrival_table()
        self.assertEqual(len(rows), 26)
        self.assertEqual(
            [row["item"] for row in rows],
            ["DQ-" + str(number) for number in range(5, 31)])
        standings = {}
        for row in rows:
            standings[row["standing"]] = standings.get(row["standing"], 0) + 1
            self.assertEqual(row["final_column"], "")
        self.assertEqual(standings, {
            "exercised": 3, "not exercised": 20, "position cannot be told": 3})
        self.assertTrue(_mod.validate_dq_arrival_table(rows))

    def test_prefilled_final_column_fails(self):
        """
        Fixture: F-22, the DQ arrival table, with one final column cell pre filled
        Pins: a fixture or form that pre fills any final column cell is rejected, and no test encodes a guess at any item from DQ-5 to DQ-30
        Bar: a test fixture that pre fills any final column cell fails this group
        Failure: a pre filled cell that is accepted, or a guessed DQ answer encoded anywhere in the case, fails this test; while the surface is absent the test fails naming this behaviour and TG-05.5
        """
        self.require_surface("pre filled arrival table cell is rejected and no DQ answer is guessed")
        rows = _mod.dq_arrival_table()
        filled = [dict(row) for row in rows]
        filled[0]["final_column"] = "a guessed answer"
        self.assertFalse(_mod.validate_dq_arrival_table(filled))
        arrived = _mod.enter_ruling(rows, "DQ-5", "the ruling text, verbatim")
        target = [row for row in arrived if row["item"] == "DQ-5"][0]
        self.assertEqual(target["final_column"], "the ruling text, verbatim")
        self.assertEqual(rows[0]["final_column"], "")


if __name__ == "__main__":
    unittest.main()

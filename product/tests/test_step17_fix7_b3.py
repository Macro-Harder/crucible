"""Step 17 fix wave 7, Builder 3 defect tests (FW7-03, Low).

Row FW7-03 (rulings T17R6-03 and T17R6-04): the unbounded echo
family at two fresh doors. Door one: crucible.mod08.score handed
a mode value of 5,000 repetitions of one character refuses named
but renders the value whole in its refusal message; the filing
(Red 1, T17R6-R1-01) measures that message at 5,029 characters.
Door two: crucible.mod12.start_sweep handed a family_id of
100,000 characters renders the value whole in its refusal
fields; the filings (Red 2, S17R6-RED2-01, and Green 2,
G2R6-01, one locus counting once) measure the failure field at
100,175 characters, the ground_in_words field at 100,154
characters, and the whole refusal at 200,607 characters, with
the second handing form (a list carrying one text element of
100,000 characters) at a failure field of 100,177 characters.
Those counts stand beside the tests as the measure of the cure
owed, never as the verdict of any test.

The verdict of each defect test is the bound the cure states:
a handed value rendered at 120 characters beside a length
statement, and no refusal message or refusal field past the
600 character bound, each field of the start_sweep refusal
bounded in its own right. Outcomes stand judged by stored
value in code, never by a repr of a returned value (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

import crucible.mod08 as mod08
import crucible.mod12 as mod12

BOUND = 600
RENDERED = 120


class TestFW703Mod08ScoreModeEcho(unittest.TestCase):

    def test_defect_score_mode_huge_bounded(self):
        handed = "x" * 5000
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score([], mode=handed)
        message = str(caught.exception)
        self.assertLessEqual(len(message), BOUND)
        self.assertIn("bounded rendering", message)
        self.assertIn("5000", message)
        self.assertNotIn("x" * (RENDERED + 1), message)

    def test_defect_score_day_mode_huge_bounded(self):
        handed = "x" * 5000
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score_day([], mode=handed)
        message = str(caught.exception)
        self.assertLessEqual(len(message), BOUND)
        self.assertIn("bounded rendering", message)
        self.assertNotIn("x" * (RENDERED + 1), message)

    def test_control_score_mode_small_named(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score([], mode="bogus")
        message = str(caught.exception)
        self.assertEqual(
            message, "scoring mode stands unnamed: bogus")
        self.assertLessEqual(len(message), BOUND)


class TestFW703Mod12StartSweepFamilyIdEcho(unittest.TestCase):

    def _assert_refusal_bounded(self, refusal):
        self.assertLessEqual(len(refusal["failure"]), BOUND)
        self.assertLessEqual(len(refusal["ground_in_words"]), BOUND)
        self.assertIn("bounded rendering", refusal["failure"])
        self.assertIn("bounded rendering", refusal["ground_in_words"])
        self.assertIs(refusal["run_started"], False)
        self.assertIs(refusal["seed_drawn"], False)

    def test_defect_start_sweep_whitespace_huge_bounded(self):
        refusal = mod12.start_sweep(" " * 100000)
        self._assert_refusal_bounded(refusal)
        self.assertIn("100002", refusal["failure"])

    def test_defect_start_sweep_list_huge_bounded(self):
        refusal = mod12.start_sweep(["x" * 100000])
        self._assert_refusal_bounded(refusal)
        self.assertNotIn("x" * (RENDERED + 1), refusal["failure"])
        self.assertNotIn("x" * (RENDERED + 1),
                         refusal["ground_in_words"])

    def test_defect_start_sweep_text_huge_no_identifier_form(self):
        refusal = mod12.start_sweep("\t" * 100000)
        self._assert_refusal_bounded(refusal)

    def test_control_start_sweep_whitespace_small(self):
        refusal = mod12.start_sweep("   ")
        self.assertLessEqual(len(refusal["failure"]), BOUND)
        self.assertLessEqual(len(refusal["ground_in_words"]), BOUND)
        self.assertIn("'   '", refusal["failure"])
        self.assertIs(refusal["run_started"], False)
        self.assertIs(refusal["seed_drawn"], False)


class TestFW703Controls(unittest.TestCase):

    def test_control_start_run_family_id_huge_bounded(self):
        refusal = mod12.start_run("screening", " " * 100000)
        self.assertLessEqual(len(refusal["failure"]), BOUND)
        self.assertLessEqual(len(refusal["ground_in_words"]), BOUND)
        self.assertIn("bounded rendering", refusal["failure"])
        self.assertIs(refusal["run_started"], False)
        self.assertIs(refusal["seed_drawn"], False)

    def test_control_start_sweep_extra_keyword_carriage(self):
        refusal = mod12.start_sweep("fam1", **{"k" * 100000: 1})
        names = refusal["unexpected_keyword_handings"]
        self.assertEqual(len(names), 1)
        self.assertLessEqual(len(names[0]), BOUND)
        self.assertIn("bounded rendering", names[0])
        self.assertLessEqual(len(refusal["extra_handing_note"]), BOUND)
        self.assertIs(refusal["run_started"], False)
        self.assertIs(refusal["seed_drawn"], False)

    def test_control_start_run_extra_keyword_carriage(self):
        refusal = mod12.start_run(
            "screening", "fam1", **{"k" * 100000: 1})
        names = refusal["unexpected_keyword_handings"]
        self.assertEqual(len(names), 1)
        self.assertLessEqual(len(names[0]), BOUND)
        self.assertIn("bounded rendering", names[0])
        self.assertLessEqual(len(refusal["extra_handing_note"]), BOUND)
        self.assertIs(refusal["run_started"], False)
        self.assertIs(refusal["seed_drawn"], False)


if __name__ == "__main__":
    unittest.main()

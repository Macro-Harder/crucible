"""Step 15, second run, reconciliation tests.

Written test first for the two behaviour cures of the
reconciliation act: the R1-084 MOD-10 limb, where the gc08_record
lookup failure carries its sought identifier under the agreed
key run_identifier, and the exercise interaction cure, where the
headline unit the MOD-16 confirmation and headline exercise
builds from its driven run stands valid under the MOD-11 bars
(Field 10 marks and the plain scope and limits sentences).
"""
import unittest

from crucible import mod10, mod11, mod16


class TestR1084Gc08RunIdentifierKey(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_gc08_failure_carries_run_identifier(self):
        with self.assertRaises(mod10.LookupFailure) as caught:
            mod10.gc08_record("call_log", "owner-rec-1")
        failure = caught.exception.failure
        self.assertEqual(failure["name"], mod10.ONE_LOOKUP_FAILURE_NAME)
        self.assertEqual(failure["run_identifier"], "owner-rec-1")
        self.assertNotIn("owner_identifier", failure)
        self.assertEqual(failure["record_kind"], "call_log")

    def test_gc08_retained_record_still_reads_back(self):
        mod10.retain_gc08_record(
            "call_log", {"calls": []}, "owner-rec-2")
        self.assertEqual(
            mod10.gc08_record("call_log", "owner-rec-2"),
            {"calls": []})


class TestExerciseInteractionHeadlineUnit(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_driven_headline_unit_validates_under_mod11_bars(self):
        result = mod16.exercise_confirmation_and_headline()
        headline = result["headline"]
        self.assertTrue(headline["unit_built"])
        self.assertTrue(headline["exercised_end_to_end"])
        unit = headline["unit"]
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertTrue(mod11._field10_stands(
            unit["qualifiers_and_markings_block"]))
        self.assertTrue(mod11._has_plain_scope_limits_sentence(
            unit["claim_sentence"]))
        self.assertTrue(mod11._has_plain_scope_limits_sentence(
            unit["grounding_sentence"]))

    def test_confirmation_lineage_record_completed_form(self):
        result = mod16.exercise_confirmation_and_headline()
        confirmation = result["confirmation"]
        self.assertTrue(confirmation["exercised_end_to_end"])
        lineage = confirmation["settings_lineage_record"]
        self.assertIsInstance(lineage, dict)
        self.assertEqual(lineage["form"], "Form 32")
        self.assertTrue(lineage["completed"])


if __name__ == "__main__":
    unittest.main()

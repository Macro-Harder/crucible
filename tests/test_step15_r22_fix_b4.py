"""Pins for fix wave 22, builder b4, Group 4: MOD-10 vocabulary
family, rows R22-004 to R22-010 of the Round 22 register, on
coordinator Ruling A at step record Entry 212.

The defect: _vocabulary_text in crucible/mod10.py renders a non
text value through _safe_str, so a plain object stands named in
the sentence by its supplied string reading. The cure: a non
text value stands rendered as _stored_text renders it, its
stored text, empty for a value carrying no text form, never by
its supplied reading, at all seven loci, and the helper stated
form stands restated to match.

Distinguishing pins fail on the pristine basis and pass on the
cured copy. Control pins pass on both trees.
"""
import unittest

from crucible import mod10


class PlainReading:
    """A plain object carrying no text form in any form, whose
    string reading alone answers the stated name."""

    def __init__(self, reading):
        self._reading = reading

    def __str__(self):
        return self._reading


class RaisingPlain:
    """A plain object carrying no text form whose string
    reading raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")


class LyingStr(str):
    """A text value storing one text whose string reading
    answers another text."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie


class RaisingStr(str):
    """A text value storing one text whose string reading
    raises."""

    def __str__(self):
        raise RuntimeError("string reading raises")


def view_record(run_id, item, seen_day, viewer="viewer-1"):
    return {
        "run_identifier": run_id,
        "viewer_identifier": viewer,
        "simulated_day": 5,
        "scheduling_position_identifier": "s",
        "rule_version_set": "r",
        "view_contents": {},
        "reputation_and_band_values": {},
        "graph_position_as_seen": {},
        "first_seen_day_per_record": {item: seen_day},
        "delay_applied_per_record": {},
        "completeness_state": "complete",
        "building_component": "c",
        "delivering_contract": "d",
        "selection_rule_version": "v",
    }


class TestR22004RetainGc08Record(unittest.TestCase):

    def test_distinguishing_plain_object_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record(
                PlainReading("dependency_manifest"), {}, "owner-1")
        message = str(ctx.exception)
        self.assertIn("unknown GC-08 record kind: ;", message)
        self.assertNotIn(
            "unknown GC-08 record kind: dependency_manifest", message)

    def test_distinguishing_raising_plain_object_names_no_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record(RaisingPlain(), {}, "owner-1")
        self.assertIn(
            "unknown GC-08 record kind: ;", str(ctx.exception))

    def test_control_plain_kind_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record("bogus", {}, "owner-1")
        self.assertIn(
            "unknown GC-08 record kind: bogus;", str(ctx.exception))

    def test_control_lying_text_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_gc08_record(
                LyingStr("bogus-kind", "dependency_manifest"),
                {}, "owner-1")
        self.assertIn(
            "unknown GC-08 record kind: bogus-kind;",
            str(ctx.exception))


class TestR22005StoreLookup(unittest.TestCase):

    def test_distinguishing_plain_object_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k", store_kind=PlainReading("sweep"))
        message = str(ctx.exception)
        self.assertIn("unknown store kind: ;", message)
        self.assertNotIn("unknown store kind: sweep", message)

    def test_control_plain_kind_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(key="k", store_kind="bogus")
        self.assertIn(
            "unknown store kind: bogus;", str(ctx.exception))

    def test_control_raising_text_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(
                key="k", store_kind=RaisingStr("bogus-kind"))
        self.assertIn(
            "unknown store kind: bogus-kind;", str(ctx.exception))

    def test_control_bytes_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(key="k", store_kind=b"bogus")
        self.assertIn(
            "unknown store kind: bogus;", str(ctx.exception))


class TestR22006ApplyFlagOutcome(unittest.TestCase):

    def test_distinguishing_plain_object_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation(
                {}, outcome=PlainReading("promote"))
        message = str(ctx.exception)
        self.assertIn(
            "outside the stated vocabulary: ;", message)
        self.assertNotIn(
            "outside the stated vocabulary: promote", message)

    def test_control_plain_outcome_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation({}, outcome="bogus-outcome")
        self.assertIn(
            "outside the stated vocabulary: bogus-outcome;",
            str(ctx.exception))


class TestR22007ApplyFlagTier(unittest.TestCase):

    def test_distinguishing_plain_object_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation(
                {}, tier=PlainReading("Tier 1"))
        message = str(ctx.exception)
        self.assertIn(
            "tier outside the tiers the rule names: ;", message)
        self.assertNotIn(
            "tier outside the tiers the rule names: Tier 1", message)

    def test_control_plain_tier_names_plain_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation({}, tier="Tier 9")
        self.assertIn(
            "tier outside the tiers the rule names: Tier 9;",
            str(ctx.exception))

    def test_control_lying_text_tier_names_stored_text(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.apply_flag_evaluation(
                {}, tier=LyingStr("Tier 9", "Tier 1"))
        self.assertIn(
            "tier outside the tiers the rule names: Tier 9;",
            str(ctx.exception))


class TestR22008SummaryRecordForRun(unittest.TestCase):

    def test_distinguishing_plain_object_names_no_supplied_reading(self):
        result = mod10.summary_record_for_run(PlainReading("run-y"))
        self.assertEqual(
            result["statement"],
            "no summary record and no run record was found for run ")
        self.assertNotIn("run-y", result["statement"])

    def test_control_plain_identifier_named(self):
        result = mod10.summary_record_for_run("run-x")
        self.assertIn("for run run-x", result["statement"])


class TestR22009RunViewLeakCheckViewName(unittest.TestCase):

    def test_distinguishing_plain_run_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                PlainReading("run-fake"), "rec-1", 9))
        message = str(ctx.exception)
        self.assertIn("view /viewer-1", message)
        self.assertNotIn("run-fake", message)

    def test_distinguishing_plain_viewer_names_no_supplied_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", "rec-1", 9,
                viewer=PlainReading("viewer-fake")))
        message = str(ctx.exception)
        self.assertIn("view run-1/", message)
        self.assertNotIn("viewer-fake", message)

    def test_control_plain_view_named_in_failure(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(
                view_record("run-1", "rec-1", 9))
        self.assertIn("view run-1/viewer-1", str(ctx.exception))

    def test_control_plain_view_named_on_pass(self):
        result = mod10.run_view_leak_check(
            view_record("run-1", "rec-1", 3))
        self.assertEqual(result["view"], "run-1/viewer-1")
        self.assertTrue(result["reportable"])


class TestR22010RunViewLeakCheckRecordItem(unittest.TestCase):

    def test_distinguishing_plain_item_after_day_names_no_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", PlainReading("rec-fake"), 9))
        message = str(ctx.exception)
        self.assertIn("record  first seen after the view day", message)
        self.assertNotIn("rec-fake", message)

    def test_distinguishing_plain_item_nonfinite_names_no_reading(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(view_record(
                "run-1", PlainReading("rec-fake"), float("inf")))
        message = str(ctx.exception)
        self.assertIn(
            "record  states a day in a non finite form", message)
        self.assertNotIn("rec-fake", message)

    def test_control_plain_item_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.run_view_leak_check(
                view_record("run-1", "rec-1", 9))
        self.assertIn(
            "record rec-1 first seen after", str(ctx.exception))


class TestVocabularyHelperForm(unittest.TestCase):

    def test_distinguishing_helper_plain_object_stored_text_empty(self):
        self.assertEqual(
            mod10._vocabulary_text(PlainReading("sweep")), "")
        self.assertEqual(
            mod10._vocabulary_text(PlainReading("sweep")),
            mod10._stored_text(PlainReading("sweep")))

    def test_control_helper_text_and_buffer_forms(self):
        self.assertEqual(mod10._vocabulary_text("sweep"), "sweep")
        self.assertEqual(
            mod10._vocabulary_text(LyingStr("run-x", "run-y")),
            "run-x")
        self.assertEqual(mod10._vocabulary_text(b"bogus"), "bogus")


if __name__ == "__main__":
    unittest.main()

"""Step 16 fix wave 2, Builder 2 tests: rows F2-01 (family door limb),
F2-03, and F2-07, at the family judgements in MOD-01.

Written test first against the landed tree at product head
195c5d7bcb9c0a439f42a8d0924ecd8dff1136f5.
"""
import unittest

from crucible import mod01, mod12

PROSE = list(mod01.COMPLETENESS_FIELDS)
SLUGS = [slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS]
MARKER = "open: OP-13 value stands open"


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


class TestF201FamilyDoorExtraField(unittest.TestCase):
    def test_unnamed_extra_field_refused_and_named(self):
        record = mod12.make_family_record()
        record["zzz_unnamed_extra"] = "a value standing nowhere named"
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertIn("zzz_unnamed_extra", judgement.standing)
        self.assertIn("zzz_unnamed_extra", judgement.extra_fields)

    def test_unnamed_extra_field_refused_on_minimal_record(self):
        record = supplied_family()
        record["an_unnamed_field"] = "x"
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertIn("an_unnamed_field", judgement.standing)
        standing = mod01.family_reportable_standing(record)
        self.assertFalse(standing["supports_reportable_run"])
        self.assertIn("an_unnamed_field", standing["extra_fields"])
        self.assertIn("an_unnamed_field", standing["standing"])

    def test_made_record_only_carriage_keys_keeps_standing(self):
        record = mod12.make_family_record()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertFalse(judgement.truth_value)
        self.assertTrue(judgement.value)
        self.assertEqual(judgement.extra_fields, ())
        self.assertIn("open", judgement.standing)
        standing = mod01.family_reportable_standing(record)
        self.assertEqual(standing["extra_fields"], [])
        self.assertTrue(standing["completeness_bar_met"])


class TestF203PrototypeOrderBar(unittest.TestCase):
    def test_prototype_order_refused_at_family_door(self):
        record = mod12.make_family_record(
            scheduling_order_identifier="prototype order")
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertIn("scheduling_order_identifier", judgement.standing)
        self.assertIn("prototype order", judgement.standing)

    def test_prototype_order_refused_on_supplied_record(self):
        record = supplied_family()
        record["scheduling_order_identifier"] = "prototype order"
        self.assertFalse(mod01.validate_record("1", record))
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        standing = mod01.family_reportable_standing(record)
        self.assertFalse(standing["supports_reportable_run"])
        self.assertIn("prototype order", standing["standing"])

    def test_supplied_record_without_barred_order_passes(self):
        record = supplied_family()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertTrue(judgement)
        self.assertTrue(judgement.truth_value)


class TestF207StatedJudgementTruthValue(unittest.TestCase):
    def test_open_marker_truth_value_is_not_unqualified_true(self):
        record = mod01.minimal_valid_family_record()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertTrue(judgement.value)
        self.assertFalse(judgement.truth_value)
        self.assertFalse(judgement == True)  # noqa: E712
        self.assertTrue(judgement != True)  # noqa: E712
        self.assertIn("open", judgement.standing)
        as_dict = judgement.as_dict()
        self.assertFalse(as_dict["judgement"])
        self.assertTrue(as_dict["completeness_bar_met"])
        self.assertFalse(as_dict["reportable_ready"])

    def test_open_marker_standing_dict_truth_reflects_open(self):
        record = mod01.minimal_valid_family_record()
        standing = mod01.family_reportable_standing(record)
        self.assertFalse(standing["supports_reportable_run"])
        self.assertTrue(standing["completeness_bar_met"])
        self.assertEqual(
            standing["open_fields"], standing["open_fields"])
        self.assertTrue(standing["open_fields"])
        self.assertFalse(standing["reportable_ready"])

    def test_supplied_truth_value_stands_true(self):
        record = supplied_family()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertTrue(judgement.truth_value)
        self.assertTrue(judgement == True)  # noqa: E712
        self.assertTrue(judgement.as_dict()["judgement"])
        standing = mod01.family_reportable_standing(record)
        self.assertTrue(standing["supports_reportable_run"])
        self.assertTrue(standing["reportable_ready"])

    def test_bar_bool_still_holds_tg013_pin(self):
        record = mod01.minimal_valid_family_record()
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertFalse(judgement.truth_value)
        self.assertTrue(judgement.value)
        replaced = mod01.minimal_valid_family_record()
        replaced[PROSE[0]] = 1
        self.assertFalse(mod01.family_supports_reportable_run(replaced))


if __name__ == "__main__":
    unittest.main()

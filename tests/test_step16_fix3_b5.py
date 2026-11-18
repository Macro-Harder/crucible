"""Step 16 fix wave 3, Builder 5 tests.

Row F3-05 (Low, ruling T16-43): the completeness standing form
at the missing spelling edge.

The defect these tests pin: at the both spellings edge, where
one spelling of a completeness pair stands alone, the
judgements of the F2-09 cure agree, all answering False, but
completeness_standing names no field, its missing_fields and
absent_fields stand empty, and the affected field stands
listed under supplied_fields, so the standing handed to the
operator names nothing to fix and misstates the field
standing.

The cure bound these tests pin, in the ruling own terms: at
the both spellings edge, completeness_standing names the
affected field as not standing complete, in the missing
fields or in its standing sentence in the form the door uses
elsewhere, and the field does not stand listed as supplied on
that ground. The agreeing False judgements of the F2-09 cure
do not change, and the supplied and control cases keep their
standing forms.

Test first: the edge tests in
TestF305MissingSpellingStandingForm were written against the
landed product at head
c56ca7437a1c348340a21b5bf1e6ffc90c28244f and failed there for
the reason the row states; the guard tests in the same file
passed there and must keep passing.

Supplied completeness values in this file are test inputs
only, standing for no design value and adopted nowhere
(OP-16). No seed is drawn, read from a clock, or assigned in
completion order (DQ7-02). Bench Python 3.14.4 stands as the
interpreter basis.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


class TestF305MissingSpellingStandingForm(unittest.TestCase):
    def test_missing_brief_spelling_names_field_not_supplied(self):
        for prose in PROSE:
            record = supplied_family()
            del record[prose]
            with self.subTest(prose=prose):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])
                self.assertIn(prose, standing["missing_fields"])
                self.assertNotIn(prose, standing["supplied_fields"])
                self.assertIn(prose, standing["standing"])

    def test_missing_form_spelling_names_field_not_supplied(self):
        for prose, slug in zip(PROSE, SLUGS):
            record = supplied_family()
            del record[slug]
            with self.subTest(prose=prose):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])
                self.assertIn(prose, standing["missing_fields"])
                self.assertNotIn(prose, standing["supplied_fields"])
                self.assertIn(prose, standing["standing"])

    def test_missing_spelling_judgements_still_agree_false(self):
        for prose, slug in zip(PROSE, SLUGS):
            for dropped in (prose, slug):
                record = supplied_family()
                del record[dropped]
                with self.subTest(prose=prose, dropped=dropped):
                    self.assertFalse(
                        mod01.family_supports_reportable_run(record))
                    self.assertFalse(mod01.validate_record("1", record))
                    self.assertFalse(mod01.run_is_reportable("1", record))
                    stated = mod01.family_reportable_standing(record)
                    self.assertFalse(stated["supports_reportable_run"])
                    self.assertFalse(stated["reportable_ready"])
                    self.assertIn(prose, stated["missing_fields"])
                    self.assertNotIn(
                        prose, stated["supplied_fields"])

    def test_missing_spelling_entry_flags_stand(self):
        record = supplied_family()
        del record["farm size steps"]
        standing = mod01.completeness_standing(record)
        entry = standing["fields"][0]
        self.assertFalse(entry["brief_name_present"])
        self.assertTrue(entry["form_name_present"])
        record = supplied_family()
        del record["farm_size_steps"]
        standing = mod01.completeness_standing(record)
        entry = standing["fields"][0]
        self.assertTrue(entry["brief_name_present"])
        self.assertFalse(entry["form_name_present"])

    def test_missing_spelling_open_marker_sentence_names_field(self):
        for prose, slug in zip(PROSE, SLUGS):
            for dropped in (prose, slug):
                record = mod01.minimal_valid_family_record()
                del record[dropped]
                with self.subTest(prose=prose, dropped=dropped):
                    standing = mod01.completeness_standing(record)
                    self.assertFalse(
                        standing["complete_on_completeness_limb"])
                    self.assertNotIn(
                        prose, standing["supplied_fields"])
                    named = (
                        prose in standing["missing_fields"]
                        or prose in standing["standing"])
                    self.assertTrue(named)

    def test_both_spellings_supplied_standing_form_kept(self):
        record = supplied_family()
        standing = mod01.completeness_standing(record)
        self.assertTrue(standing["complete_on_completeness_limb"])
        self.assertTrue(standing["reportable_ready"])
        self.assertEqual(standing["missing_fields"], [])
        self.assertEqual(standing["absent_fields"], [])
        for prose in PROSE:
            self.assertIn(prose, standing["supplied_fields"])
        self.assertTrue(mod01.validate_record("1", record))
        self.assertTrue(mod01.family_supports_reportable_run(record))

    def test_field_missing_on_both_spellings_standing_kept(self):
        record = supplied_family()
        del record["farm size steps"]
        del record["farm_size_steps"]
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["missing_fields"])
        self.assertNotIn("farm size steps", standing["supplied_fields"])
        self.assertIn("farm size steps", standing["standing"])
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(mod01.validate_record("1", record))

    def test_diverged_pair_standing_kept(self):
        record = supplied_family()
        record["farm size steps"] = "a different supplied test value"
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["diverged_fields"])
        self.assertNotIn("farm size steps", standing["supplied_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(mod01.validate_record("1", record))

    def test_placeholder_pair_standing_kept(self):
        record = supplied_family()
        record["farm_size_steps"] = "stated value"
        record["farm size steps"] = "stated value"
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["placeholder_fields"])
        self.assertNotIn("farm size steps", standing["supplied_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(mod01.validate_record("1", record))


if __name__ == "__main__":
    unittest.main()

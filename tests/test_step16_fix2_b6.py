"""Step 16 fix wave 2, Builder 6 tests.

Rows F2-09 (Low, ruling T16-33) and F2-05 (Low, ruling T16-27).

F2-09: at the missing spelling edge the judgements read the one
completeness key set the same way. The shared reading these tests
pin: the two spellings carry one field, and a field stands
complete only where both of its spellings stand and agree, taking
the standing of the value they carry. Where one spelling alone
stands, the field stands named on its remaining spelling with
that spelling's standing, and the record stands incomplete on
the completeness limb for every judgement: completeness_standing
answers not complete, family_supports_reportable_run answers
False, validate_record answers False, and run_is_reportable
answers False. The reading is the one the completeness standing
and the family bar already apply, and the one the TG-01.3 pins
stand on; validate_record is the outlier the cure brings to it.
Test first: the edge tests in TestF209MissingSpellingEdge were
written against the landed product at head
195c5d7bcb9c0a439f42a8d0924ecd8dff1136f5 and failed there for the
reason the row states, validate_record answering True at the
edge; the guard tests in the same class passed there and must
keep passing.

F2-05: the surface guide in the README and in the package
docstring states the landed tree summed total of exported names,
computed here from the tree itself on the summed basis, the sum
of the fifteen module export lists, so the tests hold at whatever
figure the merged landed tree sums to. Test first: the census
tests failed on the landed tree, which states 641 against a
computed sum of 656.

Supplied completeness values in this file are test inputs only,
standing for no design value and adopted nowhere (OP-16). No seed
is drawn, read from a clock, or assigned in completion order
(DQ7-02). Bench Python 3.14.4 stands as the interpreter basis.

Copyright: J.P. Picard aka Macro-Harder.
"""
import importlib
import pathlib
import unittest

import crucible
from crucible import mod01

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)
MODULES = (
    "mod01", "mod02", "mod03", "mod04", "mod05", "mod06", "mod07",
    "mod08", "mod09", "mod10", "mod11", "mod12", "mod13", "mod14",
    "mod16",
)


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def summed_total():
    total = 0
    for name in MODULES:
        module = importlib.import_module("crucible." + name)
        total += len(module.__all__)
    return total


class TestF209MissingSpellingEdge(unittest.TestCase):
    def test_missing_brief_spelling_judgements_agree(self):
        record = supplied_family()
        del record["farm size steps"]
        standing = mod01.completeness_standing(record)
        entry = standing["fields"][0]
        self.assertEqual(entry["standing"], "supplied")
        self.assertFalse(entry["brief_name_present"])
        self.assertTrue(entry["form_name_present"])
        self.assertIn("farm size steps", standing["missing_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))
        self.assertFalse(mod01.run_is_reportable("1", record))
        stated = mod01.family_reportable_standing(record)
        self.assertFalse(stated["supports_reportable_run"])
        self.assertFalse(stated["reportable_ready"])

    def test_missing_brief_spelling_at_every_pair(self):
        for prose in PROSE:
            record = supplied_family()
            del record[prose]
            with self.subTest(prose=prose):
                self.assertFalse(
                    mod01.family_supports_reportable_run(record))
                self.assertFalse(mod01.validate_record("1", record))
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])

    def test_missing_brief_spelling_open_marker_form(self):
        record = mod01.minimal_valid_family_record()
        del record["farm size steps"]
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertIn("farm size steps", judgement.open_fields)
        self.assertFalse(mod01.validate_record("1", record))

    def test_both_spellings_supplied_still_pass(self):
        record = supplied_family()
        self.assertTrue(mod01.family_supports_reportable_run(record))
        self.assertTrue(mod01.validate_record("1", record))
        standing = mod01.completeness_standing(record)
        self.assertTrue(standing["complete_on_completeness_limb"])
        self.assertTrue(standing["reportable_ready"])

    def test_diverged_pair_still_refused(self):
        record = supplied_family()
        record["farm size steps"] = "a different supplied test value"
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["diverged_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])

    def test_field_missing_on_both_spellings_still_refused(self):
        record = supplied_family()
        del record["farm size steps"]
        del record["farm_size_steps"]
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["missing_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])

    def test_alias_spelling_alone_does_not_complete_the_field(self):
        record = supplied_family()
        del record["farm_size_steps"]
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])

    def test_placeholder_on_the_form_spelling_still_refused(self):
        record = supplied_family()
        record["farm_size_steps"] = "stated value"
        record["farm size steps"] = "stated value"
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["placeholder_fields"])
        self.assertFalse(standing["complete_on_completeness_limb"])


class TestF205GuideTotal(unittest.TestCase):
    def test_readme_states_the_summed_total_of_the_tree(self):
        total = summed_total()
        self.assertIn(
            "exporting %d names in total on the summed basis" % total,
            README)

    def test_docstring_states_the_summed_total_of_the_tree(self):
        total = summed_total()
        self.assertIn(
            "exporting %d names in total" % total, crucible.__doc__)

    def test_no_stale_total_stands_in_the_guide(self):
        self.assertNotIn("exporting 641 names", README)
        self.assertNotIn("exporting 641 names", crucible.__doc__)


if __name__ == "__main__":
    unittest.main()

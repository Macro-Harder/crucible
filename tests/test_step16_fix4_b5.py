"""Step 16 fix wave 4, Builder 5 tests.

Row F4-05 (Low, ruling T16-53): the completeness standing
unmet naming beside a diverged pair.

The defect these tests pin, as finding R4-RED5-N02 filed it:
in completeness_standing, a single spelling field standing
beside a diverged pair is named in neither missing_fields nor
the standing sentence, because the diverged branch of the
sentence computation preempts the widened unmet naming the
fix wave 3 cure (row F3-05, ruling T16-43) built into the
unmet branch. A single spelling field of the supplied kind
keeps its missing_fields placement from that cure but drops
out of the sentence; a single spelling field of the open
marker, placeholder, bare scalar, or absent kind stands in
its own kind bucket alone and is named in neither place.

The cure bound these tests pin, in ruling T16-53 own terms:
every unmet field in completeness_standing is named in
missing_fields and in the standing sentence, whether it
stands alone or beside a diverged pair. The alone field and
diverged pair cases name their fields exactly as the landed
cure already names them, and the guard tests below pin those
forms unchanged.

Test first: the beside diverged tests in
TestF405UnmetNamingBesideDivergedPair were written against
the landed product at head
1e1c33acdd33d2a8bdf081754cbca226a3ce355a and fail there for
the reason the row states; the guard tests in
TestF405LandedNamingKept passed there and must keep passing.
Bench runs of this file stand owed while the PC bench tunnel
stands closed, as the fix paper states in the open; no run
of this file ran on the VM.

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

TARGET = 1
DIVERGED = 0


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def diverged_family():
    record = supplied_family()
    record[PROSE[DIVERGED]] = "a different supplied test value"
    return record


def set_single_spelling(record, index, dropped, value):
    prose, slug = PROSE[index], SLUGS[index]
    if dropped == prose:
        del record[prose]
        record[slug] = value
    else:
        del record[slug]
        record[prose] = value
    return prose


def kind_value(kind, index):
    if kind == "supplied":
        return "supplied test value for " + SLUGS[index]
    if kind == "open marker":
        return mod01.minimal_valid_family_record()[PROSE[index]]
    if kind == "placeholder":
        return "stated value"
    if kind == "bare scalar":
        return 123
    if kind == "absent":
        return None
    raise AssertionError(kind)


KIND_BUCKET = {
    "open marker": "open_fields",
    "placeholder": "placeholder_fields",
    "bare scalar": "bare_scalar_fields",
    "absent": "absent_fields",
}


class TestF405UnmetNamingBesideDivergedPair(unittest.TestCase):
    def test_single_spelling_kinds_beside_diverged_named(self):
        for kind in ("supplied", "open marker", "placeholder",
                     "bare scalar", "absent"):
            for dropped in (PROSE[TARGET], SLUGS[TARGET]):
                record = diverged_family()
                prose = set_single_spelling(
                    record, TARGET, dropped, kind_value(kind, TARGET))
                with self.subTest(kind=kind, dropped=dropped):
                    standing = mod01.completeness_standing(record)
                    self.assertFalse(
                        standing["complete_on_completeness_limb"])
                    self.assertFalse(standing["reportable_ready"])
                    self.assertIn(prose, standing["missing_fields"])
                    self.assertIn(prose, standing["standing"])
                    self.assertNotIn(
                        prose, standing["supplied_fields"])
                    self.assertIn(
                        PROSE[DIVERGED], standing["diverged_fields"])
                    self.assertIn(
                        PROSE[DIVERGED], standing["standing"])
                    entry = standing["fields"][TARGET]
                    self.assertEqual(entry["standing"], kind)
                    if kind in KIND_BUCKET:
                        self.assertIn(
                            prose, standing[KIND_BUCKET[kind]])

    def test_supplied_single_spelling_beside_diverged_all_pairs(self):
        for index, prose in enumerate(PROSE):
            diverged_index = 0 if index != 0 else 1
            for dropped in (prose, SLUGS[index]):
                record = supplied_family()
                record[PROSE[diverged_index]] = (
                    "a different supplied test value")
                set_single_spelling(
                    record, index, dropped,
                    "supplied test value for " + SLUGS[index])
                with self.subTest(prose=prose, dropped=dropped):
                    standing = mod01.completeness_standing(record)
                    self.assertFalse(
                        standing["complete_on_completeness_limb"])
                    self.assertFalse(standing["reportable_ready"])
                    self.assertIn(prose, standing["missing_fields"])
                    self.assertIn(prose, standing["standing"])
                    self.assertNotIn(
                        prose, standing["supplied_fields"])
                    self.assertIn(
                        PROSE[diverged_index],
                        standing["diverged_fields"])
                    self.assertIn(
                        PROSE[diverged_index], standing["standing"])

    def test_missing_field_beside_diverged_named(self):
        record = diverged_family()
        del record[PROSE[TARGET]]
        del record[SLUGS[TARGET]]
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertIn(PROSE[TARGET], standing["missing_fields"])
        self.assertIn(PROSE[TARGET], standing["standing"])
        self.assertNotIn(PROSE[TARGET], standing["supplied_fields"])
        self.assertIn(PROSE[DIVERGED], standing["diverged_fields"])
        self.assertIn(PROSE[DIVERGED], standing["standing"])

    def test_family_reportable_standing_carries_beside_naming(self):
        record = diverged_family()
        prose = set_single_spelling(
            record, TARGET, PROSE[TARGET],
            kind_value("open marker", TARGET))
        stated = mod01.family_reportable_standing(record)
        self.assertFalse(stated["supports_reportable_run"])
        self.assertFalse(stated["reportable_ready"])
        self.assertIn(prose, stated["missing_fields"])
        self.assertIn(prose, stated["standing"])
        self.assertNotIn(prose, stated["supplied_fields"])


class TestF405LandedNamingKept(unittest.TestCase):
    def test_alone_supplied_single_spelling_naming_kept(self):
        for dropped in (PROSE[TARGET], SLUGS[TARGET]):
            record = supplied_family()
            prose = set_single_spelling(
                record, TARGET, dropped,
                "supplied test value for " + SLUGS[TARGET])
            with self.subTest(dropped=dropped):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertIn(prose, standing["missing_fields"])
                self.assertIn(prose, standing["standing"])
                self.assertNotIn(prose, standing["supplied_fields"])

    def test_alone_open_marker_single_spelling_naming_kept(self):
        record = supplied_family()
        prose = set_single_spelling(
            record, TARGET, PROSE[TARGET],
            kind_value("open marker", TARGET))
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertIn(prose, standing["open_fields"])
        self.assertIn(prose, standing["standing"])
        self.assertNotIn(prose, standing["missing_fields"])
        self.assertNotIn(prose, standing["supplied_fields"])

    def test_alone_other_kinds_single_spelling_naming_kept(self):
        for kind in ("placeholder", "bare scalar", "absent"):
            record = supplied_family()
            prose = set_single_spelling(
                record, TARGET, SLUGS[TARGET], kind_value(kind, TARGET))
            with self.subTest(kind=kind):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertIn(prose, standing[KIND_BUCKET[kind]])
                self.assertIn(prose, standing["standing"])
                self.assertNotIn(prose, standing["supplied_fields"])

    def test_diverged_pair_alone_naming_kept(self):
        record = diverged_family()
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertIn(PROSE[DIVERGED], standing["diverged_fields"])
        self.assertIn(PROSE[DIVERGED], standing["standing"])
        self.assertEqual(standing["missing_fields"], [])
        for prose in PROSE[1:]:
            self.assertIn(prose, standing["supplied_fields"])
            self.assertNotIn(prose, standing["standing"])

    def test_both_spellings_supplied_standing_kept(self):
        record = supplied_family()
        standing = mod01.completeness_standing(record)
        self.assertTrue(standing["complete_on_completeness_limb"])
        self.assertTrue(standing["reportable_ready"])
        self.assertEqual(standing["missing_fields"], [])
        self.assertEqual(standing["absent_fields"], [])
        for prose in PROSE:
            self.assertIn(prose, standing["supplied_fields"])

    def test_field_missing_on_both_spellings_alone_kept(self):
        record = supplied_family()
        del record[PROSE[TARGET]]
        del record[SLUGS[TARGET]]
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertIn(PROSE[TARGET], standing["missing_fields"])
        self.assertIn(PROSE[TARGET], standing["standing"])
        self.assertNotIn(PROSE[TARGET], standing["supplied_fields"])


if __name__ == "__main__":
    unittest.main()

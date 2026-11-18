"""Step 16 fix wave 4, Builder 2 tests.

Row F4-02 (Low, ruling T16-50): two limbs against the fix
wave 3 cure of ruling T16-41, as filed at Round 4 findings
R4-RED1-N03 and R4-RED1-N04.

Limb (a), N03: the open marker recognition at
_stands_open_marker_text in crucible/mod01.py reads any
folded text opening "open:" and carrying "op-13" anywhere
as a marker, so a supplied narrative that opens with the
word "open:" and mentions the OP-13 name in passing folds
to the open standing over recorded substance. The cure
bound of T16-50: open marker recognition is of the marker
vocabulary in folded form, whole and in place, not
substring presence anywhere in the text. The marker
vocabulary stands as the one marker text _OP13_MARKER,
"open: OP-13 value stands open".

Limb (b), N04: the placeholder scan at
family_record_presentation in crucible/mod12.py reads
every stored pair of the record, so a non completeness
field carrying placeholder text stands named in
placeholder_fields. The cure bound of T16-50:
placeholder_fields at the mod12 presentation scan names
completeness fields alone, the scan field set being the
completeness field set.

Test first: every defect test in this file was written
against the landed product at head
1e1c33acdd33d2a8bdf081754cbca226a3ce355a and stands to
fail there for the reason its name states, except the
genuine marker controls, which pass there and must keep
passing. Bench runs of this file stand owed while the PC
bench tunnel stands closed, as the builder paper states
in the open; no run of this file stood on the VM.

Supplied completeness values in this file are test inputs
only, standing for no design value and adopted nowhere
(OP-16). No seed is drawn, read from a clock, or assigned
in completion order (DQ7-02). Bench Python 3.14.4 stands
as the interpreter basis for every figure in the builder
paper (Carry 6).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod12

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)
PAIRS = list(zip(PROSE, SLUGS))

EXACT_MARKER = "open: OP-13 value stands open"

MARKER_DRESSES = (
    "Open: OP-13 value stands open",
    " open: OP-13 value stands open ",
    "OPEN:  OP-13  value stands open",
    "open: op-13 value stands open",
    "Open:\tOP-13\tvalue stands open",
)

NARRATIVE = (
    "open: a status note mentioning OP-13 in passing, with "
    "the recorded substance following after that mention "
    "for this field")

NARRATIVE_VARIANTS = (
    "open: OP-13",
    "open: OP-13 value stands open in full for this field",
    "Open: the OP-13 item stands open for review, and the "
    "recorded substance stands here",
    "open: op-13 value stands open, the recorded substance "
    "standing after the marker words",
)


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in PAIRS:
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def valued_family(value, pairs=None):
    record = supplied_family()
    for prose, slug in (pairs if pairs is not None else PAIRS):
        record[prose] = value
        record[slug] = value
    return record


class TestNarrativeNotOpenMarker(unittest.TestCase):
    def test_narrative_open_prefix_with_op13_in_body_reads_supplied(self):
        standing = mod01.completeness_standing(
            valued_family(NARRATIVE))
        self.assertEqual(tuple(standing["supplied_fields"]), PROSE)
        self.assertEqual(standing["open_fields"], [])
        self.assertTrue(standing["reportable_ready"])

    def test_narrative_variants_read_supplied(self):
        for value in NARRATIVE_VARIANTS:
            with self.subTest(value=value):
                standing = mod01.completeness_standing(
                    valued_family(value, pairs=PAIRS[:1]))
                self.assertEqual(
                    standing["fields"][0]["standing"], "supplied")
                self.assertNotIn(PROSE[0], standing["open_fields"])

    def test_helper_rejects_narrative_forms(self):
        for value in (NARRATIVE,) + NARRATIVE_VARIANTS:
            with self.subTest(value=value):
                self.assertFalse(mod01._stands_open_marker_text(value))


class TestGenuineMarkerStillMarker(unittest.TestCase):
    def test_exact_marker_reads_open(self):
        standing = mod01.completeness_standing(
            valued_family(EXACT_MARKER))
        self.assertEqual(tuple(standing["open_fields"]), PROSE)
        self.assertEqual(standing["supplied_fields"], [])
        self.assertFalse(standing["reportable_ready"])

    def test_dressed_marker_reads_open(self):
        for dress in MARKER_DRESSES:
            with self.subTest(dress=dress):
                standing = mod01.completeness_standing(
                    valued_family(dress, pairs=PAIRS[:1]))
                self.assertEqual(
                    standing["fields"][0]["standing"], "open marker")
                self.assertIn(PROSE[0], standing["open_fields"])

    def test_helper_accepts_folded_marker_forms(self):
        for dress in (EXACT_MARKER,) + MARKER_DRESSES:
            with self.subTest(dress=dress):
                self.assertTrue(mod01._stands_open_marker_text(dress))


class TestPresentationPlaceholderFieldSet(unittest.TestCase):
    def test_non_completeness_placeholder_not_named(self):
        record = supplied_family()
        record["operator_note_xyz"] = "stated value"
        presentation = mod12.family_record_presentation(record)
        self.assertNotIn(
            "operator_note_xyz", presentation["placeholder_fields"])
        self.assertEqual(presentation["placeholder_fields"], [])
        self.assertTrue(presentation["finished"])

    def test_non_completeness_placeholder_dresses_not_named(self):
        for dress in ("Stated Value", "STATED  VALUE", b"stated value"):
            with self.subTest(dress=dress):
                record = supplied_family()
                record["operator_note_xyz"] = dress
                presentation = mod12.family_record_presentation(record)
                self.assertNotIn(
                    "operator_note_xyz",
                    presentation["placeholder_fields"])
                self.assertEqual(presentation["placeholder_fields"], [])

    def test_completeness_placeholder_named_alone_beside_ordinary(self):
        record = valued_family("stated value", pairs=PAIRS[:1])
        record["operator_note_xyz"] = "stated value"
        presentation = mod12.family_record_presentation(record)
        self.assertEqual(
            presentation["placeholder_fields"], [PROSE[0]])
        self.assertFalse(presentation["finished"])


if __name__ == "__main__":
    unittest.main()

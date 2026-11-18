"""Step 16 fix wave 3, Builder 3 tests.

Row F3-03 (Medium, ruling T16-41): the folded placeholder and
open marker recognition. On the landed tree the placeholder
and open marker readings at completeness_standing in
crucible/mod01.py stand on exact text only, and the scan at
family_record_presentation in crucible/mod12.py stands on
exact text only, so dressed placeholder text and dressed
open markers read as supplied: the presentation stands
finished True with a supplied claim, the truth value reads
True, the record stands reportable, and the record seals,
over text that is the placeholder in dress. The Low limb of
Blue 4 finding B4-N3 folds into this row: in the mixed case
of a placeholder field beside an absent field, the
presentation standing text takes the awaiting supply branch
alone and states no placeholder standing.

Test first: every defect test in this file was written
against the landed product at head
c56ca7437a1c348340a21b5bf1e6ffc90c28244f and failed there
for the reason its name states, except the control tests,
which passed there and must keep passing.

The folding boundary these tests pin, stated in the open:
recognition reads the folded form of a value, case folded
and spacing folded (letter case disregarded, leading and
trailing spacing disregarded, and any run of spacing
between words read as the one space). No other character
stands folded away: a value that differs from the
placeholder or marker vocabulary in any other character,
in its words, or in its word order does not fold to that
vocabulary and keeps standing as supplied. The stored dress
readings the door already applies (a text value, a bytes
value, and a single part container) stand read before the
fold, as they stood.

Supplied completeness values in this file are test inputs
only, standing for no design value and adopted nowhere
(OP-16). No seed is drawn, read from a clock, or assigned
in completion order (DQ7-02). Bench Python 3.14.4 stands
as the interpreter basis for every figure in the builder
paper.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod12

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)
PAIRS = list(zip(PROSE, SLUGS))

PLACEHOLDER_DRESSES = (
    "Stated Value",
    "STATED VALUE",
    " stated value ",
    "stated  value",
    "Stated\tValue",
)

MARKER_DRESSES = (
    "Open: OP-13 value stands open",
    " open: OP-13 value stands open ",
    "OPEN:  OP-13  value stands open",
    "open: op-13 value stands open",
)

EXACT_MARKER = "open: OP-13 value stands open"


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in PAIRS:
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def dressed_family(value, pairs=None):
    record = supplied_family()
    for prose, slug in (pairs if pairs is not None else PAIRS):
        record[prose] = value
        record[slug] = value
    return record


class TestDressedPlaceholder(unittest.TestCase):
    def test_dressed_placeholder_all_fields_read_placeholder(self):
        for dress in PLACEHOLDER_DRESSES:
            with self.subTest(dress=dress):
                standing = mod01.completeness_standing(
                    dressed_family(dress))
                self.assertEqual(
                    tuple(standing["placeholder_fields"]), PROSE)
                self.assertEqual(standing["supplied_fields"], [])
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])

    def test_dressed_placeholder_presentation_not_finished(self):
        for dress in PLACEHOLDER_DRESSES:
            with self.subTest(dress=dress):
                presentation = mod12.family_record_presentation(
                    dressed_family(dress))
                self.assertFalse(presentation["finished"])
                self.assertIn(
                    "placeholder", presentation["standing"])
                self.assertNotIn(
                    "every completeness field stands supplied",
                    presentation["standing"])
                for prose in PROSE:
                    self.assertIn(
                        prose, presentation["placeholder_fields"])

    def test_dressed_placeholder_reportable_doors_refuse(self):
        for dress in PLACEHOLDER_DRESSES:
            with self.subTest(dress=dress):
                record = dressed_family(dress)
                judgement = mod01.family_supports_reportable_run(
                    record)
                self.assertFalse(judgement.truth_value)
                self.assertFalse(bool(
                    mod01.run_is_reportable("1", record)))
                self.assertFalse(
                    mod01.validate_record("1", record))

    def test_dressed_placeholder_record_does_not_seal(self):
        for dress in PLACEHOLDER_DRESSES:
            with self.subTest(dress=dress):
                with self.assertRaises(
                        mod12.NamedControllerFailure):
                    mod12.seal_family_record(dressed_family(dress))

    def test_single_dressed_placeholder_field_reads_placeholder(self):
        record = dressed_family("STATED VALUE", pairs=PAIRS[:1])
        standing = mod01.completeness_standing(record)
        self.assertEqual(
            standing["placeholder_fields"], [PROSE[0]])
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn("placeholder", presentation["standing"])
        self.assertIn(PROSE[0], presentation["placeholder_fields"])

    def test_dressed_placeholder_in_stored_dress(self):
        for stored in (b"STATED VALUE", ["Stated Value"]):
            with self.subTest(stored=stored):
                standing = mod01.completeness_standing(
                    dressed_family(stored))
                self.assertEqual(
                    tuple(standing["placeholder_fields"]), PROSE)
                self.assertEqual(standing["supplied_fields"], [])


class TestDressedOpenMarker(unittest.TestCase):
    def test_dressed_open_marker_reads_open_at_standing(self):
        for dress in MARKER_DRESSES:
            with self.subTest(dress=dress):
                standing = mod01.completeness_standing(
                    dressed_family(dress))
                self.assertEqual(
                    tuple(standing["open_fields"]), PROSE)
                self.assertEqual(standing["supplied_fields"], [])
                self.assertTrue(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])

    def test_dressed_open_marker_presentation_awaits_supply(self):
        for dress in MARKER_DRESSES:
            with self.subTest(dress=dress):
                presentation = mod12.family_record_presentation(
                    dressed_family(dress))
                self.assertFalse(presentation["finished"])
                self.assertIn(
                    "awaiting supply", presentation["standing"])
                for prose in PROSE:
                    self.assertIn(
                        prose,
                        presentation["awaiting_supply_fields"])

    def test_dressed_open_marker_truth_value_not_true(self):
        for dress in MARKER_DRESSES:
            with self.subTest(dress=dress):
                record = dressed_family(dress)
                judgement = mod01.family_supports_reportable_run(
                    record)
                self.assertFalse(judgement.truth_value)
                standing = mod01.family_reportable_standing(record)
                self.assertFalse(
                    standing["supports_reportable_run"])


class TestMixedPlaceholderStandingText(unittest.TestCase):
    def test_mixed_placeholder_and_absent_states_placeholder(self):
        record = dressed_family("stated value", pairs=PAIRS[:1])
        prose, slug = PAIRS[1]
        del record[prose]
        del record[slug]
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn(PROSE[0], presentation["placeholder_fields"])
        self.assertIn("placeholder", presentation["standing"])

    def test_mixed_dressed_placeholder_and_absent(self):
        record = dressed_family("Stated  Value", pairs=PAIRS[:1])
        prose, slug = PAIRS[1]
        del record[prose]
        del record[slug]
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn(PROSE[0], presentation["placeholder_fields"])
        self.assertIn("placeholder", presentation["standing"])

    def test_mixed_placeholder_and_open_marker_states_placeholder(self):
        record = supplied_family()
        record[PROSE[0]] = "stated value"
        record[SLUGS[0]] = "stated value"
        record[PROSE[1]] = EXACT_MARKER
        record[SLUGS[1]] = EXACT_MARKER
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn(PROSE[0], presentation["placeholder_fields"])
        self.assertIn("placeholder", presentation["standing"])
        self.assertIn("awaiting supply", presentation["standing"])


class TestPresentationScanFolded(unittest.TestCase):
    def test_presentation_names_dressed_placeholder_key(self):
        record = supplied_family()
        record["operator_note_xyz"] = "STATED VALUE"
        presentation = mod12.family_record_presentation(record)
        self.assertNotIn(
            "operator_note_xyz", presentation["placeholder_fields"])


class TestFoldingBoundaryControls(unittest.TestCase):
    def test_resembling_values_keep_supplied(self):
        for value in (
                "stated values",
                "stated-value",
                "statedvalue",
                "a stated value",
                "stated value in full for this field"):
            with self.subTest(value=value):
                standing = mod01.completeness_standing(
                    dressed_family(value))
                self.assertEqual(
                    tuple(standing["supplied_fields"]), PROSE)
                self.assertEqual(standing["placeholder_fields"], [])
                presentation = mod12.family_record_presentation(
                    dressed_family(value))
                self.assertTrue(presentation["finished"])

    def test_marker_resembling_values_keep_supplied(self):
        for value in (
                "opening: OP-13 value stands open",
                "open OP-13 value stands open",
                "open: OP-14 value stands open",
                "open: a supplied value"):
            with self.subTest(value=value):
                standing = mod01.completeness_standing(
                    dressed_family(value))
                self.assertEqual(
                    tuple(standing["supplied_fields"]), PROSE)
                self.assertEqual(standing["open_fields"], [])

    def test_exact_forms_and_supplied_keep_standing(self):
        standing = mod01.completeness_standing(
            dressed_family("stated value"))
        self.assertEqual(
            tuple(standing["placeholder_fields"]), PROSE)
        standing = mod01.completeness_standing(
            dressed_family(EXACT_MARKER))
        self.assertEqual(tuple(standing["open_fields"]), PROSE)
        presentation = mod12.family_record_presentation(
            supplied_family())
        self.assertTrue(presentation["finished"])


if __name__ == "__main__":
    unittest.main()

"""Step 16 fix wave 5, Builder 1 tests.

Row F5-01 (Low, ruling T16-60): the completeness standing
unmet naming beside a diverged pair, at the both spellings
present unmet kinds.

The defect these tests pin, as findings R5-RED2-N01 and
R5-RED5-N01 filed it together: in completeness_standing in
crucible/mod01.py, a field standing with both spellings
present in an unmet kind (both spellings carrying a
placeholder value, a bare scalar, or an absent value),
standing beside a diverged pair, is named in neither
missing_fields nor the standing sentence, while standing
alone the unmet branch of the sentence names it. Its bucket
placement puts it in its kind bucket alone, the beside
diverged missing_fields limb of the fix wave 4 cure fires
only where the field does not stand with both spellings
present, and the diverged branch of the sentence joins the
diverged fields and then appends only the clause naming the
fields whose spellings do not both stand present, so this
field satisfies neither join.

The cure bound these tests pin, in ruling T16-60 own terms
as settled from the cure bound of ruling T16-53: on a record
standing with a diverged pair, every field unmet on its own
standing (both spellings present carrying a placeholder,
bare scalar, or absent value, and any other unmet field)
and not already named is named in missing_fields and in
the standing sentence, in field order, beside the diverged
naming; the alone form and the pure diverged form keep
their standing wordings; no judgement changes; the naming
propagates through family_reportable_standing as
completeness_standing own consumer already carries it.

Test first: the beside diverged tests in
TestF501BothSpellingsUnmetBesideDiverged were written
against the cured from source, the landed product at head
44c50223031367e100155c2af4add565a2af16d1, and read as
failing on it by source reading for the reason the row
states; the guard tests in TestF501StandingFormsKept read
as passing on it and must keep passing. Bench runs of this
file stand owed while the PC bench tunnel stands closed,
as the fix paper states in the open; no run of this file
ran on the VM.

Supplied completeness values in this file are test inputs
only, standing for no design value and adopted nowhere
(OP-16). No seed is drawn, read from a clock, or assigned
in completion order (DQ7-02). Bench Python 3.14.4 stands
as the interpreter basis (Carry 6).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)

KIND_BUCKET = {
    "placeholder": "placeholder_fields",
    "bare scalar": "bare_scalar_fields",
    "absent": "absent_fields",
}

DIVERGED_SENTENCE = (
    "completeness standing diverged: the two spellings of "
    "the fields named carry different values, and the "
    "diverged state stands named rather than judged in "
    "silence: ")

UNMET_SENTENCE = (
    "completeness standing unmet: the fields named do not "
    "all stand present in an open marker or supplied form: ")


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def make_diverged(record, index, altered):
    prose, slug = PROSE[index], SLUGS[index]
    if altered == prose:
        record[prose] = "a different supplied test value"
    else:
        record[slug] = "a different supplied test value"
    return prose


def set_both_spellings(record, index, value):
    record[PROSE[index]] = value
    record[SLUGS[index]] = value
    return PROSE[index]


def kind_value(kind, index):
    if kind == "placeholder":
        return "stated value"
    if kind == "bare scalar":
        return 123
    if kind == "absent":
        return None
    raise AssertionError(kind)


class TestF501BothSpellingsUnmetBesideDiverged(unittest.TestCase):
    def check_both_spellings_unmet_beside_diverged(
            self, kind, value, target_index, diverged_index):
        for altered in (PROSE[diverged_index], SLUGS[diverged_index]):
            record = supplied_family()
            diverged = make_diverged(record, diverged_index, altered)
            prose = set_both_spellings(record, target_index, value)
            with self.subTest(
                    kind=kind, target=prose, diverged=diverged,
                    altered=altered):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])
                entry = standing["fields"][target_index]
                self.assertEqual(entry["standing"], kind)
                self.assertTrue(entry["brief_name_present"])
                self.assertTrue(entry["form_name_present"])
                self.assertIn(prose, standing[KIND_BUCKET[kind]])
                self.assertIn(prose, standing["missing_fields"])
                self.assertIn(prose, standing["standing"])
                self.assertNotIn(prose, standing["supplied_fields"])
                self.assertIn(diverged, standing["diverged_fields"])
                self.assertIn(diverged, standing["standing"])

    def test_both_spellings_placeholder_beside_diverged_named(self):
        for target_index, diverged_index in ((1, 0), (0, 1)):
            self.check_both_spellings_unmet_beside_diverged(
                "placeholder", kind_value("placeholder", target_index),
                target_index, diverged_index)

    def test_both_spellings_bare_scalar_beside_diverged_named(self):
        for target_index, diverged_index in ((1, 0), (0, 1)):
            self.check_both_spellings_unmet_beside_diverged(
                "bare scalar", kind_value("bare scalar", target_index),
                target_index, diverged_index)

    def test_both_spellings_absent_beside_diverged_named(self):
        for value in (None, "", []):
            for target_index, diverged_index in ((1, 0), (0, 1)):
                self.check_both_spellings_unmet_beside_diverged(
                    "absent", value, target_index, diverged_index)

    def test_both_spellings_unmet_beside_diverged_all_pairs(self):
        for index, prose in enumerate(PROSE):
            diverged_index = 0 if index != 0 else 1
            for kind in ("placeholder", "bare scalar", "absent"):
                record = supplied_family()
                make_diverged(
                    record, diverged_index, PROSE[diverged_index])
                set_both_spellings(
                    record, index, kind_value(kind, index))
                with self.subTest(prose=prose, kind=kind):
                    standing = mod01.completeness_standing(record)
                    self.assertFalse(
                        standing["complete_on_completeness_limb"])
                    self.assertFalse(standing["reportable_ready"])
                    self.assertIn(prose, standing["missing_fields"])
                    self.assertIn(prose, standing["standing"])
                    self.assertIn(
                        prose, standing[KIND_BUCKET[kind]])
                    self.assertNotIn(
                        prose, standing["supplied_fields"])
                    self.assertIn(
                        PROSE[diverged_index],
                        standing["diverged_fields"])

    def test_two_both_spellings_unmet_fields_named_in_field_order(self):
        record = supplied_family()
        make_diverged(record, 2, PROSE[2])
        set_both_spellings(record, 4, kind_value("absent", 4))
        set_both_spellings(record, 1, kind_value("placeholder", 1))
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertEqual(
            standing["missing_fields"], [PROSE[1], PROSE[4]])
        self.assertIn(PROSE[1], standing["standing"])
        self.assertIn(PROSE[4], standing["standing"])
        self.assertLess(
            standing["standing"].index(PROSE[1]),
            standing["standing"].index(PROSE[4]))
        self.assertIn(PROSE[1], standing["placeholder_fields"])
        self.assertIn(PROSE[4], standing["absent_fields"])
        self.assertIn(PROSE[2], standing["diverged_fields"])

    def test_other_unmet_fields_beside_both_spellings_unmet_named(self):
        record = supplied_family()
        make_diverged(record, 0, PROSE[0])
        set_both_spellings(record, 1, kind_value("placeholder", 1))
        del record[SLUGS[3]]
        del record[PROSE[4]]
        del record[SLUGS[4]]
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertEqual(
            standing["missing_fields"],
            [PROSE[1], PROSE[3], PROSE[4]])
        for index in (1, 3, 4):
            self.assertIn(PROSE[index], standing["standing"])
            self.assertNotIn(
                PROSE[index], standing["supplied_fields"])
        self.assertIn(PROSE[0], standing["diverged_fields"])
        self.assertIn(PROSE[0], standing["standing"])

    def test_family_reportable_standing_carries_both_spellings_naming(self):
        record = supplied_family()
        make_diverged(record, 0, SLUGS[0])
        prose = set_both_spellings(
            record, 1, kind_value("bare scalar", 1))
        stated = mod01.family_reportable_standing(record)
        self.assertFalse(stated["supports_reportable_run"])
        self.assertFalse(stated["reportable_ready"])
        self.assertIn(prose, stated["missing_fields"])
        self.assertIn(prose, stated["standing"])
        self.assertNotIn(prose, stated["supplied_fields"])


class TestF501StandingFormsKept(unittest.TestCase):
    def test_alone_both_spellings_unmet_naming_kept(self):
        for kind in ("placeholder", "bare scalar", "absent"):
            record = supplied_family()
            prose = set_both_spellings(
                record, 1, kind_value(kind, 1))
            with self.subTest(kind=kind):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertFalse(standing["reportable_ready"])
                entry = standing["fields"][1]
                self.assertEqual(entry["standing"], kind)
                self.assertIn(prose, standing[KIND_BUCKET[kind]])
                self.assertEqual(standing["missing_fields"], [])
                self.assertNotIn(prose, standing["supplied_fields"])
                self.assertEqual(
                    standing["standing"], UNMET_SENTENCE + prose)

    def test_pure_diverged_form_kept(self):
        record = supplied_family()
        make_diverged(record, 0, PROSE[0])
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertIn(PROSE[0], standing["diverged_fields"])
        self.assertEqual(standing["missing_fields"], [])
        self.assertEqual(
            standing["standing"], DIVERGED_SENTENCE + PROSE[0])
        for prose in PROSE[1:]:
            self.assertIn(prose, standing["supplied_fields"])
            self.assertNotIn(prose, standing["standing"])

    def test_diverged_with_spelling_unmet_form_kept(self):
        record = supplied_family()
        make_diverged(record, 0, PROSE[0])
        del record[PROSE[1]]
        standing = mod01.completeness_standing(record)
        self.assertFalse(standing["complete_on_completeness_limb"])
        self.assertFalse(standing["reportable_ready"])
        self.assertEqual(standing["missing_fields"], [PROSE[1]])
        self.assertEqual(
            standing["standing"],
            DIVERGED_SENTENCE + PROSE[0]
            + "; the fields named also do not stand with both "
            "spellings present, and stand named as not "
            "standing complete: " + PROSE[1])

    def test_both_spellings_supplied_standing_kept(self):
        record = supplied_family()
        standing = mod01.completeness_standing(record)
        self.assertTrue(standing["complete_on_completeness_limb"])
        self.assertTrue(standing["reportable_ready"])
        self.assertEqual(standing["missing_fields"], [])
        self.assertEqual(standing["absent_fields"], [])
        for prose in PROSE:
            self.assertIn(prose, standing["supplied_fields"])
        self.assertEqual(
            standing["standing"],
            "completeness standing supplied: every completeness "
            "field stands present with a supplied value")

    def test_alone_single_spelling_supplied_naming_kept(self):
        for dropped in (PROSE[1], SLUGS[1]):
            record = supplied_family()
            if dropped == PROSE[1]:
                del record[PROSE[1]]
            else:
                del record[SLUGS[1]]
            with self.subTest(dropped=dropped):
                standing = mod01.completeness_standing(record)
                self.assertFalse(
                    standing["complete_on_completeness_limb"])
                self.assertIn(PROSE[1], standing["missing_fields"])
                self.assertNotIn(
                    PROSE[1], standing["supplied_fields"])
                self.assertEqual(
                    standing["standing"], UNMET_SENTENCE + PROSE[1])


if __name__ == "__main__":
    unittest.main()

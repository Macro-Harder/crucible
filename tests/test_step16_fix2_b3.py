"""Step 16 fix wave 2, Builder 3 tests.

Rows F2-01 (seal limb, ruling T16-23) and F2-04 (ruling T16-30):
the inner door bypass at the mod12 seal check, at mod12
validate_family_record and family_record_validation_failures,
and at the mod11 validate_family_record third caller; and the
presentation of placeholder completeness values at mod12
family_record_presentation.

Test first: every defect test in this file was written against
the landed product at head 195c5d7bcb9c0a439f42a8d0924ecd8dff1136f5
and failed there for the reason its name states, except the
control tests, which passed there and must keep passing.

Supplied completeness values in this file are test inputs only,
standing for no design value and adopted nowhere (OP-16). No
seed is drawn, read from a clock, or assigned in completion
order (DQ7-02). Bench Python 3.14.4 stands as the interpreter
basis for every figure in the builder paper.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod11
from crucible import mod12

EXTRA = "totally_unnamed_field_xyz"

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)

EXPECTED_CARRIAGE_KEYS = (
    "family_id",
    "claims",
    "kill_checks",
    "family_version",
    "family_manifest_hash",
    "sealed",
    "registry_basis_fields",
    "results_seen",
    "form",
    "alias_keys",
    "completeness_presentation",
)


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def placeholder_family(pairs):
    record = supplied_family()
    for prose, slug in pairs:
        record[prose] = "stated value"
        record[slug] = "stated value"
    return record


class TestF201SealLimbExtraField(unittest.TestCase):
    def test_seal_refuses_and_names_extra_field(self):
        record = supplied_family()
        record[EXTRA] = "an unnamed field value"
        self.assertFalse(mod01.validate_record("1", record))
        with self.assertRaises(mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertIn(EXTRA, str(caught.exception))

    def test_family_failures_name_extra_field_and_validate_refuses(self):
        record = supplied_family()
        record[EXTRA] = "an unnamed field value"
        failures = mod12.family_record_validation_failures(record)
        self.assertTrue(
            any(EXTRA in failure for failure in failures), failures)
        self.assertFalse(mod12.validate_family_record(record))

    def test_mod11_validate_family_record_refuses_extra_field(self):
        record = supplied_family()
        record[EXTRA] = "an unnamed field value"
        self.assertFalse(mod11.validate_family_record(record))

    def test_carriage_key_enumeration_matches_made_record(self):
        record = mod12.make_family_record()
        form_side = set(mod01.form_fields("1"))
        form_side.update(mod01.COMPLETENESS_FIELDS)
        carried = tuple(sorted(
            key for key in record if key not in form_side))
        self.assertEqual(carried, tuple(sorted(EXPECTED_CARRIAGE_KEYS)))
        self.assertEqual(
            tuple(sorted(mod12.FAMILY_CARRIAGE_KEYS)),
            tuple(sorted(EXPECTED_CARRIAGE_KEYS)))

    def test_made_record_only_carriage_keys_keeps_seal_and_standing(self):
        record = mod12.make_family_record()
        self.assertEqual(
            mod12.family_record_validation_failures(record),
            ["the reportable run judgement stands refused"])
        self.assertFalse(mod12.validate_family_record(record))
        self.assertFalse(mod11.validate_family_record(record))
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_supplied_record_only_carriage_keys_keeps_standing(self):
        record = supplied_family()
        self.assertEqual(
            mod12.family_record_validation_failures(record), [])
        self.assertTrue(mod12.validate_family_record(record))
        self.assertTrue(mod11.validate_family_record(record))
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])


class TestF204PlaceholderPresentation(unittest.TestCase):
    def test_all_placeholder_completeness_presents_placeholder(self):
        record = placeholder_family(list(zip(PROSE, SLUGS)))
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn("placeholder", presentation["standing"])
        self.assertNotIn(
            "every completeness field stands supplied",
            presentation["standing"])
        for prose in PROSE:
            self.assertIn(prose, presentation["placeholder_fields"])

    def test_single_placeholder_completeness_presents_placeholder(self):
        record = placeholder_family([("farm size steps", "farm_size_steps")])
        presentation = mod12.family_record_presentation(record)
        self.assertFalse(presentation["finished"])
        self.assertIn("placeholder", presentation["standing"])
        self.assertNotIn(
            "every completeness field stands supplied",
            presentation["standing"])
        self.assertIn(
            "farm size steps", presentation["placeholder_fields"])

    def test_supplied_completeness_still_presents_finished(self):
        presentation = mod12.family_record_presentation(supplied_family())
        self.assertTrue(presentation["finished"])
        self.assertIn("supplied", presentation["standing"])

    def test_open_marker_made_record_still_awaits_supply(self):
        presentation = mod12.family_record_presentation(
            mod12.make_family_record())
        self.assertFalse(presentation["finished"])
        self.assertIn("awaiting supply", presentation["standing"])
        for prose in PROSE:
            self.assertIn(prose, presentation["awaiting_supply_fields"])


if __name__ == "__main__":
    unittest.main()

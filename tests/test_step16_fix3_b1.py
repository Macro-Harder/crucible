"""Step 16 fix wave 3, Builder 1 tests.

Row F3-01 (Medium, ruling T16-39): the family carriage
enumeration settlement. The eight seal and edit keys, the four
controller bar keys, and the standing of a record sealed by the
product own seal act and of an edited record produced by the
product own edit acts at the family doors.

Test first: every defect test in this file was written against
the landed product at head
c56ca7437a1c348340a21b5bf1e6ffc90c28244f and failed there for
the reason its name states, except the control tests, which
passed there and must keep passing.

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

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = tuple(slug for _prose, slug in mod01.COMPLETENESS_KEY_PAIRS)

SEAL_EDIT_KEYS = (
    "seal",
    "seal_version",
    "seal_hash",
    "sweep_manifest",
    "runs_under",
    "edited_after_seal",
    "identifier_changed",
    "runs_start_again",
)

CONTROLLER_BAR_KEYS = (
    "ecology_point",
    "amendment_landed",
    "data_dependent_top_up",
    "look_register",
)

BAR_VALUES = {
    "ecology_point": "open point",
    "amendment_landed": True,
    "data_dependent_top_up": "stated top up value",
    "look_register": ["one look"],
}


def supplied_family():
    record = mod12.make_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


def sealed_supplied():
    return mod12.seal_family_record(supplied_family())


class TestF301SealRefusesPreCarriedKeys(unittest.TestCase):

    def test_never_sealed_record_seal_keys_refused_and_named_at_seal(self):
        for key in SEAL_EDIT_KEYS:
            with self.subTest(key=key):
                record = supplied_family()
                record[key] = "planted value"
                with self.assertRaises(
                        mod12.NamedControllerFailure) as caught:
                    mod12.seal_family_record(record)
                self.assertIn(key, str(caught.exception))

    def test_controller_bar_keys_refused_and_named_at_seal_control(self):
        for key in CONTROLLER_BAR_KEYS:
            with self.subTest(key=key):
                record = supplied_family()
                record[key] = BAR_VALUES[key]
                with self.assertRaises(
                        mod12.NamedControllerFailure) as caught:
                    mod12.seal_family_record(record)
                self.assertIn(key, str(caught.exception))


class TestF301SealedAndEditedRecordsStand(unittest.TestCase):

    def test_sealed_record_keys_are_the_seal_act_keys(self):
        sealed = sealed_supplied()
        for key in ("seal", "seal_version", "seal_hash",
                    "sweep_manifest"):
            self.assertIn(key, sealed)

    def test_sealed_record_validates_at_mod12(self):
        sealed = sealed_supplied()
        self.assertEqual(
            mod12.family_record_validation_failures(sealed), [])
        self.assertTrue(mod12.validate_family_record(sealed))

    def test_sealed_record_validates_at_mod11(self):
        sealed = sealed_supplied()
        self.assertTrue(mod11.validate_family_record(sealed))

    def test_sealed_record_stands_at_family_doors(self):
        sealed = sealed_supplied()
        judgement = mod01.family_supports_reportable_run(sealed)
        self.assertTrue(judgement.truth_value)
        self.assertEqual(judgement.extra_fields, ())
        standing = mod01.family_reportable_standing(sealed)
        self.assertTrue(standing["supports_reportable_run"])
        self.assertEqual(standing["extra_fields"], [])
        self.assertTrue(mod01.run_is_reportable("1", sealed))

    def test_edited_record_validates_and_stands(self):
        edited = mod12.apply_family_edit(sealed_supplied())
        for key in ("runs_under", "edited_after_seal",
                    "identifier_changed", "runs_start_again"):
            self.assertIn(key, edited)
        self.assertEqual(
            mod12.family_record_validation_failures(edited), [])
        self.assertTrue(mod12.validate_family_record(edited))
        self.assertTrue(mod11.validate_family_record(edited))
        judgement = mod01.family_supports_reportable_run(edited)
        self.assertTrue(judgement.truth_value)
        self.assertEqual(judgement.extra_fields, ())
        self.assertTrue(mod01.run_is_reportable("1", edited))

    def test_unsealed_edit_record_stands(self):
        edited = mod12.apply_family_edit(supplied_family())
        self.assertIn("runs_under", edited)
        self.assertEqual(
            mod12.family_record_validation_failures(edited), [])
        self.assertTrue(mod12.validate_family_record(edited))
        self.assertTrue(mod11.validate_family_record(edited))
        self.assertTrue(
            mod01.family_supports_reportable_run(edited).truth_value)
        self.assertTrue(mod01.run_is_reportable("1", edited))

    def test_made_sealed_record_validates(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertEqual(
            mod12.family_record_validation_failures(sealed),
            ["the reportable run judgement stands refused"])
        self.assertFalse(mod12.validate_family_record(sealed))
        self.assertFalse(mod11.validate_family_record(sealed))
        judgement = mod01.family_supports_reportable_run(sealed)
        self.assertFalse(judgement)
        self.assertFalse(judgement.truth_value)
        self.assertTrue(judgement.value)
        run_judgement = mod01.run_is_reportable("1", sealed)
        self.assertFalse(run_judgement)
        self.assertFalse(run_judgement.truth_value)
        self.assertTrue(run_judgement.value)

    def test_edited_record_seals_again_and_validates(self):
        edited = mod12.apply_family_edit(sealed_supplied())
        resealed = mod12.seal_family_record(edited)
        self.assertTrue(resealed["sealed"])
        self.assertEqual(
            mod12.family_record_validation_failures(resealed), [])
        self.assertTrue(mod12.validate_family_record(resealed))
        self.assertTrue(mod11.validate_family_record(resealed))


class TestF301ValidationFailuresNameWiderKeys(unittest.TestCase):

    def test_failures_name_each_seal_edit_key_on_fresh_record(self):
        for key in SEAL_EDIT_KEYS:
            with self.subTest(key=key):
                record = supplied_family()
                record[key] = "planted value"
                failures = mod12.family_record_validation_failures(
                    record)
                self.assertTrue(
                    any(key in failure for failure in failures),
                    failures)
                self.assertFalse(
                    mod12.validate_family_record(record))

    def test_failures_name_each_controller_bar_key(self):
        for key in CONTROLLER_BAR_KEYS:
            with self.subTest(key=key):
                record = supplied_family()
                record[key] = BAR_VALUES[key]
                failures = mod12.family_record_validation_failures(
                    record)
                self.assertTrue(
                    any(key in failure for failure in failures),
                    failures)
                self.assertFalse(
                    mod12.validate_family_record(record))

    def test_family_doors_refuse_and_name_fresh_wider_keys(self):
        for key in SEAL_EDIT_KEYS + CONTROLLER_BAR_KEYS:
            with self.subTest(key=key):
                record = supplied_family()
                if key in BAR_VALUES:
                    record[key] = BAR_VALUES[key]
                else:
                    record[key] = "planted value"
                judgement = mod01.family_supports_reportable_run(
                    record)
                self.assertFalse(judgement.truth_value)
                self.assertIn(key, judgement.extra_fields)
                self.assertFalse(mod01.run_is_reportable("1", record))
                self.assertFalse(mod11.validate_family_record(record))


class TestF301SealCheckTextAndControls(unittest.TestCase):

    def test_seal_check_text_states_the_cured_act(self):
        doc = mod12.seal_family_record.__doc__
        self.assertIn("never been sealed", doc)
        self.assertIn("edited form", doc)

    def test_made_record_only_carriage_keys_keeps_standing_control(self):
        record = mod12.make_family_record()
        self.assertEqual(
            mod12.family_record_validation_failures(record),
            ["the reportable run judgement stands refused"])
        self.assertFalse(mod12.validate_family_record(record))
        self.assertFalse(mod11.validate_family_record(record))
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])

    def test_plain_extra_field_still_refused_everywhere_control(self):
        record = supplied_family()
        record["payload"] = "an unnamed field value"
        with self.assertRaises(mod12.NamedControllerFailure) as caught:
            mod12.seal_family_record(record)
        self.assertIn("payload", str(caught.exception))
        failures = mod12.family_record_validation_failures(record)
        self.assertTrue(
            any("payload" in failure for failure in failures),
            failures)
        self.assertFalse(mod12.validate_family_record(record))
        self.assertFalse(mod11.validate_family_record(record))
        self.assertFalse(
            mod01.family_supports_reportable_run(record).truth_value)
        self.assertFalse(mod01.run_is_reportable("1", record))


if __name__ == "__main__":
    unittest.main()

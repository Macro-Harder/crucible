"""Step 16 fix wave 2, Builder 5 tests for row F2-08, ruling T16-32.

Two limbs, neither folded into the other. Limb one, finding
R2-RED1-N05: build_run_record at Form 4 and the never fill seed
fields of FORM_FIELD_OWNERSHIP. Limb two, finding O3-N2:
build_sweep_point against FORM_FIELD_OWNERSHIP and form_fields
for Form 2. Every cure test in this file failed on the landed
product at head 195c5d7bcb9c0a439f42a8d0924ecd8dff1136f5 before
the cure; the guard tests pass before and after by design.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01

NEVER_FILL_4 = mod01.FORM_FIELD_OWNERSHIP["4"]["never_fill"]


class TestF208LimbOneRunRecordOwnership(unittest.TestCase):
    def test_built_record_carries_no_never_fill_fields(self):
        record = mod01.build_run_record()
        for field in NEVER_FILL_4:
            self.assertNotIn(field, record)

    def test_built_record_with_supplied_values_carries_no_never_fill(self):
        record = mod01.build_run_record(
            run_class="headline", sweep_identifier="sweep-b5")
        for field in NEVER_FILL_4:
            self.assertNotIn(field, record)

    def test_built_record_validates_true(self):
        record = mod01.build_run_record(run_class="headline")
        self.assertTrue(mod01.validate_record("4", record))

    def test_record_with_never_fill_field_filled_does_not_validate(self):
        for field in NEVER_FILL_4:
            record = mod01.build_run_record()
            record[field] = "stated value"
            self.assertFalse(mod01.validate_record("4", record), field)

    def test_never_fill_filling_is_named_in_failures(self):
        record = mod01.build_run_record()
        record["root_seed_reference"] = "stated value"
        failures = mod01.record_validation_failures("4", record)
        self.assertTrue(
            any("root_seed_reference" in entry for entry in failures),
            failures)

    def test_template_instance_carries_no_never_fill_and_validates(self):
        instance = mod01.minimal_valid_instance("4")
        for field in NEVER_FILL_4:
            self.assertNotIn(field, instance)
        self.assertTrue(mod01.validate_record("4", instance))

    def test_constructor_still_refuses_never_fill_by_name(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_run_record(root_seed_reference="seed-x")
        self.assertIn("DQ7-02", str(caught.exception))


class TestF208LimbTwoSweepPointOwnership(unittest.TestCase):
    def test_built_point_keys_match_form_fields_exactly(self):
        point = mod01.build_sweep_point()
        self.assertEqual(set(point), set(mod01.form_fields("2")))

    def test_built_point_carries_decay_slice(self):
        point = mod01.build_sweep_point()
        self.assertIn("decay_slice", point)

    def test_built_point_carries_no_unnamed_key(self):
        point = mod01.build_sweep_point()
        self.assertNotIn("belongs_to_decay_arm", point)

    def test_built_point_validates_true(self):
        point = mod01.build_sweep_point(point_identifier="point-b5")
        self.assertTrue(mod01.validate_record("2", point))

    def test_supplied_decay_slice_lands_with_no_second_name(self):
        point = mod01.build_sweep_point(decay_slice="slice-b5")
        self.assertEqual(point["decay_slice"], "slice-b5")
        self.assertEqual(set(point), set(mod01.form_fields("2")))
        self.assertTrue(mod01.validate_record("2", point))

    def test_built_point_keys_match_ownership_user_supplies(self):
        point = mod01.build_sweep_point()
        self.assertEqual(
            set(point),
            set(mod01.FORM_FIELD_OWNERSHIP["2"]["user_supplies"]))

    def test_template_instance_form2_still_validates(self):
        self.assertTrue(mod01.validate_record(
            "2", mod01.minimal_valid_instance("2")))


if __name__ == "__main__":
    unittest.main()

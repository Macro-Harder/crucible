"""Step 16 fix wave, builder 3: rows R16-01, R16-13, R16-17.

Test first tests for the three rows charged to builder 3 in
design/steps/step-16-r1-register.md, sections 5 and 6, rulings
T16-01, T16-13, and T16-17. Bench basis for every figure in the
fix paper: bench Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import os
import unittest

from crucible import mod01, mod04, mod12


# The full brief Shape to product Form mapping, enumerated first
# hand from the brief (Shapes 1 to 17, section 5.3), the plan
# census (plan section 3, Form entries 1 to 37 and Form 13A, and
# the one ahead rule of plan Amendment S12-013), and
# mod01.form_name. Shape 8 states two forms, so from Shape 9 the
# product Form number runs one ahead of the brief Shape number.
EXPECTED_SHAPE_TO_FORMS = {
    "1": ("1",),
    "2": ("2",),
    "3": ("3",),
    "4": ("4",),
    "5": ("5",),
    "6": ("6",),
    "7": ("7",),
    "8": ("8", "9"),
    "9": ("10",),
    "10": ("11",),
    "11": ("12",),
    "12": ("13",),
    "13": ("14",),
    "14": ("15",),
    "15": ("16",),
    "16": ("17",),
    "17": ("18",),
}

EXPECTED_FORM_TO_SHAPE = {}
for _shape, _forms in EXPECTED_SHAPE_TO_FORMS.items():
    for _form in _forms:
        EXPECTED_FORM_TO_SHAPE[_form] = _shape

# Forms carrying no numbered brief Shape of their own: Form 13A
# stands beside Form 13 in the checkpoint layer; Forms 19, 20,
# and 21 stand defined inside brief passages (Shape 7 and the
# Shape 16 passage) with no numbered Shape of their own; Forms
# 22 to 37 stand in layer three with no numbered Shape.
FORMS_WITH_NO_NUMBERED_SHAPE = (
    "13A", "19", "20", "21",
    "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37",
)

PLACEHOLDER_HASH_WORDING = (
    "manifest hash supplied as a record value, not computed")


class TestR1601ShapeFormCrossReference(unittest.TestCase):

    def test_registry_carries_full_shape_to_form_mapping(self):
        self.assertTrue(hasattr(mod01, "BRIEF_SHAPE_CROSS_REFERENCE"))
        reference = mod01.BRIEF_SHAPE_CROSS_REFERENCE
        for form_id, shape in EXPECTED_FORM_TO_SHAPE.items():
            entry = reference[form_id]
            self.assertEqual(entry["brief_shape"], shape)
            self.assertEqual(entry["form_name"], mod01.form_name(form_id))
            if shape == "8":
                # Shape 8 states two forms under one Shape name.
                self.assertIn(mod01.form_name(form_id), entry["brief_name"])
            else:
                self.assertEqual(
                    entry["brief_name"], mod01.form_name(form_id))
        for form_id in FORMS_WITH_NO_NUMBERED_SHAPE:
            self.assertIsNone(reference[form_id]["brief_shape"])

    def test_shape_lookup_answers_both_directions(self):
        for shape, forms in EXPECTED_SHAPE_TO_FORMS.items():
            self.assertEqual(mod01.form_ids_for_brief_shape(shape), forms)
        for form_id, shape in EXPECTED_FORM_TO_SHAPE.items():
            self.assertEqual(mod01.brief_shape_for_form(form_id), shape)
        for form_id in FORMS_WITH_NO_NUMBERED_SHAPE:
            self.assertIsNone(mod01.brief_shape_for_form(form_id))

    def test_brief_led_user_finds_checkpoint_manifest_at_form_13(self):
        # A user following the brief meets CheckpointManifest at
        # Shape 12. The product registry must tell that user, at
        # the registry itself, that the form answering Shape 12
        # is Form 13, and that Form 12 answers Shape 11
        # (DetectionState), so the wrong record is not built and
        # validated under the brief number in silence.
        self.assertEqual(mod01.form_ids_for_brief_shape("12"), ("13",))
        self.assertEqual(mod01.form_name("13"), "CheckpointManifest")
        self.assertEqual(mod01.brief_shape_for_form("13"), "12")
        self.assertEqual(mod01.form_name("12"), "DetectionState")
        self.assertEqual(mod01.brief_shape_for_form("12"), "11")
        self.assertEqual(mod01.form_ids_for_brief_shape("9"), ("10",))
        self.assertEqual(mod01.form_name("10"), "EscrowContractState")

    def test_readme_states_the_cross_reference(self):
        readme_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "README.md")
        with open(readme_path, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("Shape 12", text)
        self.assertIn("Form 13", text)
        self.assertIn("CheckpointManifest", text)
        self.assertIn("Shape 9", text)
        self.assertIn("Form 10", text)
        self.assertIn("EscrowContractState", text)


class TestR1613PrototypeOrderBar(unittest.TestCase):

    def _headline_run(self, order):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = order
        return record

    def _headline_family(self, order):
        record = mod12.make_family_record(
            "family-r16-13", ["headline claim 1"],
            scheduling_order_identifier=order)
        return record

    def test_brief_literal_fails_mod01_validation_and_reportable(self):
        record = self._headline_run("prototype order")
        self.assertFalse(mod01.validate_record("4", record))
        self.assertFalse(mod01.run_is_reportable("4", record))

    def test_brief_literal_fails_family_validation_and_reportable(self):
        record = self._headline_family("prototype order")
        self.assertFalse(mod01.validate_record("1", record))
        self.assertFalse(mod01.run_is_reportable("1", record))
        self.assertTrue(mod12.family_record_validation_failures(record))
        self.assertFalse(mod12.validate_family_record(record))

    def test_brief_literal_fails_mod04_order_checks(self):
        record = {"run_class": "headline",
                  "scheduling_order_identifier": "prototype order"}
        self.assertFalse(mod04.validate_run_scheduling_order(record))
        self.assertFalse(mod04.headline_order_stands(record))
        self.assertFalse(mod04.run_is_reportable(
            dict(record, projection_canary_passed=True)))

    def test_brief_literal_family_does_not_seal(self):
        record = self._headline_family("prototype order")
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_controls_standing_both_ways(self):
        fixed = self._headline_run("fixed order A")
        self.assertTrue(mod01.validate_record("4", fixed))
        self.assertTrue(mod04.validate_run_scheduling_order(
            {"run_class": "headline",
             "scheduling_order_identifier": "fixed order A"}))
        # The shortened code literal barred before this row stays
        # barred: no existing pin is weakened.
        short = self._headline_run("prototype")
        self.assertFalse(mod04.validate_run_scheduling_order(
            {"run_class": "headline",
             "scheduling_order_identifier": "prototype"}))
        self.assertFalse(mod01.validate_record("4", short))


class TestR1617SealDefects(unittest.TestCase):

    def test_seal_stands_no_seal_on_record_validation_rejects(self):
        record = mod12.make_family_record("family-r16-17")
        del record["headline_claims"]
        self.assertFalse(mod01.validate_record("1", record))
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_seal_stands_no_seal_on_diverged_record(self):
        record = mod12.make_family_record("family-r16-17-b")
        record["farm_size_steps"] = "a supplied list in text form"
        self.assertFalse(mod01.validate_record("1", record))
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(record)

    def test_seal_hash_field_states_the_hash_as_a_hash(self):
        record = mod12.make_family_record("family-r16-17-c")
        record["family_manifest_hash"] = "hash-abc-123"
        sealed = mod12.seal_family_record(record)
        self.assertEqual(sealed["seal"]["hash"], "hash-abc-123")
        self.assertEqual(sealed["seal_hash"], "hash-abc-123")
        self.assertEqual(
            sealed["sweep_manifest"]["sealed_family_record_hash"],
            "hash-abc-123")
        self.assertNotIn(PLACEHOLDER_HASH_WORDING, str(sealed["seal"]))
        self.assertNotIn(
            PLACEHOLDER_HASH_WORDING, str(sealed["sweep_manifest"]))

    def test_seal_with_no_hash_standing_states_none_stands(self):
        # The default made record carries only the placeholder
        # wording as its hash value. The seal output must not
        # present that wording as the hash: it states that no
        # hash value stands, in a standing field beside the hash.
        record = mod12.make_family_record("family-r16-17-d")
        sealed = mod12.seal_family_record(record)
        self.assertNotIn(PLACEHOLDER_HASH_WORDING, str(sealed["seal"]))
        self.assertNotIn(
            PLACEHOLDER_HASH_WORDING, str(sealed["sweep_manifest"]))
        self.assertIsNone(sealed["seal"]["hash"])
        self.assertIsNone(sealed["seal_hash"])
        self.assertEqual(
            sealed["seal"]["hash_standing"],
            "no hash value stands on the record; "
            "no hash stands computed by this seal")

    def test_control_valid_record_still_seals(self):
        record = mod12.make_family_record("family-r16-17-e")
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])


if __name__ == "__main__":
    unittest.main()

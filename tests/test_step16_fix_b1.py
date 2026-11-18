"""Step 16 Round 1 fix pins, Builder 1: R16-02, R16-14, R16-19.

Surfaces crossed: MOD-01 validate_record, the companion failure list
door record_validation_failures beside it, and
minimal_valid_instance.
Suite form: Python standard library unittest.
Values are simulated and test values only. No seed is drawn, read
from a clock, or assigned in completion order in any test here.

Adopted form, as the fix paper states in the open: validate_record
keeps its standing boolean answer, and the named failure stands
returned beside it by record_validation_failures, in the product
own list form at mod12 family_record_validation_failures. Each
failure sentence names the field, the rule, and the next step.
"""
import unittest

import crucible.mod01 as mod01


def _valid(form_id):
    return mod01.minimal_valid_instance(form_id)


class TestR1602NamedFailureForm(unittest.TestCase):
    """R16-02: a failing record draws a named failure stating the
    field, the rule, and the next step, in place of a bare False
    standing alone with no reason anywhere at the mod01 door."""

    def test_deleted_field_failure_names_the_field(self):
        instance = _valid("2")
        first = mod01.required_fields("2")[0]
        del instance[first]
        self.assertIs(mod01.validate_record("2", instance), False)
        failures = mod01.record_validation_failures("2", instance)
        self.assertTrue(failures)
        joined = " ".join(failures)
        self.assertIn(first, joined)
        self.assertIn("next step", joined)
        self.assertIn("stands refused", joined)
        self.assertIn("no record stands validated", joined)

    def test_deleted_field_failure_names_the_field_form_4(self):
        instance = _valid("4")
        first = mod01.required_fields("4")[0]
        del instance[first]
        failures = mod01.record_validation_failures("4", instance)
        self.assertTrue(failures)
        self.assertIn(first, " ".join(failures))

    def test_unknown_form_failure_names_the_identifier(self):
        self.assertIs(mod01.validate_record("99", _valid("2")), False)
        failures = mod01.record_validation_failures("99", {})
        self.assertTrue(failures)
        joined = " ".join(failures)
        self.assertIn("99", joined)
        self.assertIn("next step", joined)

    def test_mistyped_field_name_failure_names_the_field(self):
        instance = _valid("2")
        first = mod01.required_fields("2")[0]
        instance[first + "_typo"] = instance.pop(first)
        self.assertIs(mod01.validate_record("2", instance), False)
        failures = mod01.record_validation_failures("2", instance)
        self.assertIn(first, " ".join(failures))

    def test_mistyped_value_failure_names_the_field(self):
        instance = _valid("22")
        instance["outcome"] = "bogus outcome value"
        self.assertIs(mod01.validate_record("22", instance), False)
        failures = mod01.record_validation_failures("22", instance)
        joined = " ".join(failures)
        self.assertIn("outcome", joined)
        self.assertIn("next step", joined)

    def test_non_record_failure_names_the_record_form(self):
        self.assertIs(mod01.validate_record("2", None), False)
        failures = mod01.record_validation_failures("2", None)
        self.assertTrue(failures)
        self.assertIn("next step", " ".join(failures))

    def test_valid_record_still_returns_true(self):
        for form_id in ("1", "2", "3", "4", "6", "13", "14", "36"):
            with self.subTest(form_id=form_id):
                self.assertIs(
                    mod01.validate_record(form_id, _valid(form_id)), True)
                self.assertEqual(
                    mod01.record_validation_failures(
                        form_id, _valid(form_id)), [])

    def test_failure_sentence_frame(self):
        failures = mod01.record_validation_failures("2", {})
        self.assertTrue(failures)
        for failure in failures:
            self.assertTrue(
                failure.startswith("validate_record stands refused: field "))
            self.assertIn("; next step: ", failure)
            self.assertTrue(
                failure.endswith(", and no record stands validated"))

    def test_docstring_states_operator_terms(self):
        doc = mod01.validate_record.__doc__ or ""
        self.assertIn("field", doc)
        self.assertIn("next step", doc)
        self.assertIn("record_validation_failures", doc)
        self.assertNotIn("_validate_record_inner", doc)
        self.assertNotIn("traversal bound", doc)
        self.assertNotIn("recursion", doc.lower())


class TestR1614ExtraFieldBlindness(unittest.TestCase):
    """R16-14: an instance carrying a field the form does not name
    stands refused, with the extra field named in the failure,
    across forms."""

    def test_extra_field_refused_across_forms(self):
        for form_id in ("1", "2", "3", "4", "6", "12", "13", "14", "22"):
            with self.subTest(form_id=form_id):
                instance = _valid(form_id)
                instance["zzzz_extra_field_not_in_form"] = 1
                self.assertIs(
                    mod01.validate_record(form_id, instance), False)

    def test_extra_field_named_in_the_failure(self):
        for form_id in ("2", "4", "13"):
            with self.subTest(form_id=form_id):
                instance = _valid(form_id)
                instance["zzzz_extra_field_not_in_form"] = 1
                failures = mod01.record_validation_failures(
                    form_id, instance)
                self.assertIn(
                    "zzzz_extra_field_not_in_form", " ".join(failures))

    def test_minimal_instances_carry_no_extra_field(self):
        for form_id in mod01.FORM_IDS:
            with self.subTest(form_id=form_id):
                self.assertEqual(
                    mod01.record_validation_failures(
                        form_id, _valid(form_id)), [])
                self.assertIs(
                    mod01.validate_record(form_id, _valid(form_id)), True)


class TestR1619UnknownFormTemplate(unittest.TestCase):
    """R16-19: minimal_valid_instance on an identifier naming no
    form raises a named failure in place of a silent empty dict."""

    def test_unknown_identifiers_raise_naming_the_identifier(self):
        for bad in ("99", "0", "abc", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as caught:
                    mod01.minimal_valid_instance(bad)
                message = str(caught.exception)
                self.assertIn("names no form", message)
                self.assertIn("no instance stands built", message)
                if bad:
                    self.assertIn(bad, message)

    def test_none_identifier_raises(self):
        with self.assertRaises(ValueError):
            mod01.minimal_valid_instance(None)

    def test_known_identifiers_still_build(self):
        for form_id in ("1", "2", "4", "36"):
            with self.subTest(form_id=form_id):
                instance = mod01.minimal_valid_instance(form_id)
                self.assertIsInstance(instance, dict)
                self.assertTrue(instance)


if __name__ == "__main__":
    unittest.main()

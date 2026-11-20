"""Step 17 fix wave 4, Slice 4 defect tests: the mod01
identifier and statement rows FW4-06, FW4-19, and FW4-21.

FW4-06: minimal_valid_instance and form_ids_for_brief_shape
refuse a non text identifier handing in the true ground form
the sibling doors state, naming the handing form and the
text standing of an identifier, and no door states that a
standing form or shape does not stand.
FW4-19: the docstring of form_ids_for_brief_shape states the
raising form the act and its pin carry.
FW4-21: the stated surfaces at Form 1 name the alias
exception, at the README template sentence and at the
validate_record True sentence.

Copyright: J.P. Picard aka Macro-Harder.
"""
import os
import unittest

from crucible import mod01


class TestFW406NonTextIdentifierGround(unittest.TestCase):

    def test_minimal_instance_int_states_non_text_ground(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.minimal_valid_instance(2)
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("int form", text)
        self.assertIn("stands as text", text)
        self.assertNotIn("names no form", text)

    def test_minimal_instance_bool_states_non_text_ground(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.minimal_valid_instance(True)
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("bool form", text)
        self.assertNotIn("names no form", text)

    def test_minimal_instance_list_states_non_text_ground(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.minimal_valid_instance(["2"])
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("list form", text)
        self.assertNotIn("names no form", text)

    def test_form_ids_int_shape_states_non_text_ground(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_ids_for_brief_shape(9)
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("int form", text)
        self.assertIn("stands as text", text)
        self.assertNotIn("names no numbered brief Shape", text)

    def test_form_ids_float_shape_states_non_text_ground(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_ids_for_brief_shape(2.5)
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("float form", text)
        self.assertNotIn("names no numbered brief Shape", text)

    def test_control_text_identifier_still_answers(self):
        instance = mod01.minimal_valid_instance("2")
        self.assertIsInstance(instance, dict)
        self.assertEqual(
            mod01.form_ids_for_brief_shape("9"), ("10",))

    def test_control_unknown_text_form_ground_unchanged(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.minimal_valid_instance("99")
        self.assertIn("names no form", str(ctx.exception))

    def test_control_unknown_text_shape_ground_unchanged(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_ids_for_brief_shape("99")
        text = str(ctx.exception)
        self.assertIn("names no numbered brief Shape", text)
        self.assertIn("next step", text)

    def test_control_sibling_door_ground_unchanged(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.brief_shape_for_form(2)
        text = str(ctx.exception)
        self.assertIn("non text form", text)
        self.assertIn("int form", text)


class TestFW419DocstringStatesRaisingForm(unittest.TestCase):

    def test_docstring_states_raising_form(self):
        doc = " ".join(
            mod01.form_ids_for_brief_shape.__doc__.split())
        self.assertNotIn("returns an empty tuple", doc)
        self.assertIn("refused", doc)
        self.assertIn("names no numbered brief Shape", doc)
        self.assertIn("next step", doc)

    def test_control_behaviour_raises_named_form(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_ids_for_brief_shape("99")
        text = str(ctx.exception)
        self.assertIn("names no numbered brief Shape", text)
        self.assertIn("next step", text)

    def test_control_true_shape_serves_whole(self):
        self.assertEqual(
            mod01.form_ids_for_brief_shape("8"), ("8", "9"))


class TestFW421AliasExceptionNamed(unittest.TestCase):

    def _readme_text(self):
        root = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))
        with open(os.path.join(root, "README.md"),
                  encoding="utf-8") as handle:
            return handle.read()

    def test_readme_template_sentence_names_alias_exception(self):
        readme = self._readme_text()
        self.assertIn("alias exception", readme)
        self.assertIn("spaced", readme)
        self.assertIn("Form 1", readme)

    def test_validate_true_sentence_names_alias_exception(self):
        doc = mod01.validate_record.__doc__
        self.assertIn("alias", doc)
        self.assertIn("Form 1", doc)
        self.assertIn("spaced", doc)

    def test_control_template_standing_counts(self):
        fields = mod01.form_fields("1")
        instance = mod01.minimal_valid_instance("1")
        self.assertEqual(len(fields), 18)
        self.assertEqual(len(instance), 24)
        extra = [key for key in instance if key not in fields]
        self.assertEqual(len(extra), 6)
        for key in extra:
            self.assertIn(" ", key)

    def test_control_alias_instance_validates_true(self):
        instance = mod01.minimal_valid_instance("1")
        self.assertTrue(mod01.validate_record("1", instance))
        self.assertEqual(
            mod01.record_validation_failures("1", instance), [])


if __name__ == "__main__":
    unittest.main()

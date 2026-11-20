"""Step 17 fix wave 4, Slice 8 defect tests for rows FW4-11,
FW4-15, and FW4-20.

FW4-11: the README named entry points in mod01 and mod10, and
the top level re-export, deliver a missing or extra argument
handing in the named form of their module, stating the door,
the ground, and the next step, in the form the FW3-54 cure
states at its cured acts, and never as bare interpreter text
of the form "missing 1 required positional argument" or
"takes 2 positional arguments but 3 were given".

FW4-15: the README surface guide and user entry point list
name record_validation_failures beside validate_record as
the act that states the reasons for a failing validation.

FW4-20: a stated surface of the product, at the README record
form table and at the derivation act, names the Form 5 record
and the derivation input as different shapes and states the
field name mapping between them.
"""
import os
import unittest

import crucible
from crucible import mod01, mod02, mod10


def bare_escape(exc):
    text = str(exc)
    return ("required positional argument" in text
            or "positional arguments but" in text
            or "got an unexpected keyword" in text
            or "takes 0 positional" in text)


def readme_text():
    root = os.path.dirname(os.path.dirname(
        os.path.abspath(crucible.__file__)))
    with open(os.path.join(root, "README.md"), encoding="utf-8") as fh:
        return fh.read()


class NamedFormMixin:
    def assert_named(self, door, fn):
        with self.assertRaises(ValueError) as caught:
            fn()
        text = str(caught.exception)
        self.assertFalse(bare_escape(caught.exception), text)
        self.assertIn(door + " stands refused", text)
        self.assertIn("next step", text)


class TestFW411Mod01(NamedFormMixin, unittest.TestCase):
    def test_defect_validate_record_missing(self):
        self.assert_named("validate_record",
                          lambda: mod01.validate_record())

    def test_defect_validate_record_missing_record(self):
        self.assert_named("validate_record",
                          lambda: mod01.validate_record("2"))

    def test_defect_validate_record_extra_positional(self):
        record = mod01.minimal_valid_instance("2")
        self.assert_named(
            "validate_record",
            lambda: mod01.validate_record("2", record, "extra"))

    def test_defect_validate_record_extra_keyword(self):
        record = mod01.minimal_valid_instance("2")
        self.assert_named(
            "validate_record",
            lambda: mod01.validate_record("2", record, bogus=1))

    def test_defect_minimal_valid_instance_missing(self):
        self.assert_named("minimal_valid_instance",
                          lambda: mod01.minimal_valid_instance())

    def test_defect_minimal_valid_instance_extra(self):
        self.assert_named(
            "minimal_valid_instance",
            lambda: mod01.minimal_valid_instance(
                "2", None, None, "extra"))

    def test_defect_minimal_valid_family_record_extra(self):
        self.assert_named(
            "minimal_valid_family_record",
            lambda: mod01.minimal_valid_family_record("extra"))

    def test_defect_minimal_valid_family_record_extra_keyword(self):
        self.assert_named(
            "minimal_valid_family_record",
            lambda: mod01.minimal_valid_family_record(bogus=1))

    def test_defect_top_level_validate_record_missing(self):
        self.assert_named("validate_record",
                          lambda: crucible.validate_record())

    def test_control_mod01_entry_points_serve_whole(self):
        record = mod01.minimal_valid_instance("2")
        self.assertTrue(mod01.validate_record("2", record))
        self.assertTrue(crucible.validate_record("2", record))
        family = mod01.minimal_valid_family_record()
        self.assertTrue(mod01.validate_record("1", family))


class TestFW411Mod10(NamedFormMixin, unittest.TestCase):
    def test_defect_new_store_extra_positional(self):
        self.assert_named(
            "new_store",
            lambda: mod10.new_store("sweep", None, "extra"))

    def test_defect_new_store_extra_keyword(self):
        self.assert_named("new_store",
                          lambda: mod10.new_store(bogus=1))

    def test_defect_retain_run_record_missing(self):
        self.assert_named("retain_run_record",
                          lambda: mod10.retain_run_record())

    def test_defect_retain_run_record_extra(self):
        self.assert_named(
            "retain_run_record",
            lambda: mod10.retain_run_record(
                {"run_id": "fw4-11-extra"}, "sweep", "extra"))

    def test_defect_read_run_record_missing(self):
        self.assert_named("read_run_record",
                          lambda: mod10.read_run_record())

    def test_defect_read_run_record_extra(self):
        self.assert_named(
            "read_run_record",
            lambda: mod10.read_run_record("x", "sweep", "extra"))

    def test_control_mod10_entry_points_serve_whole(self):
        store = mod10.new_store("sweep")
        self.assertIsNotNone(store)
        record = {"run_id": "fw4-11-control-run"}
        mod10.retain_run_record(record, "sweep")
        self.assertEqual(
            mod10.read_run_record("fw4-11-control-run")["run_id"],
            "fw4-11-control-run")


class TestFW415Guide(unittest.TestCase):
    def test_defect_readme_names_telling_door(self):
        self.assertIn("record_validation_failures", readme_text())

    def test_defect_entry_point_list_names_it_beside(self):
        text = readme_text()
        start = text.index("### User entry points")
        end = text.index("### Internal surface")
        section = text[start:end]
        self.assertIn("mod01.validate_record", section)
        self.assertIn("mod01.record_validation_failures", section)

    def test_control_telling_door_exported(self):
        self.assertIn("record_validation_failures", mod01.__all__)
        self.assertTrue(callable(mod01.record_validation_failures))
        self.assertTrue(callable(crucible.record_validation_failures))
        failures = mod01.record_validation_failures("2", {})
        self.assertTrue(failures)


class TestFW420Form5Mapping(unittest.TestCase):
    def test_defect_readme_states_field_mapping(self):
        text = readme_text()
        self.assertIn("derivation_version_string", text)
        self.assertIn("recorded_root_seed", text)
        self.assertIn("derivation_version", text)
        self.assertIn("root_seed_reference", text)
        self.assertIn("different shapes", text)

    def test_defect_derive_seed_docstring_states_mapping(self):
        doc = mod02.derive_seed.__doc__ or ""
        self.assertIn("derivation_version_string", doc)
        self.assertIn("recorded_root_seed", doc)
        self.assertIn("root_seed_reference", doc)

    def test_control_form5_record_refused_as_input_in_named_form(self):
        record = mod01.minimal_valid_instance("5")
        self.assertTrue(mod01.validate_record("5", record))
        self.assertEqual(mod01.record_validation_failures("5", record), [])
        answer = mod02.derive_seed(record)
        self.assertEqual(answer["status"], "input failure")
        self.assertFalse(answer["seed_drawn"])


if __name__ == "__main__":
    unittest.main()

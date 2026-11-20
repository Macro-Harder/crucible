"""Step 17, fix wave 5, Builder 5 tests. Row FW5-13 (Low, T17R4-13).

The mod01 Form 4 validation doors judge the sweep_identifier field
for its identifier form and the run_status field against the standing
status set the module own status act states, refusing a handing in
no identifier form and a status outside the set in the named failure
form the counted field failures state, so no such record validates
True at the Form 4 door.

Defect tests: each hostile handing stands reproduced from filing
R4-RED4-01 (Red 4), beside the empty and whitespace only identifier
forms the product identifier form states at the mod10 retention door.
Control tests: the standings that stand whole on the uncured tree and
stand whole after the cure, including the control_values standing the
filing reports and this row does not charge.
"""

import unittest

from crucible import mod01


def _built_record():
    return mod01.build_run_record()


def _failures(record):
    return mod01.record_validation_failures("4", record)


def _names_field(failures, field):
    prefix = "validate_record stands refused: field " + field + ":"
    return any(entry.startswith(prefix) for entry in failures)


class _TextDress(str):
    """A text value whose equality reading lies, in the standing
    dressed form: the doors judge the text a value stores, never
    a reading the value itself supplies."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class TestFW513SweepIdentifier(unittest.TestCase):
    """Defect: sweep_identifier in no identifier form validates True."""

    def _assert_refused(self, hostile):
        record = _built_record()
        record["sweep_identifier"] = hostile
        self.assertFalse(mod01.validate_record("4", record))
        failures = _failures(record)
        self.assertTrue(
            _names_field(failures, "sweep_identifier"),
            "no failure names sweep_identifier: " + repr(failures))

    def test_bare_object_identifier_refused(self):
        self._assert_refused(object())

    def test_integer_identifier_refused(self):
        self._assert_refused(42)

    def test_list_identifier_refused(self):
        self._assert_refused(["x"])

    def test_bytes_identifier_refused(self):
        self._assert_refused(b"x")

    def test_dict_identifier_refused(self):
        self._assert_refused({"x": 1})

    def test_empty_text_identifier_refused(self):
        self._assert_refused("")

    def test_whitespace_only_identifier_refused(self):
        self._assert_refused("   ")


class TestFW513RunStatus(unittest.TestCase):
    """Defect: run_status outside the standing status set validates."""

    def _assert_refused(self, hostile):
        record = _built_record()
        record["run_status"] = hostile
        self.assertFalse(mod01.validate_record("4", record))
        failures = _failures(record)
        self.assertTrue(
            _names_field(failures, "run_status"),
            "no failure names run_status: " + repr(failures))

    def test_banana_status_refused(self):
        self._assert_refused("banana")

    def test_bare_object_status_refused(self):
        self._assert_refused(object())

    def test_integer_status_refused(self):
        self._assert_refused(42)

    def test_bytes_status_refused(self):
        self._assert_refused(b"completed")

    def test_list_status_refused(self):
        self._assert_refused(["completed"])

    def test_empty_text_status_refused(self):
        self._assert_refused("")

    def test_case_variant_status_refused(self):
        self._assert_refused("Completed")

    def test_both_fields_hostile_both_named(self):
        record = _built_record()
        record["sweep_identifier"] = 42
        record["run_status"] = "banana"
        self.assertFalse(mod01.validate_record("4", record))
        failures = _failures(record)
        self.assertTrue(_names_field(failures, "sweep_identifier"))
        self.assertTrue(_names_field(failures, "run_status"))


class TestFW513Controls(unittest.TestCase):
    """Controls: standings whole before the cure and whole after it."""

    def test_unmutated_built_record_validates(self):
        record = _built_record()
        self.assertTrue(mod01.validate_record("4", record))
        self.assertEqual(_failures(record), [])

    def test_minimal_valid_instance_validates(self):
        record = mod01.minimal_valid_instance("4")
        self.assertTrue(mod01.validate_record("4", record))
        self.assertEqual(_failures(record), [])

    def test_completed_status_validates(self):
        record = _built_record()
        record["run_status"] = "completed"
        self.assertTrue(mod01.validate_record("4", record))

    def test_failed_status_validates(self):
        record = _built_record()
        record["run_status"] = "failed"
        self.assertTrue(mod01.validate_record("4", record))

    def test_dressed_completed_status_validates(self):
        record = _built_record()
        record["run_status"] = _TextDress("completed")
        self.assertTrue(mod01.validate_record("4", record))

    def test_dressed_identifier_validates(self):
        record = _built_record()
        record["sweep_identifier"] = _TextDress("sweep-1")
        self.assertTrue(mod01.validate_record("4", record))

    def test_plain_identifier_validates(self):
        record = _built_record()
        record["sweep_identifier"] = "sweep-1"
        self.assertTrue(mod01.validate_record("4", record))

    def test_control_values_standing_unchanged(self):
        # The filing reports control_values handed text as standing
        # validated; this row charges no judgement at that field,
        # so the standing stands as it stood.
        record = _built_record()
        record["control_values"] = "anything"
        self.assertTrue(mod01.validate_record("4", record))

    def test_counted_field_refusal_stands(self):
        record = _built_record()
        record["population_size"] = "hostile"
        self.assertFalse(mod01.validate_record("4", record))
        self.assertTrue(
            _names_field(_failures(record), "population_size"))

    def test_status_act_standing_unchanged(self):
        self.assertFalse(mod01.validate_run_status(
            record_status="banana"))
        self.assertFalse(mod01.validate_run_status(
            record_status=object()))
        self.assertTrue(mod01.validate_run_status(
            record_status="completed"))

    def test_field_conditions_form4_standing_unchanged(self):
        # field_conditions states conditional field conditions, each
        # in discriminator form; the two fields this row judges stand
        # as required fields, not conditional fields, so no entry
        # stands added at that door and its Form 4 standing stands
        # as it stood.
        self.assertEqual(mod01.field_conditions("4"), ())


if __name__ == "__main__":
    unittest.main()

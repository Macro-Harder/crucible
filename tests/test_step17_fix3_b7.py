"""Step 17 fix wave 3, Builder 7 tests: Slice 7, the mod01
validation and form rows. Rows FW3-12, FW3-13, FW3-18, FW3-51,
FW3-55.

Each defect test reproduces the filing defect of its row on the
uncured tree (the chain tree carrying the Slice 1 to Slice 5
cures, uncured for these rows). The stated byte bound of the
FW3-12 cure stands at 1,000,000 bytes beside the entry bound of
10,000 entries. The stated cost form of the FW3-13 cure: one
validate_record call computes the folded variants of a handed
key at most twice per handed key of the record, plus a constant
for the form own fields, where the uncured door computes them
once per key per allowed field.
Standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01, mod10


class TestFW312ByteBound(unittest.TestCase):
    """FW3-12 (Medium, T17R2-12): the validation and retention
    width bounds carry a stated byte form beside the entry form,
    refusing a record past the byte bound in named form."""

    def test_validate_record_past_byte_bound_refused(self):
        record = mod01.minimal_valid_instance("2")
        record["point_identifier"] = "x" * 2000000
        self.assertIs(mod01.validate_record("2", record), False)
        failures = mod01.record_validation_failures("2", record)
        self.assertIn("byte", " ".join(failures))

    def test_validate_bytes_value_past_byte_bound_refused(self):
        record = mod01.minimal_valid_instance("2")
        record["farm_size"] = b"z" * 2000000
        self.assertIs(mod01.validate_record("2", record), False)

    def test_retain_record_past_byte_bound_refused_in_named_form(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record(
                {"run_id": "byte-bound-run",
                 "payload": "y" * 2000000})
        self.assertIn("byte", str(caught.exception))

    def test_control_text_below_byte_bound_validates(self):
        record = mod01.minimal_valid_instance("2")
        record["point_identifier"] = "x" * 500000
        self.assertIs(mod01.validate_record("2", record), True)

    def test_control_text_below_byte_bound_retained(self):
        mod10.reset_stores()
        self.addCleanup(mod10.reset_stores)
        mod10.retain_run_record(
            {"run_id": "byte-control-run", "payload": "y" * 500000})
        read = mod10.read_run_record("byte-control-run")
        self.assertEqual(len(read["payload"]), 500000)

    def test_control_entry_bound_still_refused(self):
        record = mod01.minimal_valid_instance("1")
        for index in range(20000):
            record["extra_field_%d" % index] = index
        self.assertIs(mod01.validate_record("1", record), False)


class TestFW313ValidationCost(unittest.TestCase):
    """FW3-13 (Medium, T17R2-13): validate_record carries a
    stated cost form for the records its width bound admits, so
    one admitted call stands bounded in its work. The charged
    cost form stands counted in folded variant computations,
    never in a timing figure."""

    def test_folded_variant_work_bounded_per_key(self):
        record = mod01.minimal_valid_instance("1")
        for index in range(300):
            record["extra_field_%d" % index] = index
        calls = []
        original = mod01._folded_key_variants

        def counting(key):
            calls.append(key)
            return original(key)

        mod01._folded_key_variants = counting
        try:
            result = mod01.validate_record("1", record)
        finally:
            mod01._folded_key_variants = original
        self.assertIs(result, False)
        self.assertLessEqual(len(calls), 2 * len(record) + 50)

    def test_control_widened_record_answers_false(self):
        record = mod01.minimal_valid_instance("1")
        for index in range(300):
            record["extra_field_%d" % index] = index
        self.assertIs(mod01.validate_record("1", record), False)

    def test_control_folded_field_name_still_judged_a_field(self):
        record = mod01.minimal_valid_instance("4")
        record["run_1ength_in_days"] = record.pop(
            "run_length_in_days")
        failures = mod01.record_validation_failures("4", record)
        self.assertNotIn(
            "run_1ength_in_days",
            " ".join(failures).split("stands outside")[0]
            if "stands outside" in " ".join(failures) else "")
        extra = [
            entry for entry in failures
            if "run_1ength_in_days" in entry
            and "stands outside the record" in entry]
        self.assertEqual(extra, [])


class TestFW318NumericFields(unittest.TestCase):
    """FW3-18 (Medium, T17R2-18): the run record validators
    judge the numeric fields of a run record in their stated
    forms, answering False on a field in no judged form."""

    def _record_with(self, field, value):
        record = mod01.build_run_record()
        record[field] = value
        return record

    def test_form4_numeric_fields_reject_unjudged_forms(self):
        bad_values = (
            float("nan"), float("inf"), float("-inf"),
            True, -5, "hostile", 2.5, None, [1])
        for field in (
                "population_size", "run_length_in_days",
                "replicate_index"):
            for value in bad_values:
                with self.subTest(field=field, value=repr(value)):
                    record = self._record_with(field, value)
                    self.assertIs(
                        mod01.validate_record("4", record), False)
                    failures = mod01.record_validation_failures(
                        "4", record)
                    self.assertIn(field, " ".join(failures))

    def test_form4_zero_count_fields_rejected(self):
        for field in ("population_size", "run_length_in_days"):
            with self.subTest(field=field):
                record = self._record_with(field, 0)
                self.assertIs(
                    mod01.validate_record("4", record), False)

    def test_form2_numeric_fields_reject_unjudged_forms(self):
        for field in ("population_size", "run_length_in_days"):
            for value in (float("nan"), True, -5, "hostile", 2.5):
                with self.subTest(field=field, value=repr(value)):
                    record = mod01.minimal_valid_instance("2")
                    record[field] = value
                    self.assertIs(
                        mod01.validate_record("2", record), False)

    def test_form4_inner_judgement_rejects_unjudged_forms(self):
        record = self._record_with("population_size", float("nan"))
        self.assertIs(
            mod01._validate_record_inner("4", record), False)

    def test_control_built_run_record_validates(self):
        record = mod01.build_run_record()
        record["population_size"] = 100
        record["run_length_in_days"] = 30
        record["replicate_index"] = 0
        self.assertIs(mod01.validate_record("4", record), True)

    def test_control_placeholder_template_validates(self):
        self.assertIs(
            mod01.validate_record(
                "4", mod01.minimal_valid_instance("4")), True)
        self.assertIs(
            mod01.validate_record(
                "2", mod01.minimal_valid_instance("2")), True)

    def test_control_integral_float_and_positive_counts(self):
        record = mod01.build_run_record()
        record["population_size"] = 250
        record["run_length_in_days"] = 30.0
        record["replicate_index"] = 3
        self.assertIs(mod01.validate_record("4", record), True)


class TestFW351BuilderWholeRecordHanding(unittest.TestCase):
    """FW3-51 (Low, T17R2-51): the record builders deliver a
    whole record handing in their named refusal form."""

    def test_build_sweep_point_whole_record_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_sweep_point({"a": 1})
        text = str(caught.exception)
        self.assertIn("named arguments", text)
        self.assertIn("no record stands built", text)

    def test_build_run_record_whole_record_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_run_record({"a": 1})
        text = str(caught.exception)
        self.assertIn("named arguments", text)
        self.assertIn("no record stands built", text)

    def test_control_keyword_build_still_builds(self):
        record = mod01.build_sweep_point(point_identifier="p1")
        self.assertEqual(record["point_identifier"], "p1")
        record = mod01.build_run_record(sweep_identifier="s1")
        self.assertEqual(record["sweep_identifier"], "s1")

    def test_control_unknown_field_still_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod01.build_sweep_point(no_such_field=1)
        self.assertIn("no record stands built", str(caught.exception))


class TestFW355FormRefusalClassGround(unittest.TestCase):
    """FW3-55 (Low, T17R2-55): the form refusal doors state the
    class ground truly where an identifier stands handed in a
    non text class."""

    def test_integer_identifier_states_class_ground(self):
        with self.assertRaises(ValueError) as caught:
            mod01.form_fields(2)
        text = str(caught.exception)
        self.assertIn("non text", text)
        self.assertIn("int", text)
        self.assertNotIn("names no form", text)

    def test_float_identifier_states_class_ground(self):
        with self.assertRaises(ValueError) as caught:
            mod01.form_name(2.0)
        text = str(caught.exception)
        self.assertIn("non text", text)
        self.assertIn("float", text)

    def test_failures_door_states_class_ground(self):
        failures = mod01.record_validation_failures(
            2, mod01.minimal_valid_instance("2"))
        text = " ".join(failures)
        self.assertIn("non text", text)
        self.assertIn("int", text)

    def test_control_text_identifier_answers(self):
        self.assertEqual(len(mod01.form_fields("2")), 10)

    def test_control_unknown_text_identifier_ground_unchanged(self):
        with self.assertRaises(ValueError) as caught:
            mod01.form_fields("99")
        self.assertIn("names no form", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

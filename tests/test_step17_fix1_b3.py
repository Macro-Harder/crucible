"""Step 17 fix wave 1, Builder 3 (Slice 3) tests.

Rows: FW-09 (seal refusal grounds), FW-16 (validate_record
width bound), FW-23 (one identifier form at the validation,
store, and start doors), FW-24 (form lookup doors refuse an
unknown form identifier in named form), FW-25 (refusal
information completeness at the mod01, mod10, and mod12
doors, with the derive_seed limb in mod02).

Each defect test was written against the filing defect on
the base tree at product head
9f938470807f90b7c8c6d9882fde1105c807e0a1, to fail there for
the reason stated in the Builder 3 paper and to pass on the
fixed tree. Control tests pass on both trees.
"""
import unittest

from crucible import mod01, mod02, mod10, mod12


class TestFW09SealRefusalGrounds(unittest.TestCase):

    def test_reseal_names_the_record_as_already_sealed(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        with self.assertRaises(mod12.NamedControllerFailure) as ctx:
            mod12.seal_family_record(sealed)
        text = str(ctx.exception)
        self.assertIn("already stands sealed", text)
        self.assertIn("next step", text)
        self.assertNotIn(
            "field standing outside the form fields", text)

    def test_seal_none_named_in_no_record_form(self):
        with self.assertRaises(mod12.NamedControllerFailure) as ctx:
            mod12.seal_family_record(None)
        text = str(ctx.exception)
        self.assertIn("no record form", text)
        self.assertNotIn("completeness items missing", text)

    def test_seal_empty_record_named_on_its_form_fault(self):
        with self.assertRaises(mod12.NamedControllerFailure) as ctx:
            mod12.seal_family_record({})
        text = str(ctx.exception)
        self.assertIn("no family record form", text)
        self.assertNotIn("completeness items missing", text)

    def test_seal_wrong_form_record_named_on_its_form_fault(self):
        record = mod01.minimal_valid_instance("4")
        with self.assertRaises(mod12.NamedControllerFailure) as ctx:
            mod12.seal_family_record(record)
        text = str(ctx.exception)
        self.assertIn("no family record form", text)
        self.assertNotIn("completeness items missing", text)

    def test_seal_valid_record_still_seals(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertTrue(sealed["sealed"])

    def test_seal_missing_completeness_keeps_its_ground(self):
        record = mod12.make_family_record()
        del record[mod12.FAMILY_COMPLETENESS_ITEMS[0]]
        with self.assertRaises(mod12.NamedControllerFailure) as ctx:
            mod12.seal_family_record(record)
        self.assertIn("completeness items missing", str(ctx.exception))


class TestFW16ValidateWidthBound(unittest.TestCase):

    def test_wide_flat_record_refused_in_named_form(self):
        instance = mod01.minimal_valid_instance("2")
        for index in range(20001):
            instance["extra" + str(index)] = index
        failures = mod01.record_validation_failures("2", instance)
        self.assertEqual(len(failures), 1)
        self.assertIn("width bound", failures[0])
        self.assertIn("10000", failures[0])
        self.assertFalse(mod01.validate_record("2", instance))

    def test_wide_nested_record_refused_in_named_form(self):
        instance = mod01.minimal_valid_instance("2")
        instance["extra_nested"] = [
            {"item" + str(index): index} for index in range(12000)]
        failures = mod01.record_validation_failures("2", instance)
        self.assertEqual(len(failures), 1)
        self.assertIn("width bound", failures[0])
        self.assertFalse(mod01.validate_record("2", instance))

    def test_ordinary_record_still_validates(self):
        instance = mod01.minimal_valid_instance("2")
        self.assertTrue(mod01.validate_record("2", instance))
        self.assertEqual(
            mod01.record_validation_failures("2", instance), [])


class TestFW23OneIdentifierForm(unittest.TestCase):

    def test_int_form_identifier_refused_at_validation(self):
        record = mod01.minimal_valid_instance("2")
        self.assertFalse(mod01.validate_record(2, record))
        failures = mod01.record_validation_failures(2, record)
        self.assertTrue(failures)
        self.assertIn(
            "the identifier stands handed in a non text form, "
            "the int form", failures[0])

    def test_bytes_form_identifier_refused_at_minimal_instance(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.minimal_valid_instance(b"2")
        self.assertIn("names no form", str(ctx.exception))

    def test_bytearray_form_identifier_refused_at_validation(self):
        record = mod01.minimal_valid_instance("2")
        self.assertFalse(
            mod01.validate_record(bytearray(b"2"), record))

    def test_start_run_bytes_class_ground_names_class_as_handed(self):
        result = mod12.start_run(
            run_class=b"screening", family_id="fam-1")
        self.assertEqual(result["status"], "input failure")
        self.assertIn("b'screening'", result["ground_in_words"])
        self.assertFalse(result["run_started"])
        self.assertFalse(result["seed_drawn"])

    def test_start_run_whitespace_family_judged_missing(self):
        result = mod12.start_run(
            run_class="screening", family_id="   ")
        self.assertEqual(result["status"], "input failure")
        self.assertIn("family identifier missing",
                      result["ground_in_words"])

    def test_start_run_container_family_judged_missing(self):
        result = mod12.start_run(
            run_class="screening", family_id=["f"])
        self.assertEqual(result["status"], "input failure")
        self.assertIn("family identifier missing",
                      result["ground_in_words"])

    def test_start_sweep_nontext_family_judged_missing(self):
        for handed in (123, b"fam", ["x"], {"a": 1}):
            result = mod12.start_sweep(handed)
            self.assertEqual(result["status"], "input failure")
            self.assertIn("family identifier missing",
                          result["ground_in_words"])

    def test_start_run_valid_inputs_still_gated(self):
        result = mod12.start_run(
            run_class="screening", family_id="fam-1")
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["run_started"])

    def test_whitespace_run_identifier_refused_at_retain(self):
        store = mod10.new_store("sweep")
        with self.assertRaises(ValueError) as ctx:
            store.retain_run_record({"run_id": "   ", "v": 1})
        self.assertIn("identity less record", str(ctx.exception))
        self.assertIn("whitespace", str(ctx.exception))

    def test_text_run_identifier_still_retained(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "run-b3-1", "v": 1})
        self.assertTrue(store.has_run_record("run-b3-1"))


class TestFW24LookupDoorsRefuseUnknown(unittest.TestCase):

    def test_form_fields_unknown_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_fields("99")
        text = str(ctx.exception)
        self.assertIn("form identifier 99 names no form", text)
        self.assertIn("next step", text)

    def test_required_fields_none_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.required_fields(None)
        self.assertIn(
            "stands handed in a non text form, the NoneType form",
            str(ctx.exception))

    def test_form_name_unknown_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_name("99")
        self.assertIn("names no form", str(ctx.exception))

    def test_field_conditions_unknown_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.field_conditions("99")
        self.assertIn("names no form", str(ctx.exception))

    def test_brief_shape_unknown_form_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.brief_shape_for_form("99")
        self.assertIn("names no form", str(ctx.exception))

    def test_brief_shape_known_form_without_shape_still_none(self):
        self.assertIsNone(mod01.brief_shape_for_form("20"))

    def test_form_ids_for_unknown_shape_raises_named(self):
        with self.assertRaises(ValueError) as ctx:
            mod01.form_ids_for_brief_shape("99")
        text = str(ctx.exception)
        self.assertIn("names no numbered brief Shape", text)
        self.assertIn("next step", text)

    def test_form_ids_for_shape_8_still_answers_two_forms(self):
        self.assertEqual(
            mod01.form_ids_for_brief_shape("8"), ("8", "9"))

    def test_known_form_fields_still_returned(self):
        self.assertIn("point_identifier", mod01.form_fields("2"))
        self.assertIn("point_identifier", mod01.required_fields("2"))


class TestFW25RefusalInformationCompleteness(unittest.TestCase):

    def test_family_failures_reportable_entry_states_ground(self):
        failures = mod12.family_record_validation_failures(
            mod12.make_family_record())
        entries = [
            entry for entry in failures
            if entry.startswith(
                "the reportable run judgement stands refused")]
        self.assertEqual(len(entries), 1)
        self.assertIn("open markers", entries[0])
        self.assertIn("next step", entries[0])
        self.assertNotEqual(
            entries[0], "the reportable run judgement stands refused")

    def test_unknown_store_kind_none_rendered_at_new_store(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.new_store(store_kind=None)
        self.assertIn("unknown store kind: None;",
                      str(ctx.exception))

    def test_unknown_store_kind_none_rendered_at_retain(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.retain_run_record(
                {"run_id": "run-b3-2", "v": 1}, store_kind=None)
        self.assertIn("unknown store kind: None",
                      str(ctx.exception))

    def test_unknown_store_kind_none_rendered_at_lookup(self):
        with self.assertRaises(ValueError) as ctx:
            mod10.store_lookup(store_kinds=(None,), key="run-b3-2")
        self.assertIn("unknown store kind: None",
                      str(ctx.exception))

    def test_duplicate_retain_refusal_states_next_step(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({"run_id": "dup-run-b3", "v": 1})
        with self.assertRaises(ValueError) as ctx:
            store.retain_run_record({"run_id": "dup-run-b3", "v": 2})
        text = str(ctx.exception)
        self.assertIn("second record for the same run", text)
        self.assertIn("next step", text)
        self.assertIn("read_run_record", text)

    def test_derive_seed_malformed_input_named_input_failure(self):
        result = mod02.derive_seed({"bogus": 1})
        self.assertEqual(result["status"], "input failure")
        self.assertEqual(result["form"], "named input failure")
        self.assertFalse(result["seed_drawn"])
        self.assertIn("derivation_version", result["ground_in_words"])
        self.assertIn("next step", result["next_step"].lower())

    def test_derive_seed_nonrecord_input_named_input_failure(self):
        result = mod02.derive_seed(123)
        self.assertEqual(result["status"], "input failure")
        self.assertFalse(result["seed_drawn"])

    def test_derive_seed_no_input_still_gated(self):
        result = mod02.derive_seed()
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["seed_drawn"])

    def test_derive_seed_complete_input_still_gated(self):
        value = mod02.make_derivation_input(
            derivation_version="v1", domain="screening")
        result = mod02.derive_seed(value)
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["seed_drawn"])


if __name__ == "__main__":
    unittest.main()

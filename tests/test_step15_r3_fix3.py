# Step 15 Round 3 fix tests, cluster 3. MOD-11 headline parts standing
# as a dict carrying only empty content, or as empty bytes (R3-A7-05).
# Plain simulated values only.
import unittest

import crucible.mod11 as mod11


def string_unit():
    return {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}


def lawful_unit():
    unit = string_unit()
    unit["holding_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 200}, "outcome": "holds"}]}
    unit["failure_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 800}, "outcome": "fails"}]}
    return unit


class TestR3A705DictForms(unittest.TestCase):
    def test_breaker_five_dict_forms_fail_and_refuse_quotation(self):
        for field, value in (
            ("assumption_record", {"a": ""}),
            ("witness_block", {"a": []}),
            ("claim_sentence", {"a": None}),
            ("assumption_record", {"a": 0}),
            ("assumption_record", {"a": {}}),
        ):
            unit = lawful_unit()
            unit[field] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), (field, value))
            with self.assertRaises(Exception, msg=(field, value)):
                mod11.quote_headline_unit(unit)

    def test_dict_carrying_only_empty_content_in_nested_forms_fails(self):
        for value in (
            {"a": {"b": ""}},
            {"a": [[]]},
            {"a": (0,)},
            {"outer": {"inner": []}},
            {"a": False},
            {"a": b""},
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            with self.assertRaises(Exception, msg=repr(value)):
                mod11.quote_headline_unit(unit)

    def test_envelope_claim_reads_dict_dressed_empty_unit(self):
        unit = lawful_unit()
        unit["witness_block"] = {"a": ""}
        self.assertFalse(mod11.validate_envelope_claim(unit))


class TestR3A705BytesForms(unittest.TestCase):
    def test_breaker_empty_bytes_form_fails_and_refuses_quotation(self):
        unit = lawful_unit()
        unit["assumption_record"] = b""
        self.assertFalse(mod11.validate_headline_unit(unit))
        with self.assertRaises(Exception):
            mod11.quote_headline_unit(unit)

    def test_bytes_carrying_no_content_fail(self):
        for value in (b"\x00", b"\x00\x00", bytearray(), bytearray(b"\x00")):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))

    def test_complex_zero_falls_as_zero(self):
        unit = lawful_unit()
        unit["assumption_record"] = 0j
        self.assertFalse(mod11.validate_headline_unit(unit))


class TestR3A705LawfulControls(unittest.TestCase):
    def test_lawful_units_still_validate_and_quote(self):
        for unit in (string_unit(), lawful_unit()):
            self.assertTrue(mod11.validate_headline_unit(unit))
            self.assertEqual(mod11.quote_headline_unit(unit), unit)

    def test_dict_carrying_content_still_stands_and_quotes(self):
        unit = lawful_unit()
        unit["assumption_record"] = {"a": "stated assumption content"}
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)

    def test_dict_carrying_content_in_nested_forms_still_stands(self):
        for value in (
            {"a": {"b": "stated content"}},
            {"a": ["stated content"]},
            {"a": 1},
            [{"a": "stated content"}],
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(
                mod11.validate_headline_unit(unit), repr(value))

    def test_bytes_carrying_content_still_stands(self):
        unit = lawful_unit()
        unit["assumption_record"] = b"stated bytes content"
        self.assertTrue(mod11.validate_headline_unit(unit))
        self.assertEqual(mod11.quote_headline_unit(unit), unit)


if __name__ == "__main__":
    unittest.main()

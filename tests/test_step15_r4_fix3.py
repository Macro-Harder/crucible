# Step 15 Round 4 fix tests, cluster 3. MOD-11 headline parts standing
# as a type the envelope check does not read (R4-A6-04), and headline
# parts standing as a memoryview read through its bytes content.
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


class PinHelpers:
    def assert_refuses_quotation_in_named_form(self, unit):
        try:
            mod11.quote_headline_unit(unit)
        except ValueError:
            return
        except Exception as error:
            self.fail(
                "quotation raised " + type(error).__name__
                + " instead of the named ValueError refusal: "
                + str(error))
        self.fail("quotation did not refuse the unit")

    def assert_quotes_whole(self, unit):
        try:
            quoted = mod11.quote_headline_unit(unit)
        except Exception as error:
            self.fail(
                "quotation raised " + type(error).__name__
                + " on a standing unit: " + str(error))
        self.assertEqual(quoted, unit)


class TestR4A604UnreadTypes(PinHelpers, unittest.TestCase):
    def test_breaker_empty_range_fails_and_refuses_quotation(self):
        unit = lawful_unit()
        unit["assumption_record"] = range(0)
        self.assertFalse(mod11.validate_headline_unit(unit))
        self.assert_refuses_quotation_in_named_form(unit)

    def test_breaker_memoryview_over_empty_bytes_fails(self):
        unit = lawful_unit()
        unit["assumption_record"] = memoryview(b"")
        self.assertFalse(mod11.validate_headline_unit(unit))
        self.assert_refuses_quotation_in_named_form(unit)

    def test_breaker_memoryview_over_zero_bytes_fails(self):
        for value in (
            memoryview(b"\x00"),
            memoryview(b"\x00\x00"),
            memoryview(bytearray()),
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_refuses_quotation_in_named_form(unit)

    def test_unread_non_empty_types_fail(self):
        for value in (range(3), range(1), object()):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_refuses_quotation_in_named_form(unit)

    def test_unread_types_nested_in_containers_and_dicts_fail(self):
        for value in ([range(2)], {"a": range(2)}, (object(),)):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_refuses_quotation_in_named_form(unit)

    def test_envelope_claim_reads_unread_type_unit(self):
        unit = lawful_unit()
        unit["witness_block"] = range(0)
        self.assertFalse(mod11.validate_envelope_claim(unit))


class TestR4A604MemoryviewBytesLimb(PinHelpers, unittest.TestCase):
    def test_memoryview_over_content_stands_and_quotes_whole(self):
        for value in (
            memoryview(b"stated bytes content"),
            memoryview(bytearray(b"stated bytes content")),
            memoryview(b"\x00stated"),
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_quotes_whole(unit)

    def test_memoryview_content_nested_stands_and_quotes_whole(self):
        for value in (
            [memoryview(b"stated bytes content")],
            {"a": memoryview(b"stated bytes content")},
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_quotes_whole(unit)

    def test_memoryview_no_content_nested_fails(self):
        for value in (
            [memoryview(b"")],
            {"a": memoryview(b"\x00")},
            (memoryview(b""),),
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_refuses_quotation_in_named_form(unit)


class TestR4A604StandingControls(PinHelpers, unittest.TestCase):
    def test_every_standing_refusal_still_refuses(self):
        for value in (
            False, 0, 0.0, 0j, [], (), set(), frozenset(), {},
            "", "   ", b"", b"\x00\x00", bytearray(),
            bytearray(b"\x00"), {"a": ""}, {"a": []}, {"a": None},
            {"a": 0}, {"a": {}}, {"a": b""}, [[]], [""], [0],
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_refuses_quotation_in_named_form(unit)

    def test_lawful_units_still_validate_and_quote_whole(self):
        for unit in (string_unit(), lawful_unit()):
            self.assertTrue(mod11.validate_headline_unit(unit))
            self.assert_quotes_whole(unit)
        for value in (
            b"stated bytes content",
            bytearray(b"stated bytes content"),
            {"a": "stated assumption content"},
            ["stated assumption record"],
            1,
        ):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(
                mod11.validate_headline_unit(unit), repr(value))
            self.assert_quotes_whole(unit)


if __name__ == "__main__":
    unittest.main()

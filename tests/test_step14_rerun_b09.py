"""Step 14 re-run, Builder B9 pins. Slice S-13, MOD-11.

Pins three cured items: R5-A6-06 (headline parts standing as
method overriding subclass instances on stored empty content),
the TG4-56 readout equivalence duty, and the TG4-64 disclosure
form identification duty.
"""
import unittest

from crucible import mod11


def lawful_unit():
    values = {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}
    values["claim_sentence"] = (
        "At the sampled points within the stated scope, the result "
        "holds for the sampled points only, and nothing is claimed "
        "beyond the stated limits.")
    values["grounding_sentence"] = (
        "This unit rests on the retained run records within the "
        "stated scope, and its limits are that nothing is claimed "
        "beyond the sampled points in this unit.")
    values["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is used in "
        "this unit.")
    return mod11.make_headline_unit(values)


class StripLieStr(str):
    def strip(self, *args, **kwargs):
        return "ab"


class ValuesLieDict(dict):
    def values(self):
        return ["content"]


class IterLieBytes(bytes):
    def __iter__(self):
        return iter([65])


class IterLieBytearray(bytearray):
    def __iter__(self):
        return iter([65])


class IterLieList(list):
    def __iter__(self):
        return iter(["content"])


class NeLieInt(int):
    def __ne__(self, other):
        return True


class NeLieFloat(float):
    def __ne__(self, other):
        return True


class TestR5A606SubclassOverride(unittest.TestCase):
    def test_overriding_subclass_parts_on_empty_content_refused(self):
        forms = (
            StripLieStr(""),
            ValuesLieDict({"a": ""}),
            IterLieBytes(b""),
            IterLieBytearray(b"\x00"),
            IterLieList([""]),
            NeLieInt(0),
            NeLieFloat(0.0),
        )
        for value in forms:
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(mod11.validate_headline_unit(unit), repr(value))
            with self.assertRaises(ValueError):
                mod11.quote_headline_unit(unit)

    def test_plain_subclass_parts_carrying_content_stand(self):
        class PlainStr(str):
            pass

        class PlainList(list):
            pass

        for value in (PlainStr("stated content"), PlainList(["stated"]),
                      "stated content", 1, 1.5):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(mod11.validate_headline_unit(unit), repr(value))


class TestTG456ReadoutEquivalence(unittest.TestCase):
    def test_visual_quantity_with_recorded_number_and_class_rule(self):
        readout = {"quantities": [
            {"name": "holding share", "presented_by": "extent",
             "recorded_number": 0.4, "class_based": True,
             "class_rule": "a point stands in the holding class "
                           "where its share reaches 0.4"},
        ]}
        self.assertTrue(mod11.validate_readout(readout))

    def test_visual_only_quantity_not_published(self):
        readout = {"quantities": [
            {"name": "holding share", "presented_by": "colour",
             "recorded_number": None},
        ]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_class_based_quantity_without_rule_in_words_refused(self):
        readout = {"quantities": [
            {"name": "holding share", "presented_by": "position",
             "recorded_number": 3, "class_based": True,
             "class_rule": ""},
        ]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_empty_and_number_only_forms(self):
        self.assertFalse(mod11.validate_readout({"quantities": []}))
        self.assertFalse(mod11.validate_readout("not a readout"))
        readout = {"quantities": [
            {"name": "count", "presented_by": "numbers",
             "recorded_number": 7},
        ]}
        self.assertTrue(mod11.validate_readout(readout))


class TestTG464DisclosureIdentification(unittest.TestCase):
    def test_identified_quantities_in_fixed_order_stand(self):
        form = {"entries": [
            {"row": "row A", "column": "period 1", "quantity": 4},
            {"row": "row B", "period": "period 2", "quantity": 2},
        ]}
        self.assertTrue(mod11.validate_disclosure_form(form))

    def test_position_only_quantities_refused(self):
        form = {"entries": [{"quantity": 4}, {"quantity": 2}]}
        self.assertFalse(mod11.validate_disclosure_form(form))

    def test_out_of_order_and_missing_identifier_refused(self):
        form = {"entries": [
            {"column": "period 1", "row": "row A", "quantity": 4},
        ]}
        self.assertFalse(mod11.validate_disclosure_form(form))
        form = {"entries": [
            {"row": "row A", "column": "", "quantity": 4},
        ]}
        self.assertFalse(mod11.validate_disclosure_form(form))
        self.assertFalse(mod11.validate_disclosure_form({"entries": []}))


if __name__ == "__main__":
    unittest.main()

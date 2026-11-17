"""Step 15 re-run, fix wave 22, builder b3 pins.

Row R22-003 of the Round 22 register, Group 3: the MOD-11
headline refusal stored key text, under settlement S-16, on
ruling C. Locus: crucible/mod11.py _headline_unit_refusal alone,
at its extra field test, its field presence test, its field
order test, and the field value readings of its later limbs.

The distinguishing pins hand the refusal act, at the helper
direct and at the public gate quote_headline_unit, a lawful
headline unit whose keys stand in crafted text dresses: an
extra field key whose equality answers True against every
value, a closed field key whose equality answers False against
every value, and keys whose equality readings raise
RuntimeError. On the pristine tree each such handing is refused
on a misstated ground, is named as what it is not, or escapes
bare. On the cured tree the keys stand judged on the stored key
text they carry, in the cured form of the companion act
make_headline_unit at row R21-009, and each handing draws the
refusal sentence its stored standing carries. The controls hand
plain keys and pass on both trees.
"""
import unittest

from crucible import mod11


GENERIC_REFUSAL = (
    "quote_headline_unit stands refused: the headline unit does "
    "not validate as a quotable unit whole, and no unit stands "
    "quoted")
BEYOND_BOGUS_REFUSAL = (
    "quote_headline_unit stands refused: fields beyond the closed "
    "unit: bogus_field, and no unit stands quoted")
ORDER_REFUSAL = (
    "quote_headline_unit stands refused: the headline unit fields "
    "stand out of the closed unit order, and no unit stands quoted")
ABSENT_GROUNDING_REFUSAL = (
    "quote_headline_unit stands refused: headline unit field "
    "absent: grounding_sentence, and no unit stands quoted")
ABSENT_CLAIM_REFUSAL = (
    "quote_headline_unit stands refused: headline unit field "
    "absent: claim_sentence, and no unit stands quoted")
NO_FORM_REFUSAL = (
    "quote_headline_unit stands refused: the headline unit stands "
    "in no record form, a headline unit stands as a field mapping, "
    "and no unit stands quoted")


class AlwaysEqStr(str):
    """A text storing one text whose equality reading answers
    True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class NeverEqStr(str):
    """A text storing one text whose equality reading answers
    False against every value."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class RaisingEqStr(str):
    """A text storing one text whose equality readings raise
    RuntimeError."""

    def __eq__(self, other):
        raise RuntimeError("equality reading armed")

    def __ne__(self, other):
        raise RuntimeError("equality reading armed")

    __hash__ = str.__hash__


def lawful_values():
    values = {field: "value for " + field
              for field in mod11.HEADLINE_UNIT_FIELDS}
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
    return values


def lawful_unit():
    return mod11.make_headline_unit(lawful_values())


def dressed_claim_unit(key_class, drop=(), swap_positions=None):
    """The lawful unit rebuilt with its claim_sentence key in the
    handed dress, optionally dropping named fields and swapping
    two standing positions."""
    items = list(lawful_unit().items())
    if swap_positions is not None:
        first, second = swap_positions
        items[first], items[second] = items[second], items[first]
    rebuilt = {}
    for key, value in items:
        if key in drop:
            continue
        if str.__str__(key) == "claim_sentence":
            rebuilt[key_class("claim_sentence")] = value
        else:
            rebuilt[key] = value
    return rebuilt


def extra_key_unit(key):
    unit = dict(lawful_unit())
    unit[key] = "extra value"
    return unit


class TestR22003Distinguishing(unittest.TestCase):
    def test_helper_always_equal_extra_named_beyond(self):
        unit = extra_key_unit(AlwaysEqStr("bogus_field"))
        self.assertEqual(
            mod11._headline_unit_refusal(unit), BEYOND_BOGUS_REFUSAL)

    def test_quote_always_equal_extra_named_beyond(self):
        unit = extra_key_unit(AlwaysEqStr("bogus_field"))
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), BEYOND_BOGUS_REFUSAL)

    def test_helper_never_equal_closed_key_not_named_beyond(self):
        unit = dressed_claim_unit(NeverEqStr)
        self.assertEqual(
            mod11._headline_unit_refusal(unit), GENERIC_REFUSAL)

    def test_quote_never_equal_closed_key_not_named_beyond(self):
        unit = dressed_claim_unit(NeverEqStr)
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), GENERIC_REFUSAL)

    def test_helper_raising_extra_named_beyond_no_escape(self):
        unit = extra_key_unit(RaisingEqStr("bogus_field"))
        self.assertEqual(
            mod11._headline_unit_refusal(unit), BEYOND_BOGUS_REFUSAL)

    def test_quote_raising_extra_named_beyond_no_escape(self):
        unit = extra_key_unit(RaisingEqStr("bogus_field"))
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), BEYOND_BOGUS_REFUSAL)

    def test_helper_raising_closed_key_no_bare_escape(self):
        unit = dressed_claim_unit(RaisingEqStr)
        self.assertEqual(
            mod11._headline_unit_refusal(unit), GENERIC_REFUSAL)

    def test_helper_dressed_key_order_judged_on_stored_text(self):
        unit = dressed_claim_unit(NeverEqStr, swap_positions=(2, 3))
        self.assertEqual(
            mod11._headline_unit_refusal(unit), ORDER_REFUSAL)

    def test_helper_dressed_key_presence_judged_on_stored_text(self):
        unit = dressed_claim_unit(
            NeverEqStr, drop=("grounding_sentence",))
        self.assertEqual(
            mod11._headline_unit_refusal(unit),
            ABSENT_GROUNDING_REFUSAL)


class TestR22003Controls(unittest.TestCase):
    def test_helper_plain_lawful_generic_refusal(self):
        self.assertEqual(
            mod11._headline_unit_refusal(lawful_unit()),
            GENERIC_REFUSAL)

    def test_quote_plain_lawful_quoted_whole(self):
        quoted = mod11.quote_headline_unit(lawful_unit())
        self.assertEqual(tuple(quoted.keys()),
                         mod11.HEADLINE_UNIT_FIELDS)
        self.assertEqual(len(quoted), 14)

    def test_helper_plain_extra_named_beyond(self):
        unit = extra_key_unit("bogus_field")
        self.assertEqual(
            mod11._headline_unit_refusal(unit), BEYOND_BOGUS_REFUSAL)

    def test_quote_plain_extra_named_beyond(self):
        unit = extra_key_unit("bogus_field")
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), BEYOND_BOGUS_REFUSAL)

    def test_helper_plain_missing_field_named_absent(self):
        unit = {key: value for key, value in lawful_unit().items()
                if key != "grounding_sentence"}
        self.assertEqual(
            mod11._headline_unit_refusal(unit),
            ABSENT_GROUNDING_REFUSAL)

    def test_helper_plain_swapped_fields_order_refusal(self):
        items = list(lawful_unit().items())
        items[2], items[3] = items[3], items[2]
        self.assertEqual(
            mod11._headline_unit_refusal(dict(items)), ORDER_REFUSAL)

    def test_helper_non_dict_no_record_form(self):
        self.assertEqual(
            mod11._headline_unit_refusal("no unit"), NO_FORM_REFUSAL)

    def test_helper_plain_none_value_named_absent(self):
        unit = dict(lawful_unit())
        unit["claim_sentence"] = None
        self.assertEqual(
            mod11._headline_unit_refusal(unit), ABSENT_CLAIM_REFUSAL)


if __name__ == "__main__":
    unittest.main()

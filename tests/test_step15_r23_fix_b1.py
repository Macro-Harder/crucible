"""Step 15 re-run, fix wave 23, builder b1 pins.

Row R23-001 of the Round 23 register, Group 1: the MOD-11
validator stored key text, under settlement S-16, on Ruling 1.
Locus: crucible/mod11.py validate_headline_unit alone, at its
field presence, extra field, and field order judgements, and
the field value readings that follow them.

The distinguishing pins hand the validator act, direct and at
the public gate quote_headline_unit, a lawful headline unit
whose closed field keys stand in crafted text dresses: keys
whose equality readings raise RuntimeError, and keys whose
equality answers False against every value, at the
claim_sentence key, at the grounding_sentence key, at the
first field key, and at every key. On the pristine tree the
raising dress escapes bare at the validator and at the gate,
and the never equal dress draws a False judgement on the
lawful unit, the gate delivering only the closing generic
refusal. On the cured tree the keys stand judged on the
stored key text they carry, in the cured form of the
companion refusal _headline_unit_refusal at row R22-003, and
each lawful handing validates True and quotes whole. The
controls hand plain keys, and a raising equality key standing
as an extra key beyond the closed fields, and pass on both
trees.
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

FIRST_FIELD = mod11.HEADLINE_UNIT_FIELDS[0]


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


def dressed_unit(key_class, targets):
    """The lawful unit rebuilt with each key named in targets
    standing in the handed dress, or with every key in the
    handed dress where targets stands as the word every."""
    rebuilt = {}
    for key, value in lawful_unit().items():
        plain_key = str.__str__(key)
        if targets == "every" or plain_key in targets:
            rebuilt[key_class(plain_key)] = value
        else:
            rebuilt[key] = value
    return rebuilt


def extra_key_unit(key):
    unit = dict(lawful_unit())
    unit[key] = "extra value"
    return unit


class TestR23001RaisingDistinguishing(unittest.TestCase):
    def test_validate_raising_claim_key(self):
        unit = dressed_unit(RaisingEqStr, ("claim_sentence",))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_raising_claim_key(self):
        unit = dressed_unit(RaisingEqStr, ("claim_sentence",))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_raising_grounding_key(self):
        unit = dressed_unit(RaisingEqStr, ("grounding_sentence",))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_raising_grounding_key(self):
        unit = dressed_unit(RaisingEqStr, ("grounding_sentence",))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_raising_first_field_key(self):
        unit = dressed_unit(RaisingEqStr, (FIRST_FIELD,))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_raising_first_field_key(self):
        unit = dressed_unit(RaisingEqStr, (FIRST_FIELD,))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_raising_every_key(self):
        unit = dressed_unit(RaisingEqStr, "every")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_raising_every_key(self):
        unit = dressed_unit(RaisingEqStr, "every")
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)


class TestR23001NeverEqualDistinguishing(unittest.TestCase):
    def test_validate_never_equal_claim_key(self):
        unit = dressed_unit(NeverEqStr, ("claim_sentence",))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_never_equal_claim_key(self):
        unit = dressed_unit(NeverEqStr, ("claim_sentence",))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_never_equal_grounding_key(self):
        unit = dressed_unit(NeverEqStr, ("grounding_sentence",))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_never_equal_grounding_key(self):
        unit = dressed_unit(NeverEqStr, ("grounding_sentence",))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_never_equal_first_field_key(self):
        unit = dressed_unit(NeverEqStr, (FIRST_FIELD,))
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_never_equal_first_field_key(self):
        unit = dressed_unit(NeverEqStr, (FIRST_FIELD,))
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)

    def test_validate_never_equal_every_key(self):
        unit = dressed_unit(NeverEqStr, "every")
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_quote_never_equal_every_key(self):
        unit = dressed_unit(NeverEqStr, "every")
        quoted = mod11.quote_headline_unit(unit)
        self.assertEqual(len(quoted), 14)


class TestR23001Controls(unittest.TestCase):
    def test_validate_plain_lawful(self):
        self.assertTrue(mod11.validate_headline_unit(lawful_unit()))

    def test_quote_plain_lawful_quoted_whole(self):
        quoted = mod11.quote_headline_unit(lawful_unit())
        self.assertEqual(tuple(quoted.keys()),
                         mod11.HEADLINE_UNIT_FIELDS)
        self.assertEqual(len(quoted), 14)

    def test_validate_plain_extra_key_false(self):
        unit = extra_key_unit("bogus_field")
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_quote_plain_extra_key_named_beyond(self):
        unit = extra_key_unit("bogus_field")
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), BEYOND_BOGUS_REFUSAL)

    def test_validate_raising_extra_key_false_no_escape(self):
        unit = extra_key_unit(RaisingEqStr("bogus_field"))
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_quote_raising_extra_key_named_beyond_no_escape(self):
        unit = extra_key_unit(RaisingEqStr("bogus_field"))
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit(unit)
        self.assertEqual(str(caught.exception), BEYOND_BOGUS_REFUSAL)

    def test_validate_plain_missing_field_false(self):
        unit = {key: value for key, value in lawful_unit().items()
                if key != "grounding_sentence"}
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_validate_plain_swapped_order_false(self):
        items = list(lawful_unit().items())
        items[2], items[3] = items[3], items[2]
        self.assertFalse(mod11.validate_headline_unit(dict(items)))

    def test_validate_non_dict_false(self):
        self.assertFalse(mod11.validate_headline_unit("no unit"))

    def test_validate_plain_none_claim_false(self):
        unit = dict(lawful_unit())
        unit["claim_sentence"] = None
        self.assertFalse(mod11.validate_headline_unit(unit))


if __name__ == "__main__":
    unittest.main()

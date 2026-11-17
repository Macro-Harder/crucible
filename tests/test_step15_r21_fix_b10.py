"""

Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

Pins for fix wave 21, Builder 10, Group 10, row R21-019.

The MOD-01 provenance field judgement, under settlement S-16.
At the charged locus, validate_provenance_block in crucible/mod01.py,
the act builds the field text of a present entry field and tests
that text for the arbiter accuracy part, which decides whether the
entry stands required to carry an error direction. On the pristine
code a field in no text form is judged on the string reading the
value itself supplies, through _safe_str, so a supplied reading
that answers arbiter accuracy draws the error direction requirement
for a field whose stored form carries no such text, and a buffer
field storing arbiter accuracy whose supplied reading answers
something else escapes that requirement. Each distinguishing pin
hands the charged act one such handing and expects the act to judge
the field on the form and contents it stores. The control pins hand
plain text and plain non text fields and expect the judgements the
pristine code already delivers.
"""


import unittest
from crucible import mod06
from crucible import mod01


class LieStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return self._reading


class RaiseStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __str__(self):
        raise RuntimeError("string reading refused")


def contract_sentence(**kwargs):
    try:
        mod06.escrow_contract_state("contract-1", **kwargs)
    except ValueError as error:
        return str(error)
    return ""


def pause_sentence(variant):
    try:
        mod06.pause_cap(variant)
    except ValueError as error:
        return str(error)
    return ""


class TestR20052VariantSentence(unittest.TestCase):
    def test_lying_variant_names_stored(self):
        sentence = contract_sentence(variant=LieStr("X9", "B-4"))
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_raising_variant_names_stored(self):
        sentence = contract_sentence(variant=RaiseStr("X9"))
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_bytes_variant_names_stored(self):
        sentence = contract_sentence(variant=b"X9")
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_plain_variant_control(self):
        sentence = contract_sentence(variant="X9")
        self.assertIn(
            "the escrow variant stands outside the B-3 and B-4 "
            "set: X9, and", sentence)

    def test_valid_b4_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-4")
        self.assertEqual(state["variant"], "B-4")

    def test_valid_b3_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-3")
        self.assertEqual(state["variant"], "B-3")


class TestR20053LienStateSentence(unittest.TestCase):
    def test_lying_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4",
            lien_state=LieStr("bogus lien", "no lien in force"))
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_raising_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4", lien_state=RaiseStr("bogus lien"))
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_bytes_lien_names_stored(self):
        sentence = contract_sentence(
            variant="B-4", lien_state=b"bogus lien")
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_plain_lien_control(self):
        sentence = contract_sentence(
            variant="B-4", lien_state="bogus lien")
        self.assertIn(
            "the lien state stands outside the closed four "
            "value set: bogus lien, and", sentence)

    def test_valid_lien_control(self):
        state = mod06.escrow_contract_state(
            "contract-1", variant="B-4", lien_state="released")
        self.assertEqual(state["lien_state"], "released")


class TestR20054PauseCapSentence(unittest.TestCase):
    def test_lying_variant_names_stored(self):
        sentence = pause_sentence(LieStr("X9", "B-4"))
        self.assertIn("for an unknown variant: X9", sentence)

    def test_raising_variant_names_stored(self):
        sentence = pause_sentence(RaiseStr("X9"))
        self.assertIn("for an unknown variant: X9", sentence)

    def test_bytes_variant_names_stored(self):
        sentence = pause_sentence(b"X9")
        self.assertIn("for an unknown variant: X9", sentence)

    def test_plain_variant_control(self):
        sentence = pause_sentence("X9")
        self.assertIn("for an unknown variant: X9", sentence)

    def test_valid_b4_control(self):
        result = mod06.pause_cap("B-4")
        self.assertEqual(result["total_percent"], 400)

    def test_valid_b3_control(self):
        result = mod06.pause_cap("B-3")
        self.assertEqual(result["variant"], "B-3")


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class LyingStrInt(int):
    def __str__(self):
        return "arbiter accuracy"


class LyingStrBuffer(bytearray):
    def __str__(self):
        return "arbiter accuracy"


class OtherStrBuffer(bytearray):
    def __str__(self):
        return "something else"


class RaisingStrBuffer(bytearray):
    def __str__(self):
        raise RuntimeError("str boom")


class LyingStrList(list):
    def __str__(self):
        return "arbiter accuracy"


class LyingStrDict(dict):
    def __str__(self):
        return "arbiter accuracy"


class LyingStrText(str):
    def __str__(self):
        return "something else"


def block(field, with_direction=False):
    entry = {"field": field, "applicability": "applies"}
    if with_direction:
        entry["error_direction"] = "stated direction"
    return {
        "entries": [entry],
        "excluded_class_counts": {"a": 1},
        "excluded_class_shares": {"a": 1},
    }


class TestR21019Distinguishing(unittest.TestCase):
    def test_lying_int_field_judged_on_stored_form(self):
        self.assertTrue(
            mod01.validate_provenance_block(block(LyingStrInt(5))))

    def test_lying_buffer_field_storing_other_text(self):
        self.assertTrue(mod01.validate_provenance_block(
            block(LyingStrBuffer(b"something else"))))

    def test_buffer_field_storing_arbiter_accuracy_lying_str(self):
        self.assertFalse(mod01.validate_provenance_block(
            block(OtherStrBuffer(b"arbiter accuracy"))))

    def test_lying_list_field_storing_other_part(self):
        self.assertTrue(mod01.validate_provenance_block(
            block(LyingStrList(["something else"]))))

    def test_lying_dict_field_judged_on_stored_form(self):
        self.assertTrue(mod01.validate_provenance_block(
            block(LyingStrDict({"k": 1}))))


class TestR21019Controls(unittest.TestCase):
    def test_plain_text_arbiter_accuracy_needs_direction(self):
        self.assertFalse(mod01.validate_provenance_block(
            block("arbiter accuracy")))

    def test_plain_text_arbiter_accuracy_value_needs_direction(self):
        self.assertFalse(mod01.validate_provenance_block(
            block("arbiter_accuracy_value")))

    def test_plain_text_arbiter_accuracy_with_direction_passes(self):
        self.assertTrue(mod01.validate_provenance_block(
            block("arbiter accuracy", with_direction=True)))

    def test_plain_text_other_field_passes(self):
        self.assertTrue(mod01.validate_provenance_block(
            block("something else")))

    def test_plain_int_field_passes(self):
        self.assertTrue(mod01.validate_provenance_block(block(5)))

    def test_plain_buffer_field_passes(self):
        self.assertTrue(mod01.validate_provenance_block(
            block(bytearray(b"field"))))

    def test_raising_str_buffer_field_returns_boolean(self):
        self.assertTrue(mod01.validate_provenance_block(
            block(RaisingStrBuffer(b"field"))))

    def test_text_subclass_storing_arbiter_accuracy_judged_stored(self):
        self.assertFalse(mod01.validate_provenance_block(
            block(LyingStrText("arbiter accuracy"))))

    def test_single_part_tuple_storing_arbiter_accuracy(self):
        self.assertFalse(mod01.validate_provenance_block(
            block(("arbiter accuracy",))))

    def test_plain_bytes_storing_arbiter_accuracy(self):
        self.assertFalse(mod01.validate_provenance_block(
            block(b"arbiter accuracy")))


if __name__ == "__main__":
    unittest.main()

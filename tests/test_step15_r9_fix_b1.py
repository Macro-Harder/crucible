"""Fix wave 8 pins, Builder 1: MOD-01 rows of Round 8.

Rows pinned: R8-006, R8-011, R8-015, all at crucible/mod01.py.
Each charged defect form fails on the uncured module and passes
on the cured copy; lawful controls stand both ways.
"""
import unittest

from crucible import mod01


class HashEqLieKey(str):
    """A text key storing one field name whose hash reading
    answers as an allowed field and whose equality reading
    answers True against every value."""

    def __new__(cls, stored, answers_hash_of):
        obj = str.__new__(cls, stored)
        obj._answers_hash_of = answers_hash_of
        return obj

    def __hash__(self):
        return str.__hash__(self._answers_hash_of)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class IterLieList(list):
    """A list storing stated items whose iteration reading
    yields only the single kind sweep."""

    def __iter__(self):
        return iter(("sweep",))


class IterLieTuple(tuple):
    def __iter__(self):
        return iter(("sweep",))


class IterLieDict(dict):
    def __iter__(self):
        return iter(("sweep",))


class IterLieSet(set):
    def __iter__(self):
        return iter(("sweep",))


class EqLieKind(str):
    """A text kind storing one value whose equality reading
    answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(str.__str__(self))


class TestR8006ClosedFormStoredNames(unittest.TestCase):

    def test_r8_006_defect_lie_key_extra_field_refused(self):
        lie = HashEqLieKey(
            "evil_extra_field",
            "headline_unit_identifier_and_issue_date")
        instance = {lie: "x", **mod01.minimal_valid_instance("16")}
        self.assertFalse(mod01.validate_record("16", instance))

    def test_r8_006_control_plain_minimal_validates(self):
        instance = mod01.minimal_valid_instance("16")
        self.assertTrue(mod01.validate_record("16", instance))

    def test_r8_006_control_plain_extra_field_refused(self):
        instance = mod01.minimal_valid_instance("16")
        instance["evil_extra_field"] = "x"
        self.assertFalse(mod01.validate_record("16", instance))

    def test_r8_006_control_lie_key_storing_allowed_name(self):
        lie = HashEqLieKey(
            "claim_sentence",
            "headline_unit_identifier_and_issue_date")
        instance = {lie: "x", **mod01.minimal_valid_instance("16")}
        self.assertTrue(mod01.validate_record("16", instance))


class TestR8011StoreAddressingStoredContainer(unittest.TestCase):

    def test_r8_011_defect_iteration_lie_containers_refused(self):
        cases = [
            IterLieList(["bogus", "pilot"]),
            IterLieList(["bogus"]),
            IterLieTuple(("bogus", "pilot")),
            IterLieDict({"bogus": 1, "pilot": 2}),
            IterLieSet({"bogus", "pilot"}),
        ]
        for addressing in cases:
            with self.subTest(kind=type(addressing).__name__):
                self.assertFalse(
                    mod01.validate_store_addressing(addressing))

    def test_r8_011_control_plain_forms_both_ways(self):
        self.assertTrue(mod01.validate_store_addressing(["sweep"]))
        self.assertTrue(mod01.validate_store_addressing(("sweep",)))
        self.assertFalse(mod01.validate_store_addressing(["bogus"]))
        self.assertFalse(mod01.validate_store_addressing([]))
        self.assertFalse(
            mod01.validate_store_addressing(["sweep", "pilot"]))

    def test_r8_011_control_generator_and_kind_lie_held(self):
        self.assertFalse(mod01.validate_store_addressing(
            item for item in ("bogus",)))
        self.assertFalse(
            mod01.validate_store_addressing([EqLieKind("bogus")]))
        self.assertTrue(
            mod01.validate_store_addressing([EqLieKind("sweep")]))


class TestR8015TransliteratedDigitReadings(unittest.TestCase):

    CYRILLIC_LEET = "реа1мани"
    CYRILLIC_DROPPED = "реал7мани"

    def test_r8_015_defect_transliterated_digit_forms_barred(self):
        keys = [
            "rea1mani", "r3almani", "rea1man1", "real7mani",
            "real9mani", self.CYRILLIC_LEET, self.CYRILLIC_DROPPED,
        ]
        for key in keys:
            with self.subTest(key=key):
                self.assertTrue(
                    mod01._folded_key_carries(key, "realmoney"))
        self.assertTrue(
            mod01._carries_real_money_value({"rea1mani": 5}))

    def test_r8_015_control_plain_forms_both_ways(self):
        self.assertTrue(
            mod01._folded_key_carries("realmoney", "realmoney"))
        self.assertTrue(
            mod01._folded_key_carries("realmani", "realmoney"))
        self.assertFalse(
            mod01._folded_key_carries("clean", "realmoney"))
        self.assertTrue(
            mod01._carries_real_money_value({"realmoney": 5}))
        self.assertTrue(
            mod01._carries_real_money_value({"realmani": 5}))
        self.assertFalse(
            mod01._carries_real_money_value({"clean": 5}))


if __name__ == "__main__":
    unittest.main()

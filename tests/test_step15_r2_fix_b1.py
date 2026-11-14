# Step 15 second run fix tests, builder b1. MOD-01 surfaces only.
import unittest

import crucible.mod01 as mod01


def form4_with(key, value):
    instance = mod01.minimal_valid_instance("4")
    instance[key] = value
    return instance


class TestSmallCapitalMoneyMarker(unittest.TestCase):
    def test_small_capital_marker_key_fails(self):
        key = "\u0280\u1d07\u1d00\u029f\u1d0d\u1d0f\u0274\u1d07\u028f"
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))

    def test_small_capital_single_letters_fail(self):
        for key in ("re\u1d00lmoney", "realm\u1d0fney", "realmoney\u028f".replace("\u028f", "\u028f")):
            self.assertFalse(mod01.validate_record("4", form4_with(key, 500)), key)
        key = "real\u1d0d\u1d0f\u0274\u1d07\u028f"
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))


class TestSymbolLeet(unittest.TestCase):
    def test_symbol_marker_keys_fail(self):
        for key in ("re@lmoney", "r\u20acalmoney", "rea\u00a3money",
                    "rea!money", "rea|money", "realmone\u00a5"):
            self.assertFalse(mod01.validate_record("4", form4_with(key, 500)), key)

    def test_symbol_amount_currency_shape_fails(self):
        instance = mod01.minimal_valid_instance("4")
        instance["@mount"] = 500
        instance["currency"] = "stated"
        self.assertFalse(mod01.validate_record("4", instance))
        instance = mod01.minimal_valid_instance("4")
        instance["amount"] = 500
        instance["currenc\u00a5"] = "stated"
        self.assertFalse(mod01.validate_record("4", instance))

    def test_symbol_anchor_key_count_fails_at_four(self):
        for key in ("\u0040nchor_scenario_values", "anchor_sc\u20acnario_values"):
            good = form4_with(key, ["a", "b", "c"])
            self.assertTrue(mod01.validate_record("4", good), key)
            bad = form4_with(key, ["a", "b", "c", "d"])
            self.assertFalse(mod01.validate_record("4", bad), key)


class TestScalarAnchor(unittest.TestCase):
    def test_scalar_anchor_values_fail(self):
        for value in ("abcd", 1234, True, 42, 3.5, "x"):
            instance = form4_with("anchor_scenario_values", value)
            self.assertFalse(mod01.validate_record("4", instance), repr(value))

    def test_three_values_still_pass(self):
        instance = form4_with("anchor_scenario_values", ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", instance))


class TestArmenianLetters(unittest.TestCase):
    def test_armenian_oh_and_vo_fail(self):
        self.assertFalse(mod01.validate_record(
            "4", form4_with("realm\u0585ney", 500)))
        self.assertFalse(mod01.validate_record(
            "4", form4_with("realmo\u0578ey", 500)))

    def test_armenian_amount_shape_fails(self):
        instance = mod01.minimal_valid_instance("4")
        instance["amou\u0578t"] = 500
        instance["currency"] = "stated"
        self.assertFalse(mod01.validate_record("4", instance))


class ForgedStamp(mod01.VersionStamp):
    def as_dict(self):
        return {"family_version": "v1", "family_manifest_hash": "h",
                "rule_version_set": "r1"}


class ForgedBlock(mod01.ProvenanceBlock):
    def as_dict(self):
        return {"entries": [{"field": "plain field", "applicability": "applies"}],
                "excluded_class_counts": {"a": 1},
                "excluded_class_shares": {"a": 1}}


class TestStoredFieldsValidation(unittest.TestCase):
    def test_version_stamp_subclass_forgery_fails(self):
        stamp = ForgedStamp({"family_version": "v1"})
        self.assertFalse(mod01.validate_version_stamp(stamp))
        self.assertFalse(mod01.validate_version_stamp(stamp, sealed_family_hash="h"))

    def test_plain_complete_stamp_still_passes(self):
        stamp = mod01.VersionStamp({"family_version": "v1",
                                     "family_manifest_hash": "h",
                                     "rule_version_set": "r1"})
        self.assertTrue(mod01.validate_version_stamp(stamp, sealed_family_hash="h"))

    def test_provenance_subclass_forgery_fails(self):
        block = ForgedBlock([], {}, {})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_plain_complete_block_still_passes(self):
        block = mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}],
            {"a": 1}, {"a": 1})
        self.assertTrue(mod01.validate_provenance_block(block))


class TestProvenanceAccuracyForms(unittest.TestCase):
    def _block(self, field):
        return mod01.ProvenanceBlock(
            [{"field": field, "applicability": "applies"}], {"a": 1}, {"a": 1})

    def test_underscore_and_capitalised_forms_need_error_direction(self):
        self.assertFalse(mod01.validate_provenance_block(self._block("arbiter_accuracy_value")))
        self.assertFalse(mod01.validate_provenance_block(self._block("Arbiter accuracy value")))
        self.assertFalse(mod01.validate_provenance_block(self._block("arbiter accuracy value")))

    def test_accuracy_with_error_direction_passes(self):
        block = mod01.ProvenanceBlock(
            [{"field": "arbiter_accuracy_value", "applicability": "applies",
              "error_direction": "stated direction"}], {"a": 1}, {"a": 1})
        self.assertTrue(mod01.validate_provenance_block(block))


class TestProvenanceEmptyCountsShares(unittest.TestCase):
    def test_empty_dicts_fail(self):
        block = mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}], {}, {})
        self.assertFalse(mod01.validate_provenance_block(block))
        block = mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}], {}, {"a": 1})
        self.assertFalse(mod01.validate_provenance_block(block))
        block = mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}], {"a": 1}, {})
        self.assertFalse(mod01.validate_provenance_block(block))


class TestMinimalInstanceEntryKind(unittest.TestCase):
    def test_bogus_entry_kind_refused(self):
        with self.assertRaises(ValueError):
            mod01.minimal_valid_instance("36", entry_kind="bogus")

    def test_stated_kinds_still_build_and_validate(self):
        for kind in ("ordinary", "agent", "supersession"):
            instance = mod01.minimal_valid_instance("36", entry_kind=kind)
            self.assertTrue(mod01.validate_record("36", instance), kind)


class TestRecursionGuard(unittest.TestCase):
    def _deep(self, depth=600):
        value = {"leaf": "stated"}
        for _ in range(depth):
            value = {"nested": value}
        return value

    def test_deep_value_returns_false_not_recursion_error(self):
        instance = mod01.minimal_valid_instance("4")
        instance["annotation_link"] = self._deep(600)
        self.assertFalse(mod01.validate_record("4", instance))

    def test_cyclic_value_returns_false_not_recursion_error(self):
        instance = mod01.minimal_valid_instance("4")
        cyclic = {}
        cyclic["self"] = cyclic
        instance["annotation_link"] = cyclic
        self.assertFalse(mod01.validate_record("4", instance))

    def test_version_stamp_deep_copy_guarded(self):
        try:
            mod01.VersionStamp({"family_version": self._deep(600)})
        except RecursionError:
            self.fail("VersionStamp escaped as bare RecursionError")
        except ValueError:
            pass


class TestPartialMarking(unittest.TestCase):
    def test_absent_marked_partial_field_is_false(self):
        self.assertFalse(mod01.partial_record_is_marked(record={"partial": True}))

    def test_present_marking_still_read(self):
        self.assertTrue(mod01.partial_record_is_marked(
            record={"partial": True, "marked_partial": True}))
        self.assertFalse(mod01.partial_record_is_marked(
            record={"partial": True, "marked_partial": False}))


if __name__ == "__main__":
    unittest.main()

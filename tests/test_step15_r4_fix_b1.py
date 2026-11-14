# Step 15, second run, fix wave 3, Builder 1 pins. MOD-01 only.
# Rows R3-001, R3-012 and R3-060 of the Round 3 register.
import unittest

import crucible.mod01 as mod01


COMBINED_ANCHOR_NAME = (
    "@\u043d\u0441\u043dor_\u0441\u0441\u20ac\u043d@rio"
    "_v@\u00a3\u03c5\u20ac\u0441"
)
COMBINED_LATE_U_ONLY = (
    "@\u043d\u0441\u043dor_\u0441\u0441\u20ac\u043d@rio"
    "_v@\u00a3\u03c5\u20acs"
)
COMBINED_LATE_S_ONLY = (
    "@\u043d\u0441\u043dor_\u0441\u0441\u20ac\u043d@rio"
    "_v@\u00a3u\u20ac\u0441"
)
DRESSED_ANCHOR_NAME = "anchor_" + "\u0441\u0441enario" + "_values"


class HideKeys(dict):
    """A dict subclass whose items reading hides the named keys."""

    def __init__(self, stored, hidden):
        super().__init__(stored)
        self._hidden = frozenset(hidden)

    def items(self):
        return [
            (key, value) for key, value in dict.items(self)
            if key not in self._hidden
        ]

    def keys(self):
        return [
            key for key in dict.keys(self)
            if key not in self._hidden
        ]


def form4_with(key, value):
    instance = mod01.minimal_valid_instance("4")
    instance[key] = value
    return instance


class TestR3001RecordReadThroughBaseOperations(unittest.TestCase):
    def test_hidden_amount_and_currency_pair_fails(self):
        stored = form4_with("amount", 500)
        stored["currency"] = "USD"
        record = HideKeys(stored, ("amount", "currency"))
        self.assertEqual(dict.get(record, "amount"), 500)
        self.assertFalse(mod01.validate_record("4", record))

    def test_plain_amount_and_currency_pair_still_fails(self):
        stored = form4_with("amount", 500)
        stored["currency"] = "USD"
        self.assertFalse(mod01.validate_record("4", stored))

    def test_hidden_money_marker_field_fails(self):
        stored = form4_with("realmoney", 500)
        record = HideKeys(stored, ("realmoney",))
        self.assertFalse(mod01.validate_record("4", record))

    def test_hidden_pair_in_nested_record_fails(self):
        nested = HideKeys(
            {"amount": 500, "currency": "USD"}, ("amount", "currency"))
        stored = form4_with("nested_record", nested)
        record = HideKeys(stored, ())
        self.assertFalse(mod01.validate_record("4", record))

    def test_hidden_dressed_anchor_field_fails_at_four(self):
        stored = form4_with(DRESSED_ANCHOR_NAME, ["a", "b", "c", "d"])
        record = HideKeys(stored, (DRESSED_ANCHOR_NAME,))
        self.assertFalse(mod01.validate_record("4", record))

    def test_hidden_plain_anchor_field_fails_at_four(self):
        stored = mod01.minimal_valid_instance("4")
        stored["anchor_scenario_values"] = ["a", "b", "c", "d"]
        record = HideKeys(stored, ("anchor_scenario_values",))
        self.assertFalse(mod01.validate_record("4", record))

    def test_hidden_dressed_anchor_field_passes_at_three(self):
        stored = form4_with(DRESSED_ANCHOR_NAME, ["a", "b", "c"])
        record = HideKeys(stored, (DRESSED_ANCHOR_NAME,))
        self.assertTrue(mod01.validate_record("4", record))

    def test_hidden_benign_record_still_passes(self):
        stored = mod01.minimal_valid_instance("4")
        record = HideKeys(stored, ("amount", "currency"))
        self.assertTrue(mod01.validate_record("4", record))


class TestR3012CombinedAnchorVariantReading(unittest.TestCase):
    def test_combined_anchor_name_fails_at_four(self):
        bad = form4_with(COMBINED_ANCHOR_NAME, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))

    def test_combined_anchor_name_passes_at_three(self):
        good = form4_with(COMBINED_ANCHOR_NAME, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))

    def test_combined_anchor_name_matches_anchor_fold(self):
        self.assertTrue(mod01._folded_key_matches(
            COMBINED_ANCHOR_NAME, mod01._ANCHOR_VALUES_FIELD_FOLDED))

    def test_combined_name_with_late_u_need_fails_at_four(self):
        bad = form4_with(COMBINED_LATE_U_ONLY, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))

    def test_combined_name_with_late_s_need_fails_at_four(self):
        bad = form4_with(COMBINED_LATE_S_ONLY, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))

    def test_benign_anchor_like_name_passes_at_four(self):
        good = form4_with("combined_anchor_like_name", ["a", "b", "c", "d"])
        self.assertTrue(mod01.validate_record("4", good))


def provenance_block(counts, shares):
    return {
        "entries": [{"field": "plain field", "applicability": "applies"}],
        "excluded_class_counts": counts,
        "excluded_class_shares": shares,
    }


class TestR3060ProvenanceCountAndShareValues(unittest.TestCase):
    def test_text_count_fails(self):
        block = provenance_block({"a": "one"}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_text_share_fails(self):
        block = provenance_block({"a": 2}, {"a": "half"})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_text_count_and_share_fail(self):
        block = provenance_block({"a": "one"}, {"a": "half"})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_boolean_count_fails(self):
        block = provenance_block({"a": True}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_boolean_share_fails(self):
        block = provenance_block({"a": 2}, {"a": True})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_fractional_count_fails(self):
        block = provenance_block({"a": 1.5}, {"a": 0.5})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_text_values_in_block_object_fail(self):
        block = mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}],
            {"a": "one"}, {"a": "half"})
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_numeric_count_and_share_pass(self):
        block = provenance_block({"a": 2}, {"a": 0.5})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_zero_count_and_zero_share_pass(self):
        block = provenance_block({"a": 0}, {"a": 0})
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_whole_share_passes(self):
        block = provenance_block({"a": 1}, {"a": 1})
        self.assertTrue(mod01.validate_provenance_block(block))


if __name__ == "__main__":
    unittest.main()

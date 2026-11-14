# Step 15 rerun, fix wave 2, builder b1 tests. MOD-01 surfaces only.
import unittest

import crucible.mod01 as mod01


def form4_with(key, value):
    instance = mod01.minimal_valid_instance("4")
    instance[key] = value
    return instance


def form4_pair(amount_key, amount_value, currency_key):
    instance = mod01.minimal_valid_instance("4")
    instance[amount_key] = amount_value
    instance[currency_key] = "stated"
    return instance


class TestR2015BothReadingsOfEsInScenario(unittest.TestCase):
    def test_es_at_both_positions_of_scenario_fails_at_four(self):
        key = "anchor_" + "\u0441\u0441enario" + "_values"
        bad = form4_with(key, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))
        good = form4_with(key, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))

    def test_es_at_c_of_anchor_and_s_of_scenario_fails_at_four(self):
        key = "an\u0441hor_" + "\u0441cenario" + "_values"
        bad = form4_with(key, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))
        good = form4_with(key, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))


class TestR2016BothReadingsInCurrencyKey(unittest.TestCase):
    def test_upsilon_at_both_positions_fails(self):
        instance = form4_pair("amount", 500, "c\u03c5rrenc\u03c5")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_cyrillic_u_at_both_positions_fails(self):
        instance = form4_pair("amount", 500, "c\u0443rrenc\u0443")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_amount_key_alone_still_passes(self):
        instance = mod01.minimal_valid_instance("4")
        instance["amount"] = 500
        self.assertTrue(mod01.validate_record("4", instance))


class TestR2017ArmenianVoUnReading(unittest.TestCase):
    def test_vo_standing_for_un_pair_fails(self):
        instance = form4_pair("amo\u0578t", 500, "currency")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_vo_capital_standing_for_un_pair_fails(self):
        instance = form4_pair("amo\u0548t", 500, "currency")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_vo_at_n_position_still_fails(self):
        instance = form4_pair("amou\u0578t", 500, "currency")
        self.assertFalse(mod01.validate_record("4", instance))


class TestR2018CyrillicEnAsHInAnchor(unittest.TestCase):
    def test_en_at_h_position_fails_at_four(self):
        key = "anc\u043dor_scenario_values"
        bad = form4_with(key, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))
        good = form4_with(key, ["a", "b", "c"])
        self.assertTrue(mod01.validate_record("4", good))

    def test_en_at_n_position_still_fails_at_four(self):
        key = "a\u043dchor_scenario_values"
        bad = form4_with(key, ["a", "b", "c", "d"])
        self.assertFalse(mod01.validate_record("4", bad))


class TestR2019CherokeeAndCopticMarker(unittest.TestCase):
    def test_cherokee_whole_marker_fails(self):
        key = ("\u13d2\u13ac\u13aa\u13de\u13b7"
               "\u13be\u13c1\u13ac\u13ef")
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))

    def test_cherokee_small_whole_marker_fails(self):
        key = ("\uaba2\uab7c\uab7a\uabae\uab87"
               "\uab8e\uab91\uab7c\uabbf")
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))

    def test_coptic_whole_marker_fails(self):
        key = ("\u2ca3\u2c89\u2c81\u2c97\u2c99"
               "\u2c9f\u2c9b\u2c89\u2ca9")
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))

    def test_single_cherokee_and_coptic_letters_fail(self):
        for key in ("\u13d2ealmoney", "re\u13aalmoney",
                    "\u2ca3ealmoney"):
            self.assertFalse(
                mod01.validate_record("4", form4_with(key, 500)), key)

    def test_mixed_cherokee_marker_fails(self):
        key = ("\u13d2\u1d07@\u029f\u1d0d\u0585"
               "\u0578\u1d07\u028f")
        self.assertFalse(mod01.validate_record("4", form4_with(key, 500)))

    def test_folded_money_key_reads_both_scripts(self):
        cherokee = ("\u13d2\u13ac\u13aa\u13de\u13b7"
                    "\u13be\u13c1\u13ac\u13ef")
        coptic = ("\u2ca3\u2c89\u2c81\u2c97\u2c99"
                  "\u2c9f\u2c9b\u2c89\u2ca9")
        expected = "real" + "money"
        self.assertEqual(mod01._folded_money_key(cherokee), expected)
        self.assertEqual(mod01._folded_money_key(coptic), expected)


class TestR2020SymbolSubstitutionsCST(unittest.TestCase):
    def test_anchor_cent_at_c_positions_fails_at_four(self):
        for key in ("an\u00a2hor_scenario_values",
                    "anchor_s\u00a2enario_values"):
            bad = form4_with(key, ["a", "b", "c", "d"])
            self.assertFalse(mod01.validate_record("4", bad), key)
            good = form4_with(key, ["a", "b", "c"])
            self.assertTrue(mod01.validate_record("4", good), key)

    def test_anchor_dollar_and_section_at_s_fails_at_four(self):
        for key in ("anchor_$cenario_values",
                    "anchor_\u00a7cenario_values"):
            bad = form4_with(key, ["a", "b", "c", "d"])
            self.assertFalse(mod01.validate_record("4", bad), key)
            good = form4_with(key, ["a", "b", "c"])
            self.assertTrue(mod01.validate_record("4", good), key)

    def test_currency_cent_first_letter_pair_fails(self):
        instance = form4_pair("amount", 500, "\u00a2urrency")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_amount_plus_last_letter_pair_fails(self):
        instance = form4_pair("amoun+", 500, "currency")
        self.assertFalse(mod01.validate_record("4", instance))


class TestR2041ProvenanceSeparatorRunsAndTab(unittest.TestCase):
    def _block(self, field, with_direction=False):
        entry = {"field": field, "applicability": "applies"}
        if with_direction:
            entry["error_direction"] = "stated direction"
        return mod01.ProvenanceBlock([entry], {"a": 1}, {"a": 1})

    def test_separator_runs_and_tabs_need_error_direction(self):
        for field in ("arbiter__accuracy__value",
                      "arbiter\taccuracy\tvalue",
                      "arbiter  accuracy  value",
                      "arbiter- accuracy value",
                      "arbiter__accuracy\tvalue"):
            self.assertFalse(
                mod01.validate_provenance_block(self._block(field)), field)

    def test_separator_run_with_error_direction_passes(self):
        block = self._block("arbiter__accuracy__value", with_direction=True)
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_dict_form_block_tab_name_needs_error_direction(self):
        block = {
            "entries": [{"field": "arbiter\taccuracy\tvalue",
                         "applicability": "applies"}],
            "excluded_class_counts": {"a": 1},
            "excluded_class_shares": {"a": 1},
        }
        self.assertFalse(mod01.validate_provenance_block(block))


class TestR2042ProvenanceMappingCountsShares(unittest.TestCase):
    def _block(self, counts, shares):
        return mod01.ProvenanceBlock(
            [{"field": "plain field", "applicability": "applies"}],
            counts, shares)

    def test_string_counts_and_shares_fail(self):
        self.assertFalse(mod01.validate_provenance_block(
            self._block("abc", "abc")))

    def test_list_counts_and_shares_fail(self):
        self.assertFalse(mod01.validate_provenance_block(
            self._block(["a"], ["a"])))

    def test_one_side_non_mapping_fails(self):
        self.assertFalse(mod01.validate_provenance_block(
            self._block("abc", {"a": 1})))
        self.assertFalse(mod01.validate_provenance_block(
            self._block({"a": 1}, ["a"])))

    def test_class_without_matching_share_fails(self):
        self.assertFalse(mod01.validate_provenance_block(
            self._block({"a": 1}, {"b": 1})))
        self.assertFalse(mod01.validate_provenance_block(
            self._block({"a": 1, "b": 2}, {"a": 1})))

    def test_class_with_none_count_or_share_fails(self):
        self.assertFalse(mod01.validate_provenance_block(
            self._block({"a": None}, {"a": 1})))
        self.assertFalse(mod01.validate_provenance_block(
            self._block({"a": 1}, {"a": None})))

    def test_populated_mappings_still_pass(self):
        self.assertTrue(mod01.validate_provenance_block(
            self._block({"a": 1}, {"a": 0.5})))
        self.assertTrue(mod01.validate_provenance_block(
            self._block({"a": 1, "b": 0}, {"a": 0.5, "b": 0})))


if __name__ == "__main__":
    unittest.main()

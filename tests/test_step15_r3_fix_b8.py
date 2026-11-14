"""Step 15 rerun fix wave 2, seat 8. MOD-12 items.

Pins for register rows R2-015, R2-016, R2-017, R2-018, R2-019,
R2-020, R2-036, R2-037, R2-038, and R2-056. Each test was
written before its cure and stood failing on the uncured tree,
except the R2-017 pin, which records a reading that already
stands at MOD-12 and stood passing before the cure.
"""
import unittest

from crucible import mod12


def run_with(key, value=500):
    return {"run_class": "screening", "seed_domain": "screening",
            key: value}


def pair(amount_key="amount", currency_key="currency"):
    return {"run_class": "screening", "seed_domain": "screening",
            amount_key: 5, currency_key: "test value"}


def nested_dict(depth):
    value = {}
    cursor = value
    for _ in range(depth):
        cursor["nested"] = {}
        cursor = cursor["nested"]
    return value


def frozenset_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = frozenset((value,))
    return value


class TestBothReadingsInOneName(unittest.TestCase):
    def test_r2_015_cyrillic_es_both_positions_of_scenario(self):
        key = "anchor_" + "\u0441\u0441" + "enario_values"
        self.assertFalse(mod12.validate_run_record(
            run_with(key, ["a", "b", "c", "d"])))
        self.assertTrue(mod12.validate_run_record(
            run_with(key, ["a", "b", "c"])))

    def test_r2_015_cyrillic_es_c_of_anchor_and_s_of_scenario(self):
        key = "an\u0441hor_" + "\u0441" + "cenario_values"
        self.assertFalse(mod12.validate_run_record(
            run_with(key, ["a", "b", "c", "d"])))

    def test_r2_016_upsilon_both_positions_of_currency(self):
        self.assertFalse(mod12.validate_run_record(
            pair(currency_key="c\u03c5rrenc\u03c5")))
        self.assertFalse(mod12.validate_run_record(
            pair(currency_key="c\u03c5rrency")))
        self.assertFalse(mod12.validate_run_record(
            pair(currency_key="currency".replace("y", "\u03c5"))))

    def test_r2_016_cyrillic_u_both_positions_of_currency(self):
        self.assertFalse(mod12.validate_run_record(
            pair(currency_key="c\u0443rrenc\u0443")))

    def test_r2_018_cyrillic_en_as_h_in_anchor(self):
        key = "anc\u043dor_scenario_values"
        self.assertFalse(mod12.validate_run_record(
            run_with(key, ["a", "b", "c", "d"])))
        self.assertTrue(mod12.validate_run_record(
            run_with(key, ["a", "b", "c"])))
        control = "a\u043dchor_scenario_values"
        self.assertFalse(mod12.validate_run_record(
            run_with(control, ["a", "b", "c", "d"])))


class TestAmountVoReference(unittest.TestCase):
    def test_r2_017_armenian_vo_un_reading_stands_at_mod12(self):
        self.assertFalse(mod12.validate_run_record(
            pair(amount_key="amo\u0578t")))
        self.assertFalse(mod12.validate_run_record(
            pair(amount_key="amo\u0548t")))
        self.assertFalse(mod12.validate_run_record(
            pair(amount_key="amou\u0578t")))


class TestCherokeeAndCopticMarker(unittest.TestCase):
    def test_r2_019_cherokee_whole_marker(self):
        marker = "".join(chr(code) for code in (
            0x13D2, 0x13AC, 0x13AA, 0x13DE, 0x13B7,
            0x13BE, 0x13C1, 0x13AC, 0x13EF))
        self.assertFalse(mod12.validate_run_record(run_with(marker)))
        self.assertFalse(mod12.validate_run_record(
            run_with(marker.lower())))
        self.assertFalse(mod12.validate_run_record(
            run_with("\u13d2ealmoney")))
        self.assertFalse(mod12.validate_run_record(
            run_with("re\u13aa" + "lmoney")))

    def test_r2_019_coptic_whole_marker(self):
        marker = "".join(chr(code) for code in (
            0x2CA3, 0x2C89, 0x2C81, 0x2C97, 0x2C99,
            0x2C9F, 0x2C9B, 0x2C89, 0x2CA9))
        self.assertFalse(mod12.validate_run_record(run_with(marker)))
        self.assertFalse(mod12.validate_run_record(
            run_with(marker.upper())))
        self.assertFalse(mod12.validate_run_record(
            run_with("\u2ca3ealmoney")))

    def test_r2_019_mixed_cherokee_with_cured_dresses(self):
        marker = "\u13d2" + "\u1d07" + "@" + "\u029f" + "\u1d0d" \
            + "\u0585" + "\u0578" + "\u1d07" + "\u028f"
        self.assertFalse(mod12.validate_run_record(run_with(marker)))


class TestSymbolSubstitutionsCST(unittest.TestCase):
    def test_r2_020_cent_sign_for_c(self):
        self.assertFalse(mod12.validate_run_record(run_with(
            "an\u00a2hor_scenario_values", ["a", "b", "c", "d"])))
        self.assertFalse(mod12.validate_run_record(run_with(
            "anchor_s\u00a2enario_values", ["a", "b", "c", "d"])))
        self.assertFalse(mod12.validate_run_record(
            pair(currency_key="\u00a2urrency")))
        self.assertTrue(mod12.validate_run_record(run_with(
            "an\u00a2hor_scenario_values", ["a", "b", "c"])))

    def test_r2_020_dollar_and_section_for_s(self):
        for symbol in ("$", "\u00a7"):
            self.assertFalse(mod12.validate_run_record(run_with(
                "anchor_" + symbol + "cenario_values",
                ["a", "b", "c", "d"])), symbol)
            self.assertTrue(mod12.validate_run_record(run_with(
                "anchor_" + symbol + "cenario_values",
                ["a", "b", "c"])), symbol)

    def test_r2_020_plus_for_t(self):
        self.assertFalse(mod12.validate_run_record(
            pair(amount_key="amoun+")))
        self.assertFalse(mod12.validate_run_record(
            pair(amount_key="amoun\u002b")))


class TestApplyFamilyEditBounds(unittest.TestCase):
    def test_r2_036_deep_record_refused_in_named_form(self):
        record = mod12.make_family_record(family_id="fam-b8-deep")
        record["payload"] = nested_dict(2000)
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change={"field": "value"})

    def test_r2_036_deep_change_refused_in_named_form(self):
        record = mod12.make_family_record(family_id="fam-b8-deep2")
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(
                record, change={"payload": nested_dict(2000)})

    def test_r2_036_cyclic_change_refused_in_named_form(self):
        record = mod12.make_family_record(family_id="fam-b8-cyc")
        change = {}
        change["self"] = change
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change=change)

    def test_r2_036_cyclic_record_refused_in_named_form(self):
        record = mod12.make_family_record(family_id="fam-b8-cyc2")
        record["loop"] = record
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change={"field": "value"})

    def test_r2_036_shallow_edit_still_lands(self):
        record = mod12.make_family_record(family_id="fam-b8-ok")
        edited = mod12.apply_family_edit(
            record, change={"payload": nested_dict(10)})
        self.assertIn("payload", edited)


class TestApplyFamilyEditEmptyClaims(unittest.TestCase):
    def test_r2_037_empty_headline_claims_read_as_empty(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b8-empty"))
        edited = mod12.apply_family_edit(
            sealed, change={"headline_claims": []})
        self.assertEqual(edited["headline_claims"], [])
        self.assertEqual(edited["claims"], [])
        self.assertEqual(edited["kill_check_fields"], [])
        self.assertEqual(edited["kill_checks"], [])

    def test_r2_037_clearing_both_lists_leaves_no_stale_kill_check(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b8-empty2"))
        edited = mod12.apply_family_edit(
            sealed, change={"claims": [], "headline_claims": []})
        self.assertEqual(edited["headline_claims"], [])
        self.assertEqual(edited["kill_check_fields"], [])

    def test_r2_037_kill_check_naming_removed_claim_refused(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b8-stale"))
        stale = [mod12.kill_check_for_claim("headline claim 1")]
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(sealed, change={
                "headline_claims": [], "kill_check_fields": stale})
        broken = dict(sealed)
        broken["headline_claims"] = []
        broken["claims"] = []
        broken["kill_check_fields"] = stale
        self.assertFalse(mod12.validate_family_record(broken))


class TestShapeBoundAndFrozenset(unittest.TestCase):
    def test_r2_056_clean_record_at_depth_80_passes(self):
        record = {"run_class": "screening",
                  "seed_domain": "screening",
                  "payload": nested_dict(80)}
        self.assertTrue(mod12.validate_run_record(record))

    def test_r2_056_record_past_common_bound_refused(self):
        record = {"run_class": "screening",
                  "seed_domain": "screening",
                  "payload": nested_dict(150)}
        self.assertFalse(mod12.validate_run_record(record))

    def test_r2_038_frozenset_chain_past_bound_refused(self):
        for depth in (150, 500):
            record = {"run_class": "screening",
                      "seed_domain": "screening",
                      "payload": frozenset_chain(depth)}
            self.assertFalse(
                mod12.validate_run_record(record), depth)

    def test_r2_038_frozenset_chain_at_depth_80_passes(self):
        record = {"run_class": "screening",
                  "seed_domain": "screening",
                  "payload": frozenset_chain(80)}
        self.assertTrue(mod12.validate_run_record(record))

    def test_r2_038_mixed_frozenset_dict_chain_past_bound_refused(self):
        value = frozenset_chain(60)
        for _ in range(60):
            value = {"nested": value}
        record = {"run_class": "screening",
                  "seed_domain": "screening", "payload": value}
        self.assertFalse(mod12.validate_run_record(record))


if __name__ == "__main__":
    unittest.main()

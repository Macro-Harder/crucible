"""Step 15 second run fix wave, builder 8. MOD-12 items.

Pins for register rows R1-001, R1-004, R1-006 (MOD-12 limbs),
R1-026, R1-057, R1-058, R1-059, R1-063, R1-074, R1-090, R1-091.
Each test was written before its cure and stood failing on the
uncured tree.
"""
import pathlib
import unittest

from crucible import mod01, mod10, mod12


def run_with(key, value=500):
    return {"run_class": "screening", "seed_domain": "screening",
            key: value}


class TestLetterDresses(unittest.TestCase):
    def test_small_capital_marker(self):
        marker = "ʀᴇᴀʟᴍᴏɴᴇʏ"
        self.assertFalse(mod12.validate_run_record(run_with(marker)))
        for dressed in ("reᴀlmoney", "realmᴏney", "realmoneʏ"):
            self.assertFalse(
                mod12.validate_run_record(run_with(dressed)), dressed)

    def test_symbol_leet_marker(self):
        for dressed in ("re@lmoney", "r€almoney", "rea£money",
                        "rea!money", "rea|money", "realmone¥"):
            self.assertFalse(
                mod12.validate_run_record(run_with(dressed)), dressed)

    def test_symbol_leet_amount_currency_and_anchor(self):
        pair = {"run_class": "screening", "seed_domain": "screening",
                "@mount": 5, "currency": "test value"}
        self.assertFalse(mod12.validate_run_record(pair))
        pair = {"run_class": "screening", "seed_domain": "screening",
                "amount": 5, "currenc¥": "test value"}
        self.assertFalse(mod12.validate_run_record(pair))
        four = run_with("@nchor_scenario_values", ["a", "b", "c", "d"])
        self.assertFalse(mod12.validate_run_record(four))
        four = run_with("anchor_sc€nario_values", ["a", "b", "c", "d"])
        self.assertFalse(mod12.validate_run_record(four))
        three = run_with("@nchor_scenario_values", ["a", "b", "c"])
        self.assertTrue(mod12.validate_run_record(three))

    def test_armenian_marker_and_amount(self):
        self.assertFalse(mod12.validate_run_record(
            run_with("realmօney")))
        self.assertFalse(mod12.validate_run_record(
            run_with("realmoոey")))
        pair = {"run_class": "screening", "seed_domain": "screening",
                "amouոt": 5, "currency": "test value"}
        self.assertFalse(mod12.validate_run_record(pair))
        pair = {"run_class": "screening", "seed_domain": "screening",
                "amoոt": 5, "currency": "test value"}
        self.assertFalse(mod12.validate_run_record(pair))

    def test_cyrillic_c_anchor(self):
        key = "anchor_sсenario_values"
        self.assertFalse(mod12.validate_run_record(
            run_with(key, ["a", "b", "c", "d"])))
        self.assertTrue(mod12.validate_run_record(
            run_with(key, ["a", "b", "c"])))

    def test_t_with_stroke_amount_key(self):
        for amount_key in ("amounŧ", "amounŦ"):
            pair = {"run_class": "screening",
                    "seed_domain": "screening",
                    "payload": {amount_key: 5, "currency": "test value"}}
            self.assertFalse(mod12.validate_run_record(pair), amount_key)


class TestDependencyAndCompleteness(unittest.TestCase):
    def test_no_mod13_and_run_records_through_mod10(self):
        source = pathlib.Path(mod12.__file__).read_text(encoding="utf-8")
        self.assertNotIn("mod13", source)
        self.assertIn("mod10", source)
        mod10.reset_stores()
        try:
            mod10.retain_run_record(
                {"run_id": "run-b8", "run_class": "screening"})
            read_back = mod12.retained_run_record("run-b8")
            self.assertEqual(read_back["run_id"], "run-b8")
        finally:
            mod10.reset_stores()

    def test_completeness_fields_are_form_1_fields(self):
        self.assertEqual(
            tuple(mod12.FAMILY_COMPLETENESS_ITEMS),
            tuple(mod01.COMPLETENESS_FIELDS))
        record = mod12.make_family_record(family_id="fam-b8")
        for quantity in ("confidence interval method",
                         "numeric equivalence margin",
                         "named two sample distributional test"):
            self.assertNotIn(quantity, record)
        sealed = mod12.seal_family_record(record)
        self.assertTrue(sealed["sealed"])
        broken = mod12.make_family_record(family_id="fam-b8")
        del broken[mod01.COMPLETENESS_FIELDS[0]]
        self.assertFalse(mod12.validate_family_record(broken))
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record(broken)


class TestRunClassMarkings(unittest.TestCase):
    def test_seed_domains_in_closed_vocabulary(self):
        markings = mod12.run_class_markings()
        for marking in markings.values():
            self.assertIn(marking["seed_domain"],
                          ("screening", "held out confirmation"))
        self.assertEqual(
            markings["confirmation"]["seed_domain"],
            "held out confirmation")


class TestDepthAndCycleGuard(unittest.TestCase):
    def test_deep_record_returns_false(self):
        value = {}
        cursor = value
        for _ in range(5000):
            cursor["nested"] = {}
            cursor = cursor["nested"]
        record = {"run_class": "screening", "seed_domain": "screening",
                  "payload": value}
        self.assertFalse(mod12.validate_run_record(record))

    def test_cyclic_record_returns_false(self):
        value = {}
        value["self"] = value
        record = {"run_class": "screening", "seed_domain": "screening",
                  "payload": value}
        self.assertFalse(mod12.validate_run_record(record))


class TestManifestAndEdit(unittest.TestCase):
    def test_sweep_manifest_form_23_and_seal_match(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b8"))
        manifest = mod12.sweep_manifest(sealed)
        for field in ("family_identifier", "family_version",
                      "sealed_family_record_hash"):
            self.assertIn(field, manifest)
        self.assertTrue(
            mod01.validate_family_seal_match(manifest, sealed))
        self.assertTrue(mod01.validate_family_seal_match(
            sealed["sweep_manifest"], sealed))

    def test_edit_to_sealed_family(self):
        sealed = mod12.seal_family_record(
            mod12.make_family_record(family_id="fam-b8"))
        edited = mod12.apply_family_edit(
            sealed, change={"headline_claims": ["new claim"]})
        self.assertNotEqual(edited["family_identifier"], "fam-b8")
        self.assertEqual(edited["family_identifier"], edited["family_id"])
        self.assertEqual(
            mod12.sweep_manifest(edited)["family_identifier"],
            edited["family_id"])
        claims_named = [check.get("claim")
                        for check in edited["kill_check_fields"]]
        self.assertEqual(claims_named, ["new claim"])
        self.assertFalse(edited.get("seal"))
        self.assertFalse(edited.get("seal_hash"))


if __name__ == "__main__":
    unittest.main()

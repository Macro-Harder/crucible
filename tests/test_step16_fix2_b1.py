"""Step 16 fix wave 2, Builder 1: rows F2-01 and F2-02.

Test first tests for the two rows charged to Builder 1 in
design/steps/step-16-fix2-charge.md section 1, under rulings
T16-23 and T16-26 at design/steps/step-16-r2-register.md
section 5. Bench basis for every figure in the fix paper:
bench Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import unittest

from crucible import mod01, mod12


GENERIC_FALLBACK_WORDING = "a stated rule of this form stands unmet"

# The named carriage keys of a made family record, enumerated
# first hand from the made record construction at
# crucible/mod12.py make_family_record against the Form 1 field
# list and the completeness fields: the keys a made record
# carries that stand outside the Form 1 fields and outside the
# completeness fields of MOD-01.
EXPECTED_CARRIAGE_KEYS = {
    "family_version",
    "family_manifest_hash",
    "family_id",
    "sealed",
    "claims",
    "kill_checks",
    "registry_basis_fields",
    "results_seen",
    "form",
    "alias_keys",
    "completeness_presentation",
}


def _named_entry(failures, field):
    for entry in failures:
        if ("field " + field + ":") in entry:
            return entry
    return None


class TestF201ReportableExtraField(unittest.TestCase):

    def test_made_record_carriage_keys_enumerated(self):
        record = mod12.make_family_record("family-f2-01")
        outside = {
            key for key in record
            if key not in mod01.form_fields("1")
            and key not in mod01.COMPLETENESS_FIELDS
        }
        self.assertEqual(outside, EXPECTED_CARRIAGE_KEYS)
        self.assertEqual(len(outside), 11)

    def test_made_record_only_carriage_keys_stays_reportable(self):
        record = mod12.make_family_record("family-f2-01")
        judgement = mod01.run_is_reportable("1", record)
        self.assertFalse(judgement)
        self.assertFalse(judgement.truth_value)
        self.assertTrue(judgement.value)
        self.assertTrue(judgement.reportable_ready is False or
                        judgement.standing)

    def test_made_record_extra_field_refused_and_named(self):
        record = mod12.make_family_record("family-f2-01")
        record["zzzz_extra_field_not_in_form"] = "extra value"
        judgement = mod01.run_is_reportable("1", record)
        self.assertFalse(judgement)
        self.assertIn(
            "zzzz_extra_field_not_in_form", judgement.standing)

    def test_minimal_record_extra_field_refused_and_named(self):
        record = mod01.minimal_valid_family_record()
        record["zzzz_extra_field_not_in_form"] = "extra value"
        judgement = mod01.run_is_reportable("1", record)
        self.assertFalse(judgement)
        self.assertIn(
            "zzzz_extra_field_not_in_form", judgement.standing)


class TestF202NamedValueRuleFailures(unittest.TestCase):

    def test_placeholder_completeness_value_names_field(self):
        record = mod01.minimal_valid_family_record()
        record["farm_size_steps"] = "stated value"
        record["farm size steps"] = "stated value"
        failures = mod01.record_validation_failures("1", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(failures, "farm_size_steps")
        self.assertIsNotNone(entry)
        self.assertIn("placeholder", entry)
        self.assertIn("next step:", entry)

    def test_bare_scalar_completeness_value_names_field(self):
        record = mod01.minimal_valid_family_record()
        record["patience_steps"] = 5
        record["patience steps"] = 5
        failures = mod01.record_validation_failures("1", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(failures, "patience_steps")
        self.assertIsNotNone(entry)
        self.assertIn("next step:", entry)

    def test_diverged_completeness_pair_names_field(self):
        record = mod01.minimal_valid_family_record()
        record["farm_size_steps"] = "one supplied text"
        record["farm size steps"] = "a different supplied text"
        failures = mod01.record_validation_failures("1", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(failures, "farm_size_steps")
        self.assertIsNotNone(entry)
        self.assertIn("diverged", entry)
        self.assertIn("farm size steps", entry)
        self.assertIn("next step:", entry)

    def test_prototype_order_form1_names_field_value_rule(self):
        record = mod01.minimal_valid_family_record()
        record["scheduling_order_identifier"] = "prototype order"
        failures = mod01.record_validation_failures("1", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(
            failures, "scheduling_order_identifier")
        self.assertIsNotNone(entry)
        self.assertIn("prototype order", entry)
        self.assertIn("bar", entry)
        self.assertIn("next step:", entry)

    def test_prototype_order_form4_names_field_value_rule(self):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = "prototype order"
        failures = mod01.record_validation_failures("4", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(
            failures, "scheduling_order_identifier")
        self.assertIsNotNone(entry)
        self.assertIn("prototype order", entry)
        self.assertIn("bar", entry)

    def test_form22_reported_with_failed_confirmation_names_field(self):
        record = mod01.minimal_valid_instance("22")
        record["outcome"] = "reported"
        record["confirmation_outcome"] = "failed"
        failures = mod01.record_validation_failures("22", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
        entry = _named_entry(failures, "confirmation_outcome")
        self.assertIsNotNone(entry)
        self.assertIn("failed", entry)
        self.assertIn("next step:", entry)


if __name__ == "__main__":
    unittest.main()

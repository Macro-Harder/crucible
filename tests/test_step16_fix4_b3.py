"""Step 16 fix wave 4, Builder 3: row F4-03.

Test first tests for the row charged to Builder 3 in
design/steps/step-16-fix4-charge.md section 1, under ruling
T16-51 at design/steps/step-16-r4-register.md section 5: the
multi fault naming rule at record_validation_failures in
crucible/mod01.py. The cure bound, in the ruling own terms:
the naming rule of T16-40 applies on multi fault records in
full, every fault named by field against the inner judgement
whether or not a dedicated entry also stands.

The defect as filed (Round 4 Red 4, finding R4-RED4-N01):
the diagnosis extension of the F3-02 cure runs only where
the failures list stands empty, so where one fault on a
record draws a dedicated entry, a simultaneous inner only
fault is named nowhere. The named case of the finding: a
Form 4 record carrying an anchor_scenario_values value with
a count other than three beside a bad calibration_claim_field
returns the calibration entry alone.

These tests pin three standings. First, the named case and
further pairings of a dedicated fault with a simultaneous
inner only fault: both faults stand named by field. Second,
single fault records name their fault exactly as on the
landed tree: one entry, for the one fault, in its standing
form, whether the fault is dedicated, inner only, or the
missing spelling limb. Third, the generic fallback sentence
drawn by no fault at this door on the landed tree stays
drawn by no fault: its count in crucible/mod01.py stands
at 0 before this cure and stands at 0 after it.

Bench basis for every figure in the fix paper: bench
Python 3.14.4, Carry 6.

Copyright: J.P. Picard aka Macro-Harder.
"""

import copy
import pathlib
import unittest

from crucible import mod01


GENERIC_FALLBACK_WORDING = "a stated rule of this form stands unmet"


def _named_entries(failures, field):
    return [
        entry for entry in failures
        if ("field " + field + ":") in entry]


def _assert_both_named(case, form_id, record, first, second):
    failures = mod01.record_validation_failures(form_id, record)
    case.assertTrue(failures)
    for entry in failures:
        case.assertNotIn(GENERIC_FALLBACK_WORDING, entry)
    for field in (first, second):
        entries = _named_entries(failures, field)
        case.assertTrue(
            entries,
            "no entry names field " + field + " in "
            + repr(failures))
        case.assertIn("next step:", entries[0])
    return failures


def _bad_anchor_record():
    record = mod01.minimal_valid_instance("4")
    record["anchor_scenario_values"] = tuple(
        list(record["anchor_scenario_values"])[:2])
    return record


class TestMultiFaultNaming(unittest.TestCase):
    """A dedicated fault beside a simultaneous inner only
    fault: every fault stands named by field."""

    def test_named_case_anchor_count_beside_bad_calibration(self):
        record = _bad_anchor_record()
        record["calibration_claim_field"] = "xxx"
        failures = _assert_both_named(
            self, "4", record,
            "calibration_claim_field", "anchor_scenario_values")
        self.assertEqual(
            len(_named_entries(failures, "calibration_claim_field")),
            1)
        self.assertEqual(
            len(_named_entries(failures, "anchor_scenario_values")),
            1)

    def test_barred_order_beside_anchor_count(self):
        record = _bad_anchor_record()
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = "prototype order"
        failures = _assert_both_named(
            self, "4", record,
            "scheduling_order_identifier", "anchor_scenario_values")
        bar = _named_entries(
            failures, "scheduling_order_identifier")
        self.assertIn("prototype order bar", bar[0])

    def test_bad_calibration_beside_parameter_value_type(self):
        record = mod01.minimal_valid_instance("5")
        record["calibration_claim_field"] = "xxx"
        record["parameter_values"] = 5
        _assert_both_named(
            self, "5", record,
            "calibration_claim_field", "parameter_values")

    def test_bad_lien_state_beside_lost_contact_type(self):
        record = mod01.minimal_valid_instance("10")
        record["lien_state"] = "xxx"
        record["lost_contact_clause_on"] = 5
        _assert_both_named(
            self, "10", record,
            "lien_state", "lost_contact_clause_on")

    def test_two_dedicated_faults_beside_anchor_count(self):
        record = _bad_anchor_record()
        record["calibration_claim_field"] = "xxx"
        record["store_kind"] = "xxx"
        failures = _assert_both_named(
            self, "4", record,
            "calibration_claim_field", "anchor_scenario_values")
        _assert_both_named(
            self, "4", record,
            "store_kind", "anchor_scenario_values")
        for field in (
                "calibration_claim_field", "store_kind",
                "anchor_scenario_values"):
            self.assertEqual(
                len(_named_entries(failures, field)), 1,
                "field " + field + " named more than once in "
                + repr(failures))


class TestSingleFaultUnchanged(unittest.TestCase):
    """Controls: a single fault record names its fault
    exactly as on the landed tree, one entry for the one
    fault, and a valid record draws no entries."""

    def test_single_dedicated_calibration_one_entry(self):
        record = mod01.minimal_valid_instance("4")
        record["calibration_claim_field"] = "xxx"
        failures = mod01.record_validation_failures("4", record)
        self.assertEqual(len(failures), 1)
        entry = _named_entries(failures, "calibration_claim_field")
        self.assertEqual(len(entry), 1)
        self.assertIn(
            "the field stands in a stated form", entry[0])

    def test_single_inner_only_anchor_one_entry(self):
        record = _bad_anchor_record()
        failures = mod01.record_validation_failures("4", record)
        self.assertEqual(len(failures), 1)
        self.assertEqual(
            len(_named_entries(failures, "anchor_scenario_values")),
            1)

    def test_single_barred_order_one_entry(self):
        record = mod01.minimal_valid_instance("4")
        record["run_class"] = "headline"
        record["scheduling_order_identifier"] = "prototype order"
        failures = mod01.record_validation_failures("4", record)
        self.assertEqual(len(failures), 1)
        entry = _named_entries(
            failures, "scheduling_order_identifier")
        self.assertEqual(len(entry), 1)
        self.assertIn("prototype order bar", entry[0])

    def test_single_missing_spelling_one_entry(self):
        prose, slug = mod01.COMPLETENESS_KEY_PAIRS[0]
        record = mod01.minimal_valid_family_record()
        del record[prose]
        failures = mod01.record_validation_failures("1", record)
        self.assertEqual(len(failures), 1)
        entry = _named_entries(failures, slug)
        self.assertEqual(len(entry), 1)
        self.assertIn(prose, entry[0])

    def test_valid_form4_record_draws_no_entries(self):
        record = mod01.minimal_valid_instance("4")
        self.assertEqual(
            mod01.record_validation_failures("4", record), [])


class TestGenericFallbackAbsent(unittest.TestCase):
    """The generic fallback sentence of the door stands
    removed on the landed tree and this cure does not
    return it."""

    def test_generic_sentence_count_in_mod01_is_zero(self):
        source = pathlib.Path(mod01.__file__).read_text(
            encoding="utf-8")
        self.assertEqual(
            source.count(GENERIC_FALLBACK_WORDING), 0)

    def test_multi_fault_entries_carry_no_generic_wording(self):
        record = _bad_anchor_record()
        record["calibration_claim_field"] = "xxx"
        record["store_kind"] = "xxx"
        failures = mod01.record_validation_failures("4", record)
        self.assertTrue(failures)
        for entry in failures:
            self.assertNotIn(GENERIC_FALLBACK_WORDING, entry)


if __name__ == "__main__":
    unittest.main()

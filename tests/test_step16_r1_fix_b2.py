"""Step 16 Round 1 fix wave, builder 2 tests.

Rows R16-03, R16-04, R16-11, and R16-15: the family judgement
cluster. Test first: every test in this file was written against
the landed product at head d0fb43375412de52011e885e2f537d0086864bd7
and failed there for the reason its docstring states, except the
two pin controls, which passed there and must keep passing.

Supplied completeness values in this file are test inputs only,
standing for no design value and adopted nowhere (OP-16). No seed
is drawn, read from a clock, or assigned in completion order
(DQ7-02). Bench Python 3.14.4 stands as the interpreter basis.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01
from crucible import mod12

PROSE = tuple(mod01.COMPLETENESS_FIELDS)
SLUGS = (
    "farm_size_steps",
    "patience_steps",
    "longer_horizon_value",
    "confidence_interval_method",
    "reporting_resolution_per_trace",
    "decay_arm_donor_items",
)
MARKER = "open: OP-13 value stands open"


def supplied_family():
    record = mod01.minimal_valid_family_record()
    for prose, slug in zip(PROSE, SLUGS):
        value = "supplied test value for " + slug
        record[prose] = value
        record[slug] = value
    return record


class TestR1603ValidationStanding(unittest.TestCase):
    def test_standing_names_placeholder_fields_on_sweep_point(self):
        instance = mod01.minimal_valid_instance("2")
        result = mod01.validation_standing("2", instance)
        self.assertTrue(result["valid"])
        self.assertIn("population_size", result["placeholder_fields"])
        self.assertIn("run_length_in_days", result["placeholder_fields"])
        self.assertIn("template", result["standing"])

    def test_standing_distinguishes_template_from_real_values(self):
        template = mod01.validation_standing(
            "2", mod01.minimal_valid_instance("2"))
        instance = mod01.minimal_valid_instance("2")
        instance["population_size"] = 200
        instance["run_length_in_days"] = 180
        real = mod01.validation_standing("2", instance)
        self.assertNotIn("population_size", real["placeholder_fields"])
        self.assertNotEqual(template["standing"], real["standing"])

    def test_standing_names_placeholder_fields_on_run_record(self):
        result = mod01.validation_standing(
            "4", mod01.minimal_valid_instance("4"))
        self.assertTrue(result["valid"])
        self.assertIn("population_size", result["placeholder_fields"])
        self.assertIn("template", result["standing"])

    def test_standing_names_open_marker_fields_on_family(self):
        result = mod01.validation_standing(
            "1", mod01.minimal_valid_family_record())
        self.assertTrue(result["valid"])
        for prose in PROSE:
            self.assertIn(prose, result["open_marker_fields"])
        self.assertIn("open", result["standing"])


class TestR1603ReportableStanding(unittest.TestCase):
    def test_family_judgement_states_open_standing(self):
        result = mod01.family_supports_reportable_run(
            mod01.minimal_valid_family_record())
        self.assertFalse(result)
        self.assertFalse(result.truth_value)
        self.assertTrue(result.value)
        self.assertIn("open", result.standing)
        for prose in PROSE:
            self.assertIn(prose, result.open_fields)
        self.assertIn("open", repr(result))

    def test_run_is_reportable_family_states_open_standing(self):
        result = mod01.run_is_reportable(
            "1", mod01.minimal_valid_instance("1"))
        self.assertFalse(result)
        self.assertFalse(result.truth_value)
        self.assertTrue(result.value)
        self.assertIn("open", result.standing)
        self.assertTrue(result.open_fields)

    def test_judgement_over_open_markers_is_not_unqualified(self):
        result = mod01.family_supports_reportable_run(
            mod01.minimal_valid_family_record())
        self.assertIsNot(type(result), bool)
        self.assertFalse(result.reportable_ready)


class TestR1604Presentation(unittest.TestCase):
    def test_made_record_names_awaiting_supply_fields(self):
        record = mod12.make_family_record()
        presentation = mod12.family_record_presentation(record)
        for prose in PROSE:
            self.assertIn(prose, presentation["awaiting_supply_fields"])
        self.assertIn(
            "awaiting supply", presentation["standing"])
        self.assertNotIn(
            "scheduling_order_identifier",
            presentation["placeholder_fields"])
        self.assertEqual(presentation["placeholder_fields"], [])

    def test_made_record_carries_the_presentation(self):
        record = mod12.make_family_record()
        self.assertIn("completeness_presentation", record)
        carried = record["completeness_presentation"]
        for prose in PROSE:
            self.assertIn(prose, carried["awaiting_supply_fields"])
        self.assertFalse(carried["finished"])

    def test_sealed_record_does_not_present_as_finished(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        presentation = mod12.family_record_presentation(sealed)
        self.assertFalse(presentation["finished"])
        self.assertIn("awaiting supply", presentation["standing"])
        self.assertIn("completeness_presentation", sealed)
        self.assertFalse(sealed["completeness_presentation"]["finished"])
        self.assertIn(
            "not finished", sealed["completeness_presentation"]["standing"])


class TestR1611Aliases(unittest.TestCase):
    def test_nine_alias_pairs_marked_as_aliases(self):
        record = mod12.make_family_record()
        aliases = record["alias_keys"]
        self.assertEqual(aliases["family_id"], "family_identifier")
        self.assertEqual(aliases["claims"], "headline_claims")
        self.assertEqual(aliases["kill_checks"], "kill_check_fields")
        for prose, slug in zip(PROSE, SLUGS):
            self.assertEqual(aliases[prose], slug)
        self.assertEqual(len(aliases), 9)

    def test_completeness_pairs_named_at_mod01(self):
        pairs = dict(mod01.completeness_key_pairs())
        self.assertEqual(len(pairs), 6)
        for prose, slug in zip(PROSE, SLUGS):
            self.assertEqual(pairs[prose], slug)

    def test_diverged_claims_twin_named_not_silently_judged(self):
        record = mod12.make_family_record()
        record["claims"] = ["a claim standing nowhere else"]
        failures = mod12.family_record_validation_failures(record)
        self.assertTrue(
            any("diverged" in item and "claims" in item
                for item in failures), failures)
        self.assertFalse(mod12.validate_family_record(record))

    def test_diverged_completeness_twin_named(self):
        record = mod12.make_family_record()
        record["farm_size_steps"] = "supplied test value, one twin only"
        failures = mod12.family_record_validation_failures(record)
        self.assertTrue(
            any("diverged" in item and "farm" in item
                for item in failures), failures)
        result = mod01.family_supports_reportable_run(record)
        self.assertFalse(result)
        self.assertIn("farm size steps", result.diverged_fields)


class TestR1615OneCompletenessKeySet(unittest.TestCase):
    def test_supplied_values_validate_and_pass(self):
        record = supplied_family()
        self.assertTrue(mod01.validate_record("1", record))
        self.assertTrue(mod01.family_supports_reportable_run(record))
        self.assertTrue(mod01.run_is_reportable("1", record))
        made = mod12.make_family_record()
        for prose, slug in zip(PROSE, SLUGS):
            value = "supplied test value for " + slug
            made[prose] = value
            made[slug] = value
        self.assertEqual(mod12.family_record_validation_failures(made), [])
        self.assertTrue(mod12.validate_family_record(made))

    def test_supplied_step_lists_validate_and_pass(self):
        record = supplied_family()
        for prose, slug in (
                ("farm size steps", "farm_size_steps"),
                ("patience steps", "patience_steps")):
            record[prose] = ["step one", "step two"]
            record[slug] = ["step one", "step two"]
        self.assertTrue(mod01.validate_record("1", record))
        self.assertTrue(mod01.family_supports_reportable_run(record))

    def test_one_twin_edit_judged_once_as_diverged(self):
        record = supplied_family()
        record["farm size steps"] = "a different supplied test value"
        self.assertFalse(mod01.validate_record("1", record))
        self.assertFalse(mod01.family_supports_reportable_run(record))
        standing = mod01.completeness_standing(record)
        self.assertIn("farm size steps", standing["diverged_fields"])

    def test_bare_number_still_fails_the_completeness_bar(self):
        record = mod01.minimal_valid_family_record()
        record[PROSE[0]] = 1
        record[SLUGS[0]] = 1
        self.assertFalse(mod01.family_supports_reportable_run(record))
        self.assertFalse(mod01.validate_record("1", record))


class TestCompositionAndPins(unittest.TestCase):
    def test_marker_family_still_passes_tg013_pin(self):
        record = mod01.minimal_valid_family_record()
        for prose in PROSE:
            self.assertEqual(record[prose], MARKER)
        self.assertTrue(mod01.validate_record("1", record))
        judgement = mod01.family_supports_reportable_run(record)
        self.assertFalse(judgement)
        self.assertFalse(judgement.truth_value)
        self.assertTrue(judgement.value)

    def test_cures_compose_marker_and_supplied_standings_agree(self):
        marker = mod01.minimal_valid_family_record()
        marker_judgement = mod01.family_supports_reportable_run(marker)
        self.assertFalse(marker_judgement)
        self.assertFalse(marker_judgement.truth_value)
        self.assertTrue(marker_judgement.value)
        self.assertIn("open", marker_judgement.standing)
        supplied = supplied_family()
        supplied_judgement = mod01.family_supports_reportable_run(supplied)
        self.assertTrue(supplied_judgement)
        self.assertEqual(supplied_judgement.open_fields, ())
        for prose in PROSE:
            self.assertIn(prose, supplied_judgement.supplied_fields)
        self.assertTrue(supplied_judgement.reportable_ready)
        validation = mod01.validation_standing("1", supplied)
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["open_marker_fields"], [])


if __name__ == "__main__":
    unittest.main()

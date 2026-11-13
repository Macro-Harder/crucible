"""Step 15 Round 1 supplementary fix wave, Fix Builder 8 pins.

Cluster B: the MOD-02 and MOD-16 share of the MISSING items and
the severed limbs standing on those modules. Pins written test
first for TA-64, TA-65, C-47, TA-12, TB-50, C-39, and the MOD-02
limb of C-33, the MOD-02 limb of TA-61, the MOD-16 validator limb
of TA-13, and the MOD-16 surface of TA-30.
"""
import unittest

from crucible import mod02
from crucible import mod10
from crucible import mod11
from crucible import mod16


class TestTA64BatteryVerdictState(unittest.TestCase):
    def test_bogus_recorded_verdict_stands_gated_never_passed(self):
        state = mod02.battery_verdict_state(
            inter_stream_element_recorded=True,
            verdict_recorded=True, verdict="indeterminate")
        self.assertEqual(state, "gated")
        self.assertNotEqual(state, "passed")

    def test_three_states_unchanged(self):
        for verdict in ("passed", "failed", "gated"):
            self.assertEqual(
                mod02.battery_verdict_state(
                    inter_stream_element_recorded=True,
                    verdict_recorded=True, verdict=verdict),
                verdict)

    def test_verdict_before_inter_stream_element_still_gated(self):
        self.assertEqual(
            mod02.battery_verdict_state(
                inter_stream_element_recorded=False,
                verdict_recorded=True, verdict="passed"),
            "gated")


class TestTA65EncodeCandidateInput(unittest.TestCase):
    def test_integer_value_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input({"a": 1})
        self.assertIn("not a recorded string", str(caught.exception))

    def test_boolean_value_refused(self):
        with self.assertRaises(ValueError):
            mod02.encode_candidate_input({"a": True})

    def test_float_value_refused(self):
        with self.assertRaises(ValueError):
            mod02.encode_candidate_input({"a": 1.5})

    def test_recorded_strings_encode_as_before(self):
        self.assertEqual(
            mod02.encode_candidate_input({"a": "one", "b": "two"}),
            mod02.encode_candidate_input({"b": "two", "a": "one"}))
        self.assertNotEqual(
            mod02.encode_candidate_input({"a": "1"}),
            mod02.encode_candidate_input({"a": "one"}))


class TestC47StreamFailureForms(unittest.TestCase):
    def test_exhausted_record_points_to_recovery_forms(self):
        result = mod02.draw_from_stream(
            stream_class="class a", position=1, carried_positions=1)
        self.assertEqual(result["failure"], "STREAM-EXHAUSTED")
        self.assertIn("recovery_forms", result)
        self.assertEqual(
            tuple(result["recovery_forms"]),
            tuple(mod02.stream_recovery_forms()))

    def test_missing_position_names_position_only(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="class a", carried_positions=3)
        message = str(caught.exception)
        self.assertIn("position", message)
        self.assertNotIn("carried", message)

    def test_missing_carried_positions_names_carried_only(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(stream_class="class a", position=0)
        message = str(caught.exception)
        self.assertIn("carried positions", message)
        self.assertNotIn("lacks a position", message)


class TestC33Mod02RefusalTextLimb(unittest.TestCase):
    def test_gated_refusals_carry_ground_and_next_step_in_words(self):
        refusals = [
            mod02.derive_seed({"derivation_version": "recommended form"}),
            mod02.derive_stream_seed({}),
            mod02.derive_stream_state([]),
            mod02.advance_stream_state({}),
            mod02.request_generator(),
            mod02.draw_from_stream(
                stream_class="class a", position=0, carried_positions=2),
        ]
        for refusal in refusals:
            self.assertEqual(refusal["failure"], "DERIVATION-GATED")
            self.assertEqual(refusal["gate"], "DQ7-02")
            self.assertFalse(refusal["seed_drawn"])
            self.assertIn("adoption record", refusal["ground_in_words"])
            self.assertTrue(refusal["next_step"])
            self.assertIn("operator", refusal["next_step"])


class TestTA61Mod02Limbs(unittest.TestCase):
    def test_checkpoint_generator_state_stream_keys_sorted(self):
        state = mod02.checkpoint_generator_state(
            run_id="run-under-test",
            stream_classes=["zebra class", "middle class", "alpha class"])
        self.assertEqual(
            list(state["stream_states"].keys()),
            ["alpha class", "middle class", "zebra class"])

    def test_resume_consumed_generator_state_stream_keys_sorted(self):
        state = mod02.resume_consumed_generator_state(
            run_id="run-under-test",
            stream_classes=["zebra class", "middle class", "alpha class"])
        self.assertEqual(
            list(state["stream_states"].keys()),
            ["alpha class", "middle class", "zebra class"])

    def test_run_record_derivation_fields_render_sorted(self):
        fields = mod02.run_record_derivation_fields({
            "derivation_version": "v1",
            "parameter_values": {"z": "last", "a": "first", "m": "mid"},
        })
        self.assertEqual(
            list(fields["parameter_values"].keys()), ["a", "m", "z"])
        self.assertEqual(
            fields["parameter_values"],
            {"a": "first", "m": "mid", "z": "last"})


class TestTB50FixtureRecordFailureForm(unittest.TestCase):
    def test_unknown_fixture_raises_named_failure(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record("F-99")
        failure = caught.exception.failure
        self.assertEqual(failure["fixture"], "F-99")
        self.assertEqual(failure["module"], "MOD-16")
        self.assertTrue(failure["ground"])
        self.assertTrue(failure["name"])

    def test_known_fixture_unchanged(self):
        line = mod16.fixture_record("F-28")
        self.assertEqual(line["fixture"], "F-28")
        self.assertTrue(mod16.validate_fixture_record(line))


class TestTA30Mod16Surface(unittest.TestCase):
    def test_refusal_coverage_wrong_typed_inputs_return_false(self):
        self.assertFalse(mod16.validate_refusal_coverage(42))
        self.assertFalse(mod16.validate_refusal_coverage("text"))
        self.assertFalse(mod16.validate_refusal_coverage([42]))
        self.assertFalse(mod16.validate_refusal_coverage([{"refusal": "x"}]))

    def test_refusal_coverage_default_set_unchanged(self):
        self.assertTrue(mod16.validate_refusal_coverage())
        self.assertTrue(
            mod16.validate_refusal_coverage(mod16.refusal_set()))


class TestTA13Mod16ValidatorLimb(unittest.TestCase):
    def test_empty_records_fail_the_named_validators(self):
        self.assertFalse(mod16.validate_confirmation_result({}))
        self.assertFalse(mod16.validate_headline_claim({}))
        self.assertFalse(mod16.validate_horizon_generalisation({}))

    def test_complete_records_keep_their_standings(self):
        self.assertTrue(mod16.validate_confirmation_result(
            {"run_class": "confirmation",
             "seed_domain": "held out confirmation"}))
        self.assertFalse(mod16.validate_confirmation_result(
            {"run_class": "confirmation", "seed_domain": "screening"}))
        self.assertTrue(mod16.validate_headline_claim(
            {"headline_claim": False, "material": "validation"}))
        self.assertFalse(mod16.validate_headline_claim(
            {"headline_claim": True, "material": "validation"}))
        self.assertTrue(mod16.validate_horizon_generalisation(
            {"generalised_to_grid": False}))
        self.assertFalse(mod16.validate_horizon_generalisation(
            {"generalised_to_grid": True}))


class TestTA12ExerciseOwnsItsRecord(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_clean_case_builds_unit_with_builder_provenance(self):
        result = mod16.exercise_confirmation_and_headline()
        headline = result["headline"]
        self.assertTrue(headline["unit_built"])
        unit = headline["unit"]
        self.assertTrue(mod11.validate_headline_unit(unit))
        provenance = unit["checkability_fields"]
        self.assertIsInstance(provenance, dict)
        self.assertEqual(provenance["record"], "validation-headline-1")
        self.assertTrue(provenance["inside_unit"])

    def test_foreign_record_is_named_failure_and_no_unit_built(self):
        mod10.retain_run_record({
            "run_id": "validation-headline-1",
            "run_identifier": "validation-headline-1",
            "foreign": True,
        }, store_kind="sweep")
        result = mod16.exercise_confirmation_and_headline()
        headline = result["headline"]
        self.assertFalse(headline["unit_built"])
        self.assertIsNone(headline["unit"])
        self.assertIn("failure", headline)
        self.assertTrue(headline["failure"]["name"])
        standing = mod10.read_run_record(
            "validation-headline-1", store_kind="sweep")
        self.assertTrue(standing["foreign"])

    def test_failure_after_retention_leaves_no_partial_record(self):
        original = mod11.build_headline_unit_from_run

        def raising(*args, **kwargs):
            raise RuntimeError("forced mid act failure")

        mod16.mod11.build_headline_unit_from_run = raising
        try:
            result = mod16.exercise_confirmation_and_headline()
        finally:
            mod16.mod11.build_headline_unit_from_run = original
        headline = result["headline"]
        self.assertFalse(headline["unit_built"])
        self.assertIsNone(headline["unit"])
        self.assertTrue(headline["failure"]["name"])
        with self.assertRaises(mod10.LookupFailure):
            mod10.read_run_record(
                "validation-headline-1", store_kind="sweep")


class TestC39F01ReadableUnit(unittest.TestCase):
    def test_f01_unit_readable_in_full_with_failed_parts_named(self):
        record = mod16.f01_centre_only_unit()
        self.assertEqual(record["fixture"], "F-01")
        self.assertTrue(record["warning_example"])
        self.assertFalse(record["headline_claim"])
        unit = record["unit"]
        self.assertIn(
            "W-CENTRE-ONLY",
            unit["headline_unit_identifier_and_issue_date"])
        self.assertIn("6.85", unit["claim_sentence"])
        self.assertEqual(unit["holding_region"], "the typical point")
        self.assertEqual(unit["failure_region"], "none stated")
        failed = [part["check"] for part in record["failed_parts"]]
        self.assertEqual(
            failed,
            ["T-02", "T-03", "T-04", "T-05", "T-06",
             "T-07", "T-08", "T-10", "T-11"])
        for part in record["failed_parts"]:
            self.assertTrue(part["part"])
            self.assertTrue(part["how"])
        tally = mod11.retirement_tally("F-01")
        self.assertEqual(record["retirement_tally"]["passed"],
                         tally["passed"])
        self.assertEqual(record["retirement_tally"]["failed"],
                         tally["failed"])
        self.assertEqual(record["retirement_tally"]["not_applicable"],
                         tally["not_applicable"])
        self.assertTrue(record["retirement_tally"]
                        ["centre_quarantine_breach"])

    def test_f01_inventory_entry_stands_beside_the_unit(self):
        line = mod16.fixture_record("F-01")
        self.assertEqual(line["fixture"], "F-01")
        self.assertIn("centre only", line["showed"])


if __name__ == "__main__":
    unittest.main()

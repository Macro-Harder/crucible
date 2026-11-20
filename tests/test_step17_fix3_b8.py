"""Step 17 fix wave 3, Builder 8 defect tests.

Slice 8, the reporter and controller rows: FW3-08, FW3-14,
FW3-17, FW3-24, FW3-31, FW3-35, FW3-36, FW3-37, FW3-38,
FW3-40, FW3-41, FW3-52, and FW3-53, as charged at
design/steps/step-17-fix3-charge.md and stated at the Round 2
register rulings T17R2-08, T17R2-14, T17R2-17, T17R2-24,
T17R2-31, T17R2-35, T17R2-36, T17R2-37, T17R2-38, T17R2-40,
T17R2-41, T17R2-52, and T17R2-53. Each defect test reproduces
its filing defect on the uncured tree and passes on the cured
tree. The two scaling rows, FW3-14 and FW3-31, state the
growth form they charge and the bound the cure states: the
defect stands as the quadratic distinctness form standing
unbounded on the uncured tree, and the timing figures inside
those tests stand as measurements beside the form, never as
the verdict of the test on their own. Control tests pin the
standings that already hold.
"""
import time
import unittest

import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod12 as mod12
import crucible.mod14 as mod14


def _best_time(act, repeats=3):
    best = None
    for _ in range(repeats):
        start = time.perf_counter()
        act()
        elapsed = time.perf_counter() - start
        if best is None or elapsed < best:
            best = elapsed
    return best


class TestFW308ClosedTopUpBounds(unittest.TestCase):
    def test_defect_lower_bound_applies_at_mod12(self):
        self.assertTrue(mod12.top_up_applies(0.1, 30))

    def test_defect_upper_bound_applies_at_mod12(self):
        self.assertTrue(mod12.top_up_applies(0.9, 30))

    def test_control_doors_agree_inside_and_outside(self):
        self.assertTrue(mod11.top_up_applies(0.1))
        self.assertTrue(mod11.top_up_applies(0.9))
        self.assertTrue(mod12.top_up_applies(0.5, 30))
        self.assertFalse(mod12.top_up_applies(0.05, 30))
        self.assertFalse(mod12.top_up_applies(0.95, 30))
        self.assertFalse(mod12.top_up_applies(0.1, 29))
        self.assertFalse(mod12.top_up_applies(0.0, 30))
        self.assertFalse(mod12.top_up_applies(1.0, 30))


class TestFW314SampleStatementGrowth(unittest.TestCase):
    def _runs(self, count):
        return [{"run_id": "r-%d" % index, "run_class": "screening"}
                for index in range(count)]

    def test_defect_growth_form_bounded(self):
        # Charged form: quadratic in the runs handed in, through
        # a scan of every kept name per run and a list count per
        # rendered name. Cure bound: linear in the runs handed
        # in. The ratio of the best measured times at 2,000 and
        # at 500 runs stands as a measurement beside the form:
        # the quadratic form measures near 16, the linear form
        # near 4, and the stated bound stands at 8.
        small = self._runs(500)
        large = self._runs(2000)
        self.assertEqual(mod12.sample_statement(large)["n"], 2000)
        small_time = _best_time(lambda: mod12.sample_statement(small))
        large_time = _best_time(lambda: mod12.sample_statement(large))
        self.assertLess(large_time / small_time, 8.0)

    def test_control_duplicate_names_count_once(self):
        run = {"run_id": "r-1", "run_class": "screening"}
        result = mod12.sample_statement([run, dict(run)])
        self.assertEqual(result["n"], 1)

    def test_control_printed_name_pair_counts_once(self):
        runs = [{"run_id": 5, "run_class": "screening"},
                {"run_id": "5", "run_class": "screening"}]
        self.assertEqual(mod12.sample_statement(runs)["n"], 1)


class TestFW317LocationForEndpoint(unittest.TestCase):
    def _figure(self, share):
        return {"cumulative_incidence": {"regime": {"share": share}}}

    def test_defect_share_in_no_finite_form_refused(self):
        for share in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError) as caught:
                mod11.location_for_endpoint(
                    self._figure(share), "regime", 0.5)
            self.assertIn("location_for_endpoint stands refused",
                          str(caught.exception))

    def test_defect_share_outside_range_refused(self):
        for share in (1.5, -0.1):
            with self.assertRaises(ValueError) as caught:
                mod11.location_for_endpoint(
                    self._figure(share), "regime", 0.5)
            self.assertIn("location_for_endpoint stands refused",
                          str(caught.exception))

    def test_defect_endpoint_in_no_judged_form_refused(self):
        for endpoint in (float("nan"), float("inf"), 1.5, -0.1):
            with self.assertRaises(ValueError) as caught:
                mod11.location_for_endpoint(
                    self._figure(0.5), "regime", endpoint)
            self.assertIn("location_for_endpoint stands refused",
                          str(caught.exception))

    def test_control_reached_and_unreached_stand(self):
        result = mod11.location_for_endpoint(
            self._figure(0.99), "regime", 0.9)
        self.assertEqual(result["share"], 0.99)
        self.assertIsNone(mod11.location_for_endpoint(
            self._figure(0.5), "regime", 0.9))
        self.assertIsNone(mod11.location_for_endpoint(
            self._figure(0.99), "absent regime", 0.9))


class TestFW324HeadlineBuildFromRun(unittest.TestCase):
    RUN_ID = "run-fw324-resolves"

    def setUp(self):
        mod10.reset_stores()
        mod10.retain_run_record({
            "run_id": self.RUN_ID,
            "run_identifier": self.RUN_ID,
            "record_state": "as retained",
        })

    def _valid_values(self):
        values = {field: "value for " + field
                  for field in mod11.HEADLINE_UNIT_FIELDS
                  if field not in ("checkability_fields",
                                   "run_registry_line")}
        values["claim_sentence"] = (
            "At the sampled points within the stated scope, the "
            "result holds for the sampled points only, and nothing "
            "is claimed beyond the stated limits.")
        values["grounding_sentence"] = (
            "This unit rests on the retained run records within "
            "the stated scope, and its limits are that nothing is "
            "claimed beyond the sampled points in this unit.")
        values["qualifiers_and_markings_block"] = (
            "seam status: no cross seam effect; "
            "kill check: self checked only; "
            "dependence mark: DQ-164 confirmation form, recording "
            "that DQ-164 stands settled as confirmation only; "
            "Parley Q3 statement: no part of the result encodes "
            "Parley Q3 behaviour; "
            "core only qualifier: this unit is a core only result; "
            "anchor scenario statement: no anchor scenario is "
            "used in this unit.")
        return values

    def test_defect_non_mapping_values_named_ground_delivered(self):
        family = {}
        with self.assertRaises(ValueError) as caught:
            mod11.build_headline_unit_from_run(
                self.RUN_ID, "not a mapping", family_record=family)
        self.assertIn("make_headline_unit stands refused",
                      str(caught.exception))
        self.assertIn("stands in no record form",
                      str(caught.exception))
        self.assertNotIn("field absent", str(caught.exception))

    def test_defect_values_fault_uses_the_returned_channel(self):
        family = {}
        result = mod11.build_headline_unit_from_run(
            self.RUN_ID, {}, family_record=family)
        self.assertFalse(result["built"])
        self.assertIsNone(result["unit"])
        self.assertIn("field absent", result["failure"]["name"])
        self.assertEqual(family["named_failures"], [result["failure"]])

    def test_control_valid_values_build(self):
        result = mod11.build_headline_unit_from_run(
            self.RUN_ID, self._valid_values())
        self.assertTrue(result["built"])
        self.assertIsNone(result["failure"])

    def test_control_absent_run_named_failure_returned(self):
        family = {}
        result = mod11.build_headline_unit_from_run(
            "run-fw324-absent", {}, family_record=family)
        self.assertFalse(result["built"])
        self.assertEqual(result["failure"]["name"],
                         mod10.ONE_LOOKUP_FAILURE_NAME)
        self.assertEqual(family["named_failures"], [result["failure"]])


class TestFW331WeeklyCountGrowth(unittest.TestCase):
    def _records(self, count):
        return [{"week": 3, "headline_unit_identifiers": ["u%d" % index]}
                for index in range(count)]

    def test_defect_growth_form_linear(self):
        # Charged form: superlinear in the identifiers counted,
        # through a list membership scan over every identifier
        # already seen. Cure bound: linear in the identifiers
        # counted. The ratio of the best measured times at
        # 8,000 and at 2,000 records stands as a measurement
        # beside the form: the list scan form measures near 16,
        # the linear form near 4, and the stated bound stands
        # at 8.
        small = self._records(2000)
        large = self._records(8000)
        self.assertEqual(mod11.weekly_count(large, 3), 8000)
        small_time = _best_time(lambda: mod11.weekly_count(small, 3))
        large_time = _best_time(lambda: mod11.weekly_count(large, 3))
        self.assertLess(large_time / small_time, 8.0)

    def test_control_counts_units_once(self):
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(mod11.weekly_count(records, "W1"), 2)
        self.assertEqual(mod11.weekly_count(records, "W2"), 1)


class TestFW335MovedReading(unittest.TestCase):
    def test_defect_non_finite_change_refused(self):
        for delta in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError) as caught:
                mod11.moved_reading(delta, 0.5)
            self.assertIn("moved_reading stands refused",
                          str(caught.exception))

    def test_defect_resolution_in_no_admissible_form_refused(self):
        for resolution in (float("nan"), float("inf"), 0, -1.0):
            with self.assertRaises(ValueError) as caught:
                mod11.moved_reading(0.0, resolution)
            self.assertIn("moved_reading stands refused",
                          str(caught.exception))

    def test_control_plain_readings_stand(self):
        self.assertTrue(mod11.moved_reading(5, 3))
        self.assertFalse(mod11.moved_reading(1, 3))
        self.assertTrue(mod11.moved_reading(-5, 3))
        self.assertFalse(mod11.moved_reading(0.0, 0.5))


class TestFW336WinningRegime(unittest.TestCase):
    def test_defect_impossible_pairs_refused(self):
        for pair in ((float("inf"), 0.5), (float("nan"), 0.5),
                     (1.5, 0.4), (-0.5, -0.6), (0.6, 1.5),
                     (0.6, float("nan"))):
            with self.assertRaises(mod12.NamedControllerFailure) as caught:
                mod12.winning_regime([pair] * 30)
            self.assertIn("winning_regime stands refused",
                          str(caught.exception))

    def test_control_winning_and_losing_stand(self):
        self.assertTrue(mod12.winning_regime([(0.6, 0.4)] * 30))
        self.assertFalse(mod12.winning_regime([(0.4, 0.6)] * 30))
        self.assertFalse(mod12.winning_regime([(0.6, 0.4)] * 10))


class TestFW337ClassifyRunOutcome(unittest.TestCase):
    def test_defect_regime_class_in_no_judged_form_refused(self):
        for regime_class in (None, ["attacker"], "", 7):
            with self.assertRaises(ValueError) as caught:
                mod11.classify_run_outcome(40, regime_class)
            self.assertIn("classify_run_outcome stands refused",
                          str(caught.exception))

    def test_control_classified_and_short_runs_stand(self):
        result = mod11.classify_run_outcome(30, "steady")
        self.assertEqual(result["outcome"], "steady")
        self.assertTrue(result["contributes_to_transition_figure"])
        short = mod11.classify_run_outcome(20, "steady")
        self.assertEqual(short["outcome"], "horizon insufficient")
        self.assertFalse(short["contributes_to_transition_figure"])


class TestFW338WeeklyCountWeekForm(unittest.TestCase):
    def test_defect_mod11_nan_week_record_refused(self):
        records = [{"week": float("nan"),
                    "headline_unit_identifiers": ["u1"]}]
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(records, "W1")
        self.assertIn("no comparable form", str(caught.exception))

    def test_defect_mod11_nan_week_handing_refused(self):
        records = [{"week": "W1", "headline_unit_identifiers": ["u1"]}]
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(records, float("nan"))
        self.assertIn("no comparable form", str(caught.exception))

    def test_defect_mod14_nan_week_record_refused(self):
        records = [{"week": float("nan"),
                    "headline_unit_identifiers": ["u1"]}]
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.weekly_headline_count(records, "W1")
        self.assertIn("no comparable form", str(caught.exception))

    def test_defect_mod14_nan_week_handing_refused(self):
        records = [{"week": "W1", "headline_unit_identifiers": ["u1"]}]
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.weekly_headline_count(records, float("nan"))
        self.assertIn("no comparable form", str(caught.exception))

    def test_control_counts_stand_at_both_doors(self):
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(mod11.weekly_count(records, "W1"), 2)
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 2)


class TestFW340TransitionFigureCompetingExit(unittest.TestCase):
    def test_defect_text_competing_exit_refused(self):
        replicates = [{"competing_exit": "no",
                       "first_terminal_regime": "attacker"}]
        with self.assertRaises(ValueError) as caught:
            mod11.transition_figure(replicates)
        self.assertIn("transition_figure stands refused",
                      str(caught.exception))

    def test_defect_number_competing_exit_refused(self):
        for value in (1, 0, 1.0):
            replicates = [{"competing_exit": value,
                           "first_terminal_regime": "attacker"}]
            with self.assertRaises(ValueError) as caught:
                mod11.transition_figure(replicates)
            self.assertIn("transition_figure stands refused",
                          str(caught.exception))

    def test_control_boolean_standings_hold(self):
        competing = mod11.transition_figure(
            [{"competing_exit": True}])
        self.assertEqual(competing["competing_events"], 1)
        settled = mod11.transition_figure(
            [{"competing_exit": False,
              "first_terminal_regime": "attacker"},
             {"first_terminal_regime": "attacker"}])
        self.assertEqual(settled["competing_events"], 0)
        self.assertEqual(
            settled["cumulative_incidence"]["attacker"]["count"], 2)


class TestFW341ObservationTimePair(unittest.TestCase):
    def test_defect_builder_reversed_interval_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod11.record_first_observed(10, 5, 30)
        self.assertIn("record_first_observed stands refused",
                      str(caught.exception))

    def test_defect_builder_day_in_no_judged_form_refused(self):
        for handing in ((float("nan"), 5, 30), (5, float("inf"), 30),
                        (-1, 5, 30), (5, 10, float("nan"))):
            with self.assertRaises(ValueError) as caught:
                mod11.record_first_observed(*handing)
            self.assertIn("record_first_observed stands refused",
                          str(caught.exception))

    def test_defect_validator_reversed_or_unjudged_interval(self):
        for interval in ((10, 5), (float("nan"), 5), (-1, 5),
                         ("a", 5), (1.5, 5)):
            record = {"interval": interval, "exact_event_time": None}
            self.assertFalse(mod11.validate_observation_time(record))

    def test_control_built_interval_validates(self):
        record = mod11.record_first_observed(4, 5, 30)
        self.assertTrue(mod11.validate_observation_time(record))
        last = mod11.record_first_observed(29, 30, 30, is_last_day=True)
        self.assertTrue(mod11.validate_observation_time(last))
        self.assertTrue(mod11.validate_observation_time(
            {"interval": [1, 2]}))


class TestFW352FirstSentence(unittest.TestCase):
    def test_defect_handings_carrying_no_text_refused(self):
        for handing in (None, 123, {"a": 1}, [], 1.5, True):
            with self.assertRaises(ValueError) as caught:
                mod11.first_sentence(handing)
            self.assertIn("first_sentence stands refused",
                          str(caught.exception))

    def test_control_text_handings_stand(self):
        self.assertEqual(mod11.first_sentence("Real claim. More."),
                         "Real claim")
        self.assertEqual(mod11.first_sentence("Alpha beta. Gamma."),
                         "Alpha beta")


class TestFW353ReporterInputs(unittest.TestCase):
    def test_defect_non_record_handings_refused(self):
        for handing in ("ghost", None, ["records"], 7):
            with self.assertRaises(ValueError) as caught:
                mod11.reporter_inputs_for_family(handing)
            self.assertIn("reporter_inputs_for_family stands refused",
                          str(caught.exception))

    def test_control_record_handings_stand(self):
        empty = mod11.reporter_inputs_for_family({})
        self.assertIsNone(empty["divergence_count"])
        self.assertIsNone(empty["blocked_family_mark"])
        carried = mod11.reporter_inputs_for_family(
            {"divergence_count": 3})
        self.assertEqual(carried["divergence_count"], 3)
        self.assertIsNone(carried["blocked_family_mark"])


if __name__ == "__main__":
    unittest.main()

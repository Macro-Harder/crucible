"""Test group TG-10.4. AC-11 retention, sized and evidenced.

Slice S-10, MOD-10 Recorder and stores. Suite convention: this file tries to
import the product module for its slice, package crucible, module mod10, and
records whether the surface stands. While the surface stands absent, each non
gated test fails with a message naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
AC-11 guard form, binding on this file: the DECLARED NOT CLOSED state of the
late promotion gap is a non pass state. No test in this file records that
state, or retention resting on a declaration alone, as any form of pass.
"""
import unittest

try:
    from crucible import mod10
    SURFACE = mod10
    SURFACE_ERROR = None
except Exception as exc:
    SURFACE = None
    SURFACE_ERROR = exc

GROUP = "TG-10.4"
CENTRAL_FORM_EVENTS_PER_AGENT_DAY = 6.85


def require_surface(testcase, behaviour, *attrs):
    if SURFACE is None:
        testcase.fail(
            GROUP + ": product surface crucible.mod10 stands absent ("
            + repr(SURFACE_ERROR) + "); pinned behaviour cannot run: " + behaviour
        )
    for attr in attrs:
        if not hasattr(SURFACE, attr):
            testcase.fail(
                GROUP + ": product surface crucible.mod10 lacks " + attr
                + "; pinned behaviour cannot run: " + behaviour
            )


class TestSizingOnBothForms(unittest.TestCase):
    def test_sizing_on_both_forms(self):
        """Fixture: F-27, the retention sizing case, with fixture F-19, the event rate costing forms, supplying the high activity form, as TG-10.4 states.
        Pins: storage is sized on the high activity form as well as the central form, per AC-11, and the sizing record shows both workings with their provenance labels, derived over estimated form values.
        Bar: the central form at 6.85 events per agent per day is a spacing choice and not an expected rate, and the high form is a working form and not a ceiling.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, a sizing record missing either working or either provenance label fails.
        """
        require_surface(self, "retention sizing on both the central form and the high activity form", "retention_sizing")
        sizing = SURFACE.retention_sizing(fixture="F-27", costing_forms="F-19")
        self.assertIn("central_form", sizing["workings"])
        self.assertIn("high_form", sizing["workings"])
        self.assertEqual(
            sizing["workings"]["central_form"]["events_per_agent_per_day"],
            CENTRAL_FORM_EVENTS_PER_AGENT_DAY,
        )
        for working in sizing["workings"].values():
            self.assertIn("provenance", working)

    def test_sizing_central_alone_or_forecast_wording_fails(self):
        """Fixture: a sizing resting on the central form alone, and a sizing wording either form as a forecast or a ceiling, as TG-10.4 states.
        Pins: both forms fail validation.
        Bar: a sizing that rests on the central form alone, or that words either form as a forecast or a ceiling, fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, acceptance of either form fails.
        """
        require_surface(self, "central form alone and forecast or ceiling wording rejected", "validate_retention_sizing")
        self.assertFalse(SURFACE.validate_retention_sizing({"workings": {"central_form": {}}}))
        self.assertFalse(SURFACE.validate_retention_sizing(
            {"workings": {"central_form": {}, "high_form": {}}, "wording": {"central_form": "forecast"}}
        ))
        self.assertFalse(SURFACE.validate_retention_sizing(
            {"workings": {"central_form": {}, "high_form": {}}, "wording": {"high_form": "ceiling"}}
        ))


class TestRetentionMetOnlyByNamedRecord(unittest.TestCase):
    def test_complete_named_record_meets_form(self):
        """Fixture: a retention record for one run in its complete variant, naming the later evaluation of flag conditions 1, 2, and 3, its inputs and its outcome as written into the summary record, and the forms that record points to as retained for that run, as TG-10.4 states.
        Pins: retention is met only by that named record, per AC-11; the complete variant stands in the met form.
        Bar: DECLARED NOT CLOSED is a non pass state, and no reader, test, or suite summary may mark retention met on a declaration alone.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, a complete named record not standing as met fails.
        """
        require_surface(self, "retention met only by the named record of the later evaluation", "retention_met")
        record = {
            "later_evaluation": {"conditions": [1, 2, 3], "inputs": "recorded", "outcome": "recorded"},
            "summary_record_written": True,
            "retained_forms_pointed_to": True,
        }
        self.assertTrue(SURFACE.retention_met(record))

    def test_record_naming_no_later_evaluation_is_not_met(self):
        """Fixture: a retention record for one run naming no later evaluation, the second variant at TG-10.4.
        Pins: the record does not meet retention.
        Bar: retention is met only by the named record of the later evaluation of flag conditions 1, 2, and 3, its inputs and its outcome.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, a met verdict on this variant fails.
        """
        require_surface(self, "retention record naming no later evaluation is not met", "retention_met")
        record = {"later_evaluation": None, "summary_record_written": True}
        self.assertFalse(SURFACE.retention_met(record))

    def test_declaration_alone_is_non_pass_ac11_guard(self):
        """Fixture: a retention record for one run stating only that the late promotion gap is declared in words, the third variant at TG-10.4.
        Pins: the record does not meet retention; the AC-11 guard form holds, DECLARED NOT CLOSED is a non pass state.
        Bar: no test records the DECLARED NOT CLOSED state as any form of pass, and no suite summary may mark retention met on a declaration alone.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, any pass form recorded for this variant fails this test and the suite guard with it.
        """
        require_surface(self, "declaration alone is a non pass state under the AC-11 guard", "retention_met")
        record = {"declaration_only": "late promotion gap declared in words", "state": "DECLARED NOT CLOSED"}
        self.assertFalse(SURFACE.retention_met(record))


class TestPreRegisteredFullLogSample(unittest.TestCase):
    def test_sample_stands_in_family_record_before_runs(self):
        """Fixture: the family record inspected before runs, as TG-10.4 states.
        Pins: a pre registered full log sample of ordinary screening runs stands in the family record before runs, as a retention sample.
        Bar: the sample is a retention sample only; it is not the generator test battery sample.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, a family record with no such sample standing before runs fails.
        """
        require_surface(self, "pre registered full log sample stands in the family record before runs", "pre_registered_full_log_sample")
        sample = SURFACE.pre_registered_full_log_sample(family_id="family-under-test")
        self.assertIsNotNone(sample)
        self.assertEqual(sample["kind"], "retention_sample")
        self.assertEqual(sample["run_class"], "ordinary_screening")
        self.assertEqual(sample["family_id"], "family-under-test")
        self.assertTrue(sample["in_family_record"])
        self.assertEqual(sample["registration_standing"], "before_runs")

    def test_sample_outside_family_record_or_registered_after_runs_fails(self):
        """Fixture: a sample of the retention sample kind and the ordinary screening run class standing outside the family record, and a sample of the same kind and class registered after runs, as TG-10.4 states.
        Pins: each sample fails validation; the standing limb requires the sample to stand in the family record and to stand there before runs.
        Bar: the sample is a retention sample only; a sample of the right kind and class standing outside the family record, or registered after runs, does not satisfy this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, acceptance of either sample fails.
        """
        require_surface(self, "sample outside the family record or registered after runs rejected", "validate_sample_record")
        outside = {"kind": "retention_sample", "run_class": "ordinary_screening", "in_family_record": False, "registration_standing": "before_runs"}
        self.assertFalse(SURFACE.validate_sample_record(outside))
        late = {"kind": "retention_sample", "run_class": "ordinary_screening", "in_family_record": True, "registration_standing": "after_runs"}
        self.assertFalse(SURFACE.validate_sample_record(late))

    def test_sample_size_value_gated_on_family_record(self):
        """Fixture: the family record for a family whose sample size number stands unstated on it.
        Pins: no behaviour; this test records its state as gated on the family record stating the sample size before runs, the record waited on at plan section 2 section 10 line 2, the sample size number standing carried open at DQ7-03.
        Bar: no test states a sample size number the family record does not state.
        Failure: gated form only; this test never passes while the size stands unstated.
        """
        self.skipTest("gated on the family record stating the pre registered full log sample size before runs")

    def test_sample_conflated_with_battery_size_fails(self):
        """Fixture: a record presenting the retention sample size as the generator test battery sample size, as TG-10.4 states.
        Pins: the record fails validation.
        Bar: a test conflating the two sizes fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, acceptance of the conflated record fails.
        """
        require_surface(self, "retention sample size conflated with battery size rejected", "validate_sample_record")
        record = {"kind": "retention_sample", "presented_as": "generator_test_battery_sample"}
        self.assertFalse(SURFACE.validate_sample_record(record))


class TestRetentionStandingCarriedInSizing(unittest.TestCase):
    def test_sizing_rests_on_decided_subparts_only(self):
        """Fixture: F-27, the retention sizing case, with the retention record for one run, as TG-10.4 states.
        Pins: the sizing and retention statements in this group rest on the decided subparts of DQ7-03 and on no decided DQ7-08 rule while the reconciliation gate stands, as TG-10.2 states.
        Bar: a retention record presenting a DQ7-08 clause as its governing rule for reliance while the gate stands fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, a sizing resting on a DQ7-08 rule for reliance fails.
        """
        require_surface(self, "sizing rests on decided subparts of DQ7-03 and no DQ7-08 rule", "retention_sizing")
        sizing = SURFACE.retention_sizing(fixture="F-27", costing_forms="F-19")
        self.assertEqual(sizing["basis"], "DQ7-03 decided subparts")

    def test_retention_record_presenting_dq708_clause_fails(self):
        """Fixture: a retention record presenting a DQ7-08 clause as its governing rule for reliance while the gate stands, as TG-10.4 states.
        Pins: the record fails validation.
        Bar: a retention record presenting a DQ7-08 clause as its governing rule for reliance while the gate stands fails this group.
        Failure: while the surface stands absent the test fails naming this behaviour and TG-10.4; with the surface present, acceptance of the record fails.
        """
        require_surface(self, "retention record presenting a DQ7-08 clause as governing rejected", "validate_retention_record")
        record = {"governing_rule": "DQ7-08 clause C10", "reliance": "governing"}
        self.assertFalse(SURFACE.validate_retention_record(record))


if __name__ == "__main__":
    unittest.main()

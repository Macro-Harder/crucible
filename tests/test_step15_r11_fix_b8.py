"""Step 15 rerun fix wave 10 pins, Builder 8, at crucible/mod13.py.

Rows pinned: R10-009 (retained count bearing filter), R10-010
(expected count derived from the family record replicate plan as
sealed in the FamilyManifest), R10-011 MOD-13 limb (shortfall limb
silently not running), R10-012 MOD-13 limb (pilot artefact form),
R10-014 MOD-13 limb (amended Form 22 fields and the unranked form),
R10-015 (entry identifier fields beyond Form 22), R10-016 MOD-13
limb (result names its claim), R10-017 (empty log and entry runs
absent from the log), R10-018 (failed runs named in the result),
R10-025 (scoring and rerun validation through a handed get), and
R10-052 (extend_history sharing lost across separate freezes).

Records pin: R10-019 supplies the missing pin for the R9-037
shortfall limb as built, in the form the Purple 4 finding charges.
That pin stands both ways by design, because the limb as built
works and only its pin evidence was missing.

Control pins stand both ways. Values are simulated and test
values only.
"""
import unittest

from crucible import mod13


def registry_entry(**overrides):
    entry = {
        "claim_identifier": "claim-1",
        "sweep_family_identifier": "fam-1",
        "screening_run_identifiers": ["run-1", "run-2"],
        "held_out_confirmation_run_identifiers": ["run-3"],
    }
    entry.update(overrides)
    return entry


def run_record(run_id, run_class="screening", status="completed",
               family="fam-1", claim=None):
    record = {
        "run_identifier": run_id,
        "sweep_family_identifier": family,
        "run_class": run_class,
        "run_status": status,
    }
    if claim is not None:
        record["claim_identifier"] = claim
    return record


MATCHING_LOG = [
    run_record("run-1", "screening", "completed"),
    run_record("run-2", "screening", "failed"),
    run_record("run-3", "confirmation", "completed"),
]


def pilot_artefact(run_id="pilot-1"):
    return {
        "run_identifier": run_id,
        "sweep_family_identifier": "fam-1",
        "run_class": "screening",
        "form": "pilot artefact, stored apart from sweep results",
        "confinement_label": "pilot confined",
    }


class ReportedDict(dict):
    """A dict subclass whose get reading reports contents it does
    not store: the stored contents stand in the base storage and
    the reported contents stand apart."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class TestR10009RetainedCountBearingOnly(unittest.TestCase):

    def test_other_family_and_other_claim_records_do_not_fill(self):
        log = MATCHING_LOG + [
            run_record("run-x", "screening", "completed", family="fam-2"),
            run_record("run-y", "screening", "completed", claim="claim-9"),
        ]
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=5), log)
        self.assertTrue(result["performed"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 3)
        self.assertEqual(result["shortfall"], 2)
        self.assertEqual(result["shortfall_name"], "EXPECTED-RUN-SHORTFALL")

    def test_bearing_count_alone_meets_the_count(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=3), MATCHING_LOG)
        self.assertTrue(result["passed"])
        self.assertEqual(result["retained_run_count"], 3)


class TestR10010ManifestDerivedExpectedCount(unittest.TestCase):

    def test_manifest_argument_plan_expected_count_form(self):
        manifest = {"replicate_plan": {"expected_run_count": 5}}
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG, family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)
        self.assertEqual(result["retained_run_count"], 3)
        self.assertEqual(result["shortfall"], 2)
        self.assertEqual(result["shortfall_name"], "EXPECTED-RUN-SHORTFALL")

    def test_manifest_on_entry_replicates_per_grid_point(self):
        entry = registry_entry(
            family_manifest={"replicate_plan": {
                "grid_points": ["p1", "p2"],
                "replicates_per_grid_point": 3,
            }})
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 6)
        self.assertEqual(result["shortfall"], 3)

    def test_manifest_replicate_counts_list_form(self):
        manifest = {"replicate_plan": {"replicate_counts": [2, 2, 1]}}
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG, family_manifest=manifest)
        self.assertEqual(result["expected_run_count"], 5)
        self.assertFalse(result["passed"])

    def test_manifest_takes_precedence_over_ad_hoc_field(self):
        manifest = {"replicate_plan": {"expected_run_count": 5}}
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=3), MATCHING_LOG,
            family_manifest=manifest)
        self.assertEqual(result["expected_run_count"], 5)
        self.assertFalse(result["passed"])


class TestR10011ShortfallLimbNotSilent(unittest.TestCase):

    def test_no_expected_source_states_limb_not_run(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG)
        self.assertTrue(result["passed"])
        self.assertFalse(result["shortfall_limb_performed"])
        self.assertIn("not run", result["shortfall_status"])

    def test_stated_expected_source_states_limb_run(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=3), MATCHING_LOG)
        self.assertTrue(result["shortfall_limb_performed"])
        self.assertEqual(result["expected_run_count"], 3)
        self.assertEqual(result["retained_run_count"], 3)


class TestR10012PilotArtefactForm(unittest.TestCase):

    def test_pilot_artefact_unlisted_stands_outside_the_log(self):
        log = MATCHING_LOG + [pilot_artefact()]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertTrue(result["passed"])
        self.assertIn("pilot-1", result["excluded_pilot_run_identifiers"])
        self.assertNotIn("pilot-1", result["bearing_run_identifiers"])
        self.assertEqual(result["missing_run_identifiers"], [])

    def test_pilot_artefact_listed_does_not_fill_the_count(self):
        entry = registry_entry(
            screening_run_identifiers=["run-1", "run-2", "pilot-1"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        log = MATCHING_LOG[:2] + [pilot_artefact()]
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)
        self.assertIn("pilot-1", result["excluded_pilot_run_identifiers"])
        self.assertNotIn("pilot-1", result["bearing_run_identifiers"])


class TestR10014AmendedForm22Mod13Limb(unittest.TestCase):

    def test_confirmation_failed_and_gate_failure_both_gates_fails(self):
        entry = registry_entry(
            confirmation_outcome="failed", gate_failure="both gates",
            outcome="reported")
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])

    def test_single_gate_failure_fails(self):
        entry = registry_entry(
            confirmation_outcome="passed", gate_failure="procedure gate",
            outcome="reported")
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])

    def test_unranked_entry_with_rank_and_threshold_fails(self):
        entry = registry_entry(
            test_value="not ranked", rank=1, threshold=0.05,
            outcome="reported")
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])

    def test_control_passed_confirmation_and_no_gate_failure_passes(self):
        entry = registry_entry(
            confirmation_outcome="passed", gate_failure="none",
            outcome="reported")
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertTrue(result["passed"])

    def test_control_unranked_stated_form_passes(self):
        entry = registry_entry(
            test_value="not ranked", rank="not ranked",
            threshold="not ranked", outcome="not reported")
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertTrue(result["passed"])


class TestR10015EntryIdentifierFields(unittest.TestCase):

    def test_run_listed_only_under_generic_field_does_not_appear(self):
        entry = registry_entry(
            screening_run_identifiers=["run-1"],
            held_out_confirmation_run_identifiers=["run-3"],
            run_identifiers=["run-2"])
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])
        self.assertIn("run-2", result["missing_run_identifiers"])
        self.assertNotIn("run-2", result["entry_run_identifiers"])

    def test_run_listed_only_under_confirmation_alias_does_not_appear(self):
        entry = registry_entry(
            screening_run_identifiers=["run-1", "run-2"],
            held_out_confirmation_run_identifiers=[],
            confirmation_run_identifiers=["run-3"])
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])
        self.assertIn("run-3", result["missing_run_identifiers"])


class TestR10016ResultNamesItsClaim(unittest.TestCase):

    def test_passing_result_names_the_claim(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG)
        self.assertEqual(result["claim_identifier"], "claim-1")

    def test_failing_result_names_the_claim(self):
        log = MATCHING_LOG + [run_record("run-9", "headline", "failed")]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["claim_identifier"], "claim-1")

    def test_no_log_result_names_the_claim(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), None)
        self.assertFalse(result["performed"])
        self.assertEqual(result["claim_identifier"], "claim-1")


class TestR10017EntryRunsAbsentFromLog(unittest.TestCase):

    def test_empty_log_with_stated_runs_does_not_pass(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), [])
        self.assertTrue(result["performed"])
        self.assertFalse(result["passed"])
        self.assertEqual(
            sorted(result["absent_from_log_run_identifiers"]),
            ["run-1", "run-2", "run-3"])

    def test_entry_run_nowhere_in_log_does_not_pass(self):
        entry = registry_entry(
            screening_run_identifiers=["run-1", "run-2", "run-99"],
            held_out_confirmation_run_identifiers=["run-3"])
        result = mod13.compare_registry_against_run_log(entry, MATCHING_LOG)
        self.assertFalse(result["passed"])
        self.assertIn("run-99", result["absent_from_log_run_identifiers"])

    def test_control_legacy_form_with_no_stated_runs_still_passes(self):
        entry = {"phase_judgements": {"before_runs": "judged",
                                       "after_runs": "judged"}}
        result = mod13.compare_registry_against_run_log(
            entry, {"runs": ["retirement run 1"]})
        self.assertTrue(result["performed"])
        self.assertTrue(result["passed"])


class TestR10018FailedRunsNamed(unittest.TestCase):

    def test_failed_bearing_run_named_in_result(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG)
        self.assertTrue(result["passed"])
        self.assertEqual(result["failed_run_identifiers"], ["run-2"])

    def test_no_failed_runs_states_empty_failed_list(self):
        log = [run_record("run-1"), run_record("run-2"),
               run_record("run-3", "confirmation")]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertTrue(result["passed"])
        self.assertEqual(result["failed_run_identifiers"], [])


class TestR10025HandedGetValidation(unittest.TestCase):

    def test_scoring_record_validates_on_stored_not_reported(self):
        stored = {
            "inside_run_boundary": True,
            "value_returned_into_run": "back into the run",
            "profile_bound_label": "a wrong label",
            "separations": {},
        }
        reported = {
            "inside_run_boundary": False,
            "value_returned_into_run": None,
            "profile_bound_label": mod13.PROFILE_BOUND_LABEL,
            "separations": {name: True for name in mod13.SCORING_SEPARATIONS},
        }
        record = ReportedDict(stored, reported)
        self.assertFalse(mod13.validate_scoring_record(record))

    def test_scoring_record_stored_good_reported_bad_validates(self):
        stored = {
            "inside_run_boundary": False,
            "value_returned_into_run": None,
            "profile_bound_label": mod13.PROFILE_BOUND_LABEL,
            "separations": {name: True for name in mod13.SCORING_SEPARATIONS},
        }
        reported = {
            "inside_run_boundary": True,
            "value_returned_into_run": "back into the run",
            "profile_bound_label": "a wrong label",
            "separations": {},
        }
        record = ReportedDict(stored, reported)
        self.assertTrue(mod13.validate_scoring_record(record))

    def test_rerun_reading_validates_on_stored_not_reported(self):
        stored = {
            "read_as": "corrected version of the original",
            "overwrites_original": True,
        }
        reported = {
            "read_as": "difference between two rule sets only",
            "overwrites_original": False,
        }
        reading = ReportedDict(stored, reported)
        self.assertFalse(mod13.validate_rerun_reading(reading))

    def test_rerun_reading_stored_good_reported_bad_validates(self):
        stored = {
            "read_as": "difference between two rule sets only",
            "overwrites_original": False,
        }
        reported = {
            "read_as": "corrected version of the original",
            "overwrites_original": True,
        }
        reading = ReportedDict(stored, reported)
        self.assertTrue(mod13.validate_rerun_reading(reading))


class TestR10052ExtendHistorySharedMemo(unittest.TestCase):

    def test_part_shared_across_history_items_stays_one_copy(self):
        shared = [1, 2]
        history = [
            {"rule_set_version": "v1", "run_id": "r1", "held": shared},
            {"rule_set_version": "v1", "run_id": "r2", "held": shared},
        ]
        result = mod13.extend_history(history, {"note": "next"})
        self.assertIs(result[0]["held"], result[1]["held"])
        self.assertEqual(result[0]["held"], [1, 2])

    def test_part_shared_with_appended_segment_stays_one_copy(self):
        shared = [1, 2]
        history = [{"rule_set_version": "v1", "run_id": "r1", "held": shared}]
        segment = {"rule_set_version": "v1", "held": shared}
        result = mod13.extend_history(history, segment)
        self.assertIs(result[0]["held"], result[1]["held"])

    def test_control_plain_extension_stands(self):
        result = mod13.extend_history(
            [{"rule_set_version": "v1", "run_id": "r1"}], {"note": "next"})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["segment_order"], 2)
        self.assertEqual(result[1]["linked_run"], "r1")


class TestR10019RecordsPinForR9037ShortfallLimb(unittest.TestCase):
    """Records pin, row R10-019: the R9-037 expected run count
    shortfall limb as stated in the Builder 9 paper and as built
    in the code, supplied here because it stood in no pin."""

    def test_shortfall_limb_states_counts_under_its_name(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=99), MATCHING_LOG)
        self.assertTrue(result["performed"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["shortfall_name"], "EXPECTED-RUN-SHORTFALL")
        self.assertEqual(result["expected_run_count"], 99)
        self.assertEqual(result["retained_run_count"], 3)
        self.assertEqual(result["shortfall"], 96)

    def test_shortfall_limb_count_met_passes_with_counts_stated(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(expected_run_count=3), MATCHING_LOG)
        self.assertTrue(result["passed"])
        self.assertEqual(result["expected_run_count"], 3)
        self.assertEqual(result["retained_run_count"], 3)


class TestControlsStandingBothWays(unittest.TestCase):

    def test_control_matching_log_passes(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), MATCHING_LOG)
        self.assertTrue(result["performed"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_run_identifiers"], [])

    def test_control_pilot_by_run_class_stands_outside(self):
        log = MATCHING_LOG + [run_record("pilot-1", "pilot", "completed")]
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertTrue(result["passed"])
        self.assertIn("pilot-1", result["excluded_pilot_run_identifiers"])

    def test_control_no_run_log_states_no_performed_comparison(self):
        result = mod13.compare_registry_against_run_log(
            registry_entry(), None)
        self.assertFalse(result["performed"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()

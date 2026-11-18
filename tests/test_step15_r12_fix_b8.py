"""Step 15 rerun fix wave 11 pins, Builder 8, registry complex.

Rows pinned: R11-091 to R11-106 across crucible/mod13.py,
crucible/mod11.py, and the form 22 limb of crucible/mod01.py.
The standing construction is a complete twelve field entry for
claim claim-1 of family fam-1 against its matching three record
log, in which run-2 stands failed. Values are simulated and
test values only.
"""
# Step 16 fix merge: pin dispositions for this file stand in design/steps/step-16-fix-merge.md.
import unittest

from crucible import mod01, mod11, mod13


def full_entry(**overrides):
    entry = mod01.minimal_valid_instance("22")
    entry.update({
        "claim_identifier": "claim-1",
        "sweep_family_identifier": "fam-1",
        "test_value": "0.01",
        "rank": 1,
        "threshold": 0.05,
        "outcome": "reported",
        "confirmation_outcome": "passed",
        "gate_failure": "none",
        "screening_run_identifiers": ["run-1", "run-2"],
        "held_out_confirmation_run_identifiers": ["run-3"],
        "phase_judgements": {
            "before_runs": "judged",
            "after_runs": "judged",
        },
    })
    entry.update(overrides)
    return entry


def run_record(run_id, run_class="screening", status="completed",
               family="fam-1", claim="claim-1"):
    return {
        "run_identifier": run_id,
        "sweep_family_identifier": family,
        "claim_identifier": claim,
        "run_class": run_class,
        "run_status": status,
    }


def matching_log():
    return [
        run_record("run-1", "screening", "completed"),
        run_record("run-2", "screening", "failed"),
        run_record("run-3", "confirmation", "completed"),
    ]


def gate_valid(entry, log=None):
    return mod11.validate_registry_entry(
        entry, compiler="registrar", checker="checker",
        run_log=matching_log() if log is None else log)


class LyingEqStr(str):
    """A text value storing one text while its equality reading
    answers as handed, never as stored."""

    def __new__(cls, stored, answer):
        value = str.__new__(cls, stored)
        value._answer = answer
        return value

    def __eq__(self, other):
        return self._answer

    def __ne__(self, other):
        return not self._answer

    __hash__ = str.__hash__


class TestR11091DualFieldBearing(unittest.TestCase):

    def test_dual_family_record_does_not_bear(self):
        dual = run_record("run-x")
        dual["family_identifier"] = "fam-OTHER"
        log = matching_log()[:2] + [dual]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-x"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)
        self.assertNotIn("run-x", result["bearing_run_identifiers"])

    def test_dual_claim_record_does_not_bear(self):
        dual = run_record("run-y")
        dual["claim_id"] = "claim-9"
        log = matching_log()[:2] + [dual]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-y"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)

    def test_plain_other_family_control_does_not_bear(self):
        log = matching_log()[:2] + [
            run_record("run-x", family="fam-OTHER")]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-x"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)


class TestR11092PilotDress(unittest.TestCase):

    def pilot_log(self, marker_field, marker_value):
        pilot = {
            "run_identifier": "pilot-1",
            "sweep_family_identifier": "fam-1",
            "claim_identifier": "claim-1",
            "run_class": "screening",
            marker_field: marker_value,
        }
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "pilot-1"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        log = matching_log()[:2] + [pilot]
        return mod13.compare_registry_against_run_log(entry, log)

    def assert_excluded(self, field, value):
        result = self.pilot_log(field, value)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)
        self.assertIn("pilot-1", result["excluded_pilot_run_identifiers"])

    def test_form_bytes_dress(self):
        self.assert_excluded("form", b"pilot artefact")

    def test_run_class_bytes_dress(self):
        self.assert_excluded("run_class", b"pilot")

    def test_form_single_part_container_dress(self):
        self.assert_excluded("form", ["pilot artefact"])

    def test_confinement_label_bytes_dress(self):
        self.assert_excluded("confinement_label", b"pilot confined")

    def test_confinement_label_container_dress(self):
        self.assert_excluded("confinement_label", ["pilot confined"])

    def test_form_bytearray_dress(self):
        self.assert_excluded("form", bytearray(b"pilot artefact"))

    def test_form_memoryview_dress(self):
        self.assert_excluded("form", memoryview(b"pilot artefact"))

    def test_run_class_tuple_dress(self):
        self.assert_excluded("run_class", ("pilot",))

    def test_store_kind_bytes_dress(self):
        self.assert_excluded("store_kind", b"pilot")


class TestR11093AmendedFieldDress(unittest.TestCase):

    def test_confirmation_bytes_fails_all_three_acts(self):
        entry = full_entry(confirmation_outcome=b"failed")
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertFalse(gate_valid(entry))
        self.assertFalse(mod01.validate_record("22", entry))

    def test_confirmation_container_fails(self):
        entry = full_entry(confirmation_outcome=["failed"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertFalse(gate_valid(entry))

    def test_confirmation_bytearray_fails(self):
        entry = full_entry(confirmation_outcome=bytearray(b"failed"))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))
        self.assertFalse(mod01.validate_record("22", entry))

    def test_confirmation_memoryview_fails(self):
        entry = full_entry(confirmation_outcome=memoryview(b"failed"))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))

    def test_confirmation_tuple_fails(self):
        entry = full_entry(confirmation_outcome=("failed",))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))

    def test_confirmation_set_fails(self):
        entry = full_entry(confirmation_outcome={"failed"})
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))

    def test_gate_failure_bytes_fails_all_three_acts(self):
        entry = full_entry(gate_failure=b"both gates")
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))
        self.assertFalse(mod01.validate_record("22", entry))

    def test_gate_failure_bytearray_and_tuple_fail(self):
        for dress in (bytearray(b"both gates"), ("both gates",)):
            entry = full_entry(gate_failure=dress)
            self.assertFalse(mod13.compare_registry_against_run_log(
                entry, matching_log())["passed"])
            self.assertFalse(gate_valid(entry))

    def test_test_value_bytes_partial_unranked_fails(self):
        entry = full_entry(test_value=b"not ranked")
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))
        self.assertFalse(mod01.validate_record("22", entry))

    def test_test_value_bytearray_and_tuple_fail(self):
        for dress in (bytearray(b"not ranked"), ("not ranked",)):
            entry = full_entry(test_value=dress)
            self.assertFalse(mod13.compare_registry_against_run_log(
                entry, matching_log())["passed"])
            self.assertFalse(gate_valid(entry))

    def test_outcome_bytes_reported_with_failed_confirmation_fails_mod01(self):
        entry = full_entry(outcome=b"reported",
                           confirmation_outcome="failed")
        self.assertFalse(mod01.validate_record("22", entry))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))


class TestR11094ManifestFigureForms(unittest.TestCase):

    def test_plan_expected_count_digit_text(self):
        manifest = {"replicate_plan": {"expected_run_count": "5"}}
        result = mod13.compare_registry_against_run_log(
            full_entry(), matching_log(), family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)
        self.assertEqual(result["shortfall"], 2)
        self.assertTrue(result["shortfall_limb_performed"])

    def test_entry_grid_point_count_fallback(self):
        manifest = {"replicate_plan": {"replicates_per_grid_point": 3}}
        entry = full_entry(grid_point_count=2)
        del entry["grid_points"]
        result = mod13.compare_registry_against_run_log(
            entry, matching_log(), family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 6)

    def test_grid_points_mapping_derives_count(self):
        manifest = {"replicate_plan": {
            "replicates_per_grid_point": 3,
            "grid_points": {"p1": 1, "p2": 2}}}
        result = mod13.compare_registry_against_run_log(
            full_entry(), matching_log(), family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 6)


class TestR11095BareBytesHeldOut(unittest.TestCase):

    def test_bare_bytes_held_out_named_absent(self):
        entry = full_entry(
            held_out_confirmation_run_identifiers=b"run-99")
        result = mod13.compare_registry_against_run_log(
            entry, matching_log()[:2])
        self.assertFalse(result["passed"])
        self.assertIn("run-99", result["absent_from_log_run_identifiers"])
        self.assertIn("run-99", result["entry_run_identifiers"])

    def test_bare_bytearray_held_out_named_absent(self):
        entry = full_entry(
            held_out_confirmation_run_identifiers=bytearray(b"run-99"))
        result = mod13.compare_registry_against_run_log(
            entry, matching_log()[:2])
        self.assertFalse(result["passed"])
        self.assertIn("run-99", result["absent_from_log_run_identifiers"])

    def test_bare_memoryview_held_out_named_absent(self):
        entry = full_entry(
            held_out_confirmation_run_identifiers=memoryview(b"run-99"))
        result = mod13.compare_registry_against_run_log(
            entry, matching_log()[:2])
        self.assertFalse(result["passed"])
        self.assertIn("run-99", result["absent_from_log_run_identifiers"])


class TestR11096BytesKeyClaimNaming(unittest.TestCase):

    def test_bytes_key_claim_named_at_comparison_and_gate(self):
        entry = full_entry()
        value = entry.pop("claim_identifier")
        entry[b"claim_identifier"] = value
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])
        self.assertEqual(result["claim_identifier"], "claim-1")
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=matching_log())
        self.assertEqual(judged["claim_identifier"], "claim-1")
        self.assertNotIn("claim_identifier",
                         judged["missing_registry_fields"])


class TestR11097FailedRunNaming(unittest.TestCase):

    def failed_for(self, **status_fields):
        record = run_record("run-2", "screening", "completed")
        record.pop("run_status")
        record.update(status_fields)
        log = [run_record("run-1"), record,
               run_record("run-3", "confirmation")]
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        return result["failed_run_identifiers"]

    def test_second_status_field_failed_names_run(self):
        self.assertEqual(
            self.failed_for(status="completed", run_status="failed"),
            ["run-2"])

    def test_status_bytes_dress_names_run(self):
        self.assertEqual(self.failed_for(status=b"failed"), ["run-2"])

    def test_status_container_dress_names_run(self):
        self.assertEqual(self.failed_for(status=["failed"]), ["run-2"])

    def test_status_bytearray_dress_names_run(self):
        self.assertEqual(
            self.failed_for(status=bytearray(b"failed")), ["run-2"])

    def test_status_memoryview_dress_names_run(self):
        self.assertEqual(
            self.failed_for(status=memoryview(b"failed")), ["run-2"])

    def test_status_tuple_dress_names_run(self):
        self.assertEqual(self.failed_for(status=("failed",)), ["run-2"])

    def test_status_set_dress_names_run(self):
        self.assertEqual(self.failed_for(status={"failed"}), ["run-2"])


class TestR11098OutcomeReadInOneForm(unittest.TestCase):

    def test_reported_not_run_fails_all_three_acts(self):
        entry = full_entry(outcome="reported",
                           confirmation_outcome="not run",
                           gate_failure="none")
        self.assertFalse(mod01.validate_record("22", entry))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))

    def test_not_reported_failed_passes_all_three_acts(self):
        entry = full_entry(outcome="not reported",
                           confirmation_outcome="failed",
                           gate_failure="both gates")
        entry_for_validation = {
            key: value for key, value in entry.items()
            if key in mod01.form_fields("22")}
        self.assertTrue(mod01.validate_record("22", entry_for_validation))
        self.assertTrue(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertTrue(gate_valid(entry))

    def test_not_reported_single_gate_failure_passes_all_three(self):
        entry = full_entry(outcome="not reported",
                           confirmation_outcome="passed",
                           gate_failure="procedure gate")
        entry_for_validation = {
            key: value for key, value in entry.items()
            if key in mod01.form_fields("22")}
        self.assertTrue(mod01.validate_record("22", entry_for_validation))
        self.assertTrue(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertTrue(gate_valid(entry))


class TestR11099StatedValueSets(unittest.TestCase):

    def assert_all_fail(self, **overrides):
        entry = full_entry(**overrides)
        self.assertFalse(mod01.validate_record("22", entry))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))

    def test_bogus_outcome_alone_fails(self):
        self.assert_all_fail(outcome="bogus outcome")

    def test_bogus_confirmation_outcome_alone_fails(self):
        self.assert_all_fail(confirmation_outcome="bogus outcome")

    def test_bogus_gate_failure_alone_fails(self):
        self.assert_all_fail(gate_failure="bogus failure")

    def test_bogus_values_in_all_three_fail(self):
        self.assert_all_fail(outcome="bogus outcome",
                             confirmation_outcome="bogus outcome",
                             gate_failure="bogus failure")


class TestR11100KeyDressBearing(unittest.TestCase):

    def test_record_other_family_under_bytes_key_does_not_bear(self):
        other = run_record("run-x")
        value = other.pop("sweep_family_identifier")
        other[b"family_identifier"] = "fam-OTHER"
        other["family"] = value
        log = matching_log()[:2] + [other]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-x"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)

    def test_record_other_family_under_tuple_key_does_not_bear(self):
        other = {
            "run_identifier": "run-x",
            ("family_identifier",): "fam-OTHER",
            "claim_identifier": "claim-1",
            "run_class": "screening",
            "run_status": "completed",
        }
        log = matching_log()[:2] + [other]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-x"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)

    def test_record_other_claim_under_bytes_key_does_not_bear(self):
        other = run_record("run-x")
        other.pop("claim_identifier")
        other[b"claim_identifier"] = "claim-9"
        log = matching_log()[:2] + [other]
        entry = full_entry(
            screening_run_identifiers=["run-1", "run-2", "run-x"],
            held_out_confirmation_run_identifiers=[],
            expected_run_count=3)
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["retained_run_count"], 2)

    def test_entry_family_under_bytes_key_only_is_read(self):
        entry = full_entry()
        entry.pop("sweep_family_identifier")
        entry[b"family_identifier"] = "fam-1"
        log = matching_log()[:2] + [run_record("run-3", family="fam-OTHER")]
        entry["screening_run_identifiers"] = ["run-1", "run-2", "run-3"]
        entry["held_out_confirmation_run_identifiers"] = []
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertFalse(result["passed"])
        self.assertNotIn("run-3", result["bearing_run_identifiers"])


class TestR11101GateHandedEquality(unittest.TestCase):

    def test_phase_values_with_lying_equality_do_not_judge(self):
        entry = full_entry(phase_judgements={
            "before_runs": LyingEqStr("pending", True),
            "after_runs": LyingEqStr("pending", True),
        })
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=matching_log())
        self.assertFalse(judged["valid"])
        self.assertFalse(judged["phases_judged"]["before_runs"])
        self.assertFalse(judged["phases_judged"]["after_runs"])

    def test_same_person_with_lying_equality_is_barred(self):
        compiler = LyingEqStr("MOD-X", False)
        judged = mod11.judge_registry_entry(
            full_entry(), compiler=compiler, checker="MOD-X",
            run_log=matching_log())
        self.assertFalse(judged["valid"])
        self.assertFalse(judged["checker_did_not_compile"])

    def test_distinct_person_control_passes(self):
        self.assertTrue(gate_valid(full_entry()))


class TestR11102ValueDressBearing(unittest.TestCase):

    def assert_bears(self, dress):
        log = matching_log()[:2] + [run_record("run-3", "confirmation")]
        log[2]["sweep_family_identifier"] = dress
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])
        self.assertIn("run-3", result["bearing_run_identifiers"])
        self.assertEqual(result["absent_from_log_run_identifiers"], [])

    def test_family_bytes_dress(self):
        self.assert_bears(b"fam-1")

    def test_family_bytearray_dress(self):
        self.assert_bears(bytearray(b"fam-1"))

    def test_family_memoryview_dress(self):
        self.assert_bears(memoryview(b"fam-1"))

    def test_family_list_dress(self):
        self.assert_bears(["fam-1"])

    def test_family_tuple_dress(self):
        self.assert_bears(("fam-1",))

    def test_family_set_dress(self):
        self.assert_bears({"fam-1"})

    def test_claim_bytes_dress(self):
        log = matching_log()[:2] + [run_record("run-3", "confirmation")]
        log[2]["claim_identifier"] = b"claim-1"
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])

    def test_entry_family_bytes_dress(self):
        entry = full_entry(sweep_family_identifier=b"fam-1")
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["bearing_run_identifiers"]), 3)

    def test_entry_claim_bytes_dress(self):
        entry = full_entry(claim_identifier=b"claim-1")
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])


class TestR11103RunIdentifierDressMatching(unittest.TestCase):

    def test_entry_element_bytes_dress_matches(self):
        entry = full_entry(
            screening_run_identifiers=[b"run-1", "run-2"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_run_identifiers"], [])
        self.assertEqual(result["absent_from_log_run_identifiers"], [])

    def test_entry_element_bytearray_dress_matches(self):
        entry = full_entry(
            screening_run_identifiers=[bytearray(b"run-1"), "run-2"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])

    def test_entry_element_list_dress_matches(self):
        entry = full_entry(screening_run_identifiers=[["run-1"], "run-2"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])

    def test_entry_element_tuple_dress_matches(self):
        entry = full_entry(screening_run_identifiers=[("run-1",), "run-2"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])

    def test_record_identifier_bytes_dress_matches(self):
        log = matching_log()
        log[2]["run_identifier"] = b"run-3"
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])
        self.assertEqual(result["missing_run_identifiers"], [])
        self.assertEqual(result["absent_from_log_run_identifiers"], [])

    def test_record_identifier_bytearray_dress_matches(self):
        log = matching_log()
        log[2]["run_identifier"] = bytearray(b"run-3")
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])

    def test_record_identifier_list_dress_matches(self):
        log = matching_log()
        log[2]["run_identifier"] = ["run-3"]
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])


class TestR11104FurtherFigureForms(unittest.TestCase):

    def test_entry_expected_count_digit_text(self):
        entry = full_entry(expected_run_count="5")
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)
        self.assertTrue(result["shortfall_limb_performed"])

    def test_run_log_mapping_expected_count_digit_text(self):
        log = {"runs": matching_log(), "expected_run_count": "5"}
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)

    def test_replicate_counts_digit_text(self):
        manifest = {"replicate_plan": {"replicate_counts": ["3", "3"]}}
        result = mod13.compare_registry_against_run_log(
            full_entry(), matching_log(), family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 6)

    def test_replicates_per_grid_point_digit_text(self):
        manifest = {"replicate_plan": {
            "replicates_per_grid_point": "3", "grid_point_count": 2}}
        result = mod13.compare_registry_against_run_log(
            full_entry(), matching_log(), family_manifest=manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 6)

    def test_manifest_under_bytes_key(self):
        entry = full_entry()
        entry[b"family_manifest"] = {
            "replicate_plan": {"expected_run_count": 5}}
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)

    def test_manifest_under_tuple_key(self):
        entry = full_entry()
        entry[("family_manifest",)] = {
            "replicate_plan": {"expected_run_count": 5}}
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)

    def test_replicate_plan_under_tuple_key(self):
        entry = full_entry()
        entry["family_manifest"] = {
            ("replicate_plan",): {"expected_run_count": 5}}
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_run_count"], 5)


class TestR11105ContainerAndMemoryviewKeys(unittest.TestCase):

    def assert_claim_key_read(self, key):
        entry = full_entry()
        value = entry.pop("claim_identifier")
        entry[key] = value
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])
        self.assertEqual(result["claim_identifier"], "claim-1")
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=matching_log())
        self.assertTrue(judged["valid"])
        self.assertEqual(judged["claim_identifier"], "claim-1")
        self.assertFalse(mod01.validate_record("22", entry))

    def test_claim_under_tuple_key(self):
        self.assert_claim_key_read(("claim_identifier",))

    def test_claim_under_frozenset_key(self):
        self.assert_claim_key_read(frozenset({"claim_identifier"}))

    def test_claim_under_memoryview_key(self):
        self.assert_claim_key_read(memoryview(b"claim_identifier"))


class TestR11106RunLogReadingForms(unittest.TestCase):

    def test_single_record_under_run_id_alias_alone(self):
        record = {
            "run_id": "run-1",
            "sweep_family_identifier": "fam-1",
            "claim_identifier": "claim-1",
            "run_status": "completed",
        }
        entry = full_entry(
            screening_run_identifiers=["run-1"],
            held_out_confirmation_run_identifiers=[])
        result = mod13.compare_registry_against_run_log(entry, record)
        self.assertTrue(result["passed"])
        self.assertIn("run-1", result["bearing_run_identifiers"])

    def test_records_mapping_under_bytes_key(self):
        log = {b"runs": matching_log()}
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["bearing_run_identifiers"]), 3)

    def test_records_mapping_under_tuple_key(self):
        log = {("runs",): matching_log()}
        result = mod13.compare_registry_against_run_log(
            full_entry(), log)
        self.assertTrue(result["passed"])


class TestControlsStandingBothWays(unittest.TestCase):

    def test_matching_entry_passes_all_three_acts(self):
        entry = full_entry()
        entry_for_validation = {
            key: value for key, value in entry.items()
            if key in mod01.form_fields("22")}
        self.assertTrue(mod01.validate_record("22", entry_for_validation))
        self.assertTrue(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertTrue(gate_valid(entry))

    def test_plain_failed_confirmation_reported_fails_all_three(self):
        entry = full_entry(confirmation_outcome="failed")
        self.assertFalse(mod01.validate_record("22", entry))
        self.assertFalse(mod13.compare_registry_against_run_log(
            entry, matching_log())["passed"])
        self.assertFalse(gate_valid(entry))


if __name__ == "__main__":
    unittest.main()

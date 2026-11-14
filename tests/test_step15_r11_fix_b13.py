"""Fix wave 10 pins, Builder 13 (top up): rows R10-034 at
crucible/mod01.py, and the crucible/mod11.py limbs of rows
R10-013, R10-014, and R10-016, read against section 2 of the
Round 10 register, in particular limb 7, that every act that
decides presence or completeness reads its inputs through base
readings only, never through a hash or equality reading a handed
key supplies.

Row R10-034: the MOD-01 validation act returns the eventlog
validation for form 36 before the cured stored pairs presence
scan, and the eventlog act judges base field presence by dict
contains and dict getitem on the handed instance, so a form 36
record missing a required base field validates where the missing
field is supplied by a key whose hash and equality readings lie.

Row R10-013: judge_registry_entry and validate_registry_entry
read only the phase_judgements values and the comparison result
and never read any Form 22 field of the entry, so an entry
carrying no registry content validates as reportable.

Row R10-014: the gate acts must read the amended Form 22 fields,
confirmation_outcome and gate_failure, now in the MOD-01 field
list, and the unranked form: an entry whose confirmation outcome
stands failed, or whose gate failure stands at a gate, must not
validate, and an entry carrying not ranked in only part of its
test value, rank, and threshold fields must not validate, while
the stated not ranked form, with all three fields carrying not
ranked, stands.

Row R10-016: no return form of judge_registry_entry carries
claim_identifier or any claim naming field, so a gate result
cannot be tied to its claim from the result itself.

Values are simulated and test values only.
"""
import unittest

from crucible import mod01, mod11


class LyingKeyStr(str):
    """A text key storing one name while its hash names another
    field and its equality reading answers True to any reading.
    The stored characters are the name it stores; its hash and
    equality are readings it supplies and no presence act may
    run through them."""

    def __new__(cls, stored, hash_name):
        value = str.__new__(cls, stored)
        value._hash_name = hash_name
        return value

    def __hash__(self):
        return str.__hash__(self._hash_name)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def eventlog_with_lying_supply(missing_field, entry_kind="ordinary"):
    """A form 36 instance missing a required field in its stored
    text, where a key storing an unrelated name supplies that
    field through its hash and equality readings only."""
    instance = mod01.minimal_valid_instance("36", entry_kind=entry_kind)
    stored_value = instance.pop(missing_field)
    instance[LyingKeyStr("an unrelated stored name", missing_field)] = (
        stored_value)
    return instance


def full_entry(**overrides):
    """A registry entry carrying every Form 22 field, the two
    amended fields included, both phase judgements, and the run
    identifiers of the matching log."""
    entry = mod01.minimal_valid_instance("22")
    entry.update({
        "claim_identifier": "claim-1",
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


def run_record(run_id, run_class="screening", status="completed"):
    return {
        "run_identifier": run_id,
        "run_class": run_class,
        "run_status": status,
    }


MATCHING_LOG = [
    run_record("run-1", "screening", "completed"),
    run_record("run-2", "screening", "failed"),
    run_record("run-3", "confirmation", "completed"),
]

LEGACY_LOG = {"runs": ["retirement run 1"]}


class TestR10034EventlogStoredPairsPresence(unittest.TestCase):

    def test_base_field_supplied_by_lying_key_fails(self):
        record = eventlog_with_lying_supply("run_identifier")
        self.assertFalse(mod01.validate_record("36", record))

    def test_second_base_field_supplied_by_lying_key_fails(self):
        record = eventlog_with_lying_supply("simulated_day")
        self.assertFalse(mod01.validate_record("36", record))

    def test_eventlog_act_alone_rejects_lying_supply(self):
        record = eventlog_with_lying_supply("event_identifier")
        self.assertFalse(mod01._validate_eventlog(record))

    def test_base_field_under_true_text_with_lying_hash_passes(self):
        instance = mod01.minimal_valid_instance("36")
        stored_value = instance.pop("run_identifier")
        instance[LyingKeyStr("run_identifier", "an unrelated name")] = (
            stored_value)
        self.assertTrue(mod01.validate_record("36", instance))

    def test_supersession_field_supplied_by_lying_key_fails(self):
        record = eventlog_with_lying_supply(
            "resume_attempt_identifier", entry_kind="supersession")
        self.assertFalse(mod01.validate_record("36", record))

    def test_agent_field_supplied_by_lying_key_fails(self):
        record = eventlog_with_lying_supply(
            "agent_identifier", entry_kind="agent")
        self.assertFalse(mod01.validate_record("36", record))

    def test_forbidden_field_hidden_by_lying_hash_fails(self):
        instance = mod01.minimal_valid_instance("36")
        instance[LyingKeyStr("agent_identifier", "an unrelated name")] = (
            "stated agent")
        self.assertFalse(mod01.validate_record("36", instance))

    def test_plain_eventlog_controls_stand(self):
        for kind in ("ordinary", "agent", "supersession"):
            stored = mod01.minimal_valid_instance("36", entry_kind=kind)
            self.assertTrue(mod01.validate_record("36", stored))
        missing = mod01.minimal_valid_instance("36")
        del missing["journal_position"]
        self.assertFalse(mod01.validate_record("36", missing))


class TestR10013GateReadsForm22Fields(unittest.TestCase):

    def test_entry_with_no_registry_content_fails(self):
        entry = {"phase_judgements": {"before_runs": "judged",
                                      "after_runs": "judged"}}
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log=LEGACY_LOG)
        self.assertFalse(judged["valid"])
        self.assertIn("claim_identifier",
                      judged["missing_registry_fields"])
        self.assertFalse(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log=LEGACY_LOG))

    def test_entry_missing_one_form22_field_fails(self):
        entry = full_entry()
        del entry["claim_statement"]
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=MATCHING_LOG)
        self.assertFalse(judged["valid"])
        self.assertEqual(judged["missing_registry_fields"],
                         ["claim_statement"])
        self.assertFalse(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=MATCHING_LOG))

    def test_entry_missing_claim_identifier_fails(self):
        entry = full_entry()
        del entry["claim_identifier"]
        self.assertFalse(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=MATCHING_LOG))

    def test_entry_missing_amended_field_fails(self):
        entry = full_entry()
        del entry["confirmation_outcome"]
        self.assertFalse(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=MATCHING_LOG))

    def test_full_entry_on_matching_log_passes_control(self):
        judged = mod11.judge_registry_entry(
            full_entry(), compiler="registrar", checker="checker",
            run_log=MATCHING_LOG)
        self.assertTrue(judged["compared_against_run_log"])
        self.assertEqual(judged["missing_registry_fields"], [])
        self.assertTrue(judged["valid"])
        self.assertTrue(mod11.validate_registry_entry(
            full_entry(), compiler="registrar", checker="checker",
            run_log=MATCHING_LOG))

    def test_full_entry_same_person_still_refused_control(self):
        self.assertFalse(mod11.validate_registry_entry(
            full_entry(), compiler="registrar", checker="registrar",
            run_log=MATCHING_LOG))


class TestR10014GateReadsAmendedFieldsAndUnrankedForm(unittest.TestCase):

    def gate_valid(self, **overrides):
        return mod11.validate_registry_entry(
            full_entry(**overrides), compiler="registrar",
            checker="checker", run_log=MATCHING_LOG)

    def test_failed_confirmation_and_both_gates_fail(self):
        entry = full_entry(confirmation_outcome="failed",
                           gate_failure="both gates")
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=MATCHING_LOG)
        self.assertFalse(judged["valid"])
        self.assertTrue(judged["amended_form_failures"])
        self.assertFalse(self.gate_valid(
            confirmation_outcome="failed", gate_failure="both gates"))

    def test_gate_failure_alone_fails(self):
        self.assertFalse(self.gate_valid(
            confirmation_outcome="passed",
            gate_failure="procedure gate"))

    def test_failed_confirmation_alone_fails(self):
        self.assertFalse(self.gate_valid(
            confirmation_outcome="failed", gate_failure="none"))

    def test_unranked_test_value_with_ranked_rest_fails(self):
        self.assertFalse(self.gate_valid(
            test_value="not ranked", rank=1, threshold=0.05))

    def test_unranked_rank_with_ranked_rest_fails(self):
        self.assertFalse(self.gate_valid(
            test_value="0.01", rank="not ranked",
            threshold="not ranked"))

    def test_unranked_claim_in_stated_form_passes_control(self):
        self.assertTrue(self.gate_valid(
            test_value="not ranked", rank="not ranked",
            threshold="not ranked"))

    def test_reported_passed_entry_passes_control(self):
        self.assertTrue(self.gate_valid(
            confirmation_outcome="passed", gate_failure="none",
            outcome="reported"))


class TestR10016GateResultNamesItsClaim(unittest.TestCase):

    def test_passing_gate_result_carries_claim_identifier(self):
        judged = mod11.judge_registry_entry(
            full_entry(), compiler="registrar", checker="checker",
            run_log=MATCHING_LOG)
        self.assertEqual(judged["claim_identifier"], "claim-1")

    def test_failing_gate_result_carries_claim_identifier(self):
        log = MATCHING_LOG + [run_record("run-9", "headline", "failed")]
        judged = mod11.judge_registry_entry(
            full_entry(), compiler="registrar", checker="checker",
            run_log=log)
        self.assertFalse(judged["valid"])
        self.assertEqual(judged["claim_identifier"], "claim-1")

    def test_no_run_log_gate_result_carries_claim_identifier(self):
        judged = mod11.judge_registry_entry(
            full_entry(), compiler="registrar", checker="checker")
        self.assertFalse(judged["compared_against_run_log"])
        self.assertEqual(judged["claim_identifier"], "claim-1")

    def test_entry_with_no_claim_names_none(self):
        entry = {"phase_judgements": {"before_runs": "judged",
                                      "after_runs": "judged"}}
        judged = mod11.judge_registry_entry(
            entry, compiler="registrar", checker="independent checker",
            run_log=LEGACY_LOG)
        self.assertIsNone(judged["claim_identifier"])


if __name__ == "__main__":
    unittest.main()

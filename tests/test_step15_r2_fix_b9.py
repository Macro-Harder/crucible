"""Step 15 second run fix pins, builder 9. MOD-13 and MOD-16.

Items R1-017, R1-060, R1-061, R1-092 and R1-062.
"""
import unittest

import crucible.mod01 as mod01
import crucible.mod10 as mod10
import crucible.mod11 as mod11
import crucible.mod13 as mod13
import crucible.mod16 as mod16

STATEMENT = (
    "The same program was run again on the same records and gave "
    "the result stated. No separate team rebuilt the program, and "
    "no separate team reran the work with its own tools. This "
    "check does not show that an independent team would get the "
    "same result."
)

COMPARABILITY_ITEMS = (
    "code_version",
    "rule_version_set",
    "dependency_manifest",
    "compiler_identity_and_arithmetic_flags",
    "library_versions",
    "algorithm_selection_mode",
    "processor_class",
    "worker_count_form",
    "hash_seed_setting",
)


def _facts():
    fields = list(mod01.state_hash_field_list())
    facts = {field: "value for " + field for field in fields}
    facts["headline_unit"] = {"unit": "unit-1"}
    return fields, facts


class EvilRecord(dict):
    """A record whose own get returns one constant for every key."""

    def get(self, key, default=None):
        return "evil constant"


class TestR1017ReplayBaseGet(unittest.TestCase):
    def test_replay_reads_through_base_dict_get(self):
        fields, facts = _facts()
        first = EvilRecord()
        second = EvilRecord()
        for field in fields:
            dict.__setitem__(first, field, facts[field])
            dict.__setitem__(second, field, facts[field])
        dict.__setitem__(first, "headline_unit", {"unit": "unit-1"})
        dict.__setitem__(second, "headline_unit", {"unit": "unit-1"})
        dict.__setitem__(second, fields[0], "a different stored value")
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertTrue(check["marked_non_deterministic"])
        self.assertIn(fields[0], check["differing_fields"])


class TestR1060Comparability(unittest.TestCase):
    def _pair(self, item):
        fields, facts = _facts()
        first = dict(facts)
        second = dict(facts)
        for name in COMPARABILITY_ITEMS:
            first[name] = "first value for " + name
            second[name] = "first value for " + name
        second[item] = "a differing value for " + item
        verdicts = {
            "first verdict state after resume": "verdict-a",
            "run close": "verdict-b",
        }
        first["detection_verdicts"] = dict(verdicts)
        second["detection_verdicts"] = dict(verdicts)
        return first, second

    def test_replay_not_comparable_on_each_item(self):
        for item in COMPARABILITY_ITEMS:
            first, second = self._pair(item)
            check = mod13.replay_check(first, second)
            self.assertTrue(check.get("not_comparable"), item)
            self.assertFalse(check.get("comparable"), item)
            self.assertIn(item, check.get("not_comparable_on", []), item)
            self.assertIsNot(check.get("deterministic"), True, item)
            self.assertFalse(check.get("equality_observation_reported"), item)

    def test_resume_not_comparable_on_each_item(self):
        for item in COMPARABILITY_ITEMS:
            first, second = self._pair(item)
            check = mod13.resume_check(first, second)
            self.assertTrue(check.get("not_comparable"), item)
            self.assertFalse(check.get("comparable"), item)
            self.assertIn(item, check.get("not_comparable_on", []), item)
            self.assertIsNot(check.get("equal_in_scope"), True, item)
            self.assertFalse(check.get("equality_observation_reported"), item)

    def test_agreeing_comparability_still_reports_equality(self):
        fields, facts = _facts()
        first = dict(facts)
        second = dict(facts)
        for name in COMPARABILITY_ITEMS:
            first[name] = "same value for " + name
            second[name] = "same value for " + name
        self.assertTrue(mod13.replay_check(first, second)["deterministic"])


class TestR1061ReplayDivergenceForm(unittest.TestCase):
    def test_replay_returns_first_divergence_record(self):
        fields, facts = _facts()
        first = dict(facts)
        second = dict(facts)
        second[fields[1]] = "another value"
        second["tick"] = 5
        second["simulated_day"] = 3
        second["agent_identifier"] = "agent-1"
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertEqual(check["first_divergence"], fields[1])
        record = check["divergence_record"]
        self.assertIsNotNone(record)
        self.assertEqual(record["field"], fields[1])
        self.assertEqual(record["tick"], 5)
        self.assertEqual(record["day"], 3)
        self.assertEqual(record["agent_identifier"], "agent-1")
        self.assertEqual(
            record["values_compared"],
            [facts[fields[1]], "another value"])
        self.assertFalse(record["hash_limb_ran"])
        self.assertIn("no hash", record["compared_form"])

    def test_replay_returns_no_difference_report(self):
        fields, facts = _facts()
        first = dict(facts)
        first["run_id"] = "run-a"
        second = dict(facts)
        second["run_id"] = "run-a"
        check = mod13.replay_check(first, second)
        self.assertTrue(check["deterministic"])
        self.assertIsNone(check["divergence_record"])
        self.assertIsNone(check["first_divergence"])
        report = check["no_difference_report"]
        self.assertIsNotNone(report)
        self.assertEqual(report["fields_compared"], fields)
        self.assertFalse(report["hash_limb_ran"])
        self.assertIn("run-a", report["runs_compared"])
        self.assertTrue(report["compared_form"])


class TestR1092ReplicationStatement(unittest.TestCase):
    def test_verdict_record_carries_statement_and_publication_requires_it(self):
        record = mod13.verdict_record("claim-1")
        self.assertEqual(record["replication_statement"], STATEMENT)
        self.assertTrue(mod13.validate_verdict_record(record))
        claim = {"claim_identifier": "claim-1"}
        self.assertTrue(mod13.publishable_on_replication(claim, record))
        stripped = dict(record)
        del stripped["replication_statement"]
        self.assertFalse(mod13.validate_verdict_record(stripped))
        self.assertFalse(mod13.publishable_on_replication(claim, stripped))
        altered = dict(record)
        altered["replication_statement"] = "a shorter claim"
        self.assertFalse(mod13.validate_verdict_record(altered))
        self.assertFalse(mod13.publishable_on_replication(claim, altered))


class TestR1062DrivenExercise(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_run_class_drives_a_retained_run(self):
        for run_class in ("screening", "validation"):
            result = mod16.exercise_run_class(run_class)
            self.assertTrue(result["exercised_end_to_end"], run_class)
            record = result["record"]
            self.assertEqual(record["run_class"], run_class)
            read_back = mod10.read_run_record(
                record["run_id"], store_kind="sweep")
            self.assertEqual(read_back, record)

    def test_confirmation_and_headline_drive_runs(self):
        result = mod16.exercise_confirmation_and_headline()
        confirmation = result["confirmation"]
        self.assertTrue(confirmation["exercised_end_to_end"])
        lineage = confirmation["settings_lineage_record"]
        self.assertIsInstance(lineage, dict)
        self.assertNotIsInstance(lineage, str)
        for field in (
                "confirmation_claim", "settings_trace",
                "used_to_find_or_confirm_per_setting"):
            self.assertIn(field, lineage)
        self.assertTrue(lineage.get("completed"))
        record = confirmation["record"]
        read_back = mod10.read_run_record(
            record["run_id"], store_kind="sweep")
        self.assertEqual(read_back, record)
        headline = result["headline"]
        self.assertTrue(headline["unit_built"])
        self.assertTrue(headline["exercised_end_to_end"])
        self.assertTrue(mod11.validate_headline_unit(headline["unit"]))


if __name__ == "__main__":
    unittest.main()

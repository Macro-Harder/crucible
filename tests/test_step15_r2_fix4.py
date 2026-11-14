# Step 15 Round 2 fix tests, cluster R2-4. MOD-14 and MOD-12 surfaces.
import unittest

import crucible.mod12 as mod12
import crucible.mod14 as mod14

MONEY_KEY = "real_" + "money_value"
ANCHOR_SET_KEY = "anchor_" + "set"
ANCHOR_SPACED_KEY = "anchor" + " " + "set"
ANCHOR_JOINED_KEY = "anchor" + "set"

SEALED = "sealed family record"
CLOSED = "closed run record"
CHECKPOINT = "checkpoint set"


class TestOperatorBoundaryWidened(unittest.TestCase):
    def test_destructive_and_edit_synonyms_refused_on_sealed(self):
        verbs = (
            "purge", "drop", "wipe", "clear", "truncate", "expunge",
            "amend", "patch", "redact", "replace", "void", "supersede",
            "obliterate", "annihilate", "correct",
        )
        for verb in verbs:
            action = {"kind": verb, "target": SEALED}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_inflected_and_punctuated_verbs_refused_on_sealed(self):
        for verb in ("deleted", "deleting", "edit.", "DELETE!",
                     "remove all", "erase-record"):
            action = {"kind": verb, "target": SEALED}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_targets_with_articles_and_punctuation_refused(self):
        targets = (
            "sealed family record.",
            "the sealed family record",
            "sealed family records!",
            "sealed families record",
        )
        for target in targets:
            action = {"kind": "delete", "target": target}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_typed_kind_and_target_refused(self):
        actions = (
            {"kind": ["delete"], "target": SEALED},
            {"kind": "delete", "target": [SEALED]},
            {"kind": 123, "target": SEALED},
        )
        for action in actions:
            self.assertFalse(mod14.validate_operator_action(action), action)
            verdict = mod14.validate_operator_action_with_reason(action)
            self.assertFalse(verdict["allowed"], action)
            self.assertTrue(verdict["reason"], action)

    def test_sealed_admits_no_rule_path(self):
        action = {"kind": "edit", "target": SEALED, "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action))

    def test_flag_rule_path_bars_destructive_verbs(self):
        for verb in ("destroy", "delete", "purge"):
            action = {"kind": verb, "target": CLOSED, "path": "flag rule"}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_permitted_paths_and_read_stand(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CLOSED, "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": CLOSED, "path": "flag rule"})
            is False)
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": CHECKPOINT, "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CHECKPOINT, "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": CHECKPOINT}))
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "purge", "target": SEALED})
        self.assertFalse(verdict["allowed"])
        self.assertTrue(verdict["reason"])


class TestPilotScreeningContainers(unittest.TestCase):
    def test_list_wrapped_barred_artefacts_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", [{MONEY_KEY: 500}])
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", [{ANCHOR_SET_KEY: ["a"]}])

    def test_anchor_spellings_refused_inside_dict(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"nested": {ANCHOR_SPACED_KEY: ["a"]}})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {ANCHOR_JOINED_KEY: ["a"]})

    def test_set_carried_pairs_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"pairs": {(MONEY_KEY, 500)}})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {(ANCHOR_SET_KEY, "a")})

    def test_barred_claim_inside_list_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run(
                "timing", [{"settles_population_behaviour_rate": True}])

    def test_lawful_containers_run_under_label(self):
        out = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(out["confinement_label"], "pilot confined")
        out = mod14.pilot_run("timing", [{"figure": 1}])
        self.assertEqual(out["confinement_label"], "pilot confined")
        self.assertEqual(out["figure"], [{"figure": 1}])
        out = mod14.pilot_run("timing", {"nested": [{"figure": 2}]})
        self.assertEqual(out["confinement_label"], "pilot confined")


class TestWeeklyHeadlineCountDress(unittest.TestCase):
    def test_bare_string_identifier_counts_as_one(self):
        records = [{"week": "W1", "headline_unit_identifiers": "u1u2"}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 1)
        counted = mod14.run_command(
            "weekly_headline_count",
            {"summary_records": records, "week": "W1"})
        self.assertEqual(counted["count"], 1)

    def test_none_identifier_field_fails_by_name(self):
        records = [{"week": "W1", "headline_unit_identifiers": None}]
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count(records, "W1")
        counted = mod14.run_command(
            "weekly_headline_count",
            {"summary_records": records, "week": "W1"})
        self.assertIn("failure", counted)
        self.assertNotEqual(counted.get("count"), 0)

    def test_unreadable_identifier_field_fails_by_name(self):
        records = [{"week": "W1", "headline_unit_identifiers": 123}]
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count(records, "W1")

    def test_standing_count_and_failures_stand(self):
        records = [
            {"week": "W1", "headline_unit_identifiers": ["u1", "u2"]},
            {"week": "W1", "headline_unit_identifiers": ["u1"]},
            {"week": "W2", "headline_unit_identifiers": ["u3"]},
        ]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 2)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count([{"week": "W1"}], "W1")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.weekly_headline_count(
                [{"headline_unit_identifiers": ["u1"]}], "W1")


class TestStartRunOmittedClass(unittest.TestCase):
    def test_omitted_run_class_fails_by_name_at_mod12(self):
        result = mod12.start_run(family_id="f")
        self.assertEqual(result["status"], "input failure")
        self.assertFalse(result["run_started"])
        self.assertIn("input", result["failure"].lower())
        self.assertNotEqual(result.get("failure"), "DERIVATION-GATED")

    def test_omitted_arguments_fail_by_name(self):
        result = mod12.start_run()
        self.assertEqual(result["status"], "input failure")
        self.assertFalse(result["run_started"])

    def test_explicit_forms_stand(self):
        none_class = mod12.start_run(run_class=None, family_id="f")
        self.assertEqual(none_class["status"], "input failure")
        gated = mod12.start_run(run_class="screening", family_id="f")
        self.assertEqual(gated["failure"], "DERIVATION-GATED")
        self.assertFalse(gated["run_started"])


if __name__ == "__main__":
    unittest.main()

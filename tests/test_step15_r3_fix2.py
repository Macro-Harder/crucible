# Step 15 Round 3 fix tests, cluster R3-2. MOD-14 operator surface.
import unittest

import crucible.mod14 as mod14

SEALED = "sealed family record"
CLOSED = "closed run record"
CHECKPOINT = "checkpoint set"


class TestDottedAndSlashedTargetsRefused(unittest.TestCase):
    def test_breaker_forms_verbatim_refused(self):
        actions = (
            {"kind": "delete", "target": "sealed.family.record"},
            {"kind": "purge", "target": "sealed.family.record"},
            {"kind": "delete", "target": "sealed/family/record"},
            {"kind": "destroy", "target": "closed.run.record"},
            {"kind": "delete", "target": "checkpoint.set"},
        )
        for action in actions:
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_breaker_reason_form_reports_protected_target(self):
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "delete", "target": "sealed.family.record"})
        self.assertFalse(verdict["allowed"])
        self.assertIn("sealed family record", verdict["reason"])
        self.assertNotIn("no protected target", verdict["reason"])

    def test_mixed_joined_dresses_refused(self):
        targets = (
            "sealed/family.record",
            "sealed.family/record",
            "SEALED.FAMILY.RECORD",
            "sealed_family.record",
            "sealed-family/record",
            "closed/run/record",
            "checkpoint/set",
        )
        for target in targets:
            action = {"kind": "delete", "target": target}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_joined_dress_on_other_protected_acts_refused(self):
        actions = (
            {"kind": "edit", "target": "sealed.family.record"},
            {"kind": "edit", "target": "closed.run.record"},
            {"kind": "destroy", "target": "closed/run/record",
             "path": "flag rule"},
            {"kind": "edit", "target": "checkpoint.set"},
            {"kind": "purge", "target": "checkpoint/set"},
        )
        for action in actions:
            self.assertFalse(mod14.validate_operator_action(action), action)


class TestLawfulActsStillAdmitted(unittest.TestCase):
    def test_permitted_paths_in_joined_dress_stand(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed.run.record",
             "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint.set",
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "checkpoint/set",
             "path": "deletion rule"}))

    def test_read_acts_in_joined_dress_stand(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "sealed.family.record"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "closed/run/record"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "checkpoint.set"}))

    def test_standing_lawful_controls_stand(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CLOSED, "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": CHECKPOINT,
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CHECKPOINT,
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": CHECKPOINT}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "DeLeTe!!", "target": "checkpoint sets",
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "EdIt!!", "target": "closed run records",
             "path": "flag rule"}))

    def test_lawful_acts_on_unprotected_targets_stand(self):
        for kind in ("edit", "delete", "read"):
            action = {"kind": kind, "target": "ordinary.record"}
            self.assertTrue(mod14.validate_operator_action(action), action)
            action = {"kind": kind, "target": "ordinary/record"}
            self.assertTrue(mod14.validate_operator_action(action), action)


class TestRound2PinsStillRefuse(unittest.TestCase):
    def test_widened_verb_spellings_refused_on_sealed(self):
        verbs = (
            "purge", "drop", "wipe", "clear", "truncate", "expunge",
            "amend", "patch", "redact", "replace", "void", "supersede",
            "obliterate", "annihilate", "correct",
            "deleted", "deleting", "edit.", "DELETE!",
            "remove all", "erase-record",
        )
        for verb in verbs:
            action = {"kind": verb, "target": SEALED}
            self.assertFalse(mod14.validate_operator_action(action), action)

    def test_punctuation_and_article_target_forms_refused(self):
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
            {"kind": "delete", "target": 123},
            {"kind": 123, "target": "sealed.family.record"},
        )
        for action in actions:
            self.assertFalse(mod14.validate_operator_action(action), action)
            verdict = mod14.validate_operator_action_with_reason(action)
            self.assertFalse(verdict["allowed"], action)

    def test_destroy_on_closed_via_flag_path_refused(self):
        for verb in ("destroy", "delete", "purge"):
            action = {"kind": verb, "target": CLOSED, "path": "flag rule"}
            self.assertFalse(mod14.validate_operator_action(action), action)
        action = {"kind": "destroy", "target": "closed.run.record",
                  "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_sealed_admits_no_rule_path_in_any_dress(self):
        for target in (SEALED, "sealed.family.record", "sealed/family/record"):
            action = {"kind": "edit", "target": target, "path": "flag rule"}
            self.assertFalse(mod14.validate_operator_action(action), action)


if __name__ == "__main__":
    unittest.main()

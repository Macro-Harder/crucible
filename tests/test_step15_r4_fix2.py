# Step 15 Round 4 fix tests, cluster R4-2. MOD-14 operator surface.
import unittest

import crucible.mod14 as mod14

SEALED = "sealed family record"
CLOSED = "closed run record"
CHECKPOINT = "checkpoint set"

BREAKER_TARGETS = (
    "sealed\\family\\record", "sealed;family;record",
    "sealed:family:record", "sealed;;family;;record",
    "sealed::family::record", "closed\\run\\record",
    "closed;run;record", "closed:run:record",
    "checkpoint\\set", "checkpoint;set", "checkpoint:set",
)


class TestBreakerDressesRefused(unittest.TestCase):
    def test_breaker_forms_verbatim_refused(self):
        for target in BREAKER_TARGETS:
            for verb in ("delete", "purge", "destroy"):
                action = {"kind": verb, "target": target}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)

    def test_breaker_flag_path_destroy_refused(self):
        action = {"kind": "destroy", "target": "closed\\run\\record",
                  "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action))

    def test_breaker_reason_form_reports_barred(self):
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "destroy", "target": "closed;run;record",
             "path": "flag rule"})
        self.assertFalse(verdict["allowed"])
        self.assertIn("closed run record", verdict["reason"])

    def test_reason_form_on_backslash_sealed_names_target(self):
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "delete", "target": "sealed\\family\\record"})
        self.assertFalse(verdict["allowed"])
        self.assertIn("sealed family record", verdict["reason"])
        self.assertNotIn("no protected target", verdict["reason"])

    def test_mixed_new_separator_dresses_refused(self):
        targets = (
            "sealed\\family;record", "sealed;family:record",
            "sealed:family\\record", "closed:run\\record",
            "closed\\run;record", "checkpoint:\\set",
            "SEALED\\FAMILY;RECORD", "Closed:Run\\Record",
        )
        for target in targets:
            for verb in ("delete", "edit"):
                action = {"kind": verb, "target": target}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)

    def test_every_separator_dress_refused(self):
        separators = (
            "_", "-", ".", "/", "\\", ";", ":", "+", " ",
            "\t", "\n",
        )
        for separator in separators:
            target = separator.join(("sealed", "family", "record"))
            action = {"kind": "delete", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
            target = separator.join(("closed", "run", "record"))
            action = {"kind": "destroy", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
            target = separator.join(("checkpoint", "set"))
            action = {"kind": "delete", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_folded_joined_targets_refused(self):
        actions = (
            {"kind": "delete", "target": "sealedfamilyrecord"},
            {"kind": "purge", "target": "sealedfamilyrecord"},
            {"kind": "destroy", "target": "closedrunrecord"},
            {"kind": "delete", "target": "checkpointset"},
            {"kind": "edit", "target": "sealedfamilyrecord",
             "path": "flagrule"},
        )
        for action in actions:
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_sealed_admits_no_rule_path_in_new_dresses(self):
        for target in ("sealed\\family\\record",
                       "sealed;family;record",
                       "sealed:family:record"):
            for path in ("flag rule", "deletion rule",
                         "flag\\rule", "deletion;rule"):
                action = {"kind": "edit", "target": target,
                          "path": path}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)

    def test_checkpoint_recognised_on_deletion_path_only(self):
        for target in ("checkpoint\\set", "checkpoint;set",
                       "checkpoint:set"):
            action = {"kind": "delete", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
            action = {"kind": "delete", "target": target,
                      "path": "flag rule"}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
            action = {"kind": "edit", "target": target,
                      "path": "flag\\rule"}
            self.assertFalse(
                mod14.validate_operator_action(action), action)


class TestLawfulActsStillAdmitted(unittest.TestCase):
    def test_flag_backslash_rule_path_edit_admitted(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CLOSED, "path": "flag\\rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed\\run\\record",
             "path": "flag\\rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed;run;record",
             "path": "flag:rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closedrunrecord",
             "path": "flagrule"}))

    def test_deletion_rule_in_new_path_dresses_admitted(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint\\set",
             "path": "deletion\\rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "checkpoint;set",
             "path": "deletion;rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint:set",
             "path": "deletion:rule"}))

    def test_read_acts_in_new_dresses_admitted(self):
        for target in ("sealed\\family\\record",
                       "sealed;family;record",
                       "closed:run:record",
                       "checkpoint\\set"):
            action = {"kind": "read", "target": target}
            self.assertTrue(
                mod14.validate_operator_action(action), action)

    def test_round4_confirmed_joined_lawful_acts_stand(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed.run.record",
             "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "delete", "target": "checkpoint.set",
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": "checkpoint/set",
             "path": "deletion rule"}))
        for target in ("sealed.family.record", "closed/run/record",
                       "checkpoint.set", "sealed/family/record"):
            action = {"kind": "read", "target": target}
            self.assertTrue(
                mod14.validate_operator_action(action), action)
        for kind in ("edit", "delete", "read"):
            for target in ("ordinary.record", "ordinary/record",
                           "ordinary\\record", "ordinary;record"):
                action = {"kind": kind, "target": target}
                self.assertTrue(
                    mod14.validate_operator_action(action), action)


class TestStandingRefusalsStillRefuse(unittest.TestCase):
    def test_dotted_and_slashed_forms_still_refused(self):
        actions = (
            {"kind": "delete", "target": "sealed.family.record"},
            {"kind": "purge", "target": "sealed/family/record"},
            {"kind": "destroy", "target": "closed.run.record",
             "path": "flag rule"},
            {"kind": "delete", "target": "checkpoint.set"},
            {"kind": "delete", "target": "sealed..family..record"},
            {"kind": "destroy", "target": "closed/run/record/"},
        )
        for action in actions:
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_standing_verb_and_target_forms_still_refused(self):
        for verb in ("deleted", "deleting", "edit.", "DELETE!",
                     "remove all", "erase-record", "obliterate"):
            action = {"kind": verb, "target": SEALED}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
        for target in ("sealed family record.",
                       "the sealed family record",
                       "sealed family records!",
                       "sealed families record"):
            action = {"kind": "delete", "target": target}
            self.assertFalse(
                mod14.validate_operator_action(action), action)
        for action in ({"kind": ["delete"], "target": SEALED},
                       {"kind": "delete", "target": [SEALED]},
                       {"kind": 123, "target": SEALED}):
            self.assertFalse(
                mod14.validate_operator_action(action), action)


if __name__ == "__main__":
    unittest.main()

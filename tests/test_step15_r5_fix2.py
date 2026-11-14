# Step 15 Round 5 fix tests, cluster R5-2. MOD-14 operator surface.
import unittest

import crucible.mod14 as mod14

SEALED = "sealed family record"
CLOSED = "closed run record"
CHECKPOINT = "checkpoint set"

LETTER_DRESSED_TARGETS = (
    "s\u00e9aled family record",
    "sealed family r\u00e9cord",
    "\uff53ealed family record",
    "\uff53\uff45\uff41\uff4c\uff45\uff44 \uff46\uff41\uff4d\uff49"
    "\uff4c\uff59 \uff52\uff45\uff43\uff4f\uff52\uff44",
    "se\u0430led family record",
    "closed run rec\u043erd",
    "checkpoint s\u00e9t",
    "\u0441\u0435\u0430\u043b\u0435\u0434 family record",
    "sea1ed family record",
    "sealed famil5y record",
    "sealedx family record",
    "sealeed family record",
    "sealed family recordx",
    "clxosed run record",
)

COMPOSITE_TARGETS = (
    "sealedfamilyrecordclosedrunrecord",
    "closedrunrecordcheckpointset",
    "sealed family record closed run record",
    "sealed family record/closed run record",
    "sealed family record archive",
    "sealed family record sealed family record",
)


class TestLetterDressedTargetsRefused(unittest.TestCase):
    def test_breaker_letter_dresses_verbatim_refused(self):
        for target in LETTER_DRESSED_TARGETS:
            for verb in ("delete", "purge", "destroy"):
                action = {"kind": verb, "target": target}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)

    def test_breaker_flag_path_destroy_in_letter_dress_refused(self):
        for target in ("clos\u00e9d run record",
                       "\uff43losed run record"):
            action = {"kind": "destroy", "target": target,
                      "path": "flag rule"}
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_breaker_reason_form_names_the_bar(self):
        verdict = mod14.validate_operator_action_with_reason(
            {"kind": "delete", "target": "s\u00e9aled family record"})
        self.assertFalse(verdict["allowed"])
        self.assertIn("sealed family record", verdict["reason"])
        self.assertNotIn("no protected target", verdict["reason"])

    def test_letter_dressed_verbs_refused(self):
        for verb in ("d\u00e9lete", "d\u0435lete", "del3te",
                     "\uff44estroy"):
            action = {"kind": verb, "target": SEALED}
            self.assertFalse(
                mod14.validate_operator_action(action), action)

    def test_letter_dress_on_every_protected_target(self):
        for target in ("sealed family rec\u043erd",
                       "cl\u00f3sed run record",
                       "checkp\u043eint set",
                       "checkpoint se7"):
            for verb in ("delete", "purge", "destroy"):
                action = {"kind": verb, "target": target}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)


class TestCompositeTargetsRefused(unittest.TestCase):
    def test_breaker_composites_verbatim_refused(self):
        for target in COMPOSITE_TARGETS:
            for verb in ("delete", "purge", "destroy"):
                action = {"kind": verb, "target": target}
                self.assertFalse(
                    mod14.validate_operator_action(action), action)

    def test_breaker_reason_form_names_protected_target_touched(self):
        for target in ("sealed family record closed run record",
                       "sealed family record/closed run record"):
            verdict = mod14.validate_operator_action_with_reason(
                {"kind": "delete", "target": target})
            self.assertFalse(verdict["allowed"])
            self.assertIn("sealed family record", verdict["reason"])
            self.assertNotIn("no protected target", verdict["reason"])

    def test_composite_on_a_rule_path_still_refused(self):
        action = {"kind": "destroy",
                  "target": "closed run record checkpoint set",
                  "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action))
        action = {"kind": "edit",
                  "target": "closed run record checkpoint set",
                  "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action))
        action = {"kind": "delete",
                  "target": "checkpoint set sealed family record",
                  "path": "deletion rule"}
        self.assertFalse(mod14.validate_operator_action(action))

    def test_composite_read_still_admitted(self):
        for target in COMPOSITE_TARGETS:
            action = {"kind": "read", "target": target}
            self.assertTrue(
                mod14.validate_operator_action(action), action)


class TestContainmentBoundaryBothWays(unittest.TestCase):
    def test_lawful_targets_sharing_letters_admitted(self):
        for target in ("sealed family", "family record archive",
                       "record archive", "checkpoint",
                       "closed run", "run record book",
                       "sealed record", "family set"):
            for verb in ("delete", "purge", "destroy"):
                action = {"kind": verb, "target": target}
                self.assertTrue(
                    mod14.validate_operator_action(action), action)

    def test_lawful_names_with_accents_or_non_latin_letters(self):
        for target in ("caf\u00e9 record archive",
                       "\u0430rchive box",
                       "r\u00e9sum\u00e9 file"):
            action = {"kind": "delete", "target": target}
            self.assertTrue(
                mod14.validate_operator_action(action), action)

    def test_standing_lawful_paths_still_admitted(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CLOSED, "path": "flag rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "edit", "target": CHECKPOINT,
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "destroy", "target": CHECKPOINT,
             "path": "deletion rule"}))
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": SEALED}))

    def test_standing_refusals_still_refuse(self):
        for action in (
                {"kind": "delete", "target": SEALED},
                {"kind": "destroy", "target": CLOSED,
                 "path": "flag rule"},
                {"kind": "delete", "target": CHECKPOINT},
                {"kind": "edit", "target": SEALED,
                 "path": "deletion rule"}):
            self.assertFalse(
                mod14.validate_operator_action(action), action)


if __name__ == "__main__":
    unittest.main()

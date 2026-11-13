"""Test group TG-15.1. Shell owns no rule.
Slice S-15, Shell, MOD-14. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod14, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod14 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod14 absent, pinned behaviour unmet: " + behaviour)


class TestTG151(unittest.TestCase):
    def test_no_rule_in_the_shell(self):
        """
        Fixture: The shell command surface inspected command by command.
        Pins: Every command carries inputs to a named module and returns its outputs or its named failure; no command computes a reputation, a verdict, a retention tier, or a result wording.
        Bar: A shell level computation of any quantity a core owns fails this group, even where the computed value agrees with the core value, because agreement today is drift tomorrow.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.1 and this behaviour; a command computing a reputation, a verdict, a retention tier, or a result wording fails this test when the surface stands.
        """
        require_surface(self, "TG-15.1", "no rule in the shell, every command carries inputs to a named module and returns its outputs or its named failure")
        import crucible.mod14 as surface
        commands = surface.command_surface()
        self.assertTrue(commands)
        for entry in commands:
            self.assertIn("carries_to", entry)
            self.assertFalse(entry["computes_rule"])
            self.assertIsNone(surface.command_computes(entry["command"]))
        started = surface.run_command("start_run", {"run_class": "screening", "family_id": "fam-1"}, run_id="run-1")
        self.assertEqual(started["failure"], "DERIVATION-GATED")
        self.assertEqual(started["gate"], "DQ7-02")
        self.assertFalse(started["run_started"])

    def test_error_carriage(self):
        """
        Fixture: One failing run per named failure form, driven through the command surface.
        Pins: Errors are handled with context or propagated, never swallowed; a named failure reaches the operator as a named failure with its run identifier and its stage.
        Bar: A command that exits cleanly over a failed run, or that converts a failure into an empty result, fails this group.
        Failure: Fails while crucible.mod14 stands absent, naming TG-15.1 and this behaviour; a command exiting cleanly over a failed run, or converting a failure into an empty result, fails this test when the surface stands.
        """
        require_surface(self, "TG-15.1", "error carriage, a named failure reaches the operator with its run identifier and its stage, never swallowed")
        import crucible.mod14 as surface
        carriage = surface.error_carriage("named failure under test", run_id="run-9", stage="stage-2")
        self.assertEqual(carriage["failure"], "named failure under test")
        self.assertEqual(carriage["run_id"], "run-9")
        self.assertEqual(carriage["stage"], "stage-2")
        self.assertFalse(carriage["swallowed"])
        self.assertFalse(carriage["converted_to_empty_result"])
        self.assertTrue(carriage["operator_sees_failure"])
        unknown = surface.run_command("no_such_command", {}, run_id="run-9")
        self.assertIn("failure", unknown)
        self.assertEqual(unknown["run_id"], "run-9")
        self.assertFalse(unknown["swallowed"])


if __name__ == "__main__":
    unittest.main()

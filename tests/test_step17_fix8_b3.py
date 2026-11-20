"""Step 17 fix wave 8, Builder 3 defect tests (FW8-01, Medium,
ruling T17R7-02, the mod14 and mod16 part).

The extra argument family: at each door named in the Red 2
filing R7-RED2-01, and at each family door of the same signature
in mod14 and mod16 read at the cure test writing, an extra
argument handing, in positional form and in keyword form, must
stand refused in the named form of its module, stating the
door, the ground, and the next step, in the FW6-03 and FW7-01
cure form, instead of escaping as a bare interpreter TypeError.

The charged doors stand filed at these bare sentence lengths:
mod14.run_command at 69 characters, mod14.pilot_run at 67
characters, mod16.fixture_record at 72 characters, and
mod16.horizon_run_cost at 64 characters, each in positional
form. The family reading at the cure test writing probed every
public door of mod14 and mod16 in both handing forms on the
bench: every public door of both modules escaped as a bare
interpreter TypeError in both forms, so every public door of
both modules stands in this file. Outcomes stand judged by
stored value in code, never by a repr of a returned value
(T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod14 as mod14
import crucible.mod16 as mod16


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, exc_type, door_word, call):
    """The call refuses in named form: the module named type,
    never a bare TypeError, the message carrying the door, the
    beyond ground, a next step, and no bare interpreter phrase."""
    with case.assertRaises(exc_type) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message.lower())
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


def check_run_command_refusal(case, call):
    """The run_command call refuses in its carriage form: a
    dict carriage standing as a failure, its stored failure
    text carrying the door, the beyond ground, and a next
    step, and no bare TypeError escaping at the call."""
    result = call()
    case.assertIsInstance(result, dict)
    case.assertIs(result["operator_sees_failure"], True)
    case.assertIs(result["swallowed"], False)
    text = result["failure"] + " " + str(result["failure_value"])
    case.assertIn("run_command", text)
    case.assertIn("beyond", text)
    case.assertIn("next step", text.lower())
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, text)
    return result


class TestFW801Mod14ChargedDoors(unittest.TestCase):

    def test_defect_run_command_extra_positional(self):
        check_run_command_refusal(
            self,
            lambda: mod14.run_command("store_kind_check", {}, None, 1))

    def test_defect_run_command_extra_keyword(self):
        check_run_command_refusal(
            self,
            lambda: mod14.run_command(
                "store_kind_check", {}, None, extra_kw=1))

    def test_defect_pilot_run_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "pilot_run",
            lambda: mod14.pilot_run("timing", None, 1))

    def test_defect_pilot_run_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "pilot_run",
            lambda: mod14.pilot_run("timing", None, extra_kw=1))


class TestFW801Mod16ChargedDoors(unittest.TestCase):

    def test_defect_fixture_record_extra_positional(self):
        check_named_refusal(
            self, mod16.FixtureLookupFailure, "fixture_record",
            lambda: mod16.fixture_record("F-01", 1))

    def test_defect_fixture_record_extra_keyword(self):
        check_named_refusal(
            self, mod16.FixtureLookupFailure, "fixture_record",
            lambda: mod16.fixture_record("F-01", extra_kw=1))

    def test_defect_horizon_run_cost_extra_positional(self):
        check_named_refusal(
            self, ValueError, "horizon_run_cost",
            lambda: mod16.horizon_run_cost(2, 1, 1))

    def test_defect_horizon_run_cost_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "horizon_run_cost",
            lambda: mod16.horizon_run_cost(2, 1, extra_kw=1))


class TestFW801Mod14FamilyDoors(unittest.TestCase):

    def test_defect_command_surface_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "command_surface",
            lambda: mod14.command_surface(1))

    def test_defect_command_surface_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "command_surface",
            lambda: mod14.command_surface(extra_kw=1))

    def test_defect_command_computes_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "command_computes",
            lambda: mod14.command_computes(None, 1))

    def test_defect_command_computes_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "command_computes",
            lambda: mod14.command_computes(None, extra_kw=1))

    def test_defect_error_carriage_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "error_carriage",
            lambda: mod14.error_carriage(None, None, None, 1))

    def test_defect_error_carriage_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "error_carriage",
            lambda: mod14.error_carriage(None, None, None, extra_kw=1))

    def test_defect_flag_evaluation_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "flag_evaluation",
            lambda: mod14.flag_evaluation(None, None, None, None, None, 1))

    def test_defect_flag_evaluation_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "flag_evaluation",
            lambda: mod14.flag_evaluation(
                None, None, None, None, None, extra_kw=1))

    def test_defect_nondeterminism_census_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "nondeterminism_census",
            lambda: mod14.nondeterminism_census(None, 1))

    def test_defect_nondeterminism_census_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "nondeterminism_census",
            lambda: mod14.nondeterminism_census(None, extra_kw=1))

    def test_defect_operator_runbook_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "operator_runbook",
            lambda: mod14.operator_runbook(1))

    def test_defect_operator_runbook_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "operator_runbook",
            lambda: mod14.operator_runbook(extra_kw=1))

    def test_defect_outside_call_check_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "outside_call_check",
            lambda: mod14.outside_call_check(None, None, None, 1))

    def test_defect_outside_call_check_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "outside_call_check",
            lambda: mod14.outside_call_check(None, None, None, extra_kw=1))

    def test_defect_process_and_network_call_log_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "process_and_network_call_log",
            lambda: mod14.process_and_network_call_log(None, 1))

    def test_defect_process_and_network_call_log_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "process_and_network_call_log",
            lambda: mod14.process_and_network_call_log(None, extra_kw=1))

    def test_defect_store_kind_check_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "store_kind_check",
            lambda: mod14.store_kind_check(None, 1))

    def test_defect_store_kind_check_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "store_kind_check",
            lambda: mod14.store_kind_check(None, extra_kw=1))

    def test_defect_store_kind_check_with_reason_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "store_kind_check_with_reason",
            lambda: mod14.store_kind_check_with_reason(None, 1))

    def test_defect_store_kind_check_with_reason_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "store_kind_check_with_reason",
            lambda: mod14.store_kind_check_with_reason(None, extra_kw=1))

    def test_defect_sweep_level_determinism_contract_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "sweep_level_determinism_contract",
            lambda: mod14.sweep_level_determinism_contract(None, 1))

    def test_defect_sweep_level_determinism_contract_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "sweep_level_determinism_contract",
            lambda: mod14.sweep_level_determinism_contract(
                None, extra_kw=1))

    def test_defect_validate_operator_action_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "validate_operator_action",
            lambda: mod14.validate_operator_action(None, 1))

    def test_defect_validate_operator_action_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "validate_operator_action",
            lambda: mod14.validate_operator_action(None, extra_kw=1))

    def test_defect_validate_operator_action_with_reason_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "validate_operator_action_with_reason",
            lambda: mod14.validate_operator_action_with_reason(None, 1))

    def test_defect_validate_operator_action_with_reason_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "validate_operator_action_with_reason",
            lambda: mod14.validate_operator_action_with_reason(
                None, extra_kw=1))

    def test_defect_validate_pilot_claim_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "validate_pilot_claim",
            lambda: mod14.validate_pilot_claim(None, 1))

    def test_defect_validate_pilot_claim_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "validate_pilot_claim",
            lambda: mod14.validate_pilot_claim(None, extra_kw=1))

    def test_defect_dual_rule_retention_simulation_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "dual_rule_retention_simulation",
            lambda: mod14.dual_rule_retention_simulation(None, 1))

    def test_defect_dual_rule_retention_simulation_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure,
            "dual_rule_retention_simulation",
            lambda: mod14.dual_rule_retention_simulation(None, extra_kw=1))

    def test_defect_weekly_headline_count_extra_positional(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "weekly_headline_count",
            lambda: mod14.weekly_headline_count(None, None, 1))

    def test_defect_weekly_headline_count_extra_keyword(self):
        check_named_refusal(
            self, mod14.NamedShellFailure, "weekly_headline_count",
            lambda: mod14.weekly_headline_count(None, None, extra_kw=1))


class TestFW801Mod16FamilyDoors(unittest.TestCase):

    def test_defect_run_tracer_cut_extra_positional(self):
        check_named_refusal(
            self, ValueError, "run_tracer_cut",
            lambda: mod16.run_tracer_cut(1))

    def test_defect_run_tracer_cut_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "run_tracer_cut",
            lambda: mod16.run_tracer_cut(extra_kw=1))

    def test_defect_tracer_record_extra_positional(self):
        check_named_refusal(
            self, ValueError, "tracer_record",
            lambda: mod16.tracer_record(1))

    def test_defect_tracer_record_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "tracer_record",
            lambda: mod16.tracer_record(extra_kw=1))

    def test_defect_validate_tracer_wording_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_tracer_wording",
            lambda: mod16.validate_tracer_wording(None, 1))

    def test_defect_validate_tracer_wording_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_tracer_wording",
            lambda: mod16.validate_tracer_wording(None, extra_kw=1))

    def test_defect_fixture_inventory_extra_positional(self):
        check_named_refusal(
            self, ValueError, "fixture_inventory",
            lambda: mod16.fixture_inventory(1))

    def test_defect_fixture_inventory_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "fixture_inventory",
            lambda: mod16.fixture_inventory(extra_kw=1))

    def test_defect_f01_centre_only_unit_extra_positional(self):
        check_named_refusal(
            self, ValueError, "f01_centre_only_unit",
            lambda: mod16.f01_centre_only_unit(1))

    def test_defect_f01_centre_only_unit_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "f01_centre_only_unit",
            lambda: mod16.f01_centre_only_unit(extra_kw=1))

    def test_defect_validate_fixture_record_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_fixture_record",
            lambda: mod16.validate_fixture_record(None, 1))

    def test_defect_validate_fixture_record_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_fixture_record",
            lambda: mod16.validate_fixture_record(None, extra_kw=1))

    def test_defect_exercise_run_class_extra_positional(self):
        check_named_refusal(
            self, ValueError, "exercise_run_class",
            lambda: mod16.exercise_run_class(None, None, 1))

    def test_defect_exercise_run_class_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "exercise_run_class",
            lambda: mod16.exercise_run_class(None, None, extra_kw=1))

    def test_defect_exercise_confirmation_and_headline_extra_positional(self):
        check_named_refusal(
            self, ValueError, "exercise_confirmation_and_headline",
            lambda: mod16.exercise_confirmation_and_headline(1))

    def test_defect_exercise_confirmation_and_headline_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "exercise_confirmation_and_headline",
            lambda: mod16.exercise_confirmation_and_headline(extra_kw=1))

    def test_defect_validate_confirmation_result_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_confirmation_result",
            lambda: mod16.validate_confirmation_result(None, 1))

    def test_defect_validate_confirmation_result_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_confirmation_result",
            lambda: mod16.validate_confirmation_result(None, extra_kw=1))

    def test_defect_validate_headline_claim_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_headline_claim",
            lambda: mod16.validate_headline_claim(None, 1))

    def test_defect_validate_headline_claim_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_headline_claim",
            lambda: mod16.validate_headline_claim(None, extra_kw=1))

    def test_defect_folding_check_record_extra_positional(self):
        check_named_refusal(
            self, ValueError, "folding_check_record",
            lambda: mod16.folding_check_record(1))

    def test_defect_folding_check_record_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "folding_check_record",
            lambda: mod16.folding_check_record(extra_kw=1))

    def test_defect_validate_folding_discharge_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_folding_discharge",
            lambda: mod16.validate_folding_discharge(None, 1))

    def test_defect_validate_folding_discharge_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_folding_discharge",
            lambda: mod16.validate_folding_discharge(None, extra_kw=1))

    def test_defect_sham_control_standing_extra_positional(self):
        check_named_refusal(
            self, ValueError, "sham_control_standing",
            lambda: mod16.sham_control_standing(1))

    def test_defect_sham_control_standing_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "sham_control_standing",
            lambda: mod16.sham_control_standing(extra_kw=1))

    def test_defect_validate_sham_result_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_sham_result",
            lambda: mod16.validate_sham_result(None, 1))

    def test_defect_validate_sham_result_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_sham_result",
            lambda: mod16.validate_sham_result(None, extra_kw=1))

    def test_defect_horizon_application_extra_positional(self):
        check_named_refusal(
            self, ValueError, "horizon_application",
            lambda: mod16.horizon_application(None, None, 1))

    def test_defect_horizon_application_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "horizon_application",
            lambda: mod16.horizon_application(None, None, extra_kw=1))

    def test_defect_validate_horizon_generalisation_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_horizon_generalisation",
            lambda: mod16.validate_horizon_generalisation(None, 1))

    def test_defect_validate_horizon_generalisation_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_horizon_generalisation",
            lambda: mod16.validate_horizon_generalisation(None, extra_kw=1))

    def test_defect_validate_mixed_patience_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_mixed_patience",
            lambda: mod16.validate_mixed_patience(None, 1))

    def test_defect_validate_mixed_patience_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_mixed_patience",
            lambda: mod16.validate_mixed_patience(None, extra_kw=1))

    def test_defect_refusal_set_extra_positional(self):
        check_named_refusal(
            self, ValueError, "refusal_set",
            lambda: mod16.refusal_set(1))

    def test_defect_refusal_set_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "refusal_set",
            lambda: mod16.refusal_set(extra_kw=1))

    def test_defect_validate_refusal_coverage_extra_positional(self):
        check_named_refusal(
            self, ValueError, "validate_refusal_coverage",
            lambda: mod16.validate_refusal_coverage(None, 1))

    def test_defect_validate_refusal_coverage_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "validate_refusal_coverage",
            lambda: mod16.validate_refusal_coverage(None, extra_kw=1))


class TestFW801Controls(unittest.TestCase):

    def test_control_run_command_served(self):
        result = mod14.run_command("store_kind_check", {"kind": "sweep"})
        self.assertIs(result["store_kind_ok"], True)

    def test_control_run_command_missing_named(self):
        result = mod14.run_command()
        self.assertIs(result["operator_sees_failure"], True)
        text = result["failure"] + " " + str(result["failure_value"])
        self.assertIn("run_command", text)
        self.assertIn("missing", text)
        self.assertIn("next step", text.lower())

    def test_control_pilot_run_served(self):
        result = mod14.pilot_run("timing")
        self.assertEqual(result["confinement_label"], "pilot confined")
        self.assertEqual(result["use"], "timing")

    def test_control_pilot_run_missing_named(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.pilot_run()
        self.assertIn("next step", str(caught.exception).lower())

    def test_control_fixture_record_served(self):
        line = mod16.fixture_record("F-01")
        self.assertEqual(line["fixture"], "F-01")

    def test_control_fixture_record_unknown_named(self):
        with self.assertRaises(mod16.FixtureLookupFailure):
            mod16.fixture_record("no-such-fixture")

    def test_control_fixture_record_missing_named(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record()
        self.assertIn("next step", str(caught.exception).lower())

    def test_control_horizon_run_cost_served(self):
        result = mod16.horizon_run_cost(2, 1)
        self.assertEqual(result, {
            "form": "days multiplied",
            "days": 2,
            "base_days": 1,
            "labelled": "estimated",
        })

    def test_control_fixture_inventory_served(self):
        self.assertEqual(len(mod16.fixture_inventory()), 30)

    def test_control_horizon_application_served(self):
        self.assertIs(mod16.horizon_application(1, [1]), True)
        self.assertIs(mod16.horizon_application(1, [2]), False)

    def test_control_store_kind_check_served(self):
        self.assertIs(mod14.store_kind_check("sweep"), True)

    def test_control_validate_sham_result_served(self):
        self.assertIs(mod16.validate_sham_result(None), True)

    def test_control_command_computes_served(self):
        self.assertIsNone(mod14.command_computes("start_run"))

    def test_control_refusal_set_served(self):
        self.assertGreater(len(mod16.refusal_set()), 0)


if __name__ == "__main__":
    unittest.main()

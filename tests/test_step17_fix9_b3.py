"""Step 17 fix wave 9, Builder 3 defect tests (FW9-01, Medium,
ruling T17R8-01, Slice 3, the mod12 part).

The extra argument family: at each of the 39 doors of mod12
named in the Red 2 enumeration carried at ruling T17R8-01, an
extra argument handing, in keyword form and in positional
form, must stand refused in the named form of its module,
stating the door, the ground, and the next step, in the
FW8-01 cure form, instead of escaping as a bare interpreter
TypeError. The family door reading at the cure test writing
read every public door of mod12: 43 public doors in all, the
39 doors of this slice escaping in both handing forms and
the four cured doors of the earlier waves (start_run,
start_sweep, seal_family_record, and validate_family_record)
standing in named form in both handings, pinned below as
standing tests. No door of this slice stands at a gated start
door; the gated standings at the two start doors stand pinned
by the standing tests, run_started False and seed_drawn False
at every handing. Outcomes stand judged by stored value in
code, never by a repr of a returned value (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod12 as mod12


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "positional argument but",
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


class TestFW901Mod12Doors(unittest.TestCase):

    def test_defect_admit_claim_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "admit_claim",
            lambda: mod12.admit_claim(None, None, 1))

    def test_defect_admit_claim_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "admit_claim",
            lambda: mod12.admit_claim(None, None, extra_kw=1))

    def test_defect_alias_divergences_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "alias_divergences",
            lambda: mod12.alias_divergences(None, 1))

    def test_defect_alias_divergences_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "alias_divergences",
            lambda: mod12.alias_divergences(None, extra_kw=1))

    def test_defect_apply_family_edit_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "apply_family_edit",
            lambda: mod12.apply_family_edit(None, None, 1))

    def test_defect_apply_family_edit_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "apply_family_edit",
            lambda: mod12.apply_family_edit(None, None, extra_kw=1))

    def test_defect_claim_label_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "claim_label",
            lambda: mod12.claim_label(None, 1))

    def test_defect_claim_label_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "claim_label",
            lambda: mod12.claim_label(None, extra_kw=1))

    def test_defect_counting_basis_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "counting_basis",
            lambda: mod12.counting_basis(None, 1))

    def test_defect_counting_basis_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "counting_basis",
            lambda: mod12.counting_basis(None, extra_kw=1))

    def test_defect_decay_arm_readout_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "decay_arm_readout",
            lambda: mod12.decay_arm_readout(None, None, 1))

    def test_defect_decay_arm_readout_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "decay_arm_readout",
            lambda: mod12.decay_arm_readout(None, None, extra_kw=1))

    def test_defect_family_record_presentation_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_record_presentation",
            lambda: mod12.family_record_presentation(None, 1))

    def test_defect_family_record_presentation_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_record_presentation",
            lambda: mod12.family_record_presentation(None, extra_kw=1))

    def test_defect_family_record_validation_failures_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_record_validation_failures",
            lambda: mod12.family_record_validation_failures(None, 1))

    def test_defect_family_record_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_record_validation_failures",
            lambda: mod12.family_record_validation_failures(None, extra_kw=1))

    def test_defect_family_version_parts_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_version_parts",
            lambda: mod12.family_version_parts(None, 1))

    def test_defect_family_version_parts_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family_version_parts",
            lambda: mod12.family_version_parts(None, extra_kw=1))

    def test_defect_grid_artefacts_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "grid_artefacts",
            lambda: mod12.grid_artefacts(None, 1))

    def test_defect_grid_artefacts_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "grid_artefacts",
            lambda: mod12.grid_artefacts(None, extra_kw=1))

    def test_defect_grid_decision_log_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "grid_decision_log",
            lambda: mod12.grid_decision_log(1))

    def test_defect_grid_decision_log_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "grid_decision_log",
            lambda: mod12.grid_decision_log(extra_kw=1))

    def test_defect_hostile_family_status_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "hostile_family_status",
            lambda: mod12.hostile_family_status(None, 1))

    def test_defect_hostile_family_status_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "hostile_family_status",
            lambda: mod12.hostile_family_status(None, extra_kw=1))

    def test_defect_hostile_kind_counts_as_run_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "hostile_kind_counts_as_run",
            lambda: mod12.hostile_kind_counts_as_run(None, None, None, 1))

    def test_defect_hostile_kind_counts_as_run_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "hostile_kind_counts_as_run",
            lambda: mod12.hostile_kind_counts_as_run(None, None, None, extra_kw=1))

    def test_defect_kill_check_for_claim_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "kill_check_for_claim",
            lambda: mod12.kill_check_for_claim(None, 1))

    def test_defect_kill_check_for_claim_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "kill_check_for_claim",
            lambda: mod12.kill_check_for_claim(None, extra_kw=1))

    def test_defect_kill_checks_for_family_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "kill_checks_for_family",
            lambda: mod12.kill_checks_for_family(None, None, 1))

    def test_defect_kill_checks_for_family_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "kill_checks_for_family",
            lambda: mod12.kill_checks_for_family(None, None, extra_kw=1))

    def test_defect_look_register_for_family_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "look_register_for_family",
            lambda: mod12.look_register_for_family(None, 1))

    def test_defect_look_register_for_family_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "look_register_for_family",
            lambda: mod12.look_register_for_family(None, extra_kw=1))

    def test_defect_make_family_record_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "make_family_record",
            lambda: mod12.make_family_record(None, None, None, 1))

    def test_defect_make_family_record_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "make_family_record",
            lambda: mod12.make_family_record(None, None, None, extra_kw=1))

    def test_defect_readout_status_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "readout_status",
            lambda: mod12.readout_status(None, 1))

    def test_defect_readout_status_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "readout_status",
            lambda: mod12.readout_status(None, extra_kw=1))

    def test_defect_record_version_sets_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "record_version_sets",
            lambda: mod12.record_version_sets(None, 1))

    def test_defect_record_version_sets_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "record_version_sets",
            lambda: mod12.record_version_sets(None, extra_kw=1))

    def test_defect_registry_basis_fields_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "registry_basis_fields",
            lambda: mod12.registry_basis_fields(1))

    def test_defect_registry_basis_fields_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "registry_basis_fields",
            lambda: mod12.registry_basis_fields(extra_kw=1))

    def test_defect_retained_run_record_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "retained_run_record",
            lambda: mod12.retained_run_record(None, None, 1))

    def test_defect_retained_run_record_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "retained_run_record",
            lambda: mod12.retained_run_record(None, None, extra_kw=1))

    def test_defect_run_class_markings_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "run_class_markings",
            lambda: mod12.run_class_markings(1))

    def test_defect_run_class_markings_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "run_class_markings",
            lambda: mod12.run_class_markings(extra_kw=1))

    def test_defect_run_record_validation_failures_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "run_record_validation_failures",
            lambda: mod12.run_record_validation_failures(None, 1))

    def test_defect_run_record_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "run_record_validation_failures",
            lambda: mod12.run_record_validation_failures(None, extra_kw=1))

    def test_defect_sample_statement_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "sample_statement",
            lambda: mod12.sample_statement(None, 1))

    def test_defect_sample_statement_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "sample_statement",
            lambda: mod12.sample_statement(None, extra_kw=1))

    def test_defect_screening_readout_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "screening_readout",
            lambda: mod12.screening_readout(None, None, 1))

    def test_defect_screening_readout_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "screening_readout",
            lambda: mod12.screening_readout(None, None, extra_kw=1))

    def test_defect_sweep_manifest_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "sweep_manifest",
            lambda: mod12.sweep_manifest(None, 1))

    def test_defect_sweep_manifest_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "sweep_manifest",
            lambda: mod12.sweep_manifest(None, extra_kw=1))

    def test_defect_top_up_applies_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "top_up_applies",
            lambda: mod12.top_up_applies(None, None, 1))

    def test_defect_top_up_applies_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "top_up_applies",
            lambda: mod12.top_up_applies(None, None, extra_kw=1))

    def test_defect_validate_cost_claim_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_cost_claim",
            lambda: mod12.validate_cost_claim(None, 1))

    def test_defect_validate_cost_claim_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_cost_claim",
            lambda: mod12.validate_cost_claim(None, extra_kw=1))

    def test_defect_validate_decay_readout_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_decay_readout",
            lambda: mod12.validate_decay_readout(None, 1))

    def test_defect_validate_decay_readout_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_decay_readout",
            lambda: mod12.validate_decay_readout(None, extra_kw=1))

    def test_defect_validate_family_pooling_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_family_pooling",
            lambda: mod12.validate_family_pooling(None, 1))

    def test_defect_validate_family_pooling_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_family_pooling",
            lambda: mod12.validate_family_pooling(None, extra_kw=1))

    def test_defect_validate_grid_claim_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_grid_claim",
            lambda: mod12.validate_grid_claim(None, 1))

    def test_defect_validate_grid_claim_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_grid_claim",
            lambda: mod12.validate_grid_claim(None, extra_kw=1))

    def test_defect_validate_kill_check_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_kill_check",
            lambda: mod12.validate_kill_check(None, 1))

    def test_defect_validate_kill_check_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_kill_check",
            lambda: mod12.validate_kill_check(None, extra_kw=1))

    def test_defect_validate_look_decision_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_look_decision",
            lambda: mod12.validate_look_decision(None, 1))

    def test_defect_validate_look_decision_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_look_decision",
            lambda: mod12.validate_look_decision(None, extra_kw=1))

    def test_defect_validate_record_version_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_record_version",
            lambda: mod12.validate_record_version(None, 1))

    def test_defect_validate_record_version_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_record_version",
            lambda: mod12.validate_record_version(None, extra_kw=1))

    def test_defect_validate_run_record_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_run_record",
            lambda: mod12.validate_run_record(None, 1))

    def test_defect_validate_run_record_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_run_record",
            lambda: mod12.validate_run_record(None, extra_kw=1))

    def test_defect_validate_screening_claim_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_screening_claim",
            lambda: mod12.validate_screening_claim(None, 1))

    def test_defect_validate_screening_claim_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_screening_claim",
            lambda: mod12.validate_screening_claim(None, extra_kw=1))

    def test_defect_validate_seed_placement_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_seed_placement",
            lambda: mod12.validate_seed_placement(None, 1))

    def test_defect_validate_seed_placement_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_seed_placement",
            lambda: mod12.validate_seed_placement(None, extra_kw=1))

    def test_defect_validate_sweep_programme_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_sweep_programme",
            lambda: mod12.validate_sweep_programme(None, 1))

    def test_defect_validate_sweep_programme_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "validate_sweep_programme",
            lambda: mod12.validate_sweep_programme(None, extra_kw=1))

    def test_defect_winning_regime_extra_positional(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "winning_regime",
            lambda: mod12.winning_regime(None, 1))

    def test_defect_winning_regime_extra_keyword(self):
        check_named_refusal(
            self, mod12.NamedControllerFailure, "winning_regime",
            lambda: mod12.winning_regime(None, extra_kw=1))


class TestFW901Mod12StandingDoors(unittest.TestCase):
    """The four cured doors of mod12 stand in named form in
    both handings, as controls worked by no cure of this slice."""

    def test_standing_seal_family_record_extra_positional(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family record",
            lambda: mod12.seal_family_record(record, 1))

    def test_standing_seal_family_record_extra_keyword(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family record",
            lambda: mod12.seal_family_record(record, extra_kw=1))

    def test_standing_validate_family_record_extra_positional(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family record",
            lambda: mod12.validate_family_record(record, 1))

    def test_standing_validate_family_record_extra_keyword(self):
        record = mod12.make_family_record()
        check_named_refusal(
            self, mod12.NamedControllerFailure, "family record",
            lambda: mod12.validate_family_record(record, extra_kw=1))

    def test_standing_start_run_extra_positional(self):
        result = mod12.start_run("screening", "fam-1", 1)
        self.assertIsInstance(result, dict)
        self.assertIn("beyond", result["ground_in_words"])
        self.assertTrue(result["next_step"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)

    def test_standing_start_sweep_extra_positional(self):
        result = mod12.start_sweep("fam-1", 1)
        self.assertIsInstance(result, dict)
        self.assertIn("beyond", result["ground_in_words"])
        self.assertTrue(result["next_step"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)

    def test_standing_start_run_extra_keyword_named(self):
        result = mod12.start_run("screening", "fam-1", extra_kw=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["unexpected_keyword_handings"],
                         ["extra_kw"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)

    def test_standing_start_sweep_extra_keyword_named(self):
        result = mod12.start_sweep("fam-1", extra_kw=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["unexpected_keyword_handings"],
                         ["extra_kw"])
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)


class TestFW901Mod12Controls(unittest.TestCase):

    def test_control_make_family_record_served(self):
        record = mod12.make_family_record()
        self.assertIsInstance(record, dict)
        self.assertEqual(record["family_id"], "family-under-test")

    def test_control_family_record_validation_failures_served(self):
        record = mod12.make_family_record()
        self.assertIsInstance(
            mod12.family_record_validation_failures(record), list)

    def test_control_seal_family_record_served(self):
        sealed = mod12.seal_family_record(mod12.make_family_record())
        self.assertIsInstance(sealed, dict)

    def test_control_registry_basis_fields_served(self):
        self.assertTrue(mod12.registry_basis_fields())

    def test_control_run_class_markings_served(self):
        self.assertTrue(mod12.run_class_markings())

    def test_control_grid_decision_log_served(self):
        self.assertTrue(mod12.grid_decision_log())

    def test_control_sample_statement_served(self):
        self.assertIsInstance(mod12.sample_statement(), dict)

    def test_control_counting_basis_served(self):
        self.assertTrue(mod12.counting_basis())

    def test_control_look_register_for_family_served(self):
        self.assertTrue(mod12.look_register_for_family())

    def test_control_family_version_parts_served(self):
        self.assertTrue(mod12.family_version_parts())

    def test_control_record_version_sets_served(self):
        self.assertIsInstance(mod12.record_version_sets(), dict)

    def test_control_start_run_gated(self):
        result = mod12.start_run("screening", "fam-1")
        self.assertIs(result["run_started"], False)
        self.assertIs(result["seed_drawn"], False)


if __name__ == "__main__":
    unittest.main()

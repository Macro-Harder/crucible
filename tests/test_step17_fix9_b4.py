"""Step 17 fix wave 9, Slice 4 defect tests (FW9-01, T17R8-01).

The extra argument family in keyword form and in positional
form at the 25 owed doors of mod13: at each door named in
the slice, the door handed its ordinary arguments plus one
extra argument must refuse in the named form of its module,
NamedReplicationFailure, stating the door, the ground, and
the next step, instead of escaping as a bare interpreter
TypeError. Doors of mod13 already cured in earlier waves
stand as standing controls in the same form, and plain
handings at the doors stand served whole as controls.

Judgement stands by stored value in code: the exception type
and the stored message text, never by a repr.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod13


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "positional argument but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, door_word, call):
    """The call refuses in named form: the module named type,
    never a bare TypeError, the message carrying the door, the
    beyond ground, a next step, and no bare interpreter phrase."""
    with case.assertRaises(mod13.NamedReplicationFailure) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message)
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW901Mod13Charged(unittest.TestCase):

    def test_defect_ac1_check_extra_keyword(self):
        check_named_refusal(
            self, "ac1 check",
            lambda: mod13.ac1_check(*({},), extra_kw=1))

    def test_defect_ac1_check_extra_positional(self):
        check_named_refusal(
            self, "ac1 check",
            lambda: mod13.ac1_check(*({},), 1))

    def test_defect_ac1_field_list_extra_keyword(self):
        check_named_refusal(
            self, "ac1 field list",
            lambda: mod13.ac1_field_list(*(), extra_kw=1))

    def test_defect_ac1_field_list_extra_positional(self):
        check_named_refusal(
            self, "ac1 field list",
            lambda: mod13.ac1_field_list(*(), 1))

    def test_defect_aggregate_form_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "aggregate form validation failures",
            lambda: mod13.aggregate_form_validation_failures(*([],), extra_kw=1))

    def test_defect_aggregate_form_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "aggregate form validation failures",
            lambda: mod13.aggregate_form_validation_failures(*([],), 1))

    def test_defect_compare_registry_against_run_log_extra_keyword(self):
        check_named_refusal(
            self, "compare registry against run log",
            lambda: mod13.compare_registry_against_run_log(*({}, [], [], {}), extra_kw=1))

    def test_defect_compare_registry_against_run_log_extra_positional(self):
        check_named_refusal(
            self, "compare registry against run log",
            lambda: mod13.compare_registry_against_run_log(*({}, [], [], {}), 1))

    def test_defect_daily_aggregate_form_extra_keyword(self):
        check_named_refusal(
            self, "daily aggregate form",
            lambda: mod13.daily_aggregate_form(*(), extra_kw=1))

    def test_defect_daily_aggregate_form_extra_positional(self):
        check_named_refusal(
            self, "daily aggregate form",
            lambda: mod13.daily_aggregate_form(*(), 1))

    def test_defect_detection_comparison_points_extra_keyword(self):
        check_named_refusal(
            self, "detection comparison points",
            lambda: mod13.detection_comparison_points(*(), extra_kw=1))

    def test_defect_detection_comparison_points_extra_positional(self):
        check_named_refusal(
            self, "detection comparison points",
            lambda: mod13.detection_comparison_points(*(), 1))

    def test_defect_extend_history_extra_keyword(self):
        check_named_refusal(
            self, "extend history",
            lambda: mod13.extend_history(*([], []), extra_kw=1))

    def test_defect_extend_history_extra_positional(self):
        check_named_refusal(
            self, "extend history",
            lambda: mod13.extend_history(*([], []), 1))

    def test_defect_probe_claim_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "probe claim validation failures",
            lambda: mod13.probe_claim_validation_failures(*({},), extra_kw=1))

    def test_defect_probe_claim_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "probe claim validation failures",
            lambda: mod13.probe_claim_validation_failures(*({},), 1))

    def test_defect_probe_record_extra_keyword(self):
        check_named_refusal(
            self, "probe record",
            lambda: mod13.probe_record(*('headline scenario',), extra_kw=1))

    def test_defect_probe_record_extra_positional(self):
        check_named_refusal(
            self, "probe record",
            lambda: mod13.probe_record(*('headline scenario',), 1))

    def test_defect_publishable_on_replication_failures_extra_keyword(self):
        check_named_refusal(
            self, "publishable on replication failures",
            lambda: mod13.publishable_on_replication_failures(*({}, {}), extra_kw=1))

    def test_defect_publishable_on_replication_failures_extra_positional(self):
        check_named_refusal(
            self, "publishable on replication failures",
            lambda: mod13.publishable_on_replication_failures(*({}, {}), 1))

    def test_defect_replay_claim_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "replay claim validation failures",
            lambda: mod13.replay_claim_validation_failures(*({},), extra_kw=1))

    def test_defect_replay_claim_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "replay claim validation failures",
            lambda: mod13.replay_claim_validation_failures(*({},), 1))

    def test_defect_rerun_reading_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "rerun reading validation failures",
            lambda: mod13.rerun_reading_validation_failures(*({},), extra_kw=1))

    def test_defect_rerun_reading_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "rerun reading validation failures",
            lambda: mod13.rerun_reading_validation_failures(*({},), 1))

    def test_defect_resume_claim_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "resume claim validation failures",
            lambda: mod13.resume_claim_validation_failures(*({},), extra_kw=1))

    def test_defect_resume_claim_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "resume claim validation failures",
            lambda: mod13.resume_claim_validation_failures(*({},), 1))

    def test_defect_scoring_harness_position_extra_keyword(self):
        check_named_refusal(
            self, "scoring harness position",
            lambda: mod13.scoring_harness_position(*(), extra_kw=1))

    def test_defect_scoring_harness_position_extra_positional(self):
        check_named_refusal(
            self, "scoring harness position",
            lambda: mod13.scoring_harness_position(*(), 1))

    def test_defect_scoring_record_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "scoring record validation failures",
            lambda: mod13.scoring_record_validation_failures(*({},), extra_kw=1))

    def test_defect_scoring_record_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "scoring record validation failures",
            lambda: mod13.scoring_record_validation_failures(*({},), 1))

    def test_defect_use_stands_for_marked_run_extra_keyword(self):
        check_named_refusal(
            self, "use stands for marked run",
            lambda: mod13.use_stands_for_marked_run(*('witness', True, False), extra_kw=1))

    def test_defect_use_stands_for_marked_run_extra_positional(self):
        check_named_refusal(
            self, "use stands for marked run",
            lambda: mod13.use_stands_for_marked_run(*('witness', True, False), 1))

    def test_defect_validate_aggregate_form_extra_keyword(self):
        check_named_refusal(
            self, "validate aggregate form",
            lambda: mod13.validate_aggregate_form(*([],), extra_kw=1))

    def test_defect_validate_aggregate_form_extra_positional(self):
        check_named_refusal(
            self, "validate aggregate form",
            lambda: mod13.validate_aggregate_form(*([],), 1))

    def test_defect_validate_probe_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate probe claim",
            lambda: mod13.validate_probe_claim(*({},), extra_kw=1))

    def test_defect_validate_probe_claim_extra_positional(self):
        check_named_refusal(
            self, "validate probe claim",
            lambda: mod13.validate_probe_claim(*({},), 1))

    def test_defect_validate_rerun_reading_extra_keyword(self):
        check_named_refusal(
            self, "validate rerun reading",
            lambda: mod13.validate_rerun_reading(*({},), extra_kw=1))

    def test_defect_validate_rerun_reading_extra_positional(self):
        check_named_refusal(
            self, "validate rerun reading",
            lambda: mod13.validate_rerun_reading(*({},), 1))

    def test_defect_validate_resume_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate resume claim",
            lambda: mod13.validate_resume_claim(*({},), extra_kw=1))

    def test_defect_validate_resume_claim_extra_positional(self):
        check_named_refusal(
            self, "validate resume claim",
            lambda: mod13.validate_resume_claim(*({},), 1))

    def test_defect_validate_scoring_record_extra_keyword(self):
        check_named_refusal(
            self, "validate scoring record",
            lambda: mod13.validate_scoring_record(*({},), extra_kw=1))

    def test_defect_validate_scoring_record_extra_positional(self):
        check_named_refusal(
            self, "validate scoring record",
            lambda: mod13.validate_scoring_record(*({},), 1))

    def test_defect_validate_verdict_record_extra_keyword(self):
        check_named_refusal(
            self, "validate verdict record",
            lambda: mod13.validate_verdict_record(*({},), extra_kw=1))

    def test_defect_validate_verdict_record_extra_positional(self):
        check_named_refusal(
            self, "validate verdict record",
            lambda: mod13.validate_verdict_record(*({},), 1))

    def test_defect_verdict_record_extra_keyword(self):
        check_named_refusal(
            self, "verdict record",
            lambda: mod13.verdict_record(*('claim-1', 'exact replay alone', 'rests'), extra_kw=1))

    def test_defect_verdict_record_extra_positional(self):
        check_named_refusal(
            self, "verdict record",
            lambda: mod13.verdict_record(*('claim-1', 'exact replay alone', 'rests'), 1))

    def test_defect_verdict_record_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "verdict record validation failures",
            lambda: mod13.verdict_record_validation_failures(*({},), extra_kw=1))

    def test_defect_verdict_record_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "verdict record validation failures",
            lambda: mod13.verdict_record_validation_failures(*({},), 1))

    def test_defect_witness_rerun_extra_keyword(self):
        check_named_refusal(
            self, "witness rerun",
            lambda: mod13.witness_rerun(*({}, None), extra_kw=1))

    def test_defect_witness_rerun_extra_positional(self):
        check_named_refusal(
            self, "witness rerun",
            lambda: mod13.witness_rerun(*({}, None), 1))


class TestFW901Mod13StandingControls(unittest.TestCase):

    def test_standing_replay_check_extra_keyword(self):
        check_named_refusal(
            self, "replay check",
            lambda: mod13.replay_check({}, {}, extra_kw=1))

    def test_standing_replay_check_extra_positional(self):
        check_named_refusal(
            self, "replay check",
            lambda: mod13.replay_check({}, {}, 1))

    def test_standing_validate_replay_claim_extra_keyword(self):
        check_named_refusal(
            self, "validate replay claim",
            lambda: mod13.validate_replay_claim({}, extra_kw=1))

    def test_standing_validate_replay_claim_extra_positional(self):
        check_named_refusal(
            self, "validate replay claim",
            lambda: mod13.validate_replay_claim({}, 1))

    def test_standing_resume_check_extra_keyword(self):
        check_named_refusal(
            self, "resume check",
            lambda: mod13.resume_check({}, {}, extra_kw=1))

    def test_standing_resume_check_extra_positional(self):
        check_named_refusal(
            self, "resume check",
            lambda: mod13.resume_check({}, {}, 1))

    def test_standing_publishable_on_replication_extra_keyword(self):
        check_named_refusal(
            self, "publishable on replication",
            lambda: mod13.publishable_on_replication(
                {}, {}, extra_kw=1))

    def test_standing_publishable_on_replication_extra_positional(self):
        check_named_refusal(
            self, "publishable on replication",
            lambda: mod13.publishable_on_replication({}, {}, 1))

    def test_standing_score_detection_outputs_extra_keyword(self):
        check_named_refusal(
            self, "score detection outputs",
            lambda: mod13.score_detection_outputs([], extra_kw=1))

    def test_standing_score_detection_outputs_extra_positional(self):
        check_named_refusal(
            self, "score detection outputs",
            lambda: mod13.score_detection_outputs(
                [], "a", "k", "r", 1))


class TestFW901Mod13ServedControls(unittest.TestCase):

    def test_control_ac1_field_list_served(self):
        result = mod13.ac1_field_list()
        self.assertIsInstance(result, list)
        self.assertTrue(result)

    def test_control_daily_aggregate_form_served(self):
        self.assertEqual(
            mod13.daily_aggregate_form()[0], "run_id")

    def test_control_detection_comparison_points_served(self):
        self.assertEqual(
            len(mod13.detection_comparison_points()), 2)

    def test_control_validate_probe_claim_served(self):
        self.assertIs(mod13.validate_probe_claim({}), True)

    def test_control_validate_replay_claim_served(self):
        self.assertIs(mod13.validate_replay_claim({}), True)

    def test_control_publishable_on_replication_plain(self):
        self.assertIs(
            mod13.publishable_on_replication({}, {}), False)

    def test_control_replay_check_served(self):
        result = mod13.replay_check({}, {})
        self.assertIsInstance(result, dict)
        self.assertIn("field_list", result)

    def test_control_score_detection_outputs_served(self):
        result = mod13.score_detection_outputs(
            [], authored_by="a", knowledge="k",
            records_position="r")
        self.assertEqual(result["outputs_scored"], 0)


if __name__ == "__main__":
    unittest.main()

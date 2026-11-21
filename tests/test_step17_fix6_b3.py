"""Step 17 fix wave 6, Slice 3 defect tests (FW6-03, T17R5-04).

The too few and too many arguments family at doors outside the
FW5-10 named set: each act named in the filings, called with no
arguments, and at the three too many doors called with more
arguments than its form takes, must refuse in the named form of
its module, stating the door, the ground, and the next step,
instead of escaping as a bare interpreter TypeError.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01, mod02, mod05, mod06, mod08, mod09
from crucible import mod10, mod11, mod13


BARE_PHRASES = (
    "required positional argument",
    "positional arguments but",
    "takes from",
)


def check_named_refusal(case, exc_type, door_words, call,
                        ground_word="missing"):
    """The call refuses in named form: the module named type,
    never a bare TypeError, the message carrying the door, the
    ground word, a next step, and no bare interpreter phrase."""
    with case.assertRaises(exc_type) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    for word in door_words:
        case.assertIn(word, message)
    case.assertIn(ground_word, message)
    case.assertIn("next step", message)
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW603Mod01(unittest.TestCase):

    def test_defect_record_validation_failures_no_args(self):
        check_named_refusal(
            self, ValueError, ("record_validation_failures",),
            lambda: mod01.record_validation_failures())

    def test_defect_validate_family_seal_match_no_args(self):
        check_named_refusal(
            self, ValueError, ("validate_family_seal_match",),
            lambda: mod01.validate_family_seal_match())

    def test_defect_family_reportable_standing_no_args(self):
        check_named_refusal(
            self, ValueError, ("family_reportable_standing",),
            lambda: mod01.family_reportable_standing())

    def test_defect_brief_shape_for_form_no_args(self):
        check_named_refusal(
            self, ValueError, ("brief_shape_for_form",),
            lambda: mod01.brief_shape_for_form())

    def test_defect_form_ids_for_brief_shape_no_args(self):
        check_named_refusal(
            self, ValueError, ("form_ids_for_brief_shape",),
            lambda: mod01.form_ids_for_brief_shape())

    def test_control_brief_shape_for_form_served(self):
        self.assertEqual(mod01.brief_shape_for_form("9"), "8")

    def test_control_form_ids_for_brief_shape_served(self):
        self.assertEqual(
            mod01.form_ids_for_brief_shape("8"), ("8", "9"))

    def test_control_validate_family_seal_match_false(self):
        self.assertIs(
            mod01.validate_family_seal_match(None, None), False)

    def test_control_family_reportable_standing_none(self):
        standing = mod01.family_reportable_standing(None)
        self.assertIs(standing["reportable_ready"], False)


class TestFW603Mod02(unittest.TestCase):

    def test_defect_encode_candidate_input_no_args(self):
        check_named_refusal(
            self, ValueError, ("encode_candidate_input",),
            lambda: mod02.encode_candidate_input())

    def test_control_encode_candidate_input_empty(self):
        self.assertEqual(mod02.encode_candidate_input({}), "")

    def test_control_encode_candidate_input_served(self):
        self.assertEqual(
            mod02.encode_candidate_input({"a": "1"}), "str:1:a=1:1")


class TestFW603Mod05(unittest.TestCase):

    def test_defect_gate_passing_share_no_args(self):
        check_named_refusal(
            self, ValueError, ("gate_passing_share",),
            lambda: mod05.gate_passing_share())

    def test_defect_gate_passing_share_too_many_args(self):
        check_named_refusal(
            self, ValueError, ("gate_passing_share",),
            lambda: mod05.gate_passing_share(1, 1, "e", "x", "y"),
            ground_word="beyond")

    def test_defect_vouch_no_args(self):
        check_named_refusal(
            self, ValueError, ("vouch",),
            lambda: mod05.vouch())

    def test_defect_eligibility_no_args(self):
        check_named_refusal(
            self, ValueError, ("eligibility",),
            lambda: mod05.eligibility())

    def test_defect_aggregate_reputation_no_args(self):
        check_named_refusal(
            self, ValueError, ("aggregate_reputation",),
            lambda: mod05.aggregate_reputation())

    def test_defect_share_for_epoch_no_args(self):
        check_named_refusal(
            self, ValueError, ("share_for_epoch",),
            lambda: mod05.share_for_epoch())

    def test_defect_compute_share_no_args(self):
        check_named_refusal(
            self, ValueError, ("compute_share",),
            lambda: mod05.compute_share())

    def test_defect_recompute_share_no_args(self):
        check_named_refusal(
            self, ValueError, ("recompute_share",),
            lambda: mod05.recompute_share())

    def test_defect_recompute_share_too_many_args(self):
        check_named_refusal(
            self, ValueError, ("recompute_share",),
            lambda: mod05.recompute_share({}, {}, {}, {}),
            ground_word="beyond")

    def test_control_gate_passing_share_served(self):
        share = mod05.gate_passing_share(2, 1)
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_control_compute_share_served(self):
        share = mod05.compute_share(2, 1)
        self.assertEqual(share["numerator"], 1)

    def test_control_share_for_epoch_unknown_standing(self):
        self.assertIs(
            mod05.share_for_epoch("epoch-1"), mod05.UNKNOWN_SHARE)

    def test_control_recompute_share_served(self):
        result = mod05.recompute_share({}, {})
        self.assertEqual(result["divergence_count"], 0)

    def test_control_vouch_served(self):
        edge = mod05.vouch("agent-a", "agent-b", 3)
        self.assertEqual(edge["stake"], 3)


class TestFW603Mod06(unittest.TestCase):

    def test_defect_escrow_contract_state_no_args(self):
        check_named_refusal(
            self, ValueError, ("escrow_contract_state",),
            lambda: mod06.escrow_contract_state())

    def test_defect_run_instruction_no_args(self):
        check_named_refusal(
            self, ValueError, ("run_instruction",),
            lambda: mod06.run_instruction())

    def test_control_escrow_contract_state_served(self):
        state = mod06.escrow_contract_state("contract-1")
        self.assertEqual(state["contract_identifier"], "contract-1")

    def test_control_escrow_result_served(self):
        result = mod06.escrow_result("screening")
        self.assertEqual(result["kind"], "screening")


class TestFW603Mod08(unittest.TestCase):

    def test_defect_accept_detection_input_no_args(self):
        check_named_refusal(
            self, mod08.NamedDetectionFailure,
            ("accept_detection_input",),
            lambda: mod08.accept_detection_input())

    def test_defect_score_day_no_args(self):
        check_named_refusal(
            self, mod08.NamedDetectionFailure, ("score_day",),
            lambda: mod08.score_day())

    def test_control_score_none_refusal_standing(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score(None)

    def test_control_accept_detection_input_empty_refusal(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input({})


class TestFW603Mod09(unittest.TestCase):

    def test_defect_make_strategy_no_args(self):
        check_named_refusal(
            self, mod09.NamedAttackerFailure, ("make_strategy",),
            lambda: mod09.make_strategy())

    def test_control_make_strategy_served(self):
        strategy = mod09.make_strategy("strategy-1")
        self.assertIsInstance(strategy, dict)
        self.assertTrue(strategy)


class TestFW603Mod10(unittest.TestCase):

    def test_defect_validate_daily_aggregates_no_args(self):
        check_named_refusal(
            self, ValueError, ("validate_daily_aggregates",),
            lambda: mod10.validate_daily_aggregates())

    def test_defect_retain_daily_aggregate_deliveries_no_args(self):
        check_named_refusal(
            self, ValueError,
            ("retain_daily_aggregate_deliveries",),
            lambda: mod10.retain_daily_aggregate_deliveries())

    def test_defect_retain_checkpoint_no_args(self):
        check_named_refusal(
            self, ValueError, ("retain_checkpoint",),
            lambda: mod10.retain_checkpoint())

    def test_defect_retain_daily_snapshot_no_args(self):
        check_named_refusal(
            self, ValueError, ("retain_daily_snapshot",),
            lambda: mod10.retain_daily_snapshot())

    def test_control_validate_daily_aggregates_empty(self):
        self.assertIs(mod10.validate_daily_aggregates([]), False)

    def test_control_retain_checkpoint_identity_less(self):
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint({})

    def test_control_retain_daily_snapshot_identity_less(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_snapshot({})


class TestFW603Mod11(unittest.TestCase):

    def test_defect_retirement_verdicts_no_args(self):
        check_named_refusal(
            self, ValueError, ("retirement_verdicts",),
            lambda: mod11.retirement_verdicts())

    def test_defect_retirement_tally_no_args(self):
        check_named_refusal(
            self, ValueError, ("retirement_tally",),
            lambda: mod11.retirement_tally())

    def test_defect_quote_headline_unit_no_args(self):
        check_named_refusal(
            self, ValueError, ("quote_headline_unit",),
            lambda: mod11.quote_headline_unit())

    def test_control_retirement_verdicts_served(self):
        verdicts = mod11.retirement_verdicts("F-01")
        self.assertIsInstance(verdicts, dict)
        self.assertTrue(verdicts)

    def test_control_make_headline_unit_empty_refusal(self):
        with self.assertRaises(ValueError):
            mod11.make_headline_unit({})


class TestFW603Mod13(unittest.TestCase):

    def test_defect_score_detection_outputs_no_args(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("score", "outputs"),
            lambda: mod13.score_detection_outputs())

    def test_defect_validate_replay_claim_no_args(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure,
            ("validate replay claim",),
            lambda: mod13.validate_replay_claim())

    def test_defect_replay_check_too_many_args(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("replay check",),
            lambda: mod13.replay_check({}, {}, {}, {}),
            ground_word="beyond")

    def test_control_replay_check_served(self):
        result = mod13.replay_check({}, {})
        self.assertIsInstance(result, dict)
        self.assertIn("deterministic", result)

    def test_control_validate_replay_claim_empty(self):
        self.assertIs(mod13.validate_replay_claim({}), True)

    def test_control_score_detection_outputs_refusal(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.score_detection_outputs([])


if __name__ == "__main__":
    unittest.main()

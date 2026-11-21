"""Step 17 fix wave 7, Slice 1 defect tests (FW7-01, T17R6-01
with T17R6-09).

The too many arguments family in keyword form: at each act
named in the Green 3 filing G3-R6-01, the act handed its
ordinary valid arguments plus one extra keyword argument named
extra with value 1 must refuse in the named form of its module,
stating the door, the ground, and the next step, instead of
escaping as a bare interpreter TypeError. The two folded mod02
handings of T17R6-09 stand beside them: encode_candidate_input
handed two positional arguments and initial_stream_state handed
three positional arguments must refuse in the same named form
instead of meeting the bare interpreter TypeError signature
sentence.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod02, mod05, mod06, mod08, mod09
from crucible import mod11, mod13


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, exc_type, door_words, call,
                        ground_word="beyond"):
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


class TestFW701Mod02Keyword(unittest.TestCase):

    def test_defect_encode_candidate_input_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("encode_candidate_input",),
            lambda: mod02.encode_candidate_input({5: "v"}, extra=1))

    def test_defect_encode_candidate_input_extra_positional(self):
        check_named_refusal(
            self, ValueError, ("encode_candidate_input",),
            lambda: mod02.encode_candidate_input({5: "v"}, 1))

    def test_defect_initial_stream_state_extra_positional(self):
        check_named_refusal(
            self, ValueError, ("initial_stream_state",),
            lambda: mod02.initial_stream_state("s", 0, 1))

    def test_control_encode_candidate_input_served(self):
        self.assertEqual(
            mod02.encode_candidate_input({"a": "1"}), "str:1:a=1:1")

    def test_control_initial_stream_state_served(self):
        state = mod02.initial_stream_state("alpha", carried_positions=0)
        self.assertEqual(state["position"], 0)
        self.assertEqual(state["stream_class"], "alpha")


class TestFW701Mod05Keyword(unittest.TestCase):

    def test_defect_gate_passing_share_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("gate_passing_share",),
            lambda: mod05.gate_passing_share(2, 1, epoch="e1", extra=1))

    def test_defect_recompute_share_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("recompute_share",),
            lambda: mod05.recompute_share({"e1": 1}, {"e1": 1}, extra=1))

    def test_defect_compute_share_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("compute_share",),
            lambda: mod05.compute_share(2, 1, extra=1))

    def test_defect_vouch_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("vouch",),
            lambda: mod05.vouch("a", "b", extra=1))

    def test_control_gate_passing_share_served(self):
        share = mod05.gate_passing_share(2, 1)
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_control_compute_share_served(self):
        share = mod05.compute_share(2, 1)
        self.assertEqual(share["numerator"], 1)

    def test_control_recompute_share_served(self):
        result = mod05.recompute_share({}, {})
        self.assertEqual(result["divergence_count"], 0)

    def test_control_vouch_served(self):
        edge = mod05.vouch("agent-a", "agent-b", 3)
        self.assertEqual(edge["stake"], 3)


class TestFW701Mod06Keyword(unittest.TestCase):

    def test_defect_escrow_contract_state_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("escrow_contract_state",),
            lambda: mod06.escrow_contract_state({}, extra=1))

    def test_defect_run_instruction_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("run_instruction",),
            lambda: mod06.run_instruction({}, extra=1))

    def test_control_escrow_contract_state_served(self):
        state = mod06.escrow_contract_state("contract-1")
        self.assertEqual(state["contract_identifier"], "contract-1")


class TestFW701Mod08Keyword(unittest.TestCase):

    def test_defect_accept_detection_input_extra_keyword(self):
        check_named_refusal(
            self, mod08.NamedDetectionFailure,
            ("accept_detection_input",),
            lambda: mod08.accept_detection_input({}, extra=1))

    def test_defect_score_day_extra_keyword(self):
        check_named_refusal(
            self, mod08.NamedDetectionFailure, ("score_day",),
            lambda: mod08.score_day({}, extra=1))


class TestFW701Mod09Keyword(unittest.TestCase):

    def test_defect_make_strategy_extra_keyword(self):
        check_named_refusal(
            self, mod09.NamedAttackerFailure, ("make_strategy",),
            lambda: mod09.make_strategy({}, extra=1))

    def test_control_make_strategy_served(self):
        strategy = mod09.make_strategy("strategy-1")
        self.assertIsInstance(strategy, dict)
        self.assertTrue(strategy)


class TestFW701Mod11Keyword(unittest.TestCase):

    def test_defect_retirement_verdicts_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("retirement_verdicts",),
            lambda: mod11.retirement_verdicts({}, extra=1))

    def test_defect_retirement_tally_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("retirement_tally",),
            lambda: mod11.retirement_tally({}, extra=1))

    def test_defect_quote_headline_unit_extra_keyword(self):
        check_named_refusal(
            self, ValueError, ("quote_headline_unit",),
            lambda: mod11.quote_headline_unit({}, extra=1))

    def test_control_retirement_verdicts_served(self):
        verdicts = mod11.retirement_verdicts("F-01")
        self.assertIsInstance(verdicts, dict)
        self.assertTrue(verdicts)


class TestFW701Mod13Keyword(unittest.TestCase):

    def test_defect_replay_check_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("replay check",),
            lambda: mod13.replay_check({}, {}, extra=1))

    def test_defect_score_detection_outputs_extra_keyword(self):
        check_named_refusal(
            self, mod13.NamedReplicationFailure, ("score", "outputs"),
            lambda: mod13.score_detection_outputs({}, extra=1))

    def test_control_replay_check_served(self):
        result = mod13.replay_check({}, {})
        self.assertIsInstance(result, dict)
        self.assertIn("deterministic", result)


if __name__ == "__main__":
    unittest.main()

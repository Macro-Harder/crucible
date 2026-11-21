"""Step 17 fix wave 9, Builder 1 defect tests (FW9-02, Medium,
ruling T17R8-02, Slice 1, mod05 and mod09).

The argument count family: at each of the four doors named in
the Blue 5 filing B5-R8-01, an extra argument handing, in
keyword form and in positional form, must stand refused in the
named form of its module, stating the door, the ground, and
the next step, in the FW8-01 cure form, instead of escaping as
a bare interpreter TypeError. The filed bare sentence lengths
stand at 65 and 75 characters at proportion_record, 59 and 69
at work_credit, 68 and 78 at aggregate_reputation, and 63 and
73 at attacker_payoff, in keyword and positional form.
Outcomes stand judged by stored value in code, never by a
repr of a returned value (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod05 as mod05
import crucible.mod09 as mod09


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, exc_type, door_word, call):
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


def valid_inputs():
    return {
        "agent_identifier": "a", "accepted_work": 5,
        "vouches_received": [
            {"stake": 3, "score_bearing_flag": True}],
        "penalties": 1}


class TestFW902Mod05Charged(unittest.TestCase):

    def test_defect_proportion_record_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "proportion_record",
            lambda: mod05.proportion_record(1, 2, extra_kw=1))

    def test_defect_proportion_record_extra_positional(self):
        check_named_refusal(
            self, ValueError, "proportion_record",
            lambda: mod05.proportion_record(1, 2, 1))

    def test_defect_work_credit_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "work_credit",
            lambda: mod05.work_credit([], extra_kw=1))

    def test_defect_work_credit_extra_positional(self):
        check_named_refusal(
            self, ValueError, "work_credit",
            lambda: mod05.work_credit([], 1))

    def test_defect_aggregate_reputation_extra_keyword(self):
        check_named_refusal(
            self, ValueError, "aggregate_reputation",
            lambda: mod05.aggregate_reputation(
                valid_inputs(), extra_kw=1))

    def test_defect_aggregate_reputation_extra_positional(self):
        check_named_refusal(
            self, ValueError, "aggregate_reputation",
            lambda: mod05.aggregate_reputation(valid_inputs(), 1))


class TestFW902Mod09Charged(unittest.TestCase):

    def test_defect_attacker_payoff_extra_keyword(self):
        check_named_refusal(
            self, mod09.NamedAttackerFailure, "attacker_payoff",
            lambda: mod09.attacker_payoff(
                {"in_protocol_payoff": 3}, 4, extra_kw=1))

    def test_defect_attacker_payoff_extra_positional(self):
        check_named_refusal(
            self, mod09.NamedAttackerFailure, "attacker_payoff",
            lambda: mod09.attacker_payoff(
                {"in_protocol_payoff": 3}, 4, 1))


class TestFW902Controls(unittest.TestCase):

    def test_control_proportion_record_served(self):
        self.assertEqual(
            mod05.proportion_record(1, 2),
            {"numerator": 1, "denominator": 2})

    def test_control_work_credit_served(self):
        result = mod05.work_credit(
            [{"agent_identifier": "a", "accepted": True}])
        self.assertEqual(result["totals"]["submitted"], 1)
        self.assertEqual(result["totals"]["accepted"], 1)
        self.assertEqual(result["events_used"], 1)

    def test_control_aggregate_reputation_served(self):
        result = mod05.aggregate_reputation(valid_inputs())
        self.assertEqual(result["score"], 7)

    def test_control_attacker_payoff_served(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 3}, 4), 7)

    def test_control_proportion_record_missing_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.proportion_record()
        self.assertIn("proportion_record", str(caught.exception))
        self.assertIn("next step", str(caught.exception).lower())

    def test_control_work_credit_missing_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit()
        self.assertIn("work_credit", str(caught.exception))
        self.assertIn("next step", str(caught.exception).lower())

    def test_control_aggregate_reputation_missing_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.aggregate_reputation()
        self.assertIn(
            "aggregate_reputation", str(caught.exception))
        self.assertIn("next step", str(caught.exception).lower())

    def test_control_attacker_payoff_missing_named(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff()
        self.assertIn("missing", str(caught.exception))
        self.assertNotIsInstance(caught.exception, TypeError)

    def test_control_recompute_share_extra_keyword_named(self):
        check_named_refusal(
            self, ValueError, "recompute_share",
            lambda: mod05.recompute_share(
                {"e1": 1}, {"e1": 1}, extra=1))

    def test_control_recompute_share_extra_positional_named(self):
        check_named_refusal(
            self, ValueError, "recompute_share",
            lambda: mod05.recompute_share({"e1": 1}, {"e1": 1}, 1))

    def test_control_gate_passing_share_extra_keyword_named(self):
        check_named_refusal(
            self, ValueError, "gate_passing_share",
            lambda: mod05.gate_passing_share(
                2, 1, epoch="e1", extra=1))

    def test_control_make_strategy_extra_keyword_named(self):
        check_named_refusal(
            self, mod09.NamedAttackerFailure, "make_strategy",
            lambda: mod09.make_strategy("strategy-1", extra=1))


if __name__ == "__main__":
    unittest.main()

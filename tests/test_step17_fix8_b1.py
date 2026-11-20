"""Step 17 fix wave 8, Slice 1 defect tests (FW8-01, T17R7-02).

The extra argument family in keyword form and in positional
form: at each door named in the slice, the door handed its
ordinary valid arguments plus one extra argument must refuse
in the named form of its module, stating the door, the ground,
and the next step, instead of escaping as a bare interpreter
TypeError. The family doors of the same signature in mod06 and
mod11, the sentinel doors carrying a named missing handing
refusal or an extra keyword guard, stand read in the same
form: doors found escaping stand cured here, and doors already
refusing the keyword form in named form stand as controls for
that form with their positional form cured.

Judgement stands by stored value in code: the exception type
and the stored message text, never by a repr (T17R3-23).

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod06, mod11


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, door_word, call):
    """The call refuses in named form: ValueError, never a bare
    TypeError, the message carrying the door, the beyond ground,
    a next step, and no bare interpreter phrase."""
    with case.assertRaises(ValueError) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message)
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW801Mod06Charged(unittest.TestCase):

    def test_defect_escrow_result_extra_keyword(self):
        check_named_refusal(
            self, "escrow_result",
            lambda: mod06.escrow_result("completed", extra_kw=1))

    def test_defect_escrow_result_extra_positional(self):
        check_named_refusal(
            self, "escrow_result",
            lambda: mod06.escrow_result(
                "completed", "B-4", None, None, 1))

    def test_control_escrow_result_served(self):
        result = mod06.escrow_result("completed")
        self.assertEqual(result["kind"], "completed")


class TestFW801Mod11Charged(unittest.TestCase):

    def test_defect_make_headline_unit_extra_keyword(self):
        check_named_refusal(
            self, "make_headline_unit",
            lambda: mod11.make_headline_unit({}, extra_kw=1))

    def test_defect_make_headline_unit_extra_positional(self):
        check_named_refusal(
            self, "make_headline_unit",
            lambda: mod11.make_headline_unit({}, 1))

    def test_defect_honest_loss_rate_h1_extra_keyword(self):
        check_named_refusal(
            self, "honest_loss_rate_h1",
            lambda: mod11.honest_loss_rate_h1(10, 5, extra=1))

    def test_defect_honest_loss_rate_h1_extra_positional(self):
        check_named_refusal(
            self, "honest_loss_rate_h1",
            lambda: mod11.honest_loss_rate_h1(10, 5, 1))

    def test_defect_classify_run_outcome_extra_keyword(self):
        check_named_refusal(
            self, "classify_run_outcome",
            lambda: mod11.classify_run_outcome(30, "x", extra=1))

    def test_defect_classify_run_outcome_extra_positional(self):
        check_named_refusal(
            self, "classify_run_outcome",
            lambda: mod11.classify_run_outcome(30, "x", 1))

    def test_defect_retirement_verdicts_extra_positional(self):
        check_named_refusal(
            self, "retirement_verdicts",
            lambda: mod11.retirement_verdicts("F-01", 1))

    def test_control_retirement_verdicts_extra_keyword(self):
        check_named_refusal(
            self, "retirement_verdicts",
            lambda: mod11.retirement_verdicts("F-01", extra=1))

    def test_defect_retirement_tally_extra_positional(self):
        check_named_refusal(
            self, "retirement_tally",
            lambda: mod11.retirement_tally("F-01", 1))

    def test_control_retirement_tally_extra_keyword(self):
        check_named_refusal(
            self, "retirement_tally",
            lambda: mod11.retirement_tally("F-01", extra=1))

    def test_defect_quote_headline_unit_extra_positional(self):
        check_named_refusal(
            self, "quote_headline_unit",
            lambda: mod11.quote_headline_unit({}, 1))

    def test_control_quote_headline_unit_extra_keyword(self):
        check_named_refusal(
            self, "quote_headline_unit",
            lambda: mod11.quote_headline_unit({}, extra=1))

    def test_defect_weekly_count_extra_keyword(self):
        check_named_refusal(
            self, "weekly_count",
            lambda: mod11.weekly_count([], 1, extra_kw=1))

    def test_defect_weekly_count_extra_positional(self):
        check_named_refusal(
            self, "weekly_count",
            lambda: mod11.weekly_count([], 1, 1))

    def test_control_honest_loss_rate_h1_served(self):
        rate = mod11.honest_loss_rate_h1(10, 5)
        self.assertEqual(rate["numerator"], 5)
        self.assertEqual(rate["denominator"], 10)

    def test_control_classify_run_outcome_served(self):
        outcome = mod11.classify_run_outcome(30, "attacker_winning")
        self.assertEqual(outcome["outcome"], "attacker_winning")

    def test_control_retirement_verdicts_served(self):
        verdicts = mod11.retirement_verdicts("F-01")
        self.assertIsInstance(verdicts, dict)
        self.assertTrue(verdicts)


class TestFW801FamilyMod06(unittest.TestCase):

    def test_defect_escrow_contract_state_extra_positional(self):
        check_named_refusal(
            self, "escrow_contract_state",
            lambda: mod06.escrow_contract_state(
                "contract-1", "B-4", "no lien in force", None,
                False, None, None, None, None, None, 1))

    def test_control_escrow_contract_state_extra_keyword(self):
        check_named_refusal(
            self, "escrow_contract_state",
            lambda: mod06.escrow_contract_state(
                "contract-1", extra=1))

    def test_defect_run_instruction_extra_positional(self):
        check_named_refusal(
            self, "run_instruction",
            lambda: mod06.run_instruction("case-1", "B-4", None, 1))

    def test_control_run_instruction_extra_keyword(self):
        check_named_refusal(
            self, "run_instruction",
            lambda: mod06.run_instruction("case-1", extra=1))

    def test_defect_enter_ruling_extra_keyword(self):
        check_named_refusal(
            self, "enter_ruling",
            lambda: mod06.enter_ruling([], "DQ-5", "text", extra=1))

    def test_defect_enter_ruling_extra_positional(self):
        check_named_refusal(
            self, "enter_ruling",
            lambda: mod06.enter_ruling([], "DQ-5", "text", 1))


class TestFW801FamilyMod11(unittest.TestCase):

    def test_defect_judge_registry_entry_extra_keyword(self):
        check_named_refusal(
            self, "judge_registry_entry",
            lambda: mod11.judge_registry_entry(
                {}, "compiler-a", "checker-b", extra=1))

    def test_defect_judge_registry_entry_extra_positional(self):
        check_named_refusal(
            self, "judge_registry_entry",
            lambda: mod11.judge_registry_entry(
                {}, "compiler-a", "checker-b", None, 1))

    def test_defect_build_headline_unit_from_run_extra_keyword(self):
        check_named_refusal(
            self, "build_headline_unit_from_run",
            lambda: mod11.build_headline_unit_from_run(
                "run-1", {}, extra=1))

    def test_defect_build_headline_unit_from_run_extra_positional(self):
        check_named_refusal(
            self, "build_headline_unit_from_run",
            lambda: mod11.build_headline_unit_from_run(
                "run-1", {}, "sweep", None, 1))

    def test_defect_claim_enters_family_extra_keyword(self):
        check_named_refusal(
            self, "claim_enters_family",
            lambda: mod11.claim_enters_family(
                {}, "claim-1", False, extra=1))

    def test_defect_claim_enters_family_extra_positional(self):
        check_named_refusal(
            self, "claim_enters_family",
            lambda: mod11.claim_enters_family(
                {}, "claim-1", False, 1))


if __name__ == "__main__":
    unittest.main()

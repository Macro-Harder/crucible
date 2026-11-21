"""Step 17 fix wave 10, Builder 2 defect tests (FW10-01, Medium,
ruling T17R9-01, Slice 2, mod09).

The whole module enumeration family: at each of the 19 doors
named in the slice, an extra argument handing past the full
signature, in keyword form and in positional form, must stand
refused in the named form of its module, a NamedAttackerFailure
stating the door, the beyond ground, and the next step, in the
FW8-01 cure form as the cured door attacker_payoff of this
module carries it, instead of escaping as a bare interpreter
TypeError. At search, the cured form holds in both handing
forms on the charge reading of its variadic shape: the keyword
handing refused in the full named form, and the positional
handing answered in the full named form. Outcomes stand judged
by stored value in code, never by a repr of a returned value.

Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible.mod09 as mod09


BARE_PHRASES = (
    "unexpected keyword argument",
    "positional arguments but",
    "required positional argument",
    "takes from",
    "got an unexpected",
)


def check_named_refusal(case, door_word, call):
    with case.assertRaises(mod09.NamedAttackerFailure) as caught:
        call()
    case.assertNotIsInstance(caught.exception, TypeError)
    message = str(caught.exception)
    case.assertIn(door_word, message)
    case.assertIn("beyond", message)
    case.assertIn("next step", message.lower())
    for phrase in BARE_PHRASES:
        case.assertNotIn(phrase, message)
    return message


class TestFW1001Mod09Charged(unittest.TestCase):

    def test_defect_attacker_cost_summary_extra_keyword(self):
        check_named_refusal(
            self, "attacker_cost_summary",
            lambda: mod09.attacker_cost_summary(*(None,), extra_kw=1))

    def test_defect_attacker_cost_summary_extra_positional(self):
        check_named_refusal(
            self, "attacker_cost_summary",
            lambda: mod09.attacker_cost_summary(*(None,), 1))

    def test_defect_bond_search_extra_keyword(self):
        check_named_refusal(
            self, "bond_search",
            lambda: mod09.bond_search(*(None, None), extra_kw=1))

    def test_defect_bond_search_extra_positional(self):
        check_named_refusal(
            self, "bond_search",
            lambda: mod09.bond_search(*(None, None), 1))

    def test_defect_build_search_record_extra_keyword(self):
        check_named_refusal(
            self, "build_search_record",
            lambda: mod09.build_search_record(*(None, None, None, None, None, None, None, None, None, None, None, None, None), extra_kw=1))

    def test_defect_build_search_record_extra_positional(self):
        check_named_refusal(
            self, "build_search_record",
            lambda: mod09.build_search_record(*(None, None, None, None, None, None, None, None, None, None, None, None, None), 1))

    def test_defect_catalogue_gaps_extra_keyword(self):
        check_named_refusal(
            self, "catalogue_gaps",
            lambda: mod09.catalogue_gaps(*(), extra_kw=1))

    def test_defect_catalogue_gaps_extra_positional(self):
        check_named_refusal(
            self, "catalogue_gaps",
            lambda: mod09.catalogue_gaps(*(), 1))

    def test_defect_conditional_briber_strategy_extra_keyword(self):
        check_named_refusal(
            self, "conditional_briber_strategy",
            lambda: mod09.conditional_briber_strategy(*(None, None), extra_kw=1))

    def test_defect_conditional_briber_strategy_extra_positional(self):
        check_named_refusal(
            self, "conditional_briber_strategy",
            lambda: mod09.conditional_briber_strategy(*(None, None), 1))

    def test_defect_mod03_catalogue_record_extra_keyword(self):
        check_named_refusal(
            self, "mod03_catalogue_record",
            lambda: mod09.mod03_catalogue_record(*(None,), extra_kw=1))

    def test_defect_mod03_catalogue_record_extra_positional(self):
        check_named_refusal(
            self, "mod03_catalogue_record",
            lambda: mod09.mod03_catalogue_record(*(None,), 1))

    def test_defect_readout_extra_keyword(self):
        check_named_refusal(
            self, "readout",
            lambda: mod09.readout(*(None, None, None, None), extra_kw=1))

    def test_defect_readout_extra_positional(self):
        check_named_refusal(
            self, "readout",
            lambda: mod09.readout(*(None, None, None, None), 1))

    def test_defect_run_record_carriage_extra_keyword(self):
        check_named_refusal(
            self, "run_record_carriage",
            lambda: mod09.run_record_carriage(*(None, None, None, None, None, None), extra_kw=1))

    def test_defect_run_record_carriage_extra_positional(self):
        check_named_refusal(
            self, "run_record_carriage",
            lambda: mod09.run_record_carriage(*(None, None, None, None, None, None), 1))

    def test_defect_run_search_extra_keyword(self):
        check_named_refusal(
            self, "run_search",
            lambda: mod09.run_search(*(None, None, None, None), extra_kw=1))

    def test_defect_run_search_extra_positional(self):
        check_named_refusal(
            self, "run_search",
            lambda: mod09.run_search(*(None, None, None, None), 1))

    def test_defect_search_record_covers_hostile_kinds_extra_keyword(self):
        check_named_refusal(
            self, "search_record_covers_hostile_kinds",
            lambda: mod09.search_record_covers_hostile_kinds(*(None, None), extra_kw=1))

    def test_defect_search_record_covers_hostile_kinds_extra_positional(self):
        check_named_refusal(
            self, "search_record_covers_hostile_kinds",
            lambda: mod09.search_record_covers_hostile_kinds(*(None, None), 1))

    def test_defect_search_record_validation_failures_extra_keyword(self):
        check_named_refusal(
            self, "search_record_validation_failures",
            lambda: mod09.search_record_validation_failures(*(None, None), extra_kw=1))

    def test_defect_search_record_validation_failures_extra_positional(self):
        check_named_refusal(
            self, "search_record_validation_failures",
            lambda: mod09.search_record_validation_failures(*(None, None), 1))

    def test_defect_stopping_rule_state_extra_keyword(self):
        check_named_refusal(
            self, "stopping_rule_state",
            lambda: mod09.stopping_rule_state(*(None,), extra_kw=1))

    def test_defect_stopping_rule_state_extra_positional(self):
        check_named_refusal(
            self, "stopping_rule_state",
            lambda: mod09.stopping_rule_state(*(None,), 1))

    def test_defect_strategy_catalogue_extra_keyword(self):
        check_named_refusal(
            self, "strategy_catalogue",
            lambda: mod09.strategy_catalogue(*(None,), extra_kw=1))

    def test_defect_strategy_catalogue_extra_positional(self):
        check_named_refusal(
            self, "strategy_catalogue",
            lambda: mod09.strategy_catalogue(*(None,), 1))

    def test_defect_sweep_external_profit_extra_keyword(self):
        check_named_refusal(
            self, "sweep_external_profit",
            lambda: mod09.sweep_external_profit(*(None, None), extra_kw=1))

    def test_defect_sweep_external_profit_extra_positional(self):
        check_named_refusal(
            self, "sweep_external_profit",
            lambda: mod09.sweep_external_profit(*(None, None), 1))

    def test_defect_validate_search_record_extra_keyword(self):
        check_named_refusal(
            self, "validate_search_record",
            lambda: mod09.validate_search_record(*(None, None), extra_kw=1))

    def test_defect_validate_search_record_extra_positional(self):
        check_named_refusal(
            self, "validate_search_record",
            lambda: mod09.validate_search_record(*(None, None), 1))

    def test_defect_validate_search_record_with_reason_extra_keyword(self):
        check_named_refusal(
            self, "validate_search_record_with_reason",
            lambda: mod09.validate_search_record_with_reason(*(None, None), extra_kw=1))

    def test_defect_validate_search_record_with_reason_extra_positional(self):
        check_named_refusal(
            self, "validate_search_record_with_reason",
            lambda: mod09.validate_search_record_with_reason(*(None, None), 1))

    def test_defect_witness_carriage_extra_keyword(self):
        check_named_refusal(
            self, "witness_carriage",
            lambda: mod09.witness_carriage(*(None, None), extra_kw=1))

    def test_defect_witness_carriage_extra_positional(self):
        check_named_refusal(
            self, "witness_carriage",
            lambda: mod09.witness_carriage(*(None, None), 1))

    def test_defect_make_strategy_extra_keyword(self):
        check_named_refusal(
            self, "make_strategy",
            lambda: mod09.make_strategy(*("strategy-1", 0, None, None), extra_kw=1))

    def test_defect_make_strategy_extra_positional(self):
        check_named_refusal(
            self, "make_strategy",
            lambda: mod09.make_strategy(*("strategy-1", 0, None, None), 1))

    def test_defect_search_extra_keyword(self):
        check_named_refusal(
            self, "search",
            lambda: mod09.search(*(None, None, None, None), extra_kw=1))

    def test_defect_search_extra_positional(self):
        check_named_refusal(
            self, "search",
            lambda: mod09.search(*(None, None, None, None), 1))


class TestFW1001Mod09Controls(unittest.TestCase):

    def test_control_attacker_payoff_extra_keyword(self):
        check_named_refusal(
            self, "attacker_payoff",
            lambda: mod09.attacker_payoff(
                {"in_protocol_payoff": 3}, 4, extra_kw=1))

    def test_control_attacker_payoff_extra_positional(self):
        check_named_refusal(
            self, "attacker_payoff",
            lambda: mod09.attacker_payoff(
                {"in_protocol_payoff": 3}, 4, 1))

    def test_control_attacker_payoff_served(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 3}, 4), 7)

    def test_control_make_strategy_served(self):
        record = mod09.make_strategy("strategy-1")
        self.assertIsInstance(record, dict)

    def test_control_catalogue_gaps_served(self):
        result = mod09.catalogue_gaps()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()

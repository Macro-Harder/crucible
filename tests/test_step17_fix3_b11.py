"""Step 17 fix wave 3, Slice 11 defect tests for row FW3-05.

The digit limit bare escape family across modules: a plain
integer past the interpreter conversion limit of 4300 digits,
or a finite integer too large to convert to a float, handed to
a cured door must stand refused in the door named form or
stand served whole. No bare interpreter sentence and no bare
OverflowError stands as an answer at any door of the family.
"""
import unittest
from fractions import Fraction

from crucible import mod02, mod04, mod05, mod06, mod08, mod09
from crucible import mod10, mod11

HUGE = 10 ** 5000
OVER = 10 ** 400
SEP = ["authorship separation", "knowledge separation",
       "record separation"]


def bare_escape(exc):
    if isinstance(exc, OverflowError):
        return True
    return "Exceeds the limit" in str(exc)


class TestMod02DigitTextPosition(unittest.TestCase):
    def test_defect_digit_text_position_served_whole(self):
        result = mod02.initial_stream_state(
            "alpha", carried_positions="9" * 5000)
        self.assertEqual(
            result["carried_positions"], 10 ** 5000 - 1)

    def test_defect_dict_digit_text_position_served_whole(self):
        result = mod02.initial_stream_state(
            "alpha",
            carried_positions={"position": "9" * 4301})
        self.assertEqual(
            result["carried_positions"], 10 ** 4301 - 1)

    def test_control_int_position_served_whole(self):
        result = mod02.initial_stream_state(
            "alpha", carried_positions=HUGE)
        self.assertEqual(result["carried_positions"], HUGE)

    def test_control_plain_digit_text_position(self):
        result = mod02.initial_stream_state(
            "alpha", carried_positions="123")
        self.assertEqual(result["carried_positions"], 123)


class TestMod05ScoreBearing(unittest.TestCase):
    def test_defect_score_bearing_oversized_envelope(self):
        result = mod05.score_bearing_figure(
            OVER, {"numerator": 1, "denominator": 2})
        self.assertEqual(result * 2, OVER)

    def test_defect_score_bearing_huge_envelope(self):
        result = mod05.score_bearing_figure(
            HUGE, {"numerator": 1, "denominator": 2})
        self.assertEqual(result * 2, HUGE)

    def test_defect_population_oversized_envelope(self):
        result = mod05.population_figure(
            OVER, [{"numerator": 1, "denominator": 2}],
            record_state="stated")
        self.assertEqual(
            result["per_epoch_corrected"][0] * 4, OVER)
        self.assertEqual(
            result["population_average"] * 4, OVER)

    def test_control_score_bearing_plain(self):
        result = mod05.score_bearing_figure(
            10, {"numerator": 1, "denominator": 2})
        self.assertEqual(result, 5.0)


class TestMod09PayoffDoors(unittest.TestCase):
    def test_defect_range_huge_member_carried_whole(self):
        record = mod09.make_strategy(
            "s1", in_protocol_payoff=3,
            external_profit_range=[HUGE])
        self.assertEqual(record["external_profit_range"], [HUGE])
        self.assertNotIn(
            "external_profit_range_substituted", record)

    def test_defect_attacker_external_huge(self):
        strategy = mod09.make_strategy("s1", in_protocol_payoff=1)
        self.assertEqual(mod09.attacker_payoff(strategy, HUGE),
                         HUGE + 1)

    def test_defect_attacker_in_protocol_oversized(self):
        self.assertEqual(
            mod09.attacker_payoff(
                {"in_protocol_payoff": OVER}, 1), OVER + 1)

    def test_defect_bond_harm_oversized(self):
        result = mod09.bond_search(
            [{"parameter_set": {"x": 1}, "harm": OVER,
              "attacker_cost": 1}])
        self.assertEqual(result["worst_griefing_factor"], OVER)

    def test_defect_bond_evaluator_oversized(self):
        result = mod09.bond_search(
            [{"parameter_set": {"x": 1}}],
            griefing_evaluator=lambda params: OVER)
        self.assertEqual(result["worst_griefing_factor"], OVER)

    def test_control_attacker_plain(self):
        self.assertEqual(
            mod09.attacker_payoff(
                {"in_protocol_payoff": 3}, 4), 7)

    def test_control_make_payoff_huge_served_whole(self):
        record = mod09.make_strategy(
            "s1", in_protocol_payoff=HUGE)
        self.assertEqual(record["in_protocol_payoff"], HUGE)


class TestServedWholeControls(unittest.TestCase):
    """Doors of the family that serve the handing whole on the
    assembled chain tree, pinned in the FW3-04 form."""

    def test_control_mod10_value_served(self):
        mod10.reset_stores()
        result = mod10.retain_run_record(
            {"run_id": "x1", "value": HUGE})
        self.assertIsInstance(result, dict)

    def test_control_mod10_key_served(self):
        mod10.reset_stores()
        result = mod10.retain_run_record(
            {"run_id": "x2", HUGE: 1})
        self.assertIsInstance(result, dict)

    def test_control_mod10_nested_served(self):
        mod10.reset_stores()
        result = mod10.retain_run_record(
            {"run_id": "hn", "v": [1, [HUGE]]})
        self.assertIsInstance(result, dict)

    def test_control_mod05_aggregate_served(self):
        result = mod05.aggregate_reputation({
            "agent_identifier": "agent-1",
            "accepted_work": HUGE,
            "vouches_received": [
                {"stake": 3, "score_bearing_flag": True}],
            "penalties": 1})
        self.assertIsInstance(result, dict)

    def test_control_mod05_band_served(self):
        result = mod05.band_membership(
            HUGE, [("low", 0)], evaluation_order="O-1")
        self.assertIsNotNone(result["band"])

    def test_control_mod05_boundary_served(self):
        result = mod05.boundary_neighbourhood(
            [{"agent_identifier": "a", "score": 1}], HUGE, [1])
        self.assertIsInstance(result, dict)

    def test_control_mod04_projection_served(self):
        result = mod04.project_detection_input({
            "agent_identifier": "agent-1", "day": 1,
            "feature_values": {"f1": HUGE}, "rule_records": []})
        self.assertIsInstance(result, dict)

    def test_control_mod11_point_standing_served(self):
        result = mod11.point_standing(HUGE)
        self.assertEqual(result["replicates"], HUGE)

    def test_control_mod11_honest_loss_served(self):
        result = mod11.honest_loss_rate_h1(HUGE, HUGE)
        self.assertEqual(result["numerator"], 0)
        self.assertEqual(result["denominator"], HUGE)

    def test_control_mod08_author_served(self):
        sealed = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed)
        result = mod08.author_sealed_class(
            sealed, "sleeper class", HUGE, separations=SEP)
        self.assertIsInstance(result, dict)

    def test_control_mod06_open_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction(
                "open_request",
                context={"stated_cost": HUGE,
                         "true_cost": HUGE})
        self.assertFalse(bare_escape(caught.exception))
        self.assertIn("open_request", str(caught.exception))

    def test_control_mod10_gate_share_named_refusal(self):
        mod10.reset_stores()
        with self.assertRaises(ValueError) as caught:
            mod10.record_gate_passing_share("run-x", "e1", HUGE)
        self.assertFalse(bare_escape(caught.exception))


if __name__ == "__main__":
    unittest.main()

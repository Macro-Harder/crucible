"""Step 17 fix wave 1, Builder 6 tests (Slice 6).

Rows: FW-14 (Medium, T17-16), FW-36 (Low, T17-41),
FW-37 (Low, T17-42), FW-40 (Medium, T17-45).

Each defect test reproduces its filing defect on the base tree at
product head 9f938470807f90b7c8c6d9882fde1105c807e0a1 and passes on
the fixed tree. Control and pin tests pass on both trees and state
the standings the rulings preserve. Standard library only.
"""
import unittest

from crucible import mod02
from crucible import mod05
from crucible import mod06
from crucible import mod09
from crucible import mod10


class ExplodingEq:
    """A value whose equality and hash readings raise."""

    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    def __hash__(self):
        raise RuntimeError("hash boom")


NAMED_POSITION = "position stands in no stated form"
NAMED_DRAW = "draw_from_stream stands refused"


class TestFW14InitialStreamState(unittest.TestCase):

    def test_nondigit_text_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod02.initial_stream_state(stream_class="s", carried_positions="x")
        self.assertIn(NAMED_POSITION, str(caught.exception))
        self.assertNotIn("invalid literal", str(caught.exception))

    def test_nondigit_text_5x_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod02.initial_stream_state(
                stream_class="s", carried_positions="5x")
        self.assertIn(NAMED_POSITION, str(caught.exception))
        self.assertNotIn("invalid literal", str(caught.exception))

    def test_digit_text_control(self):
        state = mod02.initial_stream_state(
            stream_class="s", carried_positions="5")
        self.assertEqual(state["carried_positions"], 5)
        self.assertEqual(state["position"], 0)

    def test_plain_count_control(self):
        state = mod02.initial_stream_state(
            stream_class="s", carried_positions=5)
        self.assertEqual(state["carried_positions"], 5)

    def test_draw_nondigit_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position="x", carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))


class TestFW14PauseCap(unittest.TestCase):

    def test_hostile_equality_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.pause_cap(ExplodingEq())
        self.assertIn(
            "pause cap stands refused in named form", str(caught.exception))

    def test_default_variant_control(self):
        result = mod06.pause_cap()
        self.assertEqual(result["variant"], "B-4")
        self.assertEqual(result["total_percent"], 400)

    def test_b3_variant_control(self):
        result = mod06.pause_cap("B-3", stated_value={"cap": 1})
        self.assertEqual(result["variant"], "B-3")

    def test_unknown_variant_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod06.pause_cap("B-9")
        self.assertIn(
            "pause cap stands refused in named form", str(caught.exception))


class TestFW14Component(unittest.TestCase):

    def test_tuple_entries_named_refusal(self):
        edges = [("a", "a")] * 100
        with self.assertRaises(ValueError) as caught:
            mod05.component(edges)
        self.assertIn("component stands refused", str(caught.exception))

    def test_single_tuple_entry_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod05.component([("a", "b")])
        self.assertIn("component stands refused", str(caught.exception))

    def test_text_entry_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod05.component(["edge-text"])
        self.assertIn("component stands refused", str(caught.exception))

    def test_entry_missing_vouchee_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod05.component([{"voucher": "a", "stake": 1}])
        self.assertIn("component stands refused", str(caught.exception))

    def test_unhashable_member_named_refusal(self):
        edges = [
            {"voucher": ["a"], "vouchee": "b", "stake": 1},
            {"voucher": "b", "vouchee": ["a"], "stake": 1},
        ]
        with self.assertRaises(ValueError) as caught:
            mod05.component(edges)
        self.assertIn("component stands refused", str(caught.exception))

    def test_mutual_pair_control(self):
        edges = [
            {"voucher": "a", "vouchee": "b", "stake": 2},
            {"voucher": "b", "vouchee": "a", "stake": 3},
        ]
        result = mod05.component(edges)
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 2)
        self.assertEqual(len(result["component_list"]), 1)
        self.assertEqual(result["component_list"][0]["stake_total"], 5)

    def test_one_direction_control(self):
        edges = [{"voucher": "a", "vouchee": "b", "stake": 2}]
        result = mod05.component(edges)
        self.assertEqual(result["component_list"], [])
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 0)

    def test_entry_without_stake_control(self):
        edges = [
            {"voucher": "a", "vouchee": "b"},
            {"voucher": "b", "vouchee": "a"},
        ]
        result = mod05.component(edges)
        self.assertEqual(len(result["component_list"]), 1)
        self.assertEqual(result["component_list"][0]["stake_total"], 0)


class TestFW14StoreLookup(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_non_iterable_kinds_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(store_kinds=5, key="x")
        self.assertIn("exactly one store kind", str(caught.exception))

    def test_hostile_kinds_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod10.store_lookup(store_kinds=ExplodingEq(), key="x")
        self.assertIn("exactly one store kind", str(caught.exception))

    def test_float_kinds_named_refusal(self):
        with self.assertRaises(ValueError):
            mod10.store_lookup(store_kinds=1.5, key="x")

    def test_retained_record_control(self):
        mod10.retain_run_record({"run_id": "run-b6"}, store_kind="sweep")
        record = mod10.store_lookup(store_kinds="sweep", key="run-b6")
        self.assertEqual(record["run_id"], "run-b6")

    def test_missing_key_lookup_failure_control(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.store_lookup(store_kinds="sweep", key="run-absent")

    def test_two_kinds_named_refusal_control(self):
        with self.assertRaises(ValueError):
            mod10.store_lookup(store_kinds=("sweep", "pilot"), key="x")

    def test_list_kind_control(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.store_lookup(store_kinds=["sweep"], key="run-absent")


class TestFW14RequestGenerator(unittest.TestCase):

    def test_positional_dict_gated_refusal(self):
        result = mod02.request_generator({"x": object()})
        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "supply generator")
        self.assertIs(result["seed_drawn"], False)
        self.assertIn("gate", result)

    def test_positional_text_gated_refusal(self):
        result = mod02.request_generator("anything")
        self.assertIsInstance(result, dict)
        self.assertIs(result["seed_drawn"], False)

    def test_no_argument_control(self):
        result = mod02.request_generator()
        self.assertEqual(result["action"], "supply generator")
        self.assertIs(result["seed_drawn"], False)

    def test_sibling_positional_control(self):
        result = mod02.derive_seed({"x": object()})
        self.assertIs(result["seed_drawn"], False)


class TestFW36StreamPositions(unittest.TestCase):

    def test_bool_position_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=True, carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_fractional_position_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=1.9, carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_negative_position_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=-1, carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_fractional_past_end_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=10.9, carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_negative_text_position_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position="-3", carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_bool_carried_refused_at_draw(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=1, carried_positions=True)
        self.assertIn(NAMED_DRAW, str(caught.exception))

    def test_bool_carried_refused_at_state(self):
        with self.assertRaises(ValueError) as caught:
            mod02.initial_stream_state(
                stream_class="x", carried_positions=True)
        self.assertIn(NAMED_POSITION, str(caught.exception))

    def test_fractional_carried_refused_at_state(self):
        with self.assertRaises(ValueError) as caught:
            mod02.initial_stream_state(
                stream_class="x", carried_positions=1.9)
        self.assertIn(NAMED_POSITION, str(caught.exception))

    def test_negative_carried_refused_at_state(self):
        with self.assertRaises(ValueError) as caught:
            mod02.initial_stream_state(
                stream_class="x", carried_positions=-3)
        self.assertIn(NAMED_POSITION, str(caught.exception))

    def test_in_range_position_control(self):
        result = mod02.draw_from_stream(
            stream_class="s", position=2, carried_positions=10)
        self.assertEqual(result["position"], 2)
        self.assertIs(result["seed_drawn"], False)

    def test_exhausted_position_control(self):
        result = mod02.draw_from_stream(
            stream_class="s", position=10, carried_positions=10)
        self.assertEqual(result["position"], 10)
        self.assertIn("STREAM-EXHAUSTED", str(result["failure"]))

    def test_digit_text_position_control(self):
        result = mod02.draw_from_stream(
            stream_class="s", position="007", carried_positions=10)
        self.assertEqual(result["position"], 7)

    def test_nan_position_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                stream_class="s", position=float("nan"),
                carried_positions=10)
        self.assertIn(NAMED_DRAW, str(caught.exception))


class TestFW37MakeStrategy(unittest.TestCase):

    def test_bool_payoff_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.make_strategy("s1", in_protocol_payoff=True)
        self.assertIn("make_strategy stands refused", str(caught.exception))

    def test_nan_payoff_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.make_strategy("s1", in_protocol_payoff=float("nan"))
        self.assertIn("make_strategy stands refused", str(caught.exception))

    def test_infinite_payoff_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.make_strategy("s1", in_protocol_payoff=float("inf"))

    def test_text_payoff_refused(self):
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.make_strategy("s1", in_protocol_payoff="5")

    def test_substituted_range_stated_on_record(self):
        record = mod09.make_strategy("x", 5, "also-not", None)
        self.assertEqual(record["external_profit_range"], [0])
        self.assertIs(record["external_profit_range_substituted"], True)
        self.assertIn("substituted", record["external_profit_standing"])

    def test_non_sequence_range_substitution_stated(self):
        record = mod09.make_strategy("x", 5, 123)
        self.assertEqual(record["external_profit_range"], [0])
        self.assertIs(record["external_profit_range_substituted"], True)

    def test_empty_range_substitution_stated(self):
        record = mod09.make_strategy("x", 5, [])
        self.assertEqual(record["external_profit_range"], [0])
        self.assertIs(record["external_profit_range_substituted"], True)

    def test_valid_range_control(self):
        record = mod09.make_strategy("s1", 5, [1, 2])
        self.assertEqual(record["external_profit_range"], [1, 2])
        self.assertNotIn("external_profit_range_substituted", record)
        self.assertEqual(record["in_protocol_payoff"], 5)

    def test_default_range_control(self):
        record = mod09.make_strategy("s1")
        self.assertEqual(record["external_profit_range"], [0])
        self.assertNotIn("external_profit_range_substituted", record)
        self.assertEqual(record["in_protocol_payoff"], 0)

    def test_conditional_briber_control(self):
        record = mod09.conditional_briber_strategy(
            in_protocol_payoff=3, external_profit_range=[2, 4])
        self.assertEqual(record["in_protocol_payoff"], 3)
        self.assertEqual(record["external_profit_range"], [2, 4])
        self.assertIs(record["named_strategy"], True)


class TestFW40RunInstruction(unittest.TestCase):

    def open_request(self, stated, true):
        return mod06.run_instruction(
            "open_request",
            context={"stated_cost": stated, "true_cost": true})

    def test_negative_stated_cost_refused(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request(-100, 50)
        self.assertIn("open_request stands refused", str(caught.exception))
        self.assertEqual(
            caught.exception.failure_class["recorded_in"],
            "run record only")

    def test_negative_true_cost_refused(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request(50, -50)
        self.assertIn("open_request stands refused", str(caught.exception))

    def test_nan_costs_refused(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request(float("nan"), float("nan"))
        self.assertIn("open_request stands refused", str(caught.exception))

    def test_infinite_cost_refused(self):
        with self.assertRaises(ValueError):
            self.open_request(float("inf"), 50)

    def test_text_costs_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request("100", "50")
        self.assertIn("open_request stands refused", str(caught.exception))
        self.assertEqual(
            caught.exception.failure_class["recorded_in"],
            "run record only")

    def test_extreme_cost_pair_refused(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request(1e308, 1e-308)
        self.assertIn("open_request stands refused", str(caught.exception))

    def test_bool_cost_refused(self):
        with self.assertRaises(ValueError):
            self.open_request(True, 50)

    def test_valid_costs_control(self):
        result = self.open_request(100, 50)
        self.assertTrue(mod06.validate_escrow_result(result))
        payload = result["payload"]
        self.assertEqual(payload["lien_size"], 100)
        self.assertEqual(payload["estimated_cost"]["accuracy"], 2.0)

    def test_zero_stated_cost_control(self):
        result = self.open_request(0, 50)
        self.assertEqual(result["payload"]["estimated_cost"]["accuracy"], 0.0)

    def test_zero_true_cost_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            self.open_request(100, 0)
        self.assertIn("true cost stands at zero", str(caught.exception))

    def test_missing_cost_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction("open_request", context={})
        self.assertIn("open_request stands refused", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

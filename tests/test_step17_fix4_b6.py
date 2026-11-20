"""Step 17 fix wave 4, Slice 6 defect tests: row FW4-02, the bare
digit limit family across modules (T17R3-02, Medium).

Five doors stand charged: the mod14 pilot artefact door, the
mod02 draw door, the mod10 store writer key rendering, the
mod10 aggregate component judgement, and the mod05 proportion
door. At each door a handing past the digit limit stands served
whole in a stated form or refused in named form stating the
true ground and any bound in product words; no bare interpreter
digit limit sentence escapes, and no refusal states a finite
form ground for a plain integer.

Huge values stand judged by type and by stored value (bit
length and equality against the handed integer), never by a
printed repr of a huge result.

Copyright: J.P. Picard aka Macro-Harder.
"""
import os
import tempfile
import unittest
from fractions import Fraction

import crucible.mod02 as mod02
import crucible.mod05 as mod05
import crucible.mod10 as mod10
import crucible.mod14 as mod14

HUGE = 10 ** 5000
BARE = "Exceeds the limit"


def _no_bare(test_case, fn):
    try:
        return fn()
    except Exception as exc:
        test_case.assertNotIn(BARE, str(exc))
        raise


class TestFW402Mod14PilotKeys(unittest.TestCase):
    """Door 1: mod14 pilot artefact huge integer keys."""

    def test_top_level_huge_key_served_whole(self):
        result = _no_bare(self, lambda: mod14.pilot_run("timing", {HUGE: 1}))
        keys = [key for key in result if isinstance(key, int)]
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0], HUGE)
        self.assertEqual(result[HUGE], 1)

    def test_nested_huge_key_served_whole(self):
        result = _no_bare(
            self, lambda: mod14.pilot_run("timing", {"a": {HUGE: 1}}))
        self.assertEqual(result["a"][HUGE], 1)

    def test_list_carried_huge_key_served_whole(self):
        result = _no_bare(
            self, lambda: mod14.pilot_run("timing", [{HUGE: 1}]))
        self.assertEqual(result["figure"][0][HUGE], 1)

    def test_tuple_carried_huge_key_served_whole(self):
        result = _no_bare(
            self, lambda: mod14.pilot_run("timing", ({HUGE: 1},)))
        self.assertEqual(result["figure"][0][HUGE], 1)

    def test_huge_value_control_served_whole(self):
        result = mod14.pilot_run("timing", {"a": HUGE})
        self.assertEqual(result["a"], HUGE)

    def test_plain_artefact_control_served_whole(self):
        result = mod14.pilot_run("timing", {"a": 1})
        self.assertEqual(result["a"], 1)


class TestFW402Mod02DrawPosition(unittest.TestCase):
    """Door 2: mod02 draw_from_stream huge position with a state
    handed. These tests pin the served whole standing the probes
    of the builder paper state in full: the charged handings
    answer in the named STREAM-EXHAUSTED form carrying the
    position whole, judged by bit length."""

    def test_huge_int_position_with_state_served_whole(self):
        state = mod02.initial_stream_state("alpha", carried_positions=0)
        result = _no_bare(self, lambda: mod02.draw_from_stream(
            "alpha", position=HUGE, state=state))
        self.assertEqual(result["failure"], mod02.STREAM_EXHAUSTED_FAILURE)
        self.assertEqual(result["position"], HUGE)
        self.assertEqual(result["position"].bit_length(), HUGE.bit_length())

    def test_huge_text_position_with_state_served_whole(self):
        state = mod02.initial_stream_state("alpha", carried_positions=0)
        result = _no_bare(self, lambda: mod02.draw_from_stream(
            "alpha", position="9" * 5000, state=state))
        self.assertEqual(result["failure"], mod02.STREAM_EXHAUSTED_FAILURE)
        self.assertEqual(result["position"], 10 ** 5000 - 1)

    def test_huge_position_below_huge_carried_gated_whole(self):
        result = _no_bare(self, lambda: mod02.draw_from_stream(
            "alpha", position=HUGE, carried_positions=HUGE + 1))
        self.assertEqual(result["failure"], "DERIVATION-GATED")
        self.assertEqual(result["position"], HUGE)
        self.assertFalse(result["seed_drawn"])

    def test_no_state_control_refuses_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream("alpha", position=HUGE)
        self.assertIn("carried positions", str(caught.exception))
        self.assertNotIn(BARE, str(caught.exception))

    def test_under_limit_control_named_form(self):
        state = mod02.initial_stream_state("alpha", carried_positions=0)
        result = mod02.draw_from_stream(
            "alpha", position=10 ** 4000, state=state)
        self.assertEqual(result["failure"], mod02.STREAM_EXHAUSTED_FAILURE)


class TestFW402Mod10WriterKeys(unittest.TestCase):
    """Door 3: mod10 store writer top level record keys. These
    tests pin the served whole standing the builder paper probes
    state in full, at the module, class, and file backed doors."""

    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_module_door_top_huge_key_served_whole(self):
        result = _no_bare(self, lambda: mod10.retain_run_record(
            {"run_id": "fw402-w1", HUGE: "x"}))
        self.assertEqual(result[HUGE], "x")

    def test_class_door_top_huge_key_served_whole(self):
        store = mod10.new_store("sweep")
        result = _no_bare(self, lambda: store.retain_run_record(
            {"run_id": "fw402-w2", HUGE: "x"}))
        self.assertEqual(result[HUGE], "x")
        back = store.read_run_record("fw402-w2")
        self.assertEqual(back[HUGE], "x")

    def test_file_door_top_huge_key_served_whole(self):
        with tempfile.TemporaryDirectory() as folder:
            store = mod10.new_store(
                "sweep", path=os.path.join(folder, "store.json"))
            result = _no_bare(self, lambda: store.retain_run_record(
                {"run_id": "fw402-w3", HUGE: "x"}))
            self.assertEqual(result[HUGE], "x")

    def test_huge_value_control_served_whole(self):
        store = mod10.new_store("sweep")
        result = store.retain_run_record({"run_id": "fw402-w4", "v": HUGE})
        self.assertEqual(result["v"], HUGE)

    def test_nested_huge_key_control_served_whole(self):
        store = mod10.new_store("sweep")
        result = store.retain_run_record(
            {"run_id": "fw402-w5", "n": {HUGE: "x"}})
        self.assertEqual(result["n"][HUGE], "x")

    def test_small_int_key_control_served_whole(self):
        store = mod10.new_store("sweep")
        result = store.retain_run_record({"run_id": "fw402-w6", 5: "x"})
        self.assertEqual(result[5], "x")


class TestFW402Mod10Aggregate(unittest.TestCase):
    """Door 4: mod10 aggregate huge denominator at retention.
    These tests pin the served whole standing the builder paper
    probes state in full."""

    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    @staticmethod
    def _delivery(components, denominators):
        return {
            "simulated_day": 1, "viewer_id": "v1",
            "joint_outcome_components": components,
            "component_denominators": denominators,
            "honest_share": 0, "gate_passing_shares": {},
            "epochs_ending_on_day": [],
        }

    def test_huge_denominator_retained_and_read_whole(self):
        count = _no_bare(self, lambda: mod10.retain_daily_aggregate_deliveries(
            "fw402-a1", [self._delivery([1, 0, 0, 0], [HUGE, 1, 1, 1])]))
        self.assertEqual(count, 1)
        rows = mod10.daily_aggregates_for_run("fw402-a1")
        self.assertEqual(len(rows), 1)
        denominators = rows[0]["component_denominators"]
        self.assertEqual(denominators[0], HUGE)
        self.assertEqual(
            denominators[0].bit_length(), HUGE.bit_length())

    def test_component_equal_to_huge_denominator_served_whole(self):
        count = _no_bare(self, lambda: mod10.retain_daily_aggregate_deliveries(
            "fw402-a2", [self._delivery([HUGE, 0, 0, 0], [HUGE, 1, 1, 1])]))
        self.assertEqual(count, 1)

    def test_under_limit_control_served_whole(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "fw402-a3", [self._delivery(
                [10 ** 400, 0, 0, 0], [10 ** 400, 1, 1, 1])])
        self.assertEqual(count, 1)

    def test_component_above_denominator_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "fw402-a4", [self._delivery([HUGE, 0, 0, 0], [1, 1, 1, 1])])
        self.assertIn("daily aggregate delivery in named form",
                      str(caught.exception))
        self.assertNotIn(BARE, str(caught.exception))


class TestFW402Mod05Proportion(unittest.TestCase):
    """Door 5: mod05 proportion false ground refusal. A huge
    plain integer stands finite at any size and stands served
    whole, as the score doors of the same module serve a huge
    envelope whole as an exact Fraction."""

    def test_huge_numerator_served_whole(self):
        result = _no_bare(self, lambda: mod05.proportion_record(HUGE, 2))
        self.assertEqual(result["numerator"], HUGE)
        self.assertEqual(result["denominator"], 2)

    def test_huge_denominator_served_whole(self):
        result = _no_bare(self, lambda: mod05.proportion_record(1, HUGE))
        self.assertEqual(result["denominator"], HUGE)

    def test_float_overrange_numerator_served_whole(self):
        result = _no_bare(
            self, lambda: mod05.proportion_record(10 ** 400, 2))
        self.assertEqual(result["numerator"], 10 ** 400)

    def test_huge_proportion_validates_true(self):
        record = mod05.proportion_record(HUGE, HUGE)
        self.assertTrue(mod05.validate_proportion(record))
        self.assertTrue(mod05.validate_proportion(
            {"numerator": 1, "denominator": HUGE}))

    def test_huge_share_score_figure_exact_fraction(self):
        result = _no_bare(self, lambda: mod05.score_bearing_figure(
            100, {"numerator": 1, "denominator": HUGE}))
        self.assertEqual(result, Fraction(100, HUGE))

    def test_infinite_part_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod05.proportion_record(float("inf"), 2)
        self.assertIn("stands in no finite form", str(caught.exception))

    def test_nan_part_named_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod05.proportion_record(float("nan"), 2)
        self.assertIn("stands in no finite form", str(caught.exception))

    def test_plain_proportion_control_served_whole(self):
        result = mod05.proportion_record(1, 2)
        self.assertEqual(result, {"numerator": 1, "denominator": 2})
        self.assertTrue(mod05.validate_proportion(result))

    def test_negative_and_zero_controls_refuse_named(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(-1, 2)
        with self.assertRaises(ValueError):
            mod05.proportion_record(1, 0)


if __name__ == "__main__":
    unittest.main()

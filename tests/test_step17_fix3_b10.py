"""Step 17 fix wave 3, Builder 10 defect tests (Slice 10).

Rows FW3-32, FW3-34, FW3-45, FW3-46, FW3-47, FW3-48, FW3-56,
FW3-57, and FW3-58. Each defect test reproduces its filing defect
on the uncured tree and passes on the cured tree. Control tests
pin the landed standings the cures must hold. DQ7-02 stands
never circumvented: no test draws a seed, and every gated act
stands asserted on its refusal standing alone.
"""

import unittest

from crucible import mod02, mod03, mod04, mod06, mod09, mod12, mod14


def _cast_point(population):
    return {
        "population": population,
        "archetype_mix": {"a1": population},
    }


def _records():
    return [mod03.make_archetype_record("a1")]


def _complete_input():
    return mod02.make_derivation_input(
        derivation_version="v1", domain="screening")


class TestFW332BuildCastBound(unittest.TestCase):

    def test_population_past_canonical_bound_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.build_cast(
                _cast_point(801), _records(), strategy_class="honest")
        self.assertIn("800", str(caught.exception))

    def test_population_far_past_bound_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.build_cast(
                _cast_point(200000), _records(),
                strategy_class="honest")
        self.assertIn("cast rejected", str(caught.exception))

    def test_population_at_bound_builds(self):
        cast = mod03.build_cast(
            _cast_point(800), _records(), strategy_class="honest")
        self.assertEqual(len(cast["cast"]), 800)

    def test_canonical_population_builds(self):
        cast = mod03.build_cast(
            _cast_point(200), _records(), strategy_class="honest")
        self.assertEqual(cast["population"], 200)


class TestFW334OpenRequestCostBar(unittest.TestCase):

    def _open(self, stated, true):
        return mod06.run_instruction(
            "open_request",
            context={"stated_cost": stated, "true_cost": true})

    def test_oversized_true_cost_refused(self):
        with self.assertRaises(ValueError) as caught:
            self._open(10, 10 ** 5000)
        self.assertIn("open_request stands refused", str(caught.exception))

    def test_true_cost_underflowing_accuracy_refused(self):
        with self.assertRaises(ValueError) as caught:
            self._open(1, 10 ** 5000)
        self.assertIn("open_request stands refused", str(caught.exception))

    def test_plain_pair_opens(self):
        result = self._open(10, 5)
        self.assertEqual(
            result["payload"]["estimated_cost"]["accuracy"], 2.0)

    def test_oversized_stated_cost_refused_control(self):
        with self.assertRaises(ValueError) as caught:
            self._open(10 ** 5000, 10)
        self.assertIn("open_request stands refused", str(caught.exception))


class TestFW345MakeStrategyRangeMarking(unittest.TestCase):

    def test_nan_member_range_substituted_and_marked(self):
        record = mod09.make_strategy(
            "s1", external_profit_range=[float("nan"), 5])
        self.assertEqual(record["external_profit_range"], [0])
        self.assertTrue(record["external_profit_range_substituted"])

    def test_text_member_range_substituted_and_marked(self):
        record = mod09.make_strategy(
            "s1", external_profit_range=["a", "b"])
        self.assertEqual(record["external_profit_range"], [0])
        self.assertTrue(record["external_profit_range_substituted"])

    def test_infinite_member_range_substituted_and_marked(self):
        record = mod09.make_strategy(
            "s1", external_profit_range=[5, float("inf")])
        self.assertEqual(record["external_profit_range"], [0])
        self.assertTrue(record["external_profit_range_substituted"])

    def test_usable_range_carried_unmarked(self):
        record = mod09.make_strategy(
            "s1", external_profit_range=[0, 10])
        self.assertEqual(record["external_profit_range"], [0, 10])
        self.assertNotIn("external_profit_range_substituted", record)

    def test_no_range_default_unmarked(self):
        record = mod09.make_strategy("s1")
        self.assertEqual(record["external_profit_range"], [0])
        self.assertNotIn("external_profit_range_substituted", record)


class TestFW346DeriveSeedRefusalForm(unittest.TestCase):

    def test_malformed_input_refusal_states_next_step(self):
        result = mod02.derive_seed({"bogus": 1})
        self.assertEqual(result["status"], "input failure")
        self.assertIn("derivation_version", result["ground_in_words"])
        self.assertIn("next step", result["next_step"].lower())
        self.assertFalse(result["seed_drawn"])

    def test_nonrecord_input_refusal_states_next_step(self):
        result = mod02.derive_seed(123)
        self.assertEqual(result["status"], "input failure")
        self.assertIn("next step", result["next_step"].lower())
        self.assertFalse(result["seed_drawn"])

    def test_no_input_still_gated_control(self):
        result = mod02.derive_seed()
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["seed_drawn"])


class TestFW347ShellCommandFormGround(unittest.TestCase):

    def test_bytes_command_refusal_states_form_ground(self):
        carriage = mod14.run_command(b"read_store", {"run_id": "run-a"})
        self.assertIn("no command form", carriage["failure"])
        self.assertNotIn("unknown shell command", carriage["failure"])

    def test_bytearray_command_refusal_states_form_ground(self):
        carriage = mod14.run_command(
            bytearray(b"read_store"), {"run_id": "run-a"})
        self.assertIn("no command form", carriage["failure"])
        self.assertNotIn("unknown shell command", carriage["failure"])

    def test_unknown_text_command_control(self):
        carriage = mod14.run_command("bogus_cmd", run_id="r1")
        self.assertIn("unknown shell command: bogus_cmd",
                      carriage["failure"])

    def test_unknown_bytes_command_control(self):
        carriage = mod14.run_command(b"bogus-cmd")
        self.assertIn("unknown shell command: bogus-cmd",
                      carriage["failure"])


class TestFW348GatedDoorsExtraKeywords(unittest.TestCase):

    def test_derive_seed_adoption_keyword_named(self):
        result = mod02.derive_seed(
            _complete_input(), adoption_record="supposed adoption")
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["seed_drawn"])
        self.assertIn("adoption_record", str(result))

    def test_derive_seed_misspelled_keyword_named(self):
        result = mod02.derive_seed(
            _complete_input(), adoptoin_record="supposed adoption")
        self.assertEqual(result["status"], "gated")
        self.assertIn("adoptoin_record", str(result))

    def test_derive_stream_seed_extra_keyword_named(self):
        result = mod02.derive_stream_seed(_complete_input(), seed=12345)
        self.assertEqual(result["status"], "gated")
        self.assertIn("'seed'", str(result))

    def test_derive_stream_state_extra_keyword_named(self):
        result = mod02.derive_stream_state([], seed=12345)
        self.assertEqual(result["status"], "gated")
        self.assertIn("'seed'", str(result))

    def test_advance_stream_state_extra_keyword_named(self):
        result = mod02.advance_stream_state({}, seed=12345)
        self.assertEqual(result["status"], "gated")
        self.assertIn("'seed'", str(result))

    def test_request_generator_extra_keyword_named(self):
        result = mod02.request_generator(seed=12345)
        self.assertEqual(result["status"], "gated")
        self.assertIn("'seed'", str(result))

    def test_mod04_run_extra_keyword_named(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.run(adoption_record="supposed adoption")
        self.assertIn("adoption_record", str(caught.exception))

    def test_mod04_tick_extra_keyword_named(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.tick(seed=12345)
        self.assertIn("seed", str(caught.exception))

    def test_mod12_start_run_extra_keyword_named(self):
        result = mod12.start_run(
            "screening", family_id="f1",
            adoption_record="supposed adoption")
        self.assertFalse(result["run_started"])
        self.assertFalse(result["seed_drawn"])
        self.assertIn("adoption_record", str(result))

    def test_mod12_start_sweep_extra_keyword_named(self):
        result = mod12.start_sweep(family_id="f1", seed=12345)
        self.assertFalse(result["run_started"])
        self.assertIn("'seed'", str(result))

    def test_plain_derive_seed_control(self):
        result = mod02.derive_seed(_complete_input())
        self.assertEqual(result["status"], "gated")
        self.assertNotIn("unexpected_keyword_handings", result)

    def test_plain_mod04_run_control(self):
        with self.assertRaises(mod04.GatedRun) as caught:
            mod04.run()
        self.assertIn("DERIVATION-GATED", str(caught.exception))
        self.assertNotIn("adoption_record", str(caught.exception))

    def test_plain_mod12_start_run_control(self):
        result = mod12.start_run("screening", family_id="f1")
        self.assertFalse(result["run_started"])
        self.assertNotIn("unexpected_keyword_handings", result)


class TestFW356DrawPositionFormGround(unittest.TestCase):

    def test_fractional_position_states_form_ground(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "s", position=1.5, carried_positions=5)
        text = str(caught.exception)
        self.assertIn("whole number at or above zero", text)
        self.assertNotIn("stands in no numeric form", text)

    def test_negative_position_states_form_ground(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "s", position=-1, carried_positions=5)
        text = str(caught.exception)
        self.assertIn("whole number at or above zero", text)
        self.assertNotIn("stands in no numeric form", text)

    def test_non_numeric_position_control(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                "s", position="abc", carried_positions=5)
        self.assertIn("stands in no numeric form", str(caught.exception))

    def test_valid_position_gated_control(self):
        result = mod02.draw_from_stream(
            "s", position=0, carried_positions=2)
        self.assertEqual(result["status"], "gated")
        self.assertFalse(result["seed_drawn"])


class TestFW357ConstructFarmSizeZero(unittest.TestCase):

    def test_size_zero_states_member_set(self):
        result = mod03.construct_farm(["a", "b"], farm_size=0)
        self.assertEqual(result["farms"], [])
        self.assertEqual(result["unplaced_member_ids"], ["a", "b"])
        self.assertIn("member_set_standing", result)

    def test_no_size_states_member_set(self):
        result = mod03.construct_farm(["a", "b"])
        self.assertEqual(result["unplaced_member_ids"], ["a", "b"])

    def test_size_one_places_members_control(self):
        result = mod03.construct_farm(["a", "b"], farm_size=1)
        self.assertEqual(len(result["farms"]), 2)
        self.assertNotIn("unplaced_member_ids", result)

    def test_empty_member_set_control(self):
        result = mod03.construct_farm([], farm_size=0)
        self.assertEqual(result["farms"], [])
        self.assertNotIn("unplaced_member_ids", result)


class TestFW358ValidatePauseResultVariant(unittest.TestCase):

    def test_undocumented_variant_refused(self):
        self.assertFalse(mod06.validate_pause_result(
            {"variant": "B-9", "per_variant_pause_value": 123}))

    def test_bogus_variant_refused(self):
        self.assertFalse(mod06.validate_pause_result(
            {"variant": "bogus",
             "per_variant_pause_value": dict(mod06.PAUSE_CAP_B4)}))

    def test_missing_variant_refused(self):
        self.assertFalse(mod06.validate_pause_result(
            {"per_variant_pause_value": 123}))

    def test_b3_control(self):
        self.assertTrue(mod06.validate_pause_result(
            {"variant": "B-3", "per_variant_pause_value": 7}))

    def test_b4_cap_control(self):
        self.assertTrue(mod06.validate_pause_result(
            {"variant": "B-4",
             "per_variant_pause_value": dict(mod06.PAUSE_CAP_B4)}))

    def test_b4_wrong_cap_control(self):
        self.assertFalse(mod06.validate_pause_result(
            {"variant": "B-4",
             "per_variant_pause_value": {
                 "extension_percent": 100, "total_percent": 200}}))


if __name__ == "__main__":
    unittest.main()

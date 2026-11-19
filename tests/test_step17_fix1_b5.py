"""Step 17 fix wave 1, Slice 5 tests.

Rows FW-05, FW-28, FW-29, and FW-41 of the Step 17 Round 1
register, section 19. Each defect test reproduces the filing
probe on the base tree and fails there for the stated reason;
each control test pins behaviour the fix must not move.
"""

import unittest

from crucible import mod03
from crucible import mod11


class TestFW05HonestLossRate(unittest.TestCase):
    """FW-05: honest_loss_rate_h1 refuses a count pair no
    population can carry, in the named whole number form, and
    applies no clamp in silence."""

    def test_accepted_above_submitted_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod11.honest_loss_rate_h1(5, 10)
        self.assertIn(
            "honest_loss_rate_h1 stands refused",
            str(caught.exception))

    def test_zero_submitted_nonzero_accepted_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(0, 5)

    def test_negative_submitted_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(-3, 0)

    def test_both_counts_negative_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(-5, -10)

    def test_zero_pair_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(0, 0)

    def test_negative_accepted_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(10, -1)

    def test_control_pair_stands(self):
        result = mod11.honest_loss_rate_h1(10, 3)
        self.assertEqual(result["form"], "H1")
        self.assertEqual(result["numerator"], 7)
        self.assertEqual(result["denominator"], 10)

    def test_control_full_acceptance_stands(self):
        result = mod11.honest_loss_rate_h1(10, 10)
        self.assertEqual(result["numerator"], 0)
        self.assertEqual(result["denominator"], 10)

    def test_control_no_acceptance_stands(self):
        result = mod11.honest_loss_rate_h1(10, 0)
        self.assertEqual(result["numerator"], 10)
        self.assertEqual(result["denominator"], 10)

    def test_control_non_whole_number_still_refused(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(2.5, 1)
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1("5", 1)


class TestFW28TransitionFigure(unittest.TestCase):
    """FW-28: transition_figure over no replicates returns the
    undelivered standing its sibling doors state, and counts
    each replicate once."""

    def test_empty_replicates_carry_unknown_standing(self):
        figure = mod11.transition_figure([])
        self.assertEqual(figure["denominator"], 0)
        self.assertEqual(figure["cumulative_incidence"], {})
        self.assertEqual(figure["competing_events"], 0)
        self.assertEqual(figure["right_censored"]["count"], 0)
        self.assertEqual(figure["right_censored"]["denominator"], 0)
        self.assertEqual(figure["right_censored"]["share"], "unknown")

    def test_same_record_twice_counts_once(self):
        figure = mod11.transition_figure(
            [{"first_terminal_regime": "alpha"},
             {"first_terminal_regime": "alpha"}])
        self.assertEqual(figure["denominator"], 1)
        entry = figure["cumulative_incidence"]["alpha"]
        self.assertEqual(entry["count"], 1)
        self.assertEqual(entry["denominator"], 1)
        self.assertEqual(entry["share"], 1.0)

    def test_same_object_twice_counts_once(self):
        record = {"first_terminal_regime": "alpha"}
        figure = mod11.transition_figure([record, record])
        self.assertEqual(figure["denominator"], 1)

    def test_control_mixed_population_unchanged(self):
        figure = mod11.transition_figure(
            [{"first_terminal_regime": "alpha"},
             {"first_terminal_regime": "beta"},
             {},
             {"competing_exit": True}])
        self.assertEqual(figure["denominator"], 4)
        self.assertEqual(
            figure["cumulative_incidence"]["alpha"]["count"], 1)
        self.assertEqual(
            figure["cumulative_incidence"]["alpha"]["share"], 0.25)
        self.assertEqual(
            figure["cumulative_incidence"]["beta"]["share"], 0.25)
        self.assertEqual(figure["right_censored"]["count"], 1)
        self.assertEqual(figure["right_censored"]["share"], 0.25)
        self.assertEqual(figure["competing_events"], 1)

    def test_control_distinct_records_same_regime_count_twice(self):
        figure = mod11.transition_figure(
            [{"first_terminal_regime": "alpha", "run": 1},
             {"first_terminal_regime": "alpha", "run": 2}])
        self.assertEqual(figure["denominator"], 2)
        self.assertEqual(
            figure["cumulative_incidence"]["alpha"]["count"], 2)


class TestFW29WeeklyContainer(unittest.TestCase):
    """FW-29, weekly limb: make_weekly_container judges the
    population as a set of identities, deduplicating a repeated
    identity in stated form."""

    def test_repeated_identifier_counted_once(self):
        container = mod11.make_weekly_container(
            "2026-W1", ["u01", "u01", "u01"])
        self.assertEqual(container["count"], 1)
        self.assertEqual(container["headline_units"], ["u01"])
        self.assertEqual(container["weekly_load"]["H"], 1)
        self.assertEqual(container["held_count"], 0)

    def test_repeats_do_not_consume_the_cap(self):
        units = ["u%02d" % n for n in range(1, 26)] + ["u01", "u02"]
        container = mod11.make_weekly_container("2026-W1", units)
        self.assertEqual(container["count"], 25)
        self.assertEqual(container["held_count"], 0)
        self.assertEqual(container["held_units"], [])

    def test_released_repeat_counts_once(self):
        first = mod11.make_weekly_container(
            "2026-W1", ["u%02d" % n for n in range(1, 28)])
        following = mod11.next_weekly_container(
            "2026-W2", first, ["u26"])
        self.assertEqual(following["headline_units"], ["u26", "u27"])
        self.assertEqual(following["count"], 2)

    def test_control_distinct_identifiers_unchanged(self):
        container = mod11.make_weekly_container(
            "2026-W1", ["u01", "u02", "u03"])
        self.assertEqual(container["count"], 3)
        self.assertEqual(
            container["headline_units"], ["u01", "u02", "u03"])

    def test_control_cap_and_held_unchanged(self):
        units = ["u%02d" % n for n in range(1, 28)]
        container = mod11.make_weekly_container("2026-W1", units)
        self.assertEqual(container["count"], 25)
        self.assertEqual(container["held_units"], ["u26", "u27"])
        self.assertEqual(container["held_count"], 2)
        self.assertTrue(container["held_reported_as_held"])


class TestFW29ConstructFarm(unittest.TestCase):
    """FW-29, farm limb: construct_farm judges the population
    as a set of identities, deduplicating a repeated identity
    in stated form."""

    def test_repeated_member_grouped_once(self):
        result = mod03.construct_farm(["a", "a", "a"], farm_size=3)
        self.assertEqual(
            result["farms"],
            [{"farm_id": "farm-0", "member_ids": ["a"]}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0})

    def test_repeated_member_fills_size_once(self):
        result = mod03.construct_farm(["a", "a", "b"], farm_size=2)
        self.assertEqual(
            result["farms"],
            [{"farm_id": "farm-0", "member_ids": ["a", "b"]}])

    def test_control_distinct_members_unchanged(self):
        result = mod03.construct_farm(["a", "b", "c"], farm_size=2)
        self.assertEqual(
            result["farms"],
            [{"farm_id": "farm-0", "member_ids": ["a", "b"]},
             {"farm_id": "farm-1", "member_ids": ["c"]}])

    def test_control_internal_edge_count_unchanged(self):
        result = mod03.construct_farm(
            ["a", "b"], farm_size=2, edges=[("a", "b")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})


class TestFW41ColdSocietyDegree(unittest.TestCase):
    """FW-41: cold_society_degree holds returned figures to the
    bounds its docstring states, or refuses inputs that carry
    them outside, in the named failure form. This row sets no
    population bound."""

    def test_negative_day_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(-5)

    def test_negative_day_with_operands_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                -5, envelope=2, gate_passing_share=0.5)

    def test_negative_envelope_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=-3, gate_passing_share=0.5)

    def test_share_above_one_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=2, gate_passing_share=7.5)

    def test_negative_share_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=2, gate_passing_share=-0.5)

    def test_nan_share_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=2, gate_passing_share=float("nan"))

    def test_nan_envelope_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=float("nan"), gate_passing_share=0.5)

    def test_infinite_envelope_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                100, envelope=float("inf"), gate_passing_share=0.5)

    def test_control_first_days_return_zero(self):
        self.assertEqual(mod03.cold_society_degree(0), 0)
        self.assertEqual(mod03.cold_society_degree(90), 0)

    def test_control_products_stand(self):
        self.assertEqual(
            mod03.cold_society_degree(
                91, envelope=10, gate_passing_share=0.5), 5.0)
        self.assertEqual(
            mod03.cold_society_degree(
                365, envelope=8, gate_passing_share=0.25), 2.0)

    def test_control_share_bounds_inclusive(self):
        self.assertEqual(
            mod03.cold_society_degree(
                100, envelope=3, gate_passing_share=1), 3)
        self.assertEqual(
            mod03.cold_society_degree(
                100, envelope=3, gate_passing_share=0), 0)

    def test_control_gated_standing_stands(self):
        result = mod03.cold_society_degree(10000)
        self.assertIsNone(result["degree"])
        self.assertEqual(
            result["standing"], "gated by the gate passing share")

    def test_control_text_day_still_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree("100")


if __name__ == "__main__":
    unittest.main()

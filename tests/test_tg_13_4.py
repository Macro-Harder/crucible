"""Test group TG-13.4. Transition and crossover reporting, AC-13.
Slice S-13, Reporter and family registry, MOD-11. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod11, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG134(unittest.TestCase):
    def test_full_transition_report_form(self):
        """
        Fixture: F-18, the canonical scale and readout set.
        Pins: Every transition report carries the full distribution near the threshold, the three regime class counts, and the honest loss rate beside the headline figure, and rests on at least 30 replicates per control point near the threshold, with the top up rule of the fixture applied and recorded where a screening point lands between winning probability 0.1 and 0.9.
        Bar: The honest loss rate stands decided at DQ7-06 in the H1 form and travels as a defined quantity in that form; a report presenting any other form of the rate fails this group, and no report rests on the band progress or the suspect treatment companions, which stand carried open inside the DQ7-06 entry under their bars.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a transition report missing any named part, or resting on fewer than 30 replicates at a near threshold point, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "full transition report form on F-18, distribution near threshold, three regime class counts, honest loss rate in H1 form, at least 30 replicates per near threshold point")
        m = _surface_module
        report = {
            "distribution_near_threshold": {"counts_by_outcome": [12, 9, 9]},
            "regime_class_counts": {"attacker winning": 12,
                                    "defender holding": 9,
                                    "no terminal regime": 9},
            "honest_loss_rate": m.honest_loss_rate_h1(100, 90),
            "points": [{"near_threshold": True, "replicates": 30,
                        "winning_probability": 0.5,
                        "top_up_recorded": True}],
        }
        self.assertEqual(report["honest_loss_rate"]["form"], "H1")
        self.assertTrue(m.validate_transition_report(report))
        short = dict(report, points=[{"near_threshold": True,
                                      "replicates": 29,
                                      "winning_probability": 0.5,
                                      "top_up_recorded": True}])
        self.assertFalse(m.validate_transition_report(short))
        other_form = dict(report, honest_loss_rate={"form": "other form"})
        self.assertFalse(m.validate_transition_report(other_form))
        no_counts = dict(report, regime_class_counts={"attacker winning": 12})
        self.assertFalse(m.validate_transition_report(no_counts))

    def test_stability_and_crossover_wording(self):
        """
        Fixture: F-18 stability limb, region location under population change across 200, 400, and 800 agents and under the run length window change.
        Pins: A transition is reported as holding only where the region location is stable in the form the fixture states, moving by no more than one grid step on either axis, and where the narrowing test fails the region is reported as a finite population crossover, in those words. Stability is tested only where a location stands reported at both points compared. Where no location stands reported at a point, the report states the crossover form or the censored form, as the case stands, and no holding statement is made for that comparison.
        Bar: Crossover wording on a holding report, or holding wording on a failed narrowing test, fails this group; wording is behaviour and is tested as behaviour.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a holding report carrying crossover wording, or a failed narrowing test carrying holding wording, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "stability and crossover wording on F-18, holding only where location moves by no more than one grid step on either axis")
        m = _surface_module
        holding = m.transition_wording((3, 4), (4, 4))
        self.assertEqual(holding["wording"], "holding")
        self.assertTrue(holding["holding_statement"])
        crossed = m.transition_wording((3, 4), (5, 4))
        self.assertEqual(crossed["wording"], "finite population crossover")
        self.assertFalse(crossed["holding_statement"])
        censored = m.transition_wording(
            (3, 4), (3, 4), location_reported=(True, False))
        self.assertEqual(censored["wording"], "censored form")
        self.assertFalse(censored["holding_statement"])

    def test_top_up_closed_bounds_and_below_floor_point(self):
        """
        Fixture: F-18 top up limb, read with closed bounds as Amendment TG4-07 states, with a point at 29 replicates beside a point at the 30 replicate floor.
        Pins: The top up duty applies at or above 0.1 and at or below 0.9, the same edge form as the transition region it serves; a point at 29 replicates, a derived count one below the floor, is reported as below floor, with its count stated, and borrows no standing of a point at the floor.
        Bar: A below floor point reported with the standing of a point at the floor fails this group, and an open bound reading of the top up range fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a 29 replicate point reported as at floor fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "top up closed bounds at 0.1 and 0.9, and a 29 replicate point reported as below floor with its count stated")
        m = _surface_module
        self.assertTrue(m.top_up_applies(0.1))
        self.assertTrue(m.top_up_applies(0.9))
        self.assertTrue(m.top_up_applies(0.5))
        self.assertFalse(m.top_up_applies(0.05))
        self.assertFalse(m.top_up_applies(0.95))
        below = m.point_standing(29)
        self.assertEqual(below["standing"], "below floor")
        self.assertEqual(below["replicates"], 29)
        at_floor = m.point_standing(30)
        self.assertEqual(at_floor["standing"], "at floor")

    def test_short_run_horizon_insufficient(self):
        """
        Fixture: F-18, with a run shorter than 30 simulated days offered for regime classification, as Amendment TG4-43 states.
        Pins: A run shorter than 30 simulated days is not classifiable as attacker winning under the final 30 day rule; its regime outcome is recorded as horizon insufficient, it contributes to no transition figure as a winning, holding, or crossed replicate, and its outcome class stands named beside the regime class counts at this group.
        Bar: A short run counted into any transition figure, or classified as attacker winning, fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a run shorter than 30 simulated days classified as attacker winning fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "run shorter than 30 simulated days recorded as horizon insufficient and contributing to no transition figure")
        m = _surface_module
        short = m.classify_run_outcome(20, "attacker winning")
        self.assertEqual(short["outcome"], "horizon insufficient")
        self.assertFalse(short["contributes_to_transition_figure"])
        full = m.classify_run_outcome(30, "attacker winning")
        self.assertEqual(full["outcome"], "attacker winning")
        self.assertTrue(full["contributes_to_transition_figure"])

    def test_one_outcome_per_replicate_and_denominator(self):
        """
        Fixture: F-18, at one control point with replicates started at that point, as Amendment M-20 states.
        Pins: For each control point, every replicate started at that point contributes exactly one recorded outcome by the run horizon: a first terminal regime observed at a daily evaluation, named by its regime class, or no terminal regime observed by the horizon, recorded as right censored at the horizon. The transition figure at a control point is the cumulative incidence of the attacker winning regime by the horizon, computed over all replicates started at that point, with the cumulative incidence of each other terminal regime and the share right censored beside it in the same unit, and the denominator rule stated on the report itself. Competing regime exits are counted as competing events and never as censoring. Where cumulative incidence by the horizon does not reach a stated band endpoint, no location for that endpoint is reported.
        Bar: A replicate contributing no outcome or two outcomes, a denominator other than all replicates started at the point, or a competing exit counted as censoring, fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a transition figure computed over any other denominator fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "one recorded outcome per replicate started at a control point, cumulative incidence over all started replicates, denominator rule stated on the report")
        m = _surface_module
        replicates = (
            [{"first_terminal_regime": "attacker winning"}] * 6
            + [{"first_terminal_regime": "defender holding"}] * 2
            + [{"first_terminal_regime": None}] * 1
            + [{"competing_exit": True}] * 1
        )
        figure = m.transition_figure(replicates)
        self.assertEqual(figure["denominator"], 10)
        self.assertEqual(figure["outcomes_per_replicate"], 1)
        self.assertEqual(
            figure["cumulative_incidence"]["attacker winning"]["count"], 6)
        self.assertEqual(
            figure["cumulative_incidence"]["attacker winning"]["share"], 0.6)
        self.assertEqual(figure["competing_events"], 1)
        self.assertEqual(figure["right_censored"]["count"], 1)
        self.assertIn("all replicates started at the point",
                      figure["denominator_rule"])
        self.assertIn("never as censoring", figure["denominator_rule"])
        self.assertIsNone(m.location_for_endpoint(
            figure, "attacker winning", 0.9))
        self.assertIsNotNone(m.location_for_endpoint(
            figure, "attacker winning", 0.5))

    def test_interval_time_form(self):
        """
        Fixture: F-18, with a regime condition first observed at a daily evaluation, as Amendment M-21 states.
        Pins: The time of a first observed terminal regime is recorded as the interval that runs from the previous daily evaluation to the daily evaluation at which it was first observed, and is never recorded or reported as an exact event time. No report splits the final 30 simulated days rule into an exact crossing day. The same interval form governs any first observed regime condition, and a condition first seen on the last day of a run has its interval closed only by the horizon.
        Bar: An exact event time, or an exact crossing day, recorded or reported for a first observed regime fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a first observed regime recorded as an exact event time fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "first observed regime recorded as the interval from the previous daily evaluation to the observing evaluation, never as an exact event time")
        m = _surface_module
        record = m.record_first_observed(4, 5, 30)
        self.assertEqual(tuple(record["interval"]), (4, 5))
        self.assertIsNone(record["exact_event_time"])
        self.assertTrue(m.validate_observation_time(record))
        last_day = m.record_first_observed(29, 30, 30, is_last_day=True)
        self.assertEqual(tuple(last_day["interval"]), (29, 30))
        exact = {"interval": (4, 5), "exact_event_time": 5}
        self.assertFalse(m.validate_observation_time(exact))

    def test_transition_reporting_watch_same_unit(self):
        """
        Fixture: F-18, one transition report unit inspected as a whole, as Amendment G5-C22 states.
        Pins: Every transition report states, in the same unit as the headline figure, the cumulative incidence of each terminal regime class by the stated horizon and the share of replicates right censored at that horizon, each labelled derived from the replicate counts in that unit, and every location sentence names its horizon.
        Bar: A transition report carrying any of these items outside the unit, unlabelled, or with a location sentence naming no horizon, fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.4 and this behaviour; a report missing the same unit carriage fails this test when the surface stands.
        """
        require_surface(self, "TG-13.4", "cumulative incidence per terminal regime class and censored share in the same unit as the headline figure, labelled derived, every location sentence naming its horizon")
        m = _surface_module
        replicates = (
            [{"first_terminal_regime": "attacker winning"}] * 5
            + [{"first_terminal_regime": None}] * 5
        )
        unit = {
            "headline_figure": 0.5,
            "transition_figure": m.transition_figure(replicates),
            "incidence_label": "derived from the replicate counts in this unit",
            "location_sentences": [
                "the region stands at the stated horizon of 60 days"],
        }
        self.assertTrue(m.validate_transition_unit(unit))
        self.assertIn("right_censored", unit["transition_figure"])
        self.assertIn("cumulative_incidence", unit["transition_figure"])
        no_horizon = dict(unit, location_sentences=[
            "the region stands at the stated point"])
        self.assertFalse(m.validate_transition_unit(no_horizon))
        unlabelled = dict(unit, incidence_label="stated")
        self.assertFalse(m.validate_transition_unit(unlabelled))


if __name__ == "__main__":
    unittest.main()

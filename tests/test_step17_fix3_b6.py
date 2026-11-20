"""Step 17 fix wave 3, Slice 6 defect tests: the mod05 Parley
core rows FW3-19, FW3-20, FW3-28, FW3-29, FW3-42, and FW3-61.

Each defect test reproduces the filing defect of its row on the
uncured tree: a count, score, bound, share, edge, or member
judged through a reading the handed value supplies, a share
above one returned or multiplied, a graph figure computed from
an unjudged edge, or a bare escape at the component door. Each
control test pins a standing that holds before and after the
cure alike. The aggregation surface stands in comparison form
only under DQ7-04 BLOCKED: no test adopts a rule and no test
rests a headline answer on the candidate.
"""
import unittest

from crucible import mod05


class AllTrueFloat(float):
    """A float subclass storing a plain float whose comparison
    readings all answer True, in the form the Round 2 Blue 5
    paper states: only its comparison readings lie."""

    def __ge__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return True

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = float.__hash__


class AllTrueInt(int):
    """An int subclass storing a plain int whose comparison
    readings all answer True."""

    def __ge__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __lt__(self, other):
        return True

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = int.__hash__


class RaisingEqMember:
    """A member whose hash reading returns a value and whose
    equality reading raises on every comparison, in the form
    the Round 2 Red 5 paper states at finding R5-F09."""

    def __hash__(self):
        return 42

    def __eq__(self, other):
        raise RuntimeError("hostile eq")

    def __ne__(self, other):
        raise RuntimeError("hostile eq")

    def __repr__(self):
        return "RaisingEqMember()"


class HashRaisingMember:
    """A member whose hash reading raises."""

    def __hash__(self):
        raise RuntimeError("hostile hash")


def mutual_pair(stake_a=10, stake_b=5):
    return [mod05.vouch("a", "b", stake_a), mod05.vouch("b", "a", stake_b)]


class TestFW319AggregationCountGuard(unittest.TestCase):
    """FW3-19, Medium, T17R2-19: the aggregation count guard
    judges a count on its stored form, never through a
    comparison or equality reading the handed value supplies,
    in comparison form only under DQ7-04 BLOCKED."""

    def test_defect_lying_negative_accepted_work_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "accepted_work": AllTrueFloat(-5.0),
                "penalties": 0,
            })
        self.assertIn("aggregate_reputation stands refused",
                      str(caught.exception))
        self.assertIn("accepted_work", str(caught.exception))

    def test_defect_lying_negative_stake_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "accepted_work": 1,
                "vouches_received": [{
                    "stake": AllTrueFloat(-2.0),
                    "score_bearing_flag": True,
                }],
            })
        self.assertIn("aggregate_reputation stands refused",
                      str(caught.exception))
        self.assertIn("stake", str(caught.exception))

    def test_defect_lying_negative_penalties_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "accepted_work": 10,
                "penalties": AllTrueFloat(-3.0),
            })
        self.assertIn("aggregate_reputation stands refused",
                      str(caught.exception))
        self.assertIn("penalties", str(caught.exception))

    def test_control_plain_negative_count_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "accepted_work": -5.0,
                "penalties": 0,
            })

    def test_control_lawful_inputs_score_in_comparison_form(self):
        result = mod05.aggregate_reputation({
            "agent_identifier": "a",
            "accepted_work": 3,
            "vouches_received": [{
                "stake": 2,
                "score_bearing_flag": True,
            }],
            "penalties": 1,
        })
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["form"], "comparison form only")
        self.assertEqual(result["adopted"], False)
        self.assertEqual(result["headline_use_permitted"], False)

    def test_control_lying_positive_count_scores_on_stored_form(self):
        result = mod05.aggregate_reputation({
            "agent_identifier": "a",
            "accepted_work": AllTrueFloat(5.0),
            "penalties": 0,
        })
        self.assertEqual(result["score"], 5.0)


class TestFW320BandMembership(unittest.TestCase):
    """FW3-20, Medium, T17R2-20: band_membership judges its
    score and minimum on their stored forms, and its
    band_standing sentence states the ground of the judgement
    actually made."""

    def test_defect_lying_score_reaches_no_high_band(self):
        result = mod05.band_membership(
            AllTrueFloat(0.0), [("low", 0.0), ("high", 10.0)],
            evaluation_order="O-1")
        self.assertEqual(result["band"], "low")
        self.assertEqual(
            result["band_standing"],
            "the score reaches the stated minimum of the "
            "band returned")

    def test_defect_lying_minimum_admits_no_band(self):
        result = mod05.band_membership(
            5.0, [("high", AllTrueFloat(100.0))],
            evaluation_order="O-1")
        self.assertIsNone(result["band"])
        self.assertEqual(
            result["band_standing"],
            "the score reaches no stated band minimum, and "
            "no band stands returned")

    def test_defect_two_lying_minimums_judged_on_stored_forms(self):
        result = mod05.band_membership(
            50.0,
            [("low", AllTrueFloat(10.0)),
             ("high", AllTrueFloat(100.0))],
            evaluation_order="O-1")
        self.assertEqual(result["band"], "low")

    def test_control_plain_score_takes_low_band(self):
        result = mod05.band_membership(
            0.0, [("low", 0.0), ("high", 10.0)],
            evaluation_order="O-1")
        self.assertEqual(result["band"], "low")

    def test_control_plain_score_below_minimum_takes_no_band(self):
        result = mod05.band_membership(
            5.0, [("high", 100.0)], evaluation_order="O-1")
        self.assertIsNone(result["band"])
        self.assertEqual(
            result["band_standing"],
            "the score reaches no stated band minimum, and "
            "no band stands returned")


class TestFW328GraphEdges(unittest.TestCase):
    """FW3-28, Medium, T17R2-28: the graph doors judge their
    edges in stated form, refusing a self vouch and a stake in
    negative or non finite form in named form before any
    figure stands computed."""

    def test_defect_self_vouch_refused_at_graph_snapshot(self):
        with self.assertRaises(ValueError) as caught:
            mod05.graph_snapshot([mod05.vouch("a", "a", 10)])
        self.assertIn("stands refused", str(caught.exception))

    def test_defect_self_vouch_refused_at_component(self):
        with self.assertRaises(ValueError):
            mod05.component([mod05.vouch("a", "a", 10)])

    def test_defect_negative_stake_refused_at_graph_snapshot(self):
        with self.assertRaises(ValueError):
            mod05.graph_snapshot(mutual_pair(-100, -100))

    def test_defect_nan_stake_refused_at_component(self):
        with self.assertRaises(ValueError):
            mod05.component(mutual_pair(float("nan"), float("nan")))

    def test_defect_infinite_stake_refused_at_component(self):
        with self.assertRaises(ValueError):
            mod05.component(mutual_pair(float("inf"), 1))

    def test_defect_self_vouch_refused_at_component_cap_check(self):
        with self.assertRaises(ValueError):
            mod05.component_cap_check([mod05.vouch("a", "a", 10)], 5)

    def test_defect_self_vouch_refused_at_feeder_position(self):
        with self.assertRaises(ValueError):
            mod05.feeder_position("a", [mod05.vouch("a", "a", 10)])

    def test_defect_self_vouch_refused_at_degree_distribution(self):
        with self.assertRaises(ValueError):
            mod05.realised_degree_distribution(
                [mod05.vouch("a", "a", 10)])

    def test_defect_text_stake_refused_at_component(self):
        with self.assertRaises(ValueError):
            mod05.component(mutual_pair("10", "5"))

    def test_defect_bool_stake_refused_at_component(self):
        with self.assertRaises(ValueError):
            mod05.component(mutual_pair(True, True))

    def test_defect_self_vouch_snapshot_fails_validation(self):
        edges = [mod05.vouch("a", "a", 10,
                             component_definition_version="v1")]
        snapshot = {
            "edge_list_reference": edges,
            "component_list": [{
                "members": ["a"], "member_count": 1,
                "edge_count": 1, "stake_total": 10,
            }],
            "largest_mutually_vouching_component_size": 1,
            "realised_degree_distribution": {"a": 2},
            "component_definition_version": "v1",
        }
        with self.assertRaises(ValueError):
            mod05.validate_graph_snapshot(snapshot, edges)

    def test_control_mutual_pair_computes(self):
        result = mod05.component(mutual_pair(10, 5))
        self.assertEqual(len(result["component_list"]), 1)
        entry = result["component_list"][0]
        self.assertEqual(entry["members"], ["a", "b"])
        self.assertEqual(entry["edge_count"], 2)
        self.assertEqual(entry["stake_total"], 15)
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 2)

    def test_control_snapshot_validates_against_its_edges(self):
        edges = [dict(edge, component_definition_version="v1")
                 for edge in mutual_pair(10, 5)]
        snapshot = mod05.graph_snapshot(
            edges, component_definition_version="v1")
        self.assertEqual(
            snapshot["largest_mutually_vouching_component_size"], 2)
        self.assertTrue(mod05.validate_graph_snapshot(snapshot, edges))

    def test_control_one_direction_vouch_forms_no_component(self):
        result = mod05.component([mod05.vouch("a", "b", 10)])
        self.assertEqual(result["component_list"], [])
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 0)

    def test_control_pair_naming_no_stake_computes_at_zero(self):
        result = mod05.component(mutual_pair(None, None))
        self.assertEqual(len(result["component_list"]), 1)
        self.assertEqual(result["component_list"][0]["stake_total"], 0)


class TestFW329GatePassingShare(unittest.TestCase):
    """FW3-29, Medium, T17R2-29: the gate passing share doors
    judge a share in the closed unit form, refusing a share
    above one in named form before it stands returned or
    multiplied."""

    def test_defect_count_share_above_one_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(3, 5)
        self.assertIn("gate_passing_share stands refused",
                      str(caught.exception))

    def test_defect_compute_share_above_one_refused(self):
        with self.assertRaises(ValueError):
            mod05.compute_share(2, 7)

    def test_defect_share_for_epoch_above_one_refused(self):
        with self.assertRaises(ValueError):
            mod05.share_for_epoch("e1", eligible=2, passing=7)

    def test_defect_lying_counts_judged_on_stored_forms(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(AllTrueInt(3), AllTrueInt(5))
        self.assertIn("passing count stands above the eligible",
                      str(caught.exception))

    def test_defect_score_bearing_figure_above_one_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.score_bearing_figure(
                100, {"numerator": 5, "denominator": 3})
        self.assertIn("score_bearing_figure stands refused",
                      str(caught.exception))

    def test_defect_population_figure_above_one_refused(self):
        with self.assertRaises(ValueError):
            mod05.population_figure(
                100, [{"numerator": 5, "denominator": 3}],
                record_state="stated")

    def test_control_count_share_inside_range_returned(self):
        share = mod05.gate_passing_share(4, 3)
        self.assertEqual(share["numerator"], 3)
        self.assertEqual(share["denominator"], 4)

    def test_control_share_at_one_returned(self):
        share = mod05.gate_passing_share(3, 3)
        self.assertEqual(share["numerator"], 3)
        self.assertEqual(share["denominator"], 3)

    def test_control_zero_eligible_stands_unknown(self):
        self.assertEqual(mod05.gate_passing_share(0, 0), "unknown")
        self.assertEqual(mod05.gate_passing_share(0, 5), "unknown")

    def test_control_identity_share_computes(self):
        share = mod05.compute_share(["a", "b"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_control_score_bearing_figure_inside_envelope(self):
        self.assertEqual(
            mod05.score_bearing_figure(
                100, {"numerator": 1, "denominator": 2}),
            50.0)
        self.assertEqual(
            mod05.score_bearing_figure(
                100, {"numerator": 3, "denominator": 3}),
            100.0)

    def test_control_population_figure_inside_envelope(self):
        result = mod05.population_figure(
            100, [{"numerator": 1, "denominator": 2}],
            record_state="stated")
        self.assertEqual(result["population_average"], 25.0)


class TestFW342EligibilityBounds(unittest.TestCase):
    """FW3-42, Low, T17R2-42: eligibility judges its bounds on
    their stored forms, refusing a bound in no judged form in
    named form."""

    def test_defect_lying_panel_minimum_judged_on_stored_form(self):
        result = mod05.eligibility(
            5.0, [("low", 0.0)], evaluation_order="O-1",
            panel_minimum=AllTrueFloat(100.0))
        self.assertEqual(result["panel_eligible"], False)

    def test_defect_lying_cap_maximum_judged_on_stored_form(self):
        result = mod05.eligibility(
            5.0, [("low", 0.0)], evaluation_order="O-1",
            cap_maximum=AllTrueFloat(0.0))
        self.assertEqual(result["cap_eligible"], False)

    def test_defect_text_panel_minimum_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.eligibility(
                5.0, [("low", 0.0)], evaluation_order="O-1",
                panel_minimum="high")
        self.assertIn("eligibility stands refused",
                      str(caught.exception))

    def test_defect_nan_cap_maximum_refused_named(self):
        with self.assertRaises(ValueError):
            mod05.eligibility(
                5.0, [("low", 0.0)], evaluation_order="O-1",
                cap_maximum=float("nan"))

    def test_defect_infinite_panel_minimum_refused_named(self):
        with self.assertRaises(ValueError):
            mod05.eligibility(
                5.0, [("low", 0.0)], evaluation_order="O-1",
                panel_minimum=float("inf"))

    def test_control_bounds_inside_forms_answer(self):
        result = mod05.eligibility(
            5.0, [("low", 0.0)], evaluation_order="O-1",
            panel_minimum=3.0, cap_maximum=10.0)
        self.assertEqual(result["band"], "low")
        self.assertEqual(result["panel_eligible"], True)
        self.assertEqual(result["cap_eligible"], True)

    def test_control_no_bounds_answer_eligible(self):
        result = mod05.eligibility(
            5.0, [("low", 0.0)], evaluation_order="O-1")
        self.assertEqual(result["panel_eligible"], True)
        self.assertEqual(result["cap_eligible"], True)

    def test_control_plain_bounds_outside_answer_not_eligible(self):
        result = mod05.eligibility(
            5.0, [("low", 0.0)], evaluation_order="O-1",
            panel_minimum=10.0, cap_maximum=2.0)
        self.assertEqual(result["panel_eligible"], False)
        self.assertEqual(result["cap_eligible"], False)


class TestFW361ComponentRaisingEquality(unittest.TestCase):
    """FW3-61, Low, T17R2-61: component delivers a member whose
    equality reading raises in the door named form, judging
    the member on its stored form. This class rests on the
    escape form at its handing and settles no carried FW-15
    limb."""

    def test_defect_raising_equality_member_computes(self):
        member = RaisingEqMember()
        edges = [mod05.vouch(member, "b", 1),
                 mod05.vouch("b", member, 1)]
        result = mod05.component(edges)
        self.assertEqual(len(result["component_list"]), 1)
        entry = result["component_list"][0]
        self.assertEqual(entry["member_count"], 2)
        self.assertEqual(entry["stake_total"], 2)
        self.assertEqual(
            result["largest_mutually_vouching_component_size"], 2)

    def test_defect_raising_equality_member_at_cap_check(self):
        member = RaisingEqMember()
        edges = [mod05.vouch(member, "b", 1),
                 mod05.vouch("b", member, 1)]
        self.assertTrue(mod05.component_cap_check(edges, 10))

    def test_control_plain_mutual_pair_computes(self):
        result = mod05.component(mutual_pair(10, 5))
        self.assertEqual(len(result["component_list"]), 1)
        self.assertEqual(result["component_list"][0]["stake_total"], 15)

    def test_control_hash_raising_member_refused_named(self):
        member = HashRaisingMember()
        edges = [mod05.vouch(member, "b", 1),
                 mod05.vouch("b", member, 1)]
        with self.assertRaises(ValueError) as caught:
            mod05.component(edges)
        self.assertIn("component stands refused",
                      str(caught.exception))


if __name__ == "__main__":
    unittest.main()

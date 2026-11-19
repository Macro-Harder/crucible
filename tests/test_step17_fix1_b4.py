"""Step 17 fix wave 1, Builder 4 (Slice 4) tests.

Rows: FW-03, FW-04, FW-06, FW-07, FW-08, FW-27.
Each defect test reproduces its filing defect on the base tree at
product head 9f938470807f90b7c8c6d9882fde1105c807e0a1 and passes
on the fixed tree. Control tests pass on both trees and stand
marked as controls in the builder paper.
"""
import unittest

from crucible import mod05, mod10


def _events():
    return [
        {"agent_identifier": "a1", "accepted": True},
        {"agent_identifier": "a1", "accepted": False},
        {"agent_identifier": "a2", "accepted": True},
    ]


def _components():
    return {
        "attacker_controlled_share": {
            "numerator": 3, "denominator": 10, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
        "farm_share_of_reputation_mass": {
            "numerator": 1.5, "denominator": 5.0, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "binary64 value",
            "denominator_kind": "binary64 value",
        },
        "largest_component_share": {
            "component_size": 4, "population_size": 10,
            "proportion": 0.4,
            "component_definition_version": "version in force",
            "viewer_identifier": "viewer-1",
            "component_size_kind": "integer count",
            "population_size_kind": "integer count",
        },
        "honest_loss_rate": {
            "numerator": 1, "denominator": 10, "rate": 0.1,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
    }


class IterList(list):
    """A dressed container: stored elements apart from the
    elements its own iteration yields."""

    def __init__(self, stored, fabricated):
        super().__init__(stored)
        self._fabricated = list(fabricated)

    def __iter__(self):
        return iter(self._fabricated)


class NoContainer:
    """A handed object in no container form: it stores no
    elements under the stored form doctrine."""

    def __init__(self, fabricated):
        self._fabricated = list(fabricated)

    def __iter__(self):
        return iter(self._fabricated)

    def __len__(self):
        return len(self._fabricated)


class TestFW03WorkCreditIterable(unittest.TestCase):
    def test_generator_events_computed(self):
        result = mod05.work_credit(e for e in _events())
        self.assertEqual(result["events_used"], 3)
        self.assertEqual(result["totals"]["submitted"], 3)
        self.assertEqual(result["totals"]["accepted"], 2)
        self.assertEqual(
            result["counters"]["a1"]["submitted"], 2)
        self.assertEqual(
            result["counters"]["a2"]["accepted"], 1)

    def test_iterator_events_computed(self):
        result = mod05.work_credit(iter(_events()))
        self.assertEqual(result["events_used"], 3)
        self.assertEqual(result["totals"]["accepted"], 2)

    def test_text_handing_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit("abc")
        self.assertIn("work_credit stands refused",
                      str(caught.exception))

    def test_single_record_handing_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit(
                {"agent_identifier": "a", "accepted": True})
        self.assertIn("work_credit stands refused",
                      str(caught.exception))

    def test_dict_of_events_refused_in_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.work_credit({"a1": 1, "a2": 2})
        self.assertIn("work_credit stands refused",
                      str(caught.exception))

    def test_dressed_container_pin_stands(self):
        fake = IterList(
            [], [{"agent_identifier": "ghost", "accepted": True}])
        result = mod05.work_credit(fake)
        self.assertEqual(result["events_used"], 0)
        self.assertEqual(result["counters"], {})

    def test_no_container_pin_stands(self):
        event = {"agent_identifier": "ghost", "accepted": True}
        result = mod05.work_credit(NoContainer([event]))
        self.assertNotIn("ghost", result.get("counters", {}))

    def test_list_control(self):
        result = mod05.work_credit(_events())
        self.assertEqual(result["events_used"], 3)
        self.assertEqual(result["totals"]["submitted"], 3)
        self.assertEqual(result["totals"]["accepted"], 2)


class TestFW04SameEventSet(unittest.TestCase):
    def test_same_event_set_true_only_over_read_events(self):
        result = mod05.work_credit(iter(_events()))
        self.assertTrue(result["same_event_set"])
        self.assertEqual(result["events_used"], 3)

    def test_no_false_true_on_refused_handings(self):
        for handing in ("abc",
                        {"agent_identifier": "a", "accepted": True},
                        {"a1": 1, "a2": 2}):
            with self.assertRaises(ValueError):
                mod05.work_credit(handing)

    def test_empty_list_control(self):
        result = mod05.work_credit([])
        self.assertEqual(result["events_used"], 0)
        self.assertTrue(result["same_event_set"])


class TestFW06ProportionForms(unittest.TestCase):
    def test_zero_denominator_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.proportion_record(5, 0)
        self.assertIn("proportion_record stands refused",
                      str(caught.exception))

    def test_negative_numerator_refused(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(-1, 2)

    def test_nan_numerator_refused(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(float("nan"), 2)

    def test_infinite_denominator_refused(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(1, float("inf"))

    def test_text_part_refused(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record("a", "b")

    def test_bool_part_refused(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(True, 2)

    def test_above_one_still_built(self):
        record = mod05.proportion_record(7, 2)
        self.assertEqual(record, {"numerator": 7, "denominator": 2})
        self.assertTrue(mod05.validate_proportion(record))

    def test_validator_huge_int_answers_false(self):
        self.assertFalse(mod05.validate_proportion(
            {"numerator": 10 ** 5000, "denominator": 1}))

    def test_validator_huge_int_denominator_answers_false(self):
        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": 10 ** 5000}))

    def test_validator_huge_int_quotient_answers_false(self):
        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": 1,
             "quotient": 10 ** 5000}))

    def test_missing_part_control(self):
        with self.assertRaises(ValueError):
            mod05.proportion_record(None, 2)
        with self.assertRaises(ValueError):
            mod05.proportion_record(1, None)

    def test_valid_proportion_control(self):
        record = mod05.proportion_record(1, 2)
        self.assertTrue(mod05.validate_proportion(record))


class TestFW07JointOutcomeVector(unittest.TestCase):
    def test_negative_rate_refused(self):
        components = _components()
        components["honest_loss_rate"] = {
            "numerator": -1, "denominator": 2, "rate": -0.5,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        }
        with self.assertRaises(ValueError) as caught:
            mod10.build_joint_outcome_vector(components=components)
        self.assertIn("joint outcome component in named form",
                      str(caught.exception))

    def test_negative_rate_with_matching_parts_refused(self):
        components = _components()
        components["honest_loss_rate"]["numerator"] = 1
        components["honest_loss_rate"]["denominator"] = 2
        components["honest_loss_rate"]["rate"] = -0.5
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=components)

    def test_disagreeing_proportion_refused(self):
        components = _components()
        components["attacker_controlled_share"]["proportion"] = 0.99
        with self.assertRaises(ValueError) as caught:
            mod10.build_joint_outcome_vector(components=components)
        self.assertIn("joint outcome component in named form",
                      str(caught.exception))

    def test_disagreeing_rate_refused(self):
        components = _components()
        components["honest_loss_rate"]["rate"] = 0.9
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=components)

    def test_disagreeing_largest_share_refused(self):
        components = _components()
        components["largest_component_share"]["proportion"] = 0.9
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(components=components)

    def test_above_one_proportion_still_built(self):
        components = _components()
        components["attacker_controlled_share"] = {
            "numerator": 5, "denominator": 2, "proportion": 2.5,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        }
        record = mod10.build_joint_outcome_vector(
            components=components)
        self.assertEqual(
            record["attacker_controlled_share"]["proportion"], 2.5)

    def test_valid_vector_control(self):
        record = mod10.build_joint_outcome_vector(
            components=_components(),
            divergence_companion={"nil_divergence_components": []})
        self.assertEqual(
            record["honest_loss_rate"]["rate"], 0.1)


class TestFW08AggregationCounts(unittest.TestCase):
    def test_nan_accepted_work_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "accepted_work": float("nan")})
        self.assertIn("aggregate_reputation stands refused",
                      str(caught.exception))

    def test_infinite_penalties_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a", "accepted_work": 0,
                "penalties": float("inf")})

    def test_negative_penalties_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a", "accepted_work": 0,
                "penalties": -100})

    def test_negative_accepted_work_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a", "accepted_work": -100,
                "penalties": 0})

    def test_negative_stake_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a", "accepted_work": 5,
                "vouches_received": [
                    {"stake": -1000, "score_bearing_flag": True}],
                "penalties": 1})

    def test_nan_stake_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a", "accepted_work": 1,
                "vouches_received": [
                    {"stake": float("nan"),
                     "score_bearing_flag": True}]})

    def test_infinite_stake_refused(self):
        with self.assertRaises(ValueError):
            mod05.aggregate_reputation({
                "agent_identifier": "a",
                "vouches_received": [
                    {"stake": float("inf"),
                     "score_bearing_flag": True}]})

    def test_wrappers_refuse_too(self):
        bad = {"agent_identifier": "a",
               "accepted_work": float("nan")}
        with self.assertRaises(ValueError):
            mod05.aggregation_score(bad)
        with self.assertRaises(ValueError):
            mod05.compare_aggregation(bad)

    def test_valid_aggregation_control(self):
        result = mod05.aggregate_reputation({
            "agent_identifier": "a", "accepted_work": 5,
            "vouches_received": [
                {"stake": 3, "score_bearing_flag": True}],
            "penalties": 1})
        self.assertEqual(result["score"], 7)


class TestFW27ShareDoors(unittest.TestCase):
    def test_count_form_delivered(self):
        share = mod05.compute_share(5, 3)
        self.assertEqual(share["numerator"], 3)
        self.assertEqual(share["denominator"], 5)

    def test_count_form_second(self):
        share = mod05.compute_share(10, 3)
        self.assertEqual(share["numerator"], 3)
        self.assertEqual(share["denominator"], 10)

    def test_count_form_zero_eligible_unknown(self):
        self.assertEqual(
            mod05.compute_share(0, 0), mod05.UNKNOWN_SHARE)

    def test_count_form_gate_door(self):
        share = mod05.gate_passing_share(4, 2, epoch="epoch-1")
        self.assertEqual(share["numerator"], 2)
        self.assertEqual(share["denominator"], 4)
        self.assertEqual(share["epoch"], "epoch-1")

    def test_negative_count_refused(self):
        with self.assertRaises(ValueError):
            mod05.compute_share(-5, 3)
        with self.assertRaises(ValueError):
            mod05.compute_share(5, -1)

    def test_mixed_form_refused(self):
        with self.assertRaises(ValueError):
            mod05.compute_share(5, ["a", "b", "c"])

    def test_duplicate_eligible_counted_once(self):
        share = mod05.gate_passing_share(["a", "a", "a"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 1)

    def test_duplicate_population_judged_as_identities(self):
        share = mod05.gate_passing_share(
            ["a", "a", "b"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_plain_share_control(self):
        share = mod05.gate_passing_share(["a", "b"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_empty_eligible_control(self):
        self.assertEqual(
            mod05.gate_passing_share([], []), mod05.UNKNOWN_SHARE)

    def test_dressed_eligible_pin_stands(self):
        dressed = IterList([], ["a", "b"])
        self.assertEqual(
            mod05.gate_passing_share(dressed, ["a"]),
            mod05.UNKNOWN_SHARE)


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 14, Builder 6, Group 6: rows R14-039 to
R14-048, the MOD-10 direct acts in the next ring (flag,
retention, storage, and aggregates), beside the MOD-14 shell
form of the flag act at row R14-039.

Each pin states the charged defect in stored form: a reading
the handed value supplies (truth, iteration, operator,
equality, containment, or item) standing in for the stored
contents, a missing identity or hash guard, a shared inputs
object, or a missing form guard. Every pin fails on the
pristine tree and passes on the cured tree, except the plain
controls, which pass on both.
"""

import unittest

from crucible import mod10, mod14


class LyingBoolList(list):
    """A list whose truth reading answers False whatever it
    stores."""

    def __bool__(self):
        return False


class LyingTrueBoolList(list):
    """A list whose truth reading answers True whatever it
    stores."""

    def __bool__(self):
        return True


class LyingIterList(list):
    """A list whose iteration yields values it does not store."""

    def __init__(self, stored, yielded):
        super().__init__(stored)
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


class AddLieInt(int):
    """An int whose addition reading returns a fixed large
    value."""

    def __add__(self, other):
        return 9999

    __radd__ = __add__


class LtLieInt(int):
    """An int whose less than reading always answers False."""

    def __lt__(self, other):
        return False


class MulLieInt(int):
    """An int whose multiplication reading returns a fixed
    large value."""

    def __mul__(self, other):
        return 9999

    __rmul__ = __mul__


class EqLie:
    """An object whose equality reading answers True against
    every value and whose inequality reading answers False."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class LyingContainsDict(dict):
    """A dict whose containment reading answers False for
    singular_vector and True for every other name, and whose
    item reading returns four numeric values for the component
    fields, whatever it stores."""

    def __contains__(self, key):
        return key != "singular_vector"

    def __getitem__(self, key):
        if key in ("joint_outcome_components",
                   "component_denominators"):
            return [1, 2, 3, 4]
        return dict.__getitem__(self, key)


def valid_delivery(day=1, viewer="viewer-1"):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 0,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0},
    }


class B6Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR14039FlagTruthReading(B6Base):
    def test_inputs_fired_list_judged_by_stored_contents(self):
        record = {
            "run_id": "b6-039a", "retention_tier": "Tier 1",
            "flag_conditions_fired": [],
        }
        result = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired":
                    LyingBoolList(["condition-1"])})
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_record_fired_list_judged_by_stored_contents(self):
        record = {
            "run_id": "b6-039b", "retention_tier": "Tier 1",
            "flag_conditions_fired": LyingBoolList(["condition-1"]),
        }
        result = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2", inputs={})
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_shell_fired_list_judged_by_stored_contents(self):
        record = {
            "run_id": "b6-039c", "retention_tier": "Tier 1",
            "flag_conditions_fired": [],
        }
        result = mod14.flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired":
                    LyingBoolList(["condition-1"])})
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_empty_stored_list_with_true_truth_still_refused(self):
        record = {
            "run_id": "b6-039d", "retention_tier": "Tier 1",
        }
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2",
                inputs={"flag_conditions_fired":
                        LyingTrueBoolList([])})

    def test_plain_promotion_control(self):
        record = {
            "run_id": "b6-039e", "retention_tier": "Tier 1",
        }
        result = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(result["retention_tier"], "Tier 2")


class TestR14040AggregateIterationReadings(B6Base):
    def test_fabricated_delivery_not_retained(self):
        deliveries = LyingIterList(
            [], [valid_delivery(day=99, viewer="fabricated")])
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-040a", deliveries)
        self.assertEqual(count, 0)

    def test_non_numeric_delivery_refused_on_stored_components(self):
        delivery = valid_delivery()
        delivery["joint_outcome_components"] = LyingIterList(
            ["not-a-number"], [1, 2, 3, 4])
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-040b", [delivery])
        self.assertIn("non numeric", str(caught.exception))

    def test_generator_of_valid_deliveries_retained(self):
        generator = (item for item in [valid_delivery()])
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-040c", generator)
        self.assertEqual(count, 1)
        aggregates = mod10.daily_aggregates_for_run("b6-040c")
        self.assertEqual(aggregates[0]["viewer_id"], "viewer-1")


class TestR14041AggregateNonRecordDelivery(B6Base):
    def test_text_delivery_alone_does_not_crash(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-041a", ["junk"])
        self.assertEqual(count, 0)

    def test_number_delivery_alone_does_not_crash(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-041b", [123])
        self.assertEqual(count, 0)

    def test_valid_delivery_before_junk_stands_retained(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-041c", [valid_delivery(), "junk"])
        self.assertEqual(count, 1)


class TestR14042StorageCountOperatorReadings(B6Base):
    def test_accounting_uses_stored_counts(self):
        result = mod10.storage_accounting({
            "summaries": AddLieInt(1),
            "daily_snapshots": 2,
            "event_logs": 3,
            "checkpoints": 0,
            "held_corpus_copies": 0,
        })
        self.assertEqual(result["result_count"], 6)

    def test_negative_count_refused_on_stored_value(self):
        with self.assertRaises(ValueError) as caught:
            mod10.storage_accounting({"summaries": LtLieInt(-5)})
        self.assertIn("negative", str(caught.exception))

    def test_c10_count_uses_stored_counts(self):
        total = mod10.checkpoint_count_c10([
            {"retained_per_run": MulLieInt(2), "runs": 3},
        ])
        self.assertEqual(total, 6)


class TestR14043StorageTotalEqualityReading(B6Base):
    def test_result_count_judged_by_stored_value(self):
        claimed = {
            "summaries": 1, "daily_snapshots": 2, "event_logs": 3,
            "result_count": EqLie(),
        }
        self.assertFalse(mod10.validate_storage_accounting(claimed))

    def test_checkpoint_count_judged_by_stored_value(self):
        claimed = {
            "summaries": 0, "daily_snapshots": 0, "event_logs": 0,
            "result_count": 0,
            "checkpoints": 1, "held_corpus_copies": 1,
            "checkpoint_count": EqLie(),
        }
        self.assertFalse(mod10.validate_storage_accounting(claimed))

    def test_correct_plain_claim_control(self):
        claimed = {
            "summaries": 1, "daily_snapshots": 2, "event_logs": 3,
            "result_count": 6,
            "checkpoints": 1, "held_corpus_copies": 1,
            "checkpoint_count": 2,
        }
        self.assertTrue(mod10.validate_storage_accounting(claimed))


class TestR14044SummaryIdentityGuard(B6Base):
    def test_identity_less_summary_record_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.write_summary_record({"retention_tier": "Tier 1"})
        self.assertIn("no run identifier", str(caught.exception))
        found = mod10.summary_record_for_run(None)
        self.assertEqual(found.get("record_found"), False)

    def test_second_identity_less_record_also_refused(self):
        with self.assertRaises(ValueError):
            mod10.write_summary_record(
                {"retention_tier": "Tier 1", "marker": "first"})
        with self.assertRaises(ValueError):
            mod10.write_summary_record(
                {"retention_tier": "Tier 3", "marker": "second"})
        found = mod10.summary_record_for_run(None)
        self.assertEqual(found.get("record_found"), False)


class TestR14045RetentionHashGuards(B6Base):
    def test_event_log_entry_unhashable_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_event_log_entry({"run_id": {"a": 1}})
        self.assertIn("unhashable", str(caught.exception))

    def test_event_log_entry_list_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_event_log_entry({"run_id": ["x"]})
        self.assertIn("unhashable", str(caught.exception))

    def test_daily_snapshot_list_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_snapshot({"run_id": ["x"]})
        self.assertIn("unhashable", str(caught.exception))

    def test_checkpoint_list_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint({"run_id": ["x"]})
        self.assertIn("unhashable", str(caught.exception))

    def test_summary_record_mapping_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.write_summary_record({"run_id": {"a": 1}})
        self.assertIn("unhashable", str(caught.exception))


class TestR14046DailyAggregatesValidatorReadings(B6Base):
    def test_aggregate_judged_by_stored_contents(self):
        record = LyingContainsDict({
            "joint_outcome_components": "x",
            "component_denominators": "y",
        })
        self.assertFalse(mod10.validate_daily_aggregates([record]))

    def test_plain_valid_aggregate_control(self):
        record = {
            "viewer_id": "viewer-1",
            "joint_outcome_components": [1, 2, 3, 4],
            "component_denominators": [1, 1, 1, 1],
        }
        self.assertTrue(mod10.validate_daily_aggregates([record]))


class TestR14047SharedInputsCopy(B6Base):
    def test_flag_returned_inputs_not_the_handed_object(self):
        inputs = {
            "flag_conditions_fired": ["condition-1"],
            "extra": [1],
        }
        result = mod10.apply_flag_evaluation(
            {"run_id": "b6-047a", "retention_tier": "Tier 1"},
            outcome="promote", tier="Tier 2", inputs=inputs)
        returned = result["flag_evaluation"]["inputs"]
        self.assertIsNot(returned, inputs)
        inputs["flag_conditions_fired"].append("condition-2")
        inputs["new_key"] = "mutated"
        self.assertEqual(returned, {
            "flag_conditions_fired": ["condition-1"],
            "extra": [1],
        })

    def test_deferred_returned_inputs_not_the_handed_object(self):
        inputs = {"firing_marker": [1]}
        result = mod10.apply_deferred_evaluation(
            {"run_id": "b6-047b", "retention_tier": "Tier 1"},
            1, inputs=inputs, outcome="held")
        entry = result["deferred_evaluations"][-1]
        self.assertIsNot(entry["inputs"], inputs)
        inputs["firing_marker"].append(2)
        inputs["new_key"] = "mutated"
        self.assertEqual(entry["inputs"], {"firing_marker": [1]})


class TestR14048RetentionMetFormGuard(B6Base):
    def test_text_record_returns_false(self):
        self.assertFalse(mod10.retention_met("text"))

    def test_number_record_returns_false(self):
        self.assertFalse(mod10.retention_met(123))

    def test_none_record_returns_false(self):
        self.assertFalse(mod10.retention_met(None))


if __name__ == "__main__":
    unittest.main()

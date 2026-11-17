"""Step 15, second run, fix wave 20, Builder 2 pins.

Group 2: the MOD-10 reading, copy, deferred, and rendering
family, under settlements S-1, S-2, and S-16. Rows R20-010,
R20-012, R20-062, R20-063, R20-064, R20-065, R20-066,
R20-067, and R20-068. Each distinguishing pin hands the
charged act a value whose own string, repr, or hash reading
must not be trusted, or mutates a handed outcome after the
act, beside plain controls whose standing the cure keeps.
"""
import math
import unittest

import crucible.mod10 as mod10


class LieStr(str):
    """A text value storing one text whose string and repr
    readings return a stated different word."""

    def __new__(cls, stored, lie):
        value = str.__new__(cls, stored)
        value._lie = lie
        return value

    def __str__(self):
        return self._lie

    def __repr__(self):
        return self._lie


class RaiseStr(str):
    """A text value storing one text whose string and repr
    readings each raise RuntimeError."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class LieRepr:
    """A plain object whose repr and string readings return a
    stated different text."""

    def __init__(self, lie):
        self._lie = lie

    def __repr__(self):
        return self._lie

    def __str__(self):
        return self._lie


class LieFloatRepr(float):
    """A float value storing one number whose repr reading
    returns a stated different text."""

    def __new__(cls, stored, lie):
        value = float.__new__(cls, stored)
        value._lie = lie
        return value

    def __repr__(self):
        return self._lie


class HashRaiseStr(str):
    """A text value storing one text whose hash reading raises
    the stated exception kind."""

    def __new__(cls, stored, exc):
        value = str.__new__(cls, stored)
        value._exc = exc
        return value

    def __hash__(self):
        raise self._exc("hash reading raises")


def delivery(viewer, components):
    return {
        "simulated_day": 1,
        "viewer_id": viewer,
        "joint_outcome_components": components,
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 1,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 1},
    }


class TestR20062LookupFailureRunLimb(unittest.TestCase):

    def test_lie_run_names_stored_run(self):
        failure = mod10.LookupFailure(LieStr("run-x", "run-y"))
        self.assertEqual(
            failure.args[0], "one lookup resolution failure: run-x")

    def test_raise_run_names_stored_run(self):
        failure = mod10.LookupFailure(RaiseStr("run-x"))
        self.assertEqual(
            failure.args[0], "one lookup resolution failure: run-x")

    def test_bytes_run_names_stored_text(self):
        failure = mod10.LookupFailure(b"run-x")
        self.assertEqual(
            failure.args[0], "one lookup resolution failure: run-x")

    def test_control_plain_run(self):
        failure = mod10.LookupFailure("run-x")
        self.assertEqual(
            failure.args[0], "one lookup resolution failure: run-x")
        self.assertEqual(failure.run_id, "run-x")


class TestR20063LookupFailureKindLimb(unittest.TestCase):

    def test_lie_kind_names_stored_kind(self):
        failure = mod10.LookupFailure(
            "run-x", record_kind=LieStr("kind-a", "kind-b"))
        self.assertEqual(
            failure.args[0],
            "one lookup resolution failure: run-x "
            "for record kind kind-a")

    def test_raise_kind_names_stored_kind(self):
        failure = mod10.LookupFailure(
            "run-x", record_kind=RaiseStr("kind-a"))
        self.assertEqual(
            failure.args[0],
            "one lookup resolution failure: run-x "
            "for record kind kind-a")

    def test_bytes_kind_names_stored_text(self):
        failure = mod10.LookupFailure("run-x", record_kind=b"kind-a")
        self.assertEqual(
            failure.args[0],
            "one lookup resolution failure: run-x "
            "for record kind kind-a")

    def test_control_plain_kind(self):
        failure = mod10.LookupFailure("run-x", record_kind="kind-a")
        self.assertEqual(
            failure.args[0],
            "one lookup resolution failure: run-x "
            "for record kind kind-a")


class TestR20064UnknownStoreKind(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_new_store_lie_kind_names_stored_kind(self):
        with self.assertRaises(ValueError) as caught:
            mod10.new_store(LieStr("bogus-kind", "sweep"))
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_retain_lie_kind_names_stored_kind(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_run_record(
                {"run_id": "r20-064-a"}, LieStr("bogus-kind", "sweep"))
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_construction_lie_kind_names_stored_kind(self):
        with self.assertRaises(ValueError) as caught:
            mod10.RecorderStore(
                store_kind=LieStr("bogus-kind", "sweep"))
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_new_store_raise_kind_names_stored_kind(self):
        with self.assertRaises(ValueError) as caught:
            mod10.new_store(RaiseStr("bogus-kind"))
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_new_store_bytes_kind_names_stored_text(self):
        with self.assertRaises(ValueError) as caught:
            mod10.new_store(b"bogus-kind")
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_control_plain_unknown_kind(self):
        with self.assertRaises(ValueError) as caught:
            mod10.new_store("bogus-kind")
        self.assertIn(
            "unknown store kind: bogus-kind", str(caught.exception))

    def test_control_known_kind_creates_store(self):
        store = mod10.new_store("sweep")
        self.assertEqual(store.store_kind, "sweep")


class TestR20065ViewerLimb(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_lie_viewer_names_stored_viewer(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-065-a",
                [delivery(LieStr("viewer-a", "viewer-b"),
                          ["bogus-comp"])])
        self.assertIn(
            "for viewer viewer-a at day 1", str(caught.exception))

    def test_raise_viewer_names_stored_viewer(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-065-b",
                [delivery(RaiseStr("viewer-a"), ["bogus-comp"])])
        self.assertIn(
            "for viewer viewer-a at day 1", str(caught.exception))

    def test_bytes_viewer_names_stored_text(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-065-c",
                [delivery(b"viewer-a", ["bogus-comp"])])
        self.assertIn(
            "for viewer viewer-a at day 1", str(caught.exception))

    def test_control_plain_viewer(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-065-d", [delivery("viewer-a", ["bogus-comp"])])
        self.assertIn(
            "for viewer viewer-a at day 1", str(caught.exception))

    def test_control_numeric_delivery_retained(self):
        count = mod10.retain_daily_aggregate_deliveries(
            "r20-065-e", [delivery("viewer-a", [1, 1, 1, 1])])
        self.assertEqual(count, 1)


class TestR20066ComponentLimb(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_lie_repr_component_not_named_by_its_lie(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-066-a", [delivery("viewer-a", [LieRepr("7")])])
        message = str(caught.exception)
        self.assertIn("stand in a non numeric form (component ",
                      message)
        self.assertNotIn("(component 7)", message)
        self.assertIn("LieRepr", message)

    def test_lie_float_component_names_stored_number(self):
        handed = LieFloatRepr(math.inf, "9")
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-066-b", [delivery("viewer-a", [handed])])
        message = str(caught.exception)
        self.assertIn("non finite numeric form (component inf)",
                      message)
        self.assertNotIn("(component 9)", message)

    def test_lie_str_component_names_stored_text_in_repr_dress(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-066-c",
                [delivery("viewer-a", [LieStr("bogus-comp", "7")])])
        self.assertIn(
            "(component 'bogus-comp')", str(caught.exception))

    def test_control_plain_text_component(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-066-d", [delivery("viewer-a", ["bogus-comp"])])
        self.assertIn(
            "(component 'bogus-comp')", str(caught.exception))

    def test_control_plain_infinite_component(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "r20-066-e", [delivery("viewer-a", [math.inf])])
        self.assertIn(
            "non finite numeric form (component inf)",
            str(caught.exception))


class TestR20067SecondCheckpointRefusal(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_lie_run_names_stored_run(self):
        manifest = {
            "run_identifier": LieStr("run-z9", "run-a1"),
            "simulated_day": 4,
        }
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "rejected: run-z9 day 4", str(caught.exception))

    def test_raise_run_names_stored_run(self):
        manifest = {
            "run_identifier": RaiseStr("run-z9"),
            "simulated_day": 4,
        }
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "rejected: run-z9 day 4", str(caught.exception))

    def test_bytes_run_names_stored_text(self):
        manifest = {
            "run_identifier": b"run-z9",
            "simulated_day": 4,
        }
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "rejected: run-z9 day 4", str(caught.exception))

    def test_control_plain_run_pair(self):
        manifest = {"run_identifier": "run-cp", "simulated_day": 3}
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_checkpoint(dict(manifest))
        self.assertIn(
            "rejected: run-cp day 3", str(caught.exception))


class TestR20068PositionWording(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_lie_repr_position_not_named_by_its_lie(self):
        result = mod10.checkpoint_position_check({
            "run_identifier": "r20-068-a",
            "journal_position": LieRepr("7"),
        })
        self.assertIn("stands in no integer form", result["outcome"])
        self.assertNotIn("form: 7,", result["outcome"])
        self.assertIn("LieRepr", result["outcome"])
        self.assertFalse(result["reportable"])

    def test_lie_str_position_names_stored_text_in_repr_dress(self):
        result = mod10.checkpoint_position_check({
            "run_identifier": "r20-068-b",
            "journal_position": LieStr("bogus-pos", "7"),
        })
        self.assertIn(
            "stands in no integer form: 'bogus-pos'",
            result["outcome"])
        self.assertFalse(result["reportable"])

    def test_control_plain_text_position(self):
        result = mod10.checkpoint_position_check({
            "run_identifier": "r20-068-c",
            "journal_position": "bogus-pos",
        })
        self.assertIn(
            "stands in no integer form: 'bogus-pos'",
            result["outcome"])
        self.assertFalse(result["reportable"])

    def test_control_plain_integer_position_outside_log(self):
        result = mod10.checkpoint_position_check({
            "run_identifier": "r20-068-d",
            "journal_position": 5,
        })
        self.assertTrue(
            result["outcome"].startswith("retention failure"))
        self.assertFalse(result["reportable"])


class TestR20010OutcomeCopy(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_outcome_dict_mutation_after_act(self):
        outcome = {"verdict": "pending", "detail": {"score": 1}}
        returned = mod10.apply_deferred_evaluation(
            {"run_id": "r20-010-a"}, 1,
            inputs={"a": 1}, outcome=outcome)
        outcome["verdict"] = "rewritten"
        outcome["detail"]["score"] = 99
        written = returned["deferred_evaluations"][0]["outcome"]
        self.assertEqual(written["verdict"], "pending")
        self.assertEqual(written["detail"]["score"], 1)

    def test_delivered_and_stored_records_agree(self):
        outcome = {"verdict": "pending"}
        returned = mod10.apply_deferred_evaluation(
            {"run_id": "r20-010-b"}, 1,
            inputs={"a": 1}, outcome=outcome)
        outcome["verdict"] = "rewritten"
        stored = mod10.summary_record_for_run("r20-010-b")
        self.assertEqual(
            stored["deferred_evaluations"][0]["outcome"],
            returned["deferred_evaluations"][0]["outcome"])
        self.assertEqual(
            stored["deferred_evaluations"][0]["outcome"]["verdict"],
            "pending")

    def test_outcome_list_mutation_after_act(self):
        outcome = ["pending", ["x"]]
        returned = mod10.apply_deferred_evaluation(
            {"run_id": "r20-010-c"}, 1,
            inputs={"a": 1}, outcome=outcome)
        outcome[0] = "rewritten"
        outcome[1].append("y")
        outcome.append("z")
        self.assertEqual(
            returned["deferred_evaluations"][0]["outcome"],
            ["pending", ["x"]])

    def test_control_inputs_copied_and_scalar_outcome(self):
        inputs = {"a": [1]}
        returned = mod10.apply_deferred_evaluation(
            {"run_id": "r20-010-d"}, 1,
            inputs=inputs, outcome="done")
        inputs["a"].append(2)
        written = returned["deferred_evaluations"][0]
        self.assertEqual(written["inputs"], {"a": [1]})
        self.assertEqual(written["outcome"], "done")


class TestR20012HashRaisingReadings(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_aggregate_manifest_runtime_hash(self):
        run_id = HashRaiseStr("run-h", RuntimeError)
        result = mod10.aggregate_manifest_for_run(run_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)
        self.assertIs(result[0]["run_id"], run_id)

    def test_aggregate_manifest_value_hash(self):
        run_id = HashRaiseStr("run-h", ValueError)
        result = mod10.aggregate_manifest_for_run(run_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)

    def test_daily_aggregates_runtime_hash(self):
        run_id = HashRaiseStr("run-h", RuntimeError)
        result = mod10.daily_aggregates_for_run(run_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)

    def test_daily_aggregates_value_hash(self):
        run_id = HashRaiseStr("run-h", ValueError)
        result = mod10.daily_aggregates_for_run(run_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)

    def test_gate_shares_runtime_hash(self):
        run_id = HashRaiseStr("run-h", RuntimeError)
        self.assertEqual(
            mod10.gate_passing_shares_for_run(run_id), {})

    def test_gate_shares_value_hash(self):
        run_id = HashRaiseStr("run-h", ValueError)
        self.assertEqual(
            mod10.gate_passing_shares_for_run(run_id), {})

    def test_checkpoint_state_runtime_hash(self):
        run_id = HashRaiseStr("run-h", RuntimeError)
        self.assertIsNone(mod10.checkpoint_state_at(run_id, 1))

    def test_checkpoint_state_value_hash(self):
        run_id = HashRaiseStr("run-h", ValueError)
        self.assertIsNone(mod10.checkpoint_state_at(run_id, 1))

    def test_control_plain_absent_aggregates_and_shares(self):
        result = mod10.aggregate_manifest_for_run("run-absent")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)
        self.assertEqual(
            mod10.gate_passing_shares_for_run("run-absent"), {})

    def test_control_plain_absent_daily_and_state(self):
        result = mod10.daily_aggregates_for_run("run-absent")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["form"], mod10.FORM_ONLY)
        self.assertIsNone(
            mod10.checkpoint_state_at("run-absent", 1))

    def test_control_plain_present_aggregates(self):
        mod10.retain_daily_aggregate_deliveries(
            "run-present", [delivery("viewer-a", [1, 1, 1, 1])])
        manifest = mod10.aggregate_manifest_for_run("run-present")
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["viewer_id"], "viewer-a")
        records = mod10.daily_aggregates_for_run("run-present")
        self.assertEqual(records[0]["viewer_id"], "viewer-a")
        self.assertNotIn("form", records[0])

    def test_control_plain_present_shares_and_state(self):
        mod10.record_gate_passing_share(
            "run-present", "epoch-1", 1, simulated_day=1)
        shares = mod10.gate_passing_shares_for_run("run-present")
        self.assertEqual(len(shares), 1)
        mod10.retain_checkpoint({
            "run_identifier": "run-present",
            "simulated_day": 2,
            "checkpoint_state": {"marker": "state-1"},
        })
        state = mod10.checkpoint_state_at("run-present", 2)
        self.assertEqual(state, {"marker": "state-1"})


if __name__ == "__main__":
    unittest.main()

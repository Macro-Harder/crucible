"""Pin tests for fix wave 10, Builder 4, MOD-04 rows R10-001
(MOD-04 limb), R10-007 (MOD-04 limb), R10-008, R10-020, R10-021,
R10-022, R10-026, R10-027, R10-028, and R10-053 (MOD-04 limb).

Each test states its distinguishing case with controls both
ways: the dressed form the register charges, the plain form that
already stands refused or accepted, and a clean form that must
keep its standing.
"""

import unittest

from crucible import mod04
from crucible import mod10


def chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def tuple_chain(count, leaf):
    value = leaf
    for _ in range(count):
        value = (value,)
    return value


class ReportingBytes(bytes):
    """A bytes value storing one content whose string reading
    reports another word."""

    def __new__(cls, stored, reported):
        obj = super().__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class LyingLeaf:
    """A leaf whose copy protocol materialises another value
    and whose deepcopy protocol can be told to raise."""

    def __init__(self, raising=False):
        self._raising = raising

    def __deepcopy__(self, memo):
        if self._raising:
            raise RuntimeError("boom from copy protocol")
        return "materialised-other-value"

    def __copy__(self):
        return "materialised-other-value"


class LyingGetDict(dict):
    """A dict subclass storing plain contents whose get reading
    reports other contents, or raises."""

    def __init__(self, stored, reported=None, raising=False):
        super().__init__(stored)
        self._reported = reported or {}
        self._raising = raising

    def get(self, key, default=None):
        if self._raising:
            raise RuntimeError("boom from get reading")
        if key in self._reported:
            return self._reported[key]
        return super().get(key, default)


def manifest(run_id="run-b4-ckpt", day=3):
    return {
        "run_identifier": run_id,
        "run_id": run_id,
        "simulated_day": day,
    }


def parts():
    return {
        "agent_states": [{"agent_identifier": "agent-1"}],
        "escrow_contract_states": [],
        "detection_state": {"state": "stated"},
        "stream_positions_and_generator_states": {
            "stream-1": {"position": 1}},
        "simulation_clock_value": 3,
    }


class CheckpointBase(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR10001BytesStoredText(unittest.TestCase):

    def test_bytes_value_reads_as_its_decoded_stored_text(self):
        self.assertEqual(mod04._stored_text(b"membership"), "membership")
        self.assertEqual(mod04._stored_text(b"activity"), "activity")

    def test_bare_bytes_barred_names_stand_barred(self):
        for key in (b"membership", b"canary", b"ground_truth"):
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_bare_bytes_clean_name_stands_admitted(self):
        self.assertFalse(mod04._is_barred_key(b"activity"))

    def test_bytes_subclass_judged_by_stored_bytes_not_its_reading(self):
        key = ReportingBytes(b"membership", "figure")
        self.assertEqual(mod04._stored_text(key), "membership")
        self.assertTrue(mod04._is_barred_key(key))
        mirror = ReportingBytes(b"activity", "membership")
        self.assertEqual(mod04._stored_text(mirror), "activity")
        self.assertFalse(mod04._is_barred_key(mirror))

    def test_undecodable_bytes_dropped_from_the_reading(self):
        self.assertEqual(
            mod04._stored_text(b"member\xffship"), "membership")
        self.assertTrue(mod04._is_barred_key(b"member\xffship"))

    def test_bytes_part_inside_a_container_key_stands_barred(self):
        self.assertTrue(mod04._is_barred_key((b"ground_truth",)))
        self.assertTrue(mod04._is_barred_key(("outer", (b"canary",))))
        self.assertFalse(mod04._is_barred_key((b"activity",)))

    def test_bytes_parts_split_across_one_container_key_stand_barred(self):
        self.assertTrue(mod04._is_barred_key((b"member", b"ship")))
        self.assertFalse(mod04._is_barred_key((b"acti", b"vity")))

    def test_bytes_keys_stripped_from_the_projection_at_any_depth(self):
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {
                (b"ground_truth",): 1,
                "outer": {b"ground_truth": 1, "ok": 2},
                "ok": 3,
            },
            "rule_records": [],
        }
        projected = mod04.project_detection_input(state)
        self.assertEqual(
            projected["feature_values"], {"outer": {"ok": 2}, "ok": 3})

    def test_control_plain_text_standings_kept(self):
        self.assertTrue(mod04._is_barred_key("membership"))
        self.assertFalse(mod04._is_barred_key("activity"))
        self.assertEqual(mod04._stored_text(123), "")


class TestR10007MemoryviewAndBytearray(unittest.TestCase):

    def test_memoryview_reads_as_its_decoded_stored_text(self):
        self.assertEqual(
            mod04._stored_text(memoryview(b"membership")), "membership")

    def test_memoryview_barred_names_stand_barred(self):
        self.assertTrue(mod04._is_barred_key(memoryview(b"membership")))
        self.assertTrue(mod04._is_barred_key(memoryview(b"canary")))
        self.assertFalse(mod04._is_barred_key(memoryview(b"activity")))

    def test_memoryview_key_bars_a_view_record(self):
        record = {memoryview(b"ground_truth"): "x"}
        self.assertTrue(mod04.view_record_carries_barred_field(record))
        clean = {memoryview(b"activity"): "x"}
        self.assertFalse(mod04.view_record_carries_barred_field(clean))

    def test_memoryview_part_inside_a_container_key_stands_barred(self):
        self.assertTrue(
            mod04._is_barred_key((memoryview(b"ground_truth"),)))

    def test_bytearray_reads_as_its_decoded_stored_text(self):
        self.assertEqual(
            mod04._stored_text(bytearray(b"canary")), "canary")
        self.assertTrue(mod04._is_barred_key(bytearray(b"canary")))
        self.assertFalse(mod04._is_barred_key(bytearray(b"activity")))

    def test_bytearray_parts_split_across_a_container_stand_barred(self):
        key = (bytearray(b"member"), bytearray(b"ship"))
        self.assertTrue(mod04._is_barred_key(key))


class TestR10008DeepContainerKey(unittest.TestCase):

    def test_tuple_key_at_depth_2000_barred_leaf_answers_true(self):
        self.assertTrue(mod04._is_barred_key(tuple_chain(2000, "membership")))

    def test_tuple_key_at_depth_2000_clean_leaf_answers_false(self):
        self.assertFalse(mod04._is_barred_key(tuple_chain(2000, "activity")))

    def test_tuple_key_at_depth_500_answers_at_the_public_act(self):
        record = {tuple_chain(500, "membership"): 1}
        self.assertTrue(mod04.view_record_carries_barred_field(record))
        clean = {tuple_chain(500, "activity"): 1}
        self.assertFalse(mod04.view_record_carries_barred_field(clean))

    def test_cyclic_container_key_answers_without_a_bare_error(self):
        value = []
        value.append(value)
        self.assertFalse(mod04._is_barred_key(value))


class TestR10020CheckpointCopyAndClock(CheckpointBase):

    def test_clock_list_stands_copied_in_the_returned_state(self):
        clock = ["tick", ["nested"]]
        handed = parts()
        handed["simulation_clock_value"] = clock
        result = mod04.write_checkpoint(manifest(), **handed)
        clock.append("MUT")
        clock[1].append("MUT")
        self.assertEqual(
            result["checkpoint_state"]["simulation_clock_value"],
            ["tick", ["nested"]])
        self.assertEqual(
            mod10.checkpoint_state_at("run-b4-ckpt", 3),
            result["checkpoint_state"])

    def test_lying_copy_leaf_stands_as_itself_in_every_form(self):
        leaf = LyingLeaf()
        handed = parts()
        handed["simulation_clock_value"] = leaf
        result = mod04.write_checkpoint(manifest(), **handed)
        self.assertIs(result["checkpoint_state"]["simulation_clock_value"], leaf)
        self.assertIs(
            result["manifest"]["checkpoint_state"]["simulation_clock_value"],
            leaf)
        retained = mod10.checkpoints_for_run("run-b4-ckpt")
        self.assertIs(
            retained[0]["checkpoint_state"]["simulation_clock_value"],
            leaf)

    def test_lying_copy_leaf_nested_in_a_part_stands_as_itself(self):
        leaf = LyingLeaf()
        handed = parts()
        handed["agent_states"] = [{"leaf": leaf}]
        result = mod04.write_checkpoint(manifest(), **handed)
        self.assertIs(
            result["checkpoint_state"]["agent_states"][0]["leaf"], leaf)
        retained = mod10.checkpoints_for_run("run-b4-ckpt")
        self.assertIs(
            retained[0]["checkpoint_state"]["agent_states"][0]["leaf"],
            leaf)

    def test_raising_copy_leaf_does_not_escape_the_act(self):
        leaf = LyingLeaf(raising=True)
        handed = parts()
        handed["simulation_clock_value"] = leaf
        result = mod04.write_checkpoint(manifest(), **handed)
        self.assertIs(result["checkpoint_state"]["simulation_clock_value"], leaf)


class TestR10021CheckpointIdentityReading(CheckpointBase):

    def test_identity_comes_from_the_stored_manifest_contents(self):
        lying = LyingGetDict(
            manifest("stored-run", 1),
            reported={"run_identifier": "fabricated-run",
                      "run_id": "fabricated-run",
                      "simulated_day": 99})
        result = mod04.write_checkpoint(lying, **parts())
        state = result["checkpoint_state"]
        self.assertEqual(state["run_identifier"], "stored-run")
        self.assertEqual(state["simulated_day"], 1)
        self.assertIsNotNone(mod10.checkpoint_state_at("stored-run", 1))
        self.assertEqual(mod10.checkpoints_for_run("fabricated-run"), [])

    def test_raising_get_does_not_escape_the_act(self):
        raising = LyingGetDict(manifest("stored-run", 1), raising=True)
        result = mod04.write_checkpoint(raising, **parts())
        self.assertEqual(
            result["checkpoint_state"]["run_identifier"], "stored-run")
        self.assertEqual(result["checkpoint_state"]["simulated_day"], 1)


class TestR10022EventFeatureUpdateReading(unittest.TestCase):

    def test_feature_updates_come_from_the_stored_event_contents(self):
        event = LyingGetDict(
            {"kind": "work_submission"},
            reported={"feature_updates": {"fabricated_feature": 777}})
        engine = mod04.TickEngine()
        updated = mod04.apply_event_to_state(
            {"feature_values": {"activity": 1}}, event, engine=engine)
        self.assertEqual(updated["feature_values"], {"activity": 1})

    def test_stored_feature_updates_still_land(self):
        event = {"kind": "work_submission",
                 "feature_updates": {"real_feature": 5}}
        engine = mod04.TickEngine()
        updated = mod04.apply_event_to_state(
            {"feature_values": {"activity": 1}}, event, engine=engine)
        self.assertEqual(
            updated["feature_values"], {"activity": 1, "real_feature": 5})

    def test_raising_get_does_not_escape_the_act(self):
        event = LyingGetDict({"kind": "work_submission"}, raising=True)
        engine = mod04.TickEngine()
        updated = mod04.apply_event_to_state(
            {"feature_values": {"activity": 1}}, event, engine=engine)
        self.assertEqual(updated["feature_values"], {"activity": 1})


class TestR10026CheckpointDepthRefusalForm(CheckpointBase):

    def _refusal(self, slot, depth):
        handed = parts()
        handed[slot] = chain(depth)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(manifest(), **handed)
        return str(caught.exception)

    def test_one_refusal_form_at_every_too_deep_depth(self):
        for slot in ("agent_states", "simulation_clock_value"):
            for depth in (100, 101, 102, 120):
                message = self._refusal(slot, depth)
                self.assertIn("view record copy bound reached", message)
                self.assertIn("write_checkpoint", message)
                self.assertNotIn("Form 13A validation", message)
                self.assertEqual(
                    mod10.checkpoints_for_run("run-b4-ckpt"), [])

    def test_chain_of_99_in_a_state_part_stands_written(self):
        for slot in ("agent_states", "simulation_clock_value"):
            handed = parts()
            handed[slot] = chain(99)
            result = mod04.write_checkpoint(manifest(), **handed)
            self.assertEqual(
                result["checkpoint_state"][slot], chain(99))
            mod10.reset_stores()


class TestR10027GuardRefusalNamesActAndArgument(unittest.TestCase):

    def test_refusals_at_different_acts_name_their_act_and_argument(self):
        deep = chain(120)
        messages = {}
        point = mod04.DeliveryPoint("dp", "dest")
        with self.assertRaises(mod04.NamedFailure) as caught:
            point.record_interface_delivery(deep)
        messages["delivery"] = str(caught.exception)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.run_record_with_order({"run_id": "r1"}, deep)
        messages["order"] = str(caught.exception)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.ContractAHandover(deep, {}, {}, "family-1")
        messages["handover"] = str(caught.exception)
        self.assertIn("record_interface_delivery", messages["delivery"])
        self.assertIn("payload_description", messages["delivery"])
        self.assertIn("run_record_with_order", messages["order"])
        self.assertIn("order_identifier", messages["order"])
        self.assertIn("ContractAHandover", messages["handover"])
        self.assertIn("point", messages["handover"])
        self.assertEqual(len(set(messages.values())), 3)

    def test_refusals_at_different_checkpoint_arguments_differ(self):
        messages = {}
        for argument in ("detection_state", "manifest"):
            mod10.reset_stores()
            handed = parts()
            if argument == "manifest":
                bad = manifest()
                bad["deep"] = chain(120)
            else:
                bad = manifest()
                handed["detection_state"] = {"deep": chain(120)}
            with self.assertRaises(mod04.NamedFailure) as caught:
                mod04.write_checkpoint(bad, **handed)
            messages[argument] = str(caught.exception)
        self.assertIn("detection_state", messages["detection_state"])
        self.assertIn("manifest", messages["manifest"])
        self.assertNotEqual(
            messages["detection_state"], messages["manifest"])
        mod10.reset_stores()

    def test_cycle_refusal_names_the_act_and_argument(self):
        value = []
        value.append(value)
        point = mod04.DeliveryPoint("dp", "dest")
        with self.assertRaises(mod04.NamedFailure) as caught:
            point.record_interface_delivery(value)
        message = str(caught.exception)
        self.assertIn("view record copy found a cycle", message)
        self.assertIn("record_interface_delivery", message)
        self.assertIn("payload_description", message)


class TestR10028BoundCountsWrappers(unittest.TestCase):

    def test_refusal_wording_states_that_wrappers_count(self):
        point = mod04.DeliveryPoint("dp", "dest")
        with self.assertRaises(mod04.NamedFailure) as caught:
            point.record_interface_delivery(chain(120))
        message = str(caught.exception)
        self.assertIn("stated bound of 100", message)
        self.assertIn("standing around the handed value", message)

    def test_total_depth_standing_holds_across_slots(self):
        point = mod04.DeliveryPoint("dp", "dest")
        entry = point.record_interface_delivery(chain(101))
        self.assertIsNotNone(entry)
        held = mod04.hold_view({"deep": chain(100)})
        self.assertTrue(held["held"])
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view({"deep": chain(101)})
        engine = mod04.TickEngine()
        updated = mod04.apply_event_to_state(
            {"feature_values": {}},
            {"kind": "k", "deep": chain(99)}, engine=engine)
        self.assertIsNotNone(updated)
        engine = mod04.TickEngine()
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                {"feature_values": {}},
                {"kind": "k", "deep": chain(100)}, engine=engine)


class TestR10053SharedFreezeMemo(CheckpointBase):

    def test_run_record_and_order_share_one_copy_of_a_shared_part(self):
        shared = [7]
        record = {"run_id": "r1", "field": shared}
        result = mod04.run_record_with_order(record, shared)
        self.assertIs(
            result["field"], result["scheduling_order_identifier"])
        self.assertIsNot(result["field"], shared)
        self.assertEqual(result["field"], [7])

    def test_state_parts_share_one_copy_of_a_shared_part(self):
        shared = [1, 2]
        handed = parts()
        handed["agent_states"] = {"shared": shared}
        handed["detection_state"] = {"shared": shared}
        result = mod04.write_checkpoint(manifest(), **handed)
        state = result["checkpoint_state"]
        self.assertIs(state["agent_states"]["shared"],
                      state["detection_state"]["shared"])
        self.assertIsNot(state["agent_states"]["shared"], shared)
        paired_state = result["manifest"]["checkpoint_state"]
        self.assertIs(paired_state["agent_states"]["shared"],
                      paired_state["detection_state"]["shared"])


if __name__ == "__main__":
    unittest.main()

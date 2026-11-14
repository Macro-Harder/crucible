"""Pin tests for fix wave 9, Builder 5, MOD-04 rows R9-010,
R9-024, R9-025, R9-026, and R9-027.

Row R9-010, MOD-04 limb: the _stored_text helper falls back to
the plain string call for non text values, so a non text key
stands judged from a string reading it supplies itself, where
the cured form judges the same key as no name.

Row R9-024: run_record_with_order places the order identifier
into the returned record unguarded and uncopied.

Row R9-025: DeliveryPoint.record_interface_delivery copies its
payload with no bound guard ahead of the copy.

Row R9-026: the TickEngine writer path acts copy state, event,
and feature updates with no bound guard on any limb.

Row R9-027: write_checkpoint copies every state part, the
manifest, and a deepcopy of the assembled state with no bound
guard ahead of any copy.
"""

import unittest

from crucible import mod04
from crucible import mod10


class NamedKey:
    """A plain non text object whose string reading returns the
    name it is given. It stores no text at all."""

    def __init__(self, reported):
        self._reported = reported

    def __str__(self):
        return self._reported

    __hash__ = object.__hash__


class LieStr(str):
    """A text value storing one text whose string reading
    reports another text."""

    def __new__(cls, stored, reported):
        obj = super().__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class HonestStr(str):
    """A text subclass that overrides nothing."""


class ReportingBytes(bytes):
    """A bytes value storing one content whose string reading
    reports another word."""

    def __str__(self):
        return "figure"


def chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def chain_depth(value):
    depth = 0
    while isinstance(value, list):
        depth += 1
        value = value[0]
    return depth


def cycle_list():
    value = []
    value.append(value)
    return value


def cycle_dict():
    value = {}
    value["self"] = value
    return value


def good_state():
    return {
        "agent_identifier": "agent-1",
        "day": 1,
        "feature_values": {"activity": 1},
        "rule_records": [],
    }


class TestR9010StoredText(unittest.TestCase):

    def test_defect_non_text_object_reporting_barred_name_is_no_name(self):
        key = NamedKey("membership")
        self.assertEqual(mod04._stored_text(key), "")
        self.assertFalse(mod04._is_barred_key(key))
        self.assertFalse(mod04._combined_key_barred(key))
        self.assertNotIn("membership", mod04._folded_readings(key))

    def test_defect_non_text_object_reporting_ground_truth_is_no_name(self):
        key = NamedKey("ground_truth")
        self.assertEqual(mod04._stored_text(key), "")
        self.assertFalse(mod04._is_barred_key(key))

    def test_defect_non_text_object_reporting_canary_is_no_name(self):
        key = NamedKey("canary")
        self.assertEqual(mod04._stored_text(key), "")
        self.assertFalse(mod04._is_barred_key(key))

    def test_defect_bytes_value_stores_no_text_name(self):
        self.assertEqual(mod04._stored_text(b"membership"), "")
        self.assertFalse(mod04._is_barred_key(b"membership"))
        reporting = ReportingBytes(b"membership")
        self.assertEqual(mod04._stored_text(reporting), "")
        self.assertFalse(mod04._is_barred_key(reporting))

    def test_defect_plain_int_stores_no_text_name(self):
        self.assertEqual(mod04._stored_text(123), "")
        self.assertEqual(mod04._folded_readings(123), ())

    def test_control_plain_text_stands_judged_by_its_text(self):
        self.assertEqual(mod04._stored_text("membership"), "membership")
        self.assertTrue(mod04._is_barred_key("membership"))
        self.assertTrue(mod04._is_barred_key("canary"))
        self.assertFalse(mod04._is_barred_key("activity"))
        self.assertIn("membership", mod04._folded_readings("membership"))

    def test_control_lie_str_judged_by_stored_text(self):
        self.assertEqual(
            mod04._stored_text(LieStr("membership", "activity")),
            "membership")
        self.assertTrue(mod04._is_barred_key(
            LieStr("membership", "activity")))
        self.assertFalse(mod04._is_barred_key(
            LieStr("activity", "membership")))

    def test_control_honest_subclass_and_int_and_tuple_standings(self):
        self.assertTrue(mod04._is_barred_key(HonestStr("membership")))
        self.assertFalse(mod04._is_barred_key(HonestStr("activity")))
        self.assertFalse(mod04._is_barred_key(123))
        self.assertTrue(mod04._is_barred_key(("membership",)))
        self.assertFalse(mod04._is_barred_key(("activity",)))


class TestR9024RunRecordWithOrder(unittest.TestCase):

    def test_defect_past_bound_order_refused_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, chain(120))
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, chain(150))

    def test_defect_deep_order_refused_in_named_form_not_bare_error(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, chain(2000))

    def test_defect_cyclic_order_refused_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, cycle_list())
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, cycle_dict())

    def test_defect_order_copied_not_placed_by_identity(self):
        handed = ["ord-a", ["ord-b"]]
        result = mod04.run_record_with_order({"run_id": "r1"}, handed)
        placed = result["scheduling_order_identifier"]
        self.assertEqual(placed, handed)
        self.assertIsNot(placed, handed)
        self.assertIsNot(placed[1], handed[1])
        handed[1].append("mutated")
        self.assertEqual(
            result["scheduling_order_identifier"], ["ord-a", ["ord-b"]])

    def test_control_bound_standing_101_admitted_102_refused(self):
        result = mod04.run_record_with_order({"run_id": "r1"}, chain(101))
        self.assertEqual(
            chain_depth(result["scheduling_order_identifier"]), 101)
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"run_id": "r1"}, chain(102))

    def test_control_plain_order_placed_and_record_copied(self):
        record = {"run_id": "r1", "run_class": "screening"}
        result = mod04.run_record_with_order(record, "ord-1")
        self.assertEqual(result["scheduling_order_identifier"], "ord-1")
        self.assertEqual(result["run_id"], "r1")
        self.assertNotIn("scheduling_order_identifier", record)


class TestR9025RecordInterfaceDelivery(unittest.TestCase):

    def test_defect_past_bound_payload_refused_in_named_form(self):
        point = mod04.DeliveryPoint("point-1", "dest-1")
        with self.assertRaises(mod04.NamedFailure):
            point.record_interface_delivery(chain(120))
        self.assertEqual(point.deliveries, [])

    def test_defect_deep_payload_refused_in_named_form_not_bare_error(self):
        point = mod04.DeliveryPoint("point-1", "dest-1")
        with self.assertRaises(mod04.NamedFailure):
            point.record_interface_delivery(chain(2000))
        self.assertEqual(point.deliveries, [])

    def test_defect_cyclic_payload_refused_in_named_form(self):
        point = mod04.DeliveryPoint("point-1", "dest-1")
        with self.assertRaises(mod04.NamedFailure):
            point.record_interface_delivery(cycle_list())
        with self.assertRaises(mod04.NamedFailure):
            point.record_interface_delivery(
                {"payload": cycle_dict()})
        self.assertEqual(point.deliveries, [])

    def test_control_bound_standing_101_admitted_102_refused(self):
        point = mod04.DeliveryPoint("point-1", "dest-1")
        entry = point.record_interface_delivery(chain(101))
        self.assertEqual(chain_depth(entry["payload"]), 101)
        with self.assertRaises(mod04.NamedFailure):
            point.record_interface_delivery(chain(102))

    def test_control_shallow_payload_copied_and_recorded(self):
        point = mod04.RuleCoreDeliveryPoint()
        handed = {"kind": "event", "deep": chain(50)}
        entry = point.record_interface_delivery(handed)
        self.assertEqual(entry["form"], "interface")
        self.assertFalse(entry["running_delivery"])
        self.assertEqual(chain_depth(entry["payload"]["deep"]), 50)
        self.assertIsNot(entry["payload"], handed)
        self.assertEqual(len(point.deliveries), 1)


class TestR9026WriteSimulationState(unittest.TestCase):

    def test_defect_past_bound_change_refused_in_named_form(self):
        engine = mod04.TickEngine()
        with self.assertRaises(mod04.NamedFailure):
            engine.write_simulation_state(engine, chain(120))
        self.assertEqual(engine.state_writes, [])

    def test_defect_deep_change_refused_in_named_form_not_bare_error(self):
        engine = mod04.TickEngine()
        with self.assertRaises(mod04.NamedFailure):
            engine.write_simulation_state(engine, chain(2000))
        self.assertEqual(engine.state_writes, [])

    def test_defect_cyclic_change_refused_in_named_form(self):
        engine = mod04.TickEngine()
        with self.assertRaises(mod04.NamedFailure):
            engine.write_simulation_state(engine, cycle_list())
        self.assertEqual(engine.state_writes, [])

    def test_control_bound_standing_101_admitted_102_refused(self):
        engine = mod04.TickEngine()
        self.assertTrue(engine.write_simulation_state(engine, chain(101)))
        self.assertEqual(chain_depth(engine.state_writes[-1]), 101)
        with self.assertRaises(mod04.NamedFailure):
            engine.write_simulation_state(engine, chain(102))

    def test_control_shallow_change_written_and_second_writer_refused(self):
        engine = mod04.TickEngine()
        self.assertTrue(
            engine.write_simulation_state(engine, {"deep": chain(50)}))
        self.assertEqual(chain_depth(engine.state_writes[-1]["deep"]), 50)
        with self.assertRaises(mod04.NamedFailure):
            engine.write_simulation_state("other", {"deep": chain(50)})


class TestR9026ApplyEventToState(unittest.TestCase):

    def test_defect_past_bound_state_refused_in_named_form(self):
        state = good_state()
        state["deep"] = chain(120)
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                state, {"kind": "k"}, engine=mod04.TickEngine())

    def test_defect_deep_state_refused_in_named_form_not_bare_error(self):
        state = good_state()
        state["deep"] = chain(2000)
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                state, {"kind": "k"}, engine=mod04.TickEngine())

    def test_defect_deep_event_refused_in_named_form_not_bare_error(self):
        event = {"kind": "k", "deep": chain(2000)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                good_state(), event, engine=mod04.TickEngine())

    def test_defect_past_bound_feature_updates_refused_in_named_form(self):
        event = {"feature_updates": {"deep": chain(120)}}
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                good_state(), event, engine=mod04.TickEngine())
        event = {"feature_updates": {"deep": chain(2000)}}
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                good_state(), event, engine=mod04.TickEngine())

    def test_defect_cyclic_event_refused_in_named_form(self):
        event = {"kind": "k", "loop": cycle_list()}
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(
                good_state(), event, engine=mod04.TickEngine())

    def test_control_shallow_event_applies_and_updates_land(self):
        engine = mod04.TickEngine()
        event = {
            "kind": "k",
            "deep": chain(20),
            "feature_updates": {"score": 5, "deep": chain(20)},
        }
        updated = mod04.apply_event_to_state(
            good_state(), event, engine=engine)
        self.assertEqual(updated["feature_values"]["score"], 5)
        self.assertEqual(updated["feature_values"]["activity"], 1)
        self.assertEqual(
            chain_depth(updated["feature_values"]["deep"]), 20)
        self.assertEqual(len(engine.state_writes), 1)

    def test_control_no_engine_stands_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.apply_event_to_state(good_state(), {"kind": "k"})


class TestR9026ProcessDayEvents(unittest.TestCase):

    def test_defect_past_bound_state_refused_in_named_form(self):
        state = good_state()
        state["deep"] = chain(120)
        with self.assertRaises(mod04.NamedFailure):
            mod04.process_day_events(state, [{"kind": "work_submission"}])

    def test_defect_deep_state_refused_in_named_form_not_bare_error(self):
        state = good_state()
        state["deep"] = chain(2000)
        with self.assertRaises(mod04.NamedFailure):
            mod04.process_day_events(state, [{"kind": "work_submission"}])

    def test_defect_deep_event_refused_in_named_form_not_bare_error(self):
        event = {"kind": "work_submission", "deep": chain(2000)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.process_day_events(good_state(), [event])

    def test_defect_past_bound_event_refused_in_named_form(self):
        event = {"kind": "work_submission", "deep": chain(120)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.process_day_events(good_state(), [event])

    def test_defect_cyclic_state_refused_in_named_form(self):
        state = good_state()
        state["loop"] = cycle_list()
        with self.assertRaises(mod04.NamedFailure):
            mod04.process_day_events(state, [{"kind": "work_submission"}])

    def test_control_shallow_day_runs_in_sequence(self):
        result = mod04.process_day_events(
            good_state(), [{"kind": "work_submission"}])
        self.assertEqual(result["sequence"], ["apply", "project", "deliver"])
        self.assertEqual(len(result["projections"]), 1)
        self.assertEqual(
            result["projections"][0]["agent_identifier"], "agent-1")
        self.assertEqual(len(result["rule_core_deliveries"]), 1)
        self.assertEqual(len(result["detection_deliveries"]), 1)
        self.assertEqual(result["state"]["agent_identifier"], "agent-1")


class TestR9027WriteCheckpoint(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def _manifest(self, run_id):
        return {
            "run_identifier": run_id,
            "run_id": run_id,
            "simulated_day": 3,
        }

    def _parts(self):
        return {
            "agent_states": [{"agent_identifier": "agent-1"}],
            "escrow_contract_states": [],
            "detection_state": {"state": "stated"},
            "stream_positions_and_generator_states": {
                "stream-1": {"position": 1}},
            "simulation_clock_value": 3,
        }

    def test_defect_deep_agent_states_refused_by_guard_before_copy(self):
        parts = self._parts()
        parts["agent_states"] = chain(2000)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(
                self._manifest("run-b5-ckpt-deep"), **parts)
        self.assertIn("view record copy bound", str(caught.exception))
        self.assertEqual(
            mod10.checkpoints_for_run("run-b5-ckpt-deep"), [])

    def test_defect_deep_manifest_refused_by_guard_before_copy(self):
        manifest = self._manifest("run-b5-ckpt-manifest")
        manifest["deep"] = chain(2000)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(manifest, **self._parts())
        self.assertIn("view record copy bound", str(caught.exception))

    def test_defect_deep_detection_state_refused_by_guard(self):
        parts = self._parts()
        parts["detection_state"] = {"deep": chain(2000)}
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(
                self._manifest("run-b5-ckpt-detection"), **parts)
        self.assertIn("view record copy bound", str(caught.exception))

    def test_defect_past_bound_part_refused_by_guard_not_later_check(self):
        parts = self._parts()
        parts["agent_states"] = chain(120)
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(
                self._manifest("run-b5-ckpt-past"), **parts)
        self.assertIn("view record copy bound", str(caught.exception))

    def test_defect_cyclic_part_refused_by_guard_in_named_form(self):
        parts = self._parts()
        parts["agent_states"] = cycle_list()
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.write_checkpoint(
                self._manifest("run-b5-ckpt-cycle"), **parts)
        self.assertIn("view record copy found a cycle", str(caught.exception))
        self.assertEqual(
            mod10.checkpoints_for_run("run-b5-ckpt-cycle"), [])

    def test_control_shallow_checkpoint_written_and_retained(self):
        result = mod04.write_checkpoint(
            self._manifest("run-b5-ckpt-good"), **self._parts())
        state = result["checkpoint_state"]
        self.assertEqual(state["run_identifier"], "run-b5-ckpt-good")
        self.assertEqual(state["simulated_day"], 3)
        self.assertEqual(
            mod10.checkpoint_state_at("run-b5-ckpt-good", 3), state)
        self.assertEqual(result["manifest"]["checkpoint_state"], state)

    def test_control_incomplete_state_stands_refused_in_named_form(self):
        parts = self._parts()
        parts["detection_state"] = None
        with self.assertRaises(mod04.NamedFailure):
            mod04.write_checkpoint(
                self._manifest("run-b5-ckpt-incomplete"), **parts)
        self.assertEqual(
            mod10.checkpoints_for_run("run-b5-ckpt-incomplete"), [])


class TestGuardedSisterStandings(unittest.TestCase):

    def test_control_view_guard_101_admitted_102_refused(self):
        mod04._view_copy_guard(chain(101))
        with self.assertRaises(mod04.NamedFailure):
            mod04._view_copy_guard(chain(102))

    def test_control_hold_view_standing_at_the_bound(self):
        held = mod04.hold_view({"deep": chain(100)})
        self.assertTrue(held["held"])
        self.assertEqual(chain_depth(held["view_record"]["deep"]), 100)
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view({"deep": chain(101)})


if __name__ == "__main__":
    unittest.main()

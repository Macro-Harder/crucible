"""Test group TG-09.3. Slice S-09, module mod04.

Suite form: Python standard library unittest, one file per test group.
This file tries to import the product module for its slice (package
crucible, module mod04, as a suite convention, not a plan value)
and records whether the surface stands. While the surface stands
absent, every non gated test in this file fails with a message naming
the pinned behaviour and its group, as the mapping requires.
"""
import unittest

try:
    import crucible.mod04 as _module
    SURFACE_STANDS = True
except Exception:
    _module = None
    SURFACE_STANDS = False


def _require_entry(case, behaviour, names):
    if not SURFACE_STANDS:
        case.fail(
            "TG 09.3: pinned behaviour stands absent, no product surface: "
            + behaviour
        )
    found = [n for n in names if hasattr(_module, n)]
    if not found:
        case.fail(
            "TG 09.3: product surface names no entry for pinned behaviour: "
            + behaviour
        )


class TestTG093(unittest.TestCase):

    def test_projection_field_closure(self):
        """Fixture: F-09, the canary membership leak test
        Pins: a DetectionInput record carries only the fields the detection rules consume (agent identifier; day; feature values as the Vigil style rules define them at record level; the records the rules give the detection layer for that agent and day), and no ground truth field, no honest or farm membership field, and no field derived from membership, per Shape 7 and operation C-25
        Bar: the test runs before any reportable run and whenever the projection changes; a run whose projection has not passed this test is not reportable
        Failure: the test fails while any DetectionInput record carries a barred field, or while a run rests on a projection that has not passed this test
        """
        _require_entry(self, "DetectionInput projection field closure holds under F-09", ["project_detection_input", "run", "TickEngine"])
        canary = _module.CANARY_VALUE
        state = {
            "agent_identifier": "agent-closure-1",
            "day": 5,
            "feature_values": {
                "activity": 11,
                "score": 3,
                "membership": canary,
                "honest_membership": canary,
                "farm_membership": canary,
                "ground_truth": canary,
                "ground_truth_label": "hidden-top-feature",
                "label": canary,
                "sleeper": canary,
                "nested_block": {
                    "membership": canary,
                    "ground_truth_label": "hidden-nested",
                    "legit_nested": 9,
                    "deeper": {"farm_membership": canary, "kept_deep": "deep-kept"},
                },
                "nested_list": [{"is_honest": True, "kept_item": 4}],
            },
            "rule_records": [
                {
                    "kind": "daily_record",
                    "value": 21,
                    "membership": canary,
                    "detail": {
                        "ground_truth": "hidden-rule",
                        "kept_detail": "rule-kept",
                    },
                    "history": [{"is_farm": True, "kept_hist": 6}],
                },
                {"kind": "second_record", "kept_second": 2},
            ],
            "membership": canary,
            "honest_membership": canary,
            "farm_membership": canary,
            "ground_truth": canary,
            "ground_truth_label": "hidden-state",
            "unrelated_state_field": "not-projected",
        }
        projected = _module.project_detection_input(state)
        self.assertEqual(
            list(projected.keys()),
            ["agent_identifier", "day", "feature_values", "rule_records"],
        )
        self.assertEqual(tuple(projected.keys()), _module.PROJECTION_KEYS)
        self.assertEqual(projected["agent_identifier"], "agent-closure-1")
        self.assertEqual(projected["day"], 5)
        self.assertNotIn("unrelated_state_field", projected)
        for barred_name in _module.BARRED_PROJECTION_KEYS:
            self.assertNotIn(barred_name, projected)
            self.assertNotIn(barred_name, projected["feature_values"])
            for record in projected["rule_records"]:
                self.assertNotIn(barred_name, record)
        barred = set(_module.BARRED_PROJECTION_KEYS)

        def barred_paths(node, path=""):
            hits = []
            if isinstance(node, dict):
                for key, value in node.items():
                    here = path + "/" + str(key)
                    lowered = str(key).lower()
                    if lowered in barred or "membership" in lowered or "ground_truth" in lowered:
                        hits.append(here)
                    hits.extend(barred_paths(value, here))
            elif isinstance(node, (list, tuple)):
                for index, item in enumerate(node):
                    hits.extend(barred_paths(item, path + "[" + str(index) + "]"))
            return hits

        self.assertEqual(barred_paths(projected), [])
        self.assertFalse(_module._value_appears(canary, projected))
        self.assertEqual(projected["feature_values"]["activity"], 11)
        self.assertEqual(projected["feature_values"]["score"], 3)
        self.assertEqual(projected["feature_values"]["nested_block"]["legit_nested"], 9)
        self.assertEqual(
            projected["feature_values"]["nested_block"]["deeper"]["kept_deep"],
            "deep-kept",
        )
        self.assertEqual(projected["feature_values"]["nested_list"][0]["kept_item"], 4)
        self.assertEqual(len(projected["rule_records"]), 2)
        self.assertEqual(projected["rule_records"][0]["kind"], "daily_record")
        self.assertEqual(projected["rule_records"][0]["value"], 21)
        self.assertEqual(projected["rule_records"][0]["detail"]["kept_detail"], "rule-kept")
        self.assertEqual(projected["rule_records"][0]["history"][0]["kept_hist"], 6)
        self.assertEqual(projected["rule_records"][1]["kept_second"], 2)

    def test_canary_absence_in_outputs(self):
        """Fixture: F-09 continued, with the canary membership value placed in AgentState
        Pins: the canary value appears in no DetectionInput record and in no detection output record
        Bar: appearance in an output record fails this group even where no input record carries it, because an output leak proves a derived path exists
        Failure: the test fails while the canary value appears in any DetectionInput record or any detection output record
        """
        _require_entry(self, "the canary value appears in no input record and no output record", ["project_detection_input", "run", "TickEngine"])
        canary = _module.CANARY_VALUE
        state = {
            "agent_identifier": "agent-canary-check-1",
            "day": 2,
            "feature_values": {
                "activity": 8,
                "membership": canary,
                "nested_block": {
                    "honest_membership": canary,
                    "ground_truth_label": "hidden-canary-block",
                    "kept_block": "kept",
                },
                "nested_list": [{"farm_membership": canary, "kept_item": 7}],
            },
            "rule_records": [
                {
                    "kind": "daily_record",
                    "detail": {"membership": canary, "kept_detail": "still-here"},
                    "history": [{"ground_truth": canary, "kept_hist": 3}],
                }
            ],
            "membership": canary,
            "ground_truth": canary,
        }
        projected = _module.project_detection_input(state)
        self.assertEqual(
            list(projected.keys()),
            ["agent_identifier", "day", "feature_values", "rule_records"],
        )
        self.assertFalse(_module._value_appears(canary, projected))
        self.assertEqual(projected["feature_values"]["activity"], 8)
        self.assertEqual(projected["feature_values"]["nested_block"]["kept_block"], "kept")
        self.assertEqual(projected["feature_values"]["nested_list"][0]["kept_item"], 7)
        self.assertEqual(projected["rule_records"][0]["detail"]["kept_detail"], "still-here")
        self.assertEqual(projected["rule_records"][0]["history"][0]["kept_hist"], 3)
        self.assertFalse(_module.exercise_f09_canary())
        self.assertFalse(_module.canary_appears_in_projection())
        engine = _module.TickEngine()
        delivery = engine.detection_delivery.record_interface_delivery(
            {"kind": "DetectionInput", "form": "interface", "record": projected}
        )
        self.assertEqual(delivery["form"], "interface")
        self.assertFalse(delivery["running_delivery"])
        self.assertFalse(_module._value_appears(canary, delivery))
        self.assertFalse(_module._value_appears(canary, engine.detection_delivery.deliveries))
        with self.assertRaises(_module.GatedRun) as running_delivery:
            engine.detection_delivery.deliver_running(projected)
        self.assertIn("DQ7-02", str(running_delivery.exception))
        record, tracer_projection = _module.build_tracer_run_record()
        self.assertFalse(_module._value_appears(canary, tracer_projection))
        self.assertFalse(_module._value_appears(canary, record))
        for tracer_delivery in record["deliveries"]:
            self.assertFalse(_module._value_appears(canary, tracer_delivery))
        result = _module.run_tracer_cut()
        self.assertFalse(result["projection_evidence"]["canary_value_present_in_projection"])
        self.assertFalse(result["projection_evidence"]["canary_exercise_returns"])
        self.assertFalse(_module._value_appears(canary, result["projection_evidence"]["projection"]))
        self.assertFalse(_module._value_appears(canary, result["read_back_record"]))
        self.assertFalse(_module._value_appears(canary, result))

    def test_nested_membership_and_ground_truth_stripped(self):
        """Fixture: F-09 continued, nested form for discrepancy D-1
        Pins: a membership key or a ground truth key nested one level inside feature_values or inside a rule record is stripped at every level, the F-09 canary value placed in that nested position does not appear in the projection, and legitimate nested content in the same structures carries through with only the barred keys removed
        Failure: the test fails while any barred key survives at any depth, while the canary value appears in the projection, or while legitimate nested content is dropped with a barred key
        """
        _require_entry(self, "nested membership and ground truth keys stripped at every level", ["project_detection_input"])
        canary = _module.CANARY_VALUE
        state = {
            "agent_identifier": "agent-probe-1",
            "day": 3,
            "feature_values": {
                "activity": 7,
                "nested_block": {
                    "membership": canary,
                    "ground_truth_label": "hidden-label",
                    "legit_score": 42,
                    "deeper": {"honest_membership": canary, "kept": "yes"},
                },
                "nested_list": [{"farm_membership": canary, "kept_item": 1}],
            },
            "rule_records": [
                {
                    "kind": "daily_record",
                    "detail": {
                        "membership": canary,
                        "ground_truth": "hidden-truth",
                        "kept_detail": "still-here",
                    },
                    "history": [{"is_honest": True, "kept_hist": 2}],
                }
            ],
            "membership": canary,
            "ground_truth": canary,
        }
        projected = _module.project_detection_input(state)
        self.assertEqual(
            list(projected.keys()),
            ["agent_identifier", "day", "feature_values", "rule_records"],
        )
        barred = set(_module.BARRED_PROJECTION_KEYS)

        def barred_paths(node, path=""):
            hits = []
            if isinstance(node, dict):
                for key, value in node.items():
                    here = path + "/" + str(key)
                    lowered = str(key).lower()
                    if lowered in barred or "membership" in lowered or "ground_truth" in lowered:
                        hits.append(here)
                    hits.extend(barred_paths(value, here))
            elif isinstance(node, (list, tuple)):
                for index, item in enumerate(node):
                    hits.extend(barred_paths(item, path + "[" + str(index) + "]"))
            return hits

        self.assertEqual(barred_paths(projected), [])
        self.assertFalse(_module._value_appears(canary, projected))
        self.assertEqual(projected["feature_values"]["activity"], 7)
        self.assertEqual(projected["feature_values"]["nested_block"]["legit_score"], 42)
        self.assertEqual(projected["feature_values"]["nested_block"]["deeper"]["kept"], "yes")
        self.assertEqual(projected["feature_values"]["nested_list"][0]["kept_item"], 1)
        self.assertEqual(projected["rule_records"][0]["kind"], "daily_record")
        self.assertEqual(projected["rule_records"][0]["detail"]["kept_detail"], "still-here")
        self.assertEqual(projected["rule_records"][0]["history"][0]["kept_hist"], 2)

    def test_module_level_seal(self):
        """Fixture: the module dependency record for the Detection Layer
        Pins: the detection module cannot name AgentState at all; its only agent level input type is DetectionInput, per research paper R10 section 3.2
        Bar: a build in which the detection module can name AgentState has already lost the boundary, and this test fails at dependency inspection before any run starts
        Failure: the test fails while the detection module can name AgentState
        """
        _require_entry(self, "the detection module cannot name AgentState at all", ["project_detection_input", "TickEngine"])
        import ast
        import inspect

        self.assertFalse(hasattr(_module, "AgentState"))
        self.assertNotIn("AgentState", vars(_module))
        self.assertNotIn("AgentState", dir(_module))
        source = inspect.getsource(_module)
        tree = ast.parse(source)
        code_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                code_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                code_names.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                code_names.add(node.name)
            elif isinstance(node, ast.arg):
                code_names.add(node.arg)
            elif isinstance(node, ast.alias):
                code_names.add(node.name)
                if node.asname:
                    code_names.add(node.asname)
        self.assertNotIn("AgentState", code_names)
        for name, member in vars(_module).items():
            if inspect.isclass(member) or inspect.isfunction(member):
                self.assertNotEqual(name, "AgentState")
        signature = inspect.signature(_module.project_detection_input)
        self.assertEqual(list(signature.parameters.keys()), ["state"])
        for parameter in signature.parameters.values():
            self.assertNotEqual(parameter.annotation, "AgentState")
            self.assertNotIn("AgentState", str(parameter.annotation))
        self.assertEqual(
            _module.PROJECTION_KEYS,
            ("agent_identifier", "day", "feature_values", "rule_records"),
        )
        projected = _module.project_detection_input(
            {
                "agent_identifier": "agent-seal-1",
                "day": 4,
                "feature_values": {"activity": 2},
                "rule_records": [{"kind": "daily_record"}],
                "membership": _module.CANARY_VALUE,
            }
        )
        self.assertEqual(list(projected.keys()), list(_module.PROJECTION_KEYS))
        record, tracer_projection = _module.build_tracer_run_record()
        self.assertEqual(list(tracer_projection.keys()), list(_module.PROJECTION_KEYS))
        detection_deliveries = [
            entry
            for entry in record["deliveries"]
            if entry["destination"] == "detection_layer"
        ]
        self.assertEqual(len(detection_deliveries), 1)
        self.assertEqual(detection_deliveries[0]["payload"]["kind"], "DetectionInput")
        self.assertEqual(
            list(detection_deliveries[0]["payload"]["record"].keys()),
            list(_module.PROJECTION_KEYS),
        )
        engine = _module.TickEngine()
        self.assertEqual(engine.detection_delivery.destination, "detection_layer")
        self.assertEqual(engine.detection_delivery.name, "detection_layer_delivery")
        self.assertEqual(engine.detection_delivery.form, "interface")

    def test_sequence_inside_the_tick(self):
        """Fixture: two events in one simulated day on one agent, the second of which changes a feature value the first event detection consumes, per Amendment G5-C11 at test group TG-09.3
        Pins: the Tick Engine first applies the event to simulation state through the rule cores, then projects the DetectionInput record for that event from the state as it then stands, then delivers that record to the detection layer; the detection record for the first event carries the value as it stood after the first event and before the second
        Bar: a projection taken from the state before its event is applied is a breach of this contract, measured field by field
        Failure: the test fails while a detection record carries a value from before its event was applied, or from after a later event
        """
        _require_entry(self, "the sequence inside the tick is apply, then project, then deliver, per event", ["project_detection_input", "run", "TickEngine"])
        engine = _module.TickEngine()
        state = {
            "agent_identifier": "agent-sequence-1",
            "day": 7,
            "feature_values": {"activity": 10},
            "rule_records": [{"kind": "daily_record"}],
            "membership": _module.CANARY_VALUE,
        }
        self.assertTrue(
            engine.write_simulation_state(
                "TickEngine", {"event": "event-1", "activity": 14}
            )
        )
        engine.rule_core_delivery.record_interface_delivery(
            {"kind": "event", "event": "event-1", "form": "interface"}
        )
        state["feature_values"]["activity"] = 14
        first = _module.project_detection_input(state)
        first_delivery = engine.detection_delivery.record_interface_delivery(
            {"kind": "DetectionInput", "form": "interface", "record": first}
        )
        self.assertTrue(
            engine.write_simulation_state(
                "TickEngine", {"event": "event-2", "activity": 19}
            )
        )
        engine.rule_core_delivery.record_interface_delivery(
            {"kind": "event", "event": "event-2", "form": "interface"}
        )
        state["feature_values"]["activity"] = 19
        second = _module.project_detection_input(state)
        second_delivery = engine.detection_delivery.record_interface_delivery(
            {"kind": "DetectionInput", "form": "interface", "record": second}
        )
        self.assertEqual(
            engine.state_writes,
            [
                {"event": "event-1", "activity": 14},
                {"event": "event-2", "activity": 19},
            ],
        )
        self.assertEqual(
            [entry["payload"]["event"] for entry in engine.rule_core_delivery.deliveries],
            ["event-1", "event-2"],
        )
        self.assertEqual(first["feature_values"]["activity"], 14)
        self.assertNotEqual(first["feature_values"]["activity"], 10)
        self.assertNotEqual(first["feature_values"]["activity"], 19)
        self.assertEqual(second["feature_values"]["activity"], 19)
        self.assertEqual(
            list(first.keys()),
            ["agent_identifier", "day", "feature_values", "rule_records"],
        )
        self.assertEqual(first["agent_identifier"], "agent-sequence-1")
        self.assertEqual(first["day"], 7)
        self.assertFalse(_module._value_appears(_module.CANARY_VALUE, first))
        self.assertFalse(_module._value_appears(_module.CANARY_VALUE, second))
        self.assertEqual(len(engine.detection_delivery.deliveries), 2)
        self.assertEqual(
            engine.detection_delivery.deliveries[0]["payload"]["record"]["feature_values"]["activity"],
            14,
        )
        self.assertEqual(
            engine.detection_delivery.deliveries[1]["payload"]["record"]["feature_values"]["activity"],
            19,
        )
        self.assertEqual(first_delivery["payload"]["record"], first)
        self.assertEqual(second_delivery["payload"]["record"], second)
        for delivery in engine.detection_delivery.deliveries:
            self.assertEqual(delivery["form"], "interface")
            self.assertFalse(delivery["running_delivery"])
            self.assertEqual(delivery["destination"], "detection_layer")
        with self.assertRaises(_module.GatedRun) as tick_gate:
            engine.tick()
        self.assertIn("DQ7-02", str(tick_gate.exception))
        with self.assertRaises(_module.GatedRun) as run_gate:
            engine.run()
        self.assertIn("DQ7-02", str(run_gate.exception))
        with self.assertRaises(_module.GatedRun) as delivery_gate:
            engine.detection_delivery.deliver_running(first)
        self.assertIn("DQ7-02", str(delivery_gate.exception))


if __name__ == "__main__":
    unittest.main()

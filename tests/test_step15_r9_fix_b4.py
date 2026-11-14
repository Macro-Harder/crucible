"""Pin tests for fix wave 8, Builder 4, MOD-04 limbs of rows
R8-022 and R8-007.

Row R8-022: three MOD-04 public acts, run_record_with_order,
per_viewer_components, and the ContractAHandover constructor,
hand a handed value straight to the module copy act with no
bound guard before the copy, so a shape past the stated bound
of 100 stands copied whole and a deeper shape raises a bare
RecursionError, where the guarded acts of the same module
refuse the same shapes in NamedFailure form.

Row R8-007, MOD-04 limb: _folded_readings,
_combined_key_barred, and _is_barred_key take a handed text
from the plain str call, so a string subclass storing a
barred name while its string reading reports another name
stands judged as the reported name.
"""

import unittest

from crucible import mod04


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
    """A text subclass that overrides nothing. It stands as a
    control that a subclass as such changes no judgement."""


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


class TestR8022RunRecordWithOrder(unittest.TestCase):

    def test_defect_past_bound_and_deep_shapes_refused_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"deep": chain(120)}, "ord-1")
        with self.assertRaises(mod04.NamedFailure):
            mod04.run_record_with_order({"deep": chain(2000)}, "ord-1")

    def test_control_shallow_record_copied_whole_with_order(self):
        record = {"run_id": "r1", "deep": chain(50)}
        result = mod04.run_record_with_order(record, "ord-1")
        self.assertEqual(result["scheduling_order_identifier"], "ord-1")
        self.assertEqual(result["run_id"], "r1")
        self.assertEqual(chain_depth(result["deep"]), 50)
        self.assertNotIn("scheduling_order_identifier", record)

    def test_control_guarded_sister_act_refuses_past_bound_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view({"deep": chain(120)})
        held = mod04.hold_view({"deep": chain(50)})
        self.assertTrue(held["held"])
        self.assertEqual(chain_depth(held["view_record"]["deep"]), 50)


class TestR8022PerViewerComponents(unittest.TestCase):

    def test_defect_past_bound_and_deep_components_refused_in_named_form(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.per_viewer_components(components=[{"deep": chain(120)}])
        with self.assertRaises(mod04.NamedFailure):
            mod04.per_viewer_components(components=[{"deep": chain(2000)}])

    def test_control_shallow_component_copied_whole(self):
        result = mod04.per_viewer_components(
            components=[{"viewer_id": "v1", "deep": chain(50)}])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["viewer_id"], "v1")
        self.assertEqual(chain_depth(result[0]["deep"]), 50)

    def test_control_default_components_stand_per_viewer(self):
        result = mod04.per_viewer_components()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["viewer_id"], "viewer-1")
        self.assertEqual(result[1]["viewer_id"], "viewer-2")
        self.assertEqual(
            result[0]["presented_as"], "per viewer component")


class TestR8022ContractAHandover(unittest.TestCase):

    def test_defect_each_handed_value_past_bound_refused_in_named_form(self):
        shallow = {
            "point": {"point_id": "p1"},
            "assumption_record": {"assumption_record_id": "a1"},
            "seed_input_set": {"seed_inputs": ["s1"]},
            "family_id": "family-1",
        }
        for field in (
                "point", "assumption_record", "seed_input_set",
                "family_id"):
            handed = dict(shallow)
            handed[field] = {"deep": chain(120)}
            with self.assertRaises(mod04.NamedFailure, msg=field):
                mod04.ContractAHandover(**handed)
        handed = dict(shallow)
        handed["point"] = {"deep": chain(2000)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.ContractAHandover(**handed)

    def test_control_shallow_handover_stores_and_returns_copies(self):
        handover = mod04.ContractAHandover(
            point={"point_id": "p1", "deep": chain(50)},
            assumption_record={"assumption_record_id": "a1"},
            seed_input_set={"seed_inputs": ["s1"]},
            family_id="family-1",
        )
        point = handover.point
        self.assertEqual(point["point_id"], "p1")
        self.assertEqual(chain_depth(point["deep"]), 50)
        point["point_id"] = "mutated"
        self.assertEqual(handover.point["point_id"], "p1")
        self.assertEqual(handover.family_id, "family-1")

    def test_control_shallow_handover_verifies_intact(self):
        handover = mod04.ContractAHandover(
            point={"point_id": "p1"},
            assumption_record={"assumption_record_id": "a1"},
            seed_input_set={"seed_inputs": ["s1"]},
            family_id="family-1",
        )
        self.assertTrue(handover.verify_intact(
            {"point_id": "p1"},
            {"assumption_record_id": "a1"},
            {"seed_inputs": ["s1"]},
            "family-1",
        ))
        self.assertEqual(handover.as_dict()["form"], "interface")


class TestR8007FoldedReadings(unittest.TestCase):

    def test_defect_folded_readings_judge_the_stored_text(self):
        readings = mod04._folded_readings(
            LieStr("membership", "activity"))
        self.assertIn("membership", readings)
        readings = mod04._folded_readings(LieStr("canary", "activity"))
        self.assertIn("canary", readings)
        readings = mod04._folded_readings(
            LieStr("activity", "membership"))
        self.assertIn("activity", readings)
        self.assertNotIn("membership", readings)

    def test_control_plain_readings_stand_both_ways(self):
        self.assertIn("membership", mod04._folded_readings("membership"))
        self.assertIn("canary", mod04._folded_readings("canary"))
        self.assertIn("activity", mod04._folded_readings("activity"))
        self.assertNotIn(
            "membership", mod04._folded_readings("activity"))

    def test_control_honest_subclass_readings_match_plain(self):
        self.assertIn(
            "membership", mod04._folded_readings(HonestStr("membership")))
        self.assertNotIn(
            "membership", mod04._folded_readings(HonestStr("activity")))


class TestR8007CombinedKeyBarred(unittest.TestCase):

    def test_defect_combined_key_barred_judges_the_stored_text(self):
        self.assertTrue(mod04._combined_key_barred(
            LieStr("membership", "activity")))
        self.assertTrue(mod04._combined_key_barred(
            LieStr("canary", "activity")))
        self.assertFalse(mod04._combined_key_barred(
            LieStr("activity", "membership")))
        self.assertFalse(mod04._combined_key_barred(
            LieStr("figure", "canary")))

    def test_control_plain_combined_standings_both_ways(self):
        self.assertTrue(mod04._combined_key_barred("membership"))
        self.assertTrue(mod04._combined_key_barred("canary"))
        self.assertFalse(mod04._combined_key_barred("activity"))
        self.assertFalse(mod04._combined_key_barred("figure"))

    def test_control_honest_subclass_combined_matches_plain(self):
        self.assertTrue(
            mod04._combined_key_barred(HonestStr("membership")))
        self.assertFalse(
            mod04._combined_key_barred(HonestStr("activity")))


class TestR8007IsBarredKey(unittest.TestCase):

    def test_defect_is_barred_key_judges_the_stored_text(self):
        for stored in (
                "membership", "canary", "ground_truth",
                "groundtruth", "membership_id"):
            self.assertTrue(
                mod04._is_barred_key(LieStr(stored, "figure")),
                msg=stored)
        self.assertFalse(mod04._is_barred_key(
            LieStr("activity", "membership")))
        self.assertFalse(mod04._is_barred_key(
            LieStr("figure", "canary")))
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {
                LieStr("ground_truth", "figure"): 5,
                "score": 1,
            },
            "rule_records": [],
        }
        projected = mod04.project_detection_input(state)
        stored_keys = [
            str.__str__(key)
            for key in projected["feature_values"]
        ]
        self.assertEqual(stored_keys, ["score"])

    def test_control_plain_barred_and_clean_keys_both_ways(self):
        for barred in (
                "membership", "canary", "ground_truth",
                "groundtruth", "membership_id"):
            self.assertTrue(mod04._is_barred_key(barred), msg=barred)
        for clean in ("activity", "figure", "score"):
            self.assertFalse(mod04._is_barred_key(clean), msg=clean)

    def test_control_non_text_and_honest_keys_stand_as_before(self):
        self.assertFalse(mod04._is_barred_key(123))
        self.assertTrue(mod04._is_barred_key(("membership",)))
        self.assertTrue(mod04._is_barred_key(HonestStr("membership")))
        self.assertFalse(mod04._is_barred_key(HonestStr("activity")))


if __name__ == "__main__":
    unittest.main()

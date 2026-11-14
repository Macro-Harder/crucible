"""Step 15 Round 3 fix pins for cluster R3-4, Fix Builder 4.

Item R2-CT-01, Low: the MOD-04 checker must read the same four
substring parts the MOD-03 helper and the cured MOD-10 runner read,
so the joined groundtruth spelling and canary in proper substring
dress stand barred at the checker at any depth and at the module
own write act, build_view_record.

Controls pinned beside the cure: the exact names canary and
canary_value barred, ground_truth and membership forms barred, a
clean key admitted, the TG-11.2 ground_truth build refusal
preserved, and the MOD-10 variant pattern that builds a clean base
record and then swaps its contents in directly still standing.
The projection cleaning effect of the shared helper stands pinned
here as well, because the same helper governs that cleaning in the
same module.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10


GAP_KEYS = (
    "canary_token",
    "xcanaryx",
    "groundtruth",
    "groundtruth_field",
    "my_groundtruth_value",
)


def _nested_record(key, value="CANARYVAL"):
    return {"view_contents": [{"a": {"b": {key: value}}}]}


def _deep_record(key, depth=12):
    node = {key: "CANARYVAL"}
    for _ in range(depth):
        node = {"k": node}
    return {"view_contents": [node]}


def _contents_with_key(key):
    return [{
        "note": "clean",
        "first_seen_day": 1,
        "delay": 0,
        "a": {"b": {key: "CANARYVAL"}},
    }]


class TestCheckerGapFormsNested(unittest.TestCase):
    def test_canary_token_nested_three_deep_barred(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field(
                _nested_record("canary_token")))

    def test_xcanaryx_nested_three_deep_barred(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field(
                _nested_record("xcanaryx")))

    def test_groundtruth_nested_three_deep_barred(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field(
                _nested_record("groundtruth")))

    def test_groundtruth_field_nested_three_deep_barred(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field(
                _nested_record("groundtruth_field")))

    def test_my_groundtruth_value_nested_three_deep_barred(self):
        self.assertTrue(
            mod04.view_record_carries_barred_field(
                _nested_record("my_groundtruth_value")))

    def test_gap_forms_barred_at_greater_depth(self):
        for key in GAP_KEYS:
            self.assertTrue(
                mod04.view_record_carries_barred_field(
                    _deep_record(key)),
                key)

    def test_gap_forms_barred_in_other_groups(self):
        for key in GAP_KEYS:
            record = {
                "view_contents": [],
                "reputation_and_band_values": {"deep": {key: "x"}},
            }
            self.assertTrue(
                mod04.view_record_carries_barred_field(record), key)
            record = {
                "view_contents": [],
                "graph_position_as_seen": {"deep": {key: "x"}},
            }
            self.assertTrue(
                mod04.view_record_carries_barred_field(record), key)

    def test_gap_forms_barred_helper_direct(self):
        for key in GAP_KEYS:
            self.assertTrue(mod04._is_barred_key(key), key)


class TestBuildViewRecordWriteAct(unittest.TestCase):
    def test_canary_token_write_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=_contents_with_key("canary_token"),
                position="p", rule_version_set="rv")

    def test_xcanaryx_write_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=_contents_with_key("xcanaryx"),
                position="p", rule_version_set="rv")

    def test_groundtruth_write_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=_contents_with_key("groundtruth"),
                position="p", rule_version_set="rv")

    def test_groundtruth_field_write_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=_contents_with_key("groundtruth_field"),
                position="p", rule_version_set="rv")

    def test_my_groundtruth_value_write_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=_contents_with_key("my_groundtruth_value"),
                position="p", rule_version_set="rv")


class TestControls(unittest.TestCase):
    def test_exact_canary_names_barred(self):
        for key in ("canary", "canary_value"):
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(
                mod04.view_record_carries_barred_field(
                    _nested_record(key)),
                key)

    def test_ground_truth_and_membership_forms_barred(self):
        for key in (
                "ground_truth", "ground_truth_field",
                "membership", "membership_x", "membership_value"):
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(
                mod04.view_record_carries_barred_field(
                    _nested_record(key)),
                key)

    def test_clean_key_admitted_at_checker_and_write_act(self):
        self.assertFalse(mod04._is_barred_key("activity"))
        self.assertFalse(
            mod04.view_record_carries_barred_field(
                _nested_record("activity", value="stated")))
        record = mod04.build_view_record(
            contents=[{
                "activity": "stated",
                "first_seen_day": 1, "delay": 0}],
            position="p", rule_version_set="rv")
        self.assertEqual(record["form"], "ViewRecord")
        self.assertFalse(
            mod04.view_record_carries_barred_field(record))

    def test_ground_truth_build_refusal_preserved_tg_11_2(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents=[{"outer": {"ground_truth": "x"}}])


class TestMod10VariantSwapPattern(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_swap_contents_in_after_clean_build_still_stands(self):
        base = mod04.build_view_record(
            run_id="run-r3fix4-view", viewer_id="viewer-1", day=5,
            contents=[{"note": "clean", "first_seen_day": 1, "delay": 0}],
            position="pos-1", rule_version_set="rv-1")
        result = mod10.run_view_leak_check(base)
        self.assertTrue(result["reportable"])
        for key in GAP_KEYS:
            swapped = dict(base)
            swapped["view_contents"] = [{key: "CANARYVAL"}]
            with self.assertRaises(ValueError, msg=key) as caught:
                mod10.run_view_leak_check(swapped)
            self.assertIn("canary", str(caught.exception), key)
        clean = dict(base)
        clean["view_contents"] = [{
            "activity": "stated", "first_seen_day": 1, "delay": 0}]
        self.assertTrue(
            mod10.run_view_leak_check(clean)["reportable"])


class TestProjectionCleaningEffect(unittest.TestCase):
    def _state(self, features, rule_records=None):
        return {
            "agent_identifier": "agent-r3fix4-1",
            "day": 1,
            "feature_values": features,
            "rule_records": list(rule_records or ()),
        }

    def test_gap_keys_stripped_from_feature_values(self):
        for key in GAP_KEYS:
            projected = mod04.project_detection_input(
                self._state({"activity": 1, key: "secret"}))
            self.assertNotIn(key, projected["feature_values"], key)
            self.assertEqual(
                projected["feature_values"].get("activity"), 1, key)

    def test_gap_keys_stripped_at_depth_and_in_rule_records(self):
        projected = mod04.project_detection_input(self._state(
            {"activity": 1, "nested": {"groundtruth": "secret",
                                        "canary_token": "secret",
                                        "kept": 2}},
            rule_records=[{"kind": "daily_record",
                           "detail": {"xcanaryx": "secret",
                                      "my_groundtruth_value": "secret",
                                      "kept": 3}}]))
        nested = projected["feature_values"]["nested"]
        self.assertNotIn("groundtruth", nested)
        self.assertNotIn("canary_token", nested)
        self.assertEqual(nested.get("kept"), 2)
        detail = projected["rule_records"][0]["detail"]
        self.assertNotIn("xcanaryx", detail)
        self.assertNotIn("my_groundtruth_value", detail)
        self.assertEqual(detail.get("kept"), 3)


if __name__ == "__main__":
    unittest.main()

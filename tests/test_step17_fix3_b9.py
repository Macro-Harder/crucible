"""Step 17 fix wave 3, Builder 9 defect tests. Slice 9, the
replay and package surface rows: FW3-25, FW3-39, FW3-50.

Written before any product file of this slice changed. Each
defect test reproduces the filing defect of its row on the
uncured tree; each control pins a standing that already holds
and must still hold after the cure.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

import crucible
import crucible.mod01 as mod01
import crucible.mod10 as mod10
import crucible.mod13 as mod13


def _facts():
    fields = list(mod01.state_hash_field_list())
    facts = {field: "value for " + field for field in fields}
    facts["headline_unit"] = {"unit": "unit-1"}
    return fields, facts


class TestFW325ReplayComparability(unittest.TestCase):
    def test_defect_non_records_state_undelivered(self):
        result = mod13.replay_check(None, None)
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], [])
        self.assertIsNot(comp["comparable"], True)
        self.assertIn("undelivered", comp["comparison_standing"])
        self.assertIsNot(result["comparable"], True)
        self.assertFalse(result["equality_observation_reported"])

    def test_defect_small_mappings_state_undelivered(self):
        result = mod13.replay_check({"a": 1}, {"a": 1})
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], [])
        self.assertIn("undelivered", comp["comparison_standing"])
        self.assertFalse(result["equality_observation_reported"])

    def test_defect_only_present_items_stand_checked(self):
        first = {"code_version": "v1"}
        second = {"code_version": "v1"}
        result = mod13.replay_check(first, second)
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], ["code_version"])
        self.assertTrue(comp["comparable"])
        self.assertTrue(result["comparable"])

    def test_defect_present_item_difference_names_only_it(self):
        first = {"code_version": "v1"}
        second = {"code_version": "v2"}
        result = mod13.replay_check(first, second)
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], ["code_version"])
        self.assertEqual(comp["differing_items"], ["code_version"])
        self.assertTrue(result["not_comparable"])
        self.assertIn("code_version", result["not_comparable_on"])

    def test_defect_item_present_on_one_side_only_differs(self):
        result = mod13.replay_check(
            {"build_identifier": "b1"}, {"a": 1})
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], ["build_identifier"])
        self.assertEqual(comp["differing_items"], ["build_identifier"])
        self.assertTrue(result["not_comparable"])

    def test_defect_resume_check_states_undelivered(self):
        result = mod13.resume_check(None, None)
        comp = result["comparability"]
        self.assertEqual(comp["items_checked"], [])
        self.assertIsNot(comp["comparable"], True)
        self.assertIn("undelivered", comp["comparison_standing"])
        self.assertFalse(result["equality_observation_reported"])

    def test_control_full_comparability_agreement(self):
        fields, facts = _facts()
        first = dict(facts)
        second = dict(facts)
        for name in mod13.COMPARABILITY_ITEMS:
            first[name] = "same value for " + name
            second[name] = "same value for " + name
        result = mod13.replay_check(first, second)
        self.assertTrue(result["deterministic"])
        self.assertTrue(result["comparable"])
        self.assertEqual(
            result["comparability"]["items_checked"],
            list(mod13.COMPARABILITY_ITEMS))

    def test_control_differing_field_still_marked(self):
        fields, facts = _facts()
        first = dict(facts)
        second = dict(facts)
        for name in mod13.COMPARABILITY_ITEMS:
            first[name] = "same value for " + name
            second[name] = "same value for " + name
        second[fields[0]] = "a different stored value"
        result = mod13.replay_check(first, second)
        self.assertFalse(result["deterministic"])
        self.assertTrue(result["marked_non_deterministic"])


class TestFW350Mod10ReplayCheck(unittest.TestCase):
    def test_defect_one_sided_full_then_empty(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "ok"}, {})
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])
        self.assertIn("undelivered", result["comparison_standing"])

    def test_defect_one_sided_empty_then_full(self):
        result = mod10.replay_check(
            {}, {"record": {"a": 1}, "verdict": "ok"})
        self.assertIn("undelivered", result["comparison_standing"])

    def test_defect_split_parts_state_undelivered(self):
        result = mod10.replay_check(
            {"verdict": "ok"}, {"record": {"a": 1}})
        self.assertIn("undelivered", result["comparison_standing"])

    def test_defect_partial_part_states_undelivered(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "ok"},
            {"record": {"a": 1}})
        self.assertTrue(result["record_level_equal"])
        self.assertIn("undelivered", result["comparison_standing"])
        self.assertIn("verdict", result["comparison_standing"])

    def test_control_neither_side_undelivered(self):
        result = mod10.replay_check({}, {})
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])
        self.assertIn("undelivered", result["comparison_standing"])

    def test_control_equal_records_no_standing_entry(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 1}, "verdict": "x"})
        self.assertTrue(result["record_level_equal"])
        self.assertTrue(result["verdict_level_equal"])
        self.assertNotIn("comparison_standing", result)

    def test_control_differing_records_no_standing_entry(self):
        result = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 2}, "verdict": "y"})
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])
        self.assertNotIn("comparison_standing", result)

    def test_control_present_none_values_compare(self):
        result = mod10.replay_check(
            {"record": None, "verdict": None},
            {"record": None, "verdict": None})
        self.assertTrue(result["record_level_equal"])
        self.assertTrue(result["verdict_level_equal"])
        self.assertNotIn("comparison_standing", result)


class TestFW339PackageSurface(unittest.TestCase):
    def test_defect_builders_in_mod01_all(self):
        self.assertIn("build_sweep_point", mod01.__all__)
        self.assertIn("build_run_record", mod01.__all__)

    def test_defect_builders_on_package_surface(self):
        self.assertTrue(hasattr(crucible, "build_sweep_point"))
        self.assertTrue(hasattr(crucible, "build_run_record"))

    def test_defect_package_builders_are_the_mod01_builders(self):
        self.assertIs(
            crucible.build_sweep_point, mod01.build_sweep_point)
        self.assertIs(crucible.build_run_record, mod01.build_run_record)

    def test_defect_builders_in_package_all(self):
        self.assertIn("build_sweep_point", crucible.__all__)
        self.assertIn("build_run_record", crucible.__all__)

    def test_control_reexport_control_names_present(self):
        self.assertTrue(hasattr(crucible, "validate_record"))
        self.assertTrue(hasattr(crucible, "minimal_valid_instance"))
        self.assertTrue(hasattr(crucible, "minimal_valid_family_record"))

    def test_control_guide_total_matches_summed_total(self):
        import importlib
        modules = (
            "mod01", "mod02", "mod03", "mod04", "mod05", "mod06",
            "mod07", "mod08", "mod09", "mod10", "mod11", "mod12",
            "mod13", "mod14", "mod16")
        total = 0
        for name in modules:
            module = importlib.import_module("crucible." + name)
            total += len(module.__all__)
        self.assertIn(
            "exporting %d names in total" % total, crucible.__doc__)


if __name__ == "__main__":
    unittest.main()

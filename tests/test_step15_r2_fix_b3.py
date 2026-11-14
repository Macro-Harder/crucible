import os
import unittest

import crucible.mod03 as mod03
import crucible.mod04 as mod04

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestR1008HomoglyphParity(unittest.TestCase):
    def test_named_letters_read_as_in_mod03(self):
        cases = (
            ("м", "m"), ("в", "b"), ("н", "h"), ("т", "t"),
            ("β", "b"), ("γ", "g"), ("δ", "d"), ("λ", "l"),
            ("μ", "m"), ("σ", "s"), ("υ", "u"), ("ν", "n"),
        )
        for letter, reading in cases:
            dressed = "x" + letter + "y"
            expected = "x" + reading + "y"
            self.assertIn(expected, mod04._folded_readings(dressed), dressed)
            self.assertIn(
                expected, mod03._folded_readings(dressed), dressed)

    def test_full_mod03_map_parity(self):
        for letter, reading in mod03._HOMOGLYPH_MAP.items():
            dressed = "x" + letter + "y"
            expected = "x" + reading + "y"
            self.assertIn(expected, mod04._folded_readings(dressed), letter)

    def test_dressed_barred_keys_barred(self):
        keys = (
            "мembership", "laвel", "is_нonest", "ground_тruth",
            "laβel", "γround_truth", "grounδ_truth", "λabel",
            "μembership", "σleeper", "ground_trυth", "caνary",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(mod04.view_record_carries_barred_field(
                {"view_contents": [{key: "v"}]}), key)


class TestR1010LeetBeforeDropping(unittest.TestCase):
    def test_symbol_leet_entries_fire(self):
        self.assertIn("canary", mod04._folded_readings("c@nary"))
        self.assertIn("sleeper", mod04._folded_readings("$leeper"))
        self.assertTrue(mod04._is_barred_key("c@nary"))
        self.assertTrue(mod04._is_barred_key("$leeper"))
        self.assertTrue(mod04._is_barred_key("member$hip"))

    def test_digit_one_reads_as_i_and_as_l(self):
        readings = mod04._folded_readings("x1y")
        self.assertIn("xiy", readings)
        self.assertIn("xly", readings)
        self.assertTrue(mod04._is_barred_key("membersh1p"))
        self.assertTrue(mod04._is_barred_key("1abel"))


class EvilDict(dict):
    def items(self):
        return iter(())

    def keys(self):
        return iter(())

    def values(self):
        return iter(())


class TestR1016BaseDictIteration(unittest.TestCase):
    def test_overridden_items_and_keys_do_not_hide_barred(self):
        top = EvilDict({"membership": "x"})
        self.assertTrue(mod04.view_record_carries_barred_field(top))
        nested = {"view_contents": [EvilDict({"ground_truth": "x"})]}
        self.assertTrue(mod04.view_record_carries_barred_field(nested))
        grouped = EvilDict(
            {"view_contents": [], "nested": EvilDict({"canary": "x"})})
        self.assertTrue(mod04.view_record_carries_barred_field(grouped))

    def test_clean_evil_dict_stays_clean(self):
        clean = EvilDict({"view_contents": [{"kind": "daily"}]})
        self.assertFalse(mod04.view_record_carries_barred_field(clean))


class TestR1033DelayedPositionCheck(unittest.TestCase):
    def test_delayed_day_reaching_view_day_runs_position_check(self):
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "arising_position": 9, "kind": "delayed late"},
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "arising_position": 2, "kind": "delayed early"},
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "kind": "delayed no position"},
        ]
        selected = mod04.select_view_records(
            records, "viewer-1", 5, delay=-5, as_of_position=5)
        self.assertEqual(
            [item["kind"] for item in selected], ["delayed early"])

    def test_forward_delay_reaching_view_day_runs_position_check(self):
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 3,
             "arising_position": 9, "kind": "forward late"},
            {"viewer_id": "viewer-1", "first_seen_day": 3,
             "arising_position": 1, "kind": "forward early"},
        ]
        selected = mod04.select_view_records(
            records, "viewer-1", 5, delay=2, as_of_position=5)
        self.assertEqual(
            [item["kind"] for item in selected], ["forward early"])


class TestR1034NoCoercion(unittest.TestCase):
    def base(self, **overrides):
        record = {"viewer_id": "viewer-1", "first_seen_day": 3,
                  "arising_position": 1, "kind": "clean"}
        record.update(overrides)
        return record

    def test_clean_control_admitted(self):
        selected = mod04.select_view_records(
            [self.base()], "viewer-1", 5, delay=0, as_of_position=5)
        self.assertEqual(len(selected), 1)

    def test_fractional_boolean_and_string_days_refused(self):
        for bad in (3.5, 3.0, True, "3", None.__class__ and "three"):
            selected = mod04.select_view_records(
                [self.base(first_seen_day=bad)], "viewer-1", 5)
            self.assertEqual(selected, [], repr(bad))

    def test_fractional_boolean_and_string_delay_refused(self):
        for bad in (0.5, 0.0, True, "0"):
            selected = mod04.select_view_records(
                [self.base()], "viewer-1", 5, delay=bad)
            self.assertEqual(selected, [], repr(bad))

    def test_fractional_boolean_and_string_view_day_refused(self):
        for bad in (5.5, 5.0, True, "5"):
            selected = mod04.select_view_records(
                [self.base()], "viewer-1", bad)
            self.assertEqual(selected, [], repr(bad))

    def test_fractional_boolean_and_string_positions_refused(self):
        same_day = {"viewer_id": "viewer-1", "first_seen_day": 5,
                    "kind": "same day"}
        for bad in (2.5, 2.0, True, "2"):
            record = dict(same_day, arising_position=bad)
            selected = mod04.select_view_records(
                [record], "viewer-1", 5, as_of_position=5)
            self.assertEqual(selected, [], repr(bad))
        for bad in (5.5, 5.0, True, "5"):
            record = dict(same_day, arising_position=2)
            selected = mod04.select_view_records(
                [record], "viewer-1", 5, as_of_position=bad)
            self.assertEqual(selected, [], repr(bad))


class TestR1036ProjectionRefusesMalformed(unittest.TestCase):
    def state(self, **overrides):
        state = {"agent_identifier": "agent-1", "day": 1,
                 "feature_values": {"activity": 1},
                 "rule_records": [{"kind": "daily"}]}
        state.update(overrides)
        return state

    def test_valid_and_absent_forms_still_project(self):
        projected = mod04.project_detection_input(self.state())
        self.assertEqual(projected["feature_values"], {"activity": 1})
        projected = mod04.project_detection_input(
            {"agent_identifier": "agent-1", "day": 1})
        self.assertEqual(projected["feature_values"], {})
        self.assertEqual(projected["rule_records"], [])

    def test_non_dict_feature_values_refused_named(self):
        for bad in ([], "text", 7, None, (("a", 1),)):
            with self.assertRaises(mod04.NamedFailure, msg=repr(bad)) as caught:
                mod04.project_detection_input(
                    self.state(feature_values=bad))
            self.assertIn("feature", str(caught.exception))

    def test_non_list_rule_records_refused_named(self):
        for bad in ({}, "text", 7, None, ({"kind": "daily"},)):
            with self.assertRaises(mod04.NamedFailure, msg=repr(bad)) as caught:
                mod04.project_detection_input(
                    self.state(rule_records=bad))
            self.assertIn("rule", str(caught.exception))


class TestR1066WordingPinScope(unittest.TestCase):
    def test_head_assertion_scoped_to_docstring_head(self):
        path = os.path.join(PRODUCT_ROOT, "tests", "test_step15_r2_fix5.py")
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        start = text.index("class TestMod04WordingAct")
        end = text.index("class TestTB15PlanAmendment")
        segment = text[start:end]
        head_part = segment.split("test_run_tracer_cut")[0]
        self.assertIn("docstring", head_part)


if __name__ == "__main__":
    unittest.main()

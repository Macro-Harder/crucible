import unittest

import crucible.mod04 as mod04


class HideAllList(list):
    def __iter__(self):
        return iter(())


class HideAllTuple(tuple):
    def __iter__(self):
        return iter(())


def _frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


def _deep_dict(depth):
    value = "leaf"
    for _ in range(depth):
        value = {"k": value}
    return value


class TestR2001BaseIteration(unittest.TestCase):
    def test_plain_control_barred(self):
        record = {"x": [{"membership": 1}]}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_hide_all_list_does_not_hide_barred(self):
        record = {"x": HideAllList([{"membership": 1}])}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_hide_all_tuple_does_not_hide_barred(self):
        record = {"x": HideAllTuple(({"membership": 1},))}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_hide_all_list_clean_stays_clean(self):
        record = {"x": HideAllList([{"kind": 1}])}
        self.assertFalse(mod04.view_record_carries_barred_field(record))

    def test_projection_strips_barred_inside_hide_all_list(self):
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {
                "x": HideAllList([{"membership": "v", "keep": 1}]),
            },
            "rule_records": [],
        }
        projected = mod04.project_detection_input(state)
        self.assertNotIn("membership", repr(projected))

    def test_projection_strips_barred_inside_hide_all_tuple(self):
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {
                "x": HideAllTuple(({"ground_truth": "v", "keep": 1},)),
            },
            "rule_records": [],
        }
        projected = mod04.project_detection_input(state)
        self.assertNotIn("ground_truth", repr(projected))

    def test_value_appears_reads_through_base_iteration(self):
        node = {"x": HideAllList(["canary-secret"])}
        self.assertTrue(mod04._value_appears("canary-secret", node))
        node = {"x": HideAllTuple(("canary-secret",))}
        self.assertTrue(mod04._value_appears("canary-secret", node))


class TestR2022NegativeDelayPositionCheck(unittest.TestCase):
    def test_future_record_pulled_before_view_day_runs_position_check(self):
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "arising_position": 99, "kind": "future late"},
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "arising_position": 0, "kind": "future early"},
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "kind": "future no position"},
        ]
        selected = mod04.select_view_records(
            records, "viewer-1", 5, delay=-6, as_of_position=1)
        self.assertEqual(
            [item["kind"] for item in selected], ["future early"])

    def test_genuine_before_view_record_still_admitted(self):
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 3,
             "arising_position": 99, "kind": "earlier day"},
        ]
        selected = mod04.select_view_records(
            records, "viewer-1", 5, delay=0, as_of_position=1)
        self.assertEqual(
            [item["kind"] for item in selected], ["earlier day"])

    def test_delayed_day_equal_view_day_still_checked(self):
        records = [
            {"viewer_id": "viewer-1", "first_seen_day": 10,
             "arising_position": 99, "kind": "delayed late"},
        ]
        selected = mod04.select_view_records(
            records, "viewer-1", 5, delay=-5, as_of_position=1)
        self.assertEqual(selected, [])


class TestR2023HoldViewBound(unittest.TestCase):
    def test_shallow_view_still_holds(self):
        held = mod04.hold_view({"form": "ViewRecord", "x": {"y": 1}})
        self.assertTrue(held["held"])
        self.assertFalse(held["released"])

    def test_deep_view_refused_named(self):
        record = {"payload": _deep_dict(150)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view(record)

    def test_very_deep_view_refused_named_not_recursion(self):
        record = {"payload": _deep_dict(2000)}
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view(record)

    def test_cyclic_view_refused_named(self):
        record = {"form": "ViewRecord"}
        record["self"] = record
        with self.assertRaises(mod04.NamedFailure):
            mod04.hold_view(record)


class TestR2024ProjectionFrozensetBound(unittest.TestCase):
    def _state(self, value):
        return {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {"x": value},
            "rule_records": [],
        }

    def test_shallow_frozenset_chain_projects(self):
        projected = mod04.project_detection_input(
            self._state(_frozenset_chain(10)))
        self.assertIn("x", projected["feature_values"])

    def test_frozenset_chain_past_bound_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(
                self._state(_frozenset_chain(150)))

    def test_frozenset_chain_far_past_bound_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(
                self._state(_frozenset_chain(500)))


class TestR2045BuildViewRecordContentsForm(unittest.TestCase):
    def test_list_contents_still_written(self):
        record = mod04.build_view_record(
            contents=[{"first_seen_day": 1, "delay": 0}])
        self.assertEqual(len(record["view_contents"]), 1)

    def test_tuple_contents_still_written(self):
        record = mod04.build_view_record(
            contents=({"first_seen_day": 1, "delay": 0},))
        self.assertEqual(len(record["view_contents"]), 1)

    def test_none_contents_still_written(self):
        record = mod04.build_view_record(contents=None)
        self.assertEqual(record["view_contents"], [])

    def test_string_contents_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents="abc")

    def test_dict_contents_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents={"a": 1, "b": 2})

    def test_single_record_dict_contents_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(
                contents={"first_seen_day": 1, "delay": 0})

    def test_non_iterable_contents_refused_named(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.build_view_record(contents=123)


class TestR2051WiderBarredReading(unittest.TestCase):
    def test_named_composites_barred(self):
        keys = (
            "m\u03b7mb-3rship",
            "gr0un\u0434_tr-uth",
            "\u0433round._7ruth",
            "i\u03c2_hon-3st",
            "m3mbe-rs\u0445ip",
            "\u1d0d3mbe_rship",
            "\u00a3a-b3l",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(
                mod04.view_record_carries_barred_field({"x": [{key: 1}]}),
                key)

    def test_transliteration_only_letters_barred(self):
        keys = (
            "mem\u0431ership",
            "membersh\u0438p",
            "membershi\u043f",
            "membe\u0440ship",
            "is_\u03c7onest",
            "membershi\u03c0",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_small_capital_and_phonetic_letters_barred(self):
        keys = (
            "m\u1d07mbership",
            "\u0262round_truth",
            "membe\u0280ship",
            "la\u0299el",
            "is_\u029conest",
            "\u029fabel",
            "membersh\u026ap",
            "ground_\u1d1bruth",
            "membershi\u1d18",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_armenian_letters_barred(self):
        keys = (
            "gr\u0585und_truth",
            "ca\u0578ary",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_extra_symbol_letters_barred(self):
        keys = (
            "m\u20acmbership",
            "!abel",
            "|abel",
            "member\u0452hip",
            "is_\u0493onest",
        )
        for key in keys:
            self.assertTrue(mod04._is_barred_key(key), key)

    def test_projection_strips_wider_dress(self):
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {"m\u03b7mb-3rship": "v", "activity": 1},
            "rule_records": [],
        }
        projected = mod04.project_detection_input(state)
        self.assertEqual(projected["feature_values"], {"activity": 1})

    def test_clean_names_still_admitted(self):
        for key in ("activity", "labelled", "keep"):
            self.assertFalse(mod04._is_barred_key(key), key)


if __name__ == "__main__":
    unittest.main()

import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10


class LyingViewer(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class AddZeroDay(int):
    def __add__(self, other):
        return 0

    __radd__ = __add__


class LyingComparisonDay(int):
    def __add__(self, other):
        return LyingComparisonDay(int(self) + int(other))

    __radd__ = __add__

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False


class LyingArising(int):
    def __gt__(self, other):
        return False


class LyingDeepcopyPart:
    def __deepcopy__(self, memo):
        return {"membership": "barred-materialised"}

    def __repr__(self):
        return "LyingDeepcopyPart()"


def tuple_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


def frozenset_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = frozenset([value])
    return value


def state_with_features(features):
    return {
        "agent_identifier": "agent-1",
        "day": 1,
        "feature_values": features,
        "rule_records": [],
    }


class TestR4006BaseJudgement(unittest.TestCase):
    def test_viewer_str_subclass_equality_does_not_admit(self):
        record = {
            "viewer_id": LyingViewer("someone-else"),
            "first_seen_day": 1,
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5)
        self.assertEqual([], selected)

    def test_first_seen_day_addition_does_not_admit(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": AddZeroDay(999),
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5)
        self.assertEqual([], selected)

    def test_source_probe_day_999_view_day_5(self):
        record = {"viewer_id": "viewer-1", "first_seen_day": AddZeroDay(999)}
        self.assertEqual(
            [], mod04.select_view_records([record], "viewer-1", as_of_day=5))

    def test_first_seen_comparison_does_not_skip_position_check(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": LyingComparisonDay(9),
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5, as_of_position=3)
        self.assertEqual([], selected)

    def test_arising_position_comparison_does_not_admit(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": 5,
            "arising_position": LyingArising(999),
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5, as_of_position=3)
        self.assertEqual([], selected)

    def test_plain_controls_admitted_both_ways(self):
        record = {"viewer_id": "viewer-1", "first_seen_day": 1}
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5)
        self.assertEqual(1, len(selected))
        self.assertEqual("viewer-1", selected[0]["viewer_id"])
        on_day = {
            "viewer_id": "viewer-1",
            "first_seen_day": 5,
            "arising_position": 3,
        }
        selected = mod04.select_view_records(
            [on_day], "viewer-1", as_of_day=5, as_of_position=3)
        self.assertEqual(1, len(selected))
        other = {"viewer_id": "someone-else", "first_seen_day": 1}
        self.assertEqual(
            [], mod04.select_view_records(
                [other], "viewer-1", as_of_day=5))
        late = {"viewer_id": "viewer-1", "first_seen_day": 9}
        self.assertEqual(
            [], mod04.select_view_records(
                [late], "viewer-1", as_of_day=5))


class TestR4009CleaningKeyWalk(unittest.TestCase):
    def test_tuple_key_chains_past_bound_refused_named(self):
        for depth in (101, 102, 105, 150):
            state = state_with_features(
                {"wrap": {tuple_chain(depth): 1}})
            with self.assertRaises(mod04.NamedFailure, msg=str(depth)):
                mod04.project_detection_input(state)

    def test_frozenset_key_chain_past_bound_refused_named(self):
        for depth in (101, 150, 300):
            state = state_with_features(
                {"wrap": {frozenset_chain(depth): 1}})
            with self.assertRaises(mod04.NamedFailure, msg=str(depth)):
                mod04.project_detection_input(state)

    def test_top_level_key_chain_past_bound_refused_named(self):
        for depth in (105, 200):
            state = state_with_features({tuple_chain(depth): 1})
            with self.assertRaises(mod04.NamedFailure, msg=str(depth)):
                mod04.project_detection_input(state)

    def test_key_chain_within_bound_control_delivered(self):
        key = tuple_chain(50)
        state = state_with_features({"wrap": {key: 7}})
        projected = mod04.project_detection_input(state)
        self.assertEqual(7, projected["feature_values"]["wrap"][key])

    def test_value_position_past_bound_control_still_refused(self):
        value = "leaf"
        for _ in range(105):
            value = [value]
        state = state_with_features({"wrap": value})
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(state)


class TestR4013GuardedCopy(unittest.TestCase):
    def test_select_view_records_lying_deepcopy_no_barred_dict(self):
        part = LyingDeepcopyPart()
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": 1,
            "payload": part,
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5)
        self.assertEqual(1, len(selected))
        self.assertIs(part, selected[0]["payload"])
        self.assertFalse(mod04.view_record_carries_barred_field(selected[0]))

    def test_hold_view_lying_deepcopy_no_barred_dict(self):
        part = LyingDeepcopyPart()
        view_record = {"viewer_identifier": "viewer-1", "payload": part}
        held = mod04.hold_view(view_record)
        self.assertIs(part, held["view_record"]["payload"])
        self.assertFalse(
            mod04.view_record_carries_barred_field(held["view_record"]))

    def test_guarded_copy_control_is_a_real_copy(self):
        record = {
            "viewer_id": "viewer-1",
            "first_seen_day": 1,
            "payload": {"items": [1, 2]},
        }
        selected = mod04.select_view_records(
            [record], "viewer-1", as_of_day=5)
        self.assertEqual({"items": [1, 2]}, selected[0]["payload"])
        record["payload"]["items"].append(3)
        self.assertEqual({"items": [1, 2]}, selected[0]["payload"])


class TestR4031SmallCapitals(unittest.TestCase):
    def test_each_small_capital_reading_bars(self):
        cases = (
            "m\u1d31mbership",
            "\u1d38abel",
            "is_h\u1d3cnest",
            "ground_\u1d40ruth",
        )
        for key in cases:
            self.assertIn(
                key, [c for c in cases])
            self.assertTrue(mod04._is_barred_key(key), key)
            self.assertTrue(
                mod04.view_record_carries_barred_field({key: 1}), key)

    def test_readings_recorded(self):
        self.assertIn("membership", mod04._folded_readings("m\u1d31mbership"))
        self.assertIn("label", mod04._folded_readings("\u1d38abel"))
        self.assertIn("ishonest", mod04._folded_readings("is_h\u1d3cnest"))
        self.assertIn(
            "groundtruth", mod04._folded_readings("ground_\u1d40ruth"))


class TestR4015CompositeFoldMod04(unittest.TestCase):
    def test_membership_transliteration_and_homoglyph_in_one_word(self):
        key = "member\u0441hi\u0440"
        self.assertTrue(mod04._is_barred_key(key), key)
        self.assertIn("membership", mod04._folded_readings(key))

    def test_canary_three_positions_mixed_readings(self):
        key = "\u0441ana\u0440\u0443"
        self.assertTrue(mod04._is_barred_key(key), key)
        self.assertIn("canary", mod04._folded_readings(key))

    def test_mod10_control_bars_both(self):
        for key in ("member\u0441hi\u0440", "\u0441ana\u0440\u0443"):
            variants = mod10._fold_variants(key)
            self.assertTrue(
                any(
                    "membership" in variant or "canary" in variant
                    for variant in variants),
                key)

    def test_plain_and_single_map_controls(self):
        self.assertTrue(mod04._is_barred_key("membership"))
        self.assertTrue(mod04._is_barred_key("member\u0441hip"))
        self.assertTrue(mod04._is_barred_key("membe\u0440ship"))
        self.assertFalse(mod04._is_barred_key("ordinary"))


class TestR4018EnAndErFoldMod04(unittest.TestCase):
    def test_is_honest_en_at_h_and_n_positions(self):
        key = "is_\u043do\u043dest"
        self.assertTrue(mod04._is_barred_key(key), key)
        self.assertIn("ishonest", mod04._folded_readings(key))

    def test_sleeper_er_at_p_and_final_r(self):
        key = "slee\u0440e\u0440"
        self.assertTrue(mod04._is_barred_key(key), key)
        self.assertIn("sleeper", mod04._folded_readings(key))

    def test_single_position_controls(self):
        self.assertTrue(mod04._is_barred_key("is_\u043donest"))
        self.assertTrue(mod04._is_barred_key("is_hones\u0442"))
        self.assertTrue(mod04._is_barred_key("sleeper"))
        self.assertFalse(mod04._is_barred_key("ordinary"))


if __name__ == "__main__":
    unittest.main()

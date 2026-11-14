import unittest

import crucible.mod04 as mod04


WANTED = {"viewer_id": "viewer-1", "first_seen_day": 1}
OTHER = {"viewer_id": "someone-else", "first_seen_day": 1}

CORE = "membe" + "\u0440" + "\u0441" + "\u043d" + "i" + "\u0440"
SHORT_I = "\u0439"
CHI = "\u03c7"
DRESSED_CANARY = "\u0441" + "a" + "\u043d" + "a" + "\u0440" + "\u0439"


class YieldingList(list):
    def __init__(self, stored, yielded):
        super().__init__(stored)
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


def list_chain(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = [value]
    return value


def tuple_chain_key(length, leaf="leaf"):
    value = leaf
    for _ in range(length):
        value = (value,)
    return value


def state_with(features):
    return {
        "agent_identifier": "a1",
        "day": 1,
        "feature_values": features,
        "rule_records": [],
    }


class TestR5007SelectViewRecordsBaseIteration(unittest.TestCase):
    def test_defect_yielded_wanted_record_not_in_storage_excluded(self):
        handed = YieldingList([dict(OTHER)], [dict(WANTED)])
        self.assertEqual(
            mod04.select_view_records(handed, "viewer-1", 5), [])

    def test_defect_stored_wanted_record_hidden_by_empty_yield(self):
        handed = YieldingList([dict(WANTED)], [])
        selected = mod04.select_view_records(handed, "viewer-1", 5)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["viewer_id"], "viewer-1")

    def test_control_plain_list_wanted_selected(self):
        selected = mod04.select_view_records(
            [dict(WANTED)], "viewer-1", 5)
        self.assertEqual(len(selected), 1)

    def test_control_plain_list_other_viewer_excluded(self):
        self.assertEqual(
            mod04.select_view_records([dict(OTHER)], "viewer-1", 5), [])


class TestR5012ShortIReading(unittest.TestCase):
    def test_defect_composite_canary_dress_barred(self):
        self.assertTrue(mod04._is_barred_key(DRESSED_CANARY))

    def test_defect_single_dress_canary_barred(self):
        self.assertTrue(mod04._is_barred_key("canar" + SHORT_I))

    def test_defect_folded_readings_carry_canary(self):
        self.assertIn("canary", mod04._folded_readings(DRESSED_CANARY))

    def test_defect_compound_key_needs_both_readings(self):
        compound = SHORT_I + "s_honest_" + DRESSED_CANARY
        self.assertTrue(mod04._is_barred_key(compound))

    def test_defect_end_to_end_view_record_read(self):
        record = {"contents": {DRESSED_CANARY: 1}}
        self.assertTrue(mod04.view_record_carries_barred_field(record))

    def test_control_plain_canary_barred(self):
        self.assertTrue(mod04._is_barred_key("canary"))

    def test_control_plain_canari_not_barred(self):
        self.assertFalse(mod04._is_barred_key("canari"))

    def test_control_clean_field_not_barred(self):
        self.assertFalse(mod04._is_barred_key("clean_field"))


class TestR5013CountingBasis(unittest.TestCase):
    def test_defect_short_i_filler_past_bound_barred_at_mod04(self):
        key = CORE + SHORT_I * 13
        self.assertTrue(mod04._is_barred_key(key))

    def test_control_chi_filler_past_bound_barred_at_mod04(self):
        key = CORE + CHI * 13
        self.assertTrue(mod04._is_barred_key(key))

    def test_control_core_alone_barred(self):
        self.assertTrue(mod04._is_barred_key(CORE))

    def test_control_plain_membership_barred(self):
        self.assertTrue(mod04._is_barred_key("membership"))

    def test_control_clean_key_with_short_i_filler_not_barred(self):
        self.assertFalse(
            mod04._is_barred_key("activity" + SHORT_I * 13))


class TestR5031CleaningCountingBasis(unittest.TestCase):
    def test_defect_list_chain_101_as_top_level_value_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(
                state_with({"feature": list_chain(101)}))

    def test_control_tuple_chain_key_101_at_top_level_refused(self):
        with self.assertRaises(mod04.NamedFailure):
            mod04.project_detection_input(
                state_with({tuple_chain_key(101): 1}))

    def test_control_list_chain_100_as_top_level_value_delivered(self):
        result = mod04.project_detection_input(
            state_with({"feature": list_chain(100)}))
        self.assertIn("feature", result["feature_values"])

    def test_control_tuple_chain_key_100_at_top_level_delivered(self):
        result = mod04.project_detection_input(
            state_with({tuple_chain_key(100): 1}))
        self.assertEqual(len(result["feature_values"]), 1)


if __name__ == "__main__":
    unittest.main()

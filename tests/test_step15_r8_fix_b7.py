"""Step 15 rerun fix wave 7, seat 7.

Pins for register rows R7-013 and R7-022. Each pin was written
before its cure and the failing counts on the unmodified tree
stand recorded in the paper for this seat.
"""
import unittest

from crucible import mod10
from crucible import mod12
from crucible import mod14


class LyingStr(str):
    """A string key storing one name while its own string
    reading reports another name."""

    def __str__(self):
        return "figure"


def screening_record(extra):
    record = {
        "run_class": "screening",
        "seed_domain": "screening",
    }
    record.update(extra)
    return record


class TestR7013Mod10HandedStringReadings(unittest.TestCase):
    def test_lying_amount_key_matches_amount(self):
        self.assertTrue(
            mod10._money_key_matches(LyingStr("amount"), "amount"))

    def test_lying_amount_pair_carries(self):
        self.assertTrue(mod10._carries_real_money_field(
            {LyingStr("amount"): 10, "currency": "usd"}))

    def test_lying_realmoney_key_carries_marker(self):
        self.assertTrue(mod10._carries_real_money_field(
            {LyingStr("realmoney"): 5}))

    def test_lying_amount_pair_refused_at_retention(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-r8-b7-mod10-amount",
                "nested": {LyingStr("amount"): 10,
                           "currency": "usd"}})

    def test_lying_realmoney_refused_at_retention(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-r8-b7-mod10-marker",
                "nested": {LyingStr("realmoney"): 5}})

    def test_plain_amount_pair_refused_control(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-r8-b7-mod10-plain",
                "amount": 5, "currency": "usd"})

    def test_harmless_lying_key_retained_control(self):
        store = mod10.new_store()
        store.retain_run_record({
            "run_id": "run-r8-b7-mod10-clean",
            LyingStr("figure"): 5})
        back = store.read_run_record("run-r8-b7-mod10-clean")
        self.assertEqual(back["figure"], 5)


class TestR7013Mod12HandedStringReadings(unittest.TestCase):
    def test_lying_money_key_matches_money(self):
        self.assertTrue(
            mod12._folded_name_matches(LyingStr("money"), "money"))

    def test_lying_amount_pair_carries_barred_value(self):
        self.assertTrue(mod12._carries_barred_money_value(
            {"nested": {LyingStr("amount"): 10,
                         "currency": "usd"}}))

    def test_lying_amount_pair_record_refused(self):
        self.assertFalse(mod12.validate_run_record(
            screening_record(
                {"nested": {LyingStr("amount"): 10,
                             "currency": "usd"}})))

    def test_lying_realmoney_record_refused(self):
        self.assertFalse(mod12.validate_run_record(
            screening_record(
                {"nested": {LyingStr("realmoney"): 5}})))

    def test_lying_anchor_key_at_four_values_refused(self):
        self.assertFalse(mod12.validate_run_record(
            screening_record(
                {LyingStr("anchor_scenario_values"):
                 ["a", "b", "c", "d"]})))

    def test_lying_anchor_key_at_three_values_control(self):
        self.assertTrue(mod12.validate_run_record(
            screening_record(
                {LyingStr("anchor_scenario_values"):
                 ["a", "b", "c"]})))

    def test_plain_anchor_at_four_values_refused_control(self):
        self.assertFalse(mod12.validate_run_record(
            screening_record(
                {"anchor_scenario_values": ["a", "b", "c", "d"]})))

    def test_harmless_lying_key_record_control(self):
        self.assertTrue(mod12.validate_run_record(
            screening_record({LyingStr("figure"): 5})))


class TestR7013Mod14PilotHandedStringReadings(unittest.TestCase):
    def test_lying_key_form_reads_stored_characters(self):
        self.assertEqual(
            mod14._pilot_key_form(LyingStr("money")), "money")

    def test_lying_money_dict_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {LyingStr("money"): 5})

    def test_lying_money_set_element_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {LyingStr("money")})

    def test_lying_money_list_pair_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", [[LyingStr("money"), 5]])

    def test_lying_money_tuple_dict_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run(
                "timing", {(LyingStr("money"), "x"): 1})

    def test_lying_money_nested_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run(
                "timing", {"outer": [{LyingStr("money"): 5}]})

    def test_lying_anchor_set_dict_key_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {LyingStr("anchor_set"): 5})

    def test_plain_money_dict_key_refused_control(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"money": 5})

    def test_harmless_lying_key_delivered_control(self):
        output = mod14.pilot_run(
            "timing", {LyingStr("figure"): 5})
        self.assertEqual(
            output["confinement_label"], "pilot confined")
        self.assertEqual(output["figure"], 5)

    def test_plain_value_under_harmless_key_control(self):
        output = mod14.pilot_run("timing", {"note": "money"})
        self.assertEqual(
            output["confinement_label"], "pilot confined")


class TestR7022DoubleExclamationSegments(unittest.TestCase):
    def test_decomposed_pair_segments_stand_position_by_position(self):
        segments = mod10._money_segments_by_character(
            "rea\u203cmoney")
        self.assertEqual(len(segments), 10)
        self.assertEqual(segments[3], {"l", ""})
        self.assertEqual(segments[4], {"l", ""})

    def test_double_exclamation_key_matches_realmoney(self):
        self.assertTrue(mod10._money_key_matches(
            "rea\u203cmoney", "realmoney"))

    def test_double_exclamation_key_carries_marker(self):
        self.assertTrue(mod10._money_key_carries(
            "rea\u203cmoney", "realmoney"))

    def test_double_exclamation_field_carries(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"rea\u203cmoney": 5}))

    def test_double_exclamation_refused_at_retention(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-r8-b7-mod10-double",
                "rea\u203cmoney": 5})

    def test_plain_realmoney_carries_control(self):
        self.assertTrue(mod10._money_key_carries(
            "realmoney", "realmoney"))

    def test_single_exclamation_l_reading_control(self):
        self.assertTrue(mod10._money_key_carries(
            "rea!money", "realmoney"))


if __name__ == "__main__":
    unittest.main()

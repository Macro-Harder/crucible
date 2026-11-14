import unittest

import crucible.mod10 as mod10


class LyingStr(str):
    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj.reported = reported
        return obj

    def __str__(self):
        return self.reported


class NamedKey:
    def __init__(self, carried, reported):
        self.carried = carried
        self.reported = reported

    def __str__(self):
        return self.reported

    def __hash__(self):
        return hash(self.carried)

    def __eq__(self, other):
        return isinstance(other, NamedKey) and other.carried == self.carried


class LyingCheckpoint(dict):
    def __init__(self, stored, reported_get, reported_items):
        dict.__init__(self, stored)
        self.reported_get = reported_get
        self.reported_items = reported_items

    def get(self, key, default=None):
        if key in self.reported_get:
            return self.reported_get[key]
        return dict.get(self, key, default)

    def items(self):
        return list(self.reported_items)


RETAINED = {
    "run_identifier": "r9-b10-run",
    "simulated_day": 3,
    "store_kind": "sweep",
    "payload": "original",
}
RETAINED_FORM_ITEMS = [
    ("run_identifier", "r9-b10-run"),
    ("simulated_day", 3),
    ("payload", "original"),
]
RETAINED_GET = {
    "run_identifier": "r9-b10-run",
    "simulated_day": 3,
    "store_kind": "sweep",
}


class TestR8008ViewSegments(unittest.TestCase):
    def test_defect_storing_clean_reporting_barred_not_barred(self):
        key = LyingStr("cleanvalue", "canaryvalue")
        self.assertFalse(mod10._combined_view_key_barred(key))
        self.assertFalse(mod10._carries_barred_key({key: 1}))

    def test_defect_storing_barred_reporting_clean_is_barred(self):
        key = LyingStr("canaryvalue", "cleanvalue")
        self.assertTrue(mod10._combined_view_key_barred(key))

    def test_control_plain_clean_not_barred(self):
        self.assertFalse(mod10._combined_view_key_barred("cleanvalue"))
        self.assertFalse(mod10._carries_barred_key({"cleanvalue": 1}))

    def test_control_plain_barred_is_barred(self):
        self.assertTrue(mod10._combined_view_key_barred("canaryvalue"))
        self.assertTrue(mod10._carries_barred_key({"canaryvalue": 1}))

    def test_control_storing_barred_reporting_clean_view_key(self):
        key = LyingStr("canaryvalue", "cleanvalue")
        self.assertTrue(mod10._is_barred_view_key(key))


class TestR8009ResumeFromCheckpoint(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()
        mod10.retain_checkpoint(dict(RETAINED))

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_get_and_items_lying_full_tamper_refused(self):
        stored = {
            "run_identifier": "other-run",
            "simulated_day": 9,
            "store_kind": "pilot",
            "payload": "TAMPERED",
        }
        handed = LyingCheckpoint(stored, RETAINED_GET, RETAINED_FORM_ITEMS)
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_defect_items_only_lying_tampered_payload_refused(self):
        stored = {
            "run_identifier": "r9-b10-run",
            "simulated_day": 3,
            "store_kind": "sweep",
            "payload": "TAMPERED",
        }
        handed = LyingCheckpoint(stored, {}, RETAINED_FORM_ITEMS)
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_plain_exact_copy_resumes(self):
        resumed = mod10.resume_from_checkpoint(dict(RETAINED))
        self.assertEqual(dict.get(resumed, "payload"), "original")
        self.assertEqual(dict.get(resumed, "run_identifier"), "r9-b10-run")

    def test_control_plain_tamper_refused(self):
        stored = {
            "run_identifier": "other-run",
            "simulated_day": 9,
            "store_kind": "pilot",
            "payload": "TAMPERED",
        }
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(dict(stored))
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_get_only_lying_honest_items_tamper_refused(self):
        stored = {
            "run_identifier": "r9-b10-run",
            "simulated_day": 3,
            "store_kind": "sweep",
            "payload": "TAMPERED",
        }
        handed = LyingCheckpoint(stored, RETAINED_GET, list(dict.items(stored)))
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal", str(caught.exception))

    def test_control_kind_limb_lying_kind_refused(self):
        kind = LyingStr("pilot", "sweep")
        handed = dict(RETAINED)
        handed["store_kind"] = kind
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)


class TestR8010StoredTextFallback(unittest.TestCase):
    def test_defect_nontext_reporting_amount_matches_nothing(self):
        key = NamedKey("figure", "amount")
        self.assertEqual(mod10._stored_text(key), "")
        self.assertFalse(mod10._money_key_matches(key, "amount"))

    def test_defect_nontext_reporting_amount_no_money_field(self):
        key = NamedKey("figure", "amount")
        record = {key: 10, "currency": "USD"}
        self.assertFalse(mod10._carries_real_money_field(record))

    def test_control_plain_amount_matches(self):
        self.assertTrue(mod10._money_key_matches("amount", "amount"))
        record = {"amount": 10, "currency": "USD"}
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_control_plain_figure_matches_nothing(self):
        self.assertFalse(mod10._money_key_matches("figure", "amount"))
        record = {"figure": 10, "currency": "USD"}
        self.assertFalse(mod10._carries_real_money_field(record))

    def test_control_nontext_reporting_figure_matches_nothing(self):
        key = NamedKey("figure", "figure")
        self.assertFalse(mod10._money_key_matches(key, "amount"))

    def test_control_text_subclass_stored_amount_matches(self):
        key = LyingStr("amount", "cleanvalue")
        self.assertEqual(mod10._stored_text(key), "amount")
        self.assertTrue(mod10._money_key_matches(key, "amount"))


class TestR8023StatedCondition(unittest.TestCase):
    def test_defect_lone_surrogate_states_no_condition(self):
        for char in ("\ud800", "\udc00"):
            with self.subTest(code=hex(ord(char))):
                self.assertFalse(mod10._has_stated_condition([char]))

    def test_defect_unassigned_states_no_condition(self):
        for char in ("͸", "࢖"):
            with self.subTest(code=hex(ord(char))):
                self.assertFalse(mod10._has_stated_condition([char]))

    def test_defect_private_use_states_no_condition(self):
        for char in ("", "", "\U0010fffd"):
            with self.subTest(code=hex(ord(char))):
                self.assertFalse(mod10._has_stated_condition([char]))

    def test_defect_private_use_only_promotion_refused(self):
        record = {"run_id": "r9-b10-flag", "retention_tier": "Tier 2"}
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 3", actor="program",
                inputs={"flag_conditions_fired": [""]})

    def test_control_readable_entry_states_condition(self):
        self.assertTrue(mod10._has_stated_condition(["x"]))
        self.assertTrue(mod10._has_stated_condition(["condition-1"]))

    def test_control_cured_blank_entries_state_no_condition(self):
        for char in ("\u0000", "\u20dd", "\u2800"):
            with self.subTest(code=hex(ord(char))):
                self.assertFalse(mod10._has_stated_condition([char]))

    def test_control_empty_and_none_state_no_condition(self):
        self.assertFalse(mod10._has_stated_condition([]))
        self.assertFalse(mod10._has_stated_condition([None]))
        self.assertFalse(mod10._has_stated_condition([""]))

    def test_control_readable_promotion_stands(self):
        record = {"run_id": "r9-b10-flag-ok", "retention_tier": "Tier 2"}
        promoted = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 3", actor="program",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(promoted["retention_tier"], "Tier 3")


class TestR8025DaySortKey(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def test_defect_unparseable_unicode_digit_sort_key_no_raise(self):
        for char in ("\u2075", "\u00b2", "\u00b3", "\u2460"):
            with self.subTest(code=hex(ord(char))):
                key = mod10._day_sort_key((char, "viewer1"))
                self.assertEqual(key, (1, 0, char + ":" + "viewer1"))

    def test_defect_aggregate_acts_no_bare_value_error(self):
        delivery = {
            "simulated_day": "\u2075",
            "viewer_id": "viewer1",
            "joint_outcome_components": [1, 1, 1, 1],
            "component_denominators": [1, 1, 1, 1],
            "honest_share": 1,
            "epochs_ending_on_day": ["epoch-1"],
            "gate_passing_shares": {"epoch-1": 1},
        }
        mod10.retain_daily_aggregate_deliveries("r9-b10-agg", [delivery])
        records = mod10.daily_aggregates_for_run("r9-b10-agg")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["simulated_day"], "\u2075")
        manifest = mod10.aggregate_manifest_for_run("r9-b10-agg")
        self.assertEqual(len(manifest), 1)

    def test_control_plain_digit_text_sorts_as_day(self):
        self.assertEqual(mod10._day_sort_key(("5", "viewer1")), (0, 5, "viewer1"))

    def test_control_int_day_sorts_as_day(self):
        self.assertEqual(mod10._day_sort_key((5, "viewer1")), (0, 5, "viewer1"))

    def test_control_parseable_unicode_digit_sorts_as_day(self):
        self.assertEqual(mod10._day_sort_key(("\u0665", "viewer1")), (0, 5, "viewer1"))

    def test_control_nondigit_text_fallback(self):
        self.assertEqual(
            mod10._day_sort_key(("later", "viewer1")), (1, 0, "later:viewer1"))

    def test_control_plain_digit_day_aggregates(self):
        delivery = {
            "simulated_day": "5",
            "viewer_id": "viewer1",
            "joint_outcome_components": [1, 1, 1, 1],
            "component_denominators": [1, 1, 1, 1],
            "honest_share": 1,
            "epochs_ending_on_day": ["epoch-1"],
            "gate_passing_shares": {"epoch-1": 1},
        }
        mod10.retain_daily_aggregate_deliveries("r9-b10-agg-ok", [delivery])
        records = mod10.daily_aggregates_for_run("r9-b10-agg-ok")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["simulated_day"], "5")


if __name__ == "__main__":
    unittest.main()

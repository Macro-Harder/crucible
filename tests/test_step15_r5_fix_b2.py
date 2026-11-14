"""Step 15 rerun fix wave 4 pins for Builder 2, MOD-10.

Each test pins one register item from the Round 4 register
(R4-001, R4-022, R4-023, R4-027, and the MOD-10 limb of
R4-028) on the MOD-10 surface in crucible/mod10.py. Tests
reset the module stores around themselves so their standing
does not depend on suite order. Values are simulated and
test values only.
"""
import unittest

import crucible.mod10 as mod10


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def flag_record(self):
        return {
            "run_id": "run-r5-b2-flag",
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["c1"],
        }

    def promote(self, actor, fired=None):
        inputs = {"flag_conditions_fired": (
            fired if fired is not None else ["c1"])}
        return mod10.apply_flag_evaluation(
            self.flag_record(), outcome="promote", tier="Tier 2",
            actor=actor, inputs=inputs)

    def view_record(self, seen_day, view_day=1):
        return {
            "run_identifier": "run-r5-b2-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": view_day,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": {"clean_field": 1},
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"0": seen_day},
            "delay_applied_per_record": {"0": 0},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }


class TestR4001ActorDresses(B2Base):
    def assert_person_refused(self, actor):
        with self.assertRaises(ValueError):
            self.promote(actor)
        self.assertEqual(
            mod10._normalised_actor(actor), "person")


def _make_dress_test(actor):
    def test(self):
        self.assert_person_refused(actor)
    return test


_PERSON_DRESSES = [
    "personxxxx", "pirsin", "prsn", "per the the son",
    "person1234", "parsun", "pern", "pesn", "eprsun",
    "psreon", "the personxxxx", "a parsun", "per son xxxx",
    "per the the the son", "per-the-the-son",
]

for _index, _actor in enumerate(_PERSON_DRESSES):
    setattr(
        TestR4001ActorDresses,
        "test_person_dress_%02d" % _index,
        _make_dress_test(_actor))


class TestR4001Controls(B2Base):
    def test_plain_person_refused(self):
        with self.assertRaises(ValueError):
            self.promote("person")

    def test_the_person_refused(self):
        with self.assertRaises(ValueError):
            self.promote("the person")

    def test_per_the_son_refused(self):
        with self.assertRaises(ValueError):
            self.promote("per the son")

    def test_program_promotes_and_persists(self):
        result = self.promote("program")
        self.assertEqual(result["retention_tier"], "Tier 2")
        stored = mod10.summary_record_for_run("run-r5-b2-flag")
        self.assertEqual(stored.get("retention_tier"), "Tier 2")

    def test_alice_promotes(self):
        result = self.promote("alice")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_the_program_promotes(self):
        result = self.promote("the program")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_programxxxx_normalises_to_program(self):
        self.assertEqual(
            mod10._normalised_actor("programxxxx"), "program")
        result = self.promote("programxxxx")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_refused_dress_does_not_persist(self):
        with self.assertRaises(ValueError):
            self.promote("personxxxx")
        stored = mod10.summary_record_for_run("run-r5-b2-flag")
        self.assertNotEqual(stored.get("retention_tier"), "Tier 2")
        self.assertFalse(stored.get("record_found", True))


class LyingKindStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class TestR4022StoreKind(B2Base):
    def test_event_log_lying_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(
                {"run_identifier": "run-r5-b2-log"},
                store_kind=LyingKindStr("bogus-kind"))

    def test_event_log_plain_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(
                {"run_identifier": "run-r5-b2-log"},
                store_kind="bogus-kind")

    def test_event_log_plain_valid_kind_accepted(self):
        mod10.retain_event_log_entry(
            {"run_identifier": "run-r5-b2-log"}, store_kind="sweep")
        entries = mod10.event_log_entries(
            "run-r5-b2-log", store_kind="sweep")
        self.assertEqual(len(entries), 1)

    def test_event_log_lying_valid_kind_accepted(self):
        mod10.retain_event_log_entry(
            {"run_identifier": "run-r5-b2-log"},
            store_kind=LyingKindStr("sweep"))
        entries = mod10.event_log_entries(
            "run-r5-b2-log", store_kind="sweep")
        self.assertEqual(len(entries), 1)

    def test_snapshot_lying_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_daily_snapshot(
                {"run_identifier": "run-r5-b2-snap"},
                store_kind=LyingKindStr("bogus-kind"))

    def test_snapshot_plain_valid_kind_accepted(self):
        mod10.retain_daily_snapshot(
            {"run_identifier": "run-r5-b2-snap"}, store_kind="pilot")
        snapshots = mod10.daily_snapshots(
            "run-r5-b2-snap", store_kind="pilot")
        self.assertEqual(len(snapshots), 1)

    def test_checkpoint_lying_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(
                {"run_id": "run-r5-b2-ckpt", "simulated_day": 1},
                store_kind=LyingKindStr("bogus-kind"))

    def test_checkpoint_plain_valid_kind_accepted(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r5-b2-ckpt", "simulated_day": 1},
            store_kind="sweep")
        kept = mod10.checkpoints_for_run(
            "run-r5-b2-ckpt", store_kind="sweep")
        self.assertEqual(len(kept), 1)

    def test_store_lookup_lying_bogus_kind_refused(self):
        mod10.retain_run_record({"run_id": "run-r5-b2-lookup"})
        with self.assertRaises(ValueError):
            mod10.store_lookup(
                key="run-r5-b2-lookup",
                store_kind=LyingKindStr("bogus-kind"))

    def test_store_lookup_lying_bogus_kind_in_list_refused(self):
        mod10.retain_run_record({"run_id": "run-r5-b2-lookup"})
        with self.assertRaises(ValueError):
            mod10.store_lookup(
                store_kinds=[LyingKindStr("bogus-kind")],
                key="run-r5-b2-lookup")

    def test_store_lookup_plain_valid_kind_accepted(self):
        mod10.retain_run_record({"run_id": "run-r5-b2-lookup"})
        record = mod10.store_lookup(
            key="run-r5-b2-lookup", store_kind="sweep")
        self.assertEqual(record.get("run_id"), "run-r5-b2-lookup")

    def test_store_lookup_plain_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.store_lookup(
                key="run-r5-b2-lookup", store_kind="bogus-kind")


def _tuple_chain(length):
    value = "leaf"
    for _ in range(length):
        value = (value,)
    return value


def _list_chain(length):
    value = ["leaf"]
    for _ in range(length - 1):
        value = [value]
    return value


class TestR4023RunRecordRetention(B2Base):
    def key_record(self, length, run_id):
        return {"run_id": run_id, _tuple_chain(length): "payload"}

    def assert_key_chain_refused(self, length):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(
                self.key_record(length, "run-r5-b2-deep"))
        self.assertIn("deep or cyclic", str(caught.exception))

    def test_key_chain_101_refused(self):
        self.assert_key_chain_refused(101)

    def test_key_chain_102_refused(self):
        self.assert_key_chain_refused(102)

    def test_key_chain_150_refused(self):
        self.assert_key_chain_refused(150)

    def test_key_chain_100_retained_control(self):
        store = mod10.RecorderStore(store_kind="sweep")
        store.retain_run_record(
            self.key_record(100, "run-r5-b2-deep"))
        stored = store.read_run_record("run-r5-b2-deep")
        self.assertEqual(stored.get("run_id"), "run-r5-b2-deep")

    def test_list_chain_value_101_refused_control(self):
        store = mod10.RecorderStore(store_kind="sweep")
        record = {
            "run_id": "run-r5-b2-deep-list",
            "payload": _list_chain(101),
        }
        with self.assertRaises(ValueError) as caught:
            store.retain_run_record(record)
        self.assertIn("deep or cyclic", str(caught.exception))

    def test_money_read_walks_dict_keys(self):
        with self.assertRaises(ValueError) as caught:
            mod10._carries_real_money_field(
                {_tuple_chain(101): "payload"})
        self.assertIn("deep or cyclic", str(caught.exception))

    def test_money_read_key_chain_100_answers_control(self):
        self.assertFalse(
            mod10._carries_real_money_field(
                {_tuple_chain(100): "payload"}))

    def test_money_field_in_value_refused_control(self):
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r5-b2-money",
                 "payload": {"real_money": 5}})

    def test_plain_record_retained_control(self):
        store = mod10.RecorderStore(store_kind="sweep")
        store.retain_run_record(
            {"run_id": "run-r5-b2-plain", "payload": {"clean": 1}})
        stored = store.read_run_record("run-r5-b2-plain")
        self.assertEqual(stored["payload"], {"clean": 1})


class TestR4027TimingDayForms(B2Base):
    def assert_timing_refused(self, seen_day, view_day=1):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(
                self.view_record(seen_day, view_day))
        self.assertIn("timing", str(caught.exception))
        with self.assertRaises(ValueError):
            mod10.retain_view_record(
                self.view_record(seen_day, view_day))
        self.assertEqual(
            mod10.view_records_for_run("run-r5-b2-view"), [])

    def test_float_seen_day_after_int_view_day_refused(self):
        self.assert_timing_refused(5.0, 1)

    def test_fractional_seen_day_after_int_view_day_refused(self):
        self.assert_timing_refused(5.5, 1)

    def test_int_seen_day_after_float_view_day_refused(self):
        self.assert_timing_refused(5, 1.0)

    def test_decimal_string_seen_day_refused(self):
        self.assert_timing_refused("5.0", 1)

    def test_decimal_string_fraction_seen_day_refused(self):
        self.assert_timing_refused("5.5", 1)

    def test_int_seen_day_refused_control(self):
        self.assert_timing_refused(5, 1)

    def test_digit_string_seen_day_refused_control(self):
        self.assert_timing_refused("5", 1)

    def test_padded_digit_string_seen_day_refused_control(self):
        self.assert_timing_refused(" 5 ", 1)

    def test_signed_digit_string_seen_day_refused_control(self):
        self.assert_timing_refused("+5", 1)

    def test_zero_padded_digit_string_seen_day_refused_control(self):
        self.assert_timing_refused("05", 1)

    def test_float_seen_day_on_view_day_passes(self):
        result = mod10.run_view_leak_check(self.view_record(1.0, 1))
        self.assertTrue(result["reportable"])

    def test_decimal_string_seen_day_on_view_day_passes(self):
        result = mod10.run_view_leak_check(
            self.view_record("1.0", 1))
        self.assertTrue(result["reportable"])

    def test_int_seen_day_on_float_view_day_passes(self):
        result = mod10.run_view_leak_check(self.view_record(1, 1.0))
        self.assertTrue(result["reportable"])

    def test_float_seen_day_before_view_day_passes(self):
        result = mod10.run_view_leak_check(self.view_record(0.5, 1))
        self.assertTrue(result["reportable"])

    def test_clean_record_retained_control(self):
        mod10.retain_view_record(self.view_record(1, 1))
        kept = mod10.view_records_for_run("run-r5-b2-view")
        self.assertEqual(len(kept), 1)


class TestR4028InvisibleFormatCondition(B2Base):
    def assert_no_condition(self, fired):
        with self.assertRaises(ValueError):
            self.promote("program", fired=fired)


def _make_format_test(character):
    def test(self):
        self.assert_no_condition([character])
    return test


_FORMAT_CHARACTERS = [
    "\u00ad", "\u180e", "\u200e", "\u200f", "\u061c",
    "\u202a", "\u202e", "\u2061", "\u2064",
]

for _index, _character in enumerate(_FORMAT_CHARACTERS):
    setattr(
        TestR4028InvisibleFormatCondition,
        "test_format_character_%02d" % _index,
        _make_format_test(_character))


class TestR4028Controls(B2Base):
    def test_format_character_bare_string_form(self):
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                self.flag_record(), outcome="promote", tier="Tier 2",
                actor="program",
                inputs={"flag_conditions_fired": "\u202e"})

    def test_format_character_on_record_only(self):
        record = self.flag_record()
        record["flag_conditions_fired"] = ["\u2064"]
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2",
                actor="program", inputs={})

    def test_cured_zero_width_only_refused_control(self):
        with self.assertRaises(ValueError):
            self.promote("program", fired=["\u200b"])

    def test_readable_text_beside_format_character_promotes(self):
        result = self.promote(
            "program", fired=["\u202e" + "c1"])
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_stated_condition_beside_format_character_promotes(self):
        result = self.promote(
            "program", fired=["\u00ad", "c1"])
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_stated_condition_control_promotes(self):
        result = self.promote("program", fired=["c1"])
        self.assertEqual(result["retention_tier"], "Tier 2")


if __name__ == "__main__":
    unittest.main()

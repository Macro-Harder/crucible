"""Step 15 rerun fix wave 6 pins, Builder 2, MOD-10 surface.

Pins for rows R6-012, R6-020 (MOD-10 limb), R6-024, R6-027,
R6-032 (MOD-10 limb), R6-019 (MOD-10 limb), R6-010 (MOD-10
limb), and R6-038 (MOD-10 limb), each with lawful controls.
Values are simulated and test values only.
"""
import time
import unittest

import crucible.mod10 as mod10


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


def _chain(count, leaf=0):
    value = leaf
    for _ in range(count):
        value = [value]
    return value


def _wrap(value, count):
    for _ in range(count):
        value = [value]
    return value


class TestR6012MoneyCombinedPastCap(B2Base):
    def test_marker_red1_read(self):
        key = "r9999999999993almo9ne\u0443"
        self.assertTrue(mod10._carries_real_money_field({key: 5}))

    def test_marker_red1_retention_refused(self):
        key = "r9999999999993almo9ne\u0443"
        store = mod10.RecorderStore("sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "r6012-a", key: 5})

    def test_amount_red1_read(self):
        key = "9994m999999999ount"
        record = {key: 5, "currency": "usd"}
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_amount_red5_read(self):
        key = "4m0unt9" + "1" * 8
        record = {key: 5, "currency": "usd"}
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_amount_blue5_read(self):
        key = "am90unt" + "9" * 11
        record = {key: 5, "currency": "usd"}
        self.assertTrue(mod10._carries_real_money_field(record))

    def test_marker_blue5_read(self):
        key = "re94l9999m99o99n9e9y9"
        self.assertTrue(mod10._carries_real_money_field({key: 5}))

    def test_marker_blue5_retention_refused(self):
        key = "re94l9999m99o99n9e9y9"
        store = mod10.RecorderStore("sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "r6012-b", key: 5})

    def test_plain_marker_control(self):
        self.assertTrue(
            mod10._carries_real_money_field({"realmoney": 5}))

    def test_inside_cap_triple_control(self):
        key = "r99993almo9ne\u0443"
        self.assertTrue(mod10._carries_real_money_field({key: 5}))

    def test_clean_filler_control(self):
        key = "activity" + "1" * 13
        self.assertFalse(mod10._carries_real_money_field({key: 5}))


class TestR6010CountingBasis(B2Base):
    CORE = "\u0441a\u043dary"

    def test_eta_single_options(self):
        self.assertEqual(len(mod10._expanded_texts("\u03b7")), 1)

    def test_theta_single_options(self):
        self.assertEqual(len(mod10._expanded_texts("\u03b8")), 2)

    def test_eta_eleven_inside_bound(self):
        key = self.CORE + "\u03b7" * 11
        self.assertEqual(len(mod10._expanded_texts(key)), 4)

    def test_theta_eleven_past_bound(self):
        key = self.CORE + "\u03b8" * 11
        self.assertEqual(mod10._expanded_texts(key), set())

    def test_eta_ten_inside_bound(self):
        key = self.CORE + "\u03b7" * 10
        self.assertEqual(len(mod10._expanded_texts(key)), 4)

    def test_theta_ten_at_bound(self):
        key = self.CORE + "\u03b8" * 10
        self.assertEqual(len(mod10._expanded_texts(key)), 4096)

    def test_short_i_eleven_past_bound_control(self):
        key = self.CORE + "\u0439" * 11
        self.assertEqual(mod10._expanded_texts(key), set())

    def test_core_inside_bound_control(self):
        self.assertEqual(len(mod10._expanded_texts(self.CORE)), 4)


class TestR6038StatedCaps(B2Base):
    def test_expanded_texts_at_cap_passes(self):
        self.assertEqual(len(mod10._expanded_texts("\u0441" * 12)), 4096)

    def test_expanded_texts_past_cap_empty(self):
        self.assertEqual(mod10._expanded_texts("\u0441" * 13), set())

    def test_fold_variants_past_index_variant_absent(self):
        key = "re94l9999m99o99n9e9y9"
        self.assertNotIn("realmoney", mod10._fold_variants(key))

    def test_fold_variants_amount_past_index_absent(self):
        key = "am90unt" + "9" * 11
        self.assertNotIn("amount", mod10._fold_variants(key))

    def test_fold_variants_inside_cap_variant_present(self):
        key = "re94l999m99o99n9e9y"
        self.assertIn("realmoney", mod10._fold_variants(key))


class TestR6020GuardDepth(B2Base):
    def test_list_deep_first_order_refused(self):
        shared = _chain(50)
        deep = _wrap(shared, 60)
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape([deep, shared])

    def test_list_shared_first_order_refused_control(self):
        shared = _chain(50)
        deep = _wrap(shared, 60)
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape([shared, deep])

    def test_dict_b_first_order_refused(self):
        shared = _chain(60)
        wrapped = _wrap(shared, 50)
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape({"b": wrapped, "a": shared})

    def test_dict_a_first_order_refused_control(self):
        shared = _chain(60)
        wrapped = _wrap(shared, 50)
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape({"a": shared, "b": wrapped})

    def test_event_log_public_act_refused_b_order(self):
        shared = _chain(60)
        wrapped = _wrap(shared, 50)
        entry = {"run_id": "run-r6020", "b": wrapped, "a": shared}
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(entry)

    def test_plain_chain_102_refused_control(self):
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape(_chain(102))

    def test_plain_chain_101_passes_control(self):
        mod10._guard_retention_shape(_chain(101))

    def test_shared_dag_inside_bound_passes_control(self):
        value = ["clean"]
        for _ in range(24):
            value = [value, value]
        mod10._guard_retention_shape(value)


class TestR6019MoneyRewalk(B2Base):
    def test_shared_dag_cost(self):
        value = ["clean"]
        for _ in range(22):
            value = [value, value]
        started = time.monotonic()
        result = mod10._carries_real_money_field(value)
        elapsed = time.monotonic() - started
        self.assertFalse(result)
        self.assertLess(elapsed, 5.0)

    def test_shared_money_dag_found_control(self):
        value = {"amount": 5, "currency": "usd"}
        for _ in range(10):
            value = [value, value]
        self.assertTrue(mod10._carries_real_money_field(value))

    def test_deeper_reach_rejudged_control(self):
        shared = {"notes": "clean"}
        deep = _wrap(shared, 105)
        with self.assertRaises(ValueError):
            mod10._carries_real_money_field({"a": shared, "b": deep})

    def test_shared_subtree_result_stable_control(self):
        shared = {"amount": 5, "currency": "usd"}
        record = {"a": shared, "b": shared}
        self.assertTrue(mod10._carries_real_money_field(record))


class HashPilotKind(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__("pilot")


class HashBogusKind(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 1234567


class TestR6024StoreKindKeying(B2Base):
    def setUp(self):
        super().setUp()
        mod10.retain_run_record(
            {"run_id": "run-6024", "marker": "SWEEP-REC"}, "sweep")
        mod10.retain_run_record(
            {"run_id": "run-6024", "marker": "PILOT-REC"}, "pilot")

    def test_store_lookup_hash_pilot_returns_sweep(self):
        found = mod10.store_lookup(
            key="run-6024", store_kind=HashPilotKind("sweep"))
        self.assertEqual(found["marker"], "SWEEP-REC")

    def test_store_lookup_hash_bogus_returns_sweep(self):
        found = mod10.store_lookup(
            key="run-6024", store_kind=HashBogusKind("sweep"))
        self.assertEqual(found["marker"], "SWEEP-REC")

    def test_store_lookup_list_form_hash_pilot(self):
        found = mod10.store_lookup(
            store_kinds=[HashPilotKind("sweep")], key="run-6024")
        self.assertEqual(found["marker"], "SWEEP-REC")

    def test_event_log_canonical(self):
        mod10.retain_event_log_entry(
            {"run_id": "run-6024e", "v": 1}, HashPilotKind("sweep"))
        self.assertEqual(
            len(mod10.event_log_entries("run-6024e", "sweep")), 1)
        self.assertEqual(
            len(mod10.event_log_entries("run-6024e", "pilot")), 0)

    def test_daily_snapshot_canonical(self):
        mod10.retain_daily_snapshot(
            {"run_id": "run-6024d", "v": 1}, HashPilotKind("sweep"))
        self.assertEqual(
            len(mod10.daily_snapshots("run-6024d", "sweep")), 1)
        self.assertEqual(
            len(mod10.daily_snapshots("run-6024d", "pilot")), 0)

    def test_checkpoint_canonical(self):
        mod10.retain_checkpoint(
            {"run_id": "run-6024c", "simulated_day": 1},
            HashPilotKind("sweep"))
        self.assertEqual(
            len(mod10.checkpoints_for_run("run-6024c", "sweep")), 1)
        self.assertEqual(
            len(mod10.checkpoints_for_run("run-6024c", "pilot")), 0)

    def test_event_log_read_under_hash_kind(self):
        mod10.retain_event_log_entry({"run_id": "run-6024r", "v": 1})
        found = mod10.event_log_entries(
            "run-6024r", HashPilotKind("sweep"))
        self.assertEqual(len(found), 1)

    def test_plain_bogus_kind_refused_control(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(
                {"run_id": "run-6024x", "v": 1}, "bogus-kind")

    def test_lying_bogus_kind_refused_control(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(
                {"run_id": "run-6024x", "v": 1},
                HashPilotKind("bogus-kind"))

    def test_plain_sweep_lookup_control(self):
        found = mod10.store_lookup(key="run-6024", store_kind="sweep")
        self.assertEqual(found["marker"], "SWEEP-REC")


class TestR6027TimingRadix(B2Base):
    def view_record(self, seen_day, view_day=1):
        return {
            "run_identifier": "run-r6027-view",
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

    def test_timing_day_values(self):
        self.assertEqual(mod10._timing_day("0x5"), 5)
        self.assertEqual(mod10._timing_day("0X10"), 16)
        self.assertEqual(mod10._timing_day("0x1p4"), 16.0)
        self.assertEqual(mod10._timing_day("0b101"), 5)
        self.assertEqual(mod10._timing_day("0o17"), 15)

    def test_view_day_side_hex_refused(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record(5, "0x1"))

    def test_hex_seen_retention_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_view_record(self.view_record("0x5"))
        self.assertEqual(
            mod10.view_records_for_run("run-r6027-view"), [])

    def test_on_day_hex_passes_control(self):
        result = mod10.run_view_leak_check(self.view_record("0x1"))
        self.assertTrue(result["reportable"])

    def test_plain_future_day_refused_control(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record(5))

    def test_exponent_future_refused_control(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record("5e0"))

    def test_past_day_passes_control(self):
        result = mod10.run_view_leak_check(self.view_record(0))
        self.assertTrue(result["reportable"])


def _radix_seen_test(seen_day):
    def test(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record(seen_day))
    return test


_RADIX_SEEN_FORMS = ["0x5", "0X10", "0x1p4", "0b101", "0o17"]
for _i, _seen in enumerate(_RADIX_SEEN_FORMS):
    setattr(TestR6027TimingRadix, "test_radix_seen_%02d" % _i,
            _radix_seen_test(_seen))


class TestR6032BlankCondition(B2Base):
    def flag_record(self):
        return {
            "run_id": "run-r6032-flag",
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["c1"],
        }

    def promote(self, fired):
        return mod10.apply_flag_evaluation(
            self.flag_record(), outcome="promote", tier="Tier 2",
            actor="program",
            inputs={"flag_conditions_fired": fired})

    def test_readable_condition_promotes_control(self):
        updated = self.promote(["c1"])
        self.assertEqual(updated["retention_tier"], "Tier 2")

    def test_mark_beside_readable_promotes_control(self):
        updated = self.promote(["\u034f", "c1"])
        self.assertEqual(updated["retention_tier"], "Tier 2")

    def test_cf_only_refused_control(self):
        self.assertFalse(mod10._has_stated_condition(["\u200b"]))
        with self.assertRaises(ValueError):
            self.promote(["\u200b"])

    def test_bare_string_blank_glyph(self):
        self.assertFalse(mod10._has_stated_condition("\u2800"))


def _blank_condition_test(character):
    def test(self):
        self.assertFalse(mod10._has_stated_condition([character]))
        with self.assertRaises(ValueError):
            self.promote([character])
    return test


_BLANK_CODEPOINTS = [
    0x034F, 0x180B, 0x180C, 0x180D, 0xFE00, 0xFE0F, 0x2800, 0x115F,
]
for _i, _cp in enumerate(_BLANK_CODEPOINTS):
    setattr(TestR6032BlankCondition, "test_blank_%02d" % _i,
            _blank_condition_test(chr(_cp)))


if __name__ == "__main__":
    unittest.main()

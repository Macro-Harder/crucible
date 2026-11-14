"""Step 15 rerun fix wave 5 pins, MOD-10 surface.

Pins for rows R5-001, R5-005 (MOD-10 limb), R5-008 (MOD-10
limb), R5-013 (MOD-10 limb), R5-023 (MOD-10 limb), R5-024,
R5-025, and R5-033 (MOD-10 limb), with control pins for the
R5-009 money read controls. Values are simulated and test
values only.
"""
import types
import unittest
from decimal import Decimal

import crucible.mod10 as mod10


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def flag_record(self):
        return {
            "run_id": "run-r6-b2-flag",
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
            "run_identifier": "run-r6-b2-view",
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

    def assert_person_refused(self, actor):
        self.assertEqual(mod10._normalised_actor(actor), "person")
        with self.assertRaises(ValueError):
            self.promote(actor)


def _dress_test(actor):
    def test(self):
        self.assert_person_refused(actor)
    return test


class TestR5001ShellFormDresses(B2Base):
    pass


_R5001_DRESSES = [
    "personxxxxx", "person12345", "xyzson", "xexsxn",
    "prn", "pen", "psn", "pesrno", "eprqoz",
]
for _i, _a in enumerate(_R5001_DRESSES):
    setattr(TestR5001ShellFormDresses, "test_dress_%02d" % _i,
            _dress_test(_a))


class TestR5005PastBoundDresses(B2Base):
    pass


_R5005_DRESSES = [
    "personxxxxxx", "xyzzon", "xxxxon", "pn", "epsrno",
]
for _i, _a in enumerate(_R5005_DRESSES):
    setattr(TestR5005PastBoundDresses, "test_dress_%02d" % _i,
            _dress_test(_a))


class TestActorControls(B2Base):
    def test_plain_person_refused(self):
        self.assert_person_refused("person")

    def test_cured_dress_refused(self):
        self.assert_person_refused("personxxxx")

    def test_program_promotes(self):
        self.assertEqual(
            self.promote("program")["retention_tier"], "Tier 2")

    def test_alice_promotes(self):
        self.assertEqual(
            self.promote("alice")["retention_tier"], "Tier 2")

    def test_seven_added_letters_promotes_past_the_bound(self):
        self.assertEqual(
            self.promote("personxxxxxxx")["retention_tier"], "Tier 2")


class EvilSet(set):
    def __new__(cls, items=None):
        if isinstance(items, types.GeneratorType):
            return {"real_money": "materialised"}
        obj = super().__new__(cls)
        if items:
            obj.update(items)
        return obj


class EvilFrozenSet(frozenset):
    def __new__(cls, items=None):
        if isinstance(items, types.GeneratorType):
            return {"real_money": "materialised"}
        return super().__new__(cls, items or ())


class TestR5008SafeCopy(B2Base):
    def test_evil_set_copy_stays_a_set(self):
        copied = mod10._safe_copy(EvilSet(["a"]))
        self.assertIsInstance(copied, set)
        self.assertNotIsInstance(copied, dict)
        self.assertEqual(set(copied), {"a"})

    def test_evil_frozenset_copy_stays_a_frozenset(self):
        copied = mod10._safe_copy(EvilFrozenSet(["a"]))
        self.assertIsInstance(copied, frozenset)
        self.assertNotIsInstance(copied, dict)
        self.assertEqual(set(copied), {"a"})

    def test_evil_set_through_retain_and_read(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": "run-r6-b2-evil", "payload": EvilSet(["a"])})
        back = store.read_run_record("run-r6-b2-evil")
        self.assertNotIsInstance(back["payload"], dict)
        self.assertEqual(set(back["payload"]), {"a"})

    def test_plain_set_control(self):
        copied = mod10._safe_copy({"a", "b"})
        self.assertIsInstance(copied, set)
        self.assertEqual(copied, {"a", "b"})

    def test_plain_frozenset_control(self):
        copied = mod10._safe_copy(frozenset({"a"}))
        self.assertIsInstance(copied, frozenset)
        self.assertEqual(copied, frozenset({"a"}))

    def test_open_barred_dict_control_refused(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r6-b2-open",
                 "payload": {"real_money": "x"}})


_CORE = "membe\u0440\u0441\u043di\u0440"


class TestR5013CountingBasis(B2Base):
    def test_core_alone_barred_control(self):
        self.assertTrue(mod10._is_barred_view_key(_CORE))

    def test_plain_membership_barred_control(self):
        self.assertTrue(mod10._is_barred_view_key("membership"))

    def test_chi_filler_past_bound_like_the_sisters(self):
        self.assertFalse(
            mod10._is_barred_view_key(_CORE + "\u03c7" * 13))

    def test_short_i_filler_past_bound_control(self):
        self.assertFalse(
            mod10._is_barred_view_key(_CORE + "\u0439" * 13))

    def test_clean_key_with_filler_not_barred_control(self):
        self.assertFalse(
            mod10._is_barred_view_key("activity" + "\u0439" * 13))


class TestR5023SharedRewalk(B2Base):
    def shared(self, depth):
        value = ["x"]
        for _ in range(depth):
            value = [value, value]
        return value

    def test_shared_depth_20_guard_answers(self):
        import time
        start = time.time()
        mod10._guard_retention_shape(self.shared(20))
        self.assertLess(time.time() - start, 5.0)

    def test_shared_record_retained(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": "run-r6-b2-shared", "payload": self.shared(12)})
        back = store.read_run_record("run-r6-b2-shared")
        self.assertIn("payload", back)

    def test_cycle_control_refused(self):
        value = []
        value.append(value)
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape(value)

    def test_deep_chain_control_refused(self):
        value = "leaf"
        for _ in range(102):
            value = [value]
        with self.assertRaises(ValueError):
            mod10._guard_retention_shape(value)

    def test_plain_chain_control_answers(self):
        value = "leaf"
        for _ in range(50):
            value = [value]
        mod10._guard_retention_shape(value)


class LyingKind(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class CollidingKind(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return hash("sweep")


class TestR5024ModuleStoreKind(B2Base):
    def record(self):
        return {"run_id": "run-r6-b2-kind"}

    def test_plain_bogus_kind_retain_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record(self.record(), "bogus-kind")

    def test_plain_bogus_kind_read_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.read_run_record("run-r6-b2-kind", "bogus-kind")

    def test_lying_bogus_kind_retain_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record(self.record(), LyingKind("bogus-kind"))

    def test_lying_bogus_kind_read_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.read_run_record("run-r6-b2-kind", LyingKind("bogus-kind"))

    def test_colliding_kind_retain_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record(
                self.record(), CollidingKind("bogus-kind"))

    def test_colliding_kind_read_named_failure(self):
        with self.assertRaises(ValueError):
            mod10.read_run_record(
                "run-r6-b2-kind", CollidingKind("bogus-kind"))

    def test_plain_kind_control(self):
        mod10.retain_run_record(self.record(), "sweep")
        back = mod10.read_run_record("run-r6-b2-kind", "sweep")
        self.assertEqual(back["run_id"], "run-r6-b2-kind")

    def test_lying_kind_with_valid_stored_text_control(self):
        mod10.retain_run_record(self.record(), LyingKind("sweep"))
        back = mod10.read_run_record("run-r6-b2-kind", LyingKind("sweep"))
        self.assertEqual(back["run_id"], "run-r6-b2-kind")


class TestR5025TimingForms(B2Base):
    def assert_timing_refused(self, seen_day, view_day=1):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record(seen_day, view_day))

    def test_exponent_string_5e0(self):
        self.assert_timing_refused("5e0")

    def test_exponent_string_5E0(self):
        self.assert_timing_refused("5E0")

    def test_exponent_string_5e1(self):
        self.assert_timing_refused("5e1")

    def test_exponent_string_1e2(self):
        self.assert_timing_refused("1e2")

    def test_exponent_string_signed_1e2(self):
        self.assert_timing_refused("+1e2")

    def test_underscored_digit_string(self):
        self.assert_timing_refused("5_0")

    def test_inf_string(self):
        self.assert_timing_refused("inf")

    def test_decimal_seen_day(self):
        self.assert_timing_refused(Decimal("5.0"))

    def test_decimal_view_day(self):
        self.assert_timing_refused(5, Decimal("1.0"))

    def test_decimal_view_day_with_decimal_string_seen(self):
        self.assert_timing_refused("5.0", Decimal("1.0"))

    def test_nan_seen_day(self):
        self.assert_timing_refused(float("nan"))

    def test_nan_view_day(self):
        self.assert_timing_refused(5, float("nan"))

    def test_exponent_form_refused_at_retention(self):
        with self.assertRaises(ValueError):
            mod10.retain_view_record(self.view_record("5e0"))

    def test_on_day_exponent_control_passes(self):
        result = mod10.run_view_leak_check(self.view_record("1e0"))
        self.assertTrue(result["reportable"])

    def test_on_day_decimal_control_passes(self):
        result = mod10.run_view_leak_check(
            self.view_record(Decimal("1.0")))
        self.assertTrue(result["reportable"])

    def test_cured_decimal_string_control_refused(self):
        self.assert_timing_refused("5.0")

    def test_cured_float_control_refused(self):
        self.assert_timing_refused(5.0)

    def test_on_day_integer_control_passes(self):
        result = mod10.run_view_leak_check(self.view_record(1))
        self.assertTrue(result["reportable"])


_CF_CHARS = [
    "\u202b", "\u202c", "\u202d", "\u2062", "\u2063", "\u2066",
    "\u2067", "\u2068", "\u2069", "\u206a", "\u206f", "\u08e2",
    "\ufff9",
]


class TestR5033ConditionCharacters(B2Base):
    def test_cf_characters_state_no_condition(self):
        for char in _CF_CHARS:
            self.assertFalse(
                mod10._has_stated_condition([char]), repr(char))

    def test_cf_only_promotion_refused(self):
        for char in _CF_CHARS:
            with self.assertRaises(ValueError, msg=repr(char)):
                self.promote("program", fired=[char])

    def test_cured_zero_width_control(self):
        self.assertFalse(mod10._has_stated_condition(["\u200b"]))

    def test_cured_soft_hyphen_control(self):
        self.assertFalse(mod10._has_stated_condition(["\u00ad"]))

    def test_stated_condition_control(self):
        self.assertTrue(mod10._has_stated_condition(["c1"]))
        self.assertEqual(
            self.promote("program", fired=["c1"])["retention_tier"],
            "Tier 2")

    def test_readable_text_beside_cf_control(self):
        self.assertTrue(mod10._has_stated_condition(["c1\u202b"]))


class TestR5009MoneyControls(B2Base):
    def test_plain_pair_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"amount": 5, "currency": "usd"}))

    def test_leet_only_amount_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"4m0unt": 5, "currency": "usd"}))

    def test_drop_only_amount_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"amount9": 5, "currency": "usd"}))

    def test_leet_only_marker_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"r3almoney": 5}))

    def test_drop_only_marker_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"realmo9ney": 5}))

    def test_clean_record_control(self):
        self.assertFalse(mod10._carries_real_money_field(
            {"clean": 5}))


if __name__ == "__main__":
    unittest.main()

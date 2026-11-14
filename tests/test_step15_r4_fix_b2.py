"""Step 15 rerun fix wave 3 pins for Builder 2, MOD-10.

Each test pins one register item from the Round 3 register
(R3-003, R3-013, R3-030, R3-034, R3-043, R3-052, R3-057) on
the MOD-10 surface in crucible/mod10.py. Tests reset the
module stores around themselves so their standing does not
depend on suite order. Values are simulated and test values
only.
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
            "run_id": "run-r4-b2-flag",
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["c1"],
        }

    def promote(self, actor, fired=None):
        inputs = {"flag_conditions_fired": (
            fired if fired is not None else ["c1"])}
        return mod10.apply_flag_evaluation(
            self.flag_record(), outcome="promote", tier="Tier 2",
            actor=actor, inputs=inputs)

    def view_record(self, seen_day, view_day=1, contents=None):
        return {
            "run_identifier": "run-r4-b2-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": view_day,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": (
                contents if contents is not None
                else {"clean_field": 1}),
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"0": seen_day},
            "delay_applied_per_record": {"0": 0},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }

    def retain_two_kinds(self, run_id):
        mod10.retain_checkpoint(
            {"run_id": run_id, "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": run_id, "simulated_day": 1,
             "state_reference": "pilot-state"}, store_kind="pilot")


class TestR3003ActorNormalisation(B2Base):
    def assert_person_refused(self, actor):
        with self.assertRaises(ValueError):
            self.promote(actor)


def _make_person_test(actor):
    def test(self):
        self.assert_person_refused(actor)
    return test


_PERSON_DRESSES = [
    "the the person", "a a person", "the a person",
    "an the person", "persons", "persn", "persson",
    "p3rson", "pers0n", "peerson", "prson", "pesron",
    "personxxx", "per son", "p e r s o n", "pe rson",
    "per-son", "per_son", "per.son", "per/son",
    "the.person", "person.", ".person", "per the son",
    "p\u0435rson",
]

for _index, _actor in enumerate(_PERSON_DRESSES):
    setattr(
        TestR3003ActorNormalisation,
        "test_person_dress_%02d" % _index,
        _make_person_test(_actor))


class TestR3003Controls(B2Base):
    def test_plain_person_refused(self):
        with self.assertRaises(ValueError):
            self.promote("person")

    def test_the_person_refused(self):
        with self.assertRaises(ValueError):
            self.promote("the person")

    def test_program_promotes(self):
        result = self.promote("program")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_the_program_promotes(self):
        result = self.promote("the program")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_programs_promotes(self):
        result = self.promote("programs")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_leet_program_promotes(self):
        result = self.promote("pr0gram")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_split_program_promotes(self):
        result = self.promote("prog ram")
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_refused_dress_does_not_persist(self):
        with self.assertRaises(ValueError):
            self.promote("the the person")
        stored = mod10.summary_record_for_run("run-r4-b2-flag")
        self.assertNotEqual(stored.get("retention_tier"), "Tier 2")
        self.assertFalse(stored.get("record_found", True))


class TestR3013ShortI(B2Base):
    def test_membership_with_short_i_at_i_position_barred(self):
        self.assertTrue(
            mod10._is_barred_view_key("membersh\u0439p"))

    def test_is_honest_with_short_i_at_i_position_barred(self):
        self.assertTrue(
            mod10._is_barred_view_key("\u0439s_honest"))

    def test_composite_with_short_i_barred(self):
        self.assertTrue(
            mod10._is_barred_view_key("m3mbersh\u0439-p"))

    def test_leak_check_refuses_short_i_key(self):
        record = self.view_record(
            1, contents={"membersh\u0439p": 1})
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_short_i_y_reading_still_stands(self):
        self.assertTrue(
            mod10._is_barred_view_key("canar\u0439"))

    def test_clean_key_admitted(self):
        self.assertFalse(
            mod10._is_barred_view_key("clean_field"))


class LyingKindStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class TestR3030StoreKind(B2Base):
    def test_lying_kind_outside_closed_set_refused(self):
        with self.assertRaises(ValueError):
            mod10.RecorderStore(store_kind=LyingKindStr("bogus-kind"))

    def test_plain_bogus_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.RecorderStore(store_kind="bogus-kind")

    def test_plain_valid_kind_accepted(self):
        store = mod10.RecorderStore(store_kind="sweep")
        self.assertEqual(store.store_kind, "sweep")

    def test_lying_kind_with_valid_stored_value_accepted(self):
        store = mod10.RecorderStore(store_kind=LyingKindStr("sweep"))
        self.assertTrue(str.__eq__(store.store_kind, "sweep"))


class TestR3034ResumeEmptyKind(B2Base):
    def test_tampered_copy_named_empty_kind_by_call_refused(self):
        self.retain_two_kinds("run-r3034a")
        tampered = mod10.checkpoints_for_run(
            "run-r3034a", store_kind="sweep")[0]
        tampered["state_reference"] = "altered"
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(tampered, store_kind="live")
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_tampered_copy_named_empty_kind_on_checkpoint_refused(self):
        self.retain_two_kinds("run-r3034b")
        tampered = mod10.checkpoints_for_run(
            "run-r3034b", store_kind="sweep")[0]
        tampered["state_reference"] = "altered"
        tampered["store_kind"] = "live"
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(tampered)
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_exact_copy_named_empty_kind_refused(self):
        self.retain_two_kinds("run-r3034c")
        pilot_copy = mod10.checkpoints_for_run(
            "run-r3034c", store_kind="pilot")[0]
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(pilot_copy, store_kind="live")
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_enumerated_copy_resumes_control(self):
        self.retain_two_kinds("run-r3034d")
        pilot_copy = mod10.checkpoints_for_run(
            "run-r3034d", store_kind="pilot")[0]
        resumed = mod10.resume_from_checkpoint(pilot_copy)
        self.assertEqual(resumed["state_reference"], "pilot-state")

    def test_tampered_copy_no_kind_refused_control(self):
        self.retain_two_kinds("run-r3034e")
        tampered = mod10.checkpoints_for_run(
            "run-r3034e", store_kind="sweep")[0]
        tampered["state_reference"] = "altered"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(tampered)


class TestR3043TimingDayForm(B2Base):
    def test_string_seen_day_after_int_view_day_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(self.view_record("5", 1))
        self.assertIn("timing", str(caught.exception))

    def test_string_seen_day_after_string_view_day_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(self.view_record("5", "1"))
        self.assertIn("timing", str(caught.exception))

    def test_int_seen_day_after_view_day_refused_control(self):
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(self.view_record(5, 1))

    def test_string_seen_day_on_view_day_passes(self):
        result = mod10.run_view_leak_check(self.view_record("1", 1))
        self.assertTrue(result["reportable"])

    def test_int_seen_day_on_string_view_day_passes(self):
        result = mod10.run_view_leak_check(self.view_record(1, "1"))
        self.assertTrue(result["reportable"])


class TestR3052ZeroWidthCondition(B2Base):
    def assert_no_condition(self, fired):
        with self.assertRaises(ValueError):
            self.promote("program", fired=fired)

    def test_zero_width_space_only(self):
        self.assert_no_condition(["\u200b"])

    def test_zero_width_joiner_only(self):
        self.assert_no_condition(["\u200d"])

    def test_byte_order_mark_only(self):
        self.assert_no_condition(["\ufeff"])

    def test_zero_width_mix_only(self):
        self.assert_no_condition(["\u200b\u200d\ufeff"])

    def test_zero_width_bare_string_form(self):
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                self.flag_record(), outcome="promote", tier="Tier 2",
                actor="program",
                inputs={"flag_conditions_fired": "\u200b"})

    def test_zero_width_on_record_only(self):
        record = self.flag_record()
        record["flag_conditions_fired"] = ["\u200b"]
        with self.assertRaises(ValueError):
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2",
                actor="program", inputs={})

    def test_stated_condition_beside_zero_width_promotes(self):
        result = self.promote("program", fired=["\u200b", "c1"])
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_stated_condition_control_promotes(self):
        result = self.promote("program", fired=["c1"])
        self.assertEqual(result["retention_tier"], "Tier 2")


class TestR3057ResumeDayForm(B2Base):
    def test_exact_copy_with_string_day_resumes(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r3057a", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        copy = mod10.checkpoints_for_run(
            "run-r3057a", store_kind="sweep")[0]
        copy["simulated_day"] = "1"
        resumed = mod10.resume_from_checkpoint(copy)
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_exact_copy_with_int_day_resumes_control(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r3057b", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        copy = mod10.checkpoints_for_run(
            "run-r3057b", store_kind="sweep")[0]
        resumed = mod10.resume_from_checkpoint(copy)
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_string_day_retained_copy_resumes_control(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r3057c", "simulated_day": "1",
             "state_reference": "sweep-state"}, store_kind="sweep")
        copy = mod10.checkpoints_for_run(
            "run-r3057c", store_kind="sweep")[0]
        resumed = mod10.resume_from_checkpoint(copy)
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_tampered_copy_with_string_day_still_refused(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r3057d", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        copy = mod10.checkpoints_for_run(
            "run-r3057d", store_kind="sweep")[0]
        copy["simulated_day"] = "1"
        copy["state_reference"] = "altered"
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(copy)
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))


if __name__ == "__main__":
    unittest.main()

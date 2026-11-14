"""Step 15, second run, fix wave 7 pins for Builder 8.

Each test pins one register item from the Round 7 register
(R7-016 and R7-027) on the MOD-10 surface in crucible/mod10.py.
Tests reset the module stores around themselves so their standing
does not depend on suite order. Values are simulated and test
values only.
"""
import unittest

import crucible.mod10 as mod10


class LyingKindStr(str):
    """A store kind whose own equality reading answers True
    against every kind, whatever text it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class CollidingHashKindStr(str):
    """A store kind whose hash answers as the pilot kind, whatever
    text it stores."""

    def __hash__(self):
        return hash("pilot")


class B8Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def retain_two_kinds(self, run_id):
        mod10.retain_checkpoint(
            {"run_id": run_id, "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": run_id, "simulated_day": 1,
             "state_reference": "pilot-state"}, store_kind="pilot")

    def copies(self, run_id):
        sweep_copy = mod10.checkpoints_for_run(
            run_id, store_kind="sweep")[0]
        pilot_copy = mod10.checkpoints_for_run(
            run_id, store_kind="pilot")[0]
        return sweep_copy, pilot_copy

    def view_record(self, seen_day, view_day=1):
        return {
            "run_identifier": "run-r8-b8-view",
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


class TestR7016ResumeLyingKind(B8Base):
    def assert_integrity_refusal(self, handed, kind_marker, kind):
        with self.assertRaises(ValueError) as caught:
            if kind_marker == "call":
                mod10.resume_from_checkpoint(handed, store_kind=kind)
            else:
                handed = dict(handed)
                handed["store_kind"] = kind
                mod10.resume_from_checkpoint(handed)
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_pilot_copy_under_lying_sweep_kind_by_call_refused(self):
        self.retain_two_kinds("run-r7016a")
        _, pilot_copy = self.copies("run-r7016a")
        self.assert_integrity_refusal(
            pilot_copy, "call", LyingKindStr("sweep"))

    def test_pilot_copy_under_lying_sweep_kind_on_checkpoint_refused(self):
        self.retain_two_kinds("run-r7016b")
        _, pilot_copy = self.copies("run-r7016b")
        self.assert_integrity_refusal(
            pilot_copy, "field", LyingKindStr("sweep"))

    def test_pilot_copy_under_lying_bogus_kind_by_call_refused(self):
        self.retain_two_kinds("run-r7016c")
        _, pilot_copy = self.copies("run-r7016c")
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(
                pilot_copy, store_kind=LyingKindStr("bogus"))
        self.assertIn("unknown store kind", str(caught.exception))

    def test_sweep_copy_under_lying_pilot_kind_by_call_refused(self):
        self.retain_two_kinds("run-r7016d")
        sweep_copy, _ = self.copies("run-r7016d")
        self.assert_integrity_refusal(
            sweep_copy, "call", LyingKindStr("pilot"))

    def test_sweep_copy_under_lying_live_kind_by_call_refused(self):
        self.retain_two_kinds("run-r7016e")
        sweep_copy, _ = self.copies("run-r7016e")
        self.assert_integrity_refusal(
            sweep_copy, "call", LyingKindStr("live"))

    def test_sweep_copy_under_lying_live_kind_on_checkpoint_refused(self):
        self.retain_two_kinds("run-r7016f")
        sweep_copy, _ = self.copies("run-r7016f")
        self.assert_integrity_refusal(
            sweep_copy, "field", LyingKindStr("live"))

    def test_tampered_sweep_copy_under_lying_sweep_kind_by_call(self):
        self.retain_two_kinds("run-r7016g")
        sweep_copy, _ = self.copies("run-r7016g")
        tampered = dict(sweep_copy)
        tampered["state_reference"] = "pilot-state"
        self.assert_integrity_refusal(
            tampered, "call", LyingKindStr("sweep"))

    def test_tampered_sweep_copy_under_lying_sweep_kind_on_checkpoint(self):
        self.retain_two_kinds("run-r7016h")
        sweep_copy, _ = self.copies("run-r7016h")
        tampered = dict(sweep_copy)
        tampered["state_reference"] = "pilot-state"
        self.assert_integrity_refusal(
            tampered, "field", LyingKindStr("sweep"))

    def test_unretained_checkpoint_under_lying_bogus_kind_refused(self):
        handed = {"run_id": "run-r7016i", "simulated_day": 1,
                  "state_reference": "sweep-state"}
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(
                handed, store_kind=LyingKindStr("bogus"))
        self.assertIn("unknown store kind", str(caught.exception))


class TestR7016Controls(B8Base):
    def test_pilot_copy_under_plain_pilot_kind_resumes(self):
        self.retain_two_kinds("run-r7016j")
        _, pilot_copy = self.copies("run-r7016j")
        resumed = mod10.resume_from_checkpoint(
            pilot_copy, store_kind="pilot")
        self.assertEqual(resumed["state_reference"], "pilot-state")

    def test_sweep_copy_under_plain_sweep_kind_resumes(self):
        self.retain_two_kinds("run-r7016k")
        sweep_copy, _ = self.copies("run-r7016k")
        resumed = mod10.resume_from_checkpoint(
            sweep_copy, store_kind="sweep")
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_pilot_copy_under_plain_sweep_kind_refused(self):
        self.retain_two_kinds("run-r7016l")
        _, pilot_copy = self.copies("run-r7016l")
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(pilot_copy, store_kind="sweep")
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_sweep_copy_under_lying_kind_storing_sweep_resumes(self):
        self.retain_two_kinds("run-r7016m")
        sweep_copy, _ = self.copies("run-r7016m")
        resumed = mod10.resume_from_checkpoint(
            sweep_copy, store_kind=LyingKindStr("sweep"))
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_pilot_copy_under_lying_kind_storing_pilot_resumes(self):
        self.retain_two_kinds("run-r7016n")
        _, pilot_copy = self.copies("run-r7016n")
        resumed = mod10.resume_from_checkpoint(
            pilot_copy, store_kind=LyingKindStr("pilot"))
        self.assertEqual(resumed["state_reference"], "pilot-state")

    def test_sweep_copy_under_colliding_hash_kind_storing_sweep(self):
        self.retain_two_kinds("run-r7016o")
        sweep_copy, _ = self.copies("run-r7016o")
        resumed = mod10.resume_from_checkpoint(
            sweep_copy, store_kind=CollidingHashKindStr("sweep"))
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_pilot_copy_under_colliding_hash_kind_storing_sweep(self):
        self.retain_two_kinds("run-r7016p")
        _, pilot_copy = self.copies("run-r7016p")
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(
                pilot_copy, store_kind=CollidingHashKindStr("sweep"))
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))

    def test_plain_bogus_kind_refused_unknown(self):
        self.retain_two_kinds("run-r7016q")
        sweep_copy, _ = self.copies("run-r7016q")
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(sweep_copy, store_kind="bogus")
        self.assertIn("unknown store kind", str(caught.exception))


_DIGIT_FORMS = ["\u2075", "\u00b2", "\u00b3", "\u2460"]


class TestR7027WholeDay(B8Base):
    def test_mixed_plain_and_superscript_day_stands_as_itself(self):
        self.assertEqual(mod10._whole_day("5\u2075"), "5\u2075")

    def test_signed_superscript_day_stands_as_itself(self):
        self.assertEqual(mod10._whole_day("+\u2075"), "+\u2075")

    def test_padded_superscript_day_stands_as_itself(self):
        self.assertEqual(mod10._whole_day(" \u2075 "), " \u2075 ")

    def test_dotted_superscript_day_stands_as_itself_whole(self):
        self.assertEqual(mod10._whole_day("\u00b2.5"), "\u00b2.5")


def _make_whole_day_test(form):
    def test(self):
        result = mod10._whole_day(form)
        self.assertEqual(result, form)
        self.assertIsInstance(result, str)
    return test


def _make_timing_day_test(form):
    def test(self):
        result = mod10._timing_day(form)
        self.assertEqual(result, form)
        self.assertIsInstance(result, str)
    return test


for _index, _form in enumerate(_DIGIT_FORMS):
    setattr(TestR7027WholeDay,
            "test_whole_day_digit_%d_stands_as_itself" % _index,
            _make_whole_day_test(_form))
    setattr(TestR7027WholeDay,
            "test_timing_day_digit_%d_stands_as_itself" % _index,
            _make_timing_day_test(_form))


class TestR7027TimingDayComposite(B8Base):
    def test_dotted_superscript_day_stands_as_itself_timing(self):
        self.assertEqual(mod10._timing_day("\u00b2.5"), "\u00b2.5")


class TestR7027ViewSeam(B8Base):
    def test_first_seen_superscript_five_passes_leak_check(self):
        result = mod10.run_view_leak_check(
            self.view_record("\u2075", view_day=1))
        self.assertTrue(result["reportable"])

    def test_first_seen_circled_one_passes_leak_check(self):
        result = mod10.run_view_leak_check(
            self.view_record("\u2460", view_day=1))
        self.assertTrue(result["reportable"])

    def test_view_day_superscript_five_passes_leak_check(self):
        result = mod10.run_view_leak_check(
            self.view_record(1, view_day="\u2075"))
        self.assertTrue(result["reportable"])

    def test_first_seen_superscript_five_stands_retained(self):
        stored = mod10.retain_view_record(
            self.view_record("\u2075", view_day=1))
        self.assertEqual(stored["run_identifier"], "run-r8-b8-view")
        retained = mod10.view_records_for_run("run-r8-b8-view")
        self.assertEqual(len(retained), 1)

    def test_view_day_superscript_two_stands_retained(self):
        mod10.retain_view_record(self.view_record(1, view_day="\u00b2"))
        retained = mod10.view_records_for_run("run-r8-b8-view")
        self.assertEqual(len(retained), 1)


class TestR7027CheckpointActs(B8Base):
    def test_checkpoint_state_at_superscript_three_returns_none(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027a", "simulated_day": 1,
             "state_reference": "sweep-state",
             "checkpoint_state": {"marker": "stated"}},
            store_kind="sweep")
        self.assertIsNone(
            mod10.checkpoint_state_at("run-r7027a", "\u00b3"))

    def test_second_retain_with_superscript_three_day_stands(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027b", "simulated_day": 1,
             "state_reference": "first"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": "run-r7027b", "simulated_day": "\u00b3",
             "state_reference": "second"}, store_kind="sweep")
        copies = mod10.checkpoints_for_run(
            "run-r7027b", store_kind="sweep")
        self.assertEqual(len(copies), 2)

    def test_retain_with_superscript_day_and_state_stands(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027c", "simulated_day": "\u00b3",
             "state_reference": "stated",
             "checkpoint_state": {"marker": "stated"}},
            store_kind="sweep")
        state = mod10.checkpoint_state_at("run-r7027c", "\u00b3")
        self.assertEqual(state, {"marker": "stated"})

    def test_resume_named_kind_superscript_day_integrity_form(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027d", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        handed = mod10.checkpoints_for_run(
            "run-r7027d", store_kind="sweep")[0]
        handed["simulated_day"] = "\u00b3"
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(handed, store_kind="sweep")
        self.assertIn("checkpoint integrity refusal",
                      str(caught.exception))
        self.assertNotIn("invalid literal", str(caught.exception))

    def test_delete_checkpoint_superscript_day_removes_none(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027e", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        act = mod10.delete_checkpoint(
            "run-r7027e", "\u00b3",
            trigger="clause C5 stated trigger",
            rule_path="stated deletion rule path")
        self.assertEqual(act["removed"], 0)
        self.assertEqual(
            len(mod10.checkpoints_for_run("run-r7027e")), 1)

    def test_close_retention_with_superscript_day_checkpoint(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r7027f", "simulated_day": "\u2075",
             "state_reference": "stated"}, store_kind="sweep")
        result = mod10.close_run_retention("run-r7027f", "Tier 3")
        self.assertEqual(result["kept_days"], [])
        self.assertEqual(result["released_days"], [])


class TestR7027Controls(B8Base):
    def test_arabic_indic_five_reads_as_five_whole(self):
        self.assertEqual(mod10._whole_day("\u0665"), 5)

    def test_arabic_indic_five_reads_as_five_timing(self):
        self.assertEqual(mod10._timing_day("\u0665"), 5)

    def test_arabic_indic_five_first_seen_refused_named_timing(self):
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(
                self.view_record("\u0665", view_day=1))
        self.assertIn("view leak check failure", str(caught.exception))
        self.assertIn("timing", str(caught.exception))
        self.assertNotIn("invalid literal", str(caught.exception))

    def test_fullwidth_five_reads_as_five_whole(self):
        self.assertEqual(mod10._whole_day("\uff15"), 5)

    def test_plain_digit_string_days_read_as_integers(self):
        self.assertEqual(mod10._whole_day("5"), 5)
        self.assertEqual(mod10._whole_day("+5"), 5)
        self.assertEqual(mod10._whole_day(5), 5)

    def test_malformed_prefix_0x_stands_as_itself(self):
        self.assertEqual(mod10._timing_day("0x"), "0x")

    def test_malformed_prefix_0xg_stands_as_itself(self):
        self.assertEqual(mod10._timing_day("0xg"), "0xg")

    def test_malformed_prefix_0b102_stands_as_itself(self):
        self.assertEqual(mod10._timing_day("0b102"), "0b102")

    def test_hex_spelling_still_reads_as_its_day(self):
        self.assertEqual(mod10._timing_day("0x5"), 5)


if __name__ == "__main__":
    unittest.main()

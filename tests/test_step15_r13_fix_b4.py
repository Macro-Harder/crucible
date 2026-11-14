"""Pin tests for fix wave 12, Builder 4, MOD-10 rows R12-018 to
R12-024 of the Round 12 register.

Each defect method states the exact proving act of its source
paper: Red 5 Findings 3 to 6 for rows R12-018 to R12-021, Blue 5
Finding 2 and Purple 5 Finding P5-4 for row R12-022, and Yellow 5
Findings 1 and 2 for rows R12-023 and R12-024, beside plain
controls that must keep their standing both ways.
"""

import unittest

from crucible import mod04
from crucible import mod10


class LyingLowerStr(str):
    def lower(self):
        return "clause c5 deletion rule"


class LyingStripStr(str):
    def strip(self, *args):
        return "999"


class LyingGetDict(dict):
    def __init__(self, stored, reported=None):
        super().__init__(stored)
        self._reported = reported or {}

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return super().get(key, default)


def manifest(run="run-b4", day=5, state=None, **extra):
    base = {"run_identifier": run, "run_id": run, "simulated_day": day}
    if state is not None:
        base["checkpoint_state"] = state
    base.update(extra)
    return base


def view_record(run="run-v"):
    return mod04.build_view_record(
        run_id=run, viewer_id="viewer-1", day=5,
        contents=[{"note": "clean", "first_seen_day": 1, "delay": 0}],
        position="pos-1", rule_version_set="rv-1")


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR12018DeletionGateLower(Base):
    def test_lying_lower_trigger_and_rule_path_refused(self):
        mod10.retain_checkpoint(manifest(
            run="del-run", day=3, state={"k": "v"}))
        with self.assertRaises(ValueError) as caught:
            mod10.delete_checkpoint(
                "del-run", 3,
                trigger=LyingLowerStr("total nonsense"),
                rule_path=LyingLowerStr("more nonsense"))
        self.assertIn("no clause C5 trigger", str(caught.exception))
        self.assertEqual(len(mod10.checkpoints_for_run("del-run")), 1)
        self.assertEqual(
            mod10.checkpoint_state_at("del-run", 3), {"k": "v"})

    def test_lying_lower_rule_path_alone_refused(self):
        mod10.retain_checkpoint(manifest(
            run="del-run", day=3, state={"k": "v"}))
        with self.assertRaises(ValueError) as caught:
            mod10.delete_checkpoint(
                "del-run", 3,
                trigger="clause C5 trigger",
                rule_path=LyingLowerStr("more nonsense"))
        self.assertIn("no deletion rule path", str(caught.exception))
        self.assertEqual(len(mod10.checkpoints_for_run("del-run")), 1)
        self.assertEqual(
            mod10.checkpoint_state_at("del-run", 3), {"k": "v"})

    def test_controls_honest_forms(self):
        mod10.retain_checkpoint(manifest(
            run="del-run", day=3, state={"k": "v"}))
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(
                "del-run", 3, trigger="total nonsense",
                rule_path="more nonsense")
        self.assertEqual(len(mod10.checkpoints_for_run("del-run")), 1)
        with self.assertRaises(ValueError):
            mod10.delete_checkpoint(
                "del-run", 3, trigger="clause C5 trigger",
                rule_path="deletion rule path",
                integrity_flag_open=True)
        self.assertEqual(len(mod10.checkpoints_for_run("del-run")), 1)
        act = mod10.delete_checkpoint(
            "del-run", 3, trigger="clause C5 trigger",
            rule_path="deletion rule path")
        self.assertEqual(act["removed"], 1)
        self.assertEqual(mod10.checkpoints_for_run("del-run"), [])
        self.assertIsNone(mod10.checkpoint_state_at("del-run", 3))


class TestR12019RestoreAndReplayGet(Base):
    def test_restore_check_lying_get_refused(self):
        portable = LyingGetDict(
            {"relative_identifier": "checkpoints/real-absent"},
            reported={"relative_identifier": "checkpoints/99:int:1"})
        self.assertFalse(
            mod10.restore_check(portable, {"checkpoints/99:int:1"}))

    def test_replay_check_lying_gets_refused(self):
        shared = {"record": {"same": 1}, "verdict": "same"}
        original = LyingGetDict(
            {"record": {"a": 1}, "verdict": "x"}, reported=shared)
        resumed = LyingGetDict(
            {"record": {"a": 2}, "verdict": "y"}, reported=shared)
        result = mod10.replay_check(original, resumed)
        self.assertFalse(result["record_level_equal"])
        self.assertFalse(result["verdict_level_equal"])

    def test_controls_honest_dicts(self):
        self.assertTrue(mod10.restore_check(
            {"relative_identifier": "checkpoints/present"},
            {"checkpoints/present"}))
        self.assertFalse(mod10.restore_check(
            {"relative_identifier": "checkpoints/absent"},
            {"checkpoints/present"}))
        same = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 1}, "verdict": "x"})
        self.assertTrue(same["record_level_equal"])
        self.assertTrue(same["verdict_level_equal"])
        differing = mod10.replay_check(
            {"record": {"a": 1}, "verdict": "x"},
            {"record": {"a": 2}, "verdict": "y"})
        self.assertFalse(differing["record_level_equal"])
        self.assertFalse(differing["verdict_level_equal"])


class TestR12020TimingDayStrip(Base):
    def test_helper_readings_judge_stored_text(self):
        dressed = LyingStripStr("5")
        self.assertEqual(mod10._whole_day(dressed), 5)
        self.assertEqual(mod10._timing_day(dressed), 5)
        self.assertEqual(mod10._day_match_form(dressed), ("int", 5))

    def test_public_timing_gate_judges_stored_day(self):
        record = view_record()
        record["simulated_day"] = LyingStripStr("5")
        record["first_seen_day_per_record"] = {"0": 10}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("timing", str(caught.exception))
        self.assertIn("first seen after the view day",
                      str(caught.exception))

    def test_controls_honest_text_day(self):
        self.assertEqual(mod10._whole_day("5"), 5)
        self.assertEqual(mod10._whole_day(" 5 "), 5)
        self.assertEqual(mod10._timing_day("5"), 5)
        record = view_record()
        record["simulated_day"] = "5"
        record["first_seen_day_per_record"] = {"0": 10}
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)


SUPERSCRIPT_FIVE = "⁵"
CIRCLED_FIVE = "⑤"
SUPERSCRIPT_TWO = "²"


class TestR12021CloseNondecimalDigitText(Base):
    def _assert_preserved(self, form, index):
        run = "close-run-" + str(index)
        mod10.retain_checkpoint(manifest(
            run=run, day=form, state={"k": "v"}))
        result = mod10.close_run_retention(run, "Tier 0")
        self.assertNotIn(form, result["released_days"])
        self.assertNotIn(form, result["kept_days"])
        self.assertEqual(len(mod10.checkpoints_for_run(run)), 1)
        self.assertEqual(mod10.checkpoint_state_at(run, form), {"k": "v"})

    def test_second_sign_and_trailing_sign_forms_preserved(self):
        forms = [
            "++" + SUPERSCRIPT_FIVE,
            "--" + SUPERSCRIPT_FIVE,
            "+-" + SUPERSCRIPT_FIVE,
            SUPERSCRIPT_FIVE + "+",
            SUPERSCRIPT_FIVE + "-",
        ]
        for index, form in enumerate(forms):
            with self.subTest(form=form):
                self._assert_preserved(form, index)

    def test_space_after_sign_and_multi_digit_forms_preserved(self):
        forms = [
            "+ " + SUPERSCRIPT_FIVE,
            "+ " + SUPERSCRIPT_FIVE,
            "++" + SUPERSCRIPT_FIVE + SUPERSCRIPT_FIVE,
            "++" + CIRCLED_FIVE,
            "++" + SUPERSCRIPT_TWO,
        ]
        for index, form in enumerate(forms):
            with self.subTest(form=form):
                self._assert_preserved(form, 100 + index)

    def test_controls_already_preserved_and_integer_released(self):
        forms = [
            SUPERSCRIPT_FIVE,
            "+" + SUPERSCRIPT_FIVE,
            "-" + SUPERSCRIPT_FIVE,
            " " + SUPERSCRIPT_FIVE + " ",
            SUPERSCRIPT_FIVE + SUPERSCRIPT_FIVE,
            CIRCLED_FIVE,
            "+" + CIRCLED_FIVE,
        ]
        for index, form in enumerate(forms):
            with self.subTest(form=form):
                self._assert_preserved(form, 200 + index)
        mod10.retain_checkpoint(manifest(
            run="close-int", day=1, state={"k": "v"}))
        result = mod10.close_run_retention("close-int", "Tier 0")
        self.assertEqual(result["released_days"], [1])
        self.assertEqual(mod10.checkpoints_for_run("close-int"), [])
        self.assertIsNone(mod10.checkpoint_state_at("close-int", 1))


class TestR12022GateEpochKey(Base):
    def _assert_two_slots(self, first, second, tag):
        for order in (0, 1):
            run = "epoch-" + tag + "-" + str(order)
            pair = [(first, "first"), (second, "second")]
            if order:
                pair.reverse()
            for epoch, share in pair:
                mod10.record_gate_passing_share(run, epoch, share)
            got = mod10.gate_passing_shares_for_run(run)
            self.assertEqual(len(got), 2)
            self.assertEqual(
                sorted(item["share"] for item in got.values()),
                ["first", "second"])

    def test_blue_pairs_hold_two_slots(self):
        pairs = [
            (5, "int:5"),
            (True, "bool:1"),
            (5.0, "float:5.0"),
            (None, "none"),
            (b"5", "bytes:35"),
        ]
        for index, (first, second) in enumerate(pairs):
            with self.subTest(first=first, second=second):
                self._assert_two_slots(first, second, "blue" + str(index))

    def test_purple_pairs_hold_two_slots(self):
        pairs = [
            (1, "int:1"),
            (b"x", "bytes:78"),
            (None, "none"),
        ]
        for index, (first, second) in enumerate(pairs):
            with self.subTest(first=first, second=second):
                self._assert_two_slots(
                    first, second, "purple" + str(index))

    def test_controls_cured_epoch_forms(self):
        mod10.record_gate_passing_share("epoch-ctl", 5, "share-int")
        mod10.record_gate_passing_share("epoch-ctl", True, "share-bool")
        mod10.record_gate_passing_share("epoch-ctl", 5.0, "share-float")
        self.assertEqual(
            len(mod10.gate_passing_shares_for_run("epoch-ctl")), 3)
        mod10.record_gate_passing_share("epoch-ctl2", 5, "share-int")
        mod10.record_gate_passing_share("epoch-ctl2", "5", "share-text")
        self.assertEqual(
            len(mod10.gate_passing_shares_for_run("epoch-ctl2")), 2)
        mod10.record_gate_passing_share(
            "epoch-ctl3", "epoch-1", "share-text")
        got = mod10.gate_passing_shares_for_run("epoch-ctl3")
        self.assertEqual(got["epoch-1"]["share"], "share-text")


class LyingViewDict(dict):
    def __init__(self, stored, reported=None):
        super().__init__(stored)
        self._reported = reported or {}

    def get(self, key, default=None):
        if key in self._reported:
            return self._reported[key]
        return super().get(key, default)


class TestR12023ViewLeakCheckGet(Base):
    def test_canary_lying_get_refused(self):
        record = view_record()
        record["view_contents"] = [{"membership": "canaryvalue"}]
        handed = LyingViewDict(
            record, reported={"view_contents": [{"note": "clean"}]})
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(handed)
        self.assertIn("canary", str(caught.exception))

    def test_retain_lying_get_refused_and_not_retained(self):
        record = view_record()
        record["view_contents"] = [{"membership": "canaryvalue"}]
        handed = LyingViewDict(
            record, reported={"view_contents": [{"note": "clean"}]})
        with self.assertRaises(ValueError):
            mod10.retain_view_record(handed)
        self.assertEqual(mod10.view_records_for_run("run-v"), [])

    def test_timing_lying_get_refused(self):
        record = view_record()
        record["first_seen_day_per_record"] = {"0": 10}
        handed = LyingViewDict(
            record, reported={"first_seen_day_per_record": {}})
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(handed)
        self.assertIn("timing", str(caught.exception))

    def test_controls_plain_stored_forms(self):
        clean = view_record()
        self.assertTrue(mod10.run_view_leak_check(clean)["reportable"])
        barred = view_record()
        barred["view_contents"] = [{"membership": "canaryvalue"}]
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(barred)


class TestR12024TimingFormGuard(Base):
    def test_text_first_seen_raises_named_failure(self):
        record = view_record()
        record["first_seen_day_per_record"] = "oops"
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        message = str(caught.exception)
        self.assertIn("timing", message)
        self.assertIn("first_seen_day_per_record", message)
        self.assertIn("run-v/viewer-1", message)

    def test_list_first_seen_raises_named_failure(self):
        record = view_record()
        record["first_seen_day_per_record"] = ["oops"]
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("timing", str(caught.exception))
        self.assertIn(
            "first_seen_day_per_record", str(caught.exception))

    def test_lying_get_reporting_text_passes_on_stored_mapping(self):
        record = view_record()
        handed = LyingViewDict(
            record, reported={"first_seen_day_per_record": "oops"})
        result = mod10.run_view_leak_check(handed)
        self.assertTrue(result["reportable"])


if __name__ == "__main__":
    unittest.main()

"""Pins for fix wave 17, Builder 6, rows R17-011, R17-013,
R17-014, R17-015, R17-017, R17-018, R17-044, R17-047, R17-048,
and R17-052.

Each pin proves its charged defect on the pristine tree in the
distinguishing case standard: a handed equality, truth, string,
or rendering reading that the charged act must not trust, beside
a plain control whose standing the cure must keep.
"""
import unittest

from crucible import mod10, mod11, mod13, mod14


class LyingWeek:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class RaisingWeek:
    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = object.__hash__


class EqTrueStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqFalseStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class EqRaiseStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = str.__hash__


class ArmedKey:
    armed = False
    raised = False

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 42

    def __eq__(self, other):
        if ArmedKey.armed and not ArmedKey.raised:
            ArmedKey.raised = True
            raise RuntimeError("eq boom")
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class MergeKey:
    armed = False

    def __hash__(self):
        return hash("swallowed")

    def __eq__(self, other):
        if MergeKey.armed:
            raise RuntimeError("eq boom")
        return False

    def __ne__(self, other):
        if MergeKey.armed:
            raise RuntimeError("eq boom")
        return True


class CarriedFailure(Exception):
    pass


FIRED = {"flag_conditions_fired": ["condition-1"]}


class TestR17011WeeklyPairJudgement(unittest.TestCase):

    def test_lying_week_counts_no_record_at_either_act(self):
        records = [{"week": 999,
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(
            mod14.weekly_headline_count(records, LyingWeek()), 0)
        self.assertEqual(mod11.weekly_count(records, LyingWeek()), 0)

    def test_lying_week_helper_both_orders(self):
        self.assertFalse(mod14._week_stands_equal(LyingWeek(), 999))
        self.assertFalse(mod14._week_stands_equal(999, LyingWeek()))
        self.assertFalse(mod11._week_stands_equal(LyingWeek(), 999))
        self.assertFalse(mod11._week_stands_equal(999, LyingWeek()))

    def test_boolean_week_stands_apart_from_int_week(self):
        self.assertFalse(mod14._week_stands_equal(True, 1))
        self.assertFalse(mod14._week_stands_equal(1, True))
        self.assertFalse(mod11._week_stands_equal(True, 1))
        self.assertFalse(mod11._week_stands_equal(1, True))
        records = [{"week": 1,
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod14.weekly_headline_count(records, True), 0)
        self.assertEqual(mod11.weekly_count(records, True), 0)

    def test_raising_week_judges_not_equal_without_escape(self):
        self.assertFalse(mod14._week_stands_equal(RaisingWeek(), 1))
        self.assertFalse(mod11._week_stands_equal(RaisingWeek(), 1))
        self.assertFalse(mod11._week_stands_equal(1, RaisingWeek()))

    def test_plain_week_controls_hold(self):
        self.assertTrue(mod14._week_stands_equal("W1", "W1"))
        self.assertTrue(mod11._week_stands_equal(3, 3))
        self.assertFalse(mod11._week_stands_equal("W1", "W2"))
        records = [{"week": "W1",
                    "headline_unit_identifiers": ["u1"]}]
        self.assertEqual(mod14.weekly_headline_count(records, "W1"), 1)
        self.assertEqual(mod11.weekly_count(records, "W1"), 1)


class TestR17013PilotRunMembership(unittest.TestCase):

    def test_lying_true_bogus_use_refused(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.pilot_run(EqTrueStr("bogus"))
        self.assertIn("pilot use outside", str(caught.exception))

    def test_lying_false_timing_use_accepted(self):
        output = mod14.pilot_run(EqFalseStr("timing"))
        self.assertEqual(str.__str__(output["use"]), "timing")
        self.assertEqual(
            output["confinement_label"], "pilot confined")

    def test_raising_equality_timing_use_accepted(self):
        output = mod14.pilot_run(EqRaiseStr("timing"))
        self.assertEqual(str.__str__(output["use"]), "timing")

    def test_plain_controls_hold(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("bogus")
        output = mod14.pilot_run("timing")
        self.assertEqual(output["use"], "timing")


class TestR17014PilotConfined(unittest.TestCase):

    def test_lying_material_class_refused_at_contract(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.sweep_level_determinism_contract(
                {"material_class": EqTrueStr("bogus")})

    def test_lying_confinement_label_refused_at_census(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.nondeterminism_census(
                {"confinement_label": EqTrueStr("bogus")})

    def test_lying_false_genuine_label_accepted(self):
        record = mod14.sweep_level_determinism_contract(
            {"material_class": EqFalseStr("pilot confined")})
        self.assertEqual(record["material_class"], "pilot confined")

    def test_plain_controls_hold(self):
        record = mod14.nondeterminism_census(
            {"confinement_label": "pilot confined"})
        self.assertEqual(record["form"], "nondeterminism census")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.nondeterminism_census({"material_class": "bogus"})


class TestR17015ShellWriteEmptyIdentifier(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_shell_write_empty_run_identifier_refused(self):
        result = mod14.run_command("write_store", {
            "record": {"run_identifier": "", "figure": 1},
            "store_kind": "sweep"})
        self.assertIn("failure", result)
        self.assertIn("no identifier form", result["failure"])

    def test_core_retain_empty_run_identifier_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_run_record({"run_identifier": ""})

    def test_plain_write_and_read_controls_hold(self):
        result = mod14.run_command("write_store", {
            "record": {"run_id": "b6-015-run", "figure": 1},
            "store_kind": "sweep"})
        self.assertNotIn("failure", result)
        read = mod14.run_command("read_store", {
            "run_id": "b6-015-run", "store_kind": "sweep"})
        self.assertEqual(read["run_id"], "b6-015-run")


class TestR17017BufferTierConsumers(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def _promote(self, run_id, tier):
        mod10.write_summary_record({
            "run_id": run_id, "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition-1"]})
        return mod10.apply_flag_evaluation(
            mod10.summary_record_for_run(run_id),
            outcome="promote", tier=tier, inputs=dict(FIRED))

    def test_bytes_tier_promotion_reports_tier_forms(self):
        self._promote("b6-017a", b"Tier 2")
        record = mod10.retention_record_for_run("b6-017a")
        self.assertEqual(
            record["tier_forms"],
            ["final_checkpoint", "tenth_point_checkpoints"])
        self.assertEqual(record["shortfall"]["count"], 2)

    def test_bytearray_tier_promotion_reports_without_escape(self):
        self._promote("b6-017b", bytearray(b"Tier 2"))
        record = mod10.retention_record_for_run("b6-017b")
        self.assertEqual(
            record["tier_forms"],
            ["final_checkpoint", "tenth_point_checkpoints"])

    def test_memoryview_tier_promotion_reports_tier_forms(self):
        self._promote("b6-017c", memoryview(b"Tier 3"))
        record = mod10.retention_record_for_run("b6-017c")
        self.assertEqual(
            record["tier_forms"],
            ["final_checkpoint", "daily_checkpoints"])

    def test_effected_buffer_tier_closes(self):
        promoted = self._promote("b6-017d", b"Tier 2")
        with self.assertRaises(ValueError) as caught:
            mod10.close_run_retention(
                "b6-017d", promoted["retention_tier"])
        self.assertIn("run close in named form",
                      str(caught.exception))
        self.assertIn("no checkpoint stands retained",
                      str(caught.exception))

    def test_stored_bytes_tier_read_in_plain_form(self):
        mod10.write_summary_record({
            "run_id": "b6-017e", "retention_tier": b"Tier 2"})
        record = mod10.retention_record_for_run("b6-017e")
        self.assertEqual(
            record["tier_forms"],
            ["final_checkpoint", "tenth_point_checkpoints"])

    def test_plain_promotion_control_hold(self):
        self._promote("b6-017f", "Tier 2")
        record = mod10.retention_record_for_run("b6-017f")
        self.assertEqual(record["retention_tier"], "Tier 2")
        self.assertEqual(
            record["tier_forms"],
            ["final_checkpoint", "tenth_point_checkpoints"])


class TestR17018CloseRetentionTier(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()
        for day in (1, 2):
            mod10.retain_checkpoint({
                "run_identifier": "b6-018-run",
                "simulated_day": day})

    def test_lying_bogus_tier_refused_at_close(self):
        with self.assertRaises(ValueError) as caught:
            mod10.close_run_retention(
                "b6-018-run", EqTrueStr("bogus"))
        self.assertIn("unknown retention tier", str(caught.exception))

    def test_plain_controls_hold(self):
        with self.assertRaises(ValueError):
            mod10.close_run_retention("b6-018-run", "bogus")
        record = mod10.close_run_retention("b6-018-run", "Tier 0")
        self.assertEqual(record["kept_days"], [])
        self.assertEqual(record["released_days"], [1, 2])


class TestR17044WeeklyRefusalSentences(unittest.TestCase):

    def _message(self, records, week="W1"):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.weekly_headline_count(records, week)
        return str(caught.exception)

    def test_missing_field_sentence_complete(self):
        message = self._message([{"week": "W1"}])
        self.assertIn(
            "and no weekly headline count stands certified "
            "without it", message)

    def test_no_value_sentence_complete(self):
        message = self._message(
            [{"week": "W1", "headline_unit_identifiers": None}])
        self.assertIn(
            "and no weekly headline count stands certified "
            "without it", message)

    def test_unreadable_field_sentence_complete(self):
        message = self._message(
            [{"week": "W1", "headline_unit_identifiers": 42}])
        self.assertIn(
            "no weekly headline count stands certified "
            "without it", message)


class TestR17047ErrorCarriageLimbs(unittest.TestCase):

    def tearDown(self):
        ArmedKey.armed = False
        ArmedKey.raised = False
        MergeKey.armed = False

    def test_freeze_inner_dict_raising_keys_carried(self):
        first = ArmedKey("a")
        second = ArmedKey("b")
        failure = CarriedFailure("boom")
        failure.failure = {"inner": {first: 1, second: 2}}
        ArmedKey.armed = True
        carriage = mod14.error_carriage(failure)
        self.assertTrue(carriage["operator_sees_failure"])

    def test_merge_loop_raising_key_carried(self):
        key = MergeKey()
        failure = CarriedFailure("boom")
        failure.failure = {key: "carried value"}
        MergeKey.armed = True
        carriage = mod14.error_carriage(failure)
        self.assertTrue(carriage["operator_sees_failure"])
        self.assertFalse(carriage["swallowed"])

    def test_plain_carriage_control_hold(self):
        carriage = mod14.error_carriage(
            mod14.NamedShellFailure("named boom"))
        self.assertIn("named boom", carriage["failure"])
        self.assertTrue(carriage["operator_sees_failure"])


class TestR17048WeekEscapeCarriage(unittest.TestCase):

    def test_direct_helper_raising_week_no_escape(self):
        self.assertFalse(
            mod14._week_stands_equal(RaisingWeek(), 7))

    def test_shell_weekly_count_over_raising_week(self):
        result = mod14.run_command("weekly_headline_count", {
            "summary_records": [{
                "week": RaisingWeek(),
                "headline_unit_identifiers": ["u1"]}],
            "week": 7})
        self.assertEqual(result.get("count"), 0)
        self.assertNotIn("failure", result)


class TestR17052MemoryviewVocabularyRendering(unittest.TestCase):

    def setUp(self):
        mod10.reset_stores()

    def test_mod10_tier_vocabulary_names_stored_tier(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                {}, outcome=None, tier=memoryview(b"Tier 9"))
        message = str(caught.exception)
        self.assertIn("names: Tier 9;", message)
        self.assertNotIn("memory at", message)

    def test_mod10_no_rise_names_stated_tier(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                {"retention_tier": "Tier 2"}, outcome="promote",
                tier=memoryview(b"Tier 2"), inputs=dict(FIRED))
        message = str(caught.exception)
        self.assertIn("stated tier Tier 2 does not rise", message)
        self.assertNotIn("memory at", message)

    def test_mod14_tier_vocabulary_names_stored_tier(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                {}, outcome="promote",
                tier=memoryview(b"Tier 9"), inputs=dict(FIRED))
        message = str(caught.exception)
        self.assertIn("names: Tier 9;", message)
        self.assertNotIn("memory at", message)

    def test_mod13_outcome_vocabulary_names_stored_outcome(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record(
                "c1", outcome=memoryview(b"rests"))
        message = str(caught.exception)
        self.assertIn("unknown verdict outcome: rests;", message)
        self.assertNotIn("memory at", message)


if __name__ == "__main__":
    unittest.main()

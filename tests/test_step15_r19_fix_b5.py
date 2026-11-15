"""Pins for fix wave 18, Builder 5, rows R18-009, R18-010,
R18-011, R18-012, R18-013, R18-015, and R18-057.

Each pin proves its charged defect on the pristine tree in the
distinguishing case standard: a handed equality, hash, or kind
reading that the charged act must not trust, beside a plain
control whose standing the cure must keep.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod10


class AlwaysEq:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class EqFalseStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class EqTrueStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqRaiseStr(str):
    def __new__(cls, text):
        return str.__new__(cls, text)

    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = str.__hash__


class CraftedTier:
    def __hash__(self):
        return hash("Tier 2")

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


class RaisingEqTier:
    def __hash__(self):
        return hash("Tier 2")

    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")


class RaisingHashTier:
    def __hash__(self):
        raise RuntimeError("hash boom")

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


def view_record(run_id):
    return {
        "run_identifier": run_id,
        "viewer_identifier": "viewer-1",
        "simulated_day": 5,
        "scheduling_position_identifier": "position-1",
        "rule_version_set": "rule-set-1",
        "view_contents": [{"item": "ordinary content"}],
        "reputation_and_band_values": {"band": "stated"},
        "graph_position_as_seen": "stated",
        "first_seen_day_per_record": {"item": 3},
        "delay_applied_per_record": {"item": 1},
        "completeness_state": "complete",
        "building_component": "Recorder",
        "delivering_contract": "stated",
        "selection_rule_version": "rule-set-1",
    }


class B5Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR18009BaseValueEqClosingLimb(B5Base):

    def test_distinct_always_equal_objects_judge_apart(self):
        self.assertFalse(mod10._base_value_eq(AlwaysEq(), AlwaysEq()))

    def test_resume_refused_on_always_equal_checkpoint_value(self):
        mod10.retain_checkpoint({
            "run_identifier": "b5-r09-run", "simulated_day": 1,
            "payload": AlwaysEq()})
        handed = {
            "run_identifier": "b5-r09-run", "simulated_day": 1,
            "payload": AlwaysEq()}
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)

    def test_same_object_judges_equal(self):
        obj = AlwaysEq()
        self.assertTrue(mod10._base_value_eq(obj, obj))

    def test_plain_pairs_control(self):
        self.assertTrue(mod10._base_value_eq(1, 1))
        self.assertTrue(mod10._base_value_eq(
            [1, {"a": 2}], [1, {"a": 2}]))
        self.assertTrue(mod10._base_value_eq("x", "x"))
        self.assertFalse(mod10._base_value_eq([1, 2], [1, 3]))
        self.assertTrue(mod10._base_value_eq(
            Decimal(1), Decimal(1)))
        self.assertFalse(mod10._base_value_eq(True, 1))


class TestR18010DeferredEvaluationFiring(B5Base):

    def test_bool_firing_refused(self):
        record = {"run_id": "b5-r10-boolf"}
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                record, True, inputs="i", outcome="o")

    def test_decimal_firing_1_refused(self):
        record = {"run_id": "b5-r10-decf"}
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                record, Decimal(1), inputs="i", outcome="o")

    def test_fraction_firing_1_refused(self):
        record = {"run_id": "b5-r10-fracf"}
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                record, Fraction(1, 1), inputs="i", outcome="o")

    def test_decimal_and_fraction_firing_2_refused(self):
        first = [{"firing": 1, "inputs": "x", "outcome": "y"}]
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                {"run_id": "b5-r10-dec2",
                 "deferred_evaluations": list(first)}, Decimal(2),
                inputs="i", outcome="o")
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                {"run_id": "b5-r10-frac2",
                 "deferred_evaluations": list(first)}, Fraction(2, 1),
                inputs="i", outcome="o")

    def test_float_firing_2_refused_and_hold_kept(self):
        mod10.place_reserve_hold("b5-r10-hold")
        mod10.apply_deferred_evaluation(
            {"run_id": "b5-r10-hold"}, 1, inputs="i", outcome="o")
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                {"run_id": "b5-r10-hold"}, 2.0, inputs="i", outcome="o")
        self.assertIsNotNone(mod10.reserve_hold_for_run("b5-r10-hold"))

    def test_second_firing_written_twice_across_records_refused(self):
        mod10.apply_deferred_evaluation(
            {"run_id": "b5-r10-dup"}, 1, inputs="i", outcome="o")
        mod10.apply_deferred_evaluation(
            {"run_id": "b5-r10-dup"}, 2, inputs="i", outcome="o")
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                {"run_id": "b5-r10-dup"}, 2, inputs="i", outcome="o")

    def test_bool_entry_does_not_displace_genuine_firing_1(self):
        handed = {
            "run_id": "b5-r10-boolentry",
            "deferred_evaluations": [
                {"firing": True, "inputs": "x", "outcome": "y"}]}
        result = mod10.apply_deferred_evaluation(
            handed, 1, inputs="i", outcome="o")
        firings = [
            entry.get("firing")
            for entry in result["deferred_evaluations"]]
        self.assertIn(1, firings)

    def test_plain_firings_control_and_release(self):
        mod10.place_reserve_hold("b5-r10-plain")
        mod10.apply_deferred_evaluation(
            {"run_id": "b5-r10-plain"}, 1, inputs="i", outcome="o")
        second = mod10.apply_deferred_evaluation(
            {"run_id": "b5-r10-plain"}, 2, inputs="i", outcome="o")
        self.assertEqual(second.get("reserve_hold_state"), "released")


class TestR18011Gc08KindLimb(B5Base):

    def test_lying_kind_refused(self):
        with self.assertRaises(ValueError):
            mod10.retain_gc08_record(
                EqTrueStr("bogus"), {"a": 1}, "b5-owner-lying")

    def test_stated_kind_in_eq_false_dress_retained(self):
        returned = mod10.retain_gc08_record(
            EqFalseStr("call_log"), {"a": 1}, "b5-owner-false")
        self.assertEqual(returned, {"a": 1})
        self.assertEqual(
            mod10.gc08_record("call_log", "b5-owner-false"), {"a": 1})

    def test_raising_kind_retained(self):
        returned = mod10.retain_gc08_record(
            EqRaiseStr("dependency_manifest"), {"b": 2}, "b5-owner-raise")
        self.assertEqual(returned, {"b": 2})

    def test_plain_kinds_control(self):
        returned = mod10.retain_gc08_record(
            "call_log", {"c": 3}, "b5-owner-plain")
        self.assertEqual(returned, {"c": 3})
        with self.assertRaises(ValueError):
            mod10.retain_gc08_record(
                "bogus", {"c": 3}, "b5-owner-plain")


class TestR18012ComposedTierLookup(B5Base):

    def _record_for(self, run_id, tier):
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": tier})
        return mod10.retention_record_for_run(run_id)

    def test_crafted_tier_object_judged_as_no_tier(self):
        crafted = CraftedTier()
        result = self._record_for("b5-r12-crafted", crafted)
        self.assertFalse(result["shortfall_judged"])
        self.assertEqual(result["tier_forms"], [])
        self.assertIsNot(result["retention_tier"], crafted)
        self.assertIsNone(result["retention_tier"])

    def test_raising_eq_tier_escapes_nowhere(self):
        result = self._record_for("b5-r12-raisingeq", RaisingEqTier())
        self.assertFalse(result["shortfall_judged"])
        self.assertEqual(result["tier_forms"], [])

    def test_raising_hash_tier_escapes_nowhere(self):
        result = self._record_for("b5-r12-raisinghash", RaisingHashTier())
        self.assertFalse(result["shortfall_judged"])
        self.assertEqual(result["tier_forms"], [])

    def test_plain_and_buffer_tier_controls(self):
        plain = self._record_for("b5-r12-plain", "Tier 2")
        self.assertTrue(plain["shortfall_judged"])
        self.assertIn("final_checkpoint", plain["tier_forms"])
        buffered = self._record_for("b5-r12-buffer", b"Tier 2")
        self.assertTrue(buffered["shortfall_judged"])
        self.assertIn("final_checkpoint", buffered["tier_forms"])


class TestR18013CloseTenthSet(B5Base):

    def test_tier2_keeps_day_10_not_day_11(self):
        for day in range(2, 13):
            mod10.retain_checkpoint({
                "run_identifier": "b5-r13-run", "simulated_day": day})
        result = mod10.close_run_retention("b5-r13-run", "Tier 2")
        self.assertEqual(result["kept_days"], [10, 12])
        self.assertIn(11, result["released_days"])
        self.assertNotIn(10, result["released_days"])

    def test_tier2_final_only_control(self):
        for day in (1, 2, 3):
            mod10.retain_checkpoint({
                "run_identifier": "b5-r13-ctl", "simulated_day": day})
        result = mod10.close_run_retention("b5-r13-ctl", "Tier 2")
        self.assertEqual(result["kept_days"], [3])
        self.assertEqual(result["released_days"], [1, 2])


class TestR18015RetainViewRecordSplit(B5Base):

    def test_buffer_tier_argument_takes_companion(self):
        returned = mod10.retain_view_record(
            view_record("b5-r15-bufarg"), tier=b"Tier 1")
        self.assertIn("divergence_companion", returned)
        self.assertNotIn("view_contents", returned)
        self.assertEqual(returned["retention_tier"], "Tier 1")
        self.assertIs(type(returned["retention_tier"]), str)

    def test_buffer_tier_on_record_takes_companion(self):
        record = view_record("b5-r15-bufrec")
        record["retention_tier"] = b"Tier 1"
        returned = mod10.retain_view_record(record)
        self.assertIn("divergence_companion", returned)
        self.assertNotIn("view_contents", returned)
        self.assertEqual(returned["retention_tier"], "Tier 1")

    def test_raising_eq_tier_takes_companion(self):
        returned = mod10.retain_view_record(
            view_record("b5-r15-raise"), tier=EqRaiseStr("Tier 1"))
        self.assertIn("divergence_companion", returned)
        self.assertEqual(returned["retention_tier"], "Tier 1")

    def test_plain_tier_controls(self):
        companion = mod10.retain_view_record(
            view_record("b5-r15-t1"), tier="Tier 1")
        self.assertIn("divergence_companion", companion)
        full = mod10.retain_view_record(
            view_record("b5-r15-t2"), tier="Tier 2")
        self.assertIn("view_contents", full)
        self.assertEqual(full["retention_tier"], "Tier 2")


class TestR18057ShortfallSentenceGround(B5Base):

    def test_number_tier_sentence_does_not_claim_unstated(self):
        mod10.write_summary_record(
            {"run_id": "b5-r57-num", "retention_tier": 3})
        result = mod10.retention_record_for_run("b5-r57-num")
        self.assertFalse(result["shortfall_judged"])
        self.assertEqual(result["tier_forms"], [])
        bound = result["shortfall"]["bound"]
        self.assertIn("not judged", bound)
        self.assertNotIn("unstated or unknown", bound)

    def test_no_tier_sentence_control(self):
        mod10.write_summary_record({"run_id": "b5-r57-none"})
        result = mod10.retention_record_for_run("b5-r57-none")
        self.assertFalse(result["shortfall_judged"])
        self.assertIn("unstated or unknown", result["shortfall"]["bound"])

    def test_unknown_tier_name_control(self):
        mod10.write_summary_record(
            {"run_id": "b5-r57-t9", "retention_tier": "Tier 9"})
        result = mod10.retention_record_for_run("b5-r57-t9")
        self.assertFalse(result["shortfall_judged"])
        self.assertEqual(result["tier_forms"], [])
        self.assertIn("not judged", result["shortfall"]["bound"])


if __name__ == "__main__":
    unittest.main()

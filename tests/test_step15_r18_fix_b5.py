"""Pin tests for fix wave 17, Builder 5, Group 5 rows.

Rows pinned: R17-008, R17-016, R17-029, R17-030, R17-031,
R17-032, R17-033, R17-034, R17-050. Each pin states the charged
defect at its locus in crucible/mod10.py and fails on the pristine
code for that defect.
"""
import os
import tempfile
import unittest
from decimal import Decimal
from fractions import Fraction

import crucible.mod10 as mod10


class CustomBoom(Exception):
    pass


class StrBoomStr(str):
    def __str__(self):
        raise RuntimeError("boom-str-rid")


class StrRaisesValue:
    def __str__(self):
        raise ValueError("boom-str-view")


class StrRaisesCustom:
    def __str__(self):
        raise CustomBoom("boom-str-custom")


class ReprRaisesValue:
    def __repr__(self):
        raise ValueError("boom-repr-value")


class ReprRaisesCustom:
    def __repr__(self):
        raise CustomBoom("boom-repr-custom")


class EqRaises:
    def __init__(self, target):
        self._target = target

    def __hash__(self):
        return hash(self._target)

    def __eq__(self, other):
        raise RuntimeError("boom-eq")


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR17008(Base):
    def test_bool_decimal_fraction_apart_from_int(self):
        self.assertFalse(mod10._base_value_eq(True, 1))
        self.assertFalse(mod10._base_value_eq(1, True))
        self.assertFalse(mod10._base_value_eq(Decimal(1), 1))
        self.assertFalse(mod10._base_value_eq(1, Decimal(1)))
        self.assertFalse(mod10._base_value_eq(Fraction(1, 1), 1))
        self.assertFalse(mod10._base_value_eq(1, Fraction(1, 1)))
        self.assertFalse(mod10._base_value_eq(False, 0))

    def test_nested_cross_kind(self):
        self.assertFalse(mod10._base_value_eq([True], [1]))
        self.assertFalse(mod10._base_value_eq([Decimal(1)], [1]))
        self.assertFalse(mod10._base_value_eq({"k": Fraction(1, 1)}, {"k": 1}))

    def test_same_kind_controls(self):
        self.assertTrue(mod10._base_value_eq(True, True))
        self.assertTrue(mod10._base_value_eq(Decimal(1), Decimal(1)))
        self.assertTrue(mod10._base_value_eq(Fraction(1, 2), Fraction(1, 2)))
        self.assertFalse(mod10._base_value_eq(Decimal(1), Decimal(2)))
        self.assertTrue(mod10._base_value_eq(1, 1))
        self.assertTrue(mod10._base_value_eq(1, 1.0))
        self.assertTrue(mod10._base_value_eq([1, 2, 3], [1, 2, 3]))

    def _record(self, conditions):
        return {
            "later_evaluation": {
                "conditions": conditions,
                "inputs": "recorded",
                "outcome": "recorded",
            },
            "summary_record_written": True,
            "retained_forms_pointed_to": ["event_log"],
        }

    def test_retention_met_cross_kind_conditions(self):
        self.assertFalse(mod10.retention_met(self._record([True, 2, 3])))
        self.assertFalse(mod10.retention_met(self._record([Decimal(1), 2, 3])))
        self.assertFalse(mod10.retention_met(self._record([Fraction(1, 1), 2, 3])))
        self.assertTrue(mod10.retention_met(self._record([1, 2, 3])))
        self.assertTrue(mod10.retention_met(self._record([1.0, 2, 3])))


class TestR17016(Base):
    def test_tier3_fully_retained_no_shortfall(self):
        run_id = "b5-t3full"
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 3"})
        for day in (1, 2, 3):
            mod10.retain_checkpoint(
                {"run_identifier": run_id, "simulated_day": day})
            mod10.retain_daily_snapshot(
                {"run_identifier": run_id, "simulated_day": day})
        mod10.retain_event_log_entry({"run_identifier": run_id})
        record = mod10.retention_record_for_run(run_id)
        self.assertIn("daily_checkpoints", record["retained_forms"])
        self.assertEqual(record["not_retained"], [])
        self.assertEqual(record["shortfall"]["count"], 0)

    def test_tier2_tenth_point_retained_no_shortfall(self):
        run_id = "b5-t2full"
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 2"})
        for day in (0, 10, 20):
            mod10.retain_checkpoint(
                {"run_identifier": run_id, "simulated_day": day})
        record = mod10.retention_record_for_run(run_id)
        self.assertIn("tenth_point_checkpoints", record["retained_forms"])
        self.assertEqual(record["not_retained"], [])
        self.assertEqual(record["shortfall"]["count"], 0)

    def test_tier2_without_tenth_point_still_shortfall(self):
        run_id = "b5-t2part"
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 2"})
        for day in (1, 2):
            mod10.retain_checkpoint(
                {"run_identifier": run_id, "simulated_day": day})
        record = mod10.retention_record_for_run(run_id)
        self.assertEqual(
            record["not_retained"], ["tenth_point_checkpoints: not retained"])
        self.assertEqual(record["shortfall"]["count"], 1)

    def test_tier3_single_checkpoint_daily_not_yet_credited(self):
        run_id = "b5-t3single"
        mod10.write_summary_record(
            {"run_id": run_id, "retention_tier": "Tier 3"})
        mod10.retain_checkpoint(
            {"run_identifier": run_id, "simulated_day": 1})
        record = mod10.retention_record_for_run(run_id)
        self.assertEqual(
            record["not_retained"], ["daily_checkpoints: not retained"])

    def test_nothing_retained_controls(self):
        mod10.write_summary_record(
            {"run_id": "b5-t3none", "retention_tier": "Tier 3"})
        record = mod10.retention_record_for_run("b5-t3none")
        self.assertEqual(record["shortfall"]["count"], 2)
        mod10.write_summary_record(
            {"run_id": "b5-t1one", "retention_tier": "Tier 1"})
        mod10.retain_checkpoint(
            {"run_identifier": "b5-t1one", "simulated_day": 1})
        record = mod10.retention_record_for_run("b5-t1one")
        self.assertEqual(record["shortfall"]["count"], 0)


class TestR17050(Base):
    def test_tier0_judged_zero(self):
        mod10.write_summary_record(
            {"run_id": "b5-tier0", "retention_tier": "Tier 0"})
        record = mod10.retention_record_for_run("b5-tier0")
        self.assertEqual(record["shortfall"]["count"], 0)
        self.assertTrue(record["shortfall_judged"])
        self.assertIn("0 of 0", record["shortfall"]["bound"])

    def test_unstated_tier_not_judged(self):
        mod10.write_summary_record({"run_id": "b5-notier"})
        record = mod10.retention_record_for_run("b5-notier")
        self.assertFalse(record["shortfall_judged"])
        self.assertNotIn("0 of 0", record["shortfall"]["bound"])
        self.assertIn("not judged", record["shortfall"]["bound"])

    def test_unknown_tier_not_judged(self):
        mod10.write_summary_record(
            {"run_id": "b5-tier9", "retention_tier": "Tier 9"})
        record = mod10.retention_record_for_run("b5-tier9")
        self.assertFalse(record["shortfall_judged"])
        self.assertNotIn("0 of 0", record["shortfall"]["bound"])
        self.assertIn("not judged", record["shortfall"]["bound"])

    def test_known_tier_bound_differs_from_unstated(self):
        mod10.write_summary_record(
            {"run_id": "b5-t0b", "retention_tier": "Tier 0"})
        mod10.write_summary_record({"run_id": "b5-ntb"})
        tier0 = mod10.retention_record_for_run("b5-t0b")
        unstated = mod10.retention_record_for_run("b5-ntb")
        self.assertNotEqual(
            tier0["shortfall"]["bound"], unstated["shortfall"]["bound"])


class TestR17029(Base):
    def test_sort_limb_str_raising_identifier_no_bare_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(path=path)
            try:
                store.retain_run_record(
                    {"run_id": StrBoomStr("b5-sb1"), "v": 1})
            except RuntimeError:
                self.fail("bare RuntimeError escaped the flush sort limb")
            except ValueError as exc:
                self.assertIn("flush failure", str(exc))
                self.assertFalse(store.has_run_record(StrBoomStr("b5-sb1")))
            else:
                self.assertTrue(os.path.exists(path))

    def test_serialisation_limb_named_sentence_and_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(path=path)
            with self.assertRaises(ValueError) as caught:
                store.retain_run_record({"run_id": "b5-ns1", "v": object()})
            text = str(caught.exception)
            self.assertIn("recorder store flush failure", text)
            self.assertIn("not written", text)
            self.assertIn("prior store file stands whole", text)
            self.assertFalse(store.has_run_record("b5-ns1"))
            self.assertFalse(os.path.exists(path))

    def test_serialisation_limb_set_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(path=path)
            with self.assertRaises(ValueError) as caught:
                store.retain_run_record({"run_id": "b5-ns2", "v": {1, 2}})
            self.assertIn("recorder store flush failure", str(caught.exception))
            self.assertFalse(store.has_run_record("b5-ns2"))

    def test_clear_failure_named_sentence_and_state_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(path=path)
            store.retain_run_record({"run_id": "b5-cl1", "v": 1})
            os.mkdir(path + ".tmp")
            with self.assertRaises(ValueError) as caught:
                store.clear()
            text = str(caught.exception)
            self.assertIn("flush failure", text)
            self.assertIn("prior store file stands whole", text)
            self.assertEqual(store.index(), ["b5-cl1"])
            self.assertTrue(store.has_run_record("b5-cl1"))

    def test_oserror_control_still_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "store.json")
            store = mod10.new_store(path=path)
            store.retain_run_record({"run_id": "b5-oe1", "v": 1})
            os.mkdir(path + ".tmp")
            with self.assertRaises(ValueError) as caught:
                store.retain_run_record({"run_id": "b5-oe2", "v": 2})
            self.assertIn(
                "recorder store flush failure", str(caught.exception))
            self.assertEqual(store.index(), ["b5-oe1"])


class TestR17030(Base):
    def test_view_name_str_raising_value_error(self):
        record = {"run_identifier": StrRaisesValue(), "viewer_id": "v1"}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("view leak check failure", str(caught.exception))
        self.assertNotIn("boom-str-view", str(caught.exception))

    def test_view_name_str_raising_custom(self):
        record = {"run_id": "b5-v2", "viewer_identifier": StrRaisesCustom()}
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("view leak check failure", str(caught.exception))


class TestR17031(Base):
    def test_position_repr_raising_value_error(self):
        manifest = {
            "run_identifier": "b5-p1", "journal_position": ReprRaisesValue()}
        result = mod10.checkpoint_position_check(manifest)
        self.assertIn("no integer form", result["outcome"])
        self.assertIn("not checked", result["outcome"])

    def test_position_repr_raising_custom(self):
        manifest = {
            "run_identifier": "b5-p2", "journal_position": ReprRaisesCustom()}
        result = mod10.checkpoint_position_check(manifest)
        self.assertIn("no integer form", result["outcome"])


class TestR17032(Base):
    def _delivery(self, viewer, component):
        return {
            "viewer_id": viewer,
            "simulated_day": 1,
            "joint_outcome_components": [component],
            "component_denominators": [1],
        }

    def test_where_clause_viewer_str_raising_custom(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b5-d1", [self._delivery(StrRaisesCustom(), "bad")])
        self.assertIn(
            "daily aggregate delivery in named form", str(caught.exception))

    def test_component_repr_raising_custom(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b5-d2", [self._delivery("v1", ReprRaisesCustom())])
        self.assertIn(
            "daily aggregate delivery in named form", str(caught.exception))

    def test_component_repr_raising_value_error_named_sentence(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b5-d3", [self._delivery("v1", ReprRaisesValue())])
        text = str(caught.exception)
        self.assertIn("daily aggregate delivery in named form", text)
        self.assertIn("non numeric form", text)
        self.assertNotIn("boom-repr-value", text)


class TestR17033(Base):
    def test_unhashable_identifier_named_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod10.restore_check({"relative_identifier": ["x"]}, {"a"})
        self.assertIn("restore_check", str(caught.exception))
        self.assertIn("stands refused", str(caught.exception))

    def test_controls(self):
        portable = {"relative_identifier": "checkpoints/a"}
        self.assertTrue(mod10.restore_check(portable, {"checkpoints/a"}))
        self.assertFalse(mod10.restore_check(portable, {"other"}))


class TestR17034(Base):
    def test_eq_raising_identifier_lookup_failure(self):
        mod10.write_summary_record(
            {"run_id": "b5-x34", "retention_tier": "Tier 1"})
        with self.assertRaises(mod10.LookupFailure):
            mod10.summary_record_for_run(EqRaises("b5-x34"))

    def test_eq_raising_identifier_empty_store_control(self):
        result = mod10.summary_record_for_run(EqRaises("b5-absent34"))
        self.assertEqual(result["form"], "form_only")
        self.assertFalse(result["record_found"])


if __name__ == "__main__":
    unittest.main()

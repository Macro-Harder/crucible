"""Pins for fix wave 18, Builder 8, Group 8 rows.

Rows pinned: R18-019 (MOD-05 _get non dict limb), R18-039
(MOD-01 _base_value_equals closing fallback), R18-047 (MOD-07
identifier comparisons), R18-048 (MOD-05 _panel_leaf_copy buffer
limb), and R18-049 (MOD-04 ContractAHandover.verify_intact).
"""

import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod01, mod04, mod05, mod07


class AlwaysEqual:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 42


class RaisingEq:
    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    def __ne__(self, other):
        raise RuntimeError("equality reading raises")

    def __hash__(self):
        return 43


class GetattrFabricator:
    def __getattr__(self, name):
        if name == "agent_identifier":
            return "fabricated-agent"
        if name == "accepted":
            return True
        return 999


class RaisingPropertyEvent:
    @property
    def agent_identifier(self):
        raise RuntimeError("property reading raises")


class AttributeEvent:
    agent_identifier = "attr-agent"
    accepted = True


class TestR18019GetNonDictLimb(unittest.TestCase):
    def test_get_lying_getattr_unknown_field_reads_default(self):
        self.assertIsNone(mod05._get(GetattrFabricator(), "some_field"))

    def test_get_lying_getattr_named_field_reads_default(self):
        self.assertIsNone(
            mod05._get(GetattrFabricator(), "agent_identifier"))

    def test_get_raising_property_reads_default(self):
        self.assertIsNone(
            mod05._get(RaisingPropertyEvent(), "agent_identifier"))

    def test_work_credit_fabricated_agent_refused(self):
        with self.assertRaises(ValueError):
            mod05.work_credit([GetattrFabricator()])

    def test_work_credit_raising_property_refused_by_sentence(self):
        with self.assertRaises(ValueError):
            mod05.work_credit([RaisingPropertyEvent()])

    def test_work_credit_attribute_event_refused(self):
        with self.assertRaises(ValueError):
            mod05.work_credit([AttributeEvent()])

    def test_dict_event_counted_whole(self):
        result = mod05.work_credit(
            [{"agent_identifier": "agent-a", "accepted": True}])
        self.assertEqual(
            result["counters"]["agent-a"]["submitted"], 1)
        self.assertEqual(
            result["counters"]["agent-a"]["accepted"], 1)

    def test_dict_event_without_agent_refused(self):
        with self.assertRaises(ValueError):
            mod05.work_credit([{"accepted": True}])

    def test_get_dict_limb_reads_stored_fields(self):
        self.assertEqual(mod05._get({"x": 5}, "x"), 5)
        self.assertIsNone(mod05._get({}, "x"))
        self.assertEqual(
            mod05._get({"x": None}, "x", default="d"), "d")


class TestR18039BaseValueEqualsClosing(unittest.TestCase):
    def test_always_equal_pair_judged_apart(self):
        self.assertFalse(
            mod01._base_value_equals(AlwaysEqual(), AlwaysEqual()))

    def test_raising_pair_judged_apart_without_escape(self):
        self.assertFalse(
            mod01._base_value_equals(RaisingEq(), RaisingEq()))

    def test_always_equal_against_plain_object_judged_apart(self):
        self.assertFalse(
            mod01._base_value_equals(AlwaysEqual(), object()))

    def test_nested_always_equal_values_judged_apart(self):
        self.assertFalse(mod01._base_value_equals(
            {"k": AlwaysEqual()}, {"k": AlwaysEqual()}))

    def test_gate_always_equal_versions_refused(self):
        manifest = {
            "family_version": AlwaysEqual(),
            "sealed_family_record_hash": "hash-a",
        }
        record = {
            "family_version": AlwaysEqual(),
            "family_manifest_hash": "hash-a",
        }
        self.assertFalse(
            mod01.validate_family_seal_match(manifest, record))

    def test_gate_raising_versions_refused_without_escape(self):
        manifest = {
            "family_version": RaisingEq(),
            "sealed_family_record_hash": "hash-a",
        }
        record = {
            "family_version": RaisingEq(),
            "family_manifest_hash": "hash-a",
        }
        self.assertFalse(
            mod01.validate_family_seal_match(manifest, record))

    def test_plain_number_controls(self):
        self.assertTrue(mod01._base_value_equals(7, 7))
        self.assertFalse(mod01._base_value_equals(7, 8))
        self.assertTrue(mod01._base_value_equals(1, 1.0))

    def test_kind_first_core_controls(self):
        self.assertFalse(mod01._base_value_equals(True, 1))
        self.assertTrue(
            mod01._base_value_equals(Decimal(1), Decimal(1)))
        self.assertTrue(mod01._base_value_equals(
            Fraction(1, 1), Fraction(1, 1)))
        self.assertFalse(
            mod01._base_value_equals(Decimal(1), 1))

    def test_text_and_identity_controls(self):
        self.assertTrue(mod01._base_value_equals("abc", "abc"))
        self.assertFalse(mod01._base_value_equals("abc", "abd"))
        marker = AlwaysEqual()
        self.assertTrue(mod01._base_value_equals(marker, marker))

    def test_buffer_controls(self):
        self.assertTrue(mod01._base_value_equals(b"abc", b"abc"))
        self.assertFalse(mod01._base_value_equals(b"abc", b"abd"))
        self.assertTrue(mod01._base_value_equals(
            bytearray(b"abc"), bytearray(b"abc")))


class TestR18047Mod07Identifiers(unittest.TestCase):
    def test_reading_bool_entry_not_matched_by_int(self):
        log = [{"choice_identifier": True, "reading_applied": "r"}]
        self.assertIsNone(mod07.reading_for_result(log, 1))

    def test_reading_int_entry_not_matched_by_bool(self):
        log = [{"choice_identifier": 1, "reading_applied": "r"}]
        self.assertIsNone(mod07.reading_for_result(log, True))

    def test_reading_decimal_entry_not_matched_by_int(self):
        log = [
            {"choice_identifier": Decimal(1), "reading_applied": "r"}]
        self.assertIsNone(mod07.reading_for_result(log, 1))

    def test_pair_stands_ignores_cross_kind_stored_log_entry(self):
        choice = mod07.make_adapter_choice(
            1, "reading one", "rule point 1", "text v1",
            "B-4 fold 1")
        built_log = mod07.interpretation_log_entry(choice)
        tampered = dict(built_log)
        tampered["choice_identifier"] = True
        tampered["reading_applied"] = "wrong reading"
        run = {"interpretation_log_entries": [tampered]}
        self.assertTrue(mod07._stored_pair_stands(run, choice))

    def test_reading_exact_match_control(self):
        log = [{"choice_identifier": 1, "reading_applied": "r"}]
        found = mod07.reading_for_result(log, 1)
        self.assertEqual(found["reading_applied"], "r")
        text_log = [
            {"choice_identifier": "choice-x", "reading_applied": "s"}]
        found_text = mod07.reading_for_result(text_log, "choice-x")
        self.assertEqual(found_text["reading_applied"], "s")

    def test_pair_stands_no_stored_sides_control(self):
        choice = mod07.make_adapter_choice(
            1, "reading one", "rule point 1", "text v1",
            "B-4 fold 1")
        self.assertTrue(mod07._stored_pair_stands({}, choice))

    def test_pair_stands_wrong_run_entry_control(self):
        choice = mod07.make_adapter_choice(
            1, "reading one", "rule point 1", "text v1",
            "B-4 fold 1")
        built_run = mod07.run_record_entry(choice)
        wrong = dict(built_run)
        wrong["reading_applied"] = "wrong reading"
        run = {"run_record_entries": [wrong]}
        self.assertFalse(mod07._stored_pair_stands(run, choice))


class TestR18048PanelLeafBuffer(unittest.TestCase):
    def test_bytearray_leaf_copied_apart(self):
        source = bytearray(b"efg")
        delivered = mod05.panel_inputs({"field": source})
        self.assertIsNot(delivered["field"], source)
        self.assertEqual(bytes(delivered["field"]), b"efg")
        source[0] = ord("X")
        self.assertEqual(bytes(delivered["field"]), b"efg")

    def test_memoryview_leaf_copied_apart(self):
        backing = bytearray(b"abc")
        source = memoryview(backing)
        delivered = mod05.panel_inputs({"field": source})
        self.assertIsNot(delivered["field"], source)
        self.assertIsInstance(delivered["field"], memoryview)
        self.assertEqual(bytes(delivered["field"]), b"abc")
        backing[0] = ord("X")
        self.assertEqual(bytes(delivered["field"]), b"abc")

    def test_nested_bytearray_leaf_copied_apart(self):
        source = bytearray(b"zz")
        delivered = mod05.panel_inputs({"outer": [{"field": source}]})
        inner = delivered["outer"][0]["field"]
        self.assertIsNot(inner, source)
        source[0] = ord("Y")
        self.assertEqual(bytes(inner), b"zz")

    def test_plain_leaves_control(self):
        delivered = mod05.panel_inputs({"a": "text", "n": 3})
        self.assertEqual(delivered, {"a": "text", "n": 3})


class TestR18049VerifyIntact(unittest.TestCase):
    def test_bool_in_place_of_int_barred(self):
        handover = mod04.ContractAHandover(1, 1, 1, 1)
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(True, 1, 1, 1)

    def test_decimal_in_place_of_int_barred(self):
        handover = mod04.ContractAHandover(1, 1, 1, 1)
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(1, 1, 1, Decimal(1))

    def test_fraction_in_place_of_int_barred(self):
        handover = mod04.ContractAHandover(1, 1, 1, 1)
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(1, 1, Fraction(1, 1), 1)

    def test_nested_bool_barred(self):
        handover = mod04.ContractAHandover(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1")
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(
                {"n": True}, {"a": 1}, {"s": [1]}, "family-1")

    def test_nested_decimal_barred(self):
        handover = mod04.ContractAHandover(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1")
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(
                {"n": Decimal(1)}, {"a": 1}, {"s": [1]}, "family-1")

    def test_nested_fraction_barred(self):
        handover = mod04.ContractAHandover(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1")
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(
                {"n": 1}, {"a": 1}, {"s": [Fraction(1, 1)]},
                "family-1")

    def test_always_equal_object_barred(self):
        handover = mod04.ContractAHandover(
            {"m": AlwaysEqual()}, 1, 1, 1)
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact({"m": AlwaysEqual()}, 1, 1, 1)

    def test_exact_values_control(self):
        handover = mod04.ContractAHandover(1, 1, 1, 1)
        self.assertTrue(handover.verify_intact(1, 1, 1, 1))
        dict_handover = mod04.ContractAHandover(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1")
        self.assertTrue(dict_handover.verify_intact(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1"))

    def test_changed_value_control(self):
        handover = mod04.ContractAHandover(
            {"n": 1}, {"a": 1}, {"s": [1]}, "family-1")
        with self.assertRaises(mod04.AlterationBarred):
            handover.verify_intact(
                {"n": 2}, {"a": 1}, {"s": [1]}, "family-1")

    def test_plain_number_float_control(self):
        handover = mod04.ContractAHandover(1, 1, 1, 1)
        self.assertTrue(handover.verify_intact(1.0, 1, 1, 1))


if __name__ == "__main__":
    unittest.main()

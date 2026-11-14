"""Fix wave 10 pins, Builder 9: the MOD-10 limbs of rows
R10-001, R10-003, R10-006, and R10-007, and row R10-004 whole,
all at crucible/mod10.py under the Round 10 governing stored
text settlement, section 2 of the Round 10 register.

Each defect method fails on the uncured module and passes on
the cured module. Control methods pass both ways.
"""
import unittest

import crucible.mod04 as mod04
import crucible.mod10 as mod10


class NamedKey:
    def __init__(self, reported):
        self._reported = reported

    def __str__(self):
        return self._reported

    __repr__ = __str__


class LieBytes(bytes):
    def __new__(cls, stored, reported):
        instance = bytes.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported

    __repr__ = __str__


class LieStr(str):
    def __new__(cls, stored, reported):
        instance = str.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported


def _view(contents=None):
    base = mod04.build_view_record(
        run_id="run-r11-b9-view", viewer_id="viewer-1", day=5,
        contents=[{"note": "clean", "first_seen_day": 1, "delay": 0}],
        position="pos-1", rule_version_set="rv-1")
    if contents is not None:
        base["view_contents"] = contents
    return base


class B9Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestStoredTextHelper(B9Base):
    def test_defect_bytes_decoded(self):
        self.assertEqual("membership", mod10._stored_text(b"membership"))

    def test_defect_liebytes_stored_bytes_judged(self):
        key = LieBytes(b"membership", "figure")
        self.assertEqual("membership", mod10._stored_text(key))

    def test_defect_bytearray_decoded(self):
        self.assertEqual(
            "membership", mod10._stored_text(bytearray(b"membership")))

    def test_defect_memoryview_decoded(self):
        self.assertEqual(
            "membership", mod10._stored_text(memoryview(b"membership")))

    def test_defect_undecodable_bytes_dropped(self):
        self.assertEqual("canary", mod10._stored_text(b"can\xffary"))

    def test_control_non_text_stores_no_text(self):
        self.assertEqual("", mod10._stored_text(NamedKey("membership")))
        self.assertEqual("", mod10._stored_text(12345))

    def test_control_lie_str_stored_text_judged(self):
        self.assertEqual(
            "membership", mod10._stored_text(LieStr("membership", "x")))
        self.assertEqual(
            "activity", mod10._stored_text(LieStr("activity", "membership")))


class TestR10001AndR10007ViewBytes(B9Base):
    def test_defect_plain_bytes_barred_key(self):
        self.assertTrue(mod10._is_barred_view_key(b"membership"))
        self.assertTrue(mod10._combined_view_key_barred(b"canaryvalue"))

    def test_defect_liebytes_barred_key(self):
        self.assertTrue(
            mod10._is_barred_view_key(LieBytes(b"membership", "figure")))
        self.assertFalse(
            mod10._is_barred_view_key(LieBytes(b"activity", "membership")))

    def test_defect_bytes_key_carried(self):
        self.assertTrue(mod10._carries_barred_key({b"canary": 1}))
        self.assertTrue(
            mod10._carries_barred_key({"outer": [{b"ground_truth": 1}]}))

    def test_defect_memoryview_barred_key(self):
        self.assertTrue(
            mod10._is_barred_view_key(memoryview(b"membership")))
        self.assertTrue(
            mod10._combined_view_key_barred(memoryview(b"canaryvalue")))
        self.assertTrue(
            mod10._carries_barred_key({memoryview(b"canary"): 1}))

    def test_defect_bytearray_inside_container_barred(self):
        self.assertTrue(
            mod10._is_barred_view_key((bytearray(b"membership"),)))

    def test_defect_public_leak_bytes_key_refused(self):
        record = _view(contents=[{b"membership": "x"}])
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("canary", str(caught.exception))

    def test_defect_public_leak_memoryview_key_refused(self):
        record = _view(contents=[{memoryview(b"canary"): "x"}])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_control_plain_bytes_clean_key(self):
        self.assertFalse(mod10._is_barred_view_key(b"activity"))
        self.assertFalse(mod10._carries_barred_key({b"activity": 1}))


class TestR10004AndR10003ViewContainers(B9Base):
    def test_defect_single_part_tuple_carries_part(self):
        self.assertTrue(mod10._is_barred_view_key(("membership",)))
        self.assertTrue(mod10._is_barred_view_key((b"membership",)))
        self.assertTrue(mod10._combined_view_key_barred(("canaryvalue",)))

    def test_defect_split_tuple_joined_barred(self):
        self.assertTrue(mod10._is_barred_view_key(("member", "ship")))
        self.assertTrue(mod10._is_barred_view_key(("ground", "truth")))
        self.assertTrue(mod10._is_barred_view_key(("can", "ary")))

    def test_defect_split_mixed_bytes_joined_barred(self):
        self.assertTrue(mod10._is_barred_view_key(("mem", b"bership")))
        self.assertTrue(mod10._is_barred_view_key((b"member", "ship")))

    def test_defect_split_with_separator_part_barred(self):
        self.assertTrue(mod10._is_barred_view_key(("member", "-", "ship")))

    def test_defect_nested_container_barred(self):
        self.assertTrue(mod10._is_barred_view_key((("canary",),)))
        self.assertTrue(mod10._is_barred_view_key((("ground", "truth"),)))

    def test_defect_list_and_frozenset_forms_barred(self):
        self.assertTrue(mod10._is_barred_view_key(["membership"]))
        self.assertTrue(mod10._is_barred_view_key(frozenset(("membership",))))

    def test_defect_carries_container_key(self):
        self.assertTrue(mod10._carries_barred_key({("member", "ship"): 1}))
        self.assertTrue(
            mod10._carries_barred_key({"outer": [{("ground", "truth"): 1}]}))
        self.assertTrue(
            mod10._carries_barred_key([({"canary": 1},)]))

    def test_defect_public_leak_container_key_refused(self):
        record = _view(contents=[{("member", "ship"): "x"}])
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("canary", str(caught.exception))

    def test_defect_public_leak_top_level_container_field_refused(self):
        record = _view()
        record[("member", "ship")] = "x"
        with self.assertRaises(ValueError) as caught:
            mod10.run_view_leak_check(record)
        self.assertIn("canary", str(caught.exception))

    def test_control_clean_containers_not_barred(self):
        self.assertFalse(mod10._is_barred_view_key(("clean", "value")))
        self.assertFalse(mod10._is_barred_view_key(("acti", "vity")))
        self.assertFalse(mod10._is_barred_view_key(("member",)))
        self.assertFalse(mod10._carries_barred_key({("clean", "value"): 1}))


class TestR10006MoneyForms(B9Base):
    def test_defect_money_key_matches_bytes(self):
        self.assertTrue(mod10._money_key_matches(b"amount", "amount"))
        self.assertTrue(mod10._money_key_matches(b"currency", "currency"))

    def test_defect_money_key_matches_single_part_container(self):
        self.assertTrue(mod10._money_key_matches(("amount",), "amount"))
        self.assertTrue(mod10._money_key_matches((b"amount",), "amount"))

    def test_defect_money_key_matches_split_container(self):
        self.assertTrue(mod10._money_key_matches(("am", "ount"), "amount"))
        self.assertTrue(mod10._money_key_matches(("curr", "ency"), "currency"))

    def test_defect_bytes_pair_carried(self):
        self.assertTrue(mod10._carries_real_money_field(
            {b"amount": 10, b"currency": "USD"}))
        self.assertTrue(mod10._carries_real_money_field(
            {LieBytes(b"amount", "notes"): 10, b"currency": "USD"}))

    def test_defect_single_part_container_pair_carried(self):
        self.assertTrue(mod10._carries_real_money_field(
            {("amount",): 10, ("currency",): "USD"}))

    def test_defect_split_container_pair_carried(self):
        self.assertTrue(mod10._carries_real_money_field(
            {("am", "ount"): 10, ("curr", "ency"): "USD"}))

    def test_defect_memoryview_pair_carried(self):
        self.assertTrue(mod10._carries_real_money_field(
            {memoryview(b"amount"): 10, memoryview(b"currency"): "USD"}))

    def test_defect_bytes_real_money_key_carried(self):
        self.assertTrue(mod10._carries_real_money_field({b"real_money": 5}))
        self.assertTrue(
            mod10._carries_real_money_field({("real_money",): 5}))
        self.assertTrue(
            mod10._carries_real_money_field({("real", "_money"): 5}))

    def test_defect_retention_refuses_bytes_pair(self):
        store = mod10.new_store("sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_identifier": "r11-b9-bytes",
                "payload": {b"amount": 10, b"currency": "USD"}})

    def test_defect_retention_refuses_container_pair(self):
        store = mod10.new_store("sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_identifier": "r11-b9-container",
                "payload": {("am", "ount"): 10, ("currency",): "USD"}})

    def test_control_clean_bytes_and_containers_not_money(self):
        self.assertFalse(mod10._carries_real_money_field(
            {b"notes": 10, b"currency": "USD"}))
        self.assertFalse(mod10._carries_real_money_field(
            {("notes",): 10, ("currency",): "USD"}))
        self.assertFalse(mod10._money_key_matches(b"notes", "amount"))
        self.assertFalse(mod10._money_key_matches(("am",), "amount"))

    def test_control_retention_accepts_clean_record(self):
        store = mod10.new_store("sweep")
        store.retain_run_record({
            "run_identifier": "r11-b9-clean",
            "payload": {b"notes": 10, ("activity",): "x"}})
        self.assertTrue(store.has_run_record("r11-b9-clean"))


if __name__ == "__main__":
    unittest.main()

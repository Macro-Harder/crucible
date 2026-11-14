"""Fix wave 9 pins, Builder 4: row R9-010, MOD-03, MOD-05,
MOD-06, and MOD-08 limbs.

Row R9-010: the _stored_text helpers at those modules fall back
to the plain str call for a non text value, so a non text object
whose string reading reports a barred name stands barred, and a
bytes subclass storing a barred name while its string reading
reports a clean name stands passed. The cured form stands at
MOD-01: a non text value stores no name. Bytes stand judged on
their decoded stored bytes, never on a string reading a bytes
subclass supplies, so plain bytes keep the barred standing they
held and a lying bytes subclass loses its escape.

Each defect method fails on the uncured module and passes on
the cured module. Control methods pass both ways.
"""
import unittest

from crucible import mod03, mod05, mod06, mod08


class NamedKey:
    """A plain non text object carrying no text at all, whose
    string reading returns the name it is given."""

    def __init__(self, reported):
        self._reported = reported

    def __str__(self):
        return self._reported

    __repr__ = __str__


class LieBytes(bytes):
    """A bytes subclass storing one name in its bytes while its
    string reading reports another name."""

    def __new__(cls, stored, reported):
        instance = bytes.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported

    __repr__ = __str__


class LieStr(str):
    """A string subclass storing one text while its string
    reading reports another text."""

    def __new__(cls, stored, reported):
        instance = str.__new__(cls, stored)
        instance._reported = reported
        return instance

    def __str__(self):
        return self._reported


class TestR9010Mod03(unittest.TestCase):

    def test_defect_non_text_reporting_membership_not_barred(self):
        key = NamedKey("membership")
        self.assertEqual("", mod03._stored_text(key))
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod03._combined_key_barred(key))
        self.assertFalse(
            mod03.record_carries_ground_truth({key: 1}))

    def test_defect_non_text_reporting_ground_truth_not_barred(self):
        key = NamedKey("ground_truth")
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(
            mod03.record_carries_ground_truth({"a": {key: 1}}))

    def test_defect_non_text_reporting_canary_not_barred(self):
        self.assertFalse(mod03._is_barred_key(NamedKey("canary")))
        self.assertEqual("", mod03._stored_text(12345))

    def test_defect_liebytes_storing_membership_barred(self):
        key = LieBytes(b"membership", "figure")
        self.assertEqual("membership", mod03._stored_text(key))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod03._combined_key_barred(key))
        self.assertTrue(
            mod03.record_carries_ground_truth({key: 1}))

    def test_defect_liebytes_storing_ground_truth_barred(self):
        key = LieBytes(b"ground_truth", "figure")
        self.assertTrue(mod03._is_barred_key(key))

    def test_defect_liebytes_storing_clean_reported_barred(self):
        key = LieBytes(b"activity", "membership")
        self.assertEqual("activity", mod03._stored_text(key))
        self.assertFalse(mod03._is_barred_key(key))
        self.assertFalse(mod03._combined_key_barred(key))

    def test_control_plain_forms(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertTrue(mod03._is_barred_key(b"membership"))
        self.assertFalse(mod03._is_barred_key("activity"))
        self.assertFalse(mod03._is_barred_key(12345))

    def test_control_str_subclass_stored_name_judged(self):
        self.assertTrue(
            mod03._is_barred_key(LieStr("membership", "activity")))
        self.assertFalse(
            mod03._is_barred_key(LieStr("activity", "membership")))


class TestR9010Mod05(unittest.TestCase):

    def test_defect_non_text_reporting_membership_not_barred(self):
        key = NamedKey("membership")
        self.assertEqual("", mod05._stored_text(key))
        self.assertFalse(mod05._panel_key_barred(key))
        self.assertFalse(mod05._combined_key_barred(key))

    def test_defect_non_text_reporting_ground_truth_not_barred(self):
        key = NamedKey("ground_truth")
        self.assertFalse(mod05._panel_key_barred(key))
        self.assertTrue(mod05.validate_panel_inputs({key: 1}))

    def test_defect_liebytes_storing_ground_truth_barred(self):
        key = LieBytes(b"ground_truth", "figure")
        self.assertEqual("ground_truth", mod05._stored_text(key))
        self.assertTrue(mod05._panel_key_barred(key))
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))

    def test_defect_liebytes_storing_membership_barred(self):
        key = LieBytes(b"membership", "activity")
        self.assertTrue(mod05._panel_key_barred(key))
        self.assertTrue(mod05._combined_key_barred(key))

    def test_defect_liebytes_storing_clean_reported_barred(self):
        key = LieBytes(b"activity", "ground_truth")
        self.assertEqual("activity", mod05._stored_text(key))
        self.assertFalse(mod05._panel_key_barred(key))

    def test_control_plain_forms(self):
        self.assertTrue(mod05._panel_key_barred("membership"))
        self.assertTrue(mod05._panel_key_barred("ground_truth"))
        self.assertTrue(mod05._panel_key_barred(b"membership"))
        self.assertTrue(mod05._panel_key_barred(b"ground_truth"))
        self.assertFalse(mod05._panel_key_barred("activity"))
        self.assertFalse(mod05._panel_key_barred(12345))

    def test_control_str_subclass_stored_name_judged(self):
        self.assertTrue(mod05._panel_key_barred(
            LieStr("membership", "activity")))
        self.assertFalse(mod05._panel_key_barred(
            LieStr("activity", "membership")))


class TestR9010Mod06(unittest.TestCase):

    def test_defect_non_text_reporting_anchor_set_not_barred(self):
        key = NamedKey("anchor_set")
        self.assertEqual("", mod06._stored_text(key))
        self.assertFalse(mod06._payload_carries_barred({key: 1}))
        result = mod06.escrow_result("x", payload={key: 1})
        self.assertEqual("x", result["kind"])

    def test_defect_non_text_amount_currency_pair_not_barred(self):
        payload = {NamedKey("amount"): 10, NamedKey("currency"): "USD"}
        self.assertFalse(mod06._payload_carries_barred(payload))

    def test_defect_non_text_reporting_real_money_not_barred(self):
        payload = {NamedKey("real_money"): 5}
        self.assertFalse(mod06._payload_carries_barred(payload))

    def test_defect_liebytes_storing_anchor_set_barred(self):
        key = LieBytes(b"anchor_set", "notes")
        self.assertEqual("anchor_set", mod06._stored_text(key))
        self.assertTrue(mod06._payload_carries_barred({key: 1}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("x", payload={key: 1})

    def test_defect_liebytes_amount_currency_pair_barred(self):
        payload = {
            LieBytes(b"amount", "notes"): 10,
            LieBytes(b"currency", "notes"): "USD",
        }
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_defect_plain_bytes_amount_currency_pair_barred(self):
        payload = {b"amount": 10, b"currency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_defect_liebytes_storing_clean_reported_barred(self):
        key = LieBytes(b"notes", "anchor_set")
        self.assertEqual("notes", mod06._stored_text(key))
        self.assertFalse(mod06._payload_carries_barred({key: 1}))

    def test_control_plain_forms(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 10, "currency": "USD"}))
        self.assertTrue(mod06._payload_carries_barred(
            {"anchor_set": 1}))
        self.assertFalse(mod06._payload_carries_barred(
            {"notes": 10, "currency": "USD"}))
        self.assertFalse(mod06._payload_carries_barred({"activity": 1}))

    def test_control_str_subclass_stored_name_judged(self):
        payload = {LieStr("amount", "notes"): 10, "currency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        payload = {LieStr("notes", "amount"): 10, "currency": "USD"}
        self.assertFalse(mod06._payload_carries_barred(payload))


class TestR9010Mod08(unittest.TestCase):

    def test_defect_non_text_reporting_membership_not_barred(self):
        key = NamedKey("membership")
        self.assertEqual("", mod08._stored_text(key))
        self.assertFalse(mod08._is_barred_key(key))
        self.assertFalse(mod08._combined_key_barred(key))
        self.assertEqual([], mod08._find_barred({"a": {key: 1}}))

    def test_defect_non_text_reporting_ground_truth_not_barred(self):
        self.assertFalse(
            mod08._is_barred_key(NamedKey("ground_truth")))
        self.assertFalse(mod08._is_barred_key(NamedKey("canary")))

    def test_defect_liebytes_storing_membership_barred(self):
        key = LieBytes(b"membership", "figure")
        self.assertEqual("membership", mod08._stored_text(key))
        self.assertTrue(mod08._is_barred_key(key))
        self.assertTrue(mod08._combined_key_barred(key))

    def test_defect_liebytes_storing_canary_barred(self):
        key = LieBytes(b"canary", "activity")
        self.assertTrue(mod08._is_barred_key(key))
        self.assertTrue(mod08._find_barred({"a": {key: 1}}))

    def test_defect_liebytes_storing_clean_reported_barred(self):
        key = LieBytes(b"activity", "membership")
        self.assertEqual("activity", mod08._stored_text(key))
        self.assertFalse(mod08._is_barred_key(key))

    def test_control_plain_forms(self):
        self.assertTrue(mod08._is_barred_key("membership"))
        self.assertTrue(mod08._is_barred_key("canary"))
        self.assertTrue(mod08._is_barred_key(b"membership"))
        self.assertFalse(mod08._is_barred_key("activity"))
        self.assertFalse(mod08._is_barred_key(12345))

    def test_control_str_subclass_stored_name_judged(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("membership", "activity")))
        self.assertFalse(
            mod08._is_barred_key(LieStr("activity", "membership")))


class TestR9010ContainerKeyControls(unittest.TestCase):
    """Container keys stood barred on the plain str call of the
    container before the cure, and stand barred after it by
    every part standing inside them, at every module. These
    controls pass both ways."""

    def test_control_mod03_container_key(self):
        self.assertTrue(mod03._is_barred_key(("membership", "x")))
        self.assertTrue(
            mod03.record_carries_ground_truth(
                {("membership", "x"): 1}))
        self.assertFalse(mod03._is_barred_key(("activity", "x")))

    def test_control_mod05_container_key(self):
        self.assertTrue(mod05._panel_key_barred(("membership", "x")))
        self.assertFalse(
            mod05.validate_panel_inputs({("membership", "x"): 1}))
        self.assertTrue(
            mod05.validate_panel_inputs({("activity", "x"): 1}))

    def test_control_mod06_container_key(self):
        self.assertTrue(mod06._payload_carries_barred(
            {("anchor_set", "x"): 1}))
        self.assertFalse(mod06._payload_carries_barred(
            {("notes", "x"): 1}))

    def test_control_mod08_container_key(self):
        self.assertTrue(mod08._is_barred_key(("membership", "x")))
        self.assertTrue(
            mod08._find_barred({("membership", "x"): 1}))
        self.assertFalse(mod08._is_barred_key(("activity", "x")))


if __name__ == "__main__":
    unittest.main()

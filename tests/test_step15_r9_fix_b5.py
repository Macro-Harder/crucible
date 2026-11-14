"""Step 15 Round 9 fix pins, Fix Wave 8 Builder 5.

Row R8-007, MOD-05 and MOD-06 limbs: the decomposed character
fold at each module takes its text from the plain str call, so a
string subclass storing a barred name while its string reading
reports another name stands judged as the reported name. The pins
assert the stored text stands judged in both directions at the
MOD-05 panel surface and at the MOD-06 money screen, in the form
row R7-013 cured at the sister surfaces: text taken from the
stored characters through the base class string form.
"""
import unittest

import crucible.mod05 as mod05
import crucible.mod06 as mod06


class LieStr(str):
    """A string storing one text and reporting another."""

    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class Mod05DecomposedTests(unittest.TestCase):

    def test_defect_stored_barred_reported_clean_decomposed(self):
        key = LieStr("membership", "activity")
        self.assertEqual(
            "".join(mod05._decomposed_characters(key)), "membership")
        key = LieStr("activity", "membership")
        self.assertEqual(
            "".join(mod05._decomposed_characters(key)), "activity")

    def test_defect_stored_barred_reported_clean_panel_barred(self):
        self.assertTrue(
            mod05._panel_key_barred(LieStr("membership", "activity")))
        self.assertTrue(
            mod05._panel_key_barred(LieStr("ground_truth", "activity")))
        self.assertFalse(
            mod05._panel_key_barred(LieStr("activity", "membership")))
        self.assertFalse(
            mod05._panel_key_barred(LieStr("activity", "ground_truth")))

    def test_control_plain_panel_forms(self):
        self.assertTrue(mod05._panel_key_barred("membership"))
        self.assertTrue(mod05._panel_key_barred("ground_truth"))
        self.assertFalse(mod05._panel_key_barred("activity"))

    def test_control_agreeing_and_plain_decomposed_forms(self):
        self.assertEqual(
            "".join(mod05._decomposed_characters("Membership")),
            "membership")
        self.assertTrue(mod05._panel_key_barred(
            LieStr("membership", "membership")))
        self.assertFalse(mod05._panel_key_barred(
            LieStr("activity", "activity")))


class Mod06DecomposedTests(unittest.TestCase):

    def test_defect_stored_barred_reported_clean_decomposed(self):
        key = LieStr("amount", "notes")
        self.assertEqual(
            "".join(mod06._decomposed_characters(key)), "amount")
        key = LieStr("notes", "amount")
        self.assertEqual(
            "".join(mod06._decomposed_characters(key)), "notes")

    def test_defect_stored_barred_reported_clean_payload(self):
        payload = {LieStr("amount", "notes"): 10, "currency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        payload = {LieStr("real_money", "notes"): 5}
        self.assertTrue(mod06._payload_carries_barred(payload))
        payload = {LieStr("notes", "amount"): 10, "currency": "USD"}
        self.assertFalse(mod06._payload_carries_barred(payload))
        payload = {LieStr("notes", "real_money"): 5}
        self.assertFalse(mod06._payload_carries_barred(payload))

    def test_control_plain_payload_forms(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 10, "currency": "USD"}))
        self.assertFalse(mod06._payload_carries_barred(
            {"notes": 10, "currency": "USD"}))
        self.assertTrue(mod06._payload_carries_barred(
            {"real_money": 5}))
        self.assertFalse(mod06._payload_carries_barred(
            {"activity": 1}))

    def test_control_agreeing_and_plain_fold_forms(self):
        self.assertIn("amount", mod06._folded_readings("amount"))
        self.assertTrue(mod06._payload_carries_barred(
            {LieStr("amount", "amount"): 10, "currency": "USD"}))
        self.assertFalse(mod06._payload_carries_barred(
            {LieStr("notes", "notes"): 10, "currency": "USD"}))


if __name__ == "__main__":
    unittest.main()

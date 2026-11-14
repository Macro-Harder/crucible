"""Step 15 rerun fix wave 5 pins, MOD-10 money read supplement.

Pins for row R5-041: the mixed leet and drop forms of the money
names, with control pins for the forms that stand detected on
the unmodified tree and for lawful names that stand undetected.
Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10


class B14Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR5041MixedForms(B14Base):
    def test_mixed_amount_key_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"4m0unt9": 5, "currency": "usd"}))

    def test_mixed_marker_leet_then_drop_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"r3almo9ney": 5}))

    def test_mixed_marker_second_form_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"rea1mo9ney": 5}))


class TestMoneyControlsDetected(B14Base):
    def test_plain_pair_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"amount": 5, "currency": "usd"}))

    def test_leet_only_amount_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"4m0unt": 5, "currency": "usd"}))

    def test_drop_only_amount_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"amount9": 5, "currency": "usd"}))

    def test_leet_only_marker_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"r3almoney": 5}))

    def test_drop_only_marker_detected(self):
        self.assertTrue(mod10._carries_real_money_field(
            {"realmo9ney": 5}))


class TestLawfulNamesUndetected(B14Base):
    def test_clean_record_not_detected(self):
        self.assertFalse(mod10._carries_real_money_field(
            {"clean": 5}))

    def test_amount_alone_not_detected(self):
        self.assertFalse(mod10._carries_real_money_field(
            {"amount": 5}))

    def test_currency_alone_not_detected(self):
        self.assertFalse(mod10._carries_real_money_field(
            {"currency": "usd"}))

    def test_plain_pair_refused_at_retention_control(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({
                "run_id": "run-r6-b14-plain",
                "amount": 5, "currency": "usd"})

    def test_clean_record_retained_control(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": "run-r6-b14-clean", "clean": 5})
        back = store.read_run_record("run-r6-b14-clean")
        self.assertEqual(back["clean"], 5)


if __name__ == "__main__":
    unittest.main()

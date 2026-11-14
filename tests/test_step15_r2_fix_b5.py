import unittest

from crucible import mod06


def _deep(depth):
    value = {"ordinary": 1}
    for _ in range(depth):
        value = {"nested": value}
    return value


class TestB5Mod06(unittest.TestCase):
    # R1-024 containment, not startswith, for the money marker
    def test_r1024_prefixed_money_marker_barred(self):
        for payload in (
            {"prefix_real_money_value": 5},
            {"my_real_money": 5},
            {"nested": {"xrealmoneyx": 5}},
        ):
            with self.subTest(payload=payload):
                self.assertTrue(mod06._payload_carries_barred(payload))
                with self.assertRaises(ValueError):
                    mod06.escrow_result("k", payload=payload)

    # R1-025 a money name with a None value is not barred
    def test_r1025_none_valued_money_name_not_barred(self):
        for payload in (
            {"real_money_value": None},
            {"prefix_real_money": None},
            {"nested": {"realmoney": None}},
        ):
            with self.subTest(payload=payload):
                self.assertFalse(mod06._payload_carries_barred(payload))
                result = mod06.escrow_result("k", payload=payload)
                self.assertTrue(mod06.validate_escrow_result(result))

    # R1-039 residual letter classes in the fold
    def test_r1039_special_latin_letters_barred(self):
        self.assertTrue(mod06._payload_carries_barred({"rea\u0142_money": 5}))
        self.assertTrue(mod06._payload_carries_barred({"anchor_se\u0167": ["a"]}))
        self.assertTrue(mod06._payload_carries_barred(
            {"amoun\u0167": 5, "currency": "USD"}))

    def test_r1039_digit_one_read_as_i(self):
        self.assertIn("field", mod06._folded_readings("f1eld"))
        self.assertIn("fleld", mod06._folded_readings("f1eld"))

    def test_r1039_transliterated_cyrillic_barred(self):
        # Cyrillic u, en, te spell the tail of amount only in the
        # transliterated reading.
        self.assertTrue(mod06._payload_carries_barred(
            {"amo\u0443\u043d\u0442": 5, "currency": "USD"}))
        # Cyrillic es transliterates to s in anchor set.
        self.assertTrue(mod06._payload_carries_barred(
            {"anchor_\u0441et": ["a"]}))
        # Cyrillic er transliterates to r at the head of the marker.
        self.assertTrue(mod06._payload_carries_barred(
            {"\u0440eal_money_value": 5}))
        # The transliterated spelling of the marker word itself.
        self.assertTrue(mod06._payload_carries_barred({"realmani_value": 5}))

    # R1-041 folded reading for the excluded profile and instruction name
    def test_r1041_zero_width_dressed_excluded_profile_refused(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup\u200bextended profile")
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup extended\u200bprofile")

    def test_r1041_zero_width_dressed_profile_context_refused(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(
                "deposit", context={"profile": "backup\u200bextended profile"})

    # R1-042 validate_escrow_result checks money, limit, K1 and L2 state
    def test_r1042_forged_results_fail_validation(self):
        genuine = mod06.escrow_result("k", payload={"ordinary": 1})
        self.assertTrue(mod06.validate_escrow_result(genuine))
        forged_money = dict(genuine)
        forged_money["real_money_value"] = 999
        self.assertFalse(mod06.validate_escrow_result(forged_money))
        forged_limit = dict(genuine)
        forged_limit["verification_limit"] = "verified in full"
        self.assertFalse(mod06.validate_escrow_result(forged_limit))
        no_state = dict(genuine)
        del no_state["k1_and_l2_state"]
        self.assertFalse(mod06.validate_escrow_result(no_state))
        empty_state = dict(genuine)
        empty_state["k1_and_l2_state"] = None
        self.assertFalse(mod06.validate_escrow_result(empty_state))

    # R1-044 UnnamedInstruction carries the recorded failure class
    def test_r1044_unnamed_instruction_carries_failure_class(self):
        with self.assertRaises(mod06.UnnamedInstruction) as caught:
            mod06.run_instruction("no_such_instruction_name")
        failure_class = getattr(caught.exception, "failure_class", None)
        self.assertIsNotNone(failure_class)
        self.assertEqual(failure_class, mod06.classify_instruction_refusal())
        self.assertEqual(failure_class["recorded_in"], "run record only")
        self.assertIsNone(failure_class["run_status"])

    # R1-072 depth bound and cycle guard on the barred payload read
    def test_r1072_cyclic_payload(self):
        cyclic = {"ordinary": 1}
        cyclic["self"] = cyclic
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=cyclic)
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = cyclic
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_r1072_deep_payload(self):
        deep = _deep(300)
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=deep)
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = deep
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_r1072_moderate_payload_still_read(self):
        result = mod06.escrow_result("k", payload=_deep(20))
        self.assertTrue(mod06.validate_escrow_result(result))


if __name__ == "__main__":
    unittest.main()

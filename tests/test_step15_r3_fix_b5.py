import unittest

from crucible import mod06


class HidingDict(dict):
    """A dict subclass whose own reading methods hide its stored
    contents: items, keys and iteration all report nothing, while
    the base class storage holds the entries set below."""

    def items(self):
        return iter(())

    def keys(self):
        return iter(())

    def __iter__(self):
        return iter(())

    def __contains__(self, key):
        return False


def hiding(entries):
    instance = HidingDict()
    for key, value in entries.items():
        dict.__setitem__(instance, key, value)
    return instance


class ForgingDict(dict):
    """A dict subclass whose get reports lawful validator field
    values whatever the base class storage holds, and whose items
    report nothing."""

    _FORGED = {
        "core_only_qualifier": True,
        "verification_limit": mod06.VERIFICATION_LIMIT,
        "k1_and_l2_state": "carried; value set open at OP-21 G-10",
        "real_money_value": None,
        "payload": {"ordinary": 1},
    }

    def get(self, key, default=None):
        return self._FORGED.get(key, default)

    def items(self):
        return iter(())

    def keys(self):
        return iter(())

    def __iter__(self):
        return iter(())


def forging(entries):
    instance = ForgingDict()
    for key, value in entries.items():
        dict.__setitem__(instance, key, value)
    return instance


def frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


class TestR2003BaseClassRecordReading(unittest.TestCase):
    def test_payload_screen_reads_stored_real_money_through_base(self):
        payload = hiding({"real_money": 5})
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_payload_screen_reads_stored_amount_currency_pair(self):
        payload = hiding({"amount": 5, "currency": "USD"})
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_payload_screen_reads_stored_anchor_set(self):
        payload = hiding({"anchor_set": ["a"]})
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_payload_screen_reads_nested_hiding_record(self):
        payload = {"nested": hiding({"real_money": 5})}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_validator_reads_stored_fields_through_base(self):
        result = forging({
            "core_only_qualifier": False,
            "verification_limit": "a forged limit statement",
            "k1_and_l2_state": "carried; value set open at OP-21 G-10",
            "real_money_value": 999,
            "payload": {"real_money": 5},
        })
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_validator_reads_stored_payload_through_base(self):
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = hiding({"real_money": 5})
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_clean_hiding_record_still_validates(self):
        payload = hiding({"ordinary": 1})
        self.assertFalse(mod06._payload_carries_barred(payload))
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = hiding({"ordinary": 1})
        self.assertTrue(mod06.validate_escrow_result(result))


class TestR2004PayloadFoldSisterReadings(unittest.TestCase):
    def assert_barred(self, payload):
        self.assertTrue(mod06._payload_carries_barred(payload), payload)
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = payload
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_small_capital_whole_marker(self):
        self.assert_barred(
            {"\u0280\u1d07\u1d00\u029f\u1d0d\u1d0f\u0274\u1d07\u028f": 5})

    def test_small_capital_single_letters(self):
        self.assert_barred({"rea\u029f_money": 5})
        self.assert_barred({"anchor_s\u1d07t": ["a"]})
        self.assert_barred(
            {"amoun\u1d1b": 5, "currency": "USD"})

    def test_symbol_leet_readings(self):
        self.assert_barred({"re@lmoney": 5})
        self.assert_barred({"r\u20acalmoney": 5})
        self.assert_barred({"rea\u00a3money": 5})
        self.assert_barred({"rea!money": 5})
        self.assert_barred({"rea|money": 5})
        self.assert_barred({"real_mone\u00a5": 5})
        self.assert_barred({"anchor_$et": ["a"]})

    def test_armenian_oh_readings(self):
        self.assert_barred({"real_m\u0585ney": 5})
        self.assert_barred({"real_m\u0555ney": 5})

    def test_armenian_vo_readings(self):
        # The vo letters read as n at the sister folds, so the dress
        # stands with vo at the n position of the marker.
        self.assert_barred({"real_mo\u0578ey": 5})
        self.assert_barred({"real_mo\u0548ey": 5})

    def test_armenian_vo_un_reading_in_amount_pair(self):
        self.assert_barred({"amo\u0578t": 5, "currency": "USD"})

    def test_excluded_profile_small_capital_dress(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup extended profi\u029fe")

    def test_excluded_profile_small_capital_dress_in_context(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(
                "deposit",
                context={"profile": "backup extended profi\u029fe"})

    def test_excluded_profile_symbol_and_armenian_dress(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("b@ckup extended profile")
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup extended pr\u0585file")

    def test_clean_keys_still_pass(self):
        self.assertFalse(mod06._payload_carries_barred({"honestscore": 5}))
        result = mod06.escrow_result("k", payload={"honestscore": 5})
        self.assertTrue(mod06.validate_escrow_result(result))


class TestR2028FrozensetBound(unittest.TestCase):
    def test_frozenset_chain_past_bound_reads_barred(self):
        self.assertTrue(mod06._payload_carries_barred(frozenset_chain(150)))

    def test_frozenset_chain_shallow_reads_clean(self):
        self.assertFalse(mod06._payload_carries_barred(frozenset_chain(10)))
        self.assertFalse(mod06._payload_carries_barred(
            {"items": frozenset((1, 2))}))

    def test_escrow_result_refuses_frozenset_chain_in_module_form(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=frozenset_chain(150))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=frozenset_chain(5000))

    def test_escrow_result_refuses_nested_frozenset_chain(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "k", payload={"nested": frozenset_chain(150)})

    def test_validate_refuses_frozenset_chain(self):
        result = mod06.escrow_result("k", payload={"ordinary": 1})
        result["payload"] = frozenset_chain(150)
        self.assertFalse(mod06.validate_escrow_result(result))
        result["payload"] = frozenset_chain(5000)
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_shallow_frozenset_payload_still_accepted(self):
        result = mod06.escrow_result(
            "k", payload={"items": frozenset((1, 2))})
        self.assertTrue(mod06.validate_escrow_result(result))


if __name__ == "__main__":
    unittest.main()

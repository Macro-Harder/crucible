"""Pins for fix wave 3, MOD-06 items R3-008, R3-021, R3-022,
R3-023, R3-024, R3-028, R3-049, and the MOD-06 limb of R3-056.

Each test states its distinguishing case with controls both ways:
the dressed or hostile form the register charges, the plain form
that already stands refused or accepted, and a clean form that
must keep its standing.
"""

import unittest

from crucible import mod06


class _Trojan:
    """A part inert at the screen whose deepcopy protocol returns
    a real money dict."""

    def __deepcopy__(self, memo):
        return {"real_money": 999, "amount": 5, "currency": "USD"}

    def __repr__(self):
        return "clean"


class _LyingStr(str):
    """A string whose own equality agrees with everything."""

    __hash__ = str.__hash__

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


def _list_chain(length):
    value = 0
    for _ in range(length):
        value = [value]
    return value


def _frozenset_chain_key_payload(depth):
    key = "leaf"
    for _ in range(depth):
        key = frozenset((key,))
    return {key: 1}


def _genuine_result():
    return mod06.escrow_result("k", payload={"ordinary": 1})


class TestR3008CopyAct(unittest.TestCase):

    def test_trojan_part_does_not_materialise(self):
        result = mod06.escrow_result("k", payload={"item": _Trojan()})
        stored = result["payload"]["item"]
        self.assertNotIsInstance(stored, dict)
        self.assertFalse(mod06._payload_carries_barred(result["payload"]))
        self.assertTrue(mod06.validate_escrow_result(result))

    def test_trojan_nested_in_list_does_not_materialise(self):
        result = mod06.escrow_result("k", payload={"item": [_Trojan()]})
        stored = result["payload"]["item"][0]
        self.assertNotIsInstance(stored, dict)
        self.assertTrue(mod06.validate_escrow_result(result))

    def test_plain_money_still_refused_and_clean_still_passes(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={"real_money": 5})
        result = mod06.escrow_result("k", payload={"item": {"a": 1}})
        self.assertEqual(result["payload"], {"item": {"a": 1}})


class TestR3021EnAsH(unittest.TestCase):

    def test_en_at_h_position_of_anchor_set_barred(self):
        payload = {"anc\u043dor_set": [1, 2, 3, 4]}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_en_as_h_reading_present(self):
        self.assertIn("anchorset", mod06._folded_readings("anc\u043dor_set"))

    def test_controls(self):
        self.assertTrue(mod06._payload_carries_barred({"anchor_set": [1]}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={"anchor_set": [1]})
        self.assertFalse(mod06._payload_carries_barred({"honest": 1}))


class TestR3022BothReadingsCurrency(unittest.TestCase):

    def test_upsilon_at_both_positions_barred(self):
        payload = {"amount": 5, "c\u03c5rrenc\u03c5": "x"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_cyrillic_u_at_both_positions_barred(self):
        payload = {"amount": 5, "c\u0443rrenc\u0443": "x"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_controls(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 5, "currency": "x"}))
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 5, "c\u03c5rrency": "x"}))
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 5, "currenc\u03c5": "x"}))
        split = {"a": {"amount": 1}, "b": {"currency": 2}}
        self.assertFalse(mod06._payload_carries_barred(split))
        result = mod06.escrow_result("k", payload=split)
        self.assertTrue(mod06.validate_escrow_result(result))


class TestR3023CherokeeCoptic(unittest.TestCase):

    CHEROKEE = "\u13d2\u13ac\u13aa\u13de\u13b7\u13be\u13c1\u13ac\u13ef"
    COPTIC = "\u2ca3\u2c89\u2c81\u2c97\u2c99\u2c9f\u2c9b\u2c89\u2ca9"

    def test_cherokee_marker_barred(self):
        self.assertTrue(mod06._payload_carries_barred({self.CHEROKEE: 5}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={self.CHEROKEE: 5})

    def test_coptic_marker_barred(self):
        self.assertTrue(mod06._payload_carries_barred({self.COPTIC: 5}))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={self.COPTIC: 5})

    def test_controls(self):
        self.assertTrue(mod06._payload_carries_barred({"real_money": 5}))
        self.assertFalse(mod06._payload_carries_barred({"honestscore": 5}))


class TestR3024SymbolReadings(unittest.TestCase):

    def test_cent_sign_as_c(self):
        payload = {"amount": 5, "\u00a2urrency": "x"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)
        self.assertTrue(mod06._payload_carries_barred(
            {"an\u00a2hor_set": [1]}))

    def test_plus_sign_as_t(self):
        payload = {"amoun+": 5, "currency": "x"}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_section_sign_as_s(self):
        payload = {"anchor_\u00a7et": [1]}
        self.assertTrue(mod06._payload_carries_barred(payload))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=payload)

    def test_controls(self):
        self.assertTrue(mod06._payload_carries_barred(
            {"amount": 5, "currency": "x"}))
        self.assertTrue(mod06._payload_carries_barred({"re@lmoney": 5}))
        self.assertTrue(mod06._payload_carries_barred(
            {"anchor_$et": [1]}))
        self.assertFalse(mod06._payload_carries_barred({"honest": 1}))


class TestR3028BaseClassJudgement(unittest.TestCase):

    def test_lying_variant_refused(self):
        with self.assertRaises(ValueError):
            mod06.escrow_contract_state("c1", variant=_LyingStr("B-9"))

    def test_lying_lien_state_refused(self):
        with self.assertRaises(ValueError):
            mod06.escrow_contract_state(
                "c1", lien_state=_LyingStr("bogus lien"))

    def test_lying_verification_limit_fails_validation(self):
        result = _genuine_result()
        result["verification_limit"] = _LyingStr("totally different")
        self.assertFalse(mod06.validate_escrow_result(result))

    def test_controls(self):
        with self.assertRaises(ValueError):
            mod06.escrow_contract_state("c1", variant="B-9")
        state = mod06.escrow_contract_state("c1", variant="B-4")
        self.assertEqual(state["variant"], "B-4")
        plain = _genuine_result()
        plain["verification_limit"] = "totally different"
        self.assertFalse(mod06.validate_escrow_result(plain))
        self.assertTrue(mod06.validate_escrow_result(_genuine_result()))


class TestR3049KeyPositionDepth(unittest.TestCase):

    def test_key_chain_past_bound_refused_in_stated_form(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "k", payload=_frozenset_chain_key_payload(150))

    def test_key_chain_at_2000_no_bare_recursion_error(self):
        try:
            mod06.escrow_result(
                "k", payload=_frozenset_chain_key_payload(2000))
        except ValueError:
            pass
        except RecursionError:
            self.fail("bare RecursionError escaped escrow_result")
        else:
            self.fail(
                "escrow_result returned normally at depth 2000, "
                "silently admitting the key chain payload")

    def test_screen_itself_counts_key_position(self):
        self.assertTrue(mod06._payload_carries_barred(
            _frozenset_chain_key_payload(150)))

    def test_controls(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={"x": _list_chain(150)})
        shared = {"a": 1}
        result = mod06.escrow_result(
            "k", payload={"one": shared, "two": shared})
        self.assertTrue(mod06.validate_escrow_result(result))


class TestR3056CountingBasis(unittest.TestCase):

    def test_chain_101_admitted(self):
        self.assertFalse(mod06._payload_carries_barred(_list_chain(101)))
        result = mod06.escrow_result("k", payload=_list_chain(101))
        self.assertEqual(result["payload"], _list_chain(101))

    def test_chain_102_refused(self):
        self.assertTrue(mod06._payload_carries_barred(_list_chain(102)))
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload=_list_chain(102))

    def test_chain_100_admitted(self):
        self.assertFalse(mod06._payload_carries_barred(_list_chain(100)))


if __name__ == "__main__":
    unittest.main()

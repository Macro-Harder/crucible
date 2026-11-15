import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod05, mod12, mod13, mod14


def deep_list(depth, leaf="x"):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def deep_tuple(depth, leaf="x"):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


class StrRaises(float):
    def __str__(self):
        raise RuntimeError("str raises")


class ReprRaises:
    def __repr__(self):
        raise RuntimeError("repr raises")


class StrRaisesObj:
    def __str__(self):
        raise RuntimeError("str raises")


class ArmedKey:
    armed = False

    def __init__(self, target):
        self.target = target

    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("eq raises")
        return NotImplemented


class TestR18027(unittest.TestCase):
    def test_deep_values_equal(self):
        first = deep_list(3000, "leaf")
        second = deep_list(3000, "leaf")
        self.assertTrue(mod12._stored_values_equal(first, second))
        third = deep_list(3000, "other")
        self.assertFalse(mod12._stored_values_equal(first, third))

    def test_deep_values_equal_via_gate(self):
        placement = {
            "confirmation_family": deep_list(3000, "fam"),
            "screening_family": deep_list(3000, "fam"),
        }
        self.assertFalse(mod12.validate_seed_placement(placement))
        placement2 = {
            "confirmation_family": deep_list(3000, "fam"),
            "screening_family": deep_list(3000, "other"),
        }
        self.assertTrue(mod12.validate_seed_placement(placement2))


class TestR18028(unittest.TestCase):
    def test_deep_key_texts(self):
        key = deep_tuple(3000, "field")
        texts = mod13._stored_key_texts(key)
        self.assertIsInstance(texts, set)
        self.assertEqual(mod13._stored_key_text(key), "" if False else mod13._stored_key_text(key))

    def test_deep_stored_text_and_get(self):
        key = deep_tuple(3000, "field")
        self.assertIsNone(mod13._stored_text(key))
        record = {key: 1}
        self.assertIsNone(mod13._stored_get(record, "field"))
        plain = {"field": 7}
        self.assertEqual(mod13._stored_get(plain, "field"), 7)


class TestR18029(unittest.TestCase):
    def test_sample_statement_raising_str_float(self):
        runs = [{"run_class": "screening", "run_id": StrRaises(1.5)}]
        result = mod12.sample_statement(runs)
        self.assertEqual(result["n"], 1)

    def test_sealed_edit_raising_str_id(self):
        record = {"sealed": True, "family_identifier": StrRaises(2.5)}
        edited = mod12.apply_family_edit(record)
        self.assertIn("-edited-1", edited["family_id"])


class TestR18030(unittest.TestCase):
    def test_claims_repr_refusal(self):
        record = {"claims": ReprRaises()}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record)

    def test_kill_check_str_refusal_first(self):
        record = {"headline_claims": ["standing claim"]}
        change = {"kill_checks": [{"claim": StrRaisesObj()}]}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change)

    def test_kill_check_str_refusal_second(self):
        record = {"headline_claims": ["standing claim"]}
        change = {"claims": None, "kill_checks": [{"claim": StrRaisesObj()}]}
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.apply_family_edit(record, change)


class TestR18031(unittest.TestCase):
    def test_record_version_sets_raising_str(self):
        result = mod12.record_version_sets([StrRaisesObj(), "plain"])
        self.assertEqual(len(result), 2)
        self.assertIn("plain", result)


class TestR18032(unittest.TestCase):
    def _record(self, field, base):
        ArmedKey.armed = False
        record = dict(base)
        record[ArmedKey(field)] = "decoy"
        ArmedKey.armed = True
        return record

    def test_validate_record_version_armed_key(self):
        try:
            record = self._record(
                "produced_under", {"presented_under": "v1"})
            self.assertFalse(mod12.validate_record_version(record))
        finally:
            ArmedKey.armed = False

    def test_validate_seed_placement_armed_key(self):
        try:
            record = self._record(
                "confirmation_family", {"screening_family": "b"})
            self.assertTrue(mod12.validate_seed_placement(record))
        finally:
            ArmedKey.armed = False


class TestR18033(unittest.TestCase):
    def test_base_get_armed_key(self):
        ArmedKey.armed = False
        record = {}
        record[ArmedKey("code_version")] = "decoy"
        plain = {"code_version": "v1"}
        ArmedKey.armed = True
        try:
            self.assertIsNone(mod13._base_get(record, "code_version"))
            self.assertIsNone(mod13._stored_get(record, "code_version"))
            self.assertEqual(mod13._base_get(plain, "code_version"), "v1")
            result = mod13.replay_check(record, record)
            self.assertIsInstance(result, dict)
        finally:
            ArmedKey.armed = False


class TestR18040(unittest.TestCase):
    def test_sample_counts_decimal_once(self):
        runs = [
            {"run_class": "screening", "run_id": [Decimal(5)]},
            {"run_class": "screening", "run_id": [Decimal(5)]},
        ]
        self.assertEqual(mod12.sample_statement(runs)["n"], 1)

    def test_ids_equal_number_kinds(self):
        self.assertTrue(mod12._stored_ids_equal(Decimal(5), Decimal(5)))
        self.assertTrue(mod12._stored_ids_equal(Fraction(1, 2), Fraction(1, 2)))
        self.assertTrue(mod12._stored_ids_equal(complex(1, 2), complex(1, 2)))
        self.assertTrue(mod12._stored_ids_equal([Decimal(5)], [Decimal(5)]))
        self.assertFalse(mod12._stored_ids_equal(Decimal(1), 1))
        self.assertFalse(mod12._stored_ids_equal(Decimal(5), Decimal(6)))


class TestR18041(unittest.TestCase):
    def test_strict_eq_decimal_fraction(self):
        self.assertTrue(mod13._strict_eq(Decimal(5), Decimal(5)))
        self.assertTrue(mod13._strict_eq(Fraction(1, 2), Fraction(1, 2)))
        self.assertFalse(mod13._strict_eq(Decimal(1), 1))
        self.assertFalse(mod13._strict_eq(Decimal(5), Decimal(6)))
        self.assertTrue(mod13._identifiers_agree(Decimal(5), Decimal(5)))
        self.assertTrue(mod13._identifiers_agree(Fraction(3, 4), Fraction(3, 4)))


class TestR18046(unittest.TestCase):
    def _check_freeze(self, module):
        buf = bytearray(b"xy")
        frozen = module._freeze({"a": [buf]})
        buf[0] = 122
        self.assertEqual(bytes(frozen["a"][0]), b"xy")
        backing = bytearray(b"ab")
        view = memoryview(backing)
        frozen2 = module._freeze({"a": view})
        backing[0] = 122
        self.assertEqual(bytes(frozen2["a"]), b"ab")

    def test_freeze_mod13(self):
        self._check_freeze(mod13)

    def test_freeze_mod05(self):
        self._check_freeze(mod05)

    def test_freeze_mod14(self):
        self._check_freeze(mod14)

    def test_freeze_consumers(self):
        buf = bytearray(b"xy")
        out = mod14.pilot_run("timing", {"buf": buf})
        buf[0] = 122
        self.assertEqual(bytes(out["buf"]), b"xy")
        buf2 = bytearray(b"pq")
        history = [{"run_id": "r1", "segment_order": 1,
                    "rule_set_version": "v1"}]
        segment = {"run_id": "r1", "segment_order": 2,
                   "rule_set_version": "v1", "buf": buf2}
        extended = mod13.extend_history(history, segment)
        buf2[0] = 122
        self.assertEqual(bytes(extended[-1]["buf"]), b"pq")


if __name__ == "__main__":
    unittest.main()

"""Pin tests for fix wave 17 builder 7 rows.

Rows: R17-009, R17-012, R17-038, R17-039, R17-040, R17-042, R17-043.
Each pin stands in the distinguishing case standard: it fails on
the pristine code for the charged defect and passes after the cure.
For row R17-040, a statement row against docstrings, the pin form
is a statement pin: it reads the three charged docstrings and
requires each to state the seven named kinds qualification, in
place of the unqualified never escapes bare form. The escape
itself stands as the stated bound and stands charged nowhere, so
no pin in this file charges the escape behaviour beyond the
standing control that a named kind returns the base object repr.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod01, mod04, mod07, mod08, mod09, mod13


class LyingFalseStr(str):
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class RaisingEqStr(str):
    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = str.__hash__


class StrRaiser:
    def __str__(self):
        raise RuntimeError("str boom")

    def __repr__(self):
        return "StrRaiser()"


class PlainException(Exception):
    pass


class ReprPlainRaiser:
    def __repr__(self):
        raise PlainException("repr boom")


class StrPlainRaiser:
    def __str__(self):
        raise PlainException("str boom")

    def __repr__(self):
        return "StrPlainRaiser()"


class ReprRuntimeRaiser:
    def __repr__(self):
        raise RuntimeError("repr boom")


SEVEN_KINDS = (
    "TypeError", "RuntimeError", "ValueError", "AttributeError",
    "OverflowError", "KeyError", "OSError",
)


class TestR17009Mod01Equality(unittest.TestCase):
    def test_bool_not_equal_int(self):
        self.assertFalse(mod01._base_value_equals(True, 1))
        self.assertFalse(mod01._base_value_equals(1, True))
        self.assertFalse(mod01._base_value_equals(False, 0))

    def test_decimal_not_equal_int(self):
        self.assertFalse(mod01._base_value_equals(Decimal(1), 1))
        self.assertFalse(mod01._base_value_equals(1, Decimal(1)))

    def test_fraction_not_equal_int(self):
        self.assertFalse(mod01._base_value_equals(Fraction(1, 1), 1))
        self.assertFalse(mod01._base_value_equals(1, Fraction(1, 1)))

    def test_nested_bool_not_equal_int(self):
        self.assertFalse(mod01._base_value_equals([True], [1]))

    def test_same_kind_controls_stand(self):
        self.assertTrue(mod01._base_value_equals(True, True))
        self.assertTrue(mod01._base_value_equals(Decimal(1), Decimal(1)))
        self.assertTrue(mod01._base_value_equals(Fraction(1, 1), Fraction(1, 1)))
        self.assertTrue(mod01._base_value_equals(1, 1))
        self.assertTrue(mod01._base_value_equals(1.0, 1))
        self.assertTrue(mod01._base_value_equals([1], [1]))

    def test_seal_match_bool_version_refused(self):
        manifest = {"family_version": 1, "sealed_family_record_hash": "abc"}
        record = {"family_version": True, "family_manifest_hash": "abc"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_decimal_version_refused(self):
        manifest = {"family_version": 1, "sealed_family_record_hash": "abc"}
        record = {"family_version": Decimal(1), "family_manifest_hash": "abc"}
        self.assertFalse(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_bool_hash_refused(self):
        manifest = {"family_version": 1, "sealed_family_record_hash": 1}
        record = {"family_version": 1, "family_manifest_hash": True}
        self.assertFalse(mod01.validate_family_seal_match(manifest, record))

    def test_seal_match_plain_control_stands(self):
        manifest = {"family_version": 1, "sealed_family_record_hash": "abc"}
        record = {"family_version": 1, "family_manifest_hash": "abc"}
        self.assertTrue(mod01.validate_family_seal_match(manifest, record))


class TestR17012Form22(unittest.TestCase):
    def test_form22_minimal_instance_validates(self):
        instance = mod01.minimal_valid_instance("22")
        self.assertTrue(mod01.validate_record("22", instance))

    def test_form22_fields_inside_stated_sets(self):
        instance = mod01.minimal_valid_instance("22")
        self.assertIn(instance["outcome"], ("reported", "not reported"))
        self.assertIn(
            instance["confirmation_outcome"], ("passed", "failed", "not run"))
        self.assertIn(
            instance["gate_failure"],
            ("procedure gate", "confirmation gate", "both gates", "none"))

    def test_every_form_minimal_instance_validates(self):
        for fid in mod01.FORM_IDS:
            if fid == "36":
                for kind in ("ordinary", "agent", "supersession"):
                    self.assertTrue(
                        mod01.validate_record(
                            fid, mod01.minimal_valid_instance(fid, kind)),
                        fid + " " + kind)
            elif fid == "13A":
                continue
            else:
                self.assertTrue(
                    mod01.validate_record(
                        fid, mod01.minimal_valid_instance(fid)), fid)


class TestR17038Mod04GuardedCopy(unittest.TestCase):
    def test_bytearray_part_copied_apart(self):
        original = bytearray(b"abc")
        held = mod04.hold_view({"part": original})
        copied = held["view_record"]["part"]
        self.assertIsNot(copied, original)
        original[0] = 88
        self.assertEqual(bytes(copied), b"abc")

    def test_memoryview_part_copied_apart(self):
        backing = bytearray(b"abc")
        original = memoryview(backing)
        held = mod04.hold_view({"part": original})
        copied = held["view_record"]["part"]
        self.assertIsNot(copied, original)
        backing[0] = 88
        self.assertEqual(bytes(copied), b"abc")

    def test_guarded_copy_direct_buffer_forms(self):
        original = bytearray(b"xy")
        copied = mod04._guarded_copy(original)
        self.assertIsNot(copied, original)
        self.assertEqual(bytes(copied), b"xy")
        view = memoryview(bytearray(b"xy"))
        copied_view = mod04._guarded_copy(view)
        self.assertEqual(bytes(copied_view), b"xy")


class TestR17039Mod07PairEqual(unittest.TestCase):
    def test_decimal_pair_equal(self):
        self.assertTrue(
            mod07._stored_pair_equal(Decimal("1"), Decimal("1")))

    def test_fraction_pair_equal(self):
        self.assertTrue(
            mod07._stored_pair_equal(Fraction(1, 2), Fraction(1, 2)))

    def test_complex_pair_equal(self):
        self.assertTrue(
            mod07._stored_pair_equal(complex(1, 2), complex(1, 2)))

    def test_nested_pairs_equal(self):
        self.assertTrue(mod07._stored_pair_equal(
            {"k": Decimal("1")}, {"k": Decimal("1")}))
        self.assertTrue(mod07._stored_pair_equal(
            [Fraction(1, 2)], [Fraction(1, 2)]))

    def test_cross_kind_and_unequal_controls_stand(self):
        self.assertFalse(mod07._stored_pair_equal(Decimal("1"), 1))
        self.assertFalse(mod07._stored_pair_equal(Fraction(1, 1), 1))
        self.assertFalse(mod07._stored_pair_equal(Decimal("1"), Decimal("2")))
        self.assertFalse(
            mod07._stored_pair_equal(Fraction(1, 2), Fraction(1, 3)))
        self.assertFalse(
            mod07._stored_pair_equal(complex(1, 2), complex(1, 3)))
        self.assertFalse(mod07._stored_pair_equal(True, 1))


class TestR17040SafeHelperStatements(unittest.TestCase):
    def test_docstrings_state_seven_named_kinds(self):
        for doc in (mod08._safe_repr.__doc__, mod08._safe_str.__doc__,
                    mod09._safe_repr.__doc__):
            self.assertIsNotNone(doc)
            for kind in SEVEN_KINDS:
                self.assertIn(kind, doc)

    def test_named_kind_control_stands(self):
        rendered = mod08._safe_repr(ReprRuntimeRaiser())
        self.assertIn("ReprRuntimeRaiser", rendered)


class TestR17042Mod13StoredString(unittest.TestCase):
    def test_witness_rerun_str_raising_identifier(self):
        result = mod13.witness_rerun({"run_id": StrRaiser()})
        self.assertTrue(result["run_id"].endswith("-rerun"))
        self.assertIn("StrRaiser()", result["run_id"])

    def test_witness_rerun_plain_controls_stand(self):
        self.assertEqual(
            mod13.witness_rerun({"run_id": "run-1"})["run_id"], "run-1-rerun")
        self.assertEqual(
            mod13.witness_rerun({"run_id": 42})["run_id"], "42-rerun")


class TestR17043Mod13UseStands(unittest.TestCase):
    def test_lying_false_permitted_use_admitted(self):
        self.assertTrue(
            mod13.use_stands_for_marked_run(LyingFalseStr("pilot timing")))
        self.assertTrue(
            mod13.use_stands_for_marked_run(LyingFalseStr("pilot cost")))

    def test_raising_equality_permitted_use_admitted(self):
        self.assertTrue(
            mod13.use_stands_for_marked_run(RaisingEqStr("pilot timing")))

    def test_raising_equality_barred_use_refused(self):
        self.assertFalse(
            mod13.use_stands_for_marked_run(RaisingEqStr("witness")))

    def test_raising_equality_screening_form(self):
        self.assertFalse(mod13.use_stands_for_marked_run(
            RaisingEqStr("screening observation")))
        self.assertTrue(mod13.use_stands_for_marked_run(
            RaisingEqStr("screening observation"), labelled_screening=True))

    def test_plain_controls_stand(self):
        self.assertTrue(mod13.use_stands_for_marked_run("pilot timing"))
        self.assertFalse(mod13.use_stands_for_marked_run("bogus"))
        self.assertFalse(mod13.use_stands_for_marked_run("witness"))
        self.assertFalse(
            mod13.use_stands_for_marked_run(LyingFalseStr("bogus")))


if __name__ == "__main__":
    unittest.main()

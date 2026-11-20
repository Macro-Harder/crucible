"""Step 17 fix wave 5, Builder 2 (Slice 2) tests.

Rows: FW5-05, FW5-06, FW5-12, all at crucible.mod05.
Each defect test reproduces its filing defect on the uncured tree
at product head e86d02fcde5a99f0795fdc12fdffd342e641e1b7 and
passes on the cured tree. Control tests pass on both trees.
Standard library only.
"""
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod05


def _cyclic_list():
    cyc = []
    cyc.append(cyc)
    return cyc


def _cyclic_dict():
    cyc = {}
    cyc["self"] = cyc
    return cyc


def _deep_list(levels):
    value = 1
    for _ in range(levels):
        value = [value]
    return value


def _good_shares():
    return {1: mod05.gate_passing_share(10, 5, epoch=1)}


class TestFW505RecomputeShareForm(unittest.TestCase):
    """FW5-05 (Medium, T17R4-05): recompute_share escapes in bare
    interpreter text on a handing in no mapping form."""

    def _assert_named_refusal(self, logged, recomputed):
        with self.assertRaises(ValueError) as caught:
            mod05.recompute_share(logged, recomputed)
        text = str(caught.exception)
        self.assertIn("recompute_share stands refused", text)
        self.assertIn("no mapping form", text)
        self.assertIn("no share stands returned", text)

    def test_defect_list_handing_refused_named_form(self):
        self._assert_named_refusal([1, 2], [1, 2])

    def test_defect_text_handing_refused_named_form(self):
        self._assert_named_refusal("junk", "junk")

    def test_defect_int_handing_refused_named_form(self):
        self._assert_named_refusal(7, 7)

    def test_defect_none_handing_refused_named_form(self):
        self._assert_named_refusal(None, None)

    def test_defect_cyclic_list_handing_refused_named_form(self):
        self._assert_named_refusal(_cyclic_list(), _cyclic_list())

    def test_defect_second_arg_non_mapping_refused_named_form(self):
        self._assert_named_refusal(_good_shares(), [1, 2])

    def test_control_equal_mappings_divergence_zero(self):
        good = _good_shares()
        result = mod05.recompute_share(good, dict(good))
        self.assertEqual(result["divergence_count"], 0)

    def test_control_differing_mappings_divergence_counted(self):
        logged = _good_shares()
        other = {1: mod05.gate_passing_share(10, 3, epoch=1)}
        result = mod05.recompute_share(logged, other)
        self.assertEqual(result["divergence_count"], 1)


class TestFW506GateEpochForm(unittest.TestCase):
    """FW5-06 (Medium, T17R4-06): gate_passing_share serves a
    cyclic epoch whole and stores the handed epoch by identity."""

    def test_defect_cyclic_list_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(10, 5, epoch=_cyclic_list())
        text = str(caught.exception)
        self.assertIn("gate_passing_share stands refused", text)
        self.assertIn("cyclic", text)
        self.assertIn("no share stands returned", text)

    def test_defect_cyclic_dict_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(10, 5, epoch=_cyclic_dict())
        self.assertIn("cyclic", str(caught.exception))

    def test_defect_deep_200_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(10, 5, epoch=_deep_list(200))
        text = str(caught.exception)
        self.assertIn("gate_passing_share stands refused", text)
        self.assertIn("deeper than the retention bound of 100", text)
        self.assertIn("no share stands returned", text)

    def test_defect_deep_2000_epoch_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(
                ["a", "b"], ["a"], epoch=_deep_list(2000))
        self.assertIn(
            "deeper than the retention bound of 100",
            str(caught.exception))

    def test_defect_epoch_stored_by_value_not_identity(self):
        epoch = {"day": 1, "tags": ["x"]}
        share = mod05.gate_passing_share(10, 5, epoch=epoch)
        epoch["day"] = 999
        epoch["tags"].append("y")
        self.assertEqual(share["epoch"], {"day": 1, "tags": ["x"]})
        self.assertTrue(mod05.validate_logged_share(share))

    def test_defect_wrappers_cyclic_epoch_refused_named_form(self):
        with self.assertRaises(ValueError):
            mod05.compute_share(10, 5, epoch=_cyclic_list())
        with self.assertRaises(ValueError):
            mod05.share_for_epoch(
                _cyclic_list(), eligible=10, passing=5)

    def test_control_plain_epoch_served(self):
        share = mod05.gate_passing_share(10, 5, epoch=1)
        self.assertEqual(share["numerator"], 5)
        self.assertEqual(share["denominator"], 10)
        self.assertEqual(share["epoch"], 1)
        self.assertTrue(mod05.validate_logged_share(share))

    def test_control_dict_epoch_served_and_valid(self):
        share = mod05.gate_passing_share(10, 5, epoch={"day": 1})
        self.assertEqual(share["epoch"], {"day": 1})
        self.assertTrue(mod05.validate_logged_share(share))

    def test_control_nested_epoch_within_bound_served(self):
        epoch = _deep_list(50)
        share = mod05.gate_passing_share(10, 5, epoch=epoch)
        self.assertEqual(share["epoch"], epoch)

    def test_control_text_epoch_served(self):
        share = mod05.gate_passing_share(4, 2, epoch="epoch-1")
        self.assertEqual(share["epoch"], "epoch-1")


class TestFW512GateNeitherForm(unittest.TestCase):
    """FW5-12 (Low, T17R4-12): gate_passing_share returns the
    unknown share in silence on a handing in neither stated form.
    The two stated forms stand as the count form, two plain
    counts, and the identity form, two containers of identities."""

    def _assert_named_refusal(self, eligible, passing):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(eligible, passing)
        text = str(caught.exception)
        self.assertIn("gate_passing_share stands refused", text)
        self.assertIn("neither stated form", text)
        self.assertIn("no share stands returned", text)

    def test_defect_bool_pair_refused_named_form(self):
        self._assert_named_refusal(True, True)

    def test_defect_float_pair_refused_named_form(self):
        self._assert_named_refusal(2.0, 1.0)

    def test_defect_decimal_pair_refused_named_form(self):
        self._assert_named_refusal(Decimal(2), Decimal(1))

    def test_defect_fraction_pair_refused_named_form(self):
        self._assert_named_refusal(Fraction(2), Fraction(1))

    def test_defect_text_pair_refused_named_form(self):
        self._assert_named_refusal("ab", "a")

    def test_defect_none_pair_refused_named_form(self):
        self._assert_named_refusal(None, None)

    def test_defect_wrappers_neither_form_refused_named_form(self):
        with self.assertRaises(ValueError) as caught:
            mod05.compute_share(True, True)
        self.assertIn("neither stated form", str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            mod05.compute_share(None, None)
        self.assertIn("neither stated form", str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            mod05.share_for_epoch("e1", eligible=True, passing=True)
        self.assertIn("neither stated form", str(caught.exception))

    def test_defect_container_text_pair_refused_named_form(self):
        self._assert_named_refusal(["a"], "a")

    def test_control_count_form_served(self):
        share = mod05.gate_passing_share(4, 2)
        self.assertEqual(share["numerator"], 2)
        self.assertEqual(share["denominator"], 4)

    def test_control_identity_form_served(self):
        share = mod05.gate_passing_share(["a", "b"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_control_zero_eligible_count_unknown(self):
        self.assertEqual(mod05.gate_passing_share(0, 0), "unknown")
        self.assertEqual(mod05.gate_passing_share(0, 5), "unknown")

    def test_control_empty_identity_unknown(self):
        self.assertEqual(
            mod05.gate_passing_share([], []), mod05.UNKNOWN_SHARE)

    def test_control_mixed_count_container_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.compute_share(5, ["a", "b", "c"])
        self.assertIn(
            "gate_passing_share stands refused", str(caught.exception))

    def test_control_passing_above_eligible_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share(3, 4)
        self.assertIn(
            "gate_passing_share stands refused", str(caught.exception))

    def test_control_unhashable_member_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod05.gate_passing_share([["x"]], [["x"]])
        self.assertIn(
            "gate_passing_share stands refused", str(caught.exception))

    def test_control_share_for_epoch_undelivered_unknown(self):
        self.assertEqual(mod05.share_for_epoch("e1"), "unknown")


if __name__ == "__main__":
    unittest.main()

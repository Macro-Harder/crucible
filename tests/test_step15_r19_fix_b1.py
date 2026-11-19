"""Pins for fix wave 18, Builder 1, Group 1.

Rows R18-002, R18-003, R18-004, R18-026, R18-050, R18-051,
R18-052, R18-053, and R18-054. Distinguishing pins fail or
error on the pristine code for their charged defect; controls
hold on the pristine code and on the cured code alike.
"""
import time
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod01
from crucible import mod11
from crucible import mod12
from crucible import mod13


class LieStr(str):
    """A str subclass storing its text, whose equality reading
    answers True against every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class FalseStr(str):
    """A str subclass storing its text, whose equality reading
    answers False against every value."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class RaisingEqStr(str):
    """A str subclass whose equality reading raises."""

    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("eq boom")

    __hash__ = str.__hash__


class LieCmp(float):
    """A float subclass whose comparison readings answer True."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __lt__(self, other):
        return True


class RaisingCmp:
    """An object whose comparison readings raise."""

    def __le__(self, other):
        raise RuntimeError("cmp boom")

    def __ge__(self, other):
        raise RuntimeError("cmp boom")

    def __lt__(self, other):
        raise RuntimeError("cmp boom")

    def __gt__(self, other):
        raise RuntimeError("cmp boom")

    def __eq__(self, other):
        raise RuntimeError("cmp boom")


class RaisingBool:
    """An object whose truth reading raises."""

    def __bool__(self):
        raise RuntimeError("bool boom")


def paired_levels(level):
    base = frozenset("abcdef")
    key = base
    for _ in range(level):
        key = (key, key)
    return key


class TestR18002RegistryEnumeration(unittest.TestCase):
    """Row R18-002: a part standing twice in one key stands
    read once, at every sister reading charged inside the row."""

    def test_mod11_shared_part_read_once(self):
        key = paired_levels(8)
        start = time.perf_counter()
        texts = mod11._registry_key_texts(key)
        elapsed = time.perf_counter() - start
        self.assertEqual(len(texts), 1)
        self.assertLess(elapsed, 0.5)

    def test_mod12_shared_part_read_once(self):
        key = paired_levels(8)
        start = time.perf_counter()
        texts = mod12._key_stored_texts(key)
        elapsed = time.perf_counter() - start
        self.assertEqual(len(texts), 1)
        self.assertLess(elapsed, 0.5)

    def test_mod13_shared_part_read_once(self):
        key = paired_levels(8)
        start = time.perf_counter()
        texts = mod13._stored_key_texts(key)
        elapsed = time.perf_counter() - start
        self.assertEqual(len(texts), 1)
        self.assertLess(elapsed, 0.5)

    def test_mod01_shared_part_read_once(self):
        key = paired_levels(8)
        start = time.perf_counter()
        texts = mod01._joined_text_candidates(key)
        elapsed = time.perf_counter() - start
        self.assertEqual(len(texts), 1)
        self.assertLess(elapsed, 0.5)

    def test_small_key_texts_control(self):
        self.assertEqual(
            mod11._registry_key_texts(("ab", "cd")), {"abcd"})
        self.assertIn(
            "abcd", mod11._registry_key_texts(frozenset(("ab", "cd"))))
        self.assertEqual(
            mod12._key_stored_texts(("ab", "cd")), {"abcd"})
        self.assertEqual(
            mod13._stored_key_texts(("ab", "cd")), {"abcd"})
        self.assertIn("abcd", mod01._joined_text_candidates(("ab", "cd")))

    def test_fallback_constructions_control(self):
        nine = frozenset("abcdefghi")
        self.assertEqual(len(mod11._registry_key_texts(nine)), 1)
        base = frozenset("abcdef")
        self.assertEqual(
            len(mod11._registry_key_texts((base, base))), 1)


class TestR18003ClaimEntersFamily(unittest.TestCase):

    def family(self):
        return {"headline_claims": ["claim-a"]}

    def test_lying_claim_does_not_enter(self):
        self.assertFalse(mod11.claim_enters_family(
            self.family(), LieStr("claim-b"), False))

    def test_controls(self):
        self.assertTrue(mod11.claim_enters_family(
            self.family(), "claim-a", False))
        self.assertFalse(mod11.claim_enters_family(
            self.family(), "claim-b", False))
        self.assertFalse(mod11.claim_enters_family(
            self.family(), "claim-a", True))


class TestR18004RetirementFixture(unittest.TestCase):

    def test_lying_bogus_fixture_refused(self):
        with self.assertRaises(ValueError):
            mod11.retirement_verdicts(LieStr("bogus"))

    def test_lying_f02_tally_carries_no_f01_breach(self):
        tally = mod11.retirement_tally(LieStr("F-02"))
        self.assertEqual(tally["passed"], 8)
        self.assertEqual(tally["failed"], 2)
        self.assertNotIn("centre_quarantine_breach", tally)

    def test_stored_text_fixture_judged_on_its_text(self):
        verdicts = mod11.retirement_verdicts(FalseStr("F-01"))
        self.assertEqual(verdicts, mod11.retirement_verdicts("F-01"))
        verdicts = mod11.retirement_verdicts(RaisingEqStr("F-01"))
        self.assertEqual(verdicts, mod11.retirement_verdicts("F-01"))

    def test_controls(self):
        tally = mod11.retirement_tally("F-01")
        self.assertEqual(
            (tally["passed"], tally["failed"],
             tally["not_applicable"], tally["total"]), (3, 9, 3, 15))
        self.assertTrue(tally["centre_quarantine_breach"])
        with self.assertRaises(ValueError):
            mod11.retirement_verdicts("bogus")


class TestR18026CompoundBarredPlural(unittest.TestCase):

    def test_compound_s_plurals_refused(self):
        for word in ("dogchilds", "dogwomans", "dogfoots",
                     "dogleafs", "dogsheeps", "dogmouses",
                     "dogdatas", "dogwifes", "doghalfs",
                     "dogshelfs", "doglifes", "dogmans"):
            self.assertFalse(mod11._is_readable_word(word), word)

    def test_compound_es_plurals_refused(self):
        for word in ("dogtoothes", "paintoothes", "dogchildes",
                     "dogsheepes"):
            self.assertFalse(mod11._is_readable_word(word), word)

    def test_readout_refuses_compound_barred_plural(self):
        readout = {"quantities": [
            {"name": "dogchilds", "recorded_number": 1}]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_controls(self):
        self.assertTrue(mod11._is_readable_word("sheep"))
        self.assertTrue(mod11._is_readable_word("humans"))
        self.assertFalse(mod11._is_readable_word("childs"))
        self.assertFalse(mod11._is_readable_word("toothes"))
        self.assertFalse(mod11._is_readable_word("qqzx"))

    def test_bound_forms_control(self):
        self.assertTrue(mod11._is_readable_word("informations"))
        self.assertTrue(mod11._is_readable_word("informationes"))
        self.assertTrue(mod11._is_readable_word("doginformations"))
        self.assertTrue(mod11._is_readable_word("doginformationes"))


class TestR18050PartTextBudget(unittest.TestCase):

    def test_delivered_text_inside_stated_budget(self):
        parts = frozenset(
            letter * length for letter, length in zip(
                "abcdef", (230, 230, 230, 230, 230, 233)))
        text = mod11._part_text(parts)
        self.assertLessEqual(len(text), 1000000)

    def test_single_level_orders_control(self):
        text = mod11._part_text(frozenset(("ab", "cd", "ef")))
        self.assertEqual(text.count("\n"), 5)

    def test_shared_budget_control(self):
        first = frozenset(
            letter * 166 for letter in "abcdef")
        text = mod11._part_text([first, first])
        self.assertEqual(text.count("\n"), 719)


class TestR18051WholeNumberCounts(unittest.TestCase):

    def test_point_standing_refuses_no_whole_number_forms(self):
        for handed in (30.9, "30", True, Decimal(30), Fraction(30, 1)):
            with self.assertRaises(ValueError, msg=repr(handed)):
                mod11.point_standing(handed)

    def test_classify_refuses_no_whole_number_forms(self):
        for handed in (30.5, "30", False, Decimal(30)):
            with self.assertRaises(ValueError, msg=repr(handed)):
                mod11.classify_run_outcome(handed, "attacker winning")

    def test_honest_loss_refuses_no_whole_number_forms(self):
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(Fraction(21, 2), 1)
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(10.9, 4.5)
        with self.assertRaises(ValueError):
            mod11.honest_loss_rate_h1(10, True)

    def test_controls(self):
        self.assertEqual(mod11.point_standing(30)["standing"], "at floor")
        self.assertEqual(
            mod11.point_standing(29)["standing"], "below floor")
        self.assertEqual(
            mod11.classify_run_outcome(30, "attacker winning")["outcome"],
            "attacker winning")
        self.assertEqual(
            mod11.classify_run_outcome(20, "attacker winning")["outcome"],
            "horizon insufficient")
        self.assertEqual(
            mod11.honest_loss_rate_h1(10, 4),
            {"form": "H1", "numerator": 6, "denominator": 10})
        with self.assertRaises(ValueError):
            mod11.point_standing("x")


class TestR18052BoundingHeadline(unittest.TestCase):

    def headline(self, **overrides):
        headline = {
            "axes": list(mod11.AXES),
            "traces": [{"moved": True}, {"moved": False},
                       {"moved": True}],
            "rests_on_axis": "farm size",
        }
        headline.update(overrides)
        return headline

    def test_lying_axes_refused(self):
        headline = self.headline(axes=[
            LieStr("bogus"), LieStr("bogus2"), LieStr("bogus3")])
        self.assertFalse(mod11.validate_bounding_headline(
            headline, {}, {}))

    def test_raising_edge_comparison_does_not_escape(self):
        result = mod11.validate_bounding_headline(
            self.headline(), {"near_zero_bound": 5},
            {"farm_internal_edge_count": RaisingCmp()})
        self.assertFalse(result)

    def test_controls(self):
        self.assertTrue(mod11.validate_bounding_headline(
            self.headline(), {}, {}))
        self.assertFalse(mod11.validate_bounding_headline(
            self.headline(axes=["a", "b", "c"]), {}, {}))
        self.assertFalse(mod11.validate_bounding_headline(
            self.headline(), {"near_zero_bound": 5},
            {"farm_internal_edge_count": 3}))
        self.assertTrue(mod11.validate_bounding_headline(
            self.headline(), {"near_zero_bound": 5},
            {"farm_internal_edge_count": 100}))


class TestR18053TopUpApplies(unittest.TestCase):

    def test_lying_probability_judged_on_stored_value(self):
        with self.assertRaises(ValueError):
            mod11.top_up_applies(LieCmp(5.0))
        self.assertFalse(mod11.top_up_applies(LieCmp(0.05)))

    def test_controls(self):
        with self.assertRaises(ValueError):
            mod11.top_up_applies(5.0)
        self.assertFalse(mod11.top_up_applies(0.05))
        self.assertTrue(mod11.top_up_applies(0.5))
        self.assertTrue(mod11.top_up_applies(0.1))
        self.assertTrue(mod11.top_up_applies(0.9))
        with self.assertRaises(ValueError):
            mod11.top_up_applies("x")


class TestR18054ShareReportStands(unittest.TestCase):

    def inputs(self, mark):
        return {"blocked_family_mark": mark}

    def test_lying_share_names_no_other_share(self):
        mark = {"affected_share": LieStr("share-a"),
                "count": 2, "resolved": False}
        self.assertTrue(mod11.share_report_stands(
            self.inputs(mark), "share-b"))
        self.assertFalse(mod11.share_report_stands(
            self.inputs(mark), "share-a"))

    def test_raising_truth_readings_do_not_escape(self):
        mark = {"affected_share": "share-a",
                "count": RaisingBool(), "resolved": False}
        self.assertFalse(mod11.share_report_stands(
            self.inputs(mark), "share-a"))
        mark = {"affected_share": "share-a",
                "count": 2, "resolved": RaisingBool()}
        self.assertTrue(mod11.share_report_stands(
            self.inputs(mark), "share-a"))

    def test_controls(self):
        mark = {"affected_share": "share-a",
                "count": 2, "resolved": False}
        self.assertFalse(mod11.share_report_stands(
            self.inputs(mark), "share-a"))
        self.assertTrue(mod11.share_report_stands(
            self.inputs(mark), "share-b"))
        self.assertTrue(mod11.share_report_stands({}, "share-a"))


if __name__ == "__main__":
    unittest.main()

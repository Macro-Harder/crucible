import unittest
from fractions import Fraction

from crucible import mod11, mod14


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


class HashArmedKey:
    armed = False

    def __init__(self, target):
        self.target = target

    def __hash__(self):
        if HashArmedKey.armed:
            raise RuntimeError("hash raises")
        return hash(self.target)

    def __eq__(self, other):
        return self is other


class HashArmedElement:
    armed = False

    def __hash__(self):
        if HashArmedElement.armed:
            raise RuntimeError("hash raises")
        return 4242

    def __eq__(self, other):
        return self is other


class CollidingKey(str):
    def __hash__(self):
        return hash("week")

    def __eq__(self, other):
        raise RuntimeError("eq raises")


class StrRaisesObj:
    def __str__(self):
        raise RuntimeError("str raises")


class StrRaisesText(str):
    def __str__(self):
        raise RuntimeError("str raises")


class IntLie(int):
    def __int__(self):
        return 99


class LenLie:
    def __len__(self):
        return 3


class LenRaises:
    def __len__(self):
        raise RuntimeError("len raises")


class BoolRaises:
    def __bool__(self):
        raise RuntimeError("bool raises")


class LowerLie(str):
    def lower(self):
        return "the location at 10 days horizon"


class WordLie(str):
    def __new__(cls, stored, spoken):
        obj = str.__new__(cls, stored)
        obj._spoken = spoken
        return obj

    def __str__(self):
        return self._spoken


class AbsLie:
    def __abs__(self):
        return 100


class ShareLie(float):
    def __lt__(self, other):
        return False


class ShareRaise(float):
    def __lt__(self, other):
        raise RuntimeError("lt raises")


class ReprRaisesPair(tuple):
    def __repr__(self):
        raise RuntimeError("repr raises")


def good_report():
    return {
        "distribution_near_threshold": True,
        "regime_class_counts": {"a": 1, "b": 2, "c": 3},
        "honest_loss_rate": {"form": "H1"},
        "points": [{"near_threshold": True, "replicates": 40}],
    }


def good_unit():
    return {
        "transition_figure": {
            "cumulative_incidence": {"r": 1},
            "right_censored": 0.1,
            "horizon": 10,
        },
        "incidence_label": "derived from the replicate counts in this unit",
        "location_sentences": ["the location at 10 days horizon"],
    }


class TestR19006(unittest.TestCase):
    def test_counts_text_form_refused(self):
        report = good_report()
        report["regime_class_counts"] = "abc"
        self.assertFalse(mod11.validate_transition_report(report))

    def test_counts_len_lie_refused(self):
        report = good_report()
        report["regime_class_counts"] = LenLie()
        self.assertFalse(mod11.validate_transition_report(report))

    def test_counts_len_raises_no_bare_escape(self):
        report = good_report()
        report["regime_class_counts"] = LenRaises()
        self.assertFalse(mod11.validate_transition_report(report))

    def test_replicates_text_refused(self):
        report = good_report()
        report["points"] = [{"near_threshold": True, "replicates": "99"}]
        self.assertFalse(mod11.validate_transition_report(report))

    def test_replicates_fractional_refused(self):
        report = good_report()
        report["points"] = [{"near_threshold": True, "replicates": 30.9}]
        self.assertFalse(mod11.validate_transition_report(report))

    def test_replicates_int_lie_refused(self):
        report = good_report()
        report["points"] = [
            {"near_threshold": True, "replicates": IntLie(10)}]
        self.assertFalse(mod11.validate_transition_report(report))

    def test_near_threshold_bool_raises_no_bare_escape(self):
        report = good_report()
        report["points"] = [
            {"near_threshold": BoolRaises(), "replicates": 5}]
        self.assertFalse(mod11.validate_transition_report(report))

    def test_controls(self):
        self.assertTrue(mod11.validate_transition_report(good_report()))
        low = good_report()
        low["points"] = [{"near_threshold": True, "replicates": 5}]
        self.assertFalse(mod11.validate_transition_report(low))
        two = good_report()
        two["regime_class_counts"] = {"a": 1, "b": 2}
        self.assertFalse(mod11.validate_transition_report(two))


class TestR19020(unittest.TestCase):
    def test_armed_inner_dict_carried_whole(self):
        ArmedKey.armed = False
        inner = {"week": "a"}
        inner[ArmedKey("week")] = "b"
        ArmedKey.armed = True
        try:
            copied = mod11._quoted_copy({"outer": inner})
        finally:
            ArmedKey.armed = False
        carried = copied["outer"]
        self.assertEqual(len(carried), 2)
        self.assertEqual(sorted(carried.values()), ["a", "b"])

    def test_plain_copy_control(self):
        source = {"a": {"b": [1, 2]}}
        copied = mod11._quoted_copy(source)
        self.assertEqual(copied, source)
        self.assertIsNot(copied["a"], source["a"])


class TestR19024(unittest.TestCase):
    def test_hash_armed_key_carried(self):
        HashArmedKey.armed = False
        inner = {"week": "a"}
        inner[HashArmedKey("week")] = "b"
        HashArmedKey.armed = True
        try:
            copied = mod11._quoted_copy(inner)
        finally:
            HashArmedKey.armed = False
        self.assertEqual(len(copied), 2)
        self.assertEqual(sorted(copied.values()), ["a", "b"])

    def test_hash_armed_set_element_carried(self):
        HashArmedElement.armed = False
        element = HashArmedElement()
        source = {element, "plain"}
        HashArmedElement.armed = True
        try:
            copied = mod11._quoted_copy(source)
        finally:
            HashArmedElement.armed = False
        self.assertEqual(len(copied), 2)
        self.assertIn("plain", copied)

    def test_plain_set_control(self):
        self.assertEqual(mod11._quoted_copy({1, 2}), {1, 2})


class TestR19025(unittest.TestCase):
    def test_text_location_refused(self):
        with self.assertRaises(ValueError):
            mod11.region_shift_steps(("3", 0), (0, 0))

    def test_fraction_location_refused(self):
        with self.assertRaises(ValueError):
            mod11.region_shift_steps((Fraction(3, 1), 0), (0, 0))

    def test_repr_raising_location_named_refusal(self):
        location = ReprRaisesPair(("x", 2))
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps(location, (0, 0))
        self.assertIn("region_shift_steps", str(caught.exception))

    def test_transition_wording_text_location_refused(self):
        with self.assertRaises(ValueError):
            mod11.transition_wording(("1", 0), (0, 0))

    def test_controls(self):
        self.assertEqual(mod11.region_shift_steps((1, 2), (3, 5)), (2, 3))
        self.assertTrue(
            mod11.transition_wording((3, 4), (4, 4))["holding_statement"])


class TestR19026And45(unittest.TestCase):
    TEXT = ("Over assumption set A-1, rows R-1, in the working "
            "range kind, the claim holds.")

    def test_str_raising_object_boolean_returned(self):
        result = mod11.validate_working_range_claim(
            self.TEXT, StrRaisesObj(), "rows R-1", "working range")
        self.assertFalse(result)

    def test_str_raising_text_judged_on_stored_text(self):
        result = mod11.validate_working_range_claim(
            self.TEXT, StrRaisesText("assumption set A-1"),
            "rows R-1", "working range")
        self.assertTrue(result)

    def test_empty_name_not_counted(self):
        text = "Over rows R-1, in the working range kind, the claim holds."
        self.assertFalse(mod11.validate_working_range_claim(
            text, "", "rows R-1", "working range"))

    def test_control(self):
        self.assertTrue(mod11.validate_working_range_claim(
            self.TEXT, "assumption set A-1", "rows R-1", "working range"))


class TestR19041(unittest.TestCase):
    def _record(self):
        record = {"headline_unit_identifiers": ["u1"]}
        record[CollidingKey("week")] = "2026-W01"
        return record

    def test_mod11_weekly_count_colliding_key(self):
        self.assertEqual(
            mod11.weekly_count([self._record()], "2026-W01"), 1)

    def test_mod14_weekly_count_colliding_key(self):
        self.assertEqual(
            mod14.weekly_headline_count([self._record()], "2026-W01"), 1)

    def test_controls(self):
        plain = {"week": "2026-W01",
                 "headline_unit_identifiers": ["u1", "u2"]}
        self.assertEqual(mod11.weekly_count([plain], "2026-W01"), 2)
        self.assertEqual(
            mod14.weekly_headline_count([plain], "2026-W01"), 2)
        self.assertEqual(mod11.weekly_count([plain], "2026-W02"), 0)


class TestR19044(unittest.TestCase):
    def test_lying_sentence_wrong_horizon_refused(self):
        unit = good_unit()
        unit["location_sentences"] = [
            LowerLie("the location at 999 days horizon")]
        self.assertFalse(mod11.validate_transition_unit(unit))

    def test_text_horizon_refused(self):
        unit = good_unit()
        figure = dict(unit["transition_figure"])
        figure["horizon"] = "10"
        unit["transition_figure"] = figure
        self.assertFalse(mod11.validate_transition_unit(unit))

    def test_control(self):
        self.assertTrue(mod11.validate_transition_unit(good_unit()))


class TestR19046(unittest.TestCase):
    def test_lying_name_refused(self):
        readout = {"quantities": [{
            "name": WordLie("zz", "share value standing"),
            "recorded_number": 3}]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_lying_rule_refused(self):
        readout = {"quantities": [{
            "name": "share value",
            "recorded_number": 3,
            "class_based": True,
            "class_rule": WordLie("zz", "share value standing recorded"),
        }]}
        self.assertFalse(mod11.validate_readout(readout))

    def test_control(self):
        readout = {"quantities": [{
            "name": "share value", "recorded_number": 3}]}
        self.assertTrue(mod11.validate_readout(readout))


class TestR19047(unittest.TestCase):
    def test_abs_lie_refused_named(self):
        with self.assertRaises(ValueError) as caught:
            mod11.moved_reading(AbsLie(), 1)
        self.assertIn("moved_reading", str(caught.exception))

    def test_controls(self):
        self.assertTrue(mod11.moved_reading(5, 3))
        self.assertFalse(mod11.moved_reading(1, 3))


class TestR19048(unittest.TestCase):
    def _figure(self, share):
        return {"cumulative_incidence": {"regime": {"share": share}}}

    def test_lying_share_below_endpoint(self):
        self.assertIsNone(mod11.location_for_endpoint(
            self._figure(ShareLie(0.1)), "regime", 0.9))

    def test_raising_share_verdict_returned(self):
        self.assertIsNone(mod11.location_for_endpoint(
            self._figure(ShareRaise(0.5)), "regime", 0.9))

    def test_control(self):
        result = mod11.location_for_endpoint(
            self._figure(0.99), "regime", 0.9)
        self.assertIsNotNone(result)
        self.assertEqual(result["share"], 0.99)


if __name__ == "__main__":
    unittest.main()

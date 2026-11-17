"""Pins for fix wave 20, Builder 3, Group 3, the MOD-11 family.

Rows R20-001, R20-019, R20-024, R20-077, R20-078, R20-079,
R20-080, R20-081, R20-082, and R20-083 of the Round 20 register.


Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

"""


import unittest
from decimal import Decimal
from fractions import Fraction
from crucible import mod11
from crucible import mod09


class EqLieStr(str):
    """A text storing one value whose equality and inequality
    readings answer as configured: a fixed boolean, or a raise."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __eq__(self, other):
        if self._lie == "raise":
            raise RuntimeError("equality reading raises")
        return self._lie

    def __ne__(self, other):
        if self._lie == "raise":
            raise RuntimeError("inequality reading raises")
        return not self._lie

    __hash__ = str.__hash__


class LieStr(str):
    """A text storing one value whose string reading and repr
    reading both name another value."""

    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return repr(self._reading)


class RaiseStr(str):
    """A text whose string and repr readings raise."""

    def __str__(self):
        raise RuntimeError("string reading raises")

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class LieReprList(list):
    def __new__(cls, items, reading):
        obj = list.__new__(cls)
        obj._reading = reading
        return obj

    def __init__(self, items, reading):
        list.__init__(self, items)

    def __repr__(self):
        return self._reading


class LieReprDict(dict):
    def __init__(self, items, reading):
        dict.__init__(self, items)
        self._reading = reading

    def __repr__(self):
        return self._reading


class LieReprSet(set):
    def __init__(self, items, reading):
        set.__init__(self, items)
        self._reading = reading

    def __repr__(self):
        return self._reading


class LyingLocation:
    """A location whose item readings return texts and whose
    repr reading names a valid grid pair."""

    def __init__(self):
        self.items = ("bogus", "bogus")

    def __getitem__(self, index):
        return self.items[index]

    def __repr__(self):
        return "(1, 2)"


def _headline(rests, witness=False):
    headline = {
        "axes": list(mod11.AXES),
        "traces": [{"moved": True}, {"moved": False},
                   {"moved": True}],
        "rests_on_axis": rests,
    }
    if witness:
        headline["zero_edge_witness_shape"] = "shape"
    return headline


def _envelope(scope):
    return {
        "scope": scope,
        "claims_between_points": False,
        "monotonicity_claimed": False,
        "interpolation_claimed": False,
        "holds": True,
    }


def _report(form, counts=None):
    if counts is None:
        counts = {"a": 1, "b": 2, "c": 3}
    return {
        "distribution_near_threshold": True,
        "regime_class_counts": counts,
        "honest_loss_rate": {"form": form},
        "points": [],
    }


def _unit(label):
    return {
        "transition_figure": {
            "cumulative_incidence": {"regime": 1},
            "right_censored": {"count": 0},
        },
        "incidence_label": label,
        "location_sentences": [],
    }


def _weekly_record(identifiers, week="W1"):
    return {"week": week,
            "headline_unit_identifiers": identifiers}


class TestR20001ValidatorStoredText(unittest.TestCase):
    """R20-001: the four MOD-11 validator acts judge a returned
    value on the text it stores, under settlement S-16."""

    def test_bounding_wrong_text_eq_true_no_witness(self):
        rests = EqLieStr("farm size", True)
        self.assertTrue(
            mod11.validate_bounding_headline(
                _headline(rests), None, None))

    def test_bounding_stated_text_eq_false_no_witness(self):
        rests = EqLieStr("external work issuance", False)
        self.assertFalse(
            mod11.validate_bounding_headline(
                _headline(rests), None, None))

    def test_bounding_stated_text_eq_raises(self):
        rests = EqLieStr("external work issuance", "raise")
        self.assertFalse(
            mod11.validate_bounding_headline(
                _headline(rests), None, None))

    def test_bounding_wrong_text_eq_raises(self):
        rests = EqLieStr("farm size", "raise")
        self.assertTrue(
            mod11.validate_bounding_headline(
                _headline(rests), None, None))

    def test_bounding_plain_stated_no_witness_control(self):
        self.assertFalse(
            mod11.validate_bounding_headline(
                _headline("external work issuance"), None, None))

    def test_bounding_plain_stated_with_witness_control(self):
        self.assertTrue(
            mod11.validate_bounding_headline(
                _headline("external work issuance", witness=True),
                None, None))

    def test_bounding_plain_other_axis_control(self):
        self.assertTrue(
            mod11.validate_bounding_headline(
                _headline("farm size"), None, None))

    def test_envelope_wrong_scope_eq_true(self):
        scope = EqLieStr("everywhere", True)
        self.assertFalse(mod11.validate_envelope_claim(
            _envelope(scope)))

    def test_envelope_stated_scope_eq_false(self):
        scope = EqLieStr(
            "sampled points and stated ranges only", False)
        self.assertTrue(mod11.validate_envelope_claim(
            _envelope(scope)))

    def test_envelope_stated_scope_eq_raises(self):
        scope = EqLieStr(
            "sampled points and stated ranges only", "raise")
        self.assertTrue(mod11.validate_envelope_claim(
            _envelope(scope)))

    def test_envelope_wrong_scope_eq_raises(self):
        scope = EqLieStr("everywhere", "raise")
        self.assertFalse(mod11.validate_envelope_claim(
            _envelope(scope)))

    def test_envelope_plain_stated_control(self):
        self.assertTrue(mod11.validate_envelope_claim(
            _envelope("sampled points and stated ranges only")))

    def test_envelope_plain_wrong_control(self):
        self.assertFalse(mod11.validate_envelope_claim(
            _envelope("everywhere")))

    def test_report_wrong_form_eq_true(self):
        form = EqLieStr("X9", True)
        self.assertFalse(mod11.validate_transition_report(
            _report(form)))

    def test_report_stated_form_eq_false(self):
        form = EqLieStr("H1", False)
        self.assertTrue(mod11.validate_transition_report(
            _report(form)))

    def test_report_stated_form_eq_raises(self):
        form = EqLieStr("H1", "raise")
        self.assertTrue(mod11.validate_transition_report(
            _report(form)))

    def test_report_plain_h1_control(self):
        self.assertTrue(mod11.validate_transition_report(
            _report("H1")))

    def test_report_plain_wrong_form_control(self):
        self.assertFalse(mod11.validate_transition_report(
            _report("X9")))

    def test_unit_wrong_label_eq_true(self):
        label = EqLieStr("some other label", True)
        self.assertFalse(mod11.validate_transition_unit(
            _unit(label)))

    def test_unit_stated_label_eq_false(self):
        label = EqLieStr(
            "derived from the replicate counts in this unit",
            False)
        self.assertTrue(mod11.validate_transition_unit(
            _unit(label)))

    def test_unit_stated_label_eq_raises(self):
        label = EqLieStr(
            "derived from the replicate counts in this unit",
            "raise")
        self.assertTrue(mod11.validate_transition_unit(
            _unit(label)))

    def test_unit_plain_label_control(self):
        self.assertTrue(mod11.validate_transition_unit(
            _unit("derived from the replicate counts in this "
                  "unit")))

    def test_unit_plain_wrong_label_control(self):
        self.assertFalse(mod11.validate_transition_unit(
            _unit("some other label")))


class TestR20019CountsWholeNumber(unittest.TestCase):
    """R20-019: each regime class count stands judged in whole
    number form under settlement S-16."""

    def _check(self, bad):
        counts = {"a": bad, "b": 1, "c": 2}
        self.assertFalse(mod11.validate_transition_report(
            _report("H1", counts)))

    def test_text_count(self):
        self._check("three")

    def test_none_count(self):
        self._check(None)

    def test_object_count(self):
        self._check(object())

    def test_bool_count(self):
        self._check(True)

    def test_fraction_count(self):
        self._check(Fraction(3, 1))

    def test_decimal_count(self):
        self._check(Decimal(3))

    def test_list_form_text_count(self):
        self.assertFalse(mod11.validate_transition_report(
            _report("H1", ["three", 1, 2])))

    def test_plain_counts_control(self):
        self.assertTrue(mod11.validate_transition_report(
            _report("H1")))

    def test_list_form_counts_control(self):
        self.assertTrue(mod11.validate_transition_report(
            _report("H1", [1, 2, 3])))

    def test_int_subclass_counts_control(self):
        class CountInt(int):
            pass

        counts = {"a": CountInt(4), "b": 1, "c": 2}
        self.assertTrue(mod11.validate_transition_report(
            _report("H1", counts)))


class TestR20024WeeklyKeying(unittest.TestCase):
    """R20-024: a container identifier stands keyed on its
    stored form, in the MOD-14 sister act cured form."""

    def _count(self, identifiers):
        return mod11.weekly_count(
            [_weekly_record(identifiers)], "W1")

    def test_list_shared_repr_counts_two(self):
        ids = [LieReprList([1], "[9]"), LieReprList([2], "[9]")]
        self.assertEqual(self._count(ids), 2)

    def test_list_split_repr_counts_one(self):
        ids = [LieReprList([1], "[1]"), LieReprList([1], "[7]")]
        self.assertEqual(self._count(ids), 1)

    def test_dict_shared_repr_counts_two(self):
        ids = [LieReprDict({"a": 1}, "same"),
               LieReprDict({"a": 2}, "same")]
        self.assertEqual(self._count(ids), 2)

    def test_dict_split_repr_counts_one(self):
        ids = [LieReprDict({"a": 1}, "first"),
               LieReprDict({"a": 1}, "second")]
        self.assertEqual(self._count(ids), 1)

    def test_set_shared_repr_counts_two(self):
        ids = [LieReprSet({1}, "same"), LieReprSet({2}, "same")]
        self.assertEqual(self._count(ids), 2)

    def test_set_split_repr_counts_one(self):
        ids = [LieReprSet({1}, "first"),
               LieReprSet({1}, "second")]
        self.assertEqual(self._count(ids), 1)

    def test_plain_distinct_lists_control(self):
        self.assertEqual(self._count([[1], [2]]), 2)

    def test_plain_duplicate_lists_control(self):
        self.assertEqual(self._count([[1], [1]]), 1)

    def test_plain_text_identifiers_control(self):
        self.assertEqual(self._count(["u1", "u2", "u1"]), 2)

    def test_plain_dict_and_set_control(self):
        ids = [{"a": 1}, {"a": 1}, {5}, {5}, {6}]
        self.assertEqual(self._count(ids), 3)


class TestR20077RetirementSentence(unittest.TestCase):
    """R20-077: the no verdict recorded sentence names the
    fixture on the text it stores."""

    def test_lying_fixture_named_on_stored_text(self):
        fixture = LieStr("XX-9", "F-01")
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(fixture)
        message = str(caught.exception)
        self.assertIn("recorded for: XX-9;", message)
        self.assertNotIn("recorded for: F-01;", message)

    def test_raising_fixture_named_on_stored_text(self):
        fixture = RaiseStr("XX-9")
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts(fixture)
        self.assertIn("XX-9", str(caught.exception))

    def test_plain_unrecorded_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.retirement_verdicts("XX-9")
        self.assertIn("XX-9", str(caught.exception))

    def test_plain_recorded_control(self):
        verdicts = mod11.retirement_verdicts("F-01")
        self.assertEqual(len(verdicts), 15)


class TestR20078MakeHeadlineSentence(unittest.TestCase):
    """R20-078: the fields beyond the closed unit sentence of
    make_headline_unit names each extra key on the text it
    stores."""

    def test_lying_extra_key_named_on_stored_text(self):
        key = LieStr("bogus_field", "claim_sentence")
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit({key: 1})
        message = str(caught.exception)
        self.assertIn("bogus_field", message)
        self.assertNotIn("claim_sentence", message)

    def test_plain_extra_key_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit({"bogus_field": 1})
        self.assertIn("bogus_field", str(caught.exception))


class TestR20079HeadlineRefusalSentence(unittest.TestCase):
    """R20-079: the fields beyond the closed unit sentence of
    the headline unit refusal names each extra key on the text
    it stores."""

    def test_lying_extra_key_named_on_stored_text(self):
        key = LieStr("bogus_field", "claim_sentence")
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit({key: 1})
        message = str(caught.exception)
        self.assertIn("bogus_field", message)
        self.assertNotIn("claim_sentence", message)

    def test_plain_extra_key_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.quote_headline_unit({"bogus_field": 1})
        self.assertIn("bogus_field", str(caught.exception))


CONTROL_CLAIM = (
    "Over assumption set A-1, rows R-1, in the working range "
    "kind, the claim holds.")


NONE_CLAIM = (
    "The claim holds over sampled points within the stated "
    "scope and limits alone for this run")


class TestR20080FirstSentence(unittest.TestCase):
    """R20-080: first_sentence reads a claim on the text it
    stores."""

    def test_stored_sentence_naming_none_refused(self):
        claim = LieStr(NONE_CLAIM, CONTROL_CLAIM)
        self.assertFalse(mod11.validate_working_range_claim(
            claim, "A-1", "R-1", "working range kind"))

    def test_stored_sentence_naming_all_validated(self):
        claim = LieStr(CONTROL_CLAIM, NONE_CLAIM)
        self.assertTrue(mod11.validate_working_range_claim(
            claim, "A-1", "R-1", "working range kind"))

    def test_first_sentence_helper_on_stored_text(self):
        claim = LieStr("Alpha beta. Gamma.", "Delta epsilon.")
        self.assertEqual(mod11.first_sentence(claim),
                         "Alpha beta")

    def test_plain_control_claim_validated(self):
        self.assertTrue(mod11.validate_working_range_claim(
            CONTROL_CLAIM, "A-1", "R-1", "working range kind"))

    def test_plain_none_claim_refused(self):
        self.assertFalse(mod11.validate_working_range_claim(
            NONE_CLAIM, "A-1", "R-1", "working range kind"))

    def test_first_sentence_plain_control(self):
        self.assertEqual(
            mod11.first_sentence("Alpha beta. Gamma."),
            "Alpha beta")


class TestR20081GridPairRefusal(unittest.TestCase):
    """R20-081: the grid pair refusal names the location on
    the form it stands in, at both consumers."""

    def test_region_shift_refusal_names_handed_location(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps(LyingLocation(), (0, 0))
        message = str(caught.exception)
        self.assertNotIn("(1, 2)", message)
        self.assertIn("bogus", message)

    def test_transition_wording_refusal_names_location(self):
        with self.assertRaises(ValueError) as caught:
            mod11.transition_wording(LyingLocation(), (0, 0))
        message = str(caught.exception)
        self.assertNotIn("(1, 2)", message)
        self.assertIn("bogus", message)

    def test_plain_location_refusal_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps(("a", "b"), (0, 0))
        self.assertIn("('a', 'b')", str(caught.exception))

    def test_plain_shift_control(self):
        self.assertEqual(
            mod11.region_shift_steps((0, 0), (1, 2)), (1, 2))


class TestR20082WeeklyRefusalSentence(unittest.TestCase):
    """R20-082: the weekly_count identifier refusal names the
    identifier on the form it stands in."""

    def test_lying_identifier_named_on_stored_form(self):
        identifier = LieStr("bogus id", "u1")
        record = _weekly_record([identifier])
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count([record], "W1")
        message = str(caught.exception)
        self.assertIn("bogus id", message)
        self.assertNotIn("'u1'", message)

    def test_plain_identifier_control(self):
        record = _weekly_record(["bogus id"])
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count([record], "W1")
        self.assertIn("'bogus id'", str(caught.exception))

    def test_plain_valid_identifier_control(self):
        record = _weekly_record(["u1"])
        self.assertEqual(mod11.weekly_count([record], "W1"), 1)


class TestR20083WeeklyContainerSentence(unittest.TestCase):
    """R20-083: the make_weekly_container held item refusal
    names the item on the form it stands in."""

    def test_lying_item_named_on_stored_form(self):
        item = LieStr("bogus id", "u1")
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("W1", [item])
        message = str(caught.exception)
        self.assertIn("bogus id", message)
        self.assertNotIn("'u1'", message)

    def test_plain_item_control(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("W1", ["bogus id"])
        self.assertIn("'bogus id'", str(caught.exception))

    def test_plain_valid_item_control(self):
        container = mod11.make_weekly_container("W1", ["u1"])
        self.assertEqual(container["count"], 1)


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


def readout_unit(outcome):
    record = {
        "run_record": {
            "ladder_position": 6,
            "strategies_exercised": ["conditional briber"],
        },
        "external_profit_swept_values": [0, 5],
        "search_record": {
            "per_point_outcome": {"point one": outcome},
        },
    }
    return mod09.readout(record, found_failure=False)


class TestR21004Distinguishing(unittest.TestCase):
    def test_decimal_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(Decimal(0)))

    def test_decimal_zero_point_zero_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(Decimal("0.00")))

    def test_fraction_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(Fraction(0)))

    def test_fraction_zero_over_five_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(Fraction(0, 5)))

    def test_readout_decimal_zero_point_mapping_no_sentence(self):
        unit = readout_unit(Decimal(0))
        self.assertNotIn("no_failure_sentence", unit)

    def test_readout_fraction_zero_point_mapping_no_sentence(self):
        unit = readout_unit(Fraction(0))
        self.assertNotIn("no_failure_sentence", unit)


class TestR21004Controls(unittest.TestCase):
    def test_decimal_nonzero_carries_content(self):
        self.assertTrue(mod09._outcome_carries_content(Decimal(1)))
        self.assertTrue(mod09._outcome_carries_content(Decimal("0.5")))
        self.assertTrue(mod09._outcome_carries_content(Decimal(-2)))

    def test_fraction_nonzero_carries_content(self):
        self.assertTrue(mod09._outcome_carries_content(Fraction(1, 2)))
        self.assertTrue(mod09._outcome_carries_content(Fraction(3)))

    def test_int_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(0))

    def test_float_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(0.0))

    def test_complex_zero_carries_no_content(self):
        self.assertFalse(mod09._outcome_carries_content(0j))

    def test_readout_decimal_nonzero_point_mapping_sentence(self):
        unit = readout_unit(Decimal(2))
        self.assertEqual(
            unit.get("no_failure_sentence"), mod09.NO_FAILURE_SENTENCE)

    def test_readout_fraction_nonzero_point_mapping_sentence(self):
        unit = readout_unit(Fraction(1, 2))
        self.assertEqual(
            unit.get("no_failure_sentence"), mod09.NO_FAILURE_SENTENCE)

    def test_readout_int_zero_point_mapping_no_sentence(self):
        unit = readout_unit(0)
        self.assertNotIn("no_failure_sentence", unit)

    def test_readout_float_zero_point_mapping_no_sentence(self):
        unit = readout_unit(0.0)
        self.assertNotIn("no_failure_sentence", unit)

    def test_readout_complex_zero_point_mapping_no_sentence(self):
        unit = readout_unit(0j)
        self.assertNotIn("no_failure_sentence", unit)


if __name__ == "__main__":
    unittest.main()

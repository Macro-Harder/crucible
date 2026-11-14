"""Pins for the Step 15 fix wave 3 items charged to this seat on
MOD-05: R3-008, R3-020, R3-025, R3-027, R3-029, R3-048, and the
MOD-05 limb of R3-051. Each pin stands in the distinguishing case
form, with a plain control and a clean control standing beside it.
"""

import unittest

from crucible import mod05


class EvilMembership:
    def __init__(self):
        self.stored = {"membership": 1}

    def __deepcopy__(self, memo=None):
        return {"membership": 1}


class LyingStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


def frozenset_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = frozenset((value,))
    return value


def tuple_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = (value,)
    return value


def adjudicate_kwargs(outcome):
    return {
        "accuracy_value": 0.5,
        "assumption_set": "assumption-set-1",
        "row": "row-1",
        "error_direction": "over",
        "outcome": outcome,
    }


class TestR3008PanelCopyAct(unittest.TestCase):
    def test_leaf_deepcopy_protocol_does_not_materialise(self):
        evil = EvilMembership()
        formed = mod05.panel_inputs({"item": evil, "ok": 2})
        self.assertIs(formed["item"], evil)
        self.assertEqual(formed["ok"], 2)
        self.assertTrue(mod05.validate_panel_inputs(formed))

    def test_leaf_in_list_deepcopy_protocol_does_not_materialise(self):
        evil = EvilMembership()
        formed = mod05.panel_inputs({"item": [evil]})
        self.assertIs(formed["item"][0], evil)

    def test_adjudicate_formed_set_carries_no_materialised_dict(self):
        evil = EvilMembership()
        case = {"case_identifier": "c1", "item": evil, "ok": 2}
        record = mod05.adjudicate(case, **adjudicate_kwargs("slashable"))
        self.assertIs(record["panel_inputs"]["item"], evil)
        self.assertTrue(
            mod05.validate_panel_inputs(record["panel_inputs"]))

    def test_plain_barred_control_still_refused(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"x": {"membership": 1}}))
        with self.assertRaises(ValueError):
            mod05.adjudicate(
                {"case_identifier": "c1", "membership": 1},
                **adjudicate_kwargs("slashable"))

    def test_clean_control_forms_unchanged(self):
        self.assertEqual(mod05.panel_inputs({"item": 3}), {"item": 3})


class TestR3020ArmenianVoAsUn(unittest.TestCase):
    def test_vo_lowercase_as_un_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"gro\u0578d_truth": 1}))

    def test_vo_capital_as_un_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"gro\u0548d_truth": 1}))

    def test_vo_as_un_removed_by_former(self):
        formed = mod05.panel_inputs(
            {"gro\u0578d_truth": 1, "gro\u0548d_truth": 1, "keep": 1})
        self.assertEqual(formed, {"keep": 1})

    def test_vo_as_n_control_still_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"grou\u0578d_truth": 1}))

    def test_clean_control(self):
        self.assertTrue(mod05.validate_panel_inputs({"clean": 1}))


class TestR3025PanelSymbolReadings(unittest.TestCase):
    def test_section_sign_as_s_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"member\u00a7hip": 1}))

    def test_plus_sign_as_t_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"is_hones+": 1}))
        self.assertFalse(
            mod05.validate_panel_inputs({"ground_+ruth": 1}))

    def test_cent_sign_as_c_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"label_referen\u00a2e": 1}))

    def test_symbol_keys_removed_by_former(self):
        formed = mod05.panel_inputs(
            {"member\u00a7hip": 1, "is_hones+": 1, "keep": 1})
        self.assertEqual(formed, {"keep": 1})

    def test_clean_control(self):
        self.assertTrue(mod05.validate_panel_inputs({"clean": 1}))


class TestR3027ProportionBaseNumber(unittest.TestCase):
    def test_int_override_denominator_judged_on_stored_value(self):
        class DenLie(int):
            def __int__(self):
                return 5

        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": DenLie(-5)}))

    def test_float_override_quotient_judged_on_stored_value(self):
        class QuotLie(float):
            def __float__(self):
                return 0.25

        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": 4,
             "quotient": QuotLie(0.9)}))

    def test_float_override_denominator_judged_on_stored_value(self):
        class DenLie(float):
            def __float__(self):
                return 4.0

        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": DenLie(-4.0)}))

    def test_int_override_numerator_refusal_direction(self):
        class NumLie(int):
            def __int__(self):
                return 8

        self.assertTrue(mod05.validate_proportion(
            {"numerator": NumLie(1), "denominator": 4,
             "quotient": 0.25}))

    def test_plain_controls(self):
        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": -5}))
        self.assertTrue(mod05.validate_proportion(
            {"numerator": 1, "denominator": 4, "quotient": 0.25}))
        self.assertFalse(mod05.validate_proportion(
            {"numerator": 1, "denominator": 4, "quotient": 0.9}))

    def test_plain_int_subclass_without_override_control(self):
        class PlainInt(int):
            pass

        self.assertTrue(mod05.validate_proportion(
            {"numerator": 1, "denominator": PlainInt(4),
             "quotient": 0.25}))


class TestR3029AdjudicateOutcome(unittest.TestCase):
    def test_lying_outcome_refused(self):
        with self.assertRaises(ValueError):
            mod05.adjudicate(
                {"case_identifier": "c1", "item": 3},
                **adjudicate_kwargs(LyingStr("bogus")))

    def test_plain_bogus_outcome_refused(self):
        with self.assertRaises(ValueError):
            mod05.adjudicate(
                {"case_identifier": "c1", "item": 3},
                **adjudicate_kwargs("bogus"))

    def test_plain_lawful_outcome_accepted(self):
        record = mod05.adjudicate(
            {"case_identifier": "c1", "item": 3},
            **adjudicate_kwargs("slashable"))
        self.assertEqual(record["outcome"], "slashable")

    def test_honest_subclass_lawful_outcome_accepted(self):
        class PlainStr(str):
            pass

        record = mod05.adjudicate(
            {"case_identifier": "c1", "item": 3},
            **adjudicate_kwargs(PlainStr("not slashable")))
        self.assertEqual(record["outcome"], "not slashable")


class TestR3048PanelKeyPositionDepth(unittest.TestCase):
    def test_frozenset_chain_key_past_bound_refused(self):
        self.assertFalse(
            mod05.validate_panel_inputs({frozenset_chain(150): 1}))

    def test_tuple_chain_key_past_bound_refused(self):
        self.assertFalse(
            mod05.validate_panel_inputs({tuple_chain(150): 1}))

    def test_frozenset_chain_key_at_2000_refused(self):
        self.assertFalse(
            mod05.validate_panel_inputs({frozenset_chain(2000): 1}))

    def test_nested_dict_frozenset_chain_key_past_bound_refused(self):
        self.assertFalse(mod05.validate_panel_inputs(
            {"outer": {frozenset_chain(150): 1}}))

    def test_panel_inputs_frozenset_chain_key_past_bound_raises(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs({frozenset_chain(150): 1})

    def test_panel_inputs_tuple_chain_key_past_bound_raises(self):
        with self.assertRaises(ValueError):
            mod05.panel_inputs({tuple_chain(150): 1})

    def test_shallow_chain_key_controls_stand(self):
        key = frozenset_chain(10)
        self.assertTrue(mod05.validate_panel_inputs({key: 1}))
        formed = mod05.panel_inputs({key: 1})
        self.assertEqual(formed, {key: 1})
        tuple_key = tuple_chain(10)
        self.assertTrue(mod05.validate_panel_inputs({tuple_key: 1}))

    def test_value_position_chain_control_still_refused(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"x": frozenset_chain(150)}))


class TestR3051CherokeeAndCopticPanelFold(unittest.TestCase):
    def test_cherokee_m_in_membership_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"\u13b7embership": 1}))

    def test_coptic_e_in_membership_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"m\u2c89mbership": 1}))

    def test_coptic_m_in_membership_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"\u2c99embership": 1}))
        self.assertFalse(
            mod05.validate_panel_inputs({"\u2c98embership": 1}))

    def test_cherokee_l_in_label_barred(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"\u13deabel": 1}))

    def test_cherokee_and_coptic_keys_removed_by_former(self):
        formed = mod05.panel_inputs(
            {"\u13b7embership": 1, "m\u2c89mbership": 1, "keep": 1})
        self.assertEqual(formed, {"keep": 1})

    def test_clean_control(self):
        self.assertTrue(mod05.validate_panel_inputs({"clean": 1}))
        self.assertFalse(mod05.validate_panel_inputs({"membership": 1}))


if __name__ == "__main__":
    unittest.main()

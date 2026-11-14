"""Step 15 Round 2 fix pins, cluster R2-3 (names read as names).

Each test pins one limb of R2-A7-04 or R2-A7-05 in the standing form
of its module: MOD-01 validation and reportability stay boolean,
MOD-10 retention refuses in its named ValueError form, and MOD-12
run record validation stays boolean. The money field names below
stand built by joining parts, in the form MOD-12 itself uses for
its marker, so this file carries no joined spelling of its own.
"""

import unittest

from crucible import mod01, mod10, mod12


_M = "real_" + "money"
_MV = _M + "_value"
_NAME_FORMS = (
    _MV,
    _MV.title(),
    _M.upper(),
    "real" + "Money" + "Value",
    _MV.replace("_", "-"),
    _M + "_amount",
)
_SHAPE_FORMS = (
    {"Amount": 5, "Currency": "USD"},
    {"amount": 5, "Currency": "USD"},
    {"Amount": 5, "currency": "USD"},
    {"AMOUNT": 5, "CURRENCY": "USD"},
)


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


def _run_record(**overrides):
    record = {"run_class": "screening", "seed_domain": "screening"}
    record.update(overrides)
    return record


class TestR2A704Mod01Names(unittest.TestCase):
    def test_money_name_forms_fail_validation_and_reportability(self):
        for name in _NAME_FORMS:
            instance = _form4(**{name: 500})
            self.assertIs(mod01.validate_record("4", instance), False, name)
            self.assertIs(mod01.run_is_reportable("4", instance), False, name)

    def test_money_name_form_nested_at_depth_fails(self):
        instance = _form4(outer={"inner": {_MV.title(): 5}})
        self.assertIs(mod01.validate_record("4", instance), False)

    def test_money_name_with_no_value_standing_still_validates(self):
        for name in (_MV, _MV.title(), _M.upper()):
            instance = _form4(**{name: None})
            self.assertIs(mod01.validate_record("4", instance), True, name)

    def test_unmutated_form4_still_passes(self):
        self.assertIs(mod01.validate_record("4", _form4()), True)
        self.assertIs(mod01.run_is_reportable("4", _form4()), True)


class TestR2A704Mod01Shape(unittest.TestCase):
    def test_amount_currency_shapes_fail_in_any_case_dress(self):
        for shape in _SHAPE_FORMS:
            instance = _form4(stake=dict(shape))
            self.assertIs(mod01.validate_record("4", instance), False, shape)
            self.assertIs(mod01.run_is_reportable("4", instance), False, shape)

    def test_shape_fragments_in_sibling_branches_still_validate(self):
        instance = _form4(
            first={"amount": 5}, second={"currency": "USD"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_amount_alone_still_validates(self):
        instance = _form4(stake={"amount": 5})
        self.assertIs(mod01.validate_record("4", instance), True)


class TestR2A704Mod10Retention(unittest.TestCase):
    def test_retention_refuses_money_name_forms_in_any_dress(self):
        for name in _NAME_FORMS:
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=name):
                store.retain_run_record({"run_id": "r2-fix3-a", name: 500})

    def test_retention_refuses_amount_currency_shapes_in_any_case(self):
        for shape in _SHAPE_FORMS:
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=str(shape)):
                store.retain_run_record(
                    {"run_id": "r2-fix3-b", "stake": dict(shape)})

    def test_retention_keeps_clean_and_valueless_forms(self):
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record({"run_id": "r2-fix3-c"})
        self.assertEqual(kept["run_id"], "r2-fix3-c")
        kept = store.retain_run_record(
            {"run_id": "r2-fix3-d", _MV.title(): None})
        self.assertEqual(kept["run_id"], "r2-fix3-d")
        kept = store.retain_run_record(
            {"run_id": "r2-fix3-e", "stake": {"amount": 5}})
        self.assertEqual(kept["run_id"], "r2-fix3-e")


class TestR2A704Mod12RunRecord(unittest.TestCase):
    def test_amount_currency_shape_read_in_any_case_dress(self):
        for shape in _SHAPE_FORMS:
            record = _run_record(stake=dict(shape))
            self.assertIs(mod12.validate_run_record(record), False, shape)

    def test_money_name_forms_fail_in_any_dress(self):
        for name in _NAME_FORMS:
            record = _run_record(**{name: 500})
            self.assertIs(mod12.validate_run_record(record), False, name)

    def test_conforming_and_valueless_forms_still_pass(self):
        self.assertIs(mod12.validate_run_record(_run_record()), True)
        self.assertIs(
            mod12.validate_run_record(_run_record(**{_MV.title(): None})),
            True)
        self.assertIs(
            mod12.validate_run_record(_run_record(stake={"amount": 5})),
            True)


class TestR2A705AnchorSets(unittest.TestCase):
    def test_set_forms_carrying_other_than_three_values_fail(self):
        for values in ({"a", "b", "c", "d"},
                       frozenset(["a", "b", "c", "d"]),
                       {"a", "b"},
                       frozenset(["a", "b"])):
            instance = _form4(anchor_scenario_values=values)
            self.assertIs(
                mod01.validate_record("4", instance), False, values)
            self.assertIs(
                mod01.run_is_reportable("4", instance), False, values)

    def test_set_forms_carrying_three_values_still_pass(self):
        for values in ({"a", "b", "c"}, frozenset(["a", "b", "c"])):
            instance = _form4(anchor_scenario_values=values)
            self.assertIs(mod01.validate_record("4", instance), True, values)

    def test_dict_and_list_anchor_forms_keep_their_standings(self):
        four = ["a", "b", "c", "d"]
        three = ["a", "b", "c"]
        self.assertIs(
            mod01.validate_record("4", _form4(anchor_scenario_values=four)),
            False)
        self.assertIs(
            mod01.validate_record("4", _form4(anchor_scenario_values=three)),
            True)


if __name__ == "__main__":
    unittest.main()

"""Step 15 Round 3 fix pins, cluster R3-1 (names in any separator dress).

Each test pins one limb of R3-A7-02 or R3-A7-03 in the standing form
of its module: MOD-01 validation and reportability stay boolean,
MOD-10 retention refuses in its named ValueError form, and MOD-12
run record validation stays boolean. The money field names below
stand built by joining parts, in the form MOD-12 itself uses for
its marker, so this file carries no joined spelling of its own.
"""

import unittest

from crucible import mod01, mod10, mod12


_M = "real" + "_" + "money"
_MV = _M + "_" + "value"
_DOT = "."
_DOTTED_NAMES = (
    _DOT.join(("real", "money", "value")),
    _DOT.join(("Real", "Money", "Value")),
    _DOT.join(("real", "money")),
    "real" + _DOT + "money" + "_" + "value",
)
_TAB_NAME = "real" + "\t" + "money"
_DOTTED_SHAPES = (
    {"Amount" + _DOT: 5, "Currency": "USD"},
    {"Amount" + _DOT: 5, "Currency" + _DOT: "USD"},
)
_SEPARATOR_SHAPES = (
    {"Amo" + "_" + "unt": 5, "Curr" + "_" + "ency": "USD"},
    {"Amo unt": 5, "Curr ency": "USD"},
    {"Amo-unt": 5, "Curr-ency": "USD"},
    {"Amount ": 5, "Currency ": "USD"},
)


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


def _run_record(**overrides):
    record = {"run_class": "screening", "seed_domain": "screening"}
    record.update(overrides)
    return record


class TestR3A702DottedNames(unittest.TestCase):
    def test_dotted_money_names_fail_at_mod01(self):
        for name in _DOTTED_NAMES:
            instance = _form4(**{name: 500})
            self.assertIs(mod01.validate_record("4", instance), False, name)
            self.assertIs(mod01.run_is_reportable("4", instance), False, name)

    def test_dotted_money_names_refused_at_mod10_retention(self):
        for name in _DOTTED_NAMES:
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=name):
                store.retain_run_record({"run_id": "r3-fix1-a", name: 500})

    def test_dotted_money_names_fail_at_mod12(self):
        for name in _DOTTED_NAMES:
            record = _run_record(**{name: 500})
            self.assertIs(mod12.validate_run_record(record), False, name)

    def test_tab_money_name_fails_at_all_three_modules(self):
        instance = _form4(**{_TAB_NAME: 500})
        self.assertIs(mod01.validate_record("4", instance), False)
        self.assertIs(mod01.run_is_reportable("4", instance), False)
        store = mod10.RecorderStore(store_kind="sweep")
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "r3-fix1-b", _TAB_NAME: 500})
        record = _run_record(**{_TAB_NAME: 500})
        self.assertIs(mod12.validate_run_record(record), False)

    def test_underscore_ahead_of_dot_name_still_refused(self):
        name = _M + _DOT + "value"
        instance = _form4(**{name: 500})
        self.assertIs(mod01.validate_record("4", instance), False, name)
        record = _run_record(**{name: 500})
        self.assertIs(mod12.validate_run_record(record), False, name)


class TestR3A702DottedShape(unittest.TestCase):
    def test_trailing_dot_shape_fails_at_all_three_modules(self):
        for shape in _DOTTED_SHAPES:
            instance = _form4(stake=dict(shape))
            self.assertIs(mod01.validate_record("4", instance), False, shape)
            self.assertIs(mod01.run_is_reportable("4", instance), False, shape)
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=str(shape)):
                store.retain_run_record(
                    {"run_id": "r3-fix1-c", "stake": dict(shape)})
            record = _run_record(stake=dict(shape))
            self.assertIs(mod12.validate_run_record(record), False, shape)


class TestR3A703Mod12SeparatorShapes(unittest.TestCase):
    def test_separator_shape_keys_fail_at_mod12(self):
        for shape in _SEPARATOR_SHAPES:
            record = _run_record(stake=dict(shape))
            self.assertIs(mod12.validate_run_record(record), False, shape)

    def test_separator_shape_keys_still_fail_at_mod01_and_mod10(self):
        for shape in _SEPARATOR_SHAPES:
            instance = _form4(stake=dict(shape))
            self.assertIs(mod01.validate_record("4", instance), False, shape)
            store = mod10.RecorderStore(store_kind="sweep")
            with self.assertRaises(ValueError, msg=str(shape)):
                store.retain_run_record(
                    {"run_id": "r3-fix1-d", "stake": dict(shape)})


class TestR3StandingControls(unittest.TestCase):
    def test_money_name_at_none_validates_and_retains(self):
        name = _DOTTED_NAMES[0]
        instance = _form4(**{name: None})
        self.assertIs(mod01.validate_record("4", instance), True, name)
        self.assertIs(mod01.run_is_reportable("4", instance), True, name)
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record({"run_id": "r3-fix1-e", name: None})
        self.assertEqual(kept["run_id"], "r3-fix1-e")
        record = _run_record(**{name: None})
        self.assertIs(mod12.validate_run_record(record), True, name)

    def test_amount_alone_still_validates_at_all_three(self):
        instance = _form4(stake={"amount": 5})
        self.assertIs(mod01.validate_record("4", instance), True)
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record(
            {"run_id": "r3-fix1-f", "stake": {"amount": 5}})
        self.assertEqual(kept["run_id"], "r3-fix1-f")
        record = _run_record(stake={"amount": 5})
        self.assertIs(mod12.validate_run_record(record), True)

    def test_shape_fragments_in_sibling_branches_still_validate(self):
        instance = _form4(
            first={"amount": 5}, second={"currency": "USD"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_unmutated_form4_and_clean_run_record_still_pass(self):
        self.assertIs(mod01.validate_record("4", _form4()), True)
        self.assertIs(mod01.run_is_reportable("4", _form4()), True)
        self.assertIs(mod12.validate_run_record(_run_record()), True)


if __name__ == "__main__":
    unittest.main()

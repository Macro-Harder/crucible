"""Step 15 Round 4 fix pins, cluster R4-1 (a name read by its letters and digits).

Each test pins one limb of R4-A6-01 or R4-A6-02 in the standing form
of its module: MOD-01 validation and reportability stay boolean,
MOD-10 retention refuses in its named ValueError form, and MOD-12
run record validation stays boolean. The money and anchor field
names below stand built by joining parts, so this file carries no
joined spelling of its own.
"""

import unittest

from crucible import mod01, mod10, mod12


def _joined(separator, *parts):
    return separator.join(parts)


_MONEY_PARTS = ("real", "money", "value")
_NAME_SEPS = (
    "/", ":", ";", "+", "\\", "\n", "\r", "\v", "\f",
    "\u00a0", "\u2003",
)
_NAME_NAMES = tuple(
    _joined(sep, *_MONEY_PARTS) for sep in _NAME_SEPS
) + (
    _joined("/", "real", "money"),
    _joined("\n", "real", "money"),
    _joined("//", *_MONEY_PARTS),
    _joined("::", *_MONEY_PARTS),
    _joined(";;", *_MONEY_PARTS),
    "/" + _joined("/", *_MONEY_PARTS) + "/",
    "///" + _joined("///", "real", "money") + "///",
    _joined("\r", *_MONEY_PARTS),
)

_SHAPE_SEPS = ("/", ":", ";", "+", "\\")


def _inside_shape(sep):
    return {"Amo" + sep + "unt": 5, "Curr" + sep + "ency": "USD"}


def _trailing_shape(sep):
    return {"Amount" + sep: 5, "Currency" + sep: "USD"}


_SHAPES = tuple(_inside_shape(sep) for sep in _SHAPE_SEPS) + tuple(
    _trailing_shape(sep) for sep in (":", ";", "+")
) + (
    {"/Amount/": 5, "/Currency/": "USD"},
    _inside_shape("\n"),
    _inside_shape("\u00a0"),
    _trailing_shape("\u2003"),
)

_ANCHOR_PARTS = ("anchor", "scenario", "values")
_ANCHOR_EXACT = _joined("_", *_ANCHOR_PARTS)
_ANCHOR_NAMES = (
    _joined(".", *_ANCHOR_PARTS),
    _joined("/", *_ANCHOR_PARTS),
    _joined(":", *_ANCHOR_PARTS),
    _joined("-", *_ANCHOR_PARTS),
    _joined(" ", *_ANCHOR_PARTS),
    _joined("..", *_ANCHOR_PARTS),
    _joined(";", *_ANCHOR_PARTS),
    _joined("+", *_ANCHOR_PARTS),
    _joined("\\", *_ANCHOR_PARTS),
    _joined("\t", *_ANCHOR_PARTS),
    _joined("_", *_ANCHOR_PARTS).upper(),
    _joined("_", "Anchor", "Scenario", "Values"),
    _ANCHOR_EXACT + " ",
    " " + _ANCHOR_EXACT,
)


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


def _run_record(**overrides):
    record = {"run_class": "screening", "seed_domain": "screening"}
    record.update(overrides)
    return record


def _assert_money_refused(test_case, name, value):
    instance = _form4(**{name: value})
    test_case.assertIs(mod01.validate_record("4", instance), False, name)
    test_case.assertIs(mod01.run_is_reportable("4", instance), False, name)
    store = mod10.RecorderStore(store_kind="sweep")
    with test_case.assertRaises(ValueError, msg=name):
        store.retain_run_record({"run_id": "r4-fix1-a", name: value})
    record = _run_record(**{name: value})
    test_case.assertIs(mod12.validate_run_record(record), False, name)


def _assert_shape_refused(test_case, shape):
    instance = _form4(stake=dict(shape))
    test_case.assertIs(mod01.validate_record("4", instance), False, shape)
    test_case.assertIs(mod01.run_is_reportable("4", instance), False, shape)
    store = mod10.RecorderStore(store_kind="sweep")
    with test_case.assertRaises(ValueError, msg=str(shape)):
        store.retain_run_record({"run_id": "r4-fix1-b", "stake": dict(shape)})
    record = _run_record(stake=dict(shape))
    test_case.assertIs(mod12.validate_run_record(record), False, shape)


class TestR4A601FurtherSeparatorNames(unittest.TestCase):
    def test_separator_money_names_fail_at_all_three_modules(self):
        for name in _NAME_NAMES:
            _assert_money_refused(self, name, 500)


class TestR4A601FurtherSeparatorShapes(unittest.TestCase):
    def test_separator_shapes_fail_at_all_three_modules(self):
        for shape in _SHAPES:
            _assert_shape_refused(self, shape)


class TestR4A602AnchorDressedNames(unittest.TestCase):
    def test_dressed_anchor_count_of_four_fails_at_both_modules(self):
        for name in _ANCHOR_NAMES:
            values = {"a", "b", "c", "d"}
            instance = _form4(**{name: values})
            self.assertIs(mod01.validate_record("4", instance), False, name)
            record = _run_record(**{name: values})
            self.assertIs(mod12.validate_run_record(record), False, name)

    def test_dressed_anchor_count_of_two_fails_at_both_modules(self):
        for name in _ANCHOR_NAMES:
            values = {"a", "b"}
            instance = _form4(**{name: values})
            self.assertIs(mod01.validate_record("4", instance), False, name)
            record = _run_record(**{name: values})
            self.assertIs(mod12.validate_run_record(record), False, name)

    def test_dressed_anchor_count_of_three_validates_at_both_modules(self):
        for name in _ANCHOR_NAMES:
            values = {"a", "b", "c"}
            instance = _form4(**{name: values})
            self.assertIs(mod01.validate_record("4", instance), True, name)
            record = _run_record(**{name: values})
            self.assertIs(mod12.validate_run_record(record), True, name)


class TestR4StandingControls(unittest.TestCase):
    def test_exact_anchor_count_of_three_validates_at_both_modules(self):
        values = {"a", "b", "c"}
        instance = _form4(**{_ANCHOR_EXACT: values})
        self.assertIs(mod01.validate_record("4", instance), True)
        record = _run_record(**{_ANCHOR_EXACT: values})
        self.assertIs(mod12.validate_run_record(record), True)

    def test_exact_anchor_count_of_four_still_fails_at_both_modules(self):
        values = {"a", "b", "c", "d"}
        instance = _form4(**{_ANCHOR_EXACT: values})
        self.assertIs(mod01.validate_record("4", instance), False)
        record = _run_record(**{_ANCHOR_EXACT: values})
        self.assertIs(mod12.validate_run_record(record), False)

    def test_money_name_at_none_validates_and_retains(self):
        name = _NAME_NAMES[0]
        instance = _form4(**{name: None})
        self.assertIs(mod01.validate_record("4", instance), True, name)
        self.assertIs(mod01.run_is_reportable("4", instance), True, name)
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record({"run_id": "r4-fix1-c", name: None})
        self.assertEqual(kept["run_id"], "r4-fix1-c")
        record = _run_record(**{name: None})
        self.assertIs(mod12.validate_run_record(record), True, name)

    def test_amount_alone_still_validates_at_all_three(self):
        instance = _form4(stake={"amount": 5})
        self.assertIs(mod01.validate_record("4", instance), True)
        store = mod10.RecorderStore(store_kind="sweep")
        kept = store.retain_run_record(
            {"run_id": "r4-fix1-d", "stake": {"amount": 5}})
        self.assertEqual(kept["run_id"], "r4-fix1-d")
        record = _run_record(stake={"amount": 5})
        self.assertIs(mod12.validate_run_record(record), True)

    def test_shape_fragments_in_sibling_branches_still_validate(self):
        instance = _form4(
            first={"amount": 5}, second={"currency": "USD"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_prior_dresses_still_refused(self):
        for name in (
            _joined(".", *_MONEY_PARTS),
            _joined("_", *_MONEY_PARTS),
            _joined("-", *_MONEY_PARTS),
            _joined(" ", *_MONEY_PARTS),
            _joined("\t", "real", "money"),
        ):
            _assert_money_refused(self, name, 500)
        for shape in (
            {"Amo" + "_" + "unt": 5, "Curr" + "_" + "ency": "USD"},
            {"Amount ": 5, "Currency ": "USD"},
            {"Amount" + ".": 5, "Currency": "USD"},
        ):
            _assert_shape_refused(self, shape)

    def test_unmutated_form4_and_clean_run_record_still_pass(self):
        self.assertIs(mod01.validate_record("4", _form4()), True)
        self.assertIs(mod01.run_is_reportable("4", _form4()), True)
        self.assertIs(mod12.validate_run_record(_run_record()), True)


if __name__ == "__main__":
    unittest.main()

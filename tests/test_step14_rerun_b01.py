"""Step 14 re-run pins, cluster B1, slice S-01.

Each test pins one limb of finding R5-A6-01 or R5-A6-02 at MOD-01
only, in the standing form of that module: validation and
reportability stay boolean. The barred names below stand built by
joining parts or by letter escapes, so this file carries no joined
spelling of its own.
"""

import unittest

from crucible import mod01


_M = "real" + "money"
_FIELD_PARTS = ("anchor", "scenario", "values")
_FIELD_EXACT = "_".join(_FIELD_PARTS)


def _form4(**overrides):
    instance = mod01.minimal_valid_instance("4")
    instance.update(overrides)
    return instance


_MONEY_NAMES = (
    "r\u00e9almoneyvalue",
    "realm\u00f3neyvalue",
    "r\u00ebal_money_value",
    "\uff52ealmoneyvalue",
    "\uff52\uff45\uff41\uff4c\uff4d\uff4f\uff4e\uff45\uff59"
    "\uff56\uff41\uff4c\uff55\uff45",
    "re\u0430lmoneyvalue",
    "realm\u043eneyvalue",
    "realm\u03bfneyvalue",
    "\u0440\u0435\u0430\u043b\u043c\u0430\u043d\u0438value",
    "real5moneyvalue",
    "real\u0665moneyvalue",
    "real\uff15moneyvalue",
    "rea1moneyvalue",
    "re4lmoneyvalue",
)

_SHAPES = (
    {"Amo\u00fcnt": 5, "Curr\u00e9ncy": "USD"},
    {"\uff21\uff4d\uff4f\uff55\uff4e\uff54": 5,
     "\uff23\uff55\uff52\uff52\uff45\uff4e\uff43\uff59": "USD"},
    {"\u0410mount": 5, "Currency": "USD"},
    {"Amo5unt": 5, "Curr5ency": "USD"},
    {"Amount5": 5, "Currency5": "USD"},
)

_FIELD_NAMES = (
    "\u00e0nchor_scenario_values",
    "anchor_sc\u00e9nario_values",
    "\uff41nchor_scenario_values",
    "\uff41\uff4e\uff43\uff48\uff4f\uff52\uff53\uff43\uff45\uff4e"
    "\uff41\uff52\uff49\uff4f\uff56\uff41\uff4c\uff55\uff45\uff53",
    "\u0430nchor_scenario_values",
    "\u0430\u043d\u0447\u043e\u0440_scenario_values",
)


class TestR5A601MoneyNamesInLetterDresses(unittest.TestCase):
    def test_each_dressed_name_fails_and_is_not_reportable(self):
        for name in _MONEY_NAMES:
            instance = _form4(**{name: 500})
            self.assertIs(mod01.validate_record("4", instance), False, name)
            self.assertIs(mod01.run_is_reportable("4", instance), False, name)


class TestR5A601ShapesInLetterDresses(unittest.TestCase):
    def test_each_dressed_shape_fails_and_is_not_reportable(self):
        for shape in _SHAPES:
            instance = _form4(stake=dict(shape))
            self.assertIs(mod01.validate_record("4", instance), False, shape)
            self.assertIs(mod01.run_is_reportable("4", instance), False, shape)


class TestR5A602FieldNameInLetterDresses(unittest.TestCase):
    def test_count_of_four_fails_under_each_dressed_name(self):
        for name in _FIELD_NAMES:
            instance = _form4(**{name: {"a", "b", "c", "d"}})
            self.assertIs(mod01.validate_record("4", instance), False, name)

    def test_count_of_two_fails_under_each_dressed_name(self):
        for name in _FIELD_NAMES:
            instance = _form4(**{name: {"a", "b"}})
            self.assertIs(mod01.validate_record("4", instance), False, name)

    def test_count_of_three_passes_under_each_dressed_name(self):
        for name in _FIELD_NAMES:
            instance = _form4(**{name: {"a", "b", "c"}})
            self.assertIs(mod01.validate_record("4", instance), True, name)


class TestLawfulNamesUnaffected(unittest.TestCase):
    def test_accented_lawful_name_passes(self):
        instance = _form4(**{"caf\u00e9_label": "stated value"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_non_latin_lawful_name_passes(self):
        instance = _form4(**{"\u043f\u0440\u0438\u043c\u0435\u0440": "x"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_lawful_names_sharing_only_parts_pass(self):
        instance = _form4(stake={"amount_of_work": 5,
                                 "currency_of_record": "stated value"})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_digit_carrying_lawful_name_passes(self):
        instance = _form4(**{"fie1d_note": "stated value"})
        self.assertIs(mod01.validate_record("4", instance), True)


class TestStandingControlsHold(unittest.TestCase):
    def test_unmutated_instance_passes(self):
        self.assertIs(mod01.validate_record("4", _form4()), True)

    def test_money_name_at_none_value_passes(self):
        instance = _form4(**{_M + "value": None})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_amount_alone_passes(self):
        instance = _form4(stake={"amount": 5})
        self.assertIs(mod01.validate_record("4", instance), True)

    def test_exact_field_name_counts_hold(self):
        four = _form4(**{_FIELD_EXACT: {"a", "b", "c", "d"}})
        three = _form4(**{_FIELD_EXACT: {"a", "b", "c"}})
        two = _form4(**{_FIELD_EXACT: {"a", "b"}})
        self.assertIs(mod01.validate_record("4", four), False)
        self.assertIs(mod01.validate_record("4", three), True)
        self.assertIs(mod01.validate_record("4", two), False)


if __name__ == "__main__":
    unittest.main()

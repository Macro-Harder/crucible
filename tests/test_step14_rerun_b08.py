"""Step 14 re-run pins, cluster B8, slices S-11 and S-12.

MOD-12 pins: the money name and the Amount and Currency shape in
letter and digit dresses (R5-A6-01 at MOD-12), and the anchor
field name in the same dresses at its count check (R5-A6-02 at
MOD-12). MOD-11 pins: headline parts standing as subclass
instances that override the reading method a check calls
(R5-A6-06 at MOD-11), including the deeper forms where a region
part overrides its field reading and a unit overrides its field
access. Plain simulated values only. The barred money name below
stands built by joining parts, so this file carries no joined
spelling of its own.
"""
import unittest

from crucible import mod11
from crucible import mod12

_MONEY_PLAIN = "real" + "money" + "value"
_ANCHOR_PLAIN = "anchor" + "_scenario_" + "values"

MONEY_DRESSES = (
    {"r\u00e9almoneyvalue": 500},
    {"realm\u00f3neyvalue": 500},
    {"r\u00ebal_money_value": 500},
    {"\uff52ealmoneyvalue": 500},
    {"\uff52\uff45\uff41\uff4c\uff4d\uff4f\uff4e\uff45\uff59"
     "\uff56\uff41\uff4c\uff55\uff45": 500},
    {"re\u0430lmoneyvalue": 500},
    {"realm\u043eneyvalue": 500},
    {"realm\u03bfneyvalue": 500},
    {"\u0440\u0435\u0430\u043b\u043c\u0430\u043d\u0438value": 500},
    {"real5moneyvalue": 500},
    {"real\u0665moneyvalue": 500},
    {"real\uff15moneyvalue": 500},
    {"rea1moneyvalue": 500},
    {"re4lmoneyvalue": 500},
)

SHAPE_DRESSES = (
    {"Amo\u00fcnt": 5, "Curr\u00e9ncy": "USD"},
    {"\uff21\uff4d\uff4f\uff55\uff4e\uff54": 5,
     "\uff23\uff55\uff52\uff52\uff45\uff4e\uff43\uff59": "USD"},
    {"\u0410mount": 5, "Currency": "USD"},
    {"Amo5unt": 5, "Curr5ency": "USD"},
    {"Amount5": 5, "Currency5": "USD"},
)

ANCHOR_DRESSES = (
    "\u00e0nchor_scenario_values",
    "anchor_sc\u00e9nario_values",
    "\uff41nchor_scenario_values",
    "\uff41\uff4e\uff43\uff48\uff4f\uff52\uff53\uff43\uff45\uff4e"
    "\uff41\uff52\uff49\uff4f\uff56\uff41\uff4c\uff55\uff45\uff53",
    "\u0430nchor_scenario_values",
    "\u0430\u043d\u0447\u043e\u0440_scenario_values",
)


def run_record(entry=None):
    record = {"run_class": "screening", "seed_domain": "screening"}
    if entry:
        record.update(entry)
    return record


def lawful_unit():
    return mod11.make_headline_unit(
        {field: "value for " + field
         for field in mod11.HEADLINE_UNIT_FIELDS})


class TestMoneyDressesAtMod12(unittest.TestCase):
    def test_money_name_dresses_fail(self):
        for entry in MONEY_DRESSES:
            self.assertFalse(
                mod12.validate_run_record(run_record(entry)), entry)

    def test_shape_dresses_fail(self):
        for shape in SHAPE_DRESSES:
            entry = {"stake": dict(shape)}
            self.assertFalse(
                mod12.validate_run_record(run_record(entry)), entry)

    def test_separator_dresses_still_fail(self):
        for entry in ({"real/money/value": 5}, {"real:money:value": 5},
                      {"real.money.value": 5}, {"real money value": 5}):
            self.assertFalse(
                mod12.validate_run_record(run_record(entry)), entry)

    def test_controls_hold(self):
        self.assertTrue(mod12.validate_run_record(run_record()))
        self.assertFalse(mod12.validate_run_record(
            run_record({_MONEY_PLAIN: 5})))
        self.assertTrue(mod12.validate_run_record(
            run_record({_MONEY_PLAIN: None})))
        self.assertTrue(mod12.validate_run_record(
            run_record({"stake": {"amount": 5}})))

    def test_lawful_names_stand(self):
        self.assertTrue(mod12.validate_run_record(
            run_record({"caf\u00e9_label": "stated value"})))
        self.assertTrue(mod12.validate_run_record(run_record(
            {"\u043f\u0440\u0438\u043c\u0435\u0440": "stated value"})))
        self.assertTrue(mod12.validate_run_record(
            run_record({"fie1d_note": "stated value"})))
        self.assertTrue(mod12.validate_run_record(run_record(
            {"stake": {"amount_of_work": 5,
                       "currency_of_record": "stated value"}})))


class TestAnchorDressesAtMod12(unittest.TestCase):
    def test_dressed_name_counts_checked(self):
        for name in ANCHOR_DRESSES:
            self.assertFalse(mod12.validate_run_record(
                run_record({name: {"a", "b", "c", "d"}})), name)
            self.assertFalse(mod12.validate_run_record(
                run_record({name: {"a", "b"}})), name)
            self.assertTrue(mod12.validate_run_record(
                run_record({name: {"a", "b", "c"}})), name)

    def test_exact_name_counts_hold(self):
        self.assertFalse(mod12.validate_run_record(
            run_record({_ANCHOR_PLAIN: {"a", "b", "c", "d"}})))
        self.assertTrue(mod12.validate_run_record(
            run_record({_ANCHOR_PLAIN: {"a", "b", "c"}})))


class StripLieStr(str):
    def strip(self, *args, **kwargs):
        return "ab"


class ValuesLieDict(dict):
    def values(self):
        return ["content"]


class IterLieBytes(bytes):
    def __iter__(self):
        return iter([65])


class IterLieBytearray(bytearray):
    def __iter__(self):
        return iter([65])


class IterLieList(list):
    def __iter__(self):
        return iter(["content"])


class NeLieInt(int):
    def __ne__(self, other):
        return True


class GetLieRegion(dict):
    def get(self, key, default=None):
        if key == "sampled_points":
            return [{"outcome": "holds", "axis_values": {"x": 1}}]
        return dict.get(self, key, default)


class GetLiePoint(dict):
    def get(self, key, default=None):
        if key == "outcome":
            return "holds"
        if key == "axis_values":
            return {"x": 1}
        return dict.get(self, key, default)


class StrLieIdentifier(str):
    def __str__(self):
        return "plain identifier"


class GetLieUnit(dict):
    def get(self, key, default=None):
        return "value for " + str(key)


class TestSubclassPartsAtMod11(unittest.TestCase):
    def test_method_overriding_parts_on_empty_content_refused(self):
        forms = (
            StripLieStr(""),
            ValuesLieDict({"a": ""}),
            IterLieBytes(b""),
            IterLieBytearray(b"\x00"),
            IterLieList([""]),
            NeLieInt(0),
        )
        for value in forms:
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertFalse(mod11.validate_headline_unit(unit), repr(value))
            with self.assertRaises(ValueError):
                mod11.quote_headline_unit(unit)

    def test_region_part_overriding_its_field_reading_refused(self):
        unit = lawful_unit()
        unit["holding_region"] = GetLieRegion({"other": "content"})
        self.assertFalse(mod11.validate_headline_unit(unit))
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_region_point_overriding_its_field_reading_refused(self):
        unit = lawful_unit()
        unit["holding_region"] = {
            "sampled_points": [GetLiePoint()],
            "other": "content",
        }
        self.assertFalse(mod11.validate_headline_unit(unit))
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_identifier_overriding_its_string_reading_refused(self):
        unit = lawful_unit()
        unit["headline_unit_identifier_and_issue_date"] = (
            StrLieIdentifier("unit " + mod11.F01_UNIT_MARK + " 2026"))
        self.assertFalse(mod11.validate_headline_unit(unit))
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_unit_overriding_its_field_access_refused(self):
        unit = GetLieUnit(
            {field: "" for field in mod11.HEADLINE_UNIT_FIELDS})
        self.assertFalse(mod11.validate_headline_unit(unit))
        with self.assertRaises(ValueError):
            mod11.quote_headline_unit(unit)

    def test_lawful_unit_and_plain_subclasses_stand(self):
        class PlainStr(str):
            pass

        class PlainList(list):
            pass

        self.assertTrue(mod11.validate_headline_unit(lawful_unit()))
        for value in (PlainStr("stated content"),
                      PlainList(["stated"]), "stated content", 1):
            unit = lawful_unit()
            unit["assumption_record"] = value
            self.assertTrue(mod11.validate_headline_unit(unit), repr(value))


if __name__ == "__main__":
    unittest.main()

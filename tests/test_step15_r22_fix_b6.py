"""Step 15, second run, fix wave 22, Builder b6 pins.

Group 6, row R22-013: crucible/mod09.py _catalogue_repr, at its
stored mapping reading through vars, standing behind
_stored_form_repr and so behind every cured sentence of rows
R21-029 to R21-037, MOD-09. The helper stands cured so the
stored mapping reading stands guarded against every raising
kind a handed class supplies at that access, in the named
kinds guard form of the neighbouring _safe_repr, and the
rendering delivers its kind form with no bare escape.

Pins whose names carry control stand as the controls, passing
on the pristine tree and on the cured tree alike. Every other
pin stands distinguishing, failing or erroring on the pristine
tree and passing on the cured tree.
"""

import unittest

from crucible import mod09


class EvilVarsRuntime:
    """A handed object whose repr reading answers 5 and whose
    stored mapping access raises RuntimeError, built by
    object.__new__ so no instance mapping stands laid down."""

    def __repr__(self):
        return "5"

    @property
    def __dict__(self):
        raise RuntimeError("stored mapping raises RuntimeError")


class EvilVarsValue:
    """The same form raising ValueError at the stored mapping
    access."""

    def __repr__(self):
        return "5"

    @property
    def __dict__(self):
        raise ValueError("stored mapping raises ValueError")


class PlainObj:
    """A plain object carrying no stored content, whose repr
    reading answers 5."""

    def __repr__(self):
        return "5"


def evil_runtime():
    return object.__new__(EvilVarsRuntime)


def evil_value():
    return object.__new__(EvilVarsValue)


EVILS = (
    (evil_runtime, "EvilVarsRuntime"),
    (evil_value, "EvilVarsValue"),
)

VALID_ARGS = dict(
    strategy_class=["alpha"],
    ladder_position=3,
    catalogue_version_or_hash="v1",
    ladder_definition_pointer="pointer",
    ladder_definition_version="v1",
)


class TestR22013SliceActs(unittest.TestCase):
    def check_named(self, act, kind_name):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            act()
        self.assertIn(kind_name, str(caught.exception))

    def test_direct_helper_runtime(self):
        self.assertEqual(
            mod09._stored_form_repr(evil_runtime()), "EvilVarsRuntime")

    def test_direct_helper_value(self):
        self.assertEqual(
            mod09._stored_form_repr(evil_value()), "EvilVarsValue")

    def test_strategies_form_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.run_record_carriage(
                    strategies=make(), **VALID_ARGS), kind)

    def test_strategies_form_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.run_record_carriage(
                    strategies=make(), **VALID_ARGS), kind)

    def test_ladder_position_runtime(self):
        for make, kind in EVILS[:1]:
            args = dict(VALID_ARGS, ladder_position=make())
            self.check_named(
                lambda: mod09.run_record_carriage(**args), kind)

    def test_ladder_position_value(self):
        for make, kind in EVILS[1:]:
            args = dict(VALID_ARGS, ladder_position=make())
            self.check_named(
                lambda: mod09.run_record_carriage(**args), kind)

    def test_strategy_inside_list_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.run_record_carriage(
                    strategies=[make()], **VALID_ARGS), kind)

    def test_strategy_inside_list_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.run_record_carriage(
                    strategies=[make()], **VALID_ARGS), kind)

    def test_bond_harm_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": make(), "attacker_cost": 2}]), kind)

    def test_bond_harm_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": make(), "attacker_cost": 2}]), kind)

    def test_bond_factor_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"parameter_set": {"a": 1}}],
                    griefing_evaluator=lambda params: make()), kind)

    def test_bond_factor_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"parameter_set": {"a": 1}}],
                    griefing_evaluator=lambda params: make()), kind)

    def test_case_use_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.build_search_record(
                    {}, 1, [], [], case_uses=[make()]), kind)

    def test_case_use_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.build_search_record(
                    {}, 1, [], [], case_uses=[make()]), kind)

    def test_readout_carriage_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.readout({"run_record": make()}), kind)

    def test_readout_carriage_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.readout({"run_record": make()}), kind)

    def test_readout_exercised_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.readout(
                    {"run_record": {"strategies_exercised": make()}}),
                kind)

    def test_readout_exercised_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.readout(
                    {"run_record": {"strategies_exercised": make()}}),
                kind)

    def test_readout_swept_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.readout({
                    "run_record": {"strategies_exercised": []},
                    "external_profit_swept_values": make()}), kind)

    def test_readout_swept_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.readout({
                    "run_record": {"strategies_exercised": []},
                    "external_profit_swept_values": make()}), kind)


class TestR22013Nested(unittest.TestCase):
    def check_named(self, act, kind_name):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            act()
        self.assertIn(kind_name, str(caught.exception))

    def test_nested_list_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": [make()], "attacker_cost": 2}]), kind)

    def test_nested_list_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": [make()], "attacker_cost": 2}]), kind)

    def test_nested_dict_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": {"x": make()}, "attacker_cost": 2}]),
                kind)

    def test_nested_dict_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.bond_search(
                    [{"harm": {"x": make()}, "attacker_cost": 2}]),
                kind)

    def test_nested_set_runtime(self):
        for make, kind in EVILS[:1]:
            self.check_named(
                lambda: mod09.readout({
                    "run_record": {"strategies_exercised": []},
                    "external_profit_swept_values": {make()}}), kind)

    def test_nested_set_value(self):
        for make, kind in EVILS[1:]:
            self.check_named(
                lambda: mod09.readout({
                    "run_record": {"strategies_exercised": []},
                    "external_profit_swept_values": {make()}}), kind)


class TestR22013Controls(unittest.TestCase):
    def test_control_direct_plain_object(self):
        self.assertEqual(
            mod09._stored_form_repr(object.__new__(PlainObj)),
            "PlainObj()")

    def test_control_direct_plain_number(self):
        self.assertEqual(mod09._stored_form_repr(5), "5")

    def test_control_direct_plain_text(self):
        self.assertEqual(mod09._stored_form_repr("x"), "'x'")

    def test_control_direct_object_with_content(self):
        obj = PlainObj()
        obj.marker = "stored-content-xyz"
        self.assertEqual(
            mod09._stored_form_repr(obj),
            "PlainObj(marker='stored-content-xyz')")

    def test_control_carriage_valid(self):
        record = mod09.run_record_carriage(
            strategies=["alpha"], **VALID_ARGS)
        self.assertEqual(record["ladder_position"], 3)
        self.assertEqual(record["strategies_exercised"], ["alpha"])

    def test_control_carriage_plain_strategies_refusal(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.run_record_carriage(strategies=5, **VALID_ARGS)
        self.assertIn("5", str(caught.exception))

    def test_control_bond_plain_scored(self):
        result = mod09.bond_search([{"harm": 4, "attacker_cost": 2}])
        self.assertEqual(result["worst_griefing_factor"], 2.0)

    def test_control_bond_plain_text_harm(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.bond_search([{"harm": "x", "attacker_cost": 2}])
        self.assertIn("'x'", str(caught.exception))

    def test_control_case_use_plain(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.build_search_record({}, 1, [], [], case_uses=[5])
        self.assertIn("5", str(caught.exception))

    def test_control_readout_plain_carriage(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.readout({"run_record": 5})
        self.assertIn("5", str(caught.exception))

    def test_control_readout_valid(self):
        unit = mod09.readout({})
        self.assertEqual(unit["readout_status"], "not at the readout point")
        self.assertEqual(unit["result_kind"], "in protocol result only")

    def test_control_readout_plain_swept(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.readout({
                "run_record": {"strategies_exercised": []},
                "external_profit_swept_values": 5})
        self.assertIn("5", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

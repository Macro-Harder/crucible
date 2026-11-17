"""Step 15, second run, fix wave 23, Builder b3 pins.

Group 3, row R23-004: crucible/mod09.py _catalogue_repr, at its
stored mapping reading through vars, standing behind
_stored_form_repr and so behind every sentence the helper
reaches, MOD-09. The helper stands cured so the stored mapping
reading falls to the kind name on any raising kind a handed
class supplies at that access, the seven named kinds standing
as the minimum covered.

Pins whose names carry control stand as the controls, passing
on the pristine tree and on the cured tree alike. Every other
pin stands distinguishing, failing on the pristine tree and
passing on the cured tree. Distinguishing acts catch
BaseException inside the pin and assert on the outcome, so a
bare escape of any kind, KeyboardInterrupt and SystemExit
included, stands as a pin failure and never as a runner abort.
"""

import unittest

from crucible import mod09


class CustomKind(Exception):
    """A custom Exception subclass of this pin file."""


def make_evil(class_name, exc):
    """Build a handed class whose __dict__ property raises exc,
    its repr reading answering 5, in the b6 pin construction
    form. Instances stand built by object.__new__ so no
    instance mapping stands laid down."""

    def raise_it(self, _exc=exc):
        raise _exc("stored mapping raises")

    return type(class_name, (), {
        "__repr__": lambda self: "5",
        "__dict__": property(raise_it),
    })


BEYOND_SEVEN = (
    ("EvilIndex", IndexError),
    ("EvilZeroDivision", ZeroDivisionError),
    ("EvilLookup", LookupError),
    ("EvilArithmetic", ArithmeticError),
    ("EvilName", NameError),
    ("EvilStopIteration", StopIteration),
    ("EvilImport", ImportError),
    ("EvilAssertion", AssertionError),
    ("EvilEOF", EOFError),
    ("EvilMemory", MemoryError),
    ("EvilCustom", CustomKind),
    ("EvilKeyboardInterrupt", KeyboardInterrupt),
    ("EvilSystemExit", SystemExit),
)

SEVEN_NAMED = (
    ("NamedType", TypeError),
    ("NamedRuntime", RuntimeError),
    ("NamedValue", ValueError),
    ("NamedAttribute", AttributeError),
    ("NamedOverflow", OverflowError),
    ("NamedKey", KeyError),
    ("NamedOS", OSError),
)

INHERITING = (
    ("InheritRecursion", RecursionError),
    ("InheritNotImplemented", NotImplementedError),
    ("InheritPermission", PermissionError),
    ("InheritUnicode", UnicodeError),
)

EVIL_CLASSES = {
    name: make_evil(name, exc) for name, exc in BEYOND_SEVEN}
NAMED_CLASSES = {
    name: make_evil(name, exc) for name, exc in SEVEN_NAMED}
INHERIT_CLASSES = {
    name: make_evil(name, exc) for name, exc in INHERITING}


def evil(name):
    return object.__new__(EVIL_CLASSES[name])


class PlainObj:
    """A plain object whose repr reading answers 5."""

    def __repr__(self):
        return "5"


VALID_ARGS = dict(
    strategy_class=["alpha"],
    ladder_position=3,
    catalogue_version_or_hash="v1",
    ladder_definition_pointer="pointer",
    ladder_definition_version="v1",
)


def attempt(act):
    """Run one act, returning (True, value) where it stands
    delivered and (False, kind name) where any kind escapes
    bare, BaseException kinds included."""
    try:
        return (True, act())
    except BaseException as escaped:
        return (False, type(escaped).__name__)


def named_attempt(act):
    """Run one gate act, returning (True, sentence) where the
    named refusal stands delivered and (False, kind name)
    where any other kind escapes bare."""
    try:
        act()
    except mod09.NamedAttackerFailure as failure:
        return (True, str(failure))
    except BaseException as escaped:
        return (False, type(escaped).__name__)
    return (False, "no refusal delivered")


class TestR23004Direct(unittest.TestCase):
    pass


def _direct_pin(name):
    def pin(self):
        delivered, value = attempt(
            lambda: mod09._stored_form_repr(evil(name)))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertEqual(value, name)
    return pin


for _name, _exc in BEYOND_SEVEN:
    setattr(TestR23004Direct, "test_direct_%s" % _name,
            _direct_pin(_name))


class TestR23004Gates(unittest.TestCase):
    def check_gate(self, act, class_name):
        delivered, value = named_attempt(act)
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(class_name, value)


def _carriage_strategies_pin(name):
    def pin(self):
        self.check_gate(
            lambda: mod09.run_record_carriage(
                strategies=evil(name), **VALID_ARGS), name)
    return pin


for _name, _exc in BEYOND_SEVEN:
    setattr(TestR23004Gates,
            "test_carriage_strategies_%s" % _name,
            _carriage_strategies_pin(_name))


class TestR23004GatePositions(unittest.TestCase):
    def check_gate(self, act, class_name):
        delivered, value = named_attempt(act)
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(class_name, value)

    def test_carriage_ladder_index(self):
        args = dict(VALID_ARGS, ladder_position=evil("EvilIndex"))
        self.check_gate(
            lambda: mod09.run_record_carriage(**args), "EvilIndex")

    def test_carriage_ladder_custom(self):
        args = dict(VALID_ARGS, ladder_position=evil("EvilCustom"))
        self.check_gate(
            lambda: mod09.run_record_carriage(**args), "EvilCustom")

    def test_carriage_inside_list_index(self):
        self.check_gate(
            lambda: mod09.run_record_carriage(
                strategies=[evil("EvilIndex")], **VALID_ARGS),
            "EvilIndex")

    def test_carriage_inside_list_zero_division(self):
        self.check_gate(
            lambda: mod09.run_record_carriage(
                strategies=[evil("EvilZeroDivision")], **VALID_ARGS),
            "EvilZeroDivision")

    def test_bond_harm_index(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": evil("EvilIndex"), "attacker_cost": 2}]),
            "EvilIndex")

    def test_bond_harm_zero_division(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": evil("EvilZeroDivision"),
                  "attacker_cost": 2}]),
            "EvilZeroDivision")

    def test_bond_harm_custom(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": evil("EvilCustom"), "attacker_cost": 2}]),
            "EvilCustom")

    def test_bond_harm_keyboard_interrupt(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": evil("EvilKeyboardInterrupt"),
                  "attacker_cost": 2}]),
            "EvilKeyboardInterrupt")

    def test_readout_carriage_index(self):
        self.check_gate(
            lambda: mod09.readout(
                {"run_record": evil("EvilIndex")}), "EvilIndex")

    def test_readout_carriage_zero_division(self):
        self.check_gate(
            lambda: mod09.readout(
                {"run_record": evil("EvilZeroDivision")}),
            "EvilZeroDivision")

    def test_readout_carriage_custom(self):
        self.check_gate(
            lambda: mod09.readout(
                {"run_record": evil("EvilCustom")}), "EvilCustom")

    def test_readout_carriage_system_exit(self):
        self.check_gate(
            lambda: mod09.readout(
                {"run_record": evil("EvilSystemExit")}),
            "EvilSystemExit")

    def test_readout_swept_index(self):
        self.check_gate(
            lambda: mod09.readout({
                "run_record": {"strategies_exercised": []},
                "external_profit_swept_values": evil("EvilIndex")}),
            "EvilIndex")

    def test_readout_swept_custom(self):
        self.check_gate(
            lambda: mod09.readout({
                "run_record": {"strategies_exercised": []},
                "external_profit_swept_values": evil("EvilCustom")}),
            "EvilCustom")

    def test_catalogue_inside_set_index(self):
        handed = evil("EvilIndex")
        delivered, value = attempt(
            lambda: mod09.strategy_catalogue({handed}))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(handed, value["identifiers"])

    def test_catalogue_inside_set_custom(self):
        handed = evil("EvilCustom")
        delivered, value = attempt(
            lambda: mod09.strategy_catalogue({handed}))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(handed, value["identifiers"])

    def test_catalogue_inside_set_system_exit(self):
        handed = evil("EvilSystemExit")
        delivered, value = attempt(
            lambda: mod09.strategy_catalogue({handed}))
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(handed, value["identifiers"])


class TestR23004Nested(unittest.TestCase):
    def check_render(self, act, class_name):
        delivered, value = attempt(act)
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(class_name, value)

    def check_gate(self, act, class_name):
        delivered, value = named_attempt(act)
        self.assertTrue(delivered, "bare escape: %s" % value)
        self.assertIn(class_name, value)

    def test_nested_list_helper_index(self):
        self.check_render(
            lambda: mod09._stored_form_repr([evil("EvilIndex")]),
            "EvilIndex")

    def test_nested_list_helper_custom(self):
        self.check_render(
            lambda: mod09._stored_form_repr([evil("EvilCustom")]),
            "EvilCustom")

    def test_nested_dict_helper_index(self):
        self.check_render(
            lambda: mod09._stored_form_repr(
                {"x": evil("EvilIndex")}), "EvilIndex")

    def test_nested_dict_helper_custom(self):
        self.check_render(
            lambda: mod09._stored_form_repr(
                {"x": evil("EvilCustom")}), "EvilCustom")

    def test_nested_set_helper_index(self):
        self.check_render(
            lambda: mod09._stored_form_repr({evil("EvilIndex")}),
            "EvilIndex")

    def test_nested_set_helper_custom(self):
        self.check_render(
            lambda: mod09._stored_form_repr({evil("EvilCustom")}),
            "EvilCustom")

    def test_nested_holder_mapping_index(self):
        holder = PlainObj()
        holder.part = evil("EvilIndex")
        self.check_render(
            lambda: mod09._stored_form_repr(holder), "EvilIndex")

    def test_nested_holder_mapping_system_exit(self):
        holder = PlainObj()
        holder.part = evil("EvilSystemExit")
        self.check_render(
            lambda: mod09._stored_form_repr(holder), "EvilSystemExit")

    def test_nested_list_bond_index(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": [evil("EvilIndex")], "attacker_cost": 2}]),
            "EvilIndex")

    def test_nested_dict_bond_index(self):
        self.check_gate(
            lambda: mod09.bond_search(
                [{"harm": {"x": evil("EvilIndex")},
                  "attacker_cost": 2}]),
            "EvilIndex")

    def test_nested_set_readout_index(self):
        self.check_gate(
            lambda: mod09.readout({
                "run_record": {"strategies_exercised": []},
                "external_profit_swept_values": {evil("EvilIndex")}}),
            "EvilIndex")


class TestR23004Controls(unittest.TestCase):
    def test_control_direct_plain_object(self):
        self.assertEqual(
            mod09._stored_form_repr(object.__new__(PlainObj)),
            "PlainObj()")

    def test_control_direct_object_with_content(self):
        obj = PlainObj()
        obj.marker = "stored-content-xyz"
        self.assertEqual(
            mod09._stored_form_repr(obj),
            "PlainObj(marker='stored-content-xyz')")

    def test_control_direct_plain_number(self):
        self.assertEqual(mod09._stored_form_repr(5), "5")

    def test_control_direct_plain_text(self):
        self.assertEqual(mod09._stored_form_repr("x"), "'x'")

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

    def test_control_readout_plain_carriage(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.readout({"run_record": 5})
        self.assertIn("5", str(caught.exception))

    def test_control_readout_valid(self):
        unit = mod09.readout({})
        self.assertEqual(
            unit["readout_status"], "not at the readout point")
        self.assertEqual(
            unit["result_kind"], "in protocol result only")


def _control_named_pin(name):
    def pin(self):
        self.assertEqual(
            mod09._stored_form_repr(object.__new__(NAMED_CLASSES[name])),
            name)
    return pin


for _name, _exc in SEVEN_NAMED:
    setattr(TestR23004Controls, "test_control_named_%s" % _name,
            _control_named_pin(_name))


def _control_inherit_pin(name):
    def pin(self):
        self.assertEqual(
            mod09._stored_form_repr(
                object.__new__(INHERIT_CLASSES[name])),
            name)
    return pin


for _name, _exc in INHERITING:
    setattr(TestR23004Controls, "test_control_inherit_%s" % _name,
            _control_inherit_pin(_name))


if __name__ == "__main__":
    unittest.main()

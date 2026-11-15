"""Pins for Round 13 rows R13-028 to R13-032.

The MOD-02 next ring: the _base_name_eq handed equality, the
_stream_set_classes hash guard and repr limbs, the _position_value
conversions, and make_derivation_input. Each test pins the defect
its row states with the proving acts the source paper used, beside
the plain controls that paper ran.
"""
import unittest
from decimal import Decimal

from crucible import mod02


class EqAll:
    """Stores no class name, answers True to every equality."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class HashOSError:
    """Its hash reading raises OSError."""

    def __hash__(self):
        raise OSError("hash boom")


class HashKeyError:
    """Its hash reading raises KeyError."""

    def __hash__(self):
        raise KeyError("hash boom")


class HashRuntimeError:
    """Its hash reading raises RuntimeError."""

    def __hash__(self):
        raise RuntimeError("hash boom")


class HashRuntimeReprRuntime:
    """Its hash reading and its repr reading both raise."""

    def __hash__(self):
        raise RuntimeError("hash boom")

    def __repr__(self):
        raise RuntimeError("repr boom")


class HashTypePlain:
    """Its hash reading raises TypeError, its repr stands plain."""

    def __hash__(self):
        raise TypeError("hash boom")


class StrReprRaises(str):
    """Stores text, its repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class StrKeyRaises:
    """Its string reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("str boom")

    __hash__ = object.__hash__


class HashRaisesName:
    """Its hash reading raises RuntimeError."""

    def __hash__(self):
        raise RuntimeError("hash boom")


def _cardinality(counts, inventory):
    return mod02.validate_stream_cardinality(
        counts=counts,
        stream_set={"stream_class_inventory": inventory})


class TestR13028BaseNameEq(unittest.TestCase):
    def test_eqall_counts_key_does_not_validate_against_int_class(self):
        self.assertTrue(_cardinality({5: 1}, [5]))
        self.assertFalse(_cardinality({EqAll(): 1}, [5]))

    def test_eqall_inventory_class_does_not_match_plain_count(self):
        self.assertTrue(_cardinality({"cls1": 1}, ["cls1"]))
        self.assertFalse(_cardinality({5: 1}, [EqAll()]))

    def test_distinct_eqall_instances_do_not_match(self):
        self.assertTrue(_cardinality({"cls1": 1}, ["cls1"]))
        self.assertFalse(_cardinality({EqAll(): 1}, [EqAll()]))
        self.assertFalse(_cardinality({"cls1": 1}, [5]))


class TestR13029StreamSetHashGuard(unittest.TestCase):
    def test_hash_oserror_restated_as_value_error(self):
        with self.assertRaises(ValueError):
            _cardinality({"a": 1}, [HashRuntimeError()])
        with self.assertRaises(ValueError):
            _cardinality({"a": 1}, [["unhashable"]])
        with self.assertRaises(ValueError):
            _cardinality({"a": 1}, [HashOSError()])

    def test_hash_keyerror_restated_as_named_value_error(self):
        with self.assertRaises(ValueError) as caught:
            _cardinality({"a": 1}, [HashKeyError()])
        self.assertIn("stream class entry stands in no stated form",
                      str(caught.exception))


class TestR13030StreamSetReprLimbs(unittest.TestCase):
    def test_hash_and_repr_both_raise_runtime(self):
        with self.assertRaises(ValueError):
            _cardinality({"a": 1}, [HashRuntimeReprRuntime()])

    def test_repr_raising_string_inventory(self):
        with self.assertRaises(ValueError):
            _cardinality({"a": 1}, "plain inventory text")
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                counts={"a": 1},
                stream_set={"stream_class_inventory":
                            StrReprRaises("ghost")})

    def test_hash_typeerror_refusal_text_carries_no_address(self):
        texts = []
        for _ in range(2):
            with self.assertRaises(ValueError) as caught:
                _cardinality({"a": 1}, [HashTypePlain()])
            texts.append(str(caught.exception))
        self.assertNotIn("0x", texts[0])
        self.assertEqual(texts[0], texts[1])

    def test_nameless_entry_dict_refusal_text_carries_no_address(self):
        texts = []
        for _ in range(2):
            with self.assertRaises(ValueError) as caught:
                _cardinality({"a": 1}, [{"other": object()}])
            texts.append(str(caught.exception))
        self.assertNotIn("0x", texts[0])
        self.assertEqual(texts[0], texts[1])


class TestR13031PositionValue(unittest.TestCase):
    def test_draw_position_infinity_value_error(self):
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=float("nan"),
                carried_positions=10)
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=float("inf"),
                carried_positions=10)
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=Decimal("Infinity"),
                carried_positions=10)

    def test_draw_carried_infinity_value_error(self):
        exhausted = mod02.draw_from_stream(
            stream_class="s", position=99, carried_positions=10)
        self.assertEqual(exhausted["failure"], "STREAM-EXHAUSTED")
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=0,
                carried_positions=float("inf"))

    def test_initial_carried_infinity_value_error(self):
        with self.assertRaises(ValueError):
            mod02._position_value(float("inf"))
        with self.assertRaises(ValueError):
            mod02.initial_stream_state("s", float("inf"))

    def test_initial_complex_value_error_and_draw_complex_control(self):
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=complex(1, 2),
                carried_positions=10)
        with self.assertRaises(ValueError):
            mod02.initial_stream_state("s", complex(1, 2))


class TestR13032MakeDerivationInput(unittest.TestCase):
    def test_str_raising_key_non_text_value_value_error(self):
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values={"p": 123})
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values={StrKeyRaises(): 123})

    def test_unhashable_pair_name_value_error(self):
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values=[123])
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values=[("a", "1", "extra")])
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values=[(["x"], "1")])

    def test_hash_raising_pair_name_value_error(self):
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values=[("q", "2")])
        self.assertEqual(built["parameter_values"], {"q": "2"})
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values=[(HashRaisesName(), "1")])


if __name__ == "__main__":
    unittest.main()

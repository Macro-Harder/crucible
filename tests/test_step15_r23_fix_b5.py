"""Step 15, second run, fix wave 23, Builder b5 pins.

Group 5, row R23-007: crucible/mod11.py _form_repr, at its stored
mapping reading through vars, MOD-11. The helper stands cured so
the stored mapping reading falls to the kind name on any raising
kind, in the breadth the MOD-14 control stands in, restating the
guard to the cured MOD-09 companion form as Ruling 4 settles it,
the seven named kinds standing as the minimum covered.

Pins whose names carry control stand as the controls, passing
on the pristine tree and on the cured tree alike. Every other
pin stands distinguishing, failing or erroring on the pristine
tree and passing on the cured tree.
"""

import unittest

from crucible import mod11


def make_evil(kind_name, exc):
    cls = type(kind_name, (), {
        "__repr__": lambda self: "5",
        "__dict__": property(
            lambda self: (_ for _ in ()).throw(exc)),
    })
    return object.__new__(cls)


def evil_runtime():
    return make_evil(
        "EvilVarsRuntime",
        RuntimeError("stored mapping raises RuntimeError"))


def evil_value():
    return make_evil(
        "EvilVarsValue",
        ValueError("stored mapping raises ValueError"))


def evil_type():
    return make_evil(
        "EvilVarsType",
        TypeError("stored mapping raises TypeError"))


class PlainObj:
    def __repr__(self):
        return "5"


class Holder:
    pass


class TestR23007Helper(unittest.TestCase):
    def test_direct_runtime(self):
        self.assertEqual(
            mod11._form_repr(evil_runtime()), "EvilVarsRuntime")

    def test_direct_value(self):
        self.assertEqual(
            mod11._form_repr(evil_value()), "EvilVarsValue")

    def test_nested_list_runtime(self):
        self.assertEqual(
            mod11._form_repr([evil_runtime()]),
            "[EvilVarsRuntime]")

    def test_nested_list_value(self):
        self.assertEqual(
            mod11._form_repr([evil_value()]), "[EvilVarsValue]")

    def test_nested_dict_value_runtime(self):
        self.assertEqual(
            mod11._form_repr({"k": evil_runtime()}),
            "{'k': EvilVarsRuntime}")

    def test_nested_dict_value_value(self):
        self.assertEqual(
            mod11._form_repr({"k": evil_value()}),
            "{'k': EvilVarsValue}")

    def test_helper_overflow_error(self):
        evil = make_evil(
            "EvilVarsOverflow",
            OverflowError("stored mapping raises OverflowError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsOverflow")

    def test_helper_key_error(self):
        evil = make_evil(
            "EvilVarsKey", KeyError("stored mapping raises KeyError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsKey")

    def test_helper_os_error(self):
        evil = make_evil(
            "EvilVarsOs", OSError("stored mapping raises OSError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsOs")

    def test_helper_beyond_seven_index_error(self):
        evil = make_evil(
            "EvilVarsIndex",
            IndexError("stored mapping raises IndexError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsIndex")


class TestR23007Gates(unittest.TestCase):
    def test_region_shift_runtime(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps(evil_runtime(), (1, 2))
        self.assertIn("EvilVarsRuntime", str(caught.exception))

    def test_region_shift_value(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps((1, 2), evil_value())
        self.assertIn("EvilVarsValue", str(caught.exception))

    def test_weekly_container_runtime(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("w1", [evil_runtime()])
        self.assertIn("EvilVarsRuntime", str(caught.exception))

    def test_weekly_container_value(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("w1", [evil_value()])
        self.assertIn("EvilVarsValue", str(caught.exception))


class TestR23007Controls(unittest.TestCase):
    def test_control_attribute_error_by_kind_name(self):
        evil = make_evil(
            "EvilVarsAttribute",
            AttributeError("stored mapping raises AttributeError"))
        self.assertEqual(mod11._form_repr(evil), "EvilVarsAttribute")

    def test_control_type_error_by_kind_name(self):
        self.assertEqual(
            mod11._form_repr(evil_type()), "EvilVarsType")

    def test_control_plain_no_stored_content(self):
        self.assertEqual(mod11._form_repr(PlainObj()), "PlainObj()")

    def test_control_plain_with_stored_content(self):
        holder = Holder()
        holder.plain = "abc"
        holder.num = 3
        self.assertEqual(
            mod11._form_repr(holder), "Holder(num=3, plain='abc')")


if __name__ == "__main__":
    unittest.main()

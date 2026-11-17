"""Step 15, second run, fix wave 24, Builder b2 pins.

Row R24-003: crucible/mod11.py, at the gates region_shift_steps,
make_weekly_container, and weekly_count, bounded to the gate
form, MOD-11. At those three gates, whose stated forms promise
named ValueError refusals built through _form_repr, a handed
value whose stored mapping reading raises KeyboardInterrupt or
SystemExit escapes bare on the pristine tree, so the promised
refusal stands never delivered. The cure stands at the gate
form alone: each gate delivers its promised named ValueError
refusal whole on those dresses, carrying the kind name form,
and _form_repr itself stands unedited.

The distinguishing pins catch BaseException inside the pin
itself and assert on the delivered exception, so a bare escape
on the pristine tree stands as a plain pin failure and never
as a runner abort. Pins whose names carry control stand as
the controls, passing on the pristine tree and on the cured
tree alike. Every other pin stands distinguishing, failing
on the pristine tree and passing on the cured tree.
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


def evil_keyboard():
    return make_evil(
        "EvilVarsKeyboard",
        KeyboardInterrupt("stored mapping raises KeyboardInterrupt"))


def evil_system_exit():
    return make_evil(
        "EvilVarsSystemExit",
        SystemExit("stored mapping raises SystemExit"))


def evil_runtime():
    return make_evil(
        "EvilVarsRuntime",
        RuntimeError("stored mapping raises RuntimeError"))


def evil_value():
    return make_evil(
        "EvilVarsValue",
        ValueError("stored mapping raises ValueError"))


def weekly_record(identifier):
    return [{
        "week": "2026-W01",
        "headline_unit_identifiers": [identifier],
    }]


def delivered(call):
    try:
        call()
    except BaseException as exc:
        return exc
    return None


class TestR24003RegionShiftSteps(unittest.TestCase):
    def check(self, call, kind_name, extra=None):
        exc = delivered(call)
        self.assertIsInstance(exc, ValueError)
        self.assertIn(kind_name, str(exc))
        if extra is not None:
            self.assertIn(extra, str(exc))

    def test_region_a_keyboard(self):
        self.check(
            lambda: mod11.region_shift_steps(
                evil_keyboard(), (1, 2)),
            "EvilVarsKeyboard",
            "a location must stand as a pair of grid numbers")

    def test_region_a_system_exit(self):
        self.check(
            lambda: mod11.region_shift_steps(
                evil_system_exit(), (1, 2)),
            "EvilVarsSystemExit")

    def test_region_b_keyboard(self):
        self.check(
            lambda: mod11.region_shift_steps(
                (1, 2), evil_keyboard()),
            "EvilVarsKeyboard")

    def test_region_b_system_exit(self):
        self.check(
            lambda: mod11.region_shift_steps(
                (1, 2), evil_system_exit()),
            "EvilVarsSystemExit")


class TestR24003MakeWeeklyContainer(unittest.TestCase):
    def test_container_keyboard(self):
        exc = delivered(
            lambda: mod11.make_weekly_container(
                "w1", [evil_keyboard()]))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsKeyboard", str(exc))
        self.assertIn(
            "a held item stands in no unit identifier form",
            str(exc))

    def test_container_system_exit(self):
        exc = delivered(
            lambda: mod11.make_weekly_container(
                "w1", [evil_system_exit()]))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsSystemExit", str(exc))


class TestR24003WeeklyCount(unittest.TestCase):
    def test_weekly_count_keyboard(self):
        exc = delivered(
            lambda: mod11.weekly_count(
                weekly_record(evil_keyboard()), "2026-W01"))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsKeyboard", str(exc))
        self.assertIn(
            "identifier standing in no unit identifier form",
            str(exc))

    def test_weekly_count_system_exit(self):
        exc = delivered(
            lambda: mod11.weekly_count(
                weekly_record(evil_system_exit()), "2026-W01"))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsSystemExit", str(exc))


class TestR24003Controls(unittest.TestCase):
    def test_control_region_runtime(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps(evil_runtime(), (1, 2))
        self.assertIn("EvilVarsRuntime", str(caught.exception))

    def test_control_region_value(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps((1, 2), evil_value())
        self.assertIn("EvilVarsValue", str(caught.exception))

    def test_control_container_runtime(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("w1", [evil_runtime()])
        self.assertIn("EvilVarsRuntime", str(caught.exception))

    def test_control_container_value(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("w1", [evil_value()])
        self.assertIn("EvilVarsValue", str(caught.exception))

    def test_control_weekly_count_runtime(self):
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(
                weekly_record(evil_runtime()), "2026-W01")
        self.assertIn("EvilVarsRuntime", str(caught.exception))

    def test_control_weekly_count_value(self):
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(
                weekly_record(evil_value()), "2026-W01")
        self.assertIn("EvilVarsValue", str(caught.exception))

    def test_control_region_plain_bad_location(self):
        with self.assertRaises(ValueError) as caught:
            mod11.region_shift_steps("xy", (1, 2))
        self.assertIn("'xy'", str(caught.exception))

    def test_control_container_plain_object(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_weekly_container("w1", [object()])
        self.assertIn("object", str(caught.exception))

    def test_control_weekly_count_plain_object(self):
        with self.assertRaises(ValueError) as caught:
            mod11.weekly_count(
                weekly_record(object()), "2026-W01")
        self.assertIn("object", str(caught.exception))

    def test_control_region_valid_shift(self):
        self.assertEqual(
            mod11.region_shift_steps((0, 0), (1, 2)), (1, 2))

    def test_control_container_valid_unit(self):
        container = mod11.make_weekly_container("w1", ["u1"])
        self.assertEqual(container["count"], 1)

    def test_control_weekly_count_valid(self):
        self.assertEqual(
            mod11.weekly_count(
                weekly_record("u1"), "2026-W01"), 1)

    def test_control_helper_keyboard_stands_bare(self):
        with self.assertRaises(KeyboardInterrupt):
            mod11._form_repr(evil_keyboard())

    def test_control_helper_system_exit_stands_bare(self):
        with self.assertRaises(SystemExit):
            mod11._form_repr(evil_system_exit())


if __name__ == "__main__":
    unittest.main()

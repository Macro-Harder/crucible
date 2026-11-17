"""Step 15, second run, fix wave 25, Builder b1 pins.

Row R25-001: crucible/mod11.py transition_wording, at its
fallback pair reading, MOD-11. transition_wording catches the
named ValueError that region_shift_steps delivers and retries
the pair reading through _grid_pair direct with its own act
name. On a handed location whose stored mapping reading
raises KeyboardInterrupt or SystemExit, that direct call
renders the location through _form_repr inside its own
refusal construction and the BaseException kind escapes
bare, so the named transition_wording refusal stands never
delivered. The IndexError dress at the same handing delivers
the named refusal whole. The cure stands at the fallback pair
reading alone: the fallback delivers its named refusal whole
on those dresses, and _grid_pair and _form_repr themselves
take no edit.

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


def evil_index_error():
    return make_evil(
        "EvilVarsIndexError",
        IndexError("stored mapping raises IndexError"))


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


class TestR25001TransitionFallback(unittest.TestCase):
    def check_refusal(self, call, kind_name):
        exc = delivered(call)
        self.assertIsInstance(exc, ValueError)
        self.assertIn(
            "transition_wording stands refused", str(exc))
        self.assertIn(
            "a location must stand as a pair of grid numbers",
            str(exc))
        self.assertIn(kind_name, str(exc))
        self.assertIn("stands in no such form", str(exc))

    def test_transition_a_keyboard(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                evil_keyboard(), (1, 0)),
            "EvilVarsKeyboard")

    def test_transition_a_system_exit(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                evil_system_exit(), (1, 0)),
            "EvilVarsSystemExit")

    def test_transition_b_keyboard(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                (0, 0), evil_keyboard()),
            "EvilVarsKeyboard")

    def test_transition_b_system_exit(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                (0, 0), evil_system_exit()),
            "EvilVarsSystemExit")

    def test_transition_nested_list_keyboard(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                [evil_keyboard(), 0], (1, 0)),
            "list")

    def test_transition_nested_list_system_exit(self):
        self.check_refusal(
            lambda: mod11.transition_wording(
                (0, 0), [evil_system_exit(), 0]),
            "list")


class TestR25001Controls(unittest.TestCase):
    def test_control_plain_holding_pair(self):
        result = mod11.transition_wording((0, 0), (1, 0))
        self.assertEqual(result["wording"], "holding")
        self.assertTrue(result["holding_statement"])

    def test_control_plain_crossover_pair(self):
        result = mod11.transition_wording((0, 0), (5, 0))
        self.assertEqual(
            result["wording"], "finite population crossover")
        self.assertFalse(result["holding_statement"])

    def test_control_plain_bad_location_refusal(self):
        exc = delivered(
            lambda: mod11.transition_wording("xy", (1, 0)))
        self.assertIsInstance(exc, ValueError)
        self.assertIn(
            "transition_wording stands refused", str(exc))
        self.assertIn("'xy'", str(exc))

    def test_control_index_error_a_refusal(self):
        exc = delivered(
            lambda: mod11.transition_wording(
                evil_index_error(), (1, 0)))
        self.assertIsInstance(exc, ValueError)
        self.assertIn(
            "transition_wording stands refused", str(exc))
        self.assertIn("EvilVarsIndexError", str(exc))

    def test_control_index_error_b_refusal(self):
        exc = delivered(
            lambda: mod11.transition_wording(
                (0, 0), evil_index_error()))
        self.assertIsInstance(exc, ValueError)
        self.assertIn(
            "transition_wording stands refused", str(exc))
        self.assertIn("EvilVarsIndexError", str(exc))

    def test_control_region_gate_keyboard_standing(self):
        exc = delivered(
            lambda: mod11.region_shift_steps(
                evil_keyboard(), (1, 2)))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsKeyboard", str(exc))
        self.assertIn(
            "region_shift_steps stands refused", str(exc))

    def test_control_container_gate_keyboard_standing(self):
        exc = delivered(
            lambda: mod11.make_weekly_container(
                "w1", [evil_keyboard()]))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsKeyboard", str(exc))

    def test_control_weekly_count_gate_system_exit_standing(self):
        exc = delivered(
            lambda: mod11.weekly_count(
                weekly_record(evil_system_exit()), "2026-W01"))
        self.assertIsInstance(exc, ValueError)
        self.assertIn("EvilVarsSystemExit", str(exc))

    def test_control_helper_keyboard_stands_bare(self):
        with self.assertRaises(KeyboardInterrupt):
            mod11._form_repr(evil_keyboard())

    def test_control_helper_system_exit_stands_bare(self):
        with self.assertRaises(SystemExit):
            mod11._form_repr(evil_system_exit())

    def test_control_grid_pair_direct_keyboard_stands_bare(self):
        with self.assertRaises(KeyboardInterrupt):
            mod11._grid_pair(
                evil_keyboard(), "transition_wording")


if __name__ == "__main__":
    unittest.main()

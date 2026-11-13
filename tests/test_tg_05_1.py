"""Test group TG-05.1, slice S-05, MOD-06 Escrow Core.

Suite form: Python standard library unittest, one file per test group.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each test body first requires the product surface: while the surface
is absent the test fails, naming the pinned behaviour and its group.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only. No real money stake
behaviour stands in any fixture, branch or variable in this file.
"""
import unittest

try:
    from crucible import mod06 as _mod
    SURFACE = True
    SURFACE_ERROR = ""
except Exception as exc:
    _mod = None
    SURFACE = False
    SURFACE_ERROR = str(exc)


class TestTG051(unittest.TestCase):
    def require_surface(self, behaviour):
        if not SURFACE:
            self.fail(
                "Surface absent for TG-05.1: pinned behaviour not testable: "
                + behaviour + " (import error: " + SURFACE_ERROR + ")"
            )

    def test_qualifier_true_on_every_escrow_result(self):
        """
        Fixture: one result of each escrow bearing kind the core can produce, as TG-05.1 states
        Pins: the core only qualifier reads true for every escrow bearing result, in the form operation C-23 states for comparison arms and decision D-02 states for the centre
        Bar: silence on this check counts as fail, never as not applicable, in the same form as retirement check T-08 at fixture F-01
        Failure: a result with the qualifier absent or reading other than true fails this test; while the surface is absent the test fails naming this behaviour and TG-05.1
        """
        self.require_surface("core only qualifier reads true on every escrow bearing result")
        for kind in ("deposit", "withdraw_unliened", "open_request", "contract state"):
            result = _mod.escrow_result(kind)
            self.assertIs(result["core_only_qualifier"], True)
            self.assertTrue(_mod.validate_escrow_result(result))
            self.assertEqual(result["verification_limit"], _mod.VERIFICATION_LIMIT)
            self.assertIsNone(result["real_money_value"])

    def test_result_without_qualifier_is_not_reportable(self):
        """
        Fixture: one escrow bearing result with the core only qualifier removed
        Pins: a result carrying no core only qualifier is not reportable as an escrow result
        Bar: no escrow result stands without the qualifier, per the guard at plan section 2 section 8 item 6(d)
        Failure: a result without the qualifier that validates or is reported fails this test; while the surface is absent the test fails naming this behaviour and TG-05.1
        """
        self.require_surface("escrow result without the core only qualifier is rejected")
        self.require_surface("escrow result without the core only qualifier is rejected")
        result = _mod.escrow_result("deposit")
        stripped = dict(result)
        del stripped["core_only_qualifier"]
        self.assertFalse(_mod.validate_escrow_result(stripped))
        lowered = dict(result)
        lowered["core_only_qualifier"] = False
        self.assertFalse(_mod.validate_escrow_result(lowered))


if __name__ == "__main__":
    unittest.main()

"""Step 17 fix wave 5, Slice 8 defect tests, row FW5-10.

The too few arguments family at fresh doors: each act named in
the filings, called with too few arguments or with none, stands
refused in the named form of its module, stating the door, the
ground, and the next step, in the form the FW4-11 cure states
at its cured acts, instead of escaping as a bare interpreter
TypeError stating only that a required positional argument
stands missing.

Filing seats: Purple 2 P2-01 (mod13 replay_check); Orange 2
S17R4-O2-02 (mod14 run_command, mod14 pilot_run, mod12
seal_family_record, mod16 fixture_record); Orange 5 S17R4-O5-02
(mod05 proportion_record, mod05 work_credit, mod05
band_membership, mod06 escrow_result, mod08 score, mod11
make_headline_unit, mod13 replay_check).

Python standard library only.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod05
from crucible import mod06
from crucible import mod08
from crucible import mod11
from crucible import mod12
from crucible import mod13
from crucible import mod14
from crucible import mod16


def check_named(case, exc_type, call, door, consequence):
    """One too few arguments handing refuses in named form."""
    with case.assertRaises(exc_type) as caught:
        call()
    message = str(caught.exception)
    case.assertIn(door, message)
    case.assertIn("missing", message)
    case.assertIn("next step", message.lower())
    case.assertIn(consequence, message)
    case.assertNotIn("required positional argument", message)
    return message


class TestFW510Mod05(unittest.TestCase):

    def test_defect_proportion_record_no_args(self):
        check_named(
            self, ValueError, lambda: mod05.proportion_record(),
            "proportion_record", "no proportion stands stored")

    def test_defect_proportion_record_one_arg(self):
        check_named(
            self, ValueError, lambda: mod05.proportion_record(1),
            "proportion_record", "no proportion stands stored")

    def test_defect_proportion_record_keyword_partial(self):
        check_named(
            self, ValueError,
            lambda: mod05.proportion_record(numerator=1),
            "proportion_record", "no proportion stands stored")

    def test_defect_work_credit_no_args(self):
        check_named(
            self, ValueError, lambda: mod05.work_credit(),
            "work_credit", "no work credit stands computed")

    def test_defect_band_membership_no_args(self):
        check_named(
            self, ValueError, lambda: mod05.band_membership(),
            "band_membership", "no band stands returned")

    def test_defect_band_membership_one_arg(self):
        check_named(
            self, ValueError, lambda: mod05.band_membership(5),
            "band_membership", "no band stands returned")

    def test_control_proportion_record_served_whole(self):
        self.assertEqual(
            mod05.proportion_record(1, 2),
            {"numerator": 1, "denominator": 2})

    def test_control_proportion_record_none_refusal_stands(self):
        with self.assertRaises(ValueError) as caught:
            mod05.proportion_record(None, 2)
        self.assertIn("no proportion stands stored",
                      str(caught.exception))

    def test_control_work_credit_empty_served_whole(self):
        result = mod05.work_credit([])
        self.assertEqual(result["events_used"], 0)
        self.assertEqual(result["totals"]["submitted"], 0)

    def test_control_band_membership_served_whole(self):
        result = mod05.band_membership(
            5, [("low", 0), ("high", 10)], evaluation_order="O-1")
        self.assertEqual(result["band"], "low")


class TestFW510Mod06(unittest.TestCase):

    def test_defect_escrow_result_no_args(self):
        check_named(
            self, ValueError, lambda: mod06.escrow_result(),
            "escrow_result", "no escrow result stands returned")

    def test_control_escrow_result_served_whole(self):
        result = mod06.escrow_result("screening")
        self.assertEqual(result["kind"], "screening")
        self.assertIs(result["core_only_qualifier"], True)


class TestFW510Mod08(unittest.TestCase):

    def test_defect_score_no_args(self):
        check_named(
            self, mod08.NamedDetectionFailure,
            lambda: mod08.score(),
            "score", "no answer stands returned")

    def test_control_score_none_refusal_stands(self):
        with self.assertRaises(mod08.NamedDetectionFailure) as caught:
            mod08.score(None)
        self.assertIn("delivery rejected", str(caught.exception))


class TestFW510Mod11(unittest.TestCase):

    def test_defect_make_headline_unit_no_args(self):
        check_named(
            self, ValueError, lambda: mod11.make_headline_unit(),
            "make_headline_unit", "no unit stands built")

    def test_control_make_headline_unit_empty_refusal_stands(self):
        with self.assertRaises(ValueError) as caught:
            mod11.make_headline_unit({})
        self.assertIn("no unit stands built", str(caught.exception))


class TestFW510Mod12(unittest.TestCase):

    def test_defect_seal_family_record_no_args(self):
        check_named(
            self, mod12.NamedControllerFailure,
            lambda: mod12.seal_family_record(),
            "seal", "no seal stands")

    def test_control_seal_family_record_empty_refusal_stands(self):
        with self.assertRaises(mod12.NamedControllerFailure):
            mod12.seal_family_record({})


class TestFW510Mod13(unittest.TestCase):

    def test_defect_replay_check_no_args(self):
        check_named(
            self, mod13.NamedReplicationFailure,
            lambda: mod13.replay_check(),
            "replay check", "no replay check stands performed")

    def test_defect_replay_check_one_arg(self):
        check_named(
            self, mod13.NamedReplicationFailure,
            lambda: mod13.replay_check({}),
            "replay check", "no replay check stands performed")

    def test_control_replay_check_pair_served_whole(self):
        result = mod13.replay_check({}, {})
        self.assertIsInstance(result, dict)
        self.assertIn("deterministic", result)


class TestFW510Mod14(unittest.TestCase):

    def test_defect_run_command_no_args(self):
        result = mod14.run_command()
        self.assertIsInstance(result, dict)
        self.assertIs(result["operator_sees_failure"], True)
        text = result["failure"] + " " + str(result["failure_value"])
        self.assertIn("run_command", text)
        self.assertIn("missing", text)
        self.assertIn("next step", text.lower())
        self.assertNotIn("required positional argument", text)

    def test_defect_run_command_payload_only(self):
        result = mod14.run_command(payload={})
        self.assertIsInstance(result, dict)
        self.assertIs(result["operator_sees_failure"], True)
        text = result["failure"] + " " + str(result["failure_value"])
        self.assertIn("run_command", text)
        self.assertIn("missing", text)
        self.assertIn("next step", text.lower())

    def test_defect_pilot_run_no_args(self):
        check_named(
            self, mod14.NamedShellFailure,
            lambda: mod14.pilot_run(),
            "pilot_run", "no pilot run stands performed")

    def test_control_run_command_unknown_carriage_stands(self):
        result = mod14.run_command("no_such_command", {})
        self.assertIsInstance(result, dict)
        self.assertIs(result["operator_sees_failure"], True)
        self.assertIn("unknown shell command", result["failure"])

    def test_control_pilot_run_served_whole(self):
        result = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(result["use"], "timing")
        self.assertEqual(
            result["confinement_label"], "pilot confined")


class TestFW510Mod16(unittest.TestCase):

    def test_defect_fixture_record_no_args(self):
        check_named(
            self, mod16.FixtureLookupFailure,
            lambda: mod16.fixture_record(),
            "fixture_record", "no fixture record stands returned")

    def test_control_fixture_record_served_whole(self):
        result = mod16.fixture_record("F-01")
        self.assertEqual(result["fixture"], "F-01")

    def test_control_fixture_record_unknown_refusal_stands(self):
        with self.assertRaises(mod16.FixtureLookupFailure) as caught:
            mod16.fixture_record("no such fixture")
        self.assertIn("names no fixture", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

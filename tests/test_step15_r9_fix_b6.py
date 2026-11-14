"""Step 15, second run, fix wave 8 pins, Builder 6.

Row pinned: R8-007, the MOD-08 limb only.

R8-007, MOD-08 limb: the barred key fold at MOD-08 takes a
handed text from the plain str call, so a string subclass
storing a barred name while its string reading reports
another name stands judged as the reported name at
_folded_readings and at _is_barred_key, which also reads
_combined_key_barred and its own lowered text from the
same plain call.

Each charged defect form fails on the uncured module and
passes on the cured copy; lawful controls pass both ways.
No detection score is reported as a pass or as a fail in
this file: barred readings and delivery standings only.
"""

import unittest

from crucible import mod08

_THETA_PREFIX = "\u03b8" * 13


class LieStr(str):
    """A string subclass storing one text in its characters
    while its own string reading reports another text."""

    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class LowerLieStr(str):
    """A string subclass whose string reading stands honest
    and whose lower reading alone reports another text."""

    def __new__(cls, stored, reported):
        obj = str.__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return str.__str__(self)

    def lower(self):
        return self._reported


def _record_with_nested_key(key):
    return {
        "agent_identifier": "agent-b6",
        "day": 2,
        "feature_values": {"activity": 3},
        "records_for_agent_and_day": [{"wrap": {key: 1}}],
    }


class TestR8007Mod08FoldedReadings(unittest.TestCase):

    def test_lying_membership_reads_as_stored_in_folded_readings(self):
        key = LieStr("membership", "activity")
        self.assertIn("membership", mod08._folded_readings(key))
        self.assertNotIn("activity", mod08._folded_readings(key))

    def test_lying_canary_reads_as_stored_in_folded_readings(self):
        key = LieStr("canary", "activity")
        self.assertIn("canary", mod08._folded_readings(key))

    def test_reverse_lying_key_reads_as_stored_in_folded_readings(self):
        key = LieStr("activity", "membership")
        self.assertIn("activity", mod08._folded_readings(key))
        self.assertNotIn("membership", mod08._folded_readings(key))


class TestR8007Mod08IsBarredKey(unittest.TestCase):

    def test_lying_membership_is_barred(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("membership", "activity")))

    def test_lying_canary_is_barred(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("canary", "activity")))

    def test_lying_ground_truth_is_barred(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("ground_truth", "figure")))

    def test_lying_exact_key_label_is_barred(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("label", "activity")))

    def test_reverse_lying_clean_key_is_not_barred(self):
        self.assertFalse(
            mod08._is_barred_key(LieStr("activity", "membership")))
        self.assertFalse(
            mod08._is_barred_key(LieStr("figure", "ground_truth")))
        self.assertFalse(
            mod08._is_barred_key(LieStr("activity", "label")))

    def test_lying_canary_past_the_bound_is_barred(self):
        key = LieStr(_THETA_PREFIX + "canary", "activity")
        self.assertTrue(mod08._combined_key_barred(key))
        self.assertTrue(mod08._is_barred_key(key))

    def test_reverse_lying_key_past_the_bound_is_not_barred(self):
        key = LieStr(_THETA_PREFIX + "activity", "canary")
        self.assertFalse(mod08._combined_key_barred(key))
        self.assertFalse(mod08._is_barred_key(key))


class TestR8007Mod08PublicAct(unittest.TestCase):

    def test_public_act_refuses_lying_canary_key(self):
        record = _record_with_nested_key(LieStr("canary", "activity"))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_public_act_refuses_lying_ground_truth_key(self):
        record = _record_with_nested_key(
            LieStr("ground_truth", "figure"))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_public_act_accepts_reverse_lying_clean_key(self):
        record = _record_with_nested_key(
            LieStr("activity", "canary"))
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(accepted["agent_identifier"], "agent-b6")
        self.assertEqual(accepted["day"], 2)


class TestR8007Mod08Controls(unittest.TestCase):

    def test_plain_controls_stand(self):
        self.assertTrue(mod08._is_barred_key("membership"))
        self.assertTrue(mod08._is_barred_key("canary"))
        self.assertTrue(mod08._is_barred_key("ground_truth"))
        self.assertTrue(mod08._is_barred_key("label"))
        self.assertFalse(mod08._is_barred_key("activity"))
        self.assertFalse(mod08._is_barred_key("figure"))
        self.assertIn("membership", mod08._folded_readings("membership"))
        self.assertFalse(
            mod08._combined_key_barred(_THETA_PREFIX + "activity"))
        self.assertTrue(
            mod08._combined_key_barred(_THETA_PREFIX + "canary"))

    def test_agreeing_lying_controls_stand(self):
        self.assertTrue(
            mod08._is_barred_key(LieStr("canary", "canary")))
        self.assertFalse(
            mod08._is_barred_key(LieStr("figure", "figure")))

    def test_lower_only_lying_control_stands(self):
        self.assertTrue(mod08._is_barred_key(
            LowerLieStr("membership", "activity")))
        self.assertFalse(mod08._is_barred_key(
            LowerLieStr("activity", "membership")))

    def test_public_act_plain_controls_stand(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(
                _record_with_nested_key("canary"))
        accepted = mod08.accept_detection_input(
            _record_with_nested_key("activity"))
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


if __name__ == "__main__":
    unittest.main()

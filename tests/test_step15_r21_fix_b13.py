"""Pins for fix wave 21, builder b13, group 13.

Row pinned: R21-021, the MOD-14 NamedShellFailure construction.
The construction must build its failure message through the
module stored text form, so a dressed message stands carried
as the text it stores, never as a reading it supplies, and a
raising string reading never escapes bare at construction.
"""

import unittest

from crucible import mod14
from crucible.mod14 import NamedShellFailure


class RaisingStr(str):
    """A text value storing its text whose string reading
    raises RuntimeError on every call."""

    def __str__(self):
        raise RuntimeError("str boom")


class LyingStr(str):
    """A text value storing its text whose string reading
    answers a different text than the one it stores."""

    def __str__(self):
        return "FAKE-LIE"


class TestR21021Distinguishing(unittest.TestCase):
    """Distinguishing pins: each fails or errors on the
    pristine construction, which builds its failure dict
    through plain str(message)."""

    def test_raising_message_failure_dict_stored_form(self):
        failure = NamedShellFailure(RaisingStr("stored-refusal"))
        self.assertEqual(failure.failure["message"], "stored-refusal")
        self.assertEqual(failure.failure["name"], "NamedShellFailure")

    def test_raising_message_exception_text_stored_form(self):
        failure = NamedShellFailure(RaisingStr("stored-refusal"))
        self.assertEqual(str(failure), "stored-refusal")

    def test_raising_message_carriage_stored_form(self):
        failure = NamedShellFailure(RaisingStr("stored-refusal"))
        carriage = mod14.error_carriage(failure, run_id="r1", stage="s1")
        self.assertEqual(
            carriage["failure"], "NamedShellFailure: stored-refusal")
        self.assertEqual(
            carriage["failure_value"]["message"], "stored-refusal")

    def test_lying_message_failure_dict_stored_form(self):
        failure = NamedShellFailure(LyingStr("stored-refusal"))
        self.assertEqual(failure.failure["message"], "stored-refusal")
        self.assertNotEqual(failure.failure["message"], "FAKE-LIE")

    def test_lying_message_exception_text_stored_form(self):
        failure = NamedShellFailure(LyingStr("stored-refusal"))
        self.assertEqual(str(failure), "stored-refusal")

    def test_lying_message_carriage_stored_form(self):
        failure = NamedShellFailure(LyingStr("stored-refusal"))
        carriage = mod14.error_carriage(failure, run_id="r1", stage="s1")
        self.assertEqual(
            carriage["failure"], "NamedShellFailure: stored-refusal")
        self.assertEqual(
            carriage["failure_value"]["message"], "stored-refusal")
        self.assertNotIn("FAKE-LIE", carriage["failure"])


class TestR21021Controls(unittest.TestCase):
    """Control pins: plain message handings, passing on the
    pristine construction and on the cured construction
    alike."""

    def test_plain_message_failure_dict(self):
        failure = NamedShellFailure("plain refusal")
        self.assertEqual(failure.failure["message"], "plain refusal")
        self.assertEqual(failure.failure["name"], "NamedShellFailure")

    def test_plain_message_exception_text(self):
        failure = NamedShellFailure("plain refusal")
        self.assertEqual(str(failure), "plain refusal")

    def test_plain_message_carriage(self):
        failure = NamedShellFailure("plain refusal")
        carriage = mod14.error_carriage(failure, run_id="r1", stage="s1")
        self.assertEqual(
            carriage["failure"], "NamedShellFailure: plain refusal")
        self.assertEqual(
            carriage["failure_value"]["message"], "plain refusal")

    def test_default_message_constructs_empty(self):
        failure = NamedShellFailure()
        self.assertEqual(failure.failure["message"], "")
        self.assertEqual(str(failure), "")


if __name__ == "__main__":
    unittest.main()

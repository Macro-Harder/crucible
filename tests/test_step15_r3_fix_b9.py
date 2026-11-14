"""Step 15 rerun fix wave 2 pins, seat 9. MOD-13.

Items R2-010 and R2-039.
"""
import unittest

import crucible.mod13 as mod13


class LyingStr(str):
    """A string whose own equality agrees with everything, while
    the characters it stores stand as given."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)


def _facts():
    fields = list(mod13.ac1_field_list())
    facts = {field: "value for " + field for field in fields}
    facts["headline_unit"] = {"unit": "unit-1"}
    return fields, facts


def _pair():
    fields, facts = _facts()
    first = dict(facts)
    second = dict(facts)
    verdicts = {
        "first verdict state after resume": "verdict-a",
        "run close": "verdict-b",
    }
    first["detection_verdicts"] = dict(verdicts)
    second["detection_verdicts"] = dict(verdicts)
    return fields, first, second


class TestR2010ReplayStrictComparison(unittest.TestCase):
    def test_replay_top_level_lying_string_differs(self):
        fields, first, second = _pair()
        second[fields[0]] = LyingStr("a completely different stored value")
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertTrue(check["marked_non_deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_string_nested_in_plain_list(self):
        fields, first, second = _pair()
        first[fields[1]] = ["alpha", "beta"]
        second[fields[1]] = [LyingStr("gamma"), "beta"]
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertTrue(check["marked_non_deterministic"])
        self.assertIn(fields[1], check["differing_fields"])

    def test_replay_lying_string_nested_in_dict_in_plain_list(self):
        fields, first, second = _pair()
        first[fields[2]] = [{"key": "alpha"}]
        second[fields[2]] = [{"key": LyingStr("gamma")}]
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[2], check["differing_fields"])

    def test_replay_lying_string_nested_in_tuple_and_dict(self):
        fields, first, second = _pair()
        first[fields[3]] = ("alpha", {"key": "beta"})
        second[fields[3]] = ("alpha", {"key": LyingStr("gamma")})
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[3], check["differing_fields"])

    def test_replay_lying_headline_unit_differs(self):
        fields, first, second = _pair()
        first["headline_unit"] = "unit one"
        second["headline_unit"] = LyingStr("unit two")
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn("headline_unit", check["differing_fields"])
        self.assertFalse(check["identical_headline_unit"])

    def test_replay_lying_comparability_value_differs(self):
        fields, first, second = _pair()
        first["code_version"] = "version one"
        second["code_version"] = LyingStr("version two")
        check = mod13.replay_check(first, second)
        self.assertTrue(check["not_comparable"])
        self.assertIn("code_version", check["not_comparable_on"])
        self.assertIsNot(check["deterministic"], True)

    def test_replay_lying_string_with_same_stored_value_agrees(self):
        fields, first, second = _pair()
        second[fields[0]] = LyingStr(first[fields[0]])
        second[fields[1]] = [LyingStr("nested same")]
        first[fields[1]] = ["nested same"]
        check = mod13.replay_check(first, second)
        self.assertTrue(check["deterministic"])
        self.assertEqual(check["differing_fields"], [])


class TestR2010ResumeStrictComparison(unittest.TestCase):
    def test_resume_top_level_lying_string_differs(self):
        fields, first, second = _pair()
        second[fields[0]] = LyingStr("a completely different stored value")
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[0], check["differing_fields"])
        self.assertTrue(check["promoted_to_full_retention"])
        self.assertTrue(check["witness_use_barred"])

    def test_resume_lying_string_nested_in_plain_list(self):
        fields, first, second = _pair()
        first[fields[1]] = ["alpha", "beta"]
        second[fields[1]] = [LyingStr("gamma"), "beta"]
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[1], check["differing_fields"])

    def test_resume_lying_verdict_nested_in_plain_list(self):
        fields, first, second = _pair()
        first["detection_verdicts"] = {
            "first verdict state after resume": ["verdict-a"],
            "run close": "verdict-b",
        }
        second["detection_verdicts"] = {
            "first verdict state after resume": [LyingStr("verdict-z")],
            "run close": "verdict-b",
        }
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertEqual(
            check["first_divergence"], "first verdict state after resume")

    def test_resume_lying_string_with_same_stored_value_agrees(self):
        fields, first, second = _pair()
        second[fields[0]] = LyingStr(first[fields[0]])
        check = mod13.resume_check(first, second)
        self.assertTrue(check["equal_in_scope"])


class TestR2039ReplicationSentences(unittest.TestCase):
    def _record(self):
        return mod13.verdict_record("claim-1")

    def _claim(self):
        return {"claim_identifier": "claim-1"}

    def test_valid_record_passes_and_stands_publishable(self):
        record = self._record()
        self.assertTrue(mod13.validate_verdict_record(record))
        self.assertTrue(
            mod13.publishable_on_replication(self._claim(), record))

    def test_empty_sentence_form_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = []
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_missing_sentence_form_fails(self):
        record = self._record()
        del record["replication_statement_sentences"]
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_contradicting_sentence_fails(self):
        record = self._record()
        sentences = list(record["replication_statement_sentences"])
        sentences[0] = (
            "A separate team rebuilt the program and reran the work.")
        record["replication_statement_sentences"] = sentences
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_all_sentences_replaced_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = [
            "One sentence.", "Another sentence.", "A third sentence."]
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_truncated_sentence_form_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = (
            list(record["replication_statement_sentences"])[:2])
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_extra_sentence_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = (
            list(record["replication_statement_sentences"])
            + ["An extra sentence stands added."])
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_reordered_sentences_fail(self):
        record = self._record()
        sentences = list(record["replication_statement_sentences"])
        record["replication_statement_sentences"] = [
            sentences[1], sentences[0], sentences[2]]
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_lying_sentence_with_different_stored_value_fails(self):
        record = self._record()
        sentences = list(record["replication_statement_sentences"])
        sentences[2] = LyingStr("A contradictory stored sentence.")
        record["replication_statement_sentences"] = sentences
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_sentence_form_as_one_joined_string_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = (
            record["replication_statement"])
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))


if __name__ == "__main__":
    unittest.main()

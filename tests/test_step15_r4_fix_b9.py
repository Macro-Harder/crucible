"""Step 15 rerun fix wave 3 pins, seat 9. MOD-13.

Items R3-009, R3-010, R3-019, R3-039, and R3-040.
"""
import unittest

import crucible.mod13 as mod13


class LyingStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)


class LyingFloat(float):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return float.__hash__(self)


class LyingInt(int):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return int.__hash__(self)


class LyingObject:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class LyingSet(set):
    def __iter__(self):
        return iter(["alpha"])


class LyingFrozenset(frozenset):
    def __iter__(self):
        return iter(["alpha"])


class LyingSentenceList(list):
    def __iter__(self):
        return iter(mod13.REPLICATION_STATEMENT_SENTENCES)


class LyingSentenceTuple(tuple):
    def __iter__(self):
        return iter(mod13.REPLICATION_STATEMENT_SENTENCES)


class LyingClaimId(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return str.__hash__(self)

    def __len__(self):
        return 5


def _pair():
    fields = list(mod13.ac1_field_list())
    facts = {field: "value for " + field for field in fields}
    facts["headline_unit"] = {"unit": "unit-1"}
    first = dict(facts)
    second = dict(facts)
    verdicts = {
        "first verdict state after resume": "verdict-a",
        "run close": "verdict-b",
    }
    first["detection_verdicts"] = dict(verdicts)
    second["detection_verdicts"] = dict(verdicts)
    return fields, first, second


def _chain(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


class TestR3009MixedNumericReplay(unittest.TestCase):
    def test_replay_lying_float_against_plain_int_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = 1
        second[fields[0]] = LyingFloat(999.0)
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_int_against_plain_float_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = 1.0
        second[fields[0]] = LyingInt(999)
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_mixed_same_stored_value_agrees(self):
        fields, first, second = _pair()
        first[fields[0]] = 1
        second[fields[0]] = LyingFloat(1.0)
        check = mod13.replay_check(first, second)
        self.assertTrue(check["deterministic"])

    def test_replay_plain_mixed_controls(self):
        fields, first, second = _pair()
        first[fields[0]] = 1
        second[fields[0]] = 999.0
        self.assertFalse(mod13.replay_check(first, second)["deterministic"])
        second[fields[0]] = 1.0
        self.assertTrue(mod13.replay_check(first, second)["deterministic"])


class TestR3009MixedNumericResume(unittest.TestCase):
    def test_resume_lying_float_against_plain_int_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = 1
        second[fields[0]] = LyingFloat(999.0)
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_resume_lying_int_against_plain_float_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = 1.0
        second[fields[0]] = LyingInt(999)
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[0], check["differing_fields"])


class TestR3009FallbackReplay(unittest.TestCase):
    def test_replay_lying_object_top_level_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = LyingObject(1)
        second[fields[0]] = LyingObject(2)
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_object_nested_in_dict_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = {"key": LyingObject(1)}
        second[fields[0]] = {"key": LyingObject(2)}
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_plain_objects_differ(self):
        fields, first, second = _pair()
        first[fields[0]] = object()
        second[fields[0]] = object()
        self.assertFalse(mod13.replay_check(first, second)["deterministic"])


class TestR3009FallbackResume(unittest.TestCase):
    def test_resume_lying_object_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = LyingObject(1)
        second[fields[0]] = LyingObject(2)
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[0], check["differing_fields"])


class TestR3010SetIterationReplay(unittest.TestCase):
    def test_replay_lying_set_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = {"alpha"}
        dressed = LyingSet()
        set.add(dressed, "beta")
        second[fields[0]] = dressed
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_frozenset_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = frozenset(["alpha"])
        second[fields[0]] = LyingFrozenset(["beta"])
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_set_nested_in_list_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = [{"alpha"}]
        dressed = LyingSet()
        set.add(dressed, "beta")
        second[fields[0]] = [dressed]
        check = mod13.replay_check(first, second)
        self.assertFalse(check["deterministic"])
        self.assertIn(fields[0], check["differing_fields"])

    def test_replay_lying_set_same_stored_value_agrees(self):
        fields, first, second = _pair()
        first[fields[0]] = {"alpha"}
        dressed = LyingSet()
        set.add(dressed, "alpha")
        second[fields[0]] = dressed
        self.assertTrue(mod13.replay_check(first, second)["deterministic"])

    def test_replay_plain_set_controls(self):
        fields, first, second = _pair()
        first[fields[0]] = {"alpha"}
        second[fields[0]] = {"beta"}
        self.assertFalse(mod13.replay_check(first, second)["deterministic"])
        second[fields[0]] = {"alpha"}
        self.assertTrue(mod13.replay_check(first, second)["deterministic"])


class TestR3010SetIterationResume(unittest.TestCase):
    def test_resume_lying_set_verdict_differs(self):
        fields, first, second = _pair()
        dressed = LyingSet()
        set.add(dressed, "beta")
        second["detection_verdicts"] = {
            "first verdict state after resume": dressed,
            "run close": "verdict-b",
        }
        first["detection_verdicts"] = {
            "first verdict state after resume": {"alpha"},
            "run close": "verdict-b",
        }
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])

    def test_resume_lying_frozenset_field_differs(self):
        fields, first, second = _pair()
        first[fields[0]] = frozenset(["alpha"])
        second[fields[0]] = LyingFrozenset(["beta"])
        check = mod13.resume_check(first, second)
        self.assertFalse(check["equal_in_scope"])
        self.assertIn(fields[0], check["differing_fields"])


class TestR3019DepthBound(unittest.TestCase):
    def test_strict_eq_deep_chain_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(_chain(150, "leaf"), _chain(150, "leaf"))

    def test_strict_eq_depth_2000_refused_in_named_form(self):
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13._strict_eq(_chain(2000, "leaf"), _chain(2000, "leaf"))

    def test_replay_deep_chain_refused_in_named_form(self):
        fields, first, second = _pair()
        first[fields[0]] = _chain(150, "leaf")
        second[fields[0]] = _chain(150, "leaf")
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.replay_check(first, second)

    def test_replay_depth_2000_refused_in_named_form(self):
        fields, first, second = _pair()
        first[fields[0]] = _chain(2000, "leaf")
        second[fields[0]] = _chain(2000, "leaf")
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.replay_check(first, second)

    def test_resume_deep_chain_refused_in_named_form(self):
        fields, first, second = _pair()
        first[fields[0]] = _chain(150, "leaf")
        second[fields[0]] = _chain(150, "leaf")
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.resume_check(first, second)

    def test_within_bound_chain_answers(self):
        fields, first, second = _pair()
        first[fields[0]] = _chain(90, "leaf")
        second[fields[0]] = _chain(90, "leaf")
        self.assertTrue(mod13.replay_check(first, second)["deterministic"])
        second[fields[0]] = _chain(90, "other")
        self.assertFalse(mod13.replay_check(first, second)["deterministic"])


class TestR3039SentenceIteration(unittest.TestCase):
    def _record(self):
        return mod13.verdict_record("claim-1")

    def _claim(self):
        return {"claim_identifier": "claim-1"}

    def test_list_subclass_storing_contradictory_sentences_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = LyingSentenceList([
            "Completely contradictory stored sentence one.",
            "Stored two.",
            "Stored three.",
        ])
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_tuple_subclass_storing_contradictory_sentences_fails(self):
        record = self._record()
        record["replication_statement_sentences"] = LyingSentenceTuple((
            "Completely contradictory stored sentence one.",
            "Stored two.",
            "Stored three.",
        ))
        self.assertFalse(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_plain_tuple_canonical_sentences_pass(self):
        record = self._record()
        record["replication_statement_sentences"] = tuple(
            mod13.REPLICATION_STATEMENT_SENTENCES)
        self.assertTrue(mod13.validate_verdict_record(record))
        self.assertTrue(
            mod13.publishable_on_replication(self._claim(), record))


class TestR3040VerdictEquality(unittest.TestCase):
    def _record(self):
        return mod13.verdict_record("claim-1")

    def _claim(self):
        return {"claim_identifier": "claim-1"}

    def test_validate_lying_bogus_outcome_fails(self):
        record = self._record()
        record["outcome"] = LyingStr("bogus outcome")
        self.assertFalse(mod13.validate_verdict_record(record))

    def test_publishable_lying_non_resting_outcome_fails(self):
        record = self._record()
        record["outcome"] = LyingStr("does not rest")
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_publishable_lying_claim_identifier_fails_for_other_claim(self):
        record = mod13.verdict_record(LyingStr("claim-999"))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))

    def test_validate_lying_empty_claim_identifier_fails(self):
        record = self._record()
        record["claim_identifier"] = LyingClaimId("")
        self.assertFalse(mod13.validate_verdict_record(record))

    def test_publishable_lying_hand_claim_identifier_fails(self):
        record = self._record()
        claim = {"claim_identifier": LyingStr("claim-999")}
        self.assertFalse(mod13.publishable_on_replication(claim, record))

    def test_valid_record_controls(self):
        record = self._record()
        self.assertTrue(mod13.validate_verdict_record(record))
        self.assertTrue(
            mod13.publishable_on_replication(self._claim(), record))
        record["outcome"] = "does not rest"
        self.assertTrue(mod13.validate_verdict_record(record))
        self.assertFalse(
            mod13.publishable_on_replication(self._claim(), record))


if __name__ == "__main__":
    unittest.main()

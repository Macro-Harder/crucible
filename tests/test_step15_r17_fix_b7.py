"""Pins for fix wave 16, Builder 7: rows R16-024, R16-055,
R16-088, and R16-089 of the Round 16 register.

R16-024: MOD-06 _run_instruction_act judges its handed name on
its stored text, not on readings the handed value supplies.
R16-055: MOD-13 verdict_record judges its standard and outcome
membership by base string equality, as its companions do.
R16-088: MOD-06 _run_instruction_act states a consequence at
its two GuessedAnswer sentences, its UnnamedInstruction
sentence, and its replace_backup_key sentence.
R16-089: MOD-02 encode_candidate_input states the full lawful
form and a consequence at its two refusal sentences.
"""

import unittest

from crucible import mod02, mod06, mod13


class StrReturnsPool(str):
    """Stores one text; its string reading returns pool."""

    def __str__(self):
        return "pool"


class EqRaisesStr(str):
    """Stores one text; its equality reading raises."""

    __hash__ = str.__hash__

    def __eq__(self, other):
        raise RuntimeError("eq boom")


class EqTrueStr(str):
    """Stores one text; its equality reading answers True."""

    __hash__ = str.__hash__

    def __eq__(self, other):
        return True


class TestR16024InstructionNameStoredText(unittest.TestCase):

    def test_bytes_allowed_name_reaches_its_own_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction(b"replace_backup_key")
        self.assertIn(
            "replace_backup_key stands refused",
            str(caught.exception))

    def test_bytes_allowed_name_runs(self):
        result = mod06.run_instruction(b"deposit")
        self.assertEqual(
            result["payload"]["instruction"], "deposit")

    def test_bytearray_allowed_name_reaches_its_own_refusal(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction(bytearray(b"replace_backup_key"))
        self.assertIn(
            "replace_backup_key stands refused",
            str(caught.exception))

    def test_memoryview_allowed_name_runs(self):
        result = mod06.run_instruction(memoryview(b"deposit"))
        self.assertEqual(
            result["payload"]["instruction"], "deposit")

    def test_list_name_draws_unnamed_refusal(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction(["deposit"])

    def test_dict_name_draws_unnamed_refusal(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction({"deposit": 1})

    def test_set_name_draws_unnamed_refusal(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction({"deposit"})

    def test_raising_equality_name_draws_unnamed_refusal(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction(EqRaisesStr("bogus_name"))

    def test_pool_reading_name_storing_deposit_runs(self):
        result = mod06.run_instruction(StrReturnsPool("deposit"))
        self.assertEqual(
            result["payload"]["instruction"], "deposit")

    def test_plain_unnamed_control(self):
        with self.assertRaises(mod06.UnnamedInstruction):
            mod06.run_instruction("bogus_name")

    def test_plain_pool_control(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("pool_init")

    def test_bytes_excluded_profile_control(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(b"backup extended profile")


class TestR16055VerdictRecordMembership(unittest.TestCase):

    def test_lying_equality_standard_draws_unknown_standard(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record(
                "c1", standard=EqTrueStr("bogus standard"))
        self.assertIn(
            "unknown replication standard", str(caught.exception))

    def test_lying_equality_outcome_draws_unknown_outcome(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record(
                "c1", outcome=EqTrueStr("bogus outcome"))
        self.assertIn(
            "unknown verdict outcome", str(caught.exception))

    def test_plain_bogus_standard_control(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", standard="bogus")
        self.assertIn(
            "unknown replication standard", str(caught.exception))

    def test_plain_bogus_outcome_control(self):
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.verdict_record("c1", outcome="bogus")
        self.assertIn(
            "unknown verdict outcome", str(caught.exception))

    def test_valid_record_control(self):
        record = mod13.verdict_record("c1")
        self.assertEqual(
            record["standard_applied"], "exact replay alone")
        self.assertEqual(record["outcome"], "rests")

    def test_stored_valid_standard_with_lying_equality_control(self):
        record = mod13.verdict_record(
            "c1", standard=EqTrueStr("exact replay alone"))
        self.assertEqual(
            record["standard_applied"], "exact replay alone")


class TestR16088InstructionSentenceConsequences(unittest.TestCase):

    def test_guessed_answer_claims_states_consequence(self):
        with self.assertRaises(mod06.GuessedAnswer) as caught:
            mod06.run_instruction(
                "open_request", context={"claims_dq_answer": True})
        self.assertIn(
            "no instruction stands run", str(caught.exception))

    def test_guessed_answer_floor_states_consequence(self):
        with self.assertRaises(mod06.GuessedAnswer) as caught:
            mod06.run_instruction(
                "open_request",
                context={"asserts_floor_under_n": True})
        self.assertIn(
            "no instruction stands run", str(caught.exception))

    def test_unnamed_sentence_states_consequence(self):
        with self.assertRaises(
                mod06.UnnamedInstruction) as caught:
            mod06.run_instruction("bogus_name")
        self.assertIn(
            "no instruction stands run", str(caught.exception))

    def test_replace_backup_key_sentence_states_consequence(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction("replace_backup_key")
        self.assertIn(
            "no key stands replaced", str(caught.exception))

    def test_open_request_consequence_control(self):
        with self.assertRaises(ValueError) as caught:
            mod06.run_instruction("open_request", context={})
        self.assertIn(
            "no request stands opened", str(caught.exception))

    def test_excluded_subpath_sentence_unchanged_control(self):
        with self.assertRaises(mod06.ExcludedSubpath) as caught:
            mod06.run_instruction("pool_init")
        self.assertEqual(
            str(caught.exception),
            "a construction excluded on a DQ ground stays "
            "excluded on that ground: pool_init")


class TestR16089EncodeCandidateInputSentences(unittest.TestCase):

    def test_text_handling_states_form_and_consequence(self):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input("text")
        text = str(caught.exception)
        self.assertIn("candidate input is not a field mapping", text)
        self.assertIn(
            "mapping of field names to recorded string values",
            text)
        self.assertIn("no encoding stands returned", text)

    def test_list_handling_states_form_and_consequence(self):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input(["k"])
        text = str(caught.exception)
        self.assertIn(
            "mapping of field names to recorded string values",
            text)
        self.assertIn("no encoding stands returned", text)

    def test_parameter_value_states_form_and_consequence(self):
        with self.assertRaises(ValueError) as caught:
            mod02.encode_candidate_input({"k": 5})
        text = str(caught.exception)
        self.assertIn("is not a recorded string", text)
        self.assertIn(
            "mapping of field names to recorded string values",
            text)
        self.assertIn("no encoding stands returned", text)

    def test_valid_encoding_control(self):
        self.assertEqual(
            mod02.encode_candidate_input({"k": "v"}),
            "str:1:k=1:v")

    def test_draw_from_stream_full_sentence_control(self):
        with self.assertRaises(ValueError) as caught:
            mod02.draw_from_stream(
                position="abc", carried_positions=3)
        self.assertIn(
            "no draw stands made", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

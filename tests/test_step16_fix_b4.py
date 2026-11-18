"""Step 16 fix wave, Builder 4. Rows R16-10 and R16-16.

R16-10: aggregate_reputation, aggregation_score, and
compare_aggregation must not return a score 0 indistinguishable
from a genuine zero for inputs carrying no documented field.
Adopted form: a named refusal, a ValueError stating that no
stated field stood read and nothing stood scored.

R16-16: malformed typed fields at the same surface must stand
refused in a named failure form naming the field, in place of
bare interpreter errors.

DQ7-04 stands comparison form only. No treatment stands adopted
by these tests. Documented inputs must compute exactly as before.
"""
import unittest

import crucible.mod05 as mod05


FIELDLESS_INPUTS = [
    None,
    {},
    [],
    {"unknown_key": 3},
    {"scores": [1, 2, 3]},
    {"accepted_work": None},
    {"agent_identifier": None},
]

SURFACES = [
    ("aggregate_reputation", mod05.aggregate_reputation),
    ("aggregation_score", mod05.aggregation_score),
    ("compare_aggregation", mod05.compare_aggregation),
]

ORDER = {"order": "sequential"}
BANDS = [("low", 0), ("high", 5)]


class TestR1610FieldlessRefusal(unittest.TestCase):
    def test_fieldless_inputs_refused_at_every_surface(self):
        for name, fn in SURFACES:
            for inputs in FIELDLESS_INPUTS:
                with self.subTest(surface=name, inputs=repr(inputs)):
                    with self.assertRaises(ValueError) as caught:
                        fn(inputs)
                    message = str(caught.exception)
                    self.assertIn("stands refused", message)
                    self.assertIn("no stated field stood read", message)
                    self.assertIn("nothing stood scored", message)

    def test_genuine_zero_still_computes(self):
        result = mod05.aggregate_reputation(
            {"agent_identifier": "a", "accepted_work": 0,
             "vouches_received": [], "penalties": 0})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["scores"], [0])
        self.assertEqual(result["agent_identifier"], "a")

    def test_documented_inputs_compute_exactly_as_before(self):
        inputs = {"agent_identifier": "agent-1", "accepted_work": 5,
                  "vouches_received": [{"stake": 3, "score_bearing_flag": True}],
                  "penalties": 1}
        for name, fn in SURFACES:
            with self.subTest(surface=name):
                result = fn(inputs)
                self.assertEqual(result["score"], 7)
                self.assertEqual(result["scores"], [7])
                self.assertEqual(result["form"], "comparison form only")
                self.assertFalse(result["adopted"])
                self.assertIsNone(result["adopted_rule"])
                self.assertFalse(result["headline_use_permitted"])
                for statement in mod05.AC8_FACE_STATEMENTS:
                    self.assertIn(statement, result["face_statements"])

    def test_single_documented_field_computes(self):
        result = mod05.aggregate_reputation(
            {"agent_identifier": "agent-a", "accepted_work": 1})
        self.assertEqual(result["score"], 1)
        result = mod05.aggregate_reputation({"agent_identifier": "agent-a"})
        self.assertEqual(result["score"], 0)
        result = mod05.aggregate_reputation({"penalties": 0})
        self.assertEqual(result["score"], 0)


class TestR1616AggregateMalformed(unittest.TestCase):
    def assert_named_refusal(self, fn, inputs, field):
        with self.assertRaises(ValueError) as caught:
            fn(inputs)
        self.assertNotIsInstance(caught.exception, TypeError)
        message = str(caught.exception)
        self.assertIn("stands refused", message)
        self.assertIn(field, message)

    def test_text_accepted_work_refused_naming_field(self):
        for name, fn in SURFACES:
            with self.subTest(surface=name):
                self.assert_named_refusal(
                    fn, {"agent_identifier": "a", "accepted_work": "text"},
                    "accepted_work")

    def test_list_accepted_work_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": [1]}, "accepted_work")

    def test_bool_accepted_work_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": True}, "accepted_work")

    def test_text_penalties_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": 1, "penalties": "x"},
            "penalties")

    def test_int_vouches_received_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": 1, "vouches_received": 5},
            "vouches_received")

    def test_text_vouches_received_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": 1,
             "vouches_received": "text"}, "vouches_received")

    def test_text_stake_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": 1,
             "vouches_received": [{"stake": "x", "score_bearing_flag": True}]},
            "stake")

    def test_non_dict_vouch_entry_refused_naming_field(self):
        self.assert_named_refusal(
            mod05.aggregate_reputation,
            {"agent_identifier": "a", "accepted_work": 1,
             "vouches_received": ["text"]}, "vouches_received")

    def test_non_bearing_vouch_stake_not_read(self):
        result = mod05.aggregate_reputation(
            {"agent_identifier": "a", "accepted_work": 1,
             "vouches_received": [{"stake": "x", "score_bearing_flag": False}]})
        self.assertEqual(result["score"], 1)


class TestR1616ReputationAndBandMalformed(unittest.TestCase):
    def assert_named_refusal(self, args, field):
        with self.assertRaises(ValueError) as caught:
            mod05.reputation_and_band_values(*args)
        self.assertNotIsInstance(caught.exception, TypeError)
        message = str(caught.exception)
        self.assertIn("stands refused", message)
        self.assertIn(field, message)

    def test_none_agents_scores_refused_naming_field(self):
        self.assert_named_refusal(
            (None, BANDS), "agents_scores")
        self.assert_named_refusal(
            (None, BANDS, None, ORDER), "agents_scores")

    def test_list_agents_scores_refused_naming_field(self):
        self.assert_named_refusal(
            ([("a", 5)], BANDS, None, ORDER), "agents_scores")

    def test_text_score_refused_naming_field(self):
        self.assert_named_refusal(
            ({"a": "text"}, BANDS, None, ORDER), "agents_scores")

    def test_bool_score_refused_naming_field(self):
        self.assert_named_refusal(
            ({"a": True}, BANDS, None, ORDER), "agents_scores")

    def test_none_bands_refused_naming_field(self):
        self.assert_named_refusal(
            ({"a": 5}, None, None, ORDER), "bands")

    def test_text_band_minimum_refused_naming_field(self):
        self.assert_named_refusal(
            ({"a": 5}, [("low", "x")], None, ORDER), "bands")

    def test_documented_reputation_and_band_still_computes(self):
        out = mod05.reputation_and_band_values(
            {"agent-a": 10}, BANDS, evaluation_order=ORDER)
        self.assertEqual(out["values"]["agent-a"]["band"], "high")
        self.assertEqual(out["values"]["agent-a"]["score"], 10)
        out = mod05.reputation_and_band_values(
            {"agent-a": 0}, BANDS, evaluation_order=ORDER)
        self.assertEqual(out["values"]["agent-a"]["band"], "low")


if __name__ == "__main__":
    unittest.main()

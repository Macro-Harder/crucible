"""

Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

"""


import unittest
from crucible import mod08


class LieEqStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class RaiseEqStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __eq__(self, other):
        raise RuntimeError("equality raises")

    def __ne__(self, other):
        raise RuntimeError("equality raises")

    __hash__ = str.__hash__


class LieStr(str):
    def __new__(cls, stored, reading):
        obj = str.__new__(cls, stored)
        obj._reading = reading
        return obj

    def __str__(self):
        return self._reading

    def __repr__(self):
        return self._reading


class RaiseStr(str):
    def __new__(cls, stored):
        return str.__new__(cls, stored)

    def __str__(self):
        raise RuntimeError("string raises")

    def __repr__(self):
        raise RuntimeError("repr raises")


def score_sentence(**kwargs):
    try:
        mod08.score_day([], **kwargs)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def use_sentence(artefact, run_record_uses=None):
    try:
        mod08.validate_use_naming(artefact, run_record_uses)
    except mod08.SilentUseMovement as error:
        return str(error)
    return ""


def conformance_sentence(**kwargs):
    try:
        mod08.conformance_statement(**kwargs)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def author_sentence(kind):
    sealed = mod08.freeze_sealed_set(mod08.create_sealed_set())
    try:
        mod08.author_sealed_class(
            sealed, kind, "id-1",
            separations=list(mod08._SEPARATIONS))
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def detection_sentence(record):
    try:
        mod08.accept_detection_input(record)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


def profiles_sentence(streams):
    profile_set = {
        "profiles": list(mod08.F06_PROFILES),
        "streams_per_profile": streams,
    }
    try:
        mod08.score_profiles(profile_set)
    except mod08.NamedDetectionFailure as error:
        return str(error)
    return ""


class TestR20020ScoreDayMembership(unittest.TestCase):
    def test_lying_mode_storing_bogus_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day([], mode=LieEqStr("bogus"))

    def test_raising_mode_storing_conformance_delivered(self):
        result = mod08.score_day([], mode=RaiseEqStr("conformance"))
        self.assertIn("detection_output", result)

    def test_bytes_mode_storing_conformance_delivered(self):
        result = mod08.score_day([], mode=b"conformance")
        self.assertIn("detection_output", result)

    def test_lying_use_storing_bogus_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day([], uses=[LieEqStr("bogus")])

    def test_raising_use_storing_conformance_delivered(self):
        result = mod08.score_day([], uses=[RaiseEqStr("conformance")])
        self.assertIn("detection_output", result)

    def test_bytes_use_storing_assumption_delivered(self):
        result = mod08.score_day([], uses=[b"assumption"])
        self.assertIn("detection_output", result)

    def test_plain_mode_conformance_delivered_control(self):
        result = mod08.score_day([])
        self.assertEqual(result["mode"], "conformance")
        self.assertEqual(result["uses_named"], ["conformance"])

    def test_plain_bogus_mode_refused_control(self):
        sentence = score_sentence(mode="bogus")
        self.assertIn("scoring mode stands unnamed: bogus", sentence)

    def test_plain_bogus_use_refused_control(self):
        sentence = score_sentence(uses=["bogus"])
        self.assertIn("scoring use stands unnamed: bogus", sentence)


class TestR20021UseNaming(unittest.TestCase):
    def test_lying_use_in_artefact_refused(self):
        sentence = use_sentence({"uses_named": [LieEqStr("bogus_use")]})
        self.assertIn("a use stands unnamed", sentence)

    def test_lying_run_record_use_judged_disagreeing(self):
        sentence = use_sentence(
            {"uses_named": ["conformance"]}, [LieEqStr("other")])
        self.assertIn("while the run record names other", sentence)

    def test_raising_use_storing_conformance_accepted(self):
        self.assertTrue(mod08.validate_use_naming(
            {"uses_named": [RaiseEqStr("conformance")]}))

    def test_number_beside_text_in_run_record_named_refusal(self):
        sentence = use_sentence(
            {"uses_named": ["conformance"]}, [1, "conformance"])
        self.assertIn("while the run record names", sentence)

    def test_plain_conformance_accepted_control(self):
        self.assertTrue(mod08.validate_use_naming(
            {"uses_named": ["conformance"]}))

    def test_plain_matching_run_record_accepted_control(self):
        self.assertTrue(mod08.validate_use_naming(
            {"uses_named": ["conformance"]}, ["conformance"]))

    def test_plain_mismatch_named_control(self):
        sentence = use_sentence(
            {"uses_named": ["conformance"]}, ["assumption"])
        self.assertIn(
            "the artefact names conformance while the run record "
            "names assumption", sentence)


class TestR20022ConformanceStatement(unittest.TestCase):
    def test_lying_table_storing_lr9_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.conformance_statement(table_identifier=LieEqStr("LR-9"))

    def test_raising_table_storing_lr1_delivered(self):
        statement = mod08.conformance_statement(
            table_identifier=RaiseEqStr("LR-1"))
        self.assertEqual(statement["threshold_set"], "epoch weighted")

    def test_raising_threshold_storing_epoch_weighted_delivered(self):
        statement = mod08.conformance_statement(
            threshold_set=RaiseEqStr("epoch weighted"))
        self.assertEqual(statement["table_identifier"], "LR-1")

    def test_bytes_threshold_storing_epoch_weighted_delivered(self):
        statement = mod08.conformance_statement(
            threshold_set=b"epoch weighted")
        self.assertEqual(statement["table_identifier"], "LR-1")

    def test_bytes_table_storing_lr1_delivered(self):
        statement = mod08.conformance_statement(table_identifier=b"LR-1")
        self.assertEqual(statement["threshold_set"], "epoch weighted")

    def test_default_statement_control(self):
        statement = mod08.conformance_statement()
        self.assertEqual(statement["table_identifier"], "LR-1")
        self.assertEqual(statement["threshold_set"], "epoch weighted")

    def test_plain_unrecorded_table_refused_control(self):
        sentence = conformance_sentence(table_identifier="LR-9")
        self.assertIn("names no recorded table: LR-9", sentence)

    def test_plain_unrecorded_threshold_refused_control(self):
        sentence = conformance_sentence(threshold_set="bogus")
        self.assertIn("names no recorded threshold set: bogus", sentence)

    def test_plain_formula_table_delivered_control(self):
        statement = mod08.conformance_statement(
            table_identifier="threshold formula table")
        self.assertEqual(
            statement["table_identifier"], "threshold formula table")


class TestR20050ScoreDayUseSentence(unittest.TestCase):
    def test_lying_use_sentence_names_stored(self):
        sentence = score_sentence(uses=[LieStr("bogus", "conformance")])
        self.assertIn("scoring use stands unnamed: bogus", sentence)

    def test_raising_use_sentence_names_stored(self):
        sentence = score_sentence(uses=[RaiseStr("bogus")])
        self.assertIn("scoring use stands unnamed: bogus", sentence)

    def test_bytes_use_sentence_names_stored(self):
        sentence = score_sentence(uses=[b"bogus"])
        self.assertIn("scoring use stands unnamed: bogus", sentence)
        self.assertNotIn("b'bogus'", sentence)

    def test_plain_bogus_use_sentence_control(self):
        sentence = score_sentence(uses=["bogus"])
        self.assertIn("scoring use stands unnamed: bogus", sentence)


class TestR20051ThresholdSentence(unittest.TestCase):
    def test_lying_threshold_sentence_names_stored(self):
        sentence = conformance_sentence(
            threshold_set=LieStr("bogus", "epoch weighted"))
        self.assertIn("names no recorded threshold set: bogus", sentence)

    def test_raising_threshold_sentence_names_stored(self):
        sentence = conformance_sentence(threshold_set=RaiseStr("bogus"))
        self.assertIn("names no recorded threshold set: bogus", sentence)

    def test_bytes_threshold_sentence_names_stored(self):
        sentence = conformance_sentence(threshold_set=b"bogus")
        self.assertIn("names no recorded threshold set: bogus", sentence)
        self.assertNotIn("b'bogus'", sentence)

    def test_plain_bogus_threshold_sentence_control(self):
        sentence = conformance_sentence(threshold_set="bogus")
        self.assertIn("names no recorded threshold set: bogus", sentence)


class TestR20055AuthoredKindSentence(unittest.TestCase):
    def test_lying_kind_sentence_names_stored(self):
        sentence = author_sentence(LieStr("bogus kind", "sleeper class"))
        self.assertIn("authored kind stands unnamed: bogus kind", sentence)

    def test_bytes_kind_sentence_names_stored(self):
        sentence = author_sentence(b"bogus kind")
        self.assertIn("authored kind stands unnamed: bogus kind", sentence)
        self.assertNotIn("b'bogus kind'", sentence)

    def test_plain_bogus_kind_sentence_control(self):
        sentence = author_sentence("bogus kind")
        self.assertIn("authored kind stands unnamed: bogus kind", sentence)

    def test_plain_named_kind_authored_control(self):
        sealed = mod08.freeze_sealed_set(mod08.create_sealed_set())
        entry = mod08.author_sealed_class(
            sealed, "sleeper class", "id-1",
            separations=list(mod08._SEPARATIONS))
        self.assertEqual(entry["kind"], "sleeper class")


class TestR20056EmptyIdentifierSentence(unittest.TestCase):
    def record(self, identifier):
        return {
            "agent_identifier": identifier,
            "day": 3,
            "feature_values": {},
            "records_for_agent_and_day": [],
        }

    def test_lying_repr_identifier_sentence_names_stored_form(self):
        sentence = detection_sentence(
            self.record(LieStr("", "'innocent'")))
        self.assertIn("no identifier stands stated in it: ''", sentence)
        self.assertNotIn("innocent", sentence)

    def test_raising_repr_identifier_sentence_names_stored_form(self):
        sentence = detection_sentence(self.record(RaiseStr("")))
        self.assertIn("no identifier stands stated in it: ''", sentence)

    def test_plain_empty_identifier_sentence_control(self):
        sentence = detection_sentence(self.record(""))
        self.assertIn("no identifier stands stated in it: ''", sentence)


class TestR20057StreamsSentence(unittest.TestCase):
    def test_lying_repr_streams_sentence_names_stored_form(self):
        sentence = profiles_sentence(LieStr("bogus", "'42'"))
        self.assertIn("stands in no number form: 'bogus'", sentence)
        self.assertNotIn("'42'", sentence)

    def test_raising_repr_streams_sentence_names_stored_form(self):
        sentence = profiles_sentence(RaiseStr("bogus"))
        self.assertIn("stands in no number form: 'bogus'", sentence)

    def test_plain_bogus_streams_sentence_control(self):
        sentence = profiles_sentence("bogus")
        self.assertIn("stands in no number form: 'bogus'", sentence)


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class LyingIdentifier:
    def __repr__(self):
        return "'agent-9'"

    def __str__(self):
        return "agent-9"


class LyingDay:
    def __repr__(self):
        return "3"

    def __str__(self):
        return "3"


class LyingFeatureName:
    def __repr__(self):
        return "'feature_x'"

    def __str__(self):
        return "feature_x"


class RaisingRepr:
    def __repr__(self):
        raise RuntimeError("repr raises")

    def __str__(self):
        raise RuntimeError("str raises")


def figure(extra):
    output = {
        "profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }
    output.update(extra)
    return output


def record(**overrides):
    handed = {
        "agent_identifier": "agent-1",
        "day": 3,
        "feature_values": {"feature_x": 1},
        "records_for_agent_and_day": [],
    }
    handed.update(overrides)
    return handed


class TestR21018BarredVerdictContainerDress(unittest.TestCase):
    def test_tuple_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": ("pass",)})))

    def test_list_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": ["pass"]})))

    def test_set_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": {"pass"}})))

    def test_frozenset_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": frozenset({"pass"})})))

    def test_bytes_tuple_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": (b"pass",)})))

    def test_split_pair_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": ("pa", "ss")})))

    def test_outcome_key_tuple_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"outcome": ("pass",)})))

    def test_verdict_key_list_failed_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"verdict": ["failed"]})))

    def test_uppercase_tuple_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": ("PASS",)})))


class TestR21022IdentifierSentence(unittest.TestCase):
    def test_lying_identifier_named_by_stored_form(self):
        sentence = detection_sentence(
            record(agent_identifier=LyingIdentifier()))
        self.assertIn(
            "the agent identifier stands in no identifier form: "
            "LyingIdentifier", sentence)
        self.assertNotIn("agent-9", sentence)

    def test_raising_identifier_named_by_stored_form(self):
        sentence = detection_sentence(
            record(agent_identifier=RaisingRepr()))
        self.assertIn(
            "the agent identifier stands in no identifier form: "
            "RaisingRepr", sentence)

    def test_set_identifier_named_in_sorted_stored_form(self):
        sentence = detection_sentence(record(
            agent_identifier={
                "t5", "t1", "t3", "t2", "t7", "t4", "t6",
                LyingIdentifier()}))
        self.assertIn(
            "the agent identifier stands in no identifier form: "
            "{'t1', 't2', 't3', 't4', 't5', 't6', 't7', "
            "LyingIdentifier}",
            sentence)
        self.assertNotIn("agent-9", sentence)


class TestR21023DaySentence(unittest.TestCase):
    def test_lying_day_named_by_stored_form(self):
        sentence = detection_sentence(record(day=LyingDay()))
        self.assertIn(
            "the day stands in no stated simulated day form: "
            "LyingDay", sentence)
        self.assertFalse(sentence.endswith(": 3"))

    def test_raising_day_named_by_stored_form(self):
        sentence = detection_sentence(record(day=RaisingRepr()))
        self.assertIn(
            "the day stands in no stated simulated day form: "
            "RaisingRepr", sentence)

    def test_set_day_named_in_sorted_stored_form(self):
        sentence = detection_sentence(
            record(day={"d", "b", "a", LyingDay()}))
        self.assertIn(
            "the day stands in no stated simulated day form: "
            "{'a', 'b', 'd', LyingDay}", sentence)


class TestR21024FeatureNameSentence(unittest.TestCase):
    def test_lying_feature_name_named_by_stored_form(self):
        sentence = detection_sentence(
            record(feature_values={LyingFeatureName(): 1}))
        self.assertIn(
            "a feature name stands in no string form: "
            "LyingFeatureName", sentence)
        self.assertNotIn("feature_x", sentence)

    def test_raising_feature_name_named_by_stored_form(self):
        sentence = detection_sentence(
            record(feature_values={RaisingRepr(): 1}))
        self.assertIn(
            "a feature name stands in no string form: RaisingRepr",
            sentence)


class TestControls(unittest.TestCase):
    def test_control_plain_scalar_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": "pass"})))

    def test_control_buffer_pass_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": b"pass"})))
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": bytearray(b"pass")})))
        self.assertFalse(mod08.validate_output(
            figure({"score_verdict": memoryview(b"pass")})))

    def test_control_plain_outcome_failed_barred(self):
        self.assertFalse(mod08.validate_output(
            figure({"outcome": "failed"})))

    def test_control_innocent_output_valid(self):
        self.assertTrue(mod08.validate_output(figure({})))

    def test_control_unbarred_text_value_valid(self):
        self.assertTrue(mod08.validate_output(
            figure({"score_verdict": "WATCH"})))

    def test_control_unbarred_container_value_valid(self):
        self.assertTrue(mod08.validate_output(
            figure({"score_verdict": ("watch",)})))

    def test_control_joined_container_not_barred_valid(self):
        self.assertTrue(mod08.validate_output(
            figure({"score_verdict": ["pass", "extra"]})))

    def test_control_plain_record_accepted(self):
        accepted = mod08.accept_detection_input(record())
        self.assertEqual(accepted["agent_identifier"], "agent-1")
        self.assertEqual(accepted["day"], 3)
        self.assertEqual(accepted["feature_values"], {"feature_x": 1})

    def test_control_plain_identifier_form_sentence(self):
        sentence = detection_sentence(record(agent_identifier=5))
        self.assertIn(
            "the agent identifier stands in no identifier form: 5",
            sentence)

    def test_control_plain_day_form_sentence(self):
        sentence = detection_sentence(record(day="3"))
        self.assertIn(
            "the day stands in no stated simulated day form: '3'",
            sentence)

    def test_control_plain_feature_name_sentence(self):
        sentence = detection_sentence(record(feature_values={5: 1}))
        self.assertIn(
            "a feature name stands in no string form: 5", sentence)


if __name__ == "__main__":
    unittest.main()

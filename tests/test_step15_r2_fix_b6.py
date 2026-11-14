"""Step 15 re run, Fix Builder 6 pins. MOD-08 items R1-015, R1-016,
R1-022, R1-023, R1-049, R1-050, R1-051 and R1-073.

Plain simulated values only. No detection score is reported as a
pass or as a fail in this file: verdict states and accumulator
totals are read as recorded values only.
"""
import unittest

from crucible import mod01, mod08


def valid_record():
    return {
        "agent_identifier": "agent-b6",
        "day": 1,
        "feature_values": {"activity": 2},
        "records_for_agent_and_day": [],
    }


SEPARATIONS = [
    "authorship separation",
    "knowledge separation",
    "record separation",
]


class LieDayInt(int):
    """An int storing minus 5 whose comparisons claim it stands
    in range."""

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False


class LieIdentifierStr(str):
    """A str storing the empty string whose truth, length and
    text readings claim it names an agent."""

    def __bool__(self):
        return True

    def __len__(self):
        return 7

    def __str__(self):
        return "agent-b6"


class LieTotalFloat(float):
    """A float storing 0.0 whose text readings state a total of
    999."""

    def __str__(self):
        return "999"

    def __repr__(self):
        return "999"


class ItemsLieDict(dict):
    """A dict whose items reading hides every stored entry."""

    def items(self):
        return iter(())


class KeysLieDict(dict):
    """A dict whose keys reading names only the allowed fields."""

    def keys(self):
        return iter((
            "agent_identifier", "day", "feature_values",
            "records_for_agent_and_day"))


class ValuesCarrier:
    """An object merely carrying a values dict, stating no record
    form."""

    def __init__(self, values):
        self.values = values


class TestR1015BaseClassReadings(unittest.TestCase):
    def test_day_judged_on_stored_base_value(self):
        record = valid_record()
        record["day"] = LieDayInt(-5)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_identifier_judged_on_stored_base_value(self):
        record = valid_record()
        record["agent_identifier"] = LieIdentifierStr("")
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_feature_value_scored_on_stored_base_value(self):
        record = valid_record()
        record["feature_values"] = {"activity": LieTotalFloat(0.0)}
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(accepted["feature_values"], {"activity": 0.0})
        result = mod08.score_day([record])
        state = result["detection_states"][0]
        self.assertEqual(
            state["accumulator_values"]["total_feature_value"], "0.0")
        self.assertEqual(
            result["verdict_states"][0]["verdict_state"], "NO-SIGNAL")

    def test_plain_subclass_parts_carrying_values_stand(self):
        class PlainInt(int):
            pass

        class PlainStr(str):
            pass

        class PlainFloat(float):
            pass

        record = valid_record()
        record["day"] = PlainInt(2)
        record["agent_identifier"] = PlainStr("agent-b6")
        record["feature_values"] = {"activity": PlainFloat(3.0)}
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(accepted["day"], 2)
        self.assertEqual(accepted["agent_identifier"], "agent-b6")
        self.assertEqual(accepted["feature_values"], {"activity": 3.0})


class TestR1016BaseDictReadings(unittest.TestCase):
    def test_barred_search_reads_base_dict_items(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            ItemsLieDict({"ground_truth": "hidden"})]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_field_reading_reads_base_dict_keys(self):
        record = KeysLieDict(valid_record())
        dict.__setitem__(record, "extra_field", "outside")
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)


class TestR1022StatedRecordForm(unittest.TestCase):
    def test_values_carrier_without_stated_form_rejected(self):
        carrier = ValuesCarrier(valid_record())
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(carrier)

    def test_stated_detection_input_form_stands(self):
        stated = mod01.DetectionInput(valid_record())
        accepted = mod08.accept_detection_input(stated)
        self.assertEqual(accepted["agent_identifier"], "agent-b6")
        self.assertEqual(accepted["day"], 1)
        self.assertEqual(accepted["feature_values"], {"activity": 2})
        self.assertEqual(accepted["records_for_agent_and_day"], [])


class TestR1023FoldedBarredReading(unittest.TestCase):
    def test_dressed_ground_truth_keys_barred_at_depth(self):
        dressed = (
            "ground-truth",
            "ground truth",
            "GROUND TRUTH",
            "gr0und-truth",
            "gr\u043eund_truth",
            "member-ship",
            "can ary",
        )
        for key in dressed:
            record = valid_record()
            record["records_for_agent_and_day"] = [
                {"nested": [{"deep": {key: "hidden"}}]}]
            with self.assertRaises(
                    mod08.NamedDetectionFailure, msg=key):
                mod08.accept_detection_input(record)

    def test_legitimate_neighbour_keys_stand(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"nested": {"ground": "stated", "truthful_note": "kept",
                        "labelled_note": "kept"}}]
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(accepted["agent_identifier"], "agent-b6")


class TestR1049AuthoringAfterScoringClosed(unittest.TestCase):
    def test_authoring_barred_once_scoring_has_closed(self):
        sealed = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed)
        mod08.author_sealed_class(
            sealed, "sleeper class", "s1", SEPARATIONS)
        mod08.author_sealed_class(
            sealed, "honest challenge variant", "h1", SEPARATIONS)
        mod08.seal_sealed_set(sealed)
        mod08.unseal_sealed_set(sealed, scoring_closed=True)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed, "sleeper class", "late extra", SEPARATIONS)


class TestR1050ProfileStreamCountForm(unittest.TestCase):
    def test_non_number_stream_count_refused(self):
        for bad in ("1000", None, [1000], {"count": 1000}):
            profile_set = {
                "profiles": mod08.F06_PROFILES,
                "streams_per_profile": bad,
            }
            with self.assertRaises(
                    mod08.NamedDetectionFailure, msg=repr(bad)):
                mod08.score_profiles(profile_set)

    def test_number_stream_counts_keep_their_reading(self):
        profile_set = {
            "profiles": mod08.F06_PROFILES,
            "streams_per_profile": 1000,
        }
        result = mod08.score_profiles(profile_set)
        self.assertEqual(result["minimum_streams_per_profile"], 1000)
        profile_set["streams_per_profile"] = 10
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_profiles(profile_set)


class TestR1051FeatureNameForm(unittest.TestCase):
    def test_non_string_feature_name_refused_by_name(self):
        record = valid_record()
        record["feature_values"] = {1: 4}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_mixed_feature_names_raise_named_failure_not_type_error(self):
        record = valid_record()
        record["feature_values"] = {"activity": 1, 2: 3}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day([record])

    def test_string_feature_names_stand(self):
        accepted = mod08.accept_detection_input(valid_record())
        self.assertEqual(accepted["feature_values"], {"activity": 2})


class TestR1073BoundedVerdictRead(unittest.TestCase):
    def test_cyclic_output_validates_false(self):
        output = {
            "profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
            "score_verdict": None,
        }
        output["self"] = output
        self.assertFalse(mod08.validate_output(output))

    def test_depth_5000_output_validates_false(self):
        node = {"score_verdict": None}
        for _ in range(5000):
            node = {"inner": node}
        output = {
            "profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
            "score_verdict": None,
            "inner": node,
        }
        self.assertFalse(mod08.validate_output(output))

    def test_ordinary_and_shared_outputs_keep_their_reading(self):
        shared = {"note": "shared part"}
        output = {
            "profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
            "score_verdict": None,
            "first": shared,
            "second": shared,
        }
        self.assertTrue(mod08.validate_output(output))
        barred = dict(output)
        barred["score_verdict"] = "pass"
        self.assertFalse(mod08.validate_output(barred))


if __name__ == "__main__":
    unittest.main()

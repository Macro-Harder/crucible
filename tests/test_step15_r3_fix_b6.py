"""Step 15 re run Round 2, Fix Builder 6 pins. MOD-08 items
R2-001 (MOD-08 limb), R2-005 (MOD-08 limb), R2-030, R2-031,
R2-048 and R2-049.

Plain simulated values only. No detection score is reported in
this file in the barred reporting form: verdict material stands
here only as fixture data for the output validator, and profile
records are read as records only.
"""
import unittest

from crucible import mod08


def valid_record():
    return {
        "agent_identifier": "agent-b6-fix2",
        "day": 1,
        "feature_values": {"activity": 2},
        "records_for_agent_and_day": [],
    }


class LieIterList(list):
    """A list whose own iteration yields nothing, while its base
    class storage holds the given items."""

    def __iter__(self):
        return iter(())


class LieIterTuple(tuple):
    """A tuple whose own iteration yields nothing, while its base
    class storage holds the given items."""

    def __iter__(self):
        return iter(())


class TrojanPart:
    """A part standing inert at the check whose copy protocol
    returns a barred dict when a copy act honours it."""

    def __deepcopy__(self, memo):
        return {"ground_truth": "hidden", "membership": 1}


class LieCopyList(list):
    """A list whose copy protocol returns forged content, while
    its base class storage holds plain content."""

    def __deepcopy__(self, memo):
        return [{"ground_truth": "forged"}]


def frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


SMALL_CAPITAL_GROUNDTRUTH = (
    "\u0262\u0280\u1d0f\u1d1c\u0274\u1d05\u1d1b\u0280\u1d1c"
    "\u1d1b\u029c"
)


class TestR2001BarredSearchBaseIteration(unittest.TestCase):
    def test_lying_list_in_records_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = LieIterList(
            [{"ground_truth": 1}])
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_lying_tuple_in_records_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            LieIterTuple(({"canary": 1},))]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_lying_list_nested_in_plain_dict_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"note": LieIterList([{"ground_truth": 1}])}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_lying_list_in_output_read_by_validator(self):
        output = {
            mod08.PROFILE_BOUND_LABEL_FIELD: (
                mod08.PROFILE_LABEL_CARRIAGE),
            "score_verdict": None,
            "extra": LieIterList([{"score_verdict": "pass"}]),
        }
        self.assertFalse(mod08.validate_output(output))

    def test_lying_tuple_in_output_read_by_validator(self):
        output = {
            mod08.PROFILE_BOUND_LABEL_FIELD: (
                mod08.PROFILE_LABEL_CARRIAGE),
            "score_verdict": None,
            "extra": LieIterTuple(({"result": "fail"},)),
        }
        self.assertFalse(mod08.validate_output(output))

    def test_clean_lying_list_content_still_accepted(self):
        record = valid_record()
        record["records_for_agent_and_day"] = LieIterList(
            [{"note": "clean"}])
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(
            list(accepted["records_for_agent_and_day"]),
            [{"note": "clean"}])

    def test_plain_list_barred_control_still_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [{"ground_truth": 1}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)


class TestR2005AcceptanceCopyUndirected(unittest.TestCase):
    def test_trojan_part_not_materialised_in_accepted_record(self):
        trojan = TrojanPart()
        record = valid_record()
        record["records_for_agent_and_day"] = [trojan]
        accepted = mod08.accept_detection_input(record)
        stored = accepted["records_for_agent_and_day"]
        self.assertEqual(len(stored), 1)
        self.assertIs(stored[0], trojan)
        self.assertEqual(mod08._find_barred(accepted), [])

    def test_trojan_nested_in_plain_dict_not_materialised(self):
        trojan = TrojanPart()
        record = valid_record()
        record["records_for_agent_and_day"] = [{"note": trojan}]
        accepted = mod08.accept_detection_input(record)
        stored = accepted["records_for_agent_and_day"]
        self.assertIs(stored[0]["note"], trojan)
        self.assertEqual(mod08._find_barred(accepted), [])

    def test_list_copy_protocol_not_honoured(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            LieCopyList([{"note": "real"}])]
        accepted = mod08.accept_detection_input(record)
        stored = accepted["records_for_agent_and_day"]
        self.assertEqual(list(stored[0]), [{"note": "real"}])
        self.assertEqual(mod08._find_barred(accepted), [])

    def test_plain_record_copy_still_deep(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [{"note": {"x": 1}}]
        accepted = mod08.accept_detection_input(record)
        accepted["records_for_agent_and_day"][0]["note"]["x"] = 9
        self.assertEqual(
            record["records_for_agent_and_day"][0]["note"]["x"], 1)


class TestR2030NuAndTeReadings(unittest.TestCase):
    def test_nu_dressed_groundtruth_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"grou\u03bddtruth": 1}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_te_dressed_groundtruth_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"ground\u0442ruth": 1}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)


class TestR2031FrozensetBound(unittest.TestCase):
    def test_validate_output_past_bound_in_frozenset_chain(self):
        output = {
            mod08.PROFILE_BOUND_LABEL_FIELD: (
                mod08.PROFILE_LABEL_CARRIAGE),
            "score_verdict": None,
            "extra": frozenset_chain(150),
        }
        self.assertFalse(mod08.validate_output(output))

    def test_validate_output_mixed_chain_past_bound(self):
        value = frozenset_chain(150)
        mixed = {"level": {value}}
        output = {
            mod08.PROFILE_BOUND_LABEL_FIELD: (
                mod08.PROFILE_LABEL_CARRIAGE),
            "score_verdict": None,
            "extra": mixed,
        }
        self.assertFalse(mod08.validate_output(output))

    def test_acceptance_past_bound_in_frozenset_chain(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"payload": frozenset_chain(150)}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_shallow_frozenset_still_accepted(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"payload": frozenset_chain(5)}]
        accepted = mod08.accept_detection_input(record)
        self.assertEqual(
            accepted["records_for_agent_and_day"][0]["payload"],
            frozenset_chain(5))


class TestR2048SmallCapitalReading(unittest.TestCase):
    def test_small_capital_nested_key_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {SMALL_CAPITAL_GROUNDTRUTH: 1}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_small_capital_feature_name_rejected(self):
        record = valid_record()
        record["feature_values"] = {SMALL_CAPITAL_GROUNDTRUTH: 1}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_single_small_capital_letter_rejected(self):
        record = valid_record()
        record["records_for_agent_and_day"] = [
            {"\u0262round_truth": 1}]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)


class TestR2049NonFiniteStreamCount(unittest.TestCase):
    def _profile_set(self, streams):
        return {
            "profiles": list(mod08.F06_PROFILES),
            "streams_per_profile": streams,
        }

    def test_nan_stream_count_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_profiles(self._profile_set(float("nan")))

    def test_infinite_stream_count_refused(self):
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_profiles(self._profile_set(float("inf")))

    def test_finite_at_minimum_still_returned(self):
        result = mod08.score_profiles(self._profile_set(1000))
        self.assertEqual(result["fixture"], "F-06")


if __name__ == "__main__":
    unittest.main()

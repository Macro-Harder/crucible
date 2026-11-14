"""Step 15 rerun fix wave 12 pins, Builder 8, Group 8.

Rows pinned: R12-056 to R12-070 and R12-076 to R12-077 of the
Round 12 register, across crucible/mod03.py, crucible/mod08.py,
crucible/mod13.py, and the form 22 limb of crucible/mod01.py.
The proving acts are the acts the Round 12 source papers used:
Red 3 Findings 1, 2, 3, 7, and 8, Blue 3 Findings 1, 2, 5, 6,
and 7, Yellow 3 Findings 1, 2, 3, 4, 5, 6, 7, 8, and 9, and
Purple 1 Findings 1 and 2. Values are simulated and test
values only.
"""
import os
import subprocess
import sys
import unittest

from crucible import mod01, mod03, mod08, mod11, mod13

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_at_seed(code, seed):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(seed)
    env["PYTHONPATH"] = ROOT
    done = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True,
        env=env, cwd=ROOT, timeout=60)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return done.stdout.strip()


class LieGet(dict):
    """A record storing plain values whose get reading reports
    the values its lie mapping states instead."""

    def __init__(self, stored, lie):
        super().__init__(stored)
        self._lie = lie

    def get(self, key, default=None):
        if key in self._lie:
            return self._lie[key]
        return dict.get(self, key, default)


class RaiseGet(dict):
    """A record whose get reading raises a bare error."""

    def get(self, key, default=None):
        raise RuntimeError("get boom")


class LieItem(dict):
    """A record whose item reading reports a lie for one key."""

    def __init__(self, stored, lie_key, lie_value):
        super().__init__(stored)
        self._lie_key = lie_key
        self._lie_value = lie_value

    def __getitem__(self, key):
        if key == self._lie_key:
            return self._lie_value
        return dict.__getitem__(self, key)


class EqAll:
    """A value whose equality reading agrees with everything."""

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class LieEqStr(str):
    """A text value storing one text whose equality reading
    agrees with everything."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class TruthyEmptyStr(str):
    """A text value storing the empty text whose truth reading
    reports True and whose length reading reports 5."""

    def __bool__(self):
        return True

    def __len__(self):
        return 5


class FalsyList(list):
    """A list storing its items whose truth reading reports
    False."""

    def __bool__(self):
        return False


class LieDayInt(int):
    """An int storing 10 whose conversion reading reports 200."""

    def __new__(cls):
        return int.__new__(cls, 10)

    def __int__(self):
        return 200


class LieEnvFloat(float):
    """A float storing 2.0 whose conversion reading reports
    200.0."""

    def __new__(cls):
        return float.__new__(cls, 2.0)

    def __float__(self):
        return 200.0


class LenLieEmptyList(list):
    """A list storing no segment whose length reading reports
    one."""

    def __len__(self):
        return 1


class LenLieFullList(list):
    """A list storing one segment whose length reading reports
    zero."""

    def __len__(self):
        return 0


def registry_entry(**overrides):
    entry = mod01.minimal_valid_instance("22")
    entry.update({
        "claim_identifier": "claim-1",
        "sweep_family_identifier": "fam-1",
        "test_value": "0.01",
        "rank": 1,
        "threshold": 0.05,
        "outcome": "reported",
        "confirmation_outcome": "passed",
        "gate_failure": "none",
        "screening_run_identifiers": ["run-1", "run-2"],
        "held_out_confirmation_run_identifiers": ["run-3"],
        "phase_judgements": {
            "before_runs": "judged",
            "after_runs": "judged",
        },
    })
    entry.update(overrides)
    return entry


def run_record(run_id, status="completed"):
    return {
        "run_identifier": run_id,
        "sweep_family_identifier": "fam-1",
        "claim_identifier": "claim-1",
        "run_class": "screening",
        "run_status": status,
    }


def matching_log():
    return [
        run_record("run-1"),
        run_record("run-2", "failed"),
        run_record("run-3"),
    ]


def plain_record(identifier, signature="sig"):
    return {
        "archetype_id": identifier,
        "generator_signature": signature,
        "parameter_rows": [["r1"]],
        "farm_member": False,
        "ground_truth_label": None,
    }


class TestR12056FarmBytesTie(unittest.TestCase):

    CODE = (
        "from crucible.mod03 import construct_farm\n"
        "members = {bytes([97]), bytes([255, 97]), bytes([253, 97]),"
        " bytes([255, 253, 97]), bytes([128, 97]), bytes([98]),"
        " bytes([255, 98])}\n"
        "edges = [(bytes([97]), bytes([98])),"
        " (bytes([255, 97]), bytes([255, 98]))]\n"
        "result = construct_farm(members, 3, edges)\n"
        "farms = [[list(m) for m in farm['member_ids']]"
        " for farm in result['farms']]\n"
        "print(farms)\n"
        "print(sorted(result["
        "'internal_edge_count_per_farm_identity'].items()))\n"
    )

    def test_grouping_same_at_every_seed(self):
        expected_farms = (
            "[[97], [128, 97], [253, 97]] "
            "[[255, 97], [255, 253, 97], [98]] [[255, 98]]")
        for seed in (0, 1, 2, 42):
            out = run_at_seed(self.CODE, seed)
            farms_line, counts_line = out.splitlines()
            self.assertEqual(
                farms_line,
                "[[[97], [128, 97], [253, 97]], "
                "[[255, 97], [255, 253, 97], [98]], [[255, 98]]]",
                "seed %s" % seed)
            self.assertEqual(
                counts_line,
                "[('farm-0', 0), ('farm-1', 0), ('farm-2', 0)]",
                "seed %s" % seed)
            self.assertIn(expected_farms.split(" ")[0], farms_line)

    def test_order_key_breaks_decoded_tie_on_raw_bytes(self):
        first = mod03._member_order_key(b"\xffa")
        second = mod03._member_order_key(b"\xfda")
        third = mod03._member_order_key(b"a")
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, third)
        keys = [
            mod03._member_order_key(value)
            for value in (b"a", b"\xffa", b"\xfda", b"\xff\xfda",
                          b"\x80a", b"b", b"\xffb")]
        self.assertEqual(len(set(keys)), 7)


class TestR12057StoredKeyText(unittest.TestCase):

    CODE = (
        "from crucible.mod13 import compare_registry_against_run_log\n"
        "entry = {'claim_identifier': 'c1',"
        " 'sweep_family_identifier': 'f1',"
        " 'screening_run_identifiers': ['run-1'],"
        " 'held_out_confirmation_run_identifiers': [],"
        " 'outcome': 'reported', 'confirmation_outcome': 'passed',"
        " 'gate_failure': 'none', 'test_value': '0.01',"
        " 'rank': 1, 'threshold': 0.05}\n"
        "record = {'run_identifier': 'run-1',"
        " 'sweep_family_identifier': 'f1',"
        " 'claim_identifier': 'c1', 'run_status': 'completed'}\n"
        "log = {frozenset({'ru', 'ns'}): [record]}\n"
        "result = compare_registry_against_run_log(entry, log)\n"
        "print(result['passed'], result['bearing_run_identifiers'])\n"
    )

    def test_split_frozenset_key_reads_at_every_seed(self):
        for seed in (0, 1, 2, 7, 42):
            self.assertEqual(
                run_at_seed(self.CODE, seed), "True ['run-1']",
                "seed %s" % seed)

    def test_stored_get_reads_split_frozenset_key(self):
        log = {frozenset({"ru", "ns"}): ["the-runs"]}
        self.assertEqual(mod13._stored_get(log, "runs"), ["the-runs"])
        tuple_log = {("ru", "ns"): ["the-runs"]}
        self.assertEqual(
            mod13._stored_get(tuple_log, "runs"), ["the-runs"])


class TestR12058IdentifiersAgree(unittest.TestCase):

    def test_eq_all_instances_do_not_agree(self):
        record = run_record("run-9")
        record["sweep_family_identifier"] = EqAll(999)
        entry = registry_entry(
            screening_run_identifiers=["run-9"],
            held_out_confirmation_run_identifiers=[])
        entry["sweep_family_identifier"] = EqAll(5)
        self.assertFalse(mod13._identifiers_agree(EqAll(999), EqAll(5)))
        result = mod13.compare_registry_against_run_log(entry, [record])
        self.assertFalse(result["passed"])
        self.assertNotIn("run-9", result["bearing_run_identifiers"])

    def test_two_part_list_with_lying_first_part(self):
        first = [LieEqStr("fa"), "m"]
        second = ["zz", "m"]
        self.assertFalse(mod13._identifiers_agree(first, second))
        self.assertTrue(mod13._identifiers_agree(["fa", "m"], ["fa", "m"]))
        self.assertTrue(mod13._identifiers_agree(5, 5))
        self.assertFalse(mod13._identifiers_agree(5, 6))


class TestR12059CatalogueGetReading(unittest.TestCase):

    def test_lied_identifier_and_signature_not_delivered(self):
        record = LieGet(
            plain_record("real-id", "real-sig"),
            {"archetype_id": "fake-id",
             "generator_signature": "fake-sig"})
        catalogue = mod03.archetype_catalogue([record])
        self.assertIn("real-id", catalogue["entries"])
        self.assertNotIn("fake-id", catalogue["entries"])
        self.assertEqual(
            catalogue["entries"]["real-id"]["generator_signature"],
            "real-sig")

    def test_duplicate_stored_identifiers_refused(self):
        first = LieGet(plain_record("dup-id"), {"archetype_id": "id-one"})
        second = LieGet(plain_record("dup-id"), {"archetype_id": "id-two"})
        with self.assertRaises(ValueError):
            mod03.archetype_catalogue([first, second])

    def test_mirror_and_headline_and_extend_stamp(self):
        record = LieGet(
            plain_record("stored-1"), {"archetype_id": "ghost-1"})
        catalogue = mod03.archetype_catalogue([record])
        self.assertIn("stored-1", catalogue["entries"])
        self.assertNotIn("ghost-1", catalogue["entries"])
        self.assertTrue(
            mod03.run_headline_reportable(["stored-1"], [record]))
        self.assertFalse(
            mod03.run_headline_reportable(["ghost-1"], [record]))
        extended = mod03.extend_catalogue(
            [], record, strategy_class="fixed class")
        self.assertEqual(
            extended["version_stamp"]["added_archetype"], "stored-1")

    def test_raising_get_answers_on_stored_contents(self):
        record = RaiseGet(plain_record("stored-1"))
        catalogue = mod03.archetype_catalogue([record])
        self.assertIn("stored-1", catalogue["entries"])
        cast = mod03.build_cast(
            {"population_size": 1, "archetype_mix": {"stored-1": 1}},
            [record], strategy_class="fixed class")
        self.assertEqual(cast["population"], 1)


class TestR12060BehaviourGetReading(unittest.TestCase):

    def test_proposals_state_stored_action_and_identifier(self):
        record = LieGet(
            {"behaviour": LieGet(
                {"action": "stored-action"},
                {"action": "ghost-action"}),
             "archetype_id": "a"},
            {"archetype_id": "ghost"})
        proposals = mod03.archetype_behaviour(
            record, stream_state=[1.0])
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["action"], "stored-action")
        self.assertEqual(proposals[0]["archetype_id"], "a")


class TestR12061BuildCastPointReading(unittest.TestCase):

    def records(self):
        return [plain_record("honest"), plain_record("sleeper")]

    def test_reported_population_does_not_build_cast(self):
        point = LieGet(
            {"population_size": 99,
             "archetype_mix": {"honest": 1, "sleeper": 1}},
            {"population_size": 2, "population": 2})
        with self.assertRaises(ValueError):
            mod03.build_cast(
                point, self.records(), strategy_class="fixed class")

    def test_mirror_point_builds_on_stored_population(self):
        point = LieGet(
            {"population_size": 2,
             "archetype_mix": {"honest": 1, "sleeper": 1}},
            {"population_size": 99, "population": 99})
        cast = mod03.build_cast(
            point, self.records(), strategy_class="fixed class")
        self.assertEqual(cast["population"], 2)
        self.assertEqual(
            cast["archetype_counts"], {"honest": 1, "sleeper": 1})

    def test_reported_mix_membership_not_delivered(self):
        point = LieGet(
            {"population_size": 2, "archetype_mix": {"honest": 2}},
            {"archetype_mix": {"honest": 1, "sleeper": 1}})
        cast = mod03.build_cast(
            point, self.records(), strategy_class="fixed class")
        self.assertEqual(cast["archetype_counts"], {"honest": 2})


class TestR12062TruthReadings(unittest.TestCase):

    def test_empty_strategy_class_with_lying_truth_refused(self):
        with self.assertRaises(ValueError):
            mod03.extend_catalogue(
                [], plain_record("new-1"),
                strategy_class=TruthyEmptyStr(""))

    def test_record_set_with_lying_truth_not_lost(self):
        records = FalsyList(
            [plain_record("a-1"), plain_record("a-2")])
        catalogue = mod03.archetype_catalogue(records)
        self.assertEqual(sorted(catalogue["entries"]), ["a-1", "a-2"])
        extended = mod03.extend_catalogue(
            records, plain_record("a-3"), strategy_class="fixed class")
        self.assertEqual(extended["entries_before"], 2)
        self.assertEqual(extended["entries_after"], 3)


class TestR12063ColdSocietyDegree(unittest.TestCase):

    def test_day_subclass_conversion_lie(self):
        self.assertEqual(mod03.cold_society_degree(LieDayInt()), 0)
        self.assertEqual(mod03.cold_society_degree(10), 0)

    def test_envelope_subclass_conversion_lie(self):
        result = mod03.cold_society_degree(
            100, envelope=LieEnvFloat(), gate_passing_share=0.5)
        self.assertEqual(result, 1.0)
        self.assertEqual(
            mod03.cold_society_degree(
                100, envelope=2.0, gate_passing_share=0.5),
            1.0)


class TestR12064SealedSetReadings(unittest.TestCase):

    def test_seal_on_reported_authored_entries(self):
        sealed_set = LieGet(
            {"authored": [], "sealed": False},
            {"authored": [
                {"kind": "sleeper class"},
                {"kind": "honest challenge variant"}]})
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.seal_sealed_set(sealed_set)

    def test_seal_on_reported_entry_kinds(self):
        entries = [
            LieItem({"kind": "other"}, "kind", "sleeper class"),
            LieItem({"kind": "other"}, "kind",
                    "honest challenge variant"),
        ]
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.seal_sealed_set({"authored": entries})

    def test_score_sealed_on_reported_sealed_standing(self):
        sealed_set = LieGet(
            {"sealed": False, "authored": []}, {"sealed": True})
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_sealed(sealed_set)
        plain_sealed = {"sealed": True, "authored": []}
        self.assertEqual(
            mod08.score_sealed(plain_sealed)["standing"],
            "sealed until scoring closes")


class TestR12065ProfileAndNamingReadings(unittest.TestCase):

    def test_score_profiles_on_reported_set(self):
        profile_set = LieGet(
            {"profiles": ("bogus",), "streams_per_profile": 0},
            {"profiles": mod08.F06_PROFILES,
             "streams_per_profile": 2000})
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_profiles(profile_set)

    def test_validate_use_naming_on_reported_uses(self):
        artefact = LieGet(
            {"uses_named": []}, {"uses_named": ["conformance"]})
        with self.assertRaises(mod08.SilentUseMovement):
            mod08.validate_use_naming(artefact)


class TestR12066AuthorKindEquality(unittest.TestCase):

    def test_kind_with_lying_equality_refused(self):
        sealed_set = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed_set)
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed_set, LieEqStr("bogus kind"), "id-1",
                separations=("authorship separation",
                             "knowledge separation",
                             "record separation"))
        self.assertEqual(sealed_set["authored"], [])


class TestR12067StrictEqMemoryview(unittest.TestCase):

    def test_memoryview_parts_judged_by_content(self):
        first = {"field": memoryview(b"same-bytes")}
        second = {"field": memoryview(bytearray(b"same-bytes"))}
        self.assertTrue(mod13._strict_eq(first, second))
        third = {"field": memoryview(b"other-bytes")}
        self.assertFalse(mod13._strict_eq(first, third))
        self.assertTrue(mod13._strict_eq(
            {"field": bytearray(b"same-bytes")},
            {"field": bytearray(b"same-bytes")}))


class TestR12068ComparisonResultForms(unittest.TestCase):

    def test_claim_and_outcome_normalised_and_not_shared(self):
        outcome_bytes = bytearray(b"passed")
        entry = registry_entry(
            claim_identifier=b"claim-9",
            confirmation_outcome=outcome_bytes)
        log = matching_log()
        for record in log:
            record["claim_identifier"] = "claim-9"
        result = mod13.compare_registry_against_run_log(entry, log)
        self.assertTrue(result["passed"])
        self.assertEqual(result["claim_identifier"], "claim-9")
        self.assertIsInstance(result["claim_identifier"], str)
        self.assertEqual(result["confirmation_outcome"], "passed")
        self.assertIsInstance(result["confirmation_outcome"], str)
        outcome_bytes[:] = b"failed"
        self.assertEqual(result["confirmation_outcome"], "passed")


class TestR12069EntryRunIdentifierOrder(unittest.TestCase):

    CODE = (
        "from crucible.mod13 import compare_registry_against_run_log\n"
        "ids = {'run-a', 'run-b', 'run-c', 'run-d', 'run-e', 'run-f'}\n"
        "entry = {'claim_identifier': 'c1',"
        " 'sweep_family_identifier': 'f1',"
        " 'screening_run_identifiers': ids,"
        " 'held_out_confirmation_run_identifiers': [],"
        " 'outcome': 'reported', 'confirmation_outcome': 'passed',"
        " 'gate_failure': 'none', 'test_value': '0.01',"
        " 'rank': 1, 'threshold': 0.05}\n"
        "log = [{'run_identifier': rid,"
        " 'sweep_family_identifier': 'f1',"
        " 'claim_identifier': 'c1', 'run_status': 'completed'}"
        " for rid in sorted(ids)]\n"
        "result = compare_registry_against_run_log(entry, log)\n"
        "print(result['entry_run_identifiers'])\n"
        "print(result['absent_from_log_run_identifiers'])\n"
    )

    def test_set_identifiers_delivered_sorted_at_every_seed(self):
        for seed in (0, 1, 2, 42):
            out = run_at_seed(self.CODE, seed)
            lines = out.splitlines()
            self.assertEqual(
                lines[0],
                "['run-a', 'run-b', 'run-c', 'run-d', 'run-e', "
                "'run-f']",
                "seed %s" % seed)
            self.assertEqual(lines[1], "[]", "seed %s" % seed)

    def test_list_identifiers_keep_handed_order(self):
        entry = registry_entry(
            screening_run_identifiers=["run-2", "run-1"],
            held_out_confirmation_run_identifiers=["run-3"])
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertEqual(
            result["entry_run_identifiers"],
            ["run-2", "run-1", "run-3"])


class TestR12070ExtendHistoryGuard(unittest.TestCase):

    def segment(self):
        return {"run_id": "run-1", "rule_set_version": "v1"}

    def test_empty_history_with_lying_length_named_refusal(self):
        history = LenLieEmptyList()
        with self.assertRaises(mod13.NamedReplicationFailure):
            mod13.extend_history(history, self.segment())

    def test_full_history_with_lying_length_extends(self):
        history = LenLieFullList([self.segment()])
        result = mod13.extend_history(
            history, {"run_id": "run-2", "rule_set_version": "v1"})
        self.assertEqual(len(result), 2)


class TestR12076AmendedNoTextDress(unittest.TestCase):

    def check_all_refuse(self, entry):
        self.assertFalse(mod01.validate_record("22", entry))
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertFalse(result["passed"])
        self.assertFalse(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=matching_log()))

    def test_confirmation_outcome_dict_and_int_dress(self):
        for value in ({"x": "failed"}, {"failed": 1}, 5):
            with self.subTest(value=repr(value)):
                self.check_all_refuse(
                    registry_entry(confirmation_outcome=value))

    def test_gate_failure_dict_and_int_dress(self):
        for value in ({"x": "both gates"}, 5):
            with self.subTest(value=repr(value)):
                self.check_all_refuse(
                    registry_entry(gate_failure=value))

    def test_outcome_dict_and_int_dress_beside_failed(self):
        for value in ({"x": "reported"}, 5):
            with self.subTest(value=repr(value)):
                self.check_all_refuse(registry_entry(
                    outcome=value, confirmation_outcome="failed"))

    def test_plain_controls_stand(self):
        entry = registry_entry()
        self.assertTrue(mod01.validate_record("22", entry))
        result = mod13.compare_registry_against_run_log(
            entry, matching_log())
        self.assertTrue(result["passed"])
        self.assertTrue(mod11.validate_registry_entry(
            entry, compiler="registrar", checker="checker",
            run_log=matching_log()))


class TestR12077AmendedNoneValue(unittest.TestCase):

    def test_none_amended_fields_refused_at_comparison(self):
        cases = (
            {"confirmation_outcome": None},
            {"confirmation_outcome": None, "outcome": "not reported"},
            {"outcome": None, "confirmation_outcome": "failed"},
            {"gate_failure": None},
        )
        for overrides in cases:
            with self.subTest(overrides=repr(overrides)):
                entry = registry_entry(**overrides)
                self.assertFalse(mod01.validate_record("22", entry))
                result = mod13.compare_registry_against_run_log(
                    entry, matching_log())
                self.assertFalse(result["passed"])
                self.assertFalse(mod11.validate_registry_entry(
                    entry, compiler="registrar", checker="checker",
                    run_log=matching_log()))


if __name__ == "__main__":
    unittest.main()

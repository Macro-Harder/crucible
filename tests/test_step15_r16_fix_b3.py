"""Pins for fix wave 15, Builder 3, rows R15-025 to R15-038.

Each pin fails on the charged defect against the pristine tree and
passes after the cure. Settlement S-1 governs throughout: a part's
own copy, iteration, or reading protocol never supplies the reading
an act judges or delivers by.
"""
import collections.abc
import unittest

import crucible.mod01 as mod01
import crucible.mod06 as mod06
import crucible.mod07 as mod07
import crucible.mod08 as mod08
import crucible.mod09 as mod09
import crucible.mod10 as mod10
import crucible.mod11 as mod11


class LyingList(list):
    """A list storing stored_items whose iteration yields yielded."""

    def __init__(self, stored_items, yielded):
        super().__init__(stored_items)
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


class FabricatingIterable:
    """An object in no container form whose iteration yields items."""

    def __init__(self, yielded):
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


class MappingLie(collections.abc.Mapping):
    """A mapping in no dict form: it stores stored, and its mapping
    protocol readings yield yielded."""

    def __init__(self, stored, yielded):
        self._stored = stored
        self._yielded = yielded

    def __getitem__(self, key):
        return self._yielded[key]

    def __iter__(self):
        return iter(self._yielded)

    def __len__(self):
        return len(self._yielded)


class DeepcopyLie:
    def __deepcopy__(self, memo):
        return "FABRICATED-ID"


class DeepcopyRaise:
    def __deepcopy__(self, memo):
        raise RuntimeError("raising copy protocol")


def clean_record():
    return {
        "agent_identifier": "a1",
        "day": 1,
        "feature_values": {"activity": 1},
        "records_for_agent_and_day": [],
    }


def headline_values():
    values = {field: "value for " + field
              for field in mod11.HEADLINE_UNIT_FIELDS
              if field not in ("checkability_fields",
                               "run_registry_line")}
    values["claim_sentence"] = (
        "At the sampled points within the stated scope, the "
        "result holds for the sampled points only, and nothing "
        "is claimed beyond the stated limits.")
    values["grounding_sentence"] = (
        "This unit rests on the retained run records within "
        "the stated scope, and its limits are that nothing is "
        "claimed beyond the sampled points in this unit.")
    values["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording "
        "that DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes "
        "Parley Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is "
        "used in this unit.")
    return values


class TestR15025ContractStateCopies(unittest.TestCase):
    def test_contract_identifier_copied_apart(self):
        handed = ["contract-1"]
        state = mod06.escrow_contract_state(handed)
        self.assertIsNot(state["contract_identifier"], handed)
        handed.append("MUTATED")
        self.assertEqual(state["contract_identifier"], ["contract-1"])

    def test_standard_identifier_copied_apart(self):
        handed = ["profile-1"]
        state = mod06.escrow_contract_state(
            "c1", standard_or_profile_identifier=handed)
        self.assertIsNot(
            state["standard_or_profile_identifier"], handed)
        handed.append("MUTATED")
        self.assertEqual(
            state["standard_or_profile_identifier"], ["profile-1"])

    def test_window_n_copied_apart(self):
        handed = [7]
        state = mod06.escrow_contract_state(
            "c1", lost_contact_clause_on=True, window_n=handed)
        self.assertIsNot(state["lost_contact_window_n"], handed)
        handed.append(99)
        self.assertEqual(state["lost_contact_window_n"], [7])


class TestR15026ResultAndPauseCopies(unittest.TestCase):
    def test_result_values_copied_apart(self):
        k1 = ["k1-state"]
        lien = ["lien-state"]
        kind = ["kind-list"]
        result = mod06.escrow_result(
            kind,
            contract_state={"k1_and_l2_state": k1,
                            "lien_state": lien})
        self.assertIsNot(result["k1_and_l2_state"], k1)
        self.assertIsNot(result["lien_state"], lien)
        self.assertIsNot(result["kind"], kind)
        k1.append("MUTATED")
        self.assertEqual(result["k1_and_l2_state"], ["k1-state"])

    def test_pause_cap_stated_value_copied_apart(self):
        handed = bytearray(b"cap")
        record = mod06.pause_cap("B-3", stated_value=handed)
        delivered = record["per_variant_pause_value"]
        self.assertIsNot(delivered, handed)
        self.assertIsInstance(delivered, bytearray)
        handed[0] = ord("X")
        self.assertEqual(bytes(delivered), b"cap")


class TestR15027RunInstructionContext(unittest.TestCase):
    def test_non_dict_mapping_context_delivers_no_result(self):
        lie = MappingLie(
            {"claims_dq_answer": True},
            {"backup_key_registered_at_setup": True})
        with self.assertRaises(ValueError):
            mod06.run_instruction(
                "replace_backup_key", context=lie)


class TestR15028RecordFormNonDict(unittest.TestCase):
    def test_mapping_lie_form_does_not_validate(self):
        valid = mod01.minimal_valid_instance("1")
        bogus = dict(valid)
        bogus["family_identifier"] = None
        lie = MappingLie(bogus, valid)
        form_cls = mod01.FORM_TYPES["1"]
        form = form_cls(lie)
        self.assertFalse(form.validate())
        self.assertNotEqual(form.values, valid)


class TestR15029VersionStampNonDict(unittest.TestCase):
    def test_mapping_lie_stamp_does_not_validate(self):
        lie = MappingLie(
            {"family_version": "x"},
            {"family_version": "v", "family_manifest_hash": "h",
             "rule_version_set": "r"})
        stamp = mod01.VersionStamp(lie)
        self.assertFalse(
            mod01.validate_version_stamp(stamp, "h"))


class TestR15030TracerResultsNonDict(unittest.TestCase):
    def test_mapping_lie_result_not_recorded(self):
        lie = MappingLie(
            {"OS-1": "bogus-result"},
            {"OS-1": "passed as a record"})
        records = mod07.tracer_passage_records("run-r16", results=lie)
        first = [r for r in records
                 if r["open_semantic_item"] == "OS-1"]
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["result"], "not attempted")


class TestR15031Mod07ListCarriage(unittest.TestCase):
    def test_record_folding_reads_stored_rulings(self):
        handed = LyingList(["DQ-5"], ["DQ-9"])
        record = mod07.record_folding(
            {"choice_identifier": "c1"}, handed)
        self.assertEqual(record["rulings_recorded"], ["DQ-5"])

    def test_classify_seam_feedback_reads_stored_standings(self):
        handed = LyingList(["stored-x"], ["yielded-y"])
        record = mod07.classify_seam_feedback(
            "OS-1", {"choice_identifier": "c1"}, handed)
        self.assertEqual(
            record["both_standings_carried"], ["stored-x"])


class TestR15032Mod08Iteration(unittest.TestCase):
    def test_score_day_reads_stored_records(self):
        handed = LyingList([], [clean_record()])
        result = mod08.score_day(handed)
        self.assertEqual(result["detection_states"], [])

    def test_score_reads_stored_records(self):
        handed = LyingList([], [clean_record()])
        result = mod08.score(handed)
        self.assertEqual(result["detection_states"], [])

    def test_score_day_reads_stored_uses(self):
        handed = LyingList(["bogus-use"], ["conformance"])
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_day([clean_record()], uses=handed)


class TestR15033ScoreProfilesFallback(unittest.TestCase):
    def test_non_container_profiles_refused(self):
        profile_set = {
            "profiles": FabricatingIterable(
                list(mod08.F06_PROFILES)),
            "streams_per_profile": 1000,
        }
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.score_profiles(profile_set)


class TestR15034AuthorSealedClassFallback(unittest.TestCase):
    def test_list_subclass_separations_judged_on_stored(self):
        sealed = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed)
        handed = LyingList(["bogus"], list(mod08._SEPARATIONS))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed, "sleeper class", "id-1", handed)

    def test_non_container_separations_refused(self):
        sealed = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed)
        handed = FabricatingIterable(list(mod08._SEPARATIONS))
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.author_sealed_class(
                sealed, "sleeper class", "id-1", handed)


class TestR15035MakeStrategyRange(unittest.TestCase):
    def test_list_subclass_range_reads_stored(self):
        handed = LyingList([999], [1, 2])
        strategy = mod09.make_strategy(
            "s1", external_profit_range=handed)
        self.assertEqual(strategy["external_profit_range"], [999])

    def test_generator_range_not_delivered(self):
        def gen():
            yield 7
            yield 8
        strategy = mod09.make_strategy(
            "s1", external_profit_range=gen())
        self.assertEqual(strategy["external_profit_range"], [0])


class TestR15036BoundingHeadlineAxesFallback(unittest.TestCase):
    def test_non_container_axes_do_not_validate(self):
        headline = {
            "axes": FabricatingIterable(list(mod11.AXES)),
            "traces": [{"moved": True}, {"moved": False},
                       {"moved": True}],
            "rests_on_axis": "farm size",
        }
        self.assertFalse(mod11.validate_bounding_headline(
            headline, {}, {}))


class TestR15037HeadlineUnitCallerDict(unittest.TestCase):
    def test_mapping_lie_values_build_no_unit(self):
        mod10.retain_run_record({
            "run_id": "run-r16-b3-37",
            "run_identifier": "run-r16-b3-37",
            "record_state": "as retained"})
        valid = headline_values()
        bogus = dict(valid)
        bogus["extra_field_xyz"] = "extra"
        lie = MappingLie(bogus, valid)
        with self.assertRaises(ValueError):
            mod11.build_headline_unit_from_run(
                "run-r16-b3-37", lie)


class TestR15038FailureCarriageCopy(unittest.TestCase):
    def test_deepcopy_lie_run_id_recorded_as_itself(self):
        run_id = DeepcopyLie()
        family = {}
        result = mod11.build_headline_unit_from_run(
            run_id, {}, family_record=family)
        self.assertFalse(result["built"])
        self.assertEqual(len(family["named_failures"]), 1)
        self.assertIs(
            family["named_failures"][0]["run_identifier"], run_id)

    def test_deepcopy_raise_run_id_returns_failure(self):
        run_id = DeepcopyRaise()
        family = {}
        result = mod11.build_headline_unit_from_run(
            run_id, {}, family_record=family)
        self.assertFalse(result["built"])
        self.assertIs(result["failure"]["run_identifier"], run_id)
        self.assertEqual(len(family["named_failures"]), 1)
        self.assertIs(
            family["named_failures"][0]["run_identifier"], run_id)


if __name__ == "__main__":
    unittest.main()

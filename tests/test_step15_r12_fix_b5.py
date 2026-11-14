"""Fix wave 11 pins, Builder 5: rows R11-056 to R11-070.

MOD-01 and MOD-02 handed readings. Every act stands judged on
the stored contents of the handed mapping or value, read under
the governing stored text settlement, never through a get,
contains, getitem, truth, length, iteration, hash, equality,
string, or integer reading the handed form itself supplies.
The constructions are the source paper forms: a lie key storing
an unrelated name, hashing as the target field, and answering
True on equality; a mirror key storing the true field name while
hashing as an unrelated name; and handed mappings whose own get,
truth, contains, iteration, and getitem readings supply the
answer, beside mirror objects storing the contents plainly.
"""
import unittest

from crucible import mod01, mod02


class LieKey(str):
    """Stores an unrelated name, hashes as the target, eq True."""

    def __new__(cls, stored, target):
        value = str.__new__(cls, stored)
        value._target = target
        return value

    def __hash__(self):
        return str.__hash__(self._target)

    def __eq__(self, other):
        return True


class MirrorKey(str):
    """Stores the true name, hashes as an unrelated name."""

    def __hash__(self):
        return str.__hash__("an unrelated stored name")


class GetLieDict(dict):
    """Stores nothing; its get reading reports handed contents."""

    def __init__(self, reported):
        super().__init__()
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class GetMirrorDict(dict):
    """Stores contents plainly; its get reading reports nothing."""

    def get(self, key, default=None):
        return default


class LenLieDict(dict):
    """Stores a mapping plainly; its length reading reports 0."""

    def __len__(self):
        return 0


class LenLieStr(str):
    """Stores one text; its length reading reports a number."""

    def __new__(cls, stored, reported):
        value = str.__new__(cls, stored)
        value._reported = reported
        return value

    def __len__(self):
        return self._reported


class StrLieStr(str):
    """Stores one text; its string reading reports another."""

    def __str__(self):
        return "ghost"


class IntLie(int):
    """Stores one number; its int reading reports another."""

    def __new__(cls, stored, reported):
        value = int.__new__(cls, stored)
        value._reported = reported
        return value

    def __int__(self):
        return self._reported


class GetitemLieDict(dict):
    """Stores a mapping; its getitem reading reports 99."""

    def __getitem__(self, key):
        return 99


class ContainsLieDict(dict):
    """Stores a mapping; its contains reading reports False."""

    def __contains__(self, key):
        return False


class GhostPositions(dict):
    """Stores a dummy entry; iteration, contains, and getitem
    readings report a ghost stream at position 7."""

    def __iter__(self):
        return iter(("ghost",))

    def __contains__(self, key):
        return True

    def __getitem__(self, key):
        return 7


class TraceLieEntry(dict):
    """Stores nothing; get and getitem report one trace row."""

    def __init__(self, field, source_form, place):
        super().__init__()
        self._reported = {
            "field": field,
            "source_form": source_form,
            "place_in_single_record": place,
        }

    def get(self, key, default=None):
        return self._reported.get(key, default)

    def __getitem__(self, key):
        return self._reported[key]


COMPLETE_INPUT = {
    "derivation_version": "v1",
    "domain": "screening",
    "root_seed_reference": "root",
    "scenario_identifier": "scenario",
    "run_identifier": "run",
    "stream_class_identifier": "stream",
    "parameter_values": {"p1": "a", "p2": "b"},
}


class TestR11056Form15Components(unittest.TestCase):
    def test_part_supplied_only_by_lie_key_fails(self):
        instance = mod01.minimal_valid_instance("15")
        component = dict(instance["attacker_controlled_share"])
        del component["numerator"]
        component[LieKey("unrelated", "numerator")] = "stated value"
        instance["attacker_controlled_share"] = component
        self.assertFalse(mod01.validate_record("15", instance))

    def test_complete_component_under_mirror_key_passes(self):
        instance = mod01.minimal_valid_instance("15")
        complete = dict(instance["attacker_controlled_share"])
        del instance["attacker_controlled_share"]
        instance[MirrorKey("attacker_controlled_share")] = complete
        self.assertTrue(mod01.validate_record("15", instance))

    def test_plain_controls_stand(self):
        self.assertTrue(mod01.validate_record(
            "15", mod01.minimal_valid_instance("15")))
        instance = mod01.minimal_valid_instance("15")
        del instance["attacker_controlled_share"]["numerator"]
        self.assertFalse(mod01.validate_record("15", instance))


class TestR11057GenericAndLienLimbs(unittest.TestCase):
    def test_bogus_calibration_under_mirror_key_fails(self):
        for form_id in ("1", "2", "3", "5", "10", "13"):
            instance = mod01.minimal_valid_instance(form_id)
            instance[MirrorKey("calibration_claim_field")] = (
                "bogus calibration")
            self.assertFalse(
                mod01.validate_record(form_id, instance), form_id)

    def test_bogus_store_kind_under_mirror_key_fails(self):
        for form_id in ("1", "2", "3", "5", "10", "13"):
            instance = mod01.minimal_valid_instance(form_id)
            instance[MirrorKey("store_kind")] = "bogus kind"
            self.assertFalse(
                mod01.validate_record(form_id, instance), form_id)

    def test_bogus_lien_under_mirror_key_fails(self):
        instance = mod01.minimal_valid_instance("10")
        del instance["lien_state"]
        instance[MirrorKey("lien_state")] = "bogus lien"
        self.assertFalse(mod01.validate_record("10", instance))

    def test_plain_bogus_controls_fail(self):
        instance = mod01.minimal_valid_instance("2")
        instance["calibration_claim_field"] = "bogus calibration"
        self.assertFalse(mod01.validate_record("2", instance))
        instance = mod01.minimal_valid_instance("10")
        instance["lien_state"] = "bogus lien"
        self.assertFalse(mod01.validate_record("10", instance))


class TestR11058SlugAndParameterLimbs(unittest.TestCase):
    def test_slug_value_under_mirror_key_fails(self):
        instance = mod01.minimal_valid_instance("1")
        del instance["farm_size_steps"]
        instance[MirrorKey("farm_size_steps")] = "not an open marker"
        self.assertFalse(mod01.validate_record("1", instance))

    def test_parameter_values_under_mirror_key_fails(self):
        instance = mod01.minimal_valid_instance("5")
        del instance["parameter_values"]
        instance[MirrorKey("parameter_values")] = 12345
        self.assertFalse(mod01.validate_record("5", instance))

    def test_plain_controls_stand(self):
        instance = mod01.minimal_valid_instance("1")
        instance["farm_size_steps"] = "not an open marker"
        self.assertFalse(mod01.validate_record("1", instance))
        instance = mod01.minimal_valid_instance("5")
        instance["parameter_values"] = 12345
        self.assertFalse(mod01.validate_record("5", instance))
        self.assertTrue(mod01.validate_record(
            "5", mod01.minimal_valid_instance("5")))


class TestR11059SealActs(unittest.TestCase):
    def test_seal_fabricated_by_lie_keys_fails(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "hashA"}
        record = {
            LieKey("unrelated one", "family_version"): "v1",
            LieKey("unrelated two", "family_manifest_hash"): "hashA",
        }
        self.assertFalse(
            mod01.validate_family_seal_match(manifest, record))

    def test_seal_mirror_record_passes(self):
        manifest = {"family_version": "v1",
                    "sealed_family_record_hash": "hashA"}
        record = {
            MirrorKey("family_version"): "v1",
            MirrorKey("family_manifest_hash"): "hashA",
        }
        self.assertTrue(
            mod01.validate_family_seal_match(manifest, record))

    def test_seal_mirror_manifest_passes(self):
        manifest = {
            MirrorKey("family_version"): "v1",
            MirrorKey("sealed_family_record_hash"): "hashA",
        }
        record = {"family_version": "v1", "family_manifest_hash": "hashA"}
        self.assertTrue(
            mod01.validate_family_seal_match(manifest, record))

    def test_stamp_fabricated_by_lie_keys_fails(self):
        stamp = {
            LieKey("unrelated one", "family_version"): "v1",
            LieKey("unrelated two", "family_manifest_hash"): "hashA",
            LieKey("unrelated three", "rule_version_set"): "r1",
        }
        self.assertFalse(
            mod01.validate_version_stamp(stamp, sealed_family_hash="hashA"))

    def test_stamp_mirror_passes(self):
        stamp = {
            MirrorKey("family_version"): "v1",
            MirrorKey("family_manifest_hash"): "hashA",
            MirrorKey("rule_version_set"): "r1",
        }
        self.assertTrue(
            mod01.validate_version_stamp(stamp, sealed_family_hash="hashA"))

    def test_stamp_plain_controls_stand(self):
        stamp = {"family_version": "v1", "family_manifest_hash": "hashA",
                 "rule_version_set": "r1"}
        self.assertTrue(
            mod01.validate_version_stamp(stamp, sealed_family_hash="hashA"))
        stamp["family_manifest_hash"] = "wrong"
        self.assertFalse(
            mod01.validate_version_stamp(stamp, sealed_family_hash="hashA"))


def plain_block():
    return {
        "excluded_class_counts": {"a": 1},
        "excluded_class_shares": {"a": 1},
        "entries": [{"field": "plain field", "applicability": "applies"}],
    }


class TestR11060ProvenanceBlock(unittest.TestCase):
    def test_block_fabricated_by_lie_keys_fails(self):
        plain = plain_block()
        block = {
            LieKey("unrelated one", "excluded_class_counts"):
                plain["excluded_class_counts"],
            LieKey("unrelated two", "excluded_class_shares"):
                plain["excluded_class_shares"],
            LieKey("unrelated three", "entries"): [{
                LieKey("unrelated four", "field"): "plain field",
                LieKey("unrelated five", "applicability"): "applies",
            }],
        }
        self.assertFalse(mod01.validate_provenance_block(block))

    def test_block_mirror_passes(self):
        plain = plain_block()
        block = {
            MirrorKey("excluded_class_counts"):
                plain["excluded_class_counts"],
            MirrorKey("excluded_class_shares"):
                plain["excluded_class_shares"],
            MirrorKey("entries"): plain["entries"],
        }
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_block_plain_control_passes(self):
        self.assertTrue(mod01.validate_provenance_block(plain_block()))


class TestR11061RunIsReportable(unittest.TestCase):
    def test_failed_run_under_mirror_key_not_reportable(self):
        for form_id in ("2", "3", "5", "10"):
            instance = mod01.minimal_valid_instance(form_id)
            instance[MirrorKey("run_status")] = "failed"
            self.assertFalse(
                mod01.run_is_reportable(form_id, instance), form_id)

    def test_plain_controls_stand(self):
        for form_id in ("2", "3", "5", "10"):
            self.assertTrue(mod01.run_is_reportable(
                form_id, mod01.minimal_valid_instance(form_id)), form_id)
            instance = mod01.minimal_valid_instance(form_id)
            instance["run_status"] = "failed"
            self.assertFalse(
                mod01.run_is_reportable(form_id, instance), form_id)


class TestR11062RunStatusAndPartial(unittest.TestCase):
    def test_presented_mismatch_under_mirror_key_fails(self):
        record = {"run_status": "completed",
                  MirrorKey("presented_as"): "failed"}
        self.assertFalse(mod01.validate_run_status(record=record))

    def test_partial_marking_fabricated_by_lie_keys_fails(self):
        record = {
            LieKey("unrelated one", "partial"): True,
            LieKey("unrelated two", "marked_partial"): True,
        }
        self.assertFalse(mod01.partial_record_is_marked(record=record))

    def test_plain_controls_stand(self):
        self.assertFalse(mod01.validate_run_status(
            record={"run_status": "completed", "presented_as": "failed"}))
        self.assertTrue(mod01.partial_record_is_marked(
            record={"partial": True, "marked_partial": True}))
        self.assertFalse(mod01.partial_record_is_marked(
            record={"partial": True}))


class TestR11063ReconciliationTrace(unittest.TestCase):
    def test_lying_entries_storing_nothing_fail(self):
        plain = mod01.reconciliation_trace()
        lying = [
            TraceLieEntry(
                entry["field"], entry["source_form"],
                entry["place_in_single_record"])
            for entry in plain
        ]
        self.assertFalse(mod01.check_reconciliation_trace(lying))

    def test_plain_controls_stand(self):
        plain = mod01.reconciliation_trace()
        self.assertTrue(mod01.check_reconciliation_trace(plain))
        self.assertFalse(mod01.check_reconciliation_trace(plain[:-1]))


class TestR11064DerivationRecordBuilders(unittest.TestCase):
    def test_record_from_lying_get_is_empty(self):
        record = mod02.derivation_input_record(GetLieDict(COMPLETE_INPUT))
        self.assertIsNone(record["derivation_version_string"])
        self.assertEqual(record["parameter_values"], ())

    def test_record_from_mirror_get_is_full(self):
        mirror = GetMirrorDict()
        dict.update(mirror, COMPLETE_INPUT)
        record = mod02.derivation_input_record(mirror)
        self.assertEqual(record["derivation_version_string"], "v1")
        self.assertEqual(record["parameter_values"], ("p1=a", "p2=b"))

    def test_run_record_fields_from_lying_get_are_empty(self):
        fields = mod02.run_record_derivation_fields(
            GetLieDict(COMPLETE_INPUT))
        self.assertIsNone(fields["derivation_version"])
        self.assertEqual(fields["parameter_values"], {})

    def test_run_record_fields_from_mirror_get_are_full(self):
        mirror = GetMirrorDict()
        dict.update(mirror, COMPLETE_INPUT)
        fields = mod02.run_record_derivation_fields(mirror)
        self.assertEqual(fields["derivation_version"], "v1")
        self.assertEqual(
            fields["parameter_values"], {"p1": "a", "p2": "b"})

    def test_typed_input_from_lying_get_is_empty(self):
        typed = mod02.typed_derivation_input(GetLieDict(COMPLETE_INPUT))
        self.assertIsNone(typed.values["derivation_version_string"])
        self.assertEqual(typed.values["parameter_values"], ())

    def test_plain_control_is_full(self):
        record = mod02.derivation_input_record(dict(COMPLETE_INPUT))
        self.assertEqual(record["derivation_version_string"], "v1")
        self.assertEqual(record["parameter_values"], ("p1=a", "p2=b"))


class TestR11065CarriedPositions(unittest.TestCase):
    def carried(self, positions):
        state = mod02.checkpoint_generator_state(
            run_id="r", stream_classes=["real"], positions=positions)
        return state["stream_states"]

    def test_zero_length_reading_keeps_stored_position(self):
        positions = LenLieDict()
        dict.update(positions, {"real": 5})
        self.assertEqual(self.carried(positions), {"real": {"position": 5}})

    def test_getitem_reading_does_not_misstate_position(self):
        positions = GetitemLieDict()
        dict.update(positions, {"real": 5})
        self.assertEqual(self.carried(positions), {"real": {"position": 5}})

    def test_contains_reading_does_not_lose_position(self):
        positions = ContainsLieDict()
        dict.update(positions, {"real": 5})
        self.assertEqual(self.carried(positions), {"real": {"position": 5}})

    def test_ghost_stream_is_not_carried(self):
        positions = GhostPositions()
        dict.update(positions, {"dummy": 1})
        states = mod02.checkpoint_generator_state(
            run_id="r", positions=positions)["stream_states"]
        self.assertEqual(states, {"dummy": {"position": 1}})

    def test_resume_path_keeps_stored_position(self):
        positions = LenLieDict()
        dict.update(positions, {"real": 5})
        state = mod02.resume_consumed_generator_state(
            run_id="r", stream_classes=["real"], positions=positions)
        self.assertEqual(
            state["stream_states"], {"real": {"position": 5}})

    def test_plain_control_stands(self):
        self.assertEqual(
            self.carried({"real": 5}), {"real": {"position": 5}})


class TestR11066DrawAndInitialState(unittest.TestCase):
    def test_draw_from_lying_get_state_is_not_exhausted(self):
        state = GetLieDict({
            "stream_class": "s", "position": 99, "carried_positions": 10})
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(state=state)

    def test_draw_with_int_lie_position_stands_at_stored_position(self):
        result = mod02.draw_from_stream(state={
            "stream_class": "s", "position": IntLie(0, 99),
            "carried_positions": 10})
        self.assertEqual(result["position"], 0)
        self.assertNotEqual(result.get("run_status"), "failed")

    def test_initial_state_with_int_lie_carried_positions(self):
        state = mod02.initial_stream_state("s", IntLie(3, 99))
        self.assertEqual(state["carried_positions"], 3)

    def test_plain_controls_stand(self):
        exhausted = mod02.draw_from_stream(state={
            "stream_class": "s", "position": 99, "carried_positions": 10})
        self.assertEqual(exhausted["position"], 99)
        self.assertEqual(exhausted["run_status"], "failed")
        inside = mod02.draw_from_stream(state={
            "stream_class": "s", "position": 0, "carried_positions": 10})
        self.assertEqual(inside["position"], 0)


class TestR11067StreamSetClasses(unittest.TestCase):
    def test_inventory_supplied_only_by_lie_key_fails(self):
        stream_set = {
            LieKey("unrelated", "stream_class_inventory"): ["cls1"]}
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality({"cls1": 1}, stream_set)

    def test_entry_name_supplied_only_by_lie_key_fails(self):
        entry = {LieKey("unrelated", "name"): "cls1"}
        stream_set = {"stream_class_inventory": [entry]}
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality({"cls1": 1}, stream_set)

    def test_inventory_under_mirror_key_passes(self):
        stream_set = {MirrorKey("stream_class_inventory"): ["cls1"]}
        self.assertTrue(
            mod02.validate_stream_cardinality({"cls1": 1}, stream_set))

    def test_plain_control_passes(self):
        self.assertTrue(mod02.validate_stream_cardinality(
            {"cls1": 1}, {"stream_class_inventory": ["cls1"]}))


class TestR11068BatteryRecord(unittest.TestCase):
    def record(self, element):
        return {
            "single_stream_results": {"fam1": "result"},
            "inter_stream_element": {"fam1": element},
        }

    def test_empty_element_with_length_five_fails(self):
        self.assertFalse(mod02.validate_battery_record(
            self.record(LenLieStr("", 5))))

    def test_complete_element_with_length_zero_passes(self):
        self.assertTrue(mod02.validate_battery_record(
            self.record(LenLieStr("real", 0))))

    def test_plain_controls_stand(self):
        self.assertTrue(mod02.validate_battery_record(self.record("real")))
        record = {"single_stream_results": {"fam1": "result"},
                  "inter_stream_element": {}}
        self.assertFalse(mod02.validate_battery_record(record))


class TestR11069BuilderOrTests(unittest.TestCase):
    def test_make_derivation_input_keeps_stored_parameters(self):
        params = LenLieDict()
        dict.update(params, {"p1": "a"})
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values=params)
        self.assertEqual(built["parameter_values"], {"p1": "a"})

    def test_make_exposure_log_entry_keeps_stored_value(self):
        values = LenLieDict()
        first = mod02.exposure_log_fields()[0]
        dict.update(values, {first: "channeled"})
        entry = mod02.make_exposure_log_entry(values)
        self.assertEqual(entry[first], "channeled")

    def test_plain_controls_stand(self):
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values={"p1": "a"})
        self.assertEqual(built["parameter_values"], {"p1": "a"})
        first = mod02.exposure_log_fields()[0]
        entry = mod02.make_exposure_log_entry({first: "channeled"})
        self.assertEqual(entry[first], "channeled")


class TestR11070EncodeCandidateInput(unittest.TestCase):
    def test_value_length_prefix_states_stored_length(self):
        encoded = mod02.encode_candidate_input({"p": LenLieStr("ab", 99)})
        self.assertEqual(encoded, "str:1:p=2:ab")

    def test_key_name_states_stored_name(self):
        encoded = mod02.encode_candidate_input({StrLieStr("p"): "ab"})
        self.assertTrue(encoded.endswith(":1:p=2:ab"))
        self.assertNotIn("ghost", encoded)

    def test_plain_control_stands(self):
        self.assertEqual(
            mod02.encode_candidate_input({"p": "ab"}), "str:1:p=2:ab")


if __name__ == "__main__":
    unittest.main()

import unittest

from crucible import mod01, mod03, mod04, mod05, mod06, mod07, mod08
from crucible import mod12, mod13


class ArmedKey:
    armed = False

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 7

    def __eq__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed equality")
        return False

    def __ne__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed inequality")
        return True


class HashKey:
    armed = False

    def __hash__(self):
        if HashKey.armed:
            raise RuntimeError("armed hash")
        return 7

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


def armed_inner():
    ArmedKey.armed = False
    inner = {ArmedKey("a"): 1, ArmedKey("b"): 2}
    ArmedKey.armed = True
    return inner


def hash_inner():
    HashKey.armed = False
    inner = {HashKey(): 1}
    HashKey.armed = True
    return inner


def armed_set(form):
    ArmedKey.armed = False
    items = form((ArmedKey("a"), ArmedKey("b")))
    ArmedKey.armed = True
    return items


class StrRaises(str):
    def __str__(self):
        raise RuntimeError("str boom")


class LieEqStr(str):
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqRaisesStr(str):
    def __eq__(self, other):
        raise RuntimeError("eq boom")

    def __ne__(self, other):
        raise RuntimeError("ne boom")

    __hash__ = str.__hash__


class ReprRaises:
    def __repr__(self):
        raise RuntimeError("repr boom")

    def __str__(self):
        raise RuntimeError("str boom")


class BufferStrRaises(bytearray):
    def __str__(self):
        raise RuntimeError("str boom")


class Base(unittest.TestCase):
    def tearDown(self):
        ArmedKey.armed = False
        HashKey.armed = False


class TestR19001EntryKind(Base):
    def test_lying_equality_kind_refused(self):
        with self.assertRaises(ValueError):
            mod01.minimal_valid_instance(
                "36", entry_kind=LieEqStr("bogus"))

    def test_raising_equality_kind_refused_named(self):
        with self.assertRaises(ValueError):
            mod01.minimal_valid_instance(
                "36", entry_kind=EqRaisesStr("bogus"))

    def test_raising_equality_agent_kind_delivered(self):
        instance = mod01.minimal_valid_instance(
            "36", entry_kind=EqRaisesStr("agent"))
        self.assertIn("agent_identifier", instance)
        self.assertNotIn("superseded_from_journal_position", instance)

    def test_raising_string_kind_refused_named(self):
        with self.assertRaises(ValueError):
            mod01.minimal_valid_instance(
                "36", entry_kind=StrRaises("bogus"))

    def test_plain_bogus_kind_control(self):
        with self.assertRaises(ValueError) as caught:
            mod01.minimal_valid_instance("36", entry_kind="bogus")
        self.assertIn("unknown entry kind: bogus", str(caught.exception))

    def test_plain_kinds_control(self):
        ordinary = mod01.minimal_valid_instance(
            "36", entry_kind="ordinary")
        self.assertNotIn("agent_identifier", ordinary)
        self.assertNotIn("superseded_from_journal_position", ordinary)
        agent = mod01.minimal_valid_instance("36", entry_kind="agent")
        self.assertIn("agent_identifier", agent)
        self.assertNotIn("superseded_from_journal_position", agent)
        supered = mod01.minimal_valid_instance(
            "36", entry_kind="supersession")
        self.assertIn("superseded_from_journal_position", supered)
        self.assertIn("resume_attempt_identifier", supered)
        self.assertNotIn("agent_identifier", supered)


class TestR19013Mod01Copy(Base):
    def test_version_stamp_armed_inner_carried(self):
        stamp = mod01.VersionStamp({"nested": armed_inner()})
        nested = stamp.as_dict()["nested"]
        self.assertEqual(len(nested), 2)
        self.assertEqual(sorted(nested.values()), [1, 2])

    def test_plain_stamp_control(self):
        stamp = mod01.VersionStamp({"nested": {"a": 1, "b": 2}})
        self.assertEqual(
            stamp.as_dict()["nested"], {"a": 1, "b": 2})


class TestR19014Mod03Copy(Base):
    def test_archetype_armed_inner_carried(self):
        record = mod03.make_archetype_record(
            behaviour={"nested": armed_inner()})
        nested = record["behaviour"]["nested"]
        self.assertEqual(len(nested), 2)
        self.assertEqual(sorted(nested.values()), [1, 2])

    def test_plain_archetype_control(self):
        record = mod03.make_archetype_record(
            behaviour={"nested": {"a": 1}})
        self.assertEqual(record["behaviour"]["nested"], {"a": 1})


class TestR19015Mod06Copy(Base):
    def test_escrow_armed_inner_carried(self):
        result = mod06.escrow_result(
            "kind", payload={"nested": armed_inner()})
        nested = result["payload"]["nested"]
        self.assertEqual(len(nested), 2)
        self.assertEqual(sorted(nested.values()), [1, 2])

    def test_plain_escrow_control(self):
        result = mod06.escrow_result(
            "kind", payload={"nested": {"a": 1}})
        self.assertEqual(result["payload"]["nested"], {"a": 1})


class TestR19016Mod07Copy(Base):
    def test_adapter_armed_inner_carried(self):
        record = mod07.make_adapter_choice(
            "choice-1", "reading", "point", "text-1", "fold-1",
            approval={"nested": armed_inner()})
        nested = record["approval"]["nested"]
        self.assertEqual(len(nested), 2)
        self.assertEqual(sorted(nested.values()), [1, 2])

    def test_plain_adapter_control(self):
        record = mod07.make_adapter_choice(
            "choice-1", "reading", "point", "text-1", "fold-1",
            approval={"nested": {"a": 1}})
        self.assertEqual(record["approval"]["nested"], {"a": 1})


class TestR19017Mod08Copy(Base):
    def test_score_day_copy_armed_inner_carried(self):
        copied = mod08._undirected_copy({"nested": armed_inner()})
        nested = copied["nested"]
        self.assertEqual(len(nested), 2)
        self.assertEqual(sorted(nested.values()), [1, 2])

    def test_plain_score_day_control(self):
        result = mod08.score_day(
            [], society_state={"nested": {"a": 1}})
        self.assertIsInstance(result, dict)


class TestR19021FreezeEquality(Base):
    def test_mod04_freeze_equality_carried(self):
        copied = mod04._freeze(armed_inner())
        self.assertEqual(len(copied), 2)
        self.assertEqual(sorted(copied.values()), [1, 2])

    def test_mod05_freeze_equality_carried(self):
        copied = mod05._freeze(armed_inner())
        self.assertEqual(len(copied), 2)
        self.assertEqual(sorted(copied.values()), [1, 2])

    def test_mod12_freeze_equality_carried(self):
        copied = mod12._freeze(armed_inner())
        self.assertEqual(len(copied), 2)
        self.assertEqual(sorted(copied.values()), [1, 2])

    def test_mod13_freeze_equality_carried(self):
        copied = mod13._freeze(armed_inner())
        self.assertEqual(len(copied), 2)
        self.assertEqual(sorted(copied.values()), [1, 2])

    def test_mod04_handover_equality_carried(self):
        handover = mod04.ContractAHandover(
            armed_inner(), {}, set(), "fam-1")
        self.assertEqual(len(handover.point), 2)

    def test_mod12_admit_claim_equality_carried(self):
        result = mod12.admit_claim({}, claim=armed_inner())
        self.assertEqual(len(result["claim"]), 2)


class TestR19022FreezeHash(Base):
    def check_hash_carried(self, freeze):
        copied = freeze(hash_inner())
        self.assertEqual(list(copied.keys()), ["(carried key 3)"])
        self.assertEqual(list(copied.values()), [1])

    def test_mod04_freeze_hash_carried(self):
        self.check_hash_carried(mod04._freeze)

    def test_mod05_freeze_hash_carried(self):
        self.check_hash_carried(mod05._freeze)

    def test_mod12_freeze_hash_carried(self):
        self.check_hash_carried(mod12._freeze)

    def test_mod13_freeze_hash_carried(self):
        self.check_hash_carried(mod13._freeze)


class TestR19023FreezeSets(Base):
    def check_set_list_form(self, freeze):
        copied = freeze(armed_set(set))
        self.assertIsInstance(copied, list)
        self.assertEqual(len(copied), 2)
        copied = freeze(armed_set(frozenset))
        self.assertIsInstance(copied, list)
        self.assertEqual(len(copied), 2)

    def test_mod05_set_limbs_list_form(self):
        self.check_set_list_form(mod05._freeze)

    def test_mod12_set_limbs_list_form(self):
        self.check_set_list_form(mod12._freeze)

    def test_mod13_set_limbs_list_form(self):
        self.check_set_list_form(mod13._freeze)

    def test_plain_set_control(self):
        self.assertEqual(mod05._freeze({1, 2}), {1, 2})
        self.assertEqual(
            mod12._freeze(frozenset((1, 2))), frozenset((1, 2)))
        self.assertEqual(mod13._freeze({1, 2}), {1, 2})


class TestR19028PanelCleanPath(Base):
    def test_panel_inputs_raising_key_delivered(self):
        result = mod05.panel_inputs(
            {"plain": 1, StrRaises("feat"): 3})
        self.assertEqual(len(result), 2)
        self.assertEqual(result["plain"], 1)
        self.assertEqual(sorted(result.values()), [1, 3])

    def test_plain_panel_control(self):
        self.assertEqual(mod05.panel_inputs({"plain": 1}), {"plain": 1})


class TestR19029CleanValuePath(Base):
    def test_feature_raising_key_delivered(self):
        result = mod04.project_detection_input({
            "agent_identifier": "agent-1", "day": 1,
            "feature_values": {StrRaises("feat"): 3},
            "rule_records": []})
        self.assertEqual(len(result["feature_values"]), 1)
        self.assertEqual(list(result["feature_values"].values()), [3])

    def test_rule_record_raising_key_delivered(self):
        result = mod04.project_detection_input({
            "agent_identifier": "agent-1", "day": 1,
            "feature_values": {},
            "rule_records": [{StrRaises("feat"): 3}]})
        self.assertEqual(len(result["rule_records"]), 1)
        self.assertEqual(list(result["rule_records"][0].values()), [3])

    def test_plain_projection_control(self):
        result = mod04.project_detection_input({
            "agent_identifier": "agent-1", "day": 1,
            "feature_values": {"feat": 3},
            "rule_records": []})
        self.assertEqual(result["feature_values"], {"feat": 3})


class TestR19030ProvenanceField(Base):
    def test_buffer_raising_field_returns_boolean(self):
        block = {
            "entries": [{"field": BufferStrRaises(b"field"),
                         "applicability": "applies"}],
            "excluded_class_counts": {"a": 1},
            "excluded_class_shares": {"a": 1}}
        self.assertTrue(mod01.validate_provenance_block(block))

    def test_plain_buffer_field_control(self):
        block = {
            "entries": [{"field": bytearray(b"field"),
                         "applicability": "applies"}],
            "excluded_class_counts": {"a": 1},
            "excluded_class_shares": {"a": 1}}
        self.assertTrue(mod01.validate_provenance_block(block))


class TestR19031BarredFieldLabel(Base):
    def test_label_tuple_raising_part_rendered(self):
        label = mod04._barred_field_label(("membership", ReprRaises()))
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_build_view_record_tuple_key_refused_named(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(
                contents=[{("membership", ReprRaises()): 1}])
        self.assertIn("barred field", str(caught.exception))

    def test_plain_barred_key_control(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(contents=[{"membership": 1}])
        self.assertIn("membership", str(caught.exception))


class TestR19043CleanLeafBuffers(Base):
    def test_bytearray_part_copied_apart(self):
        buffer = bytearray(b"cfg")
        result = mod04.project_detection_input({
            "agent_identifier": "a1", "day": 3,
            "feature_values": {"f": [buffer]},
            "rule_records": []})
        delivered = result["feature_values"]["f"][0]
        self.assertIsNot(delivered, buffer)
        buffer[0] = ord("X")
        self.assertEqual(bytes(delivered), b"cfg")

    def test_memoryview_part_copied_apart(self):
        backing = bytearray(b"cfg")
        result = mod04.project_detection_input({
            "agent_identifier": "a1", "day": 3,
            "feature_values": {"f": [memoryview(backing)]},
            "rule_records": []})
        delivered = result["feature_values"]["f"][0]
        backing[0] = ord("X")
        self.assertEqual(bytes(delivered), b"cfg")

    def test_plain_leaf_control(self):
        result = mod04.project_detection_input({
            "agent_identifier": "a1", "day": 3,
            "feature_values": {"f": ["cfg"]},
            "rule_records": []})
        self.assertEqual(result["feature_values"], {"f": ["cfg"]})


if __name__ == "__main__":
    unittest.main()

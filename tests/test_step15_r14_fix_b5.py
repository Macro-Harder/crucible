"""Step 15 rerun fix wave 13 pins, Builder 5, Group 5.

Rows pinned: R13-021 to R13-023, R13-037, R13-038, and R13-039
of the Round 13 register, the copy family under settlement S-1
across crucible/mod01.py, crucible/mod03.py, crucible/mod06.py,
crucible/mod07.py, and crucible/mod08.py. The proving acts are
the acts the Round 13 source papers used: Red 2 Findings 1, 2,
and 3, Purple 4 Findings 1 and 2, Purple 2 Finding 1, and
Yellow 1 Findings Y1-1 and Y1-2. Values are simulated and test
values only.
"""
import unittest

from crucible import mod01, mod03, mod06, mod07, mod08


class LieCopy:
    """A part whose copy protocol returns a fabricated value."""

    def __init__(self, fabricated):
        self.fabricated = fabricated

    def __deepcopy__(self, memo):
        return self.fabricated

    def __copy__(self):
        return self.fabricated


class RaiseCopy:
    """A part whose copy protocol raises a bare error."""

    def __deepcopy__(self, memo):
        raise RuntimeError("copy boom")

    def __copy__(self):
        raise RuntimeError("copy boom")


class LieInt(int):
    """An int subclass storing 4 whose copy protocol returns 4000."""

    def __new__(cls):
        return int.__new__(cls, 4)

    def __deepcopy__(self, memo):
        return 4000


class GhostRecord(dict):
    """A record whose copy protocol returns a wholly different
    record in place of the one it stores."""

    def __deepcopy__(self, memo):
        return {
            "agent_identifier": "ghost-agent",
            "day": 9,
            "feature_values": {"activity": 99},
            "records_for_agent_and_day": [],
        }


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


def cast_records():
    return [
        mod03.make_archetype_record(
            archetype_id="honest", behaviour={"action": "vouch"},
            parameter_rows=[{"row": "honest row"}],
            ground_truth_label="honest"),
        mod03.make_archetype_record(
            archetype_id="sleeper", behaviour={"action": "wait"},
            parameter_rows=[{"row": "sleeper row"}],
            ground_truth_label="sleeper"),
    ]


class TestR13038VersionStamp(unittest.TestCase):

    def test_lying_hash_stands_as_itself_and_does_not_validate(self):
        leaf = LieCopy("sealed-hash")
        stamp = mod01.VersionStamp({
            "family_version": "v1",
            "family_manifest_hash": leaf,
            "rule_version_set": "r1",
        })
        self.assertIs(
            stamp.as_dict()["family_manifest_hash"], leaf)
        self.assertFalse(mod01.validate_version_stamp(
            stamp, sealed_family_hash="sealed-hash"))

    def test_raising_protocol_escapes_no_bare_error(self):
        leaf = RaiseCopy()
        stamp = mod01.VersionStamp({
            "family_version": "v1",
            "family_manifest_hash": "h",
            "rule_version_set": leaf,
        })
        self.assertIs(stamp.as_dict()["rule_version_set"], leaf)

    def test_stamp_values_copied_apart_from_caller(self):
        handed = ["a"]
        stamp = mod01.VersionStamp({
            "family_version": "v1",
            "family_manifest_hash": "h",
            "rule_version_set": handed,
        })
        handed.append("caller change")
        self.assertEqual(stamp.as_dict()["rule_version_set"], ["a"])
        read_back = stamp.as_dict()
        read_back["rule_version_set"].append("reader change")
        self.assertEqual(stamp.as_dict()["rule_version_set"], ["a"])

    def test_honest_stamp_validates_and_wrong_hash_fails(self):
        stamp = mod01.VersionStamp({
            "family_version": "v1",
            "family_manifest_hash": "sealed-hash",
            "rule_version_set": "r1",
        })
        self.assertTrue(mod01.validate_version_stamp(
            stamp, sealed_family_hash="sealed-hash"))
        wrong = mod01.VersionStamp({
            "family_version": "v1",
            "family_manifest_hash": "wrong",
            "rule_version_set": "r1",
        })
        self.assertFalse(mod01.validate_version_stamp(
            wrong, sealed_family_hash="sealed-hash"))


class TestR13038ProvenanceBlock(unittest.TestCase):

    def test_lying_count_stands_as_itself(self):
        leaf = LieCopy(3)
        block = mod01.ProvenanceBlock(
            [], {"excluded": leaf}, {})
        self.assertIs(
            block.as_dict()["excluded_class_counts"]["excluded"],
            leaf)

    def test_raising_protocol_escapes_no_bare_error(self):
        leaf = RaiseCopy()
        block = mod01.ProvenanceBlock(
            [{"entry": leaf}], {"excluded": 1}, {})
        self.assertIs(
            block.as_dict()["entries"][0]["entry"], leaf)

    def test_buffer_part_copied_apart(self):
        buffer = bytearray(b"abc")
        block = mod01.ProvenanceBlock([buffer], {}, {})
        buffer[0] = 122
        delivered = block.as_dict()["entries"][0]
        self.assertEqual(bytes(delivered), b"abc")
        self.assertIsNot(delivered, buffer)


class TestR13039EscrowCopies(unittest.TestCase):

    def test_lying_pair_identifier_stands_as_itself(self):
        leaf = LieCopy("LIED-PAIR")
        state = mod06.escrow_contract_state(
            "c1", pair_identifiers=[leaf])
        self.assertIs(state["pair_identifiers"][0], leaf)

    def test_raising_pair_identifier_escapes_no_bare_error(self):
        leaf = RaiseCopy()
        state = mod06.escrow_contract_state(
            "c1", pair_identifiers=[leaf])
        self.assertIs(state["pair_identifiers"][0], leaf)

    def test_lying_pause_cap_value_stands_as_itself(self):
        leaf = LieCopy(999)
        state = mod06.escrow_contract_state(
            "c1", pause_cap_value={"total": leaf})
        self.assertIs(state["pause_cap_value"]["total"], leaf)

    def test_lying_difference_stands_as_itself(self):
        leaf = LieCopy("LIED-DIFF")
        shown = mod06.report_difference({"delta": leaf})
        self.assertIs(shown["difference"]["delta"], leaf)
        self.assertEqual(
            shown["reported_as"], "unfolded difference only")

    def test_lying_folding_record_stands_as_itself(self):
        leaf = LieCopy("LIED-FOLD")
        folded = {"entries": [{
            "ruling": "DQ-1",
            "checked_by_independent_reader": True,
            "note": leaf,
        }]}
        shown = mod06.report_difference(
            {"delta": 1}, folding_record=folded)
        self.assertTrue(shown["ruling_effect_wording"])
        self.assertIs(
            shown["folding_record"]["entries"][0]["note"], leaf)

    def test_raising_difference_escapes_no_bare_error(self):
        leaf = RaiseCopy()
        shown = mod06.report_difference({"delta": leaf})
        self.assertIs(shown["difference"]["delta"], leaf)

    def test_enter_ruling_lying_row_stands_as_itself(self):
        leaf = LieCopy("LIED-STANDING")
        rows = mod06.dq_arrival_table()
        rows[0]["standing"] = leaf
        arrived = mod06.enter_ruling(
            rows, "DQ-5", "the ruling text, verbatim")
        self.assertIs(arrived[0]["standing"], leaf)
        self.assertEqual(
            arrived[0]["final_column"], "the ruling text, verbatim")
        rows[1]["final_column"] = "caller change"
        self.assertEqual(arrived[1]["final_column"], "")

    def test_enter_ruling_raising_row_escapes_no_bare_error(self):
        leaf = RaiseCopy()
        rows = mod06.dq_arrival_table()
        rows[0]["standing"] = leaf
        arrived = mod06.enter_ruling(rows, "DQ-5", "entered")
        self.assertIs(arrived[0]["standing"], leaf)
        self.assertEqual(arrived[0]["final_column"], "entered")

    def test_plain_escrow_controls_stand(self):
        handed = ["p1", "p2"]
        state = mod06.escrow_contract_state(
            "c1", pair_identifiers=handed)
        handed.append("caller change")
        self.assertEqual(state["pair_identifiers"], ["p1", "p2"])
        shown = mod06.report_difference({"delta": 1})
        self.assertEqual(shown["difference"], {"delta": 1})


class TestR13021CompareVerdictDeterminism(unittest.TestCase):

    def material(self, feature_value, records=None):
        return [{
            "agent_identifier": "agent-x",
            "day": 1,
            "feature_values": {"activity": feature_value},
            "records_for_agent_and_day": (
                [] if records is None else records),
        }]

    def test_lying_int_scores_its_stored_value(self):
        material = self.material(LieInt())
        direct = mod08.score_day(material)
        self.assertEqual(
            direct["verdict_states"][0]["verdict_state"], "NOTICED")
        self.assertEqual(
            direct["verdict_states"][0]
            ["accumulator_update"]["total_feature_value"], "4")
        check = mod08.compare_verdict_determinism(material)
        self.assertTrue(check["same"])
        self.assertEqual(
            check["verdict_states"][0]["verdict_state"], "NOTICED")
        self.assertEqual(
            check["verdict_states"][0]
            ["accumulator_update"]["total_feature_value"], "4")

    def test_ghost_record_copy_delivers_stored_material(self):
        record = GhostRecord({
            "agent_identifier": "agent-x",
            "day": 1,
            "feature_values": {"activity": 4},
            "records_for_agent_and_day": [],
        })
        check = mod08.compare_verdict_determinism([record])
        self.assertTrue(check["same"])
        self.assertEqual(
            check["verdict_states"][0]["agent_identifier"],
            "agent-x")
        self.assertEqual(check["verdict_states"][0]["day"], 1)
        self.assertEqual(
            check["verdict_states"][0]["verdict_state"], "NOTICED")

    def test_raising_leaf_escapes_no_bare_error(self):
        material = self.material(4, records=[{"note": RaiseCopy()}])
        check = mod08.compare_verdict_determinism(material)
        self.assertTrue(check["same"])
        self.assertEqual(
            check["verdict_states"][0]["verdict_state"], "NOTICED")

    def test_memoryview_leaf_escapes_no_bare_error(self):
        material = self.material(
            4, records=[memoryview(b"abc")])
        check = mod08.compare_verdict_determinism(material)
        self.assertTrue(check["same"])
        self.assertEqual(
            check["verdict_states"][0]["verdict_state"], "NOTICED")

    def test_plain_material_control_stands(self):
        check = mod08.compare_verdict_determinism(
            self.material(4))
        self.assertTrue(check["same"])
        self.assertEqual(
            check["verdict_states"][0]["verdict_state"], "NOTICED")


class TestR13022BuildCastGetReadings(unittest.TestCase):

    def test_initial_edge_argument_reads_stored_edge(self):
        edge = LieGet(
            {"voucher": "agent-0002", "vouchee": "agent-0003",
             "stake": 7},
            {"voucher": "agent-0000", "vouchee": "agent-0001",
             "stake": 111})
        point = {"population_size": 2,
                 "archetype_mix": {"honest": 1, "sleeper": 1}}
        cast = mod03.build_cast(
            point, cast_records(), strategy_class="fixed class",
            initial_edges=[edge])
        self.assertEqual(
            cast["initial_graph"]["edges"],
            [{"voucher": "agent-0002", "vouchee": "agent-0003",
              "stake": 7}])

    def test_initial_edge_on_point_reads_stored_edge(self):
        edge = LieGet(
            {"voucher": "agent-0002", "vouchee": "agent-0003",
             "stake": 7},
            {"voucher": "agent-0000", "vouchee": "agent-0001",
             "stake": 111})
        point = {"population_size": 2,
                 "archetype_mix": {"honest": 1, "sleeper": 1},
                 "initial_edges": [edge]}
        cast = mod03.build_cast(
            point, cast_records(), strategy_class="fixed class")
        self.assertEqual(
            cast["initial_graph"]["edges"],
            [{"voucher": "agent-0002", "vouchee": "agent-0003",
              "stake": 7}])

    def test_stream_text_with_reported_list_assigns_as_plain(self):
        stream = LieGet(
            {"cast": "dcba"},
            {"cast": [0.1, 0.2, 0.3, 0.4]})
        point = {"population": 4,
                 "archetype_mix": {"honest": 3, "sleeper": 1}}
        cast = mod03.build_cast(
            point, cast_records(), stream_state=stream,
            strategy_class="fixed class")
        sleeper_agents = [
            agent["agent_id"] for agent in cast["cast"]
            if agent["archetype_id"] == "sleeper"]
        self.assertEqual(sleeper_agents, ["agent-0003"])
        plain = mod03.build_cast(
            point, cast_records(), stream_state={"cast": "dcba"},
            strategy_class="fixed class")
        self.assertEqual(cast["cast"], plain["cast"])

    def test_stream_behaviour_reported_non_list_draws_stored(self):
        record = cast_records()[0]
        stream = LieGet(
            {"behaviour": [1.0], "values": [5.0]},
            {"behaviour": "reported non list"})
        proposals = mod03.archetype_behaviour(
            record, stream_state=stream)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["draw"], 1.0)

    def test_stream_reported_values_with_no_stored_key_no_error(self):
        record = cast_records()[0]
        stream = LieGet({}, {"values": [99.0]})
        proposals = mod03.archetype_behaviour(
            record, stream_state=stream)
        self.assertEqual(proposals, [])

    def test_stream_raising_get_answers_on_stored_contents(self):
        record = cast_records()[0]
        stream = RaiseGet({"behaviour": [2.0]})
        proposals = mod03.archetype_behaviour(
            record, stream_state=stream)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["draw"], 2.0)

    def test_cast_reported_values_with_no_stored_key_builds(self):
        stream = LieGet({}, {"cast": [99.0]})
        point = {"population_size": 1,
                 "archetype_mix": {"honest": 1}}
        cast = mod03.build_cast(
            point, cast_records(), stream_state=stream,
            strategy_class="fixed class")
        self.assertEqual(cast["population"], 1)
        self.assertEqual(
            cast["cast"][0]["archetype_id"], "honest")


class TestR13023CastRecordActs(unittest.TestCase):

    def test_cast_agent_record_reads_stored_values(self):
        agent = LieGet(
            {"agent_id": "real-agent", "archetype_id": "sleeper",
             "ground_truth": "sleeper"},
            {"agent_id": "ghost-agent",
             "archetype_id": "ghost-arch",
             "ground_truth": "ghost-gt"})
        self.assertEqual(
            mod03.cast_agent_record(agent),
            {"agent_identifier": "real-agent",
             "archetype_identifier": "sleeper",
             "membership_ground_truth": "sleeper"})

    def test_cast_edge_record_reads_stored_values(self):
        edge = LieGet(
            {"voucher": "real-a", "vouchee": "real-b", "stake": 3},
            {"voucher": "ghost-voucher",
             "vouchee": "ghost-vouchee", "stake": 999})
        self.assertEqual(
            mod03.cast_edge_record(edge),
            {"voucher": "real-a", "vouchee": "real-b", "stake": 3})

    def test_cast_records_raising_get_answer_on_stored(self):
        agent = RaiseGet(
            {"agent_id": "real-agent", "archetype_id": "sleeper",
             "ground_truth": "sleeper"})
        self.assertEqual(
            mod03.cast_agent_record(agent)["agent_identifier"],
            "real-agent")
        edge = RaiseGet(
            {"voucher": "real-a", "vouchee": "real-b", "stake": 3})
        self.assertEqual(
            mod03.cast_edge_record(edge)["stake"], 3)

    def test_cast_records_plain_controls_stand(self):
        self.assertEqual(
            mod03.cast_agent_record(
                {"agent_id": "a", "archetype_id": "honest",
                 "ground_truth": "honest"}),
            {"agent_identifier": "a",
             "archetype_identifier": "honest",
             "membership_ground_truth": "honest"})
        self.assertEqual(
            mod03.cast_edge_record(
                {"voucher": "a", "vouchee": "b", "stake": 5}),
            {"voucher": "a", "vouchee": "b", "stake": 5})


class TestR13037AdapterChoiceCopies(unittest.TestCase):

    def build(self, **parts):
        return mod07.make_adapter_choice(
            "choice-1", "reading", "point", "text version",
            "variant and fold", **parts)

    def test_nested_parts_copied_apart_from_caller(self):
        drives_buffer = bytearray(b"abc")
        mark_buffer = bytearray(b"xy")
        reference = {"ref": "r1"}
        choice = self.build(
            drives=[drives_buffer],
            dependence_marks=[{"mark": mark_buffer}],
            ruling_references=[reference])
        self.assertIsNot(choice["drives"][0], drives_buffer)
        self.assertIsNot(
            choice["dependence_marks"][0]["mark"], mark_buffer)
        self.assertIsNot(choice["ruling_references"][0], reference)
        drives_buffer[0] = 122
        mark_buffer[0] = 122
        reference["ref"] = "caller change"
        self.assertEqual(bytes(choice["drives"][0]), b"abc")
        self.assertEqual(
            bytes(choice["dependence_marks"][0]["mark"]), b"xy")
        self.assertEqual(
            choice["ruling_references"][0]["ref"], "r1")

    def test_nested_list_part_copied_apart(self):
        inner = ["a", "b"]
        choice = self.build(dependence_marks=[inner])
        inner.append("caller change")
        self.assertEqual(
            choice["dependence_marks"], [["a", "b"]])

    def test_raising_leaf_carried_as_itself(self):
        leaf = RaiseCopy()
        choice = self.build(drives=[{"d": leaf}])
        self.assertIs(choice["drives"][0]["d"], leaf)

    def test_plain_choice_control_stands(self):
        choice = self.build(
            drives=["d1"], dependence_marks=["m1"],
            ruling_references=["r1"],
            approval={"approver": "captain"})
        self.assertEqual(choice["drives"], ["d1"])
        self.assertEqual(choice["dependence_marks"], ["m1"])
        self.assertEqual(choice["ruling_references"], ["r1"])
        self.assertEqual(
            choice["recorded_as"], "adapter choice")


if __name__ == "__main__":
    unittest.main()

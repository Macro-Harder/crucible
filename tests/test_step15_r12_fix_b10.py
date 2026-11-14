"""Pins for fix wave 11, Builder 10: rows R11-013, R11-014, R11-015.

R11-013 (Red 5 Finding 7): the MOD-04 freeze acts ContractAHandover,
build_view_record, and per_viewer_components freeze each handed value
under its own memo, so a container handed in two or three places of
one act stands in the read backs as two or three distinct copies.
Settlement S-1 governs: one shared memo across all values of one act,
so a container handed in two places of one act stands as one copy.

R11-014 (Blue 2 Finding 4): release_view at MOD-04 copies its held
record plainly as dict(held), so the released record and the held
record share the one view record container, and a change made
through the released record rewrites the held record the leak check
passed on. Settlement S-1 governs at its copy limb: the guarded copy
form, under which no copy protocol a part supplies is ever honoured.

R11-015 (Blue 2 Finding 5): the MOD-03 record building acts
make_archetype_record and archetype_behaviour copy plainly and
shallowly, so nested containers handed in stand shared with the
delivered record and a caller side change after the act rewrites it.
Settlement S-1 governs at its copy limbs.
"""

import unittest

from crucible import mod03, mod04


class TestR11013SharedMemoFreeze(unittest.TestCase):

    def test_contract_a_handover_shares_one_copy_across_values(self):
        shared = [7, 8]
        handover = mod04.ContractAHandover(
            point=shared,
            assumption_record={"shared": shared},
            seed_input_set={"seeds": shared},
            family_id="family-1",
        )
        read_back = handover.as_dict()
        self.assertIs(read_back["point"],
                      read_back["assumption_record"]["shared"])
        self.assertIs(read_back["point"],
                      read_back["seed_input_set"]["seeds"])
        self.assertIsNot(read_back["point"], shared)
        self.assertEqual(read_back["point"], [7, 8])

    def test_build_view_record_contents_and_reputation_share_one_copy(self):
        shared = [1, 2]
        record = mod04.build_view_record(
            run_id="run-b10-view", viewer_id="viewer-1", day=1,
            contents=[
                {"first_seen_day": 1, "delay": 0, "payload": shared},
                {"first_seen_day": 1, "delay": 0, "payload": shared},
            ],
            reputation_and_band={"rep": shared},
            graph_position={},
        )
        first = record["view_contents"][0]["payload"]
        second = record["view_contents"][1]["payload"]
        reputation = record["reputation_and_band_values"]["rep"]
        self.assertIs(first, second)
        self.assertIs(first, reputation)
        self.assertIsNot(first, shared)
        self.assertEqual(first, [1, 2])

    def test_build_view_record_graph_shares_one_copy_with_contents(self):
        shared = [3, 4]
        record = mod04.build_view_record(
            run_id="run-b10-view2", viewer_id="viewer-1", day=1,
            contents=[
                {"first_seen_day": 1, "delay": 0, "payload": shared},
            ],
            reputation_and_band={},
            graph_position={"pos": shared},
        )
        self.assertIs(record["view_contents"][0]["payload"],
                      record["graph_position_as_seen"]["pos"])
        self.assertIsNot(record["view_contents"][0]["payload"], shared)

    def test_per_viewer_components_share_one_copy(self):
        shared = [5, 6]
        result = mod04.per_viewer_components(
            run_id="run-b10-pvc",
            components=[
                {"viewer_id": "viewer-1", "shared": shared},
                {"viewer_id": "viewer-2", "shared": shared},
            ],
        )
        self.assertIs(result[0]["shared"], result[1]["shared"])
        self.assertIsNot(result[0]["shared"], shared)
        self.assertEqual(result[0]["shared"], [5, 6])


class TestR11014ReleaseViewGuardedCopy(unittest.TestCase):

    def _held(self):
        record = mod04.build_view_record(
            run_id="run-b10-release", viewer_id="viewer-1", day=2,
            contents=[{"first_seen_day": 1, "delay": 0}],
            position="pos-1", rule_version_set="rv-1")
        return mod04.hold_view(record)

    def test_released_view_record_is_not_the_held_container(self):
        held = self._held()
        released = mod04.release_view(held)
        self.assertIsNot(released["view_record"], held["view_record"])
        self.assertIsNot(released, held)
        self.assertEqual(
            released["view_record"]["view_contents"],
            held["view_record"]["view_contents"])

    def test_released_mutation_does_not_rewrite_held(self):
        held = self._held()
        held_count = len(held["view_record"]["view_contents"])
        released = mod04.release_view(held)
        released["view_record"]["view_contents"].append(
            {"membership": 1})
        self.assertEqual(
            len(held["view_record"]["view_contents"]), held_count)
        self.assertEqual(
            len(released["view_record"]["view_contents"]),
            held_count + 1)


class TestR11015Mod03GuardedCopy(unittest.TestCase):

    def test_make_archetype_record_behaviour_nested_not_shared(self):
        nested = {"deep": [1]}
        record = mod03.make_archetype_record(
            archetype_id="arch-1", behaviour={"cfg": nested})
        self.assertIsNot(record["behaviour"]["cfg"], nested)
        self.assertEqual(record["behaviour"]["cfg"], {"deep": [1]})
        nested["deep"].append(99)
        self.assertEqual(record["behaviour"]["cfg"], {"deep": [1]})

    def test_make_archetype_record_parameter_rows_not_shared(self):
        row = ["r1"]
        record = mod03.make_archetype_record(
            archetype_id="arch-1", behaviour={}, parameter_rows=[row])
        self.assertIsNot(record["parameter_rows"][0], row)
        self.assertEqual(record["parameter_rows"][0], ["r1"])
        row.append("r2")
        self.assertEqual(record["parameter_rows"][0], ["r1"])

    def test_archetype_behaviour_assumptions_nested_not_shared(self):
        nested = {"deep": [1]}
        proposals = mod03.archetype_behaviour(
            {"archetype_id": "arch-1", "behaviour": {"action": "propose"}},
            stream_state=[1], assumption_values={"cfg": nested})
        self.assertEqual(len(proposals), 1)
        delivered = proposals[0]["assumptions"]["cfg"]
        self.assertIsNot(delivered, nested)
        self.assertEqual(delivered, {"deep": [1]})
        nested["deep"].append(99)
        self.assertEqual(delivered, {"deep": [1]})


if __name__ == "__main__":
    unittest.main()

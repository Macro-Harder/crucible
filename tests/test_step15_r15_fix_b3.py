"""Pins for fix wave 14, Builder 3, rows R14-019 to R14-028.

Each pin fails on the charged defect against the pristine tree and
passes after the cure. Settlement S-1 governs throughout: a part's
own copy, iteration, or reading protocol never supplies the reading
an act judges or delivers by.
"""
import unittest

import crucible.mod01 as mod01
import crucible.mod03 as mod03
import crucible.mod06 as mod06
import crucible.mod08 as mod08
import crucible.mod09 as mod09
import crucible.mod11 as mod11


class LyingStr(str):
    def __deepcopy__(self, memo):
        return "sweep"


class LyingInt(int):
    def __deepcopy__(self, memo):
        return 4000


class RaisingPart:
    def __deepcopy__(self, memo):
        raise RuntimeError("raising copy protocol")


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


def search_carriage():
    return mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])


def build_search(**overrides):
    kwargs = {
        "points_tried": ["point one"],
        "per_point_outcome": [{"point": "point one",
                               "outcome": "no failure"}],
        "bond_candidates": [{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        "budget": "stated budget",
        "neighbourhood": {"definition": "adjacent points",
                          "step sizes": [1]},
        "starting_points": ["point zero"],
        "order_of_search": ["point one"],
    }
    kwargs.update(overrides)
    return mod09.build_search_record(search_carriage(), **kwargs)


def headline_values():
    return {field: "value for " + field
            for field in mod11.HEADLINE_UNIT_FIELDS}


class TestR14019RecordForm(unittest.TestCase):
    def test_lying_store_kind_does_not_validate(self):
        instance = mod01.minimal_valid_instance("4")
        instance["store_kind"] = LyingStr("bogus")
        form_cls = mod01.FORM_TYPES["4"]
        form = form_cls(instance)
        self.assertEqual(str.__str__(form.values["store_kind"]), "bogus")
        self.assertFalse(form.validate())

    def test_lying_int_stays_stored_value(self):
        instance = mod01.minimal_valid_instance("1")
        field = next(iter(instance))
        instance[field] = LyingInt(4)
        form_cls = mod01.FORM_TYPES["1"]
        form = form_cls(instance)
        self.assertEqual(int.__int__(form.values[field]), 4)

    def test_raising_part_escapes_no_bare_error(self):
        instance = mod01.minimal_valid_instance("1")
        field = next(iter(instance))
        part = RaisingPart()
        instance[field] = part
        form_cls = mod01.FORM_TYPES["1"]
        form = form_cls(instance)
        self.assertIs(form.values[field], part)

    def test_nested_lying_part_does_not_fabricate(self):
        instance = mod01.minimal_valid_instance("1")
        field = next(iter(instance))
        instance[field] = {"nested": LyingInt(4)}
        form_cls = mod01.FORM_TYPES["1"]
        form = form_cls(instance)
        self.assertEqual(
            int.__int__(form.values[field]["nested"]), 4)


class TestR14020UndirectedCopyBuffers(unittest.TestCase):
    def test_payload_bytearray_copied_apart(self):
        handed = bytearray(b"cfg")
        result = mod06.escrow_result("kind", payload={"data": handed})
        self.assertIsNot(result["payload"]["data"], handed)
        self.assertIsInstance(result["payload"]["data"], bytearray)
        handed[0] = ord("X")
        self.assertEqual(bytes(result["payload"]["data"]), b"cfg")

    def test_payload_memoryview_copied_apart_in_form(self):
        backing = bytearray(b"cfg")
        handed = memoryview(backing)
        result = mod06.escrow_result("kind", payload={"data": handed})
        delivered = result["payload"]["data"]
        self.assertIsInstance(delivered, memoryview)
        self.assertIsNot(delivered, handed)
        backing[0] = ord("X")
        self.assertEqual(delivered.tobytes(), b"cfg")

    def test_contract_state_pair_bytearray_copied_apart(self):
        handed = bytearray(b"cfg")
        state = mod06.escrow_contract_state(
            "c1", pair_identifiers=[handed])
        self.assertIsNot(state["pair_identifiers"][0], handed)
        handed[0] = ord("X")
        self.assertEqual(bytes(state["pair_identifiers"][0]), b"cfg")


class TestR14021ContractStateUncopiedFields(unittest.TestCase):
    def test_estimated_cost_dict_copied_apart(self):
        handed = {"amount": 5}
        state = mod06.escrow_contract_state(
            "c1", estimated_cost_value=handed)
        self.assertIsNot(state["estimated_cost_value"], handed)
        handed["amount"] = 999
        self.assertEqual(state["estimated_cost_value"]["amount"], 5)

    def test_pause_state_dict_copied_apart(self):
        handed = {"paused": True}
        state = mod06.escrow_contract_state("c1", pause_state=handed)
        self.assertIsNot(state["pause_state"], handed)
        handed["paused"] = False
        self.assertEqual(state["pause_state"]["paused"], True)

    def test_estimated_cost_list_copied_apart(self):
        handed = [1, 2]
        state = mod06.escrow_contract_state(
            "c1", estimated_cost_value=handed)
        self.assertIsNot(state["estimated_cost_value"], handed)
        handed.append(999)
        self.assertEqual(state["estimated_cost_value"], [1, 2])


class TestR14022SearchRecordSharing(unittest.TestCase):
    def test_swept_dict_copied_apart(self):
        handed = {"value": 1}
        record = build_search(external_profit_swept_values=[handed])
        delivered = record["external_profit_swept_values"][0]
        self.assertIsNot(delivered, handed)
        handed["value"] = 999
        self.assertEqual(delivered["value"], 1)

    def test_swept_list_and_bytearray_copied_apart(self):
        handed_list = [1]
        handed_buffer = bytearray(b"ab")
        record = build_search(
            external_profit_swept_values=[handed_list, handed_buffer])
        delivered = record["external_profit_swept_values"]
        self.assertIsNot(delivered[0], handed_list)
        self.assertIsNot(delivered[1], handed_buffer)
        handed_buffer[0] = ord("Z")
        self.assertEqual(bytes(delivered[1]), b"ab")

    def test_budget_list_copied_apart(self):
        handed = ["stated"]
        record = build_search(budget=handed)
        self.assertIsNot(record["search_record"]["search_budget"], handed)
        handed.append("appended")
        self.assertEqual(
            record["search_record"]["search_budget"], ["stated"])


class TestR14023QuotedCopyBuffers(unittest.TestCase):
    def test_headline_bytearray_copied_apart(self):
        handed = bytearray(b"abc")
        values = headline_values()
        values[mod11.HEADLINE_UNIT_FIELDS[0]] = handed
        unit = mod11.make_headline_unit(values)
        delivered = unit[mod11.HEADLINE_UNIT_FIELDS[0]]
        self.assertIsNot(delivered, handed)
        self.assertIsInstance(delivered, bytearray)
        handed[0] = ord("Z")
        self.assertEqual(bytes(delivered), b"abc")

    def test_headline_nested_memoryview_keeps_form_and_separation(self):
        backing = bytearray(b"abc")
        values = headline_values()
        values["holding_region"] = {"part": memoryview(backing)}
        unit = mod11.make_headline_unit(values)
        delivered = unit["holding_region"]["part"]
        self.assertIsInstance(delivered, memoryview)
        backing[0] = ord("Z")
        self.assertEqual(delivered.tobytes(), b"abc")

    def test_quoted_copy_bytearray_direct(self):
        handed = bytearray(b"abc")
        delivered = mod11._quoted_copy({"part": handed})["part"]
        self.assertIsNot(delivered, handed)
        self.assertIsInstance(delivered, bytearray)


class TestR14024ProvenanceEntriesIteration(unittest.TestCase):
    def test_entries_read_by_stored_contents(self):
        stored_entry = {"field": "", "applicability": ""}
        yielded_entry = {"field": "stated field",
                         "applicability": "stated"}
        entries = LyingList([stored_entry], [yielded_entry])
        block = mod01.ProvenanceBlock(entries, {"x": 1}, {"x": 1})
        self.assertEqual(block.as_dict()["entries"], [stored_entry])
        self.assertFalse(mod01.validate_provenance_block(block))


class TestR14025EnterRulingIteration(unittest.TestCase):
    def test_rows_read_by_stored_contents(self):
        yielded_row = {"item": "DQ-5", "standing": "open",
                       "final_column": ""}
        rows = LyingList([], [yielded_row])
        delivered = mod06.enter_ruling(rows, "DQ-5", "entered text")
        self.assertEqual(delivered, [])


class TestR14026WeeklyContainerIteration(unittest.TestCase):
    def test_units_read_by_stored_contents(self):
        units = LyingList(["not-an-id"], ["u123"])
        with self.assertRaises(ValueError):
            mod11.make_weekly_container("W1", units)

    def test_next_container_new_units_read_by_stored_contents(self):
        units = LyingList(["not-an-id"], ["u123"])
        with self.assertRaises(ValueError):
            mod11.next_weekly_container("W2", {"held_units": []}, units)


class TestR14027RecordSequenceFallback(unittest.TestCase):
    def test_non_container_iterable_yields_no_catalogue_entry(self):
        record = {"archetype_id": "fab",
                  "generator_signature": "sig",
                  "parameter_rows": []}
        catalogue = mod03.archetype_catalogue(
            FabricatingIterable([record]))
        self.assertEqual(catalogue["entries"], {})

    def test_record_sequence_fallback_direct(self):
        self.assertEqual(
            mod03._record_sequence(FabricatingIterable([{"a": 1}])), [])

    def test_stored_rows_fallback_direct(self):
        self.assertEqual(
            mod03._stored_rows(FabricatingIterable([{"a": 1}])), [])


class TestR14028Mod08NonContainerIteration(unittest.TestCase):
    def test_use_naming_non_container_iterable_does_not_pass(self):
        artefact = {"value": 4.0,
                    "uses_named": FabricatingIterable(["conformance"])}
        with self.assertRaises(mod08.SilentUseMovement):
            mod08.validate_use_naming(artefact)

    def test_seal_non_container_authored_does_not_seal(self):
        entries = [{"kind": "sleeper class"},
                   {"kind": "honest challenge variant"}]
        sealed = {"authored": FabricatingIterable(entries)}
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.seal_sealed_set(sealed)


if __name__ == "__main__":
    unittest.main()

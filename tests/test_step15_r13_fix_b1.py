"""Fix wave 12, Builder 1 pins: rows R12-001 to R12-008.

Each test pins a defect the Round 12 register states for the
segmentation family, on the proving acts the source papers used.
Time pins state the bound the cure applies at the act, in the
form settlement S-10 states: the enumeration stands bounded by
the stated candidate caps' discipline applied to its own
candidate space, reusing the stated values.
"""

import time
import unittest

from crucible import mod03, mod04, mod05, mod06, mod08, mod10


SPELLING = [
    frozenset(("u", "n")), frozenset(("d", "t")),
    frozenset(("r", "u")), frozenset(("t", "h")),
]
FILLERS = [
    frozenset(("a", "b")), frozenset(("c", "e")),
    frozenset(("f", "g")), frozenset(("i", "j")),
    frozenset(("k", "l")), frozenset(("m", "o")),
    frozenset(("p", "q")), frozenset(("s", "w")),
    frozenset(("v", "x")), frozenset(("y", "z")),
    frozenset(("a", "c")),
]


def spelling_part(pair_count):
    pairs = SPELLING + FILLERS[:pair_count - len(SPELLING)]
    return tuple(pairs)


def view_fixture(contents):
    return {
        "run_identifier": "run-fix12-b1",
        "viewer_identifier": "viewer-1",
        "simulated_day": 5,
        "scheduling_position_identifier": "position-1",
        "rule_version_set": "rule-set-1",
        "view_contents": contents,
        "reputation_and_band_values": {"band": "stated"},
        "graph_position_as_seen": "stated",
        "first_seen_day_per_record": {"item": 3},
        "delay_applied_per_record": {"item": 1},
        "completeness_state": "complete",
        "building_component": "Recorder",
        "delivering_contract": "stated",
        "selection_rule_version": "rule-set-1",
    }


class TestR12001PayloadWalkBound(unittest.TestCase):
    """R12-001: a small clean payload key leaves the MOD-06
    escrow gate with no answer, the payload walk enumerating
    its joined and multi readings to exhaustion on clean keys.
    Bound applied: the walk judges folded containment position
    by position and judges a handed name against a target only
    where a combined reading of the name can stand at the
    target length, so no combined variant text stands listed
    for a name that cannot reach the target."""

    def test_clean_five_part_frozenset_answers(self):
        payload = {frozenset(
            ["part1", "part2", "part3", "part4", "part5"]): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_clean_six_part_frozenset_answers(self):
        payload = {frozenset(
            ["part1", "part2", "part3", "part4", "part5",
             "part6"]): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_clean_tuple_carrying_five_part_frozenset(self):
        payload = {(frozenset(
            ["part1", "part2", "part3", "part4", "part5"]),
            "tail"): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_escrow_result_clean_payload_answers(self):
        payload = {(frozenset(
            ["part1", "part2", "part3", "part4", "part5",
             "part6"]), "tail"): 1}
        start = time.time()
        result = mod06.escrow_result("release", payload=payload)
        self.assertLess(time.time() - start, 4.0)
        self.assertEqual(result["kind"], "release")

    def test_barred_payload_still_refused(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "release", payload={"real_money": 5})


class TestR12002FoldedCapPlainLimb(unittest.TestCase):
    """R12-002: past the folded cap a barred key passes the
    MOD-05 and MOD-10 gates, while the plain set stands inside
    the plain cap."""

    def test_fifteen_pairs_barred_at_both_predicates(self):
        key = frozenset(("zzgro", spelling_part(15), "cleanpart"))
        self.assertTrue(mod05._panel_key_barred(key))
        self.assertTrue(mod10._is_barred_view_key(key))

    def test_fifteen_pairs_refused_at_public_gates(self):
        key = frozenset(("zzgro", spelling_part(15), "cleanpart"))
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))
        record = view_fixture([{key: "canary value"}])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)
        with self.assertRaises(ValueError):
            mod10.retain_view_record(record)

    def test_fourteen_pairs_control_barred(self):
        key = frozenset(("zzgro", spelling_part(14), "cleanpart"))
        self.assertTrue(mod05._panel_key_barred(key))
        self.assertTrue(mod10._is_barred_view_key(key))


class TestR12003CapEdgeReach(unittest.TestCase):
    """R12-003: a barred part tiled only where a composite part
    past its cap contributes its edge, a whole reading ending
    in groundtr, and a sibling contributes uth."""

    def folded_part(self):
        fillers = [
            frozenset(pair) for pair in (
                ("z", "q"), ("x", "j"), ("q", "x"), ("j", "z"),
                ("z", "x"), ("q", "j"), ("x", "z"), ("j", "q"),
                ("z", "j"), ("q", "z"), ("x", "q"))]
        spelling = [
            frozenset(("g", "r")), frozenset(("0", "u")),
            frozenset(("n", "d")), frozenset(("7", "r"))]
        return tuple(fillers + spelling)

    def plain_part(self, filler_count):
        fillers = [
            frozenset(pair) for pair in (
                ("z", "q"), ("x", "j"), ("q", "x"), ("j", "z"),
                ("z", "x"), ("q", "j"), ("x", "z"), ("j", "q"),
                ("z", "j"), ("q", "z"), ("x", "q"), ("j", "x"),
                ("q", "j"), ("z", "q"))]
        spelling = [
            frozenset(("g", "r")), frozenset(("o", "u")),
            frozenset(("n", "d")), frozenset(("t", "r"))]
        return tuple(fillers[:filler_count] + spelling)

    def test_folded_edge_barred_at_mod03_and_mod04(self):
        key = frozenset((self.folded_part(), "uth", "zzqq"))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod04._is_barred_key(key))

    def test_plain_edge_barred_at_mod04_and_mod03(self):
        key = frozenset((self.plain_part(14), "uth", "zzqq"))
        self.assertTrue(mod04._is_barred_key(key))
        self.assertTrue(mod03._is_barred_key(key))

    def test_plain_edge_reaches_mod04_public_gate(self):
        key = frozenset((self.plain_part(14), "uth", "zzqq"))
        record = {"view_contents": [{key: 1}]}
        self.assertTrue(
            mod04.view_record_carries_barred_field(record))
        with self.assertRaises(Exception):
            mod04.build_view_record(contents=[{key: 1}])

    def test_at_cap_controls_barred(self):
        part = self.folded_part()
        folded = frozenset(
            (tuple(list(part)[:10] + list(part)[11:]), "uth", "zzqq"))
        self.assertTrue(mod03._is_barred_key(folded))
        plain = frozenset((self.plain_part(13), "uth", "zzqq"))
        self.assertTrue(mod04._is_barred_key(plain))


class TestR12004PlainInsideWholeJoin(unittest.TestCase):
    """R12-004, under settlement S-9: a plain barred reading
    inside one composite part past the plain cap, standing
    inside the whole join rather than as the whole join."""

    def part(self):
        spelling = [
            frozenset(("g", "r")), frozenset(("o", "u")),
            frozenset(("n", "d")), frozenset(("t", "r")),
            frozenset(("u", "t")), frozenset(("h", "_"))]
        return tuple(spelling + FILLERS + [frozenset(("y", "q"))])

    def test_barred_at_mod03_and_mod08(self):
        key = frozenset(("zzq", self.part(), "cleanpart"))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod08._is_barred_key(key))

    def test_mod03_public_gates(self):
        key = frozenset(("zzq", self.part(), "cleanpart"))
        self.assertFalse(mod03.validate_detection_input({key: 1}))
        self.assertTrue(mod03.record_carries_ground_truth({key: 1}))
        stripped = mod03.strip_ground_truth({key: 1})
        self.assertNotIn(key, stripped)

    def test_at_cap_control_barred(self):
        part = tuple(list(self.part())[:17])
        key = frozenset(("zzq", part, "cleanpart"))
        self.assertTrue(mod03._is_barred_key(key))


class TestR12005PlainLimbMod05Mod10(unittest.TestCase):
    """R12-005: a plain barred reading inside the stated plain
    cap escapes at MOD-05 and MOD-10 while MOD-03 bars it."""

    def test_predicates_at_fifteen_and_seventeen_pairs(self):
        for count in (15, 17):
            key = frozenset(
                ("zzgro", spelling_part(count), "cleanpart"))
            self.assertTrue(mod03._is_barred_key(key))
            self.assertTrue(mod05._panel_key_barred(key))
            self.assertTrue(mod10._is_barred_view_key(key))

    def test_public_gates_at_fifteen_pairs(self):
        key = frozenset(("zzgro", spelling_part(15), "cleanpart"))
        self.assertFalse(mod05.validate_panel_inputs({key: 1}))
        record = view_fixture([{key: "canary value"}])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)


class TestR12006FormableBound(unittest.TestCase):
    """R12-006, under settlement S-10: the segmentation
    formable computation stands outside both stated candidate
    caps. Bound applied at the act: the unordered formable
    walk stands bounded by the stated candidate cap of its
    reading space, 131072 reached states in plain space and
    20000 in folded space, and a part past the bound
    contributes its iteration order join forms, as the
    candidate caps state for a part past their bound; a
    subpart that can contribute no segment and cannot stand
    empty makes an exact join impossible and stands answered
    at once."""

    def clean_key(self, count):
        letters = [chr(ord("a") + i) for i in range(count)]
        return frozenset(("cleanfiller", frozenset(letters)))

    def test_unordered_barred_answers_at_24(self):
        start = time.time()
        self.assertFalse(
            mod03._seg_unordered_barred(self.clean_key(24)))
        self.assertLess(time.time() - start, 8.0)

    def test_is_barred_key_answers_at_24(self):
        start = time.time()
        self.assertFalse(mod03._is_barred_key(self.clean_key(24)))
        self.assertLess(time.time() - start, 8.0)

    def test_is_barred_key_answers_at_28(self):
        start = time.time()
        self.assertFalse(mod03._is_barred_key(self.clean_key(26)))
        self.assertLess(time.time() - start, 8.0)

    def test_mod06_payload_key_answers_at_22(self):
        # The letters of this key spell the anchor marker in
        # the multi reading space, so the MOD-06 act answers
        # True; the defect the row charges is the cost of the
        # answer, which Green 5 measured at 15.73 seconds.
        start = time.time()
        self.assertTrue(
            mod06._seg_payload_key(self.clean_key(22), False))
        self.assertLess(time.time() - start, 8.0)

    def test_mod04_gate_answers_at_22(self):
        record = {"view_contents": [{self.clean_key(22): 1}]}
        start = time.time()
        self.assertFalse(
            mod04.view_record_carries_barred_field(record))
        self.assertLess(time.time() - start, 8.0)

    def test_charged_construction_still_barred(self):
        key = frozenset(("zzgro", spelling_part(13), "cleanpart"))
        self.assertTrue(mod03._is_barred_key(key))


class TestR12007DictNodeGate(unittest.TestCase):
    """R12-007: a barred name split across two keys of one
    dict passes the MOD-04 gate walk, which judges each dict
    key on its own and never the dict node itself."""

    def test_predicate_control(self):
        self.assertTrue(mod04._is_barred_key({"member": 1, "ship": 2}))
        self.assertTrue(mod04._is_barred_key({"mem": 1, "bership": 2}))

    def test_gate_walk_judges_dict_node(self):
        for split in ({"member": 1, "ship": 2},
                      {"mem": 1, "bership": 2}):
            record = {"view_contents": [split]}
            self.assertTrue(
                mod04.view_record_carries_barred_field(record))

    def test_build_view_record_refuses_all_groups(self):
        split = {"member": 1, "ship": 2}
        with self.assertRaises(Exception):
            mod04.build_view_record(contents=[split])
        with self.assertRaises(Exception):
            mod04.build_view_record(reputation_and_band=split)
        with self.assertRaises(Exception):
            mod04.build_view_record(graph_position=split)

    def test_clean_feature_values_drops_split_dict(self):
        cleaned = mod04._clean_feature_values(
            {"x": {"member": 1, "ship": 2}})
        self.assertEqual(cleaned, {"x": {}})
        control = mod04._clean_feature_values(
            {"x": {"membership": 1}})
        self.assertEqual(control, {"x": {}})


class TestR12008Mod10DeepChain(unittest.TestCase):
    """R12-008: the MOD-10 view barred key predicate raises a
    bare RecursionError on a deep container chain and the
    error escapes the public leak check."""

    def chain(self, depth, base):
        key = base
        for _ in range(depth):
            key = (key,)
        return key

    def test_clean_chain_answers_at_600(self):
        key = self.chain(600, frozenset(("cle", "anx")))
        self.assertFalse(mod10._is_barred_view_key(key))

    def test_barred_chain_answers_at_990(self):
        key = self.chain(990, frozenset(("mem", "bership")))
        self.assertTrue(mod10._is_barred_view_key(key))

    def test_leak_check_clean_chain_no_bare_error(self):
        key = self.chain(500, frozenset(("cle", "anx")))
        record = view_fixture([{key: 1}])
        result = mod10.run_view_leak_check(record)
        self.assertTrue(result["reportable"])

    def test_leak_check_barred_chain_refused_named(self):
        key = self.chain(500, frozenset(("mem", "bership")))
        record = view_fixture([{key: 1}])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)


if __name__ == "__main__":
    unittest.main()

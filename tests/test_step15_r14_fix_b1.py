"""Fix wave 13, Builder 1 pins: rows R13-001, R13-002, R13-003,
R13-004, and R13-036.

Each test pins a defect the Round 13 register states for the
segmentation, enumeration, and timing family, on the proving
acts the source papers used (Red 1 Findings 1 and 2, Blue 5
Finding 1, Blue 1 Finding 1, Purple 1 Finding 1, and Red 4
Finding 2). Time pins state the bounds the settlements state:
4 seconds on the MOD-06 seven part payload acts under S-12,
and the stated candidate caps' discipline under S-10 for the
MOD-01 formable acts, with the pin bound at 4 seconds there.
The MOD-13 pin states the stated 5040 distinct join discipline
of S-13, applied to the ordered limb.
"""

import time
import unittest

from crucible import mod01, mod03, mod05, mod06, mod10, mod13


SPELL = [
    frozenset(("r", "e")), frozenset(("a", "l")),
    frozenset(("m", "o")),
]
FILLERS = [
    frozenset(("a", "b")), frozenset(("c", "e")),
    frozenset(("f", "g")), frozenset(("i", "j")),
    frozenset(("k", "l")), frozenset(("m", "o")),
    frozenset(("p", "q")), frozenset(("s", "w")),
    frozenset(("v", "x")), frozenset(("y", "z")),
    frozenset(("a", "c")), frozenset(("d", "f")),
]


def edge_part(filler_count):
    return tuple(FILLERS[:filler_count] + SPELL)


def edge_key(filler_count):
    return frozenset((edge_part(filler_count), "ney", "zzqq"))


def nested_key(part_count):
    parts = [chr(ord("a") + i) for i in range(part_count)]
    return frozenset((frozenset(parts), "zz"))


def view_fixture(contents):
    return {
        "run_identifier": "run-fix13-b1",
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


SPLIT_GT = {"gro": 1, "undtruth": 2}
SPLIT_GT3 = {"gr": 1, "ound": 2, "truth": 3}
SPLIT_RM = {"real_": 5, "money": 6}
SPLIT_RM3 = {"re": 1, "al_mo": 2, "ney": 3}
SPLIT_AS = {"anchor_": 5, "set": 6}


class TestR13001Mod01EdgeAct(unittest.TestCase):
    """R13-001: a barred folded marker tiled only where a
    composite part past the folded cap contributes its edge
    passes the MOD-01 money gate unjudged, because MOD-01
    holds no edge act at all."""

    def test_past_cap_folded_key_carries(self):
        self.assertTrue(
            mod01._folded_key_carries(edge_key(12), "realmoney"))

    def test_past_cap_seg_carrying(self):
        self.assertTrue(
            mod01._seg_carrying(edge_key(12), "realmoney"))

    def test_past_cap_money_value_gate(self):
        self.assertTrue(
            mod01._carries_real_money_value({edge_key(12): 5}))

    def test_at_cap_and_clean_controls(self):
        self.assertTrue(
            mod01._folded_key_carries(edge_key(7), "realmoney"))
        self.assertTrue(
            mod01._carries_real_money_value({edge_key(7): 5}))
        self.assertFalse(mod01._carries_real_money_value({"plain": 5}))


class TestR13002Mod01FormableBound(unittest.TestCase):
    """R13-002: the MOD-01 segmentation formable computation
    stands outside the stated caps discipline, its unordered
    walk iterating every subset mask with no reached state
    bound. Bound applied under S-10: the stated candidate cap
    of the reading space, 20000 states in folded space, reused
    as the reached state bound, beside the cured modules'
    answer at once where a subpart can contribute no segment
    and cannot stand empty. The pin bound stands at 4 seconds."""

    def test_nested_24_answers_within_bound(self):
        start = time.time()
        self.assertFalse(
            mod01._folded_key_matches(nested_key(24), "amount"))
        self.assertLess(time.time() - start, 4.0)

    def test_nested_26_answers_within_bound(self):
        start = time.time()
        self.assertFalse(
            mod01._folded_key_matches(nested_key(26), "amount"))
        self.assertLess(time.time() - start, 4.0)


class TestR13003Mod06SevenPartBound(unittest.TestCase):
    """R13-003: a clean seven part payload key costs seconds
    at the MOD-06 payload walk, past the stated bound of
    4 seconds under S-12, at the walk and at escrow_result,
    and a barred seven part form stands refused past the
    bound as well. Every answer stands correct; the defect
    is the cost."""

    def test_clean_seven_part_frozenset_within_bound(self):
        payload = {frozenset(
            ["part0", "part1", "part2", "part3", "part4",
             "part5", "part6"]): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_clean_seven_part_names_within_bound(self):
        payload = {frozenset(
            ["alpha", "bravo", "charlie", "delta", "echo",
             "foxtrot", "golf"]): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_clean_tuple_carrying_seven_part_within_bound(self):
        payload = {(frozenset(
            ["part0", "part1", "part2", "part3", "part4",
             "part5", "part6"]), "tail"): 1}
        start = time.time()
        self.assertFalse(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)

    def test_escrow_result_seven_part_within_bound(self):
        payload = {frozenset(
            ["part0", "part1", "part2", "part3", "part4",
             "part5", "part6"]): 1}
        start = time.time()
        result = mod06.escrow_result("release", payload=payload)
        self.assertLess(time.time() - start, 4.0)
        self.assertEqual(result["kind"], "release")

    def test_barred_seven_part_refused_within_bound(self):
        payload = {frozenset(
            ["re", "al", "mo", "ney", "p", "q", "s"]): 1}
        start = time.time()
        self.assertTrue(mod06._payload_carries_barred(payload))
        self.assertLess(time.time() - start, 4.0)
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=payload)


class TestR13004SplitDictGates(unittest.TestCase):
    """R13-004: a barred reading split across two keys of one
    dict passes the public gates at MOD-03, MOD-05, MOD-06,
    and MOD-10, while the segmentation predicates bar the
    same dict node and the cured MOD-04 gate refuses it.
    Under S-11 a public gate walk that judges a dict handed
    to it judges the dict node itself."""

    def test_mod03_validate_refuses_split_dict_forms(self):
        self.assertFalse(
            mod03.validate_detection_input({"field": dict(SPLIT_GT)}))
        self.assertFalse(mod03.validate_detection_input(
            {"outer": {"inner": dict(SPLIT_GT)}}))
        self.assertFalse(mod03.validate_detection_input(
            {"field": [dict(SPLIT_GT)]}))
        self.assertFalse(
            mod03.validate_detection_input({"field": dict(SPLIT_GT3)}))
        self.assertFalse(mod03.validate_detection_input(dict(SPLIT_GT)))

    def test_mod03_record_carries_split_dict(self):
        self.assertTrue(
            mod03.record_carries_ground_truth({"field": dict(SPLIT_GT)}))
        self.assertTrue(
            mod03.record_carries_ground_truth({"field": [dict(SPLIT_GT)]}))

    def test_mod03_strip_cleans_split_dict(self):
        stripped = mod03.strip_ground_truth(
            {"field": dict(SPLIT_GT), "keep": 1})
        self.assertEqual(stripped, {"field": {}, "keep": 1})
        self.assertEqual(mod03.strip_ground_truth(dict(SPLIT_GT)), {})

    def test_mod05_validate_refuses_split_dict_forms(self):
        self.assertFalse(
            mod05.validate_panel_inputs({"field": dict(SPLIT_GT)}))
        self.assertFalse(mod05.validate_panel_inputs(
            {"outer": {"inner": dict(SPLIT_GT)}}))
        self.assertFalse(mod05.validate_panel_inputs(
            {"field": [dict(SPLIT_GT)]}))
        self.assertFalse(
            mod05.validate_panel_inputs({"field": dict(SPLIT_GT3)}))

    def test_mod05_panel_inputs_cleans_split_dict(self):
        cleaned = mod05.panel_inputs({"field": dict(SPLIT_GT), "keep": 1})
        self.assertEqual(cleaned, {"field": {}, "keep": 1})

    def test_mod06_carries_split_dict_forms(self):
        self.assertTrue(mod06._payload_carries_barred(dict(SPLIT_RM)))
        self.assertTrue(
            mod06._payload_carries_barred({"x": dict(SPLIT_RM)}))
        self.assertTrue(
            mod06._payload_carries_barred({"x": [dict(SPLIT_RM)]}))
        self.assertTrue(mod06._payload_carries_barred(dict(SPLIT_RM3)))
        self.assertTrue(mod06._payload_carries_barred(dict(SPLIT_AS)))

    def test_mod06_escrow_refuses_split_dict(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=dict(SPLIT_RM))
        with self.assertRaises(ValueError):
            mod06.escrow_result("release", payload=dict(SPLIT_AS))

    def test_mod10_predicate_bars_dict_node(self):
        self.assertTrue(mod10._is_barred_view_key(dict(SPLIT_GT)))
        self.assertTrue(mod10._is_barred_view_key(dict(SPLIT_GT3)))

    def test_mod10_gate_refuses_split_dict(self):
        self.assertTrue(
            mod10._carries_barred_key({"field": dict(SPLIT_GT)}))
        record = view_fixture([dict(SPLIT_GT)])
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)
        with self.assertRaises(ValueError):
            mod10.retain_view_record(record)

    def test_split_dict_controls_hold(self):
        clean = {"gro": 1, "cleanpart": 2}
        reversed_dict = {"undtruth": 1, "gro": 2}
        self.assertTrue(mod03.validate_detection_input({"field": clean}))
        self.assertTrue(
            mod03.validate_detection_input({"field": reversed_dict}))
        self.assertTrue(mod05.validate_panel_inputs({"field": clean}))
        self.assertFalse(mod06._payload_carries_barred(
            {"gro": 1, "cleanpart": 2}))
        self.assertFalse(mod06._payload_carries_barred(
            {"money": 6, "real_": 5}))
        self.assertFalse(mod10._is_barred_view_key(clean))
        self.assertFalse(mod10._is_barred_view_key(reversed_dict))
        result = mod06.escrow_result(
            "release", payload={"gro": 1, "cleanpart": 2})
        self.assertEqual(result["kind"], "release")


def ordered_key(part_count):
    return tuple(
        frozenset(("a" + str(i), "b" + str(i)))
        for i in range(part_count))


def registry_entry():
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
    return entry


def run_record(run_id, run_class="screening", status="completed"):
    return {
        "run_identifier": run_id,
        "sweep_family_identifier": "fam-1",
        "claim_identifier": "claim-1",
        "run_class": run_class,
        "run_status": status,
    }


class TestR13036Mod13OrderedLimbBound(unittest.TestCase):
    """R13-036: the MOD-13 joined texts act bounds its
    unordered limb at 5040 and leaves its ordered limb
    unbounded. Under S-13 the ordered limb stands bounded
    by the same stated discipline: complete while the
    distinct joins stand at or under 5040, and past that
    bound the container contributes its single stored
    order join alone, as the unordered limb contributes
    its sorted join alone past its bound."""

    def test_ordered_sixteen_parts_bounded(self):
        key = ordered_key(16)
        self.assertEqual(
            mod13._stored_key_texts(key), {mod13._stored_key_text(key)})

    def test_ordered_twenty_parts_within_time_and_bound(self):
        key = ordered_key(20)
        start = time.time()
        texts = mod13._stored_key_texts(key)
        self.assertLess(time.time() - start, 4.0)
        self.assertEqual(texts, {mod13._stored_key_text(key)})

    def test_public_gate_with_decoy_key_within_bound(self):
        runs = [
            run_record("run-1"),
            run_record("run-2", status="failed"),
            run_record("run-3", run_class="confirmation"),
        ]
        log = {ordered_key(16): "decoy", "runs": runs}
        start = time.time()
        result = mod13.compare_registry_against_run_log(
            registry_entry(), log)
        self.assertLess(time.time() - start, 4.0)
        self.assertTrue(result["passed"])

    def test_ordered_and_unordered_controls_hold(self):
        self.assertEqual(len(mod13._stored_key_texts(ordered_key(8))), 256)
        self.assertEqual(
            len(mod13._stored_key_texts(ordered_key(12))), 4096)
        self.assertEqual(
            len(mod13._stored_key_texts(frozenset("abcdefg"))), 5040)
        self.assertEqual(
            mod13._stored_key_texts(frozenset("abcdefgh")),
            {mod13._stored_key_text(frozenset("abcdefgh"))})


if __name__ == "__main__":
    unittest.main()

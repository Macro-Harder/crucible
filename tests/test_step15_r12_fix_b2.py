"""Pins for fix wave 11 Builder 2: rows R11-003 to R11-008 of the
Round 11 register, under settlement S-4. A barred reading must be
judged on the joined and segmented readings of the whole key,
across nesting boundaries and across part boundaries, in plain,
folded, and multi reading spaces alike, at MOD-01, MOD-03,
MOD-04, MOD-05, MOD-06, MOD-08, and MOD-10 alike. The proving
acts are the acts the source papers ran: Red 4 Findings 1 to 4,
Purple 2 Findings 1 to 3, and Blue 2 Findings 1 and 2 for the
MOD-04 locus. Seed dependent acts run in subprocesses at the
hash seeds the papers state.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

from crucible import mod01, mod03, mod04, mod05, mod06, mod08, mod10

ROOT = Path(__file__).resolve().parent.parent

FILLERS = ("zzq", "wwk", "vjx", "qzk", "xjw", "kvq")


def run_at_seeds(code, seeds):
    """Run one act script in a fresh process per hash seed and
    return the list of its printed lines per seed."""
    results = []
    for seed in seeds:
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = str(seed)
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, env=env, cwd=str(ROOT))
        if proc.returncode != 0:
            raise AssertionError(
                "seed %s act failed: %s" % (seed, proc.stderr))
        results.append(proc.stdout.strip())
    return results


def composite_part():
    """Red 4 Finding 1: a tuple of 13 frozenset pairs, the first
    four spelling undtruth in one ordering, nine clean fillers."""
    pairs = [
        frozenset(("u", "n")), frozenset(("d", "t")),
        frozenset(("r", "u")), frozenset(("t", "h")),
        frozenset(("a", "b")), frozenset(("c", "e")),
        frozenset(("f", "g")), frozenset(("i", "j")),
        frozenset(("k", "l")), frozenset(("m", "o")),
        frozenset(("p", "q")), frozenset(("s", "w")),
        frozenset(("v", "x")),
    ]
    return tuple(pairs)


class TestR11003CompositePartPastCut(unittest.TestCase):
    """R11-003: inside one composite part past the kept helper
    cut of 5040 (8192 candidates), the barred candidate must
    still be judged at every predicate and at the MOD-03
    public gates."""

    CODE = """
from crucible import mod03, mod04, mod05, mod08, mod10
pairs = [
    frozenset(("u", "n")), frozenset(("d", "t")),
    frozenset(("r", "u")), frozenset(("t", "h")),
    frozenset(("a", "b")), frozenset(("c", "e")),
    frozenset(("f", "g")), frozenset(("i", "j")),
    frozenset(("k", "l")), frozenset(("m", "o")),
    frozenset(("p", "q")), frozenset(("s", "w")),
    frozenset(("v", "x")),
]
part = tuple(pairs)
key = frozenset(("zzgro", part, "cleanpart"))
record = {key: 1}
print(mod03._is_barred_key(key))
print(mod04._is_barred_key(key))
print(mod05._panel_key_barred(key))
print(mod08._is_barred_key(key))
print(mod10._is_barred_view_key(key))
print(mod03.validate_detection_input(record))
print(mod03.record_carries_ground_truth(record))
stripped = mod03.strip_ground_truth(record)
print(key in stripped)
print(mod03._is_barred_key(
    frozenset(("zzgro", tuple(pairs[:12]), "cleanpart"))))
"""

    def test_predicates_and_gates_at_paper_seeds(self):
        expected = "\n".join([
            "True", "True", "True", "True", "True",
            "False", "True", "False", "True",
        ])
        for out in run_at_seeds(self.CODE, (0, 1, 2, 4)):
            self.assertEqual(out, expected)

    def test_membership_spelling_of_same_construction(self):
        # Purple 2 Finding 2: the membership spelling of the 13
        # pair construction (five target pairs, eight fillers)
        # stands barred at MOD-03 and MOD-04.
        pairs = [
            frozenset(("m", "e")), frozenset(("m", "b")),
            frozenset(("e", "r")), frozenset(("s", "h")),
            frozenset(("i", "p")),
            frozenset(("a", "c")), frozenset(("f", "g")),
            frozenset(("j", "k")), frozenset(("l", "n")),
            frozenset(("o", "q")), frozenset(("t", "u")),
            frozenset(("v", "w")), frozenset(("x", "z")),
        ]
        key = tuple(pairs)
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod04._is_barred_key(key))


class TestR11004SpanningInnerUnordered(unittest.TestCase):
    """R11-004: a barred name spanning an inner unordered
    container and a sibling outside it must be judged on the
    whole key: the inner join ground_tr is a segment of a
    barred name and no barred name on its own."""

    CODE = """
from crucible import mod03, mod08, mod10
inner = frozenset(("g", "r", "o", "u", "n", "d", "_", "tr"))
tuple_key = (inner, "uth")
frozen_key = frozenset((
    inner, "uth", "zzq", "wwk", "vjx", "qzk", "xjw"))
print(mod03._is_barred_key(inner))
print(mod03._is_barred_key(tuple_key))
print(mod08._is_barred_key(tuple_key))
print(mod10._is_barred_view_key(tuple_key))
print(mod03._is_barred_key(frozen_key))
print(mod08._is_barred_key(frozen_key))
print(mod10._is_barred_view_key(frozen_key))
print(mod03.validate_detection_input({tuple_key: 1}))
print(mod03.record_carries_ground_truth({tuple_key: 1}))
whole = frozenset(("g", "r", "o", "u", "n", "d", "_t", "ruth"))
print(mod03._is_barred_key(whole))
"""

    def test_spanning_forms_at_paper_seeds(self):
        expected = "\n".join([
            "False", "True", "True", "True", "True", "True",
            "True", "False", "True", "True",
        ])
        for out in run_at_seeds(self.CODE, (1, 2)):
            self.assertEqual(out, expected)


class TestR11005Mod06MultiReadingSegmentation(unittest.TestCase):
    """R11-005: a spelling barred only under a multi reading
    mixture, split across two parts of an 8 part frozenset past
    the kept bound with non vanishing fillers, must be judged
    at MOD-06 and refused at escrow_result."""

    CODE = """
from crucible import mod06
en = "\\u043d"
es = "\\u0441"
first = "4" + en + es + en + "0" * 12
second = "0" + "r" + "5" + "3" + "7" + "0" * 12
fillers = ("zzq", "wwk", "vjx", "qzk", "xjw", "kvq")
key = frozenset((first, second) + fillers)
small = frozenset((first, second))
joined = "4" + en + es + en + "0r537"
print(mod06._key_carries_multi_reading(joined, "anchorset"))
print(mod06._seg_payload_key(key, True))
print(mod06._payload_carries_barred({key: ["x"]}))
try:
    mod06.escrow_result("x", payload={key: ["x"]})
    print("delivered")
except ValueError:
    print("refused")
print(mod06._payload_carries_barred({small: ["x"]}))
try:
    mod06.escrow_result("x", payload={small: ["x"]})
    print("delivered")
except ValueError:
    print("refused")
"""

    def test_multi_reading_split_at_paper_seeds(self):
        expected = "\n".join([
            "True", "True", "True", "refused", "True", "refused",
        ])
        for out in run_at_seeds(self.CODE, (0, 1, 2, 4)):
            self.assertEqual(out, expected)


class TestR11006FoldedAcrossPartBoundary(unittest.TestCase):
    """R11-006: the folded reading realmani to realmoney arises
    only on a joined text; split as realma and ni inside one
    8 part frozenset it must stand barred at MOD-06 and
    carried at MOD-01, as MOD-10 already judges it."""

    CODE = """
from crucible import mod01, mod06, mod10
fillers = ("zzq", "wwk", "vjx", "qzk", "xjw", "kvq")
key = frozenset(("realma", "ni") + fillers)
small = frozenset(("realma", "ni"))
print("realmoney" in mod06._folded_readings("realmani"))
print(mod01._folded_key_carries("realmani", "realmoney"))
print(mod06._seg_payload_key(key, True))
print(mod06._payload_carries_barred({key: 10}))
try:
    mod06.escrow_result("x", payload={key: 10})
    print("delivered")
except ValueError:
    print("refused")
print(mod01._folded_key_carries(key, "realmoney"))
print(mod01._carries_real_money_value({key: 10}))
print(mod10._money_key_carries(key, "realmoney"))
print(mod06._payload_carries_barred({small: 10}))
"""

    def test_boundary_fold_at_paper_seeds(self):
        expected = "\n".join([
            "True", "True", "True", "True", "refused",
            "True", "True", "True", "True",
        ])
        for out in run_at_seeds(self.CODE, (1, 2)):
            self.assertEqual(out, expected)


class TestR11007Mod04NestedJoinedReading(unittest.TestCase):
    """R11-007: the MOD-04 joined reading must cross a nesting
    boundary, and a dict read by its keys must stand judged."""

    FORMS = [
        (("member",), "ship"),
        (("mem", "ber"), "ship"),
        ("member", ("ship",)),
        (["member"], "ship"),
        (("ground",), ("_truth",)),
        (("member",), b"ship"),
        ((b"member",), "ship"),
        (("MEMBER",), "SHIP"),
        (("member",), ("ship",)),
        ((b"member",), (b"ship",)),
        (("member",), (b"ship",)),
        ((b"member",), ("ship",)),
        ("member", ("ship",)),
        (("mem",), ("ber",), ("ship",)),
        ((("member",),), (("ship",),)),
        [["member"], [b"ship"]],
        (("ground",), ("_truth",)),
    ]

    def test_nested_forms_barred_at_mod04_and_mod03(self):
        for form in self.FORMS:
            self.assertTrue(mod04._is_barred_key(form), repr(form))
            self.assertTrue(mod03._is_barred_key(form), repr(form))

    def test_controls_hold_at_mod04(self):
        self.assertTrue(mod04._is_barred_key(("member", "ship")))
        self.assertTrue(mod04._is_barred_key((("member", "ship"),)))
        self.assertTrue(mod04._is_barred_key((("membership",),)))
        self.assertFalse(
            mod04._is_barred_key(frozenset(("member", "notes"))))
        self.assertFalse(mod04._is_barred_key(("ship", "member")))

    def test_dict_read_by_its_keys(self):
        self.assertTrue(mod04._is_barred_key({"membership": 1}))
        self.assertTrue(
            mod04._is_barred_key({"member": 1, "ship": 2}))
        self.assertTrue(mod03._is_barred_key({"membership": 1}))

    def test_public_gates_at_mod04(self):
        key = (("member",), "ship")
        self.assertTrue(
            mod04.view_record_carries_barred_field({key: 1}))
        cleaned = mod04._clean_feature_values({key: 1, "clean": 2})
        self.assertNotIn(key, cleaned)
        self.assertIn("clean", cleaned)
        state = {
            "agent_identifier": "agent-1",
            "day": 1,
            "feature_values": {key: 1, "clean": 2},
            "rule_records": [],
        }
        projection = mod04.project_detection_input(state)
        self.assertNotIn(key, projection["feature_values"])
        self.assertIn("clean", projection["feature_values"])

    def test_build_view_record_refuses_nested_key_contents(self):
        key = (("member",), "ship")
        with self.assertRaises(Exception):
            mod04.build_view_record(contents=[{key: 1}])


def chain(depth, base):
    key = base
    for _ in range(depth):
        key = (key,)
    return key


class TestR11008DeepChainRecursion(unittest.TestCase):
    """R11-008: a deep container chain carrying an unordered
    split at its base must answer, never raise a bare
    RecursionError, at MOD-03 and MOD-04."""

    def test_depth_990_answers_barred(self):
        key = chain(990, frozenset(("mem", "bership")))
        self.assertTrue(mod03._is_barred_key(key))
        self.assertTrue(mod04._is_barred_key(key))
        self.assertTrue(
            mod04.view_record_carries_barred_field({key: 1}))

    def test_depth_1100_and_2000_answer_barred(self):
        for depth in (1100, 2000):
            key = chain(depth, frozenset(("mem", "bership")))
            self.assertTrue(mod03._is_barred_key(key))
            self.assertTrue(mod04._is_barred_key(key))
            self.assertTrue(
                mod04.view_record_carries_barred_field({key: 1}))
            cleaned = mod04._clean_feature_values({key: 1})
            self.assertEqual(cleaned, {})

    def test_clean_chain_answers_clean_at_depth(self):
        for depth in (1100, 2000):
            key = chain(depth, frozenset(("cle", "an")))
            self.assertFalse(mod03._is_barred_key(key))
            self.assertFalse(mod04._is_barred_key(key))


if __name__ == "__main__":
    unittest.main()

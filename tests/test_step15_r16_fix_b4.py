"""Fix wave 15 pins, Builder 4, Group 4.

Rows pinned: R15-039, R15-040, and R15-041 of the Round 15
register, at crucible/mod03.py and crucible/mod12.py, under
settlement S-15 as the register states it: dress judged on
stored contents, order insensitive for unordered containers,
content based for buffers. The proving acts are the acts the
source papers used: Red 4 Finding 1, Purple 3 Finding P3-1,
and Yellow 4 Finding 1. Seed dependence proofs run across
hash seeds in fresh processes. Values are simulated and test
values only.
"""
import os
import subprocess
import sys
import unittest

from crucible import mod03, mod12

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEEDS = (0, 1, 2, 3, 4, 5, 6, 7, 42, 99)


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


class BA(bytearray):
    """A bytearray subclass member, storing plain bytes content."""


class TestR15039BufferMemberKey(unittest.TestCase):

    def test_bytearray_key_is_plain_stored_bytes(self):
        key = mod03._stored_member_key(bytearray(b"alpha"))
        self.assertEqual(b"alpha", key)
        self.assertIs(bytes, type(key))

    def test_memoryview_key_is_plain_stored_bytes(self):
        key = mod03._stored_member_key(memoryview(b"alpha"))
        self.assertEqual(b"alpha", key)
        self.assertIs(bytes, type(key))

    def test_bytearray_subclass_key_is_plain_stored_bytes(self):
        key = mod03._stored_member_key(BA(b"alpha"))
        self.assertEqual(b"alpha", key)
        self.assertIs(bytes, type(key))

    def test_bytearray_counts_on_distinct_endpoints(self):
        members = [bytearray(b"a"), bytearray(b"b"),
                   bytearray(b"c"), bytearray(b"d")]
        edges = [(bytearray(b"a"), bytearray(b"b")),
                 (bytearray(b"c"), bytearray(b"d"))]
        result = mod03.construct_farm(members, farm_size=2,
                                      edges=edges)
        self.assertEqual(
            {"farm-0": 1, "farm-1": 1},
            result["internal_edge_count_per_farm_identity"])

    def test_memoryview_counts_on_distinct_endpoints(self):
        members = {memoryview(b"a"), memoryview(b"b"),
                   memoryview(b"c"), memoryview(b"d"),
                   memoryview(b"e"), memoryview(b"f")}
        edges = [(memoryview(b"a"), memoryview(b"b")),
                 (memoryview(b"e"), memoryview(b"f"))]
        result = mod03.construct_farm(members, farm_size=2,
                                      edges=edges)
        grouping = [
            [bytes(member) for member in farm["member_ids"]]
            for farm in result["farms"]]
        self.assertEqual(
            [[b"a", b"b"], [b"c", b"d"], [b"e", b"f"]], grouping)
        self.assertEqual(
            {"farm-0": 1, "farm-1": 0, "farm-2": 1},
            result["internal_edge_count_per_farm_identity"])

    def test_memoryview_dict_edges_on_distinct_endpoints(self):
        members = {memoryview(b"a"), memoryview(b"b"),
                   memoryview(b"c"), memoryview(b"d")}
        edges = [{"voucher": memoryview(b"a"),
                  "vouchee": memoryview(b"b")}]
        result = mod03.build_farm(members, farm_size=2, edges=edges)
        self.assertEqual(
            {"farm-0": 1, "farm-1": 0},
            result["internal_edge_count_per_farm_identity"])

    def test_control_plain_bytes_counts_on_distinct_endpoints(self):
        members = [b"a", b"b", b"c", b"d"]
        edges = [(b"a", b"b"), (b"c", b"d")]
        result = mod03.construct_farm(members, farm_size=2,
                                      edges=edges)
        self.assertEqual(
            {"farm-0": 1, "farm-1": 1},
            result["internal_edge_count_per_farm_identity"])


FARM_CODE = (
    "from crucible.mod03 import construct_farm\n"
    "members = {memoryview(b'a'), memoryview(b'b'), "
    "memoryview(b'c'), memoryview(b'd'), memoryview(b'e'), "
    "memoryview(b'f')}\n"
    "edges = [(memoryview(b'a'), memoryview(b'b')), "
    "(memoryview(b'e'), memoryview(b'f'))]\n"
    "result = construct_farm(members, farm_size=2, edges=edges)\n"
    "print([[bytes(m) for m in farm['member_ids']] "
    "for farm in result['farms']])\n"
    "print(result['internal_edge_count_per_farm_identity'])\n"
)


class TestR15039FarmCountsAcrossSeeds(unittest.TestCase):

    def test_counts_stable_at_every_seed(self):
        expected = (
            "[[b'a', b'b'], [b'c', b'd'], [b'e', b'f']]\n"
            "{'farm-0': 1, 'farm-1': 0, 'farm-2': 1}")
        for seed in SEEDS:
            self.assertEqual(
                expected, run_at_seed(FARM_CODE, seed),
                "seed %d" % seed)


ECOLOGY_CODE = (
    "from crucible.mod12 import make_family_record, "
    "validate_family_record, family_record_validation_failures\n"
    "record = make_family_record()\n"
    "record['ecology_point'] = {'fix', 'ed'}\n"
    "record.pop('amendment_landed', None)\n"
    "print(validate_family_record(record))\n"
    "print(any('ecology' in failure for failure in "
    "family_record_validation_failures(record)))\n"
)

ECOLOGY_FROZEN_CODE = ECOLOGY_CODE.replace(
    "{'fix', 'ed'}", "frozenset({'fix', 'ed'})")

KILL_CODE = (
    "from crucible.mod12 import make_family_record, "
    "validate_family_record, family_record_validation_failures\n"
    "record = make_family_record()\n"
    "checks = [{'claim': {'headline claim ', '1'}}]\n"
    "record['kill_check_fields'] = checks\n"
    "record['kill_checks'] = list(checks)\n"
    "print(validate_family_record(record))\n"
    "print(family_record_validation_failures(record))\n"
)

KILL_FROZEN_CODE = KILL_CODE.replace(
    "{'headline claim ', '1'}",
    "frozenset({'headline ', 'claim 1'})")


class TestR15040SetDressAcrossSeeds(unittest.TestCase):

    def test_ecology_set_refused_at_every_seed(self):
        for seed in SEEDS:
            self.assertEqual(
                "False\nTrue", run_at_seed(ECOLOGY_CODE, seed),
                "seed %d" % seed)

    def test_ecology_frozenset_refused_at_every_seed(self):
        for seed in SEEDS:
            self.assertEqual(
                "False\nTrue",
                run_at_seed(ECOLOGY_FROZEN_CODE, seed),
                "seed %d" % seed)

    def test_kill_set_claim_stands_at_every_seed(self):
        for seed in SEEDS:
            self.assertEqual(
                "True\n[]", run_at_seed(KILL_CODE, seed),
                "seed %d" % seed)

    def test_kill_frozenset_claim_stands_at_every_seed(self):
        for seed in SEEDS:
            self.assertEqual(
                "True\n[]", run_at_seed(KILL_FROZEN_CODE, seed),
                "seed %d" % seed)


class TestR15040DressJudgementInProcess(unittest.TestCase):

    def test_dress_eq_reads_set_parts_in_any_order(self):
        self.assertTrue(mod12._dress_eq({"fix", "ed"}, "fixed"))
        self.assertTrue(
            mod12._dress_eq(frozenset({"fix", "ed"}), "fixed"))

    def test_dress_eq_nested_unordered_part(self):
        self.assertTrue(
            mod12._dress_eq(({"fix", "ed"},), "fixed"))
        self.assertTrue(
            mod12._dress_eq(["fix", {"e", "d"}], "fixed"))

    def test_dress_eq_negative_control(self):
        self.assertFalse(mod12._dress_eq({"fix", "zz"}, "fixed"))
        self.assertFalse(
            mod12._dress_eq(frozenset({"fix", "zz"}), "fixed"))

    def test_kill_claim_in_set_dress_counts_as_standing(self):
        record = mod12.make_family_record()
        checks = [{"claim": {"headline claim ", "1"}}]
        record["kill_check_fields"] = checks
        record["kill_checks"] = list(checks)
        self.assertFalse(mod12._kill_check_names_absent(record))
        self.assertTrue(mod12.validate_family_record(record))


class ReprRaises:
    """A handed value whose repr and str readings raise."""

    def __repr__(self):
        raise RuntimeError("repr reading raises")

    def __str__(self):
        raise RuntimeError("str reading raises")


class BadReprText(str):
    """A text value whose repr reading raises."""

    def __repr__(self):
        raise RuntimeError("repr reading raises")


class TestR15041RunCompanionRepr(unittest.TestCase):

    def test_repr_raising_run_class_named_not_bare(self):
        record = {"run_class": ReprRaises(),
                  "seed_domain": "screening"}
        self.assertFalse(mod12.validate_run_record(record))
        failures = mod12.run_record_validation_failures(record)
        self.assertEqual(1, len(failures))
        self.assertIn(
            "run_class stands outside the stated run classes",
            failures[0])

    def test_repr_raising_text_run_class_named_not_bare(self):
        record = {"run_class": BadReprText("bogus class"),
                  "seed_domain": "screening"}
        self.assertFalse(mod12.validate_run_record(record))
        failures = mod12.run_record_validation_failures(record)
        self.assertEqual(1, len(failures))
        self.assertIn(
            "run_class stands outside the stated run classes",
            failures[0])

    def test_controls(self):
        bogus = {"run_class": "bogus", "seed_domain": "screening"}
        failures = mod12.run_record_validation_failures(bogus)
        self.assertEqual(1, len(failures))
        self.assertIn(
            "run_class stands outside the stated run classes",
            failures[0])
        lawful = {"run_class": "screening",
                  "seed_domain": "screening"}
        self.assertTrue(mod12.validate_run_record(lawful))
        self.assertEqual(
            [], mod12.run_record_validation_failures(lawful))


if __name__ == "__main__":
    unittest.main()

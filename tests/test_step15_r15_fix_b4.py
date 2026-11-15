"""Fix wave 14 pins, Builder 4, Group 4.

Rows pinned: R14-029, R14-030, and R14-064 of the Round 14
register, at crucible/mod03.py and crucible/mod09.py. The
proving acts are the acts the Round 14 source papers used:
Red 4 Findings 1 and 2, and Blue 4 Finding 6. Values are
simulated and test values only.
"""
import os
import subprocess
import sys
import unittest

from crucible import mod03, mod09

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEEDS = (0, 1, 2, 7, 42)


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


class B(bytes):
    """A bytes subclass member, storing plain bytes content."""


class I(int):
    """An int subclass member, storing a plain integer."""


class F(float):
    """A float subclass member, storing a plain float."""


class C(complex):
    """A complex subclass member, storing a plain complex."""


class TestR14029StoredMemberKey(unittest.TestCase):

    def test_bytes_subclass_key_is_plain_stored_bytes(self):
        key = mod03._stored_member_key(B(b"alpha"))
        self.assertEqual(b"alpha", key)
        self.assertIs(bytes, type(key))

    def test_int_subclass_key_is_plain_stored_int(self):
        key = mod03._stored_member_key(I(7))
        self.assertEqual(7, key)
        self.assertIs(int, type(key))

    def test_float_and_complex_subclass_keys_are_plain(self):
        fkey = mod03._stored_member_key(F(1.5))
        self.assertEqual(1.5, fkey)
        self.assertIs(float, type(fkey))
        ckey = mod03._stored_member_key(C(2 + 3j))
        self.assertEqual(2 + 3j, ckey)
        self.assertIs(complex, type(ckey))

    def test_subclass_members_order_by_content_not_identity(self):
        self.assertLess(
            mod03._member_order_key(B(b"a")),
            mod03._member_order_key(B(b"b")))
        self.assertEqual(1, mod03._member_order_key(B(b"a"))[0])
        self.assertLess(
            mod03._member_order_key(I(1)),
            mod03._member_order_key(I(2)))
        self.assertEqual(2, mod03._member_order_key(I(1))[0])

    def test_bytes_subclass_grouping_follows_content(self):
        members = {B(b"a"), B(b"b"), B(b"c"), B(b"d"), B(b"e"),
                   B(b"f")}
        edges = [(B(b"a"), B(b"b")), (B(b"e"), B(b"f"))]
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

    def test_int_subclass_grouping_follows_content(self):
        members = {I(1), I(2), I(3), I(4), I(5), I(6)}
        edges = [(I(1), I(2)), (I(5), I(6))]
        result = mod03.construct_farm(members, farm_size=2,
                                      edges=edges)
        grouping = [
            [int(member) for member in farm["member_ids"]]
            for farm in result["farms"]]
        self.assertEqual([[1, 2], [3, 4], [5, 6]], grouping)
        self.assertEqual(
            {"farm-0": 1, "farm-1": 0, "farm-2": 1},
            result["internal_edge_count_per_farm_identity"])

    def test_allocation_order_does_not_move_grouping(self):
        outcomes = []
        for allocate in (
                lambda: [B(bytes([97 + i])) for i in range(6)],
                lambda: [B(bytes([102 - i])) for i in range(6)]):
            members = set(allocate())
            edges = [(B(b"a"), B(b"b")), (B(b"e"), B(b"f"))]
            result = mod03.construct_farm(members, farm_size=2,
                                          edges=edges)
            outcomes.append((
                [[bytes(m) for m in farm["member_ids"]]
                 for farm in result["farms"]],
                result["internal_edge_count_per_farm_identity"]))
        self.assertEqual(outcomes[0], outcomes[1])

    def test_control_plain_members_unchanged(self):
        self.assertEqual(b"a", mod03._stored_member_key(b"a"))
        self.assertEqual(3, mod03._stored_member_key(3))
        self.assertEqual("x", mod03._stored_member_key("x"))


FROZEN_CODE = (
    "from crucible.mod09 import strategy_catalogue, "
    "_catalogue_order_key\n"
    "extras = {frozenset({'a', 'z'}), frozenset({'m', 'n'})}\n"
    "print([tuple(sorted(name)) for name in "
    "strategy_catalogue(extra_identifiers=extras)"
    "['identifiers'][1:]])\n"
    "print(_catalogue_order_key(frozenset({'a', 'z'})))\n"
    "print(_catalogue_order_key(frozenset({'m', 'n'})))\n"
)

TUPLE_CODE = (
    "from crucible.mod09 import strategy_catalogue\n"
    "extras = {(frozenset({'a', 'z'}),), (frozenset({'m', 'n'}),)}\n"
    "print([tuple(tuple(sorted(part)) for part in name) "
    "for name in strategy_catalogue(extra_identifiers=extras)"
    "['identifiers'][1:]])\n"
)


class TestR14030CatalogueSeedStability(unittest.TestCase):

    def test_frozenset_key_is_canonical_in_this_process(self):
        self.assertEqual(
            (2, "frozenset", "frozenset({'a', 'z'})"),
            mod09._catalogue_order_key(frozenset({"a", "z"})))
        self.assertEqual(
            (2, "frozenset", "frozenset({'m', 'n'})"),
            mod09._catalogue_order_key(frozenset({"m", "n"})))

    def test_frozenset_order_identical_across_seeds(self):
        outputs = {run_at_seed(FROZEN_CODE, seed) for seed in SEEDS}
        self.assertEqual(1, len(outputs))

    def test_tuple_carrying_frozenset_order_across_seeds(self):
        outputs = {run_at_seed(TUPLE_CODE, seed) for seed in SEEDS}
        self.assertEqual(1, len(outputs))

    def test_frozenset_catalogue_order_is_content_order(self):
        out = run_at_seed(FROZEN_CODE, 0)
        first_line = out.splitlines()[0]
        self.assertLess(
            first_line.index("'a'"), first_line.index("'m'"))

    def test_control_tied_nameless_keys_still_tie(self):
        class Nameless:
            def __repr__(self):
                return "nameless"

        first, second = Nameless(), Nameless()
        self.assertEqual(
            mod09._catalogue_order_key(first),
            mod09._catalogue_order_key(second))


class AlwaysEq:
    """An object whose equality reading answers True to every
    comparison, storing no identifier text."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 12345


class NeverEqStr(str):
    """A text identifier whose equality reading answers False
    to every comparison, storing plain text."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class TestR14064CatalogueMembership(unittest.TestCase):

    def test_always_eq_extra_identifier_is_listed(self):
        marker = AlwaysEq()
        result = mod09.strategy_catalogue(extra_identifiers=[marker])
        self.assertTrue(
            any(name is marker for name in result["identifiers"]))

    def test_never_eq_duplicate_extra_enters_once(self):
        result = mod09.strategy_catalogue(extra_identifiers=[
            NeverEqStr("duptext"), NeverEqStr("duptext")])
        texts = [
            str(name) for name in result["identifiers"]
            if str(name) == "duptext"]
        self.assertEqual(1, len(texts))

    def test_record_entry_membership_uses_stored_forms(self):
        marker = AlwaysEq()
        fake_record = {"entries": [
            {"archetype_id": NeverEqStr("entrydup")},
            {"archetype_id": NeverEqStr("entrydup")},
            {"archetype_id": marker},
        ]}
        original = mod09.mod03_catalogue_record
        mod09.mod03_catalogue_record = lambda: fake_record
        try:
            result = mod09.strategy_catalogue()
        finally:
            mod09.mod03_catalogue_record = original
        texts = [
            str(name) for name in result["identifiers"]
            if str(name) == "entrydup"]
        self.assertEqual(1, len(texts))
        self.assertTrue(
            any(name is marker for name in result["identifiers"]))

    def test_control_plain_duplicate_enters_once(self):
        result = mod09.strategy_catalogue(
            extra_identifiers=["alpha", "alpha"])
        self.assertEqual(
            1, result["identifiers"].count("alpha"))


if __name__ == "__main__":
    unittest.main()

"""Step 17 fix wave 5, Slice 6 defect tests, row FW5-07.

Row FW5-07 (Medium, T17R4-07, filing Green 1 S17R4-G1-01):
crucible.mod09.strategy_catalogue grows quadratically in its
extra identifiers handing, with no bound and no named refusal.
The charged growth form stands as follows: on the uncured tree
the membership judgement for each handed identifier scans every
identifier already listed, so the stored form comparison work
of one act grows with the square of the handing size.

The cure form this slice builds stands as option A of the fix
wave 5 charge, Slice 6: strategy_catalogue stands bounded in
growth form so its per act cost stands governed by the handing
in linear form. The bound the cure states stands as follows:
the stored form membership work of one act, counted as calls
to the module stored match and stored equality readings,
stands at or below a stated linear bound in the handing count
for an ordered handing of distinct short text identifiers,
the form the filing paper uses. The defect test for that bound
counts comparisons, never a timing: a timing figure alone
reproduces nothing and charges nothing, and the measured times
at the filing sizes stand printed by the served whole test as
measurements beside the row, never as a verdict.

Every other test of this file pins the served whole standing
the cure must preserve: distinct identifiers served whole in
handed order at the filing sizes, duplicates entering once
under the stored form judgement at scale, the identity form,
the numeric and buffer dedup forms, the set content order, the
bare text control, the NaN never deduped form, and a cyclic
list extra carried whole.
"""

import time
import unittest

from crucible import mod09


class NeverEqStr(str):
    """A text identifier whose equality reading answers False
    to every comparison, storing plain text."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class AlwaysEq:
    """An object whose equality reading answers True to every
    comparison, storing no identifier text."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 12345


def _tail(result, count):
    return result["identifiers"][-count:]


class TestFW507LinearGrowthForm(unittest.TestCase):

    def test_membership_work_linear_in_handing_count(self):
        n = 1500
        extras = ["s%d" % i for i in range(n)]
        calls = {"count": 0}
        real_match = mod09._stored_match
        real_eq = mod09._stored_eq

        def counting_match(first, second):
            calls["count"] += 1
            return real_match(first, second)

        def counting_eq(first, second):
            calls["count"] += 1
            return real_eq(first, second)

        mod09._stored_match = counting_match
        mod09._stored_eq = counting_eq
        try:
            result = mod09.strategy_catalogue(
                extra_identifiers=list(extras))
        finally:
            mod09._stored_match = real_match
            mod09._stored_eq = real_eq
        self.assertEqual(extras, _tail(result, n))
        self.assertLessEqual(calls["count"], 8 * n + 100)

    def test_distinct_text_extras_served_whole_at_filing_sizes(self):
        for n in (500, 1000, 2000, 5000):
            extras = ["s%d" % i for i in range(n)]
            start = time.perf_counter()
            result = mod09.strategy_catalogue(
                extra_identifiers=list(extras))
            elapsed = time.perf_counter() - start
            print("catalogue_%d %.3f seconds" % (n, elapsed))
            self.assertEqual(extras, _tail(result, n))

    def test_duplicate_text_extras_enter_once_at_scale(self):
        extras = ["d%d" % i for i in range(1200)]
        handed = extras + list(reversed(extras))
        result = mod09.strategy_catalogue(extra_identifiers=handed)
        self.assertEqual(extras, _tail(result, 1200))

    def test_stored_form_duplicate_judgement_preserved_at_scale(self):
        handed = [NeverEqStr("duptext") for _ in range(300)]
        handed += [NeverEqStr("t%d" % i) for i in range(300)]
        result = mod09.strategy_catalogue(extra_identifiers=handed)
        tail = _tail(result, 301)
        texts = [str(name) for name in tail]
        self.assertEqual(1, texts.count("duptext"))
        self.assertEqual(301, len(tail))

    def test_identity_form_extras_each_listed_at_scale(self):
        markers = [AlwaysEq() for _ in range(300)]
        result = mod09.strategy_catalogue(
            extra_identifiers=list(markers))
        tail = _tail(result, 300)
        self.assertTrue(
            all(name is marker
                for name, marker in zip(tail, markers)))

    def test_mixed_form_dedup_preserved(self):
        handed = [
            1, 1.0, True,
            b"bytes-id", bytearray(b"bytes-id"),
            memoryview(b"bytes-id"),
            [1, 2], [1.0, 2.0], (1, 2),
            {"k": 1}, {"k": 1.0},
            {1, 2}, frozenset({2, 1}),
        ]
        result = mod09.strategy_catalogue(extra_identifiers=handed)
        tail = _tail(result, 7)
        self.assertEqual(
            [1, True, b"bytes-id", [1, 2], (1, 2), {"k": 1}, {1, 2}],
            tail)
        self.assertIs(type(tail[0]), int)
        self.assertIs(tail[1], True)
        self.assertIs(type(tail[2]), bytes)
        self.assertIs(type(tail[5]), dict)
        self.assertIs(type(tail[6]), set)

    def test_set_extras_stand_in_content_order_at_scale(self):
        extras = {"s%04d" % i for i in range(800)}
        result = mod09.strategy_catalogue(extra_identifiers=extras)
        self.assertEqual(sorted(extras), _tail(result, 800))

    def test_nan_extra_never_deduped(self):
        nan = float("nan")
        result = mod09.strategy_catalogue(
            extra_identifiers=[nan, nan])
        tail = _tail(result, 2)
        self.assertTrue(all(name is nan for name in tail))

    def test_cyclic_list_extra_carried_whole(self):
        cyclic = []
        cyclic.append(cyclic)
        result = mod09.strategy_catalogue(
            extra_identifiers=[cyclic, ["plain"]])
        tail = _tail(result, 2)
        self.assertIs(tail[0], cyclic)
        self.assertEqual(["plain"], tail[1])

    def test_bare_text_and_default_controls(self):
        plain = mod09.strategy_catalogue()
        self.assertEqual("conditional briber", plain["identifiers"][0])
        solo = mod09.strategy_catalogue(extra_identifiers="solo")
        self.assertEqual("solo", solo["identifiers"][-1])
        self.assertEqual(
            len(plain["identifiers"]) + 1, len(solo["identifiers"]))


if __name__ == "__main__":
    unittest.main()

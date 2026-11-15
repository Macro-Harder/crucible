"""Pin tests for fix wave 17, builder 2, group 2 rows.

Rows pinned: R17-003, R17-010, R17-021, R17-041, and R17-045,
all at crucible/mod12.py, with the R17-003 companion limb at
crucible/mod13.py. Each test stands in the distinguishing case
form: it fails on the pristine tree for the charged defect and
passes after the cure.
"""

import time
import unittest
from decimal import Decimal
from fractions import Fraction

from crucible import mod12
from crucible import mod13


def _charged_key():
    """Seven distinct outer parts, each composing exactly the
    same three texts, the R17-003 construction: the inner
    frozenset holds the texts a, a in bytes dress, and b, so
    its joins stand as the three texts aab, aba, and baa, and
    each outer part carries that inner part beside a distinct
    integer part composing the empty text."""
    inner = frozenset({"a", b"a", "b"})
    return frozenset((inner, index) for index in range(7))


class TestR17003KeyTextsWorkBound(unittest.TestCase):

    def test_mod12_charged_construction_exact_and_fast(self):
        small = mod12._key_stored_texts(frozenset({"ab", "cd"}))
        self.assertEqual(small, {"abcd", "cdab"})
        start = time.monotonic()
        texts = mod12._key_stored_texts(_charged_key())
        elapsed = time.monotonic() - start
        self.assertEqual(len(texts), 2187)
        self.assertLess(elapsed, 5.0)

    def test_mod13_charged_construction_exact_and_fast(self):
        small = mod13._stored_key_texts(frozenset({"ab", "cd"}))
        self.assertEqual(small, {"abcd", "cdab"})
        start = time.monotonic()
        texts = mod13._stored_key_texts(_charged_key())
        elapsed = time.monotonic() - start
        self.assertEqual(len(texts), 2187)
        self.assertLess(elapsed, 5.0)


class TestR17010StoredValuesEqualKindFirst(unittest.TestCase):

    def test_cross_kind_pairs_judge_apart(self):
        self.assertIs(mod12._stored_values_equal(True, 1), False)
        self.assertIs(mod12._stored_values_equal(Decimal(1), 1), False)
        self.assertIs(mod12._stored_values_equal(Fraction(1, 1), 1), False)
        self.assertIs(mod12._stored_values_equal([True], [1]), False)
        self.assertIs(mod12._stored_values_equal(1, 1.0), False)
        self.assertIs(mod12._stored_values_equal(1, True), False)
        self.assertIs(mod12._stored_values_equal(Decimal(1), Decimal(1)), True)
        self.assertIs(
            mod12._stored_values_equal(Fraction(1, 2), Fraction(1, 2)), True)
        self.assertIs(mod12._stored_values_equal(True, True), True)
        self.assertIs(mod12._stored_values_equal(1, 1), True)
        self.assertIs(
            mod12._stored_values_equal([Decimal(1)], [Decimal(1)]), True)
        self.assertIs(mod12._stored_values_equal("claim", "claim"), True)

    def test_gate_verdicts_follow_kind_first(self):
        self.assertIs(mod12.validate_seed_placement({
            "replicates_inside_base_design": False,
            "confirmation_family": True,
            "screening_family": 1}), True)
        self.assertIs(mod12.validate_seed_placement({
            "replicates_inside_base_design": False,
            "confirmation_family": Decimal(1),
            "screening_family": 1}), True)
        self.assertIs(mod12.validate_record_version({
            "produced_under": 1, "presented_under": True}), False)
        self.assertIs(mod12.validate_record_version({
            "produced_under": 1, "presented_under": 1}), True)

    def test_kill_check_names_absent_sees_boolean_claim(self):
        self.assertIs(mod12._kill_check_names_absent({
            "headline_claims": [1],
            "kill_check_fields": [{"claim": True}]}), True)
        self.assertIs(mod12._kill_check_names_absent({
            "headline_claims": [1],
            "kill_check_fields": [{"claim": 1}]}), False)


class _IterLie(list):
    """A list subclass whose own iteration yields a claim it
    does not store."""

    def __iter__(self):
        return iter(["fabricated claim"])


class _BoolRaise:
    """A value in no container form whose truth reading raises."""

    def __bool__(self):
        raise RuntimeError("bool boom")


class TestR17021KillChecksForFamilyClaimsReading(unittest.TestCase):

    def test_list_subclass_delivers_stored_claim(self):
        checks = mod12.kill_checks_for_family(
            "family-under-test", _IterLie(["real claim"]))
        self.assertEqual(
            [check["name"] for check in checks],
            ["kill check for real claim"])
        self.assertEqual(checks[0]["claim"], "real claim")

    def test_non_container_handings_stand_as_default(self):
        default = ["kill check for headline claim 1"]
        for handing in ("ab", 5, object()):
            checks = mod12.kill_checks_for_family(
                "family-under-test", handing)
            self.assertEqual(
                [check["name"] for check in checks], default)

    def test_generator_stands_unread_as_default(self):
        def claims():
            yield "gen claim"

        handed = claims()
        checks = mod12.kill_checks_for_family(
            "family-under-test", handed)
        self.assertEqual(
            [check["name"] for check in checks],
            ["kill check for headline claim 1"])
        self.assertEqual(next(handed), "gen claim")

    def test_raising_truth_reading_stands_as_default(self):
        checks = mod12.kill_checks_for_family(
            "family-under-test", _BoolRaise())
        self.assertEqual(
            [check["name"] for check in checks],
            ["kill check for headline claim 1"])


class _StrRaise:
    """A claim whose own string reading raises."""

    def __str__(self):
        raise RuntimeError("str boom")


class TestR17041KillCheckForClaimName(unittest.TestCase):

    def test_str_raising_claim_delivers_named_check(self):
        check = mod12.kill_check_for_claim(_StrRaise())
        self.assertTrue(check["name"].startswith("kill check for "))
        self.assertEqual(
            check["killing_result"],
            "the claim does not stand as reported")
        checks = mod12.kill_checks_for_family(
            "family-under-test", [_StrRaise()])
        self.assertEqual(len(checks), 1)
        self.assertTrue(checks[0]["name"].startswith("kill check for "))
        self.assertEqual(
            mod12.kill_check_for_claim("headline claim 1")["name"],
            "kill check for headline claim 1")
        check = mod12.kill_check_for_claim(object())
        self.assertTrue(check["name"].startswith("kill check for <object"))


def _run(run_id):
    return {"run_class": "screening", "run_id": run_id}


class TestR17045SampleStatementRepeatedNames(unittest.TestCase):

    def test_repeated_printed_names_carry_their_kinds(self):
        statement = mod12.sample_statement([_run(1.0), _run("1.0")])
        self.assertEqual(statement["n"], 2)
        self.assertIn("1.0 (float)", statement["sample"])
        self.assertIn("1.0 (text)", statement["sample"])
        statement = mod12.sample_statement([_run(True), _run("True")])
        self.assertEqual(statement["n"], 2)
        self.assertIn("True (boolean)", statement["sample"])
        self.assertIn("True (text)", statement["sample"])
        statement = mod12.sample_statement([_run(2.5), _run("2.5")])
        self.assertEqual(statement["n"], 2)
        self.assertIn("2.5 (float)", statement["sample"])
        self.assertIn("2.5 (text)", statement["sample"])
        statement = mod12.sample_statement([_run(1), _run("1")])
        self.assertEqual(statement["n"], 1)
        self.assertEqual(
            statement["sample"],
            "the runs named in this statement: 1")
        statement = mod12.sample_statement([_run("r1"), _run("r2")])
        self.assertEqual(statement["n"], 2)
        self.assertEqual(
            statement["sample"],
            "the runs named in this statement: r1, r2")


if __name__ == "__main__":
    unittest.main()

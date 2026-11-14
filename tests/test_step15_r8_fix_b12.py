"""Step 15 rerun fix wave 7 completion pins, Builder 12.

Pins for the regression the fix wave 7 Builder 2 anywhere
transposition limb introduced: a word built from a candidate
by two disjoint transposed pairs and one replaced letter,
five differing positions in all, carries a transposed pair
among its differing positions, so the limb read it as one
transposed pair composed with three replacements and
resolved it, although its change total stands at three and
the standing composition form resolves such a composition
only where the total stands past three. The twelve forms
below stand as themselves at both actor normalisers and
promote at both flag acts, in the form
tests/test_step15_r6_fix_b15.py already pins. Control pins
cover the row R7-003 forms the anywhere limb was built for:
one transposed pair at any positions, the edge positions
included, composed with three genuine replacements, at the
actor words and at the MOD-14 target resolver.

Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


RESOLVER_ONLY = [
    "eprosx", "eprxno", "epsrox", "epsrxn", "epxosn", "epxsno",
    "preosx", "prexno", "pxsrno", "xesrno", "xreosn", "xresno",
]


class B12Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def core_record(self):
        return {
            "retention_tier": "Tier 1",
            "flag_conditions_fired": ["condition a"],
        }

    def core_promote(self, actor):
        return mod10.apply_flag_evaluation(
            self.core_record(), outcome="promote", tier="Tier 2",
            actor=actor,
            inputs={"flag_conditions_fired": ["condition a"]})

    def shell_promote(self, actor):
        return mod14.flag_evaluation(
            self.core_record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor=actor)

    def assert_both_refuse_person(self, actor):
        self.assertEqual(mod10._normalised_actor(actor), "person")
        self.assertEqual(mod14._normalise_actor(actor), "person")
        with self.assertRaises(ValueError):
            self.core_promote(actor)
        with self.assertRaises(ValueError):
            self.shell_promote(actor)


class TestTwoTranspositionsOneReplacementStandAsThemselves(B12Base):
    def test_resolver_only_forms_read_as_themselves_at_mod10(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(mod10._normalised_actor(actor), actor)
                self.assertEqual(
                    mod10._resolve_actor_word(actor), actor)

    def test_resolver_only_forms_read_as_themselves_at_mod14(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(mod14._normalise_actor(actor), actor)
                self.assertEqual(
                    mod14._resolve_actor_word(actor), actor)

    def test_resolver_only_forms_promote_at_both_acts(self):
        for actor in RESOLVER_ONLY:
            with self.subTest(actor=actor):
                self.assertEqual(
                    self.core_promote(actor)["retention_tier"],
                    "Tier 2")
                self.assertEqual(
                    self.shell_promote(actor)["retention_tier"],
                    "Tier 3")


class TestAnywherePairWithThreeReplacementsStillResolves(B12Base):
    def test_actor_edge_pair_with_three_replacements(self):
        self.assert_both_refuse_person("nqzjop")

    def test_target_edge_pair_with_three_replacements(self):
        self.assertEqual(mod14._resolve_word("tqzjkpoinc"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "tqzjkpoinc set",
             "path": "other rule"}))

    def test_target_inner_pair_with_three_replacements(self):
        self.assertEqual(mod14._resolve_word("chpqzejint"), "checkpoint")
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "delete", "target": "chpqzejint set",
             "path": "other rule"}))

    def test_actor_adjacent_pair_with_three_replacements(self):
        self.assert_both_refuse_person("eprxxx")


if __name__ == "__main__":
    unittest.main()

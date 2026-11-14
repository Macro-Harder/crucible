"""Step 15 rerun fix wave 8 pins, rows R8-001, R8-003, R8-004,
and R8-005, MOD-10 limbs only.

Pins for the transposition compositions at
crucible/mod10.py _resolve_actor_word. Row R8-003: three
disjoint transposed pairs standing anywhere in the word
resolve at the MOD-14 actor normaliser and stood unread at
the MOD-10 actor normaliser, which carried no pairing limb,
so a barred person promotion stood effected at the MOD-10
flag act. Row R8-004: the same missing pairing limb read a
program actor in that dress as person through the mixed
added limb, which tests person before program, so a lawful
program promotion stood refused at the MOD-10 flag act.
Row R8-001, MOD-10 limb: two transposed pairs at any
positions composed with two replaced letters, six differing
positions and a change total of four, resolved at neither
actor normaliser. Row R8-005, MOD-10 limb: a word built
from two transposed pairs and one replaced letter resolved
where exactly one pair stands adjacent, because the older
composition limb counted the adjacent pair as the
transposition and the three remaining positions as
replacements, although the change total stands at three.

Control pins stand both ways: the adjacent compositions
resolve, the resolver only forms of two transposed pairs
with one replaced letter stand as themselves, one pair at
any positions with three genuine replacements resolves,
and a total past the stated composition form stands as
itself. Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10


class B9Base(unittest.TestCase):
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

    def assert_mod10_person_refused(self, actor):
        self.assertEqual(mod10._resolve_actor_word(actor), "person")
        self.assertEqual(mod10._normalised_actor(actor), "person")
        with self.assertRaises(ValueError):
            self.core_promote(actor)

    def assert_mod10_program_promoted(self, actor):
        self.assertEqual(mod10._resolve_actor_word(actor), "program")
        self.assertEqual(mod10._normalised_actor(actor), "program")
        self.assertEqual(
            self.core_promote(actor)["retention_tier"], "Tier 2")

    def assert_mod10_itself_promoted(self, actor):
        self.assertEqual(mod10._resolve_actor_word(actor), actor)
        self.assertEqual(mod10._normalised_actor(actor), actor)
        self.assertEqual(
            self.core_promote(actor)["retention_tier"], "Tier 2")


class TestR8003ThreePairsPerson(B9Base):
    """One defect method per charged R8-003 person instance:
    three disjoint transposed pairs at nonadjacent positions."""

    def test_nosrep_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("nosrep")

    def test_nsoerp_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("nsoerp")

    def test_sonper_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("sonper")

    def test_rnpose_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("rnpose")


class TestR8004ThreePairsProgram(B9Base):
    """One defect method per charged R8-004 program instance:
    three disjoint transposed pairs read as program, not
    person, at the MOD-10 normaliser."""

    def test_margorp_resolves_program_at_mod10(self):
        self.assert_mod10_program_promoted("margorp")

    def test_agmrrpo_resolves_program_at_mod10(self):
        self.assert_mod10_program_promoted("agmrrpo")


class TestR8001TwoPairsTwoReplacements(B9Base):
    """One defect method per charged R8-001 instance at the
    MOD-10 normaliser: two transposed pairs at any positions
    composed with two replaced letters."""

    def test_nsqezp_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("nsqezp")

    def test_noxxep_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("noxxep")

    def test_sozpex_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("sozpex")

    def test_nszexp_resolves_person_at_mod10(self):
        self.assert_mod10_person_refused("nszexp")

    def test_maxxrrp_resolves_program_at_mod10(self):
        self.assert_mod10_program_promoted("maxxrrp")


class TestR8005TwoPairsOneReplacement(B9Base):
    """One defect method per charged R8-005 instance at the
    MOD-10 normaliser: two transposed pairs and one replaced
    letter, exactly one pair adjacent, standing as itself."""

    def test_nqrosp_stands_as_itself_at_mod10(self):
        self.assert_mod10_itself_promoted("nqrosp")

    def test_nqrosp_cyrillic_twin_stands_as_itself_at_mod10(self):
        actor = "nqr\u043esp"
        self.assertEqual(mod10._normalised_actor(actor), "nqrosp")
        self.assertEqual(
            self.core_promote(actor)["retention_tier"], "Tier 2")


class TestControls(B9Base):
    def test_adjacent_two_pairs_two_replacements_epsrzq(self):
        self.assert_mod10_person_refused("epsrzq")

    def test_adjacent_two_pairs_two_replacements_epqosz(self):
        self.assert_mod10_person_refused("epqosz")

    def test_adjacent_three_pairs_person_epsrno(self):
        self.assert_mod10_person_refused("epsrno")

    def test_adjacent_three_pairs_program_rpgoarm(self):
        self.assert_mod10_program_promoted("rpgoarm")

    def test_two_pairs_pure_program_maogrrp(self):
        self.assert_mod10_program_promoted("maogrrp")

    def test_resolver_only_eprosx_stands_as_itself(self):
        self.assert_mod10_itself_promoted("eprosx")

    def test_resolver_only_epsrox_stands_as_itself(self):
        self.assert_mod10_itself_promoted("epsrox")

    def test_edge_pair_three_replacements_nqzjop(self):
        self.assert_mod10_person_refused("nqzjop")

    def test_adjacent_pair_three_replacements_eprxxx(self):
        self.assert_mod10_person_refused("eprxxx")

    def test_past_form_xpsrxx_stands_as_itself(self):
        self.assert_mod10_itself_promoted("xpsrxx")

    def test_plain_actors_stand_both_ways(self):
        self.assert_mod10_person_refused("person")
        self.assert_mod10_program_promoted("program")
        self.assertEqual(
            self.core_promote("alice")["retention_tier"], "Tier 2")


if __name__ == "__main__":
    unittest.main()

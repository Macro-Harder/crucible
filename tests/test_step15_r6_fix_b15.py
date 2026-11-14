"""Step 15 rerun fix wave 5 completion pins, row R5-001.

Pins for the two transposition composition limb where the
MOD-10 core resolver and the MOD-14 shell resolver disagreed
on the merged tree: six forms built by two disjoint adjacent
transpositions and two x replacements, where the core
promoted and the shell refused, and twelve forms built by
two disjoint adjacent transpositions and one x replacement,
where the two resolver surfaces disagreed in the opposite
direction. Control pins cover the named forms from both
builders papers and generated forms at each bound. Values
are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14


class B15Base(unittest.TestCase):
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

    def assert_both_promote(self, actor):
        self.assertEqual(
            self.core_promote(actor)["retention_tier"], "Tier 2")
        self.assertEqual(
            self.shell_promote(actor)["retention_tier"], "Tier 3")


def _person_test(actor):
    def test(self):
        self.assert_both_refuse_person(actor)
    return test


def _itself_resolver_test(actor):
    def test(self):
        self.assertEqual(mod10._normalised_actor(actor), actor)
        self.assertEqual(mod14._normalise_actor(actor), actor)
        self.assert_both_promote(actor)
    return test


class TestActSplittingForms(B15Base):
    pass


_ACT_SPLITTING = [
    "epsrxx", "epxosx", "epxxno", "xreosx", "xrexno", "xxsrno",
]
for _i, _a in enumerate(_ACT_SPLITTING):
    setattr(TestActSplittingForms, "test_split_%02d" % _i,
            _person_test(_a))


class TestResolverOnlyForms(B15Base):
    pass


_RESOLVER_ONLY = [
    "eprosx", "eprxno", "epsrox", "epsrxn", "epxosn", "epxsno",
    "preosx", "prexno", "pxsrno", "xesrno", "xreosn", "xresno",
]
for _i, _a in enumerate(_RESOLVER_ONLY):
    setattr(TestResolverOnlyForms, "test_resolver_%02d" % _i,
            _itself_resolver_test(_a))


class TestNamedFormControls(B15Base):
    pass


_NAMED_DRESSES = [
    "personxxxxx", "person12345", "xyzson", "xexsxn",
    "prn", "pen", "psn", "pesrno", "eprqoz",
    "personxxxxxx", "xyzzon", "xxxxon", "pn", "epsrno",
    "person",
]
for _i, _a in enumerate(_NAMED_DRESSES):
    setattr(TestNamedFormControls, "test_named_%02d" % _i,
            _person_test(_a))


class TestPromotedControls(B15Base):
    def test_seven_added_letters_refused_at_both_acts(self):
        self.assert_both_refuse_person("personxxxxxxx")

    def test_program_promotes_at_both_acts(self):
        self.assert_both_promote("program")

    def test_alice_promotes_at_both_acts(self):
        self.assert_both_promote("alice")


class TestBoundCompositionControls(B15Base):
    def test_one_transposition_three_replacements(self):
        self.assert_both_refuse_person("eprxxx")

    def test_one_transposition_two_replacements(self):
        self.assert_both_refuse_person("epxxon")

    def test_two_transpositions_plain(self):
        self.assert_both_refuse_person("epsron")

    def test_one_transposition_one_drop(self):
        self.assert_both_refuse_person("epron")

    def test_total_five_composition_agrees_as_itself(self):
        self.assertEqual(mod10._normalised_actor("xpsrxx"), "xpsrxx")
        self.assertEqual(mod14._normalise_actor("xpsrxx"), "xpsrxx")
        self.assert_both_promote("xpsrxx")


if __name__ == "__main__":
    unittest.main()

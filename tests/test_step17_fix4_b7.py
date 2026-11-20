"""Defect tests for FW4-10, the unbounded refusal echo family.

Each defect test hands a hostile value of 5,000 to 100,000
characters, or a 5,000 digit integer, to one named refusal door
and states that the refusal message stands bounded: the whole
handing stands nowhere in the message, the message length
stands under the stated bound of 1,000 characters, and the
ground of the refusal stands readable at the head of the
message. Control tests pin the standing short handings, whose
messages stand unchanged by the cure.
Copyright: J.P. Picard aka Macro-Harder.
"""
import unittest

from crucible import mod01, mod06, mod08, mod09, mod10, mod16

BOUND = 1000
SEPS = None


def _separations():
    from crucible.mod08 import author_sealed_class  # noqa: F401
    import crucible.mod08 as m
    return list(m._SEPARATIONS)


class _EchoCase(unittest.TestCase):
    def assert_bounded(self, exc, head):
        msg = str(exc)
        self.assertLessEqual(len(msg), BOUND, msg[:200])
        self.assertTrue(msg.startswith(head), msg[:200])
        self.assertNotIn("x" * 500, msg)
        self.assertNotIn("A" * 500, msg)
        self.assertNotIn("z" * 500, msg)
        return msg


class TestFW410Mod01(_EchoCase):
    def test_minimal_valid_instance_huge_text_bounded(self):
        with self.assertRaises(ValueError) as cm:
            mod01.minimal_valid_instance("x" * 5000)
        self.assert_bounded(
            cm.exception,
            "minimal_valid_instance stands refused: form identifier ")

    def test_minimal_valid_instance_short_control(self):
        with self.assertRaises(ValueError) as cm:
            mod01.minimal_valid_instance("nope")
        self.assertIn("names no form", str(cm.exception))


class TestFW410Mod06(_EchoCase):
    def test_pause_cap_huge_variant_bounded(self):
        with self.assertRaises(ValueError) as cm:
            mod06.pause_cap("A" * 100000)
        self.assert_bounded(
            cm.exception,
            "the pause cap stands refused in named form for an "
            "unknown variant: ")


class TestFW410Mod08(_EchoCase):
    def _frozen(self):
        sealed = mod08.create_sealed_set()
        mod08.freeze_sealed_set(sealed)
        return sealed

    def test_author_sealed_class_huge_kind_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod08.author_sealed_class(
                self._frozen(), "x" * 100000, "id-1", _separations())
        self.assert_bounded(
            cm.exception,
            "sealed set rejected: authored kind stands unnamed: ")

    def test_author_sealed_class_huge_identifier_bounded(self):
        sealed = self._frozen()
        mod08.author_sealed_class(
            sealed, "sleeper class", "x" * 100000, _separations())
        with self.assertRaises(Exception) as cm:
            mod08.author_sealed_class(
                sealed, "sleeper class", "x" * 100000, _separations())
        self.assert_bounded(
            cm.exception,
            "sealed set rejected: authored identifier stands "
            "already authored: ")


class TestFW410Mod09(_EchoCase):
    def test_bond_search_huge_integer_candidate_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod09.bond_search([10 ** 5000])
        self.assert_bounded(
            cm.exception,
            "bond parameter search rejected: a candidate stands "
            "in no record form: ")

    def test_bond_search_huge_harm_text_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod09.bond_search(
                [{"harm": "x" * 100000, "attacker_cost": 1}])
        self.assert_bounded(
            cm.exception,
            "bond parameter search rejected: a candidate carries "
            "a harm or a cost in no numeric form: ")

    def test_attacker_payoff_huge_text_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod09.attacker_payoff(
                {"in_protocol_payoff": "x" * 100000}, 1)
        self.assert_bounded(
            cm.exception,
            "attacker payoff rejected: the in protocol payoff "
            "stands in no numeric form: ")

    def test_make_strategy_huge_payoff_text_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod09.make_strategy("id-1", in_protocol_payoff="A" * 100000)
        self.assert_bounded(
            cm.exception,
            "make_strategy stands refused: the in protocol payoff "
            "stands in no finite numeric form: ")


class TestFW410Mod10(_EchoCase):
    def test_new_store_huge_kind_bounded(self):
        with self.assertRaises(ValueError) as cm:
            mod10.new_store(store_kind="x" * 100000)
        self.assert_bounded(cm.exception, "unknown store kind: ")

    def test_read_run_record_huge_identifier_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod10.read_run_record("z" * 100000)
        self.assert_bounded(
            cm.exception, "one lookup resolution failure: ")

    def test_new_store_short_kind_control(self):
        with self.assertRaises(ValueError) as cm:
            mod10.new_store(store_kind="nope")
        self.assertIn("unknown store kind: nope", str(cm.exception))


class TestFW410Mod16(_EchoCase):
    def test_fixture_record_huge_identifier_bounded(self):
        with self.assertRaises(Exception) as cm:
            mod16.fixture_record("x" * 5000)
        self.assert_bounded(cm.exception, "'fixture lookup failure: ")

    def test_fixture_record_short_control(self):
        with self.assertRaises(Exception) as cm:
            mod16.fixture_record("F-99")
        self.assertIn("F-99", str(cm.exception))


if __name__ == "__main__":
    unittest.main()

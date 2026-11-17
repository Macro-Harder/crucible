"""Pins for fix wave 22, Builder b1, Group 1.

Row R22-001 of the Round 22 register: the copy family same
text collapse, under settlement S-1, on ruling B. The charged
helpers are crucible/mod07.py _stored_copy, crucible/mod09.py
_stored_copy, and crucible/mod09.py _render_safe_copy, each of
which renders a text key to its plain stored text before
insertion, so two distinct keys storing the one text deliver
one entry, the first silently dropped. The cured pole form is
the MOD-14 form of row R21-002: a carried candidate standing
inserted that drops no carried entry. MOD-12 _freeze stands
in proving scope under the row scope note: the two pins at
that helper stand as this seat proving acts, and the cure
stands charged there only as proved.

Distinguishing pins: 12. Controls: 13. Total: 25.
"""


import unittest

from crucible import mod01, mod05, mod07, mod09, mod12, mod13
from crucible import mod14


class NeverEqualText(str):
    """A text storing one stored text, hashing constantly,
    whose equality answers False against every value."""

    def __hash__(self):
        return 11

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


class HashRaisingText(str):
    """A text hashing constantly and answering False in
    equality while unarmed, whose hash reading raises
    RuntimeError once armed."""

    armed = False

    def __hash__(self):
        if self.armed:
            raise RuntimeError("armed hash reading")

        return 11

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


def never_equal_handing():
    handed = {}
    handed[NeverEqualText("shared-text")] = "entry-one"
    handed[NeverEqualText("shared-text")] = "entry-two"
    return handed


def hash_raising_handing():
    first = HashRaisingText("shared-text")
    second = HashRaisingText("shared-text")
    handed = {}
    handed[first] = "entry-one"
    handed[second] = "entry-two"
    first.armed = True
    second.armed = True
    return handed


def single_key_handing():
    handed = {}
    handed[NeverEqualText("shared-text")] = "entry-one"
    return handed


def plain_handing():
    return {"alpha": 1, "beta": 2}


def carried_values(copied):
    return sorted(list(dict.values(copied)))


class SameTextCase(unittest.TestCase):

    def assert_two_entries(self, copied):
        self.assertEqual(len(copied), 2)
        self.assertEqual(
            carried_values(copied), ["entry-one", "entry-two"])

    def assert_plain_control(self, copied):
        self.assertEqual(copied, {"alpha": 1, "beta": 2})

    def assert_single_control(self, copied):
        self.assertEqual(len(copied), 1)
        self.assertEqual(carried_values(copied), ["entry-one"])
        self.assertEqual(
            list(dict.keys(copied)), ["shared-text"])


class TestMod07StoredCopy(SameTextCase):

    def test_never_equal_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod07._stored_copy(never_equal_handing()))

    def test_hash_raising_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod07._stored_copy(hash_raising_handing()))

    def test_plain_control(self):
        self.assert_plain_control(
            mod07._stored_copy(plain_handing()))

    def test_single_key_control(self):
        self.assert_single_control(
            mod07._stored_copy(single_key_handing()))


class TestMod09StoredCopy(SameTextCase):

    def test_never_equal_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod09._stored_copy(never_equal_handing()))

    def test_hash_raising_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod09._stored_copy(hash_raising_handing()))

    def test_candidate_name_standing_delivers_all_three(self):
        handed = never_equal_handing()
        handed["shared-text (carried key 2)"] = "entry-three"
        copied = mod09._stored_copy(handed)
        self.assertEqual(len(copied), 3)
        self.assertEqual(
            carried_values(copied),
            ["entry-one", "entry-three", "entry-two"])

    def test_plain_control(self):
        self.assert_plain_control(
            mod09._stored_copy(plain_handing()))

    def test_single_key_control(self):
        self.assert_single_control(
            mod09._stored_copy(single_key_handing()))


class TestMod09RenderSafeCopy(SameTextCase):

    def test_never_equal_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod09._render_safe_copy(never_equal_handing()))

    def test_hash_raising_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod09._render_safe_copy(hash_raising_handing()))

    def test_plain_control(self):
        self.assert_plain_control(
            mod09._render_safe_copy(plain_handing()))

    def test_single_key_control(self):
        self.assert_single_control(
            mod09._render_safe_copy(single_key_handing()))


class TestMod12FreezeProving(SameTextCase):

    def test_never_equal_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod12._freeze(never_equal_handing()))

    def test_hash_raising_two_keys_deliver_both(self):
        self.assert_two_entries(
            mod12._freeze(hash_raising_handing()))

    def test_plain_control(self):
        self.assert_plain_control(
            mod12._freeze(plain_handing()))

    def test_single_key_control(self):
        self.assert_single_control(
            mod12._freeze(single_key_handing()))


class TestPublicGates(SameTextCase):

    def test_mod07_make_adapter_choice_approval(self):
        record = mod07.make_adapter_choice(
            "choice-1", "reading-1", "point-1", "text-1",
            "variant-1", approval=never_equal_handing())
        self.assert_two_entries(record["approval"])

    def test_mod09_make_strategy_parameters(self):
        record = mod09.make_strategy(
            "strategy-1", parameters=never_equal_handing())
        self.assert_two_entries(record["parameters"])

    def test_mod09_attacker_cost_summary_classification(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "run-1",
            "attacker_cost": 3,
            "harm": 2,
            "regime_classification": never_equal_handing()})
        self.assert_two_entries(summary["classification_before"])
        self.assert_two_entries(summary["classification_after"])


class TestCuredPoles(SameTextCase):

    def test_mod14_plain_stored_copy_never_equal(self):
        self.assert_two_entries(
            mod14._plain_stored_copy(never_equal_handing()))

    def test_mod14_plain_stored_copy_hash_raising(self):
        self.assert_two_entries(
            mod14._plain_stored_copy(hash_raising_handing()))

    def test_mod01_guarded_copy_never_equal(self):
        self.assert_two_entries(
            mod01._guarded_copy(never_equal_handing()))

    def test_mod05_freeze_never_equal(self):
        self.assert_two_entries(
            mod05._freeze(never_equal_handing()))

    def test_mod13_freeze_never_equal(self):
        self.assert_two_entries(
            mod13._freeze(never_equal_handing()))


if __name__ == "__main__":
    unittest.main()

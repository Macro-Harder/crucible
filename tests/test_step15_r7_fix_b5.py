"""Fix wave 6 pins, MOD-06 only.

Rows pinned: R6-023 (the figure one carrying both of its readings
inside one key), R6-034 (six sister readings standing short in the
fold maps), R6-035 (the y reading of Cyrillic short i), the MOD-06
limb of R6-009 (leet and drop digit readings mixed position by
position), the MOD-06 limb of R6-019 (a walked standing carried
across paths at _payload_carries_barred), and the MOD-06 limb of
R6-038 (the stated 4096 combined generation cap distinguished
from a raised cap).
"""

import time
import unittest

from crucible import mod06


class TestFigureOneCombinedReadings(unittest.TestCase):
    """R6-023: the figure one reads as i at one position and as l
    at another position of the same key."""

    def test_figure_one_options_carry_both_readings(self):
        options = mod06._character_reading_options("1")
        self.assertIn("i", options)
        self.assertIn("l", options)

    def test_profile_with_one_read_as_i_and_as_l(self):
        name = "backup extended prof11e"
        self.assertTrue(mod06._has_combined_reading(name))
        self.assertTrue(
            mod06._key_matches_multi_reading(
                name, "backupextendedprofile"))
        self.assertTrue(mod06._reads_as_excluded_profile(name))

    def test_run_instruction_refuses_profile_as_excluded(self):
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction("backup extended prof11e")

    def test_profile_with_es_and_two_figure_ones(self):
        name = "ba\u0441kup extended prof11e"
        self.assertTrue(mod06._reads_as_excluded_profile(name))
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(name)

    def test_single_figure_one_forms_stand_barred(self):
        for name in (
            "backup extended profi1e",
            "backup extended prof1le",
            "backup extended profile",
        ):
            self.assertTrue(mod06._reads_as_excluded_profile(name))
            with self.assertRaises(mod06.ExcludedSubpath):
                mod06.run_instruction(name)

    def test_clean_controls_stand_admitted(self):
        self.assertFalse(
            mod06._reads_as_excluded_profile("backup extended summary"))
        self.assertFalse(mod06._payload_carries_barred({"summary": 1}))
        delivered = mod06.escrow_result("k", payload={"honest": 1})
        self.assertTrue(mod06.validate_escrow_result(delivered))


class TestSisterReadings(unittest.TestCase):
    """R6-034: the six sister readings recorded to the sister form."""

    def test_options_carry_the_sister_readings(self):
        self.assertIn("k", mod06._character_reading_options("\u043a"))
        ve_options = mod06._character_reading_options("\u0432")
        self.assertIn("b", ve_options)
        self.assertIn("v", ve_options)
        phi_options = mod06._character_reading_options("\u03c6")
        self.assertIn("f", phi_options)
        self.assertIn("ph", phi_options)
        theta_options = mod06._character_reading_options("\u03b8")
        self.assertIn("t", theta_options)
        self.assertIn("th", theta_options)
        self.assertIn("s", mod06._character_reading_options("\u0452"))
        self.assertIn("h", mod06._character_reading_options("\u0493"))

    def test_ka_dressed_profile_stands_barred(self):
        name = "bac\u043aup extended profile"
        self.assertTrue(mod06._reads_as_excluded_profile(name))
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(name)

    def test_ve_dressed_profile_stands_barred(self):
        name = "\u0432ackup extended profile"
        self.assertTrue(mod06._reads_as_excluded_profile(name))
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(name)

    def test_phi_dressed_profile_stands_barred(self):
        name = "backup extended pro\u03c6ile"
        self.assertTrue(mod06._reads_as_excluded_profile(name))
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(name)

    def test_theta_dressed_profile_stands_barred(self):
        name = "backup ex\u03b8ended profile"
        self.assertTrue(mod06._reads_as_excluded_profile(name))
        with self.assertRaises(mod06.ExcludedSubpath):
            mod06.run_instruction(name)

    def test_dje_dressed_anchor_key_stands_barred(self):
        self.assertTrue(
            mod06._payload_carries_barred({"anchor\u0452et": 1}))

    def test_ghe_dressed_anchor_key_stands_barred(self):
        self.assertTrue(
            mod06._payload_carries_barred({"anc\u0493orset": 1}))

    def test_theta_dressed_amount_pair_stands_barred(self):
        payload = {"amoun\u03b8": 1, "currency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_plain_forms_stand_barred(self):
        self.assertTrue(mod06._payload_carries_barred({"anchorset": 1}))
        payload = {"amount": 1, "currency": "USD"}
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_clean_dressed_keys_stand_admitted(self):
        for key in ("bac\u043aup summary", "pro\u03c6ile summary"):
            self.assertFalse(mod06._payload_carries_barred({key: 1}))


class TestShortIReading(unittest.TestCase):
    """R6-035: the fold carries the y reading of Cyrillic short i
    beside its i reading."""

    def test_short_i_options_carry_i_and_y(self):
        character = mod06._fold_characters("\u0439")[0]
        options = mod06._character_reading_options(character)
        self.assertIn("i", options)
        self.assertIn("y", options)

    def test_short_i_money_marker_reads_whole(self):
        self.assertIn(
            "realmoney", mod06._folded_readings("real_mone\u0439"))
        self.assertIn(
            "realmoney", mod06._folded_readings("real_mone\u0419"))

    def test_short_i_money_key_stands_barred(self):
        self.assertTrue(
            mod06._payload_carries_barred({"real_mone\u0439": 1}))
        self.assertTrue(
            mod06._payload_carries_barred({"real_mone\u0419": 1}))
        with self.assertRaises(ValueError):
            mod06.escrow_result(
                "k", payload={"real_mone\u0439": 1})

    def test_plain_cyrillic_i_control_stands_admitted(self):
        self.assertNotIn(
            "realmoney", mod06._folded_readings("real_mone\u0438"))
        self.assertFalse(
            mod06._payload_carries_barred({"real_mone\u0438": 1}))

    def test_plain_money_key_stands_barred(self):
        self.assertTrue(
            mod06._payload_carries_barred({"real_money": 5}))


class TestCombinedDigitReadings(unittest.TestCase):
    """R6-009, MOD-06 limb: the leet reading at one digit position
    and the drop reading at another, in one key."""

    TRIPLE = "4\u043d\u0441hor9set"
    LEET_ONLY = "4\u043d\u0441horset"
    DROP_ONLY = "a\u043d\u0441hor9set"

    def test_triple_key_stands_barred(self):
        self.assertTrue(
            mod06._payload_carries_barred({self.TRIPLE: 1}))

    def test_triple_key_refused_at_public_act(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k", payload={self.TRIPLE: 1})

    def test_one_kind_controls_stand_barred(self):
        for key in (self.LEET_ONLY, self.DROP_ONLY, "anchorset"):
            self.assertTrue(mod06._payload_carries_barred({key: 1}))
            with self.assertRaises(ValueError):
                mod06.escrow_result("k", payload={key: 1})

    def test_clean_key_stands_admitted(self):
        self.assertFalse(mod06._payload_carries_barred({"hello": 1}))
        delivered = mod06.escrow_result("k", payload={"hello": 1})
        self.assertTrue(mod06.validate_escrow_result(delivered))


class TestWalkedStanding(unittest.TestCase):
    """R6-019, MOD-06 limb: _payload_carries_barred carries a
    walked standing across paths, keyed by depth."""

    def test_shared_list_shape_answers_inside_the_bound(self):
        value = "leaf"
        for _ in range(24):
            value = [value, value]
        started = time.monotonic()
        answer = mod06._payload_carries_barred(value)
        elapsed = time.monotonic() - started
        self.assertFalse(answer)
        self.assertLess(elapsed, 20.0)

    def test_shared_dict_shape_answers_inside_the_bound(self):
        value = {"leaf": 1}
        for _ in range(20):
            value = {"a": value, "b": value}
        started = time.monotonic()
        answer = mod06._payload_carries_barred(value)
        elapsed = time.monotonic() - started
        self.assertFalse(answer)
        self.assertLess(elapsed, 20.0)

    def test_deeper_reach_still_judged_at_its_own_depth(self):
        shared = ["clean"]
        deep = shared
        for _ in range(105):
            deep = [deep]
        payload = {"shallow": shared, "deep": deep}
        self.assertTrue(mod06._payload_carries_barred(payload))

    def test_cycle_still_reads_as_barred(self):
        value = []
        value.append(value)
        self.assertTrue(mod06._payload_carries_barred(value))

    def test_shared_barred_container_stands_barred(self):
        barred = [{"anchorset": 1}]
        self.assertTrue(
            mod06._payload_carries_barred([barred, barred]))

    def test_shared_clean_container_stands_admitted(self):
        shared = ["clean"]
        self.assertFalse(
            mod06._payload_carries_barred([shared, shared, shared]))


class TestCombinedGenerationCap(unittest.TestCase):
    """R6-038, MOD-06 limb: the stated 4096 combined generation
    cap stands distinguished from a raised cap. A key of twelve
    two reading characters generates 4096 combined texts and its
    generation completes; a key of thirteen generates 8192 and
    its generation stands abandoned whole at the stated cap, so
    no mixed reading of it stands in the folded readings. Under
    a cap raised to 8192 the thirteen character generation would
    complete and the mixed reading would stand, failing these
    pins."""

    EN = "\u043d"

    def test_generation_completes_at_the_stated_cap(self):
        key = self.EN * 12
        self.assertIn("nh" * 6, mod06._folded_readings(key))

    def test_generation_abandoned_past_the_stated_cap(self):
        key = self.EN * 13
        readings = mod06._folded_readings(key)
        self.assertNotIn("nh" * 6 + "n", readings)
        self.assertLessEqual(len(readings), 32)

    def test_past_cap_key_still_read_by_the_character_check(self):
        key = self.EN * 13 + "anchorset"
        self.assertTrue(mod06._payload_carries_barred({key: 1}))


if __name__ == "__main__":
    unittest.main()

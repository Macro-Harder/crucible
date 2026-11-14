"""Step 15, second run, fix wave 7 pins, Builder 6.

Rows pinned: R7-014, R7-009, and R7-010.

R7-014: construct_farm at MOD-03 judges a non text pair name
through the hash and equality readings the name supplies, and
reads member and edge sets in dict form through the handed
value's own iteration. R7-009: the MOD-03 fold records no
reading for Cyrillic ef, U+0444 and U+0424, or Cyrillic sha,
U+0448 and U+0428. R7-010: Greek upsilon, U+03C5 and U+03A5,
carries only its u reading at MOD-03, MOD-04, and MOD-08, so a
canary dressed with upsilon at its y position escapes at the
three surfaces.

Each charged defect form fails on the uncured modules and
passes on the cured copy; lawful controls pass both ways.
No detection score is reported as a pass or as a fail in this
file: barred readings, farm counts, and delivery standings
only.
"""

import unittest

from crucible import mod03, mod04, mod08

_EF = "\u0444"
_EF_UPPER = "\u0424"
_SHA = "\u0448"
_SHA_UPPER = "\u0428"
_UPSILON = "\u03c5"
_UPSILON_UPPER = "\u03a5"
_CYRILLIC_U = "\u0443"
_THETA_PREFIX = "\u03b8" * 11

SHA_KEY = "member" + _SHA + "ip"
SHA_KEY_UPPER = "member" + _SHA_UPPER + "ip"
EF_KEY = "is" + _EF + "arm"
EF_KEY_UPPER = "is" + _EF_UPPER + "arm"
UPSILON_CANARY = "canar" + _UPSILON
UPSILON_CANARY_UPPER = "canar" + _UPSILON_UPPER


class LyingObjectName:
    """A plain object that is not text and not a member, whose
    hash reading answers as a member text and whose equality
    reading answers True against that text."""

    def __init__(self, answers_as):
        self._answers_as = answers_as

    def __hash__(self):
        return str.__hash__(self._answers_as)

    def __eq__(self, other):
        return str.__eq__(self._answers_as, other)

    def __ne__(self, other):
        return not str.__eq__(self._answers_as, other)


class EmptyIterDict(dict):
    """A dict storing its contents in base dict storage whose
    own iteration yields nothing."""

    def __iter__(self):
        return iter(())


class TestR7014NonTextPairNames(unittest.TestCase):

    def test_dict_edge_lying_object_names_count_no_edge(self):
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": LyingObjectName("a"),
              "vouchee": LyingObjectName("b")}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_tuple_edge_lying_object_names_count_no_edge(self):
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [(LyingObjectName("a"), LyingObjectName("b"))])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_lying_object_names_for_second_farm_count_no_edge(self):
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": LyingObjectName("c"),
              "vouchee": LyingObjectName("d")}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_one_lying_object_name_counts_no_edge(self):
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": LyingObjectName("a"), "vouchee": "a"}])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_plain_controls_stand(self):
        internal = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": "a", "vouchee": "b"}])
        self.assertEqual(
            internal["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})
        cross = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": "a", "vouchee": "c"}])
        self.assertEqual(
            cross["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})
        non_member = mod03.construct_farm(
            ["a", "b", "c", "d"], 2,
            [{"voucher": "zzz", "vouchee": "yyy"}])
        self.assertEqual(
            non_member["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})

    def test_same_plain_object_member_and_pair_counts(self):
        member = object()
        result = mod03.construct_farm(
            [member, "b"], 1, [(member, member)])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_plain_scalar_names_still_count(self):
        result = mod03.construct_farm([1, 2], 1, [(1, 1)])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})


class TestR7014DictFormSets(unittest.TestCase):

    def test_dict_form_member_set_with_empty_iteration_builds(self):
        members = EmptyIterDict(
            {"a": 1, "b": 1, "c": 1, "d": 1})
        result = mod03.construct_farm(members, 2, [("a", "b")])
        self.assertEqual(
            [farm["farm_id"] for farm in result["farms"]],
            ["farm-0", "farm-1"])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_dict_form_edge_set_with_empty_iteration_counts(self):
        edges = EmptyIterDict({("a", "b"): 1})
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2, edges)
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})

    def test_dict_form_member_set_no_farm_size_branch(self):
        members = EmptyIterDict({"a": 1, "b": 1})
        result = mod03.construct_farm(members, None, [("a", "b")])
        self.assertEqual(result["farms"], [])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"], {})

    def test_plain_dict_form_controls_stand(self):
        members = {"a": 1, "b": 1, "c": 1, "d": 1}
        result = mod03.construct_farm(members, 2, [("a", "b")])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})
        edges = {("a", "b"): 1}
        result = mod03.construct_farm(
            ["a", "b", "c", "d"], 2, edges)
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1, "farm-1": 0})


class TestR7009EfAndShaAtMod03(unittest.TestCase):

    def test_sha_dressed_membership_is_barred(self):
        for key in (SHA_KEY, SHA_KEY_UPPER):
            with self.subTest(key=key):
                self.assertTrue(mod03._is_barred_key(key))
                self.assertTrue(mod03._combined_key_barred(key))

    def test_ef_dressed_isfarm_is_barred(self):
        for key in (EF_KEY, EF_KEY_UPPER):
            with self.subTest(key=key):
                self.assertTrue(mod03._is_barred_key(key))
                self.assertTrue(mod03._combined_key_barred(key))

    def test_dressed_keys_found_at_the_public_act(self):
        for key in (SHA_KEY, SHA_KEY_UPPER, EF_KEY, EF_KEY_UPPER):
            with self.subTest(key=key):
                self.assertTrue(
                    mod03.record_carries_ground_truth({key: 1}))

    def test_dressed_keys_past_the_bound_are_barred(self):
        # The past bound standing stands charged on the sha limb,
        # whose barred form is a carried part. The ef limb spells
        # an exact name, and an exact name carrying a prefix
        # stands as a different name, so no past bound form of
        # the ef limb stands pinned here.
        dressed = _THETA_PREFIX + SHA_KEY
        self.assertTrue(mod03._is_barred_key(dressed))
        self.assertTrue(mod03._combined_key_barred(dressed))

    def test_controls_stand(self):
        self.assertTrue(mod03._is_barred_key("membership"))
        self.assertTrue(mod03._is_barred_key("isfarm"))
        self.assertTrue(
            mod03.record_carries_ground_truth({"membership": 1}))
        clean = "zzzz" + _SHA + "ip"
        self.assertFalse(mod03._is_barred_key(clean))
        self.assertFalse(
            mod03.record_carries_ground_truth({clean: 1}))
        self.assertFalse(mod03._is_barred_key("activity"))


class TestR7010UpsilonYReading(unittest.TestCase):

    SURFACES = (mod03, mod04, mod08)

    def test_upsilon_canary_is_barred_at_each_surface(self):
        for module in self.SURFACES:
            for key in (UPSILON_CANARY, UPSILON_CANARY_UPPER):
                with self.subTest(module=module.__name__, key=key):
                    self.assertTrue(module._is_barred_key(key))
                    self.assertTrue(module._combined_key_barred(key))

    def test_upsilon_canary_past_the_bound_is_barred(self):
        for module in self.SURFACES:
            dressed = _THETA_PREFIX + UPSILON_CANARY
            with self.subTest(module=module.__name__):
                self.assertTrue(module._is_barred_key(dressed))
                self.assertTrue(module._combined_key_barred(dressed))

    def test_public_acts_at_each_surface(self):
        self.assertTrue(mod03.record_carries_ground_truth(
            {UPSILON_CANARY: 1}))
        self.assertTrue(mod04.view_record_carries_barred_field(
            {"feature_values": {UPSILON_CANARY: 1}}))
        record = {
            "agent_identifier": "agent-b6",
            "day": 2,
            "feature_values": {"activity": 3},
            "records_for_agent_and_day": [
                {"wrap": {UPSILON_CANARY: 1}}],
        }
        with self.assertRaises(mod08.NamedDetectionFailure):
            mod08.accept_detection_input(record)

    def test_u_reading_of_upsilon_still_stands(self):
        key = "groundtr" + _UPSILON + "th"
        for module in self.SURFACES:
            with self.subTest(module=module.__name__):
                self.assertTrue(module._is_barred_key(key))

    def test_controls_stand_at_each_surface(self):
        for module in self.SURFACES:
            with self.subTest(module=module.__name__):
                self.assertTrue(module._is_barred_key("canary"))
                self.assertTrue(module._is_barred_key(
                    "canar" + _CYRILLIC_U))
                self.assertFalse(module._is_barred_key(
                    "activit" + _UPSILON))
                self.assertFalse(module._is_barred_key(
                    _THETA_PREFIX + "activit" + _UPSILON))


if __name__ == "__main__":
    unittest.main()

"""Step 15 rerun round 4 fix wave 4 tests, builder b7.

Items pinned: R4-002, R4-003, R4-004, R4-005, R4-028
(MOD-14 limb only), R4-029, R4-030 limb b only, R4-036.
All pins stand against crucible/mod14.py only.
"""
import unittest

import crucible.mod14 as mod14


def _list_chain(depth, leaf="leaf"):
    value = leaf
    for _ in range(depth):
        value = [value]
    return value


def _tuple_chain(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


def _frozenset_chain(depth, leaf):
    value = leaf
    for _ in range(depth):
        value = frozenset((value,))
    return value


def _walk_list(value):
    depth = 0
    while isinstance(value, list):
        value = value[0]
        depth += 1
    return depth, value


class _ActorCase(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["condition a"]}

    def _inputs(self):
        return {"flag_conditions_fired": ["condition a"]}

    def _refused_flag(self, actor):
        record = self._record()
        with self.assertRaises(Exception, msg=actor):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3", actor=actor)
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def _refused_run_command(self, actor):
        record = self._record()
        result = mod14.run_command("flag_evaluation", {
            "summary_record": record,
            "inputs": self._inputs(),
            "outcome": "promote", "tier": "Tier 3", "actor": actor})
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("swallowed"), result)
        self.assertIn("person", str(result.get("failure")), result)
        self.assertEqual(record.get("retention_tier"), "Tier 1")


class _BarredCase(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def _allowed(self, action):
        self.assertTrue(mod14.validate_operator_action(action), action)


class TestR4002FiveAddedLetters(_BarredCase):
    def test_sealed_five_added_edit_and_delete(self):
        self._barred({"kind": "edit",
                      "target": "sealedxxxxx family record"})
        self._barred({"kind": "delete",
                      "target": "sealedxxxxx family record"})

    def test_closed_five_added_edit_and_delete_on_flag_path(self):
        self._barred({"kind": "edit",
                      "target": "closedxxxxx run record"})
        self._barred({"kind": "delete",
                      "target": "closedxxxxx run record",
                      "path": "flag rule"})

    def test_checkpoint_five_added_edit_and_delete(self):
        self._barred({"kind": "edit",
                      "target": "checkpointxxxxx set",
                      "path": "flag rule"})
        self._barred({"kind": "delete",
                      "target": "checkpointxxxxx set"})

    def test_family_five_added_on_middle_word(self):
        self._barred({"kind": "edit",
                      "target": "sealed familyxxxxx record"})
        self._barred({"kind": "delete",
                      "target": "sealed familyxxxxx record"})

    def test_five_added_reason_form(self):
        result = mod14.validate_operator_action_with_reason(
            {"kind": "delete", "target": "sealedxxxxx family record"})
        self.assertFalse(result["allowed"], result)

    def test_final_word_dress_boundary_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sealed family recordxxxxx"})

    def test_read_control_still_allowed(self):
        self._allowed({"kind": "read",
                       "target": "sealedxxxxx family record"})

    def test_four_added_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sealedxxxx family record"})


class TestR4003ThreeCompoundedChanges(_BarredCase):
    def test_three_replacements_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "sexxyd family record"})
        self._barred({"kind": "delete",
                      "target": "sexxyd family record"})

    def test_three_replacements_on_closed(self):
        self._barred({"kind": "edit",
                      "target": "clxxxd run record"})
        self._barred({"kind": "delete",
                      "target": "clxxxd run record",
                      "path": "flag rule"})

    def test_three_replacements_on_checkpoint(self):
        self._barred({"kind": "delete",
                      "target": "chxxxpoint set"})

    def test_three_drops_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "sel family record"})
        self._barred({"kind": "delete",
                      "target": "sel family record"})

    def test_three_drops_on_closed(self):
        self._barred({"kind": "edit",
                      "target": "cld run record"})
        self._barred({"kind": "delete",
                      "target": "cld run record",
                      "path": "flag rule"})

    def test_three_drops_on_checkpoint(self):
        self._barred({"kind": "delete",
                      "target": "chkpint set"})

    def test_two_transpositions_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "saelde family record"})
        self._barred({"kind": "delete",
                      "target": "saelde family record"})

    def test_two_transpositions_on_closed(self):
        self._barred({"kind": "edit",
                      "target": "colesd run record"})
        self._barred({"kind": "delete",
                      "target": "colesd run record",
                      "path": "flag rule"})

    def test_transposition_with_two_replacements_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "saexey family record"})
        self._barred({"kind": "delete",
                      "target": "saexey family record"})

    def test_transposition_with_two_replacements_on_closed(self):
        self._barred({"kind": "edit",
                      "target": "colsxy run record"})

    def test_two_change_controls_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "soalod family record"})
        self._barred({"kind": "edit",
                      "target": "sead family record"})

    def test_read_control_still_allowed(self):
        self._allowed({"kind": "read",
                       "target": "sexxyd family record"})


class TestR4004ArticleInsideSplitWord(_BarredCase):
    def test_sea_a_led(self):
        self._barred({"kind": "edit",
                      "target": "sea a led family record"})
        self._barred({"kind": "delete",
                      "target": "sea a led family record"})

    def test_sea_the_led(self):
        self._barred({"kind": "edit",
                      "target": "sea the led family record"})
        self._barred({"kind": "delete",
                      "target": "sea the led family record"})

    def test_seal_the_ed(self):
        self._barred({"kind": "edit",
                      "target": "seal the ed family record"})
        self._barred({"kind": "delete",
                      "target": "seal the ed family record"})

    def test_clo_a_sed(self):
        self._barred({"kind": "edit",
                      "target": "clo a sed run record"})
        self._barred({"kind": "delete",
                      "target": "clo a sed run record",
                      "path": "flag rule"})

    def test_clo_the_sed(self):
        self._barred({"kind": "edit",
                      "target": "clo the sed run record"})

    def test_check_a_point_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "check a point set"})
        self._barred({"kind": "edit",
                      "target": "check a point set",
                      "path": "flag rule"})

    def test_split_controls_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sea led family record"})
        self._barred({"kind": "edit",
                      "target": "check point set"})

    def test_read_control_still_allowed(self):
        self._allowed({"kind": "read",
                       "target": "sea a led family record"})

    def test_unrelated_target_with_article_still_allowed(self):
        self._allowed({"kind": "edit",
                       "target": "sea a led summary sheet"})


class TestR4005FlagActorPastBounds(_ActorCase):
    def test_person_five_added_flag(self):
        self._refused_flag("personxxxxx")

    def test_person_five_added_run_command(self):
        self._refused_run_command("personxxxxx")

    def test_person_three_replacements_flag(self):
        self._refused_flag("xyzson")

    def test_person_three_replacements_run_command(self):
        self._refused_run_command("xyzson")

    def test_person_three_drops_prn_flag(self):
        self._refused_flag("prn")

    def test_person_three_drops_prn_run_command(self):
        self._refused_run_command("prn")

    def test_person_transposition_two_replacements_flag(self):
        self._refused_flag("eprxun")

    def test_person_transposition_two_replacements_run_command(self):
        self._refused_run_command("eprxun")

    def test_person_three_drops_pen_flag(self):
        self._refused_flag("pen")

    def test_person_three_drops_pen_run_command(self):
        self._refused_run_command("pen")

    def test_person_pxrsxx_flag(self):
        self._refused_flag("pxrsxx")

    def test_person_pxrsxx_run_command(self):
        self._refused_run_command("pxrsxx")

    def test_person_two_transpositions_flag(self):
        self._refused_flag("pesrno")

    def test_lawful_program_actor_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")

    def test_cured_bound_actor_controls_still_refused(self):
        self._refused_flag("personxxxx")
        self._refused_flag("parsun")
        self._refused_flag("pern")


class TestR4028InvisibleFormatCondition(unittest.TestCase):
    _CHARS = ("\u00ad", "\u180e", "\u200e", "\u200f", "\u061c",
              "\u202a", "\u202e", "\u2061", "\u2064")

    def _record(self):
        return {"retention_tier": "Tier 1"}

    def _refused_inputs(self, fired):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                self._record(),
                inputs={"flag_conditions_fired": fired},
                outcome="promote", tier="Tier 3", actor="program")

    def test_each_invisible_char_states_no_condition(self):
        for char in self._CHARS:
            with self.subTest(char=hex(ord(char))):
                self._refused_inputs([char])

    def test_invisible_chars_through_the_record(self):
        for char in self._CHARS:
            with self.subTest(char=hex(ord(char))):
                record = {"retention_tier": "Tier 1",
                          "flag_conditions_fired": [char]}
                with self.assertRaises(mod14.NamedShellFailure):
                    mod14.flag_evaluation(
                        record, inputs={},
                        outcome="promote", tier="Tier 3",
                        actor="program")

    def test_invisible_chars_in_bare_string_form(self):
        for char in self._CHARS:
            with self.subTest(char=hex(ord(char))):
                self._refused_inputs(char)

    def test_invisible_char_mixed_with_spaces_only(self):
        self._refused_inputs([" \u00ad \u202e "])

    def test_cured_zero_width_controls_still_refused(self):
        self._refused_inputs(["\u200b"])
        self._refused_inputs(["\ufeff"])

    def test_stated_condition_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")

    def test_condition_with_invisible_char_beside_text_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["\u00adcondition a"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR4029LawfulRulePathPastBounds(_BarredCase):
    def test_flag_path_five_added_letters_allowed(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flagxxxxx rule"})

    def test_flag_path_three_drops_allowed(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "f rule"})

    def test_deletion_path_five_added_letters_allowed(self):
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletionxxxxx rule"})

    def test_plain_and_cured_path_controls_still_allowed(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flag rule"})
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flagxxxx rule"})
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "fg rule"})
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletion rule"})

    def test_wrong_path_with_extended_dress_still_barred(self):
        self._barred({"kind": "edit", "target": "closed run record",
                      "path": "deletionxxxxx rule"})
        self._barred({"kind": "edit", "target": "checkpoint set",
                      "path": "flagxxxxx rule"})

    def test_no_barred_act_admitted_by_extended_path(self):
        self._barred({"kind": "delete", "target": "closed run record",
                      "path": "flagxxxxx rule"})
        self._barred({"kind": "edit", "target": "sealed family record",
                      "path": "flagxxxxx rule"})
        self._barred({"kind": "delete", "target": "checkpoint set",
                      "path": "f rule"})


class TestR4030FreezeScalarLeafBasis(unittest.TestCase):
    def test_list_chain_101_leaf_preserved_by_freeze(self):
        depth, leaf = _walk_list(mod14._freeze(_list_chain(101)))
        self.assertEqual(depth, 101)
        self.assertEqual(leaf, "leaf")

    def test_list_chain_101_leaf_preserved_through_error_carriage(self):
        failure = mod14.NamedShellFailure("deep carried value")
        failure.deep_value = _list_chain(101)
        carriage = mod14.error_carriage(failure)
        depth, leaf = _walk_list(
            carriage["failure_value"]["deep_value"])
        self.assertEqual(depth, 101)
        self.assertEqual(leaf, "leaf")

    def test_list_chain_101_leaf_preserved_through_pilot_run(self):
        output = mod14.pilot_run(
            "timing", {"figure": _list_chain(100)})
        depth, leaf = _walk_list(output["figure"])
        self.assertEqual(depth, 100)
        self.assertEqual(leaf, "leaf")

    def test_list_chain_102_leaf_control_still_marked(self):
        depth, leaf = _walk_list(mod14._freeze(_list_chain(102)))
        self.assertEqual(depth, 101)
        self.assertEqual(leaf, mod14._FREEZE_TOO_DEEP)

    def test_list_chain_100_control_still_preserved(self):
        depth, leaf = _walk_list(mod14._freeze(_list_chain(100)))
        self.assertEqual(depth, 100)
        self.assertEqual(leaf, "leaf")


class TestR4036CarriageKeyCollision(unittest.TestCase):
    def _payload(self, depth, chain):
        return {chain(depth, "a"): "va", chain(depth, "b"): "vb",
                "v1": "one", "other": "x"}

    def _carriage_payload(self, depth, chain):
        failure = mod14.NamedShellFailure("carried entries")
        failure.payload = self._payload(depth, chain)
        carriage = mod14.error_carriage(failure)
        return carriage["failure_value"]["payload"]

    def test_tuple_keys_at_100_all_entries_present(self):
        carried = self._carriage_payload(100, _tuple_chain)
        self.assertEqual(len(carried), 4, carried)
        self.assertIn("one", carried.values())
        self.assertIn("va", carried.values())
        self.assertIn("vb", carried.values())

    def test_tuple_keys_at_101_all_entries_present(self):
        carried = self._carriage_payload(101, _tuple_chain)
        self.assertEqual(len(carried), 4, carried)
        self.assertIn("va", carried.values())
        self.assertIn("vb", carried.values())

    def test_tuple_keys_at_150_all_entries_present(self):
        carried = self._carriage_payload(150, _tuple_chain)
        self.assertEqual(len(carried), 4, carried)
        self.assertIn("va", carried.values())
        self.assertIn("vb", carried.values())

    def test_frozenset_keys_at_101_all_entries_present(self):
        carried = self._carriage_payload(101, _frozenset_chain)
        self.assertEqual(len(carried), 4, carried)
        self.assertIn("va", carried.values())
        self.assertIn("vb", carried.values())

    def test_frozenset_keys_at_150_all_entries_present(self):
        carried = self._carriage_payload(150, _frozenset_chain)
        self.assertEqual(len(carried), 4, carried)
        self.assertIn("va", carried.values())
        self.assertIn("vb", carried.values())

    def test_tuple_keys_shallow_controls_all_present(self):
        for depth in (90, 99):
            carried = self._carriage_payload(depth, _tuple_chain)
            self.assertEqual(len(carried), 4, (depth, carried))

    def test_freeze_direct_tuple_keys_at_101_all_present(self):
        carried = mod14._freeze(self._payload(101, _tuple_chain))
        self.assertEqual(len(carried), 4, carried)

    def test_populated_carriage_form_control_stands(self):
        failure = mod14.NamedShellFailure("plain failure")
        carriage = mod14.error_carriage(failure)
        self.assertFalse(carriage["swallowed"])
        self.assertTrue(carriage["operator_sees_failure"])
        self.assertEqual(
            carriage["failure_value"].get("name"), "NamedShellFailure")

    def test_no_bare_recursion_error_on_deep_dict_chain(self):
        failure = mod14.NamedShellFailure("deep carried value")
        value = "leaf"
        for _ in range(500):
            value = {"x": value}
        failure.deep_value = value
        carriage = mod14.error_carriage(failure)
        self.assertIn("deep_value", carriage["failure_value"])


if __name__ == "__main__":
    unittest.main()

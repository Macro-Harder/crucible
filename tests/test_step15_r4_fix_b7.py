"""Step 15 rerun round 3 fix wave 3 tests, builder b7.

Items pinned: R3-004, R3-005, R3-006, R3-007, R3-042,
R3-050, R3-052 (MOD-14 limb), R3-053.

The R3-053 pins are written against the register statement
for that item: they state the standing the path reading must
reach once the resolver cures for R3-005 to R3-007 land, and
they were run on the unmodified copy in that form, with
their pre cure standing recorded in the open in the builder
paper for this wave.
"""
import unittest

import crucible.mod10 as mod10
import crucible.mod14 as mod14
import crucible.mod16 as mod16


def _dict_chain(depth):
    value = "leaf"
    for _ in range(depth):
        value = {"x": value}
    return value


def _frozenset_chain(depth):
    value = 1
    for _ in range(depth):
        value = frozenset((value,))
    return value


def _tuple_chain(depth):
    value = 1
    for _ in range(depth):
        value = (value,)
    return value


class TestR3004ActorDressesPastCuredForms(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["condition a"]}

    def _inputs(self):
        return {"flag_conditions_fired": ["condition a"]}

    def _refused(self, actor):
        record = self._record()
        with self.assertRaises(Exception, msg=actor):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3", actor=actor)
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_actor_four_added_letters(self):
        self._refused("personxxxx")

    def test_actor_two_replacements(self):
        self._refused("parsun")

    def test_actor_two_drops(self):
        self._refused("pern")

    def test_actor_split_with_two_inserted_articles(self):
        self._refused("per the the son")

    def test_actor_split_by_separators_with_two_inserted_articles(self):
        self._refused("per-the-the-son")

    def test_program_actor_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR3005FourAddedLetters(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_four_added_on_first_word(self):
        self._barred({"kind": "edit",
                      "target": "sealedxxxx family record"})
        self._barred({"kind": "delete",
                      "target": "sealedxxxx family record"})

    def test_four_added_on_middle_word(self):
        self._barred({"kind": "edit",
                      "target": "sealed familyxxxx record"})
        self._barred({"kind": "edit",
                      "target": "closed runxxxx record"})

    def test_four_added_on_closed_first_word(self):
        self._barred({"kind": "delete",
                      "target": "closedxxxx run record",
                      "path": "flag rule"})
        self._barred({"kind": "edit",
                      "target": "closedxxxx run record"})

    def test_four_added_on_checkpoint_word(self):
        self._barred({"kind": "edit",
                      "target": "checkpointxxxx set",
                      "path": "flag rule"})
        self._barred({"kind": "delete",
                      "target": "checkpointxxxx set"})

    def test_four_added_reason_form(self):
        result = mod14.validate_operator_action_with_reason(
            {"kind": "delete", "target": "sealedxxxx family record"})
        self.assertFalse(result["allowed"], result)

    def test_trailing_dress_on_final_word_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sealed family recordxxxx"})

    def test_read_control_still_allowed(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "sealedxxxx family record"}))


class TestR3006TwoChangeCompounds(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_two_replacements_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "soalod family record"})
        self._barred({"kind": "delete",
                      "target": "soalod family record"})

    def test_two_replacements_on_closed(self):
        self._barred({"kind": "delete",
                      "target": "clozod run record",
                      "path": "flag rule"})
        self._barred({"kind": "edit",
                      "target": "clozod run record"})

    def test_two_replacements_on_checkpoint_word(self):
        self._barred({"kind": "delete",
                      "target": "chackpoont set"})

    def test_two_drops_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "sead family record"})
        self._barred({"kind": "delete",
                      "target": "sead family record"})

    def test_two_drops_on_closed(self):
        self._barred({"kind": "delete",
                      "target": "clsd run record",
                      "path": "flag rule"})

    def test_two_drops_on_middle_word(self):
        self._barred({"kind": "edit",
                      "target": "sealed famy record"})

    def test_transposition_with_replacement_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "saexed family record"})

    def test_transposition_with_replacement_on_run_word(self):
        self._barred({"kind": "delete",
                      "target": "closed urx record",
                      "path": "flag rule"})


class TestR3007SeparatorSplitsInsideOneWord(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_split_fragment_resolving_elsewhere(self):
        self._barred({"kind": "edit",
                      "target": "sea led family record"})
        self._barred({"kind": "delete",
                      "target": "sea led family record"})

    def test_hyphen_split_parts_across_target(self):
        self._barred({"kind": "edit",
                      "target": "seal-ed fam-ily rec-ord"})

    def test_letter_split_with_article_letter_inside_word(self):
        self._barred({"kind": "edit",
                      "target": "s e a l e d family record"})

    def test_split_run_word_with_resolving_fragment(self):
        self._barred({"kind": "edit",
                      "target": "closed r un record"})

    def test_split_final_word_fragments_resolving_elsewhere(self):
        self._barred({"kind": "edit",
                      "target": "sealed family rec ord"})

    def test_split_controls_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sealed.family.record"})
        self._barred({"kind": "edit",
                      "target": "check point set"})
        self._barred({"kind": "edit",
                      "target": "che ckpoint set"})


class TestR3042ErrorCarriageCopyBound(unittest.TestCase):
    def test_run_command_deep_lookup_identifier_returns_carriage(self):
        result = mod14.run_command(
            "read_store", {"run_id": _dict_chain(500)})
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("failure_value"), result)
        self.assertEqual(
            result["failure_value"].get("name"),
            "one lookup resolution failure")
        self.assertEqual(result["failure_value"].get("run_status"),
                         "failed")
        self.assertEqual(result["failure_value"].get("complete"),
                         False)
        self.assertIn("run_identifier", result["failure_value"])
        self.assertFalse(result.get("swallowed"))

    def test_error_carriage_on_deep_lookup_failure(self):
        failure = mod10.LookupFailure(_dict_chain(500))
        carriage = mod14.error_carriage(failure)
        self.assertTrue(carriage["failure_value"], carriage)
        self.assertIn("run_identifier", carriage["failure_value"])

    def test_error_carriage_on_deep_fixture_lookup_failure(self):
        failure = mod16.FixtureLookupFailure(_dict_chain(500))
        carriage = mod14.error_carriage(failure)
        self.assertTrue(carriage["failure_value"], carriage)

    def test_error_carriage_on_deep_carried_attribute(self):
        failure = mod14.NamedShellFailure("deep carried value")
        failure.deep_value = _dict_chain(500)
        carriage = mod14.error_carriage(failure)
        self.assertTrue(carriage["failure_value"], carriage)
        self.assertIn("deep_value", carriage["failure_value"])
        self.assertEqual(
            carriage["failure_value"].get("name"),
            "NamedShellFailure")

    def test_cyclic_identifier_control_still_carried(self):
        cyclic = {}
        cyclic["self"] = cyclic
        result = mod14.run_command("read_store", {"run_id": cyclic})
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("failure_value"), result)

    def test_plain_identifier_control_still_carried(self):
        result = mod14.run_command("read_store", {"run_id": "missing-1"})
        self.assertEqual(
            result["failure_value"].get("name"),
            "one lookup resolution failure")


class TestR3050PilotArtefactKeyDepth(unittest.TestCase):
    def test_frozenset_chain_key_past_bound_refused(self):
        artefact = {"figure": 1, _frozenset_chain(150): "x"}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_tuple_chain_key_past_bound_refused(self):
        artefact = {"figure": 1, _tuple_chain(150): "x"}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_frozenset_chain_key_at_depth_2000_refused_in_named_form(self):
        artefact = {"figure": 1, _frozenset_chain(2000): "x"}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_nested_dict_key_past_bound_refused(self):
        artefact = {"outer": {_frozenset_chain(150): "x"}}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_value_position_control_still_refused(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"outer": _dict_chain(150)})

    def test_shallow_key_control_still_runs(self):
        output = mod14.pilot_run(
            "timing", {"figure": 1, _frozenset_chain(10): "x"})
        self.assertEqual(output["confinement_label"], "pilot confined")


class TestR3052ZeroWidthStatedCondition(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1"}

    def _refused(self, fired, record=None):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record if record is not None else self._record(),
                inputs={"flag_conditions_fired": fired},
                outcome="promote", tier="Tier 3", actor="program")

    def test_zero_width_space_only_entry(self):
        self._refused(["\u200b"])

    def test_zero_width_joiner_only_entry(self):
        self._refused(["\u200d"])

    def test_byte_order_mark_only_entry(self):
        self._refused(["\ufeff"])

    def test_zero_width_only_entry_through_the_record(self):
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": ["\u200b"]}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record, inputs={},
                outcome="promote", tier="Tier 3", actor="program")

    def test_single_string_zero_width_fired_value(self):
        self._refused("\u200b")

    def test_zero_width_mixed_with_spaces_only(self):
        self._refused([" \u200b \ufeff "])

    def test_stated_condition_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR3053LawfulRulePathDresses(unittest.TestCase):
    def _allowed(self, action):
        self.assertTrue(mod14.validate_operator_action(action), action)

    def test_path_word_four_added_letters(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flagxxxx rule"})

    def test_path_word_two_drops(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "fg rule"})

    def test_path_word_separator_split_inside_word(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flag ru le"})

    def test_deletion_path_word_four_added_letters(self):
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletionxxxx rule"})

    def test_plain_path_control_still_allowed(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flag rule"})
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletion rule"})

    def test_wrong_path_control_still_barred(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed run record",
             "path": "deletionxxxx rule"}))


if __name__ == "__main__":
    unittest.main()

"""Step 15 rerun, fix wave 5 pins, MOD-14 rows.

Rows pinned: R5-002, R5-003, R5-004, R5-005 (MOD-14 limb),
R5-008 (MOD-14 limb), R5-027, R5-030, R5-033 (MOD-14 limb),
R5-038.
"""
import unittest

import crucible.mod14 as mod14


def _tuple_chain(leaf, depth):
    value = leaf
    for _ in range(depth):
        value = (value,)
    return value


class _EvilFrozenset(frozenset):
    """A frozenset subclass whose constructor returns a barred
    dict where its items argument stands in list form, and
    behaves as a plain frozenset otherwise. Instances built
    from a tuple are genuine frozenset instances."""

    def __new__(cls, items=()):
        if isinstance(items, list):
            return {"real_money": "materialised"}
        return super().__new__(cls, items)


class _EvilSet(set):
    """The set form of _EvilFrozenset."""

    def __new__(cls, items=()):
        if isinstance(items, list):
            return {"real_money": "materialised"}
        return super().__new__(cls, items)


class _IterLyingSet(set):
    def __iter__(self):
        return iter(("a", "barred_extra"))


class _IterLyingFrozenset(frozenset):
    def __iter__(self):
        return iter(("a", "barred_extra"))


class _SubstitutedItemsDict(dict):
    def items(self):
        return iter((("substituted_entry", "x"),))


class _EmptyItemsDict(dict):
    def items(self):
        return iter(())


def _stored_dict(cls, entries):
    instance = cls()
    for key, value in entries.items():
        dict.__setitem__(instance, key, value)
    return instance


class TestR5002SixAddedLetters(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_six_added_on_first_word(self):
        self._barred({"kind": "edit",
                      "target": "sealedxxxxxx family record"})
        self._barred({"kind": "delete",
                      "target": "sealedxxxxxx family record"})

    def test_six_added_on_middle_word(self):
        self._barred({"kind": "edit",
                      "target": "sealed familyxxxxxx record"})
        self._barred({"kind": "edit",
                      "target": "closed runxxxxxx record"})

    def test_six_added_on_checkpoint_word(self):
        self._barred({"kind": "edit",
                      "target": "checkpointxxxxxx set",
                      "path": "flag rule"})
        self._barred({"kind": "delete",
                      "target": "checkpointxxxxxx set"})

    def test_five_added_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sealedxxxxx family record"})

    def test_read_control_still_allowed(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "sealedxxxxxx family record"}))

    def test_plain_control_still_barred(self):
        self._barred({"kind": "edit", "target": "sealed family record"})


class TestR5003FourCompoundedChanges(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_four_replacements_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "xyzqed family record"})
        self._barred({"kind": "delete",
                      "target": "xyzqed family record"})

    def test_four_replacements_on_checkpoint(self):
        self._barred({"kind": "delete",
                      "target": "xyzzkpoint set"})

    def test_four_drops_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "sd family record"})
        self._barred({"kind": "delete",
                      "target": "sd family record"})

    def test_four_drops_on_record_word(self):
        self._barred({"kind": "edit",
                      "target": "sealed family rc"})

    def test_four_drops_on_checkpoint(self):
        self._barred({"kind": "edit",
                      "target": "ceoint set",
                      "path": "flag rule"})

    def test_three_transpositions_on_sealed(self):
        self._barred({"kind": "edit",
                      "target": "eslade family record"})
        self._barred({"kind": "delete",
                      "target": "eslade family record"})

    def test_three_transpositions_on_closed(self):
        self._barred({"kind": "delete",
                      "target": "lcsode run record",
                      "path": "flag rule"})

    def test_transposition_with_three_replacements(self):
        self._barred({"kind": "edit",
                      "target": "esxyzd family record"})

    def test_two_transpositions_with_two_replacements(self):
        self._barred({"kind": "edit",
                      "target": "eslaxx family record"})

    def test_three_replacements_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sxyzed family record"})

    def test_two_drops_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sead family record"})


class TestR5004PartitionSplitForms(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_split_fragment_carrying_added_letter(self):
        self._barred({"kind": "edit",
                      "target": "sea ledd family record"})
        self._barred({"kind": "delete",
                      "target": "sea ledd family record"})

    def test_split_fragment_carrying_added_letter_second_form(self):
        self._barred({"kind": "edit",
                      "target": "seal edd family record"})

    def test_split_with_article_and_fragment_dress(self):
        self._barred({"kind": "edit",
                      "target": "sea the ledd family record"})

    def test_split_into_nine_fragments(self):
        self._barred({"kind": "edit",
                      "target": "c h e c k p o i nt set"})

    def test_split_into_ten_fragments(self):
        self._barred({"kind": "edit",
                      "target": "c h e c k p o i n t set"})
        self._barred({"kind": "delete",
                      "target": "c h e c k p o i n t set"})

    def test_exact_split_control_still_barred(self):
        self._barred({"kind": "edit",
                      "target": "sea led family record"})
        self._barred({"kind": "edit",
                      "target": "check point set"})

    def test_split_read_control_still_allowed(self):
        self.assertTrue(mod14.validate_operator_action(
            {"kind": "read", "target": "sea ledd family record"}))


class TestR5005ActorNormaliserPastCuredBounds(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["condition a"]}

    def _inputs(self):
        return {"flag_conditions_fired": ["condition a"]}

    def _refused(self, actor):
        record = self._record()
        with self.assertRaises(ValueError, msg=actor):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3", actor=actor)
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_actor_six_added_letters(self):
        self._refused("personxxxxxx")

    def test_actor_four_replacements(self):
        self._refused("xyzzon")

    def test_actor_four_drops(self):
        self._refused("pn")

    def test_actor_three_transpositions(self):
        self._refused("epsrno")

    def test_actor_five_added_control_still_refused(self):
        self._refused("personxxxxx")

    def test_actor_plain_person_control_still_refused(self):
        self._refused("person")

    def test_program_actor_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR5008FreezeSetConstructor(unittest.TestCase):
    def test_evil_frozenset_freezes_to_plain_frozenset(self):
        frozen = mod14._freeze(_EvilFrozenset(("a",)))
        self.assertIs(type(frozen), frozenset)
        self.assertEqual(frozen, frozenset(("a",)))

    def test_evil_set_freezes_to_plain_set(self):
        frozen = mod14._freeze(_EvilSet(("a",)))
        self.assertIs(type(frozen), set)
        self.assertEqual(frozen, {"a"})

    def test_evil_frozenset_through_pilot_output(self):
        output = mod14.pilot_run(
            "timing", {"figure": 1, "part": _EvilFrozenset(("a",))})
        self.assertIs(type(output["part"]), frozenset)
        self.assertEqual(output["part"], frozenset(("a",)))

    def test_evil_set_through_error_carriage(self):
        failure = mod14.NamedShellFailure("carried part")
        failure.part = _EvilSet(("a",))
        carriage = mod14.error_carriage(failure)
        self.assertIs(type(carriage["failure_value"]["part"]), set)
        self.assertEqual(carriage["failure_value"]["part"], {"a"})

    def test_iter_lying_set_freezes_through_base_reading(self):
        instance = _IterLyingSet()
        set.add(instance, "a")
        frozen = mod14._freeze(instance)
        self.assertIs(type(frozen), set)
        self.assertEqual(frozen, {"a"})

    def test_iter_lying_frozenset_freezes_through_base_reading(self):
        instance = _IterLyingFrozenset(("a",))
        frozen = mod14._freeze(instance)
        self.assertIs(type(frozen), frozenset)
        self.assertEqual(frozen, frozenset(("a",)))

    def test_plain_set_and_frozenset_controls(self):
        self.assertEqual(mod14._freeze({"a", "b"}), {"a", "b"})
        self.assertIs(type(mod14._freeze({"a"})), set)
        self.assertEqual(
            mod14._freeze(frozenset(("a",))), frozenset(("a",)))
        self.assertIs(type(mod14._freeze(frozenset(("a",)))), frozenset)


class TestR5027FreezeDictItemsReading(unittest.TestCase):
    def test_substituted_items_dict_freezes_stored_entry(self):
        instance = _stored_dict(
            _SubstitutedItemsDict, {"real_entry": "kept"})
        self.assertEqual(mod14._freeze(instance), {"real_entry": "kept"})

    def test_empty_items_dict_freezes_stored_entry(self):
        instance = _stored_dict(
            _EmptyItemsDict, {"real_entry": "kept"})
        self.assertEqual(mod14._freeze(instance), {"real_entry": "kept"})

    def test_lying_dict_through_error_carriage(self):
        failure = mod14.NamedShellFailure("carriage form")
        failure.failure = _stored_dict(
            _SubstitutedItemsDict,
            {"name": "NamedShellFailure", "real_entry": "kept"})
        carriage = mod14.error_carriage(failure)
        self.assertEqual(
            carriage["failure_value"].get("real_entry"), "kept")
        self.assertNotIn("substituted_entry", carriage["failure_value"])

    def test_lying_dict_through_pilot_output(self):
        artefact = _stored_dict(
            _SubstitutedItemsDict, {"figure": 1, "real_entry": "kept"})
        output = mod14.pilot_run("timing", artefact)
        self.assertEqual(output.get("real_entry"), "kept")
        self.assertEqual(output.get("figure"), 1)
        self.assertNotIn("substituted_entry", output)

    def test_plain_dict_control(self):
        self.assertEqual(
            mod14._freeze({"real_entry": "kept"}), {"real_entry": "kept"})
        output = mod14.pilot_run(
            "timing", {"figure": 1, "real_entry": "kept"})
        self.assertEqual(output.get("real_entry"), "kept")


class TestR5030LawfulSideDresses(unittest.TestCase):
    def _allowed(self, action):
        self.assertTrue(mod14.validate_operator_action(action), action)

    def test_rule_path_six_added_letters(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flagxxxxxx rule"})

    def test_deletion_path_six_added_letters(self):
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletionxxxxxx rule"})

    def test_deletion_path_four_drops(self):
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deln rule"})

    def test_act_six_added_letters_on_protected_target(self):
        self._allowed({"kind": "editxxxxxx",
                       "target": "closed run record",
                       "path": "flag rule"})

    def test_destructive_act_six_added_on_protected_target(self):
        self._allowed({"kind": "deletexxxxxx",
                       "target": "checkpoint set",
                       "path": "deletion rule"})

    def test_plain_path_controls_still_allowed(self):
        self._allowed({"kind": "edit", "target": "closed run record",
                       "path": "flag rule"})
        self._allowed({"kind": "edit", "target": "checkpoint set",
                       "path": "deletion rule"})

    def test_wrong_path_control_still_barred(self):
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "edit", "target": "closed run record",
             "path": "deletionxxxxxx rule"}))
        self.assertFalse(mod14.validate_operator_action(
            {"kind": "edit", "target": "checkpoint set",
             "path": "flagxxxxxx rule"}))


class TestR5033CategoryCfConditionCharacters(unittest.TestCase):
    _CF_FORMS = (
        "\u202b", "\u202c", "\u202d", "\u2062", "\u2063",
        "\u2066", "\u2067", "\u206f", "\u08e2", "\ufff9",
    )

    def _record(self):
        return {"retention_tier": "Tier 1"}

    def _refused(self, fired, record=None):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record if record is not None else self._record(),
                inputs={"flag_conditions_fired": fired},
                outcome="promote", tier="Tier 3", actor="program")

    def test_each_named_cf_form_states_no_condition(self):
        for char in self._CF_FORMS:
            with self.subTest(char=hex(ord(char))):
                self._refused([char])

    def test_cf_mixed_with_spaces_only_states_no_condition(self):
        self._refused([" \u202b \u2063 "])

    def test_cf_through_the_record_states_no_condition(self):
        record = {"retention_tier": "Tier 1",
                  "flag_conditions_fired": ["\u202c"]}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                record, inputs={},
                outcome="promote", tier="Tier 3", actor="program")

    def test_cured_set_control_still_refused(self):
        self._refused(["\u200b"])
        self._refused(["\u202a"])

    def test_stated_condition_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR5038FreezeSetElementCollision(unittest.TestCase):
    def test_two_tuple_chains_at_depth_101_keep_two_elements(self):
        frozen = mod14._freeze(
            {_tuple_chain("a", 101), _tuple_chain("b", 101)})
        self.assertEqual(len(frozen), 2)

    def test_two_tuple_chains_at_depth_150_keep_two_elements(self):
        frozen = mod14._freeze(
            {_tuple_chain("a", 150), _tuple_chain("b", 150)})
        self.assertEqual(len(frozen), 2)

    def test_three_tuple_chains_at_depth_101_keep_three_elements(self):
        frozen = mod14._freeze(
            {_tuple_chain("a", 101), _tuple_chain("b", 101),
             _tuple_chain("c", 101)})
        self.assertEqual(len(frozen), 3)

    def test_frozenset_chains_at_depth_101_keep_two_elements(self):
        frozen = mod14._freeze(frozenset(
            (_tuple_chain("a", 101), _tuple_chain("b", 101))))
        self.assertIs(type(frozen), frozenset)
        self.assertEqual(len(frozen), 2)

    def test_collision_through_error_carriage(self):
        failure = mod14.NamedShellFailure("deep carried set")
        failure.carried = {
            _tuple_chain("a", 101), _tuple_chain("b", 101)}
        carriage = mod14.error_carriage(failure)
        self.assertEqual(
            len(carriage["failure_value"]["carried"]), 2)

    def test_depth_90_control_keeps_two_elements(self):
        frozen = mod14._freeze(
            {_tuple_chain("a", 90), _tuple_chain("b", 90)})
        self.assertEqual(len(frozen), 2)
        self.assertEqual(
            frozen, {_tuple_chain("a", 90), _tuple_chain("b", 90)})

    def test_depth_100_control_keeps_two_elements(self):
        frozen = mod14._freeze(
            {_tuple_chain("a", 100), _tuple_chain("b", 100)})
        self.assertEqual(len(frozen), 2)


if __name__ == "__main__":
    unittest.main()

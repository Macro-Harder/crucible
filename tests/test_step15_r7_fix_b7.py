"""Step 15 rerun, fix wave 6 pins, Builder 7, MOD-14 rows.

Rows pinned: R6-001, R6-002, R6-003, R6-004, R6-005 (MOD-14
limb), R6-008, R6-013, R6-014, R6-019 (MOD-14 limb), R6-031,
R6-032 (MOD-14 limb). Row R6-039 stands in the two named
wave 5 pin files and carries no pin here.
"""
import time
import unittest

import crucible.mod14 as mod14


def _barred(test, action):
    test.assertFalse(mod14.validate_operator_action(action), action)


def _allowed(test, action):
    test.assertTrue(mod14.validate_operator_action(action), action)


class TestR6001SevenAddedLetters(unittest.TestCase):
    def test_resolver_reads_seven_added_letters(self):
        self.assertEqual(mod14._resolve_word("xrxexcxoxrxdx"), "record")

    def test_delete_on_seven_added_target_barred(self):
        _barred(self, {"kind": "delete",
                       "target": "closed run xrxexcxoxrxdx",
                       "path": "other rule"})

    def test_six_added_control_still_barred(self):
        _barred(self, {"kind": "delete",
                       "target": "closed run xrxexcxoxrxd",
                       "path": "other rule"})

    def test_plain_target_control_still_barred(self):
        _barred(self, {"kind": "delete", "target": "closed run record",
                       "path": "other rule"})

    def test_read_control_still_allowed(self):
        _allowed(self, {"kind": "read", "target": "sealed family record"})

    def test_edit_on_flag_path_control_still_allowed(self):
        _allowed(self, {"kind": "edit", "target": "closed run record",
                        "path": "flag rule"})


class TestR6002CompoundedAtTotalSix(unittest.TestCase):
    def test_five_replacements_resolve(self):
        self.assertEqual(mod14._resolve_word("xhqczpvijt"), "checkpoint")
        _barred(self, {"kind": "delete", "target": "xhqczpvijt set",
                       "path": "other rule"})

    def test_five_drops_resolve(self):
        self.assertEqual(mod14._resolve_word("kpoit"), "checkpoint")
        _barred(self, {"kind": "delete", "target": "kpoit set",
                       "path": "other rule"})

    def test_composition_totalling_six_resolves(self):
        self.assertEqual(mod14._resolve_word("hcqkczionv"), "checkpoint")
        _barred(self, {"kind": "delete", "target": "hcqkczionv set",
                       "path": "other rule"})

    def test_three_non_adjacent_transpositions_resolve(self):
        self.assertEqual(mod14._resolve_word("tokcephinc"), "checkpoint")
        _barred(self, {"kind": "delete",
                       "target": "tokcephinc set",
                       "path": "other rule"})

    def test_four_replacements_control_still_barred(self):
        _barred(self, {"kind": "delete", "target": "xhqczpvint set",
                       "path": "other rule"})

    def test_four_drops_control_still_barred(self):
        _barred(self, {"kind": "delete", "target": "kpoint set",
                       "path": "other rule"})

    def test_total_five_composition_control_still_barred(self):
        _barred(self, {"kind": "delete", "target": "hcqkczoinv set",
                       "path": "other rule"})

    def test_three_adjacent_transpositions_control_still_barred(self):
        _barred(self, {"kind": "delete", "target": "hcekcpiont set",
                       "path": "other rule"})

    def test_single_non_adjacent_transposition_control(self):
        self.assertEqual(mod14._resolve_word("rdcore"), "record")


class TestR6003PartitionGroupReading(unittest.TestCase):
    def test_dressed_chunk_split_reads_as_target(self):
        self.assertEqual(
            mod14._normalise_name("ch ec kpx oi nt set"), "checkpoint set")
        _barred(self, {"kind": "delete",
                       "target": "ch ec kpx oi nt set",
                       "path": "other rule"})

    def test_dress_on_first_chunk(self):
        self.assertEqual(
            mod14._normalise_name("chx ec kp oi nt set"), "checkpoint set")
        _barred(self, {"kind": "delete",
                       "target": "chx ec kp oi nt set",
                       "path": "other rule"})

    def test_dress_on_last_chunk(self):
        self.assertEqual(
            mod14._normalise_name("ch ec kp oi ntx set"), "checkpoint set")
        _barred(self, {"kind": "delete",
                       "target": "ch ec kp oi ntx set",
                       "path": "other rule"})

    def test_plain_chunk_split_control_still_barred(self):
        self.assertEqual(
            mod14._normalise_name("ch ec kp oi nt set"), "checkpoint set")
        _barred(self, {"kind": "delete", "target": "ch ec kp oi nt set",
                       "path": "other rule"})

    def test_two_chunk_dressed_control_still_barred(self):
        self.assertEqual(
            mod14._normalise_name("checkpoin tx set"), "checkpoint set")
        _barred(self, {"kind": "delete", "target": "checkpoin tx set",
                       "path": "other rule"})


class TestR6004GroupReadingPastSixteenFragments(unittest.TestCase):
    def _split(self, articles):
        parts = []
        for index, char in enumerate("checkpoint"):
            parts.append(char)
            if index < articles:
                parts.append("a")
        return " ".join(parts) + " set"

    def test_seventeen_fragments_read_as_target(self):
        self.assertEqual(
            mod14._normalise_name(self._split(7)), "checkpoint set")
        _barred(self, {"kind": "delete", "target": self._split(7),
                       "path": "other rule"})

    def test_eighteen_fragments_read_as_target(self):
        self.assertEqual(
            mod14._normalise_name(self._split(8)), "checkpoint set")
        _barred(self, {"kind": "delete", "target": self._split(8),
                       "path": "other rule"})

    def test_nineteen_fragments_read_as_target(self):
        self.assertEqual(
            mod14._normalise_name(self._split(9)), "checkpoint set")
        _barred(self, {"kind": "delete", "target": self._split(9),
                       "path": "other rule"})

    def test_sixteen_fragments_control_still_barred(self):
        self.assertEqual(
            mod14._normalise_name(self._split(6)), "checkpoint set")
        _barred(self, {"kind": "delete", "target": self._split(6),
                       "path": "other rule"})

    def test_ten_fragments_control_still_barred(self):
        self.assertEqual(
            mod14._normalise_name(self._split(0)), "checkpoint set")
        _barred(self, {"kind": "delete", "target": self._split(0),
                       "path": "other rule"})


class TestR6005ShellActorPastBounds(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["threshold crossed"]}

    def _inputs(self):
        return {"flag_conditions_fired": ["threshold crossed"]}

    def _refused(self, actor):
        record = self._record()
        with self.assertRaises(ValueError, msg=actor):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 2", actor=actor)
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_actor_seven_added_letters_normalises(self):
        self.assertEqual(mod14._normalise_actor("pxexrxsxoxnxx"), "person")

    def test_actor_seven_added_letters_refused_at_shell_act(self):
        self._refused("pxexrxsxoxnxx")

    def test_actor_five_replacements_normalises(self):
        self.assertEqual(mod14._normalise_actor("qzxvjn"), "person")

    def test_actor_five_replacements_refused_at_shell_act(self):
        self._refused("qzxvjn")

    def test_actor_six_added_control_still_refused(self):
        self._refused("pxexrxsxoxnx")

    def test_actor_one_replacement_control_still_refused(self):
        self._refused("xerson")

    def test_actor_plain_person_control_still_refused(self):
        self._refused("person")

    def test_program_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 2", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 2")

    def test_program_one_drop_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 2", actor="prgram")
        self.assertEqual(updated["retention_tier"], "Tier 2")


class _DeepcopyBarred:
    def __deepcopy__(self, memo):
        return {"amount": 10, "currency": "USD"}


class TestR6008FreezeFallbackReturnsPartItself(unittest.TestCase):
    def test_fallback_part_in_dict_returned_as_itself(self):
        part = _DeepcopyBarred()
        frozen = mod14._freeze({"wrap": part})
        self.assertIs(frozen["wrap"], part)

    def test_fallback_part_in_list_returned_as_itself(self):
        part = _DeepcopyBarred()
        frozen = mod14._freeze([part])
        self.assertIs(frozen[0], part)

    def test_fallback_part_through_error_carriage(self):
        part = _DeepcopyBarred()
        failure = mod14.NamedShellFailure("carried part")
        failure.failure = {"name": "NamedShellFailure", "wrap": part}
        carriage = mod14.error_carriage(failure)
        self.assertIs(carriage["failure_value"]["wrap"], part)

    def test_fallback_part_through_pilot_output(self):
        part = _DeepcopyBarred()
        output = mod14.pilot_run("timing", {"figure": 1, "wrap": part})
        self.assertIs(output["wrap"], part)

    def test_plain_list_control_freezes_whole(self):
        self.assertEqual(mod14._freeze({"wrap": [1, 2]}), {"wrap": [1, 2]})


class _EmptyIterList(list):
    def __iter__(self):
        return iter(())


class _SubstitutedIterList(list):
    def __iter__(self):
        return iter(("substituted",))


class _EmptyIterTuple(tuple):
    def __iter__(self):
        return iter(())


class _SubstitutedIterTuple(tuple):
    def __iter__(self):
        return iter(("substituted",))


def _stored_list(cls, values):
    instance = cls()
    for value in values:
        list.append(instance, value)
    return instance


class TestR6013FreezeListTupleBaseIteration(unittest.TestCase):
    def test_empty_iter_list_freezes_stored_entries(self):
        instance = _stored_list(_EmptyIterList, [1, 2])
        self.assertEqual(mod14._freeze(instance), [1, 2])

    def test_substituted_iter_list_freezes_stored_entries(self):
        instance = _stored_list(_SubstitutedIterList, [1, 2])
        self.assertEqual(mod14._freeze(instance), [1, 2])

    def test_empty_iter_tuple_freezes_stored_entries(self):
        instance = _EmptyIterTuple((1, 2))
        self.assertEqual(mod14._freeze(instance), (1, 2))

    def test_substituted_iter_tuple_freezes_stored_entries(self):
        instance = _SubstitutedIterTuple((1, 2))
        self.assertEqual(mod14._freeze(instance), (1, 2))

    def test_lying_list_through_error_carriage(self):
        failure = mod14.NamedShellFailure("carriage form")
        failure.failure = {
            "name": "NamedShellFailure",
            "items": _stored_list(_SubstitutedIterList, ["real_a", "real_b"]),
        }
        carriage = mod14.error_carriage(failure)
        self.assertEqual(
            carriage["failure_value"]["items"], ["real_a", "real_b"])
        self.assertFalse(carriage["swallowed"])

    def test_plain_list_and_tuple_controls(self):
        self.assertEqual(mod14._freeze([1, 2]), [1, 2])
        self.assertEqual(mod14._freeze((1, 2)), (1, 2))


class _EmptyItemsDict(dict):
    def items(self):
        return iter(())


class _SubstitutedItemsDict(dict):
    def items(self):
        return iter((("figure", 1),))


class _EmptyIterSet(set):
    def __iter__(self):
        return iter(())


def _stored_dict(cls, entries):
    instance = cls()
    for key, value in entries.items():
        dict.__setitem__(instance, key, value)
    return instance


def _stored_set(cls, values):
    instance = cls()
    for value in values:
        set.add(instance, value)
    return instance


class TestR6014ScreenReadsBaseReadings(unittest.TestCase):
    def test_lying_dict_barred_entry_screened(self):
        artefact = _stored_dict(_EmptyItemsDict, {"money": 5})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_substituted_items_dict_barred_entry_screened(self):
        artefact = _stored_dict(_SubstitutedItemsDict, {"money": 5})
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_lying_set_barred_entry_screened(self):
        artefact = {"figure": _stored_set(_EmptyIterSet, ("money",))}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_plain_dict_barred_control_still_screened(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"money": 5})

    def test_plain_set_barred_control_still_screened(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"figure": {"money"}})

    def test_plain_list_pair_barred_control_still_screened(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"figure": [("money", 5)]})

    def test_lying_dict_harmless_control_passes(self):
        artefact = _stored_dict(_EmptyItemsDict, {"figure": 1})
        output = mod14.pilot_run("timing", artefact)
        self.assertEqual(output.get("figure"), 1)


class TestR6019ScreenWalkedStanding(unittest.TestCase):
    def test_shared_sibling_shape_answers_fast(self):
        value = ["leaf"]
        for _ in range(23):
            value = [value, value]
        start = time.monotonic()
        mod14._screen_pilot_artefact(value)
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 5.0)

    def test_shared_shape_plain_control_answers(self):
        value = ["leaf"]
        for _ in range(6):
            value = [value, value]
        mod14._screen_pilot_artefact(value)

    def test_deeper_reach_judged_at_its_own_depth_both_orders(self):
        shared = "leaf"
        for _ in range(10):
            shared = [shared]
        deep = shared
        for _ in range(95):
            deep = [deep]
        for root in ([shared, deep], [deep, shared]):
            with self.subTest(order=root[0] is deep):
                with self.assertRaises(mod14.NamedShellFailure):
                    mod14._screen_pilot_artefact(root)

    def test_within_bound_shared_control_answers(self):
        shared = "leaf"
        for _ in range(6):
            shared = [shared]
        deep = shared
        for _ in range(90):
            deep = [deep]
        mod14._screen_pilot_artefact([shared, deep])


class TestR6031LawfulSideAtNewBound(unittest.TestCase):
    def test_path_word_seven_added_letters_allowed(self):
        _allowed(self, {"kind": "edit", "target": "closed run record",
                        "path": "fxlxaxgxxxx rule"})

    def test_act_word_seven_added_letters_allowed(self):
        _allowed(self, {"kind": "exdxixtxxxx",
                        "target": "closed run record",
                        "path": "flag rule"})

    def test_plain_path_control_still_allowed(self):
        _allowed(self, {"kind": "edit", "target": "closed run record",
                        "path": "flag rule"})

    def test_six_added_path_control_still_allowed(self):
        _allowed(self, {"kind": "edit", "target": "closed run record",
                        "path": "flagxxxxxx rule"})

    def test_barred_delete_control_still_refused(self):
        _barred(self, {"kind": "delete", "target": "closed run record",
                       "path": "flag rule"})


class TestR6032BlankConditionClassShellLimb(unittest.TestCase):
    _CHARGED = (
        "\u034f", "\u180b", "\u180c", "\u180d", "\ufe00", "\ufe0f",
        "\u2800", "\u115f",
    )

    def _record(self):
        return {"retention_tier": "Tier 1"}

    def _refused(self, fired):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                self._record(),
                inputs={"flag_conditions_fired": fired},
                outcome="promote", tier="Tier 3", actor="program")

    def test_each_charged_char_states_no_condition(self):
        for char in self._CHARGED:
            with self.subTest(char=hex(ord(char))):
                self.assertFalse(mod14._has_stated_condition([char]))

    def test_each_charged_char_refuses_promotion(self):
        for char in self._CHARGED:
            with self.subTest(char=hex(ord(char))):
                self._refused([char])

    def test_cf_control_still_refused(self):
        self._refused(["\u202b"])

    def test_zero_width_control_still_refused(self):
        self._refused(["\u200b"])

    def test_empty_entry_control_still_refused(self):
        self._refused([""])

    def test_readable_condition_control_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["threshold crossed"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")

    def test_mn_char_beside_readable_condition_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": [
                "\u034f", "threshold crossed"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


if __name__ == "__main__":
    unittest.main()

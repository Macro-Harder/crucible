"""Step 15 rerun round 2 fix wave 2 tests, builder b7.

Items pinned: R2-011, R2-012, R2-013, R2-014, R2-057,
R2-058 (MOD-14 limb), R2-001 (MOD-03 limb), R2-043,
R2-044, R2-051 (MOD-03 limb).
"""
import unittest

import crucible.mod03 as mod03
import crucible.mod14 as mod14


class HidingList(list):
    """A list whose own iteration yields nothing."""

    def __iter__(self):
        return iter(())


class HidingTuple(tuple):
    """A tuple whose own iteration yields nothing."""

    def __iter__(self):
        return iter(())


def _hiding_list(*items):
    value = HidingList()
    for item in items:
        list.append(value, item)
    return value


def _hiding_tuple(*items):
    return HidingTuple(items)


class TestR2011ThreeAddedLetters(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_three_added_at_end_of_first_word(self):
        self._barred({"kind": "delete",
                      "target": "sealedxxx family record"})

    def test_three_added_inside_word(self):
        self._barred({"kind": "delete",
                      "target": "seaxxxled family record"})

    def test_three_added_destroy_closed_on_flag_path(self):
        self._barred({"kind": "destroy",
                      "target": "closedxxx run record",
                      "path": "flag rule"})

    def test_three_added_on_middle_word(self):
        self._barred({"kind": "delete",
                      "target": "closed runxxx record"})

    def test_three_added_checkpoint(self):
        self._barred({"kind": "delete",
                      "target": "checkpointxxx set"})

    def test_three_added_reason_form(self):
        result = mod14.validate_operator_action_with_reason(
            {"kind": "destroy", "target": "closedxxx run record",
             "path": "flag rule"})
        self.assertFalse(result["allowed"], result)

    def test_three_added_path_word_admits_lawful_edit(self):
        action = {"kind": "edit", "target": "closed run record",
                  "path": "flagxxx rule"}
        self.assertTrue(mod14.validate_operator_action(action), action)


class TestR2012DroppedLetterShortWords(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_checkpoint_set_drop_forms(self):
        self._barred({"kind": "delete", "target": "checkpoint st"})
        self._barred({"kind": "delete", "target": "checkpoint se"})

    def test_closed_run_drop_forms_on_flag_path(self):
        self._barred({"kind": "destroy", "target": "closed rn record",
                      "path": "flag rule"})
        self._barred({"kind": "destroy", "target": "closed ru record",
                      "path": "flag rule"})

    def test_checkpoint_edit_on_wrong_path_still_barred(self):
        self._barred({"kind": "edit", "target": "checkpoint se",
                      "path": "flag rule"})


class TestR2013TwoChangesOneWord(unittest.TestCase):
    def _barred(self, action):
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_dropped_with_replaced(self):
        self._barred({"kind": "delete",
                      "target": "sealx family record"})
        self._barred({"kind": "destroy",
                      "target": "clozd run record"})

    def test_transposed_with_dropped(self):
        self._barred({"kind": "delete",
                      "target": "saeld family record"})
        self._barred({"kind": "destroy",
                      "target": "saeld family record",
                      "path": "flag rule"})

    def test_script_mapping_change_with_dropped(self):
        self._barred({"kind": "delete",
                      "target": "\u0441losd run record"})
        self._barred({"kind": "destroy",
                      "target": "\u0421LOSD RUN RECORD",
                      "path": "flag rule"})


class TestR2014FlagActorNormaliser(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["condition a"]}

    def _inputs(self):
        return {"flag_conditions_fired": ["condition a"]}

    def test_letter_change_and_leet_actors_do_not_promote(self):
        for actor in ("persn", "pesron", "personx", "Persn",
                      "PERSONX", "p3rson"):
            record = self._record()
            with self.assertRaises(Exception, msg=actor):
                mod14.flag_evaluation(
                    record, inputs=self._inputs(),
                    outcome="promote", tier="Tier 3", actor=actor)
            self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_plural_actor_does_not_promote(self):
        record = self._record()
        with self.assertRaises(Exception):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3", actor="persons")
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_separator_split_actors_do_not_promote(self):
        for actor in ("per-son", "per_son", "per.son", "per son"):
            record = self._record()
            with self.assertRaises(Exception, msg=actor):
                mod14.flag_evaluation(
                    record, inputs=self._inputs(),
                    outcome="promote", tier="Tier 3", actor=actor)
            self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_doubled_article_actor_does_not_promote(self):
        record = self._record()
        with self.assertRaises(Exception):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3",
                actor="the the person")
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_script_with_letter_change_actor_does_not_promote(self):
        record = self._record()
        with self.assertRaises(Exception):
            mod14.flag_evaluation(
                record, inputs=self._inputs(),
                outcome="promote", tier="Tier 3",
                actor="p\u0435rsn")
        self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_split_actor_via_run_command_does_not_promote(self):
        result = mod14.run_command("flag_evaluation", {
            "summary_record": self._record(),
            "inputs": self._inputs(),
            "outcome": "promote", "tier": "Tier 3",
            "actor": "per-son",
        })
        self.assertIn("failure", result)
        self.assertNotEqual(result.get("retention_tier"), "Tier 3")

    def test_program_actor_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(), inputs=self._inputs(),
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR2057CensusFace(unittest.TestCase):
    def test_census_face_states_zero_permitted_divergence(self):
        record = mod14.nondeterminism_census(
            {"material_class": "pilot confined"})
        self.assertIn(
            "permitted divergence for any reportable run "
            "stays at zero",
            record["face_statement"])


class TestR2058StatedConditionEntry(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1"}

    def test_empty_string_condition_states_no_condition(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                self._record(),
                inputs={"flag_conditions_fired": [""]},
                outcome="promote", tier="Tier 3", actor="program")

    def test_none_condition_states_no_condition(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.flag_evaluation(
                self._record(),
                inputs={"flag_conditions_fired": [None]},
                outcome="promote", tier="Tier 3", actor="program")

    def test_stated_condition_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["c1"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR2001Mod03BaseIteration(unittest.TestCase):
    def test_ground_truth_in_hiding_list_part(self):
        record = {"outer": _hiding_list({"membership": "y"})}
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertFalse(mod03.validate_detection_input(record))
        self.assertFalse(mod03.validate_adjudication_input(record))

    def test_ground_truth_in_hiding_tuple_part(self):
        record = {"outer": _hiding_tuple({"ground_truth": "x"})}
        self.assertTrue(mod03.record_carries_ground_truth(record))

    def test_rule_state_in_hiding_list_part(self):
        output = [{"payload": _hiding_list({"reputation": 1})}]
        self.assertFalse(mod03.validate_generator_output(output))

    def test_strip_ground_truth_in_hiding_list_part(self):
        record = {"outer": _hiding_list(
            {"membership": "y", "keep": 1})}
        stripped = mod03.strip_ground_truth(record)
        self.assertEqual(list(stripped["outer"]), [{"keep": 1}])


class TestR2043FarmEdgeForms(unittest.TestCase):
    def test_two_character_string_edge_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=["ab"])

    def test_bytes_edge_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=[b"ab"])

    def test_wrong_size_edges_refused_in_named_form(self):
        for edges in ([("a", "b", "c")], [("a",)], [["a"]]):
            with self.assertRaises(
                    mod03.NamedGeneratorFailure, msg=repr(edges)):
                mod03.construct_farm(
                    ["a", "b"], farm_size=2, edges=edges)

    def test_non_iterable_edge_refused_in_named_form(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.construct_farm(
                ["a", "b"], farm_size=2, edges=[5])

    def test_dict_and_pair_edges_still_count(self):
        built = mod03.construct_farm(
            ["m1", "m2"], farm_size=2,
            edges=[{"voucher": "m1", "vouchee": "m2"}])
        self.assertEqual(
            built["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})
        built = mod03.construct_farm(
            ["m1", "m2"], farm_size=2, edges=[("m1", "m2")])
        self.assertEqual(
            built["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})


class TestR2044ColdSocietyDegreeOperands(unittest.TestCase):
    def test_string_share_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                91, envelope=10, gate_passing_share="0.5")

    def test_string_envelope_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                91, envelope="10", gate_passing_share=0.5)

    def test_boolean_share_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                91, envelope=10, gate_passing_share=True)

    def test_boolean_envelope_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.cold_society_degree(
                91, envelope=True, gate_passing_share=0.5)

    def test_plain_operands_still_read(self):
        self.assertEqual(mod03.cold_society_degree(90), 0)
        self.assertEqual(
            mod03.cold_society_degree(
                91, envelope=10, gate_passing_share=0.5),
            5.0)


class TestR2051Mod03WiderBarredReading(unittest.TestCase):
    def test_transliteration_readings_bar(self):
        for key in ("mem\u0431ership", "membe\u0440ship",
                    "member\u0441hip", "is_ho\u043dest",
                    "is_\u0445onest", "ground_tr\u0443th",
                    "groun\u0434_truth"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_greek_readings_only_at_mod10_now_bar(self):
        for key in ("m\u03b7mbership", "membershi\u03c0",
                    "is_\u03c7onest", "i\u03c2_honest",
                    "g\u03c1ound_truth"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_armenian_readings_bar(self):
        for key in ("is_h\u0585nest", "is_ho\u0578est"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_small_capital_and_phonetic_readings_bar(self):
        for key in ("\u1d0dembership", "is_hon\u1d07st",
                    "\u0262round_truth", "\u1d0d3mbership"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_symbol_readings_bar(self):
        for key in ("m\u20acmbership", "\u00a3abel",
                    "!abel", "|abel"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_r1_009_added_letters_bar(self):
        for key in ("member\u0452hip", "members\u0493ip"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_dressed_key_carries_ground_truth_end_to_end(self):
        record = {"outer": {"m\u03b7mbership": 1}}
        self.assertTrue(mod03.record_carries_ground_truth(record))

    def test_named_composites_from_the_source_paper_bar(self):
        for key in ("m\u03b7mb-3rship", "gr0un\u0434_tr-uth",
                    "\u0433round._7ruth", "i\u03c2_hon-3st",
                    "m3mbe-rs\u0445ip", "\u1d0d3mbe_rship",
                    "\u00a3a-b3l"):
            self.assertTrue(mod03._is_barred_key(key), key)

    def test_clean_names_still_admitted(self):
        for key in ("activity", "labelled", "keep"):
            self.assertFalse(mod03._is_barred_key(key), key)


if __name__ == "__main__":
    unittest.main()

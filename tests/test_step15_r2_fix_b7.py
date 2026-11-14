"""Step 15 round 2 fix tests, builder b7, MOD-14 and MOD-03 items.

Items pinned: R1-012, R1-013, R1-014, R1-075, R1-085,
R1-032, R1-035, R1-037, R1-016.
"""
import unittest

import crucible.mod03 as mod03
import crucible.mod04 as mod04
import crucible.mod08 as mod08
import crucible.mod09 as mod09
import crucible.mod12 as mod12
import crucible.mod13 as mod13
import crucible.mod14 as mod14


def _cast_point(**extra):
    point = {
        "population": 2,
        "archetype_mix": {"arch-a": 2},
    }
    point.update(extra)
    return point


def _records():
    return [mod03.make_archetype_record(
        archetype_id="arch-a", ground_truth_label="honest")]


class HidingDict(dict):
    """A dict whose items and keys calls hide its real entries."""

    def items(self):
        return []

    def keys(self):
        return []


class TestR1012ScriptAndDigitDress(unittest.TestCase):
    def test_uppercase_cyrillic_closed_destroy_on_flag_path(self):
        target = "cl\u041e\u0421\u0415d run record"
        action = {"kind": "destroy", "target": target, "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_uppercase_greek_sealed_edit(self):
        target = "\u03a3\u0395\u0391\u039b\u0395d family record"
        action = {"kind": "edit", "target": target}
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_arabic_indic_digits_closed_destroy_on_flag_path(self):
        target = "cl\u0660s\u0663d run record"
        action = {"kind": "destroy", "target": target, "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_extended_arabic_indic_digit_sealed_edit(self):
        target = "s\u06f3aled family record"
        action = {"kind": "edit", "target": target}
        self.assertFalse(mod14.validate_operator_action(action), action)


class TestR1013WordForms(unittest.TestCase):
    def _barred(self, target):
        action = {"kind": "destroy", "target": target, "path": "flag rule"}
        self.assertFalse(mod14.validate_operator_action(action), action)

    def test_dropped_letter_forms(self):
        self._barred("clsed run record")
        self._barred("closed run recrd")
        self._barred("seled family record")

    def test_replaced_letter_forms(self):
        self._barred("clozed run record")
        self._barred("closed run rexord")

    def test_transposed_letter_forms(self):
        self._barred("clsoed run record")
        self._barred("closed run recodr")

    def test_two_added_letter_forms(self):
        self._barred("cloxsedq run record")
        self._barred("closed run recordzz")


class TestR1014PersonActorDress(unittest.TestCase):
    def _record(self):
        return {"retention_tier": "Tier 1",
                "flag_conditions_fired": ["condition a"]}

    def test_dressed_person_actors_do_not_promote(self):
        for actor in ("PERSON", " person ", "the person", "a  person",
                      "The Person"):
            record = self._record()
            with self.assertRaises(Exception, msg=actor):
                mod14.flag_evaluation(
                    record,
                    inputs={"flag_conditions_fired": ["condition a"]},
                    outcome="promote", tier="Tier 3", actor=actor)
            self.assertEqual(record.get("retention_tier"), "Tier 1")

    def test_dressed_person_actor_via_run_command(self):
        result = mod14.run_command("flag_evaluation", {
            "summary_record": self._record(),
            "inputs": {"flag_conditions_fired": ["condition a"]},
            "outcome": "promote", "tier": "Tier 3",
            "actor": "the  PERSON",
        })
        self.assertIn("failure", result)
        self.assertNotEqual(result.get("retention_tier"), "Tier 3")

    def test_plain_program_actor_still_promotes(self):
        updated = mod14.flag_evaluation(
            self._record(),
            inputs={"flag_conditions_fired": ["condition a"]},
            outcome="promote", tier="Tier 3", actor="program")
        self.assertEqual(updated["retention_tier"], "Tier 3")


class TestR1075PilotArtefactGuard(unittest.TestCase):
    def test_deep_artefact_raises_named_failure(self):
        artefact = {"figure": 1}
        for _ in range(300):
            artefact = {"nest": artefact}
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_cyclic_dict_artefact_raises_named_failure(self):
        artefact = {}
        artefact["self"] = artefact
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_cyclic_list_artefact_raises_named_failure(self):
        artefact = []
        artefact.append(artefact)
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", artefact)

    def test_ordinary_artefact_still_runs(self):
        output = mod14.pilot_run("timing", {"figure": 1})
        self.assertEqual(output["confinement_label"], "pilot confined")


class TestR1085NamedFamilyFailureValue(unittest.TestCase):
    def test_named_family_carries_failure_value(self):
        failures = [
            mod03.NamedGeneratorFailure("probe failure b7"),
            mod04.NamedFailure("probe failure b7"),
            mod08.NamedDetectionFailure("probe failure b7"),
            mod09.NamedAttackerFailure("probe failure b7"),
            mod12.NamedControllerFailure("probe failure b7"),
            mod13.NamedReplicationFailure("probe failure b7"),
            mod14.NamedShellFailure("probe failure b7"),
        ]
        for failure in failures:
            carriage = mod14.error_carriage(
                failure, run_id="run-9", stage="probe")
            self.assertTrue(carriage["failure_value"], failure)
            self.assertIn(
                "probe failure b7", str(carriage["failure_value"]),
                failure)


class TestR1032FarmSizeGuard(unittest.TestCase):
    def test_build_cast_guards_farm_size(self):
        for bad in (-1, 2.5, "2", True):
            with self.assertRaises(mod03.NamedGeneratorFailure, msg=repr(bad)):
                mod03.build_cast(
                    _cast_point(farm_size=bad), _records(),
                    strategy_class="fixed")

    def test_construct_farm_guards_farm_size(self):
        for bad in (-1, 2.5, "2", True):
            with self.assertRaises(mod03.NamedGeneratorFailure, msg=repr(bad)):
                mod03.construct_farm(["m1", "m2"], farm_size=bad)

    def test_valid_farm_sizes_still_build(self):
        built = mod03.construct_farm(["m1", "m2"], farm_size=2)
        self.assertEqual(len(built["farms"]), 1)
        cast = mod03.build_cast(
            _cast_point(farm_size=0), _records(), strategy_class="fixed")
        self.assertEqual(cast["population"], 2)


class TestR1035ColdSocietyDegreeDayForm(unittest.TestCase):
    def test_bad_day_forms_refused_in_named_form(self):
        for bad in (90.5, 91.5, True, False, "91", "90", None):
            with self.assertRaises(mod03.NamedGeneratorFailure, msg=repr(bad)):
                mod03.cold_society_degree(bad)

    def test_plain_days_still_read(self):
        self.assertEqual(mod03.cold_society_degree(90), 0)
        result = mod03.cold_society_degree(
            91, envelope=10, gate_passing_share=0.5)
        self.assertEqual(result, 5.0)


class TestR1037InitialEdges(unittest.TestCase):
    def test_string_initial_edge_refused(self):
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.build_cast(
                _cast_point(), _records(), strategy_class="fixed",
                initial_edges=["ab"])

    def test_wrong_size_pairs_refused(self):
        for edges in ([("agent-0000",)],
                      [("agent-0000", "agent-0001", "agent-0002")],
                      [["agent-0000"]]):
            with self.assertRaises(mod03.NamedGeneratorFailure, msg=repr(edges)):
                mod03.build_cast(
                    _cast_point(), _records(), strategy_class="fixed",
                    initial_edges=edges)

    def test_valid_pair_still_builds(self):
        cast = mod03.build_cast(
            _cast_point(), _records(), strategy_class="fixed",
            initial_edges=[("agent-0000", "agent-0001")])
        self.assertEqual(len(cast["initial_graph"]["edges"]), 1)


class TestR1016BaseDictReadings(unittest.TestCase):
    def test_ground_truth_read_through_base_dict_items(self):
        record = HidingDict({"ground_truth": "x"})
        self.assertTrue(mod03.record_carries_ground_truth(record))
        self.assertFalse(mod03.validate_detection_input(record))
        self.assertFalse(mod03.validate_adjudication_input(record))

    def test_nested_ground_truth_read_through_base_dict_items(self):
        record = {"outer": HidingDict({"membership": "y"})}
        self.assertTrue(mod03.record_carries_ground_truth(record))

    def test_rule_state_read_through_base_dict_items(self):
        output = [HidingDict({"reputation": 1})]
        self.assertFalse(mod03.validate_generator_output(output))

    def test_strip_ground_truth_through_base_dict_items(self):
        record = HidingDict({"ground_truth": "x", "keep": 1})
        self.assertEqual(mod03.strip_ground_truth(record), {"keep": 1})


if __name__ == "__main__":
    unittest.main()

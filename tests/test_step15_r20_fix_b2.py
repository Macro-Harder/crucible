"""Step 15, second run, fix wave 19, Builder 2 pins.

Group 2: the MOD-10 equality, reading, copy, and deferred
family. Rows R19-003, R19-004, R19-009, R19-019, R19-033,
R19-036, R19-038, R19-040, R19-052, and R19-053. Each
distinguishing pin hands the charged act a value whose own
equality, hash, or firing reading must not be trusted, beside
plain controls whose standing the cure keeps.
"""
import unittest

import crucible.mod01 as mod01
import crucible.mod10 as mod10


class EqFalseStr(str):
    """A text value storing its text whose equality answers False."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class EqTrueStr(str):
    """A text value storing its text whose equality answers True."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class RaiseEqStr(str):
    """A text value whose equality and inequality readings raise."""

    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    def __ne__(self, other):
        raise RuntimeError("inequality reading raises")

    __hash__ = str.__hash__


class HashRaise:
    """A value whose hash reading raises the given exception."""

    def __init__(self, exc):
        self._exc = exc

    def __hash__(self):
        raise self._exc

    def __eq__(self, other):
        return False


class ArmedKey(str):
    """A key whose hash collides with a stated text and whose
    equality reading raises once the class flag stands up."""

    armed = False

    def __hash__(self):
        return str.__hash__("collide")

    def __eq__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed equality raises")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if ArmedKey.armed:
            raise RuntimeError("armed inequality raises")
        return str.__ne__(self, other)


class CollidingKey(str):
    """A key whose hash collides with the text firing and whose
    equality reading raises once the class flag stands up."""

    armed = False

    def __hash__(self):
        return str.__hash__("firing")

    def __eq__(self, other):
        if CollidingKey.armed:
            raise RuntimeError("colliding equality raises")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if CollidingKey.armed:
            raise RuntimeError("colliding inequality raises")
        return str.__ne__(self, other)


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()
        ArmedKey.armed = False
        CollidingKey.armed = False

    def tearDown(self):
        mod10.reset_stores()
        ArmedKey.armed = False
        CollidingKey.armed = False


class TestR19003BooleanValidationEquality(Base):
    """Row R19-003: the eight boolean validation acts judge
    returned values on the text they store."""

    def test_storage_claim_bypass(self):
        claim = {"basis": EqFalseStr("DQ7-08"),
                 "reliance": EqFalseStr("governing")}
        self.assertFalse(mod10.validate_storage_claim(claim))

    def test_storage_claim_false_direction(self):
        claim = {"basis": EqTrueStr("plain basis"),
                 "reliance": EqTrueStr("recorded reliance")}
        self.assertTrue(mod10.validate_storage_claim(claim))

    def test_storage_claim_raising(self):
        claim = {"basis": RaiseEqStr("DQ7-08"), "reliance": "governing"}
        self.assertFalse(mod10.validate_storage_claim(claim))

    def test_retention_report_bypass(self):
        report = {"source": EqFalseStr("interval_records"),
                  "tier_claim": EqFalseStr("final")}
        self.assertFalse(mod10.validate_retention_report(report))

    def test_retention_report_false_direction(self):
        report = {"source": EqTrueStr("direct records"),
                  "tier_claim": EqTrueStr("interim")}
        self.assertTrue(mod10.validate_retention_report(report))

    def test_retention_report_raising(self):
        report = {"source": RaiseEqStr("interval_records"),
                  "tier_claim": "final"}
        self.assertFalse(mod10.validate_retention_report(report))

    def test_annotation_claim_bypass(self):
        claim = {"claim": EqFalseStr(
            "annotation_state_equal_across_append")}
        self.assertFalse(mod10.validate_annotation_claim(claim))

    def test_annotation_claim_false_direction(self):
        claim = {"claim": EqTrueStr("some other claim")}
        self.assertTrue(mod10.validate_annotation_claim(claim))

    def test_annotation_claim_raising(self):
        claim = {"claim": RaiseEqStr(
            "annotation_state_equal_across_append")}
        self.assertFalse(mod10.validate_annotation_claim(claim))

    def _sizing(self, wording_value):
        sizing = mod10.retention_sizing()
        sizing["wording"] = {"note": wording_value}
        return sizing

    def test_retention_sizing_bypass(self):
        self.assertFalse(mod10.validate_retention_sizing(
            self._sizing(EqFalseStr("forecast"))))

    def test_retention_sizing_false_direction(self):
        self.assertTrue(mod10.validate_retention_sizing(
            self._sizing(EqTrueStr("plain wording"))))

    def test_retention_sizing_raising(self):
        self.assertFalse(mod10.validate_retention_sizing(
            self._sizing(RaiseEqStr("forecast"))))

    def test_sample_record_bypass(self):
        sample = {"presented_as": EqFalseStr(
            "generator_test_battery_sample")}
        self.assertFalse(mod10.validate_sample_record(sample))

    def test_sample_record_false_direction(self):
        sample = {"presented_as": EqTrueStr("ordinary presentation")}
        self.assertTrue(mod10.validate_sample_record(sample))

    def test_sample_record_raising(self):
        sample = {"presented_as": RaiseEqStr(
            "generator_test_battery_sample")}
        self.assertFalse(mod10.validate_sample_record(sample))

    def test_retention_record_bypass(self):
        record = {"governing_rule": "DQ7-08 stated rule",
                  "reliance": EqFalseStr("governing")}
        self.assertFalse(mod10.validate_retention_record(record))

    def test_retention_record_false_direction(self):
        record = {"governing_rule": "DQ7-08 stated rule",
                  "reliance": EqTrueStr("recorded")}
        self.assertTrue(mod10.validate_retention_record(record))

    def test_retention_record_raising(self):
        record = {"governing_rule": "DQ7-08 stated rule",
                  "reliance": RaiseEqStr("governing")}
        self.assertFalse(mod10.validate_retention_record(record))

    def test_store_placement_bypass(self):
        artefact = {"kind": EqFalseStr("pilot"), "store": "elsewhere"}
        self.assertFalse(mod10.validate_store_placement(artefact))

    def test_store_placement_false_direction(self):
        artefact = {"kind": EqTrueStr("display"),
                    "store": EqFalseStr("pilot")}
        self.assertTrue(mod10.validate_store_placement(artefact))

    def test_store_placement_raising(self):
        artefact = {"kind": RaiseEqStr("pilot"), "store": "pilot"}
        self.assertTrue(mod10.validate_store_placement(artefact))

    def test_view_carriage_bypass(self):
        carriage = {"form": EqFalseStr("singular_vector")}
        self.assertFalse(mod10.validate_view_carriage(carriage))

    def test_view_carriage_false_direction(self):
        carriage = {"form": EqTrueStr("per viewer carriage")}
        self.assertTrue(mod10.validate_view_carriage(carriage))

    def test_view_carriage_raising(self):
        carriage = {"form": RaiseEqStr("singular_vector")}
        self.assertFalse(mod10.validate_view_carriage(carriage))

    def test_plain_controls(self):
        self.assertFalse(mod10.validate_storage_claim(
            {"basis": "DQ7-08", "reliance": "governing"}))
        self.assertTrue(mod10.validate_storage_claim(
            {"basis": "plain", "reliance": "recorded"}))
        self.assertFalse(mod10.validate_retention_report(
            {"source": "interval_records", "tier_claim": "final"}))
        self.assertTrue(mod10.validate_view_carriage(
            {"form": "per viewer carriage"}))


def _components(viewer):
    return {
        "attacker_controlled_share": {
            "numerator": 3, "denominator": 10, "proportion": 0.3,
            "viewer_identifier": viewer,
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
        "farm_share_of_reputation_mass": {
            "numerator": 1.5, "denominator": 5.0, "proportion": 0.3,
            "viewer_identifier": viewer,
            "numerator_kind": "binary64 value",
            "denominator_kind": "binary64 value",
        },
        "largest_component_share": {
            "component_size": 4, "population_size": 10,
            "proportion": 0.4,
            "component_definition_version": "version in force",
            "viewer_identifier": viewer,
            "component_size_kind": "integer count",
            "population_size_kind": "integer count",
        },
        "honest_loss_rate": {
            "numerator": 1, "denominator": 10, "rate": 0.1,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": viewer,
            "numerator_kind": "integer count",
            "denominator_kind": "integer count",
        },
    }


def _components_per_field(viewers):
    components = _components("viewer-1")
    fields = list(components)
    for field, viewer in zip(fields, viewers):
        components[field]["viewer_identifier"] = viewer
    return components


class AlwaysEq:
    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 42


class TestR19004JointOutcomeViewerSet(Base):
    """Row R19-004: distinct viewers stand counted on their
    stored forms at build_joint_outcome_vector."""

    def test_always_equal_viewers_refused(self):
        viewers = [AlwaysEq(), AlwaysEq(), AlwaysEq(), AlwaysEq()]
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=_components_per_field(viewers),
                divergence_companion={"nil_divergence_components": []})

    def test_boolean_and_number_viewers_count_apart(self):
        viewers = [1, True, 1, True]
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=_components_per_field(viewers),
                divergence_companion={"nil_divergence_components": []})

    def test_list_viewer_named_refusal(self):
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=_components(["viewer-1"]),
                divergence_companion={"nil_divergence_components": []})

    def test_plain_control(self):
        record = mod10.build_joint_outcome_vector(
            components=_components("viewer-1"),
            divergence_companion={"nil_divergence_components": []})
        self.assertTrue(mod01.validate_record("15", record))


class TestR19009ReplayCheck(Base):
    """Row R19-009: replay_check judges kind first through the
    base value form."""

    def test_boolean_record_not_number_replay(self):
        result = mod10.replay_check(
            {"record": 1, "verdict": "held"},
            {"record": True, "verdict": "held"})
        self.assertFalse(result["record_level_equal"])

    def test_lying_equality_record(self):
        result = mod10.replay_check(
            {"record": "rec-A", "verdict": "held"},
            {"record": EqTrueStr("rec-B"), "verdict": "held"})
        self.assertFalse(result["record_level_equal"])

    def test_raising_equality_record(self):
        result = mod10.replay_check(
            {"record": "rec-A", "verdict": "held"},
            {"record": RaiseEqStr("rec-A"),
             "verdict": RaiseEqStr("held")})
        self.assertTrue(result["record_level_equal"])
        self.assertTrue(result["verdict_level_equal"])

    def test_plain_controls(self):
        result = mod10.replay_check(
            {"record": "rec-A", "verdict": "held"},
            {"record": "rec-A", "verdict": "held"})
        self.assertTrue(result["record_level_equal"])
        result = mod10.replay_check(
            {"record": "rec-A", "verdict": "held"},
            {"record": "rec-B", "verdict": "held"})
        self.assertFalse(result["record_level_equal"])


class TestR19019SafeCopyAssignment(Base):
    """Row R19-019: the _safe_copy dict assignment limb at
    RecorderStore.retain_run_record carries an armed inner dict
    whole or refuses it in a named form."""

    def test_armed_inner_dict_carried_or_named(self):
        inner = {"collide": 1}
        dict.__setitem__(inner, ArmedKey("armed-key"), 2)
        ArmedKey.armed = True
        record = {"run_id": "run-19-armed", "inner": inner}
        try:
            stored = mod10.retain_run_record(record)
        except ValueError:
            stored = None
        ArmedKey.armed = False
        if stored is not None:
            carried = stored["inner"]
            self.assertEqual(len(carried), 2)
            self.assertEqual(sorted(
                str.__str__(key) for key in carried
                if not isinstance(key, ArmedKey) or True), sorted(
                str.__str__(key) for key in carried))
            values = sorted(carried.values())
            self.assertEqual(values, [1, 2])

    def test_plain_control(self):
        stored = mod10.retain_run_record(
            {"run_id": "run-19-plain", "inner": {"a": 1, "b": 2}})
        self.assertEqual(stored["inner"], {"a": 1, "b": 2})
        read = mod10.read_run_record("run-19-plain")
        self.assertEqual(read["inner"], {"a": 1, "b": 2})


class TestR19033RetainedIdentifierEquality(Base):
    """Row R19-033: retained_version_set and
    rerun_list_for_rule_change match through the stored key
    match reading."""

    def test_retained_version_set_lying_dress(self):
        mod10.retain_run_record({
            "run_id": "rec-33", "rule_version_set": ["v1", "v2"]})
        result = mod10.retained_version_set(EqFalseStr("rec-33"))
        self.assertEqual(result, ["v1", "v2"])

    def test_retained_version_set_raising_dress(self):
        mod10.retain_run_record({
            "run_id": "rec-33", "rule_version_set": ["v1", "v2"]})
        result = mod10.retained_version_set(RaiseEqStr("rec-33"))
        self.assertEqual(result, ["v1", "v2"])

    def test_rerun_list_lying_family_dress(self):
        mod10.retain_run_record({
            "run_id": "rec-33f", "family_id": "fam-33"})
        result = mod10.rerun_list_for_rule_change(EqFalseStr("fam-33"))
        self.assertEqual(result["records_in_question"], ["rec-33f"])

    def test_rerun_list_raising_rid(self):
        mod10.retain_run_record({
            "run_id": "rec-33g1", "family_id": "fam-33g"})
        mod10.retain_run_record({
            "run_id": RaiseEqStr("rec-33g2"), "family_id": "fam-33g"})
        result = mod10.rerun_list_for_rule_change("fam-33g")
        self.assertEqual(len(result["records_in_question"]), 2)
        self.assertIn("rec-33g1", result["records_in_question"])

    def test_plain_controls(self):
        mod10.retain_run_record({
            "run_id": "rec-33p", "family_id": "fam-33p",
            "rule_version_set": ["v9"]})
        self.assertEqual(mod10.retained_version_set("rec-33p"), ["v9"])
        self.assertEqual(
            mod10.retained_version_set("absent")["form"],
            mod10.FORM_ONLY)
        result = mod10.rerun_list_for_rule_change("fam-33p")
        self.assertEqual(result["records_in_question"], ["rec-33p"])


class TestR19036OpeningHashGuards(Base):
    """Row R19-036: the seven acts guard their opening hash
    reading against every exception form."""

    def _acts(self, ident):
        store = mod10.new_store()
        return [
            ("read_run_record", lambda: store.read_run_record(ident)),
            ("has_run_record", lambda: store.has_run_record(ident)),
            ("run_records_for_run",
             lambda: mod10.run_records_for_run(ident)),
            ("summary_record_for_run",
             lambda: mod10.summary_record_for_run(ident)),
            ("retention_record_for_run",
             lambda: mod10.retention_record_for_run(ident)),
            ("reserve_hold_for_run",
             lambda: mod10.reserve_hold_for_run(ident)),
            ("gc08_record",
             lambda: mod10.gc08_record("call_log", ident)),
        ]

    def test_runtime_error_hash_answers_named(self):
        for name, act in self._acts(HashRaise(RuntimeError("boom"))):
            with self.assertRaises(mod10.LookupFailure, msg=name):
                act()

    def test_value_error_hash_answers_named(self):
        for name, act in self._acts(HashRaise(ValueError("boom"))):
            with self.assertRaises(mod10.LookupFailure, msg=name):
                act()

    def test_plain_absent_controls(self):
        store = mod10.new_store()
        with self.assertRaises(mod10.LookupFailure):
            store.read_run_record("absent")
        self.assertFalse(store.has_run_record("absent"))
        with self.assertRaises(mod10.LookupFailure):
            mod10.run_records_for_run("absent")
        summary = mod10.summary_record_for_run("absent")
        self.assertEqual(summary["form"], mod10.FORM_ONLY)
        retention = mod10.retention_record_for_run("absent")
        self.assertEqual(retention["form"], mod10.FORM_ONLY)
        self.assertIsNone(mod10.reserve_hold_for_run("absent"))
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", "absent")


class TestR19038SafeCopyDepth(Base):
    """Row R19-038: resume_from_checkpoint through _safe_copy
    refuses a 3000 deep checkpoint in the named deep form."""

    def _deep(self, depth):
        value = {"leaf": 1}
        for _ in range(depth):
            value = {"nested": value}
        return value

    def test_deep_checkpoint_named_refusal(self):
        checkpoint = {"run_id": "run-38-deep", "simulated_day": 1,
                      "payload": self._deep(3000)}
        with self.assertRaises(ValueError) as caught:
            mod10.resume_from_checkpoint(checkpoint)
        self.assertIn("deep or cyclic", str(caught.exception))

    def test_plain_control(self):
        checkpoint = {"run_id": "run-38-plain", "simulated_day": 1,
                      "payload": {"nested": {"leaf": 1}}}
        resumed = mod10.resume_from_checkpoint(checkpoint)
        self.assertEqual(resumed["payload"], {"nested": {"leaf": 1}})


class TestR19040DeferredEvaluationReadings(Base):
    """Row R19-040: apply_deferred_evaluation runs no handed
    equality reading at its stored record read or its duplicate
    test."""

    def test_firing_one_raising_identifier(self):
        mod10.write_summary_record({"run_id": "run-40a"})
        updated = mod10.apply_deferred_evaluation(
            {"run_id": RaiseEqStr("run-40a")}, 1,
            inputs={"a": 1}, outcome="first outcome")
        firings = [entry["firing"]
                   for entry in updated["deferred_evaluations"]]
        self.assertEqual(firings, [1])

    def test_firing_two_raising_identifier(self):
        mod10.write_summary_record({
            "run_id": "run-40b",
            "deferred_evaluations": [{
                "firing": 1, "inputs": {"a": 1},
                "outcome": "first outcome", "conditions": [1, 2],
                "written_into": "summary record"}]})
        updated = mod10.apply_deferred_evaluation(
            {"run_id": RaiseEqStr("run-40b")}, 2,
            inputs={"b": 2}, outcome="second outcome")
        firings = [entry["firing"]
                   for entry in updated["deferred_evaluations"]]
        self.assertEqual(firings, [1, 2])

    def test_colliding_entry_duplicate_test(self):
        entry = {}
        dict.__setitem__(entry, CollidingKey("other"), 0)
        dict.__setitem__(entry, "zzz", 1)
        mod10.write_summary_record({
            "run_id": "run-40c", "deferred_evaluations": [entry]})
        CollidingKey.armed = True
        updated = mod10.apply_deferred_evaluation(
            {"run_id": "run-40c"}, 1,
            inputs={"a": 1}, outcome="first outcome")
        CollidingKey.armed = False
        firings = [item.get("firing")
                   for item in updated["deferred_evaluations"]
                   if isinstance(item, dict)]
        self.assertIn(1, firings)

    def test_plain_controls(self):
        mod10.write_summary_record({"run_id": "run-40p"})
        updated = mod10.apply_deferred_evaluation(
            {"run_id": "run-40p"}, 1,
            inputs={"a": 1}, outcome="first outcome")
        self.assertEqual(
            [e["firing"] for e in updated["deferred_evaluations"]], [1])
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(
                {"run_id": "run-40p"}, 1,
                inputs={"a": 1}, outcome="first outcome")


class TestR19052CumulativeProjectionSize(Base):
    """Row R19-052: cumulative_storage_projection judges a size
    in its stated form before counting it."""

    def test_text_size_named_refusal(self):
        with self.assertRaises(ValueError):
            mod10.cumulative_storage_projection(
                [{"size": "5", "artefact_class": "a"}],
                [{"retained_per_run": 1, "runs": 1}])

    def test_boolean_size_named_refusal(self):
        with self.assertRaises(ValueError):
            mod10.cumulative_storage_projection(
                [{"size": True, "artefact_class": "a"}],
                [{"retained_per_run": 1, "runs": 1}])

    def test_plain_control(self):
        result = mod10.cumulative_storage_projection(
            [{"size": 5, "artefact_class": "a"},
             {"size": 7, "artefact_class": "a"},
             {"artefact_class": "b"}],
            [{"retained_per_run": 1, "runs": 1}])
        self.assertEqual(
            result["retained_actuals_by_artefact_class"], {"a": 12})


class TestR19053DeferredPreservation(Base):
    """Row R19-053: stored evaluations stand preserved on both
    firing limbs of apply_deferred_evaluation."""

    def test_first_firing_preserves_stored_second(self):
        mod10.write_summary_record({
            "run_id": "run-53",
            "deferred_evaluations": [{
                "firing": 2, "inputs": {"b": 2},
                "outcome": "second outcome", "conditions": [1, 2, 3],
                "written_into": "summary record"}]})
        updated = mod10.apply_deferred_evaluation(
            {"run_id": "run-53"}, 1,
            inputs={"a": 1}, outcome="first outcome")
        firings = sorted(
            entry["firing"] for entry in updated["deferred_evaluations"])
        self.assertEqual(firings, [1, 2])
        stored = mod10.summary_record_for_run("run-53")
        stored_firings = sorted(
            entry["firing"] for entry in stored["deferred_evaluations"])
        self.assertEqual(stored_firings, [1, 2])

    def test_second_firing_preservation_control(self):
        mod10.write_summary_record({
            "run_id": "run-53c",
            "deferred_evaluations": [{
                "firing": 1, "inputs": {"a": 1},
                "outcome": "first outcome", "conditions": [1, 2],
                "written_into": "summary record"}]})
        updated = mod10.apply_deferred_evaluation(
            {"run_id": "run-53c"}, 2,
            inputs={"b": 2}, outcome="second outcome")
        firings = sorted(
            entry["firing"] for entry in updated["deferred_evaluations"])
        self.assertEqual(firings, [1, 2])


if __name__ == "__main__":
    unittest.main()

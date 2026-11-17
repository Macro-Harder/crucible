"""Pins for fix wave 20, builder b4, group 4, MOD-14 family.

Rows R20-002, R20-007, R20-030, and R20-069 of the Round 20
register. Every distinguishing pin fails or errors on the
pristine code for its charged defect and passes after the
cure; the plain controls pass before and after.


Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

Pins for fix wave 21, builder b4, group 4, MOD-10 family.

Rows R21-005, R21-006, R21-007, and R21-008 of the Round 21
register, under settlement S-16. Every distinguishing pin
hands the charged act the handing its row charges, judged on
its stored form at the act, and fails or errors on the
pristine code for that defect. The plain controls pass
before and after the cure.
"""


import unittest
from crucible import mod14
from crucible.mod14 import NamedShellFailure
import crucible.mod01 as mod01
import crucible.mod10 as mod10


class BoolLiar:
    """A stored object whose truth reading answers the
    opposite of the value it stores."""

    def __init__(self, stored):
        self.stored = stored

    def __bool__(self):
        return not self.stored


class RaiseBool:
    """A stored object whose truth reading raises."""

    def __bool__(self):
        raise RuntimeError("armed truth reading")


class StrLie(str):
    """A text value storing one word whose string and repr
    readings answer another word."""

    def __new__(cls, stored, lie):
        obj = str.__new__(cls, stored)
        obj._lie = lie
        return obj

    def __str__(self):
        return self._lie

    def __repr__(self):
        return self._lie


class RaiseStr(str):
    """A text value whose string and repr readings raise."""

    def __str__(self):
        raise RuntimeError("armed string reading")

    def __repr__(self):
        raise RuntimeError("armed repr reading")


class LieRepr:
    """A plain object whose repr and string readings answer
    a stated different text."""

    def __init__(self, lie):
        self._lie = lie

    def __repr__(self):
        return self._lie

    def __str__(self):
        return self._lie


class ArmedKey:
    """A dict key whose hash reading raises once armed."""

    def __init__(self, name):
        self.name = name
        self.armed = False

    def __hash__(self):
        if self.armed:
            raise RuntimeError("armed hash reading")
        return hash(self.name)

    def __eq__(self, other):
        return self is other


class ArmedStrKey(str):
    """A text key whose hash reading raises once armed."""

    armed = False

    def __hash__(self):
        if self.armed:
            raise RuntimeError("armed hash reading")
        return str.__hash__(self)


def _armed_record(key, value):
    record = {key: value}
    key.armed = True
    return record


class TestR20002DualRuleMarks(unittest.TestCase):
    def test_synthetic_bool_liar_storing_true_admitted(self):
        families = [{
            "synthetic": BoolLiar(True),
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_paired_counts_on_stored_marks_not_supplied_truth(self):
        families = [{
            "synthetic": True,
            "retained_under_first_rule": BoolLiar(True),
            "retained_under_second_rule": BoolLiar(False),
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 1})

    def test_raising_truth_at_synthetic_mark_no_bare_escape(self):
        families = [{
            "synthetic": RaiseBool(),
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_raising_truth_at_retained_marks_no_bare_escape(self):
        families = [{
            "synthetic": True,
            "retained_under_first_rule": RaiseBool(),
            "retained_under_second_rule": RaiseBool(),
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 1})

    def test_control_plain_marks(self):
        refused = [{"synthetic": False,
                    "retained_under_first_rule": True}]
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(refused)
        families = [{
            "synthetic": True,
            "retained_under_first_rule": True,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 1, "second_rule_retained": 0})

    def test_control_stored_text_and_number_marks(self):
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": ""}])
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": {}}])
        with self.assertRaises(NamedShellFailure):
            mod14.dual_rule_retention_simulation(
                [{"synthetic": 0}])
        result = mod14.dual_rule_retention_simulation([{
            "synthetic": "yes",
            "retained_under_first_rule": 0,
            "retained_under_second_rule": 2,
        }])
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 0, "second_rule_retained": 1})

    def test_control_bool_liar_storing_false_also_present(self):
        families = [{
            "synthetic": BoolLiar(False),
            "retained_under_first_rule": False,
            "retained_under_second_rule": False,
        }]
        result = mod14.dual_rule_retention_simulation(families)
        self.assertEqual(result["paired_field"], {
            "first_rule_retained": 0, "second_rule_retained": 0})


class TestR20007PlainStoredCopy(unittest.TestCase):
    def test_armed_hash_key_carried_whole(self):
        key = ArmedKey("k")
        record = _armed_record(key, "v")
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(len(copied), 1)
        self.assertEqual(list(copied.values()), ["v"])

    def test_armed_text_key_carried_under_numbered_form(self):
        key = ArmedStrKey("field")
        record = _armed_record(key, 7)
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(len(copied), 1)
        self.assertEqual(list(copied.values()), [7])
        carried_key = list(copied.keys())[0]
        self.assertIsInstance(carried_key, str)
        self.assertIn("(carried key 2)", str.__str__(carried_key))

    def test_flag_evaluation_delegation_reached_on_armed_key(self):
        key = ArmedKey("extra")
        record = {"retention_tier": "Tier 2"}
        record[key] = "x"
        key.armed = True
        result = mod14.flag_evaluation(
            record, inputs={}, outcome=None, tier=None)
        self.assertIn("flag_evaluation", result)

    def test_control_plain_record_copied_whole(self):
        record = {"a": 1, "b": {"nested": True}}
        copied = mod14._plain_stored_copy(record)
        self.assertEqual(copied, record)
        self.assertIsNot(copied, record)

    def test_control_no_mapping_form_stands_as_itself(self):
        handed = [1, 2]
        self.assertIs(mod14._plain_stored_copy(handed), handed)


class TestR20030SafeTextSites(unittest.TestCase):
    def test_screen_pilot_key_sentence_names_stored_key(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(
                "timing", [StrLie("money", "CLEAN-TEXT")])
        message = str(caught.exception)
        self.assertIn("pilot confined label: money", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_pilot_use_sentence_names_stored_use(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(
                StrLie("bogus", "CLEAN-TEXT"), {"figure": 1})
        message = str(caught.exception)
        self.assertIn("procedure rates: bogus", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_unknown_command_sentence_names_stored_command(self):
        result = mod14.run_command(StrLie("boguscmd", "CLEAN-TEXT"))
        message = result["failure"]
        self.assertIn("unknown shell command: boguscmd", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_call_log_key_sentence_names_stored_key(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.outside_call_check(
                {}, {StrLie("boguskey", "CLEAN-TEXT"): []})
        message = str(caught.exception)
        self.assertIn("cannot read: boguskey", message)
        self.assertNotIn("CLEAN-TEXT", message)

    def test_raising_text_use_names_stored_use(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run(RaiseStr("bogus"), {"figure": 1})
        message = str(caught.exception)
        self.assertIn("procedure rates: bogus", message)
        self.assertNotIn("object at", message)

    def test_raising_text_command_names_stored_command(self):
        result = mod14.run_command(RaiseStr("boguscmd"))
        message = result["failure"]
        self.assertIn("unknown shell command: boguscmd", message)
        self.assertNotIn("object at", message)

    def test_bytes_command_names_stored_text(self):
        result = mod14.run_command(b"bogus-cmd")
        message = result["failure"]
        self.assertIn("unknown shell command: bogus-cmd", message)
        self.assertNotIn("b'bogus-cmd'", message)

    def test_bytes_call_log_key_names_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.outside_call_check({}, {b"boguskey": []})
        message = str(caught.exception)
        self.assertIn("cannot read: boguskey", message)
        self.assertNotIn("b'boguskey'", message)

    def test_control_plain_use_and_command_named(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.pilot_run("bogus", {"figure": 1})
        self.assertIn("procedure rates: bogus", str(caught.exception))
        result = mod14.run_command("bogus-cmd")
        self.assertIn("unknown shell command: bogus-cmd",
                      result["failure"])


class TestR20069WeeklyIdentifierSentence(unittest.TestCase):
    def _records(self, identifier):
        return [{"week": "W1",
                 "headline_unit_identifiers": [identifier]}]

    def test_lying_text_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(StrLie("bogus-id", "u999")), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("u999", message)

    def test_lying_repr_object_named_on_its_form_not_its_reading(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(LieRepr("u999")), "W1")
        message = str(caught.exception)
        self.assertNotIn("u999", message)
        self.assertIn("LieRepr", message)

    def test_raising_text_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(RaiseStr("bogus-id")), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("object at", message)

    def test_bytes_identifier_named_on_stored_text(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records(b"bogus-id"), "W1")
        message = str(caught.exception)
        self.assertIn("'bogus-id'", message)
        self.assertNotIn("b'bogus-id'", message)

    def test_control_plain_number_identifier_named(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(self._records(123), "W1")
        self.assertIn("unvalidated contents: 123",
                      str(caught.exception))

    def test_control_plain_text_identifier_named_in_repr_dress(self):
        with self.assertRaises(NamedShellFailure) as caught:
            mod14.weekly_headline_count(
                self._records("bogus-id"), "W1")
        self.assertIn("'bogus-id'", str(caught.exception))

    def test_control_valid_identifiers_counted(self):
        records = [{"week": "W1",
                    "headline_unit_identifiers": ["u1", "u2", "u1"]}]
        self.assertEqual(
            mod14.weekly_headline_count(records, "W1"), 2)


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class EqTrueStr(str):
    """A text value whose equality reading answers True
    against every value and whose inequality reading
    answers False, whatever text it stores."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


class EqFalseStr(str):
    """A text value whose equality reading answers False
    against every value and whose inequality reading
    answers True, whatever text it stores."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class EqRaisingStr(str):
    """A text value whose equality and inequality readings
    raise, whatever text it stores."""

    def __eq__(self, other):
        raise RuntimeError("equality boom")

    def __ne__(self, other):
        raise RuntimeError("equality boom")

    __hash__ = str.__hash__


class CollidingKey(str):
    """A text key storing one text, hashing as another
    stated text, whose equality reading raises once the
    key stands armed. While disarmed its equality reading
    answers on the text it stores, so a handing carrying
    it can stand built whole before it stands armed."""

    def __new__(cls, stored, target):
        obj = str.__new__(cls, stored)
        obj.target = target
        obj.armed = False
        return obj

    def __hash__(self):
        return str.__hash__(self.target)

    def __eq__(self, other):
        if self.armed:
            raise RuntimeError("colliding key equality boom")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if self.armed:
            raise RuntimeError("colliding key equality boom")
        return str.__ne__(self, other)


def _components(viewer="viewer-1"):
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


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


class TestR21005RederiveFormOnly(Base):
    """Row R21-005: rederive_regime_classification judges
    the form field on the text it stores."""

    def _record(self, form_value):
        return {
            "form": form_value,
            "joint_outcome_components": [1, 2, 3, 4],
        }

    def test_always_equal_bogus_form_computes(self):
        result = mod10.rederive_regime_classification(
            [self._record(EqTrueStr("bogus"))])
        self.assertEqual(
            result["classification"],
            "rederived_from_daily_aggregates")
        self.assertEqual(result["component_totals"], [1, 2, 3, 4])
        self.assertEqual(result["days"], 1)

    def test_always_unequal_form_only_stands_form_only(self):
        result = mod10.rederive_regime_classification(
            [self._record(EqFalseStr("form_only"))])
        self.assertIsNone(result["classification"])
        self.assertEqual(result["form"], mod10.FORM_ONLY)
        self.assertEqual(result["days"], 0)

    def test_raising_form_only_stands_form_only(self):
        result = mod10.rederive_regime_classification(
            [self._record(EqRaisingStr("form_only"))])
        self.assertIsNone(result["classification"])
        self.assertEqual(result["form"], mod10.FORM_ONLY)
        self.assertEqual(result["days"], 0)

    def test_raising_bogus_form_computes(self):
        result = mod10.rederive_regime_classification(
            [self._record(EqRaisingStr("bogus"))])
        self.assertEqual(
            result["classification"],
            "rederived_from_daily_aggregates")
        self.assertEqual(result["component_totals"], [1, 2, 3, 4])

    def test_plain_form_only_control(self):
        result = mod10.rederive_regime_classification(
            [self._record("form_only")])
        self.assertIsNone(result["classification"])
        self.assertEqual(result["form"], mod10.FORM_ONLY)
        self.assertEqual(result["days"], 0)

    def test_plain_computed_control(self):
        record = {"joint_outcome_components": [1, 2, 3, 4]}
        result = mod10.rederive_regime_classification([record])
        self.assertEqual(
            result["classification"],
            "rederived_from_daily_aggregates")
        self.assertEqual(result["component_totals"], [1, 2, 3, 4])


class TestR21006RejectedCheckpointWrites(Base):
    """Row R21-006: rejected_checkpoint_writes judges the
    handed run identifier on the text it stores."""

    RUN = "run-b4-rejected"

    def setUp(self):
        super().setUp()
        manifest = {
            "run_identifier": self.RUN, "simulated_day": 1}
        mod10.retain_checkpoint(dict(manifest))
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(dict(manifest))

    def test_false_equality_same_run_returns_entry(self):
        entries = mod10.rejected_checkpoint_writes(
            EqFalseStr(self.RUN))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["run_id"], self.RUN)

    def test_true_equality_other_run_returns_no_entry(self):
        entries = mod10.rejected_checkpoint_writes(
            EqTrueStr("run-b4-other"))
        self.assertEqual(entries, [])

    def test_raising_equality_same_run_returns_entry(self):
        entries = mod10.rejected_checkpoint_writes(
            EqRaisingStr(self.RUN))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["run_id"], self.RUN)

    def test_plain_same_run_control(self):
        entries = mod10.rejected_checkpoint_writes(self.RUN)
        self.assertEqual(len(entries), 1)

    def test_plain_other_run_control(self):
        entries = mod10.rejected_checkpoint_writes("run-b4-other")
        self.assertEqual(entries, [])

    def test_plain_no_identifier_control(self):
        entries = mod10.rejected_checkpoint_writes()
        self.assertEqual(len(entries), 1)


class TestR21007ResumeFromCheckpoint(Base):
    """Row R21-007: resume_from_checkpoint selects its
    candidate buckets on the stored identifier form."""

    RUN = "run-b4-resume"
    MANIFEST = {
        "run_identifier": RUN, "simulated_day": 3,
        "state_reference": "state-1",
    }

    def setUp(self):
        super().setUp()
        mod10.retain_checkpoint(dict(self.MANIFEST))

    def test_false_equality_differing_checkpoint_refused(self):
        handed = dict(self.MANIFEST)
        handed["run_identifier"] = EqFalseStr(self.RUN)
        handed["state_reference"] = "state-forged"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)

    def test_true_equality_other_run_resumes_unchecked(self):
        handed = dict(self.MANIFEST)
        handed["run_identifier"] = EqTrueStr("run-b4-other")
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(
            str.__str__(resumed["run_identifier"]), "run-b4-other")
        self.assertEqual(resumed["state_reference"], "state-1")

    def test_raising_equality_matching_checkpoint_resumes(self):
        handed = dict(self.MANIFEST)
        handed["run_identifier"] = EqRaisingStr(self.RUN)
        resumed = mod10.resume_from_checkpoint(handed)
        self.assertEqual(
            str.__str__(resumed["run_identifier"]), self.RUN)
        self.assertEqual(resumed["simulated_day"], 3)
        self.assertEqual(resumed["state_reference"], "state-1")

    def test_plain_matching_control(self):
        resumed = mod10.resume_from_checkpoint(dict(self.MANIFEST))
        self.assertEqual(resumed, self.MANIFEST)

    def test_plain_tampered_control(self):
        handed = dict(self.MANIFEST)
        handed["state_reference"] = "state-forged"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(handed)

    def test_plain_orphan_control(self):
        handed = {
            "run_identifier": "run-b4-orphan", "simulated_day": 9,
            "state_reference": "state-9",
        }
        resumed = mod10.resume_from_checkpoint(dict(handed))
        self.assertEqual(resumed, handed)


class TestR21008BuildJointOutcomeVector(Base):
    """Row R21-008: build_joint_outcome_vector reads the
    handed components and their viewer identifier through
    the stored key form."""

    def test_colliding_key_on_components_builds(self):
        extra = CollidingKey(
            "zzz-extra", "attacker_controlled_share")
        components = {extra: "extra value"}
        components.update(_components())
        extra.armed = True
        record = mod10.build_joint_outcome_vector(
            components=components,
            divergence_companion={"nil_divergence_components": []})
        self.assertTrue(mod01.validate_record("15", record))
        for field in mod01.JOINT_OUTCOME_COMPONENT_PARTS:
            self.assertEqual(
                record[field]["viewer_identifier"], "viewer-1")

    def test_colliding_viewer_key_missing_part_named_refusal(self):
        components = _components()
        inner = components["attacker_controlled_share"]
        del inner["numerator_kind"]
        extra = CollidingKey("zzz-other", "viewer_identifier")
        target = {extra: "extra value"}
        target.update(inner)
        components["attacker_controlled_share"] = target
        extra.armed = True
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=components,
                divergence_companion={
                    "nil_divergence_components": []})

    def test_plain_valid_control(self):
        record = mod10.build_joint_outcome_vector(
            components=_components(),
            divergence_companion={"nil_divergence_components": []})
        self.assertTrue(mod01.validate_record("15", record))

    def test_plain_missing_part_control(self):
        components = _components()
        del components["farm_share_of_reputation_mass"][
            "viewer_identifier"]
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=components,
                divergence_companion={
                    "nil_divergence_components": []})

    def test_plain_mixed_viewers_control(self):
        components = _components()
        components["honest_loss_rate"][
            "viewer_identifier"] = "viewer-2"
        with self.assertRaises(ValueError):
            mod10.build_joint_outcome_vector(
                components=components,
                divergence_companion={
                    "nil_divergence_components": []})


if __name__ == "__main__":
    unittest.main()

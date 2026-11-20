"""Pins for fix wave 15, Builder 6, Group 6: rows R15-046 to
R15-053 and R15-099 to R15-100, the MOD-10 direct and composed
acts (flag, retention, storage, and aggregates) with the
MOD-14 flag shell forms in the same composition.

Each pin states the charged defect in stored form: a truth,
equality, hash, get, or iteration reading the handed value
supplies standing in for the stored contents, a value in an
iterator form counted as its own stated entry, a missing
identity or hash guard at a next ring act, or a shell precheck
order that preempts or reverses the core order. Every pin
fails on the pristine tree and passes on the cured tree,
except the plain controls, which pass on both.
"""

import unittest

from crucible import mod10, mod14


class LyingLenList(list):
    """A list whose length reading answers 0 whatever it
    stores, so its truth reading answers False."""

    def __len__(self):
        return 0


class LyingLenDict(dict):
    """A dict whose length reading answers 0 whatever it
    stores, so its truth reading answers False."""

    def __len__(self):
        return 0


class LyingLenStr(str):
    """A text whose length reading answers 0 whatever it
    stores, so its truth reading answers False."""

    def __len__(self):
        return 0


class EqLie:
    """An object whose equality reading answers True against
    every value and whose inequality reading answers False."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class GetLieAggregate(dict):
    """An aggregate record whose get reading returns fabricated
    component totals, whatever it stores."""

    def get(self, key, default=None):
        if key == "joint_outcome_components":
            return [9, 9, 9, 9]
        return dict.get(self, key, default)


class FabricatingIterable:
    """An object in no container form, storing nothing, whose
    iteration yields one fabricated delivery."""

    def __init__(self, yielded):
        self._yielded = yielded

    def __iter__(self):
        return iter(self._yielded)


def valid_delivery(day=1, viewer="viewer-1"):
    return {
        "simulated_day": day,
        "viewer_id": viewer,
        "joint_outcome_components": [1, 2, 3, 4],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 0,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0},
    }


def met_record():
    return {
        "later_evaluation": {
            "conditions": [1, 2, 3],
            "inputs": {"flag_conditions_fired": ["condition-1"]},
            "outcome": "promote",
        },
        "summary_record_written": True,
        "retained_forms_pointed_to": ["final_checkpoint"],
    }


def flag_record(run_id, tier="Tier 1"):
    return {"run_id": run_id, "retention_tier": tier}


class B6Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR15046RetentionTruthReadings(B6Base):
    def test_conditions_judged_by_stored_contents(self):
        record = met_record()
        record["later_evaluation"]["conditions"] = LyingLenList(
            [1, 2, 3])
        self.assertTrue(mod10.retention_met(record))

    def test_inputs_judged_by_stored_contents(self):
        record = met_record()
        record["later_evaluation"]["inputs"] = LyingLenDict(
            {"flag_conditions_fired": ["condition-1"]})
        self.assertTrue(mod10.retention_met(record))

    def test_retained_forms_judged_by_stored_contents(self):
        record = met_record()
        record["retained_forms_pointed_to"] = LyingLenList(
            ["final_checkpoint"])
        self.assertTrue(mod10.retention_met(record))

    def test_declaration_only_judged_by_stored_contents(self):
        record = met_record()
        record["declaration_only"] = LyingLenStr("declared")
        self.assertFalse(mod10.retention_met(record))

    def test_annotation_link_judged_by_stored_contents(self):
        checkpoint = {
            "annotation_link_identifier": LyingLenStr("link-1"),
            "annotation_link": "fallback",
        }
        self.assertEqual(
            mod10.annotation_link_at_checkpoint(checkpoint),
            "link-1")

    def test_plain_met_control(self):
        self.assertTrue(mod10.retention_met(met_record()))

    def test_plain_declaration_only_control(self):
        record = met_record()
        record["declaration_only"] = "declared"
        self.assertFalse(mod10.retention_met(record))


class TestR15047FlagIteratorFired(B6Base):
    def test_empty_generator_fires_nothing_at_direct_act(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-047a"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired":
                        (item for item in ())})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_empty_list_iterator_fires_nothing(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-047b"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired": iter([])})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_exhausted_generator_fires_nothing(self):
        generator = (item for item in ("condition-1",))
        for _ in generator:
            pass
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-047c"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired": generator})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_empty_generator_fires_nothing_at_shell(self):
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                flag_record("b6-047d"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired":
                        (item for item in ())})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_record_fallback_generator_fires_nothing(self):
        record = flag_record("b6-047e")
        record["flag_conditions_fired"] = (item for item in ())
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2",
                inputs={})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_generator_yielding_a_condition_states_no_stored_form(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-047f"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired":
                        (item for item in ("condition-1",))})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_plain_empty_list_control(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-047g"), outcome="promote",
                tier="Tier 2",
                inputs={"flag_conditions_fired": []})
        self.assertIn("no stated flag condition",
                      str(caught.exception))


class TestR15048FlagEqualityReadings(B6Base):
    def test_actor_object_is_no_person_at_direct_act(self):
        result = mod10.apply_flag_evaluation(
            flag_record("b6-048a"), actor=EqLie())
        self.assertIn("flag_evaluation", result)

    def test_actor_object_is_no_person_at_shell(self):
        result = mod14.flag_evaluation(
            flag_record("b6-048b"), actor=EqLie())
        self.assertIn("flag_evaluation", result)

    def test_outcome_object_states_no_demote_at_direct_act(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-048c"), outcome=EqLie(),
                tier="Tier 2",
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("outside the stated vocabulary",
                      str(caught.exception))

    def test_outcome_object_states_no_demote_at_shell(self):
        with self.assertRaises(ValueError) as caught:
            mod14.flag_evaluation(
                flag_record("b6-048d"), outcome=EqLie(),
                tier="Tier 2",
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("outside the stated vocabulary",
                      str(caught.exception))

    def test_plain_person_control(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-048e"), actor="person")
        self.assertIn("by a person is barred",
                      str(caught.exception))

    def test_plain_demote_control(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-048f"), outcome="demote")
        self.assertIn("never demotes", str(caught.exception))


class TestR15049FlagTierHashLimbs(B6Base):
    def test_handed_list_tier_named_at_direct_act(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-049a"), outcome="promote",
                tier=["Tier 2"],
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("outside the tiers the rule names",
                      str(caught.exception))

    def test_handed_dict_tier_named_at_direct_act(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-049b"), outcome="promote",
                tier={"tier": "Tier 2"},
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("outside the tiers the rule names",
                      str(caught.exception))

    def test_stored_list_tier_no_bare_error_at_direct_act(self):
        record = flag_record("b6-049c", tier=["Tier 1"])
        result = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_stored_list_tier_no_bare_error_at_shell(self):
        record = flag_record("b6-049d", tier=["Tier 1"])
        result = mod14.flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertEqual(result["retention_tier"], "Tier 2")

    def test_plain_bogus_tier_control(self):
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                flag_record("b6-049e"), outcome="promote",
                tier="Tier 9",
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("outside the tiers the rule names",
                      str(caught.exception))


class TestR15050RederiveReadings(B6Base):
    def test_aggregate_judged_by_stored_contents(self):
        record = GetLieAggregate({
            "joint_outcome_components": [1, 2, 3, 4],
            "component_denominators": [1, 1, 1, 1],
        })
        result = mod10.rederive_regime_classification([record])
        self.assertIsNone(result)

    def test_generator_of_valid_aggregates_classifies(self):
        record = {
            "joint_outcome_components": [1, 2, 3, 4],
            "component_denominators": [1, 1, 1, 1],
        }
        generator = (item for item in (record,))
        result = mod10.rederive_regime_classification(generator)
        self.assertIsNone(result)

    def test_plain_list_control(self):
        record = {
            "joint_outcome_components": [1, 2, 3, 4],
            "component_denominators": [1, 1, 1, 1],
        }
        result = mod10.rederive_regime_classification([record])
        self.assertIsNone(result)


class TestR15051AggregateFallbackIteration(B6Base):
    def test_fabricated_delivery_not_retained(self):
        deliveries = FabricatingIterable(
            [valid_delivery(day=99, viewer="fabricated")])
        count = mod10.retain_daily_aggregate_deliveries(
            "b6-051a", deliveries)
        self.assertEqual(count, 0)
        aggregates = mod10.daily_aggregates_for_run("b6-051a")
        self.assertNotIn(
            "fabricated",
            [item.get("viewer_id") for item in aggregates])

    def test_generator_control_retained(self):
        generator = (item for item in (valid_delivery(),))
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-051b", generator)
        self.assertIn(
            "stand impossible in the form the module "
            "validator states", str(caught.exception))


class TestR15052AggregateComponentForms(B6Base):
    def test_set_components_refused_in_named_form(self):
        delivery = valid_delivery()
        delivery["joint_outcome_components"] = {"a", "b"}
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-052a", [delivery])
        self.assertIn("non numeric", str(caught.exception))

    def test_text_components_refused_in_named_form(self):
        delivery = valid_delivery()
        delivery["joint_outcome_components"] = "not-a-number"
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-052b", [delivery])
        self.assertIn("non numeric", str(caught.exception))

    def test_set_denominators_refused_in_named_form(self):
        delivery = valid_delivery()
        delivery["component_denominators"] = {"a", "b"}
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-052c", [delivery])
        self.assertIn("non numeric", str(caught.exception))

    def test_list_components_control_refused(self):
        delivery = valid_delivery()
        delivery["joint_outcome_components"] = ["x", 2, 3, 4]
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-052d", [delivery])
        self.assertIn("non numeric", str(caught.exception))

    def test_numeric_set_components_control_retained(self):
        delivery = valid_delivery()
        delivery["joint_outcome_components"] = {1, 2, 3, 4}
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                "b6-052e", [delivery])
        self.assertIn(
            "stand impossible in the form the module "
            "validator states", str(caught.exception))


class TestR15053NextRingGuards(B6Base):
    def test_aggregate_list_run_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                ["run"], [valid_delivery()])
        self.assertIn("unhashable", str(caught.exception))

    def test_aggregate_no_run_identifier_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_daily_aggregate_deliveries(
                None, [valid_delivery()])
        self.assertIn("no run identifier", str(caught.exception))

    def test_gc08_retain_list_owner_named(self):
        with self.assertRaises(ValueError) as caught:
            mod10.retain_gc08_record(
                "call_log", {"calls": []}, ["owner"])
        self.assertIn("unhashable", str(caught.exception))

    def test_gc08_lookup_list_owner_named_failure(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", ["owner"])

    def test_gc08_absent_owner_control(self):
        with self.assertRaises(mod10.LookupFailure):
            mod10.gc08_record("call_log", "absent-owner")

    def test_deferred_firing_two_list_identifier_named(self):
        record = {"run_id": ["run"], "retention_tier": "Tier 1"}
        with self.assertRaises(ValueError) as caught:
            mod10.apply_deferred_evaluation(
                record, 2, inputs={"flag_conditions_fired":
                                   ["condition-1"]},
                outcome="promote")
        self.assertIn("identity less summary record",
                      str(caught.exception))
        self.assertIn("unhashable", str(caught.exception))

    def test_deferred_firing_one_control_named(self):
        record = {"run_id": ["run"], "retention_tier": "Tier 1"}
        with self.assertRaises(ValueError) as caught:
            mod10.apply_deferred_evaluation(
                record, 1, inputs={"flag_conditions_fired":
                                   ["condition-1"]},
                outcome="promote")
        self.assertIn("identity less summary record",
                      str(caught.exception))


class TestR15099ShellDemotePrecheckOrder(B6Base):
    def test_no_inputs_demotes_at_shell(self):
        record = flag_record("b6-099a", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote", tier="Tier 1")
        self.assertIn("the stated tier stands below the record tier",
                      str(caught.exception))

    def test_text_inputs_demote_at_shell(self):
        record = flag_record("b6-099b", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote", tier="Tier 1",
                inputs="text")
        self.assertIn("the stated tier stands below the record tier",
                      str(caught.exception))

    def test_empty_fired_demote_at_shell(self):
        record = flag_record("b6-099c", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote", tier="Tier 1",
                inputs={"flag_conditions_fired": []})
        self.assertIn("the stated tier stands below the record tier",
                      str(caught.exception))

    def test_sound_inputs_demote_control(self):
        record = flag_record("b6-099d", tier="Tier 2")
        with self.assertRaises(
                (ValueError, mod14.NamedShellFailure)) as caught:
            mod14.flag_evaluation(
                record, outcome="promote", tier="Tier 1",
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("the stated tier stands below the record tier",
                      str(caught.exception))


class TestR15100ShellNoTierOrder(B6Base):
    def test_no_tier_and_no_inputs_answers_inputs_at_shell(self):
        record = flag_record("b6-100a", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(record, outcome="promote")
        self.assertIn("no inputs supplied", str(caught.exception))

    def test_no_tier_and_text_inputs_answers_inputs_form(self):
        record = flag_record("b6-100b", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote", inputs="text")
        self.assertIn("standing in no record form",
                      str(caught.exception))

    def test_no_tier_and_empty_fired_answers_condition(self):
        record = flag_record("b6-100c", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote",
                inputs={"flag_conditions_fired": []})
        self.assertIn("no stated flag condition",
                      str(caught.exception))

    def test_no_tier_with_sound_inputs_control(self):
        record = flag_record("b6-100d", tier="Tier 2")
        with self.assertRaises(mod14.NamedShellFailure) as caught:
            mod14.flag_evaluation(
                record, outcome="promote",
                inputs={"flag_conditions_fired": ["condition-1"]})
        self.assertIn("no tier stands refused",
                      str(caught.exception))


if __name__ == "__main__":
    unittest.main()

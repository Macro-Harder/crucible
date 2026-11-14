"""Step 15 rerun Round 2 fix wave 2 pins for Fix Builder 2, MOD-10.

Each test pins one register item from the Round 2 register
(R2-001, R2-005, R2-006, R2-007, R2-008, R2-009, R2-015 to
R2-020, R2-033, R2-051, R2-052, R2-053, R2-058, R2-059) on the
MOD-10 surface in crucible/mod10.py. Tests reset the module
stores around themselves so their standing does not depend on
suite order. Values are simulated and test values only.
"""
import unittest

import crucible.mod10 as mod10


class B2Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()

    def view_record(self, contents):
        return {
            "run_identifier": "run-b2-view",
            "viewer_identifier": "viewer-1",
            "simulated_day": 5,
            "scheduling_position_identifier": "position-1",
            "rule_version_set": "rule-set-1",
            "view_contents": contents,
            "reputation_and_band_values": {"band": "stated"},
            "graph_position_as_seen": "stated",
            "first_seen_day_per_record": {"item": 3},
            "delay_applied_per_record": {"item": 1},
            "completeness_state": "complete",
            "building_component": "Recorder",
            "delivering_contract": "stated",
            "selection_rule_version": "rule-set-1",
        }

    def deep_chain(self, depth, leaf=None):
        node = leaf if leaf is not None else {"leaf": 1}
        for _ in range(depth):
            node = {"a": node}
        return node


class EvilList(list):
    def __iter__(self):
        return iter(())


class EvilTuple(tuple):
    def __iter__(self):
        return iter(())


class TestR2001BaseIteration(B2Base):
    def test_money_search_reads_list_parts_by_base(self):
        store = mod10.new_store()
        record = {"run_id": "run-r2001-a",
                  "items": EvilList([{"amount": 500, "currency": "USD"}])}
        with self.assertRaises(ValueError):
            store.retain_run_record(record)

    def test_money_search_reads_tuple_parts_by_base(self):
        store = mod10.new_store()
        record = {"run_id": "run-r2001-b",
                  "items": EvilTuple(({"realmoney": 500},))}
        with self.assertRaises(ValueError):
            store.retain_run_record(record)

    def test_barred_search_reads_list_parts_by_base(self):
        record = self.view_record(EvilList([{"ground_truth": "x"}]))
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_barred_search_reads_tuple_parts_by_base(self):
        record = self.view_record(EvilTuple(({"membership": "x"},)))
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)


class DeepcopyBomb:
    def __deepcopy__(self, memo):
        return {"realmoney": 999}


class TestR2005SafeCopy(B2Base):
    def test_retained_copy_no_part_can_direct(self):
        store = mod10.new_store()
        store.retain_run_record(
            {"run_id": "run-r2005", "payload": DeepcopyBomb()})
        readback = store.read_run_record("run-r2005")
        self.assertNotEqual(readback["payload"], {"realmoney": 999})
        self.assertFalse(mod10._carries_real_money_field(readback))


class TestR2006CommonBarredMap(B2Base):
    def assert_barred(self, key):
        record = self.view_record({key: 1})
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_dze_lower_as_s(self):
        self.assert_barred("member\u0455hip")

    def test_dze_upper_as_s(self):
        self.assert_barred("\u0405leeper")

    def test_ha_lower_as_h(self):
        self.assert_barred("is_\u04bbonest")

    def test_ha_upper_as_h(self):
        self.assert_barred("is_\u04baonest")

    def test_theta_as_t(self):
        self.assert_barred("ground_\u03b8ruth")

    def test_phi_as_f(self):
        self.assert_barred("is_\u03c6arm")


class TestR2007SisterGuards(B2Base):
    def sisters(self):
        deep = self.deep_chain(150)
        return [
            ("event_log",
             lambda: mod10.retain_event_log_entry(
                 {"run_identifier": "run-r2007", "payload": deep})),
            ("daily_snapshot",
             lambda: mod10.retain_daily_snapshot(
                 {"run_identifier": "run-r2007", "payload": deep})),
            ("checkpoint",
             lambda: mod10.retain_checkpoint(
                 {"run_identifier": "run-r2007", "simulated_day": 1,
                  "payload": deep})),
            ("summary",
             lambda: mod10.write_summary_record(
                 {"run_id": "run-r2007", "payload": deep})),
            ("flag",
             lambda: mod10.apply_flag_evaluation(
                 {"run_id": "run-r2007", "payload": deep})),
        ]

    def test_sisters_refuse_deep_shape(self):
        for name, act in self.sisters():
            with self.subTest(surface=name):
                with self.assertRaises(ValueError) as caught:
                    act()
                self.assertIn("deep or cyclic", str(caught.exception))

    def test_sisters_refuse_cyclic_shape(self):
        for name in ("event_log", "daily_snapshot", "checkpoint",
                     "summary", "flag"):
            with self.subTest(surface=name):
                cyclic = {}
                cyclic["self"] = cyclic
                if name == "event_log":
                    act = lambda: mod10.retain_event_log_entry(
                        {"run_identifier": "run-r2007c", "payload": cyclic})
                elif name == "daily_snapshot":
                    act = lambda: mod10.retain_daily_snapshot(
                        {"run_identifier": "run-r2007c", "payload": cyclic})
                elif name == "checkpoint":
                    act = lambda: mod10.retain_checkpoint(
                        {"run_identifier": "run-r2007c",
                         "simulated_day": 1, "payload": cyclic})
                elif name == "summary":
                    act = lambda: mod10.write_summary_record(
                        {"run_id": "run-r2007c", "payload": cyclic})
                else:
                    act = lambda: mod10.apply_flag_evaluation(
                        {"run_id": "run-r2007c", "payload": cyclic})
                with self.assertRaises(ValueError) as caught:
                    act()
                self.assertIn("deep or cyclic", str(caught.exception))

    def test_event_log_refuses_depth_2000_as_value_error(self):
        with self.assertRaises(ValueError):
            mod10.retain_event_log_entry(
                {"run_identifier": "run-r2007d",
                 "payload": self.deep_chain(2000)})


class TestR2008ActorNormalisation(B2Base):
    def test_person_dresses_refused_at_core(self):
        for actor in ("Person", "PERSON", "  person  ", "the person",
                      "a person", "person"):
            with self.subTest(actor=actor):
                record = {"run_id": "run-r2008",
                          "retention_tier": "Tier 1",
                          "flag_conditions_fired": ["c1"]}
                with self.assertRaises(ValueError):
                    mod10.apply_flag_evaluation(
                        record, outcome="promote", tier="Tier 2",
                        actor=actor,
                        inputs={"flag_conditions_fired": ["c1"]})

    def test_program_actor_still_promotes(self):
        record = {"run_id": "run-r2008p", "retention_tier": "Tier 1",
                  "flag_conditions_fired": ["c1"]}
        updated = mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2", actor="program",
            inputs={"flag_conditions_fired": ["c1"]})
        self.assertEqual(updated["retention_tier"], "Tier 2")


class TestR2009FrozensetDepth(B2Base):
    def test_frozenset_chain_past_bound_refused(self):
        chain = frozenset()
        for _ in range(150):
            chain = frozenset([chain])
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-r2009", "chain": chain})

    def test_frozenset_chain_within_bound_retained(self):
        chain = frozenset()
        for _ in range(50):
            chain = frozenset([chain])
        store = mod10.new_store()
        store.retain_run_record({"run_id": "run-r2009b", "chain": chain})
        self.assertTrue(store.has_run_record("run-r2009b"))


class TestR2015ToR2020FoldLimbs(B2Base):
    def test_r2015_es_both_readings_in_one_anchor_name(self):
        variants = mod10._fold_variants("anchor_\u0441\u0441enario_values")
        self.assertIn("anchorscenariovalues", variants)

    def test_r2015_es_mixed_anchor_and_scenario(self):
        variants = mod10._fold_variants("an\u0441hor_\u0441cenario_values")
        self.assertIn("anchorscenariovalues", variants)

    def test_r2016_upsilon_both_readings_in_one_currency_key(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r2016a", "amount": 500,
                 "c\u03c5rrenc\u03c5": "USD"})

    def test_r2016_cyrillic_u_both_readings_in_one_currency_key(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r2016b", "amount": 500,
                 "c\u0443rrenc\u0443": "USD"})

    def test_r2017_armenian_vo_un_reading_in_amount_key(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r2017", "amo\u0578t": 500,
                 "currency": "USD"})

    def test_r2018_en_h_reading_in_anchor_name_stands(self):
        variants = mod10._fold_variants("anc\u043dor_scenario_values")
        self.assertIn("anchorscenariovalues", variants)

    def test_r2019_cherokee_marker_refused(self):
        key = ("\u13d2\u13ac\u13aa\u13de\u13b7\u13be\u13c1"
               "\u13ac\u13ef")
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-r2019a", key: 500})

    def test_r2019_coptic_marker_refused(self):
        key = ("\u2ca3\u2c89\u2c81\u2c97\u2c99\u2c9f\u2c9b"
               "\u2c89\u2ca9")
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-r2019b", key: 500})

    def test_r2019_mixed_cherokee_marker_refused(self):
        key = ("\u13d2\u1d07@\u029f\u1d0d\u0585\u0578"
               "\u1d07\u028f")
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record({"run_id": "run-r2019c", key: 500})

    def test_r2020_cent_sign_as_c_in_currency_key(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r2020a", "amount": 500,
                 "\u00a2urrency": "USD"})

    def test_r2020_plus_sign_as_t_in_amount_key(self):
        store = mod10.new_store()
        with self.assertRaises(ValueError):
            store.retain_run_record(
                {"run_id": "run-r2020b", "amoun+": 500,
                 "currency": "USD"})

    def test_r2020_section_sign_as_s_in_anchor_name(self):
        variants = mod10._fold_variants("anchor_\u00a7cenario_values")
        self.assertIn("anchorscenariovalues", variants)

    def test_r2020_cent_sign_as_c_in_anchor_name(self):
        variants = mod10._fold_variants("an\u00a2hor_scenario_values")
        self.assertIn("anchorscenariovalues", variants)


class TestR2033ResumeStoreKind(B2Base):
    def test_enumerated_copy_resumes_from_its_own_store(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r2033", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": "run-r2033", "simulated_day": 1,
             "state_reference": "pilot-state"}, store_kind="pilot")
        pilot_copy = mod10.checkpoints_for_run(
            "run-r2033", store_kind="pilot")[0]
        resumed = mod10.resume_from_checkpoint(pilot_copy)
        self.assertEqual(resumed["state_reference"], "pilot-state")
        sweep_copy = mod10.checkpoints_for_run(
            "run-r2033", store_kind="sweep")[0]
        resumed = mod10.resume_from_checkpoint(sweep_copy)
        self.assertEqual(resumed["state_reference"], "sweep-state")

    def test_resume_with_explicit_store_kind(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r2033b", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": "run-r2033b", "simulated_day": 1,
             "state_reference": "pilot-state"}, store_kind="pilot")
        pilot_copy = mod10.checkpoints_for_run(
            "run-r2033b", store_kind="pilot")[0]
        resumed = mod10.resume_from_checkpoint(
            pilot_copy, store_kind="pilot")
        self.assertEqual(resumed["state_reference"], "pilot-state")
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(pilot_copy, store_kind="sweep")

    def test_tampered_copy_still_refused(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r2033c", "simulated_day": 1,
             "state_reference": "sweep-state"}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": "run-r2033c", "simulated_day": 1,
             "state_reference": "pilot-state"}, store_kind="pilot")
        tampered = mod10.checkpoints_for_run(
            "run-r2033c", store_kind="pilot")[0]
        tampered["state_reference"] = "altered-state"
        with self.assertRaises(ValueError):
            mod10.resume_from_checkpoint(tampered)


class TestR2051WiderBarredReading(B2Base):
    def test_named_composites_barred_at_mod10(self):
        for key in ("m\u03b7mb-3rship", "gr0un\u0434_tr-uth",
                    "\u1d0d3mbe_rship", "\u00a3a-b3l",
                    "m3mbe-rs\u0445ip", "i\u03c2_hon-3st"):
            with self.subTest(key=key):
                self.assertTrue(mod10._is_barred_view_key(key))


class TestR2052WholeDayForm(B2Base):
    def test_string_day_counts_as_same_day_for_uniqueness(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r2052", "simulated_day": 1,
             "state_reference": "first"})
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(
                {"run_id": "run-r2052", "simulated_day": "1",
                 "state_reference": "second"})
        rejected = mod10.rejected_checkpoint_writes("run-r2052")
        self.assertEqual(len(rejected), 1)

    def test_string_day_counts_in_close_day_set(self):
        mod10.retain_checkpoint(
            {"run_id": "run-r2052b", "simulated_day": 1})
        mod10.retain_checkpoint(
            {"run_id": "run-r2052b", "simulated_day": "2"})
        result = mod10.close_run_retention("run-r2052b", "Tier 0")
        self.assertIn(2, result["released_days"])
        self.assertEqual(mod10.checkpoints_for_run("run-r2052b"), [])


class TestR2053LeakCheckDeletedFields(B2Base):
    def test_present_at_none_still_passes(self):
        record = self.view_record({"note": "clean"})
        record["scheduling_position_identifier"] = None
        record["rule_version_set"] = None
        result = mod10.run_view_leak_check(record)
        self.assertTrue(result["reportable"])

    def test_both_fields_deleted_fails(self):
        record = self.view_record({"note": "clean"})
        del record["scheduling_position_identifier"]
        del record["rule_version_set"]
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)

    def test_one_field_deleted_fails(self):
        record = self.view_record({"note": "clean"})
        del record["rule_version_set"]
        with self.assertRaises(ValueError):
            mod10.run_view_leak_check(record)


class TestR2058StatedConditionEntry(B2Base):
    def promote(self, fired):
        record = {"run_id": "run-r2058", "retention_tier": "Tier 1",
                  "flag_conditions_fired": []}
        return mod10.apply_flag_evaluation(
            record, outcome="promote", tier="Tier 2",
            inputs={"flag_conditions_fired": fired})

    def test_empty_string_only_refused(self):
        with self.assertRaises(ValueError):
            self.promote([""])

    def test_none_only_refused(self):
        with self.assertRaises(ValueError):
            self.promote([None])

    def test_blank_mix_refused(self):
        with self.assertRaises(ValueError):
            self.promote(["", None, "   "])

    def test_stated_condition_promotes(self):
        updated = self.promote(["c1"])
        self.assertEqual(updated["retention_tier"], "Tier 2")


class TestR2059NoInputsPin(B2Base):
    def test_no_inputs_refusal_with_fired_condition_stated(self):
        record = {"run_id": "run-r2059", "retention_tier": "Tier 1",
                  "flag_conditions_fired": ["c1"]}
        with self.assertRaises(ValueError) as caught:
            mod10.apply_flag_evaluation(
                record, outcome="promote", tier="Tier 2", inputs=None)
        self.assertIn("no inputs", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

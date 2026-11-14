"""Step 15 Round 1 fix pins, cluster 4: MOD-11, MOD-05, and MOD-06,
with the MOD-10 and MOD-02 touches the register head items carry.
Each test pins one register item by triage id, test first."""
import unittest
from crucible import mod02, mod05, mod06, mod10, mod11

def tri_edges():
    e=[]
    for a,b in [("a","b"),("b","a"),("b","c"),("c","b"),("a","c"),("c","a")]:
        e.append(mod05.vouch(a,b,1,component_definition_version="v1"))
    return e

class T(unittest.TestCase):
    def setUp(self): mod10.reset_stores()
    # TA-19
    def test_ta19_size_is_members(self):
        c=mod05.component(tri_edges(),component_definition_version="v1")
        self.assertEqual(c["largest_mutually_vouching_component_size"],3)
        self.assertTrue(mod05.component_cap_check(tri_edges(),6))
        self.assertFalse(mod05.component_cap_check(tri_edges(),5))
    # TA-20
    def test_ta20_snapshot_strict(self):
        edges=tri_edges(); snap=mod05.graph_snapshot(edges,component_definition_version="v1")
        self.assertTrue(mod05.validate_graph_snapshot(snap,edges))
        for mut in ("noversion","badref","nullref","nodist"):
            s=mod05.graph_snapshot(edges,component_definition_version="v1")
            if mut=="noversion": s.pop("component_definition_version")
            if mut=="badref": s["edge_list_reference"]=edges[:1]
            if mut=="nullref": s["edge_list_reference"]=None
            if mut=="nodist": s.pop("realised_degree_distribution")
            self.assertFalse(mod05.validate_graph_snapshot(s,edges),mut)
    # TA-21
    def test_ta21_claim_fails_open_closed(self):
        fam={"excluded_share_threshold":0.5}
        self.assertFalse(mod05.validate_headline_adjudication_claim(fam,{"run_id":"r"}))
        forged={"excluded_class_counts_and_shares":{mod05.FORGED_VOUCH_BASIS_CLASS:{"count":1,"share":0.25}}}
        self.assertFalse(mod05.validate_headline_adjudication_claim(fam,forged))
        clean={"excluded_class_counts_and_shares":{mod05.FORGED_VOUCH_BASIS_CLASS:{"count":0,"share":{"numerator":0,"denominator":4}}}}
        self.assertTrue(mod05.validate_headline_adjudication_claim(fam,clean))
    # TA-26 + TB-45
    def test_ta26_proportion_strict(self):
        self.assertFalse(mod05.validate_proportion({"numerator":1,"denominator":2,"quotient":0.9}))
        self.assertFalse(mod05.validate_proportion({"numerator":"1","denominator":2}))
        self.assertFalse(mod05.validate_proportion({"numerator":True,"denominator":2}))
        self.assertFalse(mod05.validate_proportion({"numerator":-1,"denominator":-2}))
        self.assertFalse(mod05.validate_proportion({"numerator":0,"denominator":0}))
        self.assertTrue(mod05.validate_proportion({"numerator":1,"denominator":2,"quotient":0.5}))
    def test_tb45_empty_share_unknown(self):
        self.assertEqual(mod05.gate_passing_share([],[]),mod05.UNKNOWN_SHARE)
        self.assertEqual(mod05.share_for_epoch("e1",eligible=[],passing=[]),mod05.UNKNOWN_SHARE)
        counts=mod05.excluded_class_counts([])
        for entry in counts.values(): self.assertEqual(entry["share"],mod05.UNKNOWN_SHARE)
        with self.assertRaises(ValueError):
            mod05.score_bearing_figure(100,mod05.UNKNOWN_SHARE)
        pop=mod05.population_figure(100,[],record_state="as retained")
        self.assertEqual(pop["population_average"],mod05.UNKNOWN_SHARE)
    # TA-07
    def test_ta07_panel_recursive(self):
        case={"case_identifier":"c1","membership":"m","is_honest":True,"label":"x","nested":{"ground_truth":"canary","derived_ground_truth_key":"canary2"},"ground_truth_label_reference":"lab"}
        formed=mod05.panel_inputs(case)
        self.assertNotIn("membership",formed); self.assertNotIn("is_honest",formed); self.assertNotIn("label",formed)
        self.assertEqual(formed.get("nested"),{})
        self.assertFalse(mod05.validate_panel_inputs({"a":{"ground_truth":"x"}}))
        with self.assertRaises(ValueError):
            mod05.adjudicate(case,accuracy_value=0.5,assumption_set="s",row="r",error_direction="sym")
    # TA-33
    def test_ta33_recompute_both_directions(self):
        logged={1:{"numerator":1,"denominator":2}}
        recomp={1:{"numerator":1,"denominator":2},2:{"numerator":1,"denominator":1}}
        r=mod05.recompute_share(logged,recomp)
        self.assertGreaterEqual(r["divergence_count"],1)
        self.assertFalse(mod05.validate_report_reading(r["divergence_count"]))
    # TA-34
    def test_ta34_adjudicate_domains(self):
        case={"case_identifier":"c1"}
        with self.assertRaises(ValueError):
            mod05.adjudicate(case,accuracy_value=0.5,assumption_set="s",row="r",error_direction="x",outcome="invented")
        with self.assertRaises(ValueError):
            mod05.adjudicate(case,accuracy_value=7.5,assumption_set="s",row="r",error_direction="x",outcome="slashable")
    # TA-48
    def test_ta48_band_highest(self):
        bands=[("high",10),("low",1)]
        r=mod05.band_membership(12,bands,evaluation_order="O-1")
        self.assertEqual(r["band"],"high")
    # TA-49
    def test_ta49_no_manufactured_order(self):
        with self.assertRaises(ValueError):
            mod05.reputation_and_band_values({"a":5},[("low",1)])
    # TA-69
    def test_ta69_cost_statement_share_log(self):
        rec={"share_log":[{"numerator":0,"denominator":0}],"degree_distribution_log":{}}
        self.assertFalse(mod05.cost_statement_valid(rec))
        rec2={"share_log":[{"numerator":1,"denominator":2}],"degree_distribution_log":{}}
        self.assertTrue(mod05.cost_statement_valid(rec2))
    # TA-71 mod05 limb
    def test_ta71_failure_carries_class(self):
        try:
            mod05.adjudicate({"case_identifier":"c"},accuracy_value=None,assumption_set="s",row="r",error_direction="x")
            self.fail("no failure")
        except ValueError as exc:
            cls=getattr(exc,"failure_class",None)
            self.assertIsNotNone(cls); self.assertEqual(cls["recorded_in"],"run record only"); self.assertIsNone(cls["run_status"])
    # TA-09
    def test_ta09_escrow_payload_screen(self):
        with self.assertRaises(ValueError):
            mod06.escrow_result("k",payload={"amount":5,"currency":"USD"})
        with self.assertRaises(ValueError):
            mod06.escrow_result("k",payload={"nested":{"anchor_set":["x"]}})
        ok=mod06.escrow_result("k",payload={"ordinary":1})
        self.assertTrue(mod06.validate_escrow_result(ok))
        bad=dict(ok); bad["payload"]={"real_money_value":10}
        self.assertFalse(mod06.validate_escrow_result(bad))
    # TA-50
    def test_ta50_contract_state_form10(self):
        st=mod06.escrow_contract_state("c1",pair_identifiers=("p1","p2"),standard_or_profile_identifier="std",estimated_cost_value=3,pause_state="not paused",pause_cap_value={"total_percent":400})
        for f in ("pair_identifiers","standard_or_profile_identifier","estimated_cost_value","pause_state"):
            self.assertIn(f,st)
        with self.assertRaises(ValueError):
            mod06.escrow_contract_state("c1",variant="B-9")
        with self.assertRaises(ValueError):
            mod06.escrow_contract_state("c1",lien_state="invented")
        st2=mod06.escrow_contract_state("c1",lost_contact_clause_on=True,window_n=7)
        self.assertIn("lost_contact_clock_state",st2)
    # TA-51
    def test_ta51_pause(self):
        self.assertFalse(mod06.validate_pause_result({"variant":"B-4","per_variant_pause_value":{"extension_percent":100,"total_percent":200}}))
        self.assertTrue(mod06.validate_pause_result({"variant":"B-4","per_variant_pause_value":dict(mod06.PAUSE_CAP_B4)}))
        with self.assertRaises(ValueError):
            mod06.pause_cap("B-9")
    # TA-70
    def test_ta70_dq_table_distinct(self):
        rows=mod06.dq_arrival_table()
        dup=[dict(rows[0]) for _ in range(26)]
        self.assertFalse(mod06.validate_dq_arrival_table(dup))
        self.assertTrue(mod06.validate_dq_arrival_table(rows))
    # C-48
    def test_c48_refusal_wording(self):
        with self.assertRaises(ValueError) as cm:
            mod06.run_instruction("replace_backup_key",context={})
        self.assertIn("refused",str(cm.exception).lower())
    # TA-30 mod06 limb
    def test_ta30_open_request_zero_cost(self):
        with self.assertRaises(ValueError):
            mod06.run_instruction("open_request",context={"stated_cost":1,"true_cost":0})
    # TB-46 + C-05 limb c
    def test_tb46_lookup_names(self):
        values={f:"value for "+f for f in mod11.HEADLINE_UNIT_FIELDS}
        r=mod11.build_headline_unit_from_run("missing-run",values,store_kind="bogus-kind")
        self.assertFalse(r["built"]); self.assertNotEqual(r["failure"]["name"],mod10.ONE_LOOKUP_FAILURE_NAME)
        r2=mod11.build_headline_unit_from_run("missing-run",values,store_kind="sweep")
        self.assertFalse(r2["built"]); self.assertEqual(r2["failure"]["name"],mod10.ONE_LOOKUP_FAILURE_NAME)
    def test_c05_provenance_not_defeated(self):
        mod10.retain_run_record({"run_id":"run-x","run_identifier":"run-x","record_state":"as retained"})
        values={f:"value for "+f for f in mod11.HEADLINE_UNIT_FIELDS}
        values["checkability_fields"]="caller supplied string"
        try:
            r=mod11.build_headline_unit_from_run("run-x",values)
            self.assertTrue(r["built"]); self.assertIsInstance(r["unit"]["checkability_fields"],dict); self.assertEqual(r["unit"]["checkability_fields"]["record"],"run-x")
        except ValueError:
            pass
    # C-36 mod11 limb
    def test_c36_weekly_count_named_failure(self):
        with self.assertRaises(ValueError):
            mod11.weekly_count([{"week":"W1"}],"W1")
        with self.assertRaises(ValueError):
            mod11.weekly_count([{"headline_unit_identifiers":["u1"]}],"W1")
        self.assertEqual(mod11.weekly_count([{"week":"W1","headline_unit_identifiers":["u1"]}],"W1"),1)
    # C-35 partial: pair and label
    def test_c35_pair_and_label(self):
        units=["u%02d"%n for n in range(1,4)]
        c=mod11.make_weekly_container("W1",units)
        self.assertIn("weekly_load",c); self.assertEqual(c["weekly_load"]["H"],3); self.assertIn("U",c["weekly_load"])
        self.assertIn("estimated",str(c.get("cap_form","")).lower())
    # TB-31, restated to the R1-080 cured form: a second checkpoint
    # write for one run and day stands rejected and recorded, so the
    # repeated identical writes this pin once counted on no longer
    # stand retained toward any cap.
    def test_tb31_checkpoint_cap(self):
        man={"run_identifier":"cap-run","simulated_day":1}
        mod10.retain_checkpoint(dict(man))
        with self.assertRaises(ValueError):
            mod10.retain_checkpoint(dict(man))
        self.assertEqual(len(mod10.checkpoints_for_run("cap-run")),1)
        self.assertEqual(len(mod10.rejected_checkpoint_writes("cap-run")),1)
    # TB-32
    def test_tb32_hold_end(self):
        h=mod10.place_reserve_hold("hold-run",family_states_headlines=False,start_day=3)
        self.assertEqual(h["maximum_duration_days"],30); self.assertEqual(h["end_day"],33); self.assertTrue(h["stated_end"])
        state=mod10.reserve_hold_for_run("hold-run",current_day=40)
        self.assertNotEqual(state["state"],"held")
    # TB-33
    def test_tb33_writes_into_store(self):
        mod10.write_summary_record({"run_id":"s-run","retention_tier":"Tier 1"})
        out=mod10.apply_flag_evaluation(mod10.summary_record_for_run("s-run"),outcome="promote",tier="Tier 3",inputs={"x":1,"flag_conditions_fired":["condition-1"]})
        self.assertEqual(mod10.summary_record_for_run("s-run")["retention_tier"],"Tier 3")
        base=mod10.summary_record_for_run("s-run")
        mod10.apply_deferred_evaluation(base,1,inputs={"a":1},outcome="held")
        stored=mod10.summary_record_for_run("s-run")
        self.assertEqual(len(stored.get("deferred_evaluations") or []),1)
        with self.assertRaises(ValueError):
            mod10.apply_deferred_evaluation(None,1,inputs={},outcome="x")
    # TB-34
    def test_tb34_route5_reporting(self):
        mod10.write_summary_record({"run_id":"r5-run","retention_tier":"Tier 3"})
        mod10.retain_checkpoint({"run_identifier":"r5-run","simulated_day":1})
        rec=mod10.retention_record_for_run("r5-run")
        self.assertEqual(rec.get("retention_tier"),"Tier 3")
        self.assertIn("tier_forms",rec); self.assertIn("not_retained",rec); self.assertIn("shortfall",rec)
        joined=" ".join(str(x) for x in rec.get("not_retained",[]))
        self.assertIn("not retained",joined)
    def test_ta71_mod06_failure_carries_class(self):
        try:
            mod06.run_instruction("replace_backup_key",context={})
            self.fail("no failure")
        except ValueError as exc:
            cls=getattr(exc,"failure_class",None)
            self.assertIsNotNone(cls); self.assertEqual(cls["recorded_in"],"run record only"); self.assertIsNone(cls["run_status"])
    # TB-49
    def test_tb49_wrapper_boolean(self):
        self.assertIs(mod02.validate_family_derivation_text("derive by arithmetic on a root seed"),False)
        self.assertIs(mod02.validate_family_derivation_text("an ordinary derivation text"),False)
        self.assertIs(mod02.validate_family_derivation_text(123),False)
        refusal=mod02.derivation_text_refusal("an ordinary derivation text")
        self.assertEqual(refusal["failure"],"DERIVATION-GATED")

if __name__=="__main__": unittest.main(verbosity=1)

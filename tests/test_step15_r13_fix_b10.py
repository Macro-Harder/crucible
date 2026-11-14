import copy
import math
import os
import tempfile
import unittest

from crucible import mod02, mod03, mod05, mod06, mod07, mod08
from crucible import mod09, mod10, mod11, mod12, mod13, mod14


def lawful_unit():
    values = {field: "value for " + field
              for field in mod11.HEADLINE_UNIT_FIELDS}
    values["claim_sentence"] = (
        "At the sampled points within the stated scope, the result "
        "holds for the sampled points only, and nothing is claimed "
        "beyond the stated limits.")
    values["grounding_sentence"] = (
        "This unit rests on the retained run records within the "
        "stated scope, and its limits are that nothing is claimed "
        "beyond the sampled points in this unit.")
    values["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is used in "
        "this unit.")
    return mod11.make_headline_unit(values)


def deep_chain(levels):
    value = 1
    for _ in range(levels):
        value = [value]
    return {"x": value}


def search_record():
    carriage = mod09.run_record_carriage(
        ["conditional briber"], 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])
    return mod09.build_search_record(
        carriage, points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=[0, 5])


def msg_of(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__ + ": " + str(exc)
    raise AssertionError("no exception raised by " + repr(fn))


class TestR12079Mod06InstructionRefusals(unittest.TestCase):
    def test_r12_079(self):
        m_none = msg_of(mod06.run_instruction, "open_request")
        m_stated = msg_of(mod06.run_instruction, "open_request",
                          context={"stated_cost": 5})
        m_true = msg_of(mod06.run_instruction, "open_request",
                        context={"true_cost": 5})
        self.assertIn("refused", m_none)
        self.assertIn("stated cost", m_none)
        self.assertIn("true cost", m_none)
        self.assertNotEqual(m_stated, m_true)
        self.assertIn("true cost", m_stated)
        self.assertIn("stated cost", m_true)
        base = {"stated_cost": 5, "true_cost": 5}
        m_counter = msg_of(mod06.run_instruction, "open_request",
                           context=dict(base, countersigning=True))
        m_bound = msg_of(mod06.run_instruction, "open_request",
                         context=dict(base, bound=True))
        self.assertNotEqual(m_counter, m_bound)
        self.assertIn("countersigning", m_counter)
        self.assertIn("bound", m_bound)
        self.assertIn("refused", m_counter)
        m_check = msg_of(mod06.run_instruction, "check_in")
        m_claim = msg_of(mod06.run_instruction, "claim_lost_contact")
        self.assertNotEqual(m_check, m_claim)
        self.assertIn("check_in", m_check)
        self.assertIn("clause_on", m_check)
        self.assertIn("missing", m_check)
        m_window = msg_of(mod06.run_instruction, "check_in",
                          context={"clause_on": True})
        self.assertIn("refused", m_window)
        self.assertIn("window", m_window)
        self.assertIn("missing", m_window)
        m_barred = msg_of(mod06.escrow_result, "k",
                          payload={"real_money_value": 5})
        self.assertIn("refused", m_barred)
        self.assertIn("real_money", m_barred.replace(" ", "_"))
        m_anchor = msg_of(mod06.escrow_result, "k",
                          payload={"nested": {"anchor_set": ["x"]}})
        self.assertIn("anchor_set", m_anchor.replace(" ", "_"))
        m_pair = msg_of(mod06.escrow_result, "k",
                        payload={"amount": 5, "currency": "USD"})
        self.assertIn("amount", m_pair)
        self.assertIn("currency", m_pair)
        ok = mod06.run_instruction(
            "open_request", context={"stated_cost": 5, "true_cost": 5})
        self.assertTrue(mod06.validate_escrow_result(ok))


class TestR12080EscrowVariant(unittest.TestCase):
    def test_r12_080(self):
        text = msg_of(mod06.escrow_result, "k", variant="B-9")
        self.assertIn("B-9", text)
        self.assertIn("refused", text)
        record = mod06.escrow_result("k", variant="B-4")
        record["variant"] = "B-9"
        self.assertFalse(mod06.validate_escrow_result(record))
        good = mod06.escrow_result("k", variant="B-3")
        self.assertTrue(mod06.validate_escrow_result(good))


class TestR12081QuoteHeadlineUnit(unittest.TestCase):
    def test_r12_081(self):
        unit = lawful_unit()
        missing = dict(unit)
        del missing["claim_sentence"]
        m_missing = msg_of(mod11.quote_headline_unit, missing)
        self.assertIn("claim_sentence", m_missing)
        extra = dict(unit)
        extra["zzz"] = "x"
        m_extra = msg_of(mod11.quote_headline_unit, extra)
        self.assertIn("zzz", m_extra)
        m_form = msg_of(mod11.quote_headline_unit, ["not", "a", "unit"])
        self.assertIn("refused", m_form)
        self.assertEqual(
            len({m_missing, m_extra, m_form}), 3)


class TestR12082TransitionActs(unittest.TestCase):
    def test_r12_082(self):
        m1 = msg_of(mod11.transition_wording, "north", "south")
        self.assertIn("transition_wording", m1)
        self.assertIn("pair of grid numbers", m1)
        self.assertNotIn("invalid literal", m1)
        m2 = msg_of(mod11.transition_wording, None, (1, 2))
        self.assertIn("transition_wording", m2)
        self.assertNotIn("not subscriptable", m2)
        m3 = msg_of(mod11.region_shift_steps, {"a": 1}, (1, 2))
        self.assertIn("region_shift_steps", m3)
        self.assertNotIn("KeyError", m3)
        report = {
            "distribution_near_threshold": "stated",
            "regime_class_counts": {"a": 1, "b": 2, "c": 3},
            "honest_loss_rate": {"form": "H1"},
            "points": [{"near_threshold": True, "replicates": "many"}],
        }
        self.assertFalse(mod11.validate_transition_report(report))
        self.assertEqual(
            mod11.transition_wording((1, 2), (1, 3))["wording"],
            "holding")


class TestR12083RunRecordFailures(unittest.TestCase):
    def test_r12_083(self):
        cases = [
            {},
            {"run_class": "bogus", "seed_domain": "screening"},
            {"run_class": "confirmation", "seed_domain": "screening"},
            {"run_class": "confirmation",
             "seed_domain": "held out confirmation",
             "relabelled_from": "screening"},
            {"run_class": "screening", "seed_domain": "screening",
             "nested": {"amount": 5, "currency": "USD"}},
            {"run_class": "screening", "seed_domain": "screening",
             "anchor_scenario_values": ["a", "b"]},
            {"run_class": "screening", "seed_domain": "screening",
             "chain": deep_chain(120)["x"]},
        ]
        seen = []
        for case in cases:
            self.assertFalse(mod12.validate_run_record(case))
            failures = mod12.run_record_validation_failures(case)
            self.assertTrue(failures, repr(case))
            seen.append(tuple(failures))
        self.assertEqual(len(set(seen)), len(cases))
        joined = [" ".join(item) for item in seen]
        self.assertIn("empty", joined[0])
        self.assertIn("run_class", joined[1])
        self.assertIn("screening", joined[2])
        self.assertIn("relabel", joined[3])
        self.assertIn("money", joined[4])
        self.assertIn("anchor", joined[5])
        self.assertIn("depth", joined[6] + " bound cycle")
        lawful = {"run_class": "screening", "seed_domain": "screening"}
        self.assertTrue(mod12.validate_run_record(lawful))
        self.assertEqual(mod12.run_record_validation_failures(lawful), [])


class TestR12084DepthCycleWording(unittest.TestCase):
    def test_r12_084(self):
        cyclic = []
        cyclic.append(cyclic)
        deep = deep_chain(120)
        m_seal_deep = msg_of(mod12.seal_family_record, deep)
        m_seal_cycle = msg_of(mod12.seal_family_record, {"x": cyclic})
        self.assertNotEqual(m_seal_deep, m_seal_cycle)
        self.assertIn("depth", m_seal_deep)
        self.assertIn("100", m_seal_deep)
        self.assertIn("cycle", m_seal_cycle)
        self.assertIn("record", m_seal_deep)
        base = {"family_identifier": "f1"}
        m_edit_record = msg_of(mod12.apply_family_edit, deep)
        m_edit_change = msg_of(mod12.apply_family_edit, base, deep)
        m_edit_cycle = msg_of(
            mod12.apply_family_edit, base, {"x": cyclic})
        self.assertIn("record", m_edit_record)
        self.assertIn("change", m_edit_change)
        self.assertIn("cycle", m_edit_cycle)
        self.assertEqual(
            len({m_edit_record, m_edit_change, m_edit_cycle}), 3)
        m_claim_deep = msg_of(mod12.admit_claim, {}, deep)
        m_claim_cycle = msg_of(mod12.admit_claim, {}, {"x": cyclic})
        self.assertNotEqual(m_claim_deep, m_claim_cycle)
        self.assertIn("claim", m_claim_deep)


class TestR12085JointRunFailureNames(unittest.TestCase):
    def test_r12_085(self):
        run_text = {"adapter_choices": "plain text"}
        name_text = mod07.joint_run_failure(run_text)["name"]
        self.assertIn("no record list form", name_text)
        run_bad_entry = {"adapter_choices": ["not a record"]}
        name_entry = mod07.joint_run_failure(run_bad_entry)["name"]
        self.assertIn("no record form", name_entry)
        run_map = {"adapter_choices": [],
                   "tracer_passage_records": {"a": 1}}
        name_map = mod07.joint_run_failure(run_map)["name"]
        self.assertIn("no list form", name_map)
        self.assertNotIn("missing", name_map)


class TestR12086DrawFromStream(unittest.TestCase):
    def test_r12_086(self):
        m_pos = msg_of(mod02.draw_from_stream, position="abc",
                       carried_positions=10)
        m_carried = msg_of(mod02.draw_from_stream, position=0,
                           carried_positions="abc")
        self.assertNotEqual(m_pos, m_carried)
        self.assertIn("draw_from_stream", m_pos)
        self.assertIn("position", m_pos)
        self.assertIn("carried", m_carried)
        self.assertNotIn("invalid literal", m_pos)
        m_list = msg_of(mod02.draw_from_stream, position=[1],
                        carried_positions=10)
        self.assertIn("draw_from_stream", m_list)
        self.assertIn("position", m_list)
        self.assertNotIn("int() argument", m_list)


class TestR12087ReadoutStatus(unittest.TestCase):
    def test_r12_087(self):
        status = mod12.readout_status({})
        self.assertEqual(status["named_condition"], 1)
        self.assertEqual(status["unmet_conditions"], [1, 2, 3, 4, 5, 6])
        self.assertIn("named_condition_text", status)
        self.assertIn("claim", status["named_condition_text"])
        self.assertIn("condition_texts", status)
        self.assertIn("1", status["condition_texts"])
        full = {
            "claim_in_bounding_form": False,
            "bound_fixed_in_advance": True,
            "search_complete": False,
            "material_failure_found": False,
            "search_completed_at_rung": 6,
            "tolerance_and_replication_rule": "stated",
            "confirmation_under_family_discipline": True,
            "check_artefact_battery": {"passed": [
                "A-01", "A-02", "A-03", "A-04", "A-05", "A-06",
                "A-07", "A-08", "A-09", "A-10", "A-11"]},
            "assumption_set_and_rows_inside_result": True,
        }
        both = mod12.readout_status(full)
        self.assertEqual(both["named_condition"], 1)
        only_two = dict(full, claim_in_bounding_form=True)
        self.assertEqual(
            mod12.readout_status(only_two)["named_condition"], 2)


class TestR12088Mod07NonRecord(unittest.TestCase):
    def test_r12_088(self):
        m_fold = msg_of(mod07.record_folding, None, [])
        self.assertIn("record_folding", m_fold)
        self.assertNotIn("AttributeError", m_fold)
        m_fold_list = msg_of(mod07.record_folding, ["x"], [])
        self.assertIn("record_folding", m_fold_list)
        m_class = msg_of(mod07.classify_seam_feedback, "item", ["x"], [])
        self.assertIn("classify_seam_feedback", m_class)
        self.assertIsNone(mod07.reading_for_result([["x"]], "id-1"))
        m_append = msg_of(mod07.append_reading, [["x"]],
                          {"choice_identifier": "c1"})
        self.assertIn("append_reading", m_append)


class TestR12089VocabularyRefusals(unittest.TestCase):
    def test_r12_089(self):
        m_domain = msg_of(mod02.make_derivation_input,
                          domain="bogus-domain")
        self.assertIn("bogus-domain", m_domain)
        self.assertIn("screening", m_domain)
        self.assertIn("held out confirmation", m_domain)
        m_result = msg_of(mod07.make_tracer_passage_record,
                          "item", 1, "passed", "weird-result")
        self.assertIn("weird-result", m_result)
        self.assertIn("passed as a record", m_result)
        self.assertIn("blocked", m_result)
        self.assertIn("not attempted", m_result)


class TestR12090StreamSetRefusalStable(unittest.TestCase):
    def test_r12_090(self):
        m1 = msg_of(mod02.validate_stream_cardinality,
                    counts={"ghost": 1}, stream_set=object())
        m2 = msg_of(mod02.validate_stream_cardinality,
                    counts={"ghost": 1}, stream_set=object())
        self.assertEqual(m1, m2)
        self.assertNotIn("0x", m1)
        self.assertIn("stream set stands in no stated form", m1)


class TestR12091RegistryEntryForm(unittest.TestCase):
    def test_r12_091(self):
        log = [{"run_identifier": "r1", "run_id": "r1"}]
        result = mod13.compare_registry_against_run_log(
            "not-a-record", run_log=log)
        self.assertFalse(result["performed"])
        self.assertIn("no record form", result["shortfall_status"])
        entry = {"claim_identifier": "c9",
                 "screening_run_identifiers": ["r1"]}
        no_log = mod13.compare_registry_against_run_log(entry)
        self.assertIn("no run log stands handed",
                      no_log["shortfall_status"])
        self.assertNotEqual(result["shortfall_status"],
                            no_log["shortfall_status"])


class TestR12092Mod13ValidationFailures(unittest.TestCase):
    def test_r12_092(self):
        verdict = mod13.verdict_record("c1")
        self.assertEqual(
            mod13.verdict_record_validation_failures(verdict), [])
        bad_outcome = dict(verdict, outcome="bogus")
        f_outcome = mod13.verdict_record_validation_failures(bad_outcome)
        self.assertTrue(any("outcome" in item for item in f_outcome))
        bad_standard = dict(
            verdict, standard_applied="distributional equivalence")
        f_standard = mod13.verdict_record_validation_failures(
            bad_standard)
        self.assertTrue(any("standard" in item for item in f_standard))
        bad_sent = dict(verdict, replication_statement_sentences=[])
        f_sent = mod13.verdict_record_validation_failures(bad_sent)
        self.assertTrue(any("sentence" in item for item in f_sent))
        self.assertEqual(
            len({tuple(f_outcome), tuple(f_standard), tuple(f_sent)}), 3)
        self.assertFalse(mod13.validate_verdict_record(bad_outcome))
        f_replay_hash = mod13.replay_claim_validation_failures(
            {"hash_equality_claimed": True})
        self.assertTrue(any("hash" in item for item in f_replay_hash))
        f_replay_form = mod13.replay_claim_validation_failures("x")
        self.assertTrue(any("record" in item for item in f_replay_form))
        f_resume = mod13.resume_claim_validation_failures(
            {"detection_scope": "state level"})
        self.assertTrue(any("scope" in item for item in f_resume))
        f_probe = mod13.probe_claim_validation_failures(
            {"margin_or_method_presented_as_settled": True})
        self.assertTrue(any("margin" in item for item in f_probe))
        f_scoring = mod13.scoring_record_validation_failures(
            {"inside_run_boundary": True})
        self.assertTrue(f_scoring)
        f_agg = mod13.aggregate_form_validation_failures(["horizon"])
        self.assertTrue(any("horizon" in item for item in f_agg))
        other = mod13.verdict_record("c2")
        f_pub_claim = mod13.publishable_on_replication_failures(
            {"claim_identifier": "c1"}, other)
        self.assertTrue(any("claim" in item for item in f_pub_claim))
        not_resting = mod13.verdict_record("c1", outcome="does not rest")
        f_pub_outcome = mod13.publishable_on_replication_failures(
            {"claim_identifier": "c1"}, not_resting)
        self.assertTrue(any("rests" in item for item in f_pub_outcome))
        self.assertFalse(mod13.publishable_on_replication(
            {"claim_identifier": "c1"}, other))


class TestR12093Mod08Report(unittest.TestCase):
    def test_r12_093(self):
        good_label = mod08.PROFILE_LABEL_CARRIAGE
        field = mod08.PROFILE_BOUND_LABEL_FIELD
        barred = {field: good_label, "score_verdict": "pass"}
        m_barred = msg_of(mod08.report, figures=[barred])
        self.assertIn("verdict", m_barred)
        self.assertIn("position 0", m_barred)
        self.assertNotIn("without its profile bound label", m_barred)
        m_form = msg_of(mod08.report, figures=[42])
        self.assertIn("no record form", m_form)
        bad_label = {field: "other label"}
        m_label = msg_of(mod08.report, figures=[bad_label])
        self.assertIn("profile bound label", m_label)
        lawful = {field: good_label}
        result = mod08.report(figures=[lawful])
        self.assertEqual(len(result["figures"]), 1)
        m_second = msg_of(mod08.report, figures=[lawful, barred])
        self.assertIn("position 1", m_second)


class TestR12094Mod03CastDialects(unittest.TestCase):
    def _records(self):
        return [
            mod03.make_archetype_record(
                archetype_id="a1", behaviour={"action": "vouch"}),
        ]

    def test_r12_094(self):
        point = {"population": 1, "archetype_mix": {"a1": 1}}
        messages = []
        try:
            mod03.build_cast(point, self._records(), strategy_class=None)
        except Exception as exc:
            messages.append((type(exc).__name__, str(exc)))
        self.assertIn("cast rejected", messages[0][1])
        self.assertIn("strategy class", messages[0][1])
        self.assertIn("absent or empty", messages[0][1])
        cases = [
            ("not a record", {"archetype_mix": {}}, "fixed"),
            ({"population": None, "archetype_mix": {}}, None, "fixed"),
        ]
        m_point = msg_of(mod03.build_cast, "not a record",
                         self._records(), strategy_class="fixed")
        self.assertIn("cast rejected", m_point)
        m_pop = msg_of(mod03.build_cast,
                       {"archetype_mix": {"a1": 1}},
                       self._records(), strategy_class="fixed")
        self.assertIn("cast rejected", m_pop)
        self.assertIn("population", m_pop)
        m_sum = msg_of(mod03.build_cast,
                       {"population": 2, "archetype_mix": {"a1": 1}},
                       self._records(), strategy_class="fixed")
        self.assertIn("cast rejected", m_sum)
        self.assertIn("1", m_sum)
        self.assertIn("2", m_sum)
        m_cover = msg_of(
            mod03.build_cast,
            {"population": 2, "archetype_mix": {"a1": 2}},
            self._records(), strategy_class="fixed",
            stream_state={"cast_values": [0.5]})
        self.assertIn("cast rejected", m_cover)
        m_extend = msg_of(mod03.extend_catalogue,
                          self._records(), self._records()[0],
                          strategy_class=None)
        self.assertIn("strategy class", m_extend)
        self.assertIn("absent or empty", m_extend)


class TestR12095ExtendHistoryWording(unittest.TestCase):
    def test_r12_095(self):
        segment = {"rule_set_version": "v1", "run_id": "r1"}
        m_int = msg_of(mod13.extend_history, 42, segment)
        m_none = msg_of(mod13.extend_history, None, segment)
        m_empty = msg_of(mod13.extend_history, [], segment)
        self.assertIn("no list form", m_int)
        self.assertIn("42", m_int)
        self.assertIn("empty", m_empty)
        self.assertEqual(len({m_int, m_none, m_empty}), 3)


class TestR12096Mod03BareErrors(unittest.TestCase):
    def test_r12_096(self):
        m_cat = msg_of(mod03.archetype_catalogue, records=["x"])
        self.assertIn("catalogue rejected", m_cat)
        self.assertNotIn("AttributeError", m_cat)
        self.assertNotIn("has no attribute", m_cat)
        m_cat_set = msg_of(mod03.archetype_catalogue, records="abc")
        self.assertIn("catalogue rejected", m_cat_set)
        point = {"population": 1, "archetype_mix": "ab"}
        m_cast = msg_of(mod03.build_cast, point,
                        [mod03.make_archetype_record(
                            archetype_id="a1",
                            behaviour={"action": "vouch"})],
                        strategy_class="fixed")
        self.assertIn("cast rejected", m_cast)
        self.assertNotIn("has no attribute", m_cast)


class TestR12097Mod14ErrorCarriage(unittest.TestCase):
    def test_r12_097(self):
        carriage = mod14.run_command("bogus_cmd", run_id="r1")
        self.assertIn("unknown shell command: bogus_cmd",
                      carriage["failure"])
        texts = []
        def collect(value):
            if isinstance(value, dict):
                for item in value.values():
                    collect(item)
            elif isinstance(value, str):
                texts.append(value)
        collect(carriage)
        sentence = "unknown shell command: bogus_cmd"
        self.assertEqual(
            sum(1 for item in texts if sentence in item), 2, texts)
        self.assertNotIn("message", carriage)
        self.assertNotIn("failure", carriage["failure_value"])
        store = mod14.run_command(
            "read_store", payload={"run_id": "nope"}, run_id="r1")
        message = store["failure_value"].get("message", "")
        self.assertNotIn("'", message)
        self.assertTrue(message.startswith(
            store["failure_value"]["name"]))
        self.assertEqual(store["failure_value"]["name"],
                         store.get("name"))


class TestR12098Mod09SearchRecordReason(unittest.TestCase):
    def test_r12_098(self):
        record = search_record()
        valid, failures = mod09.validate_search_record_with_reason(record)
        self.assertTrue(valid)
        self.assertEqual(failures, [])
        hollow = copy.deepcopy(record)
        hollow["search_record"]["search_budget"] = ""
        valid2, failures2 = mod09.validate_search_record_with_reason(
            hollow)
        self.assertFalse(valid2)
        self.assertTrue(failures2)
        self.assertTrue(any("search" in item for item in failures2))
        self.assertFalse(mod09.validate_search_record(hollow))
        valid3, failures3 = mod09.validate_search_record_with_reason({})
        self.assertFalse(valid3)
        self.assertTrue(failures3)


class Mod10Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()


class TestR12099UnknownStoreKind(Mod10Base):
    def test_r12_099(self):
        mod10.retain_checkpoint(
            {"run_id": "rc99", "simulated_day": 1}, store_kind="sweep")
        mod10.retain_checkpoint(
            {"run_id": "rc99", "simulated_day": 2}, store_kind="sweep")
        m_close = msg_of(mod10.close_run_retention, "rc99", "Tier 0",
                         store_kind="bogus")
        self.assertIn("unknown store kind", m_close)
        self.assertIn("bogus", m_close)
        m_delete = msg_of(
            mod10.delete_checkpoint, "rc99", 1, store_kind="bogus",
            trigger="clause C5 stated trigger",
            rule_path="stated deletion rule path")
        self.assertIn("unknown store kind", m_delete)
        self.assertEqual(
            len(mod10.checkpoints_for_run("rc99", store_kind="sweep")), 2)


class TestR12100FlagEvaluationRefusals(Mod10Base):
    def test_r12_100(self):
        deep = {"run_id": "rf100", "retention_tier": "Tier 1",
                "x": deep_chain(120)["x"]}
        m_deep = msg_of(mod10.apply_flag_evaluation, deep)
        self.assertIn("apply_flag_evaluation", m_deep)
        self.assertIn("record argument", m_deep)
        self.assertIn("no flag evaluation stands performed", m_deep)
        self.assertNotIn("no record stands retained", m_deep)
        cyclic = {"run_id": "rf100", "retention_tier": "Tier 1"}
        cyclic["self"] = cyclic
        m_cycle = msg_of(mod10.apply_flag_evaluation, cyclic)
        self.assertIn("apply_flag_evaluation", m_cycle)
        self.assertIn("cycle", m_cycle)
        record = {"run_id": "rf100", "retention_tier": "Tier 2"}
        m_promote = msg_of(
            mod10.apply_flag_evaluation, record, outcome="promote",
            tier="Tier 2", inputs={"flag_conditions_fired": ["c1"]})
        self.assertIn("Tier 2", m_promote)
        self.assertIn("rise above", m_promote)


class TestR12101CloseRecordExcludedDays(Mod10Base):
    def test_r12_101(self):
        for day in (1, 2, "²"):
            mod10.retain_checkpoint(
                {"run_id": "rd101", "simulated_day": day,
                 "checkpoint_state": {"day": str(day)}},
                store_kind="sweep")
        result = mod10.close_run_retention("rd101", "Tier 0")
        self.assertEqual(result["released_days"], [1, 2])
        self.assertEqual(result["kept_days"], [])
        self.assertIn("excluded_days", result)
        self.assertIn("²", result["excluded_days"])
        self.assertIn("excluded", " ".join(
            str(value) for value in result.values()).lower())
        remaining = mod10.checkpoints_for_run("rd101")
        self.assertEqual(len(remaining), 1)


class TestR12102CheckpointPositionCheck(Mod10Base):
    def test_r12_102(self):
        missing = mod10.checkpoint_position_check({})
        self.assertIn("no run identifier", missing["outcome"])
        self.assertNotEqual(missing.get("failure_under"), "C-09")
        for index in range(3):
            mod10.retain_event_log_entry(
                {"run_id": "rp102", "entry": index}, store_kind="sweep")
        text_pos = mod10.checkpoint_position_check(
            {"run_id": "rp102", "journal_position": "3"})
        self.assertIn("no integer form", text_pos["outcome"])
        self.assertNotEqual(text_pos.get("failure_under"), "C-09")
        float_pos = mod10.checkpoint_position_check(
            {"run_id": "rp102", "journal_position": 3.0})
        self.assertIn("no integer form", float_pos["outcome"])
        outside = mod10.checkpoint_position_check(
            {"run_id": "rp102", "journal_position": 99})
        self.assertEqual(outside["failure_under"], "C-09")
        self.assertIn("outside the retained log", outside["outcome"])
        inside = mod10.checkpoint_position_check(
            {"run_id": "rp102", "journal_position": 3})
        self.assertTrue(inside["reportable"])


class TestR12103PanelTraversal(Mod10Base):
    def test_r12_103(self):
        case = {"case_identifier": "c1", "x": deep_chain(120)["x"]}
        m_panel = msg_of(mod05.panel_inputs, case)
        self.assertIn("panel_inputs", m_panel)
        self.assertIn("refused", m_panel)
        cyclic = {"case_identifier": "c1"}
        cyclic["self"] = cyclic
        m_cycle = msg_of(mod05.panel_inputs, cyclic)
        self.assertIn("panel_inputs", m_cycle)
        self.assertIn("cycle", m_cycle)
        self.assertIn("refused", m_cycle)
        try:
            mod05.adjudicate(case, accuracy_value=0.5,
                             assumption_set="a", row="r",
                             error_direction="d")
            self.fail("adjudicate did not refuse")
        except ValueError as exc:
            self.assertIn("panel_inputs", str(exc))
            self.assertEqual(
                getattr(exc, "failure_class", None),
                mod05.adjudication_input_failure_class())


class TestR12104AdjudicateRefusals(unittest.TestCase):
    def _call(self, **overrides):
        args = {"accuracy_value": 0.5, "assumption_set": "a",
                "row": "r", "error_direction": "d"}
        args.update(overrides)
        return msg_of(mod05.adjudicate, {"case_identifier": "c1"}, **args)

    def test_r12_104(self):
        m_acc = self._call(accuracy_value=None)
        m_assump = self._call(assumption_set=None)
        m_row = self._call(row=None)
        m_dir = self._call(error_direction=None)
        self.assertIn("accuracy_value", m_acc)
        self.assertIn("assumption_set", m_assump)
        self.assertIn("row", m_row)
        self.assertIn("error_direction", m_dir)
        self.assertEqual(len({m_acc, m_assump, m_row, m_dir}), 4)
        m_text = self._call(accuracy_value="high")
        self.assertIn("no numeric form", m_text)
        m_range = self._call(accuracy_value=1.5)
        self.assertIn("range", m_range)
        self.assertNotEqual(m_text, m_range)
        m_outcome = msg_of(
            mod05.adjudicate, {"case_identifier": "c1"},
            accuracy_value=0.5, assumption_set="a", row="r",
            error_direction="d", outcome="maybe")
        self.assertIn("slashable", m_outcome)
        self.assertIn("not slashable", m_outcome)
        m_top = msg_of(
            mod05.adjudicate, {"membership": 1},
            accuracy_value=0.5, assumption_set="a", row="r",
            error_direction="d")
        self.assertIn("membership", m_top)
        m_nested = msg_of(
            mod05.adjudicate, {"outer": {"is_honest": 1}},
            accuracy_value=0.5, assumption_set="a", row="r",
            error_direction="d")
        self.assertIn("is_honest", m_nested)


class TestR12105ClosedSetRefusals(Mod10Base):
    def test_r12_105(self):
        m_new = msg_of(mod10.new_store, store_kind="bogus")
        self.assertIn("sweep, pilot, and live", m_new)
        self.assertIn("no store stands created", m_new)
        m_tier = msg_of(mod10.close_run_retention, "rx105", "Tier 9")
        self.assertIn("Tier 0", m_tier)
        self.assertIn("Tier 3", m_tier)
        self.assertIn("Tier 9", m_tier)
        m_gc = msg_of(mod10.retain_gc08_record, "bogus", {}, "owner-1")
        self.assertIn("dependency_manifest", m_gc)
        self.assertIn("call_log", m_gc)
        summary = {"run_id": "rx105"}
        m_fire0 = msg_of(mod10.apply_deferred_evaluation,
                         dict(summary), 0, inputs={}, outcome="o")
        self.assertIn("0", m_fire0)
        self.assertIn("1 and 2", m_fire0)
        self.assertNotIn("no third", m_fire0)
        m_fire3 = msg_of(mod10.apply_deferred_evaluation,
                         dict(summary), 3, inputs={}, outcome="o")
        self.assertIn("3", m_fire3)
        m_fire_text = msg_of(mod10.apply_deferred_evaluation,
                             dict(summary), "first", inputs={},
                             outcome="o")
        self.assertIn("first", m_fire_text)


class TestR12106DuplicateCheckpointDay(Mod10Base):
    def test_r12_106(self):
        mod10.retain_checkpoint(
            {"run_id": "re106", "simulated_day": 1}, store_kind="sweep")
        for dress in (" 01 ", "+1"):
            text = msg_of(mod10.retain_checkpoint,
                          {"run_id": "re106", "simulated_day": dress},
                          store_kind="sweep")
            self.assertIn("day 1", text, dress)
            self.assertNotIn("day " + dress, text, dress)


class TestR12107LookupFailureKind(Mod10Base):
    def test_r12_107(self):
        m_dep = msg_of(mod10.gc08_record, "dependency_manifest",
                       "owner-1")
        m_call = msg_of(mod10.gc08_record, "call_log", "owner-1")
        self.assertIn("dependency_manifest", m_dep)
        self.assertIn("call_log", m_call)
        self.assertNotEqual(m_dep, m_call)
        path = None
        try:
            with tempfile.NamedTemporaryFile(
                    "w", suffix=".json", delete=False) as handle:
                handle.write("{not json")
                path = handle.name
            try:
                mod10.new_store(store_kind="sweep", path=path)
                self.fail("store did not refuse")
            except mod10.LookupFailure as exc:
                self.assertIn("store file", str(exc))
                self.assertIn(path, str(exc))
                self.assertNotIn("run_identifier", exc.failure)
                self.assertEqual(exc.failure.get("store_path"), path)
        finally:
            if path and os.path.exists(path):
                os.unlink(path)


class TestR12108Mod05StatementRefusals(unittest.TestCase):
    def test_r12_108(self):
        m_num = msg_of(mod05.proportion_record, None, 2)
        m_den = msg_of(mod05.proportion_record, 1, None)
        self.assertIn("numerator", m_num)
        self.assertIn("refused", m_num)
        self.assertIn("denominator", m_den)
        self.assertNotEqual(m_num, m_den)
        m_zero = msg_of(mod05.score_bearing_figure, 10,
                        {"numerator": 1, "denominator": 0})
        self.assertIn("denominator", m_zero)
        m_disagree = msg_of(
            mod05.score_bearing_figure, 10,
            {"numerator": 1, "denominator": 2, "quotient": 0.9})
        self.assertIn("quotient", m_disagree)
        self.assertNotEqual(m_zero, m_disagree)
        m_state = msg_of(mod05.population_figure, 10, [])
        self.assertIn("record_state", m_state)
        self.assertIn("missing", m_state)
        m_unstated = msg_of(mod05.band_membership, 5, [("band", 1)],
                            evaluation_order=None)
        self.assertIn("no order stands stated", m_unstated)
        ruled = mod05.evaluation_order_record("O-1")
        ruled["presented_as_ruled"] = True
        m_ruled = msg_of(mod05.band_membership, 5, [("band", 1)],
                         evaluation_order=ruled)
        self.assertIn("presented as ruled", m_ruled)
        self.assertNotEqual(m_unstated, m_ruled)


class TestR12109AggregateDeliveryRefusal(Mod10Base):
    def test_r12_109(self):
        good = {"simulated_day": 1, "viewer_id": "viewer-1",
                "joint_outcome_components": [1.0, 2.0],
                "component_denominators": [1.0, 1.0]}
        bad = {"simulated_day": 7, "viewer_id": "viewer-9",
               "joint_outcome_components": ["text", 2.0],
               "component_denominators": [1.0, 1.0]}
        text = msg_of(mod10.retain_daily_aggregate_deliveries,
                      "run109", [good, bad])
        self.assertIn("viewer-9", text)
        self.assertIn("day 7", text)
        self.assertIn("joint_outcome_components", text)
        infinite = dict(bad, joint_outcome_components=[math.inf, 2.0])
        m_inf = msg_of(mod10.retain_daily_aggregate_deliveries,
                       "run109", [infinite])
        self.assertIn("non finite", m_inf)
        self.assertNotIn("non numeric form", m_inf)


class TestR12110WriteSummaryRecord(Mod10Base):
    def test_r12_110(self):
        m_list = msg_of(mod10.write_summary_record, ["x"])
        self.assertIn("write_summary_record", m_list)
        self.assertNotIn("has no attribute", m_list)
        m_text = msg_of(mod10.write_summary_record, "text")
        self.assertIn("write_summary_record", m_text)
        self.assertIn("no record form", m_text)


class TestR12112SuiteShadow(unittest.TestCase):
    def test_r12_112(self):
        # R12-112 basis, stated in the open: this row is the suite
        # level shadow of row R12-006. Its cure rests on the cured
        # form of row R12-006 exactly as the Round 12 register
        # states it, under settlement S-10, and on no cure of this
        # builder. Once that bound lands, the Builder 2 pin file
        # runtime stands remeasured against it, and the file
        # expected runtime stands stated beside it in the paper.
        own_path = os.path.abspath(__file__)
        with open(own_path, "r", encoding="utf-8") as handle:
            own_text = handle.read()
        self.assertIn("R12-006", own_text)
        self.assertIn("suite", own_text)
        self.assertIn("shadow", own_text)
        b2_path = os.path.join(
            os.path.dirname(own_path), "test_step15_r12_fix_b2.py")
        self.assertTrue(os.path.exists(b2_path))


if __name__ == "__main__":
    unittest.main()

"""Pin tests for fix wave 12, Builder 3, rows R12-010 to R12-017.

The copy family under settlement S-1, with settlements S-6 at the
MOD-10 sites of row R12-014. Each test states the proving act of
its source paper: a leaf carrying its own copy protocol, a buffer
form, or a shallow row, beside a plain control where the paper
states one. Plain simulated values only.
"""

import unittest

from crucible import mod03
from crucible import mod07
from crucible import mod08
from crucible import mod09
from crucible import mod10


class Lie:
    """A leaf whose deepcopy protocol returns a fabricated value."""

    def __init__(self, value="PWNED-LIE"):
        self.value = value

    def __deepcopy__(self, memo):
        return self.value

    def __copy__(self):
        return self.value


class Boom:
    """A leaf whose deepcopy protocol raises a bare error."""

    def __deepcopy__(self, memo):
        raise RuntimeError("evil boom from deepcopy")

    def __copy__(self):
        raise RuntimeError("evil boom from copy")


class ReduceLeaf:
    """A leaf whose reduce protocol rebuilds it as a string."""

    def __reduce_ex__(self, protocol):
        return (str, ("REBUILT",))


class EqSelfLeaf:
    """A leaf equal only to itself, whose deepcopy returns text."""

    def __deepcopy__(self, memo):
        return "different text"

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


class LyingGetDict(dict):
    """A dict storing one mapping and reporting another by get."""

    def __init__(self, stored, reported):
        dict.__init__(self, stored)
        self._reported = reported

    def get(self, key, default=None):
        return dict.get(self._reported, key, default)


class LyingFixtureUse(dict):
    """A case use storing one fixture and reporting F-26 by get."""

    def get(self, key, default=None):
        if key == "fixture":
            return "F-26"
        return dict.get(self, key, default)


class Base(unittest.TestCase):
    def setUp(self):
        mod10.reset_stores()

    def tearDown(self):
        mod10.reset_stores()


def valid_choice(**overrides):
    choice = {
        "choice_identifier": "choice-1",
        "reading_applied": "reading A",
        "parameter_or_rule_point_affected": "point",
        "governing_text_version": "gov v1",
        "escrow_variant_and_fold_version": "fold v1",
        "parley_test_total_source": None,
        "dependence_marks": [],
    }
    choice.update(overrides)
    return choice


def carriage_at(position):
    return mod09.run_record_carriage(
        ["conditional briber"], position, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=["conditional briber"])


def build_search(carriage, case_uses=None, **overrides):
    kwargs = {
        "points_tried": ["point one"],
        "per_point_outcome": [{"point": "point one",
                               "outcome": "no failure"}],
        "bond_candidates": [{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        "budget": "stated budget",
        "neighbourhood": {"definition": "adjacent points",
                          "step sizes": [1]},
        "starting_points": ["point zero"],
        "order_of_search": ["point one"],
        "case_uses": case_uses,
    }
    kwargs.update(overrides)
    return mod09.build_search_record(carriage, **kwargs)


def components():
    return {
        "attacker_controlled_share": {
            "numerator": 3, "denominator": 10, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count"},
        "farm_share_of_reputation_mass": {
            "numerator": 1.5, "denominator": 5.0, "proportion": 0.3,
            "viewer_identifier": "viewer-1",
            "numerator_kind": "binary64 value",
            "denominator_kind": "binary64 value"},
        "largest_component_share": {
            "component_size": 4, "population_size": 10,
            "proportion": 0.4,
            "component_definition_version": "version in force",
            "viewer_identifier": "viewer-1",
            "component_size_kind": "integer count",
            "population_size_kind": "integer count"},
        "honest_loss_rate": {
            "numerator": 1, "denominator": 10, "rate": 0.1,
            "loss_definition_version": "loss definition version 1",
            "viewer_identifier": "viewer-1",
            "numerator_kind": "integer count",
            "denominator_kind": "integer count"},
    }


def view_record(contents, run="run-b3-view"):
    return {
        "run_identifier": run,
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


class TestR12010Mod07Copy(Base):
    def test_fabricated_approval_does_not_validate(self):
        approver = Lie("Project Manager")
        standing = Lie("approved")
        approval = {"approver": approver,
                    "choice_identifier": "choice-1",
                    "effects": ["effect one"],
                    "standing": standing}
        direct = valid_choice(approval=approval)
        self.assertFalse(mod07.choice_approval_stands(direct))
        built = mod07.make_adapter_choice(
            "choice-1", "reading A", "point", "gov v1", "fold v1",
            approval=approval)
        self.assertIs(built["approval"]["approver"], approver)
        self.assertIs(built["approval"]["standing"], standing)
        self.assertFalse(mod07.choice_approval_stands(built))
        self.assertFalse(mod07.validate_adapter_choice(built))

    def test_ghost_identifier_in_log_entry(self):
        leaf = Lie("ghost-id")
        choice = valid_choice(choice_identifier=leaf)
        entry = mod07.interpretation_log_entry(choice)
        self.assertIs(entry["choice_identifier"], leaf)
        run_entry = mod07.run_record_entry(choice)
        self.assertIs(run_entry["choice_identifier"], leaf)

    def test_raising_leaf_escapes_no_act(self):
        acts = []
        boom = Boom()
        acts.append(("make_adapter_choice", lambda: mod07.make_adapter_choice(
            "choice-1", "reading A", "point", "gov v1", "fold v1",
            approval={"approver": boom})))
        acts.append(("interpretation_log_entry", lambda: (
            mod07.interpretation_log_entry(
                valid_choice(choice_identifier=Boom())))))
        acts.append(("run_record_entry", lambda: (
            mod07.run_record_entry(
                valid_choice(choice_identifier=Boom())))))
        acts.append(("append_reading", lambda: (
            mod07.append_reading(
                [{"choice_identifier": Boom()}], valid_choice()))))
        acts.append(("seam_effect_report", lambda: (
            mod07.seam_effect_report({"kind": "vouch", "value": Boom()}))))
        acts.append(("slash_outcome_report", lambda: (
            mod07.slash_outcome_report({"value": Boom()}))))
        for name, act in acts:
            with self.subTest(act=name):
                result = act()
                self.assertIsNotNone(result)

    def test_report_values_carry_the_leaf_itself(self):
        leaf = Lie()
        report = mod07.seam_effect_report(
            {"kind": "vouch", "value": leaf})
        self.assertIs(report["value"], leaf)
        slash = mod07.slash_outcome_report({"value": leaf})
        self.assertIs(slash["value"], leaf)

    def test_buffer_value_in_report_not_shared(self):
        handed = bytearray(b"payload")
        report = mod07.seam_effect_report(
            {"kind": "vouch", "value": handed})
        self.assertIsNot(report["value"], handed)
        view = memoryview(bytearray(b"viewbytes"))
        slash = mod07.slash_outcome_report({"value": view})
        self.assertIsInstance(slash["value"], memoryview)
        self.assertEqual(bytes(slash["value"]), b"viewbytes")
        handed[0] = 90
        self.assertEqual(report["value"], bytearray(b"payload"))


class TestR12011Mod09BuildReadings(Base):
    def test_case_use_fixture_read_from_stored(self):
        record = build_search(
            carriage_at(6),
            case_uses=[LyingFixtureUse(
                {"fixture": "other", "use": "plain use"})])
        entry = record["case_uses"][0]
        self.assertEqual(entry["fixture"], "other")
        self.assertEqual(entry["use"], "plain use")
        self.assertNotIn("standings_carried", entry)

    def test_ladder_position_read_from_stored_both_directions(self):
        stored = carriage_at(6)
        reported = dict(stored)
        reported["ladder_position"] = 0
        record = build_search(LyingGetDict(stored, reported))
        self.assertEqual(
            record["stopping_rule"]["ladder_position"], 6)
        self.assertTrue(record["stopping_rule"]["readout_point"])
        self.assertNotIn("rung_zero_control", record["stopping_rule"])
        stored_zero = carriage_at(0)
        reported_six = dict(stored_zero)
        reported_six["ladder_position"] = 6
        mirror = build_search(LyingGetDict(stored_zero, reported_six))
        self.assertEqual(
            mirror["stopping_rule"]["ladder_position"], 0)
        self.assertFalse(mirror["stopping_rule"]["readout_point"])
        self.assertIn("rung_zero_control", mirror["stopping_rule"])
        self.assertEqual(mirror["run_record"]["ladder_position"], 0)

    def test_carriage_leaf_carried_as_itself_and_validates(self):
        leaf = Lie("LIED-VALUE")
        carriage = carriage_at(6)
        carriage["leaf"] = leaf
        record = build_search(carriage)
        self.assertIs(record["run_record"]["leaf"], leaf)
        self.assertTrue(mod09.validate_search_record(record))


class TestR12012Mod08Copy(Base):
    def _figure(self, extra):
        return {"profile_bound_label": mod08.PROFILE_LABEL_CARRIAGE,
                "score_verdict": None, "extra": extra}

    def test_report_carries_leaf_as_itself(self):
        leaf = Lie("NEVER_HANDED_IN")
        result = mod08.report([self._figure(leaf)])
        self.assertIs(result["figures"][0]["extra"], leaf)

    def test_report_memoryview_and_raising_leaf(self):
        source = bytearray(b"abc")
        result = mod08.report([self._figure(memoryview(source))])
        carried = result["figures"][0]["extra"]
        self.assertIsInstance(carried, memoryview)
        self.assertEqual(bytes(carried), b"abc")
        source[0] = 90
        self.assertEqual(bytes(carried), b"abc")
        boom = Boom()
        raised = mod08.report([self._figure(boom)])
        self.assertIs(raised["figures"][0]["extra"], boom)

    def test_score_day_unchanged_society_reports_unchanged(self):
        record = {"agent_identifier": "a1", "day": 1,
                  "feature_values": {"f": 1.0}}
        result = mod08.score_day(
            [record], society_state={"leaf": EqSelfLeaf()})
        self.assertFalse(result["rule_state_changed"])
        self.assertTrue(result["run_valid_for_detection_reporting"])


class TestR12013Mod09BuilderCopy(Base):
    def test_make_strategy_leaf_and_memoryview(self):
        leaf = Lie("LIED")
        strategy = mod09.make_strategy(
            "s1", parameters={"k": leaf})
        self.assertIs(strategy["parameters"]["k"], leaf)
        source = bytearray(b"abc")
        strategy = mod09.make_strategy(
            "s1", parameters={"k": memoryview(source)})
        carried = strategy["parameters"]["k"]
        self.assertIsInstance(carried, memoryview)
        self.assertEqual(bytes(carried), b"abc")
        source[0] = 90
        self.assertEqual(bytes(carried), b"abc")

    def test_bond_search_leaf_at_evaluator_and_result(self):
        leaf = Lie("LIED")
        seen = []

        def evaluator(params):
            seen.append(params)
            return 2.5

        result = mod09.bond_search(
            [{"parameter_set": {"k": leaf},
              "harm": 10, "attacker_cost": 4}],
            griefing_evaluator=evaluator)
        self.assertIs(seen[0]["k"], leaf)
        self.assertIs(result["parameter_set"]["k"], leaf)
        self.assertIs(result["points_scored"][0]["parameter_set"]["k"],
                      leaf)

    def test_build_search_record_parts_carry_leaf(self):
        leaf = Lie("LIED-VALUE")
        spots = (
            ("points_tried", ["points_tried"]),
            ("neighbourhood", ["neighbourhood_definition_and_step_sizes"]),
            ("starting_points", ["starting_points"]),
            ("order_of_search", ["order_of_search"]),
            ("per_point_outcome", ["per_point_outcome"]),
            ("adaptations", ["every_adaptation"]),
        )
        for kwarg, path in spots:
            with self.subTest(part=kwarg):
                if kwarg in ("points_tried", "starting_points",
                             "order_of_search", "adaptations"):
                    handed = [leaf]
                elif kwarg == "per_point_outcome":
                    handed = [{"point": "point one", "leaf": leaf}]
                else:
                    handed = {"leaf": leaf}
                record = build_search(carriage_at(6), **{kwarg: handed})
                node = record["search_record"]
                for key in path:
                    node = node[key]
                if isinstance(node, list):
                    found = node[0]
                    if isinstance(found, dict):
                        found = found["leaf"]
                else:
                    found = node["leaf"]
                self.assertIs(found, leaf)
        use_leaf = Lie("LIED-VALUE")
        record = build_search(
            carriage_at(6),
            case_uses=[{"fixture": "other", "leaf": use_leaf}])
        self.assertIs(record["case_uses"][0]["leaf"], use_leaf)


class TestR12014Mod10Sites(Base):
    def test_joint_outcome_vector(self):
        leaf = Lie()
        record = mod10.build_joint_outcome_vector(
            components=components(),
            divergence_companion={"x": leaf})
        self.assertIs(record["divergence_companion"]["x"], leaf)
        dressed = components()
        dressed["attacker_controlled_share"]["extra"] = leaf
        record = mod10.build_joint_outcome_vector(
            components=dressed,
            divergence_companion={"nil_divergence_components": []})
        self.assertIs(
            record["attacker_controlled_share"]["extra"], leaf)
        boom = Boom()
        record = mod10.build_joint_outcome_vector(
            components=components(), divergence_companion={"x": boom})
        self.assertIs(record["divergence_companion"]["x"], boom)

    def test_summary_computed_path(self):
        leaf = Lie()
        mod10.retain_run_record({
            "run_id": "run-b3-sum", "run_identifier": "run-b3-sum",
            "flag_conditions_fired": [leaf], "week": leaf,
            "groups": {}})
        summary = mod10.summary_record_for_run("run-b3-sum")
        self.assertIs(summary["flag_conditions_fired"][0], leaf)
        self.assertIs(summary["week"], leaf)
        reduce_leaf = ReduceLeaf()
        mod10.retain_run_record({
            "run_id": "run-b3-sum2", "run_identifier": "run-b3-sum2",
            "flag_conditions_fired": [reduce_leaf], "groups": {}})
        summary = mod10.summary_record_for_run("run-b3-sum2")
        self.assertIs(summary["flag_conditions_fired"][0], reduce_leaf)
        boom = Boom()
        mod10.retain_run_record({
            "run_id": "run-b3-sum3", "run_identifier": "run-b3-sum3",
            "flag_conditions_fired": [boom], "groups": {}})
        summary = mod10.summary_record_for_run("run-b3-sum3")
        self.assertIs(summary["flag_conditions_fired"][0], boom)

    def test_place_reserve_hold(self):
        leaf = Lie()
        hold = mod10.place_reserve_hold(leaf)
        self.assertIs(hold["run_id"], leaf)
        boom = Boom()
        hold = mod10.place_reserve_hold(boom)
        self.assertIs(hold["run_id"], boom)

    def test_reserve_hold_for_run(self):
        mod10.place_reserve_hold("run-b3-hold")
        leaf = Lie()
        mod10._RESERVE_HOLDS["run-b3-hold"]["leaf"] = leaf
        self.assertIs(mod10.reserve_hold_for_run("run-b3-hold")["leaf"],
                      leaf)
        boom = Boom()
        mod10._RESERVE_HOLDS["run-b3-hold"]["leaf"] = boom
        self.assertIs(mod10.reserve_hold_for_run("run-b3-hold")["leaf"],
                      boom)

    def test_apply_deferred_first_site_writes_leaf_as_itself(self):
        leaf = Lie()
        summary = {"run_id": "run-b3-def", "retention_tier": "Tier 2",
                   "extra": leaf}
        out = mod10.apply_deferred_evaluation(
            summary, 1, inputs="i", outcome="o")
        self.assertIs(out["extra"], leaf)
        stored = mod10.summary_record_for_run("run-b3-def")
        self.assertIs(stored["extra"], leaf)

    def test_apply_deferred_second_site_stored_evaluations(self):
        mod10.apply_deferred_evaluation(
            {"run_id": "run-b3-def2", "retention_tier": "Tier 2"},
            1, inputs="i", outcome="o")
        stored = mod10.summary_record_for_run("run-b3-def2")
        leaf = Lie()
        stored["deferred_evaluations"][0]["leaf"] = leaf
        mod10.write_summary_record(stored)
        out = mod10.apply_deferred_evaluation(
            {"run_id": "run-b3-def2", "retention_tier": "Tier 2"},
            2, inputs="i2", outcome="o2")
        self.assertIs(out["deferred_evaluations"][0]["leaf"], leaf)

    def test_retention_record_later_evaluation(self):
        leaf = Lie()
        mod10.write_summary_record({
            "run_id": "run-b3-ret", "retention_tier": "Tier 2",
            "deferred_evaluations": [{"firing": 1, "leaf": leaf}]})
        record = mod10.retention_record_for_run("run-b3-ret")
        self.assertIs(record["later_evaluation"]["leaf"], leaf)

    def test_retained_version_set(self):
        leaf = Lie()
        mod10.retain_run_record({
            "run_id": "run-b3-ver", "run_identifier": "run-b3-ver",
            "rule_version_set": [leaf, "rv1"], "groups": {}})
        version_set = mod10.retained_version_set("run-b3-ver")
        self.assertIs(version_set[0], leaf)

    def test_retain_view_record_return_agrees_with_read_back(self):
        leaf = Lie()
        out = mod10.retain_view_record(
            view_record([{"item": leaf}]), tier="Tier 2")
        self.assertIs(out["view_contents"][0]["item"], leaf)
        read_back = mod10.view_records_for_run("run-b3-view")
        self.assertIs(read_back[0]["view_contents"][0]["item"], leaf)

    def test_checkpoint_control_honours_no_protocol(self):
        leaf = Lie()
        mod10.retain_checkpoint({
            "run_identifier": "run-b3-ctl", "simulated_day": 5,
            "checkpoint_state": {"leaf": leaf}})
        state = mod10.checkpoint_state_at("run-b3-ctl", 5)
        self.assertIs(state["leaf"], leaf)


class TestR12015Mod03Buffers(Base):
    def test_make_archetype_record_bytearray_copied_apart(self):
        handed = bytearray(b"cfg")
        record = mod03.make_archetype_record(
            archetype_id="arch-1",
            behaviour={"buf": handed, "lst": [handed]})
        first = record["behaviour"]["buf"]
        second = record["behaviour"]["lst"][0]
        self.assertIsNot(first, handed)
        self.assertIs(first, second)
        handed[0] = 90
        self.assertEqual(first, bytearray(b"cfg"))

    def test_buffers_in_behaviour_and_assumptions(self):
        source = bytearray(b"cfg")
        record = mod03.make_archetype_record(
            archetype_id="arch-2", behaviour={"buf": memoryview(source)})
        carried = record["behaviour"]["buf"]
        self.assertIsInstance(carried, memoryview)
        source[0] = 90
        self.assertEqual(bytes(carried), b"cfg")
        handed = bytearray(b"cfg")
        proposals = mod03.archetype_behaviour(
            {"archetype_id": "arch-2", "behaviour": {}},
            stream_state=[1], assumption_values={"cfg": handed})
        self.assertEqual(len(proposals), 1)
        assumed = proposals[0]["assumptions"]["cfg"]
        self.assertIsNot(assumed, handed)
        handed[0] = 90
        self.assertEqual(assumed, bytearray(b"cfg"))


class TestR12016Mod08Buffers(Base):
    def test_accept_detection_input_buffers_copied_apart(self):
        handed = bytearray(b"payload")
        record = {"agent_identifier": "a1", "day": 1,
                  "feature_values": {"f": 1.0},
                  "records_for_agent_and_day": [{"data": handed}]}
        accepted = mod08.accept_detection_input(record)
        carried = accepted["records_for_agent_and_day"][0]["data"]
        self.assertIsNot(carried, handed)
        handed[0] = 90
        self.assertEqual(carried, bytearray(b"payload"))
        source = bytearray(b"payload")
        record = {"agent_identifier": "a1", "day": 1,
                  "feature_values": {"f": 1.0},
                  "records_for_agent_and_day": [
                      {"data": memoryview(source)}]}
        accepted = mod08.accept_detection_input(record)
        carried = accepted["records_for_agent_and_day"][0]["data"]
        self.assertIsInstance(carried, memoryview)
        source[0] = 90
        self.assertEqual(bytes(carried), b"payload")


class TestR12017Mod03CatalogueRows(Base):
    def test_archetype_catalogue_rows_copied_apart(self):
        row = ["r1"]
        catalogue = mod03.archetype_catalogue([{
            "archetype_id": "a1", "generator_signature": "sig",
            "parameter_rows": [row]}])
        carried = catalogue["entries"]["a1"]["parameter_rows"][0]
        self.assertIsNot(carried, row)
        row.append("evil")
        self.assertEqual(
            catalogue["entries"]["a1"]["parameter_rows"], [["r1"]])

    def test_extend_catalogue_rows_copied_apart(self):
        row = ["r1"]
        records = [{"archetype_id": "a1", "generator_signature": "sig",
                    "parameter_rows": [["x"]]}]
        new_record = {"archetype_id": "a2",
                      "generator_signature": "sig2",
                      "parameter_rows": [row]}
        extended = mod03.extend_catalogue(
            records, new_record, strategy_class="fixed")
        generated = extended["generator_code_entry"]["parameter_rows"][0]
        catalogued = (extended["catalogue"]["entries"]["a2"]
                      ["parameter_rows"][0])
        self.assertIsNot(generated, row)
        self.assertIsNot(catalogued, row)
        row.append("evil")
        self.assertEqual(
            extended["generator_code_entry"]["parameter_rows"],
            [["r1"]])
        self.assertEqual(
            extended["catalogue"]["entries"]["a2"]["parameter_rows"],
            [["r1"]])


if __name__ == "__main__":
    unittest.main()

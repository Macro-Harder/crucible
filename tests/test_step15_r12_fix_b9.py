"""Fix wave 11 pins, Builder 9: Group 9, rows R11-107 to R11-112.

Row R11-107: MOD-03 construct_farm and build_farm group an
unordered member set by hash iteration order, so the grouping
and the internal edge counts vary by hash seed (Green 5
Finding R11-G5-01, High).

Row R11-108: MOD-09 strategy_catalogue appends identifiers
handed as a set in hash iteration order (Green 5 Finding
R11-G5-02, Low).

Row R11-109: MOD-04 build_view_record refuses a barred field
in one identical form for the contents, reputation_and_band,
and graph_position groups, naming neither the group nor the
barred field (Orange 2 Finding 3, Medium).

Row R11-110: MOD-04 ContractAHandover.verify_intact raises one
identical refusal whichever of its four handed values differs
(Orange 2 Finding 4, Low).

Row R11-111: the guard refusals at MOD-04 process_day_events,
select_view_records, and per_viewer_components name no item
position (Orange 2 Finding 5, Low).

Row R11-112: the MOD-04 projection cleaning refusal states
the bound of 100 without the counting clause, and a handed
depth of 100 stands admitted in feature values and refused in
a rule record because the record wrapper counts toward the
bound (Orange 2 Finding 6, Low).

Defect methods fail on the uncured modules and pass on the
cured modules. Control methods pass both ways.
"""
import json
import os
import subprocess
import sys
import unittest

from crucible import mod04


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROBE = (
    "import json\n"
    "from crucible import mod03, mod09\n"
    "members = {'member-a', 'member-b', 'member-c', 'member-d',"
    " 'member-e', 'member-f'}\n"
    "edges = [('member-a', 'member-b'), ('member-c', 'member-d'),"
    " ('member-e', 'member-f'), ('member-a', 'member-c')]\n"
    "out = {}\n"
    "out['farm_set'] = mod03.construct_farm(members, farm_size=2,"
    " edges=edges)\n"
    "out['farm_frozen'] = mod03.construct_farm(frozenset(members),"
    " farm_size=2, edges=edges)\n"
    "out['farm_alias'] = mod03.build_farm(members, farm_size=2,"
    " edges=edges)\n"
    "out['catalogue_set'] = mod09.strategy_catalogue("
    "extra_identifiers={'zeta', 'alpha', 'mid'})\n"
    "print(json.dumps(out, sort_keys=True))\n"
)

SEEDS = ("0", "1", "2", "4")

EXPECTED_FARMS = [
    ["member-a", "member-b"],
    ["member-c", "member-d"],
    ["member-e", "member-f"],
]
EXPECTED_COUNTS = {"farm-0": 1, "farm-1": 1, "farm-2": 1}
EXPECTED_CATALOGUE = ["conditional briber", "alpha", "mid", "zeta"]


def run_probe(seed):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = seed
    env["PYTHONPATH"] = ROOT
    completed = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=ROOT, env=env, capture_output=True, text=True,
        check=True)
    return json.loads(completed.stdout)


def chain(count):
    value = "leaf"
    for _ in range(count):
        value = [value]
    return value


def good_state():
    return {
        "agent_identifier": "agent-1",
        "day": 1,
        "feature_values": {"activity": 1},
        "rule_records": [],
    }


def farm_grouping(result):
    return [farm["member_ids"] for farm in result["farms"]]


class TestR11107FarmDeterminism(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.by_seed = {seed: run_probe(seed) for seed in SEEDS}

    def test_set_grouping_identical_across_seeds(self):
        for seed in SEEDS:
            result = self.by_seed[seed]["farm_set"]
            self.assertEqual(EXPECTED_FARMS, farm_grouping(result))
            self.assertEqual(
                EXPECTED_COUNTS,
                result["internal_edge_count_per_farm_identity"])

    def test_frozenset_grouping_identical_across_seeds(self):
        for seed in SEEDS:
            result = self.by_seed[seed]["farm_frozen"]
            self.assertEqual(EXPECTED_FARMS, farm_grouping(result))
            self.assertEqual(
                EXPECTED_COUNTS,
                result["internal_edge_count_per_farm_identity"])
            self.assertEqual(
                self.by_seed[seed]["farm_set"], result)

    def test_build_farm_alias_identical_across_seeds(self):
        for seed in SEEDS:
            self.assertEqual(
                self.by_seed[seed]["farm_set"],
                self.by_seed[seed]["farm_alias"])

    def test_control_list_order_preserved(self):
        from crucible import mod03
        handed = ["member-f", "member-a", "member-c",
                  "member-b", "member-e", "member-d"]
        result = mod03.construct_farm(handed, farm_size=2, edges=[])
        self.assertEqual(
            [["member-f", "member-a"], ["member-c", "member-b"],
             ["member-e", "member-d"]],
            farm_grouping(result))


class TestR11108CatalogueDeterminism(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.by_seed = {seed: run_probe(seed) for seed in SEEDS}

    def test_set_order_identical_across_seeds(self):
        for seed in SEEDS:
            self.assertEqual(
                EXPECTED_CATALOGUE,
                self.by_seed[seed]["catalogue_set"]["identifiers"])

    def test_control_list_order_preserved(self):
        from crucible import mod09
        result = mod09.strategy_catalogue(
            extra_identifiers=["zeta", "alpha", "mid"])
        self.assertEqual(
            ["conditional briber", "zeta", "alpha", "mid"],
            result["identifiers"])


def barred_message(**kwargs):
    try:
        mod04.build_view_record(**kwargs)
    except mod04.NamedFailure as exc:
        return str(exc)
    raise AssertionError("build_view_record did not refuse")


CLEAN_CONTENTS = [{"note": "clean", "first_seen_day": 1, "delay": 0}]


class TestR11109BarredFieldRefusal(unittest.TestCase):

    def contents_message(self):
        return barred_message(contents=[
            {"outer": [{"membership": 1}],
             "first_seen_day": 1, "delay": 0}])

    def reputation_message(self):
        return barred_message(
            contents=CLEAN_CONTENTS,
            reputation_and_band={"membership": 1})

    def graph_message(self):
        return barred_message(
            contents=CLEAN_CONTENTS,
            graph_position={"nested": {"membership": 1}})

    def test_contents_group_and_field_named(self):
        message = self.contents_message()
        self.assertIn("contents", message)
        self.assertIn("membership", message)

    def test_reputation_group_and_field_named(self):
        message = self.reputation_message()
        self.assertIn("reputation_and_band", message)
        self.assertIn("membership", message)

    def test_graph_group_and_field_named(self):
        message = self.graph_message()
        self.assertIn("graph_position", message)
        self.assertIn("membership", message)

    def test_three_refusals_pairwise_distinct(self):
        messages = {
            self.contents_message(),
            self.reputation_message(),
            self.graph_message(),
        }
        self.assertEqual(3, len(messages))

    def test_control_clean_record_written(self):
        record = mod04.build_view_record(
            contents=CLEAN_CONTENTS,
            reputation_and_band={"band": "b"},
            graph_position={"x": 1})
        self.assertEqual("ViewRecord", record["form"])


class TestR11110VerifyIntactRefusal(unittest.TestCase):

    def setUp(self):
        self.handover = mod04.ContractAHandover(
            "point-1", {"assumption": 1}, {"seed-1"}, "family-1")

    def message_for(self, *args):
        try:
            self.handover.verify_intact(*args)
        except mod04.AlterationBarred as exc:
            return str(exc)
        raise AssertionError("verify_intact did not refuse")

    def all_messages(self):
        return [
            self.message_for(
                "point-2", {"assumption": 1}, {"seed-1"}, "family-1"),
            self.message_for(
                "point-1", {"assumption": 2}, {"seed-1"}, "family-1"),
            self.message_for(
                "point-1", {"assumption": 1}, {"seed-2"}, "family-1"),
            self.message_for(
                "point-1", {"assumption": 1}, {"seed-1"}, "family-2"),
        ]

    def test_point_named(self):
        self.assertIn("point", self.all_messages()[0])

    def test_assumption_record_named(self):
        self.assertIn("assumption", self.all_messages()[1])

    def test_seed_input_set_named(self):
        self.assertIn("seed", self.all_messages()[2])

    def test_family_identifier_named(self):
        self.assertIn("family", self.all_messages()[3])

    def test_four_refusals_pairwise_distinct(self):
        self.assertEqual(4, len(set(self.all_messages())))

    def test_control_intact_handover_passes(self):
        self.assertTrue(self.handover.verify_intact(
            "point-1", {"assumption": 1}, {"seed-1"}, "family-1"))


class TestR11111GuardPositionRefusal(unittest.TestCase):

    def refusal(self, act):
        try:
            act()
        except mod04.NamedFailure as exc:
            return str(exc)
        raise AssertionError("the act did not refuse")

    def day_events_message(self, position):
        events = [{"kind": "work_submission"} for _ in range(3)]
        events[position] = {
            "kind": "work_submission", "deep": chain(120)}
        return self.refusal(
            lambda: mod04.process_day_events(good_state(), events))

    def select_message(self, position):
        records = []
        for index in range(3):
            record = {
                "viewer_id": "viewer-1", "first_seen_day": 1,
                "note": "x",
            }
            if index == position:
                record["deep"] = chain(120)
            records.append(record)
        return self.refusal(
            lambda: mod04.select_view_records(
                records, "viewer-1", 5))

    def components_message(self, position):
        components = [{"viewer_id": "viewer-1"} for _ in range(3)]
        components[position] = {
            "viewer_id": "viewer-1", "deep": chain(120)}
        return self.refusal(
            lambda: mod04.per_viewer_components(
                components=components))

    def test_process_day_events_position_named(self):
        first = self.day_events_message(0)
        third = self.day_events_message(2)
        self.assertIn("position 0", first)
        self.assertIn("position 2", third)
        self.assertNotEqual(first, third)

    def test_select_view_records_position_named(self):
        first = self.select_message(0)
        third = self.select_message(2)
        self.assertIn("position 0", first)
        self.assertIn("position 2", third)
        self.assertNotEqual(first, third)

    def test_per_viewer_components_position_named(self):
        first = self.components_message(0)
        third = self.components_message(2)
        self.assertIn("position 0", first)
        self.assertIn("position 2", third)
        self.assertNotEqual(first, third)

    def test_control_shallow_collections_run(self):
        result = mod04.process_day_events(
            good_state(), [{"kind": "work_submission"}])
        self.assertEqual(["apply", "project", "deliver"],
                         result["sequence"])
        selected = mod04.select_view_records(
            [{"viewer_id": "viewer-1", "first_seen_day": 1}],
            "viewer-1", 5)
        self.assertEqual(1, len(selected))
        copied = mod04.per_viewer_components(
            components=[{"viewer_id": "viewer-1"}])
        self.assertEqual(1, len(copied))


class TestR11112CleaningBoundForm(unittest.TestCase):

    def state_with(self, slot, depth):
        state = good_state()
        if slot == "feature":
            state["feature_values"] = {"deep": chain(depth)}
        else:
            state["rule_records"] = [{"deep": chain(depth)}]
        return state

    def refusal_for(self, slot, depth):
        try:
            mod04.project_detection_input(self.state_with(slot, depth))
        except mod04.NamedFailure as exc:
            return str(exc)
        raise AssertionError("the projection did not refuse")

    def test_depth_100_admitted_in_both_slots(self):
        for slot in ("feature", "rule"):
            projected = mod04.project_detection_input(
                self.state_with(slot, 100))
            self.assertEqual("agent-1", projected["agent_identifier"])

    def test_depth_101_refused_in_feature_values_with_counting_clause(self):
        message = self.refusal_for("feature", 101)
        self.assertIn("100", message)
        self.assertIn("counting every container", message)

    def test_depth_101_refused_in_rule_record_with_counting_clause(self):
        message = self.refusal_for("rule", 101)
        self.assertIn("100", message)
        self.assertIn("counting every container", message)

    def test_control_depth_99_admitted_in_both_slots(self):
        for slot in ("feature", "rule"):
            projected = mod04.project_detection_input(
                self.state_with(slot, 99))
            self.assertEqual("agent-1", projected["agent_identifier"])


if __name__ == "__main__":
    unittest.main()

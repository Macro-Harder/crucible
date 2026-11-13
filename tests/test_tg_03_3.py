import unittest

try:
    import crucible.mod03 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod03 absent, pinned behaviour unmet: " + behaviour)


def require_api(case, group, behaviour, names):
    require_surface(case, group, behaviour)
    for name in names:
        if hasattr(_surface_module, name):
            return getattr(_surface_module, name)
    case.fail(group + ": surface stands but no callable for pinned behaviour: " + behaviour)


class TestTG033(unittest.TestCase):
    def test_zero_edge_construction(self):
        """
        Fixture: F-03, zero edge counterexample, with attack edge count 0 and summed stake 0, anchor scenario AN-1 in place, the S3 acceptance rule and simplification S4 as stated, and external work access at genesis shaped rates.
        Pins: The Generator can construct the zero edge society exactly as the fixture states it, and the run record records the internal edge count per farm identity, which AC-3 needs for the zero edge witness shape.
        Bar: The mapping states the bar in the companion failure path test of this group.
        Failure: Fails while crucible.mod03 stands absent, and fails if the zero edge society cannot be constructed as the fixture states it or the per identity edge count stands unrecorded.
        """
        require_api(self, "TG-03.3", "zero edge society constructed exactly as fixture F-03 states it", ["construct_farm", "build_farm", "generate_society"])
        surface = _surface_module
        records = [
            surface.make_archetype_record(
                archetype_id="honest",
                behaviour={"action": "vouch"},
                parameter_rows=[{"row": "honest row"}],
                ground_truth_label="honest",
            ),
            surface.make_archetype_record(
                archetype_id="farm",
                behaviour={"action": "link"},
                parameter_rows=[{"row": "farm row"}],
                ground_truth_label="farm",
                farm_member=True,
            ),
        ]
        point = {
            "point_id": "TG-03.3 zero edge run",
            "population": 6,
            "archetype_mix": {"honest": 4, "farm": 2},
            "farm_size": 2,
            "anchor_set_description": "genesis anchor setting",
        }
        society = surface.zero_edge_society(
            point, records, strategy_class="fixed strategy")
        self.assertEqual(society["attack_edge_count"], 0)
        self.assertEqual(society["summed_stake"], 0)
        self.assertEqual(society["initial_graph"], {"edges": []})
        self.assertEqual(society["population"], 6)
        self.assertEqual(
            society["archetype_counts"], {"honest": 4, "farm": 2})
        self.assertEqual(
            society["farms"],
            [{"farm_id": "farm-0",
              "member_ids": ["agent-0004", "agent-0005"]}])
        self.assertEqual(
            society["internal_edge_count_per_farm"], {"farm-0": 0})
        self.assertEqual(
            society["anchor_scenario"],
            {"scenario_identifier": "AN-1",
             "anchor_set_description": "genesis anchor setting",
             "mark": surface.DQ163_MARK})
        direct = surface.construct_farm(
            ["member-1", "member-2", "member-3"], farm_size=2, edges=())
        self.assertEqual(
            direct["farms"],
            [{"farm_id": "farm-0", "member_ids": ["member-1", "member-2"]},
             {"farm_id": "farm-1", "member_ids": ["member-3"]}])
        self.assertEqual(
            direct["internal_edge_count_per_farm_identity"],
            {"farm-0": 0, "farm-1": 0})
        self.assertEqual(
            surface.build_farm(
                ["member-1", "member-2", "member-3"], farm_size=2, edges=()),
            direct)

    def test_zero_edge_result_names_simplification(self):
        """
        Fixture: F-03, zero edge counterexample, as in the happy path test of this group.
        Pins: The result on the simplified graph, the primary order parameter driven above one half by external direct credit, is reported only as a property of the simplified graph.
        Bar: A test reporting that result without the simplification named fails this group.
        Failure: Fails while crucible.mod03 stands absent, and fails if the simplified graph result is reported without the simplification named.
        """
        require_api(self, "TG-03.3", "simplified graph result reported only with the simplification named", ["construct_farm", "build_farm", "generate_society"])
        surface = _surface_module
        records = [
            surface.make_archetype_record(
                archetype_id="honest",
                behaviour={"action": "vouch"},
                parameter_rows=[{"row": "honest row"}],
                ground_truth_label="honest",
            ),
        ]
        point = {
            "point_id": "TG-03.3 result run",
            "population": 2,
            "archetype_mix": {"honest": 2},
        }
        society = surface.zero_edge_society(
            point, records, strategy_class="fixed strategy")
        self.assertEqual(society["attack_edge_count"], 0)
        self.assertEqual(society["summed_stake"], 0)
        result = surface.zero_edge_result()
        self.assertEqual(
            result,
            {"result": ("primary order parameter driven above one half "
                        "by external direct credit"),
             "standing": "property of the simplified graph only",
             "simplification_named": True,
             "simplification": "simplified graph, simplification S4"})
        self.assertTrue(result["simplification_named"])
        self.assertIn("S4", result["simplification"])
        self.assertEqual(
            result["standing"], "property of the simplified graph only")


if __name__ == "__main__":
    unittest.main()

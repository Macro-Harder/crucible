import unittest

try:
    import crucible.mod05 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod05 absent, pinned behaviour unmet: " + behaviour)


def require_api(case, group, behaviour, names):
    require_surface(case, group, behaviour)
    for name in names:
        if hasattr(_surface_module, name):
            return getattr(_surface_module, name)
    case.fail(group + ": surface stands but no callable for pinned behaviour: " + behaviour)


class TestTG042(unittest.TestCase):
    def test_component_counting_rule(self):
        """
        Fixture: A graph in which stake weight and edge count give different component sizes. Case set inside the test text, no inventory fixture.
        Pins: The component cap counts edges, not stake weight, per brief section 5.5, and each VouchEdge carries its component identifier under the component definition version in force, per Shape 8 and operation C-19.
        Bar: A snapshot computed under one component definition version read against edges under another version fails this group; the version travels with the snapshot.
        Failure: Fails while crucible.mod05 stands absent, and fails if the cap counts stake weight or a snapshot and its edges stand under different component definition versions.
        """
        require_api(self, "TG-04.2", "component cap counts edges and each VouchEdge carries its component identifier under the version in force", ["vouch", "component", "graph_snapshot"])
        surface = _surface_module
        edges = [
            surface.vouch("a", "b", 100, component_definition_version="v1"),
            surface.vouch("b", "a", 1, component_definition_version="v1"),
        ]
        comp = surface.component(edges, component_definition_version="v1")
        self.assertEqual(comp["largest_mutually_vouching_component_size"], 2)
        self.assertEqual(comp["component_list"][0]["stake_total"], 101)
        self.assertEqual(comp["counting_rule"], "edges, not stake weight")
        self.assertTrue(surface.component_cap_check(edges, 2))
        self.assertFalse(surface.component_cap_check(edges, 1))
        for edge in edges:
            self.assertIn("component_identifier", edge)
            self.assertEqual(edge["component_definition_version"], "v1")
        snapshot = surface.graph_snapshot(edges, component_definition_version="v1")
        self.assertTrue(surface.validate_graph_snapshot(snapshot, edges))
        wrong = surface.graph_snapshot(edges, component_definition_version="v2")
        self.assertFalse(surface.validate_graph_snapshot(wrong, edges))

    def test_evaluation_order_carriage(self):
        """
        Fixture: A case set exercising band membership, panel eligibility, and cap eligibility in one day. No inventory fixture.
        Pins: Eligibility judgements read the reputation score produced through the aggregation interface this slice builds, with the recommended candidate behind that interface as a comparison form only, in the evaluation order the record states. The selector stands open, no aggregation rule stands adopted, and this test pins the interface and the bar only, until a decision record adopts a rule by name and version.
        Bar: The evaluation order recommendation, order O-1 with a batch of one simulated day, order O-5 as a named sensitivity arm, stands as a recommendation and not a ruling, with judgement points and gaps open at NQ-46, open point OP-08; tests pin the order the family record states and fail any run whose order is unstated, and no test presents O-1 as ruled.
        Failure: Fails while crucible.mod05 stands absent, and fails if a run order stands unstated or O-1 is presented as ruled.
        """
        require_api(self, "TG-04.2", "eligibility judgements read the aggregation interface score in the order the record states", ["band_membership", "eligibility", "aggregation_score"])
        surface = _surface_module
        order = surface.evaluation_order_record("O-1")
        self.assertEqual(order["standing"], "recommendation, not a ruling")
        self.assertFalse(order["presented_as_ruled"])
        self.assertEqual(order["sensitivity_arm"], "O-5")
        self.assertTrue(surface.validate_evaluation_order(order))
        bands = [("low", 0), ("high", 10)]
        result = surface.band_membership(12, bands, evaluation_order=order)
        self.assertEqual(result["band"], "high")
        self.assertEqual(result["score_source"], "aggregation interface, comparison form only")
        unstated = surface.evaluation_order_record(None)
        self.assertFalse(surface.validate_evaluation_order(unstated))
        with self.assertRaises(ValueError):
            surface.band_membership(12, bands, evaluation_order=unstated)
        ruled = dict(order)
        ruled["presented_as_ruled"] = True
        self.assertFalse(surface.validate_evaluation_order(ruled))


if __name__ == "__main__":
    unittest.main()

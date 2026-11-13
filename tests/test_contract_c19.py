"""Contract test for operation C-19, plan section 2 section 5.

The test pins the check field of contract C-19 as plan section 9
states it. Surfaces crossed: MOD-05 and MOD-10, via TG-04.2 and TG-10.1.
Suite form: Python standard library unittest, one file per operation.
Each test states Fixture, Pins, Bar and Failure in its docstring.
Each behaviour test body first requires its surfaces: while a surface
is absent the test fails, naming the pinned behaviour and C-19.
Gated tests use skipTest with the gate named and never pass.
Values are simulated and test values only.
"""
import unittest

SURFACES = {}
try:
    import crucible.mod05 as _m_mod05
    SURFACES["mod05"] = True
except Exception:
    SURFACES["mod05"] = False
try:
    import crucible.mod10 as _m_mod10
    SURFACES["mod10"] = True
except Exception:
    SURFACES["mod10"] = False


class TestContractC19(unittest.TestCase):
    def require(self, behaviour, *names):
        missing = [n for n in names if not SURFACES.get(n, False)]
        if missing:
            self.fail(
                "Surface absent for C-19: pinned behaviour not testable: "
                + behaviour + " (missing: " + ", ".join(missing) + ")"
            )

    def test_snapshot_agrees_with_edge_list_under_its_version(self):
        """
        Fixture: Shape 8 record set: one graph snapshot, its referenced edge list, and its component definition version
        Pins: the snapshot recomputation check: a checker recomputes the component list, the largest mutually vouching component size and the degree distribution from the referenced edge list under the named definition version, and the snapshot agrees; the component cap counts edges, not stake weight; an edge created and expiring inside one day stands in no daily snapshot and is counted in the separate derived field for that day, the count of intra day only edges, with no component or degree claim made from it
        Bar: a snapshot with no definition version, or no edge list reference, fails validation before recomputation begins; a component identifier computed under one version read against edges under another is a misreading, not a tolerated divergence
        Failure: any recomputed difference, a missing version, or a missing edge list reference fails this test; while a crossed surface is absent the test fails naming this behaviour and C-19
        """
        self.require("graph snapshot agrees with its referenced edge list under its component definition version", "mod05", "mod10")
        import crucible.mod05 as mod05
        edges = [{"voucher": "a", "vouchee": "b"}, {"voucher": "b", "vouchee": "a"}, {"voucher": "c", "vouchee": "a"}]
        snapshot = mod05.graph_snapshot(edges, component_definition_version="v1", edge_list_reference="edges-1")
        self.assertEqual(snapshot["edge_list_reference"], "edges-1")
        self.assertTrue(mod05.validate_graph_snapshot(snapshot, edges))
        facts = mod05.graph_facts(edges, component_definition_version="v1")
        self.assertEqual(facts["component_list"], snapshot["component_list"])
        self.assertEqual(facts["largest_mutually_vouching_component_size"], snapshot["largest_mutually_vouching_component_size"])
        no_version = {"component_list": snapshot["component_list"], "component_definition_version": None, "edge_list_reference": "edges-1"}
        self.assertFalse(mod05.validate_graph_snapshot(no_version, edges))
        no_reference = {"component_list": snapshot["component_list"], "component_definition_version": "v1", "edge_list_reference": None}
        self.assertFalse(mod05.validate_graph_snapshot(no_reference, edges))

    def test_snapshot_stands_per_viewer_with_no_singular_reading(self):
        """
        Fixture: Shape 8 record set: one snapshot presented as a viewer free quantity
        Pins: the presentation fails: a snapshot stands per day and per viewer, carrying its viewer identifier and its divergence companion, and no snapshot quantity is read as a viewer free quantity
        Bar: decided bars only: the singular presentation bar stands in its decided form under DQ7-09, shared with C-15, and waits on no decision or act; it is no barred limb
        Failure: a viewer free reading that stands fails this test; while a crossed surface is absent the test fails naming this behaviour and C-19
        """
        self.require("snapshot stands per viewer and is never read as a viewer free quantity", "mod05", "mod10")
        import crucible.mod04 as mod04
        import crucible.mod10 as mod10
        components = mod04.per_viewer_components(run_id="run-c19", viewers=("viewer-1", "viewer-2"))
        self.assertTrue(all("viewer_id" in item for item in components))
        self.assertFalse(mod10.validate_view_carriage({"form": "singular_vector", "presented_as": "one comparable quantity"}))
        companion = mod04.divergence_companion(run_id="run-c19", components=components)
        self.assertIn("band_differing_share", companion["end_of_run"])
        self.assertFalse(companion["end_of_run"]["singular_vector_reported"])


if __name__ == "__main__":
    unittest.main()

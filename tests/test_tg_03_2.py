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


class TestTG032(unittest.TestCase):
    def test_archetype_determinism(self):
        """
        Fixture: One archetype generator run twice on the same stream state and the same labelled assumption values. No inventory fixture.
        Pins: Archetype generators are deterministic functions of their stream state and their labelled assumption values, per Contract B and decision D-01.
        Bar: No language model takes any part in behaviour generation (decision D-14), and a generator whose output varies across the two runs on identical inputs fails this group and marks the run non deterministic under AC-1 handling at TG-14.1.
        Failure: Fails while crucible.mod03 stands absent, and fails if the two runs on identical inputs differ.
        """
        require_api(self, "TG-03.2", "archetype behaviour is a deterministic function of stream state and labelled assumptions", ["archetype_behaviour", "generate_behaviour", "run_archetype"])
        surface = _surface_module
        record = surface.make_archetype_record(
            archetype_id="honest",
            behaviour={"action": "link"},
            parameter_rows=[{"rate": 3}],
            ground_truth_label="honest",
        )
        self.assertEqual(
            record["generator_signature"],
            "behaviour(stream_state, labelled_assumptions)")
        stream_values = [0.125, 0.5, 0.875]
        assumptions = {"assumption label": "genesis rate", "value": 2}
        first = surface.archetype_behaviour(
            record, stream_state=stream_values,
            assumption_values=assumptions, agent_id="agent-0007")
        second = surface.run_archetype(
            record, stream_state=list(stream_values),
            assumption_values=dict(assumptions), agent_id="agent-0007")
        third = surface.generate_behaviour(
            record, stream_state=list(stream_values),
            assumption_values=dict(assumptions), agent_id="agent-0007")
        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual([item["draw"] for item in first], stream_values)
        for proposal in first:
            self.assertEqual(proposal["agent_id"], "agent-0007")
            self.assertEqual(proposal["archetype_id"], "honest")
            self.assertEqual(proposal["action"], "link")
            self.assertEqual(proposal["assumptions"], assumptions)
        different = surface.archetype_behaviour(
            record, stream_state=[0.5],
            assumption_values=assumptions, agent_id="agent-0007")
        self.assertNotEqual(first, different)

    def test_catalogue_honesty(self):
        """
        Fixture: The archetype catalogue the plan names under open point OP-11. No inventory fixture.
        Pins: Every archetype identifier an AgentState can carry appears in the catalogue with its generator signature and parameter rows, or the run using it is not headline reportable.
        Bar: The cast words in the brief head (honest, sloppy, Sybil farms, sleepers, colluding rings) are not a typed catalogue, and a test treating them as one fails this group.
        Failure: Fails while crucible.mod03 stands absent, and fails if an archetype identifier stands outside the catalogue or the brief head words are treated as the catalogue.
        """
        require_api(self, "TG-03.2", "archetype catalogue carries every archetype identifier with signature and parameter rows", ["archetype_catalogue", "catalogue"])
        surface = _surface_module
        records = [
            surface.make_archetype_record(
                archetype_id="honest",
                behaviour={"action": "vouch"},
                parameter_rows=[{"row": "honest row"}],
                ground_truth_label="honest",
            ),
            surface.make_archetype_record(
                archetype_id="sleeper",
                behaviour={"action": "wait"},
                parameter_rows=[{"row": "sleeper row"}],
                ground_truth_label="sleeper",
            ),
        ]
        catalogue = surface.archetype_catalogue(records)
        self.assertEqual(catalogue["standing"], "open at OP-11")
        self.assertEqual(set(catalogue["entries"]), {"honest", "sleeper"})
        for record in records:
            self.assertEqual(
                catalogue["entries"][record["archetype_id"]],
                {"generator_signature": record["generator_signature"],
                 "parameter_rows": record["parameter_rows"]})
        self.assertEqual(
            catalogue["gaps_carried_open"],
            ["honest adaptive rewiring",
             "a targeted linking adversary parameter",
             "adaptive sleeper concealment"])
        self.assertEqual(catalogue["gaps_carried_open"], list(surface.OP11_GAPS))
        self.assertFalse(catalogue["brief_head_words_treated_as_catalogue"])
        self.assertFalse(surface.brief_head_words_are_catalogue())
        self.assertEqual(surface.catalogue(records), catalogue)
        self.assertEqual(surface.catalogue_record(records), catalogue)
        point = {
            "point_id": "TG-03.2 catalogue run",
            "population": 3,
            "archetype_mix": {"honest": 2, "sleeper": 1},
        }
        cast = surface.build_cast(point, records, strategy_class="fixed strategy")
        cast_ids = {agent["archetype_id"] for agent in cast["cast"]}
        self.assertEqual(cast_ids, {"honest", "sleeper"})
        self.assertTrue(cast_ids.issubset(set(catalogue["entries"])))
        self.assertTrue(
            surface.run_headline_reportable(sorted(cast_ids), records))
        self.assertFalse(
            surface.run_headline_reportable(
                ["honest", "not in catalogue"], records))


if __name__ == "__main__":
    unittest.main()

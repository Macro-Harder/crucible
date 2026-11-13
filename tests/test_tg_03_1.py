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


class TestTG031(unittest.TestCase):
    def test_full_cast_and_initial_graph_before_day_one(self):
        """
        Fixture: A run start with the cast list, archetype counts, and role assignments the SweepPoint names. No inventory fixture.
        Pins: The Generator delivers the full cast and the initial graph before day one, and delivers nothing into the run after that point except behaviour through the behaviour streams, per Contract B.
        Bar: A cast that grows or changes membership after day one outside the entry rules the point states fails this group.
        Failure: Fails while crucible.mod03 stands absent, and fails if delivery after day one or a late membership change is accepted.
        """
        require_api(self, "TG-03.1", "full cast and initial graph delivered before day one", ["deliver_cast", "generate_society", "build_cast"])
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
        point = {
            "point_id": "TG-03.1 run start",
            "population": 4,
            "archetype_mix": {"honest": 3, "sleeper": 1},
        }
        edges = [
            {"voucher": "agent-0000", "vouchee": "agent-0001", "stake": 5},
            {"voucher": "agent-0002", "vouchee": "agent-0003", "stake": 7},
        ]
        cast = surface.deliver_cast(
            point, records, stream_state={"cast": [0.1, 0.2, 0.3, 0.4]},
            strategy_class="fixed strategy", initial_edges=edges)
        self.assertEqual(cast["delivery_point"], "before day one")
        self.assertEqual(cast["point_id"], "TG-03.1 run start")
        self.assertEqual(cast["strategy_class"], "fixed strategy")
        self.assertEqual(cast["population"], 4)
        self.assertEqual(cast["archetype_counts"], {"honest": 3, "sleeper": 1})
        self.assertEqual(len(cast["cast"]), 4)
        self.assertEqual(
            [agent["agent_id"] for agent in cast["cast"]],
            ["agent-0000", "agent-0001", "agent-0002", "agent-0003"])
        self.assertEqual(
            [agent["archetype_id"] for agent in cast["cast"]],
            ["honest", "honest", "honest", "sleeper"])
        self.assertEqual(cast["initial_graph"], {"edges": edges})
        self.assertEqual(
            surface.cast_agent_record(cast["cast"][3]),
            {"agent_identifier": "agent-0003",
             "archetype_identifier": "sleeper",
             "membership_ground_truth": "sleeper"})
        self.assertEqual(
            cast["deliveries_after_day_one"],
            "behaviour through the behaviour streams only")
        grown_point = dict(point)
        grown_point["archetype_mix"] = {"honest": 4, "sleeper": 1}
        with self.assertRaises(ValueError):
            surface.deliver_cast(
                grown_point, records, strategy_class="fixed strategy")
        changed_point = dict(point)
        changed_point["archetype_mix"] = {"honest": 3, "outsider": 1}
        with self.assertRaises(ValueError):
            surface.deliver_cast(
                changed_point, records, strategy_class="fixed strategy")
        with self.assertRaises(ValueError):
            surface.deliver_cast(point, records, strategy_class=None)

    def test_no_rule_state_in_generator(self):
        """
        Fixture: A Generator output carrying a reputation, stake, or contract effect. No inventory fixture.
        Pins: The Generator proposes actions and holds no rule state; the rule cores decide what actions do.
        Bar: A Generator output that a core accepts as a decided effect fails this group at the core boundary as well. The mapping states no separate bar sentence beyond this failure form.
        Failure: Fails while crucible.mod03 stands absent, and fails if a Generator output is accepted as a decided effect.
        """
        require_api(self, "TG-03.1", "Generator holds no rule state and proposes actions only", ["deliver_cast", "generate_society", "build_cast"])
        surface = _surface_module
        self.assertFalse(surface.generator_holds_rule_state())
        record = surface.make_archetype_record(
            archetype_id="honest",
            behaviour={"action": "vouch"},
            parameter_rows=[{"row": "honest row"}],
            ground_truth_label="honest",
        )
        self.assertEqual(
            set(record).intersection(surface.RULE_STATE_FIELDS), set())
        self.assertNotIn("strategy_class", record)
        proposals = surface.archetype_behaviour(
            record, stream_state=[0.25, 0.75],
            assumption_values={"labelled": "case"}, agent_id="agent-0000")
        self.assertEqual(len(proposals), 2)
        self.assertEqual([item["draw"] for item in proposals], [0.25, 0.75])
        for proposal in proposals:
            self.assertEqual(
                set(proposal),
                {"agent_id", "archetype_id", "action", "draw", "assumptions"})
            self.assertEqual(
                set(proposal).intersection(surface.RULE_STATE_FIELDS), set())
            self.assertEqual(proposal["action"], "vouch")
            self.assertEqual(proposal["assumptions"], {"labelled": "case"})
        self.assertTrue(surface.validate_generator_output(proposals))
        for field in surface.RULE_STATE_FIELDS:
            poisoned = dict(proposals[0])
            poisoned[field] = "decided"
            self.assertFalse(
                surface.validate_generator_output([poisoned]), field)
            self.assertFalse(surface.validate_generator_output(poisoned), field)


class TestStep15Fix1RecursionBounds(unittest.TestCase):
    """Step 15 Round 1 fix pins: TA-03, on the MOD-03 barred key and cleaning surfaces."""

    def test_cyclic_inputs_raise_the_module_named_failure(self):
        require_surface(self, "TG-03.1", "cyclic inputs raise the module named failure, never a bare RecursionError")
        surface = _surface_module
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaises(surface.NamedGeneratorFailure):
            surface.record_carries_ground_truth(cyclic)
        with self.assertRaises(surface.NamedGeneratorFailure):
            surface.strip_ground_truth({"wrap": cyclic})

    def test_deep_inputs_raise_the_module_named_failure(self):
        require_surface(self, "TG-03.1", "deep inputs raise the module named failure at the stated bound, with the path")
        surface = _surface_module
        deep = {"leaf": 1}
        for _ in range(2000):
            deep = {"nested": deep}
        with self.assertRaises(surface.NamedGeneratorFailure) as caught:
            surface.record_carries_ground_truth(deep)
        self.assertIn("nested", str(caught.exception))
        with self.assertRaises(surface.NamedGeneratorFailure):
            surface.strip_ground_truth(deep)

    def test_ordinary_nested_inputs_still_work(self):
        require_surface(self, "TG-03.1", "ordinary nested inputs still read and strip as before")
        surface = _surface_module
        record = {"feature_values": {"nested": {"membership": "x", "activity": 1}}}
        self.assertTrue(surface.record_carries_ground_truth(record))
        self.assertEqual(
            surface.strip_ground_truth(record),
            {"feature_values": {"nested": {"activity": 1}}},
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from crucible import mod03, mod04, mod05, mod06, mod08, mod11, mod12


class IterList(list):
    def __init__(self, stored, fabricated):
        super().__init__(stored)
        self._fabricated = list(fabricated)

    def __iter__(self):
        return iter(self._fabricated)


class NoContainer:
    def __init__(self, fabricated, length=None):
        self._fabricated = list(fabricated)
        self._length = len(self._fabricated) if length is None else length

    def __iter__(self):
        return iter(self._fabricated)

    def __len__(self):
        return self._length


class LyingGetDict(dict):
    def __init__(self, stored, fabricated_get):
        super().__init__(stored)
        self._fabricated_get = dict(fabricated_get)

    def get(self, key, default=None):
        if key in self._fabricated_get:
            return self._fabricated_get[key]
        return super().get(key, default)


class RaisingGetDict(dict):
    def get(self, key, default=None):
        raise RuntimeError("fabricated get failure")


def tri_edges():
    return [
        {"voucher": "a", "vouchee": "b"},
        {"voucher": "b", "vouchee": "a"},
        {"voucher": "a", "vouchee": "c"},
    ]


class TestR16007(unittest.TestCase):
    def test_component_cap_check_list_subclass(self):
        self.assertFalse(mod05.component_cap_check(tri_edges(), 1))
        dressed = IterList(tri_edges(), [])
        self.assertFalse(mod05.component_cap_check(dressed, 1))

    def test_graph_facts_list_subclass(self):
        dressed = IterList([], tri_edges()[:1])
        facts = mod05.graph_facts(dressed)
        self.assertEqual(facts["edge_list_reference"], [])


class TestR16008(unittest.TestCase):
    def test_plain_control(self):
        share = mod05.gate_passing_share(["a", "b"], ["a"])
        self.assertEqual(share["numerator"], 1)
        self.assertEqual(share["denominator"], 2)

    def test_eligible_fabricated(self):
        dressed = IterList([], ["a", "b"])
        self.assertEqual(
            mod05.gate_passing_share(dressed, ["a"]), mod05.UNKNOWN_SHARE)

    def test_passing_fabricated(self):
        dressed = IterList([], ["a"])
        share = mod05.gate_passing_share(["a"], dressed)
        self.assertEqual(share["numerator"], 0)
        self.assertEqual(share["denominator"], 1)


class TestR16009(unittest.TestCase):
    def test_plain_control(self):
        result = mod04.measure_order_sensitivity({"k": 1}, {"k": 1})
        self.assertEqual(result["divergence"], 0)
        self.assertFalse(result["states_differ"])

    def test_lying_get(self):
        second = LyingGetDict({"k": 1}, {"k": 2})
        result = mod04.measure_order_sensitivity({"k": 1}, second)
        self.assertEqual(result["divergence"], 0)
        self.assertFalse(result["states_differ"])

    def test_raising_get(self):
        second = RaisingGetDict({"k": 1})
        result = mod04.measure_order_sensitivity({"k": 1}, second)
        self.assertEqual(result["divergence"], 0)


class TestR16010(unittest.TestCase):
    def test_fallback_object(self):
        clean = mod06.dq_arrival_table()
        filled = [dict(row) for row in clean]
        filled[0]["final_column"] = "filled"
        self.assertFalse(mod06.validate_dq_arrival_table(filled))
        dressed = NoContainer(clean)
        dressed._stored = filled
        self.assertFalse(mod06.validate_dq_arrival_table(dressed))


class TestR16011(unittest.TestCase):
    def test_empty_stored_fabricated_replicate(self):
        dressed = IterList([], [{"first_terminal_regime": "X"}])
        figure = mod11.transition_figure(dressed)
        self.assertEqual(figure["denominator"], 0)
        self.assertEqual(figure["cumulative_incidence"], {})

    def test_fabricated_competing(self):
        stored = [{"first_terminal_regime": "X"}]
        fabricated = stored + [{"competing_exit": True}]
        figure = mod11.transition_figure(IterList(stored, fabricated))
        self.assertEqual(figure["competing_events"], 0)
        self.assertEqual(figure["denominator"], 1)


class TestR16012(unittest.TestCase):
    def _record(self):
        return {
            "agent_identifier": "agent-r16",
            "day": 1,
            "feature_values": {"activity": 1},
            "records_for_agent_and_day": [],
        }

    def test_plain_control(self):
        layer = mod08.DetectionLayer()
        result = layer.score([self._record()])
        self.assertEqual(len(result["detection_states"]), 1)

    def test_list_subclass_fabricated(self):
        layer = mod08.DetectionLayer()
        dressed = IterList([], [self._record()])
        result = layer.score(dressed)
        self.assertEqual(len(result["detection_states"]), 0)
        self.assertEqual(layer.detection_states, {})


class TestR16031(unittest.TestCase):
    def test_work_credit_no_container(self):
        event = {"agent_identifier": "ghost", "accepted": True}
        result = mod05.work_credit(NoContainer([event]))
        self.assertNotIn("ghost", result.get("counters", {}))

    def test_recomputation_sample_no_container(self):
        dressed = NoContainer(["r1", "ghost"])
        self.assertEqual(mod05.recomputation_sample(dressed), [])

    def test_by_epoch_no_dict(self):
        class NoDict:
            def items(self):
                return [("epoch-1", [
                    {"voucher": "a", "vouchee": "b"},
                    {"voucher": "b", "vouchee": "a"}])]

        result = mod05.realised_degree_distribution([], by_epoch=NoDict())
        self.assertEqual(result["by_epoch"], {})


class TestR16032(unittest.TestCase):
    def _headline(self, traces):
        return {
            "axes": mod11.AXES,
            "traces": traces,
            "rests_on_axis": "external work issuance",
            "zero_edge_witness_shape": "zero edge witness shape from F-03",
        }

    def test_plain_empty_traces_control(self):
        headline = self._headline([])
        self.assertFalse(mod11.validate_bounding_headline(
            headline, {"near_zero_bound": 0},
            {"farm_internal_edge_count": 5}))

    def test_traces_no_container(self):
        traces = [{"moved": True}, {"moved": False}, {"moved": True}]
        dressed = NoContainer(traces, length=3)
        headline = self._headline(dressed)
        self.assertFalse(mod11.validate_bounding_headline(
            headline, {"near_zero_bound": 0},
            {"farm_internal_edge_count": 5}))


class TestR16033(unittest.TestCase):
    def test_claims_list_subclass(self):
        dressed = IterList(["stored claim"], ["fabricated claim"])
        record = mod12.make_family_record(claims=dressed)
        self.assertEqual(record["claims"], ["stored claim"])
        self.assertEqual(record["headline_claims"], ["stored claim"])


class TestR16034(unittest.TestCase):
    def _records(self):
        honest = mod03.make_archetype_record(
            archetype_id="honest", behaviour={"action": "vouch"})
        farm = mod03.make_archetype_record(
            archetype_id="farm", behaviour={"action": "link"},
            farm_member=True)
        return [farm, honest]

    def _point(self, cls=dict):
        stored = {
            "population": 2,
            "archetype_mix": {"farm": 2},
            "farm_size": 2,
            "initial_edges": [],
            "anchor_set_description": "stored desc",
        }
        if cls is dict:
            return stored
        return cls(stored, {"anchor_set_description": "fabricated desc"})

    def test_plain_control(self):
        society = mod03.zero_edge_society(
            self._point(), self._records(), strategy_class="fixed")
        self.assertIn("stored desc", str(society["anchor_scenario"]))

    def test_lying_get(self):
        society = mod03.zero_edge_society(
            self._point(LyingGetDict), self._records(),
            strategy_class="fixed")
        self.assertIn("stored desc", str(society["anchor_scenario"]))
        self.assertNotIn("fabricated desc", str(society["anchor_scenario"]))

    def test_raising_get(self):
        point = RaisingGetDict(self._point())
        society = mod03.zero_edge_society(
            point, self._records(), strategy_class="fixed")
        self.assertIn("stored desc", str(society["anchor_scenario"]))


class TestR16035(unittest.TestCase):
    def test_lying_get_refusal_choice(self):
        stored = mod05.evaluation_order_record(None)
        dressed = LyingGetDict(stored, {"order": "O-1"})
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(5, [("band", 1)], evaluation_order=dressed)
        self.assertIn("no order stands stated", str(caught.exception))

    def test_raising_get_refusal_choice(self):
        stored = mod05.evaluation_order_record(None)
        dressed = RaisingGetDict(stored)
        with self.assertRaises(ValueError) as caught:
            mod05.band_membership(5, [("band", 1)], evaluation_order=dressed)
        self.assertIn("no order stands stated", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

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


class TestTG043(unittest.TestCase):
    def test_one_implemented_comparison_rule(self):
        """
        Fixture: A fixed set of credits, vouches, and penalties scored under the recommended candidate in its comparison form. No inventory fixture.
        Pins: The comparison form behind the aggregation interface produces one reputation score for an agent inside the comparison programme, per operation C-18, and the interface, the candidate carriage, and the bar are what this test pins.
        Bar: The recommended candidate stands as a comparison form only and not as an adoption, the selector stands open at SEL-10 read with register item NQ-64 and open point OP-09; no headline answer rests on any candidate, and no headline rests on an eigenvector candidate while contested entry C-5 stands. A test that names a rule as the adopted rule, by name and version or in any other wording, fails this group until a decision record adopts a rule by name and version.
        Failure: Fails while crucible.mod05 stands absent, and fails if the comparison form produces no score or more than one score, or a rule is named as adopted.
        """
        require_api(self, "TG-04.3", "aggregation comparison form produces one reputation score inside the comparison programme", ["aggregate_reputation", "aggregation_score", "compare_aggregation"])
        surface = _surface_module
        inputs = {
            "agent_identifier": "agent-a",
            "accepted_work": 5,
            "vouches_received": [{"stake": 3, "score_bearing_flag": True}],
            "penalties": 1,
        }
        result = surface.aggregate_reputation(inputs)
        self.assertEqual(result["scores"], [7])
        self.assertEqual(result["score"], 7)
        self.assertEqual(result["form"], "comparison form only")
        self.assertFalse(result["adopted"])
        self.assertIsNone(result["adopted_rule"])
        self.assertFalse(result["headline_use_permitted"])
        interface = surface.aggregation_interface()
        self.assertIsNone(interface["adopted_rule"])
        self.assertTrue(interface["candidate_includes_sym_ctl"])

    def test_candidate_1_negative_fixture(self):
        """
        Fixture: F-15, Candidate 1 split decay case (70 percent volatile at a 90 day half life, 30 percent seasoned at a 730 day half life, penalty bucket at 270 days), with fixture F-14, the decay slice set, beside it.
        Pins: While the decay mapping at NQ-58 stands open, no single retention run, hysteresis readout, or aggregation comparison is reported as testing Candidate 1 as written, and every decay arm result and aggregation comparison states on its face that neither decay arm tests Candidate 1 as written and that the aggregation comparison is unspecified for Candidate 1 as written, per AC-8.
        Bar: A result missing either face statement fails this group even where its numbers are correct.
        Failure: Fails while crucible.mod05 stands absent, and fails if a result is reported as testing Candidate 1 as written or either face statement stands missing.
        """
        require_api(self, "TG-04.3", "no result reported as testing Candidate 1 as written and both AC-8 face statements carried", ["aggregate_reputation", "decay_result", "compare_aggregation"])
        surface = _surface_module
        result = surface.decay_result(69)
        self.assertFalse(result["tests_candidate_1_as_written"])
        self.assertEqual(result["face_statements"], list(surface.AC8_FACE_STATEMENTS))
        self.assertIn("neither decay arm tests Candidate 1 as written", result["face_statements"])
        self.assertIn("the aggregation comparison is unspecified for Candidate 1 as written", result["face_statements"])
        comparison = surface.aggregate_reputation({"agent_identifier": "agent-a", "accepted_work": 1})
        self.assertEqual(comparison["face_statements"], list(surface.AC8_FACE_STATEMENTS))

    def test_decay_slice_coverage(self):
        """
        Fixture: F-14, decay slice set.
        Pins: At least six decay slices in every plane the arm reports (half life 7 days, about 14 days, about 69 days, a slice at the 180 day run length scale, about 693 days, and infinite), with carried variant W-02 folded in as the zero decay edge at daily retention 1.0 and not as a separate arm, and paired cold and hot starts with the hot start donor conditions the fixture states.
        Bar: The two extension slices (half life 1 day and half life 3 days) are a weighed extension only, labelled as an outside range extension, each result carrying the honest side readout; an unlabelled extension result fails this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if a reported plane carries fewer than six slices, W-02 stands as a separate arm, or an extension result stands unlabelled.
        """
        require_api(self, "TG-04.3", "decay slice coverage of at least six slices with W-02 folded in and extension slices labelled", ["decay_slices", "decay_result", "aggregate_reputation"])
        surface = _surface_module
        slices = surface.decay_slices()
        plane = [s for s in slices if not s.get("extension") and s.get("variant") != "W-02"]
        self.assertGreaterEqual(len(plane), 6)
        self.assertEqual([s["half_life_days"] for s in plane], [7, 14, 69, 180, 693, None])
        w02 = [s for s in slices if s.get("variant") == "W-02"]
        self.assertEqual(len(w02), 1)
        self.assertTrue(w02[0]["folded_in"])
        self.assertFalse(w02[0]["separate_arm"])
        self.assertEqual(w02[0]["daily_retention"], 1.0)
        extensions = [s for s in slices if s.get("extension")]
        self.assertEqual([s["half_life_days"] for s in extensions], [1, 3])
        for entry in extensions:
            self.assertEqual(entry["extension_label"], "outside range extension")
            self.assertTrue(entry["honest_side_readout"])
            shown = surface.decay_result(entry["half_life_days"])
            self.assertEqual(shown["extension_label"], "outside range extension")

    def test_alternation_retention_pins_folded_g2_c08(self):
        """
        Fixture: F-14, the decay slice set, with F-15, the Candidate 1 split decay case, beside it, as TG-04.3 states, under folded Amendment G2-C08.
        Pins: For each decay slice, whether the retention applied to penalised behaviour and to accepted good work in that slice was the same rate or different rates, stated from the rule record; and the count of prior bad phases still present in the rule state at each exclusion.
        Bar: An alternation result that reports neither pin is reported as a band result under alternation, and not as a result about misbehaviour retention.
        Failure: Fails while crucible.mod05 stands absent, and fails if an alternation result reports neither pin yet is reported as a result about misbehaviour retention.
        """
        require_api(self, "TG-04.3", "alternation result states the same or different retention pin and the prior bad phase count pin", ["decay_slices", "alternation_result", "aggregate_reputation"])
        surface = _surface_module
        stated = surface.alternation_result(
            decay_slice=69, same_or_different_retention="different rates",
            prior_bad_phase_count=2)
        self.assertEqual(stated["retention_pin"], "different rates")
        self.assertEqual(stated["prior_bad_phase_count_pin"], 2)
        self.assertEqual(stated["classification"], "result about misbehaviour retention")
        unstated = surface.alternation_result(decay_slice=69)
        self.assertIsNone(unstated["retention_pin"])
        self.assertIsNone(unstated["prior_bad_phase_count_pin"])
        self.assertEqual(unstated["classification"], "band result under alternation")


if __name__ == "__main__":
    unittest.main()

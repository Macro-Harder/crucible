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


class TestTG046(unittest.TestCase):
    def test_one_band_boundary_neighbourhood(self):
        """
        Fixture: F-28, band boundary neighbourhood case, created by the fixture assignment act at design steps step-13-tg046-fixture-assignment section 2. Standing label: the stated distances, and with them the size of the boundary neighbourhood, stand open, to be fixed in the family record before runs. This test pins the label and the bar, and no distance and no neighbourhood size.
        Pins: A population of identities whose reputation scores, as produced by the single aggregation rule the plan fixes, stand placed at stated distances above and below one band boundary; the run record reports the count of identities in each distance slice, the count of identities that cross the boundary during the run, and the cheapest score movement, in accepted work units, that crosses the boundary from below. Test one runs fixture F-28 in per viewer form beside its society level form, per Amendment TG4-02, with the near edge split field reading the fixture in that form.
        Bar: A family that reports a band transition result without the boundary neighbourhood counts has not run the test, and no headline claim about a band boundary rests on a run that omits them.
        Failure: Fails while crucible.mod05 stands absent, and fails if a band transition result is reported without the boundary neighbourhood counts in either form.
        """
        require_api(self, "TG-04.6", "band transition result carries the boundary neighbourhood counts on fixture F-28", ["band_transition", "boundary_neighbourhood", "band_membership"])
        surface = _surface_module
        scores = [
            {"score": 90, "distance_slice": "below within 10", "crossed": False},
            {"score": 95, "distance_slice": "below within 10", "crossed": True},
            {"score": 110, "distance_slice": "above within 10", "crossed": False},
        ]
        labels = ["below within 10", "above within 10"]
        for form in ("society level", "per viewer"):
            result = surface.band_transition(scores, 100, labels, form=form)
            self.assertTrue(surface.validate_band_transition_result(result))
            self.assertEqual(result["form"], form)
            self.assertEqual(result["counts_per_distance_slice"]["below within 10"], 2)
            self.assertEqual(result["counts_per_distance_slice"]["above within 10"], 1)
            self.assertEqual(result["crossing_count"], 1)
            self.assertEqual(
                result["cheapest_crossing_movement_in_accepted_work_units"], 5)
        bare = {"counts_per_distance_slice": {"below within 10": 2}}
        self.assertFalse(surface.validate_band_transition_result(bare))

    def test_two_alternation_against_decay(self):
        """
        Fixture: F-29, alternation against decay case, created by the fixture assignment act at design steps step-13-tg046-fixture-assignment section 3, on F-14, decay slice set, for the decay slices, and on F-15, Candidate 1 split decay case, as negative companion only. Standing label: the alternation period stands open, to be stated in the family record before runs. This test pins the label and the bar, and no period, ring size, or phase length.
        Pins: One identity, and separately a ring of identities under role rotation, alternating accepted good work and penalised bad behaviour; for each decay slice of fixture F-14, the highest band the alternating identity reaches, the number of bad phases completed before exclusion, and the same two figures for the ring under role rotation. An alternation result on an extension slice of F-14 carries its outside range extension label and its honest side readout, and no alternation result is reported as testing Candidate 1 as written, per fixture F-15 and AC-8.
        Bar: A decay result reported without the alternation figures for the slices it reports is reported as a decay result on a fixed record only, and not as a result about attacker behaviour under decay.
        Failure: Fails while crucible.mod05 stands absent, and fails if a decay result is reported as a result about attacker behaviour under decay without the alternation figures for its slices.
        """
        require_api(self, "TG-04.6", "alternation figures reported for each decay slice on fixtures F-14, F-15, and F-29", ["alternation_result", "decay_slices", "decay_result"])
        surface = _surface_module
        for entry in surface.decay_slices():
            result = surface.alternation_result(
                decay_slice=entry["half_life_days"],
                same_or_different_retention="same rate", prior_bad_phase_count=1,
                highest_band="high", bad_phases_before_exclusion=3,
                ring_highest_band="mid", ring_bad_phases_before_exclusion=2)
            self.assertIsNotNone(result["highest_band"])
            self.assertIsNotNone(result["bad_phases_before_exclusion"])
            self.assertIsNotNone(result["ring_highest_band"])
            self.assertIsNotNone(result["ring_bad_phases_before_exclusion"])
            self.assertFalse(result["tests_candidate_1_as_written"])
        extension = surface.decay_result(1)
        self.assertEqual(extension["extension_label"], "outside range extension")
        self.assertTrue(extension["honest_side_readout"])
        bare = surface.alternation_result(decay_slice=69)
        self.assertEqual(bare["classification"], "band result under alternation")

    def test_three_one_directional_vouch_feeding(self):
        """
        Fixture: F-30, one directional vouch feeding case, created by the fixture assignment act at design steps step-13-tg046-fixture-assignment section 4. The fixture carries no magnitude beyond its stated structure: one feeder, one direction, no return vouch.
        Pins: An identity with a clean work record vouches in one direction only toward a mutually vouching component and receives no vouch in return; the run record states, as a run record fact, whether the feeder appears in the largest mutually vouching component figure, in the component list, or in neither, read under the TG-04.2 ground that the component cap counts edges and each VouchEdge carries its component identifier under the component definition version in force.
        Bar: No structural trace claim describes the mutually vouching component as the whole collusion surface while this test stands unrun, per AC-3.
        Failure: Fails while crucible.mod05 stands absent, and fails if the run record states none of the three feeder positions or a trace claim describes the component as the whole collusion surface while the test stands unrun.
        """
        require_api(self, "TG-04.6", "run record states the one directional feeder position on fixture F-30", ["vouch", "component", "graph_snapshot"])
        surface = _surface_module
        edges = [
            surface.vouch("feeder", "a", 5),
            surface.vouch("a", "b", 5),
            surface.vouch("b", "a", 5),
        ]
        self.assertEqual(surface.feeder_position("feeder", edges), "neither")
        self.assertEqual(
            surface.feeder_position("a", edges), "largest mutually vouching component")
        snapshot = surface.graph_snapshot(edges)
        member_lists = [entry["members"] for entry in snapshot["component_list"]]
        self.assertTrue(all("feeder" not in members for members in member_lists))


if __name__ == "__main__":
    unittest.main()

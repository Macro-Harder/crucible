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


class TestTG044(unittest.TestCase):
    def test_compute_and_log_split(self):
        """
        Fixture: F-23, cold society degree case, the unknown share limb.
        Pins: The Parley Core computes the share per epoch and the Recorder logs the share it receives and computes none of it, with epoch close as the point of performance, per brief section 5.10 and operation C-17.
        Bar: A share not computed and delivered for an epoch is logged as the explicit value unknown; a run carrying zero in that position fails this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if the Recorder computes a share or an undelivered share is logged as zero.
        """
        require_api(self, "TG-04.4", "Core computes the gate passing share per epoch and the Recorder logs it and computes none", ["gate_passing_share", "compute_share", "share_for_epoch"])
        surface = _surface_module
        share = surface.gate_passing_share(["a", "b", "c", "d"], ["a", "b"], epoch=3)
        self.assertEqual(share["numerator"], 2)
        self.assertEqual(share["denominator"], 4)
        self.assertEqual(share["epoch"], 3)
        self.assertEqual(share["computed_by"], "MOD-05 Parley Core")
        self.assertEqual(surface.share_for_epoch(4), "unknown")
        self.assertEqual(surface.undelivered_share(), "unknown")
        self.assertTrue(surface.validate_logged_share("unknown"))
        self.assertFalse(surface.validate_logged_share(0))

    def test_double_application_derivation(self):
        """
        Fixture: A logged share with a known envelope value. Basis stated in the test text, no inventory fixture.
        Pins: The per eligible identity score bearing figure is the envelope value multiplied by the share, and a population average is that figure multiplied by the share again, epoch by epoch where the share varies, and never by the share alone.
        Bar: A published population figure derived by a single application fails this group; this is the derivation trap brief section 5.10 names.
        Failure: Fails while crucible.mod05 stands absent, and fails if a population figure is derived by a single application of the share.
        """
        require_api(self, "TG-04.4", "population figures use the double application of the gate passing share", ["gate_passing_share", "population_figure", "compute_share"])
        surface = _surface_module
        shares = [
            {"numerator": 1, "denominator": 2},
            {"numerator": 1, "denominator": 4},
        ]
        self.assertEqual(surface.score_bearing_figure(100, shares[0]), 50.0)
        result = surface.population_figure(100, shares, record_state="as originally written")
        self.assertEqual(result["per_epoch_corrected"], [25.0, 6.25])
        self.assertEqual(result["population_average"], 15.625)
        self.assertEqual(result["derivation"], "double application, mean as the final step")
        self.assertNotEqual(result["population_average"], 37.5)
        with self.assertRaises(ValueError):
            surface.population_figure(100, shares)

    def test_cost_statement_invalidity_on_missing_log(self):
        """
        Fixture: A run record missing the share log or the realised degree distribution log. Basis stated in the test text, no inventory fixture.
        Pins: The run is invalid for any cost statement, per AC-5, and no cost statement assumes the share.
        Bar: The share itself stands unfitted in every assumption set; a fitted share value in a fixture fails this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if a cost statement stands on a run missing either log or a fixture carries a fitted share value.
        """
        require_api(self, "TG-04.4", "run missing the share log or the degree distribution log is invalid for any cost statement", ["gate_passing_share", "cost_statement", "compute_share"])
        surface = _surface_module
        share = surface.gate_passing_share(["a"], ["a"], epoch=1)
        complete = {"share_log": [share], "degree_distribution_log": {"a": 1}}
        self.assertTrue(surface.cost_statement_valid(complete))
        self.assertEqual(surface.cost_statement(complete), {"valid": True})
        missing_share = {"degree_distribution_log": {"a": 1}}
        self.assertFalse(surface.cost_statement_valid(missing_share))
        missing_degree = {"share_log": [share]}
        self.assertFalse(surface.cost_statement_valid(missing_degree))
        fitted = dict(complete)
        fitted["assumption_share"] = {"fitted": True}
        self.assertFalse(surface.cost_statement_valid(fitted))

    def test_gate_passing_share_recomputation_check(self):
        """
        Fixture: F-23, cold society degree case, at its gate passing share limb, with the recomputation sample drawn from the epochs of one family on the basis the slice states. Gated in part: the sample size, fraction, and selection rule, and the divergence resolver and record form, stand open at cluster R1-035 in the Manager settlement register, design steps step-13-settlement-register entry 21.
        Pins: The recomputation stands held in a separate store position from the logged share, its only output is a divergence count, ownership of the share is unchanged, and no second owner of the share is created, per picked proposal CR8B-06 as slice S-04 lands it. The sample size, fraction, and selection rule limb pins no value, because that limb rests on the open settlement at R1-035 and stands gated on it.
        Bar: A missing recomputation for a sampled epoch fails this group; a divergence count above zero is a disagreement on the record, and the affected family result does not stand as reported until the divergence is resolved on its record; and a report that reads the affected share, or any result resting on that share for the affected family, as standing as reported while a nonzero count stands unresolved fails this group.
        Failure: Gated: this test records a skip naming the R1-035 settlement while that settlement stands open, and never records a pass. Once the settlement stands, failure takes the bar forms stated in this docstring.
        """
        require_api(self, "TG-04.4", "gate passing share recomputation held apart with divergence count as its only output", ["recompute_share", "gate_passing_share", "compute_share"])
        # Standing basis: Manager ruling Entry 21 at design/steps/step-14-manager-rulings.md settles the R1-035 sample for this recomputation.
        surface = _surface_module
        boundary = list(range(200))
        self.assertEqual(surface.recomputation_sample(boundary), boundary)
        self.assertEqual(len(surface.recomputation_sample(boundary)), 200)
        below = list(range(199))
        self.assertEqual(surface.recomputation_sample(below), below)
        above_sample = surface.recomputation_sample(list(range(1000)))
        self.assertEqual(len(above_sample), 200)
        self.assertEqual(above_sample[:5], [0, 5, 10, 15, 20])
        self.assertEqual(above_sample, surface.recomputation_sample(list(range(1000))))
        larger_sample = surface.recomputation_sample(list(range(2500)))
        self.assertEqual(len(larger_sample), 250)
        self.assertEqual(larger_sample[:5], [0, 10, 20, 30, 40])
        logged = {1: surface.gate_passing_share(["a", "b", "c", "d"], ["a", "b"], epoch=1), 2: surface.gate_passing_share(["a", "b"], ["a"], epoch=2)}
        agreeing = surface.recompute_share(logged, dict(logged))
        self.assertEqual(agreeing["divergence_count"], 0)
        self.assertGreaterEqual(agreeing["divergence_count"], 0)
        self.assertEqual(agreeing["store_position"], "separate recomputation position")
        self.assertEqual(agreeing["owner_of_share"], "MOD-05 Parley Core")
        self.assertFalse(agreeing["second_owner_created"])
        self.assertTrue(surface.validate_report_reading(agreeing["divergence_count"]))
        differing = {1: logged[1], 2: surface.gate_passing_share(["a", "b"], ["a", "b"], epoch=2)}
        direct_count = sum(1 for epoch in logged if differing.get(epoch) != logged[epoch])
        diverged = surface.recompute_share(logged, differing)
        self.assertEqual(direct_count, 1)
        self.assertEqual(diverged["divergence_count"], direct_count)
        self.assertGreaterEqual(diverged["divergence_count"], 0)
        self.assertEqual(diverged["store_position"], "separate recomputation position")
        self.assertEqual(diverged["owner_of_share"], "MOD-05 Parley Core")
        self.assertFalse(diverged["second_owner_created"])
        self.assertEqual(logged[2]["numerator"], 1)
        self.assertFalse(surface.validate_report_reading(diverged["divergence_count"]))
        self.assertFalse(surface.validate_report_reading(diverged["divergence_count"], resolved=False))
        self.assertTrue(surface.validate_report_reading(diverged["divergence_count"], resolved=True))


if __name__ == "__main__":
    unittest.main()

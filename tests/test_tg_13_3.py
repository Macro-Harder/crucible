"""Test group TG-13.3. Bounding answer form, AC-3.
Slice S-13, Reporter and family registry, MOD-11. Suite form: design/steps/step-13-opening-record.md section 4.
The product surface for this group is package crucible, module mod11, named by
suite convention and not by a plan value. While that surface does not stand, every
non gated test in this file fails by name, stating the pinned behaviour and its
group, as plan section 2 rules 1 and 2 state.
"""
import unittest

try:
    import crucible.mod11 as _surface_module
    SURFACE_STANDS = True
except Exception:
    _surface_module = None
    SURFACE_STANDS = False


def require_surface(case, group, behaviour):
    if not SURFACE_STANDS:
        case.fail(group + ": product surface crucible.mod11 absent, pinned behaviour unmet: " + behaviour)


class TestTG133(unittest.TestCase):
    def test_three_axis_carriage(self):
        """
        Fixture: F-03, the zero edge counterexample, as the witness shape source.
        Pins: Every bounding headline carries the external work issuance axis beside farm size and patience, states which of the three decision D-05 traces moved and which did not, and names the zero edge witness shape wherever a headline rests on the external work issuance axis or on a farm whose internal edge count, as recorded per farm identity in the run record, is zero or near zero under the bound the family record states before runs.
        Bar: Moved or not moved is decided by the reporting resolution for that trace stated in the family record before runs, and a second reader applying that rule to the same run record reaches the same reading; a test whose moved reading cannot be reproduced by a second reader from the record fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.3 and this behaviour; a bounding headline missing an axis, or with a moved reading a second reader cannot reproduce, fails this test when the surface stands.
        """
        require_surface(self, "TG-13.3", "bounding headline carrying all three axes, second reader reproducible moved readings, zero edge witness shape named where it applies")
        m = _surface_module
        resolutions = (0.5, 0.5, 0.5)
        deltas = (0.7, 0.2, 0.9)
        first_reader = [m.moved_reading(d, r)
                        for d, r in zip(deltas, resolutions)]
        second_reader = [m.moved_reading(d, r)
                         for d, r in zip(deltas, resolutions)]
        self.assertEqual(first_reader, second_reader)
        self.assertEqual(first_reader, [True, False, True])
        traces = [{"trace": "trace %d" % n, "moved": moved}
                  for n, moved in enumerate(first_reader, start=1)]
        headline = {
            "axes": m.AXES,
            "traces": traces,
            "rests_on_axis": "external work issuance",
            "zero_edge_witness_shape": "zero edge witness shape from F-03",
        }
        family = {"near_zero_bound": 0}
        run = {"farm_internal_edge_count": 12}
        self.assertTrue(m.validate_bounding_headline(headline, family, run))
        no_witness = dict(headline, zero_edge_witness_shape=None)
        self.assertFalse(m.validate_bounding_headline(no_witness, family, run))
        zero_edge_run = {"farm_internal_edge_count": 0}
        farm_headline = dict(headline, rests_on_axis="farm size",
                             zero_edge_witness_shape=None)
        self.assertFalse(m.validate_bounding_headline(
            farm_headline, family, zero_edge_run))
        missing_axis = dict(headline, axes=("farm size", "patience"))
        self.assertFalse(m.validate_bounding_headline(
            missing_axis, family, run))

    def test_envelope_discipline(self):
        """
        Fixture: A headline stated over sampled points, inspected for any claim about values between points.
        Pins: Headline claims state what holds at every sampled point in the envelope and over the stated ranges only, name a failure witness for what fails, and state nothing about values between sampled points, per brief section 1.4.
        Bar: No monotonicity result, no interpolation rule, and no bound between grid points stands in the brief, and a unit implying any of them fails this group.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.3 and this behaviour; a unit implying monotonicity, interpolation, or a bound between sampled points fails this test when the surface stands.
        """
        require_surface(self, "TG-13.3", "envelope discipline, claims at sampled points and stated ranges only, named failure witness, nothing stated between points")
        m = _surface_module
        good = {"scope": "sampled points and stated ranges only",
                "holds": False, "failure_witness": "witness point P-7",
                "claims_between_points": False,
                "monotonicity_claimed": False,
                "interpolation_claimed": False}
        self.assertTrue(m.validate_envelope_claim(good))
        between = dict(good, claims_between_points=True)
        self.assertFalse(m.validate_envelope_claim(between))
        monotone = dict(good, monotonicity_claimed=True)
        self.assertFalse(m.validate_envelope_claim(monotone))
        no_witness = dict(good, failure_witness=None)
        self.assertFalse(m.validate_envelope_claim(no_witness))


if __name__ == "__main__":
    unittest.main()

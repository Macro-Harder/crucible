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


class TestTG035(unittest.TestCase):
    def test_cold_start_degree(self):
        """
        Fixture: F-23, cold society degree case.
        Pins: Score bearing vouch degree is 0 for at least the first 90 days in a cold society, as a derived statement in its source entry, and stays gated thereafter by the gate passing share.
        Bar: The mapping states the bar in the companion failure path test of this group.
        Failure: Fails while crucible.mod03 stands absent, and fails if score bearing vouch degree stands above 0 inside the first 90 days of a cold society.
        """
        require_api(self, "TG-03.5", "score bearing vouch degree is 0 for at least the first 90 days in a cold society", ["cold_society", "build_cold_society", "generate_society"])
        surface = _surface_module
        case = surface.cold_society(population=200)
        self.assertEqual(case["fixture"], "F-23")
        self.assertEqual(case["population"], 200)
        self.assertEqual(case["score_bearing_vouch_degree_first_90_days"], 0)
        self.assertEqual(
            case["after_day_90"], "gated by the gate passing share")
        for day in (0, 1, 30, 89, 90):
            self.assertEqual(surface.cold_society_degree(day), 0, day)
        later = surface.cold_society_degree(91)
        self.assertEqual(
            later,
            {"degree": None,
             "standing": "gated by the gate passing share",
             "provenance_label": "derived over estimated rates"})
        self.assertEqual(
            surface.cold_society_degree(
                91, envelope=10, gate_passing_share=0.5),
            5.0)
        self.assertEqual(
            surface.cold_society_degree(
                365, envelope=8, gate_passing_share=0.25),
            2.0)
        self.assertEqual(surface.build_cold_society(population=200), case)

    def test_cold_start_degree_provenance(self):
        """
        Fixture: F-23, cold society degree case, with its provenance label as the mapping states it, derived over estimated rates.
        Pins: The cold start degree figure is carried as derived over estimated rates, with its provenance label attached.
        Bar: A test presenting the figure as measured fails the provenance limb at TG-01.1 form, fixture label discipline, plan section 2, section 3.
        Failure: Fails while crucible.mod03 stands absent, and fails if the figure is presented as measured or its provenance label stands dropped.
        """
        require_api(self, "TG-03.5", "cold start degree figure carried as derived over estimated rates", ["cold_society", "build_cold_society", "generate_society"])
        surface = _surface_module
        case = surface.cold_society(population=200)
        self.assertEqual(case["provenance_label"], "derived over estimated rates")
        self.assertEqual(
            surface.cold_degree_provenance(), "derived over estimated rates")
        self.assertEqual(
            surface.COLD_SOCIETY_PROVENANCE, "derived over estimated rates")
        self.assertEqual(
            surface.build_cold_society(population=200)["provenance_label"],
            "derived over estimated rates")
        later = surface.cold_society_degree(91)
        self.assertEqual(
            later["provenance_label"], "derived over estimated rates")
        self.assertNotEqual(case["provenance_label"], "measured")
        self.assertIn("derived", case["provenance_label"])
        self.assertIn("estimated", case["provenance_label"])
        self.assertNotIn("measured", case["provenance_label"])


if __name__ == "__main__":
    unittest.main()

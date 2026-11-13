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


class TestTG034(unittest.TestCase):
    def test_anchor_scenario_form(self):
        """
        Fixture: F-04, anchor scenario AN-1.
        Pins: An AnchorScenarioRecord carries exactly three values (scenario identifier, anchor set description as a scenario setting, and the mark in the ruled form, DQ-163 RULED by Captain JP, defer until Parley exists, with no provisional anchor set), and no fourth value, no default marker, and no favoured marker, per Shape 16.
        Bar: Anchor material appears only as D-09 scenarios, each carrying the mark in the ruled form stated in this test, per AC-6.
        Failure: Fails while crucible.mod03 stands absent, and fails if an AnchorScenarioRecord carries a fourth value, a default marker, or a favoured marker.
        """
        require_api(self, "TG-03.4", "AnchorScenarioRecord carries exactly three values in the ruled mark form", ["anchor_scenario", "build_anchor_scenario"])
        surface = _surface_module
        ruled_mark = ("DQ-163 RULED by Captain JP, defer until Parley exists, "
                      "with no provisional anchor set")
        self.assertEqual(surface.DQ163_MARK, ruled_mark)
        record = surface.anchor_scenario(
            "AN-1", "anchor set as a scenario setting")
        self.assertEqual(
            record,
            {"scenario_identifier": "AN-1",
             "anchor_set_description": "anchor set as a scenario setting",
             "mark": ruled_mark})
        self.assertEqual(len(record), 3)
        self.assertEqual(
            set(record),
            {"scenario_identifier", "anchor_set_description", "mark"})
        self.assertTrue(surface.validate_anchor_scenario(record))
        self.assertEqual(
            surface.build_anchor_scenario(
                "AN-1", "anchor set as a scenario setting"),
            record)
        fourth = dict(record)
        fourth["fourth value"] = "extra"
        self.assertFalse(surface.validate_anchor_scenario(fourth))
        defaulted = dict(record)
        defaulted["mark"] = "default marker"
        self.assertFalse(surface.validate_anchor_scenario(defaulted))
        favoured = dict(record)
        favoured["mark"] = "favoured marker"
        self.assertFalse(surface.validate_anchor_scenario(favoured))

    def test_empty_anchor_set_case(self):
        """
        Fixture: F-05, empty anchor set case.
        Pins: The suite includes the empty anchor set case as a coverage duty, sitting as the control beside concentrated and dispersed placement at fixed count and fixed total share.
        Bar: The case sets no estate default anchor set; its discharge stands in the suite record, checked by a reader who did not write the suite before any report of done, in the form the fixture itself states.
        Failure: Fails while crucible.mod03 stands absent, and fails if the empty anchor set case stands missing from the suite or is read as setting an estate default.
        """
        require_api(self, "TG-03.4", "empty anchor set case stands in the suite as the control case", ["anchor_scenario", "build_anchor_scenario"])
        surface = _surface_module
        case = surface.empty_anchor_set_case()
        self.assertEqual(
            case,
            {"case": "empty anchor set",
             "anchor_set": [],
             "standing": ("control beside concentrated and dispersed "
                          "placement at fixed count and fixed total share"),
             "sets_estate_default_anchor_set": False})
        self.assertEqual(case["anchor_set"], [])
        self.assertFalse(case["sets_estate_default_anchor_set"])
        self.assertEqual(
            case["standing"],
            "control beside concentrated and dispersed placement "
            "at fixed count and fixed total share")


if __name__ == "__main__":
    unittest.main()

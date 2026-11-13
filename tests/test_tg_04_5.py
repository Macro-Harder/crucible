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


class TestTG045(unittest.TestCase):
    def test_outcome_is_function_of_labelled_parameter(self):
        """
        Fixture: F-16, arbiter accuracy point sets, one case record set scored at two accuracy points, with set ranges imported with provenance labels where the mapping requires them.
        Pins: The outcome (slashable, not slashable, or a named no determination disposition) travels with the arbiter accuracy value applied, its assumption set and row reference, and the error direction named beside the value, per Shape 10 and operation C-21.
        Bar: The accuracy value may not be derived from panel size, band gates, or fee size, and the four set ranges beside the points stand unmerged; a test merging them into one range fails this group.
        Failure: Fails while crucible.mod05 stands absent, and fails if an outcome travels without its accuracy value, set and row, or error direction, or the four set ranges stand merged.
        """
        require_api(self, "TG-04.5", "adjudication outcome travels with its accuracy value, assumption set and row, and error direction", ["adjudicate", "adjudication_outcome", "challenge_outcome"])
        surface = _surface_module
        case = {
            "case_identifier": "case-1",
            "challenge_basis": "behavioural",
            "ground_truth_label_reference": "label-1",
        }
        result = surface.adjudicate(
            case, accuracy_value=0.8, assumption_set="set-a", row="accuracy row",
            error_direction="symmetric", outcome="slashable")
        self.assertEqual(result["outcome"], "slashable")
        self.assertEqual(result["arbiter_accuracy_value"], 0.8)
        self.assertEqual(result["assumption_set_identifier"], "set-a")
        self.assertEqual(result["row_identifier"], "accuracy row")
        self.assertEqual(result["error_direction"], "symmetric")
        with self.assertRaises(ValueError):
            surface.adjudicate(case, accuracy_value=0.8, assumption_set="set-a", row="accuracy row")
        with self.assertRaises(ValueError):
            surface.adjudicate(
                case, accuracy_value=0.8, assumption_set="set-a", row="accuracy row",
                error_direction="symmetric", derived_from="panel size")
        self.assertTrue(surface.accuracy_ranges_stand_unmerged(
            ["range one", "range two", "range three", "range four"]))
        self.assertFalse(surface.accuracy_ranges_stand_unmerged(["one merged range"]))

    def test_excluded_class_carriage(self):
        """
        Fixture: A run record carrying the excluded adjudication class counts and shares for the four excluded classes. Basis stated in the test text, no inventory fixture.
        Pins: The counts stand in every run record, and a family record that fixes no excluded share threshold supports no headline adjudication claim, per brief section 5.3 Shape 10 passage.
        Bar: Where the adjacent arbitrated share for a forged vouch basis is above zero in a run a headline claim rests on, the claim fails validation while register question NQ-56 stands open.
        Failure: Fails while crucible.mod05 stands absent, and fails if a run record omits the excluded class counts or a headline adjudication claim rests on a family record with no excluded share threshold fixed.
        """
        require_api(self, "TG-04.5", "excluded adjudication class counts stand in every run record", ["adjudicate", "adjudication_outcome", "run_record"])
        surface = _surface_module
        cases = [
            {"excluded_class": surface.EXCLUDED_CLASSES[0]},
            {"excluded_class": surface.EXCLUDED_CLASSES[3]},
            {"excluded_class": None},
        ]
        counts = surface.excluded_class_counts(cases)
        self.assertEqual(set(counts), set(surface.EXCLUDED_CLASSES))
        self.assertEqual(counts[surface.EXCLUDED_CLASSES[0]]["count"], 1)
        self.assertEqual(counts[surface.EXCLUDED_CLASSES[3]]["count"], 1)
        run_record = {"excluded_class_counts_and_shares": counts}
        self.assertFalse(surface.validate_headline_adjudication_claim({}, run_record))
        family = {"excluded_share_threshold": 0.5}
        self.assertFalse(surface.validate_headline_adjudication_claim(family, run_record))
        clean_counts = surface.excluded_class_counts([{"excluded_class": None}])
        clean_run = {"excluded_class_counts_and_shares": clean_counts}
        self.assertTrue(surface.validate_headline_adjudication_claim(family, clean_run))

    def test_ground_truth_separation(self):
        """
        Fixture: An adjudication case whose panel inputs are inspected for the ground truth label reference. Basis stated in the test text, no inventory fixture.
        Pins: The ground truth label reference is held apart from the panel inputs, per Shape 10.
        Bar: A panel input set containing the label, or a field derived from it, fails this group in the same form as the canary failure at TG-09.3.
        Failure: Fails while crucible.mod05 stands absent, and fails if a panel input set contains the ground truth label or a field derived from it.
        """
        require_api(self, "TG-04.5", "ground truth label reference held apart from panel inputs", ["adjudicate", "panel_inputs", "adjudication_outcome"])
        surface = _surface_module
        case = {
            "case_identifier": "case-1",
            "challenge_basis": "behavioural",
            "panel_form": "stated panel",
            "ground_truth_label_reference": "label-1",
        }
        inputs = surface.panel_inputs(case)
        self.assertNotIn("ground_truth_label_reference", inputs)
        self.assertTrue(surface.validate_panel_inputs(inputs))
        leaked = dict(inputs)
        leaked["ground_truth_label_reference"] = "label-1"
        self.assertFalse(surface.validate_panel_inputs(leaked))
        derived = dict(inputs)
        derived["derived_from_ground_truth"] = "x"
        self.assertFalse(surface.validate_panel_inputs(derived))
        result = surface.adjudicate(
            case, accuracy_value=0.8, assumption_set="set-a", row="accuracy row",
            error_direction="symmetric")
        self.assertEqual(result["ground_truth_label_reference"], "label-1")
        self.assertNotIn("ground_truth_label_reference", result["panel_inputs"])


if __name__ == "__main__":
    unittest.main()

"""Test group TG-13.2. Headline unit form, Shape 15, AC-4.
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


class TestTG132(unittest.TestCase):
    def test_closed_unit_fixed_field_order(self):
        """
        Fixture: F-01 read in reverse, as the negative template.
        Pins: A HeadlineResultUnit carries every field required, in the fixed order Shape 15 states, carries its assumption set, its rows, its range kind, and every dependence mark it was produced under as part of the unit itself, and is quotable whole or not at all.
        Bar: The field order of F-01 and its extra Range kind field are part of the failure that fixture illustrates; a unit copying either fails this group, and F-01 itself must never be quoted as a headline unit in any test expectation, snapshot, or golden file.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.2 and this behaviour; a unit missing a field, out of order, or copying the F-01 order or its extra Range kind field fails this test when the surface stands.
        """
        require_surface(self, "TG-13.2", "closed headline unit in the fixed Shape 15 field order, quotable whole or not at all")
        m = _surface_module
        values = {field: "value for " + field
                  for field in m.HEADLINE_UNIT_FIELDS}
        values["claim_sentence"] = (
            "At the sampled points within the stated scope, the "
            "result holds for the sampled points only, and nothing "
            "is claimed beyond the stated limits.")
        values["grounding_sentence"] = (
            "This unit rests on the retained run records within "
            "the stated scope, and its limits are that nothing is "
            "claimed beyond the sampled points in this unit.")
        values["qualifiers_and_markings_block"] = (
            "seam status: no cross seam effect; "
            "kill check: self checked only; "
            "dependence mark: DQ-164 confirmation form, recording "
            "that DQ-164 stands settled as confirmation only; "
            "Parley Q3 statement: no part of the result encodes "
            "Parley Q3 behaviour; "
            "core only qualifier: this unit is a core only result; "
            "anchor scenario statement: no anchor scenario is "
            "used in this unit.")
        unit = m.make_headline_unit(values)
        self.assertEqual(tuple(unit.keys()), m.HEADLINE_UNIT_FIELDS)
        self.assertEqual(len(unit), 14)
        self.assertTrue(m.validate_headline_unit(unit))
        self.assertEqual(m.quote_headline_unit(unit), unit)
        missing = dict(values)
        del missing[m.HEADLINE_UNIT_FIELDS[0]]
        with self.assertRaises(Exception):
            m.make_headline_unit(missing)
        extra = dict(unit)
        extra["range_kind"] = "extra Range kind field"
        self.assertFalse(m.validate_headline_unit(extra))
        with self.assertRaises(Exception):
            m.quote_headline_unit(extra)
        centre = dict(unit)
        centre["headline_unit_identifier_and_issue_date"] = "W-CENTRE-ONLY"
        self.assertFalse(m.validate_headline_unit(centre))

    def test_working_range_claim_form(self):
        """
        Fixture: A headline claim shown over a working range only.
        Pins: The claim names its assumption set, its rows, and its range kind in its first sentence, per the claim form rule at brief section 4.
        Bar: A first sentence naming none of the three, or only some of them, does not meet the claim form, and the unit is not published as a headline result at all.
        Failure: Fails while crucible.mod11 stands absent, naming TG-13.2 and this behaviour; a working range claim whose first sentence omits any of the three named items fails this test when the surface stands.
        """
        require_surface(self, "TG-13.2", "working range claim naming assumption set, rows, and range kind in its first sentence")
        m = _surface_module
        good = ("Over assumption set A-1, rows R-1 to R-9, in the working "
                "range kind, the claim holds. Further sentences follow.")
        self.assertTrue(m.validate_working_range_claim(
            good, "assumption set A-1", "rows R-1 to R-9", "working range"))
        partial = "Over assumption set A-1 the claim holds. It rests on rows R-1 to R-9 in the working range kind."
        self.assertFalse(m.validate_working_range_claim(
            partial, "assumption set A-1", "rows R-1 to R-9", "working range"))
        none_named = "The claim holds at the sampled points."
        self.assertFalse(m.validate_working_range_claim(
            none_named, "assumption set A-1", "rows R-1 to R-9",
            "working range"))


if __name__ == "__main__":
    unittest.main()

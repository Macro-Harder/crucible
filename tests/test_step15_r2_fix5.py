# Step 15 Round 2 fix tests, cluster 5. MOD-11 dressed empty headline
# parts (R2-A7-07), MOD-03 generator output depth bound (R2-OBS-1),
# the MOD-04 wording act, and the TB-15 plan amendment act.
# Plain simulated values only.
import os
import unittest

import crucible.mod03 as mod03
import crucible.mod11 as mod11

PRODUCT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRUCIBLE_ROOT = os.path.dirname(PRODUCT_ROOT)

MOD04_RESTATED_HEAD = (
    "The tracer composition that retains and reads back one form only "
    "RunRecord stands at the integration surface of slice S-16, in "
    "mod16; this module holds no module level import of MOD-10, and "
    "it delegates to MOD-10 at body level in two places only, "
    "release_view calling the MOD-10 view leak check runner as the "
    "release gate and write_checkpoint retaining the checkpoint pair "
    "through the MOD-10 paired store."
)
MOD04_RESTATED_TRACER = (
    "This function imports MOD-16 only; the module delegates to "
    "MOD-10 at body level in release_view and in write_checkpoint, "
    "as the head statement states."
)
MOD04_OLD_HEAD_TAIL = "this module holds no dependency on MOD-10 in any form"
MOD04_OLD_TRACER = "This module imports no part of MOD-10 in any form"


def read_text(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as handle:
        return handle.read()


def string_unit():
    unit = {field: "value for " + field for field in mod11.HEADLINE_UNIT_FIELDS}
    unit["claim_sentence"] = (
        "At the sampled points within the stated scope, the result "
        "holds for the sampled points only, and nothing is claimed "
        "beyond the stated limits.")
    unit["grounding_sentence"] = (
        "This unit rests on the retained run records within the "
        "stated scope, and its limits are that nothing is claimed "
        "beyond the sampled points in this unit.")
    unit["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recording that "
        "DQ-164 stands settled as confirmation only; "
        "Parley Q3 statement: no part of the result encodes Parley "
        "Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is used in "
        "this unit.")
    return unit


def lawful_unit():
    unit = string_unit()
    region = {"sampled_points": [
        {"axis_values": {"farm size": 200}, "outcome": "holds"}]}
    unit["holding_region"] = region
    unit["failure_region"] = {"sampled_points": [
        {"axis_values": {"farm size": 800}, "outcome": "fails"}]}
    return unit


def deep_value(depth):
    value = {"leaf": 1}
    for _ in range(depth):
        value = {"k": value}
    return value


class TestR2A707DressedEmptyParts(unittest.TestCase):
    def test_lawful_units_still_validate_and_quote(self):
        for unit in (string_unit(), lawful_unit()):
            self.assertTrue(mod11.validate_headline_unit(unit))
            self.assertEqual(mod11.quote_headline_unit(unit), unit)

    def test_empty_list_dress_fails_and_refuses_quotation(self):
        for field in ("holding_region", "failure_region",
                      "assumption_record", "witness_block",
                      "claim_sentence"):
            unit = lawful_unit()
            unit[field] = []
            self.assertFalse(mod11.validate_headline_unit(unit), field)
            with self.assertRaises(Exception, msg=field):
                mod11.quote_headline_unit(unit)

    def test_empty_container_dress_variants_fail(self):
        for value in ((), set(), frozenset()):
            unit = lawful_unit()
            unit["holding_region"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))

    def test_zero_and_false_dress_fail_and_refuse_quotation(self):
        for value in (0, 0.0, False):
            unit = lawful_unit()
            unit["holding_region"] = value
            self.assertFalse(
                mod11.validate_headline_unit(unit), repr(value))
            with self.assertRaises(Exception, msg=repr(value)):
                mod11.quote_headline_unit(unit)

    def test_container_carrying_only_empty_content_fails(self):
        unit = lawful_unit()
        unit["holding_region"] = [[]]
        self.assertFalse(mod11.validate_headline_unit(unit))
        unit = lawful_unit()
        unit["claim_sentence"] = [""]
        self.assertFalse(mod11.validate_headline_unit(unit))
        unit = lawful_unit()
        unit["witness_block"] = [0]
        self.assertFalse(mod11.validate_headline_unit(unit))

    def test_container_carrying_content_still_stands(self):
        unit = lawful_unit()
        unit["assumption_record"] = ["stated assumption record"]
        self.assertTrue(mod11.validate_headline_unit(unit))

    def test_envelope_claim_reads_dressed_empty_unit(self):
        unit = lawful_unit()
        unit["witness_block"] = []
        self.assertFalse(mod11.validate_envelope_claim(unit))


class TestR2OBS1GeneratorOutputDepth(unittest.TestCase):
    def test_deep_output_raises_named_failure_not_recursion(self):
        for depth in (2000, 5000):
            with self.assertRaises(
                    mod03.NamedGeneratorFailure, msg=str(depth)):
                mod03.validate_generator_output([deep_value(depth)])
            with self.assertRaises(
                    mod03.NamedGeneratorFailure, msg=str(depth)):
                mod03.validate_generator_output(deep_value(depth))

    def test_named_failure_names_the_bound(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.validate_generator_output([deep_value(5000)])
        self.assertIn("bound", str(caught.exception))
        self.assertIn(str(mod03.TRAVERSAL_DEPTH_BOUND),
                      str(caught.exception))

    def test_cyclic_output_raises_named_failure(self):
        cyclic = {"k": None}
        cyclic["k"] = cyclic
        with self.assertRaises(mod03.NamedGeneratorFailure):
            mod03.validate_generator_output([cyclic])

    def test_within_bound_depth_still_read(self):
        self.assertTrue(mod03.validate_generator_output(
            [deep_value(50)]))
        poisoned = {"reputation": 5}
        for _ in range(50):
            poisoned = {"k": poisoned}
        self.assertFalse(mod03.validate_generator_output([poisoned]))

    def test_ta66_controls_stand(self):
        self.assertFalse(mod03.validate_generator_output(
            [{"effect": {"reputation": 5}}]))
        self.assertFalse(mod03.validate_generator_output(
            [{"reputation": 5}]))
        proposals = [{
            "agent_id": "agent-0000", "archetype_id": "honest",
            "action": "vouch", "draw": 0.5,
            "assumptions": {"labelled": "case"}}]
        self.assertTrue(mod03.validate_generator_output(proposals))


def normalised(text):
    return " ".join(text.split())


def module_docstring_head(*parts):
    raw = read_text(*parts)
    parts_split = raw.split('\"\"\"', 2)
    if len(parts_split) < 3:
        return ""
    return normalised(parts_split[1])


class TestMod04WordingAct(unittest.TestCase):
    def test_head_statement_restated_verbatim(self):
        docstring_head = module_docstring_head(
            PRODUCT_ROOT, "crucible", "mod04.py")
        self.assertIn(MOD04_RESTATED_HEAD, docstring_head)
        self.assertNotIn(MOD04_OLD_HEAD_TAIL, docstring_head)

    def test_run_tracer_cut_docstring_restated_verbatim(self):
        text = normalised(read_text(PRODUCT_ROOT, "crucible", "mod04.py"))
        self.assertIn(MOD04_RESTATED_TRACER, text)
        self.assertNotIn(MOD04_OLD_TRACER, text)


@unittest.skipUnless(
    os.path.exists(os.path.join(CRUCIBLE_ROOT, "design", "DESIGN-PLAN.md")),
    "the design tree stands absent in a product only tree")
class TestTB15PlanAmendment(unittest.TestCase):
    def test_tg135_body_entry_stands_in_ruled_form(self):
        text = read_text(CRUCIBLE_ROOT, "design", "DESIGN-PLAN.md")
        self.assertIn("weekly cap ruled form", text)
        self.assertIn("Manager ruling Entry 20", text)
        self.assertIn("the Reporter holds the 26th unit", text)
        self.assertIn("held units stand reported as held", text)
        self.assertIn(
            "released into the next weekly container in arrival order",
            text)
        self.assertNotIn("weekly cap open element", text)
        self.assertNotIn(
            "no behaviour at the cap stands stated in this plan", text)
        self.assertIn("- Test: one lookup or named failure.", text)
        self.assertEqual(text.count("\u2014"), 0)
        self.assertEqual(text.count("\u2013"), 0)


if __name__ == "__main__":
    unittest.main()

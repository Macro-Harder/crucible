"""Step 15, second run, fix wave 8 pins for Builder 8.

Each defect test pins one charged defect instance from the
Round 8 register on the MOD-14 text loci in crucible/mod14.py:
the MOD-14 limb of R8-007 at _canonicalise_text, the MOD-14
limb of R8-010 at _stored_text, the MOD-14 limb of R8-023 at
_stated_text and _has_stated_condition, and R8-026 at the
module head and the operator_runbook docstring. Control tests
stand both ways beside each family. Values are simulated and
test values only.
"""
import inspect
import unittest

import crucible.mod14 as mod14


class LieStr(str):
    """A string subclass storing one text and reporting another
    through its own string reading."""

    def __new__(cls, stored, reported):
        obj = super().__new__(cls, stored)
        obj._reported = reported
        return obj

    def __str__(self):
        return self._reported


class NamedKey:
    """A non text key carrying a name in an attribute and
    reporting a second name through its own string reading."""

    def __init__(self, carried, reported):
        self.carried = carried
        self._reported = reported

    def __str__(self):
        return self._reported

    __hash__ = object.__hash__


class TestR8007CanonicaliseText(unittest.TestCase):
    def test_actor_storing_person_reporting_clean_reads_as_person(self):
        self.assertEqual(
            mod14._normalise_actor(LieStr("person", "zzzzzz")),
            "person")

    def test_actor_storing_edge_dress_reporting_clean_reads_as_person(self):
        self.assertEqual(
            mod14._normalise_actor(LieStr("nqzjop", "zzzzzz")),
            "person")

    def test_actor_storing_clean_reporting_person_reads_as_stored(self):
        self.assertEqual(
            mod14._normalise_actor(LieStr("zzzzzz", "person")),
            "zzzzzz")

    def test_target_storing_checkpoint_set_reporting_clean_barred(self):
        action = {
            "kind": "edit",
            "target": LieStr("checkpoint set", "other set"),
        }
        self.assertFalse(mod14.validate_operator_action(action))

    def test_canonicalise_text_takes_stored_characters(self):
        self.assertEqual(
            mod14._canonicalise_text(LieStr("person", "zzzzzz")),
            "person")


class TestR8007Controls(unittest.TestCase):
    def test_plain_person_actor_reads_as_person(self):
        self.assertEqual(mod14._normalise_actor("person"), "person")

    def test_plain_clean_actor_reads_as_itself(self):
        self.assertEqual(mod14._normalise_actor("zzzzzz"), "zzzzzz")

    def test_plain_checkpoint_target_barred_on_edit(self):
        action = {"kind": "edit", "target": "checkpoint set"}
        self.assertFalse(mod14.validate_operator_action(action))

    def test_plain_other_target_allowed_on_edit(self):
        action = {"kind": "edit", "target": "other set"}
        self.assertTrue(mod14.validate_operator_action(action))

    def test_canonicalise_text_plain_and_empty(self):
        self.assertEqual(mod14._canonicalise_text("Person"), "person")
        self.assertEqual(mod14._canonicalise_text(""), "")
        self.assertEqual(mod14._canonicalise_text(None), "")


class TestR8010StoredTextFallback(unittest.TestCase):
    def test_stored_text_of_non_text_key_judges_no_name(self):
        self.assertEqual(
            mod14._stored_text(NamedKey("figure", "money")), "")

    def test_pilot_form_of_non_text_key_reporting_money_is_no_name(self):
        self.assertEqual(
            mod14._pilot_key_form(NamedKey("figure", "money")), "")

    def test_pilot_form_of_non_text_key_reporting_figure_is_no_name(self):
        self.assertEqual(
            mod14._pilot_key_form(NamedKey("money", "figure")), "")

    def test_pilot_run_delivers_non_text_key_reporting_money(self):
        key = NamedKey("figure", "money")
        result = mod14.pilot_run("timing", {key: 5})
        self.assertEqual(result["confinement_label"], "pilot confined")
        self.assertEqual(result["use"], "timing")


class TestR8010Controls(unittest.TestCase):
    def test_stored_text_of_plain_text_key(self):
        self.assertEqual(mod14._stored_text("money"), "money")

    def test_text_key_storing_money_reporting_figure_still_barred(self):
        self.assertEqual(
            mod14._pilot_key_form(LieStr("money", "figure")), "money")
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {LieStr("money", "figure"): 5})

    def test_text_key_storing_figure_reporting_money_not_barred(self):
        self.assertEqual(
            mod14._pilot_key_form(LieStr("figure", "money")), "figure")
        result = mod14.pilot_run(
            "timing", {LieStr("figure", "money"): 5})
        self.assertEqual(result["use"], "timing")

    def test_plain_money_key_barred_at_pilot_run(self):
        with self.assertRaises(mod14.NamedShellFailure):
            mod14.pilot_run("timing", {"money": 5})

    def test_plain_figure_key_delivered_at_pilot_run(self):
        result = mod14.pilot_run("timing", {"figure": 5})
        self.assertEqual(result["figure"], 5)


_BLANK_ONLY_CHARS = [
    ("\ud800", "lone high surrogate"),
    ("\udc00", "lone low surrogate"),
    ("\u0378", "unassigned code point U+0378"),
    ("\u0896", "unassigned code point U+0896"),
    ("\ue000", "private use U+E000"),
    ("\uf8ff", "private use U+F8FF"),
    ("\U0010fffd", "private use U+10FFFD"),
]


class TestR8023BlankCondition(unittest.TestCase):
    pass


def _make_blank_test(char):
    def test(self):
        self.assertEqual(mod14._stated_text(char), "")
        self.assertFalse(mod14._has_stated_condition([char]))
    return test


for _index, (_char, _label) in enumerate(_BLANK_ONLY_CHARS):
    setattr(
        TestR8023BlankCondition,
        "test_blank_only_char_%d_states_no_condition" % _index,
        _make_blank_test(_char))


class TestR8023StatedTextMixed(unittest.TestCase):
    def test_stated_text_strips_private_use_beside_letter(self):
        self.assertEqual(mod14._stated_text("\ue000x"), "x")

    def test_stated_text_strips_surrogate_beside_letter(self):
        self.assertEqual(mod14._stated_text("\ud800x"), "x")


class TestR8023Controls(unittest.TestCase):
    def test_readable_entry_states_a_condition(self):
        self.assertTrue(mod14._has_stated_condition(["x"]))
        self.assertEqual(mod14._stated_text("x"), "x")

    def test_cured_blank_forms_still_state_no_condition(self):
        self.assertFalse(mod14._has_stated_condition(["\u0000"]))
        self.assertFalse(mod14._has_stated_condition(["\u20dd"]))
        self.assertFalse(mod14._has_stated_condition(["\u2800"]))
        self.assertFalse(mod14._has_stated_condition([""]))
        self.assertFalse(mod14._has_stated_condition([None]))
        self.assertFalse(mod14._has_stated_condition([]))

    def test_blank_char_beside_readable_char_still_states(self):
        self.assertTrue(mod14._has_stated_condition(["\ud800x"]))
        self.assertTrue(mod14._has_stated_condition(["\ue000x"]))

    def test_mixed_list_with_one_readable_entry_states(self):
        self.assertTrue(
            mod14._has_stated_condition(["\u0378", "stated"]))


class TestR8026RunbookStatements(unittest.TestCase):
    def test_module_head_names_runbook_locus_in_code(self):
        doc = mod14.__doc__ or ""
        self.assertNotIn("public README states", doc)
        self.assertIn("operator_runbook", doc)

    def test_runbook_docstring_names_runbook_locus_in_code(self):
        doc = mod14.operator_runbook.__doc__ or ""
        self.assertNotIn("public README states", doc)
        self.assertIn("operator_runbook", doc)

    def test_runbook_source_claims_no_readme_statement(self):
        source = inspect.getsource(mod14.operator_runbook)
        self.assertNotIn("README states", source)


class TestR8026Controls(unittest.TestCase):
    def test_operator_runbook_still_returns_seven_steps(self):
        book = mod14.operator_runbook()
        self.assertEqual(book["form"], "operator runbook")
        self.assertEqual(book["deliverable_of"], "slice S-15")
        self.assertEqual(len(book["steps"]), 7)
        self.assertTrue(book["shell_owns_no_rule"])


if __name__ == "__main__":
    unittest.main()

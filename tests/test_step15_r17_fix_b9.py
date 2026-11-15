"""Pins for fix wave 16, Builder 9, Group 9.

Rows R16-027, R16-075, R16-076, and R16-086. Each defect pin
fails on the pristine tree for the charged form and passes
after the cure. Controls pass on both standings.
"""

import unittest

from crucible import mod03, mod04, mod05, mod14


CATALOGUE_REFUSAL = (
    "catalogue rejected: the record set stands in no record "
    "list form, a record set stands as records, and no "
    "catalogue stands delivered")


class StrReprRaises:
    def __str__(self):
        raise RuntimeError("strboom")

    def __repr__(self):
        raise RuntimeError("reprboom")


class TestR16027CatalogueDelivery(unittest.TestCase):
    """R16-027: MOD-03 archetype_catalogue silently delivers an
    empty catalogue for a record set handed in number, mapping,
    generator, or raising form, where the text and bytes forms
    draw the full named refusal."""

    def test_number_form_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod03.catalogue(42)
        self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_mapping_form_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod03.catalogue({"a": {"archetype_id": "a1"}})
        self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_generator_form_refused(self):
        def records():
            yield {"archetype_id": "a1"}
        with self.assertRaises(ValueError) as caught:
            mod03.catalogue(records())
        self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_raising_form_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod03.catalogue(StrReprRaises())
        self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_wrappers_refuse_number_form(self):
        for act in (mod03.archetype_catalogue, mod03.catalogue_record):
            with self.assertRaises(ValueError) as caught:
                act(42)
            self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_reportable_over_unread_set_refused(self):
        with self.assertRaises(ValueError) as caught:
            mod03.run_headline_reportable([], records=42)
        self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_non_container_iterable_control_holds(self):
        class UnreadIterable:
            def __init__(self, yielded):
                self._yielded = yielded

            def __iter__(self):
                return iter(self._yielded)
        record = {"archetype_id": "a1"}
        result = mod03.catalogue(UnreadIterable([record]))
        self.assertEqual(result["entries"], {})

    def test_text_and_bytes_controls_refuse(self):
        for handed in ("abc", b"abc"):
            with self.assertRaises(ValueError) as caught:
                mod03.catalogue(handed)
            self.assertEqual(str(caught.exception), CATALOGUE_REFUSAL)

    def test_lawful_controls_deliver(self):
        record = {"archetype_id": "a1"}
        result = mod03.catalogue([record])
        self.assertEqual(set(result["entries"]), {"a1"})
        self.assertEqual(
            set(mod03.catalogue((record,))["entries"]), {"a1"})
        self.assertEqual(mod03.catalogue(None)["entries"], {})
        self.assertEqual(mod03.catalogue()["entries"], {})


class TestR16075FirstBarredFieldNaming(unittest.TestCase):
    """R16-075: MOD-04 _first_barred_field names the whole joined
    text of a split node carrying a further key, and returns no
    field for an exact form name split in such a node."""

    def test_split_with_trailing_key_names_barred_field(self):
        self.assertEqual(
            mod04._first_barred_field(
                {"ground_": 1, "truth": 1, "note": 1}),
            "ground_truth")

    def test_split_with_leading_key_names_barred_field(self):
        self.assertEqual(
            mod04._first_barred_field(
                {"note": 1, "ground_": 1, "truth": 1}),
            "ground_truth")

    def test_exact_split_with_further_key_names_field(self):
        self.assertEqual(
            mod04._first_barred_field({"lab": 1, "el": 1, "note": 1}),
            "label")

    def test_gate_sentence_names_barred_field(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04.build_view_record(
                contents=[{"ground_": 1, "truth": 1, "note": 1}])
        message = str(caught.exception)
        self.assertIn("barred field ground_truth,", message)
        self.assertNotIn("ground_truthnote", message)

    def test_split_alone_control_holds(self):
        self.assertEqual(
            mod04._first_barred_field({"ground_": 1, "truth": 1}),
            "ground_truth")
        self.assertEqual(
            mod04._first_barred_field({"lab": 1, "el": 1}), "label")

    def test_single_key_and_clean_controls_hold(self):
        self.assertEqual(
            mod04._first_barred_field({"ground_truth": 1}),
            "ground_truth")
        self.assertIsNone(mod04._first_barred_field({"clean": 1}))
        self.assertIsNone(
            mod04._first_barred_field({"note": 1, "clean": 1}))


class TestR16076PanelBarredKeysNaming(unittest.TestCase):
    """R16-076: MOD-05 _panel_barred_keys lists the whole joined
    text of a split node carrying a further key as the barred
    key, so the adjudicate refusal names a key not in the case."""

    def test_split_with_trailing_key_lists_barred_key(self):
        self.assertEqual(
            mod05._panel_barred_keys(
                {"ground_": 1, "truth": 1, "note": 1}),
            ["ground_truth"])

    def test_case_shaped_node_lists_barred_key(self):
        self.assertEqual(
            mod05._panel_barred_keys(
                {"case_identifier": 1, "ground_": 1, "truth": 1}),
            ["ground_truth"])

    def test_adjudicate_refusal_names_barred_key(self):
        case = {"case_identifier": "c1", "ground_": 1, "truth": 1}
        with self.assertRaises(ValueError) as caught:
            mod05.adjudicate(
                case, accuracy_value=0.5, assumption_set="a",
                row="r", error_direction="d")
        message = str(caught.exception)
        self.assertIn("key: ground_truth", message)
        self.assertNotIn("case_identifierground_truth", message)

    def test_split_alone_control_holds(self):
        self.assertEqual(
            mod05._panel_barred_keys({"ground_": 1, "truth": 1}),
            ["ground_truth"])

    def test_single_key_and_clean_controls_hold(self):
        self.assertEqual(
            mod05._panel_barred_keys({"ground_truth": 1}),
            ["ground_truth"])
        self.assertEqual(mod05._panel_barred_keys({"clean": 1}), [])


class BadFailureAttribute(Exception):
    @property
    def failure(self):
        raise RuntimeError("failureboom")


class BadGateAttribute(Exception):
    @property
    def gate(self):
        raise RuntimeError("gateboom")


class BadDictAttribute(Exception):
    @property
    def __dict__(self):
        raise RuntimeError("dictboom")


class EqThing:
    raise_eq = False

    def __init__(self, number):
        self.number = number

    def __hash__(self):
        return 42

    def __eq__(self, other):
        if EqThing.raise_eq:
            raise RuntimeError("eqboom")
        return self is other


def raising_eq_set():
    items = {EqThing(1), EqThing(2)}
    EqThing.raise_eq = True
    return items


class TestR16086ErrorCarriageCraftedHandings(unittest.TestCase):
    """R16-086: MOD-14 error_carriage escapes bare on a failure
    whose failure or gate attribute access raises, on a failure
    whose __dict__ property raises past its TypeError guard, and
    on a failure dict carrying a set whose equality reading
    raises inside the _freeze set limb."""

    def tearDown(self):
        EqThing.raise_eq = False

    def assert_full_carriage(self, carriage):
        self.assertTrue(carriage["operator_sees_failure"])
        self.assertFalse(carriage["swallowed"])
        self.assertFalse(carriage["converted_to_empty_result"])
        self.assertTrue(carriage["failure"])
        self.assertTrue(carriage["failure_value"])

    def test_failure_attribute_raising_carried(self):
        carriage = mod14.error_carriage(BadFailureAttribute("x"))
        self.assert_full_carriage(carriage)

    def test_gate_attribute_raising_carried(self):
        carriage = mod14.error_carriage(BadGateAttribute("x"))
        self.assert_full_carriage(carriage)

    def test_dict_attribute_raising_carried(self):
        carriage = mod14.error_carriage(BadDictAttribute("x"))
        self.assert_full_carriage(carriage)

    def test_freeze_set_in_failure_dict_carried(self):
        failure = ValueError("boom")
        failure.failure = {"payload": raising_eq_set()}
        carriage = mod14.error_carriage(failure)
        self.assert_full_carriage(carriage)

    def test_freeze_set_in_failure_vars_carried(self):
        failure = ValueError("boom")
        failure.extra = raising_eq_set()
        carriage = mod14.error_carriage(failure)
        self.assert_full_carriage(carriage)

    def test_plain_controls_hold(self):
        self.assert_full_carriage(mod14.error_carriage("hello"))
        self.assert_full_carriage(
            mod14.error_carriage(ValueError("plain boom")))
        named = mod14.error_carriage(
            mod14.NamedShellFailure("named boom"))
        self.assert_full_carriage(named)
        self.assertEqual(
            named["failure_value"]["message"], "named boom")


if __name__ == "__main__":
    unittest.main()

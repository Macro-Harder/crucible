"""Pins for Round 20 rows R20-003, R20-004, R20-006, R20-013,
R20-027, R20-031, R20-058, R20-059, R20-060, and R20-061.

MOD-09 family, Builder 1 of fix wave 20. Each distinguishing
pin hands the charged act the handing its row charges, beside
the plain controls the source papers ran. Row R20-027 charges
the bound statement alone, so its pins stand as the proving
acts of the corrected statement and pass before and after.


Union standing (fix wave 21 merge): the fix wave 21 pin file of this same name stands composed below in its own section, its classes and helpers standing beside the landed classes above, losing neither set. The wave file docstring stands here in full:

Pins for fix wave 21, Builder 1, Group 1.

Rows R21-001 and R21-002 of the Round 21 register: the copy
family candidate taken test, under settlement S-1, on ruling
(ba). The cured pole form is the R20-009 cured form: the
numbered candidate stands tested against the copied dict
before insertion.
"""


import unittest
from decimal import Decimal
from crucible import mod09
from crucible import mod01, mod03, mod04, mod05, mod06, mod07
from crucible import mod08, mod09, mod10, mod11, mod12, mod13
from crucible import mod14


def _carriage(strategies=("conditional briber",), position=6):
    return mod09.run_record_carriage(
        list(strategies), position, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(case_uses=None):
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": "no failure"}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        case_uses=case_uses,
        external_profit_swept_values=(0, 5))


class LieRepr:
    """A plain object standing in no charged form, whose repr
    reading names the text it is handed at construction."""

    def __init__(self, text):
        self._text = text

    def __repr__(self):
        return self._text


class LieReprFloat(float):
    """A float storing its value whose repr reading answers 5."""

    def __repr__(self):
        return "5"


class AlwaysEq:
    """A plain object whose equality answers True against
    every value."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = object.__hash__


class RaiseEq:
    """A plain object whose equality readings raise."""

    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    def __ne__(self, other):
        raise RuntimeError("inequality reading raises")

    __hash__ = object.__hash__


class EqFalseStr(str):
    """A text value storing its text whose equality answers
    False against every value."""

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    __hash__ = str.__hash__


class ArmedHash:
    """A part rendered as itself whose hash reading raises
    once the class flag stands up."""

    armed = False

    def __hash__(self):
        if ArmedHash.armed:
            raise RuntimeError("armed hash raises")
        return 42

    def __eq__(self, other):
        return self is other


class CollideKey(str):
    """A stored key whose hash collides with a stated field
    name and whose equality readings raise once the class flag
    stands up."""

    armed = False

    def __hash__(self):
        return str.__hash__("in_protocol_payoff")

    def __eq__(self, other):
        if CollideKey.armed:
            raise RuntimeError("armed equality raises")
        return str.__eq__(self, other)

    def __ne__(self, other):
        if CollideKey.armed:
            raise RuntimeError("armed inequality raises")
        result = str.__ne__(self, other)
        return result if result is not NotImplemented else True


class Holder:
    """An identifier carrying one stored payload attribute."""

    def __init__(self, payload):
        self.payload = payload


class TestR20003StoredTruthyComplex(unittest.TestCase):

    def test_zero_complex_judged_not_truthy(self):
        self.assertIs(mod09._stored_truthy(0j), False)

    def test_parameter_set_zero_complex_refused(self):
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = 0j
        self.assertIs(mod09.validate_search_record(record), False)

    def test_parameter_set_zero_complex_failure_named(self):
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = 0j
        failures = mod09.search_record_validation_failures(record)
        self.assertIn(
            "the bond parameter search carries no parameter set",
            failures)

    def test_mid_run_zero_complex_validates(self):
        record = _record()
        record["mid_run_strategies"] = 0j
        self.assertIs(mod09.validate_search_record(record), True)

    def test_make_strategy_zero_complex_delivers_empty(self):
        strategy = mod09.make_strategy(
            "conditional briber", parameters=0j)
        self.assertEqual(strategy["parameters"], {})

    def test_nonzero_complex_control(self):
        self.assertIs(mod09._stored_truthy(1j), True)
        self.assertIs(mod09._stored_truthy(2 + 3j), True)

    def test_plain_zero_controls(self):
        self.assertIs(mod09._stored_truthy(0), False)
        self.assertIs(mod09._stored_truthy(0.0), False)
        self.assertIs(mod09._stored_truthy(5), True)
        record = _record()
        record["bond_parameter_search"]["parameter_set"] = 0
        self.assertIs(mod09.validate_search_record(record), False)
        record = _record()
        record["mid_run_strategies"] = 0
        self.assertIs(mod09.validate_search_record(record), True)
        strategy = mod09.make_strategy(
            "conditional briber", parameters=0)
        self.assertEqual(strategy["parameters"], {})
        strategy = mod09.make_strategy(
            "conditional briber", parameters={"a": 1})
        self.assertEqual(strategy["parameters"], {"a": 1})

    def test_decimal_zero_bound_control(self):
        self.assertIs(mod09._stored_truthy(Decimal(0)), True)


class TestR20004BuildSearchRecordFixture(unittest.TestCase):

    def test_always_equal_fixture_not_rewritten(self):
        record = _record(case_uses=[{
            "fixture": AlwaysEq(), "use": "case use alpha"}])
        use = record["case_uses"][0]
        self.assertEqual(use["use"], "case use alpha")
        self.assertNotIn("standings_carried", use)

    def test_raising_equality_fixture_builds(self):
        record = _record(case_uses=[{
            "fixture": RaiseEq(), "use": "case use alpha"}])
        self.assertEqual(record["case_uses"][0]["use"],
                         "case use alpha")

    def test_stored_f26_in_lying_dress_rewritten(self):
        record = _record(case_uses=[{
            "fixture": EqFalseStr("F-26"), "use": "case use alpha"}])
        use = record["case_uses"][0]
        self.assertEqual(use["use"], "strategy search point only")
        self.assertIn("standings_carried", use)

    def test_plain_f26_control(self):
        record = _record(case_uses=[{
            "fixture": "F-26", "use": "case use alpha"}])
        use = record["case_uses"][0]
        self.assertEqual(use["use"], "strategy search point only")
        self.assertEqual(use["standings_asserted_as_settled"], False)

    def test_plain_other_fixture_control(self):
        record = _record(case_uses=[{
            "fixture": "F-99", "use": "case use alpha"}])
        use = record["case_uses"][0]
        self.assertEqual(use["use"], "case use alpha")
        self.assertNotIn("standings_carried", use)


class TestR20006RenderSafeCopyConstruction(unittest.TestCase):

    def tearDown(self):
        ArmedHash.armed = False

    def test_dict_armed_rendered_key_carried(self):
        part = ArmedHash()
        handing = {part: "x"}
        ArmedHash.armed = True
        copied = mod09._render_safe_copy(handing)
        self.assertIsInstance(copied, dict)
        self.assertEqual(list(copied.values()), ["x"])
        self.assertEqual(len(copied), 1)

    def test_set_armed_rendered_part_carried(self):
        part = ArmedHash()
        handing = {part}
        ArmedHash.armed = True
        copied = mod09._render_safe_copy(handing)
        self.assertEqual(list(copied), [part])

    def test_frozenset_armed_rendered_part_carried(self):
        part = ArmedHash()
        handing = frozenset({part})
        ArmedHash.armed = True
        copied = mod09._render_safe_copy(handing)
        self.assertEqual(list(copied), [part])

    def test_summary_armed_classification_carried(self):
        part = ArmedHash()
        run = {"run_identifier": "run one", "attacker_cost": 1,
               "harm": 2, "regime_classification": {part: "x"}}
        ArmedHash.armed = True
        summary = mod09.attacker_cost_summary(run)
        self.assertEqual(summary["witness_run"], "run one")
        carried = summary["classification_before"]
        self.assertEqual(list(carried.values()), ["x"])

    def test_plain_copies_control(self):
        self.assertEqual(mod09._render_safe_copy({"a": 1}), {"a": 1})
        self.assertEqual(mod09._render_safe_copy({1, 2}), {1, 2})
        self.assertEqual(
            mod09._render_safe_copy(frozenset({1, 2})),
            frozenset({1, 2}))
        self.assertEqual(mod09._render_safe_copy([1, "a"]), [1, "a"])

    def test_plain_summary_control(self):
        summary = mod09.attacker_cost_summary({
            "run_identifier": "run one", "attacker_cost": 1,
            "harm": 2, "regime_classification": "regime one"})
        self.assertEqual(summary["classification_before"],
                         "regime one")
        self.assertEqual(summary["absent_fields"], [])


class TestR20013BaseDictStoredPairs(unittest.TestCase):

    def tearDown(self):
        CollideKey.armed = False

    def test_get_colliding_raising_key_answers_default(self):
        key = CollideKey("other text")
        handing = {key: 999}
        CollideKey.armed = True
        self.assertIsNone(
            mod09._base_dict_get(handing, "in_protocol_payoff"))
        self.assertEqual(
            mod09._base_dict_get(handing, "in_protocol_payoff", 7), 7)

    def test_contains_colliding_raising_key_answers_false(self):
        key = CollideKey("other text")
        handing = {key: 999}
        CollideKey.armed = True
        self.assertIs(
            mod09._base_dict_contains(handing, "in_protocol_payoff"),
            False)

    def test_get_stored_text_key_despite_raising_equality(self):
        key = CollideKey("in_protocol_payoff")
        handing = {key: 999}
        CollideKey.armed = True
        self.assertEqual(
            mod09._base_dict_get(handing, "in_protocol_payoff"), 999)
        self.assertIs(
            mod09._base_dict_contains(handing, "in_protocol_payoff"),
            True)

    def test_consumer_named_refusal_not_bare_escape(self):
        key = CollideKey("other text")
        handing = {key: 999}
        CollideKey.armed = True
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.attacker_payoff(handing, 1)

    def test_plain_get_contains_controls(self):
        handing = {"in_protocol_payoff": 5, "other": 1}
        self.assertEqual(
            mod09._base_dict_get(handing, "in_protocol_payoff"), 5)
        self.assertIsNone(mod09._base_dict_get(handing, "absent"))
        self.assertIs(
            mod09._base_dict_contains(handing, "in_protocol_payoff"),
            True)
        self.assertIs(mod09._base_dict_contains(handing, "absent"),
                      False)
        self.assertIsNone(mod09._base_dict_get("no record", "x"))

    def test_consumer_plain_control(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 5}, 1), 6)


def _nested(value, count, form):
    for _ in range(count):
        if form == "list":
            value = [value]
        elif form == "tuple":
            value = (value,)
        else:
            value = {"k": value}
    return value


class TestR20027OutcomeReachProvingActs(unittest.TestCase):

    def test_list_form_reach(self):
        for depth in (102, 150, 200, 201):
            self.assertIs(mod09._outcome_stands_failure(
                _nested("failure found", depth, "list")), True)
        for depth in (202, 3000):
            self.assertIs(mod09._outcome_stands_failure(
                _nested("failure found", depth, "list")), False)

    def test_tuple_form_reach(self):
        for depth in (102, 150, 200, 201):
            self.assertIs(mod09._outcome_stands_failure(
                _nested("failure found", depth, "tuple")), True)
        for depth in (202, 3000):
            self.assertIs(mod09._outcome_stands_failure(
                _nested("failure found", depth, "tuple")), False)

    def test_dict_form_cut(self):
        for depth in (102, 150, 3000):
            self.assertIs(mod09._outcome_stands_failure(
                _nested("failure found", depth, "dict")), False)

    def test_shallow_and_clean_controls(self):
        self.assertIs(mod09._outcome_stands_failure(
            _nested("failure found", 50, "list")), True)
        self.assertIs(mod09._outcome_stands_failure(
            _nested("failure found", 50, "dict")), True)
        self.assertIs(mod09._outcome_stands_failure(
            _nested("no failure", 3000, "list")), False)
        self.assertIs(
            mod09._outcome_stands_failure("failure found"), True)


class TestR20031CatalogueReprDictPart(unittest.TestCase):

    def test_dict_payload_renders_apart(self):
        self.assertNotEqual(
            mod09._catalogue_repr(Holder({"alpha": 1})),
            mod09._catalogue_repr(Holder({"beta": 2})))

    def test_dict_payload_order_keys_apart(self):
        self.assertNotEqual(
            mod09._catalogue_order_key(Holder({"alpha": 1})),
            mod09._catalogue_order_key(Holder({"beta": 2})))

    def test_bare_dict_part_renders_its_pairs(self):
        self.assertNotEqual(
            mod09._catalogue_repr({"alpha": 1}),
            mod09._catalogue_repr({"beta": 2}))
        self.assertEqual(
            mod09._catalogue_repr({"alpha": 1}),
            mod09._catalogue_repr({"alpha": 1}))

    def test_identical_dict_payload_ties_control(self):
        self.assertEqual(
            mod09._catalogue_repr(Holder({"alpha": 1})),
            mod09._catalogue_repr(Holder({"alpha": 1})))

    def test_list_payload_control(self):
        self.assertNotEqual(
            mod09._catalogue_repr(Holder([1, 2])),
            mod09._catalogue_repr(Holder([3, 4])))


class TestR20058AttackerPayoffInProtocolSentence(unittest.TestCase):

    def test_lying_repr_payoff_named_on_its_form(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(
                {"in_protocol_payoff": LieRepr("5")}, 1)
        sentence = str(caught.exception)
        self.assertIn("in no numeric form", sentence)
        self.assertIn("LieRepr", sentence)
        self.assertNotIn("form: 5", sentence)

    def test_combined_sentence_names_stored_number(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(
                {"in_protocol_payoff": LieReprFloat(float("inf"))}, 1)
        sentence = str(caught.exception)
        self.assertIn("in protocol inf", sentence)

    def test_text_payoff_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff({"in_protocol_payoff": "bogus"}, 1)
        self.assertIn("'bogus'", str(caught.exception))

    def test_valid_payoff_control(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 5}, 1), 6)


class TestR20059AttackerPayoffExternalSentence(unittest.TestCase):

    def test_lying_repr_external_named_on_its_form(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(
                {"in_protocol_payoff": 1}, LieRepr("999"))
        sentence = str(caught.exception)
        self.assertIn("in no numeric form", sentence)
        self.assertIn("LieRepr", sentence)
        self.assertNotIn("form: 999", sentence)

    def test_combined_sentence_names_stored_number(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff(
                {"in_protocol_payoff": 1},
                LieReprFloat(float("inf")))
        sentence = str(caught.exception)
        self.assertIn("external inf", sentence)

    def test_text_external_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.attacker_payoff({"in_protocol_payoff": 1}, "bogus")
        self.assertIn("'bogus'", str(caught.exception))

    def test_valid_external_control(self):
        self.assertEqual(
            mod09.attacker_payoff({"in_protocol_payoff": 1}, 2.5), 3.5)


class TestR20060SweepStrategySentence(unittest.TestCase):

    def test_lying_repr_strategy_named_on_its_form(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.sweep_external_profit(LieRepr("5"))
        sentence = str(caught.exception)
        self.assertIn("in no record form", sentence)
        self.assertIn("LieRepr", sentence)
        self.assertNotIn("form: 5", sentence)

    def test_text_strategy_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.sweep_external_profit("bogus")
        self.assertIn("'bogus'", str(caught.exception))

    def test_valid_sweep_control(self):
        result = mod09.sweep_external_profit({
            "in_protocol_payoff": 1, "external_profit_range": [0, 5]})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["attacker_payoff"], 6)


class TestR20061BondSearchCandidateSentence(unittest.TestCase):

    def test_lying_repr_candidate_named_on_its_form(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.bond_search([LieRepr("3")])
        sentence = str(caught.exception)
        self.assertIn("in no record form", sentence)
        self.assertIn("LieRepr", sentence)
        self.assertNotIn("form: 3", sentence)

    def test_text_candidate_control(self):
        with self.assertRaises(mod09.NamedAttackerFailure) as caught:
            mod09.bond_search(["bogus"])
        self.assertIn("'bogus'", str(caught.exception))

    def test_valid_candidate_control(self):
        result = mod09.bond_search([{
            "parameter_set": {"lien multiplier": 2},
            "harm": 10, "attacker_cost": 4}])
        self.assertEqual(result["worst_griefing_factor"], 2.5)


if __name__ == "__main__":
    unittest.main()


# Fix wave 21 pins of this name, composed in union below this line. No landed pin above stands altered.


class RaisingHashKey:
    """A non text dict key whose hash reading raises once armed."""

    armed = False

    def __hash__(self):
        if RaisingHashKey.armed:
            raise RuntimeError("armed hash")
        return 13

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class ArmedTextKey(str):
    """A text key storing one text, whose hash reading raises
    once armed and whose equality reading answers False, so two
    keys storing the same text stand as two entries."""

    armed = False

    def __hash__(self):
        if ArmedTextKey.armed:
            raise RuntimeError("armed hash")
        return 7

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True


def _raising_keys(values):
    RaisingHashKey.armed = False
    handed = {}
    for value in values:
        handed[RaisingHashKey()] = value
    RaisingHashKey.armed = True
    return handed


def _two_raising_keys():
    return _raising_keys(["first", "second"])


def _three_raising_keys():
    return _raising_keys(["first", "second", "third"])


def _one_raising_key():
    return _raising_keys(["only"])


def _plain_candidate_collision():
    RaisingHashKey.armed = False
    handed = {"(carried key 3)": "plain"}
    handed[RaisingHashKey()] = "armed"
    RaisingHashKey.armed = True
    return handed


def _same_text_keys():
    ArmedTextKey.armed = False
    handed = {}
    handed[ArmedTextKey("same")] = "first"
    handed[ArmedTextKey("same")] = "second"
    ArmedTextKey.armed = True
    return handed


TARGET_HELPERS = [
    ("mod03_guarded", mod03._guarded_copy),
    ("mod04_guarded", mod04._guarded_copy),
    ("mod06_undirected", mod06._undirected_copy),
    ("mod07_stored", mod07._stored_copy),
    ("mod08_undirected", mod08._undirected_copy),
    ("mod09_stored", mod09._stored_copy),
    ("mod09_render_safe", mod09._render_safe_copy),
    ("mod10_safe", mod10._safe_copy),
    ("mod11_quoted", mod11._quoted_copy),
    ("mod14_plain_stored", mod14._plain_stored_copy),
]


SISTER_HELPERS = [
    ("mod03_guarded", mod03._guarded_copy),
    ("mod04_guarded", mod04._guarded_copy),
    ("mod06_undirected", mod06._undirected_copy),
    ("mod07_stored", mod07._stored_copy),
    ("mod08_undirected", mod08._undirected_copy),
    ("mod09_stored", mod09._stored_copy),
    ("mod10_safe", mod10._safe_copy),
    ("mod11_quoted", mod11._quoted_copy),
    ("mod14_plain_stored", mod14._plain_stored_copy),
]


CURED_POLES = [
    ("mod01_guarded", mod01._guarded_copy),
    ("mod05_freeze", mod05._freeze),
    ("mod12_freeze", mod12._freeze),
    ("mod13_freeze", mod13._freeze),
    ("mod14_freeze", mod14._freeze),
]


class _ArmedCase(unittest.TestCase):
    def tearDown(self):
        RaisingHashKey.armed = False
        ArmedTextKey.armed = False


class TestR21001RenderSafeCopy(_ArmedCase):
    """Row R21-001: MOD-09 _render_safe_copy, two and three keys."""

    def test_two_keys_delivered_whole(self):
        result = mod09._render_safe_copy(_two_raising_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["first", "second"])

    def test_three_keys_delivered_whole(self):
        result = mod09._render_safe_copy(_three_raising_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        self.assertEqual(
            sorted(result.values()), ["first", "second", "third"])


class TestR21002SisterHelpers(_ArmedCase):
    """Row R21-002: the two key handing at each sister helper."""

    def _check_two(self, helper):
        result = helper(_two_raising_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["first", "second"])

    def test_mod03_two_keys(self):
        self._check_two(mod03._guarded_copy)

    def test_mod04_two_keys(self):
        self._check_two(mod04._guarded_copy)

    def test_mod06_two_keys(self):
        self._check_two(mod06._undirected_copy)

    def test_mod07_two_keys(self):
        self._check_two(mod07._stored_copy)

    def test_mod08_two_keys(self):
        self._check_two(mod08._undirected_copy)

    def test_mod09_stored_two_keys(self):
        self._check_two(mod09._stored_copy)

    def test_mod10_two_keys(self):
        self._check_two(mod10._safe_copy)

    def test_mod11_two_keys(self):
        self._check_two(mod11._quoted_copy)

    def test_mod14_two_keys(self):
        self._check_two(mod14._plain_stored_copy)

    def test_mod14_plain_candidate_collision(self):
        result = mod14._plain_stored_copy(_plain_candidate_collision())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["armed", "plain"])

    def test_mod14_same_text_keys(self):
        result = mod14._plain_stored_copy(_same_text_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["first", "second"])


class TestCuredPoleControls(_ArmedCase):
    """Controls: the five cured poles deliver two keys whole."""

    def _check_two(self, helper):
        result = helper(_two_raising_keys())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result.values()), ["first", "second"])

    def test_mod01_pole_two_keys(self):
        self._check_two(mod01._guarded_copy)

    def test_mod05_pole_two_keys(self):
        self._check_two(mod05._freeze)

    def test_mod12_pole_two_keys(self):
        self._check_two(mod12._freeze)

    def test_mod13_pole_two_keys(self):
        self._check_two(mod13._freeze)

    def test_mod14_pole_two_keys(self):
        self._check_two(mod14._freeze)


class TestSingleKeyControls(_ArmedCase):
    """Controls: a single armed key handing at each target helper."""

    def _check_one(self, helper):
        result = helper(_one_raising_key())
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.values()), ["only"])

    def test_mod03_one_key(self):
        self._check_one(mod03._guarded_copy)

    def test_mod04_one_key(self):
        self._check_one(mod04._guarded_copy)

    def test_mod06_one_key(self):
        self._check_one(mod06._undirected_copy)

    def test_mod07_one_key(self):
        self._check_one(mod07._stored_copy)

    def test_mod08_one_key(self):
        self._check_one(mod08._undirected_copy)

    def test_mod09_stored_one_key(self):
        self._check_one(mod09._stored_copy)

    def test_mod09_render_safe_one_key(self):
        self._check_one(mod09._render_safe_copy)

    def test_mod10_one_key(self):
        self._check_one(mod10._safe_copy)

    def test_mod11_one_key(self):
        self._check_one(mod11._quoted_copy)

    def test_mod14_one_key(self):
        self._check_one(mod14._plain_stored_copy)


class TestPlainControls(_ArmedCase):
    """Controls: plain handings at each target helper."""

    def _check_plain(self, helper):
        result = helper({"a": 1, "b": 2})
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_mod03_plain(self):
        self._check_plain(mod03._guarded_copy)

    def test_mod04_plain(self):
        self._check_plain(mod04._guarded_copy)

    def test_mod06_plain(self):
        self._check_plain(mod06._undirected_copy)

    def test_mod07_plain(self):
        self._check_plain(mod07._stored_copy)

    def test_mod08_plain(self):
        self._check_plain(mod08._undirected_copy)

    def test_mod09_stored_plain(self):
        self._check_plain(mod09._stored_copy)

    def test_mod09_render_safe_plain(self):
        self._check_plain(mod09._render_safe_copy)

    def test_mod10_plain(self):
        self._check_plain(mod10._safe_copy)

    def test_mod11_plain(self):
        self._check_plain(mod11._quoted_copy)

    def test_mod14_plain(self):
        self._check_plain(mod14._plain_stored_copy)


if __name__ == "__main__":
    unittest.main()

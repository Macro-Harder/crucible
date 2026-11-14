"""Pins for Round 12 rows R12-046 to R12-055.

MOD-09 merge form M-06 under settlement S-8, and the MOD-02 next
ring, with the MOD-07 and MOD-12 limbs of row R12-055. Each test
pins the defect its row states with the proving acts the source
papers used, beside the plain controls those papers ran.
"""
import datetime
import subprocess
import sys
import unittest
from pathlib import Path

from crucible import mod02, mod07, mod09, mod12


def _search_record(strategy_class):
    carriage = mod09.run_record_carriage(
        list(strategy_class), 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategy_class))
    return mod09.build_search_record(
        carriage, points_tried=["point one"],
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
        external_profit_swept_values=[0, 5])


class IterLie:
    """Stores nothing, iterates as the one member class."""

    def __init__(self, reported):
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)


class DictIterLie(dict):
    """Stores another class, iterates as the member class."""

    def __iter__(self):
        return iter(["conditional briber", "conditional lender"])


class StrIterLie(str):
    """Stores other text, iterates as the member class list."""

    def __iter__(self):
        return iter(["conditional briber", "conditional lender"])


class TestR12046SetFormOrder(unittest.TestCase):
    def test_two_member_set_and_frozenset_validate(self):
        record = _search_record(
            ["conditional briber", "conditional lender"])
        self.assertTrue(mod09.validate_search_record(record))
        self.assertTrue(mod09.validate_search_record(
            record, {"conditional briber", "conditional lender"}))
        self.assertTrue(mod09.validate_search_record(
            record,
            frozenset(["conditional briber", "conditional lender"])))

    def test_three_member_set_validates(self):
        record = _search_record(["alpha", "beta", "gamma"])
        self.assertTrue(mod09.validate_search_record(
            record, {"alpha", "beta", "gamma"}))
        self.assertTrue(mod09.validate_search_record(
            record, frozenset(["gamma", "alpha", "beta"])))

    def test_set_form_deterministic_across_hash_seeds(self):
        root = Path(__file__).resolve().parents[1]
        program = (
            "from crucible import mod09\n"
            "c = mod09.run_record_carriage(\n"
            "    ['conditional briber', 'conditional lender'], 6,\n"
            "    'catalogue version 1', 'ladder definition pointer',\n"
            "    'ladder version 1',\n"
            "    strategies=['conditional briber',\n"
            "                'conditional lender'])\n"
            "r = mod09.build_search_record(\n"
            "    c, points_tried=['point one'],\n"
            "    per_point_outcome=[{'point': 'point one',\n"
            "                        'outcome': 'no failure'}],\n"
            "    bond_candidates=[{'parameter_set': {\n"
            "        'lien multiplier': 2, 'lien floor': 5,\n"
            "        'cost rule prices': 3},\n"
            "        'harm': 10, 'attacker_cost': 4}],\n"
            "    budget='stated budget',\n"
            "    neighbourhood={'definition': 'adjacent points',\n"
            "                   'step sizes': [1]},\n"
            "    starting_points=['point zero'],\n"
            "    order_of_search=['point one'],\n"
            "    external_profit_swept_values=[0, 5])\n"
            "print(mod09.validate_search_record(\n"
            "    r, {'conditional briber', 'conditional lender'}))\n"
        )
        for seed in ("0", "1", "2", "4", "7", "42"):
            proc = subprocess.run(
                [sys.executable, "-c", program], cwd=str(root),
                env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "True",
                             "seed " + seed)

    def test_list_and_tuple_order_insensitive(self):
        record = _search_record(
            ["conditional briber", "conditional lender"])
        self.assertTrue(mod09.validate_search_record(
            record, ["conditional briber", "conditional lender"]))
        self.assertTrue(mod09.validate_search_record(
            record, ["conditional lender", "conditional briber"]))
        self.assertTrue(mod09.validate_search_record(
            record, ("conditional lender", "conditional briber")))
        self.assertFalse(mod09.validate_search_record(
            record, ["conditional briber", "other class"]))
        self.assertFalse(mod09.validate_search_record(
            record, {"conditional briber"}))
        self.assertFalse(mod09.validate_search_record(
            record, ["conditional briber"]))


class TestR12047HandedIterationFallback(unittest.TestCase):
    def test_handled_iteration_forms_refused(self):
        record = _search_record(
            ["conditional briber", "conditional lender"])
        self.assertFalse(mod09.validate_search_record(
            record, IterLie(
                ["conditional briber", "conditional lender"])))
        self.assertFalse(mod09.validate_search_record(
            record, DictIterLie({"other class": 1})))
        self.assertFalse(mod09.validate_search_record(
            record, {"conditional briber": 1,
                     "conditional lender": 2}))
        self.assertFalse(mod09.validate_search_record(
            record, StrIterLie("completely other stored text")))
        self.assertFalse(mod09.validate_search_record(
            record, "conditional briber"))


class TestR12048NonIterableFixedClass(unittest.TestCase):
    def test_non_iterable_fixed_class_refused_in_plain_false(self):
        record = _search_record(
            ["conditional briber", "conditional lender"])
        for fixed in (123, 5.5, object()):
            self.assertFalse(mod09.validate_search_record(
                record, fixed))
        self.assertTrue(mod09.validate_search_record(record))
        self.assertTrue(mod09.validate_search_record(record, None))


class ValuesPropertyLie:
    """Carries no inventory in its instance dict, reports one
    through a values property."""

    @property
    def values(self):
        return {"stream_class_inventory": ["ghost"]}


class TestR12049StreamSetValuesReading(unittest.TestCase):
    def test_values_property_lie_refused(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                {"ghost": 1}, ValuesPropertyLie())

    def test_controls(self):
        self.assertFalse(mod02.validate_stream_cardinality(
            {"ghost": 1}, {"stream_class_inventory": ["real"]}))
        self.assertTrue(mod02.validate_stream_cardinality(
            {"cls1": 1}, {"stream_class_inventory": ["cls1"]}))
        typed = mod02.StreamSet(
            {"stream_class_inventory": ["cls1"]})
        self.assertTrue(mod02.validate_stream_cardinality(
            {"cls1": 1}, typed))


class IntReadingLie:
    """Stands in no number form, reports 999 through its int
    reading."""

    def __int__(self):
        return 999

    __index__ = __int__


class TestR12050PositionValueFallback(unittest.TestCase):
    def test_int_reading_lie_refused_at_both_acts(self):
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=IntReadingLie(),
                carried_positions=10)
        with self.assertRaises(ValueError):
            mod02.initial_stream_state("s", IntReadingLie())

    def test_list_position_refused_as_value_error(self):
        with self.assertRaises(ValueError):
            mod02.draw_from_stream(
                stream_class="s", position=[1],
                carried_positions=10)

    def test_plain_controls(self):
        exhausted = mod02.draw_from_stream(
            stream_class="s", position=99, carried_positions=10)
        self.assertEqual(exhausted["failure"], "STREAM-EXHAUSTED")
        self.assertEqual(exhausted["position"], 99)
        inside = mod02.draw_from_stream(
            stream_class="s", position=0, carried_positions=10)
        self.assertEqual(inside["failure"], "DERIVATION-GATED")
        state = mod02.initial_stream_state("s", 10)
        self.assertEqual(state["carried_positions"], 10)


class TestR12051BaseValueEqBuffersAndDates(unittest.TestCase):
    def test_equal_buffer_and_date_copies_agree(self):
        self.assertTrue(mod02.validate_generator_state_carriage(
            {"a": bytearray(b"xy")}, {"a": bytearray(b"xy")}))
        self.assertTrue(mod02.validate_generator_state_carriage(
            {"a": memoryview(b"xy")}, {"a": memoryview(b"xy")}))
        self.assertTrue(mod02.validate_generator_state_carriage(
            {"a": datetime.date(2026, 1, 2)},
            {"a": datetime.date(2026, 1, 2)}))

    def test_unequal_copies_still_refused_and_controls(self):
        self.assertFalse(mod02.validate_generator_state_carriage(
            {"a": bytearray(b"xy")}, {"a": bytearray(b"xz")}))
        self.assertFalse(mod02.validate_generator_state_carriage(
            {"a": memoryview(b"xy")}, {"a": memoryview(b"xz")}))
        self.assertFalse(mod02.validate_generator_state_carriage(
            {"a": datetime.date(2026, 1, 2)},
            {"a": datetime.date(2026, 1, 3)}))
        self.assertTrue(mod02.validate_generator_state_carriage(
            {"a": b"xy"}, {"a": b"xy"}))
        self.assertTrue(mod02.validate_generator_state_carriage(
            {"a": 3}, {"a": 3}))


class GhostStrKey:
    """Stores no text, reports ghostkey through its string
    reading."""

    def __str__(self):
        return "ghostkey"

    def __repr__(self):
        return "ghostkey"


class TestR12052StoredName(unittest.TestCase):
    def _input(self, params):
        return {
            "derivation_version": "v1", "domain": "screening",
            "root_seed_reference": "r", "scenario_identifier": "sc",
            "run_identifier": "run",
            "stream_class_identifier": "cls",
            "parameter_values": params}

    def test_ghost_key_name_not_rendered(self):
        record = mod02.derivation_input_record(
            self._input({GhostStrKey(): "val"}))
        self.assertNotIn("ghostkey=val",
                         record["parameter_values"])
        for rendered in record["parameter_values"]:
            self.assertFalse(rendered.startswith("ghostkey="))
        encoded = mod02.encode_candidate_input(
            {GhostStrKey(): "val"})
        self.assertNotIn("ghostkey", encoded)

    def test_plain_integer_key_renders_its_digits(self):
        record = mod02.derivation_input_record(
            self._input({5: "val"}))
        self.assertEqual(record["parameter_values"], ("5=val",))
        encoded = mod02.encode_candidate_input({5: "val"})
        self.assertIn("5", encoded)


class IterListLie(list):
    """Stores one pair, iterates as a ghost pair."""

    def __iter__(self):
        return iter([("ghost", "9")])


class TestR12053MakeDerivationInputNonDict(unittest.TestCase):
    def test_list_form_builds_stored_pairs_only(self):
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values=IterListLie([("p", "1")]))
        self.assertEqual(built["parameter_values"], {"p": "1"})

    def test_controls_and_no_form_refusal(self):
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values={"p": "1"})
        self.assertEqual(built["parameter_values"], {"p": "1"})
        built = mod02.make_derivation_input(
            derivation_version="v1", domain="screening",
            parameter_values=[("q", "2")])
        self.assertEqual(built["parameter_values"], {"q": "2"})
        with self.assertRaises(ValueError):
            mod02.make_derivation_input(
                derivation_version="v1", domain="screening",
                parameter_values=12345)


class LowerLieBarred(str):
    """Stores the barred form, reports clean text through its
    lower reading."""

    def lower(self):
        return "a clean derivation note"


class LowerLieClean(str):
    """Stores clean text, reports the barred form through its
    lower reading."""

    def lower(self):
        return "arithmetic on a root seed"


class TestR12054DerivationTextRefusalLower(unittest.TestCase):
    def test_lower_reading_lies_judged_on_stored_text(self):
        barred = "arithmetic on a root seed"
        self.assertEqual(
            mod02.derivation_text_refusal(barred)["failure"],
            "BARRED-DERIVATION-FORM")
        self.assertEqual(
            mod02.derivation_text_refusal(
                LowerLieBarred(barred))["failure"],
            "BARRED-DERIVATION-FORM")
        self.assertEqual(
            mod02.derivation_text_refusal(
                LowerLieClean("a clean derivation note"))["failure"],
            "DERIVATION-GATED")
        self.assertFalse(mod02.validate_family_derivation_text(
            LowerLieBarred(barred)))


class HashRuntimeLie:
    """Its hash reading raises RuntimeError."""

    def __hash__(self):
        raise RuntimeError("hash reading fails")


class TestR12055Mod02HashForm(unittest.TestCase):
    def test_hash_runtime_error_escapes_as_value_error(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                {"x": 1},
                {"stream_class_inventory": [HashRuntimeLie()]})

    def test_unhashable_entry_still_value_error(self):
        with self.assertRaises(ValueError):
            mod02.validate_stream_cardinality(
                {"x": 1},
                {"stream_class_inventory": [["x"]]})


class StrRuntimeKey:
    """A dict key whose string reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("string reading fails")

    def __repr__(self):
        raise RuntimeError("string reading fails")

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return self is other


class TestR12055Mod07CopyGuardPath(unittest.TestCase):
    def test_str_raising_key_does_not_escape_bare(self):
        key = StrRuntimeKey()
        choice = mod07.make_adapter_choice(
            "c1", "reading", "point", "gov", "variant",
            approval={key: "v"})
        self.assertEqual(choice["choice_identifier"], "c1")
        report = mod07.seam_effect_report(
            {key: "v", "kind": "x", "value": 1})
        self.assertEqual(report["effect"], "x")

    def test_guard_named_refusals_still_stand(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(ValueError):
            mod07.make_adapter_choice(
                "c1", "reading", "point", "gov", "variant",
                approval={"a": cyclic})


class EqAllClass:
    """A non text run class whose equality answers True to
    every comparison."""

    def __eq__(self, other):
        return True

    def __hash__(self):
        return 1


class BogusStrEqAll(str):
    """Stores bogus, its equality answers True against every
    stated class."""

    def __eq__(self, other):
        return True

    def __hash__(self):
        return str.__hash__(self)


class TruthyFamilyId:
    """Carries no stored text, its truth reading returns True."""

    def __bool__(self):
        return True


class TestR12055Mod12StartRun(unittest.TestCase):
    def test_run_class_judged_on_stored_form(self):
        self.assertEqual(
            mod12.start_run(
                run_class=EqAllClass(), family_id="fam")["status"],
            "input failure")
        self.assertEqual(
            mod12.start_run(
                run_class=BogusStrEqAll("bogus"),
                family_id="fam")["status"],
            "input failure")
        self.assertEqual(
            mod12.start_run(
                run_class="bogus", family_id="fam")["status"],
            "input failure")
        self.assertEqual(
            mod12.start_run(
                run_class="screening", family_id="fam")["status"],
            "gated")

    def test_family_identifier_judged_on_stored_presence(self):
        self.assertEqual(
            mod12.start_run(
                run_class="screening",
                family_id=TruthyFamilyId())["status"],
            "input failure")
        self.assertEqual(
            mod12.start_sweep(
                family_id=TruthyFamilyId())["status"],
            "input failure")
        self.assertEqual(
            mod12.start_sweep(family_id="fam")["status"], "gated")
        self.assertEqual(
            mod12.start_run(run_class="screening")["status"],
            "input failure")


if __name__ == "__main__":
    unittest.main()

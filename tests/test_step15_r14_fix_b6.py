"""Pins for Round 13 rows R13-024, R13-026, R13-027, R13-035,
R13-044, R13-045, and R13-048.

MOD-09 search, readout, companion, and catalogue forms. Each test
pins the defect its row states with the proving acts the source
papers used (Red 2 Finding 5, Blue 4 Findings 1 and 2, Red 4
Finding 1, Orange 1 Finding 6, Orange 2 Findings 5 and 6), beside
the plain controls those papers ran.
"""
import subprocess
import sys
import unittest
from pathlib import Path

from crucible import mod09


def _carriage(strategies=("conditional briber",)):
    return mod09.run_record_carriage(
        list(strategies), 6, "catalogue version 1",
        "ladder definition pointer", "ladder version 1",
        strategies=list(strategies))


def _record(outcome="no failure", swept_values=(0, 5), **kwargs):
    return mod09.build_search_record(
        _carriage(), points_tried=["point one"],
        per_point_outcome=[{"point": "point one",
                            "outcome": outcome}],
        bond_candidates=[{
            "parameter_set": {"lien multiplier": 2, "lien floor": 5,
                              "cost rule prices": 3},
            "harm": 10, "attacker_cost": 4}],
        budget="stated budget",
        neighbourhood={"definition": "adjacent points",
                       "step sizes": [1]},
        starting_points=["point zero"],
        order_of_search=["point one"],
        external_profit_swept_values=swept_values, **kwargs)


def _class_record(members):
    record = _record()
    record["run_record"]["strategy_class"] = list(members)
    record["run_record"]["strategies_exercised"] = list(members)
    return record


class IterLieList(list):
    """Stores one set of items, iterates as another."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = list(reported)

    def __iter__(self):
        return iter(self._reported)


class LenZeroList(list):
    """Stores items, reports a length of zero."""

    def __len__(self):
        return 0


class EqAll:
    """Stores nothing equal, answers True to every comparison."""

    def __eq__(self, other):
        return True

    def __hash__(self):
        return 1


class EqRaises:
    """Its equality reading raises on every comparison."""

    def __eq__(self, other):
        raise RuntimeError("equality reading raises")

    def __hash__(self):
        return 2


class GetLieDict(dict):
    """Stores one outcome, reports another through get."""

    def __init__(self, stored, reported):
        super().__init__(stored)
        self._reported = reported

    def get(self, key, default=None):
        return self._reported.get(key, default)


class TestR13024BuildSearchRecordContainers(unittest.TestCase):

    def test_case_uses_iteration_lie_not_delivered(self):
        stored = [{"fixture": "other", "use": "another use"}]
        reported = [{"fixture": "F-26", "use": "whatever"}]
        record = _record(case_uses=IterLieList(stored, reported))
        self.assertEqual(record["case_uses"], stored)

    def test_case_uses_length_lie_stored_use_delivered(self):
        stored = [{"fixture": "F-26", "use": "whatever"}]
        record = _record(case_uses=LenZeroList(stored))
        self.assertEqual(len(record["case_uses"]), 1)
        self.assertEqual(
            record["case_uses"][0]["use"],
            "strategy search point only")
        self.assertEqual(
            record["case_uses"][0]["standings_carried"],
            list(mod09.SELFISH_MINING_STANDINGS))

    def test_swept_values_iteration_lie_not_delivered(self):
        record = _record(
            swept_values=IterLieList([0, 5], [999]))
        self.assertEqual(record["external_profit_swept_values"],
                         [0, 5])

    def test_adaptations_length_lie_stored_delivered(self):
        stored = [{"adaptation": "adaptation one"}]
        record = _record(adaptations=LenZeroList(stored))
        self.assertEqual(
            record["search_record"]["every_adaptation"], stored)

    def test_plain_containers_delivered_as_handed(self):
        uses = [{"fixture": "F-26", "use": "whatever"}]
        adaptations = [{"adaptation": "adaptation one"}]
        record = _record(case_uses=uses, adaptations=adaptations,
                         swept_values=[0, 7])
        self.assertEqual(record["external_profit_swept_values"],
                         [0, 7])
        self.assertEqual(
            record["search_record"]["every_adaptation"], adaptations)
        self.assertEqual(
            record["case_uses"][0]["use"],
            "strategy search point only")


class TestR13026FixedClassNonTextEquality(unittest.TestCase):

    def test_record_class_against_eqall_fixed_class(self):
        record = _class_record([123])
        self.assertFalse(
            mod09.validate_search_record(record, [EqAll()]))
        ok, failures = mod09.validate_search_record_with_reason(
            record, [EqAll()])
        self.assertFalse(ok)
        self.assertIn(
            "the exercised strategy class does not stand as "
            "the fixed class", failures)

    def test_eqall_record_against_plain_fixed_class(self):
        record = _class_record([EqAll()])
        self.assertFalse(
            mod09.validate_search_record(record, [object()]))
        ok, failures = mod09.validate_search_record_with_reason(
            record, [object()])
        self.assertFalse(ok)
        self.assertIn(
            "the exercised strategy class does not stand as "
            "the fixed class", failures)

    def test_plain_numeric_controls(self):
        record = _class_record([123])
        self.assertTrue(
            mod09.validate_search_record(record, [123]))
        self.assertFalse(
            mod09.validate_search_record(record, [124]))

    def test_text_member_blocks_the_lie(self):
        record = _class_record(["alpha"])
        self.assertFalse(
            mod09.validate_search_record(record, {EqAll()}))
        self.assertTrue(
            mod09.validate_search_record(record, ["alpha"]))


class TestR13027RaisingEqualityRefusedPlainly(unittest.TestCase):

    def test_raising_fixed_member_refused(self):
        record = _class_record([123])
        self.assertFalse(
            mod09.validate_search_record(record, [EqRaises()]))
        ok, failures = mod09.validate_search_record_with_reason(
            record, [EqRaises()])
        self.assertFalse(ok)
        self.assertIn(
            "the exercised strategy class does not stand as "
            "the fixed class", failures)

    def test_raising_record_member_refused(self):
        record = _class_record([EqRaises()])
        self.assertFalse(
            mod09.validate_search_record(record, [123]))
        ok, failures = mod09.validate_search_record_with_reason(
            record, [123])
        self.assertFalse(ok)
        self.assertIn(
            "the exercised strategy class does not stand as "
            "the fixed class", failures)


class TestR13035CatalogueBytesTieBreak(unittest.TestCase):

    def test_bytes_keys_distinct_on_raw_stored_bytes(self):
        keys = {
            mod09._catalogue_order_key(value)
            for value in (b"a", b"\xffa", b"\x80a", b"\xfda")}
        self.assertEqual(len(keys), 4)

    def test_memoryview_keys_distinct_on_raw_stored_bytes(self):
        first = mod09._catalogue_order_key(memoryview(b"c"))
        second = mod09._catalogue_order_key(memoryview(b"\xffc"))
        self.assertNotEqual(first, second)

    def test_catalogue_order_stable_across_hash_seeds(self):
        root = Path(__file__).resolve().parents[1]
        program = (
            "from crucible import mod09\n"
            "extras = {b'a', b'\\xffa', b'\\x80a', b'\\xfda', b'b',"
            " b'\\xffb', memoryview(b'c'), memoryview(b'\\xffc')}\n"
            "cat = mod09.strategy_catalogue(extras)\n"
            "print([(type(x).__name__, bytes(x).hex())\n"
            "       for x in cat['identifiers']\n"
            "       if isinstance(x, (bytes, memoryview))])\n"
        )
        orders = []
        for seed in ("0", "1", "2", "7", "42"):
            proc = subprocess.run(
                [sys.executable, "-c", program], cwd=str(root),
                env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            orders.append(proc.stdout.strip())
        self.assertEqual(len(set(orders)), 1, orders)

    def test_text_and_plain_catalogue_controls(self):
        cat = mod09.strategy_catalogue({"beta", "alpha"})
        extras = [name for name in cat["identifiers"]
                  if name in ("alpha", "beta")]
        self.assertEqual(extras, ["alpha", "beta"])


class TestR13044ReadoutConsultsRecordOutcomes(unittest.TestCase):

    def test_no_failure_sentence_withheld_on_failure_record(self):
        record = _record(outcome="failure found")
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_stored_outcome_read_not_reported_outcome(self):
        record = _record(outcome="failure found")
        entry = GetLieDict(
            record["search_record"]["per_point_outcome"][0],
            {"point": "point one", "outcome": "no failure"})
        record["search_record"]["per_point_outcome"] = [entry]
        unit = mod09.readout(record, found_failure=False)
        self.assertNotIn("no_failure_sentence", unit)

    def test_no_failure_sentence_on_clean_record(self):
        record = _record(outcome="no failure")
        unit = mod09.readout(record, found_failure=False)
        self.assertEqual(unit["no_failure_sentence"],
                         mod09.NO_FAILURE_SENTENCE)

    def test_default_and_true_flag_stand(self):
        record = _record(outcome="failure found")
        self.assertNotIn(
            "no_failure_sentence", mod09.readout(record))
        self.assertNotIn(
            "no_failure_sentence",
            mod09.readout(record, found_failure=True))


class TestR13045ReadoutWordingAndResultKind(unittest.TestCase):

    def test_established_wording_refused(self):
        record = _record()
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                record,
                wording="established: the system stands "
                        "economically secure")

    def test_economically_secure_wording_refused(self):
        record = _record()
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(
                record,
                wording="the system stands economically secure")

    def test_result_kind_stated_outside_in_protocol_only(self):
        unit = mod09.readout(_record())
        self.assertEqual(unit.get("result_kind"),
                         "economic security result")
        self.assertEqual(unit["readout_status"],
                         "at the readout point, not established")

    def test_result_kind_in_protocol_only_control(self):
        record = _record()
        record["external_profit_swept_values"] = [0]
        unit = mod09.readout(record)
        self.assertEqual(unit["result_kind"],
                         "in protocol result only")

    def test_plain_wording_and_established_flag_controls(self):
        unit = mod09.readout(
            _record(), wording="readout wording for the search")
        self.assertEqual(unit["wording"],
                         "readout wording for the search")
        with self.assertRaises(mod09.NamedAttackerFailure):
            mod09.readout(_record(), established=True)


class TestR13048ReasonTwinWrongFormWording(unittest.TestCase):

    def test_search_field_list_in_no_record_form(self):
        for bad in ("text", ["point one"]):
            record = _record()
            record["search_record"] = bad
            ok, failures = mod09.validate_search_record_with_reason(
                record)
            self.assertFalse(ok)
            self.assertEqual(
                failures,
                ["the search record field list stands in no "
                 "record form"], repr(bad))

    def test_bond_limb_in_no_record_form(self):
        for bad in ("text", ["lien multiplier"]):
            record = _record()
            record["bond_parameter_search"] = bad
            ok, failures = mod09.validate_search_record_with_reason(
                record)
            self.assertFalse(ok)
            self.assertEqual(
                failures,
                ["the bond parameter search limb stands in no "
                 "record form"], repr(bad))

    def test_absent_bond_limb_still_named_absent(self):
        record = _record()
        del record["bond_parameter_search"]
        ok, failures = mod09.validate_search_record_with_reason(
            record)
        self.assertFalse(ok)
        self.assertIn(
            "the bond parameter search limb stands absent", failures)

    def test_lawful_record_control(self):
        ok, failures = mod09.validate_search_record_with_reason(
            _record())
        self.assertTrue(ok)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()

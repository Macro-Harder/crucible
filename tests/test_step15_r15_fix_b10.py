"""Pins for fix wave 14, Builder 10: rows R14-066 to R14-068
and R14-086 of the Round 14 register.

R14-066: the MOD-13 failures companions answer in plain form
on a field value whose repr reading raises, where their boolean
acts return a plain False on the same record.
R14-067: the MOD-06 escrow refusals and the MOD-03 farm edge
refusals stand as full named refusals on a handed value whose
string or repr reading raises.
R14-068: the MOD-04 cleaning depth form and the MOD-13
extend_history bound grounds state their consequence, and the
extend_history cycle ground states its counting as well.
R14-086: MOD-04 carries an __all__ enumerating its public
surface, as every sibling slice module does.
"""

import types
import unittest

from crucible import mod03, mod04, mod06, mod13


class ReprRaises:
    """A plain value whose repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class StrRaises:
    """A plain value whose str reading raises RuntimeError."""

    def __str__(self):
        raise RuntimeError("str boom")


class StrReprRaises(str):
    """Stores text, its repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class ReprRaisesList(list):
    """Stores list parts, its repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


class ReprRaisesDict(dict):
    """Stores dict parts, its repr reading raises RuntimeError."""

    def __repr__(self):
        raise RuntimeError("repr boom")


def deep_list(depth):
    value = "leaf"
    for _ in range(depth):
        value = [value]
    return value


def cyclic_list():
    value = []
    value.append(value)
    return value


class TestR14066Mod13CompanionsReprRaising(unittest.TestCase):

    def test_verdict_outcome_repr_raising(self):
        record = mod13.verdict_record("claim-1")
        record["outcome"] = ReprRaises()
        self.assertFalse(mod13.validate_verdict_record(record))
        failures = mod13.verdict_record_validation_failures(record)
        self.assertTrue(
            any("outcome stands outside" in item for item in failures),
            failures)

    def test_verdict_standard_repr_raising(self):
        record = mod13.verdict_record("claim-1")
        record["standard_applied"] = ReprRaises()
        self.assertFalse(mod13.validate_verdict_record(record))
        failures = mod13.verdict_record_validation_failures(record)
        self.assertTrue(
            any("standard_applied stands outside" in item
                for item in failures),
            failures)

    def test_publishable_outcome_repr_raising(self):
        verdict = mod13.verdict_record("claim-1")
        verdict["outcome"] = ReprRaises()
        claim = {"claim_identifier": "claim-1"}
        self.assertFalse(
            mod13.publishable_on_replication(claim, verdict))
        failures = mod13.publishable_on_replication_failures(
            claim, verdict)
        self.assertTrue(failures)
        self.assertTrue(
            any("outcome" in item for item in failures), failures)

    def test_publishable_plain_outcome_sentence_control(self):
        verdict = mod13.verdict_record("claim-1")
        verdict["outcome"] = "does not rest"
        failures = mod13.publishable_on_replication_failures(
            {"claim_identifier": "claim-1"}, verdict)
        self.assertTrue(
            any("does not rest" in item
                and "publication requires" in item
                for item in failures),
            failures)

    def test_rerun_read_as_repr_raising(self):
        reading = {"read_as": ReprRaises()}
        self.assertFalse(mod13.validate_rerun_reading(reading))
        failures = mod13.rerun_reading_validation_failures(reading)
        self.assertTrue(
            any("read_as stands outside" in item for item in failures),
            failures)

    def test_resume_scope_repr_raising(self):
        claim = {"detection_scope": ReprRaises()}
        self.assertFalse(mod13.validate_resume_claim(claim))
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertTrue(
            any("detection_scope stands wider" in item
                for item in failures),
            failures)

    def test_resume_foreign_point_repr_raising(self):
        claim = {"detection_comparison_points": [
            ReprRaises(), "run close"]}
        self.assertFalse(mod13.validate_resume_claim(claim))
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertTrue(
            any("outside the two named points" in item
                for item in failures),
            failures)

    def test_resume_positional_point_repr_raising(self):
        claim = {"detection_comparison_points": [
            StrReprRaises("run close"),
            "first verdict state after resume"]}
        self.assertFalse(mod13.validate_resume_claim(claim))
        failures = mod13.resume_claim_validation_failures(claim)
        self.assertTrue(failures)
        for item in failures:
            self.assertNotIn("outside the two named points", item)
        self.assertTrue(
            any("position" in item or "order" in item
                for item in failures),
            failures)

    def test_neighbouring_companions_control(self):
        self.assertTrue(mod13.aggregate_form_validation_failures(
            [ReprRaises()]))
        self.assertTrue(mod13.probe_claim_validation_failures(
            {"catalogue_presented_as_settled": ReprRaises()}))
        self.assertEqual(
            mod13.verdict_record_validation_failures(
                mod13.verdict_record("claim-1")), [])


class TestR14067EscrowRefusalsRaisingReadings(unittest.TestCase):

    def test_contract_state_variant_str_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", variant=StrRaises())
        text = str(caught.exception)
        self.assertIn("escrow_contract_state stands refused", text)
        self.assertIn("no escrow contract state stands returned", text)

    def test_contract_state_variant_repr_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", variant=ReprRaises())
        text = str(caught.exception)
        self.assertIn("escrow_contract_state stands refused", text)
        self.assertIn("no escrow contract state stands returned", text)

    def test_contract_state_lien_str_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", lien_state=StrRaises())
        text = str(caught.exception)
        self.assertIn("lien state", text)
        self.assertIn("no escrow contract state stands returned", text)

    def test_contract_state_lien_repr_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", lien_state=ReprRaises())
        text = str(caught.exception)
        self.assertIn("lien state", text)
        self.assertIn("no escrow contract state stands returned", text)

    def test_result_variant_repr_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_result("k", variant=ReprRaises())
        text = str(caught.exception)
        self.assertIn("escrow_result stands refused", text)
        self.assertIn("no escrow result stands returned", text)

    def test_result_variant_str_raising(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_result("k", variant=StrRaises())
        text = str(caught.exception)
        self.assertIn("escrow_result stands refused", text)
        self.assertIn("no escrow result stands returned", text)

    def test_plain_bogus_controls(self):
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", variant="B-9")
        self.assertIn("B-9", str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_contract_state("c-1", lien_state="bogus lien")
        self.assertIn("bogus lien", str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            mod06.escrow_result("k", variant="B-9")
        self.assertIn("B-9", str(caught.exception))


class TestR14067FarmEdgeRefusalsRaisingReadings(unittest.TestCase):

    def test_scalar_edge_repr_raising(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["a", "b"], 2, edges=[ReprRaises()])
        text = str(caught.exception)
        self.assertIn("farm rejected", text)
        self.assertIn("not as a voucher and vouchee pair", text)

    def test_three_part_list_edge_repr_raising(self):
        edge = ReprRaisesList(["a", "b", "c"])
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["a", "b"], 2, edges=[edge])
        text = str(caught.exception)
        self.assertIn("farm rejected", text)
        self.assertIn("pair of size two", text)

    def test_dict_edge_repr_raising(self):
        edge = ReprRaisesDict({"vouchee": "b"})
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["a", "b"], 2, edges=[edge])
        text = str(caught.exception)
        self.assertIn("farm rejected", text)
        self.assertIn("carries no voucher", text)

    def test_plain_edge_controls(self):
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(["a", "b"], 2, edges=[42])
        self.assertIn("42", str(caught.exception))
        with self.assertRaises(mod03.NamedGeneratorFailure) as caught:
            mod03.construct_farm(
                ["a", "b"], 2, edges=[["a", "b", "c"]])
        self.assertIn("pair of size two", str(caught.exception))
        result = mod03.construct_farm(
            ["a", "b"], 2, edges=[["a", "b"]])
        self.assertEqual(
            result["internal_edge_count_per_farm_identity"],
            {"farm-0": 1})


class TestR14068GuardConsequences(unittest.TestCase):

    def test_mod04_cleaning_depth_states_consequence(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04._clean_value(deep_list(105))
        text = str(caught.exception)
        self.assertIn("bound of 100", text)
        self.assertIn("counting every container", text)
        self.assertIn("no cleaning stands performed", text)

    def test_mod04_cleaning_cycle_control(self):
        with self.assertRaises(mod04.NamedFailure) as caught:
            mod04._clean_value(cyclic_list())
        self.assertIn(
            "no cleaning stands performed on the cyclic value",
            str(caught.exception))

    def test_mod13_extend_history_depth_states_consequence(self):
        segment = {"rule_set_version": "v", "run_id": "r"}
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history([deep_list(105)], segment)
        text = str(caught.exception)
        self.assertIn("past the bound of 100", text)
        self.assertIn("counted on the containers only basis", text)
        self.assertIn("no extension stands made", text)

    def test_mod13_extend_history_cycle_states_counting_and_consequence(
            self):
        segment = {"rule_set_version": "v", "run_id": "r"}
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(cyclic_list(), segment)
        text = str(caught.exception)
        self.assertIn("carries a cycle", text)
        self.assertIn("counted on the containers only basis", text)
        self.assertIn("no extension stands made", text)

    def test_mod13_extend_history_segment_cycle_ground(self):
        segment = {"rule_set_version": "v", "run_id": "r"}
        history = [dict(segment)]
        cyclic_segment = {"rule_set_version": "v", "run_id": "r"}
        cyclic_segment["self"] = cyclic_segment
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(history, cyclic_segment)
        text = str(caught.exception)
        self.assertIn("the appended segment carries a cycle", text)
        self.assertIn("no extension stands made", text)

    def test_mod13_sibling_grounds_control(self):
        segment = {"rule_set_version": "v", "run_id": "r"}
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history(42, segment)
        self.assertIn("no extension stands made", str(caught.exception))
        with self.assertRaises(
                mod13.NamedReplicationFailure) as caught:
            mod13.extend_history([], segment)
        self.assertIn("no extension stands made", str(caught.exception))


class TestR14086Mod04All(unittest.TestCase):

    def test_mod04_carries_all(self):
        self.assertTrue(hasattr(mod04, "__all__"))
        self.assertIsInstance(mod04.__all__, list)
        self.assertTrue(mod04.__all__)

    def test_all_enumerates_public_surface(self):
        public = {
            name for name in dir(mod04)
            if not name.startswith("_")
            and not isinstance(getattr(mod04, name), types.ModuleType)}
        self.assertEqual(set(mod04.__all__), public)
        self.assertEqual(len(mod04.__all__), len(set(mod04.__all__)))

    def test_every_name_resolves(self):
        for name in mod04.__all__:
            self.assertTrue(hasattr(mod04, name), name)

    def test_star_import_takes_only_enumerated_surface(self):
        namespace = {}
        exec("from crucible.mod04 import *", namespace)
        taken = {
            name for name in namespace if not name.startswith("_")}
        self.assertEqual(taken, set(mod04.__all__))


if __name__ == "__main__":
    unittest.main()

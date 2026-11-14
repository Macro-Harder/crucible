"""Fix wave 10 pins, Builder 1: MOD-01 limbs of rows R10-003,
R10-006, R10-011, R10-013, R10-014, and R10-035, read against the
governing stored text settlement in section 2 of the Round 10
register.

Row R10-003: a barred or money name split across the parts of one
container key, and a name carried by one part of a container key,
stand judged at MOD-01 as at MOD-04.
Row R10-006: a real money pair, a real money name, and the anchor
values field in bytes dress, in bytearray or memoryview dress at
the helper surface, in single part container dress, or in bytes
parts inside a container, stand judged at MOD-01 as at MOD-06.
Row R10-011: at MOD-01 the FamilyManifest field list for form 23
stands as governing evidence only. It carries no count field, and
no count field stands invented here. The signalling cure at
MOD-13 stands to another builder. These pins stand as controls.
Row R10-013: at MOD-01 a form 22 entry carrying no registry
content fails validation on the standing field list. The gate
reading cure at MOD-11 stands to another builder.
Row R10-014: the amended form 22 fields, confirmation_outcome and
gate_failure, stand in the MOD-01 field list, and the MOD-01
validation act reads the outcome with those two fields and reads
the unranked claim form in its stated form only.
Row R10-035: the condition loop of the MOD-01 validation act reads
its discriminator through the stored pairs of the record, never
through a hash or equality reading a handed key supplies.
"""
import unittest

from crucible import mod01


class StrObj:
    """A non text key object reporting a name through its own
    string reading, with identity hash and identity equality."""

    def __init__(self, reported):
        self._reported = reported

    def __str__(self):
        return self._reported


class HashLieStr(str):
    """A text key storing a name while its hash names an unrelated
    field. Its equality stands as the plain stored text equality."""

    def __hash__(self):
        return str.__hash__("an unrelated stored name")


def form4_with_control(control_values):
    instance = mod01.minimal_valid_instance("4")
    instance["control_values"] = control_values
    return instance


def registry_entry(**overrides):
    entry = mod01.minimal_valid_instance("22")
    entry["test_value"] = "0.01"
    entry["rank"] = 1
    entry["threshold"] = 0.05
    entry["outcome"] = "not reported"
    entry["confirmation_outcome"] = "not run"
    entry["gate_failure"] = "none"
    entry.update(overrides)
    return entry


class TestR10003JoinedContainerKeys(unittest.TestCase):
    def test_split_amount_and_currency_pair_is_carried(self):
        value = {("am", "ount"): 10, ("curr", "ency"): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_split_amount_with_separator_part_is_carried(self):
        value = {("amount", "_x"): 10, ("curr", "ency"): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_part_alone_amount_and_currency_is_carried(self):
        value = {("amount", "extra"): 10, ("currency", "extra"): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_split_real_money_marker_is_carried(self):
        self.assertTrue(
            mod01._carries_real_money_value({("real", "money"): 5}))
        self.assertTrue(
            mod01._carries_real_money_value({("real_", "money"): 5}))

    def test_nested_single_part_containers_carry_the_pair(self):
        value = {(("amount",),): 10, (("currency",),): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_folded_matches_on_joined_and_single_part_forms(self):
        self.assertTrue(mod01._folded_key_matches(("am", "ount"), "amount"))
        self.assertTrue(mod01._folded_key_matches(("amount",), "amount"))
        self.assertTrue(mod01._folded_key_matches(["amount"], "amount"))
        self.assertTrue(
            mod01._folded_key_matches(frozenset(("amount",)), "amount"))

    def test_form4_record_with_split_money_pair_fails(self):
        instance = form4_with_control(
            {("am", "ount"): 10, ("curr", "ency"): "USD"})
        self.assertFalse(mod01.validate_record("4", instance))

    def test_split_anchor_values_field_with_two_values_fails(self):
        instance = mod01.minimal_valid_instance("4")
        instance[("anchor_", "scenario_values")] = (
            "stated anchor value one", "stated anchor value two")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_container_key_control_clean_parts_pass(self):
        value = {("note", "part"): 10, ("unit", "part"): "USD"}
        self.assertFalse(mod01._carries_real_money_value(value))
        instance = form4_with_control(value)
        self.assertTrue(mod01.validate_record("4", instance))


class TestR10006MoneyDresses(unittest.TestCase):
    def test_bytes_pair_is_carried(self):
        value = {b"amount": 10, b"currency": "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_bytes_real_money_name_is_carried(self):
        self.assertTrue(
            mod01._carries_real_money_value({b"real_money": 5}))

    def test_single_part_container_pair_is_carried(self):
        value = {("amount",): 10, ("currency",): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_single_part_container_real_money_name_is_carried(self):
        self.assertTrue(
            mod01._carries_real_money_value({("real_money",): 5}))

    def test_bytes_parts_inside_container_pair_are_carried(self):
        value = {(b"amount",): 10, (b"currency",): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))
        split = {(b"am", b"ount"): 10, (b"curr", b"ency"): "USD"}
        self.assertTrue(mod01._carries_real_money_value(split))

    def test_memoryview_pair_is_carried(self):
        value = {memoryview(b"amount"): 10, memoryview(b"currency"): "USD"}
        self.assertTrue(mod01._carries_real_money_value(value))

    def test_bytearray_and_memoryview_helper_forms_match(self):
        self.assertTrue(
            mod01._folded_key_matches(bytearray(b"amount"), "amount"))
        self.assertTrue(
            mod01._folded_key_matches(memoryview(b"amount"), "amount"))
        self.assertTrue(
            mod01._folded_key_carries(
                bytearray(b"real_money"), "realmoney"))

    def test_form4_record_with_bytes_pair_fails(self):
        instance = form4_with_control({b"amount": 10, b"currency": "USD"})
        self.assertFalse(mod01.validate_record("4", instance))

    def test_form4_record_with_container_pair_fails(self):
        instance = form4_with_control(
            {("amount",): 10, ("currency",): "USD"})
        self.assertFalse(mod01.validate_record("4", instance))

    def test_bytes_anchor_values_field_with_two_values_fails(self):
        instance = mod01.minimal_valid_instance("4")
        instance[b"anchor_scenario_values"] = (
            "stated anchor value one", "stated anchor value two")
        self.assertFalse(mod01.validate_record("4", instance))

    def test_money_controls_stand(self):
        self.assertTrue(mod01._carries_real_money_value(
            {"amount": 10, "currency": "USD"}))
        self.assertFalse(mod01._carries_real_money_value(
            {"note": 10, "unit": "USD"}))
        self.assertFalse(mod01._carries_real_money_value(
            {StrObj("amount"): 10, StrObj("currency"): "USD"}))
        self.assertTrue(mod01._folded_key_matches(b"amount", "amount"))


class TestR10011Form23Standing(unittest.TestCase):
    def test_form23_field_list_stands_as_governing_evidence(self):
        self.assertEqual(
            mod01.form_fields("23"),
            ("family_identifier", "family_version",
             "sealed_family_record_hash"))

    def test_form23_minimal_instance_validates(self):
        self.assertTrue(mod01.validate_record(
            "23", mod01.minimal_valid_instance("23")))


class TestR10013AndR10014RegistryFields(unittest.TestCase):
    def test_entry_with_no_registry_content_fails(self):
        entry = {"phase_judgements": {"before": "judged",
                                       "after": "judged"}}
        self.assertFalse(mod01.validate_record("22", entry))

    def test_form22_field_list_carries_original_and_amended_fields(self):
        fields = mod01.form_fields("22")
        for field in (
                "claim_identifier", "claim_statement",
                "assumption_set_and_row_identifiers", "grid_points",
                "screening_run_identifiers",
                "held_out_confirmation_run_identifiers", "test_value",
                "rank", "threshold", "outcome",
                "confirmation_outcome", "gate_failure"):
            self.assertIn(field, fields)

    def test_entry_missing_amended_fields_fails(self):
        entry = registry_entry()
        del entry["confirmation_outcome"]
        del entry["gate_failure"]
        self.assertFalse(mod01.validate_record("22", entry))

    def test_failed_confirmation_with_reported_outcome_fails(self):
        entry = registry_entry(
            confirmation_outcome="failed", gate_failure="both gates",
            outcome="reported")
        self.assertFalse(mod01.validate_record("22", entry))

    def test_gate_failure_with_reported_outcome_fails(self):
        entry = registry_entry(
            confirmation_outcome="passed",
            gate_failure="procedure gate", outcome="reported")
        self.assertFalse(mod01.validate_record("22", entry))

    def test_confirmation_not_run_with_reported_outcome_fails(self):
        entry = registry_entry(
            confirmation_outcome="not run", gate_failure="none",
            outcome="reported")
        self.assertFalse(mod01.validate_record("22", entry))

    def test_passed_confirmation_and_no_gate_failure_reported_passes(self):
        entry = registry_entry(
            confirmation_outcome="passed", gate_failure="none",
            outcome="reported")
        self.assertTrue(mod01.validate_record("22", entry))

    def test_failed_confirmation_not_reported_passes(self):
        entry = registry_entry(
            confirmation_outcome="failed", gate_failure="both gates",
            outcome="not reported")
        self.assertTrue(mod01.validate_record("22", entry))

    def test_unranked_claim_with_rank_and_threshold_fails(self):
        entry = registry_entry(
            test_value="not ranked", rank=1, threshold=0.05)
        self.assertFalse(mod01.validate_record("22", entry))

    def test_unranked_rank_with_ranked_test_value_fails(self):
        entry = registry_entry(
            test_value="0.01", rank="not ranked",
            threshold="not ranked")
        self.assertFalse(mod01.validate_record("22", entry))

    def test_unranked_claim_in_stated_form_passes(self):
        entry = registry_entry(
            test_value="not ranked", rank="not ranked",
            threshold="not ranked")
        self.assertTrue(mod01.validate_record("22", entry))

    def test_ranked_claim_control_passes(self):
        self.assertTrue(mod01.validate_record("22", registry_entry()))


def condition_instance(form_id, discriminator, fields_to_remove):
    instance = mod01.minimal_valid_instance(form_id)
    plain_value = instance.pop(discriminator)
    for field in fields_to_remove:
        instance.pop(field, None)
    instance[HashLieStr(discriminator)] = True
    return instance


class TestR10035ConditionDiscriminator(unittest.TestCase):
    def test_form2_discriminator_under_hash_lie_key_fails(self):
        instance = condition_instance(
            "2", "belongs_to_decay_arm", ("decay_slice",))
        self.assertFalse(mod01.validate_record("2", instance))

    def test_form10_discriminator_under_hash_lie_key_fails(self):
        instance = condition_instance(
            "10", "lost_contact_clause_on", ("lost_contact_clock_state",))
        self.assertFalse(mod01.validate_record("10", instance))

    def test_form13_discriminator_under_hash_lie_key_fails(self):
        instance = condition_instance(
            "13", "is_anchor_scenario_run",
            ("anchor_scenario_identity", "annotation_link_identifier"))
        self.assertFalse(mod01.validate_record("13", instance))

    def test_form2_hash_lie_discriminator_with_field_present_passes(self):
        instance = mod01.minimal_valid_instance(
            "2", condition_holds={"field": "decay_slice"})
        instance.pop("belongs_to_decay_arm")
        instance[HashLieStr("belongs_to_decay_arm")] = True
        self.assertTrue(mod01.validate_record("2", instance))

    def test_plain_condition_controls_stand(self):
        holding = mod01.minimal_valid_instance(
            "2", condition_holds={"field": "decay_slice"})
        self.assertTrue(mod01.validate_record("2", holding))
        missing = mod01.minimal_valid_instance(
            "2", condition_holds={"field": "decay_slice"})
        del missing["decay_slice"]
        self.assertFalse(mod01.validate_record("2", missing))
        not_holding = mod01.minimal_valid_instance("2")
        self.assertTrue(mod01.validate_record("2", not_holding))


if __name__ == "__main__":
    unittest.main()

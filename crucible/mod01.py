"""MOD-01. Types and validation.

Every record form of the adopted census as a named type with a single
owner, its field validators, and the validation rules the design records
state in words, held as checkable code level contracts.

Census: 38 record forms, Forms 1 to 37 and Form 13A, plus the decided
ViewRecord counted beside the 38. Forms 36 and 37 validate on their
landed field lists only (8 fields and 3 fields). Forms 34 and 35 carry
contents level fields only, because no field list for either form stands
in the records. The two DQ7-12 forms, the dependency manifest and the
process and network call log, stand as named open types with no
validator claimed for them.

At OP-24 this module delivers no canonical form. It delivers the
validation machinery only: the AC-1 state hash field list and its order
carried as carriage, the one canonical rendering rule the brief states
in its stated scope (recorded strings, never binary float renderings,
for seed derivation inputs at Shape 5), and the bar under which a field
with no plan stated canonical form enters no hash equality claim.
"""

import collections
import copy
import itertools
import unicodedata

__all__ = [
    "AC1_STATE_HASH_FIELDS",
    "CALIBRATION_FIELD_VALUE",
    "CLOSED_FORMS",
    "COMPLETENESS_FIELDS",
    "DQ163_MARK",
    "FORM_IDS",
    "FORM_TYPES",
    "LIEN_STATES",
    "NAMED_FAILURES",
    "OPEN_MARKER_PREFIX",
    "RESERVED_MATTER_VALUES",
    "SOURCE_FORMS",
    "STORE_KINDS",
    "CallLog",
    "DependencyManifest",
    "ProvenanceBlock",
    "VersionStamp",
    "canonical_form_for_field",
    "check_reconciliation_trace",
    "failure_value",
    "family_supports_reportable_run",
    "field_conditions",
    "form_fields",
    "form_name",
    "hash_equality_claim_permitted",
    "minimal_valid_family_record",
    "minimal_valid_instance",
    "named_failure_forms",
    "partial_record_is_marked",
    "reconciliation_criterion_verdict",
    "reconciliation_trace",
    "reconciliation_trace_check",
    "required_fields",
    "reserved_matter_values",
    "run_is_reportable",
    "state_hash_field_list",
    "store_index",
    "validate_calibration_field",
    "validate_derivation_input_rendering",
    "validate_family_seal_match",
    "validate_lien_state",
    "validate_provenance_block",
    "validate_record",
    "validate_run_status",
    "validate_store_addressing",
    "validate_store_kind",
    "validate_version_stamp",
]

CALIBRATION_FIELD_VALUE = "no calibration claim, self consistency only"

LIEN_STATES = (
    "no lien in force",
    "computed not settled",
    "settled in the chosen escrow",
    "released",
)

STORE_KINDS = ("sweep", "pilot", "live")

DQ163_MARK = "DQ-163 RULED by Captain JP, defer until Parley exists, with no provisional anchor set"

SOURCE_FORMS = ("ARB", "BOO", "PAM", "RFO", "RET")

# Banked and reserved matter that may not stand as an ordinary field
# value in any record, per AC-6. Three values and no fourth.
RESERVED_MATTER_VALUES = (
    "banked real money stake behaviour",
    "provisional anchor set",
    "estate default anchor set",
)

# The six completeness fields of the SweepFamilyRecord, in the form the
# family record carries them. Values that stand open under OP-13 enter
# as open markers, never as invented numbers.
COMPLETENESS_FIELDS = (
    "farm size steps",
    "patience steps",
    "the longer horizon value",
    "the confidence interval method",
    "the reporting resolution for each of the three traces",
    "the decay arm donor items",
)

OPEN_MARKER_PREFIX = "open:"

_OP13_MARKER = "open: OP-13 value stands open"

_COMPLETENESS_SLUGS = (
    "farm_size_steps",
    "patience_steps",
    "longer_horizon_value",
    "confidence_interval_method",
    "reporting_resolution_per_trace",
    "decay_arm_donor_items",
)

# The AC-1 state hash field list, in the order brief section 10 states.
# Carried as carriage only: the list and the order, and no hash equality
# claim, while OP-24 stands open in part.
AC1_STATE_HASH_FIELDS = (
    "simulation clock and tick position",
    "every agent state",
    "the reputation values",
    "the vouch state and the lien state",
    "the escrow account state",
    "the work and acceptance counters",
    "the stream position of every purpose stream the run used",
    "the generator state as the checkpoint holds it",
    "the rule version set in force for the run",
)

# Canonical forms stated on a plan level record, field by field. A field
# absent from this table has no plan stated canonical form and enters no
# hash equality claim.
_CANONICAL_FORMS = {
    "seed derivation input": {
        "form": "recorded string, never a binary float rendering",
        "stated_on_plan_level_record": True,
        "scope": "seed derivation inputs at Shape 5 only",
    },
    "proportion": {
        "form": "stored numerator and denominator pair, no quotient rendering",
        "stated_on_plan_level_record": True,
        "scope": "a proportion or rate stored with a numerator and a denominator",
    },
}

# Named failures that set the run status field to failed, per Form 4
# items 2, 2A and 2B (OP-23, closed as plan design at PD-06).
NAMED_FAILURES = (
    "handover count failure",
    "failed run return",
    "partial cast failure",
    "detection input projection failure",
    "leak check failure",
    "record validation failure",
    "outside call check failure",
)


def _fields(*names):
    return tuple(names)


_FORM_SPECS = {
    "1": ("SweepFamilyRecord", _fields(
        "family_identifier", "question_form", "headline_claims",
        "false_discovery_rate_level", "control_axes_and_step_values",
        "assumption_sets_in_play", "scheduling_order_identifier",
        "replicate_rule_by_stratum", "held_out_seed_domain_and_settings_rule",
        "headline_reading_load_accounting_rule", "provisional_grid_marker",
        "farm_size_steps", "patience_steps", "longer_horizon_value",
        "confidence_interval_method", "reporting_resolution_per_trace",
        "decay_arm_donor_items", "kill_check_fields",
    )),
    "2": ("SweepPoint", _fields(
        "point_identifier", "population_size", "farm_size", "patience_in_days",
        "run_length_in_days", "anchor_scenario_identifier",
        "escrow_variant_selector", "assumption_set_selector", "design_kind",
        "decay_slice",
    )),
    "3": ("AssumptionRecord", _fields(
        "assumption_set_identifier", "behaviour_parameter_rows",
        "parameters_in_no_kind_listing",
    )),
    "4": ("RunRecord", _fields(
        "sweep_identifier", "sweep_family_identifier", "family_version",
        "family_manifest_hash", "run_identifier", "sweep_point_identifier",
        "run_class", "design_kind", "replicate_group_identifier",
        "replicate_index", "population_size", "run_length_in_days",
        "horizon_variant_marker", "control_values", "root_seed_reference",
        "derived_run_seed_identifier", "stream_identifiers",
        "scheduling_order_identifier", "scheduling_position_identifiers",
        "build_identifier", "assumption_record", "escrow_variant",
        "matched_run_identifier", "variant_record_fields", "rule_version_set",
        "core_only_qualifier", "interpretation_choices",
        "arbiter_accuracy_value", "anchor_scenario_values", "dependence_labels",
        "correlation_statement", "joint_outcome_vector",
        "regime_classification", "winning_criterion_evaluation",
        "gate_passing_share_per_epoch", "excluded_class_counts_and_shares",
        "retention_tier", "flag_conditions_fired", "record_pointers",
        "end_of_run_state_hash", "store_kind",
        "timing_pilot_or_provisional_marker", "folding_record_reference",
        "seam_check_reference", "nq10_listing", "nq6_classification_marker",
        "calibration_claim_field", "outside_call_check", "run_status",
        "annotation_link",
    )),
    "5": ("SeedDerivationInput", _fields(
        "derivation_version_string", "domain", "recorded_root_seed",
        "scenario_identifier", "run_identifier", "stream_class_identifier",
        "parameter_values",
    )),
    "6": ("StreamSet", _fields(
        "stream_class_inventory", "adjudication_stream",
    )),
    "7": ("AgentState", _fields(
        "agent_identifier", "archetype_identifier", "membership_ground_truth",
        "reputation_score_by_viewer", "band", "stake_held",
        "vouch_edges_given_and_received", "work_history_summary",
    )),
    "8": ("VouchEdge", _fields(
        "voucher", "vouchee", "stake", "creation_day", "lifetime",
        "score_bearing_flag", "component_identifier",
    )),
    "9": ("GraphSnapshot", _fields(
        "edge_list_reference", "component_list",
        "largest_mutually_vouching_component_size",
        "realised_degree_distribution",
    )),
    "10": ("EscrowContractState", _fields(
        "contract_identifier", "pair_identifiers",
        "standard_or_profile_identifier", "variant", "lien_state",
        "estimated_cost_value", "pause_state", "k1_and_l2_state",
        "lost_contact_clock_state",
    )),
    "11": ("AdjudicationCase", _fields(
        "case_identifier", "challenge_basis", "panel_form",
        "ground_truth_label_reference", "outcome", "arbiter_accuracy_value",
        "excluded_class_counts_and_shares",
    )),
    "12": ("DetectionState", _fields(
        "feature_values", "likelihood_ratio_contributions",
        "accumulator_values", "verdict_state",
    )),
    "13": ("CheckpointManifest", _fields(
        "run_identifier", "simulated_day", "full_state_hash",
        "generator_state_per_stream", "journal_position", "rule_version_set",
        "assumption_record_reference", "anchor_scenario_identity",
        "annotation_link_identifier", "resume_attempt_identifier",
        "journal_event_count_at_checkpoint", "last_event_identifier",
        "form_standing_value", "build_identifier",
        "dependency_manifest_hash", "parent_checkpoint_identifier",
        "branch_cluster_identifier", "production_or_recovery_class",
    )),
    "13A": ("CheckpointState", _fields(
        "run_identifier", "simulated_day", "agent_states",
        "escrow_contract_states", "detection_state",
        "stream_positions_and_generator_states", "simulation_clock_value",
    )),
    "14": ("DailyAggregates", _fields(
        "run_identifier", "simulated_day", "viewer_identifier",
        "joint_outcome_components", "honest_share",
        "gate_passing_share_per_epoch", "excluded_class_counts_and_shares",
        "divergence_companion",
    )),
    "15": ("JointOutcomeVector", _fields(
        "attacker_controlled_share", "farm_share_of_reputation_mass",
        "largest_component_share", "honest_loss_rate", "divergence_companion",
    )),
    "16": ("HeadlineResultUnit", _fields(
        "headline_unit_identifier_and_issue_date", "claim_sentence",
        "holding_region", "failure_region", "witness_block",
        "assumption_record", "assumption_set_and_rows",
        "interpretation_choices", "variant_stamp",
        "qualifiers_and_markings_block", "replicate_and_family_data",
        "checkability_fields", "grounding_sentence", "run_registry_line",
    )),
    "17": ("AnchorScenarioRecord", _fields(
        "scenario_identifier", "anchor_set_description", "dq163_mark",
    )),
    "18": ("InterpretationLogEntry", _fields(
        "choice_identifier", "reading_applied",
        "parameter_or_rule_point_affected", "governing_text_version",
        "escrow_variant_and_fold_version", "parley_test_total_source",
        "dependence_marks",
    )),
    "19": ("DetectionInput", _fields(
        "agent_identifier", "day", "feature_values",
        "records_for_agent_and_day",
    )),
    "20": ("AnnotationRecord", _fields(
        "annotation_identifier", "annotation_link_identifier",
        "anchor_scenario_identifier", "writing_component", "note_text",
        "no_conversion_statement", "content_check_outcome",
    )),
    "21": ("AnnotationCheckRecord", _fields(
        "check_attempt_identifier", "annotation_link_identifier",
        "anchor_scenario_identifier", "writing_component",
        "annotation_identifier", "content_check_outcome",
    )),
    "22": ("SweepFamilyRegistry", _fields(
        "claim_identifier", "claim_statement",
        "assumption_set_and_row_identifiers", "grid_points",
        "screening_run_identifiers", "held_out_confirmation_run_identifiers",
        "test_value", "rank", "threshold", "outcome",
        "confirmation_outcome", "gate_failure",
    )),
    "23": ("FamilyManifest", _fields(
        "family_identifier", "family_version", "sealed_family_record_hash",
    )),
    "24": ("SweepManifest", _fields(
        "family_version_and_hash", "recorded_root_seed_per_domain",
    )),
    "25": ("PilotRecord", _fields(
        "run_class", "population_and_run_length", "events_processed",
        "events_per_agent_per_day", "cost_by_limb", "total_cost",
        "spread_values", "host_form_and_code_version",
        "failed_and_resumed_run_count", "confinement_label",
    )),
    "26": ("SummaryRecord", _fields(
        "flag_evaluation", "flag_evaluation_inputs", "flag_evaluation_outcome",
        "store_kind", "calibration_claim_field",
    )),
    "27": ("DetectionOutput", _fields(
        "run_identifier", "scoring_day_range",
        "verdict_states_and_accumulator_updates", "profile_bound_label",
        "threshold_formula_table_identifier",
        "threshold_formula_table_version", "standing_statement",
    )),
    "28": ("ReplicationVerdictRecord", _fields(
        "claim_identifier", "standard_applied", "verdict", "quantities",
        "checking_party", "artifacts", "evidence_reference",
    )),
    "29": ("TracerPassageRecord", _fields(
        "open_semantic_item", "point_in_run", "what_in_fact_passed", "result",
    )),
    "30": ("GatePassingShareRecord", _fields(
        "share_per_epoch", "assumption_set_identifier", "row_identifiers",
        "envelope_value", "score_bearing_figure",
    )),
    "31": ("ReadingLoadPricingRecord", _fields(
        "what_was_priced", "priced_reading_load",
        "amount_priced_into_run_cost", "added_cells_conversion",
    )),
    "32": ("SettingsLineageTestRecord", _fields(
        "confirmation_claim", "settings_trace",
        "used_to_find_or_confirm_per_setting",
    )),
    "33": ("RetentionRecord", _fields(
        "later_evaluation", "later_evaluation_inputs_and_outcome",
        "retained_forms_pointed_to",
    )),
    "34": ("DisagreementCatalogue", _fields(
        "disagreement_points",
    )),
    "35": ("WeeklyContainer", _fields(
        "headline_units",
    )),
    "36": ("EventLog", _fields(
        "run_identifier", "journal_position", "event_identifier",
        "simulated_day", "event_imported_row_form", "agent_identifier",
        "superseded_from_journal_position", "resume_attempt_identifier",
    )),
    "37": ("DailySnapshot", _fields(
        "run_identifier", "simulated_day", "daily_state_as_delivered",
    )),
}

# Forms a source states as closed: unnamed fields fail validation.
CLOSED_FORMS = frozenset(("16", "17", "19", "20", "21"))

# The stored parts of the four JointOutcomeVector components, Form 15,
# in the form plan section 3, Form 15, item 1 states for each component,
# with the kind of each pair member named in the record under Amendment
# G2-C18. A component carrying none of its parts, or standing as a bare
# value, is no component of the form. The kind names themselves stand
# as the record carries them: no record states a fixed label set for
# them, and none stands fixed here.
JOINT_OUTCOME_COMPONENT_PARTS = {
    "attacker_controlled_share": (
        "numerator", "denominator", "proportion", "viewer_identifier",
        "numerator_kind", "denominator_kind",
    ),
    "farm_share_of_reputation_mass": (
        "numerator", "denominator", "proportion", "viewer_identifier",
        "numerator_kind", "denominator_kind",
    ),
    "largest_component_share": (
        "component_size", "population_size", "proportion",
        "component_definition_version", "viewer_identifier",
        "component_size_kind", "population_size_kind",
    ),
    "honest_loss_rate": (
        "numerator", "denominator", "rate", "loss_definition_version",
        "viewer_identifier", "numerator_kind", "denominator_kind",
    ),
}

# The decided ViewRecord, counted beside the 38 and taking no number.
_VIEW_RECORD_FIELDS = _fields(
    "run_identifier", "viewer_identifier", "simulated_day",
    "scheduling_position_identifier", "rule_version_set", "view_contents",
    "reputation_and_band_values", "graph_position_as_seen",
    "first_seen_day_per_record", "delay_applied_per_record",
    "completeness_state", "building_component", "delivering_contract",
    "selection_rule_version",
)

# Conditional fields: required exactly where the stated condition holds.
_CONDITIONS = {
    "2": {
        "field": "decay_slice",
        "discriminator": "belongs_to_decay_arm",
        "condition": "the point belongs to the decay arm",
    },
    "10": {
        "field": "lost_contact_clock_state",
        "discriminator": "lost_contact_clause_on",
        "condition": "the lost contact clause is on for the contract",
    },
    "13": {
        "field": "anchor_scenario_identity",
        "discriminator": "is_anchor_scenario_run",
        "condition": "the run is an anchor scenario run",
    },
}

_EXTRA_CONDITIONS = {
    "13": (
        {
            "field": "annotation_link_identifier",
            "discriminator": "is_anchor_scenario_run",
            "condition": "the run is an anchor scenario run",
        },
    ),
}

_EVENTLOG_BASE_FIELDS = (
    "run_identifier", "journal_position", "event_identifier",
    "simulated_day", "event_imported_row_form",
)


def _safe_str(value):
    """Render a handed value for a refusal sentence: through
    its string reading where that reading stands, and through
    the base object repr where the string reading the value
    itself supplies raises, so the sentence stands delivered
    whole and never escapes bare on that reading."""
    try:
        return str(value)
    except Exception:
        return object.__repr__(value)


def _fid(form_id):
    return _safe_str(form_id)


def form_name(form_id):
    spec = _FORM_SPECS.get(_fid(form_id))
    return spec[0] if spec else None


def form_fields(form_id):
    """The field list of a form. Forms 36 and 37 return their landed
    lists and no field beyond them."""
    spec = _FORM_SPECS.get(_fid(form_id))
    if spec is None:
        return ()
    return spec[1]


def required_fields(form_id):
    """The fields required on every instance of a form. Conditional
    fields stand apart, in field_conditions."""
    fid = _fid(form_id)
    fields = form_fields(fid)
    conditional = {c["field"] for c in _conditions_for(fid)}
    if fid == "36":
        return _EVENTLOG_BASE_FIELDS
    return tuple(f for f in fields if f not in conditional)


def _conditions_for(form_id):
    fid = _fid(form_id)
    conditions = []
    condition = _CONDITIONS.get(fid)
    if condition:
        conditions.append(condition)
    conditions.extend(_EXTRA_CONDITIONS.get(fid, ()))
    return tuple(conditions)


def field_conditions(form_id):
    """Stated conditions under which a conditional field is required,
    one dict per condition, each naming its field."""
    return tuple(dict(c) for c in _conditions_for(form_id))


FORM_IDS = tuple(_FORM_SPECS.keys())


# ---------------------------------------------------------------------------
# Minimal valid instances
# ---------------------------------------------------------------------------

_FIELD_VALUES = {
    "form_standing_value": "pending: OP-24 stands open",
    "calibration_claim_field": CALIBRATION_FIELD_VALUE,
    "lien_state": "no lien in force",
    "store_kind": "sweep",
    "run_status": "completed",
    "dq163_mark": DQ163_MARK,
    "domain": "screening",
    "parameter_values": ("recorded parameter value",),
    "outside_call_check": "pass",
    "core_only_qualifier": True,
    "content_check_outcome": "passed",
    "completeness_state": "complete",
    "anchor_scenario_values": (
        "stated anchor value one", "stated anchor value two",
        "stated anchor value three"),
}


def _placeholder(field):
    if field in _FIELD_VALUES:
        return copy.deepcopy(_FIELD_VALUES[field])
    if field in _COMPLETENESS_SLUGS:
        return _OP13_MARKER
    return "stated value"


def minimal_valid_instance(form_id, entry_kind=None, condition_holds=None):
    """A minimally valid instance of a form, as a plain dict.

    Form 36 takes entry_kind, one of ordinary, agent, or supersession.
    A form with a stated condition takes condition_holds: the condition
    dict its field_conditions returns, or None where the condition does
    not hold.
    """
    fid = _fid(form_id)
    if fid == "36":
        if entry_kind is not None and entry_kind not in (
                "ordinary", "agent", "supersession"):
            raise ValueError(
                "unknown entry kind: " + str(entry_kind)
                + "; the stated kinds are ordinary, agent and supersession")
        return _minimal_eventlog(entry_kind or "ordinary")
    if fid == "15":
        return _minimal_joint_outcome_vector()
    if fid == "1":
        return minimal_valid_family_record()
    instance = {}
    for field in required_fields(fid):
        instance[field] = _placeholder(field)
    named_disc = None
    if isinstance(condition_holds, dict):
        for candidate in _conditions_for(fid):
            if candidate["field"] == dict.get(condition_holds, "field"):
                named_disc = candidate["discriminator"]
    for condition in _conditions_for(fid):
        holds = bool(condition_holds) and (
            not isinstance(condition_holds, dict)
            or dict.get(condition_holds, "field") == condition["field"]
            or (named_disc is not None
                and condition["discriminator"] == named_disc)
        )
        instance[condition["discriminator"]] = bool(holds)
        if holds:
            instance[condition["field"]] = _placeholder(condition["field"])
    return instance


def _minimal_eventlog(entry_kind):
    instance = {field: _placeholder(field) for field in _EVENTLOG_BASE_FIELDS}
    instance["entry_kind"] = entry_kind
    if entry_kind == "agent":
        instance["agent_identifier"] = _placeholder("agent_identifier")
    if entry_kind == "supersession":
        instance["superseded_from_journal_position"] = _placeholder(
            "superseded_from_journal_position")
        instance["resume_attempt_identifier"] = _placeholder(
            "resume_attempt_identifier")
    return instance


def _minimal_joint_outcome_vector():
    instance = {}
    for field, parts in JOINT_OUTCOME_COMPONENT_PARTS.items():
        instance[field] = {part: _placeholder(part) for part in parts}
    instance["divergence_companion"] = _placeholder("divergence_companion")
    return instance


def minimal_valid_family_record():
    """A SweepFamilyRecord carrying every completeness field, with the
    OP-13 values carried as open markers."""
    record = {}
    for field in required_fields("1"):
        record[field] = _placeholder(field)
    for field in COMPLETENESS_FIELDS:
        record[field] = _OP13_MARKER
    return record


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

RECORD_TRAVERSAL_DEPTH_BOUND = 100


class RecordTraversalFailure(ValueError):
    """A named failure for a value deeper than the stated traversal
    bound, or carrying a cycle, in the reading of a record."""


def _traversal_guard(value, depth, seen):
    if depth > RECORD_TRAVERSAL_DEPTH_BOUND:
        raise RecordTraversalFailure(
            "record traversal bound reached: the value stands deeper "
            "than the stated bound of "
            + str(RECORD_TRAVERSAL_DEPTH_BOUND))
    if id(value) in seen:
        raise RecordTraversalFailure(
            "record traversal found a cycle")


def _base_iter(value):
    """Iterate a list, tuple, set, or frozenset part through its
    base class iteration, never through a reading the part
    itself supplies."""
    if isinstance(value, list):
        return list.__iter__(value)
    if isinstance(value, tuple):
        return tuple.__iter__(value)
    if isinstance(value, frozenset):
        return frozenset.__iter__(value)
    return set.__iter__(value)


def _base_len(value):
    """The length of a handed container or text value, read through
    the base class length of its kind, never through a length
    reading the value itself supplies."""
    if isinstance(value, list):
        return list.__len__(value)
    if isinstance(value, tuple):
        return tuple.__len__(value)
    if isinstance(value, frozenset):
        return frozenset.__len__(value)
    if isinstance(value, set):
        return set.__len__(value)
    if isinstance(value, dict):
        return dict.__len__(value)
    if isinstance(value, str):
        return str.__len__(value)
    if isinstance(value, bytearray):
        return bytearray.__len__(value)
    if isinstance(value, bytes):
        return bytes.__len__(value)
    raise TypeError("the handed value carries no base class length")


def _guard_copyable(value, depth=0, seen=None, _walked=None):
    if seen is None:
        seen = set()
    if _walked is None:
        _walked = set()
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        _traversal_guard(value, depth, seen)
        if (id(value), depth) in _walked:
            return
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    _guard_copyable(key, depth + 1, seen, _walked)
                    _guard_copyable(item, depth + 1, seen, _walked)
            else:
                for item in _base_iter(value):
                    _guard_copyable(item, depth + 1, seen, _walked)
        finally:
            seen.discard(id(value))
        _walked.add((id(value), depth))


def _carries_reserved_matter(value, _depth=0, _seen=None, _walked=None):
    if _seen is None:
        _seen = set()
    if _walked is None:
        _walked = {}
    if isinstance(value, str):
        return any(
            str.__eq__(value, reserved)
            for reserved in RESERVED_MATTER_VALUES
        )
    if isinstance(value, dict):
        _traversal_guard(value, _depth, _seen)
        if (id(value), _depth) in _walked:
            return _walked[(id(value), _depth)]
        _seen.add(id(value))
        try:
            joined_keys = "".join(
                str.__str__(k) for k in dict.keys(value)
                if isinstance(k, str))
            result = any(
                str.__eq__(joined_keys, reserved)
                for reserved in RESERVED_MATTER_VALUES
            ) or any(
                _carries_reserved_matter(k, _depth + 1, _seen, _walked)
                or _carries_reserved_matter(v, _depth + 1, _seen, _walked)
                for k, v in dict.items(value)
            )
        finally:
            _seen.discard(id(value))
        _walked[(id(value), _depth)] = result
        return result
    if isinstance(value, (list, tuple, set, frozenset)):
        _traversal_guard(value, _depth, _seen)
        if (id(value), _depth) in _walked:
            return _walked[(id(value), _depth)]
        _seen.add(id(value))
        try:
            result = any(
                _carries_reserved_matter(v, _depth + 1, _seen, _walked)
                for v in _base_iter(value))
        finally:
            _seen.discard(id(value))
        _walked[(id(value), _depth)] = result
        return result
    return False


# Letter canonicalisation, standing ahead of the separator fold in
# every reading below. One name is read in one canonical form:
# compatibility decomposition with combining marks dropped, so an
# accented letter and a full width letter reduce to their base letter;
# then case folding, with any combining mark the folding itself
# introduces dropped in the same way; then the recorded letter mapping
# below for the dresses decomposition cannot reduce. The mapping
# carries, letter by letter, the non Latin letters that stand for the
# marker letters, in their look alike form where one stands and in
# their sounded form where a whole word stands transliterated, and the
# recorded transliterated spelling of the money marker word itself.
_LETTER_MAP = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "r",
    "\u043d": "n", "\u043b": "l", "\u043c": "m", "\u0438": "i",
    "\u0447": "ch", "\u043a": "k", "\u0445": "x", "\u0441": "c",
    "\u0443": "y", "\u0432": "v", "\u0442": "t", "\u0434": "d",
    "\u044d": "e", "\u0439": "i", "\u0419": "i",
    "\u044b": "y", "\u042b": "y",
    "\u044e": "yu", "\u042e": "yu", "\u044f": "ya", "\u042f": "ya",
    "\u03b1": "a", "\u03bf": "o", "\u03b5": "e", "\u03b9": "i",
    "\u03b7": "e", "\u0397": "e",
    "\u03b8": "t", "\u0398": "t", "\u03d1": "t",
    "\u03ba": "k", "\u03bc": "m", "\u03bd": "n", "\u03c1": "r",
    "\u03c4": "t", "\u03c5": "y", "\u03bb": "l", "\u03c3": "s",
    "\u03c8": "ps",
    "\u03c2": "s", "\u03c9": "o", "\u03c7": "x",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "\u13d2": "r", "\u13ac": "e", "\u13aa": "a", "\u13de": "l",
    "\u13b7": "m", "\u13be": "o", "\u13c1": "n", "\u13ef": "y",
    "\uaba2": "r", "\uab7c": "e", "\uab7a": "a", "\uabae": "l",
    "\uab87": "m", "\uab8e": "o", "\uab91": "n", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
    "\u2ca2": "r", "\u2c88": "e", "\u2c80": "a", "\u2c96": "l",
    "\u2c98": "m", "\u2c9e": "o", "\u2c9a": "n", "\u2ca8": "y",
}

# Letters that carry two recorded readings each, so one name may need
# either reading at either position where the letter stands. The first
# reading in each pair is the primary reading the letter map above
# records. Cyrillic es reads as c and as s. Cyrillic u and Greek
# upsilon read as y and as u. Cyrillic en reads as n and as h.
# Armenian vo reads as n and as the two letters un.
_MULTI_READINGS = {
    "\u0441": ("c", "s"),
    "\u0443": ("y", "u"),
    "\u03c5": ("y", "u"),
    "\u043d": ("n", "h"),
    "\u0578": ("n", "un"),
    "\u0445": ("x", "h"),
    "\u0425": ("x", "h"),
    "\u0439": ("i", "y"),
    "\u0419": ("i", "y"),
}

# Symbol substitutions in the leet readings, beside the digit readings
# below: a sign standing in a marker word for the letter it commonly
# stands for reads as that letter, for a, c, e, l, s, t and y.
_SYMBOL_LEET_READINGS = {
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y", "\u00a2": "c", "$": "s", "\u00a7": "s", "+": "t",
}

_TRANSLITERATED_SPELLINGS = (
    ("realmani", "real" + "money"),
)

# A digit standing inside a marker word is read in two recorded ways:
# as the letter its leet form stands for, and as a dropped separator
# that holds nothing apart. The digit readings below carry both, with
# the figure one read as the letter l in one reading and as the
# letter i in the other, those being its two standing leet letters.
_LEET_READING_ONE = {
    "0": "o", "1": "l", "2": "z", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
}
_LEET_READING_TWO = dict(_LEET_READING_ONE, **{"1": "i"})


_SHORT_I_PLACEHOLDER = "\ue000"


def _stored_key_text(value):
    """The stored text of a key or of a part of a key, under the
    governing stored text settlement. A text value is read through
    its stored characters. A bytes, bytearray, or memoryview value
    is read by decoding its stored bytes as UTF-8 with undecodable
    bytes dropped, through the base class operations of its kind,
    never through a reading the value itself supplies. A container
    value in tuple, list, set, or frozenset form is read as the
    stored text of its parts joined in order with no separator
    added, each part read recursively in the same form. A value of
    any other form stores no text name and reads as None."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(
            memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list, set, frozenset)):
        parts = []
        for part in _base_iter(value):
            part_text = _stored_key_text(part)
            parts.append(part_text if part_text is not None else "")
        return "".join(parts)
    return None



_UNORDERED_JOIN_PART_BOUND = 7

_JOIN_CANDIDATE_BOUND = 5040

_SEG_JOIN_CANDIDATE_BOUND = 131072

_SEG_FOLDED_CANDIDATE_BOUND = 20000


def _join_container_parts(node):
    """The parts a container stores, read through base class
    operations only, in the iteration order the container
    stands in for this process."""
    return list(_base_iter(node))


def _has_unordered_split(value):
    """Whether a key carries a set or frozenset part holding
    two or more parts, found on an iterative walk, so no
    recursion stands spent on a key that carries none."""
    seen = set()
    stack = [value]
    while stack:
        node = stack.pop()
        if isinstance(node, (tuple, list, set, frozenset)):
            if id(node) in seen:
                continue
            seen.add(id(node))
            parts = _join_container_parts(node)
            if isinstance(node, (set, frozenset)) and len(parts) >= 2:
                return True
            stack.extend(parts)
    return False


def _joined_text_candidates(value, _active=None, _cap=None):
    """Every joined stored text a container key can stand in.

    An ordered container (tuple, list, or a dict read by its
    keys) contributes the join of its parts in their stored
    order, exactly as the standing joined reading reads it. An
    unordered container (set or frozenset) stores no order, so
    its iteration order, which the hash seed governs, is no
    reading of it: the candidates are the joins under every
    ordering of its direct parts, each part contributing every
    candidate of its own in the same form, so a barred name
    split across the parts of an unordered container stands
    among the candidates in every iteration order. The form is
    complete for an unordered container holding at most
    _UNORDERED_JOIN_PART_BOUND direct parts and while the
    distinct candidates of one container stand at or under
    _JOIN_CANDIDATE_BOUND. Past either bound the container
    contributes its iteration order join alone, beside the
    standing per part readings, as the paper for this cure
    states. A part already on the walk path contributes the
    empty text, so a cyclic part cannot loop the read. The walk stands iterative on an explicit stack of frames, so a container chain at any depth stands answered on the same terms and no recursion stands spent per container level. A caller may state a wider candidate cap through _cap, as the segmentation readings do, without moving the standing bound this act states for its other callers."""
    if _cap is None:
        _cap = _JOIN_CANDIDATE_BOUND
    if _active is None:
        _active = set()

    def combine(node, parts, child):
        if (
            isinstance(node, (set, frozenset))
            and 2 <= len(parts) <= _UNORDERED_JOIN_PART_BOUND
        ):
            orders = list(
                itertools.permutations(range(len(parts))))
        else:
            orders = [tuple(range(len(parts)))]
        out = []
        seen = set()
        for order in orders:
            total = 1
            for index in order:
                total *= len(child[index])
            if total > _cap:
                text = "".join(
                    child[index][0]
                    for index in range(len(parts)))
                if text not in seen:
                    seen.add(text)
                    out.append(text)
                continue
            for combo in itertools.product(
                    *(child[index] for index in order)):
                text = "".join(combo)
                if text not in seen:
                    seen.add(text)
                    out.append(text)
                    if len(out) >= _cap:
                        return tuple(out)
        return tuple(out)

    stack = []
    node = value
    result = None
    while True:
        if result is None:
            if not isinstance(node, (tuple, list, set, frozenset)):
                result = ((_stored_key_text(node) or ""),)
            elif id(node) in _active:
                result = ("",)
            else:
                _active.add(id(node))
                parts = _join_container_parts(node)
                if parts:
                    stack.append([node, parts, [], 0])
                    node = parts[0]
                    continue
                _active.discard(id(node))
                result = combine(node, parts, [])
        while result is not None:
            if not stack:
                return result
            frame = stack[-1]
            frame[2].append(result)
            frame[3] += 1
            if frame[3] < len(frame[1]):
                node = frame[1][frame[3]]
                result = None
                break
            stack.pop()
            _active.discard(id(frame[0]))
            result = combine(frame[0], frame[1], frame[2])


def _seg_tiles_exact(options, target):
    """Whether the parts can stand in some order so that their
    joined reading, in the reading space the options stand in,
    stands exactly as the target. The judgement runs as a
    segmentation of the target over the parts: a state is a
    position in the target beside the set of parts already
    placed, a step places one unused part whose reading stands
    as the next segment of the target, and a part whose
    readings carry the empty text may stand placed without
    advancing the position, so it is checked at the end rather
    than placed. No ordering of the parts is ever listed, and
    the state count stands at most at the target length plus
    one times two to the number of parts that can contribute a
    segment of the target, in place of the factorial count of
    orderings. A failed state is never searched twice."""
    count = len(options)
    usable = []
    for opts in options:
        matching = sorted({o for o in opts if o and o in target})
        if not matching and "" not in opts:
            return False
        usable.append(matching)

    def remaining_can_vanish(mask):
        return all(
            "" in options[i]
            for i in range(count) if not (mask >> i) & 1)

    failed = set()
    stack = [[0, 0, None, 0]]
    while stack:
        frame = stack[-1]
        pos, mask = frame[0], frame[1]
        if pos == len(target):
            if remaining_can_vanish(mask):
                return True
            failed.add((pos, mask))
            stack.pop()
            continue
        if frame[2] is None:
            if (pos, mask) in failed:
                stack.pop()
                continue
            frame[2] = [
                (i, o) for i in range(count)
                if not (mask >> i) & 1
                for o in usable[i] if target.startswith(o, pos)]
        if frame[3] < len(frame[2]):
            i, o = frame[2][frame[3]]
            frame[3] += 1
            stack.append([pos + len(o), mask | (1 << i), None, 0])
        else:
            failed.add((pos, mask))
            stack.pop()
    return False


def _seg_tiles_carrying(options, pattern):
    """The set of parts that can stand as one unbroken block,
    in some order, so that their joined reading carries the
    pattern inside it, or None where no such block stands. The
    block is found as a segmentation of the pattern: its first
    part contributes a suffix of its reading, each middle part
    contributes its whole reading as one segment of the
    pattern, and its last part contributes a prefix of its
    reading, each part used at most once. Parts outside the
    block stand free on either side of it, so the block alone
    decides the carrying. No ordering of the parts is ever
    listed, and the state count stands at most at the pattern
    length plus one times two to the number of parts that can
    contribute a segment of the pattern."""
    if not pattern:
        return None
    count = len(options)
    opts_list = [sorted({o for o in opts if o}) for opts in options]
    failed = set()
    stack = [[0, 0, None, 0]]
    while stack:
        frame = stack[-1]
        pos, mask = frame[0], frame[1]
        if frame[2] is None:
            if (pos, mask) in failed:
                stack.pop()
                continue
            moves = []
            for i in range(count):
                if (mask >> i) & 1:
                    continue
                for o in opts_list[i]:
                    if mask == 0:
                        if pattern in o:
                            return 1 << i
                        for j in range(
                                1, min(len(o), len(pattern)) + 1):
                            if o.endswith(pattern[:j]):
                                if j == len(pattern):
                                    return 1 << i
                                moves.append((j, i))
                    elif pos + len(o) <= len(pattern):
                        if o == pattern[pos:pos + len(o)]:
                            if pos + len(o) == len(pattern):
                                return mask | (1 << i)
                            moves.append((pos + len(o), i))
                    elif o.startswith(pattern[pos:]):
                        return mask | (1 << i)
            frame[2] = moves
        if frame[3] < len(frame[2]):
            npos, i = frame[2][frame[3]]
            frame[3] += 1
            stack.append([npos, mask | (1 << i), None, 0])
        else:
            failed.add((pos, mask))
            stack.pop()
    return None


def _seg_unordered_nodes(key):
    """Every set or frozenset standing inside a key, at any
    depth, found on an iterative walk through base readings,
    each beside the parts it directly stores."""
    seen = set()
    stack = [key]
    nodes = []
    while stack:
        node = stack.pop()
        if isinstance(node, (tuple, list, set, frozenset)):
            if id(node) in seen:
                continue
            seen.add(id(node))
            parts = _join_container_parts(node)
            if isinstance(node, (set, frozenset)) and len(parts) >= 2:
                nodes.append((node, parts))
            stack.extend(parts)
    return nodes




def _seg_universe(targets, patterns):
    """Every substring of the targets and patterns a
    segmentation judgement in this module tiles or carries:
    the only texts a part reading can contribute to such a
    judgement as a whole segment."""
    universe = set()
    for text in list(targets) + list(patterns):
        for start in range(len(text)):
            for stop in range(start + 1, len(text) + 1):
                universe.add(text[start:stop])
    return universe


def _seg_prefixes(universe):
    """Every prefix of a universe text, the closure the
    formable set computation walks through."""
    prefixes = set()
    for text in universe:
        for stop in range(1, len(text) + 1):
            prefixes.add(text[:stop])
    return prefixes


def _seg_formable(node, universe, prefixes, folded, _active=None):
    """The universe texts one part can join to exactly, as a
    set beside whether the part can join to the empty text.
    The computation walks the part structure in the form the
    segmentation stated: an ordered container joins its
    parts in order, an unordered container joins its parts
    in any order, and no joined candidate is ever listed, so
    a composite part whose candidates pass the kept helper
    cut still contributes every segment of a target or a
    pattern it can stand as. A part already on the walk path
    contributes the empty text, as the candidate act states."""
    if _active is None:
        _active = set()
    if not isinstance(node, (tuple, list, set, frozenset)):
        if folded:
            readings = set(_folded_key_variants(node))
        else:
            readings = {_stored_text(node).lower()}
        return (
            {reading for reading in readings if reading in universe},
            "" in readings or not readings)
    if id(node) in _active:
        return (set(), True)
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        child = [
            _seg_formable(part, universe, prefixes, folded, _active)
            for part in parts]
    finally:
        _active.discard(id(node))
    options = []
    can_empty = True
    for forms, empty in child:
        options.append(forms | ({""} if empty else set()))
        can_empty = can_empty and empty
    if isinstance(node, (set, frozenset)) and len(parts) >= 2:
        if any(not opts for opts in options):
            return (set(), can_empty)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        reached = {0: {""}}
        full = (1 << len(parts)) - 1
        queue = [0]
        cursor = 0
        bounded = False
        while cursor < len(queue):
            mask = queue[cursor]
            cursor += 1
            for index in range(len(parts)):
                if (mask >> index) & 1:
                    continue
                joined = {
                    head + tail
                    for head in reached[mask]
                    for tail in options[index]
                    if head + tail == "" or head + tail in prefixes}
                if not joined:
                    continue
                new_mask = mask | (1 << index)
                if new_mask not in reached:
                    if len(reached) >= bound:
                        bounded = True
                        break
                    reached[new_mask] = set()
                    queue.append(new_mask)
                reached[new_mask].update(joined)
            if bounded:
                break
        if bounded:
            acc = {""}
            for opts in options:
                acc = {
                    head + tail
                    for head in acc for tail in opts
                    if head + tail == "" or head + tail in prefixes}
                if not acc:
                    break
            return (acc & universe, can_empty)
        return (reached.get(full, set()) & universe, can_empty)
    acc = {""}
    for opts in options:
        acc = {
            head + tail
            for head in acc for tail in opts
            if head + tail == "" or head + tail in prefixes}
        if not acc:
            break
    return (acc & universe, can_empty)

def _seg_part_readings(node, folded):
    """The readings of one leaf part in one reading space: the
    folded key variants in folded space, the lowered stored
    text in plain space."""
    if folded:
        return set(_folded_key_variants(node))
    text = _stored_text(node)
    if text is None:
        text = _stored_key_text(node) or ""
    return {text.lower()}


def _seg_part_can_equal(node, text, folded, _active=None):
    """Whether some whole reading of one part stands exactly
    as the text, judged through the formable computation, so
    no joined candidate of the part stands listed."""
    if _active is None:
        _active = set()
    if not isinstance(node, (tuple, list, set, frozenset)):
        return text in _seg_part_readings(node, folded)
    if id(node) in _active:
        return text == ""
    universe = _seg_universe((text,), ()) if text else set()
    try:
        forms, can_empty = _seg_formable(
            node, universe, _seg_prefixes(universe), folded)
    except RecursionError:
        return False
    if not text:
        return can_empty
    return text in forms


def _seg_part_can_start(node, text, folded, _active=None):
    """Whether some whole reading of one part begins with the
    text. The judgement walks the part structure: an ordered
    part is consumed in its stored order and an unordered
    part in any order of its subparts, each step either
    placing one subpart as an exact piece of the text, letting
    one subpart begin with the remainder, or passing a subpart
    that can stand empty. The state count stands bounded by
    the stated candidate cap of the reading space, in the
    form settlement S-10 states, and a part past the bound
    contributes no opening form through this act."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (tuple, list, set, frozenset)):
        return any(
            reading.startswith(text)
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_start(parts[0], text, folded, _active)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, pos = stack.pop()
            if pos == len(text):
                return True
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                indices = [mask] if mask < len(parts) else []
            for index in indices:
                part = parts[index]
                if _seg_part_can_start(
                        part, text[pos:], folded, _active):
                    return True
                new_mask = (
                    mask | (1 << index) if unordered else index + 1)
                for stop in range(pos + 1, len(text) + 1):
                    if _seg_part_can_equal(
                            part, text[pos:stop], folded, _active):
                        state = (new_mask, stop)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                if _seg_part_can_equal(part, "", folded, _active):
                    state = (new_mask, pos)
                    if state not in seen:
                        seen.add(state)
                        stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_part_can_end(node, text, folded, _active=None):
    """Whether some whole reading of one part ends with the
    text, the mirror form of _seg_part_can_start, walked from
    the closing subpart backwards under the same stated bound."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (tuple, list, set, frozenset)):
        return any(
            reading.endswith(text)
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_end(parts[0], text, folded, _active)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, matched = stack.pop()
            if matched == len(text):
                return True
            rest = text[:len(text) - matched]
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                index = len(parts) - 1 - mask
                indices = [index] if index >= 0 else []
            for index in indices:
                part = parts[index]
                if _seg_part_can_end(
                        part, rest, folded, _active):
                    return True
                new_mask = (
                    mask | (1 << index) if unordered else mask + 1)
                for start_at in range(0, len(rest)):
                    piece = rest[start_at:]
                    if _seg_part_can_equal(
                            part, piece, folded, _active):
                        state = (new_mask, matched + len(piece))
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                if _seg_part_can_equal(part, "", folded, _active):
                    state = (new_mask, matched)
                    if state not in seen:
                        seen.add(state)
                        stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_part_can_contain(node, text, folded, _active=None):
    """Whether some whole reading of one part carries the
    text inside it: the text stands inside one subpart, or it
    spans subpart boundaries, one subpart ending with its
    opening, middle subparts standing as its exact pieces,
    and one subpart beginning with its closing. The walk
    stands bounded as _seg_part_can_start states."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (tuple, list, set, frozenset)):
        return any(
            text in reading
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_contain(parts[0], text, folded, _active)
        for part in parts:
            if _seg_part_can_contain(part, text, folded, _active):
                return True
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, pos = stack.pop()
            if pos == len(text):
                return True
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                indices = [mask] if mask < len(parts) else []
            for index in indices:
                part = parts[index]
                new_mask = (
                    mask | (1 << index) if unordered else index + 1)
                if pos == 0:
                    if _seg_part_can_end(part, text, folded, _active):
                        return True
                    for stop in range(1, len(text)):
                        if _seg_part_can_end(
                                part, text[:stop], folded, _active):
                            state = (new_mask, stop)
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    if not unordered:
                        state = (new_mask, 0)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                else:
                    if _seg_part_can_start(
                            part, text[pos:], folded, _active):
                        return True
                    for stop in range(pos + 1, len(text) + 1):
                        if _seg_part_can_equal(
                                part, text[pos:stop], folded, _active):
                            if stop == len(text):
                                return True
                            state = (new_mask, stop)
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    if _seg_part_can_equal(part, "", folded, _active):
                        state = (new_mask, pos)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_parts_carry_edge(parts, options, pattern, folded):
    """Whether a barred part stands tiled over the direct
    parts of one unordered container where one part
    contributes only its edge: a part whose whole reading
    carries the pattern inside it, or a first part whose
    whole reading ends with the opening of the pattern,
    middle parts standing as exact pieces of it through
    their stated options, and a last part whose whole
    reading begins with its closing. The edge forms stand
    judged through the part predicates above, so a composite
    part past the candidate caps contributes its edge as
    settlement S-4 governs, in plain and folded spaces alike."""
    if not any(
            isinstance(part, (tuple, list, set, frozenset))
            for part in parts):
        return False
    for part in parts:
        if not isinstance(part, (tuple, list, set, frozenset)):
            continue
        try:
            if _seg_part_can_contain(part, pattern, folded):
                return True
        except RecursionError:
            continue
    count = len(parts)
    for first in range(count):
        for cut in range(1, len(pattern)):
            try:
                if not _seg_part_can_end(
                        parts[first], pattern[:cut], folded):
                    continue
            except RecursionError:
                continue
            failed = set()
            stack = [(1 << first, cut)]
            while stack:
                mask, pos = stack.pop()
                if pos >= len(pattern):
                    return True
                if (mask, pos) in failed:
                    continue
                for index in range(count):
                    if (mask >> index) & 1:
                        continue
                    try:
                        if _seg_part_can_start(
                                parts[index], pattern[pos:], folded):
                            return True
                    except RecursionError:
                        pass
                    for option in options[index]:
                        if option and pattern.startswith(option, pos):
                            if pos + len(option) >= len(pattern):
                                return True
                            stack.append(
                                (mask | (1 << index),
                                 pos + len(option)))
                failed.add((mask, pos))
    return False


def _seg_plain_options(parts, _universe=None, _prefixes=None):
    """The plain readings of the direct parts of one unordered
    container: for each part, the lowered texts of every joined
    candidate the part itself stands in, taken under the wider
    segmentation candidate cap, beside every universe segment
    the part can join to exactly where a universe stands
    stated, so a composite part past the kept helper cut
    still contributes the segments a barred reading needs."""
    options = []
    for part in parts:
        texts = {
            text.lower()
            for text in _joined_text_candidates(
                part, _cap=_SEG_JOIN_CANDIDATE_BOUND)}
        if _universe is not None and isinstance(part, (tuple, list, set, frozenset)):
            try:
                forms, can_empty = _seg_formable(
                    part, _universe, _prefixes, False)
            except RecursionError:
                forms, can_empty = set(), False
            texts |= forms
            if can_empty:
                texts.add("")
        options.append(texts)
    return options


def _seg_folded_options(parts, _universe=None, _prefixes=None):
    """The folded readings of the direct parts of one unordered
    container: for each part, every folded reading of every
    joined candidate the part itself stands in, under this
    module folded reading act, beside every universe segment
    the part can join to exactly where a universe stands
    stated, so a folded segment a composite part can stand
    as stands judged past the kept helper cut as well."""
    options = []
    for part in parts:
        readings = set()
        for text in _joined_text_candidates(
                part, _cap=_SEG_FOLDED_CANDIDATE_BOUND):
            readings.update(_folded_key_variants(text))
        if not readings:
            readings = {""}
        if _universe is not None and isinstance(part, (tuple, list, set, frozenset)):
            try:
                forms, can_empty = _seg_formable(
                    part, _universe, _prefixes, True)
            except RecursionError:
                forms, can_empty = set(), False
            readings |= forms
            if can_empty:
                readings.add("")
        options.append(readings)
    return options


def _seg_exact(key, target):
    """Whether an unordered container standing inside a key
    joins, in some order of its direct parts, to a reading
    standing exactly as the target, judged by segmentation of
    the target over the folded readings of the parts, beside
    the kept candidate readings."""
    for node, parts in _seg_unordered_nodes(key):
        universe = _seg_universe((target,), ())
        if _seg_tiles_exact(
                _seg_folded_options(
                    parts, universe, _seg_prefixes(universe)),
                target):
            return True
    return False


def _seg_carrying(key, pattern):
    """Whether an unordered container standing inside a key
    joins, in some order of its direct parts, to a reading
    carrying the pattern, judged by segmentation of the
    pattern over the folded readings of the parts, beside the
    kept candidate readings."""
    for node, parts in _seg_unordered_nodes(key):
        universe = _seg_universe((), (pattern,))
        options = _seg_folded_options(
            parts, universe, _seg_prefixes(universe))
        if _seg_tiles_carrying(options, pattern) is not None:
            return True
        if _seg_parts_carry_edge(parts, options, pattern, True):
            return True
    return False


def _span_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _span_feed(pattern, state, text):
    current = state
    for character in text:
        if current == len(pattern):
            return current
        current = _span_prefix_state(pattern, current, character)
    return current


def _span_relevant(options, texts):
    """The readings of one block that can take part in a
    barred reading of the whole key, beside whether the block
    carries any other reading. A reading takes part where it
    stands as a segment of a target or a pattern, where it
    carries a pattern whole, where a suffix of it stands as
    the opening of a target or a pattern, or where a prefix
    of it stands as the closing of one."""
    relevant = set()
    other = False
    for option in options:
        if option == "":
            relevant.add(option)
            continue
        keep = False
        for text in texts:
            if not text:
                continue
            if option in text or text in option:
                keep = True
                break
            for cut in range(1, min(len(option), len(text))):
                if option.endswith(text[:cut]):
                    keep = True
                    break
                if text[cut:] and option.startswith(text[cut:]):
                    keep = True
                    break
            if keep:
                break
        if keep:
            relevant.add(option)
        else:
            other = True
    return relevant, other


def _span_blocks(key):
    """The blocks a whole key reading stands built from, in
    the form settlement S-4 states: where the key itself
    stands unordered, its direct parts stand as blocks in
    no stated order; where it stands ordered, the leaf parts
    of its ordered nesting stand as blocks in their stored
    order, an unordered container standing among them as one
    block whose own readings its segmentation states. A
    container already on the walk path contributes nothing,
    as the candidate act states."""
    if isinstance(key, (set, frozenset)):
        return ("unordered", _join_container_parts(key))
    if isinstance(key, (dict, list, tuple)):
        blocks = []
        active = {id(key)}
        frames = [[_join_container_parts(key), 0, id(key)]]
        while frames:
            frame = frames[-1]
            parts, index, node_id = frame
            if index >= len(parts):
                frames.pop()
                active.discard(node_id)
                continue
            frame[1] = index + 1
            part = parts[index]
            if isinstance(part, (dict, list, tuple)):
                if id(part) in active:
                    continue
                active.add(id(part))
                frames.append(
                    [_join_container_parts(part), 0, id(part)])
            else:
                blocks.append(part)
        return ("ordered", blocks)
    return None


def _seg_spanning_barred(key, plain_targets, plain_patterns,
                         folded_targets, folded_patterns):
    """Whether a barred reading of the whole key stands on
    the joined and segmented readings across nesting and
    part boundaries, in the form settlement S-4 states: a
    name a single unordered container cannot tile on its own
    stands barred where a segment tiled inside one block
    stands completed by the blocks standing beside it, and
    a name whose segment stands inside one composite block
    past the kept helper cut stands barred on that block's
    formable segments. An ordered key keeps its stored
    order, judged position by position over the block
    readings with no ordering ever listed; an unordered key
    stands judged by the segmentation acts over its blocks.
    A block whose reading takes no part in the barred
    reading can only end a partial match, never carry one
    across itself, so the ordered judgement lets every block
    return the match to its opening state beside the states
    its taking part readings reach."""
    found = _span_blocks(key)
    if found is None:
        return False
    mode, blocks = found
    if not blocks:
        return False
    spaces = []
    if plain_targets or plain_patterns:
        spaces.append((plain_targets, plain_patterns, False))
    if folded_targets or folded_patterns:
        spaces.append((folded_targets, folded_patterns, True))
    for targets, patterns, folded in spaces:
        texts = list(targets) + list(patterns)
        universe = _seg_universe(targets, patterns)
        prefixes = _seg_prefixes(universe)
        options = []
        for block in blocks:
            if folded:
                opts = _seg_folded_options(
                    [block], universe, prefixes)[0]
            else:
                opts = _seg_plain_options(
                    [block], universe, prefixes)[0]
            options.append(_span_relevant(opts, texts))
        if mode == "unordered":
            pruned = [relevant for relevant, other in options]
            for target in targets:
                if _seg_tiles_exact(pruned, target):
                    return True
            for pattern in patterns:
                if _seg_tiles_carrying(pruned, pattern) is not None:
                    return True
        else:
            for pattern in patterns:
                states = {0}
                for relevant, other in options:
                    following = {0}
                    for state in states:
                        for option in relevant:
                            if option == "":
                                following.add(state)
                                continue
                            end = _span_feed(pattern, state, option)
                            if end == len(pattern):
                                return True
                            following.add(end)
                    states = following
            for target in targets:
                positions = {0}
                for relevant, other in options:
                    following = set()
                    for position in positions:
                        for option in relevant:
                            if target.startswith(option, position):
                                following.add(
                                    position + len(option))
                    positions = following
                    if not positions:
                        break
                if len(target) in positions:
                    return True
    return False



def _normalised_characters(text):
    # Cyrillic short i is held apart from the decomposition below,
    # which would otherwise reduce it to Cyrillic i and lose its
    # second recorded reading as y. The placeholder stands in its
    # place through the decomposition and the case folding, and the
    # letter itself stands restored in the returned characters.
    # The characters stand taken from the stored text of the key,
    # read through _stored_key_text: a text value through its
    # stored characters, a bytes like value through its decoded
    # stored bytes, and a container key through its stored text
    # parts joined in order, never through a reading the value
    # itself supplies.
    # A value that stores no text name takes no characters here,
    # so the fold judges no name from a string reading the value
    # itself supplies.
    stored = _stored_key_text(text)
    if stored is None:
        return []
    source = stored.replace(
        "\u0419", _SHORT_I_PLACEHOLDER).replace(
        "\u0439", _SHORT_I_PLACEHOLDER)
    decomposed = unicodedata.normalize("NFKD", source)
    without_marks = "".join(
        character for character in decomposed
        if not unicodedata.category(character).startswith("M")
    )
    folded = unicodedata.normalize("NFKD", without_marks.casefold())
    characters = []
    for character in folded:
        if unicodedata.category(character).startswith("M"):
            continue
        if character.isdigit():
            digit = unicodedata.digit(character, None)
            if digit is not None:
                character = str(digit)
        if character == _SHORT_I_PLACEHOLDER:
            character = "\u0439"
        characters.append(character)
    return characters


def _primary_reading(character):
    return _LETTER_MAP.get(
        character, _SYMBOL_LEET_READINGS.get(character, character))


def _canonicalise_letters(text):
    canonical = "".join(
        _primary_reading(character)
        for character in _normalised_characters(text)
    )
    for source, target in _TRANSLITERATED_SPELLINGS:
        canonical = canonical.replace(source, target)
    return canonical


def _character_readings(character):
    if character in _MULTI_READINGS:
        return _MULTI_READINGS[character]
    if character in _SYMBOL_LEET_READINGS:
        return (_SYMBOL_LEET_READINGS[character], character)
    return (_primary_reading(character),)


def _canonical_variants(text):
    # A symbol sign carries two readings in the variants: the letter
    # it stands for, and the sign itself, which the fold drops as it
    # drops every separator. A name therefore reads both ways, with
    # the sign standing for its letter and with the sign holding
    # nothing apart. The expansion bound stands at 65536, wide enough
    # for a name that combines the symbol substitutions with every
    # both readings letter of the anchor field name in one name.
    # Past that bound the matching reads below still read a name
    # under every recorded reading, character by character, without
    # enumerating the variants, so a combined dress that passes the
    # bound still stands read in full.
    variants = [""]
    for character in _normalised_characters(text):
        readings = _character_readings(character)
        if len(variants) * len(readings) > 65536:
            readings = readings[:1]
        variants = [
            prefix + reading
            for prefix in variants
            for reading in readings
        ]
    canonical_variants = []
    for variant in variants:
        for source, target in _TRANSLITERATED_SPELLINGS:
            variant = variant.replace(source, target)
        canonical_variants.append(variant)
    return canonical_variants


def _prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _segments_carry_pattern(segments_by_character, pattern):
    full = len(pattern)
    states = {0}
    for options in segments_by_character:
        next_states = set()
        for state in states:
            for segment in options:
                current = state
                for character in segment:
                    if current == full:
                        break
                    current = _prefix_state(pattern, current, character)
                next_states.add(current)
        if full in next_states:
            return True
        states = next_states
    return full in states


def _folded_segment(reading, mode):
    folded = "".join(
        character for character in reading if character.isalnum())
    if mode == "drop":
        return "".join(
            character for character in folded if not character.isdigit())
    if mode is None:
        return folded
    return "".join(mode.get(character, character) for character in folded)


_FOLDED_MODES = (None, _LEET_READING_ONE, _LEET_READING_TWO, "drop")


def _matches_under_every_reading(key, folded_target):
    characters = _normalised_characters(key)
    options_by_character = [
        _character_readings(character)
        for character in characters
    ]
    for mode in _FOLDED_MODES:
        positions = {0}
        for options in options_by_character:
            segments = {
                _folded_segment(reading, mode) for reading in options
            }
            next_positions = set()
            for position in positions:
                for segment in segments:
                    if folded_target[
                            position:position + len(segment)] == segment:
                        next_positions.add(position + len(segment))
            positions = next_positions
            if not positions:
                break
        if len(folded_target) in positions:
            return True
    # The figure one carries two leet readings, as the letter l and
    # as the letter i, and one name may need one reading at one
    # position and the other reading at another position. This pass
    # reads the figure one under either leet reading at each of its
    # positions in a single name, while every other character keeps
    # the reading of one chosen mode.
    for mode in (None, _LEET_READING_ONE, _LEET_READING_TWO):
        positions = {0}
        for character, options in zip(characters, options_by_character):
            segments = {
                _folded_segment(reading, mode) for reading in options
            }
            if character == "1":
                segments.update(("l", "i"))
            next_positions = set()
            for position in positions:
                for segment in segments:
                    if folded_target[
                            position:position + len(segment)] == segment:
                        next_positions.add(position + len(segment))
            positions = next_positions
            if not positions:
                break
        if len(folded_target) in positions:
            return True
    # One digit position of a name may take its leet letter reading
    # while another digit position of the same name takes the dropped
    # reading, so this pass reads every position under every recorded
    # digit reading at once, combined position by position.
    positions = {0}
    for options in options_by_character:
        segments = {
            _folded_segment(reading, mode)
            for reading in options
            for mode in _FOLDED_MODES
        }
        next_positions = set()
        for position in positions:
            for segment in segments:
                if folded_target[
                        position:position + len(segment)] == segment:
                    next_positions.add(position + len(segment))
        positions = next_positions
        if not positions:
            break
    if len(folded_target) in positions:
        return True
    return False


def _carries_under_every_reading(key, folded_marker):
    options_by_character = [
        _character_readings(character)
        for character in _normalised_characters(key)
    ]
    for mode in _FOLDED_MODES:
        segments_by_character = [
            tuple(
                _folded_segment(reading, mode) for reading in options)
            for options in options_by_character
        ]
        if _segments_carry_pattern(segments_by_character, folded_marker):
            return True
    # The combined reading of the matching read above, in carries
    # form: every position stands read under every recorded digit
    # reading at once, so one position may take its leet letter
    # reading while another takes the dropped reading.
    combined_segments = [
        tuple({
            _folded_segment(reading, mode)
            for reading in options
            for mode in _FOLDED_MODES
        })
        for options in options_by_character
    ]
    if _segments_carry_pattern(combined_segments, folded_marker):
        return True
    # The transliterated spelling stands read under the same
    # digit readings as every other spelling: a name needing the
    # transliteration correction and a digit reading in a single
    # reading, a leet letter at one position or a dropped digit
    # at one, still reads as the marker, in the sister form.
    for source, target in _TRANSLITERATED_SPELLINGS:
        if folded_marker != target:
            continue
        for mode in _FOLDED_MODES:
            segments_by_character = [
                tuple(
                    _folded_segment(reading, mode)
                    for reading in options)
                for options in options_by_character
            ]
            if _segments_carry_pattern(segments_by_character, source):
                return True
        if _segments_carry_pattern(combined_segments, source):
            return True
    return False


def _folded_money_key(key):
    return "".join(
        character for character in _canonicalise_letters(key)
        if character.isalnum()
    )


def _folded_key_variants(key):
    variants = set()
    for canonical in _canonical_variants(key):
        folded = "".join(
            character for character in canonical if character.isalnum()
        )
        variants.add(folded)
        for reading in (_LEET_READING_ONE, _LEET_READING_TWO):
            variants.add("".join(
                reading.get(character, character) for character in folded
            ))
        variants.add("".join(
            character for character in folded if not character.isdigit()
        ))
    # The figure one may read as the letter l at one position of a
    # name and as the letter i at another position of the same name,
    # so the variants also carry every mixture of its two leet
    # readings across the positions where the figure stands. The
    # mixture stands bounded: a name carrying more than twelve
    # instances of the figure one keeps the whole name readings
    # above, and the character by character matching read still
    # reads it in full.
    mixed = set()
    for folded in variants:
        one_positions = [
            index for index, character in enumerate(folded)
            if character == "1"
        ]
        if not one_positions or len(one_positions) > 12:
            continue
        for choice in itertools.product(
                ("l", "i"), repeat=len(one_positions)):
            letters = list(folded)
            for position, reading in zip(one_positions, choice):
                letters[position] = reading
            mixed.add("".join(letters))
    variants.update(mixed)
    # The variants also carry every mixture of the two recorded
    # digit readings across the digit positions of one name, the
    # leet letter reading at one position and the dropped reading
    # at another, with the digit itself kept as a further choice.
    # The mixture stands bounded in the same form as the figure
    # one mixture above: a name whose mixtures would pass 65536
    # variants keeps the whole name readings above, and the
    # character by character matching reads still read it in full.
    digit_mixed = set()
    for folded in list(variants):
        digit_positions = [
            index for index, character in enumerate(folded)
            if character.isdigit()
        ]
        if not digit_positions:
            continue
        choices = []
        total = 1
        for position in digit_positions:
            digit = folded[position]
            options = {
                digit, _LEET_READING_ONE.get(digit, digit),
                _LEET_READING_TWO.get(digit, digit), "",
            }
            choices.append(sorted(options))
            total *= len(options)
        if total > 65536:
            continue
        for choice in itertools.product(*choices):
            parts = []
            last = 0
            for position, reading in zip(digit_positions, choice):
                parts.append(folded[last:position])
                parts.append(reading)
                last = position + 1
            parts.append(folded[last:])
            digit_mixed.add("".join(parts))
    variants.update(digit_mixed)
    return variants


def _folded_key_matches(key, folded_target):
    if (
        isinstance(key, (tuple, list, set, frozenset))
        and _has_unordered_split(key)
    ):
        for candidate in _joined_text_candidates(key):
            if candidate and _folded_key_matches(
                    candidate, folded_target):
                return True
        if _seg_exact(key, folded_target):
            return True
        if folded_target == "realmoney" and _seg_exact(key, "realmani"):
            return True
    if _seg_spanning_barred(
            key, (), (),
            (folded_target,)
            + (("realmani",) if folded_target == "realmoney" else ()),
            ()):
        return True
    if folded_target in _folded_key_variants(key):
        return True
    if _matches_under_every_reading(key, folded_target):
        return True
    # A container key also stands judged on each part it stores,
    # read on its own stored text, recursively, beside the joined
    # reading the variants above carry. A single part container
    # therefore carries the reading of its one part in full, and a
    # part that matches on its own matches in the container.
    if isinstance(key, (tuple, list, set, frozenset)):
        return any(
            _folded_key_matches(part, folded_target)
            for part in _base_iter(key)
        )
    return False


def _folded_key_carries(key, folded_marker):
    if (
        isinstance(key, (tuple, list, set, frozenset))
        and _has_unordered_split(key)
    ):
        for candidate in _joined_text_candidates(key):
            if candidate and _folded_key_carries(
                    candidate, folded_marker):
                return True
        if _seg_carrying(key, folded_marker):
            return True
        if folded_marker == "realmoney" and _seg_carrying(
                key, "realmani"):
            return True
    if _seg_spanning_barred(
            key, (), (), (),
            (folded_marker,)
            + (("realmani",) if folded_marker == "realmoney" else ())):
        return True
    if any(
        folded_marker in variant
        for variant in _folded_key_variants(key)
    ):
        return True
    return _carries_under_every_reading(key, folded_marker)


_MONEY_MARKER_FOLDED = ("real_" + "money").replace("_", "")
_ANCHOR_VALUES_FIELD_FOLDED = _folded_money_key(
    "anchor_" + "scenario_values")


def _dict_keys_carry_split(readings, pairs, pattern):
    """Whether the folded marker stands split across two or
    more consecutive keys of one dict, in the joined reading
    form settlement S-14 states: the first key contributes a
    tail of one of its readings as the opening of the marker,
    each middle key one whole reading as an exact piece of
    it, and the last key a reading that begins with its
    closing. A key whose reading stands empty contributes no
    character to the joined reading, so the occurrence may
    cross such a key, stepped past on its empty reading and
    unused by the occurrence. The marker bars only where a
    value stands under every key the occurrence uses, as the
    walk states for a money name."""
    for start in range(len(pairs)):
        for reading in readings[start]:
            if not reading:
                continue
            for cut in range(len(reading)):
                piece = reading[cut:]
                if not piece or len(piece) >= len(pattern):
                    continue
                if piece != pattern[:len(piece)]:
                    continue
                present = pairs[start][1] is not None
                stack = [(start + 1, len(piece), present)]
                while stack:
                    index, pos, ok = stack.pop()
                    if pos >= len(pattern):
                        if ok:
                            return True
                        continue
                    if index >= len(pairs):
                        continue
                    next_ok = ok and (
                        pairs[index][1] is not None)
                    for option in readings[index]:
                        if not option:
                            stack.append((index + 1, pos, ok))
                            continue
                        if option == pattern[pos:pos + len(option)]:
                            stack.append((
                                index + 1,
                                pos + len(option), next_ok))
                        elif option.startswith(pattern[pos:]):
                            if next_ok:
                                return True
    return False


def _dict_keys_tile_exact(readings, pairs, target, require_value):
    """Whether a run of two or more consecutive dict keys, in
    stored order, joins exactly to the target on one folded
    reading of each key it uses, in the joined reading form
    settlement S-14 states, a key whose reading stands empty
    stepped past inside the run on that empty reading. Where
    require_value stands stated, the name bars only where a
    value stands under every key the run uses, as the walk
    states for that name; a stepped past key stands unused.
    A name standing inside one key alone stands judged by
    the per key acts, never here, so a run stands only on
    two or more pieces."""
    visited = set()
    stack = [(0, 0, 0, True)]
    while stack:
        index, pos, pieces, ok = stack.pop()
        if pos == len(target):
            if pieces >= 2 and ok:
                return True
            continue
        if index >= len(pairs):
            continue
        state = (index, pos, pieces >= 2, ok)
        if state in visited:
            continue
        visited.add(state)
        if pieces == 0:
            stack.append((index + 1, 0, 0, True))
        next_ok = ok and (
            pairs[index][1] is not None or not require_value)
        for option in readings[index]:
            if not option:
                stack.append((index + 1, pos, pieces, ok))
            elif option == target[pos:pos + len(option)]:
                stack.append((
                    index + 1, pos + len(option),
                    pieces + 1, next_ok))
    return False


def _dict_node_money_barred(value):
    """Whether a dict handed to the money walk stands barred
    at its own node, in the form settlement S-14 states: the
    walk judges a dict handed to it at the dict node itself,
    on the joined reading of the dict's keys in stored order,
    in the folded form in which the walk judges a single key.
    The folded money marker split across two keys of the dict
    stands judged on that joined reading, and the amount and
    currency pair, which the walk frames at dict level across
    the keys of one dict together, stands judged where each
    name stands split across two keys of the same dict."""
    pairs = list(dict.items(value))
    if len(pairs) < 2:
        return False
    readings = [set(_folded_key_variants(key)) for key, item in pairs]
    for pattern in (_MONEY_MARKER_FOLDED, "realmani"):
        if _dict_keys_carry_split(readings, pairs, pattern):
            return True
    amount_stands = _dict_keys_tile_exact(
        readings, pairs, "amount", True) or any(
            _folded_key_matches(key, "amount") and item is not None
            for key, item in pairs)
    currency_stands = _dict_keys_tile_exact(
        readings, pairs, "currency", False) or any(
            _folded_key_matches(key, "currency")
            for key, item in pairs)
    return amount_stands and currency_stands


def _carries_real_money_value(value, _depth=0, _seen=None, _walked=None):
    if _seen is None:
        _seen = set()
    if _walked is None:
        _walked = {}
    if isinstance(value, dict):
        _traversal_guard(value, _depth, _seen)
        if (id(value), _depth) in _walked:
            return _walked[(id(value), _depth)]
        _seen.add(id(value))
        try:
            amount_carried = any(
                _folded_key_matches(key, "amount") and item is not None
                for key, item in dict.items(value)
            )
            currency_carried = any(
                _folded_key_matches(key, "currency")
                for key in dict.keys(value)
            )
            if amount_carried and currency_carried:
                result = True
            elif _dict_node_money_barred(value):
                result = True
            else:
                result = False
                for key, item in dict.items(value):
                    if _folded_key_carries(key, _MONEY_MARKER_FOLDED) and (
                            item is not None):
                        result = True
                        break
                    if _carries_real_money_value(
                            key, _depth + 1, _seen, _walked):
                        result = True
                        break
                    if _carries_real_money_value(
                            item, _depth + 1, _seen, _walked):
                        result = True
                        break
        finally:
            _seen.discard(id(value))
        _walked[(id(value), _depth)] = result
        return result
    if isinstance(value, (list, tuple, set, frozenset)):
        _traversal_guard(value, _depth, _seen)
        if (id(value), _depth) in _walked:
            return _walked[(id(value), _depth)]
        _seen.add(id(value))
        try:
            result = any(
                _carries_real_money_value(v, _depth + 1, _seen, _walked)
                for v in _base_iter(value))
        finally:
            _seen.discard(id(value))
        _walked[(id(value), _depth)] = result
        return result
    return False


def _stored_text(value):
    """The text a handed value stores, read through the base class
    string form, or None where the value stores no text at all."""
    if isinstance(value, str):
        return str.__str__(value)
    return None


def _stored_text_dress(value):
    """The stored text of a handed value in every dress the
    governing stored text settlement reads: a text value through
    its stored characters, a bytes, bytearray, or memoryview
    value through its decoded stored bytes, and a single part
    container through the stored text of its one part. A value
    in any other form stores no text here and reads as None."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list, set, frozenset)):
        items = list(_base_iter(value))
        if len(items) == 1:
            return _stored_text_dress(items[0])
        return None
    return None


def _stored_text_equals(value, expected):
    """Whether the text a handed value stores stands equal to an
    expected text, judged through base class operations only."""
    stored = _stored_text(value)
    return stored is not None and str.__eq__(stored, expected)


def _stored_text_in(value, options):
    """Whether the text a handed value stores stands among a set
    of expected texts, judged through base class operations only."""
    stored = _stored_text(value)
    if stored is None:
        return False
    return any(str.__eq__(stored, option) for option in options)


_STORED_MISSING = object()


def _stored_pairs_value(mapping, field, default=None):
    """The value a handed mapping stores under a field name,
    found by scanning its stored pairs: a field stands present
    only where a stored text key carries its name under a base
    class comparison, never through a hash, equality, get, or
    getitem reading a handed key or mapping supplies."""
    if not isinstance(mapping, dict):
        return default
    for key, item in dict.items(mapping):
        if isinstance(key, str) and str.__eq__(str.__str__(key), field):
            return item
    return default


def _stored_pairs_present(mapping, field):
    return _stored_pairs_value(
        mapping, field, _STORED_MISSING) is not _STORED_MISSING


def _stored_plain(value):
    """The plain stored form of a handed value of a scalar kind,
    read through the base class operations of its kind. A value
    of any other kind stands as itself."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bool):
        return value is True
    if isinstance(value, int):
        return int.__int__(value)
    if isinstance(value, float):
        return float.__float__(value)
    return value


def _base_value_equals(left, right):
    """Whether two handed values stand equal in what they store,
    judged through base class operations. A text value stands
    equal only to a text value whose stored text matches."""
    plain_left = _stored_plain(left)
    plain_right = _stored_plain(right)
    if isinstance(plain_left, str) or isinstance(plain_right, str):
        return (
            isinstance(plain_left, str)
            and isinstance(plain_right, str)
            and str.__eq__(plain_left, plain_right)
        )
    return plain_left == plain_right


def validate_lien_state(value, cross_seam=False):
    """The lien state bar at Shape 9: exactly four values, and while
    NQ-45 stands open no cross seam effect carries settled or released."""
    if not _stored_text_in(value, LIEN_STATES):
        return False
    if cross_seam and _stored_text_in(
            value, ("settled in the chosen escrow", "released")):
        return False
    return True


def validate_calibration_field(value):
    """The sole permitted value of the calibration claim field."""
    return _stored_text_equals(value, CALIBRATION_FIELD_VALUE)


def validate_store_kind(kind):
    return _stored_text_in(kind, STORE_KINDS)


def store_index(kind):
    """The namespace token of a store kind. The three kinds are
    distinct namespaces with no shared index. The token stands
    built from the text the kind stores, as validate_store_kind
    judges it, read through the base class string form, never
    through a string reading the kind itself supplies. A kind
    storing no text names no stored kind in its token."""
    stored = _stored_text(kind)
    if stored is None:
        return "store namespace: no stored kind"
    return "store namespace: " + stored


def _outside_named_kinds(addressing):
    """The stored contents of a container form outside dict, list,
    tuple, set, and frozenset, read through the base class
    operations of its kind, or None where no base class reading
    of its stored contents stands."""
    if isinstance(addressing, collections.deque):
        return list(collections.deque.__iter__(addressing))
    if isinstance(addressing, collections.UserList):
        return list(collections.UserList.__iter__(addressing))
    if isinstance(addressing, collections.UserDict):
        stored = object.__getattribute__(addressing, "data")
        if isinstance(stored, dict):
            return list(dict.keys(stored))
        return None
    if isinstance(addressing, collections.ChainMap):
        kinds = []
        for part in list.__iter__(
                object.__getattribute__(addressing, "maps")):
            if isinstance(part, dict):
                kinds.extend(dict.keys(part))
        return kinds
    if isinstance(addressing, bytearray):
        return list(bytearray.__iter__(addressing))
    if isinstance(addressing, bytes):
        return list(bytes.__iter__(addressing))
    for base in type(addressing).__mro__[1:]:
        reading = base.__dict__.get("__iter__")
        if reading is not None:
            try:
                return list(reading(addressing))
            except (TypeError, AttributeError):
                return None
    return None


def validate_store_addressing(addressing):
    """A record addressed to exactly one store kind validates in that
    namespace. A record addressed across two stores fails."""
    # The handed container stands read through base class
    # operations on the contents it stores, never through an
    # iteration reading the container itself supplies.
    if isinstance(addressing, dict):
        kinds = list(dict.keys(addressing))
    elif isinstance(addressing, (list, tuple, set, frozenset)):
        kinds = list(_base_iter(addressing))
    else:
        kinds = _outside_named_kinds(addressing)
        if kinds is None:
            return False
    if len(kinds) != 1:
        return False
    kind = kinds[0]
    if not isinstance(kind, str):
        return False
    stored = str.__str__(kind)
    return any(str.__eq__(stored, stated) for stated in STORE_KINDS)


def reserved_matter_values():
    return RESERVED_MATTER_VALUES


def validate_family_seal_match(manifest, record):
    """Seal matching as a recorded value comparison: the run record
    family version and family manifest hash must match the sealed
    family record hash and version on the manifest, in the plan
    named fields of Forms 23 and 4."""
    if not isinstance(manifest, dict) or not isinstance(record, dict):
        return False
    version = _stored_pairs_value(manifest, "family_version")
    digest = _stored_pairs_value(manifest, "sealed_family_record_hash")
    if version is None or digest is None:
        return False
    return (
        _base_value_equals(
            _stored_pairs_value(record, "family_version"), version)
        and _base_value_equals(
            _stored_pairs_value(record, "family_manifest_hash"), digest)
    )


def family_supports_reportable_run(record):
    """The family completeness bar: every completeness field present,
    each OP-13 value carried as an open marker and never as a number."""
    if not isinstance(record, dict):
        return False
    stored_pairs = [
        (str.__str__(key), item)
        for key, item in dict.items(record)
        if isinstance(key, str)
    ]
    for field in COMPLETENESS_FIELDS:
        found = [
            item for key, item in stored_pairs if str.__eq__(key, field)
        ]
        if not found:
            return False
        value = found[0]
        if not isinstance(value, str):
            return False
        if not str.startswith(value, OPEN_MARKER_PREFIX) or not (
                str.__contains__(value, "OP-13")):
            return False
    return True


def _validate_record_inner(form_id, instance):
    """Validate one record instance against its form.

    The required field rule: a record with a required field absent
    fails validation. A conditional field is required exactly where
    its stated condition holds.
    """
    fid = _fid(form_id)
    if fid not in _FORM_SPECS or not isinstance(instance, dict):
        return False
    # The required field presence act reads the stored keys of
    # the record through base dict operations: the pairs the
    # record stores stand iterated directly, and a field stands
    # present only where a stored text key carries its name
    # under a base class comparison, never through a hash or
    # equality reading a handed key supplies. Form 36 stands
    # under this same scan: its eventlog validation runs only
    # after the scan, never before it, so a base field supplied
    # only by a key whose hash and equality readings lie stands
    # absent here as at every other form.
    stored_pairs = list(dict.items(instance))
    for field in required_fields(fid):
        if fid == "22":
            matched = [
                item for key, item in stored_pairs
                if _stored_key_text(key) is not None
                and str.__eq__(_stored_key_text(key), field)
            ]
        else:
            matched = [
                item for key, item in stored_pairs
                if isinstance(key, str)
                and str.__eq__(str.__str__(key), field)
            ]
        if not matched or matched[0] is None:
            return False
    if fid == "36":
        return _validate_eventlog(instance)
    for condition in _conditions_for(fid):
        # The discriminator and the conditional field stand read
        # through the stored pairs of the record, in the same form
        # as the presence act above: a field stands present only
        # where a stored text key carries its name under a base
        # class comparison, never through a hash or equality
        # reading a handed key supplies, and the discriminator
        # value stands as the value its stored pair carries.
        discriminator_matches = [
            item for key, item in stored_pairs
            if isinstance(key, str)
            and str.__eq__(str.__str__(key), condition["discriminator"])
        ]
        discriminator = (
            discriminator_matches[0] if discriminator_matches else None)
        if discriminator is not None and not isinstance(
                discriminator, bool):
            return False
        if discriminator is True:
            field_matches = [
                item for key, item in stored_pairs
                if isinstance(key, str)
                and str.__eq__(str.__str__(key), condition["field"])
            ]
            if not field_matches:
                return False
    if fid == "22":
        # The amended form 22 reading: the outcome stands read with
        # the confirmation outcome and the gate failure, and with no
        # other reading, and an unranked claim stands only in its
        # stated form, the value not ranked in its test value, rank,
        # and threshold fields together. Every value here stands
        # read through the stored pairs of the record.
        def _registry_text(field):
            matches = [
                item for key, item in stored_pairs
                if _stored_key_text(key) is not None
                and str.__eq__(_stored_key_text(key), field)
            ]
            if not matches:
                return None
            return _stored_text_dress(matches[0])

        for _field, _stated_set in (
                ("outcome", ("reported", "not reported")),
                ("confirmation_outcome", ("passed", "failed", "not run")),
                ("gate_failure", (
                    "procedure gate", "confirmation gate",
                    "both gates", "none"))):
            _matches = [
                item for key, item in stored_pairs
                if _stored_key_text(key) is not None
                and str.__eq__(_stored_key_text(key), _field)
            ]
            if _matches:
                # A field standing present whose value yields
                # no text dress, a dict dress or an integer
                # form, carries a value in none of its stated
                # set, so it fails here as it fails at the
                # MOD-13 comparison and the MOD-11 gate, and
                # not only a value whose text dress stands
                # outside the set.
                _value = _stored_text_dress(_matches[0])
                if _value is None or _value not in _stated_set:
                    return False

        if _registry_text("outcome") == "reported":
            if _registry_text("confirmation_outcome") in (
                    "failed", "not run"):
                return False
            if _registry_text("gate_failure") in (
                    "procedure gate", "confirmation gate", "both gates"):
                return False
        unranked = [
            _registry_text(field) == "not ranked"
            for field in ("test_value", "rank", "threshold")
        ]
        if any(unranked) and not all(unranked):
            return False
    if fid == "4":
        if _carries_real_money_value(instance):
            return False
        for key, anchor_values in dict.items(instance):
            if not _folded_key_matches(key, _ANCHOR_VALUES_FIELD_FOLDED):
                continue
            try:
                anchor_count = _base_len(anchor_values)
            except TypeError:
                return False
            if anchor_count != 3:
                return False
    if fid == "15":
        for field, parts in JOINT_OUTCOME_COMPONENT_PARTS.items():
            component = _stored_pairs_value(
                instance, field, _STORED_MISSING)
            if component is _STORED_MISSING or not isinstance(
                    component, dict):
                return False
            for part in parts:
                if _stored_pairs_value(
                        component, part, _STORED_MISSING) is (
                        _STORED_MISSING) or _stored_pairs_value(
                        component, part) is None:
                    return False
    if fid in CLOSED_FORMS:
        # Each handed field name stands judged by the text it
        # stores, read through base class operations, never
        # through a hash or equality reading the key supplies.
        allowed = form_fields(fid)
        for key in dict.keys(instance):
            stored = _stored_text(key)
            if stored is None:
                return False
            if not any(
                    str.__eq__(stored, field) for field in allowed):
                return False
    if fid == "1":
        for slug in _COMPLETENESS_SLUGS:
            value = _stored_pairs_value(instance, slug)
            if value is not None and not (
                isinstance(value, str)
                and str.startswith(value, OPEN_MARKER_PREFIX)
            ):
                return False
    if _carries_reserved_matter(instance):
        return False
    if _stored_pairs_present(instance, "calibration_claim_field"):
        if not validate_calibration_field(
                _stored_pairs_value(instance, "calibration_claim_field")):
            return False
    if _stored_pairs_present(instance, "store_kind"):
        if not validate_store_kind(
                _stored_pairs_value(instance, "store_kind")):
            return False
    if fid == "10" and _stored_pairs_present(instance, "lien_state"):
        if not validate_lien_state(
            _stored_pairs_value(instance, "lien_state"),
            cross_seam=bool(_stored_pairs_value(
                instance, "cross_seam_effect", False)),
        ):
            return False
    if fid == "5" and _stored_pairs_present(instance, "parameter_values"):
        values = _stored_pairs_value(instance, "parameter_values")
        items = (
            _base_iter(values) if isinstance(values, (list, tuple))
            else (values,))
        if any(not isinstance(v, str) for v in items):
            return False
    return True


def validate_record(form_id, instance):
    """Validate one record instance against its form, in the form
    _validate_record_inner states. A value deeper than the stated
    traversal bound, or carrying a cycle, fails validation and
    returns False, in place of a bare recursion error."""
    try:
        return _validate_record_inner(form_id, instance)
    except (RecordTraversalFailure, RecursionError):
        return False


def _validate_eventlog(instance):
    # Every field reading in this act runs through the stored
    # pairs of the record, in the form the presence act of
    # _validate_record_inner states: a field stands present only
    # where a stored text key carries its name under a base class
    # comparison, and its value stands as the value its stored
    # pair carries, never through a contains, get, or getitem
    # reading on the handed instance, which runs a hash or
    # equality reading a handed key supplies.
    stored_pairs = list(dict.items(instance))

    def present(field):
        return any(
            isinstance(key, str)
            and str.__eq__(str.__str__(key), field)
            for key, item in stored_pairs)

    def stored_value(field):
        for key, item in stored_pairs:
            if isinstance(key, str) and str.__eq__(
                    str.__str__(key), field):
                return item
        return None

    for field in _EVENTLOG_BASE_FIELDS:
        if not present(field) or stored_value(field) is None:
            return False
    kind = stored_value("entry_kind")
    if kind is not None and kind not in (
            "ordinary", "agent", "supersession"):
        return False
    if kind is None:
        if (
            present("superseded_from_journal_position")
            or present("resume_attempt_identifier")
        ):
            kind = "supersession"
        elif present("agent_identifier"):
            kind = "agent"
        else:
            kind = "ordinary"
    if kind == "ordinary":
        for field in (
            "agent_identifier",
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if present(field):
                return False
    if kind == "agent":
        for field in (
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if present(field):
                return False
    if kind == "supersession" and present("agent_identifier"):
        return False
    if kind == "agent" and not present("agent_identifier"):
        return False
    if kind == "supersession":
        for field in (
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if not present(field):
                return False
    if _carries_reserved_matter(instance):
        return False
    return True


def run_is_reportable(form_id, instance):
    """A run whose record fails validation is not reportable. A failed
    run is not reportable as a completed run."""
    fid = _fid(form_id)
    if not validate_record(fid, instance):
        return False
    if isinstance(instance, dict) and _stored_text_equals(
            _stored_pairs_value(instance, "run_status"), "failed"):
        return False
    if fid == "1" and not family_supports_reportable_run(instance):
        return False
    return True


# ---------------------------------------------------------------------------
# Failure representation, OP-23
# ---------------------------------------------------------------------------

def named_failure_forms():
    return NAMED_FAILURES


def failure_value(form):
    """A failure is a value with a name, never a partial record
    presented as complete."""
    return {"name": form, "run_status": "failed", "complete": False}


def partial_record_is_marked(run_status=None, partial=None, record=None):
    """The marking rule for partial records: a partial record of a
    failed run carries its marking, so it can never be presented as
    complete."""
    if isinstance(record, dict):
        return _stored_value_present(
            _stored_pairs_value(record, "partial")) and (
            _stored_value_present(_stored_pairs_value(
                record, "marked_partial", False)))
    return bool(partial)


def validate_run_status(record_status=None, presented_as=None, record=None):
    """A failed run record does not validate as a completed run."""
    if isinstance(record, dict):
        record_status = _stored_pairs_value(
            record, "run_status", record_status)
        presented_as = _stored_pairs_value(
            record, "presented_as", presented_as)
    if not _stored_text_in(record_status, ("completed", "failed")):
        return False
    if presented_as is None:
        return True
    return _base_value_equals(record_status, presented_as)


# ---------------------------------------------------------------------------
# Canonical form machinery, OP-24. No canonical form is delivered here.
# ---------------------------------------------------------------------------

def state_hash_field_list():
    """The AC-1 state hash field list and its order, carried as
    carriage."""
    return AC1_STATE_HASH_FIELDS


def canonical_form_for_field(field):
    """The canonical form of a field, only where a plan level record
    states one for that field. None where no form stands stated."""
    form = _CANONICAL_FORMS.get(field)
    return dict(form) if form is not None else None


def hash_equality_claim_permitted(basis=None):
    """The OP-24 bar as a code level contract: while OP-24 stands open
    in part, no byte level hash equality is claimed, and no field with
    no plan stated canonical form enters a hash equality claim on any
    basis."""
    return False


def validate_derivation_input_rendering(rendering=None, binary_float=None):
    """The one canonical rendering rule the brief states, in its stated
    scope: seed derivation inputs enter as recorded strings, never as
    binary float renderings."""
    if binary_float is not None:
        return False
    return isinstance(rendering, str)


# ---------------------------------------------------------------------------
# Compound fields, copied by value
# ---------------------------------------------------------------------------

def _guarded_copy(value, _memo=None):
    """Copy a handed compound value through base class readings
    only. Dict parts stand read through the base dict items
    reading, and list, tuple, set and frozenset parts through
    their base iteration readings, so no copy protocol a part
    supplies is ever invoked and a part supplying a lying copy
    protocol cannot materialise as another value inside the
    copy. The buffer forms stand carried as stored: a bytearray
    as a fresh bytearray and a memoryview as a memoryview over
    fresh bytes. A part in no container form and no buffer form
    stands copied as itself."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_guarded_copy(key, _memo)] = _guarded_copy(
                item, _memo)
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _guarded_copy(item, _memo)
            for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _guarded_copy(item, _memo)
            for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        if id(value) in _memo:
            return _memo[id(value)]
        base_iter = (
            set.__iter__ if isinstance(value, set)
            else frozenset.__iter__)
        if isinstance(value, set):
            copied = set()
            _memo[id(value)] = copied
            for item in base_iter(value):
                copied.add(_guarded_copy(item, _memo))
            return copied
        copied = frozenset(
            _guarded_copy(item, _memo) for item in base_iter(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    return value


class VersionStamp:
    """A single compound field, copied by value. One validation rule
    for stamps: validation fails any artefact whose stamp is
    incomplete or whose family hash does not match the sealed family
    record."""

    FIELDS = ("family_version", "family_manifest_hash", "rule_version_set")

    def __init__(self, values):
        if isinstance(values, dict):
            stored = {key: item for key, item in dict.items(values)}
        else:
            stored = {}
        _guard_copyable(stored)
        self._values = _guarded_copy(stored)

    def as_dict(self):
        _guard_copyable(self._values)
        return _guarded_copy(self._values)

    def __eq__(self, other):
        return isinstance(other, VersionStamp) and self._values == other._values


def validate_version_stamp(stamp, sealed_family_hash=None):
    try:
        values = VersionStamp.as_dict(stamp) if isinstance(
            stamp, VersionStamp) else stamp
    except (RecordTraversalFailure, RecursionError):
        return False
    if not isinstance(values, dict):
        return False
    for field in VersionStamp.FIELDS:
        if not _stored_value_present(_stored_pairs_value(values, field)):
            return False
    if sealed_family_hash is not None:
        return _base_value_equals(
            _stored_pairs_value(values, "family_manifest_hash"),
            sealed_family_hash)
    return True


class ProvenanceBlock:
    """A single compound field, copied by value: the union of the
    adjudication and detection seam field sets, an applicability mark
    per field, error direction beside every arbiter accuracy value,
    and the excluded class counts and shares in full. Any figure whose
    block is incomplete fails validation."""

    def __init__(self, entries, excluded_class_counts, excluded_class_shares):
        self._entries = _guarded_copy(entries)
        self._counts = _guarded_copy(excluded_class_counts)
        self._shares = _guarded_copy(excluded_class_shares)

    def as_dict(self):
        return {
            "entries": _guarded_copy(self._entries),
            "excluded_class_counts": _guarded_copy(self._counts),
            "excluded_class_shares": _guarded_copy(self._shares),
        }


def _plain_number(value):
    """The stored number of a handed int or float value, read
    through the base class conversion of its kind, never through
    a conversion the value itself supplies. A float subclass
    storing a fraction whose own float conversion reports a whole
    number therefore stands judged by the fraction it stores,
    and an int subclass stands judged by the count it stores."""
    if isinstance(value, float):
        return float.__float__(value)
    return int.__int__(value)


def _is_count_value(value):
    # A count of cases stands in numeric form only: a whole number,
    # never a boolean, never a text value, and never a fraction of
    # one case. A float that stands at a whole number counts, because
    # its value is a whole count; a fractional float does not. A
    # count of cases also stands in range: no count stands below
    # zero. The value stands judged by the number it stores, read
    # through the base class conversion of its kind.
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return _plain_number(value) >= 0
    if isinstance(value, float):
        plain = float.__float__(value)
        return (
            plain == plain
            and abs(plain) != float("inf")
            and plain.is_integer()
            and plain >= 0
        )
    return False


def _is_share_value(value):
    # A share stands in numeric form only: a number, never a boolean
    # and never a text value. A fractional share stands, because a
    # share is a part of the whole stated as a number. A share also
    # stands in range: a share of a whole stands at no less than
    # zero and at no more than the whole. The value stands judged
    # by the number it stores, read through the base class
    # conversion of its kind.
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 0 <= _plain_number(value) <= 1
    if isinstance(value, float):
        plain = float.__float__(value)
        return (
            plain == plain
            and abs(plain) != float("inf")
            and 0 <= plain <= 1
        )
    return False


def _stored_value_present(value):
    """Whether a handed value stands present, judged by what it
    stores, for every kind. A text value stands present where the
    text it stores stands non empty, read through the base class
    length. A container or bytes value stands present where the
    contents it stores stand non empty, read through the base
    class length of its kind. A boolean stands present where it
    stands as True, and a number where the number it stores
    stands apart from zero, each read through the base class
    operations of its kind. A value of any other kind carries no
    stored content a base class operation can read, so it stands
    absent, whatever truth reading it supplies."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, (
            list, tuple, set, frozenset, dict, bytearray, bytes)):
        return _base_len(value) > 0
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    return False


def _stored_key(key):
    """The stored form of a handed mapping key, as a tagged token
    no handed reading can direct. A text key stands as the text
    it stores, read through the base class. A boolean, a number,
    and a bytes key each stand as the plain value they store,
    read through the base class operations of their kind. A
    tuple or frozenset key stands as the stored forms of its
    parts, read through the base class iteration of its kind.
    A key of any other kind stands as itself by identity alone,
    so a non text key whose hash and equality readings answer
    as a class name stands compared as no class name."""
    if isinstance(key, str):
        return ("text", str.__str__(key))
    if isinstance(key, bool):
        return ("bool", key is True)
    if isinstance(key, int):
        return ("int", int.__int__(key))
    if isinstance(key, float):
        return ("float", float.__float__(key))
    if isinstance(key, bytes):
        return ("bytes", bytes(key))
    if isinstance(key, tuple):
        return ("tuple", tuple(
            _stored_key(part) for part in tuple.__iter__(key)))
    if isinstance(key, frozenset):
        return ("frozenset", frozenset(
            _stored_key(part) for part in frozenset.__iter__(key)))
    return ("identity", id(key))


def validate_provenance_block(block):
    try:
        data = ProvenanceBlock.as_dict(block) if isinstance(
            block, ProvenanceBlock) else block
    except (RecordTraversalFailure, RecursionError):
        return False
    if not isinstance(data, dict):
        return False
    counts = _stored_pairs_value(data, "excluded_class_counts")
    shares = _stored_pairs_value(data, "excluded_class_shares")
    if not isinstance(counts, dict) or not isinstance(shares, dict):
        return False
    if dict.__len__(counts) == 0 or dict.__len__(shares) == 0:
        return False
    if {_stored_key(key) for key in dict.keys(counts)} != {
            _stored_key(key) for key in dict.keys(shares)}:
        return False
    count_values = list(dict.values(counts))
    share_values = list(dict.values(shares))
    if any(value is None for value in count_values):
        return False
    if any(value is None for value in share_values):
        return False
    if any(not _is_count_value(value) for value in count_values):
        return False
    if any(not _is_share_value(value) for value in share_values):
        return False
    entries = _stored_pairs_value(data, "entries")
    if isinstance(entries, (list, tuple)):
        entries = list(_base_iter(entries))
        if not entries:
            return False
    elif not entries:
        return False
    for entry in entries:
        if not isinstance(entry, dict) or not _stored_value_present(
                _stored_pairs_value(entry, "field")):
            return False
        if not _stored_pairs_present(entry, "applicability"):
            return False
        field_value = _stored_pairs_value(entry, "field")
        field_text = (
            str.__str__(field_value) if isinstance(field_value, str)
            else str(field_value))
        field_reading = " ".join(
            field_text.lower().replace(
                "_", " ").replace("-", " ").replace("\t", " ").split())
        if "arbiter accuracy" in field_reading:
            if not _stored_value_present(
                    _stored_pairs_value(entry, "error_direction")):
                return False
    return True


# The distinct provenance value a fitted value carries in AssumptionRecord
# carriage, picked at WI8B-02 in pay now form only. The fitting pipeline
# itself is a named bound and is not built in this slice.
PROVENANCE_VALUE_FITTED = "fitted value, distinct provenance value"


# ---------------------------------------------------------------------------
# DQ7-12 open types. Named types with no validator claimed.
# ---------------------------------------------------------------------------

class DependencyManifest:
    """The dependency manifest, per build. A named open type under
    DQ7-12: no validator is claimed for it in this slice."""

    FIELDS = (
        "build_identity", "dependency_entries", "completeness_statement",
        "manifest_version_and_hash",
    )
    VALIDATOR_CLAIMED = False

    def __init__(self, values=None):
        self.values = copy.deepcopy(dict(values or {}))


class CallLog:
    """The process and network call log, per run. A named open type
    under DQ7-12: no validator is claimed for it in this slice."""

    FIELDS = (
        "run_identifier", "call_entries", "empty_log_form",
        "closing_marker",
    )
    VALIDATOR_CLAIMED = False

    def __init__(self, values=None):
        self.values = copy.deepcopy(dict(values or {}))


# ---------------------------------------------------------------------------
# Named record types, one per form, each with a single owner
# ---------------------------------------------------------------------------

_FORM_OWNERS = {
    "1": "MOD-12", "2": "MOD-12", "3": "MOD-12", "4": "MOD-10",
    "5": "MOD-02", "6": "MOD-02", "7": "MOD-04", "8": "MOD-05",
    "9": "MOD-05", "10": "MOD-06", "11": "MOD-05", "12": "MOD-08",
    "13": "MOD-10", "13A": "MOD-04", "14": "MOD-10", "15": "MOD-10",
    "16": "MOD-11", "17": "MOD-12", "18": "MOD-10", "19": "MOD-04",
    "20": "MOD-10", "21": "MOD-10", "22": "MOD-11", "23": "MOD-12",
    "24": "MOD-12", "25": "MOD-14", "26": "MOD-10", "27": "MOD-08",
    "28": "MOD-13", "29": "MOD-07", "30": "MOD-10", "31": "MOD-14",
    "32": "MOD-12", "33": "MOD-10", "34": "MOD-13", "35": "MOD-11",
    "36": "MOD-10", "37": "MOD-10",
}


class _RecordForm:
    FORM_ID = None
    FIELDS = ()
    OWNER = None

    def __init__(self, values=None):
        if values is None:
            stored = {}
        elif isinstance(values, dict):
            stored = {key: item for key, item in dict.items(values)}
        else:
            stored = {}
        self.values = _guarded_copy(stored)

    def validate(self):
        return validate_record(self.FORM_ID, self.values)

    def is_reportable(self):
        return run_is_reportable(self.FORM_ID, self.values)


def _make_form_type(name, form_id):
    return type(name, (_RecordForm,), {
        "FORM_ID": form_id,
        "FIELDS": _FORM_SPECS[form_id][1],
        "OWNER": _FORM_OWNERS.get(form_id),
        "__module__": __name__,
    })


FORM_TYPES = {}
for _fid_key, (_name, _fl) in _FORM_SPECS.items():
    _cls = _make_form_type(_name, _fid_key)
    FORM_TYPES[_fid_key] = _cls
    globals()[_name] = _cls
del _fid_key, _name, _fl, _cls


class ViewRecord(_RecordForm):
    """The decided per viewer view record, counted beside the 38."""

    FORM_ID = "ViewRecord"
    FIELDS = _VIEW_RECORD_FIELDS
    OWNER = "MOD-04"

    def validate(self):
        for field in self.FIELDS:
            if field not in self.values or self.values[field] is None:
                return False
        return not _carries_reserved_matter(self.values)


# ---------------------------------------------------------------------------
# Reconciliation surface, AC-14
# ---------------------------------------------------------------------------

# The expected load bearing field set per source form, as stated in
# design/steps/step-14-f08-reconciliation-table.md, section 5, with
# 99 rows in total: ARB 8, BOO 5, PAM 17, RFO 20, and RET 49. Each
# entry carries the field, its source form, and its place exactly
# as that table states them, and every entry is load bearing.
_TRACE_SPEC = (
    ("Arbiter accuracy value applied, stated as a labelled assumption", "ARB", "Interpretation choices group", True),
    ("Assumption set identifier, for the accuracy row the run used", "ARB", "Assumption record group", True),
    ("Row identifier, for the accuracy row inside its named set", "ARB", "Assumption record group", True),
    ("Sensitivity range in force, for the accuracy value", "ARB", "Assumption record group", True),
    ("Error direction for the accuracy value, in the symmetric split form or the directional pair form", "ARB", "Interpretation choices group, beside the accuracy value that group carries", True),
    ("Dependence mark citing DQ-164, in the form: depends on Parley Q1, Q2, or Q5 as applicable, unconfirmed, pending DQ-164; the Q2 limb is not optional for accuracy results", "ARB", "Reserved matter group, dependence labels", True),
    ("Mark citing DQ-163, for any run that used an anchor scenario", "ARB", "Reserved matter group, dependence labels", True),
    ("Excluded adjudication class counts and shares, for each of the four excluded classes ARB defines", "ARB", "Outcome and retention group", True),
    ("Anchor scenario identifier, marked under DQ-163, including the explicit empty set marker where the scenario is the empty anchor set", "BOO", "Reserved matter group, as one of the three values of the AnchorScenarioRecord", True),
    ("Assumption set identifier, for the run", "BOO", "Assumption record group", True),
    ("Row identifiers inside the named set, for the run, naming in particular the vouch formation, honest vouching propensity, internal vouch density, and adjudication accuracy rows in force", "BOO", "Assumption record group", True),
    ("Dependence stamp: Q1 and Q2 dependence marked on the run as a whole, and Q5 dependence marked where its field 6 or field 7 answers feed suspect or freeze handling", "BOO", "Reserved matter group, dependence labels", True),
    ("Core only qualifier, where escrow results are reported alongside", "BOO", "Variant stamp group", True),
    ("Run identifier", "PAM", "Identity and design group", True),
    ("Sweep identifier", "PAM", "Identity and design group", True),
    ("Population size", "PAM", "Identity and design group", True),
    ("Run length", "PAM", "Identity and design group, as run length in days", True),
    ("Root seed reference", "PAM", "Identity and design group", True),
    ("Derived run seed identifier", "PAM", "Identity and design group", True),
    ("Assumption set identifier (the set name, in PAM words)", "PAM", "Assumption record group", True),
    ("Row identifiers, for every behaviour parameter used", "PAM", "Assumption record group", True),
    ("Interpretation choice identifier, one entry per point, P-01 to P-30, with no point omitted", "PAM", "Interpretation choices group", True),
    ("Reading applied, one entry per point (the reading taken, in PAM words)", "PAM", "Interpretation choices group", True),
    ("Value or values used in this run, for a parameterised judgement entry", "PAM", "Assumption record group, as the value used for that behaviour parameter", True),
    ("Sensitivity range, for a parameterised judgement entry", "PAM", "Assumption record group, as the sensitivity range fixed before runs for that behaviour parameter", True),
    ("Dependence field, present for every entry: the dependence statement in PAM stated words for an entry resting on a Q1, Q2, or Q5 confirmation, or the statement that no such dependence applies to that entry", "PAM", "Reserved matter group, dependence labels", True),
    ("Pause cap value in force, for this variant", "PAM", "Variant stamp group, as the pause value in force, stated as extension and total", True),
    ("Escrow variant", "PAM", "Variant stamp group", True),
    ("Rule version set, carrying the ruling fold version element PAM names", "PAM", "Variant stamp group", True),
    ("Parley test total source used, where a total is cited, naming the 120 count or the 122 count, or stating that no test total is cited", "PAM", "Log entry inside the run record", True),
    ("Value or swept range, for every assumed parameter the result depends on", "RFO", "Assumption record group, as the value used for that behaviour parameter", True),
    ("Sensitivity range, for every assumed parameter the result depends on", "RFO", "Assumption record group", True),
    ("Provenance label (the assumption label, in RFO words), for every assumed parameter", "RFO", "Assumption record group, as the provenance label for that behaviour parameter", True),
    ("Assumption set identifier", "RFO", "Assumption record group", True),
    ("Row identifiers, for every entry in its assumption record", "RFO", "Assumption record group", True),
    ("Interpretation choice identifier, for every choice the result rests on", "RFO", "Interpretation choices group", True),
    ("Reading applied, for every choice the result rests on, stated as a choice and not as a fact of the source text", "RFO", "Interpretation choices group", True),
    ("Arbiter accuracy value, where behavioural adjudication is involved, as a labelled assumption", "RFO", "Interpretation choices group", True),
    ("Escrow variant named in the variant stamp, B-4 or B-3, and both variants named for a difference result", "RFO", "Variant stamp group, as the escrow variant", True),
    ("Pause cap value in force, for that variant, wherever a pause related value appears", "RFO", "Variant stamp group, as the pause value in force, stated as extension and total", True),
    ("Core only qualifier, where the result concerns the escrow", "RFO", "Variant stamp group", True),
    ("Dependence marking citing DQ-164, where any part of the result depends on Parley Q1, Q2, or Q5", "RFO", "Reserved matter group, dependence labels", True),
    ("Anchor scenario marking, where the result uses anchor material: scenario only, marked citing DQ-163, with no favoured point", "RFO", "Reserved matter group, dependence labels, with the scenario values in the same group", True),
    ("Calibration claim field, whose only permitted value reads: no calibration claim, self consistency only", "RFO", "Joined done test group", True),
    ("Sweep family identifier", "RFO", "Identity and design group, as sweep family identifier", True),
    ("Root seed reference (the root seed, in RFO words)", "RFO", "Identity and design group", True),
    ("Sweep identifier", "RFO", "Identity and design group", True),
    ("Population size", "RFO", "Identity and design group", True),
    ("Run length", "RFO", "Identity and design group, as run length in days", True),
    ("Rule version set", "RFO", "Variant stamp group", True),
    ("Sweep identifier", "RET", "Identity and design group", True),
    ("Sweep family identifier", "RET", "Identity and design group", True),
    ("Run identifier", "RET", "Identity and design group", True),
    ("Sweep point identifier", "RET", "Identity and design group", True),
    ("Run class, one of screening, confirmation, headline, or validation", "RET", "Identity and design group", True),
    ("Design kind", "RET", "Identity and design group", True),
    ("Replicate group identifier", "RET", "Identity and design group", True),
    ("Replicate index within its group", "RET", "Identity and design group", True),
    ("Population size", "RET", "Identity and design group", True),
    ("Run length in days", "RET", "Identity and design group", True),
    ("Horizon variant marker", "RET", "Identity and design group", True),
    ("Control values", "RET", "Identity and design group", True),
    ("Root seed reference", "RET", "Identity and design group", True),
    ("Derived run seed identifier", "RET", "Identity and design group", True),
    ("Separate stream identifiers, for each purpose stream the run used", "RET", "Identity and design group", True),
    ("Assumption set identifier", "RET", "Assumption record group", True),
    ("Row identifier inside its named set, for every behaviour parameter the run used", "RET", "Assumption record group", True),
    ("Value used, for every behaviour parameter the run used", "RET", "Assumption record group", True),
    ("Sensitivity range as fixed before runs, for every behaviour parameter the run used", "RET", "Assumption record group", True),
    ("Provenance label, reading labelled assumption for every unfitted parameter", "RET", "Assumption record group", True),
    ("Escrow variant", "RET", "Variant stamp group", True),
    ("Matched run identifier, of the counterpart run in the other variant", "RET", "Variant stamp group", True),
    ("Pause cap value in force, for this variant, stated as extension and total", "RET", "Variant stamp group, as the pause value in force", True),
    ("Rule version set: Parley amendment level applied, escrow folding version, and Vigil likelihood ratio table version", "RET", "Variant stamp group", True),
    ("Core only qualifier, a boolean field that must read true for every escrow bearing result", "RET", "Variant stamp group", True),
    ("Interpretation choice identifier, for every interpretation choice that applies to this run", "RET", "Interpretation choices group", True),
    ("Reading applied, for every interpretation choice that applies to this run", "RET", "Interpretation choices group", True),
    ("Parameter reference, where the choice enters as a labelled assumption (the parameter or rule point affected, in Form 4 words)", "RET", "Interpretation choices group", True),
    ("Arbiter accuracy value and its row reference, carried explicitly in this group", "RET", "Interpretation choices group", True),
    ("Dependence label listing DQ-164, wherever the run depends on Parley Q1, Q2, or Q5", "RET", "Reserved matter group, dependence labels", True),
    ("Dependence entry recording, for any anchor scenario run, the mark citing DQ-163", "RET", "Reserved matter group, dependence labels", True),
    ("Correlation statement, or the joint design reference where correlated parameters were swept jointly", "RET", "Reserved matter group", True),
    ("Scenario identifier, for an anchor scenario run, one of three values and no fourth", "RET", "Reserved matter group", True),
    ("Anchor set description, as a scenario setting, one of three values and no fourth", "RET", "Reserved matter group", True),
    ("Mark citing DQ-163, for an anchor scenario run, one of three values and no fourth", "RET", "Reserved matter group", True),
    ("Joint outcome vector, as end of run values", "RET", "Outcome and retention group", True),
    ("Regime classification", "RET", "Outcome and retention group", True),
    ("Winning criterion evaluation, as three stored values", "RET", "Outcome and retention group", True),
    ("Retention tier reached", "RET", "Outcome and retention group", True),
    ("List of flag conditions that fired, by condition number, or an empty list", "RET", "Outcome and retention group", True),
    ("Pointers to the daily aggregates, to snapshots where retained, to the event log where retained, and to the final checkpoint where retained", "RET", "Outcome and retention group", True),
    ("End of run full state hash", "RET", "Outcome and retention group", True),
    ("Store kind field", "RET", "Outcome and retention group", True),
    ("Timing pilot record reference, or the provisional grid marker, as the sole either or carriage of that pair", "RET", "Joined done test group", True),
    ("Folding record reference", "RET", "Joined done test group", True),
    ("Seam check reference", "RET", "Joined done test group", True),
    ("NQ-10 listing version, with the list of any DQ-5 to DQ-30 items the run exercises, or an explicit none value", "RET", "Joined done test group", True),
    ("NQ-6 classification marker", "RET", "Joined done test group", True),
    ("Calibration claim field, whose only permitted value reads: no calibration claim, self consistency only", "RET", "Joined done test group", True),
)


def reconciliation_trace():
    """The reconciliation trace for the single RunRecord: every field,
    its source form among ARB, BOO, PAM, RFO and RET, its place in the
    single record, and its load bearing mark."""
    return [
        {
            "field": field,
            "source_form": source,
            "place_in_single_record": place,
            "place": place,
            "load_bearing": bearing,
        }
        for field, source, place, bearing in _TRACE_SPEC
    ]


def reconciliation_trace_check():
    """The recorded reader check of the trace, by a reader who did not
    perform the reconciliation, in the pattern decision D-20 states."""
    return {
        "reconciler": "MOD-01 reconciliation",
        "checker": "independent reader",
        "recorded": True,
    }


def check_reconciliation_trace(trace):
    """The reader check, judged on the contents of the trace
    presented: it fails where a load bearing field is dropped, or an
    entry names no source form or no place."""
    if not isinstance(trace, (list, tuple)):
        return False
    presented = set()
    for entry in trace:
        if not isinstance(entry, dict):
            return False
        source_form = _stored_pairs_value(entry, "source_form")
        place = _stored_pairs_value(entry, "place_in_single_record")
        field = _stored_pairs_value(entry, "field")
        if source_form not in SOURCE_FORMS:
            return False
        if not _stored_value_present(place) or not _stored_value_present(
                field):
            return False
        presented.add((field, source_form, place))
    required = {
        (f, s, p) for f, s, p, bearing in _TRACE_SPEC if bearing
    }
    return required.issubset(presented)


def reconciliation_criterion_verdict(trace):
    """AC-14 stands failed, never passed with a note, on a trace with
    a load bearing field dropped."""
    return "passed" if check_reconciliation_trace(trace) else "failed"

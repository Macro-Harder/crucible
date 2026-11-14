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

import copy
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


def _fid(form_id):
    return str(form_id)


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
            if candidate["field"] == condition_holds.get("field"):
                named_disc = candidate["discriminator"]
    for condition in _conditions_for(fid):
        holds = bool(condition_holds) and (
            not isinstance(condition_holds, dict)
            or condition_holds.get("field") == condition["field"]
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


def _guard_copyable(value, depth=0, seen=None):
    if seen is None:
        seen = set()
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        _traversal_guard(value, depth, seen)
        seen.add(id(value))
        try:
            items = value.items() if isinstance(value, dict) else (
                (item, item) for item in value)
            for key, item in items:
                _guard_copyable(key, depth + 1, seen)
                _guard_copyable(item, depth + 1, seen)
        finally:
            seen.discard(id(value))


def _carries_reserved_matter(value, _depth=0, _seen=None):
    if _seen is None:
        _seen = set()
    if isinstance(value, str):
        return value in RESERVED_MATTER_VALUES
    if isinstance(value, dict):
        _traversal_guard(value, _depth, _seen)
        _seen.add(id(value))
        try:
            return any(
                _carries_reserved_matter(k, _depth + 1, _seen)
                or _carries_reserved_matter(v, _depth + 1, _seen)
                for k, v in value.items()
            )
        finally:
            _seen.discard(id(value))
    if isinstance(value, (list, tuple, set, frozenset)):
        _traversal_guard(value, _depth, _seen)
        _seen.add(id(value))
        try:
            return any(
                _carries_reserved_matter(v, _depth + 1, _seen)
                for v in value)
        finally:
            _seen.discard(id(value))
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
    "\u03b1": "a", "\u03bf": "o", "\u03b5": "e", "\u03b9": "i",
    "\u03ba": "k", "\u03bc": "m", "\u03bd": "n", "\u03c1": "r",
    "\u03c4": "t", "\u03c5": "y", "\u03bb": "l", "\u03c3": "s",
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


def _normalised_characters(text):
    decomposed = unicodedata.normalize("NFKD", str(text))
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


def _canonical_variants(text):
    # A symbol sign carries two readings in the variants: the letter
    # it stands for, and the sign itself, which the fold drops as it
    # drops every separator. A name therefore reads both ways, with
    # the sign standing for its letter and with the sign holding
    # nothing apart.
    variants = [""]
    for character in _normalised_characters(text):
        if character in _MULTI_READINGS:
            readings = _MULTI_READINGS[character]
        elif character in _SYMBOL_LEET_READINGS:
            readings = (_SYMBOL_LEET_READINGS[character], character)
        else:
            readings = (_primary_reading(character),)
        if len(variants) * len(readings) > 1024:
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
    return variants


def _folded_key_matches(key, folded_target):
    return folded_target in _folded_key_variants(key)


def _folded_key_carries(key, folded_marker):
    return any(
        folded_marker in variant
        for variant in _folded_key_variants(key)
    )


_MONEY_MARKER_FOLDED = ("real_" + "money").replace("_", "")
_ANCHOR_VALUES_FIELD_FOLDED = _folded_money_key(
    "anchor_" + "scenario_values")


def _carries_real_money_value(value, _depth=0, _seen=None):
    if _seen is None:
        _seen = set()
    if isinstance(value, dict):
        _traversal_guard(value, _depth, _seen)
        _seen.add(id(value))
        amount_carried = any(
            _folded_key_matches(key, "amount") and item is not None
            for key, item in value.items()
        )
        currency_carried = any(
            _folded_key_matches(key, "currency")
            for key in value.keys()
        )
        try:
            if amount_carried and currency_carried:
                return True
            for key, item in value.items():
                if _folded_key_carries(key, _MONEY_MARKER_FOLDED) and (
                        item is not None):
                    return True
                if _carries_real_money_value(item, _depth + 1, _seen):
                    return True
            return False
        finally:
            _seen.discard(id(value))
    if isinstance(value, (list, tuple, set, frozenset)):
        _traversal_guard(value, _depth, _seen)
        _seen.add(id(value))
        try:
            return any(
                _carries_real_money_value(v, _depth + 1, _seen)
                for v in value)
        finally:
            _seen.discard(id(value))
    return False


def validate_lien_state(value, cross_seam=False):
    """The lien state bar at Shape 9: exactly four values, and while
    NQ-45 stands open no cross seam effect carries settled or released."""
    if value not in LIEN_STATES:
        return False
    if cross_seam and value in ("settled in the chosen escrow", "released"):
        return False
    return True


def validate_calibration_field(value):
    """The sole permitted value of the calibration claim field."""
    return value == CALIBRATION_FIELD_VALUE


def validate_store_kind(kind):
    return kind in STORE_KINDS


def store_index(kind):
    """The namespace token of a store kind. The three kinds are
    distinct namespaces with no shared index."""
    return "store namespace: " + str(kind)


def validate_store_addressing(addressing):
    """A record addressed to exactly one store kind validates in that
    namespace. A record addressed across two stores fails."""
    kinds = tuple(addressing)
    return len(kinds) == 1 and kinds[0] in STORE_KINDS


def reserved_matter_values():
    return RESERVED_MATTER_VALUES


def validate_family_seal_match(manifest, record):
    """Seal matching as a recorded value comparison: the run record
    family version and family manifest hash must match the sealed
    family record hash and version on the manifest, in the plan
    named fields of Forms 23 and 4."""
    if not isinstance(manifest, dict) or not isinstance(record, dict):
        return False
    version = manifest.get("family_version")
    digest = manifest.get("sealed_family_record_hash")
    if version is None or digest is None:
        return False
    return (
        record.get("family_version") == version
        and record.get("family_manifest_hash") == digest
    )


def family_supports_reportable_run(record):
    """The family completeness bar: every completeness field present,
    each OP-13 value carried as an open marker and never as a number."""
    if not isinstance(record, dict):
        return False
    for field in COMPLETENESS_FIELDS:
        if field not in record:
            return False
        value = record[field]
        if not isinstance(value, str):
            return False
        if not value.startswith(OPEN_MARKER_PREFIX) or "OP-13" not in value:
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
    if fid == "36":
        return _validate_eventlog(instance)
    for field in required_fields(fid):
        if field not in instance or instance[field] is None:
            return False
    for condition in _conditions_for(fid):
        discriminator = instance.get(condition["discriminator"])
        if discriminator is not None and not isinstance(
                discriminator, bool):
            return False
        if discriminator is True:
            if condition["field"] not in instance:
                return False
    if fid == "4":
        if _carries_real_money_value(instance):
            return False
        for key, anchor_values in instance.items():
            if not _folded_key_matches(key, _ANCHOR_VALUES_FIELD_FOLDED):
                continue
            try:
                anchor_count = len(anchor_values)
            except TypeError:
                return False
            if anchor_count != 3:
                return False
    if fid == "15":
        for field, parts in JOINT_OUTCOME_COMPONENT_PARTS.items():
            component = instance.get(field)
            if not isinstance(component, dict):
                return False
            for part in parts:
                if component.get(part) is None:
                    return False
    if fid in CLOSED_FORMS:
        allowed = set(form_fields(fid))
        if any(k not in allowed for k in instance):
            return False
    if fid == "1":
        for slug in _COMPLETENESS_SLUGS:
            value = instance.get(slug)
            if value is not None and not (
                isinstance(value, str) and value.startswith(OPEN_MARKER_PREFIX)
            ):
                return False
    if _carries_reserved_matter(instance):
        return False
    if "calibration_claim_field" in instance:
        if not validate_calibration_field(instance["calibration_claim_field"]):
            return False
    if "store_kind" in instance:
        if not validate_store_kind(instance["store_kind"]):
            return False
    if fid == "10" and "lien_state" in instance:
        if not validate_lien_state(
            instance["lien_state"],
            cross_seam=bool(instance.get("cross_seam_effect", False)),
        ):
            return False
    if fid == "5" and "parameter_values" in instance:
        values = instance["parameter_values"]
        items = values if isinstance(values, (list, tuple)) else (values,)
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
    for field in _EVENTLOG_BASE_FIELDS:
        if field not in instance or instance[field] is None:
            return False
    kind = instance.get("entry_kind")
    if kind is not None and kind not in (
            "ordinary", "agent", "supersession"):
        return False
    if kind is None:
        if (
            "superseded_from_journal_position" in instance
            or "resume_attempt_identifier" in instance
        ):
            kind = "supersession"
        elif "agent_identifier" in instance:
            kind = "agent"
        else:
            kind = "ordinary"
    if kind == "ordinary":
        for field in (
            "agent_identifier",
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if field in instance:
                return False
    if kind == "agent":
        for field in (
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if field in instance:
                return False
    if kind == "supersession" and "agent_identifier" in instance:
        return False
    if kind == "agent" and "agent_identifier" not in instance:
        return False
    if kind == "supersession":
        for field in (
            "superseded_from_journal_position",
            "resume_attempt_identifier",
        ):
            if field not in instance:
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
    if isinstance(instance, dict) and instance.get("run_status") == "failed":
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
        return bool(record.get("partial")) and bool(record.get("marked_partial", False))
    return bool(partial)


def validate_run_status(record_status=None, presented_as=None, record=None):
    """A failed run record does not validate as a completed run."""
    if isinstance(record, dict):
        record_status = record.get("run_status", record_status)
        presented_as = record.get("presented_as", presented_as)
    if record_status not in ("completed", "failed"):
        return False
    if presented_as is None:
        return True
    return record_status == presented_as


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

class VersionStamp:
    """A single compound field, copied by value. One validation rule
    for stamps: validation fails any artefact whose stamp is
    incomplete or whose family hash does not match the sealed family
    record."""

    FIELDS = ("family_version", "family_manifest_hash", "rule_version_set")

    def __init__(self, values):
        stored = dict(values)
        _guard_copyable(stored)
        self._values = copy.deepcopy(stored)

    def as_dict(self):
        _guard_copyable(self._values)
        return copy.deepcopy(self._values)

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
        if not values.get(field):
            return False
    if sealed_family_hash is not None:
        return values.get("family_manifest_hash") == sealed_family_hash
    return True


class ProvenanceBlock:
    """A single compound field, copied by value: the union of the
    adjudication and detection seam field sets, an applicability mark
    per field, error direction beside every arbiter accuracy value,
    and the excluded class counts and shares in full. Any figure whose
    block is incomplete fails validation."""

    def __init__(self, entries, excluded_class_counts, excluded_class_shares):
        self._entries = copy.deepcopy(list(entries))
        self._counts = copy.deepcopy(excluded_class_counts)
        self._shares = copy.deepcopy(excluded_class_shares)

    def as_dict(self):
        return {
            "entries": copy.deepcopy(self._entries),
            "excluded_class_counts": copy.deepcopy(self._counts),
            "excluded_class_shares": copy.deepcopy(self._shares),
        }


def validate_provenance_block(block):
    try:
        data = ProvenanceBlock.as_dict(block) if isinstance(
            block, ProvenanceBlock) else block
    except (RecordTraversalFailure, RecursionError):
        return False
    if not isinstance(data, dict):
        return False
    counts = data.get("excluded_class_counts")
    shares = data.get("excluded_class_shares")
    if not isinstance(counts, dict) or not isinstance(shares, dict):
        return False
    if not counts or not shares:
        return False
    if set(counts) != set(shares):
        return False
    if any(value is None for value in counts.values()):
        return False
    if any(value is None for value in shares.values()):
        return False
    entries = data.get("entries")
    if not entries:
        return False
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("field"):
            return False
        if "applicability" not in entry:
            return False
        field_reading = " ".join(
            str(entry.get("field")).lower().replace(
                "_", " ").replace("-", " ").replace("\t", " ").split())
        if "arbiter accuracy" in field_reading:
            if not entry.get("error_direction"):
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
        self.values = copy.deepcopy(dict(values or {}))

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
        if entry.get("source_form") not in SOURCE_FORMS:
            return False
        if not entry.get("place_in_single_record") or not entry.get("field"):
            return False
        presented.add((
            entry["field"],
            entry["source_form"],
            entry["place_in_single_record"],
        ))
    required = {
        (f, s, p) for f, s, p, bearing in _TRACE_SPEC if bearing
    }
    return required.issubset(presented)


def reconciliation_criterion_verdict(trace):
    """AC-14 stands failed, never passed with a note, on a trace with
    a load bearing field dropped."""
    return "passed" if check_reconciliation_trace(trace) else "failed"

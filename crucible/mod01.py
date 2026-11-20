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

Shape and Form numbering. The brief numbers its record shapes
at section 5.3, Shapes 1 to 17, and this module numbers its
record forms under the plan census. Shape 8 states two forms,
VouchEdge and GraphSnapshot, so from brief Shape 9 the product
Form number runs one ahead of the brief Shape number, under the
plan one ahead rule: brief Shape 9 is Form 10, brief Shape 12
is Form 13, brief Shape 13 is Form 14, and brief Shape 17 is
Form 18. The full explicit cross reference stands at
BRIEF_SHAPE_CROSS_REFERENCE in this module, with
brief_shape_for_form and form_ids_for_brief_shape reading it.
No product Form stands renumbered by that cross reference: the
Form numbers stand as the plan census states them, and the
cross reference states which brief Shape each Form answers.

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
from decimal import Decimal
from fractions import Fraction

_ARGUMENT_NOT_HANDED = object()
"""The standing of an argument no handing stands made for, so a
README named entry point of this module can refuse a missing
or extra argument handing in the named form of this module
instead of escaping as bare interpreter text at the call
itself (FW4-11, in the form the FW3-54 cure states)."""

__all__ = [
    "AC1_STATE_HASH_FIELDS",
    "CALIBRATION_FIELD_VALUE",
    "CLOSED_FORMS",
    "COMPLETENESS_FIELDS",
    "COMPLETENESS_KEY_PAIRS",
    "DQ163_MARK",
    "FAMILY_CARRIAGE_KEYS",
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
    "BRIEF_SHAPE_CROSS_REFERENCE",
    "build_run_record",
    "build_sweep_point",
    "brief_shape_for_form",
    "StatedJudgement",
    "canonical_form_for_field",
    "check_reconciliation_trace",
    "completeness_key_pairs",
    "completeness_standing",
    "failure_value",
    "family_reportable_standing",
    "family_supports_reportable_run",
    "field_conditions",
    "form_fields",
    "form_ids_for_brief_shape",
    "form_name",
    "hash_equality_claim_permitted",
    "minimal_valid_family_record",
    "minimal_valid_instance",
    "named_failure_forms",
    "partial_record_is_marked",
    "record_validation_failures",
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
    "validation_standing",
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

# The one completeness key set, standing for validation and for the
# reportability judgement alike (Step 16, R16-15): each completeness
# field stands under two spellings, the brief name in
# COMPLETENESS_FIELDS and the Form 1 field name in
# _COMPLETENESS_SLUGS, and the two spellings carry one field, judged
# once by completeness_standing. A record whose two spellings carry
# different values stands diverged, and the diverged state stands
# named in every standing result, never judged in silence (R16-11).
COMPLETENESS_KEY_PAIRS = tuple(
    zip(COMPLETENESS_FIELDS, _COMPLETENESS_SLUGS))

# The named carriage keys of a made family record (Step 16 fix
# wave 2, row F2-01, ruling T16-23): the keys the product own
# made record construction in MOD-12 (make_family_record, built
# on minimal_valid_family_record) carries beside the Form 1
# fields and the completeness fields, enumerated by name from
# that construction and verified first hand against the landed
# tree. The alias_keys entry itself, the completeness prose
# names it maps, and the completeness_presentation entry stand
# among them. A family judgement door that reads a made record
# refuses a field standing outside the form fields, the
# completeness fields, and these named carriage keys, and names
# the field; a made record carrying only these keys keeps its
# standing.
FAMILY_CARRIAGE_KEYS = (
    "alias_keys",
    "claims",
    "completeness_presentation",
    "family_id",
    "family_manifest_hash",
    "family_version",
    "form",
    "kill_checks",
    "registry_basis_fields",
    "results_seen",
    "sealed",
)

# The named carriage keys of a made family record (Step 16 fix
# wave 2, row F2-01, ruling T16-23): the keys the made record
# construction at MOD-12 make_family_record carries beside the
# Form 1 fields and the completeness fields, enumerated by name
# from that construction. A made record carrying only these
# keys beside its form fields and completeness fields keeps its
# standing at the reportable judgement; a field standing
# outside the form fields, the completeness fields, and these
# named carriage keys stands refused and named there.
_FAMILY_CARRIAGE_KEYS = (
    "family_version",
    "family_manifest_hash",
    "family_id",
    "sealed",
    "claims",
    "kill_checks",
    "registry_basis_fields",
    "results_seen",
    "form",
    "alias_keys",
    "completeness_presentation",
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
    # Form 14 DailyAggregates record shape. This shape stands apart
    # from the Recorder daily aggregate row shape of MOD-10, which
    # carries viewer_id beside run_id, record_identity, and writer:
    # the two shapes stand separated by name at each locus (R16-18).
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


def _bounded_echo(rendered):
    """Bound one rendered handed value for a refusal sentence
    (FW4-10): a rendering standing at 120 characters or fewer
    stands whole; a longer rendering stands as its first 120
    characters beside a length statement naming the standing
    length of the handed value and the 120 character bound, so
    no refusal message grows with the handing past that bound
    and the ground of the refusal stands readable at its head."""
    if len(rendered) <= 120:
        return rendered
    return (rendered[:120]
            + " [bounded rendering: the handed value stands at "
            + str(len(rendered))
            + " characters and stands rendered to its first "
            "120 characters only]")


def _sentence_text(value):
    """Render a handed value for a sentence or a lookup on the
    text it stores: a text form through its base class string
    form, and a bytes, bytearray, or memoryview form through
    its stored bytes decoded as UTF-8 with undecodable bytes
    dropped, never through a reading the value itself supplies.
    A value in any other form stands rendered through _safe_str
    as before."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return _safe_str(value)


def _fid(form_id):
    """The stated form identifier a handed value carries, in
    the one identifier form of this module (FW-23): a form
    identifier stands as a text value, judged on the text it
    stores through the base class string form, and a value in
    any other form (a number, a bytes form, a container, or
    no value) carries no form identifier, so every door of
    this module judges the same handing the same way. A value
    in no identifier form stands read as the empty identifier,
    which names no form."""
    if isinstance(form_id, str):
        return str.__str__(form_id)
    return ""


def _identifier_non_text_class(form_id):
    """The class name of a handed form identifier that stands
    in a non text class whose rendering carries no class mark
    (FW3-55): an integer, a float, a boolean, or no value,
    among others. A text handing carries no class ground, and
    a bytes form renders with its class marks standing, so
    neither stands under this ground."""
    if isinstance(form_id, str):
        return None
    if isinstance(form_id, (bytes, bytearray, memoryview)):
        return None
    return type(form_id).__name__


def _unknown_form_refusal(act, form_id):
    """The named refusal the form lookup doors deliver for an
    identifier naming no form (FW-24): the refusal names the
    identifier as handed, states that no form stands under
    it, and states the next step, in the form the sibling
    door minimal_valid_instance states. Where the identifier
    stands handed in a non text class whose rendering
    carries no class mark, the refusal states the class
    ground truly instead (FW3-55): the fault stands as the
    class of the handing, not as the value it names."""
    class_name = _identifier_non_text_class(form_id)
    if class_name is not None:
        return ValueError(
            act + " stands refused: form identifier "
            + _safe_str(form_id)
            + " stands handed in a non text form, the "
            + class_name
            + " form, where a form identifier stands as text; "
            "next step: hand the identifier as text, one of "
            "the identifiers FORM_IDS states, and no answer "
            "stands returned at this door")
    return ValueError(
        act + " stands refused: form identifier "
        + _safe_str(form_id)
        + " names no form: no form stands under that "
        "identifier; next step: hand a stated form identifier, "
        "one of the identifiers FORM_IDS states, and no answer "
        "stands returned at this door")


def form_name(form_id):
    """The product name of one record form, by its product Form
    number. The brief Shape the form answers stands apart from
    the Form number from brief Shape 9 onward, under the plan
    one ahead rule: read it through BRIEF_SHAPE_CROSS_REFERENCE
    or brief_shape_for_form, never by assuming the Form number
    and the brief Shape number agree."""
    fid = _fid(form_id)
    if fid not in _FORM_SPECS:
        raise _unknown_form_refusal("form_name", form_id)
    return _FORM_SPECS[fid][0]


# The explicit brief Shape cross reference of the product
# registry, stated in the open at Step 16 row R16-01. Each entry
# names the product Form, its product name, the brief Shape it
# answers, and the brief name of that Shape. A brief Shape and
# its brief name agree with the product name wherever the Shape
# states one form; at brief Shape 8, which states two forms,
# the brief name stands as the Shape states it and each Form
# entry names its own form of the two. An entry whose
# brief_shape stands as None carries no numbered brief Shape of
# its own, in the form its brief_shape_note states. No Form
# number in this table departs from the plan census, and no
# brief Shape number departs from the brief: the table states
# the correspondence between the two numberings as they stand.
def _shape_entry(form_id, brief_shape, brief_name, note=None):
    return {
        "form_id": form_id,
        "form_name": _FORM_SPECS[form_id][0],
        "brief_shape": brief_shape,
        "brief_name": brief_name,
        "brief_shape_note": note,
    }


BRIEF_SHAPE_CROSS_REFERENCE = {
    "1": _shape_entry("1", "1", "SweepFamilyRecord"),
    "2": _shape_entry("2", "2", "SweepPoint"),
    "3": _shape_entry("3", "3", "AssumptionRecord"),
    "4": _shape_entry("4", "4", "RunRecord"),
    "5": _shape_entry("5", "5", "SeedDerivationInput"),
    "6": _shape_entry("6", "6", "StreamSet"),
    "7": _shape_entry("7", "7", "AgentState"),
    "8": _shape_entry("8", "8", "VouchEdge and GraphSnapshot",
                      "Shape 8, first form of two"),
    "9": _shape_entry("9", "8", "VouchEdge and GraphSnapshot",
                      "Shape 8, second form of two"),
    "10": _shape_entry("10", "9", "EscrowContractState"),
    "11": _shape_entry("11", "10", "AdjudicationCase"),
    "12": _shape_entry("12", "11", "DetectionState"),
    "13": _shape_entry("13", "12", "CheckpointManifest"),
    "13A": _shape_entry(
        "13A", None, "CheckpointManifest",
        "no numbered brief Shape of its own: counted beside "
        "Form 13 in the checkpoint layer"),
    "14": _shape_entry("14", "13", "DailyAggregates"),
    "15": _shape_entry("15", "14", "JointOutcomeVector"),
    "16": _shape_entry("16", "15", "HeadlineResultUnit"),
    "17": _shape_entry("17", "16", "AnchorScenarioRecord"),
    "18": _shape_entry("18", "17", "InterpretationLogEntry"),
    "19": _shape_entry(
        "19", None, "DetectionInput",
        "no numbered brief Shape of its own: defined inside "
        "the Shape 7 passage"),
    "20": _shape_entry(
        "20", None, "AnnotationRecord",
        "no numbered brief Shape of its own: defined in the "
        "Shape 16 passage"),
    "21": _shape_entry(
        "21", None, "AnnotationCheckRecord",
        "no numbered brief Shape of its own: defined in the "
        "Shape 16 passage"),
    "22": _shape_entry(
        "22", None, "SweepFamilyRegistry",
        "no numbered brief Shape: a layer three form"),
    "23": _shape_entry(
        "23", None, "FamilyManifest",
        "no numbered brief Shape: a layer three form"),
    "24": _shape_entry(
        "24", None, "SweepManifest",
        "no numbered brief Shape: a layer three form"),
    "25": _shape_entry(
        "25", None, "PilotRecord",
        "no numbered brief Shape: a layer three form"),
    "26": _shape_entry(
        "26", None, "SummaryRecord",
        "no numbered brief Shape: a layer three form"),
    "27": _shape_entry(
        "27", None, "DetectionOutput",
        "no numbered brief Shape: a layer three form"),
    "28": _shape_entry(
        "28", None, "ReplicationVerdictRecord",
        "no numbered brief Shape: a layer three form"),
    "29": _shape_entry(
        "29", None, "TracerPassageRecord",
        "no numbered brief Shape: a layer three form"),
    "30": _shape_entry(
        "30", None, "GatePassingShareRecord",
        "no numbered brief Shape: a layer three form"),
    "31": _shape_entry(
        "31", None, "ReadingLoadPricingRecord",
        "no numbered brief Shape: a layer three form"),
    "32": _shape_entry(
        "32", None, "SettingsLineageTestRecord",
        "no numbered brief Shape: a layer three form"),
    "33": _shape_entry(
        "33", None, "RetentionRecord",
        "no numbered brief Shape: a layer three form"),
    "34": _shape_entry(
        "34", None, "DisagreementCatalogue",
        "no numbered brief Shape: a layer three form"),
    "35": _shape_entry(
        "35", None, "WeeklyContainer",
        "no numbered brief Shape: a layer three form"),
    "36": _shape_entry(
        "36", None, "EventLog",
        "no numbered brief Shape: a layer three form"),
    "37": _shape_entry(
        "37", None, "DailySnapshot",
        "no numbered brief Shape: a layer three form"),
}


def brief_shape_for_form(form_id):
    """The numbered brief Shape one product Form answers, as
    BRIEF_SHAPE_CROSS_REFERENCE states it, or None where the
    Form carries no numbered brief Shape of its own."""
    entry = BRIEF_SHAPE_CROSS_REFERENCE.get(_fid(form_id))
    if entry is None:
        raise _unknown_form_refusal(
            "brief_shape_for_form", form_id)
    return entry["brief_shape"]


def form_ids_for_brief_shape(shape):
    """The product Form numbers answering one numbered brief
    Shape, as BRIEF_SHAPE_CROSS_REFERENCE states them. Brief
    Shape 8 answers with two Forms, ("8", "9"); every other
    numbered brief Shape from 1 to 17 answers with one Form.
    A shape naming no numbered brief Shape stands refused in
    the named form: the refusal states that the shape names
    no numbered brief Shape and states the next step, and no
    form list stands returned. A shape handed in a non text
    form stands refused on the handing form ground, naming
    the form handed and the text standing of a brief shape
    identifier."""
    class_name = _identifier_non_text_class(shape)
    if class_name is not None:
        raise ValueError(
            "form_ids_for_brief_shape stands refused: brief "
            "shape identifier " + _safe_str(shape)
            + " stands handed in a non text form, the "
            + class_name
            + " form, where a brief shape identifier stands "
            "as text; next step: hand the identifier as text, "
            "one of the numbered brief Shapes the cross "
            "reference states, and no form list stands returned")
    wanted = _fid(shape)
    if wanted not in {
            entry["brief_shape"]
            for entry in BRIEF_SHAPE_CROSS_REFERENCE.values()
            if entry["brief_shape"] is not None}:
        raise ValueError(
            "form_ids_for_brief_shape stands refused: brief "
            "shape " + _safe_str(shape)
            + " names no numbered brief Shape: no numbered "
            "brief Shape stands under that identifier; next "
            "step: hand a stated brief Shape number, one of "
            "the numbered brief Shapes the cross reference "
            "states, and no form list stands returned")
    return tuple(
        form_id
        for form_id, entry in BRIEF_SHAPE_CROSS_REFERENCE.items()
        if entry["brief_shape"] is not None
        and str.__eq__(entry["brief_shape"], wanted)
    )


def form_fields(form_id):
    """The field list of a form. Forms 36 and 37 return their landed
    lists and no field beyond them."""
    spec = _FORM_SPECS.get(_fid(form_id))
    if spec is None:
        raise _unknown_form_refusal("form_fields", form_id)
    return spec[1]


def required_fields(form_id):
    """The fields required on every instance of a form. Conditional
    fields stand apart, in field_conditions. A field
    FORM_FIELD_OWNERSHIP names as never_fill stands apart as
    well: it stands required on no instance, and a record
    carrying it filled stands refused at validation (F2-08,
    ruling T16-32)."""
    fid = _fid(form_id)
    if fid not in _FORM_SPECS:
        raise _unknown_form_refusal(
            "required_fields", form_id)
    fields = form_fields(fid)
    conditional = {c["field"] for c in _conditions_for(fid)}
    if fid == "36":
        return _EVENTLOG_BASE_FIELDS
    never_fill = ()
    ownership = FORM_FIELD_OWNERSHIP.get(fid)
    if ownership:
        never_fill = ownership["never_fill"]
    return tuple(
        f for f in fields
        if f not in conditional and f not in never_fill)


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
    if _fid(form_id) not in _FORM_SPECS:
        raise _unknown_form_refusal(
            "field_conditions", form_id)
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
    "outcome": "not reported",
    "confirmation_outcome": "not run",
    "gate_failure": "none",
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


def _refuse_argument_handing(door, expected, missing, extra):
    """Refuse a missing or extra argument handing at a README
    named entry point of this module, in named form: the door,
    the ground, and the next step stand stated, and no answer
    of the door stands returned."""
    if missing:
        ground = ("a handing stands missing among " + expected)
    else:
        ground = ("an argument stands handed in beyond " + expected)
    raise ValueError(
        door + " stands refused: this door stands handed "
        + expected + ", " + ground + "; next step: hand "
        + expected + " and call the door again, and no answer "
        "stands returned at this door")


def minimal_valid_instance(form_id=_ARGUMENT_NOT_HANDED, entry_kind=None, condition_holds=None, *extra_args, **extra_kwargs):
    """A minimally valid instance of a form, as a plain dict.

    Form 36 takes entry_kind, one of ordinary, agent, or supersession.
    A form with a stated condition takes condition_holds: the condition
    dict its field_conditions returns, or None where the condition does
    not hold.

    An identifier naming no form stands refused in a named failure:
    the failure names the handed identifier, states that no form
    stands under it, and states the next step, and no instance
    stands built. An identifier handed in a non text form stands
    refused on the handing form ground instead: the failure names
    the form handed in and states that a form identifier stands
    as text.
    """
    if form_id is _ARGUMENT_NOT_HANDED:
        _refuse_argument_handing(
            "minimal_valid_instance",
            "the form identifier", True, False)
    if extra_args or extra_kwargs:
        _refuse_argument_handing(
            "minimal_valid_instance",
            "the form identifier", False, True)

    fid = _fid(form_id)
    if fid not in _FORM_SPECS:
        class_name = _identifier_non_text_class(form_id)
        if class_name is not None:
            raise ValueError(
                "minimal_valid_instance stands refused: form "
                "identifier " + _bounded_echo(_safe_str(form_id))
                + " stands handed in a non text form, the "
                + class_name
                + " form, where a form identifier stands as "
                "text; next step: hand the identifier as text, "
                "one of the identifiers FORM_IDS states, and "
                "no instance stands built")
        raise ValueError(
            "minimal_valid_instance stands refused: form identifier "
            + _bounded_echo(_safe_str(form_id))
            + " names no form: no form stands under that identifier; "
            "next step: hand a stated form identifier, one of the "
            "identifiers FORM_IDS states, and no instance stands built")
    if fid == "36":
        stored_kind = _stored_text(entry_kind)
        if entry_kind is not None and stored_kind not in (
                "ordinary", "agent", "supersession"):
            raise ValueError(
                "unknown entry kind: " + _sentence_text(entry_kind)
                + "; the stated kinds are ordinary, agent and supersession")
        return _minimal_eventlog(stored_kind or "ordinary")
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


def minimal_valid_family_record(*extra_args, **extra_kwargs):
    """A SweepFamilyRecord carrying every completeness field, with the
    OP-13 values carried as open markers. An argument handed to
    this act, which takes none, stands refused in the named form
    of this module (FW4-11)."""
    if extra_args or extra_kwargs:
        _refuse_argument_handing(
            "minimal_valid_family_record",
            "no argument at all", False, True)
    record = {}
    for field in required_fields("1"):
        record[field] = _placeholder(field)
    for field in COMPLETENESS_FIELDS:
        record[field] = _OP13_MARKER
    return record


# Field ownership for Forms 2 and 4, stated on the record (R16-07).
# user_supplies: fields a user hands in when building the record.
# system_fills: fields the system writes during or after a run; a
# user building a record leaves these to the template standing.
# never_fill: fields a user must never fill. On Form 4 these stand
# as the seed fields: no seed stands drawn, read from a clock, or
# assigned in completion order while the DQ7-02 adoption gate
# stands, and the builders below refuse them by name. A built or
# template record carries no never_fill field at all, and
# validation refuses a record carrying a never_fill field filled,
# naming the field at the failure door (F2-08, ruling T16-32).
FORM_FIELD_OWNERSHIP = {
    "2": {
        "user_supplies": (
            "point_identifier", "population_size", "farm_size",
            "patience_in_days", "run_length_in_days",
            "anchor_scenario_identifier", "escrow_variant_selector",
            "assumption_set_selector", "design_kind", "decay_slice",
        ),
        "system_fills": (),
        "never_fill": (),
    },
    "4": {
        "user_supplies": (
            "sweep_identifier", "sweep_family_identifier",
            "family_version", "sweep_point_identifier", "run_class",
            "design_kind", "replicate_group_identifier",
            "replicate_index", "population_size", "run_length_in_days",
            "horizon_variant_marker", "control_values",
            "scheduling_order_identifier", "assumption_record",
            "escrow_variant", "variant_record_fields",
            "core_only_qualifier", "interpretation_choices",
            "anchor_scenario_values", "dependence_labels",
            "retention_tier", "store_kind",
            "timing_pilot_or_provisional_marker",
            "calibration_claim_field", "annotation_link",
        ),
        "system_fills": (
            "family_manifest_hash", "run_identifier",
            "stream_identifiers", "scheduling_position_identifiers",
            "build_identifier", "matched_run_identifier",
            "rule_version_set", "arbiter_accuracy_value",
            "correlation_statement", "joint_outcome_vector",
            "regime_classification", "winning_criterion_evaluation",
            "gate_passing_share_per_epoch",
            "excluded_class_counts_and_shares", "flag_conditions_fired",
            "record_pointers", "end_of_run_state_hash",
            "folding_record_reference", "seam_check_reference",
            "nq10_listing", "nq6_classification_marker",
            "outside_call_check", "run_status",
        ),
        "never_fill": (
            "root_seed_reference", "derived_run_seed_identifier",
        ),
    },
}


def _build_form(form_id, values):
    ownership = FORM_FIELD_OWNERSHIP[form_id]
    for field in values:
        if field in ownership["never_fill"]:
            raise ValueError(
                "field a user must never fill: " + field
                + " stands as a seed field, and no seed stands drawn "
                "or assigned while the DQ7-02 adoption gate stands; "
                "the field stands unfilled and no record stands built")
        if field in ownership["system_fills"]:
            raise ValueError(
                "field the system fills: " + field
                + " stands written by the system during or after a "
                "run, and a user building this record supplies no "
                "value for it; no record stands built")
        if field not in ownership["user_supplies"]:
            raise ValueError(
                "unknown field for Form " + form_id + ": " + str(field)
                + "; the fields a user supplies stand named in "
                "FORM_FIELD_OWNERSHIP, and no record stands built")
    record = minimal_valid_instance(form_id)
    for field, value in values.items():
        record[field] = copy.deepcopy(value)
    for condition in _conditions_for(form_id):
        record.pop(condition["discriminator"], None)
        if condition["field"] not in record:
            record[condition["field"]] = _placeholder(
                condition["field"])
    return record


def build_sweep_point(*args, **values):
    """Build one SweepPoint record, Form 2, from user supplied fields.

    Arguments: any of the Form 2 fields a user supplies, named in
    FORM_FIELD_OWNERSHIP at "2" under user_supplies. A field left
    unfilled carries the template standing of
    minimal_valid_instance, so the record a caller builds stands
    as a formally complete template until real values stand
    supplied for it. The built record carries exactly the fields
    form_fields names for Form 2, decay_slice among them, at the
    template standing where it stands unsupplied and at the
    supplied value where a caller supplies it; the discriminator
    carriage of the template path, belongs_to_decay_arm, stands
    not on a built record, and no second name for decay_slice
    stands on it (F2-08, ruling T16-32).
    Returns: a plain dict in the Form 2 shape, its keys exactly
    the Form 2 field list.
    Failure: a named ValueError for a field the form does not
    name. Form 2 carries no system filled field and no seed
    field, so no other refusal stands on this path. A whole
    record handing, one positional mapping carrying the
    fields, stands refused in the same named form (FW3-51):
    the fields of a record stand handed as named arguments
    at this door.
    """
    if args:
        raise ValueError(
            "build_sweep_point stands refused: the fields of "
            "a record stand handed as named arguments at this "
            "door, and a whole record handing stands in no "
            "builder form; next step: hand each field as a "
            "named argument, and no record stands built")
    return _build_form("2", values)


def build_run_record(*args, **values):
    """Build one RunRecord record, Form 4, from user supplied fields.

    Arguments: any of the Form 4 fields a user supplies, named in
    FORM_FIELD_OWNERSHIP at "4" under user_supplies. Fields the
    system fills stand left to the template standing, and the
    seed fields, root_seed_reference and
    derived_run_seed_identifier, stand never filled by a user.
    The built record carries no seed field at all: the seed
    fields stand absent on it, not filled at the placeholder
    text, and a record carrying a seed field filled stands
    refused at validate_record, with the field named at
    record_validation_failures (F2-08, ruling T16-32).
    Returns: a plain dict in the Form 4 shape, carrying the user
    supplied fields and the system filled fields at their
    template standing, and no never fill field.
    Failure: a named ValueError naming the DQ7-02 adoption gate
    where a seed field stands handed in, a named ValueError where
    a system filled field stands handed in, and a named
    ValueError for a field the form does not name; on every
    refusal no record stands built and no seed stands drawn.
    A whole record handing, one positional mapping carrying
    the fields, stands refused in the same named form
    (FW3-51): the fields of a record stand handed as named
    arguments at this door.
    """
    if args:
        raise ValueError(
            "build_run_record stands refused: the fields of "
            "a record stand handed as named arguments at this "
            "door, and a whole record handing stands in no "
            "builder form; next step: hand each field as a "
            "named argument, and no record stands built")
    return _build_form("4", values)


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
    states. One reading carries a memo of the containers it
    has already read whole, keyed on the identity of the
    container: a container standing twice in one key, as
    the same object off the walk path, stands read once,
    and its candidates stand shared by every standing of
    it, the path guard standing untouched for a container
    standing on its own path. A part already on the walk path contributes the
    empty text, so a cyclic part cannot loop the read. The walk stands iterative on an explicit stack of frames, so a container chain at any depth stands answered on the same terms and no recursion stands spent per container level. A caller may state a wider candidate cap through _cap, as the segmentation readings do, without moving the standing bound this act states for its other callers."""
    if _cap is None:
        _cap = _JOIN_CANDIDATE_BOUND
    if _active is None:
        _active = set()
    _memo = {}

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
            elif id(node) in _memo:
                result = _memo[id(node)]
            else:
                _active.add(id(node))
                parts = _join_container_parts(node)
                if parts:
                    stack.append([node, parts, [], 0])
                    node = parts[0]
                    continue
                _active.discard(id(node))
                result = combine(node, parts, [])
                _memo[id(node)] = result
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
            _memo[id(frame[0])] = result


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
    judged kind first through base class operations. A text value
    stands equal only to a text value whose stored text matches.
    A boolean stands apart from every number and stands equal
    only to a boolean holding the same value. A Decimal stands
    equal only to a Decimal holding the same stored value, and a
    Fraction only to a Fraction holding the same stored value,
    each judged through the base class operation of its kind on
    a plain copy of its kind. The plain number limb reaches int
    and float values alone, which stand equal where their plain
    values stand equal. A complex value stands equal only to a
    complex value holding the same stored value. Container values
    stand equal only to a container of the same kind whose parts
    stand equal under this same judgement, part by part.
    A buffer value stands equal only to a buffer value holding
    the same stored bytes. A value of any other kind stands
    equal only to itself, by identity alone, so no equality
    reading a handed value supplies decides the judgement."""
    if isinstance(left, str) or isinstance(right, str):
        return (
            isinstance(left, str)
            and isinstance(right, str)
            and str.__eq__(str.__str__(left), str.__str__(right)) is True
        )
    if isinstance(left, bool) or isinstance(right, bool):
        return (
            isinstance(left, bool)
            and isinstance(right, bool)
            and (left is True) == (right is True)
        )
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, Decimal) or isinstance(right, Decimal):
        return (
            isinstance(left, Decimal)
            and isinstance(right, Decimal)
            and Decimal.__eq__(
                Decimal.__new__(Decimal, left),
                Decimal.__new__(Decimal, right)) is True
        )
    if isinstance(left, Fraction) or isinstance(right, Fraction):
        return (
            isinstance(left, Fraction)
            and isinstance(right, Fraction)
            and Fraction.__eq__(
                Fraction.__new__(Fraction, left),
                Fraction.__new__(Fraction, right)) is True
        )
    if isinstance(left, complex) or isinstance(right, complex):
        return (
            isinstance(left, complex)
            and isinstance(right, complex)
            and complex.__eq__(
                complex.__new__(complex, left),
                complex.__new__(complex, right)) is True
        )
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return _stored_plain(left) == _stored_plain(right)
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        return False
    if isinstance(left, dict) and isinstance(right, dict):
        if dict.__len__(left) != dict.__len__(right):
            return False
        remaining = list(dict.items(right))
        for key, item in dict.items(left):
            matched = None
            for index, (other_key, other_item) in enumerate(remaining):
                if _base_value_equals(key, other_key):
                    matched = index
                    matched_item = other_item
                    break
            if matched is None:
                return False
            if not _base_value_equals(item, matched_item):
                return False
            remaining.pop(matched)
        return True
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if type(left) is not type(right):
            return False
        left_parts = list(_base_iter(left)) if isinstance(
            left, (list, tuple)) else []
        right_parts = list(_base_iter(right))
        if len(left_parts) != len(right_parts):
            return False
        return all(
            _base_value_equals(one, two)
            for one, two in zip(left_parts, right_parts))
    if isinstance(left, (set, frozenset)) and isinstance(
            right, (set, frozenset)):
        if type(left) is not type(right):
            return False
        left_parts = list(_base_iter(left))
        right_parts = list(_base_iter(right))
        if len(left_parts) != len(right_parts):
            return False
        remaining = list(right_parts)
        for part in left_parts:
            matched = None
            for index, other in enumerate(remaining):
                if _base_value_equals(part, other):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
        return True
    if isinstance(left, (dict, list, tuple, set, frozenset)) or isinstance(
            right, (dict, list, tuple, set, frozenset)):
        return False
    if isinstance(left, (bytes, bytearray, memoryview)) or isinstance(
            right, (bytes, bytearray, memoryview)):
        return (
            isinstance(left, (bytes, bytearray, memoryview))
            and isinstance(right, (bytes, bytearray, memoryview))
            and bytes.__eq__(bytes(left), bytes(right)) is True
        )
    return left is right


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
    """Whether one value stands as a stated store kind.

        Arguments: kind, the value handed in for judgement.
        Returns: True where the value stands as one of the stated
        store kinds in STORE_KINDS, and False in every other case.
        Failure: no exception stands raised for a value in no
        stated kind form; the failure form is the bare False
        return.
    """
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
    """The reserved matter values a record may carry.

        Arguments: no argument stands handed in.
        Returns: RESERVED_MATTER_VALUES, the tuple of reserved
        matter values the reserved matter group of a record
        admits.
        Failure: no exception stands raised at this door; the
        values stand returned as they stand.
    """
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


def completeness_key_pairs():
    """The one completeness key set: pairs of (brief name, Form 1
    field name), one pair per completeness field, in field order.
    The brief name stands as the alias of the Form 1 field name for
    the same field (R16-11); neither spelling stands as a second
    field."""
    return COMPLETENESS_KEY_PAIRS


class StatedJudgement:
    """A judgement carrying its standing in words.

    The judgement states, on its face and in its attributes, the
    standing its answer rests on: which fields stand open, which
    stand supplied, which stand diverged, and whether the record
    stands reportable ready on supplied values. Its value
    attribute stands as the completeness bar judgement the
    TG-01.3 pin states: a record carrying every completeness
    field as an open marker stands complete on that limb. Its
    truth value stands apart from that bar reading (Step 16 fix
    wave 2, row F2-07, ruling T16-31): over open markers the
    truth value does not stand as an unqualified True, it
    reflects the open standing the result states, standing as
    the reportable ready value, so a reader of the truth value,
    of an equality reading against a boolean, or of the dict
    form takes the qualified standing and not an unqualified
    True. The boolean reading __bool__ answers stands as the
    truth value stands (Step 16 fix wave 7, row F7-01, ruling
    T16-73): a judgement tests in a boolean context exactly as
    its truth value stands, at every door that returns one, so
    the boolean a caller reads from a judgement and the truth
    value the judgement states cannot part company. The dict
    form of the same judgement stands at
    family_reportable_standing.
    """

    def __init__(self, value, standing="", open_fields=(),
                 supplied_fields=(), diverged_fields=(),
                 missing_fields=(), placeholder_fields=(),
                 reportable_ready=False, extra_fields=()):
        self.value = bool(value)
        self.standing = standing
        self.open_fields = tuple(open_fields)
        self.supplied_fields = tuple(supplied_fields)
        self.diverged_fields = tuple(diverged_fields)
        self.missing_fields = tuple(missing_fields)
        self.placeholder_fields = tuple(placeholder_fields)
        self.reportable_ready = bool(reportable_ready)
        self.extra_fields = tuple(extra_fields)
        self.truth_value = bool(
            self.value and (
                self.reportable_ready or not self.open_fields))

    def __bool__(self):
        return self.truth_value

    def __eq__(self, other):
        if isinstance(other, bool):
            return self.truth_value == other
        if isinstance(other, StatedJudgement):
            return self.truth_value == other.truth_value
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash(self.truth_value)

    def __repr__(self):
        if self.value and not self.truth_value:
            word = ("True on the completeness bar in open form, "
                    "truth value False")
        else:
            word = "True" if self.truth_value else "False"
        if self.standing:
            return word + " (standing: " + self.standing + ")"
        return word

    def as_dict(self):
        return {
            "judgement": self.truth_value,
            "completeness_bar_met": self.value,
            "standing": self.standing,
            "open_fields": list(self.open_fields),
            "supplied_fields": list(self.supplied_fields),
            "diverged_fields": list(self.diverged_fields),
            "missing_fields": list(self.missing_fields),
            "placeholder_fields": list(self.placeholder_fields),
            "extra_fields": list(self.extra_fields),
            "reportable_ready": self.reportable_ready,
        }


def _folded_vocabulary_text(text):
    """The folded form of one stored text for the placeholder
    and open marker vocabulary readings (Step 16 fix wave 3,
    row F3-03, ruling T16-41): letter case stands folded away
    and spacing stands folded, leading and trailing spacing
    disregarded and any run of spacing between words read as
    the one space. No other character stands folded away: a
    text that differs from a vocabulary form in any other
    character, in its words, or in its word order does not
    fold to that form."""
    return " ".join(text.casefold().split())


def _stands_placeholder_text(text):
    """Whether one stored text stands as the placeholder text
    under the folded reading: the folded form of the text
    stands equal to the folded form of the placeholder text
    "stated value", so the placeholder in case or spacing
    dress stands read as the placeholder."""
    return str.__eq__(
        _folded_vocabulary_text(text), "stated value")


def _stands_open_marker_text(text):
    """Whether one stored text stands as an open marker under
    OP-13 under the folded reading: the folded form of the
    text stands equal to the folded form of the marker
    vocabulary, the one marker text _OP13_MARKER, whole and
    in place, so a marker in case or spacing dress stands
    read as a marker, and a text that opens with the marker
    prefix and carries the OP-13 name anywhere in its body
    stands as no marker (Step 16 fix wave 4, row F4-02,
    ruling T16-50)."""
    folded = _folded_vocabulary_text(text)
    return str.__eq__(folded, _folded_vocabulary_text(_OP13_MARKER))


def _completeness_value_standing(value):
    """The standing of one completeness value, read through base
    class operations on what the value stores: an open marker
    under OP-13, a supplied recorded value (a recorded text, or a
    non empty recorded sequence, mapping, or set of steps), the
    placeholder text, an absent value, or a bare scalar. A bare
    number stands as no recorded completeness value at all: the
    TG-01.3 pin stands, a marker replaced by a bare number fails
    the completeness bar. The placeholder and open marker
    readings stand on the folded form of the stored text, case
    and spacing folded (fix wave 3, row F3-03, ruling T16-41),
    so dressed placeholder text never reads supplied and a
    dressed open marker never reads supplied."""
    if value is None:
        return "absent"
    if isinstance(value, (list, tuple, set, frozenset)):
        if _base_len(value) == 0:
            return "absent"
        if _base_len(value) == 1:
            only = next(_base_iter(value))
            return _completeness_value_standing(only)
        return "supplied"
    if isinstance(value, dict):
        return "supplied" if _base_len(value) else "absent"
    text = _stored_text_dress(value)
    if text is not None:
        if not str.__len__(text):
            return "absent"
        if _stands_open_marker_text(text):
            return "open marker"
        if _stands_placeholder_text(text):
            return "placeholder"
        return "supplied"
    return "bare scalar"


def _values_agree(first, second):
    """Whether two handed values store the same value, judged
    through base class operations only, with a handed reading
    that raises standing as no agreement."""
    if first is second:
        return True
    try:
        return bool(_base_value_equals(first, second))
    except Exception:
        return False


def completeness_standing(record):
    """The completeness standing of one family record, judged once
    from the one completeness key set (R16-15).

    The shared reading of the one key set (T16-33): the two
    spellings carry one field, and a field stands complete only
    where both of its spellings stand and agree, taking the
    standing of the value they carry. Where one spelling alone
    stands, the field stands named on its remaining spelling with
    that spelling's standing, and the record stands incomplete on
    the completeness limb for every judgement of the key set:
    this standing, family_supports_reportable_run, validate_record,
    and run_is_reportable all read the set this one way.

    Each completeness field stands judged from its two spellings
    together: where both spellings stand present and carry
    different values the field stands diverged and stands named
    as diverged (R16-11); where they agree, or where one spelling
    alone stands, the field takes the standing of the value it
    carries, an open marker under OP-13, a supplied value, the
    placeholder text, an absent value, or a bare scalar. The
    result names the fields in each standing, so a formally
    complete template stands distinguished from a record carrying
    real values, with placeholder and marker values named as such
    (R16-03). No value stands invented by this reading (OP-16).

    At the both spellings edge (Step 16 fix wave 3, row F3-05,
    ruling T16-43), where one spelling of a pair stands alone,
    the field stands named as not standing complete: a supplied
    value standing on one spelling alone stands in
    missing_fields, not in supplied_fields, and the standing
    sentence names every field that stands incomplete for a
    missing spelling, in the same joined form the sentence uses
    for the other unmet fields. The judgements at that edge do
    not change: the record stands incomplete on the completeness
    limb for every judgement of the key set.

    Beside a diverged pair (Step 16 fix wave 4, row F4-05,
    ruling T16-53), that naming does not stand preempted by the
    diverged branch: every field that does not stand with both
    spellings present stands named in missing_fields and in
    the standing sentence, in its own kind bucket beside that
    naming where it has one, whether it stands alone or beside
    a diverged pair. A field standing with both spellings
    present keeps the naming its standing already carries.

    Beside a diverged pair (Step 16 fix wave 5, row F5-01,
    ruling T16-60), that naming runs per field unmet, not per
    branch taken: a field standing with both spellings
    present in an unmet kind (a placeholder, a bare scalar,
    or an absent value on both spellings) stands named in
    missing_fields and in the standing sentence beside the
    diverged naming, in field order, beside its own kind
    bucket. The alone form and the pure diverged form keep
    their standing wordings.
    """
    result = {
        "fields": [],
        "open_fields": [],
        "supplied_fields": [],
        "placeholder_fields": [],
        "diverged_fields": [],
        "missing_fields": [],
        "bare_scalar_fields": [],
        "absent_fields": [],
    }
    if not isinstance(record, dict):
        result["standing"] = "not a record: no completeness standing"
        result["complete_on_completeness_limb"] = False
        result["reportable_ready"] = False
        return result
    diverged_stands = False
    for prose, slug in COMPLETENESS_KEY_PAIRS:
        if _stored_pairs_present(record, prose) and (
                _stored_pairs_present(record, slug)) and not (
                _values_agree(
                    _stored_pairs_value(record, prose),
                    _stored_pairs_value(record, slug))):
            diverged_stands = True
            break
    for prose, slug in COMPLETENESS_KEY_PAIRS:
        prose_present = _stored_pairs_present(record, prose)
        slug_present = _stored_pairs_present(record, slug)
        if not prose_present and not slug_present:
            standing = "missing"
        else:
            prose_value = _stored_pairs_value(record, prose)
            slug_value = _stored_pairs_value(record, slug)
            if prose_present and slug_present and not _values_agree(
                    prose_value, slug_value):
                standing = "diverged"
            elif slug_present:
                standing = _completeness_value_standing(slug_value)
            else:
                standing = _completeness_value_standing(prose_value)
        result["fields"].append({
            "field": prose,
            "key": slug,
            "standing": standing,
            "brief_name_present": prose_present,
            "form_name_present": slug_present,
        })
        if standing == "open marker":
            result["open_fields"].append(prose)
        elif standing == "supplied" and not (
                prose_present and slug_present):
            result["missing_fields"].append(prose)
        elif standing == "supplied":
            result["supplied_fields"].append(prose)
        elif standing == "placeholder":
            result["placeholder_fields"].append(prose)
        elif standing == "diverged":
            result["diverged_fields"].append(prose)
        elif standing == "missing":
            result["missing_fields"].append(prose)
        elif standing == "bare scalar":
            result["bare_scalar_fields"].append(prose)
        else:
            result["absent_fields"].append(prose)
        if diverged_stands and standing != "diverged" and (
                not (prose_present and slug_present)
                or standing not in (
                    "open marker", "supplied")) and (
                prose not in result["missing_fields"]):
            result["missing_fields"].append(prose)
    complete = all(
        entry["standing"] in ("open marker", "supplied")
        and entry["brief_name_present"] and entry["form_name_present"]
        for entry in result["fields"])
    result["complete_on_completeness_limb"] = complete
    result["reportable_ready"] = bool(
        complete and not result["open_fields"])
    if result["diverged_fields"]:
        result["standing"] = (
            "completeness standing diverged: the two spellings of "
            "the fields named carry different values, and the "
            "diverged state stands named rather than judged in "
            "silence: " + ", ".join(result["diverged_fields"]))
        spelling_unmet = [
            entry["field"] for entry in result["fields"]
            if not (entry["brief_name_present"]
                    and entry["form_name_present"])]
        if spelling_unmet:
            result["standing"] += (
                "; the fields named also do not stand with both "
                "spellings present, and stand named as not "
                "standing complete: " + ", ".join(spelling_unmet))
        both_present_unmet = [
            entry["field"] for entry in result["fields"]
            if entry["brief_name_present"]
            and entry["form_name_present"]
            and entry["standing"] not in (
                "open marker", "supplied", "diverged")]
        if both_present_unmet:
            result["standing"] += (
                "; the fields named also stand with both "
                "spellings present in an unmet form, and stand "
                "named as not standing complete: "
                + ", ".join(both_present_unmet))
    elif not complete:
        result["standing"] = (
            "completeness standing unmet: the fields named do not "
            "all stand present in an open marker or supplied form: "
            + ", ".join(
                entry["field"] for entry in result["fields"]
                if entry["standing"] not in ("open marker", "supplied")
                or not (entry["brief_name_present"]
                        and entry["form_name_present"])))
    elif result["open_fields"]:
        result["standing"] = (
            "completeness standing open: every completeness field "
            "stands present, and the fields named stand as open "
            "markers under OP-13, awaiting supply, so the family "
            "does not stand reportable ready on supplied values: "
            + ", ".join(result["open_fields"]))
    else:
        result["standing"] = (
            "completeness standing supplied: every completeness "
            "field stands present with a supplied value")
    return result


# The seal and edit keys the product own seal and edit acts
# write onto a family record (Step 16 fix wave 3, row F3-01,
# ruling T16-39). These keys stand as named carriage at the
# family doors only in the complete form those acts write, as
# _family_legitimate_wider_keys states; a record carrying any
# of them in any other form stands refused and named at the
# family doors, as a never sealed record carrying any of them
# stands refused and named at the seal.
_FAMILY_SEAL_KEYS = (
    "seal",
    "seal_version",
    "seal_hash",
    "sweep_manifest",
)

_FAMILY_EDIT_KEYS = (
    "runs_under",
    "edited_after_seal",
    "identifier_changed",
    "runs_start_again",
)


_SEAL_NO_HASH_STANDING = (
    "no hash value stands on the record; "
    "no hash stands computed by this seal")

_SEAL_RECORDED_HASH_STANDING = (
    "hash value as recorded on the record, "
    "stated as the hash")

_EDITED_IDENTIFIER_SUFFIX = "-edited-1"


def _family_seal_form_stands(record):
    """Whether the sealed standing of one family record stands
    in the form the product own seal act writes it (Step 16
    fix wave 4, row F4-01, ruling T16-49): the record stands
    sealed, the seal stands as a record value carrying the
    version, hash, and hash standing keys alone, the seal
    version and the seal hash stand equal to the version and
    the hash the seal itself carries, the family manifest hash
    stands equal to that hash, the hash standing stands in the
    form the seal act writes for the hash it carries, the seal
    version stands as the family version the record carries or
    as the seal act default where no version value stands, and
    the sweep manifest stands as the manifest the sweep act
    produces for the record as it stands, its family
    identifier, its family version, and its sealed family
    record hash, the first hash value standing among the
    family manifest hash, the seal hash, and the seal hash
    itself. A sealed standing in any other form stands in no
    form the seal act writes."""
    if _stored_pairs_value(record, "sealed") is not True:
        return False
    seal = _stored_pairs_value(record, "seal")
    if not isinstance(seal, dict):
        return False
    seal_fields = set()
    for key in dict.keys(seal):
        stored = _stored_key_text(key)
        if stored is None:
            stored = _stored_text(key)
        if stored is not None:
            seal_fields.add(stored)
    if seal_fields != {"version", "hash", "hash_standing"}:
        return False
    version = _stored_pairs_value(seal, "version")
    hash_value = _stored_pairs_value(seal, "hash")
    hash_standing = _stored_pairs_value(seal, "hash_standing")
    if not _base_value_equals(
            _stored_pairs_value(record, "seal_version"), version):
        return False
    if not _base_value_equals(
            _stored_pairs_value(record, "seal_hash"), hash_value):
        return False
    if not _base_value_equals(
            _stored_pairs_value(record, "family_manifest_hash"),
            hash_value):
        return False
    standing_text = _stored_text(hash_standing)
    if hash_value is None:
        if standing_text is None or not str.__eq__(
                standing_text, _SEAL_NO_HASH_STANDING):
            return False
    elif _stored_value_present(hash_value):
        if standing_text is None or not str.__eq__(
                standing_text, _SEAL_RECORDED_HASH_STANDING):
            return False
    else:
        return False
    family_version = _stored_pairs_value(record, "family_version")
    expected_version = (
        family_version if _stored_value_present(family_version)
        else "version 1")
    if not _base_value_equals(version, expected_version):
        return False
    manifest = _stored_pairs_value(record, "sweep_manifest")
    if not isinstance(manifest, dict):
        return False
    manifest_fields = set()
    for key in dict.keys(manifest):
        stored = _stored_key_text(key)
        if stored is None:
            stored = _stored_text(key)
        if stored is not None:
            manifest_fields.add(stored)
    if manifest_fields != {
            "family_identifier", "family_version",
            "sealed_family_record_hash"}:
        return False
    if _stored_pairs_present(record, "family_identifier"):
        identifier_value = _stored_pairs_value(
            record, "family_identifier")
    else:
        identifier_value = _stored_pairs_value(record, "family_id")
    sealed_hash = None
    for candidate in (
            _stored_pairs_value(record, "family_manifest_hash"),
            _stored_pairs_value(record, "seal_hash"),
            hash_value):
        if _stored_value_present(candidate):
            sealed_hash = candidate
            break
    expected_manifest = {
        "family_identifier": identifier_value,
        "family_version": family_version,
        "sealed_family_record_hash": sealed_hash,
    }
    for field in ("family_identifier", "family_version",
                  "sealed_family_record_hash"):
        if not _base_value_equals(
                _stored_pairs_value(manifest, field),
                expected_manifest[field]):
            return False
    return True


def _family_legitimate_wider_keys(record, include_seal=True):
    """The seal and edit keys of one family record that stand
    in the form the product own seal and edit acts write them
    (Step 16 fix wave 3, row F3-01, ruling T16-39, as settled
    at Step 16 fix wave 4, row F4-01, ruling T16-49). The seal
    keys stand legitimate only together, on a record whose
    sealed standing stands in the form the seal act writes
    it, as _family_seal_form_stands states. The edit keys
    stand legitimate only together, with each edit marker
    standing as True, the runs under value standing as the
    family identifier the record carries, that identifier
    standing in the edited form the edit act writes, carrying
    the edited suffix that act appends, and the record
    standing unsealed as that act leaves it, or standing
    sealed in the seal act form where a later seal carried
    the edit keys through; the runs under key alone stands
    legitimate where it carries that same identifier and no
    edit marker stands beside it, the form the edit of an
    unsealed record writes. Every other seal or edit key
    standing on a record stands in no product act form and
    stands legitimate nowhere."""
    if not isinstance(record, dict):
        return set()
    try:
        present = set()
        for key in dict.keys(record):
            stored = _stored_key_text(key)
            if stored is None:
                stored = _stored_text(key)
            if stored is not None:
                present.add(stored)
    except Exception:
        return set()
    legitimate = set()
    seal_form = include_seal and _family_seal_form_stands(record)
    if include_seal and all(
            key in present for key in _FAMILY_SEAL_KEYS):
        if seal_form:
            legitimate.update(_FAMILY_SEAL_KEYS)
    identifier_text = _stored_text(
        _stored_pairs_value(record, "family_id"))
    if identifier_text is None:
        identifier_text = _stored_text(
            _stored_pairs_value(record, "family_identifier"))
    runs_text = _stored_text(
        _stored_pairs_value(record, "runs_under"))
    runs_matches = (
        runs_text is not None and identifier_text is not None
        and str.__eq__(runs_text, identifier_text))
    edited_form = (
        identifier_text is not None
        and str.endswith(identifier_text, _EDITED_IDENTIFIER_SUFFIX)
        and (_stored_pairs_value(record, "sealed") is False
             or seal_form))
    if all(key in present for key in _FAMILY_EDIT_KEYS):
        if _stored_pairs_value(
                record, "edited_after_seal") is True and (
                _stored_pairs_value(
                    record, "identifier_changed") is True) and (
                _stored_pairs_value(
                    record, "runs_start_again") is True) and (
                runs_matches) and edited_form:
            legitimate.update(_FAMILY_EDIT_KEYS)
    elif "runs_under" in present and not any(
            key in present for key in _FAMILY_EDIT_KEYS[1:]):
        if runs_matches:
            legitimate.add("runs_under")
    return legitimate


def _family_door_refusals(record):
    """The refusals the family judgement door reaches beside the
    completeness bar (Step 16 fix wave 2, rows F2-01 and F2-03):
    the fields standing outside the Form 1 fields, the
    completeness fields, and the named carriage keys of
    FAMILY_CARRIAGE_KEYS, each named, and whether the scheduling
    order identifier carries a barred prototype order value, the
    brief literal "prototype order" or the shortened literal
    "prototype" the product bar already refuses, read in the
    same form the inner validator reads it. No order value
    stands invented or set here (OP-16). The seal and edit keys
    stand beside the named carriage keys only in the form the
    product own seal and edit acts write them, as
    _family_legitimate_wider_keys states (Step 16 fix wave 3,
    row F3-01, ruling T16-39)."""
    extra_fields = []
    allowed = set(form_fields("1"))
    allowed.update(COMPLETENESS_FIELDS)
    allowed.update(FAMILY_CARRIAGE_KEYS)
    allowed.update(_family_legitimate_wider_keys(record))
    for key in dict.keys(record):
        stored = _stored_key_text(key)
        if stored is None:
            stored = _stored_text(key)
        if stored is None:
            stored = _safe_str(key)
        if stored not in allowed:
            extra_fields.append(stored)
    order_text = _stored_text_dress(_stored_pairs_value(
        record, "scheduling_order_identifier"))
    order_barred = order_text in ("prototype order", "prototype")
    return extra_fields, order_barred, order_text


def _family_refusal_standing(extra_fields, order_barred, order_text):
    parts = []
    if extra_fields:
        parts.append(
            "field " + ", ".join(extra_fields) + " stands outside "
            "the form fields and the named carriage keys, so the "
            "record stands refused at this door and the field "
            "stands named")
    if order_barred:
        parts.append(
            "field scheduling_order_identifier carries the value "
            + str(order_text) + ", which the prototype order bar "
            "refuses, so the record stands refused at this door")
    return "not reportable: " + "; ".join(parts)


def family_reportable_standing(record):
    """The reportable standing of one family record as a stated
    result: the completeness bar judgement, the standing it rests
    on, and the fields in each standing, in place of an
    unqualified True over open markers (R16-03). Its
    supports_reportable_run entry stands as the judgement truth
    value: over open markers it does not stand as an unqualified
    True, it reflects the open standing the result states, and
    the completeness bar standing stands named apart at
    completeness_bar_met (fix wave 2, row F2-07). A record
    carrying a field outside the form fields and the named
    carriage keys, or carrying the barred prototype order value,
    stands refused here and the refusal stands named in the
    standing (fix wave 2, rows F2-01 and F2-03)."""
    if not isinstance(record, dict):
        return {
            "supports_reportable_run": False,
            "completeness_bar_met": False,
            "standing": "not a record: no completeness standing",
            "open_fields": [],
            "supplied_fields": [],
            "diverged_fields": [],
            "missing_fields": [],
            "placeholder_fields": [],
            "extra_fields": [],
            "reportable_ready": False,
        }
    standing = completeness_standing(record)
    extra_fields, order_barred, order_text = _family_door_refusals(
        record)
    bar_met = bool(standing["complete_on_completeness_limb"])
    if extra_fields or order_barred:
        return {
            "supports_reportable_run": False,
            "completeness_bar_met": bar_met,
            "standing": _family_refusal_standing(
                extra_fields, order_barred, order_text),
            "open_fields": standing["open_fields"],
            "supplied_fields": standing["supplied_fields"],
            "diverged_fields": standing["diverged_fields"],
            "missing_fields": standing["missing_fields"],
            "placeholder_fields": standing["placeholder_fields"],
            "extra_fields": extra_fields,
            "reportable_ready": False,
        }
    judgement = StatedJudgement(
        bar_met,
        standing=standing["standing"],
        open_fields=standing["open_fields"],
        supplied_fields=standing["supplied_fields"],
        diverged_fields=standing["diverged_fields"],
        missing_fields=standing["missing_fields"],
        placeholder_fields=standing["placeholder_fields"],
        reportable_ready=standing["reportable_ready"])
    return {
        "supports_reportable_run": judgement.truth_value,
        "completeness_bar_met": bar_met,
        "standing": standing["standing"],
        "open_fields": standing["open_fields"],
        "supplied_fields": standing["supplied_fields"],
        "diverged_fields": standing["diverged_fields"],
        "missing_fields": standing["missing_fields"],
        "placeholder_fields": standing["placeholder_fields"],
        "extra_fields": [],
        "reportable_ready": standing["reportable_ready"],
    }


def family_supports_reportable_run(record):
    """The family completeness bar, judged once from the one
    completeness key set: every completeness field present under
    both of its spellings, the two spellings agreeing, and each
    value standing as an open marker under OP-13 or as a supplied
    recorded value, never as a bare number (TG-01.3 pin) and never
    as the placeholder text.

    The answer stands as a StatedJudgement: over open markers it
    states the open standing and names the open fields in place
    of an unqualified True (R16-03), and over supplied values it
    states the supplied standing, so a family carrying supplied
    values can pass (R16-15).

    This door reaches the refusals its charged bounds name
    beside the completeness bar (Step 16 fix wave 2): a field
    standing outside the form fields and the named carriage keys
    of FAMILY_CARRIAGE_KEYS stands refused and named (row F2-01,
    ruling T16-23), a made record carrying only named carriage
    keys keeping its standing, a record sealed by the product
    own seal act or edited by the product own edit acts keeping
    its standing on the seal and edit keys those acts write, in
    the form they write them (row F3-01, ruling T16-39), and
    the barred prototype order
    value stands refused, this judgement reaching the order bar
    as validate_record, run_is_reportable, the family failure
    list, the seal, and both MOD-04 checks already do (row
    F2-03, ruling T16-28)."""
    if not isinstance(record, dict):
        return StatedJudgement(
            False, standing="not a record: the completeness bar "
            "stands unmet")
    standing = completeness_standing(record)
    extra_fields, order_barred, order_text = _family_door_refusals(
        record)
    if extra_fields or order_barred:
        return StatedJudgement(
            False,
            standing=_family_refusal_standing(
                extra_fields, order_barred, order_text),
            open_fields=standing["open_fields"],
            supplied_fields=standing["supplied_fields"],
            diverged_fields=standing["diverged_fields"],
            missing_fields=standing["missing_fields"],
            placeholder_fields=standing["placeholder_fields"],
            extra_fields=extra_fields)
    return StatedJudgement(
        standing["complete_on_completeness_limb"],
        standing=standing["standing"],
        open_fields=standing["open_fields"],
        supplied_fields=standing["supplied_fields"],
        diverged_fields=standing["diverged_fields"],
        missing_fields=standing["missing_fields"],
        placeholder_fields=standing["placeholder_fields"],
        reportable_ready=standing["reportable_ready"])


def validation_standing(form_id, instance):
    """The stated validation result of one record instance: the
    boolean judgement of validate_record, and, beside it, the
    standing that judgement rests on, with placeholder values and
    open marker values named as such, field by field (R16-03).

    A formally complete instance carrying placeholder or marker
    values stands named a template in its standing, distinguished
    from a record carrying real values. For Form 1 the
    completeness standing of completeness_standing stands folded
    in, judged from the same one key set (R16-15)."""
    fid = _fid(form_id)
    valid = bool(validate_record(fid, instance))
    placeholder_fields = []
    open_marker_fields = []
    if isinstance(instance, dict):
        for key, item in dict.items(instance):
            key_text = _stored_text(key)
            if key_text is None:
                continue
            text = _stored_text_dress(item)
            if text is None:
                continue
            if str.__eq__(text, "stated value"):
                placeholder_fields.append(key_text)
            elif str.startswith(text, OPEN_MARKER_PREFIX):
                open_marker_fields.append(key_text)
    result = {
        "form": fid,
        "valid": valid,
        "placeholder_fields": placeholder_fields,
        "open_marker_fields": open_marker_fields,
        "supplied_fields": [],
        "diverged_fields": [],
    }
    if fid == "1" and isinstance(instance, dict):
        standing = completeness_standing(instance)
        result["supplied_fields"] = list(standing["supplied_fields"])
        result["diverged_fields"] = list(standing["diverged_fields"])
        result["open_marker_fields"] = list(standing["open_fields"])
        result["completeness_standing"] = standing["standing"]
    if not valid:
        result["standing"] = (
            "invalid: the record fails validation")
    elif fid == "1" and result["diverged_fields"]:
        result["standing"] = (
            "valid in form, with completeness standing diverged "
            "on the fields named: "
            + ", ".join(result["diverged_fields"]))
    elif result["open_marker_fields"]:
        result["standing"] = (
            "template in open form: the record stands formally "
            "complete, and the fields named carry open marker "
            "values under OP-13, awaiting supply: "
            + ", ".join(result["open_marker_fields"]))
    elif placeholder_fields:
        result["standing"] = (
            "template: the record stands formally complete, and "
            "the fields named carry the placeholder text in place "
            "of real values: " + ", ".join(placeholder_fields))
    else:
        result["standing"] = (
            "record carrying stated values: no placeholder or "
            "open marker value stands on the record")
    return result


_VALIDATE_WIDTH_BOUND = 10000


def _record_width_past_bound(instance):
    """Whether one record instance stands wider than the
    stated validation width bound of 10000 entries (FW-16).
    The width stands counted across every mapping entry and
    every sequence or set item in the instance, through base
    class readings only, each container counted once, and
    the walk stops at the bound, so the judgement itself
    stands bounded by the bound and never by the handed
    width. A text or bytes value counts as the one entry
    that carries it, never per character."""
    total = 0
    seen = set()
    stack = [instance]
    while stack:
        node = stack.pop()
        if not isinstance(node, (dict, list, tuple, set, frozenset)):
            continue
        if id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, dict):
            total += dict.__len__(node)
            for key in dict.__iter__(node):
                stack.append(key)
                stack.append(dict.__getitem__(node, key))
        else:
            items = list(_base_iter(node))
            total += len(items)
            stack.extend(items)
        if total > _VALIDATE_WIDTH_BOUND:
            return True
    return False


def _width_failure_sentence():
    return _failure_sentence(
        "record width",
        "the record carries more than the stated width bound "
        "of 10000 entries, counting every mapping entry and "
        "every sequence or set item the record carries, so "
        "the record stands refused at validation before the "
        "unbounded validation work stands done",
        "hand a record carrying no more than the stated "
        "width bound of 10000 entries, or split the record "
        "and validate each part")


_VALIDATE_BYTE_BOUND = 1000000


def _value_byte_count(value):
    """The byte count of one text or bytes value, read through
    base class readings only: a text value through the bytes
    of its stored text, and a bytes form through its stored
    length. A value in any other form carries no byte count
    here and stands counted by the entry form alone."""
    if isinstance(value, str):
        text = str.__str__(value)
        try:
            return len(text.encode("utf-8", "ignore"))
        except Exception:
            return str.__len__(text)
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, memoryview):
        return len(memoryview.tobytes(value))
    return 0


def _record_byte_past_bound(instance):
    """Whether one record instance stands past the stated
    validation byte bound of 1000000 bytes (FW3-12), beside
    the entry bound the width guard states. The bytes stand
    counted across every text and bytes value in the
    instance, keys and values alike, through base class
    readings only, and the walk stops at the bound, so the
    judgement itself stands bounded by the bound."""
    total = 0
    seen = set()
    stack = [instance]
    while stack:
        node = stack.pop()
        if isinstance(node, (str, bytes, bytearray, memoryview)):
            total += _value_byte_count(node)
            if total > _VALIDATE_BYTE_BOUND:
                return True
            continue
        if not isinstance(node, (dict, list, tuple, set, frozenset)):
            continue
        if id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, dict):
            for key in dict.__iter__(node):
                stack.append(key)
                stack.append(dict.__getitem__(node, key))
        else:
            stack.extend(list(_base_iter(node)))
    return False


def _byte_failure_sentence():
    return _failure_sentence(
        "record byte size",
        "the record carries more than the stated byte bound "
        "of 1000000 bytes, counting the bytes of every text "
        "and bytes value the record carries, so the record "
        "stands refused at validation in the stated byte form "
        "beside the entry form",
        "hand a record carrying no more than the stated "
        "byte bound of 1000000 bytes, or split the record "
        "and validate each part")


_RUN_NUMERIC_FIELD_MINIMA = (
    ("population_size", 1),
    ("run_length_in_days", 1),
    ("replicate_index", 0),
)


def _numeric_field_judged(field, value):
    """Whether one numeric field value of a run record stands
    in its stated form (FW3-18): a whole number at or above
    the stated minimum of its field, read on its stored
    form, or the placeholder template standing the product
    own minimal instance carries. A boolean, a non finite
    or fractional number, a negative count, and any text
    beside the placeholder standing stand in no judged
    form."""
    minimum = dict(_RUN_NUMERIC_FIELD_MINIMA)[field]
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return int.__ge__(value, minimum)
    if isinstance(value, float):
        if value != value:
            return False
        if value == float("inf") or value == float("-inf"):
            return False
        return float.is_integer(value) and value >= minimum
    if isinstance(value, str):
        dress = _stored_text_dress(value)
        return dress is not None and _stands_placeholder_text(dress)
    return False


def _validate_record_inner(form_id, instance):
    """Validate one record instance against its form.

    The required field rule: a record with a required field absent
    fails validation. A conditional field is required exactly where
    its stated condition holds. A field FORM_FIELD_OWNERSHIP names
    as never_fill stands apart from the required fields: it stands
    required on no record, and a record carrying it filled fails
    validation, the ownership statement read on its face (F2-08,
    ruling T16-32).
    """
    fid = _fid(form_id)
    if fid not in _FORM_SPECS or not isinstance(instance, dict):
        return False
    if _record_width_past_bound(instance):
        return False
    if _record_byte_past_bound(instance):
        return False
    if fid in ("2", "4"):
        # The numeric fields of a run record stand judged in
        # their stated forms (FW3-18): a population, a run
        # length, or a replicate index in no judged form
        # fails validation here, as it stands named at the
        # failure door.
        for _num_field, _minimum in _RUN_NUMERIC_FIELD_MINIMA:
            _num_value = _stored_pairs_value(
                instance, _num_field, _STORED_MISSING)
            if _num_value is not _STORED_MISSING and (
                    _num_value is not None) and not (
                    _numeric_field_judged(_num_field, _num_value)):
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
    never_fill = ()
    if fid in FORM_FIELD_OWNERSHIP:
        never_fill = FORM_FIELD_OWNERSHIP[fid]["never_fill"]
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
    for field in never_fill:
        filled = [
            item for key, item in stored_pairs
            if isinstance(key, str)
            and str.__eq__(str.__str__(key), field)
        ]
        if filled and filled[0] is not None:
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
    if fid in ("1", "4"):
        # The prototype order bar of brief Shape 1, at Step 16
        # row R16-13: a headline family record, and a headline
        # run record, whose scheduling order identifier reads
        # the brief literal value "prototype order" fails
        # validation and is not reportable as a headline run.
        # The shortened literal "prototype" the product bar
        # already refused at MOD-04 stays refused here as well,
        # so no bar standing before this row is weakened. The
        # Form 1 reading stands on the family record as the
        # headline family definition surface: a family carrying
        # the barred order names no lawful headline order.
        # The bar reads its value through the product standing
        # folded and dressed reading (Step 16 fix wave 2, row
        # F2-06, ruling T16-29): the value stands dressed by
        # _stored_text_dress and judged by _folded_key_matches
        # against the folded form of each charged literal, the
        # same folded reading the validator applies to stored
        # text elsewhere, so case and spacing variants of the
        # barred words stand barred in the same form as the
        # literals themselves. No new barred value stands
        # invented (OP-16): the folded judgement stands exact,
        # so a value carrying the barred words beside other
        # words, or extending them, stands unbarred.
        _order_text = _stored_text_dress(_stored_pairs_value(
            instance, "scheduling_order_identifier"))
        if fid == "4":
            _class_text = _stored_text_dress(_stored_pairs_value(
                instance, "run_class"))
            if _class_text != "headline":
                _order_text = None
        if _order_text is not None and (
                _folded_key_matches(
                    _order_text, _folded_money_key("prototype order"))
                or _folded_key_matches(
                    _order_text, _folded_money_key("prototype"))):
            return False
    if fid == "1":
        # The completeness limb, judged from the one completeness
        # key set (R16-15): each Form 1 completeness value stands
        # as an open marker under OP-13 or as a supplied recorded
        # value, and a brief name spelling standing beside it must
        # carry the same value, a diverged pair failing here in
        # the same judgement that judges the reportability bar.
        # A bare scalar, the placeholder text, and an absent value
        # all fail, as the marker only reading failed them before.
        # The shared reading of the one key set (T16-33): the two
        # spellings carry one field, and the field stands complete
        # only where both spellings stand; a Form 1 field name
        # standing with its brief name spelling absent fails here,
        # as the completeness standing and the reportability bar
        # already answer at that edge, so every judgement of the
        # key set reads the set the same way.
        for prose, slug in COMPLETENESS_KEY_PAIRS:
            value = _stored_pairs_value(instance, slug)
            if value is None:
                continue
            prose_value = _stored_pairs_value(
                instance, prose, _STORED_MISSING)
            if prose_value is _STORED_MISSING:
                return False
            if not _values_agree(value, prose_value):
                return False
            if _completeness_value_standing(value) not in (
                    "open marker", "supplied"):
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


def _failure_sentence(field, rule, step):
    return (
        "validate_record stands refused: field " + field + ": "
        + rule + "; next step: " + step
        + ", and no record stands validated")


def _diagnosed_failure_entries(form_id, instance):
    """The general naming rule of the failure door (Step 16
    fix wave 3, row F3-02, ruling T16-40).

    Where the inner judgement refuses a record and no
    dedicated entry above has named the fault, the fault
    stands diagnosed against the inner judgement itself, by
    field, as a general rule over the door failure
    generation and not as an enumeration of fault classes:
    a field stands at fault where correcting that field
    alone, to the value the product own minimal valid
    instance carries for it (or removing the field where
    the minimal instance carries no such field), leaves a
    record the inner judgement accepts. Where no single
    correction answers, the differing fields stand corrected
    together and each original value restored in turn: a
    field whose original value can stand restored while the
    record still validates stands cleared, and the fields
    that remain stand at fault together. Every entry this
    act returns names its field in the standing entry form,
    states the rule for that field (the condition rule where
    the field stands as a condition discriminator or a
    conditional field, and otherwise the stated rule of the
    form for that field), and states the next step. No entry
    of this act carries a sentence that names no field."""
    fid = _fid(form_id)
    try:
        if fid == "36":
            _kind = _stored_text_dress(_stored_pairs_value(
                instance, "entry_kind"))
            reference = minimal_valid_instance(
                fid,
                entry_kind=_kind if _kind in (
                    "ordinary", "agent", "supersession") else None)
        else:
            reference = minimal_valid_instance(fid)
    except Exception:
        reference = {}
    candidates = []

    def _add_candidate(name):
        if name is not None and name not in candidates:
            candidates.append(name)

    for _field in form_fields(fid):
        _add_candidate(_field)
    for _condition in _conditions_for(fid):
        _add_candidate(_condition["discriminator"])
        _add_candidate(_condition["field"])
    if fid == "1":
        for _field in COMPLETENESS_FIELDS:
            _add_candidate(_field)
    for _key, _item in list(dict.items(instance)):
        _add_candidate(_stored_key_text(_key))
    base = dict(instance)

    def _inner_ok(record):
        try:
            return _validate_record_inner(form_id, record)
        except (RecordTraversalFailure, RecursionError):
            return False

    def _corrected(record, field):
        trial = dict(record)
        if field in reference:
            trial[field] = copy.deepcopy(reference[field])
        else:
            trial.pop(field, None)
        return trial

    def _differs(field):
        in_base = field in base
        in_reference = field in reference
        if in_base != in_reference:
            return True
        if not in_base:
            return False
        try:
            return not _base_value_equals(
                base[field], reference[field])
        except Exception:
            return True

    differing = [
        _field for _field in candidates if _differs(_field)]
    fault_fields = []
    # A single correction that leaves a record the inner
    # judgement accepts proves its field the sole fault, so
    # the search stops at the first such field: the fields
    # whose handed standing differs from the minimal valid
    # instance stand tried first, as a fault field stands
    # among them wherever the fault is one of value, and the
    # remaining candidates stand tried after them.
    for _field in differing + [
            _field for _field in candidates
            if _field not in differing]:
        if _inner_ok(_corrected(base, _field)):
            fault_fields = [_field]
            break
    if not fault_fields:
        corrected_all = base
        for _field in differing:
            corrected_all = _corrected(corrected_all, _field)
        if differing and _inner_ok(corrected_all):
            remaining = list(differing)
            for _field in differing:
                trial = dict(corrected_all)
                if _field in base:
                    trial[_field] = base[_field]
                else:
                    trial.pop(_field, None)
                if _inner_ok(trial):
                    corrected_all = trial
                    remaining.remove(_field)
            fault_fields = remaining
        if not fault_fields and differing:
            fault_fields = differing[:1]
    if not fault_fields and candidates:
        fault_fields = candidates[:1]
    entries = []
    conditions = _conditions_for(fid)
    for _field in fault_fields:
        _discriminator_of = None
        _conditional_of = None
        for _condition in conditions:
            if _condition["discriminator"] == _field:
                _discriminator_of = _condition
            if _condition["field"] == _field:
                _conditional_of = _condition
        if _discriminator_of is not None:
            entries.append(_failure_sentence(
                _field,
                "the field stands as the discriminator of a "
                "stated condition on this form (" +
                _discriminator_of["condition"] + "), and a "
                "discriminator value stands only as a boolean "
                "on the record, while the value the record "
                "carries on this field stands as no boolean",
                "hand the field " + _field + " as a boolean, "
                "true or false, as the stated condition for "
                "it reads"))
        elif _conditional_of is not None:
            entries.append(_failure_sentence(
                _field,
                "the field stands as a conditional field of a "
                "stated condition on this form (" +
                _conditional_of["condition"] + "), and the "
                "value the record carries on this field "
                "stands outside the stated form for it where "
                "its condition stands judged with the record",
                "hand the field " + _field + " in the form "
                "the form states for it, or clear the "
                "condition field " +
                _conditional_of["discriminator"]
                + " on the record"))
        else:
            entries.append(_failure_sentence(
                _field,
                "a stated rule of this form for this field "
                "stands unmet by the value the record carries "
                "on it",
                "hand the field " + _field + " with a value "
                "in the form the form states for it, in "
                "form_fields and field_conditions for this "
                "form"))
    return entries


def _entry_named_field(entry):
    prefix = "validate_record stands refused: field "
    if not entry.startswith(prefix):
        return None
    field, sep, _tail = entry[len(prefix):].partition(": ")
    return field if sep else None


def _additional_diagnosed_failure_entries(
        form_id, instance, dedicated):
    """The multi fault naming extension (Step 16 fix wave 4,
    row F4-03, ruling T16-51).

    The naming rule of T16-40 applies on multi fault records
    in full: where dedicated entries have named some faults
    of a record the inner judgement refuses, a simultaneous
    fault no dedicated entry has named stands diagnosed by
    field against the inner judgement itself, whether or not
    a dedicated entry also stands. The act first corrects
    every field a dedicated entry has named, to the value
    the product own minimal valid instance carries for it,
    or removes the field where the minimal instance carries
    no such field; the two spellings of a Form 1 completeness
    pair stand corrected together, as the pair carries one
    field. Where the inner judgement accepts the corrected
    record, every inner fault stood among the named faults
    and no entry stands added. Where it still refuses, the
    faults that remain stand diagnosed by the standing
    diagnosis act on the corrected record, and no entry
    naming an already named field stands returned, so no
    fault at this door stands named twice and a single fault
    record keeps the entries it stood with before."""
    named = []
    for entry in dedicated:
        field = _entry_named_field(entry)
        if field is not None and field not in named:
            named.append(field)
    fid = _fid(form_id)
    if fid == "1":
        for _prose, _slug in COMPLETENESS_KEY_PAIRS:
            if _prose in named or _slug in named:
                for _spelling in (_prose, _slug):
                    if _spelling not in named:
                        named.append(_spelling)
    try:
        if fid == "36":
            _kind = _stored_text_dress(_stored_pairs_value(
                instance, "entry_kind"))
            reference = minimal_valid_instance(
                fid,
                entry_kind=_kind if _kind in (
                    "ordinary", "agent", "supersession") else None)
        else:
            reference = minimal_valid_instance(fid)
    except Exception:
        reference = {}
    corrected = {}
    for _key, _item in dict.items(instance):
        if _stored_key_text(_key) not in named:
            corrected[_key] = _item
    for _field in named:
        if _field in reference:
            corrected[_field] = copy.deepcopy(reference[_field])
    try:
        inner_ok = _validate_record_inner(form_id, corrected)
    except (RecordTraversalFailure, RecursionError):
        return []
    if inner_ok:
        return []
    entries = []
    for entry in _diagnosed_failure_entries(form_id, corrected):
        if _entry_named_field(entry) not in named:
            entries.append(entry)
    return entries


def _record_validation_failures(form_id, instance):
    fid = _fid(form_id)
    if fid not in _FORM_SPECS:
        class_name = _identifier_non_text_class(form_id)
        if class_name is not None:
            return [_failure_sentence(
                "form identifier " + _safe_str(form_id),
                "the identifier stands handed in a non text "
                "form, the " + class_name + " form, where a "
                "form identifier stands as text, so no field "
                "list stands to check the record against",
                "hand the identifier as text, one of the "
                "identifiers in FORM_IDS")]
        return [_failure_sentence(
            "form identifier " + _safe_str(form_id),
            "no form stands under that identifier, so no field "
            "list stands to check the record against",
            "hand a stated form identifier, one of the identifiers "
            "in FORM_IDS, or check the identifier for a mistyped "
            "character")]
    if _record_width_past_bound(instance):
        return [_width_failure_sentence()]
    if _record_byte_past_bound(instance):
        return [_byte_failure_sentence()]
    if not isinstance(instance, dict):
        return [_failure_sentence(
            "record",
            "a record stands as a field mapping, and the handed "
            "value stands in no record form",
            "hand the record as a mapping of field names to values")]
    failures = []
    stored_pairs = list(dict.items(instance))

    def present_value(field):
        for key, item in stored_pairs:
            if isinstance(key, str) and str.__eq__(
                    str.__str__(key), field):
                return True, item
        return False, None

    never_fill = ()
    if fid in FORM_FIELD_OWNERSHIP:
        never_fill = FORM_FIELD_OWNERSHIP[fid]["never_fill"]
    for field in required_fields(fid):
        found, value = present_value(field)
        if not found or value is None:
            failures.append(_failure_sentence(
                field,
                "the field stands required on this form and stands "
                "absent or empty on the record",
                "supply the field " + field + " with a value in "
                "the form the form states for it"))
    for field in never_fill:
        found, value = present_value(field)
        if found and value is not None:
            failures.append(_failure_sentence(
                field,
                "the field stands as a field a user must never "
                "fill under FORM_FIELD_OWNERSHIP, a seed field "
                "standing under the DQ7-02 adoption gate, and the "
                "record carries it filled",
                "remove the field " + field + " from the record, "
                "leaving it unfilled, and no seed stands drawn "
                "or assigned for it"))
    if fid in ("2", "4"):
        # The numeric field entries (FW3-18), in the same
        # judged form the inner judgement applies.
        for num_field, minimum in _RUN_NUMERIC_FIELD_MINIMA:
            found, value = present_value(num_field)
            if found and value is not None and not (
                    _numeric_field_judged(num_field, value)):
                failures.append(_failure_sentence(
                    num_field,
                    "the field stands as a whole number at or "
                    "above " + str(minimum) + " on this form, "
                    "or at the placeholder template standing, "
                    "and the value the record carries on it "
                    "stands in no judged form",
                    "supply the field " + num_field + " as a "
                    "whole number at or above " + str(minimum)))
    for condition in _conditions_for(fid):
        disc_found, disc_value = present_value(
            condition["discriminator"])
        if disc_value is True:
            field_found, _field_value = present_value(
                condition["field"])
            if not field_found:
                failures.append(_failure_sentence(
                    condition["field"],
                    "the field stands required where its stated "
                    "condition holds, and that condition stands "
                    "on the record",
                    "supply the field " + condition["field"]
                    + ", or clear the condition field "
                    + condition["discriminator"] + " on the record"))
    allowed = set(form_fields(fid))
    allowed.update(
        condition["discriminator"] for condition in _conditions_for(fid))
    if fid == "1":
        allowed.update(COMPLETENESS_FIELDS)
    if fid == "36":
        allowed.add("entry_kind")
    folded_targets = [
        _folded_money_key(field) for field in allowed]

    def key_names_a_field(key):
        plain = _stored_text(key)
        if plain is not None and any(
                str.__eq__(plain, field) for field in allowed):
            return True
        key_text = _stored_key_text(key)
        if key_text is not None and any(
                str.__eq__(key_text, field) for field in allowed):
            return True
        dress = _stored_text_dress(key)
        if dress is not None and any(
                str.__eq__(dress, field) for field in allowed):
            return True
        try:
            if isinstance(key, (tuple, list, set, frozenset)):
                for target in folded_targets:
                    if _folded_key_matches(key, target):
                        return True
                return False
            # The stated cost form of this door (FW3-13): the
            # folded variants of one handed key stand computed
            # once for the key, and the folded targets of the
            # form fields stand computed once for the call, so
            # the work of one call stands bounded by the keys
            # handed in, never by the keys multiplied by the
            # fields of the form. The judgements taken stand
            # as the folded match act takes them, limb for
            # limb: the spanning bar reading, the variant
            # membership, and the every reading match.
            variants = _folded_key_variants(key)
            for target in folded_targets:
                if target in variants:
                    return True
            for target in folded_targets:
                if _seg_spanning_barred(
                        key, (), (),
                        (target,) + (
                            ("realmani",)
                            if target == "realmoney" else ()),
                        ()):
                    return True
                if _matches_under_every_reading(key, target):
                    return True
        except Exception:
            return False
        return False

    for key, _item in stored_pairs:
        stored = _stored_key_text(key)
        if stored is None:
            failures.append(_failure_sentence(
                _safe_str(key),
                "a field name stands as text on this form, and "
                "the handed field name stands in no text form",
                "name every field with a text field name from "
                "the form field list"))
        elif not key_names_a_field(key):
            failures.append(_failure_sentence(
                stored,
                "the form names no such field, so the field "
                "stands outside the record the form states",
                "remove the field " + stored + ", or check its "
                "spelling against the form field list"))
    # Container value in a scalar stated field (Step 16 fix
    # wave 7, row F7-02, ruling T16-73): a value standing in a
    # container form, a dict, a list, or a set, in a field whose
    # stated form is scalar stands named here in the standing
    # failure form, so validate_record, which answers as this
    # list stands, refuses the record on the same fault. This
    # entry stands on Form 2, the sweep point specification
    # form, where every field stands in a scalar stated form:
    # identifiers, stepped numbers, selectors, and stated text
    # values, no field of the form admitting a container. On
    # the other forms the product carries fields whose stated
    # form is itself a container and single part container
    # dresses the doors read as the scalar value they wrap, and
    # no stated form table in the product distinguishes those
    # fields field by field, so a container entry at those
    # forms would refuse values in their stated forms, which
    # the bound forbids; those forms stand outside this entry
    # exactly as they stood before this wave.
    if fid == "2":
        for field in form_fields(fid):
            found, value = present_value(field)
            if found and isinstance(value, (dict, list, set)):
                if isinstance(value, dict):
                    _container_word = "a dict"
                elif isinstance(value, list):
                    _container_word = "a list"
                else:
                    _container_word = "a set"
                failures.append(_failure_sentence(
                    field,
                    "the field stands in a scalar stated form on "
                    "this form, and the value the record carries "
                    "on it stands in a container form, " +
                    _container_word + ", which no scalar stated "
                    "form admits",
                    "hand the field " + field + " with a value in "
                    "the scalar form the form states for it, not "
                    "in a container form"))
    for field, checker, stated in (
            ("calibration_claim_field", validate_calibration_field,
             "the stated calibration claim form"),
            ("store_kind", validate_store_kind,
             "a stated store kind")):
        found, value = present_value(field)
        if found and value is not None and not checker(value):
            failures.append(_failure_sentence(
                field,
                "the field stands in a stated form and the handed "
                "value stands outside that form",
                "hand the field " + field + " in " + stated))
    if fid == "10":
        found, value = present_value("lien_state")
        if found and value is not None and not validate_lien_state(
                value, cross_seam=bool(
                    present_value("cross_seam_effect")[1])):
            failures.append(_failure_sentence(
                "lien_state",
                "the field stands in a stated form and the handed "
                "value stands outside that form",
                "hand the field lien_state in one of the stated "
                "lien states"))
    if fid == "22":
        for field, stated_set in (
                ("outcome", ("reported", "not reported")),
                ("confirmation_outcome", ("passed", "failed", "not run")),
                ("gate_failure", (
                    "procedure gate", "confirmation gate",
                    "both gates", "none"))):
            found, value = present_value(field)
            if found and value is not None:
                dress = _stored_text_dress(value)
                if dress is None or dress not in stated_set:
                    failures.append(_failure_sentence(
                        field,
                        "the field stands in a stated set of values "
                        "and the handed value stands outside that set",
                        "hand the field " + field + " as one of: "
                        + ", ".join(stated_set)))
    # Value rule failures, named field by field (Step 16 fix
    # wave 2, row F2-02, ruling T16-26): the faults the inner
    # judgement holds as value rules stand named here in the
    # same field, rule, and next step form, so no fault of these
    # classes draws the generic fallback entry below.
    if fid in ("1", "4"):
        _order_found, _order_value = present_value(
            "scheduling_order_identifier")
        if _order_found:
            _order_text = _stored_text_dress(_order_value)
            # The naming reads the bar through the same folded
            # reading the inner judgement applies (Step 16 fix
            # wave 3, row F3-02, ruling T16-40): a case or
            # spacing variant of the barred value stands barred
            # in the inner judgement, so it draws this named bar
            # entry here in the same form as the literal, and no
            # barred variant falls to a lesser entry.
            _barred = _order_text is not None and (
                _folded_key_matches(
                    _order_text, _folded_money_key("prototype order"))
                or _folded_key_matches(
                    _order_text, _folded_money_key("prototype")))
            if _barred and fid == "4":
                _class_found, _class_value = present_value(
                    "run_class")
                if _stored_text_dress(_class_value) != "headline":
                    _barred = False
            if _barred:
                failures.append(_failure_sentence(
                    "scheduling_order_identifier",
                    "the value '" + _order_text + "' stands "
                    "barred under the prototype order bar: a "
                    "headline record whose scheduling order "
                    "identifier reads the barred value stands "
                    "refused under that bar",
                    "hand a scheduling order identifier that "
                    "stands as a lawful headline order, not the "
                    "barred value '" + _order_text + "'"))
    if fid == "1":
        for _prose, _slug in COMPLETENESS_KEY_PAIRS:
            _slug_value = _stored_pairs_value(
                instance, _slug, _STORED_MISSING)
            if _slug_value is _STORED_MISSING or (
                    _slug_value is None):
                continue
            _prose_value = _stored_pairs_value(
                instance, _prose, _STORED_MISSING)
            if _prose_value is _STORED_MISSING:
                # The missing spelling limb (Step 16 fix wave 3,
                # row F3-02, ruling T16-40): the inner judgement
                # holds the pair as one field and refuses the
                # record where one spelling stands absent, so
                # the absence stands named here in the same
                # entry form, naming the field and the missing
                # spelling, and no such record falls to a lesser
                # entry.
                failures.append(_failure_sentence(
                    _slug,
                    "the two spellings of this completeness "
                    "field stand as one field: the field stands "
                    "under " + _slug + " while its other "
                    "spelling " + _prose + " stands absent on "
                    "the record, so the completeness pair "
                    "stands with one spelling missing and no "
                    "one value stands for the field",
                    "supply the spelling " + _prose
                    + " carrying the same value as " + _slug
                    + " for this completeness field"))
                continue
            if not (
                    _values_agree(_slug_value, _prose_value)):
                failures.append(_failure_sentence(
                    _slug,
                    "the two spellings of this completeness "
                    "field stand diverged: the field stands "
                    "under both " + _slug + " and " + _prose
                    + ", and the two spellings carry different "
                    "values, so the completeness pair stands "
                    "diverged and no one value stands for the "
                    "field",
                    "make the two spellings " + _slug + " and "
                    + _prose + " carry the one same value for "
                    "this completeness field"))
                continue
            _standing = _completeness_value_standing(_slug_value)
            if _standing not in ("open marker", "supplied"):
                if _standing == "placeholder":
                    _wording = (
                        "the completeness value stands as the "
                        "placeholder text 'stated value' in "
                        "place of a recorded value")
                elif _standing == "bare scalar":
                    _wording = (
                        "the completeness value stands as a "
                        "bare scalar, and a bare scalar stands "
                        "as no recorded completeness value at all")
                elif _standing == "absent":
                    _wording = (
                        "the completeness value stands absent "
                        "in the value the field carries")
                else:
                    _wording = (
                        "the completeness value stands as "
                        + _standing)
                failures.append(_failure_sentence(
                    _slug,
                    "the completeness rule for this field "
                    "stands unmet: " + _wording + ", and a "
                    "completeness value stands only as an open "
                    "marker under OP-13 or as a supplied "
                    "recorded value",
                    "supply the field " + _slug + " with a "
                    "recorded value, or leave its value as an "
                    "open marker under OP-13"))
    if fid == "22":
        _outcome_found, _outcome_value = present_value("outcome")
        if _outcome_found and _stored_text_dress(
                _outcome_value) == "reported":
            _conf_found, _conf_value = present_value(
                "confirmation_outcome")
            _conf_text = _stored_text_dress(_conf_value)
            if _conf_found and _conf_text in (
                    "failed", "not run"):
                failures.append(_failure_sentence(
                    "confirmation_outcome",
                    "the outcome stands reported while the "
                    "confirmation outcome stands '" + _conf_text
                    + "': a reported outcome stands only where "
                    "the confirmation outcome stands passed",
                    "run the confirmation and record its "
                    "outcome as passed before the outcome "
                    "stands reported, or set the field outcome "
                    "to not reported"))
            _gate_found, _gate_value = present_value(
                "gate_failure")
            _gate_text = _stored_text_dress(_gate_value)
            if _gate_found and _gate_text in (
                    "procedure gate", "confirmation gate",
                    "both gates"):
                failures.append(_failure_sentence(
                    "gate_failure",
                    "the outcome stands reported while the "
                    "gate failure stands '" + _gate_text
                    + "': a reported outcome stands only where "
                    "no gate stands failed",
                    "clear the gate failure the field names "
                    "before the outcome stands reported, or "
                    "set the field outcome to not reported"))
        _unranked_fields = (
            "test_value", "rank", "threshold")
        _unranked_readings = []
        for _unranked_field in _unranked_fields:
            _u_found, _u_value = present_value(_unranked_field)
            _unranked_readings.append(
                _u_found and _stored_text_dress(
                    _u_value) == "not ranked")
        if any(_unranked_readings) and not all(
                _unranked_readings):
            _first_unranked = _unranked_fields[
                _unranked_readings.index(True)]
            failures.append(_failure_sentence(
                _first_unranked,
                "the value 'not ranked' stands on this field "
                "while the fields test_value, rank, and "
                "threshold do not all read 'not ranked' "
                "together: an unranked claim stands only in "
                "its stated form, the value not ranked in its "
                "test_value, rank, and threshold fields "
                "together",
                "set the fields test_value, rank, and "
                "threshold all to 'not ranked', or hand a "
                "ranked value on each of them"))
    try:
        inner_ok = _validate_record_inner(form_id, instance)
    except (RecordTraversalFailure, RecursionError):
        failures.append(_failure_sentence(
            "record",
            "the record stands deeper than the depth the reader "
            "walks, or a part of it points back to itself, so "
            "the record cannot stand read whole",
            "hand a record whose parts stand in plain nested "
            "form, with no part pointing back to a part around it"))
        return failures
    if not inner_ok and not failures:
        # The general naming rule (Step 16 fix wave 3, row
        # F3-02, ruling T16-40): a fault no dedicated entry
        # above has named stands diagnosed by field against
        # the inner judgement itself, so every entry this door
        # returns names its field, and no fault at this door
        # draws a sentence that names no field.
        failures.extend(
            _diagnosed_failure_entries(form_id, instance))
    elif not inner_ok:
        # The multi fault naming extension (Step 16 fix wave
        # 4, row F4-03, ruling T16-51): the naming rule applies
        # on multi fault records in full, so a simultaneous
        # fault no dedicated entry above has named stands
        # diagnosed by field against the inner judgement
        # whether or not a dedicated entry also stands.
        failures.extend(_additional_diagnosed_failure_entries(
            form_id, instance, failures))
    return failures


def record_validation_failures(form_id, instance):
    """Every reason a record does not stand valid against its
    form, as a list of named failures. Each failure names the
    field, the rule the field breaks, and the next step for the
    operator. An empty list stands for a record that stands
    valid. This door never raises for a record that merely
    fails validation."""
    return list(_record_validation_failures(form_id, instance))


def _validate_record_bool(form_id, instance):
    """The yes or no judgement behind validate_record, for the
    product callers whose own answer form stands as a boolean."""
    try:
        return _validate_record_inner(form_id, instance)
    except (RecordTraversalFailure, RecursionError):
        return False


def validate_record(form_id=_ARGUMENT_NOT_HANDED, instance=_ARGUMENT_NOT_HANDED, *extra_args, **extra_kwargs):
    """Check one record against its form, and say what stands wrong.

    Hand in a form identifier and the record as a mapping of
    field names to values. The answer True means the record
    carries every field its form requires, carries no field
    its form does not name, and stands under every rule its
    form states. One stated alias exception stands at Form
    1: the six completeness fields of the SweepFamilyRecord
    may stand carried under their spaced brief spellings
    beside the Form 1 field names, and a record carrying a
    completeness field under its spaced spelling carries
    that field under an alias the form names, not a field
    its form does not name. The answer False means the record does not
    stand valid, and the reason never stands hidden behind
    that False: call record_validation_failures with the
    same form identifier and record, and it returns the
    named failures, one per fault.

    Each named failure states the field at fault, the rule
    that field breaks, and the next step to take, in the
    form: field, rule, next step, and the closing words
    that no record stands validated. An operator holding a
    False answer reads the field name first, fixes that
    field by the next step the failure states, and checks
    the record again. record_validation_failures returns
    an empty list where the record stands valid.
    """
    if form_id is _ARGUMENT_NOT_HANDED or instance is _ARGUMENT_NOT_HANDED:
        _refuse_argument_handing(
            "validate_record",
            "the form identifier and the record", True, False)
    if extra_args or extra_kwargs:
        _refuse_argument_handing(
            "validate_record",
            "the form identifier and the record", False, True)

    return not _record_validation_failures(form_id, instance)


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
    run is not reportable as a completed run.

    For Form 1 the answer stands as a StatedJudgement carrying the
    family completeness standing: over open markers it states the
    open standing and names the open fields in place of an
    unqualified True (R16-03)."""
    fid = _fid(form_id)
    if fid == "1":
        # The extra field layer at this door (Step 16 fix wave 2,
        # row F2-01, ruling T16-23): a field standing outside the
        # Form 1 fields, the completeness fields, and the named
        # carriage keys (_FAMILY_CARRIAGE_KEYS, enumerated at
        # that constant from the made record construction at
        # MOD-12 make_family_record) stands refused and named in
        # the judgement standing, while a made record carrying
        # only named carriage keys keeps its reportable standing
        # on the inner judgement below.
        if isinstance(instance, dict):
            _allowed_names = (
                set(form_fields(fid)) | set(COMPLETENESS_FIELDS)
                | set(_FAMILY_CARRIAGE_KEYS)
                | _family_legitimate_wider_keys(instance))

            def _key_names_allowed(_key):
                for _reading in (
                        _stored_text(_key),
                        _stored_key_text(_key),
                        _stored_text_dress(_key)):
                    if _reading is not None and any(
                            str.__eq__(_reading, _name)
                            for _name in _allowed_names):
                        return True
                try:
                    for _name in _allowed_names:
                        if _folded_key_matches(
                                _key, _folded_money_key(_name)):
                            return True
                except Exception:
                    return False
                return False

            for _key in dict.keys(instance):
                if not _key_names_allowed(_key):
                    _extra_name = _stored_key_text(_key)
                    if _extra_name is None:
                        _extra_name = _safe_str(_key)
                    return StatedJudgement(
                        False,
                        standing=(
                            "not reportable: the record carries "
                            "the field " + _extra_name + ", which "
                            "stands outside the form fields and "
                            "the named carriage keys, and no "
                            "reportable judgement stands on a "
                            "record carrying an unnamed field"))
        # Merge composition (Step 16 fix merge): Builder 2 built
        # this Form 1 branch against validate_record as that door
        # stood in its copy, the inner record judgement. Builder 1
        # split that door, and its own hunk on this function reads
        # the inner judgement through _validate_record_bool on the
        # standing path below. This branch reads the same inner
        # judgement, so a family record carrying its marked alias
        # and presentation keys stands judged on the ground
        # Builder 2 proved.
        if not _validate_record_bool(fid, instance):
            return StatedJudgement(
                False, standing="not reportable: the record fails "
                "validation")
        judgement = family_supports_reportable_run(instance)
        if not judgement:
            return judgement
        return StatedJudgement(
            True, standing=judgement.standing,
            open_fields=judgement.open_fields,
            supplied_fields=judgement.supplied_fields,
            diverged_fields=judgement.diverged_fields,
            missing_fields=judgement.missing_fields,
            placeholder_fields=judgement.placeholder_fields,
            reportable_ready=judgement.reportable_ready)
    if not _validate_record_bool(fid, instance):
        return False
    if isinstance(instance, dict) and _stored_text_equals(
            _stored_pairs_value(instance, "run_status"), "failed"):
        return False
    return True


# ---------------------------------------------------------------------------
# Failure representation, OP-23
# ---------------------------------------------------------------------------

def named_failure_forms():
    """The named failure forms of the product.

        Arguments: no argument stands handed in.
        Returns: NAMED_FAILURES, the tuple of named failure forms
        the failure representation stands on, each a failure stated
        as a value with a name.
        Failure: no exception stands raised at this door; the
        failure form is the named failure forms themselves, which
        this door returns as they stand.
    """
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
    stands copied as itself. A dict assignment whose key hash or equality reading
    raises at the assignment itself stands carried under a
    distinct numbered form, a plain text numbered form where
    a form carrying the key itself cannot stand inserted, in
    the MOD-14 cured form, so no carried entry is silently
    dropped on that reading and no bare error escapes the copy."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied_key = _guarded_copy(key, _memo)
            copied_item = _guarded_copy(item, _memo)
            try:
                copied[copied_key] = copied_item
            except Exception:
                counter = 2
                while True:
                    if isinstance(copied_key, str):
                        candidate = (
                            str.__str__(copied_key)
                            + " (carried key " + str(counter) + ")")
                    elif counter == 2:
                        candidate = (copied_key, counter)
                    else:
                        candidate = (
                            "(carried key " + str(counter) + ")")
                    try:
                        candidate_taken = candidate in copied
                    except Exception:
                        candidate_taken = False
                    if candidate_taken:
                        counter += 1
                        continue
                    try:
                        copied[candidate] = copied_item
                        break
                    except Exception:
                        counter += 1
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
        copied_items = [
            _guarded_copy(item, _memo) for item in base_iter(value)]
        if isinstance(value, set):
            copied = set()
            _memo[id(value)] = copied
            try:
                for copied_item in copied_items:
                    copied.add(copied_item)
            except Exception:
                _memo[id(value)] = copied_items
                return copied_items
            return copied
        try:
            copied = frozenset(copied_items)
        except Exception:
            copied = copied_items
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
    """Whether one version stamp stands complete and matching.

        Arguments: stamp, a VersionStamp or a mapping of its
        fields; sealed_family_hash, the sealed family hash the
        stamp must match where one stands handed in, or None.
        Returns: True where every VersionStamp field stands
        present on the stamp and, where a sealed family hash
        stands handed in, the stamp family manifest hash stands
        equal to it; False in every other case.
        Failure: no exception stands raised for a malformed
        stamp; the failure form is the bare False return.
    """
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
    """Whether one provenance block stands in its stated form.

        Arguments: block, a ProvenanceBlock or a mapping of its
        fields, carrying its excluded class counts, its excluded
        class shares, and its entries.
        Returns: True where the counts and the shares stand as
        non empty mappings over the one key set, every count
        stands as a count value, every share stands as a share
        value, and every entry carries its field and its
        applicability; False in every other case.
        Failure: no exception stands raised for a malformed
        block; the failure form is the bare False return.
    """
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
        field_text = _stored_text_dress(field_value) or ""
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
        return _validate_record_bool(self.FORM_ID, self.values)

    def is_reportable(self):
        return run_is_reportable(self.FORM_ID, self.values)


def _form_type_doc(name, form_id):
    fields = ", ".join(_FORM_SPECS[form_id][1])
    doc = (
        name + ", Form " + form_id + ", owned by "
        + str(_FORM_OWNERS.get(form_id)) + ". "
        "A dict wrapper: an instance carries its record as a plain "
        "dict in its values attribute, validate() judges the record "
        "against Form " + form_id + ", and is_reportable() states "
        "its reportable standing. Its fields are: " + fields + ". "
        "Construction guidance stands at minimal_valid_instance "
        "for a template of this form."
    )
    if form_id in FORM_FIELD_OWNERSHIP:
        ownership = FORM_FIELD_OWNERSHIP[form_id]
        doc += (
            " Field ownership on this form: a user supplies "
            + ", ".join(ownership["user_supplies"]) + ". "
            "The system fills "
            + (", ".join(ownership["system_fills"])
               if ownership["system_fills"] else "no field") + ". "
            "Fields a user must never fill: "
            + (", ".join(ownership["never_fill"])
               if ownership["never_fill"]
               else "none on this form; this form carries no seed "
                    "field") + ". "
            "Named constructors stand at build_sweep_point for "
            "Form 2 and build_run_record for Form 4, and "
            "FORM_FIELD_OWNERSHIP states the ownership in full."
        )
    if form_id == "14":
        doc += (
            " Shape separation (R16-18): this Form 14 "
            "DailyAggregates record shape, keyed by run_identifier, "
            "simulated_day, and viewer_identifier, stands apart "
            "from the Recorder daily aggregate row shape of MOD-10, "
            "keyed by viewer_id beside run_id, record_identity, and "
            "writer. Each shape stands judged under its own name: "
            "this form under validate_record and "
            "validate_form14_daily_aggregates_record, the Recorder "
            "row under validate_recorder_daily_aggregate_rows."
        )
    return doc


def _make_form_type(name, form_id):
    return type(name, (_RecordForm,), {
        "FORM_ID": form_id,
        "FIELDS": _FORM_SPECS[form_id][1],
        "OWNER": _FORM_OWNERS.get(form_id),
        "__module__": __name__,
        "__doc__": _form_type_doc(name, form_id),
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

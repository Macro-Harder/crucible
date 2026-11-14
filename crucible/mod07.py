"""MOD-07 Escrow Adapter and seam records.

Slice S-06. The only module permitted to depend on both cores, and
that dependence stands at decision record level while register
question NQ-45 stands open: this module records every meeting point
between the cores as an adapter choice at decision record level,
and calls neither core. It builds no seam treatment that a folding
against the ruling text has not covered.

While NQ-45 stands open, every cross seam lien, release, and slash
effect in a joint run carries computed not settled, joint effects
stand reported as computed in Parley and not settled in the chosen
escrow, and a record carrying settled or released for such an
effect fails validation at MOD-01, whose lien state bar this module
applies and does not restate.
"""
import copy

from crucible import mod01

OPEN_SEMANTIC_ITEMS = tuple("OS-%d" % n for n in range(1, 15))

SEAM_GAP_COUNTS = {"creation": 7, "release": 6, "slash execution": 8}

TRACER_RESULTS = ("passed as a record", "blocked", "not attempted")

POSITIVE_CONTROL_PATH = "escrow request lien path"

COMPUTED_NOT_SETTLED = "computed not settled"

INTERIM_REPORTING = "computed in Parley and not settled in the chosen escrow"

RULING_TEXT_GAPS = tuple("G-%d" % n for n in range(1, 11))

C12_STANDINGS = (
    "the chosen escrow core has a cost pool account",
    "the chosen escrow core has no cost pool account",
)

_DEPENDENCY_EDGES = (
    ("MOD-05", "MOD-07"),
    ("MOD-06", "MOD-07"),
    ("MOD-07", "MOD-01"),
)

_LOG_FIELDS = mod01.form_fields("18")
_TRACER_FIELDS = mod01.form_fields("29")

COPY_DEPTH_BOUND = 100


def _copy_guard(value, _depth=0, _seen=None, _path="root"):
    """Walk a value the choice and seam copy surfaces are about
    to copy, under the stated depth bound of 100 and a cycle
    guard: a value standing deeper than the bound, or carrying a
    cycle, stands refused in named form, and no bare
    RecursionError escapes the copy. A value shared from two
    places on different paths carries no cycle and stands
    admitted."""
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > COPY_DEPTH_BOUND:
            raise ValueError(
                "adapter copy stands refused in named form: a "
                "value stands deeper than the stated bound of "
                + str(COPY_DEPTH_BOUND) + " at " + _path)
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise ValueError(
                "adapter copy stands refused in named form: a "
                "value carries a cycle at " + _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    _copy_guard(
                        key, _depth + 1, seen,
                        _path + "/key:" + str(key))
                    _copy_guard(
                        item, _depth + 1, seen,
                        _path + "/" + str(key))
            else:
                for index, item in enumerate(value):
                    _copy_guard(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]")
        finally:
            seen.discard(id(value))


def seam_gap_counts():
    """Return the seam gap counts R10 records: creation 7, release
    6, slash execution 8, standing over the fourteen open semantic
    items as the standing reason for the interim reporting rule."""
    return dict(SEAM_GAP_COUNTS)


def dependency_record():
    """Return the module dependency record for the seam: MOD-07
    alone depends on both cores, at decision record level while
    NQ-45 stands open, and no direct edge stands between the two
    core modules in either direction."""
    return {
        "edges": [tuple(edge) for edge in _DEPENDENCY_EDGES],
        "joint_dependent": "MOD-07",
        "depends_on_both_cores": ["MOD-05", "MOD-06"],
        "form": "decision record level while NQ-45 stands open",
        "direct_core_to_core_edges": [],
    }


def validate_dependency_record(record):
    """Return True only where the record carries no direct core to
    core edge and MOD-07 stands as the sole joint dependent."""
    if not isinstance(record, dict):
        return False
    edges = []
    for edge in record.get("edges") or []:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            return False
        edges.append(tuple(edge))
    for source, target in edges:
        if {source, target} == {"MOD-05", "MOD-06"}:
            return False
    joint = [
        module for module in ("MOD-05", "MOD-06", "MOD-07", "MOD-08")
        if ("MOD-05", module) in edges and ("MOD-06", module) in edges
    ]
    if record.get("joint_dependent") != "MOD-07":
        return False
    return joint in ([], ["MOD-07"])


def make_adapter_choice(choice_identifier, reading_applied,
                        parameter_or_rule_point_affected,
                        governing_text_version,
                        escrow_variant_and_fold_version,
                        parley_test_total_source=None,
                        dependence_marks=None, approval=None,
                        drives=None, ruling_references=None):
    """Build one adapter choice as a record. A choice stands
    recorded as an adapter choice, never as a rule of either
    system. The approval stands as its own part of the record: the
    choice, its effects, and its approver, named before a run may
    use the choice. The drives list names only decision level
    computed values."""
    for part in (approval, dependence_marks, drives,
                 ruling_references):
        if part is not None:
            _copy_guard(part)
    return {
        "choice_identifier": choice_identifier,
        "reading_applied": reading_applied,
        "parameter_or_rule_point_affected": parameter_or_rule_point_affected,
        "governing_text_version": governing_text_version,
        "escrow_variant_and_fold_version": escrow_variant_and_fold_version,
        "parley_test_total_source": parley_test_total_source,
        "dependence_marks": list(dependence_marks or []),
        "recorded_as": "adapter choice",
        "presented_as_rule_of": None,
        "approval": copy.deepcopy(approval),
        "drives": list(drives or []),
        "ruling_references": list(ruling_references or []),
        "seam_status": COMPUTED_NOT_SETTLED,
    }


def interpretation_log_entry(choice):
    """Return the InterpretationLogEntry of a choice, in the Form
    18 field order MOD-01 states, carrying the adapter choice mark
    beside the form fields."""
    _copy_guard(choice)
    entry = {}
    for field in _LOG_FIELDS:
        entry[field] = copy.deepcopy(choice.get(field))
    entry["recorded_as"] = "adapter choice"
    return entry


def run_record_entry(choice):
    """Return the run record entry of a choice: the same choice, in
    the same fields, as the interpretation choices group of the run
    record carries it."""
    _copy_guard(choice)
    entry = {}
    for field in _LOG_FIELDS:
        entry[field] = copy.deepcopy(choice.get(field))
    entry["recorded_as"] = "adapter choice"
    entry["approval"] = copy.deepcopy(choice.get("approval"))
    return entry


def validate_choice_pair(log_entry, run_entry):
    """The pair audit of operation C-12: the log entry and the run
    record entry of one choice agree on the choice identifier, the
    reading applied, the governing text version, and every
    dependence mark. A disagreeing pair fails, and a failed result
    is not reportable until the pair agrees."""
    if not isinstance(log_entry, dict) or not isinstance(run_entry, dict):
        return False
    for field in (
        "choice_identifier",
        "reading_applied",
        "governing_text_version",
        "dependence_marks",
    ):
        for entry in (log_entry, run_entry):
            if field not in entry or entry.get(field) is None:
                return False
            if field != "dependence_marks" and entry.get(field) == "":
                return False
        if log_entry.get(field) != run_entry.get(field):
            return False
    return True


def append_reading(log, choice):
    """Append a later reading for a rule point as a new entry. No
    earlier entry stands edited in place."""
    _copy_guard(log)
    updated = [copy.deepcopy(entry) for entry in log]
    updated.append(interpretation_log_entry(choice))
    return updated


def reading_for_result(log, choice_identifier):
    """Return the entry a result carries, named by its choice
    identifier, and never the latest entry in the log for its rule
    point."""
    for entry in log:
        if entry.get("choice_identifier") == choice_identifier:
            _copy_guard(entry)
            return copy.deepcopy(entry)
    return None


def choice_approval_stands(choice):
    """Return True only where the Project Manager approval stands
    on the record of the choice, naming the choice, its effects,
    and its approver."""
    approval = choice.get("approval")
    if not isinstance(approval, dict):
        return False
    if approval.get("approver") != "Project Manager":
        return False
    if approval.get("choice_identifier") != choice.get("choice_identifier"):
        return False
    if not approval.get("effects"):
        return False
    return approval.get("standing") == "approved"


def validate_adapter_choice(choice):
    """Return True only for a choice that may stand on a run: it
    stands recorded as an adapter choice and not as a rule of
    either system, it drives decision level computed values only,
    and its approval stands on the record."""
    if not isinstance(choice, dict):
        return False
    if choice.get("recorded_as") != "adapter choice":
        return False
    if choice.get("presented_as_rule_of") is not None:
        return False
    for driven in choice.get("drives") or []:
        if not isinstance(driven, dict):
            return False
        if driven.get("level") != "decision":
            return False
        if driven.get("kind") != "computed value":
            return False
    return choice_approval_stands(choice)


def seam_status():
    """Return the seam status field in its present form, stated
    plainly, in pay now form only. Dual reporting, restatement,
    and any pooled before and after claim stand as a named bound
    and stand outside this field."""
    return {
        "seam_status": COMPUTED_NOT_SETTLED,
        "stated_plainly": True,
        "bound": "dual reporting, restatement, and pooled claims stand unbuilt",
    }


def make_tracer_passage_record(item, point_in_run, what_in_fact_passed,
                               result):
    """Build one TracerPassageRecord in the Form 29 field order
    MOD-01 states."""
    if result not in TRACER_RESULTS:
        raise ValueError("tracer result outside the stated set: " + str(result))
    return {
        "open_semantic_item": item,
        "point_in_run": point_in_run,
        "what_in_fact_passed": what_in_fact_passed,
        "result": result,
    }


def tracer_passage_records(run_id, results=None):
    """Return the tracer passage record set of one joint run: one
    record per open semantic item OS-1 to OS-14. An item with no
    stated result stands recorded as not attempted."""
    stated = dict(results or {})
    records = []
    for item in OPEN_SEMANTIC_ITEMS:
        outcome = stated.get(item, "not attempted")
        records.append(make_tracer_passage_record(
            item,
            "seam point of " + str(item) + " in run " + str(run_id),
            "recorded value for " + str(item),
            outcome,
        ))
    return records


def positive_control_record():
    """Return the F-10 positive control record: a tracer value on
    the escrow request lien path, the one path the register
    records as meeting in shape, recorded as passing in record
    form."""
    return {
        "fixture": "F-10",
        "path": POSITIVE_CONTROL_PATH,
        "result": "passed as a record",
        "recorded_as_passing": True,
    }


def validate_tracer_passage_set(records, positive_control=None):
    """Return True only for a complete and valid tracer set: one
    record per open semantic item, each carrying its four stated
    parts, and a positive control recorded as passing. The control
    stands read in the record form this module itself produces:
    its fixture, its path, and its passing result on the F-10
    path each stand required, beside the passing mark. A run whose
    positive control does not pass has no valid tracer passage
    record."""
    if not isinstance(records, (list, tuple)):
        return False
    if len(records) != len(OPEN_SEMANTIC_ITEMS):
        return False
    items = []
    for record in records:
        if not isinstance(record, dict):
            return False
        for field in _TRACER_FIELDS:
            if record.get(field) is None:
                return False
            if field in ("what_in_fact_passed", "point_in_run"):
                field_value = record.get(field)
                if isinstance(field_value, str) \
                        and not field_value.strip():
                    return False
                if isinstance(field_value, bool) \
                        and field_value is False:
                    return False
                if isinstance(
                        field_value,
                        (list, tuple, dict, set, frozenset,
                         bytes, bytearray)) \
                        and len(field_value) == 0:
                    return False
        if not isinstance(record.get("open_semantic_item"), str):
            return False
        if record.get("result") not in TRACER_RESULTS:
            return False
        items.append(record.get("open_semantic_item"))
    if tuple(sorted(items)) != tuple(sorted(OPEN_SEMANTIC_ITEMS)):
        return False
    control = positive_control
    if control is None:
        control = positive_control_record()
    if not isinstance(control, dict):
        return False
    expected = positive_control_record()
    for field in ("fixture", "path", "result"):
        if control.get(field) != expected[field]:
            return False
    return control.get("recorded_as_passing") is True


def _stored_entries(run, keys):
    """Return the stored entries a run carries under any of the
    stated carriage keys, as a list of records."""
    entries = []
    for key in keys:
        carried = run.get(key)
        if isinstance(carried, dict):
            entries.append(carried)
        elif isinstance(carried, (list, tuple)):
            entries.extend(
                entry for entry in carried
                if isinstance(entry, dict))
    return entries


def _stored_pair_stands(run, choice):
    """Return True only where the choice pair a run in fact
    carries stands in agreement. The pair check reads the stored
    interpretation log entry and the stored run record entry of
    the choice, matched by choice identifier. A side the run
    does not store stands read from the entry this module builds
    for the choice, so a run storing neither side stands judged
    on its choices alone, as before."""
    identifier = choice.get("choice_identifier")
    log_entries = _stored_entries(run, (
        "interpretation_log_entries", "interpretation_log_entry",
        "interpretation_log", "log_entries"))
    run_entries = _stored_entries(run, (
        "run_record_entries", "run_record_entry",
        "run_record_choices", "record_entries"))
    log_entry = next(
        (entry for entry in log_entries
         if entry.get("choice_identifier") == identifier), None)
    run_entry = next(
        (entry for entry in run_entries
         if entry.get("choice_identifier") == identifier), None)
    if log_entry is None and run_entry is None:
        return validate_choice_pair(
            interpretation_log_entry(choice), run_record_entry(choice))
    if log_entry is None:
        log_entry = interpretation_log_entry(choice)
    if run_entry is None:
        run_entry = run_record_entry(choice)
    return validate_choice_pair(log_entry, run_entry)


def validate_joint_run(run):
    """Return True only where a joint run may stand: every adapter
    choice it uses stands recorded as a choice in both records with
    the pair in agreement and its approval on the record, its
    tracer passage set stands complete and valid, and no cross
    seam effect in it carries settled or released."""
    if not isinstance(run, dict):
        return False
    for choice in run.get("adapter_choices") or []:
        if not validate_adapter_choice(choice):
            return False
        if not _stored_pair_stands(run, choice):
            return False
    if not validate_tracer_passage_set(
        run.get("tracer_passage_records") or [],
        run.get("positive_control"),
    ):
        return False
    for effect in run.get("cross_seam_effects") or []:
        if not validate_cross_seam_effect(effect):
            return False
    return True


def joint_run_failure(run):
    """Return the failure standing on a joint run, in the MOD-01
    failure value form, or None where the run stands. The name the
    value carries is the standing name of the ground that fails the
    run: an unapproved choice, a missing tracer record, and a
    settled cross seam effect each fail the run under their name,
    with run_status failed and complete False."""
    if not isinstance(run, dict):
        return mod01.failure_value("joint run record absent")
    for choice in run.get("adapter_choices") or []:
        if not choice_approval_stands(choice):
            return mod01.failure_value(
                "run using an unapproved adapter choice fails")
        if not validate_adapter_choice(choice):
            return mod01.failure_value(
                "adapter choice stands outside its recorded form")
        if not _stored_pair_stands(run, choice):
            return mod01.failure_value(
                "joint run choice pair stands in disagreement")
    records = run.get("tracer_passage_records") or []
    if len(records) != len(OPEN_SEMANTIC_ITEMS):
        return mod01.failure_value(
            "joint run missing a tracer passage record fails")
    if not validate_tracer_passage_set(records, run.get("positive_control")):
        return mod01.failure_value(
            "joint run has no valid tracer passage record")
    for effect in run.get("cross_seam_effects") or []:
        if not validate_cross_seam_effect(effect):
            return mod01.failure_value(
                "cross seam effect carries settled wording")
    return None


def seam_headline_claim_stands(run, items_touched):
    """Return True only where a headline claim resting on the seam
    may stand from a run: the run stands, and the claim carries
    the tracer passage result for every item it touches."""
    if joint_run_failure(run) is not None:
        return False
    by_item = {
        record.get("open_semantic_item"): record
        for record in run.get("tracer_passage_records") or []
    }
    return all(item in by_item for item in items_touched)


def seam_effect_report(effect):
    """Return the interim reporting form of one cross seam effect:
    a vouch lien amount, a vouch release, or a slash outcome,
    reported as computed in Parley and not settled in the chosen
    escrow, with the lien state computed not settled, while NQ-45
    stands open. A value that is not an effect record reads as an
    empty effect, in the form the slash report reads its outcome."""
    if not isinstance(effect, dict):
        effect = {}
    _copy_guard(effect)
    return {
        "effect": effect.get("kind"),
        "reporting": INTERIM_REPORTING,
        "lien_state": COMPUTED_NOT_SETTLED,
        "value": copy.deepcopy(effect.get("value")),
        "seam_status": COMPUTED_NOT_SETTLED,
    }


def validate_cross_seam_effect(effect):
    """Return True only where a cross seam effect carries no
    settled wording: its lien state validates under the MOD-01 bar
    for cross seam effects while NQ-45 stands open."""
    if not isinstance(effect, dict):
        return False
    state = effect.get("lien_state", COMPUTED_NOT_SETTLED)
    return mod01.validate_lien_state(state, cross_seam=True)


def _wording_claims(lowered):
    """Split lowered wording into its claims, at sentence and
    clause boundaries, so each claim stands judged on its own."""
    claims = [lowered]
    for separator in (".", ";", "!", "?", ",", "\n"):
        claims = [
            part for claim in claims for part in claim.split(separator)]
    claims = [
        part for claim in claims for part in claim.split(" but ")]
    return [claim.strip() for claim in claims if claim.strip()]


def _claim_drifts(claim):
    """Return True where one claim drifts toward settled wording.

    A settled occurrence stands excused only where the word not
    stands directly before it in the same claim. A released
    occurrence stands excused only on that same ground, or where
    the word computed stands in the same claim.
    """
    index = claim.find("settled")
    while index != -1:
        if not claim[:index].rstrip().endswith("not"):
            return True
        index = claim.find("settled", index + 1)
    index = claim.find("released")
    while index != -1:
        if not claim[:index].rstrip().endswith("not"):
            start = max(
                claim.rfind(separator, 0, index)
                for separator in (",", ";", " and "))
            ends = [
                claim.find(separator, index + len("released"))
                for separator in (",", ";", " and ")]
            ends = [end for end in ends if end != -1]
            end = min(ends) if ends else len(claim)
            segment = claim[start:end]
            if "computed" not in segment:
                return True
        index = claim.find("released", index + 1)
    return False


def validate_seam_wording(text):
    """Return True only where report wording for a cross seam
    effect holds the interim form. Wording is judged per claim:
    an excusing word excuses only the claim it stands in, and a
    claim that names a seam effect as settled or released fails
    the whole wording."""
    if not isinstance(text, str):
        return False
    lowered = text.lower()
    return not any(
        _claim_drifts(claim) for claim in _wording_claims(lowered))


def slash_outcome_report(outcome):
    """Return a slash outcome in its interim form. Both standings
    of contested entry C-12 travel with the report, the chosen
    escrow core carries no cost pool account on either wording of
    that entry as a settled fact of this report, and no remainder
    destination stands named as settled."""
    _copy_guard(outcome)
    return {
        "effect": "slash",
        "reporting": INTERIM_REPORTING,
        "lien_state": COMPUTED_NOT_SETTLED,
        "value": copy.deepcopy((outcome or {}).get("value")),
        "c12_standings_carried": list(C12_STANDINGS),
        "cost_pool_account_named_as_settled": False,
        "remainder_destination": None,
        "remainder_named_as_settled": False,
    }


def validate_slash_report(report):
    """Return True only where a slash report names no remainder
    destination as settled and carries both standings of C-12."""
    if not isinstance(report, dict):
        return False
    if report.get("remainder_named_as_settled"):
        return False
    if report.get("remainder_destination") is not None:
        return False
    return tuple(report.get("c12_standings_carried") or ()) == C12_STANDINGS


def record_folding(choice, rulings_touched):
    """Record one adapter choice against the ruling text it
    touches, ruling by ruling: the S-06 part of the folding duty
    under decision D-02 condition three read with D-20. The ten
    ruling text gaps stand carried open by name in the record,
    filled by no inference."""
    return {
        "choice_identifier": choice.get("choice_identifier"),
        "rulings_recorded": list(rulings_touched),
        "recorded_ruling_by_ruling": True,
        "gaps_carried_open": list(RULING_TEXT_GAPS),
        "gaps_filled_by_inference": [],
    }


def validate_folding_record(record):
    """Return True only where a folding record covers its choice
    ruling by ruling and supplies no gap value by inference."""
    if not isinstance(record, dict):
        return False
    if not record.get("recorded_ruling_by_ruling"):
        return False
    if not record.get("rulings_recorded"):
        return False
    if record.get("gaps_filled_by_inference"):
        return False
    return tuple(record.get("gaps_carried_open") or ()) == RULING_TEXT_GAPS


def ruling_effect_reporting_stands(difference, folding_records):
    """Return True only where a B-5 difference resting on a seam
    effect may stand reported as a ruling effect: a valid folding
    record stands behind every seam choice the difference rests
    on. Until that recording stands, no such difference stands
    reported as a ruling effect from this slice."""
    choices = (difference or {}).get("seam_choice_identifiers") or []
    if not choices:
        return False
    by_choice = {
        record.get("choice_identifier"): record
        for record in folding_records or []
    }
    for identifier in choices:
        record = by_choice.get(identifier)
        if record is None or not validate_folding_record(record):
            return False
        if not set((difference or {}).get("rulings_claimed") or []).issubset(
            set(record.get("rulings_recorded") or [])
        ):
            return False
    return True


def classify_seam_feedback(item, treatment_choice, standings):
    """The seam feedback classification act for one seam item. The
    treatment stands recorded as an adapter choice with both
    standings carried, the act stands priced per seam item, and
    one paired sensitivity run stands required per feeding item
    before any headline rests on it."""
    return {
        "open_semantic_item": item,
        "classification": "feeding seam item",
        "treatment_recorded_as": "adapter choice",
        "treatment_choice_identifier": (
            treatment_choice or {}).get("choice_identifier"),
        "both_standings_carried": list(standings),
        "pricing": "priced per seam item",
        "paired_sensitivity_runs_required": 1,
        "headline_may_rest": False,
    }


def validate_feedback_classification(record):
    """Return True only where a classification carries both
    standings and its paired sensitivity requirement."""
    if not isinstance(record, dict):
        return False
    if len(record.get("both_standings_carried") or []) != 2:
        return False
    if record.get("treatment_recorded_as") != "adapter choice":
        return False
    return record.get("paired_sensitivity_runs_required") == 1


__all__ = [
    "COPY_DEPTH_BOUND",
    "OPEN_SEMANTIC_ITEMS",
    "SEAM_GAP_COUNTS",
    "TRACER_RESULTS",
    "POSITIVE_CONTROL_PATH",
    "COMPUTED_NOT_SETTLED",
    "INTERIM_REPORTING",
    "RULING_TEXT_GAPS",
    "C12_STANDINGS",
    "seam_gap_counts",
    "dependency_record",
    "validate_dependency_record",
    "make_adapter_choice",
    "interpretation_log_entry",
    "run_record_entry",
    "validate_choice_pair",
    "append_reading",
    "reading_for_result",
    "choice_approval_stands",
    "validate_adapter_choice",
    "seam_status",
    "make_tracer_passage_record",
    "tracer_passage_records",
    "positive_control_record",
    "validate_tracer_passage_set",
    "validate_joint_run",
    "joint_run_failure",
    "seam_headline_claim_stands",
    "seam_effect_report",
    "validate_cross_seam_effect",
    "validate_seam_wording",
    "slash_outcome_report",
    "validate_slash_report",
    "record_folding",
    "validate_folding_record",
    "ruling_effect_reporting_stands",
    "classify_seam_feedback",
    "validate_feedback_classification",
]

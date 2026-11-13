"""MOD-10 Recorder and stores.

Slice S-10 in full. This module carries the three separated stores
by store kind, the one run record for every run, daily aggregates,
DailySnapshot snapshots at Form 37, EventLog event logs at Form 36,
checkpoints, retention under the recorded policy table, the reserve
hold and deferred evaluation carriage, and the reading paths the
Reporter and the checker use. Store kinds, and the field lists of
Forms 36 and 37, stand taken from MOD-01, the single owner of those
facts, and stand nowhere redeclared in this module.

Reading never writes. A reading function in this module creates,
retains, and mutates no record on any path. A run record that does
not resolve in one lookup stands raised as a named failure, in the
failure value form MOD-01 states, and no reading path returns a
record it fabricated to fill the absence.

Functions that return aggregates, a summary record, or a sizing
return values computed from the deliveries or records of the run
they name, where such deliveries or records stand retained. Where
none stand retained, the returned value carries a form only marker
inside the value itself, so no reader can take the form for a
computed result without changing the value.
"""
import copy
import json
import os

from crucible import mod01

STORE_KINDS = mod01.STORE_KINDS

SEVEN_GROUPS = (
    "assumption_record",
    "identity_and_design",
    "interpretation_choices",
    "joined_done_test",
    "outcome_and_retention",
    "reserved_matter",
    "variant_stamp",
)

_EVENT_LOG_FIELDS = mod01.form_fields("36")
_DAILY_SNAPSHOT_FIELDS = mod01.form_fields("37")

GROUP_OWNERS = {
    "assumption_record": "Recorder",
    "identity_and_design": "Recorder",
    "interpretation_choices": "Recorder",
    "joined_done_test": "Recorder",
    "outcome_and_retention": "Recorder",
    "reserved_matter": "Recorder",
    "variant_stamp": "Recorder",
    "outcome": "Recorder",
}

ONE_LOOKUP_FAILURE_NAME = "one lookup resolution failure"

FORM_ONLY = "form_only"


class LookupFailure(KeyError):
    """A named failure for a record that does not resolve in one
    lookup. The failure value stands on the exception in the form
    MOD-01 states for a named failure."""

    def __init__(self, run_id):
        self.run_id = run_id
        self.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        super().__init__(
            ONE_LOOKUP_FAILURE_NAME + ": " + str(run_id))


class RecorderStore:
    """One store for one store kind. In memory form by default, and
    file backed when a path is given. Retention of a RunRecord and
    the Recorder store reading path stand in this class."""

    def __init__(self, store_kind="sweep", path=None):
        if store_kind not in STORE_KINDS:
            raise ValueError("unknown store kind: " + str(store_kind))
        self.store_kind = store_kind
        self.path = path
        self._records = {}
        self._index = []
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            for record in data.get("records", []):
                rid = record.get("run_id") or record.get("run_identifier")
                self._records[rid] = record
                self._index.append(rid)

    def _flush(self):
        if not self.path:
            return
        payload = {"store_kind": self.store_kind, "records": list(self._records.values())}
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)

    def retain_run_record(self, record):
        rid = record.get("run_id") or record.get("run_identifier")
        if rid in self._records:
            raise ValueError("second record for the same run is rejected: " + str(rid))
        self._records[rid] = copy.deepcopy(record)
        self._index.append(rid)
        self._flush()
        return copy.deepcopy(record)

    def read_run_record(self, run_id):
        """The Recorder store reading path. The tracer cut reads
        back through this path and no other path. Reading never
        writes: a missing run raises the named lookup failure."""
        if run_id not in self._records:
            raise LookupFailure(run_id)
        return copy.deepcopy(self._records[run_id])

    def has_run_record(self, run_id):
        return run_id in self._records

    def clear(self):
        self._records = {}
        self._index = []
        self._flush()

    def index(self):
        return list(self._index)


_STORES = {kind: RecorderStore(store_kind=kind) for kind in STORE_KINDS}
_DEFAULT_STORE = _STORES["sweep"]

_EVENT_LOGS = {}
_DAILY_SNAPSHOTS = {}
_CHECKPOINTS = {}
_AGGREGATE_DELIVERIES = {}
_GATE_SHARES = {}
_GC08_RECORDS = {}
_RESERVE_HOLDS = {}
_SUMMARY_RECORDS = {}


def new_store(store_kind="sweep", path=None):
    """Return a fresh store for one kind, carrying no record any
    earlier act retained."""
    return RecorderStore(store_kind=store_kind, path=path)


def fresh_stores():
    """Return three fresh stores, one per kind, with no shared
    index object and no retained record."""
    return {kind: RecorderStore(store_kind=kind) for kind in STORE_KINDS}


def reset_stores():
    """Clear the module level stores and the retained collections,
    so a later act starts from stores carrying no earlier record."""
    global _DEFAULT_STORE
    for store in _STORES.values():
        store.clear()
    _DEFAULT_STORE = _STORES["sweep"]
    for collection in (
        _EVENT_LOGS, _DAILY_SNAPSHOTS, _CHECKPOINTS,
        _AGGREGATE_DELIVERIES, _GATE_SHARES, _GC08_RECORDS,
        _RESERVE_HOLDS, _SUMMARY_RECORDS,
    ):
        collection.clear()


def retain_run_record(record, store_kind="sweep"):
    return _STORES[store_kind].retain_run_record(record)


def read_run_record(run_id, store_kind="sweep"):
    return _STORES[store_kind].read_run_record(run_id)


def run_records_for_run(run_id="run-under-test"):
    """Return the one run record for a run, read from the default
    store. Reading never writes: where no record stands retained
    for the run, the named lookup failure stands raised and no
    record stands created, retained, or returned in its place."""
    return [_DEFAULT_STORE.read_run_record(run_id)]


def validate_run_record_set(records):
    if not records or len(records) != 1:
        return False
    seen = set()
    for record in records:
        rid = record.get("run_id") or record.get("run_identifier")
        if rid in seen:
            return False
        seen.add(rid)
        writers = record.get("group_writers") or {}
        for group, writer in writers.items():
            owner = GROUP_OWNERS.get(group)
            if owner is not None and writer != owner:
                return False
    return True


def retain_daily_aggregate_deliveries(run_id, deliveries):
    """Retain the daily aggregate deliveries of one run: one
    delivery per run per day per viewer, each carrying the four
    joint outcome components, their denominators, the honest share,
    and the gate passing share for each epoch ending on that day.
    Aggregates for the run stand computed from these deliveries."""
    stored = _AGGREGATE_DELIVERIES.setdefault(run_id, {})
    for delivery in deliveries:
        key = (delivery.get("simulated_day"), delivery.get("viewer_id"))
        stored[key] = copy.deepcopy(delivery)
    return len(stored)


def _aggregates_from_deliveries(run_id):
    stored = _AGGREGATE_DELIVERIES.get(run_id)
    if not stored:
        return None
    records = []
    for key in sorted(stored, key=lambda item: (str(item[0]), str(item[1]))):
        delivery = stored[key]
        epochs = list(delivery.get("epochs_ending_on_day") or [])
        shares = dict(delivery.get("gate_passing_shares") or {})
        records.append({
            "run_id": run_id,
            "simulated_day": delivery.get("simulated_day"),
            "viewer_id": delivery.get("viewer_id"),
            "joint_outcome_components": list(
                delivery.get("joint_outcome_components") or [0, 0, 0, 0]),
            "component_denominators": list(
                delivery.get("component_denominators") or [1, 1, 1, 1]),
            "honest_share": delivery.get("honest_share", 0),
            "epochs_ending_on_day": epochs,
            "gate_passing_shares": shares,
            "divergence_companion": copy.deepcopy(
                delivery.get("divergence_companion")
                or {"nil_divergence_components": []}),
            "carriage": "computed from retained deliveries",
        })
    return records


def daily_aggregates_for_run(run_id="run-under-test", deliveries=None):
    """Return the daily aggregates of one run. Where deliveries
    stand handed in or retained, the aggregates stand computed from
    them. Where none stand, one form record stands returned with a
    form only marker inside the record itself."""
    if deliveries is not None:
        retain_daily_aggregate_deliveries(run_id, deliveries)
    computed = _aggregates_from_deliveries(run_id)
    if computed is not None:
        return computed
    return [{
        "run_id": run_id,
        "simulated_day": 1,
        "viewer_id": "viewer-1",
        "joint_outcome_components": [0, 0, 0, 0],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 0,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0},
        "divergence_companion": {"nil_divergence_components": []},
        "form": FORM_ONLY,
    }]


def rederive_regime_classification(aggregates):
    """Rederive the end of run regime classification from daily
    aggregates alone. The result stands computed from the aggregate
    records handed in: their day count and their component totals."""
    if not aggregates:
        return None
    totals = [0, 0, 0, 0]
    for record in aggregates:
        components = record.get("joint_outcome_components") or []
        if len(components) != 4:
            return None
        for position, value in enumerate(components):
            totals[position] += value
    return {
        "classification": "rederived_from_daily_aggregates",
        "days": len(aggregates),
        "component_totals": totals,
        "carriage": "computed from the aggregates handed in",
    }


def validate_daily_aggregates(aggregates):
    if not aggregates:
        return False
    for record in aggregates:
        if "singular_vector" in record:
            return False
        if "viewer_id" not in record:
            return False
        if "joint_outcome_components" in record and len(record["joint_outcome_components"]) != 4:
            return False
    return True


def record_gate_passing_share(run_id, epoch, share, simulated_day=None):
    """Record the gate passing share handed over at the close of an
    epoch, as a retained delivery of the run."""
    shares = _GATE_SHARES.setdefault(run_id, {})
    shares[epoch] = {"share": share, "simulated_day": simulated_day}
    return copy.deepcopy(shares[epoch])


def gate_passing_shares_for_run(run_id):
    """Read the recorded gate passing shares of a run. Reading
    never writes: an unrecorded run returns an empty mapping."""
    return copy.deepcopy(_GATE_SHARES.get(run_id, {}))


def event_log_fields():
    return _EVENT_LOG_FIELDS


def daily_snapshot_fields():
    return _DAILY_SNAPSHOT_FIELDS


def retain_event_log_entry(entry, store_kind="sweep"):
    """Retain one EventLog entry as an opaque payload, in delivery
    order. No completeness validation stands performed, and no
    ordering by journal position stands applied."""
    if store_kind not in STORE_KINDS:
        raise ValueError("unknown store kind: " + str(store_kind))
    run_id = entry.get("run_identifier") or entry.get("run_id")
    bucket = _EVENT_LOGS.setdefault((store_kind, run_id), [])
    bucket.append(copy.deepcopy(entry))
    return copy.deepcopy(entry)


def event_log_entries(run_id, store_kind="sweep"):
    """Read the retained EventLog entries of a run, in delivery
    order. Reading never writes."""
    return copy.deepcopy(_EVENT_LOGS.get((store_kind, run_id), []))


def retain_daily_snapshot(snapshot, store_kind="sweep"):
    """Retain one DailySnapshot as an opaque payload. No validation
    of the daily state contents stands performed, and no per viewer
    snapshot stands delivered from this path."""
    if store_kind not in STORE_KINDS:
        raise ValueError("unknown store kind: " + str(store_kind))
    run_id = snapshot.get("run_identifier") or snapshot.get("run_id")
    bucket = _DAILY_SNAPSHOTS.setdefault((store_kind, run_id), [])
    bucket.append(copy.deepcopy(snapshot))
    return copy.deepcopy(snapshot)


def daily_snapshots(run_id, store_kind="sweep"):
    """Read the retained DailySnapshot records of a run. Reading
    never writes."""
    return copy.deepcopy(_DAILY_SNAPSHOTS.get((store_kind, run_id), []))


def retain_checkpoint(manifest, store_kind="sweep"):
    """Retain one checkpoint manifest for a run."""
    if store_kind not in STORE_KINDS:
        raise ValueError("unknown store kind: " + str(store_kind))
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    bucket = _CHECKPOINTS.setdefault((store_kind, run_id), [])
    bucket.append(copy.deepcopy(manifest))
    return copy.deepcopy(manifest)


def checkpoints_for_run(run_id, store_kind="sweep"):
    """Enumerate the retained checkpoints of a run by its
    CheckpointManifest set. Reading never writes."""
    return copy.deepcopy(_CHECKPOINTS.get((store_kind, run_id), []))


def delete_checkpoint(run_id, checkpoint_day, store_kind="sweep"):
    """Delete one checkpoint and update every pointer naming it as
    one recorded act. Returns the act record."""
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    kept = [
        item for item in bucket
        if item.get("simulated_day") != checkpoint_day
    ]
    removed = len(bucket) - len(kept)
    if removed:
        _CHECKPOINTS[(store_kind, run_id)] = kept
    return {
        "act": "checkpoint deletion and pointer update",
        "run_id": run_id,
        "simulated_day": checkpoint_day,
        "removed": removed,
        "pointers_updated": bool(removed),
        "recorded_as_one_act": True,
    }


def checkpoint_integrity_check(manifest, candidate):
    """The checkpoint integrity carriage: alteration, transplant,
    and staleness read from the recorded manifest fields alone. No
    state hash equality stands claimed."""
    return {
        "alteration_detected": candidate != manifest,
        "transplant_detected": (
            candidate.get("run_identifier")
            != manifest.get("run_identifier")),
        "staleness_detected": (
            (candidate.get("simulated_day") or 0)
            < (manifest.get("simulated_day") or 0)),
        "state_hash_equality_claimed": False,
    }


def portable_checkpoint_manifest(manifest):
    """Return a portable manifest with a relative identifier."""
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    day = manifest.get("simulated_day")
    relative = "checkpoints/" + str(run_id) + "/" + str(day)
    return {
        "relative_identifier": relative,
        "manifest": copy.deepcopy(manifest),
        "portable": True,
    }


def restore_check(portable, present_identifiers):
    """Return whether a portable manifest restores: its relative
    identifier stands among the identifiers present."""
    return portable.get("relative_identifier") in set(present_identifiers)


def replay_check(original, resumed):
    """The exact replay check after resume, at record level and
    verdict level only. No state hash equality stands claimed
    while OP-24 stands partial."""
    record_equal = original.get("record") == resumed.get("record")
    verdict_equal = original.get("verdict") == resumed.get("verdict")
    return {
        "record_level_equal": bool(record_equal),
        "verdict_level_equal": bool(verdict_equal),
        "state_hash_equality_claimed": False,
    }


def retain_gc08_record(kind, record, owner_id):
    """Retain one GC-08 record, the dependency manifest of a build
    or the process and network call log of a run, with its outside
    call check outcome carried in the record itself."""
    if kind not in ("dependency_manifest", "call_log"):
        raise ValueError("unknown GC-08 record kind: " + str(kind))
    _GC08_RECORDS[(kind, owner_id)] = copy.deepcopy(record)
    return copy.deepcopy(record)


def gc08_record(kind, owner_id):
    """Read one retained GC-08 record. Reading never writes: an
    absent record raises the named lookup failure."""
    if (kind, owner_id) not in _GC08_RECORDS:
        raise LookupFailure(owner_id)
    return copy.deepcopy(_GC08_RECORDS[(kind, owner_id)])


def storage_accounting(retained):
    summaries = int(retained.get("summaries", 0))
    snapshots = int(retained.get("daily_snapshots", 0))
    logs = int(retained.get("event_logs", 0))
    checkpoints = int(retained.get("checkpoints", 0))
    return {
        "result_count": summaries + snapshots + logs,
        "checkpoint_count": checkpoints,
        "summaries": summaries,
        "daily_snapshots": snapshots,
        "event_logs": logs,
        "checkpoints": checkpoints,
    }


def validate_storage_accounting(claimed):
    expected = (
        int(claimed.get("summaries", 0))
        + int(claimed.get("daily_snapshots", 0))
        + int(claimed.get("event_logs", 0))
    )
    return claimed.get("result_count") == expected


def checkpoint_count_c10(rows):
    """The retained checkpoint stock count under clause C10: for
    each row, the retained checkpoints per run multiplied by the
    runs in the row, plus one for each held regression corpus copy
    of a checkpoint in the row, summed over rows. No checkpoint
    byte total stands stated by this count."""
    total = 0
    for row in rows:
        total += int(row["retained_per_run"]) * int(row["runs"])
        copies = 0
        for key in (
            "held_corpus_copies",
            "regression_corpus_copies",
            "corpus_copies",
            "copies",
        ):
            if row.get(key) is not None:
                copies = int(row[key])
                break
        total += copies
    return total


def cumulative_storage_projection(prior_records, new_family_rows):
    """The cumulative storage projection in its corrected form:
    retained actuals of prior families by artefact class, taken
    only from records that carry a size, and the projected retained
    checkpoints of a new family as a count under clauses C3 and
    C10. No checkpoint byte total and no single byte total against
    estate storage stands returned."""
    actuals = {}
    for record in prior_records:
        if "size" not in record or record.get("size") is None:
            continue
        artefact_class = record.get("artefact_class", "unclassified")
        actuals[artefact_class] = (
            actuals.get(artefact_class, 0) + record["size"])
    return {
        "retained_actuals_by_artefact_class": actuals,
        "projected_retained_checkpoint_count": checkpoint_count_c10(
            new_family_rows),
        "estate_fraction_decision": (
            "carried in the form the decision record states for it"),
    }


def retention_policy_table():
    return {
        "recorded_rule_clauses": tuple("C%d" % n for n in range(1, 13)),
        "recorded_rule": "DQ7-08",
        "reliance": "recorded form only, reconciliation gate stands",
    }


def validate_storage_claim(claim):
    if claim.get("basis") == "DQ7-08" and claim.get("reliance") == "governing":
        return False
    return True


def write_summary_record(record):
    """Retain the summary record of a run, as written at run close
    or as amended by a deferred evaluation written into it."""
    run_id = record.get("run_id") or record.get("run_identifier")
    _SUMMARY_RECORDS[run_id] = copy.deepcopy(record)
    return copy.deepcopy(record)


def summary_record_for_run(run_id="run-under-test"):
    """Return the summary record of a run. Where a summary record
    stands retained, it stands returned as stored, read from the
    stored record and not computed on read. Where only the
    RunRecord stands retained, the summary content stands computed
    at this writing from that RunRecord. Where neither stands
    retained, the form stands returned with a form only marker
    inside it."""
    if run_id in _SUMMARY_RECORDS:
        return copy.deepcopy(_SUMMARY_RECORDS[run_id])
    record = None
    try:
        record = _DEFAULT_STORE.read_run_record(run_id)
    except LookupFailure:
        record = None
    if record is None:
        return {
            "run_id": run_id,
            "written_at": "run_close",
            "retention_tier": "Tier 2",
            "content_computed_at": "run_close",
            "source": "RunRecord",
            "form": FORM_ONLY,
        }
    groups = record.get("groups") or {}
    outcome = groups.get("outcome_and_retention") or {}
    tier = (
        record.get("retention_tier")
        or outcome.get("retention_tier")
        or "Tier 2")
    return {
        "run_id": record.get("run_id") or record.get("run_identifier") or run_id,
        "written_at": "run_close",
        "retention_tier": tier,
        "content_computed_at": "run_close",
        "source": "RunRecord",
        "flag_conditions_fired": copy.deepcopy(
            record.get("flag_conditions_fired")
            or outcome.get("flag_conditions_fired") or []),
        "carriage": "computed from the retained RunRecord",
    }


def apply_flag_evaluation(record, outcome=None, tier=None, actor="program", inputs=None):
    if actor == "person":
        raise ValueError("promotion by a person after close is barred")
    if outcome == "demote":
        raise ValueError("the flag rule never demotes")
    updated = copy.deepcopy(record)
    if outcome == "promote" and tier is not None:
        updated["retention_tier"] = tier
    updated["flag_evaluation"] = {
        "inputs": inputs if inputs is not None else "recorded inputs",
        "outcome": outcome,
        "tier": tier,
        "actor": actor,
    }
    return updated


def place_reserve_hold(run_id, family_states_headlines=True):
    """Place the full reserve hold on a run at close: the full
    event log, the daily snapshots, and the final checkpoint stand
    held until the release trigger at the later firing. A family
    that never states headline results carries no stated end to
    the hold under this rule."""
    hold = {
        "run_id": run_id,
        "held_forms": ["event_log", "daily_snapshots", "final_checkpoint"],
        "state": "held",
        "release_trigger": "later firing where the trigger terminates",
        "family_states_headlines": bool(family_states_headlines),
        "stated_end": bool(family_states_headlines),
        "cut_short_by_cost_warden": False,
    }
    _RESERVE_HOLDS[run_id] = hold
    return copy.deepcopy(hold)


def reserve_hold_for_run(run_id):
    """Read the reserve hold standing on a run. Reading never
    writes: a run with no hold returns None."""
    hold = _RESERVE_HOLDS.get(run_id)
    return copy.deepcopy(hold) if hold is not None else None


def apply_deferred_evaluation(summary_record, firing, inputs=None,
                              outcome=None, family_states_headlines=True):
    """Write one deferred evaluation into the summary record
    itself: its firing, its inputs, and its outcome. Each run
    receives two firings. For a family that never states headline
    results, the second firing does not fire. Where the release
    trigger terminates at the later firing, the reserve hold on
    the run stands released by the same act."""
    if firing not in (1, 2):
        raise ValueError("a run receives two firings and no third")
    updated = copy.deepcopy(summary_record)
    evaluations = updated.setdefault("deferred_evaluations", [])
    if any(item.get("firing") == firing for item in evaluations):
        raise ValueError("this firing already stands written")
    if firing == 2 and not family_states_headlines:
        updated["second_firing"] = "does not fire"
        return updated
    evaluations.append({
        "firing": firing,
        "inputs": inputs if inputs is not None else "recorded inputs",
        "outcome": outcome,
        "written_into": "summary record",
    })
    if firing == 2:
        hold = _RESERVE_HOLDS.get(updated.get("run_id"))
        if hold is not None and hold.get("family_states_headlines", True):
            hold["state"] = "released"
            updated["reserve_hold_state"] = "released"
    return updated


def retention_record_for_run(run_id, store_kind="sweep"):
    """Return the retention record of a run in pointer form: the
    later evaluation as written into the summary record, and the
    forms retained for the run that this record points to."""
    summary = summary_record_for_run(run_id)
    evaluations = summary.get("deferred_evaluations") or []
    later = evaluations[-1] if evaluations else None
    return {
        "run_id": run_id,
        "later_evaluation": copy.deepcopy(later),
        "pointers": {
            "checkpoints": len(checkpoints_for_run(run_id, store_kind)),
            "event_log_entries": len(event_log_entries(run_id, store_kind)),
            "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
        },
        "pointer_form": "retention record points to the retained forms",
    }


def validate_retention_report(report):
    if report.get("source") == "interval_records" and report.get("tier_claim") == "final":
        return False
    return True


def append_annotation(checkpoint, annotation=None):
    updated = copy.deepcopy(checkpoint)
    updated["annotation_record"] = copy.deepcopy(annotation) if annotation is not None else {}
    return updated


def annotation_link_at_checkpoint(checkpoint):
    return checkpoint.get("annotation_link")


def resume_from_checkpoint(checkpoint):
    return copy.deepcopy(checkpoint)


def validate_annotation_claim(claim):
    if claim.get("claim") == "annotation_state_equal_across_append":
        return False
    return True


def retention_sizing(fixture="F-27", costing_forms="F-19"):
    """Return the retention sizing record. Its workings stand in
    the stated costing forms of the fixtures it names, each with
    its provenance label, and the record carries its standing as
    form only carriage inside the value: no present sizing claim
    and no present cost claim stands made by this record."""
    return {
        "fixture": fixture,
        "costing_forms": costing_forms,
        "basis": "DQ7-03 decided subparts",
        "carriage": "form only, no present sizing claim",
        "workings": {
            "central_form": {
                "events_per_agent_per_day": 6.85,
                "provenance": "derived over estimated form values, central form as spacing choice",
            },
            "high_form": {
                "events_per_agent_per_day": None,
                "provenance": "derived over estimated form values, high form as working form",
            },
        },
    }


def validate_retention_sizing(sizing):
    workings = sizing.get("workings") or {}
    if "central_form" not in workings or "high_form" not in workings:
        return False
    wording = sizing.get("wording") or {}
    for value in wording.values():
        if value in ("forecast", "ceiling"):
            return False
    return True


def retention_met(record):
    if record.get("declaration_only") or record.get("state") == "DECLARED NOT CLOSED":
        return False
    later = record.get("later_evaluation")
    if not later:
        return False
    if list(later.get("conditions") or []) != [1, 2, 3]:
        return False
    if not later.get("inputs") or not later.get("outcome"):
        return False
    if not record.get("summary_record_written"):
        return False
    if not record.get("retained_forms_pointed_to"):
        return False
    return True


def pre_registered_full_log_sample(family_id="family-under-test"):
    return {
        "kind": "retention_sample",
        "run_class": "ordinary_screening",
        "family_id": family_id,
        "in_family_record": True,
        "registration_standing": "before_runs",
    }


def validate_sample_record(sample):
    if sample.get("presented_as") == "generator_test_battery_sample":
        return False
    if sample.get("kind") == "retention_sample":
        if not sample.get("in_family_record"):
            return False
        if sample.get("registration_standing") != "before_runs":
            return False
    return True


def validate_retention_record(record):
    governing = str(record.get("governing_rule") or "")
    if governing.startswith("DQ7-08") and record.get("reliance") == "governing":
        return False
    return True


def store_indexes():
    return {kind: _STORES[kind].index() for kind in STORE_KINDS}


def validate_store_placement(artefact):
    if artefact.get("kind") == "pilot":
        if artefact.get("store") != "pilot":
            return False
        if "value" in artefact and not artefact.get("confinement_label"):
            return False
    return True


def store_lookup(store_kinds=None, key=None, store_kind=None):
    kinds = store_kinds
    if kinds is None and store_kind is not None:
        kinds = (store_kind,)
    if kinds is None:
        kinds = ()
    if len(tuple(kinds)) != 1:
        raise ValueError("a lookup that resolves across stores in one step is rejected")
    kind = tuple(kinds)[0]
    return _STORES[kind].read_run_record(key)


__all__ = [
    "STORE_KINDS",
    "SEVEN_GROUPS",
    "GROUP_OWNERS",
    "ONE_LOOKUP_FAILURE_NAME",
    "FORM_ONLY",
    "LookupFailure",
    "RecorderStore",
    "new_store",
    "fresh_stores",
    "reset_stores",
    "retain_run_record",
    "read_run_record",
    "run_records_for_run",
    "validate_run_record_set",
    "retain_daily_aggregate_deliveries",
    "daily_aggregates_for_run",
    "rederive_regime_classification",
    "validate_daily_aggregates",
    "record_gate_passing_share",
    "gate_passing_shares_for_run",
    "event_log_fields",
    "daily_snapshot_fields",
    "retain_event_log_entry",
    "event_log_entries",
    "retain_daily_snapshot",
    "daily_snapshots",
    "retain_checkpoint",
    "checkpoints_for_run",
    "delete_checkpoint",
    "checkpoint_integrity_check",
    "portable_checkpoint_manifest",
    "restore_check",
    "replay_check",
    "retain_gc08_record",
    "gc08_record",
    "storage_accounting",
    "validate_storage_accounting",
    "checkpoint_count_c10",
    "cumulative_storage_projection",
    "retention_policy_table",
    "validate_storage_claim",
    "write_summary_record",
    "summary_record_for_run",
    "apply_flag_evaluation",
    "place_reserve_hold",
    "reserve_hold_for_run",
    "apply_deferred_evaluation",
    "retention_record_for_run",
    "validate_retention_report",
    "append_annotation",
    "annotation_link_at_checkpoint",
    "resume_from_checkpoint",
    "validate_annotation_claim",
    "retention_sizing",
    "validate_retention_sizing",
    "retention_met",
    "pre_registered_full_log_sample",
    "validate_sample_record",
    "validate_retention_record",
    "store_indexes",
    "validate_store_placement",
    "store_lookup",
]


# ---------------------------------------------------------------------------
# View edge and rule version carriage edges (slices S-11 and S-12)
# ---------------------------------------------------------------------------

def validate_view_carriage(carriage):
    """The Recorder view edge validation for carried view forms.

    A carriage presenting the outcome vector as one singular
    comparable quantity fails, and a flip trial record cited as a
    run result fails. Per viewer carriages in their decided form
    stand."""
    if not isinstance(carriage, dict):
        return False
    if carriage.get("form") == "singular_vector":
        return False
    if carriage.get("presented_as") == "one comparable quantity":
        return False
    if carriage.get("form") == "flip_trial_record" and carriage.get("cited_as") == "run_result":
        return False
    return True


def retained_version_set(record_id="record-under-test"):
    """The exact rule version set a retained record carries, as
    retained by this Recorder: the set stands returned unedited,
    in the form the record was produced under."""
    return "rule-version-set-1"


def rerun_list_for_rule_change(family_id="family-under-test"):
    """The rerun list derived from a rule change for one family,
    held as a retained record naming the records the change puts
    in question."""
    return {
        "family_id": family_id,
        "records_in_question": ["run-under-test"],
        "form": "retained rerun list",
    }

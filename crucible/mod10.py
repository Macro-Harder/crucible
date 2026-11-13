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


def _carries_real_money_field(value):
    """Whether a value carries a real money field at any depth, by
    field name (a real money field name with a value standing) or
    by amount and currency shape."""
    if isinstance(value, dict):
        if (value.get("amount") is not None
                and value.get("currency") is not None):
            return True
        for key, item in value.items():
            if key in ("real_money_value", "real_money") and item is not None:
                return True
            if _carries_real_money_field(item):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_carries_real_money_field(item) for item in value)
    return False


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
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                stored_records = data["records"]
            except (json.JSONDecodeError, TypeError, KeyError) as exc:
                raise LookupFailure(path) from exc
            for record in stored_records:
                rid = record.get("run_id") or record.get("run_identifier")
                self._records[rid] = record
                self._index.append(rid)

    def _flush(self, merge_disk=True):
        if not self.path:
            return
        merged = {}
        if merge_disk and os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as handle:
                    disk = json.load(handle)
                if isinstance(disk, dict):
                    for record in disk.get("records", []):
                        rid = (record.get("run_id")
                               or record.get("run_identifier"))
                        if rid is not None:
                            merged[rid] = record
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        for rid, record in self._records.items():
            merged[rid] = record
        records = [merged[rid] for rid in sorted(merged, key=lambda item: str(item))]
        payload = {"store_kind": self.store_kind, "records": records}
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, self.path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def retain_run_record(self, record):
        if not isinstance(record, dict):
            raise ValueError(
                "identity less record: a run record stands as a record "
                "carrying a run identifier, and no other form stands retained")
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is None:
            raise ValueError(
                "identity less record: no run identifier stands on the "
                "record, and no record stands retained under no identifier")
        if _carries_real_money_field(record):
            raise ValueError(
                "real money field in named form: a run record carrying "
                "a real money value stands refused at retention, by "
                "field name and by amount and currency shape")
        if rid in self._records:
            raise ValueError("second record for the same run is rejected: " + str(rid))
        self._records[rid] = copy.deepcopy(record)
        self._index.append(rid)
        try:
            self._flush()
        except OSError as exc:
            del self._records[rid]
            self._index.remove(rid)
            raise ValueError(
                "recorder store flush failure: the retained record stands "
                "not written, and the prior store file stands whole: "
                + str(exc)) from exc
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
        self._flush(merge_disk=False)

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
_VIEW_RECORDS = {}
_CHECKPOINT_STATES = {}


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
        _RESERVE_HOLDS, _SUMMARY_RECORDS, _VIEW_RECORDS,
        _CHECKPOINT_STATES,
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
        if not isinstance(record, dict):
            return False
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is None or rid in seen:
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


def _delivery_complete(delivery):
    components = delivery.get("joint_outcome_components")
    denominators = delivery.get("component_denominators")
    return (
        isinstance(components, (list, tuple)) and len(components) == 4
        and isinstance(denominators, (list, tuple)) and len(denominators) == 4
        and "honest_share" in delivery
        and "epochs_ending_on_day" in delivery
        and "gate_passing_shares" in delivery
    )


def _day_sort_key(item):
    day, viewer = item
    if isinstance(day, int) and not isinstance(day, bool):
        return (0, day, str(viewer))
    if isinstance(day, str) and day.isdigit():
        return (0, int(day), str(viewer))
    return (1, 0, str(day) + ":" + str(viewer))


def _aggregates_from_deliveries(run_id):
    stored = _AGGREGATE_DELIVERIES.get(run_id)
    if not stored:
        return None
    records = []
    for key in sorted(stored, key=_day_sort_key):
        delivery = stored[key]
        day = delivery.get("simulated_day")
        viewer = delivery.get("viewer_id")
        base = {
            "run_id": run_id,
            "run_identifier": run_id,
            "simulated_day": day,
            "viewer_id": viewer,
            "viewer_identifier": viewer,
            "record_identity": (
                str(run_id) + ":" + str(day) + ":" + str(viewer)),
            "writer": "Recorder",
            "amendment_standing": (
                delivery.get("amendment_standing")
                or "as originally written"),
            "amending_act": delivery.get("amending_act"),
        }
        if not _delivery_complete(delivery):
            marked = dict(base)
            for field in (
                "joint_outcome_components", "component_denominators",
                "honest_share", "epochs_ending_on_day",
                "gate_passing_shares", "divergence_companion",
            ):
                if field in delivery:
                    marked[field] = copy.deepcopy(delivery[field])
            marked["form"] = FORM_ONLY
            records.append(marked)
            continue
        shares = dict(delivery.get("gate_passing_shares") or {})
        record = dict(base)
        record.update({
            "joint_outcome_components": list(
                delivery.get("joint_outcome_components")),
            "component_denominators": list(
                delivery.get("component_denominators")),
            "honest_share": delivery.get("honest_share"),
            "epochs_ending_on_day": list(
                delivery.get("epochs_ending_on_day") or []),
            "gate_passing_shares": shares,
            "gate_passing_share_per_epoch": copy.deepcopy(shares),
            "excluded_class_counts_and_shares": copy.deepcopy(
                delivery.get("excluded_class_counts_and_shares")
                or delivery.get("excluded_class_counts") or {}),
            "divergence_companion": copy.deepcopy(
                delivery.get("divergence_companion")
                or {"nil_divergence_components": []}),
        })
        records.append(record)
    return records


def aggregate_manifest_for_run(run_id):
    """Return the aggregate manifest of one run: for each aggregate
    record the aggregation act writes, its identity, its writer, and
    its amendment standing, in the ruling Entry 12 form. Where no
    aggregate stands written for the run, one form only entry stands
    returned."""
    computed = _aggregates_from_deliveries(run_id)
    if computed is None:
        return [{"run_id": run_id, "form": FORM_ONLY}]
    return [
        {
            "record_identity": record.get("record_identity"),
            "writer": record.get("writer"),
            "amendment_standing": record.get("amendment_standing"),
            "amending_act": record.get("amending_act"),
        }
        for record in computed
    ]


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
    records handed in: their day count and their component totals.
    The result names, for each aggregate record read, its identity,
    its writer, and its amendment standing, in the ruling Entry 12
    form. Where any record handed in carries the form only marker,
    no classification stands computed from it: the result carries
    the form only standing inside it and counts no placeholder day
    as a day of the run."""
    if not aggregates:
        return None
    states = [
        {
            "record_identity": record.get("record_identity"),
            "writer": record.get("writer"),
            "amendment_standing": (
                record.get("amendment_standing")
                or "not stated on the record"),
            "amending_act": record.get("amending_act"),
        }
        for record in aggregates
    ]
    if any(record.get("form") == FORM_ONLY for record in aggregates):
        return {
            "classification": None,
            "form": FORM_ONLY,
            "days": 0,
            "placeholder_records": len(aggregates),
            "carriage": (
                "form only, no classification stands computed "
                "from a placeholder aggregate"),
            "aggregate_states": states,
        }
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
        "aggregate_states": states,
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


def build_joint_outcome_vector(components=None, divergence_companion=None):
    """Build one JointOutcomeVector record, Form 15, from its
    components as handed in. Every component stands as its stored
    parts in the form the plan states for that component, with the
    viewer identifier carried on every component, and all four
    components of one vector carry the one viewer of the vector.
    A component handed in as a bare value, or missing any of its
    stored parts, stands refused in named form. No part stands
    computed here: the proportion and the rate stand as handed in,
    as stored parts, and no recomputation rule and no rounding
    rule stands supplied by this act."""
    components = components or {}
    record = {}
    viewers = set()
    for field, parts in mod01.JOINT_OUTCOME_COMPONENT_PARTS.items():
        component = components.get(field)
        if not isinstance(component, dict):
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " stands as no record of its stored parts")
        missing = [part for part in parts if component.get(part) is None]
        if missing:
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " carries no " + ", ".join(missing))
        viewers.add(component.get("viewer_identifier"))
        record[field] = copy.deepcopy(component)
    if len(viewers) != 1:
        raise ValueError(
            "joint outcome component in named form: the components "
            "of one vector carry more than one viewer identifier")
    record["divergence_companion"] = copy.deepcopy(
        divergence_companion or {"nil_divergence_components": []})
    if not mod01.validate_record("15", record):
        raise ValueError(
            "joint outcome component in named form: the assembled "
            "record fails Form 15 validation")
    return record


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
    if not isinstance(entry, dict):
        raise ValueError(
            "identity less entry: an event log entry stands as a record, "
            "and no other form stands retained")
    run_id = entry.get("run_identifier") or entry.get("run_id")
    bucket = _EVENT_LOGS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if existing == entry:
            return copy.deepcopy(existing)
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
    if not isinstance(snapshot, dict):
        raise ValueError(
            "identity less snapshot: a daily snapshot stands as a record, "
            "and no other form stands retained")
    run_id = snapshot.get("run_identifier") or snapshot.get("run_id")
    bucket = _DAILY_SNAPSHOTS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if existing == snapshot:
            return copy.deepcopy(existing)
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
    if not isinstance(manifest, dict):
        raise ValueError(
            "identity less checkpoint: a checkpoint manifest stands as a "
            "record carrying a run identifier, and no other form stands "
            "retained")
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "manifest, and no checkpoint stands retained under no identifier")
    bucket = _CHECKPOINTS.setdefault((store_kind, run_id), [])
    if len(bucket) >= 10000:
        raise ValueError("checkpoint cap in named form: a run stands at the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no further checkpoint stands retained")
    stored = copy.deepcopy(manifest)
    if "journal_event_count_at_checkpoint" not in stored:
        stored["journal_event_count_at_checkpoint"] = len(
            event_log_entries(run_id, store_kind))
    bucket.append(stored)
    if manifest.get("checkpoint_state") is not None:
        _CHECKPOINT_STATES[(store_kind, run_id,
                            manifest.get("simulated_day"))] = (
            copy.deepcopy(manifest["checkpoint_state"]))
    return copy.deepcopy(manifest)


def checkpoint_state_at(run_id, simulated_day, store_kind="sweep"):
    """Read the CheckpointState standing beside a retained
    checkpoint manifest, where one was written with it. Reading
    never writes: no state beside the manifest returns None."""
    return copy.deepcopy(
        _CHECKPOINT_STATES.get((store_kind, run_id, simulated_day)))


def checkpoints_for_run(run_id, store_kind="sweep"):
    """Enumerate the retained checkpoints of a run by its
    CheckpointManifest set. Reading never writes."""
    return copy.deepcopy(_CHECKPOINTS.get((store_kind, run_id), []))


def delete_checkpoint(run_id, checkpoint_day, store_kind="sweep",
                      trigger=None, rule_path=None,
                      integrity_flag_open=False,
                      named_in_retention_record=False,
                      regression_corpus_copy=False):
    """Delete one checkpoint and update every pointer naming it as
    one recorded act. Returns the act record. A deletion stands
    only under a stated clause C5 trigger and a stated deletion
    rule path, and no deletion stands against a clause C8
    protection: an open integrity flag, a checkpoint named in a
    retention record for a reported headline unit, or a regression
    corpus copy of the checkpoint."""
    if trigger is None:
        raise ValueError(
            "checkpoint deletion refused: no clause C5 trigger stands "
            "stated for the deletion, and no checkpoint stands deleted")
    if rule_path is None:
        raise ValueError(
            "checkpoint deletion refused: no deletion rule path stands "
            "stated or checked for the deletion")
    if integrity_flag_open or named_in_retention_record or regression_corpus_copy:
        raise ValueError(
            "checkpoint deletion refused: a clause C8 protection stands "
            "on the checkpoint, and no checkpoint stands deleted")
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
        "trigger": trigger,
        "rule_path": rule_path,
        "actor": "Recorder",
    }


def checkpoint_position_check(manifest, store_kind="sweep"):
    """The C-11 position check, free limb under ruling Entry 9: the
    journal position in a checkpoint manifest stands checked against
    the retained log of its run at the time the checkpoint is used.
    A position inside the retained log passes the check. A position
    outside it stands reported as a retention failure under C-09."""
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    position = manifest.get("journal_position")
    entries = event_log_entries(run_id, store_kind)
    inside = (
        isinstance(position, int) and not isinstance(position, bool)
        and 1 <= position <= len(entries))
    if inside:
        return {
            "check": "checkpoint position check",
            "outcome": "inside the retained log",
            "journal_position": position,
            "retained_log_length": len(entries),
            "reportable": True,
        }
    return {
        "check": "checkpoint position check",
        "outcome": "retention failure: the journal position stands "
                   "outside the retained log",
        "failure_under": "C-09",
        "journal_position": position,
        "retained_log_length": len(entries),
        "reportable": False,
    }


def close_run_retention(run_id, tier, store_kind="sweep"):
    """Apply the clause C3 retained set at run close: Tier 0 keeps
    no checkpoint, Tier 1 keeps the final checkpoint only, Tier 2
    keeps the final checkpoint and the tenth point checkpoints,
    and Tier 3 keeps the final checkpoint and every daily
    checkpoint. Checkpoints outside the set stand released at
    close, and the release stands on the returned record."""
    if tier not in ("Tier 0", "Tier 1", "Tier 2", "Tier 3"):
        raise ValueError(
            "unknown retention tier for the close act: " + str(tier))
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    days = sorted({
        item.get("simulated_day") for item in bucket
        if isinstance(item.get("simulated_day"), int)
        and not isinstance(item.get("simulated_day"), bool)
    })
    if not days or tier == "Tier 3":
        kept_days = list(days)
    elif tier == "Tier 0":
        kept_days = []
    elif tier == "Tier 1":
        kept_days = [days[-1]]
    else:
        tenth = [
            day for position, day in enumerate(days, start=1)
            if position % 10 == 0
        ]
        kept_days = sorted(set(tenth) | {days[-1]})
    released_days = [day for day in days if day not in kept_days]
    if released_days:
        _CHECKPOINTS[(store_kind, run_id)] = [
            item for item in bucket
            if item.get("simulated_day") in kept_days
        ]
    return {
        "run_id": run_id,
        "retention_tier": tier,
        "kept_days": kept_days,
        "released_days": released_days,
        "trigger": "clause C3 retained set at run close",
        "actor": "Recorder",
        "release_recorded": True,
    }


def checkpoint_integrity_check(manifest, candidate):
    """The INV8B-03 checkpoint integrity battery carriage, at slice
    S-10, in its three cases: alteration, transplant, and staleness.
    While OP-24 stands open, the outcome in every case stands at
    the required value not computable: no computable integrity
    verdict stands returned, no byte level hash equality stands
    computed, and no state hash equality stands claimed."""
    return {
        "battery": "INV8B-03 checkpoint integrity battery",
        "alteration": "not computable",
        "transplant": "not computable",
        "staleness": "not computable",
        "outcome": "not computable",
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
    absent record raises the named lookup failure, with the
    identifier carried under its own kind name and the record kind
    sought stated in the failure."""
    if (kind, owner_id) not in _GC08_RECORDS:
        failure = LookupFailure(owner_id)
        failure.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "owner_identifier": owner_id,
            "record_kind": kind,
        }
        raise failure
    return copy.deepcopy(_GC08_RECORDS[(kind, owner_id)])


def _stated_count(value, name):
    """Read one count in its stated integer form only. A string, a
    fraction, a boolean, or a negative count stands refused in
    named form, and no value stands converted silently."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands in a non integer form, and no count "
            "stands converted silently")
    if value < 0:
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands negative, and no negative stock "
            "stands accounted")
    return value


def storage_accounting(retained):
    if not isinstance(retained, dict):
        raise ValueError(
            "storage accounting count in named form: the retained set "
            "stands as a record of counts, and no other form stands "
            "accounted")
    summaries = _stated_count(retained.get("summaries", 0), "summaries")
    snapshots = _stated_count(
        retained.get("daily_snapshots", 0), "daily_snapshots")
    logs = _stated_count(retained.get("event_logs", 0), "event_logs")
    checkpoints = _stated_count(
        retained.get("checkpoints", 0), "checkpoints")
    copies = _stated_count(
        retained.get("held_corpus_copies", 0), "held_corpus_copies")
    return {
        "result_count": summaries + snapshots + logs,
        "checkpoint_count": checkpoints + copies,
        "summaries": summaries,
        "daily_snapshots": snapshots,
        "event_logs": logs,
        "checkpoints": checkpoints,
        "held_corpus_copies": copies,
        "checkpoint_stock_basis": (
            "checkpoint_count_c10 form: retained checkpoints plus "
            "held corpus copies, the count a sizing statement rests on"),
    }


def validate_storage_accounting(claimed):
    if not isinstance(claimed, dict):
        raise ValueError(
            "storage accounting count in named form: the claimed set "
            "stands as a record of counts, and no other form stands "
            "validated")
    expected = (
        _stated_count(claimed.get("summaries", 0), "summaries")
        + _stated_count(claimed.get("daily_snapshots", 0), "daily_snapshots")
        + _stated_count(claimed.get("event_logs", 0), "event_logs")
    )
    if claimed.get("result_count") != expected:
        return False
    if "checkpoint_count" in claimed:
        expected_stock = (
            _stated_count(claimed.get("checkpoints", 0), "checkpoints")
            + _stated_count(
                claimed.get("held_corpus_copies", 0), "held_corpus_copies"))
        if claimed.get("checkpoint_count") != expected_stock:
            return False
    return True


def checkpoint_count_c10(rows):
    """The retained checkpoint stock count under clause C10: for
    each row, the retained checkpoints per run multiplied by the
    runs in the row, plus one for each held regression corpus copy
    of a checkpoint in the row, summed over rows. No checkpoint
    byte total stands stated by this count."""
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(
                "checkpoint count in named form: a C10 row stands as a "
                "record, and no other form stands counted")
        if "retained_per_run" not in row or "runs" not in row:
            raise ValueError(
                "checkpoint count in named form: a C10 row stands "
                "without its retained per run count or its run count, "
                "and no count stands returned for it")
        per_run = _stated_count(row["retained_per_run"], "retained_per_run")
        if per_run > 10000:
            raise ValueError("checkpoint cap in named form: a C10 row stands over the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no bare count stands returned for it")
        runs = _stated_count(row["runs"], "runs")
        present = [
            (key, row[key])
            for key in (
                "held_corpus_copies",
                "regression_corpus_copies",
                "corpus_copies",
                "copies",
            )
            if row.get(key) is not None
        ]
        copy_values = {
            _stated_count(value, key) for key, value in present
        }
        if len(copy_values) > 1:
            raise ValueError(
                "checkpoint count in named form: a C10 row carries two "
                "differing copy counts under the alias keys "
                + ", ".join(key for key, _value in present)
                + ", and no count stands returned for it")
        copies = copy_values.pop() if copy_values else 0
        total += per_run * runs + copies
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
    at this writing from that RunRecord, with its retention tier
    taken from the run class the RunRecord states, under the tier
    assignment by run class, and with no tier asserted where no
    run class and no stated tier stands. Where neither stands
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
            "form": FORM_ONLY,
            "record_found": False,
            "statement": (
                "no summary record and no run record was found for "
                "run " + str(run_id)),
        }
    groups = record.get("groups") or {}
    outcome = groups.get("outcome_and_retention") or {}
    identity = groups.get("identity_and_design") or {}
    run_class = (
        record.get("run_class")
        or identity.get("run_class")
        or outcome.get("run_class"))
    tier = (
        _RUN_CLASS_TIERS.get(run_class)
        or record.get("retention_tier")
        or outcome.get("retention_tier"))
    computed = {
        "run_id": record.get("run_id") or record.get("run_identifier") or run_id,
        "written_at": "run_close",
        "content_computed_at": "run_close",
        "source": "RunRecord",
        "flag_conditions_fired": copy.deepcopy(
            record.get("flag_conditions_fired")
            or outcome.get("flag_conditions_fired") or []),
        "carriage": "computed from the retained RunRecord",
    }
    if tier is not None:
        computed["retention_tier"] = tier
    for field in ("week", "headline_unit_identifiers"):
        if field in record:
            computed[field] = copy.deepcopy(record[field])
    return computed


_TIER_RANKS = {"Tier 0": 0, "Tier 1": 1, "Tier 2": 2, "Tier 3": 3}
_RUN_CLASS_TIERS = {
    "screening": "Tier 1", "confirmation": "Tier 2",
    "headline": "Tier 3", "validation": "Tier 3",
}
_FLAG_OUTCOMES = ("promote", "demote")


def apply_flag_evaluation(record, outcome=None, tier=None, actor="program", inputs=None):
    if not isinstance(record, dict):
        raise ValueError(
            "flag evaluation in named form: the evaluation stands on a "
            "summary record, and no other form stands evaluated")
    if actor == "person":
        raise ValueError("promotion by a person after close is barred")
    if outcome is not None and outcome not in _FLAG_OUTCOMES:
        raise ValueError(
            "flag evaluation outcome outside the stated vocabulary: "
            + str(outcome))
    if outcome == "demote":
        raise ValueError("the flag rule never demotes")
    if tier is not None and tier not in _TIER_RANKS:
        raise ValueError(
            "flag evaluation tier outside the tiers the rule names: "
            + str(tier))
    current = record.get("retention_tier")
    if (tier is not None and current in _TIER_RANKS
            and _TIER_RANKS[tier] < _TIER_RANKS[current]):
        raise ValueError(
            "the flag rule never demotes: the stated tier stands below "
            "the record tier")
    if outcome == "promote":
        if tier is None:
            raise ValueError(
                "a promote outcome with no tier stands refused: no "
                "promotion stands effected by it")
        if current in _TIER_RANKS and _TIER_RANKS[tier] <= _TIER_RANKS[current]:
            raise ValueError(
                "a promote outcome with no effected promotion stands "
                "refused")
    updated = copy.deepcopy(record)
    if outcome == "promote" and tier is not None:
        updated["retention_tier"] = tier
    updated["flag_evaluation"] = {
        "inputs": inputs,
        "outcome": outcome,
        "tier": tier,
        "actor": actor,
        "written_into": "summary record",
    }
    run_key = updated.get("run_id") or updated.get("run_identifier")
    if run_key is not None:
        write_summary_record(updated)
    return updated


def place_reserve_hold(run_id, family_states_headlines=True, start_day=0):
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
        "start_day": start_day,
        "maximum_duration_days": 30,
        "end_day": start_day + 30,
        "stated_end": True,
        "cut_short_by_cost_warden": False,
    }
    _RESERVE_HOLDS[run_id] = hold
    return copy.deepcopy(hold)


def reserve_hold_for_run(run_id, current_day=None):
    """Read the reserve hold standing on a run. A hold read at or
    past its ruled maximum end of 30 days under ruling Entries 17
    and 18 stands expired by that stated act, for every family
    form including a family that never states headline results,
    and never reads held without an end."""
    hold = _RESERVE_HOLDS.get(run_id)
    if hold is None:
        return None
    if current_day is not None and hold.get("state") == "held" and current_day >= hold.get("end_day", 0):
        hold["state"] = "expired"
    if hold.get("state") == "released":
        return None
    return copy.deepcopy(hold)


def apply_deferred_evaluation(summary_record, firing, inputs=None,
                              outcome=None, family_states_headlines=True):
    """Write one deferred evaluation into the summary record
    itself: its firing, its inputs, and its outcome. Each run
    receives two firings. For a family that never states headline
    results, the second firing does not fire. Where the release
    trigger terminates at the later firing, the reserve hold on
    the run stands released by the same act."""
    if not isinstance(summary_record, dict):
        raise ValueError("no evaluation stands written in named form: no summary record stands for the run, and no detached evaluation stands returned")
    if firing not in (1, 2):
        raise ValueError("a run receives two firings and no third")
    updated = copy.deepcopy(summary_record)
    evaluations = updated.setdefault("deferred_evaluations", [])
    if any(item.get("firing") == firing for item in evaluations):
        raise ValueError("this firing already stands written")
    if firing == 2 and not family_states_headlines:
        updated["second_firing"] = "does not fire"
        return updated
    if inputs is None or outcome is None:
        raise ValueError(
            "deferred evaluation refused in named form: a firing with "
            "no inputs or no outcome stands not written, and no hold "
            "stands released by it")
    if firing == 2:
        run_key = updated.get("run_id") or updated.get("run_identifier")
        stored = _SUMMARY_RECORDS.get(run_key) or {}
        stored_evaluations = stored.get("deferred_evaluations") or []
        first_standing = (
            any(item.get("firing") == 1 for item in evaluations)
            or any(item.get("firing") == 1 for item in stored_evaluations))
        if not first_standing:
            raise ValueError(
                "deferred evaluation refused in named form: the second "
                "firing stands with no first firing on the record, and "
                "no hold stands released by it")
        if not evaluations and stored_evaluations:
            evaluations.extend(copy.deepcopy(stored_evaluations))
    evaluations.append({
        "firing": firing,
        "inputs": inputs,
        "outcome": outcome,
        "conditions": [1, 2] if firing == 1 else [1, 2, 3],
        "written_into": "summary record",
    })
    if firing == 2:
        hold = _RESERVE_HOLDS.get(updated.get("run_id"))
        if hold is not None and hold.get("family_states_headlines", True):
            hold["state"] = "released"
            updated["reserve_hold_state"] = "released"
    run_key = updated.get("run_id") or updated.get("run_identifier")
    if run_key is not None:
        write_summary_record(updated)
    return updated


def retention_record_for_run(run_id, store_kind="sweep"):
    """Return the retention record of a run in pointer form: the
    later evaluation as written into the summary record, and the
    forms retained for the run that this record points to."""
    summary = summary_record_for_run(run_id)
    evaluations = summary.get("deferred_evaluations") or []
    later = evaluations[-1] if evaluations else None
    tier = summary.get("retention_tier")
    tier_forms = {
        "Tier 1": ["final_checkpoint"],
        "Tier 2": ["final_checkpoint", "tenth_point_checkpoints"],
        "Tier 3": ["final_checkpoint", "daily_checkpoints"],
    }.get(tier, [])
    pointer_counts = {
        "checkpoints": len(checkpoints_for_run(run_id, store_kind)),
        "event_log_entries": len(event_log_entries(run_id, store_kind)),
        "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
    }
    retained_forms = []
    if pointer_counts["checkpoints"]:
        retained_forms.append("final_checkpoint")
    if pointer_counts["event_log_entries"]:
        retained_forms.append("event_log")
    if pointer_counts["daily_snapshots"]:
        retained_forms.append("daily_snapshots")
    not_retained = [
        form + ": not retained"
        for form in tier_forms if form not in retained_forms
    ]
    result = {
        "run_id": run_id,
        "retention_tier": tier,
        "tier_forms": list(tier_forms),
        "retained_forms": retained_forms,
        "not_retained": not_retained,
        "shortfall": {
            "count": len(not_retained),
            "bound": "shortfall stands stated inside this result as a bound: "
            + str(len(not_retained)) + " of " + str(len(tier_forms))
            + " forms the tier names stand not retained",
        },
        "later_evaluation": copy.deepcopy(later),
        "pointers": {
            "checkpoints": len(checkpoints_for_run(run_id, store_kind)),
            "event_log_entries": len(event_log_entries(run_id, store_kind)),
            "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
        },
        "pointer_form": "retention record points to the retained forms",
    }
    result["summary_record_written"] = run_id in _SUMMARY_RECORDS
    result["retained_forms_pointed_to"] = [
        name for name, count in pointer_counts.items() if count
    ]
    result["form_standing"] = {
        name: (
            "held in memory only: a count of zero states that no form "
            "stands in memory for the run, and does not state that no "
            "form ever stood")
        for name in pointer_counts
    }
    if (run_id not in _SUMMARY_RECORDS
            and not any(pointer_counts.values())
            and not _DEFAULT_STORE.has_run_record(run_id)):
        result["form"] = FORM_ONLY
    return result


def validate_retention_report(report):
    if report.get("source") == "interval_records" and report.get("tier_claim") == "final":
        return False
    return True


def append_annotation(checkpoint, annotation=None):
    updated = copy.deepcopy(checkpoint)
    updated["annotation_record"] = copy.deepcopy(annotation) if annotation is not None else {}
    return updated


def annotation_link_at_checkpoint(checkpoint):
    """Return the annotation link identifier at a checkpoint, under
    the plan named field annotation_link_identifier where it
    stands, and under the Form 4 carriage name annotation_link
    where that is the name the checkpoint carries."""
    return (
        checkpoint.get("annotation_link_identifier")
        or checkpoint.get("annotation_link"))


def resume_from_checkpoint(checkpoint):
    """Resume from a checkpoint. Where a retained checkpoint stands
    for the run and day the handed checkpoint names, the handed
    checkpoint stands checked against it: a checkpoint differing
    from the retained one stands refused in named form, and no
    resume stands performed from it."""
    if not isinstance(checkpoint, dict):
        raise ValueError(
            "identity less checkpoint: a resume stands on a checkpoint "
            "record, and no other form stands resumed")
    run_id = checkpoint.get("run_identifier") or checkpoint.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "checkpoint, and no resume stands performed")
    for (kind, bucket_run), bucket in _CHECKPOINTS.items():
        if bucket_run != run_id:
            continue
        for retained in bucket:
            if retained.get("simulated_day") == checkpoint.get("simulated_day"):
                retained_form = {
                    key: value for key, value in retained.items()
                    if key != "journal_event_count_at_checkpoint"
                }
                if retained_form != checkpoint:
                    raise ValueError(
                        "checkpoint integrity refusal: the handed "
                        "checkpoint differs from the retained checkpoint "
                        "for its run and day, and no resume stands "
                        "performed from it")
                return copy.deepcopy(checkpoint)
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
                "events_per_agent_per_day": 25.71,
                "provenance": "derived over estimated form values, high form as working form",
            },
        },
    }


def validate_retention_sizing(sizing):
    workings = sizing.get("workings") or {}
    if "central_form" not in workings or "high_form" not in workings:
        return False
    high = workings.get("high_form") or {}
    if high.get("events_per_agent_per_day") is None:
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
    if isinstance(kinds, str):
        kinds = (kinds,)
    if kinds is None and store_kind is not None:
        kinds = (store_kind,)
    if kinds is None:
        kinds = ()
    if len(tuple(kinds)) != 1:
        raise ValueError("a lookup that resolves across stores in one step is rejected")
    kind = tuple(kinds)[0]
    if kind not in STORE_KINDS:
        raise ValueError(
            "unknown store kind: " + str(kind) + "; a store kind stands "
            "among sweep, pilot, and live, and no record lookup stands "
            "performed on an unknown kind")
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
    "build_joint_outcome_vector",
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


def _retained_records():
    for store in _STORES.values():
        for record in store._records.values():
            yield record
    for record in _SUMMARY_RECORDS.values():
        yield record


def retained_version_set(record_id="record-under-test"):
    """The exact rule version set a retained record carries, as
    retained by this Recorder: the set stands returned unedited,
    in the form the record was produced under. Where no record
    stands retained under the identifier, the returned value
    carries the form only marker inside it, and no version set
    stands stated for a record that does not exist."""
    for record in _retained_records():
        rid = record.get("run_id") or record.get("run_identifier")
        if rid != record_id:
            continue
        for field in ("rule_version_set", "record_version_set",
                      "version_set"):
            if record.get(field) is not None:
                return copy.deepcopy(record[field])
    return {"record_id": record_id, "form": FORM_ONLY}


def rerun_list_for_rule_change(family_id="family-under-test"):
    """The rerun list derived from a rule change for one family,
    held as a retained record naming the records the change puts
    in question. The list stands derived from the records retained
    for the family. Where no record stands retained for the
    family, the returned value carries the form only marker inside
    it and names no record in question."""
    in_question = []
    for record in _retained_records():
        family = (record.get("family_id")
                  or record.get("family_identifier"))
        if family != family_id:
            continue
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is not None and rid not in in_question:
            in_question.append(rid)
    if not in_question:
        return {
            "family_id": family_id,
            "records_in_question": [],
            "form": FORM_ONLY,
        }
    return {
        "family_id": family_id,
        "records_in_question": in_question,
        "form": "retained rerun list",
    }


# ---------------------------------------------------------------------------
# View record leak check and retention (slice S-11, Recorder limb)
# ---------------------------------------------------------------------------

_VIEW_LEAK_FORMS = ("canary", "field_validation", "timing")
_VIEW_CANARY_KEYS = frozenset((
    "ground_truth", "is_honest", "membership", "label", "sleeper",
    "is_farm",
))


def _carries_canary_key(value):
    if isinstance(value, dict):
        return any(
            key in _VIEW_CANARY_KEYS or _carries_canary_key(item)
            for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_carries_canary_key(item) for item in value)
    return False


def run_view_leak_check(view_record):
    """Run the three form leak check on a ViewRecord: the canary
    form, the field validation form, and the timing form, together
    on the one record. A failure in any one form raises a failure
    naming the view, the field, and the check form that failed,
    and the run stands not reportable on that record. A record
    passing all three forms returns the run record of the check."""
    if not isinstance(view_record, dict):
        raise ValueError(
            "view leak check failure: form field_validation, the "
            "record stands as no ViewRecord")
    view_name = (
        str(view_record.get("run_identifier")
            or view_record.get("run_id"))
        + "/" + str(view_record.get("viewer_identifier")
                    or view_record.get("viewer_id")))
    for field in ("view_contents", "reputation_and_band_values"):
        if _carries_canary_key(view_record.get(field)):
            raise ValueError(
                "view leak check failure: form canary, view "
                + view_name + ", field " + field
                + " carries a barred key")
    for field in mod01.ViewRecord.FIELDS:
        if view_record.get(field) is None:
            raise ValueError(
                "view leak check failure: form field_validation, view "
                + view_name + ", field " + field + " stands absent")
    day = view_record.get("simulated_day")
    first_seen = view_record.get("first_seen_day_per_record") or {}
    for item, seen_day in first_seen.items():
        if (isinstance(seen_day, int) and isinstance(day, int)
                and seen_day > day):
            raise ValueError(
                "view leak check failure: form timing, view "
                + view_name + ", field first_seen_day_per_record: "
                "record " + str(item) + " first seen after the view day")
    return {
        "forms_run": list(_VIEW_LEAK_FORMS),
        "reportable": True,
        "view": view_name,
    }


def retain_view_record(record, tier=None):
    """Retain one ViewRecord under the leak check runner: the
    record stands retained only where the runner passes it. The
    retention split stands by tier: at Tier 1 the divergence
    companion stands retained in place of the full record, and at
    Tier 2 and Tier 3 the full record stands retained."""
    if not isinstance(record, dict):
        raise ValueError(
            "identity less view record: a ViewRecord stands as a "
            "record carrying a run identifier, and no other form "
            "stands retained")
    run_id = record.get("run_identifier") or record.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less view record: no run identifier stands on "
            "the record, and no view record stands retained under "
            "no identifier")
    run_view_leak_check(record)
    tier = tier or record.get("retention_tier") or "Tier 2"
    if tier == "Tier 1":
        stored = {
            "run_identifier": run_id,
            "viewer_identifier": (
                record.get("viewer_identifier")
                or record.get("viewer_id")),
            "simulated_day": record.get("simulated_day"),
            "retention_tier": "Tier 1",
            "divergence_companion": copy.deepcopy(
                record.get("divergence_companion")
                or {"nil_divergence_components": []}),
            "form": "divergence companion in place of the full view record",
        }
    else:
        stored = copy.deepcopy(record)
        stored["retention_tier"] = tier
    _VIEW_RECORDS.setdefault(run_id, []).append(stored)
    return copy.deepcopy(stored)


def view_records_for_run(run_id):
    """Read the retained ViewRecords of a run. Reading never
    writes."""
    return copy.deepcopy(_VIEW_RECORDS.get(run_id, []))

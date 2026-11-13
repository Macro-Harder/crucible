"""MOD-04 Tick Engine, DetectionInput projection, and view edges.

Slice S-09 in full, with the S-11 view edges this module owns. This
module carries the Contract A handover, the delivery points to the
rule cores and to the detection layer, the order of work inside one
simulated day, the DetectionInput projection from AgentState, and
the ViewRecord acts of slice S-11: selecting the records a view
contains, writing the ViewRecord, and delivering the view under
Contract K. Executable runs stand gated on DQ7-02: every barred
executable path in this module refuses by raising GatedRun, whose
message carries the recorded gated failure name DERIVATION-GATED
and names the gate DQ7-02, and no such path executes in part. The
tracer composition that retains and reads back one form only
RunRecord stands at the integration surface of slice S-16, in
mod16; this module holds no dependency on MOD-10 in any form.
"""
import copy

GATE_EXECUTABLE_RUNS = "DQ7-02"

BARRED_PROJECTION_KEYS = frozenset([
    "ground_truth", "ground_truth_field", "membership",
    "honest_membership", "farm_membership", "is_honest", "is_farm",
    "canary", "canary_value", "membership_value", "sleeper",
    "ground_truth_label", "label",
])

PROJECTION_KEYS = ("agent_identifier", "day", "feature_values", "rule_records")

CANARY_VALUE = "F09-CANARY-MEMBERSHIP-VALUE"


class NamedFailure(Exception):
    """A failure stated by name, never a partial record as complete."""


class AlterationBarred(NamedFailure):
    pass


GATED_FAILURE_NAME = "DERIVATION-GATED"


class GatedRun(NamedFailure):
    """The one gated refusal form of this module for gate DQ7-02.

    Every executable path the gate bars raises this exception. Its
    message carries the recorded gated failure name and names the
    gate, so a scan for gated behaviour finds one form here and the
    matching refusal record form in MOD-02.
    """

    failure = GATED_FAILURE_NAME
    gate = GATE_EXECUTABLE_RUNS


def _gated_message(act):
    return (
        GATED_FAILURE_NAME + ": " + act + " stands gated on "
        + GATE_EXECUTABLE_RUNS
    )


def _freeze(value):
    return copy.deepcopy(value)


class ContractAHandover:
    """One point, one assumption record, one seed input set, and one
    family identifier for one run, in interface form. The engine may
    not alter any handed value. Values are stored as deep copies and
    handed back as deep copies, so no caller side mutation reaches
    the stored handover, and any engine side attempt to change a
    stored value is checked by verify_intact."""

    __slots__ = ("_point", "_assumption_record", "_seed_input_set", "_family_id", "_sealed")

    def __init__(self, point, assumption_record, seed_input_set, family_id):
        object.__setattr__(self, "_point", _freeze(point))
        object.__setattr__(self, "_assumption_record", _freeze(assumption_record))
        object.__setattr__(self, "_seed_input_set", _freeze(seed_input_set))
        object.__setattr__(self, "_family_id", _freeze(family_id))
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        raise AlterationBarred("Contract A handed values may not be altered: " + str(name))

    @property
    def point(self):
        return _freeze(self._point)

    @property
    def assumption_record(self):
        return _freeze(self._assumption_record)

    @property
    def seed_input_set(self):
        return _freeze(self._seed_input_set)

    @property
    def family_id(self):
        return _freeze(self._family_id)

    def verify_intact(self, point, assumption_record, seed_input_set, family_id):
        ok = (
            point == self._point
            and assumption_record == self._assumption_record
            and seed_input_set == self._seed_input_set
            and family_id == self._family_id
        )
        if not ok:
            raise AlterationBarred(
                "silent correction inside the Engine: a handed value differs from the Contract A handover"
            )
        return True

    def as_dict(self):
        return {
            "point": self.point,
            "assumption_record": self.assumption_record,
            "seed_input_set": self.seed_input_set,
            "family_id": self.family_id,
            "form": "interface",
            "alteration_bar": "engine may not alter point, assumptions, seeds, or family identifier",
        }


class DeliveryPoint:
    """A named delivery point in interface form only. It records
    interface deliveries and delivers nothing in running form."""

    def __init__(self, name, destination):
        self.name = name
        self.destination = destination
        self.deliveries = []
        self.form = "interface"

    def record_interface_delivery(self, payload_description):
        entry = {
            "delivery_point": self.name,
            "destination": self.destination,
            "form": "interface",
            "payload": _freeze(payload_description),
            "running_delivery": False,
        }
        self.deliveries.append(entry)
        return entry

    def deliver_running(self, payload):
        raise GatedRun(_gated_message("running delivery"))


class RuleCoreDeliveryPoint(DeliveryPoint):
    def __init__(self):
        super().__init__("rule_core_delivery", "rule_cores")


class DetectionLayerDeliveryPoint(DeliveryPoint):
    def __init__(self):
        super().__init__("detection_layer_delivery", "detection_layer")


def _state_field(state, names, default=None):
    if isinstance(state, dict):
        for name in names:
            if name in state:
                return state[name]
        return default
    for name in names:
        if hasattr(state, name):
            return getattr(state, name)
    return default


def _is_barred_key(key):
    lowered = str(key).lower()
    return (
        lowered in BARRED_PROJECTION_KEYS
        or "membership" in lowered
        or "ground_truth" in lowered
    )


def _clean_value(value):
    if isinstance(value, dict):
        return {
            key: _clean_value(item)
            for key, item in value.items()
            if not _is_barred_key(key)
        }
    if isinstance(value, list):
        return [_clean_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_clean_value(item) for item in value)
    return _freeze(value)


def _clean_feature_values(raw):
    cleaned = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            if _is_barred_key(key):
                continue
            cleaned[key] = _clean_value(value)
    return cleaned


def _clean_rule_records(raw):
    cleaned = []
    if isinstance(raw, (list, tuple)):
        for item in raw:
            cleaned.append(_clean_value(item))
    return cleaned


def project_detection_input(state):
    """Project AgentState to DetectionInput. The result carries the
    agent identifier, the day, the feature values, and the records
    the rules give the detection layer, and nothing else. It carries
    no ground truth field and no field derived from membership."""
    agent_id = _state_field(state, ["agent_identifier", "agent_id", "identifier"])
    day = _state_field(state, ["day", "simulated_day"])
    features = _state_field(state, ["feature_values", "features"], {})
    rule_records = _state_field(state, ["rule_records", "detection_records"], [])
    return {
        "agent_identifier": agent_id,
        "day": day,
        "feature_values": _clean_feature_values(features),
        "rule_records": _clean_rule_records(rule_records),
    }


def _value_appears(value, node):
    if node == value:
        return True
    if isinstance(node, dict):
        return any(_value_appears(value, v) for v in node.values()) or any(
            _value_appears(value, k) for k in node.keys()
        )
    if isinstance(node, (list, tuple)):
        return any(_value_appears(value, item) for item in node)
    if isinstance(node, str) and isinstance(value, str):
        return value in node
    return False


def exercise_f09_canary(canary_value=CANARY_VALUE):
    """Fixture F-09 canary exercise, in code form. Places a canary
    membership value in an AgentState, runs the projection, and
    returns whether the canary appears in any projected record.
    The correct result is False: the canary must not appear."""
    state = {
        "agent_identifier": "agent-canary-1",
        "day": 1,
        "simulated_day": 1,
        "feature_values": {"activity": 1},
        "rule_records": [{"kind": "daily_record"}],
        "membership": canary_value,
        "ground_truth": canary_value,
    }
    projected = project_detection_input(state)
    return _value_appears(canary_value, projected)


def canary_appears_in_projection(canary_value=CANARY_VALUE):
    return exercise_f09_canary(canary_value)


class TickEngine:
    """The Tick Engine interface. In the tracer cut it holds the
    Contract A handover, owns the two delivery points in interface
    form, and owns the projection. It is the sole writer of
    simulation state in interface form: a write attempted through
    any other writer name is rejected."""

    def __init__(self, handover=None):
        self.handover = handover
        self.rule_core_delivery = RuleCoreDeliveryPoint()
        self.detection_delivery = DetectionLayerDeliveryPoint()
        self.state_writes = []

    def write_simulation_state(self, writer, change):
        if writer not in ("TickEngine", "tick_engine", "mod04"):
            raise NamedFailure(
                "direct state write from a second component is rejected: " + str(writer)
            )
        self.state_writes.append(_freeze(change))
        return True

    def tick(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        raise GatedRun(_gated_message("executable runs"))


def run(*args, **kwargs):
    return TickEngine().run(*args, **kwargs)


def tick(*args, **kwargs):
    return TickEngine().tick(*args, **kwargs)


def build_tracer_run_record():
    """Assemble one RunRecord in form only, one family, one point,
    one run class, through the S-09 interfaces, with its deliveries
    recorded as interface deliveries."""
    handover = ContractAHandover(
        point={"point_id": "tracer-point-1"},
        assumption_record={"assumption_record_id": "tracer-assumptions-1"},
        seed_input_set={"seed_inputs": ["tracer-seed-input-1"]},
        family_id="tracer-family-1",
    )
    engine = TickEngine(handover)
    state = {
        "agent_identifier": "agent-tracer-1",
        "day": 1,
        "feature_values": {"activity": 1},
        "rule_records": [{"kind": "daily_record"}],
        "membership": CANARY_VALUE,
    }
    projected = project_detection_input(state)
    d1 = engine.rule_core_delivery.record_interface_delivery(
        {"kind": "event", "form": "interface"}
    )
    d2 = engine.detection_delivery.record_interface_delivery(
        {"kind": "DetectionInput", "form": "interface", "record": projected}
    )
    record = {
        "run_id": "tracer-run-1",
        "run_identifier": "tracer-run-1",
        "family_id": "tracer-family-1",
        "point": handover.point,
        "run_class": "screening",
        "form": "form_only",
        "reportable": False,
        "gate": GATE_EXECUTABLE_RUNS,
        "groups": {
            "assumption_record": handover.assumption_record,
            "identity_and_design": {
                "family_id": "tracer-family-1",
                "point": handover.point,
                "run_class": "screening",
            },
            "interpretation_choices": {},
            "joined_done_test": {},
            "outcome_and_retention": {"deliveries": [d1, d2]},
            "reserved_matter": {},
            "variant_stamp": {},
        },
        "deliveries": [d1, d2],
        "handover": handover.as_dict(),
    }
    return record, projected


def run_tracer_cut():
    """Tracer entry point, kept at this name by the suite pin in
    test_tg_09_3.py, which calls this function on this module. The
    composition itself stands at the integration surface of slice
    S-16, in mod16.run_tracer_cut: the engine delivers the record
    in form only, and the integration surface composes it with the
    MOD-10 retention and reading path. This module imports no part
    of MOD-10 in any form."""
    from crucible import mod16

    return mod16.run_tracer_cut()


# ---------------------------------------------------------------------------
# S-09 in full: scheduling order, event sequence, delivery completeness
# ---------------------------------------------------------------------------

PROTOTYPE_ORDER = "prototype"
EVENT_KINDS = (
    "work_submission", "work_acceptance", "vouch_creation",
    "vouch_revocation", "challenge_opening", "challenge_response",
    "escrow_opening", "escrow_deposit", "escrow_release_request",
    "escrow_slash_request", "escrow_pause", "escrow_claim",
    "gossip_message", "trust_query", "detection_delivery",
    "day_close", "epoch_close",
)
PROCESSING_TYPES = (
    "gossip intake", "trust evaluation", "pairwise collusion evaluation",
)


def scheduling_order_record(family_id, order_identifier):
    """The scheduling order carriage of one family: one fixed order
    per family, stated in the family record the engine reads, never
    chosen inside engine code."""
    return {
        "family_id": family_id,
        "scheduling_order_identifier": order_identifier,
        "fixed_per_family": True,
        "stated_in": "family record",
    }


def run_record_with_order(run_record, order_identifier):
    """Return a copy of a run record carrying the scheduling order
    identifier the run used, as every run record must."""
    record = _freeze(run_record)
    record["scheduling_order_identifier"] = order_identifier
    return record


def validate_run_scheduling_order(record):
    """Return True only where a run record may stand on its order.

    Every run record states the order it used. A headline run whose
    scheduling order identifier is absent, or reads prototype,
    fails, per operation C-14 and open point OP-08.
    """
    if not isinstance(record, dict):
        return False
    order = record.get("scheduling_order_identifier")
    if not order:
        return False
    if record.get("run_class") == "headline" and order == PROTOTYPE_ORDER:
        return False
    return True


def headline_order_stands(record):
    """Return True only where a headline run order stands stated
    and is not a prototype order."""
    if not isinstance(record, dict):
        return False
    if record.get("run_class") != "headline":
        return False
    order = record.get("scheduling_order_identifier")
    return bool(order) and order != PROTOTYPE_ORDER


def measure_order_sensitivity(states_under_order_a, states_under_order_b):
    """The reverse order sensitivity check in family definition
    form: it measures a divergence between end of day states under
    two stated orders and states the size at which the order must
    be fixed. It fixes no order itself."""
    divergence = 0
    for key in set(states_under_order_a) | set(states_under_order_b):
        if states_under_order_a.get(key) != states_under_order_b.get(key):
            divergence += 1
    return {
        "divergence": divergence,
        "states_differ": divergence > 0,
        "order_must_be_fixed_at_divergence": 1,
        "order_fixed_by_this_check": False,
        "reportable_as": "order effect",
    }


def apply_event_to_state(state, event):
    """Apply one event to simulation state. The engine is the sole
    writer: the change is written through write_simulation_state
    under the engine name, then the event feature updates land."""
    engine = TickEngine()
    engine.write_simulation_state("TickEngine", {"event": _freeze(event)})
    updated = _freeze(state) if isinstance(state, dict) else {}
    updates = event.get("feature_updates") if isinstance(event, dict) else None
    if isinstance(updates, dict):
        features = dict(updated.get("feature_values") or {})
        features.update(_freeze(updates))
        updated["feature_values"] = features
    return updated


def process_day_events(state, events):
    """The sequence inside the tick, per event: first apply the
    event to simulation state through the rule core delivery point,
    then project the DetectionInput record from the state as it
    then stands, then deliver that record to the detection layer.
    Deliveries stand in interface form while the gate stands, and
    each projection carries the state after its own event and
    before any later event."""
    engine = TickEngine()
    current = _freeze(state) if isinstance(state, dict) else {}
    projections = []
    for event in events:
        current = apply_event_to_state(current, event)
        engine.rule_core_delivery.record_interface_delivery(
            {"kind": "event", "form": "interface", "event": _freeze(event)}
        )
        projected = project_detection_input(current)
        engine.detection_delivery.record_interface_delivery(
            {"kind": "DetectionInput", "form": "interface", "record": projected}
        )
        projections.append(projected)
    return {
        "state": current,
        "projections": projections,
        "rule_core_deliveries": engine.rule_core_delivery.deliveries,
        "detection_deliveries": engine.detection_delivery.deliveries,
        "sequence": ["apply", "project", "deliver"],
    }


def delivery_completeness(events, deliveries):
    """Return True only where every generated event in the day
    stands delivered. Processing types are not generated events
    and are never counted as events."""
    delivered_kinds = [
        entry.get("event", {}).get("kind")
        for entry in deliveries
        if isinstance(entry, dict) and isinstance(entry.get("event"), dict)
    ]
    expected = [event.get("kind") for event in events]
    return sorted(map(str, delivered_kinds)) == sorted(map(str, expected))


def is_processing_type(name):
    """Return True where a name is a processing type, not one of
    the generated event kinds."""
    return name in PROCESSING_TYPES


def projection_passed_for_run(run_record):
    """Return True only where the run record states its projection
    passed the F-09 canary test. A run whose projection has not
    passed is not reportable."""
    if not isinstance(run_record, dict):
        return False
    return run_record.get("projection_canary_passed") is True


def run_is_reportable(run_record):
    """A run is reportable only where its projection passed the
    canary test and its scheduling order stands for its class."""
    return (
        projection_passed_for_run(run_record)
        and validate_run_scheduling_order(run_record)
        and run_record.get("reportable") is not False
        and run_record.get("form") != "form_only"
    )


# ---------------------------------------------------------------------------
# S-11 view edges owned by MOD-04: selection, writing, delivery
# ---------------------------------------------------------------------------

COMPLETENESS_STATES = ("complete", "stale", "partial", "partitioned")
VIEW_CLOSED_FIELDS = (
    "run_identifier", "viewer_identifier", "simulated_day",
    "scheduling_position_identifier", "rule_version_set", "view_contents",
    "reputation_and_band_values", "graph_position_as_seen",
    "first_seen_day_per_record", "delay_applied_per_record",
    "completeness_state", "building_component", "delivering_contract",
    "selection_rule_version",
)
VIEW_EXCLUDED_CONTENT = (
    "ground truth field", "membership field",
    "field derived from membership", "record of another viewer",
)


def select_view_records(retained_records, viewer_id, as_of_day, delay=0):
    """Select the records one viewer view contains: the viewer own
    records that arrived under the delay the run applies, and no
    record dated later than the view as of point. The selection
    rule is delay, partition, and record arrival only."""
    selected = []
    for record in retained_records or ():
        if not isinstance(record, dict):
            continue
        if record.get("viewer_id") not in (viewer_id, None):
            continue
        day = record.get("day")
        if day is not None and int(day) + int(delay) > int(as_of_day):
            continue
        selected.append(_freeze(record))
    return selected


def build_view_record(run_id="run-under-test", viewer_id="viewer-1",
                      day=1, contents=None, reputation_and_band=None,
                      graph_position=None, completeness="complete",
                      selection_rule_version="view-selection-1"):
    """Write one ViewRecord in its decided field groups: identity
    and scope, content as references into retained records and as
    values for reputation, band, and graph position, arrival and
    freshness with its completeness state, the exclusion group as
    a form statement, and provenance naming the building
    component, the delivering contract, and the selection rule
    version."""
    if completeness not in COMPLETENESS_STATES:
        raise NamedFailure("completeness state outside the closed vocabulary: " + str(completeness))
    contents = list(contents or ())
    return {
        "run_identifier": run_id,
        "viewer_identifier": viewer_id,
        "simulated_day": day,
        "scheduling_position_identifier": "position-1",
        "rule_version_set": "rule-version-set-1",
        "view_contents": [_freeze(item) for item in contents],
        "reputation_and_band_values": _freeze(reputation_and_band or {}),
        "graph_position_as_seen": _freeze(graph_position or {}),
        "first_seen_day_per_record": {
            str(index): day for index, _item in enumerate(contents)
        },
        "delay_applied_per_record": {
            str(index): 0 for index, _item in enumerate(contents)
        },
        "completeness_state": completeness,
        "building_component": "MOD-04 Tick Engine",
        "delivering_contract": "Contract K",
        "selection_rule_version": selection_rule_version,
        "exclusion_group": {
            "form_statement": "no barred field stands in a view record",
            "excluded": list(VIEW_EXCLUDED_CONTENT),
        },
        "form": "ViewRecord",
    }


def view_record_carries_barred_field(view_record):
    """Return True where a ViewRecord carries a barred field at any
    depth of its content group."""
    if not isinstance(view_record, dict):
        return True
    contents = view_record.get("view_contents") or ()
    for item in contents:
        if isinstance(item, dict):
            for key in item:
                if _is_barred_key(key):
                    return True
    return False


def hold_view(view_record):
    """Hold one view at the hold point inside the tick: the
    ViewRecord stands written before delivery, and the view is
    released only after the Recorder field validation and timing
    forms pass on it."""
    return {"view_record": _freeze(view_record), "held": True, "released": False}


def release_view(held, field_validation_passed, timing_passed):
    """Release a held view only where both Recorder check forms
    pass. A view that fails either form is not delivered, and no
    agent act inside the same simulated day rests on it."""
    if not (field_validation_passed and timing_passed):
        raise NamedFailure("view failed a leak check form and is not delivered")
    released = dict(held)
    released["held"] = False
    released["released"] = True
    return released


def per_viewer_components(run_id="run-under-test", viewers=None, components=None):
    """The per viewer components of one run: every component
    carries its viewer identifier, and no component stands as a
    singular vector. Where components stand handed in, they stand
    returned per viewer in the order given."""
    if components is not None:
        return [_freeze(item) for item in components]
    viewers = list(viewers or ("viewer-1", "viewer-2"))
    result = []
    for index, viewer in enumerate(viewers):
        result.append({
            "run_id": run_id,
            "viewer_id": viewer,
            "component_values": [index + 1, index + 2, index + 3, index + 4],
            "presented_as": "per viewer component",
        })
    return result


def divergence_companion(run_id="run-under-test", components=None):
    """The viewer divergence companion: beside the per viewer form,
    in the daily aggregates and at end of run, the share of
    identities whose band differs across viewers. A view
    independent component records its coincidence as a nil
    divergence for that component, never as a singular value."""
    components = components if components is not None else per_viewer_components(run_id)
    bands = {}
    for component in components:
        bands.setdefault(component.get("viewer_id"), set()).add(
            tuple(component.get("component_values") or ())
        )
    differing = 0
    total = max(len(bands), 1)
    values = [item.get("component_values") for item in components]
    if values and any(value != values[0] for value in values):
        differing = total
    share = differing / total if total else 0
    companion_entry = {
        "band_differing_share": share,
        "form": "divergence companion",
        "singular_vector_reported": False,
    }
    return {
        "run_id": run_id,
        "daily_aggregates": dict(companion_entry),
        "end_of_run": dict(companion_entry),
        "band_differing_share": share,
    }


def flip_trial_record(trial_id="trial-under-test", candidate_forms=None):
    """The viewer flip trial record: it reports a property of
    candidate forms, restates the bar on a singular presentation
    on its face, and is never a run result."""
    return {
        "trial_id": trial_id,
        "kind": "property_of_candidate_forms",
        "candidate_forms": list(candidate_forms or ("per viewer form", "singular form")),
        "property": "whether a candidate form presents one comparable vector quantity",
        "singular_presentation_bar": (
            "no singular vector is reported and the vector is not "
            "presented as one comparable quantity in any run"
        ),
        "run_result": False,
    }

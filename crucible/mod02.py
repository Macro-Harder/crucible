"""MOD-02, Seed and Stream Engine.

Interface form only. The module states the engine interface in full:
derivation input in, stream state and draws out, and generator state in
the form checkpoints carry. Any generator, adopted or not, stands behind
this interface. No hash construction detail enters a run record beyond
the derivation version string and the recorded string parameter values
that Shape 5 states.

Gate standing. Design question DQ7-02 stands carried open in full and
register question NQ-24 stands open. No seed derivation, stream
inventory, or generator stands adopted. Until an adoption record
stands, no executable path in this module draws a seed, reads a clock,
or assigns a seed in completion order. Every executable derivation
entry point returns the gated refusal stated in this module. Order and
schedule independence stands as a stated invariant of this interface.
"""

from crucible import mod01 as _mod01

GATE_QUESTION = "DQ7-02"
REGISTER_QUESTION = "NQ-24"
GATED = "gated"
DERIVATION_GATED_FAILURE = "DERIVATION-GATED"
STREAM_EXHAUSTED_FAILURE = "STREAM-EXHAUSTED"

_DOMAINS = ("screening", "held out confirmation")
_CARDINALITY_BASIS = "inventory named in the adoption record"
_STREAM_RECOVERY_FORMS = ("fresh run",)
_BATTERY_RESULT_STATES = ("passed", "failed", "gated")
_BATTERY_FAILURE_RECORD_FIELDS = (
    "derivation input set",
    "advance sample size",
    "first mismatching stream class",
    "two differing outputs by reference",
)
_CANDIDATE_SEPARATOR = "|"
_OPEN_LIMBS = (
    ("substream extension", "NQ-60 item 5"),
    ("analysis resampling", "NQ-60 item 7"),
)
_EXPOSURE_LOG_FIELDS = (
    "family and run identifier",
    "domain of exposed material",
    "exposed material kind",
    "form of exposure",
    "receiving party",
    "channel of exposure",
    "time of exposure",
    "exposure and adaptive round counts",
    "next recorded action of receiving party",
    "commitment state",
    "disclosure state",
    "consequence recorded for the result",
    "judge note",
)
_REPORTER_READINGS = (
    "not gameable on exposure grounds",
    "gameable",
    "cannot tell from this log",
)
_DERIVATION_INPUT_FIELDS = (
    "derivation_version",
    "domain",
    "root_seed_reference",
    "scenario_identifier",
    "run_identifier",
    "stream_class_identifier",
    "parameter_values",
)
_BARRED_DERIVATION_TEXTS = (
    "arithmetic on a root seed",
    "small increment on a root seed",
    "random starting point in a shared sequence",
)


SeedDerivationInput = _mod01.SeedDerivationInput
StreamSet = _mod01.StreamSet


def mod01_surface():
    """Return the MOD-01 module this engine depends on."""
    return _mod01


def mod01_type(name):
    """Return a type named on the MOD-01 surface, or None if absent."""
    return getattr(_mod01, name, None)


def gate_standing():
    """Return the adoption gate standing for this module."""
    return {
        "gate": GATE_QUESTION,
        "register_question": REGISTER_QUESTION,
        "standing": "carried open in full",
        "executable_derivation": GATED,
        "adoption_record": None,
    }


def domain_vocabulary():
    """Return the closed two value domain vocabulary of Shape 5."""
    return _DOMAINS


def validate_domain(domain):
    """Return True only for a stated domain value."""
    return domain in _DOMAINS


def validate_derivation_domain_use(purpose=None, seed_domain=None):
    """Return True only where a seed is used inside its own domain."""
    if not validate_domain(purpose) or not validate_domain(seed_domain):
        return False
    return purpose == seed_domain


def _base_iter(value):
    """Iterate a list, tuple, set, or frozenset part through its
    base class iteration, never through a reading the part
    itself supplies."""
    iter_by_base = {list: list.__iter__, tuple: tuple.__iter__,
                    set: set.__iter__, frozenset: frozenset.__iter__}
    for base, base_iter in iter_by_base.items():
        if isinstance(value, base):
            return base_iter(value)
    return iter(value)


def _stream_set_classes(stream_set):
    """Return the stream class names a run StreamSet carries, or
    None where no StreamSet stands handed in. A StreamSet stands
    read in its typed form, in record form, or as a plain list of
    class names, and each inventory entry stands read as a name
    or as a record carrying its class name. Every reading runs
    through base class operations only, never through a protocol
    the handed value supplies. A StreamSet that stands handed in
    but cannot be read in any stated form stands refused in this
    module named failure form, a ValueError, and never falls back
    to the no StreamSet behaviour. A plain dict carrying no
    inventory key stands in no stated form and stands refused
    in the same form, instead of reading its keys as classes."""
    if stream_set is None:
        return None
    typed = False
    if isinstance(stream_set, dict):
        values = stream_set
    elif isinstance(stream_set, (list, tuple, set, frozenset)):
        values = stream_set
    else:
        stored = None
        try:
            instance_dict = object.__getattribute__(
                stream_set, "__dict__")
        except Exception:
            instance_dict = None
        if isinstance(instance_dict, dict) and dict.__contains__(
                instance_dict, "values"):
            stored = dict.__getitem__(instance_dict, "values")
        if isinstance(stored, dict):
            values = stored
            typed = True
        elif isinstance(getattr(stream_set, "values", None), dict):
            values = stream_set.values
            typed = True
        else:
            raise ValueError(
                "stream set stands in no stated form: "
                + repr(stream_set))
    inventory = None
    inventory_found = False
    if isinstance(values, dict):
        for key in ("stream_class_inventory", "stream_classes",
                    "inventory", "classes"):
            if dict.__contains__(values, key):
                inventory = dict.__getitem__(values, key)
                inventory_found = True
                break
        if not inventory_found:
            raise ValueError(
                "stream set carries no stream class inventory")
    elif isinstance(values, (list, tuple, set, frozenset)):
        inventory = list(_base_iter(values))
        inventory_found = True
    if inventory_found:
        if isinstance(inventory, dict):
            inventory = list(dict.__iter__(inventory))
        elif isinstance(inventory, (list, tuple, set, frozenset)):
            inventory = list(_base_iter(inventory))
        else:
            raise ValueError(
                "stream class inventory stands in no stated form: "
                + repr(inventory))
    classes = []
    for entry in inventory or []:
        if isinstance(entry, dict):
            name = None
            for key in ("stream_class_identifier", "stream_class",
                        "name", "identifier", "class"):
                if dict.get(entry, key) is not None:
                    name = dict.get(entry, key)
                    break
            if name is None:
                raise ValueError(
                    "stream class inventory entry names no class: "
                    + repr(entry))
            classes.append(name)
        else:
            classes.append(entry)
    for name in classes:
        try:
            hash(name)
        except TypeError:
            raise ValueError(
                "stream class entry stands in no stated form: "
                + repr(name)) from None
    return classes


def validate_stream_cardinality(counts=None, stream_set=None,
                                **kwargs):
    """Return True only at exactly one derivation input per class.

    The counts mapping names each stream class in the run StreamSet
    against the number of derivation inputs handed over for it. Any
    count other than one, for any class, fails. An empty set fails.
    Where the run StreamSet stands handed in, as the second
    argument or under a stream set keyword, the classes named in
    the counts must stand as exactly the classes of that set: a
    class of the set with no count stands missing and fails, and
    a counted class the set does not carry stands extra and fails.
    A StreamSet that stands handed in but cannot be read in any
    stated form stands refused with a ValueError, in this module
    named failure form, instead of falling back to the no
    StreamSet behaviour.
    """
    if stream_set is None:
        for key in ("streamset", "run_stream_set", "stream_classes",
                    "expected_classes"):
            if key in kwargs:
                stream_set = kwargs[key]
                break
    if counts is None:
        return False
    try:
        items = list(dict.items(counts))
    except TypeError:
        return False
    if not items:
        return False
    classes = _stream_set_classes(stream_set)
    if classes is not None:
        if len(items) != len(classes):
            return False
        remaining = list(classes)
        for name, _count in items:
            matched = None
            for index, candidate in enumerate(remaining):
                if _base_name_eq(name, candidate):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
    for _name, count in items:
        if isinstance(count, list):
            count = list.__len__(count)
        elif isinstance(count, tuple):
            count = tuple.__len__(count)
        if isinstance(count, bool):
            if count is not True:
                return False
        elif isinstance(count, int):
            if not int.__eq__(int.__new__(int, count), 1):
                return False
        elif count != 1:
            return False
    return True


def _base_name_eq(name, candidate):
    """Return whether two class names stand equal under the base
    string equality, never under a hash or equality reading a
    handed name supplies. Names that are not strings stand judged
    by identity or by their plain form, as before."""
    if isinstance(name, str) and isinstance(candidate, str):
        return str.__eq__(name, candidate) is True
    if isinstance(name, str) or isinstance(candidate, str):
        return False
    return name is candidate or name == candidate


def cardinality_basis():
    """Return the inventory the cardinality check is pinned against."""
    return _CARDINALITY_BASIS


def stream_inventory_standing():
    """Return the standing of the Shape 6 stream inventory."""
    return "recommended and unadopted"


def validate_family_derivation(version=None, adoption_record=None,
                               family_record=None):
    """Return True only where an adoption record adopts the version.

    A family record naming a derivation version with no adoption
    record behind it fails validation, and no reportable run starts
    on it. An adoption record adopts exactly one triple: the
    derivation version, the stream inventory, and the generator.
    """
    if family_record is not None and isinstance(family_record, dict):
        if version is None:
            version = family_record.get("derivation_version")
        if adoption_record is None:
            adoption_record = family_record.get("adoption_record")
    if adoption_record is None:
        return False
    if not validate_adoption_record(adoption_record):
        return False
    return version is not None and version == adoption_record.get(
        "derivation_version")


def validate_adoption_record(record):
    """Return True only for a complete adoption triple."""
    if not isinstance(record, dict):
        return False
    for key in ("derivation_version", "stream_inventory", "generator"):
        if not record.get(key):
            return False
    return True


def derivation_text_refusal(text):
    """Return the refusal for a derivation text, naming its ground.

    Two grounds stand apart and are never merged. A text that derives
    a stream seed by arithmetic on a root seed, by a small increment
    on a root seed, or by a random starting point in a shared
    sequence is refused on its content ground, the barred derivation
    forms, and supplies no run, no replicate, and no battery input.
    Any other text is refused on the gate ground alone: while the
    DQ7-02 adoption gate stands, a derivation text alone, with no
    adoption record in hand, never validates, and that refusal is
    the recorded gated refusal, DERIVATION-GATED, naming DQ7-02.
    """
    if not isinstance(text, str):
        return {
            "valid": False,
            "ground": "not a text",
            "failure": "INVALID-TEXT",
            "gate": None,
        }
    lowered = text.lower()
    for barred in _BARRED_DERIVATION_TEXTS:
        if barred in lowered:
            return {
                "valid": False,
                "ground": "barred derivation form: " + barred,
                "failure": "BARRED-DERIVATION-FORM",
                "gate": None,
                "supplies_run": False,
                "supplies_replicate": False,
                "supplies_battery_input": False,
            }
    refusal = gated_refusal("validate family derivation text")
    refusal["valid"] = False
    refusal["ground"] = (
        "gate " + GATE_QUESTION + ": no adoption record stands, so a "
        "derivation text alone never validates"
    )
    return refusal


def validate_family_derivation_text(text):
    """Return whether a derivation text may stand in a family
    record, as the boolean its name promises: False on every
    refusal ground (a barred derivation form, the DQ7-02 gate
    ground, and a value that is not a text), and True only on a
    text that validates. No refusal stands returned in a truthy
    form, so no caller reading this function as a boolean can
    read a refused text as passing. The full refusal record,
    naming its ground on every ground in the F-LE-05 form, stands
    at derivation_text_refusal, unchanged. DQ7-02 stands
    unadopted and its gated refusal form stands."""
    refusal = derivation_text_refusal(text)
    return bool(refusal.get("valid"))


def make_derivation_input(derivation_version=None, domain=None,
                          root_seed_reference=None,
                          scenario_identifier=None, run_identifier=None,
                          stream_class_identifier=None,
                          parameter_values=None):
    """Build one SeedDerivationInput value in the Shape 5 field order.

    Every parameter value that enters the derivation enters as a
    recorded string. A value that is not a string, including any
    binary float rendering, is refused at this boundary.
    """
    if not validate_domain(domain):
        raise ValueError("domain outside the two value vocabulary")
    params = dict(parameter_values or {})
    for key, value in params.items():
        if not isinstance(value, str):
            raise ValueError(
                "parameter value for " + str(key)
                + " is not a recorded string")
    return {
        "derivation_version": derivation_version,
        "domain": domain,
        "root_seed_reference": root_seed_reference,
        "scenario_identifier": scenario_identifier,
        "run_identifier": run_identifier,
        "stream_class_identifier": stream_class_identifier,
        "parameter_values": params,
    }


def validate_derivation_input(value):
    """Return True only for a complete Shape 5 input value."""
    if not isinstance(value, dict):
        return False
    for field in _DERIVATION_INPUT_FIELDS:
        if field not in value:
            return False
    if not validate_domain(value.get("domain")):
        return False
    if not isinstance(value.get("derivation_version"), str):
        return False
    if not value.get("derivation_version"):
        return False
    params = value.get("parameter_values")
    if not isinstance(params, dict):
        return False
    for item in params.values():
        if not isinstance(item, str):
            return False
    return True


def derivation_input_fields():
    """Return the Shape 5 field names in their stated order."""
    return _DERIVATION_INPUT_FIELDS


def derivation_input_record(value):
    """Return one derivation input in the MOD-01 Form 5 field naming.

    The naming is the type census naming: derivation version string,
    domain, recorded root seed, scenario identifier, run identifier,
    stream class identifier, and the parameter values as a tuple of
    recorded strings, one per parameter, in name order.
    """
    if not isinstance(value, dict):
        return {}
    params = value.get("parameter_values") or {}
    rendered = tuple(
        str(name) + "=" + str(params[name]) for name in sorted(params))
    return {
        "derivation_version_string": value.get("derivation_version"),
        "domain": value.get("domain"),
        "recorded_root_seed": value.get("root_seed_reference"),
        "scenario_identifier": value.get("scenario_identifier"),
        "run_identifier": value.get("run_identifier"),
        "stream_class_identifier": value.get("stream_class_identifier"),
        "parameter_values": rendered,
    }


def typed_derivation_input(value):
    """Return the MOD-01 SeedDerivationInput type over one input value.

    The typed form wraps the Form 5 record naming.
    """
    record = derivation_input_record(value)
    return SeedDerivationInput(record)


def run_record_derivation_fields(value):
    """Return the only derivation detail a run record may carry.

    The carriage is the derivation version string and the recorded
    string parameter values, and no other derivation detail.
    """
    if not isinstance(value, dict):
        return {"derivation_version": None, "parameter_values": {}}
    carried = value.get("parameter_values") or {}
    return {
        "derivation_version": value.get("derivation_version"),
        "parameter_values": {
            name: carried[name]
            for name in sorted(carried, key=lambda item: str(item))
        },
    }


def gated_refusal(action):
    """Return the named gated refusal every derivation path returns.

    Beside its codes, the refusal states its ground in a plain
    sentence and what stands next in words: no adoption record
    stands for the gate, and nothing stands for the operator to
    do, the block sitting with the decision on the adoption
    record. The gate itself, its codes, and the nothing drawn
    standing stand unchanged.
    """
    return {
        "status": GATED,
        "gate": GATE_QUESTION,
        "register_question": REGISTER_QUESTION,
        "action": action,
        "failure": DERIVATION_GATED_FAILURE,
        "seed_drawn": False,
        "ground_in_words": (
            "No adoption record for the DQ7-02 gate stands, so no "
            "seed can be derived and the gated act cannot proceed."),
        "next_step": (
            "Nothing stands for the operator to do here; the block "
            "sits with the decision on the DQ7-02 adoption record."),
    }


def derive_seed(derivation_input=None, **_ignored):
    """Derivation entry point. Gated: returns the gated refusal."""
    return gated_refusal("derive seed")


def derive_stream_seed(derivation_input=None, **_ignored):
    """Stream seed entry point. Gated: returns the gated refusal."""
    return gated_refusal("derive stream seed")


def derive_stream_state(derivation_inputs=None, **_ignored):
    """Stream state entry point. Gated: returns the gated refusal."""
    return gated_refusal("derive stream state")


def advance_stream_state(state=None, **_ignored):
    """Stream advance entry point. Gated: returns the gated refusal."""
    return gated_refusal("advance stream state")


def request_generator(**_ignored):
    """Generator supply entry point. Gated: returns the refusal."""
    return gated_refusal("supply generator")


def initial_stream_state(stream_class=None, carried_positions=0):
    """Return a stream state record at its first position.

    This is state carriage only. It draws no seed and assigns none.
    """
    return {
        "stream_class": stream_class,
        "position": 0,
        "carried_positions": int(carried_positions),
        "draws_made": 0,
    }


def draw_from_stream(stream_class=None, position=None,
                     carried_positions=None, state=None):
    """Draw from a purpose stream, in the forms the gate allows.

    Drawing past the position the stream carries records the named
    failure STREAM-EXHAUSTED, with the run status failed, its partial
    records marked partial, and no claim supported. A draw inside the
    carried positions needs a derived seed, so while the adoption
    gate stands it returns the gated refusal and draws nothing.
    """
    if state is not None and isinstance(state, dict):
        if stream_class is None:
            stream_class = state.get("stream_class")
        if position is None:
            position = state.get("position")
        if carried_positions is None:
            carried_positions = state.get("carried_positions")
    if position is None:
        raise ValueError(
            "stream state lacks a position: supply the position "
            "the draw stands at")
    if carried_positions is None:
        raise ValueError(
            "stream state lacks its carried positions: supply the "
            "carried positions of the stream")
    if int(position) >= int(carried_positions):
        return {
            "failure": STREAM_EXHAUSTED_FAILURE,
            "stream_class": stream_class,
            "position": int(position),
            "run_status": "failed",
            "partial_records_marked": True,
            "supports_claim": False,
            "recovery_forms": _STREAM_RECOVERY_FORMS,
        }
    refusal = gated_refusal("draw from stream")
    refusal["stream_class"] = stream_class
    refusal["position"] = int(position)
    return refusal


def stream_recovery_forms():
    """Return the only recovery form after STREAM-EXHAUSTED."""
    return _STREAM_RECOVERY_FORMS


def candidate_separator():
    """Return the separator character the candidate encoding uses."""
    return _CANDIDATE_SEPARATOR


def encode_candidate_input(values):
    """Encode one candidate derivation input in joined input form.

    Each field enters as its name and its recorded string value, each
    length prefixed, joined by the candidate separator. Two inputs
    that differ in any field encode differently, including over empty
    values, values holding the separator, and values whose plain
    concatenation coincides across different field splits. This is a
    candidate encoding for the adoption test only. It derives no
    seed and adopts no derivation form.
    """
    if not isinstance(values, dict):
        raise ValueError("candidate input is not a field mapping")
    parts = []
    for key in sorted(values, key=lambda item: str(item)):
        name = str(key)
        raw = values[key]
        if not isinstance(raw, str):
            raise ValueError(
                "parameter value for " + name
                + " is not a recorded string")
        text = raw
        parts.append(
            type(key).__name__ + ":" + str(len(name)) + ":" + name + "="
            + str(len(text)) + ":" + text)
    return _CANDIDATE_SEPARATOR.join(parts)


def battery_record_counts_as_run(record):
    """Return True only where the size stands stated in advance."""
    if not isinstance(record, dict):
        return False
    return record.get("advance_sample_size_stated") is True


def validate_battery_record(record):
    """Return True only for a complete candidate battery record.

    The record states, beside the single stream results for each test
    family, the inter stream element result for that family.
    """
    if not isinstance(record, dict):
        return False
    single = record.get("single_stream_results")
    inter = record.get("inter_stream_element")
    if not isinstance(single, dict) or not single:
        return False
    if not isinstance(inter, dict):
        return False
    for family in single:
        if not inter.get(family):
            return False
    return True


def battery_verdict_state(inter_stream_element_recorded=False,
                          verdict_recorded=False, verdict=None):
    """Return the standing of one battery verdict.

    A verdict recorded before the inter stream element result for
    its family stands recorded is gated, never passed. A recorded
    verdict outside the three states the battery result stands in
    stands gated, never passed: no fourth state converts to a
    pass in any state of the record.
    """
    if not inter_stream_element_recorded:
        return GATED
    if not verdict_recorded:
        return GATED
    if verdict in _BATTERY_RESULT_STATES:
        return verdict
    return GATED


def battery_result_states():
    """Return the three states a generator battery result may stand in."""
    return _BATTERY_RESULT_STATES


def battery_failure_record_fields():
    """Return the fields a battery failure record names."""
    return _BATTERY_FAILURE_RECORD_FIELDS


def determinism_statement_permitted(battery_state=None,
                                    corrected_battery_passed=False):
    """Return whether a determinism statement may stand for a version.

    A failed battery voids every determinism statement for its
    version and bars its runs from reportable use until a corrected
    version passes a fresh battery. A gated battery permits none.
    """
    if battery_state == "passed":
        return True
    if battery_state == "failed":
        return bool(corrected_battery_passed)
    return False


def _position_value(value):
    if isinstance(value, dict):
        return int(value.get("position", 0))
    return int(value)


def _state_from_held(held_state):
    if not isinstance(held_state, dict):
        return None
    if "stream_states" in held_state:
        streams = {}
        for name in sorted(held_state.get("stream_states") or {},
                           key=lambda item: str(item)):
            streams[name] = {
                "position": _position_value(
                    held_state["stream_states"][name])}
        return {
            "run_id": held_state.get("run_id"),
            "stream_states": streams,
            "stream_inventory_standing": held_state.get(
                "stream_inventory_standing", _CARDINALITY_BASIS),
            "carriage": held_state.get(
                "carriage", "generator state for checkpoints"),
        }
    streams = {}
    for name in sorted(held_state, key=lambda item: str(item)):
        streams[name] = {"position": _position_value(held_state[name])}
    return {
        "run_id": None,
        "stream_states": streams,
        "stream_inventory_standing": _CARDINALITY_BASIS,
        "carriage": "generator state for checkpoints",
    }


def _carried_generator_state(run_id, stream_classes=None,
                             held_state=None, positions=None):
    if held_state is not None:
        carried = _state_from_held(held_state)
        if carried is not None:
            if run_id is not None:
                carried["run_id"] = run_id
            return carried
    streams = {}
    names = list(stream_classes or ())
    if positions:
        for name in positions:
            if name not in names:
                names.append(name)
    for name in sorted(names, key=lambda item: str(item)):
        position = 0
        if positions and name in positions:
            position = _position_value(positions[name])
        streams[name] = {"position": position}
    return {
        "run_id": run_id,
        "stream_states": streams,
        "stream_inventory_standing": _CARDINALITY_BASIS,
        "carriage": "generator state for checkpoints",
    }


def checkpoint_generator_state(run_id=None, stream_classes=None,
                               held_state=None, positions=None):
    """Return the generator state a checkpoint holds for a run.

    Where the caller hands in held positions, through the positions
    mapping or through a held state, the checkpoint carries those
    positions as they stand, never a regenerated initial position.
    With no held positions handed in, every stream stands at its
    first position, as before. This is state carriage only: it
    draws no seed and assigns none.
    """
    return _carried_generator_state(
        run_id, stream_classes, held_state=held_state,
        positions=positions)


def resume_consumed_generator_state(run_id=None, scope=None,
                                    stream_classes=None,
                                    held_state=None, positions=None):
    """Return the generator state the resume path consumes.

    Carriage only: where a held state stands handed in, the
    consumed state is that held state, field for field, at the
    positions it carries. With no held state handed in, the
    consumed state stands built from the run identifier and the
    stream classes, or from the positions handed in, as before.
    The scope argument names the resume scope the caller
    states and forms no part of the carried state.
    """
    return _carried_generator_state(
        run_id, stream_classes, held_state=held_state,
        positions=positions)


def validate_generator_state_carriage(held, consumed):
    """Return True only where held and consumed state agree in full."""
    return held == consumed


def exposure_log_fields():
    """Return the thirteen fields of the seed and setting exposure log."""
    return _EXPOSURE_LOG_FIELDS


def make_exposure_log_entry(values=None):
    """Build one exposure log entry over the thirteen stated fields.

    A field the caller does not state stands in the entry as not
    recorded, so silence on a channel stays visible in the record.
    """
    given = dict(values or {})
    entry = {}
    for field in _EXPOSURE_LOG_FIELDS:
        entry[field] = given.get(field, "not recorded")
    return entry


def validate_exposure_log_entry(entry):
    """Return True only where an entry carries all thirteen fields."""
    if not isinstance(entry, dict):
        return False
    return tuple(entry.keys()) == _EXPOSURE_LOG_FIELDS or all(
        field in entry for field in _EXPOSURE_LOG_FIELDS)


def exposure_reading_rule():
    """Return the reading rule for the exposure log, in short form."""
    return ("silence on a channel is recorded as cannot tell and "
            "never as no exposure, and a screening result never "
            "confirms itself")


def channel_silence_reading():
    """Return the reading recorded where a channel stands silent."""
    return "cannot tell"


def screening_confirms_itself():
    """Return whether a screening result may confirm itself."""
    return False


def reporter_readings():
    """Return the three readings the Reporter records for a family."""
    return _REPORTER_READINGS


def confirmation_label_presents_basis_decided():
    """Return whether an exposed confirmation label decides a basis.

    An exposed confirmation label is never presented as the DQ7-07
    basis decided. This function states that bar as a value.
    """
    return False


def wording_claims_secrecy_property(scope=None):
    """Return whether suite or run wording claims a secrecy property.

    No such claim stands while NQ-60 item 6 stands open. The scope
    argument names the wording set read and forms no part of the
    answer.
    """
    return False


def open_limb_names():
    """Return the open limbs this module carries, with their items."""
    return _OPEN_LIMBS


def validate_open_limb_standing(limb, named_as=None):
    """Return True only where an open limb stands named as open."""
    names = [name for name, _item in _OPEN_LIMBS]
    if limb not in names:
        return False
    return named_as == "open"


def suite_fixes_open_limb(limb):
    """Return whether any suite test fixes an open limb by form choice."""
    return False


def interface_invariants():
    """Return the stated invariants of this interface."""
    return (
        "order and schedule independence",
        "no seed drawn while the adoption gate stands",
        "no seed read from a clock",
        "no seed assigned in completion order",
    )


def order_and_schedule_independence():
    """Return the order and schedule independence invariant."""
    return "order and schedule independence"


def clock_read_used():
    """Return whether any path in this module reads a clock."""
    return False


def completion_order_assignment_used():
    """Return whether any path assigns a seed in completion order."""
    return False


__all__ = [
    "GATE_QUESTION",
    "REGISTER_QUESTION",
    "GATED",
    "DERIVATION_GATED_FAILURE",
    "STREAM_EXHAUSTED_FAILURE",
    "SeedDerivationInput",
    "StreamSet",
    "mod01_surface",
    "mod01_type",
    "gate_standing",
    "domain_vocabulary",
    "validate_domain",
    "validate_derivation_domain_use",
    "validate_stream_cardinality",
    "cardinality_basis",
    "stream_inventory_standing",
    "validate_family_derivation",
    "validate_adoption_record",
    "validate_family_derivation_text",
    "make_derivation_input",
    "validate_derivation_input",
    "derivation_input_fields",
    "derivation_input_record",
    "typed_derivation_input",
    "run_record_derivation_fields",
    "gated_refusal",
    "derivation_text_refusal",
    "derive_seed",
    "derive_stream_seed",
    "derive_stream_state",
    "advance_stream_state",
    "request_generator",
    "initial_stream_state",
    "draw_from_stream",
    "stream_recovery_forms",
    "candidate_separator",
    "encode_candidate_input",
    "battery_record_counts_as_run",
    "validate_battery_record",
    "battery_verdict_state",
    "battery_result_states",
    "battery_failure_record_fields",
    "determinism_statement_permitted",
    "checkpoint_generator_state",
    "resume_consumed_generator_state",
    "validate_generator_state_carriage",
    "exposure_log_fields",
    "make_exposure_log_entry",
    "validate_exposure_log_entry",
    "exposure_reading_rule",
    "channel_silence_reading",
    "screening_confirms_itself",
    "reporter_readings",
    "confirmation_label_presents_basis_decided",
    "wording_claims_secrecy_property",
    "open_limb_names",
    "validate_open_limb_standing",
    "suite_fixes_open_limb",
    "interface_invariants",
    "order_and_schedule_independence",
    "clock_read_used",
    "completion_order_assignment_used",
]

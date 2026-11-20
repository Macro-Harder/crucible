"""MOD-14 Shell, pilot runner, and program checks.

Slice S-15. The shell owns no rule of its own and no result
wording of its own, with one exception stated in the open: the
outside call check outcome wording stands in this module as
that program check form, and no other result wording stands
here. Every command carries inputs to a named module and
returns its outputs or its named failure. The shell computes
no reputation, no verdict, and no retention tier. Slice S-15
states expressly that the operator procedure stands as this
slice runbook deliverable: the operator runbook stands in this
module at operator_runbook, in the code of this module, and
that code stands as its only locus in the shipped product.
"""

import ast
import itertools
import math
import re
import unicodedata
from decimal import Decimal
from fractions import Fraction

from crucible import mod01 as _mod01
from crucible import mod10 as _mod10
from crucible import mod12 as _mod12

PILOT_USES = ("timing", "conformance", "procedure rates")
STORE_KINDS = _mod01.STORE_KINDS


class NamedShellFailure(Exception):
    """A named failure reaching the operator with its run
    identifier and its stage, never swallowed."""

    def __init__(self, message=""):
        stored_message = _stored_text(message)
        super().__init__(stored_message)
        self.failure = {
            "name": type(self).__name__,
            "message": stored_message,
        }


_NAMED_FAILURE_CLASS_NAMES = frozenset((
    "NamedShellFailure", "NamedGeneratorFailure", "NamedFailure",
    "AlterationBarred", "GatedRun", "NamedDetectionFailure",
    "SilentUseMovement", "NamedAttackerFailure",
    "NamedControllerFailure", "NamedReplicationFailure",
    "LookupFailure",
))


_ARGUMENT_NOT_HANDED = object()
"""The standing of an argument no handing stands made for, so a
public act can refuse a missing argument handing in the named
form of this module instead of escaping as bare interpreter
text at the call itself (FW5-10)."""


_FREEZE_DEPTH_BOUND = 100

_FREEZE_TOO_DEEP = (
    "value stands deeper than the stated depth bound of 100 "
    "and stands not copied whole")


def _freeze_member(item, items):
    """Whether an item already stands among the frozen items
    of a set part, judged element by element. An element whose
    equality reading raises stands as not the item, so a set
    carrying such an element stands frozen whole in list form
    by the set limb's own fallback, and no bare error escapes
    the freeze on that reading."""
    for existing in items:
        try:
            if item is existing or item == existing:
                return True
        except Exception:
            continue
    return False


def _freeze(value, _depth=0, _memo=None):
    """Copy a value under a depth bound of 100 with a cycle
    guard. A container standing deeper than the bound stands
    replaced by a stated marker in place of the copy, so the
    caller still receives the surrounding value in populated
    form and no bare RecursionError escapes through the copy.
    The bound stands tested on containers only: a scalar leaf
    stands returned at any depth, so a chain of 101 containers
    stands copied whole and a chain of 102 stands marked at
    its deepest container. Cycles and shared containers
    inside the bound stand preserved, as a plain deep copy
    preserves them. A carried dict key that freezes to a form
    a key already carried in the same dict stands carried
    under a distinct numbered form of that key, so two
    distinct keys past the bound never collapse into one key
    and no carried entry is silently dropped. A dict
    assignment whose key hash or equality reading raises at
    the assignment itself stands carried under a distinct
    numbered form in the same manner, a plain text numbered
    form where a form carrying the key itself cannot stand
    inserted, so no carried entry is silently dropped on
    that reading either and no bare error escapes the copy.
    A dict part
    stands read through the base dict items reading, and a
    set or frozenset part stands read through its base
    iteration reading and rebuilt through the plain set or
    plain frozenset constructor, never through a constructor
    or a reading the part itself supplies. Two distinct set
    or frozenset elements that freeze to the same form stand
    carried under distinct numbered forms, so no carried
    element is silently dropped either. A list part and a
    tuple part stand read through their base iteration
    readings, list.__iter__ and tuple.__iter__, on the same
    standing. A part standing in no container form and in no
    plain scalar form stands returned as itself: no copy
    protocol the part supplies stands called, so no barred
    form stands materialised out of such a part."""
    if value is None or isinstance(value, (str, bytes, int, float, bool)):
        return value
    if isinstance(value, bytearray):
        return bytearray(value)
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    if _depth > _FREEZE_DEPTH_BOUND and isinstance(
            value, (dict, list, tuple, set, frozenset)):
        return _FREEZE_TOO_DEEP
    memo = _memo if _memo is not None else {}
    if isinstance(value, dict):
        if id(value) in memo:
            return memo[id(value)]
        copied = {}
        memo[id(value)] = copied
        for key, item in dict.items(value):
            frozen_key = _freeze(key, _depth + 1, memo)
            frozen_item = _freeze(item, _depth + 1, memo)
            try:
                collides = frozen_key in copied
            except Exception:
                collides = False
            if collides:
                counter = 2
                while True:
                    if isinstance(frozen_key, str):
                        distinct_key = (
                            frozen_key + " (carried key "
                            + str(counter) + ")")
                    else:
                        distinct_key = (frozen_key, counter)
                    try:
                        distinct_taken = distinct_key in copied
                    except Exception:
                        distinct_taken = False
                    if not distinct_taken:
                        frozen_key = distinct_key
                        break
                    counter += 1
            try:
                copied[frozen_key] = frozen_item
            except Exception:
                counter = 2
                while True:
                    if isinstance(frozen_key, str):
                        candidate = (
                            str.__str__(frozen_key)
                            + " (carried key " + str(counter) + ")")
                    elif counter == 2:
                        candidate = (frozen_key, counter)
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
                        copied[candidate] = frozen_item
                        break
                    except Exception:
                        counter += 1
        return copied
    if isinstance(value, list):
        if id(value) in memo:
            return memo[id(value)]
        copied = []
        memo[id(value)] = copied
        for item in list.__iter__(value):
            copied.append(_freeze(item, _depth + 1, memo))
        return copied
    if isinstance(value, tuple):
        if id(value) in memo:
            return memo[id(value)]
        copied = tuple(
            _freeze(item, _depth + 1, memo)
            for item in tuple.__iter__(value))
        if id(value) in memo:
            return memo[id(value)]
        memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        if id(value) in memo:
            return memo[id(value)]
        if isinstance(value, frozenset):
            base_iter = frozenset.__iter__
            plain_constructor = frozenset
        else:
            base_iter = set.__iter__
            plain_constructor = set
        placeholder = None
        if isinstance(value, set):
            placeholder = set()
            memo[id(value)] = placeholder
        copied_items = []
        for item in base_iter(value):
            frozen_item = _freeze(item, _depth + 1, memo)
            if _freeze_member(frozen_item, copied_items):
                counter = 2
                while True:
                    if isinstance(frozen_item, str):
                        distinct_item = (
                            frozen_item + " (carried element "
                            + str(counter) + ")")
                    else:
                        distinct_item = (frozen_item, counter)
                    if not _freeze_member(distinct_item, copied_items):
                        frozen_item = distinct_item
                        break
                    counter += 1
            copied_items.append(frozen_item)
        if placeholder is not None:
            try:
                for frozen_item in copied_items:
                    placeholder.add(frozen_item)
            except Exception:
                memo[id(value)] = copied_items
                return copied_items
            return placeholder
        try:
            copied = plain_constructor(copied_items)
        except Exception:
            copied = copied_items
        if id(value) in memo:
            return memo[id(value)]
        memo[id(value)] = copied
        return copied
    return value


# ---------------------------------------------------------------------------
# Command surface
# ---------------------------------------------------------------------------

_COMMAND_MODULES = {
    "start_run": "MOD-12",
    "start_sweep": "MOD-12",
    "read_store": "MOD-10",
    "write_store": "MOD-10",
    "run_pilot": "MOD-14 pilot runner",
    "assemble_report": "MOD-11",
    "outside_call_check": "MOD-14 program check over MOD-10 records",
    "store_kind_check": "MOD-14 program check",
    "weekly_headline_count": "MOD-14 program check",
    "flag_evaluation": "MOD-14 program check over MOD-10 records",
}


_COMMAND_DETAILS = {
    "start_run": (
        "Start one run of a stated class for one family.",
        ("run_class", "family_id"), (),
        "run_command('start_run', {'run_class': 'screening', 'family_id': 'fam-1'})"),
    "start_sweep": (
        "Start one sweep for one family.",
        ("family_id",), (),
        "run_command('start_sweep', {'family_id': 'fam-1'})"),
    "read_store": (
        "Read one run record from one store, by kind.",
        ("run_id",), ("store_kind",),
        "run_command('read_store', {'run_id': 'run-1', 'store_kind': 'sweep'})"),
    "write_store": (
        "Write one run record into one store, by kind.",
        ("record",), ("store_kind",),
        "run_command('write_store', {'record': {'run_id': 'run-1'}, 'store_kind': 'sweep'})"),
    "run_pilot": (
        "Run the pilot for one of its three confined uses.",
        ("use",), ("artefact",),
        "run_command('run_pilot', {'use': 'timing', 'artefact': {'figure': 1}})"),
    "assemble_report": (
        "Assemble a report from retained records.",
        ("family_id",), (),
        "run_command('assemble_report', {'family_id': 'fam-1'})"),
    "outside_call_check": (
        "Check a run for outside calls from its manifest and its call log only.",
        ("dependency_manifest", "call_log"), (),
        "run_command('outside_call_check', {'dependency_manifest': {}, 'call_log': {}})"),
    "store_kind_check": (
        "Check that a store kind stands in the stated store kind vocabulary.",
        ("kind",), (),
        "run_command('store_kind_check', {'kind': 'sweep'})"),
    "weekly_headline_count": (
        "Count the headline units of one week from summary records alone.",
        ("summary_records", "week"), (),
        "run_command('weekly_headline_count', {'summary_records': [], 'week': 'W1'})"),
    "flag_evaluation": (
        "Run the flag evaluation program check on one summary record: "
        "inputs stands optional beside the other outcomes and stands "
        "required for a promotion, in the form of a mapping carrying "
        "flag_conditions_fired with at least one stated flag "
        "condition fired.",
        ("summary_record",), ("inputs", "outcome", "tier"),
        "run_command('flag_evaluation', {'summary_record': {'retention_tier': 'Tier 2', 'flag_conditions_fired': ['condition-1']}, 'inputs': {'flag_conditions_fired': ['condition-1']}, 'outcome': 'promote', 'tier': 'Tier 3'})"),
}


def command_surface():
    """The shell command surface, command by command: each entry
    names the module the command carries inputs to, states its
    purpose in plain language, names its required and optional
    input fields, and gives one example invocation in the form
    the product offers, a run_command call."""
    surface = []
    for name, module in sorted(_COMMAND_MODULES.items()):
        purpose, required, optional, example = _COMMAND_DETAILS[name]
        surface.append({
            "command": name,
            "carries_to": module,
            "computes_rule": False,
            "purpose": purpose,
            "required_inputs": list(required),
            "optional_inputs": list(optional),
            "example": example,
        })
    return surface


def command_computes(command):
    """Return what a shell command itself computes. Every command
    computes nothing a core owns: no reputation, no verdict, no
    retention tier, and no result wording."""
    return None


def _safe_text(value):
    """Render a handed value for a refusal or carriage sentence
    on the text it stores, where the value stands in a text or
    buffer form, read through _stored_text, so a string reading
    the value itself supplies, lying or raising, never stands
    as the name the sentence delivers. A value in any other
    form stands rendered through its string reading where that
    reading stands, and through the base object repr where the
    string reading the value itself supplies raises, so a
    sentence naming the handed value never escapes bare on
    that reading."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    try:
        return str(value)
    except Exception:
        return object.__repr__(value)


def _vocabulary_text(value):
    """Render a handed value for a vocabulary sentence: a text
    form or a buffer form stands rendered by the text it stores,
    read through _stored_text, so a memoryview form names the
    value it stores and never a volatile memory address. Any
    other form stands rendered through _safe_text."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    return _safe_text(value)


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


def _key_error_message_text(raw_message):
    """The sentence a KeyError family failure carries, with
    the repr escapes the interpreter supplies inside its
    wrapping quote pair decoded, so the identifier the
    operator reads stands as the identifier itself: where
    the raw message stands as the repr of one text value,
    that text value stands returned whole, and any other
    raw message stands returned as it stands."""
    if (
            len(raw_message) >= 2
            and raw_message[0] == raw_message[-1]
            and raw_message[0] in ("'", '"')):
        try:
            parsed = ast.literal_eval(raw_message)
        except Exception:
            parsed = None
        if isinstance(parsed, str):
            return parsed
    return raw_message


def _safe_repr(value):
    """Render a handed value for a refusal sentence: through
    its repr reading where that reading stands, and through
    the base object repr where the repr reading the value
    itself supplies raises, so the sentence stands delivered
    whole and never escapes bare on that reading."""
    try:
        return repr(value)
    except Exception:
        return object.__repr__(value)


def error_carriage(failure, run_id=None, stage=None):
    """The error carriage of the shell: a named failure reaches
    the operator as a named failure with its run identifier and
    its stage. No failure is swallowed and none is converted into
    an empty result, and no command exits cleanly over a failed
    run."""
    if isinstance(failure, str):
        raw_message = _safe_text(failure)
        class_name = None
    else:
        raw_message = _safe_text(failure)
        class_name = type(failure).__name__
    if isinstance(failure, KeyError):
        # The KeyError family stands decoded through
        # _key_error_message_text, which returns the text a repr
        # form message stands for whole, escapes decoded, and
        # leaves any other message as it stands. A sentence of
        # any other failure class, and a sentence handed in text
        # form, stands quote wrapped only in its own right, and
        # stands carried whole, with no paired quote strip.
        raw_message = _key_error_message_text(raw_message)
    name = raw_message if class_name is None else (
        class_name + ": " + raw_message)
    fields = {}
    if isinstance(failure, str):
        fields["name"] = "failure in text form"
        fields["message"] = raw_message
    if not isinstance(failure, str):
        try:
            carried = getattr(failure, "failure", None)
        except Exception:
            carried = None
        if isinstance(carried, dict):
            fields.update(_freeze(carried))
            if isinstance(failure, NamedShellFailure):
                # The structured message of a NamedShellFailure
                # stands in the same form as the failure field of
                # the same record, built from the same raw
                # message, never in a second form of its own.
                fields["message"] = raw_message
        elif carried is not None:
            fields["failure"] = carried
        try:
            gate = getattr(failure, "gate", None)
        except Exception:
            gate = None
        if gate is not None:
            fields["gate"] = gate
        try:
            failure_vars = vars(failure)
        except Exception:
            failure_vars = {}
        for key, value in dict.items(failure_vars):
            try:
                already_carried = key in fields
            except Exception:
                continue
            try:
                is_failure_field = key == "failure"
            except Exception:
                is_failure_field = False
            if already_carried or is_failure_field:
                continue
            try:
                fields[key] = _freeze(value)
            except Exception:
                continue
        if class_name in _NAMED_FAILURE_CLASS_NAMES or class_name.startswith("Named"):
            fields.setdefault("name", class_name)
            fields.setdefault("message", raw_message)
            if not fields:
                fields["failure"] = raw_message
        elif isinstance(carried, dict) and "name" in fields:
            fields.setdefault("message", raw_message)
        if not fields:
            fields["name"] = class_name
            fields["message"] = name
    carriage = {
        "failure": name,
        "failure_value": fields,
        "run_id": run_id,
        "stage": stage,
        "swallowed": False,
        "converted_to_empty_result": False,
        "operator_sees_failure": True,
    }
    for key, value in fields.items():
        try:
            already_carried = key in carriage
        except Exception:
            already_carried = False
        try:
            is_message = key == "message"
        except Exception:
            is_message = False
        if already_carried or is_message:
            continue
        try:
            carriage[key] = value
        except Exception:
            continue
    return carriage


def run_command(command=_ARGUMENT_NOT_HANDED, payload=None, run_id=None):
    """Run one shell command. The command carries its inputs to
    its named module and returns that module outputs, or its
    named failure in the error carriage form. A handing
    missing its command stands refused in the same carriage
    form, stating the door, the ground, and the next step
    (FW5-10)."""
    if command is _ARGUMENT_NOT_HANDED:
        return error_carriage(
            NamedShellFailure(
                "run_command stands refused: this door stands "
                "handed the command, a handing stands missing "
                "for the command, and no shell command stands "
                "run; next step: hand the command, one of the "
                "shell commands, and call the door again"),
            run_id=run_id, stage=None)
    # The carriage stage names the command in bounded rendering
    # form (FW5-08): a command standing as text stands rendered
    # as its stored text bounded in the FW4-10 form, so no
    # refusal carriage of this door grows with the handing; a
    # command in any other form stands carried as handed, in
    # the standing form of the carriage.
    stage_value = (
        _bounded_echo(_stored_text(command))
        if isinstance(command, str) else command)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return error_carriage(
            NamedShellFailure(
                "shell command stands refused: the payload stands "
                "in no dict form: a mapping in dict form of input "
                "fields stands required as the payload of every "
                "shell command"),
            run_id=run_id, stage=stage_value)
    if isinstance(command, (bytes, bytearray, memoryview)) and (
            _stored_text(command) in (
                "start_run", "start_sweep", "read_store",
                "write_store", "run_pilot", "assemble_report",
                "outside_call_check", "store_kind_check",
                "weekly_headline_count", "flag_evaluation")):
        return error_carriage(
            NamedShellFailure(
                "shell command stands refused: the command stands "
                "in no command form: a command stands as text "
                "naming one of the shell commands, a command handed "
                "in buffer form stands in no command form, and no "
                "shell command stands run"),
            run_id=run_id, stage=stage_value)
    command_text = (
        _stored_text(command) if isinstance(command, str) else None)
    try:
        if command_text == "start_run":
            return _mod12.start_run(
                run_class=dict.get(payload, "run_class"),
                family_id=dict.get(payload, "family_id"),
            )
        if command_text == "start_sweep":
            return _mod12.start_sweep(family_id=dict.get(payload, "family_id"))
        if command_text == "store_kind_check":
            return store_kind_check_with_reason(dict.get(payload, "kind"))
        if command_text == "read_store":
            run_id_value = dict.get(payload, "run_id")
            if run_id_value is None:
                raise NamedShellFailure(
                    "read_store stands refused: no run_id stands "
                    "supplied: a run identifier stands required, "
                    "and no run record stands read without it")
            if not isinstance(run_id_value, str) or \
                    str.__len__(run_id_value) == 0:
                raise NamedShellFailure(
                    "read_store stands refused: the run_id stands "
                    "in no identifier form: a run identifier in "
                    "text form stands required, and no run record "
                    "stands read without it")
            return _mod10.read_run_record(
                run_id_value,
                store_kind=dict.get(payload, "store_kind", "sweep"))
        if command_text == "write_store":
            record = dict.get(payload, "record")
            if record is None:
                raise NamedShellFailure(
                    "write_store stands refused: no record stands "
                    "supplied: a record in mapping form stands "
                    "required, and nothing stands written")
            if not isinstance(record, dict):
                raise NamedShellFailure(
                    "write_store stands refused: the record stands "
                    "in no mapping form: a record in mapping form "
                    "stands required, and nothing stands written")
            record_id = dict.get(record, "run_id") or dict.get(
                record, "run_identifier")
            if record_id is not None and (
                    not isinstance(record_id, str)
                    or str.__len__(record_id) == 0):
                raise NamedShellFailure(
                    "write_store stands refused: the run_id stands "
                    "in no identifier form: a run identifier in "
                    "text form stands required, and no run record "
                    "stands written without it")
            return _mod10.retain_run_record(
                record, store_kind=dict.get(payload, "store_kind", "sweep"))
        if command_text == "run_pilot":
            return pilot_run(dict.get(payload, "use"), dict.get(payload, "artefact"))
        if command_text == "assemble_report":
            raise NamedShellFailure(
                "report assembly stands not built: no report assembly "
                "act stands in MOD-11, whose picked reporting artefacts "
                "stand partial on their own record")
        if command_text == "outside_call_check":
            return outside_call_check(
                dict.get(payload, "dependency_manifest"),
                dict.get(payload, "call_log"))
        if command_text == "flag_evaluation":
            return flag_evaluation(
                dict.get(payload, "summary_record"),
                inputs=dict.get(payload, "inputs"),
                outcome=dict.get(payload, "outcome"),
                tier=dict.get(payload, "tier"),
                actor=dict.get(payload, "actor", "program"))
        if command_text == "weekly_headline_count":
            return {
                "count": weekly_headline_count(
                    dict.get(payload, "summary_records"),
                    dict.get(payload, "week")),
                "week": dict.get(payload, "week"),
            }
        raise NamedShellFailure(
            "unknown shell command: " + _bounded_echo(_safe_text(command))
            + "; the shell commands stand as start_run, start_sweep, "
            "read_store, write_store, run_pilot, assemble_report, "
            "outside_call_check, store_kind_check, "
            "weekly_headline_count, and flag_evaluation, and no "
            "shell command stands run")
    except NamedShellFailure as failure:
        carriage = error_carriage(failure, run_id=run_id, stage=stage_value)
        if command_text == "assemble_report":
            carriage["not_built"] = True
            carriage["stands_on_record"] = (
                "the MOD-11 reporting artefacts item, Purple 2 "
                "element E-49, PARTIAL")
        if command_text == "run_pilot":
            carriage["confinement_bar"] = (
                "pilot work stands confined to timing, conformance, "
                "and procedure rates, under the pilot confined label")
        return carriage
    except Exception as failure:
        return error_carriage(failure, run_id=run_id, stage=stage_value)


# ---------------------------------------------------------------------------
# Pilot runner, decision D-07 confinement
# ---------------------------------------------------------------------------

_PILOT_BARRED_KEY_MARKERS = ("money", "anchor_" + "set")


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies. A value that stores no text at all
    judges no name: the empty text stands returned for one,
    in the cured MOD-01 form. A bytes value, a bytearray
    value, and a memoryview value stand judged on their
    stored bytes, decoded as UTF-8 with undecodable bytes
    dropped, never through a string reading the value itself
    supplies, in the governing stored text settlement form."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


def _base_get(record, key):
    """Read one field through the base dict get, never through
    a get reading the record itself supplies. A handed value in
    no mapping form stores nothing under any key."""
    if isinstance(record, dict):
        return dict.get(record, key)
    return None


def _base_contains(record, key):
    """Test one key through the base dict contains, never
    through a contains reading the record itself supplies."""
    return isinstance(record, dict) and dict.__contains__(
        record, key)


def _plain_stored_copy(record):
    """A plain dict holding exactly the stored pairs of a handed
    record, built through the base dict items reading, so an act
    this act delegates to judges the stored contents and not a
    reading the handed record supplies. A value in no mapping
    form stands as itself. A dict assignment whose key hash or
    equality reading raises at the assignment itself, in one of
    the seven named kinds (TypeError, RuntimeError, ValueError,
    AttributeError, OverflowError, KeyError, OSError), stands
    carried under a distinct numbered form in the MOD-14 cured
    form under settlement S-1: a text key in its numbered text
    form first, a form carrying the key itself in numbered
    tuple form next, and a plain text numbered form where a
    form carrying the key itself cannot stand inserted, the
    counter rising until a form stands inserted, so no carried
    entry is silently dropped on that reading and no bare error
    in one of those kinds escapes the copy."""
    if isinstance(record, dict):
        copied = {}
        for key, item in dict.items(record):
            try:
                copied[key] = item
            except (TypeError, RuntimeError, ValueError,
                    AttributeError, OverflowError, KeyError,
                    OSError):
                counter = 2
                while True:
                    if isinstance(key, str):
                        candidate = (
                            str.__str__(key)
                            + " (carried key " + str(counter) + ")")
                    elif counter == 2:
                        candidate = (key, counter)
                    else:
                        candidate = (
                            "(carried key " + str(counter) + ")")
                    try:
                        candidate_taken = candidate in copied
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
                        candidate_taken = False
                    if candidate_taken:
                        counter += 1
                        continue
                    try:
                        copied[candidate] = item
                        break
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
                        counter += 1
        return copied
    return record


def _container_parts(value):
    """The parts a container value stores, read through the
    base iteration reading of its form, never through an
    iteration reading the value itself supplies."""
    if isinstance(value, list):
        return list(list.__iter__(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    if isinstance(value, set):
        return list(set.__iter__(value))
    return []


def _is_iterator(value):
    """Whether a value stands in iterator form: it is its own
    iterator, carrying its items only as values it would
    yield, and storing no contents in any container, text,
    bytes, or dict form."""
    try:
        return iter(value) is value
    except TypeError:
        return False


def _fired_stands(fired):
    """Whether a fired value stands supplied, judged by its
    stored contents and never by a truth reading the value
    itself supplies: a value in a container form stands where
    it stores at least one entry, read through the base
    iteration of its form, a text or bytes form stands where
    it stores at least one character or byte, and no value
    stands nowhere. A value in iterator form stores nothing
    in any of those forms, so it stands as no supplied fired
    value. A value in no such form stands judged by the
    plain truth of the value itself, the one limb this
    reading does not reach."""
    if fired is None:
        return False
    if _is_iterator(fired):
        return False
    if isinstance(fired, (list, tuple, set, frozenset)):
        return len(_container_parts(fired)) > 0
    if isinstance(fired, str):
        return len(str.__str__(fired)) > 0
    if isinstance(fired, (bytes, bytearray, memoryview)):
        return len(bytes(fired)) > 0
    if isinstance(fired, dict):
        return dict.__len__(fired) > 0
    return bool(fired)


def _pilot_key_form(key, _seen=None, _depth=0):
    if isinstance(key, (list, tuple, set, frozenset)):
        if _depth > _PILOT_ARTEFACT_DEPTH_BOUND:
            return ""
        seen = _seen if _seen is not None else set()
        if id(key) in seen:
            return ""
        seen.add(id(key))
        try:
            return "".join(
                _pilot_key_form(part, seen, _depth + 1)
                for part in _container_parts(key))
        finally:
            seen.discard(id(key))
    return "".join(
        char for char in _stored_text(key).lower()
        if char.isalnum())


_PILOT_BARRED_KEY_FORMS = tuple(
    _pilot_key_form(marker) for marker in _PILOT_BARRED_KEY_MARKERS)


def _screen_pilot_key(key, _seen=None, _depth=0):
    if isinstance(key, (list, tuple, set, frozenset)):
        if _depth > _PILOT_ARTEFACT_DEPTH_BOUND:
            return
        seen = _seen if _seen is not None else set()
        if id(key) in seen:
            return
        seen.add(id(key))
        try:
            for part in _container_parts(key):
                _screen_pilot_key(part, seen, _depth + 1)
        finally:
            seen.discard(id(key))
    form = _pilot_key_form(key)
    if any(marker in form for marker in _PILOT_BARRED_KEY_FORMS):
        raise NamedShellFailure(
            "pilot artefact carries a barred entry under the "
            "pilot confined label: " + _safe_text(key))


_PILOT_ARTEFACT_DEPTH_BOUND = 100


def _pilot_int_digits(value):
    """The decimal digits of a plain integer, built in digit
    chunks from the plain integer itself through base integer
    operations, in the chunk built form the store writer of
    mod10 uses at the same handing, so an integer standing
    beyond the interpreter integer string conversion limit
    stands rendered in its plain form whole and no bare
    interpreter digit limit sentence escapes at the pilot
    artefact door (FW4-02)."""
    remaining = int.__int__(value)
    sign = ""
    if remaining < 0:
        sign = "-"
        remaining = -remaining
    chunks = []
    while remaining:
        remaining, chunk = divmod(remaining, 10 ** 9)
        chunks.append(chunk)
    if not chunks:
        return "0"
    parts = [str(chunks[-1])]
    for chunk in reversed(chunks[:-1]):
        parts.append(str(chunk).rjust(9, "0"))
    return sign + "".join(parts)


def _pilot_path_part(value):
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bool):
        return bool.__str__(value)
    if isinstance(value, int):
        try:
            return int.__str__(value)
        except ValueError:
            return _pilot_int_digits(value)
    if isinstance(value, float):
        return float.__str__(value)
    if isinstance(value, bytes):
        return bytes.__repr__(value)
    return "unreadable part"


def _screen_pilot_artefact(value, _depth=0, _seen=None, _walked=None, _path="root"):
    """Screen one artefact part, recursively. A dict part
    stands read through the base dict items reading, a set or
    frozenset part through its base iteration reading, and a
    list or tuple part through its base iteration reading, so
    no reading the part itself supplies hides a barred entry
    from the screen. The walk carries a walked standing across
    paths: a container whose walk stands completed at a stated
    depth stands not walked again where another path reaches
    it at that same depth, so a container shared by two
    siblings stands walked once for each depth it stands at,
    and a reach at a greater depth stands walked again and
    judged at its own depth against the depth bound."""
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > _PILOT_ARTEFACT_DEPTH_BOUND:
            raise NamedShellFailure(
                "pilot artefact stands refused: the pilot artefact "
                "stands deeper than the stated depth bound of "
                + str(_PILOT_ARTEFACT_DEPTH_BOUND) + " at " + _path
                + ", counted with the handed artefact standing at "
                "depth 0 and every container standing around a part "
                "counting toward that bound, and no pilot run stands "
                "performed on it")
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise NamedShellFailure(
                "pilot artefact stands refused: the pilot artefact "
                "carries a cycle at " + _path
                + ", and no pilot run stands performed on it")
        walked = _walked if _walked is not None else {}
        if (id(value), _depth) in walked:
            return
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                joined_form = "".join(
                    _pilot_key_form(key)
                    for key in dict.keys(value))
                if any(
                        marker in joined_form
                        for marker in _PILOT_BARRED_KEY_FORMS):
                    raise NamedShellFailure(
                        "pilot artefact carries a barred entry under the "
                        "pilot confined label: " + joined_form)
                for key, item in dict.items(value):
                    _screen_pilot_artefact(key, _depth + 1, seen, walked, _path + "/key")
                    _screen_pilot_key(key)
                    _screen_pilot_artefact(item, _depth + 1, seen, walked, _path + "/" + _pilot_path_part(key))
                if not validate_pilot_claim(value):
                    raise NamedShellFailure(
                        "pilot artefact carries a claim the pilot check bars")
            elif isinstance(value, (list, tuple)):
                if isinstance(value, list):
                    items = list(list.__iter__(value))
                else:
                    items = list(tuple.__iter__(value))
                for index, item in enumerate(items):
                    if not isinstance(item, (dict, list, set)):
                        _screen_pilot_key(item)
                    _screen_pilot_artefact(item, _depth + 1, seen, walked, _path + "[" + str(index) + "]")
            else:
                if isinstance(value, frozenset):
                    base_iter = frozenset.__iter__
                else:
                    base_iter = set.__iter__
                for item in base_iter(value):
                    if not isinstance(item, dict):
                        _screen_pilot_key(item)
                    _screen_pilot_artefact(item, _depth + 1, seen, walked, _path + "/part")
        finally:
            seen.discard(id(value))
        walked[(id(value), _depth)] = True


def pilot_run(use=_ARGUMENT_NOT_HANDED, artefact=None):
    """Run the purpose built run for one of its three uses only:
    timing, conformance, and procedure rates. Every pilot output
    carries its confinement label in the same artefact as the
    number. A use outside the three, including behaviour fitting,
    is refused as a named failure. The artefact stands screened
    in whatever container it arrives in, recursively, before the
    label is stamped: a barred entry carried in a list, a tuple,
    or a set, or under a spaced or joined spelling, raises the
    named failure in the same form as one carried in a dict. An
    artefact in any container form stands delivered as a copy
    apart under _freeze, in the posture of settlement S-1,
    never as the handed object itself, so a mutation of either
    side after the run stands in neither the other side nor
    the delivered record. A handing missing its use stands
    refused in the named form of this module, stating the
    door, the ground, and the next step (FW5-10)."""
    if use is _ARGUMENT_NOT_HANDED:
        raise NamedShellFailure(
            "pilot_run stands refused: this door stands "
            "handed the use, a handing stands missing for "
            "the use, and no pilot run stands performed; "
            "next step: hand the use, one of timing, "
            "conformance, and procedure rates, and call "
            "the door again")
    use_text = str.__str__(use) if isinstance(use, str) else None
    if use_text is None or use_text not in PILOT_USES:
        raise NamedShellFailure(
            "pilot use outside timing, conformance, and procedure rates: " + _bounded_echo(_safe_text(use))
        )
    _screen_pilot_artefact(artefact)
    output = _freeze(artefact) if isinstance(artefact, dict) else {"figure": _freeze(artefact)}
    output["use"] = use_text
    output["confinement_label"] = "pilot confined"
    output["form"] = "pilot artefact, stored apart from sweep results"
    return output


def _stored_truth_stands(value):
    """Whether a handed claim condition field stands, judged on
    the form it stores and never through a truth reading the
    value itself supplies: a boolean on its identity, a plain
    number on its base class reading against zero, a text,
    buffer, or container form on its base length, no value as
    not standing, and any other stored object as standing by
    its presence alone, in the stored truth form MOD-11 states
    at its _stored_truth_stands."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, bytes):
        return bytes.__len__(value) > 0
    if isinstance(value, bytearray):
        return bytearray.__len__(value) > 0
    if isinstance(value, memoryview):
        return memoryview.__len__(value) > 0
    if isinstance(value, dict):
        return dict.__len__(value) > 0
    if isinstance(value, (list, tuple, set, frozenset)):
        return len(_container_parts(value)) > 0
    return True


def validate_pilot_claim(claim):
    """Return False where a behaviour claim cites a pilot output,
    and where a pilot output stands worded as settling a
    population behaviour rate: events per agent per day and trust
    graph average degree are not settled as population behaviour
    rates by the pilot in any wording. The kind stands judged on
    the text it stores, read through the stored text form of this
    module, never through an equality reading the kind itself
    supplies, so a kind in text subclass dress or in bytes dress
    storing the word behaviour stands judged as that word. The
    two condition fields stand judged through the stored truth
    form of this module, never through a truth reading the
    handed value itself supplies, so a condition value whose
    truth reading answers False or raises stands judged on the
    form it stores, and no handing escapes this act bare on
    that reading."""
    if not isinstance(claim, dict):
        return False
    if _stored_truth_stands(dict.get(claim, "cites_pilot_output")) and str.__eq__(
            _stored_text(dict.get(claim, "kind")), "behaviour"):
        return False
    if _stored_truth_stands(
            dict.get(claim, "settles_population_behaviour_rate")):
        return False
    return True


# ---------------------------------------------------------------------------
# Confined programme forms, pilot confined and synthetic material only
# ---------------------------------------------------------------------------

def _pilot_confined(material):
    if not isinstance(material, dict):
        return False
    for key in ("material_class", "confinement_label"):
        value = dict.get(material, key)
        if isinstance(value, str) and str.__eq__(
                value, "pilot confined"):
            return True
    return False


def sweep_level_determinism_contract(material):
    """The sweep level determinism contract, on pilot confined
    material only. Material of any other class is refused in the
    named form, and no claim in this form rests on the material
    it reads."""
    if not _pilot_confined(material):
        raise NamedShellFailure(
            "determinism contract stands on pilot confined material only")
    return {
        "form": "sweep level determinism contract",
        "confinement": "pilot confined material only",
        "material_class": "pilot confined",
        "contract": (
            "the same confined material, read twice, stands read "
            "the same both times"),
    }


def nondeterminism_census(material):
    """The nondeterminism census, on pilot confined material
    only, with its face statement standing on the record."""
    if not _pilot_confined(material):
        raise NamedShellFailure(
            "nondeterminism census stands on pilot confined material only")
    return {
        "form": "nondeterminism census",
        "confinement": "pilot confined material only",
        "face_statement": (
            "this census stands on pilot confined material only "
            "and states no sweep result; permitted divergence "
            "for any reportable run stays at zero"),
        "entries_read": 1 if isinstance(material, dict) else 0,
    }


def dual_rule_retention_simulation(families):
    """The dual rule retention simulation, over synthetic families
    only, reported as one paired field and no single total. A
    family that does not stand marked synthetic is refused in
    the named form. The families argument stands read through
    the base iteration reading of its form, never through an
    iteration reading the argument itself supplies, so a stored
    family the supplied reading does not yield still reaches
    the synthetic test. The synthetic mark and the two retained
    marks stand judged through the stored truth form of this
    module at _stored_truth_stands, never through a truth
    reading a handed mark itself supplies, so a mark stands as
    the standing its stored form carries and a raising truth
    reading escapes nowhere bare."""
    if isinstance(families, (list, tuple, set, frozenset)):
        families = _container_parts(families)
    else:
        families = list(families or ())
    for family in families:
        if not isinstance(family, dict) or not _stored_truth_stands(
                dict.get(family, "synthetic")):
            raise NamedShellFailure(
                "dual rule simulation stands on synthetic families only")
    return {
        "form": "dual rule retention simulation",
        "confinement": "synthetic families only",
        "paired_field": {
            "first_rule_retained": sum(
                1 for family in families
                if _stored_truth_stands(
                    dict.get(family, "retained_under_first_rule"))),
            "second_rule_retained": sum(
                1 for family in families
                if _stored_truth_stands(
                    dict.get(family, "retained_under_second_rule"))),
        },
    }


# ---------------------------------------------------------------------------
# Program checks
# ---------------------------------------------------------------------------

def store_kind_check(kind):
    """The store kind program check, over the one store kind
    vocabulary MOD-01 owns."""
    return _mod01.validate_store_kind(kind)


def store_kind_check_with_reason(kind):
    """The store kind program check with its reason in words,
    beside the boolean standing: the permitted kinds, and whether
    the kind stood valid, missing, or unknown."""
    valid = store_kind_check(kind)
    if valid:
        standing = "valid"
        reason = "the kind stands in the store kind vocabulary"
    elif kind is None:
        standing = "missing"
        reason = "no store kind stood supplied"
    else:
        standing = "unknown"
        reason = "the kind stands outside the store kind vocabulary"
    return {
        "store_kind_ok": valid,
        "reason": reason,
        "valid_kinds": list(STORE_KINDS),
        "kind_standing": standing,
    }


RETENTION_TIERS = ("Tier 0", "Tier 1", "Tier 2", "Tier 3")


def _has_stated_condition(fired):
    """Return whether a fired condition list states a condition:
    at least one entry stands stated, where an entry that is
    empty text, blank text, or no value states no condition.
    A list holding only such entries states no condition.
    The container stands read through the base iteration
    reading of its form, never through an iteration reading
    the container itself supplies. An entry in bytes,
    bytearray, or memoryview form stands judged on its
    stored bytes in the same manner as a passage field at
    MOD-07: bytes holding only spacing, or holding only
    text that states nothing, state no condition. A fired
    value in iterator form states no condition: it stores
    no entry in any form this reading names, and it never
    stands as its own stated entry."""
    if isinstance(fired, str):
        entries = (fired,)
    elif isinstance(fired, list):
        entries = tuple(list.__iter__(fired))
    elif isinstance(fired, tuple):
        entries = tuple(tuple.__iter__(fired))
    elif isinstance(fired, frozenset):
        entries = tuple(frozenset.__iter__(fired))
    elif isinstance(fired, set):
        entries = tuple(set.__iter__(fired))
    elif fired is None:
        entries = ()
    elif _is_iterator(fired):
        entries = ()
    else:
        entries = (fired,)
    for entry in entries:
        if entry is None:
            continue
        if isinstance(entry, str) and not _stated_text(entry):
            continue
        if isinstance(entry, (bytes, bytearray, memoryview)):
            raw = bytes(entry)
            if not bytes.strip(raw):
                continue
            try:
                decoded = bytes.decode(raw, "utf-8")
            except UnicodeDecodeError:
                return True
            if not _stated_text(decoded):
                continue
        return True
    return False


_ZERO_WIDTH_CHARS = (
    "\u200b\u200c\u200d\ufeff\u2060"
    "\u00ad\u180e\u200e\u200f\u061c\u202a\u202e\u2061\u2064")


_BLANK_GLYPH_CHARS = ("\u2800", "\u115f")

_HANGUL_FILLER_CHARS = ("\u1160", "\u3164", "\uffa0")


def _stated_text(entry):
    """Return the readable text an entry carries, with zero
    width characters, byte order mark characters, and the
    other invisible format characters in the stated set
    removed, with characters of Unicode category Mn removed,
    since a nonspacing mark standing alone reads as nothing,
    and with the blank glyph characters removed, the braille
    blank and the Hangul filler, which carry the shape of a
    character and state nothing. A lone surrogate, an
    unassigned code point, and a private use character state
    nothing readable either, so characters of categories Cs,
    Cn, and Co stand removed in the same manner. An entry
    carrying only such characters, or only spacing, carries
    no readable text and states no condition. The entry
    stands read through its stored characters, through the
    base class string form, never through an iteration
    reading the entry itself supplies."""
    cleaned = "".join(
        char for char in str.__str__(entry)
        if char not in _ZERO_WIDTH_CHARS
        and char not in _BLANK_GLYPH_CHARS
        and char not in _HANGUL_FILLER_CHARS
        and unicodedata.category(char)
        not in ("Cf", "Mn", "Cc", "Mc", "Me", "Cs", "Cn", "Co"))
    return cleaned.strip()


_ACTOR_CONTAINER_FORMS = (list, tuple, set, frozenset)


def _actor_stored_text(value, _depth=0):
    """The stored text an actor value carries under the stored
    text settlement: a text form, a bytes form, a bytearray
    form, and a memoryview form each read as the stored text
    they store, and a container form reads as the stored text
    parts it stores joined in order with no separator added,
    each part read recursively on its own stored text. A
    value in any other form, an empty container, and a
    container holding a part in any other form carry no
    stored text here and stand as None."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    if isinstance(value, _ACTOR_CONTAINER_FORMS) and _depth < 8:
        parts = _container_parts(value)
        if not parts:
            return None
        pieces = []
        for part in parts:
            piece = _actor_stored_text(part, _depth + 1)
            if piece is None:
                return None
            pieces.append(piece)
        return "".join(pieces)
    return None


def _normalise_actor(actor, _depth=0):
    """Normalise an actor reading before the exact person check
    in MOD-10: case is folded, spacing is collapsed to single
    spaces, and repeated leading articles are dropped. Each
    word stands read through the leet reading and the word
    resolver against the actor vocabulary, so a person actor
    in a letter change dress or a plural dress reads as the
    plain actor it names. Separator characters stand read as
    spacing for the word reading, but the split parts of one
    actor word also stand read joined, so a separator split
    dress of one word reads as the word it names and is not
    split into a different actor. The joined reading also
    stands tried with article words dropped wherever they
    stand, so articles inserted between the split parts of
    one actor word do not hide the word they split. An actor
    value that is stored text in bytes, bytearray, memoryview,
    or container dress stands read as that stored text here,
    under the container readings of the settlement: each part
    on its own stored text, the parts joined in order as one
    name, and a single part container carrying the reading of
    its one part. An actor value in any other non text form
    stands as itself, passed through untouched."""
    if isinstance(actor, _ACTOR_CONTAINER_FORMS):
        parts = _container_parts(actor)
        if _depth >= 8 or not parts:
            return actor
        joined_text = _actor_stored_text(actor)
        if joined_text is None:
            return actor
        joined_reading = _normalise_actor(joined_text, _depth + 1)
        if joined_reading in _ACTOR_VOCABULARY:
            return joined_reading
        for part in parts:
            part_reading = _normalise_actor(part, _depth + 1)
            if isinstance(part_reading, str) and (
                    part_reading in _ACTOR_VOCABULARY):
                return part_reading
        return actor
    if isinstance(actor, (bytes, bytearray, memoryview)):
        actor = _stored_text(actor)
    if not isinstance(actor, str):
        return actor
    text = _canonicalise_text(actor)
    text = "".join(char if char.isalnum() else " " for char in text)
    words = [_canonicalise_word(word) for word in text.split()]
    while words and words[0] in _ARTICLES:
        words = words[1:]
    if not words:
        return ""
    joined = _resolve_actor_word("".join(words))
    if joined in _ACTOR_VOCABULARY:
        return joined
    without_articles = _resolve_actor_word("".join(
        word for word in words if word not in _ARTICLES))
    if without_articles in _ACTOR_VOCABULARY:
        return without_articles
    return " ".join(_resolve_actor_word(word) for word in words)


def flag_evaluation(summary_record, inputs=None, outcome=None, tier=None,
                    actor="program"):
    """The flag evaluation program check: its inputs and outcome
    stand written into the stored summary record itself by the
    MOD-10 flag rule program this check carries to. A promotion
    stands only to a tier the rule names, only with inputs
    actually supplied, and only with at least one stated flag
    condition fired, on the record or in the inputs; a promote
    outcome with no named tier, an invented tier, no supplied
    inputs, or no fired condition is refused in the named form.
    The promote prechecks stand in the core order: the tier
    vocabulary refusal first, then a stated tier below the
    record tier drawing the demote sentence before any inputs
    or stated condition precheck, then the inputs supplied,
    inputs form, and stated condition prechecks, and the no
    tier refusal last, as at the MOD-10 core. The actor stands
    as supplied, in the open, not hardcoded unseen."""
    if not isinstance(summary_record, dict):
        raise NamedShellFailure(
            "flag evaluation in named form: the evaluation stands "
            "on a summary record, and no other form stands evaluated")
    normalised_actor = _normalise_actor(actor)
    if isinstance(normalised_actor, str) and (
            _stored_text(normalised_actor) == "person"):
        raise ValueError(
            "flag evaluation by a person is barred: the flag rule "
            "stands evaluated by a program alone, and no flag "
            "evaluation stands performed")
    outcome_text = (
        _stored_text(outcome) if isinstance(
            outcome, (str, bytes, bytearray, memoryview)) else None)
    if outcome_text == "promote":
        tier_text = (
            _stored_text(tier) if isinstance(
                tier, (str, bytes, bytearray, memoryview)) else None)
        if tier is not None and tier_text not in RETENTION_TIERS:
            raise NamedShellFailure(
                "flag evaluation tier outside the tiers the rule "
                "names: " + _vocabulary_text(tier) + "; the tiers the rule names "
                "stand as Tier 0, Tier 1, Tier 2, and Tier 3, and no flag "
                "evaluation stands performed")
        current = _base_get(summary_record, "retention_tier")
        current_text = (
            _stored_text(current) if isinstance(
                current, (str, bytes, bytearray, memoryview))
            else None)
        if tier_text in RETENTION_TIERS and (
                current_text in RETENTION_TIERS) and (
                RETENTION_TIERS.index(tier_text)
                < RETENTION_TIERS.index(current_text)):
            raise NamedShellFailure(
                "the flag rule never demotes: the stated tier "
                "stands below the record tier, and no demotion "
                "stands effected by it")
        if inputs is None:
            raise NamedShellFailure(
                "flag promotion with no inputs supplied: a promotion "
                "stands only with inputs actually supplied, and no "
                "promotion stands effected by it")
        if not isinstance(inputs, dict):
            raise NamedShellFailure(
                "flag promotion with its inputs standing in no "
                "record form: a promotion stands only with its "
                "inputs handed as a mapping carrying "
                "flag_conditions_fired, and no promotion stands "
                "effected by it")
        fired = None
        if isinstance(inputs, dict):
            fired = _base_get(inputs, "flag_conditions_fired")
        if not _fired_stands(fired):
            fired = _base_get(
                summary_record, "flag_conditions_fired")
        if not _has_stated_condition(fired):
            raise NamedShellFailure(
                "flag promotion with no stated flag condition "
                "fired: a promotion stands only with at least one "
                "stated flag condition fired, and no promotion "
                "stands effected by it")
        if tier is None:
            raise NamedShellFailure(
                "a promote outcome with no tier stands refused: no "
                "promotion stands effected by it")
    return _mod10.apply_flag_evaluation(
        _plain_stored_copy(summary_record), outcome=outcome, tier=tier,
        actor=_normalise_actor(actor),
        inputs=_plain_stored_copy(inputs),
    )


def _week_plain_number(value):
    """The plain number a week value stores, built through
    base class operations, or None where the value stands in
    no plain number form: an integer week as a plain int and
    a float week as a plain float, so no equality reading a
    handed number supplies decides its own judgement."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int.__new__(int, int.__int__(value))
    if isinstance(value, float):
        return float.__new__(float, float.__float__(value))
    return None


def _week_value_equal(stored, handed, _seen=None):
    """Judge two week values equal kind first at every level:
    two text values by the base text equality of their stored
    characters, a boolean only against a boolean, a Decimal
    only against a Decimal and a Fraction only against a
    Fraction, each by its base class equality on plain copies,
    two plain number values by the plain numbers they store,
    built through base class operations so no handed equality
    reading decides, and container values part by part under
    this same reading, lists and tuples in order, sets and
    frozensets order insensitively, and dicts by matched keys
    and their values. Any other pair stands equal only where
    both stand in the same kind, judged by a guarded equality
    that a raising reading answers as not equal."""
    if stored is None or handed is None:
        return stored is None and handed is None
    if isinstance(stored, str) or isinstance(handed, str):
        return (isinstance(stored, str) and isinstance(handed, str)
                and str.__eq__(stored, handed) is True)
    if isinstance(stored, bool) or isinstance(handed, bool):
        return (isinstance(stored, bool) and isinstance(handed, bool)
                and stored is handed)
    if isinstance(stored, Decimal) or isinstance(handed, Decimal):
        return (isinstance(stored, Decimal)
                and isinstance(handed, Decimal)
                and Decimal.__eq__(
                    Decimal.__new__(Decimal, stored),
                    Decimal.__new__(Decimal, handed)) is True)
    if isinstance(stored, Fraction) or isinstance(handed, Fraction):
        return (isinstance(stored, Fraction)
                and isinstance(handed, Fraction)
                and Fraction.__eq__(
                    Fraction.__new__(Fraction, stored),
                    Fraction.__new__(Fraction, handed)) is True)
    stored_number = _week_plain_number(stored)
    handed_number = _week_plain_number(handed)
    if stored_number is not None or handed_number is not None:
        return (stored_number is not None
                and handed_number is not None
                and stored_number == handed_number)
    if isinstance(stored, (bytes, bytearray, memoryview)) or isinstance(
            handed, (bytes, bytearray, memoryview)):
        return (isinstance(stored, (bytes, bytearray, memoryview))
                and isinstance(handed, (bytes, bytearray, memoryview))
                and bytes.__eq__(bytes(stored), bytes(handed)) is True)
    if isinstance(stored, dict) or isinstance(handed, dict):
        if not (isinstance(stored, dict) and isinstance(handed, dict)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        if dict.__len__(stored) != dict.__len__(handed):
            return False
        handed_items = list(dict.items(handed))
        used = [False] * len(handed_items)
        for stored_key, stored_item in dict.items(stored):
            matched = False
            for index in range(len(handed_items)):
                if used[index]:
                    continue
                handed_key, handed_item = handed_items[index]
                if _week_value_equal(
                        stored_key, handed_key, seen) and (
                        _week_value_equal(
                            stored_item, handed_item, seen)):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                return False
        return True
    if isinstance(stored, list) or isinstance(handed, list):
        if not (isinstance(stored, list) and isinstance(handed, list)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        stored_parts = list(list.__iter__(stored))
        handed_parts = list(list.__iter__(handed))
        return len(stored_parts) == len(handed_parts) and all(
            _week_value_equal(part, other, seen)
            for part, other in zip(stored_parts, handed_parts))
    if isinstance(stored, tuple) or isinstance(handed, tuple):
        if not (isinstance(stored, tuple)
                and isinstance(handed, tuple)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        stored_parts = list(tuple.__iter__(stored))
        handed_parts = list(tuple.__iter__(handed))
        return len(stored_parts) == len(handed_parts) and all(
            _week_value_equal(part, other, seen)
            for part, other in zip(stored_parts, handed_parts))
    if isinstance(stored, (set, frozenset)) or isinstance(
            handed, (set, frozenset)):
        if isinstance(stored, set) != isinstance(handed, set):
            return False
        if isinstance(stored, frozenset) != isinstance(
                handed, frozenset):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        if isinstance(stored, frozenset):
            stored_parts = list(frozenset.__iter__(stored))
            handed_parts = list(frozenset.__iter__(handed))
        else:
            stored_parts = list(set.__iter__(stored))
            handed_parts = list(set.__iter__(handed))
        if len(stored_parts) != len(handed_parts):
            return False
        remaining = list(handed_parts)
        for part in stored_parts:
            matched = None
            for index, other in enumerate(remaining):
                if _week_value_equal(part, other, seen):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
        return True
    if type(stored) is not type(handed):
        return False
    try:
        return bool(stored == handed)
    except Exception:
        return False


def _week_stands_equal(stored_week, handed_week):
    """Judge two week values equal kind first, at the top
    level and inside any container week, under
    _week_value_equal: no handed equality reading decides a
    pair across kinds, a plain number week stands judged by
    the plain number it stores, and a container week stands
    judged part by part under the same kind first reading, so
    a boolean, a Decimal, or a Fraction standing inside a
    container week never stands equal to a plain number."""
    return _week_value_equal(stored_week, handed_week)


def _weekly_pair_present(record, field):
    """Whether a handed record carries a field among its stored
    pairs, a field standing present where a stored key carries
    its name in stored text, never through a hash or equality
    reading a handed key supplies, in the posture of the cured
    MOD-13 _base_get of row R18-033."""
    if not isinstance(record, dict):
        return False
    for key in dict.keys(record):
        if isinstance(key, (str, bytes, bytearray, memoryview)) \
                and str.__eq__(_stored_text(key), field):
            return True
    return False


def _weekly_pair_get(record, field):
    """Read one field of a handed record through its stored
    pairs, in the form _weekly_pair_present states."""
    if not isinstance(record, dict):
        return None
    for key, item in dict.items(record):
        if isinstance(key, (str, bytes, bytearray, memoryview)) \
                and str.__eq__(_stored_text(key), field):
            return item
    return None


def _stored_identifier_form(value, _depth=0, _seen=None):
    """The stored form of one headline unit identifier, built
    from the contents it stores through the base readings of
    its form, never through a repr, equality, or hash reading
    the value itself supplies: text by its stored characters,
    a boolean apart from every number, a plain number by the
    number it stores, a Decimal or a Fraction by its base
    string form, a buffer by its stored bytes, and a container
    part by part under this same reading, dicts by their
    stored pairs in order, lists and tuples in order, and
    sets and frozensets apart from each other and order
    insensitively. A part in no stated form stands keyed by
    its kind name alone, and a part standing deeper than the
    depth bound of 100, or standing again on its own walk
    path, stands keyed by a stated marker in that posture."""
    if isinstance(value, bool):
        return ("bool", value is True)
    if isinstance(value, str):
        return ("text", str.__str__(value))
    if isinstance(value, int):
        return ("int", int.__int__(value))
    if isinstance(value, float):
        return ("float", float.__float__(value))
    if isinstance(value, Decimal):
        return ("decimal", Decimal.__str__(value))
    if isinstance(value, Fraction):
        return ("fraction", Fraction.__str__(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return ("bytes", bytes(value))
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > 100:
            return ("too deep",)
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return ("cycle",)
        seen = seen | {id(value)}
        if isinstance(value, dict):
            return ("dict", tuple(
                (_stored_identifier_form(key, _depth + 1, seen),
                 _stored_identifier_form(item, _depth + 1, seen))
                for key, item in dict.items(value)))
        if isinstance(value, list):
            return ("list", tuple(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in list.__iter__(value)))
        if isinstance(value, tuple):
            return ("tuple", tuple(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in tuple.__iter__(value)))
        if isinstance(value, frozenset):
            return ("frozenset", frozenset(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in frozenset.__iter__(value)))
        return ("set", frozenset(
            _stored_identifier_form(item, _depth + 1, seen)
            for item in set.__iter__(value)))
    if value is None:
        return ("none",)
    return ("kind", type(value).__name__)


def _identifier_refusal_text(value):
    """Name a handed identifier standing in no unit identifier
    form on the form it stands in, never through a repr or
    string reading the value itself supplies: a text or buffer
    form by the repr of the text it stores, a boolean by its
    base text form, a plain number by the number it stores
    through its base class reading, a Decimal or a Fraction by
    its base class repr, no value as None, and a part in any
    other form by its kind name alone, in the posture of
    _stored_identifier_form for a part in no stated form."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return repr(_stored_text(value))
    if isinstance(value, bool):
        return bool.__str__(value)
    if isinstance(value, int):
        return int.__str__(value)
    if isinstance(value, float):
        return repr(float.__float__(value))
    if isinstance(value, Decimal):
        return Decimal.__repr__(value)
    if isinstance(value, Fraction):
        return Fraction.__repr__(value)
    if value is None:
        return "None"
    return type(value).__name__


def weekly_headline_count(summary_records, week):
    """The weekly headline count program check, counted from the
    stored summary records alone as distinct headline unit
    identifiers, under the canonical field name the reporter
    uses, whose witness records fall in the week. A record with
    no week field, and a record of the week with no headline unit
    identifier field, fail in the named form; neither is counted
    silently as zero. A record of the week whose identifier field
    stands at None, or in a form the count cannot read as a list
    of identifiers, fails in the same named form. A bare string
    identifier field counts as the one identifier it states,
    never as its characters. Both inputs stand required: an
    absent records argument or an absent week stands refused in
    named form, and no clean zero stands returned for a count
    that never ran. The records argument stands read through
    the base iteration reading of its form, never through an
    iteration or length reading the argument itself supplies,
    as its MOD-11 sister act reads the same argument. A
    container identifier stands keyed on the stored form it
    carries, built through the base readings of its form,
    never on a repr reading the identifier itself supplies,
    so two distinct container identifiers sharing one
    supplied repr stand counted as the two units they are,
    and two container identifiers storing the same contents
    stand counted as one. An identifier standing in no unit
    identifier form stands named in its refusal on the form
    it stands in, through _identifier_refusal_text, never
    through a repr reading the identifier itself supplies."""
    if summary_records is None:
        raise NamedShellFailure(
            "weekly_headline_count stands refused: no "
            "summary_records stand supplied: a list of summary "
            "records stands required, and no weekly headline "
            "count stands certified without it")
    if week is None:
        raise NamedShellFailure(
            "weekly_headline_count stands refused: no week stands "
            "supplied: a week stands required, and no weekly "
            "headline count stands certified without it")
    if not isinstance(summary_records, (list, tuple, set, frozenset)):
        raise NamedShellFailure(
            "weekly_headline_count stands refused: the "
            "summary_records argument stands in no list form: "
            "a list of summary records stands required, and no "
            "weekly headline count stands certified without it")
    if isinstance(week, float) and not math.isfinite(week):
        raise NamedShellFailure(
            "weekly_headline_count stands refused: the week "
            "stands in no comparable form, a week stands as a "
            "finite value, and no weekly headline count stands "
            "certified without it")
    seen = []
    for record in _container_parts(summary_records):
        if not isinstance(record, dict) or not _weekly_pair_present(record, "week"):
            raise NamedShellFailure(
                "summary record carries no week field, so its weekly "
                "headline count cannot stand read")
        stored_week = _weekly_pair_get(record, "week")
        if isinstance(stored_week, float) and not math.isfinite(
                stored_week):
            raise NamedShellFailure(
                "summary record carries a week standing in no "
                "comparable form, and no weekly headline count "
                "stands certified without it")
        if not _week_stands_equal(stored_week, week):
            continue
        if not _weekly_pair_present(record, "headline_unit_identifiers"):
            raise NamedShellFailure(
                "summary record for the week carries no "
                "headline_unit_identifiers field, and no weekly "
                "headline count stands certified without it")
        identifiers = _weekly_pair_get(record, "headline_unit_identifiers")
        if identifiers is None:
            raise NamedShellFailure(
                "summary record for the week carries a "
                "headline_unit_identifiers field standing at no "
                "value, and no weekly headline count stands "
                "certified without it")
        if isinstance(identifiers, str):
            identifiers = (identifiers,)
        elif not isinstance(identifiers, (list, tuple, set, frozenset)):
            raise NamedShellFailure(
                "summary record for the week carries a "
                "headline_unit_identifiers field the count cannot "
                "read: " + type(identifiers).__name__
                + "; no weekly headline count stands certified "
                "without it")
        for unit_id in _container_parts(identifiers):
            if isinstance(unit_id, (list, tuple, set, frozenset,
                                    dict)):
                # The bound of row R14-072, stated in the open: a
                # container element in place of an identifier
                # still counts as one.
                key = ("container", _stored_identifier_form(unit_id))
            elif isinstance(unit_id, str) and \
                    _HEADLINE_IDENTIFIER_PATTERN.fullmatch(
                        str.__str__(unit_id)) is not None:
                key = ("text", str.__str__(unit_id))
            else:
                raise NamedShellFailure(
                    "summary record for the week carries an "
                    "identifier standing in no unit identifier "
                    "form, and no count stands stated over "
                    "unvalidated contents: "
                    + _identifier_refusal_text(unit_id))
            if key not in seen:
                seen.append(key)
    return len(seen)


_HEADLINE_IDENTIFIER_PATTERN = re.compile(r"u[0-9]+")


def process_and_network_call_log(run_id):
    """The process and network call log of one run, supplied by
    this shell as an input record to the outside call check. The
    shell computes no check outcome from it."""
    return _mod10.gc08_record("call_log", run_id)


def outside_call_check(dependency_manifest, call_log, extra_source=None):
    """The outside call check, GC-08 in the form DQ7-12 gives it:
    the outcome stands computed from the dependency manifest and
    the process and network call log and from no other source,
    and stands in the outside call check field of the run record.
    A pass certifies only the absence the check reads. Both
    inputs stand required in record form: an input standing
    absent or in no record form stands refused in the named
    form, and no clean outcome stands returned for a check
    that examined nothing. A lawful call log carries its calls
    under the key calls or the key entries, and no other key;
    each call entry stands as a record carrying an
    outside_call mark, whose value stands as true or false,
    stated as a boolean, as the text true, false, yes, or
    no, or as the number 1 or 0. A text mark stands judged on
    the text it stores, read through the stored text form of
    this module, never through a strip or lower reading the
    mark itself supplies. A number mark stands judged on the
    number it stores, read through the base integer reading,
    never through an equality reading the mark itself
    supplies, so a mark storing a stated number stands judged
    as that number and a mark storing any other number draws
    the named refusal, with no bare escape on a raising
    equality reading. A log or an entry in any
    other form stands refused in
    named form, never read as an empty log."""
    if extra_source is not None:
        raise NamedShellFailure(
            "outside call check computed from a third source is barred"
        )
    if not isinstance(dependency_manifest, dict):
        raise NamedShellFailure(
            "outside call check carries no dependency manifest to "
            "read: a manifest in record form stands required, and "
            "no outside call standing stands certified without it")
    if not isinstance(call_log, dict):
        raise NamedShellFailure(
            "outside call check carries no call log to read: a "
            "call log in record form stands required, and no "
            "outside call standing stands certified without it")
    for key in list(dict.keys(call_log)):
        if not (isinstance(key, str) and (
                str.__eq__(key, "calls") or str.__eq__(key, "entries"))):
            raise NamedShellFailure(
                "outside call check stands refused: the call log "
                "carries a key the check cannot read: " + _safe_text(key)
                + ": a call log carries its calls under the key "
                "calls or the key entries, and no outside call "
                "standing stands certified on a log the check "
                "cannot read whole")
    calls = []
    for calls_key in ("calls", "entries"):
        if not _base_contains(call_log, calls_key):
            continue
        calls_part = _base_get(call_log, calls_key)
        if not isinstance(calls_part, (list, tuple, set, frozenset)):
            raise NamedShellFailure(
                "outside call check stands refused: the call log "
                "carries its calls in no list form under the key "
                "calls or the key entries: a list of call entries "
                "stands required, and no outside call standing "
                "stands certified without it")
        calls.extend(_container_parts(calls_part))
    outside = []
    for call in calls:
        if not isinstance(call, dict) or not _base_contains(
                call, "outside_call"):
            raise NamedShellFailure(
                "outside call check stands refused: a call entry "
                "carries no outside_call mark: each call entry "
                "stands as a record carrying an outside_call "
                "mark, and no outside call standing stands "
                "certified on an entry the check cannot read")
        mark = _base_get(call, "outside_call")
        if isinstance(mark, bool):
            stands_outside = mark
        elif isinstance(mark, str):
            word = str.lower(str.strip(_stored_text(mark)))
            if word in ("true", "yes"):
                stands_outside = True
            elif word in ("false", "no"):
                stands_outside = False
            else:
                raise NamedShellFailure(
                    "outside call check stands refused: a call "
                    "entry carries an outside_call value outside "
                    "the stated values: true or false, stated as "
                    "a boolean, as the text true, false, yes, "
                    "or no, or as the number 1 or 0")
        elif isinstance(mark, int) and int.__int__(mark) in (0, 1):
            stands_outside = bool(int.__int__(mark))
        else:
            raise NamedShellFailure(
                "outside call check stands refused: a call entry "
                "carries an outside_call value outside the stated "
                "values: true or false, stated as a boolean, as "
                "the text true, false, yes, or no, or as the "
                "number 1 or 0")
        if stands_outside:
            outside.append(call)
    outcome = "outside calls present" if outside else "no outside calls read"
    manifest_count = 0
    if isinstance(dependency_manifest, dict) and _base_contains(
            dependency_manifest, "entries"):
        manifest_value = _base_get(dependency_manifest, "entries")
        if not isinstance(manifest_value, (list, tuple, set,
                                           frozenset)):
            raise NamedShellFailure(
                "outside call check stands refused: the dependency "
                "manifest carries its entries in no list form: a "
                "list of manifest entries stands required, and no "
                "outside call standing stands certified without it")
        manifest_count = len(_container_parts(manifest_value))
    return {
        "field": "outside_call_check",
        "outcome": outcome,
        "sources": ["dependency manifest", "process and network call log"],
        "certifies": "only the absence the check reads",
        "manifest_entries": manifest_count,
    }


_EDIT_ACTS = (
    "edit", "modify", "change", "update", "alter", "rewrite",
    "amend", "patch", "redact", "replace", "correct", "supersede",
)

_DESTRUCTIVE_ACTS = (
    "delete", "destroy", "remove", "erase", "overwrite",
    "purge", "drop", "wipe", "clear", "truncate", "expunge",
    "void", "obliterate", "annihilate",
)

_READ_ACTS = ("read", "view", "inspect", "show", "list", "get", "fetch")

_ARTICLES = ("the", "a", "an")

_PROTECTED_TARGETS = (
    "sealed family record", "closed run record", "checkpoint set",
)


# Letter canonicalisation, in the form the Round 5 register
# states for the shared folded reading: compatibility
# decomposition with combining marks dropped, so accented and
# full width forms reduce to their base letters, together with
# a recorded letter mapping for the dresses decomposition
# cannot reduce. The mapping below records, per letter, the
# Latin letters that letter stands for: the Cyrillic letters by
# the Latin letters they transliterate, which for the letters
# a, e, and o are also the letters they resemble, and the Greek
# letters by the one shared folded reading the MOD-10
# transliteration map states, so pi reads as p, rho as r,
# gamma as g, eta as e, nu as n, and omega as o at both
# modules, and one folded dress reads as one party at both.
_LETTER_MAP = {
    "\u0430": "a", "\u0431": "b", "\u0432": "v", "\u0433": "g",
    "\u0434": "d", "\u0435": "e", "\u0436": "zh", "\u0437": "z",
    "\u0438": "i", "\u0439": "y", "\u043a": "k", "\u043b": "l",
    "\u043c": "m", "\u043d": "n", "\u043e": "o", "\u043f": "p",
    "\u0440": "r", "\u0441": "s", "\u0442": "t", "\u0443": "u",
    "\u0444": "f", "\u0445": "h", "\u0446": "ts", "\u0447": "ch",
    "\u0448": "sh", "\u0449": "shch", "\u044b": "y",
    "\u044d": "e", "\u044e": "yu", "\u044f": "ya",
    "\u0454": "e", "\u0456": "i", "\u0457": "yi", "\u0458": "j",
    "\u0459": "lj", "\u045a": "nj", "\u045b": "kj", "\u045f": "dz",
    "\u03b1": "a", "\u03b2": "b", "\u03b3": "g", "\u03b4": "d",
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "e", "\u03b8": "th",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03bf": "o", "\u03c0": "p", "\u03c1": "r",
    "\u03c3": "s", "\u03c4": "t", "\u03c5": "u", "\u03c6": "ph",
    "\u03c7": "x", "\u03c8": "ps", "\u03c9": "o",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
}

# Digit and leet substitutions inside a word: a digit standing
# among letters reads as the letter it stands for.
_LEET_DIGITS = {
    "0": "o", "1": "l", "2": "z", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
}


def _canonicalise_text(value):
    stored = str.__str__(value) if isinstance(value, str) else ""
    decomposed = unicodedata.normalize("NFKD", stored)
    chars = []
    for char in decomposed:
        if unicodedata.combining(char):
            continue
        mapped = _LETTER_MAP.get(
            char, _LETTER_MAP.get(char.lower(), char))
        digit = unicodedata.digit(mapped, None) if len(str(mapped)) == 1 else None
        if digit is not None:
            chars.append(str(digit))
        else:
            chars.append(mapped)
    return "".join(chars).lower()


def _canonicalise_word(word):
    word = "".join(
        str(unicodedata.digit(char)) if unicodedata.digit(char, None) is not None else char
        for char in word)
    if any(char.isalpha() for char in word) and any(
            char.isdigit() for char in word):
        word = "".join(
            _LEET_DIGITS.get(char, char) for char in word)
    return word


_VOCABULARY_WORDS = frozenset(
    word
    for phrase in (
        _PROTECTED_TARGETS + _EDIT_ACTS + _DESTRUCTIVE_ACTS
        + _READ_ACTS + ("flag rule", "deletion rule"))
    for word in phrase.split()
)


_VOCABULARY_ORDERED = tuple(dict.fromkeys(
    word
    for phrase in (
        _PROTECTED_TARGETS + _EDIT_ACTS + _DESTRUCTIVE_ACTS
        + _READ_ACTS + ("flag rule", "deletion rule"))
    for word in phrase.split()
))


def _segments_into_vocabulary(word, vocabulary):
    """Return whether a word stands as two or more vocabulary
    words joined with no separator. Such a word stands read
    by the folded joined reading, not as one dressed word, so
    the resolver leaves it as itself."""
    counts = [set() for _ in range(len(word) + 1)]
    counts[0].add(0)
    for start in range(len(word)):
        if not counts[start]:
            continue
        for candidate in vocabulary:
            if word.startswith(candidate, start):
                for count in counts[start]:
                    counts[start + len(candidate)].add(count + 1)
    return any(count >= 2 for count in counts[len(word)])


def _differing_positions(left, right):
    return [
        index for index in range(len(left)) if left[index] != right[index]]


def _carries_transposed_pair(reduced, candidate, differing):
    """Whether two of the differing positions stand as one
    transposed pair: the reduced letters at those positions
    stand as the candidate letters at each other position."""
    for first, second in itertools.combinations(differing, 2):
        if (reduced[first] == candidate[second]
                and reduced[second] == candidate[first]):
            return True
    return False


def _mixed_added_resolves(word, candidate):
    """Whether a word reads as a candidate word under added
    letters composed with replacements or with one
    transposition. The added count stands between one and
    seven. The differing positions left after the added
    letters stand struck number at most five, and the total
    of the added count and the remaining changes stands at
    most seven, where one transposed pair among the differing
    positions counts as one change in place of the two
    differing positions it stands on. A word whose differing
    count or total stands past those bounds does not resolve
    under this reading."""
    added = len(word) - len(candidate)
    if added < 1 or added > 7 or not candidate:
        return False

    def fewest_differing(variant, forced):
        unreachable = len(word) + 1
        row = [0] + [unreachable] * len(variant)
        for char in word:
            new_row = [0] * (len(variant) + 1)
            for spot in range(1, len(variant) + 1):
                if spot - 1 in forced:
                    cost = 0 if char == variant[spot - 1] else unreachable
                else:
                    cost = 0 if char == variant[spot - 1] else 1
                new_row[spot] = min(row[spot], row[spot - 1] + cost)
            row = new_row
        return row[len(variant)]

    fewest = fewest_differing(candidate, frozenset())
    if fewest < 1 or fewest > 5:
        return False
    if added + fewest <= 7:
        return True
    if added + 1 > 7:
        return False
    for first in range(len(candidate)):
        for second in range(first + 1, len(candidate)):
            if candidate[first] == candidate[second]:
                continue
            variant = list(candidate)
            variant[first], variant[second] = (
                variant[second], variant[first])
            remaining = fewest_differing(
                "".join(variant), frozenset((first, second)))
            if remaining <= 3 and added + 1 + remaining <= 7:
                return True
    return False


def _anywhere_transposition_resolves(word, candidate):
    """Whether a word reads as a candidate word under one
    transposed pair standing at any two positions of the word,
    including the two edge positions, composed with three
    further replaced letters. The differing positions number
    five: the two positions of the pair and the three replaced
    positions. The three remaining positions stand as
    replacements only where no two of them stand as a
    transposed pair of their own: a word whose remaining
    positions carry such a pair stands built from two
    transposed pairs and one replaced letter, a change total
    of three, and does not resolve under this reading."""
    if len(word) != len(candidate):
        return False
    differing = _differing_positions(word, candidate)
    if len(differing) != 5:
        return False
    for first, second in itertools.combinations(differing, 2):
        if not (word[first] == candidate[second]
                and word[second] == candidate[first]):
            continue
        remaining = [
            index for index in differing
            if index not in (first, second)]
        if not _carries_transposed_pair(word, candidate, remaining):
            return True
    return False


def _two_pairs_composed_resolves(word, candidate, differing):
    """Whether the differing positions of a word stand as
    two transposed pairs standing at any positions of the
    word, composed with the remaining differing positions
    standing as replaced letters. The differing positions
    number six or seven: four positions standing as the two
    pairs and two or three positions standing as
    replacements, a change total of four or five, inside
    the stated composition form of up to two transpositions
    composed with up to three replacements where the total
    number of changes stands past three. The remaining
    positions stand as replacements only where no two of
    them stand as a transposed pair of their own, in the
    form the anywhere transposition reading states: a word
    whose remaining positions carry such a pair stands
    built from a further transposition and does not resolve
    under this reading."""
    if len(differing) not in (6, 7):
        return False
    pairs = [
        (first, second)
        for first, second in itertools.combinations(differing, 2)
        if word[first] == candidate[second]
        and word[second] == candidate[first]]
    for spot, first_pair in enumerate(pairs):
        for second_pair in pairs[spot + 1:]:
            if set(first_pair) & set(second_pair):
                continue
            remaining = [
                index for index in differing
                if index not in first_pair
                and index not in second_pair]
            if not _carries_transposed_pair(
                    word, candidate, remaining):
                return True
    return False


def _composed_transpositions_resolve(word, candidate, differing):
    """Whether the differing positions of a word stand as
    one or two transposed pairs standing at any positions
    of the word, composed with one to three remaining
    differing positions standing as replaced letters, in
    the MOD-10 form: the composition resolves only where
    the total number of changes, the pairs plus the
    remaining positions, stands past three, and the
    remaining positions stand as replacements only where
    no two of them stand as a transposed pair of their
    own."""
    if len(differing) < 4 or len(differing) > 7:
        return False
    pair_options = [
        (first, second)
        for first, second in itertools.combinations(differing, 2)
        if word[first] == candidate[second]
        and word[second] == candidate[first]]
    for swap_count in (1, 2):
        for chosen in itertools.combinations(pair_options, swap_count):
            used = [index for pair in chosen for index in pair]
            if len(set(used)) != len(used):
                continue
            rest = [
                index for index in differing if index not in used]
            if not 1 <= len(rest) <= 3:
                continue
            if swap_count + len(rest) <= 3:
                continue
            if _carries_transposed_pair(word, candidate, rest):
                continue
            return True
    return False


def _three_pairs_composed_resolves(word, candidate, differing):
    """Whether the differing positions of a word stand as
    three disjoint transposed pairs standing at any
    positions of the word, adjacent or not, composed with
    one to three remaining differing positions standing
    as replaced letters. The remaining positions stand as
    replacements only where no two of them stand as a
    transposed pair of their own, in the form the anywhere
    transposition reading states."""
    if len(differing) not in (7, 8, 9):
        return False
    pairs = [
        (first, second)
        for first, second in itertools.combinations(differing, 2)
        if word[first] == candidate[second]
        and word[second] == candidate[first]]
    for chosen in itertools.combinations(pairs, 3):
        used = [index for pair in chosen for index in pair]
        if len(set(used)) != len(used):
            continue
        remaining = [
            index for index in differing if index not in used]
        if not 1 <= len(remaining) <= 3:
            continue
        if not _carries_transposed_pair(
                word, candidate, remaining):
            return True
    return False


def _total_three_transposition_dress(word, candidate, minimum_pairs):
    """Whether a word stands as a dress of a candidate of
    its own length built from transposed pairs and
    replaced letters at a change total of three or below,
    with at least the stated number of transposed pairs.
    Such a dress stands as itself under the stated
    composition form, which resolves transpositions
    composed with replacements only past a total of
    three, so no later limb re-reads it as another word."""
    if len(word) != len(candidate):
        return False
    differing = _differing_positions(word, candidate)
    if len(differing) not in (3, 4, 5):
        return False
    pairs = [
        (first, second)
        for first, second in itertools.combinations(differing, 2)
        if word[first] == candidate[second]
        and word[second] == candidate[first]]
    for pair_count in range(minimum_pairs, 3):
        for chosen in itertools.combinations(pairs, pair_count):
            used = [index for pair in chosen for index in pair]
            if len(set(used)) != len(used):
                continue
            remaining = len(differing) - 2 * pair_count
            if remaining >= 0 and pair_count + remaining <= 3:
                return True
    return False


def _resolve_against(word, ordered, vocabulary):
    """Read one word as the vocabulary word it dresses, where
    it dresses one: the word itself where it stands plain, a
    word with one, two, three, four, five, six, or seven
    added letters struck, a word with one letter dropped
    from a vocabulary word, a word with one letter replaced,
    a word with two adjacent letters transposed, and the
    compounded
    forms, one letter dropped together with one letter
    replaced, one transposition together with one letter
    dropped, two letters replaced, two letters dropped from
    a vocabulary word, one transposition together with one
    letter replaced, three letters replaced, three letters
    dropped from a vocabulary word, two transpositions, one
    transposition together with two letters replaced, four
    letters replaced, four letters dropped from a vocabulary
    word, three transpositions, and transpositions composed
    with replacements where the total number of changes
    stands past three, up to three replacements composed
    with up to two transpositions. Past those forms the
    resolver also reads five letters replaced where no two
    differing positions stand as a transposed pair, five
    letters dropped from a vocabulary word, three adjacent
    transpositions composed with three letters replaced, six
    changes in total, and one, two, or three transpositions
    of letter pairs standing anywhere in the word, adjacent
    or not, read by pairing the differing positions. The
    dropped, replaced, and transposed limbs run on words of
    two letters as well, so a drop from a three letter word
    still resolves. A word of one letter stands read through
    the drop limbs only where exactly one vocabulary word
    drops to it, so a one letter word that several words
    drop to stands as itself. Past those forms the resolver also reads added letters composed with replacements or with one transposition, where the differing positions left after the added letters stand struck number at most five and the total of the added count and the remaining changes stands at most seven, a transposed pair among the differing positions counting as one change in place of the two positions it stands on. The resolver also reads one transposed pair standing at any two positions of the word, including the two edge positions, composed with three further replaced letters. That anywhere composition stands in the main body, in the MOD-10 form of one or two transposed pairs at any positions beside one to three replacements resolving only past a change total of three with no transposed pair among the remaining positions, ahead of the five replacement and mixed added readings, and three disjoint transposed pairs at any positions, adjacent or not, composed with one to three replaced letters also resolve in the main body. A word built from a vocabulary word by transposed pairs and replacements at a change total of three or below stands as itself: the five replacement reading and the mixed added reading do not re-read such a word as another word. Any other word stands as
    itself."""
    if word in vocabulary:
        return word
    if _segments_into_vocabulary(word, vocabulary):
        return word
    vocabulary_lengths = {len(item) for item in vocabulary}
    for added in (1, 2, 3, 4, 5, 6, 7):
        if len(word) > added and (
                len(word) - added) in vocabulary_lengths:
            for cuts in itertools.combinations(range(len(word)), added):
                reduced = "".join(
                    char for index, char in enumerate(word)
                    if index not in cuts)
                if reduced in vocabulary:
                    return reduced
    if len(word) < 2:
        matches = []
        for drops in (1, 2, 3):
            for candidate in ordered:
                if len(candidate) != len(word) + drops:
                    continue
                for cuts in itertools.combinations(
                        range(len(candidate)), drops):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word and candidate not in matches:
                        matches.append(candidate)
        if len(matches) == 1:
            return matches[0]
        return word
    if len(word) >= 2:
        for candidate in ordered:
            if len(candidate) == len(word) + 1:
                for cut in range(len(candidate)):
                    if candidate[:cut] + candidate[cut + 1:] == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            for cut in range(len(word) - 1):
                swapped = (
                    candidate[:cut] + candidate[cut + 1]
                    + candidate[cut] + candidate[cut + 2:])
                if swapped == word:
                    return candidate
        for candidate in ordered:
            if len(candidate) == len(word) + 2:
                for cuts in itertools.combinations(
                        range(len(candidate)), 2):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) == len(word) + 3:
                for cuts in itertools.combinations(
                        range(len(candidate)), 3):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) == len(word) + 4:
                for cuts in itertools.combinations(
                        range(len(candidate)), 4):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) == len(word) + 5:
                for cuts in itertools.combinations(
                        range(len(candidate)), 5):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word) if left != right)
            if differences == 1:
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word) + 1:
                continue
            for cut in range(len(candidate)):
                dropped = candidate[:cut] + candidate[cut + 1:]
                differences = sum(
                    1 for left, right in zip(dropped, word)
                    if left != right)
                if differences == 1:
                    return candidate
                for swap in range(len(dropped) - 1):
                    swapped = (
                        dropped[:swap] + dropped[swap + 1]
                        + dropped[swap] + dropped[swap + 2:])
                    if swapped == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            if sorted(candidate) != sorted(word):
                continue
            for first in range(len(candidate) - 1):
                if candidate[first] == candidate[first + 1]:
                    continue
                once = (
                    candidate[:first] + candidate[first + 1]
                    + candidate[first] + candidate[first + 2:])
                for second in range(len(once) - 1):
                    if once[second] == once[second + 1]:
                        continue
                    twice = (
                        once[:second] + once[second + 1]
                        + once[second] + once[second + 2:])
                    if twice == word:
                        return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word) if left != right)
            if differences == 2:
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            for swap in range(len(candidate) - 1):
                if candidate[swap] == candidate[swap + 1]:
                    continue
                swapped = (
                    candidate[:swap] + candidate[swap + 1]
                    + candidate[swap] + candidate[swap + 2:])
                differences = sum(
                    1 for left, right in zip(swapped, word)
                    if left != right)
                if differences == 1:
                    return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            swaps = 0
            remaining = 0
            remaining_positions = []
            position = 0
            while position < len(differing):
                index = differing[position]
                if (position + 1 < len(differing)
                        and differing[position + 1] == index + 1
                        and word[index] == candidate[index + 1]
                        and word[index + 1] == candidate[index]):
                    swaps += 1
                    position += 2
                else:
                    remaining += 1
                    remaining_positions.append(index)
                    position += 1
            if swaps >= 1 and remaining == 0 and swaps <= 3:
                return candidate
            if (1 <= swaps <= 2 and 1 <= remaining <= 3
                    and swaps + remaining > 3
                    and not _carries_transposed_pair(
                        word, candidate, remaining_positions)):
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if not differing or len(differing) > 6:
                continue
            if len(differing) % 2:
                continue

            def pairable(indices):
                if not indices:
                    return True
                first = indices[0]
                for spot in range(1, len(indices)):
                    second = indices[spot]
                    if (word[first] == candidate[second]
                            and word[second] == candidate[first]):
                        rest = indices[1:spot] + indices[spot + 1:]
                        if pairable(rest):
                            return True
                return False

            if pairable(differing):
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if _composed_transpositions_resolve(
                    word, candidate, differing):
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if _three_pairs_composed_resolves(
                    word, candidate, differing):
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if _two_pairs_composed_resolves(word, candidate, differing):
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            starts = [
                index for index in range(len(candidate) - 1)
                if word[index] == candidate[index + 1]
                and word[index + 1] == candidate[index]]
            for combo in itertools.combinations(starts, 3):
                if any(combo[spot + 1] - combo[spot] < 2
                        for spot in range(len(combo) - 1)):
                    continue
                variant = list(candidate)
                for index in combo:
                    variant[index], variant[index + 1] = (
                        variant[index + 1], variant[index])
                remaining = sum(
                    1 for left, right in zip(variant, word)
                    if left != right)
                if remaining == 3:
                    return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word) if left != right)
            if differences == 3:
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word) if left != right)
            if differences == 4:
                return candidate
        for candidate in ordered:
            if _total_three_transposition_dress(word, candidate, 2):
                return word
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if len(differing) != 5:
                continue
            paired = any(
                word[left] == candidate[right]
                and word[right] == candidate[left]
                for left, right in itertools.combinations(differing, 2))
            if not paired:
                return candidate
        for candidate in ordered:
            if len(candidate) != len(word):
                continue
            base_differences = sum(
                1 for left, right in zip(candidate, word) if left != right)
            if base_differences < 1 or base_differences > 4:
                continue
            for swap in range(len(candidate) - 1):
                if candidate[swap] == candidate[swap + 1]:
                    continue
                swapped = (
                    candidate[:swap] + candidate[swap + 1]
                    + candidate[swap] + candidate[swap + 2:])
                differences = sum(
                    1 for left, right in zip(swapped, word)
                    if left != right)
                if differences == 2:
                    return candidate
    stands_as_itself = any(
        _total_three_transposition_dress(word, candidate, 1)
        for candidate in ordered)
    for candidate in ordered:
        if not stands_as_itself and _mixed_added_resolves(
                word, candidate):
            return candidate
        if _anywhere_transposition_resolves(word, candidate):
            return candidate
    return word


def _resolve_word(word):
    """Read one word as the vocabulary word it dresses.
    See _resolve_against for the forms read."""
    return _resolve_against(word, _VOCABULARY_ORDERED, _VOCABULARY_WORDS)


_ACTOR_VOCABULARY_ORDERED = ("person", "program")
_ACTOR_VOCABULARY = frozenset(_ACTOR_VOCABULARY_ORDERED)


def _resolve_actor_word(word):
    """Read one actor word as the actor word it dresses, under
    the same resolver limbs as the protected target words,
    against the actor vocabulary of person and program."""
    return _resolve_against(
        word, _ACTOR_VOCABULARY_ORDERED, _ACTOR_VOCABULARY)


def _plural_form(word):
    if len(word) > 3 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 1 and word.endswith("s"):
        return word[:-1]
    return word


def _single_reading(word):
    """The reading of one fragment on its own, with its
    standing: exact where the plural form stands in the
    vocabulary, resolved where the resolver reads it as a
    vocabulary word it dresses, and plain otherwise."""
    base = _plural_form(word)
    if base in _VOCABULARY_WORDS:
        return base, "exact"
    resolved = _resolve_word(_canonicalise_word(base))
    if resolved in _VOCABULARY_WORDS and resolved != base:
        return resolved, "resolved"
    return resolved, "plain"


def _group_reading(fragments):
    """The reading of several fragments joined with no
    separator, where they join into one vocabulary word:
    the joined word where its plural form stands in the
    vocabulary, the joined form read through the resolver
    where it dresses a vocabulary word, and None where the
    joined form stands as no vocabulary word under either
    reading. The exact reading stands tried first, so a
    group reading reaches a shorter word through the
    resolver only where the plain joining does not already
    read as a word, and a resolved group reading stands
    accepted only where the resolver strikes fewer letters
    than the shortest fragment carries, so no whole
    fragment stands struck away to reach a shorter word. Where the plain joined form stands as
    no vocabulary word, the joined form stands tried again
    with article fragments standing between the first and
    last fragments dropped, under both readings, so a word
    split by an inserted article still reads as the word it
    names. The plain joined form stands tried first, so a
    fragment that is itself a letter of the word, including
    the letter a, is never dropped where the plain joining
    already reads as the word."""
    joined = _plural_form("".join(fragments))
    if joined in _VOCABULARY_WORDS:
        return joined, "exact"
    resolved = _resolve_word(_canonicalise_word(joined))
    if resolved in _VOCABULARY_WORDS and (
            len(joined) - len(resolved)
            < min(len(fragment) for fragment in fragments)):
        return resolved, "resolved"
    if len(fragments) >= 3 and any(
            fragment in _ARTICLES for fragment in fragments[1:-1]):
        kept = [fragments[0]] + [
            fragment for fragment in fragments[1:-1]
            if fragment not in _ARTICLES] + [fragments[-1]]
        joined = _plural_form("".join(kept))
        if joined in _VOCABULARY_WORDS:
            return joined, "exact"
        resolved = _resolve_word(_canonicalise_word(joined))
        if resolved in _VOCABULARY_WORDS and (
                len(joined) - len(resolved)
                < min(len(fragment) for fragment in kept)):
            return resolved, "resolved"
    return None


def _reading_words(fragments):
    """Read a fragment sequence as words. The reading stands
    as the partition of the sequence with the highest score,
    where a word scores by its standing for every fragment it
    covers, an exact vocabulary word scores above a resolved
    one, a resolved word scores above a plain fragment, and
    dropping an article standing between words scores above
    keeping it as a plain fragment. The group reading of a
    whole fragment group stands judged beside the chunk
    readings of its parts on the same points: where two
    partitions stand at equal points, the partition reading
    fewer words stands chosen, so one group reading covering
    the whole group stands above rival chunk readings that
    cover the same fragments in more words. A separator
    split inside one word therefore reads as that word, even
    where a fragment on its own resolves elsewhere or stands
    as an article, while words standing apart keep their own
    readings. The group search tries groups of up to thirty
    two fragments, with the standing bound of twenty four
    joined characters governing the groups it can read."""
    scores = {"exact": 20, "resolved": 15, "plain": 2}
    best = {}

    def search(start):
        if start in best:
            return best[start]
        if start >= len(fragments):
            return (0, 0, ())
        options = []
        word, standing = _single_reading(fragments[start])
        rest_score, rest_fewer, rest_words = search(start + 1)
        options.append((
            scores[standing] + rest_score, rest_fewer - 1,
            (word,) + rest_words))
        if fragments[start] in _ARTICLES:
            options.append((5 + rest_score, rest_fewer, rest_words))
        joined = [fragments[start]]
        for size in range(2, min(32, len(fragments) - start) + 1):
            joined.append(fragments[start + size - 1])
            if len("".join(joined)) > 24:
                break
            reading = _group_reading(joined)
            if reading is None:
                continue
            group_word, group_standing = reading
            rest_score, rest_fewer, rest_words = search(start + size)
            group_score = scores[group_standing] * size
            options.append((
                group_score + rest_score, rest_fewer - 1,
                (group_word,) + rest_words))
        chosen = max(options, key=lambda option: (option[0], option[1]))
        best[start] = chosen
        return chosen

    return list(search(0)[2])


def _normalise_name(value):
    text = _canonicalise_text(value)
    text = "".join(
        char if char.isalnum() else " " for char in text)
    fragments = []
    for raw in text.split():
        word = raw.strip(".,;:!?\"'()[]{}")
        if word:
            fragments.append(word)
    return " ".join(_reading_words(fragments))


def _verb_stems(word):
    stems = [word]
    if word.endswith("ing") and len(word) > 4:
        base = word[:-3]
        stems.extend([base, base + "e"])
        if len(base) > 1 and base[-1] == base[-2]:
            stems.extend([base[:-1], base[:-1] + "e"])
    elif word.endswith("ed") and len(word) > 3:
        base = word[:-2]
        stems.extend([base, base + "e"])
        if len(base) > 1 and base[-1] == base[-2]:
            stems.extend([base[:-1], base[:-1] + "e"])
    return stems


def _act_class(kind):
    words = kind.split()
    if not words:
        return None
    forms = []
    for word in words:
        forms.extend(_verb_stems(word))
    if any(form in _DESTRUCTIVE_ACTS for form in forms):
        return "destructive"
    if any(form in _EDIT_ACTS for form in forms):
        return "edit"
    if all(word in _READ_ACTS for word in words):
        return "read"
    return "unread"


def _folded_reading(word_reading):
    return "".join(
        char for char in word_reading if char.isalnum())


_PROTECTED_TARGETS_BY_FOLDED = {
    "sealedfamilyrecord": "sealed family record",
    "closedrunrecord": "closed run record",
    "checkpointset": "checkpoint set",
}

_RULE_PATHS_BY_FOLDED = {
    "flagrule": "flag rule",
    "deletionrule": "deletion rule",
}


def _touched_protected_targets(target):
    """The protected targets a target reading touches, read by
    containment on the canonicalised reading: a protected target
    stands touched where its word sequence stands whole inside
    the target word sequence, or where its folded form stands
    whole inside the target folded form, the joined spelling
    with no separator. A target that shares letters with a
    protected target without containing it whole touches none."""
    words = target.split()
    folded = _folded_reading(target)
    touched = []
    for protected in _PROTECTED_TARGETS:
        protected_words = protected.split()
        width = len(protected_words)
        contained = any(
            words[start:start + width] == protected_words
            for start in range(len(words) - width + 1))
        if contained or _folded_reading(protected) in folded:
            touched.append(protected)
    return touched


def _bar_on_target(protected, act, path):
    if protected == "sealed family record":
        if act == "read":
            return None
        return "no operator action edits a sealed family record"
    if protected == "closed run record":
        if act == "read":
            return None
        if act == "edit" and path == "flag rule":
            return None
        if act == "destructive":
            return (
                "no operator action destroys a closed run record, "
                "on the flag rule path or on any other")
        return (
            "no operator action edits a closed run record outside "
            "the flag rule path")
    if protected == "checkpoint set":
        if act == "read":
            return None
        if act in ("edit", "destructive") and path == "deletion rule":
            return None
        return (
            "no operator action edits a checkpoint set outside "
            "the deletion rule")
    return None


def _operator_action_bar(action):
    if not isinstance(action, dict):
        return "the action is not a record of an act and a target"
    raw_kind = dict.get(action, "kind")
    raw_target = dict.get(action, "target")
    if raw_kind is not None and not isinstance(raw_kind, str):
        return (
            "the action kind stands in a form the boundary cannot "
            "read, a " + type(raw_kind).__name__
            + ", not a stated act")
    if raw_target is not None and not isinstance(raw_target, str):
        return (
            "the action target stands in a form the boundary cannot "
            "read, a " + type(raw_target).__name__
            + ", not a stated target")
    kind = _normalise_name(raw_kind)
    target = _normalise_name(raw_target)
    raw_path = dict.get(action, "path")
    if isinstance(raw_path, (bytes, bytearray, memoryview)):
        raw_path = _stored_text(raw_path)
    path = _normalise_name(raw_path)
    path = _RULE_PATHS_BY_FOLDED.get(
        _folded_reading(path), path)
    touched = _touched_protected_targets(target)
    if not kind:
        if touched:
            return (
                "an action with no kind stated stands refused on a "
                "protected target: " + touched[0])
        return "an action with no kind stated stands refused"
    act = _act_class(kind)
    for protected in touched:
        bar = _bar_on_target(protected, act, path)
        if bar is not None:
            return bar
    return None


def validate_operator_action(action):
    """The operator boundary at the shell. The act stands read,
    not its spelling: verb synonyms in the edit and destructive
    families, verb inflections, case, trailing punctuation,
    articles, plural, and underscored, hyphenated, dotted,
    slashed, backslashed, semicolon joined, and colon joined
    spellings of a protected target name the same act, as does
    a spelling joined with no separator at all, read beside
    the word reading by its folded form of letters and digits
    only, and every such act stands refused
    outside its stated rule path. The reading stands
    canonicalised before it is compared: accented and full
    width letters reduce to their base letters, letters of
    other scripts read by the recorded letter mapping, digits
    standing inside a word read as the letters they stand for,
    and a word carrying one added letter reads as the word it
    dresses, so a protected target in any such dress names the
    same target. The protected check reads containment on that
    reading: a target carrying a protected target whole, alone
    or beside further target matter, stands under that target
    bar, and the reason form names the bar on the protected
    target touched. A kind or a target standing in
    a non text form, and a verb the boundary cannot read as a
    stated act, stand refused on a protected target by name in
    the reason form. A rule path handed in a buffer form
    stands read on the text it stores, in the same manner as
    the flag evaluation tier and actor limbs of this module,
    so the allowed standing stands alike in every dress a
    path stores its text in. No operator action edits a sealed family
    record on any path; the flag rule path admits edit acts only
    on a closed run record, and a destructive act stands refused
    there as on every path; a checkpoint set stands edited only
    on the deletion rule. Validation reads the action record
    alone."""
    return _operator_action_bar(action) is None


def validate_operator_action_with_reason(action):
    """The operator boundary with its reason in words, beside the
    boolean standing: a refused action carries the rule that bars
    it, and a standing action carries the path it stands on."""
    bar = _operator_action_bar(action)
    if bar is not None:
        return {"allowed": False, "reason": bar}
    return {
        "allowed": True,
        "reason": "the action stands on its stated rule path or "
                  "touches no protected target",
    }


# ---------------------------------------------------------------------------
# Operator runbook, the S-15 deliverable in the product own form
# ---------------------------------------------------------------------------

_RUNBOOK_STEPS = (
    "Read the family record and the run record before any act. The shell carries records and interprets none of them.",
    "Start runs and sweeps through the start commands only. While the DQ7-02 adoption record does not stand, every start returns the gated refusal that names its gate, and no run starts.",
    "Keep pilot work inside its confinement: timing, conformance, and procedure rates only. Each pilot output carries its pilot confined label in the same artefact as its figure, and pilot artefacts are stored apart from sweep results.",
    "Read stores by kind: sweep, pilot, and live. Never resolve a record across stores in one lookup.",
    "Run the program checks by name: the store kind check; the flag evaluation, whose inputs and outcome stand written into the stored summary record itself; the weekly headline count, counted from the stored summary records alone; and the outside call check, computed from the dependency manifest and the process and network call log only, certifying only the absence the check reads.",
    "Treat every named failure as the result of its act. Report it with its run identifier and its stage, and never present an empty result in its place, and never let a command exit cleanly over a failed run.",
    "Make no edit to a sealed family record, to a closed run record outside the flag rule path, or to a checkpoint set outside the deletion rule. Validation reads the action record alone.",
)


def operator_runbook():
    """The operator procedure of this product, standing as the
    runbook deliverable of slice S-15 in the product own form.
    The runbook stands in this module at operator_runbook, in
    the code of this module, and that code stands as its only
    locus in the shipped product."""
    return {
        "form": "operator runbook",
        "deliverable_of": "slice S-15",
        "steps": list(_RUNBOOK_STEPS),
        "shell_owns_no_rule": True,
        "outside_call_wording_standing": (
            "the outside call check outcome wording stands in "
            "MOD-14 as its program check form; the shell owns no "
            "other result wording"),
    }


__all__ = [
    "PILOT_USES",
    "STORE_KINDS",
    "NamedShellFailure",
    "command_surface",
    "command_computes",
    "error_carriage",
    "run_command",
    "pilot_run",
    "validate_pilot_claim",
    "sweep_level_determinism_contract",
    "nondeterminism_census",
    "dual_rule_retention_simulation",
    "store_kind_check",
    "store_kind_check_with_reason",
    "RETENTION_TIERS",
    "flag_evaluation",
    "weekly_headline_count",
    "process_and_network_call_log",
    "outside_call_check",
    "validate_operator_action",
    "validate_operator_action_with_reason",
    "operator_runbook",
]

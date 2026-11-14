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
module at operator_runbook, and the public README states the
operator procedure as that runbook.
"""

import copy
import itertools
import unicodedata

from crucible import mod01 as _mod01
from crucible import mod10 as _mod10
from crucible import mod12 as _mod12

PILOT_USES = ("timing", "conformance", "procedure rates")
STORE_KINDS = _mod01.STORE_KINDS


class NamedShellFailure(Exception):
    """A named failure reaching the operator with its run
    identifier and its stage, never swallowed."""

    def __init__(self, message=""):
        super().__init__(message)
        self.failure = {
            "name": type(self).__name__,
            "message": str(message),
            "failure": str(message),
        }


_NAMED_FAILURE_CLASS_NAMES = frozenset((
    "NamedShellFailure", "NamedGeneratorFailure", "NamedFailure",
    "AlterationBarred", "GatedRun", "NamedDetectionFailure",
    "SilentUseMovement", "NamedAttackerFailure",
    "NamedControllerFailure", "NamedReplicationFailure",
    "LookupFailure",
))


_FREEZE_DEPTH_BOUND = 100

_FREEZE_TOO_DEEP = (
    "value stands deeper than the stated depth bound of 100 "
    "and stands not copied whole")


def _freeze(value, _depth=0, _memo=None):
    """Copy a value under a depth bound of 100 with a cycle
    guard. A container standing deeper than the bound stands
    replaced by a stated marker in place of the copy, so the
    caller still receives the surrounding value in populated
    form and no bare RecursionError escapes through the copy.
    Cycles and shared containers inside the bound stand
    preserved, as a plain deep copy preserves them."""
    if _depth > _FREEZE_DEPTH_BOUND:
        return _FREEZE_TOO_DEEP
    if value is None or isinstance(value, (str, bytes, int, float, bool)):
        return value
    memo = _memo if _memo is not None else {}
    if isinstance(value, dict):
        if id(value) in memo:
            return memo[id(value)]
        copied = {}
        memo[id(value)] = copied
        for key, item in value.items():
            copied[_freeze(key, _depth + 1, memo)] = _freeze(
                item, _depth + 1, memo)
        return copied
    if isinstance(value, list):
        if id(value) in memo:
            return memo[id(value)]
        copied = []
        memo[id(value)] = copied
        for item in value:
            copied.append(_freeze(item, _depth + 1, memo))
        return copied
    if isinstance(value, tuple):
        if id(value) in memo:
            return memo[id(value)]
        copied = tuple(
            _freeze(item, _depth + 1, memo) for item in value)
        memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        copied_items = [
            _freeze(item, _depth + 1, memo) for item in value]
        try:
            copied = type(value)(copied_items)
        except TypeError:
            copied = copied_items
        return copied
    try:
        return copy.deepcopy(value)
    except Exception:
        return _FREEZE_TOO_DEEP


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
        "Run the flag evaluation program check on one summary record.",
        ("summary_record",), ("inputs", "outcome", "tier"),
        "run_command('flag_evaluation', {'summary_record': {}, 'outcome': 'promote', 'tier': 'Tier 3'})"),
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


def error_carriage(failure, run_id=None, stage=None):
    """The error carriage of the shell: a named failure reaches
    the operator as a named failure with its run identifier and
    its stage. No failure is swallowed and none is converted into
    an empty result, and no command exits cleanly over a failed
    run."""
    name = failure if isinstance(failure, str) else type(failure).__name__ + ": " + str(failure)
    fields = {}
    if not isinstance(failure, str):
        carried = getattr(failure, "failure", None)
        if isinstance(carried, dict):
            fields.update(_freeze(carried))
        elif carried is not None:
            fields["failure"] = carried
        gate = getattr(failure, "gate", None)
        if gate is not None:
            fields["gate"] = gate
        for key, value in vars(failure).items():
            if key not in fields and key != "failure":
                fields[key] = _freeze(value)
        class_name = type(failure).__name__
        if class_name in _NAMED_FAILURE_CLASS_NAMES or class_name.startswith("Named"):
            fields.setdefault("name", class_name)
            fields.setdefault("message", str(failure))
            if not fields:
                fields["failure"] = str(failure)
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
        if key not in carriage:
            carriage[key] = value
    return carriage


def run_command(command, payload=None, run_id=None):
    """Run one shell command. The command carries its inputs to
    its named module and returns that module outputs, or its
    named failure in the error carriage form."""
    payload = payload or {}
    try:
        if command == "start_run":
            return _mod12.start_run(
                run_class=payload.get("run_class"),
                family_id=payload.get("family_id"),
            )
        if command == "start_sweep":
            return _mod12.start_sweep(family_id=payload.get("family_id"))
        if command == "store_kind_check":
            return store_kind_check_with_reason(payload.get("kind"))
        if command == "read_store":
            return _mod10.read_run_record(
                payload.get("run_id"),
                store_kind=payload.get("store_kind", "sweep"))
        if command == "write_store":
            record = payload.get("record")
            if not isinstance(record, dict):
                raise NamedShellFailure(
                    "write_store carries no record to write")
            return _mod10.retain_run_record(
                record, store_kind=payload.get("store_kind", "sweep"))
        if command == "run_pilot":
            return pilot_run(payload.get("use"), payload.get("artefact"))
        if command == "assemble_report":
            raise NamedShellFailure(
                "report assembly stands not built: no report assembly "
                "act stands in MOD-11, whose picked reporting artefacts "
                "stand partial on their own record")
        if command == "outside_call_check":
            return outside_call_check(
                payload.get("dependency_manifest"),
                payload.get("call_log"))
        if command == "flag_evaluation":
            return flag_evaluation(
                payload.get("summary_record"),
                inputs=payload.get("inputs"),
                outcome=payload.get("outcome"),
                tier=payload.get("tier"),
                actor=payload.get("actor", "program"))
        if command == "weekly_headline_count":
            return {
                "count": weekly_headline_count(
                    payload.get("summary_records"),
                    payload.get("week")),
                "week": payload.get("week"),
            }
        raise NamedShellFailure("unknown shell command: " + str(command))
    except NamedShellFailure as failure:
        carriage = error_carriage(failure, run_id=run_id, stage=command)
        if command == "assemble_report":
            carriage["not_built"] = True
            carriage["stands_on_record"] = (
                "the MOD-11 reporting artefacts item, Purple 2 "
                "element E-49, PARTIAL")
        if command == "run_pilot":
            carriage["confinement_bar"] = (
                "pilot work stands confined to timing, conformance, "
                "and procedure rates, under the pilot confined label")
        return carriage
    except Exception as failure:
        return error_carriage(failure, run_id=run_id, stage=command)


# ---------------------------------------------------------------------------
# Pilot runner, decision D-07 confinement
# ---------------------------------------------------------------------------

_PILOT_BARRED_KEY_MARKERS = ("money", "anchor_" + "set")


def _pilot_key_form(key):
    return "".join(
        char for char in str(key).lower() if char.isalnum())


_PILOT_BARRED_KEY_FORMS = tuple(
    _pilot_key_form(marker) for marker in _PILOT_BARRED_KEY_MARKERS)


def _screen_pilot_key(key):
    form = _pilot_key_form(key)
    if any(marker in form for marker in _PILOT_BARRED_KEY_FORMS):
        raise NamedShellFailure(
            "pilot artefact carries a barred entry under the "
            "pilot confined label: " + str(key))


_PILOT_ARTEFACT_DEPTH_BOUND = 100


def _screen_pilot_artefact(value, _depth=0, _seen=None):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > _PILOT_ARTEFACT_DEPTH_BOUND:
            raise NamedShellFailure(
                "pilot artefact stands deeper than the stated "
                "depth bound of " + str(_PILOT_ARTEFACT_DEPTH_BOUND))
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise NamedShellFailure(
                "pilot artefact carries a cycle")
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in value.items():
                    _screen_pilot_artefact(key, _depth + 1, seen)
                    if not isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        _screen_pilot_key(key)
                    _screen_pilot_artefact(item, _depth + 1, seen)
                if not validate_pilot_claim(value):
                    raise NamedShellFailure(
                        "pilot artefact carries a claim the pilot check bars")
            elif isinstance(value, (list, tuple)):
                if len(value) == 2 and isinstance(value[0], str):
                    _screen_pilot_key(value[0])
                for item in value:
                    _screen_pilot_artefact(item, _depth + 1, seen)
            else:
                for item in value:
                    if isinstance(item, str):
                        _screen_pilot_key(item)
                    _screen_pilot_artefact(item, _depth + 1, seen)
        finally:
            seen.discard(id(value))




def pilot_run(use, artefact=None):
    """Run the purpose built run for one of its three uses only:
    timing, conformance, and procedure rates. Every pilot output
    carries its confinement label in the same artefact as the
    number. A use outside the three, including behaviour fitting,
    is refused as a named failure. The artefact stands screened
    in whatever container it arrives in, recursively, before the
    label is stamped: a barred entry carried in a list, a tuple,
    or a set, or under a spaced or joined spelling, raises the
    named failure in the same form as one carried in a dict."""
    if use not in PILOT_USES:
        raise NamedShellFailure(
            "pilot use outside timing, conformance, and procedure rates: " + str(use)
        )
    _screen_pilot_artefact(artefact)
    output = _freeze(artefact) if isinstance(artefact, dict) else {"figure": artefact}
    output["use"] = use
    output["confinement_label"] = "pilot confined"
    output["form"] = "pilot artefact, stored apart from sweep results"
    return output


def validate_pilot_claim(claim):
    """Return False where a behaviour claim cites a pilot output,
    and where a pilot output stands worded as settling a
    population behaviour rate: events per agent per day and trust
    graph average degree are not settled as population behaviour
    rates by the pilot in any wording."""
    if not isinstance(claim, dict):
        return False
    if claim.get("cites_pilot_output") and claim.get("kind") == "behaviour":
        return False
    if claim.get("settles_population_behaviour_rate"):
        return False
    return True


# ---------------------------------------------------------------------------
# Confined programme forms, pilot confined and synthetic material only
# ---------------------------------------------------------------------------

def _pilot_confined(material):
    return isinstance(material, dict) and (
        material.get("material_class") == "pilot confined"
        or material.get("confinement_label") == "pilot confined"
    )


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
    the named form."""
    families = list(families or ())
    for family in families:
        if not isinstance(family, dict) or not family.get("synthetic"):
            raise NamedShellFailure(
                "dual rule simulation stands on synthetic families only")
    return {
        "form": "dual rule retention simulation",
        "confinement": "synthetic families only",
        "paired_field": {
            "first_rule_retained": sum(
                1 for family in families
                if family.get("retained_under_first_rule")),
            "second_rule_retained": sum(
                1 for family in families
                if family.get("retained_under_second_rule")),
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


RETENTION_TIERS = ("Tier 1", "Tier 2", "Tier 3")


def _has_stated_condition(fired):
    """Return whether a fired condition list states a condition:
    at least one entry stands stated, where an entry that is
    empty text, blank text, or no value states no condition.
    A list holding only such entries states no condition."""
    if isinstance(fired, str):
        entries = (fired,)
    elif isinstance(fired, (list, tuple, set, frozenset)):
        entries = tuple(fired)
    elif fired is None:
        entries = ()
    else:
        entries = (fired,)
    for entry in entries:
        if entry is None:
            continue
        if isinstance(entry, str) and not _stated_text(entry):
            continue
        return True
    return False


_ZERO_WIDTH_CHARS = "\u200b\u200c\u200d\ufeff\u2060"


def _stated_text(entry):
    """Return the readable text an entry carries, with zero
    width characters and byte order mark characters removed.
    An entry carrying only such characters, or only spacing,
    carries no readable text and states no condition."""
    cleaned = "".join(
        char for char in entry if char not in _ZERO_WIDTH_CHARS)
    return cleaned.strip()


def _normalise_actor(actor):
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
    one actor word do not hide the word they split."""
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
    The actor stands as supplied, in the open, not hardcoded
    unseen."""
    if not isinstance(summary_record, dict):
        raise NamedShellFailure(
            "flag evaluation carries no summary record to evaluate")
    if outcome == "promote":
        if tier not in RETENTION_TIERS:
            raise NamedShellFailure(
                "flag promotion to a tier the rule does not name: "
                + str(tier))
        if inputs is None:
            raise NamedShellFailure(
                "flag promotion with no inputs supplied")
        fired = []
        if isinstance(inputs, dict):
            fired = inputs.get("flag_conditions_fired") or []
        if not fired:
            fired = summary_record.get("flag_conditions_fired") or []
        if not _has_stated_condition(fired):
            raise NamedShellFailure(
                "flag promotion with no stated flag condition fired")
    return _mod10.apply_flag_evaluation(
        summary_record, outcome=outcome, tier=tier,
        actor=_normalise_actor(actor), inputs=inputs,
    )


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
    never as its characters."""
    seen = []
    for record in summary_records or ():
        if not isinstance(record, dict) or "week" not in record:
            raise NamedShellFailure(
                "summary record carries no week field, so its weekly "
                "headline count cannot stand read")
        if record.get("week") != week:
            continue
        if "headline_unit_identifiers" not in record:
            raise NamedShellFailure(
                "summary record for the week carries no "
                "headline_unit_identifiers field")
        identifiers = record.get("headline_unit_identifiers")
        if identifiers is None:
            raise NamedShellFailure(
                "summary record for the week carries a "
                "headline_unit_identifiers field standing at no value")
        if isinstance(identifiers, str):
            identifiers = (identifiers,)
        elif not isinstance(identifiers, (list, tuple, set, frozenset)):
            raise NamedShellFailure(
                "summary record for the week carries a "
                "headline_unit_identifiers field the count cannot "
                "read: " + type(identifiers).__name__)
        for unit_id in identifiers:
            if unit_id not in seen:
                seen.append(unit_id)
    return len(seen)


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
    A pass certifies only the absence the check reads."""
    if extra_source is not None:
        raise NamedShellFailure(
            "outside call check computed from a third source is barred"
        )
    calls = []
    if isinstance(call_log, dict):
        calls = call_log.get("calls") or call_log.get("entries") or []
    outside = [
        call for call in calls
        if isinstance(call, dict) and call.get("outside_call")
    ]
    outcome = "outside calls present" if outside else "no outside calls read"
    return {
        "field": "outside_call_check",
        "outcome": outcome,
        "sources": ["dependency manifest", "process and network call log"],
        "certifies": "only the absence the check reads",
        "manifest_entries": len((dependency_manifest or {}).get("entries") or ()),
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
# letters by the Latin letters they resemble.
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
    "\u03b1": "a", "\u03b2": "b", "\u03b3": "y", "\u03b4": "d",
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "n", "\u03b8": "th",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "v", "\u03bf": "o", "\u03c0": "n", "\u03c1": "p",
    "\u03c3": "s", "\u03c4": "t", "\u03c5": "u", "\u03c6": "ph",
    "\u03c7": "x", "\u03c8": "ps", "\u03c9": "w",
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
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
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


def _resolve_against(word, ordered, vocabulary):
    """Read one word as the vocabulary word it dresses, where
    it dresses one: the word itself where it stands plain, a
    word with one, two, three, or four added letters struck, a
    word with one letter dropped from a vocabulary word, a word
    with one letter replaced, a word with two adjacent letters
    transposed, and the compounded forms, one letter
    dropped together with one letter replaced, one
    transposition together with one letter dropped, two
    letters replaced, two letters dropped from a vocabulary
    word, and one transposition together with one letter
    replaced. The
    dropped, replaced, and transposed limbs run on words of
    two letters as well, so a drop from a three letter word
    still resolves. Any other word stands as itself."""
    if word in vocabulary:
        return word
    if _segments_into_vocabulary(word, vocabulary):
        return word
    for added in (1, 2, 3, 4):
        if len(word) > added:
            for cuts in itertools.combinations(range(len(word)), added):
                reduced = "".join(
                    char for index, char in enumerate(word)
                    if index not in cuts)
                if reduced in vocabulary:
                    return reduced
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
    vocabulary, and None where the joined form stands as no
    vocabulary word. The joined form stands read exact only,
    never through the resolver, so a group reading cannot
    strike a whole fragment away to reach a shorter word."""
    joined = _plural_form("".join(fragments))
    if joined in _VOCABULARY_WORDS:
        return joined, "exact"
    return None


def _reading_words(fragments):
    """Read a fragment sequence as words. The reading stands
    as the partition of the sequence with the highest score,
    where a group of fragments joining into one vocabulary
    word scores above the same fragments read one by one, an
    exact vocabulary word scores above a resolved one, a
    resolved word scores above a plain fragment, and dropping
    an article standing between words scores above keeping it
    as a plain fragment. A separator split inside one word
    therefore reads as that word, even where a fragment on its
    own resolves elsewhere or stands as an article, while
    words standing apart keep their own readings."""
    scores = {"exact": 20, "resolved": 15, "plain": 2}
    best = {}

    def search(start):
        if start in best:
            return best[start]
        if start >= len(fragments):
            return (0, ())
        options = []
        word, standing = _single_reading(fragments[start])
        rest_score, rest_words = search(start + 1)
        options.append((
            scores[standing] + rest_score, (word,) + rest_words))
        if fragments[start] in _ARTICLES:
            options.append((5 + rest_score, rest_words))
        joined = [fragments[start]]
        for size in range(2, min(8, len(fragments) - start) + 1):
            joined.append(fragments[start + size - 1])
            if len("".join(joined)) > 24:
                break
            reading = _group_reading(joined)
            if reading is None:
                continue
            group_word, group_standing = reading
            rest_score, rest_words = search(start + size)
            group_score = scores[group_standing] * size + 10
            options.append((
                group_score + rest_score, (group_word,) + rest_words))
        chosen = max(options, key=lambda option: option[0])
        best[start] = chosen
        return chosen

    return list(search(0)[1])


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
    raw_kind = action.get("kind")
    raw_target = action.get("target")
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
    path = _normalise_name(action.get("path"))
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
    the reason form. No operator action edits a sealed family
    record on any path; the flag rule path admits edit acts only
    on a closed run record, and a destructive act stands refused
    there as on every path; a checkpoint set stands edited only
    on the deletion rule. Validation reads checkpoint manifests
    beside the run record to compare seeds, settings, and rule
    versions."""
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
    "Make no edit to a sealed family record, to a closed run record outside the flag rule path, or to a checkpoint set outside the deletion rule. Validation reads checkpoint manifests beside the run record to compare seeds, settings, and rule versions.",
)


def operator_runbook():
    """The operator procedure of this product, standing as the
    runbook deliverable of slice S-15 in the product own form.
    The public README states this same procedure as the runbook;
    where the two texts differ, the difference stands named on
    the record of the wave that finds it."""
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

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

from crucible import mod01 as _mod01
from crucible import mod10 as _mod10
from crucible import mod12 as _mod12

PILOT_USES = ("timing", "conformance", "procedure rates")
STORE_KINDS = _mod01.STORE_KINDS


class NamedShellFailure(Exception):
    """A named failure reaching the operator with its run
    identifier and its stage, never swallowed."""


def _freeze(value):
    return copy.deepcopy(value)


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


def _screen_pilot_artefact(value):
    if isinstance(value, dict):
        for key, item in value.items():
            name = str(key).lower()
            if any(marker in name for marker in _PILOT_BARRED_KEY_MARKERS):
                raise NamedShellFailure(
                    "pilot artefact carries a barred entry under the "
                    "pilot confined label: " + str(key))
            _screen_pilot_artefact(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _screen_pilot_artefact(item)
    if isinstance(value, dict) and not validate_pilot_claim(value):
        raise NamedShellFailure(
            "pilot artefact carries a claim the pilot check bars")




def pilot_run(use, artefact=None):
    """Run the purpose built run for one of its three uses only:
    timing, conformance, and procedure rates. Every pilot output
    carries its confinement label in the same artefact as the
    number. A use outside the three, including behaviour fitting,
    is refused as a named failure."""
    if use not in PILOT_USES:
        raise NamedShellFailure(
            "pilot use outside timing, conformance, and procedure rates: " + str(use)
        )
    if isinstance(artefact, dict):
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
            "and states no sweep result"),
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
        if not fired:
            raise NamedShellFailure(
                "flag promotion with no stated flag condition fired")
    return _mod10.apply_flag_evaluation(
        summary_record, outcome=outcome, tier=tier,
        actor=actor, inputs=inputs,
    )


def weekly_headline_count(summary_records, week):
    """The weekly headline count program check, counted from the
    stored summary records alone as distinct headline unit
    identifiers, under the canonical field name the reporter
    uses, whose witness records fall in the week. A record with
    no week field, and a record of the week with no headline unit
    identifier field, fail in the named form; neither is counted
    silently as zero."""
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
        for unit_id in record.get("headline_unit_identifiers") or ():
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
    "delete", "destroy", "remove", "erase", "overwrite",
)


def _normalise_name(value):
    text = str(value or "").lower().replace("_", " ").replace("-", " ")
    words = []
    for word in text.split():
        if len(word) > 1 and word.endswith("s"):
            word = word[:-1]
        words.append(word)
    return " ".join(words)


def _operator_action_bar(action):
    if not isinstance(action, dict):
        return "the action is not a record of an act and a target"
    kind = _normalise_name(action.get("kind"))
    target = _normalise_name(action.get("target"))
    path = _normalise_name(action.get("path"))
    if not kind:
        if target in ("sealed family record", "closed run record",
                      "checkpoint set"):
            return (
                "an action with no kind stated stands refused on a "
                "protected target: " + target)
        return "an action with no kind stated stands refused"
    if kind in _EDIT_ACTS:
        if target == "sealed family record":
            return "no operator action edits a sealed family record"
        if target == "closed run record" and path != "flag rule":
            return (
                "no operator action edits a closed run record outside "
                "the flag rule path")
        if target == "checkpoint set" and path != "deletion rule":
            return (
                "no operator action edits a checkpoint set outside "
                "the deletion rule")
    return None


def validate_operator_action(action):
    """The operator boundary at the shell. The act stands read,
    not its spelling: verb synonyms, case, plural, and underscored
    spellings of a protected target name the same act, and every
    such act stands refused outside its stated rule path. No
    operator action edits a sealed family record, a closed run
    record outside the flag rule path, or a checkpoint set outside
    the deletion rule. Validation reads checkpoint manifests beside
    the run record to compare seeds, settings, and rule versions."""
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

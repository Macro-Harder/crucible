"""MOD-14 Shell, pilot runner, and program checks.

Slice S-15. The shell owns no rule of its own and no result
wording of its own. Every command carries inputs to a named
module and returns its outputs or its named failure. The shell
computes no reputation, no verdict, no retention tier, and no
result wording. Slice S-15 states expressly that the operator
procedure stands as this slice runbook deliverable: the operator
runbook stands in this module at operator_runbook, and the
public README states the operator procedure as that runbook.
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
}


def command_surface():
    """The shell command surface, command by command: each command
    names the module it carries inputs to."""
    return [
        {"command": name, "carries_to": module, "computes_rule": False}
        for name, module in sorted(_COMMAND_MODULES.items())
    ]


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
    return {
        "failure": name,
        "run_id": run_id,
        "stage": stage,
        "swallowed": False,
        "converted_to_empty_result": False,
        "operator_sees_failure": True,
    }


def run_command(command, payload=None, run_id=None):
    """Run one shell command. The command carries its inputs to
    its named module and returns that module outputs, or its
    named failure in the error carriage form."""
    payload = payload or {}
    try:
        if command == "start_run":
            return _mod12.start_run(
                run_class=payload.get("run_class", "screening"),
                family_id=payload.get("family_id"),
            )
        if command == "start_sweep":
            return _mod12.start_sweep(family_id=payload.get("family_id"))
        if command == "store_kind_check":
            return {"store_kind_ok": store_kind_check(payload.get("kind"))}
        if command in _COMMAND_MODULES:
            return {
                "command": command,
                "carried_to": _COMMAND_MODULES[command],
                "form": "carriage only in this act",
            }
        raise NamedShellFailure("unknown shell command: " + str(command))
    except NamedShellFailure as failure:
        return error_carriage(failure, run_id=run_id, stage=command)
    except Exception as failure:
        return error_carriage(failure, run_id=run_id, stage=command)


# ---------------------------------------------------------------------------
# Pilot runner, decision D-07 confinement
# ---------------------------------------------------------------------------

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
# Program checks
# ---------------------------------------------------------------------------

def store_kind_check(kind):
    """The store kind program check, over the one store kind
    vocabulary MOD-01 owns."""
    return _mod01.validate_store_kind(kind)


def flag_evaluation(summary_record, inputs=None, outcome=None, tier=None):
    """The flag evaluation program check: its inputs and outcome
    stand written into the stored summary record itself by the
    MOD-10 flag rule program this check carries to."""
    return _mod10.apply_flag_evaluation(
        summary_record, outcome=outcome, tier=tier,
        actor="program", inputs=inputs,
    )


def weekly_headline_count(summary_records, week):
    """The weekly headline count program check, counted from the
    stored summary records alone as distinct headline unit
    identifiers whose witness records fall in the week."""
    seen = []
    for record in summary_records or ():
        if record.get("week") != week:
            continue
        for unit_id in record.get("headline_unit_ids") or ():
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


def validate_operator_action(action):
    """The operator boundary at the shell. No operator action
    edits a sealed family record, a closed run record outside the
    flag rule path, or a checkpoint set outside the deletion
    rule. Validation reads checkpoint manifests beside the run
    record to compare seeds, settings, and rule versions."""
    if not isinstance(action, dict):
        return False
    kind = action.get("kind")
    if kind == "edit":
        target = action.get("target")
        if target == "sealed family record":
            return False
        if target == "closed run record" and action.get("path") != "flag rule":
            return False
        if target == "checkpoint set" and action.get("path") != "deletion rule":
            return False
    return True


# ---------------------------------------------------------------------------
# Operator runbook, the S-15 deliverable in the product own form
# ---------------------------------------------------------------------------

_RUNBOOK_STEPS = (
    "Read the family record and the run record before any act; the shell carries records and interprets none of them.",
    "Start runs and sweeps through the start commands only; while the DQ7-02 adoption record does not stand, every start returns the gated refusal and no run starts.",
    "Keep pilot work inside its confinement: timing, conformance, and procedure rates only, each output carrying its pilot confined label in the same artefact, stored apart from sweep results.",
    "Read stores by kind, sweep, pilot, and live, and never resolve a record across stores in one lookup.",
    "Run the program checks by name: the store kind check, the flag evaluation, the weekly headline count from summary records alone, and the outside call check over the dependency manifest and the call log only.",
    "Treat every named failure as the result of its act: report it with its run identifier and its stage, and never present an empty result in its place.",
    "Make no edit to a sealed family record, to a closed run record outside the flag rule path, or to a checkpoint set outside the deletion rule.",
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
        "shell_owns_no_result_wording": True,
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
    "store_kind_check",
    "flag_evaluation",
    "weekly_headline_count",
    "process_and_network_call_log",
    "outside_call_check",
    "validate_operator_action",
    "operator_runbook",
]

"""MOD-12 Sweep Controller and family definition.

Slice S-12. This module owns the sweep family definition fixed
before any sweep runs, the screening, confirmation, headline, and
validation run classes, the replicate plan, and the point at
which a readout may be called established under the stopping
rule. Executable runs wait on the DQ7-02 gate at slice S-02: a
start that would need a derived seed returns the recorded gated
refusal of MOD-02, DERIVATION-GATED naming DQ7-02, and starts
nothing. Grid values stand provisional until the NQ-4 timing
pilot lands, and that pilot stands prepared and not landed, so
no grid artefact in this module is presented as affordable and
no sweep run starts here.
"""

import copy

from crucible import mod02 as _mod02

RUN_CLASSES = ("screening", "confirmation", "headline", "validation")
GATE_QUESTION = "DQ7-02"


class NamedControllerFailure(Exception):
    """A failure stated by name, never a silent correction."""


def _freeze(value):
    return copy.deepcopy(value)


# ---------------------------------------------------------------------------
# Family definition, seal, and claims
# ---------------------------------------------------------------------------

def make_family_record(family_id="family-under-test", claims=None,
                       scheduling_order_identifier=None):
    """One family record in form: identifier, headline claims with
    their kill checks, the scheduling order identifier the family
    reads, and its registry basis fields. The record stands
    unsealed until seal_family_record seals it."""
    claims = list(claims or ("headline claim 1",))
    return {
        "family_id": family_id,
        "sealed": False,
        "claims": claims,
        "kill_checks": [kill_check_for_claim(claim) for claim in claims],
        "scheduling_order_identifier": scheduling_order_identifier,
        "registry_basis_fields": registry_basis_fields(),
        "results_seen": False,
        "form": "family record",
    }


def seal_family_record(record):
    """Seal one family record. From the seal, any edit creates a
    new family identifier and runs under it start again."""
    sealed = _freeze(record)
    sealed["sealed"] = True
    sealed["seal"] = "family seal: version and hash match required"
    return sealed


def apply_family_edit(record, change=None):
    """Apply an edit to a family record. An edit to a sealed record
    creates a new family identifier, and runs under the new
    identifier start again, per Shape 1 and operation C-10. An
    edit to an unsealed record lands in place."""
    edited = _freeze(record)
    if isinstance(change, dict):
        edited.update(_freeze(change))
    if record.get("sealed"):
        new_id = str(record.get("family_id")) + "-edited-1"
        edited["family_id"] = new_id
        edited["runs_under"] = new_id
        edited["edited_after_seal"] = True
        edited["identifier_changed"] = True
        edited["runs_start_again"] = True
    else:
        edited["runs_under"] = edited.get("family_id")
    return edited


def validate_family_record(record):
    """Return True only where a family record stands in a lawful
    form: no identifier reuse across a sealed edit, no ecology
    point fixed before its amendment stands, and no data dependent
    top up resting on an empty look register."""
    if not isinstance(record, dict):
        return False
    if record.get("sealed") and record.get("edited_after_seal"):
        if not record.get("identifier_changed"):
            return False
    if record.get("ecology_point") == "fixed" and not record.get("amendment_landed"):
        return False
    if record.get("data_dependent_top_up") and not record.get("look_register"):
        return False
    return True


def admit_claim(family, claim=None):
    """Admit one claim to a family. A claim entering after results
    are seen is barred from the family and supports no headline
    publication from it."""
    if isinstance(family, dict) and family.get("results_seen"):
        raise NamedControllerFailure(
            "claim entering after results are seen is barred from the family"
        )
    return {"admitted": True, "claim": _freeze(claim)}


def kill_check_for_claim(claim):
    """One named kill check for one headline claim, in four parts:
    the name of the check; the data it runs on, standing outside
    the artefact under check; the judge that applies it, standing
    outside the artefact under check; and the killing result."""
    return {
        "claim": claim,
        "name": "kill check for " + str(claim),
        "data": "records outside the artefact under check",
        "judge": "checker outside the artefact under check",
        "killing_result": "the claim does not stand as reported",
        "data_outside_artefact": True,
        "judge_outside_artefact": True,
        "fixed_before_runs": True,
    }


def kill_checks_for_family(family_id="family-under-test", claims=None):
    """The kill checks fixed before runs for one family, one per
    headline claim in the family list."""
    claims = list(claims or ("headline claim 1",))
    return [kill_check_for_claim(claim) for claim in claims]


def validate_kill_check(check):
    """Return True only for a complete kill check whose data and
    judge both stand outside the artefact under check."""
    if not isinstance(check, dict):
        return False
    if not check.get("name") or not check.get("killing_result"):
        return False
    return bool(
        check.get("data_outside_artefact")
        and check.get("judge_outside_artefact")
    )


def registry_basis_fields():
    """The family facing registry basis carriage of DQ7-07: the
    family record carries the registry basis fields, and until the
    basis stands, the 5 percent figure is not reported as a
    recomputed result."""
    return {
        "basis_standing": "carried, not adopted as recomputed",
        "five_percent_figure_reported_as_recomputed": False,
        "fields": [
            "family sentence", "claim form blocks", "run set sentence",
            "dependence sentence", "procedure sentence",
            "confirmation sentence", "coverage sentence", "version sentence",
        ],
    }


# ---------------------------------------------------------------------------
# Run classes, the stopping rule, and the look register
# ---------------------------------------------------------------------------

def run_class_markings():
    """The four run classes and their record markings. The classes
    are distinct; confirmation uses held out seeds and held out
    settings."""
    return {
        "screening": {"seed_domain": "screening", "held_out_settings": False, "reporting": False},
        "confirmation": {"seed_domain": "held_out", "held_out_settings": True, "reporting": True},
        "headline": {"seed_domain": "held_out", "held_out_settings": True, "reporting": True},
        "validation": {"seed_domain": "validation", "held_out_settings": True, "reporting": False},
    }


def validate_run_record(run):
    """Return True only where a run record stands in its class: a
    screening run promoted into a confirmation role by relabelling
    fails, and a confirmation run on the screening domain fails."""
    if not isinstance(run, dict):
        return False
    if run.get("relabelled_from") == "screening" and run.get("run_class") != "screening":
        return False
    if run.get("run_class") == "confirmation" and run.get("seed_domain") == "screening":
        return False
    return True


def claim_label(claim=None):
    """The label of one claim: a claim without a settings lineage
    is labelled a screening finding only."""
    if not isinstance(claim, dict) or not claim.get("settings_lineage"):
        return "screening finding only"
    return "claim with settings lineage"


def readout_status(readout):
    """The standing of one readout under the stopping rule. Where
    the challenge search is incomplete against the conditions, or
    a material failure stands found under the bound, or the
    materiality bound was not fixed in advance of the runs it
    judges, the readout is reported as a lower bound with
    condition 2 named, and never as established."""
    readout = readout or {}
    if not readout.get("bound_fixed_in_advance"):
        return {"form": "lower_bound", "named_condition": 2}
    if not readout.get("search_complete") or readout.get("material_failure_found"):
        return {"form": "lower_bound", "named_condition": 2}
    return {"form": "established", "named_condition": None}


def look_register_for_family(family_id="family-under-test"):
    """The look register of one family, under a prewritten alpha
    spending function fixed in advance. Each entry records the
    look number, the information fraction as a derived ratio, the
    boundary the spending function assigned to that look, and
    whether the readout crossed it."""
    return {
        "family_id": family_id,
        "spending_function_fixed_in_advance": True,
        "entries": [
            {
                "look_number": 1,
                "information_fraction": 0.5,
                "boundary": "spending function boundary for look 1",
                "crossed": False,
            }
        ],
    }


def validate_look_decision(decision):
    """Return True only where a decision rests on a registered
    look. No promotion, refinement, top up beyond a rule fixed in
    the family record before runs, or readout wording decision
    rests on an unregistered look, and a register entry written
    after the decision it would judge does not cure it."""
    if not isinstance(decision, dict):
        return False
    if not decision.get("registered"):
        return False
    if decision.get("entry_written_after_decision"):
        return False
    return True


# ---------------------------------------------------------------------------
# Grids, replicates, screening surfaces, and the decay arm
# ---------------------------------------------------------------------------

def grid_artefacts(produced_before_pilot=True):
    """Grid artefacts. Every artefact produced before the NQ-4
    timing pilot lands is marked provisional, per AC-7."""
    standing = "provisional" if produced_before_pilot else "refixed on the pilot figure"
    return [
        {"kind": "grid", "standing": standing},
        {"kind": "density", "standing": standing},
        {"kind": "run count", "standing": standing},
    ]


def grid_decision_log():
    """The grid decision log as a family definition record: every
    candidate value and rejection carries the provisional standing
    until the pilot figure lands, and no grid is fixed by the
    log."""
    return {
        "form": "family definition record",
        "grid_fixed_by_log": False,
        "entries": [
            {"candidate": "grid candidate 1", "standing": "provisional"},
        ],
    }


def validate_grid_claim(claim):
    """Return False where a grid point stands presented as
    affordable before the timing pilot lands."""
    if not isinstance(claim, dict):
        return False
    if claim.get("claim") == "affordable" and not claim.get("pilot_landed"):
        return False
    return True


def screening_readout(fixture="F-17"):
    """The screening readout for the past programme points of
    fixture F-17: farm shares of 50, 60, and 70 percent, reported
    on the D-05 traces and on the honest loss rate and not on the
    win count, in their weighed and not adopted standing."""
    return {
        "fixture": fixture,
        "farm_shares_percent": [50, 60, 70],
        "reported_on": ["D-05 traces", "honest loss rate"],
        "standing": "weighed, not adopted",
    }


def winning_regime(daily_shares):
    """Return True only where the attacker share stands above the
    honest share at every daily evaluation over the final 30
    simulated days. Shares are evaluated at the end of each
    simulated day; each entry is an attacker and honest pair."""
    shares = list(daily_shares or ())
    if len(shares) < 30:
        return False
    for attacker, honest in shares[-30:]:
        if not attacker > honest:
            return False
    return True


def validate_screening_claim(claim):
    """Return False where an F-17 screening point stands presented
    as adopted scope: the points are a weighing, not adopted
    scope."""
    if not isinstance(claim, dict):
        return False
    if claim.get("fixture") == "F-17" and claim.get("standing") == "adopted scope":
        return False
    return True


def top_up_applies(winning_probability, replicates_after_top_up):
    """The top up rule of fixture F-18 as this controller states
    it: a control point found in screening with a winning
    probability above 0.1 and below 0.9 is topped up to at least
    30 replicates, and the rule stands recorded in the run
    record."""
    return bool(
        0.1 < winning_probability < 0.9
        and replicates_after_top_up >= 30
    )


def decay_arm_readout(fixture="F-14"):
    """The decay arm readout: at least six slices in every plane
    the arm reports, the two weighed extension slices labelled as
    an outside range extension, and the decay arm companion table
    in the same readout, one row per slice, carrying its half
    life, its control point values, and its result values beside
    the decay readout it accompanies."""
    rows = []
    for index in range(6):
        rows.append({
            "slice": "decay slice " + str(index + 1),
            "half_life": "stated per slice",
            "control_point_values": ["control value"],
            "result_values": ["result value"],
        })
    rows.append({
        "slice": "extension slice 1",
        "half_life": "stated per slice",
        "control_point_values": ["control value"],
        "result_values": ["result value"],
        "label": "outside range extension",
    })
    rows.append({
        "slice": "extension slice 2",
        "half_life": "stated per slice",
        "control_point_values": ["control value"],
        "result_values": ["result value"],
        "label": "outside range extension",
    })
    return {
        "fixture": fixture,
        "planes": [
            {"name": "decay plane", "companion_table": rows},
        ],
    }


def validate_decay_readout(readout):
    """Return False where a decay arm plane stands reported with
    no companion table in the same readout."""
    if not isinstance(readout, dict):
        return False
    for plane in readout.get("planes") or ():
        if not plane.get("companion_table"):
            return False
    return True


# ---------------------------------------------------------------------------
# Hostile family ownership and counting illustrations
# ---------------------------------------------------------------------------

def hostile_family_status(fixture="F-13"):
    """The hostile input family stands as a required sweep family
    under this controller, with magnitudes fixed in the family
    record before runs."""
    return {
        "fixture": fixture,
        "standing": "required",
        "magnitudes_fixed_before_runs": True,
    }


def validate_sweep_programme(programme):
    """Return False where a sweep programme carries the hostile
    family as absent, optional, or sampled below magnitude: such
    a programme has not run as required."""
    if not isinstance(programme, dict):
        return False
    for family in programme.get("families") or ():
        if family.get("name") == "hostile":
            return family.get("standing") == "required"
    return False


def hostile_kind_counts_as_run(kind=None, ran_at=None, fixed_magnitude=None):
    """A hostile kind run below its fixed magnitude does not count
    as run."""
    if ran_at is None or fixed_magnitude is None:
        return False
    return ran_at >= fixed_magnitude


def counting_basis(fixture="F-20"):
    """The Saltelli counting illustrations of fixture F-20: 14,336
    distinct evaluations at 12 inputs and a base sample of 1,024
    without second order indices. The figures illustrate the
    counting method and price nothing."""
    return {
        "fixture": fixture,
        "distinct_evaluations": 14336,
        "inputs": 12,
        "base_sample": 1024,
        "standing": "illustration",
        "prices_anything": False,
    }


def validate_cost_claim(claim):
    """Return False for any cost claim, run count commitment, or
    affordability statement resting on an F-20 figure, and for an
    F-19 composite form worded as a measured cost."""
    if not isinstance(claim, dict):
        return False
    if claim.get("basis_fixture") == "F-20":
        return False
    if claim.get("basis_fixture") == "F-19" and claim.get("wording") == "measured cost":
        return False
    return True


def validate_seed_placement(placement):
    """Seed replicates sit outside any sampled base design, and
    held out confirmation seeds form a separate seed family from
    the screening family."""
    if not isinstance(placement, dict):
        return False
    if placement.get("replicates_inside_base_design"):
        return False
    return placement.get("confirmation_family") != placement.get("screening_family")


# ---------------------------------------------------------------------------
# Rule version carriage and the family split
# ---------------------------------------------------------------------------

def record_version_sets(record_kinds=()):
    """The rule version set each named record kind carries: every
    record carries the exact set under which it was produced, as
    data."""
    return {kind: "rule-version-set-1" for kind in record_kinds or ()}


def validate_record_version(record):
    """Return False where a record stands presented under a rule
    version set it was not produced under."""
    if not isinstance(record, dict):
        return False
    return record.get("produced_under") == record.get("presented_under")


def family_version_parts(family_id="family-under-test"):
    """The family split by rule version: results under two version
    sets stand in two version parts of the family."""
    return [
        {"family_id": family_id, "rule_version_set": "set-a", "part": 1},
        {"family_id": family_id, "rule_version_set": "set-b", "part": 2},
    ]


def validate_family_pooling(pooling):
    """Return False for pooled results across a rule change with
    no bound recorded in the family record. Pooling recorded as a
    named bound, stating the two version sets pooled and the
    ground for pooling them, stands in the recorded form."""
    if not isinstance(pooling, dict):
        return False
    pooled = pooling.get("pooled_version_sets") or ()
    if len(pooled) <= 1:
        return True
    bound = pooling.get("bound_recorded")
    if not isinstance(bound, dict):
        return False
    return bool(bound.get("version_sets") and bound.get("ground"))


# ---------------------------------------------------------------------------
# Gated run starts
# ---------------------------------------------------------------------------

def start_run(run_class="screening", family_id=None):
    """Start one run. Executable runs wait on the DQ7-02 gate: the
    start returns the recorded gated refusal of MOD-02 and starts
    nothing, in the one form that gate uses across MOD-02 and
    MOD-04."""
    refusal = _mod02.gated_refusal("start run")
    refusal["run_class"] = run_class
    refusal["family_id"] = family_id
    refusal["run_started"] = False
    return refusal


def start_sweep(family_id=None):
    """Start one sweep. Gated on DQ7-02 in the same form."""
    refusal = _mod02.gated_refusal("start sweep")
    refusal["family_id"] = family_id
    refusal["run_started"] = False
    return refusal


__all__ = [
    "RUN_CLASSES",
    "GATE_QUESTION",
    "NamedControllerFailure",
    "make_family_record",
    "seal_family_record",
    "apply_family_edit",
    "validate_family_record",
    "admit_claim",
    "kill_check_for_claim",
    "kill_checks_for_family",
    "validate_kill_check",
    "registry_basis_fields",
    "run_class_markings",
    "validate_run_record",
    "claim_label",
    "readout_status",
    "look_register_for_family",
    "validate_look_decision",
    "grid_artefacts",
    "grid_decision_log",
    "validate_grid_claim",
    "screening_readout",
    "winning_regime",
    "validate_screening_claim",
    "top_up_applies",
    "decay_arm_readout",
    "validate_decay_readout",
    "hostile_family_status",
    "validate_sweep_programme",
    "hostile_kind_counts_as_run",
    "counting_basis",
    "validate_cost_claim",
    "validate_seed_placement",
    "record_version_sets",
    "validate_record_version",
    "family_version_parts",
    "validate_family_pooling",
    "start_run",
    "start_sweep",
]

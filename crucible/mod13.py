"""MOD-13 Replication Checker and scoring interface.

Slice S-14. This module owns exact replay checks inside one
implementation, the distributional equivalence comparison where
one is commissioned, and the Contract F scoring counterpart, with
the Scoring Harness placed outside the run boundary inside this
slice packaging and never inside MOD-08. While open point OP-24
stands PARTIAL, an exact replay check here claims record level
and verdict level equality only; it claims no state hash
equality, and acceptance criterion AC-1 stands unimplementable
in its state hash limb at this locus. The detection part of a
resume comparison stands compared at the decision record two
points only: on resume, at the first verdict state the resumed
run produces, and again at run close. No third comparison point
stands in this module.
"""

import copy

from crucible import mod01 as _mod01

DETECTION_COMPARISON_POINTS = (
    "first verdict state after resume",
    "run close",
)
STANDARDS = ("exact replay alone", "distributional equivalence")
OP20_QUANTITIES = (
    "confidence interval method",
    "numeric equivalence margin",
    "named two sample distributional test",
)


class NamedReplicationFailure(Exception):
    """A failure stated by name, never a silent gap."""


def _freeze(value):
    return copy.deepcopy(value)


def ac1_field_list():
    """The AC-1 state hash field list and its order, as MOD-01
    carries them. This checker pins the list and the order only,
    while OP-24 stands open in part."""
    return list(_mod01.state_hash_field_list())


# ---------------------------------------------------------------------------
# Exact replay, AC-1
# ---------------------------------------------------------------------------

def replay_check(first, second):
    """Compare two runs over the AC-1 field list, field for field
    in list order, over the run fact values each run carries under
    those field names. An identical headline unit stands required
    beside the field agreement. Any difference marks the run non
    deterministic. No byte level hash equality stands claimed
    across independent renderings, and no completeness stands
    claimed over the detection state: summary record fields
    written or amended after run close stand outside the list,
    because the comparison is a statement about end of run
    state."""
    fields = ac1_field_list()
    differing = []
    for field in fields:
        if (first or {}).get(field) != (second or {}).get(field):
            differing.append(field)
    unit_differs = (first or {}).get("headline_unit") != (second or {}).get("headline_unit")
    if unit_differs:
        differing.append("headline_unit")
    deterministic = not differing
    return {
        "field_list": fields,
        "order": list(fields),
        "differing_fields": differing,
        "identical_headline_unit": not unit_differs,
        "deterministic": deterministic,
        "marked_non_deterministic": not deterministic,
        "hash_equality_claimed": False,
        "detection_state_completeness_claimed": False,
    }


def ac1_check(run_facts):
    """The AC-1 check in its pinned form: the field list and its
    order, with every hashed value that has no plan stated
    canonical form carried as HASH-VALUE-BARRED and entering no
    hash equality claim."""
    fields = ac1_field_list()
    values = {}
    for field in fields:
        if _mod01.canonical_form_for_field(field) is None:
            values[field] = "HASH-VALUE-BARRED"
        else:
            values[field] = (run_facts or {}).get(field)
    return {
        "field_list": fields,
        "order": list(fields),
        "values": values,
        "hash_equality_claimed": False,
        "pins": "field list and order only",
    }


def validate_replay_claim(claim):
    """Return False for any replay claim that asserts byte level
    hash equality while OP-24 stands open in part, or completeness
    over the detection state."""
    if not isinstance(claim, dict):
        return False
    if claim.get("hash_equality_claimed"):
        return False
    if claim.get("detection_state_completeness_claimed"):
        return False
    return True


# ---------------------------------------------------------------------------
# Non deterministic consequences
# ---------------------------------------------------------------------------

NON_DETERMINISTIC_BARRED_USES = (
    "witness", "headline support", "confirmation support",
)
NON_DETERMINISTIC_PERMITTED_USES = (
    "screening observation", "pilot timing", "pilot cost",
)


def use_stands_for_marked_run(use, marked_non_deterministic=True,
                              labelled_screening=False):
    """Return True only where a use of a run marked non
    deterministic stands permitted: the run is barred from
    witness, headline support, and confirmation support; it may
    still feed a screening observation labelled as a screening
    observation, and a timing or cost figure under the pilot
    confinement, and no other use."""
    if not marked_non_deterministic:
        return True
    if use in NON_DETERMINISTIC_BARRED_USES:
        return False
    if use == "screening observation":
        return bool(labelled_screening)
    if use in NON_DETERMINISTIC_PERMITTED_USES:
        return True
    return False


# ---------------------------------------------------------------------------
# Resume equality, AC-2, with the detection part at two points only
# ---------------------------------------------------------------------------

def detection_comparison_points():
    """The two points at which the detection part of a resume
    comparison runs, and no others: on resume at the first
    verdict state the resumed run produces, and again at run
    close. The daily checkpoint position stands scoped to the
    non detection state."""
    return list(DETECTION_COMPARISON_POINTS)


def resume_check(original, resumed):
    """Compare a resumed run with the uninterrupted run inside the
    stated scope: the same state on every part of the non
    detection state, over the AC-1 field list with the detection
    state outside it, and the detection part compared at verdict
    level only, at the two points detection_comparison_points
    names. A resume check failure promotes the run to full
    retention and bars its use as a witness until the difference
    is explained, and records the first divergence."""
    fields = ac1_field_list()
    differing = []
    for field in fields:
        if (original or {}).get(field) != (resumed or {}).get(field):
            differing.append(field)
    verdict_points = detection_comparison_points()
    verdict_differing = []
    original_verdicts = (original or {}).get("detection_verdicts") or {}
    resumed_verdicts = (resumed or {}).get("detection_verdicts") or {}
    for point in verdict_points:
        if original_verdicts.get(point) != resumed_verdicts.get(point):
            verdict_differing.append(point)
    failed = bool(differing or verdict_differing)
    first = (differing + verdict_differing)[0] if failed else None
    divergence_record = None
    if failed:
        divergence_record = {
            "field": first,
            "tick": (resumed or {}).get("tick"),
            "day": (resumed or {}).get("simulated_day"),
            "agent_identifier": (resumed or {}).get("agent_identifier"),
            "values_compared": [
                (original or {}).get(first) if first in differing else original_verdicts.get(first),
                (resumed or {}).get(first) if first in differing else resumed_verdicts.get(first),
            ],
            "hash_limb_ran": False,
            "compared_form": "record level and verdict level values, no hash equality",
        }
    return {
        "equal_in_scope": not failed,
        "scope": "non detection state, plus detection verdicts at two points only",
        "differing_fields": differing,
        "first_divergence": first,
        "divergence_record": divergence_record,
        "detection_comparison_points": verdict_points,
        "detection_scope": "verdict level only",
        "promoted_to_full_retention": failed,
        "witness_use_barred": failed,
    }


def validate_resume_claim(claim):
    """Return False for any resume equality claim for the
    detection part in a form wider than verdict level, or at any
    point beyond the two named points, in any artefact."""
    if not isinstance(claim, dict):
        return False
    if claim.get("detection_scope") not in (None, "verdict level only"):
        return False
    points = claim.get("detection_comparison_points")
    if points is not None and list(points) != list(DETECTION_COMPARISON_POINTS):
        return False
    return True


# ---------------------------------------------------------------------------
# Replication verdicts, Contract J, and the probe
# ---------------------------------------------------------------------------

def verdict_record(claim_id, standard="exact replay alone", outcome="rests"):
    """One ReplicationVerdictRecord for one claim, holding the
    claim identifier, the standard applied, and the rests or does
    not rest outcome. A record naming the distributional standard
    while the OP-20 quantities stand unfixed does not stand."""
    if standard not in STANDARDS:
        raise NamedReplicationFailure("unknown replication standard: " + str(standard))
    if outcome not in ("rests", "does not rest"):
        raise NamedReplicationFailure("unknown verdict outcome: " + str(outcome))
    record = {
        "claim_identifier": claim_id,
        "standard_applied": standard,
        "outcome": outcome,
        "quantities": None,
    }
    if not validate_verdict_record(record):
        raise NamedReplicationFailure(
            "verdict record naming the distributional standard while the OP-20 quantities stand unfixed"
        )
    return record


def validate_verdict_record(record):
    """Return True only for a lawful verdict record. While the
    OP-20 quantities stand unfixed, no record naming the
    distributional equivalence standard stands."""
    if not isinstance(record, dict):
        return False
    if not record.get("claim_identifier"):
        return False
    if record.get("outcome") not in ("rests", "does not rest"):
        return False
    if record.get("standard_applied") == "distributional equivalence":
        return False
    return record.get("standard_applied") == "exact replay alone"


def publishable_on_replication(claim, verdict):
    """Return True only where the Reporter may publish a claim as
    resting on replication: a verdict record for that claim must
    stand, with the outcome rests."""
    if not isinstance(verdict, dict):
        return False
    if verdict.get("claim_identifier") != (claim or {}).get("claim_identifier"):
        return False
    if not validate_verdict_record(verdict):
        return False
    return verdict.get("outcome") == "rests"


def probe_record(scenario="headline scenario"):
    """The replication probe record for one scenario: the probe is
    scoped as a probe of specification completeness with a
    disagreement catalogue as its deliverable, not as a full
    second implementation. The catalogue stands carried with its
    field list open inside OP-20, in gated form."""
    return {
        "scenario": scenario,
        "scope": "probe of specification completeness",
        "deliverable": "disagreement catalogue",
        "full_second_implementation": False,
        "catalogue": {
            "form": "DisagreementCatalogue",
            "field_list": "open inside OP-20",
            "standing": "gated, never passed, until the field list stands fixed",
        },
        "margin_or_method_presented_as_settled": False,
    }


def validate_probe_claim(claim):
    """Return False where a headline claim quotes a margin or a
    method as settled before the family record fixes it, or where
    a catalogue stands presented as a delivered form with a
    settled field list."""
    if not isinstance(claim, dict):
        return False
    if claim.get("margin_or_method_presented_as_settled"):
        return False
    if claim.get("catalogue_presented_as_settled"):
        return False
    return True


# ---------------------------------------------------------------------------
# Scoring harness separation, Contract F
# ---------------------------------------------------------------------------

SCORING_SEPARATIONS = ("authorship", "knowledge", "record separation")


def scoring_harness_position():
    """The Scoring Harness sits outside the run boundary, inside
    this slice packaging, and never inside MOD-08. Scoring
    consumes records after the run and returns no value into the
    run."""
    return {
        "position": "outside the run boundary",
        "packaging": "MOD-13",
        "inside_detection_module": False,
        "consumes": "records after the run",
        "value_returned_into_run": None,
    }


def score_detection_outputs(outputs, authored_by=None, knowledge=None,
                            records_position=None):
    """Score retained DetectionOutput records after a run, under
    the three separations. The record states who authored the
    profiles, what they could know, and where the records sit, as
    record properties. While OP-16 stands open, no score stands
    reported as a pass or a fail: outputs carry their profile
    bound label in carriage form."""
    return {
        "outputs_scored": len(list(outputs or ())),
        "separations": {
            "authorship": authored_by or "profile authors, named on the record",
            "knowledge": knowledge or "no ground truth and no membership",
            "record separation": records_position or "records held outside the run",
        },
        "inside_run_boundary": False,
        "value_returned_into_run": None,
        "score_reported_as": "neither pass nor fail, OP-16 open",
        "profile_bound_label": "carriage form, value set open at OP-16",
    }


def validate_scoring_record(record):
    """Return True only for a scoring record standing outside the
    run boundary under all three separations, returning no value
    into the run."""
    if not isinstance(record, dict):
        return False
    if record.get("inside_run_boundary"):
        return False
    if record.get("value_returned_into_run") is not None:
        return False
    separations = record.get("separations") or {}
    return all(separations.get(name) for name in SCORING_SEPARATIONS)


# ---------------------------------------------------------------------------
# Witness rerun and history extension, operations C-04 and C-05
# ---------------------------------------------------------------------------

def witness_rerun(original, rule_set_version=None):
    """A witness rerun under a later rule set: a new run linked to
    the original, carrying the rule set version identity it ran
    under, read as a report of the difference between two rule
    sets and nothing more. The original result, the original run
    record, and the original witness standing stand untouched."""
    rerun = {
        "run_id": str((original or {}).get("run_id")) + "-rerun",
        "linked_to": (original or {}).get("run_id"),
        "rule_set_version": rule_set_version,
        "original_rule_set_version": (original or {}).get("rule_set_version"),
        "form": "witness rerun",
        "reading": "difference between two rule sets only",
        "verdicts_transferred": False,
    }
    return rerun


def validate_rerun_reading(reading):
    """Return False where a rerun stands read as the corrected
    version of the older record, or where it overwrites the
    original result, record, or standing."""
    if not isinstance(reading, dict):
        return False
    if reading.get("read_as") == "corrected version of the original":
        return False
    if reading.get("overwrites_original"):
        return False
    return reading.get("read_as") in (None, "difference between two rule sets only")


def extend_history(history, segment):
    """Extend a history past its first horizon: the extension
    appends a new linked segment, linked by run identifier and
    segment order, under the same rule set version as the segment
    it extends, rewriting no part of the segment it extends. The
    seed derivation limb of an extension stands gated on DQ7-02
    wherever it would consume derived seeds, and stands in no
    part of this act."""
    segments = [_freeze(item) for item in (history or ())]
    if not segments:
        raise NamedReplicationFailure("a history extension extends an existing segment")
    first = segments[0]
    appended = _freeze(segment)
    appended["linked_run"] = first.get("run_id")
    appended["segment_order"] = len(segments) + 1
    appended["rule_set_version"] = first.get("rule_set_version")
    return segments + [appended]


def daily_aggregate_form():
    """The daily aggregate form, identical across horizons and
    carrying no horizon field: the aggregates stay horizon
    neutral."""
    return [
        "run_id", "simulated_day", "joint_outcome_components_per_viewer",
        "honest_share", "gate_passing_shares",
    ]


def validate_aggregate_form(form):
    """Return False where an aggregate form carries a horizon
    field or changes meaning with the horizon."""
    if not isinstance(form, (list, tuple)):
        return False
    return "horizon" not in form and list(form) == daily_aggregate_form()


__all__ = [
    "DETECTION_COMPARISON_POINTS",
    "STANDARDS",
    "OP20_QUANTITIES",
    "NamedReplicationFailure",
    "ac1_field_list",
    "replay_check",
    "ac1_check",
    "validate_replay_claim",
    "NON_DETERMINISTIC_BARRED_USES",
    "NON_DETERMINISTIC_PERMITTED_USES",
    "use_stands_for_marked_run",
    "detection_comparison_points",
    "resume_check",
    "validate_resume_claim",
    "verdict_record",
    "validate_verdict_record",
    "publishable_on_replication",
    "probe_record",
    "validate_probe_claim",
    "SCORING_SEPARATIONS",
    "scoring_harness_position",
    "score_detection_outputs",
    "validate_scoring_record",
    "witness_rerun",
    "validate_rerun_reading",
    "extend_history",
    "daily_aggregate_form",
    "validate_aggregate_form",
]

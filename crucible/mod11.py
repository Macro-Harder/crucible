"""MOD-11 Reporter and family registry.

Slice S-13. The Reporter reads retained records only, and nothing
inside a run. It builds headline result units in the closed Shape
15 form, envelope statements, transition and crossover wording,
the weekly container under decision D-12, and the SweepFamily
Registry under its registrar duty. A headline unit stands built
only from retained records that resolve in one lookup, and its
provenance lives inside the unit itself.

The weekly cap stands at 25 whole headline units in the weekly
container. A unit beyond the cap stands held: neither refused nor
carried silently. A held unit stands reported as held in the
container record of its week and stands released into the next
weekly container in arrival order.
"""
import copy

from crucible import mod01
from crucible import mod10

HEADLINE_UNIT_FIELDS = mod01.form_fields("16")
REGISTRY_FIELDS = mod01.form_fields("22")

RETIREMENT_CHECKS = tuple("T-%02d" % n for n in range(1, 16))

WEEKLY_CAP = 25

AXES = ("farm size", "patience", "external work issuance")

F01_UNIT_MARK = "W-CENTRE-ONLY"

_F01_VERDICTS = {}
for _check in ("T-01", "T-09", "T-12"):
    _F01_VERDICTS[_check] = "passed"
for _check in ("T-02", "T-03", "T-04", "T-05", "T-06", "T-07",
               "T-08", "T-10", "T-11"):
    _F01_VERDICTS[_check] = "failed"
for _check in ("T-13", "T-14", "T-15"):
    _F01_VERDICTS[_check] = "not applicable"

_EX01_VERDICTS = {}
for _check in ("T-01", "T-02", "T-03", "T-05", "T-07", "T-08",
               "T-09", "T-10"):
    _EX01_VERDICTS[_check] = "passed"
for _check in ("T-04", "T-06"):
    _EX01_VERDICTS[_check] = "failed"
for _check in ("T-11", "T-12", "T-13", "T-14", "T-15"):
    _EX01_VERDICTS[_check] = "not applicable"
del _check


def _tally(verdicts):
    tally = {"passed": 0, "failed": 0, "not_applicable": 0, "total": 0}
    failed = []
    for check in RETIREMENT_CHECKS:
        verdict = verdicts[check]
        tally["total"] += 1
        if verdict == "passed":
            tally["passed"] += 1
        elif verdict == "failed":
            tally["failed"] += 1
            failed.append(check)
        else:
            tally["not_applicable"] += 1
    tally["failed_checks"] = failed
    return tally


def retirement_verdicts(fixture):
    """Return the per check verdicts of the retirement test for a
    fixture, over all fifteen checks T-01 to T-15 in the version of
    the report format paper pinned in the family record."""
    if fixture == "F-01":
        return dict(_F01_VERDICTS)
    if fixture in ("F-02", "EX-01"):
        return dict(_EX01_VERDICTS)
    raise ValueError("no retirement verdict stands recorded for: " + str(fixture))


def retirement_tally(fixture):
    """Return the retirement tally of one fixture as its own
    record. The F-01 tally and the EX-01 tally stand apart and
    stand never merged."""
    tally = _tally(retirement_verdicts(fixture))
    tally["fixture"] = fixture
    if fixture == "F-01":
        tally["centre_quarantine_breach"] = True
    return tally


def validate_publication_record(record):
    """Return True only for a complete publication record: it
    names the retirement test run that covered the unit, the
    version that run used, the verdict on each of the fifteen
    checks, and every failure that run recorded."""
    if not isinstance(record, dict):
        return False
    if not record.get("test_run") or not record.get("version"):
        return False
    verdicts = record.get("verdicts")
    if not isinstance(verdicts, dict):
        return False
    if tuple(sorted(verdicts)) != tuple(sorted(RETIREMENT_CHECKS)):
        return False
    recorded_failures = list(record.get("failures_recorded") or [])
    expected = [
        check for check in RETIREMENT_CHECKS
        if verdicts.get(check) == "failed"
    ]
    return recorded_failures == expected


def unit_is_publishable(unit):
    """Return True only where a unit carries a valid publication
    record. A unit covered by no recorded test run, or by a run
    with an unrecorded failure, is not published."""
    if not isinstance(unit, dict):
        return False
    return validate_publication_record(unit.get("publication_record"))


def judge_registry_entry(entry, compiler, checker):
    """Judge one SweepFamilyRegistry entry by phase, as the
    Reporter acting as family registrar: the before runs fields
    for lateness, the after runs fields for completeness, the
    entry compared against the run log by a checker who did not
    compile the registry."""
    same_person = compiler == checker
    phases = (entry or {}).get("phase_judgements") or {}
    judged = {
        "before_runs": phases.get("before_runs") == "judged",
        "after_runs": phases.get("after_runs") == "judged",
    }
    return {
        "before_runs_judged_for": "lateness",
        "after_runs_judged_for": "completeness",
        "phases_judged": judged,
        "compared_against_run_log": not same_person,
        "checker_did_not_compile": not same_person,
        "valid": (not same_person) and all(judged.values()),
    }


def validate_registry_entry(entry, compiler, checker):
    """Return True only where an entry stands judged in both
    phases by a checker who did not compile it."""
    return judge_registry_entry(entry, compiler, checker)["valid"]


def make_headline_unit(values):
    """Build one HeadlineResultUnit in the fixed Shape 15 field
    order. The unit is a closed unit: every field required, no
    field beyond the fourteen, quotable whole or not at all."""
    if not isinstance(values, dict):
        raise ValueError("a headline unit is built from a field mapping")
    extra = [key for key in values if key not in HEADLINE_UNIT_FIELDS]
    if extra:
        raise ValueError("fields beyond the closed unit: " + ", ".join(extra))
    unit = {}
    for field in HEADLINE_UNIT_FIELDS:
        if field not in values or values[field] is None:
            raise ValueError("headline unit field absent: " + field)
        unit[field] = copy.deepcopy(values[field])
    return unit


def validate_headline_unit(unit):
    """Return True only for a closed unit in the fixed field
    order, carrying its assumption set, its rows, its range kind,
    and every dependence mark as part of the unit itself. The
    centre only fixture unit never validates as a headline unit,
    and a unit carrying an extra Range kind field fails."""
    if not isinstance(unit, dict):
        return False
    if tuple(unit.keys()) != HEADLINE_UNIT_FIELDS:
        return False
    identifier = str(unit.get("headline_unit_identifier_and_issue_date"))
    if F01_UNIT_MARK in identifier:
        return False
    for field in HEADLINE_UNIT_FIELDS:
        if unit.get(field) is None:
            return False
    return True


def quote_headline_unit(unit):
    """Quote a headline unit whole. A unit that does not validate
    is not quoted at all."""
    if not validate_headline_unit(unit):
        raise ValueError("a headline unit is quotable whole or not at all")
    return copy.deepcopy(unit)


def first_sentence(text):
    """Return the first sentence of a claim text."""
    return str(text).split(".", 1)[0]


def validate_working_range_claim(text, assumption_set, rows, range_kind):
    """Return True only where the first sentence of a working
    range claim names its assumption set, its rows, and its range
    kind. A first sentence naming none of the three, or only some
    of them, does not meet the claim form."""
    sentence = first_sentence(text)
    return all(
        str(named) in sentence
        for named in (assumption_set, rows, range_kind)
    )


def moved_reading(delta, reporting_resolution):
    """Decide moved or not moved for one trace: the trace moved
    where its change reaches the reporting resolution for that
    trace stated in the family record before runs. The rule reads
    only the recorded change and the recorded resolution, so a
    second reader applying it to the same record reaches the same
    reading."""
    return abs(delta) >= reporting_resolution


def validate_bounding_headline(headline, family_record, run_record):
    """Return True only for a bounding headline in full form: it
    carries the external work issuance axis beside farm size and
    patience, it states which of the three traces moved and which
    did not, and it names the zero edge witness shape wherever the
    headline rests on the external work issuance axis or on a farm
    whose internal edge count stands zero or near zero under the
    bound the family record states."""
    if not isinstance(headline, dict):
        return False
    if tuple(headline.get("axes") or ()) != AXES:
        return False
    traces = headline.get("traces") or []
    if len(traces) != 3:
        return False
    for trace in traces:
        if not isinstance(trace, dict) or "moved" not in trace:
            return False
    needs_witness = headline.get("rests_on_axis") == "external work issuance"
    edge_count = (run_record or {}).get("farm_internal_edge_count")
    bound = (family_record or {}).get("near_zero_bound")
    if edge_count is not None and bound is not None and edge_count <= bound:
        needs_witness = True
    if needs_witness and not headline.get("zero_edge_witness_shape"):
        return False
    return True


def validate_envelope_claim(claim):
    """Return True only under envelope discipline: the claim
    states what holds at sampled points and over the stated ranges
    only, names a failure witness for what fails, and states
    nothing about values between sampled points."""
    if not isinstance(claim, dict):
        return False
    if claim.get("scope") != "sampled points and stated ranges only":
        return False
    if claim.get("claims_between_points"):
        return False
    if claim.get("monotonicity_claimed") or claim.get("interpolation_claimed"):
        return False
    if claim.get("holds") is False and not claim.get("failure_witness"):
        return False
    return True


def honest_loss_rate_h1(submitted, accepted_by_submission_period):
    """The honest loss rate in the decided H1 form: the period
    subtraction, with each accepted unit attributed to the period
    in which it was submitted. So attributed, the subtraction
    equals the event count by construction and cannot fall below
    zero. The rate travels as a stored numerator and denominator
    pair."""
    numerator = int(submitted) - int(accepted_by_submission_period)
    if numerator < 0:
        numerator = 0
    return {
        "form": "H1",
        "numerator": numerator,
        "denominator": int(submitted),
    }


def top_up_applies(winning_probability):
    """The top up duty at F-18, read with closed bounds: it
    applies at or above 0.1 and at or below 0.9."""
    return 0.1 <= winning_probability <= 0.9


def point_standing(replicate_count):
    """Return the standing of one control point against the 30
    replicate floor, with its count stated. A point below the
    floor borrows no standing of a point at the floor."""
    count = int(replicate_count)
    return {
        "replicates": count,
        "standing": "at floor" if count >= 30 else "below floor",
    }


def classify_run_outcome(run_length_in_days, regime_class):
    """Classify one run outcome. A run shorter than 30 simulated
    days is not classifiable as attacker winning under the final
    30 day rule: its outcome stands recorded as horizon
    insufficient and contributes to no transition figure."""
    if int(run_length_in_days) < 30:
        return {
            "outcome": "horizon insufficient",
            "contributes_to_transition_figure": False,
        }
    return {
        "outcome": regime_class,
        "contributes_to_transition_figure": True,
    }


def transition_figure(replicates):
    """Compute the transition figure at one control point over all
    replicates started at that point. Every replicate contributes
    exactly one recorded outcome by the horizon: a first terminal
    regime named by its class, or right censoring at the horizon.
    Competing regime exits stand counted as competing events and
    never as censoring. The denominator rule stands stated in the
    result."""
    total = len(replicates)
    counts = {}
    competing = 0
    censored = 0
    for replicate in replicates:
        if replicate.get("competing_exit"):
            competing += 1
            continue
        regime = replicate.get("first_terminal_regime")
        if regime is None:
            censored += 1
        else:
            counts[regime] = counts.get(regime, 0) + 1
    denominator = total if total else 1
    incidence = {
        regime: {"count": count, "denominator": total,
                 "share": count / denominator}
        for regime, count in counts.items()
    }
    return {
        "denominator": total,
        "denominator_rule": (
            "computed over all replicates started at the point; "
            "competing regime exits counted as competing events "
            "and never as censoring"),
        "cumulative_incidence": incidence,
        "competing_events": competing,
        "right_censored": {
            "count": censored, "denominator": total,
            "share": censored / denominator,
        },
        "outcomes_per_replicate": 1,
    }


def location_for_endpoint(figure, regime, band_endpoint):
    """Return the location of a band endpoint at a point, or None
    where cumulative incidence by the horizon does not reach the
    endpoint: no location stands reported for that endpoint at
    that point."""
    entry = (figure.get("cumulative_incidence") or {}).get(regime)
    if entry is None or entry["share"] < band_endpoint:
        return None
    return {"regime": regime, "endpoint": band_endpoint,
            "share": entry["share"]}


def record_first_observed(previous_evaluation_day, observed_day,
                          horizon, is_last_day=False):
    """Record the time of a first observed regime condition as the
    interval from the previous daily evaluation to the evaluation
    at which it was first observed, never as an exact event time.
    A condition first seen on the last day of a run has its
    interval closed only by the horizon."""
    close = horizon if is_last_day else observed_day
    return {
        "interval": (previous_evaluation_day, close),
        "form": "interval from previous daily evaluation",
        "exact_event_time": None,
    }


def validate_observation_time(record):
    """Return True only where a first observed regime stands in
    interval form. An exact event time fails."""
    if not isinstance(record, dict):
        return False
    if record.get("exact_event_time") is not None:
        return False
    interval = record.get("interval")
    return isinstance(interval, (list, tuple)) and len(interval) == 2


def region_shift_steps(location_a, location_b):
    """Return the shift of a region location between two points,
    in grid steps on each axis."""
    return (
        abs(int(location_a[0]) - int(location_b[0])),
        abs(int(location_a[1]) - int(location_b[1])),
    )


def transition_wording(location_a, location_b, location_reported=None):
    """Return the wording of a stability comparison. A transition
    stands reported as holding only where the region location is
    stable, moving by no more than one grid step on either axis.
    Where the narrowing test fails, the region stands reported as
    a finite population crossover, in those words. Stability is
    tested only where a location stands reported at both points:
    where no location stands reported at a point, the report
    states the crossover form or the censored form and makes no
    holding statement."""
    if location_reported is not None and not all(location_reported):
        return {
            "wording": "censored form",
            "holding_statement": False,
        }
    shift = region_shift_steps(location_a, location_b)
    if shift[0] <= 1 and shift[1] <= 1:
        return {"wording": "holding", "holding_statement": True}
    return {
        "wording": "finite population crossover",
        "holding_statement": False,
    }


def validate_transition_report(report):
    """Return True only for a full transition report: the full
    distribution near the threshold, the three regime class
    counts, the honest loss rate in the H1 form beside the
    headline figure, and at least 30 replicates per control point
    near the threshold, with the top up rule applied and recorded
    where a screening point lands within the closed bounds."""
    if not isinstance(report, dict):
        return False
    if not report.get("distribution_near_threshold"):
        return False
    counts = report.get("regime_class_counts") or {}
    if len(counts) != 3:
        return False
    rate = report.get("honest_loss_rate") or {}
    if rate.get("form") != "H1":
        return False
    for point in report.get("points") or []:
        if point.get("near_threshold") and int(point.get("replicates", 0)) < 30:
            return False
        probability = point.get("winning_probability")
        if probability is not None and top_up_applies(probability):
            if not point.get("top_up_recorded"):
                return False
    return True


def validate_transition_unit(unit):
    """Return True only where a transition report unit carries, in
    the same unit as its headline figure, the cumulative incidence
    of each terminal regime class by the stated horizon and the
    share of replicates right censored at that horizon, each
    labelled derived from the replicate counts in that unit, and
    every location sentence names its horizon."""
    if not isinstance(unit, dict):
        return False
    figure = unit.get("transition_figure") or {}
    if not figure.get("cumulative_incidence"):
        return False
    if "right_censored" not in figure:
        return False
    if unit.get("incidence_label") != "derived from the replicate counts in this unit":
        return False
    for sentence in unit.get("location_sentences") or []:
        if "horizon" not in sentence:
            return False
    return True


def reporter_inputs_for_family(retained_records):
    """Return the Reporter inputs of one family as carried through
    the retained records at S-10: the divergence count computed at
    S-04 as it stands, or the blocked family mark where it stands,
    naming the affected family and the affected share."""
    records = retained_records or {}
    return {
        "divergence_count": records.get("divergence_count"),
        "blocked_family_mark": copy.deepcopy(
            records.get("blocked_family_mark")),
    }


def share_report_stands(inputs, share):
    """Return True only where a report may read an affected share
    as standing as reported. While a blocked family mark stands
    for a share, with its count nonzero and unresolved, no report
    reads that share as standing as reported and no headline unit
    resting on it stands built."""
    mark = (inputs or {}).get("blocked_family_mark")
    if isinstance(mark, dict) and mark.get("affected_share") == share:
        if mark.get("count", 0) and not mark.get("resolved"):
            return False
    return True


def build_headline_unit_from_run(run_id, values, store_kind="sweep",
                                 family_record=None):
    """Build one headline unit from the retained records of one
    run, resolving the run record in one lookup through the
    Recorder store reading path. Where the record does not
    resolve, no unit stands built and the failure stands returned
    as a named failure and recorded in the family record where
    one stands handed in."""
    try:
        record = mod10.store_lookup(store_kinds=(store_kind,), key=run_id)
    except Exception:
        failure = {
            "name": mod10.ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "record": run_id,
        }
        if isinstance(family_record, dict):
            family_record.setdefault("named_failures", []).append(
                copy.deepcopy(failure))
        return {"built": False, "failure": failure, "unit": None}
    unit_values = dict(values)
    unit_values.setdefault(
        "run_registry_line",
        "run record " + str(run_id) + " read in one lookup")
    provenance = {
        "record": run_id,
        "record_state": record.get("record_state", "as retained"),
        "inside_unit": True,
    }
    unit_values.setdefault("checkability_fields", provenance)
    unit = make_headline_unit(unit_values)
    return {"built": True, "failure": None, "unit": unit}


def weekly_count(summary_records, week):
    """Compute the weekly headline reading load from the stored
    summary records alone: distinct headline unit identifiers
    whose witness records fall in the week, one unit counting
    once however many runs support it."""
    identifiers = set()
    for record in summary_records or []:
        if record.get("week") != week:
            continue
        for identifier in record.get("headline_unit_identifiers") or []:
            identifiers.add(identifier)
    return len(identifiers)


def make_weekly_container(week, units):
    """Build the weekly container for one week in arrival order.
    At most 25 whole headline units stand in the container under
    decision D-12. A unit beyond the cap stands held, reported as
    held in the container record of its own week."""
    ordered = list(units or [])
    inside = ordered[:WEEKLY_CAP]
    held = ordered[WEEKLY_CAP:]
    return {
        "week": week,
        "cap": WEEKLY_CAP,
        "headline_units": inside,
        "held_units": held,
        "held_count": len(held),
        "held_reported_as_held": bool(held),
        "count": len(inside),
    }


def next_weekly_container(week, previous_container, new_units):
    """Build the next weekly container: units held from the
    previous container stand released into it first, in arrival
    order, ahead of the new units of the week."""
    released = list((previous_container or {}).get("held_units") or [])
    return make_weekly_container(week, released + list(new_units or []))


def claim_enters_family(family_record, claim, results_seen):
    """Return True only where a claim may enter a family: the
    family stands fixed before runs, and no claim enters the
    family after results are seen."""
    if results_seen:
        return False
    return claim in ((family_record or {}).get("headline_claims") or [])


def validate_family_record(family_record):
    """Return whether a family record passes MOD-01 validation
    for Form 1 and supports a reportable run under its
    completeness bar."""
    if not isinstance(family_record, dict):
        return False
    if not mod01.validate_record("1", family_record):
        return False
    return mod01.family_supports_reportable_run(family_record)


__all__ = [
    "HEADLINE_UNIT_FIELDS",
    "REGISTRY_FIELDS",
    "RETIREMENT_CHECKS",
    "WEEKLY_CAP",
    "AXES",
    "F01_UNIT_MARK",
    "retirement_verdicts",
    "retirement_tally",
    "validate_publication_record",
    "unit_is_publishable",
    "judge_registry_entry",
    "validate_registry_entry",
    "make_headline_unit",
    "validate_headline_unit",
    "quote_headline_unit",
    "first_sentence",
    "validate_working_range_claim",
    "moved_reading",
    "validate_bounding_headline",
    "validate_envelope_claim",
    "honest_loss_rate_h1",
    "top_up_applies",
    "point_standing",
    "classify_run_outcome",
    "transition_figure",
    "location_for_endpoint",
    "record_first_observed",
    "validate_observation_time",
    "region_shift_steps",
    "transition_wording",
    "validate_transition_report",
    "validate_transition_unit",
    "reporter_inputs_for_family",
    "share_report_stands",
    "build_headline_unit_from_run",
    "weekly_count",
    "make_weekly_container",
    "next_weekly_container",
    "claim_enters_family",
    "validate_family_record",
]

"""MOD-05. Parley Core.

Work credit, vouching, reputation aggregation in interface form,
band and cap logic, challenge handling and behavioural adjudication
outcomes at decision record level, the gate passing share computed
per epoch and handed to the Recorder, and the graph facts.

DQ7-04 stands blocked in full. The aggregation surface in this module
is the aggregation interface plus the recommended candidate held
behind it as a comparison form only. No aggregation rule stands
adopted here, no headline answer rests on the candidate, and the
selector stands open. This module never calls MOD-06 and depends
only on MOD-01 types, with draws reaching it only as stream state
values passed in.
"""

import copy
import math
import unicodedata

from . import mod01

__all__ = [
    "AC8_FACE_STATEMENTS",
    "AGGREGATION_STANDING",
    "COMPONENT_DEFINITION_VERSION_FIELD",
    "EXCLUDED_CLASSES",
    "FORGED_VOUCH_BASIS_CLASS",
    "UNKNOWN_SHARE",
    "accept_work",
    "accuracy_ranges_stand_unmerged",
    "adjudicate",
    "adjudication_input_failure_class",
    "adjudication_outcome",
    "aggregate_reputation",
    "aggregation_interface",
    "aggregation_score",
    "alternation_result",
    "band_membership",
    "band_transition",
    "boundary_neighbourhood",
    "challenge_outcome",
    "compare_aggregation",
    "component",
    "component_cap_check",
    "compute_share",
    "cost_statement",
    "cost_statement_valid",
    "credit_work",
    "decay_result",
    "decay_slices",
    "eligibility",
    "evaluation_order_record",
    "excluded_class_counts",
    "feeder_position",
    "gate_passing_share",
    "graph_facts",
    "graph_snapshot",
    "panel_inputs",
    "population_figure",
    "proportion_record",
    "realised_degree_distribution",
    "recompute_share",
    "recomputation_sample",
    "reputation_and_band_values",
    "score_bearing_figure",
    "share_for_epoch",
    "undelivered_share",
    "validate_band_transition_result",
    "validate_evaluation_order",
    "validate_graph_snapshot",
    "validate_headline_adjudication_claim",
    "validate_logged_share",
    "validate_panel_inputs",
    "validate_proportion",
    "validate_report_reading",
    "validate_run_share_logs",
    "validate_view_wording",
    "vouch",
    "work_credit",
]

UNKNOWN_SHARE = "unknown"

AGGREGATION_STANDING = (
    "interface plus recommended candidate as comparison form only; "
    "no aggregation rule adopted; selector open at SEL-10 read with "
    "register item NQ-64 and open point OP-09; DQ7-04 blocked"
)

AC8_FACE_STATEMENTS = (
    "neither decay arm tests Candidate 1 as written",
    "the aggregation comparison is unspecified for Candidate 1 as written",
)

EXCLUDED_CLASSES = (
    "cryptographic offences",
    "challenges closed by two of two settlement before determination",
    "panel exhausted dispositions with no determination",
    "the adjacent arbitrated share for a forged vouch basis",
)

FORGED_VOUCH_BASIS_CLASS = EXCLUDED_CLASSES[3]

COMPONENT_DEFINITION_VERSION_FIELD = "component_definition_version"

_DECAY_PLANE = (
    {"half_life_days": 7, "label": "half life 7 days"},
    {"half_life_days": 14, "label": "about 14 days"},
    {"half_life_days": 69, "label": "about 69 days"},
    {"half_life_days": 180, "label": "slice at the 180 day run length scale"},
    {"half_life_days": 693, "label": "about 693 days"},
    {"half_life_days": None, "label": "infinite"},
)

_EXTENSION_SLICES = (
    {"half_life_days": 1, "label": "half life 1 day"},
    {"half_life_days": 3, "label": "half life 3 days"},
)


def _get(record, *names, default=None):
    if isinstance(record, dict):
        for name in names:
            if name in record and record[name] is not None:
                return record[name]
        return default
    for name in names:
        if hasattr(record, name):
            value = getattr(record, name)
            if value is not None:
                return value
    return default


def _freeze(value):
    return copy.deepcopy(value)


# ---------------------------------------------------------------------------
# Work credit and proportions, Shape 14
# ---------------------------------------------------------------------------

def proportion_record(numerator, denominator):
    """A proportion stored only with its numerator and denominator
    stored apart. A proportion without its parts is refused."""
    if numerator is None or denominator is None:
        raise ValueError("a proportion is stored only with its numerator and denominator stored apart")
    return {"numerator": numerator, "denominator": denominator}


def _base_number(part):
    if isinstance(part, float):
        return float.__float__(part)
    return int.__int__(part)


def validate_proportion(record):
    """True only where a proportion stands stored with its numerator
    and denominator apart, and any stored quotient agrees with them."""
    if not isinstance(record, dict):
        return False
    if not dict.__contains__(record, "numerator") or not dict.__contains__(record, "denominator"):
        return False
    numerator = dict.__getitem__(record, "numerator")
    denominator = dict.__getitem__(record, "denominator")
    for part in (numerator, denominator):
        if isinstance(part, bool) or not isinstance(part, (int, float)):
            return False
        if not math.isfinite(_base_number(part)):
            return False
    numerator = _base_number(numerator)
    denominator = _base_number(denominator)
    if denominator <= 0 or numerator < 0:
        return False
    if dict.__contains__(record, "quotient") and dict.__getitem__(record, "quotient") is not None:
        quotient = dict.__getitem__(record, "quotient")
        if isinstance(quotient, bool) or not isinstance(quotient, (int, float)):
            return False
        quotient = _base_number(quotient)
        if not math.isfinite(quotient):
            return False
        if abs(quotient - numerator / denominator) > 1e-12:
            return False
    return True


def work_credit(events):
    """Work and acceptance counters computed from the same events.

    Each event is one work completion with its acceptance outcome.
    The counters that enter the AC-1 hash list and the denominator
    of the primary order parameter come from this one event set, and
    each proportion stands stored as its numerator and denominator
    apart, per Shape 14.
    """
    events = list(events)
    per_agent = {}
    for event in events:
        agent = _get(event, "agent_identifier", "agent")
        if agent is None:
            raise ValueError("a work event carries no agent identifier")
        bucket = per_agent.setdefault(agent, {"submitted": 0, "accepted": 0})
        bucket["submitted"] += 1
        if _get(event, "accepted", default=False):
            bucket["accepted"] += 1
    counters = {}
    total_submitted = 0
    total_accepted = 0
    for agent, bucket in per_agent.items():
        total_submitted += bucket["submitted"]
        total_accepted += bucket["accepted"]
        counters[agent] = {
            "submitted": bucket["submitted"],
            "accepted": bucket["accepted"],
            "proportion": proportion_record(bucket["accepted"], bucket["submitted"]),
        }
    return {
        "counters": counters,
        "totals": {
            "submitted": total_submitted,
            "accepted": total_accepted,
            "proportion": (
                proportion_record(total_accepted, total_submitted)
                if total_submitted else UNKNOWN_SHARE
            ),
        },
        "events_used": len(events),
        "same_event_set": True,
    }


def credit_work(events):
    return work_credit(events)


def accept_work(events):
    return work_credit(events)


# ---------------------------------------------------------------------------
# Vouching, components and graph facts, Shape 8 and Shape 9
# ---------------------------------------------------------------------------

def vouch(voucher, vouchee, stake, creation_day=0, lifetime=None,
          score_bearing=True, component_identifier=None,
          component_definition_version=None):
    """One VouchEdge in Shape 8 form, carrying its component
    identifier under the component definition version in force."""
    edge = {
        "voucher": voucher,
        "vouchee": vouchee,
        "stake": stake,
        "creation_day": creation_day,
        "lifetime": lifetime,
        "score_bearing_flag": bool(score_bearing),
        "component_identifier": component_identifier,
    }
    if component_definition_version is not None:
        edge[COMPONENT_DEFINITION_VERSION_FIELD] = component_definition_version
    return edge


def _mutual_pairs(edges):
    directed = set()
    for edge in edges:
        directed.add((_get(edge, "voucher"), _get(edge, "vouchee")))
    pairs = set()
    for a, b in directed:
        if (b, a) in directed:
            pairs.add(tuple(sorted((a, b))))
    return pairs


def _components(edges):
    pairs = _mutual_pairs(edges)
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    members = set()
    for a, b in pairs:
        members.add(a)
        members.add(b)
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    groups = {}
    for member in members:
        groups.setdefault(find(member), []).append(member)
    result = []
    for group_members in groups.values():
        group_members = sorted(group_members)
        member_set = set(group_members)
        group_edges = [
            edge for edge in edges
            if _get(edge, "voucher") in member_set and _get(edge, "vouchee") in member_set
        ]
        result.append({
            "members": group_members,
            "edge_count": len(group_edges),
            "stake_total": sum(_get(edge, "stake", default=0) or 0 for edge in group_edges),
            "edges": _freeze(group_edges),
        })
    result.sort(key=lambda item: item["members"])
    return result


def component(edges, component_definition_version=None):
    """The component list under one component definition version.
    Component size for the cap counts edges, not stake weight."""
    edges = list(edges)
    groups = _components(edges)
    largest = max((len(g["members"]) for g in groups), default=0)
    return {
        "component_list": [
            {"members": g["members"], "member_count": len(g["members"]), "edge_count": g["edge_count"], "stake_total": g["stake_total"]}
            for g in groups
        ],
        "largest_mutually_vouching_component_size": largest,
        "counting_rule": "edges, not stake weight",
        COMPONENT_DEFINITION_VERSION_FIELD: component_definition_version,
    }


def component_cap_check(edges, cap_edges):
    """The component cap counts edges, not stake weight: a component
    passes the cap only where its edge count is at or under the cap,
    whatever its stake total."""
    for group in _components(list(edges)):
        if group["edge_count"] > cap_edges:
            return False
    return True


def realised_degree_distribution(edges, by_epoch=None):
    """The realised degree distribution, by graph and, where epochs
    are supplied, by epoch."""
    def distribution(edge_set):
        degree = {}
        for edge in edge_set:
            for agent in (_get(edge, "voucher"), _get(edge, "vouchee")):
                degree[agent] = degree.get(agent, 0) + 1
        return degree

    edges = list(edges)
    result = {"by_graph": distribution(edges)}
    if by_epoch is not None:
        result["by_epoch"] = {
            epoch: distribution(list(epoch_edges)) for epoch, epoch_edges in by_epoch.items()
        }
    return result


def graph_snapshot(edges, component_definition_version=None, edge_list_reference=None):
    """A GraphSnapshot in Form 9 form, under its component definition
    version, which travels with the snapshot."""
    edges = list(edges)
    comp = component(edges, component_definition_version=component_definition_version)
    return {
        "edge_list_reference": edge_list_reference if edge_list_reference is not None else _freeze(edges),
        "component_list": comp["component_list"],
        "largest_mutually_vouching_component_size": comp["largest_mutually_vouching_component_size"],
        "realised_degree_distribution": realised_degree_distribution(edges)["by_graph"],
        COMPONENT_DEFINITION_VERSION_FIELD: component_definition_version,
    }


def validate_graph_snapshot(snapshot, edges):
    """A snapshot computed under one component definition version
    read against edges under another version fails. The snapshot
    must also agree with its referenced edge list."""
    if not isinstance(snapshot, dict):
        return False
    edges = list(edges)
    if snapshot.get(COMPONENT_DEFINITION_VERSION_FIELD) is None:
        return False
    reference = snapshot.get("edge_list_reference")
    if reference is None:
        return False
    if isinstance(reference, (list, tuple)) and list(reference) != edges:
        return False
    if snapshot.get("realised_degree_distribution") is None:
        return False
    versions = {
        _get(edge, COMPONENT_DEFINITION_VERSION_FIELD)
        for edge in edges
        if _get(edge, COMPONENT_DEFINITION_VERSION_FIELD) is not None
    }
    snap_version = snapshot.get(COMPONENT_DEFINITION_VERSION_FIELD)
    if versions and snap_version not in versions:
        return False
    if len(versions) > 1:
        return False
    expected = graph_snapshot(edges, component_definition_version=snap_version)
    return (
        snapshot.get("component_list") == expected["component_list"]
        and snapshot.get("largest_mutually_vouching_component_size")
        == expected["largest_mutually_vouching_component_size"]
        and snapshot.get("realised_degree_distribution")
        == expected["realised_degree_distribution"]
    )


def graph_facts(edges, by_epoch=None, component_definition_version=None):
    """The graph facts the core hands on: the edge list reference,
    the component list, the largest mutually vouching component size,
    and the realised degree distribution by graph and by epoch."""
    edges = list(edges)
    snapshot = graph_snapshot(
        edges, component_definition_version=component_definition_version)
    facts = {
        "edge_list_reference": snapshot["edge_list_reference"],
        "component_list": snapshot["component_list"],
        "largest_mutually_vouching_component_size":
            snapshot["largest_mutually_vouching_component_size"],
        "realised_degree_distribution": realised_degree_distribution(edges, by_epoch=by_epoch),
    }
    return facts


def feeder_position(feeder, edges):
    """The one directional feeder fact: whether the feeder appears in
    the largest mutually vouching component figure, in the component
    list, or in neither. A one directional vouch with no return vouch
    places the feeder in neither."""
    groups = _components(list(edges))
    if not groups:
        return "neither"
    largest_size = max(len(g["members"]) for g in groups)
    for group in groups:
        if feeder in group["members"]:
            if len(group["members"]) == largest_size:
                return "largest mutually vouching component"
            return "component list"
    return "neither"


# ---------------------------------------------------------------------------
# Aggregation interface and the recommended candidate, comparison form only
# ---------------------------------------------------------------------------

def aggregation_interface():
    return {
        "form": "interface",
        "standing": AGGREGATION_STANDING,
        "adopted_rule": None,
        "adopted": False,
        "selector": "open at SEL-10, read with NQ-64 and OP-09",
        "candidate": "recommended candidate, comparison form only",
        "candidate_includes_sym_ctl": True,
        "headline_use_permitted": False,
    }


def aggregate_reputation(inputs):
    """The recommended candidate behind the aggregation interface,
    in comparison form only. It produces one reputation score for an
    agent inside the comparison programme. It adopts no rule and no
    headline answer rests on it.

    Inputs: an agent identifier, its accepted work count, its score
    bearing vouches received, and its penalty count. The comparison
    score is accepted work plus received score bearing stake, less
    penalties, as a single deterministic value.
    """
    agent = _get(inputs, "agent_identifier", "agent")
    accepted = _get(inputs, "accepted_work", "accepted", default=0) or 0
    penalties = _get(inputs, "penalties", "penalty_count", default=0) or 0
    received = _get(inputs, "vouches_received", "received_vouches", default=()) or ()
    stake_total = 0
    for edge in received:
        if _get(edge, "score_bearing_flag", "score_bearing", default=True):
            stake_total += _get(edge, "stake", default=0) or 0
    score = accepted + stake_total - penalties
    return {
        "agent_identifier": agent,
        "score": score,
        "scores": [score],
        "form": "comparison form only",
        "standing": AGGREGATION_STANDING,
        "adopted_rule": None,
        "adopted": False,
        "headline_use_permitted": False,
        "face_statements": list(AC8_FACE_STATEMENTS),
    }


def aggregation_score(inputs):
    return aggregate_reputation(inputs)


def compare_aggregation(inputs):
    return aggregate_reputation(inputs)


# ---------------------------------------------------------------------------
# Bands, caps and eligibility, in the evaluation order the record states
# ---------------------------------------------------------------------------

def evaluation_order_record(order=None, batch=None):
    """The evaluation order carriage. Order O-1 with a batch of one
    simulated day stands as a recommendation, not a ruling, with
    order O-5 as a named sensitivity arm. Judgement points and gaps
    stand open at NQ-46, open point OP-08."""
    return {
        "order": order,
        "batch": batch if batch is not None else "one simulated day",
        "standing": "recommendation, not a ruling",
        "presented_as_ruled": False,
        "sensitivity_arm": "O-5",
        "open_at": "NQ-46, OP-08",
    }


def validate_evaluation_order(record):
    """A run whose order stands unstated fails, and no record may
    present O-1, or any order, as ruled."""
    if not isinstance(record, dict):
        return False
    if not record.get("order"):
        return False
    if record.get("presented_as_ruled"):
        return False
    return True


def band_membership(score, bands, evaluation_order=None):
    """Band membership read from a score produced through the
    aggregation interface, in the evaluation order the record states.
    Bands are stated as (band name, minimum score) pairs in the
    record; the highest band whose minimum the score reaches holds."""
    order_record = evaluation_order if isinstance(evaluation_order, dict) else evaluation_order_record(evaluation_order)
    if not validate_evaluation_order(order_record):
        raise ValueError("eligibility judgements require the evaluation order the record states, unstated or presented as ruled")
    chosen = None
    chosen_minimum = None
    for name, minimum in bands:
        if score >= minimum and (chosen_minimum is None or minimum > chosen_minimum):
            chosen = name
            chosen_minimum = minimum
    return {
        "band": chosen,
        "score": score,
        "score_source": "aggregation interface, comparison form only",
        "evaluation_order": _freeze(order_record),
    }


def eligibility(score, bands, evaluation_order=None, panel_minimum=None, cap_maximum=None):
    """Eligibility judgements for band membership, panel eligibility
    and cap eligibility in one day, all read from the one score."""
    result = band_membership(score, bands, evaluation_order=evaluation_order)
    result["panel_eligible"] = True if panel_minimum is None else score >= panel_minimum
    result["cap_eligible"] = True if cap_maximum is None else score <= cap_maximum
    return result


def reputation_and_band_values(agents_scores, bands, viewer=None, evaluation_order=None):
    """The view edge supply: the reputation and band values this core
    already owns, supplied for assembly into a view by MOD-04,
    without MOD-04 taking over their computation."""
    order_record = evaluation_order if isinstance(evaluation_order, dict) else evaluation_order_record(evaluation_order)
    values = {}
    for agent, score in agents_scores.items():
        values[agent] = band_membership(score, bands, evaluation_order=order_record)
    return {"viewer": viewer, "values": values}


def validate_view_wording(wording):
    """The record enforced description of brief section 7 boundaries
    one and two stands permitted for agent held views only, and for
    no wider class, in any position the wording appears."""
    if not isinstance(wording, dict):
        return False
    if wording.get("description") != "record enforced":
        return False
    return wording.get("scope") == "agent held views"


# ---------------------------------------------------------------------------
# Decay slices, Candidate 1 carriage and alternation, fixtures F-14 and F-15
# ---------------------------------------------------------------------------

def decay_slices():
    """The decay slice set of fixture F-14: at least six slices in
    every reported plane, carried variant W-02 folded in as the zero
    decay edge at daily retention 1.0 and not as a separate arm, and
    the two extension slices labelled as an outside range extension."""
    slices = [dict(item) for item in _DECAY_PLANE]
    slices.append({
        "half_life_days": None,
        "label": "W-02 zero decay edge",
        "variant": "W-02",
        "daily_retention": 1.0,
        "folded_in": True,
        "separate_arm": False,
    })
    for item in _EXTENSION_SLICES:
        entry = dict(item)
        entry["extension"] = True
        entry["extension_label"] = "outside range extension"
        entry["honest_side_readout"] = "honest side readout carried with the result"
        slices.append(entry)
    return slices


def decay_result(half_life_days="stated", reported_as=None):
    """One decay arm result. Every decay arm result states on its
    face that neither decay arm tests Candidate 1 as written and
    that the aggregation comparison is unspecified for Candidate 1
    as written, per AC-8."""
    extension = half_life_days in (1, 3)
    result = {
        "half_life_days": half_life_days,
        "face_statements": list(AC8_FACE_STATEMENTS),
        "tests_candidate_1_as_written": False,
        "reported_as": reported_as,
    }
    if extension:
        result["extension"] = True
        result["extension_label"] = "outside range extension"
        result["honest_side_readout"] = "honest side readout carried with the result"
    return result


def alternation_result(decay_slice=None, same_or_different_retention=None,
                       prior_bad_phase_count=None, highest_band=None,
                       bad_phases_before_exclusion=None,
                       ring_highest_band=None,
                       ring_bad_phases_before_exclusion=None,
                       reported_as=None):
    """An alternation result states, from the rule record, whether
    the retention applied to penalised behaviour and to accepted
    good work was the same rate or different rates, and the count
    of prior bad phases still present in the rule state at each
    exclusion. A result reporting neither pin stands as a band
    result under alternation, and not as a result about
    misbehaviour retention."""
    pins_stated = same_or_different_retention is not None and prior_bad_phase_count is not None
    result = {
        "decay_slice": decay_slice,
        "retention_pin": same_or_different_retention,
        "prior_bad_phase_count_pin": prior_bad_phase_count,
        "highest_band": highest_band,
        "bad_phases_before_exclusion": bad_phases_before_exclusion,
        "ring_highest_band": ring_highest_band,
        "ring_bad_phases_before_exclusion": ring_bad_phases_before_exclusion,
        "face_statements": list(AC8_FACE_STATEMENTS),
        "tests_candidate_1_as_written": False,
    }
    if pins_stated:
        result["classification"] = reported_as or "result about misbehaviour retention"
    else:
        result["classification"] = "band result under alternation"
    return result


# ---------------------------------------------------------------------------
# Band boundary neighbourhood and transitions, fixture F-28
# ---------------------------------------------------------------------------

def boundary_neighbourhood(scores, boundary, distance_slices):
    """The boundary neighbourhood counts for one band boundary:
    the count of identities in each stated distance slice above
    and below the boundary, the count crossing the boundary during
    the run, and the cheapest score movement, in accepted work
    units, that crosses the boundary from below. Distances and the
    neighbourhood size stand open, fixed in the family record
    before runs; this function pins the counts, not a distance."""
    counts = {}
    for label in distance_slices:
        counts[label] = 0
    crossings = 0
    cheapest = None
    for entry in scores:
        label = _get(entry, "distance_slice")
        if label in counts:
            counts[label] += 1
        if _get(entry, "crossed", default=False):
            crossings += 1
        score = _get(entry, "score")
        if score is not None and score < boundary:
            movement = boundary - score
            if cheapest is None or movement < cheapest:
                cheapest = movement
    return {
        "boundary": boundary,
        "counts_per_distance_slice": counts,
        "crossing_count": crossings,
        "cheapest_crossing_movement_in_accepted_work_units": cheapest,
        "standing_label": "distances and neighbourhood size open, fixed in the family record before runs",
    }


def band_transition(scores, boundary, distance_slices, form="society level"):
    result = boundary_neighbourhood(scores, boundary, distance_slices)
    result["form"] = form
    return result


def validate_band_transition_result(result):
    """A band transition result without the boundary neighbourhood
    counts has not run the test, in either form."""
    if not isinstance(result, dict):
        return False
    if not isinstance(result.get("counts_per_distance_slice"), dict):
        return False
    if "crossing_count" not in result:
        return False
    if "cheapest_crossing_movement_in_accepted_work_units" not in result:
        return False
    return True


# ---------------------------------------------------------------------------
# Gate passing share, Contract G and brief section 5.10
# ---------------------------------------------------------------------------

def gate_passing_share(eligible, passing, epoch=None):
    """The gate passing share computed per epoch by this core, as a
    proportion stored with its numerator and denominator apart."""
    eligible = list(eligible)
    if not eligible:
        return UNKNOWN_SHARE
    passing_set = set(passing)
    numerator = sum(1 for item in eligible if item in passing_set)
    share = proportion_record(numerator, len(eligible))
    share["epoch"] = epoch
    share["computed_by"] = "MOD-05 Parley Core"
    return share


def compute_share(eligible, passing, epoch=None):
    return gate_passing_share(eligible, passing, epoch=epoch)


def share_for_epoch(epoch, eligible=None, passing=None):
    """The share for one epoch, or the explicit value unknown where
    no share was computed and delivered for that epoch. Unknown is
    never zero."""
    if eligible is None or passing is None:
        return UNKNOWN_SHARE
    return gate_passing_share(eligible, passing, epoch=epoch)


def undelivered_share():
    return UNKNOWN_SHARE


def validate_logged_share(logged):
    """A logged share position holding zero where the share was not
    delivered fails. The explicit value unknown is the only lawful
    undelivered entry."""
    if isinstance(logged, dict):
        return validate_proportion(logged)
    return logged == UNKNOWN_SHARE


def score_bearing_figure(envelope_value, share):
    """The per eligible identity score bearing figure: the envelope
    value multiplied by the share."""
    if not validate_proportion(share):
        raise ValueError("the score bearing figure reads a share stored with its parts apart")
    return envelope_value * share["numerator"] / share["denominator"]


def population_figure(envelope_value, shares, record_state=None):
    """A population figure under the double application rule: per
    epoch, the score bearing figure multiplied by the share again,
    and the population average as the mean of the corrected per
    epoch figures, as the final step. The derivation names its
    record state. A single application figure is not this figure."""
    if record_state is None:
        raise ValueError("the derivation names its record state")
    if not shares:
        return {
            "per_epoch_corrected": [],
            "population_average": UNKNOWN_SHARE,
            "derivation": "double application, mean as the final step",
            "record_state": record_state,
        }
    corrected = []
    for share in shares:
        first = score_bearing_figure(envelope_value, share)
        corrected.append(first * share["numerator"] / share["denominator"])
    average = sum(corrected) / len(corrected) if corrected else 0
    return {
        "per_epoch_corrected": corrected,
        "population_average": average,
        "derivation": "double application, mean as the final step",
        "record_state": record_state,
    }


def cost_statement_valid(record):
    """A run missing the share log or the realised degree
    distribution log is invalid for any cost statement, per AC-5,
    and no cost statement assumes the share. The share itself
    stands unfitted in every assumption set."""
    if not isinstance(record, dict):
        return False
    if "share_log" not in record or record["share_log"] is None:
        return False
    if "degree_distribution_log" not in record or record["degree_distribution_log"] is None:
        return False
    share_entry = record.get("assumption_share")
    if isinstance(share_entry, dict) and share_entry.get("fitted"):
        return False
    share_log = record.get("share_log")
    entries = []
    if isinstance(share_log, (list, tuple)):
        entries = list(share_log)
    elif isinstance(share_log, dict) and "numerator" in share_log:
        entries = [share_log]
    for entry in entries:
        if not validate_logged_share(entry):
            return False
    return True


def cost_statement(record):
    return {"valid": cost_statement_valid(record)}


def validate_run_share_logs(record):
    return cost_statement_valid(record)


# ---------------------------------------------------------------------------
# Recomputation check, picked proposal CR8B-06, sample per Manager Entry 21
# ---------------------------------------------------------------------------

def recomputation_sample(records):
    """The sample rule settled at Manager Entry 21 for R1-035: the
    full set where the set holds 200 records or fewer; above that,
    10 percent of the set with a floor of 200 records, selected by
    deterministic stride from the record order."""
    records = list(records)
    if len(records) <= 200:
        return records
    take = max(200, len(records) // 10)
    stride = len(records) / take
    chosen = []
    index = 0.0
    while len(chosen) < take and int(index) < len(records):
        chosen.append(records[int(index)])
        index += stride
    return chosen


def recompute_share(logged_shares, recomputed_shares):
    """The one fact computed twice check, as a check artefact only.
    It stands held in a separate store position from the logged
    share, its only lawful output is a divergence count, ownership
    of the share is unchanged, and no second owner is created."""
    divergent = []
    for epoch in sorted(set(logged_shares) | set(recomputed_shares), key=str):
        if epoch not in logged_shares or epoch not in recomputed_shares or logged_shares[epoch] != recomputed_shares[epoch]:
            divergent.append(epoch)
    divergence = len(divergent)
    return {
        "divergence_count": divergence,
        "divergent_epochs": divergent,
        "store_position": "separate recomputation position",
        "owner_of_share": "MOD-05 Parley Core",
        "second_owner_created": False,
    }


def validate_report_reading(divergence_count, resolved=False):
    """While a nonzero divergence count stands unresolved, no report
    reads the affected share, and no result resting on that share,
    as standing as reported."""
    if divergence_count and divergence_count != 0 and not resolved:
        return False
    return True


# ---------------------------------------------------------------------------
# Challenge handling and behavioural adjudication, Shape 10
# ---------------------------------------------------------------------------

_PANEL_BARRED_KEYS = {
    "membership", "label", "is_honest", "label_reference",
    "membership_ground_truth",
}


_HOMOGLYPH_MAP = {
    "\u0430": "a", "\u0441": "c", "\u0435": "e", "\u043e": "o",
    "\u0440": "p", "\u0445": "x", "\u0443": "y", "\u0456": "i",
    "\u0458": "j", "\u0455": "s", "\u04bb": "h", "\u043a": "k",
    "\u043c": "m", "\u043d": "h", "\u0442": "t", "\u0432": "b",
    "\u03b1": "a", "\u03b2": "b", "\u03b5": "e", "\u03b9": "i",
    "\u03ba": "k", "\u03bc": "m", "\u03bf": "o", "\u03c1": "p",
    "\u03c4": "t", "\u03c7": "x", "\u03c5": "u", "\u03bd": "n",
    "\u03b3": "g", "\u03b4": "d", "\u03bb": "l", "\u03c3": "s",
    "\u03c9": "w", "\u03b6": "z", "\u03b8": "t", "\u03c6": "f",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "\u0452": "s", "\u0493": "h",
    "\u13d2": "r", "\uaba2": "r", "\u13ac": "e", "\uab7c": "e",
    "\u13aa": "a", "\uab7a": "a", "\u13de": "l", "\uabae": "l",
    "\u13b7": "m", "\uab87": "m", "\u13be": "o", "\uab8e": "o",
    "\u13c1": "n", "\uab91": "n", "\u13ef": "y", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
    "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l", "\u00a5": "y",
    "\u00a2": "c", "\u00a7": "s", "+": "t",
}
for _upper, _lower in list(_HOMOGLYPH_MAP.items()):
    _HOMOGLYPH_MAP[_upper.upper()] = _lower

_TRANSLITERATION_MAP = dict(_HOMOGLYPH_MAP)
_TRANSLITERATION_MAP.update({
    "\u0431": "b", "\u0432": "v", "\u0433": "g", "\u0434": "d",
    "\u0451": "e", "\u0436": "zh", "\u0437": "z", "\u0438": "i",
    "\u0439": "y", "\u043b": "l", "\u043c": "m", "\u043d": "n",
    "\u043f": "p", "\u0440": "r", "\u0441": "s", "\u0442": "t",
    "\u0443": "u", "\u0444": "f", "\u0445": "h", "\u0446": "ts",
    "\u0447": "ch", "\u0448": "sh", "\u0449": "shch", "\u044a": "",
    "\u044b": "y", "\u044c": "", "\u044d": "e", "\u044e": "yu",
    "\u044f": "ya",
    "\u03b2": "b", "\u03b3": "g", "\u03b4": "d", "\u03b6": "z",
    "\u03b7": "e", "\u03b8": "th", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03c0": "p", "\u03c1": "r", "\u03c2": "s",
    "\u03c3": "s", "\u03c5": "u", "\u03c6": "ph", "\u03c7": "h",
    "\u03c8": "ps", "\u03c9": "o",
})
for _upper, _lower in list(_TRANSLITERATION_MAP.items()):
    _TRANSLITERATION_MAP[_upper.upper()] = _lower

_HOMOGLYPH_MAP_VO = dict(
    _HOMOGLYPH_MAP, **{"\u0578": "un", "\u0548": "un"})
_TRANSLITERATION_MAP_VO = dict(
    _TRANSLITERATION_MAP, **{"\u0578": "un", "\u0548": "un"})

_LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "@": "a", "$": "s",
}

_LEET_L_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "@": "a", "$": "s",
}


def _folded_readings(key):
    """The folded readings of one key, in the same canonicalised
    form the barred surfaces read: compatibility decomposition
    with combining marks dropped, non Latin homoglyph letters
    mapped to the Latin letters they stand for, separators and
    zero width characters dropped, beside a reading with digit
    substitutions read as letters and a reading with digits
    dropped. The panel vocabulary itself stands unmoved; only its
    reading gains the folded form. The readings stand taken under
    both the homoglyph map and the transliteration map."""
    readings = []

    def add(transformed):
        plain = "".join(
            character for character in transformed
            if character.isalnum())
        if plain and plain not in readings:
            readings.append(plain)

    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        decomposed = unicodedata.normalize("NFKD", str(key).lower())
        base = "".join(
            letter_map.get(character, character)
            for character in decomposed
            if not unicodedata.category(character).startswith("M")
        )
        add(base)
        add("".join(_LEET_MAP.get(character, character)
                    for character in base))
        add("".join(_LEET_L_MAP.get(character, character)
                    for character in base))
        add("".join(character for character in base
                    if not character.isdigit()))
    return tuple(readings)


_PANEL_BARRED_FOLDED_EXACT = frozenset(
    reading
    for name in _PANEL_BARRED_KEYS
    for reading in _folded_readings(name)
)


def _panel_key_barred(key):
    lowered = str(key).lower()
    if "ground_truth" in lowered or lowered in _PANEL_BARRED_KEYS:
        return True
    for reading in _folded_readings(key):
        if reading in _PANEL_BARRED_FOLDED_EXACT:
            return True
        if "groundtruth" in reading:
            return True
        if "membership" in reading:
            return True
    return False


PANEL_TRAVERSAL_DEPTH_BOUND = 100


def _panel_traversal_guard(value, depth, seen, path):
    if depth > PANEL_TRAVERSAL_DEPTH_BOUND:
        raise ValueError(
            "panel traversal bound reached at " + (path or "root")
            + ": the value stands deeper than the stated bound of "
            + str(PANEL_TRAVERSAL_DEPTH_BOUND)
        )
    if id(value) in seen:
        raise ValueError(
            "panel traversal found a cycle at " + (path or "root")
        )


def _base_iter(value):
    if isinstance(value, list):
        return list.__iter__(value)
    if isinstance(value, tuple):
        return tuple.__iter__(value)
    if isinstance(value, frozenset):
        return frozenset.__iter__(value)
    if isinstance(value, set):
        return set.__iter__(value)
    return iter(value)


def _panel_leaf_copy(value):
    """Copy one leaf part of a checked panel record as itself.

    The container parts of a panel record stand rebuilt through
    base class readings in _panel_clean, so no part of the record
    can direct the copy. A leaf part stands in no container form,
    so it stands carried as itself and never through a copy
    protocol the part itself supplies."""
    return value


def _panel_clean(value, _depth=0, _seen=None, _path=""):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        _panel_traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                cleaned = {}
                for key, item in dict.items(value):
                    if _panel_key_barred(key):
                        continue
                    cleaned_key = _panel_clean(
                        key, _depth + 1, seen, _path + "/" + str(key))
                    cleaned[cleaned_key] = _panel_clean(
                        item, _depth + 1, seen, _path + "/" + str(key))
                return cleaned
            if isinstance(value, list):
                return [
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                ]
            if isinstance(value, tuple):
                return tuple(
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                )
            if isinstance(value, frozenset):
                return frozenset(
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                )
            return {
                _panel_clean(
                    item, _depth + 1, seen,
                    _path + "[" + str(index) + "]")
                for index, item in enumerate(_base_iter(value))
            }
        finally:
            seen.discard(id(value))
    return _panel_leaf_copy(value)


def _panel_carries_barred(value, _depth=0, _seen=None, _path=""):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        _panel_traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                return any(
                    _panel_key_barred(key)
                    or _panel_carries_barred(
                        key, _depth + 1, seen, _path + "/" + str(key))
                    or _panel_carries_barred(
                        item, _depth + 1, seen, _path + "/" + str(key))
                    for key, item in dict.items(value)
                )
            return any(
                _panel_carries_barred(
                    item, _depth + 1, seen,
                    _path + "[" + str(index) + "]")
                for index, item in enumerate(_base_iter(value))
            )
        finally:
            seen.discard(id(value))
    return False


def panel_inputs(case):
    """The panel inputs of an adjudication case, with the ground
    truth label reference held apart from them. One barred key
    rule stands for the former and the validator alike, read
    recursively at every depth: ground truth keys, derived ground
    truth keys, and the membership, label, and honesty keys never
    stand in a formed panel set."""
    if isinstance(case, dict):
        return _panel_clean(case)
    return _panel_clean(dict(case))


def validate_panel_inputs(inputs):
    """A panel input set containing the ground truth label, or a
    field derived from it, at any depth, fails."""
    if not isinstance(inputs, dict):
        return False
    try:
        return not _panel_carries_barred(inputs)
    except (ValueError, RecursionError):
        return False


def adjudicate(case, accuracy_value=None, assumption_set=None, row=None,
               error_direction=None, outcome=None, derived_from=None):
    """A behavioural adjudication outcome at decision record level.
    The outcome travels with the arbiter accuracy value applied,
    its assumption set and row reference, and the error direction
    named beside the value. The accuracy value may not be derived
    from panel size, band gates, or fee size."""
    def fail(message):
        error = ValueError(message)
        error.failure_class = adjudication_input_failure_class()
        raise error
    if derived_from in ("panel size", "band gates", "fee size"):
        fail("the accuracy value may not be derived from panel size, band gates, or fee size")
    if accuracy_value is None or assumption_set is None or row is None or error_direction is None:
        fail("an outcome travels with its accuracy value, assumption set and row, and error direction")
    if isinstance(accuracy_value, bool) or not isinstance(accuracy_value, (int, float)) or not 0 <= accuracy_value <= 1:
        fail("the arbiter accuracy value stands outside its probability range")
    if outcome is None:
        outcome = "no determination"
    elif not (isinstance(outcome, str) and (
            str.__eq__(outcome, "slashable")
            or str.__eq__(outcome, "not slashable"))):
        fail("the adjudication outcome stands outside the stated vocabulary")
    formed = panel_inputs(case)
    if isinstance(case, dict):
        remainder = {
            key: value for key, value in dict.items(case)
            if key not in ("ground_truth_label_reference", "ground_truth_label", "label_reference")
        }
    else:
        remainder = {
            key: value for key, value in dict(case).items()
            if key not in ("ground_truth_label_reference", "ground_truth_label", "label_reference")
        }
    if _panel_carries_barred(remainder):
        fail("the formed panel set carries a barred ground truth or membership key")
    return {
        "case_identifier": _get(case, "case_identifier"),
        "outcome": outcome,
        "arbiter_accuracy_value": accuracy_value,
        "assumption_set_identifier": assumption_set,
        "row_identifier": row,
        "error_direction": error_direction,
        "panel_inputs": formed,
        "ground_truth_label_reference": _get(case, "ground_truth_label_reference"),
        "excluded_class_counts_and_shares": _get(case, "excluded_class_counts_and_shares"),
        "form": "decision record level",
    }


def adjudication_outcome(case, **kwargs):
    return adjudicate(case, **kwargs)


def challenge_outcome(case, **kwargs):
    return adjudicate(case, **kwargs)


def adjudication_input_failure_class():
    """Manager Entry 6: the MOD-05 challenge or adjudication input
    failure is recorded in the run record only. It does not set the
    run status to failed."""
    return {"recorded_in": "run record only", "run_status": None}


def excluded_class_counts(cases):
    """The excluded adjudication class counts and shares for the
    four excluded classes, carried in every run record."""
    cases = list(cases)
    counts = {name: 0 for name in EXCLUDED_CLASSES}
    for case in cases:
        name = _get(case, "excluded_class")
        if name in counts:
            counts[name] += 1
    total = len(cases)
    return {
        name: {
            "count": counts[name],
            "share": proportion_record(counts[name], total) if total else UNKNOWN_SHARE,
        }
        for name in EXCLUDED_CLASSES
    }


def accuracy_ranges_stand_unmerged(ranges):
    """The four set ranges beside the accuracy points stand
    unmerged: exactly four ranges, kept apart, never one range."""
    ranges = list(ranges)
    return len(ranges) == 4 and len({str(item) for item in ranges}) == 4


def validate_headline_adjudication_claim(family_record, run_record):
    """A family record that fixes no excluded share threshold
    supports no headline adjudication claim. A claim fails
    validation where the total excluded share passes the fixed
    threshold, or where the adjacent arbitrated share for the
    forged vouch basis is above zero while NQ-56 stands open."""
    if not isinstance(family_record, dict) or not isinstance(run_record, dict):
        return False
    threshold = family_record.get("excluded_share_threshold")
    if threshold is None:
        return False
    counts = run_record.get("excluded_class_counts_and_shares") or {}
    if not isinstance(counts, dict) or not counts:
        return False
    if FORGED_VOUCH_BASIS_CLASS not in counts:
        return False
    total_share = 0.0
    forged_share = 0.0
    for name, entry in counts.items():
        share = entry.get("share") if isinstance(entry, dict) else None
        if isinstance(share, dict):
            if not validate_proportion(share):
                return False
            value = share["numerator"] / share["denominator"]
        elif isinstance(share, (int, float)) and not isinstance(share, bool):
            value = share
        else:
            return False
        total_share += value
        if name == FORGED_VOUCH_BASIS_CLASS:
            forged_share = value
    if total_share > threshold:
        return False
    if forged_share > 0:
        return False
    return True

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

import itertools
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


def _freeze(value, _memo=None):
    """Copy a value through base class readings only.

    Dict parts stand read through the base dict items reading,
    and list, tuple, set, and frozenset parts through their
    base iteration readings, so no reading a part itself
    supplies directs the copy. A set part stands rebuilt
    through the plain set constructor and a frozenset part
    through the plain frozenset constructor, never through a
    constructor the part itself supplies. A part in no
    container form stands copied as itself. Shared and cyclic
    container parts stand preserved through the memo, as a
    plain deep copy preserves them."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_freeze(key, _memo)] = _freeze(item, _memo)
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _freeze(item, _memo) for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _freeze(item, _memo) for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, frozenset):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = frozenset(
            _freeze(item, _memo) for item in frozenset.__iter__(value))
        _memo[id(value)] = copied
        return copied
    if isinstance(value, set):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = set(
            _freeze(item, _memo) for item in set.__iter__(value))
        _memo[id(value)] = copied
        return copied
    return value


# ---------------------------------------------------------------------------
# Work credit and proportions, Shape 14
# ---------------------------------------------------------------------------

def proportion_record(numerator, denominator):
    """A proportion stored only with its numerator and denominator
    stored apart. A proportion without its parts is refused."""
    if numerator is None or denominator is None:
        missing = []
        if numerator is None:
            missing.append("numerator")
        if denominator is None:
            missing.append("denominator")
        raise ValueError(
            "proportion_record stands refused: the "
            + " and ".join(missing) + " stands missing, a proportion "
            "is stored only with its numerator and denominator "
            "stored apart, and no proportion stands stored")
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
        if not isinstance(order_record, dict) or not order_record.get("order"):
            raise ValueError(
                "band_membership stands refused: no order stands "
                "stated in the evaluation order, eligibility "
                "judgements require the evaluation order the record "
                "states, and no band stands returned")
        raise ValueError(
            "band_membership stands refused: the evaluation order "
            "stands presented as ruled, eligibility judgements "
            "require the evaluation order the record states as a "
            "recommendation and not as ruled, and no band stands "
            "returned")
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


def _score_share_ground(share):
    if not isinstance(share, dict):
        return "the share stands in no record form"
    if not dict.__contains__(share, "numerator"):
        return "the share carries no numerator"
    if not dict.__contains__(share, "denominator"):
        return "the share carries no denominator"
    denominator = dict.__getitem__(share, "denominator")
    if isinstance(denominator, bool) or not isinstance(
            denominator, (int, float)):
        return "the denominator of the share stands in no numeric form"
    if _base_number(denominator) == 0:
        return (
            "the denominator of the share stands at 0, so no "
            "quotient stands from its parts")
    if dict.__contains__(share, "quotient") and dict.__getitem__(
            share, "quotient") is not None:
        return (
            "the stored quotient of the share disagrees with its "
            "numerator and denominator parts")
    return (
        "the share does not stand stored with its numerator and "
        "denominator parts apart in valid form")


def score_bearing_figure(envelope_value, share):
    """The per eligible identity score bearing figure: the envelope
    value multiplied by the share."""
    if not validate_proportion(share):
        raise ValueError(
            "score_bearing_figure stands refused: "
            + _score_share_ground(share)
            + ", and no score bearing figure stands returned")
    return envelope_value * share["numerator"] / share["denominator"]


def population_figure(envelope_value, shares, record_state=None):
    """A population figure under the double application rule: per
    epoch, the score bearing figure multiplied by the share again,
    and the population average as the mean of the corrected per
    epoch figures, as the final step. The derivation names its
    record state. A single application figure is not this figure."""
    if record_state is None:
        raise ValueError(
            "population_figure stands refused: the record_state "
            "stands missing, the derivation names its record state, "
            "and no population figure stands returned")
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
    else:
        return False
    if not entries:
        return False
    degree_log = record.get("degree_distribution_log")
    if not isinstance(degree_log, (list, tuple, dict)):
        return False
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
    "\u03c9": "w", "\u03b6": "z", "\u03b7": "e", "\u03b8": "t", "\u03c6": "f",
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
    "\u1d31": "e", "\u1d38": "l", "\u1d3c": "o", "\u1d40": "t",
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


_LETTER_MAPS = (
    _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
    _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
)

COMBINED_TEXT_BOUND = 4096


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies. A value that is not a text form stores
    no text, so no name stands judged from a string reading
    a non text value itself supplies, and its stored text
    stands as the empty text, in the cured MOD-01 form. A
    bytes value stands judged on its stored bytes, decoded
    as UTF-8 with undecodable bytes dropped, never through
    a string reading a bytes subclass itself supplies, so a
    bytes form keeps the standing its stored name carries. A
    bytearray value and a memoryview value stand judged the
    same way, on the bytes they store or view decoded the
    same way, in the helper form limb 6 of the Round 10
    settlement states."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


def _decomposed_characters(key):
    """The characters the fold reads, on the counting basis the
    combined text bound stands on: the key lowercased, put
    through compatibility decomposition, lowercased again so a
    capital form a decomposition yields stands in its lower case
    form, with combining marks dropped. The modifier small
    capital letters reduce under this decomposition to the
    capital letters they stand for, and so stand read through
    the readings the letter maps record for them. The key text
    stands taken from the stored characters through the base
    class string form, so a string reading a handed key supplies
    never stands as the text judged."""
    decomposed = unicodedata.normalize(
        "NFKD", _stored_text(key).lower()).lower()
    return [
        character for character in decomposed
        if not unicodedata.category(character).startswith("M")
    ]


def _character_options(character):
    """The distinct readings one decomposed character carries:
    the reading each letter map of the fold records for it, with
    the character itself standing as its reading under a map
    that records none for it. The combined text count of a key
    is the size of the running set of distinct combined texts
    built position by position over these option sets."""
    return {
        letter_map.get(character, character)
        for letter_map in _LETTER_MAPS
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
    both the homoglyph map and the transliteration map, and under
    every combination of the two readings position by position, so
    a key needing the transliteration reading at one position and
    the homoglyph reading at another position of the same word
    stands read as the word it spells, as the MOD-10 fold reads
    it. The combination limb enumerates the combined texts while
    their running distinct count stands at or under the stated
    bound of 4096 combined texts, counted on the basis
    _character_options states; past that bound the enumeration
    stands set aside and the barred reading of the key stands
    judged by _combined_key_barred, which reads the same
    combination limb position by position and so abandons no
    combined reading."""
    readings = []

    def add(transformed):
        plain = "".join(
            character for character in transformed
            if character.isalnum())
        if plain and plain not in readings:
            readings.append(plain)

    characters = _decomposed_characters(key)
    for letter_map in _LETTER_MAPS:
        base = "".join(
            letter_map.get(character, character)
            for character in characters
        )
        add(base)
        add("".join(_LEET_MAP.get(character, character)
                    for character in base))
        add("".join(_LEET_L_MAP.get(character, character)
                    for character in base))
        add("".join(character for character in base
                    if not character.isdigit()))
    expanded = {""}
    for character in characters:
        options = _character_options(character)
        combined = {
            prefix + option
            for prefix in expanded
            for option in options
        }
        if len(combined) > COMBINED_TEXT_BOUND:
            expanded = None
            break
        expanded = combined
    if expanded is not None:
        for base in expanded:
            add(base)
            add("".join(_LEET_MAP.get(character, character)
                        for character in base))
            add("".join(_LEET_L_MAP.get(character, character)
                        for character in base))
            add("".join(character for character in base
                        if not character.isdigit()))
    return tuple(readings)


def _character_variants(character):
    """Every folded form one decomposed character can contribute
    to a combined reading: each of its readings under the letter
    maps, taken plain, under each digit substitution reading,
    and with digits dropped, each form holding only its letter
    and digit characters, as the add limb of _folded_readings
    holds a whole combined text."""
    variants = set()
    for base in _character_options(character):
        for transformed in (
            base,
            "".join(_LEET_MAP.get(part, part) for part in base),
            "".join(_LEET_L_MAP.get(part, part) for part in base),
            "".join(part for part in base if not part.isdigit()),
        ):
            variants.add("".join(
                part for part in transformed if part.isalnum()))
    return variants


def _combined_matches_exact(variant_sets, target):
    states = {0}
    for variants in variant_sets:
        following = set()
        for state in states:
            for variant in variants:
                if not variant:
                    following.add(state)
                elif target.startswith(variant, state):
                    following.add(state + len(variant))
        states = following
        if not states:
            return False
    return len(target) in states


def _combined_contains(variant_sets, target):
    states = set()
    for variants in variant_sets:
        current = states | {0}
        following = set()
        for state in current:
            for variant in variants:
                if not variant:
                    following.add(state)
                    continue
                if target.startswith(variant, state):
                    following.add(state + len(variant))
                if state and target[state:] and variant.startswith(
                        target[state:]):
                    return True
                if state == 0:
                    for start in range(1, len(variant)):
                        suffix = variant[start:]
                        if suffix.startswith(target):
                            return True
                        if target.startswith(suffix):
                            following.add(len(suffix))
        if len(target) in following:
            return True
        states = following
    return False


def _combined_key_barred(key):
    """Whether any combined reading of the key stands barred,
    judged position by position over the per character variants
    without enumerating the combined texts, so the judgement
    stands the same inside the combined text bound and past it.
    The forms judged are the forms _panel_key_barred judges on
    an enumerated reading: a reading standing in the folded
    exact set of the panel barred keys, a reading carrying the
    membership part, and a reading carrying the groundtruth
    part."""
    variant_sets = [
        _character_variants(character)
        for character in _decomposed_characters(key)
    ]
    for target in _PANEL_BARRED_FOLDED_EXACT:
        if _combined_matches_exact(variant_sets, target):
            return True
    for target in ("membership", "groundtruth"):
        if _combined_contains(variant_sets, target):
            return True
    return False


_PANEL_BARRED_FOLDED_EXACT = frozenset(
    reading
    for name in _PANEL_BARRED_KEYS
    for reading in _folded_readings(name)
)


def _joined_stored_text(key):
    """The stored text parts of a container key joined in
    order, with no separator added, read leaf by leaf through
    _stored_text at any depth, on an explicit stack, in the
    joined reading limb 3 of the Round 10 settlement states
    on the MOD-04 model text. A container part already visited
    on this walk contributes its text once, so a cyclic part
    adds nothing on a revisit."""
    texts = []
    seen = set()
    stack = [key]
    while stack:
        part = stack.pop()
        if isinstance(part, (dict, list, tuple, set, frozenset)):
            if id(part) in seen:
                continue
            seen.add(id(part))
            if isinstance(part, dict):
                parts = list(dict.keys(part))
            else:
                parts = list(_base_iter(part))
            stack.extend(reversed(parts))
        else:
            texts.append(_stored_text(part))
    return "".join(texts)



_UNORDERED_JOIN_PART_BOUND = 7

_JOIN_CANDIDATE_BOUND = 5040

_SEG_JOIN_CANDIDATE_BOUND = 131072

_SEG_FOLDED_CANDIDATE_BOUND = 20000


def _join_container_parts(node):
    """The parts a container stores, read through base class
    operations only, in the iteration order the container
    stands in for this process."""
    if isinstance(node, dict):
        return list(dict.keys(node))
    return list(_base_iter(node))


def _has_unordered_split(value):
    """Whether a key carries a set or frozenset part holding
    two or more parts, found on an iterative walk, so no
    recursion stands spent on a key that carries none."""
    seen = set()
    stack = [value]
    while stack:
        node = stack.pop()
        if isinstance(node, (dict, list, tuple, set, frozenset)):
            if id(node) in seen:
                continue
            seen.add(id(node))
            parts = _join_container_parts(node)
            if isinstance(node, (set, frozenset)) and len(parts) >= 2:
                return True
            stack.extend(parts)
    return False


def _joined_text_candidates(value, _active=None, _cap=None):
    """Every joined stored text a container key can stand in.

    An ordered container (tuple, list, or a dict read by its
    keys) contributes the join of its parts in their stored
    order, exactly as the standing joined reading reads it. An
    unordered container (set or frozenset) stores no order, so
    its iteration order, which the hash seed governs, is no
    reading of it: the candidates are the joins under every
    ordering of its direct parts, each part contributing every
    candidate of its own in the same form, so a barred name
    split across the parts of an unordered container stands
    among the candidates in every iteration order. The form is
    complete for an unordered container holding at most
    _UNORDERED_JOIN_PART_BOUND direct parts and while the
    distinct candidates of one container stand at or under
    _JOIN_CANDIDATE_BOUND. Past either bound the container
    contributes its iteration order join alone, beside the
    standing per part readings, as the paper for this cure
    states. A part already on the walk path contributes the
    empty text, so a cyclic part cannot loop the read. The walk stands iterative on an explicit stack of frames, so a container chain at any depth stands answered on the same terms and no recursion stands spent per container level. A caller may state a wider candidate cap through _cap, as the segmentation readings do, without moving the standing bound this act states for its other callers."""
    if _cap is None:
        _cap = _JOIN_CANDIDATE_BOUND
    if _active is None:
        _active = set()

    def combine(node, parts, child):
        if (
            isinstance(node, (set, frozenset))
            and 2 <= len(parts) <= _UNORDERED_JOIN_PART_BOUND
        ):
            orders = list(
                itertools.permutations(range(len(parts))))
        else:
            orders = [tuple(range(len(parts)))]
        out = []
        seen = set()
        for order in orders:
            total = 1
            for index in order:
                total *= len(child[index])
            if total > _cap:
                text = "".join(
                    child[index][0]
                    for index in range(len(parts)))
                if text not in seen:
                    seen.add(text)
                    out.append(text)
                continue
            for combo in itertools.product(
                    *(child[index] for index in order)):
                text = "".join(combo)
                if text not in seen:
                    seen.add(text)
                    out.append(text)
                    if len(out) >= _cap:
                        return tuple(out)
        return tuple(out)

    stack = []
    node = value
    result = None
    while True:
        if result is None:
            if not isinstance(node, (dict, list, tuple, set, frozenset)):
                result = (_stored_text(node),)
            elif id(node) in _active:
                result = ("",)
            else:
                _active.add(id(node))
                parts = _join_container_parts(node)
                if parts:
                    stack.append([node, parts, [], 0])
                    node = parts[0]
                    continue
                _active.discard(id(node))
                result = combine(node, parts, [])
        while result is not None:
            if not stack:
                return result
            frame = stack[-1]
            frame[2].append(result)
            frame[3] += 1
            if frame[3] < len(frame[1]):
                node = frame[1][frame[3]]
                result = None
                break
            stack.pop()
            _active.discard(id(frame[0]))
            result = combine(frame[0], frame[1], frame[2])


def _seg_tiles_exact(options, target):
    """Whether the parts can stand in some order so that their
    joined reading, in the reading space the options stand in,
    stands exactly as the target. The judgement runs as a
    segmentation of the target over the parts: a state is a
    position in the target beside the set of parts already
    placed, a step places one unused part whose reading stands
    as the next segment of the target, and a part whose
    readings carry the empty text may stand placed without
    advancing the position, so it is checked at the end rather
    than placed. No ordering of the parts is ever listed, and
    the state count stands at most at the target length plus
    one times two to the number of parts that can contribute a
    segment of the target, in place of the factorial count of
    orderings. A failed state is never searched twice."""
    count = len(options)
    usable = []
    for opts in options:
        matching = sorted({o for o in opts if o and o in target})
        if not matching and "" not in opts:
            return False
        usable.append(matching)

    def remaining_can_vanish(mask):
        return all(
            "" in options[i]
            for i in range(count) if not (mask >> i) & 1)

    failed = set()
    stack = [[0, 0, None, 0]]
    while stack:
        frame = stack[-1]
        pos, mask = frame[0], frame[1]
        if pos == len(target):
            if remaining_can_vanish(mask):
                return True
            failed.add((pos, mask))
            stack.pop()
            continue
        if frame[2] is None:
            if (pos, mask) in failed:
                stack.pop()
                continue
            frame[2] = [
                (i, o) for i in range(count)
                if not (mask >> i) & 1
                for o in usable[i] if target.startswith(o, pos)]
        if frame[3] < len(frame[2]):
            i, o = frame[2][frame[3]]
            frame[3] += 1
            stack.append([pos + len(o), mask | (1 << i), None, 0])
        else:
            failed.add((pos, mask))
            stack.pop()
    return False


def _seg_tiles_carrying(options, pattern):
    """The set of parts that can stand as one unbroken block,
    in some order, so that their joined reading carries the
    pattern inside it, or None where no such block stands. The
    block is found as a segmentation of the pattern: its first
    part contributes a suffix of its reading, each middle part
    contributes its whole reading as one segment of the
    pattern, and its last part contributes a prefix of its
    reading, each part used at most once. Parts outside the
    block stand free on either side of it, so the block alone
    decides the carrying. No ordering of the parts is ever
    listed, and the state count stands at most at the pattern
    length plus one times two to the number of parts that can
    contribute a segment of the pattern."""
    if not pattern:
        return None
    count = len(options)
    opts_list = [sorted({o for o in opts if o}) for opts in options]
    failed = set()
    stack = [[0, 0, None, 0]]
    while stack:
        frame = stack[-1]
        pos, mask = frame[0], frame[1]
        if frame[2] is None:
            if (pos, mask) in failed:
                stack.pop()
                continue
            moves = []
            for i in range(count):
                if (mask >> i) & 1:
                    continue
                for o in opts_list[i]:
                    if mask == 0:
                        if pattern in o:
                            return 1 << i
                        for j in range(
                                1, min(len(o), len(pattern)) + 1):
                            if o.endswith(pattern[:j]):
                                if j == len(pattern):
                                    return 1 << i
                                moves.append((j, i))
                    elif pos + len(o) <= len(pattern):
                        if o == pattern[pos:pos + len(o)]:
                            if pos + len(o) == len(pattern):
                                return mask | (1 << i)
                            moves.append((pos + len(o), i))
                    elif o.startswith(pattern[pos:]):
                        return mask | (1 << i)
            frame[2] = moves
        if frame[3] < len(frame[2]):
            npos, i = frame[2][frame[3]]
            frame[3] += 1
            stack.append([npos, mask | (1 << i), None, 0])
        else:
            failed.add((pos, mask))
            stack.pop()
    return None


def _seg_unordered_nodes(key):
    """Every set or frozenset standing inside a key, at any
    depth, found on an iterative walk through base readings,
    each beside the parts it directly stores."""
    seen = set()
    stack = [key]
    nodes = []
    while stack:
        node = stack.pop()
        if isinstance(node, (dict, list, tuple, set, frozenset)):
            if id(node) in seen:
                continue
            seen.add(id(node))
            parts = _join_container_parts(node)
            if isinstance(node, (set, frozenset)) and len(parts) >= 2:
                nodes.append((node, parts))
            stack.extend(parts)
    return nodes




def _seg_universe(targets, patterns):
    """Every substring of the targets and patterns a
    segmentation judgement in this module tiles or carries:
    the only texts a part reading can contribute to such a
    judgement as a whole segment."""
    universe = set()
    for text in list(targets) + list(patterns):
        for start in range(len(text)):
            for stop in range(start + 1, len(text) + 1):
                universe.add(text[start:stop])
    return universe


def _seg_prefixes(universe):
    """Every prefix of a universe text, the closure the
    formable set computation walks through."""
    prefixes = set()
    for text in universe:
        for stop in range(1, len(text) + 1):
            prefixes.add(text[:stop])
    return prefixes


def _seg_formable(node, universe, prefixes, folded, _active=None):
    """The universe texts one part can join to exactly, as a
    set beside whether the part can join to the empty text.
    The computation walks the part structure in the form the
    segmentation stated: an ordered container joins its
    parts in order, an unordered container joins its parts
    in any order, and no joined candidate is ever listed, so
    a composite part whose candidates pass the kept helper
    cut still contributes every segment of a target or a
    pattern it can stand as. A part already on the walk path
    contributes the empty text, as the candidate act states."""
    if _active is None:
        _active = set()
    if not isinstance(node, (dict, list, tuple, set, frozenset)):
        if folded:
            readings = set(_folded_readings(node))
        else:
            readings = {_stored_text(node).lower()}
        return (
            {reading for reading in readings if reading in universe},
            "" in readings or not readings)
    if id(node) in _active:
        return (set(), True)
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        child = [
            _seg_formable(part, universe, prefixes, folded, _active)
            for part in parts]
    finally:
        _active.discard(id(node))
    options = []
    can_empty = True
    for forms, empty in child:
        options.append(forms | ({""} if empty else set()))
        can_empty = can_empty and empty
    if isinstance(node, (set, frozenset)) and len(parts) >= 2:
        if any(not opts for opts in options):
            return (set(), can_empty)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        reached = {0: {""}}
        full = (1 << len(parts)) - 1
        queue = [0]
        cursor = 0
        bounded = False
        while cursor < len(queue):
            mask = queue[cursor]
            cursor += 1
            for index in range(len(parts)):
                if (mask >> index) & 1:
                    continue
                joined = {
                    head + tail
                    for head in reached[mask]
                    for tail in options[index]
                    if head + tail == "" or head + tail in prefixes}
                if not joined:
                    continue
                new_mask = mask | (1 << index)
                if new_mask not in reached:
                    if len(reached) >= bound:
                        bounded = True
                        break
                    reached[new_mask] = set()
                    queue.append(new_mask)
                reached[new_mask].update(joined)
            if bounded:
                break
        if bounded:
            acc = {""}
            for opts in options:
                acc = {
                    head + tail
                    for head in acc for tail in opts
                    if head + tail == "" or head + tail in prefixes}
                if not acc:
                    break
            return (acc & universe, can_empty)
        return (reached.get(full, set()) & universe, can_empty)
    acc = {""}
    for opts in options:
        acc = {
            head + tail
            for head in acc for tail in opts
            if head + tail == "" or head + tail in prefixes}
        if not acc:
            break
    return (acc & universe, can_empty)

def _seg_part_readings(node, folded):
    """The readings of one leaf part in one reading space: the
    folded readings in folded space, the lowered stored text
    in plain space."""
    if folded:
        return set(_folded_readings(node))
    return {_stored_text(node).lower()}


def _seg_part_can_equal(node, text, folded, _active=None):
    """Whether some whole reading of one part stands exactly
    as the text, judged through the formable computation, so
    no joined candidate of the part stands listed."""
    if _active is None:
        _active = set()
    if not isinstance(node, (dict, list, tuple, set, frozenset)):
        return text in _seg_part_readings(node, folded)
    if id(node) in _active:
        return text == ""
    universe = _seg_universe((text,), ()) if text else set()
    try:
        forms, can_empty = _seg_formable(
            node, universe, _seg_prefixes(universe), folded)
    except RecursionError:
        return False
    if not text:
        return can_empty
    return text in forms


def _seg_part_can_start(node, text, folded, _active=None):
    """Whether some whole reading of one part begins with the
    text. The judgement walks the part structure: an ordered
    part is consumed in its stored order and an unordered
    part in any order of its subparts, each step either
    placing one subpart as an exact piece of the text, letting
    one subpart begin with the remainder, or passing a subpart
    that can stand empty. The state count stands bounded by
    the stated candidate cap of the reading space, in the
    form settlement S-10 states, and a part past the bound
    contributes no opening form through this act."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (dict, list, tuple, set, frozenset)):
        return any(
            reading.startswith(text)
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_start(parts[0], text, folded, _active)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0) if unordered else (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, pos = stack.pop()
            if pos == len(text):
                return True
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                indices = [mask] if mask < len(parts) else []
            for index in indices:
                part = parts[index]
                if _seg_part_can_start(
                        part, text[pos:], folded, _active):
                    return True
                new_mask = (
                    mask | (1 << index) if unordered else index + 1)
                for stop in range(pos + 1, len(text) + 1):
                    if _seg_part_can_equal(
                            part, text[pos:stop], folded, _active):
                        state = (new_mask, stop)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                if _seg_part_can_equal(part, "", folded, _active):
                    state = (new_mask, pos)
                    if state not in seen:
                        seen.add(state)
                        stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_part_can_end(node, text, folded, _active=None):
    """Whether some whole reading of one part ends with the
    text, the mirror form of _seg_part_can_start, walked from
    the closing subpart backwards under the same stated bound."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (dict, list, tuple, set, frozenset)):
        return any(
            reading.endswith(text)
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_end(parts[0], text, folded, _active)
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, matched = stack.pop()
            if matched == len(text):
                return True
            rest = text[:len(text) - matched]
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                index = len(parts) - 1 - mask
                indices = [index] if index >= 0 else []
            for index in indices:
                part = parts[index]
                if _seg_part_can_end(
                        part, rest, folded, _active):
                    return True
                new_mask = (
                    mask | (1 << index) if unordered else mask + 1)
                for start_at in range(0, len(rest)):
                    piece = rest[start_at:]
                    if _seg_part_can_equal(
                            part, piece, folded, _active):
                        state = (new_mask, matched + len(piece))
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                if _seg_part_can_equal(part, "", folded, _active):
                    state = (new_mask, matched)
                    if state not in seen:
                        seen.add(state)
                        stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_part_can_contain(node, text, folded, _active=None):
    """Whether some whole reading of one part carries the
    text inside it: the text stands inside one subpart, or it
    spans subpart boundaries, one subpart ending with its
    opening, middle subparts standing as its exact pieces,
    and one subpart beginning with its closing. The walk
    stands bounded as _seg_part_can_start states."""
    if not text:
        return True
    if _active is None:
        _active = set()
    if not isinstance(node, (dict, list, tuple, set, frozenset)):
        return any(
            text in reading
            for reading in _seg_part_readings(node, folded))
    if id(node) in _active:
        return False
    _active.add(id(node))
    try:
        parts = _join_container_parts(node)
        if not parts:
            return False
        if len(parts) == 1:
            return _seg_part_can_contain(parts[0], text, folded, _active)
        for part in parts:
            if _seg_part_can_contain(part, text, folded, _active):
                return True
        bound = (
            _SEG_FOLDED_CANDIDATE_BOUND if folded
            else _SEG_JOIN_CANDIDATE_BOUND)
        unordered = (
            isinstance(node, (set, frozenset)) and len(parts) >= 2)
        start = (0, 0)
        seen = {start}
        stack = [start]
        while stack:
            mask, pos = stack.pop()
            if pos == len(text):
                return True
            if unordered:
                indices = [
                    i for i in range(len(parts))
                    if not (mask >> i) & 1]
            else:
                indices = [mask] if mask < len(parts) else []
            for index in indices:
                part = parts[index]
                new_mask = (
                    mask | (1 << index) if unordered else index + 1)
                if pos == 0:
                    if _seg_part_can_end(part, text, folded, _active):
                        return True
                    for stop in range(1, len(text)):
                        if _seg_part_can_end(
                                part, text[:stop], folded, _active):
                            state = (new_mask, stop)
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    if not unordered:
                        state = (new_mask, 0)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
                else:
                    if _seg_part_can_start(
                            part, text[pos:], folded, _active):
                        return True
                    for stop in range(pos + 1, len(text) + 1):
                        if _seg_part_can_equal(
                                part, text[pos:stop], folded, _active):
                            if stop == len(text):
                                return True
                            state = (new_mask, stop)
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    if _seg_part_can_equal(part, "", folded, _active):
                        state = (new_mask, pos)
                        if state not in seen:
                            seen.add(state)
                            stack.append(state)
            if len(seen) > bound:
                return False
        return False
    finally:
        _active.discard(id(node))


def _seg_parts_carry_edge(parts, options, pattern, folded):
    """Whether a barred part stands tiled over the direct
    parts of one unordered container where one part
    contributes only its edge: a part whose whole reading
    carries the pattern inside it, or a first part whose
    whole reading ends with the opening of the pattern,
    middle parts standing as exact pieces of it through
    their stated options, and a last part whose whole
    reading begins with its closing. The edge forms stand
    judged through the part predicates above, so a composite
    part past the candidate caps contributes its edge as
    settlement S-4 governs, in plain and folded spaces alike."""
    if not any(
            isinstance(part, (dict, list, tuple, set, frozenset))
            for part in parts):
        return False
    for part in parts:
        if not isinstance(part, (dict, list, tuple, set, frozenset)):
            continue
        try:
            if _seg_part_can_contain(part, pattern, folded):
                return True
        except RecursionError:
            continue
    count = len(parts)
    for first in range(count):
        for cut in range(1, len(pattern)):
            try:
                if not _seg_part_can_end(
                        parts[first], pattern[:cut], folded):
                    continue
            except RecursionError:
                continue
            failed = set()
            stack = [(1 << first, cut)]
            while stack:
                mask, pos = stack.pop()
                if pos >= len(pattern):
                    return True
                if (mask, pos) in failed:
                    continue
                for index in range(count):
                    if (mask >> index) & 1:
                        continue
                    try:
                        if _seg_part_can_start(
                                parts[index], pattern[pos:], folded):
                            return True
                    except RecursionError:
                        pass
                    for option in options[index]:
                        if option and pattern.startswith(option, pos):
                            if pos + len(option) >= len(pattern):
                                return True
                            stack.append(
                                (mask | (1 << index),
                                 pos + len(option)))
                failed.add((mask, pos))
    return False

def _seg_plain_options(parts, _universe=None, _prefixes=None):
    """The plain readings of the direct parts of one unordered
    container: for each part, the lowered texts of every joined
    candidate the part itself stands in, taken under the wider
    segmentation candidate cap, beside every universe segment
    the part can join to exactly where a universe stands
    stated, so a composite part past the kept helper cut
    still contributes the segments a barred reading needs."""
    options = []
    for part in parts:
        texts = {
            text.lower()
            for text in _joined_text_candidates(
                part, _cap=_SEG_JOIN_CANDIDATE_BOUND)}
        if _universe is not None and isinstance(part, (dict, list, tuple, set, frozenset)):
            try:
                forms, can_empty = _seg_formable(
                    part, _universe, _prefixes, False)
            except RecursionError:
                forms, can_empty = set(), False
            texts |= forms
            if can_empty:
                texts.add("")
        options.append(texts)
    return options


def _seg_folded_options(parts, _universe=None, _prefixes=None):
    """The folded readings of the direct parts of one unordered
    container: for each part, every folded reading of every
    joined candidate the part itself stands in, under this
    module folded reading act, beside every universe segment
    the part can join to exactly where a universe stands
    stated, so a folded segment a composite part can stand
    as stands judged past the kept helper cut as well."""
    options = []
    for part in parts:
        readings = set()
        for text in _joined_text_candidates(
                part, _cap=_SEG_FOLDED_CANDIDATE_BOUND):
            readings.update(_folded_readings(text))
        if not readings:
            readings = {""}
        if _universe is not None and isinstance(part, (dict, list, tuple, set, frozenset)):
            try:
                forms, can_empty = _seg_formable(
                    part, _universe, _prefixes, True)
            except RecursionError:
                forms, can_empty = set(), False
            readings |= forms
            if can_empty:
                readings.add("")
        options.append(readings)
    return options


def _seg_unordered_barred(key):
    """Whether an unordered container standing inside a key
    joins, in some order of its direct parts, to a barred name
    under this module scalar barred judgement, judged by
    segmentation beside the kept candidate readings. The plain
    limb tiles the plain exact names and the plain barred parts
    of the scalar judgement over the lowered joined texts of
    the parts; the folded limb tiles its folded exact names
    and folded barred parts over the folded readings of the
    parts. Either limb standing barred bars the key, as a
    joined candidate standing barred bars it."""
    for node, parts in _seg_unordered_nodes(key):
        plain_universe = _seg_universe(
            _PANEL_BARRED_KEYS, ("ground_truth", "groundtruth"))
        plain = _seg_plain_options(
            parts, plain_universe, _seg_prefixes(plain_universe))
        for target in tuple(_PANEL_BARRED_KEYS):
            if _seg_tiles_exact(plain, target):
                return True
        for pattern in ("ground_truth", "groundtruth"):
            if _seg_tiles_carrying(plain, pattern) is not None:
                return True
        for pattern in ("ground_truth", "groundtruth"):
            if _seg_parts_carry_edge(parts, plain, pattern, False):
                return True
        folded_universe = _seg_universe(
            _PANEL_BARRED_FOLDED_EXACT, ("groundtruth", "membership"))
        folded = _seg_folded_options(
            parts, folded_universe, _seg_prefixes(folded_universe))
        for target in tuple(_PANEL_BARRED_FOLDED_EXACT):
            if _seg_tiles_exact(folded, target):
                return True
        for pattern in ("groundtruth", "membership"):
            if _seg_tiles_carrying(folded, pattern) is not None:
                return True
        for pattern in ("groundtruth", "membership"):
            if _seg_parts_carry_edge(parts, folded, pattern, True):
                return True
    return False


def _span_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _span_feed(pattern, state, text):
    current = state
    for character in text:
        if current == len(pattern):
            return current
        current = _span_prefix_state(pattern, current, character)
    return current


def _span_relevant(options, texts):
    """The readings of one block that can take part in a
    barred reading of the whole key, beside whether the block
    carries any other reading. A reading takes part where it
    stands as a segment of a target or a pattern, where it
    carries a pattern whole, where a suffix of it stands as
    the opening of a target or a pattern, or where a prefix
    of it stands as the closing of one."""
    relevant = set()
    other = False
    for option in options:
        if option == "":
            relevant.add(option)
            continue
        keep = False
        for text in texts:
            if not text:
                continue
            if option in text or text in option:
                keep = True
                break
            for cut in range(1, min(len(option), len(text))):
                if option.endswith(text[:cut]):
                    keep = True
                    break
                if text[cut:] and option.startswith(text[cut:]):
                    keep = True
                    break
            if keep:
                break
        if keep:
            relevant.add(option)
        else:
            other = True
    return relevant, other


def _span_blocks(key):
    """The blocks a whole key reading stands built from, in
    the form settlement S-4 states: where the key itself
    stands unordered, its direct parts stand as blocks in
    no stated order; where it stands ordered, the leaf parts
    of its ordered nesting stand as blocks in their stored
    order, an unordered container standing among them as one
    block whose own readings its segmentation states. A
    container already on the walk path contributes nothing,
    as the candidate act states."""
    if isinstance(key, (set, frozenset)):
        return ("unordered", _join_container_parts(key))
    if isinstance(key, (dict, list, tuple)):
        blocks = []
        active = {id(key)}
        frames = [[_join_container_parts(key), 0, id(key)]]
        while frames:
            frame = frames[-1]
            parts, index, node_id = frame
            if index >= len(parts):
                frames.pop()
                active.discard(node_id)
                continue
            frame[1] = index + 1
            part = parts[index]
            if isinstance(part, (dict, list, tuple)):
                if id(part) in active:
                    continue
                active.add(id(part))
                frames.append(
                    [_join_container_parts(part), 0, id(part)])
            else:
                blocks.append(part)
        return ("ordered", blocks)
    return None


def _seg_spanning_barred(key, plain_targets, plain_patterns,
                         folded_targets, folded_patterns):
    """Whether a barred reading of the whole key stands on
    the joined and segmented readings across nesting and
    part boundaries, in the form settlement S-4 states: a
    name a single unordered container cannot tile on its own
    stands barred where a segment tiled inside one block
    stands completed by the blocks standing beside it, and
    a name whose segment stands inside one composite block
    past the kept helper cut stands barred on that block's
    formable segments. An ordered key keeps its stored
    order, judged position by position over the block
    readings with no ordering ever listed; an unordered key
    stands judged by the segmentation acts over its blocks.
    A block whose reading takes no part in the barred
    reading can only end a partial match, never carry one
    across itself, so the ordered judgement lets every block
    return the match to its opening state beside the states
    its taking part readings reach."""
    found = _span_blocks(key)
    if found is None:
        return False
    mode, blocks = found
    if not blocks:
        return False
    spaces = []
    if plain_targets or plain_patterns:
        spaces.append((plain_targets, plain_patterns, False))
    if folded_targets or folded_patterns:
        spaces.append((folded_targets, folded_patterns, True))
    for targets, patterns, folded in spaces:
        texts = list(targets) + list(patterns)
        universe = _seg_universe(targets, patterns)
        prefixes = _seg_prefixes(universe)
        options = []
        for block in blocks:
            if folded:
                opts = _seg_folded_options(
                    [block], universe, prefixes)[0]
            else:
                opts = _seg_plain_options(
                    [block], universe, prefixes)[0]
            options.append(_span_relevant(opts, texts))
        if mode == "unordered":
            pruned = [relevant for relevant, other in options]
            for target in targets:
                if _seg_tiles_exact(pruned, target):
                    return True
            for pattern in patterns:
                if _seg_tiles_carrying(pruned, pattern) is not None:
                    return True
        else:
            for pattern in patterns:
                states = {0}
                for relevant, other in options:
                    following = {0}
                    for state in states:
                        for option in relevant:
                            if option == "":
                                following.add(state)
                                continue
                            end = _span_feed(pattern, state, option)
                            if end == len(pattern):
                                return True
                            following.add(end)
                    states = following
            for target in targets:
                positions = {0}
                for relevant, other in options:
                    following = set()
                    for position in positions:
                        for option in relevant:
                            if target.startswith(option, position):
                                following.add(
                                    position + len(option))
                    positions = following
                    if not positions:
                        break
                if len(target) in positions:
                    return True
    return False



def _panel_key_barred(key):
    if isinstance(key, (dict, list, tuple, set, frozenset)):
        stack = [key]
        seen = set()
        containers = []
        while stack:
            part = stack.pop()
            if isinstance(part, (dict, list, tuple, set, frozenset)):
                if id(part) in seen:
                    continue
                seen.add(id(part))
                if isinstance(part, dict):
                    parts = list(dict.keys(part))
                else:
                    parts = list(_base_iter(part))
                containers.append((part, len(parts)))
                stack.extend(parts)
            elif _panel_key_barred(part):
                return True
        joined_standings = {}
        for container, part_count in containers:
            if part_count == 1:
                continue
            joined = _joined_stored_text(container)
            if not joined:
                continue
            if joined not in joined_standings:
                joined_standings[joined] = _panel_key_barred(joined)
            if joined_standings[joined]:
                return True
        if _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and _panel_key_barred(candidate):
                    return True
        if _seg_unordered_barred(key):
            return True
        if _seg_spanning_barred(
                key, tuple(_PANEL_BARRED_KEYS),
                ("ground_truth", "groundtruth"),
                tuple(_PANEL_BARRED_FOLDED_EXACT),
                ("groundtruth", "membership")):
            return True
        return False
    lowered = _stored_text(key).lower()
    if "ground_truth" in lowered or lowered in _PANEL_BARRED_KEYS:
        return True
    for reading in _folded_readings(key):
        if reading in _PANEL_BARRED_FOLDED_EXACT:
            return True
        if "groundtruth" in reading:
            return True
        if "membership" in reading:
            return True
    return _combined_key_barred(key)


PANEL_TRAVERSAL_DEPTH_BOUND = 100


def _panel_traversal_guard(value, depth, seen, path):
    if depth > PANEL_TRAVERSAL_DEPTH_BOUND:
        raise ValueError(
            "panel_inputs stands refused: panel traversal bound "
            "reached at " + (path or "root")
            + ": the value stands deeper than the stated bound of "
            + str(PANEL_TRAVERSAL_DEPTH_BOUND)
            + ", counted with the handed value standing at depth 0 "
            "and every container standing around a part counting "
            "toward that bound, and no panel inputs stand returned")
    if id(value) in seen:
        raise ValueError(
            "panel_inputs stands refused: panel traversal found a "
            "cycle at " + (path or "root")
            + ", and no panel inputs stand returned")


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


def _panel_clean(value, _depth=0, _seen=None, _path="", _walked=None):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        walked = _walked if _walked is not None else {}
        walked_key = (id(value), _depth)
        if walked_key in walked:
            return walked[walked_key]
        seen = _seen if _seen is not None else set()
        _panel_traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                if _panel_key_barred(value) and not any(
                        _panel_key_barred(key)
                        for key in dict.keys(value)):
                    walked[walked_key] = {}
                    return {}
                cleaned = {}
                for key, item in dict.items(value):
                    if _panel_key_barred(key):
                        continue
                    cleaned_key = _panel_clean(
                        key, _depth + 1, seen, _path + "/" + str(key),
                        walked)
                    cleaned[cleaned_key] = _panel_clean(
                        item, _depth + 1, seen, _path + "/" + str(key),
                        walked)
                walked[walked_key] = cleaned
                return cleaned
            if isinstance(value, list):
                cleaned = [
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]", walked)
                    for index, item in enumerate(_base_iter(value))
                ]
                walked[walked_key] = cleaned
                return cleaned
            if isinstance(value, tuple):
                cleaned = tuple(
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]", walked)
                    for index, item in enumerate(_base_iter(value))
                )
                walked[walked_key] = cleaned
                return cleaned
            if isinstance(value, frozenset):
                cleaned = frozenset(
                    _panel_clean(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]", walked)
                    for index, item in enumerate(_base_iter(value))
                )
                walked[walked_key] = cleaned
                return cleaned
            cleaned = {
                _panel_clean(
                    item, _depth + 1, seen,
                    _path + "[" + str(index) + "]", walked)
                for index, item in enumerate(_base_iter(value))
            }
            walked[walked_key] = cleaned
            return cleaned
        finally:
            seen.discard(id(value))
    return _panel_leaf_copy(value)


def _panel_carries_barred(value, _depth=0, _seen=None, _path="",
                            _walked=None):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        walked = _walked if _walked is not None else {}
        walked_key = (id(value), _depth)
        if walked_key in walked:
            return walked[walked_key]
        seen = _seen if _seen is not None else set()
        _panel_traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                result = (
                    _panel_key_barred(value) and not any(
                        _panel_key_barred(key)
                        for key in dict.keys(value))
                ) or any(
                    _panel_key_barred(key)
                    or _panel_carries_barred(
                        key, _depth + 1, seen, _path + "/" + str(key),
                        walked)
                    or _panel_carries_barred(
                        item, _depth + 1, seen, _path + "/" + str(key),
                        walked)
                    for key, item in dict.items(value)
                )
                walked[walked_key] = result
                return result
            result = any(
                _panel_carries_barred(
                    item, _depth + 1, seen,
                    _path + "[" + str(index) + "]", walked)
                for index, item in enumerate(_base_iter(value))
            )
            walked[walked_key] = result
            return result
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


def _panel_barred_keys(value, _depth=0, _seen=None):
    found = []
    if isinstance(value, dict):
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return found
        seen.add(id(value))
        for key, item in dict.items(value):
            if _panel_key_barred(key):
                found.append(str(key))
            found.extend(_panel_barred_keys(item, _depth + 1, seen))
    elif isinstance(value, (list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return found
        seen.add(id(value))
        for item in value:
            found.extend(_panel_barred_keys(item, _depth + 1, seen))
    return found


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
        missing = []
        if accuracy_value is None:
            missing.append("accuracy_value")
        if assumption_set is None:
            missing.append("assumption_set")
        if row is None:
            missing.append("row")
        if error_direction is None:
            missing.append("error_direction")
        fail(
            "adjudicate stands refused: the "
            + " and ".join(missing) + " argument stands missing, an "
            "outcome travels with its accuracy value, assumption "
            "set and row, and error direction, and no adjudication "
            "stands returned")
    if isinstance(accuracy_value, bool) or not isinstance(accuracy_value, (int, float)):
        fail(
            "adjudicate stands refused: the accuracy value stands "
            "in no numeric form: " + repr(accuracy_value)
            + ", an accuracy value stands as a number, and no "
            "adjudication stands returned")
    if not 0 <= accuracy_value <= 1:
        fail("the arbiter accuracy value stands outside its probability range")
    if outcome is None:
        outcome = "no determination"
    elif not (isinstance(outcome, str) and (
            str.__eq__(outcome, "slashable")
            or str.__eq__(outcome, "not slashable"))):
        fail(
            "the adjudication outcome stands outside the stated "
            "vocabulary: " + repr(outcome)
            + "; an outcome stands among slashable and not slashable")
    try:
        formed = panel_inputs(case)
    except ValueError as exc:
        error = ValueError(str(exc))
        error.failure_class = adjudication_input_failure_class()
        raise error from None
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
    try:
        barred_keys = _panel_barred_keys(remainder)
    except ValueError as exc:
        error = ValueError(str(exc))
        error.failure_class = adjudication_input_failure_class()
        raise error from None
    if barred_keys:
        fail(
            "the formed panel set carries a barred ground truth or "
            "membership key: " + ", ".join(barred_keys))
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

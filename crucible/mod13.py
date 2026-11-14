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


REPLICATION_STATEMENT_SENTENCES = (
    "The same program was run again on the same records and gave the result stated.",
    "No separate team rebuilt the program, and no separate team reran the work with its own tools.",
    "This check does not show that an independent team would get the same result.",
)
REPLICATION_STATEMENT = " ".join(REPLICATION_STATEMENT_SENTENCES)

COMPARABILITY_ITEM_ALIASES = {
    "code_version": ("code_version", "code version"),
    "rule_version_set": ("rule_version_set", "rule version set"),
    "dependency_manifest": (
        "dependency_manifest", "dependency manifest",
        "dependency_manifest_hash", "dependency manifest hash"),
    "compiler_identity_and_arithmetic_flags": (
        "compiler_identity_and_arithmetic_flags",
        "compiler identity and arithmetic flags",
        "compiler_identity", "compiler identity"),
    "library_versions": ("library_versions", "library versions"),
    "algorithm_selection_mode": (
        "algorithm_selection_mode", "algorithm selection mode",
        "algorithm_selection_modes"),
    "processor_class": ("processor_class", "processor class"),
    "worker_count_form": ("worker_count_form", "worker count form"),
    "hash_seed_setting": (
        "hash_seed_setting", "hash seed setting",
        "process_hash_seed_setting", "hash_seed"),
    "build_identifier": ("build_identifier", "build identifier"),
}
COMPARABILITY_ITEMS = tuple(COMPARABILITY_ITEM_ALIASES)


def _base_get(record, key):
    """Read one field through the base dict get, never through a
    get the record itself overrides."""
    if isinstance(record, dict):
        return dict.get(record, key)
    return None


def _strict_eq(first, second, _seen=None):
    """Judge two values by the values themselves, through base
    class comparisons that no part can override, at every nesting
    level. A part that overrides its own equality, for example a
    str subclass whose equality agrees with everything, is judged
    by the characters it stores, and the same rule runs inside
    plain lists, tuples, dicts, sets and frozensets nested at any
    depth the comparison acts read."""
    if first is None or second is None:
        return first is None and second is None
    if isinstance(first, bool) or isinstance(second, bool):
        if not (isinstance(first, bool) and isinstance(second, bool)):
            return False
        return bool.__eq__(first, second)
    if isinstance(first, str) or isinstance(second, str):
        if not (isinstance(first, str) and isinstance(second, str)):
            return False
        result = str.__eq__(first, second)
        return result if result is not NotImplemented else False
    if isinstance(first, bytes) or isinstance(second, bytes):
        if not (isinstance(first, bytes) and isinstance(second, bytes)):
            return False
        result = bytes.__eq__(first, second)
        return result if result is not NotImplemented else False
    if isinstance(first, dict) or isinstance(second, dict):
        if not (isinstance(first, dict) and isinstance(second, dict)):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        _seen = _seen | {pair}
        first_items = list(dict.items(first))
        second_items = list(dict.items(second))
        if len(first_items) != len(second_items):
            return False
        used = [False] * len(second_items)
        for first_key, first_value in first_items:
            matched = False
            for index in range(len(second_items)):
                if used[index]:
                    continue
                second_key, second_value = second_items[index]
                if _strict_eq(first_key, second_key, _seen) and _strict_eq(
                        first_value, second_value, _seen):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                return False
        return True
    if isinstance(first, list) or isinstance(second, list):
        if not (isinstance(first, list) and isinstance(second, list)):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        _seen = _seen | {pair}
        if list.__len__(first) != list.__len__(second):
            return False
        for index in range(list.__len__(first)):
            if not _strict_eq(
                    list.__getitem__(first, index),
                    list.__getitem__(second, index), _seen):
                return False
        return True
    if isinstance(first, tuple) or isinstance(second, tuple):
        if not (isinstance(first, tuple) and isinstance(second, tuple)):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        _seen = _seen | {pair}
        if tuple.__len__(first) != tuple.__len__(second):
            return False
        for index in range(tuple.__len__(first)):
            if not _strict_eq(
                    tuple.__getitem__(first, index),
                    tuple.__getitem__(second, index), _seen):
                return False
        return True
    if isinstance(first, (set, frozenset)) or isinstance(
            second, (set, frozenset)):
        if not (isinstance(first, (set, frozenset))
                and isinstance(second, (set, frozenset))):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        _seen = _seen | {pair}
        first_items = list(first)
        second_items = list(second)
        if len(first_items) != len(second_items):
            return False
        used = [False] * len(second_items)
        for first_item in first_items:
            matched = False
            for index in range(len(second_items)):
                if used[index]:
                    continue
                if _strict_eq(first_item, second_items[index], _seen):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                return False
        return True
    if isinstance(first, int) and isinstance(second, int):
        result = int.__eq__(first, second)
        if result is not NotImplemented:
            return result
        return float.__eq__(float(first), float(second))
    if isinstance(first, float) and isinstance(second, float):
        result = float.__eq__(first, second)
        return result if result is not NotImplemented else False
    if isinstance(first, (int, float)) and isinstance(second, (int, float)):
        return first == second
    if type(first) is not type(second):
        return False
    return first == second


def _replication_sentences_ok(record):
    """Return True only where the sentence form of a verdict
    record answers to the joined replication statement: the field
    stands present, in list or tuple form, holding exactly the
    canonical sentences in order, as read through the base dict
    get and judged by the strict value comparison, and the
    sentences joined with single spaces give the joined statement
    the record carries, which is the canonical statement."""
    if not isinstance(record, dict):
        return False
    sentences = dict.get(record, "replication_statement_sentences")
    if not isinstance(sentences, (list, tuple)):
        return False
    if len(sentences) == 0:
        return False
    if not _strict_eq(
            list(sentences), list(REPLICATION_STATEMENT_SENTENCES)):
        return False
    joined = dict.get(record, "replication_statement")
    if not isinstance(joined, str):
        return False
    constructed = " ".join(list(sentences))
    return (
        _strict_eq(constructed, REPLICATION_STATEMENT)
        and _strict_eq(joined, REPLICATION_STATEMENT)
    )


def _comparability_value(record, item):
    for alias in COMPARABILITY_ITEM_ALIASES[item]:
        value = _base_get(record, alias)
        if value is not None:
            return value
    return None


def _comparability(first, second):
    """The contracts C-02 and C-03 comparability check, in the
    consolidated form: the items the plan names, read from both
    records, with every differing item named."""
    differing = [
        item for item in COMPARABILITY_ITEMS
        if not _strict_eq(
            _comparability_value(first, item),
            _comparability_value(second, item))
    ]
    record = {
        "comparable": not differing,
        "not_comparable": bool(differing),
        "items_checked": list(COMPARABILITY_ITEMS),
        "differing_items": differing,
        "not_comparable_on": differing,
    }
    return differing, record


def _run_label(record):
    for key in ("run_id", "run_identifier", "run"):
        value = _base_get(record, key)
        if value is not None:
            return value
    return None


def _no_difference_report(fields, first, second, compared_form, points):
    return {
        "fields_compared": list(fields),
        "compared_form": compared_form,
        "form": compared_form,
        "points_compared": list(points),
        "comparison_points": list(points),
        "runs_compared": [_run_label(first), _run_label(second)],
        "hash_limb_ran": False,
        "wider_claim": False,
        "no_wider_claim": True,
        "report_kind": "observation",
    }


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
    state. A field missing on either side is a stated divergence
    named in missing_fields, never agreement. A field standing
    present with the value None stands as missing in the same
    form: no value stands stated on that side, and the headline
    unit stands under the same rule. Every field stands read
    through the base dict get, never through a get the record
    itself overrides. The comparison runs only where the two
    records agree on every comparability item of contracts C-02
    and C-03; a differing item records the pair as not comparable
    on that item and no equality observation stands reported from
    it. A differing comparison returns the consolidated first
    divergence record, and a comparison with no difference returns
    the consolidated no difference report, each in the form the
    resume check returns for its state limb."""
    fields = ac1_field_list()
    first_record = first if isinstance(first, dict) else {}
    second_record = second if isinstance(second, dict) else {}
    comp_differing, comp_record = _comparability(first_record, second_record)
    if comp_differing:
        return {
            "field_list": fields,
            "order": list(fields),
            "differing_fields": [],
            "missing_fields": [],
            "identical_headline_unit": None,
            "deterministic": None,
            "marked_non_deterministic": None,
            "hash_equality_claimed": False,
            "detection_state_completeness_claimed": False,
            "comparable": False,
            "not_comparable": True,
            "not_comparable_on": comp_differing,
            "comparability_differing_items": comp_differing,
            "comparability": comp_record,
            "comparability_record": comp_record,
            "equality_observation_reported": False,
            "comparison_reported": False,
            "first_divergence": None,
            "divergence_record": None,
            "no_difference_report": None,
        }
    missing = [
        field for field in fields
        if _base_get(first_record, field) is None
        or _base_get(second_record, field) is None
    ]
    differing = []
    for field in fields:
        if field in missing:
            differing.append(field)
        elif not _strict_eq(
                _base_get(first_record, field),
                _base_get(second_record, field)):
            differing.append(field)
    unit_differs = (
        _base_get(first_record, "headline_unit") is None
        or _base_get(second_record, "headline_unit") is None
        or not _strict_eq(
            _base_get(first_record, "headline_unit"),
            _base_get(second_record, "headline_unit"))
    )
    if unit_differs:
        differing.append("headline_unit")
    deterministic = not differing
    divergence_record = None
    no_difference_report = None
    if differing:
        first_diff = differing[0]
        divergence_record = {
            "field": first_diff,
            "tick": _base_get(second_record, "tick"),
            "day": _base_get(second_record, "simulated_day"),
            "agent_identifier": _base_get(second_record, "agent_identifier"),
            "values_compared": [
                _base_get(first_record, first_diff),
                _base_get(second_record, first_diff),
            ],
            "hash_limb_ran": False,
            "compared_form": "record level and verdict level values, no hash equality",
        }
    else:
        no_difference_report = _no_difference_report(
            fields, first_record, second_record,
            "record level and verdict level values, no hash equality",
            ["end of run"])
    return {
        "field_list": fields,
        "order": list(fields),
        "differing_fields": differing,
        "missing_fields": missing,
        "identical_headline_unit": not unit_differs,
        "deterministic": deterministic,
        "marked_non_deterministic": not deterministic,
        "hash_equality_claimed": False,
        "detection_state_completeness_claimed": False,
        "comparable": True,
        "not_comparable": False,
        "not_comparable_on": [],
        "comparability_differing_items": [],
        "comparability": comp_record,
        "comparability_record": comp_record,
        "equality_observation_reported": True,
        "first_divergence": differing[0] if differing else None,
        "divergence_record": divergence_record,
        "no_difference_report": no_difference_report,
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
    is explained, and records the first divergence. A field
    missing on either side is a divergence of that kind, named in
    missing_fields, and it promotes and bars in the same form. A
    field standing present with the value None stands as missing
    in the same form. A detection verdict standing absent at a
    comparison point on either side, or standing present with
    the value None, is a divergence of that point in the same
    form: a point on which no verdict stands on either side
    certifies no agreement. The comparison runs only where the
    two records agree on every comparability item of contracts
    C-02 and C-03; a differing item records the pair as not
    comparable on that item and no equality observation stands
    reported from it."""
    fields = ac1_field_list()
    original_record = original if isinstance(original, dict) else {}
    resumed_record = resumed if isinstance(resumed, dict) else {}
    comp_differing, comp_record = _comparability(original_record, resumed_record)
    verdict_points = detection_comparison_points()
    if comp_differing:
        return {
            "equal_in_scope": None,
            "scope": "non detection state, plus detection verdicts at two points only",
            "differing_fields": [],
            "missing_fields": [],
            "first_divergence": None,
            "divergence_record": None,
            "no_difference_report": None,
            "detection_comparison_points": verdict_points,
            "detection_scope": "verdict level only",
            "promoted_to_full_retention": False,
            "witness_use_barred": False,
            "comparable": False,
            "not_comparable": True,
            "not_comparable_on": comp_differing,
            "comparability_differing_items": comp_differing,
            "comparability": comp_record,
            "comparability_record": comp_record,
            "equality_observation_reported": False,
            "comparison_reported": False,
        }
    missing = [
        field for field in fields
        if _base_get(original_record, field) is None
        or _base_get(resumed_record, field) is None
    ]
    differing = []
    for field in fields:
        if field in missing:
            differing.append(field)
        elif not _strict_eq(
                _base_get(original_record, field),
                _base_get(resumed_record, field)):
            differing.append(field)
    verdict_differing = []
    original_verdicts = _base_get(original_record, "detection_verdicts")
    if not isinstance(original_verdicts, dict):
        original_verdicts = {}
    resumed_verdicts = _base_get(resumed_record, "detection_verdicts")
    if not isinstance(resumed_verdicts, dict):
        resumed_verdicts = {}
    for point in verdict_points:
        if (
            _base_get(original_verdicts, point) is None
            or _base_get(resumed_verdicts, point) is None
            or not _strict_eq(
                _base_get(original_verdicts, point),
                _base_get(resumed_verdicts, point))
        ):
            verdict_differing.append(point)
    failed = bool(differing or verdict_differing)
    first = (differing + verdict_differing)[0] if failed else None
    divergence_record = None
    if failed:
        divergence_record = {
            "field": first,
            "tick": _base_get(resumed_record, "tick"),
            "day": _base_get(resumed_record, "simulated_day"),
            "agent_identifier": _base_get(resumed_record, "agent_identifier"),
            "values_compared": [
                _base_get(original_record, first) if first in differing else _base_get(original_verdicts, first),
                _base_get(resumed_record, first) if first in differing else _base_get(resumed_verdicts, first),
            ],
            "hash_limb_ran": False,
            "compared_form": "record level and verdict level values, no hash equality",
        }
    no_difference_report = None
    if not failed:
        no_difference_report = _no_difference_report(
            fields, original_record, resumed_record,
            "record level and verdict level values, no hash equality",
            verdict_points)
    return {
        "equal_in_scope": not failed,
        "scope": "non detection state, plus detection verdicts at two points only",
        "differing_fields": differing,
        "missing_fields": missing,
        "first_divergence": first,
        "divergence_record": divergence_record,
        "no_difference_report": no_difference_report,
        "detection_comparison_points": verdict_points,
        "detection_scope": "verdict level only",
        "promoted_to_full_retention": failed,
        "witness_use_barred": failed,
        "comparable": True,
        "not_comparable": False,
        "not_comparable_on": [],
        "comparability_differing_items": [],
        "comparability": comp_record,
        "comparability_record": comp_record,
        "equality_observation_reported": True,
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
    if not claim_id:
        raise NamedReplicationFailure(
            "verdict record requires a claim identifier: no claim identifier stands supplied"
        )
    if standard not in STANDARDS:
        raise NamedReplicationFailure("unknown replication standard: " + str(standard))
    if outcome not in ("rests", "does not rest"):
        raise NamedReplicationFailure("unknown verdict outcome: " + str(outcome))
    record = {
        "claim_identifier": claim_id,
        "standard_applied": standard,
        "outcome": outcome,
        "quantities": None,
        "replication_statement": REPLICATION_STATEMENT,
        "replication_statement_sentences": list(REPLICATION_STATEMENT_SENTENCES),
    }
    if not validate_verdict_record(record):
        raise NamedReplicationFailure(
            "verdict record naming the distributional standard while the OP-20 quantities stand unfixed"
        )
    return record


def validate_verdict_record(record):
    """Return True only for a lawful verdict record. While the
    OP-20 quantities stand unfixed, no record naming the
    distributional equivalence standard stands. The sentence form
    of the replication statement must answer to the joined
    statement: a record whose sentence form stands empty or
    missing, or whose sentences contradict the joined statement,
    does not validate."""
    if not isinstance(record, dict):
        return False
    if not record.get("claim_identifier"):
        return False
    if record.get("outcome") not in ("rests", "does not rest"):
        return False
    if record.get("standard_applied") == "distributional equivalence":
        return False
    if dict.get(record, "replication_statement") != REPLICATION_STATEMENT:
        return False
    if not _replication_sentences_ok(record):
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
    if not _replication_sentences_ok(verdict):
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


PROFILE_BOUND_LABEL = "profile bound label attached (value set open at OP-16)"


def _is_detection_output(record):
    """Return True only for a checkable DetectionOutput form: a
    record carrying its run identifier, its scoring day range, and
    its verdict states and accumulator updates, in the combined
    Form 27 field or in the split fields MOD-08 builds."""
    if not isinstance(record, dict):
        return False
    if not record.get("run_identifier"):
        return False
    if "scoring_day_range" not in record:
        return False
    return (
        "verdict_states_and_accumulator_updates" in record
        or "verdict_states_by_agent_and_day" in record
    )


def score_detection_outputs(outputs, authored_by=None, knowledge=None,
                            records_position=None):
    """Score retained DetectionOutput records after a run, under
    the three separations. The record states who authored the
    profiles, what they could know, and where the records sit, as
    record properties supplied by the caller: this act supplies
    none of them itself, and it counts only records in a checkable
    DetectionOutput form. While OP-16 stands open, no score stands
    reported as a pass or a fail: the record carries its profile
    bound label in the stated carriage value, as the product own
    carriage, never as a value taken from an input."""
    if not isinstance(outputs, (list, tuple)):
        raise NamedReplicationFailure(
            "scoring requires a list of DetectionOutput records: the input stands in no list form"
        )
    supplied = {
        "authorship": authored_by,
        "knowledge": knowledge,
        "record separation": records_position,
    }
    missing = [name for name, value in supplied.items() if not value]
    if missing:
        raise NamedReplicationFailure(
            "scoring requires the three separations as record properties, supplied and not defaulted: missing "
            + ", ".join(missing)
        )
    for index, record in enumerate(outputs):
        if not _is_detection_output(record):
            raise NamedReplicationFailure(
                "scoring counts only checkable DetectionOutput records: input at position "
                + str(index) + " stands in no DetectionOutput form"
            )
    return {
        "outputs_scored": len(outputs),
        "separations": supplied,
        "inside_run_boundary": False,
        "value_returned_into_run": None,
        "score_reported_as": "neither pass nor fail, OP-16 open",
        "profile_bound_label": PROFILE_BOUND_LABEL,
    }


def validate_scoring_record(record):
    """Return True only for a scoring record standing outside the
    run boundary under all three separations, returning no value
    into the run, and carrying its profile bound label in the
    stated carriage value."""
    if not isinstance(record, dict):
        return False
    if record.get("inside_run_boundary"):
        return False
    if record.get("value_returned_into_run") is not None:
        return False
    if record.get("profile_bound_label") != PROFILE_BOUND_LABEL:
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
    if not isinstance(history, (list, tuple)) or not history:
        raise NamedReplicationFailure("a history extension extends an existing segment")
    if not isinstance(segment, dict):
        raise NamedReplicationFailure(
            "a history extension appends a segment record: the appended value stands in no record form"
        )
    segments = [_freeze(item) for item in history]
    first = segments[0]
    if not isinstance(first, dict) or not first.get("rule_set_version"):
        raise NamedReplicationFailure(
            "a history extension stands under the same rule set version as the segment it extends: no rule set version stands on that segment"
        )
    if not first.get("run_id"):
        raise NamedReplicationFailure(
            "a history extension links by run identifier: no run identifier stands on the segment it extends"
        )
    appended = _freeze(segment)
    stated_version = appended.get("rule_set_version")
    if stated_version is not None and stated_version != first.get("rule_set_version"):
        raise NamedReplicationFailure(
            "a history extension stands under the same rule set version as the segment it extends: the appended segment states another version"
        )
    stated_link = appended.get("linked_run")
    if stated_link is not None and stated_link != first.get("run_id"):
        raise NamedReplicationFailure(
            "a history extension links to the segment it extends: the appended segment states another linked run"
        )
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
    "REPLICATION_STATEMENT",
    "REPLICATION_STATEMENT_SENTENCES",
    "COMPARABILITY_ITEMS",
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
    "PROFILE_BOUND_LABEL",
    "scoring_harness_position",
    "score_detection_outputs",
    "validate_scoring_record",
    "witness_rerun",
    "validate_rerun_reading",
    "extend_history",
    "daily_aggregate_form",
    "validate_aggregate_form",
]

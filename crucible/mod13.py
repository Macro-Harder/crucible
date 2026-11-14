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
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, set):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = set()
        _memo[id(value)] = copied
        for item in set.__iter__(value):
            copied.add(_freeze(item, _memo))
        return copied
    return value


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


COMPARISON_DEPTH_BOUND = 100


def _base_str_eq(first, second):
    """Judge two values by base string equality, which no part
    can override. A value that does not stand in string form, or
    whose stored characters differ, does not agree."""
    if not (isinstance(first, str) and isinstance(second, str)):
        return False
    result = str.__eq__(first, second)
    return result if result is not NotImplemented else False


def _base_str_member(value, options):
    """Return True only where a value stands, by base string
    equality, among the stated options."""
    return any(_base_str_eq(value, option) for option in options)


def _base_set_items(value):
    """Read the stored elements of a set or frozenset part
    through base class iteration, never through an iteration
    the part itself supplies."""
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    return list(set.__iter__(value))


def _base_sentence_items(sentences):
    """Read the stored sentences of a handed list or tuple
    through base class iteration, never through an iteration
    the handed part itself supplies."""
    if isinstance(sentences, tuple):
        return list(tuple.__iter__(sentences))
    return list(list.__iter__(sentences))


def _strict_eq(first, second, _seen=None, _depth=0, _walked=None):
    """Judge two values by the values themselves, through base
    class comparisons that no part can override, at every nesting
    level. A part that overrides its own equality, for example a
    str subclass whose equality agrees with everything, is judged
    by the characters it stores, and the same rule runs inside
    plain lists, tuples, dicts, sets and frozensets nested at any
    depth the comparison acts read. The reading carries the
    stated depth bound of 100: a shape standing deeper than the
    bound stands refused in NamedReplicationFailure form, at
    this reading and at both public acts over it. The counting
    basis for the bound is containers only: the depth of a value
    counts the containers standing above it, and a scalar leaf
    standing at the end of a chain counts no depth of its own.
    On that basis a chain of 101 nested containers over a scalar
    leaf stands within the bound, and a chain of 102 stands past
    it and stands refused. A container pair that stands judged
    stands carried in a walked standing across every path that
    reaches it, keyed by the pair and by the depth at which it
    stands reached, so the work grows with the size of the
    values and a reach at a greater depth stands judged at its
    own depth against the bound."""
    if _depth > COMPARISON_DEPTH_BOUND:
        if isinstance(first, (dict, list, tuple, set, frozenset)) or isinstance(
                second, (dict, list, tuple, set, frozenset)):
            raise NamedReplicationFailure(
                "comparison depth bound reached: the value stands "
                "deeper than the stated bound of "
                + str(COMPARISON_DEPTH_BOUND)
            )
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
        if _walked is None:
            _walked = {}
        walked_key = (pair[0], pair[1], _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        _seen = _seen | {pair}
        first_items = list(dict.items(first))
        second_items = list(dict.items(second))
        if len(first_items) != len(second_items):
            _walked[walked_key] = False
            return False
        used = [False] * len(second_items)
        for first_key, first_value in first_items:
            matched = False
            for index in range(len(second_items)):
                if used[index]:
                    continue
                second_key, second_value = second_items[index]
                if _strict_eq(first_key, second_key, _seen, _depth + 1, _walked) and _strict_eq(
                        first_value, second_value, _seen, _depth + 1, _walked):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                _walked[walked_key] = False
                return False
        _walked[walked_key] = True
        return True
    if isinstance(first, list) or isinstance(second, list):
        if not (isinstance(first, list) and isinstance(second, list)):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        if _walked is None:
            _walked = {}
        walked_key = (pair[0], pair[1], _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        _seen = _seen | {pair}
        if list.__len__(first) != list.__len__(second):
            _walked[walked_key] = False
            return False
        for index in range(list.__len__(first)):
            if not _strict_eq(
                    list.__getitem__(first, index),
                    list.__getitem__(second, index), _seen, _depth + 1, _walked):
                _walked[walked_key] = False
                return False
        _walked[walked_key] = True
        return True
    if isinstance(first, tuple) or isinstance(second, tuple):
        if not (isinstance(first, tuple) and isinstance(second, tuple)):
            return False
        if _seen is None:
            _seen = set()
        pair = (id(first), id(second))
        if pair in _seen:
            return True
        if _walked is None:
            _walked = {}
        walked_key = (pair[0], pair[1], _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        _seen = _seen | {pair}
        if tuple.__len__(first) != tuple.__len__(second):
            _walked[walked_key] = False
            return False
        for index in range(tuple.__len__(first)):
            if not _strict_eq(
                    tuple.__getitem__(first, index),
                    tuple.__getitem__(second, index), _seen, _depth + 1, _walked):
                _walked[walked_key] = False
                return False
        _walked[walked_key] = True
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
        if _walked is None:
            _walked = {}
        walked_key = (pair[0], pair[1], _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        _seen = _seen | {pair}
        first_items = _base_set_items(first)
        second_items = _base_set_items(second)
        if len(first_items) != len(second_items):
            _walked[walked_key] = False
            return False
        used = [False] * len(second_items)
        for first_item in first_items:
            matched = False
            for index in range(len(second_items)):
                if used[index]:
                    continue
                if _strict_eq(first_item, second_items[index], _seen, _depth + 1, _walked):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                _walked[walked_key] = False
                return False
        _walked[walked_key] = True
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
        if isinstance(first, float):
            result = float.__eq__(first, second)
        else:
            result = float.__eq__(second, first)
        return result if result is not NotImplemented else False
    if isinstance(first, complex) or isinstance(second, complex):
        if not (isinstance(first, (int, float, complex))
                and isinstance(second, (int, float, complex))):
            return False
        if isinstance(first, complex):
            result = complex.__eq__(first, second)
        else:
            result = complex.__eq__(second, first)
        return result if result is not NotImplemented else False
    if isinstance(first, bytearray) or isinstance(second, bytearray):
        if not (isinstance(first, bytearray)
                and isinstance(second, bytearray)):
            return False
        result = bytearray.__eq__(first, second)
        return result if result is not NotImplemented else False
    if type(first) is not type(second):
        return False
    result = object.__eq__(first, second)
    return result if result is not NotImplemented else False


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
    stored_sentences = _base_sentence_items(sentences)
    if len(stored_sentences) == 0:
        return False
    if not _strict_eq(
            stored_sentences, list(REPLICATION_STATEMENT_SENTENCES)):
        return False
    joined = dict.get(record, "replication_statement")
    if not isinstance(joined, str):
        return False
    constructed = " ".join(stored_sentences)
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
    claim_identifier = dict.get(record, "claim_identifier")
    if isinstance(claim_identifier, str):
        if str.__len__(claim_identifier) == 0:
            return False
    elif not claim_identifier:
        return False
    if not _base_str_member(
            dict.get(record, "outcome"), ("rests", "does not rest")):
        return False
    if _base_str_eq(
            dict.get(record, "standard_applied"),
            "distributional equivalence"):
        return False
    if not _base_str_eq(
            dict.get(record, "replication_statement"),
            REPLICATION_STATEMENT):
        return False
    if not _replication_sentences_ok(record):
        return False
    return _base_str_eq(
        dict.get(record, "standard_applied"), "exact replay alone")


def publishable_on_replication(claim, verdict):
    """Return True only where the Reporter may publish a claim as
    resting on replication: a verdict record for that claim must
    stand, with the outcome rests."""
    if not isinstance(verdict, dict):
        return False
    verdict_claim = dict.get(verdict, "claim_identifier")
    handed_claim = (
        _base_get(claim, "claim_identifier")
        if isinstance(claim, dict) else None
    )
    if isinstance(verdict_claim, str) or isinstance(handed_claim, str):
        if not _base_str_eq(verdict_claim, handed_claim):
            return False
    elif not _strict_eq(verdict_claim, handed_claim):
        return False
    if not _replication_sentences_ok(verdict):
        return False
    if not validate_verdict_record(verdict):
        return False
    return _base_str_eq(dict.get(verdict, "outcome"), "rests")


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


_HISTORY_CONTAINER_TYPES = (dict, list, tuple, set, frozenset)


def _history_base_children(value):
    if isinstance(value, dict):
        return list(dict.keys(value)) + list(dict.values(value))
    if isinstance(value, list):
        return list(list.__iter__(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    return list(set.__iter__(value))


def _bound_grounds(value):
    """Return the pair (past the bound, carries a cycle) for a
    value, each ground judged on its own, on the containers only
    basis the comparison reading states: a chain of 101 nested
    containers over a scalar leaf stands within the bound, and a
    chain of 102 stands past it. Every container stands read
    through base class operations only, and the walk runs on
    explicit stacks over the graph of distinct containers,
    reading the longest container path from the root, so a
    hostile shape stands reported in this form and never as a
    bare RecursionError, and a container shared by two siblings
    costs one walk, not one per path. A cycle edge closes no
    height: the height of a node counts only the child paths
    that end, so a shallow cycle reads as a cycle and not as
    depth."""
    if not isinstance(value, _HISTORY_CONTAINER_TYPES):
        return (False, False)
    children_by_id = {}
    pending = [value]
    while pending:
        current = pending.pop()
        if id(current) in children_by_id:
            continue
        child_containers = [
            child for child in _history_base_children(current)
            if isinstance(child, _HISTORY_CONTAINER_TYPES)]
        children_by_id[id(current)] = [
            id(child) for child in child_containers]
        for child in child_containers:
            if id(child) not in children_by_id:
                pending.append(child)
    root_id = id(value)
    heights = {}
    cyclic = False
    on_path = {root_id}
    stack = [(root_id, iter(children_by_id[root_id]))]
    while stack:
        node_id, child_iter = stack[-1]
        advanced = False
        for child_id in child_iter:
            if child_id in on_path:
                cyclic = True
                continue
            if child_id in heights:
                continue
            on_path.add(child_id)
            stack.append((child_id, iter(children_by_id[child_id])))
            advanced = True
            break
        if not advanced:
            stack.pop()
            on_path.discard(node_id)
            ended = [
                heights[child_id] for child_id in children_by_id[node_id]
                if child_id in heights]
            heights[node_id] = 1 + max(ended) if ended else 0
    return (heights[root_id] > COMPARISON_DEPTH_BOUND, cyclic)


def _shape_exceeds_bound(value):
    """True where a value stands deeper than the stated bound
    of COMPARISON_DEPTH_BOUND or carries a cycle on one of its
    paths, as _bound_grounds judges the two grounds apart."""
    past, cyclic = _bound_grounds(value)
    return past or cyclic


def _history_base_items(history):
    """Read the stored items of a handed history through the
    base class iteration of its form, never through an
    iteration the handed history itself supplies, so what the
    bound guard walks is what the copy limb copies."""
    if isinstance(history, tuple):
        return list(tuple.__iter__(history))
    return list(list.__iter__(history))


def extend_history(history, segment):
    """Extend a history past its first horizon: the extension
    appends a new linked segment, linked by run identifier and
    segment order, under the same rule set version as the segment
    it extends, rewriting no part of the segment it extends. The
    seed derivation limb of an extension stands gated on DQ7-02
    wherever it would consume derived seeds, and stands in no
    part of this act. The handed history and the appended
    segment stand under the stated bound of
    COMPARISON_DEPTH_BOUND before any copy stands made: a shape
    past the bound or carrying a cycle stands refused in
    NamedReplicationFailure form, never as a bare
    RecursionError, and the refusal states the true ground for
    each input, past the bound or a cycle, and names the input
    that carries it. The copy of the handed history reads the
    history through the same base class reading the guard
    walks, so what is guarded is what is copied."""
    if not isinstance(history, (list, tuple)) or not history:
        raise NamedReplicationFailure("a history extension extends an existing segment")
    if not isinstance(segment, dict):
        raise NamedReplicationFailure(
            "a history extension appends a segment record: the appended value stands in no record form"
        )
    grounds = []
    for label, handed in (
            ("the handed history", history),
            ("the appended segment", segment)):
        past, cyclic = _bound_grounds(handed)
        if past:
            grounds.append(
                label + " stands past the bound of "
                + str(COMPARISON_DEPTH_BOUND))
        if cyclic:
            grounds.append(label + " carries a cycle")
    if grounds:
        raise NamedReplicationFailure(
            "a history extension stands refused: " + "; ".join(grounds))
    segments = [_freeze(item) for item in _history_base_items(history)]
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


def _base_container_items(value):
    """Read the stored items of a handed container through its
    base class iteration, never through an iteration the handed
    part itself supplies."""
    if isinstance(value, dict):
        return list(dict.values(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    if isinstance(value, set):
        return list(set.__iter__(value))
    return list(list.__iter__(value))


def _run_log_records(run_log):
    """Read a handed run log as its run records. The run log of
    the registry comparison is the set of RunRecords retained
    for the family, so a part that stands in no record form
    stands as no run log entry. A mapping carrying its records
    under a runs, run records, or records field reads through
    that field, and a single record handed whole reads as a
    one record log."""
    if run_log is None:
        return None
    if isinstance(run_log, dict):
        if _base_get(run_log, "run_identifier") is not None or (
                _base_get(run_log, "run_id") is not None
                and _base_get(run_log, "run_class") is not None):
            return [run_log]
        for key in ("runs", "run_records", "records", "run_log"):
            inner = dict.get(run_log, key)
            if inner is not None:
                return _run_log_records(inner) or []
        return []
    if isinstance(run_log, (list, tuple, set, frozenset)):
        return [
            item for item in _base_container_items(run_log)
            if isinstance(item, dict)]
    return []


def _first_base_value(record, fields):
    for field in fields:
        value = _base_get(record, field)
        if value is not None:
            return value
    return None


def _record_is_pilot(record):
    """True where a record stands as a pilot artefact. Pilot
    artefacts are stored apart from sweep results and a pilot
    record is never a run log entry for this check."""
    for field in ("run_class", "store_kind", "kind", "record_kind"):
        if _base_str_eq(_base_get(record, field), "pilot"):
            return True
    return False


def _record_bears_on_entry(record, entry):
    """True where a run record bears on the claim an entry
    carries. A record of another family, or of another claim,
    where both sides state the identifier, bears on no claim of
    this entry. A failed run bears as any other run bears: its
    status stands read as failed and it stands in the log."""
    family = _first_base_value(
        record, ("sweep_family_identifier", "family_identifier",
                 "family_id"))
    entry_family = _first_base_value(
        entry, ("sweep_family_identifier", "family_identifier",
                "family_id"))
    if family is not None and entry_family is not None and not (
            _base_str_eq(family, entry_family)):
        return False
    claim = _first_base_value(record, ("claim_identifier", "claim_id"))
    entry_claim = _first_base_value(
        entry, ("claim_identifier", "claim_id"))
    if claim is not None and entry_claim is not None and not (
            _base_str_eq(claim, entry_claim)):
        return False
    return True


def _entry_run_identifiers(entry):
    """The run identifiers a registry entry carries, read
    through base class readings from its screening and held out
    confirmation identifier fields."""
    identifiers = []
    for field in ("screening_run_identifiers",
                  "held_out_confirmation_run_identifiers",
                  "confirmation_run_identifiers",
                  "run_identifiers"):
        value = _base_get(entry, field)
        if isinstance(value, (list, tuple, set, frozenset)):
            identifiers.extend(_base_container_items(value))
        elif isinstance(value, str):
            identifiers.append(value)
    return identifiers


def compare_registry_against_run_log(entry, run_log=None,
                                     retained_records=None):
    """Compare one SweepFamilyRegistry entry against the run
    log, in the form the brief at section 2.4 and the plan at
    Form 22 item 4 and section 6.1 item 13 state. The act stands
    in this module, the Replication Checker, which did not
    compile the registry: the compiling module is MOD-11, and no
    part of this act reads a MOD-11 surface. The comparison
    stands before any headline claim is reported.

    The run log the comparison reads is the set of RunRecords
    retained by MOD-10 for the family, handed in as the run log
    argument or as the retained records argument, or carried on
    the entry itself under a run log field. Its membership is:
    every run of the family whose RunRecord stands retained, of
    every run class, screening, confirmation, headline, and
    validation; failed runs stand in it, by their RunRecords
    with the status field read as failed; pilot runs do not
    stand in it. Every bearing run must appear in the claim
    entry, among its screening run identifiers or its held out
    confirmation run identifiers, read by base string equality.

    The result states whether a comparison was performed, and
    whether it passed. With no run log among the inputs, no
    comparison stands performed and none stands passed. Where
    an expected run count stands stated, on the entry or as
    the expected count field of the run log mapping, a shortfall
    of retained records against that count fails the comparison
    under the name EXPECTED-RUN-SHORTFALL, as Form 22 item 5
    states."""
    if not isinstance(entry, dict):
        return {
            "performed": False,
            "passed": False,
            "checker_module": "MOD-13",
            "compared_against_run_log": False,
            "bearing_run_identifiers": [],
            "missing_run_identifiers": [],
            "excluded_pilot_run_identifiers": [],
            "entry_run_identifiers": [],
        }
    source = retained_records if retained_records is not None else run_log
    if source is None:
        source = _base_get(entry, "run_log")
    records = _run_log_records(source)
    if records is None:
        return {
            "performed": False,
            "passed": False,
            "checker_module": "MOD-13",
            "compared_against_run_log": False,
            "bearing_run_identifiers": [],
            "missing_run_identifiers": [],
            "excluded_pilot_run_identifiers": [],
            "entry_run_identifiers": _entry_run_identifiers(entry),
        }
    entry_ids = _entry_run_identifiers(entry)
    bearing = []
    excluded_pilot = []
    for record in records:
        run_id = _first_base_value(record, ("run_identifier", "run_id"))
        if _record_is_pilot(record):
            excluded_pilot.append(run_id)
            continue
        if not _record_bears_on_entry(record, entry):
            continue
        bearing.append(run_id)
    missing = [
        run_id for run_id in bearing
        if run_id is None or not any(
            _base_str_eq(run_id, entry_id) for entry_id in entry_ids)]
    result = {
        "performed": True,
        "passed": not missing,
        "checker_module": "MOD-13",
        "compared_against_run_log": True,
        "bearing_run_identifiers": bearing,
        "missing_run_identifiers": missing,
        "excluded_pilot_run_identifiers": excluded_pilot,
        "entry_run_identifiers": entry_ids,
    }
    expected = _first_base_value(
        entry, ("expected_run_count", "expected_runs"))
    if expected is None and isinstance(source, dict):
        expected = _first_base_value(
            source, ("expected_run_count", "expected_runs"))
    if isinstance(expected, int) and not isinstance(expected, bool):
        retained_count = len(records) - len(excluded_pilot)
        result["expected_run_count"] = expected
        result["retained_run_count"] = retained_count
        if retained_count < expected:
            result["passed"] = False
            result["shortfall_name"] = "EXPECTED-RUN-SHORTFALL"
            result["shortfall"] = expected - retained_count
    return result


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
    "compare_registry_against_run_log",
    "daily_aggregate_form",
    "validate_aggregate_form",
]

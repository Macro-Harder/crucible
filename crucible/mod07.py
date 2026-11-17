"""MOD-07 Escrow Adapter and seam records.

Slice S-06. The only module permitted to depend on both cores, and
that dependence stands at decision record level while register
question NQ-45 stands open: this module records every meeting point
between the cores as an adapter choice at decision record level,
and calls neither core. It builds no seam treatment that a folding
against the ruling text has not covered.

While NQ-45 stands open, every cross seam lien, release, and slash
effect in a joint run carries computed not settled, joint effects
stand reported as computed in Parley and not settled in the chosen
escrow, and a record carrying settled or released for such an
effect fails validation at MOD-01, whose lien state bar this module
applies and does not restate.
"""
import copy
import unicodedata
from decimal import Decimal
from fractions import Fraction

from crucible import mod01

OPEN_SEMANTIC_ITEMS = tuple("OS-%d" % n for n in range(1, 15))

SEAM_GAP_COUNTS = {"creation": 7, "release": 6, "slash execution": 8}

TRACER_RESULTS = ("passed as a record", "blocked", "not attempted")

POSITIVE_CONTROL_PATH = "escrow request lien path"

COMPUTED_NOT_SETTLED = "computed not settled"

INTERIM_REPORTING = "computed in Parley and not settled in the chosen escrow"

RULING_TEXT_GAPS = tuple("G-%d" % n for n in range(1, 11))

C12_STANDINGS = (
    "the chosen escrow core has a cost pool account",
    "the chosen escrow core has no cost pool account",
)

_DEPENDENCY_EDGES = (
    ("MOD-05", "MOD-07"),
    ("MOD-06", "MOD-07"),
    ("MOD-07", "MOD-01"),
)

_LOG_FIELDS = mod01.form_fields("18")
_TRACER_FIELDS = mod01.form_fields("29")

COPY_DEPTH_BOUND = 100


def _guard_path_part(value):
    """One part of a copy guard path, read through the base
    form of the value kind, never through a string reading
    the value itself supplies. A value whose form stands in
    no base readable kind stands in the path as an unreadable
    part, so building the path itself raises no bare error
    and states no reported text."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bool):
        return bool.__str__(value)
    if isinstance(value, int):
        return int.__str__(value)
    if isinstance(value, float):
        return float.__str__(value)
    if isinstance(value, bytes):
        return bytes.__repr__(value)
    return "unreadable part"


def _copy_guard(value, _depth=0, _seen=None, _path="root",
                _walked=None):
    """Walk a value the choice and seam copy surfaces are about
    to copy, under the stated depth bound of 100 and a cycle
    guard: a value standing deeper than the bound, or carrying a
    cycle, stands refused in named form, and no bare
    RecursionError escapes the copy. A value shared from two
    places on different paths carries no cycle and stands
    admitted. The walk carries a walked standing across paths:
    a container whose walk stands completed at a stated depth
    stands not walked again where another path reaches it at
    that same depth, so a container shared by two siblings
    stands walked once for each depth it stands at, and a reach
    at a greater depth stands walked again and judged at its
    own depth against the depth bound."""
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > COPY_DEPTH_BOUND:
            raise ValueError(
                "adapter copy stands refused in named form: a "
                "value stands deeper than the stated bound of "
                + str(COPY_DEPTH_BOUND) + " at " + _path
                + ", counted with every container standing around a "
                "part counting toward that bound, and no copy stands "
                "made")
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise ValueError(
                "adapter copy stands refused in named form: a "
                "value carries a cycle at " + _path
                + ", and no copy stands made")
        walked = _walked if _walked is not None else {}
        if (id(value), _depth) in walked:
            return
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    _copy_guard(
                        key, _depth + 1, seen,
                        _path + "/key:" + _guard_path_part(key),
                        walked)
                    _copy_guard(
                        item, _depth + 1, seen,
                        _path + "/" + _guard_path_part(key), walked)
            else:
                for index, item in enumerate(value):
                    _copy_guard(
                        item, _depth + 1, seen,
                        _path + "[" + int.__str__(index) + "]",
                        walked)
        finally:
            seen.discard(id(value))
        walked[(id(value), _depth)] = True


def _bget(mapping, key, default=None):
    """The value a handed mapping stores under a key, read
    through the base dict get, never through a get reading the
    mapping itself supplies."""
    if isinstance(mapping, dict):
        for stored_key, item in dict.items(mapping):
            if isinstance(stored_key, str) and str.__eq__(
                    str.__str__(stored_key), key):
                return item
    return default


def _stored_copy(value, _memo=None):
    """A copy of a handed value built from its stored contents
    only: dict parts through the base dict items reading, list,
    tuple, set, and frozenset parts through their base iteration
    readings, and text parts through the base string form, so
    no reading a part itself supplies directs the copy. The
    buffer forms stand carried as stored: a bytearray as a fresh
    bytearray and a memoryview as a memoryview over fresh bytes. A dict assignment whose key hash or equality reading
    raises at the assignment itself stands carried under a
    distinct numbered form, a plain text numbered form where
    a form carrying the key itself cannot stand inserted, in
    the MOD-14 cured form, so no carried entry is silently
    dropped on that reading and no bare error escapes the copy. A text key whose plain stored text already stands in the copy from a distinct handed key stands carried under the same distinct numbered form, so two distinct keys storing the one text stand as two entries in the copy."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied_key = _stored_copy(key, _memo)
            copied_item = _stored_copy(item, _memo)
            key_taken = False
            if isinstance(copied_key, str):
                try:
                    key_taken = copied_key in copied
                except Exception:
                    key_taken = False
            if not key_taken:
                try:
                    copied[copied_key] = copied_item
                    continue
                except Exception:
                    pass
            counter = 2
            while True:
                if isinstance(copied_key, str):
                    candidate = (
                        str.__str__(copied_key)
                        + " (carried key " + str(counter) + ")")
                elif counter == 2:
                    candidate = (copied_key, counter)
                else:
                    candidate = (
                        "(carried key " + str(counter) + ")")
                try:
                    candidate_taken = candidate in copied
                except Exception:
                    candidate_taken = False
                if candidate_taken:
                    counter += 1
                    continue
                try:
                    copied[candidate] = copied_item
                    break
                except Exception:
                    counter += 1
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _stored_copy(item, _memo)
            for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _stored_copy(item, _memo)
            for item in tuple.__iter__(value))
        _memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        parts = [
            _stored_copy(item, _memo) for item in (
                set.__iter__(value) if isinstance(value, set)
                else frozenset.__iter__(value))]
        try:
            return set(parts) if isinstance(value, set) else frozenset(
                parts)
        except Exception:
            return parts
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, bytearray):
        return bytearray(value)
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    return value


def _base_sequence(value):
    """The stored parts of a handed sequence, read through the
    base iteration of its form, as a list. A value in no
    sequence form stands as no parts."""
    if isinstance(value, list):
        return list(list.__iter__(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    if isinstance(value, set):
        return list(set.__iter__(value))
    return []


def _value_present(value):
    """Whether a handed value stands present, judged by the
    contents it stores, read through base class operations of
    its kind, never through a truth reading it supplies."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, (list, tuple, set, frozenset, dict,
                          bytes, bytearray, memoryview)):
        if isinstance(value, list):
            return list.__len__(value) > 0
        if isinstance(value, tuple):
            return tuple.__len__(value) > 0
        if isinstance(value, dict):
            return dict.__len__(value) > 0
        if isinstance(value, (bytes, bytearray)):
            return bytes.__len__(bytes(value)) > 0
        if isinstance(value, memoryview):
            return bytes.__len__(bytes(value)) > 0
        if isinstance(value, frozenset):
            return frozenset.__len__(value) > 0
        return set.__len__(value) > 0
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    return False


def _stored_text_eq(value, stated):
    """Whether a handed value stores the stated text, judged on
    its stored text form."""
    return isinstance(value, str) and str.__eq__(
        str.__str__(value), stated) is True


def _stored_pair_equal(first, second, _depth=0, _seen=None):
    """Whether two handed values store the same value, judged on
    their stored forms only, never through an equality reading
    either value itself supplies: text values by their stored
    characters, bytes form values by their stored bytes, numbers
    and booleans by the base class operations of their kind,
    containers part by part on their stored parts, and any other
    value by identity alone. A container pair standing on the
    current path, or a walk past the stated depth bound of the
    module copy guard, stands apart, so a part carrying a cycle
    answers a verdict and no bare RecursionError escapes the
    reading, in the form of the cycle guard at the stored edge
    text reading of this same module."""
    if first is second:
        return True
    if _depth > COPY_DEPTH_BOUND:
        return False
    if isinstance(first, str) or isinstance(second, str):
        return isinstance(first, str) and isinstance(second, str) \
            and str.__eq__(
                str.__str__(first), str.__str__(second)) is True
    if isinstance(first, (bytes, bytearray, memoryview)) \
            or isinstance(second, (bytes, bytearray, memoryview)):
        return isinstance(first, (bytes, bytearray, memoryview)) \
            and isinstance(second, (bytes, bytearray, memoryview)) \
            and bytes.__eq__(bytes(first), bytes(second)) is True
    if first is None or second is None:
        return first is None and second is None
    if isinstance(first, bool) or isinstance(second, bool):
        return isinstance(first, bool) and isinstance(second, bool) \
            and first is second
    if isinstance(first, int) and isinstance(second, int):
        return int.__eq__(first, second) is True
    if isinstance(first, float) and isinstance(second, float):
        return float.__eq__(first, second) is True
    if isinstance(first, Decimal) or isinstance(second, Decimal):
        return isinstance(first, Decimal) and isinstance(second, Decimal) \
            and Decimal.__eq__(
                Decimal.__new__(Decimal, first),
                Decimal.__new__(Decimal, second)) is True
    if isinstance(first, Fraction) or isinstance(second, Fraction):
        return isinstance(first, Fraction) and isinstance(second, Fraction) \
            and Fraction.__eq__(
                Fraction.__new__(Fraction, first),
                Fraction.__new__(Fraction, second)) is True
    if isinstance(first, complex) or isinstance(second, complex):
        return isinstance(first, complex) and isinstance(second, complex) \
            and complex.__eq__(
                complex.__new__(complex, first),
                complex.__new__(complex, second)) is True
    if isinstance(first, dict) and isinstance(second, dict):
        pair = (id(first), id(second))
        if _seen is not None and pair in _seen:
            return False
        _seen = (_seen or frozenset()) | {pair}
        if dict.__len__(first) != dict.__len__(second):
            return False
        second_items = list(dict.items(second))
        for key, item in dict.items(first):
            matched = None
            for index, (other_key, other_item) in enumerate(second_items):
                if _stored_pair_equal(key, other_key, _depth + 1, _seen):
                    matched = index
                    matched_item = other_item
                    break
            if matched is None:
                return False
            if not _stored_pair_equal(item, matched_item, _depth + 1, _seen):
                return False
            second_items.pop(matched)
        return True
    if isinstance(first, (list, tuple)) \
            and isinstance(second, (list, tuple)):
        pair = (id(first), id(second))
        if _seen is not None and pair in _seen:
            return False
        _seen = (_seen or frozenset()) | {pair}
        if type(first) is not type(second):
            return False
        first_parts = _base_sequence(first)
        second_parts = _base_sequence(second)
        if len(first_parts) != len(second_parts):
            return False
        return all(
            _stored_pair_equal(one, two, _depth + 1, _seen)
            for one, two in zip(first_parts, second_parts))
    if isinstance(first, (set, frozenset)) \
            and isinstance(second, (set, frozenset)):
        pair = (id(first), id(second))
        if _seen is not None and pair in _seen:
            return False
        _seen = (_seen or frozenset()) | {pair}
        first_parts = _base_sequence(first)
        second_parts = _base_sequence(second)
        if len(first_parts) != len(second_parts):
            return False
        remaining = list(second_parts)
        for part in first_parts:
            matched = None
            for index, other in enumerate(remaining):
                if _stored_pair_equal(part, other, _depth + 1, _seen):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
        return True
    return first is second


def seam_gap_counts():
    """Return the seam gap counts R10 records: creation 7, release
    6, slash execution 8, standing over the fourteen open semantic
    items as the standing reason for the interim reporting rule."""
    return dict(SEAM_GAP_COUNTS)


def dependency_record():
    """Return the module dependency record for the seam: MOD-07
    alone depends on both cores, at decision record level while
    NQ-45 stands open, and no direct edge stands between the two
    core modules in either direction."""
    return {
        "edges": [tuple(edge) for edge in _DEPENDENCY_EDGES],
        "joint_dependent": "MOD-07",
        "depends_on_both_cores": ["MOD-05", "MOD-06"],
        "form": "decision record level while NQ-45 stands open",
        "direct_core_to_core_edges": [],
    }


def _dict_carriage_edges(edges):
    """The edges a dict carriage carries, read through the base
    dict items reading: a pair standing under the source and
    target names stands as one edge, an edge standing as a key
    stands as that edge, a target set standing under one source
    stands as one edge per target, and every other stored pair
    stands as one edge from its key to its value, so a dict
    carriage stands judged on the edges it stores and never
    read as no edges."""
    items = list(dict.items(edges))
    key_texts = [_stored_text(key) for key, _item in items]
    if "source" in key_texts and "target" in key_texts:
        return [(_bget(edges, "source"), _bget(edges, "target"))]
    carried = []
    for key, item in items:
        if isinstance(item, dict):
            item_texts = [_stored_text(part) for part in dict.keys(item)]
            if "source" in item_texts and "target" in item_texts:
                carried.append(
                    (_bget(item, "source"), _bget(item, "target")))
                continue
        if isinstance(key, (list, tuple, set, frozenset)):
            carried.append(key)
        elif isinstance(item, (list, tuple, set, frozenset)) \
                and not isinstance(
                    item, (str, bytes, bytearray, memoryview)):
            for target in _base_sequence(item):
                carried.append((key, target))
        else:
            carried.append((key, item))
    return carried


def validate_dependency_record(record):
    """Return True only where the record carries no direct core to
    core edge and MOD-07 stands as the sole joint dependent."""
    if not isinstance(record, dict):
        return False
    raw_edges = _bget(record, "edges")
    if isinstance(raw_edges, dict):
        edge_values = _dict_carriage_edges(raw_edges)
    else:
        edge_values = _base_sequence(raw_edges)
    edges = []
    try:
        for edge in edge_values:
            if not isinstance(edge, (list, tuple)):
                return False
            parts = _base_sequence(edge)
            if len(parts) != 2:
                return False
            edges.append(
                tuple(_stored_edge_text(part) for part in parts))
        joint_text = _stored_edge_text(
            _bget(record, "joint_dependent"))
    except ValueError:
        return False
    for source, target in edges:
        if {source, target} == {"MOD-05", "MOD-06"}:
            return False
    joint = [
        module for module in ("MOD-05", "MOD-06", "MOD-07", "MOD-08")
        if ("MOD-05", module) in edges and ("MOD-06", module) in edges
    ]
    if not _stored_text_eq(joint_text, "MOD-07"):
        return False
    return joint in ([], ["MOD-07"])


def make_adapter_choice(choice_identifier, reading_applied,
                        parameter_or_rule_point_affected,
                        governing_text_version,
                        escrow_variant_and_fold_version,
                        parley_test_total_source=None,
                        dependence_marks=None, approval=None,
                        drives=None, ruling_references=None):
    """Build one adapter choice as a record. A choice stands
    recorded as an adapter choice, never as a rule of either
    system. The approval stands as its own part of the record: the
    choice, its effects, and its approver, named before a run may
    use the choice. The drives list names only decision level
    computed values."""
    for part in (approval, dependence_marks, drives,
                 ruling_references):
        if part is not None:
            _copy_guard(part)
    return {
        "choice_identifier": choice_identifier,
        "reading_applied": reading_applied,
        "parameter_or_rule_point_affected": parameter_or_rule_point_affected,
        "governing_text_version": governing_text_version,
        "escrow_variant_and_fold_version": escrow_variant_and_fold_version,
        "parley_test_total_source": parley_test_total_source,
        "dependence_marks": _stored_copy(dependence_marks or []),
        "recorded_as": "adapter choice",
        "presented_as_rule_of": None,
        "approval": _stored_copy(approval),
        "drives": _stored_copy(drives or []),
        "ruling_references": _stored_copy(ruling_references or []),
        "seam_status": COMPUTED_NOT_SETTLED,
    }


def interpretation_log_entry(choice):
    """Return the InterpretationLogEntry of a choice, in the Form
    18 field order MOD-01 states, carrying the adapter choice mark
    beside the form fields."""
    _copy_guard(choice)
    entry = {}
    for field in _LOG_FIELDS:
        entry[field] = _stored_copy(_bget(choice, field))
    entry["recorded_as"] = "adapter choice"
    return entry


def run_record_entry(choice):
    """Return the run record entry of a choice: the same choice, in
    the same fields, as the interpretation choices group of the run
    record carries it."""
    _copy_guard(choice)
    entry = {}
    for field in _LOG_FIELDS:
        entry[field] = _stored_copy(_bget(choice, field))
    entry["recorded_as"] = "adapter choice"
    entry["approval"] = _stored_copy(_bget(choice, "approval"))
    return entry


def validate_choice_pair(log_entry, run_entry):
    """The pair audit of operation C-12: the log entry and the run
    record entry of one choice agree on the choice identifier, the
    reading applied, the governing text version, and every
    dependence mark. A disagreeing pair fails, and a failed result
    is not reportable until the pair agrees."""
    if not isinstance(log_entry, dict) or not isinstance(run_entry, dict):
        return False
    for field in (
        "choice_identifier",
        "reading_applied",
        "governing_text_version",
        "dependence_marks",
    ):
        for entry in (log_entry, run_entry):
            if not dict.__contains__(entry, field) \
                    or dict.get(entry, field) is None:
                return False
            if field != "dependence_marks" \
                    and _stored_text_eq(dict.get(entry, field), ""):
                return False
        if field == "dependence_marks":
            if not _stored_pair_equal(
                    dict.get(log_entry, field),
                    dict.get(run_entry, field)):
                return False
        elif not _stored_pair_equal(
                dict.get(log_entry, field),
                dict.get(run_entry, field)):
            return False
    return True


def append_reading(log, choice):
    """Append a later reading for a rule point as a new entry. No
    earlier entry stands edited in place."""
    _copy_guard(log)
    if isinstance(log, (list, tuple)):
        entries = _base_sequence(log)
    else:
        try:
            entries = list(log)
        except Exception:
            raise ValueError(
                "append_reading stands refused: the log stands in "
                "no list form, a log stands as a list of records, "
                "and no reading stands appended") from None
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "append_reading stands refused: a log entry stands "
                "in no record form, a log entry stands as a record, "
                "and no reading stands appended")
    updated = [_stored_copy(entry) for entry in entries]
    updated.append(interpretation_log_entry(choice))
    return updated


def reading_for_result(log, choice_identifier):
    """Return the entry a result carries, named by its choice
    identifier, and never the latest entry in the log for its rule
    point."""
    entries = _base_sequence(log) if isinstance(
        log, (list, tuple, set, frozenset)) else log
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if _stored_pair_equal(
                _stored_copy(_bget(entry, "choice_identifier")),
                _stored_copy(choice_identifier)):
            _copy_guard(entry)
            return _stored_copy(entry)
    return None


def choice_approval_stands(choice):
    """Return True only where the Project Manager approval stands
    on the record of the choice, naming the choice, its effects,
    and its approver."""
    if not isinstance(choice, dict):
        return False
    approval = dict.get(choice, "approval")
    if not isinstance(approval, dict):
        return False
    if not _stored_text_eq(
            dict.get(approval, "approver"), "Project Manager"):
        return False
    if not _stored_pair_equal(
            dict.get(approval, "choice_identifier"),
            dict.get(choice, "choice_identifier")):
        return False
    if not _value_present(dict.get(approval, "effects")):
        return False
    return _stored_text_eq(dict.get(approval, "standing"), "approved")


def validate_adapter_choice(choice):
    """Return True only for a choice that may stand on a run: it
    stands recorded as an adapter choice and not as a rule of
    either system, it drives decision level computed values only,
    and its approval stands on the record."""
    if not isinstance(choice, dict):
        return False
    if not _stored_text_eq(
            dict.get(choice, "recorded_as"), "adapter choice"):
        return False
    if dict.get(choice, "presented_as_rule_of") is not None:
        return False
    drives = dict.get(choice, "drives")
    if drives is not None and not isinstance(
            drives, (list, tuple, set, frozenset)):
        return False
    for driven in _base_sequence(drives):
        if not isinstance(driven, dict):
            return False
        if not _stored_text_eq(dict.get(driven, "level"), "decision"):
            return False
        if not _stored_text_eq(
                dict.get(driven, "kind"), "computed value"):
            return False
    return choice_approval_stands(choice)


def seam_status():
    """Return the seam status field in its present form, stated
    plainly, in pay now form only. Dual reporting, restatement,
    and any pooled before and after claim stand as a named bound
    and stand outside this field."""
    return {
        "seam_status": COMPUTED_NOT_SETTLED,
        "stated_plainly": True,
        "bound": "dual reporting, restatement, and pooled claims stand unbuilt",
    }


def _safe_repr(value):
    """Render a handed value for a refusal sentence: through
    its repr reading where that reading stands, and through
    the base object repr where the repr reading the value
    itself supplies raises, so the sentence stands delivered
    whole and never escapes bare on that reading."""
    try:
        return repr(value)
    except Exception:
        return object.__repr__(value)


def _safe_str(value):
    """Render a handed value for a refusal sentence: through
    its string reading where that reading stands, and through
    the base object repr where the string reading the value
    itself supplies raises, so the sentence stands delivered
    whole and never escapes bare on that reading."""
    try:
        return str(value)
    except Exception:
        return object.__repr__(value)


def _sentence_text(value):
    """Render a handed value for a sentence or a delivered record
    field on the text it stores: a text or buffer form through
    _stored_text, never through a reading the value itself
    supplies, and a value in any other form through _safe_str
    as before."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    return _safe_str(value)


def make_tracer_passage_record(item, point_in_run, what_in_fact_passed,
                               result):
    """Build one TracerPassageRecord in the Form 29 field order
    MOD-01 states."""
    if not any(_stored_text_eq(result, stated)
               for stated in TRACER_RESULTS):
        raise ValueError(
            "tracer result outside the stated set: " + _sentence_text(result)
            + "; a tracer result stands among "
            + ", ".join(TRACER_RESULTS))
    return {
        "open_semantic_item": item,
        "point_in_run": point_in_run,
        "what_in_fact_passed": what_in_fact_passed,
        "result": result,
    }


def tracer_passage_records(run_id, results=None):
    """Return the tracer passage record set of one joint run: one
    record per open semantic item OS-1 to OS-14. An item with no
    stated result stands recorded as not attempted."""
    if isinstance(results, dict):
        stated = {key: item for key, item in dict.items(results)}
    else:
        stated = {}
    records = []
    for item in OPEN_SEMANTIC_ITEMS:
        outcome = stated.get(item, "not attempted")
        records.append(make_tracer_passage_record(
            item,
            "seam point of " + _sentence_text(item) + " in run " + _sentence_text(run_id),
            "recorded value for " + _sentence_text(item),
            outcome,
        ))
    return records


def positive_control_record():
    """Return the F-10 positive control record: a tracer value on
    the escrow request lien path, the one path the register
    records as meeting in shape, recorded as passing in record
    form."""
    return {
        "fixture": "F-10",
        "path": POSITIVE_CONTROL_PATH,
        "result": "passed as a record",
        "recorded_as_passing": True,
    }


_PASSAGE_BLANK_GLYPHS = frozenset(("\u2800", "\u115f"))

_PASSAGE_HANGUL_FILLER_CHARS = frozenset(("\u1160", "\u3164", "\uffa0"))


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies. A bytes, bytearray, or memoryview value
    stands read as its stored bytes, decoded as UTF-8 with
    undecodable bytes dropped, read through the base bytes
    form, never through a reading the value itself supplies.
    A value that is not a text form stores no text, so its
    stored text stands as the empty text."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


def _edge_parts(value):
    """The parts one edge container holds, in reading order: a
    list or tuple in its stored order, and a set or frozenset in
    the sorted order of the stored text of its parts, so an
    unordered dress stands read on its stored contents in an
    order insensitive form and never on its iteration order."""
    parts = _base_sequence(value)
    if isinstance(value, (set, frozenset)):
        return sorted(parts, key=_stored_text)
    return parts


def _stored_edge_text(value):
    """The text one edge part stores, in scalar or container
    dress: a scalar part by its stored text, and a list,
    tuple, set, or frozenset part by the stored text of its
    parts joined in order, so an edge part handed in split container dress
    stands judged as the text it stores. The container walk
    runs on an explicit stack with a cycle guard on the
    containers standing on the current path: a part carrying
    a cycle stands refused in named form as a ValueError,
    and no bare RecursionError escapes the reading, while a
    container shared from two places on different paths
    carries no cycle and stands read at each place."""
    if not isinstance(value, (list, tuple, set, frozenset)):
        return _stored_text(value)
    pieces = []
    on_path = {id(value)}
    stack = [[value, _edge_parts(value), 0]]
    while stack:
        frame = stack[-1]
        container, parts, index = frame
        if index >= len(parts):
            on_path.discard(id(container))
            stack.pop()
            continue
        frame[2] = index + 1
        part = parts[index]
        if isinstance(part, (list, tuple, set, frozenset)):
            if id(part) in on_path:
                raise ValueError(
                    "adapter edge text stands refused in named "
                    "form: an edge part carries a cycle, and no "
                    "edge text stands read")
            on_path.add(id(part))
            stack.append([part, _edge_parts(part), 0])
        else:
            pieces.append(_stored_text(part))
    return "".join(pieces)



def _passage_text_states_something(text):
    """Return True only where a text carries readable text, in
    the form of row R6-032: characters of Unicode category Cf,
    characters of Unicode category Mn, and the blank glyphs
    carry no readable text, and spacing alone carries none.
    The blank class settled at the flag acts stands in the
    same form here: characters of Unicode category Cc, lone
    combining marks of Unicode categories Mc and Me, and the
    Hangul filler characters also carry no readable text.
    A lone surrogate, an unassigned code point, and a private
    use character carry no readable text in the same manner,
    so characters of Unicode categories Cs, Cn, and Co also
    carry none. The text stands read from its stored
    characters, through the stored text reading, never
    through an iteration reading or a strip reading the
    handed value supplies."""
    cleaned = "".join(
        char for char in _stored_text(text)
        if char not in _PASSAGE_BLANK_GLYPHS
        and char not in _PASSAGE_HANGUL_FILLER_CHARS
        and unicodedata.category(char)
        not in ("Cf", "Mn", "Cc", "Mc", "Me", "Cs", "Cn", "Co"))
    return bool(str.strip(cleaned))


def _passage_field_is_blank(field_value):
    """Return True where a passage field holds only characters
    that state nothing readable, in string, bytes, bytearray,
    and memoryview forms alike. A bytes form stands read
    through its stored bytes: where those bytes decode as
    UTF-8 text, the decoded text stands judged on the same
    readable text form as a string, and where they do not,
    the bytes stand judged on their whitespace reading."""
    if isinstance(field_value, str):
        return not _passage_text_states_something(
            _stored_text(field_value))
    if isinstance(field_value, (bytes, bytearray, memoryview)):
        raw = bytes(field_value)
        if not bytes.strip(raw):
            return True
        try:
            decoded = bytes.decode(raw, "utf-8")
        except UnicodeDecodeError:
            return False
        return not _passage_text_states_something(decoded)
    return False


def validate_tracer_passage_set(records, positive_control=None):
    """Return True only for a complete and valid tracer set: one
    record per open semantic item, each carrying its four stated
    parts, and a positive control recorded as passing. The control
    stands read in the record form this module itself produces:
    its fixture, its path, and its passing result on the F-10
    path each stand required, beside the passing mark. A run whose
    positive control does not pass has no valid tracer passage
    record."""
    if not isinstance(records, (list, tuple)):
        return False
    stored_count = (
        list.__len__(records) if isinstance(records, list)
        else tuple.__len__(records))
    if stored_count != len(OPEN_SEMANTIC_ITEMS):
        return False
    items = []
    for record in _base_sequence(records):
        if not isinstance(record, dict):
            return False
        for field in _TRACER_FIELDS:
            if dict.get(record, field) is None:
                return False
            if field in ("what_in_fact_passed", "point_in_run"):
                field_value = dict.get(record, field)
                if _passage_field_is_blank(field_value):
                    return False
                if isinstance(field_value, bool) \
                        and field_value is False:
                    return False
                if isinstance(
                        field_value,
                        (list, tuple, dict, set, frozenset,
                         bytes, bytearray)) \
                        and not _value_present(field_value):
                    return False
        if not isinstance(dict.get(record, "open_semantic_item"), str):
            return False
        if not any(_stored_text_eq(dict.get(record, "result"), stated)
                   for stated in TRACER_RESULTS):
            return False
        items.append(_stored_copy(dict.get(record, "open_semantic_item")))
    if tuple(sorted(items)) != tuple(sorted(OPEN_SEMANTIC_ITEMS)):
        return False
    control = positive_control
    if control is None:
        control = positive_control_record()
    if not isinstance(control, dict):
        return False
    expected = positive_control_record()
    for field in ("fixture", "path", "result"):
        if not _stored_text_eq(
                dict.get(control, field), expected[field]):
            return False
    return dict.get(control, "recorded_as_passing") is True


def _stored_entries(run, keys):
    """Return the stored entries a run carries under any of the
    stated carriage keys, as a list of records."""
    entries = []
    for key in keys:
        carried = _bget(run, key)
        if isinstance(carried, dict):
            entries.append(carried)
        elif isinstance(carried, (list, tuple)):
            entries.extend(
                entry for entry in _base_sequence(carried)
                if isinstance(entry, dict))
    return entries


def _stored_pair_stands(run, choice):
    """Return True only where the choice pair a run in fact
    carries stands in agreement. The pair check reads the stored
    interpretation log entry and the stored run record entry of
    the choice, matched by choice identifier. A side the run
    does not store stands read from the entry this module builds
    for the choice, so a run storing neither side stands judged
    on its choices alone, as before."""
    identifier = _stored_copy(_bget(choice, "choice_identifier"))
    log_entries = _stored_entries(run, (
        "interpretation_log_entries", "interpretation_log_entry",
        "interpretation_log", "log_entries"))
    run_entries = _stored_entries(run, (
        "run_record_entries", "run_record_entry",
        "run_record_choices", "record_entries"))
    log_entry = next(
        (entry for entry in log_entries
         if _stored_pair_equal(
             _stored_copy(_bget(entry, "choice_identifier")),
             identifier)), None)
    run_entry = next(
        (entry for entry in run_entries
         if _stored_pair_equal(
             _stored_copy(_bget(entry, "choice_identifier")),
             identifier)), None)
    try:
        if log_entry is None and run_entry is None:
            return validate_choice_pair(
                interpretation_log_entry(choice),
                run_record_entry(choice))
        if log_entry is None:
            log_entry = interpretation_log_entry(choice)
        if run_entry is None:
            run_entry = run_record_entry(choice)
    except ValueError:
        return False
    return validate_choice_pair(log_entry, run_entry)


def validate_joint_run(run):
    """Return True only where a joint run may stand: every adapter
    choice it uses stands recorded as a choice in both records with
    the pair in agreement and its approval on the record, its
    tracer passage set stands complete and valid, and no cross
    seam effect in it carries settled or released."""
    if not isinstance(run, dict):
        return False
    choices = dict.get(run, "adapter_choices")
    if choices is not None and not isinstance(
            choices, (list, tuple, set, frozenset)):
        return False
    for choice in _base_sequence(choices):
        if not validate_adapter_choice(choice):
            return False
        if not _stored_pair_stands(run, choice):
            return False
    records = dict.get(run, "tracer_passage_records")
    if not validate_tracer_passage_set(
        records if records is not None else [],
        dict.get(run, "positive_control"),
    ):
        return False
    effects = dict.get(run, "cross_seam_effects")
    if effects is not None and not isinstance(
            effects, (list, tuple, set, frozenset)):
        return False
    for effect in _base_sequence(effects):
        if not validate_cross_seam_effect(effect):
            return False
    return True


def joint_run_failure(run):
    """Return the failure standing on a joint run, in the MOD-01
    failure value form, or None where the run stands. The name the
    value carries is the standing name of the ground that fails the
    run: an unapproved choice, a missing tracer record, and a
    settled cross seam effect each fail the run under their name,
    with run_status failed and complete False."""
    if not isinstance(run, dict):
        return mod01.failure_value("joint run record absent")
    choices = _bget(run, "adapter_choices")
    if choices is None:
        choices = []
    if not isinstance(choices, (list, tuple, set, frozenset)):
        return mod01.failure_value(
            "joint run adapter choices stand in no record list form fails")
    for choice in _base_sequence(choices):
        if not isinstance(choice, dict):
            return mod01.failure_value(
                "joint run adapter choice stands in no record form fails")
        if not choice_approval_stands(choice):
            return mod01.failure_value(
                "run using an unapproved adapter choice fails")
        if not validate_adapter_choice(choice):
            return mod01.failure_value(
                "adapter choice stands outside its recorded form")
        if not _stored_pair_stands(run, choice):
            return mod01.failure_value(
                "joint run choice pair stands in disagreement")
    records = _bget(run, "tracer_passage_records")
    if records is not None and not isinstance(
            records, (list, tuple, set, frozenset)):
        return mod01.failure_value(
            "joint run tracer passage records stand in no list form fails")
    if not isinstance(records, (list, tuple, set, frozenset)):
        records = []
    stored_records = _base_sequence(records)
    if len(stored_records) != len(OPEN_SEMANTIC_ITEMS):
        return mod01.failure_value(
            "joint run missing a tracer passage record fails")
    if not validate_tracer_passage_set(
            stored_records, _bget(run, "positive_control")):
        return mod01.failure_value(
            "joint run has no valid tracer passage record")
    effects = _bget(run, "cross_seam_effects")
    if effects is not None and not isinstance(
            effects, (list, tuple, set, frozenset)):
        if isinstance(effects, dict) \
                and not validate_cross_seam_effect(effects):
            return mod01.failure_value(
                "cross seam effect carries settled wording")
        return mod01.failure_value(
            "joint run cross seam effects stand in no list form fails")
    for effect in _base_sequence(effects):
        if not validate_cross_seam_effect(effect):
            return mod01.failure_value(
                "cross seam effect carries settled wording")
    return None


def seam_headline_claim_stands(run, items_touched):
    """Return True only where a headline claim resting on the seam
    may stand from a run: the run stands, and the claim carries
    the tracer passage result for every item it touches."""
    if joint_run_failure(run) is not None:
        return False
    by_item = {
        _stored_copy(_bget(record, "open_semantic_item")): record
        for record in _base_sequence(
            _bget(run, "tracer_passage_records"))
    }
    touched = _base_sequence(items_touched) if isinstance(
        items_touched, (list, tuple, set, frozenset)) else items_touched
    try:
        return all(_stored_copy(item) in by_item for item in touched)
    except TypeError:
        return False


def seam_effect_report(effect):
    """Return the interim reporting form of one cross seam effect:
    a vouch lien amount, a vouch release, or a slash outcome,
    reported as computed in Parley and not settled in the chosen
    escrow, with the lien state computed not settled, while NQ-45
    stands open. A value that is not an effect record reads as an
    empty effect, in the form the slash report reads its outcome."""
    if not isinstance(effect, dict):
        effect = {}
    _copy_guard(effect)
    return {
        "effect": _stored_copy(_bget(effect, "kind")),
        "reporting": INTERIM_REPORTING,
        "lien_state": COMPUTED_NOT_SETTLED,
        "value": _stored_copy(_bget(effect, "value")),
        "seam_status": COMPUTED_NOT_SETTLED,
    }


def validate_cross_seam_effect(effect):
    """Return True only where a cross seam effect carries no
    settled wording: its lien state validates under the MOD-01 bar
    for cross seam effects while NQ-45 stands open."""
    if not isinstance(effect, dict):
        return False
    state = dict.get(effect, "lien_state", COMPUTED_NOT_SETTLED)
    try:
        state_text = _stored_edge_text(state)
    except ValueError:
        return False
    return mod01.validate_lien_state(state_text, cross_seam=True)


def _wording_claims(lowered):
    """Split lowered wording into its claims, at sentence and
    clause boundaries, so each claim stands judged on its own."""
    claims = [lowered]
    for separator in (".", ";", "!", "?", ",", "\n"):
        claims = [
            part for claim in claims for part in claim.split(separator)]
    claims = [
        part for claim in claims for part in claim.split(" but ")]
    return [claim.strip() for claim in claims if claim.strip()]


def _claim_drifts(claim):
    """Return True where one claim drifts toward settled wording.

    A settled occurrence stands excused only where the word not
    stands directly before it in the same claim. A released
    occurrence stands excused only on that same ground, or where
    the word computed stands in the same claim.
    """
    index = claim.find("settled")
    while index != -1:
        if not claim[:index].rstrip().endswith("not"):
            return True
        index = claim.find("settled", index + 1)
    index = claim.find("released")
    while index != -1:
        if not claim[:index].rstrip().endswith("not"):
            start = max(
                claim.rfind(separator, 0, index)
                for separator in (",", ";", " and "))
            ends = [
                claim.find(separator, index + len("released"))
                for separator in (",", ";", " and ")]
            ends = [end for end in ends if end != -1]
            end = min(ends) if ends else len(claim)
            segment = claim[start:end]
            if "computed" not in segment:
                return True
        index = claim.find("released", index + 1)
    return False


def validate_seam_wording(text):
    """Return True only where report wording for a cross seam
    effect holds the interim form. Wording is judged per claim:
    an excusing word excuses only the claim it stands in, and a
    claim that names a seam effect as settled or released fails
    the whole wording."""
    if not isinstance(text, str):
        return False
    lowered = str.lower(_stored_text(text))
    return not any(
        _claim_drifts(claim) for claim in _wording_claims(lowered))


def slash_outcome_report(outcome):
    """Return a slash outcome in its interim form. Both standings
    of contested entry C-12 travel with the report, the chosen
    escrow core carries no cost pool account on either wording of
    that entry as a settled fact of this report, and no remainder
    destination stands named as settled."""
    _copy_guard(outcome)
    if not isinstance(outcome, dict):
        outcome = {}
    return {
        "effect": "slash",
        "reporting": INTERIM_REPORTING,
        "lien_state": COMPUTED_NOT_SETTLED,
        "value": _stored_copy(_bget(outcome, "value")),
        "c12_standings_carried": list(C12_STANDINGS),
        "cost_pool_account_named_as_settled": False,
        "remainder_destination": None,
        "remainder_named_as_settled": False,
    }


def validate_slash_report(report):
    """Return True only where a slash report names no remainder
    destination as settled and carries both standings of C-12."""
    if not isinstance(report, dict):
        return False
    if _value_present(_bget(report, "remainder_named_as_settled")):
        return False
    if _bget(report, "remainder_destination") is not None:
        return False
    return tuple(
        _stored_copy(part) for part in _base_sequence(
            _bget(report, "c12_standings_carried"))
    ) == C12_STANDINGS


def record_folding(choice, rulings_touched):
    """Record one adapter choice against the ruling text it
    touches, ruling by ruling: the S-06 part of the folding duty
    under decision D-02 condition three read with D-20. The ten
    ruling text gaps stand carried open by name in the record,
    filled by no inference."""
    if not isinstance(choice, dict):
        raise ValueError(
            "record_folding stands refused: the choice stands in no "
            "record form, a choice stands as a record, and no folding "
            "stands recorded")
    return {
        "choice_identifier": _stored_copy(
            _bget(choice, "choice_identifier")),
        "rulings_recorded": [
            _stored_copy(part) for part in _base_sequence(
                rulings_touched)],
        "recorded_ruling_by_ruling": True,
        "gaps_carried_open": list(RULING_TEXT_GAPS),
        "gaps_filled_by_inference": [],
    }


def validate_folding_record(record):
    """Return True only where a folding record covers its choice
    ruling by ruling and supplies no gap value by inference."""
    if not isinstance(record, dict):
        return False
    if not _value_present(dict.get(record, "recorded_ruling_by_ruling")):
        return False
    if not _value_present(dict.get(record, "rulings_recorded")):
        return False
    if _value_present(dict.get(record, "gaps_filled_by_inference")):
        return False
    carried = dict.get(record, "gaps_carried_open")
    if carried is not None and not isinstance(
            carried, (list, tuple, set, frozenset)):
        return False
    return tuple(
        _stored_copy(part) for part in _base_sequence(carried)
    ) == RULING_TEXT_GAPS


def ruling_effect_reporting_stands(difference, folding_records):
    """Return True only where a B-5 difference resting on a seam
    effect may stand reported as a ruling effect: a valid folding
    record stands behind every seam choice the difference rests
    on. Until that recording stands, no such difference stands
    reported as a ruling effect from this slice."""
    if not isinstance(difference, dict):
        return False
    choices = [
        _stored_copy(part) for part in _base_sequence(
            _bget(difference, "seam_choice_identifiers"))]
    if not choices:
        return False
    records = folding_records
    if isinstance(records, (list, tuple, set, frozenset)):
        records = _base_sequence(records)
    by_choice = {
        _stored_copy(_bget(record, "choice_identifier")): record
        for record in records or []
    }
    claimed = {
        _stored_copy(part) for part in _base_sequence(
            _bget(difference, "rulings_claimed"))}
    for identifier in choices:
        record = by_choice.get(identifier)
        if record is None or not validate_folding_record(record):
            return False
        recorded = {
            _stored_copy(part) for part in _base_sequence(
                _bget(record, "rulings_recorded"))}
        if not claimed.issubset(recorded):
            return False
    return True


def classify_seam_feedback(item, treatment_choice, standings):
    """The seam feedback classification act for one seam item. The
    treatment stands recorded as an adapter choice with both
    standings carried, the act stands priced per seam item, and
    one paired sensitivity run stands required per feeding item
    before any headline rests on it."""
    if treatment_choice is not None and not isinstance(
            treatment_choice, dict):
        raise ValueError(
            "classify_seam_feedback stands refused: the treatment "
            "choice stands in no record form, a treatment choice "
            "stands as a record, and no classification stands recorded")
    return {
        "open_semantic_item": item,
        "classification": "feeding seam item",
        "treatment_recorded_as": "adapter choice",
        "treatment_choice_identifier": _stored_copy(_bget(
            treatment_choice, "choice_identifier")) if isinstance(
            treatment_choice, dict) else None,
        "both_standings_carried": [
            _stored_copy(part) for part in _base_sequence(standings)],
        "pricing": "priced per seam item",
        "paired_sensitivity_runs_required": 1,
        "headline_may_rest": False,
    }


def validate_feedback_classification(record):
    """Return True only where a classification carries both
    standings and its paired sensitivity requirement."""
    if not isinstance(record, dict):
        return False
    if len(_base_sequence(
            _bget(record, "both_standings_carried"))) != 2:
        return False
    if not _stored_text_eq(
            _bget(record, "treatment_recorded_as"), "adapter choice"):
        return False
    required = _bget(record, "paired_sensitivity_runs_required")
    return isinstance(required, int) \
        and not isinstance(required, bool) \
        and int.__eq__(required, 1)


__all__ = [
    "COPY_DEPTH_BOUND",
    "OPEN_SEMANTIC_ITEMS",
    "SEAM_GAP_COUNTS",
    "TRACER_RESULTS",
    "POSITIVE_CONTROL_PATH",
    "COMPUTED_NOT_SETTLED",
    "INTERIM_REPORTING",
    "RULING_TEXT_GAPS",
    "C12_STANDINGS",
    "seam_gap_counts",
    "dependency_record",
    "validate_dependency_record",
    "make_adapter_choice",
    "interpretation_log_entry",
    "run_record_entry",
    "validate_choice_pair",
    "append_reading",
    "reading_for_result",
    "choice_approval_stands",
    "validate_adapter_choice",
    "seam_status",
    "make_tracer_passage_record",
    "tracer_passage_records",
    "positive_control_record",
    "validate_tracer_passage_set",
    "validate_joint_run",
    "joint_run_failure",
    "seam_headline_claim_stands",
    "seam_effect_report",
    "validate_cross_seam_effect",
    "validate_seam_wording",
    "slash_outcome_report",
    "validate_slash_report",
    "record_folding",
    "validate_folding_record",
    "ruling_effect_reporting_stands",
    "classify_seam_feedback",
    "validate_feedback_classification",
]

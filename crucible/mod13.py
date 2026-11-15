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

import itertools

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


def _base_contains(record, key):
    """Test one key through the base dict contains, never
    through a contains reading the record itself supplies."""
    return isinstance(record, dict) and dict.__contains__(
        record, key)


def _base_sequence_items(value):
    """Read the stored items of a handed list or tuple through
    its base class iteration, never through an iteration the
    value itself supplies."""
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, list):
        return list(list.__iter__(value))
    return []


def _base_sequence_length(value):
    """Read the stored length of a handed list or tuple through
    its base class length, never through a length reading the
    value itself supplies."""
    if isinstance(value, tuple):
        return tuple.__len__(value)
    if isinstance(value, list):
        return list.__len__(value)
    return 0


def _stored_present(value):
    """Whether a stored value stands present, judged on what it
    stores: containers and text by their base class length, a
    boolean by itself, a number by standing apart from zero,
    and any other stored value by standing apart from None."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, (bytes, bytearray, memoryview)):
        return len(bytes(value)) > 0
    if isinstance(value, list):
        return list.__len__(value) > 0
    if isinstance(value, tuple):
        return tuple.__len__(value) > 0
    if isinstance(value, dict):
        return dict.__len__(value) > 0
    if isinstance(value, frozenset):
        return frozenset.__len__(value) > 0
    if isinstance(value, set):
        return set.__len__(value) > 0
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _stored_string(value):
    """The stored string form of a value: a text value through
    its base class string form, any other value through the
    safe string form, which renders through the base object
    repr where the string reading the value itself supplies
    raises, so a caller building a sentence or an identifier
    from the stored form never escapes bare on that reading."""
    if isinstance(value, str):
        return str.__str__(value)
    return _safe_str(value)


def _safe_repr(value):
    """Render a handed value for a refusal or failure sentence:
    through its repr reading where that reading stands, and
    through the base object repr where the repr reading the
    value itself supplies raises, so a sentence naming the
    handed value never escapes bare on that reading."""
    try:
        return repr(value)
    except Exception:
        return object.__repr__(value)


def _safe_str(value):
    """Render a handed value for a refusal sentence through
    its string reading where that reading stands, and through
    the safe repr form where the string reading the value
    itself supplies raises, so a sentence naming the handed
    value never escapes bare on that reading."""
    try:
        return str(value)
    except Exception:
        return _safe_repr(value)


def _vocabulary_text(value):
    """Render a handed value for a vocabulary sentence: a text
    form or a buffer form stands rendered by the text it stores,
    read through _stored_text, so a memoryview form names the
    value it stores and never a volatile memory address. Any
    other form stands rendered through _safe_str."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        stored = _stored_text(value)
        if stored is not None:
            return stored
    return _safe_str(value)


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


def _stored_key_text(value):
    """The stored text of a key or of a part of a key, under the
    governing stored text settlement, in the form crucible/mod01.py
    states for its key reading."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list, set, frozenset)):
        parts = []
        for part in _base_container_items(value):
            part_text = _stored_key_text(part)
            parts.append(part_text if part_text is not None else "")
        if isinstance(value, (set, frozenset)):
            # An unordered container stores no part order, so
            # its single joined text stands in the sorted order
            # of its part texts, the same at every hash seed.
            # The full set of joins it can stand in stands at
            # _stored_key_texts, which the field readings use.
            parts.sort()
        return "".join(parts)
    return None


def _stored_key_texts(value):
    """Every joined stored text a key can stand in. An ordered
    container contributes the joins of its parts in their
    stored order, each part contributing every text of its
    own. An unordered container stores no order, so it
    contributes the joins under every ordering of its direct
    parts, in the form the sister modules state for their
    joined candidates: complete for an unordered container
    holding at most seven direct parts and while the distinct
    joins stand at or under 5040. Past either bound the
    unordered container contributes its sorted join alone,
    as _stored_key_text states it. The ordered limb stands
    bounded by the same stated discipline, in the form
    settlement S-13 states: the combination total of its
    parts' texts stands computed before any join stands
    built, and where that total passes 5040 the ordered
    container contributes its stored order join alone, as
    _stored_key_text states it, so no cross product past
    the bound stands ever built. The unordered limb stands
    under the same discipline in the same form: the
    combination total of its parts' texts stands computed
    before any join stands built, and where that total
    passes 5040 the unordered container contributes its
    sorted join alone, as _stored_key_text states it, so
    no cross product past the bound stands ever built for
    any ordering. The joins of an unordered container stand
    built by used part sets, each part entering a join once,
    with the partial joins deduplicated as they grow, so
    orderings that compose the same texts stand built once
    and the work the act performs stands bounded by the
    distinct partial joins, never by the factorial of the
    part count times the cross product of one ordering.
    Where a partial join set passes 5040 the unordered
    container contributes its sorted join alone, in the
    bound form this reading already states."""
    if isinstance(value, (tuple, list)):
        part_texts = [
            _stored_key_texts(part)
            for part in _base_container_items(value)]
        total = 1
        for texts in part_texts:
            total *= len(texts)
            if total > 5040:
                return {_stored_key_text(value)}
        joined = {""}
        for texts in part_texts:
            joined = {
                head + (tail if tail is not None else "")
                for head in joined
                for tail in texts}
        return joined
    if isinstance(value, (set, frozenset)):
        parts = _base_container_items(value)
        if len(parts) <= 7:
            part_texts = [_stored_key_texts(part) for part in parts]
            total = 1
            for texts in part_texts:
                total *= len(texts)
                if total > 5040:
                    return {_stored_key_text(value)}
            states = {0: {""}}
            for _level in range(len(parts)):
                next_states = {}
                for mask, partials in states.items():
                    for index in range(len(parts)):
                        bit = 1 << index
                        if mask & bit:
                            continue
                        grown = next_states.setdefault(mask | bit, set())
                        for head in partials:
                            for tail in part_texts[index]:
                                grown.add(
                                    head
                                    + (tail if tail is not None else ""))
                                if len(grown) > 5040:
                                    return {_stored_key_text(value)}
                states = next_states
            return states.get((1 << len(parts)) - 1, set())
        return {_stored_key_text(value)}
    return {_stored_key_text(value)}


def _stored_text(value):
    """The stored text of a handed value under the governing
    stored text settlement: a text value through its stored
    characters, a bytes, bytearray, or memoryview value through
    its decoded stored bytes, and a single part container through
    the stored text of its one part. Any other form stores no
    text here and reads as None."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list, set, frozenset)):
        items = _base_container_items(value)
        if len(items) == 1:
            return _stored_text(items[0])
        return None
    return None


def _stored_text_eq(first, second):
    """Whether two handed values agree in stored text, where the
    second stands as a plain stated text."""
    stored = _stored_text(first)
    return stored is not None and str.__eq__(stored, second)


def _stored_get(record, field):
    """Read one field of a handed record through its stored
    pairs, a field standing present where a stored key carries
    its name in stored text, never through a hash or equality
    reading a handed key supplies."""
    if not isinstance(record, dict):
        return None
    for key, item in dict.items(record):
        if any(
                text is not None and str.__eq__(text, field)
                for text in _stored_key_texts(key)):
            return item
    return None


def _all_stored_values(record, fields):
    """Every stored value a handed record carries under any of
    the stated fields, read through its stored pairs in the form
    _stored_get states."""
    values = []
    if not isinstance(record, dict):
        return values
    for key, item in dict.items(record):
        key_texts = _stored_key_texts(key)
        if any(
                text is not None and str.__eq__(text, field)
                for text in key_texts for field in fields):
            if item is not None:
                values.append(item)
    return values


def _first_stored_value(record, fields):
    values = _all_stored_values(record, fields)
    return values[0] if values else None


def _norm_identifier(value):
    """The identifier a handed value states, in its stored text
    where it carries one, and as itself where it carries none."""
    stored = _stored_text(value)
    return stored if stored is not None else value


def _result_field_value(value):
    """A field value as a delivered comparison result carries
    it: in its stored text where it carries one, so a bytes,
    bytearray, memoryview, or single part container dress
    stands named as the plain text it stores, in the same
    form the result names its bearing and entry run
    identifiers, and otherwise as a frozen copy of itself,
    so no field of a delivered result stands shared with a
    mutable value the caller handed in."""
    stored = _stored_text(value)
    if stored is not None:
        return stored
    return _freeze(value)


def _identifiers_agree(first, second):
    """Whether two identifier values state the same identifier,
    judged on their stored texts where either carries one."""
    first_text = _stored_text(first)
    second_text = _stored_text(second)
    if first_text is not None or second_text is not None:
        return (first_text is not None and second_text is not None
                and str.__eq__(first_text, second_text))
    # Neither identifier carries a stored text, so the
    # judgement stands on the strict base reading of this
    # module, which judges every part through base class
    # comparisons and a value in no stated form by identity
    # alone, never through an equality reading a handed
    # value supplies.
    try:
        return _strict_eq(first, second)
    except NamedReplicationFailure:
        return False


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
                + ", counted on the containers only basis, the depth "
                "of a value counting the containers standing above it "
                "and a scalar leaf counting no depth of its own, and "
                "no comparison stands performed on it"
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
    if isinstance(first, memoryview) or isinstance(second, memoryview):
        if not (isinstance(first, memoryview)
                and isinstance(second, memoryview)):
            return False
        # A memoryview part stands judged by the bytes it
        # views, as the bytearray limb below judges by
        # content and as the neighbouring acts of this
        # module read memoryview by its bytes as one buffer
        # family, never by the identity of the buffer.
        result = bytes.__eq__(
            memoryview.tobytes(first), memoryview.tobytes(second))
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
    if _stored_present(_base_get(claim, "hash_equality_claimed")):
        return False
    if _stored_present(_base_get(
            claim, "detection_state_completeness_claimed")):
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
    if _base_str_member(use, NON_DETERMINISTIC_BARRED_USES):
        return False
    if _base_str_eq(use, "screening observation"):
        return bool(labelled_screening)
    if _base_str_member(use, NON_DETERMINISTIC_PERMITTED_USES):
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
    scope = _base_get(claim, "detection_scope")
    if scope is not None and not _base_str_eq(
            scope, "verdict level only"):
        return False
    points = _base_get(claim, "detection_comparison_points")
    if points is not None:
        if not isinstance(points, (list, tuple)):
            return False
        stored_points = _base_sequence_items(points)
        if _base_sequence_length(points) != len(
                DETECTION_COMPARISON_POINTS):
            return False
        for stored_point, named_point in zip(
                stored_points, DETECTION_COMPARISON_POINTS):
            if not _base_str_eq(stored_point, named_point):
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
    if not _base_str_member(standard, STANDARDS):
        raise NamedReplicationFailure(
            "unknown replication standard: " + _safe_str(standard)
            + "; the stated standard stands as exact replay alone, "
            "and no verdict record stands made")
    if not _base_str_member(outcome, ("rests", "does not rest")):
        raise NamedReplicationFailure(
            "unknown verdict outcome: " + _vocabulary_text(outcome)
            + "; the stated outcomes stand as rests and does not "
            "rest, and no verdict record stands made")
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


def verdict_record_validation_failures(record):
    failures = []
    if not isinstance(record, dict):
        return ["the verdict record stands in no record form"]
    claim_identifier = dict.get(record, "claim_identifier")
    if isinstance(claim_identifier, str):
        if str.__len__(claim_identifier) == 0:
            failures.append("claim_identifier stands empty")
    elif not _stored_present(claim_identifier):
        failures.append("claim_identifier stands absent")
    if not _base_str_member(
            dict.get(record, "outcome"), ("rests", "does not rest")):
        failures.append(
            "outcome stands outside the stated outcomes "
            "(rests, does not rest): " + _safe_repr(dict.get(record, "outcome")))
    if _base_str_eq(
            dict.get(record, "standard_applied"),
            "distributional equivalence"):
        failures.append(
            "standard_applied names the distributional equivalence "
            "standard, which stands barred while the OP-20 "
            "quantities stand unfixed")
    elif not _base_str_eq(
            dict.get(record, "standard_applied"), "exact replay alone"):
        failures.append(
            "standard_applied stands outside the stated standard "
            "(exact replay alone): "
            + _safe_repr(dict.get(record, "standard_applied")))
    if not _base_str_eq(
            dict.get(record, "replication_statement"),
            REPLICATION_STATEMENT):
        failures.append(
            "replication_statement does not stand as the stated "
            "replication statement")
    if not _replication_sentences_ok(record):
        failures.append(
            "replication_statement_sentences stand empty or "
            "contradict the joined statement (sentence form)")
    return failures


def replay_claim_validation_failures(claim):
    if not isinstance(claim, dict):
        return ["the replay claim stands in no record form"]
    failures = []
    if _stored_present(_base_get(claim, "hash_equality_claimed")):
        failures.append(
            "hash_equality_claimed stands asserted: a replay claim "
            "asserting byte level hash equality stands refused "
            "while OP-24 stands open in part")
    if _stored_present(_base_get(
            claim, "detection_state_completeness_claimed")):
        failures.append(
            "detection_state_completeness_claimed stands asserted: "
            "completeness over the detection state stands refused")
    return failures


def resume_claim_validation_failures(claim):
    if not isinstance(claim, dict):
        return ["the resume claim stands in no record form"]
    failures = []
    scope = _base_get(claim, "detection_scope")
    if scope is not None and not _base_str_eq(
            scope, "verdict level only"):
        failures.append(
            "detection_scope stands wider than verdict level only: "
            + _safe_repr(scope) + " (scope form)")
    points = _base_get(claim, "detection_comparison_points")
    if points is not None:
        if not isinstance(points, (list, tuple)):
            failures.append(
                "detection_comparison_points stand in no list form")
        elif _base_sequence_length(points) != len(
                DETECTION_COMPARISON_POINTS):
            failures.append(
                "detection_comparison_points stand at a count other "
                "than the two named points")
        else:
            for stored_point, named_point in zip(
                    _base_sequence_items(points),
                    DETECTION_COMPARISON_POINTS):
                if not _base_str_eq(stored_point, named_point):
                    if any(
                            _base_str_eq(stored_point, named)
                            for named in DETECTION_COMPARISON_POINTS):
                        failures.append(
                            "detection_comparison_points stand in "
                            "an order other than the two named "
                            "points in their stated order: "
                            + _safe_repr(stored_point)
                            + " stands at a position other than "
                            "its named position")
                    else:
                        failures.append(
                            "detection_comparison_points name a point "
                            "outside the two named points: "
                            + _safe_repr(stored_point))
                    break
    return failures


def probe_claim_validation_failures(claim):
    if not isinstance(claim, dict):
        return ["the probe claim stands in no record form"]
    failures = []
    if _stored_present(_base_get(
            claim, "margin_or_method_presented_as_settled")):
        failures.append(
            "margin_or_method_presented_as_settled stands asserted: "
            "a margin or method presented as settled before the "
            "family record fixes it stands refused")
    if _stored_present(_base_get(
            claim, "catalogue_presented_as_settled")):
        failures.append(
            "catalogue_presented_as_settled stands asserted: a "
            "catalogue presented as a delivered form with a settled "
            "field list stands refused")
    return failures


def scoring_record_validation_failures(record):
    if not isinstance(record, dict):
        return ["the scoring record stands in no record form"]
    failures = []
    if _base_get(record, "inside_run_boundary"):
        failures.append(
            "inside_run_boundary stands asserted: a scoring record "
            "stands outside the run boundary")
    if _base_get(record, "value_returned_into_run") is not None:
        failures.append(
            "value_returned_into_run stands stated: no value stands "
            "returned into the run")
    if not _base_str_eq(
            _base_get(record, "profile_bound_label"),
            PROFILE_BOUND_LABEL):
        failures.append(
            "profile_bound_label does not stand as the stated "
            "carriage value")
    separations = _base_get(record, "separations")
    if not isinstance(separations, dict):
        failures.append("separations stand in no record form")
    else:
        for name in SCORING_SEPARATIONS:
            if not _base_get(separations, name):
                failures.append(
                    "separations name no standing for: " + name)
    return failures


def aggregate_form_validation_failures(form):
    if not isinstance(form, (list, tuple)):
        return ["the aggregate form stands in no list form"]
    failures = []
    stored_form = _base_sequence_items(form)
    if any(_base_str_eq(item, "horizon") for item in stored_form):
        failures.append(
            "the aggregate form carries a horizon field, and an "
            "aggregate form changes no meaning with the horizon")
    daily = daily_aggregate_form()
    if _base_sequence_length(form) != len(daily):
        failures.append(
            "the aggregate form stands at a length other than the "
            "daily aggregate form")
    elif not all(
            _base_str_eq(stored_item, daily_item)
            for stored_item, daily_item in zip(stored_form, daily)):
        if all(
                any(
                    _base_str_eq(stored_item, daily_item)
                    for daily_item in daily)
                for stored_item in stored_form):
            failures.append(
                "the aggregate form stands in an order other "
                "than the daily aggregate form")
        else:
            failures.append(
                "the aggregate form names a field outside the daily "
                "aggregate form")
    return failures


def publishable_on_replication_failures(claim, verdict):
    if not isinstance(verdict, dict):
        return ["the verdict stands in no record form"]
    failures = []
    verdict_claim = dict.get(verdict, "claim_identifier")
    handed_claim = (
        _base_get(claim, "claim_identifier")
        if isinstance(claim, dict) else None)
    if isinstance(verdict_claim, str) or isinstance(handed_claim, str):
        if not _base_str_eq(verdict_claim, handed_claim):
            failures.append(
                "the verdict names a different claim than the claim "
                "handed: claim mismatch")
    elif not _strict_eq(verdict_claim, handed_claim):
        failures.append(
            "the verdict names a different claim than the claim "
            "handed: claim mismatch")
    for item in verdict_record_validation_failures(verdict):
        failures.append("verdict record: " + item)
    if not failures and not _base_str_eq(
            dict.get(verdict, "outcome"), "rests"):
        failures.append(
            "the verdict outcome does not rest: outcome stands as "
            + _safe_repr(dict.get(verdict, "outcome"))
            + ", and publication requires the outcome rests")
    return failures


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
    elif not _stored_present(claim_identifier):
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
    if _stored_present(_base_get(
            claim, "margin_or_method_presented_as_settled")):
        return False
    if _stored_present(_base_get(
            claim, "catalogue_presented_as_settled")):
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
    if not _stored_present(_base_get(record, "run_identifier")):
        return False
    if not _base_contains(record, "scoring_day_range"):
        return False
    return (
        _base_contains(
            record, "verdict_states_and_accumulator_updates")
        or _base_contains(
            record, "verdict_states_by_agent_and_day")
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
    for index, record in enumerate(_base_sequence_items(outputs)):
        if not _is_detection_output(record):
            raise NamedReplicationFailure(
                "scoring counts only checkable DetectionOutput records: input at position "
                + str(index) + " stands in no DetectionOutput form"
            )
    return {
        "outputs_scored": _base_sequence_length(outputs),
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
    if _base_get(record, "inside_run_boundary"):
        return False
    if _base_get(record, "value_returned_into_run") is not None:
        return False
    if not _base_str_eq(
            _base_get(record, "profile_bound_label"), PROFILE_BOUND_LABEL):
        return False
    separations = _base_get(record, "separations")
    if not isinstance(separations, dict):
        return False
    return all(_base_get(separations, name) for name in SCORING_SEPARATIONS)


# ---------------------------------------------------------------------------
# Witness rerun and history extension, operations C-04 and C-05
# ---------------------------------------------------------------------------

def witness_rerun(original, rule_set_version=None):
    """A witness rerun under a later rule set: a new run linked to
    the original, carrying the rule set version identity it ran
    under, read as a report of the difference between two rule
    sets and nothing more. The original result, the original run
    record, and the original witness standing stand untouched."""
    stored_original = original if isinstance(
        original, dict) else {}
    stored_run_id = _base_get(stored_original, "run_id")
    rerun = {
        "run_id": _stored_string(stored_run_id) + "-rerun",
        "linked_to": stored_run_id,
        "rule_set_version": rule_set_version,
        "original_rule_set_version": _base_get(
            stored_original, "rule_set_version"),
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
    read_as = _base_get(reading, "read_as")
    if _base_str_eq(read_as, "corrected version of the original"):
        return False
    if _stored_present(_base_get(reading, "overwrites_original")):
        return False
    return read_as is None or _base_str_eq(
        read_as, "difference between two rule sets only")


def rerun_reading_validation_failures(reading):
    """The named failures companion of validate_rerun_reading:
    each ground the act refuses on stands named apart, so an
    operator can tell a reading stated as the corrected version
    of the original from a reading that overwrites the original
    and from a reading stated in no stated form. This companion
    states the act's grounds only and settles nothing under
    OP-16, which stands OPEN."""
    if not isinstance(reading, dict):
        return ["the rerun reading stands in no record form"]
    failures = []
    read_as = _base_get(reading, "read_as")
    if _base_str_eq(read_as, "corrected version of the original"):
        failures.append(
            "read_as stands as the corrected version of the "
            "original: a rerun stands read as a report of the "
            "difference between two rule sets only, never as "
            "the corrected version of the original")
    elif read_as is not None and not _base_str_eq(
            read_as, "difference between two rule sets only"):
        failures.append(
            "read_as stands outside the stated reading "
            "(difference between two rule sets only): "
            + _safe_repr(read_as))
    if _stored_present(_base_get(reading, "overwrites_original")):
        failures.append(
            "overwrites_original stands asserted: a rerun "
            "overwrites neither the original result, nor the "
            "original record, nor the original standing")
    return failures


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
    walks, so what is guarded is what is copied. The history
    items and the appended segment stand copied under one
    shared memo, so a part shared across items, or between
    the history and the appended segment, stands in the
    returned history as one copy and the sharing stands."""
    if not isinstance(history, (list, tuple)):
        raise NamedReplicationFailure(
            "a history extension stands refused: the handed history "
            "stands in no list form: " + _safe_repr(history)
            + "; a history stands as a non empty list of segments, "
            "and no extension stands made")
    if not _history_base_items(history):
        raise NamedReplicationFailure(
            "a history extension stands refused: the handed history "
            "stands empty, no existing segment stands to extend, "
            "and no extension stands made")
    if not isinstance(segment, dict):
        raise NamedReplicationFailure(
            "a history extension appends a segment record: the appended value stands in no record form"
            ", and no extension stands made"
        )
    grounds = []
    for label, handed in (
            ("the handed history", history),
            ("the appended segment", segment)):
        past, cyclic = _bound_grounds(handed)
        if past:
            grounds.append(
                label + " stands past the bound of "
                + str(COMPARISON_DEPTH_BOUND)
                + " (counted on the containers only basis)"
                + ", and no extension stands made")
        if cyclic:
            grounds.append(
                label + " carries a cycle"
                + " (counted on the containers only basis)"
                + ", and no extension stands made")
    if grounds:
        raise NamedReplicationFailure(
            "a history extension stands refused: " + "; ".join(grounds))
    memo = {}
    segments = [_freeze(item, memo) for item in _history_base_items(history)]
    first = segments[0]
    if not isinstance(first, dict) or not first.get("rule_set_version"):
        raise NamedReplicationFailure(
            "a history extension stands under the same rule set version as the segment it extends: no rule set version stands on that segment"
            ", and no extension stands made"
        )
    if not first.get("run_id"):
        raise NamedReplicationFailure(
            "a history extension links by run identifier: no run identifier stands on the segment it extends"
            ", and no extension stands made"
        )
    appended = _freeze(segment, memo)
    stated_version = appended.get("rule_set_version")
    if stated_version is not None and stated_version != first.get("rule_set_version"):
        raise NamedReplicationFailure(
            "a history extension stands under the same rule set version as the segment it extends: the appended segment states another version"
            ", and no extension stands made"
        )
    stated_link = appended.get("linked_run")
    if stated_link is not None and stated_link != first.get("run_id"):
        raise NamedReplicationFailure(
            "a history extension links to the segment it extends: the appended segment states another linked run"
            ", and no extension stands made"
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
    that field, the field name read in its stored text under
    any key dress, and a single record handed whole reads as a
    one record log, a lone record standing under its run_id
    alias alone counting as a record."""
    if run_log is None:
        return None
    if isinstance(run_log, dict):
        if _stored_get(run_log, "run_identifier") is not None or (
                _stored_get(run_log, "run_id") is not None):
            return [run_log]
        for key in ("runs", "run_records", "records", "run_log"):
            inner = _stored_get(run_log, key)
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
    record is never a run log entry for this check. The pilot
    standing stands read in every form the product itself
    stamps: the run class, store kind, kind, and record kind
    fields carrying the value pilot, and the pilot artefact
    form the MOD-14 pilot runner stamps, the form field
    carrying the pilot artefact value and the confinement
    label field carrying the pilot confined value. Every
    marker stands read in its stored text, in bytes,
    bytearray, memoryview, and single part container dress
    alike, under the governing stored text settlement."""
    for field in ("run_class", "store_kind", "kind", "record_kind"):
        if _stored_text_eq(_stored_get(record, field), "pilot"):
            return True
    if _stored_text_eq(_stored_get(record, "form"), "pilot artefact") or (
            _stored_text_eq(
                _stored_get(record, "form"),
                "pilot artefact, stored apart from sweep results")):
        return True
    if _stored_text_eq(
            _stored_get(record, "confinement_label"), "pilot confined"):
        return True
    return False


def _record_bears_on_entry(record, entry):
    """True where a run record bears on the claim an entry
    carries. A record of another family, or of another claim,
    where both sides state the identifier, bears on no claim of
    this entry. Every identifier field a record or an entry
    states stands read, through its stored pairs and in its
    stored text, so a record that matches on one of its two
    family or claim fields and contradicts on the other bears
    in no part, and an identifier stated under a key in bytes
    or container dress, or as a value in bytes, bytearray,
    memoryview, or single part container dress, stands read
    as the identifier it stores. A failed run bears as any
    other run bears: its status stands read as failed and it
    stands in the log."""
    family_fields = (
        "sweep_family_identifier", "family_identifier", "family_id")
    record_families = _all_stored_values(record, family_fields)
    entry_families = _all_stored_values(entry, family_fields)
    if record_families and entry_families:
        for record_family in record_families:
            for entry_family in entry_families:
                if not _identifiers_agree(record_family, entry_family):
                    return False
    claim_fields = ("claim_identifier", "claim_id")
    record_claims = _all_stored_values(record, claim_fields)
    entry_claims = _all_stored_values(entry, claim_fields)
    if record_claims and entry_claims:
        for record_claim in record_claims:
            for entry_claim in entry_claims:
                if not _identifiers_agree(record_claim, entry_claim):
                    return False
    return True


def _entry_run_identifiers(entry):
    """The run identifiers a registry entry carries, read
    through base class readings from its screening and held out
    confirmation identifier fields, the two identifier fields
    Form 22 item 1 states, and from no other field. Each stated
    identifier stands named in its stored text, so an identifier
    stated in bytes, bytearray, memoryview, list, or tuple dress,
    whether as one element of a container field or as a bare
    value of the field itself, stands named as the run it
    states."""
    identifiers = []
    for field in ("screening_run_identifiers",
                  "held_out_confirmation_run_identifiers"):
        value = _stored_get(entry, field)
        if isinstance(value, (list, tuple, set, frozenset)):
            named = [
                _norm_identifier(item)
                for item in _base_container_items(value)]
            if isinstance(value, (set, frozenset)):
                # An unordered identifier field stores no
                # order, so its identifiers stand delivered
                # in the sorted order of the stored text
                # they carry, the same at every hash seed.
                # An identifier carrying no stored text keeps
                # its base reading place after the text
                # forms, as the bound at this act states.
                named.sort(key=_identifier_order_key)
            identifiers.extend(named)
        elif value is not None:
            identifiers.append(_norm_identifier(value))
    return identifiers


def _identifier_order_key(identifier):
    """The stated order key for one identifier drawn from an
    unordered identifier field: its stored text where it
    carries one, and its kind name after the text forms
    where it carries none."""
    text = _stored_text(identifier)
    if text is not None:
        return (0, text, "")
    return (1, type(identifier).__name__, "")


def _record_status_failed(record):
    """True where a record stands as a failed run, under the
    status field or the run status field. Every status field
    the record states stands read, in its stored text in any
    dress, so a run failed in its second status field, or in
    bytes or single part container dress, stands named as a
    failed run stands named. A failed run bears as any other
    run bears; this reading names it in the result only."""
    for value in _all_stored_values(record, ("status", "run_status")):
        if _stored_text_eq(value, "failed"):
            return True
    return False


def _stored_count(value):
    """Read a stored count as a plain integer, or None where
    the value stores no count. A boolean stores no count. A
    figure stated in digit text, in any text dress the stored
    text settlement reads, stores the count it states."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int(value)
    text = _stored_text(value)
    if text is not None:
        stripped = text.strip()
        digits = stripped[1:] if stripped[:1] in ("+", "-") else stripped
        if digits and all("0" <= char <= "9" for char in digits):
            return int(stripped)
    return None


def _plan_expected_count(plan, entry):
    """Derive the expected run count from one replicate plan,
    in the smallest forms the records state. A plan stating an
    expected count carries that count. A plan stating a list
    of replicate counts per grid point carries the sum of its
    counts. A plan stating replicates per grid point carries
    the product of that figure and its grid points, the grid
    points standing in the plan or, where the plan states
    none, in the entry, under the grid points field or the
    grid point count field alike, and a grid points mapping
    stating its points as its stored pairs counts as its
    points. A plan nested under a replicate plan field reads
    through that field. Figures stand read through their
    stored pairs and in digit text as _stored_count states,
    and field names stand read in stored text under any key
    dress. No other form derives a count, and no figure
    stands invented here."""
    if plan is None:
        return None
    direct = _stored_count(plan)
    if direct is not None:
        return direct
    if isinstance(plan, (list, tuple, set, frozenset)):
        total = 0
        for item in _base_container_items(plan):
            count = _stored_count(item)
            if count is None:
                return None
            total += count
        return total
    if not isinstance(plan, dict):
        return None
    stated = _stored_count(_first_stored_value(
        plan, ("expected_run_count", "expected_runs", "expected_count")))
    if stated is not None:
        return stated
    counts = _first_stored_value(plan, ("replicate_counts", "replicates_per_point"))
    if isinstance(counts, (list, tuple, set, frozenset)):
        return _plan_expected_count(counts, entry)
    per_point = _stored_count(_first_stored_value(
        plan, ("replicates_per_grid_point", "replicate_count",
               "replicates")))
    if per_point is not None:
        points = _first_stored_value(
            plan, ("grid_points", "grid_point_count"))
        if points is None and isinstance(entry, dict):
            points = _first_stored_value(
                entry, ("grid_points", "grid_point_count"))
        point_count = _stored_count(points)
        if point_count is None and isinstance(
                points, (list, tuple, set, frozenset)):
            point_count = len(_base_container_items(points))
        if point_count is None and isinstance(points, dict):
            point_count = len(list(dict.items(points)))
        if point_count is not None:
            return per_point * point_count
    nested = _stored_get(plan, "replicate_plan")
    if nested is not None:
        return _plan_expected_count(nested, entry)
    return None


def _manifest_expected_count(manifest, entry):
    """Derive the expected run count from a FamilyManifest
    handed to the act, through the family record replicate
    plan it carries as sealed, in the form
    _plan_expected_count states, the replicate plan field
    read through its stored pairs under any key dress."""
    if manifest is None:
        return None
    if isinstance(manifest, dict):
        plan = _stored_get(manifest, "replicate_plan")
        if plan is not None:
            return _plan_expected_count(plan, entry)
    return _plan_expected_count(manifest, entry)


def _expected_count_and_source(entry, source, family_manifest):
    """Return the expected run count and the name of its
    source. The governing source stands first: the family
    record replicate plan as sealed in the FamilyManifest,
    handed as the family manifest argument, carried on the
    entry, or carried on the run log mapping, the manifest
    read through its stored pairs under any key dress. The
    stated expected count fields of the entry and of the run
    log mapping stand as the remaining read sources, as the
    act has always read them. Where no source states a count,
    the pair stands as no count and no source, and the caller
    states that the shortfall limb did not run."""
    manifest = family_manifest
    if manifest is None and isinstance(entry, dict):
        manifest = _first_stored_value(
            entry, ("family_manifest", "manifest"))
    if manifest is None and isinstance(source, dict):
        manifest = _first_stored_value(
            source, ("family_manifest", "manifest"))
    if manifest is not None:
        derived = _manifest_expected_count(manifest, entry)
        if derived is not None:
            return derived, "family manifest replicate plan"
    if isinstance(entry, dict):
        plan = _stored_get(entry, "replicate_plan")
        if plan is not None:
            derived = _plan_expected_count(plan, entry)
            if derived is not None:
                return derived, "entry replicate plan"
        stated = _stored_count(_first_stored_value(
            entry, ("expected_run_count", "expected_runs")))
        if stated is not None:
            return stated, "entry expected count field"
    if isinstance(source, dict):
        stated = _stored_count(_first_stored_value(
            source, ("expected_run_count", "expected_runs")))
        if stated is not None:
            return stated, "run log expected count field"
    return None, None


_AMENDED_VALUE_SETS = (
    ("outcome", ("reported", "not reported")),
    ("confirmation_outcome", ("passed", "failed", "not run")),
    ("gate_failure", (
        "procedure gate", "confirmation gate", "both gates", "none")),
)


def _amended_form_failures(entry):
    """The failures the amended Form 22 fields state on an
    entry, at this act, in the one form the three registry
    acts share. The outcome stands read with the confirmation
    outcome field and the gate failure field and with no
    other reading: where the outcome stands reported, a
    confirmation outcome of failed or not run fails, and a
    gate failure at the procedure gate, at the confirmation
    gate, or at both gates fails; where the outcome does not
    stand reported, neither amended field fails on its
    stated barred values. A value standing in none of its
    field stated set fails in every outcome form. An entry
    for an unranked claim carries the value not ranked in
    its test value, rank, and threshold fields and no other
    value, so a not ranked value in one of those fields
    beside another value in any of them fails. Every value
    stands read in its stored text, in plain, bytes,
    bytearray, memoryview, and single part container dress
    alike, through its stored pairs."""
    failures = []
    if not isinstance(entry, dict):
        return failures
    for field, stated_set in _AMENDED_VALUE_SETS:
        value = _stored_get(entry, field)
        stated_values = [
            item for key, item in dict.items(entry)
            if any(
                text is not None and str.__eq__(text, field)
                for text in _stored_key_texts(key))]
        if any(item is None for item in stated_values):
            # A field standing present with the value None
            # carries a value in no stated set, None standing
            # in none of them, so it fails in every outcome
            # form, as the other two registry acts judge it.
            failures.append(
                "value outside its stated set: " + field)
        elif value is not None and not any(
                _stored_text_eq(value, stated) for stated in stated_set):
            failures.append(
                "value outside its stated set: " + field)
    if _stored_text_eq(_stored_get(entry, "outcome"), "reported"):
        if _stored_text_eq(
                _stored_get(entry, "confirmation_outcome"), "failed"):
            failures.append("confirmation outcome failed")
        if _stored_text_eq(
                _stored_get(entry, "confirmation_outcome"), "not run"):
            failures.append("confirmation outcome not run")
        gate_failure = _stored_get(entry, "gate_failure")
        for stated in ("procedure gate", "confirmation gate", "both gates"):
            if _stored_text_eq(gate_failure, stated):
                failures.append("gate failure: " + stated)
    ranked_fields = [
        _stored_get(entry, field)
        for field in ("test_value", "rank", "threshold")]
    carries_not_ranked = any(
        _stored_text_eq(value, "not ranked") for value in ranked_fields)
    all_not_ranked = all(
        _stored_text_eq(value, "not ranked") for value in ranked_fields)
    if carries_not_ranked and not all_not_ranked:
        failures.append(
            "unranked form incomplete: the test value, rank, and "
            "threshold fields do not all carry not ranked")
    return failures


def compare_registry_against_run_log(entry, run_log=None,
                                     retained_records=None,
                                     family_manifest=None):
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
    whether it passed, and it names the claim it judges in its
    claim identifier field, on every return form. With no run
    log among the inputs, no comparison stands performed and
    none stands passed. The comparison runs in both
    directions: every bearing run must appear in the entry,
    and every run the entry itself states must stand in the
    log, named in the result where it stands absent, so a
    comparison over an empty log does not pass an entry that
    states runs. The bearing runs that stand failed stand
    named in the result, while standing in the log as Form 22
    item 4 states. The amended Form 22 fields stand read at
    this act in the form _amended_form_failures states.

    The expected run count stands derived from the family
    record replicate plan as sealed in the FamilyManifest,
    handed as the family manifest argument, carried on the
    entry, or carried on the run log mapping, with the stated
    expected count fields of the entry and of the run log
    mapping as the remaining read sources. The retained count
    the shortfall is judged against is the count of bearing
    records only, the same membership the bearing list states,
    pilot records and records bearing on no claim of the entry
    standing outside it. A shortfall of retained records
    against the expected count fails the comparison under the
    name EXPECTED-RUN-SHORTFALL, as Form 22 item 5 states.
    Where no source states an expected count, the result
    states that the shortfall limb did not run, in its
    shortfall limb performed and shortfall status fields, so
    its absence never reads as a pass of that limb."""
    claim_id = None
    if isinstance(entry, dict):
        claim_raw = _first_stored_value(
            entry, ("claim_identifier", "claim_id"))
        if claim_raw is not None:
            claim_id = _result_field_value(claim_raw)
    if not isinstance(entry, dict):
        return {
            "performed": False,
            "passed": False,
            "checker_module": "MOD-13",
            "compared_against_run_log": False,
            "claim_identifier": claim_id,
            "bearing_run_identifiers": [],
            "missing_run_identifiers": [],
            "excluded_pilot_run_identifiers": [],
            "entry_run_identifiers": [],
            "absent_from_log_run_identifiers": [],
            "failed_run_identifiers": [],
            "shortfall_limb_performed": False,
            "shortfall_status": (
                "not run: the registry entry stands in no record "
                "form, and no comparison stands performed on it"),
        }
    source = retained_records if retained_records is not None else run_log
    if source is None:
        source = _stored_get(entry, "run_log")
    records = _run_log_records(source)
    if records is None:
        return {
            "performed": False,
            "passed": False,
            "checker_module": "MOD-13",
            "compared_against_run_log": False,
            "claim_identifier": claim_id,
            "bearing_run_identifiers": [],
            "missing_run_identifiers": [],
            "excluded_pilot_run_identifiers": [],
            "entry_run_identifiers": _entry_run_identifiers(entry),
            "absent_from_log_run_identifiers": [],
            "failed_run_identifiers": [],
            "shortfall_limb_performed": False,
            "shortfall_status": "not run: no run log stands handed",
        }
    entry_ids = _entry_run_identifiers(entry)
    bearing = []
    excluded_pilot = []
    failed = []
    for record in records:
        run_id = _norm_identifier(_first_stored_value(
            record, ("run_identifier", "run_id")))
        if _record_is_pilot(record):
            excluded_pilot.append(run_id)
            continue
        if not _record_bears_on_entry(record, entry):
            continue
        bearing.append(run_id)
        if _record_status_failed(record):
            failed.append(run_id)
    missing = [
        run_id for run_id in bearing
        if run_id is None or not any(
            _identifiers_agree(run_id, entry_id) for entry_id in entry_ids)]
    absent = [
        entry_id for entry_id in entry_ids
        if not any(
            _identifiers_agree(entry_id, run_id) for run_id in bearing)]
    amended_failures = _amended_form_failures(entry)
    result = {
        "performed": True,
        "passed": not missing and not absent and not amended_failures,
        "checker_module": "MOD-13",
        "compared_against_run_log": True,
        "claim_identifier": claim_id,
        "bearing_run_identifiers": bearing,
        "missing_run_identifiers": missing,
        "excluded_pilot_run_identifiers": excluded_pilot,
        "entry_run_identifiers": entry_ids,
        "absent_from_log_run_identifiers": absent,
        "failed_run_identifiers": failed,
    }
    if amended_failures:
        result["amended_form_failures"] = amended_failures
    confirmation_outcome = _stored_get(entry, "confirmation_outcome")
    if confirmation_outcome is not None:
        result["confirmation_outcome"] = _result_field_value(
            confirmation_outcome)
    gate_failure = _stored_get(entry, "gate_failure")
    if gate_failure is not None:
        result["gate_failure"] = _result_field_value(gate_failure)
    expected, expected_source = _expected_count_and_source(
        entry, source, family_manifest)
    if expected is not None:
        retained_count = len(bearing)
        result["shortfall_limb_performed"] = True
        result["expected_count_source"] = expected_source
        result["expected_run_count"] = expected
        result["retained_run_count"] = retained_count
        if retained_count < expected:
            result["passed"] = False
            result["shortfall_name"] = "EXPECTED-RUN-SHORTFALL"
            result["shortfall"] = expected - retained_count
    else:
        result["shortfall_limb_performed"] = False
        result["expected_count_source"] = None
        result["shortfall_status"] = (
            "not run: no expected run count stands stated in a "
            "read source")
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
    stored_form = _base_sequence_items(form)
    if any(_base_str_eq(item, "horizon") for item in stored_form):
        return False
    daily = daily_aggregate_form()
    if _base_sequence_length(form) != len(daily):
        return False
    return all(
        _base_str_eq(stored_item, daily_item)
        for stored_item, daily_item in zip(stored_form, daily))


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
    "rerun_reading_validation_failures",
    "extend_history",
    "compare_registry_against_run_log",
    "daily_aggregate_form",
    "validate_aggregate_form",
]

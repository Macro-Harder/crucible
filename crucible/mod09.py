"""MOD-09. Attacker Seat.

The attacker strategies exercised in a run, drawn from the fixed
strategy class for that run, and the search ladder position of the
run as a run record input. The seat builds the seat mechanism and
the ladder carriage, and invents no rung list the brief does not
enumerate: the ladder stands enumerated only at the stopping rule
level, rung 6 completion as the readout point and the zero attacker
control at rung 0, carried as item INV-5 and battery check A-01.

Every quantity in this module stands in simulated units only, as a
test value only under DQ-162 as ruled by Captain JP. No field in
any record of this module holds a real money value, and no branch
of this module encodes any real money stake behaviour.

Open standings carried in this module, by name. OP-11 stands open:
the strategy catalogue gap stands carried open in the same
catalogue record the Society Generator delivers, and this module
names no strategy identifier beyond the catalogue identifiers a
run record itself supplies and the one named strategy the plan
names for this seat, the conditional briber. DQ7-10 stands open:
no materiality bound stands fixed in this module, and no readout
is reported as established under stopping condition 2 while that
bound stands unfixed. The consolidated R20 duty stands checked at
test group TG-08.2 only: the coverage sentence form, the search
record field list, and the no failure sentence form stand carried
in this module in the forms the plan states for them.
"""

import copy
import math
from decimal import Decimal
from fractions import Fraction

from crucible import mod03 as _mod03

__all__ = [
    "BOND_PARAMETERS",
    "CATALOGUE_STANDING",
    "COVERAGE_SENTENCE",
    "HOSTILE_INPUT_KINDS",
    "LADDER_STANDING",
    "NAMED_STRATEGIES",
    "NO_FAILURE_SENTENCE",
    "OP11_GAPS",
    "READOUT_POINT_RUNG",
    "RUNG_ZERO_CONTROL",
    "SEARCH_RECORD_FIELDS",
    "SELFISH_MINING_CASE",
    "SELFISH_MINING_STANDINGS",
    "UNITS",
    "AttackerSeat",
    "NamedAttackerFailure",
    "attacker_cost_summary",
    "attacker_payoff",
    "bond_search",
    "build_search_record",
    "catalogue_gaps",
    "conditional_briber_strategy",
    "make_strategy",
    "mod03_catalogue_record",
    "readout",
    "run_record_carriage",
    "run_search",
    "search",
    "search_record_covers_hostile_kinds",
    "stopping_rule_state",
    "strategy_catalogue",
    "sweep_external_profit",
    "validate_search_record",
    "witness_carriage",
]

UNITS = "simulated units only, test value only under DQ-162"

CATALOGUE_STANDING = _mod03.CATALOGUE_STANDING

OP11_GAPS = _mod03.OP11_GAPS

LADDER_STANDING = (
    "enumerated only at the stopping rule level: rung 6 "
    "completion, and the zero attacker control at rung 0"
)

READOUT_POINT_RUNG = 6

RUNG_ZERO_CONTROL = {
    "rung": 0,
    "control": "zero attacker control",
    "carriage": ("item INV-5", "battery check A-01"),
}

NAMED_STRATEGIES = ("conditional briber",)

SELFISH_MINING_CASE = {
    "fixture": "F-26",
    "case": "selfish mining",
    "use": "strategy search point only",
    "deployed_failure_case": False,
}

SELFISH_MINING_STANDINGS = (
    "inside its model, attackers below 25 percent can still gain "
    "under a proposed countermeasure",
    "with propagation delay modelled the threshold vanishes",
)

HOSTILE_INPUT_KINDS = (
    "junk share",
    "veto and hostage behaviour",
    "stalls and abandonment",
    "duplicate rates",
    "oversize rates",
    "rush rates",
    "cost error in both directions",
    "question rounds",
    "pause use to the cap in force",
)

SEARCH_RECORD_FIELDS = (
    "search budget",
    "points tried",
    "neighbourhood definition and step sizes",
    "starting points",
    "order of search",
    "per point outcome",
    "every adaptation",
)

COVERAGE_SENTENCE = (
    "Coverage: this readout reports the attacker search over the "
    "fixed strategy class and the search points the search record "
    "names, and over no wider class."
)

NO_FAILURE_SENTENCE = (
    "The search found no failure at the points the search record "
    "names."
)

BOND_PARAMETERS = (
    "lien multiplier",
    "lien floor",
    "cost rule prices",
)


class NamedAttackerFailure(Exception):
    """An attacker seat failure stated by name."""


def _stands_numeric(value):
    """Return whether a value stands in numeric form, a boolean
    standing in no numeric form for this module."""
    return isinstance(value, (int, float)) and not isinstance(
        value, bool)


def _base_dict_get(mapping, key, default=None):
    """Return the value a handed mapping stores under a key,
    read through its stored pairs, never through a get reading
    the mapping itself supplies and never through a hash or
    equality reading a stored key supplies, so a stored key
    stands matched on the form it stores through the stored
    match and stored equality readings of this module. A
    handed value in no mapping form stores nothing under any
    key."""
    if isinstance(mapping, dict):
        for stored_key, item in dict.items(mapping):
            if _stored_match(stored_key, key) and _stored_eq(
                    stored_key, key):
                return item
    return default


def _base_dict_contains(mapping, key):
    """Return whether a handed mapping stores a key, read
    through its stored pairs, never through a contains reading
    the mapping itself supplies and never through a hash or
    equality reading a stored key supplies, a stored key
    standing matched on the form it stores through the stored
    match and stored equality readings of this module."""
    if isinstance(mapping, dict):
        return any(
            _stored_match(stored_key, key) and _stored_eq(
                stored_key, key)
            for stored_key in dict.keys(mapping))
    return False


def _base_length(value):
    """Return the length a handed container or text value
    stores, read through the base length of its form, never
    through a length reading the value itself supplies."""
    if isinstance(value, str):
        return str.__len__(value)
    if isinstance(value, list):
        return list.__len__(value)
    if isinstance(value, tuple):
        return tuple.__len__(value)
    if isinstance(value, dict):
        return dict.__len__(value)
    if isinstance(value, frozenset):
        return frozenset.__len__(value)
    if isinstance(value, set):
        return set.__len__(value)
    if isinstance(value, bytes):
        return bytes.__len__(value)
    if isinstance(value, bytearray):
        return bytearray.__len__(value)
    if isinstance(value, memoryview):
        return memoryview.__len__(value)
    return len(value)


def _base_items(value):
    """Read the stored items of a handed list or tuple through
    its base class iteration, never through an iteration the
    value itself supplies. A value in no such form stores no
    items."""
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, list):
        return list(list.__iter__(value))
    return []


def _plain_number(value):
    """A numeric value as the plain number it stores, read
    through the base class reading of its own form, never
    through a reading the value itself supplies."""
    if isinstance(value, int):
        return int.__int__(value)
    if isinstance(value, float):
        return float.__float__(value)
    return complex.__complex__(value)


def _base_value_eq(first, second):
    """Whether two handed values in no text form stand equal on
    their stored forms alone: a boolean by identity, a number
    by the plain number it stores, judged through the plain
    equality of two plain numbers, a list or a tuple by its
    stored parts in order, a set or a frozenset by its stored
    parts in any order, a mapping by its stored pairs, and
    every other value by identity, so no equality reading a
    value itself supplies is ever consulted, and no such
    reading can raise out of the judgement."""
    if isinstance(first, bool) or isinstance(second, bool):
        return first is second
    if isinstance(first, (int, float, complex)) and isinstance(
            second, (int, float, complex)):
        result = _plain_number(first) == _plain_number(second)
        return result is True
    if (isinstance(first, list) and isinstance(second, list)) or (
            isinstance(first, tuple)
            and isinstance(second, tuple)):
        first_parts = _base_items(first)
        second_parts = _base_items(second)
        return len(first_parts) == len(second_parts) and all(
            _stored_match(part, other) and _stored_eq(part, other)
            for part, other in zip(first_parts, second_parts))
    if isinstance(first, (set, frozenset)) and isinstance(
            second, (set, frozenset)):
        remaining = _base_sequence(second)
        if len(_base_sequence(first)) != len(remaining):
            return False
        for part in _base_sequence(first):
            hit = None
            for index, candidate in enumerate(remaining):
                if _stored_match(part, candidate) and _stored_eq(
                        part, candidate):
                    hit = index
                    break
            if hit is None:
                return False
            remaining.pop(hit)
        return True
    if isinstance(first, dict) and isinstance(second, dict):
        first_items = list(dict.items(first))
        remaining = list(dict.items(second))
        if len(first_items) != len(remaining):
            return False
        for key, value in first_items:
            hit = None
            for index, (other_key, other_value) in enumerate(
                    remaining):
                if _stored_match(key, other_key) and _stored_eq(
                        key, other_key) and _stored_match(
                        value, other_value) and _stored_eq(
                        value, other_value):
                    hit = index
                    break
            if hit is None:
                return False
            remaining.pop(hit)
        return True
    return first is second


def _stored_match(first, second):
    """Judge two stored values: text values by their stored
    characters through the base string equality, any other pair
    on its stored forms through the base value equality of this
    module, never through an equality reading either value
    itself supplies."""
    if isinstance(first, str) or isinstance(second, str):
        if not (isinstance(first, str) and isinstance(second, str)):
            return False
        result = str.__eq__(first, second)
        return result if result is not NotImplemented else False
    if isinstance(first, (bytes, bytearray, memoryview)) \
            and isinstance(second, (bytes, bytearray, memoryview)):
        return bytes(first) == bytes(second)
    return _base_value_eq(first, second)


def _base_sequence(value):
    """The stored parts of a handed sequence, read through the
    base iteration of its form, as a list of stored parts, text
    parts standing as the plain text they store. A value in no
    sequence form stands as no parts."""
    if isinstance(value, list):
        parts = list.__iter__(value)
    elif isinstance(value, tuple):
        parts = tuple.__iter__(value)
    elif isinstance(value, frozenset):
        parts = frozenset.__iter__(value)
    elif isinstance(value, set):
        parts = set.__iter__(value)
    else:
        return []
    return [
        str.__str__(part) if isinstance(part, str)
        else bytes(part) if isinstance(part, bytes)
        else part
        for part in parts]


def _stored_eq(first, second):
    """Whether two handed values stand equal on their stored
    forms: text values on the text they store, read through
    the base string form, and every other value on its own
    base equality."""
    if isinstance(first, str) and isinstance(second, str):
        return str.__eq__(
            str.__str__(first), str.__str__(second)) is True
    if isinstance(first, (bytes, bytearray, memoryview)) \
            and isinstance(second, (bytes, bytearray, memoryview)):
        return bytes(first) == bytes(second)
    return _base_value_eq(first, second)


def _base_contains(container, item):
    """Whether a handed container stores an item, judged on its
    stored contents: a mapping by its base contains, a list,
    tuple, set, or text value by its stored parts read through
    base class readings, each stored part judged by both stored
    equality forms of this module, the stored match and the
    stored equality, so a part stands contained only where both
    forms judge it equal, never through a contains, iteration,
    or equality reading the container or a part itself
    supplies."""
    if isinstance(container, dict):
        return dict.__contains__(container, item)
    if isinstance(container, (list, tuple)):
        return any(
            _stored_match(part, item) and _stored_eq(part, item)
            for part in _base_items(container))
    if isinstance(container, frozenset):
        return any(
            _stored_match(part, item) and _stored_eq(part, item)
            for part in frozenset.__iter__(container))
    if isinstance(container, set):
        return any(
            _stored_match(part, item) and _stored_eq(part, item)
            for part in set.__iter__(container))
    if isinstance(container, str):
        if not isinstance(item, str):
            return False
        return str.__contains__(container, item)
    return False


def _stored_truthy(value):
    """Whether a stored value stands truthy, judged on what it
    stores: containers and text by their base class length, a
    boolean by itself, a number by standing apart from zero
    on the plain number it stores, read through the plain
    number reading of this module and never through an
    inequality reading the value itself supplies, and any
    other stored value by standing apart from None."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, (str, list, tuple, dict, set, frozenset,
                          bytes, bytearray, memoryview)):
        return _base_length(value) > 0
    if isinstance(value, (int, float, complex)):
        return _plain_number(value) != 0
    return True


def _stored_strip_blank(value):
    """Whether a handed text value stores only blank space,
    judged on the text it stores through the base string form
    and the base strip, never through a strip reading the
    value itself supplies."""
    if isinstance(value, str):
        return not str.strip(str.__str__(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return not bytes.strip(bytes(value))
    return False


def _stored_copy(value, _memo=None):
    """A copy of a handed value built from its stored contents
    only: dict parts through the base dict items reading, list,
    tuple, set, and frozenset parts through their base iteration
    readings, and text parts through the base string form, so
    no copy protocol a part supplies is ever honoured and no
    reading a part itself supplies directs the copy. The buffer
    forms stand carried as stored: a bytearray as a fresh
    bytearray and a memoryview as a memoryview over fresh bytes.
    A dict assignment whose key hash or equality reading raises
    one of the seven named kinds (TypeError, RuntimeError,
    ValueError, AttributeError, OverflowError, KeyError, and
    OSError) at the assignment itself stands carried under a
    distinct numbered form, a plain text numbered form where a
    form carrying the key itself cannot stand inserted, in the
    MOD-14 cured form, so no carried entry is silently dropped
    on that reading and no bare error of those kinds escapes
    the copy. A part
    in no container form and no buffer form stands copied
    as itself."""
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
            try:
                copied[copied_key] = copied_item
            except (TypeError, RuntimeError, ValueError,
                    AttributeError, OverflowError, KeyError,
                    OSError):
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
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
                        candidate_taken = False
                    if candidate_taken:
                        counter += 1
                        continue
                    try:
                        copied[candidate] = copied_item
                        break
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
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
        except (TypeError, RuntimeError, ValueError,
                AttributeError, OverflowError, KeyError,
                OSError):
            return parts
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    return value


def _carry_text(value):
    """A text value as the plain text it stores, and any other
    value as itself, for carriage in a built record."""
    if isinstance(value, str):
        return str.__str__(value)
    return value


def mod03_catalogue_record(records=None):
    """Return the catalogue record the Society Generator delivers."""
    return _mod03.catalogue_record(records)


def catalogue_gaps():
    """The OP-11 gaps, carried open by name, from their single
    owner in MOD-03."""
    return tuple(_mod03.catalogue_gaps())


def _catalogue_repr(name, _depth=0, _seen=None):
    """Return a content derived representation of one identifier
    in a container form, built from the stored parts alone. A
    set or frozenset part stands represented by the sorted
    representations of its stored parts, so the representation
    stands the same at every hash seed, where the printed form
    of the set itself prints its parts in iteration order. A
    tuple or list part stands represented by the representations
    of its stored parts in stored order, so a frozenset carried
    inside a tuple carries its seed stable form with it. A dict
    part stands represented by the representations of its stored
    pairs, sorted on the rendered pair forms, so the
    representation stands the same at every hash seed and two
    dict parts whose stored pairs differ stand represented
    apart. A text
    part stands represented by the plain text it stores, a
    bytes form part by the plain bytes it stores, and a plain
    scalar part by the plain scalar it stores, each read through
    the base class reading of its kind. Every other part stands
    represented by its kind name and the stored contents it
    carries in its own stored mapping, read part by part
    through this same reading, never by a representation
    reading the part itself supplies, so two parts whose kind
    name and stored contents tie still tie here, and no order
    rule for such tied parts stands stated by this act. The
    walk stands bounded at a depth of 100, in the form the
    neighbouring stored readings state for this shape, and
    stands guarded against cycles: a part standing past that
    depth, or standing again on its own walk path, stands
    represented by its kind name alone."""
    if _depth > 100:
        return type(name).__name__
    if isinstance(name, (set, frozenset)):
        if _seen is not None and id(name) in _seen:
            return type(name).__name__
        seen = (_seen or frozenset()) | {id(name)}
        parts = sorted(
            _catalogue_repr(part, _depth + 1, seen) for part in (
                set.__iter__(name) if isinstance(name, set)
                else frozenset.__iter__(name)))
        return "%s({%s})" % (type(name).__name__, ", ".join(parts))
    if isinstance(name, tuple):
        if _seen is not None and id(name) in _seen:
            return type(name).__name__
        seen = (_seen or frozenset()) | {id(name)}
        parts = [
            _catalogue_repr(part, _depth + 1, seen)
            for part in tuple.__iter__(name)]
        return "(%s%s)" % (
            ", ".join(parts), "," if len(parts) == 1 else "")
    if isinstance(name, list):
        if _seen is not None and id(name) in _seen:
            return type(name).__name__
        seen = (_seen or frozenset()) | {id(name)}
        return "[%s]" % ", ".join(
            _catalogue_repr(part, _depth + 1, seen)
            for part in list.__iter__(name))
    if isinstance(name, dict):
        if _seen is not None and id(name) in _seen:
            return type(name).__name__
        seen = (_seen or frozenset()) | {id(name)}
        rendered = [
            (_catalogue_repr(key, _depth + 1, seen),
             _catalogue_repr(item, _depth + 1, seen))
            for key, item in list(dict.items(name))]
        parts = [
            "%s=%s" % pair for pair in sorted(rendered)]
        return "%s({%s})" % (
            type(name).__name__, ", ".join(parts))
    if isinstance(name, str):
        return repr(str.__str__(name))
    if isinstance(name, (bytes, bytearray, memoryview)):
        return repr(bytes(name))
    if isinstance(name, bool):
        return repr(name)
    if isinstance(name, int):
        return repr(int.__int__(name))
    if isinstance(name, float):
        return repr(float.__float__(name))
    if isinstance(name, complex):
        return repr(complex.__complex__(name))
    try:
        stored = vars(name)
    except TypeError:
        stored = None
    if isinstance(stored, dict):
        if _seen is not None and id(name) in _seen:
            return type(name).__name__
        seen = (_seen or frozenset()) | {id(name)}
        rendered = [
            (str.__str__(key) if isinstance(key, str)
             else _catalogue_repr(key, _depth + 1, seen),
             _catalogue_repr(item, _depth + 1, seen))
            for key, item in list(dict.items(stored))]
        parts = [
            "%s=%s" % pair
            for pair in sorted(rendered, key=lambda pair: pair[0])]
        return "%s(%s)" % (type(name).__name__, ", ".join(parts))
    return type(name).__name__


def _catalogue_order_key(name):
    """Return the stated order key for one identifier of an
    unordered identifier container. A text identifier stands
    ordered by its stored text, read character by character
    through the base string reading so a reading the identifier
    itself supplies directs nothing. A bytes form identifier
    stands ordered after text identifiers, by the text its
    stored bytes decode to, by its kind name, and by its raw
    stored bytes as the tie break. Every other identifier stands
    ordered last, by its kind name and its content derived
    representation under _catalogue_repr, which stands the same
    at every hash seed for an identifier in a container form."""
    if isinstance(name, str):
        return (0, "".join(
            str.__getitem__(name, index)
            for index in range(str.__len__(name))), "")
    if isinstance(name, (bytes, bytearray, memoryview)):
        # The decoded text alone does not order this group:
        # distinct stored bytes that decode, with undecodable
        # bytes dropped, to the same text would tie on it and
        # fall back to the iteration order of the handed set,
        # which the hash seed governs. The raw stored bytes
        # stand as the tie break after the decoded text, in the
        # form of the sibling cure at MOD-03, so two identifiers
        # of this group tie only where their stored bytes stand
        # identical as well.
        return (1, bytes(name).decode("utf-8", "ignore"),
                type(name).__name__, bytes(name))
    return (2, type(name).__name__, _catalogue_repr(name))


def strategy_catalogue(extra_identifiers=None):
    """The strategy catalogue standing for this seat.

    Strategy identifiers stand drawn from the catalogue record the
    Society Generator delivers under OP-11, from identifiers a run
    record itself supplies, and from the one named strategy of this
    seat. No other identifier is invented here. Identifiers handed
    in an unordered container, a set or a frozenset, stand appended
    in the stated content derived order of _catalogue_order_key,
    so the same identifier content gives the same catalogue order
    at every hash seed. Identifiers handed in an ordered container
    stand appended in the order handed, read through the base
    iteration of the container form, never through an iteration
    reading the container itself supplies, and identifiers handed
    as one bare text or buffer value stand as the one identifier
    handed, never read character by character. Whether an identifier
    already stands listed stands judged through _base_contains
    on the stored forms of the listed identifiers, as every
    other membership judgement of this module stands judged,
    never through an equality reading a handed identifier
    itself supplies.
    """
    identifiers = list(NAMED_STRATEGIES)
    record = mod03_catalogue_record()
    if isinstance(record, dict):
        for entry in record.get("entries", []):
            if isinstance(entry, dict) and entry.get(
                    "archetype_id") is not None:
                name = entry["archetype_id"]
                if not _base_contains(identifiers, name):
                    identifiers.append(name)
    if extra_identifiers is None:
        extras = []
    elif isinstance(extra_identifiers, (str, bytes, bytearray,
                                        memoryview)):
        extras = [extra_identifiers]
    elif isinstance(extra_identifiers, (set, frozenset)):
        extras = sorted(
            _base_sequence(extra_identifiers),
            key=_catalogue_order_key)
    elif isinstance(extra_identifiers, (list, tuple)):
        extras = _base_items(extra_identifiers)
    else:
        extras = []
    for name in extras:
        if not _base_contains(identifiers, name):
            identifiers.append(name)
    return {
        "identifiers": identifiers,
        "standing": CATALOGUE_STANDING,
        "gaps": list(catalogue_gaps()),
        "source": "the catalogue record under OP-11",
    }


def make_strategy(identifier, in_protocol_payoff=0,
                  external_profit_range=None, parameters=None):
    """State one attacker strategy record.

    Each strategy carries an external profit parameter, in
    simulated units only, swept over a stated range as a labelled
    assumption, representing profit the attacker can obtain
    outside the simulated system. The parameter stands as a swept
    range, never as a declared value supplied by the evaluated
    party or by the strategy author.
    """
    stored_range = _base_sequence(external_profit_range)
    return {
        "strategy_identifier": identifier,
        "in_protocol_payoff": in_protocol_payoff,
        "external_profit_range": stored_range if stored_range else [0],
        "external_profit_standing": (
            "swept parameter, labelled assumption, " + UNITS),
        "external_profit_declared_by": None,
        "parameters": _stored_copy(
            parameters if _stored_truthy(parameters) else {}),
        "units": UNITS,
    }


def conditional_briber_strategy(in_protocol_payoff=0,
                                external_profit_range=None):
    """The conditional briber, the one named strategy of this seat.

    It pays a bribed party only on a stated losing outcome and
    reimburses collaborators on failure, in the P plus epsilon
    form.
    """
    strategy = make_strategy(
        "conditional briber",
        in_protocol_payoff=in_protocol_payoff,
        external_profit_range=external_profit_range,
        parameters={
            "pays_on": "a stated losing outcome only",
            "on_failure": "reimburses collaborators",
            "form": "P plus epsilon",
        },
    )
    strategy["named_strategy"] = True
    return strategy


def attacker_payoff(strategy, external_profit_value):
    """An attacker payoff: its in protocol payoff plus its
    external profit parameter, in simulated units only. A strategy
    standing in no record form, or carrying no numeric in protocol
    payoff, fails by name in this module failure form."""
    if not isinstance(strategy, dict) or (
            not _base_dict_contains(strategy, "in_protocol_payoff")):
        raise NamedAttackerFailure(
            "attacker payoff rejected: the strategy stands in no "
            "record form carrying an in protocol payoff"
        )
    in_protocol = _base_dict_get(strategy, "in_protocol_payoff")
    if isinstance(in_protocol, bool) or not isinstance(
            in_protocol, (int, float)):
        raise NamedAttackerFailure(
            "attacker payoff rejected: the in protocol payoff "
            "stands in no numeric form: "
            + _stored_form_repr(in_protocol)
        )
    if isinstance(external_profit_value, bool) or not isinstance(
            external_profit_value, (int, float)):
        raise NamedAttackerFailure(
            "attacker payoff rejected: the external profit value "
            "stands in no numeric form: "
            + _stored_form_repr(external_profit_value)
        )
    if not math.isfinite(in_protocol) or not math.isfinite(
            external_profit_value):
        raise NamedAttackerFailure(
            "attacker payoff rejected: a payoff part stands in no "
            "finite numeric form: in protocol "
            + _stored_form_repr(in_protocol) + ", external "
            + _stored_form_repr(external_profit_value)
        )
    return _plain_number(in_protocol) + _plain_number(
        external_profit_value)


def _stored_form_repr(value):
    """Render a handed value for a refusal sentence on the form
    it stands in, through the content derived representation of
    this module, which reads every part on the stored form it
    carries, never through a repr or string reading the value
    itself supplies, so the sentence names the handed value on
    its stored form and no reading it supplies can misname it
    or raise out of the sentence."""
    return _catalogue_repr(value)


def _safe_repr(value):
    """Render a handed value for a refusal sentence: through
    its repr reading where that reading stands, and through
    the base object repr where the repr reading the value
    itself supplies raises one of the seven named kinds
    (TypeError, RuntimeError, ValueError, AttributeError,
    OverflowError, KeyError, OSError), so the sentence stands
    delivered whole and never escapes bare on a reading that
    raises one of those seven named kinds."""
    try:
        return repr(value)
    except (TypeError, RuntimeError, ValueError, AttributeError,
            OverflowError, KeyError, OSError):
        return object.__repr__(value)


def _safe_str(value):
    """Render a handed value for a refusal sentence: through
    its string reading where that reading stands, and through
    the base object repr where the string reading the value
    itself supplies raises TypeError, RuntimeError, ValueError,
    AttributeError, OverflowError, KeyError, or OSError, so
    the sentence stands delivered whole on those kinds."""
    try:
        return str(value)
    except (TypeError, RuntimeError, ValueError, AttributeError,
            OverflowError, KeyError, OSError):
        return object.__repr__(value)


def _render_safe_copy(value, _depth=0, _seen=None):
    """A copy of a handed value whose every part stands safe
    to render: container parts copied part by part through
    this same reading, a text part as the plain text it
    stores, a buffer part in its own buffer form, and every
    other part as itself where its repr reading stands, or
    as its base object repr text where that reading raises
    TypeError, RuntimeError, ValueError, AttributeError,
    OverflowError, KeyError, or OSError. A dict entry whose
    rendered key hash or equality reading raises one of those
    seven kinds at the construction itself stands carried
    under a distinct numbered form, in the form the stored
    copy of this module states, so no carried entry is
    silently dropped on that reading, and a set or frozenset
    whose rendered part raises one of those kinds at the
    construction stands carried whole in list form, in the
    cured pole list form of this module family. A part
    standing past a depth of 100, or standing again on its own
    copy path, stands as its base object repr text."""
    if isinstance(value, dict):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return object.__repr__(value)
        seen = (_seen or frozenset()) | {id(value)}
        copied = {}
        for key, item in list(dict.items(value)):
            copied_key = _render_safe_copy(key, _depth + 1, seen)
            copied_item = _render_safe_copy(item, _depth + 1, seen)
            try:
                copied[copied_key] = copied_item
            except (TypeError, RuntimeError, ValueError,
                    AttributeError, OverflowError, KeyError,
                    OSError):
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
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
                        candidate_taken = False
                    if candidate_taken:
                        counter += 1
                        continue
                    try:
                        copied[candidate] = copied_item
                        break
                    except (TypeError, RuntimeError, ValueError,
                            AttributeError, OverflowError, KeyError,
                            OSError):
                        counter += 1
        return copied
    if isinstance(value, list):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return object.__repr__(value)
        seen = (_seen or frozenset()) | {id(value)}
        return [
            _render_safe_copy(item, _depth + 1, seen)
            for item in list.__iter__(value)]
    if isinstance(value, tuple):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return object.__repr__(value)
        seen = (_seen or frozenset()) | {id(value)}
        return tuple(
            _render_safe_copy(item, _depth + 1, seen)
            for item in tuple.__iter__(value))
    if isinstance(value, (set, frozenset)):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return object.__repr__(value)
        seen = (_seen or frozenset()) | {id(value)}
        parts = [
            _render_safe_copy(item, _depth + 1, seen)
            for item in (
                set.__iter__(value) if isinstance(value, set)
                else frozenset.__iter__(value))]
        try:
            return set(parts) if isinstance(value, set) else (
                frozenset(parts))
        except (TypeError, RuntimeError, ValueError,
                AttributeError, OverflowError, KeyError, OSError):
            return parts
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    try:
        repr(value)
    except (TypeError, RuntimeError, ValueError, AttributeError,
            OverflowError, KeyError, OSError):
        return object.__repr__(value)
    return value


def sweep_external_profit(strategy, largest_in_protocol_payoff=None):
    """Sweep the external profit parameter over its stated range.

    The stated range includes zero and at least one value above
    the largest in protocol payoff in the run. A strategy whose
    stated range carries no such value stands rejected, because
    its sweep would not cover the range the seat requires.
    """
    if not isinstance(strategy, dict):
        raise NamedAttackerFailure(
            "external profit sweep rejected: the strategy stands "
            "in no record form: " + _stored_form_repr(strategy)
        )
    stated_range = _base_dict_get(
        strategy, "external_profit_range", [])
    if stated_range is None:
        values = []
    elif isinstance(stated_range, (list, tuple)):
        values = _base_sequence(stated_range)
    else:
        raise NamedAttackerFailure(
            "external profit sweep rejected: the stated range "
            "stands in no range form: " + _stored_form_repr(stated_range)
        )
    for value in values:
        if not _stands_numeric(value):
            raise NamedAttackerFailure(
                "external profit sweep rejected: a stated range "
                "value stands in no numeric form: " + _stored_form_repr(value)
            )
    if not any(
            _stored_match(value, 0) and _stored_eq(value, 0)
            for value in values):
        raise NamedAttackerFailure(
            "external profit sweep rejected: the stated range "
            "carries no zero value"
        )
    largest = largest_in_protocol_payoff
    if largest is None:
        largest = _base_dict_get(strategy, "in_protocol_payoff", 0)
    if not _stands_numeric(largest):
        raise NamedAttackerFailure(
            "external profit sweep rejected: the largest in "
            "protocol payoff stands in no numeric form: "
            + _stored_form_repr(largest)
        )
    if not any(
            _plain_number(value) > _plain_number(largest)
            for value in values):
        raise NamedAttackerFailure(
            "external profit sweep rejected: the stated range "
            "carries no value above the largest in protocol payoff"
        )
    return [
        {
            "external_profit_value": value,
            "attacker_payoff": attacker_payoff(strategy, value),
            "standing": (
                "labelled assumption, " + UNITS),
        }
        for value in values
    ]


def run_record_carriage(strategy_class, ladder_position,
                        catalogue_version_or_hash,
                        ladder_definition_pointer,
                        ladder_definition_version, strategies=None):
    """The run record carriage of one search bearing run.

    The record carries the fixed strategy class, the ladder
    position, the catalogue version or hash of the class
    definition in force, and the ladder definition pointer and
    version in force, beside the strategies exercised, each drawn
    from the fixed class.
    """
    if strategy_class is None:
        raise NamedAttackerFailure(
            "run record rejected: no fixed strategy class stands "
            "stated"
        )
    if not isinstance(strategy_class, (list, tuple)):
        raise NamedAttackerFailure(
            "run record rejected: the fixed strategy class stands "
            "in no class list form: " + _stored_form_repr(strategy_class)
        )
    if _base_length(strategy_class) == 0:
        raise NamedAttackerFailure(
            "run record rejected: no fixed strategy class stands "
            "stated"
        )
    if strategies is not None and not isinstance(
            strategies, (list, tuple)):
        raise NamedAttackerFailure(
            "run record rejected: the strategies exercised stand "
            "in no list form: " + _stored_form_repr(strategies)
        )
    if ladder_position is None:
        raise NamedAttackerFailure(
            "run record rejected: no ladder position stands stated"
        )
    if isinstance(ladder_position, bool) or not isinstance(
            ladder_position, int) or _plain_number(
            ladder_position) < 0 or (
            _plain_number(ladder_position) > READOUT_POINT_RUNG):
        raise NamedAttackerFailure(
            "run record rejected: the ladder position stands outside "
            "the whole rungs 0 to 6 of the search ladder: "
            + _stored_form_repr(ladder_position)
        )
    if catalogue_version_or_hash is None or (
            isinstance(
                catalogue_version_or_hash,
                (str, bytes, bytearray, memoryview))
            and _stored_strip_blank(catalogue_version_or_hash)):
        raise NamedAttackerFailure(
            "run record rejected: no catalogue version or hash "
            "stands stated"
        )
    if ladder_definition_pointer is None or (
            ladder_definition_version is None) or (
            isinstance(
                ladder_definition_pointer,
                (str, bytes, bytearray, memoryview))
            and _stored_strip_blank(ladder_definition_pointer)) or (
            isinstance(
                ladder_definition_version,
                (str, bytes, bytearray, memoryview))
            and _stored_strip_blank(ladder_definition_version)):
        raise NamedAttackerFailure(
            "run record rejected: no ladder definition pointer "
            "and version stand stated"
        )
    exercised = []
    for strategy in _base_sequence(strategies):
        name = strategy
        if isinstance(strategy, dict):
            name = dict.get(strategy, "strategy_identifier")
        if not _base_contains(strategy_class, name):
            raise NamedAttackerFailure(
                "strategy outside the fixed class stands rejected: "
                + _stored_form_repr(name)
            )
        exercised.append(_carry_text(name))
    return {
        "strategy_class": _base_sequence(strategy_class),
        "ladder_position": ladder_position,
        "catalogue_version_or_hash": _carry_text(
            catalogue_version_or_hash),
        "ladder_definition_pointer": _carry_text(
            ladder_definition_pointer),
        "ladder_definition_version": _carry_text(
            ladder_definition_version),
        "strategies_exercised": exercised,
        "catalogue_standing": CATALOGUE_STANDING,
        "units": UNITS,
    }


def search_record_validation_failures(record, fixed_class=None):
    failures = []
    if not isinstance(record, dict):
        return ["the search record stands in no record form"]
    missing = object()
    carriage = _base_dict_get(record, "run_record", missing)
    if carriage is missing:
        carriage = record
    if _stored_truthy(_base_dict_get(record, "mid_run_strategies")):
        failures.append(
            "mid_run_strategies stand stated: a strategy stands "
            "introduced mid run")
    try:
        run_record_carriage(
            _base_dict_get(carriage, "strategy_class"),
            _base_dict_get(carriage, "ladder_position"),
            _base_dict_get(carriage, "catalogue_version_or_hash"),
            _base_dict_get(carriage, "ladder_definition_pointer"),
            _base_dict_get(carriage, "ladder_definition_version"),
            strategies=_base_dict_get(
                carriage, "strategies_exercised", []),
        )
    except NamedAttackerFailure as failure:
        failures.append(
            "the run record carriage stands refused: " + str(failure))
    if fixed_class is not None:
        if not isinstance(
                fixed_class, (list, tuple, set, frozenset)):
            failures.append(
                "the fixed class stands in no iterable form")
        else:
            carriage_parts = _base_sequence(
                _base_dict_get(carriage, "strategy_class", []))
            fixed_parts = _base_sequence(fixed_class)
            matched_all = len(carriage_parts) == len(fixed_parts)
            if matched_all:
                remaining = list(fixed_parts)
                for part in carriage_parts:
                    hit = None
                    for index, candidate in enumerate(remaining):
                        if _stored_match(part, candidate) and _stored_eq(
                                part, candidate):
                            hit = index
                            break
                    if hit is None:
                        matched_all = False
                        break
                    remaining.pop(hit)
            if not matched_all:
                failures.append(
                    "the exercised strategy class does not stand as "
                    "the fixed class")
    search = _base_dict_get(record, "search_record", {})
    if not isinstance(search, dict):
        failures.append(
            "the search record field list stands in no record form")
    else:
        for field in SEARCH_RECORD_FIELDS:
            key = field.replace(" ", "_")
            if not _base_dict_contains(search, key) or _base_dict_get(
                    search, key) is None:
                failures.append(
                    "the search record field stands absent: " + field)
            else:
                stored = _base_dict_get(search, key)
                if key != "every_adaptation" and isinstance(
                        stored, (str, list, tuple, dict, set,
                                 frozenset, bytes, bytearray,
                                 memoryview)) and (
                        _base_length(stored) == 0):
                    failures.append(
                        "the search record field stands empty: "
                        + field)
    bond = _base_dict_get(record, "bond_parameter_search")
    if not isinstance(bond, dict):
        if _base_dict_contains(record, "bond_parameter_search"):
            failures.append(
                "the bond parameter search limb stands in no "
                "record form")
        else:
            failures.append(
                "the bond parameter search limb stands absent")
    else:
        if _base_dict_get(bond, "worst_griefing_factor") is None:
            failures.append(
                "the bond parameter search carries no worst "
                "griefing factor")
        if not _stored_truthy(_base_dict_get(bond, "parameter_set")):
            failures.append(
                "the bond parameter search carries no parameter set")
    case_uses = _base_dict_get(record, "case_uses", [])
    if not isinstance(case_uses, (list, tuple)):
        failures.append("case_uses stand in no list form")
    else:
        for use in _base_items(case_uses):
            if not isinstance(use, dict):
                failures.append("a case use stands in no record form")
                break
            fixture = _base_dict_get(use, "fixture")
            use_text = _base_dict_get(use, "use")
            if _stored_match(fixture, "F-26") and _stored_eq(
                    fixture, "F-26") and not (
                    _stored_match(
                        use_text, "strategy search point only")
                    and _stored_eq(
                        use_text, "strategy search point only")):
                failures.append(
                    "the F-26 case stands in a use other than a "
                    "strategy search point")
                break
    return failures


def validate_search_record_with_reason(record, fixed_class=None):
    failures = search_record_validation_failures(record, fixed_class)
    return (not failures, failures)


def validate_search_record(record, fixed_class=None):
    """Check one search record against the seat bars.

    A record fails where a strategy stands introduced mid run,
    where an exercised strategy stands outside the fixed class,
    where the ladder position or the version carriage stands
    absent, where the search record field list stands incomplete,
    where the bond parameter search limb stands absent, or where
    the F-26 case stands in any use other than a search point.
    Every reading of a handed record in this act runs through
    base dict readings, never through a get, contains, or item
    reading the handed record itself supplies, and the hostile
    kind coverage act below reads its handed records the same
    way.
    """
    if not isinstance(record, dict):
        return False
    missing = object()
    carriage = _base_dict_get(record, "run_record", missing)
    if carriage is missing:
        carriage = record
    if _stored_truthy(_base_dict_get(record, "mid_run_strategies")):
        return False
    try:
        run_record_carriage(
            _base_dict_get(carriage, "strategy_class"),
            _base_dict_get(carriage, "ladder_position"),
            _base_dict_get(carriage, "catalogue_version_or_hash"),
            _base_dict_get(carriage, "ladder_definition_pointer"),
            _base_dict_get(carriage, "ladder_definition_version"),
            strategies=_base_dict_get(
                carriage, "strategies_exercised", []),
        )
    except NamedAttackerFailure:
        return False
    if fixed_class is not None:
        if not isinstance(
                fixed_class, (list, tuple, set, frozenset)):
            return False
        carriage_parts = _base_sequence(
            _base_dict_get(carriage, "strategy_class", []))
        fixed_parts = _base_sequence(fixed_class)
        if len(carriage_parts) != len(fixed_parts):
            return False
        remaining = list(fixed_parts)
        for part in carriage_parts:
            matched = None
            for index, candidate in enumerate(remaining):
                if _stored_match(part, candidate) and _stored_eq(
                        part, candidate):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
    search = _base_dict_get(record, "search_record", {})
    if not isinstance(search, dict):
        return False
    for field in SEARCH_RECORD_FIELDS:
        key = field.replace(" ", "_")
        if not _base_dict_contains(search, key) or _base_dict_get(
                search, key) is None:
            return False
        stored = _base_dict_get(search, key)
        if key != "every_adaptation" and isinstance(
                stored, (str, list, tuple, dict, set, frozenset,
                         bytes, bytearray, memoryview)) and (
                _base_length(stored) == 0):
            return False
    bond = _base_dict_get(record, "bond_parameter_search")
    if not isinstance(bond, dict):
        return False
    if _base_dict_get(bond, "worst_griefing_factor") is None or (
            not _stored_truthy(
                _base_dict_get(bond, "parameter_set"))):
        return False
    case_uses = _base_dict_get(record, "case_uses", [])
    if not isinstance(case_uses, (list, tuple)):
        return False
    for use in _base_items(case_uses):
        if not isinstance(use, dict):
            return False
        fixture = _base_dict_get(use, "fixture")
        use_text = _base_dict_get(use, "use")
        if _stored_match(fixture, "F-26") and _stored_eq(
                fixture, "F-26") and not (
                _stored_match(
                    use_text, "strategy search point only")
                and _stored_eq(
                    use_text, "strategy search point only")):
            return False
    return True


def stopping_rule_state(ladder_position):
    """The stopping rule standing at one ladder position.

    The readout point stands at rung 6 completion. A position
    below that point is not a readout point, and no readout at
    such a position is reported as established.
    """
    complete = (
        isinstance(ladder_position, int)
        and not isinstance(ladder_position, bool)
        and _plain_number(ladder_position) == READOUT_POINT_RUNG
    )
    state = {
        "ladder_position": ladder_position,
        "readout_point": complete,
        "established": False,
        "established_bar": (
            "no readout is reported as established under stopping "
            "condition 2 while DQ7-10 stands open"),
    }
    if isinstance(ladder_position, int) and not isinstance(
            ladder_position, bool) and _plain_number(
            ladder_position) == 0:
        state["rung_zero_control"] = copy.deepcopy(RUNG_ZERO_CONTROL)
    return state


def bond_search(parameter_candidates, griefing_evaluator=None):
    """Run one optimisation search over the bond parameter space.

    The search stands above the fixed search ladder, over the lien
    multiplier, the lien floor, and the cost rule prices, each over
    its estimated sweep range as a labelled assumption. It reports
    the worst griefing factor found and the parameter set that
    produced it, in simulated units only. Where no evaluator is
    supplied, the griefing factor of a candidate stands as the
    candidate harm divided by its attacker cost, in the R-09-1
    form the record states, and a candidate with no stated cost
    stands unscored. This search changes no bond parameter from
    its unsettled standing.
    """
    if parameter_candidates is not None and not isinstance(
            parameter_candidates, (list, tuple)):
        raise NamedAttackerFailure(
            "bond parameter search rejected: the candidate set "
            "stands in no candidate list form"
        )
    scored = []
    for candidate in _base_items(parameter_candidates):
        if not isinstance(candidate, dict):
            raise NamedAttackerFailure(
                "bond parameter search rejected: a candidate stands "
                "in no record form: " + _stored_form_repr(candidate)
            )
        params = _base_dict_get(
            candidate, "parameter_set", candidate)
        if griefing_evaluator is not None:
            factor = griefing_evaluator(_stored_copy(params))
        else:
            cost = _base_dict_get(candidate, "attacker_cost")
            harm = _base_dict_get(candidate, "harm")
            if (harm is not None and not _stands_numeric(harm)) or (
                    cost is not None and not _stands_numeric(cost)):
                raise NamedAttackerFailure(
                    "bond parameter search rejected: a candidate "
                    "carries a harm or a cost in no numeric form: "
                    + _stored_form_repr(candidate)
                )
            if cost is None or _plain_number(cost) == 0 or (
                    harm is None):
                continue
            factor = _plain_number(harm) / _plain_number(cost)
        if not _stands_numeric(factor) or not math.isfinite(factor):
            raise NamedAttackerFailure(
                "bond parameter search rejected: a griefing factor "
                "stands in no finite numeric form: "
                + _stored_form_repr(factor)
            )
        scored.append({
            "parameter_set": _stored_copy(params),
            "griefing_factor": _plain_number(factor),
        })
    if not scored:
        raise NamedAttackerFailure(
            "bond parameter search rejected: no scored parameter "
            "set stands in the search"
        )
    worst = max(
        scored,
        key=lambda item: _plain_number(item["griefing_factor"]))
    return {
        "search_kind": (
            "optimisation search above the fixed search ladder"),
        "parameter_space": list(BOND_PARAMETERS),
        "ranges_standing": (
            "estimated sweep ranges, labelled assumptions"),
        "worst_griefing_factor": worst["griefing_factor"],
        "parameter_set": worst["parameter_set"],
        "points_scored": scored,
        "units": UNITS,
        "bond_parameters_changed": False,
    }


def build_search_record(run_carriage, points_tried,
                        per_point_outcome, bond_candidates,
                        griefing_evaluator=None, budget=None,
                        neighbourhood=None, starting_points=None,
                        order_of_search=None, adaptations=None,
                        case_uses=None, mid_run_strategies=None,
                        external_profit_swept_values=None):
    """Assemble one search bearing run record in full.

    The record carries the run record carriage, the R20-B search
    record field list in full, the bond parameter search limb, and
    the case uses of the run, each F-26 use standing as a strategy
    search point only with both C-7 standings carried beside it.
    """
    uses = []
    for use in _base_items(case_uses):
        entry = _stored_copy(use)
        if not isinstance(entry, dict):
            raise NamedAttackerFailure(
                "search record rejected: a case use stands in "
                "no record form: " + _stored_form_repr(entry)
            )
        fixture = _base_dict_get(entry, "fixture")
        if _stored_match(fixture, "F-26") and _stored_eq(
                fixture, "F-26"):
            entry["use"] = "strategy search point only"
            entry["standings_carried"] = list(
                SELFISH_MINING_STANDINGS)
            entry["standings_asserted_as_settled"] = False
            entry["deployed_failure_case"] = False
        uses.append(entry)
    record = {
        "run_record": _stored_copy(run_carriage),
        "search_record": {
            "search_budget": _stored_copy(budget),
            "points_tried": _stored_copy(points_tried),
            "neighbourhood_definition_and_step_sizes": (
                _stored_copy(neighbourhood)),
            "starting_points": _stored_copy(starting_points),
            "order_of_search": _stored_copy(order_of_search),
            "per_point_outcome": _stored_copy(per_point_outcome),
            "every_adaptation": _stored_copy(
                adaptations if adaptations is not None else []),
        },
        "bond_parameter_search": bond_search(
            bond_candidates, griefing_evaluator),
        "case_uses": uses,
        "external_profit_swept_values": [
            _stored_copy(part)
            for part in _base_sequence(external_profit_swept_values)],
        "mid_run_strategies": list(
            _base_sequence(mid_run_strategies)),
        "stopping_rule": stopping_rule_state(
            _base_dict_get(run_carriage, "ladder_position")),
        "units": UNITS,
    }
    if not validate_search_record(record):
        raise NamedAttackerFailure(
            "search record rejected: the assembled record fails "
            "its own seat bars"
        )
    return record


def run_search(run_carriage, points_tried, per_point_outcome,
               bond_candidates, **kwargs):
    """Run the seat search for one run and return its record."""
    return build_search_record(
        run_carriage, points_tried, per_point_outcome,
        bond_candidates, **kwargs)


def search(*args, **kwargs):
    """Alias of run_search, in the suite entry name form."""
    return run_search(*args, **kwargs)


def _wording_claim_text(value, _depth=0, _seen=None):
    """The text a handed wording carries, read on its stored
    form: a text value on the text it stores, a buffer value on
    the text its stored bytes decode to, a list or tuple value
    on the texts its stored parts carry in stored order, a set
    or frozenset value on the texts its stored parts carry in
    sorted text order, so the reading stands the same at every
    hash seed, and a dict value on the texts its stored keys
    and values carry, each part read recursively and joined by
    single spaces. A value in no such form carries no wording
    text. The walk stands bounded at a depth of 100, in the
    form the neighbouring bounded readings of this module
    state, and stands guarded against cycles: a part standing
    past that depth, or standing again on its own walk path,
    carries no wording text at that limb, so no bare
    RecursionError escapes the reading on a deep or cyclic
    wording."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).decode("utf-8", "ignore")
    if isinstance(value, (list, tuple)):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return ""
        seen = (_seen or frozenset()) | {id(value)}
        return " ".join(
            _wording_claim_text(part, _depth + 1, seen)
            for part in _base_items(value))
    if isinstance(value, (set, frozenset)):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return ""
        seen = (_seen or frozenset()) | {id(value)}
        return " ".join(sorted(
            _wording_claim_text(part, _depth + 1, seen)
            for part in _base_sequence(value)))
    if isinstance(value, dict):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return ""
        seen = (_seen or frozenset()) | {id(value)}
        parts = []
        for key, item in list(dict.items(value)):
            parts.append(_wording_claim_text(key, _depth + 1, seen))
            parts.append(
                _wording_claim_text(item, _depth + 1, seen))
        return " ".join(parts)
    return ""


def _normalised_claim_text(value):
    """The wording claim text of a handed wording in normalised
    dress: lower case, with each hyphen standing as a space and
    every run of whitespace standing as one space, so a claim
    phrase stands judged in the dress it was written in."""
    text = str.lower(_wording_claim_text(value))
    return " ".join(text.replace("-", " ").split())


def _outcome_stands_failure(value, _depth=0, _seen=None):
    """Whether a stored per point outcome stands as the failure
    outcome: a text value on the text it stores, a buffer value
    on the bytes it stores, each judged against the failure
    outcome in its own form, a list, tuple, set, or
    frozenset value where any stored part stands as the failure
    outcome on this same reading or where the texts its stored
    parts carry join, in the wording claim reading of this
    module, to the failure outcome text whole, and a dict
    value where any stored key or stored value stands as the
    failure outcome on this same reading or where the texts
    its stored keys and values carry join, in that same
    wording claim reading, to the failure outcome text
    whole. The walk stands bounded at a depth of 100, in the
    form the neighbouring bounded readings of this module
    state, and stands guarded against cycles: a part standing
    past that depth, or standing again on its own walk path,
    stands as no failure at that limb, so no bare
    RecursionError escapes the reading on a deep or cyclic
    outcome."""
    if isinstance(value, str):
        return _stored_eq(value, "failure found")
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value) == b"failure found"
    if isinstance(value, (list, tuple, set, frozenset)):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return False
        seen = (_seen or frozenset()) | {id(value)}
        if any(
                _outcome_stands_failure(part, _depth + 1, seen)
                for part in _base_sequence(value)):
            return True
        return _stored_eq(
            _wording_claim_text(value), "failure found")
    if isinstance(value, dict):
        if _depth > 100 or (
                _seen is not None and id(value) in _seen):
            return False
        seen = (_seen or frozenset()) | {id(value)}
        if any(
                _outcome_stands_failure(key, _depth + 1, seen)
                or _outcome_stands_failure(item, _depth + 1, seen)
                for key, item in list(dict.items(value))):
            return True
        return _stored_eq(
            _wording_claim_text(value), "failure found")
    return False


def _outcome_carries_content(value):
    """Whether a stored outcome value carries any outcome
    content at all, judged on its stored form: no value, a
    boolean standing at False, a number standing at zero, an
    empty text or buffer, and an empty list, tuple, set,
    frozenset, or dict each carry no outcome content, and
    every other stored value carries the content it stores. A
    Decimal and a Fraction each stand judged in their own
    kind at the number limb, a zero in either kind carrying
    no outcome content."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, (int, float, complex)):
        return _plain_number(value) != 0
    if isinstance(value, Decimal):
        return not (Decimal.__eq__(
            Decimal.__new__(Decimal, value), Decimal(0)) is True)
    if isinstance(value, Fraction):
        return not (Fraction.__eq__(
            Fraction.__new__(Fraction, value), Fraction(0)) is True)
    if isinstance(value, (str, bytes, bytearray, memoryview,
                          list, tuple, set, frozenset, dict)):
        return _base_length(value) > 0
    return True


def _stands_point_mapping(entry):
    """Whether a handed dict stands in point mapping form:
    a non empty mapping carrying at least one stored value
    in an outcome bearing form, a record, a text or buffer
    outcome, or a container of outcomes, whose every other
    stored value stands in an outcome bearing form or in a
    plain scalar outcome form, an int, a float, a complex,
    a boolean, or no value, each standing as the outcome a
    point records in scalar dress beside the outcomes under
    its fellow point keys. A dict carrying no outcome
    bearing value at all, as an entry in record form
    carrying a plain scalar beside its keys, stands as an
    entry in record form and not as a point mapping."""
    if not isinstance(entry, dict) or _base_length(entry) == 0:
        return False
    values = list(dict.values(entry))
    if not any(
            isinstance(item, (dict, str, bytes, bytearray,
                              memoryview, list, tuple, set,
                              frozenset))
            for item in values):
        return False
    return all(
        isinstance(item, (dict, str, bytes, bytearray,
                          memoryview, list, tuple, set,
                          frozenset, bool, int, float,
                          complex))
        or item is None
        for item in values)


def _entry_outcome_state(entry):
    """The recorded outcome state of one per point outcome
    entry in record form, as a pair of whether an outcome
    stands recorded and whether it stands as a failure. An
    entry records the outcome its outcome key carries, and an
    entry carrying no outcome key, or an outcome carrying no
    outcome content, records nothing."""
    if not isinstance(entry, dict):
        return (False, False)
    if not _base_dict_contains(entry, "outcome"):
        return (False, False)
    outcome = _base_dict_get(entry, "outcome")
    if not _outcome_carries_content(outcome):
        return (False, False)
    return (True, _outcome_stands_failure(outcome))


def _list_entry_outcome_state(entry):
    """The recorded outcome state of one per point outcome
    entry handed in list carriage, judged in the same form
    the dict carriage walk judges the identical contents. A
    dict entry carrying an outcome key, or carrying any
    stored value in an outcome bearing form under a key
    other than the point key, stands walked whole by
    _recorded_outcome_state, so a failure recorded beside
    the outcome, under a fellow point key, or in a nested
    record stands recorded whatever form a fellow value
    stands in. A dict entry carrying a failure under the
    point key itself beside any fellow key likewise stands
    walked whole, whatever form the fellow value stands
    in, a plain scalar form or a form no routing scan
    lists, so list carriage and dict carriage judge the
    identical contents one way. A dict entry carrying
    neither, and carrying no fellow key beside its point
    key, stands as a record entry alone, judged by
    _entry_outcome_state, so an entry whose point key
    stands alone as the name of its point records nothing
    on that name. An entry in no dict form stands judged
    on its own stored form, recording the content it
    carries and standing as a failure where
    _outcome_stands_failure judges it one."""
    if isinstance(entry, dict):
        keys = list(dict.keys(entry))
        has_point_key = any(
            isinstance(key, str) and str.__eq__(
                str.__str__(key), "point")
            for key in keys)
        has_fellow_key = any(
            not (isinstance(key, str) and str.__eq__(
                str.__str__(key), "point"))
            for key in keys)
        if _base_dict_contains(entry, "outcome") or any(
                isinstance(item, (dict, str, bytes, bytearray,
                                  memoryview, list, tuple, set,
                                  frozenset))
                for key, item in list(dict.items(entry))
                if not (isinstance(key, str) and str.__eq__(
                        str.__str__(key), "point"))) or (
                has_point_key and has_fellow_key):
            return _recorded_outcome_state(entry)
        return _entry_outcome_state(entry)
    return (_outcome_carries_content(entry),
            _outcome_stands_failure(entry))


def _recorded_outcome_state(carriage, _depth=0):
    """The recorded outcome state of a per point outcome handed
    in dict form, as a pair of whether an outcome stands
    recorded and whether a recorded outcome stands as a
    failure. A dict carrying an outcome key stands as one
    outcome entry, judged as _entry_outcome_state judges it,
    and the walk also records what the values under its other
    keys record, those keys standing as point keys beside the
    outcome key. A dict carrying no outcome key stands as a
    point mapping, point names to their outcomes or to their
    own outcome records, and records what its stored values
    record, read recursively under its point keys. The walk
    reads at most sixteen mapping levels; a carriage nested
    deeper records nothing past that depth."""
    if not isinstance(carriage, dict) or _depth > 16:
        return (False, False)
    recorded = False
    failure = False
    if _base_dict_contains(carriage, "outcome"):
        recorded, failure = _entry_outcome_state(carriage)
    for key, item in list(dict.items(carriage)):
        if _base_dict_contains(carriage, "outcome") and (
                isinstance(key, str) and str.__eq__(
                    str.__str__(key), "outcome")):
            continue
        if _base_dict_contains(carriage, "outcome") and (
                isinstance(key, str) and str.__eq__(
                    str.__str__(key), "point")):
            continue
        if isinstance(item, dict):
            item_recorded, item_failure = _recorded_outcome_state(
                item, _depth + 1)
        elif item is None:
            item_recorded, item_failure = (False, False)
        else:
            item_recorded = _outcome_carries_content(item)
            item_failure = _outcome_stands_failure(item)
        recorded = recorded or item_recorded
        failure = failure or item_failure
    return (recorded, failure)


def readout(search_record, found_failure=True, wording="",
            established=False):
    """State one readout reporting an attacker search result.

    The readout unit carries the coverage sentence in the same
    unit as its wording, states no coverage number for the
    confined strategy class, and reports a search that found no
    failure in the no failure sentence form only. A readout called
    established before its stopping conditions stand met, or while
    DQ7-10 stands open, stands rejected. A bond adequacy or
    adjudication robustness readout that ran no conditional
    briber strategy, or that ran with the external profit
    parameter fixed at zero only, stands reported as an in
    protocol result only, never as an economic security result,
    and the unit states its result kind in both cases. The no
    failure sentence stands added only where the search record
    itself records per point outcomes in record form and none
    of them records a failure, whatever the caller's flag
    states: an entry records an outcome only where it carries
    an outcome standing apart from no value, and a per point
    outcome handed in point mapping form stands read under its
    point keys. A wording that carries an established claim or
    an economic security claim stands refused in the same form
    as the established flag, the claim judged on the text the
    wording stores in text, buffer, list, tuple, set, frozenset,
    or dict form, in normalised whitespace and hyphen dress.
    """
    if not isinstance(search_record, dict):
        raise NamedAttackerFailure(
            "readout rejected: no search record stands supplied for "
            "the readout"
        )
    carriage = _base_dict_get(
        search_record, "run_record", search_record)
    if not isinstance(carriage, dict):
        raise NamedAttackerFailure(
            "readout rejected: the run record carriage stands in "
            "no record form: " + _stored_form_repr(carriage)
        )
    position = _base_dict_get(carriage, "ladder_position")
    if established:
        raise NamedAttackerFailure(
            "readout rejected: no readout stands reported as "
            "established while DQ7-10 stands open, and none "
            "before its stopping conditions stand met"
        )
    wording_text = _normalised_claim_text(wording)
    if "established" in wording_text or (
            "economically secure" in wording_text) or (
            "economic security" in wording_text):
        raise NamedAttackerFailure(
            "readout rejected: no readout stands reported as "
            "established while DQ7-10 stands open, and none "
            "before its stopping conditions stand met"
        )
    if not stopping_rule_state(position)["readout_point"]:
        status = "not at the readout point"
    else:
        status = "at the readout point, not established"
    exercised = _base_dict_get(carriage, "strategies_exercised", [])
    if not isinstance(exercised, (list, tuple)):
        raise NamedAttackerFailure(
            "readout rejected: the strategies exercised stand in "
            "no list form: " + _stored_form_repr(exercised)
        )
    swept = _base_dict_get(
        search_record, "external_profit_swept_values", [])
    if swept is None:
        swept = []
    if not isinstance(swept, (list, tuple)):
        raise NamedAttackerFailure(
            "readout rejected: the external profit swept values "
            "stand in no list form: " + _stored_form_repr(swept)
        )
    in_protocol_only = (
        not _base_contains(exercised, "conditional briber")
        or not any(
            _stands_numeric(v) and _plain_number(v) > 0
            for v in _base_sequence(swept))
    )
    search_limb = _base_dict_get(search_record, "search_record", {})
    recorded_failure = False
    outcomes_recorded = False
    if isinstance(search_limb, dict):
        outcomes = _base_dict_get(
            search_limb, "per_point_outcome", [])
        if isinstance(outcomes, dict):
            outcomes_recorded, recorded_failure = (
                _recorded_outcome_state(outcomes))
        else:
            for entry in _base_sequence(outcomes):
                entry_recorded, entry_failure = (
                    _list_entry_outcome_state(entry))
                outcomes_recorded = (
                    outcomes_recorded or entry_recorded)
                recorded_failure = (
                    recorded_failure or entry_failure)
    unit = {
        "wording": wording,
        "coverage_sentence": COVERAGE_SENTENCE,
        "coverage_number_for_confined_class": None,
        "readout_status": status,
        "units": UNITS,
    }
    if not found_failure and not recorded_failure and (
            outcomes_recorded):
        unit["no_failure_sentence"] = NO_FAILURE_SENTENCE
    if in_protocol_only:
        unit["result_kind"] = "in protocol result only"
    else:
        unit["result_kind"] = "economic security result"
    return unit


def attacker_cost_summary(witness_run):
    """The attacker cost summary of INV8B-14 for one witness run.

    A descriptive figure beside the witness, priced per failure
    witness run, changing no regime classification. Every field
    the summary carries stands rendered safe, so the summary
    itself stands safe to render whole. A run carrying none of
    a figure the summary reports stands named in the summary
    itself: absent_fields names each reported field whose
    value stands absent on the run, and where no regime
    classification stands on the run the summary states that
    standing in classification_standing and carries no changed
    verdict, regime_classification_changed standing as no
    value, in place of a verdict reading as a classification
    that stood and did not change.
    """
    if not isinstance(witness_run, dict):
        raise NamedAttackerFailure(
            "attacker cost summary rejected: the witness run "
            "stands in no record form: " + _stored_form_repr(witness_run)
        )
    identifier = _base_dict_get(witness_run, "run_identifier")
    cost = _stored_copy(_base_dict_get(witness_run, "attacker_cost"))
    harm = _stored_copy(_base_dict_get(witness_run, "harm"))
    classification = _base_dict_get(
        witness_run, "regime_classification")
    absent_fields = []
    if identifier is None:
        absent_fields.append("run_identifier")
    if cost is None:
        absent_fields.append("attacker_cost")
    if harm is None:
        absent_fields.append("harm")
    if classification is None:
        absent_fields.append("regime_classification")
    if classification is None:
        classification_standing = (
            "no regime classification stands on the run, and no "
            "classification change stands judged")
        classification_changed = None
    else:
        classification_standing = (
            "the regime classification stands on the run and "
            "stands unchanged by this summary")
        classification_changed = False
    classification_safe = _render_safe_copy(classification)
    return {
        "witness_run": _render_safe_copy(identifier),
        "attacker_cost": _render_safe_copy(cost),
        "harm": _render_safe_copy(harm),
        "standing": "descriptive figure beside the witness",
        "priced_per": "failure witness run",
        "regime_classification_changed": classification_changed,
        "classification_before": classification_safe,
        "classification_after": classification_safe,
        "absent_fields": absent_fields,
        "classification_standing": classification_standing,
        "units": UNITS,
    }


def witness_carriage(witness_run, envelope_claim_names_witness=True):
    """The witness carriage this slice supplies for one run."""
    if not isinstance(witness_run, dict):
        raise NamedAttackerFailure(
            "witness carriage rejected: the witness run stands in "
            "no record form: " + _stored_form_repr(witness_run)
        )
    carriage = {
        "witness_run": _render_safe_copy(
            _base_dict_get(witness_run, "run_identifier")),
        "regime_classification": _render_safe_copy(
            _base_dict_get(witness_run, "regime_classification")),
    }
    if envelope_claim_names_witness:
        carriage["attacker_cost_summary"] = attacker_cost_summary(
            witness_run)
    return carriage


def search_record_covers_hostile_kinds(record, family_record_kinds):
    """Check the hostile input family carriage of one record.

    Each kind stands with a magnitude or range fixed in the family
    record before runs. A kind run below its fixed magnitude does
    not count as run.
    """
    covered = {}
    runs = _base_dict_get(record, "hostile_kind_runs", {}) if (
        isinstance(record, dict)) else {}
    if not isinstance(runs, dict):
        runs = {}
    family = family_record_kinds if isinstance(
        family_record_kinds, dict) else {}
    for kind in HOSTILE_INPUT_KINDS:
        fixed = _base_dict_get(family, kind)
        ran = _base_dict_get(runs, kind)
        if not _stands_numeric(fixed) or not _stands_numeric(ran):
            covered[kind] = False
        else:
            covered[kind] = _plain_number(ran) >= _plain_number(
                fixed)
    return covered


class AttackerSeat:
    """The Attacker Seat: mechanism and ladder carriage."""

    def __init__(self, strategy_class=None, ladder_position=None,
                 catalogue_version_or_hash=None,
                 ladder_definition_pointer=None,
                 ladder_definition_version=None):
        self.strategy_class = strategy_class
        self.ladder_position = ladder_position
        self.catalogue_version_or_hash = catalogue_version_or_hash
        self.ladder_definition_pointer = ladder_definition_pointer
        self.ladder_definition_version = ladder_definition_version

    def run_record_carriage(self, strategies=None):
        return run_record_carriage(
            self.strategy_class, self.ladder_position,
            self.catalogue_version_or_hash,
            self.ladder_definition_pointer,
            self.ladder_definition_version, strategies=strategies)

    def run_search(self, points_tried, per_point_outcome,
                   bond_candidates, strategies=None, **kwargs):
        carriage = self.run_record_carriage(strategies=strategies)
        return run_search(carriage, points_tried, per_point_outcome,
                          bond_candidates, **kwargs)

    def search(self, *args, **kwargs):
        return self.run_search(*args, **kwargs)

    def bond_search(self, parameter_candidates,
                    griefing_evaluator=None):
        return bond_search(parameter_candidates, griefing_evaluator)

    def readout(self, search_record, **kwargs):
        return readout(search_record, **kwargs)

    def stopping_rule_state(self):
        return stopping_rule_state(self.ladder_position)

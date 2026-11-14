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
    read through the base dict get, never through a get reading
    the mapping itself supplies. A handed value in no mapping
    form stores nothing under any key."""
    if isinstance(mapping, dict):
        return dict.get(mapping, key, default)
    return default


def _base_dict_contains(mapping, key):
    """Return whether a handed mapping stores a key, read
    through the base dict contains, never through a contains
    reading the mapping itself supplies."""
    return isinstance(mapping, dict) and dict.__contains__(
        mapping, key)


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


def _stored_match(first, second):
    """Judge two stored values: text values by their stored
    characters through the base string equality, any other pair
    by the plain equality of its plain forms."""
    if isinstance(first, str) or isinstance(second, str):
        if not (isinstance(first, str) and isinstance(second, str)):
            return False
        result = str.__eq__(first, second)
        return result if result is not NotImplemented else False
    return first == second


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
    result = first == second
    return result is True


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
    boolean by itself, a number by standing apart from zero,
    and any other stored value by standing apart from None."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, (str, list, tuple, dict, set, frozenset,
                          bytes, bytearray, memoryview)):
        return _base_length(value) > 0
    if isinstance(value, (int, float)):
        return value != 0
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
    A part in no container form and no buffer form stands copied
    as itself."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_stored_copy(key, _memo)] = _stored_copy(
                item, _memo)
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
        return set(parts) if isinstance(value, set) else frozenset(
            parts)
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


def _catalogue_order_key(name):
    """Return the stated order key for one identifier of an
    unordered identifier container. A text identifier stands
    ordered by its stored text, read character by character
    through the base string reading so a reading the identifier
    itself supplies directs nothing. A bytes form identifier
    stands ordered after text identifiers, by the text its
    stored bytes decode to. Every other identifier stands
    ordered last, by its kind name and its base representation."""
    if isinstance(name, str):
        return (0, "".join(
            str.__getitem__(name, index)
            for index in range(str.__len__(name))), "")
    if isinstance(name, (bytes, bytearray, memoryview)):
        return (1, bytes(name).decode("utf-8", "ignore"),
                type(name).__name__)
    return (2, type(name).__name__, repr(name))


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
    stand appended in the order handed.
    """
    identifiers = list(NAMED_STRATEGIES)
    record = mod03_catalogue_record()
    if isinstance(record, dict):
        for entry in record.get("entries", []):
            if isinstance(entry, dict) and entry.get(
                    "archetype_id") is not None:
                name = entry["archetype_id"]
                if name not in identifiers:
                    identifiers.append(name)
    extras = extra_identifiers or []
    if isinstance(extras, (set, frozenset)):
        extras = sorted(extras, key=_catalogue_order_key)
    for name in extras:
        if name not in identifiers:
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
    return {
        "strategy_identifier": identifier,
        "in_protocol_payoff": in_protocol_payoff,
        "external_profit_range": list(external_profit_range or [0]),
        "external_profit_standing": (
            "swept parameter, labelled assumption, " + UNITS),
        "external_profit_declared_by": None,
        "parameters": _stored_copy(parameters or {}),
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
            "stands in no numeric form: " + repr(in_protocol)
        )
    if isinstance(external_profit_value, bool) or not isinstance(
            external_profit_value, (int, float)):
        raise NamedAttackerFailure(
            "attacker payoff rejected: the external profit value "
            "stands in no numeric form: " + repr(external_profit_value)
        )
    if not math.isfinite(in_protocol) or not math.isfinite(
            external_profit_value):
        raise NamedAttackerFailure(
            "attacker payoff rejected: a payoff part stands in no "
            "finite numeric form: in protocol "
            + repr(in_protocol) + ", external "
            + repr(external_profit_value)
        )
    return in_protocol + external_profit_value


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
            "in no record form: " + repr(strategy)
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
            "stands in no range form: " + repr(stated_range)
        )
    for value in values:
        if not _stands_numeric(value):
            raise NamedAttackerFailure(
                "external profit sweep rejected: a stated range "
                "value stands in no numeric form: " + repr(value)
            )
    if 0 not in values:
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
            + repr(largest)
        )
    if not any(value > largest for value in values):
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
            "in no class list form: " + repr(strategy_class)
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
            "in no list form: " + repr(strategies)
        )
    if ladder_position is None:
        raise NamedAttackerFailure(
            "run record rejected: no ladder position stands stated"
        )
    if isinstance(ladder_position, bool) or not isinstance(
            ladder_position, int) or ladder_position < 0 or (
            ladder_position > READOUT_POINT_RUNG):
        raise NamedAttackerFailure(
            "run record rejected: the ladder position stands outside "
            "the whole rungs 0 to 6 of the search ladder: "
            + repr(ladder_position)
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
                + str(name)
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
        failures.append("the search record field list stands absent")
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
                        stored, (str, list, tuple, dict, set)) and (
                        _base_length(stored) == 0):
                    failures.append(
                        "the search record field stands empty: "
                        + field)
    bond = _base_dict_get(record, "bond_parameter_search")
    if not isinstance(bond, dict):
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
            if _base_dict_get(use, "fixture") == "F-26" and (
                    _base_dict_get(use, "use")
                    != "strategy search point only"):
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
                stored, (str, list, tuple, dict, set)) and (
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
        if _base_dict_get(use, "fixture") == "F-26" and (
                _base_dict_get(use, "use")
                != "strategy search point only"):
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
        and ladder_position == READOUT_POINT_RUNG
    )
    state = {
        "ladder_position": ladder_position,
        "readout_point": complete,
        "established": False,
        "established_bar": (
            "no readout is reported as established under stopping "
            "condition 2 while DQ7-10 stands open"),
    }
    if ladder_position == 0:
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
                "in no record form: " + repr(candidate)
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
                    + repr(candidate)
                )
            if not cost or harm is None:
                continue
            factor = harm / cost
        if not _stands_numeric(factor) or not math.isfinite(factor):
            raise NamedAttackerFailure(
                "bond parameter search rejected: a griefing factor "
                "stands in no finite numeric form: " + repr(factor)
            )
        scored.append({
            "parameter_set": _stored_copy(params),
            "griefing_factor": factor,
        })
    if not scored:
        raise NamedAttackerFailure(
            "bond parameter search rejected: no scored parameter "
            "set stands in the search"
        )
    worst = max(scored, key=lambda item: item["griefing_factor"])
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
    for use in case_uses or []:
        entry = _stored_copy(use)
        if entry.get("fixture") == "F-26":
            entry["use"] = "strategy search point only"
            entry["standings_carried"] = list(
                SELFISH_MINING_STANDINGS)
            entry["standings_asserted_as_settled"] = False
            entry["deployed_failure_case"] = False
        uses.append(entry)
    record = {
        "run_record": _stored_copy(run_carriage),
        "search_record": {
            "search_budget": budget,
            "points_tried": _stored_copy(points_tried),
            "neighbourhood_definition_and_step_sizes": (
                _stored_copy(neighbourhood)),
            "starting_points": _stored_copy(starting_points),
            "order_of_search": _stored_copy(order_of_search),
            "per_point_outcome": _stored_copy(per_point_outcome),
            "every_adaptation": _stored_copy(adaptations or []),
        },
        "bond_parameter_search": bond_search(
            bond_candidates, griefing_evaluator),
        "case_uses": uses,
        "external_profit_swept_values": list(
            external_profit_swept_values or []),
        "mid_run_strategies": list(mid_run_strategies or []),
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
    protocol result only, never as an economic security result.
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
            "no record form: " + repr(carriage)
        )
    position = _base_dict_get(carriage, "ladder_position")
    if established:
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
            "no list form: " + repr(exercised)
        )
    swept = _base_dict_get(
        search_record, "external_profit_swept_values", [])
    if swept is None:
        swept = []
    if not isinstance(swept, (list, tuple)):
        raise NamedAttackerFailure(
            "readout rejected: the external profit swept values "
            "stand in no list form: " + repr(swept)
        )
    in_protocol_only = (
        not _base_contains(exercised, "conditional briber")
        or not any(
            _stands_numeric(v) and v > 0
            for v in _base_sequence(swept))
    )
    unit = {
        "wording": wording,
        "coverage_sentence": COVERAGE_SENTENCE,
        "coverage_number_for_confined_class": None,
        "readout_status": status,
        "units": UNITS,
    }
    if not found_failure:
        unit["no_failure_sentence"] = NO_FAILURE_SENTENCE
    if in_protocol_only:
        unit["result_kind"] = "in protocol result only"
    return unit


def attacker_cost_summary(witness_run):
    """The attacker cost summary of INV8B-14 for one witness run.

    A descriptive figure beside the witness, priced per failure
    witness run, changing no regime classification.
    """
    if not isinstance(witness_run, dict):
        raise NamedAttackerFailure(
            "attacker cost summary rejected: the witness run "
            "stands in no record form: " + repr(witness_run)
        )
    return {
        "witness_run": _base_dict_get(witness_run, "run_identifier"),
        "attacker_cost": _base_dict_get(witness_run, "attacker_cost"),
        "harm": _base_dict_get(witness_run, "harm"),
        "standing": "descriptive figure beside the witness",
        "priced_per": "failure witness run",
        "regime_classification_changed": False,
        "classification_before": _base_dict_get(
            witness_run, "regime_classification"),
        "classification_after": _base_dict_get(
            witness_run, "regime_classification"),
        "units": UNITS,
    }


def witness_carriage(witness_run, envelope_claim_names_witness=True):
    """The witness carriage this slice supplies for one run."""
    if not isinstance(witness_run, dict):
        raise NamedAttackerFailure(
            "witness carriage rejected: the witness run stands in "
            "no record form: " + repr(witness_run)
        )
    carriage = {
        "witness_run": _base_dict_get(witness_run, "run_identifier"),
        "regime_classification": _base_dict_get(
            witness_run, "regime_classification"),
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
            covered[kind] = ran >= fixed
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

"""MOD-06. Escrow Core.

The core contract behaviour for both variants, B-4 the ruled core
and B-3 the core as built for comparison arms, with the K1 and L2
state per contract carried in every B-5 run record as Shape 9
requires, and with the core only qualifier true on every escrow
bearing result.

The verification limit of the source account travels with this
module in every output statement: integration never run, on chain
runtime not verified. No field in any output holds a real money
value. This module never calls MOD-05.

The ruling text gaps at OP-21, G-1 to G-10, stand carried open by
name. Where a value set stands unstated, among them the K1 and L2
value sets at G-10 and the pause arithmetic form at G-8, this
module carries the field and states the gap, and invents no value.
"""

import copy
import unicodedata

from . import mod01

__all__ = [
    "CORE_INSTRUCTION_COUNT",
    "DQ_ARRIVAL_STANDINGS",
    "EXCLUDED_PROFILE",
    "NAMED_CORE_INSTRUCTIONS",
    "PAUSE_CAP_B4",
    "RULING_TEXT_GAPS",
    "VERIFICATION_LIMIT",
    "ExcludedSubpath",
    "GuessedAnswer",
    "UnnamedInstruction",
    "allowed_subpaths",
    "classify_instruction_refusal",
    "contested_entries_for",
    "core_instructions",
    "dq_arrival_table",
    "enter_ruling",
    "escrow_contract_state",
    "escrow_result",
    "excluded_constructions",
    "excluded_subpaths",
    "instruction_refusal_class",
    "matched_arms_valid",
    "pause_cap",
    "pause_value_in_force",
    "profiles",
    "recommended_sweep_set",
    "report_difference",
    "run_instruction",
    "ruling_text_gaps",
    "split_on_construction",
    "validate_dq_arrival_table",
    "validate_escrow_result",
    "validate_folding_record",
    "validate_pause_result",
    "validate_sweep_membership",
]

VERIFICATION_LIMIT = "integration never run, on chain runtime not verified"

CORE_INSTRUCTION_COUNT = 12

NAMED_CORE_INSTRUCTIONS = (
    "replace_backup_key",
    "deposit",
    "withdraw_unliened",
    "open_request",
    "check_in",
    "claim_lost_contact",
)

PAUSE_CAP_B4 = {"extension_percent": 300, "total_percent": 400, "ruling": "DQ-3"}

RULING_TEXT_GAPS = tuple("G-" + str(number) for number in range(1, 11))

EXCLUDED_PROFILE = "backup extended profile"

_ALLOWED = {
    "replace_backup_key": "DQ-5",
    "deposit": "DQ-5",
    "withdraw_unliened": "DQ-5",
    "open_request": "DQ-10, estimated cost limb only",
    "check_in": "DQ-17",
    "claim_lost_contact": "DQ-17",
}

_CONTESTED = {
    "DQ-5": ("C-11",),
    "DQ-10": (),
    "DQ-17": ("C-9",),
}

DQ_ARRIVAL_STANDINGS = {
    "exercised": ("DQ-5", "DQ-10", "DQ-17"),
    "not exercised": tuple(
        "DQ-" + str(number) for number in range(5, 31)
        if "DQ-" + str(number) not in ("DQ-5", "DQ-10", "DQ-17", "DQ-7", "DQ-18", "DQ-30")
    ),
    "position cannot be told": ("DQ-7", "DQ-18", "DQ-30"),
}


class ExcludedSubpath(Exception):
    """A subpath or profile excluded on a DQ ground stays excluded."""


class UnnamedInstruction(Exception):
    """An instruction stands unnamed in the cited set of core
    instructions: no exercised case stands for it, and it stands
    refused as unnamed, not as an excluded subpath."""


class GuessedAnswer(Exception):
    """No case encodes a guess at any item from DQ-5 to DQ-30."""


def _get(record, *names, default=None):
    if isinstance(record, dict):
        for name in names:
            if name in record and record[name] is not None:
                return record[name]
        return default
    return default


def core_instructions():
    """The core as cited at the Step 2 reading: 12 core instructions
    in count, of which the records in this plan name six. The other
    six stand unnamed in the material this slice rests on, and no
    name is invented for them here. That gap stands carried open."""
    return {
        "count": CORE_INSTRUCTION_COUNT,
        "named": list(NAMED_CORE_INSTRUCTIONS),
        "unnamed_count": CORE_INSTRUCTION_COUNT - len(NAMED_CORE_INSTRUCTIONS),
    }


def ruling_text_gaps():
    """The ruling text gaps at OP-21, G-1 to G-10, carried open by
    name, filled by no inference."""
    return list(RULING_TEXT_GAPS)


# ---------------------------------------------------------------------------
# Escrow bearing results and the core only qualifier
# ---------------------------------------------------------------------------

_HOMOGLYPH_MAP = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0445": "x", "\u0443": "y", "\u0456": "i",
    "\u0458": "j", "\u0455": "s", "\u04bb": "h",
    "\u03b1": "a", "\u03b5": "e", "\u03bf": "o", "\u03c1": "p",
    "\u03c4": "t", "\u03ba": "k", "\u03b9": "i", "\u03bd": "v",
    "\u03c7": "x",
}

_HOMOGLYPH_MAP.update({
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
})

# The sister fold readings: the small capital letters read as the
# Latin letters they stand for, the Armenian oh and vo letters read
# as o and n, and the symbol substitutions read as the letters they
# commonly stand for. The symbol readings stand in the letter maps
# themselves, so a symbol standing in a word reads as its letter
# before any non alphanumeric character is dropped from the fold.
_HOMOGLYPH_MAP.update({
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u1d31": "e", "\u1d38": "l", "\u1d3c": "o", "\u1d40": "t",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y", "$": "s",
    "\u00a2": "c", "\u00a7": "s", "+": "t",
    "\u13d2": "r", "\u13ac": "e", "\u13aa": "a", "\u13de": "l",
    "\u13b7": "m", "\u13be": "o", "\u13c1": "n", "\u13ef": "y",
    "\uaba2": "r", "\uab7c": "e", "\uab7a": "a", "\uabae": "l",
    "\uab87": "m", "\uab8e": "o", "\uab91": "n", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
    "\u2ca2": "r", "\u2c88": "e", "\u2c80": "a", "\u2c96": "l",
    "\u2c98": "m", "\u2c9e": "o", "\u2c9a": "n", "\u2ca8": "y",
})

# The transliterated reading: the same letters read by the Latin
# spelling they transliterate to, where that spelling differs from
# the letter they stand rendered as. Cyrillic er reads as r, es as
# s, en as n, u as u, and ha as h in this reading, and letters with
# no Latin letter of their own read as their sounded spelling.
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

# Beside the n reading of the Armenian vo letters, the same letters
# carry an un reading, as the sister fold at MOD-12 records, so an
# amount key spelled with vo standing for the letters un reads as
# amount under this further reading while the n reading stands.
_HOMOGLYPH_MAP_VO = dict(_HOMOGLYPH_MAP, **{"\u0578": "un", "\u0548": "un"})
_TRANSLITERATION_MAP_VO = dict(
    _TRANSLITERATION_MAP, **{"\u0578": "un", "\u0548": "un"})

_LEET_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s",
}

# The figure one stands for two letters: l in one reading and i in
# the other, as the reference fold reads it.
_LEET_MAP_I = dict(_LEET_MAP, **{"1": "i"})

_PAYLOAD_DEPTH_BOUND = 100


# Letters that carry two recorded readings each, so one key may
# need either reading at either position where the letter stands:
# Cyrillic en reads as n and as h, and Cyrillic u and Greek
# upsilon each read as u and as y. A single map reading takes one
# reading for every position at once, so the folded readings also
# stand generated position by position over these letters.
_MULTI_READINGS = {
    "\u043d": ("n", "h"),
    "\u0443": ("u", "y"),
    "\u03c5": ("u", "y"),
    "\u0578": ("n", "un"),
}


def _fold_characters(key):
    """The characters of one key in folded form: lowercased,
    compatibility decomposed and lowercased again, so a modifier
    small capital letter reduces to the Latin letter it stands
    for, with combining marks dropped."""
    decomposed = unicodedata.normalize(
        "NFKD", str(key).lower()).lower()
    return [
        character for character in decomposed
        if not unicodedata.category(character).startswith("M")
    ]


def _character_reading_options(character):
    """Every reading one character carries across the reading
    kinds of this module: the homoglyph reading, the
    transliteration reading, the vo variant readings of both, and
    the multi readings where the character carries two. A
    character recorded in no map reads as itself."""
    options = set()
    if character in _MULTI_READINGS:
        options.update(_MULTI_READINGS[character])
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        if character in letter_map:
            options.add(letter_map[character])
    if not options:
        options.add(character)
    return tuple(sorted(options))


def _folded_readings(key):
    """The folded readings of one key, in the same canonicalised
    form the barred surfaces read: compatibility decomposition
    with combining marks dropped, non Latin homoglyph letters
    mapped to the Latin letters they stand for, separators and
    zero width characters dropped, beside a reading with digit
    substitutions read as letters and a reading with digits
    dropped. The barred forms themselves stand unmoved; only
    their reading gains the folded form. The readings stand taken
    under both the homoglyph map and the transliteration map, and
    under both readings of the figure one, as l and as i, and the
    transliterated spelling of the money marker word itself reads
    as the marker. The readings also stand generated position by
    position over every reading a character carries across the
    reading kinds, so a key needing a homoglyph reading at one
    position and a transliteration or multi reading at another
    stands read as the word it spells. The combined generation
    stands abandoned past 4096 combined texts, never trimmed
    partway through a key, and the character by character
    readings below cover the combinations past that bound."""
    readings = []
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        decomposed = unicodedata.normalize(
            "NFKD", str(key).lower()).lower()
        base = "".join(
            letter_map.get(character, character)
            for character in decomposed
            if not unicodedata.category(character).startswith("M")
        )
        plain = "".join(
            character for character in base if character.isalnum())
        for reading in (
            plain,
            "".join(_LEET_MAP.get(character, character)
                    for character in plain),
            "".join(_LEET_MAP_I.get(character, character)
                    for character in plain),
            "".join(character for character in plain
                    if not character.isdigit()),
        ):
            reading = reading.replace("realmani", "realmoney")
            if reading and reading not in readings:
                readings.append(reading)
    characters = _fold_characters(key)
    if any(
        len(_character_reading_options(character)) > 1
        for character in characters
    ):
        variants = [""]
        for character in characters:
            options = _character_reading_options(character)
            variants = [
                variant + option
                for variant in variants for option in options
            ]
            if len(variants) > 4096:
                variants = None
                break
        for variant in variants or ():
            plain = "".join(
                character for character in variant if character.isalnum())
            for reading in (
                plain,
                "".join(_LEET_MAP.get(character, character)
                        for character in plain),
                "".join(_LEET_MAP_I.get(character, character)
                        for character in plain),
                "".join(character for character in plain
                        if not character.isdigit()),
            ):
                reading = reading.replace("realmani", "realmoney")
                if reading and reading not in readings:
                    readings.append(reading)
    return tuple(readings)


_MULTI_FOLDED_MODES = (None, _LEET_MAP, _LEET_MAP_I, "drop")


def _multi_folded_segment(option, mode):
    plain = "".join(
        character for character in option if character.isalnum())
    if mode is None:
        return plain
    if mode == "drop":
        return "".join(
            character for character in plain if not character.isdigit())
    return "".join(mode.get(character, character) for character in plain)


def _multi_segments_by_character(key, mode):
    """The per character segment options of one key under one
    folded mode, in the form the combined reading generation
    builds: every letter offers each reading it carries across
    the reading kinds, the homoglyph reading, the transliteration
    reading, the vo variant readings, and the multi readings
    where it carries two. No variant is enumerated, so the
    reading covers the whole key at any count of letters carrying
    more than one reading."""
    segments = []
    for character in _fold_characters(key):
        options = _character_reading_options(character)
        segments.append(tuple(
            {_multi_folded_segment(option, mode) for option in options}))
    return segments


def _has_combined_reading(key):
    """Whether any character of the key carries more than one
    reading across the reading kinds, so a combined reading of
    the key can differ from every whole map reading."""
    return any(
        len(_character_reading_options(character)) > 1
        for character in _fold_characters(key)
    )


def _multi_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _multi_segments_carry(segments_by_character, pattern):
    full = len(pattern)
    states = {0}
    for options in segments_by_character:
        next_states = set()
        for state in states:
            for segment in options:
                current = state
                for character in segment:
                    if current == full:
                        break
                    current = _multi_prefix_state(
                        pattern, current, character)
                next_states.add(current)
        if full in next_states:
            return True
        states = next_states
    return full in states


def _multi_segments_match(segments_by_character, target):
    positions = {0}
    for options in segments_by_character:
        next_positions = set()
        for position in positions:
            for segment in options:
                if target[position:position + len(segment)] == segment:
                    next_positions.add(position + len(segment))
        positions = next_positions
        if not positions:
            return False
    return len(target) in positions


def _key_carries_multi_reading(key, marker):
    """Whether some position by position combined reading of the
    whole key carries the marker, read character by character
    without enumerating the variants, so a marker whose reading
    stands past the combined generation bound still stands read.
    The transliterated spelling realmani reads as the marker
    realmoney under the same replacement the folded readings
    apply, so that spelling stands checked beside the marker."""
    if not _has_combined_reading(key):
        return False
    patterns = (marker, "realmani") if marker == "realmoney" else (marker,)
    for mode in _MULTI_FOLDED_MODES:
        segments = _multi_segments_by_character(key, mode)
        if any(
            _multi_segments_carry(segments, pattern)
            for pattern in patterns
        ):
            return True
    return False


def _key_matches_multi_reading(key, target):
    """Whether some position by position combined reading of the
    whole key stands equal to the target, read character by
    character without enumerating the variants."""
    if not _has_combined_reading(key):
        return False
    targets = (target, "realmani") if target == "realmoney" else (target,)
    for mode in _MULTI_FOLDED_MODES:
        segments = _multi_segments_by_character(key, mode)
        if any(
            _multi_segments_match(segments, candidate)
            for candidate in targets
        ):
            return True
    return False


def _key_reads_as(key, folded_name):
    return (
        folded_name in _folded_readings(key)
        or _key_matches_multi_reading(key, folded_name))


def _base_str_eq(first, second):
    """Judge two values by base string equality, where both stand
    in string form, so an equality reading a part supplies is
    never the judgement. A value in no string form never stands
    equal under this reading."""
    if not isinstance(first, str) or not isinstance(second, str):
        return False
    result = str.__eq__(first, second)
    return result if result is not NotImplemented else False


def _base_member(value, options):
    """Whether a value stands in a closed set of string options,
    judged by base string value comparison only."""
    return any(_base_str_eq(value, option) for option in options)


def _undirected_copy(value, _memo=None):
    """Copy a checked payload through base class readings only.

    Dict parts stand read through the base dict items reading,
    and list, tuple, set and frozenset parts through their base
    iteration readings, so no copy protocol a part supplies is
    ever invoked. A part in no container form stands copied as
    itself, so a part that stands inert at the screen stays inert
    in the stored copy and never materialises as another value.
    """
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_undirected_copy(key, _memo)] = (
                _undirected_copy(item, _memo))
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _undirected_copy(item, _memo)
            for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        return tuple(
            _undirected_copy(item, _memo)
            for item in tuple.__iter__(value))
    if isinstance(value, (set, frozenset)):
        base_iter = (
            set.__iter__ if isinstance(value, set)
            else frozenset.__iter__)
        plain_constructor = (
            set if isinstance(value, set) else frozenset)
        return plain_constructor(
            _undirected_copy(item, _memo)
            for item in base_iter(value))
    return value


def _payload_carries_barred(value, _depth=0, _seen=None):
    """Screen a payload at any depth for the barred money and
    anchor forms: a real money value, an amount and currency pair,
    or a supplied anchor set, which DQ-162 and DQ-163 bar. The
    names stand read through the folded reading, so a split or
    dressed spelling of a barred name stands barred as the plain
    spelling stands barred. The money screen reads containment,
    as the other money surfaces do: a folded key that contains
    the marker stands barred, not only a key that starts with it.
    A money name carrying no standing value stands unbarred, as
    on the sister surfaces: the name bars only where a value
    stands under it. The read stands bounded in depth and guarded
    against cycles: a payload past the bound, or one that revisits
    a container on its own path, reads as barred, so the callers
    answer in their stated forms and never in a bare recursion
    error. The bound counts containers only, on the common basis
    the cured guard surfaces state: a chain of 101 containers
    ending in a scalar leaf stands within the bound, and a chain
    of 102 containers stands past it. Records stand read through
    base class operations, so a dict subclass cannot hide its
    stored contents behind its own items, keys, iteration or get
    readings, and set and frozenset nesting stands traversed and
    bounded on the same terms as list and tuple nesting. Nesting
    standing in a dict key stands traversed and bounded on the
    same terms as nesting standing in a dict value."""
    if isinstance(value, dict):
        if _depth > _PAYLOAD_DEPTH_BOUND:
            return True
        seen = set(_seen) if _seen is not None else set()
        if id(value) in seen:
            return True
        seen.add(id(value))
        keys = {str(key).lower() for key in dict.keys(value)}
        if "amount" in keys and "currency" in keys:
            return True
        if (
            any(_key_reads_as(key, "amount") for key in dict.keys(value))
            and any(_key_reads_as(key, "currency") for key in dict.keys(value))
        ):
            return True
        for key, item in dict.items(value):
            lowered = str(key).lower()
            if "anchor_set" in lowered or (
                "real_money" in lowered and item is not None
            ):
                return True
            for reading in _folded_readings(key):
                if "anchorset" in reading or (
                    "realmoney" in reading and item is not None
                ):
                    return True
            if _key_carries_multi_reading(key, "anchorset") or (
                _key_carries_multi_reading(key, "realmoney")
                and item is not None
            ):
                return True
            if _payload_carries_barred(key, _depth + 1, seen):
                return True
            if _payload_carries_barred(item, _depth + 1, seen):
                return True
        return False
    if isinstance(value, (list, tuple)):
        if _depth > _PAYLOAD_DEPTH_BOUND:
            return True
        seen = set(_seen) if _seen is not None else set()
        if id(value) in seen:
            return True
        seen.add(id(value))
        base_iter = list.__iter__ if isinstance(value, list) else tuple.__iter__
        return any(
            _payload_carries_barred(item, _depth + 1, seen)
            for item in base_iter(value))
    if isinstance(value, (set, frozenset)):
        if _depth > _PAYLOAD_DEPTH_BOUND:
            return True
        seen = set(_seen) if _seen is not None else set()
        if id(value) in seen:
            return True
        seen.add(id(value))
        base_iter = (
            frozenset.__iter__ if isinstance(value, frozenset)
            else set.__iter__)
        return any(
            _payload_carries_barred(item, _depth + 1, seen)
            for item in base_iter(value))
    return False


def escrow_result(kind, variant="B-4", payload=None, contract_state=None):
    """One escrow bearing result. Every such result carries the
    core only qualifier reading true, the K1 and L2 state carriage
    Shape 9 requires, and the verification limit statement."""
    if _payload_carries_barred(payload):
        raise ValueError("an escrow result payload carries no real money value and no supplied anchor set")
    state = contract_state if isinstance(contract_state, dict) else {}
    return {
        "kind": kind,
        "variant": variant,
        "core_only_qualifier": True,
        "payload": _undirected_copy(payload),
        "k1_and_l2_state": state.get("k1_and_l2_state", "carried; value set open at OP-21 G-10"),
        "lien_state": state.get("lien_state"),
        "verification_limit": VERIFICATION_LIMIT,
        "real_money_value": None,
    }


def escrow_contract_state(contract_identifier, variant="B-4", lien_state="no lien in force",
                          pause_state=None, lost_contact_clause_on=False,
                          pair_identifiers=None, standard_or_profile_identifier=None,
                          estimated_cost_value=None, pause_cap_value=None, window_n=None):
    """An EscrowContractState in Shape 9 and Form 10 form, carrying
    every Form 10 field group: the pair identifiers, the standard
    or profile identifier, the estimated cost value, the pause
    state with the pause cap value in force, and, where the lost
    contact clause stands on, the clock state with the window
    value N recorded as used. The variant and the lien state stand
    validated against their closed sets. The K1 and L2 state stands
    carried as a field whose value set stands unstated at
    OP-21 G-10, and no value is invented for it."""
    if not _base_member(variant, ("B-3", "B-4")):
        raise ValueError("the escrow variant stands outside the B-3 and B-4 set: " + str(variant))
    if not _base_member(lien_state, mod01.LIEN_STATES):
        raise ValueError("the lien state stands outside the closed four value set: " + str(lien_state))
    state = {
        "contract_identifier": contract_identifier,
        "pair_identifiers": copy.deepcopy(pair_identifiers),
        "standard_or_profile_identifier": standard_or_profile_identifier,
        "variant": variant,
        "lien_state": lien_state,
        "estimated_cost_value": estimated_cost_value,
        "pause_state": pause_state,
        "pause_cap_value": copy.deepcopy(pause_cap_value) if pause_cap_value is not None else pause_cap(variant)["per_variant_pause_value"],
        "k1_and_l2_state": "carried; value set open at OP-21 G-10",
        "lost_contact_clause_on": bool(lost_contact_clause_on),
    }
    if lost_contact_clause_on:
        state["lost_contact_clock_state"] = "contact clocks tracked"
        state["lost_contact_window_n"] = window_n
        state["lost_contact_clock_scope"] = "window value N recorded as used in the standard for that contract"
    return state


def validate_escrow_result(result):
    """A result carrying no core only qualifier, or one reading
    other than true, is not reportable as an escrow result."""
    if not isinstance(result, dict):
        return False
    if dict.get(result, "core_only_qualifier") is not True:
        return False
    if not _base_str_eq(
            dict.get(result, "verification_limit"), VERIFICATION_LIMIT):
        return False
    if not dict.get(result, "k1_and_l2_state"):
        return False
    if dict.get(result, "real_money_value") is not None:
        return False
    if _payload_carries_barred(result):
        return False
    return not _payload_carries_barred(dict.get(result, "payload"))


# ---------------------------------------------------------------------------
# Instruction runs, fixture F-21
# ---------------------------------------------------------------------------

def allowed_subpaths():
    return dict(_ALLOWED)


def excluded_subpaths():
    return {
        "pool subpaths": "excluded; no pool instruction stands among the 12 core instructions",
        EXCLUDED_PROFILE: "excluded in every working run; the construction that needs a DQ-5 answer",
    }


def contested_entries_for(item):
    """The contested entries travelling beside a path: C-11 beside
    the DQ-5 paths, C-9 beside the DQ-17 paths, in every fixture
    that touches them."""
    return list(_CONTESTED.get(item, ()))


def run_instruction(name, variant="B-4", context=None):
    """Run one exercised instruction case as written, fixture F-21.

    Allowed subpaths run as written and claim no DQ answer. Pool
    subpaths and the backup extended profile are refused. A case
    presenting a treatment as a DQ answer, a floor under N, or a
    clock scope reading as an answer is refused as a guess.
    """
    try:
        return _run_instruction_act(name, variant=variant, context=context)
    except (ExcludedSubpath, GuessedAnswer, UnnamedInstruction, ValueError) as error:
        error.failure_class = classify_instruction_refusal()
        raise


def _run_instruction_act(name, variant="B-4", context=None):
    context = dict(context or {})
    if context.get("claims_dq_answer") or context.get("dq_answer") is not None:
        raise GuessedAnswer("no case encodes a guess at any DQ-5 to DQ-30 item")
    if context.get("asserts_floor_under_n") or context.get("asserts_clock_scope_as_answer"):
        raise GuessedAnswer("no floor under N and no clock scope reading stands as a DQ answer")
    if (
        "pool" in str(name)
        or name == EXCLUDED_PROFILE
        or context.get("profile") == EXCLUDED_PROFILE
        or _reads_as_excluded_profile(name)
        or _reads_as_excluded_profile(context.get("profile"))
    ):
        raise ExcludedSubpath("a construction excluded on a DQ ground stays excluded on that ground: " + str(name))
    if name not in _ALLOWED:
        raise UnnamedInstruction("instruction stands unnamed in the cited set of 12 core instructions, with no exercised case standing for it: " + str(name))
    item = _ALLOWED[name].split(",")[0]
    result_payload = {"instruction": name, "dq_item": _ALLOWED[name]}
    result_payload["contested_entries"] = contested_entries_for(item)
    result_payload["claims_dq_answer"] = False
    result_payload["traversal_claim"] = None
    if name == "replace_backup_key":
        if not context.get("backup_key_registered_at_setup"):
            raise ValueError("refused: replace_backup_key stands refused, because it runs only with backup key registration at setup")
        result_payload["backup_key_registered_at_setup"] = True
    if name == "open_request":
        additions = [key for key in ("countersigning", "bound", "verification") if context.get(key)]
        if additions:
            raise ValueError("open_request runs with no countersigning, bound or verification added")
        stated = context.get("stated_cost")
        true = context.get("true_cost")
        if stated is None or true is None:
            raise ValueError("open_request carries its self declared estimated cost in accuracy form")
        if true == 0:
            raise ValueError("open_request stands refused in named form: the true cost stands at zero, so no accuracy form stands")
        result_payload["lien_sized_from"] = "self declared estimated cost"
        result_payload["lien_size"] = stated
        result_payload["estimated_cost"] = {
            "value": stated,
            "form": "labelled assumption, accuracy form: stated cost divided by true cost",
            "accuracy": stated / true,
            "sensitivity_range": context.get("sensitivity_range", "about 0.1 to about 10 on a log spacing, range estimated"),
        }
        result_payload["additions"] = []
    if name in ("check_in", "claim_lost_contact"):
        if not context.get("clause_on"):
            raise ValueError("check_in and claim_lost_contact run for each contract that turns the clause on")
        if context.get("window_n") is None:
            raise ValueError("the window value N stands set in the standard for that contract")
        result_payload["window_n"] = context["window_n"]
        result_payload["window_n_form"] = "labelled assumption in the standard for that contract"
        result_payload["contact_clocks_tracked"] = True
    return escrow_result(name, variant=variant, payload=result_payload)


def _reads_as_excluded_profile(value):
    """Whether a name or profile reads as the excluded profile
    through the folded reading, so a dressed spelling of it, for
    example one carrying a zero width character, stands read as
    the excluded profile itself."""
    if value is None:
        return False
    excluded_readings = _folded_readings(EXCLUDED_PROFILE)
    return any(
        _key_reads_as(value, reading)
        for reading in excluded_readings)


def classify_instruction_refusal():
    """Manager Entry 6: the MOD-06 instruction refusal is recorded
    in the run record only. It does not set the run status to
    failed."""
    return {"recorded_in": "run record only", "run_status": None}


def instruction_refusal_class():
    return classify_instruction_refusal()


# ---------------------------------------------------------------------------
# Pause cap, fixture F-25 and ruling DQ-3
# ---------------------------------------------------------------------------

def pause_cap(variant="B-4", stated_value=None):
    """The pause cap in force, stated per variant. For ruled core
    runs the cap is an extension up to 300 percent, a total of 400
    percent, under ruling DQ-3. For B-3 the value in force stands
    stated in the same per variant field form, and its text
    ambiguity, total or extension, stands unresolved: no reading
    is chosen for B-3 here or by any test."""
    if variant not in ("B-3", "B-4"):
        raise ValueError("the pause cap stands refused in named form for an unknown variant: " + str(variant))
    if variant == "B-4":
        return {
            "variant": "B-4",
            "per_variant_pause_value": dict(PAUSE_CAP_B4),
            "extension_percent": 300,
            "total_percent": 400,
        }
    return {
        "variant": variant,
        "per_variant_pause_value": stated_value,
        "ambiguity": "total or extension unstated in the B-3 variant text",
        "reading_chosen": None,
    }


def pause_value_in_force(variant="B-4", stated_value=None):
    return pause_cap(variant, stated_value=stated_value)


def validate_pause_result(result):
    """A pause related result stating no per variant pause value
    fails validation."""
    if not isinstance(result, dict):
        return False
    value = result.get("per_variant_pause_value")
    if value is None:
        payload = result.get("payload")
        if isinstance(payload, dict):
            value = payload.get("per_variant_pause_value")
    if value is None:
        return False
    variant = result.get("variant")
    if variant is None and isinstance(result.get("payload"), dict):
        variant = result["payload"].get("variant")
    if variant == "B-4":
        if not isinstance(value, dict):
            return False
        return (value.get("extension_percent") == PAUSE_CAP_B4["extension_percent"]
                and value.get("total_percent") == PAUSE_CAP_B4["total_percent"])
    return True


# ---------------------------------------------------------------------------
# Profiles and sweep sets, fixture F-24
# ---------------------------------------------------------------------------

def recommended_sweep_set():
    """Profile 1 and Profile 2 as the recommended sweep set,
    carried as a recommendation and not a ruling at register
    question NQ-50."""
    return [
        {"name": "Profile 1", "construction": "B-3 core only, all toggles off",
         "standing": "recommendation, not a ruling", "register_question": "NQ-50"},
        {"name": "Profile 2", "construction": "B-4 ruled core only, all toggles off",
         "standing": "recommendation, not a ruling", "register_question": "NQ-50"},
    ]


def profiles():
    return recommended_sweep_set()


def split_on_construction():
    """The core with split on construction, distinct from both the
    recommended set and the excluded set."""
    return {
        "name": "core with split on construction",
        "in_recommended_set": False,
        "in_excluded_set": False,
    }


def excluded_constructions():
    """Constructions excluded on a DQ ground stay excluded on that
    ground, with grounds kept apart: 18 entries on a DQ ground, 1
    on a ruling ground, 2 on a scope or coverage ground."""
    return {
        "grounds": {
            "DQ ground": 18,
            "ruling ground": 1,
            "scope or coverage ground": 2,
        },
        "total": 21,
    }


def validate_sweep_membership(construction):
    """True only for a member of the recommended sweep set. An
    excluded construction never runs as a sweep member, and the
    split on construction stands in neither set."""
    names = {entry["name"] for entry in recommended_sweep_set()}
    constructions = {entry["construction"] for entry in recommended_sweep_set()}
    return construction in names or construction in constructions


# ---------------------------------------------------------------------------
# Matched arms, fixture F-12 and contract C-23
# ---------------------------------------------------------------------------

def matched_arms_valid(arm_a, arm_b):
    """Matched arms share every stated input and differ only in
    the variant and the stated conversions, and every escrow
    bearing result in both arms carries the core only qualifier
    reading true."""
    if not isinstance(arm_a, dict) or not isinstance(arm_b, dict):
        return False
    if arm_a.get("variant") == arm_b.get("variant"):
        return False
    shared_keys = ("inputs", "society", "parameters", "seeds")
    for key in shared_keys:
        if key in arm_a or key in arm_b:
            if arm_a.get(key) != arm_b.get(key):
                return False
    for arm in (arm_a, arm_b):
        for result in arm.get("results", ()):
            if not validate_escrow_result(result):
                return False
    return True


# ---------------------------------------------------------------------------
# Folding duty, decision D-02 condition three read with D-20
# ---------------------------------------------------------------------------

def validate_folding_record(record):
    """A folding record stands only where the folding is recorded
    ruling by ruling against the ruling text, with at least one
    seam case per ruling checked by a reader who did not perform
    that folding, and no ruling text gap supplied by inference."""
    if not isinstance(record, dict):
        return False
    entries = record.get("entries")
    if not entries:
        return False
    for entry in entries:
        if not isinstance(entry, dict):
            return False
        if entry.get("filled_by_inference"):
            return False
        if not entry.get("checked_by_independent_reader"):
            return False
        if not entry.get("ruling"):
            return False
    return True


def report_difference(difference, folding_record=None):
    """No B-5 difference is reported as a ruling effect until the
    folding stands recorded in the form validate_folding_record
    states. A difference with no such record stands reported as
    an unfolded difference only, in no ruling effect wording."""
    if folding_record is not None and validate_folding_record(folding_record):
        return {
            "difference": copy.deepcopy(difference),
            "reported_as": "ruling effect",
            "ruling_effect_wording": True,
            "folding_record": copy.deepcopy(folding_record),
        }
    return {
        "difference": copy.deepcopy(difference),
        "reported_as": "unfolded difference only",
        "ruling_effect_wording": False,
        "folding_record": None,
    }


# ---------------------------------------------------------------------------
# DQ arrival table, fixture F-22
# ---------------------------------------------------------------------------

def dq_arrival_table():
    """The shipped blank form of fixture F-22: 26 rows, one per
    item from DQ-5 to DQ-30, with the fixture standings, and the
    final column of every row empty until the ruling for that item
    arrives, when the ruling text is entered there verbatim. No
    row carries an expected answer, a favoured answer, or a
    placeholder value."""
    standing_by_item = {}
    for standing, items in DQ_ARRIVAL_STANDINGS.items():
        for item in items:
            standing_by_item[item] = standing
    rows = []
    for number in range(5, 31):
        item = "DQ-" + str(number)
        rows.append({
            "item": item,
            "standing": standing_by_item[item],
            "final_column": "",
        })
    return rows


def validate_dq_arrival_table(rows):
    """The blank form integrity check: 26 rows, the fixture
    standings, and every final column cell empty. A form with any
    final column cell filled before its ruling arrives fails."""
    rows = list(rows)
    if len(rows) != 26:
        return False
    expected = {row["item"]: row["standing"] for row in dq_arrival_table()}
    seen = [row.get("item") for row in rows if isinstance(row, dict)]
    if len(set(seen)) != 26 or set(seen) != set(expected):
        return False
    for row in rows:
        if not isinstance(row, dict):
            return False
        if expected.get(row.get("item")) != row.get("standing"):
            return False
        if row.get("final_column") not in ("", None):
            return False
    return True


def enter_ruling(rows, item, ruling_text):
    """Enter a ruling in the final column of its row, verbatim,
    when the ruling for that item arrives."""
    updated = copy.deepcopy(list(rows))
    for row in updated:
        if row.get("item") == item:
            row["final_column"] = ruling_text
    return updated

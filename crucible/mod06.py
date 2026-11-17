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

import itertools
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

# Sister readings the letter maps stand short on without this
# block: Cyrillic ka reads as k, Cyrillic ve as b beside its
# transliterated v, Greek phi as f beside its transliterated ph,
# Greek theta as t beside its transliterated th, Cyrillic dje as
# s, Cyrillic ghe with stroke as h, and Cyrillic short i as i
# beside its transliterated y. The transliteration map below
# inherits these entries and then records its own readings over
# the ve, phi, theta, and short i entries, so each of those
# letters carries both readings across the two maps.
_HOMOGLYPH_MAP.update({
    "\u043a": "k", "\u0432": "b", "\u03c6": "f",
    "\u03b8": "t", "\u0439": "i", "\u0452": "s",
    "\u0493": "h",
})

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


_SHORT_I_PLACEHOLDER = "\ue000"


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
    """The characters of one key after compatibility
    decomposition: lowercased, compatibility decomposed and
    lowercased again. Cyrillic short i is held apart from the
    decomposition, which would otherwise reduce it to Cyrillic i
    and lose its second recorded reading as y: the placeholder
    stands in its place through the decomposition, and the letter
    itself stands restored in the returned characters. The key
    text stands taken from the stored characters through the
    base class string form, so a string reading a handed key
    supplies never stands as the text judged."""
    source = _stored_text(key).lower().replace(
        "\u0439", _SHORT_I_PLACEHOLDER)
    decomposed = unicodedata.normalize("NFKD", source).lower()
    return [
        "\u0439" if character == _SHORT_I_PLACEHOLDER else character
        for character in decomposed
    ]


def _fold_characters(key):
    """The characters of one key in folded form: lowercased,
    compatibility decomposed and lowercased again, so a modifier
    small capital letter reduces to the Latin letter it stands
    for, with combining marks dropped."""
    return [
        character for character in _decomposed_characters(key)
        if not unicodedata.category(character).startswith("M")
    ]


def _character_reading_options(character):
    """Every reading one character carries across the reading
    kinds of this module: the homoglyph reading, the
    transliteration reading, the vo variant readings of both, and
    the multi readings where the character carries two. A digit
    carries its digit readings beside itself: the letter of each
    leet map that records it, so the figure one carries both l
    and i, and the dropped reading, so one digit position of a
    key may take its leet letter reading while another takes the
    dropped reading, the two combined position by position inside
    one key. A character recorded in no map reads as itself."""
    options = set()
    if character in _MULTI_READINGS:
        options.update(_MULTI_READINGS[character])
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        if character in letter_map:
            options.add(letter_map[character])
    if character.isdigit():
        options.add(character)
        options.add("")
        for leet_map in (_LEET_MAP, _LEET_MAP_I):
            if character in leet_map:
                options.add(leet_map[character])
    if not options:
        options.add(character)
    return tuple(sorted(options))


def _folded_base_readings(key):
    """The folded readings of one key under the whole map
    readings alone, with no combined variant ever listed: the
    four letter maps, each taken plain, under both digit
    substitution readings, and with digits dropped."""
    readings = []
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        decomposed = _decomposed_characters(key)
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
    return tuple(readings)


def _payload_folded_carries(key, marker):
    """Whether some folded reading of a key carries the
    marker, judged without listing a combined variant text:
    the whole map readings stand read directly, and the
    combined readings stand judged position by position
    through the multi reading act, which covers the
    combinations in the form _folded_readings itself states
    for the texts past its combined bound."""
    if any(
            marker in reading
            for reading in _folded_base_readings(key)):
        return True
    return _key_carries_multi_reading(key, marker)


def _payload_folded_carries_pair(key, first, second):
    """Whether some folded reading of a key carries both
    markers, judged as _payload_folded_carries judges one
    marker: the whole map readings stand read directly, and
    the combined readings stand judged position by position
    over the pair of marker prefix states at once, so no
    combined variant text stands listed."""
    if any(
            first in reading and second in reading
            for reading in _folded_base_readings(key)):
        return True
    if not _has_combined_reading(key):
        return False
    for mode in _MULTI_FOLDED_MODES:
        segments = _multi_segments_by_character(key, mode)
        states = {(0, 0)}
        for options in segments:
            following = set()
            for first_state, second_state in states:
                for segment in options:
                    new_first = first_state
                    new_second = second_state
                    for character in segment:
                        if new_first < len(first):
                            new_first = _multi_prefix_state(
                                first, new_first, character)
                        if new_second < len(second):
                            new_second = _multi_prefix_state(
                                second, new_second, character)
                    following.add((new_first, new_second))
            if (len(first), len(second)) in following:
                return True
            states = following
    return False


def _payload_pair_can_stand(key):
    """Whether the amount and currency pair can stand in any
    folded reading of a container key at all, judged on the
    characters the key stores: every character of the two
    markers must stand producible, with its multiplicity in
    the markers, by the stored characters under some reading
    a character carries, in the generous form that counts a
    character for every marker character any of its folded
    segments contains. Where the supply falls short the pair
    stands in no reading of any order of the parts, and the
    walk lists no joined candidate for it."""
    needed = {}
    for character in "amountcurrency":
        needed[character] = needed.get(character, 0) + 1
    characters = _fold_characters(_joined_stored_text(key))
    supply = {}
    for character in set(characters):
        produced = set()
        for option in _character_reading_options(character):
            for mode in _MULTI_FOLDED_MODES:
                produced.update(_multi_folded_segment(option, mode))
        for marker in needed:
            if marker in produced:
                supply[marker] = supply.get(marker, 0) + len(
                    [c for c in characters if c == character])
    return all(
        supply.get(marker, 0) >= count
        for marker, count in needed.items())


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
    readings = list(_folded_base_readings(key))
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


def _unordered_scalar_parts_read_as(key, folded_name):
    """Whether some joined candidate of an unordered container
    whose direct parts all stand in short scalar text form
    reads as the folded name, judged without listing any
    candidate: a candidate stands judged, in the scalar limb
    of _key_reads_as, on its whole map readings and on its
    position by position combined readings, and each of those
    readings stands built character by character under one
    map or one mode taken whole. The judgement therefore
    stands as an exact tiling of the name over the parts, one
    tiling per map and mode family, in the form
    _seg_tiles_exact states, with every part placed exactly
    once and a part whose segment stands empty placed without
    advancing. The form stands stated for a container of at
    most the unordered join part bound of seven direct parts,
    each storing at most two characters of text whose
    decomposed base stands in ASCII form, a part carried in
    a one part tuple or list container standing read on the
    text its one part stores, as the standing candidate
    enumeration reads it; a key in any other form stands
    answered by the standing candidate enumeration, and this
    act returns None for it, stating no decision."""
    if not isinstance(key, (set, frozenset)):
        return None
    parts = _join_container_parts(key)
    if not 2 <= len(parts) <= _UNORDERED_JOIN_PART_BOUND:
        return None
    texts = []
    for part in parts:
        if isinstance(part, (tuple, list)):
            inner = _join_container_parts(part)
            if len(inner) != 1:
                return None
            part = inner[0]
        if isinstance(part, (dict, list, tuple, set, frozenset)):
            return None
        text = _stored_text(part)
        if len(text) > 2:
            return None
        if not text.isascii():
            decomposed = "".join(
                character
                for character in unicodedata.normalize("NFKD", text)
                if not unicodedata.category(
                    character).startswith("M"))
            if not decomposed.isascii():
                return None
        texts.append(text)
    targets = [folded_name]
    if "realmoney" in folded_name:
        targets.append(folded_name.replace("realmoney", "realmani"))
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        for mode in (None, _LEET_MAP, _LEET_MAP_I, "drop"):
            options = []
            for text in texts:
                base = "".join(
                    letter_map.get(character, character)
                    for character in _decomposed_characters(text)
                    if not unicodedata.category(
                        character).startswith("M"))
                plain = "".join(
                    character for character in base
                    if character.isalnum())
                if mode is None:
                    segment = plain
                elif mode == "drop":
                    segment = "".join(
                        character for character in plain
                        if not character.isdigit())
                else:
                    segment = "".join(
                        mode.get(character, character)
                        for character in plain)
                options.append({segment})
            if any(
                _seg_tiles_exact(options, target)
                for target in targets
            ):
                return True
    for mode in _MULTI_FOLDED_MODES:
        options = []
        for text in texts:
            segments = {""}
            for character in _fold_characters(text):
                segments = {
                    head + _multi_folded_segment(option, mode)
                    for head in segments
                    for option in _character_reading_options(
                        character)}
            options.append(segments)
        if any(
            _seg_tiles_exact(options, target)
            for target in targets
        ):
            return True
    return False


def _key_reads_as(key, folded_name):
    if isinstance(key, (dict, list, tuple, set, frozenset)):
        if _has_unordered_split(key):
            joined_text = _joined_stored_text(key)
            low = 0
            high = 0
            for character in _fold_characters(joined_text):
                lengths = []
                for option in _character_reading_options(character):
                    plain_option = "".join(
                        part for part in option if part.isalnum())
                    lengths.append(len(plain_option))
                    lengths.append(len("".join(
                        part for part in plain_option
                        if not part.isdigit())))
                if lengths:
                    low += min(lengths)
                    high += max(lengths)
            if low <= len(folded_name) <= high:
                decided = _unordered_scalar_parts_read_as(
                    key, folded_name)
                if decided is not None:
                    if decided:
                        return True
                else:
                    for candidate in _joined_text_candidates(key):
                        if candidate and _key_reads_as(
                                candidate, folded_name):
                            return True
        if _seg_exact(key, folded_name):
            return True
        joined = _joined_stored_text(key)
        if joined and _key_reads_as(joined, folded_name):
            return True
        seen = set()
        stack = [key]
        while stack:
            part = stack.pop()
            if isinstance(part, (dict, list, tuple, set, frozenset)):
                if id(part) in seen:
                    continue
                seen.add(id(part))
                if isinstance(part, dict):
                    stack.extend(dict.keys(part))
                elif isinstance(part, list):
                    stack.extend(list.__iter__(part))
                elif isinstance(part, tuple):
                    stack.extend(tuple.__iter__(part))
                elif isinstance(part, frozenset):
                    stack.extend(frozenset.__iter__(part))
                else:
                    stack.extend(set.__iter__(part))
            elif _key_reads_as(part, folded_name):
                return True
        return False
    if folded_name in _folded_base_readings(key):
        return True
    low = 0
    high = 0
    for character in _fold_characters(key):
        lengths = []
        for option in _character_reading_options(character):
            plain_option = "".join(
                part for part in option if part.isalnum())
            lengths.append(len(plain_option))
            lengths.append(len("".join(
                part for part in plain_option
                if not part.isdigit())))
        if lengths:
            low += min(lengths)
            high += max(lengths)
    if len(folded_name) < low or len(folded_name) > high:
        return False
    if _key_matches_multi_reading(key, folded_name):
        return True
    return folded_name in _folded_readings(key)


def _base_iter(value):
    """Iterate a container through its base class iteration, never
    through a reading the value itself supplies."""
    if isinstance(value, list):
        return list.__iter__(value)
    if isinstance(value, tuple):
        return tuple.__iter__(value)
    if isinstance(value, frozenset):
        return frozenset.__iter__(value)
    return set.__iter__(value)


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


def _refusal_text(value):
    """Render a handed value for a refusal sentence: through
    its string reading where that reading stands, and through
    the base object repr where the string or repr reading the
    value itself supplies raises, so the refusal stands as a
    full named refusal and never escapes bare on that reading."""
    try:
        return str(value)
    except Exception:
        return object.__repr__(value)


def _sentence_text(value):
    """Render a handed value for a refusal sentence on the
    text it stores, where the value stands in a text or
    buffer form, so a string reading the value itself
    supplies, lying or raising, never stands as the name
    the sentence delivers. A value in any other form
    stands rendered through _refusal_text, as before."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    return _refusal_text(value)


def _undirected_copy(value, _memo=None):
    """Copy a checked payload through base class readings only.

    Dict parts stand read through the base dict items reading,
    and list, tuple, set and frozenset parts through their base
    iteration readings, so no copy protocol a part supplies is
    ever invoked. The buffer forms stand carried as stored: a
    bytearray as a fresh bytearray and a memoryview as a
    memoryview over fresh bytes. A part in no container form and
    no buffer form stands copied as itself, so a part that stands
    inert at the screen stays inert in the stored copy and never
    materialises as another value. A dict assignment whose key hash or equality reading
    raises at the assignment itself stands carried under a
    distinct numbered form, a plain text numbered form where
    a form carrying the key itself cannot stand inserted, in
    the MOD-14 cured form, so no carried entry is silently
    dropped on that reading and no bare error escapes the copy.
    """
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied_key = _undirected_copy(key, _memo)
            copied_item = _undirected_copy(item, _memo)
            try:
                copied[copied_key] = copied_item
            except Exception:
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
            _undirected_copy(item, _memo)
            for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _undirected_copy(item, _memo)
            for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        if id(value) in _memo:
            return _memo[id(value)]
        base_iter = (
            set.__iter__ if isinstance(value, set)
            else frozenset.__iter__)
        copied_items = [
            _undirected_copy(item, _memo)
            for item in base_iter(value)]
        if isinstance(value, set):
            copied = set()
            _memo[id(value)] = copied
            try:
                for copied_item in copied_items:
                    copied.add(copied_item)
            except Exception:
                _memo[id(value)] = copied_items
                return copied_items
            return copied
        try:
            copied = frozenset(copied_items)
        except Exception:
            copied = copied_items
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    return value


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
            elif isinstance(part, list):
                parts = list(list.__iter__(part))
            elif isinstance(part, tuple):
                parts = list(tuple.__iter__(part))
            elif isinstance(part, frozenset):
                parts = list(frozenset.__iter__(part))
            else:
                parts = list(set.__iter__(part))
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
    if isinstance(node, list):
        return list(list.__iter__(node))
    if isinstance(node, tuple):
        return list(tuple.__iter__(node))
    if isinstance(node, frozenset):
        return list(frozenset.__iter__(node))
    return list(set.__iter__(node))


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


def _seg_exact(key, target):
    """Whether an unordered container standing inside a key
    joins, in some order of its direct parts, to a reading
    standing exactly as the target, judged by segmentation of
    the target over the folded readings of the parts, beside
    the kept candidate readings."""
    for node, parts in _seg_unordered_nodes(key):
        universe = _seg_universe((target,), ())
        if _seg_tiles_exact(
                _seg_folded_options(
                    parts, universe, _seg_prefixes(universe)),
                target):
            return True
    return False


def _multi_part_transition(part, mode, pattern):
    """The folded multi reading transition of one part under
    one mode, stated per opening position of the pattern:
    for each opening position, the set of positions the part
    can leave the reading at beside whether the part can
    complete the pattern from that position. The part stands
    read character by character over its recorded reading
    options, with no variant text ever listed."""
    segments = _multi_segments_by_character(part, mode)
    table = []
    for state in range(len(pattern)):
        current = {state}
        matched = False
        for options in segments:
            following = set()
            for opening in current:
                for segment in options:
                    position = opening
                    for character in segment:
                        if position == len(pattern):
                            break
                        position = _multi_prefix_state(
                            pattern, position, character)
                    following.add(position)
            if len(pattern) in following:
                matched = True
            current = following
        table.append((current, matched))
    return table


def _seg_multi_carrying(parts, pattern):
    """Whether the direct parts of one unordered container
    can stand in some order so that a multi reading mixture
    of their joined reading carries the pattern, in the form
    settlement S-4 states for the multi reading space: the
    judgement runs as a walk over the sets of parts already
    placed beside the reading positions they reach, under
    each folded mode in turn, with every part used at most
    once and parts outside the carrying block standing free.
    No ordering and no combined variant text is ever listed,
    so the judgement stands the same past the kept candidate
    bound as inside it."""
    if len(parts) > 10:
        return False
    if any(
            isinstance(part, (dict, list, tuple, set, frozenset))
            for part in parts):
        return False
    if not any(_has_combined_reading(part) for part in parts):
        return False
    for mode in _MULTI_FOLDED_MODES:
        tables = [
            _multi_part_transition(part, mode, pattern)
            for part in parts]
        reached = {0: {0}}
        for mask in range(1 << len(parts)):
            states = reached.get(mask)
            if not states:
                continue
            for index in range(len(parts)):
                if (mask >> index) & 1:
                    continue
                following = set()
                for state in states:
                    out, matched = tables[index][state]
                    if matched:
                        return True
                    following |= out
                if len(pattern) in following:
                    return True
                if following:
                    reached.setdefault(
                        mask | (1 << index), set()).update(following)
    return False



def _payload_block_exact_options(block, universe, prefixes, folded):
    """The exact pieces one block of a whole key reading can
    contribute to a spanning judgement: for a leaf block its
    stated options, and for a composite block the universe
    texts it can join to exactly through the formable
    computation, so no joined candidate of the block and no
    folded variant of one stands listed."""
    if not isinstance(block, (dict, list, tuple, set, frozenset)):
        if folded:
            return _seg_folded_options(
                [block], universe, prefixes)[0]
        return _seg_plain_options([block], universe, prefixes)[0]
    try:
        forms, can_empty = _seg_formable(
            block, universe, prefixes, folded)
    except RecursionError:
        forms, can_empty = set(), False
    options = set(forms)
    if can_empty:
        options.add("")
    return options


def _payload_spanning_barred(key, item_present):
    """Whether a barred marker of the payload walk stands
    spanned across the blocks of the whole key, in the form
    settlement S-4 states and _seg_spanning_barred judges,
    with the blocks judged through the part edge predicates
    and their exact formable pieces, so the judgement stands
    the same past the candidate caps as inside them and no
    candidate of a composite block stands listed. An ordered
    key keeps its stored order; an unordered key stands
    judged over its direct parts in any order."""
    found = _span_blocks(key)
    if found is None:
        return False
    mode, blocks = found
    if not blocks:
        return False
    spaces = []
    plain_patterns = ("anchor_set",) + (
        ("real_money",) if item_present else ())
    folded_patterns = ("anchorset",) + (
        ("realmoney", "realmani") if item_present else ())
    spaces.append((plain_patterns, False))
    spaces.append((folded_patterns, True))
    for patterns, folded in spaces:
        universe = _seg_universe((), patterns)
        prefixes = _seg_prefixes(universe)
        options = [
            _payload_block_exact_options(
                block, universe, prefixes, folded)
            for block in blocks]
        for pattern in patterns:
            for block in blocks:
                try:
                    if _seg_part_can_contain(block, pattern, folded):
                        return True
                except RecursionError:
                    continue
            if mode == "unordered":
                if _seg_parts_carry_edge(
                        blocks, options, pattern, folded):
                    return True
                continue
            seen = {(0, 0)}
            stack = [(0, 0)]
            while stack:
                index, matched = stack.pop()
                if matched == len(pattern):
                    return True
                if index >= len(blocks):
                    continue
                block = blocks[index]
                if matched == 0:
                    try:
                        if _seg_part_can_end(block, pattern, folded):
                            return True
                    except RecursionError:
                        pass
                    for stop in range(1, len(pattern)):
                        try:
                            if _seg_part_can_end(
                                    block, pattern[:stop], folded):
                                state = (index + 1, stop)
                                if state not in seen:
                                    seen.add(state)
                                    stack.append(state)
                        except RecursionError:
                            continue
                    state = (index + 1, 0)
                    if state not in seen:
                        seen.add(state)
                        stack.append(state)
                else:
                    try:
                        if _seg_part_can_start(
                                block, pattern[matched:], folded):
                            return True
                    except RecursionError:
                        pass
                    for option in options[index]:
                        if option and pattern.startswith(
                                option, matched):
                            if matched + len(option) >= len(pattern):
                                return True
                            state = (index + 1, matched + len(option))
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    try:
                        if _seg_part_can_equal(block, "", folded):
                            state = (index + 1, matched)
                            if state not in seen:
                                seen.add(state)
                                stack.append(state)
                    except RecursionError:
                        pass
    return False


def _seg_payload_key(key, item_present):
    """Whether a key carrying an unordered container stands
    barred at the payload walk on its joined reading past the
    candidate bound: an anchor set marker or a real money
    marker tiled over the parts of the container in the plain
    reading or in the folded reading, or the amount and
    currency names tiled as two blocks over disjoint parts of
    the one container in either reading, in the joined pair
    form the walk states."""
    if _payload_spanning_barred(key, item_present):
        return True
    for node, parts in _seg_unordered_nodes(key):
        if _seg_multi_carrying(parts, "anchorset"):
            return True
        if item_present and (
                _seg_multi_carrying(parts, "realmoney")
                or _seg_multi_carrying(parts, "realmani")):
            return True
    for node, parts in _seg_unordered_nodes(key):
        plain_universe = _seg_universe(
            (), ("anchor_set", "real_money"))
        plain = _seg_plain_options(
            parts, plain_universe, _seg_prefixes(plain_universe))
        folded_universe = _seg_universe(
            (), ("anchorset", "realmoney", "realmani"))
        folded = _seg_folded_options(
            parts, folded_universe, _seg_prefixes(folded_universe))
        if _seg_tiles_carrying(plain, "anchor_set") is not None:
            return True
        if _seg_tiles_carrying(folded, "anchorset") is not None:
            return True
        if item_present:
            if _seg_tiles_carrying(plain, "real_money") is not None:
                return True
            if _seg_tiles_carrying(folded, "realmoney") is not None:
                return True
            if _seg_tiles_carrying(folded, "realmani") is not None:
                return True
        for options in (plain, folded):
            for first, second in (
                    ("amount", "currency"), ("currency", "amount")):
                block = _seg_tiles_carrying(options, first)
                if block is None:
                    continue
                rest = [
                    set() if (block >> i) & 1 else options[i]
                    for i in range(len(options))]
                if _seg_tiles_carrying(rest, second) is not None:
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



def _key_and_parts(key):
    """One key beside every part standing inside it, where the
    key stands in a container form: a container key stands
    judged by every part it carries, at any nesting, through
    base class readings, never through a string reading of
    the container itself. The walk stands iterative, so a
    key chain at any depth stands read on the same terms as
    the payload walk that carries it, and a container part
    already visited stands visited once. Beside the parts,
    the joined reading of each container in the key stands
    in the returned forms as one text: the stored text parts
    joined in order with no separator added, so a name split
    across the parts of one container key stands judged as
    the name it spells, under limb 3 of the Round 10
    settlement. The joined forms stand listed once per
    container, in stored order: the readings of an unordered
    container under its other orders stand judged by the
    segmentation acts of _seg_payload_key over its parts, in
    plain, folded, and multi reading spaces alike, and by
    _key_reads_as over its candidates, so no order of the
    parts stands listed here for the walk to enumerate."""
    forms = []
    seen = set()
    stack = [key]
    while stack:
        part = stack.pop()
        if isinstance(part, (dict, list, tuple, set, frozenset)):
            if id(part) in seen:
                continue
            seen.add(id(part))
            forms.append(part)
            if isinstance(part, dict):
                stack.extend(dict.keys(part))
            elif isinstance(part, list):
                stack.extend(list.__iter__(part))
            elif isinstance(part, tuple):
                stack.extend(tuple.__iter__(part))
            elif isinstance(part, frozenset):
                stack.extend(frozenset.__iter__(part))
            else:
                stack.extend(set.__iter__(part))
        else:
            forms.append(part)
    joined_seen = set()
    for form in list(forms):
        if isinstance(form, (dict, list, tuple, set, frozenset)):
            joined_forms = (_joined_stored_text(form),)
            for joined in joined_forms:
                if joined and joined not in joined_seen:
                    joined_seen.add(joined)
                    forms.append(joined)
    return forms


def _payload_carries_barred(value, _depth=0, _seen=None, _walked=None):
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
    same terms as nesting standing in a dict value. A container
    the walk has already answered clean carries that walked
    standing across every later path that reaches it, so a
    container shared by two siblings stands walked once for each
    depth at which it stands reached; the standing stands keyed
    by the container and the depth together, so a reach at a
    greater depth still stands judged at its own depth against
    the bound, and no standing earned inside a cycle or past the
    bound stands carried."""
    if not isinstance(value, (dict, list, tuple, set, frozenset)):
        return False
    if _walked is None:
        _walked = {}
    standing_key = (id(value), _depth)
    if standing_key in _walked:
        return False
    result = _payload_walk_barred(value, _depth, _seen, _walked)
    if not result:
        _walked[standing_key] = True
    return result


def _key_reading_stands_empty(text):
    """Whether one key reading stands empty in the walk folded
    forms: under some letter map the plain reading of the key,
    with digits dropped, stands empty, so on that map the key
    contributes no character to a joined folded reading. A
    separator only, space only, or dash only key folds to no
    reading at all on every map, and a digit only key folds to
    a reading its digits dropped form leaves empty on every
    map, so both forms stand empty here, as the sibling money
    walks read them. A key standing as a Cyrillic hard sign or
    soft sign, in either case, doubled, or mixed with a digit
    or a separator, stands empty here on the transliteration
    map, which records those signs with an empty reading and
    so reads the key as no character at all, while a key whose
    plain reading carries a letter on every map stands read
    on that letter."""
    for letter_map in (
        _HOMOGLYPH_MAP, _TRANSLITERATION_MAP,
        _HOMOGLYPH_MAP_VO, _TRANSLITERATION_MAP_VO,
    ):
        base = "".join(
            letter_map.get(character, character)
            for character in _decomposed_characters(text)
            if not unicodedata.category(character).startswith("M"))
        plain = "".join(
            character for character in base if character.isalnum())
        if not any(not character.isdigit() for character in plain):
            return True
    return False


def _dict_node_split_barred(value):
    """Whether a barred marker stands split across two or more
    keys of one dict, in the form settlement S-11 states: the
    dict node itself stands judged, in its stored key order,
    where an occurrence of the marker crosses a boundary
    between consecutive keys, the first key contributing a
    tail of one of its readings that stands as the opening of
    the marker, each middle key contributing one whole reading
    as an exact piece of it, and the last key contributing a
    reading that begins with its closing. A marker standing
    inside one key alone stands judged by the per key acts,
    never here. A key whose reading stands empty contributes
    no character to the joined reading, so an occurrence may
    cross such a key: the walk steps past a middle key on its
    empty reading, and that key stands unused by the
    occurrence. The money marker bars only where a value
    stands under every key the occurrence uses, as the walk
    states for a money name; the anchor marker bars on its
    reading alone, as the walk states for it."""
    pairs = list(dict.items(value))
    if len(pairs) < 2:
        return False
    texts = [_joined_stored_text(key) for key, item in pairs]
    spaces = []
    spaces.append((
        [{text.lower()} if text else {""} for text in texts],
        (("anchor_set", False), ("real_money", True))))
    folded_space = []
    for text in texts:
        readings = set(_folded_readings(text)) if text else {""}
        if text and _key_reading_stands_empty(text):
            readings.add("")
        folded_space.append(readings)
    spaces.append((
        folded_space,
        (("anchorset", False), ("realmoney", True),
         ("realmani", True))))
    for readings, patterns in spaces:
        for pattern, money in patterns:
            for start in range(len(pairs)):
                for reading in readings[start]:
                    if not reading:
                        continue
                    for cut in range(len(reading)):
                        piece = reading[cut:]
                        if not piece or len(piece) >= len(pattern):
                            continue
                        if piece != pattern[:len(piece)]:
                            continue
                        present = pairs[start][1] is not None
                        stack = [(start + 1, len(piece), present)]
                        while stack:
                            index, pos, ok = stack.pop()
                            if pos >= len(pattern):
                                if not money or ok:
                                    return True
                                continue
                            if index >= len(pairs):
                                continue
                            next_ok = ok and (
                                pairs[index][1] is not None)
                            for option in readings[index]:
                                if not option:
                                    stack.append((index + 1, pos, ok))
                                    continue
                                if option == pattern[pos:pos + len(option)]:
                                    stack.append((
                                        index + 1,
                                        pos + len(option), next_ok))
                                elif option.startswith(pattern[pos:]):
                                    if not money or next_ok:
                                        return True
    return False


def _dict_keys_tile_exact(readings, target):
    """Whether a run of two or more consecutive dict keys, in
    stored order, joins exactly to the target on one reading
    of each key it uses, in the joined reading form settlement
    S-14 states: the first key of the run contributes the
    opening piece, each later key one whole reading as the
    next piece, and a key whose reading stands empty may
    stand inside the run, stepped past on that empty reading
    and contributing no piece. A name standing inside one key
    alone stands judged by the per key acts, never here, so a
    run stands only on two or more pieces."""
    visited = set()
    stack = [(0, 0, 0)]
    while stack:
        index, pos, pieces = stack.pop()
        if pos == len(target):
            if pieces >= 2:
                return True
            continue
        if index >= len(readings):
            continue
        state = (index, pos, pieces >= 2)
        if state in visited:
            continue
        visited.add(state)
        if pieces == 0:
            stack.append((index + 1, 0, 0))
        for option in readings[index]:
            if not option:
                stack.append((index + 1, pos, pieces))
            elif option == target[pos:pos + len(option)]:
                stack.append((
                    index + 1, pos + len(option), pieces + 1))
    return False


def _dict_node_pair_barred(value):
    """Whether the amount and currency pair stands barred at
    the dict node itself, in the form settlement S-14 states:
    the walk frames the pair at dict level, across the keys of
    one dict together, so each name stands judged on the
    joined reading of the dict's keys in stored order, in the
    plain and folded forms in which the walk judges a single
    key, and a name split across two keys of the dict stands
    judged on that joined reading."""
    pairs = list(dict.items(value))
    if len(pairs) < 2:
        return False
    plain = []
    folded = []
    for key, item in pairs:
        text = _joined_stored_text(key)
        plain.append({text.lower()} if text else {""})
        readings = set(_folded_readings(text)) if text else set()
        if text and _key_reading_stands_empty(text):
            readings.add("")
        folded.append(readings if readings else {""})
    for target in ("amount", "currency"):
        if not (
            _dict_keys_tile_exact(plain, target)
            or _dict_keys_tile_exact(folded, target)
            or any(
                _key_reads_as(key, target) for key, item in pairs)
        ):
            return False
    return True


def _payload_walk_barred(value, _depth=0, _seen=None, _walked=None):
    """The walk behind _payload_carries_barred, carrying the
    path scoped seen set its cycle guard states and reaching its
    children through _payload_carries_barred, so each child
    stands answered under the walked standing that function
    carries across paths."""
    if isinstance(value, dict):
        if _depth > _PAYLOAD_DEPTH_BOUND:
            return True
        seen = set(_seen) if _seen is not None else set()
        if id(value) in seen:
            return True
        seen.add(id(value))
        if _dict_node_split_barred(value):
            return True
        all_keys = []
        for key in dict.keys(value):
            all_keys.extend(_key_and_parts(key))
        keys = {_stored_text(key).lower() for key in all_keys}
        if "amount" in keys and "currency" in keys:
            return True
        if (
            any(_key_reads_as(key, "amount") for key in all_keys)
            and any(_key_reads_as(key, "currency") for key in all_keys)
        ):
            return True
        if _dict_node_pair_barred(value):
            return True
        for key, item in dict.items(value):
            for key_form in _key_and_parts(key):
                lowered = _stored_text(key_form).lower()
                if "anchor_set" in lowered or (
                    "real_money" in lowered and item is not None
                ):
                    return True
                if _payload_folded_carries(
                        key_form, "anchorset") or (
                        item is not None
                        and _payload_folded_carries(
                            key_form, "realmoney")):
                    return True
            if isinstance(key, (dict, list, tuple, set, frozenset)):
                if _has_unordered_split(key):
                    joined_forms = _joined_text_candidates(key)
                else:
                    joined_forms = (_joined_stored_text(key),)
                if not _has_unordered_split(key) or \
                        _payload_pair_can_stand(key):
                    for joined in joined_forms:
                        if joined:
                            lowered_joined = joined.lower()
                            if (
                                "amount" in lowered_joined
                                and "currency" in lowered_joined
                            ):
                                return True
                            if _payload_folded_carries_pair(
                                    joined, "amount", "currency"):
                                return True
            if _seg_payload_key(key, item is not None):
                return True
            if _payload_carries_barred(key, _depth + 1, seen, _walked):
                return True
            if _payload_carries_barred(item, _depth + 1, seen, _walked):
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
            _payload_carries_barred(item, _depth + 1, seen, _walked)
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
            _payload_carries_barred(item, _depth + 1, seen, _walked)
            for item in base_iter(value))
    return False


def _namer_key_text(key):
    """The text a key stores for the item namer, read through
    _stored_text where the key stands in a text or buffer
    form, so a string reading the key itself supplies, lying
    or raising, never stands as the name, and through
    _refusal_text for a key in any other form, whose string
    reading stands guarded there against every exception."""
    if isinstance(key, (str, bytes, bytearray, memoryview)):
        return _stored_text(key)
    return _refusal_text(key)


def _dict_node_actual_barred(value):
    """Whether one dict node itself carries a barred form on
    its own judgements, in the local form _payload_walk_barred
    states for a dict node, without the walk cycle and depth
    readings: the split and pair node acts, the per key plain
    and folded readings, the container key joined readings,
    and the spanning act. A node standing barred only through
    a child stands judged at that child, not here."""
    if _dict_node_split_barred(value):
        return True
    all_keys = []
    for key in dict.keys(value):
        all_keys.extend(_key_and_parts(key))
    keys = {_stored_text(key).lower() for key in all_keys}
    if "amount" in keys and "currency" in keys:
        return True
    if (
        any(_key_reads_as(key, "amount") for key in all_keys)
        and any(_key_reads_as(key, "currency") for key in all_keys)
    ):
        return True
    if _dict_node_pair_barred(value):
        return True
    for key, item in dict.items(value):
        for key_form in _key_and_parts(key):
            lowered = _stored_text(key_form).lower()
            if "anchor_set" in lowered or (
                "real_money" in lowered and item is not None
            ):
                return True
            if _payload_folded_carries(
                    key_form, "anchorset") or (
                    item is not None
                    and _payload_folded_carries(
                        key_form, "realmoney")):
                return True
        if isinstance(key, (dict, list, tuple, set, frozenset)):
            if _has_unordered_split(key):
                joined_forms = _joined_text_candidates(key)
            else:
                joined_forms = (_joined_stored_text(key),)
            if not _has_unordered_split(key) or \
                    _payload_pair_can_stand(key):
                for joined in joined_forms:
                    if joined:
                        lowered_joined = joined.lower()
                        if (
                            "amount" in lowered_joined
                            and "currency" in lowered_joined
                        ):
                            return True
                        if _payload_folded_carries_pair(
                                joined, "amount", "currency"):
                            return True
        if _seg_payload_key(key, item is not None):
            return True
    return False


def _payload_contains_barred_content(payload):
    """Whether a payload carries a barred form on a judgement
    of its contents, as distinct from the walk readings that
    read a payload past the depth bound, and a payload that
    revisits a container on its own path, as barred. The
    traversal stands iterative, path scoped against cycles,
    and bounded in depth at 1000 containers, past which no
    content judgement stands taken by this act."""
    stack = [(payload, 0, frozenset())]
    while stack:
        value, depth, seen = stack.pop()
        if depth > 1000:
            continue
        if not isinstance(
                value, (dict, list, tuple, set, frozenset)):
            continue
        if id(value) in seen:
            continue
        seen = seen | {id(value)}
        if isinstance(value, dict):
            if _dict_node_actual_barred(value):
                return True
            for key, item in dict.items(value):
                stack.append((item, depth + 1, seen))
                stack.append((key, depth + 1, seen))
        else:
            base_iter = (
                list.__iter__ if isinstance(value, list)
                else tuple.__iter__ if isinstance(value, tuple)
                else frozenset.__iter__
                if isinstance(value, frozenset)
                else set.__iter__)
            for item in base_iter(value):
                stack.append((item, depth + 1, seen))
    return False


def _payload_children(value):
    """The children of one container, read through base
    class operations: a dict contributes its keys and its
    values in stored order, and every other container its
    elements in its base iteration order."""
    if isinstance(value, dict):
        children = []
        for key, item in dict.items(value):
            children.append(key)
            children.append(item)
        return children
    if isinstance(value, list):
        return list(list.__iter__(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    return list(set.__iter__(value))


def _payload_revisits_container(value):
    """Whether a payload revisits a container on its own
    path, in the cycle form _payload_carries_barred states,
    judged on an iterative path scoped traversal of its
    own, so a container chain at any depth stands answered
    and no recursion stands spent per container level."""
    if not isinstance(value, (dict, list, tuple, set, frozenset)):
        return False
    seen = set()
    stack = [(value, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            seen.discard(id(node))
            continue
        if not isinstance(
                node, (dict, list, tuple, set, frozenset)):
            continue
        if id(node) in seen:
            return True
        seen.add(id(node))
        stack.append((node, True))
        for child in _payload_children(node):
            stack.append((child, False))
    return False


def _payload_past_depth_bound(value):
    """Whether a container of a payload stands at a depth
    past the stated bound, in the counting _payload_walk_
    barred states: the top container stands at depth 0, each
    child container one deeper, and a container standing at
    a depth greater than _PAYLOAD_DEPTH_BOUND stands past
    the bound. A part shared on different paths stands read
    on each path, as the walk reads it. The traversal stands
    iterative and path scoped, so a container chain at any
    depth stands answered."""
    if not isinstance(value, (dict, list, tuple, set, frozenset)):
        return False
    seen = set()
    stack = [(value, 0, False)]
    while stack:
        node, depth, leaving = stack.pop()
        if leaving:
            seen.discard(id(node))
            continue
        if not isinstance(
                node, (dict, list, tuple, set, frozenset)):
            continue
        if depth > _PAYLOAD_DEPTH_BOUND:
            return True
        if id(node) in seen:
            continue
        seen.add(id(node))
        stack.append((node, depth, True))
        for child in _payload_children(node):
            stack.append((child, depth + 1, False))
    return False


def _barred_payload_item(payload):
    found = []
    stack = [(payload, 0, frozenset())]
    while stack:
        value, depth, seen = stack.pop()
        if depth > 1000:
            continue
        if isinstance(value, dict):
            if id(value) in seen:
                continue
            seen = seen | {id(value)}
            keys = [_namer_key_text(key) for key in dict.keys(value)]
            lowered = [key.lower() for key in keys]
            if "amount" in lowered and "currency" in lowered:
                found.append("an amount and currency pair")
            if _dict_node_pair_barred(value):
                found.append("an amount and currency pair")
            joined_text = "".join(
                _joined_stored_text(key) for key in dict.keys(value))
            for key, item in dict.items(value):
                text = _namer_key_text(key).lower().replace(" ", "_")
                if "anchor_set" in text:
                    found.append("a supplied anchor set (anchor_set)")
                if "real_money" in text and item is not None:
                    found.append(
                        "a real money value (real_money_value)")
                for key_form in _key_and_parts(key):
                    if _payload_folded_carries(key_form, "anchorset"):
                        found.append(
                            "a supplied anchor set (anchor_set)")
                    if item is not None and _payload_folded_carries(
                            key_form, "realmoney"):
                        found.append(
                            "a real money value (real_money_value)")
                stack.append((item, depth + 1, seen))
                stack.append((key, depth + 1, seen))
            joined_lowered = joined_text.lower().replace(" ", "_")
            if "anchor_set" in joined_lowered:
                found.append("a supplied anchor set (anchor_set)")
            if "real_money" in joined_lowered and any(
                    item is not None for item in dict.values(value)):
                found.append("a real money value (real_money_value)")
            for reading in _folded_readings(joined_text):
                if "anchorset" in reading:
                    found.append("a supplied anchor set (anchor_set)")
                if "realmoney" in reading and any(
                        item is not None
                        for item in dict.values(value)):
                    found.append(
                        "a real money value (real_money_value)")
        elif isinstance(value, (list, tuple, set, frozenset)):
            if id(value) in seen:
                continue
            seen = seen | {id(value)}
            for item in value:
                stack.append((item, depth + 1, seen))
    return found[0] if found else "a barred value"


def escrow_result(kind, variant="B-4", payload=None, contract_state=None):
    """One escrow bearing result. Every such result carries the
    core only qualifier reading true, the K1 and L2 state carriage
    Shape 9 requires, and the verification limit statement."""
    if not _base_member(variant, ("B-3", "B-4")):
        raise ValueError(
            "escrow_result stands refused: the escrow variant stands outside the B-3 and B-4 set: "
            + _sentence_text(variant) + ", and no escrow result stands returned")
    if _payload_carries_barred(payload):
        if not _payload_contains_barred_content(payload):
            if _payload_revisits_container(payload):
                raise ValueError(
                    "escrow_result stands refused: the payload revisits a container on its own path, so it stands read as barred on its cycle ground alone, a payload carries no real money value and no supplied anchor set, and no escrow result stands returned")
            raise ValueError(
                "escrow_result stands refused: the payload stands past the stated depth bound of 100, so it stands read as barred on its depth bound ground alone, a payload carries no real money value and no supplied anchor set, and no escrow result stands returned")
        raise ValueError(
            "escrow_result stands refused: the payload carries a barred value, "
            + _barred_payload_item(payload)
            + ", a payload carries no real money value and no supplied anchor set, and no escrow result stands returned")
    state = contract_state if isinstance(contract_state, dict) else {}
    return {
        "kind": _undirected_copy(kind),
        "variant": variant,
        "core_only_qualifier": True,
        "payload": _undirected_copy(payload),
        "k1_and_l2_state": _undirected_copy(dict.get(state, "k1_and_l2_state", "carried; value set open at OP-21 G-10")),
        "lien_state": _undirected_copy(dict.get(state, "lien_state")),
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
        raise ValueError(
            "escrow_contract_state stands refused: the escrow variant "
            "stands outside the B-3 and B-4 set: " + _sentence_text(variant)
            + ", and no escrow contract state stands returned")
    if not _base_member(lien_state, mod01.LIEN_STATES):
        raise ValueError(
            "escrow_contract_state stands refused: the lien state "
            "stands outside the closed four value set: " + _sentence_text(lien_state)
            + ", and no escrow contract state stands returned")
    state = {
        "contract_identifier": _undirected_copy(contract_identifier),
        "pair_identifiers": _undirected_copy(pair_identifiers),
        "standard_or_profile_identifier": _undirected_copy(standard_or_profile_identifier),
        "variant": variant,
        "lien_state": lien_state,
        "estimated_cost_value": _undirected_copy(estimated_cost_value),
        "pause_state": _undirected_copy(pause_state),
        "pause_cap_value": _undirected_copy(pause_cap_value) if pause_cap_value is not None else pause_cap(variant)["per_variant_pause_value"],
        "k1_and_l2_state": "carried; value set open at OP-21 G-10",
        "lost_contact_clause_on": bool(lost_contact_clause_on),
    }
    if lost_contact_clause_on:
        state["lost_contact_clock_state"] = "contact clocks tracked"
        state["lost_contact_window_n"] = _undirected_copy(window_n)
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
    if not _base_member(dict.get(result, "variant", "B-4"), ("B-3", "B-4")):
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
    if isinstance(context, dict):
        context = {key: item for key, item in dict.items(context)}
    else:
        context = {}
    stored_name = _stored_text(name)
    name_is_text = isinstance(
        name, (str, bytes, bytearray, memoryview))
    judged_name = stored_name if name_is_text else None
    name_text = stored_name if name_is_text else _refusal_text(name)
    if context.get("claims_dq_answer") or context.get("dq_answer") is not None:
        raise GuessedAnswer("no case encodes a guess at any DQ-5 to DQ-30 item, and no instruction stands run")
    if context.get("asserts_floor_under_n") or context.get("asserts_clock_scope_as_answer"):
        raise GuessedAnswer("no floor under N and no clock scope reading stands as a DQ answer, and no instruction stands run")
    if (
        "pool" in stored_name
        or _base_member(judged_name, (EXCLUDED_PROFILE,))
        or _base_member(context.get("profile"), (EXCLUDED_PROFILE,))
        or _reads_as_excluded_profile(name)
        or _reads_as_excluded_profile(context.get("profile"))
    ):
        raise ExcludedSubpath("a construction excluded on a DQ ground stays excluded on that ground: " + name_text)
    if judged_name is None or judged_name not in _ALLOWED:
        raise UnnamedInstruction("instruction stands unnamed in the cited set of 12 core instructions, with no exercised case standing for it: " + name_text + ", and no instruction stands run")
    item = _ALLOWED[judged_name].split(",")[0]
    result_payload = {"instruction": judged_name, "dq_item": _ALLOWED[judged_name]}
    result_payload["contested_entries"] = contested_entries_for(item)
    result_payload["claims_dq_answer"] = False
    result_payload["traversal_claim"] = None
    if judged_name == "replace_backup_key":
        if not context.get("backup_key_registered_at_setup"):
            raise ValueError("refused: replace_backup_key stands refused, because it runs only with backup key registration at setup, and no key stands replaced")
        result_payload["backup_key_registered_at_setup"] = True
    if judged_name == "open_request":
        additions = [key for key in ("countersigning", "bound", "verification") if context.get(key)]
        if additions:
            raise ValueError(
                "open_request stands refused: the addition "
                + " and ".join(additions)
                + " stands added, open_request runs with no countersigning, bound or verification added, and no request stands opened")
        stated = context.get("stated_cost")
        true = context.get("true_cost")
        if stated is None or true is None:
            missing = []
            if stated is None:
                missing.append("the stated cost")
            if true is None:
                missing.append("the true cost")
            raise ValueError(
                "open_request stands refused: "
                + " and ".join(missing)
                + " stands missing, and no request stands opened")
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
    if judged_name in ("check_in", "claim_lost_contact"):
        if not context.get("clause_on"):
            raise ValueError(
                judged_name + " stands refused: the clause_on context stands missing, "
                + judged_name + " runs only for a contract that turns the clause on, and no "
                + judged_name + " stands performed")
        if context.get("window_n") is None:
            raise ValueError(
                judged_name + " stands refused: the window value N stands missing, no window value was handed for the contract, and no "
                + judged_name + " stands performed")
        result_payload["window_n"] = context["window_n"]
        result_payload["window_n_form"] = "labelled assumption in the standard for that contract"
        result_payload["contact_clocks_tracked"] = True
    return escrow_result(judged_name, variant=variant, payload=result_payload)


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
        raise ValueError("the pause cap stands refused in named form for an unknown variant: " + _sentence_text(variant))
    if variant == "B-4":
        return {
            "variant": "B-4",
            "per_variant_pause_value": dict(PAUSE_CAP_B4),
            "extension_percent": 300,
            "total_percent": 400,
        }
    return {
        "variant": variant,
        "per_variant_pause_value": _undirected_copy(stated_value),
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
    value = dict.get(result, "per_variant_pause_value")
    if value is None:
        payload = dict.get(result, "payload")
        if isinstance(payload, dict):
            value = dict.get(payload, "per_variant_pause_value")
    if value is None:
        return False
    variant = dict.get(result, "variant")
    if variant is None and isinstance(dict.get(result, "payload"), dict):
        variant = dict.get(dict.get(result, "payload"), "variant")
    if variant == "B-4":
        if not isinstance(value, dict):
            return False
        return (dict.get(value, "extension_percent") == PAUSE_CAP_B4["extension_percent"]
                and dict.get(value, "total_percent") == PAUSE_CAP_B4["total_percent"])
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
    if dict.get(arm_a, "variant") == dict.get(arm_b, "variant"):
        return False
    shared_keys = ("inputs", "society", "parameters", "seeds")
    for key in shared_keys:
        if dict.__contains__(arm_a, key) or dict.__contains__(arm_b, key):
            if dict.get(arm_a, key) != dict.get(arm_b, key):
                return False
    for arm in (arm_a, arm_b):
        for result in dict.get(arm, "results", ()):
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
    entries = dict.get(record, "entries")
    if not entries:
        return False
    if isinstance(entries, list):
        entries = list(list.__iter__(entries))
    elif isinstance(entries, tuple):
        entries = list(tuple.__iter__(entries))
    for entry in entries:
        if not isinstance(entry, dict):
            return False
        if dict.get(entry, "filled_by_inference"):
            return False
        if not dict.get(entry, "checked_by_independent_reader"):
            return False
        if not dict.get(entry, "ruling"):
            return False
    return True


def report_difference(difference, folding_record=None):
    """No B-5 difference is reported as a ruling effect until the
    folding stands recorded in the form validate_folding_record
    states. A difference with no such record stands reported as
    an unfolded difference only, in no ruling effect wording."""
    if folding_record is not None and validate_folding_record(folding_record):
        return {
            "difference": _undirected_copy(difference),
            "reported_as": "ruling effect",
            "ruling_effect_wording": True,
            "folding_record": _undirected_copy(folding_record),
        }
    return {
        "difference": _undirected_copy(difference),
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
    rows = list(_base_iter(rows)) if isinstance(rows, (list, tuple, set, frozenset)) else []
    if len(rows) != 26:
        return False
    expected = {row["item"]: row["standing"] for row in dq_arrival_table()}
    seen = [dict.get(row, "item") for row in rows if isinstance(row, dict)]
    if len(set(seen)) != 26 or set(seen) != set(expected):
        return False
    for row in rows:
        if not isinstance(row, dict):
            return False
        if dict.get(expected, dict.get(row, "item")) != dict.get(row, "standing"):
            return False
        if dict.get(row, "final_column") not in ("", None):
            return False
    return True


def enter_ruling(rows, item, ruling_text):
    """Enter a ruling in the final column of its row, verbatim,
    when the ruling for that item arrives."""
    updated = _undirected_copy(rows)
    for row in updated:
        if row.get("item") == item:
            row["final_column"] = ruling_text
    return updated

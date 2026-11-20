"""MOD-03, Society Generator and archetype generators.

Tracer form of the slice core. The module builds the cast for one run
from archetype records: population, archetype mix, farm construction,
and the initial graph, delivered in full before day one. After that
point it delivers nothing into the run except behaviour through the
behaviour streams.

The generator holds no rule state. It proposes actions, and the rule
cores decide what the actions do. Archetype behaviour stands as one
generator driven by an archetype record, with only archetype
behaviour stated in the record. The strategy class for a run is fixed
in advance and stated on the cast record. Ground truth labels travel
in the cast for scoring only and stand in no detection input and no
adjudication input this module forms.

Cast construction takes stream state passed in as values. This
module imports no seed or stream engine and no generator from any
other module, adopted or not.
"""

import itertools
import unicodedata

from crucible import mod01 as _mod01

DQ163_MARK = _mod01.DQ163_MARK
CATALOGUE_STANDING = "open at OP-11"
OP11_GAPS = (
    "honest adaptive rewiring",
    "a targeted linking adversary parameter",
    "adaptive sleeper concealment",
)
CANONICAL_SCALE_SET = (
    {"population": 200, "provenance_label": "estimated"},
    {"population": 400, "provenance_label": "estimated"},
    {"population": 800, "provenance_label": "estimated"},
)
COLD_SOCIETY_PROVENANCE = "derived over estimated rates"
COLD_SOCIETY_FIRST_DAYS = 90
GROUND_TRUTH_FIELDS = (
    "ground_truth",
    "ground_truth_label",
    "honest_or_farm_membership",
    "membership",
    "membership_ground_truth",
)
RULE_STATE_FIELDS = (
    "reputation",
    "reputation_score",
    "band",
    "stake_held",
    "contract_effect",
    "lien_state",
    "decided_effect",
)
BARRED_PROJECTION_KEYS = frozenset([
    "ground_truth", "ground_truth_field", "membership",
    "honest_membership", "farm_membership", "is_honest", "is_farm",
    "canary", "canary_value", "membership_value", "sleeper",
    "ground_truth_label", "label",
])

_BARRED_KEY_PARTS = (
    "membership",
    "ground_truth",
    "groundtruth",
    "canary",
)

_HOMOGLYPH_MAP = {
    "а": "a", "с": "c", "е": "e", "о": "o",
    "р": "p", "х": "x", "у": "y", "і": "i",
    "й": "i",
    "ј": "j", "ѕ": "s", "һ": "h", "к": "k",
    "м": "m", "н": "h", "т": "t", "в": "b",
    "α": "a", "β": "b", "ε": "e", "ι": "i",
    "κ": "k", "μ": "m", "ο": "o", "ρ": "p",
    "τ": "t", "χ": "x", "υ": "u", "ν": "n",
    "γ": "g", "δ": "d", "λ": "l", "σ": "s",
    "ω": "w", "ζ": "z", "θ": "t", "φ": "f",
    "η": "e",
    "э": "e", "л": "l", "ф": "f", "ш": "sh", "ψ": "ps",
    "ъ": "", "ь": "",
    "æ": "ae", "œ": "oe", "ø": "o", "đ": "d",
    "ł": "l", "ß": "ss", "þ": "th", "ð": "d",
    "ħ": "h", "ŋ": "n", "ƒ": "f", "ı": "i",
    "ŧ": "t",
    "Æ": "ae", "Œ": "oe", "Ø": "o", "Đ": "d",
    "Ł": "l", "ẞ": "ss", "Þ": "th", "Ð": "d",
    "Ħ": "h", "Ŋ": "n", "Ƒ": "f", "Ŧ": "t",
}
for _upper, _lower in list(_HOMOGLYPH_MAP.items()):
    _HOMOGLYPH_MAP[_upper.upper()] = _lower

# The wider barred reading set, in its own map beside the
# shared homoglyph map above: the letter classes the MOD-10
# surfaces carry in their transliteration and symbol maps,
# stated at MOD-10 for the transliteration letters, the
# small capital and phonetic Latin letters, the Armenian
# letters, and the extra symbol classes, together with the
# two letters the R1-009 cure added at MOD-10. These readings
# feed the folded barred reading of this module, so the
# barred reading of this module reads the wider set, while
# the shared homoglyph map above stands as the parity map
# its sister surfaces stand on.
_WIDER_READING_MAP = {
    "б": "b", "г": "g", "д": "d", "и": "i",
    "п": "p",
    "ё": "e", "ђ": "s", "ѓ": "h",
    "ς": "s",
    "օ": "o", "Օ": "o", "ւ": "n", "Ո": "n",
    "ᴀ": "a", "ʙ": "b", "ᴄ": "c", "ᴅ": "d",
    "ᴇ": "e", "ꜰ": "f", "ɢ": "g", "ʜ": "h",
    "ɪ": "i", "ᴊ": "j", "ᴋ": "k", "ʟ": "l",
    "ᴍ": "m", "ɴ": "n", "ᴏ": "o", "ᴘ": "p",
    "ꞯ": "q", "ʀ": "r", "ꜱ": "s", "ᴛ": "t",
    "ᴜ": "u", "ᴠ": "v", "ᴡ": "w", "ʏ": "y",
    "ᴢ": "z",
    "€": "e", "£": "l", "!": "l", "|": "l",
    "¥": "y",
    "¢": "c", "§": "s", "+": "t",
    "Ꮢ": "r", "Ꮼ": "e", "Ꭺ": "a", "Ꮮ": "l",
    "Ꮟ": "m", "Ᏸ": "o", "Ꮑ": "n", "Ꮿ": "y",
    "ꪖ": "r", "ꫜ": "e", "ꪊ": "a", "ꪮ": "l",
    "ꪇ": "m", "ꪎ": "o", "ꪑ": "n", "꪿": "y",
    "ⲣ": "r", "ⲉ": "e", "ⲁ": "a", "ⲗ": "l",
    "ⲙ": "m", "ⲟ": "o", "ⲛ": "n", "ⲩ": "y",
}
# Transcription repair, stated in the open: fifteen entries of
# the wider map above stand keyed in this copy by a neighbouring
# codepoint in place of the codepoint the merged tree records.
# Each entry stands moved here to its recorded codepoint, by
# number, before the uppercase pass below runs, so the map this
# copy builds is the map the merged tree builds.
for _recorded, _reading, _neighbour in (
        (0x0493, "h", 0x0453), (0x0578, "n", 0x0552),
        (0x0548, "n", 0x0582), (0x13AC, "e", 0x13EC),
        (0x13B7, "m", 0x13CF), (0x13BE, "o", 0x13F0),
        (0xABA2, "r", 0xAA96), (0xAB7C, "e", 0xAADC),
        (0xAB7A, "a", 0xAA8A), (0xABAE, "l", 0xAAAE),
        (0xAB87, "m", 0xAA87), (0xAB8E, "o", 0xAA8E),
        (0xAB91, "n", 0xAA91), (0xABBF, "y", 0xAABF)):
    _WIDER_READING_MAP.pop(chr(_neighbour), None)
    _WIDER_READING_MAP[chr(_recorded)] = _reading
for _upper, _lower in list(_WIDER_READING_MAP.items()):
    _WIDER_READING_MAP[_upper.upper()] = _lower

_WIDE_LETTER_MAP = dict(_HOMOGLYPH_MAP)
_WIDE_LETTER_MAP.update(_WIDER_READING_MAP)

# The transliteration reading of the letters whose rendered
# form reads as a different Latin letter: the wider reading
# set the MOD-10 surfaces carry, where a letter stands read
# both as the letter it resembles and as the letter it
# transliterates. These readings stand beside the homoglyph
# reading above, never in place of it.
_TRANSLITERATION_OVERRIDES = {
    "р": "r", "х": "h", "в": "v", "с": "s",
    "н": "n", "у": "u", "й": "y",
    "η": "e", "π": "p", "χ": "h", "ρ": "r",
    "ω": "o", "υ": "y", "φ": "ph",
    "θ": "th", "ы": "y", "ю": "yu", "я": "ya",
}
_ALT_LETTER_MAP = dict(_WIDE_LETTER_MAP)
_ALT_LETTER_MAP.update(_TRANSLITERATION_OVERRIDES)
for _upper, _lower in list(_TRANSLITERATION_OVERRIDES.items()):
    _ALT_LETTER_MAP[_upper.upper()] = _lower

_DROPPED_INVISIBLE = frozenset(
    ["​", "‌", "‍", "﻿", "­", "⁠"])

_LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "@": "a", "$": "s",
    "€": "e", "£": "l", "!": "l", "|": "l",
    "¥": "y", "¢": "c", "§": "s", "+": "t",
}


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
    bytes form keeps the standing its stored name carries.
    A bytearray value and a memoryview value stand judged
    the same way, on the bytes they store or view, decoded
    as UTF-8 with undecodable bytes dropped, in the form
    the condition and passage limbs already use."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    if isinstance(value, (bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


def _refusal_repr(value):
    """Render a handed value for a refusal sentence: through
    its repr reading where that reading stands, and through
    the base object repr where the repr reading the value
    itself supplies raises, so the refusal stands as a full
    named refusal and never escapes bare on that reading."""
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
    """Render a handed value for a refusal sentence on the
    text it stores, where the value stands in a text or
    buffer form, through the module stored text reading at
    _stored_text, so a string reading the value itself
    supplies, lying or raising, never stands as the name
    the sentence delivers. A value in any other form
    stands rendered through _safe_str, as before."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    return _safe_str(value)


def _path_key_text(key):
    """The text a walk path names a dict key by: the stored text
    of a text or buffer form key, read through _stored_text, and
    any other form through _safe_str, so a key whose string
    reading raises or lies never directs the path building and
    no walk escapes bare on that reading."""
    if isinstance(key, (str, bytes, bytearray, memoryview)):
        return _stored_text(key)
    return _safe_str(key)


def _canonical_text(key, letter_map=None):
    mapping = _HOMOGLYPH_MAP if letter_map is None else letter_map
    chars = []
    for character in _stored_text(key):
        if character.casefold() == "й":
            # Cyrillic short i stands read as a whole letter,
            # never reduced by compatibility decomposition to
            # Cyrillic i plus a combining mark before any letter
            # map reads it, so each map records its own reading
            # of the letter: i in the homoglyph and wide maps
            # and y in the alternate map.
            chars.append(mapping.get(
                character,
                mapping.get("й", mapping.get("Й", "i"))))
            continue
        decomposed = unicodedata.normalize("NFKD", character)
        for part in decomposed:
            if part in _DROPPED_INVISIBLE:
                continue
            if unicodedata.category(part).startswith("M"):
                continue
            chars.append(mapping.get(part, part))
    return "".join(chars).casefold()


def _readings_for(canonical):
    letters_only = "".join(
        character for character in canonical if character.isalpha())
    leet_read = "".join(
        _LEET_MAP.get(character, character) for character in canonical)
    leet_letters = "".join(
        character for character in leet_read if character.isalpha())
    leet_l_read = "".join(
        "l" if character == "1" else _LEET_MAP.get(character, character)
        for character in canonical)
    leet_l_letters = "".join(
        character for character in leet_l_read if character.isalpha())
    return (letters_only, leet_letters, leet_l_letters)


def _folded_readings(key):
    readings = list(_readings_for(_canonical_text(key, _WIDE_LETTER_MAP)))
    for reading in _readings_for(_canonical_text(key)):
        if reading not in readings:
            readings.append(reading)
    for reading in _readings_for(_canonical_text(key, _ALT_LETTER_MAP)):
        if reading not in readings:
            readings.append(reading)
    # The counting basis for the 4096 combined text bound is one
    # basis at every surface: the number of distinct combined
    # texts built position by position over the original
    # characters of the key, each original character contributing
    # the set of its distinct readings across the letter maps.
    # Cyrillic short i contributes two readings on that basis, i
    # and y, and Greek chi contributes two, x and h, so a key
    # stands inside or past the bound alike at MOD-03, MOD-04,
    # MOD-05, and MOD-10.
    texts = {""}
    overflow = False
    for character in _stored_text(key):
        options = set()
        for letter_map in (
                _WIDE_LETTER_MAP, _HOMOGLYPH_MAP, _ALT_LETTER_MAP):
            options.add(_canonical_text(character, letter_map))
        expanded = set()
        for prefix in texts:
            for option in options:
                expanded.add(prefix + option)
        if len(expanded) > 4096:
            overflow = True
            break
        texts = expanded
    if not overflow:
        for text in texts:
            for reading in _readings_for(text):
                if reading not in readings:
                    readings.append(reading)
    return tuple(readings)


def _fold_name(name):
    return "".join(
        character for character in name if character.isalpha())


_BARRED_EXACT_FOLDED = frozenset(
    _fold_name(name)
    for name in tuple(GROUND_TRUTH_FIELDS) + tuple(BARRED_PROJECTION_KEYS)
)
_BARRED_PARTS_FOLDED = frozenset(
    _fold_name(part) for part in _BARRED_KEY_PARTS)


def _character_variants(character):
    """Every folded form one original character can contribute
    to a combined reading: each of its readings across the
    letter maps, taken under the readings _readings_for states,
    as the combination limb of _folded_readings builds them."""
    variants = set()
    for letter_map in (
            _WIDE_LETTER_MAP, _HOMOGLYPH_MAP, _ALT_LETTER_MAP):
        variants.update(
            _readings_for(_canonical_text(character, letter_map)))
    return variants


def _combined_matches_exact(variant_sets, target):
    states = {0}
    for variants in variant_sets:
        following = set()
        for state in states:
            for variant in variants:
                if target.startswith(variant, state):
                    following.add(state + len(variant))
        states = following
        if not states:
            return False
    return len(target) in states


def _combined_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _combined_carries(variant_sets, pattern):
    full = len(pattern)
    states = {0}
    for variants in variant_sets:
        following = set()
        for state in states:
            for variant in variants:
                current = state
                for character in variant:
                    if current == full:
                        break
                    current = _combined_prefix_state(
                        pattern, current, character)
                following.add(current)
        if full in following:
            return True
        states = following
    return full in states


def _combined_key_barred(key):
    """Whether any combined reading of the key stands barred,
    judged position by position over the per character variants
    without enumerating the combined texts, so the judgement
    stands the same inside the 4096 combined text bound and
    past it, in the form the MOD-05 read takes. The forms
    judged are the forms _is_barred_key judges on an enumerated
    reading: a reading standing in the folded exact set of the
    barred keys, and a reading carrying a folded barred part."""
    variant_sets = [
        _character_variants(character) for character in _stored_text(key)
    ]
    for target in _BARRED_EXACT_FOLDED:
        if _combined_matches_exact(variant_sets, target):
            return True
    for part in _BARRED_PARTS_FOLDED:
        if _combined_carries(variant_sets, part):
            return True
    return False



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
            tuple(GROUND_TRUTH_FIELDS) + tuple(BARRED_PROJECTION_KEYS),
            _BARRED_KEY_PARTS)
        plain = _seg_plain_options(
            parts, plain_universe, _seg_prefixes(plain_universe))
        for target in tuple(GROUND_TRUTH_FIELDS) + tuple(BARRED_PROJECTION_KEYS):
            if _seg_tiles_exact(plain, target):
                return True
        for pattern in tuple(_BARRED_KEY_PARTS):
            if _seg_tiles_carrying(plain, pattern) is not None:
                return True
        for pattern in tuple(_BARRED_KEY_PARTS):
            if _seg_parts_carry_edge(parts, plain, pattern, False):
                return True
        folded_universe = _seg_universe(
            _BARRED_EXACT_FOLDED, _BARRED_PARTS_FOLDED)
        folded = _seg_folded_options(
            parts, folded_universe, _seg_prefixes(folded_universe))
        for target in tuple(_BARRED_EXACT_FOLDED):
            if _seg_tiles_exact(folded, target):
                return True
        for pattern in tuple(_BARRED_PARTS_FOLDED):
            if _seg_tiles_carrying(folded, pattern) is not None:
                return True
        for pattern in tuple(_BARRED_PARTS_FOLDED):
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



def _is_barred_key(key):
    """Return whether a key stands barred under the standing vocabulary.

    The vocabulary is the one the projection applies one module
    away: the thirteen projection names, beside the ground truth
    names this module has always barred, with substring matching
    on the membership, ground truth, and canary parts, so
    capitalised and variant forms stand barred as well. The key
    stands read through the folded reading stated for the barred
    surfaces: compatibility decomposition with combining marks
    dropped, invisible characters dropped, non Latin homoglyph
    letters mapped to their Latin forms, case folded, and every
    separator or digit standing inside a word dropped, with a
    second reading in which digit and symbol substitutions stand
    mapped to the letters they replace. A name that stands barred
    only in its exact form stays exact in the folded reading, so
    a name carrying extra letters beside it reads as a different
    name, as before.
    """
    if isinstance(key, (dict, list, tuple, set, frozenset)):
        # A container key stands barred where a part it stores
        # stands barred on its own stored text at any depth,
        # where the stored text parts of one container joined
        # in order, with no separator added, spell a barred
        # name, and where a single part container carries the
        # reading of its one part, in the joined reading the
        # MOD-04 barred key text states. The walk is a post
        # order walk on an explicit stack of frames, never a
        # recursion on each part, so a key nested to depth
        # 2000 still answers both ways. Joined readings stand
        # cached by their text inside one walk, so a deep
        # chain of single part containers does not rejudge
        # the same joined text at every level.
        joined_cache = {}

        def scalar_barred(text):
            if text not in joined_cache:
                joined_cache[text] = _is_barred_key(text)
            return joined_cache[text]

        def container_items(container):
            if isinstance(container, dict):
                return list(dict.keys(container))
            return list(_base_iter(container))

        active = set()
        frames = []

        def push(container):
            frames.append(
                [id(container), container_items(container),
                 0, [], False])
            active.add(id(container))

        push(key)
        result = False
        while frames:
            frame = frames[-1]
            container_id, items, index, joined_parts, barred = frame
            if index < len(items):
                frame[2] = index + 1
                part = items[index]
                if isinstance(
                        part, (dict, list, tuple, set, frozenset)):
                    if id(part) in active:
                        continue
                    push(part)
                else:
                    if _is_barred_key(part):
                        frame[4] = True
                    joined_parts.append(_stored_text(part))
            else:
                joined = "".join(joined_parts)
                barred_here = barred or (
                    bool(joined) and scalar_barred(joined))
                frames.pop()
                active.discard(container_id)
                if frames:
                    parent = frames[-1]
                    parent[3].append(joined)
                    if barred_here:
                        parent[4] = True
                else:
                    result = barred_here
        if not result and _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and scalar_barred(candidate):
                    return True
        if not result and _seg_unordered_barred(key):
            return True
        if not result and _seg_spanning_barred(
                key,
                tuple(GROUND_TRUTH_FIELDS) + tuple(BARRED_PROJECTION_KEYS),
                tuple(_BARRED_KEY_PARTS),
                tuple(_BARRED_EXACT_FOLDED),
                tuple(_BARRED_PARTS_FOLDED)):
            return True
        return result
    lowered = _stored_text(key).lower()
    if lowered in GROUND_TRUTH_FIELDS:
        return True
    if lowered in BARRED_PROJECTION_KEYS:
        return True
    if any(part in lowered for part in _BARRED_KEY_PARTS):
        return True
    for reading in _folded_readings(key):
        if reading in _BARRED_EXACT_FOLDED:
            return True
        if any(part in reading for part in _BARRED_PARTS_FOLDED):
            return True
    return _combined_key_barred(key)


def _key_string_is_barred(key):
    """Return whether any string standing inside a container key
    stands barred. A plain string key is judged as itself, and a
    tuple, frozenset, set, or list key is judged by every string
    standing inside it, at any nesting."""
    if isinstance(key, str):
        return _is_barred_key(key)
    if isinstance(key, dict):
        return any(
            _key_string_is_barred(part) for part in dict.keys(key))
    if isinstance(key, (list, tuple, set, frozenset)):
        return any(
            _key_string_is_barred(part) for part in _base_iter(key))
    return False


_GENERATOR_SIGNATURE = "behaviour(stream_state, labelled_assumptions)"

TRAVERSAL_DEPTH_BOUND = 100


class NamedGeneratorFailure(ValueError):
    """A generator failure stated by name, with its ground and path."""


def _traversal_guard(value, depth, seen, path):
    """Guard one traversal step under the stated bound of 100.

    The counting basis for the bound is containers only: the
    depth of a value counts the containers standing above it,
    and a scalar leaf standing at the end of a chain counts
    no depth of its own. On that basis a chain of 101 nested
    containers over a scalar leaf stands within the bound,
    and a chain of 102 stands past it and stands refused.
    """
    if depth > TRAVERSAL_DEPTH_BOUND:
        raise NamedGeneratorFailure(
            "ground truth traversal bound reached at " + (path or "root")
            + ": the value stands deeper than the stated bound of "
            + str(TRAVERSAL_DEPTH_BOUND)
            + ", counted on the containers only basis, the depth of "
            "a value counting the containers standing above it and a "
            "scalar leaf counting no depth of its own, and no "
            "traversal stands performed past that bound"
        )
    if id(value) in seen:
        raise NamedGeneratorFailure(
            "ground truth traversal found a cycle at " + (path or "root")
            + ", and no traversal stands performed on the cyclic value"
        )


AgentState = _mod01.AgentState
VouchEdge = _mod01.VouchEdge


def mod01_surface():
    """Return the MOD-01 module this generator depends on."""
    return _mod01


def mod01_type(name):
    """Return a type named on the MOD-01 surface, or None if absent."""
    return getattr(_mod01, name, None)


def _guarded_copy(value, _memo=None):
    """Copy a value through base class readings only, the guarded
    copy form of the estate. Dict parts stand read through the base
    dict items reading, and list, tuple, set, and frozenset parts
    through their base iteration readings, built as plain containers
    of their kind, so no copy protocol a part supplies is ever
    invoked and a part supplying a lying deepcopy protocol cannot
    materialise as another value inside the copy. The buffer
    forms stand carried as stored: a bytearray as a fresh
    bytearray and a memoryview as a memoryview over fresh bytes.
    A part in no container form and no buffer form stands copied
    as itself. One memo stands shared
    across the values of one act where the act hands one in, so a
    part shared between those values stands as one copy. A dict assignment whose key hash or equality reading
    raises at the assignment itself stands carried under a
    distinct numbered form, a plain text numbered form where
    a form carrying the key itself cannot stand inserted, in
    the MOD-14 cured form, so no carried entry is silently
    dropped on that reading and no bare error escapes the copy."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied_key = _guarded_copy(key, _memo)
            copied_item = _guarded_copy(item, _memo)
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
            _guarded_copy(item, _memo) for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _guarded_copy(item, _memo) for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, frozenset):
        if id(value) in _memo:
            return _memo[id(value)]
        copied_items = [
            _guarded_copy(item, _memo)
            for item in frozenset.__iter__(value)]
        try:
            copied = frozenset(copied_items)
        except Exception:
            copied = copied_items
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, set):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = set()
        _memo[id(value)] = copied
        copied_items = [
            _guarded_copy(item, _memo)
            for item in set.__iter__(value)]
        try:
            for copied_item in copied_items:
                copied.add(copied_item)
        except Exception:
            _memo[id(value)] = copied_items
            return copied_items
        return copied
    if isinstance(value, bytearray):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = bytearray(bytes(value))
        _memo[id(value)] = copied
        return copied
    if isinstance(value, memoryview):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = memoryview(bytes(value))
        _memo[id(value)] = copied
        return copied
    return value


def _stored_key_matches(stored, key):
    """Whether a stored key stands as a handed key, judged on
    the forms each side stores, never through a hash or
    equality reading either side itself supplies. A text form
    key stands judged on its stored text, in the stored text
    form of this module. A plain scalar key stands judged
    kind first on the scalar it stores, a boolean apart from
    every number, under settlement S-16. Any other key stands
    as itself alone, by identity."""
    if stored is key:
        return True
    if isinstance(key, (str, bytes, bytearray, memoryview)) \
            and isinstance(
                stored, (str, bytes, bytearray, memoryview)):
        result = str.__eq__(_stored_text(stored), _stored_text(key))
        return result if result is not NotImplemented else False
    if isinstance(key, bool) or isinstance(stored, bool):
        return False
    if isinstance(key, int) and isinstance(stored, int):
        result = int.__eq__(stored, key)
        return result if result is not NotImplemented else False
    if isinstance(key, float) and isinstance(stored, float):
        result = float.__eq__(stored, key)
        return result if result is not NotImplemented else False
    if isinstance(key, complex) and isinstance(stored, complex):
        result = complex.__eq__(stored, key)
        return result if result is not NotImplemented else False
    return False


def _base_get(record, key, default=None):
    """Read one field of a handed record through its stored
    pairs, never through a get reading the record itself
    supplies and never through a hash or equality reading a
    stored key supplies, so a record stands judged and built
    from the contents it stores, in the cured companion form
    of the MOD-13 stored pairs reading. A value in no record
    form stores nothing under any key and reads as the
    default."""
    if isinstance(record, dict):
        for stored_key, item in dict.items(record):
            if _stored_key_matches(stored_key, key):
                return item
    return default


def _record_sequence(records):
    """The records a handed record set stores, read through
    the base iteration of its form where it stands in a
    container form, never through a truth or iteration
    reading the set itself supplies, so stored records stand
    counted and read whole."""
    if records is None:
        return []
    if isinstance(records, (list, tuple, set, frozenset)):
        return list(_base_iter(records))
    return []


def _stored_rows(value):
    """The parameter rows a record stores, as a new outer list
    holding the stored rows, read through the base iteration
    of the rows value where it stands in a sequence form."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(_base_iter(value))
    return []


def make_archetype_record(archetype_id=None, behaviour=None,
                          parameter_rows=None, generator_signature=None,
                          ground_truth_label=None, farm_member=False):
    """Build one archetype record, the data a generator is driven by.

    Only archetype behaviour is stated in the record: the behaviour
    mapping, its parameter rows, and its generator signature. No rule
    state and no strategy stands in the record. The strategy class
    for a run is stated on the cast, never in an archetype record.
    """
    memo = {}
    rows = _guarded_copy(parameter_rows or (), memo)
    if not isinstance(rows, list):
        rows = list(rows)
    return {
        "archetype_id": archetype_id,
        "behaviour": _guarded_copy(behaviour or {}, memo),
        "parameter_rows": rows,
        "generator_signature": generator_signature or _GENERATOR_SIGNATURE,
        "ground_truth_label": ground_truth_label,
        "farm_member": bool(farm_member),
    }


def archetype_catalogue(records=None):
    """Return the archetype catalogue record this slice delivers.

    Every entry carries its generator signature and its parameter
    rows, built from the archetype records supplied. The gaps inside
    OP-11 stand carried open by name. No entry is invented to fill a
    gap, and the cast words of the brief head stand treated as no
    typed catalogue.
    """
    entries = {}
    if records is not None and not isinstance(
            records, (list, tuple, set, frozenset)):
        # A record set handed in a form the act refuses stands
        # refused in the same named sentence: a text, bytes, or
        # mapping form, a number or any other form standing in
        # no iterable form at all, and an iterator form, whose
        # contents stand as a one shot stream and not as a
        # record set. An iterable object in no container form
        # and in no iterator form stands unread under the
        # _record_sequence standing, as that reading states,
        # and delivers the empty catalogue of that standing.
        if (
                isinstance(records, (str, bytes, dict))
                or hasattr(records, "__next__")
                or not hasattr(records, "__iter__")):
            raise ValueError(
                "catalogue rejected: the record set stands in no "
                "record list form, a record set stands as records, "
                "and no catalogue stands delivered")
    for record in _record_sequence(records):
        if not isinstance(record, dict):
            raise ValueError(
                "catalogue rejected: an archetype record stands in "
                "no record form: " + _refusal_repr(record))
        identifier = _base_get(record, "archetype_id")
        if identifier is None:
            raise ValueError(
                "catalogue rejected: an archetype record carries no "
                "identifier"
            )
        if identifier in entries:
            raise ValueError(
                "catalogue rejected: a duplicate archetype identifier "
                "stands in the record set: " + _safe_str(identifier)
            )
        rows = _guarded_copy(
            _base_get(record, "parameter_rows") or ())
        if not isinstance(rows, list):
            rows = list(rows)
        entries[identifier] = {
            "generator_signature": _base_get(
                record, "generator_signature"),
            "parameter_rows": rows,
        }
    return {
        "standing": CATALOGUE_STANDING,
        "entries": entries,
        "gaps_carried_open": list(OP11_GAPS),
        "brief_head_words_treated_as_catalogue": False,
    }


def catalogue(records=None):
    """Return the archetype catalogue record. See archetype_catalogue."""
    return archetype_catalogue(records)


def catalogue_record(records=None):
    """Return the catalogue record the slice delivers for a record set."""
    return archetype_catalogue(records)


def catalogue_gaps():
    """Return the OP-11 catalogue gaps carried open, by name."""
    return OP11_GAPS


def brief_head_words_are_catalogue():
    """Return whether the brief head cast words form a catalogue."""
    return False


def run_headline_reportable(archetype_ids, records=None):
    """Return whether every archetype in use stands in the catalogue.

    A run using an archetype identifier outside the catalogue is not
    headline reportable.
    """
    entries = archetype_catalogue(records)["entries"]
    if not isinstance(archetype_ids, (list, tuple, set, frozenset)):
        raise ValueError(
            "run_headline_reportable stands refused: the archetype "
            "identifiers stand in no list form, a list of archetype "
            "identifiers stands required, and no headline reportable "
            "standing stands returned")
    identifiers = list(_base_iter(archetype_ids))
    return all(identifier in entries for identifier in identifiers)


def canonical_scale_set():
    """Return fixture F-18, the canonical scale set.

    Populations 200, 400, and 800, each labelled estimated.
    """
    return tuple(dict(entry) for entry in CANONICAL_SCALE_SET)


def scale_populations():
    """Return the F-18 population values in their stated order."""
    return tuple(entry["population"] for entry in CANONICAL_SCALE_SET)


def _stream_values(stream_state, preferred_key=None):
    """Read stream values handed in as values, in their stated order.

    A dict is read by named keys. The preferred key wins where it
    carries a list or tuple, and the key named values wins next.
    Where neither named key carries a list or tuple, the fallback
    selection is stated and deterministic: the candidate list or
    tuple values are sorted by a stated key, the string form of
    their dict key, with the sort key function str applied to each
    key, and the first candidate in that sorted order is selected.
    The fallback therefore selects the same value for the same
    entries whatever order the container iterates them in.
    """
    if stream_state is None:
        return []
    if isinstance(stream_state, (list, tuple)):
        return list(_base_iter(stream_state))
    if isinstance(stream_state, dict):
        if preferred_key is not None and isinstance(
                _base_get(stream_state, preferred_key),
                (list, tuple)):
            return list(_base_iter(
                _base_get(stream_state, preferred_key)))
        if isinstance(
                _base_get(stream_state, "values"), (list, tuple)):
            return list(_base_iter(
                _base_get(stream_state, "values")))
        candidates = [
            (key, value) for key, value in dict.items(stream_state)
            if isinstance(value, (list, tuple))
        ]
        if candidates:
            candidates.sort(key=lambda item: str(item[0]))
            return list(_base_iter(candidates[0][1]))
    return []


def _guard_farm_size(farm_size, form):
    """Guard a farm size as a non negative whole count.

    None stands as no farm size stated and reads as zero. Every
    other form that is not a non negative whole count, including
    a boolean, a fractional number, and a text form, fails in
    the named failure form.
    """
    if farm_size is None:
        return 0
    if isinstance(farm_size, bool) or not isinstance(
            farm_size, int) or farm_size < 0:
        raise NamedGeneratorFailure(
            form + ": the farm size is not a non negative whole "
            "count: " + _refusal_repr(farm_size))
    return farm_size


def _records_by_id(archetype_records):
    by_id = {}
    for record in _record_sequence(archetype_records):
        by_id[_base_get(record, "archetype_id")] = record
    return by_id


def build_cast(point, archetype_records, stream_state=None,
               strategy_class=None, initial_edges=None):
    """Build the cast for one run and deliver it before day one.

    The point names the population and the archetype mix. The mix
    counts must sum to the population, and every archetype in the mix
    must stand in the records supplied. The population stands bounded
    by the largest population of the canonical scale set this module
    states, and a population past that bound stands refused in named
    form. The strategy class for a run is
    fixed in advance: a cast with no strategy class stated does not
    build. Cast order is a deterministic function of the stream state
    values handed in: where cast values stand supplied, one per agent,
    agents take their archetypes in the order those values state, ties
    broken by agent identifier.
    """
    if not strategy_class or not isinstance(strategy_class, str):
        raise NamedGeneratorFailure(
            "cast rejected: the strategy class for a run is fixed "
            "in advance and must be stated before the run: the "
            "strategy class stands absent or empty")
    if not isinstance(point, dict):
        raise NamedGeneratorFailure(
            "cast rejected: the point for a cast is not a record: "
            + _refusal_repr(point))
    population = _base_get(
        point, "population_size", _base_get(point, "population"))
    mix_value = _base_get(point, "archetype_mix")
    if mix_value is not None and not isinstance(mix_value, dict):
        raise NamedGeneratorFailure(
            "cast rejected: the archetype mix stands in no record "
            "form: " + _refusal_repr(mix_value))
    mix_items = (
        list(dict.items(mix_value)) if isinstance(mix_value, dict)
        else [])
    if population is None:
        raise NamedGeneratorFailure(
            "cast rejected: the point states no population")
    if isinstance(population, bool) or not isinstance(
            population, int) or population < 0:
        raise NamedGeneratorFailure(
            "cast rejected: the population the point states is not "
            "a non negative whole count: " + _refusal_repr(population))
    population_bound = max(scale_populations())
    if population > population_bound:
        raise NamedGeneratorFailure(
            "cast rejected: the population the point states stands "
            "past the stated population bound of "
            + str(population_bound) + ", the largest population of "
            "the canonical scale set this module states: "
            + _refusal_repr(population))
    for mix_identifier, mix_count in mix_items:
        if isinstance(mix_count, bool) or not isinstance(
                mix_count, int) or mix_count < 0:
            raise NamedGeneratorFailure(
                "cast rejected: the mix count for "
                + _sentence_text(mix_identifier) + " is not a non negative "
                "whole count: " + _refusal_repr(mix_count))
    if sum(count for _identifier, count in mix_items) != population:
        raise NamedGeneratorFailure(
            "cast rejected: archetype mix counts sum to "
            + str(sum(
                count for _identifier, count in mix_items))
            + ", not to the population "
            "the point names: " + str(population))
    by_id = _records_by_id(archetype_records)
    for identifier, _count in mix_items:
        if identifier not in by_id:
            raise NamedGeneratorFailure(
                "cast rejected: archetype in the mix stands outside "
                "the records supplied: " + _sentence_text(identifier))
    agent_ids = ["agent-%04d" % index for index in range(population)]
    order = list(agent_ids)
    cast_values = _stream_values(stream_state, "cast")
    if cast_values:
        if len(cast_values) != population:
            raise NamedGeneratorFailure(
                "cast rejected: cast stream values cover "
                + str(len(cast_values)) + " agents, not the "
                "population: " + str(population))
        order = [agent for _value, agent in sorted(
            zip(cast_values, agent_ids),
            key=lambda pair: (pair[0], pair[1]))]
    assignment = []
    for identifier, count in mix_items:
        assignment.extend([identifier] * count)
    farm_size = _guard_farm_size(
        _base_get(point, "farm_size"), "cast rejected")
    farm_members = []
    agents = []
    farm_of = {}
    for agent_id, archetype_id in zip(order, assignment):
        record = by_id[archetype_id]
        farm_id = None
        if _base_get(record, "farm_member") and farm_size:
            farm_members.append(agent_id)
            farm_id = "farm-%d" % ((len(farm_members) - 1) // farm_size)
        farm_of[agent_id] = farm_id
        agents.append({
            "agent_id": agent_id,
            "archetype_id": archetype_id,
            "ground_truth": _base_get(record, "ground_truth_label"),
            "farm_id": farm_id,
        })
    agents.sort(key=lambda agent: agent["agent_id"])
    farms = []
    if farm_size:
        grouped = {}
        for agent_id in farm_members:
            grouped.setdefault(farm_of[agent_id], []).append(agent_id)
        for farm_id in sorted(grouped):
            farms.append({
                "farm_id": farm_id,
                "member_ids": sorted(grouped[farm_id]),
            })
    edges = []
    edge_source = initial_edges
    if edge_source is None:
        edge_source = _base_get(point, "initial_edges")
    for edge in edge_source or ():
        if isinstance(edge, dict):
            edges.append({
                "voucher": _base_get(edge, "voucher"),
                "vouchee": _base_get(edge, "vouchee"),
                "stake": _base_get(edge, "stake", 0),
            })
        elif isinstance(edge, (str, bytes)):
            raise NamedGeneratorFailure(
                "cast rejected: an initial edge stands as text, "
                "not as a voucher and vouchee pair: " + _refusal_repr(edge))
        elif isinstance(edge, (list, tuple)) and len(edge) == 2:
            voucher, vouchee = edge
            edges.append({
                "voucher": voucher,
                "vouchee": vouchee,
                "stake": 0,
            })
        else:
            raise NamedGeneratorFailure(
                "cast rejected: an initial edge is not a voucher "
                "and vouchee pair of size two: " + _refusal_repr(edge))
    internal_counts = {}
    for farm in farms:
        internal_counts[farm["farm_id"]] = 0
    for edge in edges:
        first = farm_of.get(edge["voucher"])
        if first is not None and first == farm_of.get(edge["vouchee"]):
            internal_counts[first] += 1
    cast_record = {
        "delivery_point": "before day one",
        "point_id": _base_get(
            point, "point_id", _base_get(point, "point_identifier")),
        "strategy_class": strategy_class,
        "population": population,
        "archetype_counts": dict(mix_items),
        "cast": agents,
        "farms": farms,
        "initial_graph": {"edges": edges},
        "internal_edge_count_per_farm": internal_counts,
        "deliveries_after_day_one": (
            "behaviour through the behaviour streams only"),
    }
    if not farm_size and any(
            _base_get(by_id[agent["archetype_id"]], "farm_member")
            for agent in agents):
        cast_record["farm_construction"] = (
            "not built: no farm size stands stated in the point, "
            "so no farms stand constructed over the farm members "
            "the cast carries")
    return cast_record


def cast_agent_record(agent):
    """Return one cast member in the MOD-01 Form 7 field naming.

    The cast states the agent identifier, the archetype identifier,
    and the membership ground truth, which the cast carries for
    scoring only. The remaining Form 7 fields are simulation state
    written after day one by the engine that owns that state, and
    the cast states no value for them.
    """
    if not isinstance(agent, dict):
        return {}
    return {
        "agent_identifier": _base_get(agent, "agent_id"),
        "archetype_identifier": _base_get(agent, "archetype_id"),
        "membership_ground_truth": _base_get(agent, "ground_truth"),
    }


def cast_edge_record(edge):
    """Return one initial graph edge in the MOD-01 Form 8 field naming.

    The cast states the voucher, the vouchee, and the stake of an
    initial edge. The remaining Form 8 fields stand stated by the
    core that owns the edge after delivery, not by the cast.
    """
    if not isinstance(edge, dict):
        return {}
    return {
        "voucher": _base_get(edge, "voucher"),
        "vouchee": _base_get(edge, "vouchee"),
        "stake": _base_get(edge, "stake"),
    }


def deliver_cast(point, archetype_records, stream_state=None,
                 strategy_class=None, initial_edges=None):
    """Deliver the full cast and initial graph. See build_cast."""
    return build_cast(point, archetype_records, stream_state,
                      strategy_class, initial_edges)


def generate_society(point, archetype_records, stream_state=None,
                     strategy_class=None, initial_edges=None):
    """Build one society for a run. See build_cast."""
    return build_cast(point, archetype_records, stream_state,
                      strategy_class, initial_edges)


def _stored_member_key(name):
    """Return the key a farm membership judgement stands on for
    one name. For a text name, the key stands as the stored text
    of the name, read character by character through the base
    string reading, so a hash or equality reading the name
    supplies directs nothing. For a bytes form name, the key
    stands as the plain bytes the name stores, read through
    the base bytes reading, so a bytes subclass member stands
    judged on its stored bytes in the same form as a plain
    bytes member. A bytearray name and a memoryview name
    stand in the same bytes form, judged on the bytes they
    store or view, read through the base bytes reading in the
    same way, so a buffer member carrying the same stored
    bytes as a plain bytes member carries the same key, and
    a bytearray subclass member stands judged the same way.
    For a plain scalar name, the key stands as
    the plain scalar the name stores, read through the base
    class reading of its kind, so an int, float, or complex
    subclass member stands judged on its stored value in the
    same form as a plain member of that kind, and a boolean
    stands as itself. For every other name, the key stands as
    an identity pair built from a fixed marker and the identity
    of the name object, read through the base identity reading,
    so the name stands judged as the member it is in itself and
    never by a hash or equality reading it supplies against a
    text name or against any other name."""
    if isinstance(name, str):
        return "".join(
            str.__getitem__(name, index)
            for index in range(str.__len__(name)))
    if isinstance(name, (bytes, bytearray, memoryview)):
        return bytes(name)
    if isinstance(name, bool):
        return name
    if isinstance(name, int):
        return int.__int__(name)
    if isinstance(name, float):
        return float.__float__(name)
    if isinstance(name, complex):
        return complex.__complex__(name)
    return ("non text name", id(name))


def _member_order_key(name):
    """Return the stated order key for one member of an unordered
    member container. A text member stands ordered by its stored
    text, read through _stored_text so a reading the member itself
    supplies directs nothing. A bytes form member stands ordered
    after text members, by the text its stored bytes decode to. A
    plain scalar member stands ordered after those, by its kind
    name and its base representation. Every other member stands
    ordered last, by its kind name and the identity reading its
    stored member key carries, the same identity reading farm
    membership itself stands judged on."""
    key = _stored_member_key(name)
    if isinstance(key, str):
        return (0, key, "")
    if isinstance(key, bytes) or isinstance(
            name, (bytearray, memoryview)):
        # The decoded text alone does not order this group:
        # distinct stored bytes that decode, with undecodable
        # bytes dropped, to the same text would tie on it and
        # fall back to the iteration order of the handed set,
        # which the hash seed governs. The raw stored bytes
        # stand as the tie break after the decoded text, so
        # two members of this group tie only where their
        # stored bytes stand identical as well.
        return (1, _stored_text(name), type(name).__name__,
                bytes(name))
    if type(key) in (bool, int, float, complex):
        return (2, type(name).__name__, repr(key))
    return (3, type(name).__name__, str(key[1]))


def construct_farm(member_ids, farm_size=None, edges=None):
    """Construct farms over a member set and count internal edges.

    Returns the farm identities with their members and the internal
    edge count per farm identity, the count the run record carries.
    With no edges stated, every internal count stands at zero. Where
    no farm size stands stated and the member set stands non empty,
    no farms stand constructed and the answer states the standing
    of the member set: the members stand named in
    unplaced_member_ids, with the standing stated in
    member_set_standing.

    The member set and the edge set stand read through their base
    class iteration, an edge pair stands read through the base
    length and item readings of its kind, and the farm membership
    of each name in a counted pair stands judged on the stored
    text of the name, so no iteration, length, item, hash, or
    equality reading a handed value supplies directs the count.
    Members handed in an unordered container, a set or a
    frozenset, stand ordered by the stated content derived order
    of _member_order_key before any grouping, so the same member
    content gives the same grouping and the same counts at every
    hash seed. Members handed in an ordered container stand
    grouped in the order handed. The population stands judged
    as a set of identities: a member handed more than once,
    judged on the stored member key the membership judgement
    itself stands on, stands grouped once, in its first arrival
    position, so the membership lists state the same population
    the farm membership carriage keys, one farm standing per
    member.
    """
    if member_ids is None:
        members = []
    else:
        members = list(_base_iter(member_ids))
        if isinstance(member_ids, (set, frozenset)):
            members = sorted(members, key=_member_order_key)
    distinct_members = []
    seen_keys = {}
    for member in members:
        key = _stored_member_key(member)
        try:
            present = key in seen_keys
        except Exception:
            present = False
        if not present:
            seen_keys[key] = True
            distinct_members.append(member)
    members = distinct_members
    farm_size = _guard_farm_size(farm_size, "farm rejected")
    if not farm_size:
        farms = []
        farm_of = {_stored_member_key(member): None
                   for member in members}
    else:
        grouped = {}
        farm_of = {}
        for index, member in enumerate(members):
            farm_id = "farm-%d" % (index // farm_size)
            grouped.setdefault(farm_id, []).append(member)
            farm_of[_stored_member_key(member)] = farm_id
        farms = [
            {"farm_id": farm_id, "member_ids": list(grouped[farm_id])}
            for farm_id in sorted(grouped)
        ]
    counts = {farm["farm_id"]: 0 for farm in farms}
    edge_iter = () if edges is None else _base_iter(edges)
    for edge in edge_iter:
        if isinstance(edge, dict):
            if dict.get(edge, "voucher") is None:
                raise NamedGeneratorFailure(
                    "farm rejected: an edge carries no voucher, "
                    "not as a voucher and vouchee pair: "
                    + _refusal_repr(edge))
            if dict.get(edge, "vouchee") is None:
                raise NamedGeneratorFailure(
                    "farm rejected: an edge carries no vouchee, "
                    "not as a voucher and vouchee pair: "
                    + _refusal_repr(edge))
            first, second = (
                dict.get(edge, "voucher"), dict.get(edge, "vouchee"))
        elif isinstance(edge, (str, bytes)):
            raise NamedGeneratorFailure(
                "farm rejected: an edge stands as text, not as a "
                "voucher and vouchee pair: " + _refusal_repr(edge))
        elif isinstance(edge, (list, tuple)):
            if isinstance(edge, list):
                pair_size = list.__len__(edge)
                pair_item = list.__getitem__
            else:
                pair_size = tuple.__len__(edge)
                pair_item = tuple.__getitem__
            if pair_size != 2:
                raise NamedGeneratorFailure(
                    "farm rejected: an edge is not a voucher and "
                    "vouchee pair of size two: " + _refusal_repr(edge))
            first, second = pair_item(edge, 0), pair_item(edge, 1)
        else:
            raise NamedGeneratorFailure(
                "farm rejected: an edge stands in no pair form, "
                "not as a voucher and vouchee pair: " + _refusal_repr(edge))
        farm_id = farm_of.get(_stored_member_key(first))
        if farm_id is not None and farm_id == farm_of.get(
                _stored_member_key(second)):
            counts[farm_id] += 1
    answer = {
        "farms": farms,
        "internal_edge_count_per_farm_identity": counts,
    }
    if not farm_size and members:
        answer["unplaced_member_ids"] = list(members)
        answer["member_set_standing"] = (
            "no farm size stands stated, so no farms stand "
            "constructed and the handed members stand unplaced, "
            "named in unplaced_member_ids")
    return answer


def build_farm(member_ids, farm_size=None, edges=None):
    """Construct farms over a member set. See construct_farm."""
    return construct_farm(member_ids, farm_size, edges)


def zero_edge_society(point, archetype_records, stream_state=None,
                      strategy_class=None):
    """Construct the fixture F-03 zero edge society.

    The cast builds with no initial edges, so every per farm
    identity internal edge count stands at zero on the record.
    Both headline figures, the attack edge count and the summed
    stake, are computed from the society as constructed, from its
    initial graph, and stand at 0 because that graph is empty.
    Anchor scenario AN-1 stands in place.
    """
    cast = build_cast(point, archetype_records, stream_state,
                      strategy_class, initial_edges=())
    built_edges = cast["initial_graph"]["edges"]
    cast["attack_edge_count"] = len(built_edges)
    cast["summed_stake"] = sum(
        edge.get("stake", 0) for edge in built_edges)
    cast["anchor_scenario"] = anchor_scenario(
        "AN-1", _base_get(point, "anchor_set_description", "scenario setting"))
    return cast


def zero_edge_result():
    """Return the zero edge result in its only reportable form.

    The result, the primary order parameter driven above one half by
    external direct credit, stands reported only as a property of
    the simplified graph, with the simplification named.
    """
    return {
        "result": ("primary order parameter driven above one half "
                   "by external direct credit"),
        "standing": "property of the simplified graph only",
        "simplification_named": True,
        "simplification": "simplified graph, simplification S4",
    }


def archetype_behaviour(archetype_record, stream_state=None,
                        assumption_values=None, agent_id=None):
    """Return the proposals one archetype record generates.

    A deterministic function of the stream state values handed in
    and the labelled assumption values stated. The same record, the
    same stream values, and the same assumptions give the same
    proposals on every call. Proposals carry no rule state: no
    reputation, stake, band, or contract effect stands in a proposal.
    """
    record = archetype_record if archetype_record is not None else {}
    behaviour_value = _base_get(record, "behaviour")
    behaviour = (
        behaviour_value if isinstance(behaviour_value, dict) else {})
    action = _base_get(behaviour, "action", "propose")
    if isinstance(stream_state, (int, float)):
        values = [stream_state]
    else:
        values = _stream_values(stream_state, "behaviour")
    proposals = []
    for value in values:
        proposals.append({
            "agent_id": agent_id,
            "archetype_id": _base_get(record, "archetype_id"),
            "action": action,
            "draw": value,
            "assumptions": _guarded_copy(
                assumption_values if assumption_values is not None
                else {}),
        })
    return proposals


def generate_behaviour(archetype_record, stream_state=None,
                       assumption_values=None, agent_id=None):
    """Generate archetype behaviour. See archetype_behaviour."""
    return archetype_behaviour(archetype_record, stream_state,
                               assumption_values, agent_id)


def run_archetype(archetype_record, stream_state=None,
                  assumption_values=None, agent_id=None):
    """Run one archetype generator once. See archetype_behaviour."""
    return archetype_behaviour(archetype_record, stream_state,
                               assumption_values, agent_id)


def generator_holds_rule_state():
    """Return whether the generator holds any rule state."""
    return False


def _base_iter(value):
    """Iterate a list, tuple, set, frozenset, or dict part
    through its base class iteration, never through a reading
    the part itself supplies, so a part whose own iteration
    yields nothing still stands read by the contents in its
    base class storage, a dict part standing read by the keys
    it holds in base dict storage."""
    iter_by_base = {list: list.__iter__, tuple: tuple.__iter__,
                    set: set.__iter__, frozenset: frozenset.__iter__,
                    dict: dict.__iter__}
    for base, base_iter in iter_by_base.items():
        if isinstance(value, base):
            return base_iter(value)
    return iter(value)


def _key_carries_rule_state(key):
    """Return whether a dict key carries a rule state field name.

    A plain string key stands judged through the base string
    equality against each field name, never through an equality
    reading the key itself supplies. A container key stands
    judged by every string standing inside it, at any nesting,
    in the form the ground truth read judges container keys.
    """
    if isinstance(key, str):
        return any(
            str.__eq__(key, field) is True
            for field in RULE_STATE_FIELDS)
    if isinstance(key, dict):
        return any(
            _key_carries_rule_state(part)
            for part in dict.keys(key))
    if isinstance(key, (list, tuple, set, frozenset)):
        return any(
            _key_carries_rule_state(part) for part in _base_iter(key))
    return False


def _value_carries_rule_state(value, _depth=0, _seen=None, _path=""):
    """Return whether a value carries a rule state field at any depth.

    Dicts are read by their keys and by every value they hold, and
    lists, tuples, and sets are read by every item they hold, so a
    decided effect nested inside another value still counts. The
    reading stands under the module traversal guard: a value
    standing deeper than the stated traversal bound, and a value
    carrying a cycle, each fail in the module named failure form,
    as the ground truth reading of this module fails, and no bare
    recursion error escapes.

    A container shared by two siblings stands walked once at each
    depth at which it stands reached: its walked standing stands
    carried across every path that reaches it at that depth, so
    the walk grows with the size of the value, and a reach at a
    greater depth stands rejudged at its own depth, where the
    traversal bound is judged afresh.
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if isinstance(_seen, dict):
            state = _seen
        else:
            state = {"active": set(_seen or ()), "done": {}}
        marker = (id(value), _depth)
        if marker in state["done"]:
            return state["done"][marker]
        _traversal_guard(value, _depth, state["active"], _path)
        state["active"].add(id(value))
        try:
            result = False
            if isinstance(value, dict):
                joined_keys = "".join(
                    str.__str__(key) for key in dict.keys(value)
                    if isinstance(key, str))
                if any(
                        str.__eq__(joined_keys, field) is True
                        for field in RULE_STATE_FIELDS):
                    result = True
                    state["done"][marker] = result
                    return result
                for key, item in dict.items(value):
                    if isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        if _value_carries_rule_state(
                                key, _depth + 1, state,
                                _path + "/key"):
                            result = True
                            break
                    if _key_carries_rule_state(key):
                        result = True
                        break
                    if _value_carries_rule_state(
                            item, _depth + 1, state,
                            _path + "/" + _path_key_text(key)):
                        result = True
                        break
            else:
                for index, item in enumerate(_base_iter(value)):
                    if _value_carries_rule_state(
                            item, _depth + 1, state,
                            _path + "[" + str(index) + "]"):
                        result = True
                        break
            state["done"][marker] = result
            return result
        finally:
            state["active"].discard(id(value))
    return False


def validate_generator_output(output):
    """Return True only where an output proposes and decides nothing.

    An output carrying a reputation, stake, band, or contract effect
    as a decided effect fails this check, at any depth the traversal
    bound reaches: the reading carries no shallower limit of its
    own, and a value standing deeper than the module traversal
    bound, or carrying a cycle, fails in the module named failure
    form instead of standing read as clean. Ground truth carriage
    in a cast delivery is scoring carriage, not an effect, and
    stands outside this check, which reads proposal outputs.
    """
    items = _base_iter(output) if isinstance(
        output, (list, tuple)) else [output]
    for item in items:
        if not isinstance(item, dict):
            return False
        if _value_carries_rule_state(item):
            return False
    return True


def _value_carries_ground_truth(value, _depth=0, _seen=None, _path=""):
    """Return whether a value carries a ground truth field at any depth.

    Dicts are read by their keys and by every value they hold, and
    lists, tuples, and sets are read by every item they hold, so a
    barred key nested inside a feature value, inside a rule
    record, or inside a container at any further depth still counts.

    A container shared by two siblings stands walked once at
    each depth at which it stands reached: its walked standing
    stands carried across every path that reaches it at that
    depth, so the walk grows with the size of the value, and the
    standing carries the depth at which it stands earned, so a
    reach at a greater depth stands rejudged at its own depth
    and the traversal guard stands called on that reach before
    any cached standing stands returned. A container that stands
    on its own walk path still stands as a cycle and stands
    refused in the module named failure form.
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if isinstance(_seen, dict):
            state = _seen
        else:
            state = {"active": set(_seen or ()), "done": {}}
        marker = (id(value), _depth)
        if marker in state["done"]:
            return state["done"][marker]
        _traversal_guard(value, _depth, state["active"], _path)
        state["active"].add(id(value))
        try:
            result = False
            if isinstance(value, dict):
                if _is_barred_key(value) and not any(
                        _is_barred_key(key)
                        for key in dict.keys(value)):
                    state["done"][marker] = True
                    return True
                for key, item in dict.items(value):
                    if isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        if _value_carries_ground_truth(
                                key, _depth + 1, state,
                                _path + "/key"):
                            result = True
                            break
                        if _is_barred_key(key):
                            result = True
                            break
                    elif _is_barred_key(key):
                        result = True
                        break
                    if _value_carries_ground_truth(
                            item, _depth + 1, state,
                            _path + "/" + _path_key_text(key)):
                        result = True
                        break
            else:
                for index, item in enumerate(_base_iter(value)):
                    if _value_carries_ground_truth(
                            item, _depth + 1, state,
                            _path + "[" + str(index) + "]"):
                        result = True
                        break
            state["done"][marker] = result
            return result
        finally:
            state["active"].discard(id(value))
    return False


def record_carries_ground_truth(record):
    """Return whether a record carries a ground truth field.

    The test is recursive: a ground truth or membership field at
    any level of nesting, inside a feature value, inside a rule
    record, or inside a nested container, counts as carried.
    """
    return _value_carries_ground_truth(record)


def _strip_ground_truth_value(value, _depth=0, _seen=None, _path=""):
    """Return a value with every ground truth field removed at any depth.

    Dicts lose every barred key wherever it stands and keep their
    remaining content, cleaned in the same way. Lists and tuples
    keep their form, with each item cleaned in the same way.
    Content that carries no barred key passes through unchanged.

    A container shared by two siblings stands stripped once at
    each depth at which it stands reached: its stripped form
    stands carried across every path that reaches it at that
    depth, so the walk grows with the size of the value, and a
    reach at a greater depth stands restripped at its own depth,
    where the traversal bound is judged afresh.
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if isinstance(_seen, dict):
            state = _seen
        else:
            state = {"active": set(_seen or ()), "done": {}}
        marker = (id(value), _depth)
        if marker in state["done"]:
            return state["done"][marker]
        _traversal_guard(value, _depth, state["active"], _path)
        state["active"].add(id(value))
        try:
            if isinstance(value, dict):
                if _is_barred_key(value) and not any(
                        _is_barred_key(key)
                        for key in dict.keys(value)):
                    result = {}
                    state["done"][marker] = result
                    return result
                stripped = {}
                for key, item in dict.items(value):
                    if isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        new_key = _strip_ground_truth_value(
                            key, _depth + 1, state, _path + "/key")
                        if _is_barred_key(key):
                            continue
                    else:
                        if _is_barred_key(key):
                            continue
                        new_key = key
                    stripped[new_key] = _strip_ground_truth_value(
                        item, _depth + 1, state,
                        _path + "/" + _path_key_text(key))
                result = stripped
            elif isinstance(value, list):
                result = [
                    _strip_ground_truth_value(
                        item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                ]
            elif isinstance(value, tuple):
                result = tuple(
                    _strip_ground_truth_value(
                        item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                )
            elif isinstance(value, frozenset):
                result = frozenset(
                    _strip_ground_truth_value(
                        item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                )
            elif isinstance(value, set):
                result = {
                    _strip_ground_truth_value(
                        item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                }
            else:
                result = value
            state["done"][marker] = result
            return result
        finally:
            state["active"].discard(id(value))
    return value


def strip_ground_truth(record):
    """Return a copy of a record with every ground truth field removed.

    The removal is recursive: a ground truth or membership field
    nested inside a feature value, inside a rule record, or inside
    a nested container is removed wherever it stands, and the
    legitimate content around it carries through.
    """
    if not isinstance(record, dict):
        return record
    return _strip_ground_truth_value(record)


def validate_detection_input(record):
    """Return True only where a detection input carries no ground truth.

    The bar holds at every level of nesting, inside feature values
    and inside any container the record holds. A value that is not
    a record at all fails this check, before any barred key read.
    """
    if not isinstance(record, dict):
        return False
    return not record_carries_ground_truth(record)


def validate_adjudication_input(record):
    """Return True only where panel inputs carry no ground truth label.

    The bar holds at every level of nesting, inside rule records
    and inside any container the input holds. The ground truth
    label reference stands held apart from the panel inputs, in
    the case record, and never inside them. A value that is not
    a record at all fails this check, before any barred key read.
    """
    if not isinstance(record, dict):
        return False
    return not record_carries_ground_truth(record)


def anchor_scenario(scenario_identifier, anchor_set_description):
    """Build an AnchorScenarioRecord of exactly three values.

    The values are the scenario identifier, the anchor set
    description as a scenario setting, and the mark in its ruled
    form. No fourth value, no default marker, and no favoured
    marker stands in the record.
    """
    return {
        "scenario_identifier": scenario_identifier,
        "anchor_set_description": anchor_set_description,
        "mark": DQ163_MARK,
    }


def build_anchor_scenario(scenario_identifier, anchor_set_description):
    """Build an AnchorScenarioRecord. See anchor_scenario."""
    return anchor_scenario(scenario_identifier, anchor_set_description)


def validate_anchor_scenario(record):
    """Return True only for the three value form with the ruled mark."""
    if not isinstance(record, dict):
        return False
    if set(dict.keys(record)) != {
            "scenario_identifier", "anchor_set_description", "mark"}:
        return False
    mark = dict.get(record, "mark")
    if not isinstance(mark, str):
        return False
    judged = str.__eq__(mark, DQ163_MARK)
    return judged if isinstance(judged, bool) else False


def empty_anchor_set_case():
    """Return fixture F-05, the empty anchor set case.

    The case stands as the control beside concentrated and dispersed
    placement at fixed count and fixed total share. It sets no
    estate default anchor set.
    """
    return {
        "case": "empty anchor set",
        "anchor_set": [],
        "standing": ("control beside concentrated and dispersed "
                     "placement at fixed count and fixed total share"),
        "sets_estate_default_anchor_set": False,
    }


def cold_society(population=None):
    """Return fixture F-23, the cold society degree case.

    Score bearing vouch degree is 0 for at least the first 90 days
    in a cold society, and stays gated thereafter by the gate
    passing share. The figure stands carried as derived over
    estimated rates, with that label attached.
    """
    return {
        "fixture": "F-23",
        "population": population,
        "score_bearing_vouch_degree_first_90_days": 0,
        "after_day_90": "gated by the gate passing share",
        "provenance_label": COLD_SOCIETY_PROVENANCE,
    }


def build_cold_society(population=None):
    """Build the cold society case record. See cold_society."""
    return cold_society(population)


def cold_society_degree(day, envelope=None, gate_passing_share=None):
    """Return the score bearing vouch degree for a cold society day.

    Days inside the first 90 return 0. A later day returns the
    envelope value multiplied by the gate passing share where both
    stand supplied, and otherwise returns the gated standing with
    no degree stated. A stated day before day zero stands refused
    in the named failure form. An envelope below zero, a gate
    passing share below zero or above one, and an operand standing
    as a non finite number each stand refused in the named failure
    form, so no returned figure stands outside the bounds this
    statement carries.
    """
    if isinstance(day, bool) or not isinstance(day, int):
        raise NamedGeneratorFailure(
            "cold society degree rejected: the stated day is not "
            "a whole count day in its stated form: " + _refusal_repr(day))
    # The day and the operands stand read by the numbers they
    # store, through the base class conversion of their kind,
    # never through a reconstruction by the type constructor,
    # which dispatches to a conversion reading a subclass
    # instance supplies, in the cured form of row R11-066 at
    # MOD-02 for plain conversion readings.
    plain_day = int.__int__(day)
    if int.__lt__(plain_day, 0):
        raise NamedGeneratorFailure(
            "cold society degree rejected: the stated day is a "
            "negative count of days, a day before the society "
            "stands, and no degree stands returned for it: "
            + _refusal_repr(day))
    if int.__le__(plain_day, COLD_SOCIETY_FIRST_DAYS):
        return 0
    for operand, naming in ((envelope, "envelope"),
                            (gate_passing_share, "gate passing share")):
        if operand is not None and (
                isinstance(operand, bool)
                or not isinstance(operand, (int, float))):
            raise NamedGeneratorFailure(
                "cold society degree rejected: the stated "
                + naming + " is not a number in its stated "
                "form: " + _refusal_repr(operand))
    for operand, naming, upper in (
            (envelope, "envelope", None),
            (gate_passing_share, "gate passing share", 1)):
        if operand is None:
            continue
        plain_operand = (
            float.__float__(operand) if isinstance(operand, float)
            else int.__int__(operand))
        if isinstance(plain_operand, float) and (
                plain_operand != plain_operand
                or plain_operand in (float("inf"), float("-inf"))):
            raise NamedGeneratorFailure(
                "cold society degree rejected: the stated "
                + naming + " is not a finite number, and no "
                "degree stands returned on it: "
                + _refusal_repr(operand))
        if plain_operand < 0 or (
                upper is not None and plain_operand > upper):
            raise NamedGeneratorFailure(
                "cold society degree rejected: the stated "
                + naming + " stands outside the bounds the "
                "figure states, and no degree stands returned "
                "on it: " + _refusal_repr(operand))
    if envelope is None or gate_passing_share is None:
        return {
            "degree": None,
            "standing": "gated by the gate passing share",
            "provenance_label": COLD_SOCIETY_PROVENANCE,
        }
    plain_envelope = (
        float.__float__(envelope) if isinstance(envelope, float)
        else int.__int__(envelope))
    plain_share = (
        float.__float__(gate_passing_share)
        if isinstance(gate_passing_share, float)
        else int.__int__(gate_passing_share))
    if isinstance(plain_envelope, float) or isinstance(
            plain_share, float):
        # Both operands stand plain here, exact int or exact
        # float as the conversions above return them, so the
        # constructor form on them dispatches to no reading a
        # handed value supplied.
        return float.__mul__(
            plain_envelope if isinstance(plain_envelope, float)
            else float.__new__(float, plain_envelope),
            plain_share if isinstance(plain_share, float)
            else float.__new__(float, plain_share))
    return int.__mul__(plain_envelope, plain_share)


def cold_degree_provenance():
    """Return the provenance label the cold degree figure carries."""
    return COLD_SOCIETY_PROVENANCE


def extend_catalogue(records, new_record, strategy_class=None):
    """Return a catalogue with one archetype added at the edge.

    A new archetype enters as data under the fixed strategy class
    for a run. The record carries the family labelling from before
    and after the addition, as entry counts over the entries.
    """
    if strategy_class is None or (
            isinstance(strategy_class, str)
            and str.__len__(str.__str__(strategy_class)) == 0) or (
            not isinstance(strategy_class, str)
            and not strategy_class):
        raise ValueError(
            "catalogue rejected: a new archetype enters only under "
            "the fixed strategy class for a run: the strategy class "
            "stands absent or empty")
    before = archetype_catalogue(records)
    after = archetype_catalogue(_record_sequence(records) + [new_record])
    added = _base_get(new_record, "archetype_id")
    generated_rows = _guarded_copy(
        _base_get(new_record, "parameter_rows") or ())
    if not isinstance(generated_rows, list):
        generated_rows = list(generated_rows)
    return {
        "catalogue": after,
        "entries_before": len(before["entries"]),
        "entries_after": len(after["entries"]),
        "strategy_class": strategy_class,
        "version_stamp": {
            "entries_before": len(before["entries"]),
            "entries_after": len(after["entries"]),
            "added_archetype": added,
            "strategy_class": strategy_class,
            "standing": CATALOGUE_STANDING,
        },
        "family_labelling_before": list(before["entries"].keys()),
        "family_labelling_after": list(after["entries"].keys()),
        "generator_code_entry": {
            "archetype_id": added,
            "generator_signature": _base_get(
                new_record, "generator_signature"),
            "parameter_rows": generated_rows,
            "entry_form": "data and generator code at the edge",
        },
        "pricing_record": {
            "priced_work": (
                "the extension and labelling work of this addition"),
            "basis": "priced as plan work per addition",
            "figure": None,
            "figure_standing": (
                "no figure stated in the plan for this work"),
        },
    }


__all__ = [
    "DQ163_MARK",
    "CATALOGUE_STANDING",
    "OP11_GAPS",
    "CANONICAL_SCALE_SET",
    "COLD_SOCIETY_PROVENANCE",
    "COLD_SOCIETY_FIRST_DAYS",
    "NamedGeneratorFailure",
    "TRAVERSAL_DEPTH_BOUND",
    "GROUND_TRUTH_FIELDS",
    "BARRED_PROJECTION_KEYS",
    "RULE_STATE_FIELDS",
    "AgentState",
    "VouchEdge",
    "mod01_surface",
    "mod01_type",
    "make_archetype_record",
    "archetype_catalogue",
    "catalogue",
    "catalogue_record",
    "catalogue_gaps",
    "brief_head_words_are_catalogue",
    "run_headline_reportable",
    "canonical_scale_set",
    "scale_populations",
    "build_cast",
    "cast_agent_record",
    "cast_edge_record",
    "deliver_cast",
    "generate_society",
    "construct_farm",
    "build_farm",
    "zero_edge_society",
    "zero_edge_result",
    "archetype_behaviour",
    "generate_behaviour",
    "run_archetype",
    "generator_holds_rule_state",
    "validate_generator_output",
    "record_carries_ground_truth",
    "strip_ground_truth",
    "validate_detection_input",
    "validate_adjudication_input",
    "anchor_scenario",
    "build_anchor_scenario",
    "validate_anchor_scenario",
    "empty_anchor_set_case",
    "cold_society",
    "build_cold_society",
    "cold_society_degree",
    "cold_degree_provenance",
    "extend_catalogue",
]

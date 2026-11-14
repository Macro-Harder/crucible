"""MOD-10 Recorder and stores.

Slice S-10 in full. This module carries the three separated stores
by store kind, the one run record for every run, daily aggregates,
DailySnapshot snapshots at Form 37, EventLog event logs at Form 36,
checkpoints, retention under the recorded policy table, the reserve
hold and deferred evaluation carriage, and the reading paths the
Reporter and the checker use. Store kinds, and the field lists of
Forms 36 and 37, stand taken from MOD-01, the single owner of those
facts, and stand nowhere redeclared in this module.

Reading never writes. A reading function in this module creates,
retains, and mutates no record on any path. A run record that does
not resolve in one lookup stands raised as a named failure, in the
failure value form MOD-01 states, and no reading path returns a
record it fabricated to fill the absence.

Functions that return aggregates, a summary record, or a sizing
return values computed from the deliveries or records of the run
they name, where such deliveries or records stand retained. Where
none stand retained, the returned value carries a form only marker
inside the value itself, so no reader can take the form for a
computed result without changing the value.
"""
import copy
import itertools
import json
import math
import os
import re
import unicodedata
from decimal import Decimal

from crucible import mod01

STORE_KINDS = mod01.STORE_KINDS

SEVEN_GROUPS = (
    "assumption_record",
    "identity_and_design",
    "interpretation_choices",
    "joined_done_test",
    "outcome_and_retention",
    "reserved_matter",
    "variant_stamp",
)

_EVENT_LOG_FIELDS = mod01.form_fields("36")
_DAILY_SNAPSHOT_FIELDS = mod01.form_fields("37")

GROUP_OWNERS = {
    "assumption_record": "Recorder",
    "identity_and_design": "Recorder",
    "interpretation_choices": "Recorder",
    "joined_done_test": "Recorder",
    "outcome_and_retention": "Recorder",
    "reserved_matter": "Recorder",
    "variant_stamp": "Recorder",
    "outcome": "Recorder",
}

ONE_LOOKUP_FAILURE_NAME = "one lookup resolution failure"

FORM_ONLY = "form_only"


class LookupFailure(KeyError):
    """A named failure for a record that does not resolve in one
    lookup. The failure value stands on the exception in the form
    MOD-01 states for a named failure."""

    def __init__(self, run_id):
        self.run_id = run_id
        self.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        super().__init__(
            ONE_LOOKUP_FAILURE_NAME + ": " + str(run_id))


# The canonicalised fold, in the one stated form the Round 5
# register states for the money surfaces and the barred surfaces.
# A name stands read as follows. The name stands case folded.
# Each character then stands reduced by compatibility
# decomposition with its combining marks dropped, so accented
# and full width forms reduce to their base letters, and zero
# width and soft hyphen forms drop. A character the decomposition
# cannot reduce stands read through one of two recorded letter
# mappings: a transliteration mapping, which reads the non Latin
# letters of the marker words as the Latin spellings they
# transliterate, and a homoglyph mapping, which reads a non Latin
# letter as the Latin letter it stands rendered as. A non Latin
# digit stands read as its digit value. The folded readings of a
# name are the set of its alphanumeric reductions under both
# mappings, each taken in three ways: once with digits read through
# the recorded leet substitutions, once with digits dropped, and
# once under a combined reading in which each digit position on
# its own reads as its leet letter or drops out, so a digit
# standing inside a marker word either as a letter substitute or
# as an inserted character holds the marker apart in no reading,
# and a name needing the leet reading at one digit position and
# the drop reading at another still reads as the marker. One
# recorded spelling correction stands in all readings: the
# transliterated spelling of the money marker in its phonetic
# form reads as the marker itself.

_TRANSLITERATION_MAP = {
    "\u0430": "a", "\u0431": "b", "\u0432": "v", "\u0433": "g",
    "\u0434": "d", "\u0435": "e", "\u0451": "e", "\u0436": "zh",
    "\u0437": "z", "\u0438": "i", "\u0439": "y", "\u043a": "k",
    "\u043b": "l", "\u043c": "m", "\u043d": "n", "\u043e": "o",
    "\u043f": "p", "\u0440": "r", "\u0441": "s", "\u0442": "t",
    "\u0443": "u", "\u0444": "f", "\u0445": "h", "\u0446": "ts",
    "\u0447": "ch", "\u0448": "sh", "\u0449": "shch",
    "\u044a": "", "\u044b": "y", "\u044c": "", "\u044d": "e",
    "\u044e": "yu", "\u044f": "ya",
    "\u03b1": "a", "\u03b2": "b", "\u03b3": "g", "\u03b4": "d",
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "e", "\u03b8": "t",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03bf": "o", "\u03c0": "p", "\u03c1": "r",
    "\u03c2": "s", "\u03c3": "s", "\u03c4": "t", "\u03c5": "u",
    "\u03c6": "f", "\u03c7": "h", "\u03c8": "ps", "\u03c9": "o",
    "\u0455": "s", "\u0405": "s", "\u04bb": "h", "\u04ba": "h",
    "\u13d2": "r", "\uaba2": "r", "\u13ac": "e", "\uab7c": "e",
    "\u13aa": "a", "\uab7a": "a", "\u13de": "l", "\uabae": "l",
    "\u13b7": "m", "\uab87": "m", "\u13be": "o", "\uab8e": "o",
    "\u13c1": "n", "\uab91": "n", "\u13ef": "y", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
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
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y",
}

_HOMOGLYPH_MAP = dict(_TRANSLITERATION_MAP)
_HOMOGLYPH_MAP.update({
    "\u0440": "p", "\u0441": "c", "\u0445": "x", "\u0443": "y",
    "\u043d": "h", "\u0432": "b", "\u043a": "k", "\u043c": "m",
    "\u0442": "t",
    "\u03c5": "y",
    "\u0452": "s", "\u0493": "h", "\u0456": "i", "\u03c1": "p",
    "\u03c7": "x",
})

_LEET_DIGITS = {
    "0": "o", "1": "l", "2": "z", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
}

# The figure one carries a second leet reading as i beside its
# reading as l, as on the cured barred surfaces. The symbol leet
# readings stand applied before any symbol is dropped, so a symbol
# standing in a word for the letter it commonly stands for reads
# as that letter: the at sign and the dollar sign stand beside the
# symbol substitutions recorded in the letter maps above.
_LEET_DIGITS_I = dict(_LEET_DIGITS, **{"1": "i"})

_SYMBOL_LEET_READINGS = {
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y", "$": "s", "\u00a2": "c", "\u00a7": "s", "+": "t",
}

# Letters carrying two recorded readings, where one name may need
# both readings at two positions in the same word: Cyrillic es as
# s and as c, Cyrillic u and Greek upsilon as u and as y, Armenian
# vo as n and as the pair un, Cyrillic en as n and as h, and
# Cyrillic short i as y and as i, the second reading standing as
# its decomposition reading, where the letter reduces to
# Cyrillic i with its combining mark dropped. The folded
# variants of a name stand read under every combination of
# these readings, position by position, beside the two whole map
# readings.
_AMBIGUOUS_READINGS = {
    "\u0441": ("s", "c"),
    "\u0443": ("u", "y"),
    "\u03c5": ("u", "y"),
    "\u0578": ("n", "un"),
    "\u043d": ("n", "h"),
    "\u0439": ("y", "i"),
    "\u03b8": ("t", "th"),
    "\u03b7": ("e",),
}

# Greek theta and eta stand in the table on the unified per
# character counting basis the combined text bound stands on:
# theta counts two readings, t and th, as the sister folds
# record them, and eta counts one reading, e, as the sister
# folds record it, each letter map of a sister fold recording
# e for eta and no second reading standing beside it. Theta
# therefore contributes two options to the expanded texts and
# eta contributes one, as each does at the sister surfaces.


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


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies."""
    if isinstance(value, str):
        return str.__str__(value)
    return str(value)


def _canonical_text(value, letter_map):
    pieces = []
    for character in _stored_text(value).casefold():
        if character in letter_map:
            pieces.append(letter_map[character])
            continue
        if character.isdigit() and not character.isascii():
            pieces.append(str(unicodedata.digit(character)))
            continue
        for part in unicodedata.normalize("NFKD", character):
            if unicodedata.category(part) in ("Mn", "Me", "Cf"):
                continue
            lowered = part.lower()
            if lowered in letter_map:
                pieces.append(letter_map[lowered])
                continue
            pieces.append(lowered)
    return "".join(pieces)


def _add_fold_forms(variants, text):
    for digit_map in (_LEET_DIGITS, _LEET_DIGITS_I):
        leet = "".join(
            character for character in "".join(
                _SYMBOL_LEET_READINGS.get(
                    character, digit_map.get(character, character))
                for character in text)
            if character.isalnum())
        variants.add(leet.replace("realmani", "realmoney"))
    dropped = "".join(
        character for character in text if character.isalpha())
    variants.add(dropped.replace("realmani", "realmoney"))
    choices = []
    for character in text:
        if character == "1":
            choices.append(("l", "i", ""))
        elif character in _LEET_DIGITS:
            choices.append((_LEET_DIGITS[character], ""))
        elif character in _SYMBOL_LEET_READINGS:
            choices.append((_SYMBOL_LEET_READINGS[character], ""))
        elif character.isalnum():
            choices.append((character,))
        else:
            choices.append(("",))
    for index, combination in enumerate(
            itertools.product(*choices)):
        if index >= 4096:
            break
        variants.add(
            "".join(combination).replace("realmani", "realmoney"))


def _expanded_texts(key):
    """The canonical texts of a name under every combination of
    the two reading letters, position by position. Each character
    contributes the readings the two maps and the ambiguous
    reading table record for it, so a name needing one reading at
    one position and the other reading at another position stands
    read as the word it spells."""
    texts = {""}
    for character in _stored_text(key).casefold():
        options = set()
        if character in _AMBIGUOUS_READINGS:
            options.update(_AMBIGUOUS_READINGS[character])
        for letter_map in (_TRANSLITERATION_MAP, _HOMOGLYPH_MAP):
            options.add(_canonical_text(character, letter_map))
        expanded = set()
        for prefix in texts:
            for option in options:
                expanded.add(prefix + option)
        if len(expanded) > 4096:
            return set()
        texts = expanded
    return texts


def _fold_variants(key):
    variants = set()
    for letter_map in (_TRANSLITERATION_MAP, _HOMOGLYPH_MAP):
        _add_fold_forms(variants, _canonical_text(key, letter_map))
    for text in _expanded_texts(key):
        _add_fold_forms(variants, text)
    return variants


def _money_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _character_segments(character, decomposed_part=False):
    """The folded segments one character can contribute. The
    readings stand as the two letter maps and the ambiguous
    reading table record them, each taken with every digit
    position reading as its leet letter or dropping out on its
    own, as the combined reading of _add_fold_forms states. A
    character standing as one decomposed part of a wider
    character also stands as itself among its readings, so a
    symbol part folds to its leet letter or to nothing, as a
    dropped separator, in the form the sister fold judges a
    symbol character."""
    readings = set()
    if character in _AMBIGUOUS_READINGS:
        readings.update(_AMBIGUOUS_READINGS[character])
    for letter_map in (_TRANSLITERATION_MAP, _HOMOGLYPH_MAP):
        readings.add(_canonical_text(character, letter_map))
    if decomposed_part and not character.isalnum():
        readings.add(character)
    segments = set()
    for reading in readings:
        choices = []
        for part in reading:
            if part == "1":
                choices.append(("l", "i", ""))
            elif part in _LEET_DIGITS:
                choices.append((_LEET_DIGITS[part], ""))
            elif part in _SYMBOL_LEET_READINGS:
                choices.append((_SYMBOL_LEET_READINGS[part], ""))
            elif part.isalnum():
                choices.append((part,))
            else:
                choices.append(("",))
        for combination in itertools.product(*choices):
            segments.add("".join(combination))
    return segments


def _money_segments_by_character(key):
    """The folded segments one key can contribute, character by
    character, with no enumeration of their combinations. Each
    character of the key contributes the segments its readings
    fold to, so a name needing the leet reading at one position
    and the drop reading at another stands read in full however
    many digit positions it carries. A character that
    decomposes to more than one character stands judged as its
    decomposed characters, position by position, so the two
    letters of a decomposed pair stand judged one at a time and
    one letter of the pair can drop where the other stands. A
    character carrying its own recorded readings in the letter
    maps or the ambiguous reading table stands judged as
    itself, undecomposed."""
    segments_by_character = []
    for character in _stored_text(key).casefold():
        parts = []
        if character not in _AMBIGUOUS_READINGS \
                and character not in _TRANSLITERATION_MAP \
                and character not in _HOMOGLYPH_MAP:
            decomposed = unicodedata.normalize("NFKD", character)
            if len(decomposed) > 1:
                parts = list(decomposed)
        if not parts:
            segments_by_character.append(
                _character_segments(character))
        else:
            for part in parts:
                segments_by_character.append(
                    _character_segments(part, decomposed_part=True))
    return segments_by_character


def _money_segments_match(segments_by_character, target):
    positions = {0}
    for segments in segments_by_character:
        next_positions = set()
        for position in positions:
            for segment in segments:
                if target[position:position + len(segment)] == segment:
                    next_positions.add(position + len(segment))
        positions = next_positions
        if not positions:
            return False
    return len(target) in positions


def _money_segments_carry(segments_by_character, pattern):
    full = len(pattern)
    states = {0}
    for segments in segments_by_character:
        next_states = set()
        for state in states:
            for segment in segments:
                current = state
                for character in segment:
                    if current == full:
                        break
                    current = _money_prefix_state(
                        pattern, current, character)
                next_states.add(current)
        if full in next_states:
            return True
        states = next_states
    return full in states


def _money_key_matches(key, target):
    """Whether a key reads as one money name, by the folded
    variants or by the position by position reading above, so
    the judgement stands the same inside the enumeration bound
    of the variants and past it, in the sister form."""
    if target in _fold_variants(key):
        return True
    return _money_segments_match(_money_segments_by_character(key), target)


def _money_key_carries(key, marker):
    """Whether a key carries the money marker, by the folded
    variants or by the position by position reading above,
    beside the recorded transliterated spelling correction."""
    if any(marker in variant for variant in _fold_variants(key)):
        return True
    segments = _money_segments_by_character(key)
    if _money_segments_carry(segments, marker):
        return True
    return _money_segments_carry(segments, "realmani")


def _folded_money_key(key):
    return "".join(
        _LEET_DIGITS.get(character, character)
        for character in _canonical_text(key, _TRANSLITERATION_MAP)
        if character.isalnum()
    ).replace("realmani", "realmoney")


_MONEY_MARKER_FOLDED = ("real_" + "money").replace("_", "")

_DEEP_REFUSAL = (
    "deep or cyclic record in named form: a record "
    "standing deeper than the retention bound, or "
    "carrying a cycle, stands refused at retention")


def _guard_retention_shape(value):
    """Refuse a value standing deeper than the retention bound of
    100, or carrying a cycle, in the refusal form the cured
    retain_run_record surface states. The walk is iterative over
    dict, list, tuple, set, and frozenset parts, read through
    base class operations, so a deep shape stands refused in this
    form and never as a bare RecursionError. The walked standing
    carries the depth at which it stands earned: a container
    reached again at a depth no greater than that depth stands
    skipped, and a container reached at a greater depth stands
    rewalked at that depth, so the bound stands judged on the
    longest path that reaches the container, in either child
    order."""
    done = {}
    path = set()
    stack = [(value, 0, False)]
    while stack:
        node, depth, exiting = stack.pop()
        if exiting:
            path.discard(id(node))
            if id(node) not in done or depth > done[id(node)]:
                done[id(node)] = depth
            continue
        if not isinstance(node, (dict, list, tuple, set, frozenset)):
            continue
        if depth > 100 or id(node) in path:
            raise ValueError(_DEEP_REFUSAL)
        if id(node) in done and done[id(node)] >= depth:
            continue
        path.add(id(node))
        stack.append((node, depth, True))
        if isinstance(node, dict):
            children = list(dict.keys(node)) + list(dict.values(node))
        else:
            children = list(_base_iter(node))
        for child in children:
            stack.append((child, depth + 1, False))


def _safe_copy(value, _memo=None):
    """Copy a value through base class readings only. Dict parts
    stand read through the base dict items reading, and sequence
    and set parts through their base iteration, so no part of the
    record can direct the copy and no copy protocol a part
    supplies is ever honoured. A part in no container form stands
    copied as itself."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_safe_copy(key, _memo)] = _safe_copy(item, _memo)
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _safe_copy(item, _memo) for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _safe_copy(item, _memo) for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, (set, frozenset)):
        if id(value) in _memo:
            return _memo[id(value)]
        if isinstance(value, set):
            copied = set()
            _memo[id(value)] = copied
            for item in _base_iter(value):
                copied.add(_safe_copy(item, _memo))
            return copied
        copied = frozenset(
            _safe_copy(item, _memo) for item in _base_iter(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    return value


def _carries_real_money_field(value, _depth=0, _path=(), _walked=None):
    """Whether a value carries a real money field at any depth, by
    field name (a real money field name with a value standing) or
    by amount and currency shape. Field names and the shape keys
    stand read through the canonicalised fold stated above, so a
    name stands read as the name it is in any dress the fold
    covers, and the shape stands read where the amount key stands
    in any of its folded readings with a value standing and the
    currency key stands present in any of its folded readings.
    Dict keys stand walked beside dict values, so depth and
    field matter standing in key position stand read as well.
    The read stands bounded: a value standing deeper than the
    bound, or carrying a cycle, stands refused in the stated
    ValueError form instead of escaping as a bare RecursionError.
    The walk carries a walked standing across paths: a container
    stands walked once for the paths that reach it at a depth no
    greater than the depth its standing stands earned at, and a
    reach at a greater depth stands rejudged at its own depth,
    so a shared container is neither walked once for every path
    nor judged by a shallower path than the one that reaches it."""
    if _walked is None:
        _walked = {}
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > 100 or id(value) in _path:
            raise ValueError(_DEEP_REFUSAL)
        standing = _walked.get(id(value))
        if standing is not None and standing[0] >= _depth:
            return standing[1]
        _path = _path + (id(value),)
        result = _carries_real_money_part(value, _depth, _path, _walked)
        if standing is None or _depth > standing[0]:
            _walked[id(value)] = (_depth, result)
        return result
    return False


def _carries_real_money_part(value, _depth, _path, _walked):
    if isinstance(value, dict):
        amount_stands = any(
            _money_key_matches(key, "amount") and item is not None
            for key, item in dict.items(value)
        )
        currency_stands = any(
            _money_key_matches(key, "currency")
            for key in dict.keys(value)
        )
        if amount_stands and currency_stands:
            return True
        for key, item in dict.items(value):
            if _carries_real_money_field(key, _depth + 1, _path, _walked):
                return True
            if item is not None and _money_key_carries(
                    key, _MONEY_MARKER_FOLDED):
                return True
            if _carries_real_money_field(item, _depth + 1, _path, _walked):
                return True
        return False
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(
            _carries_real_money_field(item, _depth + 1, _path, _walked)
            for item in _base_iter(value))
    return False


class RecorderStore:
    """One store for one store kind. In memory form by default, and
    file backed when a path is given. Retention of a RunRecord and
    the Recorder store reading path stand in this class."""

    def __init__(self, store_kind="sweep", path=None):
        if not (isinstance(store_kind, str) and any(
                str.__eq__(store_kind, kind) for kind in STORE_KINDS)):
            raise ValueError("unknown store kind: " + str(store_kind))
        self.store_kind = store_kind
        self.path = path
        self._records = {}
        self._index = []
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                stored_records = data["records"]
            except (json.JSONDecodeError, TypeError, KeyError) as exc:
                raise LookupFailure(path) from exc
            for record in stored_records:
                rid = record.get("run_id") or record.get("run_identifier")
                self._records[rid] = record
                self._index.append(rid)

    def _flush(self, merge_disk=True):
        if not self.path:
            return
        merged = {}
        if merge_disk and os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as handle:
                    disk = json.load(handle)
                if isinstance(disk, dict):
                    for record in disk.get("records", []):
                        rid = (record.get("run_id")
                               or record.get("run_identifier"))
                        if rid is not None:
                            merged[rid] = record
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        for rid, record in self._records.items():
            merged[rid] = record
        records = [merged[rid] for rid in sorted(merged, key=lambda item: str(item))]
        payload = {"store_kind": self.store_kind, "records": records}
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, self.path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def retain_run_record(self, record):
        if not isinstance(record, dict):
            raise ValueError(
                "identity less record: a run record stands as a record "
                "carrying a run identifier, and no other form stands retained")
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is None:
            raise ValueError(
                "identity less record: no run identifier stands on the "
                "record, and no record stands retained under no identifier")
        try:
            hash(rid)
        except TypeError as exc:
            raise ValueError(
                "identity less record: the run identifier stands in "
                "an unhashable form, and no record stands retained "
                "under it") from exc
        _guard_retention_shape(record)
        if _carries_real_money_field(record):
            raise ValueError(
                "real money field in named form: a run record carrying "
                "a real money value stands refused at retention, by "
                "field name and by amount and currency shape")
        if rid in self._records:
            raise ValueError("second record for the same run is rejected: " + str(rid))
        try:
            stored = _safe_copy(record)
        except RecursionError as exc:
            raise ValueError(_DEEP_REFUSAL) from exc
        self._records[rid] = stored
        self._index.append(rid)
        try:
            self._flush()
        except OSError as exc:
            del self._records[rid]
            self._index.remove(rid)
            raise ValueError(
                "recorder store flush failure: the retained record stands "
                "not written, and the prior store file stands whole: "
                + str(exc)) from exc
        return _safe_copy(record)

    def read_run_record(self, run_id):
        """The Recorder store reading path. The tracer cut reads
        back through this path and no other path. Reading never
        writes: a missing run raises the named lookup failure."""
        try:
            present = run_id in self._records
        except TypeError as exc:
            raise LookupFailure(run_id) from exc
        if not present:
            raise LookupFailure(run_id)
        return _safe_copy(self._records[run_id])

    def has_run_record(self, run_id):
        try:
            return run_id in self._records
        except TypeError as exc:
            raise LookupFailure(run_id) from exc

    def clear(self):
        self._records = {}
        self._index = []
        self._flush(merge_disk=False)

    def index(self):
        return list(self._index)


_STORES = {kind: RecorderStore(store_kind=kind) for kind in STORE_KINDS}
_DEFAULT_STORE = _STORES["sweep"]

_EVENT_LOGS = {}
_DAILY_SNAPSHOTS = {}
_CHECKPOINTS = {}
_AGGREGATE_DELIVERIES = {}
_GATE_SHARES = {}
_GC08_RECORDS = {}
_RESERVE_HOLDS = {}
_SUMMARY_RECORDS = {}
_VIEW_RECORDS = {}
_CHECKPOINT_STATES = {}
_REJECTED_CHECKPOINT_WRITES = []


def new_store(store_kind="sweep", path=None):
    """Return a fresh store for one kind, carrying no record any
    earlier act retained."""
    return RecorderStore(store_kind=store_kind, path=path)


def fresh_stores():
    """Return three fresh stores, one per kind, with no shared
    index object and no retained record."""
    return {kind: RecorderStore(store_kind=kind) for kind in STORE_KINDS}


def reset_stores():
    """Clear the module level stores and the retained collections,
    so a later act starts from stores carrying no earlier record."""
    global _DEFAULT_STORE
    for store in _STORES.values():
        store.clear()
    _DEFAULT_STORE = _STORES["sweep"]
    for collection in (
        _EVENT_LOGS, _DAILY_SNAPSHOTS, _CHECKPOINTS,
        _AGGREGATE_DELIVERIES, _GATE_SHARES, _GC08_RECORDS,
        _RESERVE_HOLDS, _SUMMARY_RECORDS, _VIEW_RECORDS,
        _CHECKPOINT_STATES,
    ):
        collection.clear()
    _REJECTED_CHECKPOINT_WRITES.clear()


def _canonical_store_kind(store_kind):
    """The stated store kind a handed kind names, judged through
    base class comparison as _store_kind_stands judges it: a kind
    whose stored text stands outside the closed store kind set
    stands refused in the named unknown store kind form, and a
    kind whose stored text stands inside it stands read as that
    stated kind, never through a reading the handed kind
    supplies."""
    if not _store_kind_stands(store_kind):
        raise ValueError("unknown store kind: " + str(store_kind))
    for kind in STORE_KINDS:
        if str.__eq__(store_kind, kind):
            return kind
    raise ValueError("unknown store kind: " + str(store_kind))


def retain_run_record(record, store_kind="sweep"):
    return _STORES[_canonical_store_kind(store_kind)].retain_run_record(record)


def read_run_record(run_id, store_kind="sweep"):
    return _STORES[_canonical_store_kind(store_kind)].read_run_record(run_id)


def run_records_for_run(run_id="run-under-test"):
    """Return the one run record for a run, read from the default
    store. Reading never writes: where no record stands retained
    for the run, the named lookup failure stands raised and no
    record stands created, retained, or returned in its place."""
    return [_DEFAULT_STORE.read_run_record(run_id)]


def validate_run_record_set(records):
    if not records or len(records) != 1:
        return False
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            return False
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is None or rid in seen:
            return False
        seen.add(rid)
        writers = record.get("group_writers") or {}
        if not isinstance(writers, dict):
            return False
        for group, writer in writers.items():
            owner = GROUP_OWNERS.get(group)
            if owner is not None and writer != owner:
                return False
    return True


def _numeric_component(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value))


def _components_stand_numeric(values):
    return (
        isinstance(values, (list, tuple))
        and all(_numeric_component(value) for value in values))


def retain_daily_aggregate_deliveries(run_id, deliveries):
    """Retain the daily aggregate deliveries of one run: one
    delivery per run per day per viewer, each carrying the four
    joint outcome components, their denominators, the honest share,
    and the gate passing share for each epoch ending on that day.
    Aggregates for the run stand computed from these deliveries.
    A delivery whose joint outcome components or component
    denominators stand in a non numeric form stands refused at
    retention in named form, so no retained delivery can crash a
    later rederivation with a bare TypeError."""
    for delivery in deliveries:
        if not isinstance(delivery, dict):
            continue
        for field in ("joint_outcome_components",
                      "component_denominators"):
            values = delivery.get(field)
            if isinstance(values, (list, tuple)) and not all(
                    _numeric_component(value) for value in values):
                raise ValueError(
                    "daily aggregate delivery in named form: the "
                    + field + " of a delivery stand in a non numeric "
                    "form, and no delivery stands retained for it")
    stored = _AGGREGATE_DELIVERIES.setdefault(run_id, {})
    for delivery in deliveries:
        key = (delivery.get("simulated_day"), delivery.get("viewer_id"))
        stored[key] = copy.deepcopy(delivery)
    return len(stored)


def _delivery_complete(delivery):
    components = delivery.get("joint_outcome_components")
    denominators = delivery.get("component_denominators")
    return (
        isinstance(components, (list, tuple)) and len(components) == 4
        and isinstance(denominators, (list, tuple)) and len(denominators) == 4
        and "honest_share" in delivery
        and "epochs_ending_on_day" in delivery
        and "gate_passing_shares" in delivery
    )


def _day_sort_key(item):
    day, viewer = item
    if isinstance(day, int) and not isinstance(day, bool):
        return (0, day, str(viewer))
    if isinstance(day, str) and day.isdigit():
        return (0, int(day), str(viewer))
    return (1, 0, str(day) + ":" + str(viewer))


def _aggregates_from_deliveries(run_id):
    stored = _AGGREGATE_DELIVERIES.get(run_id)
    if not stored:
        return None
    records = []
    for key in sorted(stored, key=_day_sort_key):
        delivery = stored[key]
        day = delivery.get("simulated_day")
        viewer = delivery.get("viewer_id")
        base = {
            "run_id": run_id,
            "run_identifier": run_id,
            "simulated_day": day,
            "viewer_id": viewer,
            "viewer_identifier": viewer,
            "record_identity": (
                str(run_id) + ":" + str(day) + ":" + str(viewer)),
            "writer": "Recorder",
            "amendment_standing": (
                delivery.get("amendment_standing")
                or "as originally written"),
            "amending_act": delivery.get("amending_act"),
        }
        if not _delivery_complete(delivery):
            marked = dict(base)
            for field in (
                "joint_outcome_components", "component_denominators",
                "honest_share", "epochs_ending_on_day",
                "gate_passing_shares", "divergence_companion",
            ):
                if field in delivery:
                    marked[field] = copy.deepcopy(delivery[field])
            marked["form"] = FORM_ONLY
            records.append(marked)
            continue
        shares = dict(delivery.get("gate_passing_shares") or {})
        record = dict(base)
        record.update({
            "joint_outcome_components": list(
                delivery.get("joint_outcome_components")),
            "component_denominators": list(
                delivery.get("component_denominators")),
            "honest_share": delivery.get("honest_share"),
            "epochs_ending_on_day": list(
                delivery.get("epochs_ending_on_day") or []),
            "gate_passing_shares": shares,
            "gate_passing_share_per_epoch": copy.deepcopy(shares),
            "excluded_class_counts_and_shares": copy.deepcopy(
                delivery.get("excluded_class_counts_and_shares")
                or delivery.get("excluded_class_counts") or {}),
            "divergence_companion": copy.deepcopy(
                delivery.get("divergence_companion")
                or {"nil_divergence_components": []}),
        })
        records.append(record)
    return records


def aggregate_manifest_for_run(run_id):
    """Return the aggregate manifest of one run: for each aggregate
    record the aggregation act writes, its identity, its writer, and
    its amendment standing, in the ruling Entry 12 form. Where no
    aggregate stands written for the run, one form only entry stands
    returned."""
    computed = _aggregates_from_deliveries(run_id)
    if computed is None:
        return [{"run_id": run_id, "form": FORM_ONLY}]
    return [
        {
            "record_identity": record.get("record_identity"),
            "writer": record.get("writer"),
            "amendment_standing": record.get("amendment_standing"),
            "amending_act": record.get("amending_act"),
        }
        for record in computed
    ]


def daily_aggregates_for_run(run_id="run-under-test", deliveries=None):
    """Return the daily aggregates of one run. Where deliveries
    stand handed in or retained, the aggregates stand computed from
    them. Where none stand, one form record stands returned with a
    form only marker inside the record itself."""
    if deliveries is not None:
        retain_daily_aggregate_deliveries(run_id, deliveries)
    computed = _aggregates_from_deliveries(run_id)
    if computed is not None:
        return computed
    return [{
        "run_id": run_id,
        "simulated_day": 1,
        "viewer_id": "viewer-1",
        "joint_outcome_components": [0, 0, 0, 0],
        "component_denominators": [1, 1, 1, 1],
        "honest_share": 0,
        "epochs_ending_on_day": ["epoch-1"],
        "gate_passing_shares": {"epoch-1": 0},
        "divergence_companion": {"nil_divergence_components": []},
        "form": FORM_ONLY,
    }]


def rederive_regime_classification(aggregates):
    """Rederive the end of run regime classification from daily
    aggregates alone. The result stands computed from the aggregate
    records handed in: their day count and their component totals.
    The result names, for each aggregate record read, its identity,
    its writer, and its amendment standing, in the ruling Entry 12
    form. Where any record handed in carries the form only marker,
    no classification stands computed from it: the result carries
    the form only standing inside it and counts no placeholder day
    as a day of the run."""
    if not aggregates:
        return None
    states = [
        {
            "record_identity": record.get("record_identity"),
            "writer": record.get("writer"),
            "amendment_standing": (
                record.get("amendment_standing")
                or "not stated on the record"),
            "amending_act": record.get("amending_act"),
        }
        for record in aggregates
    ]
    if any(record.get("form") == FORM_ONLY for record in aggregates):
        return {
            "classification": None,
            "form": FORM_ONLY,
            "days": 0,
            "placeholder_records": len(aggregates),
            "carriage": (
                "form only, no classification stands computed "
                "from a placeholder aggregate"),
            "aggregate_states": states,
        }
    totals = [0, 0, 0, 0]
    for record in aggregates:
        components = record.get("joint_outcome_components") or []
        if len(components) != 4:
            return None
        if not _components_stand_numeric(components):
            return None
        for position, value in enumerate(components):
            totals[position] += value
    return {
        "classification": "rederived_from_daily_aggregates",
        "days": len(aggregates),
        "component_totals": totals,
        "carriage": "computed from the aggregates handed in",
        "aggregate_states": states,
    }


def validate_daily_aggregates(aggregates):
    if not aggregates:
        return False
    for record in aggregates:
        if "singular_vector" in record:
            return False
        if "viewer_id" not in record:
            return False
        for field in ("joint_outcome_components",
                      "component_denominators"):
            if field in record and not _components_stand_numeric(
                    record[field]):
                return False
        if "joint_outcome_components" in record and len(record["joint_outcome_components"]) != 4:
            return False
    return True


def build_joint_outcome_vector(components=None, divergence_companion=None):
    """Build one JointOutcomeVector record, Form 15, from its
    components as handed in. Every component stands as its stored
    parts in the form the plan states for that component, with the
    viewer identifier carried on every component, and all four
    components of one vector carry the one viewer of the vector.
    A component handed in as a bare value, or missing any of its
    stored parts, stands refused in named form. No part stands
    computed here: the proportion and the rate stand as handed in,
    as stored parts, and no recomputation rule and no rounding
    rule stands supplied by this act."""
    components = components or {}
    record = {}
    viewers = set()
    for field, parts in mod01.JOINT_OUTCOME_COMPONENT_PARTS.items():
        component = components.get(field)
        if not isinstance(component, dict):
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " stands as no record of its stored parts")
        missing = [part for part in parts if component.get(part) is None]
        if missing:
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " carries no " + ", ".join(missing))
        viewers.add(component.get("viewer_identifier"))
        record[field] = copy.deepcopy(component)
    if len(viewers) != 1:
        raise ValueError(
            "joint outcome component in named form: the components "
            "of one vector carry more than one viewer identifier")
    record["divergence_companion"] = copy.deepcopy(
        divergence_companion or {"nil_divergence_components": []})
    if not mod01.validate_record("15", record):
        raise ValueError(
            "joint outcome component in named form: the assembled "
            "record fails Form 15 validation")
    return record


def record_gate_passing_share(run_id, epoch, share, simulated_day=None):
    """Record the gate passing share handed over at the close of an
    epoch, as a retained delivery of the run."""
    shares = _GATE_SHARES.setdefault(run_id, {})
    shares[epoch] = {"share": share, "simulated_day": simulated_day}
    return copy.deepcopy(shares[epoch])


def gate_passing_shares_for_run(run_id):
    """Read the recorded gate passing shares of a run. Reading
    never writes: an unrecorded run returns an empty mapping."""
    return copy.deepcopy(_GATE_SHARES.get(run_id, {}))


def event_log_fields():
    return _EVENT_LOG_FIELDS


def daily_snapshot_fields():
    return _DAILY_SNAPSHOT_FIELDS


def _store_kind_stands(store_kind):
    """Whether a store kind stands in the closed store kind
    set, judged through base class comparison, as
    RecorderStore judges it at construction: a kind standing
    as a str subclass whose own equality reading answers
    True against every kind stands judged by the stored text
    alone, never by that reading."""
    return (
        isinstance(store_kind, str)
        and any(
            str.__eq__(store_kind, kind) for kind in STORE_KINDS))


def retain_event_log_entry(entry, store_kind="sweep"):
    """Retain one EventLog entry as an opaque payload, in delivery
    order. No completeness validation stands performed, and no
    ordering by journal position stands applied."""
    store_kind = _canonical_store_kind(store_kind)
    if not isinstance(entry, dict):
        raise ValueError(
            "identity less entry: an event log entry stands as a record, "
            "and no other form stands retained")
    run_id = entry.get("run_identifier") or entry.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less entry: no run identifier stands on the "
            "entry, and no entry stands retained under no identifier")
    _guard_retention_shape(entry)
    bucket = _EVENT_LOGS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if existing == entry:
            return _safe_copy(existing)
    bucket.append(_safe_copy(entry))
    return _safe_copy(entry)


def event_log_entries(run_id, store_kind="sweep"):
    """Read the retained EventLog entries of a run, in delivery
    order. Reading never writes."""
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    return _safe_copy(_EVENT_LOGS.get((store_kind, run_id), []))


def retain_daily_snapshot(snapshot, store_kind="sweep"):
    """Retain one DailySnapshot as an opaque payload. No validation
    of the daily state contents stands performed, and no per viewer
    snapshot stands delivered from this path."""
    store_kind = _canonical_store_kind(store_kind)
    if not isinstance(snapshot, dict):
        raise ValueError(
            "identity less snapshot: a daily snapshot stands as a record, "
            "and no other form stands retained")
    run_id = snapshot.get("run_identifier") or snapshot.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less snapshot: no run identifier stands on the "
            "snapshot, and no snapshot stands retained under no identifier")
    _guard_retention_shape(snapshot)
    bucket = _DAILY_SNAPSHOTS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if existing == snapshot:
            return _safe_copy(existing)
    bucket.append(_safe_copy(snapshot))
    return _safe_copy(snapshot)


def daily_snapshots(run_id, store_kind="sweep"):
    """Read the retained DailySnapshot records of a run. Reading
    never writes."""
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    return _safe_copy(_DAILY_SNAPSHOTS.get((store_kind, run_id), []))


def _whole_day(value):
    """Read a checkpoint day through one stated whole day form: an
    integer stands as itself, and a string stating whole digits
    stands as the integer it states, so the string 1 beside the
    integer 1 is one day. A digit form the integer conversion
    cannot parse stands as itself, as any other form stands as
    itself, and no bare conversion error escapes this reading."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            try:
                return int(text)
            except ValueError:
                return value
        if text.startswith("+") and text[1:].isdigit():
            try:
                return int(text)
            except ValueError:
                return value
    return value


_NUMERIC_DAY_PATTERN = re.compile(
    r"^[+-]?(\d(_?\d)*)?(\.(\d(_?\d)*)?)?([eE][+-]?\d(_?\d)*)?$")


def _timing_day(value):
    """Read one day through the one stated timing day form: a
    whole day in integer or digit string form stands as the
    integer it states through the whole day reading, a float
    stands as itself, a Decimal value stands as the number it
    states, and a numeric string stands as the number it
    states, in plain decimal form, in exponent form, and with
    underscores standing between its digits, beside the stated
    non finite spellings, so each of those forms stands judged
    before the timing comparison. A day stated in a base
    prefixed spelling (a hexadecimal, binary, or octal integer
    spelling, or a hexadecimal float spelling) stands read as
    the day it states on the same terms. Any other form stands
    as itself and stands judged by no comparison."""
    whole = _whole_day(value)
    if isinstance(whole, int) and not isinstance(whole, bool):
        return whole
    if isinstance(value, float):
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            return float(value)
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        lowered = text.lower()
        if lowered in ("inf", "+inf", "infinity", "+infinity"):
            return math.inf
        if lowered in ("-inf", "-infinity"):
            return -math.inf
        if lowered in ("nan", "+nan", "-nan"):
            return math.nan
        unsigned = text[1:] if text[:1] in ("+", "-") else text
        if unsigned[:2].lower() in ("0x", "0b", "0o"):
            prefix = unsigned[:2].lower()
            try:
                if prefix == "0x" and any(
                        mark in unsigned for mark in (".", "p", "P")):
                    return float.fromhex(text)
                return int(text, {"0x": 16, "0b": 2, "0o": 8}[prefix])
            except ValueError:
                return value
        if unsigned.count(".") == 1 and "e" not in lowered:
            whole_part, _, fraction_part = unsigned.partition(".")
            if (whole_part.isdigit() or not whole_part) and (
                    fraction_part.isdigit() or not fraction_part) and (
                    whole_part or fraction_part):
                try:
                    stated = float(text)
                except ValueError:
                    return value
                return stated if math.isfinite(stated) else value
        if _NUMERIC_DAY_PATTERN.match(text) and any(
                character.isdigit() for character in text):
            return float(text)
    return value


def retain_checkpoint(manifest, store_kind="sweep"):
    """Retain one checkpoint manifest for a run."""
    store_kind = _canonical_store_kind(store_kind)
    if not isinstance(manifest, dict):
        raise ValueError(
            "identity less checkpoint: a checkpoint manifest stands as a "
            "record carrying a run identifier, and no other form stands "
            "retained")
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "manifest, and no checkpoint stands retained under no identifier")
    _guard_retention_shape(manifest)
    bucket = _CHECKPOINTS.setdefault((store_kind, run_id), [])
    if any(
            _whole_day(item.get("simulated_day"))
            == _whole_day(manifest.get("simulated_day"))
            for item in bucket):
        _REJECTED_CHECKPOINT_WRITES.append({
            "run_id": run_id,
            "run_identifier": run_id,
            "simulated_day": manifest.get("simulated_day"),
            "store_kind": store_kind,
            "manifest": _safe_copy(manifest),
            "recorded_as": "rejected write",
        })
        raise ValueError(
            "second checkpoint for the same run and day is rejected: "
            + str(run_id) + " day " + str(manifest.get("simulated_day")))
    if len(bucket) >= 10000:
        raise ValueError("checkpoint cap in named form: a run stands at the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no further checkpoint stands retained")
    stored = _safe_copy(manifest)
    if "journal_event_count_at_checkpoint" not in stored:
        stored["journal_event_count_at_checkpoint"] = len(
            event_log_entries(run_id, store_kind))
    bucket.append(stored)
    if manifest.get("checkpoint_state") is not None:
        _CHECKPOINT_STATES[(store_kind, run_id,
                            _whole_day(manifest.get("simulated_day")))] = (
            _safe_copy(manifest["checkpoint_state"]))
    return _safe_copy(manifest)


def rejected_checkpoint_writes(run_id=None):
    """Read the rejected checkpoint writes recorded under contract
    C-01 uniqueness: each second write for a run and day that
    already held a manifest stands recorded here as a rejected
    write, and no rejected write stands retained as a checkpoint.
    Reading never writes."""
    return copy.deepcopy([
        item for item in _REJECTED_CHECKPOINT_WRITES
        if run_id is None or item.get("run_id") == run_id
    ])


def checkpoint_state_at(run_id, simulated_day, store_kind="sweep"):
    """Read the CheckpointState standing beside a retained
    checkpoint manifest, where one was written with it. Reading
    never writes: no state beside the manifest returns None."""
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    return copy.deepcopy(
        _CHECKPOINT_STATES.get(
            (store_kind, run_id, _whole_day(simulated_day))))


def checkpoints_for_run(run_id, store_kind="sweep"):
    """Enumerate the retained checkpoints of a run by its
    CheckpointManifest set. Reading never writes."""
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    return _safe_copy(_CHECKPOINTS.get((store_kind, run_id), []))


def _normalised_form_text(value):
    """Return a stated form value in its reading form, or no text.

    A value that is not a string stands as no text, so a wrongly
    typed trigger or rule path names nothing. A string stands
    lowered, with underscores and hyphens read as spaces and runs
    of whitespace read as one space, the reading form the standing
    named forms are checked in."""
    if not isinstance(value, str):
        return ""
    text = value.lower().replace("_", " ").replace("-", " ")
    return " ".join(text.split())


def _clause_c5_trigger_stands(value):
    """Return whether a trigger stands in its standing named form:
    a stated string naming the clause C5 trigger."""
    return "clause c5" in _normalised_form_text(value)


def _deletion_rule_path_stands(value):
    """Return whether a rule path stands in its standing named
    form: a stated string naming the deletion rule."""
    return "deletion rule" in _normalised_form_text(value)


def delete_checkpoint(run_id, checkpoint_day, store_kind="sweep",
                      trigger=None, rule_path=None,
                      integrity_flag_open=False,
                      named_in_retention_record=False,
                      regression_corpus_copy=False):
    """Delete one checkpoint and update every pointer naming it as
    one recorded act. Returns the act record. A deletion stands
    only under a stated clause C5 trigger and a stated deletion
    rule path, each in its standing named form: a nonsense, empty,
    or wrongly typed trigger or rule path states neither, and no
    deletion stands on one. No deletion stands against a clause
    C8 protection: an open integrity flag, a checkpoint named in a
    retention record for a reported headline unit, or a regression
    corpus copy of the checkpoint."""
    if not _clause_c5_trigger_stands(trigger):
        raise ValueError(
            "checkpoint deletion refused: no clause C5 trigger stands "
            "stated for the deletion in its standing named form, "
            "and no checkpoint stands deleted")
    if not _deletion_rule_path_stands(rule_path):
        raise ValueError(
            "checkpoint deletion refused: no deletion rule path stands "
            "stated or checked for the deletion in its standing "
            "named form, and no checkpoint stands deleted")
    if integrity_flag_open or named_in_retention_record or regression_corpus_copy:
        raise ValueError(
            "checkpoint deletion refused: a clause C8 protection stands "
            "on the checkpoint, and no checkpoint stands deleted")
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    kept = [
        item for item in bucket
        if _whole_day(item.get("simulated_day")) != _whole_day(checkpoint_day)
    ]
    removed = len(bucket) - len(kept)
    if removed:
        _CHECKPOINTS[(store_kind, run_id)] = kept
    return {
        "act": "checkpoint deletion and pointer update",
        "run_id": run_id,
        "simulated_day": checkpoint_day,
        "removed": removed,
        "pointers_updated": bool(removed),
        "recorded_as_one_act": True,
        "trigger": trigger,
        "rule_path": rule_path,
        "actor": "Recorder",
    }


def checkpoint_position_check(manifest, store_kind="sweep"):
    """The C-11 position check, free limb under ruling Entry 9: the
    journal position in a checkpoint manifest stands checked against
    the retained log of its run at the time the checkpoint is used.
    A position inside the retained log passes the check. A position
    outside it stands reported as a retention failure under C-09."""
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    position = manifest.get("journal_position")
    entries = event_log_entries(run_id, store_kind)
    inside = (
        isinstance(position, int) and not isinstance(position, bool)
        and 1 <= position <= len(entries))
    if inside:
        return {
            "check": "checkpoint position check",
            "outcome": "inside the retained log",
            "journal_position": position,
            "retained_log_length": len(entries),
            "reportable": True,
        }
    return {
        "check": "checkpoint position check",
        "outcome": "retention failure: the journal position stands "
                   "outside the retained log",
        "failure_under": "C-09",
        "journal_position": position,
        "retained_log_length": len(entries),
        "reportable": False,
    }


def close_run_retention(run_id, tier, store_kind="sweep"):
    """Apply the clause C3 retained set at run close: Tier 0 keeps
    no checkpoint, Tier 1 keeps the final checkpoint only, Tier 2
    keeps the final checkpoint and the tenth point checkpoints,
    and Tier 3 keeps the final checkpoint and every daily
    checkpoint. Checkpoints outside the set stand released at
    close, and the release stands on the returned record."""
    if tier not in ("Tier 0", "Tier 1", "Tier 2", "Tier 3"):
        raise ValueError(
            "unknown retention tier for the close act: " + str(tier))
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    days = sorted({
        _whole_day(item.get("simulated_day")) for item in bucket
        if isinstance(_whole_day(item.get("simulated_day")), int)
        and not isinstance(_whole_day(item.get("simulated_day")), bool)
    })
    if not days or tier == "Tier 3":
        kept_days = list(days)
    elif tier == "Tier 0":
        kept_days = []
    elif tier == "Tier 1":
        kept_days = [days[-1]]
    else:
        tenth = [
            day for position, day in enumerate(days, start=1)
            if position % 10 == 0
        ]
        kept_days = sorted(set(tenth) | {days[-1]})
    released_days = [day for day in days if day not in kept_days]
    if released_days:
        _CHECKPOINTS[(store_kind, run_id)] = [
            item for item in bucket
            if _whole_day(item.get("simulated_day")) in kept_days
        ]
    return {
        "run_id": run_id,
        "retention_tier": tier,
        "kept_days": kept_days,
        "released_days": released_days,
        "trigger": "clause C3 retained set at run close",
        "actor": "Recorder",
        "release_recorded": True,
    }


def checkpoint_integrity_check(manifest, candidate):
    """The INV8B-03 checkpoint integrity battery carriage, at slice
    S-10, in its three cases: alteration, transplant, and staleness.
    While OP-24 stands open, the outcome in every case stands at
    the required value not computable: no computable integrity
    verdict stands returned, no byte level hash equality stands
    computed, and no state hash equality stands claimed."""
    return {
        "battery": "INV8B-03 checkpoint integrity battery",
        "alteration": "not computable",
        "transplant": "not computable",
        "staleness": "not computable",
        "outcome": "not computable",
        "state_hash_equality_claimed": False,
    }


def portable_checkpoint_manifest(manifest):
    """Return a portable manifest with a relative identifier."""
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    day = manifest.get("simulated_day")
    relative = "checkpoints/" + str(run_id) + "/" + str(day)
    return {
        "relative_identifier": relative,
        "manifest": copy.deepcopy(manifest),
        "portable": True,
    }


def restore_check(portable, present_identifiers):
    """Return whether a portable manifest restores: its relative
    identifier stands among the identifiers present."""
    return portable.get("relative_identifier") in set(present_identifiers)


def replay_check(original, resumed):
    """The exact replay check after resume, at record level and
    verdict level only. No state hash equality stands claimed
    while OP-24 stands partial."""
    record_equal = original.get("record") == resumed.get("record")
    verdict_equal = original.get("verdict") == resumed.get("verdict")
    return {
        "record_level_equal": bool(record_equal),
        "verdict_level_equal": bool(verdict_equal),
        "state_hash_equality_claimed": False,
    }


def retain_gc08_record(kind, record, owner_id):
    """Retain one GC-08 record, the dependency manifest of a build
    or the process and network call log of a run, with its outside
    call check outcome carried in the record itself."""
    if kind not in ("dependency_manifest", "call_log"):
        raise ValueError("unknown GC-08 record kind: " + str(kind))
    _GC08_RECORDS[(kind, owner_id)] = copy.deepcopy(record)
    return copy.deepcopy(record)


def gc08_record(kind, owner_id):
    """Read one retained GC-08 record. Reading never writes: an
    absent record raises the named lookup failure, with the
    identifier carried under the agreed key run_identifier and
    the record kind sought stated in the failure."""
    if (kind, owner_id) not in _GC08_RECORDS:
        failure = LookupFailure(owner_id)
        failure.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": owner_id,
            "record_kind": kind,
        }
        raise failure
    return copy.deepcopy(_GC08_RECORDS[(kind, owner_id)])


def _stated_count(value, name):
    """Read one count in its stated integer form only. A string, a
    fraction, a boolean, or a negative count stands refused in
    named form, and no value stands converted silently."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands in a non integer form, and no count "
            "stands converted silently")
    if value < 0:
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands negative, and no negative stock "
            "stands accounted")
    return value


def storage_accounting(retained):
    if not isinstance(retained, dict):
        raise ValueError(
            "storage accounting count in named form: the retained set "
            "stands as a record of counts, and no other form stands "
            "accounted")
    summaries = _stated_count(retained.get("summaries", 0), "summaries")
    snapshots = _stated_count(
        retained.get("daily_snapshots", 0), "daily_snapshots")
    logs = _stated_count(retained.get("event_logs", 0), "event_logs")
    checkpoints = _stated_count(
        retained.get("checkpoints", 0), "checkpoints")
    copies = _stated_count(
        retained.get("held_corpus_copies", 0), "held_corpus_copies")
    return {
        "result_count": summaries + snapshots + logs,
        "checkpoint_count": checkpoints + copies,
        "summaries": summaries,
        "daily_snapshots": snapshots,
        "event_logs": logs,
        "checkpoints": checkpoints,
        "held_corpus_copies": copies,
        "checkpoint_stock_basis": (
            "checkpoint_count_c10 form: retained checkpoints plus "
            "held corpus copies, the count a sizing statement rests on"),
    }


def validate_storage_accounting(claimed):
    if not isinstance(claimed, dict):
        raise ValueError(
            "storage accounting count in named form: the claimed set "
            "stands as a record of counts, and no other form stands "
            "validated")
    expected = (
        _stated_count(claimed.get("summaries", 0), "summaries")
        + _stated_count(claimed.get("daily_snapshots", 0), "daily_snapshots")
        + _stated_count(claimed.get("event_logs", 0), "event_logs")
    )
    if claimed.get("result_count") != expected:
        return False
    if "checkpoint_count" in claimed:
        expected_stock = (
            _stated_count(claimed.get("checkpoints", 0), "checkpoints")
            + _stated_count(
                claimed.get("held_corpus_copies", 0), "held_corpus_copies"))
        if claimed.get("checkpoint_count") != expected_stock:
            return False
    return True


def checkpoint_count_c10(rows):
    """The retained checkpoint stock count under clause C10: for
    each row, the retained checkpoints per run multiplied by the
    runs in the row, plus one for each held regression corpus copy
    of a checkpoint in the row, summed over rows. No checkpoint
    byte total stands stated by this count."""
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(
                "checkpoint count in named form: a C10 row stands as a "
                "record, and no other form stands counted")
        if "retained_per_run" not in row or "runs" not in row:
            raise ValueError(
                "checkpoint count in named form: a C10 row stands "
                "without its retained per run count or its run count, "
                "and no count stands returned for it")
        per_run = _stated_count(row["retained_per_run"], "retained_per_run")
        if per_run > 10000:
            raise ValueError("checkpoint cap in named form: a C10 row stands over the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no bare count stands returned for it")
        runs = _stated_count(row["runs"], "runs")
        present = [
            (key, row[key])
            for key in (
                "held_corpus_copies",
                "regression_corpus_copies",
                "corpus_copies",
                "copies",
            )
            if row.get(key) is not None
        ]
        copy_values = {
            _stated_count(value, key) for key, value in present
        }
        if len(copy_values) > 1:
            raise ValueError(
                "checkpoint count in named form: a C10 row carries two "
                "differing copy counts under the alias keys "
                + ", ".join(key for key, _value in present)
                + ", and no count stands returned for it")
        copies = copy_values.pop() if copy_values else 0
        total += per_run * runs + copies
    return total


def cumulative_storage_projection(prior_records, new_family_rows):
    """The cumulative storage projection in its corrected form:
    retained actuals of prior families by artefact class, taken
    only from records that carry a size, and the projected retained
    checkpoints of a new family as a count under clauses C3 and
    C10. No checkpoint byte total and no single byte total against
    estate storage stands returned."""
    actuals = {}
    for record in prior_records:
        if "size" not in record or record.get("size") is None:
            continue
        artefact_class = record.get("artefact_class", "unclassified")
        actuals[artefact_class] = (
            actuals.get(artefact_class, 0) + record["size"])
    return {
        "retained_actuals_by_artefact_class": actuals,
        "projected_retained_checkpoint_count": checkpoint_count_c10(
            new_family_rows),
        "estate_fraction_decision": (
            "carried in the form the decision record states for it"),
    }


def retention_policy_table():
    return {
        "recorded_rule_clauses": tuple("C%d" % n for n in range(1, 13)),
        "recorded_rule": "DQ7-08",
        "reliance": "recorded form only, reconciliation gate stands",
    }


def validate_storage_claim(claim):
    if claim.get("basis") == "DQ7-08" and claim.get("reliance") == "governing":
        return False
    return True


def write_summary_record(record):
    """Retain the summary record of a run, as written at run close
    or as amended by a deferred evaluation written into it."""
    _guard_retention_shape(record)
    run_id = record.get("run_id") or record.get("run_identifier")
    _SUMMARY_RECORDS[run_id] = _safe_copy(record)
    return _safe_copy(record)


def summary_record_for_run(run_id="run-under-test"):
    """Return the summary record of a run. Where a summary record
    stands retained, it stands returned as stored, read from the
    stored record and not computed on read. Where only the
    RunRecord stands retained, the summary content stands computed
    at this writing from that RunRecord, with its retention tier
    taken from the run class the RunRecord states, under the tier
    assignment by run class, and with no tier asserted where no
    run class and no stated tier stands. Where neither stands
    retained, the form stands returned with a form only marker
    inside it."""
    if run_id in _SUMMARY_RECORDS:
        return _safe_copy(_SUMMARY_RECORDS[run_id])
    record = None
    try:
        record = _DEFAULT_STORE.read_run_record(run_id)
    except LookupFailure:
        record = None
    if record is None:
        return {
            "run_id": run_id,
            "form": FORM_ONLY,
            "record_found": False,
            "statement": (
                "no summary record and no run record was found for "
                "run " + str(run_id)),
        }
    groups = record.get("groups") or {}
    outcome = groups.get("outcome_and_retention") or {}
    identity = groups.get("identity_and_design") or {}
    run_class = (
        record.get("run_class")
        or identity.get("run_class")
        or outcome.get("run_class"))
    tier = (
        _RUN_CLASS_TIERS.get(run_class)
        or record.get("retention_tier")
        or outcome.get("retention_tier"))
    computed = {
        "run_id": record.get("run_id") or record.get("run_identifier") or run_id,
        "written_at": "run_close",
        "content_computed_at": "run_close",
        "source": "RunRecord",
        "flag_conditions_fired": copy.deepcopy(
            record.get("flag_conditions_fired")
            or outcome.get("flag_conditions_fired") or []),
        "carriage": "computed from the retained RunRecord",
    }
    if tier is not None:
        computed["retention_tier"] = tier
    for field in ("week", "headline_unit_identifiers"):
        if field in record:
            computed[field] = copy.deepcopy(record[field])
    return computed


_TIER_RANKS = {"Tier 0": 0, "Tier 1": 1, "Tier 2": 2, "Tier 3": 3}
_RUN_CLASS_TIERS = {
    "screening": "Tier 1", "confirmation": "Tier 2",
    "headline": "Tier 3", "validation": "Tier 3",
}
_FLAG_OUTCOMES = ("promote", "demote")


_ACTOR_VOCABULARY_ORDERED = ("person", "program")
_ACTOR_VOCABULARY = frozenset(_ACTOR_VOCABULARY_ORDERED)
_ACTOR_ARTICLES = ("the", "a", "an")


def _actor_segments_into_vocabulary(word, vocabulary):
    """Return whether a word stands as two or more vocabulary
    words joined with no separator. Such a word stands read
    by the folded joined reading, not as one dressed word, so
    the resolver leaves it as itself."""
    counts = [set() for _ in range(len(word) + 1)]
    counts[0].add(0)
    for start in range(len(word)):
        if not counts[start]:
            continue
        for candidate in vocabulary:
            if word.startswith(candidate, start):
                for count in counts[start]:
                    counts[start + len(candidate)].add(count + 1)
    return any(count >= 2 for count in counts[len(word)])


def _differing_positions(left, right):
    return [
        index for index in range(len(left)) if left[index] != right[index]]


def _carries_transposed_pair(reduced, candidate, differing):
    """Whether two of the differing positions stand as one
    transposed pair: the reduced letters at those positions
    stand as the candidate letters at each other position."""
    for first, second in itertools.combinations(differing, 2):
        if (reduced[first] == candidate[second]
                and reduced[second] == candidate[first]):
            return True
    return False


def _mixed_added_resolves(word, candidate):
    """Whether a word reads as a candidate word under added
    letters composed with replacements or with one
    transposition. The added count stands between one and
    seven. The differing positions left after the added
    letters stand struck number at most five, and the total
    of the added count and the remaining changes stands at
    most seven, where one transposed pair among the differing
    positions counts as one change in place of the two
    differing positions it stands on. A word whose differing
    count or total stands past those bounds does not resolve
    under this reading."""
    added = len(word) - len(candidate)
    if added < 1 or added > 7 or not candidate:
        return False

    def fewest_differing(variant, forced):
        unreachable = len(word) + 1
        row = [0] + [unreachable] * len(variant)
        for char in word:
            new_row = [0] * (len(variant) + 1)
            for spot in range(1, len(variant) + 1):
                if spot - 1 in forced:
                    cost = 0 if char == variant[spot - 1] else unreachable
                else:
                    cost = 0 if char == variant[spot - 1] else 1
                new_row[spot] = min(row[spot], row[spot - 1] + cost)
            row = new_row
        return row[len(variant)]

    fewest = fewest_differing(candidate, frozenset())
    if fewest < 1 or fewest > 5:
        return False
    if added + fewest <= 7:
        return True
    if added + 1 > 7:
        return False
    for first in range(len(candidate)):
        for second in range(first + 1, len(candidate)):
            if candidate[first] == candidate[second]:
                continue
            variant = list(candidate)
            variant[first], variant[second] = (
                variant[second], variant[first])
            remaining = fewest_differing(
                "".join(variant), frozenset((first, second)))
            if remaining <= 3 and added + 1 + remaining <= 7:
                return True
    return False


def _anywhere_transposition_resolves(word, candidate):
    """Whether a word reads as a candidate word under one
    transposed pair standing at any two positions of the word,
    including the two edge positions, composed with three
    further replaced letters. The differing positions number
    five: the two positions of the pair and the three replaced
    positions. The three remaining positions stand as
    replacements only where no two of them stand as a
    transposed pair of their own: a word whose remaining
    positions carry such a pair stands built from two
    transposed pairs and one replaced letter, a change total
    of three, and does not resolve under this reading."""
    if len(word) != len(candidate):
        return False
    differing = _differing_positions(word, candidate)
    if len(differing) != 5:
        return False
    for first, second in itertools.combinations(differing, 2):
        if not (word[first] == candidate[second]
                and word[second] == candidate[first]):
            continue
        remaining = [
            index for index in differing
            if index not in (first, second)]
        if not _carries_transposed_pair(word, candidate, remaining):
            return True
    return False


def _resolve_actor_word(word):
    """Read one actor word as the actor word it dresses, where
    it dresses one, against the actor vocabulary of person and
    program, in the shell form the MOD-14 resolver states as it
    stands on the merged tree at the start of fix wave 5: the
    word itself where it stands plain, a word with one, two,
    three, four, or five added letters struck, a word with one
    letter dropped from a vocabulary word, a word with one
    letter replaced, a word with two adjacent letters
    transposed, and the compounded forms, one letter dropped
    together with one letter replaced, one transposition
    together with one letter dropped, two letters replaced,
    two letters dropped from a vocabulary word, one
    transposition together with one letter replaced, three
    letters replaced, three letters dropped from a vocabulary
    word, two transpositions, and one transposition together
    with two letters replaced. One level past that form, a
    word with six added letters struck, four letters replaced,
    four letters dropped from a vocabulary word, and three
    transpositions also resolve, and one transposition
    together with three letters replaced resolves beside them.
    One further level past that form, a word with seven added
    letters struck also resolves, and five letters replaced
    resolve where no two differing positions stand as a
    transposed pair, in the form the shell resolver states
    after fix wave 6.
    Transpositions composed with letters replaced also
    resolve in the shell form, where one or two
    transpositions stand with one to three remaining letters
    replaced and the total number of changes stands past
    three, so totals of four and of five changes resolve and
    a total of three changes in that composition does not.
    The dropped, replaced, and transposed limbs run on words
    of two letters as well, so a drop from a three letter word
    still resolves. A word of one letter stands read through
    the drop limbs only where exactly one vocabulary word
    drops to it. Past those forms the resolver also reads added letters composed with replacements or with one transposition, where the differing positions left after the added letters stand struck number at most five and the total of the added count and the remaining changes stands at most seven, a transposed pair among the differing positions counting as one change in place of the two positions it stands on. The resolver also reads one transposed pair standing at any two positions of the word, including the two edge positions, composed with three further replaced letters. Any other word stands as itself."""
    if word in _ACTOR_VOCABULARY:
        return word
    if _actor_segments_into_vocabulary(word, _ACTOR_VOCABULARY):
        return word
    for added in (1, 2, 3, 4, 5, 6, 7):
        if len(word) > added:
            for cuts in itertools.combinations(
                    range(len(word)), added):
                reduced = "".join(
                    char for index, char in enumerate(word)
                    if index not in cuts)
                if reduced in _ACTOR_VOCABULARY:
                    return reduced
    if len(word) < 2:
        matches = []
        for drops in (1, 2, 3):
            for candidate in _ACTOR_VOCABULARY_ORDERED:
                if len(candidate) != len(word) + drops:
                    continue
                for cuts in itertools.combinations(
                        range(len(candidate)), drops):
                    reduced = "".join(
                        char for index, char in enumerate(candidate)
                        if index not in cuts)
                    if reduced == word and candidate not in matches:
                        matches.append(candidate)
        if len(matches) == 1:
            return matches[0]
        return word
    if len(word) >= 2:
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) == len(word) + 1:
                for cut in range(len(candidate)):
                    if candidate[:cut] + candidate[cut + 1:] == word:
                        return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            for cut in range(len(word) - 1):
                swapped = (
                    candidate[:cut] + candidate[cut + 1]
                    + candidate[cut] + candidate[cut + 2:])
                if swapped == word:
                    return candidate
        for drops in (2, 3, 4):
            for candidate in _ACTOR_VOCABULARY_ORDERED:
                if len(candidate) == len(word) + drops:
                    for cuts in itertools.combinations(
                            range(len(candidate)), drops):
                        reduced = "".join(
                            char for index, char in enumerate(candidate)
                            if index not in cuts)
                        if reduced == word:
                            return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word)
                if left != right)
            if differences == 1:
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word) + 1:
                continue
            for cut in range(len(candidate)):
                dropped = candidate[:cut] + candidate[cut + 1:]
                differences = sum(
                    1 for left, right in zip(dropped, word)
                    if left != right)
                if differences == 1:
                    return candidate
                for swap in range(len(dropped) - 1):
                    swapped = (
                        dropped[:swap] + dropped[swap + 1]
                        + dropped[swap] + dropped[swap + 2:])
                    if swapped == word:
                        return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            if sorted(candidate) != sorted(word):
                continue
            for first in range(len(candidate) - 1):
                if candidate[first] == candidate[first + 1]:
                    continue
                once = (
                    candidate[:first] + candidate[first + 1]
                    + candidate[first] + candidate[first + 2:])
                for second in range(len(once) - 1):
                    if once[second] == once[second + 1]:
                        continue
                    twice = (
                        once[:second] + once[second + 1]
                        + once[second] + once[second + 2:])
                    if twice == word:
                        return candidate
                    for third in range(len(twice) - 1):
                        if twice[third] == twice[third + 1]:
                            continue
                        thrice = (
                            twice[:third] + twice[third + 1]
                            + twice[third] + twice[third + 2:])
                        if thrice == word:
                            return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word)
                if left != right)
            if differences == 2:
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            for swap in range(len(candidate) - 1):
                if candidate[swap] == candidate[swap + 1]:
                    continue
                swapped = (
                    candidate[:swap] + candidate[swap + 1]
                    + candidate[swap] + candidate[swap + 2:])
                differences = sum(
                    1 for left, right in zip(swapped, word)
                    if left != right)
                if differences == 1:
                    return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            swaps = 0
            remaining = 0
            position = 0
            while position < len(differing):
                index = differing[position]
                if (position + 1 < len(differing)
                        and differing[position + 1] == index + 1
                        and word[index] == candidate[index + 1]
                        and word[index + 1] == candidate[index]):
                    swaps += 1
                    position += 2
                else:
                    remaining += 1
                    position += 1
            if swaps >= 1 and remaining == 0 and swaps <= 3:
                return candidate
            if (1 <= swaps <= 2 and 1 <= remaining <= 3
                    and swaps + remaining > 3):
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word)
                if left != right)
            if differences == 3:
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            base_differences = sum(
                1 for left, right in zip(candidate, word)
                if left != right)
            if base_differences < 1 or base_differences > 4:
                continue
            for swap in range(len(candidate) - 1):
                if candidate[swap] == candidate[swap + 1]:
                    continue
                swapped = (
                    candidate[:swap] + candidate[swap + 1]
                    + candidate[swap] + candidate[swap + 2:])
                differences = sum(
                    1 for left, right in zip(swapped, word)
                    if left != right)
                if differences == 2:
                    return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differences = sum(
                1 for left, right in zip(candidate, word)
                if left != right)
            if differences == 4:
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if len(differing) != 5:
                continue
            paired = any(
                word[left] == candidate[right]
                and word[right] == candidate[left]
                for left, right in itertools.combinations(differing, 2))
            if not paired:
                return candidate
    for candidate in _ACTOR_VOCABULARY_ORDERED:
        if _mixed_added_resolves(word, candidate):
            return candidate
        if _anywhere_transposition_resolves(word, candidate):
            return candidate
    return word


def _canonicalise_actor_word(word):
    """Read one actor word through the leet reading: a digit
    standing among letters reads as the letter it stands
    for, under the recorded leet digit readings."""
    if any(char.isalpha() for char in word) and any(
            char.isdigit() for char in word):
        word = "".join(
            _LEET_DIGITS.get(char, char) for char in word)
    return word


def _normalised_actor(actor):
    """Normalise an actor reading before the person check, to
    the same form the MOD-14 shell applies: case is folded,
    the text stands canonicalised, separator characters stand
    read as spacing for the word reading, repeated leading
    articles are dropped, and each word stands read through
    the leet reading and the word resolver against the actor
    vocabulary. The split parts of one actor word also stand
    read joined, so a separator split dress of one word reads
    as the word it names and is not split into a different
    actor. The joined reading also stands tried with article
    words dropped wherever they stand, so articles inserted
    between the split parts of one actor word do not hide the
    word they split."""
    if not isinstance(actor, str):
        return actor
    text = _canonical_text(actor, _TRANSLITERATION_MAP)
    text = "".join(
        char if char.isalnum() else " " for char in text)
    words = [_canonicalise_actor_word(word) for word in text.split()]
    while words and words[0] in _ACTOR_ARTICLES:
        words = words[1:]
    if not words:
        return ""
    joined = _resolve_actor_word("".join(words))
    if joined in _ACTOR_VOCABULARY:
        return joined
    without_articles = _resolve_actor_word("".join(
        word for word in words if word not in _ACTOR_ARTICLES))
    if without_articles in _ACTOR_VOCABULARY:
        return without_articles
    return " ".join(_resolve_actor_word(word) for word in words)


_ZERO_WIDTH_CHARS = frozenset((
    "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff",
    "\u00ad", "\u180e", "\u200e", "\u200f", "\u061c",
    "\u202a", "\u202e", "\u2061", "\u2064",
))

_BLANK_GLYPHS = frozenset(("\u2800", "\u115f"))

_HANGUL_FILLER_CHARS = frozenset(("\u1160", "\u3164", "\uffa0"))


def _has_stated_condition(fired):
    """Whether a fired condition list states at least one
    condition: an entry states a condition where it stands as a
    string carrying text, or as a stated value other than None.
    A list holding only an empty string or only None states no
    condition. An entry carrying only zero width, byte order
    mark, or invisible format characters, beside any spacing,
    reads as blank text and states no condition, because those
    characters carry no readable text. The invisible format
    characters stand in the stated set beside the zero width
    set: the soft hyphen, the Mongolian vowel separator, the
    left to right and right to left marks, the Arabic letter
    mark, the left to right and right to left embeddings, and
    the invisible operator and invisible plus characters. A
    combining mark standing alone, with no base character it
    modifies, and a blank glyph carry no readable text in the
    same manner, so an entry holding only characters of those
    kinds states no condition either."""
    if isinstance(fired, str):
        entries = [fired]
    elif isinstance(fired, (list, tuple, set, frozenset)):
        entries = list(_base_iter(fired))
    elif fired is None:
        entries = []
    else:
        entries = [fired]
    for entry in entries:
        if isinstance(entry, str):
            readable = "".join(
                char for char in entry
                if char not in _ZERO_WIDTH_CHARS
                and char not in _BLANK_GLYPHS
                and char not in _HANGUL_FILLER_CHARS
                and unicodedata.category(char)
                not in ("Cf", "Mn", "Cc", "Mc", "Me"))
            if readable.strip():
                return True
        elif entry is not None:
            return True
    return False


def apply_flag_evaluation(record, outcome=None, tier=None, actor="program", inputs=None):
    if not isinstance(record, dict):
        raise ValueError(
            "flag evaluation in named form: the evaluation stands on a "
            "summary record, and no other form stands evaluated")
    _guard_retention_shape(record)
    actor = _normalised_actor(actor)
    if actor == "person":
        raise ValueError("promotion by a person after close is barred")
    if outcome is not None and outcome not in _FLAG_OUTCOMES:
        raise ValueError(
            "flag evaluation outcome outside the stated vocabulary: "
            + str(outcome))
    if outcome == "demote":
        raise ValueError("the flag rule never demotes")
    if tier is not None and tier not in _TIER_RANKS:
        raise ValueError(
            "flag evaluation tier outside the tiers the rule names: "
            + str(tier))
    current = record.get("retention_tier")
    if (tier is not None and current in _TIER_RANKS
            and _TIER_RANKS[tier] < _TIER_RANKS[current]):
        raise ValueError(
            "the flag rule never demotes: the stated tier stands below "
            "the record tier")
    if outcome == "promote":
        if inputs is None:
            raise ValueError(
                "flag promotion with no inputs supplied: a promotion "
                "stands only with inputs actually supplied, and no "
                "promotion stands effected by it")
        fired = []
        if isinstance(inputs, dict):
            fired = inputs.get("flag_conditions_fired") or []
        if not fired:
            fired = record.get("flag_conditions_fired") or []
        if not _has_stated_condition(fired):
            raise ValueError(
                "flag promotion with no stated flag condition fired: "
                "a promotion stands only with at least one stated "
                "flag condition fired, and no promotion stands "
                "effected by it")
        if tier is None:
            raise ValueError(
                "a promote outcome with no tier stands refused: no "
                "promotion stands effected by it")
        if current in _TIER_RANKS and _TIER_RANKS[tier] <= _TIER_RANKS[current]:
            raise ValueError(
                "a promote outcome with no effected promotion stands "
                "refused")
    updated = _safe_copy(record)
    if outcome == "promote" and tier is not None:
        updated["retention_tier"] = tier
    updated["flag_evaluation"] = {
        "inputs": inputs,
        "outcome": outcome,
        "tier": tier,
        "actor": actor,
        "written_into": "summary record",
    }
    run_key = updated.get("run_id") or updated.get("run_identifier")
    if run_key is not None:
        write_summary_record(updated)
    return updated


def place_reserve_hold(run_id, family_states_headlines=True, start_day=0):
    """Place the full reserve hold on a run at close: the full
    event log, the daily snapshots, and the final checkpoint stand
    held until the release trigger at the later firing. A family
    that never states headline results carries no stated end to
    the hold under this rule."""
    hold = {
        "run_id": run_id,
        "held_forms": ["event_log", "daily_snapshots", "final_checkpoint"],
        "state": "held",
        "release_trigger": "later firing where the trigger terminates",
        "family_states_headlines": bool(family_states_headlines),
        "start_day": start_day,
        "maximum_duration_days": 30,
        "end_day": start_day + 30,
        "stated_end": True,
        "cut_short_by_cost_warden": False,
    }
    _RESERVE_HOLDS[run_id] = hold
    return copy.deepcopy(hold)


def reserve_hold_for_run(run_id, current_day=None):
    """Read the reserve hold standing on a run. A hold read at or
    past its ruled maximum end of 30 days under ruling Entries 17
    and 18 stands expired by that stated act, for every family
    form including a family that never states headline results,
    and never reads held without an end."""
    hold = _RESERVE_HOLDS.get(run_id)
    if hold is None:
        return None
    if current_day is not None and hold.get("state") == "held" and current_day >= hold.get("end_day", 0):
        hold["state"] = "expired"
    if hold.get("state") == "released":
        return None
    return copy.deepcopy(hold)


def apply_deferred_evaluation(summary_record, firing, inputs=None,
                              outcome=None, family_states_headlines=True):
    """Write one deferred evaluation into the summary record
    itself: its firing, its inputs, and its outcome. Each run
    receives two firings. For a family that never states headline
    results, the second firing does not fire. Where the release
    trigger terminates at the later firing, the reserve hold on
    the run stands released by the same act."""
    if not isinstance(summary_record, dict):
        raise ValueError("no evaluation stands written in named form: no summary record stands for the run, and no detached evaluation stands returned")
    if firing not in (1, 2):
        raise ValueError("a run receives two firings and no third")
    updated = copy.deepcopy(summary_record)
    evaluations = updated.setdefault("deferred_evaluations", [])
    if any(item.get("firing") == firing for item in evaluations):
        raise ValueError("this firing already stands written")
    if firing == 2 and not family_states_headlines:
        updated["second_firing"] = "does not fire"
        return updated
    if inputs is None or outcome is None:
        raise ValueError(
            "deferred evaluation refused in named form: a firing with "
            "no inputs or no outcome stands not written, and no hold "
            "stands released by it")
    if firing == 2:
        run_key = updated.get("run_id") or updated.get("run_identifier")
        stored = _SUMMARY_RECORDS.get(run_key) or {}
        stored_evaluations = stored.get("deferred_evaluations") or []
        first_standing = (
            any(item.get("firing") == 1 for item in evaluations)
            or any(item.get("firing") == 1 for item in stored_evaluations))
        if not first_standing:
            raise ValueError(
                "deferred evaluation refused in named form: the second "
                "firing stands with no first firing on the record, and "
                "no hold stands released by it")
        if not evaluations and stored_evaluations:
            evaluations.extend(copy.deepcopy(stored_evaluations))
    evaluations.append({
        "firing": firing,
        "inputs": inputs,
        "outcome": outcome,
        "conditions": [1, 2] if firing == 1 else [1, 2, 3],
        "written_into": "summary record",
    })
    if firing == 2:
        hold = _RESERVE_HOLDS.get(
            updated.get("run_id") or updated.get("run_identifier"))
        if hold is not None and hold.get("family_states_headlines", True):
            hold["state"] = "released"
            updated["reserve_hold_state"] = "released"
    run_key = updated.get("run_id") or updated.get("run_identifier")
    if run_key is not None:
        write_summary_record(updated)
    return updated


def retention_record_for_run(run_id, store_kind="sweep"):
    """Return the retention record of a run in pointer form: the
    later evaluation as written into the summary record, and the
    forms retained for the run that this record points to."""
    summary = summary_record_for_run(run_id)
    evaluations = summary.get("deferred_evaluations") or []
    later = evaluations[-1] if evaluations else None
    tier = summary.get("retention_tier")
    tier_forms = {
        "Tier 1": ["final_checkpoint"],
        "Tier 2": ["final_checkpoint", "tenth_point_checkpoints"],
        "Tier 3": ["final_checkpoint", "daily_checkpoints"],
    }.get(tier, [])
    pointer_counts = {
        "checkpoints": len(checkpoints_for_run(run_id, store_kind)),
        "event_log_entries": len(event_log_entries(run_id, store_kind)),
        "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
    }
    retained_forms = []
    if pointer_counts["checkpoints"]:
        retained_forms.append("final_checkpoint")
    if pointer_counts["event_log_entries"]:
        retained_forms.append("event_log")
    if pointer_counts["daily_snapshots"]:
        retained_forms.append("daily_snapshots")
    not_retained = [
        form + ": not retained"
        for form in tier_forms if form not in retained_forms
    ]
    result = {
        "run_id": run_id,
        "retention_tier": tier,
        "tier_forms": list(tier_forms),
        "retained_forms": retained_forms,
        "not_retained": not_retained,
        "shortfall": {
            "count": len(not_retained),
            "bound": "shortfall stands stated inside this result as a bound: "
            + str(len(not_retained)) + " of " + str(len(tier_forms))
            + " forms the tier names stand not retained",
        },
        "later_evaluation": copy.deepcopy(later),
        "pointers": {
            "checkpoints": len(checkpoints_for_run(run_id, store_kind)),
            "event_log_entries": len(event_log_entries(run_id, store_kind)),
            "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
        },
        "pointer_form": "retention record points to the retained forms",
    }
    result["summary_record_written"] = run_id in _SUMMARY_RECORDS
    result["retained_forms_pointed_to"] = [
        name for name, count in pointer_counts.items() if count
    ]
    result["form_standing"] = {
        name: (
            "held in memory only: a count of zero states that no form "
            "stands in memory for the run, and does not state that no "
            "form ever stood")
        for name in pointer_counts
    }
    if (run_id not in _SUMMARY_RECORDS
            and not any(pointer_counts.values())
            and not _DEFAULT_STORE.has_run_record(run_id)):
        result["form"] = FORM_ONLY
    return result


def validate_retention_report(report):
    if report.get("source") == "interval_records" and report.get("tier_claim") == "final":
        return False
    return True


def append_annotation(checkpoint, annotation=None):
    updated = copy.deepcopy(checkpoint)
    updated["annotation_record"] = copy.deepcopy(annotation) if annotation is not None else {}
    return updated


def annotation_link_at_checkpoint(checkpoint):
    """Return the annotation link identifier at a checkpoint, under
    the plan named field annotation_link_identifier where it
    stands, and under the Form 4 carriage name annotation_link
    where that is the name the checkpoint carries."""
    return (
        checkpoint.get("annotation_link_identifier")
        or checkpoint.get("annotation_link"))


def resume_from_checkpoint(checkpoint, store_kind=None):
    """Resume from a checkpoint. Where a retained checkpoint stands
    for the run and day the handed checkpoint names, the handed
    checkpoint stands checked against the retained bucket of its
    own store kind: where a store kind stands named, by the call
    or on the checkpoint itself, that bucket alone stands
    compared; where none stands named, the handed checkpoint
    stands checked against every retained bucket for its run and
    day and stands resumed where it matches the retained
    checkpoint of any one of them. A checkpoint differing from
    every retained checkpoint for its run and day stands refused
    in named form, and no resume stands performed from it. Where
    a store kind stands named and that kind holds no retained
    bucket for the run and day, the handed checkpoint stands
    refused in the same checkpoint integrity refusal form
    instead of standing returned unchecked. The checkpoint day
    stands read through the one stated whole day form at the
    final comparison, as the candidate selection already reads
    it, so a day stated in string whole day form beside the
    same day stated as an integer names the one day. A handed
    store kind stands judged through the canonical kind, by its
    stored text, at the kind test and at the bucket filter, and
    never through a reading the handed kind supplies."""
    if not isinstance(checkpoint, dict):
        raise ValueError(
            "identity less checkpoint: a resume stands on a checkpoint "
            "record, and no other form stands resumed")
    run_id = checkpoint.get("run_identifier") or checkpoint.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "checkpoint, and no resume stands performed")
    kind = store_kind or checkpoint.get("store_kind")
    if kind is not None:
        kind = _canonical_store_kind(kind)
    handed_form = {
        key: value for key, value in checkpoint.items()
        if key not in ("journal_event_count_at_checkpoint", "store_kind")
    }
    candidates = []
    for (bucket_kind, bucket_run), bucket in _CHECKPOINTS.items():
        if bucket_run != run_id:
            continue
        if kind is not None and bucket_kind != kind:
            continue
        for retained in bucket:
            if _whole_day(retained.get("simulated_day")) == _whole_day(
                    checkpoint.get("simulated_day")):
                candidates.append(retained)
    if not candidates:
        if kind is not None:
            raise ValueError(
                "checkpoint integrity refusal: the handed "
                "checkpoint names a store kind holding no "
                "retained checkpoint for its run and day, and "
                "no resume stands performed from it")
        return copy.deepcopy(checkpoint)

    def _comparison_form(form):
        compared = dict(form)
        if "simulated_day" in compared:
            compared["simulated_day"] = _whole_day(
                compared["simulated_day"])
        return compared

    handed_compared = _comparison_form(handed_form)
    for retained in candidates:
        retained_form = {
            key: value for key, value in retained.items()
            if key not in ("journal_event_count_at_checkpoint", "store_kind")
        }
        if _comparison_form(retained_form) == handed_compared:
            return copy.deepcopy(checkpoint)
    raise ValueError(
        "checkpoint integrity refusal: the handed "
        "checkpoint differs from the retained checkpoint "
        "for its run and day, and no resume stands "
        "performed from it")


def validate_annotation_claim(claim):
    if claim.get("claim") == "annotation_state_equal_across_append":
        return False
    return True


def retention_sizing(fixture="F-27", costing_forms="F-19"):
    """Return the retention sizing record. Its workings stand in
    the stated costing forms of the fixtures it names, each with
    its provenance label, and the record carries its standing as
    form only carriage inside the value: no present sizing claim
    and no present cost claim stands made by this record."""
    return {
        "fixture": fixture,
        "costing_forms": costing_forms,
        "basis": "DQ7-03 decided subparts",
        "carriage": "form only, no present sizing claim",
        "workings": {
            "central_form": {
                "events_per_agent_per_day": 6.85,
                "provenance": "derived over estimated form values, central form as spacing choice",
            },
            "high_form": {
                "events_per_agent_per_day": 25.71,
                "provenance": "derived over estimated form values, high form as working form",
            },
        },
    }


def validate_retention_sizing(sizing):
    workings = sizing.get("workings") or {}
    if "central_form" not in workings or "high_form" not in workings:
        return False
    high = workings.get("high_form") or {}
    if high.get("events_per_agent_per_day") is None:
        return False
    wording = sizing.get("wording") or {}
    for value in wording.values():
        if value in ("forecast", "ceiling"):
            return False
    return True


def retention_met(record):
    if record.get("declaration_only") or record.get("state") == "DECLARED NOT CLOSED":
        return False
    later = record.get("later_evaluation")
    if not later:
        return False
    if list(later.get("conditions") or []) != [1, 2, 3]:
        return False
    if not later.get("inputs") or not later.get("outcome"):
        return False
    if not record.get("summary_record_written"):
        return False
    if not record.get("retained_forms_pointed_to"):
        return False
    return True


def pre_registered_full_log_sample(family_id="family-under-test"):
    return {
        "kind": "retention_sample",
        "run_class": "ordinary_screening",
        "family_id": family_id,
        "in_family_record": True,
        "registration_standing": "before_runs",
    }


def validate_sample_record(sample):
    if sample.get("presented_as") == "generator_test_battery_sample":
        return False
    if sample.get("kind") == "retention_sample":
        if not sample.get("in_family_record"):
            return False
        if sample.get("registration_standing") != "before_runs":
            return False
    return True


def validate_retention_record(record):
    governing = str(record.get("governing_rule") or "")
    if governing.startswith("DQ7-08") and record.get("reliance") == "governing":
        return False
    return True


def store_indexes():
    return {kind: _STORES[kind].index() for kind in STORE_KINDS}


def validate_store_placement(artefact):
    if artefact.get("kind") == "pilot":
        if artefact.get("store") != "pilot":
            return False
        if "value" in artefact and not artefact.get("confinement_label"):
            return False
    return True


def store_lookup(store_kinds=None, key=None, store_kind=None):
    kinds = store_kinds
    if isinstance(kinds, str):
        kinds = (kinds,)
    if kinds is None and store_kind is not None:
        kinds = (store_kind,)
    if kinds is None:
        kinds = ()
    if len(tuple(kinds)) != 1:
        raise ValueError("a lookup that resolves across stores in one step is rejected")
    kind = tuple(kinds)[0]
    if not _store_kind_stands(kind):
        raise ValueError(
            "unknown store kind: " + str(kind) + "; a store kind stands "
            "among sweep, pilot, and live, and no record lookup stands "
            "performed on an unknown kind")
    return _STORES[_canonical_store_kind(kind)].read_run_record(key)


__all__ = [
    "STORE_KINDS",
    "SEVEN_GROUPS",
    "GROUP_OWNERS",
    "ONE_LOOKUP_FAILURE_NAME",
    "FORM_ONLY",
    "LookupFailure",
    "RecorderStore",
    "new_store",
    "fresh_stores",
    "reset_stores",
    "retain_run_record",
    "read_run_record",
    "run_records_for_run",
    "validate_run_record_set",
    "retain_daily_aggregate_deliveries",
    "daily_aggregates_for_run",
    "rederive_regime_classification",
    "validate_daily_aggregates",
    "build_joint_outcome_vector",
    "record_gate_passing_share",
    "gate_passing_shares_for_run",
    "event_log_fields",
    "daily_snapshot_fields",
    "retain_event_log_entry",
    "event_log_entries",
    "retain_daily_snapshot",
    "daily_snapshots",
    "retain_checkpoint",
    "checkpoints_for_run",
    "rejected_checkpoint_writes",
    "delete_checkpoint",
    "checkpoint_integrity_check",
    "portable_checkpoint_manifest",
    "restore_check",
    "replay_check",
    "retain_gc08_record",
    "gc08_record",
    "storage_accounting",
    "validate_storage_accounting",
    "checkpoint_count_c10",
    "cumulative_storage_projection",
    "retention_policy_table",
    "validate_storage_claim",
    "write_summary_record",
    "summary_record_for_run",
    "apply_flag_evaluation",
    "place_reserve_hold",
    "reserve_hold_for_run",
    "apply_deferred_evaluation",
    "retention_record_for_run",
    "validate_retention_report",
    "append_annotation",
    "annotation_link_at_checkpoint",
    "resume_from_checkpoint",
    "validate_annotation_claim",
    "retention_sizing",
    "validate_retention_sizing",
    "retention_met",
    "pre_registered_full_log_sample",
    "validate_sample_record",
    "validate_retention_record",
    "store_indexes",
    "validate_store_placement",
    "store_lookup",
]


# ---------------------------------------------------------------------------
# View edge and rule version carriage edges (slices S-11 and S-12)
# ---------------------------------------------------------------------------

def validate_view_carriage(carriage):
    """The Recorder view edge validation for carried view forms.

    A carriage presenting the outcome vector as one singular
    comparable quantity fails, and a flip trial record cited as a
    run result fails. Per viewer carriages in their decided form
    stand."""
    if not isinstance(carriage, dict):
        return False
    if carriage.get("form") == "singular_vector":
        return False
    if carriage.get("presented_as") == "one comparable quantity":
        return False
    if carriage.get("form") == "flip_trial_record" and carriage.get("cited_as") == "run_result":
        return False
    return True


def _retained_records():
    for store in _STORES.values():
        for record in store._records.values():
            yield record
    for record in _SUMMARY_RECORDS.values():
        yield record


def retained_version_set(record_id="record-under-test"):
    """The exact rule version set a retained record carries, as
    retained by this Recorder: the set stands returned unedited,
    in the form the record was produced under. Where no record
    stands retained under the identifier, the returned value
    carries the form only marker inside it, and no version set
    stands stated for a record that does not exist."""
    for record in _retained_records():
        rid = record.get("run_id") or record.get("run_identifier")
        if rid != record_id:
            continue
        for field in ("rule_version_set", "record_version_set",
                      "version_set"):
            if record.get(field) is not None:
                return copy.deepcopy(record[field])
    return {"record_id": record_id, "form": FORM_ONLY}


def rerun_list_for_rule_change(family_id="family-under-test"):
    """The rerun list derived from a rule change for one family,
    held as a retained record naming the records the change puts
    in question. The list stands derived from the records retained
    for the family. Where no record stands retained for the
    family, the returned value carries the form only marker inside
    it and names no record in question."""
    in_question = []
    for record in _retained_records():
        family = (record.get("family_id")
                  or record.get("family_identifier"))
        if family != family_id:
            continue
        rid = record.get("run_id") or record.get("run_identifier")
        if rid is not None and rid not in in_question:
            in_question.append(rid)
    if not in_question:
        return {
            "family_id": family_id,
            "records_in_question": [],
            "form": FORM_ONLY,
        }
    return {
        "family_id": family_id,
        "records_in_question": in_question,
        "form": "retained rerun list",
    }


# ---------------------------------------------------------------------------
# View record leak check and retention (slice S-11, Recorder limb)
# ---------------------------------------------------------------------------

_VIEW_LEAK_FORMS = ("canary", "field_validation", "timing")

# The one barred vocabulary, as the cured MOD-04 checker and the
# cured MOD-03 helper stand on it: the thirteen projection names,
# beside the ground truth names MOD-03 has always barred, read
# lowered, with lowered substring matching on the membership,
# ground truth, groundtruth, and canary parts, so capitalised and
# variant forms stand barred as well. The plain word label stands
# barred as an exact name only, never as a substring, so
# legitimate sibling content such as labelled assumptions stands.
_VIEW_BARRED_KEYS = frozenset((
    "ground_truth", "ground_truth_field", "membership",
    "honest_membership", "farm_membership", "is_honest", "is_farm",
    "canary", "canary_value", "membership_value", "sleeper",
    "ground_truth_label", "label",
    "honest_or_farm_membership", "membership_ground_truth",
))

_VIEW_BARRED_KEY_PARTS = (
    "membership",
    "ground_truth",
    "groundtruth",
    "canary",
)


_VIEW_BARRED_KEYS_FOLDED = frozenset((
    "groundtruth", "groundtruthfield", "membership",
    "honestmembership", "farmmembership", "ishonest", "isfarm",
    "canary", "canaryvalue", "membershipvalue", "sleeper",
    "groundtruthlabel", "label",
    "honestorfarmmembership", "membershipgroundtruth",
))

_VIEW_BARRED_KEY_PARTS_FOLDED = (
    "membership",
    "groundtruth",
    "canary",
)


def _view_segments_by_character(key):
    """The folded segments one key can contribute at the view
    surface, character by character, with no enumeration of
    their combinations. Each character contributes the segments
    its readings fold to under _add_fold_forms: the readings
    the two letter maps and the ambiguous reading table record
    for it, as the expanded texts of _expanded_texts state
    them, so a name needing one reading at one position and
    the other reading at another stands read in full however
    many ambiguous positions it carries."""
    segments_by_character = []
    for character in str(key).casefold():
        readings = set()
        if character in _AMBIGUOUS_READINGS:
            readings.update(_AMBIGUOUS_READINGS[character])
        for letter_map in (_TRANSLITERATION_MAP, _HOMOGLYPH_MAP):
            readings.add(_canonical_text(character, letter_map))
        segments = set()
        for reading in readings:
            _add_fold_forms(segments, reading)
        segments_by_character.append(segments)
    return segments_by_character


def _combined_view_key_barred(key):
    """Whether any combined reading of the key stands barred
    at the view surface, judged position by position over the
    per character segments without enumerating the combined
    texts, so the judgement stands the same inside the 4096
    enumeration bound and past it, in the form the MOD-05 read
    takes and the money read of this module already takes. The
    forms judged are the forms _is_barred_view_key judges on
    an enumerated variant: a variant standing in the folded
    barred key set, and a variant carrying a folded barred
    part."""
    segments_by_character = _view_segments_by_character(key)
    for target in _VIEW_BARRED_KEYS_FOLDED:
        if _money_segments_match(segments_by_character, target):
            return True
    for part in _VIEW_BARRED_KEY_PARTS_FOLDED:
        if _money_segments_carry(segments_by_character, part):
            return True
    return False


def _is_barred_view_key(key):
    """Return whether a key stands barred under the one barred
    vocabulary. The key stands read through the canonicalised
    fold stated at the money reading above, in the same form the
    cured surfaces are charged to share, so a key split inside
    its marker word, or dressed in a letter or digit dress the
    fold covers, reads as its marker. The plain word label stands
    barred as an exact folded name only, never as a part, as on
    the standing surfaces."""
    for variant in _fold_variants(key):
        if variant in _VIEW_BARRED_KEYS_FOLDED:
            return True
        if any(part in variant for part in _VIEW_BARRED_KEY_PARTS_FOLDED):
            return True
    return _combined_view_key_barred(key)


def _carries_barred_key(value):
    """Return whether a value carries a barred key at any depth.

    The read is iterative, through dicts, lists, tuples, sets, and
    frozensets, with a visited set, so content nested at any depth
    stands read and cyclic content cannot loop the read. Keys
    stand read; values standing as plain text stand unread, as on
    the cured surfaces."""
    stack = [value]
    visited = set()
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if id(node) in visited:
                continue
            visited.add(id(node))
            for key, item in dict.items(node):
                if _is_barred_view_key(key):
                    return True
                stack.append(item)
        elif isinstance(node, (list, tuple, set, frozenset)):
            if id(node) in visited:
                continue
            visited.add(id(node))
            stack.extend(_base_iter(node))
    return False


def run_view_leak_check(view_record):
    """Run the three form leak check on a ViewRecord: the canary
    form, the field validation form, and the timing form, together
    on the one record. The canary form reads every group of the
    record, the graph position group beside the content and
    reputation and band groups, under the one barred vocabulary
    the cured MOD-04 checker and the cured MOD-03 helper stand on,
    at any depth, so the gate this runner governs is the checker
    it was charged to follow. A failure in any one form raises a
    failure naming the view, the field, and the check form that
    failed, and the run stands not reportable on that record. A
    record passing all three forms returns the run record of the
    check."""
    if not isinstance(view_record, dict):
        raise ValueError(
            "view leak check failure: form field_validation, the "
            "record stands as no ViewRecord")
    view_name = (
        str(view_record.get("run_identifier")
            or view_record.get("run_id"))
        + "/" + str(view_record.get("viewer_identifier")
                    or view_record.get("viewer_id")))
    groups = [
        name for name in (
            "view_contents", "reputation_and_band_values",
            "graph_position_as_seen")
        if name in view_record
    ]
    groups.extend(
        name for name in view_record if name not in groups)
    for field in groups:
        if _is_barred_view_key(field) or _carries_barred_key(
                view_record.get(field)):
            raise ValueError(
                "view leak check failure: form canary, view "
                + view_name + ", field " + field
                + " carries a barred key")
    for field in mod01.ViewRecord.FIELDS:
        if field in ("scheduling_position_identifier",
                     "rule_version_set") and field in view_record:
            continue
        if view_record.get(field) is None:
            raise ValueError(
                "view leak check failure: form field_validation, view "
                + view_name + ", field " + field + " stands absent")
    day = _timing_day(view_record.get("simulated_day"))
    first_seen = view_record.get("first_seen_day_per_record") or {}
    for item, seen_day in first_seen.items():
        seen_day = _timing_day(seen_day)
        if (isinstance(seen_day, (int, float))
                and not isinstance(seen_day, bool)
                and isinstance(day, (int, float))
                and not isinstance(day, bool)
                and not (math.isfinite(seen_day)
                         and math.isfinite(day))):
            raise ValueError(
                "view leak check failure: form timing, view "
                + view_name + ", field first_seen_day_per_record: "
                "record " + str(item) + " states a day in a non "
                "finite form the timing comparison cannot order")
        if (isinstance(seen_day, (int, float))
                and not isinstance(seen_day, bool)
                and isinstance(day, (int, float))
                and not isinstance(day, bool)
                and seen_day > day):
            raise ValueError(
                "view leak check failure: form timing, view "
                + view_name + ", field first_seen_day_per_record: "
                "record " + str(item) + " first seen after the view day")
    return {
        "forms_run": list(_VIEW_LEAK_FORMS),
        "reportable": True,
        "view": view_name,
    }


def retain_view_record(record, tier=None):
    """Retain one ViewRecord under the leak check runner: the
    record stands retained only where the runner passes it. The
    retention split stands by tier: at Tier 1 the divergence
    companion stands retained in place of the full record, and at
    Tier 2 and Tier 3 the full record stands retained."""
    if not isinstance(record, dict):
        raise ValueError(
            "identity less view record: a ViewRecord stands as a "
            "record carrying a run identifier, and no other form "
            "stands retained")
    run_id = record.get("run_identifier") or record.get("run_id")
    if run_id is None:
        raise ValueError(
            "identity less view record: no run identifier stands on "
            "the record, and no view record stands retained under "
            "no identifier")
    run_view_leak_check(record)
    tier = tier or record.get("retention_tier") or "Tier 2"
    if tier == "Tier 1":
        stored = {
            "run_identifier": run_id,
            "viewer_identifier": (
                record.get("viewer_identifier")
                or record.get("viewer_id")),
            "simulated_day": record.get("simulated_day"),
            "retention_tier": "Tier 1",
            "divergence_companion": _safe_copy(
                record.get("divergence_companion")
                or {"nil_divergence_components": []}),
            "form": "divergence companion in place of the full view record",
        }
    else:
        stored = _safe_copy(record)
        stored["retention_tier"] = tier
    _VIEW_RECORDS.setdefault(run_id, []).append(stored)
    return copy.deepcopy(stored)


def view_records_for_run(run_id):
    """Read the retained ViewRecords of a run. Reading never
    writes."""
    return _safe_copy(_VIEW_RECORDS.get(run_id, []))

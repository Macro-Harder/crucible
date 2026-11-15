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
from fractions import Fraction

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


def _vocabulary_text(value):
    """Render a handed value for a vocabulary sentence: a text
    form or a buffer form stands rendered by the text it stores,
    read through _stored_text, so a memoryview form names the
    value it stores and never a volatile memory address. Any
    other form stands rendered through _safe_str."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    return _safe_str(value)

FORM_ONLY = "form_only"


class LookupFailure(KeyError):
    """A named failure for a record that does not resolve in one
    lookup. The failure value stands on the exception in the form
    MOD-01 states for a named failure."""

    def __init__(self, run_id, record_kind=None):
        self.run_id = run_id
        self.record_kind = record_kind
        self.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        if record_kind is not None:
            self.failure["record_kind"] = record_kind
        text = ONE_LOOKUP_FAILURE_NAME + ": " + _safe_str(run_id)
        if record_kind is not None:
            text = (
                ONE_LOOKUP_FAILURE_NAME + ": " + _safe_str(run_id)
                + " for record kind " + _safe_str(record_kind))
        super().__init__(text)


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
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "e", "\u03b8": "th",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03bf": "o", "\u03c0": "p", "\u03c1": "r",
    "\u03c2": "s", "\u03c3": "s", "\u03c4": "t", "\u03c5": "u",
    "\u03c6": "ph", "\u03c7": "h", "\u03c8": "ps", "\u03c9": "o",
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
# Cyrillic i with its combining mark dropped, and Greek theta
# as t beside its governing reading th and Greek phi as f
# beside its governing reading ph. The folded
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
    "\u03c6": ("f", "ph"),
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
    itself supplies. A value that is not a text form stores
    no text, so no name stands judged from a string reading
    a non text value itself supplies, and its stored text
    stands as the empty text. A bytes, bytearray, or
    memoryview value stands judged on its stored bytes,
    decoded as UTF-8 with undecodable bytes dropped, never
    through a string reading a bytes subclass itself
    supplies, so a bytes form keeps the standing its stored
    name carries, in the form the cured sister helpers at
    MOD-03, MOD-05, MOD-06, and MOD-08 state and the
    condition limb of this module already states."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


_CONTAINER_KEY_FORMS = (tuple, list, set, frozenset)


def _container_parts(key):
    """The parts a container key stores, read through the
    base iteration of its own form, never through an
    iteration reading the container itself supplies."""
    if isinstance(key, list):
        return list(list.__iter__(key))
    if isinstance(key, tuple):
        return list(tuple.__iter__(key))
    if isinstance(key, frozenset):
        return list(frozenset.__iter__(key))
    return list(set.__iter__(key))


def _joined_stored_text(key):
    """The stored text parts of a container key joined in
    order, with no separator added, each part read on its
    own stored text at any depth. A bare value reads as its
    own stored text. The walk is iterative and keeps a
    visited set, so a shared or cyclic part cannot loop it."""
    pieces = []
    stack = [key]
    seen = set()
    while stack:
        node = stack.pop()
        if isinstance(node, _CONTAINER_KEY_FORMS):
            if id(node) in seen:
                continue
            seen.add(id(node))
            stack.extend(reversed(_container_parts(node)))
        elif isinstance(node, dict):
            if id(node) in seen:
                continue
            seen.add(id(node))
            stack.extend(reversed(list(dict.keys(node))))
        else:
            pieces.append(_stored_text(node))
    return "".join(pieces)



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
    return _container_parts(node)


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
            readings = set(_fold_variants(node))
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
        return set(_fold_variants(node))
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
            readings.update(_fold_variants(text))
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
    under the view barred judgement, judged by segmentation
    beside the kept candidate readings. The plain exact names
    and plain barred parts of the scalar judgement stand
    tiled over the lowered joined texts of the parts, and the
    folded exact names and folded barred parts stand tiled
    over the folded readings of the parts, in the form
    settlement S-4 states for both reading spaces."""
    for node, parts in _seg_unordered_nodes(key):
        plain_universe = _seg_universe(
            _VIEW_BARRED_KEYS, _VIEW_BARRED_KEY_PARTS)
        plain = _seg_plain_options(
            parts, plain_universe, _seg_prefixes(plain_universe))
        for target in tuple(_VIEW_BARRED_KEYS):
            if _seg_tiles_exact(plain, target):
                return True
        for pattern in tuple(_VIEW_BARRED_KEY_PARTS):
            if _seg_tiles_carrying(plain, pattern) is not None:
                return True
        for pattern in tuple(_VIEW_BARRED_KEY_PARTS):
            if _seg_parts_carry_edge(parts, plain, pattern, False):
                return True
        folded_universe = _seg_universe(
            _VIEW_BARRED_KEYS_FOLDED, _VIEW_BARRED_KEY_PARTS_FOLDED)
        folded = _seg_folded_options(
            parts, folded_universe, _seg_prefixes(folded_universe))
        for target in tuple(_VIEW_BARRED_KEYS_FOLDED):
            if _seg_tiles_exact(folded, target):
                return True
        for pattern in tuple(_VIEW_BARRED_KEY_PARTS_FOLDED):
            if _seg_tiles_carrying(folded, pattern) is not None:
                return True
        for pattern in tuple(_VIEW_BARRED_KEY_PARTS_FOLDED):
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


def _seg_carrying(key, pattern):
    """Whether an unordered container standing inside a key
    joins, in some order of its direct parts, to a reading
    carrying the pattern, judged by segmentation of the
    pattern over the folded readings of the parts, beside the
    kept candidate readings."""
    for node, parts in _seg_unordered_nodes(key):
        universe = _seg_universe((), (pattern,))
        if _seg_tiles_carrying(
                _seg_folded_options(
                    parts, universe, _seg_prefixes(universe)),
                pattern) is not None:
            return True
    return False



def _plain_number(value):
    """Return a plain number holding the value a handed number
    stores, built through base class operations, or None where
    the value stands in no number form this module reads."""
    if isinstance(value, bool):
        return int.__new__(int, int.__int__(value))
    if isinstance(value, int):
        return int.__new__(int, int.__int__(value))
    if isinstance(value, float):
        return float.__new__(float, float.__float__(value))
    if isinstance(value, Decimal):
        return Decimal.__new__(Decimal, value)
    if isinstance(value, Fraction):
        return Fraction.__new__(Fraction, value)
    if isinstance(value, complex):
        return complex.__new__(complex, value)
    return None


def _stored_form(value):
    """The stored form of one value, as one sortable text built
    from base readings only: a type tag for the form the value
    stands in, beside the value it stores read through its base
    class form. Two values take one stored form only where the
    forms they stand in and the values they store agree, so a
    stored form keeps distinct stored values distinct, and a
    text value stands in it by its stored characters, never by
    a reading the value itself supplies."""
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "bool:" + str(int.__int__(value))
    if isinstance(value, int):
        return "int:" + str(int.__int__(value))
    if isinstance(value, float):
        return "float:" + repr(float.__float__(value))
    if isinstance(value, str):
        text = str.__str__(value)
        return "str:" + str(len(text)) + ":" + text
    if isinstance(value, bytes):
        return "bytes:" + bytes(value).hex()
    if isinstance(value, bytearray):
        return "bytearray:" + bytes(value).hex()
    if isinstance(value, memoryview):
        return "memoryview:" + bytes(value).hex()
    plain = _plain_number(value)
    if plain is not None:
        return type(value).__name__ + ":" + repr(plain)
    if isinstance(value, (list, tuple)):
        items = (
            list.__iter__(value) if isinstance(value, list)
            else tuple.__iter__(value))
        return type(value).__name__ + ":[" + ",".join(
            _stored_form(item) for item in items) + "]"
    if isinstance(value, (set, frozenset)):
        return type(value).__name__ + ":{" + ",".join(sorted(
            _stored_form(item) for item in _base_iter(value))) + "}"
    if isinstance(value, dict):
        return "dict:{" + ",".join(sorted(
            _stored_form(key) + "=" + _stored_form(
                dict.__getitem__(value, key))
            for key in dict.__iter__(value))) + "}"
    try:
        carried = type(value).__repr__(value)
    except Exception:
        carried = object.__repr__(value)
    return "other:" + type(value).__name__ + ":" + carried


def _record_identity(run_id, day, viewer):
    """The identity of one aggregate record, built from the
    stored forms of its run, its day, and its viewer, each part
    carried at its stated length, so the identity keeps
    distinct stored pairs distinct and no part stands in it
    through a plain string reading or a bare separator the
    values themselves can contain."""
    parts = []
    for value in (run_id, day, viewer):
        form = _stored_form(value)
        parts.append(str(len(form)) + ":" + form)
    return "record:" + "|".join(parts)


def _day_match_form(value):
    """The form under which one checkpoint day stands matched:
    a whole day in integer form or in digit text form stands
    as the integer it states, a text day stands as its stored
    text, and every other form stands as its own stored form,
    so a float day and a bool day never stand as the integer
    day they happen to equal in number."""
    if isinstance(value, bool):
        return ("bool", int.__int__(value))
    if isinstance(value, int):
        return ("int", int.__int__(value))
    if isinstance(value, float):
        return ("float", float.__float__(value))
    if isinstance(value, str):
        whole = _whole_day(str.__str__(value))
        if isinstance(whole, int) and not isinstance(whole, bool):
            return ("int", whole)
        return ("str", str.__str__(value))
    if isinstance(value, Decimal):
        if value.is_finite() and value == value.to_integral_value():
            return ("int", int(value))
        return ("other", _stored_form(value))
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return ("int", value.numerator)
        return ("other", _stored_form(value))
    return ("other", _stored_form(value))


def _same_day_form(left, right):
    return _day_match_form(left) == _day_match_form(right)


def _comparison_day(value):
    """The day value a resume comparison judges: the integer a
    whole day form states, the stored text of a text day, or
    the stored form of any other day, so a float day and a
    bool day never compare equal to an integer day."""
    form = _day_match_form(value)
    if form[0] in ("int", "str"):
        return form[1]
    return _stored_form(value)


def _base_value_eq(left, right):
    """Return whether two handed values agree on their stored
    contents, judged through base class operations at every
    level, never through an equality, get, keys, or iteration
    reading a handed value supplies."""
    if left is None or right is None:
        return left is right
    if isinstance(left, str) or isinstance(right, str):
        if not isinstance(left, str) or not isinstance(right, str):
            return False
        return str.__eq__(
            str.__str__(left), str.__str__(right)) is True
    if isinstance(left, dict) or isinstance(right, dict):
        if not isinstance(left, dict) or not isinstance(right, dict):
            return False
        if dict.__len__(left) != dict.__len__(right):
            return False
        for key in dict.__iter__(left):
            matched = None
            found = False
            for other_key in dict.__iter__(right):
                if _base_value_eq(key, other_key):
                    matched = other_key
                    found = True
                    break
            if not found:
                return False
            if not _base_value_eq(
                    dict.__getitem__(left, key),
                    dict.__getitem__(right, matched)):
                return False
        return True
    if isinstance(left, (list, tuple)) or isinstance(
            right, (list, tuple)):
        if not isinstance(left, (list, tuple)) or not isinstance(
                right, (list, tuple)):
            return False
        if isinstance(left, list) != isinstance(right, list):
            return False
        if isinstance(left, list):
            left_items = list(list.__iter__(left))
            right_items = list(list.__iter__(right))
        else:
            left_items = list(tuple.__iter__(left))
            right_items = list(tuple.__iter__(right))
        if len(left_items) != len(right_items):
            return False
        return all(
            _base_value_eq(a, b)
            for a, b in zip(left_items, right_items))
    if isinstance(left, (set, frozenset)) or isinstance(
            right, (set, frozenset)):
        if not isinstance(left, (set, frozenset)) or not isinstance(
                right, (set, frozenset)):
            return False
        return _base_set_eq(left, right)
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, Decimal) or isinstance(right, Decimal):
        if not isinstance(left, Decimal) or not isinstance(
                right, Decimal):
            return False
        return Decimal.__eq__(
            Decimal.__new__(Decimal, left),
            Decimal.__new__(Decimal, right)) is True
    if isinstance(left, Fraction) or isinstance(right, Fraction):
        if not isinstance(left, Fraction) or not isinstance(
                right, Fraction):
            return False
        return Fraction.__eq__(
            Fraction.__new__(Fraction, left),
            Fraction.__new__(Fraction, right)) is True
    left_number = _plain_number(left)
    right_number = _plain_number(right)
    if left_number is not None or right_number is not None:
        if left_number is None or right_number is None:
            return False
        return left_number == right_number
    if isinstance(left, (bytes, bytearray, memoryview)) or isinstance(
            right, (bytes, bytearray, memoryview)):
        if not isinstance(left, (bytes, bytearray, memoryview)) or not isinstance(
                right, (bytes, bytearray, memoryview)):
            return False
        return bytes.__eq__(bytes(left), bytes(right)) is True
    if type(left) is type(right):
        try:
            judged = type(left).__eq__(left, right)
        except Exception:
            judged = NotImplemented
        if isinstance(judged, bool):
            return judged
        try:
            return type(left).__repr__(left) == type(right).__repr__(right)
        except Exception:
            return left is right
    return left is right


def _base_set_eq(left, right):
    """Return whether two handed sets hold matching stored
    elements, matched through base value equality."""
    left_items = []
    for item in (set.__iter__(left) if isinstance(left, set)
                 else frozenset.__iter__(left)):
        left_items.append(item)
    right_items = []
    for item in (set.__iter__(right) if isinstance(right, set)
                 else frozenset.__iter__(right)):
        right_items.append(item)
    if len(left_items) != len(right_items):
        return False
    remaining = list(right_items)
    for item in left_items:
        matched = None
        for index, candidate in enumerate(remaining):
            if _base_value_eq(item, candidate):
                matched = index
                break
        if matched is None:
            return False
        remaining.pop(matched)
    return True


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
    of the variants and past it, in the sister form. A key in
    container dress stands judged as its parts stand judged,
    each part on its own stored text, and as the stored text
    parts joined in order stand judged, so a name split
    across the parts of one container key reads as the one
    name, and a single part container carries the reading of
    its one part."""
    if isinstance(key, _CONTAINER_KEY_FORMS):
        if any(
                _money_key_matches(part, target)
                for part in _container_parts(key)):
            return True
        if _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and _money_key_matches(candidate, target):
                    return True
        if _seg_exact(key, target):
            return True
        joined = _joined_stored_text(key)
        if joined:
            return _money_key_matches(joined, target)
        return False
    if target in _fold_variants(key):
        return True
    return _money_segments_match(_money_segments_by_character(key), target)


def _money_key_carries(key, marker):
    """Whether a key carries the money marker, by the folded
    variants or by the position by position reading above,
    beside the recorded transliterated spelling correction.
    A key in container dress stands judged as at
    _money_key_matches: by each part on its own stored text
    and by the stored text parts joined in order."""
    if isinstance(key, _CONTAINER_KEY_FORMS):
        if any(
                _money_key_carries(part, marker)
                for part in _container_parts(key)):
            return True
        if _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and _money_key_carries(candidate, marker):
                    return True
        if _seg_carrying(key, marker) or _seg_carrying(key, "realmani"):
            return True
        joined = _joined_stored_text(key)
        if joined:
            return _money_key_carries(joined, marker)
        return False
    if any(marker in variant for variant in _fold_variants(key)):
        return True
    segments = _money_segments_by_character(key)
    if _money_segments_carry(segments, marker):
        return True
    return _money_segments_carry(segments, "realmani")


def _folded_money_key(key):
    if isinstance(key, _CONTAINER_KEY_FORMS):
        key = _joined_stored_text(key)
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


def _retention_refusal(act, argument, cause, consequence=None):
    where = ""
    if act is not None:
        where = " at " + act + " on the " + str(argument) + " argument"
    if consequence is None:
        consequence = "and no record stands retained"
    if cause == "cycle":
        return (
            "deep or cyclic record in named form: cause cycle: "
            "a record carrying a cycle stands refused" + where
            + ": the retention bound is 100, counted with the "
            "handed value standing at depth 0 and every container "
            "standing around a part counting toward that bound, "
            + consequence)
    return (
        "deep or cyclic record in named form: cause depth: "
        "a record standing deeper than the retention bound of "
        "100 stands refused" + where + ": the bound is 100, "
        "counted with the handed value standing at depth 0 and "
        "every container standing around a part counting toward "
        "that bound, " + consequence)


def _guard_retention_shape(value, act=None, argument=None,
                           consequence=None):
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
        if id(node) in path:
            raise ValueError(_retention_refusal(act, argument, "cycle", consequence))
        if depth > 100:
            raise ValueError(_retention_refusal(act, argument, "depth", consequence))
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
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
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


def _dict_keys_carry_split(readings, pairs, pattern):
    """Whether the folded marker stands split across two or
    more consecutive keys of one dict, in the joined reading
    form settlement S-14 states: the first key contributes a
    tail of one of its readings as the opening of the marker,
    each middle key one whole reading as an exact piece of
    it, and the last key a reading that begins with its
    closing. A key whose reading stands empty contributes no
    character to the joined reading, so the occurrence may
    cross such a key, stepped past on its empty reading and
    unused by the occurrence. The marker bars only where a
    value stands under every key the occurrence uses, as the
    walk states for a money name."""
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
                        if ok:
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
                            if next_ok:
                                return True
    return False


def _dict_keys_tile_exact(readings, pairs, target, require_value):
    """Whether a run of two or more consecutive dict keys, in
    stored order, joins exactly to the target on one folded
    reading of each key it uses, in the joined reading form
    settlement S-14 states, a key whose reading stands empty
    stepped past inside the run on that empty reading. Where
    require_value stands stated, the name bars only where a
    value stands under every key the run uses, as the walk
    states for that name; a stepped past key stands unused.
    A name standing inside one key alone stands judged by
    the per key acts, never here, so a run stands only on
    two or more pieces."""
    visited = set()
    stack = [(0, 0, 0, True)]
    while stack:
        index, pos, pieces, ok = stack.pop()
        if pos == len(target):
            if pieces >= 2 and ok:
                return True
            continue
        if index >= len(pairs):
            continue
        state = (index, pos, pieces >= 2, ok)
        if state in visited:
            continue
        visited.add(state)
        if pieces == 0:
            stack.append((index + 1, 0, 0, True))
        next_ok = ok and (
            pairs[index][1] is not None or not require_value)
        for option in readings[index]:
            if not option:
                stack.append((index + 1, pos, pieces, ok))
            elif option == target[pos:pos + len(option)]:
                stack.append((
                    index + 1, pos + len(option),
                    pieces + 1, next_ok))
    return False


def _dict_node_money_barred(value):
    """Whether a dict handed to the Recorder money walk stands
    barred at its own node, in the form settlement S-14
    states: the walk judges a dict handed to it at the dict
    node itself, on the joined reading of the dict's keys in
    stored order, in the folded forms in which the walk
    judges a single key. The folded money marker split
    across two keys of the dict stands judged on that joined
    reading, and the amount and currency pair, which the
    walk frames at dict level across the keys of one dict
    together, stands judged where each name stands split
    across two keys of the same dict."""
    pairs = list(dict.items(value))
    if len(pairs) < 2:
        return False
    readings = []
    for key, item in pairs:
        options = set(_fold_variants(key))
        options.add(_folded_money_key(key))
        readings.append(options)
    for pattern in (_MONEY_MARKER_FOLDED, "realmani"):
        if _dict_keys_carry_split(readings, pairs, pattern):
            return True
    amount_stands = _dict_keys_tile_exact(
        readings, pairs, "amount", True) or any(
            _money_key_matches(key, "amount") and item is not None
            for key, item in pairs)
    currency_stands = _dict_keys_tile_exact(
        readings, pairs, "currency", False) or any(
            _money_key_matches(key, "currency")
            for key, item in pairs)
    return amount_stands and currency_stands


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
        if _dict_node_money_barred(value):
            return True
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
            raise ValueError(
                "unknown store kind: " + _safe_str(store_kind)
                + "; a store kind stands among sweep, pilot, and "
                "live, and no store stands created")
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
                failure = LookupFailure(path)
                failure.failure = {
                    "name": ONE_LOOKUP_FAILURE_NAME,
                    "run_status": "failed",
                    "complete": False,
                    "store_path": path,
                }
                failure.args = (
                    ONE_LOOKUP_FAILURE_NAME
                    + ": the store file at " + str(path)
                    + " could not be read as a store",)
                raise failure from exc
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
        records = [merged[rid] for rid in sorted(merged, key=lambda item: _safe_str(item))]
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
        rid = dict.get(record, "run_id") or dict.get(
            record, "run_identifier")
        if rid is None:
            raise ValueError(
                "identity less record: no run identifier stands on the "
                "record, and no record stands retained under no identifier")
        if not isinstance(rid, str):
            raise ValueError(
                "identity less record: the run identifier stands in "
                "no identifier form: a run identifier in text form "
                "stands required, and no record stands retained "
                "under it")
        if str.__len__(rid) == 0:
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
        _guard_retention_shape(record, "retain_run_record", "record")
        if _carries_real_money_field(record):
            raise ValueError(
                "real money field in named form: a run record carrying "
                "a real money value stands refused at retention, by "
                "field name and by amount and currency shape")
        if rid in self._records:
            raise ValueError("second record for the same run is rejected: " + _safe_str(rid))
        try:
            stored = _safe_copy(record)
        except RecursionError as exc:
            raise ValueError(_DEEP_REFUSAL) from exc
        self._records[rid] = stored
        self._index.append(rid)
        try:
            self._flush()
        except Exception as exc:
            del self._records[rid]
            self._index.remove(rid)
            raise ValueError(
                "recorder store flush failure: the retained record stands "
                "not written, and the prior store file stands whole: "
                + _safe_str(exc)) from exc
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
        kept_records = self._records
        kept_index = self._index
        self._records = {}
        self._index = []
        try:
            self._flush(merge_disk=False)
        except Exception as exc:
            self._records = kept_records
            self._index = kept_index
            raise ValueError(
                "recorder store flush failure: the store stands not "
                "cleared, and the prior store file stands whole: "
                + _safe_str(exc)) from exc

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
        raise ValueError(
            "unknown store kind: " + _safe_str(store_kind)
            + "; a store kind stands among sweep, pilot, and live")
    for kind in STORE_KINDS:
        if str.__eq__(store_kind, kind):
            return kind
    raise ValueError(
        "unknown store kind: " + _safe_str(store_kind)
        + "; a store kind stands among sweep, pilot, and live")


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
    if not isinstance(records, (list, tuple)):
        return False
    stored_records = list(_base_iter(records))
    if len(stored_records) != 1:
        return False
    seen = []
    for record in stored_records:
        if not isinstance(record, dict):
            return False
        rid = dict.get(record, "run_id")
        if rid is None:
            rid = dict.get(record, "run_identifier")
        if rid is None:
            return False
        if any(_base_value_eq(rid, earlier) for earlier in seen):
            return False
        seen.append(rid)
        writers = dict.get(record, "group_writers")
        if writers is None:
            writers = {}
        if not isinstance(writers, dict):
            return False
        for group, writer in dict.items(writers):
            owner = None
            for owned_group, owned_writer in dict.items(
                    GROUP_OWNERS):
                if _base_value_eq(group, owned_group):
                    owner = owned_writer
                    break
            if owner is not None and not _base_value_eq(
                    writer, owner):
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
    later rederivation with a bare TypeError. The deliveries
    stand read once, through the base iteration of their form
    where they stand in a container form, and a handed iterator
    stands read whole by that one reading, so no fabricated
    delivery stands retained and no valid delivery stands lost
    to a second reading. The component values stand read
    through the base iteration of their form on the same
    ground. A delivery in no record form stands skipped in
    both loops, so it neither crashes the act nor leaves a
    partial retention standing behind a crash. The run
    identifier stands guarded in the form the sibling retention
    acts of this module carry: no identifier stands refused in
    named form, and an identifier in an unhashable form stands
    refused in named form, before any store keying. A deliveries
    value in no container form and in no iterator form stores
    no delivery in any form this act reads, so it stands read
    as no deliveries, never through an iteration reading the
    value itself supplies. The numeric refusal reads component
    values in set and frozenset form through the base iteration
    of their form, and a component value standing as a single
    text stands judged as the one component it states."""
    if run_id is None:
        raise ValueError(
            "identity less aggregate delivery: no run identifier "
            "stands supplied, and no daily aggregate delivery "
            "stands retained under no identifier")
    try:
        hash(run_id)
    except TypeError as exc:
        raise ValueError(
            "identity less aggregate delivery: the run identifier "
            "stands in an unhashable form, and no daily aggregate "
            "delivery stands retained under it") from exc
    if isinstance(deliveries, (list, tuple, set, frozenset)):
        stored_deliveries = list(_base_iter(deliveries))
    elif _is_iterator(deliveries):
        stored_deliveries = list(deliveries)
    else:
        stored_deliveries = []
    for delivery in stored_deliveries:
        if not isinstance(delivery, dict):
            continue
        for field in ("joint_outcome_components",
                      "component_denominators"):
            values = dict.get(delivery, field)
            if isinstance(values, (list, tuple, set, frozenset)):
                components = list(_base_iter(values))
            elif isinstance(values, str):
                components = [values]
            else:
                components = None
            if components is not None:
                for component in components:
                    if _numeric_component(component):
                        continue
                    where = (
                        " for viewer " + _safe_str(dict.get(delivery, "viewer_id"))
                        + " at day " + _safe_str(dict.get(delivery, "simulated_day")))
                    if isinstance(component, (int, float)) and not isinstance(
                            component, bool):
                        raise ValueError(
                            "daily aggregate delivery in named form: "
                            "the " + field + " of the delivery" + where
                            + " stand in a non finite numeric form "
                            "(component " + _safe_repr(component)
                            + "), and that delivery stands not retained")
                    raise ValueError(
                        "daily aggregate delivery in named form: the "
                        + field + " of the delivery" + where
                        + " stand in a non numeric form (component "
                        + _safe_repr(component)
                        + "), and that delivery stands not retained")
    stored = _AGGREGATE_DELIVERIES.setdefault(run_id, {})
    for delivery in stored_deliveries:
        if not isinstance(delivery, dict):
            continue
        key = (
            _retention_day_key(dict.get(delivery, "simulated_day")),
            _stored_form(dict.get(delivery, "viewer_id")))
        stored[key] = _safe_copy(delivery)
    return len(stored)


def _retention_day_key(day):
    """The retention key of one delivery day: the day match
    form of the day, serialised, so every form the match form
    states as the integer day (an integer, digit text in any
    signed or spaced dress, an integral Decimal, and an
    integral Fraction) stands retained once, as one delivery
    per run per day per viewer, while a day in a form the
    match form states as distinct, such as a float day, a
    bool day, or a bytes family day, keeps its own form."""
    form = _day_match_form(day)
    if form[0] == "str":
        return "str:" + str(len(form[1])) + ":" + form[1]
    if form[0] == "other":
        return "other:" + form[1]
    return form[0] + ":" + str(form[1])


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
    """The sort key for one retained delivery, by its day and its
    viewer, each read by its stored characters through
    _stored_text, never through a reading the handed day or
    viewer supplies.

    The ordering, in plain terms. Numbered days first, in number
    order: an integer day counts as itself, and a day in digit
    text counts as the number its stored digits state, so the
    numeric day value itself never splits by form. Beside that
    number the key carries the stored form of the day as a tie
    breaker, so distinct stored forms of one numbered day keep
    a stable order of their own instead of standing in
    retention order, and only then do records stand ordered by
    the stored text of the viewer, with the stored form of the
    viewer carried beside that text on the same ground. Every
    other day stands after all numbered days. Among those later
    records, the order runs by the stored text of the day,
    character by character, then by the stored form of the day,
    and then by the stored text of the viewer and its stored
    form, with the day and the viewer kept as separate parts of
    the key, so two records whose day and viewer texts differ
    never take one key from a joining of the two texts, and two
    records whose days or viewers differ only in stored form,
    such as a viewer standing as no value against a viewer
    standing as the empty text or as a number, never take one
    key either. A day that carries no stored text, such as None
    or a decimal number, stands in the later group ordered by
    its stored form among the days carrying no stored text, and
    records that still share one key keep the order in which
    their deliveries were retained. So the text minus 1, whose
    first character is not a digit, stands in the later group
    after day 100, while the integer minus 1 stands first among
    the numbered days; the text plus 2 stands in the later group
    on the same ground; and a circled digit, whose stored text
    states a digit the number conversion cannot read, stands in
    the later group ordered by its character, after the plain
    letter and digit texts."""
    day, viewer = item
    viewer_text = _stored_text(viewer)
    viewer_form = _stored_form(viewer)
    if isinstance(day, int) and not isinstance(day, bool):
        return (0, int.__int__(day), _stored_form(day),
                viewer_text, viewer_form)
    day_text = _stored_text(day)
    if isinstance(day, str):
        stripped = day_text.strip()
        if stripped.isdecimal():
            try:
                return (0, int(stripped), _stored_form(day),
                        viewer_text, viewer_form)
            except ValueError:
                return (1, 0, day_text, _stored_form(day),
                        viewer_text, viewer_form)
    return (1, 0, day_text, _stored_form(day),
            viewer_text, viewer_form)


def _aggregates_from_deliveries(run_id):
    stored = _AGGREGATE_DELIVERIES.get(run_id)
    if not stored:
        return None
    records = []
    ordered = sorted(
        stored.values(),
        key=lambda delivery: _day_sort_key((
            delivery.get("simulated_day"),
            delivery.get("viewer_id"))))
    for delivery in ordered:
        day = delivery.get("simulated_day")
        viewer = delivery.get("viewer_id")
        base = {
            "run_id": run_id,
            "run_identifier": run_id,
            "simulated_day": day,
            "viewer_id": viewer,
            "viewer_identifier": viewer,
            "record_identity": _record_identity(run_id, day, viewer),
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
                    marked[field] = _safe_copy(delivery[field])
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
            "gate_passing_share_per_epoch": _safe_copy(shares),
            "excluded_class_counts_and_shares": _safe_copy(
                delivery.get("excluded_class_counts_and_shares")
                or delivery.get("excluded_class_counts") or {}),
            "divergence_companion": _safe_copy(
                delivery.get("divergence_companion")
                or {"nil_divergence_components": []}),
        })
        records.append(record)
    return records


def aggregate_manifest_for_run(run_id):
    """Return the aggregate manifest of one run: for each aggregate
    record the aggregation act writes, its identity, its day, its
    viewer, its writer, and
    its amendment standing, in the ruling Entry 12 form. The entries
    stand in the day order stated at _day_sort_key: numbered days
    first in number order, then every other day by its stored day
    text and then its stored viewer text. Where no
    aggregate stands written for the run, one form only entry stands
    returned."""
    computed = _aggregates_from_deliveries(run_id)
    if computed is None:
        return [{"run_id": run_id, "form": FORM_ONLY}]
    return [
        {
            "record_identity": record.get("record_identity"),
            "simulated_day": record.get("simulated_day"),
            "viewer_id": record.get("viewer_id"),
            "writer": record.get("writer"),
            "amendment_standing": record.get("amendment_standing"),
            "amending_act": record.get("amending_act"),
        }
        for record in computed
    ]


def daily_aggregates_for_run(run_id="run-under-test", deliveries=None):
    """Return the daily aggregates of one run. Where deliveries
    stand handed in or retained, the aggregates stand computed from
    them, in the day order stated at _day_sort_key: numbered days
    first in number order, then every other day by its stored day
    text and then its stored viewer text. Where none stand, one
    form record stands returned with a form only marker inside the
    record itself."""
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
    as a day of the run. The aggregates stand read once into a
    stored list, through the base iteration of their form where
    they stand in a container form, and a handed iterator stands
    read whole by that one reading, and each aggregate record
    stands read through the base dict readings, so no
    classification stands computed from a reading the handed
    aggregates or records supply and no later pass reads an
    exhausted handing."""
    if aggregates is None:
        return None
    if isinstance(aggregates, (list, tuple, set, frozenset)):
        stored_aggregates = list(_base_iter(aggregates))
    else:
        stored_aggregates = list(aggregates)
    if not stored_aggregates:
        return None
    states = [
        {
            "record_identity": (
                dict.get(record, "record_identity")
                if isinstance(record, dict) else None),
            "writer": (
                dict.get(record, "writer")
                if isinstance(record, dict) else None),
            "amendment_standing": (
                (dict.get(record, "amendment_standing")
                 if isinstance(record, dict) else None)
                or "not stated on the record"),
            "amending_act": (
                dict.get(record, "amending_act")
                if isinstance(record, dict) else None),
        }
        for record in stored_aggregates
    ]
    if any(
            isinstance(record, dict)
            and dict.get(record, "form") == FORM_ONLY
            for record in stored_aggregates):
        return {
            "classification": None,
            "form": FORM_ONLY,
            "days": 0,
            "placeholder_records": len(stored_aggregates),
            "carriage": (
                "form only, no classification stands computed "
                "from a placeholder aggregate"),
            "aggregate_states": states,
        }
    totals = [0, 0, 0, 0]
    for record in stored_aggregates:
        if not isinstance(record, dict):
            return None
        components = dict.get(record, "joint_outcome_components")
        if components is None:
            components = []
        if isinstance(components, (list, tuple)):
            components = list(_base_iter(components))
        if len(components) != 4:
            return None
        if not _components_stand_numeric(components):
            return None
        for position, value in enumerate(components):
            totals[position] += value
    return {
        "classification": "rederived_from_daily_aggregates",
        "days": len(stored_aggregates),
        "component_totals": totals,
        "carriage": "computed from the aggregates handed in",
        "aggregate_states": states,
    }


def validate_daily_aggregates(aggregates):
    """Validate daily aggregate records on their stored contents:
    every record stands read through the base dict readings, its
    containment judged by the base containment reading, its
    fields taken by the base get reading, and its component
    values read through the base iteration of their form, never
    through a containment, item, or iteration reading the handed
    record supplies."""
    if not isinstance(aggregates, (list, tuple)):
        return False
    stored_records = list(_base_iter(aggregates))
    if not stored_records:
        return False
    for record in stored_records:
        if not isinstance(record, dict):
            return False
        if dict.__contains__(record, "singular_vector"):
            return False
        if not dict.__contains__(record, "viewer_id"):
            return False
        for field in ("joint_outcome_components",
                      "component_denominators"):
            if dict.__contains__(record, field):
                values = dict.get(record, field)
                if isinstance(values, (list, tuple)):
                    values = list(_base_iter(values))
                if not _components_stand_numeric(values):
                    return False
        if dict.__contains__(record, "joint_outcome_components"):
            components = dict.get(record, "joint_outcome_components")
            if isinstance(components, (list, tuple)):
                components = list(_base_iter(components))
            if not isinstance(components, (list, tuple)):
                return False
            if len(components) != 4:
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
    if components is None:
        components = {}
    if not isinstance(components, dict):
        raise ValueError(
            "joint outcome component in named form: the components "
            "stand as no record of their stored parts")
    record = {}
    viewers = set()
    for field, parts in mod01.JOINT_OUTCOME_COMPONENT_PARTS.items():
        component = dict.get(components, field)
        if not isinstance(component, dict):
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " stands as no record of its stored parts")
        missing = [part for part in parts if dict.get(component, part) is None]
        if missing:
            raise ValueError(
                "joint outcome component in named form: component "
                + field + " carries no " + ", ".join(missing))
        viewers.add(dict.get(component, "viewer_identifier"))
        record[field] = _safe_copy(component)
    if len(viewers) != 1:
        raise ValueError(
            "joint outcome component in named form: the components "
            "of one vector carry more than one viewer identifier")
    record["divergence_companion"] = _safe_copy(
        divergence_companion or {"nil_divergence_components": []})
    if not mod01.validate_record("15", record):
        raise ValueError(
            "joint outcome component in named form: the assembled "
            "record fails Form 15 validation")
    return record


def _gate_epoch_key(epoch):
    """The slot key of one epoch: a text epoch stands under its
    own text, and every other epoch form stands under its
    stored form, so the integer, bool, and float forms of one
    epoch number never take one slot. One bound stands on the
    text limb: a stored form is itself a text string, so a
    text epoch that spells a stored form would land on the
    slot of the non text epoch whose stored form it spells.
    A text epoch carrying a colon, and the text epoch none,
    which is the stored form of the None epoch, therefore
    stand under their own stored form instead of under their
    bare text, so no text epoch takes the slot of a non text
    epoch and no recorded share stands silently overwritten.
    A text epoch carrying no colon keeps its own text as its
    key, exactly as the standing contract states."""
    if isinstance(epoch, str):
        text = str.__str__(epoch)
        if ":" in text or text == "none":
            return _stored_form(epoch)
        return text
    return _stored_form(epoch)


def _gate_shares_copy(run_id):
    return {
        _safe_copy(key): _safe_copy(value)
        for key, value in _GATE_SHARES.get(run_id, {}).items()}


def record_gate_passing_share(run_id, epoch, share, simulated_day=None):
    """Record the gate passing share handed over at the close of an
    epoch, as a retained delivery of the run."""
    shares = _GATE_SHARES.setdefault(run_id, {})
    key = _gate_epoch_key(epoch)
    shares[key] = {"share": _safe_copy(share), "simulated_day": simulated_day}
    return _safe_copy(shares[key])


def gate_passing_shares_for_run(run_id):
    """Read the recorded gate passing shares of a run. Reading
    never writes: an unrecorded run returns an empty mapping."""
    return _gate_shares_copy(run_id)


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
    run_id = dict.get(entry, "run_identifier") or dict.get(entry, "run_id")
    if run_id is None:
        raise ValueError(
            "identity less entry: no run identifier stands on the "
            "entry, and no entry stands retained under no identifier")
    try:
        hash(run_id)
    except TypeError as exc:
        raise ValueError(
            "identity less entry: the run identifier stands in an "
            "unhashable form, and no entry stands retained under "
            "it") from exc
    _guard_retention_shape(entry, "retain_event_log_entry", "entry")
    bucket = _EVENT_LOGS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if _stored_form(existing) == _stored_form(entry):
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
    run_id = dict.get(snapshot, "run_identifier") or dict.get(
        snapshot, "run_id")
    if run_id is None:
        raise ValueError(
            "identity less snapshot: no run identifier stands on the "
            "snapshot, and no snapshot stands retained under no identifier")
    try:
        hash(run_id)
    except TypeError as exc:
        raise ValueError(
            "identity less snapshot: the run identifier stands in an "
            "unhashable form, and no snapshot stands retained under "
            "it") from exc
    _guard_retention_shape(snapshot, "retain_daily_snapshot", "snapshot")
    bucket = _DAILY_SNAPSHOTS.setdefault((store_kind, run_id), [])
    for existing in bucket:
        if _stored_form(existing) == _stored_form(snapshot):
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
    integer stands as itself, and a string stating whole decimal
    digits stands as the integer it states, so the string 1 beside
    the integer 1 is one day. The text reading is a decimal digit
    reading only: a digit character that is not a decimal digit,
    such as a superscript digit, which the digit test accepts but
    the decimal test does not, is not read as a day number at all
    and stands as itself, as any other form stands as itself, and
    no bare conversion error escapes this reading. A string
    stands read through its stored text, taken through the base
    class string form, never through a strip reading the handed
    string itself supplies."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = str.__str__(value).strip()
        if text.isdecimal():
            try:
                return int(text)
            except ValueError:
                return value
        if text.startswith("+") and text[1:].isdecimal():
            try:
                return int(text)
            except ValueError:
                return value
        if text.startswith("-") and text[1:].isdecimal():
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
    as itself and stands judged by no comparison. A string
    stands read through its stored text, taken through the base
    class string form, never through a strip or lower reading
    the handed string itself supplies."""
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
        text = str.__str__(value).strip()
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
    run_id = dict.get(manifest, "run_identifier") or dict.get(
        manifest, "run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "manifest, and no checkpoint stands retained under no identifier")
    try:
        hash(run_id)
    except TypeError as exc:
        raise ValueError(
            "identity less checkpoint: the run identifier stands in "
            "an unhashable form, and no checkpoint stands retained "
            "under it") from exc
    _guard_retention_shape(manifest, "retain_checkpoint", "manifest")
    bucket = _CHECKPOINTS.setdefault((store_kind, run_id), [])
    if any(
            _same_day_form(
                dict.get(item, "simulated_day"),
                dict.get(manifest, "simulated_day"))
            for item in bucket):
        _REJECTED_CHECKPOINT_WRITES.append({
            "run_id": run_id,
            "run_identifier": run_id,
            "simulated_day": dict.get(manifest, "simulated_day"),
            "store_kind": store_kind,
            "manifest": _safe_copy(manifest),
            "recorded_as": "rejected write",
        })
        judged_day = dict.get(manifest, "simulated_day")
        judged_form = _day_match_form(judged_day)
        named_day = judged_form[1] if judged_form[0] == "int" else judged_day
        raise ValueError(
            "second checkpoint for the same run and day is rejected: "
            + str(run_id) + " day " + str(named_day))
    if len(bucket) >= 10000:
        raise ValueError("checkpoint cap in named form: a run stands at the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no further checkpoint stands retained")
    stored = _safe_copy(manifest)
    if "journal_event_count_at_checkpoint" not in stored:
        stored["journal_event_count_at_checkpoint"] = len(
            event_log_entries(run_id, store_kind))
    state_copy = None
    if dict.get(manifest, "checkpoint_state") is not None:
        state_copy = _safe_copy(
            dict.__getitem__(manifest, "checkpoint_state"))
    bucket.append(stored)
    if state_copy is not None:
        _CHECKPOINT_STATES[(store_kind, run_id,
                            _day_match_form(
                                dict.get(manifest, "simulated_day")))] = (
            state_copy)
    return _safe_copy(manifest)


def rejected_checkpoint_writes(run_id=None):
    """Read the rejected checkpoint writes recorded under contract
    C-01 uniqueness: each second write for a run and day that
    already held a manifest stands recorded here as a rejected
    write, and no rejected write stands retained as a checkpoint.
    Reading never writes."""
    return _safe_copy([
        item for item in _REJECTED_CHECKPOINT_WRITES
        if run_id is None or item.get("run_id") == run_id
    ])


def checkpoint_state_at(run_id, simulated_day, store_kind="sweep"):
    """Read the CheckpointState standing beside a retained
    checkpoint manifest, where one was written with it. Reading
    never writes: no state beside the manifest returns None. A
    day queried in a float or bool form stands matched only
    against a retained day in that same form, never against the
    integer day it happens to equal in number."""
    if _store_kind_stands(store_kind):
        store_kind = _canonical_store_kind(store_kind)
    state = _CHECKPOINT_STATES.get(
        (store_kind, run_id, _day_match_form(simulated_day)))
    if state is None:
        return None
    return _safe_copy(state)


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
    judged on its stored text, taken through the base class
    string form, and that stored text stands lowered, with
    underscores and hyphens read as spaces and runs
    of whitespace read as one space, the reading form the standing
    named forms are checked in. No lower reading the handed
    string itself supplies stands honoured."""
    if not isinstance(value, str):
        return ""
    text = str.__str__(value).lower().replace("_", " ").replace("-", " ")
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
    protections = []
    if integrity_flag_open:
        protections.append("an open integrity flag")
    if named_in_retention_record:
        protections.append("a checkpoint named in a retention record")
    if regression_corpus_copy:
        protections.append("a regression corpus copy")
    if protections:
        raise ValueError(
            "checkpoint deletion refused: a clause C8 protection stands "
            "on the checkpoint, namely " + "; ".join(protections)
            + ", and no checkpoint stands deleted")
    store_kind = _canonical_store_kind(store_kind)
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    kept = [
        item for item in bucket
        if not _same_day_form(
            dict.get(item, "simulated_day"), checkpoint_day)
    ]
    removed = len(bucket) - len(kept)
    if removed:
        _CHECKPOINTS[(store_kind, run_id)] = kept
        _CHECKPOINT_STATES.pop(
            (store_kind, run_id, _day_match_form(checkpoint_day)), None)
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
    if not isinstance(manifest, dict):
        raise ValueError(
            "identity less checkpoint: a checkpoint position check "
            "stands on a checkpoint record, and no other form "
            "stands checked")
    run_id = dict.get(manifest, "run_identifier") or dict.get(
        manifest, "run_id")
    position = dict.get(manifest, "journal_position")
    if run_id is None:
        return {
            "check": "checkpoint position check",
            "outcome": (
                "not checked: no run identifier stands on the "
                "manifest, and no position stands checked"),
            "journal_position": position,
            "retained_log_length": 0,
            "reportable": False,
        }
    if not isinstance(position, int) or isinstance(position, bool):
        if position is None:
            wording = "the journal position stands missing"
        else:
            wording = (
                "the journal position stands in no integer form: "
                + _safe_repr(position))
        return {
            "check": "checkpoint position check",
            "outcome": (
                "not checked: " + wording
                + ", and no retention failure stands reported"),
            "journal_position": position,
            "retained_log_length": len(
                event_log_entries(run_id, store_kind)),
            "reportable": False,
        }
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


def _nondecimal_digit_text(value):
    """Return whether one value stands in digit text that is not
    decimal digit text: text, in plain form or behind one leading
    sign, whose characters the digit test accepts and the decimal
    test does not, such as a superscript digit character. Such a
    text is not a day under the decimal text reading at all, even
    though it stands as its own stored text form for sameness
    under the day match form at every other act. The sign dress
    stands read whole: any run of leading signs, a space standing
    between a sign and the digit text, and one trailing sign all
    stand peeled before the digit test, so a non decimal digit
    behind a second sign, behind a space after its sign, or
    carrying a trailing sign stands in this form as surely as
    the plain and single signed forms do."""
    if not isinstance(value, str):
        return False
    text = str.__str__(value).strip()
    while text[:1] in ("+", "-"):
        text = text[1:].lstrip()
    if text[-1:] in ("+", "-"):
        text = text[:-1].rstrip()
    return bool(text) and text.isdigit() and not text.isdecimal()


def _close_day_output(group):
    """The day one close group stands named by on the close
    record: a group standing as the integer day through decimal
    digit text is named by that integer day, in the integer form,
    and every other group is named by the day it stores."""
    form, day = group
    if form[0] == "int" and isinstance(day, str):
        return form[1]
    return day


def close_run_retention(run_id, tier, store_kind="sweep"):
    """Apply the clause C3 retained set at run close: Tier 0 keeps
    no checkpoint, Tier 1 keeps the final checkpoint only, Tier 2
    keeps the final checkpoint and the tenth point checkpoints,
    and Tier 3 keeps the final checkpoint and every daily
    checkpoint. Checkpoints outside the set stand released at
    close, and the release stands on the returned record. The
    close day set stands built under the day match form, with two
    readings from stored text: a day in decimal digit text stands
    in the set as the integer day it names and stands named on
    the record by that integer, and a day in digit text that is
    not decimal digit text stands outside the close day set
    altogether, neither kept nor released by this act, its
    checkpoint and its state standing untouched by the close."""
    tier_text = (
        _stored_text(tier) if isinstance(
            tier, (str, bytes, bytearray, memoryview)) else None)
    if tier_text not in ("Tier 0", "Tier 1", "Tier 2", "Tier 3"):
        raise ValueError(
            "unknown retention tier for the close act: "
            + _vocabulary_text(tier)
            + "; a retention tier stands among Tier 0, Tier 1, "
            "Tier 2, and Tier 3, and no close stands performed")
    tier = tier_text
    store_kind = _canonical_store_kind(store_kind)
    bucket = _CHECKPOINTS.get((store_kind, run_id), [])
    groups = []
    seen_forms = []
    for item in bucket:
        day = dict.get(item, "simulated_day")
        form = _day_match_form(day)
        if form not in seen_forms:
            seen_forms.append(form)
            groups.append((form, day))
    excluded_forms = [
        form for form, day in groups if _nondecimal_digit_text(day)]
    excluded_days = [
        _close_day_output(group) for group in groups
        if group[0] in excluded_forms]
    groups = [
        group for group in groups
        if group[0] not in excluded_forms]

    def _close_order(group):
        form, day = group
        if form[0] == "int":
            return (0, form[1], "")
        return (1, 0, _stored_form(day))

    groups.sort(key=_close_order)
    if not groups or tier == "Tier 3":
        kept_groups = list(groups)
    elif tier == "Tier 0":
        kept_groups = []
    elif tier == "Tier 1":
        kept_groups = [groups[-1]]
    else:
        tenth = [
            group for position, group in enumerate(groups, start=1)
            if position % 10 == 0
        ]
        kept_groups = [
            group for group in groups
            if group in tenth or group is groups[-1]]
    kept_forms = [form for form, day in kept_groups]
    kept_days = [_close_day_output(group) for group in kept_groups]
    released_days = [
        _close_day_output(group) for group in groups
        if group[0] not in kept_forms]
    released_forms = [
        form for form, day in groups if form not in kept_forms]
    if released_forms:
        _CHECKPOINTS[(store_kind, run_id)] = [
            item for item in bucket
            if _day_match_form(
                dict.get(item, "simulated_day")) in kept_forms
            or _day_match_form(
                dict.get(item, "simulated_day")) in excluded_forms
        ]
        for form in released_forms:
            _CHECKPOINT_STATES.pop((store_kind, run_id, form), None)
    return {
        "run_id": run_id,
        "retention_tier": tier,
        "kept_days": kept_days,
        "released_days": released_days,
        "excluded_days": excluded_days,
        "excluded_statement": (
            "the days in excluded_days stand outside the close "
            "day set: their checkpoints and states stand untouched "
            "by the close"),
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
    if not isinstance(manifest, dict):
        raise ValueError(
            "identity less checkpoint: a portable checkpoint "
            "manifest stands as a record carrying a run "
            "identifier, and no other form stands made portable")
    run_id = dict.get(manifest, "run_identifier") or dict.get(
        manifest, "run_id")
    day = dict.get(manifest, "simulated_day")
    parts = []
    for value in (run_id, day):
        form = _stored_form(value)
        parts.append(str(len(form)) + ":" + form)
    relative = "checkpoints/" + "/".join(parts)
    return {
        "relative_identifier": relative,
        "manifest": _safe_copy(manifest),
        "portable": True,
    }


def restore_check(portable, present_identifiers):
    """Return whether a portable manifest restores: its relative
    identifier stands among the identifiers present. The portable
    manifest stands read through the base class dict reading, on
    the identifier it stores, never through a get reading the
    handed manifest itself supplies, as at the cured portable
    manifest and resume acts beside this one."""
    identifier = (
        dict.get(portable, "relative_identifier")
        if isinstance(portable, dict) else None)
    try:
        present_set = set(present_identifiers)
    except Exception:
        raise ValueError(
            "restore_check stands refused: the present identifiers "
            "stand in no iterable form, a set of present identifiers "
            "stands required, and no restore standing stands "
            "returned") from None
    try:
        return identifier in present_set
    except TypeError:
        raise ValueError(
            "restore_check stands refused: the relative identifier "
            "stands in an unhashable form, a present identifier in "
            "text form stands required, and no restore standing "
            "stands returned") from None


def replay_check(original, resumed):
    """The exact replay check after resume, at record level and
    verdict level only. No state hash equality stands claimed
    while OP-24 stands partial. Each record stands read through
    the base class dict reading, on the record and verdict it
    stores, never through a get reading the handed record itself
    supplies."""
    record_equal = (
        (dict.get(original, "record") if isinstance(original, dict)
         else None)
        == (dict.get(resumed, "record") if isinstance(resumed, dict)
            else None))
    verdict_equal = (
        (dict.get(original, "verdict") if isinstance(original, dict)
         else None)
        == (dict.get(resumed, "verdict") if isinstance(resumed, dict)
            else None))
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
        raise ValueError(
            "unknown GC-08 record kind: " + _safe_str(kind)
            + "; a GC-08 record kind stands among "
            "dependency_manifest and call_log, and no record "
            "stands retained")
    if owner_id is None:
        raise ValueError(
            "identity less GC-08 record: no owner identifier "
            "stands supplied, and no record stands retained "
            "under no identifier")
    try:
        hash(owner_id)
    except TypeError as exc:
        raise ValueError(
            "identity less GC-08 record: the owner identifier "
            "stands in an unhashable form, and no record stands "
            "retained under it") from exc
    _GC08_RECORDS[(kind, owner_id)] = _safe_copy(record)
    return _safe_copy(record)


def gc08_record(kind, owner_id):
    """Read one retained GC-08 record. Reading never writes: an
    absent record raises the named lookup failure, with the
    identifier carried under the agreed key run_identifier and
    the record kind sought stated in the failure."""
    owner_unhashable = False
    try:
        hash(owner_id)
    except TypeError:
        owner_unhashable = True
    if owner_unhashable or (kind, owner_id) not in _GC08_RECORDS:
        failure = LookupFailure(owner_id, record_kind=kind)
        failure.failure = {
            "name": ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": owner_id,
            "record_kind": kind,
        }
        raise failure
    return _safe_copy(_GC08_RECORDS[(kind, owner_id)])


def _stated_count(value, name):
    """Read one count in its stated integer form only. A string, a
    fraction, a boolean, or a negative count stands refused in
    named form, and no value stands converted silently. The
    count stands returned as a plain integer holding the value
    the handed count stores, read through the base integer
    reading, so the sign judgement above and every arithmetic
    step a consumer runs on the count run on the stored value
    and never on an operator reading the handed count
    supplies."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands in a non integer form, and no count "
            "stands converted silently")
    plain = int.__int__(value)
    if plain < 0:
        raise ValueError(
            "storage accounting count in named form: the count for "
            + str(name) + " stands negative, and no negative stock "
            "stands accounted")
    return plain


def storage_accounting(retained):
    if not isinstance(retained, dict):
        raise ValueError(
            "storage accounting count in named form: the retained set "
            "stands as a record of counts, and no other form stands "
            "accounted")
    summaries = _stated_count(
        dict.get(retained, "summaries", 0), "summaries")
    snapshots = _stated_count(
        dict.get(retained, "daily_snapshots", 0), "daily_snapshots")
    logs = _stated_count(
        dict.get(retained, "event_logs", 0), "event_logs")
    checkpoints = _stated_count(
        dict.get(retained, "checkpoints", 0), "checkpoints")
    copies = _stated_count(
        dict.get(retained, "held_corpus_copies", 0), "held_corpus_copies")
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


def _claimed_total(claimed, name):
    """Read one claimed total through the stated count form, so
    the total stands judged by the integer it stores and never
    by an equality reading the claimed value supplies. A total
    standing in no stated count form, or standing negative,
    stands as no total, and the claim that carries it stands
    not validated."""
    if not dict.__contains__(claimed, name):
        return None
    try:
        return _stated_count(dict.get(claimed, name), name)
    except ValueError:
        return None


def validate_storage_accounting(claimed):
    if not isinstance(claimed, dict):
        raise ValueError(
            "storage accounting count in named form: the claimed set "
            "stands as a record of counts, and no other form stands "
            "validated")
    expected = (
        _stated_count(dict.get(claimed, "summaries", 0), "summaries")
        + _stated_count(
            dict.get(claimed, "daily_snapshots", 0), "daily_snapshots")
        + _stated_count(dict.get(claimed, "event_logs", 0), "event_logs")
    )
    claimed_result = _claimed_total(claimed, "result_count")
    if claimed_result is None or claimed_result != expected:
        return False
    if dict.__contains__(claimed, "checkpoint_count"):
        expected_stock = (
            _stated_count(dict.get(claimed, "checkpoints", 0), "checkpoints")
            + _stated_count(
                dict.get(claimed, "held_corpus_copies", 0),
                "held_corpus_copies"))
        claimed_stock = _claimed_total(claimed, "checkpoint_count")
        if claimed_stock is None or claimed_stock != expected_stock:
            return False
    return True


def checkpoint_count_c10(rows):
    """The retained checkpoint stock count under clause C10: for
    each row, the retained checkpoints per run multiplied by the
    runs in the row, plus one for each held regression corpus copy
    of a checkpoint in the row, summed over rows. No checkpoint
    byte total stands stated by this count."""
    total = 0
    for row in (list(_base_iter(rows)) if isinstance(rows, (list, tuple, set, frozenset)) else rows):
        if not isinstance(row, dict):
            raise ValueError(
                "checkpoint count in named form: a C10 row stands as a "
                "record, and no other form stands counted")
        if not dict.__contains__(row, "retained_per_run") or not dict.__contains__(row, "runs"):
            raise ValueError(
                "checkpoint count in named form: a C10 row stands "
                "without its retained per run count or its run count, "
                "and no count stands returned for it")
        per_run = _stated_count(dict.__getitem__(row, "retained_per_run"), "retained_per_run")
        if per_run > 10000:
            raise ValueError("checkpoint cap in named form: a C10 row stands over the ruled cap of 10,000 checkpoints per run under ruling Entry 18, and no bare count stands returned for it")
        runs = _stated_count(dict.__getitem__(row, "runs"), "runs")
        present = [
            (key, dict.__getitem__(row, key))
            for key in (
                "held_corpus_copies",
                "regression_corpus_copies",
                "corpus_copies",
                "copies",
            )
            if dict.get(row, key) is not None
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
    for record in (list(_base_iter(prior_records)) if isinstance(prior_records, (list, tuple, set, frozenset)) else prior_records):
        if not isinstance(record, dict):
            continue
        if not dict.__contains__(record, "size") or dict.get(record, "size") is None:
            continue
        artefact_class = dict.get(record, "artefact_class", "unclassified")
        actuals[artefact_class] = (
            actuals.get(artefact_class, 0) + dict.__getitem__(record, "size"))
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
    if not isinstance(claim, dict):
        return False
    if dict.get(claim, "basis") == "DQ7-08" and dict.get(claim, "reliance") == "governing":
        return False
    return True


def write_summary_record(record):
    """Retain the summary record of a run, as written at run close
    or as amended by a deferred evaluation written into it."""
    if not isinstance(record, dict):
        raise ValueError(
            "write_summary_record stands refused: the record stands "
            "in no record form, a summary record stands as a record, "
            "and no summary record stands retained")
    _guard_retention_shape(record, "write_summary_record", "record")
    run_id = dict.get(record, "run_id") or dict.get(
        record, "run_identifier")
    if run_id is None:
        raise ValueError(
            "identity less summary record: no run identifier stands "
            "on the record, and no summary record stands retained "
            "under no identifier")
    try:
        hash(run_id)
    except TypeError as exc:
        raise ValueError(
            "identity less summary record: the run identifier stands "
            "in an unhashable form, and no summary record stands "
            "retained under it") from exc
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
    try:
        hash(run_id)
    except TypeError as exc:
        raise LookupFailure(run_id) from exc
    try:
        summary_present = run_id in _SUMMARY_RECORDS
    except Exception as exc:
        raise LookupFailure(run_id) from exc
    if summary_present:
        return _safe_copy(_SUMMARY_RECORDS[run_id])
    record = None
    try:
        record = _DEFAULT_STORE.read_run_record(run_id)
    except LookupFailure:
        record = None
    except Exception as exc:
        raise LookupFailure(run_id) from exc
    if record is None:
        return {
            "run_id": run_id,
            "form": FORM_ONLY,
            "record_found": False,
            "statement": (
                "no summary record and no run record was found for "
                "run " + _safe_str(run_id)),
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
        "flag_conditions_fired": _safe_copy(
            record.get("flag_conditions_fired")
            or outcome.get("flag_conditions_fired") or []),
        "carriage": "computed from the retained RunRecord",
    }
    if tier is not None:
        computed["retention_tier"] = tier
    for field in ("week", "headline_unit_identifiers"):
        if field in record:
            computed[field] = _safe_copy(record[field])
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


def _two_pairs_beside_one_replacement(word, candidate):
    """Whether a word reads as a candidate word under two
    disjoint transposed pairs beside one replaced letter, a
    change total of three. Such a composition stands as itself
    under the stated composition form, which resolves composed
    transpositions only where the total stands past three, so
    the word does not fall through to a reading of another
    candidate."""
    if len(word) != len(candidate):
        return False
    differing = _differing_positions(word, candidate)
    if len(differing) != 5:
        return False
    pair_options = [
        (first, second)
        for first, second in itertools.combinations(differing, 2)
        if word[first] == candidate[second]
        and word[second] == candidate[first]]
    for chosen in itertools.combinations(pair_options, 2):
        used = [index for pair in chosen for index in pair]
        if len(set(used)) != len(used):
            continue
        rest = [index for index in differing if index not in used]
        if len(rest) == 1:
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
    resolve in the shell form, where one, two, or three
    transpositions stand with one to three remaining letters
    replaced and the total number of changes stands past
    three, so totals of four and of five changes resolve and
    a total of three changes in that composition does not.
    One, two, or three transpositions of letter pairs
    standing anywhere in the word, adjacent or not, also
    resolve, read by pairing the differing positions, and a
    transposed pair in a composition stands counted at any
    positions in the word, where the positions counted as
    replacements carry no transposed pair of their own.
    The dropped, replaced, and transposed limbs run on words
    of two letters as well, so a drop from a three letter word
    still resolves. A word of one letter stands read through
    the drop limbs only where exactly one vocabulary word
    drops to it. Past those forms the resolver also reads added letters composed with replacements or with one transposition, where the differing positions left after the added letters stand struck number at most five and the total of the added count and the remaining changes stands at most seven, a transposed pair among the differing positions counting as one change in place of the two positions it stands on. The resolver also reads one transposed pair standing at any two positions of the word, including the two edge positions, composed with three further replaced letters. Three transpositions beside one replaced letter also resolve, in the same composed form, the total standing past three. A word that stands as itself under the composition forms, in particular a word built from a candidate by two disjoint transposed pairs beside one replaced letter, does not fall through to the mixed added reading of a shorter candidate. Five letters dropped from a vocabulary word also resolve, in the form the MOD-14 resolver states, so a two letter word that stands as a subsequence of a seven letter vocabulary word with five letters dropped resolves to that word at this resolver as it does at the MOD-14 resolver. Any other word stands as itself."""
    if word in _ACTOR_VOCABULARY:
        return word
    if _actor_segments_into_vocabulary(word, _ACTOR_VOCABULARY):
        return word
    vocabulary_lengths = {len(item) for item in _ACTOR_VOCABULARY}
    for added in (1, 2, 3, 4, 5, 6, 7):
        if len(word) > added and (
                len(word) - added) in vocabulary_lengths:
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
        for drops in (2, 3, 4, 5):
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
            remaining_positions = []
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
                    remaining_positions.append(index)
                    position += 1
            if swaps >= 1 and remaining == 0 and swaps <= 3:
                return candidate
            if (1 <= swaps <= 2 and 1 <= remaining <= 3
                    and swaps + remaining > 3
                    and not _carries_transposed_pair(
                        word, candidate, remaining_positions)):
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if not differing or len(differing) > 6:
                continue
            if len(differing) % 2:
                continue

            def pairable(indices):
                if not indices:
                    return True
                first = indices[0]
                for spot in range(1, len(indices)):
                    second = indices[spot]
                    if (word[first] == candidate[second]
                            and word[second] == candidate[first]):
                        rest = indices[1:spot] + indices[spot + 1:]
                        if pairable(rest):
                            return True
                return False

            if pairable(differing):
                return candidate
        for candidate in _ACTOR_VOCABULARY_ORDERED:
            if len(candidate) != len(word):
                continue
            differing = [
                index for index in range(len(word))
                if candidate[index] != word[index]]
            if len(differing) < 4 or len(differing) > 7:
                continue
            pair_options = [
                (first, second)
                for first, second in itertools.combinations(differing, 2)
                if word[first] == candidate[second]
                and word[second] == candidate[first]]
            for swap_count in (1, 2, 3):
                for chosen in itertools.combinations(
                        pair_options, swap_count):
                    used = [
                        index for pair in chosen for index in pair]
                    if len(set(used)) != len(used):
                        continue
                    rest = [
                        index for index in differing
                        if index not in used]
                    if not 1 <= len(rest) <= 3:
                        continue
                    if swap_count + len(rest) <= 3:
                        continue
                    if _carries_transposed_pair(
                            word, candidate, rest):
                        continue
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
            if not any(
                    other != candidate
                    and _two_pairs_beside_one_replacement(word, other)
                    for other in _ACTOR_VOCABULARY_ORDERED):
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


def _actor_stored_text(value, _depth=0):
    """The stored text an actor value carries under the stored
    text settlement: a text form, a bytes form, a bytearray
    form, and a memoryview form each read as the stored text
    they store, and a container form reads as the stored text
    parts it stores joined in order with no separator added,
    each part read recursively on its own stored text. A
    value in any other form, an empty container, and a
    container holding a part in any other form carry no
    stored text here and stand as None."""
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return _stored_text(value)
    if isinstance(value, _CONTAINER_KEY_FORMS) and _depth < 8:
        parts = _container_parts(value)
        if not parts:
            return None
        pieces = []
        for part in parts:
            piece = _actor_stored_text(part, _depth + 1)
            if piece is None:
                return None
            pieces.append(piece)
        return "".join(pieces)
    return None


def _normalised_actor(actor, _depth=0):
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
    word they split. An actor value that is stored text in
    bytes, bytearray, memoryview, or container dress stands
    read as that stored text here, under the container
    readings of the settlement: each part on its own stored
    text, the parts joined in order as one name, and a single
    part container carrying the reading of its one part. An
    actor value in any other non text form stands as itself,
    passed through untouched."""
    if isinstance(actor, _CONTAINER_KEY_FORMS):
        parts = _container_parts(actor)
        if _depth >= 8 or not parts:
            return actor
        joined_text = _actor_stored_text(actor)
        if joined_text is None:
            return actor
        joined_reading = _normalised_actor(joined_text, _depth + 1)
        if joined_reading in _ACTOR_VOCABULARY:
            return joined_reading
        for part in parts:
            part_reading = _normalised_actor(part, _depth + 1)
            if isinstance(part_reading, str) and (
                    part_reading in _ACTOR_VOCABULARY):
                return part_reading
        return actor
    if isinstance(actor, (bytes, bytearray, memoryview)):
        actor = _stored_text(actor)
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


def _text_states_condition(text):
    """Whether a text carries readable text past the blank
    classes the flag condition reading states: zero width and
    invisible format characters, blank glyphs, Hangul filler
    characters, and characters of the stated blank categories
    carry no readable text, and spacing alone carries none."""
    readable = "".join(
        char for char in text
        if char not in _ZERO_WIDTH_CHARS
        and char not in _BLANK_GLYPHS
        and char not in _HANGUL_FILLER_CHARS
        and unicodedata.category(char)
        not in ("Cf", "Mn", "Cc", "Mc", "Me", "Cs", "Cn", "Co"))
    return bool(readable.strip())


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
    kinds states no condition either. A lone surrogate, an
    unassigned code point, and a private use character carry
    no readable text in the same manner, so an entry holding
    only characters of those kinds states no condition
    either. A text entry stands read by its stored characters,
    through the stored text reading, never through an iteration
    reading the entry itself supplies. A bytes, bytearray, or
    memoryview entry stands judged on its decoded stored text
    in the same manner: where its stored bytes decode as UTF-8
    text, that decoded text stands judged as a string entry,
    so a blank bytes form states no condition, and where its
    stored bytes do not decode, the entry states a condition
    where it carries any byte past spacing, as MOD-07 judges
    those forms. A fired value in iterator form states no
    condition: it stores no entry in any form this reading
    names, and it never stands as its own stated entry."""
    if isinstance(fired, str):
        entries = [fired]
    elif isinstance(fired, (list, tuple, set, frozenset)):
        entries = list(_base_iter(fired))
    elif fired is None:
        entries = []
    elif _is_iterator(fired):
        entries = []
    else:
        entries = [fired]
    for entry in entries:
        if isinstance(entry, str):
            if _text_states_condition(_stored_text(entry)):
                return True
        elif isinstance(entry, (bytes, bytearray, memoryview)):
            raw = bytes(entry)
            if not bytes.strip(raw):
                continue
            try:
                decoded = bytes.decode(raw, "utf-8")
            except UnicodeDecodeError:
                return True
            if _text_states_condition(decoded):
                return True
        elif entry is not None:
            return True
    return False


def _is_iterator(value):
    """Whether a value stands in iterator form: it is its own
    iterator, carrying its items only as values it would
    yield, and storing no contents in any container, text,
    bytes, or dict form."""
    try:
        return iter(value) is value
    except TypeError:
        return False


def _stored_stands(value):
    """Whether a stored value stands present, judged by its
    stored contents and never by a truth reading the value
    itself supplies: a container form stands where it stores
    at least one entry, read through the base iteration of
    its form, a text form stands where it stores at least one
    character, a bytes family form stands where it stores at
    least one byte, a dict form stands where it stores at
    least one entry, and no value stands nowhere. A value in
    no such form stands judged by the plain truth of the
    value itself."""
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, frozenset)):
        return len(list(_base_iter(value))) > 0
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, (bytes, bytearray, memoryview)):
        return len(bytes(value)) > 0
    if isinstance(value, dict):
        return dict.__len__(value) > 0
    return bool(value)


def _fired_stands(fired):
    """Whether a fired value stands supplied, judged by its
    stored contents and never by a truth reading the value
    itself supplies: a value in a container form stands where
    it stores at least one entry, read through the base
    iteration of its form, a text or bytes form stands where
    it stores at least one character or byte, and no value
    stands nowhere. A value in iterator form stores nothing
    in any of those forms, so it stands as no supplied fired
    value. A value in no such form stands judged by the
    plain truth of the value itself, the one limb this
    reading does not reach."""
    if fired is None:
        return False
    if _is_iterator(fired):
        return False
    if isinstance(fired, (list, tuple, set, frozenset)):
        return len(list(_base_iter(fired))) > 0
    if isinstance(fired, str):
        return len(str.__str__(fired)) > 0
    if isinstance(fired, (bytes, bytearray, memoryview)):
        return len(bytes(fired)) > 0
    if isinstance(fired, dict):
        return dict.__len__(fired) > 0
    return bool(fired)


def apply_flag_evaluation(record, outcome=None, tier=None, actor="program", inputs=None):
    if not isinstance(record, dict):
        raise ValueError(
            "flag evaluation in named form: the evaluation stands on a "
            "summary record, and no other form stands evaluated")
    _guard_retention_shape(
        record, "apply_flag_evaluation", "record",
        consequence="and no flag evaluation stands performed")
    actor = _normalised_actor(actor)
    if isinstance(actor, str) and _stored_text(actor) == "person":
        raise ValueError(
            "flag evaluation by a person is barred: the flag rule "
            "stands evaluated by a program alone, and no flag "
            "evaluation stands performed")
    outcome_text = (
        _stored_text(outcome) if isinstance(
            outcome, (str, bytes, bytearray, memoryview)) else None)
    if outcome is not None and outcome_text not in _FLAG_OUTCOMES:
        raise ValueError(
            "flag evaluation outcome outside the stated vocabulary: "
            + _safe_str(outcome)
            + "; the outcomes the rule names stand as promote and "
            "demote, and no flag evaluation stands performed")
    if outcome_text == "demote":
        raise ValueError(
            "the flag rule never demotes: the stated outcome "
            "stands as demote, and no demotion stands effected "
            "by it")
    tier_text = (
        _stored_text(tier) if isinstance(
            tier, (str, bytes, bytearray, memoryview)) else None)
    if tier is not None and tier_text not in _TIER_RANKS:
        raise ValueError(
            "flag evaluation tier outside the tiers the rule names: "
            + _vocabulary_text(tier) + "; the tiers the rule names stand as "
            "Tier 0, Tier 1, Tier 2, and Tier 3, and no flag "
            "evaluation stands performed")
    current = dict.get(record, "retention_tier")
    current_text = (
        _stored_text(current) if isinstance(
            current, (str, bytes, bytearray, memoryview)) else None)
    if (tier is not None and current_text in _TIER_RANKS
            and _TIER_RANKS[tier_text] < _TIER_RANKS[current_text]):
        raise ValueError(
            "the flag rule never demotes: the stated tier stands below "
            "the record tier, and no demotion stands effected by it")
    if outcome_text == "promote":
        if inputs is None:
            raise ValueError(
                "flag promotion with no inputs supplied: a promotion "
                "stands only with inputs actually supplied, and no "
                "promotion stands effected by it")
        if inputs is not None and not isinstance(inputs, dict):
            raise ValueError(
                "flag promotion with its inputs standing in no "
                "record form: a promotion stands only with its "
                "inputs handed as a mapping carrying "
                "flag_conditions_fired, and no promotion stands "
                "effected by it")
        fired = None
        if isinstance(inputs, dict):
            fired = dict.get(inputs, "flag_conditions_fired")
        if not _fired_stands(fired):
            fired = dict.get(record, "flag_conditions_fired")
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
        if current_text in _TIER_RANKS and _TIER_RANKS[tier_text] <= _TIER_RANKS[current_text]:
            raise ValueError(
                "a promote outcome with no effected promotion stands "
                "refused: the stated tier " + _vocabulary_text(tier)
                + " does not rise above the standing tier "
                + _vocabulary_text(current)
                + ", a promotion must rise above the standing tier, "
                "and no promotion stands effected by it")
    updated = _safe_copy(record)
    if outcome_text == "promote" and tier is not None:
        updated["retention_tier"] = tier_text
    updated["flag_evaluation"] = {
        "inputs": _safe_copy(inputs),
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
    return _safe_copy(hold)


def reserve_hold_for_run(run_id, current_day=None):
    """Read the reserve hold standing on a run. A hold read at or
    past its ruled maximum end of 30 days under ruling Entries 17
    and 18 stands expired by that stated act, for every family
    form including a family that never states headline results,
    and never reads held without an end."""
    try:
        hash(run_id)
    except TypeError as exc:
        raise LookupFailure(run_id) from exc
    hold = _RESERVE_HOLDS.get(run_id)
    if hold is None:
        return None
    if current_day is not None and hold.get("state") == "held" and current_day >= hold.get("end_day", 0):
        hold["state"] = "expired"
    if hold.get("state") == "released":
        return None
    return _safe_copy(hold)


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
        raise ValueError(
            "apply_deferred_evaluation stands refused: the firing "
            + _safe_repr(firing) + " stands outside the stated firings "
            "1 and 2, a run receives two firings (firings 1 and 2) "
            "and no other firing, and no evaluation stands written")
    updated = _safe_copy(summary_record)
    evaluations = updated.setdefault("deferred_evaluations", [])
    if any(item.get("firing") == firing for item in evaluations):
        raise ValueError(
            "apply_deferred_evaluation stands refused: this firing "
            "already stands written, a run receives two firings "
            "(firings 1 and 2) and no firing stands written twice, "
            "and no evaluation stands written")
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
        if run_key is not None:
            try:
                hash(run_key)
            except TypeError as exc:
                raise ValueError(
                    "identity less summary record: the run "
                    "identifier stands in an unhashable form, and "
                    "no summary record stands retained under "
                    "it") from exc
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
            evaluations.extend(_safe_copy(stored_evaluations))
    evaluations.append({
        "firing": firing,
        "inputs": _safe_copy(inputs),
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
    try:
        hash(run_id)
    except TypeError as exc:
        raise LookupFailure(run_id) from exc
    summary = summary_record_for_run(run_id)
    evaluations = summary.get("deferred_evaluations") or []
    later = evaluations[-1] if evaluations else None
    tier = summary.get("retention_tier")
    tier_key = (
        _stored_text(tier) if isinstance(
            tier, (str, bytes, bytearray, memoryview)) else tier)
    tier_map = {
        "Tier 0": [],
        "Tier 1": ["final_checkpoint"],
        "Tier 2": ["final_checkpoint", "tenth_point_checkpoints"],
        "Tier 3": ["final_checkpoint", "daily_checkpoints"],
    }
    try:
        tier_judged = tier_key in tier_map
        tier_forms = tier_map.get(tier_key, [])
    except TypeError:
        tier_judged = False
        tier_forms = []
    retained_checkpoints = checkpoints_for_run(run_id, store_kind)
    pointer_counts = {
        "checkpoints": len(retained_checkpoints),
        "event_log_entries": len(event_log_entries(run_id, store_kind)),
        "daily_snapshots": len(daily_snapshots(run_id, store_kind)),
    }
    retained_forms = []
    if pointer_counts["checkpoints"]:
        retained_forms.append("final_checkpoint")
    if "tenth_point_checkpoints" in tier_forms and any(
            _day_match_form(dict.get(checkpoint, "simulated_day"))[0]
            == "int"
            and _day_match_form(
                dict.get(checkpoint, "simulated_day"))[1] % 10 == 0
            for checkpoint in retained_checkpoints
            if isinstance(checkpoint, dict)):
        retained_forms.append("tenth_point_checkpoints")
    if "daily_checkpoints" in tier_forms and (
            pointer_counts["checkpoints"] >= 2
            or pointer_counts["daily_snapshots"]):
        retained_forms.append("daily_checkpoints")
    if pointer_counts["event_log_entries"]:
        retained_forms.append("event_log")
    if pointer_counts["daily_snapshots"]:
        retained_forms.append("daily_snapshots")
    not_retained = [
        form + ": not retained"
        for form in tier_forms if form not in retained_forms
    ]
    if tier_judged:
        shortfall_bound = (
            "shortfall stands stated inside this result as a bound: "
            + str(len(not_retained)) + " of " + str(len(tier_forms))
            + " forms the tier names stand not retained")
    else:
        shortfall_bound = (
            "shortfall stands not judged inside this result: no tier "
            "forms stand named for the tier the run states, the tier "
            "standing unstated or unknown, and no shortfall stands "
            "stated against it")
    result = {
        "run_id": run_id,
        "retention_tier": tier_key,
        "tier_forms": list(tier_forms),
        "retained_forms": retained_forms,
        "not_retained": not_retained,
        "shortfall_judged": tier_judged,
        "shortfall": {
            "count": len(not_retained),
            "judged": tier_judged,
            "bound": shortfall_bound,
        },
        "later_evaluation": _safe_copy(later),
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
    if not isinstance(report, dict):
        return False
    if dict.get(report, "source") == "interval_records" and dict.get(report, "tier_claim") == "final":
        return False
    return True


def append_annotation(checkpoint, annotation=None):
    if not isinstance(checkpoint, dict):
        raise ValueError(
            "identity less checkpoint: an annotation stands on a "
            "checkpoint record, and no other form stands annotated")
    updated = _safe_copy(checkpoint)
    updated["annotation_record"] = _safe_copy(annotation) if annotation is not None else {}
    return updated


def annotation_link_at_checkpoint(checkpoint):
    """Return the annotation link identifier at a checkpoint, under
    the plan named field annotation_link_identifier where it
    stands, and under the Form 4 carriage name annotation_link
    where that is the name the checkpoint carries."""
    if not isinstance(checkpoint, dict):
        return None
    identifier = dict.get(checkpoint, "annotation_link_identifier")
    if _stored_stands(identifier):
        return identifier
    return dict.get(checkpoint, "annotation_link")


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
    never through a reading the handed kind supplies. The handed
    checkpoint itself stands read through base class dict
    operations, so its run identifier, its store kind, its day,
    and the form compared against the retained checkpoint all
    stand taken from its stored contents, never through a get
    or items reading the handed checkpoint supplies. The final
    comparison stands judged through _base_value_eq, the base
    reading equality on stored contents, at every level of the
    compared forms, never through plain dict equality running
    equality readings the handed values supply. The day stands
    matched under its day match form, so a float day and a bool
    day never stand as the integer day they happen to equal in
    number: where a retained checkpoint stands for the run
    under that loose number reading and the handed day stands
    in a float or bool form, the resume stands refused in the
    checkpoint integrity refusal form. Where the handed
    checkpoint matches a retained checkpoint, the resumed form
    stands returned as a copy of the retained checkpoint, in
    the retained day form, carrying a field the retained
    checkpoint carries beside the compared form only where the
    handed checkpoint carried that field as well."""
    if not isinstance(checkpoint, dict):
        raise ValueError(
            "identity less checkpoint: a resume stands on a checkpoint "
            "record, and no other form stands resumed")
    run_id = dict.get(checkpoint, "run_identifier") or dict.get(
        checkpoint, "run_id")
    if run_id is None:
        raise ValueError(
            "identity less checkpoint: no run identifier stands on the "
            "checkpoint, and no resume stands performed")
    kind = store_kind or dict.get(checkpoint, "store_kind")
    if kind is not None:
        kind = _canonical_store_kind(kind)
    handed_form = {
        key: value for key, value in dict.items(checkpoint)
        if key not in ("journal_event_count_at_checkpoint", "store_kind")
    }
    candidates = []
    for (bucket_kind, bucket_run), bucket in _CHECKPOINTS.items():
        if bucket_run != run_id:
            continue
        if kind is not None and bucket_kind != kind:
            continue
        for retained in bucket:
            if _same_day_form(
                    dict.get(retained, "simulated_day"),
                    dict.get(checkpoint, "simulated_day")):
                candidates.append(retained)
    if not candidates:
        handed_day = dict.get(checkpoint, "simulated_day")
        if isinstance(handed_day, (bool, float)):
            for (bucket_kind, bucket_run), bucket in _CHECKPOINTS.items():
                if bucket_run != run_id:
                    continue
                if kind is not None and bucket_kind != kind:
                    continue
                for retained in bucket:
                    if _whole_day(
                            dict.get(retained, "simulated_day")) == _whole_day(
                            handed_day):
                        raise ValueError(
                            "checkpoint integrity refusal: the handed "
                            "checkpoint states its day in a form no "
                            "surface states as that day, and no resume "
                            "stands performed from it")
        if kind is not None:
            raise ValueError(
                "checkpoint integrity refusal: the handed "
                "checkpoint names a store kind holding no "
                "retained checkpoint for its run and day, and "
                "no resume stands performed from it")
        return _safe_copy(checkpoint)

    def _comparison_form(form):
        compared = dict(form)
        if "simulated_day" in compared:
            compared["simulated_day"] = _comparison_day(
                compared["simulated_day"])
        return compared

    handed_compared = _comparison_form(handed_form)
    for retained in candidates:
        retained_form = {
            key: value for key, value in dict.items(retained)
            if key not in ("journal_event_count_at_checkpoint", "store_kind")
        }
        if _base_value_eq(
                _comparison_form(retained_form), handed_compared):
            resumed = _safe_copy(retained)
            for field in (
                    "journal_event_count_at_checkpoint", "store_kind"):
                if field not in dict.__iter__(checkpoint):
                    resumed.pop(field, None)
            return resumed
    raise ValueError(
        "checkpoint integrity refusal: the handed "
        "checkpoint differs from the retained checkpoint "
        "for its run and day, and no resume stands "
        "performed from it")


def validate_annotation_claim(claim):
    if not isinstance(claim, dict):
        return False
    if dict.get(claim, "claim") == "annotation_state_equal_across_append":
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
    if not isinstance(sizing, dict):
        return False
    workings = dict.get(sizing, "workings") or {}
    if not isinstance(workings, dict):
        return False
    if not dict.__contains__(workings, "central_form") or not dict.__contains__(workings, "high_form"):
        return False
    high = dict.get(workings, "high_form") or {}
    if not isinstance(high, dict):
        return False
    if dict.get(high, "events_per_agent_per_day") is None:
        return False
    wording = dict.get(sizing, "wording") or {}
    if not isinstance(wording, dict):
        return False
    for value in dict.values(wording):
        if value in ("forecast", "ceiling"):
            return False
    return True


def retention_met(record):
    if not isinstance(record, dict):
        return False
    if _stored_stands(dict.get(record, "declaration_only")) or _stored_text(dict.get(record, "state")) == "DECLARED NOT CLOSED":
        return False
    later = dict.get(record, "later_evaluation")
    if not isinstance(later, dict):
        return False
    conditions = dict.get(later, "conditions")
    if conditions is None:
        conditions = []
    if isinstance(conditions, (list, tuple, set, frozenset)):
        conditions = list(_base_iter(conditions))
    elif isinstance(conditions, dict):
        conditions = list(dict.__iter__(conditions))
    elif isinstance(conditions, str):
        conditions = list(str.__iter__(conditions))
    elif isinstance(conditions, (bytes, bytearray, memoryview)):
        conditions = list(bytes(conditions))
    else:
        conditions = []
    if not _base_value_eq(conditions, [1, 2, 3]):
        return False
    if not _stored_stands(dict.get(later, "inputs")) or not _stored_stands(dict.get(later, "outcome")):
        return False
    if not _stored_stands(dict.get(record, "summary_record_written")):
        return False
    if not _stored_stands(dict.get(record, "retained_forms_pointed_to")):
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
    if not isinstance(sample, dict):
        return False
    if dict.get(sample, "presented_as") == "generator_test_battery_sample":
        return False
    if dict.get(sample, "kind") == "retention_sample":
        if not dict.get(sample, "in_family_record"):
            return False
        if dict.get(sample, "registration_standing") != "before_runs":
            return False
    return True


def validate_retention_record(record):
    if not isinstance(record, dict):
        return False
    governing = _safe_str(dict.get(record, "governing_rule") or "")
    if governing.startswith("DQ7-08") and dict.get(record, "reliance") == "governing":
        return False
    return True


def store_indexes():
    return {kind: _STORES[kind].index() for kind in STORE_KINDS}


def validate_store_placement(artefact):
    if not isinstance(artefact, dict):
        return False
    if dict.get(artefact, "kind") == "pilot":
        if dict.get(artefact, "store") != "pilot":
            return False
        if dict.__contains__(artefact, "value") and not dict.get(artefact, "confinement_label"):
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
        raise ValueError(
            "a lookup that resolves across stores in one step is "
            "rejected: exactly one store kind stands required, and "
            "no record lookup stands performed")
    kind = tuple(kinds)[0]
    if not _store_kind_stands(kind):
        raise ValueError(
            "unknown store kind: " + _safe_str(kind) + "; a store kind stands "
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
    if dict.get(carriage, "form") == "singular_vector":
        return False
    if dict.get(carriage, "presented_as") == "one comparable quantity":
        return False
    if dict.get(carriage, "form") == "flip_trial_record" and dict.get(carriage, "cited_as") == "run_result":
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
                return _safe_copy(record[field])
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
    many ambiguous positions it carries. Each character stands
    taken from the stored characters of the key through the
    base class string form, in the form _stored_text states,
    never from a string reading the handed key supplies."""
    segments_by_character = []
    for character in _stored_text(key).casefold():
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
    part. A key in container dress stands judged as at
    _is_barred_view_key, by its parts and by its joined
    stored text."""
    if isinstance(key, _CONTAINER_KEY_FORMS):
        return _is_barred_view_key(key)
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
    the standing surfaces. A key in container dress stands
    barred where a part it stores stands barred, judged on the
    stored parts through their base readings at any depth, or
    where the stored text parts joined in order, with no
    separator added, spell a barred name, in the MOD-04 barred
    key form, and a single part container carries the reading
    of its one part. A bytes part inside a container key stands
    read on its decoded stored bytes, as a bare bytes key
    stands read. A dict stands judged at its own node beside
    its parts and its whole joined text: a barred exact name
    split across two or more consecutive keys of the dict, in
    stored order, stands barred on the tiling of those keys
    folded readings, so the exact form names stand judged at
    a node carrying further keys beside the split, in the
    joined reading form settlement S-14 states."""
    if isinstance(key, _CONTAINER_KEY_FORMS + (dict,)):
        stack = [key]
        seen = set()
        containers = []
        while stack:
            part = stack.pop()
            if isinstance(part, _CONTAINER_KEY_FORMS + (dict,)):
                if id(part) in seen:
                    continue
                seen.add(id(part))
                parts = (
                    list(dict.keys(part)) if isinstance(part, dict)
                    else _container_parts(part))
                containers.append((part, len(parts)))
                stack.extend(parts)
            elif _is_barred_view_key(part):
                return True
        joined_standings = {}
        for container, part_count in containers:
            if part_count == 1:
                continue
            joined = _joined_stored_text(container)
            if not joined:
                continue
            if joined not in joined_standings:
                joined_standings[joined] = _is_barred_view_key(joined)
            if joined_standings[joined]:
                return True
        if _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and _is_barred_view_key(candidate):
                    return True
        if _seg_unordered_barred(key):
            return True
        if _seg_spanning_barred(
                key, tuple(_VIEW_BARRED_KEYS),
                tuple(_VIEW_BARRED_KEY_PARTS),
                tuple(_VIEW_BARRED_KEYS_FOLDED),
                tuple(_VIEW_BARRED_KEY_PARTS_FOLDED)):
            return True
        if isinstance(key, dict):
            pairs = list(dict.items(key))
            if len(pairs) >= 2:
                readings = []
                for node_key, node_value in pairs:
                    options = set(_fold_variants(node_key))
                    if isinstance(node_key, _CONTAINER_KEY_FORMS
                                  + (dict,)):
                        options.update(_fold_variants(
                            _joined_stored_text(node_key)))
                    readings.append(options)
                for target in _VIEW_BARRED_KEYS_FOLDED:
                    if _dict_keys_tile_exact(
                            readings, pairs, target, False):
                        return True
        joined = _joined_stored_text(key)
        if joined:
            return _is_barred_view_key(joined)
        return False
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
            if _is_barred_view_key(node) and not any(
                    _is_barred_view_key(key)
                    for key in dict.keys(node)):
                return True
            for key, item in dict.items(node):
                if _is_barred_view_key(key):
                    return True
                stack.append(key)
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
    check. The record stands read through the base class dict
    readings, on the values it stores, never through a get
    reading the handed record itself supplies, at the view name,
    the group list, the barred carriage test, the field
    validation, and the timing reading alike. The timing form
    reads the first seen day per record only in mapping form: a
    record carrying that field in a non mapping form stands
    refused in the named timing failure form, naming the view,
    the field, and the check form, and no bare error escapes."""
    if not isinstance(view_record, dict):
        raise ValueError(
            "view leak check failure: form field_validation, the "
            "record stands as no ViewRecord")
    view_name = (
        _safe_str(dict.get(view_record, "run_identifier")
            or dict.get(view_record, "run_id"))
        + "/" + _safe_str(dict.get(view_record, "viewer_identifier")
                    or dict.get(view_record, "viewer_id")))
    groups = [
        name for name in (
            "view_contents", "reputation_and_band_values",
            "graph_position_as_seen")
        if dict.__contains__(view_record, name)
    ]
    groups.extend(
        name for name in dict.keys(view_record) if name not in groups)
    if _is_barred_view_key(view_record) and not any(
            _is_barred_view_key(key)
            for key in dict.keys(view_record)):
        raise ValueError(
            "view leak check failure: form canary, view "
            + view_name + ", field "
            + _joined_stored_text(view_record)
            + " carries a barred key")
    for field in groups:
        if _is_barred_view_key(field) or _carries_barred_key(
                dict.get(view_record, field)):
            raise ValueError(
                "view leak check failure: form canary, view "
                + view_name + ", field " + str(field)
                + " carries a barred key")
    for field in mod01.ViewRecord.FIELDS:
        if field in ("scheduling_position_identifier",
                     "rule_version_set") and dict.__contains__(
                         view_record, field):
            continue
        if dict.get(view_record, field) is None:
            raise ValueError(
                "view leak check failure: form field_validation, view "
                + view_name + ", field " + field + " stands absent")
    day = _timing_day(dict.get(view_record, "simulated_day"))
    first_seen = dict.get(view_record, "first_seen_day_per_record")
    if first_seen is None:
        first_seen = {}
    if not isinstance(first_seen, dict):
        raise ValueError(
            "view leak check failure: form timing, view "
            + view_name + ", field first_seen_day_per_record: "
            "the first seen day per record stands in a non mapping "
            "form the timing form cannot read")
    for item, seen_day in dict.items(first_seen):
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
    Tier 2 and Tier 3 the full record stands retained. The record
    stands read through the base class dict readings, on the
    values it stores, never through a get reading the handed
    record itself supplies."""
    if not isinstance(record, dict):
        raise ValueError(
            "identity less view record: a ViewRecord stands as a "
            "record carrying a run identifier, and no other form "
            "stands retained")
    run_id = dict.get(record, "run_identifier") or dict.get(
        record, "run_id")
    if run_id is None:
        raise ValueError(
            "identity less view record: no run identifier stands on "
            "the record, and no view record stands retained under "
            "no identifier")
    run_view_leak_check(record)
    tier = tier or dict.get(record, "retention_tier") or "Tier 2"
    if tier == "Tier 1":
        stored = {
            "run_identifier": run_id,
            "viewer_identifier": (
                dict.get(record, "viewer_identifier")
                or dict.get(record, "viewer_id")),
            "simulated_day": dict.get(record, "simulated_day"),
            "retention_tier": "Tier 1",
            "divergence_companion": _safe_copy(
                dict.get(record, "divergence_companion")
                or {"nil_divergence_components": []}),
            "form": "divergence companion in place of the full view record",
        }
    else:
        stored = _safe_copy(record)
        stored["retention_tier"] = tier
    _VIEW_RECORDS.setdefault(run_id, []).append(stored)
    return _safe_copy(stored)


def view_records_for_run(run_id):
    """Read the retained ViewRecords of a run. Reading never
    writes."""
    try:
        hash(run_id)
    except TypeError as exc:
        raise LookupFailure(run_id) from exc
    return _safe_copy(_VIEW_RECORDS.get(run_id, []))

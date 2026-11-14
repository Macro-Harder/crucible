"""MOD-12 Sweep Controller and family definition.

Slice S-12. This module owns the sweep family definition fixed
before any sweep runs, the screening, confirmation, headline, and
validation run classes, the replicate plan, and the point at
which a readout may be called established under the stopping
rule. Executable runs wait on the DQ7-02 gate at slice S-02: a
start that would need a derived seed returns the recorded gated
refusal of MOD-02, DERIVATION-GATED naming DQ7-02, and starts
nothing. Grid values stand provisional until the NQ-4 timing
pilot lands, and that pilot stands prepared and not landed, so
no grid artefact in this module is presented as affordable and
no sweep run starts here.
"""

import itertools
import unicodedata

from crucible import mod01 as _mod01
from crucible import mod02 as _mod02
from crucible import mod10 as _mod10

RUN_CLASSES = ("screening", "confirmation", "headline", "validation")
GATE_QUESTION = "DQ7-02"

FAMILY_COMPLETENESS_ITEMS = tuple(_mod01.COMPLETENESS_FIELDS)

_MONEY_MARKER = "real_" + "money"
_ANCHOR_VALUES_FIELD = "anchor_" + "scenario_values"


class NamedControllerFailure(Exception):
    """A failure stated by name, never a silent correction."""


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


# ---------------------------------------------------------------------------
# Family definition, seal, and claims
# ---------------------------------------------------------------------------

def make_family_record(family_id="family-under-test", claims=None,
                       scheduling_order_identifier=None):
    """One family record in the Shape 1 form MOD-01 states as
    Form 1: every field of that form stands on the record, under
    the form field names, beside the controller carriage keys.
    The completeness items the seal path checks stand on the
    record by name. The record stands unsealed until
    seal_family_record seals it."""
    claims = list(claims or ("headline claim 1",))
    record = _mod01.minimal_valid_family_record()
    record["family_identifier"] = family_id
    record["headline_claims"] = claims
    record["kill_check_fields"] = [
        kill_check_for_claim(claim) for claim in claims]
    if scheduling_order_identifier is not None:
        record["scheduling_order_identifier"] = scheduling_order_identifier
    # The six completeness fields stand on the record as the MOD-01
    # builder carries them, in open marker form. No stated value
    # stands written here for the OP-20 replication quantities,
    # which the plan carries as unfixed.
    record["family_version"] = "version 1"
    record["family_manifest_hash"] = (
        "manifest hash supplied as a record value, not computed")
    record.update({
        "family_id": family_id,
        "sealed": False,
        "claims": claims,
        "kill_checks": record["kill_check_fields"],
        "registry_basis_fields": registry_basis_fields(),
        "results_seen": False,
        "form": "family record",
    })
    return record


def sweep_manifest(record):
    """The sweep manifest of one family record, in the Form 23
    fields: the family identifier, the family version, and the
    sealed family record hash, each as the record carries it."""
    record = record or {}
    seal = record.get("seal") if isinstance(record.get("seal"), dict) else {}
    return {
        "family_identifier": record.get(
            "family_identifier", record.get("family_id")),
        "family_version": record.get("family_version"),
        "sealed_family_record_hash": (
            record.get("family_manifest_hash")
            or record.get("seal_hash")
            or seal.get("hash")),
    }


def retained_run_record(run_id, store_kind="sweep"):
    """One run record read through MOD-10, the Recorder store
    reading path the plan boundary row for this controller states.
    A record that does not resolve stands raised as the MOD-10
    named lookup failure, and no record is fabricated here."""
    return _mod10.read_run_record(run_id, store_kind=store_kind)


def seal_family_record(record):
    """Seal one family record. The completeness condition stands
    performed before the seal: a record missing any one of the
    completeness items this controller names is refused in the
    named form and does not seal. The seal carries the version
    value and the hash value as recorded strings supplied on the
    record; no hash form is computed in this act. A sweep
    manifest stands produced beside the seal. From the seal, any
    edit creates a new family identifier and runs under it start
    again. The record stands under the same depth bound and
    cycle guard as the sister record acts of this module,
    checked before the copy: a shape past the bound or carrying
    a cycle stands refused in the named form, never as a bare
    RecursionError."""
    missing = [
        item for item in FAMILY_COMPLETENESS_ITEMS
        if not isinstance(record, dict) or not record.get(item)
    ]
    if missing:
        raise NamedControllerFailure(
            "family record cannot seal, completeness items missing: "
            + ", ".join(missing))
    if _shape_exceeds_bounds(record):
        raise NamedControllerFailure(
            "family record cannot seal: the record stands "
            "deeper than the stated bound of "
            + str(_MAX_BARRED_READ_DEPTH)
            + " or carries a cycle")
    sealed = _freeze(record)
    sealed["sealed"] = True
    sealed["seal"] = {
        "version": record.get("family_version") or "version 1",
        "hash": record.get("family_manifest_hash") or (
            "manifest hash supplied as a record value, not computed"),
    }
    sealed["seal_version"] = sealed["seal"]["version"]
    sealed["seal_hash"] = sealed["seal"]["hash"]
    sealed["sweep_manifest"] = sweep_manifest(sealed)
    return sealed


def apply_family_edit(record, change=None):
    """Apply an edit to a family record. An edit to a sealed record
    creates a new family identifier, and runs under the new
    identifier start again, per Shape 1 and operation C-10. An
    edit to an unsealed record lands in place. The record and the
    change stand under the same depth bound and cycle guard as
    validate_run_record: a shape past the bound or carrying a
    cycle is refused in the named form, never as a bare
    RecursionError. A claims list handed in as an empty list
    stands read as an empty list, never as absent, and an edit
    whose kill check fields name a claim that no longer stands
    is refused in the named form. A claims value that does not
    stand in list or tuple form is refused in the named form,
    never read character by character or part by part."""
    if _shape_exceeds_bounds(record) or (
            change is not None and _shape_exceeds_bounds(change)):
        raise NamedControllerFailure(
            "family edit refused: the record or the change stands "
            "deeper than the stated bound of "
            + str(_MAX_BARRED_READ_DEPTH)
            + " or carries a cycle")
    edited = _freeze(record)
    if isinstance(change, dict):
        edited.update(_freeze(change))
    explicit_checks = []
    if isinstance(change, dict):
        for field in ("kill_check_fields", "kill_checks"):
            supplied = change.get(field)
            if isinstance(supplied, (list, tuple)):
                explicit_checks.extend(supplied)
    if isinstance(change, dict) and (
            "headline_claims" in change or "claims" in change):
        raw = change.get("headline_claims") if (
            "headline_claims" in change) else change.get("claims")
    else:
        raw = edited.get("headline_claims") if (
            "headline_claims" in edited) else edited.get("claims")
    if raw is not None:
        if not isinstance(raw, (list, tuple)):
            raise NamedControllerFailure(
                "family edit refused: a claims value handed in "
                "does not stand in list or tuple form: "
                + repr(raw))
        standing = list(raw)
        edited["headline_claims"] = standing
        edited["claims"] = standing
        checks = [kill_check_for_claim(claim) for claim in standing]
        edited["kill_check_fields"] = checks
        edited["kill_checks"] = checks
        for check in explicit_checks:
            if isinstance(check, dict) and check.get("claim") is not None \
                    and check.get("claim") not in standing:
                raise NamedControllerFailure(
                    "family edit refused: a kill check field names "
                    "a claim that no longer stands: "
                    + str(check.get("claim")))
    elif explicit_checks:
        standing_now = edited.get("headline_claims")
        if not isinstance(standing_now, (list, tuple)):
            standing_now = edited.get("claims")
        if isinstance(standing_now, (list, tuple)):
            for check in explicit_checks:
                if isinstance(check, dict) \
                        and check.get("claim") is not None \
                        and check.get("claim") not in standing_now:
                    raise NamedControllerFailure(
                        "family edit refused: a kill check field "
                        "names a claim that no longer stands: "
                        + str(check.get("claim")))
    if record.get("sealed"):
        base_id = record.get("family_identifier") or record.get("family_id")
        new_id = str(base_id) + "-edited-1"
        edited["family_id"] = new_id
        edited["family_identifier"] = new_id
        edited["runs_under"] = new_id
        edited["edited_after_seal"] = True
        edited["identifier_changed"] = True
        edited["runs_start_again"] = True
        edited["sealed"] = False
        for carried in ("seal", "seal_version", "seal_hash",
                        "sweep_manifest"):
            edited.pop(carried, None)
    else:
        edited["runs_under"] = edited.get("family_id")
    return edited


def family_record_validation_failures(record):
    """The named validation failures of one family record, field
    by field: every missing Form 1 field, every missing
    completeness field of the MOD-01 bar, and every missing
    completeness item this controller names, each named in the
    returned list. An empty list stands for a record carrying
    every named field."""
    if not isinstance(record, dict):
        return ["family record is not a record"]
    failures = []
    for field in _mod01.form_fields("1"):
        if field not in record or record.get(field) is None:
            failures.append("missing field: " + field)
    for field in _mod01.COMPLETENESS_FIELDS:
        if field not in record:
            failures.append("missing completeness field: " + field)
    for item in FAMILY_COMPLETENESS_ITEMS:
        if not record.get(item):
            failures.append("missing completeness item: " + item)
    return failures


def validate_family_record(record):
    """Return True only where a family record stands in a lawful
    form: the record stands in the Shape 1 form the reporter
    path checks through MOD-01, it carries every completeness
    field and completeness item by name, and it stands under the
    controller bars: no identifier reuse across a sealed edit, no
    ecology point fixed before its amendment stands, and no data
    dependent top up resting on an empty look register. An empty
    record and a record the type layer rejects both fail here,
    so the controller path and the reporter path agree."""
    if not isinstance(record, dict):
        return False
    if family_record_validation_failures(record):
        return False
    if not _mod01.validate_record("1", record):
        return False
    if not _mod01.family_supports_reportable_run(record):
        return False
    if record.get("sealed") and record.get("edited_after_seal"):
        if not record.get("identifier_changed"):
            return False
    for field in ("kill_check_fields", "kill_checks"):
        checks = record.get(field)
        if not isinstance(checks, (list, tuple)):
            continue
        standing_claims = record.get("headline_claims")
        if not isinstance(standing_claims, (list, tuple)):
            standing_claims = record.get("claims")
        if not isinstance(standing_claims, (list, tuple)):
            continue
        for check in checks:
            if isinstance(check, dict) and check.get("claim") is not None \
                    and check.get("claim") not in standing_claims:
                return False
    if record.get("ecology_point") == "fixed" and not record.get("amendment_landed"):
        return False
    if record.get("data_dependent_top_up") and not record.get("look_register"):
        return False
    return True


def admit_claim(family, claim=None):
    """Admit one claim to a family. A claim entering after results
    are seen is barred from the family and supports no headline
    publication from it."""
    if isinstance(family, dict) and family.get("results_seen"):
        raise NamedControllerFailure(
            "claim entering after results are seen is barred from the family"
        )
    return {"admitted": True, "claim": _freeze(claim)}


def kill_check_for_claim(claim):
    """One named kill check for one headline claim, in four parts:
    the name of the check; the data it runs on, standing outside
    the artefact under check; the judge that applies it, standing
    outside the artefact under check; and the killing result."""
    return {
        "claim": claim,
        "name": "kill check for " + str(claim),
        "data": "records outside the artefact under check",
        "judge": "checker outside the artefact under check",
        "killing_result": "the claim does not stand as reported",
        "data_outside_artefact": True,
        "judge_outside_artefact": True,
        "fixed_before_runs": True,
    }


def kill_checks_for_family(family_id="family-under-test", claims=None):
    """The kill checks fixed before runs for one family, one per
    headline claim in the family list."""
    claims = list(claims or ("headline claim 1",))
    return [kill_check_for_claim(claim) for claim in claims]


def validate_kill_check(check):
    """Return True only for a complete kill check whose data and
    judge both stand outside the artefact under check."""
    if not isinstance(check, dict):
        return False
    if not check.get("name") or not check.get("killing_result"):
        return False
    return bool(
        check.get("data_outside_artefact")
        and check.get("judge_outside_artefact")
    )


def registry_basis_fields():
    """The family facing registry basis carriage of DQ7-07: the
    family record carries the registry basis fields, and until the
    basis stands, the 5 percent figure is not reported as a
    recomputed result."""
    return {
        "basis_standing": "carried, not adopted as recomputed",
        "five_percent_figure_reported_as_recomputed": False,
        "fields": [
            "family sentence", "claim form blocks", "run set sentence",
            "dependence sentence", "procedure sentence",
            "confirmation sentence", "coverage sentence", "version sentence",
        ],
    }


# ---------------------------------------------------------------------------
# Run classes, the stopping rule, and the look register
# ---------------------------------------------------------------------------

def run_class_markings():
    """The four run classes and their record markings. The classes
    are distinct; confirmation uses held out seeds and held out
    settings."""
    return {
        "screening": {"seed_domain": "screening", "held_out_settings": False, "reporting": False},
        "confirmation": {"seed_domain": "held out confirmation", "held_out_settings": True, "reporting": True},
        "headline": {"seed_domain": "held out confirmation", "held_out_settings": True, "reporting": True},
        "validation": {"seed_domain": "held out confirmation", "held_out_settings": True, "reporting": False},
    }


# The letter canonicalisation the money and anchor readings share,
# stated in one form. A name first reads through the recorded letter
# mapping below, which covers the letters compatibility decomposition
# cannot reduce: non Latin letters standing for Latin letters of the
# marker words, in homoglyph form and in transliteration form, and
# special Latin letters with no decomposition. The mapped name then
# reads through compatibility decomposition with combining marks
# dropped, so accented and fullwidth forms reduce to their base
# letters, and the decomposed and case folded characters then read
# through the letter mapping again, in the sister form, so a letter
# that decomposition or case folding reduces to a mapped letter
# stands read as that letter. Every remaining digit reads as its
# decimal value in plain digits. Only letters and digits survive
# the fold.
_LETTER_MAP = {
    "\u0430": "a", "\u0431": "b", "\u0432": "v", "\u0433": "g",
    "\u0434": "d", "\u0435": "e", "\u0451": "e", "\u0436": "zh",
    "\u0437": "z", "\u0438": "i", "\u0439": "y", "\u043a": "k",
    "\u043b": "l", "\u043c": "m", "\u043d": "n", "\u043e": "o",
    "\u043f": "p", "\u0440": "r", "\u0441": "s", "\u0442": "t",
    "\u0443": "y", "\u0444": "f", "\u0445": "h", "\u0446": "ts",
    "\u0447": "ch", "\u0448": "sh", "\u0449": "shch", "\u044a": "",
    "\u044b": "y", "\u044c": "", "\u044d": "e", "\u044e": "yu",
    "\u044f": "ya",
    "\u03b1": "a", "\u03b2": "b", "\u03b3": "g", "\u03b4": "d",
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "e", "\u03b8": "t",
    "\u0398": "t", "\u03d1": "t", "\u03f4": "t",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03be": "x", "\u03bf": "o", "\u03c0": "p",
    "\u03c1": "r", "\u03c3": "s", "\u03c2": "s", "\u03c4": "t",
    "\u03c5": "y", "\u03c6": "ph", "\u03c7": "ch", "\u03c8": "ps",
    "\u03c9": "o",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0166": "t", "\u0167": "t",
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
    "\u13d2": "r", "\u13ac": "e", "\u13aa": "a", "\u13de": "l",
    "\u13b7": "m", "\u13be": "o", "\u13c1": "n", "\u13ef": "y",
    "\uaba2": "r", "\uab7c": "e", "\uab7a": "a", "\uabae": "l",
    "\uab87": "m", "\uab8e": "o", "\uab91": "n", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
}

# Beside the s reading of Cyrillic U+0441, the same letter carries
# a c reading, as in the scenario field name. Beside the n reading
# of Armenian U+0578, the same letter carries an un reading, as in
# the amount key. Each reading stands as its own canonical map, and
# a name stands read under every map.
_LETTER_MAP_C = dict(_LETTER_MAP, **{"\u0441": "c"})
_LETTER_MAP_VO = dict(_LETTER_MAP, **{"\u0578": "un", "\u0548": "un"})
_CANONICAL_MAPS = (_LETTER_MAP, _LETTER_MAP_C, _LETTER_MAP_VO)

# Digit and leet substitutions inside a marker word read in two
# further forms beside the canonical form: one where each digit
# reads as the letter it commonly stands for, and one where digits
# drop out, for a digit standing inside a word in place of nothing.
_LEET_MAP = {
    "0": "o", "1": "l", "2": "z", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y",
}
_LEET_MAP_I = dict(_LEET_MAP, **{"1": "i"})


# Letters that carry two recorded readings at once, so one name
# can need both readings at two positions in a single word:
# Cyrillic es as s and as c, Greek upsilon and Cyrillic u as u
# and as y, Cyrillic en as n and as its look alike reading h,
# Armenian vo as n and as the two letters un, and Greek theta as
# t and as th. A name stands read
# under every combination of these readings, position by position.
_ALT_READINGS = {
    "\u03b8": ("t", "th"),
    "\u0441": ("s", "c"),
    "\u03c5": ("u", "y"),
    "\u0443": ("u", "y"),
    "\u043d": ("n", "h"),
    "\u0439": ("y", "i"),
    "\u0578": ("n", "un"),
    "\u00a2": ("", "c"),
    "$": ("", "s"),
    "\u00a7": ("", "s"),
    "+": ("", "t"),
}


def _reading_characters(character):
    """The characters one handed character stands as beside
    itself: the parts of its compatibility decomposition and
    the parts of its case folded form, with combining marks
    left out, so a reading recorded for a decomposed or case
    folded form of the character stands gathered for it."""
    forms = [character]
    for form in (unicodedata.normalize("NFKD", character),
                 unicodedata.normalize(
                     "NFKD", character.casefold())):
        for part in form:
            if unicodedata.combining(part) or \
                    unicodedata.category(part).startswith("M"):
                continue
            if part not in forms:
                forms.append(part)
    return forms


def _canonicalise_mapped(mapped, letter_map=None):
    if letter_map is None:
        letter_map = _LETTER_MAP
    decomposed = unicodedata.normalize("NFKD", mapped)
    folded = unicodedata.normalize("NFKD", decomposed.casefold())
    pieces = []
    for character in folded:
        if unicodedata.combining(character) or \
                unicodedata.category(character).startswith("M"):
            continue
        digit = unicodedata.digit(character, None)
        if digit is not None:
            pieces.append(str(digit))
            continue
        pieces.append(letter_map.get(
            character, letter_map.get(character.lower(), character)))
    return "".join(piece for piece in pieces if piece.isalnum())


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies. A value that is not a text form stores
    no text at all, in the cured MOD-01 form: the helper
    returns None for one, so no name stands judged from a
    string reading a non text key itself supplies."""
    if isinstance(value, str):
        return str.__str__(value)
    return None


def _canonicalised_name(key, letter_map=None):
    if letter_map is None:
        letter_map = _LETTER_MAP
    if not isinstance(key, str):
        return ""
    mapped = "".join(
        letter_map.get(character, letter_map.get(
            character.lower(), character))
        for character in str.__str__(key)
    )
    return _canonicalise_mapped(mapped, letter_map)


def _folded_money_key(key):
    return _canonicalised_name(_stored_text(key))


def _folded_money_variants(key):
    """The folded forms one name reads under, in one stated set: the
    canonical form; that form with digit and leet substitutions read
    as the letters they stand for (the digit 1 read as l and, in a
    second form, as i); that form with digits dropped; and each of
    those with the transliterated spelling of the money marker, the
    Cyrillic spelling that reads realmani in Latin letters, read as
    the marker itself. A letter that carries two recorded readings
    stands read under every combination of its readings, position
    by position, so a single name can carry both readings at once.
    A name stands as a barred or counted name where any one of its
    forms reads as that name. The checks that consume these forms
    also read a name through the bound free reading below, so a
    name whose combinations pass the enumeration bound above, and
    a name needing two leet readings of one figure at two
    positions, still stand read in full."""
    forms = set()
    bases = set()
    stored = _stored_text(key)
    if stored is None:
        stored = ""
    for letter_map in _CANONICAL_MAPS:
        bases.add(_canonicalised_name(stored, letter_map))
    options = []
    for character in stored:
        readings = set()
        for form in _reading_characters(character):
            alt = _ALT_READINGS.get(
                form, _ALT_READINGS.get(form.lower()))
            if alt is not None:
                readings.update(alt)
        if readings:
            options.append(tuple(sorted(readings)))
        else:
            options.append((_LETTER_MAP.get(
                character,
                _LETTER_MAP.get(character.lower(), character)),))
    for index, combination in enumerate(
            itertools.product(*options)):
        if index >= 2048:
            break
        bases.add(_canonicalise_mapped("".join(combination)))
    for base in bases:
        forms.add(base)
        for table in (_LEET_MAP, _LEET_MAP_I):
            forms.add("".join(table.get(character, character)
                              for character in base))
        forms.add("".join(
            character for character in base if not character.isdigit()))
        digit_choices = []
        for character in base:
            if character == "1":
                digit_choices.append(("l", "i", ""))
            elif character.isdigit() and character in _LEET_MAP:
                digit_choices.append((_LEET_MAP[character], ""))
            else:
                digit_choices.append((character,))
        for index, combination in enumerate(
                itertools.product(*digit_choices)):
            if index >= 4096:
                break
            forms.add("".join(combination))
    marker = _MONEY_MARKER.replace("_", "")
    return tuple(
        form.replace("realmani", marker) for form in forms
    )


_MONEY_MARKER_FOLDED = _MONEY_MARKER.replace("_", "")
_ANCHOR_VALUES_FIELD_FOLDED = _folded_money_key(_ANCHOR_VALUES_FIELD)


# The bound free reading behind the folded forms. The enumeration
# above stops at 2048 combinations, so a name carrying more alt
# reading positions than that bound holds, or a name needing two
# different leet readings of the figure 1 at two positions, can
# stand past every enumerated form while still reading as a barred
# or counted name. The reading below never enumerates the
# combinations: it carries, character by character, the set of
# readings each character can stand for, and walks a target or a
# marker through those sets position by position, in the manner
# of the bound free character read at MOD-01. Each character
# stands under the readings of every canonical map and under its
# alt readings where it carries them, and the walk then runs
# under four whole name modes: the readings as they stand, the
# leet mode, the digit drop mode, and the combined mode, where
# each digit position on its own reads as its leet letter or
# drops out, so one name can carry a leet reading at one digit
# position and a drop reading at another in a single reading.
# In the leet mode a digit
# reads as the letter it stands for at that position, and the
# figure 1 reads as l or as i at each position on its own, so one
# name can carry the i reading at one position and the l reading
# at another in a single reading.

_FOLDED_READ_MODES = (None, "leet", "drop", "leetdrop")


def _base_reading_options(key):
    options = []
    stored = _stored_text(key)
    if stored is None:
        return options
    for character in stored:
        raw = set()
        for form in _reading_characters(character):
            alt = _ALT_READINGS.get(
                form, _ALT_READINGS.get(form.lower()))
            if alt is not None:
                raw.update(alt)
            for letter_map in _CANONICAL_MAPS:
                raw.add(letter_map.get(
                    form,
                    letter_map.get(form.lower(), form)))
        segments = {
            _canonicalise_mapped(reading) for reading in raw}
        options.append(tuple(sorted(segments)))
    return options


def _folded_segment_options(segment, mode):
    if mode == "drop":
        return {"".join(
            character for character in segment
            if not character.isdigit())}
    if mode == "leetdrop":
        choices = []
        for character in segment:
            if character == "1":
                choices.append(("l", "i", ""))
            elif character.isdigit() and character in _LEET_MAP:
                choices.append((_LEET_MAP[character], ""))
            elif character.isdigit():
                choices.append((character, ""))
            else:
                choices.append((character,))
        if not choices:
            return {""}
        return {
            "".join(parts)
            for parts in itertools.product(*choices)}
    if mode == "leet":
        choices = []
        for character in segment:
            if character == "1":
                choices.append(("l", "i"))
            elif character in _LEET_MAP:
                choices.append((_LEET_MAP[character],))
            else:
                choices.append((character,))
        if not choices:
            return {""}
        return {
            "".join(parts)
            for parts in itertools.product(*choices)}
    return {segment}


def _segments_by_character(key, mode):
    return [
        tuple(sorted({
            folded
            for base in options
            for folded in _folded_segment_options(base, mode)}))
        for options in _base_reading_options(key)
    ]


def _folded_name_matches(key, folded_target):
    """True where a name reads as the folded target under every
    recorded reading, read position by position with no bound on
    the number of combinations the name carries."""
    for mode in _FOLDED_READ_MODES:
        positions = {0}
        for segment_options in _segments_by_character(key, mode):
            next_positions = set()
            for position in positions:
                for segment in segment_options:
                    if folded_target[
                            position:position + len(segment)] == segment:
                        next_positions.add(position + len(segment))
            positions = next_positions
            if not positions:
                break
        if len(folded_target) in positions:
            return True
    return False


def _prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _segments_carry_pattern(segments_by_character, pattern):
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
                    current = _prefix_state(pattern, current, character)
                next_states.add(current)
        if full in next_states:
            return True
        states = next_states
    return full in states


def _folded_name_carries(key, folded_marker):
    """True where a name carries the folded marker under every
    recorded reading, read position by position, including the
    transliterated spelling of the money marker, which the folded
    forms above read as the marker itself."""
    for mode in _FOLDED_READ_MODES:
        if _segments_carry_pattern(
                _segments_by_character(key, mode), folded_marker):
            return True
    if folded_marker == _MONEY_MARKER_FOLDED:
        for mode in _FOLDED_READ_MODES:
            if _segments_carry_pattern(
                    _segments_by_character(key, mode), "realmani"):
                return True
    return False


# One barred read bound for MOD-12 and its sister surfaces,
# stated at 100, the bound every sister cured surface states.
_MAX_BARRED_READ_DEPTH = 100


def _base_iter(value):
    """Iterate a list, tuple, set, or frozenset part through its
    base class iteration, never through a reading the part itself
    supplies, so a part whose own iteration yields nothing still
    stands read by the contents in its base class storage."""
    if isinstance(value, list):
        return list.__iter__(value)
    if isinstance(value, tuple):
        return tuple.__iter__(value)
    if isinstance(value, frozenset):
        return frozenset.__iter__(value)
    return set.__iter__(value)


def _base_children(value):
    """The parts one container holds, read through base class
    operations only: dict keys beside dict values through the
    base dict readings, and every other container through its
    base class iteration."""
    if isinstance(value, dict):
        return list(dict.keys(value)) + list(dict.values(value))
    return list(_base_iter(value))


def _base_count(value):
    """The count of a handed value through its base class length
    reading, never through a length reading the value itself
    supplies. A value in no sized base form carries no base
    class length: the helper raises TypeError in the sister
    form, and the caller handles that refusal, so no count
    stands judged from a reading the value itself supplies."""
    if isinstance(value, list):
        return list.__len__(value)
    if isinstance(value, tuple):
        return tuple.__len__(value)
    if isinstance(value, frozenset):
        return frozenset.__len__(value)
    if isinstance(value, set):
        return set.__len__(value)
    if isinstance(value, dict):
        return dict.__len__(value)
    if isinstance(value, str):
        return str.__len__(value)
    if isinstance(value, bytearray):
        return bytearray.__len__(value)
    if isinstance(value, bytes):
        return bytes.__len__(value)
    raise TypeError("the handed value carries no base class length")


_CONTAINER_TYPES = (dict, list, tuple, set, frozenset)


def _shape_exceeds_bounds(value):
    """True where a value stands deeper than the barred read bound
    or carries a cycle on one of its paths. The walk counts
    containers only against the bound, so a scalar leaf standing
    below a chain of containers adds no level of its own, and it
    walks dict keys beside dict values, so nesting that stands
    in a dict key counts in the same way as nesting in a dict
    value. Every container stands read through base class
    operations only, and every distinct container stands walked
    once: the walk first gathers the distinct containers the
    value reaches and the child containers each one holds, then
    reads that graph once for a cycle and once for the longest
    container path from the root, so a container shared by two
    siblings costs one walk, not one walk per path. A container
    repeated on a path stands as a cycle in that graph, and the
    bound stands crossed where the longest container path from
    the root runs past it. The check walks with explicit stacks,
    so a hostile shape is reported in this form and never as a
    bare RecursionError."""
    if not isinstance(value, _CONTAINER_TYPES):
        return False
    children_by_id = {}
    nodes_by_id = {}
    pending = [value]
    while pending:
        current = pending.pop()
        if id(current) in children_by_id:
            continue
        nodes_by_id[id(current)] = current
        child_containers = [
            child for child in _base_children(current)
            if isinstance(child, _CONTAINER_TYPES)]
        children_by_id[id(current)] = [
            id(child) for child in child_containers]
        for child in child_containers:
            if id(child) not in children_by_id:
                pending.append(child)
    root_id = id(value)
    heights = {}
    on_path = {root_id}
    stack = [(root_id, iter(children_by_id[root_id]))]
    while stack:
        node_id, child_iter = stack[-1]
        advanced = False
        for child_id in child_iter:
            if child_id in on_path:
                return True
            if child_id in heights:
                continue
            on_path.add(child_id)
            stack.append((child_id, iter(children_by_id[child_id])))
            advanced = True
            break
        if not advanced:
            stack.pop()
            on_path.discard(node_id)
            child_ids = children_by_id[node_id]
            if child_ids:
                heights[node_id] = 1 + max(
                    heights[child_id] for child_id in child_ids)
            else:
                heights[node_id] = 0
    return heights[root_id] > _MAX_BARRED_READ_DEPTH


def _carries_barred_money_value(value, _depth=0, _seen=None):
    """True where a barred money field stands in the value within
    the barred read bound. Every distinct container stands read
    once, at the least depth any path reaches it, through base
    class operations only: a dict part through the base dict
    items reading, and every other container through its base
    class iteration. A container shared by two siblings therefore
    costs one read, not one read per path, while a money field
    standing within the bound on any path still stands read,
    because the least depth path reads the widest part of the
    shared subtree. Dict keys stand unread by this read, as
    before; the walk runs over dict values and over the elements
    of the other container forms."""
    if _depth > _MAX_BARRED_READ_DEPTH:
        return False
    if not isinstance(value, _CONTAINER_TYPES):
        return False
    best_depth = {id(value): _depth}
    stack = [(value, _depth)]
    while stack:
        current, depth = stack.pop()
        if depth > _MAX_BARRED_READ_DEPTH:
            continue
        if best_depth.get(id(current), depth) < depth:
            continue
        if isinstance(current, dict):
            entries = list(dict.items(current))
            amount_stands = False
            currency_stands = False
            for key, item in entries:
                variants = _folded_money_variants(key)
                if ("amount" in variants
                        or _folded_name_matches(key, "amount")) \
                        and item is not None:
                    amount_stands = True
                if "currency" in variants \
                        or _folded_name_matches(key, "currency"):
                    currency_stands = True
            if amount_stands and currency_stands:
                return True
            for key, item in entries:
                if (any(
                        _MONEY_MARKER_FOLDED in variant
                        for variant in _folded_money_variants(key))
                        or _folded_name_carries(
                            key, _MONEY_MARKER_FOLDED)) and (
                        item is not None):
                    return True
            children = [item for key, item in entries]
        else:
            children = list(_base_iter(current))
        for child in children:
            if not isinstance(child, _CONTAINER_TYPES):
                continue
            child_depth = depth + 1
            if child_depth > _MAX_BARRED_READ_DEPTH:
                continue
            if child_depth < best_depth.get(
                    id(child), _MAX_BARRED_READ_DEPTH + 1):
                best_depth[id(child)] = child_depth
                stack.append((child, child_depth))
    return False


def validate_run_record(run):
    """Return True only where a run record stands in its class,
    with its class fields stated: an empty record fails, a record
    with no stated class or no stated seed domain fails, a
    screening run promoted into a confirmation role by
    relabelling fails, and a reporting run, headline or
    confirmation, on the screening domain fails. A record
    carrying a barred money field at any depth fails, and a
    record whose anchor scenario values stand at a count other
    than the three stated values fails."""
    if not isinstance(run, dict) or not run:
        return False
    if run.get("run_class") not in RUN_CLASSES:
        return False
    if not run.get("seed_domain"):
        return False
    if run.get("relabelled_from") == "screening" and run.get("run_class") != "screening":
        return False
    if run.get("run_class") in ("confirmation", "headline") \
            and run.get("seed_domain") == "screening":
        return False
    if _shape_exceeds_bounds(run):
        return False
    if _carries_barred_money_value(run):
        return False
    for key, values in run.items():
        if _ANCHOR_VALUES_FIELD_FOLDED not in _folded_money_variants(key) \
                and not _folded_name_matches(
                    key, _ANCHOR_VALUES_FIELD_FOLDED):
            continue
        try:
            count = _base_count(values)
        except TypeError:
            return False
        if count != 3:
            return False
    return True


def claim_label(claim=None):
    """The label of one claim: a claim without a settings lineage
    is labelled a screening finding only."""
    if not isinstance(claim, dict) or not claim.get("settings_lineage"):
        return "screening finding only"
    return "claim with settings lineage"


def readout_status(readout):
    """The standing of one readout under the stopping rule, over
    all six conditions together: condition 1, the claim in
    bounding form; condition 2, the search completed at rung 6
    under a materiality bound fixed in advance, with no material
    failure found; condition 3, the tolerance and replication
    rule stated; condition 4, confirmation under the family
    discipline; condition 5, the eleven check artefact battery
    with A-04, A-05, A-09, A-10, and A-11 passed; condition 6,
    the assumption set and row identifiers inside the result.
    Established stands only where all six hold. Every lower form
    names the first unmet condition, and names every unmet
    condition beside it."""
    readout = readout or {}
    battery = readout.get("check_artefact_battery")
    if isinstance(battery, dict):
        passed = battery.get("passed") or ()
        battery_ok = all(
            mark in passed
            for mark in ("A-04", "A-05", "A-09", "A-10", "A-11")
        ) and len(passed) >= 11
    else:
        battery_ok = battery is True
    conditions = {
        1: bool(readout.get("claim_in_bounding_form")),
        2: bool(
            readout.get("bound_fixed_in_advance")
            and readout.get("search_complete")
            and not readout.get("material_failure_found")
            and readout.get("search_completed_at_rung", 6) == 6
        ),
        3: bool(readout.get("tolerance_and_replication_rule")),
        4: bool(readout.get("confirmation_under_family_discipline")),
        5: bool(battery_ok),
        6: bool(readout.get("assumption_set_and_rows_inside_result")),
    }
    unmet = [number for number in sorted(conditions) if not conditions[number]]
    if not unmet:
        return {
            "form": "established",
            "named_condition": None,
            "unmet_conditions": [],
        }
    return {
        "form": "lower_bound",
        "named_condition": 2 if 2 in unmet else unmet[0],
        "unmet_conditions": unmet,
    }


def look_register_for_family(family_id="family-under-test"):
    """The look register of one family, under a prewritten alpha
    spending function fixed in advance. Each entry records the
    look number, the information fraction as a derived ratio, the
    boundary the spending function assigned to that look, and
    whether the readout crossed it."""
    return {
        "family_id": family_id,
        "spending_function_fixed_in_advance": True,
        "entries": [
            {
                "look_number": 1,
                "information_fraction": 0.5,
                "boundary": "spending function boundary for look 1",
                "crossed": False,
            }
        ],
    }


def validate_look_decision(decision):
    """Return True only where a decision rests on a registered
    look. No promotion, refinement, top up beyond a rule fixed in
    the family record before runs, or readout wording decision
    rests on an unregistered look, and a register entry written
    after the decision it would judge does not cure it."""
    if not isinstance(decision, dict):
        return False
    if not decision.get("registered"):
        return False
    if decision.get("entry_written_after_decision"):
        return False
    return True


# ---------------------------------------------------------------------------
# Grids, replicates, screening surfaces, and the decay arm
# ---------------------------------------------------------------------------

def grid_artefacts(produced_before_pilot=True):
    """Grid artefacts. Every artefact produced before the NQ-4
    timing pilot lands is marked provisional, per AC-7."""
    standing = "provisional" if produced_before_pilot else "refixed on the pilot figure"
    return [
        {"kind": "grid", "standing": standing},
        {"kind": "density", "standing": standing},
        {"kind": "run count", "standing": standing},
    ]


def grid_decision_log():
    """The grid decision log as a family definition record: every
    candidate value and rejection carries the provisional standing
    until the pilot figure lands, and no grid is fixed by the
    log."""
    return {
        "form": "family definition record",
        "grid_fixed_by_log": False,
        "entries": [
            {"candidate": "grid candidate 1", "standing": "provisional"},
        ],
    }


def validate_grid_claim(claim):
    """Return False where a grid point stands presented as
    affordable before the timing pilot lands."""
    if not isinstance(claim, dict):
        return False
    if claim.get("claim") == "affordable" and not claim.get("pilot_landed"):
        return False
    return True


def sample_statement(runs=None):
    """The sample statement of one result, inside the result: the
    count of runs completed in each run class, stated class by
    class, what the sample was as the concrete units counted,
    and, where no run stands completed, the bound stated in
    words with no count invented."""
    counts = {run_class: 0 for run_class in RUN_CLASSES}
    named = []
    for run in runs or ():
        if isinstance(run, dict) and run.get("run_class") in counts:
            counts[run["run_class"]] += 1
            named.append(run.get("run_id") or run.get("run_identifier")
                         or run["run_class"])
    total = sum(counts.values())
    if not total:
        return {
            "n": 0,
            "runs_completed_by_class": counts,
            "sample": "none",
            "bound": (
                "no run stands completed behind this result; "
                "the DQ7-02 gate stands unadopted"),
        }
    return {
        "n": total,
        "runs_completed_by_class": counts,
        "sample": "the runs named in this statement: " + ", ".join(
            str(name) for name in named),
        "bound": "counts taken from the runs this result rests on only",
    }


def screening_readout(fixture="F-17", runs=None):
    """The screening readout for the past programme points of
    fixture F-17: farm shares of 50, 60, and 70 percent, reported
    on the D-05 traces and on the honest loss rate and not on the
    win count, in their weighed and not adopted standing. The
    sample statement stands inside the readout, counted from the
    runs handed in and from no others."""
    return {
        "fixture": fixture,
        "farm_shares_percent": [50, 60, 70],
        "reported_on": ["D-05 traces", "honest loss rate"],
        "standing": "weighed, not adopted",
        "sample_statement": sample_statement(runs),
    }


def winning_regime(daily_shares):
    """Return True only where the attacker share stands above the
    honest share at every daily evaluation over the final 30
    simulated days. Shares are evaluated at the end of each
    simulated day; each entry is an attacker and honest pair. An
    entry that is not a pair of numbers fails in the named form,
    never as a bare unpacking or comparison error."""
    shares = list(daily_shares or ())
    if len(shares) < 30:
        return False
    for entry in shares[-30:]:
        try:
            attacker, honest = entry
        except (TypeError, ValueError):
            raise NamedControllerFailure(
                "winning regime entry is not an attacker and honest pair: "
                + repr(entry))
        if not isinstance(attacker, (int, float)) \
                or not isinstance(honest, (int, float)) \
                or isinstance(attacker, bool) or isinstance(honest, bool):
            raise NamedControllerFailure(
                "winning regime entry carries a non numeric share: "
                + repr(entry))
        if not attacker > honest:
            return False
    return True


def validate_screening_claim(claim):
    """Return False where an F-17 screening point stands presented
    as adopted scope: the points are a weighing, not adopted
    scope."""
    if not isinstance(claim, dict):
        return False
    if claim.get("fixture") == "F-17" and claim.get("standing") == "adopted scope":
        return False
    return True


def top_up_applies(winning_probability, replicates_after_top_up):
    """The top up rule of fixture F-18 as this controller states
    it: a control point found in screening with a winning
    probability above 0.1 and below 0.9 is topped up to at least
    30 replicates, and the rule stands recorded in the run
    record."""
    if not isinstance(winning_probability, (int, float)) \
            or isinstance(winning_probability, bool) \
            or not isinstance(replicates_after_top_up, (int, float)) \
            or isinstance(replicates_after_top_up, bool):
        raise NamedControllerFailure(
            "top up rule inputs are not numbers: "
            + repr((winning_probability, replicates_after_top_up)))
    return bool(
        0.1 < winning_probability < 0.9
        and replicates_after_top_up >= 30
    )


DECAY_SLICES = (
    "7 days",
    "about 14 days",
    "about 69 days",
    "180 day run length scale",
    "about 693 days",
    "infinite",
)


def decay_arm_readout(fixture="F-14", runs=None):
    """The decay arm readout: the six named half life slices in
    every plane the arm reports, the two weighed extension slices
    labelled as an outside range extension, and the decay arm
    companion table in the same readout, one row per slice. Each
    row carries its values from the arm it reports or an explicit
    no result standing in words, never placeholder text. The
    sample statement stands inside the readout."""
    rows = []
    for slice_name in DECAY_SLICES:
        rows.append({
            "slice": slice_name,
            "half_life": slice_name,
            "control_point_values": ["no result standing for this slice"],
            "result_values": ["no result standing for this slice"],
        })
    for index in (1, 2):
        rows.append({
            "slice": "extension slice " + str(index),
            "half_life": "extension slice " + str(index),
            "control_point_values": ["no result standing for this slice"],
            "result_values": ["no result standing for this slice"],
            "label": "outside range extension",
        })
    return {
        "fixture": fixture,
        "planes": [
            {"name": "decay plane", "companion_table": rows},
        ],
        "sample_statement": sample_statement(runs),
    }


def validate_decay_readout(readout):
    """Return False where a decay arm plane stands reported with
    no companion table in the same readout."""
    if not isinstance(readout, dict):
        return False
    for plane in readout.get("planes") or ():
        if not plane.get("companion_table"):
            return False
    return True


# ---------------------------------------------------------------------------
# Hostile family ownership and counting illustrations
# ---------------------------------------------------------------------------

def hostile_family_status(fixture="F-13"):
    """The hostile input family stands as a required sweep family
    under this controller, with magnitudes fixed in the family
    record before runs."""
    return {
        "fixture": fixture,
        "standing": "required",
        "magnitudes_fixed_before_runs": True,
    }


def validate_sweep_programme(programme):
    """Return False where a sweep programme carries the hostile
    family as absent, optional, or sampled below magnitude: such
    a programme has not run as required."""
    if not isinstance(programme, dict):
        return False
    for family in programme.get("families") or ():
        if isinstance(family, dict) and family.get("name") == "hostile":
            if family.get("standing") != "required":
                return False
            magnitudes = (
                family.get("magnitudes")
                or family.get("fixed_magnitudes")
                or family.get("magnitude_fields")
            )
            return bool(magnitudes)
    return False


def hostile_kind_counts_as_run(kind=None, ran_at=None, fixed_magnitude=None):
    """A hostile kind run below its fixed magnitude does not count
    as run."""
    if ran_at is None or fixed_magnitude is None:
        return False
    return ran_at >= fixed_magnitude


def counting_basis(fixture="F-20"):
    """The Saltelli counting illustrations of fixture F-20: 14,336
    distinct evaluations at 12 inputs and a base sample of 1,024
    without second order indices. The figures illustrate the
    counting method and price nothing."""
    return {
        "fixture": fixture,
        "distinct_evaluations": 14336,
        "inputs": 12,
        "base_sample": 1024,
        "standing": "illustration",
        "prices_anything": False,
    }


def validate_cost_claim(claim):
    """Return False for any cost claim, run count commitment, or
    affordability statement resting on an F-20 figure, and for an
    F-19 composite form worded as a measured cost."""
    if not isinstance(claim, dict):
        return False
    if claim.get("basis_fixture") == "F-20":
        return False
    if claim.get("basis_fixture") == "F-19" and claim.get("wording") == "measured cost":
        return False
    return True


def validate_seed_placement(placement):
    """Seed replicates sit outside any sampled base design, and
    held out confirmation seeds form a separate seed family from
    the screening family."""
    if not isinstance(placement, dict):
        return False
    if placement.get("replicates_inside_base_design"):
        return False
    return placement.get("confirmation_family") != placement.get("screening_family")


# ---------------------------------------------------------------------------
# Rule version carriage and the family split
# ---------------------------------------------------------------------------

def record_version_sets(record_kinds=()):
    """The rule version set each named record kind carries: every
    record carries the exact set under which it was produced, as
    data."""
    return {
        kind: "rule-version-set-1"
        for kind in sorted(record_kinds or (), key=str)
    }


def validate_record_version(record):
    """Return False where a record stands presented under a rule
    version set it was not produced under."""
    if not isinstance(record, dict):
        return False
    return record.get("produced_under") == record.get("presented_under")


def family_version_parts(family_id="family-under-test"):
    """The family split by rule version: results under two version
    sets stand in two version parts of the family."""
    return [
        {"family_id": family_id, "rule_version_set": "set-a", "part": 1},
        {"family_id": family_id, "rule_version_set": "set-b", "part": 2},
    ]


def validate_family_pooling(pooling):
    """Return False for pooled results across a rule change with
    no bound recorded in the family record. Pooling recorded as a
    named bound, stating the two version sets pooled and the
    ground for pooling them, stands in the recorded form."""
    if not isinstance(pooling, dict):
        return False
    pooled = pooling.get("pooled_version_sets") or ()
    if len(pooled) <= 1:
        return True
    bound = pooling.get("bound_recorded")
    if not isinstance(bound, dict):
        return False
    return bool(bound.get("version_sets") and bound.get("ground"))


# ---------------------------------------------------------------------------
# Gated run starts
# ---------------------------------------------------------------------------

def _input_failure(action, ground):
    return {
        "status": "input failure",
        "form": "named input failure",
        "action": action,
        "failure": "named input failure: " + ground,
        "run_started": False,
        "seed_drawn": False,
    }


def _gated_start(action, run_class=None, family_id=None):
    refusal = _mod02.gated_refusal(action)
    refusal["run_class"] = run_class
    refusal["family_id"] = family_id
    refusal["run_started"] = False
    refusal["ground_in_words"] = (
        "No adoption record for the DQ7-02 gate stands, so no seed "
        "can be derived and no run can start.")
    refusal["next_step"] = (
        "Nothing stands for the operator to do here; the block sits "
        "with the decision on the DQ7-02 adoption record.")
    refusal["sample_statement"] = sample_statement()
    return refusal


def start_run(run_class=None, family_id=None):
    """Start one run. Start inputs stand validated before the gate
    answer: a run class outside the four stated classes, a missing
    run class, and a missing family identifier each return a named
    input failure, never the gated refusal, and no default run
    class stands substituted. Executable runs wait on the DQ7-02
    gate: a lawful start returns the recorded gated refusal of
    MOD-02 and starts nothing, in the one form that gate uses
    across MOD-02 and MOD-04, with its ground and its next step
    stated in words beside its codes and its sample statement
    inside the result."""
    if run_class not in RUN_CLASSES:
        return _input_failure(
            "start run", "run class missing or outside the stated classes: "
            + str(run_class))
    if not family_id:
        return _input_failure("start run", "family identifier missing")
    return _gated_start("start run", run_class=run_class, family_id=family_id)


def start_sweep(family_id=None):
    """Start one sweep. A missing family identifier returns a named
    input failure. Gated on DQ7-02 in the same form as a run
    start."""
    if not family_id:
        return _input_failure("start sweep", "family identifier missing")
    return _gated_start("start sweep", family_id=family_id)


__all__ = [
    "RUN_CLASSES",
    "GATE_QUESTION",
    "FAMILY_COMPLETENESS_ITEMS",
    "DECAY_SLICES",
    "NamedControllerFailure",
    "make_family_record",
    "sweep_manifest",
    "retained_run_record",
    "family_record_validation_failures",
    "sample_statement",
    "seal_family_record",
    "apply_family_edit",
    "validate_family_record",
    "admit_claim",
    "kill_check_for_claim",
    "kill_checks_for_family",
    "validate_kill_check",
    "registry_basis_fields",
    "run_class_markings",
    "validate_run_record",
    "claim_label",
    "readout_status",
    "look_register_for_family",
    "validate_look_decision",
    "grid_artefacts",
    "grid_decision_log",
    "validate_grid_claim",
    "screening_readout",
    "winning_regime",
    "validate_screening_claim",
    "top_up_applies",
    "decay_arm_readout",
    "validate_decay_readout",
    "hostile_family_status",
    "validate_sweep_programme",
    "hostile_kind_counts_as_run",
    "counting_basis",
    "validate_cost_claim",
    "validate_seed_placement",
    "record_version_sets",
    "validate_record_version",
    "family_version_parts",
    "validate_family_pooling",
    "start_run",
    "start_sweep",
]

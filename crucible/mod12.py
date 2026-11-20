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
import math
import unicodedata
from decimal import Decimal
from fractions import Fraction

from crucible import mod01 as _mod01
from crucible import mod02 as _mod02
from crucible import mod10 as _mod10

RUN_CLASSES = ("screening", "confirmation", "headline", "validation")
GATE_QUESTION = "DQ7-02"

FAMILY_COMPLETENESS_ITEMS = tuple(_mod01.COMPLETENESS_FIELDS)

# The alias keys of the user facing family record (Step 16,
# R16-11): each alias stands marked as an alias of the one field
# it carries, in the record itself under the alias_keys entry.
# The completeness pairs stand in the same marking: the brief
# name of a completeness field stands as the alias of its Form 1
# field name, the one key set of MOD-01 (R16-15).
FAMILY_ALIAS_KEYS = {
    "family_id": "family_identifier",
    "claims": "headline_claims",
    "kill_checks": "kill_check_fields",
}

_CONTROLLER_ALIAS_PAIRS = (
    ("family_id", "family_identifier"),
    ("claims", "headline_claims"),
    ("kill_checks", "kill_check_fields"),
)

# The named carriage keys of a made family record (Step 16 fix
# wave 2, row F2-01, ruling T16-23): the keys make_family_record
# carries beside the Form 1 fields and the completeness brief
# names, enumerated by name from that construction. A stored
# key standing outside the Form 1 fields, the completeness
# brief names, and these carriage keys stands unnamed, and the
# family surfaces that read the MOD-01 judgement on a made
# record refuse it by name, in place of reading the inner
# judgement alone. The seal and edit keys below stand beside
# the made record keys only in the complete form the seal and
# edit acts themselves write, as _legitimate_wider_keys
# states (Step 16 fix wave 3, row F3-01, ruling T16-39): a
# record that has never been sealed carrying any of them
# stands refused and named at the seal, and a fresh record
# carrying any of them in any other form stands refused and
# named at the validation surfaces. The controller bar keys
# below stand admitted at no family surface: they stand
# refused and named at the seal and refused and named at
# validation, while the gates that judge those bars by name
# stand as they stood.
FAMILY_CARRIAGE_KEYS = (
    "family_id",
    "claims",
    "kill_checks",
    "family_version",
    "family_manifest_hash",
    "sealed",
    "registry_basis_fields",
    "results_seen",
    "form",
    "alias_keys",
    "completeness_presentation",
)

_FAMILY_SEAL_EDIT_KEYS = (
    "seal",
    "seal_version",
    "seal_hash",
    "sweep_manifest",
    "runs_under",
    "edited_after_seal",
    "identifier_changed",
    "runs_start_again",
)

_FAMILY_CONTROLLER_BAR_KEYS = (
    "ecology_point",
    "amendment_landed",
    "data_dependent_top_up",
    "look_register",
)


def _stored_pairs_value(record, field):
    """The value one family record stores under a field name,
    found by scanning its stored pairs through base dict
    operations, a field standing present only where a stored
    key carries its name in stored text, never through a
    reading the handed record supplies."""
    if not isinstance(record, dict):
        return None
    for key, item in list(dict.items(record)):
        if _key_stored_text(key) == field:
            return item
    return None


_SEAL_RECORDED_HASH_STANDING = (
    "hash value as recorded on the record, "
    "stated as the hash")

_EDITED_IDENTIFIER_SUFFIX = "-edited-1"


def _seal_form_stands(record):
    """Whether the sealed standing of one family record stands
    in the form the product own seal act writes it (Step 16
    fix wave 4, row F4-01, ruling T16-49): the record stands
    sealed, the seal stands as a record value carrying the
    version, hash, and hash standing keys alone, the seal
    version and the seal hash stand equal to the version and
    the hash the seal itself carries, the family manifest hash
    stands equal to that hash, the hash standing stands in the
    form the seal act writes for the hash it carries, the seal
    version stands as the family version the record carries or
    as the seal act default where no version value stands, and
    the sweep manifest stands equal to the manifest the sweep
    act produces for the record as it stands. A sealed standing
    in any other form stands in no form the seal act writes."""
    if _stored_pairs_value(record, "sealed") is not True:
        return False
    seal = _stored_pairs_value(record, "seal")
    if not isinstance(seal, dict):
        return False
    seal_fields = set()
    for key, _item in list(dict.items(seal)):
        text = _key_stored_text(key)
        if text:
            seal_fields.add(text)
    if seal_fields != {"version", "hash", "hash_standing"}:
        return False
    version = _stored_pairs_value(seal, "version")
    hash_value = _stored_pairs_value(seal, "hash")
    hash_standing = _stored_pairs_value(seal, "hash_standing")
    if not _stored_values_equal(
            _stored_pairs_value(record, "seal_version"), version):
        return False
    if not _stored_values_equal(
            _stored_pairs_value(record, "seal_hash"), hash_value):
        return False
    if not _stored_values_equal(
            _stored_pairs_value(record, "family_manifest_hash"),
            hash_value):
        return False
    if hash_value is None:
        if not _stored_text_equals_form(
                hash_standing, _SEAL_NO_HASH_STANDING):
            return False
    elif _stored_value_present(hash_value):
        if not _stored_text_equals_form(
                hash_standing, _SEAL_RECORDED_HASH_STANDING):
            return False
    else:
        return False
    family_version = _stored_pairs_value(record, "family_version")
    expected_version = (
        family_version if _stored_value_present(family_version)
        else "version 1")
    if not _stored_values_equal(version, expected_version):
        return False
    manifest = _stored_pairs_value(record, "sweep_manifest")
    if not isinstance(manifest, dict):
        return False
    manifest_fields = set()
    for key, _item in list(dict.items(manifest)):
        text = _key_stored_text(key)
        if text:
            manifest_fields.add(text)
    if manifest_fields != {
            "family_identifier", "family_version",
            "sealed_family_record_hash"}:
        return False
    try:
        expected_manifest = sweep_manifest(record)
    except Exception:
        return False
    for field in ("family_identifier", "family_version",
                  "sealed_family_record_hash"):
        if not _stored_values_equal(
                _stored_pairs_value(manifest, field),
                _stored_pairs_value(expected_manifest, field)):
            return False
    return True


def _stored_text_equals_form(value, expected):
    """Whether a handed value stands as the expected text,
    judged on the text it stores, never through a reading the
    value itself supplies."""
    stored = _stored_text(value)
    return stored is not None and str.__eq__(stored, expected)


def _legitimate_wider_keys(record, include_seal=True):
    """The seal and edit keys of one family record that stand
    in the form the product own seal and edit acts write them
    (Step 16 fix wave 3, row F3-01, ruling T16-39, as settled
    at Step 16 fix wave 4, row F4-01, ruling T16-49). The seal
    keys stand legitimate only together, on a record whose
    sealed standing stands in the form the seal act writes
    it, as _seal_form_stands states. The edit keys stand
    legitimate only together, with each edit marker standing
    as True, the runs under value standing as the family
    identifier the record carries, that identifier standing
    in the edited form the edit act writes, carrying the
    edited suffix that act appends, and the record standing
    unsealed as that act leaves it, or standing sealed in the
    seal act form where a later seal carried the edit keys
    through; the runs under key alone stands legitimate where
    it carries that same identifier and no edit marker stands
    beside it, the form the edit of an unsealed record writes.
    Where include_seal stands False, at the seal itself, the
    seal keys stand legitimate nowhere, because no record
    handed to the seal has yet been sealed by that act, and
    the resealed standing does not carry the edit keys
    through that act either."""
    if not isinstance(record, dict):
        return set()
    try:
        present = set()
        for key, _item in list(dict.items(record)):
            text = _key_stored_text(key)
            if text:
                present.add(text)
    except Exception:
        return set()
    legitimate = set()
    seal_keys = _FAMILY_SEAL_EDIT_KEYS[:4]
    edit_keys = _FAMILY_SEAL_EDIT_KEYS[4:]
    seal_form = include_seal and _seal_form_stands(record)
    if include_seal and all(key in present for key in seal_keys):
        if seal_form:
            legitimate.update(seal_keys)
    identifier_text = _stored_text(
        _stored_pairs_value(record, "family_id"))
    if identifier_text is None:
        identifier_text = _stored_text(
            _stored_pairs_value(record, "family_identifier"))
    runs_text = _stored_text(
        _stored_pairs_value(record, "runs_under"))
    runs_matches = (
        runs_text is not None and identifier_text is not None
        and str.__eq__(runs_text, identifier_text))
    edited_form = (
        identifier_text is not None
        and str.endswith(identifier_text, _EDITED_IDENTIFIER_SUFFIX)
        and (_stored_pairs_value(record, "sealed") is False
             or seal_form))
    if all(key in present for key in edit_keys):
        if _stored_pairs_value(
                record, "edited_after_seal") is True and (
                _stored_pairs_value(
                    record, "identifier_changed") is True) and (
                _stored_pairs_value(
                    record, "runs_start_again") is True) and (
                runs_matches) and edited_form:
            legitimate.update(edit_keys)
    elif "runs_under" in present and not any(
            key in present for key in edit_keys[1:]):
        if runs_matches:
            legitimate.add("runs_under")
    return legitimate


def _unnamed_family_fields(record, controller_bars=False,
                           for_seal=False):
    """The stored keys of one family record standing outside
    the Form 1 fields, the completeness brief names, and the
    named carriage keys, each named by the text it stores.
    The keys stand read through base dict operations on the
    stored pairs, never through a reading the handed record
    supplies, in the form the seal already guards. A key
    storing no text stands named by its safe string form.
    The seal and edit keys stand outside the named carriage
    keys except in the form the product own seal and edit
    acts write them, as _legitimate_wider_keys states, and
    the controller bar keys stand outside them at every
    surface this helper serves, the seal and the validation
    failures alike, so each one stands named where it stands
    refused (Step 16 fix wave 3, row F3-01, ruling T16-39).
    The controller_bars argument stands retained in the form
    the validation surface has called it in; it admits
    nothing."""
    if not isinstance(record, dict):
        return []
    allowed = set(_mod01.form_fields("1"))
    allowed.update(_mod01.COMPLETENESS_FIELDS)
    allowed.update(FAMILY_CARRIAGE_KEYS)
    allowed.update(_legitimate_wider_keys(
        record, include_seal=not for_seal))
    unnamed = []
    for key, _item in list(dict.items(record)):
        text = _key_stored_text(key)
        if not text:
            unnamed.append(_safe_str(key))
        elif text not in allowed:
            unnamed.append(text)
    return unnamed


def _alias_values_equal(first, second):
    """Whether two alias twin values store the same value, judged
    through the stored values reading of this module, with a
    cyclic or raising reading standing as no agreement beyond
    identity."""
    if first is second:
        return True
    try:
        if _carries_cycle(first) or _carries_cycle(second):
            return False
        return bool(_stored_values_equal(first, second))
    except Exception:
        return False


def alias_divergences(record):
    """The diverged alias states of one family record, named:
    one entry per alias pair whose two keys stand present and
    carry different values, across the controller pairs and the
    completeness pairs. A diverged alias state stands named here
    rather than silently judged (R16-11)."""
    diverged = []
    if not isinstance(record, dict):
        return diverged
    for alias, canonical in _CONTROLLER_ALIAS_PAIRS:
        if dict.__contains__(record, alias) and dict.__contains__(
                record, canonical):
            if not _alias_values_equal(
                    dict.get(record, alias),
                    dict.get(record, canonical)):
                diverged.append(
                    "diverged alias keys: " + alias + " and "
                    + canonical + " carry different values for one "
                    "field, and the diverged state stands named "
                    "rather than judged in silence")
    standing = _mod01.completeness_standing(record)
    for prose in standing["diverged_fields"]:
        entry = None
        for candidate in standing["fields"]:
            if candidate["field"] == prose:
                entry = candidate
                break
        slug = entry["key"] if entry is not None else prose
        diverged.append(
            "diverged alias keys: " + slug + " and " + prose
            + " carry different values for one completeness "
            "field, and the diverged state stands named rather "
            "than judged in silence")
    return diverged


def family_record_presentation(record):
    """The presentation of one family record (Step 16, R16-04):
    the completeness fields standing as open markers stand named
    as awaiting supply, the fields carrying placeholder text
    stand named as placeholder fields, and the record stands as
    finished only where no completeness field stands awaiting
    supply, missing, diverged, or standing as a placeholder
    value, and a completeness field standing as a placeholder
    value stands named as placeholder in the standing text
    (Step 16 fix wave 2, row F2-04, ruling T16-30). The
    placeholder reading stands on the folded form of the
    stored text, case and spacing folded, and the standing
    text states the placeholder standing whenever any field
    stands placeholder, in the mixed case of a placeholder
    field beside an absent or open field as in the whole
    placeholder case (Step 16 fix wave 3, row F3-03, ruling
    T16-41). The placeholder fields this presentation names
    stand as the completeness fields alone: the scan field
    set is the completeness field set, so a non completeness
    field carrying placeholder text stands named nowhere in
    placeholder_fields (Step 16 fix wave 4, row F4-02,
    ruling T16-50). The supply itself stands charged to no
    fix and no value stands invented here (OP-16).
    """
    if not isinstance(record, dict):
        return {
            "standing": "not a record: no presentation stands",
            "awaiting_supply_fields": [],
            "open_fields": [],
            "supplied_fields": [],
            "diverged_fields": [],
            "missing_fields": [],
            "placeholder_fields": [],
            "finished": False,
        }
    standing = _mod01.completeness_standing(record)
    completeness_placeholder_fields = list(
        standing["placeholder_fields"])
    placeholder_fields = list(completeness_placeholder_fields)
    awaiting = list(standing["open_fields"]) + list(
        standing["missing_fields"])
    finished = bool(
        not awaiting and not standing["diverged_fields"]
        and not standing["bare_scalar_fields"]
        and not standing["absent_fields"]
        and not completeness_placeholder_fields)
    if awaiting:
        standing_text = (
            "awaiting supply and not finished: the completeness "
            "fields named stand awaiting supply, their values "
            "standing as open markers under OP-13 in place of "
            "supplied values: " + ", ".join(awaiting))
    elif standing["diverged_fields"]:
        standing_text = (
            "not finished: the completeness fields named stand "
            "diverged between their two spellings: "
            + ", ".join(standing["diverged_fields"]))
    elif completeness_placeholder_fields:
        standing_text = (
            "not finished: the completeness fields named stand "
            "as placeholder values, placeholder text in place "
            "of supplied values, and no completeness field "
            "standing as placeholder stands supplied: "
            + ", ".join(completeness_placeholder_fields))
    elif finished:
        standing_text = (
            "supplied: every completeness field stands supplied, "
            "and no completeness field stands awaiting supply")
    else:
        standing_text = (
            "not finished: the completeness standing stands as "
            + standing["standing"])
    if completeness_placeholder_fields and (
            "placeholder" not in standing_text):
        standing_text = (
            standing_text
            + "; and the completeness fields named stand as "
            "placeholder values, placeholder text in place of "
            "supplied values, and no completeness field "
            "standing as placeholder stands supplied: "
            + ", ".join(completeness_placeholder_fields))
    return {
        "standing": standing_text,
        "awaiting_supply_fields": awaiting,
        "open_fields": list(standing["open_fields"]),
        "supplied_fields": list(standing["supplied_fields"]),
        "diverged_fields": list(standing["diverged_fields"]),
        "missing_fields": list(standing["missing_fields"]),
        "placeholder_fields": placeholder_fields,
        "finished": finished,
    }

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
    plain deep copy preserves them. A dict assignment whose key hash or equality reading
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
            copied_key = _freeze(key, _memo)
            copied_item = _freeze(item, _memo)
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
        copied_items = [
            _freeze(item, _memo) for item in frozenset.__iter__(value)]
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
            _freeze(item, _memo) for item in set.__iter__(value)]
        try:
            for frozen_item in copied_items:
                copied.add(frozen_item)
        except Exception:
            _memo[id(value)] = copied_items
            return copied_items
        return copied
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, bytearray):
        return bytearray(value)
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    return value


def _stored_id_text(value):
    """The text a handed identifier value stores, read through
    the stored text reading of this module where the value
    stands in a text form, so a new identifier stands built
    from the stored identifier, never from a string reading
    the handed value itself supplies."""
    stored = _stored_text(value)
    if stored is not None:
        return stored
    return _safe_str(value)


def _stored_value_present(value):
    """Whether a handed value stands present, judged by what it
    stores, for every kind, in the cured MOD-01 form. A text
    value stands present where the text it stores stands non
    empty, read through the base class length. A container or
    bytes value stands present where the contents it stores
    stand non empty, read through the base class length of its
    kind. A boolean stands present where it stands as True, and
    a number where the number it stores stands apart from zero,
    each read through the base class operations of its kind. A
    value of any other kind carries no stored content a base
    class operation can read, so it stands absent, whatever
    truth reading it supplies."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, memoryview):
        return bytes.__len__(bytes(value)) > 0
    if isinstance(value, (
            list, tuple, set, frozenset, dict, bytearray, bytes)):
        return _base_count(value) > 0
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    return False


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
    if claims is None:
        claims = ["headline claim 1"]
    elif isinstance(claims, (list, tuple, set, frozenset)):
        claims = list(_base_iter(claims)) or ["headline claim 1"]
    else:
        claims = ["headline claim 1"]
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
    # The alias keys stand marked as aliases on the record itself
    # (R16-11): one key per field stands as the field, and every
    # further spelling stands in this marking and nowhere as a
    # second field. The completeness pairs stand in the same
    # marking, the brief name as alias of the Form 1 field name.
    aliases = dict(FAMILY_ALIAS_KEYS)
    for prose, slug in _mod01.COMPLETENESS_KEY_PAIRS:
        aliases[prose] = slug
    record["alias_keys"] = aliases
    # The presentation names the unsupplied completeness fields
    # as awaiting supply (R16-04): the made record does not
    # present as finished while its completeness values stand as
    # open markers.
    record["completeness_presentation"] = family_record_presentation(
        record)
    return record


def sweep_manifest(record):
    """The sweep manifest of one family record, in the Form 23
    fields: the family identifier, the family version, and the
    sealed family record hash, each as the record carries it.
    Each copied value stands under the same depth bound and
    cycle guard as the sister family acts of this module,
    checked before the copy: a value past the bound or carrying
    a cycle stands refused in the named form, never copied as a
    bare RecursionError."""
    if not isinstance(record, dict):
        record = {}
    seal = dict.get(record, "seal")
    if not isinstance(seal, dict):
        seal = {}
    sealed_hash = None
    for candidate in (dict.get(record, "family_manifest_hash"),
                      dict.get(record, "seal_hash"),
                      dict.get(seal, "hash")):
        if _stored_value_present(candidate):
            sealed_hash = candidate
            break
    identifier_value = dict.get(
        record, "family_identifier", dict.get(record, "family_id"))
    version_value = dict.get(record, "family_version")
    for subject, field_value in (
            ("family identifier value", identifier_value),
            ("family version value", version_value),
            ("sealed family record hash value", sealed_hash)):
        if _shape_exceeds_bounds(field_value):
            raise NamedControllerFailure(_shape_refusal(
                subject, field_value, "sweep manifest refused"))
    return {
        "family_identifier": _freeze(identifier_value),
        "family_version": _freeze(version_value),
        "sealed_family_record_hash": _freeze(sealed_hash),
    }


def retained_run_record(run_id, store_kind="sweep"):
    """One run record read through MOD-10, the Recorder store
    reading path the plan boundary row for this controller states.
    A record that does not resolve stands raised as the MOD-10
    named lookup failure, and no record is fabricated here."""
    return _mod10.read_run_record(run_id, store_kind=store_kind)


def _shape_cause(value):
    stack = [(value, "root", 0, frozenset())]
    while stack:
        node, path, depth, seen = stack.pop()
        if not isinstance(node, _CONTAINER_TYPES):
            continue
        if id(node) in seen:
            return ("cycle", path)
        if depth > _MAX_BARRED_READ_DEPTH:
            return ("depth", path)
        seen = seen | {id(node)}
        if isinstance(node, dict):
            children = []
            for key in dict.keys(node):
                children.append((key, path + "/" + _safe_str(key)))
                children.append((dict.get(node, key), path + "/" + _safe_str(key)))
        else:
            base_iter = (list.__iter__ if isinstance(node, list)
                         else tuple.__iter__ if isinstance(node, tuple)
                         else set.__iter__ if isinstance(node, set)
                         else frozenset.__iter__)
            children = [(item, path + "[" + str(index) + "]")
                        for index, item in enumerate(base_iter(node))]
        for child, child_path in children:
            stack.append((child, child_path, depth + 1, seen))
    return (None, "root")


def _shape_refusal(subject, value, act_wording):
    cause, path = _shape_cause(value)
    if cause == "cycle":
        return (
            act_wording + ": the " + subject + " carries a cycle at "
            + path + ", and no act stands performed on it")
    return (
        act_wording + ": the " + subject + " stands deeper than the "
        "stated bound of " + str(_MAX_BARRED_READ_DEPTH)
        + " (depth past the bound) at " + path
        + ", and no act stands performed on it")


_SEAL_HASH_PLACEHOLDER = (
    "manifest hash supplied as a record value, not computed")

_SEAL_NO_HASH_STANDING = (
    "no hash value stands on the record; "
    "no hash stands computed by this seal")


def seal_family_record(record):
    """Seal one family record. The completeness condition stands
    performed before the seal: a record missing any one of the
    completeness items this controller names is refused in the
    named form and does not seal. At Step 16 row R16-17 the seal
    also stands no seal on a record the product own validation
    rejects on its inner judgement: a record failing the MOD-01
    inner record judgement for Form 1 is refused in the named
    form and does not seal. A record that has never been sealed
    and carries any of the seal and edit keys the seal and edit
    acts write (seal, seal_version, seal_hash, sweep_manifest,
    runs_under, edited_after_seal, identifier_changed,
    runs_start_again), or any other field standing outside the
    form fields and the named carriage keys, stands refused and
    named in the same form: those keys stand as carriage only
    in the form a product act writes them, never as values
    handed in before the act. A record standing in the
    edited form the edit act writes after a seal, its edit
    keys complete with their markers standing as True and its
    runs under value standing as the new family identifier it
    carries, may seal as the new family it stands as, and its
    edit keys stand carried into the sealed record in that
    form. The seal
    hash field states the hash as a hash: where a hash value
    stands recorded on the record it stands carried as the
    hash, and where no hash value stands, or the only value
    standing is the placeholder wording that stood here before
    that row, the hash field stands as None and a hash standing
    field beside it states that no hash value stands and no
    hash stands computed by this seal, in place of presenting
    the placeholder wording as a hash. No hash form is computed
    in this act. A sweep
    manifest stands produced beside the seal. From the seal, any
    edit creates a new family identifier and runs under it start
    again. The record stands under the same depth bound and
    cycle guard as the sister record acts of this module,
    checked before the copy: a shape past the bound or carrying
    a cycle stands refused in the named form, never as a bare
    RecursionError. The bound guard runs before any reading of
    the handed record's contents takes effect, and the
    completeness, version, and hash readings run through base
    dict operations on the stored contents, never through a
    reading the handed record itself supplies, so a hostile
    record meets the named refusal form and no bare exception
    escapes. The version and hash values stand bound checked
    and copied under the guard before sealing, so nothing the
    handed record reports seals unguarded or by identity."""
    if _shape_exceeds_bounds(record):
        raise NamedControllerFailure(_shape_refusal(
            "record", record, "family record cannot seal"))
    if not isinstance(record, dict):
        raise NamedControllerFailure(
            "family record cannot seal: the value handed in "
            "stands in no record form (it stands in "
            + type(record).__name__ + " form, not as a "
            "record), and no seal stands on a value in no "
            "record form; next step: hand a family record, "
            "the record make_family_record builds, and call "
            "the seal again")
    if _stored_value_present(dict.get(record, "sealed")):
        raise NamedControllerFailure(
            "family record cannot seal: the record already "
            "stands sealed, and no second seal stands written "
            "on a sealed record; next step: start from the "
            "unsealed family record to seal a family, or apply "
            "a family edit to the sealed record, which starts "
            "a new family, and seal the edited record")
    if not any(
            _stored_pairs_value(record, field) is not None
            for field in (
                "family_identifier", "family_id",
                "headline_claims", "claims")):
        raise NamedControllerFailure(
            "family record cannot seal: the record stands in "
            "no family record form: it carries no family "
            "identifier and no headline claims, so it stands "
            "as a record of another form or as an empty "
            "record, not as a family record missing "
            "completeness items; next step: hand a family "
            "record, the record make_family_record builds, "
            "and call the seal again")
    missing = [
        item for item in FAMILY_COMPLETENESS_ITEMS
        if not isinstance(record, dict)
        or not _stored_value_present(dict.get(record, item))
    ]
    if missing:
        raise NamedControllerFailure(
            "family record cannot seal, completeness items missing: "
            + ", ".join(missing))
    # Step 16 fix wave 2, row F2-01, ruling T16-23, as settled
    # at Step 16 fix wave 3, row F3-01, ruling T16-39: the seal
    # check reads the inner judgement together with the named
    # extra field layer, in carriage form: a stored field
    # standing outside the Form 1 fields, the completeness
    # brief names, and the named carriage keys stands refused
    # and named here, while a made record carrying only named
    # carriage keys seals on the inner judgement as before.
    # The seal and edit keys stand in that extra field layer in
    # full at this act: a record that has never been sealed
    # carrying any of them stands refused and named here, and
    # only a record standing in the edited form the edit act
    # writes carries its edit keys through this check, as the
    # seal docstring above states. The docstring stands true of
    # this act in that form.
    unnamed = _unnamed_family_fields(record, for_seal=True)
    if isinstance(record, dict) and unnamed:
        raise NamedControllerFailure(
            "family record cannot seal, the record carries a "
            "field standing outside the form fields and the "
            "named carriage keys: " + ", ".join(unnamed)
            + ", and no seal stands on a record carrying an "
            "unnamed field")
    if isinstance(record, dict) and not _mod01._validate_record_bool(
            "1", record):
        raise NamedControllerFailure(
            "family record cannot seal, the record validation "
            "stands refused: the MOD-01 record judgement for "
            "Form 1 rejects this record, and no seal stands on "
            "a record the product own validation rejects")
    version_value = dict.get(record, "family_version")
    hash_value = dict.get(record, "family_manifest_hash")
    for seal_name, seal_value in (
            ("version", version_value), ("hash", hash_value)):
        if _shape_exceeds_bounds(seal_value):
            raise NamedControllerFailure(_shape_refusal(
                seal_name + " value", seal_value,
                "family record cannot seal"))
    if _stored_value_present(hash_value) and not (
            isinstance(hash_value, str)
            and str.__eq__(str.__str__(hash_value),
                          _SEAL_HASH_PLACEHOLDER)):
        resolved_hash = _freeze(hash_value)
        hash_standing = (
            "hash value as recorded on the record, "
            "stated as the hash")
    else:
        resolved_hash = None
        hash_standing = _SEAL_NO_HASH_STANDING
    sealed = _freeze(record)
    sealed["sealed"] = True
    sealed["seal"] = {
        "version": _freeze(version_value)
        if _stored_value_present(version_value) else "version 1",
        "hash": resolved_hash,
        "hash_standing": hash_standing,
    }
    sealed["seal_version"] = sealed["seal"]["version"]
    sealed["seal_hash"] = sealed["seal"]["hash"]
    sealed["family_manifest_hash"] = resolved_hash
    sealed["sweep_manifest"] = sweep_manifest(sealed)
    # The sealed record carries its presentation on its face
    # (R16-04): where its completeness values stand unsupplied,
    # the presentation names the fields as awaiting supply and
    # the sealed record does not present as finished.
    sealed["completeness_presentation"] = family_record_presentation(
        sealed)
    return sealed


def _edit_claim_stands(claim, standing):
    """Whether one explicit kill check claim stands among the
    standing claims, judged on the stored contents each side
    carries, in the claim reading form of this module: a claim
    and a standing claim in bytes, buffer, or split container
    dress stand judged as the texts they store and on stored
    values equality, never by plain membership on the handed
    claim value itself."""
    for part in standing:
        if _stored_values_equal(claim, part):
            return True
        claim_texts = _key_stored_texts(claim)
        part_texts = _key_stored_texts(part)
        if any(text != "" and text in part_texts
               for text in claim_texts):
            return True
    return False


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
    if _shape_exceeds_bounds(record):
        raise NamedControllerFailure(_shape_refusal(
            "record", record, "family edit refused"))
    if change is not None and _shape_exceeds_bounds(change):
        raise NamedControllerFailure(_shape_refusal(
            "change", change, "family edit refused"))
    edited = _freeze(record)
    frozen_change = _freeze(change) if isinstance(change, dict) else None
    if frozen_change is not None:
        edited.update(frozen_change)
    explicit_checks = []
    if frozen_change is not None:
        for field in ("kill_check_fields", "kill_checks"):
            supplied = dict.get(frozen_change, field)
            if isinstance(supplied, (list, tuple)):
                explicit_checks.extend(
                    item for item in (
                        list.__iter__(supplied)
                        if isinstance(supplied, list)
                        else tuple.__iter__(supplied)))
    if isinstance(change, dict) and (
            dict.__contains__(change, "headline_claims")
            or dict.__contains__(change, "claims")):
        raw = dict.get(change, "headline_claims") if (
            dict.__contains__(change, "headline_claims")) else dict.get(
                change, "claims")
    else:
        raw = dict.get(edited, "headline_claims") if (
            dict.__contains__(edited, "headline_claims")) else dict.get(
                edited, "claims")
    if raw is not None:
        if not isinstance(raw, (list, tuple)):
            raise NamedControllerFailure(
                "family edit refused: a claims value handed in "
                "does not stand in list or tuple form: "
                + _sentence_form(raw))
        standing = [
            _freeze(item) for item in (
                list.__iter__(raw) if isinstance(raw, list)
                else tuple.__iter__(raw))]
        edited["headline_claims"] = standing
        edited["claims"] = standing
        checks = [kill_check_for_claim(claim) for claim in standing]
        edited["kill_check_fields"] = checks
        edited["kill_checks"] = checks
        for check in explicit_checks:
            if isinstance(check, dict) \
                    and dict.get(check, "claim") is not None \
                    and not _edit_claim_stands(
                        dict.get(check, "claim"), standing):
                raise NamedControllerFailure(
                    "family edit refused: a kill check field names "
                    "a claim that no longer stands: "
                    + _safe_str(dict.get(check, "claim")))
    elif explicit_checks:
        standing_now = dict.get(edited, "headline_claims")
        if not isinstance(standing_now, (list, tuple)):
            standing_now = dict.get(edited, "claims")
        if isinstance(standing_now, (list, tuple)):
            for check in explicit_checks:
                if isinstance(check, dict) \
                        and dict.get(check, "claim") is not None \
                        and not _edit_claim_stands(
                            dict.get(check, "claim"), standing_now):
                    raise NamedControllerFailure(
                        "family edit refused: a kill check field "
                        "names a claim that no longer stands: "
                        + _safe_str(dict.get(check, "claim")))
    if isinstance(record, dict) and _stored_value_present(
            dict.get(record, "sealed")):
        base_id = dict.get(record, "family_identifier")
        if not _stored_value_present(base_id):
            base_id = dict.get(record, "family_id")
        new_id = _stored_id_text(base_id) + "-edited-1"
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
        edited["runs_under"] = dict.get(edited, "family_id")
    return edited


def family_record_validation_failures(record):
    """The named validation failures of one family record, field
    by field: every missing Form 1 field, every missing
    completeness field of the MOD-01 bar, and every missing
    completeness item this controller names, each named in the
    returned list. An empty list stands for a record carrying
    every named field. Every wider key this door refuses on
    stands named in its own entry: the eight seal and edit keys
    in any form but the form the product own seal and edit acts
    write them, and the four controller bar keys (ecology_point,
    amendment_landed, data_dependent_top_up, look_register)
    alike (Step 16 fix wave 3, row F3-01, ruling T16-39)."""
    if not isinstance(record, dict):
        return ["family record is not a record"]
    failures = []
    for field in _mod01.form_fields("1"):
        if not dict.__contains__(record, field) \
                or dict.get(record, field) is None:
            failures.append("missing field: " + field)
    for field in _mod01.COMPLETENESS_FIELDS:
        if not dict.__contains__(record, field):
            failures.append("missing completeness field: " + field)
    for item in FAMILY_COMPLETENESS_ITEMS:
        if not _stored_value_present(dict.get(record, item)):
            failures.append("missing completeness item: " + item)
    if not _mod01._validate_record_bool("1", record):
        failures.append("the MOD-01 record judgement stands refused")
    if not _mod01.family_supports_reportable_run(record):
        standing = _mod01.family_reportable_standing(record)
        failures.append(
            "the reportable run judgement stands refused: "
            + str(dict.get(standing, "standing"))
            + "; next step: supply stated values for the "
            "completeness fields the standing names, or "
            "correct the fields it names, and check the "
            "family record again")
    if _stored_value_present(dict.get(record, "sealed")) \
            and _stored_value_present(
                dict.get(record, "edited_after_seal")):
        if not _stored_value_present(
                dict.get(record, "identifier_changed")):
            failures.append(
                "sealed and edited record carries no identifier "
                "change: the sealed and edited identifier gate "
                "stands refused")
    if _kill_check_names_absent(record):
        failures.append(
            "a kill check names a claim standing nowhere among "
            "the record claims: the kill check gate stands refused")
    if _dress_eq(dict.get(record, "ecology_point"), "fixed") \
            and not _stored_value_present(
                dict.get(record, "amendment_landed")):
        failures.append(
            "ecology point stands fixed with no amendment landed: "
            "the ecology point gate stands refused")
    if _stored_value_present(
            dict.get(record, "data_dependent_top_up")) \
            and not _stored_value_present(
                dict.get(record, "look_register")):
        failures.append(
            "data dependent top up stands with no look register: "
            "the data dependent top up gate stands refused")
    # A field standing outside the Form 1 fields and the named
    # carriage keys stands named as a failure (Step 16 fix wave
    # 2, row F2-01, ruling T16-23), in place of passing on the
    # inner judgement alone.
    for field in _unnamed_family_fields(
            record, controller_bars=True):
        failures.append(
            "unnamed field: " + field + ": the field stands "
            "outside the Form 1 fields and the named carriage "
            "keys, so the record stands refused on that field")
    # A diverged alias state stands named as a failure, never
    # silently judged (R16-11): the entry names the pair and the
    # divergence, on the controller pairs and on the completeness
    # pairs alike.
    failures.extend(alias_divergences(record))
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
    so the controller path and the reporter path agree. A record
    sealed by the product own seal act, carrying the keys that
    act writes, and an edited record produced by the product own
    edit acts, validate here in that form (Step 16 fix wave 3,
    row F3-01, ruling T16-39)."""
    if not isinstance(record, dict):
        return False
    if family_record_validation_failures(record):
        return False
    if not _mod01._validate_record_bool("1", record):
        return False
    if not _mod01.family_supports_reportable_run(record):
        return False
    if _stored_value_present(dict.get(record, "sealed")) \
            and _stored_value_present(
                dict.get(record, "edited_after_seal")):
        if not _stored_value_present(
                dict.get(record, "identifier_changed")):
            return False
    if _kill_check_names_absent(record):
        return False
    if _dress_eq(dict.get(record, "ecology_point"), "fixed") \
            and not _stored_value_present(
                dict.get(record, "amendment_landed")):
        return False
    if _stored_value_present(
            dict.get(record, "data_dependent_top_up")) \
            and not _stored_value_present(
                dict.get(record, "look_register")):
        return False
    return True


def admit_claim(family, claim=None):
    """Admit one claim to a family. A claim entering after results
    are seen is barred from the family and supports no headline
    publication from it. The claim stands under the same depth
    bound and cycle guard as the sister record acts of this
    module, checked ahead of the copy: a claim past the bound
    or carrying a cycle stands refused in the named form, never
    copied whole, preserved in its cycle, or raised as a bare
    RecursionError."""
    if _shape_exceeds_bounds(claim):
        raise NamedControllerFailure(_shape_refusal(
            "claim", claim, "claim cannot be admitted"))
    if isinstance(family, dict) and _stored_value_present(
            dict.get(family, "results_seen")):
        raise NamedControllerFailure(
            "claim entering after results are seen is barred from the family"
        )
    return {"admitted": True, "claim": _freeze(claim)}


def _safe_str(value):
    """Render a handed value for a sentence: through its string
    reading where that reading stands, and through the base
    object repr where the string reading the value itself
    supplies raises, so the sentence stands delivered whole and
    never escapes bare on that reading."""
    try:
        return str(value)
    except Exception:
        return object.__repr__(value)


def _plain_number_value(value):
    """The plain number a handed value stands as, where the
    value stands in the plain number limb, an int or a float
    with a boolean standing apart from every number, read
    through its base class reading, so a number subclass
    stands judged on the number it stores and never through
    a comparison reading it supplies, in the cured MOD-11
    sister form. A value in any other form reads as None."""
    if isinstance(value, bool) \
            or not isinstance(value, (int, float)):
        return None
    if isinstance(value, int):
        return int.__int__(value)
    return float.__float__(value)


def kill_check_for_claim(claim):
    """One named kill check for one headline claim, in four parts:
    the name of the check; the data it runs on, standing outside
    the artefact under check; the judge that applies it, standing
    outside the artefact under check; and the killing result.
    The name stands built from the text the claim stores, read
    through the stored text reading of this module where the
    claim stands in a text form, and through the safe string
    form of this module where it does not, so a claim whose own
    string reading raises or misstates its stored text still
    stands named whole."""
    name_text = _stored_text(claim)
    if name_text is None:
        name_text = _safe_str(claim)
    return {
        "claim": claim,
        "name": "kill check for " + name_text,
        "data": "records outside the artefact under check",
        "judge": "checker outside the artefact under check",
        "killing_result": "the claim does not stand as reported",
        "data_outside_artefact": True,
        "judge_outside_artefact": True,
        "fixed_before_runs": True,
    }


def kill_checks_for_family(family_id="family-under-test", claims=None):
    """The kill checks fixed before runs for one family, one per
    headline claim in the family list. The claims stand read in
    the form of the cured sibling act make_family_record: a
    handing in list, tuple, set, or frozenset form stands read
    through the base iteration of its form, and a handing in
    any other form stands as the default claim list, so no
    truth, iteration, or string reading the handing itself
    supplies directs which claims stand checked."""
    if claims is None:
        claims = ["headline claim 1"]
    elif isinstance(claims, (list, tuple, set, frozenset)):
        claims = list(_base_iter(claims)) or ["headline claim 1"]
    else:
        claims = ["headline claim 1"]
    return [kill_check_for_claim(claim) for claim in claims]


def validate_kill_check(check):
    """Return True only for a complete kill check whose data and
    judge both stand outside the artefact under check."""
    if not isinstance(check, dict):
        return False
    if not _stored_value_present(dict.get(check, "name")) \
            or not _stored_value_present(
                dict.get(check, "killing_result")):
        return False
    return bool(
        _stored_value_present(dict.get(check, "data_outside_artefact"))
        and _stored_value_present(
            dict.get(check, "judge_outside_artefact"))
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
    string reading a non text key itself supplies. A bytes
    value, a bytearray value, and a memoryview value stand
    read as stored text by decoding their stored bytes as
    UTF-8 with undecodable bytes dropped, never through a
    string reading such a value itself supplies, so a form
    in bytes dress keeps the standing its stored name
    carries, in the form of section 2 of the Round 10
    register, limbs 2 and 6."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return None


def _key_stored_text(key, _depth=0):
    """The stored text of one key, in the container form of
    section 2 of the Round 10 register, limbs 3 and 4. A
    scalar key stands as its stored text. A container key
    in tuple, list, frozenset, or set form stands as the
    stored text of its parts joined in order with no
    separator added, each part read on its own stored text
    recursively, so a single part container carries the
    reading of its one part, a name split across the parts
    of one container key reads as one name, and a bytes
    part inside a container key reads under the bytes limb
    exactly as a bare bytes key reads. Parts past the
    barred read bound stand unread. The parts of a set or
    frozenset key carry no order of their own, so this
    single text reading joins them in the sorted order of
    their stored texts, the same reading in every process;
    the dress equality judgement stands on the fuller
    reading of _key_stored_texts, which reads the parts of
    an unordered container in every order they compose."""
    text = _stored_text(key)
    if text is not None:
        return text
    if _depth > _MAX_BARRED_READ_DEPTH:
        return ""
    if isinstance(key, (tuple, list)):
        return "".join(
            _key_stored_text(part, _depth + 1)
            for part in _base_iter(key))
    if isinstance(key, (frozenset, set)):
        return "".join(sorted(
            _key_stored_text(part, _depth + 1)
            for part in _base_iter(key)))
    return ""


# The bound on the composed texts one dress reading carries,
# in the enumeration bound form this module already states
# for its folded readings.
_DRESS_TEXTS_BOUND = 4096


def _key_stored_texts(key, _depth=0, _memo=None):
    """Every stored text one key composes, as a set of texts.
    A scalar key composes its one stored text. A key in
    tuple or list form composes the joins of its parts in
    their handed order, each part under every text it
    composes. A key in set or frozenset form carries no
    order of its own, so it composes the joins of its parts
    in every order of those parts, each part under every
    text it composes, so a name split across the parts of
    an unordered container stands composed whole whatever
    order the parts stand read in, and the judgement on it
    stands the same in every process. Parts past the barred
    read bound stand unread, as at _key_stored_text. Where
    the composed texts pass the stated bound, the reading
    falls back to the one deterministic text of
    _key_stored_text for that key, and no further text of
    that key stands composed. The combination total of the
    parts texts stands computed before any join stands
    built, in the form the sister reading at MOD-13 states:
    where that total passes the stated bound, the fallback
    stands taken at once and no cross product past the
    bound stands ever built. An unordered container
    holding more than seven parts stands under the same
    discipline: it contributes the one deterministic text
    of _key_stored_text alone, so no ordering enumeration
    past seven parts stands ever run. The joins of an
    unordered container stand built by used part sets, each
    part entering a join once, with the partial joins
    deduplicated as they grow, so orderings that compose the
    same texts stand built once and the work the act performs
    stands bounded by the distinct partial joins, never by
    the factorial of the part count times the cross product
    of one ordering. Where a partial join set passes the
    stated bound, the fallback stands taken at once, in the
    bound form this reading already states. One reading
    carries a memo of the parts it has already read, keyed
    on the identity of the part beside the depth it stands
    read at, threaded through every level of the reading:
    a part standing twice in one key, as the same object at
    the same depth, stands read once, and its texts stand
    shared by every standing of it."""
    text = _stored_text(key)
    if text is not None:
        return {text}
    if _memo is None:
        _memo = {}
    _memo_key = None
    if isinstance(key, (tuple, list, set, frozenset)):
        _memo_key = (id(key), _depth)
        if _memo_key in _memo:
            return _memo[_memo_key]

    def _done(result):
        if _memo_key is not None:
            _memo[_memo_key] = result
        return result

    if _depth > _MAX_BARRED_READ_DEPTH:
        return _done({""})
    if isinstance(key, (tuple, list)):
        options = [
            _key_stored_texts(part, _depth + 1, _memo)
            for part in _base_iter(key)]
        total = 1
        for part_options in options:
            total *= len(part_options)
            if total > _DRESS_TEXTS_BOUND:
                return _done({_key_stored_text(key, _depth)})
        texts = {""}
        for part_options in options:
            texts = {
                head + option
                for head in texts for option in part_options}
        return _done(texts)
    if isinstance(key, (frozenset, set)):
        parts = list(_base_iter(key))
        if len(parts) > 7:
            return _done({_key_stored_text(key, _depth)})
        options = [
            _key_stored_texts(part, _depth + 1, _memo)
            for part in parts]
        total = 1
        for part_options in options:
            total *= len(part_options)
            if total > _DRESS_TEXTS_BOUND:
                return _done({_key_stored_text(key, _depth)})
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
                        for option in options[index]:
                            grown.add(head + option)
                            if len(grown) > _DRESS_TEXTS_BOUND:
                                return _done(
                                    {_key_stored_text(key, _depth)})
            states = next_states
        return _done(states.get((1 << len(parts)) - 1, set()))
    return {""}


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
    return _canonicalised_name(_key_stored_text(key))


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
    stored = _key_stored_text(key)
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
    stored = _key_stored_text(key)
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


def _anchor_values_field_matches(key):
    """True where a key reads as the anchor scenario values
    field, judged on every text the key composes beside the
    one sorted text: a field name split across the parts of
    an unordered container key composes the name in one
    order of its parts, and that composed text, folded as
    the count limb folds a name, stands judged as the field
    in the dress judgement form of settlement S-15."""
    if _ANCHOR_VALUES_FIELD_FOLDED in _folded_money_variants(key) \
            or _folded_name_matches(key, _ANCHOR_VALUES_FIELD_FOLDED):
        return True
    for text in _key_stored_texts(key):
        if _ANCHOR_VALUES_FIELD_FOLDED in _folded_money_variants(text) \
                or _folded_name_matches(text, _ANCHOR_VALUES_FIELD_FOLDED):
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


def _dict_node_money_barred(entries):
    """Whether one dict standing in the barred money walk
    stands barred at its own node, in the form settlement
    S-14 states: the node stands judged on the joined
    reading of its keys in stored order, in the folded forms
    in which the walk judges a single key. The folded money
    marker split across two keys stands judged on that
    joined reading, and the amount and currency pair, which
    the walk frames at dict level across the keys of one
    dict together, stands judged where each name stands
    split across two keys of the same dict."""
    if len(entries) < 2:
        return False
    readings = [
        set(_folded_money_variants(key)) for key, item in entries]
    if _dict_keys_carry_split(readings, entries, _MONEY_MARKER_FOLDED):
        return True
    amount_stands = _dict_keys_tile_exact(
        readings, entries, "amount", True) or any(
            ("amount" in _folded_money_variants(key)
             or _folded_name_matches(key, "amount"))
            and item is not None
            for key, item in entries)
    currency_stands = _dict_keys_tile_exact(
        readings, entries, "currency", False) or any(
            "currency" in _folded_money_variants(key)
            or _folded_name_matches(key, "currency")
            for key, item in entries)
    return amount_stands and currency_stands


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
            if _dict_node_money_barred(entries):
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


def _text_eq(value, stated):
    """Judge a stored value against a stated text by its stored
    characters, through the base string equality, never through
    an equality reading the value itself supplies."""
    if not isinstance(value, str):
        return False
    result = str.__eq__(value, stated)
    return result if result is not NotImplemented else False


def _stored_eq(value, stated):
    """Judge a handed value against a stated text by the text it
    stores, in the stored text form of this module: a text value
    by its stored characters, and a bytes, bytearray, or
    memoryview value by its stored bytes decoded in that form,
    never through an equality reading the value itself supplies.
    A value storing no text stands apart from every stated text."""
    text = _stored_text(value)
    if text is None:
        return False
    result = str.__eq__(text, stated)
    return result if result is not NotImplemented else False


def _dress_text(value):
    """The text a handed value stores under the container form as
    well: a scalar value by its stored text, and a single or
    multi part container by the stored text of its parts joined
    in order, through the key stored text reading of this module,
    so a value in bytes, buffer, or container dress stands judged
    as the text it stores. For a value in set or frozenset dress
    this one text stands in the deterministic sorted part order
    of _key_stored_text; the equality judgement of _dress_eq
    stands on every text the dress composes."""
    return _key_stored_text(value)


def _dress_eq(value, stated):
    """Judge a handed value against a stated text by the texts it
    stores in scalar or container dress, through the base string
    equality on each stored text the dress composes: a value in
    set or frozenset dress, whose parts carry no order of their
    own, stands equal to the stated text where any order of its
    parts composes that text, so the judgement stands on the
    stored contents of the dress and the same in every process,
    never on the iteration order of the container."""
    for text in _key_stored_texts(value):
        result = str.__eq__(text, stated)
        if result is not NotImplemented and result:
            return True
    return False


def _carries_cycle(value):
    """Whether a handed value carries a cycle on one of its
    paths, walked with an explicit stack over the base class
    readings of this module, so the walk itself never recurses
    without bound. A container shared from two places on
    different paths carries no cycle."""
    if not isinstance(value, _CONTAINER_TYPES):
        return False
    on_path = set()
    stack = [(value, False)]
    while stack:
        current, closing = stack.pop()
        if closing:
            on_path.discard(id(current))
            continue
        if not isinstance(current, _CONTAINER_TYPES):
            continue
        if id(current) in on_path:
            return True
        on_path.add(id(current))
        stack.append((current, True))
        for child in _base_children(current):
            stack.append((child, False))
    return False


def _stored_values_equal(first, second):
    """Whether two handed values store the same value, judged on
    their stored forms: text storing values by their stored text,
    and every other value kind first under settlement S-16, in
    the form of the sibling act _stored_ids_equal of this
    module, never through an equality reading either value
    itself supplies and never by the plain equality of frozen
    copies, which judges kind blind."""
    first_text = _stored_text(first)
    second_text = _stored_text(second)
    if first_text is not None or second_text is not None:
        if first_text is None or second_text is None:
            return False
        result = str.__eq__(first_text, second_text)
        return result if result is not NotImplemented else False
    if _carries_cycle(first) or _carries_cycle(second):
        return first is second
    return _values_equal_kind_first(first, second)


def _values_equal_kind_first(one, two):
    """Whether two handed values store the same value, judged
    kind first part by part: a boolean stands apart from every
    number, an integer from a float, and a Decimal, a Fraction,
    and a complex value each stand judged against their own
    kind alone, outside the plain number limb, in the form
    settlement S-16 states and the sibling act
    _stored_ids_equal of this module states for identifiers.
    Containers stand judged part by part under this same
    reading, and a value of any other kind stands judged by
    identity, so no equality reading a handed value itself
    supplies decides the judgement. The part by part judgement
    stands walked on an explicit stack, in the walk form of
    the sibling act, so a value nested at any depth answers
    under this reading and never escapes as a bare
    RecursionError."""
    result = False
    stack = [{"first": one, "second": two, "state": "enter",
              "awaiting": False}]

    def deliver(value):
        nonlocal result
        result = value
        stack.pop()

    while stack:
        frame = stack[-1]
        state = frame["state"]
        if state == "enter":
            left = frame["first"]
            right = frame["second"]
            left_text = _stored_text(left)
            right_text = _stored_text(right)
            if left_text is not None or right_text is not None:
                if left_text is None or right_text is None:
                    deliver(False)
                else:
                    eq = str.__eq__(left_text, right_text)
                    deliver(eq if eq is not NotImplemented else False)
                continue
            if left is None or right is None:
                deliver(left is None and right is None)
                continue
            if isinstance(left, bool) or isinstance(right, bool):
                deliver(isinstance(left, bool)
                        and isinstance(right, bool) and left is right)
                continue
            if isinstance(left, int) or isinstance(right, int):
                deliver(isinstance(left, int) and isinstance(right, int)
                        and int.__eq__(left, right) is True)
                continue
            if isinstance(left, float) or isinstance(right, float):
                deliver(isinstance(left, float)
                        and isinstance(right, float)
                        and float.__eq__(left, right) is True)
                continue
            if isinstance(left, (Decimal, Fraction, complex)) \
                    or isinstance(right, (Decimal, Fraction, complex)):
                deliver(type(left) is type(right)
                        and type(left).__eq__(left, right) is True)
                continue
            if isinstance(left, dict) and isinstance(right, dict):
                if dict.__len__(left) != dict.__len__(right):
                    deliver(False)
                    continue
                frame["items"] = list(dict.items(left))
                frame["remaining"] = list(dict.items(right))
                frame["index"] = 0
                frame["state"] = "dict_next"
                continue
            if isinstance(left, (list, tuple)) \
                    and isinstance(right, (list, tuple)):
                if type(left) is not type(right):
                    deliver(False)
                    continue
                left_parts = _base_sequence(left)
                right_parts = _base_sequence(right)
                if len(left_parts) != len(right_parts):
                    deliver(False)
                    continue
                frame["pairs"] = list(zip(left_parts, right_parts))
                frame["index"] = 0
                frame["state"] = "seq_next"
                continue
            if isinstance(left, (set, frozenset)) \
                    and isinstance(right, (set, frozenset)):
                left_parts = _base_sequence(left)
                right_parts = _base_sequence(right)
                if len(left_parts) != len(right_parts):
                    deliver(False)
                    continue
                frame["items"] = left_parts
                frame["remaining"] = right_parts
                frame["index"] = 0
                frame["state"] = "set_next"
                continue
            deliver(left is right)
            continue
        if state == "seq_next":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if not result:
                    deliver(False)
                    continue
                frame["index"] += 1
            if frame["index"] >= len(frame["pairs"]):
                deliver(True)
                continue
            pair = frame["pairs"][frame["index"]]
            frame["awaiting"] = True
            stack.append({"first": pair[0], "second": pair[1],
                          "state": "enter", "awaiting": False})
            continue
        if state == "dict_next":
            if frame["index"] >= len(frame["items"]):
                deliver(True)
                continue
            frame["candidate"] = 0
            frame["state"] = "dict_key"
            continue
        if state == "dict_key":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["state"] = "dict_value"
                    continue
                frame["candidate"] += 1
            if frame["candidate"] >= len(frame["remaining"]):
                deliver(False)
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]][0],
                "second": frame["remaining"][frame["candidate"]][0],
                "state": "enter", "awaiting": False})
            continue
        if state == "dict_value":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["remaining"].pop(frame["candidate"])
                    frame["index"] += 1
                    frame["state"] = "dict_next"
                    continue
                frame["candidate"] += 1
                frame["state"] = "dict_key"
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]][1],
                "second": frame["remaining"][frame["candidate"]][1],
                "state": "enter", "awaiting": False})
            continue
        if state == "set_next":
            if frame["index"] >= len(frame["items"]):
                deliver(True)
                continue
            frame["candidate"] = 0
            frame["state"] = "set_part"
            continue
        if state == "set_part":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["remaining"].pop(frame["candidate"])
                    frame["index"] += 1
                    frame["state"] = "set_next"
                    continue
                frame["candidate"] += 1
            if frame["candidate"] >= len(frame["remaining"]):
                deliver(False)
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]],
                "second": frame["remaining"][frame["candidate"]],
                "state": "enter", "awaiting": False})
            continue
    return result


def _stored_ids_equal(first, second):
    """Whether two handed run identifiers store the same
    identifier, judged by kind before value, in the form of
    the estate stored pair reading at MOD-07: a boolean stands
    apart from every number, an integer from a float, a text
    form value, in string, bytes, bytearray, or memoryview
    dress, stands judged on the text it stores against a text
    form value alone, and containers stand judged part by part
    under this same reading, so no identifier stands conflated
    with one of another kind on a plain equality reading. The
    part by part judgement stands walked on an explicit stack,
    in the walk form this module states for its other deep
    walks, so a deep identifier answers under this reading at
    any depth and never escapes as a bare RecursionError; a
    cyclic identifier stands answered by identity, in the cured
    form of row R15-059, before the walk begins on it."""
    result = False
    stack = [{"first": first, "second": second, "state": "enter",
              "awaiting": False}]

    def deliver(value):
        nonlocal result
        result = value
        stack.pop()

    while stack:
        frame = stack[-1]
        state = frame["state"]
        if state == "enter":
            one = frame["first"]
            two = frame["second"]
            one_text = _stored_text(one)
            two_text = _stored_text(two)
            if one_text is not None or two_text is not None:
                if one_text is None or two_text is None:
                    deliver(False)
                else:
                    eq = str.__eq__(one_text, two_text)
                    deliver(eq if eq is not NotImplemented else False)
                continue
            if one is None or two is None:
                deliver(one is None and two is None)
                continue
            if isinstance(one, bool) or isinstance(two, bool):
                deliver(isinstance(one, bool)
                        and isinstance(two, bool) and one is two)
                continue
            if isinstance(one, int) and isinstance(two, int):
                deliver(int.__eq__(one, two) is True)
                continue
            if isinstance(one, float) and isinstance(two, float):
                deliver(float.__eq__(one, two) is True)
                continue
            if isinstance(one, (Decimal, Fraction, complex)) \
                    or isinstance(two, (Decimal, Fraction, complex)):
                deliver(type(one) is type(two)
                        and type(one).__eq__(one, two) is True)
                continue
            if _carries_cycle(one) or _carries_cycle(two):
                deliver(one is two)
                continue
            if isinstance(one, dict) and isinstance(two, dict):
                if dict.__len__(one) != dict.__len__(two):
                    deliver(False)
                    continue
                frame["items"] = list(dict.items(one))
                frame["remaining"] = list(dict.items(two))
                frame["index"] = 0
                frame["state"] = "dict_next"
                continue
            if isinstance(one, (list, tuple)) \
                    and isinstance(two, (list, tuple)):
                if type(one) is not type(two):
                    deliver(False)
                    continue
                one_parts = _base_sequence(one)
                two_parts = _base_sequence(two)
                if len(one_parts) != len(two_parts):
                    deliver(False)
                    continue
                frame["pairs"] = list(zip(one_parts, two_parts))
                frame["index"] = 0
                frame["state"] = "seq_next"
                continue
            if isinstance(one, (set, frozenset)) \
                    and isinstance(two, (set, frozenset)):
                one_parts = _base_sequence(one)
                two_parts = _base_sequence(two)
                if len(one_parts) != len(two_parts):
                    deliver(False)
                    continue
                frame["items"] = one_parts
                frame["remaining"] = two_parts
                frame["index"] = 0
                frame["state"] = "set_next"
                continue
            deliver(one is two)
            continue
        if state == "seq_next":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if not result:
                    deliver(False)
                    continue
                frame["index"] += 1
            if frame["index"] >= len(frame["pairs"]):
                deliver(True)
                continue
            pair = frame["pairs"][frame["index"]]
            frame["awaiting"] = True
            stack.append({"first": pair[0], "second": pair[1],
                          "state": "enter", "awaiting": False})
            continue
        if state == "dict_next":
            if frame["index"] >= len(frame["items"]):
                deliver(True)
                continue
            frame["candidate"] = 0
            frame["state"] = "dict_key"
            continue
        if state == "dict_key":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["state"] = "dict_value"
                    continue
                frame["candidate"] += 1
            if frame["candidate"] >= len(frame["remaining"]):
                deliver(False)
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]][0],
                "second": frame["remaining"][frame["candidate"]][0],
                "state": "enter", "awaiting": False})
            continue
        if state == "dict_value":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["remaining"].pop(frame["candidate"])
                    frame["index"] += 1
                    frame["state"] = "dict_next"
                    continue
                frame["candidate"] += 1
                frame["state"] = "dict_key"
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]][1],
                "second": frame["remaining"][frame["candidate"]][1],
                "state": "enter", "awaiting": False})
            continue
        if state == "set_next":
            if frame["index"] >= len(frame["items"]):
                deliver(True)
                continue
            frame["candidate"] = 0
            frame["state"] = "set_part"
            continue
        if state == "set_part":
            if frame["awaiting"]:
                frame["awaiting"] = False
                if result:
                    frame["remaining"].pop(frame["candidate"])
                    frame["index"] += 1
                    frame["state"] = "set_next"
                    continue
                frame["candidate"] += 1
            if frame["candidate"] >= len(frame["remaining"]):
                deliver(False)
                continue
            frame["awaiting"] = True
            stack.append({
                "first": frame["items"][frame["index"]],
                "second": frame["remaining"][frame["candidate"]],
                "state": "enter", "awaiting": False})
            continue
    return result


def _printed_int_name_matches(name, kept):
    """The printed name limb of row R14-076 in its cured form:
    an integer identifier and a text form identifier whose
    stored text stands as that integer printed name stand as
    one run. No other kind pairing stands joined on a printed
    name alone."""
    for number, other in ((name, kept), (kept, name)):
        if isinstance(number, int) and not isinstance(number, bool):
            other_text = _stored_text(other)
            if other_text is not None and str.__eq__(
                    other_text, int.__str__(number)) is True:
                return True
    return False


def _check_claim_value(check):
    """The claim one kill check stores, found by scanning its
    stored pairs and judging each stored key by every text it
    composes, so a key whose hash or equality reading names
    another field still stands found under the name it stores,
    and a field name split across the parts of an unordered
    container key stands found in the order its parts compose
    it, in the dress judgement form of settlement S-15. A
    check storing no claim stands as None."""
    for key, item in dict.items(check):
        for key_text in _key_stored_texts(key):
            if str.__eq__(key_text, "claim"):
                return item
    return None


def _kill_check_claim_values(record):
    """Every claim the kill check fields of one family record
    name, in list, tuple, and dict carriage alike: a check in
    list or tuple carriage stands judged on the claim it
    stores, a dict standing as one check stands judged on the
    claim that check stores, and a dict keyed by claim names
    stands judged on every key it carries and on the claim of
    any check it carries as a value, so no dict carriage of a
    kill check stands passed over in silence."""
    values = []
    for field in ("kill_check_fields", "kill_checks"):
        checks = dict.get(record, field)
        if isinstance(checks, dict):
            single = _check_claim_value(checks)
            if single is not None:
                values.append(single)
                continue
            for key, item in dict.items(checks):
                values.append(key)
                if isinstance(item, dict):
                    nested = _check_claim_value(item)
                    if nested is not None:
                        values.append(nested)
            continue
        if not isinstance(checks, (list, tuple)):
            continue
        for check in _base_sequence(checks):
            if isinstance(check, dict):
                claim = _check_claim_value(check)
                if claim is not None:
                    values.append(claim)
    return values


def _kill_check_names_absent(record):
    """Whether any kill check of one family record names a claim
    standing nowhere among the record claims, judged on the
    dress text each side stores and on the stored values
    equality of this module, never through an equality reading
    a handed claim itself supplies and never through a plain
    membership test on frozen copies: the standing claims stand
    read in bare form as the one claim that form carries, as
    well as in list, tuple, set, frozenset, and dict carriage,
    so no carriage of the standing claims stands passed over
    in silence: a claim and a standing
    claim in bytes, buffer, or split container dress stand
    judged as the text they store, on either side alike, and
    a claim or a standing claim in set or frozenset dress
    stands judged on every text its parts compose, in every
    order of those parts, so the judgement stands the same
    in every process."""
    standing_claims = dict.get(record, "headline_claims")
    if not isinstance(
            standing_claims, (list, tuple, set, frozenset, dict)):
        claims_fallback = dict.get(record, "claims")
        if isinstance(
                claims_fallback, (list, tuple, set, frozenset, dict)):
            standing_claims = claims_fallback
    if isinstance(standing_claims, dict):
        standing_parts = list(dict.keys(standing_claims))
    elif isinstance(
            standing_claims, (list, tuple, set, frozenset)):
        standing_parts = _base_sequence(standing_claims)
    elif standing_claims is not None:
        standing_parts = [standing_claims]
    else:
        claims_fallback = dict.get(record, "claims")
        if claims_fallback is None:
            return False
        standing_parts = [claims_fallback]
    standing_texts = [
        _key_stored_texts(part) for part in standing_parts]
    for claim in _kill_check_claim_values(record):
        if claim is None:
            continue
        claim_texts = _key_stored_texts(claim)
        matched = False
        for part, texts in zip(standing_parts, standing_texts):
            if any(
                    text != "" and text in texts
                    for text in claim_texts):
                matched = True
                break
            if _stored_values_equal(claim, part):
                matched = True
                break
        if not matched:
            return True
    return False


def _base_sequence(value):
    """The stored parts of a handed sequence, read through the
    base iteration of its form, as a list. A value in no sequence
    form stands as no parts."""
    if isinstance(value, list):
        return list(list.__iter__(value))
    if isinstance(value, tuple):
        return list(tuple.__iter__(value))
    if isinstance(value, frozenset):
        return list(frozenset.__iter__(value))
    if isinstance(value, set):
        return list(set.__iter__(value))
    return []


def _run_field(run, name):
    """The value a run record stores under a field name, found by
    scanning its stored pairs and judging each stored key by
    every text it composes, so a key whose hash or equality
    reading names another field still stands found under the
    name it stores, in the stored pairs scan form of the sister
    modules, and a field name split across the parts of an
    unordered container key stands found in the order its parts
    compose it, in the dress judgement form of settlement S-15.
    A field the record does not store stands as None."""
    for key, item in dict.items(run):
        for key_text in _key_stored_texts(key):
            if str.__eq__(key_text, name):
                return item
    return None


def _safe_repr(value):
    """Render a handed value for a refusal or failure sentence:
    through its repr reading where that reading stands, and
    through the base object repr where the repr reading the
    value itself supplies raises, so a sentence naming the
    handed value never escapes bare on that reading, in the
    guarded form of the sister modules."""
    try:
        return repr(value)
    except Exception:
        return object.__repr__(value)


def _sentence_form(value, _depth=0):
    """Render a handed value for a refusal or failure sentence
    on the form it stands in, for a sentence whose act judges
    form alone. A value standing in a stated scalar form
    stands rendered through the base class repr of the value
    it stores, so a repr reading the value itself supplies
    never stands as the name the sentence delivers, and a
    plain value in a stated form renders exactly as its
    plain repr renders. A container stands rendered part by
    part in the same form, in its handed order, past a
    stated depth bound by its kind name alone. A value in
    no stated form stands named by the name of its kind,
    the form it stands in, and never through a reading it
    supplies."""
    if isinstance(value, bool):
        return bool.__repr__(value)
    if isinstance(value, str):
        return str.__repr__(str.__str__(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.__repr__(bytes(value))
    if isinstance(value, int):
        return int.__repr__(value)
    if isinstance(value, float):
        return float.__repr__(value)
    if isinstance(value, complex):
        return complex.__repr__(value)
    if isinstance(value, Decimal):
        return Decimal.__repr__(value)
    if isinstance(value, Fraction):
        return Fraction.__repr__(value)
    if _depth >= 8:
        return type(value).__name__
    if isinstance(value, (list, tuple)):
        parts = [_sentence_form(part, _depth + 1)
                 for part in _base_iter(value)]
        if isinstance(value, tuple):
            if len(parts) == 1:
                return "(" + parts[0] + ",)"
            return "(" + ", ".join(parts) + ")"
        return "[" + ", ".join(parts) + "]"
    if isinstance(value, dict):
        parts = sorted(
            _sentence_form(key, _depth + 1) + ": "
            + _sentence_form(item, _depth + 1)
            for key, item in dict.items(value))
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, (set, frozenset)):
        parts = sorted(
            _sentence_form(part, _depth + 1)
            for part in _base_iter(value))
        return "{" + ", ".join(parts) + "}"
    return type(value).__name__


def _sentence_stored_repr(value):
    """Render a handed value for a failure sentence on the
    text it stores, for a sentence whose act judges the
    value on its stored text in scalar or container dress
    through _dress_eq. A value carrying a stored text
    stands rendered as the base repr of that stored text,
    and a value in container dress stands rendered as the
    base repr of the dress text its parts compose, so a
    repr reading the value itself supplies never stands
    as the name the sentence delivers, and a plain text
    value renders exactly as its plain repr renders. A
    value carrying no stored text and standing in no
    container dress stands rendered on the form it stands
    in, through _sentence_form."""
    stored = _stored_text(value)
    if stored is not None:
        return str.__repr__(stored)
    if isinstance(value, (list, tuple, set, frozenset)):
        return str.__repr__(_dress_text(value))
    return _sentence_form(value)


_RUN_NUMERIC_FIELD_MINIMA = (
    ("population_size", 1),
    ("run_length_in_days", 1),
    ("replicate_index", 0),
)


def _run_numeric_field_judged(field, value):
    """Whether one numeric field value of a run record stands
    in its stated form (FW4-04), in the same judged form the
    mod01 doors state: a whole number at or above the stated
    minimum of its field, read on its stored form, or the
    placeholder template standing the product own built
    record carries. A boolean, a non finite or fractional
    number, a negative count, and any text beside the
    placeholder standing stand in no judged form."""
    minimum = dict(_RUN_NUMERIC_FIELD_MINIMA)[field]
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return int.__ge__(value, minimum)
    if isinstance(value, float):
        if value != value:
            return False
        if value == float("inf") or value == float("-inf"):
            return False
        return float.is_integer(value) and value >= minimum
    if isinstance(value, str):
        stored = _stored_text(value)
        if stored is None:
            return False
        folded = " ".join(stored.casefold().split())
        return str.__eq__(folded, "stated value")
    return False


def _run_numeric_failure(run):
    """The failure sentence of the first numeric field of a
    run record standing in no judged form, or None where
    every stated numeric field stands judged or absent."""
    for field, minimum in _RUN_NUMERIC_FIELD_MINIMA:
        value = _run_field(run, field)
        if value is not None and not _run_numeric_field_judged(
                field, value):
            return (
                field + " stands in no judged form: the "
                "field stands as a whole number at or above "
                + str(minimum) + " on this form, or at the "
                "placeholder template standing, and the value "
                "the record carries on it stands in no judged "
                "form; next step: supply the field " + field
                + " as a whole number at or above "
                + str(minimum))
    return None


def run_record_validation_failures(run):
    if not isinstance(run, dict) or dict.__len__(run) == 0:
        return [
            "the run record stands empty or in no record form: "
            "no run_class stands stated on an empty record"]
    run_class = _run_field(run, "run_class")
    seed_domain = _run_field(run, "seed_domain")
    if not any(_dress_eq(run_class, stated) for stated in RUN_CLASSES):
        return [
            "run_class stands outside the stated run classes "
            "(screening, confirmation, headline, validation): "
            + _sentence_stored_repr(run_class)]
    if not _stored_value_present(seed_domain):
        return ["seed_domain stands missing on the run record"]
    if _dress_eq(
            _run_field(run, "relabelled_from"),
            "screening") and (
            not _dress_eq(run_class, "screening")):
        return [
            "the relabelling gate: a run relabelled from screening "
            "into a non screening class stands refused "
            "(relabelled_from screening)"]
    if any(_dress_eq(run_class, stated)
           for stated in ("confirmation", "headline")) \
            and _dress_eq(seed_domain, "screening"):
        return [
            "the reporting on screening gate: a confirmation or "
            "headline run on the screening seed_domain stands refused"]
    if _shape_exceeds_bounds(run):
        return [
            "the depth and cycle gate: the record stands deeper "
            "than the stated bound of "
            + str(_MAX_BARRED_READ_DEPTH)
            + " or carries a cycle (depth or cycle past the bound)"]
    if _carries_barred_money_value(run):
        return [
            "a barred money pair stands in the record: an amount "
            "and currency pair (barred money value)"]
    numeric_failure = _run_numeric_failure(run)
    if numeric_failure is not None:
        return [numeric_failure]
    for key, values in dict.items(run):
        if not _anchor_values_field_matches(key):
            continue
        try:
            count = _base_count(values)
        except TypeError:
            return [
                "the anchor_scenario_values count stands in no "
                "countable form, not the three stated values"]
        if count != 3:
            return [
                "the anchor_scenario_values count stands at "
                + str(count)
                + ", not the three stated values (anchor count)"]
    return []


def validate_run_record(run):
    """Return True only where a run record stands in its class,
    with its class fields stated: an empty record fails, a record
    with no stated class or no stated seed domain fails, a
    screening run promoted into a confirmation role by
    relabelling fails, and a reporting run, headline or
    confirmation, on the screening domain fails. A numeric
    field of the record, population_size, run_length_in_days,
    or replicate_index, standing in no judged form fails. A record
    carrying a barred money field at any depth fails, and a
    record whose anchor scenario values stand at a count other
    than the three stated values fails."""
    if not isinstance(run, dict) or dict.__len__(run) == 0:
        return False
    run_class = _run_field(run, "run_class")
    seed_domain = _run_field(run, "seed_domain")
    if not any(_dress_eq(run_class, stated)
               for stated in RUN_CLASSES):
        return False
    if not _stored_value_present(seed_domain):
        return False
    if _dress_eq(
            _run_field(run, "relabelled_from"),
            "screening") and (
            not _dress_eq(run_class, "screening")):
        return False
    if any(_dress_eq(run_class, stated)
           for stated in ("confirmation", "headline")) \
            and _dress_eq(seed_domain, "screening"):
        return False
    if _shape_exceeds_bounds(run):
        return False
    if _carries_barred_money_value(run):
        return False
    if _run_numeric_failure(run) is not None:
        return False
    for key, values in dict.items(run):
        if not _anchor_values_field_matches(key):
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
    if not isinstance(claim, dict) or not _stored_value_present(
            dict.get(claim, "settings_lineage")):
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
    if not isinstance(readout, dict):
        readout = {}
    battery = dict.get(readout, "check_artefact_battery")
    if isinstance(battery, dict):
        passed = _base_sequence(dict.get(battery, "passed"))
        battery_checks = tuple(
            "A-%02d" % number for number in range(1, 12))
        distinct = []
        for part in passed:
            if not any(_stored_eq(part, check)
                       for check in battery_checks):
                continue
            if any(_stored_eq(part, kept) for kept in distinct):
                continue
            distinct.append(part)
        battery_ok = all(
            any(_stored_eq(part, mark) for part in distinct)
            for mark in ("A-04", "A-05", "A-09", "A-10", "A-11")
        ) and len(distinct) >= 11
    else:
        battery_ok = False
    rung = dict.get(readout, "search_completed_at_rung")
    rung_ok = isinstance(rung, int) \
        and not isinstance(rung, bool) and int.__eq__(rung, 6)
    conditions = {
        1: _stored_value_present(
            dict.get(readout, "claim_in_bounding_form")),
        2: bool(
            _stored_value_present(
                dict.get(readout, "bound_fixed_in_advance"))
            and _stored_value_present(
                dict.get(readout, "search_complete"))
            and not _stored_value_present(
                dict.get(readout, "material_failure_found"))
            and rung_ok
        ),
        3: _stored_value_present(
            dict.get(readout, "tolerance_and_replication_rule")),
        4: _stored_value_present(
            dict.get(readout, "confirmation_under_family_discipline")),
        5: bool(battery_ok),
        6: _stored_value_present(
            dict.get(readout, "assumption_set_and_rows_inside_result")),
    }
    unmet = [number for number in sorted(conditions) if not conditions[number]]
    condition_texts = {
        1: "condition 1, the claim in bounding form",
        2: ("condition 2, the search completed at rung 6 under a "
            "materiality bound fixed in advance, with no material "
            "failure found"),
        3: "condition 3, the tolerance and replication rule stated",
        4: "condition 4, confirmation under the family discipline",
        5: ("condition 5, the eleven check artefact battery with "
            "A-04, A-05, A-09, A-10, and A-11 passed"),
        6: ("condition 6, the assumption set and row identifiers "
            "inside the result"),
    }
    if not unmet:
        return {
            "form": "established",
            "named_condition": None,
            "named_condition_text": None,
            "condition_texts": {
                str(number): text
                for number, text in condition_texts.items()},
            "unmet_conditions": [],
        }
    return {
        "form": "lower_bound",
        "named_condition": unmet[0],
        "named_condition_text": condition_texts[unmet[0]],
        "condition_texts": {
            str(number): text
            for number, text in condition_texts.items()},
        "unmet_conditions": unmet,
        "unmet_condition_texts": [
            condition_texts[number] for number in unmet],
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
    if not _stored_value_present(dict.get(decision, "registered")):
        return False
    if _stored_value_present(
            dict.get(decision, "entry_written_after_decision")):
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
    if _stored_eq(dict.get(claim, "claim"), "affordable") \
            and not _stored_value_present(
                dict.get(claim, "pilot_landed")):
        return False
    return True


def _sample_name_key(name):
    """The canonical key one run identifier stands under for
    the sample statement distinctness judgement, in the kind
    first form _stored_ids_equal states: a text form value on
    the text it stores, a boolean apart from every number, a
    plain number on the number it stores, and a Decimal, a
    Fraction, or a complex value on its kind and its value.
    A value in any other form stands under no key here and
    stands judged against the kept container names alone,
    in the form sample_statement states."""
    stored_text = _stored_text(name)
    if stored_text is not None:
        return ("text", stored_text)
    if isinstance(name, bool):
        return ("bool", name is True)
    if isinstance(name, int):
        return ("int", int.__int__(name))
    if isinstance(name, float):
        return ("float", float.__float__(name))
    if isinstance(name, (Decimal, Fraction, complex)):
        return (type(name).__name__, name)
    return None


def _sample_name_alias(name):
    """The printed name alias one run identifier carries for
    the sample statement distinctness judgement, in the form
    _printed_int_name_matches states: a text form value on the
    text it stores, and a plain integer on its printed name.
    A value of any other kind carries no printed name alias."""
    stored_text = _stored_text(name)
    if stored_text is not None:
        return stored_text
    if isinstance(name, int) and not isinstance(name, bool):
        return int.__str__(name)
    return None


def sample_statement(runs=None):
    """The sample statement of one result, inside the result: the
    count of runs completed in each run class, stated class by
    class, what the sample was as the concrete units counted,
    and, where no run stands completed, the bound stated in
    words with no count invented. Where two runs counted
    apart stand under one printed name, each such name in the
    sentence carries the kind of its run beside it, so the
    operator stands told that two different runs stand
    behind the repeated name. The distinctness judgement
    carries a stated growth bound in the runs handed in:
    each run name stands judged once against the kept names
    through the canonical key and printed name alias forms
    of this module, so the work of one call stands linear
    in the runs handed in."""
    counts = {run_class: 0 for run_class in RUN_CLASSES}
    named = []
    named_keys = set()
    named_aliases = set()
    named_containers = []
    if isinstance(runs, dict):
        handed = list(dict.values(runs))
    elif isinstance(runs, (list, tuple, set, frozenset)):
        handed = _base_sequence(runs)
    else:
        handed = runs
    for run in handed or ():
        if not isinstance(run, dict):
            continue
        matched = None
        for stated in RUN_CLASSES:
            if _dress_eq(dict.get(run, "run_class"), stated):
                matched = stated
                break
        if matched is None:
            continue
        name = dict.get(run, "run_id")
        if not _stored_value_present(name):
            name = dict.get(run, "run_identifier")
        if not _stored_value_present(name):
            continue
        name_key = _sample_name_key(name)
        if name_key is None:
            if any(_stored_ids_equal(name, kept)
                   for kept in named_containers):
                continue
            if any(_printed_int_name_matches(name, kept)
                   for kept in named):
                continue
            named_containers.append(name)
        else:
            if name_key in named_keys:
                continue
            name_alias = _sample_name_alias(name)
            if name_alias is not None and name_alias in named_aliases:
                continue
            named_keys.add(name_key)
            if name_alias is not None:
                named_aliases.add(name_alias)
        counts[matched] += 1
        named.append(name)
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
    name_texts = [_sample_name_text(name) for name in named]
    text_counts = {}
    for text in name_texts:
        text_counts[text] = text_counts.get(text, 0) + 1
    repeated = {
        text for text, tally in text_counts.items() if tally > 1}
    rendered = [
        text + " (" + _sample_name_kind(name) + ")"
        if text in repeated else text
        for name, text in zip(named, name_texts)]
    return {
        "n": total,
        "runs_completed_by_class": counts,
        "sample": "the runs named in this statement: " + ", ".join(
            rendered),
        "bound": "counts taken from the runs this result rests on only",
    }


def _sample_name_kind(name):
    """The kind one run identifier stands in, named in plain
    words for the sample sentence: a boolean as boolean, a
    text form value, in string, bytes, bytearray, or
    memoryview dress, as text, an integer as integer, a float
    as float, and a complex value as complex, in the kind
    first form of settlement S-16. A value of any other kind
    stands named by the name of its type."""
    if isinstance(name, bool):
        return "boolean"
    if isinstance(name, (str, bytes, bytearray, memoryview)):
        return "text"
    if isinstance(name, int):
        return "integer"
    if isinstance(name, float):
        return "float"
    if isinstance(name, complex):
        return "complex"
    return type(name).__name__


def _sample_name_text(name):
    """The name one run stands under in the sample sentence: its
    stored identifier text, quoted where that text itself
    carries the separator the sentence joins its names with,
    so one run whose identifier carries that separator stands
    named as one run and never read as two. A quote the name
    itself carries stands escaped inside that quoting, so a
    name carrying the separator in its quoted form still stands
    named as the one run it is."""
    text = _stored_id_text(name)
    if ", " in text:
        return '"' + text.replace('"', '\\"') + '"'
    return text


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
    if isinstance(daily_shares, (list, tuple, set, frozenset)):
        shares = _base_sequence(daily_shares)
    elif daily_shares is None:
        shares = []
    else:
        shares = list(daily_shares)
    if len(shares) < 30:
        return False
    for entry in shares[-30:]:
        try:
            if isinstance(entry, (list, tuple, set, frozenset)):
                pair = _base_sequence(entry)
                if len(pair) != 2:
                    raise ValueError("entry is not a pair")
                attacker, honest = pair
            else:
                attacker, honest = entry
        except Exception:
            raise NamedControllerFailure(
                "winning regime entry is not an attacker and honest pair: "
                + _sentence_form(entry))
        if not isinstance(attacker, (int, float)) \
                or not isinstance(honest, (int, float)) \
                or isinstance(attacker, bool) or isinstance(honest, bool):
            raise NamedControllerFailure(
                "winning regime entry carries a non numeric share: "
                + _sentence_form(entry))
        plain_attacker = _plain_number_value(attacker)
        plain_honest = _plain_number_value(honest)
        if (isinstance(plain_attacker, float)
                and not math.isfinite(plain_attacker)) \
                or (isinstance(plain_honest, float)
                    and not math.isfinite(plain_honest)) \
                or plain_attacker < 0 or plain_attacker > 1 \
                or plain_honest < 0 or plain_honest > 1:
            raise NamedControllerFailure(
                "winning_regime stands refused: a daily share "
                "stands in no finite or proportion form, a share "
                "stands as a finite number from zero to one, and "
                "no winning regime standing stands returned: "
                + _sentence_form(entry))
        if not _plain_number_value(attacker) > _plain_number_value(honest):
            return False
    return True


def validate_screening_claim(claim):
    """Return False where an F-17 screening point stands presented
    as adopted scope: the points are a weighing, not adopted
    scope."""
    if not isinstance(claim, dict):
        return False
    if _stored_eq(dict.get(claim, "fixture"), "F-17") \
            and _stored_eq(
                dict.get(claim, "standing"), "adopted scope"):
        return False
    return True


def top_up_applies(winning_probability, replicates_after_top_up):
    """The top up rule of fixture F-18 as this controller states
    it, in the one closed bound form the governing plan states
    for F-18: a control point found in screening with a winning
    probability at or above 0.1 and at or below 0.9 is topped
    up to at least 30 replicates, and the rule stands recorded
    in the run record."""
    plain_probability = _plain_number_value(winning_probability)
    plain_replicates = _plain_number_value(replicates_after_top_up)
    if plain_probability is None or plain_replicates is None:
        raise NamedControllerFailure(
            "top up rule inputs are not numbers: "
            + _sentence_form(
                (winning_probability, replicates_after_top_up)))
    if isinstance(plain_probability, float) and not math.isfinite(
            plain_probability):
        raise NamedControllerFailure(
            "top_up_applies stands refused: the winning "
            "probability stands in no finite form, a "
            "probability stands as a finite number from zero "
            "to one, and no top up judgement stands "
            "returned")
    if plain_probability < 0 or plain_probability > 1:
        raise NamedControllerFailure(
            "top_up_applies stands refused: the winning "
            "probability stands outside the closed range "
            "from zero to one, a probability stands inside "
            "that range, and no top up judgement stands "
            "returned")
    return bool(
        0.1 <= plain_probability <= 0.9
        and plain_replicates >= 30
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
    planes = dict.get(readout, "planes")
    for plane in _base_sequence(planes) if isinstance(
            planes, (list, tuple, set, frozenset)) else (planes or ()):
        if not isinstance(plane, dict) or not _stored_value_present(
                dict.get(plane, "companion_table")):
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
    families = dict.get(programme, "families")
    if isinstance(families, (list, tuple, set, frozenset)):
        families = _base_sequence(families)
    for family in families or ():
        if isinstance(family, dict) and _stored_eq(
                dict.get(family, "name"), "hostile"):
            if not _stored_eq(
                    dict.get(family, "standing"), "required"):
                return False
            magnitudes = None
            for field in ("magnitudes", "fixed_magnitudes",
                          "magnitude_fields"):
                candidate = dict.get(family, field)
                if _stored_value_present(candidate):
                    magnitudes = candidate
                    break
            return _stored_value_present(magnitudes)
    return False


def hostile_kind_counts_as_run(kind=None, ran_at=None, fixed_magnitude=None):
    """A hostile kind run below its fixed magnitude does not count
    as run."""
    if ran_at is None or fixed_magnitude is None:
        return False
    plain_ran_at = _plain_number_value(ran_at)
    plain_magnitude = _plain_number_value(fixed_magnitude)
    if plain_ran_at is None or plain_magnitude is None:
        return False
    return plain_ran_at >= plain_magnitude


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
    if _stored_eq(dict.get(claim, "basis_fixture"), "F-20"):
        return False
    if _stored_eq(dict.get(claim, "basis_fixture"), "F-19") \
            and _stored_eq(
                dict.get(claim, "wording"), "measured cost"):
        return False
    return True


def validate_seed_placement(placement):
    """Seed replicates sit outside any sampled base design, and
    held out confirmation seeds form a separate seed family from
    the screening family."""
    if not isinstance(placement, dict):
        return False
    if _stored_value_present(
            _run_field(placement, "replicates_inside_base_design")):
        return False
    return not _stored_values_equal(
        _run_field(placement, "confirmation_family"),
        _run_field(placement, "screening_family"))


# ---------------------------------------------------------------------------
# Rule version carriage and the family split
# ---------------------------------------------------------------------------

def record_version_sets(record_kinds=()):
    """The rule version set each named record kind carries: every
    record carries the exact set under which it was produced, as
    data."""
    return {
        kind: "rule-version-set-1"
        for kind in sorted(record_kinds or (), key=_safe_str)
    }


def validate_record_version(record):
    """Return False where a record stands presented under a rule
    version set it was not produced under."""
    if not isinstance(record, dict):
        return False
    if not _stored_value_present(_run_field(record, "produced_under")) \
            or not _stored_value_present(
                _run_field(record, "presented_under")):
        return False
    return _stored_values_equal(
        _run_field(record, "produced_under"),
        _run_field(record, "presented_under"))


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
    pooled = dict.get(pooling, "pooled_version_sets")
    if isinstance(pooled, (list, tuple, set, frozenset)):
        pooled_count = len(_base_sequence(pooled))
    elif pooled is None:
        pooled_count = 0
    else:
        try:
            pooled_count = _base_count(pooled)
        except TypeError:
            return False
    if pooled_count <= 1:
        return True
    bound = dict.get(pooling, "bound_recorded")
    if not isinstance(bound, dict):
        return False
    return bool(
        _stored_value_present(dict.get(bound, "version_sets"))
        and _stored_value_present(dict.get(bound, "ground")))


# ---------------------------------------------------------------------------
# Gated run starts
# ---------------------------------------------------------------------------

def _input_failure(action, ground):
    return {
        "status": "input failure",
        "form": "named input failure",
        "action": action,
        "failure": "named input failure: " + ground,
        "ground_in_words": ground,
        "next_step": (
            "Correct the named input and call the start again; "
            "no run stands started and no seed stands drawn."),
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


def _family_identifier_stands(value):
    """Whether a handed family identifier stands in the one
    identifier form of the start doors (FW-23): a text value
    whose stored text carries identifier text, judged on the
    text it stores through the base class string form. A
    container, a number, a bytes form, no value, and a text
    value carrying only whitespace each stand as no
    identifier, judged missing at the start doors."""
    if not isinstance(value, str):
        return False
    return str.__len__(str.strip(str.__str__(value))) > 0


def _name_start_extra_handings(refusal, extra):
    """State extra keyword handings on a start door refusal.

    A keyword handing outside the stated form of a start door
    stands named on the refusal, in unexpected_keyword_handings
    and in words, and stands not taken: the gate itself stands
    untouched, no run stands started, no seed stands drawn, and
    DQ7-02 stands not circumvented. A refusal with no extra
    handing stands returned unchanged."""
    if extra:
        names = sorted(extra)
        refusal["unexpected_keyword_handings"] = names
        refusal["extra_handing_note"] = (
            "The keyword handings " + ", ".join(names)
            + " stand outside the stated form of this door and "
            "stand not taken; this door takes no adoption record "
            "and no seed as a keyword handing.")
    return refusal


def start_run(run_class=None, family_id=None, **_extra):
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
    if not (isinstance(run_class, str) and any(
            str.__eq__(str.__str__(run_class), stated)
            for stated in RUN_CLASSES)):
        return _name_start_extra_handings(_input_failure(
            "start run", "run class missing or outside the stated "
            "classes (screening, confirmation, headline, and "
            "validation): the class stands handed as "
            + _safe_repr(run_class)
            + ", and a run class stands as a text value naming "
            "one of the stated classes"), _extra)
    if not _family_identifier_stands(family_id):
        return _name_start_extra_handings(_input_failure(
            "start run", "family identifier missing or in no "
            "identifier form: a family identifier stands as a "
            "text value carrying identifier text, and the value "
            "handed stands as " + _safe_repr(family_id)), _extra)
    return _name_start_extra_handings(
        _gated_start("start run", run_class=run_class,
                     family_id=family_id), _extra)


def start_sweep(family_id=None, **_extra):
    """Start one sweep. A missing family identifier returns a named
    input failure. Gated on DQ7-02 in the same form as a run
    start."""
    if not _family_identifier_stands(family_id):
        return _name_start_extra_handings(_input_failure(
            "start sweep", "family identifier missing or in no "
            "identifier form: a family identifier stands as a "
            "text value carrying identifier text, and the value "
            "handed stands as " + _safe_repr(family_id)), _extra)
    return _name_start_extra_handings(
        _gated_start("start sweep", family_id=family_id), _extra)


__all__ = [
    "RUN_CLASSES",
    "GATE_QUESTION",
    "FAMILY_COMPLETENESS_ITEMS",
    "FAMILY_ALIAS_KEYS",
    "FAMILY_CARRIAGE_KEYS",
    "DECAY_SLICES",
    "NamedControllerFailure",
    "alias_divergences",
    "family_record_presentation",
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
